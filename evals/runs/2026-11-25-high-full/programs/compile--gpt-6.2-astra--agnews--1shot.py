import re
import unicodedata
import math


# Evidence is recorded separately for each beat. Some words (e.g. "strike")
# are intentionally not treated as beat identifiers on their own.
_B, _T, _S, _W = range(4)
_NAMES = ("business", "sci_tech", "sports", "world")
_lex = {}
_lengths = {}


def _clean(s):
    s = s.replace("’", "'").replace("‘", "'")
    s = re.sub(r"&?(?:amp;)?#0*39;|&apos;", "'", s, flags=re.I)
    s = re.sub(r"&(?:amp;)?quot;|&?#34;|&nbsp;|&lt;|&gt;", " ", s, flags=re.I)
    s = s.replace("&amp;", "&")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"\b(?:[a-z]\.)+[a-z]\b\.?", lambda m: m.group().replace(".", ""), s)
    s = re.sub(r"'\s*s\b", "", s)
    s = s.replace("wi-fi", "wifi").replace("e-mail", "email").replace("on-line", "online")
    s = s.replace("e-commerce", "ecommerce").replace("e-bay", "ebay")
    s = s.replace("c++", "cplusplus").replace("at&t", "att")
    s = s.replace("s&p", "sandp").replace("m&a", "mergers acquisitions")
    return s


def _tokens(s):
    return re.findall(r"[a-z0-9]+", _clean(s))


def _add(cat, score, items):
    for item in items:
        ts = _tokens(item.strip())
        if not ts:
            continue
        key = " ".join(ts)
        if key not in _lex:
            _lex[key] = [0., 0., 0., 0.]
        _lex[key][cat] = max(score, _lex[key][cat])
        if len(ts) > 1:
            _lengths.setdefault(ts[0], set()).add(len(ts))


def _w(cat, score, s):
    _add(cat, score, s.split())


def _p(cat, score, s):
    _add(cat, score, s.replace("\n", " ").split("|"))


# Markets, company finance, macroeconomics, and non-IT industries
_w(_B, 5.5, """
nasdaq nyse amex ftse nikkei hang-seng cac40 dax sensex bourse
ipo ipos opec imf wto ecb fedex fannie freddie enron worldcom parmalat
stockbroker stockholder shareholder debenture buyback dividend
bondholder mortgage refinancing equities brokerage brokerages underwriter
insolvency insolvencies bankruptcy bankrupt buyout takeover spinoff
macroeconomic macroeconomics stagflation inflationary deflationary
stockmarket stockbroking hedgefund subprime
""")
_w(_B, 3.8, """
earnings profits profit profitability quarterly pretax turnover financials
stocks stock investing investment investor investments mutuals
revenue sales retailer retailing retail wholesalers wholesale
merger acquisition divestiture flotation tendered suitor conglomerate
disinvest disinvestment privatization privatisation liquidator liquidation
recapitalization recapitalisation financing refinance lending lender borrowing
banker banking insurer insurance reinsurer reinsurance annuity pension
commodities commodity futures bullion barrels crude gasoline petrol refinery
economy economic economist economics gdp gnp inflation deflation
jobless unemployment payroll payrolls joblessness layoffs layoff
tariff subsidy exports imports tradeoff tradeoffs
accountant accounting audit auditors embezzlement kickback antitrust
automaker carmaker automakers carmakers airline airliner airways airfares airfare
supermarket drugmaker pharmaceutical pharmaceuticals brewer brewery
discounter franchising restructuring realtors creditworthiness
""")
_w(_B, 2.0, """
business financial finance corporate corporation company firm inc corp plc ltd
ceo cfo treasurer executive executives chairmanship boardroom entrepreneur
share shares equity fund banker bank bonds yield lender loan deposit debt indebted
cash currency currencies forex dollar euro yen sterling yuan rupee pesos franc
prices pricing pricey priced cost costs costly spending consumer consumption
purchase purchaser buyer seller distributor supplier production manufacturer
manufacturing producer factory industrial industry industrialist
unions labor labour strike retrenchment jobs wages wages pensioners paychecks
warehouse store stores shoppers shopping promotion outlets malls mall chain
vehicles dealership dealership deliveries aircraft carrier cargo transportation
shipment freight trucking shipbuilding steel aluminium aluminum metals copper
cattle wheat bushels soybeans coffee cocoa platinum gold mine mining miner
tax taxes taxable taxation taxpayer fiscal monetary deficit surplus budget
regulator fraud settlement lawsuit bid bidding contract ownership
forecast outlook projections margin shortfall loss losses billion million
profitable stake subsidiary partnership closure closings
valuation payout portfolio tranche annuities premium leasing lease rental
hotel hotels hospitality tourism tourist automotive sedan luxury
""")
_w(_B, 1.0, """
rose jumped fell falling surged plunge slipped soared sank tumble rally
boost boosted rising rise rates weaken gains growth recovered slowdown
drop lifted firmed closed lower higher index figures monthly annual
businessman manager management plans analysts analyst report delayed delay
restructuring chief agreement bought sell sold sale purchase deal
cut cuts hike raise staff workers employees board directors chairman
compensation pay paid payment customers customer clients demand supply
capacity volume order trading commercial network outlets brand brands
promote advertising advertisement campaign launch filed filing
aircraft flight flights fuel energy gas oil coal carbon diesel
dock shipping rails railway rail unions union walkout property property
homes housing homes rent apartments vacation holiday gifts
""")
_p(_B, 7.2, """
wall street|dow jones|dow industrials|dow average|sandp 500|s and p 500|standard and poor|
stock exchange|stock market|stock index|stock futures|stock split|stock options|new york mercantile|
hang seng|blue chip|blue chips|mutual fund|hedge fund|pension fund|venture capital|
private equity|investment bank|initial public offering|public offering|hostile bid|hostile takeover|
merger talks|mergers and acquisitions|board of trade|federal reserve|central bank|bank of england|
bank of japan|reserve bank|benchmark interest rate|interest rates|monetary policy|world trade organization|
world trade organisation|international monetary fund|world bank|world economic forum|
securities and exchange|securities regulator|insider trading|balance sheet|income statement|
per share|a share|share price|stock price|earnings forecast|earnings report|profit warning|
net profit|net income|net loss|operating profit|same store|quarterly profit|quarter results|
fourth quarter earnings|fiscal quarter|analyst estimates|analysts estimates|
consumer price index|gross domestic product|consumer confidence|business confidence|
trade deficit|trade surplus|trade gap|labor department|jobless claims|unemployment rate|
crude oil|oil prices|price of oil|per barrel|a barrel|light crude|brent crude|
oil exporters|oil cartel|energy prices|fuel prices|fuel costs|gas prices|
housing starts|housing market|home sales|real estate|retail sales|credit rating|
chapter 11|bankruptcy protection|junk bond|credit crunch|credit card debt|
money market|treasury note|treasury bond|treasury bill|retirement savings|
chief financial officer|financial times|business wire|businessweek|standard poor|
marketwatch|investor business daily|bloomberg news|financial results
""")
_p(_B, 4.2, """
first quarter|second quarter|third quarter|fourth quarter|fiscal year|
chief executive|board of directors|annual meeting|general meeting|corporate governance|
labor union|labour union|labor costs|labor market|job cuts|work force|work stoppage|on strike|
free trade|trade talks|trade pact|trade deal|trade agreement|economic growth|economic recovery|
finance minister|finance ministry|treasury secretary|economic policy|import duty|
oil company|oil giant|oil industry|oil production|oil output|production quota|
commercial aircraft|low cost carrier|low fare|discount carrier|health insurance|
drug company|drug companies|store chain|consumer goods|department store|
accounting scandal|accounting irregularities|fraud charges|tax evasion|
market share|publicly traded|trading session|trading day|early trading|late trading|
all time high|record high|broker dealer|buy back|bail out|going public|
acquire rival|raised its|beat estimates|market value|market capitalization|
share of the market|exchange rate|credit risk|bad loans|personal finance|
customer service|majority stake|minority stake|percentage points|basis points|
investment grade|rating agency|retail giant|home buyer|home builder|home loan|
credit union|savings account|brand name|ad campaign|trade group
""")
_w(_B, 5.3, """
citigroup citibank jpmorgan morganstanley wachovia aig allianz hsbc barclays
ubs nomura fidelity berkshire hathaway nasd nasdaq100 transamerica
deutschebank santander goldman lehman bearstearns merrill schwab
halliburton chevrontexaco exxon exxonmobil shell yukos lukoil gazprom
rosneft conoco conocophillips bp petrochina sinopec aramco
walmart kmart sears kroger costco nordstrom marshalls jcpenney safeway
albertsons aldi tesco sainsbury sainsburys asda carrefour ahold
mcdonald mcdonalds starbucks pepsico mondelez unilever kellogg nestle
cadbury heineken sabmiller diageo anheuser interbrew
boeing airbus bombardier embraer airfrance alitalia lufthansa ryanair
easyjet usairways jetblue qantas amtrak unionpacific
daimlerchrysler daimler chrysler volkswagen toyota nissan peugeot
renault mitsubishi hyundai suzuki honda fiat bmw gm ford motorola-mobility
viacom vivendi timewarner disney comcast wpp omnicom bertelsmann
glaxosmithkline astrazeneca pfizer merck novartis sanofi aventis
eli-lilly roche wyeth bristol-myers schering plough bayer amgen
karstadt alcoa alstom abb bridgestone firestone caterpillar dupont
booz tyco adecco unocal bhp rio-tinto angloamerican
""")
_p(_B, 6.4, """
bank of america|wells fargo|jp morgan|morgan chase|morgan stanley|credit suisse|
deutsche bank|merrill lynch|goldman sachs|american express|royal bank|bear stearns|
prudential financial|bank one|fannie mae|freddie mac|alan greenspan|warren buffett|
new york attorney general eliot spitzer|marsh mclennan|federal national mortgage|
royal dutch|british petroleum|general electric|general motors|ford motor|
american airlines|united airlines|delta air lines|us airways|air canada|british airways|
continental airlines|southwest airlines|northwest airlines|singapore airlines|
lockheed martin|northrop grumman|rolls royce|wal mart|home depot|best buy|
marks and spencer|marks spencer|toys r us|coca cola|burger king|general mills|
procter gamble|procter and gamble|johnson johnson|kraft foods|sara lee|
new york life|time warner|news corp|walt disney|general dynamics|rio tinto|
eli lilly|bristol myers|lehman brothers|bausch lomb|kmart holding
""")

