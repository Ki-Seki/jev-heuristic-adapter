import re
import unicodedata
from collections import defaultdict


_CATEGORIES = ("world", "business", "sci_tech", "sports")

_VOCABULARY = {
    "sports": (
        (8, """super bowl|world series|stanley cup|wimbledon|uefa|fifa|nba|wnba|nfl|nhl|ncaa|mlb|pga tour|lpga|nascar|formula one/formula 1|champions league|premier league|la liga|serie a|bundesliga|six nations|davis cup|ryder cup|tour de france|us open|australian open|french open|olympics/olympic games|paralympics|world cup|copa america|major league baseball|minor league baseball|college basketball|college football|test cricket|ashes series|rugby league|rugby union|grand slam|sports illustrated"""),
        (6, """football/soccer|basketball|baseball|ice hockey/hockey|cricket|rugby|tennis|golf|volleyball|softball|lacrosse|wrestling|gymnastics|figure skating|motorsport/motor racing|boxing|speed skating|marathon|decathlon|athletics|quarterback|wide receiver|running back|linebacker|touchdown/touchdowns|field goal/field goals|home run/home runs|grand prix|innings|wicket/wickets|bullpen|starting pitcher|fastball|no hitter|free throw/free throws|three pointer/three pointers|hat trick|penalty shootout|extra innings|pole position|tiebreak/tiebreaker|match point|tee shot|birdie/birdies/eagle putt|batsman/batsmen|batting average|box score|all star game|trade deadline|free agent/free agency|doping/anti doping|transfer window|gold medal/silver medal/bronze medal|yankees|red sox|white sox|mets|dodgers|orioles|cubs|astros|padres|angels|oakland athletics|cleveland indians|blue jays|phillies|marlins|braves|cardinals|seattle mariners|pittsburgh pirates|texas rangers|san francisco giants|new york giants|new york jets|seattle seahawks|packers|cowboys|patriots|raiders|vikings|broncos|buccaneers|bengals|steelers|dolphins|eagles|chargers|saints|49ers|redskins|commanders|titans|bills|atlanta falcons|lakers|celtics|knicks|nets|timberwolves|mavericks|76ers|trail blazers|golden state warriors|san antonio spurs|miami heat|houston rockets|detroit pistons|toronto raptors|chicago bulls|red wings|maple leafs|canadiens|chelsea|arsenal|manchester united/man united/man utd|manchester city/man city|real madrid|barcelona fc/fc barcelona|bayern munich|juventus|ac milan|inter milan|liverpool fc|tottenham|everton|newcastle united|celtic fc|tiger woods|roger federer|rafael nadal|andy roddick|serena williams|venus williams|maria sharapova|lance armstrong|michael schumacher|kobe bryant|shaquille o neal|lebron james|david beckham|michael phelps|barry bonds|babe ruth"""),
        (4.2, """athlete/athletes|coach/coaches/coaching|goalkeeper/keeper|midfielder/midfielders|fullback/fullbacks|striker/strikers|pitcher/pitchers|catcher/catchers|shortstop|outfielder|goaltender|rookie/rookies|rebounding/rebounds|playoffs/playoff/postseason|preseason|regular season|semifinal/semifinals/semi final/semi finals|quarterfinal/quarterfinals/quarter final/quarter finals|final round|first round pick|draft pick|scored/scoring|scoreless|shutout/shut out|inning|batting|dribbled/dribbling|sacked quarterback|defending champion|title defense|league title|season opener|home opener|tournament/tournaments|scoreboard|stoppage time|yellow card/red card|home game/away game|training camp|locker room|disabled list/injured reserve|sideline/sidelined|hamstring injury|club captain|player of the year|winning streak/losing streak|season high/career high|reigning champion|playoff berth|relegation/promotion playoff|podium finish|tee off|touchline|red devils|new york yankees|trojans|sooners|wolverines|buckeyes|huskies|blue devils"""),
        (2.1, """team/teams|player/players|match/matches|game/games|league/leagues|goals/goal|win/wins/won|beat/beats/defeated|victory/victories|opener|season/seasons|stadium/arena|captain|standings|club/clubs|rival/rivals|referee/umpire|draw/drew|squad|halftime/half time|finals|championship/championships/champion/champions|seeded/top seed|overtime|second half/first half|holder|relay|retired/retirement|bronze/silver medalist|sports|foul/fouls|shorthanded"""),
    ),
    "sci_tech": (
        (8, """artificial intelligence|machine learning|quantum computing|quantum computer|genetic engineering|gene therapy|genome sequencing|stem cell/stem cells/stem cell research|climate model/climate models|mars rover|space shuttle|international space station/iss|space telescope|hubble telescope|james webb|satellite launch|lunar mission|spacecraft/space probe|exoplanets/exoplanet|particle accelerator|gravitational waves|black hole/black holes|clinical trials/clinical trial|randomized trial|peer reviewed|double blind|software update|operating system/operating systems|web browser|search engine/search engines|open source|source code|security patch|cybersecurity/cyber security|antivirus/anti virus|computer virus/computer worm|data breach|ransomware|smartphone/smartphones|video game/video games/videogame/videogames|gaming console/game console|playstation/playstation 2/playstation 3/ps2/ps3/psp|xbox/xbox live|game boy|iphone/ipad/ipod|windows xp/windows vista/windows 11|wi fi/wifi|fiber optic/fibre optic|semiconductor/semiconductors|microprocessor/microprocessors|graphics processor|cloud computing|internet explorer|world wide web|broadband internet|mobile phone/mobile phones|cell phone/cell phones/cellphone/cellphones|wireless network/wireless networks|voice over ip/voip|digital camera/digital cameras|digital music player|genetically modified|radio frequency identification/rfid|virtual reality|augmented reality|social media platform|instant messaging"""),
        (5.5, """software|hardware|internet|computing|computer/computers|technology/technologies|telecom/telecommunications|broadband|wireless|bluetooth|electronics|chipmaker/chipmakers|chipset/chipsets|processor/processors|microchip/microchips|graphics card|laptop/laptops/notebook pc|personal computer/desktop pc|tablet computer|web site/web sites/website/websites|online search|webmail|email/e mail|browser/browsers|malware|spyware|phishing|hackers/hacker/hacking|cyberattack/cyber attack|encryption|download/downloads/downloading|mp3 player|application software|database/databases|video streaming|robot/robots/robotics|android|linux|firefox/mozilla|mac os/macos|nasa|spacex|space station|astronaut/astronauts|astronomy/astronomers/astronomer|telescope/telescopes|planet/planets|orbital/orbiting|rover|asteroid/asteroids|comet/comets|galaxy/galaxies|cosmic|supernova|fossil/fossils|dinosaurs/dinosaur|archaeologists/archaeology|paleontologists|physicist/physicists|neuroscience|genetics/genetic|genome/genomes|genomics|dna|rna|protein/proteins|molecule/molecules|biotechnology/biotech|nanotechnology|vaccine/vaccines|experimental drug|drug trial|medical journal|new treatment|cancer research|renewable energy technology|electric vehicle battery"""),
        (3.4, """science/scientific|scientist/scientists|researcher/researchers|research/researching|study finds/studies find/study suggests/study shows/new study|laboratory/laboratories|experiment/experiments|genetically|therapy/therapies|biologists/biology|data center/data centre|server/servers|workstation/workstations|online|website launch|digital|silicon|chips/chip|handset/handsets|battery/batteries|networking|telecommunications equipment|tech/hi tech/high tech|innovation/innovations|app/apps|programmers/programmer|3g/4g/5g|codec|messaging|spam|e commerce/ecommerce|domain name/domain names|copyright infringement|patent infringement|robotic|satellite/satellites|orbit|space tourism|launch pad|climate change/global warming|simulation/simulations|discovery|bacteria/bacterium|cancer|immune system|antibiotic/antibiotics|antibody/antibodies|virus/viruses|mammal/mammals|vulnerability/vulnerabilities|test results|data privacy"""),
        (1.8, """medical|health|patient/patients|drug/drugs|engineer/engineers/engineering|developers/developer|upgrade/upgraded/upgrades|version/versions|device/devices|platform/platforms|network/networks|users/user|data|privacy|patent/patents|prototype|released/release|unveils/unveiled|launch/launches/launched|discovered|lab|findings|species|carbon dioxide|emissions|smart|electric car/electric cars|gaming|cyber|bluetooth enabled|mobile|console|pc/pcs|television|screens/screen|display|startup/start up"""),
    ),
    "business": (
        (8, """stock market/stock markets|wall street|dow jones/dow industrials/dow jones industrial average|nasdaq composite|s p 500/s and p 500/standard and poor s 500|ftse 100|nikkei 225|hang seng|euro stoxx|stock exchange|share price/share prices|quarterly profit|quarterly earnings|quarterly loss|third quarter earnings/second quarter earnings/first quarter earnings/fourth quarter earnings|earnings forecast/earnings guidance/earnings report|profit warning|net income/net profit/net loss|operating profit|fiscal quarter|initial public offering/ipo|interest rate/interest rates|rate hike/rate cut|federal reserve/fed reserve|central bank|consumer price index|gross domestic product/gdp|trade deficit/trade surplus|crude oil|oil price/oil prices|oil futures|brent crude|saudi aramco|oil production|price of oil|barrel of oil|natural gas prices|gold futures|commodity/commodities|foreign exchange|bond market|takeover bid|hostile takeover|merger talks|buyout|chapter 11|bankruptcy|retail sales|consumer spending|consumer confidence|labor market/labour market|jobless claims|minimum wage|balance sheet|annualized rate"""),
        (5.4, """shares/stock/stocks/equities|shareholders/stockholders|earnings|profits/profit/profitable|revenues/revenue|dividend/dividends|investor/investors|brokerage/stockbroker|trading/traded|acquisition/acquisitions|merger/mergers|takeover|buyback|private equity|investment bank|mutual fund/mutual funds|hedge fund/hedge funds|venture capital|securities|market capitalization/market cap|nasdaq|dow|ftse|nikkei|economic growth|economy/economies|recession|inflation|deflation|unemployment|payrolls|layoffs/lay offs|job cuts|restructuring|bankrupt|insolvent/insolvency|credit rating|mortgage/mortgages|home sales/housing market|exports/exporters/exports rose|imports/importers|tariff/tariffs|free trade/trade agreement/trade pact|world trade organization/wto|trade talks/trade dispute|free trade agreement|opec|natural gas|oilfield/oil fields|refinery/refineries|barrel/barrels|oil output|futures|exchange rate|currency/currencies|treasury yields|bonds/bond yields|supply chain|airline/airlines/airways|airline industry|airline fares|boeing/airbus|retailer/retailers/retailing|supermarket/supermarkets|department store/department stores|wal mart/walmart|k mart/kmart|sears|costco|kroger|home depot|tesco|carrefour|mcdonald s/mcdonalds|starbucks|general motors|ford motor|toyota|volkswagen|daimlerchrysler|chrysler|honda|exxon/exxonmobil|chevron|halliburton|royal dutch shell|goldman sachs|morgan stanley|bank of america|jpmorgan/jp morgan|citigroup|lehman brothers|berkshire hathaway|fannie mae/freddie mac|wells fargo|procter and gamble|coca cola/pepsico|fiscal year|same store sales|stock index|corporate bonds|pension fund"""),
        (3.3, """market/markets|deal/deals|investment/investments|commerce|industry/industrial|manufacturer/manufacturing|corporate/corporation|company/companies|business/businesses|financial/finances|bank/banks/banking|lender/lenders|sales/sold/selling|retail|price/prices|quarter/quarterly|ceo/chief executive|chief financial officer/cfo|chief operating officer|board of directors|forecast/forecasts|outlook|capital|percent/percentage|dollar/dollars|euro/euros|yen|yuan|sterling|cut jobs/cutting jobs|operating costs|economic/economics|shop/shopping|oil|gasoline|gallon/gallons|tax rate|automaker/automakers/carmaker/carmakers|insurance/insurer/insurers|union workers|collective bargaining|labor dispute/labour dispute|bankruptcy protection|purchase price|cash offer|analysts/analyst|recall/recalls|consumer/consumers"""),
        (1.6, """product/products|rose/rise/rises|fell/falls|rally/rallied|slump/slumped|buy/bought/buys|offer/offers|bid/bids|stake|owners/owner|contract/contracts|jobs|employment|fund/funds|budget|commercial|management|executive/executives|tax/taxes|wages/salary/salaries|customer/customers|debt/debts|loan/loans|asset/assets|loss/losses|gains/gain|turnover|subsidiary|acquire/acquired/acquires|benefits|pension/pensions|spending|brands/brand"""),
    ),
    "world": (
        (8, """white house|united nations|un security council/security council|secretary general|prime minister/prime ministers|foreign minister/foreign ministry|head of state|general election/parliamentary election/presidential election|electoral college|polling station/polling stations|ballot boxes/ballot box|voter turnout|election campaign|military coup|peace talks/peace negotiations|ceasefire/cease fire|civil war|war crimes|war crime tribunal|invasion of iraq/iraq war|middle east peace|west bank/gaza strip|suicide bombing/suicide bomber|car bomb/truck bomb|bomb blast|rocket attack/missile attack|air strike/air strikes/airstrike/airstrikes|terrorist attack|hostage crisis|insurgent attack|mass shooting|mass grave|death toll|state of emergency|natural disaster|hurricane/hurricanes|typhoon/typhoons|earthquake/earthquakes|tsunami/tsunamis|plane crash/air crash|train crash/train derailment|volcanic eruption|flash floods|wildfire/wildfires|school shooting|human rights|death penalty|manslaughter|human trafficking|police shooting|court martial|international criminal court"""),
        (5.5, """president/presidential|parliament/parliamentary|congress/congressional|senate/senator/senators|governor/governors|mayor/mayoral|legislature/lawmakers|legislation|election/elections|electoral|voters/voter|ballot/ballots|referendum|democrats/democrat/democratic party|republicans/republican party|labour party/labor party|opposition party|government/governments|cabinet|ministry|politics/political|diplomat/diplomats/diplomacy/diplomatic|ambassador/ambassadors|embassy/embassies|bilateral talks|border dispute|peacekeepers/peacekeeping|sanctions|military|soldier/soldiers/troops|army|navy|armed forces|pentagon|nato|occupation forces|insurgent/insurgents/insurgency|militant/militants|guerrilla/guerrillas|rebels/rebellion|abducted/abduction|kidnapped/kidnapping|hostage/hostages|bomb/bombs/bombing/bombings|terrorism/terrorist/terrorists|al qaeda/al qaida|taliban|hamas|hezbollah|israeli palestinian|palestinian authority|yasser arafat|saddam hussein|osama bin laden|vladimir putin|george w bush/george bush|john kerry|tony blair|ariel sharon|kofi annan|north korea|darfur|kashmir|chechnya|abu ghraib|genocide|refugee/refugees|warfare|weapon/weapons|nuclear weapons|arms control|detonated/explosion/explosions|gunmen/gunman|police/cops|murder/murders/murdered|homicide|robbery/robberies|prosecutor/prosecutors|arrest/arrested/arrests|convicted/conviction|prison/prisoner/prisoners|jail/jailed|gunfire|firefighters|flood/floods/flooding|evacuation/evacuated|rescue workers|aid workers|landslide/mudslide|missing persons|drought/famine|protests/protesters/protestor/protestors|asylum seekers|immigration|vandalism|riot/riots|drug trafficking|terror alert|outbreak/epidemic/pandemic"""),
        (3.3, """war/wars|conflict/conflicts|border/borders|armed|crime/crimes|accused/accusations|verdict|sentence/sentenced|criminal|sued/lawsuit/lawsuits|court/courts|judge/judges|prosecution|investigation/investigators|killed/killings/killing|wounded/injured|bodies|dead/deaths|victims/victim|clashes/clash|violence/violent|shooting/shot|attack/attacks/attacked|fighters|battles/battle|disaster|storm/storms|casualties|tragedy|wreckage|relief efforts|reconstruction|peace|security forces|rally/protest|demonstration/demonstrators|voted/vote/votes|minister/ministers|campaign/campaigns|coalition|candidate/candidates|authorities/officials|reform/reforms|treaty|constitution/constitutional|resigns/resigned/resignation|corruption|scandal|israel/israeli|palestinian/palestinians|iraq/iraqi|afghanistan/afghan|iran/iranian|pakistan/pakistani|korean peninsula|baghdad|gaza|fallujah|kabul|beslan|sudan|shia/shiite/sunni|separatist/separatists|activists/activist|aid convoy|hiv outbreak|bird flu outbreak|bird flu cases|public health emergency"""),
        (1.6, """nation/nations|national|international|country/countries|citizens|unrest|region|ruling|law/laws|power|rights|policy/policies|summit|moratorium|alert|banned/ban|strike/strikes|crash|rescue|missing|fired|charged|disputed|ruling party|emergency|victory|official|london|moscow|geneva|washington|courtroom|cleric|pope/vatican|church|union|federal|state"""),
    ),
}


