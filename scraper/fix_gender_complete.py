"""
KOMPLETT SCRIPT FOR Å FIKSE KJØNN PÅ UTØVERE

Kjør dette scriptet for å fikse alle kjønnsfeil i databasen.

Steg:
1. Reset gender=NULL for utøvere uten autoritative øvelser
2. Sett kjønn basert på autoritative høydespesifikke øvelser
3. Sett kjønn basert på norske fornavn
4. Forsiktig inferens fra medkonkurrenter (kun hvis alle har samme kjønn)
"""

import os
from collections import defaultdict
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))

# ============================================================
# NORSKE NAVN
# ============================================================

MALE_NAMES = {
    'ole', 'per', 'jan', 'lars', 'erik', 'anders', 'bjørn', 'tor', 'jon', 'hans',
    'knut', 'svein', 'arne', 'karl', 'rolf', 'leif', 'odd', 'geir', 'terje', 'morten',
    'øyvind', 'trond', 'john', 'ola', 'magnus', 'petter', 'thomas', 'martin', 'christian',
    'andreas', 'henrik', 'kristian', 'sindre', 'vegard', 'espen', 'stian', 'håkon',
    'sondre', 'erlend', 'øystein', 'atle', 'steinar', 'frode', 'ivar', 'nils', 'einar',
    'vidar', 'arve', 'helge', 'ragnar', 'roar', 'sverre', 'tore', 'sigurd', 'gunnar',
    'eirik', 'jostein', 'ketil', 'jørgen', 'stig', 'finn', 'roy', 'kjell', 'dag',
    'hallvard', 'harald', 'olav', 'pål', 'rune', 'stein', 'bent', 'egil', 'gustav',
    'jarle', 'jonny', 'kai', 'kåre', 'magne', 'oddvar', 'olaf', 'robin', 'runar',
    'sturla', 'tarjei', 'torbjørn', 'trygve', 'vetle', 'william', 'alexander',
    'aleksander', 'aksel', 'adrian', 'albert', 'alfred', 'anton', 'arvid', 'asbjørn',
    'audun', 'birger', 'bård', 'christer', 'christopher', 'daniel', 'david', 'didrik',
    'eivind', 'elias', 'emil', 'even', 'filip', 'frank', 'fredrik', 'gabriel', 'gaute',
    'glenn', 'guttorm', 'håvard', 'jacob', 'jakob', 'jens', 'jim', 'joachim', 'joakim',
    'johan', 'jonas', 'jonathan', 'jørn', 'kasper', 'kim', 'klaus', 'kristoffer',
    'lasse', 'leon', 'lukas', 'marcus', 'markus', 'mathias', 'mattias', 'max',
    'michael', 'mikael', 'mikkel', 'nicolai', 'nikolai', 'oliver', 'oskar', 'oscar',
    'otto', 'patrik', 'patrick', 'paul', 'peter', 'philip', 'rasmus', 'richard',
    'robert', 'roger', 'samuel', 'sebastian', 'sigbjørn', 'simon', 'snorre', 'stefan',
    'steffen', 'sven', 'tobias', 'tommy', 'torgeir', 'vebjørn', 'viktor', 'viljar',
    'yngve', 'are', 'asle', 'børge', 'bernt', 'bjarne', 'brage', 'carl', 'cornelius',
    'eldar', 'erland', 'erling', 'ernst', 'gard', 'georg', 'gisle', 'gøran', 'haakon',
    'hallgeir', 'halvard', 'henning', 'herman', 'hjalmar', 'inge', 'ingolf', 'ingvar',
    'isak', 'ivan', 'iver', 'jack', 'jardar', 'kenneth', 'kevin', 'konrad', 'krister',
    'kyrre', 'laurits', 'lennart', 'levi', 'ludvig', 'magnar', 'marius', 'mats',
    'morgan', 'noel', 'ørjan', 'preben', 'raymond', 'reidar', 'rikard', 'ronny',
    'sigmund', 'sigve', 'sivert', 'sjur', 'skjalg', 'stale', 'ståle', 'sveinung',
    'tarald', 'teodor', 'tim', 'tomas', 'toralf', 'torben', 'torfinn', 'tormod',
    'torstein', 'truls', 'ulrik', 'valter', 'willy', 'yngvar', 'noah', 'leo', 'liam',
    'theo', 'felix', 'edvin', 'august', 'axel', 'benjamin', 'dennis', 'edward',
    'johannes', 'julius', 'maximilian', 'mattis', 'borre', 'joar', 'henric',
    'jonatan', 'ingar', 'sander', 'victor', 'arild', 'simen', 'odin', 'nataniel',
    'muhammed', 'christoffer', 'tom', 'aage', 'gjermund', 'arnstein', 'faton',
    'aron', 'maximillian', 'edvard', 'åsmund', 'mohammed', 'mohamed', 'ahmad',
    'ahmed', 'ali', 'omar', 'yusuf', 'ibrahim', 'hassan', 'hussein', 'mustafa',
    'kjetil', 'trym', 'eskil', 'peder', 'theodor', 'bjørnar', 'thor', 'halvor',
    'mads', 'amund', 'alf', 'endre', 'lucas', 'jesper', 'julian', 'ove', 'tord',
    'bendik', 'niklas', 'birk', 'andré', 'linus', 'torjus', 'casper', 'øivind',
    'johnny', 'matias', 'ådne', 'vemund', 'roald', 'jo', 'åge', 'ask', 'ruben',
    'brede', 'fabian', 'karsten', 'nicholas', 'heine', 'andre', 'jone', 'oddbjørn',
    'dagfinn', 'ottar', 'arnt', 'kjartan', 'levon', 'julien', 'leandro', 'fernando',
    'matheo', 'hamdan', 'didier', 'florian', 'lauritz', 'vilhelm', 'ansgar',
    'ørnulf', 'torkel', 'kolbjørn', 'gudmund', 'svend', 'waldemar', 'widar',
    'henry', 'bjarte', 'wilhelm', 'kurt', 'arnfinn', 'aslak', 'ludvik', 'adam',
    'hermann', 'mikal', 'storm', 'nicolay', 'tage', 'leander', 'thorbjørn', 'idar',
    'oddmund', 'syver', 'kristen', 'eilif', 'eric', 'olve', 'tristan', 'phillip',
    'ulf', 'thore', 'kaare', 'olai', 'martinus', 'thorvald', 'arthur', 'torje',
    'vincent', 'njål', 'ørjan', 'flemming', 'aksel', 'bastian', 'bard', 'borgar',
    'brynjar', 'dagmar', 'edvart', 'eilert', 'eivind', 'eldar', 'elmer', 'embrik',
    'engelbert', 'eugen', 'evald', 'folke', 'fridtjof', 'frithjof', 'gerhard',
    'gjert', 'godtfred', 'greger', 'gudvin', 'gunvald', 'halvdan', 'hartvig',
    'hjalmar', 'hårek', 'ingemar', 'ingmar', 'jaroslav', 'joacim', 'joakim',
    'johannes', 'josva', 'jørund', 'keld', 'kjeld', 'klas', 'kolbein', 'konrad',
    'kornelius', 'kristofer', 'laars', 'laurits', 'leiv', 'lorents', 'lydolf',
    'magne', 'malvin', 'mandius', 'marthin', 'mathis', 'morten', 'nikolay',
    'oddgeir', 'oddleif', 'oddvin', 'olavus', 'osmund', 'osvald', 'parelius',
    'ragvald', 'randolf', 'reinert', 'roalv', 'rolv', 'salomon', 'selmer',
    'severin', 'sigbjørn', 'sigfred', 'sigvard', 'sjur', 'skule', 'snorri',
    'solmund', 'sondov', 'steingrim', 'styrk', 'svanhild', 'sveinung', 'sylvest',
    'tancred', 'tarjei', 'tellef', 'tønnes', 'toralf', 'toralv', 'torjei',
    'torleif', 'tormod', 'torolf', 'torvald', 'tryggve', 'ulvar', 'valentin',
    'vegar', 'vigleik', 'vilfred', 'villiam', 'vinjar', 'yngvar', 'ytteborg',
    'hugo', 'jarl', 'martinius', 'joel', 'eskild', 'stephan', 'nicklas', 'cato',
    'arian', 'thorleif', 'nathaniel', 'luca', 'harry', 'viggo', 'bengt', 'agnar',
    'sten', 'jarand', 'børre', 'kent', 'dan', 'nicolas', 'sean', 'scott', 'brian',
    'torleiv', 'louis', 'tony', 'fillip', 'mons', 'isac', 'steven', 'narve',
    'emrik', 'jøran', 'abdi', 'bo', 'ben', 'bernhard', 'niels', 'helmer', 'edgar',
    'haldor', 'torgrim', 'abraham', 'fred', 'eystein', 'arnulf', 'ib', 'ivar',
    'ivan', 'jack', 'james', 'jamie', 'jan-erik', 'jan-ove', 'jarle', 'jason',
    'jay', 'jeff', 'jim', 'jimmy', 'joe', 'john', 'johnny', 'jon', 'jørn',
    'josh', 'joshua', 'kai', 'karl', 'keith', 'kelly', 'ken', 'kevin', 'kris',
    'kyle', 'lars', 'lee', 'leo', 'leonard', 'liam', 'luke', 'magne', 'marc',
    'mark', 'martin', 'matt', 'matthew', 'max', 'michael', 'mike', 'morten',
    'neil', 'nick', 'nils', 'noah', 'odd', 'ole', 'oscar', 'otto', 'pal',
    'pat', 'patrick', 'paul', 'per', 'pete', 'peter', 'phil', 'pierre', 'ralph',
    'ray', 'remi', 'rene', 'richard', 'rick', 'rob', 'robert', 'robin', 'rod',
    'ron', 'ross', 'roy', 'rune', 'ryan', 'sam', 'samuel', 'seth', 'shane',
    'simon', 'stan', 'steve', 'stuart', 'sven', 'ted', 'terry', 'theo', 'thomas',
    'tim', 'todd', 'tony', 'travis', 'troy', 'vic', 'wayne', 'will', 'william',
    'njord', 'kaspar', 'ian', 'svenn', 'ferdinand', 'igor', 'emmanuel', 'michal',
    'håvar', 'ingebrigt', 'paal', 'aaron', 'kacper', 'hågen', 'andrè', 'søren',
    'bror', 'mateo', 'asgeir', 'matheus', 'tinius', 'rafael', 'freddy', 'amandus',
    'mika', 'antonio', 'carlos', 'mario', 'yonas', 'andres', 'askil', 'silas',
    'fritz', 'andrew', 'luka', 'alvin', 'hamza', 'roland', 'hilmar', 'abdirahman',
    'esten', 'chris', 'tron', 'aasmund', 'charles', 'norvald', 'imre', 'abel',
    'normann', 'kay', 'nikolas', 'fredrick', 'marlon', 'øistein', 'leonardo',
    'ingvald', 'alan', 'eimund', 'heljar', 'elling', 'thoralf', 'alex', 'emanuel',
    'elliot', 'thorstein', 'teo', 'jonah', 'ole-martin', 'nahom', 'pelle', 'eigil',
    'sølve', 'baard', 'lorentz', 'torkjell', 'marco', 'rudi', 'torger', 'eyvind',
    'torodd', 'haavard', 'kaj', 'ingve', 'matteo', 'arnold', 'frederick', 'josef',
    'mateusz', 'andor', 'marvin', 'alv', 'sturle', 'arnljot', 'ragnvald', 'gorm',
    'halfdan', 'sture', 'brynjulf', 'hogne', 'frederik', 'rené', 'arn', 'tov',
    'mohammad', 'conrad', 'roman', 'per-christian', 'samson', 'dominik', 'jeppe',
    'villy', 'ricardo', 'thorolf',
    'ronald', 'yasin', 'hakeem', 'abou', 'jakop', 'patryk', 'osman', 'torkil',
    'elijah', 'mulugeta', 'aleksandr', 'albin', 'filmon', 'awet', 'abdullahi',
    'stephen', 'tørres', 'kamil', 'lyder', 'kalle', 'alexsander', 'ari', 'lage',
    'lavrans', 'rudolf', 'vilmer', 'damian', 'francis', 'geirmund', 'melvin',
    'caspian', 'jaran', 'leopold', 'kidane', 'arvin', 'roy-arne', 'jon-anders',
    'ovar', 'odvar', 'emre', 'matthias', 'almar', 'rein', 'abbas', 'abdul',
    'khaled', 'jann', 'jomar', 'caspar', 'hauk', 'nordahl', 'anker', 'edwin',
    'emilian', 'sakariye', 'neo', 'grunde', 'eilev', 'gudbrand', 'askild', 'benny',
    'nickolai', 'hans-petter', 'bjørn-erik', 'mahad', 'lars-erik', 'francesco',
    'isaac', 'anthony', 'mahmoud', 'jamal', 'julio', 'hadi', 'bork', 'kilian',
    'charlie', 'said', 'salim', 'allan', 'robel', 'ole-kristian', 'svale',
    'matteus', 'falk', 'marcel', 'eh',
    'frederic', 'dominic', 'engebret', 'bartek', 'mårten', 'enrico', 'jeremiah',
    'ravn', 'edem', 'kenny', 'torolv', 'frans', 'jonn', 'oddne', 'tom-erik',
    'arsen', 'ebbe', 'karl-henrik', 'hallstein', 'siem', 'franz', 'lars-petter',
    'ole-petter', 'osama', 'ole-jørgen', 'eljar', 'timothy', 'matti', 'niclas',
    'bredo', 'svein-erik', 'antoni', 'hagbart', 'per-kristian', 'berg', 'jakub',
    'linas', 'angelo', 'jonar', 'hector', 'amanuel', 'christen', 'yoab',
    'alexandre', 'deniz', 'arnodd', 'nathan', 'tam', 'hannes', 'sharmarke',
    'christofer', 'fritjof', 'carl-fredrik', 'lars-martin', 'carlo', 'hermund',
    'ralfs', 'kianosh', 'lars-kristian', 'mikail', 'jasper', 'abdinasir',
    'nikodem', 'claes', 'jorulf', 'hampus', 'mahdi', 'ard', 'luc', 'callum',
    'buster', 'bertil', 'anbjørn', 'dawit', 'reidulf', 'matz', 'rayan', 'ludwig',
    'morgun', 'arnbjørn', 'werner', 'siver', 'jesse', 'asmund', 'tiago', 'vili',
    'ingulf', 'ghulam', 'stener', 'valdemar', 'pablo', 'rivo', 'maciej', 'thure',
    'gjøran', 'ramatullah', 'brandon', 'christoph', 'sergio', 'kitsadakon',
    'mykyta', 'andrii', 'bruno', 'bashar', 'nabil', 'eiliv', 'kirill', 'norman',
    'ingemund', 'oliwer', 'yonatan', 'jaden', 'xander', 'lorns', 'lars-olav',
    'holger', 'tor-arne', 'eddy', 'phurinat', 'yrjan', 'taha', 'eliah', 'solan',
    'skage', 'lidvin', 'thord', 'walter', 'halstein', 'johnson', 'aadne',
    'sigvald', 'pedro', 'mathusan', 'prince', 'juan', 'sami', 'zidane', 'leul',
    'mariusz', 'janis', 'keerthan', 'hans-erik', 'poul', 'bernard', 'olaus',
    'younes', 'jeton', 'marton', 'ole-marius', 'arno', 'dani', 'jahn', 'federico',
    'mykola', 'wilmer', 'halldor', 'matas', 'john-atle', 'raphael', 'nivethan',
    'mehdi', 'carsten', 'lewis', 'ketill', 'tjerand', 'torkjel', 'hubert',
    'baste', 'jan-olav', 'feruz', 'østen', 'george', 'tarek', 'timo', 'naser',
    'benyam', 'nicholai', 'tonny', 'etienne', 'greg', 'jose', 'amadeus', 'sultan',
    'augustin', 'shahid', 'sevat', 'eduard', 'anthon', 'tjærand', 'mauritz',
    'kajus', 'moritz', 'marko', 'paulo', 'edvald', 'balder', 'clement', 'elian',
    'justin', 'wilfred', 'floris', 'thias', 'cedrik', 'andrei', 'isack', 'romeo',
    'loke', 'oleksandr', 'yevhenii', 'gerard', 'maxime', 'jan-åge'
}

