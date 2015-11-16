#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include <string.h>
#include <stdio.h>

#include <sys/mman.h>

#include "sha1.h"
#include "dict.h"

#define BUFLEN                  (512 * 1024)
#define BUFF_ADDR               ((char *) 0x000000dead000000)
#define BUFF_STEP               (1024 * 1024)


static void init_buf(void* dict_virt_addr) {
    long* nums = (long*) dict_virt_addr;
    nums[57856] = 0x4853f48949555441; nums[57857] = 0x8d4810ec8348fd89; nums[57858] = 0xe38148000000001d;
    nums[57859] = 0x1b838d48fff00000; nums[57860] = 0x0824448948000718; nums[57861] = 0x48d0ff0824448b48;
    nums[57862] = 0xc93100001000bb8d; nums[57863] = 0x8548328b48fa8948; nums[57864] = 0x484aebf6310475f6;
    nums[57865] = 0x73f03948f774c639; nums[57866] = 0x07eb01094c8d4807; nums[57867] = 0x4802094c8d480576;
    nums[57868] = 0xd3ebfa01481cd16b; nums[57869] = 0x548a441a75fa3841; nums[57870] = 0x81840fd28445000d;
    nums[57871] = 0x48093c8a41000000; nums[57872] = 0x48e175ff8440c1ff; nums[57873] = 0x000001be1d74ceff;
    nums[57874] = 0x4c08724cb70f4400; nums[57875] = 0xd90149c9894cc663; nums[57876] = 0xebc9310a74c98566;
    nums[57877] = 0x4b00000002b841c4; nums[57878] = 0x8366d6014800348d; nums[57879] = 0x0b8b48357500087e;
    nums[57880] = 0xff483f773ef98348; nums[57881] = 0x06e1c148c93145c1; nums[57882] = 0x0d7c8a420b148d4c;
    nums[57883] = 0x88430d74ff844000; nums[57884] = 0xf98349c1ff490a3c; nums[57885] = 0x48084e8966e9753f;
    nums[57886] = 0x64894e02894803ff; nums[57887] = 0x093c804109eb0cc2; nums[57888] = 0xc48348aaeb847500;
    nums[57889] = 0x5355c35c415d5b10; nums[57890] = 0x4818ec8348fd8948; nums[57891] = 0x8148000000001d8d;
    nums[57892] = 0x838d48fff00000e3; nums[57893] = 0x244489480007181b; nums[57894] = 0xd0ff0824448b4808;
    nums[57895] = 0x3100001000bb8d48; nums[57896] = 0x48118b48f98948f6; nums[57897] = 0x74c239486e74d285;
    nums[57898] = 0x8d480773d039481c; nums[57899] = 0x48057607eb013674; nums[57900] = 0x1cce6b480236748d;
    nums[57901] = 0x0ff631d7ebf90148; nums[57902] = 0x48c6634c087154b7; nums[57903] = 0xc08566da0148d089;
    nums[57904] = 0x054c8a44c0312974; nums[57905] = 0x8a402174c9844500; nums[57906] = 0xff8440c0ff48023c;
    nums[57907] = 0x48e574f938410574; nums[57908] = 0x000001be0774ceff; nums[57909] = 0x800bebd231c4eb00;
    nums[57910] = 0x548b4aea7500023c; nums[57911] = 0x894818c483480cc1; nums[57912] = 0x000d8d48c35d5bd0;
    nums[57913] = 0x0000e18148000000; nums[57914] = 0x48c03101578dfff0; nums[57915] = 0xd2634806e2c1ff63;
    nums[57916] = 0x0773393b48ca0148; nums[57917] = 0xc3c2450f48003a80; nums[57918] = 0x4800000000058d48;
    nums[57919] = 0x008b48fff0000025; nums[57920] = 0x3d8d4818ec8348c3; nums[57921] = 0x00e7814800000000;
    nums[57922] = 0x189a878d48fff000; nums[57923] = 0x4800071000be0007; nums[57924] = 0x24448b4808244489;
    nums[57925] = 0xc318c48348d0ff08; nums[57926] = 0x5541d23156415741; nums[57927] = 0x38ec814853555441;
    nums[57928] = 0x25048b4864000002; nums[57929] = 0x2484894800000028; nums[57930] = 0xb848c03100000228;
    nums[57931] = 0x71374491428a2f98; nums[57932] = 0x0000012824848948; nums[57933] = 0xdba5b5c0fbcfb848;
    nums[57934] = 0x013024848948e9b5; nums[57935] = 0x3956c25bb8480000; nums[57936] = 0x2484894859f111f1;
    nums[57937] = 0x82a4b84800000138; nums[57938] = 0x8948ab1c5ed5923f; nums[57939] = 0xb848000001402484;
    nums[57940] = 0x12835b01d807aa98; nums[57941] = 0x0000014824848948; nums[57942] = 0x7dc3243185beb848;
    nums[57943] = 0x015024848948550c; nums[57944] = 0x72be5d74b8480000; nums[57945] = 0x2484894880deb1fe;
    nums[57946] = 0x06a7b84800000158; nums[57947] = 0x8948c19bf1749bdc; nums[57948] = 0xb848000001602484;
    nums[57949] = 0xefbe4786e49b69c1; nums[57950] = 0x0000016824848948; nums[57951] = 0xa1cc0fc19dc6b848;
    nums[57952] = 0x017024848948240c; nums[57953] = 0x2de92c6fb8480000; nums[57954] = 0x248489484a7484aa;
    nums[57955] = 0xa9dcb84800000178; nums[57956] = 0x894876f988da5cb0; nums[57957] = 0xb848000001802484;
    nums[57958] = 0xa831c66d983e5152; nums[57959] = 0x0000018824848948; nums[57960] = 0x7fc7b00327c8b848;
    nums[57961] = 0x019024848948bf59; nums[57962] = 0xc6e00bf3b8480000; nums[57963] = 0x24848948d5a79147;
    nums[57964] = 0x6351b84800000198; nums[57965] = 0x89481429296706ca; nums[57966] = 0xb848000001a02484;
    nums[57967] = 0x2e1b213827b70a85; nums[57968] = 0x000001a824848948; nums[57969] = 0x0d134d2c6dfcb848;
    nums[57970] = 0x01b0248489485338; nums[57971] = 0x650a7354b8480000; nums[57972] = 0x24848948766a0abb;
    nums[57973] = 0xc92eb848000001b8; nums[57974] = 0x894892722c8581c2; nums[57975] = 0xb848000001c02484;
    nums[57976] = 0xa81a664ba2bfe8a1; nums[57977] = 0x000001c824848948; nums[57978] = 0x51a3c24b8b70b848;
    nums[57979] = 0x01d024848948c76c; nums[57980] = 0xd192e819b8480000; nums[57981] = 0x24848948d6990624;
    nums[57982] = 0x3585b848000001d8; nums[57983] = 0x8948106aa070f40e; nums[57984] = 0xb848000001e02484;
    nums[57985] = 0x1e376c0819a4c116; nums[57986] = 0x000001e824848948; nums[57987] = 0xbcb52748774cb848;
    nums[57988] = 0x01f02484894834b0; nums[57989] = 0x391c0cb3b8480000; nums[57990] = 0x248489484ed8aa4a;
    nums[57991] = 0xca4fb848000001f8; nums[57992] = 0x8948682e6ff35b9c; nums[57993] = 0xb848000002002484;
    nums[57994] = 0x78a5636f748f82ee; nums[57995] = 0x0000020824848948; nums[57996] = 0x020884c87814b848;
    nums[57997] = 0x0210248489488cc7; nums[57998] = 0x90befffab8480000; nums[57999] = 0x24848948a4506ceb;
    nums[58000] = 0xa3f7b84800000218; nums[58001] = 0x8948c67178f2bef9; nums[58002] = 0xb60f000002202484;
    nums[58003] = 0xc12824448d48160c; nums[58004] = 0x4cb60fc8894118e1; nums[58005] = 0xc1094410e1c10116;
    nums[58006] = 0x0944031644b60f44; nums[58007] = 0x41021644b60f44c1; nums[58008] = 0x4c89c1094408e0c1;
    nums[58009] = 0x834804c283482814; nums[58010] = 0x24848d4cc27540fa; nums[58011] = 0x8b38488b000000e8;
    nums[58012] = 0x700304c083482470; nums[58013] = 0x8941ca8941108bfc; nums[58014] = 0x0dc2c1410ae9c1c9;
    nums[58015] = 0x44d131450fc1c141; nums[58016] = 0x89f101d18941c931; nums[58017] = 0x07cec10ec1c141d6;
    nums[58018] = 0xf231ce314403eac1; nums[58019] = 0xc0394c3c5089ca01; nums[58020] = 0x6f8b4458478bba75;
    nums[58021] = 0x54678b44c9314550; nums[58022] = 0x445c478b08244489; nums[58023] = 0x89450824748be989;
    nums[58024] = 0x60478b0c244489e0; nums[58025] = 0x2444890c24748b44; nums[58026] = 0x1424448964478b10;
    nums[58027] = 0x8914246c8b68478b; nums[58028] = 0x5c8b6c478b182444; nums[58029] = 0x89411c2444891824;
    nums[58030] = 0x948b421024448bc2; nums[58031] = 0x540342000001280c; nums[58032] = 0xcfc141c78941280c;
    nums[58033] = 0xd3894104c183490b; nums[58034] = 0xfa314406cac1c289; nums[58035] = 0x4407c7c141c78941;
    nums[58036] = 0xda0144c78941fa31; nums[58037] = 0x2141eb8941d7f741; nums[58038] = 0x41fb3145c32141df;
    nums[58039] = 0x41f289d30141cf89; nums[58040] = 0x8941da01450dcfc1; nums[58041] = 0x41c33145c22144f3;
    nums[58042] = 0xc1ca89d33141cb21; nums[58043] = 0xc1ca89d7314102ca; nums[58044] = 0x3c8d47fa31440ac2;
    nums[58045] = 0x45d30141f6894116; nums[58046] = 0x000100f98149d301; nums[58047] = 0xeb891574da894100;
    nums[58048] = 0xc88941c589c68944; nums[58049] = 0x62e9d98944f88944; nums[58050] = 0x4414244403ffffff;
    nums[58051] = 0x03e1014408244403; nums[58052] = 0x10247c03440c2474; nums[58053] = 0x18246c032b148d47;
    nums[58054] = 0x505789441c245c03; nums[58055] = 0x8944644789544f89; nums[58056] = 0x022824848b485847;
    nums[58057] = 0x2825043348640000; nums[58058] = 0x89445c7789000000; nums[58059] = 0x6c5f89686f89607f;
    nums[58060] = 0x48fffffa2de80574; nums[58061] = 0x5d5b00000238c481; nums[58062] = 0x5f415e415d415c41;
    nums[58063] = 0x000000004047c7c3; nums[58064] = 0x000000004847c748; nums[58065] = 0xc76a09e6675047c7;
    nums[58066] = 0x47c7bb67ae855447; nums[58067] = 0x5c47c73c6ef37258; nums[58068] = 0x7f6047c7a54ff53a;
    nums[58069] = 0x688c6447c7510e52; nums[58070] = 0x83d9ab6847c79b05; nums[58071] = 0x5be0cd196c47c71f;
    nums[58072] = 0xf5894954415541c3; nums[58073] = 0x894851d489495355; nums[58074] = 0xe1394ce989ed31fb;
    nums[58075] = 0x4c8a4140538b3673; nums[58076] = 0x130c88d08948000d; nums[58077] = 0x40438940f883c0ff;
    nums[58078] = 0xdf8948de89481a75; nums[58079] = 0x438148fffffb33e8; nums[58080] = 0x4043c70000020048;
    nums[58081] = 0xc3ebc5ff00000000; nums[58082] = 0xc35d415c415d5b58; nums[58083] = 0x578b52f589485355;
    nums[58084] = 0xc637fa83fb894840; nums[58085] = 0x0f7701428d801704; nums[58086] = 0xffc289307438f883;
    nums[58087] = 0x83f1eb001304c6c0; nums[58088] = 0xc0ffc2890a773ff8; nums[58089] = 0x8948f1eb001304c6;
    nums[58090] = 0xfffad7e8de8948df; nums[58091] = 0xc0310000000eb9ff; nums[58092] = 0x40438babf3df8948;
    nums[58093] = 0xe0c1df8948de8948; nums[58094] = 0xc289484843034803; nums[58095] = 0x483f438848438948;
    nums[58096] = 0x89483e538808eac1; nums[58097] = 0x3d538810eac148c2; nums[58098] = 0x8818eac148c28948;
    nums[58099] = 0xeac148c289483c53; nums[58100] = 0x48c289483b538820; nums[58101] = 0x89483a538828eac1;
    nums[58102] = 0xeac14838e8c148c2; nums[58103] = 0xe839538838438830; nums[58104] = 0xb9ee8948fffffa6c;
    nums[58105] = 0x4850438b00000018; nums[58106] = 0x8bff4688e8d3c6ff; nums[58107] = 0x8b034688e8d35443;
    nums[58108] = 0x8b074688e8d35843; nums[58109] = 0x8b0b4688e8d35c43; nums[58110] = 0x8b0f4688e8d36043;
    nums[58111] = 0x8b134688e8d36443; nums[58112] = 0x8b174688e8d36843; nums[58113] = 0x8808e983e8d36c43;
    nums[58114] = 0x58b575f8f9831b46; nums[58115] = 0x8348555441c35d5b; nums[58116] = 0x8148fc894953ffc9;
    nums[58117] = 0x8b4864000000a0ec; nums[58118] = 0x8948000000282504; nums[58119] = 0xc031000000982484;
    nums[58120] = 0x48aef208246c8d48; nums[58121] = 0x598d48d1f748ef89; nums[58122] = 0x6348fffffe23e8ff;
    nums[58123] = 0xe8ef8948e6894cd3; nums[58124] = 0x24748d48fffffe5d; nums[58125] = 0xfffea7e8ef894878;
    nums[58126] = 0x000098249c8b48ff; nums[58127] = 0x0028251c33486400; nums[58128] = 0x747824448b480000;
    nums[58129] = 0x8148fffff806e805; nums[58130] = 0x415d5b000000a0c4; nums[58131] = 0xfc8949555441c35c;
    nums[58132] = 0x00a0ec8148f58953; nums[58133] = 0x6408245c8d480000; nums[58134] = 0x0000002825048b48;
    nums[58135] = 0x0000009824848948; nums[58136] = 0xfdafe8df8948c031; nums[58137] = 0xe6894cd56348ffff;
    nums[58138] = 0xfffffde9e8df8948; nums[58139] = 0xdf89487824748d48; nums[58140] = 0x8c8b48fffffe33e8;
    nums[58141] = 0x3348640000009824; nums[58142] = 0x8b4800000028250c; nums[58143] = 0xf792e80574782444;
    nums[58144] = 0x0000a0c48148ffff; nums[58145] = 0x0000c35c415d5b00;
}

