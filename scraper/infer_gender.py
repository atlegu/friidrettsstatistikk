"""
Infer gender from Norwegian first names and update athletes table.
"""

import os
from dotenv import load_dotenv
from supabase import create_client
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Common Norwegian male names (and international names common in Norway)
MALE_NAMES = {
    # Traditional Norwegian
    'ole', 'lars', 'per', 'jan', 'erik', 'kjell', 'arne', 'bjørn', 'odd', 'svein',
    'knut', 'tor', 'geir', 'terje', 'jon', 'morten', 'hans', 'rune', 'trond', 'stein',
    'yngve', 'øystein', 'øyvind', 'asbjørn', 'einar', 'ivar', 'leif', 'ragnar', 'sigurd', 'torbjørn',
    'harald', 'olav', 'petter', 'magnus', 'henrik', 'andreas', 'martin', 'thomas', 'anders', 'christian',
    'kristian', 'johan', 'johannes', 'jakob', 'nicolai', 'nikolai', 'alexander', 'fredrik', 'daniel', 'markus',
    'marcus', 'tobias', 'jonas', 'sander', 'mathias', 'mattias', 'emil', 'adrian', 'sebastian', 'oliver',
    'william', 'noah', 'lucas', 'luca', 'isak', 'isaac', 'jakob', 'oskar', 'oscar', 'filip',
    'philip', 'elias', 'theodor', 'aksel', 'axel', 'herman', 'felix', 'victor', 'viktor', 'ludvig',
    'ludvik', 'august', 'alfred', 'mikkel', 'mikael', 'michael', 'gabriel', 'rafael', 'david', 'simon',
    'simen', 'stian', 'vegard', 'håkon', 'haakon', 'erlend', 'espen', 'frode', 'gard', 'gaute',
    'gunnar', 'gustaf', 'gustav', 'halvor', 'helge', 'henning', 'jarle', 'jens', 'joakim', 'joachim',
    'jørgen', 'jørn', 'kai', 'karl', 'kasper', 'kenneth', 'kim', 'klaus', 'kristoffer', 'christopher',
    'dag', 'edvard', 'edward', 'egil', 'eirik', 'even', 'finn', 'frank', 'glenn', 'guttorm',
    'pål', 'paul', 'robert', 'robin', 'roar', 'roy', 'ruben', 'sindre', 'snorre', 'sondre',
    'steffen', 'stefan', 'sverre', 'tarjei', 'vetle', 'vidar', 'vincent', 'atle', 'bård', 'børge',
    'carl', 'casper', 'christoffer', 'cato', 'conrad', 'conrad', 'dennis', 'didrik', 'eivind',
    'erling', 'eskil', 'eystein', 'fabian', 'ferdinand', 'gjermund', 'gjert', 'gregor', 'gregers',
    'hallvard', 'håvard', 'ingvar', 'iver', 'ivo', 'jostein', 'kjetil', 'kolbjørn', 'konrad',
    'kristján', 'krister', 'kurt', 'lauritz', 'lorents', 'magne', 'mathis', 'mats', 'max',
    'nils', 'njål', 'normann', 'olaf', 'odin', 'orm', 'ola', 'otto', 'patrik', 'patrick',
    'preben', 'raymond', 'reidar', 'richard', 'rolf', 'ronald', 'samuel', 'sigbjørn', 'sigmund',
    'sigve', 'sivert', 'sjur', 'skjalg', 'ståle', 'sturla', 'stig', 'tage', 'tallak', 'tore',
    'torgeir', 'tormod', 'torstein', 'trygve', 'ulf', 'ulrik', 'valentin', 'vebjørn', 'vegar',
    'werner', 'wilfred', 'wilhelm', 'yan', 'yngvar', 'ørnulf', 'øyvin', 'åge', 'ådne',
    'imran', 'mohamed', 'mohammed', 'ali', 'ahmed', 'hassan', 'ibrahim', 'omar', 'yosef', 'josef',
    'benjamin', 'jonathan', 'kevin', 'brian', 'jason', 'justin', 'brandon', 'ryan', 'kyle', 'tyler',
    'leo', 'liam', 'hugo', 'theo', 'henry', 'jack', 'james', 'john', 'luke', 'matthew',
    'nataniel', 'nathaniel', 'peter', 'phillip', 'sam', 'tom', 'tommy', 'tony', 'trym',
    'heine', 'ailo', 'brede', 'birk', 'bo', 'edvin', 'eldar', 'embrik', 'falk', 'fillip',
    'gjermund', 'hågen', 'isac', 'jesper', 'jone', 'kato', 'lasse', 'leander', 'lorentz', 'lorenz',
    'mads', 'nicolay', 'narve', 'olve', 'olle', 'orre', 'peder', 'rasmus', 'sigvart', 'sigvald',
    'sølve', 'tallak', 'teodor', 'tidemann', 'tomas', 'toralf', 'torben', 'torger', 'torleif',
    'ulv', 'varg', 'viljar', 'willian', 'yonas', 'ørjan', 'ørn', 'øystein', 'åsmund',
    # Additional common male names found in the data
    'adam', 'albert', 'aleksander', 'aleksandr', 'alexis', 'alf', 'andre', 'andrei', 'andrew',
    'andré', 'anker', 'anthony', 'anton', 'are', 'arild', 'arnfinn', 'arnt', 'aron', 'arthur',
    'arve', 'arvid', 'ask', 'asle', 'audun', 'bastian', 'bendik', 'bjarnar', 'bjarne', 'bjarte',
    'bjørnar', 'brage', 'bror', 'brynjar', 'børre', 'cassius', 'christoph', 'dani', 'dario',
    'dejan', 'dominic', 'dominik', 'donovan', 'dylan', 'edmund', 'eide', 'eik', 'eilev', 'einar',
    'einride', 'elling', 'elliot', 'elmer', 'elon', 'elvis', 'enok', 'enzo', 'eric', 'ernest',
    'ernst', 'eugen', 'evan', 'fillipp', 'flemming', 'florian', 'folke', 'freddy', 'frederic',
    'frikk', 'frithjof', 'georg', 'gisle', 'glenn', 'godwin', 'gordon', 'gøran', 'hafiz', 'hagen',
    'hakon', 'halvdan', 'hamza', 'hasan', 'havard', 'helmer', 'hermann', 'hilmar', 'hovedn',
    'ian', 'ibrahim', 'igor', 'ilja', 'inge', 'ingebrigt', 'ismail', 'ivan', 'jack', 'jacob',
    'jarl', 'jayden', 'jean', 'jermund', 'jimmy', 'jo', 'joacim', 'job', 'joel', 'john', 'johnny',
    'jonah', 'jonar', 'jonas', 'jonn', 'joris', 'jose', 'joseph', 'julian', 'julius', 'jørund',
    'karim', 'karsten', 'khalid', 'kiran', 'klaus', 'kristen', 'kyrre', 'lander', 'landon',
    'lars-erik', 'laurits', 'laurtiz', 'lavrans', 'leon', 'leonard', 'logan', 'loke', 'lucas',
    'lukas', 'magne', 'malik', 'marcel', 'marco', 'marian', 'mario', 'mark', 'marko', 'marlo',
    'marius', 'martin', 'matheo', 'matteo', 'matteus', 'maurice', 'maximilian', 'melvin', 'milian',
    'milo', 'mirza', 'mo', 'moritz', 'morten', 'muhammad', 'natanel', 'nathan', 'nicholas',
    'nick', 'niclas', 'niklas', 'noel', 'noah', 'noralf', 'norman', 'ole-martin', 'oliver',
    'omer', 'orion', 'orjan', 'osmund', 'otto', 'pascal', 'pawel', 'pelle', 'per-erik', 'philip',
    'pierre', 'rafael', 'ragnar', 'rami', 'range', 'raphael', 'rico', 'rikard', 'rocky', 'roger',
    'roland', 'rolf', 'romar', 'ronaldo', 'ronny', 'runar', 'sander', 'sasha', 'savio', 'scott',
    'selmer', 'semir', 'severin', 'sigve', 'silas', 'simeon', 'sixten', 'siver', 'sjur', 'sol',
    'stein-erik', 'steinar', 'sture', 'svein-erik', 'syver', 'søren', 'teodor', 'terrance',
    'theodore', 'thomas', 'thoralf', 'thorbjørn', 'thorvald', 'tim', 'timothy', 'tobben', 'todd',
    'tollef', 'tollev', 'tord', 'torgrim', 'torjus', 'torkil', 'torkjell', 'torleiv', 'tov',
    'tristan', 'troy', 'truls', 'ture', 'ty', 'ulrich', 'urban', 'vegard', 'vigleik', 'viggo',
    'vilhelm', 'vilmar', 'vincent', 'walter', 'wiktor', 'willy', 'wilson', 'william', 'xavier',
    'yasin', 'yasser', 'yusuf', 'zakaria', 'zander', 'øistein', 'øivind', 'ørjan', 'ørnulv',
    # Additional names from database review
    'abdalla', 'abdullahi', 'abhyudhay', 'abraham', 'adil', 'adrean', 'aiden', 'ajibola', 'alan',
    'albin', 'aldric', 'anders-johan', 'ånung', 'ariand', 'arkadiusz', 'awet', 'bakr', 'bereket',
    'callum', 'carl-wilhelm', 'carlo', 'casey', 'caspian', 'charles', 'chinua', 'chrisander',
    'christer', 'dagfinn', 'danel', 'darin', 'david-thierry', 'diego', 'dyre', 'edem', 'eilif',
    'elijah', 'eljar', 'emanuel', 'emanuels', 'emiliano', 'endre', 'enrico', 'erikas', 'eskild',
    'ethan', 'eurico', 'filippo', 'filmon', 'finn-obert', 'florient', 'floris', 'francisco',
    'frans', 'franz', 'frederik', 'gagan', 'graham', 'grzegorz', 'hagbart', 'halfdan-emil',
    'hans-joachim', 'hans-magnus', 'hans-olav', 'harry', 'hauk', 'hayato', 'hayden', 'hector',
    'heljar', 'hjalmar', 'idar', 'ilian', 'ilunga', 'ingar', 'ingve', 'ishaan', 'jacek',
    'jan-olav', 'jan-trygve', 'janis', 'jaroslaw', 'jens-kristian', 'jeremiah', 'joar', 'johann',
    'john-rune', 'johnson', 'jon-anders', 'jon-henning', 'jon-magnus', 'jon-marius', 'jon-vidar',
    'jonatan', 'jonny', 'jøran', 'josé', 'josep', 'joseph-justus', 'josh', 'joshua', 'julio',
    'kåre', 'karl-henrik', 'karol', 'kashif', 'kebron', 'ken', 'kenny', 'kim-roger', 'kirill',
    'kjartan', 'kornelius', 'kyryl', 'lars-kristian', 'lars-martin', 'lars-olav', 'leander-johannes',
    'leandro', 'leif-andreas', 'leighton', 'leiv', 'leonardo', 'leonid', 'leul', 'levi', 'lewis',
    'linus', 'logman', 'luc', 'luka', 'lutz', 'magnus-johan', 'marchus', 'marcin', 'marino',
    'marthon', 'martinus', 'matas', 'mateusz', 'matheus', 'matias', 'mattis', 'michal', 'mickey',
    'mikail', 'mikal', 'mohammad', 'mons', 'morthen', 'mugis', 'mustafa', 'myron', 'nahom',
    'nazar', 'nicklas', 'nicolas', 'nikhilkanth', 'nikkolaj', 'nilas', 'nouri', 'oddne',
    'ol-duommá', 'olai', 'olaus', 'ole-andreas', 'ole-erich', 'ole-jørgen', 'ole-kristian',
    'oleksandr', 'olliver', 'osama', 'ottar', 'ove', 'paal', 'paul-louis', 'pavlo',
    'per-christian', 'per-einar', 'piera', 'radoslaw', 'reinert', 'rene', 'rené', 'rhys', 'rick',
    'rolv-jørgen', 'roy-arne', 'ruairi', 'sacarias', 'salum', 'san', 'senay', 'sergejs', 'siem',
    'soban', 'sofian', 'sten', 'steven', 'stian-mikael', 'storm', 'sveinung', 'sven', 'sven-are',
    'svend', 'svenn', 'tedros', 'teklu', 'tellef', 'thimon', 'thor', 'tobi', 'tom-rune', 'tomack',
    'tor-aanen', 'tor-henning', 'tor-inge', 'torfinn', 'torje', 'torkel', 'tov-christian', 'tron',
    'tshishimbi', 'vadim', 'vilmer', 'vinjar', 'waldemar', 'weldu', 'widar', 'william-andre',
    'wilmer', 'yevhenii', 'yoann', 'zion',
}