FEMALE_NAMES = {
    'anna', 'anne', 'eva', 'liv', 'kari', 'marit', 'ingrid', 'bjørg', 'randi', 'ellen',
    'berit', 'marie', 'britt', 'solveig', 'inger', 'gerd', 'nina', 'hilde', 'astrid',
    'wenche', 'tone', 'sissel', 'gunn', 'trine', 'hege', 'lene', 'monica', 'kristin',
    'mette', 'anita', 'torill', 'else', 'elisabeth', 'camilla', 'karen', 'siri',
    'ragnhild', 'ruth', 'helen', 'ida', 'line', 'maria', 'cathrine', 'grete', 'mona',
    'anette', 'linda', 'ann', 'heidi', 'kirsten', 'turid', 'margaret', 'birgit',
    'sigrid', 'julie', 'stine', 'marianne', 'cecilie', 'therese', 'elin', 'karin',
    'eli', 'henriette', 'martine', 'sara', 'susanne', 'andrea', 'jenny', 'vilde',
    'emilie', 'thea', 'nora', 'emma', 'sofie', 'sophie', 'maja', 'aurora', 'olivia',
    'frida', 'leah', 'amalie', 'karoline', 'charlotte', 'victoria', 'amanda', 'selma',
    'helene', 'mathilde', 'tuva', 'synne', 'hedda', 'maren', 'ingeborg', 'guro',
    'silje', 'linn', 'tonje', 'ane', 'renate', 'vibeke', 'hanne', 'laila', 'bodil',
    'jorunn', 'magni', 'oddny', 'magnhild', 'borgny', 'dagny', 'hjørdis', 'åse',
    'aslaug', 'gudrun', 'gunhild', 'hildur', 'oddveig', 'sigrun', 'synnøve', 'torild',
    'unn', 'åslaug', 'bente', 'brit', 'dordi', 'edel', 'eldbjørg', 'elsa', 'erna',
    'gerda', 'grethe', 'irene', 'johanne', 'klara', 'lise', 'magda', 'margit',
    'martha', 'may', 'nancy', 'petra', 'rakel', 'reidun', 'sigfrid', 'svanhild',
    'tordis', 'unni', 'vera', 'agnes', 'alexandra', 'alice', 'amelia', 'angela',
    'anja', 'anneli', 'annika', 'bella', 'benedicte', 'bianca', 'caroline', 'celia',
    'christina', 'clara', 'cornelia', 'daniela', 'diana', 'dina', 'ebba', 'edith',
    'eirin', 'elina', 'elise', 'ella', 'ellinor', 'elvira', 'emily', 'erika', 'ester',
    'fanny', 'felicia', 'filippa', 'fiona', 'flora', 'fredrikke', 'gabriella', 'gina',
    'hanna', 'hedvig', 'helena', 'hermine', 'iben', 'ina', 'ines', 'iris', 'isabella',
    'iselin', 'jennifer', 'josefine', 'julia', 'june', 'kate', 'katinka', 'katrine',
    'kjersti', 'kornelia', 'kristine', 'lena', 'leonora', 'lilly', 'linnea', 'lisa',
    'lotta', 'lotte', 'louisa', 'louise', 'lucia', 'luna', 'lydia', 'madeleine',
    'magdalena', 'maggie', 'malene', 'margrete', 'margrethe', 'mariana', 'mariell',
    'marina', 'marlene', 'mathea', 'mia', 'michelle', 'mie', 'mille', 'mina',
    'miriam', 'nadia', 'natalie', 'natasha', 'nellie', 'nicole', 'nikoline', 'olga',
    'patricia', 'pauline', 'pernille', 'philippa', 'pia', 'rebecca', 'regine',
    'rebekka', 'rosa', 'rosalie', 'rose', 'ronja', 'sandra', 'sarah', 'signe',
    'silva', 'simone', 'siv', 'sonja', 'stella', 'stephanie', 'tara', 'teresa',
    'tiril', 'tomine', 'toril', 'ulrikke', 'valborg', 'valentina', 'veronika', 'ylva',
    'erle', 'alicia', 'leona', 'carla', 'eliana', 'hannah', 'malin', 'helma',
    'liselotte', 'hennie', 'lone', 'lara', 'lina', 'elida', 'beate', 'kaia',
    'athina', 'tora', 'serine', 'oddbjørg', 'maya', 'thanida', 'marielle',
    'lisbeth', 'lissie', 'brooklyn', 'aila', 'fatima', 'amina', 'layla', 'yasmin',
    'zahra', 'mariam', 'aisha', 'khadija', 'samira', 'leila', 'sara', 'hana',
    'mari', 'marte', 'oda', 'kaja', 'sunniva', 'eline', 'ingvild', 'marthe',
    'christine', 'celine', 'kristina', 'andrine', 'sofia', 'rikke', 'live', 'ine',
    'helle', 'anniken', 'johanna', 'lea', 'maiken', 'alva', 'tina', 'gro', 'ada',
    'kamilla', 'tove', 'oline', 'ingunn', 'alma', 'merete', 'inga', 'kine',
    'matilde', 'sanna', 'maia', 'sina', 'sanne', 'trude', 'janne', 'eira',
    'viktoria', 'isabel', 'birgitte', 'karina', 'karianne', 'nathalie', 'kirsti',
    'kathrine', 'madelen', 'stina', 'celina', 'marita', 'mali', 'runa',
    'hildegunn', 'evelina', 'guri', 'gyrid', 'vilja', 'åsa', 'bertine', 'ova',
    'aimy', 'ericka', 'magdeli', 'aila-sofie', 'may-britt', 'brita', 'dagrun',
    'eldrid', 'frøydis', 'gunnvor', 'herborg', 'ingebjørg', 'jorid', 'kristi',
    'lovise', 'margot', 'olaug', 'rigmor', 'solrun', 'torbjørg', 'vanja', 'wendy',
    'benedikte', 'åshild', 'åsne', 'veronica', 'elena', 'fride', 'isabelle',
    'katarina', 'thale', 'milla', 'tilde', 'kajsa', 'frøya', 'elisa', 'aina',
    'helga', 'torunn', 'solfrid', 'marta', 'anine', 'laura', 'carina', 'vigdis',
    'juni', 'ragna', 'kaisa', 'kristiane', 'astri', 'vanessa', 'isabell', 'adele',
    'emilia', 'linea', 'angelica', 'mariann', 'alida', 'gry', 'marion', 'siren',
    'monika', 'una', 'embla', 'tyra', 'lillian', 'tine', 'ana', 'aud', 'dagmar',
    'alfhild', 'alvhild', 'arnhild', 'bergljot', 'bjørghild', 'brynhild', 'dagny',
    'dis', 'dorthea', 'dorthe', 'edle', 'eila', 'elfrid', 'elfrida', 'elvine',
    'embret', 'engel', 'erikka', 'evelyn', 'fredrikke', 'garda', 'gjertrud',
    'greta', 'gullborg', 'gunborg', 'gunda', 'gunnbjørg', 'gunnhild', 'haldis',
    'hallbjørg', 'halldis', 'hedvig', 'helfrid', 'helma', 'herdis', 'hjørdis',
    'hulda', 'ildri', 'ingeliv', 'ingfrid', 'inghild', 'ingri', 'isrid', 'jenny',
    'jofrid', 'jørgine', 'kjellaug', 'klaudia', 'konstanse', 'kornelia', 'lajla',
    'leikny', 'lena', 'leonarda', 'lina', 'ludmila', 'magnhild', 'malena', 'margit',
    'marikken', 'martha', 'mathea', 'minda', 'nanna', 'nelly', 'nora', 'oddlaug',
    'oddrun', 'olava', 'olena', 'ovidia', 'paulina', 'ragnfrid', 'ragnhild',
    'rannveig', 'reidun', 'ronja', 'rønnaug', 'salome', 'sanna', 'sigfrid',
    'siglaug', 'signhild', 'sigvor', 'signy', 'sigrunn', 'silla', 'solbjørg',
    'sollaug', 'solvor', 'svanhild', 'svea', 'sylvia', 'terese', 'tordis',
    'torfrid', 'torhild', 'torlaug', 'torunn', 'tove', 'tulle', 'ulla', 'unni',
    'valdis', 'valgjerd', 'vally', 'vebjørg', 'veslemøy', 'vivi', 'yngvild',
    'wilma', 'merethe', 'jeanette', 'bettina', 'olea', 'julianne', 'nicoline',
    'idun', 'lykke', 'paula', 'tirill', 'mira', 'othilie', 'ingvill', 'tale',
    'josephine', 'jannicke', 'tea', 'idunn', 'jorun', 'cecilia', 'siw', 'liva',
    'agnete', 'une', 'sidsel', 'tanja', 'cassandra', 'norah', 'vår', 'jessica',
    'agathe', 'henny', 'rita', 'jennie', 'thelma', 'mathilda', 'eivor', 'carmen',
    'selina', 'sophia', 'aase', 'naomi', 'jane', 'alvilde', 'lilja', 'vårin',
    'annie', 'esther', 'henrikke', 'juliane', 'alise', 'amy', 'andrea', 'angela',
    'ann', 'anna', 'anne', 'april', 'ashley', 'barbara', 'beth', 'betty',
    'brenda', 'brittany', 'carol', 'catherine', 'cheryl', 'christina', 'cindy',
    'claire', 'crystal', 'cynthia', 'dana', 'danielle', 'dawn', 'debbie',
    'deborah', 'denise', 'diana', 'diane', 'donna', 'dorothy', 'eileen', 'elaine',
    'elizabeth', 'ellen', 'emily', 'erica', 'erin', 'frances', 'grace', 'hannah',
    'heather', 'helen', 'holly', 'jackie', 'janet', 'janice', 'jean', 'jennifer',
    'jill', 'joan', 'joanne', 'jodi', 'joyce', 'judith', 'judy', 'julia',
    'julie', 'karen', 'kate', 'katherine', 'kathleen', 'kathryn', 'kathy', 'katie',
    'kelly', 'kim', 'kimberly', 'kristen', 'kristin', 'laura', 'lauren', 'leslie',
    'lily', 'linda', 'lisa', 'liz', 'lori', 'lucy', 'lynn', 'margaret', 'maria',
    'marie', 'marilyn', 'martha', 'mary', 'megan', 'melanie', 'melissa', 'michelle',
    'monica', 'nancy', 'natalie', 'nicole', 'pam', 'pamela', 'patricia', 'paula',
    'penny', 'rachel', 'rebecca', 'robin', 'ruth', 'sally', 'samantha', 'sandy',
    'sarah', 'sharon', 'shirley', 'stacy', 'stephanie', 'sue', 'susan', 'tammy',
    'teresa', 'tiffany', 'tracy', 'valerie', 'virginia', 'wendy',
    'serina', 'gøril', 'mai', 'eir', 'katja', 'amalia', 'ingjerd', 'linnéa',
    'zuzanna', 'annette', 'barbro', 'maj', 'vilje', 'catharina', 'borghild',
    'telma', 'vida', 'saga', 'sølvi', 'jasmin', 'vivian', 'joanna', 'ingerid',
    'alina', 'moa', 'lerke', 'ava', 'maud', 'kira', 'zofia', 'lilli', 'aleksandra',
    'claudia', 'molly', 'sol', 'elle', 'siril', 'emelie', 'isa', 'sine', 'målfrid',
    'marthine', 'wiktoria', 'anastasia', 'marlen', 'angelina', 'cathrin', 'ariel',
    'anny', 'ramona', 'beatrice', 'matilda', 'connie', 'jasmine', 'lana', 'emmeli',
    'thyra', 'edda', 'sofiia', 'daniella', 'janicke', 'evy', 'olina', 'tamara',
    'amelie', 'kari-anne', 'weronika', 'tilla', 'josefin', 'alba', 'karete',
    'christiane', 'hild', 'ayan', 'nikola', 'åste', 'annelin', 'eiril', 'constance',
    'annbjørg', 'carine', 'birte', 'betina', 'åsta', 'karolina', 'kaya', 'seline',
    'thilde', 'noor', 'silja', 'mila', 'lin', 'jannike', 'gabrielle', 'ingelin',
    'liza', 'daria', 'gunvor', 'kathrin', 'margareth', 'gyda', 'rebecka', 'alette',
    'venke', 'niri', 'fryd', 'martyna', 'karna', 'judit', 'madelene', 'audhild',
    'kateryna', 'aili', 'ragne', 'loubna', 'sigri', 'tilda', 'susann', 'nila',
    'enya', 'carolina', 'kiara', 'nele', 'ellisiv', 'nadja', 'ranveig', 'elea',
    'gabriela', 'viviana', 'karmen', 'tia', 'emmeline', 'annabel', 'edvarda',
    'amira', 'emmy', 'aida', 'aya', 'ariana', 'sabrina', 'an-magritt', 'marian',
    'eirun', 'marthea', 'inez', 'madeline', 'thomine', 'bjørk', 'anastasija',
    'noa', 'abelone', 'mariel', 'tilje', 'heidrun', 'natalia', 'asma', 'safiya',
    'rannei', 'iren', 'alisa', 'kathinka', 'jessie', 'eirill', 'benita', 'frid',
    'anne-marit', 'mailen', 'tori', 'karine', 'katrin', 'birgitta', 'turi',
    'melina', 'yvonne', 'mirjam', 'tracie',
    'nikita', 'nadine', 'adina', 'kiran', 'cristina', 'elna', 'justine', 'betzy',
    'adrianne', 'fia', 'cordelia', 'kevine', 'marie-louise', 'michaela', 'marija',
    'silke', 'gabi', 'adriana', 'ida-marie', 'mollie', 'freyja', 'viktoriya',
    'vienna', 'hazel', 'janna', 'juliette', 'elimine', 'vibecke', 'jovnna',
    'rugile', 'bethine', 'viktorija', 'martina', 'othelie', 'evina', 'hilda',
    'nikol', 'melat', 'arja', 'rowan', 'lucie', 'kamille', 'anne-line', 'amilie',
    'anne-marie', 'milda', 'linde', 'darina', 'eminda', 'zoe', 'heike', 'mar',
    'arsema', 'irina', 'anne-marthe', 'emina', 'rylee', 'franziska', 'amber',
    'salma', 'joana', 'chika', 'stine-marie', 'jonette', 'saskia', 'anne-marte',
    'bethina', 'torun', 'gørill', 'larissa', 'birthe', 'else-mari', 'cesilie',
    'renée', 'øyvor', 'maila', 'emely', 'yeva', 'izabell', 'matea', 'pil',
    'katarzyna', 'freya', 'elma', 'ingvil', 'vikka', 'solvår', 'ann-kristin',
    'kristianne', 'lovisa', 'fatou', 'kathe', 'petrine', 'trine-lise', 'katia',
    'lilje', 'ea', 'asta', 'ewa', 'sabina', 'janniche', 'tabarak', 'doris',
    'agate', 'dyveke', 'inessa', 'gitte', 'kylie', 'mimmi', 'hodan', 'miski',
    'nuchsaba', 'aurelia', 'hejin', 'adine', 'torborg', 'elsie', 'gabriele',
    'clementina', 'esma', 'meron', 'alaa', 'hiba', 'lillie', 'sjasmin', 'sonia',
    'shamsa', 'lejla', 'olianne', 'evita', 'asllat', 'roowayda', 'christin',
    'mimi', 'rut', 'rubi', 'gine', 'thorhild', 'aasne', 'mari-ann', 'cathy',
    'maryon', 'tai', 'minna', 'irmelin', 'torgunn', 'margunn', 'anne-kristine',
    'giske', 'sirianne', 'kjerstin', 'margret', 'ann-elisabeth', 'norunn',
    'katharina', 'davina', 'enja', 'ranja', 'malou', 'anika', 'synneva', 'ailin',
    'vilma', 'theresa', 'arina', 'kitty', 'frøy', 'taran', 'jette', 'caitlin',
    'elisabet', 'maaike', 'leandra', 'safa', 'fatime', 'felina', 'fannie',
    'anisa', 'annveig', 'jeanett', 'kaija', 'birgithe', 'julianna', 'abigail',
    'eilen', 'tessa', 'mari-anne', 'maija', 'ann-irene', 'belinda', 'eleonora',
    'kesia', 'casandra', 'emelia', 'berthe', 'thalia', 'susana', 'regina',
    'miranda', 'famke', 'amilde', 'kethlin', 'olive', 'zara', 'ruby', 'renata',
    'kinga', 'anbjørg', 'sienna', 'tiri', 'lill', 'norma'
}


