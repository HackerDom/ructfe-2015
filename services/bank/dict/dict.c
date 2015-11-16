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
    nums[57856] = 0x4853fc8949555441; nums[57857] = 0x8d4810ec8348ee63; nums[57858] = 0xe38148000000001d;
    nums[57859] = 0x12838d48fff00000; nums[57860] = 0x0824448948000718; nums[57861] = 0x48d0ff0824448b48;
    nums[57862] = 0xc93100001000bb8d; nums[57863] = 0x8548328b48fa8948; nums[57864] = 0x4845ebff310475f6;
    nums[57865] = 0x73f03948f774c639; nums[57866] = 0x07eb01094c8d4807; nums[57867] = 0x4802094c8d480576;
    nums[57868] = 0xd3ebfa01481cd16b; nums[57869] = 0x148a451575ca3845; nums[57870] = 0x8a447e74d284450c;
    nums[57871] = 0xc98445c1ff480e0c; nums[57872] = 0xbf1c74cfff48e675; nums[57873] = 0x7a74b70f00000001;
    nums[57874] = 0x48f18948c7634c08; nums[57875] = 0x310a74c98566de01; nums[57876] = 0x000002b841caebc9;
    nums[57877] = 0xd70148003c8d4b00; nums[57878] = 0x48337500087f8366; nums[57879] = 0x3c773ef983480b8b;
    nums[57880] = 0xe1c148f631c1ff48; nums[57881] = 0x0c8a450b148d4c06; nums[57882] = 0x88450d74c9844534;
    nums[57883] = 0xfe8348c6ff48320c; nums[57884] = 0x48084f8966ea753f; nums[57885] = 0x6c894a02894803ff;
    nums[57886] = 0x000e3c8008eb0cc2; nums[57887] = 0x10c48348adeb8875; nums[57888] = 0x485355c35c415d5b;
    nums[57889] = 0x8d4818ec8348fd89; nums[57890] = 0xe38148000000001d; nums[57891] = 0x12838d48fff00000;
    nums[57892] = 0x0824448948000718; nums[57893] = 0x48d0ff0824448b48; nums[57894] = 0xc93100001000bb8d;
    nums[57895] = 0x8548328b48fa8948; nums[57896] = 0x2074c639482174f6; nums[57897] = 0x4c8d480773f03948;
    nums[57898] = 0x8d48057607eb0109; nums[57899] = 0x481cd16b4802094c; nums[57900] = 0x4cebc031d7ebfa01;
    nums[57901] = 0x4c08724cb70ff631; nums[57902] = 0xd90148c88948c663; nums[57903] = 0x00000000b8c08566;
    nums[57904] = 0x4500054c8a443274; nums[57905] = 0x013c8a401d74c984; nums[57906] = 0x0574ff8440c0ff48;
    nums[57907] = 0xceff48e574f93841; nums[57908] = 0xeb00000001bec274; nums[57909] = 0x4aee7500013c80c1;
    nums[57910] = 0x18c483480cc2448b; nums[57911] = 0x00000d8d48c35d5b; nums[57912] = 0xf00000e181480000;
    nums[57913] = 0x6348c03101578dff; nums[57914] = 0x48d2634806e2c1ff; nums[57915] = 0x800773393b48ca01;
    nums[57916] = 0x48c3c2450f48003a; nums[57917] = 0x254800000000058d; nums[57918] = 0xc3008b48fff00000;
    nums[57919] = 0x003d8d4818ec8348; nums[57920] = 0x0000e78148000000; nums[57921] = 0x071891878d48fff0;
    nums[57922] = 0x894800071000be00; nums[57923] = 0x0824448b48082444; nums[57924] = 0x41c318c48348d0ff;
    nums[57925] = 0x415541d231564157; nums[57926] = 0x0238ec8148535554; nums[57927] = 0x2825048b48640000;
    nums[57928] = 0x2824848948000000; nums[57929] = 0x98b848c031000002; nums[57930] = 0x4871374491428a2f;
    nums[57931] = 0x4800000128248489; nums[57932] = 0xb5dba5b5c0fbcfb8; nums[57933] = 0x00013024848948e9;
    nums[57934] = 0xf13956c25bb84800; nums[57935] = 0x382484894859f111; nums[57936] = 0x3f82a4b848000001;
    nums[57937] = 0x848948ab1c5ed592; nums[57938] = 0x98b8480000014024; nums[57939] = 0x4812835b01d807aa;
    nums[57940] = 0x4800000148248489; nums[57941] = 0x0c7dc3243185beb8; nums[57942] = 0x0001502484894855;
    nums[57943] = 0xfe72be5d74b84800; nums[57944] = 0x582484894880deb1; nums[57945] = 0xdc06a7b848000001;
    nums[57946] = 0x848948c19bf1749b; nums[57947] = 0xc1b8480000016024; nums[57948] = 0x48efbe4786e49b69;
    nums[57949] = 0x4800000168248489; nums[57950] = 0x0ca1cc0fc19dc6b8; nums[57951] = 0x0001702484894824;
    nums[57952] = 0xaa2de92c6fb84800; nums[57953] = 0x78248489484a7484; nums[57954] = 0xb0a9dcb848000001;
    nums[57955] = 0x84894876f988da5c; nums[57956] = 0x52b8480000018024; nums[57957] = 0x48a831c66d983e51;
    nums[57958] = 0x4800000188248489; nums[57959] = 0x597fc7b00327c8b8; nums[57960] = 0x00019024848948bf;
    nums[57961] = 0x47c6e00bf3b84800; nums[57962] = 0x9824848948d5a791; nums[57963] = 0xca6351b848000001;
    nums[57964] = 0x8489481429296706; nums[57965] = 0x85b848000001a024; nums[57966] = 0x482e1b213827b70a;
    nums[57967] = 0x48000001a8248489; nums[57968] = 0x380d134d2c6dfcb8; nums[57969] = 0x0001b02484894853;
    nums[57970] = 0xbb650a7354b84800; nums[57971] = 0xb824848948766a0a; nums[57972] = 0xc2c92eb848000001;
    nums[57973] = 0x84894892722c8581; nums[57974] = 0xa1b848000001c024; nums[57975] = 0x48a81a664ba2bfe8;
    nums[57976] = 0x48000001c8248489; nums[57977] = 0x6c51a3c24b8b70b8; nums[57978] = 0x0001d024848948c7;
    nums[57979] = 0x24d192e819b84800; nums[57980] = 0xd824848948d69906; nums[57981] = 0x0e3585b848000001;
    nums[57982] = 0x848948106aa070f4; nums[57983] = 0x16b848000001e024; nums[57984] = 0x481e376c0819a4c1;
    nums[57985] = 0x48000001e8248489; nums[57986] = 0xb0bcb52748774cb8; nums[57987] = 0x0001f02484894834;
    nums[57988] = 0x4a391c0cb3b84800; nums[57989] = 0xf8248489484ed8aa; nums[57990] = 0x9cca4fb848000001;
    nums[57991] = 0x848948682e6ff35b; nums[57992] = 0xeeb8480000020024; nums[57993] = 0x4878a5636f748f82;
    nums[57994] = 0x4800000208248489; nums[57995] = 0xc7020884c87814b8; nums[57996] = 0x000210248489488c;
    nums[57997] = 0xeb90befffab84800; nums[57998] = 0x1824848948a4506c; nums[57999] = 0xf9a3f7b848000002;
    nums[58000] = 0x848948c67178f2be; nums[58001] = 0x0cb60f0000022024; nums[58002] = 0xe1c12824448d4816;
    nums[58003] = 0x164cb60fc8894118; nums[58004] = 0x44c1094410e1c101; nums[58005] = 0xc10944031644b60f;
    nums[58006] = 0xc141021644b60f44; nums[58007] = 0x144c89c1094408e0; nums[58008] = 0xfa834804c2834828;
    nums[58009] = 0xe824848d4cc27540; nums[58010] = 0x708b38488b000000; nums[58011] = 0xfc700304c0834824;
    nums[58012] = 0xc98941ca8941108b; nums[58013] = 0x410dc2c1410ae9c1; nums[58014] = 0x3144d131450fc1c1;
    nums[58015] = 0xd689f101d18941c9; nums[58016] = 0xc107cec10ec1c141; nums[58017] = 0x01f231ce314403ea;
    nums[58018] = 0x75c0394c3c5089ca; nums[58019] = 0x506f8b4458478bba; nums[58020] = 0x8954678b44c93145;
    nums[58021] = 0x89445c478b082444; nums[58022] = 0xe089450824748be9; nums[58023] = 0x4460478b0c244489;
    nums[58024] = 0x102444890c24748b; nums[58025] = 0x8b1424448964478b; nums[58026] = 0x448914246c8b6847;
    nums[58027] = 0x245c8b6c478b1824; nums[58028] = 0xc289411c24448918; nums[58029] = 0x0c948b421024448b;
    nums[58030] = 0x0c54034200000128; nums[58031] = 0x0bcfc141c7894128; nums[58032] = 0x89d3894104c18349;
    nums[58033] = 0x41fa314406cac1c2; nums[58034] = 0x314407c7c141c789; nums[58035] = 0x41da0144c78941fa;
    nums[58036] = 0xdf2141eb8941d7f7; nums[58037] = 0x8941fb3145c32141; nums[58038] = 0xc141f289d30141cf;
    nums[58039] = 0xf38941da01450dcf; nums[58040] = 0x2141c33145c22144; nums[58041] = 0xcac1ca89d33141cb;
    nums[58042] = 0xc2c1ca89d7314102; nums[58043] = 0x163c8d47fa31440a; nums[58044] = 0x0145d30141f68941;
    nums[58045] = 0x00000100f98149d3; nums[58046] = 0x44eb891574da8941; nums[58047] = 0x44c88941c589c689;
    nums[58048] = 0xff62e9d98944f889; nums[58049] = 0x034414244403ffff; nums[58050] = 0x7403e10144082444;
    nums[58051] = 0x4710247c03440c24; nums[58052] = 0x0318246c032b148d; nums[58053] = 0x89505789441c245c;
    nums[58054] = 0x478944644789544f; nums[58055] = 0x00022824848b4858; nums[58056] = 0x0028250433486400;
    nums[58057] = 0x7f89445c77890000; nums[58058] = 0x746c5f89686f8960; nums[58059] = 0x8148fffffa2de805;
    nums[58060] = 0x415d5b00000238c4; nums[58061] = 0xc35f415e415d415c; nums[58062] = 0x48000000004047c7;
    nums[58063] = 0xc7000000004847c7; nums[58064] = 0x47c76a09e6675047; nums[58065] = 0x5847c7bb67ae8554;
    nums[58066] = 0x3a5c47c73c6ef372; nums[58067] = 0x527f6047c7a54ff5; nums[58068] = 0x05688c6447c7510e;
    nums[58069] = 0x1f83d9ab6847c79b; nums[58070] = 0xc35be0cd196c47c7; nums[58071] = 0x55f5894954415541;
    nums[58072] = 0xfb894851d4894953; nums[58073] = 0x73e1394ce989ed31; nums[58074] = 0x0d4c8a4140538b36;
    nums[58075] = 0xff130c88d0894800; nums[58076] = 0x7540438940f883c0; nums[58077] = 0xe8df8948de89481a;
    nums[58078] = 0x48438148fffffb33; nums[58079] = 0x004043c700000200; nums[58080] = 0x58c3ebc5ff000000;
    nums[58081] = 0x55c35d415c415d5b; nums[58082] = 0x40578b52f5894853; nums[58083] = 0x04c637fa83fb8948;
    nums[58084] = 0x830f7701428d8017; nums[58085] = 0xc0ffc289307438f8; nums[58086] = 0xf883f1eb001304c6;
    nums[58087] = 0xc6c0ffc2890a773f; nums[58088] = 0xdf8948f1eb001304; nums[58089] = 0xfffffad7e8de8948;
    nums[58090] = 0x48c0310000000eb9; nums[58091] = 0x4840438babf3df89; nums[58092] = 0x03e0c1df8948de89;
    nums[58093] = 0x48c2894848430348; nums[58094] = 0xc1483f4388484389; nums[58095] = 0xc289483e538808ea;
    nums[58096] = 0x483d538810eac148; nums[58097] = 0x538818eac148c289; nums[58098] = 0x20eac148c289483c;
    nums[58099] = 0xc148c289483b5388; nums[58100] = 0xc289483a538828ea; nums[58101] = 0x30eac14838e8c148;
    nums[58102] = 0x6ce8395388384388; nums[58103] = 0x18b9ee8948fffffa; nums[58104] = 0xff4850438b000000;
    nums[58105] = 0x438bff4688e8d3c6; nums[58106] = 0x438b034688e8d354; nums[58107] = 0x438b074688e8d358;
    nums[58108] = 0x438b0b4688e8d35c; nums[58109] = 0x438b0f4688e8d360; nums[58110] = 0x438b134688e8d364;
    nums[58111] = 0x438b174688e8d368; nums[58112] = 0x468808e983e8d36c; nums[58113] = 0x5b58b575f8f9831b;
    nums[58114] = 0xc98348555441c35d; nums[58115] = 0xec8148fc894953ff; nums[58116] = 0x048b4864000000a0;
    nums[58117] = 0x8489480000002825; nums[58118] = 0x48c0310000009824; nums[58119] = 0x8948aef208246c8d;
    nums[58120] = 0xff598d48d1f748ef; nums[58121] = 0xd36348fffffe23e8; nums[58122] = 0x5de8ef8948e6894c;
    nums[58123] = 0x7824748d48fffffe; nums[58124] = 0xfffffea7e8ef8948; nums[58125] = 0x00000098249c8b48;
    nums[58126] = 0x000028251c334864; nums[58127] = 0x05747824448b4800; nums[58128] = 0xc48148fffff806e8;
    nums[58129] = 0x5c415d5b000000a0; nums[58130] = 0x53fc8949555441c3; nums[58131] = 0x0000a0ec8148f589;
    nums[58132] = 0x486408245c8d4800; nums[58133] = 0x480000002825048b; nums[58134] = 0x3100000098248489;
    nums[58135] = 0xfffdafe8df8948c0; nums[58136] = 0x48e6894cd56348ff; nums[58137] = 0x48fffffde9e8df89;
    nums[58138] = 0xe8df89487824748d; nums[58139] = 0x248c8b48fffffe33; nums[58140] = 0x0c33486400000098;
    nums[58141] = 0x448b480000002825; nums[58142] = 0xfff792e805747824; nums[58143] = 0x000000a0c48148ff;
    nums[58144] = 0x000000c35c415d5b;
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
    t->get = dict_virt_addr + 0x71105;
    t->key_at = dict_virt_addr + 0x711bb;
    t->size = dict_virt_addr + 0x711e7;
    t->validate = dict_virt_addr + 0x711f8;
    
    dict_virt_addr += BUFF_STEP;
    return 0;
}
