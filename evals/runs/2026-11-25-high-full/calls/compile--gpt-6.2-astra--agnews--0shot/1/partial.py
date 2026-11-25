import re
import unicodedata
from collections import Counter

# The features are scored by subject, not by the dateline of the story.
_CATS = ("world", "business", "sci_tech", "sports")
_LEX = {c: {} for c in _CATS}
_MAXLEN = 1


def _norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("`", "'")
    s = s.replace("&amp;", " and ").replace("&#39;", "'").replace("&apos;", "'")
    s = re.sub(r"&(?:quot|lt|gt|nbsp|#34);|<[^>]{1,160}>", " ", s)
    s = unicodedata.normalize("NFKD", s.casefold())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\b(?:[a-z]\.){2,}(?=[^\w]|$)", lambda m: m.group().replace(".", ""), s)
    s = re.sub(r"'s\b", "", s).replace("'", "")
    return re.findall(r"[a-z]+|\d+", s)


def _add(cat, weight, words):
    global _MAXLEN
    d = _LEX[cat]
    for item in words.split("|"):
        k = tuple(_norm(item.strip()))
        if k:
            d[k] = max(d.get(k, 0), weight)
            _MAXLEN = max(_MAXLEN, len(k))


S = "sports"
T = "sci_tech"
B = "business"
W = "world"

_add(S, 7, """
football|baseball|basketball|hockey|cricket|rugby|soccer|tennis|golf|cycling|athletics|
badminton|volleyball|softball|triathlon|biathlon|weightlifting|gymnastics|archery|handball|
taekwondo|judo|karate|freestyle wrestling|boxing|lacrosse|billiards|snooker|curling|
marathon|decathlon|heptathlon|pentathlon|skiing|speedskating|skating|bobsled|bobsleigh|
snowboard|snowboarding|track and field|table tennis|beach volleyball|sailing regatta|equestrian|
auto racing|motor racing|horse racing|motorsport|olympics|olympic|paralympics|paralympic|
nba|wnba|nfl|nhl|mlb|mls|ncaa|ncaa tournament|afc|nfc|uefa|fifa|atp|wta|pga|lpga|
nascar|indycar|motogp|formula one|formula 1|super bowl|superbowl|world series|world cup|
champions league|premier league|premiership|bundesliga|serie a|la liga|eredivisie|fa cup|
uefa cup|six nations|tri nations|heineken cup|currie cup|stanley cup|calder cup|ryder cup|
presidents cup|solheim cup|davis cup|fed cup|hopman cup|heisman|wimbledon|roland garros|
tour de france|giro d italia|vuelta|grand prix|british open|australian open|french open|
pga tour|champions tour|us open|u s open|kentucky derby|breeders cup|melbourne cup|
world championships|world champion|world number one|world record holder|ballon d or|
grand slam|gold medal|silver medal|bronze medal|olympian|olympiad|sports network|espn
""")
_add(S, 5.5, """
quarterback|running back|linebacker|wide receiver|cornerback|fullback|tailback|tight end|
defensive end|defensive tackle|offensive tackle|defensive lineman|kicker|placekicker|
touchdown|interception|punt|kickoff|fumble|first downs|yards rushing|yards passing|end zone|
field goal|scrimmage|gridiron|ballpark|bullpen|dugout|pitcher|pitching|catcher|outfielder|
infielder|shortstop|baseman|slugger|hitter|batting|batter|leadoff|rbi|rbis|homer|homered|
home run|inning|strikeout|shutout|no hitter|doubleheader|pinch hit|sacrifice fly|stolen base|
reliever|closer role|fastball|designated hitter|bases loaded|triple double|double double|
dunk|slam dunk|free throw|three pointer|jumper at the buzzer|point guard|shooting guard|
rebounder|assists|layup|goaltender|goalie|blue line|power play goal|puck|hat trick|
midfielder|striker|defender|goalkeeper|equaliser|equalizer|penalty shootout|spot kick|
nil|extra time|yellow card|red card|centre back|winger|scrum|flyhalf|fly half|all blacks|
touchline|test match|one day international|limited overs|innings|wicket|batsman|batsmen|
bowler|leg spinner|lbw|half century|all rounder|not out|birdie|bogey|putt|golfer|fairway|
clubhouse lead|under par|over par|course record|tee shot|hole in one|playoff|quarterfinal|
semifinal|semi final|quarter final|tiebreak|tiebreaker|match point|break point|straight sets|
wild card|wildcard|pole position|pole sitter|pit stop|checkered flag|chequered flag|
race car|racehorse|jockey|racecourse|racetrack|sprinter|hurdler|medalist|medallist|
championship|champ|champion|heavyweight|middleweight|featherweight|welterweight|knockout|
lineout|penalty kick|doping|anti doping|sportsman|sportswoman|ballclub|test cricket
""")
_add(S, 3.4, """
sport|sports|athlete|athletic director|coach|coaching|team mate|teammate|trainer|club captain|
training camp|squad|roster|rookie|free agent|free agency|draft pick|all star|all american|
hall of fame|hall of famer|most valuable player|mvp|varsity|seeded|top seed|unseeded|
tournament|tourney|league|postseason|post season|preseason|pre season|regular season|
season opener|season finale|winning streak|losing streak|win streak|undefeated|winless|
levelled|rematch|matchup|rivalry|standings|bowl game|division title|baton|medal|podium|
referee|umpire|stadium|duel|tee off|leaderboard|peloton|velodrome|rider|time trial|
swimmer|diver|gymnast|wrestler|boxer|skier|skater|racer|runners up|runner up|finalist|
goal scorer|goalscorer|scorer|scoring|scored|sidelined|halftime|overtime|extra innings|
offseason|shot clock|locker room|home crowd|home side|away goal|home ice|speedway|
club record|showpiece event|first leg|second leg|return leg|top flight|relegation|
fixtures|relegated|kick off|first round|second round|third round|final round|opening round|
national team|national coach|captaincy|captained|captain of|comeback win|victory over|
win over|win against|loss to|defeat by|victory against|beat the|defending champion|
defending champs|defending champions|title defence|title defense|title holder|titleholder|
defending their title|title bout|title fight|banned substance|performance enhancing|
world ranking|world rankings|career high|personal best|career best|sudden death|play offs|
all stars|sideline|outplayed|outclassed|outscored|sacked as coach
""")
_add(S, 1.35, """
win|wins|won|victory|defeat|beat|beats|beating|beaten|edged|trounced|thrash|rout|outlast|
clinch|cruise|triumph|overcome|team|player|game|match|contest|season|cup|trophy|
unbeaten|streak|scoring|score|goal|yard|captain|bench|rival|favorite|favourite|
supporters|fans|arena|ball|kick|racing|runners|swimming|relay|lap|bout|final|finals|
surged past|finished first|finished second|took the lead|takes the lead|opening day|
second half|first half|second straight|third straight|fourth straight|six straight|
fourth quarter|fourth quarter comeback|career|injury|injured reserve|knee injury|
ankle injury|groin injury|shoulder injury|hamstring|torn ligament|comeback|retirement|
rebound|assisting|dribble|seed|yardage|meters|metres|record time|hosts|series opener|
home opener|fixture|shut out|buzzer|on aggregate|level terms|silverware|berth
""")

