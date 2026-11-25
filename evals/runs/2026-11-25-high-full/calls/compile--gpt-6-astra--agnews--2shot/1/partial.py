import re
import unicodedata


_CATEGORIES = ("world", "business", "sports", "sci_tech")


def _words(text):
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"<[^>]*>", " ", text)
    for old, new in (
        ("&amp;", " and "), ("&quot;", " "), ("&#39;", "'"),
        ("&apos;", "'"), ("&nbsp;", " "), ("&lt;", " "),
        ("&gt;", " "), ("’", "'"), ("`", "'"),
    ):
        text = text.replace(old, new)
    text = re.sub(r"\b(?:[a-z]\.){2,}", lambda m: m.group(0).replace(".", ""), text)
    text = re.sub(r"\bu\.s\b", "us", text)
    text = re.sub(r"\bu\.k\b", "uk", text)
    text = re.sub(r"\bu\.n\b", "un", text)
    text = re.sub(r"\be[\s-]?mail\b", "email", text)
    text = re.sub(r"\b([a-z0-9]+)'s\b", r"\1", text)
    text = text.replace("&", " and ")
    return tuple(re.findall(r"[a-z0-9]+", text))


def _phrase_set(data):
    return {p for p in (_words(s.strip()) for s in data.split("|")) if p}


_FEATURES = {}


def _add(category, weight, data):
    for phrase in _phrase_set(data):
        weights = _FEATURES.setdefault(phrase, {})
        weights[category] = max(weight, weights.get(category, 0.0))


# General economic and corporate reporting.
_add("business", 5.5, """
stock market|stock markets|dow jones|nasdaq composite|s&p 500|ftse 100|
nikkei index|hang seng|wall street|federal reserve|gross domestic product|
consumer price index|initial public offering|balance of trade|
trade deficit|trade surplus|interest rate cut|interest rate hike|
quarterly earnings|earnings report|profit warning|central bank|
securities and exchange commission|bank of england|european central bank
""")
_add("business", 4.2, """
stocks|equities|earnings|inflation|deflation|recession|gdp|opec|
ipo|ip os|bankruptcy|bankrupt|insolvency|insolvent|privatization|
privatisation|merger|mergers|takeover|takeovers|dividend|dividends|
shareholders|shareholder|stockholders|stockholder|nasdaq|nyse|
ftse|nikkei|dow|bull market|bear market|stock exchange|
commodity prices|oil prices|oil price|crude prices|crude oil|
housing market|housing prices|real estate|mortgage rates|
retail sales|consumer spending|economic growth|economic recovery|
economic slowdown|economic outlook|economic forecast|jobless claims|
unemployment rate|nonfarm payrolls|money supply|bond market|
foreign exchange|exchange rate|exchange rates|venture capital|
private equity|hedge fund|hedge funds|investment banking|
insider trading|accounting fraud|money laundering|credit rating|
credit ratings|financial crisis|debt crisis|budget deficit|
fiscal deficit|trade talks|free trade|trade agreement|world trade organization
""")
_add("business", 3.0, """
economy|economies|economic|economics|financial|finance|finances|
investors|investor|investment|investments|investing|shares|stock|
profits|profit|profitable|profitability|revenue|revenues|
bourse|bourses|brokerage|brokerages|broker|brokers|
banking|banker|bankers|lender|lenders|mortgage|mortgages|
acquisition|acquisitions|buyout|buyouts|bidder|bidders|
retailer|retailers|retailing|retail|wholesale|wholesaler|
currency|currencies|devaluation|devalued|treasury yields|
commodities|commodity|futures|bullion|barrel|barrels|
unemployment|jobless|payrolls|layoffs|layoff|redundancies|
outsourcing|offshoring|tariffs|tariff|exports|exporters|imports|
consumer confidence|business confidence|factory orders|
industrial output|manufacturing output|durable goods|
purchasing managers|capital spending|capital expenditure|
annual results|quarterly results|operating profit|net income|
net loss|net losses|pretax profit|pre tax profit|bottom line|
financial results|financial statements|annual report|
market capitalization|market capitalisation|market cap|
stock split|share price|share prices|share sale|share offering|
public offering|bond yields|government bonds|treasury bonds|
credit card|credit cards|credit crunch|debt restructuring|
hostile bid|hostile takeover|antitrust|anti trust|
bank account|savings account|pension fund|pension funds|
chief financial officer|chief executive officer|chief executive|
chief economist|business news|financial markets|capital markets|
business investment|balance sheet|cash flow|cash flows|
supply chain|supply chains|cost cutting|job cuts|cut jobs|
cutting jobs|cut costs|cutting costs|slash jobs|slashing jobs|
price war|price wars|fuel prices|gas prices|gasoline prices
""")
_add("business", 2.0, """
bank|banks|economist|economists|trader|traders|trading|traded|
sales|selloff|sell off|selloffs|selling|purchases|purchasing|
debt|debts|deficit|surplus|credit|credits|equity|equities|
bond|bonds|divest|divested|divestiture|liquidation|
restructuring|restructure|restructured|refinancing|
earn|earned|earning|outlook|forecast|forecasts|
quarterly|fiscal|taxation|taxes|taxpayers|subsidies|
subsidy|deregulation|commerce|commercial|consumer|consumers|
businesses|entrepreneur|entrepreneurs|entrepreneurship|
ceo|cfo|chairman|chairwoman|conglomerate|conglomerates|
corporation|corporations|corporate|corporations|
manufacturing|manufacturer|manufacturers|factory|factories|
automaker|automakers|carmaker|carmakers|airline|airlines|
insurer|insurers|insurance|reinsurer|reinsurance|
oil|petroleum|gasoline|refinery|refineries|refining|
mining|mines|miner|miners|steelmaker|steelmakers|
steel|copper|aluminum|aluminium|gold prices|gold price|
wheat|soybeans|cotton|coffee prices|palm oil|
drugmaker|drugmakers|pharmaceutical company|pharmaceutical companies|
foodmaker|brewer|brewers|brewery|breweries|distiller|
car sales|auto sales|vehicle sales|home sales|house prices|
home prices|property prices|property market|commercial property|
shopping|shopper|shoppers|supermarket|supermarkets|
department store|department stores|discount store|
franchise|franchises|franchising|business plan|business model|
union workers|labor union|labour union|labor dispute|
labour dispute|wage talks|pay dispute|industrial action|
business deal|licensing deal|distribution deal|supply agreement|
air traffic|air travel|air fares|airfares|tourism|tourist industry|
hotel chain|hotel group|cruise line|travel industry|
box office|film studio|movie studio|advertising revenue|
advertisers|advertiser|advertising industry|
bitcoin|cryptocurrency|cryptocurrencies|digital currency
""")
_add("business", 0.9, """
business|company|companies|firm|firms|industry|industries|
market|markets|dollar|dollars|euro|euros|yen|sterling|
cost|costs|price|prices|priced|pricing|expensive|
million|billion|trillion|percent|percentage|
sale|sold|sell|buy|buys|bought|purchase|deal|deals|
acquire|acquires|acquired|merge|merges|merged|
expand|expands|expanded|expansion|growth|growing|
executive|executives|management|manager|managers|
employees|employee|workforce|workers|worker|jobs|employment|
production|output|supply|demand|spending|budget|budgets|
tax|wage|wages|salary|salaries|pension|pensions|
lease|leases|leasing|rent|rents|rental|property|
ownership|owner|owners|assets|asset|liabilities|
valuation|valuations|stake|stakes|bid|bids|bidding|
contract|contracts|agreement|agreements|
regulator|regulators|regulatory|competition|competitive|
energy|fuel|gas|transport|transportation|cargo|freight|
shipping|shipments|shipment|warehouses|warehouse|
cruise|aviation|aircraft|jet|jets|airbus|boeing|
advertising|advertisement|sponsorship|brand|brands
""")

_BUSINESS_NAMES = _phrase_set("""
walmart|wal mart|wal-mart|target corp|target corporation|costco|
tesco|sainsbury|sainsbury's|asda|carrefour|aldi|lidl|
marks and spencer|marks & spencer|macy's|macys|nordstrom|sears|
kmart|j c penney|jc penney|home depot|lowe's|lowes|best buy|
gap inc|gap stores|h&m|zara|ikea|walgreens|cvs|rite aid|
procter & gamble|procter and gamble|p&g|unilever|colgate palmolive|
coca cola|coca-cola|pepsi|pepsico|nestle|kraft|danone|heinz|
kellogg|kellogg's|general mills|campbell soup|cadbury|
mcdonald's|mcdonalds|burger king|wendy's|starbucks|yum brands|
anheuser busch|inbev|heineken|diageo|sabmiller|
exxon|exxon mobil|exxonmobil|chevron|texaco|royal dutch shell|
shell oil|bp plc|bp oil|conocophillips|halliburton|
schlumberger|saudi aramco|aramco|petrobras|gazprom|
general motors|gm|ford motor|ford motors|ford|toyota|honda|
nissan|renault|volkswagen|vw|daimler|chrysler|fiat|
stellantis|bmw|mercedes benz|hyundai|kia|porsche|volvo|
ferrari shares|tesla shares|tesla earnings|
general electric|ge capital|honeywell|3m|caterpillar|
deere|john deere|alcoa|arcelor|arcelormittal|us steel|
rio tinto|bhp|bhp billiton|anglo american|glencore|
dow chemical|dupont|basf|bayer|
boeing|airbus|embraer|bombardier|lockheed martin|
northrop grumman|raytheon|bae systems|
american airlines|united airlines|delta air lines|delta airlines|
southwest airlines|continental airlines|northwest airlines|
us airways|british airways|virgin atlantic|lufthansa|
air france|klm|ryanair|easyjet|qantas|cathay pacific|
singapore airlines|emirates airlines|jetblue|
fedex|united parcel service|dhl|maersk|
marriott|hilton hotels|hilton worldwide|hyatt|
carnival corp|royal caribbean|intercontinental hotels|
goldman sachs|morgan stanley|merrill lynch|jpmorgan|
jp morgan|j p morgan|chase bank|citigroup|citibank|
bank of america|wells fargo|wachovia|lehman brothers|
bear stearns|credit suisse|ubs|deutsche bank|
barclays|hsbc|lloyds|royal bank of scotland|rbs|
santander|bnp paribas|societe generale|
american express|mastercard|visa inc|capital one|
berkshire hathaway|warren buffett|aig|allianz|axa|prudential|
metlife|allstate|state farm|munich re|swiss re|
fannie mae|freddie mac|charles schwab|blackrock|blackstone|
fidelity investments|vanguard group|carlyle group|
enron|tyco|parmalat|arthur andersen|
pfizer|merck|glaxosmithkline|gsk|astrazeneca|novartis|
roche|sanofi|eli lilly|johnson & johnson|johnson and johnson|
bristol myers squibb|abbott laboratories|amgen|
gilead sciences|moderna shares|
nike|adidas|reebok|puma shares|under armour|
lvmh|louis vuitton|gucci|hermes|burberry|ralph lauren|
walt disney|disney|time warner|news corp|news corporation|
viacom|comcast|nbc universal|universal studios|
paramount|warner bros|warner brothers|dreamworks|pixar|
sony pictures|bertelsmann|pearson plc|penguin random house|
clear channel|directv|dish network|sirius radio|xm radio|
rupert murdoch|richard branson|martha stewart|
alan greenspan|ben bernanke|jerome powell|
international monetary fund|imf|world bank|world trade organization|
wto|organization of petroleum exporting countries
""")
for _p in _BUSINESS_NAMES:
    _FEATURES.setdefault(_p, {})["business"] = 4.0


