import re
import unicodedata

POSITIVE = {}
NEGATIVE = {}


def _add_words(target, words, weight, adverbs=False):
    for word in words.split():
        target[word] = weight
        if adverbs and len(word) > 3:
            if word.endswith("y"):
                adverb = word[:-1] + "ily"
            elif word.endswith("le"):
                adverb = word[:-1] + "y"
            elif word.endswith("ic"):
                adverb = word + "ally"
            else:
                adverb = word + "ly"
            target.setdefault(adverb, weight * 0.9)


_add_words(POSITIVE, """
good nice fine pleasant enjoyable entertaining engaging interesting appealing
amusing enjoyable agreeable worthwhile satisfying refreshing lively warm
charming delightful lovely welcome solid capable effective successful
accessible smart clever witty funny humorous comic playful sincere heartfelt
touching moving poignant sweet tender thoughtful observant insightful
perceptive sensitive intelligent imaginative inventive original creative
fresh surprising revealing fascinating compelling absorbing involving
captivating intriguing memorable distinctive unique impressive accomplished
polished graceful elegant beautiful gorgeous stunning handsome visual
spirited energetic vibrant charismatic likable likeable lovable endearing
affecting authentic convincing credible believable realistic natural
genuine honest subtle nuanced deft skillful skilful assured confident
ambitious adventurous bold daring inventive restrained sophisticated
professional worthwhile watchable rewatchable recommend recommended
recommendable riveting gripping exciting thrilling suspenseful inspired
inspiring uplifting exhilarating joyous joyful enjoyable enchanting
""" , 1.4, True)

_add_words(POSITIVE, """
great excellent wonderful terrific fantastic fabulous marvelous marvellous
superb brilliant outstanding extraordinary exceptional phenomenal
magnificent remarkable splendid spectacular sublime exquisite flawless
perfect masterful marvelous triumphant triumph masterpiece classic
hilarious uproarious irresistible mesmerizing mesmerising breathtaking
bravura dazzling astonishing electrifying extraordinary unforgettable
""" , 2.4, True)

_add_words(POSITIVE, """
better best favorite favourite finest funniest loveliest strongest
sharpest smartest richest happiest greatest sweetest funniest funniest
""", 2.0)

_add_words(POSITIVE, """
love loved loving loves adore adored adores enjoy enjoyed enjoying enjoys
like liked likes appreciate appreciated admires admire admired
savor savour relished relish delight delights delighted
captivates captivated enchants enchanted entertains entertained
engages engaged fascinates fascinated impresses impressed
succeeds succeeded works sparkles shines triumphs wins
recommend recommends applauds applaud rewards rewarded
""", 1.6)

_add_words(POSITIVE, """
fun pleasure joy delight charm charms wit humor humour laughter laughs
laugh entertainment surprise surprises intelligence humanity heart
warmth compassion depth insight originality beauty poetry
excellence artistry craft brilliance vitality energy exuberance
""", 1.0)

_add_words(POSITIVE, """
well-crafted well-made must-see crowd-pleaser
""", 1.8)

_add_words(NEGATIVE, """
bad poor weak mediocre dull boring bored tedious tiresome tiring
uninteresting uninspired unoriginal unimaginative predictable formulaic
generic derivative clichéd cliched trite stale hackneyed corny cheesy
hokey clumsy awkward inept incompetent amateurish sloppy messy muddled
confused confusing incoherent disjointed uneven unfocused meandering
aimless pointless empty hollow shallow thin flat lifeless listless
wooden stiff bland drab dreary monotonous humorless humourless unfunny
unamusing charmless witless joyless soulless tedious plodding slow
sluggish overlong bloated repetitive redundant forgettable disposable
ordinary pedestrian routine conventional contrived forced artificial
phony fake false pretentious pompous smug self-indulgent indulgent
heavy-handed heavyhanded preachy manipulative sentimental saccharine
maudlin melodramatic overwrought overblown shrill grating annoying
irritating obnoxious unpleasant unappealing ugly crude crass tasteless
tacky vulgar offensive insulting insensitive mean-spirited cynical
embarrassing cringe cringeworthy ridiculous silly absurd ludicrous
laughable implausible unbelievable unconvincing unbelievable
disappointing unsatisfying frustrating underwhelming lackluster
lacklustre miscast misguided misjudged misbegotten flawed faulty
broken weakly shoddy cheap inadequate ineffective unsuccessful
unwatchable unbearable intolerable painful excruciating
""", 1.6, True)