_add(S, 7, """
yankees|red sox|bosox|white sox|mets|dodgers|orioles|marlins|phillies|pirates of pittsburgh|
athletics of oakland|oakland as|padres|diamondbacks|d backs|astros|rockies|brewers|blue jays|
royals|cubs|braves|mariners|expos|twins|cardinals|reds|nationals|texas rangers|
san francisco giants|detroit tigers|anaheim angels|los angeles angels|cleveland indians|
lakers|celtics|knicks|mavericks|76ers|sixers|pistons|timberwolves|raptors|cavaliers|
clippers|grizzlies|supersonics|sonics|nuggets|spurs|trail blazers|warriors|nets|
miami heat|orlando magic|utah jazz|indiana pacers|atlanta hawks|chicago bulls|
charlotte bobcats|new orleans hornets|sacramento kings|houston rockets|phoenix suns|
washington wizards|packers|patriots|steelers|buccaneers|bucs|colts|bengals|jaguars|
vikings|raiders|seahawks|chargers|broncos|49ers|niners|cowboys|ravens|dolphins|
philadelphia eagles|new york giants|new york jets|detroit lions|chicago bears|
atlanta falcons|tennessee titans|kansas city chiefs|carolina panthers|miami dolphins|
new orleans saints|cleveland browns|st louis rams|washington redskins|buffalo bills|
canadiens|canucks|oilers|senators of ottawa|flames of calgary|calgary flames|ottawa senators|
maple leafs|red wings|bruins|blackhawks|flyers|thrashers|penguins|islanders|sabres|predators|
blue jackets|minnesota wild|colorado avalanche|tampa bay lightning|san jose sharks|
new jersey devils|dallas stars|anaheim ducks|new york rangers|nhlpa|
manchester united|manchester city|man utd|man united|arsenal|chelsea|liverpool|everton|
tottenham|hotspur|fulham|newcastle united|blackburn|bolton wanderers|aston villa|west brom|
west ham|crystal palace|charlton athletic|birmingham city|southampton fc|leicester city|
leeds united|real madrid|atletico madrid|fc barcelona|real sociedad|deportivo la coruna|
athletic bilbao|ac milan|inter milan|interazionale|internazionale|juventus|as roma|
fiorentina|sampdoria|lazio|bayern|bayer leverkusen|borussia|ajax amsterdam|psv|
feyenoord|paris saint germain|psg|olympique|benfica|fc porto|galatasaray|
glasgow rangers|glasgow celtic|celtic fc|old trafford|highbury|anfield|stamford bridge|
santiago bernabeu|san siro|wembley|lords cricket|fenway|yankee stadium|wrigley field|
busch stadium|lambeau field|the ashes|old firm|big ten|pac 10|big east|big 12|big twelve|
tar heels|blue devils|hokies|sooners|buckeyes|longhorns|nittany lions|fighting irish|
wolverines|cornhuskers|huskers|seminoles|boilermakers|razorbacks|yellow jackets|
crimson tide|trojans|bulldogs|huskies|aggies|gators|jayhawks|mountaineers|
rose bowl|orange bowl|fiesta bowl|sugar bowl|cotton bowl|bcs|march madness|
springboks|wallabies|black caps|wta tour|wembley stadium
""")
# Common names with non-sport meanings need more context than a full team name.
for _x in ("nets", "reds", "twins", "nationals", "warriors", "predators", "royals",
           "penguins", "mountaineers", "chargers", "raiders", "patriots", "clippers",
           "rockies", "senators", "arsenal", "chelsea", "liverpool", "braves", "rider",
           "defender", "wildcard", "nil", "cardinals"):
    if (_x,) in _LEX[S]:
        _LEX[S][(_x,)] = 3.1
_add(S, 1.8, """
giants|angels|falcons|eagles|bears|browns|jets|panthers|saints|rams|tigers|chiefs|
rangers|hawks|suns|hornets|bulls|rockets|devils|pacers|bobcats|penguins|wildcats|
pirates|badgers|bruins|ducks|coyotes|oaks|celtic|barca|toon|gunners|jaguars|
redskins|horned frogs|magpies|toffees|cavaliers
""")
_add(S, 7, """
schumacher|barrichello|raikkonen|montoya|jenson button|fernando alonso|michael schumacher|
dale earnhardt|earnhardt|gordon wins|jeff gordon|jimmie johnson|kurt busch|tony stewart|
lance armstrong|jan ullrich|ivan basso|roger federer|federer|roddick|hewitt|agassi|
safin|nalbandian|moya|henman|ferrero|nadal|srichaphan|ljubicic|serena williams|venus williams|
sharapova|mauresmo|henin|clijsters|davenport|kuznetsova|dementieva|myskina|capriati|
hingis|navratilova|molik|hantuchova|schnyder|zvonareva|sugiyama|tiger woods|vijay singh|
mickelson|els|goosen|garcia wins|darren clarke|montgomerie|sorenstam|karrie webb|michelle wie|
lindsay davenport|freddy adu|beckham|ronaldo|rooney|zidane|ronaldinho|owen hargreaves|
thierry henry|van nistelrooy|rvn|patrick vieira|vieira|eriksson|wenger|mourinho|
rafael benitez|benitez|alex ferguson|gerrard|lampard|owen hargreaves|didier drogba|
drogba|shevchenko|ballack|podolski|klinsmann|deco|ferdinand|raul gonzalez|eto o|
phelps|thorpe|el guerrouj|paula radcliffe|kelly holmes|marion jones|balco|gatlin|
asafa powell|carly patterson|hamm|ian thorpe|michael phelps|liu xiang|
tendulkar|ganguly|dravid|sehwag|laxman|dhoni|pathan|kumble|harbhajan|in­zamam|
inzamam|shoaib|afridi|muralitharan|sangakkara|jayawardene|lara hit|brian lara|
flintoff|michael vaughan|trescothick|strauss hit|harmison|ponting|gilchrist|warne|
mcgrath|hayden hit|kallis|pollock|ntini|graeme smith|flemming|wilkinson kicked|
lebron|kobe bryant|shaquille|shaq|iverson|garnett|nowitzki|yao ming|vince carter|
tracy mcgrady|ginobili|tim duncan|carmelo anthony|artest|dwyane wade|steve nash|
peyton manning|eli manning|tom brady|favre|culpepper|mcnabb|terrell owens|vick|
pennington|roethlisberger|bledsoe|belichick|bill parcells|randy moss|priest holmes|
barry bonds|sammy sosa|jeter|schilling|pedro martinez|manny ramirez|ortiz|
alex rodriguez|a rod|ichiro|clemens|matsui|pujols|beltran|garciaparra|francona|
joe torre|steinbrenner|guerrero hit|the yankees|nolan ryan|wayne gretzky|lemieux|
brodeur|bettman|bertuzzi|tyson|de la hoya|hopkins knocked|klitschko|trinidad ko|
muhammad ali|mike tyson|de la hoya|oscar dela hoya|yogi berra|messi|djokovic
""")