# Computing, communications, scientific work and medical research.
_add("sci_tech", 6.0, """
artificial intelligence|machine learning|deep learning|
large language model|large language models|generative ai|
quantum computing|quantum computer|quantum computers|
operating system|operating systems|computer virus|computer viruses|
computer worm|computer worms|computer security|cyber security|
cybersecurity|cyberattack|cyberattacks|cyber attack|cyber attacks|
data breach|data breaches|ransomware|malware|spyware|
space shuttle|space station|international space station|
hubble telescope|hubble space telescope|james webb|
human genome|genome sequencing|gene editing|gene therapy|
stem cell|stem cells|clinical trial|clinical trials|
medical research|scientific research|scientific discovery|
particle physics|higgs boson|gravitational waves|black hole|
black holes|dark matter|dark energy|big bang|
nobel prize in physics|nobel prize in chemistry|
nobel prize in medicine|national institutes of health|
national science foundation|european space agency|
jet propulsion laboratory|national aeronautics and space administration
""")
_add("sci_tech", 4.5, """
technology|technological|software|hardware|computing|computer|
computers|internet|broadband|wireless|telecom|telecommunications|
semiconductor|semiconductors|microprocessor|microprocessors|
processor|processors|chipmaker|chipmakers|chipset|chipsets|
smartphone|smartphones|cellphone|cellphones|cellular|
laptop|laptops|notebook computer|notebook computers|
desktop computer|desktop computers|personal computer|personal computers|
mainframe|mainframes|supercomputer|supercomputers|
datacenter|datacenters|data center|data centers|cloud computing|
web browser|web browsers|search engine|search engines|
social media|social network|social networking|instant messaging|
email|website|websites|web site|web sites|world wide web|
e commerce|ecommerce|e business|ebusiness|online search|
file sharing|peer to peer|open source|source code|
programming|programmer|programmers|algorithm|algorithms|
encryption|cryptography|cryptographic|authentication|
password|passwords|phishing|hacking|hacker|hackers|hacked|
screensaver|screensavers|keystrokes|keylogger|keyloggers|
trojan horse|trojan|botnet|botnets|firewall|firewalls|
security flaw|security flaws|security hole|security holes|
security vulnerability|security vulnerabilities|
denial of service|distributed denial of service|
antivirus|anti virus|spam|spammer|spammers|
video game|video games|videogame|videogames|
computer game|computer games|online game|online games|
gaming console|game console|gaming consoles|game consoles|
virtual reality|augmented reality|esports|e sports|
robot|robots|robotics|robotic|nanotechnology|nanotech|
biotechnology|biotech|bioengineering|
science|scientific|scientist|scientists|researcher|researchers|
astronomy|astronomer|astronomers|astrophysics|cosmology|
physicist|physicists|physics|quantum|relativity|
chemist|chemists|chemistry|biologist|biologists|biology|
geneticist|geneticists|genetics|genetic|genetically|genome|genomes|
dna|rna|chromosome|chromosomes|genomic|
neuroscience|neuroscientist|neuroscientists|
archaeology|archeology|archaeologist|archaeologists|
archeologist|archeologists|paleontology|palaeontology|
paleontologist|paleontologists|fossil|fossils|dinosaur|dinosaurs|
evolution|evolutionary|neanderthal|neanderthals|
astronaut|astronauts|cosmonaut|cosmonauts|
spacecraft|spaceship|spaceflight|spacewalk|spacewalks|
orbiter|orbiters|orbital|orbit|orbits|
exoplanet|exoplanets|supernova|supernovae|
asteroid|asteroids|comet|comets|meteorite|meteorites|
telescope|telescopes|observatory|observatories|
vaccine|vaccines|vaccination|immunotherapy|
alzheimer|alzheimer's|parkinson|parkinson's|
diabetes|cancer research|cancer treatment|
gene|genes|cloning|cloned|clone|clones|
cern|nasa|esa|seti|caltech
""")
_add("sci_tech", 3.0, """
research|researching|studies|study|experiment|experiments|
experimental|laboratory|laboratories|lab|labs|
discovery|discoveries|discover|discovers|discovered|
breakthrough|breakthroughs|innovation|innovations|
invention|inventions|inventor|inventors|invented|
engineer|engineers|engineering|technologies|
pc|pcs|cpu|cpus|gpu|gpus|chip|chips|
circuit|circuits|circuitry|transistor|transistors|
memory chip|memory chips|flash memory|hard drive|hard drives|
disk drive|disk drives|disk|disks|dvd|dvds|cd rom|
blu ray|bluetooth|wi fi|wifi|wimax|wlan|5g|4g|3g|
voip|voice over internet|internet telephony|ip telephony|
fiber optic|fibre optic|optical fiber|optical fibre|
networking|router|routers|modem|modems|ethernet|
server|servers|database|databases|databases|
digital camera|digital cameras|mp3|mp3 player|mp3 players|
portable music player|digital music|music downloads|
flat panel|flat screen|liquid crystal|lcd|oled|
touchscreen|touchscreens|wearable|wearables|
mobile phone|mobile phones|cell phone|cell phones|
handset|handsets|tablet|tablets|pda|pdas|
app|apps|application software|mobile application|
download|downloads|downloaded|downloading|upload|
browser|browsers|portal|portals|webcam|webcams|
blog|blogs|blogger|bloggers|blogging|podcast|podcasts|
streaming|livestreaming|online service|online services|
digital rights management|drm|html|xml|javascript|python|
java|linux kernel|unix|sql|api|apis|html5|
blockchain|blockchains|fintech|3d printing|3d printer|
drone|drones|autonomous vehicle|autonomous vehicles|
self driving|driverless|autonomous driving|
facial recognition|face recognition|speech recognition|
neural network|neural networks|chatbot|chatbots|
ai|chatgpt|gpt|llm|llms|
medicine|medical|clinical|biomedical|biological|
cancer|tumor|tumors|tumour|tumours|leukemia|leukaemia|
lymphoma|melanoma|oncology|cardiology|cardiovascular|
antibody|antibodies|antibiotic|antibiotics|
antiviral|antivirals|protein|proteins|enzyme|enzymes|
bacteria|bacterial|bacterium|microbe|microbes|microbial|
molecule|molecules|molecular|atom|atoms|atomic|
cellular biology|cell biology|cell division|
embryo|embryos|embryonic|fertility|infertility|
ivf|in vitro|transplant|transplants|transplantation|
neuron|neurons|neural|neurological|
hiv|aids research|aids vaccine|malaria|tuberculosis|
sars|ebola|coronavirus|covid 19|bird flu|avian flu|
flu vaccine|influenza|immunization|immunisation|
obesity|obese|cholesterol|blood pressure|
heart disease|heart attack|heart attacks|
breast cancer|lung cancer|prostate cancer|
side effects|drug trial|drug trials|drug approval|fda|
food and drug administration|cdc|centers for disease control|
world health organization|who study|
mars|venus|jupiter|saturn|neptune|pluto|mercury planet|
lunar|martian|interplanetary|interstellar|
galaxy|galaxies|nebula|nebulae|solar system|
solar flare|solar flares|sunspot|sunspots|
solar wind|cosmic rays|cosmic|cosmos|universe|
satellite|satellites|space|gravity|gravitational|
light years|light year|lightyear|lightyears|
fusion|fission|particle|particles|proton|protons|
neutrino|neutrinos|electron|electrons|
superconductivity|superconductor|superconductors|
laser|lasers|photon|photons|photonics|optics|
global warming|climate change|greenhouse gas|greenhouse gases|
greenhouse effect|ozone layer|ozone hole|
biodiversity|ecosystem|ecosystems|ecology|ecological|
geology|geologist|geologists|seismology|seismologist|
tectonic|plate tectonics|oceanography|
extinction|extinct|endangered species|
radiocarbon|carbon dating|archaeological|prehistoric|
renewable technology|solar cell|solar cells|fuel cell|fuel cells|
battery technology|lithium ion|graphene|
massachusetts institute of technology|johns hopkins|
royal society|national academy of sciences|
new scientist|scientific american|nature journal|science journal|
new england journal of medicine|the lancet
""")
_add("sci_tech", 1.5, """
online|web|digital|network|networks|mobile|phone|phones|
telephone|telephony|electronic|electronics|electrical|
multimedia|cyber|virtual|interactive|automated|automation|
data|analytics|bandwidth|connectivity|connected|
interface|interfaces|upgrade|upgrades|upgraded|
patch|patches|patched|vulnerability|vulnerabilities|
gadget|gadgets|device|devices|patent|patents|patented|
computational|simulation|simulations|simulate|simulator|
innovation|innovative|technical|prototype|prototypes|
high tech|hi tech|tech|hi-tech|
health|healthy|healthcare|health care|disease|diseases|
patient|patients|doctor|doctors|physician|physicians|
treatment|treatments|therapy|therapies|therapeutic|
drug|drugs|pill|pills|medication|medications|
surgery|surgeon|surgeons|surgical|diagnosis|diagnostic|
symptom|symptoms|infection|infections|infected|
virus|viruses|viral|flu|vital|immune|immunity|
brain|brains|kidney|kidneys|lung|lungs|liver|
blood|tissue|tissues|cell|cells|diabetic|stroke|
epidemic|pandemic|nutrition|diet|diets|
vitamin|vitamins|supplement|supplements|
smoking|tobacco|nicotine|carcinogen|carcinogens|
pregnancy|pregnant|birth defects|newborn|
life expectancy|longevity|aging|ageing|
mental health|depression treatment|psychiatry|psychology|
adhd|autism|schizophrenia|dementia|
organism|organisms|species|mammal|mammals|
amphibian|amphibians|reptile|reptiles|primate|primates|
chimpanzee|chimpanzees|orangutan|orangutans|
whale|whales|dolphin|dolphins|shark|sharks|
insect|insects|pollination|pollinator|
habitat|habitats|coral|reef|reefs|
ocean|oceans|arctic|antarctic|antarctica|
glacier|glaciers|glacial|permafrost|
carbon dioxide|methane|emissions|carbon emissions|
environmental|environment|pollution|pollutants|
climate|climatic|warming|rainforest|rainforests|
planet|planets|earth|moon|moons|sunlight|
rocket|rockets|launch vehicle|launch pad|launchpad|
probe|probes|lander|rover|rovers|
measurement|measurements|hypothesis|theory|
mathematics|mathematician|mathematicians|mathematical
""")

