#!/usr/bin/perl -s

use strict;
use lib '.';
use lib './lib';
use fasta;

$::abnum='abnum' unless(defined($::abnum));
$::abnum .= ' -f';
$::cdr='kabat' unless(defined($::cdr));

$::cdrdef{'kabat'}{'L1'}{'start'} = 'L24';
$::cdrdef{'kabat'}{'L1'}{'stop'}  = 'L34';
$::cdrdef{'kabat'}{'L2'}{'start'} = 'L50';
$::cdrdef{'kabat'}{'L2'}{'stop'}  = 'L56';
$::cdrdef{'kabat'}{'L3'}{'start'} = 'L89';
$::cdrdef{'kabat'}{'L3'}{'stop'}  = 'L97';
$::cdrdef{'kabat'}{'H1'}{'start'} = 'H31';
$::cdrdef{'kabat'}{'H1'}{'stop'}  = 'H35';
$::cdrdef{'kabat'}{'H2'}{'start'} = 'H50';
$::cdrdef{'kabat'}{'H2'}{'stop'}  = 'H65';
$::cdrdef{'kabat'}{'H3'}{'start'} = 'H95';
$::cdrdef{'kabat'}{'H3'}{'stop'}  = 'H102';

$::cdrdef{'chothia'}{'L1'}{'start'} = 'L24';
$::cdrdef{'chothia'}{'L1'}{'stop'}  = 'L34';
$::cdrdef{'chothia'}{'L2'}{'start'} = 'L50';
$::cdrdef{'chothia'}{'L2'}{'stop'}  = 'L56';
$::cdrdef{'chothia'}{'L3'}{'start'} = 'L89';
$::cdrdef{'chothia'}{'L3'}{'stop'}  = 'L97';
$::cdrdef{'chothia'}{'H1'}{'start'} = 'H26';
$::cdrdef{'chothia'}{'H1'}{'stop'}  = 'H32';
$::cdrdef{'chothia'}{'H2'}{'start'} = 'H50';
$::cdrdef{'chothia'}{'H2'}{'stop'}  = 'H58';
$::cdrdef{'chothia'}{'H3'}{'start'} = 'H95';
$::cdrdef{'chothia'}{'H3'}{'stop'}  = 'H102';

$::cdrdef{'combined'}{'L1'}{'start'} = 'L24';
$::cdrdef{'combined'}{'L1'}{'stop'}  = 'L34';
$::cdrdef{'combined'}{'L2'}{'start'} = 'L50';
$::cdrdef{'combined'}{'L2'}{'stop'}  = 'L56';
$::cdrdef{'combined'}{'L3'}{'start'} = 'L89';
$::cdrdef{'combined'}{'L3'}{'stop'}  = 'L97';
$::cdrdef{'combined'}{'H1'}{'start'} = 'H26';
$::cdrdef{'combined'}{'H1'}{'stop'}  = 'H35';
$::cdrdef{'combined'}{'H2'}{'start'} = 'H50';
$::cdrdef{'combined'}{'H2'}{'stop'}  = 'H65';
$::cdrdef{'combined'}{'H3'}{'start'} = 'H95';
$::cdrdef{'combined'}{'H3'}{'stop'}  = 'H102';



my $fastaFile = shift @ARGV;
my $tFile = "/tmp/abannotate_" . $$ . time();

if(open(my $in, '<', $fastaFile))
{
    my($id, $info, $sequence);
    
    while((($id, $info, $sequence) = fasta::ReadFasta($in)) && ($id ne ''))
    {
        if(open(my $out, '>', $tFile))
        {
            print $out "$info\n$sequence\n";
            close $out;

            my $exe = "$::abnum $tFile";
            my $result = `$exe`;

            print "$info\n";
            $result = Annotate($result, $::cdr);
            print "$result\n";
        }
    }
    close($in);
    unlink($tFile);
}


sub Annotate
{
    my($result, $cdr) = @_;
    $result =~ s/^\s+//;  # Remove leading spaces;
    
    # Error message
    if($result =~ /^#/)
    {
        chomp $result;
        return($result);
    }
    # Blank result
    if(!length($result))
    {
        return('# no result from numbering');
    }
    
    my $chain = substr($result, 0, 1);
    my @lines = split(/\n/, $result);
    my $inCDR = 0;
    $result = '';
    foreach my $line (@lines)
    {
        chomp $line;
        my($resnum, $aa) = split(/\s+/, $line);
        for(my $i=1; $i<=3; $i++)
        {
            if($resnum eq $::cdrdef{$cdr}{"$chain$i"}{'start'})
            {
                $result .= '|';
                last;
            }
        }

        $result .= $aa;

        for(my $i=1; $i<=3; $i++)
        {
            if($resnum eq $::cdrdef{$cdr}{"$chain$i"}{'stop'})
            {
                $result .= '|';
                last;
            }
        }
    }
    return($result);
}
