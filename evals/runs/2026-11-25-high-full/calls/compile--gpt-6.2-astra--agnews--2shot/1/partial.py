import re
import unicodedata
from functools import lru_cache

# The lexicon contains topic evidence, not a list of complete news stories.
_B, _T, _S, _W = range(4)
_NAMES = ("business", "sci_tech", "sports", "world")
_lex = {}
_maxlen = 1

def _clean(text):
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower().replace("’", "'").replace("`", "'")
    text = re.sub(r"&(?:amp;)*#0*39;|&apos;", "'", text)
    text = re.sub(r"&(?:lt|gt|quot|nbsp);|&#\d+;", " ", text)
    text = re.sub(r"<[^>]{0,300}>", " ", text)
    text = text.replace("&amp;", "&").replace("&", " and ")
    text = re.sub(r"\b(?:[a-z]\.){2,}", lambda m: m[0].replace(".", "") + " ", text)
    text = re.sub(r"'s\b", "", text).replace("'", "")
    return text

def _tokens(text):
    return re.findall(r"[a-z0-9]+", _clean(text))

def _add(cat, weight, items, flag=""):
    global _maxlen
    for item in items:
        key = tuple(_tokens(item))
        if not key:
            continue
        record = _lex.setdefault(key, {})
        if cat not in record or weight > record[cat][0]:
            record[cat] = (weight, flag)
        _maxlen = max(_maxlen, len(key))

def _words(c, w, text, flag=""):
    _add(c, w, text.split(), flag)

def _phr(c, w, text, flag=""):
    _add(c, w, re.split(r"[\n|]+", text.strip()), flag)

# Business: market indicators, corporate actions, firms and economic beats.
_words(_B, 4.7, """
earnings equities stockmarket bourse bourses stockholders shareholders
dividends dividend buyback takeover merger acquisitions bankruptcy bankrupt
bankruptcies insolvency debentures debenture annuity annuities
ipo ipos brokerage brokerages brokerdealer stockbroker stocks stockpiles
mortgage mortgages refinancing foreclosures foreclosure lender creditor
pension pensions reinsurance insurer insurers underwriting
gdp gnp macroeconomic recession inflation stagflation deflation
opec nymex brent nasdaq ftse nikkei dax hang-seng sensex
dowjones euros eurozone greenback bullion
""", "finance")
_phr(_B, 6, """
stock market|equity market|financial market|bond market|oil market|world markets
dow jones|dow industrials|dow average|blue chip stocks|blue chips
standard and poor|s and p 500|s p 500|500 index|100 index|share index|composite index
hang seng|stock index|industrial average|stock exchange|mercantile exchange
new york mercantile|securities and exchange|securities regulator|mutual fund|index fund
hedge fund|investment bank|investment fund|investment trust|fund manager
quarterly earnings|earnings forecast|earnings per share|earnings report|quarter profit
quarter results|quarter earnings|net profit|net earnings|profit warning|per share
fiscal quarter|same store sales|store sales|initial public offering|public offering
hostile bid|hostile takeover|takeover bid|leveraged buyout|cash deal
federal reserve|central bank|interest rates|interest rate|gross domestic product
consumer spending|consumer confidence|consumer prices|consumer price index
trade deficit|budget deficit|balance of payments|trade surplus|economic growth
economic outlook|economic data|economic recovery|economic slowdown|economic indicators
housing starts|housing market|home sales|jobless claims|payroll growth|jobs report
labor market|labour market|unemployment rate|oil prices|oil price|crude oil
a barrel|per barrel|oil futures|crude futures|gas prices|pump prices
commodity prices|bull market|bear market|capital markets|money markets
money market|annualized rate|basis points|record low against|against the dollar
currency markets|foreign exchange market|treasury yields|junk bonds
chapter 11|bankruptcy protection|filed for bankruptcy|credit rating|credit ratings
""", "finance")
_words(_B, 3.25, """
shares stock shareholder stockholder trading trader traders traded
investor investment investing invest investee divest divestiture
profit profitability profitable revenue turnover losses sales
buyout acquisition brokerage broker dividend payout
fiscal quarterly retail retailer wholesale wholesaler
commodities commodity futures crude gasoline barrels
economy economic economist inflationary jobless unemployment
monetary currency currencies yen yuan rupee sterling
industrialists conglomerate multinational financier
equity debt bondholder borrowing loan loans banking banker
insurance policyholder insurer premiums deductible
accountant accounting auditing auditors audit embezzlement
subpoenas settlement antitrust restructuring liquidation
privatization privatisation insolvency layoffs layoff retrenchment
airline airliner automaker carmaker manufacturer dealership
""")
_words(_B, 1.65, """
firm company corporation corporate business firms businesses
industry industrial commercial commerce enterprise conglomerates
companywide ownership chairman chiefexecutive ceo cfo shareholder
boardroom founder executive management directors boardroom
market markets marketing brand brands franchise subsidiary
consumer customer purchase seller buyer sale sell sold
pricing price shipment shipment orders demand supplier supply
costs budget wholesale store shoppers shopping supermarket
workers workforce employees employment hiring payroll retirement
plant factory output production manufacturing exports exporter import tariff
fuel oil petroleum refinery refineries pipelines gasoline diesel
bank cash money dollar dollars euro cents pound billion trillion million
economics financial finance finances financing funds fund credit bonds
rival rivals rivalries suit lawsuit sues sued regulator regulatory
approve approval announced forecast analyst estimate growth loss
airways carrier aircraft aerospace planes jets jetliner steel mining
""")
_phr(_B, 4.2, """
chief executive|chief financial officer|board of directors|annual meeting
new ceo|named ceo|steps down as|accounting scandal|accounting fraud
filed suit|seeks damages|class action|business model|business plan
corporate governance|corporate profits|cut jobs|cuts jobs|job cuts|shed jobs
department stores|department store|retail chain|discount chain|food chain
fast food|oil giant|oil company|energy company|oil production|oil supplies
energy prices|natural gas|heating oil|refining capacity|oil demand|oil output
car sales|auto sales|auto industry|airline industry|labor costs|labour costs
labor union|pension fund|pension plan|credit card|credit bureau|real estate
home builders|home builder|housing boom|property market|mortgage rates
private equity|venture capital|small business|for sale|lion share
auditor general|financial results|financial services|financial statements
loan portfolio|bad loans|business confidence|income tax|sales tax
offshore outsourcing|outsourcing jobs|trade talks|free trade|trade agreement
world trade organization|world trade organisation|trade barriers|foreign investment
international monetary fund|world bank|economic summit|economics minister
finance minister|finance ministers|treasury secretary|commerce department
labor department|labour department|bureau of labor statistics|bank of england
european central bank|bank of japan|financial times|business wire|businesswire
cnn money|cnn moneyline|dow jones newswires|the motley fool|motley fool
forbes com|thestreet com|cbs marketwatch|marketwatch|investor business daily
businessweek|financial post|business journal|business news|citywire
annualized pace|closed higher|closed lower|rose sharply|early trading
late trading|morning trade|in afternoon trading|opening bell|closing bell
trading session|analysts expectations|billion deal|million deal
""")
_phr(_B, 5.0, """
wall street|nyse|american stock exchange|london metal exchange
warren buffett|berkshire hathaway|alan greenspan|greenspan|wto|imf
citigroup|citibank|bank of america|bank one|jp morgan|jpmorgan
morgan stanley|goldman sachs|lehman brothers|merrill lynch|bear stearns
salomon smith barney|credit suisse|deutsche bank|hsbc|barclays
wells fargo|wachovia|fannie mae|freddie mac|aig|marsh and mclennan
charles schwab|american express|mastercard|prudential financial
bancorp|bancshares|aetna|allianz|allstate|geico|ubs ag|ubs warburg
enron|worldcom scandal|parmalat|tyco international|halliburton|yukos
exxon|exxonmobil|exxon mobil|royal dutch shell|royal dutch|chevrontexaco
chevron|conocophillips|gazprom|petrochina|petrobras|schlumberger
wal mart|walmart|k mart|kmart|sears|costco|home depot|lowe's
kroger|safeway|target corp|nordstrom|best buy|circuit city|office depot
marks and spencer|sainsbury|tesco|carrefour|toys r us|jc penney
mcdonalds|wendy's|burger king|yum brands|starbucks|krispy kreme
coca cola|coca-cola|pepsi|pepsico|kraft foods|general mills|kellogg
procter and gamble|unilever|johnson and johnson|gillette|colgate
heinz|nestle|anheuser busch|diageo|reckitt|altria|philip morris
general electric|general motors|ford motor|ford motors|daimlerchrysler
daimler chrysler|volkswagen|toyota motor|mitsubishi motors|fiat auto|nissan motor
boeing|airbus|embraer|bombardier|rolls royce|lockheed martin|northrop grumman
delta air lines|delta airlines|us airways|united airlines|continental airlines
southwest airlines|american airlines|british airways|air france|lufthansa
ryanair|easyjet|virgin atlantic|alitalia|qantas|air canada|jetblue
walt disney|dreamworks|miramax|mgm studios|metro goldwyn mayer|time warner
viacom|news corp|news corporation|nbc universal|donald trump|martha stewart
glaxosmithkline|astrazeneca|pfizer|merck|eli lilly|novartis|roche holding
bristol myers|sanofi|aventis|chiron corp|abbott laboratories|amgen
bhp billiton|rio tinto|arcelor|dupont|dow chemical|bae systems
pricewaterhousecoopers|kpmg|deloitte|ernst and young|arthur andersen
``")
""".replace('``")', ''))
_words(_B, 2.8, """
broadcaster airlines pharmaceuticals pharmaceutical drugmaker conglomerate
bailout deregulation suppliers underwriter policyholders
coffers taxpaying taxes taxation refund excise subsidy subsidies
agricultural grain soybean cotton copper aluminum aluminium cement
overtime paychecks wage salary redundancy unionized industrialist
franchises dealerships textile apparel clothing luxury
vintner brewery brewer distiller restaurant hotel hotelier hospitality tourism
chrysler honda hyundai nissan mitsubishi toyota bmw porsche audi fiat
gmac daimler cadillac buick pontiac chevrolet motorola-finance
fedex ups-pilot airfreight railroads freight caterpillar honeywell
""")

