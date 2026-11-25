import re
import unicodedata


def _text_from_state(state):
    if isinstance(state, str):
        return state
    if isinstance(state, (list, tuple)):
        return " ".join(_text_from_state(item) for item in state)
    if isinstance(state, dict):
        fields = (
            "title", "headline", "text", "description", "summary",
            "body", "content", "article", "news", "sentence",
            "input", "message", "state",
        )
        parts = []
        seen = set()
        for key in fields:
            if key in state:
                value = _text_from_state(state[key])
                if value and value not in seen:
                    parts.append(value)
                    seen.add(value)
        if parts:
            return " ".join(parts)
        for key, value in state.items():
            if str(key).lower() not in {
                "label", "answer", "category", "class", "id", "source", "url"
            }:
                text = _text_from_state(value)
                if text:
                    parts.append(text)
        return " ".join(parts)
    return ""


def _normalize(text):
    text = unicodedata.normalize("NFKC", text).lower()
    return re.sub(r"[^a-z0-9%$]+", " ", text).strip()


def _make_terms(groups):
    terms = []
    for weight, phrases in groups:
        terms.extend((phrase.strip(), weight) for phrase in phrases.split("|")
                     if phrase.strip())
    return terms


TERMS = {
    "sports": _make_terms([
        (9, "world cup|super bowl|champions league|premier league|"
            "olympic games|olympics|winter olympics|summer olympics|"
            "world series|grand slam|wimbledon|tour de france|"
            "formula one|formula 1|stanley cup|nba finals|"
            "ncaa tournament|european championship|africa cup of nations"),
        (8, "nfl|nba|mlb|nhl|wnba|fifa|uefa|ncaa|nascar|"
            "cricket world cup|championship game|playoffs|"
            "football match|soccer match|tennis match|"
            "gold medal|silver medal|bronze medal"),
        (7, "soccer|football|basketball|baseball|cricket|tennis|"
            "rugby|golf|hockey|volleyball|badminton|boxing|"
            "motogp|grand prix|marathon|athletics|"
            "manchester united|real madrid|barcelona|"
            "bayern munich|liverpool|arsenal|chelsea|"
            "red sox|new york yankees|los angeles lakers|"
            "golden state warriors"),
        (6, "touchdown|quarterback|pitcher|batsman|bowler|"
            "striker|goalkeeper|referee|umpire|hat trick|"
            "penalty shootout|home run|offside|knockout|"
            "semifinal|semi final|quarterfinal|quarter final|"
            "tournament|medals|athlete|athletes|"
            "us open tennis|australian open tennis|"
            "french open tennis|masters tournament"),
        (5, "league|match|matches|season opener|"
            "playoff|finals|championship|champion|"
            "goals|scored|scoring|race winner|"
            "team captain|football club|soccer club|"
            "new york mets|chicago cubs|los angeles dodgers|"
            "dallas cowboys|new england patriots|"
            "green bay packers|boston celtics|"
            "chicago bulls|miami heat|toronto raptors|"
            "serena williams|roger federer|rafael nadal|"
            "novak djokovic|lionel messi|cristiano ronaldo|"
            "lebron james|tiger woods|michael phelps|usain bolt"),
        (4, "coach|coaches|player|players|"
            "stadium|arena|rally driver|"
            "transfer window|fixtures|standings|"
            "medal|defender|midfielder|forward|"
            "inning|innings|wicket|wickets|"
            "game winning|winning streak|"
            "f1|atp|wta|pga|epl|bundesliga|serie a|la liga"),
        (3, "teams|game|games|victory|"
            "defeat|draw|sports|sporting|"
            "racing|racer|sprint|swimming|"
            "cycling|skiing|snowboarding|"
            "practice squad|draft pick|"
            "transfer fee|contract extension"),
        (1.5, "win|wins|won|beat|beats|"
              "loss|lost|fans|season|record|team|"
              "rival|rivals|score|scores"),
    ]),
    "sci_tech": _make_terms([
        (9, "artificial intelligence|machine learning|"
            "space shuttle|space station|international space station|"
            "clinical trial|clinical trials|"
            "scientific study|scientific research|"
            "medical research|computer virus|"
            "video game|video games|"
            "operating system|open source software|"
            "search engine|electric vehicle technology"),
        (8, "microsoft|google|alphabet inc|apple inc|"
            "ibm|intel|nvidia|amd|qualcomm|"
            "oracle corp|amazon com|facebook|meta platforms|"
            "samsung|nokia|motorola|cisco|"
            "sony playstation|nintendo|"
            "spacex|nasa|openai|chatgpt|"
            "android|iphone|ipad|windows xp|"
            "windows vista|windows 10|windows 11|"
            "mac os|macos|linux|youtube|"
            "playstation|xbox|"
            "cybersecurity|semiconductor|semiconductors"),
        (7, "software|computer|computers|internet|"
            "smartphone|smartphones|"
            "microchip|microchips|"
            "chipmaker|chipmakers|"
            "spacecraft|astronaut|astronauts|"
            "telescope|genome|genomics|"
            "scientists|researchers|"
            "scientific discovery|"
            "hubble|mars rover|"
            "broadband|wireless network|"
            "computer security|data breach|"
            "hacker|hackers|hacking|"
            "malware|ransomware"),
        (6, "technology|technologies|tech firms|"
            "tech companies|tech company|"
            "research study|new study|study finds|"
            "experiment|experiments|"
            "research laboratory|laboratory research|"
            "vaccine trial|drug trial|"
            "biotechnology|biotech|"
            "satellite|satellites|"
            "mobile phone|mobile phones|cell phone|cell phones|"
            "web browser|website|websites|"
            "online search|social network|"
            "digital camera|processor|processors|"
            "quantum computing|robotics|robot"),
        (5, "apple|amazon|tesla|netflix|ebay|"
            "yahoo|dell|hewlett packard|hp inc|"
            "blackberry|research in motion|"
            "tiktok|twitter|instagram|"
            "spotify|steam|"
            "app store|apps|"
            "computer game|gaming console|"
            "gaming industry|"
            "hardware|database|"
            "microprocessor|microprocessors|"
            "solar system|planet|planets|"
            "galaxy|galaxies|"
            "physics|chemistry|biology|"
            "genetic|genetics|"
            "stem cells|stem cell|"
            "medical study|"
            "vaccine|vaccines"),
        (4, "online|digital|"
            "electronics|electronic device|"
            "chip|chips|"
            "mobile device|mobile devices|"
            "smartwatch|tablet computer|"
            "web|email|e mail|"
            "wireless|wifi|wi fi|"
            "telecom|telecommunications|"
            "fiber optic|fibre optic|"
            "network equipment|"
            "encryption|privacy software|"
            "data center|cloud computing|"
            "space exploration|rocket launch|"
            "astronomy|cosmos|"
            "scientist|researcher|"
            "researchers discovered|"
            "clinical research|"
            "disease treatment|"
            "drug discovery|"
            "electric cars|self driving cars|"
            "autonomous vehicles"),
        (3, "tech|science|"
            "innovation|invention|"
            "research|discovery|"
            "space|rocket|"
            "software update|"
            "browser|server|servers|"
            "programmer|programming|"
            "developer|developers|"
            "app|"
            "ai|"
            "medical breakthrough|"
            "treatment|"
            "cancer research|"
            "climate research|climate study|"
            "climate change|"
            "electric vehicle|electric vehicles"),
        (1.5, "device|devices|"
              "prototype|"
              "users|download|"
              "online service|"
              "health study|"
              "scientific|"
              "scientists say"),
    ]),
    "business": _make_terms([
        (9, "stock market|stock markets|"
            "wall street|federal reserve|"
            "interest rates|interest rate|"
            "gross domestic product|"
            "oil prices|oil price|"
            "crude oil prices|"
            "quarterly earnings|"
            "trade deficit|"
            "economic growth|"
            "financial markets|"
            "initial public offering|"
            "s p 500|dow jones"),
        (8, "earnings report|"
            "profit forecast|revenue forecast|"
            "share price|share prices|"
            "stock exchange|"
            "nasdaq|"
            "ipo|"
            "merger|mergers|"
            "acquisition|acquisitions|"
            "central bank|"
            "world bank|"
            "international monetary fund|"
            "imf|"
            "opec|"
            "consumer spending|"
            "unemployment rate|"
            "inflation rate"),
        (7, "stocks|shares|"
            "investors|investment bank|"
            "economic recession|"
            "recession|inflation|"
            "commodity prices|"
            "trade agreement|"
            "trade deal|"
            "takeover|buyout|"
            "corporate earnings|"
            "annual profit|"
            "net profit|"
            "quarterly profit|"
            "quarterly revenue|"
            "gross domestic product|"
            "crude oil|"
            "airline industry|"
            "retail sales|"
            "housing market"),
        (6, "economy|economic|"
            "profits|profit|"
            "revenue|"
            "shareholders|shareholder|"
            "trading|traders|"
            "businesses|"
            "financial|finance|"
            "banking|"
            "banks|"
            "investments|"
            "exports|imports|"
            "commodities|"
            "oil futures|"
            "unemployment|"
            "jobless claims|"
            "consumer confidence|"
            "airlines|"
            "retailer|retailers|"
            "real estate|"
            "mortgage rates|"
            "corporate bonds"),
        (5, "stock|"
            "earnings|"
            "investor|"
            "market rally|"
            "market downturn|"
            "bank|"
            "currency|"
            "dollar|euro|yen|"
            "export|import|"
            "trade|"
            "merging|"
            "corporation|"
            "business|"
            "oil industry|"
            "natural gas prices|"
            "airline|"
            "retail|"
            "sales figures|"
            "sales forecast|"
            "auto industry|"
            "automaker|automakers|"
            "manufacturer|manufacturers|"
            "factory output|"
            "economic data|"
            "job growth|"
            "walmart|wal mart|"
            "ford motor|general motors|"
            "toyota|volkswagen|boeing"),
        (4, "market|markets|"
            "companies|company|"
            "industry|industries|"
            "oil|"
            "gasoline|"
            "prices|"
            "employment|"
            "jobs report|"
            "budget deficit|"
            "debt|"
            "bond|bonds|"
            "funds|"
            "insurance|"
            "mortgage|"
            "property prices|"
            "ceo|chief executive|"
            "executives|"
            "retail chain|"
            "supermarket|"
            "store chain|"
            "car sales|"
            "aircraft maker"),
        (2, "deal|deals|"
            "sales|"
            "contract|contracts|"
            "workers|"
            "factory|"
            "enterprise|"
            "commercial|"
            "consumer|"
            "corporate|"
            "price|"
            "jobs|"
            "demand|"
            "supply"),
    ]),
    "world": _make_terms([
        (9, "presidential election|"
            "general election|"
            "prime minister|"
            "white house|"
            "united nations|"
            "security council|"
            "terrorist attack|"
            "suicide bombing|"
            "war crimes|"
            "civil war|"
            "peace talks|"
            "earthquake kills|"
            "hurricane kills|"
            "death toll|"
            "nuclear weapons"),
        (8, "elections|election|"
            "parliament|"
            "government|"
            "president elect|"
            "foreign minister|"
            "secretary of state|"
            "military forces|"
            "armed forces|"
            "terrorism|terrorists|"
            "bombing|"
            "airstrike|airstrikes|"
            "missile strike|"
            "hostages|"
            "refugees|"
            "earthquake|"
            "tsunami|"
            "genocide|"
            "invasion"),
        (7, "politics|political|"
            "diplomacy|diplomatic|"
            "senate|congress|"
            "lawmakers|legislators|"
            "war|warfare|"
            "troops|"
            "soldiers|"
            "rebels|insurgents|"
            "militants|"
            "bomb|bombs|"
            "explosion|"
            "hurricane|"
            "flooding|floods|"
            "wildfires|"
            "disaster|"
            "murder|"
            "kidnapped|kidnapping|"
            "united nations peacekeepers"),
        (6, "minister|"
            "candidate|"
            "ballot|"
            "voters|"
            "vote recount|"
            "peace treaty|"
            "ceasefire|"
            "conflict|"
            "combat|"
            "attack|attacks|"
            "killed|"
            "police|"
            "arrested|"
            "criminal charges|"
            "mass shooting|"
            "protesters|"
            "protests|"
            "sanctions|"
            "evacuated|"
            "storm surge|"
            "natural disaster|"
            "state of emergency"),
        (5, "president|"
            "governor|"
            "mayor|"
            "politician|politicians|"
            "opposition leader|"
            "ruling party|"
            "diplomat|"
            "military|"
            "army|"
            "navy|"
            "weapons|"
            "missile|missiles|"
            "gunmen|"
            "shooting|"
            "fighting|"
            "clashes|"
            "violence|"
            "violent|"
            "police officer|"
            "crime|"
            "criminal|"
            "prison|"
            "sentenced|"
            "convicted|"
            "drought|"
            "wildfire|"
            "tornado|"
            "outbreak|"
            "pandemic|"
            "human rights|"
            "immigration|"
            "asylum seekers"),
        (4, "administration|"
            "cabinet|"
            "legislation|"
            "lawmaker|"
            "congressional|"
            "federal government|"
            "democracy|"
            "referendum|"
            "constitution|"
            "international relations|"
            "border|"
            "occupation|"
            "uprising|"
            "protest|"
            "rally against|"
            "demonstration|"
            "explosives|"
            "detained|"
            "suspect|suspects|"
            "investigation|"
            "trial court|"
            "verdict|"
            "judge|"
            "storm|"
            "famine|"
            "relief workers|"
            "rescue workers|"
            "public health crisis"),
        (2, "officials|"
            "authority|authorities|"
            "court|"
            "law|"
            "policy|"
            "national|"
            "international|"
            "security|"
            "leaders|"
            "leader|"
            "people died|"
            "deaths|"
            "victims|"
            "injured|"
            "iraq|"
            "ukraine|"
            "afghanistan|"
            "israel|"
            "palestinian|"
            "biden|"
            "trump|"
            "obama|"
            "bush|"
            "putin|"
            "zelensky"),
    ]),
}


