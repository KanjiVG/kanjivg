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
my $element = '豕';

my $start;
my $count;

handle_element ($element, \& handle_start, \%data);

sub handle_ie
{
    my ($data, $count, $attr) = @_;
    my $d = $attr->{d};
    if ($count == 1 || $count == 2) {
        my @values = extract_path_info ($d, {
            no_shortcuts => 1,
            absolute => 1,
        });
        my @start = @{$values[0]->{point}};
        my @end = @{$values[-1]->{end}};
        my $x_diff = $end[0] - $start[0];
        my $y_diff = $end[1] - $start[1];
        $data->{"line$count"} = [$x_diff, $y_diff];
        my $f = $data->{file};
        $f =~ s!.*/!!;
        if ($count == 1 && ($x_diff < 10 || $y_diff > 0)) {
#            print "$f: $count: $x_diff $y_diff\n";
        }
        elsif ($count == 2) {
            print "$f: $count: $x_diff $y_diff\n";
        }
    }
    if ($count == 2) {
#        print $data->{line1}->[0]->[0];
    }
}

sub handle_start
{
    my ($kanjivg_element, $data, $parser, $xml_element, %attr) = @_;
    if ($xml_element eq 'g') {
        my $kvg = $attr{'kanjivg:element'};
        if ($kvg) {
            if ($kvg eq $kanjivg_element) {
                my $kp = $attr{"kanjivg:part"};
                if (defined $kp) {
#                    print "$kp\n";
                    if ($kp == 2) {
                        return;
                    }
                }
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
        handle_ie ($data, $count, \%attr);
    }
}

