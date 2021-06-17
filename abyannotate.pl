#!/usr/bin/perl -s
#*************************************************************************
#
#   Program:    abyannotate
#   File:       abyannotate.pl
#   
#   Version:    V1.0
#   Date:       17.06.21
#   Function:   Annotate CDRs in FASTA sequences
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
#   commercial product except as described in the file LICENSE.
#
#*************************************************************************
#
#   Description:
#   ============
#   abyannotate makes use of abnum (or some other antibody numbering
#   program able to generate Chothia numbering) to annotate CDRs with
#   curly brackets around them.
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
#   V1.0   17.06.21   Original   By: ACRM
#
#*************************************************************************
use strict;

# Add the path of the executable to the library path
use FindBin;
use lib $FindBin::Bin;
# and the lib subdirectory
use Cwd qw(abs_path);
use lib abs_path("$FindBin::Bin/lib");

use fasta;
use config;

my $configFile = "$FindBin::Bin" . "/config.cfg";

my %config = config::ReadConfig($configFile);

$::abnum=$config{'abnum'} unless(defined($::abnum));

UsageDie() if(defined($::h));

if(! -x $::abnum)
{
    print "Abnum executable not found: $::abnum\n";
    exit 1;
}

$::abnum .= ' -f -c';
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

$::cdrdef{'imgt'}{'L1'}{'start'} = 'L27';
$::cdrdef{'imgt'}{'L1'}{'stop'}  = 'L32';
$::cdrdef{'imgt'}{'L2'}{'start'} = 'L50';
$::cdrdef{'imgt'}{'L2'}{'stop'}  = 'L52';
$::cdrdef{'imgt'}{'L3'}{'start'} = 'L89';
$::cdrdef{'imgt'}{'L3'}{'stop'}  = 'L97';
$::cdrdef{'imgt'}{'H1'}{'start'} = 'H26';
$::cdrdef{'imgt'}{'H1'}{'stop'}  = 'H33';
$::cdrdef{'imgt'}{'H2'}{'start'} = 'H51';
$::cdrdef{'imgt'}{'H2'}{'stop'}  = 'H56';
$::cdrdef{'imgt'}{'H3'}{'start'} = 'H93';
$::cdrdef{'imgt'}{'H3'}{'stop'}  = 'H102';

#*************************************************************************
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
            my $labels = '';

            ($result, $labels) = Annotate($result, $::cdr);
            print "$info\n";
            print "$labels\n" if(defined($::label));
            print "$result\n";
        }
    }
    close($in);
    unlink($tFile);
}


#*************************************************************************
sub Annotate
{
    my($input, $cdr) = @_;
    $input =~ s/^\s+//;  # Remove leading spaces;
    
    # Error message
    if($input =~ /^#/)
    {
        chomp $input;
        return($input);
    }
    # Blank input
    if(!length($input))
    {
        return('# no result from numbering');
    }
    
    my $chain = substr($input, 0, 1);
    my @lines = split(/\n/, $input);
    my $inCDR = 0;

    my $output = '';
    my $labels = '';
    my $skipcount = 0;
    my $inCDR     = 0;
    foreach my $line (@lines)
    {
        chomp $line;
        my($resnum, $aa) = split(/\s+/, $line);
        for(my $i=1; $i<=3; $i++)
        {
            if($resnum eq $::cdrdef{$cdr}{"$chain$i"}{'start'})
            {
                $output   .= '{';
                $labels   .= "{$chain$i";
                $skipcount = 2;
                $inCDR     = 1;
                last;
            }
        }

        $output .= $aa;
        if($skipcount-- <= 0)
        {
            if($inCDR)
            {
                $labels .= '-';
            }
            else
            {
                $labels .= ' ';
            }
        }

        for(my $i=1; $i<=3; $i++)
        {
            if($resnum eq $::cdrdef{$cdr}{"$chain$i"}{'stop'})
            {
                $output .= '}';
                $labels .= '}';
                $inCDR   = 0;
                last;
            }
        }
    }
    return($output, $labels);
}

#*************************************************************************
sub UsageDie
{
    print <<__EOF;

abyannotate V1.0 (c) 2021, UCL, Prof Andrew C.R. Martin

Usage: abyannotate [-h][-cdr=cdrdef][-abnum=abnumexe] [seqs.faa]
          -h              This help message
          -cdr=cdrdef     CDR definition to use [default: Kabat]
                          Must be one of 'kabat', 'chothia', 'combined'
                          or 'imgt'
          -abnum=abnumexe Specify the abnum executable
                          [$::abnum]

Input is from standard input if the seqs.faa file is not specified.

abYannotate is a simple program to identify the CDRs in a (set of)
antibody sequences in FASTA format. These can be the Kabat, Chothia,
Combined (Kabat+Chothia), or IMGT definitions. It applies Chothia
numbering using abnum and then identifies the required CDR regions.

__EOF

    exit 0;
}

