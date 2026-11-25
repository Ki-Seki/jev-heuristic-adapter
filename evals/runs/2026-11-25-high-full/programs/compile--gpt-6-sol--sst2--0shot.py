import re
import unicodedata


def _words(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower().replace("’", "'").replace("`", "'")
    return re.findall(r"[a-z]+(?:'[a-z]+)?|\d+(?:\.\d+)?|[.!?;,]", text)


def _extract_text(state):
    if isinstance(state, str):
        return state
    if isinstance(state, dict):
        for key in (
            "text", "sentence", "review", "movie_review", "film_review",
            "comment", "content", "message", "utterance", "input", "state",
        ):
            if key in state:
                value = state[key]
                if isinstance(value, str):
                    return value
                if isinstance(value, (dict, list, tuple)):
                    result = _extract_text(value)
                    if result:
                        return result
        strings = [value for value in state.values() if isinstance(value, str)]
        return max(strings, key=len) if strings else ""
    if isinstance(state, (list, tuple)):
        strings = [_extract_text(item) for item in state]
        return " ".join(item for item in strings if item)
    return ""


_LEXICON = {}


def _add_words(weight, words):
    for word in words.split():
        _LEXICON[word] = weight


_add_words(4.0, """
masterpiece masterpieces phenomenal phenomenalistic outstanding exceptional
extraordinary superb magnificent brilliant flawless perfect perfection
incredible breathtaking riveting mesmerizing spellbinding sensational
""")
_add_words(3.3, """
amazing awesome fantastic excellent wonderful marvelous marvellous spectacular
terrific splendid fabulous phenomenal stunning beautiful gorgeous delightful
hilarious engrossing captivating enthralling unforgettable heartwarming
heartfelt inspiring inspired exhilarating impeccable immaculate remarkable
""")
_add_words(2.6, """
great loved love adore adored favorite favourite favorites favourites
enjoyable entertaining compelling impressive impressive-looking
well-made well-written well-acted well-directed brilliant-looking
clever witty charming moving touching powerful gripping engaging
original inventive imaginative refreshing memorable satisfying
satisfied rewarding delightful surprising superbly masterful
""")
_add_words(2.1, """
good liked like enjoy enjoyed fun funny solid strong effective
effective-looking exciting interesting thoughtful smart skillful skilful
talented polished authentic excellent-looking appealing pleasing
beautifully wonderfully brilliantly expertly artful cinematic
underrated worthwhile recommend recommended recommendation
""")
_add_words(1.4, """
decent fine nice pleasant amusing enjoyable-looking watchable
promising creative stylish competent coherent believable fresh
sweet warm endearing ambitious entertainingly charmingly
entertained interestingly impressive-looking-indeed
""")
_add_words(0.8, """
okay ok alright acceptable adequate passable fair satisfying-enough
interesting-enough enjoyably
""")

_add_words(-4.1, """
abysmal atrocious appalling awful dreadful horrendous horrible
unwatchable unbearable insufferable excruciating atrociously
""")
_add_words(-3.4, """
terrible disastrous abominable garbage trash rubbish worthless
pathetic miserable abysmal disappointing disappointment
disappoints disappointed worst hated hate loathed loathe
unbearably painfully laughable laughably
""")
_add_words(-2.8, """
bad poor boring bored tedious dull bland awful-looking dreadful-looking
waste wasted pointless annoying irritating obnoxious stupid idiotic
ridiculous incoherent nonsensical incomprehensible confusing
unconvincing uninspired unoriginal predictable clichéd cliched
cliche cliches clichés contrived amateurish sloppy clumsy
cheesy corny cringeworthy cringe cringey lifeless soulless
shallow hollow forgettable underwhelming overrated
""")
_add_words(-2.1, """
weak mediocre lackluster lacklustre tediousness monotonous
repetitive derivative generic formulaic flat wooden stilted
awkward unfunny uninteresting unengaging unsatisfying
unbelievable implausible inconsistent messy muddled
disjointed frustrating tiresome tediously dragged dragging
draggy overlong overstuffed overacted overacting miscast
unnecessary disappointing-looking
""")
_add_words(-1.5, """
slow sluggish thin predictable-looking uneven flawed flaws flaw
lacking fails failed fail failure misses missed miss
underdeveloped superficial forgettable-looking uninspired-looking
cheap forced grating irritatingly jarring hollow-looking
mediocrity mediocre-looking disappointing-enough
""")
_add_words(-0.8, """
weakness weaknessses flawed-looking ordinary conventional
passable-looking lengthy excessive slight underwhelmingly
""")

# Hyphens separate words in the tokenizer. These entries supply useful
# single-word forms alongside the groups above.
_LEXICON.update({
    "well": 0.0,
    "crafted": 1.1,
    "written": 0.0,
    "acted": 0.0,
    "directed": 0.0,
    "executed": 0.0,
    "paced": 0.0,
    "produced": 0.0,
    "made": 0.0,
    "worth": 2.0,
    "worthy": 1.8,
    "recommendable": 2.3,
    "recommendations": 1.3,
    "recommending": 2.2,
    "loves": 2.6,
    "loving": 1.7,
    "likes": 1.9,
    "enjoys": 2.0,
    "enjoying": 2.0,
    "enjoyment": 2.0,
    "pleased": 1.8,
    "pleasure": 1.6,
    "delighted": 2.8,
    "delight": 2.5,
    "thrilled": 2.5,
    "thrilling": 2.5,
    "thrill": 1.4,
    "laughs": 1.3,
    "laughed": 1.5,
    "laughing": 1.2,
    "humor": 0.7,
    "humour": 0.7,
    "hysterical": 2.0,
    "hysterically": 1.6,
    "hated": -3.4,
    "hates": -3.4,
    "dislike": -2.4,
    "disliked": -2.4,
    "dislikes": -2.4,
    "disgusting": -3.0,
    "disgusted": -2.5,
    "disappointment": -3.3,
    "disappointing": -3.3,
    "disappointed": -3.1,
    "disappoints": -2.8,
    "disappoint": -2.8,
    "underwhelmed": -2.5,
    "unimpressed": -2.5,
    "unimpressive": -2.4,
    "boringly": -2.5,
    "boredom": -2.8,
    "dullness": -2.5,
    "stinks": -3.0,
    "stink": -3.0,
    "sucks": -3.4,
    "sucked": -3.4,
    "suck": -3.2,
    "awfully": -2.3,
    "horribly": -2.6,
    "terribly": -2.5,
    "badly": -2.1,
    "poorly": -2.1,
    "beautifully": 2.2,
    "wonderfully": 2.7,
    "brilliantly": 2.9,
    "masterfully": 3.0,
    "superbly": 3.0,
    "perfectly": 2.8,
    "exceptionally": 1.6,
    "fascinating": 2.5,
    "fascinated": 2.0,
    "fascinates": 2.0,
    "absorbing": 2.4,
    "immersive": 2.2,
    "immersed": 1.5,
    "heart": 0.0,
    "heartfelt": 2.7,
    "hilariously": 2.8,
    "convincing": 1.9,
    "believable": 1.5,
    "satisfies": 2.0,
    "satisfy": 1.8,
    "delivers": 1.9,
    "delivered": 1.7,
    "deliver": 1.4,
    "succeeds": 2.1,
    "succeeded": 1.9,
    "successful": 1.6,
    "works": 1.7,
    "worked": 1.5,
    "working": 0.5,
    "win": 1.4,
    "winner": 2.1,
    "wins": 1.4,
    "gem": 2.7,
    "treasure": 2.2,
    "classic": 2.5,
    "triumph": 3.0,
    "triumphant": 2.8,
    "achievement": 2.0,
    "must": 0.0,
    "see": 0.0,
    "rewatch": 1.5,
    "rewatched": 1.7,
    "repeatedly": 0.0,
    "revisit": 1.1,
    "recommend": 2.6,
    "recommended": 2.6,
    "recommendation": 2.1,
    "flop": -2.4,
    "flopped": -2.4,
    "failure": -2.2,
    "fails": -2.0,
    "failed": -2.0,
    "fail": -2.0,
    "ruined": -2.7,
    "ruins": -2.7,
    "ruin": -2.5,
    "waste": -3.0,
    "wasted": -2.8,
    "wasting": -2.8,
    "regret": -2.8,
    "regretted": -2.8,
    "regrettable": -2.2,
    "avoid": -2.8,
    "skip": -2.2,
    "skippable": -2.5,
    "unwatchable": -4.0,
    "unbearable": -3.8,
    "forgettable": -2.5,
    "mediocre": -2.0,
    "mediocrity": -2.0,
    "mess": -2.6,
    "messy": -2.0,
    "confused": -1.7,
    "confusing": -2.1,
    "confusion": -1.7,
    "baffling": -1.4,
    "predictability": -2.1,
    "cliches": -2.5,
    "cliched": -2.7,
    "cliche": -2.4,
    "cheesiness": -1.9,
    "campy": -0.5,
    "camp": 0.0,
    "tedium": -2.5,
    "tedious": -2.8,
    "drag": -1.8,
    "drags": -2.2,
    "dragged": -2.1,
    "dragging": -2.0,
    "slow": -1.3,
    "sluggish": -2.0,
    "rushed": -1.8,
    "hollow": -2.0,
    "empty": -1.6,
    "shallow": -2.3,
    "lacks": -2.0,
    "lacked": -2.0,
    "lacking": -2.0,
    "lack": -1.8,
    "overrated": -2.5,
    "underrated": 2.0,
    "overhyped": -2.5,
    "overdone": -1.9,
    "underwritten": -2.4,
    "predictable": -2.6,
    "unpredictable": 1.4,
    "original": 2.0,
    "unoriginal": -2.6,
    "formulaic": -2.2,
    "forgettable": -2.5,
    "memorable": 2.0,
    "forgettable": -2.5,
    "unforgettable": 3.0,
    "better": 1.4,
    "best": 2.6,
    "worse": -2.1,
    "worst": -3.7,
    "improved": 1.2,
    "improvement": 1.1,
    "improves": 1.1,
    "unpleasant": -2.1,
    "pleasant": 1.4,
    "enough": 0.0,
    "fine": 1.2,
    "okay": 0.8,
    "ok": 0.8,
    "meh": -1.5,
    "average": -0.7,
    "so-so": -1.0,
    "mixed": -0.5,
    "intense": 0.5,
    "dark": 0.0,
    "scary": 0.0,
    "frightening": 0.0,
    "terrifying": 0.3,
    "disturbing": -0.2,
    "violent": 0.0,
    "brutal": 0.0,
    "sad": -0.3,
    "tragic": 0.0,
})


_PHRASES = {}


def _add_phrases(weight, phrases):
    for phrase in phrases.split("|"):
        tokens = tuple(_words(phrase.strip()))
        if tokens:
            _PHRASES[tokens] = weight


_add_phrases(4.2, """
one of the best|the best movie|the best film|best movie ever|
best film ever|a must see|a must watch|must see movie|must watch movie|
worth every minute|worth the price of admission|worth watching|
worth seeing|highly recommend|highly recommended|strongly recommend|
cannot recommend enough|can't recommend enough|couldn't recommend more|
could not recommend more|not to be missed|don't miss it|do not miss it|
two thumbs up|thumbs up|a breath of fresh air|a work of art|
a masterpiece|an instant classic|a hidden gem|an absolute gem|
a real treat|a joy to watch|a pleasure to watch
""")
_add_phrases(3.3, """
well worth watching|well worth seeing|well worth your time|
worth your time|worth a watch|worth a look|worth seeing|
great movie|great film|great acting|great performances|
great performance|great story|great script|great direction|
great cast|great ending|great cinematography|
excellent movie|excellent film|excellent acting|
beautifully shot|beautifully filmed|beautifully crafted|
well written|well acted|well directed|well made|well crafted|
well executed|well paced|very funny|really funny|
laugh out loud|had me laughing|kept me entertained|
kept me engaged|kept me hooked|kept me on the edge of my seat|
blew me away|blown away|exceeded my expectations|
better than expected|better than i expected|
pleasantly surprised|surprisingly good|surprisingly enjoyable|
loved every minute|loved every second|loved this movie|
loved this film|i loved it|i love it|i really liked it|
i really enjoyed it|i enjoyed every minute|
would watch again|will watch again|watch it again|
can't wait to see it again|can not wait to see it again
""")
_add_phrases(2.4, """
a good movie|a good film|a fun movie|a fun film|
a solid movie|a solid film|a solid performance|
good acting|good performances|good performance|
good story|good script|good direction|good cast|
good ending|good cinematography|good soundtrack|
good pacing|good writing|a pleasant surprise|
better than most|enjoyed the movie|enjoyed the film|
enjoyed watching|enjoyed it|i liked it|i liked this movie|
i liked this film|had a good time|had fun watching|
made me laugh|made me smile|made me cry in a good way|
not bad|not half bad|not too bad|not so bad|
not terrible|not awful|not horrible|not boring|
never boring|never dull|not a waste of time|
no waste of time|not disappointed|wasn't disappointed|
was not disappointed|didn't disappoint|did not disappoint|
doesn't disappoint|does not disappoint|never disappoints|
no complaints|nothing to complain about|hard not to like|
hard to dislike|far from bad|anything but boring|
nothing short of amazing|nothing short of brilliant|
so bad it's good|so bad it is good|so bad they're good|
a guilty pleasure|guilty pleasure|better than i thought
""")
_add_phrases(-4.2, """
one of the worst|the worst movie|the worst film|
worst movie ever|worst film ever|waste of time|
a waste of time|complete waste of time|waste of money|
waste of two hours|waste of my time|waste of my money|
not worth watching|not worth seeing|not worth the time|
not worth my time|not worth your time|not worth the money|
not worth a watch|not worth it|not worth the price|
don't waste your time|do not waste your time|
avoid this movie|avoid this film|avoid at all costs|
save your money|save your time|skip this movie|
skip this film|thumbs down|two thumbs down|
walked out|turned it off|fell asleep|put me to sleep|
a total disaster|a complete disaster|an absolute disaster|
an absolute mess|a complete mess|a total mess|
painful to watch|unbearable to watch|unwatchable movie
""")
_add_phrases(-3.3, """
terrible movie|terrible film|terrible acting|
awful movie|awful film|awful acting|
bad movie|bad film|bad acting|bad performances|
bad performance|bad story|bad script|bad direction|
bad writing|poor acting|poor writing|poor direction|
poorly written|poorly acted|poorly directed|poorly made|
horribly written|horribly acted|horribly directed|
not good|not great|not very good|not very funny|
not funny|not interesting|not entertaining|
not enjoyable|not engaging|not impressive|
not a good movie|not a good film|no good|
far from good|far from great|anything but good|
nothing special|nothing happens|nothing to recommend|
no redeeming qualities|no redeeming features|
no redeeming value|no plot|no story|no substance|
no character development|no chemistry|no laughs|
lack of plot|lack of story|lack of substance|
lacks depth|lacks substance|lacks originality|
fails to deliver|failed to deliver|doesn't deliver|
does not deliver|didn't deliver|did not deliver|
falls flat|fell flat|falls apart|fell apart|
missed the mark|misses the mark|misses the point|
a letdown|a let down|let me down|let us down|
a disappointment|deeply disappointing|
disappointed by this movie|disappointed by this film|
i hated it|i hate it|i hated this movie|
i hated this film|i didn't like it|i did not like it|
i didn't enjoy it|i did not enjoy it|
i don't like it|i do not like it|
i wish i hadn't watched it|i wish i had not watched it|
wish i could unsee it|wish i could get my time back|
would not recommend|wouldn't recommend|
cannot recommend|can't recommend|
couldn't recommend|could not recommend|
wouldn't watch again|would not watch again|
won't watch again|will not watch again|
don't bother|do not bother|don't watch it|
do not watch it|no reason to watch
""")
_add_phrases(-2.5, """
below average|less than average|underwhelming movie|
underwhelming film|weak plot|weak script|weak story|
weak ending|weak performances|weak performance|
weak acting|weak direction|thin plot|thin story|
forgettable movie|forgettable film|
predictable plot|predictable story|predictable ending|
too predictable|too long|way too long|far too long|
too slow|too short|too boring|too dull|
dragged on|drags on|dragged out|poorly paced|
badly paced|painfully slow|excruciatingly slow|
not as good as|nowhere near as good as|
could have been better|could've been better|
should have been better|should've been better|
i expected better|expected better|i wanted to like it|
wanted to like it|hard to watch|difficult to watch|
hard to sit through|a chore to watch|
not my cup of tea|left me cold|left me bored|
wasn't impressed|was not impressed|
didn't impress me|did not impress me|
couldn't get into it|could not get into it|
not for me|not worth the hype|doesn't live up to the hype|
does not live up to the hype|didn't live up to the hype|
did not live up to the hype|a missed opportunity|
wasted potential|wasted talent|wasted cast|
no sense|makes no sense|made no sense
""")
_add_phrases(2.0, """
couldn't have been better|could not have been better|
can't get enough|cannot get enough|couldn't stop watching|
could not stop watching|couldn't take my eyes off|
could not take my eyes off|didn't want it to end|
did not want it to end|never gets old|
never failed to entertain|never fails to entertain|
wasn't as bad as i expected|was not as bad as i expected|
better than the original|better than the first|
a lot of fun|loads of fun|so much fun|
not without its merits|not without merit
""")
_add_phrases(-2.7, """
wasn't as good as i expected|was not as good as i expected|
not nearly as good|not nearly as funny|not remotely funny|
not at all funny|not at all entertaining|
not at all interesting|not at all enjoyable|
not a masterpiece|no masterpiece|didn't think it was good|
did not think it was good|i wanted to like this but couldn't|
i wanted to like this but could not|
i wanted to enjoy it but couldn't|
i wanted to enjoy it but could not|
better in the trailer|the trailer was better|
the trailer is better|nothing but a disappointment|
not what i expected|wasn't what i expected|
was not what i expected
""")
_add_phrases(2.3, """
didn't think it was bad|did not think it was bad|
wasn't as bad as i thought|was not as bad as i thought|
not as bad as they say|not as bad as people say|
not as bad as it sounds|better than its reputation
""")
_add_phrases(0.0, """
bad guy|bad guys|the bad guy|the bad guys|
good guy|good guys|the good guy|the good guys
""")

_PHRASE_BY_FIRST = {}
for _tokens, _weight in _PHRASES.items():
    _PHRASE_BY_FIRST.setdefault(_tokens[0], []).append((_tokens, _weight))
for _entries in _PHRASE_BY_FIRST.values():
    _entries.sort(key=lambda entry: len(entry[0]), reverse=True)

_NEGATORS = {
    "not", "no", "never", "neither", "nor", "nothing", "nobody",
    "nowhere", "without", "cannot", "can't", "couldn't", "don't",
    "doesn't", "didn't", "isn't", "wasn't", "weren't", "aren't",
    "won't", "wouldn't", "shouldn't", "hardly", "scarcely", "barely",
}
_STRONG_INTENSIFIERS = {
    "extremely", "incredibly", "absolutely", "utterly", "completely",
    "totally", "exceptionally", "immensely", "profoundly",
    "phenomenally", "unbelievably", "super", "really",
}
_INTENSIFIERS = {
    "very", "so", "quite", "particularly", "especially", "highly",
    "remarkably", "seriously", "thoroughly", "deeply", "rather", "too",
}
_DIMINISHERS = {
    "slightly", "somewhat", "mildly", "partly", "occasionally",
    "fairly", "kinda", "kindof",
}
_BOUNDARIES = {".", "!", "?", ";", ",", "but", "however", "yet", "though", "although"}


def _contraction_normalize(tokens):
    result = []
    for token in tokens:
        if token == "cannot":
            result.extend(("can", "not"))
        elif token.endswith("n't"):
            result.extend((token[:-3] if token != "can't" else "can", "not"))
        elif token == "wont":
            result.extend(("will", "not"))
        elif token == "dont":
            result.extend(("do", "not"))
        elif token == "didnt":
            result.extend(("did", "not"))
        elif token == "doesnt":
            result.extend(("does", "not"))
        elif token == "wasnt":
            result.extend(("was", "not"))
        elif token == "isnt":
            result.extend(("is", "not"))
        elif token == "wouldnt":
            result.extend(("would", "not"))
        elif token == "couldnt":
            result.extend(("could", "not"))
        else:
            result.append(token)
    return result


def _rating_score(text):
    low = text.lower()
    scores = []

    for match in re.finditer(
        r"\b(\d+(?:\.\d+)?)\s*(?:/|out of)\s*(5|10|100)\b", low
    ):
        value = float(match.group(1))
        maximum = float(match.group(2))
        if value <= maximum:
            scores.append(5.0 * (value / maximum - 0.52))

    for match in re.finditer(
        r"\b(\d+(?:\.\d+)?)\s*(?:stars?|★)\b", low
    ):
        value = float(match.group(1))
        if value <= 5:
            scores.append(5.0 * (value / 5.0 - 0.52))

    if re.search(r"\b(?:zero|one|two|three|four|five)\s+stars?\b", low):
        numbers = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
        for match in re.finditer(
            r"\b(zero|one|two|three|four|five)\s+stars?\b", low
        ):
            scores.append(5.0 * (numbers[match.group(1)] / 5.0 - 0.52))

    return sum(scores)


def _is_negated(tokens, start):
    count = 0
    distance = 0
    j = start - 1
    while j >= 0 and distance < 6:
        token = tokens[j]
        if token in _BOUNDARIES:
            break
        if token in _NEGATORS:
            if token == "not" and j + 1 < len(tokens) and tokens[j + 1] == "only":
                pass
            elif token == "no" and j + 1 < len(tokens) and tokens[j + 1] == "doubt":
                pass
            else:
                count += 1
        if token in {"and", "or"} and distance >= 3:
            break
        distance += 1
        j -= 1
    return count % 2 == 1


def _modifier(tokens, start):
    multiplier = 1.0
    for offset in (1, 2):
        j = start - offset
        if j < 0 or tokens[j] in _BOUNDARIES:
            break
        token = tokens[j]
        if token in _STRONG_INTENSIFIERS:
            multiplier *= 1.45 if offset == 1 else 1.18
        elif token in _INTENSIFIERS:
            multiplier *= 1.25 if offset == 1 else 1.1
        elif token in _DIMINISHERS:
            multiplier *= 0.65
        elif token in {"a", "bit", "little", "kind", "sort", "of"}:
            multiplier *= 0.88
    return min(multiplier, 2.0)


def _contrast_weights(tokens):
    weights = [1.0] * len(tokens)
    contrast_indices = [
        i for i, token in enumerate(tokens)
        if token in {"but", "however", "yet", "though", "although", "nevertheless"}
        and not (
            token == "but"
            and i > 0
            and "only" in tokens[max(0, i - 7):i]
        )
    ]
    if contrast_indices:
        pivot = contrast_indices[-1]
        if tokens[pivot] in {"although", "though"} and pivot <= 2:
            end = next(
                (i for i in range(pivot + 1, len(tokens)) if tokens[i] == ","),
                len(tokens),
            )
            for i in range(pivot, end):
                weights[i] = 0.65
            for i in range(end + 1, len(tokens)):
                weights[i] = 1.35
        else:
            for i in range(pivot):
                weights[i] = 0.72
            for i in range(pivot + 1, len(tokens)):
                weights[i] = 1.45
    return weights


def _sentiment(text):
    tokens = _words(text)
    if not tokens:
        return -1.0

    weights = _contrast_weights(tokens)
    score = _rating_score(text)
    used = [False] * len(tokens)
    i = 0

    while i < len(tokens):
        matched = None
        for phrase, value in _PHRASE_BY_FIRST.get(tokens[i], ()):
            end = i + len(phrase)
            if end <= len(tokens) and tuple(tokens[i:end]) == phrase:
                matched = (end, value)
                break

        if matched is not None:
            end, value = matched
            if value and _is_negated(tokens, i):
                value = -value * 0.88
            score += value * weights[i]
            for j in range(i, end):
                used[j] = True
            i = end
        else:
            i += 1

    for i, token in enumerate(tokens):
        if used[i]:
            continue

        value = _LEXICON.get(token, 0.0)
        if not value:
            continue

        if token in {"good", "bad"} and i + 1 < len(tokens):
            if tokens[i + 1] in {"guy", "guys", "character", "characters"}:
                continue

        if _is_negated(tokens, i):
            value = -value * (0.9 if value > 0 else 0.78)

        if i > 0 and tokens[i - 1] in {"barely", "hardly", "scarcely"}:
            value = -abs(value) * 0.85 if value > 0 else abs(value) * 0.65

        score += value * _modifier(tokens, i) * weights[i]

    low = text.lower()
    if "👎" in text or "😡" in text or "😠" in text:
        score -= 2.3
    if "👍" in text or "😍" in text or "❤️" in text:
        score += 2.3

    if score == 0:
        if re.search(r"\b(?:okay|ok|fine|decent|enjoyed|recommend)\b", low):
            return 0.5
        return -0.1
    return score


def predict(state) -> dict:
    text = _extract_text(state)
    return {"answer": "positive" if _sentiment(text) > 0 else "negative"}