_add(T, 8, """
microsoft|windows xp|windows server|windows media|windows vista|google|apple computer|
apple inc|apple macintosh|apple store|ibm|intel|advanced micro devices|amd|motorola|
nokia|samsung|qualcomm|siemens mobile|alcatel|ericsson|sony ericsson|blackberry|
research in motion|rim blackberry|palmone|palmsource|cisco|hewlett packard|compaq|
dell|sun microsystems|oracle|peoplesoft|siebel|sap ag|adobe|macromedia|symantec|
veritas software|mcafee|computer associates|novell|red hat|mandrake linux|suse|
mozilla|netscape|firefox|thunderbird|linux|unix|solaris|openoffice|realnetworks|
nvidia|ati technologies|broadcom|infineon|texas instruments|tsmc|micron technology|
applied materials|national semiconductor|freescale|renesas|asustek|lenovo|acer inc|
toshiba|fujitsu|hitachi|sharp corp|kyocera|nec corp|canon inc|nikon|palm inc|
yahoo|ebay|paypal|aol|america online|ask jeeves|lycos|doubleclick|overture services|
earthlink|verisign|akamai|rackspace|autodesk|salesforce|vmware|checkpoint software|
check point software|seagate|western digital|emc corp|network appliance|sandisk|
linksys|juniper networks|brocade communications|lucent|nortel|jds uniphase|
sbc communications|bellsouth|verizon|cingular|nextel|sprint nextel|t mobile|
deutsche telekom|british telecom|bt group|vodafone|ntt docomo|ntt do co mo|sk telecom|
china mobile|china unicom|telecom italia|nintendo|playstation|xbox|gamecube|game boy|
electronic arts|ea sports|ubisoft|activision|atari|sega|capcom|konami|square enix|
rockstar games|blizzard entertainment|valve software|id software|sony computer|
openai|chatgpt|alphabet inc|meta platforms|facebook|instagram|tiktok|netflix|spotify|
youtube|skype|itunes|ipod|iphone|ipad|imac|ibook|powerbook|power mac|mac os|
macintosh|pentium|athlon|opteron|itanium|centrino|xeon|powerpc|thinkpad|vaio|
dreamworks animation software|bill gates|steve ballmer|steve jobs|linus torvalds|
larry ellison|carly fiorina|michael dell|scott mcnealy|sergey brin|larry page|
tim berners lee|craig barrett|andy grove|paul otellini|mark zuckerberg
""")
_add(T, 5.5, """
technology|technological|software|hardware|internet|cyberspace|world wide web|
website|web site|websites|web sites|web page|web server|online service|web portal|
web search|web browser|browser|search engine|search giant|search technology|
email|e mail|spam|spammer|anti spam|phishing|spyware|adware|malware|ransomware|
antivirus|anti virus|worm|computer virus|hacker|hacking|cyberattack|cybersecurity|
cyber security|denial of service|identity theft|firewall|exploit code|security flaw|
security hole|security vulnerability|security patch|security software|service pack|
operating system|os x|longhorn|directx|windows users|activex|sql server|open source|
free software|proprietary software|source code|programming language|java|javascript|
python language|visual basic|visual studio|xml|html|css|perl|linux kernel|
developer kit|web services|software maker|software company|software giant|
download|upload|downloading|file sharing|peer to peer|p2p|bittorrent|kazaa|grokster|
napster|edonkey|mp3|mpeg|streaming video|streaming music|digital music|music player|
dvd|blu ray|hd dvd|hdtv|flat panel|liquid crystal|plasma display|lcd|oled|megapixel|
digital camera|digital imaging|camcorder|digital video recorder|tivo|vcr|digital tv|
consumer electronics|electronics maker|gadget|gizmo|robot|robotics|artificial intelligence|
machine learning|neural network|chatbot|facial recognition|speech recognition|data mining|
database|data center|datacentre|supercomputer|mainframe|workstation|computer|computing|
personal computer|laptop|notebook computer|tablet pc|pda|handheld|desktop pc|smartphone|
smart phone|cellphone|cell phone|mobile phone|cellular phone|handset|mobile device|
wireless|wi fi|wifi|wimax|bluetooth|broadband|dsl|adsl|ethernet|fiber optic|fibre optic|
telecom|telecommunications|telephony|voip|internet protocol|voice over ip|3g|4g|5g|
gsm|cdma|gprs|text message|instant messaging|messenger service|ringtone|modem|
router|networking|bandwidth|hotspot|access point|rfid|radio frequency identification|
semiconductor|chipmaker|chip maker|microchip|chipset|microprocessor|processor|cpu|
chipmaking|transistor|integrated circuit|motherboard|graphics card|graphics chip|
memory chip|flash memory|ram chip|hard drive|hard disk|floppy disk|usb|firewire|
gigabyte|megabyte|terabyte|gigahertz|mhz|nanometer|server|storage array|
video game|videogame|video gaming|game console|console maker|game developer|game publisher|
game studio|game developers|game industry|games industry|computer game|online game|
gaming console|gaming system|halo 2|half life|grand theft auto|world of warcraft|mmorpg|
doom 3|sims 2|madden nfl|final fantasy|mp3 player|walkman|portable player|digital rights|
drm|riaa|mpaa|icann|domain name|dot com|dotcom|blog|blogger|blogging|weblog|
podcast|e commerce|e tailer|e business|online auction|online retailer|click fraud|
spectrum auction|information technology|infotech|nanotechnology|nanotech|biotechnology
""")
_add(T, 3, """
tech|hi tech|high tech|pc|pcs|notebook|desktop|chip|silicon valley|electronics|
digital|online|web|website|multimedia|virtual reality|interactive entertainment|
network equipment|network gear|network security|wireless carrier|phone company|
mobile operator|cellular|cell phones|landline|telephone service|local phone|long distance phone|
mobile network|telecoms|phone maker|phone users|mobile|sms|telco|telstra|telekom|
comcast|comdex|linuxworld|macworld|idg|zdnet|cnet|pcworld|computerworld|infoworld|
pc magazine|pc world|the register|slashdot|techweb|eweek|wired news|newsfactor|
technology research|forrester|gartner|forrester research|it departments|it managers|
silicon|microelectronics|data storage|server market|enterprise applications|it services|
benchmark test|security update|file format|format war|prototype|beta version|
user interface|password|encrypted|encryption|decrypt|authenticate|authentication|
browsing|toolbar|popup|pop up ads|pop ups|teleconference|videoconference|screen saver|
freeware|patch|dial up|batteries|lithium ion|rechargeable|fuel cell|hybrid engine|
search tool|web based|online shopping|online advertising|online music|music download|
archiving|news feed|rss|wikimedia|wikipedia|chat room|message board|newsgroup|
gamers|gameplay|gaming|joystick|console|pixel|graphics|animation|animator|rendering|
electronic device|printer|scanner|copier|photocopy|inkjet|laserjet|dvr|mobile computing|
television set|remote control|set top box|cable modem|digital subscriber line|
apple|amazon com|amazon web services|amazon|realplayer|sony|philips electronics|
panasonic|lg electronics|logitech|gateway inc|sun java|hp|sprint corp|att wireless|
at t wireless|at t corp|sk telecom|bt broadband|symbian|tungsten handheld|
flaw in|vulnerability|exploit a|security bulletin|security bug|security fix
""")
_add(T, 1.2, """
network|electronic|device|machinery|innovation|innovative|keyboard|mouse|screen|
display|portable|users|installation|install|upgrade|release date|platform|systems|
developer|application|code|bug|fixes|memory|license|licensing|band|speed|camera|phone|
telephone|patent|copyright|piracy|pirated|high definition|video|data|surfing|design|
unveil|rollout|roll out|version|features|experimental|battery|engineer|engineering|
laboratory|lab|technical|sensor|wire|cable|photograph|imaging|model|automated|
automatic|on the net|surfers|the net|keynote|breakthrough
""")

