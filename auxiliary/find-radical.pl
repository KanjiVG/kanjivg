#!/home/ben/software/install/bin/perl
use warnings;
use strict;
use FindBin;
use XML::Parser;
use Image::SVG::Path 'extract_path_info';
use utf8;
use KanjiVG qw/find_element/;
binmode STDOUT, "utf8";
my %data;
my $element = '氵';


sub handle_start
{
    my ($data, $count, $d) = @_;
    if ($count == 3) {
        my @values = extract_path_info ($d, {
            no_shortcuts => 1,
            absolute => 1,
        });
        my @start = @{$values[0]->{point}};
        my @end = @{$values[-1]->{end}};
        my $x_diff = $end[0] - $start[0];
        my $y_diff = $end[1] - $start[1];
#        if ($x_diff < 0 || $y_diff > 0) {
            printf ("file $global{file}: %d %d\n", $x_diff, $y_diff);
#        }
    }
}
