#!/usr/bin/perl -s

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

if(! -x $::abnum)
{
    print "Abnum executable not found: $::abnum\n";
    exit 1;
}

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
            my $labels = '';

            ($result, $labels) = Annotate($result, $::cdr);
            if(defined($::html))
            {
                $info = FixHTMLChars($info);
                print "<h2>$info</h2>\n";
                if($::label)
                {
                    $labels = HTMLizeLabels($labels);
                    print "<p class='sequence'>$labels</p>\n";
                }
                $result = HTMLizeSequence($result);
                print "<p class='sequence'>$result</p>\n";
            }
            else
            {
                print "$info\n";
                print "$labels\n" if(defined($::label));
                print "$result\n";
            }
        }
    }
    close($in);
    unlink($tFile);
}


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

sub FixHTMLChars
{
    my($input) = @_;
    $input =~ s/\&/\&amp;/;
    $input =~ s/\>/\&gt;/;
    $input =~ s/\</\&lt;/;
    return($input);
}