_add(T, 6.5, """
science|scientific|scientist|researcher|astronomer|astronomy|astrophysicist|cosmologist|
nasa|esa spacecraft|space agency|space station|space shuttle|space exploration|
outer space|space travel|space flight|spaceflight|spaceship|spacecraft|space probe|
space telescope|space tourism|space tourist|spacewalk|spacesuit|spaceport|space race|
astronaut|cosmonaut|spacex|virgin galactic|sputnik|soyuz|baikonur|cape canaveral|
hubble|cassini|huygens|voyager probe|mars rover|mars express|international space|
red planet|jet propulsion laboratory|spaceshipone|x prize|ansari x|burts rutan|
comet|asteroid|supernova|black hole|neutron star|galaxy|galaxies|planet|planetary|
exoplanet|solar system|solar wind|big bang|light years|telescope|interstellar|
martian|meteorite|lunar|milky way|kuiper belt|dark matter|gamma ray|celestial|
genetics|geneticist|genetic|genetically modified|genome|genomics|genomic|dna|rna|
chromosome|stem cell|embryonic|cloning|clone embryo|biologist|molecular biology|
biology|biochemical|biochemistry|microbe|microbiology|bacteria|bacterium|
antibody|protein|neuron|neuroscience|clinical trial|gene therapy|biomedical|
paleontologist|palaeontologist|fossil|dinosaur|prehistoric|tyrannosaurus|
archaeologist|archeologist|archaeology|excavation site|hominid|hominin|neanderthal|
anthropologist|geologist|geological survey research|seismologist|physicist|physics|
chemistry|particle accelerator|cern|quantum|proton|neutrino|antimatter|fusion reactor|
nanotube|nanoparticle|isotope|magnetic field|laser beam|superconductivity|
national academy of sciences|journal nature|journal science|new scientist|
nobel prize in physics|nobel prize in medicine|nobel prize in chemistry|
national institutes of health|journal of medicine|medical journal|lancet|
new england journal|american medical association|scientific american
""")
_add(T, 3.4, """
research|study finds|study shows|new study|a study|studies show|studies suggest|
according to a study|clinical study|in the journal|published in|peer reviewed|
findings|experiment|discovery|uncovered evidence|evidence suggests|discovered|
theory of|scholar|laboratory|lab tests|patient|diagnosis|diagnostic|diagnose|
cancer|tumor|tumour|alzheimer|parkinson|diabetes|diabetic|dementia|heart disease|
heart attack|cardiac|stroke risk|cholesterol|obesity|obese|hypertension|artery|
vaccine|vaccination|inoculation|antiviral|antibiotic|infection|infectious disease|
pathogen|parasite|immune system|immunity|immune response|influenza strain|
medical research|medicine|therapy|therapeutic|surgery|surgical|transplant|
medical procedure|physician|biopsy|fertility|embryo|molecule|enzyme|tissue|
organism|species|evolution|evolutionary|primate|mammal|extinct|extinction|
conservationist|wildlife|ecosystem|biodiversity|marine life|coral reef|ecology|
habitat|rainforest|glacier|arctic ice|ice sheet|ice age|global warming|climate change|
greenhouse gas|carbon dioxide|ozone layer|climatologist|meteorologist|ocean floor|
tectonic|atmospheric|solar energy|renewable energy technology|time capsule|
rocket launch|satellite|orbit|orbital|mars|saturn|jupiter|pluto|neptune|moon|
universe|cosmos|zero gravity|mission control|rocket booster|launch pad|robotic|
alien life|extraterrestrial|intelligent life|light year|space elevator|space age|
accelerator|electromagnetic|infrared|ultraviolet|radio waves|microscope|molecular|
algorithm|simulation|computational|mathematical|mathematician|theorem|prime number
""")
_add(T, 1.15, """
study|studied|investigation found|found that|suggests|evidence|discover|reveal|
university|professor|institute|colleagues|published|samples|tested|testing|
medical|health|doctors|drug|disease|virus|brain|body weight|healthy|cure|
treatment|illness|cells|gene|animal|human|oxygen|carbon|environmental|environment|
climate|earth|space|rocket|mission|physics|gravity|crater|ancient|ruins|bones|
museum|skeleton|expedition|habitable|volcanic|fireball|sea level|endangered|rare
""")

