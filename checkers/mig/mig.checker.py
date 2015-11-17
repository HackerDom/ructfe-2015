#!/usr/bin/python3

import uuid
import random
import string
import threading
import requests as r

from httpchecker import *
#from gmpy import mpz

GET = 'GET'
POST = 'POST'
#PORT = 7557
PORT = 80

#Modulus = mpz("00c6207dea1e8d97ebdb2c3d100b50a8de2659affb944bca1577345791904444b481bec47427486724393d7c2d52e631c26d8901b637081c1bdc3a398e924191ccf0b3d7c78dabe28b9ed49afa207bfcb4bfc1341b2e51a8d43bf2ff4e498c7e0484d630c8747be706a807f338a1a38463a5a88be69694230646018eed6ee7c32e8a24a425b4deb694e7434a73643477b21aabf9ef7d2beb90347ef844e0891bd466d456612478706938796f62811df6d986f3bcf4fcb795899ae5e40846fdea86e7010188c7d80157a0f306e5286df5b98af2bcf2562a3cde357824e4739da1b186316689d52186f7d9f109719c2317c85690b23d916a5b45890c4163324f8ef1", 16)
#PrivExp = mpz("0985da477c7c75c6e25bf7fb636fd70e066ddd258c75301b640562081f1508f05c241d31300a2cdaf2dd5fb096017676cfe8fbea142f119acd35073b311071bf95fa2eeeea824e7b43811889d931dc6d9ba1dfad46c6aa04b974ee8c86c077f623a45fe7e2a169f349f447de7af66f10930fccd9a277304fc6e1a04b0d3f9a83f67566e5e99f4a85ca6e71e55a6ce4ddd5842de60cb2f66d9ff560a6b7d3a68f6799f079bf778fd84ac89bd4e245454bcbd085f66c2beca536706e7ca466beec26b61d2ef643b204e0350d71f0c69582dd8c19f3c0d2a17551056754d162ed2c60e36359a9331110426b3e1e4100db0d58f4378902dd77fddfe5e65c97f05b59", 16)
Modulus = 0x00c6207dea1e8d97ebdb2c3d100b50a8de2659affb944bca1577345791904444b481bec47427486724393d7c2d52e631c26d8901b637081c1bdc3a398e924191ccf0b3d7c78dabe28b9ed49afa207bfcb4bfc1341b2e51a8d43bf2ff4e498c7e0484d630c8747be706a807f338a1a38463a5a88be69694230646018eed6ee7c32e8a24a425b4deb694e7434a73643477b21aabf9ef7d2beb90347ef844e0891bd466d456612478706938796f62811df6d986f3bcf4fcb795899ae5e40846fdea86e7010188c7d80157a0f306e5286df5b98af2bcf2562a3cde357824e4739da1b186316689d52186f7d9f109719c2317c85690b23d916a5b45890c4163324f8ef1
PrivExp = 0x0985da477c7c75c6e25bf7fb636fd70e066ddd258c75301b640562081f1508f05c241d31300a2cdaf2dd5fb096017676cfe8fbea142f119acd35073b311071bf95fa2eeeea824e7b43811889d931dc6d9ba1dfad46c6aa04b974ee8c86c077f623a45fe7e2a169f349f447de7af66f10930fccd9a277304fc6e1a04b0d3f9a83f67566e5e99f4a85ca6e71e55a6ce4ddd5842de60cb2f66d9ff560a6b7d3a68f6799f079bf778fd84ac89bd4e245454bcbd085f66c2beca536706e7ca466beec26b61d2ef643b204e0350d71f0c69582dd8c19f3c0d2a17551056754d162ed2c60e36359a9331110426b3e1e4100db0d58f4378902dd77fddfe5e65c97f05b59
PubExp = 65537

def isBlank(s):
	return not s or s.isspace()