_TECH_COMPANIES = _phrase_set("""
microsoft|google|alphabet inc|alphabet shares|apple|apple computer|
apple inc|ibm|international business machines|intel|amd|
advanced micro devices|nvidia|ati technologies|ati|
hewlett packard|hewlett-packard|hp|hpe|dell|lenovo|acer|asus|
asustek|toshiba|fujitsu|nec|hitachi|panasonic|sharp electronics|
samsung|lg electronics|sony|nintendo|sega|electronic arts|
ubisoft|activision|blizzard|activision blizzard|take two interactive|
take-two interactive|rockstar games|epic games|valve software|
square enix|konami|capcom|bandai namco|
oracle|sap|salesforce|adobe|adobe systems|autodesk|intuit|
sun microsystems|sun micro|red hat|novell|suse|
vmware|citrix|netscape|realnetworks|macromedia|corel|
symantec|mcafee|norton|kaspersky|sophos|trend micro|
palo alto networks|fortinet|crowdstrike|okta|
cisco|cisco systems|juniper networks|arista networks|
broadcom|qualcomm|marvell|mediatek|texas instruments|
micron|infineon|stmicroelectronics|arm holdings|arm ltd|
tsmc|taiwan semiconductor|asml|applied materials|
lam research|kla tencor|globalfoundries|sk hynix|
western digital|seagate|sandisk|kingston technology|
logitech|razer|corsair|creative technology|
emc|netapp|veritas|storage technology|
nokia|motorola|ericsson|sony ericsson|huawei|zte|htc|
blackberry|research in motion|palm|palmone|palmsource|
oneplus|oppo|vivo smartphones|xiaomi|
alcatel|lucent|alcatel lucent|nortel|siemens|
at&t|at and t|verizon|vodafone|sprint|t mobile|t-mobile|
deutsche telekom|france telecom|orange telecom|telefonica|
telecom italia|british telecom|bt group|o2|
sbc communications|sbc|bellsouth|bell south|qwest|
mci|worldcom|ntt|ntt docomo|docomo|softbank|
china mobile|china telecom|china unicom|singtel|telstra|
yahoo|aol|america online|lycos|ask jeeves|ask com|
alta vista|altavista|baidu|yandex|
amazon|amazon.com|ebay|paypal|alibaba|tencent|jd.com|
rakuten|shopify|etsy|mercadolibre|
facebook|meta|meta platforms|instagram|whatsapp|
twitter|x formerly twitter|snapchat|snap inc|tiktok|bytedance|
linkedin|pinterest|reddit|tumblr|wechat|weibo|
youtube|netflix|spotify|pandora media|twitch|
skype|zoom|zoom video|slack|discord|telegram|signal app|
dropbox|box inc|evernote|notion labs|
openai|anthropic|deepmind|hugging face|stability ai|
databricks|snowflake inc|palantir|mongodb|elastic nv|
cloudflare|akamai|fastly|godaddy|verisign|verisign inc|
github|gitlab|bitbucket|atlassian|servicenow|
workday|peoplesoft|siebel|business objects|
uber|lyft|airbnb|doordash|grubhub|instacart|
expedia|booking holdings|tripadvisor|
spacex|blue origin|rocket lab|virgin galactic|
dji|boston dynamics|irobot|fitbit|garmin|gopro|oculus|
foxconn|hon hai|quanta computer|compal|
bill gates|steve jobs|steve ballmer|tim cook|
satya nadella|sundar pichai|larry page|sergey brin|
mark zuckerberg|larry ellison|michael dell|linus torvalds|
jensen huang|sam altman|steve wozniak
""")
for _p in _TECH_COMPANIES:
    _FEATURES.setdefault(_p, {})["sci_tech"] = 5.8

_TECH_PRODUCTS = _phrase_set("""
windows xp|windows vista|windows 7|windows 8|windows 10|windows 11|
windows server|windows update|microsoft windows|microsoft office|
office 365|microsoft 365|microsoft word|microsoft excel|
microsoft teams|microsoft edge|internet explorer|
outlook express|windows media|windows phone|directx|
linux|ubuntu|debian|fedora linux|android|ios|macos|mac os|
iphone|ipad|ipod|imac|macbook|mac mini|apple watch|airpods|
itunes|app store|apple music|apple tv|apple pay|
google play|google maps|google earth|google news|
google search|google chrome|chrome browser|chromebook|
gmail|google cloud|google drive|google docs|
firefox|mozilla|thunderbird|opera browser|safari browser|
bing|duckduckgo|chatgpt|copilot|google gemini|claude ai|
xbox|xbox live|xbox 360|xbox one|playstation|playstation 2|
playstation 3|playstation 4|playstation 5|ps2|ps3|ps4|ps5|
psp|wii|gamecube|nintendo ds|nintendo switch|game boy|
steam deck|steam games|battle net|
halo 2|halo 3|half life|half life 2|doom 3|
grand theft auto|world of warcraft|warcraft|
call of duty|fortnite|minecraft|the sims|pokémon|pokemon|
geforce|radeon|pentium|athlon|xeon|itanium|ryzen|snapdragon|
centrino|powerpc|power mac|thinkpad|ideapad|
photoshop|acrobat|flash player|dreamweaver|coldfusion|
quicktime|realplayer|winamp|napster|kazaa|bittorrent|
ipaq|treo|blackberry phone|razr|galaxy smartphone|
galaxy phone|galaxy s|google pixel|surface pro|
kindle|alexa|amazon echo|aws|amazon web services|
sql server|mysql|postgresql|apache|kubernetes|docker|
tensor flow|tensorflow|pytorch|cuda|
hubble|chandra telescope|cassini|huygens probe|galileo probe|
voyager spacecraft|voyager 1|voyager 2|mars express|
mars rover|mars rovers|mars pathfinder|mars odyssey|
spirit rover|opportunity rover|curiosity rover|perseverance rover|
new horizons|rosetta spacecraft|starliner|
shuttle discovery|shuttle atlantis|shuttle columbia|
shuttle endeavour|shuttle endeavor|soyuz spacecraft|
artemis mission|apollo mission|falcon 9|starship rocket|
james webb space telescope
""")
for _p in _TECH_PRODUCTS:
    _FEATURES.setdefault(_p, {})["sci_tech"] = 5.4
_add("sci_tech", 2.0, "windows|terabyte|gigabyte|megabyte|gigahertz|megahertz|pixel|pixels")


# Sporting events, participants, competitions and clubs.
_add("sports", 5.5, """
sports|sport|sporting|football|soccer|basketball|baseball|
hockey|cricket|rugby|tennis|golf|badminton|volleyball|
handball|softball|lacrosse|netball|squash|table tennis|
olympics|olympic|olympians|olympian|paralympics|paralympic|
world cup|world series|super bowl|superbowl|stanley cup|
champions league|europa league|premier league|premiership|
major league baseball|major league soccer|national football league|
national basketball association|national hockey league|
national rugby league|national collegiate athletic association|
nba|wnba|nfl|nhl|mlb|mls|ncaa|fifa|uefa|afc champions league|
fiba|icc cricket|international cricket council|
pga|lpga|atp|wta|wimbledon|roland garros|
us open|u.s. open|australian open|french open|british open|
ryder cup|davis cup|fed cup|presidents cup|
tour de france|giro d italia|vuelta a espana|
formula one|formula 1|f1|nascar|indycar|indy 500|
grand prix|motogp|world rally championship|
heavyweight|welterweight|middleweight|lightweight title|
boxing|boxer|boxers|kickboxing|mixed martial arts|mma|ufc|
wrestling|wrestler|wrestlers|sumo|judo|taekwondo|
olympic games|commonwealth games|asian games|winter games|
championship|championships|tournament|tournaments|
playoffs|playoff|postseason|post season|
semifinal|semifinals|semi final|semi finals|
quarterfinal|quarterfinals|quarter final|quarter finals|
quarterback|quarterbacks|touchdown|touchdowns|
linebacker|linebackers|running back|running backs|
wide receiver|wide receivers|field goal|field goals|
home run|home runs|homer|homers|pitcher|pitchers|
shortstop|catcher|outfielder|outfielders|infielder|
bullpen|dugout|designated hitter|batting average|
goalkeeper|goalkeepers|goalie|goalies|striker|strikers|
midfielder|midfielders|hat trick|hat tricks|
wicket|wickets|batsman|batsmen|batswoman|batswomen|
bowler|bowlers|innings|lbw|test match|test matches|
birdie|birdies|bogey|bogeys|eagle putt|tee off|
pole vault|high jump|long jump|triple jump|shot put|
decathlon|heptathlon|steeplechase|hurdles|
gold medal|silver medal|bronze medal|gold medals|
silver medals|bronze medals|world record|world records
""")
_add("sports", 3.5, """
athlete|athletes|athletic|athletics|sportsman|sportsmen|
sportswoman|sportswomen|sportsmanship|
champion|champions|championship game|title defense|
medalist|medallists|medallist|medalists|podium|
gymnastics|gymnast|gymnasts|swimming|swimmer|swimmers|
diving|diver|divers|rowing|rower|rowers|canoeing|kayaking|
sailing|sailor|sailors|yachting|windsurfing|
cycling|cyclist|cyclists|bicycling|triathlon|triathlete|
marathon|marathoner|sprinter|sprinters|sprinting|
skiing|skier|skiers|snowboarding|snowboarder|
bobsled|bobsleigh|luge|biathlon|curling|
figure skating|speed skating|skater|skaters|skating|
fencing|fencer|archery|archer|weightlifting|weightlifter|
equestrian|show jumping|dressage|horse racing|
racehorse|racehorses|jockey|jockeys|thoroughbred|
derby winner|kentucky derby|belmont stakes|preakness|
breeders cup|melbourne cup|grand national|
motor racing|auto racing|motorsport|motorsports|racecar|
speedway|racing driver|racing drivers|pit stop|pole position|
checkered flag|chequered flag|
knockout|knockouts|knocked out|boxing ring|
bout|bouts|sparring|knockdown|undercard|
doping|steroids|anti doping|antidoping|
matchup|matchups|rematch|fixtures|fixture|
league|leagues|standings|scoreboard|
coach|coaches|coaching|head coach|
roster|rosters|teammate|teammates|team mate|team mates|
playmaker|playmakers|defender|defenders|
fullback|fullbacks|halftime|half time|overtime|
goalscorer|goalscorers|goal scorer|goal scorers|
equalizer|equaliser|penalty shootout|shoot out|
penalty kick|penalty kicks|red card|yellow card|
clean sheet|offside|off side|free kick|free kicks|
corner kick|header|headers|stoppage time|injury time|
kickoff|kick off|kicked off|dribble|dribbling|
relegation|relegated|promotion playoff|
slam dunk|slam dunks|dunk|dunks|rebounds|rebounder|
three pointer|three pointers|free throw|free throws|
buzzer beater|basketball court|shooting guard|point guard|
strikeout|strikeouts|strike out|strike outs|
fastball|curveball|pinch hitter|pinch hit|
batting|batting order|batting lineup|batting line up|
batting title|base hit|base hits|rbi|rbis|grand slam|
no hitter|perfect game|doubleheader|double header|
power play|powerplay|puck|pucks|faceoff|face off|
saves|shutout|shutouts|blue line|penalty box|
scrum|scrums|lineout|lineouts|rugby union|rugby league|
six nations|tri nations|super rugby|super 12|
test cricket|one day cricket|one day international|
twenty20|t20|ipl|ashes|the ashes|
spinner|spinners|seamer|seamers|centuries|
bowling figures|run rate|opening batsman|
putt|putts|putting|fairway|fairways|greenside|
clubhouse lead|clubhouse leader|under par|over par|
straight sets|straight set|tiebreak|tiebreaker|
tie break|tie breaker|match point|break point|
set point|double fault|double faults|
serve and volley|tennis court|tennis star|
seeded|top seeded|top seed|world number one|
world no 1|number one seed|
sprint finish|peloton|time trial|yellow jersey|
personal best|season best|career best|
training camp|preseason|pre season|regular season|
season opener|home opener|opening game|away game|
winning streak|losing streak|unbeaten|undefeated|
team captain|national team|national side|international cap|
free agent|free agency|transfer window|transfer fee|
sports federation|sports minister|sports ministry|
international olympic committee|ioc|usoc|
anti doping agency|wada|ballon d or
""")
_add("sports", 1.3, """
player|players|team|teams|captain|captains|captaincy|
fan|fans|supporters|stadium|stadiums|arena|
match|matches|game|games|season|seasons|
win|wins|winning|winner|winners|won|
beat|beats|beaten|beating|defeat|defeats|defeated|
victory|victories|triumph|triumphs|triumphant|
loser|losers|lost|losses|draw|draws|drawn|tied|
score|scores|scored|scoring|goal|goals|
final|finals|finalist|finalists|runner up|runners up|
round|rounds|contest|contestants|competitor|competitors|
compete|competes|competed|competing|competitive|
qualifier|qualifiers|qualifying|qualified|qualification|
rival|rivals|rivalry|derby|clash|clashes|
defending|defense|defence|offense|offence|
penalty|penalties|referee|referees|umpire|umpires|
tackle|tackles|tackling|passes|passing|passer|
interception|interceptions|reception|receptions|
rushing|rusher|yards|yardage|kick|kicks|
pitch|pitches|pitching|batter|batters|
run|runs|inning|bat|bats|ball|balls|
swing|swings|stroke|strokes|ace|aces|
racquet|racket|rackets|racketers|
serve|serves|serving|returner|volleys|volley|
bench|benched|lineup|line up|starting lineup|
substitute|substitutes|substitution|
injury|injuries|injured|fitness|hamstring|ankle|knee|
tendon|ligament|concussion|rehabilitation|
comeback|comebacks|retirement|retired|retires|
contract extension|signing|signings|signed|
medal|medals|trophy|trophies|cup|cups|
race|races|racing|racer|racers|runner|runners|
track|tracks|lap|laps|finish line|finishing line|
record holder|record breaking|record breaker|
sports car|mountain biking|skateboarding|surfing|
chess|billiards|snooker|darts|bowling|poker|
espn|eurosport|sports illustrated
""")

