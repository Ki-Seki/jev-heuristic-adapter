import re


def _compile_features(groups):
    return [
        (weight, re.compile(r"(?<![a-z0-9])(?:%s)(?![a-z0-9])" % pattern))
        for weight, pattern in groups
    ]


FEATURES = {
    "sports": _compile_features([
        (6, r"football|soccer|baseball|basketball|hockey|ice hockey|rugby|cricket|tennis|golf|volleyball|badminton|lacrosse|softball|field hockey|handball|water polo"),
        (6, r"nfl|nba|wnba|mlb|nhl|mls|ncaa|uefa|fifa|pga|lpga|atp tour|wta tour|ipl|afl|nrl"),
        (6, r"olympics?|olympians?|olympic games|paralympics?|world cup|champions league|premier league|la liga|bundesliga|serie a|world series|super bowl|stanley cup|wimbledon|tour de france|ryder cup|davis cup|six nations"),
        (5, r"nascar|formula one|formula 1|f1 racing|grand prix|indycar|motogp|motorsports?|stock car racing"),
        (5, r"boxing|boxer|boxers|wrestling|wrestler|wrestlers|mixed martial arts|mma|ufc|heavyweight title|welterweight|knockout round"),
        (5, r"quarterbacks?|touchdowns?|interceptions?|wide receiver|running back|field goal|linebacker|super bowl"),
        (5, r"pitchers?|pitching|batters?|batting|home runs?|innings?|bullpen|shortstop|strikeouts?|major leagues|minor leagues|no hitter"),
        (5, r"slam dunks?|three pointers?|rebounds?|point guard|free throws?|slam dunk"),
        (5, r"wickets?|batsman|batsmen|bowlers?|test match|test cricket|one day international|twenty20|t20"),
        (5, r"grand slam|match point|set point|break point|serves? an ace|aces? and double faults|singles title|doubles title"),
        (5, r"birdies|eagles and birdies|putts?|putting green|golfers?|fairway|under par|over par|golf course"),
        (5, r"marathons?|triathlons?|decathlon|sprint(?:er|ers|ing)?|track and field|pole vault|high jump|long jump|swimming championships?|gymnastics|figure skating|ski jumping"),
        (4.5, r"athletes?|sportsperson|sportsmen|sportswomen|sporting event|sports league|professional sports|sports team"),
        (4, r"playoffs?|postseason|semifinals?|quarterfinals?|championship game|title game|league title|league standings|division title|league championship|tournament"),
        (4, r"coaches?|head coach|team captain|goalkeeper|goalie|defender|midfielder|striker|forward line|team roster|draft pick|drafted by"),
        (3.5, r"teams?|teammates?|opponents?|rivals?|players?|fans|spectators|club side|home crowd|away team|home team"),
        (3, r"match(?:es)?|games?|fixture|fixtures|season opener|season finale|regular season|winning streak|losing streak|unbeaten|undefeated"),
        (3, r"scored|scores|scoring|goal(?:s)?|goalless|goal scorer|equalizer|equaliser|hat trick|penalty shootout|overtime|extra time|shutout"),
        (2.5, r"defeated|defeats|beat|beats|beaten|victory|victories|win(?:s|ning|ner|ners)?|won|loss|losses|lost|draws?|drawn|titles?"),
        (5, r"arsenal|chelsea|liverpool|manchester united|manchester city|real madrid|barcelona|bayern munich|borussia dortmund|juventus|ac milan|inter milan|paris saint germain|celtic fc|rangers fc|tottenham"),
        (5, r"yankees|red sox|dodgers|mets|cubs|phillies|astros|braves|cardinals|blue jays|lakers|celtics|warriors|knicks|bulls|cavaliers|spurs|heat|mavericks|bucks|76ers|eagles|cowboys|patriots|chiefs|49ers|packers|steelers|ravens|bengals|seahawks|broncos|dolphins|raiders|jets|maple leafs|canadiens|oilers|penguins"),
        (5, r"michael jordan|lebron james|kobe bryant|stephen curry|shaquille o neal|tom brady|peyton manning|patrick mahomes|aaron rodgers|lionel messi|cristiano ronaldo|david beckham|ronaldinho|zinedine zidane|kylian mbappe|erling haaland|serena williams|venus williams|roger federer|rafael nadal|novak djokovic|andy murray|tiger woods|rory mcilroy|michael schumacher|lewis hamilton|max verstappen|lance armstrong|usain bolt|michael phelps"),
    ]),
    "business": _compile_features([
        (6, r"stock markets?|stock exchanges?|wall street|stock indexes?|stock indices|stock market|equity markets?|financial markets?|bond markets?|futures markets?|trading session"),
        (5, r"dow jones|nasdaq composite|s&p 500|standard and poor s|ftse|nikkei|hang seng|dax index|cac 40|index of leading shares"),
        (4, r"stocks?|shares?|equities|shareholders?|investors?|investment|investing|dividends?|securities|bonds?|treasuries|mutual funds?|hedge funds?|asset managers?"),
        (5, r"earnings|quarterly profit|quarterly results|quarterly revenue|net income|operating profit|profit margins?|net loss|fiscal (?:year|quarter)|full year results|financial results|sales forecast|revenue forecast"),
        (3.5, r"profits?|revenues?|turnover|sales|losses|earnings per share|eps|forecast|outlook|guidance|annual results"),
        (5, r"mergers?|acquisitions?|takeovers?|buyouts?|buyout|buying a stake|acquire[sd]?|acquisition|acquiring|acquirer|acquired by|merging|takeover bid|deal to buy"),
        (5, r"initial public offering|initial share offering|ipo|going public|listed on the stock exchange|stock market flotation|share offering"),
        (5, r"interest rates?|inflation|deflation|gross domestic product|gdp|economic growth|economic slowdown|recession|economic output|consumer prices|producer prices|unemployment rate"),
        (5, r"federal reserve|the fed|central banks?|bank of england|european central bank|ecb|bank of japan|monetary policy|rate cut|rate hike|benchmark rate"),
        (4.5, r"economy|economies|economic|economists?|macroeconomic|economic data|economic indicators?|consumer spending|consumer confidence|retail sales|jobless claims|payrolls|labor market|labour market"),
        (5, r"oil prices?|crude oil|crude prices?|oil futures|brent crude|west texas intermediate|natural gas prices?|gasoline prices?|petrol prices?|commodity prices?|commodities markets?|gold prices?|copper prices?|barrels? of oil|opec"),
        (4, r"currency markets?|foreign exchange|exchange rates?|the dollar|the euro|the yen|the pound|dollar rose|dollar fell|currency trading"),
        (4.5, r"bankruptcy|bankrupt|insolvency|insolvent|chapter 11|creditors?|debt restructuring|defaulted on|debt payments?|credit rating|ratings agency"),
        (4, r"banks?|banking|lenders?|loans?|mortgages?|credit cards?|insurance companies|insurers?|underwriters?|financial services|private equity"),
        (4, r"businesses|corporations?|companies|company|firms?|chief executives?|chief financial officers?|ceos?|executives?|board of directors|management|corporate"),
        (4, r"manufacturers?|manufacturing|factories|factory|industrial production|supply chains?|production costs|automakers?|car makers?|car sales"),
        (4, r"retailers?|retailing|retail industry|department stores?|supermarkets?|shopping malls?|consumer goods|consumer products|retail chain"),
        (4, r"airlines?|air carriers?|aviation industry|air travel demand|passenger traffic|air fares?|airfares?|flight attendants?|airline pilots?"),
        (4, r"international trade|trade deficit|trade surplus|exports?|imports?|tariffs?|trade agreement|trade talks|trade barriers|free trade|world trade organization|wto"),
        (3.5, r"real estate|housing market|home prices?|house prices?|housing prices?|home sales|house sales|property market|commercial property|construction spending"),
        (3.5, r"layoffs?|laid off|job cuts?|jobs? cut|cutting jobs|downsizing|restructur(?:e|ed|ing)|plant closure|factory closure|strike by workers|labor union|labour union|workers union"),
        (4.5, r"walmart|wal mart|target corp|costco|carrefour|tesco|home depot|mcdonalds|coca cola|pepsi(?:co)?|procter and gamble|unilever|nestle|boeing|airbus|general motors|ford motor|toyota|volkswagen|bmw|chrysler|exxon(?:mobil)?|chevron|shell oil|bp plc|jpmorgan|goldman sachs|morgan stanley|citigroup|bank of america|wells fargo|berkshire hathaway"),
    ]),
    "sci_tech": _compile_features([
        (11, r"microsoft|google|alphabet inc|apple inc|apple computer|international business machines|ibm|intel|amd|advanced micro devices|nvidia|qualcomm|cisco|oracle corp|oracle corporation|samsung|sony|huawei|ericsson|nokia|motorola|dell|hewlett packard|hewlett packard enterprise|hp inc|lenovo|asus|acer computer|adobe|salesforce|sap software|vmware|red hat|linux foundation|openai|anthropic|deepmind|meta platforms|facebook|instagram|whatsapp|tiktok|bytedance|twitter|linkedin|snapchat|ebay|paypal|yahoo|aol|america online|lycos|netscape|mozilla|netflix|spotify|uber|lyft|airbnb|shopify|alibaba|tencent|baidu|broadcom|arm holdings|tsmc|micron technology|seagate|western digital|blackberry|research in motion"),
        (7, r"iphone|ipad|ipod|macintosh|macbook|windows (?:xp|vista|7|8|10|11|server)|microsoft windows|android|ios|chrome os|linux|unix|playstation|xbox|nintendo|game boy|kindle|google search|google maps|gmail|chatgpt|gpt 4|gpt 5"),
        (6, r"software|hardware|computer programs?|computer systems?|operating systems?|applications?|apps?|software developers?|software companies|programming|source code|open source|software update|firmware"),
        (6, r"computers?|laptops?|desktops?|tablets?|smartphones?|mobile phones?|cell ?phones?|handsets?|personal digital assistants?|pda|workstations?|computer servers?|data centers?|data centres?|supercomputers?"),
        (6, r"semiconductors?|microprocessors?|processors?|computer chips?|chipmakers?|chip makers?|graphics cards?|graphics processors?|gpu|cpu|microchips?|integrated circuits?|silicon chips?"),
        (6, r"internet|websites?|world wide web|web pages?|web browsers?|online services?|search engines?|search results?|email|e mail|emails|e mails|social media|social networks?|online platforms?|web traffic"),
        (6, r"cybersecurity|cyber security|cyberattacks?|cyber attacks?|computer viruses|computer virus|malware|ransomware|spyware|phishing|keystrokes?|passwords?|hackers?|hacking|data breaches?|security flaws?|security vulnerabilities|screensavers?|screensaver|firewalls?|antivirus"),
        (6, r"telecommunications?|telecoms?|broadband|wireless networks?|mobile networks?|cellular networks?|5g|4g|3g|wi fi|wifi|fiber optic|fibre optic|telecom(?:munications)? companies|mobile carriers?|mobile operators?"),
        (6, r"video games?|videogames?|gaming consoles?|game consoles?|game developers?|game publishers?|computer games?|online gaming|esports|e sports"),
        (6, r"artificial intelligence|machine learning|deep learning|neural networks?|generative ai|large language models?|chatbots?|robotics|robots?|autonomous systems?|computer vision"),
        (6, r"nasa|space agency|spacecraft|space shuttle|space station|international space station|space telescopes?|space probes?|space missions?|space exploration|astronauts?|cosmonauts?|mars rover|lunar lander|moon landing|rocket launch|satellites? in orbit"),
        (5, r"astronomy|astronomers?|astrophysics|astrophysicists?|galax(?:y|ies)|black holes?|exoplanets?|solar systems?|distant planets?|the universe|the cosmos|mars|jupiter|saturn|asteroids?|comets?|meteorites?"),
        (5, r"scientific research|medical research|clinical (?:trial|trials|study|studies)|scientific (?:study|studies|discovery|findings)|researchers?|scientists?|scientific journal|peer reviewed|laboratory|laboratories|research team|new study|new studies"),
        (5, r"genetics|genetic research|genome|genomics|dna sequencing|gene editing|crispr|stem cells?|molecular biology|biotechnology|biotech|nanotechnology|quantum computing|particle physics"),
        (5, r"medical researchers?|medical breakthrough|experimental (?:drug|treatment|therapy|vaccine)|new (?:drug|treatment|therapy|vaccine)|drug trials?|vaccine trials?|clinical evidence|drug development|cancer research|diagnostic test|medical device|scientific evidence"),
        (4, r"physicists?|chemists?|biologists?|neuroscientists?|epidemiologists?|archaeologists?|archaeology|paleontology|palaeontology|fossils?|dinosaurs?|new species|scientific discovery"),
        (4, r"technology|technologies|technological|tech industry|tech sector|technology companies|tech companies|tech firms|tech giant|tech giants|high tech|electronics|digital devices?"),
        (4, r"cloud computing|cloud services?|data storage|databases?|digital privacy|data privacy|data protection|encryption|virtual reality|augmented reality|blockchain|cryptocurrency|bitcoin"),
        (3, r"downloads?|downloaded|downloading|online|digital|web based|internet based|browsing|streaming|search engine"),
        (3, r"patients?|disease|diseases|cancer|diabetes|alzheimer(?:s)?|parkinson(?:s)?|heart disease|treatments?|therap(?:y|ies)|vaccines?|infections?|viruses|virus|bacteria"),
        (3, r"climate science|climate researchers?|climate model|global warming research|environmental research|oceanographers?|geologists?|earthquake research"),
    ]),
    "world": _compile_features([
        (5, r"presidents?|prime ministers?|foreign ministers?|heads? of state|chancellors?|governors?|mayors?|cabinet ministers?|secretary of state|white house|downing street"),
        (5, r"elections?|electoral|ballots?|polling stations?|voters?|voting|vote count|vote counting|referendums?|referenda|campaign trail|presidential race|presidential candidate|parliamentary candidate|re election|reelection"),
        (4, r"governments?|politicians?|political parties|political party|politics|political|parliament|parliamentary|congress|congressional|senate|senators?|lawmakers?|legislators?|legislature|opposition party|ruling party|coalition government"),
        (5, r"donald trump|joe biden|barack obama|george w bush|george bush|john kerry|kamala harris|hillary clinton|bill clinton|tony blair|gordon brown|keir starmer|rishi sunak|vladimir putin|volodymyr zelensky|benjamin netanyahu|mahmoud abbas|yasser arafat|saddam hussein|xi jinping|narendra modi|emmanuel macron|angela merkel|olaf scholz|kim jong un|united nations secretary general"),
        (5, r"democrats?|republicans?|conservatives?|labour party|labor party|liberal party|democratic party|republican party|party leadership|political campaign"),
        (6, r"war|warfare|armed conflict|invasion|invaded|invading|military offensive|military operation|airstrikes?|air strikes?|bombardment|shelling|artillery fire|troops?|soldiers?|battlefields?|battle|battles|combat|front lines?|ceasefires?|peace talks|peace agreement"),
        (6, r"missiles?|rockets? (?:hit|struck|fired|attacked)|bombs?|bombings?|suicide bombers?|explosions?|explosives?|gunmen|gunman|gunfire|shootings?|firing shots|hostages?|kidnapp(?:ed|ing|ers?)|abduct(?:ed|ion|ors?)"),
        (6, r"terrorism|terrorists?|terror attacks?|extremists?|militants?|insurgents?|insurgency|rebels?|rebel forces|guerrillas?|jihadists?|al qaeda|islamic state|isis|isil|hamas|hezbollah|taliban"),
        (5, r"armed forces|military|army|navy|air force|defen[cs]e ministry|defen[cs]e minister|pentagon|national security|nato|security forces|occupation forces"),
        (5, r"diplomacy|diplomatic|diplomats?|ambassadors?|foreign affairs|foreign policy|international relations|bilateral talks|summit meeting|state visit|united nations|un security council|security council|human rights"),
        (5, r"police|law enforcement|detectives?|prosecutors?|prosecution|charged with|criminal charges|arrest(?:ed|s)?|custody|prison|prisoners?|jail|jail(?:ed)?|sentenced|convicted|conviction|murder|murdered|homicide|manslaughter|rape|raped|robbery|robbers?|stabbing|stabbed|criminal investigation"),
        (5, r"earthquakes?|tsunamis?|hurricanes?|typhoons?|cyclones?|tornado(?:es|s)?|floods?|flooding|floodwaters?|landslides?|mudslides?|avalanches?|volcanic eruptions?|wildfires?|forest fires?|drought|natural disaster"),
        (4, r"dead|deaths?|died|killed|fatalities|fatality|injured|injuries|wounded|casualties|victims?|survivors?|rescue workers?|emergency services|evacuated|evacuation|missing persons?"),
        (4, r"refugees?|asylum seekers?|displaced people|displaced persons|humanitarian crisis|humanitarian aid|famine|starvation|food aid|aid workers?"),
        (4, r"protests?|protesters?|demonstrations?|demonstrators?|riots?|rioting|uprising|civil unrest|crackdown|martial law|coup|overthrown"),
        (4, r"immigration|immigrants?|border security|deportations?|deported|asylum|citizenship law"),
        (4, r"supreme court|constitutional court|constitutional amendment|civil rights|legislation|legislative|bill passed|new law|court ruling|judges?|judiciary"),
        (3.5, r"public health emergency|epidemic|pandemic|disease outbreak|virus outbreak|outbreak of|quarantine|health officials?|health ministry|health minister"),
        (2, r"iraq|afghanistan|ukraine|gaza|west bank|syria|north korea|middle east|israel|palestinians?|palestine|iran"),
    ]),
}

