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

# Create filenames
my $fileStem = 'abyannotate_' . $$ . time();
my $htmlView = '/tmp/' . $fileStem . '.html';
my $htmlPage = $config{'webtmp'} . "/${fileStem}.html";
my $textPage = $config{'webtmp'} . "/${fileStem}.txt";
my $faaFile  = $config{'webtmp'} . "/${fileStem}.faa";

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
my $nSeqs = GetFileOrPastedSequences($cgi, $faaFile);
if(!$nSeqs)
{
    PrintHTMLError('Error: You must specify some sequences or a FASTA file');
    exit 0;
}

RunSlowProgram($htmlPage, $htmlView, $textPage, $cdrdef, $labelcdrs, $pretty, $plain, $faaFile, $nSeqs);

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
    my ($htmlPage, $htmlView, $textPage, $cdrdef, $labelcdrs, $pretty, $plain, $faaFile, $nSeqs) = @_;

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
            print $fp "sequences : $faaFile   \n";
            print $fp "nseqs     : $nSeqs     \n";
            close $fp;
        }
    }

    unlink $textPage;
    unlink $htmlPage;
    sleep 1 while(-e $htmlPage);
    `nohup ./cgiwrap.pl $htmlPage $htmlView $textPage $cdrdef $labelcdrs $pretty $plain $faaFile $nSeqs &> /dev/null &`;
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
    my($cgi, $faaFile) = @_;
    my $sequences = $cgi->param('sequences');
    my $filename  = $cgi->param('fastafile');
    my $nSeqs     = 0;
    
    if($filename ne '')
    {
#        $CGI::POST_MAX = 1024 * 5000;
        my $fhIn = $cgi->upload('fastafile');
        if(open(UPLOADFILE, '>', $faaFile))
        {
            binmode UPLOADFILE;
            while (<$fhIn>) 
            {
                $nSeqs++ if(/^\>/);
                print UPLOADFILE;
            } 
            close UPLOADFILE;
        }
        else
        {
            PrintHTMLError("Unable to write uploaded FASTA file");
            exit 1;
        }

        return($nSeqs);
    }

    return(0);
}