TECH_COMPANIES = {
    "microsoft", "google", "alphabet inc", "apple inc", "ibm", "intel",
    "nvidia", "amd", "qualcomm", "oracle corp", "amazon com", "facebook",
    "meta platforms", "samsung", "nokia", "motorola", "cisco", "spacex",
    "openai", "nintendo", "sony playstation", "tesla", "netflix", "ebay",
    "yahoo", "dell", "hewlett packard", "hp inc", "blackberry",
    "research in motion", "tiktok", "twitter", "instagram", "spotify",
}
FINANCIAL_COMPANY_NEWS = {
    "earnings", "revenue", "profit", "profits", "shares", "stock",
    "share price", "quarterly", "lawsuit", "sued", "antitrust",
    "settlement", "acquisition", "merger",
}
BROAD_MARKET = {
    "stock market", "stock markets", "wall street", "dow jones",
    "s p 500", "financial markets", "market rally", "market downturn",
    "federal reserve",
}


def _has(padded_text, phrase):
    return (" " + phrase + " ") in padded_text


def predict(state) -> dict:
    text = _normalize(_text_from_state(state)[:12000])
    if not text:
        return {"answer": "world"}

    padded = " " + text + " "
    scores = {}
    for category, terms in TERMS.items():
        scores[category] = sum(
            weight for phrase, weight in terms if _has(padded, phrase)
        )

    tech_company = any(_has(padded, name) for name in TECH_COMPANIES)
    broad_market = any(_has(padded, term) for term in BROAD_MARKET)

    if tech_company and any(
        _has(padded, term) for term in FINANCIAL_COMPANY_NEWS
    ):
        scores["sci_tech"] += 6

    if broad_market:
        scores["business"] += 5

    if re.search(
        r"\b\d+\s+(?:goals|runs|wickets|touchdowns|medals|"
        r"innings|points|sets)\b", text
    ):
        scores["sports"] += 5

    if re.search(r"\b(?:defeated|beat|beats)\b", text):
        if scores["sports"] >= 5:
            scores["sports"] += 3
        elif any(_has(padded, term) for term in
                 ("earnings", "estimates", "forecasts", "expectations")):
            scores["business"] += 2

    if _has(padded, "clinical trial") or _has(padded, "medical research"):
        scores["sci_tech"] += 4
    if _has(padded, "oil spill") or _has(padded, "oil spills"):
        scores["world"] += 7
    if _has(padded, "rocket attack") or _has(padded, "rocket attacks"):
        scores["world"] += 8

    if _has(padded, "amazon rainforest"):
        scores["sci_tech"] -= 5
        scores["world"] += 3
    if any(_has(padded, term) for term in
           ("apple orchard", "apple juice", "apple harvest")):
        scores["sci_tech"] -= 5

    if scores["sports"] >= 7 and scores["sports"] >= max(
        scores["business"], scores["sci_tech"], scores["world"]
    ) - 1:
        answer = "sports"
    else:
        answer = max(
            ("world", "business", "sci_tech", "sports"),
            key=lambda category: scores[category],
        )
    return {"answer": answer}