TECH_COMPANIES = re.compile(
    r"(?<![a-z0-9])(?:microsoft|google|ibm|intel|nvidia|amd|qualcomm|"
    r"cisco|samsung|sony|huawei|nokia|motorola|dell|adobe|salesforce|"
    r"facebook|instagram|whatsapp|tiktok|bytedance|twitter|linkedin|"
    r"ebay|paypal|yahoo|aol|lycos|netflix|spotify|alibaba|tencent|"
    r"baidu|broadcom|tsmc|openai|anthropic|apple inc|meta platforms|"
    r"alphabet inc|oracle corp|amazon\.com)(?![a-z0-9])"
)

BUSINESS_CONTEXT = re.compile(
    r"\b(?:earnings|revenue|profit|sales|shares|stock|investors|"
    r"merger|acquisition|acquire|acquired|lawsuit|sued|antitrust|"
    r"quarter|quarterly|billion|million|company|companies|ceo|deal)\b"
)

RESEARCH_CONTEXT = re.compile(
    r"\b(?:research|researchers|scientists|scientific|study|studies|"
    r"clinical|trial|trials|laboratory|discovery|findings|experiment|"
    r"experimental|journal|evidence)\b"
)

HEALTH_CONTEXT = re.compile(
    r"\b(?:medical|medicine|health|patients|disease|cancer|drug|drugs|"
    r"vaccine|vaccines|treatment|therapy|virus|viruses|infection|"
    r"genetic|gene|genes|brain|heart|cells|blood)\b"
)