_SPORT_ENTITIES = _phrase_set("""
new york yankees|yankees|boston red sox|red sox|chicago white sox|
white sox|new york mets|mets|chicago cubs|cubs|
st louis cardinals|st. louis cardinals|los angeles dodgers|dodgers|
san francisco giants|san diego padres|padres|atlanta braves|braves|
philadelphia phillies|phillies|baltimore orioles|orioles|
toronto blue jays|blue jays|tampa bay rays|devil rays|
minnesota twins|cleveland indians|cleveland guardians|
detroit tigers|kansas city royals|oakland athletics|
oakland a's|seattle mariners|mariners|texas rangers|
anaheim angels|los angeles angels|houston astros|astros|
florida marlins|miami marlins|marlins|montreal expos|expos|
washington nationals|pittsburgh pirates|cincinnati reds|
milwaukee brewers|colorado rockies|arizona diamondbacks|diamondbacks|
los angeles lakers|lakers|los angeles clippers|clippers|
boston celtics|celtics|chicago bulls|new york knicks|knicks|
brooklyn nets|new jersey nets|miami heat|orlando magic|
detroit pistons|pistons|indiana pacers|pacers|
cleveland cavaliers|cavaliers|toronto raptors|raptors|
philadelphia 76ers|76ers|sixers|washington wizards|
milwaukee bucks|atlanta hawks|charlotte hornets|charlotte bobcats|
golden state warriors|sacramento kings|phoenix suns|
dallas mavericks|mavericks|san antonio spurs|spurs|
houston rockets|denver nuggets|nuggets|utah jazz|
portland trail blazers|trail blazers|memphis grizzlies|grizzlies|
minnesota timberwolves|timberwolves|seattle supersonics|supersonics|
oklahoma city thunder|new orleans pelicans|new orleans hornets|
new england patriots|patriots|dallas cowboys|cowboys|
green bay packers|packers|pittsburgh steelers|steelers|
san francisco 49ers|49ers|niners|new york giants|new york jets|
philadelphia eagles|baltimore ravens|ravens|washington redskins|
redskins|washington commanders|chicago bears|detroit lions|
minnesota vikings|vikings|atlanta falcons|new orleans saints|
carolina panthers|tampa bay buccaneers|buccaneers|
los angeles rams|st louis rams|seattle seahawks|seahawks|
arizona cardinals|denver broncos|broncos|kansas city chiefs|
oakland raiders|las vegas raiders|san diego chargers|los angeles chargers|
miami dolphins|buffalo bills|cincinnati bengals|bengals|
cleveland browns|indianapolis colts|colts|tennessee titans|
houston texans|jacksonville jaguars|
toronto maple leafs|maple leafs|montreal canadiens|canadiens|
boston bruins|bruins|new york rangers|new york islanders|islanders|
new jersey devils|philadelphia flyers|flyers|pittsburgh penguins|
washington capitals|tampa bay lightning|florida panthers|
detroit red wings|red wings|chicago blackhawks|blackhawks|
colorado avalanche|dallas stars|los angeles kings|
san jose sharks|anaheim ducks|mighty ducks|vancouver canucks|canucks|
calgary flames|edmonton oilers|oilers|ottawa senators|
winnipeg jets|nashville predators|carolina hurricanes|
columbus blue jackets|st louis blues|buffalo sabres|sabres|
minnesota wild|vegas golden knights|seattle kraken|
manchester united|man united|man utd|manchester city|man city|
liverpool|chelsea|arsenal|tottenham|tottenham hotspur|
everton|aston villa|newcastle united|newcastle utd|
west ham|west ham united|leeds united|leicester city|
nottingham forest|blackburn rovers|bolton wanderers|
wolverhampton wanderers|wolverhampton|southampton fc|
portsmouth fc|fulham|charlton athletic|crystal palace|
west bromwich|sunderland afc|birmingham city|
real madrid|atletico madrid|atletico|fc barcelona|barcelona|
valencia cf|villarreal|sevilla fc|real sociedad|
athletic bilbao|deportivo la coruna|real betis|
bayern munich|bayern|borussia dortmund|dortmund|
bayer leverkusen|werder bremen|schalke|rb leipzig|
ac milan|inter milan|internazionale|juventus|
as roma|lazio|napoli|fiorentina|atalanta|
paris saint germain|paris st germain|psg|
olympique lyon|olympique lyonnais|marseille|
ajax|psv eindhoven|feyenoord|fc porto|benfica|
sporting lisbon|sporting cp|celtic fc|glasgow celtic|
glasgow rangers|aberdeen fc|hearts fc|
galatasaray|fenerbahce|besiktas|shakhtar donetsk|
dynamo kyiv|dynamo kiev|dinamo zagreb|
boca juniors|river plate|flamengo|corinthians|
santos fc|sao paulo fc|palmeiras|gremio|
la galaxy|los angeles galaxy|inter miami|dc united|
new york red bulls|seattle sounders|
a league|bundesliga|la liga|serie a|ligue 1|
eredivisie|fa cup|carabao cup|copa del rey|copa america|
copa libertadores|concacaf|conmebol|euro 2004|euro 2024|
all blacks|springboks|wallabies|british lions|british and irish lions|
queensland reds|new south wales waratahs|leicester tigers|
sydney swans|brisbane lions|collingwood|geelong|essendon|
west coast eagles|adelaide crows|port adelaide|
melbourne storm|brisbane broncos|sydney roosters|
new york marathon|boston marathon|london marathon|
daytona 500|daytona international speedway|indianapolis 500|
scuderia ferrari|mclaren racing|mercedes f1|red bull racing|
williams f1|renault f1|aston martin f1|
duke blue devils|north carolina tar heels|tar heels|
kentucky wildcats|connecticut huskies|uconn|
michigan wolverines|ohio state buckeyes|buckeyes|
alabama crimson tide|crimson tide|auburn tigers|
florida gators|gators|florida state seminoles|seminoles|
usc trojans|ucla bruins|notre dame fighting irish|
penn state nittany lions|nittany lions|lsu tigers|
oklahoma sooners|sooners|texas longhorns|longhorns|
nebraska cornhuskers|cornhuskers|oregon ducks|
big ten|big 12|big east|southeastern conference|
pac 10|pac 12|atlantic coast conference|
roger federer|federer|rafael nadal|nadal|novak djokovic|djokovic|
andy murray|andy roddick|roddick|andre agassi|agassi|
pete sampras|sampras|lleyton hewitt|hewitt tennis|
marat safin|safin|tim henman|henman|juan carlos ferrero|
david nalbandian|nalbandian|carlos moya|gustavo kuerten|
serena williams|serena|venus williams|martina hingis|hingis|
maria sharapova|sharapova|justine henin|henin|
kim clijsters|clijsters|lindsay davenport|davenport tennis|
amelie mauresmo|mauresmo|svetlana kuznetsova|kuznetsova|
elena dementieva|dementieva|jennifer capriati|capriati|
martina navratilova|navratilova|chris evert|steffi graf|
naomi osaka|iga swiatek|swiatek|coco gauff|
carlos alcaraz|alcaraz|jannik sinner|
tiger woods|phil mickelson|mickelson|vijay singh|
ernie els|els golf|retief goosen|goosen|sergio garcia|
padraig harrington|darren clarke|colin montgomerie|montgomerie|
jack nicklaus|nicklaus|arnold palmer|tom watson|
davis love iii|john daly|rory mcilroy|mcilroy|
jordan spieth|brooks koepka|jon rahm|scottie scheffler|
annika sorenstam|sorenstam|michelle wie|lorena ochoa|
david beckham|beckham|wayne rooney|rooney|
cristiano ronaldo|ronaldo|ronaldinho|rivaldo|
zinedine zidane|zidane|thierry henry|patrick vieira|
ruud van nistelrooy|van nistelrooy|dennis bergkamp|bergkamp|
michael owen|steven gerrard|gerrard|frank lampard|lampard|
paul scholes|ryan giggs|giggs|roy keane|robbie keane|
david villa|fernando torres|raul gonzalez|iker casillas|
gianluigi buffon|buffon|alessandro del piero|del piero|
francesco totti|totti|paolo maldini|maldini|
andriy shevchenko|shevchenko|didier drogba|drogba|
samuel eto o|sachin tendulkar|tendulkar|
lionel messi|messi|neymar|kylian mbappe|mbappe|
erling haaland|haaland|mohamed salah|sadio mane|
zlatan ibrahimovic|ibrahimovic|luis suarez|
alex ferguson|arsene wenger|wenger|jose mourinho|mourinho|
rafael benitez|rafa benitez|pep guardiola|guardiola|
jurgen klopp|klopp|carlo ancelotti|ancelotti|
sven goran eriksson|eriksson|
michael jordan|lebron james|lebron|kobe bryant|kobe|
shaquille o neal|shaquille|shaq|allen iverson|iverson|
tim duncan|kevin garnett|garnett|dirk nowitzki|nowitzki|
yao ming|tracy mcgrady|mcgrady|vince carter|
jason kidd|steve nash|nash nba|paul pierce|
dwyane wade|carmelo anthony|chris bosh|
stephen curry|steph curry|kevin durant|durant|
giannis antetokounmpo|antetokounmpo|nikola jokic|jokic|
luka doncic|doncic|joel embiid|embiid|jayson tatum|
magic johnson|larry bird|kareem abdul jabbar|
barry bonds|sammy sosa|mark mcgwire|derek jeter|jeter|
alex rodriguez|a rod|babe ruth|hank aaron|
roger clemens|clemens|randy johnson|pedro martinez|
curt schilling|schilling|david ortiz|manny ramirez|
ichiro suzuki|ichiro|hideki matsui|matsui|
albert pujols|pujols|ken griffey|shohei ohtani|ohtani|
mike trout|aaron judge|mookie betts|
tom brady|brady nfl|peyton manning|eli manning|
brett favre|favre|joe montana|dan marino|
michael vick|vick|donovan mcnabb|mcnabb|
ben roethlisberger|roethlisberger|drew brees|
terrell owens|randy moss|jerry rice|emmitt smith|
ladainian tomlinson|tomlinson nfl|ray lewis|
aaron rodgers|patrick mahomes|mahomes|
lamar jackson|josh allen|travis kelce|
wayne gretzky|gretzky|mario lemieux|lemieux|
sidney crosby|crosby nhl|alex ovechkin|ovechkin|
jaromir jagr|jagr|martin brodeur|brodeur|
connor mcdavid|mcdavid|nathan mackinnon|
brian lara|rahul dravid|dravid|sourav ganguly|ganguly|
vvs laxman|anil kumble|kumble|virender sehwag|sehwag|
harbhajan singh|harbhajan|yuvraj singh|
ricky ponting|ponting|adam gilchrist|gilchrist|
shane warne|warne|glenn mcgrath|mcgrath|
steve waugh|mark waugh|brett lee|
muttiah muralitharan|muralitharan|sanath jayasuriya|jayasuriya|
kumar sangakkara|sangakkara|mahela jayawardene|jayawardene|
wasim akram|waqar younis|shoaib akhtar|akhtar|
inzamam ul haq|inzamam|younis khan|
jacques kallis|kallis|shaun pollock|pollock cricket|
graeme smith|herschelle gibbs|michael vaughan|
andrew flintoff|flintoff|kevin pietersen|pietersen|
andrew strauss|andrew freddie flintoff|
ms dhoni|mahendra singh dhoni|dhoni|virat kohli|kohli|
rohit sharma|jasprit bumrah|bumrah|ben stokes|
joe root|kane williamson|babar azam|
michael schumacher|schumacher|ralf schumacher|
rubens barrichello|barrichello|juan pablo montoya|montoya|
fernando alonso|alonso|kimi raikkonen|raikkonen|
jenson button|david coulthard|coulthard|
lewis hamilton|max verstappen|verstappen|
sebastian vettel|vettel|charles leclerc|
valentino rossi|rossi motogp|marc marquez|
dale earnhardt|earnhardt|jeff gordon|jimmie johnson|
tony stewart|kurt busch|kyle busch|matt kenseth|
lance armstrong|jan ullrich|ullrich|ivan basso|
alberto contador|contador|chris froome|froome|
tadej pogacar|pogacar|jonas vingegaard|vingegaard|
michael phelps|phelps|ian thorpe|thorpe|
katie ledecky|ledecky|caeleb dressel|
usain bolt|bolt sprinter|carl lewis|justin gatlin|gatlin|
maurice greene|asafa powell|tyson gay|yohan blake|
paula radcliffe|radcliffe|haile gebrselassie|gebrselassie|
kenenisa bekele|bekele|eliud kipchoge|kipchoge|
hicham el guerrouj|el guerrouj|kelly holmes|
yuliya nesterenko|liu xiang|liu xiang hurdles|
simone biles|biles|nadia comaneci|
carly patterson|svetlana khorkina|khorkina|
muhammad ali|mike tyson|tyson boxer|lennox lewis|
evander holyfield|holyfield|oscar de la hoya|de la hoya|
bernard hopkins|roy jones jr|floyd mayweather|mayweather|
manny pacquiao|pacquiao|wladimir klitschko|klitschko|
tyson fury|oleksandr usyk|usyk|canelo alvarez|
conor mcgregor|khabib nurmagomedov|jon jones|
ronda rousey|rousey|serena tennis|
magnus carlsen|carlsen|garry kasparov|kasparov|
viswanathan anand|vladimir kramnik|kramnik|
bobby fischer|fischer chess
""")
for _p in _SPORT_ENTITIES:
    _FEATURES.setdefault(_p, {})["sports"] = 5.6