# Common Norwegian female names
FEMALE_NAMES = {
    # Traditional Norwegian
    'anne', 'anna', 'ingrid', 'kari', 'marit', 'liv', 'bjørg', 'randi', 'solveig', 'gerd',
    'astrid', 'berit', 'eva', 'inger', 'kirsten', 'kristin', 'ellen', 'hanne', 'hilde', 'tone',
    'silje', 'ida', 'maria', 'marie', 'maja', 'maia', 'emma', 'sara', 'nora', 'emilie',
    'sofie', 'sophie', 'thea', 'julie', 'andrea', 'camilla', 'cecilie', 'elisabeth', 'elizabeth',
    'line', 'lene', 'lise', 'lisa', 'mette', 'monica', 'monika', 'nina', 'rita', 'ruth',
    'sigrid', 'siri', 'stine', 'susanne', 'trine', 'turid', 'vibeke', 'wenche', 'yvonne',
    'amalie', 'aurora', 'celine', 'charlotte', 'clara', 'klara', 'elise', 'ella', 'emily',
    'frida', 'hedda', 'hedvig', 'helene', 'helena', 'henriette', 'ina', 'ingeborg', 'jenny',
    'johanne', 'josefine', 'karoline', 'caroline', 'katrine', 'kathrine', 'katherine', 'lea',
    'leah', 'linnea', 'linn', 'linda', 'lovise', 'louise', 'madeleine', 'magdalena', 'margit',
    'maren', 'margrethe', 'marthe', 'martha', 'martine', 'mathilde', 'matilde', 'mia', 'mina',
    'natalie', 'nathalie', 'olivia', 'petra', 'rebecca', 'rebekka', 'ragnhild', 'renate',
    'sandra', 'selma', 'sissel', 'synne', 'synnøve', 'tiril', 'tonje', 'torill', 'trude',
    'una', 'unni', 'vilde', 'victoria', 'viktoria', 'veronika', 'veronica', 'åse', 'åshild',
    'aleksandra', 'alexandra', 'ane', 'anette', 'anita', 'ann', 'anja', 'benedicte', 'benedichte',
    'birgit', 'bodil', 'britt', 'brit', 'cathrine', 'christina', 'christine', 'connie', 'dagny',
    'diana', 'dina', 'dorthe', 'eline', 'eli', 'elin', 'elina', 'erica', 'erika', 'erna',
    'esther', 'ester', 'fride', 'gina', 'grete', 'grethe', 'gro', 'gunn', 'guri', 'gyda',
    'hanna', 'hannah', 'heidi', 'hildegunn', 'iben', 'idunn', 'irmelin', 'isabel', 'isabell',
    'janne', 'jannike', 'jennifer', 'jorunn', 'kaia', 'karen', 'katarina', 'katharina', 'kine',
    'kristina', 'laila', 'laura', 'laurine', 'lena', 'lillian', 'lilly', 'lotta', 'lucia',
    'lucy', 'madelene', 'magda', 'maiken', 'malin', 'malene', 'margareth', 'marianne', 'merete',
    'michelle', 'mille', 'miriam', 'nanna', 'nicole', 'oda', 'olaug', 'paula', 'pauline',
    'pia', 'rachel', 'ragna', 'regine', 'ronja', 'rose', 'saga', 'sanna', 'sarah', 'sienna',
    'sigrun', 'silva', 'siv', 'sonja', 'stefanie', 'stephanie', 'stella', 'svanhild', 'tanja',
    'tea', 'teresa', 'terese', 'therese', 'tina', 'tora', 'torhild', 'torild', 'tuva',
    'ulrikke', 'valentine', 'valerie', 'vanessa', 'vera', 'veslemøy', 'vigdis', 'ylva',
    'fatima', 'aisha', 'ayesha', 'mariam', 'amina', 'khadija', 'layla', 'leyla', 'nadia', 'yasmin', 'moa',
    'jasmine', 'jessica', 'amanda', 'ashley', 'brittany', 'crystal', 'danielle', 'heather',
    'jennifer', 'jessica', 'kelly', 'kimberly', 'lauren', 'megan', 'melissa', 'michelle',
    'nicole', 'samantha', 'stephanie', 'tiffany', 'vanessa', 'amy', 'alice', 'chloe', 'grace',
    'hannah', 'isabelle', 'ivy', 'lily', 'lucy', 'megan', 'molly', 'ruby', 'zoe',
}

