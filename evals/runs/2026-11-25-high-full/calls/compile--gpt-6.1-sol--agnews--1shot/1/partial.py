import re
import unicodedata


_CATEGORIES = ("business", "sci_tech", "sports", "world")
_LEXICON = {}
_LENGTHS = set()


def _tokens(text):
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower().replace("’", "'").replace("‘", "'")
    for a, b in (
        ("&amp;", " and "), ("&quot;", " "), ("&apos;", "'"),
        ("&#39;", "'"), ("&nbsp;", " "), ("&lt;", " "), ("&gt;", " "),
        ("u.s.", " us "), ("u.n.", " un "), ("u.k.", " uk "),
        ("e.u.", " eu "),
    ):
        text = text.replace(a, b)
    text = re.sub(r"<[^>]*>", " ", text)
    return re.findall(r"[a-z]+(?:'[a-z]+)?|\d+(?:\.\d+)?", text)


def _add(category, weight, phrases):
    for phrase in phrases.split("|"):
        key = tuple(_tokens(phrase.strip()))
        if not key:
            continue
        values = _LEXICON.setdefault(key, {})
        values[category] = max(weight, values.get(category, 0.0))
        _LENGTHS.add(len(key))


def _phrase_set(phrases):
    return {tuple(_tokens(p.strip())) for p in phrases.split("|") if p.strip()}


# Business, markets, and non-technology industries.
_add("business", 6.5, """
wall street|stock market|stock markets|federal reserve|interest rates|
dow jones|standard and poor's|s&p 500|s&p500|bank of england|
european central bank|gross domestic product|initial public offering
""")
_add("business", 4.8, """
earnings|profits|profit|recession|inflation|merger|mergers|buyout|buyouts|
bankruptcy|bankrupt|nasdaq|ftse|nikkei|nyse|opec|ipo|
quarterly earnings|quarterly profit|quarterly loss|annual profit|
oil prices|crude prices|crude oil prices|consumer prices|
central bank|central banks|stock exchange|trade deficit|
unemployment rate|jobless rate|retail sales|same store sales|
economic growth|economic recovery|hostile takeover|hostile bid|
job cuts|job losses|credit rating|credit ratings|credit crunch|
balance sheet|income statement|profit warning|profit forecast
""")
_add("business", 3.7, """
economy|economies|economic|economists|economist|earnings forecast|
revenue|revenues|stocks|shares|shareholders|shareholder|
investors|investor|investment|investments|investing|
acquisition|acquisitions|takeover|takeovers|merging|merged|
dividend|dividends|banking|insurer|insurers|insurance|
retailer|retailers|retailing|retail|wholesaler|
commodities|commodity|futures|unemployment|jobless|
currency|currencies|deflation|stagflation|devaluation|
tariffs|tariff|exports|imports|exporters|exporter|
privatization|privatisation|pensions|pension|layoffs|layoff|
mortgage|mortgages|lending|lender|lenders|brokerage|
brokerages|securities|equities|equity|treasuries|
financial markets|financial results|financial crisis|financial services|
private equity|hedge fund|hedge funds|mutual fund|mutual funds|
stock options|stock price|stock prices|share price|share prices|
corporate earnings|business confidence|consumer confidence|
manufacturing sector|housing market|real estate|
trade talks|trade agreement|free trade|world trade organization|
world trade organisation|wto|international monetary fund|imf|
world bank|alan greenspan|jerome powell|ben bernanke
""")
_add("business", 2.8, """
sales|bank|banks|banker|bankers|finance|financial|
crude|barrel|barrels|oil|petroleum|gasoline|diesel|
yen|dollar|dollars|sterling|euro|eurozone|euro zone|
treasury|bonds|bond|debt|debts|deficit|
mining|miner|mines|steel|aluminum|aluminium|
manufacturing|manufacturer|manufacturers|factory|factories|
automaker|automakers|carmaker|carmakers|automotive|
airline|airlines|airways|airfare|airfares|
supermarket|supermarkets|shopping|retail chain|
wages|wage|payrolls|payroll|employment|
outsourcing|outsource|outsourced|redundancies|
taxes|taxation|spending|consumer spending|
purchasing|purchases|purchased|buyback|buybacks|
accounting|accountants|auditor|auditors|audit|
insolvency|liquidation|restructuring|restructured|
conglomerate|conglomerates|valuation|valuations|
chief executive officer|chief financial officer|
supply chain|chief executive|cost cutting|cost cuts|
financial times|business news|economic policy|
credit card|credit cards|venture capital|capital markets|
labor union|labour union|trade union|industrial action
""")
_add("business", 1.7, """
company|companies|corporate|corporation|corporations|corp|inc|
business|businesses|market|markets|share|stake|stakes|
quarter|quarterly|fiscal|annual|growth|forecast|forecasts|
forecasting|outlook|analyst|analysts|broker|brokers|
fund|funds|capital|portfolio|portfolios|assets|asset|
cash|cashflow|turnover|costs|cost|pricing|prices|price|
tax|taxpayer|taxpayers|budget|budgets|subsidy|subsidies|
loan|loans|credit|creditors|creditor|debit|
savings|saving|deposit|deposits|cheaper|expensive|
production|output|productivity|industrial|industry|
demand|supply|trade|trading|traded|trader|traders|
export|import|exporting|importing|shipments|
coal|copper|gold|platinum|silver|cotton|wheat|soybeans|
agriculture|agricultural|harvest|crop|crops|farmers|
commercial|commerce|franchise|franchises|
executives|executive|ceo|cfo|chairman|
union|unions|workers|employees|employee|workforce|
strike|strikes|striking|walkout|walkouts|
payout|payouts|compensation|bonus|bonuses|
antitrust|anti trust|class action|fraud|fraudulent|
lawsuit|lawsuits|litigation|settlement|settlements|
distributor|distributors|supplier|suppliers|distribution|
marketing|advertising|advertiser|advertisers|
acquire|acquires|acquired|buying|selling|sold|
deal|deals|bid|bids|bidding|auction|auctions|
investment bank|regulator|regulators|regulatory|
fuel|fuels|refinery|refineries|pipeline|pipelines|
transportation|freight|shipping|cargo|railroad|railways|
hospitality|tourism|hotels|hotel|luxury|discount|discounts
""")
_add("business", 0.65, """
million|billion|trillion|percent|percentage|per cent|
rate|rates|rise|rises|rose|fall|falls|fell|gains|gained|
loss|losses|higher|lower|increase|increased|decline|declined|
contract|contracts|orders|order|agreement|agreements|president|
rebound|rally|rallied|rallies|index|indices|indexes|
distribution|merchandise|consumer|consumers|customer|customers
""")
_add("business", 4.5, """
wal mart|walmart|kmart|sears|costco|target corp|target corporation|
home depot|lowe's|lowes|tesco|carrefour|sainsbury|sainsbury's|
marks and spencer|marks & spencer|macy's|macys|jc penney|
j c penney|gap inc|best buy|circuit city|
general motors|ford motor|ford motors|chrysler|daimlerchrysler|
daimler|volkswagen|toyota|nissan|honda|hyundai|renault|peugeot|
coca cola|pepsi|pepsico|mcdonald's|mcdonalds|starbucks|
burger king|yum brands|procter and gamble|procter & gamble|
unilever|nestle|kraft|heinz|anheuser busch|sabre holdings|
exxon|exxonmobil|exxon mobil|chevron|texaco|conocophillips|
royal dutch shell|royal dutch|halliburton|schlumberger|
goldman sachs|morgan stanley|jpmorgan|jp morgan|j p morgan|
citigroup|citibank|bank of america|wells fargo|
merrill lynch|credit suisse|deutsche bank|ubs|hsbc|barclays|
royal bank of scotland|bank of japan|bank of china|
lehman brothers|bear stearns|american express|mastercard|
fannie mae|freddie mac|aig|allianz|prudential|
berkshire hathaway|warren buffett|blackrock|
enron|parmalat|arthur andersen|martha stewart|
united airlines|american airlines|british airways|
delta air lines|delta airlines|southwest airlines|
continental airlines|northwest airlines|us airways|
air france|klm|lufthansa|ryanair|easyjet|qantas|
singapore airlines|cathay pacific|virgin atlantic|
boeing|airbus|bombardier|general electric|
lockheed martin|northrop grumman|raytheon|
fedex|federal express|united parcel service|
disney|walt disney|time warner|news corp|viacom|
comcast|cbs corp|nbc universal|vivendi|
nike|adidas|reebok|puma|gucci|louis vuitton|
hilton|marriott|intercontinental hotels|
de beers|rio tinto|bhp billiton|anglo american
""")
_add("business", 2.4, """
ford|gm|fiat|shell|bp|delta|boeing co|gmac|
pfizer|merck|glaxosmithkline|glaxo|astrazeneca|
sanofi|novartis|roche|bristol myers|eli lilly|
johnson and johnson|johnson & johnson|abbott laboratories|
wyeth|bayer|schering|amgen|genentech|
dreamworks|mgm|paramount|universal studios|
american international group|sec|ftc|dow|dow industrials
""")