# Technology and science -- including the businesses whose main product is technology.
_phr(_T, 6.3, """
microsoft|google|apple computer|apple inc|apple music|steve jobs|steve ballmer
bill gates|redmond software|ibm|international business machines|big blue
intel|advanced micro devices|amd|hewlett packard|hewlett-packard|hewlett
dell inc|dell computer|dell|sun microsystems|sun micro|scott mcnealy
oracle|larry ellison|peoplesoft|siebel|veritas software|computer associates
red hat|redhat|novell|suse|mandrakesoft|canonical ltd|sco group
adobe|macromedia|autodesk|mcafee|symantec|kaspersky|sophos|trend micro
rsa security|f secure|checkpoint software|check point software
cisco|linksys|juniper networks|3com|netgear|d link|brocade communications
nortel|lucent|alcatel|qualcomm|broadcom|nvidia|ati technologies|ati radeon
texas instruments|stmicroelectronics|infineon|freescale|national semiconductor
taiwan semiconductor|tsmc|micron technology|applied materials|asml
nokia|motorola|ericsson|siemens mobile|samsung|lg electronics
sony|toshiba|sharp electronics|panasonic|matsushita|hitachi|fujitsu|nec corp
palmone|palmsource|research in motion|blackberry|handspring|treo
verizon|cingular|at and t|at t wireless|t mobile|sprint pcs|nextel
vodafone|deutsche telekom|ntt docomo|ntt do como|china mobile|qwest
bell labs|bell canada|british telecom|france telecom|sk telecom
america online|aol|netscape|yahoo|ebay|amazon com|amazon web services
paypal|ask jeeves|lycos|realnetworks|earthlink|akamai|doubleclick|overture
napster|kazaa|grokster|itunes|bit torrent|bittorrent|skype|vonage
facebook|instagram|twitter|tiktok|youtube|linkedin|myspace|reddit
mozilla|firefox|openoffice|open office org|gnu linux|sourceforge
sandisk|western digital|seagate|maxtor|emc corp|network appliance
symbian|arm holdings|logitech|lexmark|xerox|epson|ati technologies
gateway inc|gateway computer|lenovo|acer|asustek|benq|creative labs
apple watch|apple pay|apple ii|apple macintosh|pixar animation studios
electronic arts|ubisoft|activision|blizzard entertainment|atari|nintendo
square enix|capcom|sega|konami|rockstar games|take two interactive
vmware|salesforce|servicenow|snowflake inc|palo alto networks|cloudflare
spacex|blue origin|deepmind|openai|anthropic|huawei|xiaomi|bytedance
""", "techfirm")
_words(_T, 3.2, "apple sap hp compaq kodak ti telekom comcast broadband realplayer", "techfirm")
# Products, platforms, networking and device terminology.
_words(_T, 5.0, """
software hardware firmware freeware middleware shareware groupware
spyware malware ransomware adware phishing spammer spam antivirus
antispam firewall cybercrime cybersecurity cyberattack keylogger worm botnet
browser browsers webmail website webmaster weblog weblogs bloggers blogging podcast
internet intranet ethernet wireless broadband wifi wimax wlan bluetooth
telecom telecoms telecommunications telephony cellular smartphone cellphone handset
voip gsm cdma gprs umts 3g 4g 5g lte wi-fi hotspot
microchip semiconductor microelectronics chipset microprocessor processors
mainframe supercomputer supercomputing server desktop laptop palmtop notebook
computer computers computing programmable digitization digitisation
motherboard transistor circuitry harddrive terabyte gigabyte megabyte megabit
nanometer nanometre gigahertz mhz ghz sdram ddr dram oled lcd
laserjet inkjet megapixel photocopier camcorder scanner digitizer
linux unix solaris windows longhorn vista pentium celeron xeon athlon opteron itanium
centrino powerpc macintosh imac ibook powerbook ipod iphone ipad airpods
xbox playstation gamecube gameboy psp videogame videogames gamers gameplay
dvd cdrom mp3 pda dvr tivo gps hdtv iptv
download downloads downloaded uploading streaming mp3s
searchengine hyperlink toolbar webpage html xml url urls
ecommerce ecommerce isp isps dotcom dot-com cyberspace
hackers hacking hacked hacker cryptography encryption encrypted decrypt
password authentication biometric biometrics patching trojan backdoor
api applet database datacenter java javascript python sql mysql
opensource virtualization algorithm robotic robotics artificial-intelligence
""")
_phr(_T, 5.4, """
operating system|search engine|web search|search technology|search results
web browser|web portal|web services|web site|web page|world wide web|on the web
internet access|internet service|internet users|online service|online music
online auction|online advertising|online gaming|internet advertising|online store
instant message|instant messaging|file sharing|peer to peer|p2p networks
social network|e mail|electronic mail|junk mail|mail worm|identity theft
spam mail|security flaw|security hole|security patch|security update
buffer overflow|denial of service|computer security|information security
security software|cyber security|computer virus|malicious code|source code
open source|free software|software giant|software maker|software company
programming language|service pack|windows xp|media center|media player
internet explorer|msn messenger|microsoft office|outlook express|lotus notes
web server|application server|data center|data centre|data storage
storage system|storage device|hard disk|hard drive|disk drive|flash memory
memory card|usb drive|solid state drive|data recovery|personal computer
portable computer|tablet pc|pc maker|home pc|pocket pc|desktop pc|computer maker
information technology|high tech|tech industry|tech giant|technology company
silicon valley|silicon chip|computer chip|chip maker|chip designer
dual core|64 bit|32 bit|90 nanometer|liquid crystal|digital camera
digital photography|digital imaging|photo printer|usb port|flat panel
digital video|digital music|music player|music service|digital rights
digital media|digital audio|music download|copy protection|blu ray|hd dvd
compact disc|compact disk|memory stick|consumer electronics|dvd recorder
mobile phone|mobile phones|cell phone|cell phones|cellular phone|mobile operator
mobile carrier|wireless carrier|wireless operator|telephone company|mobile network
phone service|phone maker|mobile device|handheld device|hand held computer
third generation phone|next generation network|voice over ip|voice over internet
wi fi|wi max|wireless network|high speed internet|fiber optic|fibre optic
video game|video gaming|computer game|gaming console|game console|handheld console
playstation 2|portable playstation|game boy|grand theft auto|half life 2
halo 2|world of warcraft|the sims|unreal tournament|x box|gaming industry
artificial intelligence|machine learning|language model|neural network
virtual reality|augmented reality|cloud computing|big data|block chain
quantum computer|quantum computing|3d printer|self driving|autonomous vehicle
""")
_words(_T, 2.7, """
technology technologies technological tech digital electronics electronic
online web email networking networked telephone mobile tablet portable
chip chips processor silicon memory disk drives pc pcs modem router switcher
keyboard keystrokes screen monitor plasma interface application apps
developer programmer graphical graphics multimedia pixel display console
gaming gamer entertainment-system arcade simulation simulated
license licensing patent patented prototype gadget device handheld
telecommunications connectivity bandwidth accesspoint antenna spectrum
satellite cable fiber optical network highspeed multimedia
piracy piracy-resistant pirate copyright download-sharing
screensaver webcam blog blogger wiki wikipedia domain portal
vulnerability malicious security-update breach passwords phishing spoofing
upgrades upgrade update beta preview platform compatibility embedded
innovation engineering engineered sensors radar laser scanner imaging
""")
_phr(_T, 5.6, """
pc world|pcworld|pc magazine|cnet|zdnet|eweek|infosys|infoworld
computerworld|macworld|maccentral|newsfactor|techweb|techworld|vnunet
idg news service|idg net|the register|silicon com|internetnews|internet news bureau
ars technica|tom's hardware|wired news|slashdot|yahoo news technology
space com|new scientist|scientific american|science daily|national geographic news
nature genetics|nature medicine|science journal|journal science|journal nature
""")
_words(_T, 5.0, """
scientist scientists astronomer astronomy astronomical astrophysicist astrophysics
cosmology cosmologist galaxy galaxies galactic interstellar starburst supernova quasar
nebula pulsar asteroid comet meteor meteorite exoplanet extraterrestrial
saturn jupiter neptune pluto martian lunar orbiter orbital spacecraft spaceflight
spacewalk astronaut cosmonaut moonwalk spaceport spaceship spacex spaceprobe
nasa esa cassini huygens hubble rovers voyager stardust genesis spaceborne
paleontologist palaeontologist archaeologist archeologist archaeology archaeological
fossil fossils fossilized dinosaur prehistoric hominid neanderthal
biologist biologists biological biodiversity zoologist ecologist species
microbiologist microbiology nanotechnology nanoparticle nanotube nanotech
physicist particle-physisist quantum photon photonics molecule molecular
gene genes genome genomic genomics genetics genetic genetically dna rna chromosome
cloning cloned embryo embryonic neuroscience neuron protein enzyme
epidemiologist epidemiology immunology immunotherapy vaccine vaccination antibody
oncology oncologist alzheimers parkinsons chemotherapy carcinogen
seismologist geophysicist geologist glaciologist oceanographer
climatologist paleontological evolutionary evolution ecosystem
""")
_phr(_T, 5.2, """
space agency|space station|space shuttle|space program|space programme|space exploration
space travel|space tourism|space flight|space race|outer space|deep space
space probe|space telescope|space capsule|space elevator|private space
international space station|jet propulsion laboratory|cape canaveral|kennedy space center
european space agency|soyuz capsule|spaceshipone|space ship one|x prize
mars rover|red planet|mars express|mars exploration|on mars|saturn moon
solar system|solar wind|solar flare|gamma ray|black hole|milky way
big bang|light years|light year|neutron star|dark matter|dark energy
solar eclipse|lunar eclipse|night sky|earth orbit|into orbit
science fiction|nobel prize in physics|nobel prize in chemistry|nobel prize in medicine
science and technology|scientific research|research team|research findings
researchers say|researchers found|researchers have found|scientists say|scientists have
scientists found|study finds|study suggests|new study|studies suggest|a new study
according to a study|research suggests|new research|published in the journal
clinical trial|medical research|stem cell|stem cells|bone marrow|blood cell
gene therapy|genetic code|genetic mutation|human genome|human evolution
bird flu virus|flu vaccine|hiv vaccine|heart disease|heart attack risk|blood pressure
cancer risk|breast cancer|lung cancer|cancer cells|immune system|health benefits
side effects|drug trial|experimental drug|disease control and prevention
national institutes of health|food and drug administration|world health organization
global warming|climate change|greenhouse gases|ice age|ice sheet|ice cap
ozone layer|endangered species|coral reef|animal kingdom|rain forest
renewable energy|fuel cell|hydrogen fuel|solar cell|carbon dioxide
periodic table|speed of light|particle accelerator|large hadron collider
""")
_words(_T, 2.55, """
science scientific researcher research laboratory experiment discovery discovered
evidence-based breakthrough physics chemistry biology mathematics
telescope star planet planetary universe cosmos cosmic orbit rocket launchpad
moon mars venus solar sunspot atmosphere atmospheric alien meteorological
volcano seismic tectonic oceanic geological ancient extinct extinction evolutionary
skull skeleton unearthed remains cave mammal mammals amphibian amphibians
whale dolphin orangutan primate ape monkey shark elephant wildlife habitats
warming glacier glacial arctic antarctic icecap rainforest environmental ecologists
pollution emissions carbon fossil-fuel climate ozone oxygen nitrogen
medical medically biomedical medicine health illness diseases cancer tumor tumour
diabetes diabetic patients diagnosis diagnosed treatment therapy medication
drug drugs dosage prescription clinical trial laboratory therapeutic
infections infectious virus viral bacteria bacterial outbreak epidemic
influenza flu aids hiv malaria sars polio ebola chickenpox tuberculosis
obesity nutrition smoking tobacco fertility reproductive pregnancy
psychiatry psychology hospital surgery surgical surgeon physician
""")
_words(_T, 1.3, """
study studies findings journal researchers professor university team-based
tested testing tests test experimental experimentalists experts found
model models system systems tool tools service users user machine
communications information screen data version launched launch release
site sites powered design designed solution solution-based robot
environment air water temperature tropical forest fish birds animal
brain blood cell cells risk symptoms scientists-reported
""")

