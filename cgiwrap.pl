#!/usr/bin/perl
use strict;
use CGI;

my $htmlPage  = shift @ARGV;
my $htmlView  = shift @ARGV;
my $textPage  = shift @ARGV;
my $cdrdef    = shift @ARGV;
my $labelcdrs = shift @ARGV;
my $pretty    = shift @ARGV;
my $plain     = shift @ARGV;
my $sequences = shift @ARGV;


if(1)
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
#        print $fp "sequences : $sequences \n";
        close $fp;
    }
}


    
`touch $textPage`;

PrintUpdatingHTMLPage($htmlPage, $htmlView);
DoSlowStuff($htmlPage, $htmlView, $textPage, $cdrdef, $labelcdrs, $pretty,$plain, "$sequences");

sub DoSlowStuff
{
    my($htmlPage, $htmlView, $textPage, $cdrdef, $labelcdrs, $pretty, $plain, $sequences) = @_;

    `./abyannotate.cgi $htmlPage $htmlView $textPage $cdrdef $labelcdrs $pretty $plain "$sequences"`;
}

sub PrintUpdatingHTMLPage
{
    my($htmlPage, $htmlView) = @_;

    if(open(my $fp, '>', $htmlPage))
    {
        print $fp <<__EOF;
<html>
  <head>
    <title>abYannotate - please wait...</title>
    <meta http-equiv="refresh" content="10" />
  </head>
  <body>
    <h1>abYannotate</h1>
    <h2>Waiting for calculations to complete...</h2>
    <p>If this page does not refresh after 10 seconds, press 
      <a href='$htmlView'>here</a>
    </p>
  </body>
</html>
__EOF
        close $fp;
    }
}
