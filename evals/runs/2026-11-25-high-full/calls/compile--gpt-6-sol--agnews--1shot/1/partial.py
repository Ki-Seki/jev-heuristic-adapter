import re
import unicodedata

_CUES = {
    "sports": {
        7.5: """
            olympics?|olympians?|paralympics?|fifa|uefa|nfl|nba|mlb|nhl|ncaa|
            world cup|super bowl|world series|champions league|premier league|
            grand slam|grand prix|tour de france|wimbledon|stanley cup|
            formula one|formula 1|nascar|pga tour|atp tour|wta tour|
            red sox|white sox|new york yankees|new york mets|los angeles lakers|
            boston celtics|manchester united|manchester city|real madrid|
            bayern munich|borussia dortmund|ac milan|inter milan|
            roger federer|rafael nadal|serena williams|venus williams|
            tiger woods|lebron james|kobe bryant|michael phelps|
            michael schumacher|lionel messi|cristiano ronaldo|
            david beckham|tom brady|sachin tendulkar
        """,
        5.2: """
            football|soccer|basketball|baseball|cricket|hockey|tennis|
            rugby|volleyball|badminton|boxing|wrestling|golf|golfers?|
            athletes?|quarterbacks?|pitchers?|strikers?|goalkeepers?|
            touchdowns?|home runs?|strikeouts?|wickets?|penalty shootouts?|
            playoffs?|championships?|tournaments?|semifinals?|quarterfinals?|
            referees?|coaches?|stadiums?|medals?|gold medal|
            chelsea|arsenal|liverpool|tottenham|barcelona|juventus|
            patriots|packers|steelers|lakers|celtics|yankees|dodgers|
            mets|cubs|pistons|mavericks|knicks|bulls|ravens|
            marathons?|triathlons?|gymnastics|motorsport|motor racing
        """,
        3.0: """
            sports?|matches?|leagues?|teams?|players?|champions?|
            finals?|finalists?|scored|scoring|goals?|tackles?|batters?|
            bowlers?|innings?|rallies|rally|sprints?|swimmers?|skiers?|
            cycling|cyclists?|races?|racing|runners?|season opener|
            transfer window|transfer fee|free agent|draft picks?|
            rosters?|fixtures?|kickoff|kick off|red card|yellow card|
            hat trick|knockout|heavyweight|welterweight|title fight|
            seeded|seeding|defending champion|points table
        """,
        1.15: """
            games?|wins?|won|loses?|lost|defeats?|beats?|victory|
            victories|season|titles?|clubs?|fans?|draws?|squads?|
            competition|competitors?|rounds?|score|scores|playing|played
        """,
    },
    "sci_tech": {
        8.0: """
            microsoft|google|alphabet inc|ibm|intel|nvidia|amd|apple|
            iphone|ipad|ipod|macintosh|macbook|windows|linux|android|
            playstation|xbox|nintendo|yahoo|aol|ebay|amazon|oracle|
            cisco|dell|hewlett packard|samsung|nokia|motorola|ericsson|
            blackberry|research in motion|sun microsystems|adobe|
            facebook|instagram|whatsapp|youtube|twitter|netflix|
            tesla|spacex|openai|chatgpt|tiktok|snapchat|qualcomm|
            nasa|space shuttle|international space station|hubble|
            james webb|mars rover|human genome|stem cells?
        """,
        5.2: """
            technology|technologies|software|hardware|computers?|
            smartphones?|cell phones?|mobile phones?|mobile handsets?|
            internet|websites?|web sites?|world wide web|broadband|
            wi fi|wireless networks?|semiconductors?|microchips?|
            processors?|laptops?|desktops?|tablets?|data centers?|
            artificial intelligence|machine learning|virtual reality|
            cybersecurity|cyber attacks?|cyberattacks?|hacking|hackers?|
            spyware|malware|ransomware|computer virus|trojan horse|
            video games?|gaming consoles?|video game consoles?|
            operating systems?|search engines?|e commerce|
            telecommunications?|telecoms?|fiber optics?|
            spacecraft|space probes?|astronauts?|asteroids?|telescope|
            satellites?|planets?|galaxies|galaxy|genomes?|
            biotechnology|biotech|clinical trials?|medical research|
            scientific research|scientists?|physicists?|astronomers?
        """,
        3.0: """
            online|digital|electronic|electronics|devices?|gadgets?|
            browsers?|downloads?|downloaded|uploads?|email|e mail|
            spam|passwords?|keystrokes?|screensavers?|webcams?|
            websites?|apps?|applications?|databases?|servers?|
            networks?|programmers?|programming|developers?|
            patents?|inventions?|robotics?|robots?|drones?|
            chips?|microprocessors?|personal computers?|
            mobile internet|text messages?|bluetooth|smartwatches?|
            3d printing|4g|5g|streaming|social media|
            studies|study|researchers?|research|experiments?|
            discoveries|discovery|laboratories|laboratory|
            medicines?|medical|diseases?|cancer|diabetes|hiv|aids|
            vaccines?|vaccinations?|viruses?|genetic|genes?|dna|
            drugs?|treatments?|therapies|patients?|diagnosis|
            antibiotics?|infections?|solar system|lunar|orbiting|
            moon landing|rocket launch|space exploration
        """,
        1.2: """
            science|scientific|health|doctors?|physicians?|hospitals?|
            computers?|phones?|mobile|web|space|moon|mars|solar|
            probes?|launches?|launched|tests?|testing|innovation|
            innovations?|platforms?|systems?|privacy|security
        """,
    },
    "business": {
        7.0: """
            stock markets?|wall street|dow jones|nasdaq|s p 500|
            federal reserve|central bank|interest rates?|gross domestic product|
            world trade organization|international monetary fund|
            opec|crude oil|oil prices?|natural gas prices?|
            initial public offering|stock exchange|
            bankruptcy|bankruptcies|unemployment rate|
            general motors|volkswagen|wal mart|walmart|
            goldman sachs|morgan stanley|bank of america|
            jpmorgan|jp morgan|citigroup|hsbc|barclays|
            exxon mobil|exxonmobil|chevron|royal dutch shell|
            british airways|american airlines|united airlines|
            coca cola|procter gamble
        """,
        5.0: """
            stocks?|shares?|shareholders?|investors?|investment banks?|
            inflation|recessions?|economies|economy|economic growth|
            gross domestic product|gdp|oil|petroleum|airlines?|
            mergers?|acquisitions?|takeovers?|buyouts?|ipos?|
            commodities|currency markets?|foreign exchange|
            trade deficit|trade surplus|bond markets?|
            retail sales|quarterly earnings|quarterly profits?|
            boeing|airbus|ford motor|toyota|chrysler|honda|
            pfizer|merck|disney|mcdonalds|starbucks|
            walmart|general electric|ge capital|
            unemployment|jobless claims?
        """,
        3.0: """
            earnings?|profits?|revenues?|quarterly|sales|retailers?|
            retailers?|retail|banks?|banking|lenders?|loans?|
            mortgages?|traders?|trading|bonds?|treasurys?|treasuries|
            currencies|dollars?|euros?|yen|exports?|imports?|tariffs?|
            commerce|businesses?|companies|company|corporations?|
            ceos?|executives?|industries|industry|manufacturers?|
            factories|production|consumers?|consumer spending|
            prices?|pricing|financial|finances?|fiscal|
            markets?|merchandise|aircraft makers?|automakers?|
            carmakers?|vehicles?|car sales|airfares?|
            airlines?|flights?|oilfields?|refineries|
            miners?|mining|coal|steel|copper|gold prices?|
            acquisitions?|buying|selling|dividends?|
            layoffs?|workforces?|wages?|pensions?|employment|
            budget deficit
        """,
        1.15: """
            businesses?|firms?|corporate|commercial|costs?|growth|
            billions?|millions?|deal|deals|contracts?|spending|
            demand|supply|prices?|manufacturing|factory|budgets?|
            forecasts?|forecasts|rose|fell|rises?|falls?|higher|
            lower|increases?|declines?
        """,
    },
    "world": {
        7.0: """
            prime ministers?|white house|united nations|security council|
            state department|foreign ministers?|secretary of state|
            presidential elections?|general elections?|
            military coups?|civil wars?|terrorist attacks?|
            suicide bombings?|al qaeda|al qaida|islamic state|
            taliban|nato|un peacekeepers?|
            earthquakes?|tsunamis?|hurricanes?|typhoons?|
            george w bush|barack obama|donald trump|joe biden|
            vladimir putin|saddam hussein|osama bin laden
        """,
        5.2: """
            governments?|presidents?|parliaments?|congress|
            senators?|senates?|governors?|politicians?|political|
            elections?|ballots?|candidates?|campaigns?|
            diplomacy|diplomats?|embassies|ambassadors?|
            militaries|military|armies|army|troops?|soldiers?|
            invasions?|air strikes?|airstrikes?|bombings?|
            bombs?|explosions?|terrorists?|terrorism|
            insurgents?|insurgencies|rebels?|militants?|
            wars?|warfare|ceasefires?|hostages?|refugees?|
            conflicts?|peace talks?|nuclear weapons?|
            police|murders?|homicides?|kidnappings?|arrested|
            arrests?|convicted|sentenced|shootings?|
            killed|deaths?|fatalities|disasters?|floods?|
            wildfires?|tornadoes?|volcanic eruptions?
        """,
        3.0: """
            ministers?|officials?|lawmakers?|legislation|laws?|
            votes?|voting|polls?|opposition|democracy|
            protests?|protesters?|riots?|demonstrators?|
            human rights|sanctions?|treaties|summits?|
            ceasefire|peacekeeping|border|immigration|
            missiles?|weapons?|gunfire|gunmen|gunman|
            prisoners?|detained|detention|courts?|judges?|
            trials?|guilty|crimes?|criminal|charges?|
            injured|wounded|casualties|violence|assault|
            earthquakes?|storms?|evacuated|evacuations?|
            emergencies|displaced|humanitarian|
            iraq|baghdad|afghanistan|kabul|gaza|taliban|
            palestine|palestinian|israeli|syria|ukraine|
            north korea|pyongyang|tehran
        """,
        1.0: """
            international|foreign|national|nations?|countries|country|
            leaders?|authorities|citizens?|attacks?|fighting|
            killed|dead|policies|public|crisis|iraqi|afghan|
            iran|israel|russia|china|pakistan|lebanon|sudan|
            britain|france|germany|japan
        """,
    },
}