_TECH_NAMES = """
microsoft|google|alphabet inc|international business machines/ibm|intel|advanced micro devices/amd|nvidia|qualcomm|cisco/cisco systems|juniper networks|broadcom|texas instruments|micron technology|infineon|analog devices|tsmc/taiwan semiconductor|applied materials|asml|arm holdings|hp/hewlett packard|dell computer/dell technologies/dell inc|apple computer/apple inc|sun microsystems/sun micro|oracle corp/oracle corporation|sap ag/sap se|peoplesoft/people soft|siebel systems|adobe/adobe systems|autodesk|intuit|salesforce|symantec|mcafee|kaspersky|red hat|suse|novell|vmware|citrix|veritas software|check point software|sybase|computer associates|bea systems|borland|macromedia|realnetworks|akamai|nortel|lucent|alcatel|motorola|nokia|ericsson|blackberry/research in motion/rim ltd|samsung electronics/samsung|lg electronics|sony/sony ericsson/sony computer entertainment|toshiba|panasonic/matsushita|fujitsu|nec corp|lenovo|acer inc|asus|logitech|palmone/palm pilot/palmsource|seagate|western digital|lexmark|canon inc|epson|xerox|kodak|nintendo|electronic arts/ea sports|activision/activision blizzard|ubisoft|take two interactive|square enix|sega|epic games|valve software|yahoo|lycos|ask jeeves|america online/aol|netscape|ebay/e bay|paypal|amazon com|netflix|facebook/meta platforms|instagram|whatsapp|twitter|tiktok|snapchat|baidu|alibaba|tencent|sina com|openai|huawei|zte|at and t/att wireless|verizon|sprint nextel/nextel|t mobile|vodafone|bell south/bellsouth|cingular|sbc communications|worldcom|mci|bt group/british telecom|deutsche telekom|france telecom|telecom italia|telefonica|china mobile|ntt docomo|sk telecom|telstra|comcast|starlink|level 3 communications|vonnage/vonage
"""