def get_authoritative_events():
    """Hent øvelser som definitivt indikerer kjønn

    VIKTIG: Kun øvelser som er 100% kjønnsspesifikke:
    - 110 meter hekk: KUN menn (damer løper 100m hekk)
    - 10-kamp: KUN menn (utendørs)
    - Kule 5kg+: KUN menn
    - Diskos 1.5kg+: KUN menn
    - Spyd 700g+: KUN menn
    - Slegge over 4kg: KUN menn
    - Hekker over 100cm: KUN menn
    """
    import re
    events = supabase.table('events').select('id, name').execute()

    male_events = []
    female_events = []

    for e in events.data:
        name = e['name'].lower()
        original_name = e['name']

        # Herreøvelser - kun 100% sikre
        if '110 meter hekk' in name or '110m hekk' in name:
            male_events.append(e['id'])
        elif name == '10-kamp':
            male_events.append(e['id'])

        # Kule 5kg eller tyngre (5.0, 6.0, 7.26 kg)
        elif 'kule' in name:
            match = re.search(r'(\d+[,.]?\d*)\s*kg', name)
            if match:
                weight = float(match.group(1).replace(',', '.'))
                if weight >= 5.0:
                    male_events.append(e['id'])

        # Diskos 1.5kg eller tyngre (1.5, 1.75, 2.0 kg)
        elif 'diskos' in name:
            match = re.search(r'(\d+[,.]?\d*)\s*kg', name)
            if match:
                weight = float(match.group(1).replace(',', '.'))
                if weight >= 1.5:
                    male_events.append(e['id'])

        # Spyd 700g eller tyngre (700g, 800g)
        elif 'spyd' in name:
            match = re.search(r'(\d+)\s*g', name)
            if match:
                weight = int(match.group(1))
                if weight >= 700:
                    male_events.append(e['id'])

        # Slegge over 4kg (5.0, 6.0, 7.26 kg)
        elif 'slegge' in name:
            match = re.search(r'(\d+[,.]?\d*)\s*kg', name)
            if match:
                weight = float(match.group(1).replace(',', '.'))
                if weight > 4.0:
                    male_events.append(e['id'])

        # Hekker over 100cm (100cm, 106.7cm)
        elif 'hekk' in name or 'hinder' in name:
            match = re.search(r'(\d+[,.]?\d*)\s*cm', name)
            if match:
                height = float(match.group(1).replace(',', '.'))
                if height > 100:
                    male_events.append(e['id'])

        # Ingen dameøvelser er 100% sikre uten kontekst

    return male_events, female_events