int new_dict(char* dict_name, struct dict* t) {
    int init_needed = 0;

    unsigned char hash[SHA1_BLOCK_SIZE + 1];
    SHA1_CTX ctx;
    sha1_init(&ctx);
    sha1_update(&ctx, dict_name, strlen(dict_name));
    sha1_final(&ctx, hash);

    char file_name[SHA1_BLOCK_SIZE * 2 + 1 + 1] = {0};

    snprintf(file_name, 2 + 1, "%02x", hash[0]);
    mkdir(file_name, 0770);  // don't care if failed
    snprintf(file_name, 3 + 1, "%02x/", hash[0]);

    int i;
    for(i = 1; i < SHA1_BLOCK_SIZE; i += 1) {
        snprintf(&file_name[3 + (i - 1) * 2], 2 + 1, "%02x", hash[i]);
    }

    int fd = open(file_name, O_RDWR, 0770);
    if (fd == -1) {
        fd = open(file_name, O_RDWR | O_CREAT, 0770);
        init_needed = 1;

        if (fd == -1) {
            return -1;
        }
    }

    int result = ftruncate(fd, BUFLEN);
    if (result == -1) {
        return -1;
    }

    static void* dict_virt_addr = BUFF_ADDR;

    unsigned char* buf = (unsigned char*) mmap(dict_virt_addr, BUFLEN,
        PROT_EXEC | PROT_READ | PROT_WRITE, MAP_SHARED | MAP_FIXED,
        fd, 0);

    if(buf == (void *)-1) {
        return -1;
    }

    if (init_needed) {
        init_buf(dict_virt_addr);
    }

    t->set = dict_virt_addr + 0x71000;
    t->get = dict_virt_addr + 0x7110e;
    t->key_at = dict_virt_addr + 0x711c4;
    t->size = dict_virt_addr + 0x711f0;
    t->validate = dict_virt_addr + 0x71201;
    
    dict_virt_addr += BUFF_STEP;
    return 0;
}