# These place names and ordinary words are less conclusive than full club names.
for _p in _phrase_set("chelsea|liverpool|barcelona|dortmund|arsenal|ajax|alonso"):
    _FEATURES.setdefault(_p, {})["sports"] = 2.8


# Politics, international affairs, conflict, public safety and crime.
_add("world", 5.0, """
election|elections|electoral|referendum|referendums|
presidential election|general election|parliamentary election|
prime minister|foreign minister|defense minister|defence minister|
interior minister|foreign secretary|secretary of state|
foreign ministry|foreign affairs|state department|
united nations|un security council|security council|
un general assembly|nato|north atlantic treaty organization|
peace talks|peace agreement|peace accord|ceasefire|cease fire|
peacekeeping|peacekeepers|peacekeeper|
terrorism|terrorist|terrorists|terror attack|terror attacks|
suicide bomber|suicide bombers|suicide bombing|suicide bombings|
car bomb|car bombs|bomb blast|bomb blasts|
insurgency|insurgent|insurgents|militant|militants|
hostage|hostages|hostage taking|kidnapping|kidnapped|
civil war|civil unrest|ethnic violence|sectarian violence|
genocide|war crime|war crimes|crimes against humanity|
military coup|coup attempt|coup d etat|martial law|
assassination|assassinated|assassinate|
human rights|humanitarian crisis|refugee crisis|
earthquake|earthquakes|tsunami|tsunamis|
hurricane|hurricanes|typhoon|typhoons|tornado|tornadoes|
flooding|floods|landslide|landslides|mudslide|mudslides|
wildfire|wildfires|bushfire|bushfires|forest fire|forest fires|
plane crash|air crash|train crash|train derailment|
ferry disaster|ferry sinking|building collapse|mine collapse|
death toll|mass shooting|mass shootings|serial killer
""")
_add("world", 3.4, """
politics|political|politician|politicians|politically|
government|governments|governing|governance|
parliament|parliamentary|congress|congressional|
senate|senator|senators|legislature|legislatures|
legislator|legislators|lawmaker|lawmakers|
democrat|democrats|democratic party|
republican|republicans|republican party|
conservative party|labour party|labor party|liberal democrats|
green party|socialist party|communist party|
opposition leader|opposition party|ruling party|
political party|political parties|political campaign|
presidential campaign|campaign trail|election campaign|
presidential debate|presidential debates|running mate|
ballot|ballots|voter|voters|voting|recount|
constitution|constitutional|amendment|amendments|
impeachment|impeached|inauguration|
minister|ministers|cabinet|chancellor|
diplomat|diplomats|diplomacy|diplomatic|
ambassador|ambassadors|embassy|embassies|consulate|
envoy|envoys|summit|state visit|official visit|
treaty|treaties|sanctions|sanctioned|embargo|
sovereignty|sovereign|secession|separatist|separatists|
independence referendum|territorial dispute|
war|wars|warfare|wartime|warring|
military|militaries|army|armies|navy|naval|air force|
soldier|soldiers|troop|troops|marine|marines|
combat|combatant|combatants|battlefield|
invasion|invade|invaded|invading|occupation|
airstrike|airstrikes|air strike|air strikes|
air raid|air raids|bombardment|shelling|
bomb|bombs|bombing|bombings|bomber|bombers|
explosion|explosions|explosive|explosives|
missile|missiles|warhead|warheads|
nuclear weapons|nuclear weapon|nuclear program|nuclear programme|
nuclear talks|nuclear test|nuclear tests|nuclear deal|
weapons of mass destruction|wmd|
rebels|rebel|rebellion|guerrilla|guerrillas|
guerilla|guerillas|militia|militias|
extremist|extremists|extremism|radical islam|
islamist|islamists|jihadist|jihadists|jihad|
hamas|hezbollah|hizbollah|taliban|al qaeda|al qaida|
islamic state|isil|isis|boko haram|islamic jihad|
fatah|plo|pkk|eta separatists|farc|
protester|protesters|protestor|protestors|demonstrators|
demonstration|demonstrations|riots|riot|rioting|
uprising|revolution|revolutionary|coup|junta|
curfew|crackdown|crackdowns|state of emergency|
police|policing|constable|detective|detectives|
arrest|arrests|arrested|detained|detention|
prison|prisons|prisoner|prisoners|jail|jailed|
criminal|criminals|crime|crimes|
murder|murders|murdered|murderer|murderers|
homicide|manslaughter|slaying|slain|killing|killings|
killed|kill|kills|dead|deadly|fatal|fatalities|
shooting|shootings|gunman|gunmen|gunfire|gunfight|
stabbing|stabbed|knife attack|armed robbery|robbery|
raped|rape|rapist|sexual assault|sexual abuse|
abduction|abducted|abductors|trafficking|drug trafficking|
drug smuggling|drug cartel|cartel violence|
smuggler|smugglers|smuggling|gang|gangs|
organized crime|organised crime|mafia|
prosecutor|prosecutors|prosecution|prosecutions|
indicted|indictment|indictments|convicted|conviction|
acquitted|acquittal|sentenced|sentencing|
execution|executed|death penalty|death sentence|
extradition|extradited|extradite|fugitive|fugitives|
corruption|bribery|bribe|bribes|
refugee|refugees|asylum|asylum seeker|asylum seekers|
displaced|displacement|famine|starvation|
humanitarian|relief efforts|relief supplies|
rescue operation|rescue operations|rescue workers|
disaster|disasters|catastrophe|catastrophic|
flood|flooded|evacuation|evacuations|evacuated|
avalanche|avalanches|blizzard|blizzards|
volcanic eruption|volcano erupts|volcano eruption|
oil spill|oil spills|chemical spill|toxic spill|
power outage|power outages|blackout|blackouts|
shipwreck|shipwrecks|capsized|sank|drowned|drowning|
amnesty international|human rights watch|red cross|
red crescent|international criminal court|war crimes tribunal|
supreme court|supreme court justice|
white house|downing street|kremlin|pentagon|
buckingham palace|vatican|holy see|
pope|papal|pontiff|archbishop|cardinal|
dalai lama|ayatollah|grand ayatollah|
gaza|gaza strip|west bank|occupied territories|
baghdad|fallujah|najaf|mosul|kirkuk|basra|
kabul|kandahar|donetsk|luhansk|
guantanamo|abu ghraib|abu ghraib prison|
north korea|north korean|pyongyang|
darfur|srebrenica|kashmir|chechnya|chechen|
beslan|belfast agreement|good friday agreement
""")
_add("world", 1.6, """
president|presidential|premier|governor|governors|
mayor|mayors|council|councillor|councilors|
administration|official|officials|authorities|
politic|policy|policies|legislation|legislative|
law|laws|legal|lawyer|lawyers|attorney|attorneys|
judge|judges|judicial|judiciary|justice|
court|courts|courtroom|hearing|hearings|
lawsuit|lawsuits|sued|sues|sue|
appeal|appeals|ruling|rulings|verdict|
trial|trials|testimony|testified|witness|witnesses|
suspect|suspects|suspected|alleged|allegedly|
investigation|investigations|investigate|investigates|
investigating|investigated|inquiry|inquiries|
officer|officers|sheriff|sheriffs|fbi|cia|interpol|
security|surveillance|intelligence|espionage|
spy|spies|spying|spied|espionage|
amnesty|pardon|pardoned|bail|custody|
fraud|fraudulent|scandal|scandals|
immigration|immigrant|immigrants|migrant|migrants|
migration|deportation|deported|border|borders|
citizenship|citizen|citizens|nationality|
democracy|democratic|democratization|dictator|dictatorship|
authoritarian|autocratic|regime|regimes|
communist|communists|socialist|socialists|
right wing|left wing|far right|far left|
nationalist|nationalists|nationalism|
conservative|conservatives|liberal|liberals|
vote|votes|voted|elect|elected|reelection|re election|
candidate|candidates|candidacy|nominee|nominees|
campaign|campaigning|poll|polls|polling|exit poll|exit polls|
coalition|opposition|incumbent|mandate|
protest|protests|protesting|activist|activists|
civil rights|civil liberties|civil society|
abortion|gay marriage|same sex marriage|
religion|religious|church|churches|mosque|mosques|
synagogue|synagogues|temple|temples|
muslim|muslims|islam|islamic|christian|christians|
christianity|jewish|jews|judaism|catholic|catholics|
protestant|protestants|hindu|hindus|buddhist|buddhists|
sunni|shiite|shiites|shia|sikh|sikhs|
cleric|clerics|clergy|priest|priests|bishop|bishops|
monk|monks|nun|nuns|imam|imams|rabbi|rabbis|
pilgrimage|pilgrims|hajj|ramadan|
monarch|monarchy|royal family|royal wedding|
king|queen|prince|princess|crown prince|
peace|peaceful|conflict|conflicts|violence|violent|
attack|attacks|attacked|attacking|assault|assaults|
battle|battles|fighting|fight|fought|
ambush|ambushed|raid|raids|raided|
armed|arms|weapon|weapons|gun|guns|rifle|rifles|
artillery|grenade|grenades|tank|tanks|
soldiers killed|casualty|casualties|wounded|wound|
injured|injuries|injury|injures|injuring|
death|deaths|died|dying|survivor|survivors|
victim|victims|corpse|corpses|bodies|
funeral|funerals|mourning|mourners|
crash|crashes|crashed|collision|collisions|accident|accidents|
rescue|rescued|rescues|rescuers|search and rescue|
missing|trapped|stranded|homeless|shelter|
storm|storms|stormy|rainstorm|rainstorms|
tropical storm|tropical depression|monsoon|monsoons|
heavy rain|heavy rains|torrential rain|torrential rains|
heatwave|heat wave|drought|droughts|
emergency|emergencies|emergency services|
firefighters|firefighter|firemen|fireman|fire brigade|
wildfires burning|blaze|blazes|
aid|aids|aid workers|aid agencies|humanitarian aid|
united nations aid|unicef|unesco|
outbreak|outbreaks|epidemic|pandemic|
world leaders|international relations|
european union|eu|african union|asean|arab league|
g7|g8|g20|apec|osce|council of europe|
kyoto protocol|paris agreement|
middle east|mideast|balkans|
iraq|iraqi|iraqis|afghanistan|afghan|afghans|
israel|israeli|israelis|palestine|palestinian|palestinians|
syria|syrian|syrians|iran|iranian|iranians|
lebanon|lebanese|yemen|yemeni|libya|libyan|
sudan|sudanese|somalia|somali|rwanda|rwandan|
ukraine|ukrainian|ukrainians|russia|russian|russians|
pakistan|pakistani|taiwan|taiwanese|
beirut|damascus|jerusalem|ramallah|tel aviv|
tehran|islamabad|karachi|peshawar|
kyiv|kiev|tbilisi|grozny|minsk|
khartoum|mogadishu|port au prince|
hong kong protests|tiananmen
""")
_add("world", 0.45, """
united states|us|usa|america|american|americans|
britain|british|uk|united kingdom|england|english|
france|french|germany|german|germans|
italy|italian|spain|spanish|portugal|portuguese|
europe|european|europeans|eurozone|
china|chinese|beijing|shanghai|
japan|japanese|tokyo|south korea|korean|seoul|
india|indian|indians|delhi|new delhi|
indonesia|indonesian|malaysia|malaysian|
singapore|thailand|thai|vietnam|vietnamese|
philippines|philippine|filipino|manila|
myanmar|burma|burmese|bangladesh|bangladeshi|
nepal|nepalese|sri lanka|sri lankan|
australia|australian|australians|new zealand|
canada|canadian|canadians|ottawa|
mexico|mexican|brazil|brazilian|argentina|argentine|
chile|chilean|colombia|colombian|venezuela|venezuelan|
peru|peruvian|bolivia|bolivian|ecuador|ecuadorian|
cuba|cuban|haiti|haitian|honduras|guatemala|
nicaragua|el salvador|panama|costa rica|
south africa|south african|nigeria|nigerian|kenya|kenyan|
ethiopia|ethiopian|zimbabwe|zimbabwean|
congo|congolese|uganda|ugandan|tanzania|
egypt|egyptian|algeria|algerian|morocco|moroccan|
tunisia|tunisian|saudi arabia|saudi|qatar|kuwait|
bahrain|oman|united arab emirates|dubai|
turkey|turkish|greece|greek|cyprus|cypriot|
serbia|serbian|croatia|croatian|bosnia|bosnian|
kosovo|albania|albanian|macedonia|montenegro|
poland|polish|hungary|hungarian|romania|romanian|
bulgaria|bulgarian|czech republic|czechia|slovakia|
slovenia|lithuania|latvia|estonia|belarus|
sweden|swedish|norway|norwegian|denmark|danish|
finland|finnish|iceland|icelandic|ireland|irish|
scotland|scottish|wales|welsh|northern ireland|
switzerland|swiss|austria|austrian|belgium|belgian|
netherlands|dutch|luxembourg|
georgia|georgian|armenia|armenian|azerbaijan|
kazakhstan|uzbekistan|kyrgyzstan|tajikistan|
mongolia|mongolian|tibet|tibetan|bhutan|
nation|nations|national|international|global|
country|countries|region|regional|province|provincial|
capital|city|cities|town|towns|village|villages|
washington|london|paris|berlin|rome|madrid|
moscow|brussels|geneva|vienna|the hague|
new york|los angeles|chicago|boston|san francisco|
sydney|melbourne|toronto|montreal|vancouver|
cairo|athens|istanbul|ankara|jakarta|bangkok
""")

