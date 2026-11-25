import re

POSITIVE = {
    "adore": 2.4, "adored": 2.4, "amaze": 2.2, "amazed": 2.2,
    "amazing": 2.2, "awesome": 2.2, "beautiful": 1.7, "best": 2.3,
    "brilliant": 2.2, "captivating": 1.9, "charming": 1.6, "classic": 1.3,
    "compelling": 1.8, "delight": 1.8, "delightful": 1.9, "engaging": 1.6,
    "enjoy": 1.7, "enjoyable": 1.8, "entertaining": 1.8, "excellent": 2.2,
    "exciting": 1.7, "exceptional": 2.1, "fantastic": 2.3, "favorite": 2.0,
    "fascinating": 1.8, "fun": 1.5, "funniest": 1.8, "funny": 1.5,
    "good": 1.4, "great": 1.9, "impressive": 1.7, "incredible": 2.1,
    "interesting": 1.1, "joy": 1.7, "loved": 2.2, "love": 2.2,
    "masterpiece": 2.5, "moving": 1.7, " original": 0.8, "perfect": 2.2,
    "phenomenal": 2.3, "powerful": 1.5, "recommend": 1.6, "refreshing": 1.5,
    "remarkable": 1.7, "rich": 0.8, "riveting": 2.0, "satisfying": 1.7,
    "smooth": 0.9, "solid": 1.0, "spectacular": 2.2, "strong": 1.1,
    "stunning": 2.0, "superb": 2.2, "terrific": 2.0, "touching": 1.6,
    "unique": 1.0, "wonderful": 2.1, "worthwhile": 1.5, "worthy": 1.1,
}

NEGATIVE = {
    "annoy": -1.5, "annoying": -1.6, "atrocious": -2.4, "awful": -2.1,
    "bad": -1.5, "banal": -1.5, "bizarre": -0.7, "boring": -1.8,
    "cliche": -1.3, "cliched": -1.5, "confusing": -1.0, "contrived": -1.7,
    "corny": -1.2, " disappointing": -1.7, "disappoint": -1.7,
    "disappointing": -1.8, "disappointment": -1.8, "disjointed": -1.4,
    "dreadful": -2.1, "dull": -1.7, "evil": -0.8, "fail": -1.3,
    "failed": -1.4, "fails": -1.4, "flaw": -1.0, "flawed": -1.3,
    "forgettable": -1.5, "frustrating": -1.7, "gimmicky": -1.3,
    "hackneyed": -1.5, "horrible": -2.2, "loathe": -2.1, "loathed": -2.1,
    "lame": -1.4, "mediocre": -1.5, "mess": -1.3, "messy": -1.3,
    "miserable": -1.8, "misleading": -1.2, "nonsense": -1.5,
    "offensive": -1.6, "painful": -1.7, "pathetic": -1.9,
    "poor": -1.4, "predictable": -1.0, "ridiculous": -1.2,
    "rotten": -1.8, "rubbish": -1.8, "sad": -0.8, "shallow": -1.3,
    " stupid": -1.5, "stupid": -1.6, "tedious": -1.8, "terrible": -2.2,
    "tiresome": -1.6, "tragic": -0.8, "ugly": -1.3, "unconvincing": -1.5,
    "unfunny": -1.6, "uninteresting": -1.6, "uninspired": -1.5,
    "unoriginal": -1.4, "unpleasant": -1.5, "unwatchable": -2.2,
    "useless": -1.5, "weak": -1.2, "worse": -1.8, "worst": -2.2,
}

# Remove leading spaces used only to keep the literal dictionaries readable.
POSITIVE = {k.strip(): v for k, v in POSITIVE.items()}
NEGATIVE = {k.strip(): v for k, v in NEGATIVE.items()}

PHRASES = {
    "a cut above": 1.8, "a lot of fun": 1.8, "a masterpiece": 2.5,
    "a must see": 2.1, "a must watch": 2.1, "a waste of time": -2.2,
    "all time favorite": 2.2, "an absolute delight": 2.2,
    "at its best": 1.6, "badly made": -1.7, "barely watchable": -1.8,
    "better than expected": 1.6, "best movie": 2.3, "best film": 2.3,
    "could not stop watching": 1.7, "does not disappoint": 1.8,
    "doesn't disappoint": 1.8, "do not recommend": -1.8,
    "don't recommend": -1.8, "edge of my seat": 1.8,
    "enjoyed every minute": 2.0, "far from perfect": -0.8,
    "fails to deliver": -1.8, "fell asleep": -1.5, "feel good": 1.3,
    "full of heart": 1.6, "highly recommend": 2.0, "laugh out loud": 1.6,
    "leave you wanting more": -1.0, "love this movie": 2.4,
    "love this film": 2.4, "not a good": -1.7, "not bad": 1.4,
    "not disappointed": 1.3, "not enjoyable": -1.6, "not excellent": -1.4,
    "not fun": -1.4, "not good": -1.7, "not great": -1.5,
    "not interesting": -1.3, "not recommend": -1.7, "not terrible": 1.1,
    "not worth": -1.5, "nothing special": -0.8, "one of the best": 2.3,
    "painfully boring": -2.2, "pretty good": 1.6, "really enjoyed": 2.0,
    "so bad": -1.8, "so good": 1.9, "some of the best": 2.0,
    "surprisingly good": 1.8, "the best": 2.1, "the worst": -2.2,
    "too long": -0.8, "truly awful": -2.4, "utterly boring": -2.2,
    "well acted": 1.3, "well crafted": 1.4, "well directed": 1.3,
    "well done": 1.3, "well written": 1.5, "waste of time": -2.1,
    "worth watching": 1.5, "worth the watch": 1.5,
}