# Science, computing, telecommunications, and technology businesses.
_TECH_COMPANIES_TEXT = """
microsoft|google|apple|apple computer|apple inc|ibm|
international business machines|intel|amd|advanced micro devices|
nvidia|qualcomm|broadcom|texas instruments|tsmc|
cisco|cisco systems|oracle|sap|salesforce|adobe|macromedia|
dell|hewlett packard|hp|compaq|gateway|lenovo|acer|asus|
sun microsystems|silicon graphics|silicon image|
yahoo|yahoo's|ebay|e bay|amazon|amazon.com|amazon com|
aol|america online|lycos|ask jeeves|ask.com|ask com|
facebook|meta platforms|instagram|whatsapp|tiktok|bytedance|
twitter|youtube|snapchat|pinterest|reddit|linkedin|
netflix|spotify|paypal|square inc|stripe|
openai|open ai|anthropic|deepmind|chatgpt|gpt|
samsung|samsung electronics|lg electronics|panasonic|
sony|sony ericsson|ericsson|nokia|motorola|blackberry|
research in motion|rim|palmone|palm one|palm inc|
nortel|lucent|alcatel|avaya|siemens|fujitsu|toshiba|nec|
verizon|at&t|at and t|sprint|t mobile|tmobile|
vodafone|deutsche telekom|france telecom|british telecom|
bt group|telecom italia|telefonica|ntt|ntt docomo|
china mobile|china telecom|china unicom|mci|worldcom|
skype|vonage|earthlink|bellsouth|qwest|
symantec|mcafee|kaspersky|trend micro|sophos|
red hat|redhat|novell|suse|canonical|mozilla|opera software|
netscape|realnetworks|real networks|napster|kazaa|bittorrent|
sandisk|seagate|western digital|hitachi|emc|netapp|
micron|infineon|stmicroelectronics|arm holdings|
applied materials|asml|xilinx|altera|
nintendo|sega|electronic arts|activision|blizzard|ubisoft|
take two interactive|rockstar games|konami|capcom|
logitech|creative technology|creative labs|epson|lexmark|
3com|juniper networks|d link|netgear|belkin|
akamai|cloudflare|snowflake|databricks|palantir|
spacex|blue origin|tesla|baidu|alibaba|tencent|huawei|xiaomi
"""
_add("sci_tech", 5.2, _TECH_COMPANIES_TEXT)
_TECH_ENTITIES = _phrase_set(_TECH_COMPANIES_TEXT)

_add("sci_tech", 6.3, """
computer virus|computer viruses|computer worm|computer worms|
internet security|cyber security|cybersecurity|cyber attack|cyberattack|
cyber attacks|cyberattacks|denial of service|data breach|data breaches|
identity theft|operating system|operating systems|
open source|source code|artificial intelligence|machine learning|
large language model|large language models|neural network|neural networks|
quantum computing|quantum computer|generative ai|
video game|video games|videogame|videogames|
computer game|computer games|game console|games console|
mobile phone|mobile phones|cell phone|cell phones|cellphone|cellphones|
smartphone|smartphones|smart phone|smart phones|
search engine|search engines|web browser|web browsers|
personal computer|personal computers|personal data|
world wide web|worldwide web|internet explorer|
windows xp|windows vista|windows server|windows 11|windows 10|
service pack|service pack 2|mac os|mac os x|
playstation|playstation 2|playstation 3|playstation 4|playstation 5|
xbox|xbox 360|gamecube|game boy|gameboy|nintendo ds|nintendo switch|
grand theft auto|world of warcraft|half life 2|halo 2|
dvd player|dvd players|blu ray|high definition television|
voice over internet|voice over ip|voice over internet protocol|
wireless network|wireless networks|wireless networking|
broadband internet|internet access|internet service provider|
federal communications commission|fcc|
bill gates|steve jobs|steve ballmer|steve wozniak|
larry page|sergey brin|eric schmidt|mark zuckerberg|
tim cook|satya nadella|jensen huang|sam altman|
linus torvalds|tim berners lee|linus torvalds|
international space station|hubble space telescope|
james webb|mars rover|mars rovers|space shuttle|
human genome|stem cell|stem cells|clinical trial|clinical trials|
study finds|researchers found|scientists found|scientists discover|
global warming|climate change|greenhouse gases
""")
_add("sci_tech", 4.3, """
software|hardware|internet|broadband|semiconductor|semiconductors|
chipmaker|chipmakers|microprocessor|microprocessors|
microchip|microchips|processor|processors|silicon chips|
computing|computer|computers|laptop|laptops|notebook computer|
desktop computer|desktop computers|supercomputer|supercomputers|
telecommunications|telecom|telecoms|telephony|
smartwatch|wearable technology|wearables|
bluetooth|wifi|wi fi|wimax|voip|dsl|adsl|rfid|
malware|spyware|ransomware|adware|phishing|
hacker|hackers|hacking|hacked|botnet|botnets|
firewall|firewalls|encryption|cryptography|cryptographic|
antivirus|anti virus|anti spam|spam filter|spam filters|
linux|unix|android|ios|ios 18|macintosh|imac|macbook|
ipod|ipods|iphone|iphones|ipad|ipads|itunes|
gmail|hotmail|outlook express|firefox|thunderbird|
mozilla firefox|google chrome|google maps|google earth|
google search|google news|google drive|
photoshop|acrobat|flash player|microsoft office|
powerpoint|excel|windows media|media player|
java software|java programming|javascript|python programming|
html|xml|sql|database|databases|server|servers|
mainframe|mainframes|motherboard|motherboards|
graphics card|graphics cards|hard drive|hard drives|
hard disk|hard disks|flash memory|memory chip|memory chips|
usb|firewire|ethernet|modem|modems|routers|router|
webcam|webcams|screensaver|screensavers|screen saver|
nanotechnology|nanotech|biotechnology|biotech|bioinformatics|
robotics|robotic|robots|robot|automation|
scientist|scientists|researcher|researchers|
astronomer|astronomers|astronomy|astrophysics|cosmology|
physicist|physicists|physics|quantum|particle physics|
biologist|biologists|biology|microbiology|
genetics|geneticist|geneticists|genome|genomes|genomic|genomics|
neuroscience|neuroscientists|paleontologist|paleontologists|
archaeologist|archaeologists|archaeology|paleontology|
nasa|esa|astronaut|astronauts|cosmonaut|cosmonauts|
spacecraft|spaceship|spaceships|satellite|satellites|
telescope|telescopes|observatory|observatories|
mars|martian|cassini|huygens|hubble|voyager|rosetta|
asteroid|asteroids|comet|comets|meteorite|meteorites|
exoplanet|exoplanets|galaxy|galaxies|supernova|supernovae|
black hole|black holes|dark matter|dark energy|big bang|
solar system|solar flare|solar flares|solar wind|
lunar|moon landing|moon mission|space station|
fossil|fossils|dinosaur|dinosaurs|prehistoric|
dna|rna|mrna|chromosome|chromosomes|cloning|cloned|
crispr|gene editing|gene therapy|genetically modified|
alzheimer's|alzheimer|alzheimers|parkinson's|parkinsons|
cancer research|cancer treatment|cancer cells|
medical research|scientific research|scientific discovery|
nobel prize in physics|nobel prize in chemistry|
new species|endangered species|human evolution
""")
_add("sci_tech", 2.7, """
technology|technologies|technological|tech|high tech|hi tech|
digital|electronic|electronics|wireless|mobile|handset|handsets|
cellular|portable|computers'|computers's|
networking|networked|online|web|website|websites|web site|web sites|
webpage|webpages|web page|web pages|homepage|
email|emails|e mail|e mails|e commerce|ecommerce|
e business|e learning|e books|ebook|ebooks|
blog|blogs|blogger|bloggers|blogging|podcast|podcasts|
social media|social networking|streaming|download|downloads|
downloading|downloaded|upload|uploads|bandwidth|
codec|mpeg|mp3|dvd|cd rom|cdrom|drm|
copy protection|digital rights|copyright|copyrights|
patent|patents|patented|intellectual property|
browser|browsers|programmer|programmers|programming|
application software|software application|app|apps|
vulnerability|vulnerabilities|security flaw|security flaws|
security hole|security holes|security patch|security patches|
bug fix|bug fixes|patching|patches|patch|
spam|spammers|spammer|spamming|worm|worms|trojan|trojans|
keystroke|keystrokes|password|passwords|
authentication|biometric|biometrics|fingerprint recognition|
encryption key|surveillance technology|facial recognition|
it security|information technology|it industry|tech industry|
tech stocks|technology stocks|tech companies|technology companies|
dot com|dotcom|startup|startups|start up|start ups|
silicon valley|silicon|chipset|chipsets|dual core|multi core|
gigahertz|megahertz|gigabyte|gigabytes|terabyte|terabytes|
megabyte|megabytes|gigabit|megabit|pixels|megapixel|megapixels|
lcd|oled|plasma display|touchscreen|touch screen|3d printing|
printer|printers|scanner|scanners|digital camera|digital cameras|
high definition|hdtv|flat panel|flat screen|set top box|
consumer electronics|gadget|gadgets|gizmo|gizmos|
bluetooth headset|virtual reality|augmented reality|
game developer|game developers|gameplay|gaming|gamer|gamers|
multiplayer|mmorpg|esports|e sports|
autonomous vehicle|self driving|driverless|electric vehicle|
electric vehicles|ev battery|lithium ion|solar panel|solar panels|
renewable energy|fuel cell|fuel cells|fusion energy|
scientific|science|laboratory|laboratories|lab|labs|
experiment|experiments|experimental|discovery|discoveries|
invention|inventions|inventor|inventors|breakthrough|
research|researches|researching|
medical|medicine|biomedical|diagnostic|diagnosis|
vaccine|vaccines|vaccination|vaccinations|
antibody|antibodies|antibiotic|antibiotics|
cancer|tumor|tumors|tumour|tumours|leukemia|leukaemia|
diabetes|diabetic|obesity|obese|cholesterol|
heart disease|heart attack|heart attacks|cardiovascular|
blood pressure|blood sugar|clinical|therapeutic|therapies|
treatment|treatments|therapy|patients|patient|
fertility|infertility|embryo|embryos|embryonic|
transplant|transplants|surgery|surgical|surgeons|surgeon|
protein|proteins|enzyme|enzymes|hormone|hormones|
gene|genes|genetic|molecular|molecule|molecules|
cell biology|cellular biology|immune system|immunity|
hiv|aids|sars|coronavirus|covid|covid 19|
neuron|neurons|brain cells|brain scan|brain scans|
psychology|psychologists|psychiatry|psychiatric|
antidepressant|antidepressants|prozac|
evolution|evolutionary|ecosystem|ecosystems|
biodiversity|species|extinction|habitat|habitats|
ecology|ecological|conservation|conservationists|
geology|geologist|geologists|geological|
seismic|seismologists|tectonic|tectonics|
climate scientists|climatologists|ozone|greenhouse|
carbon dioxide|carbon emissions|methane|
arctic ice|antarctic ice|ice sheet|ice sheets|glaciers|
planets|planet|planetary|orbit|orbital|orbiting|
rocket|rockets|spaceflight|space flight|spacewalk|
propulsion|space probe|space probes|probe mission|
titan|saturn|jupiter|neptune|uranus|pluto|venus|
mercury planet|milky way|light years|light year|
manned mission|unmanned mission|zero gravity|
laser|lasers|optical|optics|photon|photons|
atom|atoms|atomic|electron|electrons|proton|protons|
neutron|neutrons|particle|particles|antimatter|
nanoparticle|nanoparticles|superconductor|superconductors|
chemistry|chemical reaction|chemical reactions|
mathematician|mathematicians|mathematics|
radiocarbon|carbon dating|ancient remains|archaeological|
meteorology|meteorologist|meteorologists
""")
_add("sci_tech", 1.15, """
study|studies|studied|survey|surveys|evidence|findings|
health|healthy|healthier|doctors|doctor|disease|diseases|
infection|infections|infected|infectious|virus|viruses|
flu|influenza|avian|bacteria|bacterial|
hospital|hospitals|medical center|medical journal|
drug|drugs|medication|medications|pharmaceutical|
pharmaceuticals|pharmacy|pharmacies|biological|
brain|blood|tissue|tissues|organ|organs|
diet|diets|nutrition|nutritional|vitamin|vitamins|
sleep|sleeping|aging|ageing|longevity|
animals|animal|mice|mouse|monkey|monkeys|
birds|bird|whales|whale|dolphins|dolphin|
sharks|shark|fish|insects|insect|bees|bee|
environment|environmental|pollution|pollutants|carbon|
renewable|energy efficiency|recycling|
warming|glacier|glacial|polar|antarctica|antarctic|
solar|lunar surface|launch|launches|launched|mission|
discovered|discovery|excavation|excavations|artifact|artifacts|
innovation|innovative|innovations|engineering|engineers|
network|networks|platform|platforms|interface|interfaces|
display|displays|screen|screens|windows|
data|information systems|processing|simulation|simulations|
nobel|nobel prize|university study|journal nature|journal science|
nuclear reactor|nuclear reactors|nuclear fusion|
cryptocurrency|bitcoin|ethereum|blockchain|fda
""")