_WORLD_PEOPLE = _phrase_set("""
george bush|george w bush|george w. bush|bush|
john kerry|kerry|john edwards|dick cheney|cheney|
donald rumsfeld|rumsfeld|colin powell|condoleezza rice|
paul wolfowitz|wolfowitz|john ashcroft|ashcroft|
bill clinton|hillary clinton|clinton|
barack obama|obama|joe biden|biden|
donald trump|trump|kamala harris|mike pence|
nancy pelosi|pelosi|chuck schumer|mitch mcconnell|
john mccain|mccain|mitt romney|romney|
bernie sanders|elizabeth warren|ron desantis|
nikki haley|rudy giuliani|arnold schwarzenegger|
tony blair|blair|gordon brown|david cameron|
theresa may|boris johnson|rishi sunak|keir starmer|
vladimir putin|putin|dmitry medvedev|medvedev|
boris yeltsin|mikhail gorbachev|gorbachev|
volodymyr zelensky|volodymyr zelenskyy|zelensky|zelenskyy|
viktor yushchenko|yushchenko|viktor yanukovych|yanukovych|
leonid kuchma|kuchma|alexander lukashenko|lukashenko|
alexei navalny|navalny|
jacques chirac|chirac|nicolas sarkozy|sarkozy|
francois hollande|hollande|emmanuel macron|macron|
gerhard schroeder|gerhard schröder|schroeder|schroder|
angela merkel|merkel|olaf scholz|scholz|
silvio berlusconi|berlusconi|giorgia meloni|meloni|
jose luis rodriguez zapatero|zapatero|jose maria aznar|aznar|
pedro sanchez|mark rutte|rutte|
recep tayyip erdogan|erdogan|abdullah gul|
ariel sharon|sharon|benjamin netanyahu|netanyahu|
ehud olmert|ehud barak|shimon peres|yitzhak rabin|
yasser arafat|arafat|mahmoud abbas|abbas|
ahmed qurei|ismail haniyeh|khaled meshaal|
mahmoud ahmadinejad|ahmadinejad|ali khamenei|khamenei|
mohammad khatami|khatami|hassan rouhani|rouhani|
ebrahim raisi|raisi|
saddam hussein|saddam|hussein|iyad allawi|allawi|
ibrahim al jaafari|nouri al maliki|maliki|
jalal talabani|talabani|masoud barzani|barzani|
muqtada al sadr|moqtada al sadr|al sadr|
ali al sistani|ayatollah sistani|sistani|
bashar al assad|bashar assad|assad|bashar|
hassan nasrallah|nasrallah|rafik hariri|saad hariri|
hosni mubarak|mubarak|abdel fattah el sisi|
muammar gaddafi|gaddafi|qaddafi|moammar gadhafi|gadhafi|
omar al bashir|bashir|
osama bin laden|bin laden|ayman al zawahiri|zawahiri|
abu musab al zarqawi|zarqawi|
abu bakr al baghdadi|al baghdadi|
hamid karzai|karzai|ashraf ghani|ghani|
pervez musharraf|musharraf|benazir bhutto|bhutto|
asif ali zardari|zardari|nawaz sharif|imran khan|
manmohan singh|atal bihari vajpayee|vajpayee|
sonia gandhi|rahul gandhi|narendra modi|modi|
ab vajpayee|a b vajpayee|
hu jintao|jiang zemin|wen jiabao|xi jinping|jinping|
li keqiang|li qiang|zhao ziyang|
junichiro koizumi|koizumi|shinzo abe|shigeru ishiba|
kim jong il|kim jong un|kim jong-il|kim jong-un|
kim il sung|roh moo hyun|lee myung bak|
moon jae in|yoon suk yeol|
chen shui bian|chen shui-bian|tsai ing wen|lai ching te|
megawati|susilo bambang yudhoyono|yudhoyono|
joko widodo|prabowo subianto|
thaksin shinawatra|thaksin|yingluck shinawatra|
aung san suu kyi|suu kyi|
gloria macapagal arroyo|arroyo|rodrigo duterte|duterte|
ferdinand marcos|marcos jr|
mahathir mohamad|mahathir|anwar ibrahim|
lee kuan yew|lee hsien loong|
john howard|kevin rudd|julia gillard|tony abbott|
scott morrison|anthony albanese|
helen clark|jacinda ardern|
paul martin|stephen harper|justin trudeau|trudeau|
fidel castro|castro|raul castro|
hugo chavez|chavez|nicolas maduro|maduro|
luiz inacio lula da silva|lula|dilma rousseff|
jair bolsonaro|bolsonaro|
nestor kirchner|cristina kirchner|kirchner|javier milei|milei|
vicente fox|felipe calderon|lopez obrador|claudia sheinbaum|
alvaro uribe|uribe|gustavo petro|
evo morales|morales bolivia|
nelson mandela|mandela|thabo mbeki|mbeki|
jacob zuma|zuma|cyril ramaphosa|ramaphosa|
robert mugabe|mugabe|morgan tsvangirai|tsvangirai|
mwAI kibaki|kibaki|william ruto|raila odinga|
yoweri museveni|museveni|paul kagame|kagame|
olusegun obasanjo|obasanjo|goodluck jonathan|bola tinubu|
ellen johnson sirleaf|charles taylor|
kofi annan|annan|ban ki moon|antonio guterres|guterres|
javier solana|solana|jose manuel barroso|barroso|
ursula von der leyen|von der leyen|
jens stoltenberg|stoltenberg|
pope john paul|john paul ii|pope benedict|benedict xvi|
pope francis|jorge bergoglio|
queen elizabeth|elizabeth ii|king charles|charles iii|
prince william|prince harry|kate middleton|
king abdullah|king salman|mohammed bin salman|
dalai lama|tenzin gyatso|
nobel peace prize
""")
for _p in _WORLD_PEOPLE:
    _FEATURES.setdefault(_p, {})["world"] = 4.8