NEGATORS = {"not", "no", "never", "neither", "nor", "hardly", "barely"}
INTENSIFIERS = {
    "absolutely": 1.45, "completely": 1.35, "deeply": 1.25,
    "extremely": 1.45, "incredibly": 1.4, "really": 1.2, "so": 1.2,
    "totally": 1.35, "truly": 1.3, "very": 1.2,
}
DOWNTONERS = {"almost": 0.7, "fairly": 0.8, "kind": 0.75, "kinda": 0.75,
              "little": 0.75, "pretty": 0.9, "rather": 0.85, "somewhat": 0.7}


def _extract_text(state):
    """Get textual content without treating mapping keys as review text."""
    preferred = {
        "text", "sentence", "review", "content", "input", "message",
        "statement", "movie_review", "movie_text",
    }
    found = []

    def visit(value, key_hint=""):
        if isinstance(value, str):
            if value.strip():
                found.append((0 if key_hint.lower() in preferred else 1, value))
        elif isinstance(value, dict):
            for key, item in value.items():
                visit(item, str(key))
        elif isinstance(value, (list, tuple)):
            for item in value:
                visit(item, key_hint)

    visit(state)
    found.sort(key=lambda item: item[0])
    return " ".join(text for _, text in found)


def _normalize(text):
    text = text.lower()
    replacements = (
        (r"\bcan't\b", "can not"), (r"\bcannot\b", "can not"),
        (r"\bwon't\b", "will not"), (r"\bdon't\b", "do not"),
        (r"\bdoesn't\b", "does not"), (r"\bdidn't\b", "did not"),
        (r"\bisn't\b", "is not"), (r"\baren't\b", "are not"),
        (r"\bwasn't\b", "was not"), (r"\bweren't\b", "were not"),
        (r"\bhaven't\b", "have not"), (r"\bhasn't\b", "has not"),
        (r"\bhadn't\b", "had not"), (r"\bwouldn't\b", "would not"),
        (r"\bshouldn't\b", "should not"), (r"\bcouldn't\b", "could not"),
        (r"\bmustn't\b", "must not"),
    )
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)
    return text


def _tokens(text):
    return re.findall(r"[a-z]+(?:'[a-z]+)?|[.!?,;:]", text)


def _clause_weight(tokens, index):
    # Sentiment after contrast words is usually the more informative judgment.
    start = 0
    for i in range(index):
        if tokens[i] in {".", "!", "?", ";"}:
            start = i + 1
    for i in range(start, index):
        if tokens[i] in {"but", "however", "though", "although", "yet"}:
            return 1.3
    for i in range(index + 1, len(tokens)):
        if tokens[i] in {"but", "however", "though", "although", "yet"}:
            return 0.8
        if tokens[i] in {".", "!", "?", ";"}:
            break
    return 1.0


def _sentiment_score(text):
    normalized = _normalize(text)
    words = _tokens(normalized)
    if not words:
        return 0.0

    score = 0.0
    covered = set()

    # Apply the most specific sentiment phrases first, avoiding double counting.
    phrase_items = sorted(
        ((tuple(_tokens(phrase)), value) for phrase, value in PHRASES.items()),
        key=lambda item: len(item[0]),
        reverse=True,
    )
    for i in range(len(words)):
        if words[i] in {".", "!", "?", ";", ",", ":"}:
            continue
        for phrase_words, value in phrase_items:
            end = i + len(phrase_words)
            if end > len(words) or any(j in covered for j in range(i, end)):
                continue
            if tuple(words[i:end]) == phrase_words:
                score += value * _clause_weight(words, i)
                covered.update(range(i, end))
                break

    lexicon = dict(POSITIVE)
    lexicon.update(NEGATIVE)
    for i, word in enumerate(words):
        if i in covered or word not in lexicon:
            continue

        value = lexicon[word]
        # A nearby negator reverses the sentiment, except "not only".
        prior = words[max(0, i - 3):i]
        if "only" in prior and "not" in prior:
            pass
        elif any(token in NEGATORS for token in prior):
            value = -value * 0.9

        # Scale sentiment for nearby emphasis or qualification.
        for token in prior[-2:]:
            if token in INTENSIFIERS:
                value *= INTENSIFIERS[token]
            elif token in DOWNTONERS:
                value *= DOWNTONERS[token]

        score += value * _clause_weight(words, i)

    # Common emphatic punctuation offers only a small tie-break.
    if score > 0 and "!" in words:
        score += 0.1
    return score


def predict(state) -> dict:
    text = _extract_text(state)
    score = _sentiment_score(text)
    return {"answer": "positive" if score > 0 else "negative"}