# Sports: competitions, terminology, teams, and prominent participants.
_add("sports", 6.2, """
football|soccer|baseball|basketball|hockey|cricket|rugby|tennis|golf|
volleyball|badminton|softball|handball|lacrosse|futsal|
nfl|nba|wnba|nhl|mlb|mls|ncaa|uefa|fifa|fiba|icc|pga|lpga|
olympics|olympic games|paralympics|super bowl|superbowl|
world cup|world series|champions league|premier league|
premiership|bundesliga|la liga|serie a|ligue 1|
fa cup|carling cup|league cup|uefa cup|europa league|
six nations|tri nations|ryder cup|davis cup|fed cup|
stanley cup|heineken cup|the ashes|test cricket|
us open|u s open|australian open|french open|british open|
wimbledon|roland garros|flushing meadows|
tour de france|giro d italia|vuelta a espana|
formula one|formula 1|f1|grand prix|nascar|indycar|
indianapolis 500|daytona 500|nextel cup|champ car|
kentucky derby|preakness|belmont stakes|breeders cup|
grand slam|world championship|world championships|
championship game|championship match|gold medal|gold medals|
silver medal|silver medals|bronze medal|bronze medals|
euro 2004|euro 2008|euro 2012|euro 2016|euro 2020|euro 2024|
college football|college basketball|major league|minor league
""")
_add("sports", 4.4, """
athlete|athletes|athletic|athletics|sports|sporting|
championship|championships|tournament|tournaments|
playoff|playoffs|postseason|post season|preseason|
semifinal|semifinals|semi final|semi finals|
quarterfinal|quarterfinals|quarter final|quarter finals|
finals|finalist|finalists|quarterback|quarterbacks|
touchdown|touchdowns|linebacker|linebackers|
running back|wide receiver|tight end|field goal|
pitcher|pitchers|pitching|inning|innings|batter|batters|
batting|batsman|batsmen|bowler|bowlers|bowling|
wicket|wickets|century partnership|leg spinner|off spinner|
home run|home runs|homerun|homeruns|homer|homers|
grandstand|ballpark|ballparks|ballgame|
goaltender|goaltenders|goalkeeper|goalkeepers|goalie|goalies|
midfielder|midfielders|striker|strikers|fullback|fullbacks|
hat trick|hat tricks|hattrick|hattricks|
penalty kick|penalty kicks|penalty shootout|penalty shoot out|
red card|red cards|yellow card|yellow cards|
free throw|free throws|three pointer|three pointers|
slam dunk|triple double|double double|
pole position|checkered flag|chequered flag|pit stop|pit stops|
racecar|racing driver|race driver|race track|racetrack|
jockey|jockeys|thoroughbred|thoroughbreds|
wrestling|wrestler|wrestlers|boxing|boxer|boxers|
heavyweight|welterweight|middleweight|featherweight|
gymnastics|gymnast|gymnasts|swimming|swimmer|swimmers|
diving|diver|divers|sprinting|sprinter|sprinters|
weightlifting|weightlifter|fencing|fencer|
skiing|skier|skiers|snowboarding|biathlon|bobsleigh|
speed skating|figure skating|ice skating|skating|
cycling|cyclist|cyclists|triathlon|triathlete|
marathon|marathoner|decathlon|heptathlon|pentathlon|
hurdles|hurdler|hurdlers|javelin|discus|pole vault|
shot put|long jump|high jump|triple jump|
equestrian|dressage|showjumping|show jumping|
sailing regatta|regatta|canoeing|kayaking|rowing|
surfing|surfer|surfers|skateboarding|
motorsport|motorsports|motocross|rally driver|
sportsman|sportsmen|sportswoman|sportswomen|
anti doping|doping|sportsmanship|sportswear|
batting average|earned run|run batted in|runs batted in|
batting order|test match|one day international|
atp|wta|dp world tour|european tour|pga tour|lpga tour
""")
_add("sports", 2.7, """
sport|champion|champions|defending champion|
coach|coaches|coaching|coached|managerial|
match|matches|matchup|matchups|fixture|fixtures|
scored|scorer|scorers|scoring|scoreless|goalless|
goal|goals|goalpost|goalposts|nets|
rebound|rebounds|rebounding|assist|assists|
overtime|halftime|half time|extra time|injury time|
equalizer|equaliser|equalized|equalised|
penalties|penalty|foul|fouls|referee|referees|umpire|umpires|
racket|racquet|backhand|forehand|tiebreak|tie break|
eagle putt|birdie|birdies|bogey|bogeys|putt|putts|
fairway|fairways|clubhouse lead|under par|over par|
knockout|knocked out|knockdowns|title bout|
ringside|undisputed champion|world title|
streak|streaks|winning streak|losing streak|
standings|league table|leaderboard|
roster|rosters|lineup|lineups|squad|squads|
seeded|unseeded|top seed|top seeded|
medal|medals|medalist|medallists|medalists|medallist|
podium|qualifier|qualifiers|qualifying|qualification round|
stadium|stadiums|stadia|arena|arenas|
season opener|season finale|home opener|
training camp|training camps|free agent|free agents|
trade deadline|transfer window|transfer fee|
rookie|rookies|veteran player|veteran players|
all star|all stars|most valuable player|mvp|
mound|dugout|bullpen|shortstop|outfielder|outfield|
catcher|catchers|baseman|designated hitter|
punt|punter|kickoff|kick off|kick return|
defender|defenders|defensive tackle|offensive line|
touchline|sideline|sidelines|end zone|
hurdle race|relay|relays|freestyle|backstroke|breaststroke|
butterfly stroke|100 meters|200 meters|100 metres|200 metres|
relegation|relegated|promotion playoff
""")
_add("sports", 1.25, """
game|games|player|players|played|playing|play|
team|teams|teammate|teammates|teammate's|
league|leagues|season|seasons|club|clubs|
win|wins|winning|winner|winners|won|victory|victories|
beat|beats|beaten|beating|defeat|defeats|defeated|
loss|losses|lost|losing|draw|draws|drew|tied|
score|scores|point|points|lead|leads|leading|
final|round|rounds|opener|opening round|second round|
third round|fourth round|first round|
cup|cups|captain|captains|captaincy|
fans|fan|supporters|crowd|crowds|cheered|
injury|injuries|injured|ankle|knee|hamstring|groin|
bench|benched|suspended|suspension|ban|banned|
practice|practices|practising|practicing|
pitch|pitching staff|runs|run|batted|bats|
serve|serving|ace|aces|court|courts|set|sets|
sweep|sweeps|swept|sweeping|
title|titles|record holder|world record|personal best|
bout|bouts|fight night|rematch|
race winner|race victory|racing|racer|racers|
sponsor|sponsors|sponsorship|espn
""")
_add("sports", 5.1, """
manchester united|manchester city|real madrid|barcelona|
fc barcelona|ac milan|inter milan|internazionale|
juventus|bayern munich|borussia dortmund|werder bremen|
bayer leverkusen|paris st germain|paris saint germain|
psg|atletico madrid|deportivo coruna|real sociedad|
celtic|glasgow rangers|glasgow celtic|
newcastle united|west ham|west bromwich|aston villa|
blackburn rovers|bolton wanderers|tottenham|hotspur|
everton|fulham|portsmouth|southampton fc|crystal palace|
ipswich|norwich city|leeds united|nottingham forest|
charlton athletic|wolverhampton|sunderland|middlesbrough|
porto|benfica|sporting lisbon|galatasaray|fenerbahce|
ajax|psv eindhoven|feyenoord|dynamo kiev|cska moscow|
boca juniors|river plate|corinthians|flamengo|
la galaxy|los angeles galaxy|inter miami|
new york yankees|yankees|boston red sox|red sox|white sox|
new york mets|mets|baltimore orioles|orioles|
toronto blue jays|blue jays|tampa bay rays|devil rays|
cleveland guardians|cleveland indians|detroit tigers|
minnesota twins|kansas city royals|oakland athletics|
los angeles angels|anaheim angels|seattle mariners|mariners|
texas rangers|atlanta braves|braves|philadelphia phillies|phillies|
florida marlins|miami marlins|marlins|montreal expos|expos|
washington nationals|chicago cubs|cubs|cincinnati reds|
st louis cardinals|pittsburgh pirates|milwaukee brewers|brewers|
houston astros|astros|arizona diamondbacks|diamondbacks|
colorado rockies|rockies|los angeles dodgers|dodgers|
san diego padres|padres|san francisco giants|
los angeles lakers|lakers|boston celtics|celtics|
chicago bulls|new york knicks|knicks|brooklyn nets|
new jersey nets|toronto raptors|raptors|
philadelphia 76ers|76ers|sixers|miami heat|
cleveland cavaliers|cavaliers|detroit pistons|pistons|
indiana pacers|pacers|milwaukee bucks|orlando magic|
washington wizards|charlotte hornets|charlotte bobcats|
atlanta hawks|dallas mavericks|mavericks|
houston rockets|san antonio spurs|spurs|
phoenix suns|suns|sacramento kings|golden state warriors|
los angeles clippers|clippers|portland trail blazers|
minnesota timberwolves|timberwolves|utah jazz|
memphis grizzlies|grizzlies|denver nuggets|nuggets|
oklahoma city thunder|seattle supersonics|supersonics|
new orleans pelicans|new orleans hornets|
new england patriots|patriots|new york jets|
new york giants|buffalo bills|miami dolphins|
pittsburgh steelers|steelers|baltimore ravens|ravens|
cincinnati bengals|bengals|cleveland browns|
indianapolis colts|colts|tennessee titans|
houston texans|texans|jacksonville jaguars|
kansas city chiefs|denver broncos|broncos|
oakland raiders|las vegas raiders|raiders|
san diego chargers|los angeles chargers|chargers|
dallas cowboys|cowboys|philadelphia eagles|
washington redskins|redskins|washington commanders|
green bay packers|packers|minnesota vikings|vikings|
chicago bears|detroit lions|atlanta falcons|
carolina panthers|new orleans saints|tampa bay buccaneers|
buccaneers|arizona cardinals|st louis rams|los angeles rams|
san francisco 49ers|49ers|seattle seahawks|seahawks|
detroit red wings|red wings|toronto maple leafs|maple leafs|
montreal canadiens|canadiens|ottawa senators|
boston bruins|bruins|buffalo sabres|sabres|
new york rangers|new york islanders|islanders|
new jersey devils|philadelphia flyers|flyers|
pittsburgh penguins|tampa bay lightning|
carolina hurricanes|florida panthers|washington capitals|
columbus blue jackets|blue jackets|chicago blackhawks|blackhawks|
nashville predators|st louis blues|minnesota wild|
colorado avalanche|dallas stars|edmonton oilers|oilers|
calgary flames|vancouver canucks|canucks|
san jose sharks|anaheim ducks|mighty ducks|phoenix coyotes|
los angeles kings|atlanta thrashers|
all blacks|wallabies|springboks|british lions|
leicester tigers|northampton saints|london wasps|
melbourne storm|brisbane broncos|sydney roosters|
wigan warriors|st helens|leeds rhinos|
ohio state|penn state|notre dame|virginia tech|
ucla|usc trojans|tar heels|blue devils|fighting irish|
wolverines|buckeyes|sooners|cornhuskers|seminoles|
boilermakers|huskies|hoosiers|jayhawks|razorbacks
""")
_add("sports", 3.0, """
arsenal|chelsea|liverpool|rangers|cardinals|eagles|giants|
panthers|falcons|dolphins|jaguars|tigers|pirates|
warriors|bulldogs|wildcats|longhorns|aggies|
ferrari|mclaren|renault f1|williams f1|bar honda|
indy racing|a1 grand prix|red bull racing|
eastern conference|western conference|american league|national league
""")
_add("sports", 5.0, """
tiger woods|phil mickelson|ernie els|vijay singh|
retief goosen|sergio garcia|rory mcilroy|jack nicklaus|
arnold palmer|annika sorenstam|michelle wie|lorena ochoa|
roger federer|rafael nadal|novak djokovic|andy roddick|
andre agassi|pete sampras|lleyton hewitt|tim henman|
marat safin|juan carlos ferrero|david nalbandian|
carlos moya|gaston gaudio|andy murray|
serena williams|venus williams|maria sharapova|
lindsay davenport|amelie mauresmo|justine henin|
kim clijsters|jennifer capriati|elena dementieva|
anastasia myskina|svetlana kuznetsova|martina hingis|
michael jordan|lebron james|kobe bryant|shaquille o'neal|
shaquille oneal|shaquille|shaquille o neal|yao ming|
tim duncan|kevin garnett|allen iverson|tracy mcgrady|
vince carter|carmelo anthony|steve nash|dirk nowitzki|
dwyane wade|stephen curry|kevin durant|
barry bonds|alex rodriguez|derek jeter|babe ruth|
sammy sosa|mark mcgwire|roger clemens|randy johnson|
pedro martinez|curt schilling|david ortiz|manny ramirez|
ichiro|hideki matsui|carlos beltran|albert pujols|
tom brady|peyton manning|eli manning|brett favre|
michael vick|donovan mcnabb|terrell owens|randy moss|
ray lewis|jerry rice|joe montana|ben roethlisberger|
wayne rooney|david beckham|michael owen|steven gerrard|
frank lampard|john terry|rio ferdinand|paul scholes|
ryan giggs|roy keane|thierry henry|patrick vieira|
dennis bergkamp|zinedine zidane|ronaldo|ronaldinho|
cristiano ronaldo|lionel messi|luis figo|raul gonzalez|
roberto carlos|david trezeguet|andriy shevchenko|
ruud van nistelrooy|robin van persie|arjen robben|
didier drogba|samuel eto'o|simon kjaer|
jose mourinho|alex ferguson|arsene wenger|rafael benitez|
sven goran eriksson|sven goran|marcello lippi|
sachin tendulkar|brian lara|ricky ponting|steve waugh|
sourav ganguly|rahul dravid|virender sehwag|anil kumble|
vvs laxman|yuvraj singh|mahendra singh dhoni|ms dhoni|
virat kohli|rohit sharma|shane warne|glenn mcgrath|
adam gilchrist|matthew hayden|justin langer|brett lee|
andrew flintoff|michael vaughan|marcus trescothick|
kevin pietersen|andrew strauss|james anderson|
muttiah muralitharan|sanath jayasuriya|kumara sangakkara|
kumar sangakkara|mahela jayawardene|shoaib akhtar|
inzamam ul haq|wasim akram|waqar younis|shahid afridi|
jacques kallis|graeme smith|shaun pollock|
michael schumacher|ralf schumacher|rubens barrichello|
fernando alonso|kimi raikkonen|juan pablo montoya|
jenson button|david coulthard|lewis hamilton|max verstappen|
dale earnhardt|dale earnhardt jr|jeff gordon|jimmie johnson|
tony stewart|kurt busch|kyle busch|matt kenseth|
lance armstrong|jan ullrich|ivan basso|tyler hamilton|
michael phelps|ian thorpe|natalie coughlin|amanda beard|
usain bolt|justin gatlin|maurice greene|asafa powell|
hicham el guerrouj|kenenisa bekele|haile gebrselassie|
paula radcliffe|kelly holmes|liu xiang|carl lewis|
marion jones|tim montgomery|yuriy borzakovskiy|
paul hamm|carly patterson|svetlana khorkina|simone biles|
mike tyson|lennox lewis|evander holyfield|
vitali klitschko|wladimir klitschko|bernard hopkins|
oscar de la hoya|floyd mayweather|manny pacquiao|
roy jones jr|antonio tarver|
wayne gretzky|mario lemieux|sidney crosby|alex ovechkin|
jaromir jagr|martin brodeur|patrick roy|brett hull|
joe sakic|steve yzerman|jeremy roenick|
jonny wilkinson|brian o'driscoll|dan carter|johnny wilkinson|
michael cheika|clive woodward|eddie jones|
reggie bush|drew brees|aaron rodgers|patrick mahomes|
bill belichick|bill parcells|tony dungy|andy reid|
joe torre|terry francona|tony la russa|bobby cox|
phil jackson|gregg popovich|larry brown|pat riley
""")

