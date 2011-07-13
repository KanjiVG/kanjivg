#!/home/ben/software/install/bin/perl
use warnings;
use strict;
use FindBin;
use XML::Parser;
use Image::SVG::Path 'extract_path_info';
use utf8;
my $string = qr/kanjivg:element="氵"/;
my @files = <$FindBin::Bin/kanjivg/*.svg>;
my @matches;
for my $file (@files) {
    open my $in, "<:encoding(utf8)", $file
        or die $!;
    while (<$in>) {
        if (/$string/) {
            push @matches, $file;
#            print "$file matches.\n";
        }
    }
    close $in or die $!;
}

my $start;
my $count;

my %global;

my $parser = XML::Parser->new (
    Handlers => {
        Start => \& handle_start
    },
);

binmode STDOUT, "utf8";

for my $file (@matches) {
#    print "Parsing '$file'.\n";
    $global{file} = $file;
    $parser->parsefile ($file);
}

sub handle_start
{
    my ($parser, $element, %attr) = @_;
    if ($element eq 'g') {
        my $kvg = $attr{'kanjivg:element'};
        if ($kvg) {
            if ($kvg eq '氵') {
                #print "Found '$kvg' in '$global{file}'\n";
                $start = 1;
                $count = 0;
            }
        }
        else {
            $start = undef;
            $count = 0;
        }
    }
    if ($start && $element eq 'path') {
        $count++;
        if ($count ==  3) {
            my $d = $attr{d};
            my @values = extract_path_info ($d, {
                no_shortcuts => 1,
                absolute => 1,
            });
            my @start = @{$values[0]->{point}};
            my @end = @{$values[-1]->{end}};
            my $x_diff = $end[0] - $start[0];
            my $y_diff = $end[1] - $start[1];
            if ($x_diff < 0 || $y_diff > 0) {
                printf ("file $global{file}: %d %d\n", $x_diff, $y_diff);
            }
        }
    }
}
