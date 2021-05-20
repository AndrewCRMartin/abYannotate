#!/usr/bin/perl

use strict;
use CGI;

$::abnum="../../abs/bin/abnum";

my $cgi = new CGI;

my $sequences = $cgi->param('sequences');
my $cdrdef    = $cgi->param('cdrdef');

my $fastaFile = WriteFastaFile($sequences);
my $result    = '';
if($fastaFile ne '')
{
    my $exe = "./abyannotate.pl -cdr=$cdrdef -abnum=$::abnum $fastaFile";
    $result = `$exe`;
}


print $cgi->header();
PrintHTML($result);

sub PrintHTML
{
    my($result) = @_;

    print <<__EOF;
<html>
  <head>
    <title>
      Antibody sequence bulk annotation
    </title>
  </head>

  <body>
    <h1>Antibody sequence bulk annotation</h1>
__EOF

    if($result eq '')
    {
        print "# Error: processing failed\n";
    }
    else
    {
        print "<pre>\n";
        print $result;
        print "</pre>\n";
    }

    print <<__EOF;
  </body>
</html>
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
