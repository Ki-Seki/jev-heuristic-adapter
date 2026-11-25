import re

SPORTS_TERMS = {
    "sports": 4, "sport": 4, "match": 3, "matches": 3, "game": 2, "games": 3,
    "team": 2, "teams": 3, "league": 3, "tournament": 3, "championship": 3,
    "athlete": 3, "athletes": 3, "coach": 2, "player": 2, "players": 3,
    "score": 3, "scores": 3, "scored": 3, "victory": 3, "defeat": 3,
    "win": 2, "wins": 3, "won": 2, "lost": 2, "season": 2, "final": 2,
    "goal": 2, "goals": 3, "touchdown": 3, "playoff": 3, "playoffs": 3,
    "cup": 2, "olympics": 4, "olympic": 4, "medal": 2, "medals": 3,
    "tennis": 4, "golf": 4, "cricket": 4, "rugby": 4, "baseball": 4,
    "basketball": 4, "football": 3, "soccer": 4, "hockey": 4, "boxing": 4,
    "race": 2, "racing": 3, "grand prix": 4, "formula one": 4,
    "transfer": 2, "transferred": 2, "relegation": 3, "kickoff": 3,
    "innings": 3, "home run": 3, "world cup": 3, "quarterback": 3,
}

TECH_TERMS = {
    "technology": 3, "tech": 2, "computer": 3, "computers": 3,
    "software": 4, "hardware": 4, "internet": 4, "website": 3,
    "web site": 3, "online": 2, "email": 2, "emails": 2, "e mail": 2,
    "screen saver": 3, "screensaver": 3, "virus": 4, "malware": 5,
    "spyware": 5, "ransomware": 5, "worm": 2, "hacker": 3, "hackers": 3,
    "hacking": 3, "cyber": 3, "cybersecurity": 4, "data breach": 4,
    "password": 2, "passwords": 2, "keystroke": 3, "keystrokes": 3,
    "keylogger": 4, "encryption": 3, "database": 2, "server": 2,
    "servers": 2, "smartphone": 3, "mobile phone": 3, "cellphone": 3,
    "telecom": 4, "telecommunications": 4, "broadband": 3, "wireless": 2,
    "app": 2, "apps": 2, "application": 2, "operating system": 3,
    "browser": 3, "search engine": 3, "social media": 2, "chip": 3,
    "semiconductor": 4, "processor": 3, "robot": 2, "artificial intelligence": 3,
    "video game": 3, "video games": 3, "gaming": 2, "console": 2,
    "screens": 1, "digital": 1, "portal": 2, "internet portal": 3,
    "scientist": 2, "scientists": 2, "scientific": 3, "research": 2,
    "study": 1, "clinical trial": 3, "vaccine": 2, "gene": 2, "genome": 3,
    "medical research": 3, "space": 3, "astronaut": 3, "astronauts": 3,
    "nasa": 4, "satellite": 3, "telescope": 3, "planet": 2, "orbit": 2,
    "microsoft": 4, "google": 4, "apple": 4, "ibm": 4, "intel": 4,
    "oracle": 3, "amazon": 3, "facebook": 3, "meta": 2, "samsung": 3,
    "sony": 3, "nvidia": 4, "cisco": 4, "dell": 3, "hp": 2,
    "lycos": 3, "twitter": 3, "tesla": 3, "netflix": 3,
}

BUSINESS_TERMS = {
    "business": 2, "economy": 3, "economic": 2, "stock": 3, "stocks": 3,
    "stock market": 4, "shares": 3, "share price": 3, "market": 1,
    "earnings": 4, "profit": 3, "profits": 3, "revenue": 3, "sales": 2,
    "investor": 2, "investors": 3, "investment": 2, "company": 1,
    "companies": 2, "firm": 1, "firms": 2, "merger": 4, "mergers": 4,
    "acquisition": 3, "acquisitions": 3, "trade": 2, "exports": 2,
    "imports": 2, "oil": 2, "commodity": 3, "commodities": 3,
    "retail": 3, "retailer": 3, "retailers": 3, "airline": 3,
    "airlines": 3, "bank": 1, "banking": 2, "interest rate": 2,
    "inflation": 3, "recession": 3, "unemployment": 2, "jobs": 1,
    "employment": 2, "manufacturing": 2, "industrial": 2, "factory": 2,
    "factories": 2, "consumer": 1, "consumers": 1, "prices": 1,
    "price": 1, "dollar": 1, "currency": 2, "bond": 2, "bonds": 2,
    "insurance": 2, "mortgage": 2, "housing market": 3, "gdp": 3,
    "quarterly results": 3, "earnings report": 4, "economic growth": 3,
}

WORLD_TERMS = {
    "government": 3, "president": 3, "prime minister": 4, "minister": 2,
    "parliament": 3, "congress": 2, "senate": 2, "election": 4,
    "elections": 4, "vote": 2, "voters": 2, "political": 2, "politics": 3,
    "party": 1, "diplomat": 3, "diplomats": 3, "foreign policy": 4,
    "international": 2, "united nations": 3, "war": 3, "military": 2,
    "troops": 3, "soldier": 2, "soldiers": 2, "conflict": 3,
    "ceasefire": 3, "invasion": 3, "rebel": 2, "rebels": 2,
    "terrorism": 3, "terrorist": 3, "sanctions": 2, "border": 1,
    "police": 2, "crime": 2, "criminal": 2, "murder": 3, "arrest": 2,
    "arrested": 2, "court": 1, "trial": 1, "prison": 2, "kidnap": 3,
    "attack": 1, "bomb": 2, "explosion": 2, "disaster": 2, "earthquake": 3,
    "flood": 2, "hurricane": 2, "refugee": 2, "refugees": 2,
    "protest": 2, "protests": 3, "demonstration": 2, "ministerial": 1,
}

def _normalize(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()

def _score(text, terms):
    padded = " " + text + " "
    total = 0
    for term, weight in terms.items():
        normalized = _normalize(term)
        if " " + normalized + " " in padded:
            total += weight
    return total

def predict(state) -> dict:
    text = _normalize(state)
    scores = {
        "sports": _score(text, SPORTS_TERMS),
        "sci_tech": _score(text, TECH_TERMS),
        "business": _score(text, BUSINESS_TERMS),
        "world": _score(text, WORLD_TERMS),
    }

    # Give clear technology-company coverage extra weight, including reports
    # about their products, earnings, or legal disputes.
    if scores["sci_tech"] >= 4:
        scores["sci_tech"] += 2

    # Sports reporting usually contains multiple match, team, or event cues.
    if scores["sports"] >= 5:
        scores["sports"] += 2

    # Prefer the more specific news categories on ties; world is the fallback.
    order = ("sports", "sci_tech", "business", "world")
    answer = max(order, key=lambda category: (scores[category], -order.index(category)))
    return {"answer": answer}