# Name endings that strongly indicate gender
MALE_ENDINGS = ('ulf', 'var', 'vin', 'vind', 'stein', 'bjørn', 'geir', 'mund', 'ard', 'ald')
FEMALE_ENDINGS = ('hild', 'borg', 'bjørg', 'rid', 'gunn', 'unn', 'dis', 'run', 'frid', 'ine', 'ette')


def infer_gender(first_name: str) -> str | None:
    """
    Infer gender from Norwegian first name.
    Returns 'M', 'K', or None if uncertain.
    """
    if not first_name:
        return None

    name = first_name.lower().strip()

    # Direct lookup
    if name in MALE_NAMES:
        return 'M'
    if name in FEMALE_NAMES:
        return 'F'

    # Check endings
    for ending in MALE_ENDINGS:
        if name.endswith(ending):
            return 'M'
    for ending in FEMALE_ENDINGS:
        if name.endswith(ending):
            return 'F'

    # Common patterns
    # Names ending in -a are often female (but not always in Norwegian)
    # Names ending in -e can be either

    return None


def update_athlete_genders():
    """Fetch all athletes and update their gender based on first name."""

    # Fetch all athletes without gender
    logger.info("Fetching athletes without gender...")

    all_athletes = []
    offset = 0
    batch_size = 1000

    while True:
        resp = supabase.table('athletes').select('id, first_name, gender').is_('gender', 'null').range(offset, offset + batch_size - 1).execute()
        all_athletes.extend(resp.data)
        logger.info(f"Fetched {len(all_athletes)} athletes so far...")
        if len(resp.data) < batch_size:
            break
        offset += batch_size

    logger.info(f"Total athletes without gender: {len(all_athletes)}")

    # Infer gender for each
    updates = {'M': [], 'F': [], 'unknown': []}

    for athlete in all_athletes:
        gender = infer_gender(athlete['first_name'])
        if gender:
            updates[gender].append(athlete['id'])
        else:
            updates['unknown'].append((athlete['id'], athlete['first_name']))

    logger.info(f"Inferred: {len(updates['M'])} menn, {len(updates['F'])} kvinner, {len(updates['unknown'])} ukjent")

    # Update males
    if updates['M']:
        logger.info(f"Updating {len(updates['M'])} male athletes...")
        batch_size = 100
        for i in range(0, len(updates['M']), batch_size):
            batch = updates['M'][i:i+batch_size]
            supabase.table('athletes').update({'gender': 'M'}).in_('id', batch).execute()

    # Update females
    if updates['F']:
        logger.info(f"Updating {len(updates['F'])} female athletes...")
        batch_size = 100
        for i in range(0, len(updates['F']), batch_size):
            batch = updates['F'][i:i+batch_size]
            supabase.table('athletes').update({'gender': 'F'}).in_('id', batch).execute()

    # Log unknown names for manual review
    if updates['unknown']:
        logger.info(f"\nUkjente navn ({len(updates['unknown'])}):")
        unknown_names = set(name for _, name in updates['unknown'])
        for name in sorted(unknown_names)[:50]:
            logger.info(f"  - {name}")
        if len(unknown_names) > 50:
            logger.info(f"  ... og {len(unknown_names) - 50} flere")

    logger.info("Done!")


if __name__ == '__main__':
    update_athlete_genders()