_add_words(NEGATIVE, """
awful terrible horrible dreadful dreadful disastrous atrocious abysmal
appalling abominable horrendous execrable atrocious horrid wretched
miserable lousy rotten pathetic dreadful dreadful worthless dreadful
abysmal ineptitude fiasco disaster failure debacle travesty garbage
rubbish trash junk mess stink stinker turkey dud bore nightmare
worst worse worst-ever garbage
""", 2.4, True)

_add_words(NEGATIVE, """
hate hated hates loathe loathed loathes despise despised detest detested
dislike disliked dislikes disappoint disappointed disappoints
bore bores bored irritate irritated irritates annoy annoyed annoys
fail failed fails failing falters flounders botches ruins ruined
wastes wasted squandered squanders suffers suffering
""", 1.7)

_add_words(NEGATIVE, """
flaw flaws problem problems weakness weaknesses defect defects cliche
cliches cliché clichés disappointment mediocrity boredom tedium
incompetence pretension pretentiousness stupidity nonsense monotony
incoherence implausibility artificiality messiness
""", 1.1)

PHRASE_GROUPS = [
    (3.0, """
        a must see|a must watch|must see|must watch|one of the best|
        one of the greatest|among the best|a real masterpiece|
        a tour de force|a work of art|a rare gem|a genuine gem|
        sheer delight|pure delight|pure joy|a triumph|
        worth every minute|well worth watching|well worth seeing|
        highly recommended|highly recommend|highly entertaining|
        not to be missed|nothing to complain about|
        what is not to like|what not to like|could not be better|
        could not have been better|so bad it is good
    """),
    (2.0, """
        worth watching|worth seeing|worth a look|worth a watch|
        worth your time|worth the time|worth the price of admission|
        well worth|well made|well crafted|well written|well directed|
        well acted|well performed|well executed|well done|
        a good time|good fun|great fun|lots of fun|a lot of fun|
        plenty of fun|a lot to like|much to like|easy to like|
        hard to resist|hard to dislike|hard not to like|
        impossible not to like|a breath of fresh air|
        does not disappoint|never disappoints|never fails to entertain|
        succeeds in|pulls it off|pulls this off|hits the mark|
        on top form|at its best|better than expected|pleasantly surprised|
        in good hands|full of life|full of heart|full of charm|
        has heart|has charm|has a heart|has a lot of heart|
        brings to life|comes to life|a cut above|above average|
        more than the sum of its parts|a delight to watch|
        makes you care|makes us care|keeps you interested|
        keeps you engaged|keeps you guessing|keeps you entertained|
        not half bad|not too shabby|not bad at all|no small feat|
        no mean feat|nothing less than brilliant
    """),
    (-3.0, """
        one of the worst|among the worst|worst movie ever|
        worst film ever|the worst film|the worst movie|
        a complete waste of time|a total waste of time|
        a waste of time|waste of time|waste of money|
        waste of your time|waste of talent|waste of a good cast|
        not worth watching|not worth seeing|not worth your time|
        not worth the trouble|not worth the price|not worth a look|
        no redeeming qualities|no redeeming value|
        no reason to see|no reason to watch|no reason to care|
        nothing to recommend|nothing to recommend it|
        nothing to like|nothing to enjoy|nothing to offer|
        nothing going for it|nothing worth watching|
        a complete disaster|a total disaster|a total mess|
        an absolute mess|an utter mess|an utter failure|
        a painful experience|an insult to the audience|
        an insult to your intelligence|bottom of the barrel|
        scraping the bottom of the barrel|avoid at all costs|
        do not waste your time|save your money|save your time
    """),
    (-2.0, """
        not very good|not much good|not good enough|
        not much fun|no fun|no laughs|few laughs|not funny|
        not at all funny|not remotely funny|not the least bit funny|
        not worth|hard to watch|difficult to watch|hard to sit through|
        a chore to watch|a chore to sit through|a chore|
        hard to care|difficult to care|impossible to care|
        fails to deliver|fails to entertain|fails to engage|
        fails to convince|fails to work|does not work|
        does not deliver|does not convince|does not satisfy|
        does not add up|does not make sense|makes no sense|
        falls flat|falls apart|falls short|fall short|falling short|
        misses the mark|misses its mark|never takes off|
        goes nowhere|leads nowhere|gets nowhere|sits there|
        runs out of steam|outstays its welcome|wears out its welcome|
        overstays its welcome|dead on arrival|dead in the water|
        not much happens|nothing happens|little happens|
        little more than|nothing more than|nothing but a mess|
        too much|too little|too long|too slow|too boring|
        all style and no substance|style over substance|
        style without substance|more style than substance|
        a missed opportunity|a missed chance|a wasted opportunity|
        a letdown|a let down|a big letdown|a disappointment|
        could have been better|should have been better|
        not as good as|nowhere near as good as|
        far from perfect|far from good|far from great|
        too clever for its own good|too smart for its own good|
        tries too hard|trying too hard|tries to be funny|
        trying to be funny|supposed to be funny|
        thinks it is funny|thinks it is clever|
        takes itself too seriously|takes itself seriously|
        leaves much to be desired|leaves a lot to be desired|
        leaves you cold|left me cold|left us cold|
        does not live up to|does not live up to the hype|
        fails to live up to|fails to live up to the hype|
        lacks imagination|lacks originality|lacks depth|lacks charm|
        lacks energy|lacks heart|lacks focus|lacks substance|
        lack of imagination|lack of originality|lack of depth|
        lack of charm|lack of energy|lack of heart|lack of substance|
        no imagination|no originality|no depth|no charm|no substance|
        no chemistry|no spark|no tension|no suspense|no sense of humor|
        no sense of humour|not a good film|not a good movie|
        nothing special|not particularly good|not particularly interesting|
        not particularly funny|not very interesting|
        not very funny|not very entertaining|
        a poor excuse for|a pale imitation|a bad idea|
        in spite of itself|despite itself
    """),
]