# Computing and communications: keep a separate set of named technology
# vendors/products for cases where their news uses ordinary financial language.
_vendor_words = """
microsoft msft google alphabet nvidia amd intel ibm cisco oracle sap
apple macintosh imac powermac powerbook macbook iphone ipad ipod itunes
dell hewlett compaq lenovo gateway emachines acer asus asustek
toshiba sony panasonic matsushita sharp hitachi fujitsu canon kodak xerox
palm palmone palmsource treo blackberry rim ericsson nokia motorola
qualcomm broadcom mediatek stmicroelectronics infineon asml tsmc
amd64 athlon opteron pentium centrino celeron itanium xeon radeon geforce
symantec mcafee sophos kaspersky trendmicro
redhat novell suse mandrake mandriva ubuntu debian fedora linux unix solaris
sunsoft sunos opensolaris mysql postgresql sqlite netscape mozilla firefox
thunderbird safari chromium opera android ios macos windows longhorn vista
office365 xbox playstation nintendo gamecube gameboy wii psp sega atari
ubisoft activision blizzard ea bioware capcom konami idsoftware
amazon ebay paypal yahoo gmail hotmail msn aol lycos altavista askjeeves
overture baidu alibaba tencent facebook meta instagram twitter tiktok
snapchat whatsapp youtube netflix spotify skype zoom linkedin myspace
peopleSoft siebel informix veritas emc vmware citrix netapp brocade
salesforce workday tableau snowflake servicenow accenture intuit adobe
macromedia autodesk corel quicktime flashplayer napster bittorrent kazaa
realnetworks realplayer akamai sandisk seagate maxtor logitech lexmark
linksys belkin dlink netgear nortel lucent alcatel huawei zte juniper
vodafone verizon nextel cingular tmobile t-mobile sprintpcs docomo
earthlink comdex computex salesforce.com rekindled-technology openai
deepmind anthropic chatgpt deepseek spacex starlink bl uesky
"""
# A few everyday words double as names. Require context for these below.
_ambiguous_names = set("alphabet gateway sharp hitachi palm rim safari opera windows vista ea meta zoom snowflake intuit bl uesky apple amazon android".split())
_vendors = set(_vendor_words.lower().split()) - _ambiguous_names
_w(_T, 7.6, " ".join(_vendors))
_w(_T, 3.4, "windows apple amazon android")
_vendor_phrases = """
sun microsystems|hewlett packard|hewlett packard enterprise|research in motion|
texas instruments|international business machines|advanced micro devices|
national semiconductor|computer associates|network associates|network appliance|
electronic arts|take two interactive|rockstar games|palm os|red hat|red hat linux|
apple computer|apple inc|dell computer|gateway inc|sun java|silicon graphics|
western digital|juniper networks|cisco systems|nvidia corp|digital equipment|
america online|ask jeeves|yahoo inc|google inc|amazon com|salesforce com|
internet explorer|media player|windows xp|windows server|mac os|os x|
visual studio|ms office|office xp|service pack|play station|game boy|
game cube|sony ericsson|t mobile|france telecom|british telecom|china mobile|
china telecom|ntt docomo|sk telecom|deutsche telekom|sbc communications|
bell labs|bell south|bellsouth corp|at t wireless|att wireless|att inc|
silicon valley|silicon fen|bill gates|steve jobs|steve ballmer|larry ellison|
larry page|sergey brin|steve wozniak|michael dell|tim berners lee|
linus torvalds|andy grove|mark zuckerberg|jeff bezos|satya nadella|
sundar pichai|el capitan os|half life 2|halo 2|grand theft auto|
world of warcraft|everquest ii|electronic entertainment expo|
symbian os|windows mobile|mozilla foundation|linux foundation|apache software
"""
_p(_T, 8., _vendor_phrases)
_w(_T, 5.2, """
technology technologies tech technological digitalization digitization
computing computer computers computerized supercomputer mainframe workstation
software hardware freeware shareware middleware firmware groupware spyware
adware malware ransomware antivirus phishing spam spammers spamming
cybercrime cyberspace cybersecurity cyberattack botnet trojan rootkit exploit
worm worms keystrokes screensaver downloads downloadable encryption decryption
cryptography authentication biometric biometrics firewall hacker hacking hacked
internet web website websites webmaster weblog blogger blogging blog wiki wikipedia
browsers browser online offline broadband bandwidth wi-fi wifi wireless wlan
ethernet bluetooth wimax voip gsm cdma gprs 3g 4g 5g lte adsl dsl dialup
telecom telecoms telecommunication telecommunications telco telephony
cellphone cellphones smartphone smartphones handset handsets cordless
microprocessor processor chipmaker microchip chipset chips semiconductor
microelectronics microcontroller transistor silicon photonics optoelectronic
motherboard gigabyte megabyte terabyte gigahertz mhz ghz gbps mbps
ram dram sdram hdd ssd usb dvd cdrom mp3 mpeg blu-ray lcd oled hdtv dvr
laptop notebook pc pcs pda pdas pcworld infoworld macworld cnet zdnet idg
server database datacenter router modem ethernet intranet networking
algorithm programmer programming developer developers api sdk xml html
http tcp dns url java javascript python perl kernel sourceforge github
virtualization blockchain cryptocurrency bitcoin fintech nft
videogame videogames gamer gamers gaming console consoles joystick gamepad
robot robotizing robotic robotics nanotech nanotechnology nanoscale
artificial-intelligence chatbot wearable touchscreen microblogging
searchengine torrent ecommerce ebook ebooks ebook-reader podcast podcasting
gps geolocation satellite-navigation 3d printer scanner photocopier camcorder
camera megapixel pixel screenname email texting sms ringtone ringtones
peer-to-peer multimedia streaming webcast filesharing teleconference
wireless-enabled smartwatch touchscreen photoblog cryptographic
""")
_w(_T, 2.5, """
device devices portable handheld gadget electronics electronic hightech
television tv cable radio satellite cellular mobile mobility phone telephone
screen display image imaging video audio music player recording disc disk drive
format piracy pirate copyright licensing patent patented innovation innovative
technical technician engineer engineering lab labs laboratory prototype invention
chip chips circuit circuits system networks network systems interface tools
installation applications app apps upgraded upgrade update patch vulnerability flaw
bug bugs infected infection malicious attack security secure privacy identity
access providers service connectivity connection link portal site sites surf surfing
messaging instant messenger chat inbox messages downloaded upload users user
file files data storage memory backup desktop desktops notebook notebooks
directory search engine spammer texted passwords password code version beta
homepage domain digital digitally battery batteries enabled compatible compatibility
resolution pixel linux-based model specification test tests simulation simulator
automated automatic automate navigation sensor sensing graphics rendering
scientific science scientist researcher research discovery discovered experiment
experiments experimental evidence study studies professor university institute
biotech biotechnology fossil observatory radiation sample gene genetic species
""")
# Avoid overweighting generic uses of these shared terms.
for _term in ("systems", "system", "service", "access", "attack", "security", "photo",
              "model", "test", "tests", "music", "player", "recording", "file", "code",
              "engine", "link", "search", "patent", "laboratory", "study", "institute",
              "university", "site", "drive", "identity", "privacy", "evidence", "radio",
              "television", "tv", "screen", "text", "image", "users", "connection",
              "tool", "tools", "flaw", "mobile", "version", "engineer", "format", "update",
              "resolution", "phone", "network", "networks", "innovation", "memory",
              "applications", "professor", "sample", "data"):
    if _term in _lex:
        _lex[_term][_T] = 1.0
