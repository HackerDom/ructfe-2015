use strict;
use File::Copy;

my $IN="30";
my $TEMP="temp";
my $OUT="bundles";
my $COUNT=30;

unlink glob "$OUT/*.*";

for my $i (1..$COUNT) {
	print ">>> Making dev bundle $i of $COUNT ... \n";
	unlink glob "$TEMP/*.*";
	copy("$IN/dev$i.key", "$TEMP/dev$i.key") or die;
	copy("$IN/dev$i.crt", "$TEMP/dev$i.crt") or die;
	copy("dev-ta.key",    "$TEMP/dev-ta.key") or die;
	copy("ca.crt",        "$TEMP/ca.crt") or die;
	open FIN, "template.ovpn" or die;
	open FOUT, ">$TEMP/dev$i.ovpn" or die;
	while (<FIN>) {
		s/<N>/$i/g;
		print FOUT $_;
	}
	close FIN;
	close FOUT;
	print `7z a -bd $OUT\\dev$i.zip .\\temp\\*.*`;
}