# Markers used to distinguish an industry's news from incidental vocabulary.
def _markers(data):
    phrases = _phrase_set(data)
    for phrase in phrases:
        _FEATURES.setdefault(phrase, {})
    return phrases


_FINANCE = _markers("""
earnings|profit|profits|revenue|revenues|sales|shares|stock|
quarterly|fiscal|ipo|initial public offering|merger|mergers|
acquisition|acquisitions|takeover|buyout|dividend|dividends|
shareholders|investors|net income|net loss|financial results|
financial|forecast|forecasts|bankruptcy|valuation|
market capitalization|public offering|share price|share prices|
job cuts|cut jobs|layoffs|restructuring|chief executive|
ceo|business deal|deal|buys|acquires|acquired|buy|
antitrust|accounting|accounting fraud
""")
_LEGAL = _markers("""
lawsuit|lawsuits|sue|sues|sued|court|courts|judge|judges|
antitrust|anti trust|patent|patents|copyright|copyrights|
intellectual property|licensing|license|licences|
regulator|regulators|regulatory|european commission|
fine|fines|fined|settlement|litigation|appeal|appeals|
securities and exchange commission
""")
_MARKET_WIDE = _markers("""
stock market|stock markets|wall street|dow jones|
nasdaq composite|s&p 500|ftse 100|nikkei index|hang seng|
benchmark index|benchmark indices|benchmark indexes|
share market|share markets|equity markets|equity market|
asian stocks|european stocks|us stocks|u.s. stocks|
american stocks|japanese stocks|british stocks|
stocks rise|stocks fall|stocks fell|stocks climb|stocks jump|
stocks slide|stocks tumble|stocks slump|stocks rally|
stocks surge|stocks dip|stocks gain|stocks drop|stocks edge|
stocks close|stocks open|stocks end|stocks finish|
shares rise|shares fall|market roundup|stock futures|
technology stocks|tech stocks|technology shares|tech shares
""")
_MARKET_INDICES = _markers("nasdaq|dow|nikkei|ftse|dax|cac 40|sensex|nifty|hang seng|s&p")
_MARKET_MOVES = _markers("""
stocks|markets|index|indexes|indices|rally|rallied|
rises|rise|rose|falls|fall|fell|slump|slumps|slumped|
tumble|tumbled|tumbles|slide|slides|slid|surge|surges|surged|
gains|gain|gained|drop|drops|dropped|jump|jumps|jumped|
close|closes|closed|higher|lower|points|session|trading
""")
_CONCRETE_TECH = _markers("""
software|hardware|computer|computers|internet|web|
wireless|broadband|telecom|telecommunications|semiconductor|
semiconductors|chip|chips|chipmaker|chipmakers|
processor|processors|microprocessor|microprocessors|
mobile phone|mobile phones|smartphone|smartphones|
cellphone|cellphones|handset|handsets|tablet|tablets|
laptop|laptops|pc|pcs|server|servers|database|databases|
operating system|search engine|online search|
video game|video games|game console|gaming console|
cybersecurity|malware|spyware|ransomware|phishing|
screensaver|password|passwords|hacker|hackers|
cloud computing|artificial intelligence|machine learning|
chatbot|chatbots|robot|robots|robotics|nanotechnology|
programming|encryption|blockchain|ai|technology|
app|apps|data center|social media|digital music
""")
_DIGITAL_GAMES = _markers("""
video game|video games|videogame|videogames|
computer game|computer games|online game|online games|
gaming console|gaming consoles|game console|game consoles|
xbox|playstation|ps2|ps3|ps4|ps5|psp|nintendo|sega|
gamecube|game boy|wii|nintendo ds|nintendo switch|
electronic arts|activision|blizzard|ubisoft|
grand theft auto|halo 2|doom 3|half life 2|
world of warcraft|warcraft|fortnite|minecraft|the sims|
esports|e sports|virtual reality|game developer|game developers
""")
_RESEARCH = _markers("""
research|researchers|scientists|scientific|experiment|
experiments|laboratory|laboratories|study|studies|
clinical trial|clinical trials|clinical|gene|genes|dna|rna|
genome|genetics|vaccine|vaccines|vaccination|
treatment|treatments|therapy|therapies|drug trial|drug trials|
antibody|antibodies|antiviral|antibiotic|
discovery|discovered|breakthrough|findings|
new england journal of medicine|the lancet|
nature journal|science journal
""")
_HEALTH_EMERGENCY = _markers("""
outbreak|outbreaks|epidemic|pandemic|quarantine|
quarantined|health emergency|public health emergency|
bird flu|avian flu|ebola|cholera|sars|coronavirus
""")
_HARD_CRIME = _markers("""
murder|murdered|homicide|manslaughter|killed|killing|
shooting|shootings|mass shooting|gunman|gunmen|
stabbing|stabbed|rape|raped|sexual assault|kidnapped|
kidnapping|hostage|hostages|terrorist|terrorists|
bombing|bombings|suicide bombing|car bomb|assassination|
police|arrested|prison|jailed
""")
_SPORT_SPECIFIC = _markers("""
football|soccer|basketball|baseball|hockey|cricket|rugby|
tennis|golf|boxing|olympics|olympic|tournament|championship|
playoffs|playoff|quarterback|touchdown|home run|innings|
wicket|wickets|birdie|birdies|nba|nfl|nhl|mlb|fifa|uefa|
pga|atp|wta|ncaa|premier league|world cup|super bowl|
grand prix|formula one|formula 1|nascar|motogp
""")
_GENERIC_SPORT = _phrase_set("""
game|games|player|players|team|teams|win|wins|winning|
winner|winners|won|beat|beats|beaten|beating|match|matches|
season|seasons|score|scores|scored|scoring|race|races|
racing|rival|rivals|competition|competitive|league|leagues|
goal|goals|victory|victories|champion|champions
""")
_ECONOMIC_RESEARCH = _markers("""
economic research|economic study|economic report|
economists|economist|gdp|inflation|unemployment|
consumer confidence|consumer spending|retail sales|
interest rates|interest rate|federal reserve|
economic growth|economic outlook|economic forecast|
business confidence|jobless claims|trade deficit
""")
_NONTECH_FINANCIAL = _markers("""
airline|airlines|automaker|automakers|carmaker|carmakers|
retailer|retailers|supermarket|supermarkets|oil company|
oil companies|bank|banks|insurer|insurers|insurance|
drugmaker|drugmakers|pharmaceutical company|
pharmaceutical companies|brewer|brewers|hotel chain|
department store|department stores|steelmaker|
mining company|construction company|food company
""")
_NATURE_AMAZON = _markers("""
rainforest|rainforests|jungle|river|basin|deforestation|
indigenous|tribe|tribes|tribal|amazon forest|amazon forests
""")
_FRUIT_APPLE = _markers("""
orchard|orchards|apple juice|apple cider|apple crop|
apple crops|apple growers|apple harvest|apple trees|
apple tree|fruit growers|fruit harvest
""")
_PHYSICAL_PALM = _markers("palm oil|palm tree|palm trees|palm beach")
_STRONG_RESEARCH = _markers("""
scientists|scientist|researchers|researcher|
clinical trial|clinical trials|clinical|vaccine|vaccines|
gene|genes|dna|rna|genome|genetic|laboratory|laboratories|
experiment|experiments|scientific|medical research|
stem cell|stem cells|physics|biology|chemistry
""")
_COMMODITY_PRICE = _markers("""
oil price|oil prices|crude prices|fuel prices|gasoline prices|
gas prices|gold prices|commodity prices|oil futures|
crude futures|oil rises|oil falls|oil climbs|oil surges|
oil hits|oil nears|oil tops|crude oil|opec|
barrel|barrels|gold futures|wheat futures
""")
_POLITICAL_FOCUS = _markers("""
election|elections|voters|presidential|presidential campaign|
presidential election|presidential debate|campaign trail|
referendum|ballot|ballots|parliament|senate|congress|
prime minister|foreign minister|peace talks|ceasefire
""")

# A small inflection table supplements the explicitly listed vocabulary.
_ALIASES = {
    "cyberattacked": "cyberattack",
    "telecommunication": "telecommunications",
    "telecommunication's": "telecommunications",
    "stockmarkets": "stocks",
    "stockmarket": "stocks",
    "stockbrokers": "brokers",
    "stockbroker": "broker",
    "microchips": "chips",
    "microchip": "chip",
    "microbiology": "biology",
    "biochemistry": "chemistry",
    "immunology": "medicine",
    "astrophysicists": "physicists",
    "astrophysicist": "physicist",
    "neurobiology": "neuroscience",
    "palaeontologists": "paleontologists",
    "palaeontologist": "paleontologist",
    "cybercriminals": "hackers",
    "cybercriminal": "hacker",
    "cybercrime": "cybersecurity",
    "cybercrimes": "cybersecurity",
    "cyberwarfare": "cybersecurity",
    "smartwatches": "wearables",
    "smartwatch": "wearable",
    "smartglasses": "wearables",
    "telemedicine": "medical",
    "telehealth": "medical",
    "biopharmaceutical": "biotech",
    "biopharmaceuticals": "biotech",
    "bioscience": "biology",
    "biosciences": "biology",
    "nanoparticles": "nanotechnology",
    "nanoparticle": "nanotechnology",
    "cosmologists": "astronomers",
    "cosmologist": "astronomer",
    "astronautical": "space",
    "spacefaring": "space",
    "spacecrafts": "spacecraft",
    "exoplanetary": "exoplanet",
    "footballer": "football",
    "footballers": "football",
    "cricketer": "cricket",
    "cricketers": "cricket",
    "golfer": "golf",
    "golfers": "golf",
    "rugbyman": "rugby",
    "sportsperson": "athlete",
    "sportspeople": "athletes",
    "sportsmen": "athletes",
    "sportswomen": "athletes",
    "sportscaster": "sports",
    "goalscoring": "scoring",
    "ballplayer": "baseball",
    "ballplayers": "baseball",
    "playofffs": "playoffs",
    "semifinalists": "semifinals",
    "semifinalist": "semifinal",
    "quarterfinalist": "quarterfinal",
    "quarterfinalists": "quarterfinals",
    "weightlifters": "weightlifting",
    "snowboarders": "snowboarding",
    "triathletes": "triathlon",
    "medalling": "medal",
    "medaling": "medal",
    "hatchets": "weapon",
    "terroristic": "terrorist",
    "counterterrorism": "terrorism",
    "counterterrorist": "terrorist",
    "counterinsurgency": "insurgency",
    "peacekeeping": "peacekeeping",
    "peacebuilding": "peacekeeping",
    "peacekeepers": "peacekeepers",
    "warmongering": "war",
    "gunmen": "gunmen",
    "gunwoman": "gunman",
    "policeman": "police",
    "policemen": "police",
    "policewoman": "police",
    "policewomen": "police",
    "policymakers": "officials",
    "parliamentarians": "lawmakers",
    "parliamentarian": "lawmaker",
    "evacuating": "evacuation",
    "evacuate": "evacuation",
    "evacuates": "evacuation",
    "floodwaters": "flooding",
    "aftershock": "earthquake",
    "aftershocks": "earthquake",
    "temblor": "earthquake",
    "temblors": "earthquake",
    "cyclone": "hurricane",
    "cyclones": "hurricanes",
    "landslips": "landslides",
    "landslip": "landslide",
    "assailant": "gunman",
    "assailants": "gunmen",
    "kidnapper": "kidnapping",
    "kidnappers": "kidnapping",
    "kidnappings": "kidnapping",
    "abductions": "abduction",
    "hijacking": "kidnapping",
    "hijacked": "kidnapped",
    "hijackers": "kidnapping",
    "burglar": "robbery",
    "burglars": "robbery",
    "burglary": "robbery",
    "burglaries": "robbery",
    "embezzlement": "fraud",
    "embezzled": "fraud",
    "embez­zlement": "fraud",
    "electioneering": "elections",
    "reelected": "reelection",
    "reelect": "reelection",
    "inaugurated": "inauguration",
    "impeach": "impeachment",
    "impeaching": "impeachment",
    "economical": "economic",
    "macroeconomic": "economic",
    "macroeconomics": "economics",
    "microeconomics": "economics",
    "hyperinflation": "inflation",
    "disinflation": "inflation",
    "stagflation": "inflation",
    "recessionary": "recession",
    "privatize": "privatization",
    "privatise": "privatisation",
    "privatized": "privatization",
    "privatised": "privatisation",
    "bankruptcies": "bankruptcy",
    "insolvencies": "insolvency",
    "delisting": "stock",
    "delisted": "stock",
    "shareholding": "shareholders",
    "shareholdings": "shareholders",
    "shareholder's": "shareholder",
    "stockholder's": "stockholder",
    "foreclosure": "mortgage",
    "foreclosures": "mortgages",
    "refinance": "refinancing",
    "refinanced": "refinancing",
    "retailer's": "retailer",
    "retailers'": "retailers",
}