# Sport-specific vocabulary and scoring language.
_words(_S, 5.1, """
sports sport sporting sportsman sportswoman sportsmanship athlete athletic athletics
olympics olympic paralympic paralympics olympiad olympian medalist medallist medals
baseball softball mlb ballpark slugger shortstop pitcher pitching inning innings
bullpen outfielder infielder catcher baseman rightfielder lefthander righthander
homered homer homers homering rbi rbis batting batter batsman batters strikeouts
touchdown touchdowns gridiron football footballer quarterback linebacker cornerback
tailback fullback halfback wideout kicker punt punter interception sacks nfl ncaa
basketball nba wnba rebound rebounds dunk layup hoops postseason playoffs playoff
hockey nhl puck goalie goaltender slapshot powerplay
soccer fifa uefa premiership midfielder striker defender goalkeeper footballers
winger hattrick offside equaliser equalizer routs relegation relegated
rugby scrum flyhalf allblacks wallabies springboks cricketer cricket wicket wickets
bowler bowling century overs odi lbw batted runout spinner wicketkeeper test-match
tennis wta atp tiebreak tiebreaker forehand backhand wimbledon racquet doubles
golf golfer pga lpga putt putting birdie birdied bogey eagle-putt fairway
leaderboard clubhouse ryder nascar indycar motorsport motorcycling motocross
pole-sitter formula1 racecar speedway grandprix
boxing boxer heavyweight welterweight middleweight featherweight bout wbc ibf wba
wrestler wrestling judo judoka taekwondo fencing archery badminton volleyball
handball triathlon biathlon marathon decathlon heptathlon hurdles hurdler sprinter
gymnast gymnastics equestrian dressage swimmer swimming freestyle backstroke
breaststroke butterfly-stroke weightlifter weightlifting cyclist cycling peloton
skiing skier slalom bobsled luge skating skater snowboarding snowboarder
lacrosse billiards snooker darts futsal netball curling
championship championship-winning semifinal semifinals semifinalist quarterfinal
quarterfinals finalist finals grandfinal tournament tourney hat-trick
""")
_phr(_S, 5.8, """
world cup|world series|stanley cup|super bowl|superbowl|champions league
uefa cup|uefa nations league|premier league|premiership title|football league
championship league|league cup|fa cup|carling cup|liga title|la liga|serie a
bundesliga|primera liga|major league|minor league|little league|american league
national league|division series|wild card|pennant race|spring training
national football league|national basketball association|national hockey league
hall of fame|hall of famer|pro bowl|bcs standings|bowl championship series
college football|college basketball|big ten|big east|pac 10|acc tournament
all star|all stars|all pro|all american|most valuable player|free agent
free agency|first round pick|draft pick|rookie of the year|coach of the year
game winner|game winning|winning streak|losing streak|two run|home run
grand slam|run homer|run single|run double|three pointer|three pointers
free throw|triple double|scored twice|scored two|scored a goal|minutes remaining
scored points|points and rebounds|goal scorer|field goal|penalty shootout
penalty kick|red card|yellow card|friendly match|man of the match
test cricket|test series|test match|one day international|one dayer|limited overs
davis cup|fed cup|hopman cup|masters cup|trophy series|us open|usopen
u s open|french open|australian open|british open|china open|japan open
pga tour|european tour|champions tour|ryder cup|solheim cup|buick open
formula one|formula 1|grand prix|champ car|nextel cup|busch series
indy 500|pit stop|pole position|tour de france|tour of spain|yellow jersey
america's cup|breeders cup|kentucky derby|horse racing|at the track
summer games|winter games|athens games|athens olympics|olympic games
gold medal|silver medal|bronze medal|medal count|world record|personal best
track and field|time trial|100 metres|100 meters|meter dash|metre dash
anti doping|doping test|performance enhancing|anabolic steroids|drug test
title bout|world heavyweight|knocked out in|boxing ring|mixed martial arts
head coach|assistant coach|offensive coordinator|defensive coordinator
kick off|kickoff return|end zone|running back|wide receiver|tight end
defensive back|offensive line|defensive tackle|point guard|shooting guard
second baseman|first baseman|third baseman|designated hitter|starting pitcher
seeded first|top seed|second seed|top seeded|straight sets|straight set
first leg|return leg|round robin|quarter final|semi final|title defence
training camp|transfer window|transfer fee|signing bonus|contract extension
sports network|sports illustrated|sporting news|sportsline|skysports|si com|espn
""")
_words(_S, 3.05, """
champion champs champions medal bronze silver-medal gold-medal defending
athletes runner runners marathoner relay sprinters trackside
team teammate team-mates coach coaches coaching player players playmaker
rookie rookie-season veteran captain skipper squad roster lineup line-up
league cup trophy stadium arena fieldhouse pavilion dugout locker-room
fixture qualifying qualifier pole vault seed seeded unseeded draw
victory victors victorious defeated defeat beats beat beaten won wins win winner
scoring scorer scored score goalless scoreless consolation own-goal
playoffs relegation clinch clinched berth standings sweep swept unbeaten undefeated
comeback squeaker overtime penalty foul ejected suspension suspended
injury injured sidelined ankle knee hamstring shoulder ligament sprain
rally rallied rallies romped rout thrashed trounced knocked-out outlasted
match game matchday halftime half-time contest showdown faceoff opener
retirement retires signed signing resigns derby rematch training
swimming cycling racing racecourse contender fumble forecheck batter dismissed
yardage yards touchdown kick tackle assist shots saves slam lap laps
""")
_words(_S, 1.28, """
season round season-ending top ranking ranked rankings final place lead
led leads lead-off tie tied drew draw streak series result results
host hosts record bid best second straight title challenge action
Saturday Sunday Monday Tuesday Wednesday Thursday Friday afternoon night
crowd fans supporters star legendary hero captaincy manager boss
promoted debut return comeback edge edges edge-out lift lifts blanks
downed topples topple snaps stops ruins sinks ousts cruise cruises
winless stuns stunner shock upset shocker giantkiller opens outshot
defence offense offensive defense defensive bench field yard run runs
drill practice athlete-only camp arena course lap clock seconds
""")
# Club/national-team names and sports figures disambiguate short recaps.
_phr(_S, 5.4, """
yankees|red sox|white sox|sox|mets|orioles|blue jays|devil rays|tampa bay rays
indians baseball|cleveland indians|royals|detroit tigers|minnesota twins
texas rangers|oakland athletics|angels baseball|anaheim angels|seattle mariners
phillies|marlins|expos|braves|cubs|pirates baseball|st louis cardinals
houston astros|astros|brewers|cincinnati reds|dodgers|san francisco giants
colorado rockies|padres|diamondbacks|d backs|washington nationals
new england patriots|buffalo bills|miami dolphins|new york jets|ravens
steelers|cincinnati bengals|cleveland browns|indianapolis colts|titans
jacksonville jaguars|houston texans|broncos|oakland raiders|las vegas raiders
kansas city chiefs|chargers|philadelphia eagles|dallas cowboys|redskins
green bay packers|chicago bears|minnesota vikings|detroit lions|packers
falcons|carolina panthers|buccaneers|tampa bay bucs|new orleans saints
seahawks|49ers|st louis rams|arizona cardinals|new york giants
lakers|celtics|knicks|76ers|sixers|raptors|pistons|cleveland cavaliers
pacers|chicago bulls|milwaukee bucks|miami heat|orlando magic
washington wizards|charlotte bobcats|atlanta hawks|minnesota timberwolves
nuggets|utah jazz|trail blazers|supersonics|dallas mavericks|san antonio spurs
houston rockets|memphis grizzlies|new orleans hornets|golden state warriors
phoenix suns|clippers|sacramento kings|nets basketball|new jersey nets
maple leafs|canadiens|senators hockey|edmonton oilers|calgary flames|canucks
boston bruins|buffalo sabres|detroit red wings|blackhawks|avalanche hockey
blue jackets|sharks hockey|new jersey devils|ny rangers|islanders hockey
philadelphia flyers|penguins hockey|carolina hurricanes|mighty ducks|predators hockey
manchester united|man utd|man united|manchester city|arsenal|chelsea|liverpool
everton|fulham|tottenham|hotspur|newcastle united|blackburn rovers|bolton wanderers
aston villa|crystal palace|west brom|portsmouth fc|leeds united|southampton fc
west ham|middlesbrough|charlton athletic|sunderland|wolverhampton wanderers
real madrid|atletico madrid|ac milan|inter milan|juventus|lazio|as roma
bayern munich|borussia|bayer leverkusen|werder bremen|schalke|fc porto
ajax amsterdam|psv eindhoven|feyenoord|paris saint germain|olympique lyon
glasgow celtic|glasgow rangers|old trafford|stamford bridge|highbury|anfield
new zealand all blacks|all blacks|springboks|wallabies|british lions
fighting irish|notre dame|ohio state|florida state|usc trojans|oklahoma sooners
wolverines|buckeyes|seminoles|longhorns|aggies|tar heels|blue devils
cornhuskers|crimson tide|nittany lions|boilermakers|hawkeyes|hokies
barry bonds|babe ruth|sammy sosa|mark mcgwire|alex rodriguez|a rod
derek jeter|mariano rivera|joe torre|randy johnson|pedro martinez|david ortiz
manny ramirez|curt schilling|roger clemens|ichiro|albert pujols|cabrera homer
lebron|kobe bryant|shaq|shaquille|michael jordan|kevin garnett|yao ming
vince carter|tracy mcgrady|dirk nowitzki|tim duncan|allen iverson|carmelo anthony
peyton manning|eli manning|tom brady|brett favre|donovan mcnabb|terrell owens
michael vick|ben roethlisberger|bill belichick|joe gibbs|bill parcells
wayne gretzky|mario lemieux|sidney crosby|martin brodeur|gary bettman
roger federer|federer|andy roddick|roddick|lleyton hewitt|andre agassi|agassi
tim henman|henman|marat safin|david nalbandian|rafael nadal|djokovic
serena williams|venus williams|serena|sharapova|mauresmo|davenport tennis
justine henin|henin hardenne|kim clijsters|kuznetsova|myskina|dementieva
tiger woods|vijay singh|ernie els|phil mickelson|mickelson|sergio garcia
retief goosen|padraig harrington|davis love|jack nicklaus|annika sorenstam
michael schumacher|schumacher|rubens barrichello|barrichello|jenson button
raikkonen|fernando alonso|juan pablo montoya|dale earnhardt|jeff gordon
jimmie johnson|kurt busch|lance armstrong|jan ullrich|tyler hamilton
sachin tendulkar|tendulkar|rahul dravid|sourav ganguly|virender sehwag
brian lara|ricky ponting|shane warne|glenn mcgrath|andrew flintoff
michael vaughan|michael owen|david beckham|beckham|ronaldo|ronaldinho
thierry henry|wayne rooney|rooney|zidane|mourinho|arsene wenger|alex ferguson
lionel messi|pele|maradona|michael phelps|ian thorpe|marion jones|paula radcliffe
amir khan boxer|mike tyson|oscar de la hoya|bernard hopkins|lennox lewis
""")
_words(_S, 2.95, """
sooner sooners terrapins wildcats jayhawks gators badgers huskies bulldogs trojans
spartans volunteers razorbacks cardinals eagles vikings bears cowboys colts
bucs buccaneers patriots rams bengals raiders dolphins lions chiefs titans
mariners jays twins reds tigers angels royals giants mets nationals
hornets mavericks mavs spurs cavaliers cavs grizzlies bobcats blazers warriors
bruins senators leafs ducks panthers sharks flyers penguins lightning
rangers celtic barca barcelona valencia deportivo juventus merseyside
ferrari mclaren renault williams-bmw bridgestone ducati yamaha motogp
athens athenians ioc doping balco steroid olympia paralympians
""")

