#!/usr/bin/perl
#*************************************************************************
#
#   Program:    abYannotate web interface
#   File:       abyannotate.cgi
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
my $faaFile   = shift @ARGV;

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
        print $fp "sequences : $faaFile   \n";
        close $fp;
    }
}

# Run abyannotate to analyze the data and place results in the web tmp
# directory
my $rawFile   = $textPage;
my $exe = "./abyannotate.pl $labelcdrs -cdr=$cdrdef -abnum=$::abnum $faaFile";
`$exe > $rawFile`;
my $result    = `cat $rawFile`;

# Remove the temporary FASTA file
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
PrintHTML($htmlPage, $result, $plain, 0, $rawFile);

#*************************************************************************
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

#*************************************************************************
sub PrintHTMLFooter
{
    my($fp) = @_;
    print $fp <<__EOF;
  </body>
</html>
__EOF
}


#*************************************************************************
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


#*************************************************************************
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


#*************************************************************************
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

#*************************************************************************
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

#*************************************************************************
sub FixHTMLChars
{
    my($input) = @_;
    $input =~ s/\&/\&amp;/;
    $input =~ s/\>/\&gt;/;
    $input =~ s/\</\&lt;/;
    return($input);
}