# World affairs, politics, public safety, crime, and disasters.
_add("world", 6.0, """
united nations|white house|security council|un security council|
prime minister|foreign minister|foreign ministry|defense minister|
defence minister|interior minister|secretary of state|
presidential election|presidential elections|general election|
general elections|election campaign|electoral college|
suicide bomber|suicide bombers|suicide bombing|suicide bombings|
car bomb|car bombs|roadside bomb|roadside bombs|
nuclear weapons|nuclear weapon|weapons of mass destruction|
middle east peace|peace talks|peace process|cease fire|
human rights|war crimes|war crime|ethnic cleansing|
supreme court|supreme court justice|constitutional court|
state of emergency|martial law|military coup|
al qaeda|al qaida|al queda|islamic state|isis|isil|
taliban|hamas|hezbollah|hezbollah's|islamic jihad|
nobel peace prize|nobel peace|roman catholic church
""")
_add("world", 4.3, """
war|warfare|terrorism|terrorist|terrorists|terror|
insurgent|insurgents|insurgency|militant|militants|militancy|
rebel|rebels|rebellion|revolt|uprising|
bombing|bombings|bomber|bombers|bomb|bombs|bombed|
airstrike|airstrikes|air strike|air strikes|
ceasefire|ceasefires|hostage|hostages|kidnap|kidnapped|kidnapping|
abducted|abduction|abductors|ransom|
assassination|assassinated|massacre|massacred|slaughter|
genocide|atrocities|civil war|civilian casualties|
earthquake|earthquakes|quake|quakes|tsunami|tsunamis|
hurricane|hurricanes|typhoon|typhoons|tornado|tornadoes|
floods|flooding|flooded|flash floods|landslide|landslides|
mudslide|mudslides|wildfire|wildfires|forest fires|
avalanche|avalanches|volcanic eruption|
disaster|disasters|catastrophe|catastrophic|
election|elections|electoral|elected|reelection|re election|
parliament|parliamentary|congressional|congressman|congresswoman|
senator|senators|senate|democrat|democrats|republican|republicans|
democratic party|republican party|labour party|labor party|
conservative party|liberal party|communist party|
ballot|ballots|voter|voters|voting|polling station|
referendum|referendums|referenda|inauguration|inaugurated|
constitution|constitutional|monarchy|monarch|
diplomacy|diplomatic|ambassador|ambassadors|embassy|embassies|
peacekeeping|peacekeepers|peacekeeper|peacekeeping force|
nato|unhcr|unicef|amnesty international|red cross|
pentagon|guantanamo|abu ghraib|fallujah|falluja|
gaza|gaza strip|west bank|ramallah|rafah|
murder|murdered|murderer|manslaughter|homicide|
rape|raped|rapist|rapists|serial killer|
execution|executions|executed|death penalty|death sentence|
prison|prisons|jail|jailed|jails|prisoner|prisoners|
riot|riots|rioting|riot police|looting|
clashes|clashed|clash|gunfire|gunbattle|gunfight|
shooting|shootings|gunman|gunmen|gunshot|gunshots|
church|churches|mosque|mosques|synagogue|synagogues|
vatican|pope|papal|pontiff|archbishop|bishop|
refugee|refugees|asylum|asylum seekers|deportation|
immigration|immigrant|immigrants|migrant|migrants
""")
_add("world", 2.7, """
politics|political|politician|politicians|government|governments|
governing|governor|governors|governance|
minister|ministers|ministry|ministries|cabinet|
chancellor|premier|premiers|presidency|
opposition|coalition|administration|lawmakers|lawmaker|
legislation|legislative|legislature|congress|congresses|
campaigning|campaigner|campaigners|campaign|
democracy|democratic|dictator|dictatorship|regime|
nationalist|nationalists|separatist|separatists|
communist|communists|socialist|socialists|marxist|
protest|protests|protester|protesters|protesting|demonstrators|
demonstration|demonstrations|activist|activists|
sanctions|sanction|treaty|treaties|bilateral|multilateral|
diplomat|diplomats|diplomatically|negotiations|
summit|summits|geopolitical|international affairs|
military|army|navy|marines|air force|troop|troops|
soldier|soldiers|battalion|battalions|combat|battle|battles|
fighting|fought|offensive|invasion|invaded|invading|
occupation|occupied|occupying|withdrawal|withdraw|
weapons|weapon|missile|missiles|warhead|warheads|
artillery|shelling|shelled|mortar|mortars|munitions|
armed|gun|guns|rifle|rifles|firearm|firearms|
attack|attacks|attacked|attacking|
explosion|explosions|exploded|explosive|explosives|blast|blasts|
killed|killing|killings|kill|kills|dead|deaths|fatalities|
wounded|wounding|casualty|casualties|
rescue|rescued|rescuers|rescuing|evacuated|evacuation|
survivor|survivors|trapped|missing persons|death toll|
storm|storms|stormy|drought|droughts|famine|famines|
torrential|torrential rains|monsoon|monsoons|
emergency|emergencies|relief workers|aid workers|
plane crash|plane crashes|air crash|jet crash|
helicopter crash|train crash|train derailment|derailment|
shipwreck|shipwrecked|capsized|ferry disaster|
firefighters|firefighter|blaze|blazes|
police|policeman|policemen|policewoman|policing|
detective|detectives|criminal|criminals|crime|crimes|
arrest|arrests|arrested|detained|detention|detainee|detainees|
suspect|suspects|suspected|fugitive|fugitives|
robbery|robber|robbers|burglary|burglars|theft|stolen|
smuggling|smuggler|smugglers|trafficking|traffickers|
prosecutor|prosecutors|prosecution|indictment|indicted|
convicted|conviction|convictions|sentenced|sentencing|
guilty|acquitted|acquittal|testified|testimony|
cocaine|heroin|cartel|cartels|gang|gangs|gangster|
apartheid|racism|racist|discrimination|
religion|religious|cleric|clerics|clergy|pilgrims|pilgrimage|
catholic|catholics|christian|christians|islam|islamic|
muslim|muslims|jewish|judaism|hindu|hinduism|buddhist|
sectarian|sunni|shiite|shia|sikh|sikhs|
humanitarian|unrest|turmoil|bloodshed|
epidemic|epidemics|outbreak|outbreaks|pandemic|
disease outbreak|cholera|ebola|
border|borders|checkpoint|checkpoints|territorial|
sovereignty|sovereign|annexation|annexed|independence
""")
_add("world", 1.15, """
president|presidential|official|officials|authorities|authority|
leader|leaders|leadership|ruler|rulers|
state department|interior ministry|justice department|
law|laws|legal|justice|judge|judges|judicial|
court|courts|trial|trials|hearing|hearings|
charged|charges|charge|alleged|allegedly|accused|
investigation|investigations|investigating|investigators|
inquiry|inquiries|scandal|scandals|corruption|bribery|
witness|witnesses|evidence|custody|bail|appeal|appeals|
citizen|citizens|citizenship|residents|resident|
national|nationally|nation|nations|
public policy|public safety|civil|civic|civilian|civilians|
security|defense|defence|intelligence|spying|espionage|
nuclear|uranium|plutonium|enrichment|
peace|peaceful|peacefully|conflict|conflicts|
tensions|tension|dispute|disputed|disputes|
threat|threats|threatened|warning|warned|
emergency services|ambulance|ambulances|fire|fires|
accident|accidents|crash|crashed|crashes|
injured|injuries|injuring|injury|wounds|
funeral|funerals|burial|mourning|memorial|
death|victim|victims|died|dying|
safety|shelter|shelters|homeless|homelessness|
school|schools|students|student|teachers|teacher|
education|educational|tuition|schoolchildren|
embattled|controversial|controversy|
un|eu|european union|african union|arab league|
commonwealth|g8|g7|g20|
ballistic|ammunition|patrol|patrols|
naval|aircraft carrier|destroyer|submarine|
iraq|iraqi|iraqis|afghanistan|afghan|afghans|
israel|israeli|israelis|palestine|palestinian|palestinians|
iran|iranian|iranians|syria|syrian|syrians|
ukraine|ukrainian|ukrainians|north korea|north korean|
south sudan|darfur|chechnya|chechen|kashmir|
baghdad|kabul|jerusalem|beirut|damascus|tehran|
donetsk|luhansk|kyiv|kiev|crimea|srebrenica|grozny
""")
_add("world", 4.7, """
george bush|george w bush|president bush|bush administration|
john kerry|john edwards|dick cheney|condoleezza rice|colin powell|
tony blair|gordon brown|david cameron|theresa may|
boris johnson|rishi sunak|keir starmer|
vladimir putin|dmitry medvedev|volodymyr zelensky|
volodymyr zelenskyy|zelensky|zelenskyy|
ariel sharon|yasser arafat|mahmoud abbas|benjamin netanyahu|
ehud olmert|ehud barak|yitzhak rabin|shimon peres|
saddam hussein|saddam|osama bin laden|bin laden|
abu musab al zarqawi|zarqawi|ayman al zawahiri|
pervez musharraf|hamid karzai|karzai|
jacques chirac|gerhard schroeder|angela merkel|
olaf scholz|emmanuel macron|nicolas sarkozy|
silvio berlusconi|romano prodi|jose manuel barroso|
jose luis rodriguez zapatero|jose maria aznar|
kofi annan|ban ki moon|antonio guterres|
junichiro koizumi|koizumi|shinzo abe|
hu jintao|jiang zemin|wen jiabao|xi jinping|
kim jong il|kim jong un|kim il sung|roh moo hyun|
manmohan singh|sonia gandhi|atal bihari vajpayee|
narendra modi|rahul gandhi|pervez elahi|
robert mugabe|mugabe|nelson mandela|thabo mbeki|
jacob zuma|cyril ramaphosa|jacob zuma|
paul kagame|yoweri museveni|omar al bashir|
mwai kibaki|raila odinga|ellen johnson sirleaf|
mohammad khatami|mahmoud ahmadinejad|ali khamenei|
ayatollah|muammar gaddafi|gaddafi|bashar assad|bashar al assad|
hafez assad|assad|hassan nasrallah|
hugo chavez|nicolas maduro|fidel castro|raul castro|
lula da silva|jair bolsonaro|luiz inacio lula|
alvaro uribe|vicente fox|lopez obrador|
viktor yushchenko|viktor yanukovych|yanukovich|yushchenko|
alexander lukashenko|lukashenko|mikheil saakashvili|
slobodan milosevic|radovan karadzic|ratko mladic|
susilo bambang yudhoyono|megawati|suharto|
gloria arroyo|thaksin shinawatra|aung san suu kyi|
barack obama|joe biden|donald trump|kamala harris|
hillary clinton|bill clinton|bernie sanders|nancy pelosi|
john mccain|mitt romney|ron desantis|
pope john paul|john paul ii|pope benedict|pope francis|
dalai lama|desmond tutu|mother teresa|
queen elizabeth|king charles|prince william|prince harry|
king abdullah|king fahd|crown prince|mohammed bin salman
""")
_add("world", 3.1, """
bush|kerry|cheney|blair|putin|arafat|sharon|netanyahu|
musharraf|chirac|schroeder|berlusconi|annan|
obama|biden|trump|clinton|zelenskiy|macron|merkel|
republicans'|democrats'|downing street|kremlin|
oval office|capitol hill|capitol|buckingham palace|
belfast|northern ireland|basque|eta separatists|
farc|sinn fein|ira militants|ira rebels|ltte|tamil tigers|
boko haram|al shabaab|houthi|houthis|hizbollah|
guerrilla|guerrillas|paramilitary|militia|militias|
fbi|cia|mi5|mi6|interpol|scotland yard|
reuters world|associated press world|world news
""")

