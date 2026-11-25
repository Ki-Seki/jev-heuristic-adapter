import re
import unicodedata


def _compile_rules(rules):
    return [
        (weight, re.compile(r"(?<!\w)(?:" + pattern + r")(?!\w)", re.I))
        for weight, pattern in rules
    ]


_RULES = {
    "sports": _compile_rules([
        (5.0, r"football|soccer|basketball|baseball|hockey|ice hockey|cricket|rugby|tennis|golf|volleyball|lacrosse|softball|badminton|squash|handball|water polo|field hockey"),
        (4.5, r"boxing|boxer|wrestling|wrestler|mixed martial arts|mma|kickboxing|judo|karate|taekwondo|fencing|gymnastics|gymnast|figure skating|speed skating|snowboarding|skiing|cycling|cyclist|marathon|triathlon|athletics|track and field"),
        (5.5, r"nfl|nba|wnba|mlb|nhl|mls|ncaa|uefa|fifa|wta|atp tour|pga tour|lpga|ufc|nascar|indycar|formula (?:one|1)|f1 racing|premier league|champions league|europa league|la liga|serie a|bundesliga|ligue 1|major league baseball|national football league|national basketball association|national hockey league"),
        (5.0, r"super bowl|world series|stanley cup|ryder cup|davis cup|fed cup|billie jean king cup|world cup|european championship|euros|copa america|africa cup of nations|asian cup|six nations|ashes series|tour de france|giro d'italia|vuelta a españa|grand slam|wimbledon|roland garros|french open|australian open|us open|kentucky derby|indianapolis 500|monaco grand prix|olympic(?:s| games)?|paralympic(?:s| games)?"),
        (4.5, r"touchdown|quarterback|running back|wide receiver|linebacker|field goal|end zone|super bowl|yardage|rushing yards|passing yards|interception|home run|home runs|grand slam homer|strikeout|pitcher|bullpen|inning|innings|batter|batting average|shortstop|outfielder|catcher|pinch hitter"),
        (4.5, r"three.pointer|three.point shot|slam dunk|rebound(?:s|ed)?|point guard|power forward|free throw|penalty kick|penalty shootout|hat trick|goalkeeper|goaltender|wicket|bowler|batsman|batter scored|century partnership|test match|tiebreak|tie.break|match point|set point|birdie|eagle putt|bogey|hole.in.one|pole position|checkered flag"),
        (3.5, r"goal(?:s|keeper)?|scor(?:ed|es|ing) (?:a |two |three |four |the )?(?:goal|goals|touchdown|points|runs)|shutout|clean sheet|overtime win|extra time|playoffs?|postseason|semifinals?|quarterfinals?|title game|championship game|league title|league leaders?|league standings|tournament|finals?|medal(?:ist|ists)?|podium finish"),
        (3.5, r"athlete(?:s)?|sportsman|sportswoman|sports team|head coach|assistant coach|team coach|manager of the team|player(?:s)?|striker|midfielder|defender|goalie|teammate(?:s)?|rookie|all.star|mvp|most valuable player|sports franchise|referee|umpire|stadium|ballpark|locker room|roster"),
        (3.0, r"season opener|season finale|regular season|preseason|winning streak|losing streak|unbeaten|undefeated|reigning champion|defending champion|league champion|world champion|top seed|second seed|third seed|seeded player|ranked player|sports fans|fans at the game"),
        (4.0, r"beat(?:s|en)?|defeat(?:s|ed)?|edg(?:e|es|ed)|rout(?:s|ed)?|crush(?:es|ed)?|upset(?:s)?|outscor(?:e|es|ed)|trounc(?:e|es|ed)\s+(?:the\s+)?(?:\w+\s+){0,3}(?:team|club|rivals?|champions?)"),
        (4.5, r"\b\d{1,3}\s*[-:]\s*\d{1,3}\s+(?:victory|win|loss|defeat|draw|tie)|(?:won|lost|win|beat|defeated|victory|loss|score)\s+(?:by\s+)?\d{1,3}\s*[-:]\s*\d{1,3}"),
        (5.0, r"yankees|red sox|mets|dodgers|giants|cubs|white sox|astros|braves|phillies|padres|orioles|blue jays|cardinals|mariners|athletics baseball|tigers baseball|lakers|celtics|warriors|knicks|bulls|heat|spurs|mavericks|rockets|suns|bucks|76ers|sixers|clippers|cavaliers|raptors|nuggets|timberwolves"),
        (5.0, r"patriots|cowboys|steelers|packers|49ers|forty.niners|eagles|chiefs|ravens|bengals|broncos|raiders|jets|bills|dolphins|seahawks|vikings|saints|buccaneers|panthers|falcons|colts|chargers|rams|browns|titans|jaguars|commanders|redskins"),
        (5.0, r"manchester united|manchester city|arsenal|chelsea|liverpool|tottenham|real madrid|barcelona|bayern munich|borussia dortmund|juventus|ac milan|inter milan|paris saint.germain|psg|ajax|celtic fc|rangers fc"),
        (5.0, r"messi|cristiano ronaldo|ronaldo|neymar|mbapp[eé]|haaland|beckham|zidane|ronaldinho|kobe bryant|lebron james|michael jordan|stephen curry|shaquille o.neal|shaquille|tiger woods|jack nicklaus|serena williams|venus williams|roger federer|rafael nadal|novak djokovic|andy murray|michael phelps|usain bolt|simone biles|tom brady|peyton manning|patrick mahomes|babe ruth|barry bonds|mike tyson|muhammad ali|lewis hamilton|michael schumacher|max verstappen"),
        (2.0, r"sport(?:s|ing)?|fixture|match(?:es)?|game(?:s)?|season|opponent(?:s)?|rival(?:s)?|club|coach(?:es|ed)?|team(?:s)?|victory|defeat(?:ed)?"),
    ]),
    "sci_tech": _compile_rules([
        (6.0, r"microsoft|google|alphabet inc|apple inc|apple computer|ibm|intel|nvidia|amd|advanced micro devices|qualcomm|cisco|oracle|salesforce|adobe|hewlett.packard|hewlett packard|hp inc|dell technologies|dell computer|lenovo|samsung electronics|tsmc|taiwan semiconductor|broadcom|arm holdings|micron|motorola|nokia|ericsson|huawei|blackberry|blackberry maker|sun microsystems|red hat|vmware"),
        (6.0, r"openai|anthropic|deepmind|chatgpt|facebook|instagram|whatsapp|meta platforms|tiktok|bytedance|snapchat|youtube|netflix|spotify|twitter|linkedin|pinterest|reddit|ebay|yahoo|aol|america online|amazon\.com|amazon web services|amazon prime|aws|alibaba|tencent|baidu|bytedance"),
        (5.0, r"apple(?=\s+(?:inc|computer|iphone|ipad|watch|mac|stock|shares|earnings|revenue|profit|sales|said|says|announced|announces|launched|launches|unveiled|unveils|released|releases|plans|will|is|has|reported|reports|sued|lawsuit|ceo|co.founder))|amazon(?=\s+(?:inc|\.com|stock|shares|earnings|revenue|profit|sales|said|says|announced|announces|launched|launches|unveiled|unveils|plans|will|is|has|reported|reports|sued|lawsuit|ceo|web services))"),
        (5.5, r"iphone|ipad|ipod|macbook|macintosh|imac|apple watch|ios|android|windows (?:xp|vista|7|8|10|11|phone)|microsoft windows|windows operating system|office 365|microsoft office|linux|unix|ubuntu|chrome browser|firefox|safari browser|internet explorer|google search|google maps|google cloud|playstation|xbox|nintendo|game boy|gamecube|wii|switch console|geforce|radeon|pentium|core processor|ryzen|snapdragon"),
        (4.5, r"software|hardware|computer(?:s)?|computing|laptop(?:s)?|desktop computer|personal computer|pc makers?|smartphone(?:s)?|mobile phone(?:s)?|cell ?phone(?:s)?|handset(?:s)?|tablet computers?|computer chips?|microchips?|microprocessors?|semiconductors?|integrated circuits?|graphics card|graphics processor|gpu|cpu|processors?|motherboard|data centers?|cloud computing|cloud storage"),
        (4.5, r"artificial intelligence|generative ai|machine learning|deep learning|large language models?|language model|chatbots?|neural networks?|robotics|robots?|autonomous vehicles?|self.driving (?:cars?|vehicles?)|facial recognition|virtual reality|augmented reality|quantum computing|quantum computer"),
        (4.0, r"internet|websites?|web pages?|world wide web|worldwide web|online platform|social media|social network|search engine|web browser|broadband|wi.fi|wifi|wireless network|5g network|4g network|telecommunications?|telecoms?|mobile network|cellular network|fiber.optic|fibre.optic|satellite communications?"),
        (4.0, r"cybersecurity|cyber.security|cyberattack|cyber attack|ransomware|malware|computer virus|computer worm|hackers?|hacking|phishing|data breach|security breach|software vulnerability|cybercrime|cyber crime|encryption|passwords?|firewall|computer network"),
        (4.0, r"video games?|videogames?|computer games?|gaming console|game console|game developers?|game publishers?|esports|e.sports|gaming industry|online gaming|multiplayer game"),
        (3.5, r"app(?:s|lication)?(?: store)?|mobile app|download(?:s|ed|ing)?|software updates?|operating system|database|data analytics|digital technology|tech(?:nology)? (?:company|companies|firm|firms|giant|giants|industry|sector|product|products|startup|startups)|start.up|startup|silicon valley|high.tech|tech giant"),
        (5.0, r"nasa|esa spacecraft|european space agency|spacex|blue origin|international space station|space station|space shuttle|spacecraft|astronauts?|cosmonauts?|space mission|space probe|space exploration|space telescope|hubble telescope|james webb telescope|mars rover|lunar lander|moon landing|rocket launch|satellite launch"),
        (4.5, r"astronom(?:y|er|ers|ical)|astrophysic(?:s|ist|ists)|galax(?:y|ies)|exoplanets?|black holes?|solar system|distant stars?|planetary science|cosmic rays?|supernova|meteorites?|asteroids?|comets?|lunar surface|martian surface"),
        (4.0, r"scientists?|scientific research|science research|researchers?|research team|research study|laboratory|laboratories|scientific discovery|scientific breakthrough|experiment(?:al|s)?|physics|physicists?|chemistry|chemists?|biology|biologists?|genetics|geneticists?|genome|genomics|dna sequencing|gene editing|crispr|fossils?|paleontolog(?:y|ist|ists)|archaeolog(?:y|ist|ists)|archaeological"),
        (4.5, r"clinical trials?|drug trials?|vaccine trials?|medical research|medical study|medical breakthrough|new treatment|experimental treatment|experimental drug|new drug|gene therapy|stem cells?|cancer research|cancer treatment|cancer drug|cancer vaccine|disease research|research into (?:cancer|disease|diabetes|alzheimer.s)|develop(?:ed|ing)? (?:a )?(?:vaccine|drug|treatment|cure)|study (?:finds|found|shows|showed|suggests|suggested|reveals|revealed)"),
        (3.0, r"peer.reviewed|journal (?:nature|science|medicine)|published (?:a |the )?(?:study|findings|research)|new study|new research|research findings|human genome|genetic mutation|genetic engineering|cloning|cloned|biotechnology|biotech|pharmaceutical research|researchers (?:say|said|found|have found|discovered)"),
    ]),
    "business": _compile_rules([
        (5.0, r"stock market|stock markets|stock exchange|stock prices?|stock indexes?|stock indices|stock futures|equity markets?|share prices?|wall street|dow jones|dow industrials|s&p 500|s&p index|nasdaq|nikkei|ftse|hang seng|dax index|treasury bonds?|bond market|bond yields?|market capitalization|market cap|mutual funds?|hedge funds?|stockholders?|shareholders?|investors?"),
        (4.0, r"stocks?|shares?|equities|securities|bonds?|dividends?|dividend payments?|trading session|trading day|trading volume|stock trading|stock traders?|market rally|market sell.off|bull market|bear market|closing bell|opening bell|ipo|initial public offering|public offering|listing on the exchange|investment portfolio|brokerage|stockbroker|analysts?"),
        (4.5, r"earnings|quarterly (?:results|profit|profits|revenue|sales|earnings|loss|losses)|annual (?:results|profit|profits|revenue|sales|earnings|loss|losses)|net income|net profit|net loss|operating profit|operating loss|revenue|revenues|profit(?:s|able)?|losses for the quarter|fiscal (?:year|quarter)|earnings per share|sales forecast|profit forecast|earnings forecast|financial results|balance sheet|cash flow"),
        (4.0, r"merger|mergers|merged|acquisition|acquisitions|acquire(?:s|d)?|acquiring|takeover|takeover bid|buyout|buy.out|business deal|corporate deal|joint venture|private equity|venture capital|bankrupt(?:cy)?|insolvency|restructuring|layoffs?|laid off|job cuts?|corporate restructuring|antitrust lawsuit|antitrust suit"),
        (4.5, r"econom(?:y|ies|ic|ics)|gross domestic product|gdp|inflation|deflation|recession|economic growth|economic downturn|economic recovery|economic data|unemployment rate|jobless rate|jobs report|labor market|labour market|consumer spending|consumer confidence|retail sales|industrial production|manufacturing output|trade deficit|trade surplus|trade agreement|international trade|tariffs?|exports?|imports?"),
        (4.0, r"interest rates?|rate cut|rate hike|rate increase|central bank|federal reserve|fed chair|bank of england|european central bank|monetary policy|interest.rate policy|currency markets?|foreign exchange|exchange rate|dollar (?:rose|fell|rises|falls|gained|weakened|strengthened)|yen (?:rose|fell|rises|falls)|euro (?:rose|fell|rises|falls)|devaluation"),
        (4.5, r"oil prices?|crude oil|crude futures|brent crude|west texas intermediate|opec|petroleum|gasoline prices?|petrol prices?|natural gas prices?|energy prices?|oil futures|oil markets?|oil production|oil producers?|commodity prices?|commodities markets?|gold prices?|gold futures|copper prices?|wheat prices?|commodity traders?"),
        (4.0, r"airlines?|airways|air carriers?|commercial aviation|airfare|air fares?|airline tickets?|flight bookings?|retailers?|retailing|retail chains?|supermarkets?|grocery chains?|department stores?|shopping malls?|automakers?|car makers?|auto industry|automobile industry|manufacturers?|manufacturing industry|banks?|banking industry|insurance companies|insurers?|hotel chains?|shipping companies|freight companies"),
        (5.0, r"walmart|wal.mart|costco|target corp|target stores|home depot|lowe.s|carrefour|tesco|kroger|safeway|amazon retailer|mcdonald.s|burger king|starbucks|coca.cola|pepsi(?:co)?|procter\s*(?:&|and)\s*gamble|unilever|nestl[eé]|general mills|kraft heinz|tyson foods|nike|adidas|gap inc|disney|walt disney|comcast|warner bros|time warner|viacom|paramount global"),
        (5.0, r"exxon(?:mobil)?|chevron|shell oil|royal dutch shell|british petroleum|bp oil|conocophillips|saudi aramco|totalenergies|petrobras|boeing|airbus|general motors|ford motor|chrysler|stellantis|toyota|honda|volkswagen|bmw|mercedes.benz|hyundai|nissan|tesla motors|fedex|united parcel service|dhl|american airlines|united airlines|delta air lines|southwest airlines|british airways|lufthansa|air france|ryanair|easyjet"),
        (5.0, r"jpmorgan|jp morgan|goldman sachs|morgan stanley|bank of america|citigroup|citibank|wells fargo|hsbc|barclays|deutsche bank|credit suisse|ubs bank|berkshire hathaway|blackrock|visa inc|mastercard|american express|lehman brothers|merrill lynch"),
        (3.0, r"chief executive|chief financial officer|ceo|cfo|corporate|corporation|company|companies|businesses|business sector|business executives?|board of directors|corporate earnings|firm(?:s)?|price cuts?|price increases?|wholesale prices?|consumer prices?|supply chain|distribution centers?"),
    ]),
    "world": _compile_rules([
        (4.0, r"government|governments|president|presidential|prime minister|premier of|chancellor|governor|mayor|cabinet minister|foreign minister|defense minister|defence minister|secretary of state|head of state|head of government|white house|state department|pentagon|downing street"),
        (4.5, r"election(?:s|eer(?:ing)?)?|voters?|voting|ballot(?:s)?|polling station|polling place|opinion polls?|campaign trail|election campaign|political campaign|presidential candidate|presidential race|primary election|general election|midterm election|runoff election|electoral college|referendum|plebiscite|ballot measure"),
        (4.0, r"politic(?:s|al|ian|ians)|parliament|parliamentary|congress|congressional|senate|senator(?:s)?|house of representatives|lawmakers?|legislators?|legislature|legislation|bill passed|bill signed|political party|ruling party|opposition party|democrats?|republicans?|labour party|labor party|conservatives?|liberal party|coalition government|diplomacy|diplomatic"),
        (4.5, r"united nations|u\.n\.|security council|nato|european union|european commission|european parliament|arab league|african union|peace talks|peace treaty|cease.fire|truce|diplomatic relations|foreign policy|international relations|sanctions against|economic sanctions"),
        (5.0, r"war|warfare|armed conflict|civil war|invasion|invad(?:e|ed|es|ing)|military offensive|military operation|military forces|troops?|soldiers?|armed forces|army|navy|air force|battlefield|combat|fighting in|airstrikes?|air strikes?|missile attacks?|rocket attacks?|shelling|artillery|bombardment|bombings?|bomb explosion|suicide bomber|insurgents?|militants?|guerrillas?|rebel forces|rebels?|terroris(?:m|t|ts)|terror attacks?|hostages?|kidnapp(?:ed|ing|ers?)"),
        (4.0, r"israel(?:i)?|palestinian(?:s)?|gaza|west bank|hamas|hezbollah|taliban|al.qaeda|isis|islamic state|iraqi forces|ukrainian forces|russian forces|north korean missile|nuclear weapons?|nuclear warheads?|weapons of mass destruction"),
        (4.5, r"police|sheriff|detectives?|law enforcement|arrest(?:ed|s|ing)?|charged with|criminal charges?|indict(?:ed|ment)?|prosecutors?|criminal trial|murder(?:ed|s|er)?|homicide|manslaughter|shooting|shot dead|shot and killed|stabbed|stabbing|robbery|robberies|burglary|burglars?|assault(?:ed)?|sexual assault|rape|rapist|abduction|missing person|suspect(?:s)?|convict(?:ed|ion)?|sentenced|prison(?:er|ers)?|jail(?:ed)?|death penalty|execution|drug trafficking|human trafficking|gang violence"),
        (4.5, r"earthquake|quake|tsunami|hurricane|typhoon|cyclone|tornado(?:es)?|wildfire|forest fires?|flood(?:s|ing|ed)?|landslide|mudslide|avalanche|volcanic eruption|volcano erupts|disaster|natural disaster|drought|heat wave|heatwave|severe storm|blizzard|plane crash|aircraft crash|train crash|train derailment|shipwreck|ferry sank|ferry disaster|building collapse|bridge collapse"),
        (3.5, r"killed|dead(?:ly)?|deaths?|death toll|fatalities|injured|injuries|wounded|casualties|victims?|rescue workers?|emergency services|evacuat(?:e|ed|ion|ions)|refugees?|displaced people|humanitarian crisis|protests?|protesters?|demonstrators?|riots?|riot police"),
        (4.5, r"george w\.? bush|president bush|john kerry|barack obama|president obama|joe biden|president biden|donald trump|president trump|vladimir putin|president putin|volodymyr zelensky(?:y)?|zelensky(?:y)?|tony blair|george w bush|bill clinton|hillary clinton|kamala harris|angela merkel|emmanuel macron|benjamin netanyahu|saddam hussein|osama bin laden|xi jinping|kim jong.un|nelson mandela"),
        (2.0, r"court ruling|supreme court|federal court|judge|judges|judicial|lawsuit|lawsuits|legal case|criminal case|constitutional|constitution|human rights|civil rights|immigration|immigrants?|asylum seekers?|border security|officials?|authorities"),
    ]),
}