OUTBREAK_CONTEXT = re.compile(
    r"\b(?:outbreak|epidemic|pandemic|quarantine|"
    r"health officials|health ministry|health minister)\b"
)

SPORTS_CONTEXT = re.compile(
    r"\b(?:team|teams|game|games|match|matches|league|season|"
    r"tournament|coach|player|players|championship|final|finals|"
    r"football|soccer|baseball|basketball|hockey|tennis|cricket)\b"
)

SCORE_PATTERN = re.compile(
    r"(?<!\d)\d{1,3}\s*[-:]\s*\d{1,3}(?!\d)"
)


def _score_features(text, lead, features):
    score = 0.0
    for weight, pattern in features:
        first = pattern.search(text)
        if not first:
            continue
        score += weight
        if pattern.search(lead):
            score += weight * 0.3
        # Reward distinct corroborating terms, but do not let repeated words
        # in a long article overwhelm the other signals.
        distinct = set()
        for match in pattern.finditer(text):
            distinct.add(match.group())
            if len(distinct) >= 3:
                break
        if len(distinct) > 1:
            score += weight * 0.15 * (len(distinct) - 1)
    return score


def predict(state):
    text = state if isinstance(state, str) else ""
    text = text.casefold()
    text = text.replace("\u2019", "'").replace("\u2013", "-").replace("\u2014", "-")
    lead = text[:160]

    scores = {
        category: _score_features(text, lead, features)
        for category, features in FEATURES.items()
    }

    tech_company = bool(TECH_COMPANIES.search(text))

    if re.search(r"\bapple\b", text):
        fruit_context = re.search(r"\b(?:orchard|fruit|apples|cider|harvest)\b", text)
        if not fruit_context or re.search(r"\b(?:iphone|ipad|macbook|software|ceo|shares|earnings)\b", text):
            scores["sci_tech"] += 10
            tech_company = True

    if re.search(r"\bamazon\b", text):
        geographic = re.search(r"\b(?:rainforest|rain forest|river|basin|jungle|indigenous|deforestation)\b", text)
        commercial = re.search(r"\b(?:company|retailer|online|cloud|aws|web services|shares|earnings|ceo|kindle)\b", text)
        if commercial or not geographic:
            scores["sci_tech"] += 9
            tech_company = True

    if re.search(r"\bmeta\b", text) and re.search(
        r"\b(?:facebook|instagram|social media|platforms|zuckerberg|shares|earnings)\b", text
    ):
        scores["sci_tech"] += 9
        tech_company = True

    if re.search(r"\boracle\b", text) and re.search(
        r"\b(?:software|database|company|corporation|shares|earnings|ellison|acquisition)\b", text
    ):
        scores["sci_tech"] += 9
        tech_company = True

    if tech_company and BUSINESS_CONTEXT.search(text):
        scores["sci_tech"] += 5

    if RESEARCH_CONTEXT.search(text) and HEALTH_CONTEXT.search(text):
        scores["sci_tech"] += 5

    if OUTBREAK_CONTEXT.search(text) and not RESEARCH_CONTEXT.search(text):
        scores["world"] += 3

    if SCORE_PATTERN.search(text) and SPORTS_CONTEXT.search(text):
        scores["sports"] += 5

    if re.search(
        r"\b(?:computer|software|internet|email|e mail|screensaver|"
        r"password|passwords|malware|cyber)\b", text
    ) and re.search(r"\b(?:virus|viruses|worm|worms|trojan)\b", text):
        scores["sci_tech"] += 5

    if re.search(r"\b(?:stock market|wall street|shares|stocks|futures)\b", text) and re.search(
        r"\b(?:rose|fell|rallied|slumped|trading|investors|index|indexes|indices)\b", text
    ):
        scores["business"] += 4

    scores["world"] += 0.1
    category = max(("world", "business", "sci_tech", "sports"), key=scores.get)
    return {"answer": category}