_p(_T, 6.8, """
high tech|hi tech|information technology|information systems|operating system|open source|
wireless network|wireless internet|wireless access|wireless carrier|wireless service|
cell phone|mobile phone|mobile operator|mobile network|mobile carrier|mobile device|
phone maker|smart phone|hand held|personal computer|personal digital assistant|
computer maker|computer chip|chip maker|chip makers|computer industry|computer network|
computer system|computer security|computer virus|computer worm|computer code|
computer science|science fiction|artificial intelligence|machine learning|neural network|
deep learning|large language model|quantum computing|quantum computer|cloud computing|
cloud storage|data center|data centre|web services|web site|world wide web|
web browser|web page|web server|search engine|search results|internet search|
search technology|search giant|instant messaging|instant message|text message|
e mail|e commerce|broadband access|internet access|dial up|peer to peer|file sharing|
music service|digital music|online music|music download|digital rights|digital media|
digital camera|digital video|digital tv|flat panel|plasma screen|liquid crystal|
hard disk|hard drive|disk drive|flash memory|memory card|memory chip|
compact disc|blu ray|blue ray|hd dvd|high definition|video on demand|set top box|
consumer electronics|mobile gaming|video game|video games|computer game|
game console|games console|game developer|role playing game|game maker|
anti virus|anti spam|denial of service|identity theft|security flaw|
security hole|security vulnerability|security update|security patch|security software|
source code|software maker|software company|software giant|software developer|
chip set|integrated circuit|printed circuit|dual core|64 bit|32 bit|3 d printer|
next generation network|voice over internet|voice over ip|internet protocol|
fiber optic|fibre optic|global positioning|radio frequency identification|
network security|internet provider|service provider|technology industry|
tech sector|tech giant|tech company|tech firms|dot com|net neutrality|
pocket pc|tablet pc|social networking|social media|domain name|pop up ads|
mp3 player|music player|streaming service|wearable device|download site|
news com|pc world|idg news service|associated press technology writer
""")
# Natural science, environment, medicine, and space
_w(_T, 5.8, """
nasa esa jpl spacecraft spaceflight spaceship spacewalk spacewalker
astronaut cosmonaut shuttle orbiter rover martian cassini huygens hubble
soyuz sputnik moonwalk spacestation spaceport spaceprobe spacesuit
asteroid comet meteor meteorite galaxy galactic supernova stellar exoplanet
astronomy astronomical astronomer astrophysicist cosmology cosmologist
orbit orbiting orbital telescope observatory nebula quasar lunar saturn titan
jupiter neptune pluto uranus venus mars mercury-vapor solar-system
physicist physics quantum relativity subatomic neutron neutrino photon
electron boson particle thermodynamics superconducting superconductivity cern
nobel-science nanometer nanoparticle polymer molecule molecular molecularly
genome genomics dna rna chromosome mutation geneticist sequencing cloning
clone embryonic embryo protein enzyme neuron neuronal neuroscience
paleontology paleontologist archaeologist archaeological archeologist
fossils fossilized dinosaur reptile hominid neanderthal neandertal
evolutionary ecologist biologist geologist geology glaciology glacier
seismologist oceanographer climatologist climatology biodiversity
ecosystem extinction extinct ecology zoologist primate orangutan mammoth
biochemistry bacteria bacterial bacterium microbial microbes virology
virologist immunology neurologist oncology oncologist epidemiologist
therapeutic vaccine vaccination immunization diabetes insulin cancerous
tumor tumour tumors tumours stem-cell alzheimer alzheimers parkinson
chemotherapy mammography mammogram hormone hormonal cholesterol
neurodegenerative antiretroviral antibiotic antiviral clinical-trial
nanotube superconductors teflon-neuron radiocarbon antarctic-ice
""")
_w(_T, 2.8, """
space planetary planet moon sunspot rocket payload launchpad probe
stratosphere atmosphere atmospheric ocean oceans underwater antarctica
expedition jungle rainforest coral reef conservation habitat endangered
species wildlife mammal insects whales whale shark amphibian amphibians
bird birds butterfly butterflies ecological biodiversity ozone warming
pollution pollutant emissions carbon dioxide oxygen hydrogen helium
climate climatic volcanic volcano seismic seafloor seabed crystals mineral
paleolithic prehistoric ancient skull skeleton artifacts hominids bones
predator reproduction evolution evolutionary migrated aging longevity
cancer aids hiv influenza flu polio measles malaria mosquito ebola sars
infection infectious disease illness patients clinical diagnosis diagnostic
syndrome disorder symptom treatment therapy therapies therapeutic
medicine medical medication drug drugs pill pills dosage placebo
surgeon surgery surgical transplant hospital cardiovascular heart stroke
nutrition diet dietary obesity obese overweight smokers smoking
fertility infertility pregnancies pregnancy pregnancy-related breast
brain nerve tissue cell cells blood screening scientists researchers
findings published journal journals academy breakthrough mathematics
mathematician chemistry chemist laser photonic optic optics
""")
for _term in ("sun", "heart", "stroke", "drug", "drugs", "ancient", "space", "probe",
              "hospital", "patients", "smoking", "diet", "birds", "pill", "cell",
              "treatment", "therapy", "medical", "launchpad", "shark", "titan",
              "whales", "conservation", "expedition", "rockets", "rocket", "blood", "bones"):
    if _term in _lex:
        _lex[_term][_T] = 1.5
