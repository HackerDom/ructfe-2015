#!/usr/bin/perl -l

use Mojo::UserAgent;
use Mojo::Util qw/url_escape spurt/;

my $ua       = Mojo::UserAgent->new;
my $base_url = 'https://ructf.org/e/2015';

my $mode = shift // 'local';
mkdir 'images' if $mode eq 'remote';

my $tx = $ua->get("$base_url/teams/info");
die %{$tx->error} unless my $res = $tx->success;

binmode STDOUT, ':utf8';

my $teams = $res->json;
shift @$teams;

for (sort {$a->[0]<=>$b->[0]} @$teams) {
  my $team_id = $_->[0];
  my $a   = 60 + int($team_id / 256);
  my $b   = $team_id % 256;
  my $net = "10.$a.$b.0/24";

  my $escaped_name = url_escape $_->[1];
  my $name = $_->[1];

  if ($mode eq 'remote') {
    my $tx = $ua->get("$base_url/logos/$escaped_name");
    die %{$tx->error} unless my $res = $tx->success;
    spurt $res->body, "images/$name";
  }
  $_->[1] =~ s/'/\\'/g;
  print
"{name => '$_->[1]',\tnetwork => '$net',\thost => 'team${team_id}.e.ructf.org',\tlogo => '/images/$escaped_name'},";
}
