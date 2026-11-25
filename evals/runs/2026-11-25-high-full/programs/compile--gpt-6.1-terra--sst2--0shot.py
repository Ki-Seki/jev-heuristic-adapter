import re

TOKEN_RE = re.compile(r"[^\W\d_]+(?:'[^\W\d_]+)?|\d+(?:\.\d+)?|[.!?;,:]", re.UNICODE)

WORD_GROUPS = [
    (3.4, """
        masterpiece masterpieces masterwork masterworks flawless perfect perfection
        extraordinary exceptional phenomenal breathtaking magnificent superb sublime
        outstanding brilliant brilliance spectacular unforgettable sensational
        fantastic marvelous marvellous terrific wonderful superbly brilliantly
        magnificently extraordinarily exceptionally phenomenally
    """),
    (2.5, """
        excellent excellence amazing amazingly awesome incredible incredibly terrific
        gorgeous beautifully beautiful delightful delightful marvelous marvellous
        entertaining enthralling captivating compelling riveting fascinating
        absorbing mesmerizing mesmerising enchanting charming lovable loveable
        hilarious hysterical uproarious inspiring inspirational moving touching
        poignant heartwarming heartwarming joyous joyousness exhilarating
        satisfying worthwhile remarkable impressive impressive impressively
        memorable splendid dazzling superbly stunning stunningly exquisite
        delightful enjoyable engrossing engrossed fabulous terrific triumphant
        winner winners gem gems treasure treasures genius inventive innovative
        powerful effective accomplished expertly skillful skilful rewarding
        refreshing refreshingly heartfelt sincere engaging delightful
        recommend recommended recommending recommends recommendation recommendations
        loved loves adore adored adores cherish cherished cherished
    """),
    (1.7, """
        good great fine nice enjoyable enjoyable entertaining entertainment
        funny fun amusing amusement witty witty clever cleverness smart
        enjoyable enjoyable watchable worthwhile worthwhile appealing appealing
        interesting intriguing intriguing original originality imaginative
        imagination creative creativity delightful likable likeable likeable
        lovely lovely endearing engrossing authentic believable convincing
        solid strong successful successfully successful effective effectively
        well-made well-crafted well-acted well-written polished polished
        thoughtful thoughtful intelligent intelligence meaningful meaningful
        touching warmth warm tender charming charm charm charming
        laughs laugh laughter hilarious comedy comedic comic
        entertainingly beautifully gracefully gracefully elegant elegance
        skillfully skilfully expertly expertly expertly lively energetic
        vibrant delightful fresh freshness unique distinctive distinctive
        impressive impressive memorable memorable marvelous marvellous
        enjoyable enjoyable recommend recommendable admirable admirably
        entertaining entertains entertained entertain
        enjoy enjoys enjoyed enjoying enjoyment
        like likes liked liking love loving
        better best favorite favourite favorites favourites
        underrated underrated pleasing pleasant pleasure pleasures
        remarkable resonant rich nuanced nuanced subtle
        wins winning succeeds succeeded succeeding success
        captures captured elevates elevated uplifting uplifting
        worthwhile worthy worth
    """),
    (1.0, """
        decent adequate competent competent competently capable capable
        watchable passable satisfactory satisfying satisfying satisfying
        enjoyable appealing agreeably agreeable promising promising
        solid respect respectable respectable earnest earnestly
        ambitious ambition quirky amusingly enjoyable delightful
        good-hearted sympathetic thoughtfully sincere
    """),
    (-3.4, """
        atrocious abysmal appalling dreadful horrendous horrific execrable
        unwatchable unbearable insufferable excruciating painfully
        awful awfully terrible terribly horrible horribly disastrous disaster
        catastrophically catastrophic atrociously abysmally appallingly
        garbage rubbish trash crap crapfest turd stink stinker stinkers
        worst hated despise despised loathe loathed detest detested
        masterpiece-disaster
    """),
    (-2.5, """
        bad badly boring bored boredom tedious tediously dull dullness
        disappointing disappointed disappoints disappointment disappointments
        dreadful dreadful dreary dreariness dismal miserably miserable misery
        painful painfully poor poorly lousy lousily pathetic pathetically
        inept ineptly incompetence incompetent incompetently
        failure failures failed fails failing fail failure
        awful atrocious absurdly annoying annoyingly irritating irritation
        infuriating frustrating frustrated frustratingly frustrating
        forgettable forgettably pointless pointless pointless
        pointless worthless useless waste wasted wastes wasting
        mess messy messes muddled muddle incoherent incoherence
        nonsensical nonsense nonsensically nonsensical
        unfunny humorless humourless laughless
        uninteresting unengaging uninspired uninspiring unimaginative
        unoriginal unoriginality unconvincing unbelievable
        unlikable unlikeable unlovable unpleasant
        tiresome tiring wearisome exhausting
        lifeless soulless charmless joyless joylessly passionless
        vapid vacuous insipid bland flat flatness
        stupid stupidly stupidity idiotic idiocy idiotic
        ridiculous ridiculously ludicrous ludicrously
        pretentious pretentiously pretension pretentiousness
        trite cliched cliched cliche cliches cliché clichés
        predictable predictability formulaic formulaically
        derivative hackneyed hackneyed corny cheesy cheesiness
        contrived contrivance contrivances contrived
        overlong bloated overblown overwrought overacted
        amateurish amateurishly amateurishness
        clumsy clumsily sloppy sloppily shoddy
        misguided misfire misfires misfired misfiring
        botched botches botch butchered ruined ruins ruin
        squanders squandered squandering squander
        atrocious dreadful horrible horrible awful terrible
        insult insulting insultingly offensive offensively
        cringe cringey cringeworthy cringy
        avoid avoided avoids avoiding
        regretted regrettable regret regretting
        hated hate hates hating disliked dislike dislikes
        loathsome contemptible despicable
        disappointing disappointing disappoint
    """),
    (-1.5, """
        mediocre mediocrity mediocrely middling mediocre
        uneven flawed flaws flaw weak weaker weakness weaknesses
        unimpressive underwhelming underwhelmed underwhelms
        overhyped overrated overrated overrates
        thin thinly shallow shallowness superficial superficiality
        hollow hollowly empty emptiness empty
        mechanical generic routine ordinary unremarkable
        predictable derivative formulaic conventional uninspired
        unevenness unevenly clunky awkward awkwardly
        cheesy corniness hokey silly silliness
        slow sluggish sluggishly plodding plods plodded
        repetitive repetition repetitious repetitive monotonous monotony
        drag drags dragged dragging drawn-out overlong
        lackluster lacklustre lacklustre lackluster
        stiff wooden forced forcedness strained
        forgettable disappointing disappointing
        suspect dubious questionable
        misses missed missing miss
        problems problem issues issue shortcomings shortcoming
        suffers suffered suffering suffer
        fails failed failing flounders floundered
        cheap cheaply poorly poor
        tepid dull flat underwhelming
        boringly tediousness
    """),
]