_TITLE_KEYS = ("headline", "title", "newsheadline", "articletitle", "newstitle", "subject")
_LEAD_KEYS = ("description", "summary", "subtitle", "subheading", "abstract", "lead", "blurb", "snippet")
_BODY_KEYS = (
    "text", "articletext", "newstext", "inputtext", "body", "articlebody", "content",
    "article", "newsarticle", "news", "story", "passage", "sentence", "document",
    "input", "payload", "data", "example", "record", "features", "item", "state",
)
_SKIP_KEYS = {
    "id", "label", "labels", "answer", "answers", "class", "classindex", "category",
    "categories", "topic", "target", "question", "instructions", "source", "author",
    "date", "timestamp", "url", "link", "metadata", "options", "choices",
}
_ENTITIES = {
    "amp": "&", "quot": '"', "apos": "'", "lt": "<", "gt": ">", "nbsp": " ",
    "rsquo": "'", "lsquo": "'", "rdquo": '"', "ldquo": '"', "mdash": "—",
    "ndash": "–", "hellip": "...", "pound": "£", "euro": "€",
}


def _key(value):
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _fields(value, depth=0):
    if depth > 12:
        return "", ""
    if isinstance(value, str):
        return "", value
    if isinstance(value, (tuple, list)):
        heads = []
        bodies = []
        for element in value:
            head, body = _fields(element, depth + 1)
            if head:
                heads.append(head)
            if body:
                bodies.append(body)
        return "\n".join(heads), "\n".join(bodies)
    if not isinstance(value, dict):
        return "", ""
    fields = {_key(key): item for key, item in value.items() if isinstance(key, str)}
    heads = []
    bodies = []
    for key in _TITLE_KEYS + _LEAD_KEYS + _BODY_KEYS:
        if key not in fields:
            continue
        head, body = _fields(fields[key], depth + 1)
        if head and head not in heads:
            heads.append(head)
        if body and key in _TITLE_KEYS and body not in heads:
            heads.append(body)
        elif body and key not in _TITLE_KEYS and body not in bodies:
            bodies.append(body)
    if not heads and not bodies:
        for key, item in fields.items():
            if key not in _SKIP_KEYS:
                head, body = _fields(item, depth + 1)
                if head:
                    heads.append(head)
                if body:
                    bodies.append(body)
    return "\n".join(heads), "\n".join(bodies)