PHRASES = {}
for value, group in PHRASE_GROUPS:
    for item in group.split("|"):
        item = item.strip()
        if item:
            words = tuple(item.split())
            PHRASES.setdefault(words[0], []).append((words, value))
for first in PHRASES:
    PHRASES[first].sort(key=lambda pair: len(pair[0]), reverse=True)

NEGATORS = {
    "not", "never", "no", "neither", "nor", "without", "hardly",
    "barely", "scarcely", "rarely", "seldom", "nothing", "lack",
    "lacks", "lacking", "lacked", "fail", "fails", "failed", "failing",
}
BOUNDARIES = {".", "!", "?", ";", ":", ",", "but", "however", "yet", "although", "though"}
STRONG_MODIFIERS = {
    "very": 1.35, "really": 1.3, "extremely": 1.7, "incredibly": 1.5,
    "utterly": 1.55, "absolutely": 1.5, "completely": 1.4,
    "totally": 1.4, "thoroughly": 1.35, "highly": 1.35,
    "deeply": 1.3, "especially": 1.25, "particularly": 1.2,
    "remarkably": 1.3, "exceptionally": 1.4, "so": 1.25,
    "quite": 1.15, "rather": 1.15, "too": 1.25,
    "truly": 1.3, "genuinely": 1.2, "unusually": 1.2,
    "most": 1.2, "more": 1.1, "much": 1.15,
}
WEAK_MODIFIERS = {
    "slightly": 0.65, "somewhat": 0.7, "fairly": 0.8,
    "mildly": 0.6, "vaguely": 0.5, "moderately": 0.7,
    "marginally": 0.6, "occasionally": 0.7, "sometimes": 0.75,
    "partly": 0.75, "partially": 0.75, "little": 0.75,
}
CONTRAST = {"but", "however", "yet", "nevertheless", "nonetheless"}
CLAUSE_END = {".", "!", "?", ";"}


def _normalize(text):
    text = unicodedata.normalize("NFKC", text).casefold()
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r"\bn\s*'\s*t\b", " not", text)
    text = re.sub(r"n\s*'\s*t\b", " not", text)
    text = re.sub(r"\bwhat\s*'\s*s\b", "what is", text)
    text = re.sub(r"\bit\s*'\s*s\b", "it is", text)
    text = re.sub(r"\bthat\s*'\s*s\b", "that is", text)
    text = re.sub(r"\bthere\s*'\s*s\b", "there is", text)
    text = re.sub(r"\bhere\s*'\s*s\b", "here is", text)
    text = re.sub(r"\bnothing short of\b", "extremely", text)
    text = re.sub(r"\bnot only\b", "only", text)
    text = re.sub(r"\bnot merely\b", "merely", text)
    text = re.sub(r"\bnot just\b", "just", text)
    text = re.sub(r"\bnot without\b", "with some", text)
    text = re.sub(r"\bno doubt\b", "certainly", text)
    text = re.sub(r"\bno less than\b", "at least", text)
    text = re.sub(r"\bnever fails to\b", "always manages to", text)
    text = re.sub(r"\bcannot help but\b", "inevitably", text)
    text = re.sub(r"\bcan not help but\b", "inevitably", text)
    text = re.sub(r"\bnothing but\b(?!\s+a\s+mess)", "only", text)
    text = re.sub(r"\b(too|very|really)\s+\1\b", r"\1", text)
    return re.findall(r"[^\W\d_]+(?:-[^\W\d_]+)*|\d+|[.!?,;:]", text, re.UNICODE)


