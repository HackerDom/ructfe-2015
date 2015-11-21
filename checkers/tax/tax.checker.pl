#!/usr/bin/perl

use LWP::UserAgent;
use Time::HiRes qw/sleep/;

use constant {
    DEBUG => 0,

    CHECKER_OK => 101,
    CHECKER_NOFLAG => 102,
    CHECKER_MUMBLE => 103,
    CHECKER_DOWN => 104,
    CHECKER_ERROR => 105,
};

my @agents = (
    "Ubuntu APT-HTTP/1.3 (0.7.23.1ubuntu2)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.215 Safari/535.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.205 Safari/534.16",
    "curl/7.19.5 (i586-pc-mingw32msvc) libcurl/7.19.5 OpenSSL/0.9.8l zlib/1.2.3",
    "Emacs-W3/4.0pre.46 URL/p4.0pre.46 (i686-pc-linux; X11)",
    "Mozilla/5.0 (X11; U; Linux i686; en-us) AppleWebKit/531.2+ (KHTML, like Gecko) Safari/531.2+ Epiphany/2.29.5",
    "Mozilla/5.0 (X11; U; Linux armv61; en-US; rv:1.9.1b2pre) Gecko/20081015 Fennec/1.0a1",
    "Mozilla/5.0 (Windows NT 7.0; Win64; x64; rv:3.0b2pre) Gecko/20110203 Firefox/4.0b12pre",
    "Mozilla/5.0 (X11; Linux i686; rv:6.0.2) Gecko/20100101 Firefox/6.0.2",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:5.0) Gecko/20100101 Firefox/5.0",
    "Mozilla/5.0 (Linux; U; Android 1.1; en-gb; dream) AppleWebKit/525.10+ (KHTML, like Gecko) Version/3.0.4 Mobile Safari/523.12.2",
    "Mozilla/4.5 RPT-HTTPClient/0.3-2",
    "Mozilla/5.0 (compatible; Konqueror/4.0; Linux) KHTML/4.0.5 (like Gecko)",
    "Links (2.1pre31; Linux 2.6.21-omap1 armv6l; x)",
    "Lynx/2.8.5dev.16 libwww-FM/2.14 SSL-MM/1.4.1 OpenSSL/0.9.6b",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.9) Gecko/20100508 SeaMonkey/2.0.4",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; InfoPath.3; Creative AutoUpdate v1.40.02)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; GTB6.4; .NET CLR 1.1.4322; FDM; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; Rogers Hi�Speed Internet; (R1 1.3))",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.12) Gecko/20080219 Firefox/2.0.0.12 Navigator/9.0.0.6",
    "Opera/9.80 (J2ME/MIDP; Opera Mini/4.2.13221/25.623; U; en) Presto/2.5.25 Version/10.54",
    "Opera/9.80 (J2ME/MIDP; Opera Mini/5.1.21214/19.916; U; en) Presto/2.5.25",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; en-us) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27",
    "Wget/1.8.1"
);

my @vuln_vec = (1, 2, 2, 2, 2);

($mode, $ip, $id, $flag, $vuln) = @ARGV;
%handlers = ('info' => \&info,
             'check' => \&check, 'put' => \&put, 'get' => \&get);

$ua = LWP::UserAgent->new();
$ua->agent($agents[int rand @agents]);
$ua->cookie_jar({});
push @{$ua->requests_redirectable}, 'POST';

$port = 80;
$url = "http://$ip:$port";
$handlers{$mode}->($id, $flag, $vuln);

sub do_exit {
    my ($code, $msg, $log) = @_;

    if (DEBUG) { $msg = "\nOK" if CHECKER_OK == $code }

    print $msg;
    print STDERR $log;
    exit $code;
}

sub rand_abc {
    my ($min, $max, @abc) = @_;
    join '', map { $abc[int rand @abc] } (0 .. ($min + int rand ($max - $min)))
}

sub rand_str {
    rand_abc(@_, 'a'..'z')
}

sub rand_text {
    rand_abc(@_, ('a'..'z', 'A'..'Z', '0'..'9', ' '))
}

sub _check {
    my ($r, $msg) = @_;
    do_exit(CHECKER_DOWN, "$msg (0)") if $r->code >= 500;
    do_exit(CHECKER_MUMBLE, "$msg (1)") unless $r->is_success;
    do_exit(CHECKER_MUMBLE, "$msg (2)") if $r->content =~ /error/i;
}