def _decode_entity(match):
    token = match.group(1)
    if token.startswith("#"):
        number = token[1:]
        try:
            code = int(number[1:], 16) if number.lower().startswith("x") else int(number)
            if 0 <= code <= 0x10ffff:
                return chr(code)
        except ValueError:
            pass
        return " "
    return _ENTITIES.get(token.lower(), " ")


def _clean(text):
    for _ in range(2):
        text = re.sub(r"&(#(?:[0-9]{1,8}|[xX][0-9a-fA-F]{1,7})|[a-zA-Z]{2,12});", _decode_entity, text)
    text = re.sub(r"(?<!\w)#(39|34|36|160);", lambda m: chr(int(m.group(1))), text)
    text = re.sub(r"<(?:br|/p|/div)\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</?(?:a|b|i|u|p|div|span|strong|em|h[1-6]|font)\b[^<>]*>", " ", text, flags=re.I)
    text = text.replace("\\n", "\n").replace("\\", " ")
    return text.strip()


def _words(text):
    text = unicodedata.normalize("NFKD", text.casefold())
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.replace("’", "'").replace("&", " and ")
    text = re.sub(r"\b(?:[a-z]\.){2,}(?:[a-z]\b)?", lambda m: m.group().replace(".", ""), text)
    text = re.sub(r"(?<=\w)'s\b", "", text)
    return re.findall(r"[a-z0-9]+", text)