# Public affairs: armed conflicts, political actors, justice and disasters.
_words(_W, 4.25, """
war warfare warlord guerrilla guerilla guerrillas militants insurgency insurgents
insurgent rebels rebel separatist militia militiamen jihadist jihad militants
terrorism terrorist terror terroristic jihadists islamist islamicist
hostage captor abducted kidnappers kidnapper kidnapping abductees detainee
ransom beheaded beheading decapitated executed massacre genocide bloodshed
assassinated assassination murdered murder homicide killings killer slain
bomb bombed bombing bombings bomber car-bomb explosives dynamite landmine
explosion blast airstrike airstrikes mortar artillery missile warplane
troops troop soldiers soldier marines infantry paratroopers peacekeepers
military army navy airforce naval battalion brigade generalissimo
offensive ceasefire truce peacekeeping peacekeepers disarmament disarm
invasion invaded occupation occupied withdraws withdrawal redeployment
attackers gunmen gunman gunfire gunshot shooting shelling firefight clashes
wounded casualties deaths deadliest fatalities violence violent deadly
election elections electorate electoral reelection reelectionist referendum
ballot ballots voters voter voting polls pollsters polling caucus
parliament parliamentarian parliamentary congressmen congressman congresswoman
lawmakers legislator legislation legislature bipartisan democrat republican
democratic party-political opposition incumbent coalition cabinet government
minister premier presidency presidential chancellor monarchy monarch kingmaker
diplomat diplomatic diplomacy envoy ambassador multilateral bilateral summit
sanctions treaty sovereignty sovereign constitution constitutional amnesty
coup dictatorship dictator autocratic regime junta martial-law impeachment
protester protestors protesters demonstrations crackdown activists dissident
refugee asylum deportation immigrant immigration migrant humanitarian
earthquake quake aftershock tsunami tidal-wave hurricane typhoon cyclone
tornadoes landslide mudslide avalanche flooding floods floodwaters
famine drought disaster devastation evacuation evacuees displaced
criminal accused arrested arrests custody manslaughter rape rapist robbery
burglar burglary heist smuggling smuggler trafficking narcotics
prisoner prison jail jailed sentencing sentenced acquitted convicted
extradition prosecution prosecutors prosecutor indictment indicted trial
policeman policewoman constable sheriff coroner inquest detective fugitives
""")
_phr(_W, 5.6, """
white house|oval office|camp david|state department|us state department
prime minister|foreign minister|interior minister|defense minister|defence minister
foreign secretary|home secretary|secretary of state|secretary of defense
president bush|president george|george w bush|george bush|bush administration
john kerry|john edwards|dick cheney|colin powell|donald rumsfeld|condoleezza rice
tony blair|vladimir putin|jacques chirac|silvio berlusconi|gerhard schroeder
kofi annan|un secretary general|united nations|security council|general assembly
peace talks|peace process|peace agreement|peace deal|peace treaty
nuclear weapons|weapons of mass destruction|nuclear arms|nuclear program
nuclear programme|atomic energy agency|uranium enrichment|nuclear watchdog
middle east|west bank|gaza strip|palestinian territories|palestinian authority
ariel sharon|yasser arafat|yassir arafat|mahmoud abbas|israeli troops
saddam hussein|saddam|abu ghraib|abu musab|al zarqawi|ayad allawi|iyad allawi
moqtada al sadr|muqtada al sadr|mahdi army|green zone|sunni triangle
al qaeda|al qaida|al jazeera|bin laden|bin ladin|september 11 attacks
suicide bomber|suicide bombing|suicide attack|car bomb|roadside bomb
military operation|military base|military action|armed forces|army chief
coalition forces|security forces|rebel forces|law enforcement|police officers
police said|authorities said|was killed|people killed|people were killed|killed in
wounded in|death toll|were injured|killed at least|people dead|people died
state of emergency|emergency services|natural disaster|red cross|aid workers
human rights|civil rights|civil war|civil unrest|humanitarian aid|relief effort
war on terror|war on terrorism|war crimes|international criminal court
supreme court|high court|death penalty|life sentence|death row
guilty plea|pleaded guilty|pleaded not guilty|on trial|murder trial
criminal charges|charged with murder|district attorney|behind bars
general election|presidential election|election campaign|election day
national convention|running mate|electoral college|exit polls|opinion polls
votes cast|polling station|ballot box|vote count|campaign trail|presidential debate
republican party|democratic party|labour party|conservative party|ruling party
opposition party|opposition leader|house of representatives|capitol hill
house of commons|national assembly|european parliament|political party
foreign policy|foreign affairs|national security|homeland security
international community|heads of state|african union|arab league|group of eight
european union leaders|northern alliance|irish republican army|tamil tigers
north korea|north korean|sudan darfur|darfur region|hague tribunal
pope john paul|pope francis|roman catholic church|anglican church|dalai lama
buckingham palace|british royal family|prince charles|queen elizabeth
""")
_words(_W, 4.65, """
iraq iraqi iraqis baghdad fallujah falluja ramadi najaf sadr karbala kirkuk mosul
basra sunni shiite shia kurd kurdish kurds peshmerga
afghanistan afghan afghans kabul taliban karzai pakistan musharraf
palestine palestinian palestinians gaza ramallah intifada hamas fatah
hezbollah hizbollah hebron jenin sharon arafat israeli israelis jerusalem
lebanon beirut syria syrian damascus tehran ayatollah
darfur sudan sudanese khartoum janjaweed somalia somali mogadishu
rwanda kigali congo kinshasa liberia liberian monrovia harare mugabe
chechnya chechen chechens beslan grozny caucasus ossetia ingushetia
kashmir kashmiri tamil ltte nepalese maoist coup plotters
haiti haitian aristide pyongyang dprk myanmar burmese suu kyi
putin kremlin yushchenko yanukovych kuchma lukashenko milosevic
kosovo serbs belgrade bosnian macedonia hague montenegro
bush cheney kerry rumsfeld blair berlusconi chirac annan powell pows
obama biden trump clinton zelensky zelenskyy netanyahu zelenskiy
pentagon nato iaea nato-led interpol fbi cia guantanamo gitmo
kremlin downing whitehall westminster vatican pope papal archbishop
""")
_words(_W, 2.6, """
politics political politician official authorities administration ministry
president leader leadership ministerial senatorial senator senate congress
council mayor governor mayoral county federal federation national assembly
statehood independence independent-state democracy democratic communist socialist
royal king queen prince princess throne emperor ruler cleric clerical
conservative liberal centrist nationalist nationalism party leftist rightwing
speech address campaign pledge vote support law bill reform policy policies
delegation conference visit meeting talks negotiation negotiate dispute mediation
condemned denounced urged vowed accused allegations corruption bribery
intelligence spy spies espionage agent border frontier checkpoint patrol
security raid raided raid police officer guard guards force gun armed arms
combat battle fighting combatants conflict tensions crisis allied ally allies
protest march strike rally demonstrators riot mob unrest marchers blockade
attack attacked attacks threat retaliation revenge assault investigation inquiry
death dead killed kill injure injured hurt missing survivor survived rescued rescue
crash crashed collision wreckage sank sinking fire flames wildfire firefighter
tragedy victim mourning mourn mourners funeral cemetery widow memorial
church christian catholic christianity muslim islam islamic jewish jews mosque
synagogue religious religion faith priest bishop parish abuse ban banned
court judge hearing jury lawyer illegal guilty suspect sentenced fugitives crime
citizens residents civilians villagers village capital province provincial
aid relief camp storm rain torrential monsoon coastal magnitude richter
epicenter inundated stranded homeless tropical-storm electioneering
""")
_phr(_W, 3.6, """
national hurricane center|tropical storm|gulf coast|florida coast|heavy rains
flash flood|strong quake|rescue workers|emergency landing|plane crash
train crash|air crash|crashed into|on board were|search and rescue
hurricane ivan|hurricane charley|hurricane frances|hurricane jeanne
presidential candidate|senior official|spokesman said|police chief
international affairs|climate talks|un resolution|un mission|un troops
human shield|embassy compound|mass grave|mass graves|militant group
claimed responsibility|opening fire|opened fire|oil for food
under fire|rocket fire|waving flags|no confidence|to the polls
foreign ministry|defence ministry|defense ministry|arab world
nobel peace prize|nobel literature prize|royal palace|first lady
prime minster|under arrest|in custody|prison sentence|national guard
war torn|weapons inspectors|battle against terrorism|on charges of
reuters alertnet|voice of america|radio free europe
""")