_add(B, 6.5, """
wall street|stock market|stock exchange|share market|equity market|stock index|
dow jones|dow industrials|dow average|nasdaq|nyse|amex composite|s p 500|sp 500|
ftse|footsie|nikkei|hang seng|cac 40|dax|russell 2000|standard poor|standard and poor|
standard poors|stock futures|blue chip stocks|blue chips|industrial average|
mutual fund|hedge fund|exchange traded fund|investment banking|investment bank|
private equity|venture capital|initial public offering|ipo|listed shares|share price|
price target|share buyback|stock buyback|stock split|stock option|quarterly earnings|
quarterly profit|net income|net profit|net loss|operating profit|earnings per share|
per share|a share|earnings forecast|earnings estimates|profit forecast|profit warning|
interest rates|interest rate|basis point|federal reserve|alan greenspan|central bank|
bank of england|european central bank|bank of japan|monetary policy|gross domestic product|
gdp|economic growth|economic recovery|trade deficit|budget deficit|trade surplus|
consumer confidence|consumer prices|consumer price index|producer prices|consumer spending|
retail sales|housing starts|unemployment rate|jobless claims|payroll report|balance of payments|
money supply|treasury bond|treasury yield|treasury note|bond market|currency market|
foreign exchange|exchange rate|greenback|forex|record low against|record high against|
crude oil|crude futures|oil futures|oil prices|price of oil|oil price|light crude|
brent crude|nymex|opec|petroleum exporting countries|oil cartel|gold futures|
london metal exchange|commodity prices|commodity market|energy prices|prices per barrel|
quarter profit|quarter loss|quarter earnings|quarter results|quarter revenue|
third quarter profit|same store sales|quarterly results|securities and exchange commission|
insider trading|securities fraud|accounting fraud|accounting scandal|bankruptcy protection|
chapter 11|antitrust regulators|credit rating|chief financial officer|cash dividend|
quarterly dividend|merger agreement|takeover bid|hostile takeover|buyout offer|
stockholders|shareholder|shareholders|stockbroker|brokerage|underwriter|
day trader|trading session|in early trading|in late trading|after hours trading|
stock analyst|fund manager|business confidence|world trade organization|wto|
international monetary fund|world bank|economic outlook|marketwatch|cnn money|
forbes|bloomberg|financial times|investor business daily|the motley fool
""")
_add(B, 4.1, """
business|economy|economic|economist|economics|financial|finance|fiscal|
banking|banker|bank|lender|mortgage|loan|borrower|debt|bondholder|creditor|
investment|investor|portfolio|equities|stock|stocks|shares|stockholder|securities|
bourse|bullish|bearish|trader|trading|selloff|sell off|rallied|benchmark index|
earnings|profit|profitable|profitability|revenue|turnover|dividend|pretax|
pre tax|after tax|balance sheet|cash flow|write down|writedown|write off|
accountant|audit|auditor|regulator|antitrust|anti trust|price fixing|
merger|merge|takeover|buyout|acquire|acquisition|bidder|spinoff|spin off|
conglomerate|subsidiary|holding company|joint venture|consortium|liquidation|
liquidate|receivership|bankrupt|bankruptcy|restructuring|restructure|refinance|
bailout|solvency|defaulted|fraud charges|indictment of former|chief executive|
ceo|cfo|board of directors|corporate governance|corporation|corporate|company|
retail|retailer|wholesaler|wholesale|supermarket|department store|discount store|
grocery chain|fast food chain|franchisee|automaker|carmaker|auto maker|auto sales|
motor vehicle sales|airline|airways|air carrier|air fare|airfare|airliner order|
low cost carrier|discount carrier|aviation industry|manufacturer|manufacturing|
factory orders|industrial production|labor market|jobs growth|hiring|layoffs|
layoff|payroll|unemployment|jobless|labor costs|pension|401 k|health insurer|
insurance|insurer|reinsurance|premium rates|reinsurer|real estate|housing market|
homebuilder|property market|inflation|deflation|recession|monetary|tariff|subsidies|
importers|exporters|exports|imports|trade agreement|trade talks|free trade|
fuel costs|oil supply|oil output|oil production|oil demand|gasoline|refiner|refinery|
petroleum|crude|barrel|commodity|commodities|bullion|futures|fixed income|
credit card|debit card|savings account|car loans|currency|devaluation|
depreciation|bond yield|yields rose|yields fell|benchmark rate|rate hike|
rate cut|raise rates|cut rates|tax cuts|tax break|sales tax|income tax|
consumer sentiment|business activity|service sector|purchasing managers|supply management|
productivity|valuation|market capitalization|market value|competitiveness|
marketing|advertising agency|advertiser|ad campaign|price cuts|capital spending
""")
_add(B, 1.8, """
corp|inc|ltd|plc|co ltd|firm|companies|industry|commercial|sector|market|
sales|sell|selling|buy|purchase|deal|agreement|bid|offer|transaction|buyer|
ownership|owner|management|executive|chairman|businessman|billionaire|entrepreneur|
share|index|dow|exchange|analyst|estimate|forecast|outlook|margin|quarterly|
third quarter|second quarter|first quarter|fourth quarter|year ago|year earlier|
full year|sales growth|year on year|grew|growth|expand|expansion|slump|sluggish|
surge|plunge|tumbled|fell|declined|climbed|gained|edged higher|higher|lower|
record high|record low|all time high|all time low|pricing|price|cost|spending|
supply|demand|production|output|export|import|trade|traded|money|fund|funding|
billion|million dollars|dollar|euro|yen|sterling|cent|percent|tax|accounting|
capital|cash|payment|fees|wealth|compensation|salary|budget|losses|annual|
customer|consumer|shopping|store|outlet|restaurant|chain|product|inventory|
shipment|delivery|overhaul|workforce|employment|employee|employer|worker|
labor union|strike action|job cuts|cut jobs|labor costs|labor dispute|factory|
business plan|contract|supplier|distributor|exporting|distribution|warehouse|
carrier|flights|jetliner|fleet|passengers|aircraft|ticket prices|tourism|tourist industry|
oil|petrol|diesel|energy|natural gas|mining|industrial|rubber|gold prices|
pharmaceutical|drugmaker|drug maker|luxury|luxury goods|fashion|brand|recall|
chief operating officer|filed suit|settlement|compensate|liability|franchise
""")
_add(B, 7, """
exxon|mobil corp|exxonmobil|chevrontexaco|chevron|conocophillips|royal dutch|
royal dutch shell|british petroleum|yukos|gazprom|lukoil|rosneft|yuganskneftegaz|
petrochina|sinopec|petrobras|totalfina|schlumberger|halliburton co|saudi aramco|
wal mart|walmart|asda|kmart|sears|jc penney|costco|home depot|lowe s|
target corp|toys r us|best buy co|circuit city|barnes noble|barnes and noble|
marks spencer|marks and spencer|sainsbury|sainsburys|tesco|carrefour|ahold|
morrisons|federated department stores|neiman marcus|macy|nordstrom|kohl|
procter gamble|procter and gamble|unilever|nestle|kraft foods|general mills|
kellogg|coca cola|pepsico|pepsi|mcdonald|burger king|starbucks|wrigley co|
heinz|cadbury|diageo|anheuser|safeway|kroger|tyson foods|hershey|danone|
altria|philip morris|british american tobacco|reynolds american|
colgate palmolive|kimberly clark|gillette co|l oreal|estee lauder|
daimlerchrysler|daimler|chrysler|general motors|ford motor|toyota|honda motor|
hyundai motor|volkswagen|bmw|renault|nissan|peugeot|fiat auto|mitsubishi motors|
volvo|rolls royce|porsche|suzuki motor|caterpillar inc|deere co|
boeing|airbus|eads|embraer|bombardier|american airlines|united airlines|
us airways|delta air lines|continental airlines|northwest airlines|southwest airlines|
jetblue|ryanair|easyjet|british airways|air france|lufthansa|alitalia|qantas|
singapore airlines|cathay pacific|air canada|virgin atlantic|american express|
bear stearns|goldman sachs|morgan stanley|merrill lynch|jpmorgan|jp morgan|
bank of america|citigroup|citibank|hsbc|deutsche bank|credit suisse|ubs|
barclays|lloyds tsb|abbey national|santander|lehman brothers|wells fargo|
bank one|royal bank of scotland|fannie mae|freddie mac|countrywide financial|
aig|american international group|marsh mclennan|marsh and mclennan|metlife|
berkshire hathaway|warren buffett|fidelity investments|charles schwab|
general electric|honeywell|tyco|enron|worldcom|parmalat|arthur andersen|
kpmg|pricewaterhousecoopers|deloitte|ernst young|ernst and young|
pfizer|merck|glaxosmithkline|astrazeneca|novartis|roche holding|bayer ag|
bristol myers|eli lilly|johnson johnson|sanofi|aventis|wyeth|schering plough|
amgen|chiron corp|biogen|medtronic|guidant|boston scientific|vioxx|
walt disney|viacom|time warner|news corp|dreamworks|metro goldwyn mayer|
nbc universal|mgm mirage|harrah|hilton hotels|marriott|mcdonalds corp|
fedex|united parcel service|deutsche post|union pacific|p o ferries|
nike inc|reebok|adidas|tiffany co|lvmh|gucci|prada|richemont|
bhp billiton|rio tinto|anglo american|arcelor|us steel|alcoa|dupont|
dow chemical|monsanto|international paper|lockheed martin|northrop grumman|
raytheon|bae systems|blackstone group|carlyle group|kkr|aetna|anthem inc
""")