def _compile_groups(source):
    return tuple(
        tuple(dict.fromkeys(" ".join(_words(alias)) for alias in group.split("/") if alias.strip()))
        for group in source.split("|") if group.strip()
    )


_TERMS = {}
_MAX_PHRASE = 1
for _category, _bands in _VOCABULARY.items():
    _table = {}
    for _weight, _source in _bands:
        for _group in _compile_groups(_source):
            for _term in _group:
                if _term and (_term not in _table or _table[_term][0] < _weight):
                    _table[_term] = (_weight, _group[0])
                    _MAX_PHRASE = max(_MAX_PHRASE, len(_term.split()))
    _TERMS[_category] = _table
_TECH_GROUPS = _compile_groups(_TECH_NAMES)
for _group in _TECH_GROUPS:
    for _term in _group:
        _MAX_PHRASE = max(_MAX_PHRASE, len(_term.split()))

_WIRE = re.compile(
    r"\s+\((?:AP|AFP|Reuters|UPI|Bloomberg|Canadian Press|The Associated Press|"
    r"washingtonpost\.com|PC World|ZDNet|InfoWorld|TechWeb|SPACE\.com|Reuters Health)\)"
    r"(?=\s|$)", re.I,
)
_RESULT = re.compile(r"(?<![\d.,])(\d{1,3})\s*[-–—:]\s*(\d{1,3})(?![\d.,])")
_MONEY = re.compile(
    r"(?:[$€£]\s*\d|\b\d+(?:[.,]\d+)?\s*(?:(?:us|canadian|australian)\s+)?"
    r"(?:dollars|euros|pounds sterling|yen)\b|\b\d+(?:\.\d+)?\s*(?:million|billion|trillion)\s+"
    r"(?:dollars|euros|yen)\b)", re.I,
)
_MARKET_ACTION = re.compile(
    r"\b(?:stocks|shares|equities|dow|nasdaq|nikkei|ftse|markets|futures|"
    r"dollar|yen|euro|bonds|wall street)\b.{0,45}\b(?:gain\w*|jump\w*|climb\w*|"
    r"slid\w*|drop\w*|dip\w*|sink\w*|slip\w*|slump\w*|surg\w*|ris\w*|rose|"
    r"fell|fall\w*|down|higher|lower|steady|flat|rebound\w*|rall\w*|inch\w*|"
    r"clos\w*|open\w*|lost|los\w*|weak\w*|strengthen\w*)\b"
)
_MATCH_ACTION = re.compile(
    r"\b(?:beats?|beat\w*|defeat\w*|blanks?|sweeps?|edges?|tops?|"
    r"rout\w*|outlast\w*|upset\w*|overpower\w*|ties?|"
    r"draws?|held|eliminat\w*|clinch\w*|thrash\w*|downs?)\b"
)
_SPORT_DETAIL = re.compile(
    r"\b(?:\d+\s+(?:rebounds|assists|innings|touchdowns|catches|goals|saves|"
    r"strikeouts|wickets|birdies|yards)|(?:scored|added|had|with)\s+\d+\s+points|"
    r"set\s+scores|three\s+sets|straight\s+sets|second\s+leg|on\s+aggregate|"
    r"\d+\s+under\s+par|box\s+score|bottom\s+of\s+the\s+ninth|"
    r"advanc\w*\s+to\s+the\s+(?:final|semifinals|quarterfinals|second round))\b"
)
_CORPORATE_EVENT = re.compile(
    r"\b(?:earnings|revenues?|sales|profits?|losses|shares|stocks?|quarter(?:ly)?|"
    r"financial results|antitrust|lawsuits?|sued|sues|suing|settle\w*|patent\w*|"
    r"court|fined|acqui\w*|merg\w*|buys?|bought|buying|takeover|offer\w*|"
    r"bids?|deal|chief executive|ceo|ipo|bankrupt\w*|"
    r"restructur\w*|job cuts|layoffs|hiring|agreement|invest\w*|partners?|"
    r"announc\w*|releas\w*|unveil\w*|introduc\w*|launch\w*|ship\w*|"
    r"develop\w*|upgrad\w*|test\w*|recall\w*|service|network)\b"
)
_RESEARCH_EVENT = re.compile(
    r"\b(?:research(?:ers?)?|scientists?|stud(?:y|ies)|clinical|"
    r"trial|experiment\w*|journal|discov\w*|laborator\w*|measur\w*|"
    r"breakthrough|evidence|findings|published|develop\w*)\b"
)
_PUBLIC_EVENT = re.compile(
    r"\b(?:killed|dead|death toll|died|arrest\w*|kidnap\w*|hostages?|"
    r"murder\w*|shooting|gunm[ae]n|bomb\w*|explosion|crash\w*|"
    r"evacuat\w*|hurricane|typhoon|flood\w*|earthquake|tsunami|"
    r"ceasefire|cease fire|troops|militants?|referendum|elections?|"
    r"protest\w*|riot\w*|siege|coup|wildfires?)\b"
)
_OUTBREAK = re.compile(
    r"\b(?:outbreak|epidemic|pandemic|infected people|confirmed cases|"
    r"quarantine|avian flu|bird flu|bird flu cases|ebola|sars|"
    r"world health organization|swine flu|cholera)\b"
)
_CARE_EVENT = re.compile(
    r"\b(?:vaccine\w*|drug\w*|treatment\w*|medicin\w*|cells?|gene\w*|"
    r"biolog\w*|molecular|clinical|cancer|patients?|surgery|infection\w*|"
    r"antibod\w*|virus\w*|bacteri\w*)\b"
)
_FINANCIAL_FOCUS = re.compile(
    r"\b(?:stock markets?|wall street|dow jones|s p 500|nasdaq composite|"
    r"ftse 100|nikkei 225|hang seng|market wrap|market report|bond markets?|"
    r"oil prices|crude oil|oil futures|treasur(?:y|ies)|federal reserve)\b"
)