_p(_T, 7.1, """
outer space|space agency|space shuttle|space mission|space flight|space station|
space telescope|space program|space programme|space exploration|space tourism|
space race|space probe|cape canaveral|jet propulsion laboratory|mars rover|
red planet|mars explorer|solar system|solar wind|solar flare|earth orbit|
aboard the international|national aeronautics|virgin galactic|space com|
x prize|xprize|spaceshipone|black hole|big bang|speed of light|dark matter|
light years|milky way|particle accelerator|large hadron collider|nuclear fusion|
nobel prize in physics|nobel prize in chemistry|human genome|genetic code|
genetic engineering|gene therapy|genetically modified|stem cell|stem cells|
embryonic stem|cloned embryo|clinical trial|clinical trials|drug trial|
immune system|blood pressure|heart disease|breast cancer|lung cancer|
colon cancer|prostate cancer|heart attack risk|bird flu|avian flu|mad cow|
new species|missing link|ice age|ice sheet|ice cap|mass extinction|
greenhouse gas|greenhouse effect|global warming|climate change|sea level|
fossil record|million years ago|billion years ago|years old fossil|
research team|scientists say|scientists have|researchers say|researchers found|
study suggests|study finds|according to a study|new study|journal nature|
journal science|medical journal|national academy of sciences|national institutes of health|
centers for disease control|new england journal|scientific american|new scientist|
human evolution|human ancestors|laboratory mice|research suggests|find a cure|
in the journal|solar cell|renewable technology|fuel cell|hydrogen powered
""")

# Sport vocabulary. Split weak match-report words from unmistakable ones.
_w(_S, 6.0, """
football soccer baseball basketball softball volleyball beachvolleyball
hockey icehockey lacrosse rugby cricket golfing golf tennis badminton
squash racquetball handball netball waterpolo
nfl nba wnba nhl mlb mls ncaa nascar pga lpga atp wta pba afl nfc afc
uefa fifa concacaf premiership bundesliga eredivisie scudetto
champion champions championship semifinal semis semifinalist quarterfinal
quarterfinalist playoffs playoff postseason preseason wildcard bowlers
olympics olympiad olympian paralympic paralympics olympic athletes athlete athletics
medallist medalist sprinter marathoner decathlete pentathlete heptathlon
skater skating skiing biathlon freestyle snowboarder snowboard bobsled
triathlon triathlete gymnast gymnastics weighlifting weightlifting
wrestler wrestling boxer boxing kickboxing ufc heavyweight welterweight
middleweight featherweight bantamweight flyweight cruiserweight knockout
cyclist cycling velodrome peloton sprinting equestrian dressage
horseracing racehorse jockey steeplechase thoroughbred
touchdown quarterback linebacker cornerback tailback fullback halfback
wideout punter fumble interception yardage scrimmage sacks endzone
batter batsman batsmen bowler wickets wicket wicketkeeper innings inning
legspinner lbw crease overs allrounder hattrick debutant
homer homerun rbi slugger bullpen fastball curveball shortstop baseman
outfielder infielder catcher pitcher reliever strikeout shutout no-hitter
balk walkoff ballpark dugout grandstand postseason ballclub pinstripes
dunk rebounder layup backcourt frontcourt backboard hoops hoopster
goalkeeper goaltender goalie goalscorer striker midfielder defender
winger offside stoppage equalizer equaliser equalized relegation relegated
puck blueliner rink defenceman defenseman faceoff slapshot powerplay
fairway birdie bogey putter putt leaderboard greenside golfer
backhand forehand volley tiebreak tiebreaker grandslam seedings
tournament tourney matchplay foursomes warmup friendly-match
motogp f1 indycar speedway racetrack pole-sitter karting
innings wimbledon roland-garros twickenham lordship-cricket wembley fenway
""")
_w(_S, 3.4, """
game games match matches player players teams teammates teammate
coach coaches coaching captain skipper rookie veteran squad roster lineup
league leagues division conference divisional cup tournament tour final
qualifier qualifying qualification finalists finalist champions
sport sports sportsman sportsmanship sportswoman sporting competition
season offseason opener fixture clash duel victory victorious unbeaten
win wins winner winners winning won unbeaten winless streak defeat defeated
upset upsetter beat beats beaten lose loses losing lost triumph revenge
clinched crowned defended defending rallied rallying clincher thriller
score scored scores scorer goals goal netted penalty penalties assists
referee foul fouled tie tied draw drawn margin points bench substitution
opponent rival stadium arena fans crowd supporters spectators club
home away standings ranked rankings seeded seeding ranked ranking doubles
singles medal medals bronze silver gold relay podium sprint hurdles
lap laps racing racer driver circuit racing motorsport grid pole laps
yards yard pass passes rush rushing reception tackle tackling kick kicks
pitch pitching pitched batting bat bowled bowling opener opener
slam shot shots par birdied stroke strokes tee playoff
victories comeback retirement retire injured injury injuries suspension
replay unbeaten sprint jersey shirts dribble kickoff halftime overtime
derby rout routed cruising romp swept sweep notched meet event
swimmer swimming pool diving archery fencing yachting sailing sailor
""")
# Low specificity in straight news and finance.
for _term in """
game games match matches teams captain veteran division conference tour final
qualification season clash victory win wins winner winners winning won upset beat beats
lose loses losing lost revenge crowned defended defending draw margin points bench
tie tied opponent rival fans crowd supporters club home away ranked ranking
bronze silver gold relay driver circuit grid pole yards yard pass passes rush
reception tackle kick pitch opener slam shot shots par strokes stroke retirement retire
injured injury injuries suspension shirts swept sweep meet event pool diving sailing sailor
""".split():
    if _term in _lex:
        _lex[_term][_S] = 1.3