WORDS = {}
for weight, group in WORD_GROUPS:
    for word in group.split():
        WORDS[word] = weight

PHRASE_GROUPS = [
    (3.5, """
        must see|must watch|a must see|a must watch|must be seen|
        not to be missed|do not miss|don't miss|cannot be missed|
        can't be missed|one of the best|among the best|
        highly recommended|highly recommend|strongly recommend|
        two thumbs up|thumbs up|five stars|five out of five|
        four stars|four out of four|10 out of 10|10/10|
        a work of art|a work of genius|a triumph|a masterpiece|
        well worth watching|well worth seeing|worth every minute|
        well worth the time|well worth your time|time well spent|
        never fails to entertain|never fails to impress|
        could not be better|couldn't be better|can't get enough|
        cannot get enough|could watch it again and again|
        so bad it's good|so bad it is good|bad in a good way|
        laughed out loud|laugh out loud|had me laughing|
        couldn't stop laughing|could not stop laughing|
        blew me away|blows me away|blown away|
        did not disappoint|didn't disappoint|does not disappoint|
        doesn't disappoint|never disappoints|never disappointed|
        not a waste of time|not a waste of your time
    """),
    (2.1, """
        worth watching|worth seeing|worth a watch|worth a look|
        worth your time|worth the time|worth the price|
        worth the effort|worth the wait|worth it|
        well worth it|worth checking out|worth checking|
        would recommend|would recommend it|i recommend|
        i loved it|i love it|i liked it|i enjoyed it|
        a good time|a great time|a fun time|lots of fun|
        a lot of fun|so much fun|great fun|good fun|
        made me laugh|makes me laugh|makes you laugh|
        held my attention|kept me entertained|kept me interested|
        keeps you entertained|keeps you engaged|
        exceeded my expectations|exceeded expectations|
        better than expected|better than i expected|
        pleasantly surprised|a pleasant surprise|
        lived up to expectations|lives up to expectations|
        well done|well made|well written|well acted|
        well directed|well crafted|well executed|
        well worth|a breath of fresh air|a breath of fresh air|
        stands out|stand out|stands the test of time|
        has heart|full of heart|full of charm|full of life|
        on the edge of my seat|on the edge of your seat|
        not bad at all|not too bad|not half bad|not all bad|
        no complaints|nothing to complain about|
        nothing wrong with it|no flaws|without flaws|
        no complaints whatsoever
    """),
    (-3.5, """
        waste of time|waste of my time|waste of your time|
        waste of money|waste of my money|waste of your money|
        waste of two hours|waste of an hour|waste of a film|
        waste of talent|wasted my time|wasted my money|
        don't waste your time|do not waste your time|
        don't waste your money|do not waste your money|
        don't bother watching|do not bother watching|
        don't bother|do not bother|not worth watching|
        not worth seeing|not worth the time|not worth your time|
        not worth my time|not worth the money|not worth the effort|
        not worth it|not worth a watch|not worth a look|
        hardly worth watching|hardly worth seeing|
        not worth a damn|can't recommend|cannot recommend|
        could not recommend|couldn't recommend|would not recommend|
        wouldn't recommend|do not recommend|don't recommend|
        wouldn't recommend it|would never recommend|
        cannot recommend it|can't recommend it|
        no redeeming qualities|no redeeming value|
        no redeeming features|not a single redeeming quality|
        one of the worst|among the worst|the worst movie|
        the worst film|worst movie ever|worst film ever|
        thumbs down|two thumbs down|zero stars|one star|
        zero out of five|one out of five|0 out of 10|
        should not have been made|shouldn't have been made|
        avoid at all costs|stay away|stay away from this|
        could not sit through|couldn't sit through|
        couldn't finish it|could not finish it|
        turned it off|switched it off|walked out|
        wanted my money back|want my money back|
        want my time back|wanted my time back|
        nothing short of awful|nothing short of terrible
    """),
    (-2.0, """
        not a fan|not a fan of|no fan of|not my cup of tea|
        not for me|not for everyone|nothing special|
        nothing to write home about|nothing to write home|
        leaves much to be desired|left much to be desired|
        leaves a lot to be desired|left a lot to be desired|
        could have been better|could've been better|
        should have been better|should've been better|
        should have been much better|could have been so much better|
        falls short|fell short|falls flat|fell flat|
        falls apart|fell apart|fall apart|
        misses the mark|missed the mark|misses its mark|
        fails to deliver|failed to deliver|failure to deliver|
        fails to impress|failed to impress|fails to entertain|
        failed to entertain|fails to engage|failed to engage|
        no reason to watch|no reason to see|
        no point in watching|no point in seeing|
        no fun|not fun|not funny|not amusing|
        not interesting|not entertaining|not enjoyable|
        not good|not very good|not particularly good|
        not great|not very great|not impressive|
        nothing happens|nothing much happens|nothing ever happens|
        puts you to sleep|put me to sleep|putting me to sleep|
        fell asleep|fall asleep|almost fell asleep|
        left me cold|leaves me cold|leave you cold|
        hard to watch|hard to sit through|difficult to watch|
        difficult to sit through|hard to care|hard to follow|
        could not care less|couldn't care less|
        didn't care|did not care|do not care|don't care|
        a letdown|a let down|let me down|lets me down|
        does not work|doesn't work|did not work|didn't work|
        never works|not working|does not deliver|doesn't deliver|
        no chemistry|lacks chemistry|lack of chemistry|
        lack of depth|lacks depth|no depth|
        no plot|no story|no substance|no originality|
        no imagination|no charm|no heart|
        no laughs|not a laugh|not a single laugh|
        no suspense|no excitement|no tension|
        all style and no substance|style over substance|
        tries too hard|trying too hard|takes itself too seriously|
        takes too long|too long|too slow|
        poorly written|poorly acted|poorly directed|poorly made|
        poorly executed|badly written|badly acted|badly directed|
        badly made|badly executed|worse than expected|
        worse than i expected|below expectations|
        failed to live up to|fails to live up to|
        not up to par|not up to scratch|out of its depth|
        a mess|a total mess|a complete mess|a hot mess|
        a missed opportunity|missed opportunity|
        a waste|a total waste|a complete waste|
        not without flaws|not without its flaws|
        not without problems|not without its problems
    """),
]

