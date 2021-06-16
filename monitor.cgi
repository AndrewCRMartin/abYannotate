#!/usr/bin/perl
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


my $fileStem='abyannotate_' . $$ . time();
my $htmlView='/tmp/' . $fileStem . '.html';
my $htmlPage=$config{'webtmp'} . "/${fileStem}.html";
my $textPage=$config{'webtmp'} . "/${fileStem}.txt";

# Obtain parameters from web site
my $cgi       = new CGI;
my $cdrdef    = defined($cgi->param('cdrdef'))?$cgi->param('cdrdef'):'kabat';
my $labelcdrs = defined($cgi->param('labelcdrs'))?'-label':'';
my $pretty    = ($cgi->param('outstyle') eq 'pretty')?1:0;
my $plain     = (defined($cgi->param('plain')))?1:0;
$pretty       = 0 if($plain);


# Check that the executables are present
if(! -x $::abnum)
{
    PrintHTMLError("Error: Abnum executable not found: $::abnum");
    exit 1;
}
if(! -x "./abyannotate.pl")
{
    PrintHTMLError("Error: abyannotate Perl script executable not found!");
    exit 1;
}


# Obtain the sequence data
my $sequences = GetFileOrPastedSequences($cgi);
if($sequences eq '')
{
    PrintHTMLError('Error: You must specify some sequences or a FASTA file');
    exit 0;
}


RunSlowProgram($htmlPage, $htmlView, $textPage, $cdrdef, $labelcdrs, $pretty, $plain, $sequences);

my $page= '';
if(-e $htmlPage)
{
    $page = `cat $htmlPage`;
}
else
{
    PrintHTMLError('Error: no HTML page');
}
    
$page    =~ s/\<meta.*?\>/<meta http-equiv='refresh' content="0; URL=$htmlView" \/\>/;
print $cgi->header();
print $page;

sub PrintHTMLError
{
    my($text) = @_;
    print $cgi->header();
    
    print <<__EOF;
<html>
  <head>
    <title>
      Antibody sequence bulk annotation
    </title>
    <link rel='stylesheet' href='$::css' />
  </head>

  <body>
    <h1>$text</h1>
  </body>
</html>
__EOF
}

sub RunSlowProgram
{
    my ($htmlPage, $htmlView, $textPage, $cdrdef, $labelcdrs, $pretty, $plain, $sequences) = @_;

    if(0)
    {
        if(open(my $fp, '>>', '/var/www/html/tmp/errors.log'))
        {
            print $fp localtime(time()) . " (MONITOR.CGI)\n";
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

    unlink $textPage;
    unlink $htmlPage;
    sleep 1 while(-e $htmlPage);
    `nohup ./cgiwrap.pl $htmlPage $htmlView $textPage $cdrdef $labelcdrs $pretty $plain "$sequences" &> /dev/null &`;
    sleep 1 while(! -e $htmlPage);
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


