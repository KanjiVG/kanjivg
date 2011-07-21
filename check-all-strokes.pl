#!/home/ben/software/install/bin/perl
use warnings;
use strict;
use XML::Parser;
use FindBin;
use Image::SVG::Path 'extract_path_info';
use utf8;
my $dir = "$FindBin::Bin/kanjivg";

# The grep only allows the "normal" files from the complete list of
# files.

my @files = grep /\/[0-9a-f]+\.svg$/, <$dir/*.svg>;

my %stroke_types;

my %global;

my %angles;

# List of errors which are known to come from bad information about
# stroke types.

my @known_bad_elements = qw/冬 羽 尽 辛 手 羊 冫 半/;

my %known_bad_elements = map {$_ => 1} @known_bad_elements;

#print keys %known_bad_elements;

$global{known_bad_elements} = \%known_bad_elements;

my $parser = XML::Parser->new (
    Handlers => {
        Start => sub { &{handle_start} (\%global, @_) },
    },
);

# This doesn't let us use current_line.
#$global{parser} = $parser;

for my $file (@files) {
#for my $file (qw!kanjivg/087bd.svg!) {
    $global{file} = $file;
    $global{bad_element} = undef;
    $parser->parsefile ($file);
}

#for my $t (sort keys %stroke_types) {
#    print "$t\n";
#}

my %average;

for my $t (sort keys %angles) {
    if ($t eq 'None') {
        next;
    }
    my $total_angle = 0;
    my $n = 0;
    for my $se (@{$angles{$t}}) {
        my ($start, $end) = @$se;
        my $angle = atan2 ($end->[1] - $start->[1], $end->[0] - $start->[0]);
        $total_angle += $angle;
        $n++;
    }
    $average{$t} = $total_angle / $n;

# The following line prints out the "type" field and the average angle
# in radians.

#    print "$t $average{$t}\n";

}

my $limit = 1.0;

for my $t (sort keys %angles) {
    if ($t eq 'None') {
        next;
    }
    for my $se (@{$angles{$t}}) {
        my ($start, $end, $location) = @$se;
        my $angle = atan2 ($end->[1] - $start->[1], $end->[0] - $start->[0]);
        if ($angle - $average{$t} > $limit) {
            print $location, "more than $limit radian from average.\n"
        }
    }
}

exit;

sub handle_start
{
    my ($global_ref, $parser, $element, %attr) = @_;
    if ($global_ref->{bad_element}) {
        return;
    }

    # Use the expat parser so we can use current_line.
    $global_ref->{parser} = $parser;
    if ($element eq 'path') {
        gather_path_info ($global_ref, \%attr);
    }
    elsif ($element eq 'g') {
        if ($attr{id} =~ /^([0-9a-f]+)$/) {
            $global_ref->{kanji_id} = $attr{id};
        }
        my $el = $attr{"kanjivg:element"};
#        print "element $el\n";
        if (defined $el) {
            if ($global_ref->{known_bad_elements}->{$el}) {
#                print "Known bad element $el in $global_ref->{file}.\n";
                $global_ref->{bad_element} = 1;
            }
        }
    }
}

# Get the location for warning messages.

sub location
{
    my ($global) = @_;
    my $l = '';
    $l .= $global->{file};
    $l .= ":";
    $l .= $global->{parser}->current_line ();
    $l .= ": ";
    return $l;
}

sub gather_path_info
{
    my ($global_ref, $attr_ref) = @_;
    my $type = $attr_ref->{'kanjivg:type'};
    if (! $type) {
        warn location ($global_ref), "no type.\n";
        return;
    }
    $type =~ s/([^[:ascii:]])/"{" . sprintf ("%X", ord $1) . "}"/ge;
    $stroke_types{$type}++;
    my $d = $attr_ref->{d};
    if (! $d) {
        warn location ($global_ref), "no path.\n";
        return;
    }
    my @info = extract_path_info ($d, {absolute => 1, no_shortcuts => 1});
    my $start = $info[0]->{point};
    my $end = $info[-1]->{end};
    if (! $start || ! $end) {
        warn location ($global_ref), "parse failed for '$d': no start/end";
        return;
    }
    push @{$angles{$type}}, [$start, $end, location ($global_ref)];
}