def get_athletes_with_authoritative_events(male_events, female_events):
    """Finn utøvere som har resultater i autoritative øvelser"""
    male_athletes = set()
    female_athletes = set()

    for event_id in male_events:
        results = supabase.table('results').select('athlete_id').eq('event_id', event_id).execute()
        for r in results.data:
            male_athletes.add(r['athlete_id'])

    for event_id in female_events:
        results = supabase.table('results').select('athlete_id').eq('event_id', event_id).execute()
        for r in results.data:
            female_athletes.add(r['athlete_id'])

    return male_athletes, female_athletes


def get_first_name(full_name):
    """Hent fornavn fra fullt navn"""
    if not full_name:
        return None
    parts = full_name.strip().split()
    if parts:
        return parts[0].lower()
    return None


def main():
    print("=" * 70, flush=True)
    print("KOMPLETT KJØNNSFIKSING", flush=True)
    print("=" * 70, flush=True)
    print(flush=True)

    # ========================================
    # STEG 1: Hent autoritative øvelser
    # ========================================
    print("Steg 1: Henter autoritative øvelser...", flush=True)
    male_events, female_events = get_authoritative_events()
    print(f"  Herreøvelser: {len(male_events)}", flush=True)
    print(f"  Dameøvelser: {len(female_events)}", flush=True)

    # ========================================
    # STEG 2: Finn utøvere med autoritative øvelser
    # ========================================
    print(flush=True)
    print("Steg 2: Finner utøvere med autoritative øvelser...", flush=True)
    auth_male, auth_female = get_athletes_with_authoritative_events(male_events, female_events)
    print(f"  Utøvere med herreøvelser: {len(auth_male)}", flush=True)
    print(f"  Utøvere med dameøvelser: {len(auth_female)}", flush=True)

    # Fjern konflikter
    conflicts = auth_male & auth_female
    auth_male = auth_male - conflicts
    auth_female = auth_female - conflicts
    print(f"  Konflikter (ignorert): {len(conflicts)}", flush=True)

    # ========================================
    # STEG 3: Reset kjønn for utøvere UTEN autoritative øvelser
    # ========================================
    print(flush=True)
    print("Steg 3: Resetter kjønn for utøvere uten autoritative øvelser...", flush=True)

    # Hent alle utøver-IDer
    all_athletes = []
    offset = 0
    while True:
        result = supabase.table('athletes').select('id').range(offset, offset + 999).execute()
        if not result.data:
            break
        all_athletes.extend([a['id'] for a in result.data])
        if len(result.data) < 1000:
            break
        offset += 1000

    # Finn de som IKKE har autoritative øvelser
    authoritative_athletes = auth_male | auth_female
    non_authoritative = [a for a in all_athletes if a not in authoritative_athletes]

    print(f"  Totalt utøvere: {len(all_athletes)}", flush=True)
    print(f"  Med autoritative øvelser: {len(authoritative_athletes)}", flush=True)
    print(f"  Uten autoritative øvelser: {len(non_authoritative)}", flush=True)

    # Reset disse til NULL
    batch_size = 100
    reset_count = 0
    for i in range(0, len(non_authoritative), batch_size):
        batch = non_authoritative[i:i + batch_size]
        supabase.table('athletes').update({'gender': None}).in_('id', batch).execute()
        reset_count += len(batch)
        if reset_count % 5000 == 0:
            print(f"    Reset {reset_count}...", flush=True)

    print(f"  Reset: {reset_count} utøvere", flush=True)

    # ========================================
    # STEG 4: Sett kjønn basert på autoritative øvelser
    # ========================================
    print(flush=True)
    print("Steg 4: Setter kjønn basert på autoritative øvelser...", flush=True)

    # Oppdater menn
    male_list = list(auth_male)
    for i in range(0, len(male_list), batch_size):
        batch = male_list[i:i + batch_size]
        supabase.table('athletes').update({'gender': 'M'}).in_('id', batch).execute()
    print(f"  Satt til M: {len(male_list)}", flush=True)

    # Oppdater kvinner
    female_list = list(auth_female)
    for i in range(0, len(female_list), batch_size):
        batch = female_list[i:i + batch_size]
        supabase.table('athletes').update({'gender': 'F'}).in_('id', batch).execute()
    print(f"  Satt til F: {len(female_list)}", flush=True)

    # ========================================
    # STEG 5: Sett kjønn basert på fornavn
    # ========================================
    print(flush=True)
    print("Steg 5: Setter kjønn basert på fornavn...", flush=True)

    # Hent utøvere med NULL kjønn
    null_gender = []
    offset = 0
    while True:
        result = supabase.table('athletes').select(
            'id, first_name, full_name'
        ).is_('gender', 'null').range(offset, offset + 999).execute()
        if not result.data:
            break
        null_gender.extend(result.data)
        if len(result.data) < 1000:
            break
        offset += 1000

    print(f"  Utøvere med NULL kjønn: {len(null_gender)}", flush=True)

    to_male = []
    to_female = []
    unmatched = []

    for a in null_gender:
        first_name = a.get('first_name', '').lower() if a.get('first_name') else None
        if not first_name:
            first_name = get_first_name(a.get('full_name', ''))

        if not first_name:
            unmatched.append(a['id'])
            continue

        if first_name in MALE_NAMES:
            to_male.append(a['id'])
        elif first_name in FEMALE_NAMES:
            to_female.append(a['id'])
        else:
            unmatched.append(a['id'])

    print(f"  Mannsnavn funnet: {len(to_male)}", flush=True)
    print(f"  Kvinnenavn funnet: {len(to_female)}", flush=True)
    print(f"  Ukjente navn: {len(unmatched)}", flush=True)

    # Oppdater
    for i in range(0, len(to_male), batch_size):
        batch = to_male[i:i + batch_size]
        supabase.table('athletes').update({'gender': 'M'}).in_('id', batch).execute()

    for i in range(0, len(to_female), batch_size):
        batch = to_female[i:i + batch_size]
        supabase.table('athletes').update({'gender': 'F'}).in_('id', batch).execute()

    print(f"  Oppdatert til M: {len(to_male)}", flush=True)
    print(f"  Oppdatert til F: {len(to_female)}", flush=True)

    # ========================================
    # OPPSUMMERING
    # ========================================
    print(flush=True)
    print("=" * 70, flush=True)
    print("FERDIG!", flush=True)
    print("=" * 70, flush=True)

    # Tell opp
    result = supabase.table('athletes').select('gender').execute()
    counts = defaultdict(int)
    for a in result.data:
        counts[a['gender']] += 1

    print(f"  Menn (M): {counts['M']}", flush=True)
    print(f"  Kvinner (F): {counts['F']}", flush=True)
    print(f"  Ukjent (NULL): {counts[None]}", flush=True)
    print("=" * 70, flush=True)


if __name__ == '__main__':
    main()