_add(W, 6.5, """
election|reelection|re election|electoral|voter|ballot|referendum|parliament|
parliamentary|senate|senator|congressman|congresswoman|legislature|legislator|
lawmakers|prime minister|foreign minister|foreign ministry|interior minister|
foreign secretary|secretary of state|defense minister|defence minister|cabinet minister|
head of state|presidential candidate|democratic party|republican party|labour party|
conservative party|opposition party|ruling party|party leader|opposition leader|
politburo|communist party|national assembly|constitutional court|supreme court|
white house|downing street|kremlin|state department|pentagon|defence ministry|
united nations|security council|general assembly|un peacekeepers|peacekeeper|
peacekeeping|nato|african union|arab league|middle east peace|peace talks|
peace process|peace accord|ceasefire|cease fire|truce|disarmament|
genocide|war crime|massacre|atrocity|ethnic cleansing|human rights|civil liberties|
terrorism|terrorist|counterterrorism|counter terrorism|anti terror|al qaeda|al qaida|
al queda|al jazeera|bin laden|taliban|hamas|hezbollah|hizbollah|islamic jihad|
islamist|insurgency|insurgent|militant|militia|guerrilla|guerilla|separatist|
suicide bomber|suicide bomb|car bomb|roadside bomb|bomb blast|air strike|airstrike|
hostage|kidnap|abduct|abduction|kidnapping|behead|assassination|assassinate|
gunmen|gunman|gunfire|shootout with police|armed men|warplane|warship|troops|
peace deal|civil war|war on terror|terror suspect|martial law|prisoner of war|
weapons of mass destruction|nuclear weapons|nuclear arms|nuclear program|nuclear programme|
hurricane|typhoon|cyclone|earthquake|tsunami|tornado|aftershock|landslide|
suicide attack|death toll|killed at least|were killed|people were killed|people died|
refugee|asylum seeker|humanitarian|aid workers|red cross|famine|evacuation|
war crimes tribunal|death row|death penalty|mass grave|mass graves|darfur|
gaza|west bank|ramallah|baghdad|fallujah|falluja|najaf|sadr city|abu ghraib|
guantanamo|chechnya|beslan|kashmir|darfur region|srebrenica
""")
_add(W, 4.0, """
politics|political|politician|diplomacy|diplomatic|diplomat|embassy|ambassador|
government|governor|mayor|premier|chancellor|monarch|monarchy|kingdom|cabinet|
ministry|minister|constitution|constitutional|coalition|opposition|democracy|
democratic|republican|democrat|bipartisan|presidency|presidential|administration|
campaign trail|candidate|candidacy|running mate|swing state|primaries|nominee|
nomination|polling|pollsters|voting|vote|inauguration|resignation|ousted|
resign|overthrow|coup|dictator|regime|reformist|nationalist|communist|
socialist|conservatives|right wing|left wing|legislation|lawmaker|congress|
protester|protestor|demonstrator|demonstration|rally against|unrest|riot|
rioter|protest|activist|petition|dissident|oppression|torture|civilian|
occupation|occupied|army|military|soldier|marine corps|us marines|infantry|
battalion|commander|general staff|armed forces|naval|navy|air force|air raid|
security forces|security personnel|rebel|rebellion|uprising|resistance fighters|
border guard|border crossing|invasion|invade|combat|battlefield|offensive against|
artillery|rocket attack|missile|munition|warhead|uranium enrichment|nuclear watchdog|
explosive|explode|explosion|bomb|bomber|bombing|terror|terrorize|attackers|
ambush|clash|ambushed|shelling|firefight|bloodshed|bloodiest|deadliest|
murder|homicide|slaying|slain|rape|molest|stabbing|stabbed|arson|
police|detective|policeman|policemen|sheriff|fbi|scotland yard|interpol|
arrest|custody|detain|detainee|detention|prison|prisoner|jail|sentenced|
convict|acquit|defendant|prosecutor|indict|trial of|pleaded guilty|pleaded not guilty|
wanted for|accused of killing|shooting|robbery|theft|drug trafficking|
smuggling|extradition|perpetrator|culprit|criminal|crime|corruption|
casualties|casualty|fatality|victim|survivor|wounded|evacuate|disaster|
devastation|flooding|floods|mudslide|avalanche|wildfire|drought|monsoon|
torrential|storm surge|relief efforts|rescuers|wreckage|plane crash|air crash|
derailment|collision|epicenter|rich­ter scale|outbreak|bird flu|avian flu|
epidemic|pandemic|aids epidemic|world health organization|sars outbreak|
border dispute|sanctions|arms embargo|summit|peace envoy|envoy|treaty|
religious|mosque|islamic|muslim|sunni|shiite|shia|cleric|ayatollah|imam|
church|pope|pontiff|vatican|catholic|archbishop|pilgrim|pilgrimage|
same sex marriage|gay marriage|abortion rights|apartheid|racism|racial discrimination
""")
_add(W, 1.65, """
nation|national|state run|authorities|officials|president|leadership|leader|
citizen|policy|law|ban|banned|accused|alleged|inquiry|investigation|investigate|
justice|judge|court|witness|testified|trial|hearing|appeal|allegation|charges|
accuse|guilty|lawyer|attorney|evidence of|scandal|illegal|borders|border|
immigrant|immigration|religion|ethnic|tribal|public opinion|crowd|march|
peace|war|conflict|crisis|violence|violent|kill|dead|death|die|fatal|injure|
injuries|missing|rescue|recover bodies|incident|accident|threat|threaten|
attack|security|targeted|warn|warning|urgent|blast|shot dead|shoot|armed|
storm|winds|rain|rains|flood|battered|shore|coast|severe weather|homeless|
poor people|poverty|aid|donor|international community|allies|delegation|
bilateral|relations|visited|talks|meeting|urged|vow|pledge|rally|campaign|
province|village|district|local residents|capital city|neighboring|neighbouring|
unity|memorial|funeral|flag|anniversary|schoolchildren|children killed|hospitalized|
embattled|controversial|disputed|tensions|independence|autonomy
""")
_add(W, 5.7, """
george bush|george w bush|president bush|john kerry|kerry|cheney|john edwards|
colin powell|condoleezza|donald rumsfeld|rumsfeld|john ashcroft|tom ridge|
homeland security|tony blair|jack straw|downing st|jacques chirac|chirac|
schroeder|berlusconi|vladimir putin|putin|medvedev|boris yeltsin|lukashenko|
yanukovich|yanukovych|yushchenko|kuchma|saakashvili|kofi annan|annan|
yasser arafat|arafat|ariel sharon|sharon|mahmoud abbas|netanyahu|olmert|
palestinian|israeli|intifada|west bank settlement|settlers|p l o|plo|
muqtada|moqtada|al sadr|allawi|alawi|al sistani|zarqawi|saddam|iraqi|
iranian nuclear|tehran|pyongyang|kim jong|pervez musharraf|musharraf|
hamid karzai|karzai|osama|al zawahri|zawahiri|abu sayyaf|jemaa islamiyah|
megawati|yudhoyono|thaksin|suu kyi|junta|hu jintao|wen jiabao|koizumi|
dalai lama|chen shui bian|manmohan singh|atal bihari|sonia gandhi|
robert mugabe|mugabe|thabo mbeki|mbeki|nelson mandela|olusegun obasanjo|
laurent gbagbo|janjaweed|african mediation|hugo chavez|chavez|fidel castro|
pinochet|lula da silva|martin torrijos|aristide|zapatero|aznar|
elbaradei|iaea|amnesty international|human rights watch|european parliament|
boris johnson|joe biden|president trump|barack obama|zelensky|zelenskiy
""")
_add(W, 1.5, """
bush|blair|clinton|blix|afghanistan|afghan|iraq|iran|israel|palestine|palestinians|
syria|lebanon|lebanese|sudan|somalia|rwanda|congo|sierra leone|liberia|
haiti|bosnia|kosovo|serbia|macedonia|ukraine|north korea|myanmar|burma|
tibet|east timor|aceh|west darfur|ivory coast|saudi arabia|jordanian|
damascus|kabul|beirut|jerusalem|tel aviv|basra|mosul|samarra|tikrit|
kandahar|khartoum|the hague|kiev|kyiv|islamabad|grozny|jakarta|pristina|
middle east|middle eastern|arab world|southeast asia|korean peninsula|
european union|united states and|african leaders|western leaders
""")

