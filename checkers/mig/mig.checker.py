#!/usr/bin/python3

import uuid
import time
import random
import string
import threading
import requests as r
import binascii

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
		s.headers['User-Agent'] = self.randua()
		s.headers['Accept'] = '*/*'
		s.headers['Accept-Language'] = 'en-US,en;q=0.5'
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
		dump = '' if data == None else json.dumps(data)
		response = s.post(self.url(addr, suffix), dump, timeout=5)
		return self.parseresponse(response, suffix)

	def jposts(self, s, addr, suffix, data = None):
		dump = '' if data == None else json.dumps(data)
		response = s.post(self.url(addr, suffix), dump, timeout=5)
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

	def randword(self, maxlength=10):
		word = ''
		rnd = random.randrange(2, maxlength)
		for i in range(rnd):
			word += random.choice(string.ascii_lowercase)
		return word

	def randphrase(self):
		phrase = ''
		rnd = random.randrange(1,5)
		for i in range(rnd):
			phrase += ' ' + self.randword();
		return phrase.lstrip()

	def randua(self):
		return random.choice([
			'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36',
			'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36',
			'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36',
			'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
			'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
			'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',

			'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 YaBrowser/14.8.1985.11875 Safari/537.36',
			'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 YaBrowser/14.8.1985.12017 Safari/537.36',
			'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 YaBrowser/14.8.1985.12018 Safari/537.36',
			'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 YaBrowser/14.8.1985.12084 Safari/537.36',
			'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 YaBrowser/14.8.1985.12084 Safari/537.36',

			'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/33.0.1750.152 Chrome/33.0.1750.152 Safari/537.36',
			'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36',
			'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/36.0.1985.125 Chrome/36.0.1985.125 Safari/537.36',
			'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/38.0.2125.111 Chrome/38.0.2125.111 Safari/537.36',
			'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/38.0.2125.111 Chrome/38.0.2125.111 Safari/537.36',

			'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0',
			'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20130401 Firefox/31.0',
			'Mozilla/5.0 (X11; OpenBSD amd64; rv:28.0) Gecko/20100101 Firefox/28.0',
			'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0',
			'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:36.0) Gecko/20100101 Firefox/36.0',
			'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0',

			'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
			'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
			'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
			'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
			'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',

			'Opera/9.80 (Windows NT 6.1; U; es-ES) Presto/2.9.181 Version/12.00',
			'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
			'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16',
			'Opera/9.80 (Windows NT 6.1) Presto/2.12.388 Version/12.16',
			'Opera/9.80 (Windows NT 6.1; Win64; x64) Presto/2.12.388 Version/12.17'
		])

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

	def randname(self):
		return random.choice([
			'Abraham','Ada','Adelina','Adeline','Adrian','Agnes','Albert','Alberta','Alfred','Alice','Ambrose','Amelia','Amy','Ann',
			'Anna','Anne','Annie','Anthony','Arabella','Archibald','Archie','Arnold','Arthur','Audrey','Augusta','Augustus','Barnard',
			'Barney','Beatrice','Benjamin','Bernarr','Beryl','Bessie','Betsey','Betty','Blanche','Brian','Caleb','Caroline','Catherine',
			'Cecil','Cecily','Charles','Charley','Charlotte','Christopher','Clara','Clare','Constance','Cyril','Daniel','David','Denis',
			'Dewey','Doboral','Dora','Doris','Dorothy','Douglas','Ebinezer','Edgar','Edith','Edmond','Edmund','Edward','Edwin','Eileen',
			'Eleanor','Elijah','Eliza','Elizabeth','Ellen','Elsie','Emanuel','Emily','Emma','Emmeline','Ernest','Esther','Ethel','Eva',
			'Eve','Eveline','Evelyn','Fanny','Felix','Fitz','Flora','Florence','Florrie','Foster','Frances','Francis','Frank','Fred',
			'Freddy','Frederick','George','Gladys','Gordon','Grace','Gwendoline','Hannah','Harold','Harriet','Harriett','Harriot',
			'Harry','Helen','Henrietta','Henry','Herbert','Hester','Hilary','Hilda','Horace','Hubert','Humphrey','Ida','Indra','Irene',
			'Isaac','Isabella','Jack','James','Jane','Janet','Jasper','Jean','Jemima','Jesse','Jessie','Joan','Joanna','Joel','John',
			'Jonathan','Jonathon','Joseph','Joshua','Josiah','Julia','Kate','Kath','Kathleen','Kezia','Kossuth','Laura','Lavinia',
			'Lawrence','Leah','Leonard','Leslie','Lilian','Lilias','Lillian','Lillie','Lilly','Lily','Linda','Lionel','Lizzie',
			'Llewellyn','Lottie','Louisa','Louise','Lucy','Mabel','Macarthur','Maggie','Malcolm','Mansel','Margaret','Margery','Maria',
			'Marjorie','Martha','Mary','MaryAnn','Matilda','Matthew','Maud','Maude','Maurice','May','Mercy','Meshach','Mildred','Miles',
			'Millicent','Miriam','Molly','Myrtle','Nellie','Nigel','Norah','Olive','Osborn','Patricia','Patrick','Paul','Pauline','Percival',
			'Percy','Peter','Phillip','Polly','Ralph','RALPH','Ralph','Randolph','Raymond','Rebecca','Reubin','Rhoda','Richard','Rob',
			'Robert','Robinson','Roland','Ronald','Rosa','Rosalinde','Rose','Rufus','Ruth','Sam','Samuel','Sarah','Selina','Septima',
			'Shadrach','Sidney','Simon','Sophia','Stanley','Stephen','Susan','Susanna','Susannah','Sybil','Sydney','Sylvia','Theodore',
			'Thomas','Tom','Victor','Victoria','Walter','Wilfred','Willam','William','Winifred'
		])

	def randsurname(self):
		return random.choice([
			'Smith','Johnson','Williams','Jones','Brown','Davis','Miller','Wilson','Moore','Taylor','Anderson','Thomas','Jackson','White',
			'Harris','Martin','Thompson','Garcia','Martinez','Robinson','Clark','Rodriguez','Lewis','Lee','Walker','Hall','Allen','Young',
			'Hernandez','King','Wright','Lopez','Hill','Scott','Green','Adams','Baker','Gonzalez','Nelson','Carter','Mitchell','Perez','Roberts',
			'Turner','Phillips','Campbell','Parker','Evans','Edwards','Collins','Stewart','Sanchez','Morris','Rogers','Reed','Cook','Morgan','Bell',
			'Murphy','Bailey','Rivera','Cooper','Richardson','Cox','Howard','Ward','Torres','Peterson','Gray','Ramirez','James','Watson','Brooks',
			'Kelly','Sanders','Price','Bennett','Wood','Barnes','Ross','Henderson','Coleman','Jenkins','Perry','Powell','Long','Patterson','Hughes',
			'Flores','Washington','Butler','Simmons','Foster','Gonzales','Bryant','Alexander','Russell','Griffin','Diaz','Hayes','Myers','Ford',
			'Hamilton','Graham','Sullivan','Wallace','Woods','Cole','West','Jordan','Owens','Reynolds','Fisher','Ellis','Harrison','Gibson',
			'Mcdonald','Cruz','Marshall','Ortiz','Gomez','Murray','Freeman','Wells','Webb','Simpson','Stevens','Tucker','Porter','Hunter','Hicks',
			'Crawford','Henry','Boyd','Mason','Morales','Kennedy','Warren','Dixon','Ramos','Reyes','Burns','Gordon','Shaw','Holmes','Rice','Robertson',
			'Hunt','Black','Daniels','Palmer','Mills','Nichols','Grant','Knight','Ferguson','Rose','Stone','Hawkins','Dunn','Perkins','Hudson','Spencer',
			'Gardner','Stephens','Payne','Pierce','Berry','Matthews','Arnold','Wagner','Willis','Ray','Watkins','Olson','Carroll','Duncan','Snyder','Hart',
			'Cunningham','Bradley','Lane','Andrews','Ruiz','Harper','Fox','Riley','Armstrong','Carpenter','Weaver','Greene','Lawrence','Elliott','Chavez',
			'Sims','Austin','Peters','Kelley','Franklin','Lawson','Fields','Gutierrez','Ryan','Schmidt','Carr','Vasquez','Castillo','Wheeler','Chapman',
			'Oliver','Montgomery','Richards','Williamson','Johnston','Banks','Meyer','Bishop','Mccoy','Howell','Alvarez','Morrison','Hansen','Fernandez',
			'Garza','Harvey','Little','Burton','Stanley','Nguyen','George','Jacobs','Reid','Kim','Fuller','Lynch','Dean','Gilbert','Garrett','Romero',
			'Welch','Larson','Frazier','Burke','Hanson','Day','Mendoza','Moreno','Bowman','Medina','Fowler','Brewer','Hoffman','Carlson','Silva','Pearson',
			'Holland','Douglas','Fleming','Jensen','Vargas','Byrd','Davidson','Hopkins','May','Terry','Herrera','Wade','Soto','Walters','Curtis','Neal',
			'Caldwell','Lowe','Jennings','Barnett','Graves','Jimenez','Horton','Shelton','Barrett','Obrien','Castro','Sutton','Gregory','Mckinney','Lucas',
			'Miles','Craig','Rodriquez','Chambers','Holt','Lambert','Fletcher','Watts','Bates','Hale','Rhodes','Pena','Beck','Newman','Haynes','Mcdaniel',
			'Mendez','Bush','Vaughn','Parks','Dawson','Santiago','Norris','Hardy','Love','Steele','Curry','Powers','Schultz','Barker','Guzman','Page','Munoz',
			'Ball','Keller','Chandler','Weber','Leonard','Walsh','Lyons','Ramsey','Wolfe','Schneider','Mullins','Benson','Sharp','Bowen','Daniel','Barber',
			'Cummings','Hines','Baldwin','Griffith','Valdez','Hubbard','Salazar','Reeves','Warner','Stevenson','Burgess','Santos','Tate','Cross','Garner',
			'Mann','Mack','Moss','Thornton','Dennis','Mcgee','Farmer','Delgado','Aguilar','Vega','Glover','Manning','Cohen','Harmon','Rodgers','Robbins',
			'Newton','Todd','Blair','Higgins','Ingram','Reese','Cannon','Strickland','Townsend','Potter','Goodwin','Walton','Rowe','Hampton','Ortega','Patton',
			'Swanson','Joseph','Francis','Goodman','Maldonado','Yates','Becker','Erickson','Hodges','Rios','Conner','Adkins','Webster','Norman','Malone',
			'Hammond','Flowers','Cobb','Moody','Quinn','Blake','Maxwell','Pope','Floyd','Osborne','Paul','Mccarthy','Guerrero','Lindsey','Estrada','Sandoval',
			'Gibbs','Tyler','Gross','Fitzgerald','Stokes','Doyle','Sherman','Saunders','Wise','Colon','Gill','Alvarado','Greer','Padilla','Simon','Waters',
			'Nunez','Ballard','Schwartz','Mcbride','Houston','Christensen','Klein','Pratt','Briggs','Parsons','Mclaughlin','Zimmerman','French','Buchanan',
			'Moran','Copeland','Roy','Pittman','Brady','Mccormick','Holloway','Brock','Poole','Frank','Logan','Owen','Bass','Marsh','Drake','Wong','Jefferson',
			'Park','Morton','Abbott','Sparks','Patrick','Norton','Huff','Clayton','Massey','Lloyd','Figueroa','Carson','Bowers','Roberson','Barton','Tran',
			'Lamb','Harrington','Casey','Boone','Cortez','Clarke','Mathis','Singleton','Wilkins','Cain','Bryan','Underwood','Hogan','Mckenzie','Collier','Luna',
			'Phelps','Mcguire','Allison','Bridges','Wilkerson','Nash','Summers','Atkins','Wilcox','Pitts','Conley','Marquez','Burnett','Richard','Cochran',
			'Chase','Davenport','Hood','Gates','Clay','Ayala','Sawyer','Roman','Vazquez','Dickerson','Hodge','Acosta','Flynn','Espinoza','Nicholson','Monroe',
			'Wolf','Morrow','Kirk','Randall','Anthony','Whitaker','Oconnor','Skinner','Ware','Molina','Kirby','Huffman','Bradford','Charles','Gilmore','Dominguez',
			'Oneal','Bruce','Lang','Combs','Kramer','Heath','Hancock','Gallagher','Gaines','Shaffer','Short','Wiggins','Mathews','Mcclain','Fischer','Wall','Small',
			'Melton','Hensley','Bond','Dyer','Cameron','Grimes','Contreras','Christian','Wyatt','Baxter','Snow','Mosley','Shepherd','Larsen','Hoover','Beasley',
			'Glenn','Petersen','Whitehead','Meyers','Keith','Garrison','Vincent','Shields','Horn','Savage','Olsen','Schroeder','Hartman','Woodard','Mueller','Kemp',
			'Deleon','Booth','Patel','Calhoun','Wiley','Eaton','Cline','Navarro','Harrell','Lester','Humphrey','Parrish','Duran','Hutchinson','Hess','Dorsey',
			'Bullock','Robles','Beard','Dalton','Avila','Vance','Rich','Blackwell','York','Johns','Blankenship','Trevino','Salinas','Campos','Pruitt','Moses',
			'Callahan','Golden','Montoya','Hardin','Guerra','Mcdowell','Carey','Stafford','Gallegos','Henson','Wilkinson','Booker','Merritt','Miranda','Atkinson',
			'Orr','Decker','Hobbs','Preston','Tanner','Knox','Pacheco','Stephenson','Glass','Rojas','Serrano','Marks','Hickman','English','Sweeney','Strong','Prince',
			'Mcclure','Conway','Walter','Roth','Maynard','Farrell','Lowery','Hurst','Nixon','Weiss','Trujillo','Ellison','Sloan','Juarez','Winters','Mclean','Randolph',
			'Leon','Boyer','Villarreal','Mccall','Gentry','Carrillo','Kent','Ayers','Lara','Shannon','Sexton','Pace','Hull','Leblanc','Browning','Velasquez','Leach',
			'Chang','House','Sellers','Herring','Noble','Foley','Bartlett','Mercado','Landry','Durham','Walls','Barr','Mckee','Bauer','Rivers','Everett','Bradshaw',
			'Pugh','Velez','Rush','Estes','Dodson','Morse','Sheppard','Weeks','Camacho','Bean','Barron','Livingston','Middleton','Spears','Branch','Blevins','Chen',
			'Kerr','Mcconnell','Hatfield','Harding','Ashley','Solis','Herman','Frost','Giles','Blackburn','William','Pennington','Woodward','Finley','Mcintosh','Koch',
			'Best','Solomon','Mccullough','Dudley','Nolan','Blanchard','Rivas','Brennan','Mejia','Kane','Benton','Joyce','Buckley','Haley','Valentine','Maddox','Russo',
			'Mcknight','Buck','Moon','Mcmillan','Crosby','Berg','Dotson','Mays','Roach','Church','Chan','Richmond','Meadows','Faulkner','Oneill','Knapp','Kline','Barry',
			'Ochoa','Jacobson','Gay','Avery','Hendricks','Horne','Shepard','Hebert','Cherry','Cardenas','Mcintyre','Whitney','Waller','Holman','Donaldson','Cantu',
			'Terrell','Morin','Gillespie','Fuentes','Tillman','Sanford','Bentley','Peck','Key','Salas','Rollins','Gamble','Dickson','Battle','Santana','Cabrera',
			'Cervantes','Howe','Hinton','Hurley','Spence','Zamora','Yang','Mcneil','Suarez','Case','Petty','Gould','Mcfarland','Sampson','Carver','Bray','Rosario',
			'Macdonald','Stout','Hester','Melendez','Dillon','Farley','Hopper','Galloway','Potts','Bernard','Joyner','Stein','Aguirre','Osborn','Mercer','Bender',
			'Franco','Rowland','Sykes','Benjamin','Travis','Pickett','Crane','Sears','Mayo','Dunlap','Hayden','Wilder','Mckay','Coffey','Mccarty','Ewing','Cooley',
			'Vaughan','Bonner','Cotton','Holder','Stark','Ferrell','Cantrell','Fulton','Lynn','Lott','Calderon','Rosa','Pollard','Hooper','Burch','Mullen','Fry','Riddle',
			'Levy','David','Duke','Odonnell','Guy','Michael','Britt','Frederick','Daugherty','Berger','Dillard','Alston','Jarvis','Frye','Riggs','Chaney','Odom','Duffy',
			'Fitzpatrick','Valenzuela','Merrill','Mayer','Alford','Mcpherson','Acevedo','Donovan','Barrera','Albert','Cote','Reilly','Compton','Raymond','Mooney','Mcgowan',
			'Craft','Cleveland','Clemons','Wynn','Nielsen','Baird','Stanton','Snider','Rosales','Bright','Witt','Stuart','Hays','Holden','Rutledge','Kinney','Clements',
			'Castaneda','Slater','Hahn','Emerson','Conrad','Burks','Delaney','Pate','Lancaster','Sweet','Justice','Tyson','Sharpe','Whitfield','Talley','Macias','Irwin',
			'Burris','Ratliff','Mccray','Madden','Kaufman','Beach','Goff','Cash','Bolton','Mcfadden','Levine','Good','Byers','Kirkland','Kidd','Workman','Carney','Dale',
			'Mcleod','Holcomb','England','Finch','Head','Burt','Hendrix','Sosa','Haney','Franks','Sargent','Nieves','Downs','Rasmussen','Bird','Hewitt','Lindsay','Le',
			'Foreman','Valencia','Oneil','Delacruz','Vinson','Dejesus','Hyde','Forbes','Gilliam','Guthrie','Wooten','Huber','Barlow','Boyle','Mcmahon','Buckner','Rocha',
			'Puckett','Langley','Knowles','Cooke','Velazquez','Whitley','Noel','Vang'
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

	def randplanet(self):
		return random.choice([
			'11 UMi','14 And','14 Her','16 Cygni B','18 Del','1RXS1609','1SWASP J1407','2M 044144','2M 0746','2M 1938?','2M 2140','2M 2206-20',
			'2M1207','2MASS 0122-2439','2MASS J0219-3925','30 Ari B','4 UMa','42 Dra','47 UMa','51 Eri','51 Peg','55 Cnc','6 Lyn','61 Vir','7 CMa',
			'70 Vir','75 Cet','81 Cet','83 Leonis B','91 Aquarii A','AB Pic','alf Ari','alf Tau','Alpha Centauri B','BD 1790','BD 274','BD 2940','BD 738',
			'BD 828','BD-082823','BD-10 3166','BD-114672','BD-17 63','BD14 4559','BD20 2457','betaCancri','betaPic','betaUrsae Minoris','CFBDS 1458','CFBDSIR2149',
			'CHXR 73','CoRoT-1','CoRoT-10','CoRoT-11','CoRoT-12','CoRoT-13','CoRoT-14','CoRoT-16','CoRoT-17','CoRoT-18','CoRoT-19','CoRoT-2','CoRoT-3','CoRoT-4',
			'CoRoT-5','CoRoT-6','CoRoT-7','CoRoT-8','CoRoT-9','CT Cha','DH Tau','DP Leo','EPIC 201208431','EPIC 201295312','EPIC 201338508','EPIC 201367065',
			'EPIC 201384232','EPIC 201393098','EPIC 201403446','EPIC 201445392','EPIC 201465501','EPIC 201505350','EPIC 201828749','EPIC 201855371','EPIC 201912552',
			'EPIC 206011691','eps Coronae Borealis','eps Eridani','eps Tau','eta Cet','Fomalhaut','FU Tau','FW Tau','Gamma Cephei','Gamma Leonis','GJ 160.2','GJ 180',
			'GJ 229','GJ 27.1','GJ 422','GJ 649.02','GJ 682','Gliese 1214','Gliese 15 A','Gliese 163','Gliese 176','Gliese 179','Gliese 221','Gliese 3021 A','Gliese 317',
			'Gliese 328','Gliese 581','Gliese 649','Gliese 667 C','Gliese 674','Gliese 676 A','Gliese 687','Gliese 777 A','Gliese 785','Gliese 832','Gliese 849',
			'Gliese 86','Gliese 876','GQ Lup','GSC 06214-00210','GU Psc','HAT-P-1','HAT-P-11','HATS-3','HATS-4','HATS-5','HATS-6','HATS-7','HATS-8','HATS-9','HD 100546',
			'HD 100655','HD 100777','HD 10180','HD 101930','HD 102117','HD 102195','HD 102272','HD 95127','HD 9578','HD 96063','HD 96127','HD 96167','HD 96700','HD 97658',
			'HD 98219','HD 98649','HD 99109','HD 99706','HIP 107773','HIP 116454','HIP 11915','HIP 11952','HIP 12961','HIP 13044','HIP 14810','HIP 5158','HIP 57050',
			'HIP 57274','HIP 63242','HIP 65891','HIP 67851','HIP 70849','HIP 78530','HIP 79431','HIP 91258','HIP 97233','HN Peg','HR 810','HR 8799','HU Aqr (AB)','HW Vir (AB)',
			'iota Draconis','Kappa And','kappa CrB','Kapteyn','KELT-10','KELT-2A','KELT-3','KELT-6','KELT-7','KELT-8','Kepler-10','Kepler-100','Kepler-101','Kepler-102','Kepler-20',
			'Kepler-200','Kepler-201','Kepler-202','Kepler-447','Kepler-449','Kepler-45','Kepler-450','Kepler-452','Kepler-46','Kepler-47 (AB)','Kepler-48','Kepler-49','Kepler-5',
			'Kepler-50','Kepler-51','Kepler-52','Kepler-53','Kepler-54','Kepler-55','Kepler-56','Kepler-57','Kepler-89','Kepler-9','Kepler-90','Kepler-91','Kepler-93','Kepler-94',
			'Kepler-95','Kepler-96','Kepler-97','Kepler-98','Kepler-99','KIC 10001893','KIC 10905746','KIC 6185331','KIC 8435766','KIC 9632895','KMT-2015-1','KOI-1194','KOI-1194.02',
			'KOI-12','KOI-1257','KOI-1299','KOI-135','KOI-142','KOI-1474','KOI-1576.03','KOI-1612.01','KOI-1781','KOI-1781.01','KOI-523.02','KOI-55','KOI-680','KOI-806.01',
			'KOI-806.02','KOI-806.03','KOI-830','LkCa 15','Lupus-TR 3b','MOA-2007-BLG-192-L','MOA-2007-BLG-400-L','MOA-2008-BLG-310-L','MOA-2008-BLG-379L','MOA-2009-BLG-266L',
			'OGLE-2008-BLG-092L','OGLE-2008-BLG-355L','OGLE-2011-BLG-0251','OGLE-2011-BLG-0265L','OGLE-2012-BLG-0026L','OGLE-2012-BLG-0358L','OGLE-2012-BLG-0406L',
			'OGLE-2013-BLG-0102LB','OGLE-2013-BLG-0341L B','OGLE-2013-BLG-0723LB','OGLE-2015-BLG-0563L','OGLE-2015-BLG-0966L','OGLE-TR-10','OGLE-TR-111','OGLE-TR-113','OGLE-TR-132',
			'OGLE-TR-182','OGLE-TR-211','OGLE-TR-56','OGLE2-TR-L9','OGLE235-MOA53','Omega Serpentis','omi CrB','omi UMa','Oph 11','PH-1 A(ab)','PH-2','PH3','POTS-1','Pr0201','Pr0211',
			'PSO J318.5-22','PSR 1257 12','PSR B1620-26','PSR J1719-1438','PTFO 8-8695','Quatar-1','Quatar-2','Rho Coronae Borealis','Ross 458','ROXs 12','ROXs 42 B','RR Cae (AB)',
			'SAND364','SR 12','SWEEPS-11','SWEEPS-4','tau Boo A','tau Ceti','tau Gem','TrES-1','TrES-2','TrES-3','TrES-4 A','TrES-5','TYC 1422-614-1','Upsilon Andromedae A',
			'UScoCTIO 108','UZ For(ab)','V391 Peg','VHS 1256-1257','WASP-1','WASP-10','WASP-100','WASP-101','WASP-103','WASP-104','WASP-106','WASP-108','WASP-109','WASP-11','WASP-110',
			'WASP-111','WASP-112','WASP-117','WASP-12','WASP-120','WASP-121','WASP-122','WASP-123','WASP-13','WASP-14','WASP-15','WASP-16','WASP-17','WASP-18','WASP-19','WASP-2 A',
			'WASP-20','WASP-21','WASP-22','WASP-23','WASP-24','WASP-25','WASP-26','WASP-28','WASP-29','WASP-3','WASP-31','WASP-32','WASP-33','WASP-34','WASP-35','WASP-36','WASP-37',
			'WASP-38','WASP-39','WASP-4','WASP-41','WASP-42','WASP-43','WASP-44','WASP-97','WASP-98','WASP-99','WD 0806-661','WTS-1','WTS-2','xi Aql','XO-1','XO-2N','XO-2S','XO-3','XO-4',
			'XO-5','YBP1194','YBP1514','HD 142','GJ 3021','HIP 2247','54 Piscium','Upsilon Andromedae','109 Piscium','Eta2 Hydri','HD 11964','Alpha Arietis','HD 15082','79 Ceti',
			'30 Arietis','81 Ceti','Iota Horologii','SAO 38269','94 Ceti','82 G. Eridani','Epsilon Eridani','UZ Fornacis','HD 24496','Epsilon Reticuli','Epsilon Tauri','2M J044144',
			'Pi Mensae','HD 38529','Beta Pictoris','HD 41004','HD 40979','6 Lyncis','HD 46375','7 Canis Majoris','Gliese 253','NGC 2423-3','Pollux','XO-2','GJ 3483','WASP-51',
			'4 Ursae Majoris','HD 75289','55 Cancri','41 Lyncis','Gliese 370','HIP 49067','BD+20°2457','Gamma1 Leonis','HD 89744','HD 233731','24 Sextantis','BD-10°3166','GJ 3634',
			'47 Ursae Majoris','DP Leonis','83 Leonis','Gliese 439','HD 106515','HD 109749','Chi Virginis','HW Virginis','PSR B1257+12','HD 114729','61 Virginis','70 Virginis',
			'NY Virginis','Tau Boötis','Qatar-2','HD 126614','Alpha Centauri','HAT-P-27/WASP-40','HD 132563','CFBDS 1448','23 Librae','11 Ursae Minoris','Lupus-TR-3','Kappa Coronae Borealis',
			'NN Serpentis','1RXS 1609','HD 142022','14 Herculis','HD 146389','HD 147513','WASP-70','MOA-2008-BLG-310L','GJ 1214','Gliese 667','Gliese 676','OGLE-2005-BLG-071L',
			'OGLE-2006-BLG-109L','TrES-4','OGLE-2005-BLG-390L','SWEEPS-04','OGLE-2003-BLG-235L','OGLE-2005-BLG-169L','MOA-2009-BLG-319L','MOA-2007-BLG-192L','MOA-2007-BLG-400L',
			'42 Draconis','Kepler-30','HD 177830','HD 178911','HD 179070','Kepler-16','KOI-410','KOI-254','Kepler-35','16 Cygni','Kepler-70','Kepler-34','Kepler-40','HD 188015',
			'KOI-730','Xi Aquilae','HD 189733','Gliese 777','Qatar-1','HD 195019','WASP-2','HD 196050','HD 196885','18 Delphini','WASP-11/HAT-P-10','HIP 104780','V391 Pegasi',
			'HD 213240','Tau1 Gruis','Rho Indi','51 Pegasi','91 Aquarii','14 Andromedae','HD 222582'
		])

	def randomdate(self, format, start, end):
		starttime = time.mktime(time.strptime(start, format))
		endtime = time.mktime(time.strptime(end, format))
		ptime = starttime + random.random() * (endtime - starttime)
		return time.strftime(format, time.localtime(ptime))

	def randengphrase(self, maxlength):
		result = self.randengword()
		if len(result) > maxlength:
			self.randword(maxlength)
		phrase = result + ' ' + self.randfreqengword() + ' ' + self.randengword()
		if len(phrase) > maxlength:
			return result
		return phrase

	def randuser(self, randlen):
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

	def randhex(self, len):
		lst = [random.choice('0123456789ABCDEF') for i in range(len)]
		return "".join(lst)

	def randbdate(self):
		return self.randomdate('%d.%m.%Y', "01.01.1930", "01.01.2000")

	def randthought(self):
		return self.randhex(random.randrange(16,32))

	def randform(self, rnd, vuln, i, state, flag):
		if i == 0:
			return {'action': 'load'}
		if i == 1:
			return {
				'action': 'next',
				'fields':{
					'name': self.randname(),
					'sname': self.randsurname(),
					'bdate': self.randbdate(),
					'bplace': flag if vuln == 2 else self.randplanet(),
					'mphone': self.randhex(8)},
				'state': state}
		if i == 2:
			return {
				'action': 'next',
				'fields': {
					'occup': self.randplanet(),
					'empl': self.randengphrase(48)},
				'state': state}
		if i == 3:
			self.debug('Rnd: ' + rnd)
			return {
				'action': 'next',
				'fields': {
					'thought': flag if vuln == 1 else self.randengphrase(32),
					'rnd': rnd,
					'sign': self.sign(rnd)},
				'state': state}
		if i == 4:
			return {
				'action': 'next',
				'fields': {
					'private': 'yes' if vuln == 1 else '',
					'offer': 'yes'},
				'state': state}
		raise

	def existsfield(self, fields, name):
		for field in fields:
			if field and field.get('name') == name:
				return True
		return False

	def findfield(self, fields, name):
		for field in fields:
			if field and field.get('name') == name:
				return field.get('value')
		return None

	def checkfields(self, form, names):
		if not form or isBlank(form.get('state')):
			return False
		fields = form.get('fields')
		if not fields or not isinstance(fields, list) or len(fields) == 0:
			return False
		for name in names:
			if not self.existsfield(fields, name):
				return False
		return True

	def checkform(self, form, i, flag):
		if i == 5:
			return not isBlank(form)
		fields = []
		if i == 1: fields = ['name', 'sname', 'bdate', 'bplace', 'mphone']
		if i == 2: fields = ['occup', 'empl']
		if i == 3:
			if not self.checkfields(form, ['thought', 'rnd', 'sign']):
				return False
			rnd = self.findfield(form.get('fields'), 'rnd')
			if not (rnd and all(c in string.hexdigits for c in rnd)):
				return False
			return True
		if i == 4: fields = ['private', 'offer']
		if len(fields) == 0: raise
		return self.checkfields(form, fields)

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

	def register(self, s, addr):
		user = self.randuser(1)
		self.debug('User: ' + str(user))

		for i in range(0, 3):
			try:
				result = self.jposts(s, addr, '/auth/', user)
				self.debug('Auth: ' + str(result))

				if result != 'OK':
					raise CheckException(EXITCODE_MUMBLE, 'registration failed')

				break

			except HttpWebException as e:
				if e.value != 403 or i == 2:
					raise CheckException(EXITCODE_MUMBLE, 'registration failed')

				user = self.randuser(i * 5)

		return user

	def fillform(self, s, addr, flag, vuln, user, withlast):
		state = ''
		rnd = ''

		for i in range(0, 4):
			form = self.randform(rnd, vuln, i, state, flag)
			self.debug('Send[' + str(i) + ']: ' + str(form))
			result = self.jpost(s, addr, '/form/', form)
			self.debug('Recv[' + str(i + 1) + ']: ' + str(result)[:1024] + '...')

			if not self.checkform(result, i + 1, flag):
				raise CheckException(EXITCODE_MUMBLE, 'form step' + str(i + 1) + 'failed')

			state = result.get('state')
			rnd = '' if i != 2 else self.findfield(result.get('fields'), 'rnd')

		if withlast:
			form = self.randform('', vuln, 4, state, flag)
			self.debug('Send[4]: ' + str(form))
			result = self.jposts(s, addr, '/form/', form)
			self.debug('Recv[5]: ' + str(result)[:1024] + '...')

			if not result:
				raise CheckException(EXITCODE_MUMBLE, 'form step 5 failed')

			if result.find(flag) < 0:
				raise CheckException(EXITCODE_CORRUPT, 'flag not found')

		return result

	#################
	#      GET      #
	#################
	def get(self, addr, flag_id, flag, vuln):
		s = self.session(addr)

		if vuln == 1:
			user = self.register(s, addr)
			result = self.fillform(s, addr, flag, vuln, user, False)
			if not str(result).find(flag):
				print('flag not found')
				return EXITCODE_CORRUPT

		if vuln == 2:
			parts = flag_id.split(':', 2)
			user = {'login':parts[0], 'pass':parts[1]}

			self.debug('User: ' + str(user))

			result = self.sget(s, addr, '/last/')
			self.debug('Last: ' + str(result)[:512])

			if not result or result.find(user['login']) < 0:
				print('not found self in /last/')
				return EXITCODE_MUMBLE

			result = self.jposts(s, addr, '/auth/', user)
			self.debug('Auth: ' + str(result))

			if result != 'OK':
				print('login failed')
				return EXITCODE_MUMBLE

			result = self.jposts(s, addr, '/form/')
			self.debug('Form: ' + str(result)[:1024])

			if not result or result.find(flag) < 0:
				print('flag not found')
				return EXITCODE_CORRUPT

		return EXITCODE_OK

	#################
	#      PUT      #
	#################
	def put(self, addr, flag_id, flag, vuln):
		s = self.session(addr)

		user = self.register(s, addr)
		result = self.fillform(s, addr, flag, vuln, user, True)

		if vuln == 2:
			result = self.sget(s, addr, '/last/')
			self.debug('Last: ' + str(result)[:512])

			if not result or result.find(user['login']) < 0:
				print('not found self in /last/')
				return EXITCODE_MUMBLE

		print('{}:{}'.format(user['login'], user['pass']))
		return EXITCODE_OK

Checker().run()
