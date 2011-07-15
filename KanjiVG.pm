package KanjiVG;
use parent Exporter;
our @EXPORT_OK = qw/handle_element/;
use warnings;
use strict;
use Carp;

my $dir = "$FindBin::Bin/kanjivg";

sub find_element
{
    my ($element) = @_;
    if (! defined $element) {
        croak "No element";
    }
    my $string = qr/kanjivg:element="$element"/;
    my @files = <$dir/*.svg>;
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
    return @matches;
}

sub handle_element
{
    my ($element, $handle_start, $data) = @_;
    my @matches = find_element ($element);
    if (ref $data ne 'HASH') {
        croak "Give me a hash ref";
    }
    my $parser = XML::Parser->new (
        Handlers => {
            Start => sub { &{$handle_start} ($element, $data, @_)},
        },
    );
    for my $file (@matches) {
#    print "Parsing '$file'.\n";
        $data->{file} = $file;
        $parser->parsefile ($file);
    }
}



1;