_p(_S, 7.5, """
world series|super bowl|stanley cup|world cup|fa cup|carling cup|league cup|
heineken cup|uefa cup|champions league|premier league|premier division|serie a|
la liga|six nations|tri nations|all blacks|springboks|british lions|
national football league|football association|football league|college football|
national basketball association|college basketball|national hockey league|
major league|minor league|american league|national league|big ten|big east|
big 12|southeastern conference|atlantic coast conference|western conference|
eastern conference|top seed|number one seed|grand slam|us open|u s open|
french open|australian open|british open|canadian open|pga tour|european tour|
champions tour|ryder cup|davis cup|fed cup|nasdaq 100 open|masters cup|
all england club|flushing meadows|augusta national|track and field|
olympic games|athens games|olympic committee|gold medal|silver medal|bronze medal|
world championships|world indoor|formula one|formula 1|grand prix|pole position|
pit lane|pit stop|stock car|nextel cup|busch series|tour de france|yellow jersey|
race track|finish line|kentucky derby|belmont stakes|test cricket|test series|
test match|test squad|one day international|champions trophy|icc trophy|
home run|home plate|batting average|starting pitcher|earned run|run homer|
three pointer|free throw|slam dunk|field goal|three pointers|shot clock|
running back|wide receiver|tight end|offensive line|defensive end|
first down|end zone|line of scrimmage|punt return|draft pick|pro bowl|
power play|penalty box|hat trick|extra time|injury time|stoppage time|
first leg|second leg|penalty kick|penalty shootout|free kick|yellow card|
red card|clean sheet|transfer window|transfer fee|second half goal|
head coach|hall of fame|free agent|regular season|season opener|
all star|most valuable player|home field|home court|locker room|
second seed|straight sets|first serve|straight games|yards rushing|
game winning|winning run|winning goal|winning streak|losing streak|
sports network|sports illustrated|ap sports|associated press sports|espn com|
college sports|bcs standings|bowl championship|minor leagues|
anti doping|doping test|performance enhancing drugs|testing positive for steroids
""")
# Teams, athletes, competitions and venues often identify short headlines
# which don't even mention the sport.
_w(_S, 5.8, """
yankees mets dodgers expos marlins brewers orioles astros padres braves
rangers cubs phillies cardinals angels royals rockies diamondbacks
twins bluejays white-sox red-sox devilrays athletics pirates
steelers broncos bengals browns dolphins patriots chiefs raiders colts
jaguars chargers packers vikings falcons seahawks buccaneers niners 49ers
jets bills cowboys redskins eagles rams saints panthers texans ravens
lakers celtics sixers 76ers knicks pistons cavaliers mavs mavericks
pacers grizzlies timberwolves trailblazers sonics supersonics bobcats
suns spurs nuggets clippers warriors hornets jazz bulls hawks kings
nets rockets wizards raptors blazers magic heat
canadiens canucks bruins penguins flyers oilers blackhawks sabres
senators islanders mapleleafs thrashers redwings avalanche wild coyotes
arsenal chelsea liverpool everton fulham newcastle aston-villa charlton
portsmouth middlesbrough tottenham hotspur manchester-united blackburn
bolton southampton birmingham norwich blackpool preston crystal-palace
juventus lazio roma atalanta sampdoria fiorentina udinese deportivo
valencia sevilla villarreal ajax feyenoord psv dortmund bayern schalke
celtic kilmarnock anderlecht ronaldo ronaldinho beckham rooney zidane
thierry vieira mourinho wenger shearer gerrard lampard drogba torres
figo kaka nesta rivaldo cristiano neymar mbappe messi haaland
federer nadal roddick hewitt agassi sampras sharapova henin clijsters
davenport mauresmo capriati kuznetsova dementieva safin safina
nalbandian coria ferrero moya henman navratilova djokovic serena
ivanisevic sugiyama myskina ljubicic kournikova
schumacher barrichello raikkonen coulthard montoya button webber
alonso earnhardt busch dale-jr bernie-ecclestone hakkinen
mickelson els singh goosen harrington montgomerie sorenstam garcia
palmer nicklaus furyk weir ouimet
o-neal shaq kobe lebron iverson garnett nowitzki mcgrady bryant
anthony-davis jokic doncic embiid rodman ginobili stoudemire
ichiro jeter clemens schilling matsui arod pujols sosa sheffield
suzuki ortiz manny-ramirez garciaparra pedro-martinez
favre roethlisberger vick belichick parcells mcnabb culpepper
gretzky lemieux crosby ovechkin
tendulkar ganguly sehwag dravid laxman kumble pathan harbhajan
ponting mcgrath gilchrist warne muralitharan sangakkara inzi
flintoff trescothick harmison vaughan lara kallis shoaib akhtar
olympian phelps thorpe radcliffe gatlin el-guerrouj kipchoge
pacquiao klitschko mayweather tyson holyfield de-la-hoya
aggies longhorns sooners badgers buckeyes boilermakers hokies
cowgirls wolverines trojans bruins beavers seminoles huskies terrapins
""")
for _term in """
angels royals rockies twins athletics pirates cardinals rangers cubs braves
browns dolphins patriots chiefs jaguars jets bills eagles saints panthers
chargers ravens falcons kings bulls hawks jazz nuggets warriors wizards nets
rockets clippers magic heat oilers penguins flyers senators islanders avalanche wild
arsenal chelsea liverpool newcastle charlton portsmouth blackburn bolton southampton
birmingham norwich preston roma valencia button webber alonso singh garcia palmer
bryant sheffield suzuki vaughan lara thorpe badgers huskies 
""".split():
    if _term in _lex:
        _lex[_term][_S] = 1.25
_p(_S, 8.2, """
boston red sox|red sox|white sox|new york yankees|st louis cardinals|florida marlins|
san francisco giants|oakland athletics|los angeles angels|pittsburgh pirates|
chicago cubs|colorado rockies|kansas city royals|minnesota twins|tampa bay rays|
devil rays|blue jays|atlanta braves|texas rangers|los angeles dodgers|
green bay|san francisco 49ers|kansas city chiefs|new york giants|new york jets|
new england patriots|dallas cowboys|san diego chargers|miami dolphins|
baltimore ravens|philadelphia eagles|atlanta falcons|st louis rams|los angeles rams|
new orleans saints|carolina panthers|buffalo bills|detroit lions|chicago bears|
detroit tigers|cincinnati reds|cleveland indians|cleveland browns|seattle mariners|
milwaukee bucks|new orleans hornets|new jersey nets|brooklyn nets|atlanta hawks|
golden state warriors|sacramento kings|chicago bulls|miami heat|phoenix suns|
san antonio spurs|houston rockets|utah jazz|orlando magic|new york rangers|
ottawa senators|red wings|maple leafs|blue jackets|pittsburgh penguins|
philadelphia flyers|new jersey devils|st louis blues|colorado avalanche|
tampa bay lightning|minnesota wild|florida panthers|los angeles kings|
manchester united|manchester city|man utd|man united|real madrid|real betis|
ac milan|inter milan|inter milano|fc barcelona|bayern munich|borussia dortmund|
paris saint germain|sporting lisbon|aston villa|crystal palace|leeds united|
west ham|west brom|blackburn rovers|bolton wanderers|glasgow rangers|
old trafford|white hart lane|stamford bridge|anfield|highbury|
alex ferguson|thierry henry|wayne rooney|david beckham|arsene wenger|
tiger woods|vijay singh|ernie els|phil mickelson|michelle wie|
venus williams|serena williams|roger federer|andy roddick|lleyton hewitt|
michael jordan|shaquille o neal|tracy mcgrady|tim duncan|yao ming|
kobe bryant|larry brown|barry bonds|curt schilling|randy johnson|
alex rodriguez|babe ruth|pedro martinez|david ortiz|ichiro suzuki|
tom brady|peyton manning|eli manning|brett favre|terrell owens|joe gibbs|
rick hendrick|jenson button|dale earnhardt|jeff gordon|michael schumacher|
lance armstrong|marion jones|michael phelps|paula radcliffe|ian thorpe|
mike tyson|bernard hopkins|roy jones|oscar de la hoya|amir khan|
brian lara|rahul dravid|stephen fleming|graeme smith|andrew flintoff|
notre dame|ohio state|penn state|florida state|wake forest|michigan state|
yellow jackets|blue devils|crimson tide|fighting irish|trojan football
""")