# Some high-frequency homonyms are weak evidence in isolation.
for _c, _items in (
    (S, {"assists": 2.7, "defender": 2.2, "heavyweight": 3.0, "duel": 1.8,
         "grand prix": 6.5, "tyson": 4, "hamm": 4, "seed": .8}),
    (T, {"worm": 4.2, "apple": 3.5, "mobile": 1.9, "discovery": 2.4,
         "patient": 2.3, "influenza strain": 4.3, "research": 3.0,
         "published in": 2.3, "extinct": 4.4, "batteries": 1.8,
         "infection": 2.7, "mars": 5.2, "laboratory": 3, "java": 4.1}),
    (W, {"premier": 1.8, "resign": 2, "resignation": 2, "summit": 2.8,
         "cabinet": 2.8, "demonstration": 2.5, "nomination": 2.7,
         "administration": 2, "congress": 3, "convict": 3.5}),
    (B, {"company": 2.6, "shareholder": 4.8, "shareholders": 4.8,
         "regulator": 2.7, "financial": 3.2, "business": 2.9, "capital": .8,
         "bank": 3.3, "turnover": 2.6, "output": 1.5, "higher": .8, "lower": .8})
):
    for _k, _val in _items.items():
        _LEX[_c][tuple(_norm(_k))] = _val

# Context patterns include events often described without explicitly naming the field.
_RX = {c: [] for c in _CATS}


def _rx(c, w, p):
    _RX[c].append((re.compile(p, re.I), w))


_rx(S, 5.8, r"\b\d{1,3}\s*[-–]\s*\d{1,3}(?!\s*[-–]\s*\d)\b")
_rx(S, 6, r"\b(?:beat|defeated|downed|edged|routed|lost to|win over|won|whipped|thrashed|overcame|drew)\b.{0,65}?\b\d+\s*(?:-|to)\s*\d+")
_rx(S, 5, r"\b(?:ran|rushed|threw|pass(?:ed)?|carry|carries|rushing|passing|scampered)\b.{0,24}\b(?:yards?|touchdowns?)\b")
_rx(S, 5, r"\b(?:[0-9]+|two|three|four|five|six|seven|eight|nine|ten)[- ](?:run|wicket|yard|hole|goal|point|shot|stroke|set|game|match|inning|under|over par|length)(?:s)?\b")
_rx(S, 5, r"\b(?:win|victory|rout|thrashing|loss|draw|triumph|upset|rally|comeback|lead)\s+(?:over|against|at home to)\b")
_rx(S, 3.8, r"\b(?:title|final|medal|tournament|trophy|championship|opener|race|round|tourney|series|match)\b.{0,48}\b(?:win|won|winner|clinched|defence|defense|defend|defeat|victory|record|play|rival)\b")
_rx(S, 4.5, r"\b(?:defend(?:ing)?|reach(?:ed)?|retain(?:ed)?|win(?:ning)?|won|clinche[ds]?|captur(?:e[ds]?|ing)|claim(?:ed)?|advanc(?:e[ds]?|ing) to)\b.{0,44}\b(?:title|round|championship|semis|finals?|quarterfinals?|crown|trophy|cup|medal|pennant)\b")
_rx(S, 3.5, r"\b(?:no\.?|number|ranked|seeded)\s*(?:1|2|3|4|5|one|two|three|four)\b.{0,55}\b(?:beat|win|lost|defeated|advanced|played|won)\b")
_rx(S, 3.5, r"\b(?:first|second|third|fourth|fifth|last|final|opening|extra)[- ](?:period|inning|set|hole|lap|minute|touchdown|wicket|round)\b")
_rx(S, 4, r"\b(?:his|her|their|team'?s?)\s+(?:\w+[- ]straight|\w+ career|first career|home|away)\s+(?:wins?|victor(?:y|ies)|starts?|games?|titles?|defeats?)\b")
_rx(S, 4, r"\b(?:scored|added|had|finished with|recorded)\s+(?:a (?:career|season)[- ]high )?\d+ (?:points|goals|assists|rebounds|runs|saves|aces|yards)\b")
_rx(B, 3.5, r"(?:[$£€]\s*(?:us)?\s*[\d.,]+|\b[\d.,]+\s*(?:billion|million|bn|bln|mln)\s*(?:dollars|pounds|euros|yen|yuan|rupees)\b)")
_rx(B, 2.8, r"\b(?:rose|fell|up|down|gained|lost|soared|grew|climbed|decreased|increased|plunged|slid|added|shed|growth of)\s+(?:by |nearly |almost )?\d[\d.,]*\s*(?:%|percent|per cent|points|cents)")
_rx(B, 3, r"\b(?:[1-4]q|q[1-4]|yr[- ]on[- ]yr|yoy|eps|ebitda|ebit)\b")
_rx(B, 4.5, r"\b(?:reporte[ds]|post(?:s|ed)|forecast[s]?|saw|expect[s]?|announce[sd])\b.{0,45}\b(?:profit|loss|earnings|revenue|income|sales)\b")
_rx(B, 3.5, r"\b(?:buy|acquire|sell|buying|take over|purchase)\b.{0,45}(?:[$£€]|\b(?:rival|stake|division|unit)\b)")
_rx(B, 3.5, r"\b(?:oil|crude|bullion|dollar|sterling|gold|stocks|shares|prices|indexes|bourses|yields)\s+(?:rose|fell|hit|jump|jumped|slide|slip|drop|end|set|rise|gain|up|down|dip|firm|soar|sink|ease|close|surge|rally|tumble|rebound)\w*\b")
_rx(B, 4.5, r"\b(?:reuters|ap)\s*[-:–]?\s*(?:u\.?s\.? |european |tokyo |japanese |asian )?(?:stock[s]?|crude|oil prices|share prices|the dollar)\b")
_rx(T, 4.5, r"\b(?:scientists?|researchers?|astronomers?|doctors?|experts?|a study|the study)\b.{0,70}\b(?:found|identified|discovered|say|said|link|suggest|reveal|detect|report|warn|isolate|unlock|show|uncover)\w*\b")
_rx(T, 3.5, r"\b(?:new|next[- ]generation|latest|first|portable|digital|wireless|mobile|handheld|online)\s+(?:versions?|models?|devices?|chips?|services?|players?|phones?|networks?|technology|handsets?|systems?|products?)\b")
_rx(T, 4.8, r"\b(?:windows|mac|pc|playstation|nintendo|xbox)\s+(?:\d+|xp|users?|software|games?|platforms?|consoles?|based|compatible|mini|os|system)\b")
_rx(T, 3.5, r"\b(?:\d+(?:\.\d+)?\s*(?:gb|mb|ghz|mhz|mbps|gbps|megapixels?)|802\.11\w?|802\.16\w?)\b")
_rx(T, 4.5, r"\b(?:mysterious|new|ancient|previously unknown)\s+(?:species|fossil|creature|planet|particle|skull|skeleton|star|galaxy|organism)\b")
_rx(W, 4, r"\b(?:killed|dead|wounded|injured|drowned|trapped|missing|arrested)\b.{0,28}\b(?:people|civilians|men|women|children|officers|soldiers|others|rebels)\b|\b(?:people|civilians|others|troops|soldiers)\s+(?:were |have been |are )?(?:dead|wounded|killed|injured|missing)\b")
_rx(W, 3.8, r"\b(?:charged|accused|convicted|sentenced|arrested|suspected)\s+(?:of|with|in connection|on suspicion|over|for|to)\b")
_rx(W, 3.8, r"\b(?:category [1-5]|richter scale|magnitude [0-9]|powerful quake|ashore|storm[- ]battered|made landfall)\b")
_rx(W, 4, r"\b(?:the polls|presidential (?:race|debate|campaign)|cast (?:their |his |her )?ballots?|voted (?:to|for|in favor)|running for (?:office|president))\b")