# Small contextual cues, intentionally weaker than topical content.
_words(_W, 1.05, """
international foreign regional nation nations country countries national global
american british french german russian turkish chinese indian japanese italian
spanish pakistani malaysian indonesian philippine vietnamese cambodian cambodia
iraqi iranian african brazilian egyptian libyan saudi turkish jordanian
israel iran ukraine russia beijing moscow paris berlin london cairo
riyadh amman jeddah islamabad delhi kathmandu ankara athens tripoli
ankara brussels luxembourg strasbourg geneva jakarta taipei seoul
bangladesh dhaka manila thailand bangkok turkey indonesia indonesia
island islands coast africa europe asia south north east west
people told said reported yesterday friday sunday monday tuesday thursday
""")
# Additional common news beats.
_phr(_B, 4.7, """
world economic forum|organization of petroleum exporting countries|light sweet crude
oil cartel|oil minister|record oil|price of oil|cost of oil|nymex crude
world biggest retailer|world largest retailer|world largest automaker
profit rose|profit fell|profit jumped|sales rose|sales fell|posted a loss
posted a profit|boost profits|reported a loss|reported a profit|raise prices
company said|company reported|credit crunch|debt crisis|wealth management
bankruptcy court|securities fraud|insider trading|money laundering
annual revenue|annual sales|operating profit|operating income|net income
net loss|quarter loss|third quarter|second quarter|first quarter|fourth quarter
year on year|market share|cash flow|balance sheet|bottom line
raise capital|raising capital|capital spending|capital expenditure|share capital
business leaders|business group|growth rate|trade gap|currency traders
federal funds|prime rate|tax cuts|tax breaks| tax relief|tax evasion
oil and gas|housing prices|retail sales|consumer goods|luxury goods
out of work|gold prices|stock options|stock split|stock futures
london stocks|tokyo stocks|us stocks|asian stocks|european stocks
gross profit|share price|selling price|bond prices|10 year note
transportation department|discount carrier|flag carrier|low cost carrier
low fare|no frills airline|air fares|ticket prices|going public
rupert murdoch|richard branson|walt disney co|michael eisner|ted turner
""")
_phr(_T, 4.1, """
cell biology|laboratory animals|national academy of sciences|american medical association
science magazine|scientific journal|a team of researchers|million years ago
billion years ago|oldest known|new species|deep sea|space center
computer model|fingerprint sensor|electronic voting|voting machines|internet phone
broadband connection|adsl line|sharing network|pop up ads|search tool
graphics card|home network|home networking|component maker|printer maker
metal detector|mobile music|satellite radio|mobile computing|digital television
digital tv|digital rights management|open standard|web based|grid computing
high definition|on demand video|video on demand|on demand computing
tech companies|tech firms|business software|high speed connection|high bandwidth
personal data|personal information|intel corp|apple store|playstation portable
martian surface|nobel physics|space race|mass extinction|wildlife conservation
weather satellite|hydrogen powered|hybrid engine|rechargeable battery
mobile technology|mobile gaming|interactive entertainment|internet piracy
computer network|computer systems|user interface|data mining|autonomic computing
""")
_phr(_S, 4.1, """
walk off|extra innings|last gasp|injury time|stoppage time|season opener
league leaders|points behind|out of contention|defending champions|first half
second half goal|in the second half|regular season|at home to|away win
come from behind|golden goal|against the run of play|captaincy|title hopes
title race|league debut|season debut|sent off|knockout stages|beat rivals
opening round|second round|third round|first set|final round|final lap
final whistle|tee off|under par|over par|under 19|team usa
international olympic committee|world anti doping|football association
cricket board|all rounder|test captain|fast bowler|bad light|follow on
century stand|ran for|yards rushing|yards passing|ankle injury|out for season
career high|season high|career best|club record|cup tie|locker room
monday night football|champions trophy|pro football|women open|men final
boston marathon|indianapolis 500|league baseball|little leaguers|home ground
""")

