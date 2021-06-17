#!/usr/bin/perl
#*************************************************************************
#
#   Program:    abYannotate web interface
#   File:       cgiwrap.pl
#   
#   Version:    V1.0
#   Date:       17.06.21
#   Function:   
#   
#   Copyright:  (c) Prof. Andrew C. R. Martin, UCL, 2021
#   Author:     Prof. Andrew C. R. Martin
#   Address:    Institute of Structural and Molecular Biology
#               Division of Biosciences
#               University College
#               Gower Street
#               London
#               WC1E 6BT
#   EMail:      andrew@bioinf.org.uk
#               
#*************************************************************************
#
#   This program is not in the public domain, but it may be copied
#   according to the conditions laid out in the accompanying file
#   LICENSE
#
#   The code may be modified as required, but any modifications must be
#   documented so that the person responsible can be identified. If 
#   someone else breaks this code, I don't want to be blamed for code 
#   that does not work! 
#
#   The code may not be sold commercially or included as part of a 
#   commercial product except as described in the file LICENSE
#
#*************************************************************************
#
#   Description:
#   ============
#
#*************************************************************************
#
#   Usage:
#   ======
#
#*************************************************************************
#
#   Revision History:
#   =================
#   V1.0   17.06.21  Original   By: ACRM
#
#*************************************************************************
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
$::htmllocation=$config{'htmllocation'};
$::css = "$::htmllocation/abyannotate.css";

my $htmlPage  = shift @ARGV;
my $htmlView  = shift @ARGV;
my $textPage  = shift @ARGV;
my $cdrdef    = shift @ARGV;
my $labelcdrs = shift @ARGV;
my $pretty    = shift @ARGV;
my $plain     = shift @ARGV;
my $faaFile   = shift @ARGV;
my $nSeqs     = shift @ARGV;

if(0)
{
    if(open(my $fp, '>>', '/var/www/html/tmp/errors.log'))
    {
        print $fp localtime(time()) . " (CGIWRAP)\n";
        print $fp "htmlPage  : $htmlPage  \n";
        print $fp "htmlView  : $htmlView  \n";
        print $fp "textPage  : $textPage  \n";
        print $fp "cdrdef    : $cdrdef    \n";
        print $fp "labelcdrs : $labelcdrs \n";
        print $fp "pretty    : $pretty    \n";
        print $fp "plain     : $plain     \n";
        print $fp "sequences : $faaFile   \n";
        print $fp "nSeqs     : $nSeqs     \n";
        close $fp;
    }
}

`touch $textPage`;

my $timeEstimate = int(0.5 + ($nSeqs * $config{'timeperseq'}));
PrintUpdatingHTMLPage($htmlPage, $htmlView, $nSeqs, $timeEstimate);
DoSlowStuff($htmlPage, $htmlView, $textPage, $cdrdef, $labelcdrs, $pretty,$plain, $faaFile);

#*************************************************************************
sub DoSlowStuff
{
    my($htmlPage, $htmlView, $textPage, $cdrdef, $labelcdrs, $pretty, $plain, $faaFile) = @_;

    `./abyannotate.cgi $htmlPage $htmlView $textPage $cdrdef $labelcdrs $pretty $plain $faaFile`;
}

#*************************************************************************
sub PrintUpdatingHTMLPage
{
    my($htmlPage, $htmlView, $nSeqs, $timeEstimate) = @_;

    if(open(my $fp, '>', $htmlPage))
    {
        print $fp <<__EOF;
<html>
  <head>
    <title>abYannotate - please wait...</title>
    <link rel='stylesheet' href='$::css' />
    <meta http-equiv="refresh" content="10" />
  </head>
  <body>
    <h1>abYannotate</h1>
    <h2>Waiting for calculations to complete... <img src='$::htmllocation/throbber.gif' /></h2>
    <p>This page will refresh every 10 seconds. Press 
      <a href='$htmlView'>here</a> to force a refresh.
    </p>
    <p>You uploaded $nSeqs sequences. Estimated total time: $timeEstimate seconds</p>
  </body>
</html>
__EOF
        close $fp;
    }
}