_TEXT_KEYS = {
    "text", "title", "headline", "heading", "subject", "description",
    "summary", "article", "article_text", "article_body", "body", "content",
    "story", "news", "news_text", "passage", "document", "input", "prompt",
    "abstract", "snippet", "lead", "body_text", "query",
}
_TITLE_KEYS = {"title", "headline", "heading", "subject"}
_SKIP_KEYS = {
    "answer", "label", "labels", "category", "categories", "class",
    "classification", "target", "expected", "output", "id", "url", "link",
    "source", "author", "date", "timestamp", "published", "metadata",
}


def _extract_text(state):
    pieces = []
    titles = []
    seen = set()

    def add(value, is_title):
        value = value.strip()
        if not value:
            return
        if value not in seen:
            seen.add(value)
            pieces.append(value)
        if is_title and value not in titles:
            titles.append(value)

    def visit(value, key="", depth=0):
        if depth > 20:
            return
        if isinstance(value, str):
            if key not in _SKIP_KEYS:
                add(value, key in _TITLE_KEYS)
        elif isinstance(value, dict):
            entries = []
            for k, v in value.items():
                name = str(k).strip().lower().replace(" ", "_").replace("-", "_")
                if name not in _SKIP_KEYS:
                    entries.append((name, v))
            entries.sort(key=lambda item: (0 if item[0] in _TITLE_KEYS else
                                           1 if item[0] in _TEXT_KEYS else 2))
            for name, v in entries:
                visit(v, name, depth + 1)
        elif isinstance(value, (list, tuple)):
            for item in value:
                visit(item, key, depth + 1)

    visit(state)
    text = "\n".join(pieces)
    if titles:
        headline = " ".join(titles)
    else:
        headline = text[:220]
        sentence = re.search(r"[.!?](?:\s|$)", headline)
        if sentence and sentence.end() >= 35:
            headline = headline[:sentence.end()]
    return text, headline