_GEO = _phrase_set("""
united states|united kingdom|britain|british|england|scotland|wales|
ireland|irish|france|french|germany|german|germans|
italy|italian|spain|spanish|portugal|portuguese|
russia|russian|russians|china|chinese|japan|japanese|
india|indian|indians|pakistan|pakistani|bangladesh|
sri lanka|sri lankan|nepal|nepalese|bhutan|
australia|australian|new zealand|new zealanders|
canada|canadian|mexico|mexican|brazil|brazilian|
argentina|argentine|chile|chilean|peru|peruvian|
colombia|colombian|venezuela|venezuelan|ecuador|bolivia|
uruguay|paraguay|cuba|cuban|haiti|haitian|
dominican republic|jamaica|costa rica|guatemala|honduras|
nicaragua|el salvador|panama|puerto rico|
egypt|egyptian|libya|libyan|tunisia|algeria|morocco|
sudan|sudanese|somalia|somali|ethiopia|ethiopian|
eritrea|kenya|kenyan|tanzania|uganda|rwanda|congo|
democratic republic of congo|nigeria|nigerian|niger|
senegal|ivory coast|ghana|cameroon|zimbabwe|zambian|
zambia|mozambique|angola|botswana|namibia|south africa|
south african|liberia|liberian|sierra leone|guinea|
burundi|madagascar|malawi|mali|chad|gabon|
saudi arabia|saudi|yemen|yemeni|oman|bahrain|
qatar|kuwait|kuwaiti|united arab emirates|uae|
jordan|jordanian|lebanon|lebanese|turkey|turkish|
greece|greek|cyprus|cypriot|malta|
netherlands|dutch|belgium|belgian|luxembourg|
switzerland|swiss|austria|austrian|poland|polish|
czech republic|czech|slovakia|slovak|hungary|hungarian|
romania|romanian|bulgaria|bulgarian|albania|albanian|
serbia|serbian|montenegro|bosnia|bosnian|croatia|croatian|
slovenia|slovenian|macedonia|kosovo|kosovar|
belarus|belarusian|moldova|moldovan|georgia|georgian|
armenia|armenian|azerbaijan|azerbaijani|
estonia|estonian|latvia|latvian|lithuania|lithuanian|
sweden|swedish|norway|norwegian|denmark|danish|
finland|finnish|iceland|icelandic|
indonesia|indonesian|malaysia|malaysian|singapore|
thailand|thai|vietnam|vietnamese|cambodia|cambodian|
laos|laotian|myanmar|burma|burmese|philippines|filipino|
taiwan|taiwanese|hong kong|macao|macau|
south korea|south korean|mongolia|mongolian|
uzbekistan|uzbek|kazakhstan|kazakh|tajikistan|
kyrgyzstan|turkmenistan|tibet|tibetan|
east timor|timor leste|papua new guinea|fiji|solomon islands|
europe|european|asia|asian|africa|african|
latin america|middle east|balkans|
london|paris|berlin|rome|madrid|lisbon|brussels|
moscow|beijing|tokyo|seoul|taipei|bangkok|jakarta|
manila|hanoi|new delhi|islamabad|dhaka|colombo|
ottawa|mexico city|buenos aires|caracas|havana|
cairo|riyadh|jeddah|doha|dubai|amman|ankara|
istanbul|athens|nairobi|johannesburg|pretoria|
harare|lagos|abuja|khartoum|mogadishu|
washington|new york|los angeles|chicago|san francisco|
boston|sydney|melbourne|toronto|montreal
""")