def tokenize(text):
    return TOKEN_RE.findall(text.casefold().replace("’", "'").replace("‘", "'"))

PHRASES = {}
MAX_PHRASE = 1
for weight, group in PHRASE_GROUPS:
    for phrase in group.split("|"):
        phrase = phrase.strip()
        if phrase:
            tokens = tuple(tokenize(phrase))
            if tokens:
                PHRASES[tokens] = weight
                MAX_PHRASE = max(MAX_PHRASE, len(tokens))

NEGATORS = {
    "not", "no", "never", "neither", "nor", "nothing", "nowhere",
    "hardly", "barely", "scarcely", "without", "cannot", "can't",
    "couldn't", "wouldn't", "shouldn't", "didn't", "doesn't", "don't",
    "isn't", "aren't", "wasn't", "weren't", "hasn't", "haven't",
    "hadn't", "won't", "lack", "lacks", "lacking", "lacked"
}
INTENSIFIERS = {
    "very": 1.35, "really": 1.3, "truly": 1.35, "extremely": 1.6,
    "absolutely": 1.55, "utterly": 1.5, "completely": 1.4,
    "totally": 1.4, "quite": 1.2, "particularly": 1.25,
    "especially": 1.3, "incredibly": 1.45, "exceptionally": 1.45,
    "remarkably": 1.35, "highly": 1.35, "deeply": 1.35,
    "so": 1.3, "too": 1.3, "terribly": 1.35, "awfully": 1.3,
    "unbelievably": 1.45, "extraordinarily": 1.5,
    "pretty": 1.15, "rather": 1.15, "somewhat": 0.75,
    "slightly": 0.65, "a little": 0.7, "barely": 0.65
}
BOUNDARIES = {".", "!", "?", ";", ":", "but", "however", "yet", "although", "though", "whereas", "instead"}
TEXT_KEYS = (
    "text", "sentence", "review", "movie_review", "film_review",
    "movie review", "film review", "content", "input", "phrase",
    "passage", "statement", "utterance", "body", "review_text",
    "sentence_text", "description", "message", "data", "state"
)