sub _register {
    my ($name, $pass) = @_;
    my $r = $ua->post("$url/r", ['name' => $name, 'password' => $pass]);
    _check($r, "Registration error");
    $r
}

sub _login {
    my ($name, $pass) = @_;
    my $r = $ua->post("$url/l", ['name' => $name, 'password' => $pass]);
    _check($r, "Login error");
    $r
}

sub _update_me {
    my ($name, $private) = @_;
    my $r = $ua->post("$url/me", ['name' => $name, 'private' => $private]);
    _check($r, "`Me` page update error");
    $r
}

sub info {
    my %c;
    map { ++ $c{$_} } @vuln_vec;
    print join ':', 'vulns', (map { $c{$_} } sort { $a <=> $b } keys %c);
    do_exit(CHECKER_OK)
}

sub check {
    my ($name, $pass) = (rand_str(8, 16), rand_str(8, 16));

    my $r = $ua->get("$url");
    _check($r, "Retrieve main page error");

    for my $str ('registration', 'login') {
        do_exit(CHECKER_MUMBLE, "Error on main page")
            unless $r->content =~ qr/$str/i;
    }

    $r = _register($name, $pass);
    for my $str ('Upload your tax', $name) {
        do_exit(CHECKER_MUMBLE, "Error while registering user")
            unless $r->content =~ qr/$str/i;
    }

    do_exit(CHECKER_OK)
}

sub put {
    my ($id, $flag, $vuln) = @_;
    $vuln = $vuln_vec[int rand @vuln_vec] unless $vuln;

    my ($name, $pass) = (rand_str(8, 16), rand_str(8, 16));

    _register($name, $pass);

    my $r = $ua->get("$url/me");
    do_exit(CHECKER_MUMBLE, "Error on `me` page") unless $r->is_success;

    $id = "$name:$pass";
    $dname = rand_str(8, 16);
    if ($vuln == 1) {
        $r = _update_me($dname,
                        rand_text(128, 512) . " $flag " . rand_text(128, 384));
        do_exit(CHECKER_MUMBLE, "New personal data not found")
            unless $r->content =~ $dname;

        print "1:$id";
    }
    elsif ($vuln == 2) {
        $r = _update_me($dname, rand_text(256, 896));
        do_exit(CHECKER_MUMBLE, "Error while updating `me` page")
            unless $r->is_success;

        my $fn = join ':', rand_str(5, 8), rand_str(2, 4);
        my $cont = join ' ', rand_text(512, 1024), $flag, rand_text(512, 1024);
        $r->content =~ /"(.*?)">\s*$dname/;
        $r = $ua->post("$url/u", Content_Type => 'form-data',
            Content => ['pdata' => $1, Filedata => [
                undef, $fn, Content_Type => 'text/plain', Content => $cont]]);
        do_exit(CHECKER_MUMBLE, "Error while uploading file")
            unless $r->is_success;

        $r->content =~ /href="(.*?)">\s*here\s*<\/a> to download/i;

        print "2:$id:$1";
    }
    else {
        do_exit(CHECKER_ERROR, "<PUT> Unknown flag type");
    }

    do_exit(CHECKER_OK)
}

sub get {
    my ($id, $flag, $vuln) = @_;
    my ($t, $rest) = split /:/, $id, 2;
    # do_exit(CHECKER_ERROR, "flag type mismatch") if $vuln != $t;

    # Hack
    sleep(1);

    if ($t == 1) {
        my ($name, $pass) = split /:/, $rest;
        _login($name, $pass);

        my $r = $ua->get("$url/me");
        do_exit(CHECKER_MUMBLE, "Error on `me` page") unless $r->is_success;

        my $cont = $r->content;
        do_exit(CHECKER_NOFLAG, "Flag not found", "Content = '$cont'")
            unless $cont =~ qr/$flag/;
    }
    elsif ($t == 2) {
        my ($name, $pass, $link) = split /:/, $rest;
        _login($name, $pass);

        my $r = $ua->get("$url/$link");
        do_exit(CHECKER_MUMBLE, "Error while downloading file")
            unless $r->is_success;

        my $cont = $r->content;
        do_exit(CHECKER_NOFLAG, "Flag not found", "Content = '$cont'")
            unless $cont =~ qr/$flag/;
    }
    else {
        do_exit(CHECKER_ERROR, "<GET> Unknown flag type");
    }

    do_exit(CHECKER_OK)
}

