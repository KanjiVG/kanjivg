#!/usr/bin/env perl
use warnings;
use strict;
use utf8;
use FindBin '$Bin';
use v5.32;
no warnings qw(experimental::signatures);
use feature qw(signatures say);
# Requires install. "cpanm JSON::Create"
use JSON::Create 'write_json';

# The index we write to the file.
my %index;
my @files = <$Bin/kanji/*.svg>;
for my $file (@files) {
    my ($kanji, $ex) = file_to_kanji ($file);
    if (! $kanji) {
	next;
    }
    my $tfile = $file;
    $tfile =~ s!.*/!!;
    push @{$index{$kanji}}, $tfile;
}
write_json ("$Bin/kvg-index.json", \%index, indent => 1, sort => 1);
exit;

sub file_to_kanji ($file) {
    if ($file !~ m!([0-9a-f]{5})(-.*)?\.svg!) {
	warn "Could not get kanji from $file";
	return (undef, undef);
    }
    return chr (hex ($1)), $2;
}
