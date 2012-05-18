#!/home/ben/software/install/bin/perl
use warnings;
use strict;
use FindBin;
use XML::Parser;
use Image::SVG::Path 'extract_path_info';
use utf8;
use KanjiVG qw/handle_element/;
binmode STDOUT, "utf8";
my %data;
my $element = '氵';

my $start;
my $count;

handle_element ($element, \& handle_start, \%data);

sub handle_sanzui
{
    my ($data, $count, $attr) = @_;
    if ($count == 3) {
    my $d = $attr->{d};
        my @values = extract_path_info ($d, {
            no_shortcuts => 1,
            absolute => 1,
        });
        my @start = @{$values[0]->{point}};
        my @end = @{$values[-1]->{end}};
        my $x_diff = $end[0] - $start[0];
        my $y_diff = $end[1] - $start[1];
#        if ($x_diff < 0 || $y_diff > 0) {
            printf ("file $data->{file}: %d %d\n", $x_diff, $y_diff);
#        }
    }
}

sub handle_start
{
    my ($kanjivg_element, $data, $parser, $xml_element, %attr) = @_;
    if ($xml_element eq 'g') {
        my $kvg = $attr{'kanjivg:element'};
        if ($kvg) {
            if ($kvg eq $kanjivg_element) {
#                print "Found '$kvg' in '$data->{file}'\n";
                $start = 1;
                $count = 0;
            }
        }
        else {
            $start = undef;
            $count = 0;
        }
    }
    elsif ($start && $xml_element eq 'path') {
        $count++;
        handle_sanzui ($data, $count, \%attr);
    }
}

