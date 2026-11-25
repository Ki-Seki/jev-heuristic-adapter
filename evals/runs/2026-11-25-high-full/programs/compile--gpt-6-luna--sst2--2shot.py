import re

_POSITIVE = {}
_NEGATIVE = {}

def _add(target, words, weight):
    for word in words.split():
        target[word] = weight

_add(_POSITIVE, """
adore adored adores adoring amazing amazingly amaze amazed amazes amusing
appealing astonishing astounding authentic awesome beautiful beautifully
best better brilliant bravo captivating charming cheerful classic clever
comic comedic confident convincing creative delightful delightful
delightfully delicious entertaining enthralling excellent exceptional
exciting exquisite extraordinary fabulous fantastic favorable favorite
favourite flawless fun funny gem genius genuine glorious glorious
good gorgeous graceful gripping happy heartwarming heartfelt hilarious
hopeful impressive ingenious insightful inspired inspiring intelligent
intriguing likable likeable liked likes lively lovely magnificent masterful
memorable mesmerizing moving original outstanding perfect phenomenal
pleased pleasing pleasurable powerful profound refreshing remarkable
riveting satisfying sensitive sensational sincere skillful skilled
smart smooth solid spectacular splendid stirring strong stunning sublime
superb superior surprising sweet talented tender terrific touching
triumphant true truthful unforgettable unique uplifting useful valuable
vibrant visionary warm wonderful worthwhile worthy
""", 1.5)
_add(_POSITIVE, """
enjoy enjoyed enjoys enjoying love loved loves loving recommend recommended
recommendation succeeds success successful triumph entertaining
engaging engrossing fascinating compelling effective emotional revealing
better improved improvement rich rewarding meaningful nuanced persuasive
polished potent poetic realistic romantic sympathetic thoughtful
wellmade well-acted witty wise
""", 1.1)
_add(_POSITIVE, """
interesting entertaining decent pleasant earnest ambitious bold brave
 likable original unusual watchable pretty cute charmingly
""".replace(" ", ""), 0.65)
_add(_POSITIVE, "interesting decent pleasant watchable cute", 0.65)
_add(_POSITIVE, "emotional revealing surprising", 0.8)
_add(_POSITIVE, "more", 0.0)

_add(_NEGATIVE, """
abysmal atrocious awful appalling atrociously bad banal bland botched
boring bothersome clumsy contrived corny cringeworthy crude cruel
depressing derivative disastrous disappointing dismal dreadful dull
failure fail failed fails fake farfetched feeble flawed foolish
forgettable frustrating hamfisted hackneyed hollow horrible horrid
illogical incompetent incoherent inept insipid irritating lame laughable
lifeless listless ludicrous mediocre melodramatic mess messy miserable
misguided monotonous nonsensical offensive obnoxious painful pathetic
poor pointless predictable pretentious primitive problematic ridiculous
ridiculous rotten rough sad shallow shabby shame shameful silly slow
sloppy smarmy soulless stale stereotyped stupid tedious terrible tiresome
tired trite unbelievable unconvincing uneven unfair unpleasant unoriginal
unsatisfying useless weak worthless worst worst-written
""", 1.5)
_add(_NEGATIVE, """
annoyed annoying complaint complained disappointing disappointment dislike
disliked dislikes hating hate hated hates loathe loathed loses loss lost
problem regrettable regret regretted sucks suffered suffers suffering
waste wasted
""", 1.2)
_add(_NEGATIVE, """
awkward cheap confusing dark difficult excessive exploitive incoherent
overlong repetitive tiresome violent
""", 0.55)
_add(_NEGATIVE, "pedestrian", 1.0)

_PHRASES = {
    ("too", "much"): -2.5,
    ("too", "many"): -1.7,
    ("too", "long"): -1.8,
    ("too", "slow"): -1.8,
    ("too", "little"): -1.2,
    ("too", "late"): -1.2,
    ("too", "bad"): -1.2,
    ("waste", "of", "time"): -2.8,
    ("waste", "of", "money"): -2.8,
    ("waste", "of", "talent"): -2.5,
    ("waste", "time"): -2.4,
    ("worth", "watching"): 1.5,
    ("must", "see"): 2.0,
    ("highly", "recommended"): 2.0,
    ("highly", "recommend"): 2.0,
    ("not", "worth"): -1.8,
    ("no", "fun"): -1.5,
    ("poorly", "made"): -2.0,
    ("well", "made"): 1.5,
    ("well", "acted"): 1.5,
    ("well", "written"): 1.5,
    ("high", "quality"): 1.3,
    ("low", "budget"): -0.4,
    ("special", "effects"): 0.0,
    ("waste", "of"): -1.0,
}

_NEGATORS = {"not", "no", "never", "neither", "nor", "hardly", "scarcely", "without"}
_INTENSIFIERS = {
    "very": 1.35, "really": 1.3, "extremely": 1.6, "incredibly": 1.5,
    "absolutely": 1.5, "completely": 1.35, "totally": 1.35, "deeply": 1.3,
    "so": 1.25, "quite": 1.15, "especially": 1.2, "particularly": 1.2,
    "highly": 1.25, "truly": 1.25, "remarkably": 1.3, "utterly": 1.5,
}
_DOWNTONERS = {
    "slightly": 0.65, "somewhat": 0.7, "rather": 0.8, "fairly": 0.8,
    "pretty": 0.9, "a_bit": 0.6, "barely": 0.55, "vaguely": 0.55,
    "mildly": 0.6, "almost": 0.8,
}
_BOUNDARIES = {".", "!", "?", ";", ":", ",", "but", "however", "although", "though", "yet", "whereas"}

def _clause_factor(tokens, index):
    factor = 1.0
    for i, token in enumerate(tokens):
        if token in {"but", "however", "yet", "whereas"}:
            if index > i:
                factor = 1.35
            elif index < i:
                factor = min(factor, 0.8)
    return factor

def _preceding(tokens, index, limit=4):
    result = []
    i = index - 1
    while i >= 0 and len(result) < limit:
        token = tokens[i]
        if token in _BOUNDARIES:
            break
        if re.fullmatch(r"[a-z]+(?:'[a-z]+)?", token):
            result.append((i, token))
        i -= 1
    return result

def predict(state) -> dict:
    text = state if isinstance(state, str) else str(state)
    tokens = re.findall(r"[a-z]+(?:'[a-z]+)?|[.!?;:,]", text.lower())
    score = 0.0

    for i, token in enumerate(tokens):
        value = _POSITIVE.get(token, 0.0) - _NEGATIVE.get(token, 0.0)
        if not value:
            continue

        previous = _preceding(tokens, i)
        previous_words = [word for _, word in previous]
        if any(word in _NEGATORS for word in previous_words):
            # "not only good" and "not just good" are not ordinary negations.
            negator_index = next(
                (j for j, word in previous if word in _NEGATORS), None
            )
            following = tokens[negator_index + 1:negator_index + 3] if negator_index is not None else []
            if not (tokens[negator_index] == "not" and following and following[0] in {"only", "just"}):
                value = -value

        for _, word in previous[:2]:
            if word in _INTENSIFIERS:
                value *= _INTENSIFIERS[word]
                break
            if word in _DOWNTONERS:
                value *= _DOWNTONERS[word]
                break

        score += value * _clause_factor(tokens, i)

    for phrase, value in _PHRASES.items():
        size = len(phrase)
        for i in range(len(tokens) - size + 1):
            if tuple(tokens[i:i + size]) == phrase:
                score += value * _clause_factor(tokens, i)

    return {"answer": "positive" if score > 0 else "negative"}