def _normalize(text):
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("&amp;", "&").replace("&quot;", '"')
    text = text.replace("&#39;", "'").replace("&nbsp;", " ")
    return text


def _rule_score(text, headline, rules):
    total = 0.0
    for weight, pattern in rules:
        full_count = 0
        for _ in pattern.finditer(text):
            full_count += 1
            if full_count == 3:
                break
        if not full_count:
            continue
        headline_count = 0
        for _ in pattern.finditer(headline):
            headline_count += 1
            if headline_count == 2:
                break
        total += weight * (1.0 + 0.35 * (full_count - 1))
        total += weight * 1.25 * (headline_count ** 0.5)
    return total


def predict(state):
    text, headline = _extract_text(state)
    text = _normalize(text)
    headline = _normalize(headline)
    if not text.strip():
        return {"answer": "world"}

    scores = {
        category: _rule_score(text, headline, rules)
        for category, rules in _RULES.items()
    }

    # General-purpose words can mean something quite different outside sports.
    if not re.search(
        r"\b(?:sport|sports|game|games|match|matches|team|teams|player|players|"
        r"coach|league|championship|tournament|season|goal|football|soccer|"
        r"baseball|basketball|hockey|tennis|golf|cricket|olympic|nfl|nba|mlb|nhl|"
        r"fifa|uefa|win|won|score|scored|race|racing|medal)\b",
        text, re.I
    ):
        scores["sports"] *= 0.75

    # Political uses of "campaign", "race", "win" and "defeat" are not sports.
    if re.search(r"\b(?:election|electoral|voters?|ballot|presidential race|"
                 r"political campaign)\b", headline, re.I):
        scores["world"] += 4.0

    # An accident or attack involving an aircraft is ordinarily disaster news,
    # not a commercial airline report.
    if re.search(r"\b(?:plane|aircraft|airliner|jet|helicopter)\b.{0,55}"
                 r"\b(?:crash(?:ed|es)?|shot down|explod(?:ed|es)|hijack(?:ed|ing)?)\b|"
                 r"\b(?:plane|aircraft|airliner|aviation) crash\b",
                 headline, re.I):
        scores["world"] += 9.0

    # Market roundups are business stories even when technology shares are
    # mentioned among the companies contributing to the market movement.
    if re.search(r"\b(?:wall street|stock market|stocks|shares|dow jones|"
                 r"nasdaq|s&p 500)\b", headline, re.I) and re.search(
                     r"\b(?:stocks|market|markets|dow|index|indices|"
                     r"shares)\b.{0,45}\b(?:rise|rose|rises|fall|fell|"
                     r"falls|gain|gained|drop|dropped|close|closed|"
                     r"higher|lower|rally|rallied|slide|slid)\b|"
                     r"\b(?:rise|fall|rally|sell.off)\b.{0,35}"
                     r"\b(?:stocks|markets|shares)\b", headline, re.I):
        scores["business"] += 6.0

    # Reports about research into a disease are science; reports of deaths or
    # outbreaks without a research context are more often general news.
    if re.search(r"\b(?:outbreak|epidemic|pandemic)\b", headline, re.I):
        if not re.search(r"\b(?:research|study|scientists?|trial|vaccine|"
                         r"treatment|discovery)\b", headline, re.I):
            scores["world"] += 4.0

    # A score such as "3-1" is useful when surrounded by sports language,
    # but not when it is part of a date or a financial figure.
    if re.search(r"\b\d{1,2}\s*[-:]\s*\d{1,2}\b", headline) and re.search(
        r"\b(?:win|won|beat|beats|defeat|defeated|victory|loss|draw|game|"
        r"match|team|goal|goals|set|sets|innings)\b", headline, re.I
    ):
        scores["sports"] += 5.0

    # Prefer the more specific subject areas on a close tie.
    order = ("sci_tech", "sports", "business", "world")
    answer = max(order, key=lambda category: scores[category])
    if scores[answer] <= 0:
        answer = "world"
    return {"answer": answer}