# Explicit contextual features keep ambiguous common words from dominating.
_add("world", 6.0, """
arab league|national league for democracy|league of arab states|
presidential race|presidential contest|election race|senate race|
electoral victory|election victory|election results|
bank robbery|armed robbery|drug trafficking|drug cartel|
military intelligence|military operation|military operations|
terror attack|terror attacks|terrorist attack|terrorist attacks|
bomb attack|bomb attacks|rocket attack|rocket attacks|
missile attack|missile attacks|missile strike|missile strikes|
hurricane ivan|hurricane frances|hurricane charley|hurricane jeanne|
hurricane katrina|hurricane rita|typhoon tokage|
tropical storm|tropical depression|disaster relief|
bird flu outbreak|avian flu outbreak|flu outbreak|
nuclear program|nuclear programme|uranium enrichment|
atomic weapons|nuclear arms|arms control|arms talks|
peace treaty|peace deal|border crossing|border crossings
""")
_add("sci_tech", 5.5, """
computer security|network security|software security|
internet worm|internet virus|email virus|email worm|
e mail virus|e mail worm|banking trojan|computer hackers|
software giant|software maker|software makers|software firm|
software company|software companies|technology giant|tech giant|
technology giants|tech giants|computer maker|computer makers|
pc maker|pc makers|pc sales|pc market|computer sales|
mobile operator|mobile operators|mobile network|
phone maker|phone makers|handset maker|handset makers|
telecom operator|telecom operators|telecommunications company|
chip maker|chip makers|chip manufacturer|chip manufacturers|
internet company|internet companies|internet firm|
web search|internet search|search technology|
gaming console|gaming consoles|online gaming|online games|
online game|online music|digital music|music downloads|
digital video|digital television|satellite television|
broadband service|broadband services|wireless service|
third generation mobile|3g|4g|5g|6g|
3d printer|3d printers|quantum mechanics|quantum physics|
stem cell research|embryonic stem|climate research|
medical study|new study|new research|scientific study|
drug trial|drug trials|drug discovery|vaccine trial|vaccine trials|
flu vaccine|bird flu vaccine|aids vaccine|hiv vaccine|
research team|research teams|research project|research projects|
space agency|european space agency|space tourism|commercial space|
mars exploration|red planet|saturn moon|saturn's moon|
earth orbit|low earth orbit|solar powered|hydrogen powered|
computer model|computer models|computer simulation|
nuclear power plant|nuclear power plants|nuclear energy|
electric car|electric cars|hybrid car|hybrid cars|
renewable power|solar power|wind power
""")
_add("business", 5.2, """
oil company|oil companies|oil giant|oil giants|
energy company|energy companies|energy stocks|
automobile industry|auto industry|car industry|
airline industry|retail industry|banking industry|
pharmaceutical company|pharmaceutical companies|
drug company|drug companies|drugmaker|drugmakers|
real estate market|commercial property|property market|
home prices|house prices|housing prices|housing starts|
existing home sales|new home sales|consumer price index|
producer price index|purchasing managers index|
nonfarm payrolls|non farm payrolls|job growth|
business spending|business investment|corporate spending|
oil supply|oil output|oil production|crude futures|
oil futures|gold futures|gold prices|gold price|
oil price|gas prices|gasoline prices|fuel prices|
stock futures|stock index|stock indexes|stock indices|
market capitalization|market capitalisation|
federal funds|discount rate|benchmark rate|
cuts rates|cut rates|raises rates|rate hike|rate hikes|
interest rate|monetary policy|fiscal policy|
quarterly results|quarterly sales|quarterly revenue|
net income|net profit|net loss|operating profit|operating income|
earnings per share|profit margin|profit margins|
earnings report|earnings reports|sales forecast|
sales growth|revenue growth|earnings growth|
takeover bid|merger talks|merger deal|acquisition deal|
insider trading|accounting scandal|accounting fraud|
securities and exchange commission|
federal trade commission|department of commerce|
department of labor|labour market|labor market|
pension fund|pension funds|pension plan|pension plans|
health insurance|health insurer|health insurers
""")

