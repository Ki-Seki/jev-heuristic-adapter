import re
import unicodedata

CATEGORY_TERMS = {
    "sports": [
        (r"\bsports?\b", 2.5), (r"\b(match|game|fixture|tournament|championship|playoffs?)\b", 2.0),
        (r"\b(score|scored|goal|goals|touchdown|home run|hat[- ]trick)\b", 2.5),
        (r"\b(league|coach|manager|referee|captain|athlete|team|club)\b", 1.5),
        (r"\b(win|wins|won|lose|loses|lost|draw|draws|defeat|defeats)\b", 1.2),
        (r"\b(football|soccer|baseball|basketball|hockey|tennis|golf|rugby|cricket|boxing|g?mma|volleyball|formula one|f1)\b", 2.2),
        (r"\b(nfl|nba|mlb|nhl|wnba|fifa|uefa|olympics?|world cup|premier league)\b", 3.0),
        (r"\b(traded|transfer|transferred|drafted|signed|free agent|season opener|quarterback|pitcher|striker)\b", 1.8),
    ],
    "sci_tech": [
        (r"\b(technology|tech|scientist|science|research|study|discovery|experiment|clinical trial)\b", 1.7),
        (r"\b(software|hardware|internet|online|website|web|app|application|smartphone|mobile phone|computer|laptop|server|cloud computing)\b", 2.2),
        (r"\b(artificial intelligence|machine learning|generative ai|robot|robotics|algorithm|cybersecurity|data breach|encryption)\b", 2.8),
        (r"\b(chip|processor|semiconductor|microchip|quantum computing|operating system|source code|open source)\b", 2.4),
        (r"\b(satellite|spacecraft|rocket| nasa |astronaut|orbit|mars mission|telescope|planet|space exploration)\b", 2.0),
        (r"\b(telecom|telecommunications|broadband|wireless|5g|6g|fiber optic|mobile network|video game|gaming console)\b", 2.0),
        (r"\b(vaccine|medical research|gene therapy|genome|biotechnology|drug trial|cancer research|public health study)\b", 1.8),
        (r"\b(microsoft|google|alphabet|apple|ibm|intel|nvidia|amd|qualcomm|meta platforms|facebook|amazon|tesla|samsung|sony|oracle|adobe|openai|tiktok|netflix|uber|airbnb)\b", 1.5),
        (r"\b(iphone|ipad|macbook|windows|android|pixel phone|playstation|xbox|chatgpt|youtube|instagram|whatsapp)\b", 2.5),
        (r"\b(launched|unveiled|released|updates|upgrade|patent|data center|search engine|social media platform)\b", 0.8),
    ],
    "business": [
        (r"\b(stock market|share market|stock exchange|wall street|stocks|shares|equities|bond market|investors?)\b", 2.5),
        (r"\b(earnings|revenue|profits?|losses|quarterly results|annual results|sales figures|dividend|shareholders?)\b", 2.2),
        (r"\b(economy|economic|inflation|recession|interest rates?|central bank|federal reserve|fed policy|unemployment|gdp|currency|exchange rate)\b", 2.2),
        (r"\b(oil|crude|natural gas|commodit(?:y|ies)|gold prices?|copper prices?|wheat prices?|energy prices?)\b", 2.0),
        (r"\b(trade deal|tariffs?|exports?|imports?|supply chain|merger|acquisition|takeover|bankruptcy|ipo|buyback)\b", 2.0),
        (r"\b(company|companies|business|businesses|corporate|firm|firms|industry|industries|retailer|retail|airline|airlines|manufacturer)\b", 1.2),
        (r"\b(hiring|layoffs?|job cuts|workforce|union contract|consumer spending|housing market|mortgage|bank|banks|lender|lenders)\b", 1.6),
        (r"\b(price|prices|costs?|market|markets|deal|contract|investment|investments|entrepreneur|startup)\b", 0.8),
    ],
    "world": [
        (r"\b(president|prime minister|parliament|congress|government|minister|senate|politician|diplomat|state department)\b", 2.0),
        (r"\b(election|elections|vote|voting|ballot|campaign|referendum|polls|coalition|opposition party)\b", 2.4),
        (r"\b(war|conflict|invasion|military|troops|ceasefire|missile|airstrike|bombing|hostage|peace talks|sanctions)\b", 2.5),
        (r"\b(international|foreign affairs|border|embassy|united nations|nato|european union|summit|treaty|diplomatic)\b", 1.8),
        (r"\b(earthquake|hurricane|typhoon|flood|wildfire|landslide|volcano|disaster|evacuation|rescue operation)\b", 2.3),
        (r"\b(murder|killed|killing|dead|death|arrested|police|suspect|crime|criminal|prison|kidnapping|prosecutor|accused)\b", 1.6),
        (r"\b(protest|protests|demonstration|riot|refugee|immigration|asylum|human rights|court ruling|supreme court)\b", 1.6),
        (r"\b(china|russia|ukraine|israel|gaza|iran|iraq|syria|taiwan|afghanistan|north korea|south korea|united states|u\.s\.|britain|france|germany)\b", 0.7),
    ],
}

