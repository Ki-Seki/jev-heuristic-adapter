import re


def _make_lexicon():
    lexicon = {}

    groups = {
        2.5: """
            amazing excellent outstanding superb fantastic phenomenal brilliant
            masterpiece perfect flawless extraordinary exceptional magnificent
            wonderful terrific incredible
        """,
        2.0: """
            great best awesome beautiful gorgeous stunning delightful marvelous
            favourite favorite love loved adore adored hilarious hilarious
            compelling captivating engaging gripping absorbing enthralling
            moving touching heartwarming powerful
        """,
        1.5: """
            good better enjoyable entertaining funny witty clever smart fresh
            original creative innovative impressive memorable satisfying
            charming charismatic authentic convincing effective successful
            refreshing recommend recommended succeeds triumph gem
        """,
        1.0: """
            nice fine solid polished coherent realistic tasteful subtle dynamic
            worthwhile interesting ambitious revealing emotional surprising
            thoughtful sincere skillful skilful wellmade
        """,
        0.5: """
            decent watchable entertainingly amusing likable likeable succeeds
            delivers
        """,
        -2.5: """
            awful terrible horrible atrocious abysmal appalling disgraceful
            unwatchable unbearable
        """,
        -2.0: """
            worst hate hated loathe disaster disastrous garbage rubbish trash
            worthless pathetic incompetent appalling
        """,
        -1.7: """
            bad boring dull tedious disappointing disappointed disappoints
            disappoint disappointment waste failure fails failed fail flawed
            weak lifeless pointless incoherent derivative unoriginal
            uninteresting pretentious overlong miscast contrived wooden
            repetitive formulaic predictable implausible shallow shoddy
            amateurish mediocre forgettable annoying irritating frustrating
            offensive tasteless ruined mess messy clumsy awkward stale tiresome
            painful embarrassing laughable lame overrated bloated stilted
            unconvincing misguided
        """,
        -1.3: """
            poor worse confusing confusingly silly ridiculous cheesy corny
            melodramatic cheap forced flat slow tedious badly poorly
            pedestrian monotonous uninspired artificial inconsistent
            unnecessary
        """,
        -1.0: """
            disappointingness imperfect unpleasant crude crude
        """,
        -0.7: """
            violent grim bleak dark depressing sad disappointing
        """,
    }

    for value, words in groups.items():
        for word in words.split():
            lexicon[word] = value

    # Override ambiguous or repeated entries with their intended weights.
    lexicon["entertaining"] = 1.5
    lexicon["disappointing"] = -1.7
    lexicon["disappoint"] = -1.7
    lexicon["disappoints"] = -1.7
    lexicon["disappointment"] = -1.7
    lexicon["hilarious"] = 2.0
    lexicon["crude"] = -1.0
    lexicon["confusing"] = -1.3
    return lexicon


_LEXICON = _make_lexicon()

_PHRASES = [
    ("couldn't", "be", "better", 3.0),
    ("could", "not", "be", "better", 3.0),
    ("can't", "get", "enough", 2.0),
    ("cannot", "get", "enough", 2.0),
    ("doesn't", "disappoint", 1.6),
    ("doesn't", "disappoints", 1.6),
    ("does", "not", "disappoint", 1.6),
    ("does", "not", "disappoints", 1.6),
    ("never", "disappoints", 1.6),
    ("not", "disappointing", 1.4),
    ("not", "bad", 1.3),
    ("not", "good", -1.4),
    ("not", "great", -1.4),
    ("not", "funny", -1.2),
    ("not", "entertaining", -1.4),
    ("not", "worth", -1.5),
    ("no", "fun", -1.5),
    ("waste", "of", "time", -2.2),
    ("waste", "of", "money", -2.0),
    ("waste", "of", "talent", -2.0),
    ("must", "see", 2.0),
    ("must", "watch", 1.8),
    ("highly", "recommended", 1.8),
    ("well", "worth", 1.2),
    ("worth", "watching", 1.0),
    ("highly", "entertaining", 1.8),
    ("laugh", "out", "loud", 1.5),
    ("falls", "flat", -1.6),
    ("falls", "apart", -1.5),
    ("doesn't", "work", -1.4),
    ("does", "not", "work", -1.4),
    ("ripped", "off", -1.8),
    ("so", "bad", "it's", "good", 0.5),
]

_PHRASES.sort(key=lambda item: len(item) - 1, reverse=True)

_NEGATORS = {
    "not", "never", "no", "none", "nobody", "nothing", "neither",
    "hardly", "barely", "without", "cannot",
}

_BOOSTERS = {
    "very": 1.30,
    "really": 1.25,
    "extremely": 1.50,
    "absolutely": 1.40,
    "incredibly": 1.40,
    "exceptionally": 1.40,
    "especially": 1.20,
    "quite": 1.15,
    "pretty": 1.15,
    "so": 1.20,
    "too": 1.15,
    "highly": 1.30,
    "deeply": 1.25,
    "utterly": 1.45,
    "completely": 1.30,
    "slightly": 0.70,
    "somewhat": 0.75,
    "rather": 1.10,
    "barely": 0.55,
}


def predict(state) -> dict:
    text = state if isinstance(state, str) else str(state)
    tokens = re.findall(r"[a-z]+(?:'[a-z]+)?|[.!?;:,]", text.lower())

    phrase_at = {}
    masked = set()
    for index in range(len(tokens)):
        if index in masked or tokens[index] in ".!?;:,":
            continue
        for phrase in _PHRASES:
            words, value = phrase[:-1], phrase[-1]
            end = index + len(words)
            if end <= len(tokens) and tuple(tokens[index:end]) == words:
                if any(pos in masked or tokens[pos] in ".!?;:," for pos in range(index, end)):
                    continue
                phrase_at[index] = (value, end)
                masked.update(range(index, end))
                break

    score = 0.0
    negation_left = 0
    booster = 1.0
    booster_left = 0
    clause_breaks = {".", "!", "?", ";", ":"}
    contrast_words = {"but", "however", "although", "though", "yet"}

    for index, token in enumerate(tokens):
        if index in phrase_at:
            value, end = phrase_at[index]
            score += value
            negation_left = 0
            booster = 1.0
            booster_left = 0
            continue
        if index in masked:
            continue

        if token in clause_breaks:
            negation_left = 0
            booster = 1.0
            booster_left = 0
            continue

        if token in contrast_words:
            negation_left = 0
            booster = 1.0
            booster_left = 0
            continue

        if token == "not" and index + 1 < len(tokens) and tokens[index + 1] == "only":
            continue

        is_negator = token in _NEGATORS or token.endswith("n't")
        if is_negator:
            negation_left = 3
            booster = 1.0
            booster_left = 0
            continue

        if token in _BOOSTERS:
            booster = _BOOSTERS[token]
            booster_left = 2
            if negation_left:
                negation_left -= 1
            continue

        value = _LEXICON.get(token)
        if value is not None:
            adjusted = value * booster
            if negation_left:
                adjusted = -adjusted
            score += adjusted
            if negation_left:
                negation_left -= 1
            booster = 1.0
            booster_left = 0
            continue

        if negation_left:
            negation_left -= 1
        if booster_left:
            booster_left -= 1
            if booster_left == 0:
                booster = 1.0

    return {"answer": "positive" if score > 0 else "negative"}