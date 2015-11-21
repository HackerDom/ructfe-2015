#!/usr/bin/perl -l

use Mojo::JSON 'j';
use Mojo::UserAgent;
use Mojo::Util qw/url_escape spurt/;

my $ua       = Mojo::UserAgent->new;
my $base_url = 'https://ructf.org/e/2015';

mkdir 'images';

my $tx = $ua->get("$base_url/teams/info");
die %{$tx->error} unless my $res = $tx->success;

my $teams = $res->json;
shift @$teams;

my $team_id = 1;
for (@$teams) {
  my $a   = 60 + int($team_id / 256);
  my $b   = $team_id % 256;
  my $net = "10.$a.$b.0/24";

  my $escaped_name = url_escape $_->[1];

  my $tx = $ua->get("$base_url/logos/$escaped_name");
  die %{$tx->error} unless my $res = $tx->success;
  spurt $res->body, "images/$escaped_name";

  my $team =
    {name => $_->[1], network => $net, host => "team${team_id}.e.ructf.org", logo => "/images/$escaped_name"};
  print j $team;

  $team_id++;
}