def _compile_cues():
    compiled = {}
    for category, tiers in _CUES.items():
        entries = []
        for weight, vocabulary in tiers.items():
            for term in vocabulary.split("|"):
                term = term.strip()
                if term:
                    pattern = term.replace(" ", r"\s+")
                    entries.append((weight, re.compile(r"(?<![a-z0-9])(?:" + pattern + r")(?![a-z0-9])")))
        compiled[category] = entries
    return compiled

_PATTERNS = _compile_cues()

def _text_from_state(state):
    if isinstance(state, str):
        return state
    if isinstance(state, dict):
        for key in ("text", "article", "content", "news"):
            value = state.get(key)
            if isinstance(value, str):
                return value
        return " ".join(
            state[key] for key in ("title", "headline", "description", "body")
            if isinstance(state.get(key), str)
        )
    return ""

def predict(state) -> dict:
    text = _text_from_state(state)
    normalized = unicodedata.normalize("NFKD", text).lower()
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized).strip()
    if not normalized:
        return {"answer": "world"}

    scores = {"business": 0.0, "sci_tech": 0.0, "sports": 0.0, "world": 0.3}
    strong = {category: 0 for category in scores}

    for category, entries in _PATTERNS.items():
        for weight, pattern in entries:
            match = pattern.search(normalized)
            if match is not None:
                scores[category] += weight * (1.35 if match.start() < 105 else 1.0)
                if weight >= 5:
                    strong[category] += 1

    def has(pattern):
        return re.search(pattern, normalized) is not None

    tech_company = has(
        r"\b(?:microsoft|google|ibm|intel|nvidia|amd|apple|amazon|"
        r"oracle|cisco|dell|yahoo|ebay|samsung|nokia|motorola|"
        r"sony|nintendo|facebook|netflix|tesla|qualcomm|adobe|"
        r"salesforce|hp|hewlett packard|blackberry)\b"
    )
    financial = has(
        r"\b(?:earnings?|profits?|revenues?|shares?|stocks?|"
        r"sales|quarterly|investors?|acquisitions?|mergers?)\b"
    )
    if tech_company:
        scores["sci_tech"] += 5.0
        if financial:
            scores["sci_tech"] += 3.0

    if has(r"\b(?:video games?|computer games?|gaming consoles?)\b"):
        scores["sports"] -= 3.5
    if has(r"\b(?:software|media|music|video|computer)\s+players?\b"):
        scores["sports"] -= 3.0
    if has(r"\b(?:computer|email|e mail|internet|cyber)\s+viruses?\b"):
        scores["sci_tech"] += 5.0
    if has(r"\b(?:company|corporate|bank|firm)\s+presidents?\b"):
        scores["business"] += 4.0
        scores["world"] -= 2.0
    if has(r"\b(?:presidents?|prime ministers?|governments?)\b") and has(
        r"\b(?:elections?|parliaments?|voters?|troops?|war|summit)\b"
    ):
        scores["world"] += 3.0
    if has(r"\b(?:research|researchers?|scientists?|study|clinical trials?)\b") and has(
        r"\b(?:diseases?|viruses?|vaccines?|patients?|drugs?|"
        r"treatments?|genes?|cancer|medicine|health)\b"
    ):
        scores["sci_tech"] += 4.0
    if has(r"\b(?:matches?|teams?|players?|athletes?|leagues?)\b") and has(
        r"\b(?:wins?|won|defeats?|beats?|scored|goals?|"
        r"championships?|tournaments?)\b"
    ):
        scores["sports"] += 3.0

    priority = ("sci_tech", "sports", "business", "world")
    answer = max(priority, key=lambda category: (scores[category], strong[category]))
    return {"answer": answer}