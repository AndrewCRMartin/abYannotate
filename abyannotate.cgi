#!/usr/bin/perl

use strict;
use CGI;

# Add the path of the executable/lib to the library path
use FindBin;
use Cwd qw(abs_path);
use lib abs_path("$FindBin::Bin/lib");
use CGI::Carp qw ( fatalsToBrowser );


use config;

my $configFile = "$FindBin::Bin" . "/config.cfg";

my %config = config::ReadConfig($configFile);

$::abnum=$config{'abnum'} unless(defined($::abnum));

my $cgi = new CGI;
print $cgi->header();
if(! -x $::abnum)
{
    PrintHTML("# Abnum executable not found: $::abnum", 0);
    exit 1;
}
if(! -x "./abyannotate.pl")
{
    PrintHTML("# abyannotate Perl script executable not found!", 0);
    exit 1;
}

my $sequences = $cgi->param('sequences');
my $cdrdef    = $cgi->param('cdrdef');
my $labelcdrs = defined($cgi->param('labelcdrs'))?'-label':'';
my $html      = ($cgi->param('outstyle') eq 'html')?'-html':'';

my $uploadDir = "/home/public/abyannotate_" . $$ . time();
my $filename  = $cgi->param('fastafile');

if($filename ne '')
{
    $CGI::POST_MAX = 1024 * 5000;
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
}
elsif($sequences eq '')
{
    PrintHTML('# You must specify some sequences or a FASTA file', 0);
    exit 0;
}


my $fastaFile = WriteFastaFile($sequences);
my $result    = '';
if($fastaFile ne '')
{
    my $exe = "./abyannotate.pl $html $labelcdrs -cdr=$cdrdef -abnum=$::abnum $fastaFile";
    $result = `$exe`;
    unlink $fastaFile;
}
else
{
    PrintHTML('# Unable to create temp file', 0);
    exit 0;
}


my $wrapInPre = ($html eq '-html')?0:1;
PrintHTML($result, $wrapInPre);

sub PrintHTML
{
    my($result, $wrapInPre) = @_;

    PrintHTMLHeader();

    if($result eq '')
    {
        print "# Error: processing failed\n";
    }
    else
    {
        if($wrapInPre)
        {
            print "<pre>\n";
            print $result;
            print "</pre>\n";
        }
        else
        {
            print $result;
        }
    }

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
    my($sequences) = @_;
    my $tFile = "/var/tmp/abyannotate_" . $$ . time() . ".faa";
    if(open(my $fp, '>', $tFile))
    {
        $sequences =~ s/\r//g;
        print $fp $sequences;
        close $fp;
        return($tFile);
    }
    return('');
}