_TECHCO = set()
for _item, _w in _LEX[T].items():
    if _w == 8 or _item in (("apple",), ("sony",), ("hp",), ("amazon",)):
        _TECHCO.add(_item)

# Resolve inflections without stemming unrelated words to the same prefix.
def _forms(w):
    f = []
    if w.endswith("ies"):
        f.append(w[:-3] + "y")
    if w.endswith("es"):
        f.append(w[:-2])
    if w.endswith("s") and len(w) > 3:
        f.append(w[:-1])
    if w.endswith("ied"):
        f.append(w[:-3] + "y")
    if w.endswith("ed"):
        f.extend((w[:-1], w[:-2]))
        if len(w) > 4 and w[-3] == w[-4]:
            f.append(w[:-3])
    if w.endswith("ing"):
        f.extend((w[:-3], w[:-3] + "e"))
        if len(w) > 5 and w[-4] == w[-5]:
            f.append(w[:-4])
    return f


def _weight(text, heading):
    tokens = _norm(text)
    sc = {c: 0.0 for c in _CATS}
    if not tokens:
        return sc
    if len(tokens) > 1800:
        tokens = tokens[:1800]
    techco = 0
    for cat in _CATS:
        counts = Counter()
        hits = []
        d = _LEX[cat]
        i = 0
        while i < len(tokens):
            # Prefer a whole entity/phrase to counting its component words twice.
            for size in range(min(_MAXLEN, len(tokens) - i), 0, -1):
                key = tuple(tokens[i:i + size])
                weight = d.get(key, 0)
                if not weight and (size == 1 or size <= 4 and key[-1].endswith("s")):
                    for alt in _forms(key[-1]):
                        k2 = key[:-1] + (alt,)
                        if k2 in d:
                            key = k2
                            weight = d[key] * .95
                            break
                if weight:
                    n = counts[key]
                    if n < 3:
                        lead = (1.34 if i < 10 else 1.09 if i < 23 else 1) if not heading else 1
                        hits.append(weight * lead * (1, .27, .11)[n])
                        if cat == T and key in _TECHCO:
                            techco = max(techco, 2 if i < 15 or heading else 1)
                    counts[key] += 1
                    i += size
                    break
            else:
                i += 1
        raw = text[:12000]
        for pat, value in _RX[cat]:
            m = pat.search(raw)
            if m:
                # A number range can also denote dates, years, prices, etc.
                if cat == S and value == 5.8 and (not hits or max(hits) < 2.0):
                    value = 1.2
                hits.append(value * (1.15 if m.start() < 80 else 1))
        hits.sort(reverse=True)
        sc[cat] = sum(v * (1 if j < 3 else .77 if j < 7 else .47 if j < 15 else .22)
                      for j, v in enumerate(hits))

    # Company results and litigation centered on a technology firm are tech;
    # do not make the same adjustment in a general market roundup.
    if techco and sc[B] > 0:
        roundup = re.search(r"\b(?:stock markets?|wall street|dow jones|market wrap|stocks (?:rose|fell|end|close|up|down))\b", text, re.I)
        sc[T] += min(sc[B] * (.55 if not roundup else .15), 13 if techco == 2 else 7)
        if not roundup:
            sc[B] *= .82
    return sc


_HEAD = {"title", "headline", "subject", "news_title", "article_title", "heading"}
_BODY = {"text", "article", "news", "story", "body", "content", "description", "summary",
         "snippet", "document", "passage", "lead", "abstract", "news_text", "article_text",
         "full_text", "fulltext", "context", "sentence", "input", "message"}
_IGNORE = {"id", "label", "category", "class", "answer", "question", "options",
           "date", "time", "timestamp", "index", "url", "link", "guid"}


def _parts(obj, ishead=False):
    if isinstance(obj, str):
        return [(obj.strip(), ishead)] if obj.strip() else []
    if isinstance(obj, dict):
        keys = [(k, str(k).lower().strip().replace(" ", "_")) for k in obj]
        relevant = [(k, n) for k, n in keys if n in _BODY or n in _HEAD]
        res = []
        for k, n in relevant or keys:
            if n not in _IGNORE:
                res.extend(_parts(obj[k], ishead or n in _HEAD))
        return res
    if isinstance(obj, (tuple, list)):
        return [p for x in obj for p in _parts(x, ishead)]
    return []


def predict(state) -> dict:
    parts = _parts(state)
    scores = {W: 2.2, B: .35, S: 0., T: .2}
    seen = set()
    for s, head in sorted(parts, key=lambda x: not x[1]):
        if s in seen:
            continue
        seen.add(s)
        v = _weight(s, head)
        for c in _CATS:
            scores[c] += v[c] * (1.48 if head else 1)
    return {"answer": max(_CATS, key=scores.get)}