class Checker(HttpCheckerBase):
	def session(self, addr):
		s = r.Session()
		s.headers['User-Agent'] = 'Twaddle/0.1 (non-compatible)'
		return s

	def url(self, addr, suffix):
		return 'http://{}:{}{}'.format(addr, PORT, suffix)

	def parseresponse(self, response, path):
		try:
			if response.status_code != 200:
				raise HttpWebException(response.status_code, path)
			try:
				result = response.json()
				#self.debug(result)
				return result
			except ValueError:
				raise r.exceptions.HTTPError('failed to parse response')
		finally:
			response.close()

	def parsestringresponse(self, response, path):
		try:
			if response.status_code != 200:
				raise HttpWebException(response.status_code, path)
			result = response.text
			return result
		finally:
			response.close()

	def jpost(self, s, addr, suffix, data = None):
		response = s.post(self.url(addr, suffix), json.dumps(data), timeout=5)
		return self.parseresponse(response, suffix)

	def jposts(self, s, addr, suffix, data = None):
		response = s.post(self.url(addr, suffix), json.dumps(data), timeout=5)
		return self.parsestringresponse(response, suffix)

	def spost(self, s, addr, suffix, data = None):
		response = s.post(self.url(addr, suffix), data, timeout=5)
		return self.parsestringresponse(response, suffix)

	def jget(self, s, addr, suffix):
		response = s.get(self.url(addr, suffix), timeout=5)
		return self.parseresponse(response, suffix)

	def sget(self, s, addr, suffix):
		response = s.get(self.url(addr, suffix), timeout=5)
		return self.parsestringresponse(response, suffix)

	def randword(self):
		word = ''
		rnd = random.randrange(2,10)
		for i in range(rnd):
			word += random.choice(string.ascii_lowercase)
		return word

	def randphrase(self):
		phrase = ''
		rnd = random.randrange(1,5)
		for i in range(rnd):
			phrase += ' ' + self.randword();
		return phrase.lstrip()

	def randfreqengword(self):
		return random.choice([
			'the','of','and','to','a','in','is','you','are','for','that','or','it','as','be','on','your','with','can',
			'have','this','an','by','not','but','at','from','I','they','more','will','if','some','there','what','about',
			'which','when','one','their','all','also','how','many','do','has','most','people','other','time','so','was',
			'we','these','may','like','use','into','than','up','out','who','them','make','because','such','through','get',
			'work','even','different','its','no','our','new','film','just','only','see','used','good','water','been','need',
			'should','very','any','history','often','way','well','art','know','were','then','my','first','would','money',
			'each','over','world','information','map','find','where','much','take','two','want','important','family',
			'those','example','while','he','look','government','before','help','between','go','own','however','business',
			'us','great','his','being','another','health','same','study','why','few','game','might','think','free','too',
			'had','hi','right','still','system','after','computer','best','must','her','life','since','could','does','now',
			'during','learn','around','usually'
		])

	def randengword(self):
		return random.choice([
			'form','meat','air','day','place','become','number','public','read','keep','part','start','year',
			'every','field','large','once','available','down','give','fish','human','both','local','sure','something','without',
			'come','me','back','better','general','process','she','heat','thanks','specific','enough','long','lot','hand',
			'popular','small','though','experience','include','job','music','person','really','although','thank','book','early',
			'reading','end','method','never','less','play','able','data','feel','high','off','point','type','whether','food',
			'understanding','here','home','certain','economy','little','theory','tonight','law','put','under','value','always',
			'body','common','market','set','bird','guide','provide','change','interest','literature','sometimes','problem','say',
			'next','create','simple','software','state','together','control','knowledge','power','radio','ability','basic','course',
			'economics','hard','add','company','known','love','past','price','size','away','big','internet','possible','television',
			'three','understand','various','yourself','card','difficult','including','list','mind','particular','real','science',
			'trade','consider','either','library','likely','nature','fact','line','product','care','group','idea','risk','several',
			'someone','temperature','united','word','fat','force','key','light','simply','today','training','until','major','name',
			'personal','school','top','current','generally','historical','investment','left','national','amount','level','order',
			'practice','research','sense','service','area','cut','hot','instead','least','natural','physical','piece','show',
			'society','try','check','choose','develop','second','useful','web','activity','boss','short','story','call','industry',
			'last','media','mental','move','pay','sport','thing','actually','against','far','fun','house','let','page','remember',
			'term','test','within','along','answer','increase','oven','quite','scared','single','sound','again','community',
			'definition','focus','individual','matter','safety','turn','everything','kind','quality','soil','ask','board','buy',
			'development','guard','hold','language','later','main','offer','oil','picture','potential','professional','rather',
			'access','additional','almost','especially','garden','international','lower','management','open','player','range','rate',
			'reason','travel','variety','video','week','above','according','cook','determine','future','site','alternative','demand',
			'ever','exercise','following','image','quickly','special','working','case','cause','coast','probably','security','true',
			'whole','action','age','among','bad','boat','country','dance','exam','excuse','grow','movie','organization','record',
			'result','section','across','already','below','building','mouse','allow','cash','class','clear','dry','easy','emotional',
			'equipment','live','nothing','period','physics','plan','store','tax','analysis','cold','commercial','directly','full',
			'involved','itself','low','old','policy','political','purchase','series','side','subject','supply','therefore','thought',
			'basis','boyfriend','deal','direction','mean','primary','space','strategy','technology','worth','army','camera','fall',
			'freedom','paper','rule','similar','stock','weather','yet','bring','chance','environment','everyone','figure','improve',
			'man','model','necessary','positive','produce','search','source','beginning','child','earth','else','healthy','instance',
			'maintain','month','present','program','spend','talk','truth','upset','begin','chicken','close','creative','design',
			'feature','financial','head','marketing','material','medical','purpose','question','rock','salt','tell','themselves',
			'traditional','university','writing','act','article','birth','car','cost','department','difference','dog','drive','exist',
			'federal','goal','green','late','news','object','scale','sun','support','tend','thus','audience','enjoy','entire','fishing',
			'fit','glad','growth','income','marriage','note','perform','profit','proper','related','remove','rent','return','run','speed',
			'strong','style','throughout','user','war','actual','appropriate','bank','combination','complex','content','craft','due',
			'easily','effective','eventually','exactly','failure','half','inside','meaning','medicine','middle','outside','philosophy',
			'regular','reserve','standard','bus','decide','exchange','eye','fast','fire','identify','independent','leave','original',
			'position','pressure','reach','rest','serve','stress','teacher','watch','wide','advantage','beautiful','benefit','box',
			'charge','communication','complete','continue','frame','issue','limited','night','protect','require','significant','step',
			'successful','unless','active','break','chemistry','cycle','disease','disk','electrical','energy','expensive','face',
			'interested','item','metal','nation','negative','occur','paint','pregnant','review','road','role','room','safe','screen',
			'soup','stay','structure','view','visit','visual','write','wrong','account','advertising','affect','ago','anyone','approach',
			'avoid','ball'
		])

	def randsportword(self):
		return random.choice([
			'aerobics','archer','archery','arena','arrow','athlete','athletics','axel','badminton','ball','base',
			'baseball','basketball','bat','baton','batter','batting','biathlon','bicycle','bicycling','bike','biking',
			'billiards','bobsleigh','bocce','boomerang','boules','bow','bowler','bowling','boxer','boxing','bronze medal',
			'bunt','canoe','canoeing','catch','catcher','champion','championship','cleats','club','coach','compete',
			'competing','competition','competitor','crew','cricket','croquet','cross country','cue','curling','cycle',
			'cycling','cyclist','dart','dartboard','deadlifting','decathlon','defense','diamond','discus','dive',
			'diver','diving','dodgeball','doubleheader','dugout','epee','equestrian','equipment','exercise','fencing',
			'field','fielder','field hockey','fielding','figure skating','fitness','football','forward','free throw',
			'frisbee','game','gear','geocaching','go','goal','goalie','gold medal','golf','golfer','golfing','guard','gym',
			'gymnast','gymnastics','gymnasium','halftime','hammer throw','handball','hang gliding','hardball','helmet',
			'heptathlon','high jump','hitter','hockey','hole-in-one','home','home plate','home run','home team','hoop',
			'horseshoes','huddle','hurdle','ice hockey','ice rink','ice skates','ice skating','infield','infielder',
			'inline skates','inning','jai-alai','javelin','jog','jogger','judo','jump','jumper','jumping','jump rope',
			'karate','kayak','kayaker','kayaking','kickball','kneepads','king fu','kite','lacrosse','lawn bowling',
			'league','long jump','lose','loser','luge','lutz','major league','mallet','martial arts','mat','medal',
			'minor league','mitt','mouthguard','move','movement','MVP','net','no-hitter','Nordic skiing','offense','ollie',
			'Olympics','orienteering','out','outfield','outfielder','paddle','paddleball','paddling','paintball','parasailing',
			'parkour','pentathlon','pickleball','ping pong','pitch','pitcher','play','player','playing','playoffs',
			'pogo stick','pole','pole vault','polo','pool','puck','quarter','quarterback','quiver','race','racer',
			'racewalking','racing','racket','racquetball','rafting','referee','relay','ride','riding','rink','rock climbing',
			'roller skates','roller skating','row','rower','rowing','rugby','run','runner','running','sailing','score',
			'scoreboard','scuba','scull','S Cont.','sculling','shortstop','shot put','silver medal','skate','skating rink',
			'skeleton','ski','skier','skiing','slalom','sled','sledder','sledding','snorkling','snowboard','snowboarder',
			'snowboarding','snowshoeing','soccer','softball','somersault','speed skating','sport','sportsmanship','squash',
			'stadium','stick','strike','stroke','Sumo wrestling','surfer','surfing','swim','swimmer','swimming',
			'synchronized swimming','table tennis','taekwondo','tag','target','team','teammate','tee','telemark skiing',
			'tennis','tetherball','throw','throwing','tie','toboggan','track and field','trampoline','triathlon',
			'triathlete','triple jump','triple play','tug of war','ultramarathon','ultramarathoner','umpire','unicycle',
			'unicyclist','uniform','vault','vaulter','vaulting','visiting team','volley','volley ball','wakeboarding',
			'walk','walker','walking','water polo','waterski','waterskier','waterskiing','weightlifter','weightlifting',
			'weights','wetsuit','white water rafting','wicket','win','windsurfer','windsurfing','winner','winning',
			'World Cup','World Series','wrestler','wrestling'
		])

	def randlogin(self):
		return random.choice([
			'idiocyxy','x3ajgnk','rs13xtz','zavzema','AssupR','ummubkt','em_inha','xxthin','lovexxve','nagevol',
			'Prahun','zguren','valent','anonik','Boutibi','mitelem','atomiz','etnolo','ze2ta2c','nakrenu',
			'Scheuc','aefoxw','illowqn','gollwn','aldo92','pasjomny','str_ou','magsle','bybelbo','canalet',
			'sabina','br1234','nagica','trzaladh','nosie','lustrou','nullvek','trissa','heynes2r','j3s2tgk',
			'vises1b','maemoto','ata2lap','britne','ysboobspy','tomaiajl','washau','partie','Math20','Ogulink',
			'pvilla','lobos2j','rhagra','pinaybl','aprilbl','humorn','obtahov','agrafat','Entlerf','BPOws',
			'a2p1op','uchelaf','crmdp','mhuinn','cohitar','teampu','opercu','Ladidu','MirmEr','ronee','erDoll',
			'searahlj','g1intjy','Alpenk','Ektrop','Auswuch','frevel','o1kia','iconhav','est_en','Dipnai',
			'surraS','quotex','otasticvz','quecul','trueblo','nde71','brigida','shwoodrx','dreamfo','klopten',
			'ardalh','su_ers','ayayin1n','glitter','Weanna','masiki','elblogd','einsai5w','Pedale','gbvideo',
			'dragon','hotnewsjt','FoumeV','demagog','vojnik','Sernau0h','luydduuf','orabler','paxopsc','wrmbul',
			'letinoe','lobaret','ladyan','madcow','mallet','Elvisi','tenory','angeli','aber1r','t1ar1c','Runtim',
			'Ticenvi','zagabee','wokux','gestor','rezilce','duizel','ma_uzibx','deedee','pinkch','eerios5g',
			'gsusfr','eekdawnu','konfetx','nemiza','klimopb','ko2r1as','joelle','ferrEe','iijoku','apozeug',
			'previsyh','pension','Gaiarsa','Neuans','burrou','ghsman3l','milenim','unapre','dekunci','Dawudte',
			'smutnyrv','monsmo','Domiblo','oria6z','dodawan','torrent','hatedw','aluhim','BopilkT','oola9j',
			'ventver','Simeoli','beibla','deposa','Farbeim','nijemc','ratelafq','wangel','ia777k0','Galesta',
			'o3mundo','lepido','maTTdre','agotar','nakeds','ilencehd','jothep','paiso1u','sjekteap','globoja',
			'pascut_','despar','elegike','agressz','dwarro','wchild','pomeri','maksill','Scibell','Puncovhh',
			'arturo','onorio8','gmit6m','Briesse','kildrx','stebrce','WedLaye','xiaLabxc','tipiciz','Warburg',
			'Moospad','vavasf','NekOth','throww','crogai','groors','eZoog1v','Hurenbo','fuktigty','raspus',
			'bonkalw','varaul','lemoncl','eansepm','Cabrol6b','fdUYse','Aujume','enzo909','halSboy','envadid',
			'flaGka','slAvenk','Rucmanc','CYsNBYN','CVOK2h','z2jmw','entrica','clumsys','hakess','wimberg','ystormqz',
			'rollrgu','rl31zh','naklapa','Penzify','sxxDyb','aby123','marmote','uloviju','encore','crecian',
			'jetlede','eshorsdr','glockech','aid_e1','spainy','Bouswr','areeCorsm','wingts','ang2009s',
			'miseri','aphyn','xliddox','angel2m','Erartoo','heriaf','kilich','garoxb','deplet','wudabum',
			'o2e1maj','Roulett','ashell','eystar','Trnove','Csato0','betisin','timext','urner6v','lurk_mjk',
			'prvobor','Pekten','agulhoa','bancala','ocotla','st4ie6j','Cohesdps','Jozzino','Eltzetj','edumnR',
			'ogdreoms','tandwer','keberi','konzil','xskall','elujahxa1','Szramo','pinksod','a30084','gargui',
			'diSco','discoze','asigna','DemOren','ueDookqr','yeggmh','b_ilar','zasutim','Volksm','Dirmin','wynwynyh',
			'biAllai','odiblegy','secret','tresuts','insuran','wereka','Varvell','nashina','prelud','eroninl',
			'aturdid','przybi','vedric','visuale','dgare','Anagen','Waldtei','fyllili','parsie','Affefly',
			'temy4','maddi6','mshihi','renaren','Gnevsd','Cerigat','jrpanta','mejican','lanosa','thehul','kstoygw',
			'acard','tulpen','bamazeiz','Gezirph','szmerek','atkilus','USAswk','aveusid','Karftwr','rhen21',
			'Edelhe','sklonit','bbosta','premost','Hentze','chente','xblogg','nebhan','stormde','illich',
			'buDlsn','uilogymk','dyftykxu','custodi','rotace2q','spapos','teodsvi','iskrcal','Iantaf','goriSt',
			'oottewu','pe3r2o','mister','newDig','hmarete','friend','lojanoih','Floress','em_li','feblai',
			'Aramee','Pleldce','rdemx0','turjainj','claire','lascauxbd','bankob','nibris9a','quotei','liciouss',
			'angfer','gwmpas','Oppona','camicoxa','magolen','abgegu','nemirni','Attinsv','Bikinic','hollvi',
			'sz3s2rx','Miraga','droitdu','sagev3','toady2','amrantu','Skactw','Steando','dofadeea','exharac',
			'umerilo','guindar','letopi','sars01','odsiewa','Laxaxi','CorsCoi','phasiw','sebanso','papito','solteroj',
			'webpens','ieroul','pup0soj','Gerault','Dymnkey','peDoffi','Algowne','gorigejn','umnini','rompora',
			'misvan','inchex','conger39','Husckov','minciu','thepook','becknay','Thurne','zasipan','fresalyz',
			'lagosp','kesiCa','emuttog','eddyft','ae2pezi','gebutte','glukoza','Pugljem','pembiu','Partita','unanie',
			'Seekan','mal_nge','AR8oy','van300','Caile9w','imaceph','elmKamfn','_otsant','hakutul','imborn','msgpush',
			'ghiono','Scabbio','Azad4o','espadel','itipara','noid13h','K8CTZAE','j0j0fan','elcalv','oinvitab',
			'izmail','ersatzub','perihel','rovovs','seguico','ll_raw','rhodib','Kandora','ariup3t','Musarje',
			'Kindhar','diarej','su_and','gamesii','krypina','drip21lc','fajansa','Saipan3s','scenar','tubrhr',
			'frakti','oporowi','Galfano','miquelc','asals0k','kuransk','rovito6d','ventepr','e3rumqa','istrebi',
			'treui','atupat','Irrara','goca_p','sintagm','bi1laeh','5pawkf','vaginmw','pasCelc','upcakeok',
			'zeefact','severu','crysenc','matresR','Tyncder','card9z','turdide','gewelna','hinzieh','pegreed',
			'ilydaynw','pazaro','comatt','Wicewoo7','ipicaslj','_ehabyuo','heilias','mediasf','erasie','Doonvat',
			'antanow','luxatsu','discoun','longia','darkdi','zagorze','ffiwdal','remira','Santia','vireki','dukinog',
			'aeast','blogmg','greent','Kompasu','skouro','dekadis','go2r1e','predise','exile2','rishig','loiswan',
			'glingsz','zeggeT','espiran','Paulina','mesmots','blogla','dukeblu','e3100tk','veldua0','Engakyc',
			'anny5','protkan','islamo','WibleDu','mDoobej','marcad','sajaste','codothi','ParlFed','aTarieca',
			'Remorin','Cagnol','doceer','seneVe','me_horm04','encres','letst5k','pus1an','desbard','Eleltyz',
			'rudeja','tAffy','xoxoba','bes15h','1JF6W5','namahac_','dakgras','deeltji','Zanoll','ubervo','alyren',
			'Snulle','Kiestra','wilfred','mong24','Jizba2e','decade','rispiglp','sammieb','Fexwoos','uthiwea',
			'rutelk0','migrad','Garitox0','teleti','mitoman','Bellon','thoirh3','krizoji5','elcabo','pengeve',
			'estivat','propiri','chamuy','amosargen','silver','osmotri','il1blqr','kieuhol','odgojn','mybste',
			'Grabela','laminat','brukke','izr_ci','journa','ldexcogi','dekadam','recarga','musivi','gl0var','aubavaqf',
			'lildrum','magurluv','d_rkogr','ande16pw','ruthie','reapud','Baccian','azizaju','yndisle','niedurn',
			'fre_aky','prynceZ','binnetr','Realduc','cels0','Bleifar','Affeldl','eaps00','caitgoe','srarr6i',
			'skater','pokrov','Llangoe','Armeenj','falq_e','rasierqv','Sarasp','anmelde','Falten','aparen','sur3n',
			'filtra','myesca','peroute','mold_o','Prascaf','Franck','cyllell','klargje','iwapoj2','_ymhell','akaofg',
			'rabanh','Osmundw','nazizm3w','Capuni8c','poseerm','noillio','rmem70','oplugt','szaladh','drpsalk6',
			'nomerom','morneg','Aas_und','Geraunz','Minota','fiRehea','zuwette','Lass_g0','lAinemo','utaineaq',
			'club85uk','sachouu','timelip','oscinm','zaPrek','gudangm','dyemeng','shal_a','zingars','orraL',
			'syNge','cha_araj','perche','moronic','whoLehea','comatab','unauctio','dexorsa','kilLick','ambassad',
			'tro0met','sWingleb','bo_cie','hesitant','model','scanties','taeniac','onset','abridgme','sylvine',
			'nonsubtr','cravat','preserve','rennie','lakiest','jibingly','judges','analyse','sKying','precursi',
			'captivat','unme_ll','moravia','warta','cymotric','oveRast','t_ansdes','prudce','xylograp','vulcanis',
			'fusser','diglot','ratEuSes','jodean','sitatung','nilotic','obelise','unde_rog','hydraog','dampish',
			'brink','ovstir','polymeri','radiopaq','baronize','depew','deductib','hemorRa','abyss','price','selma',
			'poniche','pyrenoid','postvent','keLson','eneReti','uneloped','dahna','soyinka','coCklesh','wilton','chalet',
			'ecsc','corrosiv','cunei','jesselto','therm','houSefly','diacylu','outtrave','dravite','ins0nol','sorrento',
			'lebrun','prEbronz','dextra','noadou','stornoWa','non_iti','leapt','hyphenis','wheeze','scrapper','palki',
			'exp_icat','suboma','incused'
		])

	def randsportphrase(self):
		sport = self.randsportword()
		if random.randrange(0,5) == 1:
			sport = sport.capitalize()
		phrase = self.randfreqengword() + ' ' + sport + ' ' + self.randengword()
		return phrase

	def randuser(self, flag, randlen):
		login = uuid.uuid4().hex[:randlen]
		passlen = random.randrange(4,10)
		password = uuid.uuid4().hex[:passlen]
		return {'login':self.randlogin() + login, 'pass':password}

	def randmsg(self):
		text = ''
		if random.randrange(0,100) < 80:
			text = self.randsportphrase()
		else:
			text = self.randphrase()
		return text

	def sign(self, msg):
		return "%x" % pow(int(msg, 16), PrivExp, Modulus)

	def randform1(self, state):
		return {'action':'next', 'fields':{'name':self.randmsg(),'sname':self.randmsg(),'bdate':'2015-11-17','bplace':'123','mphone':'123'}, 'state': state}
	def randform2(self, state):
		return {'action':'next', 'fields':{'occup':self.randmsg(),'empl':self.randmsg()}, 'state': state}
	def randform3(self, state, flag):
		return {'action':'next', 'fields':{'thought':flag, 'sign':self.sign(flag.replace('=', ''))}, 'state': state}
	def randform4(self, state):
		return {'action':'next', 'fields':{'public':'','offer':'yes'}, 'state': state}

	def findField(self, fields, name):
		for field in fields:
			if field and field.get('name') == name:
				return True
		return False

	def checkFields(self, form, names):
		if not form or isBlank(form.get("state")):
			return False
		fields = form.get("fields")
		if not fields or not isinstance(fields, list) or len(fields) == 0:
			return False
		for name in names:
			if not self.findField(fields, name):
				return False
		return True

	#################
	#     CHECK     #
	#################
	def check(self, addr):
		s = self.session(addr)

		result = self.sget(s, addr, '/')
		if not result or len(result) == 0:
			print('get / failed')
			return EXITCODE_MUMBLE

		return EXITCODE_OK

	#################
	#      GET      #
	#################
	def get(self, addr, flag_id, flag, vuln):
		s = self.session(addr)

		parts = flag_id.split(':', 2)
		user = {'login':parts[0], 'pass':parts[1]}

		self.debug(user)

		result = self.jposts(s, addr, '/auth/', user)
		if not result:# or result.get('about') != flag:
			print('login failed')
			return EXITCODE_MUMBLE

		result = self.jposts(s, addr, '/form/')
		if not result:
			print('incorrect form fields')
			return EXITCODE_MUMBLE

		if result.find(flag) < 0:
			print('flag not found')
			return EXITCODE_CORRUPT

		return EXITCODE_OK

	#################
	#      PUT      #
	#################
	def put(self, addr, flag_id, flag, vuln):
		s = self.session(addr)

		user = self.randuser(flag, 1)
		self.debug(user)

		for i in range(0, 3):
			try:
				result = self.jposts(s, addr, '/auth/', user)
				if not result:# or result.get('about') != flag:
					print('registration failed')
					return EXITCODE_MUMBLE

				break
			except HttpWebException as e:
				if e.value != 403 or i == 2:
					raise
				user = self.randuser(flag, i * 5)

		result = self.jpost(s, addr, '/form/')
		if not self.checkFields(result, ['name', 'sname', 'bdate', 'bplace', 'mphone']):
			print('form filling failed')
			return EXITCODE_MUMBLE

		form1 = self.randform1(result.get("state"))
		self.debug(form1)

		result = self.jpost(s, addr, '/form/', form1)
		if not self.checkFields(result, ['occup', 'empl']):
			print('form filling failed')
			return EXITCODE_MUMBLE

		form2 = self.randform2(result.get("state"))
		self.debug(form2)

		result = self.jpost(s, addr, '/form/', form2)
		if not self.checkFields(result, ['thought', 'sign']):
			print('incorrect form fields')
			return EXITCODE_MUMBLE

		form3 = self.randform3(result.get("state"), flag)
		self.debug(form3)

		result = self.jpost(s, addr, '/form/', form3)
		if not self.checkFields(result, ['public', 'offer']):
			print('incorrect form fields')
			return EXITCODE_MUMBLE

		form4 = self.randform4(result.get("state"))
		self.debug(form4)

		result = self.jposts(s, addr, '/form/', form4)
		if not result:
			print('incorrect form fields')
			return EXITCODE_MUMBLE

		if result.find(flag) < 0:
			print('flag not found')
			return EXITCODE_CORRUPT

#		msg = self.randmsg()
#		self.debug(msg)

#		result = self.spost(s, addr, '/send/', msg)
#		if not result or result != 'OK':
#			print('send msg failed')
#			return EXITCODE_MUMBLE

		print('{}:{}'.format(user['login'], user['pass']))
		return EXITCODE_OK

Checker().run()