# Some ordinary words strongly favor different sections in particular collocations.
_phr(_W, 5.2, """
military strike|air strike|air strikes|missile strike|military offensive
tiger rebels|tamil tiger|detention center|pirate attack|peace accord
terror alert|kidnap victim|armed robbery|violent crime|bird flu outbreak
war crimes tribunal|riot police|storm surge|hit by hurricane|hurricane force
election victory|won the election|won the presidency|voter turnout|road map for peace
""")
_phr(_B, 5.3, """
workers strike|strike action|pay dispute|labor dispute|stock rally|stocks rally
market rally|rebound in oil prices|fuel surcharge|bank of china|airline pilots
world oil|economic policy|pension reform|federal budget|state owned bank
finance ministry|energy department|department of energy|world economy
""")
_phr(_S, 5.2, """
players union|players association|nhl lockout|salary cap|players championship
athletics federation|football federation|football club|basketball team|medical timeout
gold in the|international cricket council|test victory|european champions
new zealand rugby|national team coach|grand national|appointed captain
""")

@lru_cache(maxsize=8192)
def _variants(t):
    # The unchanged word is handled separately. Use conservative inflections,
    # particularly for place names, acronyms and lexical plurals like "Windows".
    v = []
    if len(t) > 3 and t.endswith("s") and not t.endswith(("ss", "us", "is", "ous")):
        v.append(t[:-1])
        if t.endswith(("sses", "xes", "zes", "ches", "shes", "oes")):
            v.append(t[:-2])
        if t.endswith("ies"):
            v.append(t[:-3] + "y")
        if t.endswith("men"):
            v.append(t[:-3] + "man")
    if t.endswith("men") and len(t) > 4:
        v.append(t[:-3] + "man")
    if len(t) >= 5 and t.endswith("ed"):
        base = t[:-2]
        v.extend((base, t[:-1]))
        if base.endswith("i"):
            v.append(base[:-1] + "y")
        if len(base) > 2 and base[-1] == base[-2]:
            v.append(base[:-1])
    if len(t) >= 6 and t.endswith("ing"):
        base = t[:-3]
        v.extend((base, base + "e"))
        if base[-1] == base[-2]:
            v.append(base[:-1])
    return tuple(v)

