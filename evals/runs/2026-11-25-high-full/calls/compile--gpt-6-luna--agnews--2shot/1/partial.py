import re

CATEGORIES = ("business", "sci_tech", "sports", "world")

TERMS = {
    "business": [
        ("stock market", 3.2), ("stock markets", 3.2), ("share price", 2.8),
        ("oil prices", 2.8), ("crude oil", 2.8), ("earnings report", 3.0),
        ("gross domestic product", 3.0), ("interest rates", 2.4),
        ("exchange rate", 2.4), ("mergers and acquisitions", 3.2),
        ("initial public offering", 3.0), ("quarterly results", 2.6),
        ("stock", 1.8), ("stocks", 2.0), ("shares", 1.8), ("market", 1.4),
        ("markets", 1.6), ("earnings", 2.2), ("revenue", 2.0),
        ("profit", 1.8), ("profits", 1.8), ("loss", 1.3), ("losses", 1.5),
        ("investor", 1.7), ("investors", 1.7), ("trading", 1.5),
        ("trader", 1.5), ("traders", 1.5), ("economy", 2.0),
        ("economic", 1.1), ("inflation", 1.8), ("recession", 2.0),
        ("unemployment", 1.7), ("oil", 1.8), ("barrel", 1.8),
        ("commodity", 1.8), ("commodities", 1.8), ("gasoline", 1.5),
        ("fuel prices", 1.8), ("bank", 1.3), ("banks", 1.4),
        ("banking", 1.6), ("mortgage", 1.8), ("currency", 1.7),
        ("dollar", 1.0), ("yen", 1.3), ("euro", 1.0),
        ("trade", 1.0), ("exports", 1.4), ("imports", 1.4),
        ("retail", 1.8), ("retailer", 1.6), ("retailers", 1.6),
        ("sales", 1.2), ("consumer spending", 2.2), ("merger", 2.2),
        ("acquisition", 2.0), ("acquire", 1.6), ("takeover", 2.0),
        ("company", 0.5), ("companies", 0.5), ("corporate", 0.8),
        ("business", 1.0), ("airline", 1.8), ("airlines", 1.8),
        ("automaker", 1.8), ("automakers", 1.8), ("manufacturer", 1.0),
        ("manufacturing", 1.2), ("factory", 1.0), ("factories", 1.0),
        ("retail sales", 2.0), ("bonds", 1.5), ("bond market", 2.0),
        ("dividend", 1.5), ("bankruptcy", 1.8), ("debt", 1.1),
        ("wages", 1.0), ("labor market", 1.8), ("union", 0.8),
        ("production", 0.8), ("commodity prices", 2.0),
    ],
    "sci_tech": [
        ("computer virus", 3.4), ("computer security", 2.8),
        ("cyber attack", 2.8), ("social media", 2.2),
        ("search engine", 2.2), ("mobile phone", 2.2),
        ("cell phone", 2.2), ("smart phone", 2.4), ("smartphone", 2.4),
        ("artificial intelligence", 2.8), ("machine learning", 2.4),
        ("video game", 2.5), ("video games", 2.5), ("space shuttle", 2.6),
        ("space station", 2.4), ("climate change", 1.8),
        ("clinical trial", 2.6), ("medical research", 2.6),
        ("scientific study", 2.2), ("technology company", 2.5),
        ("tech company", 2.4), ("personal computer", 2.4),
        ("operating system", 2.4), ("computer network", 2.4),
        ("internet", 2.1), ("web site", 1.8), ("website", 1.8),
        ("online", 1.2), ("software", 2.4), ("hardware", 2.2),
        ("computer", 2.0), ("computers", 2.0), ("virus", 2.0),
        ("malware", 2.8), ("ransomware", 2.8), ("spyware", 2.8),
        ("phishing", 2.5), ("hacker", 2.2), ("hackers", 2.2),
        ("cyber", 2.2), ("password", 1.4), ("passwords", 1.4),
        ("email", 1.3), ("e-mail", 1.3), ("internet", 2.1),
        ("telecom", 2.2), ("telecommunications", 2.2), ("wireless", 2.0),
        ("broadband", 2.0), ("network", 1.1), ("chip", 2.0),
        ("chips", 2.0), ("processor", 2.0), ("semiconductor", 2.2),
        (" smartphone", 2.4), ("database", 1.8), ("digital", 1.0),
        ("robot", 2.0), ("robotics", 2.0), ("satellite", 1.8),
        ("nasa", 2.5), ("astronomy", 2.0), ("space", 1.4),
        ("scientist", 1.5), ("scientists", 1.5), ("research", 1.2),
        ("laboratory", 1.6), ("lab", 1.0), ("invention", 1.7),
        ("device", 1.0), ("gadget", 1.8), ("technology", 2.4),
        ("tech", 1.8), ("television", 0.9), ("console", 1.5),
        ("playstation", 2.7), ("xbox", 2.7), ("nintendo", 2.7),
        ("microsoft", 2.7), ("google", 2.7), ("apple", 2.2),
        ("ibm", 2.7), ("intel", 2.7), ("oracle", 2.4),
        ("amazon", 2.0), ("yahoo", 2.4), ("lycos", 2.4),
        ("facebook", 2.5), ("twitter", 2.0), ("samsung", 2.2),
        ("sony", 2.2), ("huawei", 2.2), ("nokia", 2.2),
        ("qualcomm", 2.5), ("dell", 2.2), ("hewlett-packard", 2.4),
        ("hp", 1.8), ("virus protection", 2.8), ("keystroke", 1.8),
        ("keystrokes", 1.8), ("biotechnology", 2.2), ("genetic", 1.4),
        ("gene", 1.3), ("genes", 1.3), ("drug trial", 2.0),
        ("vaccine", 1.7), ("medical", 1.2), ("medicine", 1.0),
        ("disease", 0.8), ("researchers", 1.3), ("study", 0.5),
    ],
    "sports": [
        ("world cup", 3.0), ("olympic games", 3.2), ("champions league", 3.0),
        ("premier league", 2.8), ("national football league", 3.2),
        ("major league baseball", 3.2), ("nba finals", 3.0),
        ("the match", 1.4), ("scores", 1.6), ("score", 1.4),
        ("football", 2.4), ("soccer", 2.6), ("basketball", 2.5),
        ("baseball", 2.5), ("hockey", 2.4), ("tennis", 2.5),
        ("golf", 2.2), ("rugby", 2.5), ("cricket", 2.5),
        ("athlete", 2.0), ("athletes", 2.0), ("team", 1.2),
        ("teams", 1.2), ("league", 1.8), ("tournament", 2.0),
        ("championship", 2.0), ("champion", 1.8), ("playoff", 2.0),
        ("playoffs", 2.0), ("final", 1.0), ("finals", 1.5),
        ("coach", 1.4), ("manager", 0.8), ("stadium", 1.7),
        ("goal", 1.5), ("goals", 1.5), ("goalkeeper", 2.0),
        ("touchdown", 2.5), ("quarterback", 2.5), ("pitcher", 2.2),
        ("innings", 2.0), ("home run", 2.2), ("kickoff", 2.0),
        ("defeated", 1.8), ("beat", 1.0), ("victory", 1.5),
        ("defeat", 1.5), ("won", 1.0), ("lost", 0.8),
        ("draw", 0.8), ("transfer", 1.4), ("transfers", 1.5),
        ("athletics", 1.6), ("race", 1.0), ("racing", 1.3),
        ("grand prix", 2.2), ("formula one", 2.7), ("f1", 2.0),
        ("boxing", 2.2), ("wrestling", 1.8), ("medal", 1.8),
        ("medals", 1.8), ("season", 0.8), ("referee", 1.7),
        ("championships", 2.0), ("nba", 2.5), ("nfl", 2.5),
        ("mlb", 2.5), ("nhl", 2.5), ("fifa", 2.5),
    ],
    "world": [
        ("prime minister", 2.4), ("foreign minister", 2.6),
        ("united nations", 2.3), ("security council", 2.5),
        ("human rights", 1.8), ("cease-fire", 2.6), ("ceasefire", 2.6),
        ("peace talks", 2.5), ("peace agreement", 2.5),
        ("general election", 2.6), ("presidential election", 2.8),
        ("election campaign", 2.2), ("military coup", 2.8),
        ("civil war", 2.8), ("suicide bombing", 2.8),
        ("car bomb", 2.6), ("bomb attack", 2.6), ("natural disaster", 2.6),
        ("earthquake", 2.4), ("hurricane", 2.2), ("flooding", 1.8),
        ("armed forces", 2.0), ("troop withdrawal", 2.4),
        ("government forces", 2.0), ("political party", 1.7),
        ("president", 1.8), ("presidential", 1.5), ("government", 1.5),
        ("minister", 1.5), ("parliament", 2.0), ("congress", 1.3),
        ("election", 2.0), ("elections", 2.1), ("vote", 1.2),
        ("voting", 1.5), ("political", 1.3), ("politics", 1.5),
        ("diplomat", 1.8), ("diplomats", 1.8), ("diplomatic", 1.6),
        ("foreign policy", 2.2), ("sanctions", 1.7), ("treaty", 1.8),
        ("war", 2.0), ("troops", 1.8), ("military", 1.7),
        ("soldier", 1.5), ("soldiers", 1.5), ("army", 1.2),
        ("conflict", 1.8), ("violence", 1.5), ("terrorist", 2.0),
        ("terrorism", 2.0), ("bombing", 2.0), ("bomb", 1.3),
        ("attack", 1.2), ("killed", 1.6), ("killings", 1.8),
        ("murder", 1.8), ("murdered", 1.8), ("police", 1.4),
        ("arrested", 1.4), ("arrest", 1.3), ("kidnap", 1.8),
        ("kidnapped", 1.8), ("hostage", 1.8), ("hostages", 1.8),
        ("crime", 1.2), ("criminal", 1.0), ("court", 0.7),
        ("judge", 0.8), ("trial", 0.7), ("protest", 1.6),
        ("protests", 1.7), ("demonstration", 1.4), ("riot", 1.6),
        ("refugee", 1.7), ("refugees", 1.7), ("immigration", 1.2),
        ("border", 0.9), ("country", 0.5), ("countries", 0.5),
        ("international", 0.7), ("minister", 1.5), ("officials", 0.5),
        ("disaster", 1.7), ("earthquake", 2.4), ("tsunami", 2.5),
        ("volcano", 1.8), ("flood", 1.7), ("wildfire", 1.8),
        ("crash", 0.9), ("plane crash", 2.1), ("outbreak", 1.4),
        ("epidemic", 1.8), ("pandemic", 1.8), ("death toll", 1.8),
        ("injured", 0.8), ("injuries", 0.8), ("killing", 1.5),
        ("supreme court", 1.2), ("corruption", 1.6),
        ("referendum", 2.0), ("regime", 1.5), ("opposition", 1.0),
        ("rebel", 1.5), ("rebels", 1.7), ("insurgent", 1.6),
        ("insurgents", 1.7), ("peacekeepers", 2.0), ("embassy", 1.5),
        ("drought", 1.5), ("aid workers", 1.5), ("humanitarian", 1.0),
    ],
}

COMPILED_TERMS = {
    category: [
        (re.compile(r"(?<!\w)" + re.escape(term.strip()).replace(r"\ ", r"\s+") + r"(?!\w)"), weight)
        for term, weight in entries
    ]
    for category, entries in TERMS.items()
}

def _category_scores(text):
    scores = {category: 0.0 for category in CATEGORIES}
    for category, entries in COMPILED_TERMS.items():
        for pattern, weight in entries:
            matches = pattern.findall(text)
            if matches:
                scores[category] += weight * min(len(matches), 4)
    return scores

def predict(state) -> dict:
    if isinstance(state, str):
        text = state
    else:
        text = str(state)
    text = text.lower()
    title = text[:240]

    scores = _category_scores(text)
    title_scores = _category_scores(title)
    for category in CATEGORIES:
        scores[category] += title_scores[category] * 0.55

    # Prefer the category with the strongest topic-specific evidence.
    # World is the residual category when the text has no stronger
    # business, science/technology, or sports signal.
    answer = max(CATEGORIES, key=lambda category: scores[category])
    return {"answer": answer}