for _alias, _base in _ALIASES.items():
    _base_key = _words(_base)
    _alias_key = _words(_alias)
    if _base_key in _FEATURES and _alias_key not in _FEATURES:
        _FEATURES[_alias_key] = dict(_FEATURES[_base_key])

_FIRST = {}
for _phrase in _FEATURES:
    _FIRST.setdefault(_phrase[0], []).append(_phrase)


def _extract_text(state):
    if isinstance(state, str):
        return state
    if isinstance(state, dict):
        pieces = []
        for key in ("headline", "title", "text", "description", "body", "content", "summary"):
            value = state.get(key)
            if isinstance(value, str) and value and value not in pieces:
                pieces.append(value)
        if pieces:
            return "\n".join(pieces)
        for key in ("article", "news", "input", "state"):
            if key in state:
                value = _extract_text(state[key])
                if value:
                    return value
        return ""
    if isinstance(state, (list, tuple)):
        return "\n".join(value for value in state if isinstance(value, str))
    return ""


def _find_hits(tokens):
    hits = {}
    length = len(tokens)
    for index, token in enumerate(tokens):
        for phrase in _FIRST.get(token, ()):
            size = len(phrase)
            if index + size <= length and tokens[index:index + size] == phrase:
                previous = hits.get(phrase)
                if previous is None:
                    hits[phrase] = [index, 1]
                else:
                    previous[1] += 1
    return hits


def _has(hits, group):
    return any(phrase in hits for phrase in group)


def _first_position(hits, group):
    positions = [hits[phrase][0] for phrase in group if phrase in hits]
    return min(positions) if positions else 1000000


def _count_present(hits, group):
    return sum(1 for phrase in group if phrase in hits)


def _position_weight(position):
    if position < 9:
        return 1.65
    if position < 20:
        return 1.35
    if position < 40:
        return 1.12
    return 1.0


def predict(state):
    text = _extract_text(state)
    tokens = _words(text)
    if not tokens:
        return {"answer": "world"}

    hits = _find_hits(tokens)

    # A proper name can instead denote a fruit, a river, or a tree.
    ignored = set()
    if _has(hits, _NATURE_AMAZON) and not _has(hits, _CONCRETE_TECH):
        ignored.add(("amazon",))
    if _has(hits, _FRUIT_APPLE) and not _has(hits, _CONCRETE_TECH):
        ignored.add(("apple",))
    if _has(hits, _PHYSICAL_PALM):
        ignored.add(("palm",))
    for phrase in ignored:
        hits.pop(phrase, None)

    scores = {"world": 0.4, "business": 0.1, "sports": 0.0, "sci_tech": 0.0}
    generic_sport_score = 0.0
    for phrase, (position, count) in hits.items():
        multiplier = _position_weight(position) * (1.0 + 0.13 * min(count - 1, 3))
        for category, weight in _FEATURES[phrase].items():
            contribution = weight * multiplier
            scores[category] += contribution
            if category == "sports" and phrase in _GENERIC_SPORT:
                generic_sport_score += contribution

    tech_company = _has(hits, _TECH_COMPANIES)
    company_position = _first_position(hits, _TECH_COMPANIES)
    tech_product = _has(hits, _TECH_PRODUCTS)
    product_position = _first_position(hits, _TECH_PRODUCTS)
    tech_context = _count_present(hits, _CONCRETE_TECH)
    finance_context = _count_present(hits, _FINANCE)
    legal_context = _has(hits, _LEGAL)
    sport_entity = _has(hits, _SPORT_ENTITIES)
    sport_entity_position = _first_position(hits, _SPORT_ENTITIES)
    sport_specific = _count_present(hits, _SPORT_SPECIFIC)
    research_context = _count_present(hits, _RESEARCH)

    # Index movements concern the market as a whole, not a technology
    # manufacturer that happens to be named among its constituents.
    market_position = _first_position(hits, _MARKET_WIDE)
    market_focus = market_position < 17
    if market_focus:
        only_individual_shares = not any(
            phrase in hits and hits[phrase][0] < 17
            for phrase in _MARKET_WIDE
            if phrase not in {("shares", "rise"), ("shares", "fall")}
        )
        if only_individual_shares and tech_company:
            market_focus = False
    if not market_focus:
        index_position = _first_position(hits, _MARKET_INDICES)
        if index_position < 8 and _has(hits, _MARKET_MOVES):
            market_focus = True

    if market_focus:
        scores["business"] += 11.0
        if tech_company and not tech_product and tech_context < 3:
            scores["sci_tech"] *= 0.72

    # Sector-specific company reporting remains science/technology, even
    # when the article discusses profits, an acquisition, or litigation.
    company_focus = (
        tech_company and
        (company_position < 23 or tech_context >= 2 or tech_product)
    )
    if company_focus and not market_focus:
        if finance_context:
            redirected = min(24.0, scores["business"] * 0.58)
            scores["sci_tech"] += redirected + 2.5
            scores["business"] *= 0.64
        if legal_context:
            scores["sci_tech"] += min(14.0, scores["world"] * 0.46) + 2.5
            if not _has(hits, _HARD_CRIME):
                scores["world"] *= 0.88
    elif tech_product and product_position < 22 and finance_context and not market_focus:
        scores["sci_tech"] += min(13.0, scores["business"] * 0.35)
        scores["business"] *= 0.80

    if tech_context >= 3 and finance_context and not market_focus:
        scores["sci_tech"] += min(10.0, scores["business"] * 0.20)

    # Playing a video game, a console release and the game industry are
    # technology stories, rather than sporting contests.
    digital_games = _has(hits, _DIGITAL_GAMES)
    if digital_games:
        scores["sci_tech"] += 7.0
        scores["sports"] = max(0.0, scores["sports"] - generic_sport_score * 0.85)
        if not sport_entity and sport_specific <= 1:
            scores["sports"] *= 0.55
        if finance_context and not market_focus:
            scores["sci_tech"] += min(10.0, scores["business"] * 0.25)

    # Financial terms in transfers, player contracts and club transactions
    # should not turn otherwise unambiguous sports reports into business.
    sports_focus = (
        sport_specific >= 2 or
        (sport_entity and sport_entity_position < 20 and sport_specific >= 1)
    )
    if sports_focus and not digital_games:
        if finance_context and not _has(hits, _NONTECH_FINANCIAL):
            scores["sports"] += min(12.0, scores["business"] * 0.35)
            scores["business"] *= 0.83
        if re.search(r"\b\d{1,3}\s*[-–]\s*\d{1,3}\b", text):
            scores["sports"] += 4.0
    elif scores["sports"] >= 5.0 and re.search(
        r"\b[0-7]\s*[-–]\s*[0-7](?:\s*,?\s+[0-7]\s*[-–]\s*[0-7])+\b", text
    ):
        scores["sports"] += 5.0

    # Remove metaphorical "games", "wins", "races" and "teams" when there
    # is no sporting subject and another domain has substantive evidence.
    if not sport_entity and sport_specific == 0:
        other = max(scores["world"], scores["business"], scores["sci_tech"])
        if other >= 8.0:
            scores["sports"] = max(
                0.0, scores["sports"] - generic_sport_score * 0.65
            )

    # Medical product research differs from the financial performance of
    # a pharmaceutical firm, and from a public-health emergency.
    strong_research = _count_present(hits, _STRONG_RESEARCH)
    if strong_research >= 2:
        scores["sci_tech"] += 4.0
    if _has(hits, _HEALTH_EMERGENCY):
        if research_context == 0 or (
            strong_research == 0 and research_context <= 1
        ):
            scores["world"] += 6.5
            if _has(hits, _HARD_CRIME) or any(
                word in tokens for word in ("killed", "deaths", "died", "dead", "quarantine")
            ):
                scores["world"] += 4.0
        elif strong_research >= 1:
            scores["sci_tech"] += 4.0

    # Economic reports and economic research remain business, whereas
    # a political debate about economic policy remains politics.
    economic_count = _count_present(hits, _ECONOMIC_RESEARCH)
    if economic_count >= 2:
        scores["business"] += 5.0
        if not strong_research and not tech_company and not tech_product:
            scores["sci_tech"] *= 0.82
    if _first_position(hits, _POLITICAL_FOCUS) < 12:
        if _has(hits, _WORLD_PEOPLE):
            scores["world"] += 4.0

    commodity_count = _count_present(hits, _COMMODITY_PRICE)
    if commodity_count >= 2:
        scores["business"] += 5.0
    if _has(hits, _NONTECH_FINANCIAL) and finance_context >= 2:
        if not company_focus and not tech_product:
            scores["business"] += 4.0

    # Serious violence/disasters can mention companies, athletes or
    # communications equipment without being industry or sports stories.
    crime_count = _count_present(hits, _HARD_CRIME)
    crime_position = _first_position(hits, _HARD_CRIME)
    if crime_count >= 3 and crime_position < 16:
        if not (company_focus and legal_context and tech_context >= 2):
            scores["world"] += 5.0

    # Price and earnings formats provide a little extra evidence, but
    # are not allowed to outweigh the technology-company distinction.
    if re.search(r"(?:[$€£]\s*\d|\b\d+(?:\.\d+)?\s*(?:billion|million)\b)", text.lower()):
        if finance_context or _has(hits, _NONTECH_FINANCIAL):
            scores["business"] += 1.5

    answer = max(_CATEGORIES, key=lambda category: scores[category])
    if scores[answer] < 2.0:
        answer = "world"
    return {"answer": answer}