_TECH_SECTORS = _phrase_set("""
software|hardware|internet|semiconductor|semiconductors|
chipmaker|chipmakers|chip maker|chip makers|microprocessor|
telecommunications|telecom|telecoms|broadband|wireless|
computer maker|computer makers|pc maker|pc makers|
mobile phone|mobile phones|cell phone|cell phones|
handset|handsets|smartphone|smartphones|
information technology|technology company|technology companies|
software maker|software makers|software company|software companies|
phone maker|phone makers|internet company|internet companies|
computer|computers|laptop|laptops|electronics|
video game|video games|gaming console|game console|
artificial intelligence|cloud computing
""")

_MARKET_WRAPS = _phrase_set("""
wall street|stock market|stock markets|stocks|stock futures|
dow jones|dow industrials|nasdaq composite|s&p 500|s&p500|
ftse|nikkei|stocks rise|stocks fall|stocks fell|stocks rose|
stocks gain|stocks gained|stocks drop|stocks dropped|
stocks rally|stocks rallied|stocks higher|stocks lower|
markets rise|markets fall|market wrap|market roundup|
asian stocks|european stocks|us stocks|u.s. stocks|
tokyo stocks|london stocks|new york stocks|tech stocks|
technology stocks|blue chips|blue chip stocks
""")

_FINANCIAL_ACTIONS = _phrase_set("""
earnings|profit|profits|sales|revenue|revenues|shares|shareholders|
quarterly|quarter|merger|mergers|acquisition|acquisitions|
takeover|buyout|deal|deals|bid|bids|jobs|job cuts|layoffs|
antitrust|lawsuit|lawsuits|litigation|patent|patents|
settlement|settlements|fine|fined|ceo|chief executive|
investors|investment|forecast|forecasts|outlook|bankruptcy|
restructuring|accounting|ipo|dividend|dividends|market share
""")

_VIOLENT_NEWS = _phrase_set("""
murder|murdered|killed|killing|dead|shot dead|shooting|gunman|
kidnapped|abducted|hostage|suicide bombing|bombing|
earthquake|tsunami|hurricane|tornado|typhoon|floods|
plane crash|train crash|car crash|fatal crash|
arrested for murder|war|invasion|terrorist attack
""")

_SCIENCE_RESULTS = _phrase_set("""
scientist|scientists|researcher|researchers|research|
study|studies|medical study|clinical trial|clinical trials|
experiment|experiments|laboratory|laboratories|dna|
genetic|genome|vaccine|vaccines|drug trial|drug trials|
cancer treatment|stem cells|stem cell|fossils|discovery
""")

_SPORT_FINANCE = _phrase_set("""
transfer|transfers|transfer fee|transfer window|contract|
contracts|deal|deals|signed|signing|signings|sponsor|
sponsors|sponsorship|owner|owners|ownership|buyout|
takeover|salary|salaries|wages|trade|traded|trades
""")

_LENGTHS = tuple(sorted(_LENGTHS))


def _extract_text(state):
    if isinstance(state, str):
        return state
    if isinstance(state, dict):
        parts = []
        for key in (
            "title", "headline", "description", "summary",
            "text", "content", "body", "article", "news", "sentence",
        ):
            if key in state:
                value = state[key]
                if isinstance(value, str):
                    if value and value not in parts:
                        parts.append(value)
                elif isinstance(value, (dict, list, tuple)):
                    extracted = _extract_text(value)
                    if extracted and extracted not in parts:
                        parts.append(extracted)
        if parts:
            return "\n".join(parts)
        for value in state.values():
            if isinstance(value, (str, dict, list, tuple)):
                extracted = _extract_text(value)
                if extracted:
                    parts.append(extracted)
        return "\n".join(parts)
    if isinstance(state, (list, tuple)):
        return "\n".join(_extract_text(x) for x in state)
    return ""


def _position_weight(position):
    if position < 12:
        return 1.45
    if position < 28:
        return 1.20
    return 1.0


def _first_of(found, phrases, default=1000000):
    return min((found[k][0] for k in phrases if k in found), default=default)


