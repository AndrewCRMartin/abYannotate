#!/usr/bin/perl
use strict;

my $head = '';
my $seq = '';
my $gothead = 0;
while(<>)
{
    chomp;
    if(/^>/)
    {
        $head = $_;
        $head =~ s/^\>P1;/\>/;
        $head =~ s/\s+$//;
        $head .= "|";
        $head .= <>;
        chomp $head;
        $seq = '';
        $gothead=1;
    }
    else
    {
        $seq .= $_;
        if($seq =~ /\*/) # End of sequence
        {
            if(index($seq, '?') == -1)
            {
                if(!$gothead)
                {
                    $head =~ s/\|/_2\|/;
                }
                $seq =~ s/\*//;
                print "$head\n";
                print "$seq\n\n";
            }
            $gothead = 0;
            $seq='';
        }
    }
}