COMPILED_TERMS = {
    category: [(re.compile(pattern, re.IGNORECASE), weight) for pattern, weight in terms]
    for category, terms in CATEGORY_TERMS.items()
}


def _collect_text(value):
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        parts = []
        for item in value.values():
            parts.extend(_collect_text(item))
        return parts
    if isinstance(value, (list, tuple)):
        parts = []
        for item in value:
            parts.extend(_collect_text(item))
        return parts
    if value is None:
        return []
    if isinstance(value, (int, float, bool)):
        return [str(value)]
    return []


def _score(text):
    scores = {category: 0.0 for category in CATEGORY_TERMS}
    for category, terms in COMPILED_TERMS.items():
        for pattern, weight in terms:
            matches = pattern.findall(text)
            if matches:
                scores[category] += min(len(matches), 3) * weight

    # Earnings and corporate news about technology firms are technology news
    # under the task's definition, while general market reporting remains business.
    tech_company = re.search(
        r"\b(microsoft|google|alphabet|apple|ibm|intel|nvidia|amd|qualcomm|meta platforms|facebook|amazon|tesla|samsung|sony|oracle|adobe|openai|tiktok|netflix)\b",
        text,
        re.IGNORECASE,
    )
    tech_corporate = re.search(
        r"\b(earnings|revenue|profits?|losses|lawsuit|sued|settlement|quarterly results|sales)\b",
        text,
        re.IGNORECASE,
    )
    if tech_company and tech_corporate:
        scores["sci_tech"] += 3.0

    # Strong category-specific clues help short headlines where only one clue appears.
    if re.search(r"\b(score|scored|touchdown|home run|hat[- ]trick|goal|goals)\b", text, re.IGNORECASE):
        scores["sports"] += 1.5
    if re.search(r"\b(election|war|invasion|earthquake|hurricane|ceasefire|president)\b", text, re.IGNORECASE):
        scores["world"] += 1.2
    if re.search(r"\b(stock market|shares rose|shares fell|inflation|interest rates|quarterly earnings|merger)\b", text, re.IGNORECASE):
        scores["business"] += 1.2
    if re.search(r"\b(iphone|artificial intelligence|semiconductor|software update|rocket launch|clinical trial)\b", text, re.IGNORECASE):
        scores["sci_tech"] += 1.2
    return scores


def predict(state) -> dict:
    text = " ".join(_collect_text(state))
    text = unicodedata.normalize("NFKC", text).lower()
    scores = _score(text)

    # On ties, prefer the category with the most distinctive headline cues.
    tie_order = ("sports", "sci_tech", "business", "world")
    best = max(tie_order, key=lambda category: scores[category])
    if scores[best] == 0:
        best = "world"
    return {"answer": best}