def _ngrams(words):
    return {
        " ".join(words[start:start + length])
        for length in range(1, min(_MAX_PHRASE, len(words)) + 1)
        for start in range(len(words) - length + 1)
    }


def _regions(title, body):
    if not title and body:
        wire = _WIRE.search(body)
        if wire and 1 <= len(_words(body[:wire.start()])) <= 31:
            title = body[:wire.start()]
            body = body[wire.end():].lstrip(" -—–:\n")
        else:
            pieces = body.split("\n", 1)
            if len(pieces) == 2 and 2 <= len(_words(pieces[0])) <= 25 and pieces[1].strip():
                title, body = pieces
    headline = _words(title)[:80]
    body_words = _words(body)[:2000]
    return title, body, headline, body_words


def _weigh(table, terms, high, lead):
    groups = defaultdict(float)
    salient = 0.0
    strong = 0
    for term in table.keys() & terms:
        weight, group = table[term]
        if term in high:
            multiplier = 1.47
            salient = max(salient, weight)
        elif term in lead:
            multiplier = 1.12
            salient = max(salient, weight * 0.78)
        else:
            multiplier = 0.78
        groups[group] = max(groups[group], weight * multiplier)
    ranked = sorted(groups.values(), reverse=True)
    strong = sum(value >= 4.1 for value in ranked)
    discounts = (1, 0.94, 0.79, 0.66, 0.55, 0.46, 0.38, 0.31, 0.26, 0.21, 0.17, 0.14)
    score = sum(value * discount for value, discount in zip(ranked, discounts))
    score += min(2.5, sum(ranked[len(discounts):]) * 0.10)
    return score, salient, strong