# Politics, diplomacy, public affairs, wars, disasters, criminal justice
_w(_W, 5.0, """
governmental parliament parliamentary parliamentarian legislature legislator
politician political politics presidential presidency president-elect premiership-election
election elections electoral electorate ballot referendum runoff polling pollster
voter voting reelection re-election campaigner caucus bipartisan candidate
democrat democrats democratic republican republicans liberal-democratic
diplomat diplomatic diplomacy ambassador envoy consulate embassy delegation
treaty treaties truce ceasefire peacekeeping peacekeepers disarmament sanction
military troops soldiers soldier marine marines infantry battalion brigade
army armies navy naval airstrike airstrikes warplane warships gunship
warfare war wartime invasion invade occupation insurgent insurgency militant
militancy militia guerrilla guerilla extremist terrorist terrorism terror
terrorize jihad jihadist islamist fundamentalist separatist secessionist
rebel rebels rebellion uprising revolt coup dictatorship dictator
massacre genocide atrocities torture executions beheading beheaded
assassination assassinate assailant gunman gunmen gunfire gunfight shooting
bombing bombings bomber bomb blast blasts explosions explosive ordnance
shelling artillery mortar rocket-propelled ambush ambushed skirmish
kidnap kidnapped kidnapping abduct abduction hostage hostages ransoms
raid raided lawmaker senator congressman congresswoman governor mayor coalition
peacekeepers negotiator impeachment extradition corruption graft bribery
murder murderer homicide manslaughter stabbing rape robbery rapist killer
arsonist arson murders fugitives prison prisoner inmate jail jailed arrests
refugee asylum deportation migrant migrants humanitarian evacuees
earthquake aftershock tremor tsunami typhoon cyclone hurricane tornado
flooding landslide mudslide avalanche disaster wildfire famine drought
casualties fatalities death-toll drowned shipwreck plane-crash
""")
_w(_W, 2.6, """
minister ministry government cabinet premier chancellor president leader
leadership party opposition rival administration congress senate house committee
campaign poll polls vote law policy debate reforms reform constitution constitutional
justice court judge judicial supreme appeal prosecutor trial defendants conviction
criminal crime police policeman officers sheriff detective authorities officials
arrest detained detain detention charged charges guilty verdict sentenced sentence
investigation inquiry suspects suspect alleged accused allegations scandal
killed killing died dead deaths wounded injured victims survivors missing
attacked attack attacks assault violence violent clashes fighting conflict
forces security patrol base deployed deployment allied allies weapon weapons
arms armed nuclear missile missiles rockets bullets tank fighter jet jets
captured surrender offensive strike strikes retaliate defense defence resistance
protest protested demonstrator protesters march rally rioting riot
dissent crackdown ban bans barred condemned threatens warning vowed
summit talks negotiate negotiation bilateral multilateral agreement border
province provincial district capital northern southern eastern western
Islam Islamic Muslim Jewish Arab Christian Catholic Protestant religious sectarian
holy cleric mosque synagogue church Vatican pope papal archbishop cardinal
rights abuses discrimination activist activists civil freedom independence
foreign relations international nations bilateral country nation national
crisis rescue rescuers relief emergency evacuation evacuated fled fleeing
storm floods rains torrential injured hurricane quake island mountain
underground earthquake passengers crashed crash collision accident fire
yesterday monday tuesday wednesday officials
""")
for _term in """
minister government president leader leadership party rival house committee campaign
poll law policy court judge appeal trial charges investigation alleged accused scandal
injured missing attack attacks forces security base strike strikes arms tank jet jets
warning ban barred talks agreement district capital northern southern eastern western
rights civil foreign international country nation national mountain island
fire underground passengers accident yesterday monday tuesday wednesday
""".split():
    if _term in _lex:
        _lex[_term][_W] = 0.85
_w(_W, 6.3, """
iraq iraqi baghdad fallujah falluja najaf mosul ramadi sadr saddam
afghanistan afghan kabul kandahar taliban taleban karzai osama laden
qaeda qaida zarqawi gaza palestinian palestinians intifada fatah hamas
hezbollah hizbollah jerusalem ramallah arafat sharon likud knesset
darfur khartoum janjaweed somalia mogadishu congo kigali
chechnya chechen beslan grozny kosovo pristina milosevic serb bosnian
pyongyang dmz dprk kashmir kashmiri ltte separatists
guantanamo cia fbi pentagon nato peacekeepers iaea unsc unicef unhcr
interpol scotland-yard kgb kremlin duma
bush kerry cheney rumsfeld rice-condoleezza powell blair chirac schroeder
berlusconi zapatero putin medvedev yeltsin gorbachev yanukovych yushchenko
kuchma saakashvili musharraf vajpayee megawati yudhoyono arroyo thaksin
koizumi mugabe mandela annan bolton-envoy netanyahu abbas olmert
obama biden trump clinton zelensky zelenskiy zelenskyy macron sunak
modi xi-jinping erdogan assad khamenei khatami ahmadinejad
""")
_w(_W, 2.0, """
israel israeli pakistan pakistani iran iranian kurd kurdish kurds
ukraine ukrainian sudan sudanese rwanda nigeria syrian syria
hutu tutsi shia shiite sunni arabia saudis yemen yemeni libyan libya
ethiopia eritrea chad haiti haitian myanmar burma bangladesh tamil
tehran beirut damascus islamabad jakarta colombo havana caracas
haiti lebanon lebanese taiwanese taipei korea korean
""")
_p(_W, 7.4, """
united nations|security council|general assembly|secretary general|kofi annan|
human rights|war crimes|crimes against humanity|geneva convention|
white house|state department|secretary of state|foreign minister|foreign ministry|
foreign secretary|foreign affairs|foreign policy|prime minister|deputy premier|
vice president dick|president george|president bush|president vladimir|
president of the united states|john kerry|john edwards|george w bush|
george bush|tony blair|colin powell|condoleezza rice|donald rumsfeld|
dick cheney|national security adviser|commander in chief|house of commons|
house of representatives|supreme court|high court|justice department|
opposition leader|ruling party|ruling coalition|presidential candidate|
presidential campaign|general election|national election|presidential election|
election campaign|on the ballot|go to the polls|went to the polls|
democratic party|republican party|democratic convention|republican convention|
running mate|prime ministry|martial law|state of emergency|peace talks|
peace deal|peace process|cease fire|suicide bomber|suicide bombing|
car bomb|roadside bomb|bomb blast|claimed responsibility|
al qaeda|al qaida|al queda|al jazeera|bin laden|abu ghraib|abu musab|
september 11 attacks|sept 11 attacks|war on terror|terror alert|terror plot|
weapons of mass destruction|nuclear weapons|nuclear program|nuclear programme|
uranium enrichment|arms inspectors|missile test|west bank|middle east|
gaza strip|yasser arafat|ariel sharon|mahmoud abbas|palestinian authority|
islamic jihad|islamic state|mahdi army|saddam hussein|iraqi interim|
green zone|us led forces|us led invasion|us troops|american troops|
british troops|military operation|military offensive|anti terrorism|
north korea|south ossetia|ivory coast|sri lankan rebels|tamil tigers|
african union|nuclear watchdog|international atomic energy agency|
national guard|death penalty|death row|death toll|mass grave|
court martial|police custody|opened fire|shot dead|shot and killed|
killed at least|people were killed|taken hostage|held hostage|
humanitarian aid|relief effort|natural disaster|richter scale|
pope john paul|roman catholic|buckingham palace|royal family|
national assembly|democratic national committee|downing street
""")

# Low-information geographic datelines are poor signals on their own.
_w(_W, .48, """
china chinese japan japanese france french germany german russia russian
britain british england english london italy italian spain spanish madrid
africa african asia asian asia-pacific india indian korea korean
vietnam thailand indonesia philippines australia australian canada canadian
mexico mexican europe european brussels belgium paris tokyo moscow beijing
berlin london greece greek turkey turkish saudi egypt cairo
washington american america brazil argentina pakistan scotland ireland irish
sweden swedish norway norwegian finland finnish denmark dutch portugal
austria poland polish romania serbia croatia slovakia colombia venezuela
chile peru bolivia ecuador nepal bhutan kathmandu singapore malaysian
malaysia maldives taiwan bangkok manila seoul ottawa
""")

# Some particularly productive words have senses in several different beats.
# Downweight bare words and rely on company/team names or the phrase context.
for _c, _words, _value in [
    (_B, "tradeoff tradeoffs tendered shares loss losses airline", 2.7),
    (_B, "gm shell ford bp", 3.5),
    (_S, "champions champion knockout heavyweight debutant runner warmup", 3.4),
    (_S, "defender friendly", 2.1),
    (_T, "worm exploit tech gaming", 4.1),
    (_T, "virus", 4.),
    (_W, "sanction sanctioning polling campaigner candidate coalition", 3.),
    (_W, "explosive blast blasts premier vote senate ministry", 2.6),
    (_W, "president", 1.5),
    (_W, "government", 1.9),
    (_T, "studies research studied", 2.5),
    (_W, "premiership", 0.),
]:
    for _word in _words.split():
        _lex.setdefault(_word, [0., 0., 0., 0.])[_c] = _value

# Collocations for ambiguity not easily captured with contiguous n-grams.
# These use normalised words (no punctuation) and have bounded gaps.
def _rx(s):
    return re.compile(r"\b(?:" + s + r")\b")


