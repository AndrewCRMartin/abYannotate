#!/usr/bin/perl

# For WS access a newline in a FASTA format file may be replaced by a ~

use strict;
use CGI;

# Add the path of the executable/lib to the library path
use FindBin;
use Cwd qw(abs_path);
use lib abs_path("$FindBin::Bin/lib");
use CGI::Carp qw ( fatalsToBrowser );

# Read the config file
use config;
my $configFile = "$FindBin::Bin" . "/config.cfg";
my %config = config::ReadConfig($configFile);
$::abnum=$config{'abnum'} unless(defined($::abnum));
$::css=$config{'htmllocation'} . "/abyannotate.css";

# Obtain parameters from command line
my $htmlPage  = shift @ARGV;
my $htmlView  = shift @ARGV;
my $textPage  = shift @ARGV;
my $cdrdef    = shift @ARGV;
my $labelcdrs = shift @ARGV;
my $pretty    = shift @ARGV;
my $plain     = shift @ARGV;
my $sequences = shift @ARGV;

if(0)
{
    if(open(my $fp, '>>', '/var/www/html/tmp/errors.log'))
    {
        print $fp localtime(time()) . " (ABYANNOTATE.CGI)\n";
        print $fp "htmlPage  : $htmlPage  \n";
        print $fp "htmlView  : $htmlView  \n";
        print $fp "textPage  : $textPage  \n";
        print $fp "cdrdef    : $cdrdef    \n";
        print $fp "labelcdrs : $labelcdrs \n";
        print $fp "pretty    : $pretty    \n";
        print $fp "plain     : $plain     \n";
#        print $fp "sequences : $sequences \n";
        close $fp;
    }
}



# Write it to a FASTA file
my $fastaFile = WriteFastaFile($sequences, $plain);
if($fastaFile eq '')
{
    PrintHTML($htmlPage, 'Error: Unable to create FASTA file', $plain, 1, '');
    exit 0;
}

# Run abyannotate to analyze the data and place results in the web tmp
# directory
my $rawFile   = $textPage;
my $exe = "./abyannotate.pl $labelcdrs -cdr=$cdrdef -abnum=$::abnum $fastaFile";
`$exe > $rawFile`;
my $result    = `cat $rawFile`;

# Remove the temporary FASTA file
unlink $fastaFile;

my $wrapInPre = 0;
if($pretty)
{
    $result = ConvertToHTML($result);
}
elsif(!$plain)
{
    $result = "<pre>\n${result}\n</pre>";
}
PrintHTML($htmlPage, $result, $plain, 0, $rawFile);

sub PrintHTML
{
    my($htmlPage, $result, $plain, $isError, $rawFile) = @_;

    if(open(my $fp, '>', $htmlPage))
    {
        if(!$plain)
        {
            PrintHTMLHeader($fp);

            if($rawFile ne '')
            {
                $rawFile =~ s/^.*\///;
                print $fp "<div><a class='btn' download='$rawFile' href='/tmp/$rawFile'>Download</a></div>\n";
            }
            
            print $fp "<div>\n";
        }

        if($result eq '')
        {
            print $fp "<p>Error: processing failed</p>\n";
        }
        elsif($isError)
        {
            $result = "<p class='error'>$result</p>" if(!$plain);
            print $fp "$result\n";
        }
        else
        {
            print $fp "$result\n";
        }
        
        if(!$plain)
        {
            print $fp "</div>\n";
            PrintHTMLFooter($fp);
        }
    }

}

sub PrintHTMLFooter
{
    my($fp) = @_;
    print $fp <<__EOF;
  </body>
</html>
__EOF
}


sub PrintHTMLHeader
{
    my($fp) = @_;
    print $fp <<__EOF;
<html>
  <head>
    <title>
      Antibody sequence bulk annotation
    </title>
    <link rel='stylesheet' href='$::css' />
  </head>

  <body>
    <h1>Antibody sequence bulk annotation</h1>
__EOF
}

sub WriteFastaFile
{
    my($sequences, $plain) = @_;
    my $tFile = "/var/tmp/abyannotate_" . $$ . time() . ".faa";
    if(open(my $fp, '>', $tFile))
    {
        $sequences =~ s/\r//g;
        if($plain)
        {
            my @data = split(/[\~\n]/, $sequences);
            foreach my $datum (@data)
            {
                print STDERR ">> $datum\n";   #HERE
                print $fp "$datum\n";
            }
        }
        else
        {
            print $fp $sequences;
        }
        close $fp;
        return($tFile);
    }
    return('');
}

sub ConvertToHTML
{
    my($result) = @_;

    my $html = '';
    my @data = split(/\n/, $result);

    foreach $_ (@data)
    {
        if(/^>/)
        {
            $_ = FixHTMLChars($_);
            $html .= "<h2>$_</h2>\n";

        }
        elsif(/H1/ || /H2/ || /H3/ || /L1/ || /L2/ || /L3/)
        {
            my $labels = HTMLizeLabels($_);
            $html .= "<p class='sequence'>$labels</p>\n";
        }
        elsif(length($_))
        {
            my $annotation = HTMLizeSequence($_);
            $html .= "<p class='sequence'>$annotation</p>\n";
        }
    }
    return($html);
}

sub HTMLizeSequence
{
    my($input) = @_;
    my $output = '';
    my $inCDR  = 0;

    return($input) if($input =~ /^#/);
    
    my @chars = split(//, $input);
    foreach my $char (@chars)
    {
        if($char eq '{')
        {
            $inCDR   = 1;
        }
        elsif($char eq '}')
        {
            $inCDR   = 0;
        }
        else
        {
            if($inCDR)
            {
                $output .= "<span class='aa cdr$char'>$char</span>";
            }
            else
            {
                $output .= "<span class='aa fw$char'>$char</span>";
            }
        }
    }
    return($output);
}

sub HTMLizeLabels
{
    my($input) = @_;
    my $output = '';
    my $inCDR  = 0;
    
    my @chars = split(//, $input);
    foreach my $char (@chars)
    {
        if($char eq '{')
        {
            $inCDR   = 1;
        }
        elsif($char eq '}')
        {
            $inCDR   = 0;
        }
        elsif($char eq ' ')
        {
            $output .= "<span class='label'>&nbsp;</span>";
        }
        else
        {
            $output .= "<span class='label'>$char</span>";
        }
    }
    return($output);
}

sub FixHTMLChars
{
    my($input) = @_;
    $input =~ s/\&/\&amp;/;
    $input =~ s/\>/\&gt;/;
    $input =~ s/\</\&lt;/;
    return($input);
}

sub PrintHTTPHeader
{
    my($cgi, $plain) = @_;
    if($plain)
    {
        print $cgi->header(-type=>'text/plain');
    }
    else
    {
        print $cgi->header();
    }
}