def _tech_entities(raw, all_terms, high, lead):
    levels = []
    for group in _TECH_GROUPS:
        for region, value in ((high, 3), (lead, 2), (all_terms, 1)):
            if any(term in region for term in group):
                levels.append(value)
                break
    ambiguous = (
        ("apple", r"\bApple\b", r"\b(?:orchards?|fruit|growers?|cider)\b"),
        ("amazon", r"\bAmazon\b", r"\b(?:rainforest|rain forest|river basin|amazon river|deforestation|jungle)\b"),
        ("oracle", r"\bOracle\b", r"\b(?:delphi|prophecy)\b"),
        ("dell", r"\bDell\b", r"\b(?:dell curry|northean dell)\b"),
        ("gateway", r"\bGateway\b", r"\b(?:gateway to|gateway city|gateway arch)\b"),
        ("sap", r"\bSAP\b", r"\b(?:maple|tree)\b"),
        ("sprint", r"\bSprint\b", r"\b(?:meters|metres|swimming|sprint cup|olympic|relay)\b"),
        ("arm", r"\bARM\b", r"\b(?:arms control)\b"),
        ("sun", r"\bSun\b", r"\b(?:the sun|sun shines|sun newspaper)\b"),
    )
    normalized = " ".join(_words(raw))
    for term, spelling, exclusion in ambiguous:
        if term not in all_terms or not re.search(spelling, raw) or re.search(exclusion, normalized):
            continue
        if term in {"sun", "sprint", "arm", "gateway"}:
            if not re.search(r"\b(?:microsystems|computer\w*|software|hardware|"
                             r"telecom\w*|wireless|chip\w*|pc|pcs|mobile|"
                             r"nextel|servers?|network|systems|processor\w*|corp)\b", normalized):
                continue
        levels.append(3 if term in high else 2 if term in lead else 1)
    return (max(levels) if levels else 0), len(levels)


def _contains(terms, alternatives):
    return any(term in terms for term in alternatives.split("|"))


