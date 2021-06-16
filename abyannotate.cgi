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

# Obtain parameters from web site
my $cgi       = new CGI;
my $cdrdef    = defined($cgi->param('cdrdef'))?$cgi->param('cdrdef'):'kabat';
my $labelcdrs = defined($cgi->param('labelcdrs'))?'-label':'';
my $pretty    = ($cgi->param('outstyle') eq 'pretty')?1:0;
my $plain     = defined($cgi->param('plain'));
$pretty = 0 if($plain);

# Print HTTP header
PrintHTTPHeader($cgi, $plain);

# Check that the executables are present
if(! -x $::abnum)
{
    PrintHTML("Error: Abnum executable not found: $::abnum", $plain, 1);
    exit 1;
}
if(! -x "./abyannotate.pl")
{
    PrintHTML("Error: abyannotate Perl script executable not found!", $plain, 1);
    exit 1;
}


# Obtain the sequence data
my $sequences = GetFileOrPastedSequences($cgi);
#my $sequences = GetFileOrPastedSequences($cgi->param('sequences'),
#                                         $cgi->param('fastafile'));
if($sequences eq '')
{
    PrintHTML('Error: You must specify some sequences or a FASTA file', $plain, 1);
    exit 0;
}

# Write it to a FASTA file
my $fastaFile = WriteFastaFile($sequences, $plain);
if($fastaFile eq '')
{
    PrintHTML('Error: Unable to create FASTA file', $plain, 1);
    exit 0;
}

# Run abyannotate to analyze the data and place results in the web tmp
# directory
my $rawFile   = $config{'webtmp'} . "/" . $$ . time() . ".txt";
my $exe = "./abyannotate.pl $labelcdrs -cdr=$cdrdef -abnum=$::abnum $fastaFile";
`$exe > $rawFile`;
my $result    = `cat $rawFile`;

# Remove the temporary FASTA file
print STDERR "FASTA:\n$fastaFile\n";
#unlink $fastaFile;

my $wrapInPre = 0;
if($pretty)
{
    $result = ConvertToHTML($result);
}
elsif(!$plain)
{
    $result = "<pre>\n${result}\n</pre>";
}
PrintHTML($result, $plain, 0);

sub PrintHTML
{
    my($result, $plain, $isError) = @_;

    if(!$plain)
    {
        PrintHTMLHeader();
        print "<div>\n";
    }

    if($result eq '')
    {
        print "<p>Error: processing failed</p>\n";
    }
    elsif($isError)
    {
        $result = "<p class='error'>$result</p>" if(!$plain);
        print "$result\n";
    }
    else
    {
        print "$result\n";
    }

    if(!$plain)
    {
        print "</div>\n";
        PrintHTMLFooter();
    }

}

sub PrintHTMLFooter
{
    print <<__EOF;
  </body>
</html>
__EOF
}


sub PrintHTMLHeader
{
    print <<__EOF;
<html>
  <head>
    <title>
      Antibody sequence bulk annotation
    </title>
    <link rel='stylesheet' href='abyannotate.css' />
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

sub GetFileOrPastedSequences
{
    my($cgi) = @_;
    my $sequences = $cgi->param('sequences');
    my $filename  = $cgi->param('fastafile');
    
    if($filename ne '')
    {
        $CGI::POST_MAX = 1024 * 5000;
        my $uploadDir = "/tmp/abyannotate_" . $$ . time();

        my $safeFilenameCharacters = "a-zA-Z0-9_.-";
        $filename =~ s/.*\///;
        $filename =~ tr/ /_/;
        $filename =~ s/[^$safeFilenameCharacters]//g;
        if ( $filename =~ /^([$safeFilenameCharacters]+)$/ )
        {
            $filename = $1;
        }
        else
        {
            $filename = 'upload.faa';
        }
        
        `mkdir $uploadDir`;
        my $fhIn = $cgi->upload('fastafile');
        my $fullFilename = "$uploadDir/$filename";
        if(open(UPLOADFILE, '>', $fullFilename))
        {
            binmode UPLOADFILE;
            while (<$fhIn>) 
            { 
                print UPLOADFILE;
            } 
            close UPLOADFILE;
        }
        
        $sequences = '';
        if(open(my $fp, '<', $fullFilename))
        {
            while(<$fp>)
            {
                $sequences .= $_;
            }
            close($fp);
        }
        unlink $uploadDir;
    }

    return($sequences);
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
