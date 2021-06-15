#!/usr/bin/perl

use strict;
use CGI;

# Add the path of the executable/lib to the library path
use FindBin;
use Cwd qw(abs_path);
use lib abs_path("$FindBin::Bin/lib");

use config;

my $configFile = "$FindBin::Bin" . "/config.cfg";

my %config = config::ReadConfig($configFile);

$::abnum=$config{'abnum'} unless(defined($::abnum));

if(! -x $::abnum)
{
    print "Abnum executable not found: $::abnum\n";
    exit 1;
}

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