# Avoid treating generic calendar words or compass directions as topics.
for _k in """
sunday monday tuesday wednesday thursday friday saturday yesterday said
north east south west national told
""".split():
    _lex.pop((_k,), None)

def _scores(tokens):
    evidence = [[] for _ in range(4)]
    n = len(tokens)
    for i in range(n):
        for j in range(i + 1, min(n, i + _maxlen) + 1):
            k = tuple(tokens[i:j])
            rec = _lex.get(k)
            if rec:
                for c, (val, flag) in rec.items():
                    evidence[c].append((val, i, j, k, flag))
            else:
                for v in _variants(k[-1]):
                    k1 = k[:-1] + (v,)
                    rec1 = _lex.get(k1)
                    if rec1:
                        for c, (val, flag) in rec1.items():
                            evidence[c].append((val * .95, i, j, k1, flag))
                        break
    scores = [0.35, 0.1, 0.0, 1.05]
    flags = {}
    for c, spans in enumerate(evidence):
        taken = set()
        counts = {}
        weak = 0.0
        medium = 0.0
        strong = 0.0
        for val, i, j, key, flag in sorted(spans, key=lambda x: (-x[0], x[1], -x[2])):
            if any(t in taken for t in range(i, j)):
                continue
            taken.update(range(i, j))
            seen = counts.get(key, 0)
            counts[key] = seen + 1
            if seen >= 3:
                continue
            mult = (1.58 if i < 7 else 1.28 if i < 12 else 1.05 if i < 22 else 1.0)
            if n > 100 and i > 70:
                mult *= .78
            adjusted = val * mult * (1.0, .47, .19)[seen]
            if val <= 1.8:
                weak += adjusted
            elif val <= 3.6:
                medium += adjusted
            else:
                strong += adjusted
            if flag:
                old = flags.get(flag, (0.0, n))
                flags[flag] = (old[0] + adjusted, min(old[1], i))
        scores[c] += strong + min(medium, 20) + .64 * max(0, medium - 20)
        scores[c] += min(weak, 5.0) + .28 * min(10, max(weak - 5, 0))
    return scores, flags