def predict(state):
    text = _extract_text(state)
    tokens = _tokens(text)
    if not tokens:
        return {"answer": "world"}

    token_set = set(tokens)
    found = {}
    size = len(tokens)

    fruit_apple = bool(
        token_set.intersection({
            "orchard", "orchards", "growers", "cider", "apples",
            "fruit", "harvest",
        })
    ) and not token_set.intersection({
        "iphone", "ipod", "ipad", "macintosh", "macbook", "itunes",
        "imac", "ios", "software", "computer",
    })
    forest_amazon = bool(token_set.intersection({
        "rainforest", "rainforests", "deforestation", "jungle",
        "indigenous", "biodiversity",
    })) and not token_set.intersection({
        "retailer", "shopping", "ecommerce", "aws", "bezos", "kindle",
    })
    broken_windows = bool(token_set.intersection({
        "shattered", "smashed", "panes", "windshield",
    })) and not token_set.intersection({
        "microsoft", "software", "computer", "xp", "vista",
    })

    for i in range(size):
        for length in _LENGTHS:
            if i + length > size:
                break
            key = tuple(tokens[i:i + length])
            if key not in _LEXICON:
                continue
            if key == ("apple",) and fruit_apple:
                continue
            if key == ("amazon",) and forest_amazon:
                continue
            if key == ("windows",) and broken_windows:
                continue
            if key in found:
                found[key][1] += 1
            else:
                found[key] = [i, 1]

    scores = {
        "business": 0.35,
        "sci_tech": 0.0,
        "sports": 0.0,
        "world": 0.6,
    }
    strong_hits = {c: [] for c in _CATEGORIES}
    contributions = {}

    for key, (position, count) in found.items():
        multiplier = _position_weight(position)
        multiplier *= 1.0 + 0.10 * min(count - 1, 3)
        for category, weight in _LEXICON[key].items():
            contribution = multiplier * weight
            scores[category] += contribution
            contributions[(category, key)] = contribution
            if weight >= 4.0:
                strong_hits[category].append((position, weight, key))

    # Geography is supporting evidence, not a reason to call a business,
    # sporting, or scientific story "world".
    geo_count = 0
    for length in (1, 2, 3, 4, 5):
        if length > size:
            break
        seen_geo = set()
        for i in range(size - length + 1):
            key = tuple(tokens[i:i + length])
            if key in _GEO and key not in seen_geo:
                seen_geo.add(key)
                geo_count += 1
    scores["world"] += min(2.4, 0.3 * geo_count)

    # The fixed taxonomy puts technology-company earnings, transactions,
    # employment changes, and litigation in science/technology.
    entity_keys = [k for k in _TECH_ENTITIES if k in found]
    entity_first = min(
        (found[k][0] for k in entity_keys), default=1000000
    )
    sector_first = _first_of(found, _TECH_SECTORS)
    financial_keys = [k for k in _FINANCIAL_ACTIONS if k in found]
    finance_first = min(
        (found[k][0] for k in financial_keys), default=1000000
    )
    market_first = _first_of(found, _MARKET_WRAPS)
    violence_first = _first_of(found, _VIOLENT_NEWS)

    # A market roundup can mention a technology stock without becoming a
    # technology-company story.
    market_wrap = market_first < 15
    if market_wrap:
        wrap_phrases = (
            ("wall", "street"), ("stock", "market"),
            ("stock", "markets"), ("stock", "futures"),
            ("dow", "jones"), ("s", "p", "500"),
            ("nasdaq", "composite"), ("stocks",),
        )
        market_wrap = any(
            key in found and found[key][0] < 16
            for key in wrap_phrases
        )
        if not market_wrap:
            market_wrap = market_first < 8 and entity_first > market_first

    if entity_keys:
        entity_subject = entity_first < 22
        finance_is_focus = bool(financial_keys) and (
            finance_first < 35 or scores["business"] >= 8.0
        )
        violent_focus = (
            violence_first < 22
            and not finance_is_focus
            and scores["world"] > scores["sci_tech"] * 1.25
        )
        if finance_is_focus and not market_wrap and not violent_focus:
            original_business = scores["business"]
            if entity_subject:
                scores["sci_tech"] += 0.88 * original_business + 3.0
                scores["business"] *= 0.52
            elif entity_first < 60:
                scores["sci_tech"] += 0.45 * original_business + 1.0
                scores["business"] *= 0.82
            else:
                scores["sci_tech"] += min(4.0, 0.18 * original_business)
        elif entity_subject and not violent_focus and not market_wrap:
            scores["sci_tech"] += 2.0
        elif market_wrap and scores["business"] > 12:
            scores["business"] += 4.0

    elif sector_first < 24 and financial_keys and not market_wrap:
        # Industry stories without a named firm, such as chipmaker profits.
        original_business = scores["business"]
        scores["sci_tech"] += 0.52 * original_business
        scores["business"] *= 0.77

    # Players, teams, and competition remain sporting subjects even when
    # money, contracts, sponsorship, or ownership are involved.
    sports_strong_early = [
        hit for hit in strong_hits["sports"] if hit[0] < 30
    ]
    sports_finance = any(k in found for k in _SPORT_FINANCE)
    if sports_strong_early and sports_finance:
        sports_base = scores["sports"]
        if sports_base >= 9.0:
            scores["sports"] += min(13.0, scores["business"] * 0.48)
            scores["business"] *= 0.75

    # Distinguish video-game launches from sports news about actual games.
    video_terms = _phrase_set("""
        video game|video games|videogame|videogames|computer game|
        computer games|game console|games console|gaming console|
        playstation|xbox|nintendo|electronic arts|activision|
        gamecube|game boy|gameboy|nintendo ds|nintendo switch|
        grand theft auto|world of warcraft|halo 2|half life 2
    """)
    video_first = _first_of(found, video_terms)
    if video_first < 35:
        scores["sci_tech"] += 5.0
        for word in ("game", "games", "player", "players", "playing", "play"):
            key = (word,)
            scores["sports"] -= 0.7 * contributions.get(
                ("sports", key), 0.0
            )

    # Conventional phrases that contain otherwise misleading sports words.
    if ("arab", "league") in found:
        scores["sports"] -= contributions.get(
            ("sports", ("league",)), 0.0
        )
    if ("national", "league", "for", "democracy") in found:
        scores["sports"] -= contributions.get(
            ("sports", ("league",)), 0.0
        )
        scores["sports"] -= contributions.get(
            ("sports", ("national", "league")), 0.0
        )
    if (
        ("tech", "giants") in found
        or ("technology", "giants") in found
        or ("software", "giant") in found
    ):
        scores["sports"] -= contributions.get(
            ("sports", ("giants",)), 0.0
        )

    # Outbreak/death reporting is public-affairs news; research into the
    # pathogen, a vaccine, or a treatment belongs to science.
    outbreak_keys = _phrase_set("""
        outbreak|outbreaks|epidemic|epidemics|pandemic|
        bird flu outbreak|avian flu outbreak|flu outbreak
    """)
    outbreak_first = _first_of(found, outbreak_keys)
    science_results = [k for k in _SCIENCE_RESULTS if k in found]
    hard_research = any(
        k in found for k in _phrase_set("""
            clinical trial|clinical trials|vaccine|vaccines|
            drug trial|drug trials|scientist|scientists|
            researcher|researchers|laboratory|laboratories|
            dna|genome|stem cell|stem cells|medical study
        """)
    )
    if outbreak_first < 45 and not hard_research:
        death_words = token_set.intersection({
            "killed", "kills", "dead", "deaths", "died", "toll",
            "officials", "authorities", "quarantine", "quarantined",
        })
        if death_words:
            scores["world"] += 4.0 + min(4.0, 1.2 * len(death_words))
    if hard_research and len(science_results) >= 3:
        scores["sci_tech"] += 3.0

    # Cybercrime is a technology topic, rather than ordinary crime.
    cyber_keys = _phrase_set("""
        malware|ransomware|spyware|phishing|hacker|hackers|
        hacking|cybersecurity|cyber security|cyberattack|cyberattacks|
        cyber attack|cyber attacks|computer virus|computer worm|
        internet worm|email virus|e mail virus|data breach|data breaches
    """)
    if _first_of(found, cyber_keys) < 35:
        scores["sci_tech"] += 4.5
        if scores["world"] > 8:
            scores["sci_tech"] += min(7.0, 0.23 * scores["world"])

    # Specific disaster reports override incidental airline or energy-company
    # mentions, but not market stories discussing their financial impact.
    disaster_terms = _phrase_set("""
        earthquake|earthquakes|quake|quakes|tsunami|tsunamis|
        hurricane|hurricanes|typhoon|typhoons|tornado|tornadoes|
        plane crash|train crash|helicopter crash|air crash|
        landslide|landslides|mudslide|mudslides|wildfire|wildfires|
        flooding|floods|ferry disaster|shipwreck|capsized
    """)
    disaster_first = _first_of(found, disaster_terms)
    if disaster_first < 18:
        public_impact = token_set.intersection({
            "killed", "dead", "deaths", "died", "missing", "evacuated",
            "rescued", "rescue", "survivors", "homeless", "casualties",
        })
        if public_impact and not hard_research:
            scores["world"] += min(8.0, 2.5 + 1.4 * len(public_impact))

    # Sparse texts still benefit from their clearest subject anchor.
    for category in _CATEGORIES:
        early = [x for x in strong_hits[category] if x[0] < 12]
        if early and len(strong_hits[category]) >= 2:
            scores[category] += 1.5

    answer = max(_CATEGORIES, key=lambda category: scores[category])
    return {"answer": answer}