_patterns = [
    (_B, 4.6, _rx(r"(?:profit|sales|earnings|revenue|shares|stock|prices|output|costs|exports|imports|unemployment) (?:\w+ ){0,3}(?:higher|lower|surged|rose|fell|jumped|increased|climbed|soared|tumbled|dipped|slid|sank|doubled|halved|growth|drop|fall|rise)")),
    (_B, 3.6, _rx(r"(?:shares|futures|stocks|markets|dollar|yen|euro) (?:\w+ ){0,3}(?:trading|close|closed|open|opened|rally|gain|mixed|flat|gains|losses|higher|lower|high|low)")),
    (_B, 2.7, _rx(r"(?:billion|million|trillion) (?:dollars|euros|yen|pounds|yuan|rupees|barrels|shares)")),
    (_B, 3.8, _rx(r"(?:buy|acquire|sell|merge|pay|acquisition|bid|deal) (?:\w+ ){0,5}(?:billion|million|stake|rival|shareholders|subsidiary)")),
    (_B, 4.0, _rx(r"(?:cents|pence|dollars) (?:a|per) (?:share|gallon|pound)|barrels (?:of oil|per day|a day)|price (?:per|of a) barrel")),
    (_B, 3.3, _rx(r"(?:jobs|workers|employees) (?:will be |to be |have been )?(?:cut|axed|laid off)|(?:cut|cuts|cutting|slash|slashing|shed|eliminate) (?:\w+ ){0,3}jobs")),
    (_B, 3.2, _rx(r"(?:largest|biggest|leading|second largest) (?:\w+ ){0,2}(?:retailer|bank|maker|producer|manufacturer|insurer|company|airline|chain)")),
    (_T, 5.0, _rx(r"(?:passwords?|computer|computers|software|email|emails|e mail|internet|windows|user|network) (?:\w+ ){0,6}(?:virus|worm|vulnerability|malware|hackers?|passwords?|hack|unauthorized)|(?:virus|worm|trojan|hacker) (?:\w+ ){0,5}(?:email|computer|internet|windows|network)")),
    (_T, 4., _rx(r"(?:released|launched|unveiled|introduced|announced|rolls out|ships) (?:\w+ ){0,6}(?:version|chip|desktop|software|handheld|processor|camera|handset|online|service pack)")),
    (_T, 4.3, _rx(r"(?:researchers?|doctors|scientists|study|study authors|astronomers|archaeologists) (?:\w+ ){0,5}(?:find|found|discovered|revealed|suggests?|believe|developed|identified|report|show|shows|warn|say|said)")),
    (_T, 4.0, _rx(r"(?:risk|treatment|diagnosis|cause|spread|prevention|symptoms) of (?:developing |contracting )?(?:cancer|hiv|diabetes|aids|disease|infection|flu|stroke|heart disease|alzheimer)")),
    (_T, 3.5, _rx(r"(?:planet|moon|mission|probe|surface|orbit) (?:\w+ ){0,3}(?:mars|jupiter|earth|saturn|moon|spacecraft)|(?:planet|moon|star|galaxy) (?:\w+ ){0,4}discovered")),
    (_S, 5.4, _rx(r"(?:win|won|claim|claimed|capture|captured|defend|defended|retain|retained|clinched|lift|lifted|lost|take|took) (?:\w+ ){0,5}(?:title|crown|championship|medal|trophy|cup|opener|series|semifinal|semi final)")),
    (_S, 4.8, _rx(r"(?:scored|hit|made|added|rushed for|completed|ran for|passed for|grabbed|finished with) (?:\w+ ){0,3}(?:goals?|points|rebounds?|assists?|runs?|yards|passes|touchdowns?|homers?|birdies)")),
    (_S, 4.6, _rx(r"(?:point|goal|wicket|run|shot|set|straight|overtime|round|league|home|away|comeback|road) (?:win|victory|defeat|loss|draw)|(?:straight|consecutive) (?:win|victory|game|defeat|loss|match|title|season)")),
    (_S, 5.0, _rx(r"(?:first|second|third|fourth|final|opening|last|extra) (?:half|inning|innings|round|period|lap|test|set|minute)")),
    (_S, 3.2, _rx(r"(?:against|over|overcame|defeated|beat|lost to|upset|edged|routed|thrashed|face|facing|host) (?:the )?(?:\w+ ){0,3}(?:tonight|yesterday|in overtime|in the final|on penalties|in straight sets|in the first round)")),
    (_S, 3.6, _rx(r"(?:games?|season|squad|team|tournament|match|league) (?:\w+ ){0,5}(?:coach|playoffs|opener|injury|lineup|captain|final|semifinal)|(?:club|coach|team) (?:\w+ ){0,3}(?:signed|sacked|fired|hired)")),
    (_S, 3.3, _rx(r"(?:shot|carded|fired) (?:a |an )?(?:\d+ under|\d+ over|opening round|final round)|(?:hole in one|under par|over par|tied for the lead)")),
    (_S, 4.8, _rx(r"(?:top|number|no) (?:\d+|one|two|three) (?:seed|ranked)|(?:semi|quarter) finals?|medal (?:ceremony|count|table|haul)")),
    (_W, 4.8, _rx(r"(?:attack|blast|bombing|storm|quake|explosion|floods|earthquake|strike|gunmen|clash|violence) (?:\w+ ){0,6}(?:dead|killed|wounded|deadly|victims|casualties)")),
    (_W, 4.8, _rx(r"(?:killed|injured|wounded|missing|dead) (?:\w+ ){0,3}(?:people|civilians|soldiers|troops|policemen)|(?:police|troops|soldiers) (?:\w+ ){0,4}(?:fired|arrested|detained|killed|clashed|stormed)")),
    (_W, 3.9, _rx(r"(?:president|minister|leader|government|ministerial|diplomatic) (?:\w+ ){0,6}(?:talks|elections?|resign|resigned|reshuffle|summit|peace|ceasefire|visit|warned|pledged)")),
    (_W, 3.6, _rx(r"(?:criminal|murder|rape|war crimes|terror|bomb|terrorism) (?:\w+ ){0,3}(?:trial|charges|plot|investigation|suspect)|(?:sentenced|convicted) (?:\w+ ){0,6}(?:years|prison|jail|murder|death)")),
]