def predict(state) -> dict:
    title, body = _fields(state)
    title, body, headline, words = _regions(_clean(title), _clean(body))
    if not headline and not words:
        return {"answer": "world"}

    first = headline if headline else words[:13]
    lead_words = words[:36]
    high = _ngrams(first)
    lead = high | _ngrams(lead_words)
    terms = lead | _ngrams(words)
    front = " ".join(first)
    beginning = " ".join(headline + lead_words)
    normalized = " ".join(headline + words)
    raw = (title + "\n" + body).strip()
    early_raw = title + "\n" + " ".join(body.split()[:40])
    scores = {}
    salience = {}
    anchors = {}
    for category in _CATEGORIES:
        scores[category], salience[category], anchors[category] = _weigh(
            _TERMS[category], terms, high, lead
        )
        scores[category] += 0.34 * salience[category]

    market_headline = bool(_FINANCIAL_FOCUS.search(front))
    market_action = bool(_MARKET_ACTION.search(front))
    if market_action or market_headline:
        scores["business"] += 5.0 if market_action else 3.3
    elif _MARKET_ACTION.search(beginning):
        scores["business"] += 2.5
    if _MONEY.search(early_raw):
        if scores["business"] >= 5 or _CORPORATE_EVENT.search(beginning):
            scores["business"] += 2.5
    if _contains(lead, "stock market|earnings|profits|profit|net income|revenues|revenue|quarterly|shares|dividend"):
        if _contains(lead, "company|quarter|quarterly|analysts|forecast|investors|sales|rose|fell|dollars"):
            scores["business"] += 2.5
    if _contains(lead, "oil|crude oil|gasoline|opec|refinery|natural gas"):
        if _contains(lead, "price|prices|futures|barrels|output|production|exports|supply|demand"):
            scores["business"] += 4.4

    entity_level, entity_count = _tech_entities(raw, terms, high, lead)
    if entity_level:
        scores["sci_tech"] += (0, 4.6, 8.6, 12.2)[entity_level]
        scores["sci_tech"] += min(4, (entity_count - 1) * 1.65)
        if _CORPORATE_EVENT.search(beginning if entity_level >= 2 else normalized):
            scores["sci_tech"] += (0, 1.9, 5.0, 8.0)[entity_level]
            # A report on a technology company is technology news even when
            # the event is a financial filing, takeover, or civil lawsuit.
            if entity_level >= 2 and not market_headline and not market_action:
                bias = 6.2 if entity_level == 3 else 3.4
                scores["sci_tech"] += bias
                scores["business"] *= 0.69 if entity_level == 3 else 0.85

    tech_product = _contains(
        lead, "software|hardware|internet|telecom|telecommunications|wireless|broadband|"
        "smartphone|semiconductor|operating system|computer|web browser|video game|"
        "smartphones|computers|chipmaker|mobile phone|search engine"
    )
    if tech_product and _CORPORATE_EVENT.search(beginning):
        if not market_headline and not market_action:
            scores["sci_tech"] += 3.7
        if salience["sci_tech"] >= 5.5 and _contains(
            high, "software|internet|telecom|wireless|chipmaker|computer|computers|"
            "semiconductor|gaming|handset|electronics|technology"
        ):
            scores["sci_tech"] += 3.2
            scores["business"] *= 0.88

    research = bool(_RESEARCH_EVENT.search(beginning))
    medical = bool(_CARE_EVENT.search(beginning))
    if research and (medical or salience["sci_tech"] >= 3.4):
        scores["sci_tech"] += 6.1
        if _RESEARCH_EVENT.search(front):
            scores["sci_tech"] += 2.8
    if _OUTBREAK.search(beginning):
        if not research or _contains(high, "outbreak|quarantine|death toll"):
            scores["world"] += 4.3
        if not tech_product and not research and not _contains(high, "vaccine|vaccines|new treatment"):
            scores["sci_tech"] *= 0.77

    scoreline = any(
        0 <= int(match.group(1)) <= 199 and 0 <= int(match.group(2)) <= 199
        for match in _RESULT.finditer(early_raw)
    )
    match_action = bool(_MATCH_ACTION.search(beginning))
    procedural_vote = _contains(
        high, "vote|votes|voted|senate|parliament|lawmakers|congress|verdict|ruling|court|referendum"
    )
    if scoreline and not procedural_vote:
        if match_action or salience["sports"] >= 2.1:
            scores["sports"] += 9.3
        elif salience["world"] < 4 and salience["business"] < 4 and salience["sci_tech"] < 4:
            if not re.search(r"\b(?:aged|ages|am|pm|degrees|percent|poll|case)\b", beginning):
                scores["sports"] += 3.5
    if _SPORT_DETAIL.search(normalized[:650]):
        scores["sports"] += 7.0
    if match_action and anchors["sports"] >= 1:
        scores["sports"] += 3.1
    if _contains(lead, "player|players|match|matches|game|games|team|teams|coach|coaches"):
        if _contains(lead, "season|league|standings|scored|goals|streak|championship|points|rival|win|won|draw|final"):
            scores["sports"] += 3.5
    if _contains(high, "video game|video games|xbox|playstation|gaming console|game console"):
        scores["sports"] *= 0.63

    if _PUBLIC_EVENT.search(front):
        scores["world"] += 4.0
        if _contains(high, "plane crash|air crash|train crash|death toll|hostage|hostages|"
                     "suicide bombing|mass shooting|hurricane|earthquake|typhoon|wildfire"):
            scores["world"] += 6.0
    elif _PUBLIC_EVENT.search(beginning) and anchors["world"] >= 2:
        scores["world"] += 2.1
    if _contains(high, "president|prime minister|congress|government|senate|minister|parliament"):
        if _contains(lead, "election|elections|voters|party|campaign|legislation|bill|treaty|opposition|cabinet"):
            scores["world"] += 3.8
    if _contains(lead, "president|vice president") and _contains(
        lead, "chief executive|ceo|executive|company|corporation|board of directors"
    ) and not _contains(lead, "white house|prime minister|elections|election|senate|government"):
        scores["world"] *= 0.69

    if scores["sports"] > 0 and anchors["sports"] == 0 and not scoreline:
        if not _SPORT_DETAIL.search(beginning):
            scores["sports"] *= 0.68
    if anchors["business"] == 0 and not _MONEY.search(early_raw):
        scores["business"] *= 0.79
    if anchors["sci_tech"] == 0 and not entity_level and not research:
        scores["sci_tech"] *= 0.75

    best = max(_CATEGORIES, key=lambda category: (scores[category], salience[category]))
    if scores[best] < 2.5:
        best = "world"
    return {"answer": best}