def extract_text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in TEXT_KEYS:
            if key in value:
                result = extract_text(value[key])
                if result:
                    return result
        for key, item in value.items():
            if isinstance(key, str) and key.casefold() in {
                "id", "label", "answer", "sentiment", "category",
                "rating", "score", "role", "type"
            }:
                continue
            result = extract_text(item)
            if result:
                return result
        return ""
    if isinstance(value, (list, tuple)):
        parts = [extract_text(item) for item in value]
        return " ".join(part for part in parts if part)
    return ""

def negation_count(tokens, index):
    count = 0
    start = max(0, index - 5)
    for j in range(index - 1, start - 1, -1):
        word = tokens[j]
        if word in BOUNDARIES:
            break
        if word == "," and index - j > 2:
            break
        if word in NEGATORS:
            if word == "not" and j + 1 < len(tokens) and tokens[j + 1] in ("only", "just", "merely"):
                continue
            if word == "nothing" and tokens[j + 1:j + 3] == ["short", "of"]:
                continue
            count += 1
    return count

def modifier(tokens, index):
    result = 1.0
    for j in range(max(0, index - 2), index):
        word = tokens[j]
        if word in INTENSIFIERS:
            result *= INTENSIFIERS[word]
    return min(1.8, max(0.55, result))

def contrast_multiplier(tokens, index):
    start = index
    while start > 0 and tokens[start - 1] not in {".", "!", "?", ";"}:
        start -= 1
    end = index
    while end < len(tokens) and tokens[end] not in {".", "!", "?", ";"}:
        end += 1
    contrasts = [j for j in range(start, end) if tokens[j] in {"but", "however", "yet", "whereas"}]
    if contrasts:
        pivot = contrasts[-1]
        return 0.65 if index < pivot else 1.4
    for j in range(start, min(index + 1, end)):
        if tokens[j] in {"although", "though", "despite"}:
            comma = next((k for k in range(j + 1, end) if tokens[k] == ","), None)
            if comma is not None:
                return 0.65 if index < comma else 1.35
    return 1.0

def sentiment(text):
    tokens = tokenize(text)
    if not tokens:
        return 0.0
    score = 0.0
    i = 0
    while i < len(tokens):
        match = None
        length = 0
        for size in range(min(MAX_PHRASE, len(tokens) - i), 1, -1):
            candidate = tuple(tokens[i:i + size])
            if candidate in PHRASES:
                match = PHRASES[candidate]
                length = size
                break
        if match is None:
            match = WORDS.get(tokens[i])
            length = 1
        if match is not None:
            negations = negation_count(tokens, i)
            if negations % 2:
                match = -match * 0.8
            match *= modifier(tokens, i)
            match *= contrast_multiplier(tokens, i)
            score += match
        i += length
    return score

def predict(state):
    text = extract_text(state)
    score = sentiment(text)
    return {"answer": "negative" if score < 0 else "positive"}