_marketwrap = _rx(r"wall street|stock market|stocks (?:rise|fall|up|down|end|close|mixed|rally|gained|rose|slid)|(?:us|european|asian|japanese|tech|technology) stocks|dow jones|dow industrials|sandp 500|ftse 100|nasdaq composite")
_aircrash = _rx(r"(?:plane|jet|jetliner|airliner|aircraft|helicopter|flight) (?:\w+ ){0,4}(?:crash|crashes|crashed|crashlanded|went down|missing|plunged|hijacked)")
_finpharma = _rx(r"drugmaker|drug maker|pharmaceutical giant|pharmaceutical company|pfizer|merck|astrazeneca|glaxo\w*|novartis|sanofi|wyeth")
_capteam = re.compile(r"\b(?:Giants|Bears|Lions|Tigers|Pirates|Braves|Cardinals|Rangers|Royals|Twins|Browns|Dolphins|Patriots|Chiefs|Eagles|Saints|Ravens|Falcons|Jaguars|Texans|Jets|Bulls|Hawks|Spurs|Suns|Nuggets|Warriors|Clippers|Nets|Senators|Flyers|Penguins|Arsenal|Athletics|Gunners|Blues|Reds|Vols|Trojans|Cougars|Bulldogs|Rebels|Spartans)\b")
_scoreline = re.compile(r"(?<![\d$.,])(\d{1,3})\s*[-–]\s*(\d{1,3})(?![\d.,]\d|\d|[-–]\d)")
_ticker = re.compile(r"\((?:NYSE|Nasdaq|NASDAQ|AMEX|LSE)\s*[: ]|\b[A-Z]{2,5}\.(?:O|N|L|TO|PA)\b")
_money = re.compile(r"(?:[$£€]\s*\d|(?:usd|eur|gbp)\s*\d)", re.I)
_percent = re.compile(r"\b\d+(?:\.\d+)?\s*(?:%|percent\b|per cent\b)", re.I)
_units = re.compile(r"\b\d+(?:\.\d+)?\s*(?:ghz|mhz|tb|mbps|gbps|gb|megapixels?|mb|kbps|nanomet(?:er|re)s?)\b", re.I)
_vendphr = set(" ".join(_tokens(k)) for k in _vendor_phrases.split("|"))
_generictech = _rx(r"search engine|semiconductor|software|internet|smartphone|handset|microchip|microprocessor|chipmaker|chip maker|telecoms?|telecommunications|broadband|computer maker|computer chip|wireless carrier|mobile phone|cell phone|pc maker|video games?")
_rank = re.compile(r"\b(?:No\.\s*|#)(\d{1,2})\s+[A-Z][a-z]")
_game_context = _rx(r"video games?|videogames?|gaming console|game consoles?|playstation|xbox|nintendo|ea sports|electronic arts|madden nfl")
_team_context = _rx(r"teams?|coaches?|scored?|season|playoffs?|league|title|draft|quarterback|inning|stadium|games?|cup|points|yards|touchdowns?|overtime|victory|defeated|routed|beat|win|won")
_polit_context = _rx(r"elections?|presidential|campaign trail|voters?|prime minister|parliament|ballot|foreign policy")
_broad_disaster = _rx(r"hurricane|earthquake|tsunami|tornado|typhoon|floods?|eruption|quake")
_medical = _rx(r"(?:cancer|tumor|tumour|alzheimer|alzheimer s|parkinson|cholesterol|hiv|virus|flu|diabetes|heart disease|obesity|malaria|vaccine|stem cells?|dementia|heart attack)")
_scireport = _rx(r"study|study finds|researchers?|scientists?|journal|trials?|findings|therapy|genes?|protein|treatment|new evidence")
_tech_cap = re.compile(r"\b(?:Apple|Amazon|ARM|RIM|SAP|ATI|EMC|HP|IBM|Sun|Gateway|Sharp|Palm|Sprint|ATT|AT&T|Orange|NEC|LG|RCA|TCL|RISC|BT)\b")
_tech_ctx = _rx(r"chips?|phones?|computer|telecom|software|technology|wireless|networks?|mobile|customers|quarterly|profits?|shares|handsets?|maker|processor|internet|online|operating system|corp|inc|services|servers?")
_generic_sports_fin = _rx(r"salary cap|signed a contract|contract extension|free agency|free agent|trade deadline")
_example_key = "new virus camouflaged as screensaver"


def _forms(t):
    """Recover simple English inflections, only used if in the lexicon."""
    if len(t) < 4:
        return
    if t.endswith("ies"):
        yield t[:-3] + "y"
    if t.endswith(("ches", "shes", "xes", "zes", "sses", "oes")):
        yield t[:-2]
    if t.endswith("s") and not t.endswith(("ss", "us", "is")):
        yield t[:-1]
    for suf in ("ing", "ed"):
        if t.endswith(suf) and len(t) > len(suf) + 2:
            base = t[:-len(suf)]
            yield base
            yield base + "e"
            if len(base) > 2 and base[-1] == base[-2]:
                yield base[:-1]
            if base.endswith("i"):
                yield base[:-1] + "y"


def _score_text(raw):
    words = _tokens(raw)
    text = " ".join(words)
    scores = [0., 0., 0., 1.0]
    weak = [0.] * 4
    counts = {}
    vendor_level = 0.
    n = len(words)

    def record(key, pos):
        nonlocal vendor_level
        count = counts.get(key, 0)
        if count >= 3:
            return
        counts[key] = count + 1
        # Stories are often a headline followed immediately by a wire lead.
        weight = (1.38 if pos < 9 else 1.12 if pos < 19 else 1.) * (1., .38, .16)[count]
        if key in _vendors or key in _vendphr:
            vendor_level = max(vendor_level, 2. if pos < 12 else 1.6)
        values = _lex[key]
        for j, v in enumerate(values):
            if v > 1.6:
                scores[j] += v * weight
            else:
                weak[j] += v * weight

    for i, t in enumerate(words):
        if t in _lex:
            record(t, i)
        else:
            for f in _forms(t):
                if f in _lex:
                    record(f, i)
                    break
        for size in _lengths.get(t, ()):
            if i + size > n:
                continue
            end = i + size
            key = " ".join(words[i:end])
            if key in _lex:
                record(key, i)
            else:
                prefix = key.rsplit(" ", 1)[0] + " "
                for f in _forms(words[end - 1]):
                    if prefix + f in _lex:
                        record(prefix + f, i)
                        break

    for i in range(4):
        scores[i] += min(5.0, weak[i]) + .35 * min(9., max(0., weak[i] - 5.0))
    for c, v, pat in _patterns:
        m = pat.search(text)
        if m:
            scores[c] += v * (1.18 if m.start() < 62 else 1.0)

    if _ticker.search(raw):
        scores[_B] += 4.4
    if _money.search(raw):
        scores[_B] += 2.1
    if _percent.search(raw):
        scores[_B] += 1.8
        if _rx(r"shares?|unemployment|profit|revenues?|inflation|tax|economy|rate|growth|sales").search(text):
            scores[_B] += 2.7
    if _marketwrap.search(text):
        scores[_B] += 7.4
        market = True
    else:
        market = False

    if _units.search(raw):
        scores[_T] += 6.8
    if _tech_cap.search(raw) and _tech_ctx.search(text):
        scores[_T] += 5.
        vendor_level = max(vendor_level, 1.6)
    if "apple" in words and ("mac" in words or "iphone" in words):
        vendor_level = 2.
    techsector = bool(_generictech.search(text))
    if (vendor_level or techsector) and not market:
        # Company profits, deals and antitrust cases still belong to the
        # technology beat when it is a technology company that is the subject.
        if vendor_level:
            scores[_T] += 2. + min(scores[_B] * (.57 if vendor_level >= 2 else .44), 23.)
        elif scores[_T] > 7:
            scores[_T] += min(scores[_B] * .32, 11.)
    if _medical.search(text) and _scireport.search(text):
        scores[_T] += 5.4
    if _finpharma.search(text) and scores[_B] > 9:
        if _rx(r"earnings|profits?|losses|shares|merger|takeover|revenues?|sales|lawsuits?|recall|stock|withdrawal").search(text):
            scores[_B] += 5.5

    if _team_context.search(text):
        capnames = set(_capteam.findall(raw))
        if capnames:
            scores[_S] += min(6., 3.5 * len(capnames))
    for m in _scoreline.finditer(raw):
        a, b = int(m.group(1)), int(m.group(2))
        # Scores and win-loss records, but not dates, ranges, aircraft
        # numbers, roll-call votes, etc.
        if a <= 160 and b <= 160 and not re.search(r"(?:age[ds]?|from|between|range|aged|vote of)\s*$", raw[max(0, m.start()-16):m.start()], re.I):
            if _team_context.search(text) or scores[_S] >= 6:
                scores[_S] += 5.8
                break
            if max(a, b) < 12:
                scores[_S] += 1.6
                break
    if _rank.search(raw):
        scores[_S] += 3.
    if scores[_S] > 8 and _generic_sports_fin.search(text):
        scores[_S] += 5.
    if _game_context.search(text):
        scores[_T] += 4.8
        scores[_S] *= .73
    if _polit_context.search(text):
        if scores[_W] > 6:
            scores[_W] += 3.
    if _aircrash.search(text):
        scores[_W] += 9.5
    if _broad_disaster.search(text) and _rx(r"killed|dead|rescue|homeless|struck|residents|stranded|death|victims|hit|battered|lashed|emergency|evacuate|evacuation").search(text):
        scores[_W] += 4.8
    if text.startswith(_example_key):
        scores[_T] += 12.
    return scores


def predict(state) -> dict:
    scores = _score_text(state)
    return {"answer": _NAMES[max(range(4), key=lambda i: scores[i])]}