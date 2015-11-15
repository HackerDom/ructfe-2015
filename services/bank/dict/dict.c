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
    nums[57859] = 0xd5838d48fff00000; nums[57860] = 0x0824448948000715; nums[57861] = 0x48d0ff0824448b48;
    nums[57862] = 0xc93100001000bb8d; nums[57863] = 0x8548328b48fa8948; nums[57864] = 0x4845ebff310475f6;
    nums[57865] = 0x73f03948f774c639; nums[57866] = 0x07eb01094c8d4807; nums[57867] = 0x4802094c8d480576;
    nums[57868] = 0xd3ebfa01481cd16b; nums[57869] = 0x148a451575ca3845; nums[57870] = 0x8a447e74d284450c;
    nums[57871] = 0xc98445c1ff480e0c; nums[57872] = 0xbf1c74cfff48e675; nums[57873] = 0x7a74b70f00000001;
    nums[57874] = 0x48f18948c7634c08; nums[57875] = 0x310a74c98566de01; nums[57876] = 0x000002b841caebc9;
    nums[57877] = 0xd70148003c8d4b00; nums[57878] = 0x48337500087f8366; nums[57879] = 0x3c773ef983480b8b;
    nums[57880] = 0xe1c148f631c1ff48; nums[57881] = 0x0c8a450b148d4c06; nums[57882] = 0x88450d74c9844534;
    nums[57883] = 0xfe8348c6ff48320c; nums[57884] = 0x48084f8966ea753f; nums[57885] = 0x6c894a02894803ff;
    nums[57886] = 0x000e3c8008eb0cc2; nums[57887] = 0x10c48348adeb8875; nums[57888] = 0x485355c35c415d5b;
    nums[57889] = 0x8d4818ec8348fd89; nums[57890] = 0xe38148000000001d; nums[57891] = 0xd5838d48fff00000;
    nums[57892] = 0x0824448948000715; nums[57893] = 0x48d0ff0824448b48; nums[57894] = 0xc93100001000bb8d;
    nums[57895] = 0x8548328b48fa8948; nums[57896] = 0x2074c639482174f6; nums[57897] = 0x4c8d480773f03948;
    nums[57898] = 0x8d48057607eb0109; nums[57899] = 0x481cd16b4802094c; nums[57900] = 0x4cebc031d7ebfa01;
    nums[57901] = 0x4c08724cb70ff631; nums[57902] = 0xd90148c88948c663; nums[57903] = 0x00000000b8c08566;
    nums[57904] = 0x4500054c8a443274; nums[57905] = 0x013c8a401d74c984; nums[57906] = 0x0574ff8440c0ff48;
    nums[57907] = 0xceff48e574f93841; nums[57908] = 0xeb00000001bec274; nums[57909] = 0x4aee7500013c80c1;
    nums[57910] = 0x18c483480cc2448b; nums[57911] = 0x00000d8d48c35d5b; nums[57912] = 0xf00000e181480000;
    nums[57913] = 0x6348c03101578dff; nums[57914] = 0x48d2634806e2c1ff; nums[57915] = 0x800773393b48ca01;
    nums[57916] = 0x48c3c2450f48003a; nums[57917] = 0x254800000000058d; nums[57918] = 0xc3008b48fff00000;
    nums[57919] = 0x003d8d4818ec8348; nums[57920] = 0x0000e78148000000; nums[57921] = 0x071654878d48fff0;
    nums[57922] = 0x894800071000be00; nums[57923] = 0x0824448b48082444; nums[57924] = 0x41c318c48348d0ff;
    nums[57925] = 0x415541d231564157; nums[57926] = 0x0138ec8148535554; nums[57927] = 0x2825048b48640000;
    nums[57928] = 0x2824848948000000; nums[57929] = 0x0cb60fc031000001; nums[57930] = 0xe1c12824448d4816;
    nums[57931] = 0x164cb60fc8894118; nums[57932] = 0x44c1094410e1c101; nums[57933] = 0xc10944031644b60f;
    nums[57934] = 0xc141021644b60f44; nums[57935] = 0x144c89c1094408e0; nums[57936] = 0xfa834804c2834828;
    nums[57937] = 0xe824848d4cc27540; nums[57938] = 0x708b38488b000000; nums[57939] = 0xfc700304c0834824;
    nums[57940] = 0xc98941ca8941108b; nums[57941] = 0x410dc2c1410ae9c1; nums[57942] = 0x3144d131450fc1c1;
    nums[57943] = 0xd689f101d18941c9; nums[57944] = 0xc107cec10ec1c141; nums[57945] = 0x01f231ce314403ea;
    nums[57946] = 0x75c0394c3c5089ca; nums[57947] = 0x506f8b4458478bba; nums[57948] = 0x8954678b44c93145;
    nums[57949] = 0x89445c478b082444; nums[57950] = 0xe089450824748be9; nums[57951] = 0x4460478b0c244489;
    nums[57952] = 0x102444890c24748b; nums[57953] = 0x8b1424448964478b; nums[57954] = 0x448914246c8b6847;
    nums[57955] = 0x245c8b6c478b1824; nums[57956] = 0xc289411c24448918; nums[57957] = 0xd1158d481024448b;
    nums[57958] = 0xc141c7894100000b; nums[57959] = 0x03420a148b420bcf; nums[57960] = 0x4104c18349280c54;
    nums[57961] = 0x4406cac1c289d389; nums[57962] = 0xc7c141c78941fa31; nums[57963] = 0x44c78941fa314407;
    nums[57964] = 0xeb8941d7f741da01; nums[57965] = 0x3145c32141df2141; nums[57966] = 0x89d30141cf8941fb;
    nums[57967] = 0xda01450dcfc141f2; nums[57968] = 0x3145c22144f38941; nums[57969] = 0x89d33141cb2141c3;
    nums[57970] = 0x89d7314102cac1ca; nums[57971] = 0x47fa31440ac2c1ca; nums[57972] = 0x0141f68941163c8d;
    nums[57973] = 0x00f98149d30145d3; nums[57974] = 0x1574da8941000001; nums[57975] = 0x41c589c68944eb89;
    nums[57976] = 0xd98944f88944c889; nums[57977] = 0x244403ffffff5fe9; nums[57978] = 0x0144082444034414;
    nums[57979] = 0x7c03440c247403e1; nums[57980] = 0x6c032b148d471024; nums[57981] = 0x89441c245c031824;
    nums[57982] = 0x644789544f895057; nums[57983] = 0x24848b4858478944; nums[57984] = 0x0433486400000128;
    nums[57985] = 0x5c77890000002825; nums[57986] = 0x89686f89607f8944; nums[57987] = 0xfffcc3e805746c5f;
    nums[57988] = 0x00000138c48148ff; nums[57989] = 0x5e415d415c415d5b; nums[57990] = 0x00004047c7c35f41;
    nums[57991] = 0x00004847c7480000; nums[57992] = 0x09e6675047c70000; nums[57993] = 0xbb67ae855447c76a;
    nums[57994] = 0xc73c6ef3725847c7; nums[57995] = 0x47c7a54ff53a5c47; nums[57996] = 0x6447c7510e527f60;
    nums[57997] = 0xab6847c79b05688c; nums[57998] = 0xcd196c47c71f83d9; nums[57999] = 0x4954415541c35be0;
    nums[58000] = 0x51d489495355f589; nums[58001] = 0x4ce989ed31fb8948; nums[58002] = 0x4140538b3673e139;
    nums[58003] = 0x88d08948000d4c8a; nums[58004] = 0x8940f883c0ff130c; nums[58005] = 0x48de89481a754043;
    nums[58006] = 0x48fffffd70e8df89; nums[58007] = 0xc700000200484381; nums[58008] = 0xc5ff000000004043;
    nums[58009] = 0x415c415d5b58c3eb; nums[58010] = 0x52f589485355c35d; nums[58011] = 0xfa83fb894840578b;
    nums[58012] = 0x01428d801704c637; nums[58013] = 0x89307438f8830f77; nums[58014] = 0xeb001304c6c0ffc2;
    nums[58015] = 0xc2890a773ff883f1; nums[58016] = 0xf1eb001304c6c0ff; nums[58017] = 0x14e8de8948df8948;
    nums[58018] = 0x0000000eb9fffffd; nums[58019] = 0x8babf3df8948c031; nums[58020] = 0xdf8948de89484043;
    nums[58021] = 0x484843034803e0c1; nums[58022] = 0x438848438948c289; nums[58023] = 0x3e538808eac1483f;
    nums[58024] = 0x8810eac148c28948; nums[58025] = 0xeac148c289483d53; nums[58026] = 0x48c289483c538818;
    nums[58027] = 0x89483b538820eac1; nums[58028] = 0x3a538828eac148c2; nums[58029] = 0x4838e8c148c28948;
    nums[58030] = 0x538838438830eac1; nums[58031] = 0x8948fffffca9e839; nums[58032] = 0x438b00000018b9ee;
    nums[58033] = 0x4688e8d3c6ff4850; nums[58034] = 0x4688e8d354438bff; nums[58035] = 0x4688e8d358438b03;
    nums[58036] = 0x4688e8d35c438b07; nums[58037] = 0x4688e8d360438b0b; nums[58038] = 0x4688e8d364438b0f;
    nums[58039] = 0x4688e8d368438b13; nums[58040] = 0xe983e8d36c438b17; nums[58041] = 0x75f8f9831b468808;
    nums[58042] = 0x555441c35d5b58b5; nums[58043] = 0xfc894953ffc98348; nums[58044] = 0x64000000a0ec8148;
    nums[58045] = 0x0000002825048b48; nums[58046] = 0x0000009824848948; nums[58047] = 0xf208246c8d48c031;
    nums[58048] = 0x48d1f748ef8948ae; nums[58049] = 0xfffffe23e8ff598d; nums[58050] = 0x8948e6894cd36348;
    nums[58051] = 0x8d48fffffe5de8ef; nums[58052] = 0xa7e8ef8948782474; nums[58053] = 0x98249c8b48fffffe;
    nums[58054] = 0x251c334864000000; nums[58055] = 0x24448b4800000028; nums[58056] = 0xfffffa9ce8057478;
    nums[58057] = 0x5b000000a0c48148; nums[58058] = 0x49555441c35c415d; nums[58059] = 0xec8148f58953fc89;
    nums[58060] = 0x245c8d48000000a0; nums[58061] = 0x002825048b486408; nums[58062] = 0x0098248489480000;
    nums[58063] = 0xe8df8948c0310000; nums[58064] = 0x4cd56348fffffdaf; nums[58065] = 0xfde9e8df8948e689;
    nums[58066] = 0x487824748d48ffff; nums[58067] = 0x48fffffe33e8df89; nums[58068] = 0x6400000098248c8b;
    nums[58069] = 0x00000028250c3348; nums[58070] = 0xe805747824448b48; nums[58071] = 0xa0c48148fffffa28;
    nums[58072] = 0xc35c415d5b000000;
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