def predict(state) -> dict:
    text = state if isinstance(state, str) else ""
    toks = _tokens(text)
    scores, flags = _scores(toks)
    lower = text.lower()
    # Financial figures are not the same as game scores, dates or page numbers.
    if re.search(r"(?:[$£€]\s*\d|\b(?:usd|eur|gbp)\s*\d)", lower):
        scores[_B] += 2.25
    if re.search(r"\b\d[\d.,]*\s*(?:billion|million|trillion|bln|mln|bn)\b", lower):
        scores[_B] += 2.05
    if re.search(r"\b\d+(?:\.\d+)?\s*(?:percent|per cent|%)", lower):
        scores[_B] += 2
    if re.search(r"\b\d+\s*(?:cents|pence)\b", lower):
        scores[_B] += 1.8
    if re.search(r"\b[A-Z]{1,5}\.(?:N|O|L|AX|TO|DE|PA|HK|T)\b|\b(?:NYSE|NASDAQ|AMEX)\s*:", text):
        scores[_B] += 2.5
    if re.search(r"(?<![a-z])(?:inc|corp|ltd|plc|co)\.", lower):
        scores[_B] += 1.5
    if re.search(r"\b(?:stocks?|bonds?|shares|oil|dollar|gold|prices?|profits?|sales)\s+(?:soar|plung|surge|fall|rose|ris|jump|dip|slid|climb|drop|hit|slip|rebound|tumb|softe|eas|gain|rall)", lower):
        scores[_B] += 3.8
    if re.search(r"\b(?:q[1-4]|[1-4]q|fy\d\d(?:\d\d)?)\b", lower):
        scores[_B] += 2.8
    if re.search(r"(?<![\d/-])\b(?:[0-9]|[1-9]\d|1[0-4]\d)\s*[-–]\s*(?:[0-9]|[1-9]\d|1[0-4]\d)\b(?!\s*[/\-]\d|\s*(?:year|month|week|day|percent|per cent|million|billion))", lower):
        scores[_S] += 4.8
    if re.search(r"\b(?:no\.\s*\d{1,2}\b|best.of.(?:five|seven)|[0-9]+(?:st|nd|rd|th)[ -](?:seed|minute|inning|goal|hole)|\d+[ -](?:yard|point win|under.par|wicket|game streak|stroke lead))", lower):
        scores[_S] += 4
    if re.search(r"\b(?:[0-9]+[ -](?:gb|mb|kb|mbps|ghz|mhz|megapixel)|802\.11[a-z]?|wi-fi|usb\s*[23]\.0)\b", lower):
        scores[_T] += 5
    if re.search(r"\b(?:IT (?:industry|professionals|security|managers|systems|departments?|spending)|PCs?|PDAs?|RFID|RIAA|ICANN|DVDs?|ISPs?|MP3s?)\b", text):
        scores[_T] += 2.9
    if re.search(r"\b(?:HP|SAP|RIM|AMD|ATI|TSMC|EMC)\b", text):
        scores[_T] += 2.2
    if re.search(r"\b(?:UN|U\.N\.|NATO|IAEA|FBI|GOP|Gaza)\b", text):
        scores[_W] += 1.9
    if re.search(r"\b(?:killed|wounded|dead|injured)\s+(?:at least\s+)?(?:\d+|three|four|five|six|ten|dozens)|\b(?:\d+|six|seven|eight|nine|ten)\s+(?:dead|wounded|killed)\b", lower):
        scores[_W] += 4.8
    # Corporate news about a technology vendor belongs on the technology beat.
    # A passing reference to a vendor late in a market roundup is weaker.
    if "techfirm" in flags:
        mass, first = flags["techfirm"]
        if first < 12 or mass >= 9:
            scores[_T] += 3.8 if first < 8 else 2.4
            scores[_B] *= .73 if first < 10 else .86
        elif first < 30:
            scores[_T] += 1.6
            scores[_B] *= .95
    # A few usually informational terms also occur as team names (Senators,
    # Kings, Rangers, etc.). Other evidence from the recap breaks such ties.
    if re.search(r"\b(?:beat|defeated|edged|routed|thrashed|ousted)\b", lower) and re.search(r"\b(?:win|victory|[0-9]{1,2}[-–][0-9]{1,2}|season|cup|final|league)\b", lower):
        scores[_S] += 2.5
    if len(toks) >= 2 and ("researchers" in toks or "scientists" in toks):
        scores[_T] += 2.2
    return {"answer": _NAMES[max(range(4), key=lambda c: scores[c])]}