def _contrast_weight(tokens, position):
    start = position
    while start > 0 and tokens[start - 1] not in CLAUSE_END:
        start -= 1
    end = position + 1
    while end < len(tokens) and tokens[end] not in CLAUSE_END:
        end += 1

    before = any(t in CONTRAST for t in tokens[start:position])
    after = any(t in CONTRAST for t in tokens[position + 1:end])
    weight = 1.0
    if before:
        weight *= 1.35
    if after:
        weight *= 0.65

    for j in range(start, position):
        if tokens[j] in {"although", "though", "while", "despite"}:
            if not any(t in {",", "but", "yet", "however"} for t in tokens[j + 1:position]):
                weight *= 0.65
                break
    return weight


def _negated(tokens, position):
    count = 0
    steps = 0
    for j in range(position - 1, -1, -1):
        word = tokens[j]
        if word in BOUNDARIES or word in CONTRAST:
            break
        steps += 1
        if steps > 6:
            break
        if word in NEGATORS:
            count += 1
        elif word == "few" and steps <= 3:
            count += 1
    return count % 2 == 1


def _modifier(tokens, position):
    factor = 1.0
    for j in range(max(0, position - 3), position):
        word = tokens[j]
        if word in BOUNDARIES or word in CONTRAST:
            factor = 1.0
        elif word in STRONG_MODIFIERS:
            factor *= STRONG_MODIFIERS[word]
        elif word in WEAK_MODIFIERS:
            factor *= WEAK_MODIFIERS[word]
    return max(0.4, min(factor, 1.8))


def _word_score(tokens, i):
    word = tokens[i]
    score = POSITIVE.get(word, 0.0) - NEGATIVE.get(word, 0.0)

    if word in {"like", "likes", "liked"}:
        following = tokens[i + 1] if i + 1 < len(tokens) else ""
        previous = tokens[i - 1] if i else ""
        if previous in {"looks", "look", "looked", "feels", "feel", "felt",
                        "seems", "seem", "seemed", "sounds", "sound", "sounded",
                        "something", "anything", "nothing", "just", "rather"}:
            return 0.0
        if following in {"a", "an", "something", "nothing", "some", "those"}:
            return 0.0
        if following in {"the", "this", "that"}:
            later = tokens[i + 2] if i + 2 < len(tokens) else ""
            if later not in {"film", "movie", "show", "picture", "performance",
                             "story", "director", "cast", "acting"}:
                return 0.0

    if word in {"love", "loving", "loves"}:
        following = tokens[i + 1] if i + 1 < len(tokens) else ""
        previous = tokens[i - 1] if i else ""
        if following in {"story", "affair", "interest", "triangle", "scene"}:
            return 0.0
        if previous in {"about", "of", "in", "for", "finds", "find", "romantic"}:
            return 0.0

    if word in {"visual", "comic", "surprise", "surprises", "energy", "heart",
                "laughs", "humor", "humour"}:
        score *= 0.7

    return score


def predict(state):
    if not isinstance(state, str):
        return {"answer": "positive"}

    tokens = _normalize(state)
    total = 0.0
    i = 0
    while i < len(tokens):
        token = tokens[i]
        phrase = None
        for words, value in PHRASES.get(token, ()):
            if tuple(tokens[i:i + len(words)]) == words:
                phrase = (words, value)
                break

        if phrase is not None:
            words, score = phrase
            length = len(words)
        else:
            score = _word_score(tokens, i)
            length = 1

        if score:
            if _negated(tokens, i):
                if score > 0:
                    score *= -0.9
                else:
                    score *= -0.75
            score *= _modifier(tokens, i)
            score *= _contrast_weight(tokens, i)

            previous = tokens[max(0, i - 5):i]
            if score > 0 and any(w in {"supposedly", "supposed", "allegedly"} for w in previous):
                score *= 0.45
            if score > 0 and any(w in {"thinks", "claims", "pretends"} for w in previous):
                score *= 0.4

            total += score
        i += length

    return {"answer": "positive" if total >= 0 else "negative"}