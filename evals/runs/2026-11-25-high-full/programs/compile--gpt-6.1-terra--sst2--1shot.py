import re
import unicodedata


def _make_lexicon():
    lexicon = {}

    groups = [
        (3.4, """
            masterpiece masterful perfection perfect flawless outstanding exceptional
            extraordinary brilliant breathtaking magnificent marvelous marvellous
            phenomenal superb sublime terrific splendid fantastic wonderful
            unforgettable transcendent mesmerizing mesmerising riveting sensational
            triumph triumphant brilliantest
        """),
        (2.6, """
            excellent amazing marvelous marvellous glorious delightful delightful
            enthralling captivating compelling mesmerizing enchanting exhilarating
            dazzling gorgeous ingenious inspired irresistible superbly brilliantly
            beautifully masterfully stunning astounding remarkable remarkable
            spectacular fabulous gorgeous fantastic lovely delightful
        """),
        (1.9, """
            great best superb wonderful terrific impressive entertaining enjoyable
            engaging delightful charming powerful moving touching hilarious funny
            clever smart witty vibrant vivid gripping absorbing engrossing affecting
            poignant heartfelt heartwarming heartwarming heartening stirring
            rewarding satisfying refreshing inventive imaginative insightful
            thoughtful intelligent memorable enjoyable enjoyable fascinating
            beautiful excellent enjoyable pleasurable appealing endearing
            accomplished assured authentic exhilarating enchanting graceful
            lively vibrant spirited sophisticated nuanced deft skillful skilful
            skillfully skilfully expertly splendidly effectively succeeds succeed
            successful successfully succeeds succeeds delightful
            love loved loves loving adore adored adores
            recommend recommended recommends recommendation worthwhile
            favorite favourite favorites favourites gem gems delight delights
            pleasure pleasures joy joyous joyful delightfully wonderfully
            entertainingly amusing amusingly humorous humorously
            impressive impressively impressive impressive
            captivatingly engagingly movingly compellingly
        """),
        (1.3, """
            good better well fun entertainingly amusing interesting intriguing
            original inventive exciting excitingly sweet tender warm warmth
            touching touching charmingly charm charms charismatic charisma
            likable likeable likability likability lovable loveable appealing
            appealingly winning wins winner winners funny humor humour hilarious
            laughs laugh laughter chuckles laugh-out-loud witty wittily wit
            quirky lively energetic energy dynamic lively fresh refreshing
            genuine sincere sincerity believable convincing persuasive
            realistic realism effective effective effectively solid strong
            stronger strength strengths fine fine nicely nice nicely
            engaging engagement entertaining entertainment enjoyable enjoyment
            enjoy enjoyed enjoys enjoying like liked likes liking
            pleased pleasing pleasant pleasantly welcome welcome
            worthy worth merit merits meritorious quality polished
            beautifully beauty beautiful artistry artistic artful
            rich richness richly colorful colourful colorful
            cleverness intelligence insight insights perceptive
            satisfying satisfaction satisfies satisfy satisfies
            thoughtful thought-provoking thought-provoking
            deftly deft skill skillful talent talented talents
            accomplished confident confidence competence competent
            refreshing originality originality imagination imagination
            inventive invention creativity creative cleverly
            subtle subtlety honest honesty humane humanity
            human humanely tenderly sensitive sensitivity
            moving moved moved emotionally affecting
            unusual distinctive unique worthwhile
            recommendable recommendable successful
        """),
        (0.7, """
            decent fair adequate okay ok goodish respectable reasonable reasonably
            passable watchable agreeable appealing interestingly curiosity curious
            competent competently amusing chuckle chuckling entertaining
            promising promise promisingly betterment advantage advantages
            surprising surprisingly surprised surprise surprises
            reveal revealing revelations emotional emotion emotionality
            ambitious ambition ambition earnest earnestness
            earnest well-made well-crafted well-acted well-written well-directed
            beautifully-shot effective efficiently efficient
            breezy brisk briskly easy accessible accessible
            well done well-done nicely done
        """),
        (-3.4, """
            atrocious abysmal dreadful execrable appalling horrendous horrid
            terrible awful unbearable unwatchable worthless disastrous disaster
            catastrophic catastrophe atrociously abysmally
            worst masterpiece-less detestable loathsome repulsive revolting
            excruciating excruciatingly torture torturous
        """),
        (-2.6, """
            horrible horrid dreadful pathetic miserable misery painful painfully
            dreadful embarrassingly embarrassing embarrassment embarrassing
            inept ineptitude incompetence incompetent incompetently
            tedious tediousness tediously boring bored boredom
            awful awfully terrible terribly lousy rotten dreadful
            dreadful disastrous disaster fiasco debacle travesty
            atrocious atrociously atrocious horrifically horrible
            ridiculous ridiculously absurdity laughable laughably
            stupid stupidity idiotic idiocy moronic brainless
            wretched wretchedly miserable miserable miserably
            pointless pointlessly pointless futile futility
            unbearable intolerable insufferable obnoxious
            offensive offensively offensive insulting insult insultingly
            hateful hatred hate hated hates hating despise despised
            despises loathe loathed loathes loathing
            waste wasted wastes wasting ripoff rip-off
            awful crap crappy garbage trash rubbish junk dreck dross
            mess messes messiest trainwreck train-wreck
            unfunny joyless lifeless soulless humorless humourless
            witless talentless clueless hopeless hopelessly
            disappointing disappointment disappointments disappoint disappoints
            disappointed disappointingly fails failed failure failures failing
            botched botch botches botching ruins ruined ruin ruining
            destroys destroyed destroy destructive sabotages sabotaged sabotage
        """),
        (-1.8, """
            bad worse worst poor poorly weak weaker weakest weakness weaknesses
            mediocre mediocrity mediocrities bland blandness dull dullness
            dreary drab stale staleness flat flatness flatly
            tiresome tiring tired tedious slow sluggish plodding
            predictable predictability predictable formulaic formula
            clichéd cliched cliche cliches cliché clichés clichéd
            generic derivative unoriginal unimaginative uninspired uninspiring
            forgettable forgettably forgetfulness forgettable
            hollow empty emptiness vacuous vacuousness shallow shallowness
            superficial superficiality trivial triviality insubstantial
            overwrought overblown overlong overdone overstuffed overacted
            pretentious pretension pretensions pretentiously pretentiousness
            contrived contrivance contrivances contrived artificially artificial
            forced forcedly awkward awkwardly awkwardness clumsy clumsily
            amateur amateurish amateurishly shoddy sloppy sloppily
            messy muddled muddle muddles muddling incoherent incoherence
            confused confusing confusion unfocused disjointed disjointedly
            uneven unevenness unevenly erratic erratically inconsistent
            unconvincing unconvincingly unbelievable implausible implausibility
            improbable improbability implausibly
            annoying annoys annoy annoyed annoying irritation irritating
            grating grates gratingly aggravating aggravates irritatingly
            shrill shrillness obnoxiously offputting off-putting
            frustrating frustration frustrates frustrated frustratingly
            unsatisfying unsatisfied unsatisfactory unsatisfactorily
            underwhelming underwhelmed underwhelms underwhelm
            uninteresting unengaging unappealing unlikable unlikeable
            dislike disliked dislikes disliking
            obnoxious nasty unpleasant unpleasantness ugliness ugly
            crude crass tasteless tastelessness vulgar vulgarity
            manipulative manipulates manipulation manipulative
            maudlin schmaltzy saccharine syrupy sentimental sentimentality
            corny corniness cheesy cheesiness hokey hokum
            silly silliness foolish foolishness dopey dumb dumbness
            heavy-handed heavyhanded ham-fisted hamfisted
            lackluster lacklustre lacklusterly lacklustrely
            feeble feebly limp flimsy flimsy
            forgettable forgettable disappointing
            misfire misfires misfired misfiring failure failed
            squander squandered squanders squandering squanders
            disappointingly deficient deficiency deficiently
            flawed flaws flaw fault faults faulty problems problem
            shortcomings shortcomings shortcoming shortfalls shortfall
            defects defect defective weakness weakness weakly
            unnecessary needless redundant redundancy redundancy
            pointless purposeless misguided misjudged miscalculated
            miscast miscasting misdirected misbegotten
            poor-quality poorly-written poorly-acted poorly-directed
            uninvolving tiresomely
        """),
        (-0.8, """
            limited limitation limitations conventional conventionality
            ordinary ordinarily pedestrian routine routinely familiar
            typical typically standard standard-issue standard issue
            modest modestly minor slight slightly slightness
            unevenness uneven imperfect imperfection imperfections
            derivative derivative predictably predictability
            formulaic formulaically formulaicness
            simplistic simplicity simplistic simplistically
            shallow thin thinly thinness slight slightness
            slow slowly slowness sluggishness meandering meanders
            long lengthy overlength pacing padded padding pad
            lag lags lagging drags dragged dragging drag
            stilted wooden stiff stiffness stiffness
            murky murkiness murkily messy messiness
            weakly weakness weak weaknesses dubious questionable
            questionable questionable puzzling puzzlingly
            odd oddly strange strangely weird weirdly
            unfortunately regrettably sadly alas
            despite although however but
            lacks lacking lacked lack absence absent missing misses miss
            squandered wasted
        """),
    ]

    for value, words in groups:
        for word in words.split():
            if "-" not in word:
                lexicon[word] = value

    # Words whose meaning is primarily positive should not be overwritten by
    # their appearance in a lower-intensity group.
    lexicon.update({
        "masterpiece": 3.5, "perfect": 3.2, "brilliant": 3.1,
        "wonderful": 2.8, "fantastic": 2.8, "excellent": 2.8,
        "great": 2.4, "good": 1.7, "better": 1.8, "best": 2.3,
        "well": 0.35, "fine": 0.9, "nice": 1.0,
        "fun": 1.9, "funny": 1.9, "laugh": 1.1, "laughs": 1.1,
        "entertaining": 2.0, "entertainment": 1.2, "entertains": 1.7,
        "entertain": 1.6, "entertained": 1.7, "enjoy": 1.8,
        "enjoyable": 2.0, "enjoyed": 1.9, "enjoys": 1.5,
        "like": 0.9, "liked": 1.4, "love": 2.3, "loved": 2.3,
        "interesting": 1.3, "interested": 0.9, "interest": 0.8,
        "intriguing": 1.5, "surprising": 0.8, "surprisingly": 0.5,
        "emotional": 0.6, "revealing": 0.8, "warm": 1.0,
        "strong": 1.2, "solid": 1.2, "talent": 0.9, "talented": 1.3,
        "original": 1.4, "originality": 1.2, "creative": 1.4,
        "flaw": -1.2, "flaws": -1.2, "flawed": -1.1,
        "problem": -1.0, "problems": -1.0, "fault": -0.9,
        "slow": -1.0, "long": -0.4, "modest": 0.0,
        "ordinary": -0.9, "pedestrian": -1.4, "familiar": -0.3,
        "strange": -0.2, "weird": -0.2, "odd": -0.2,
        "sentimental": -0.5, "silly": -0.8, "conventional": -0.5,
        "bad": -2.2, "worse": -2.2, "worst": -3.0,
        "boring": -2.4, "bored": -1.8, "bore": -1.8, "bores": -1.8,
        "disappointing": -2.0, "disappointed": -1.9,
        "disappoint": -1.9, "disappoints": -1.9,
        "waste": -2.3, "wasted": -1.8, "wastes": -2.1,
        "fails": -1.5, "fail": -1.5, "failed": -1.5, "failure": -2.0,
        "lacks": -1.1, "lack": -1.1, "lacking": -1.1, "lacked": -1.1,
        "miss": -0.5, "missing": -0.6, "misses": -0.7,
        "but": 0.0, "however": 0.0, "although": 0.0, "despite": 0.0,
        "issue": 0.0, "well-made": 1.5,
    })
    return lexicon


LEXICON = _make_lexicon()

# Phrases capture idioms whose sentiment is not the sum of their component words.
PHRASES = [
    (r"so bad (?:that )?(?:it is|it's|its) good", 1.8),
    (r"so bad (?:that )?(?:it is|it's|its) (?:actually )?funny", 1.2),
    (r"not only (?:is it )?good but (?:it is |it's )?great", 2.7),
    (r"(?:cannot|can't|couldn't|can not) recommend (?:it |this )?(?:highly )?enough", 3.0),
    (r"(?:cannot|can't|couldn't|can not) praise (?:it |this )?enough", 3.0),
    (r"(?:not|never) to be missed", 2.5),
    (r"not (?:one|a film|a movie) to be missed", 2.3),
    (r"(?:do not|don't|never) miss (?:it|this|the film|the movie)", 2.2),
    (r"(?:a )?must[ -]see", 2.4),
    (r"(?:a )?must (?:see|watch)", 2.3),
    (r"(?:is|are|be) a must", 2.0),
    (r"well worth (?:a look|a watch|watching|seeing|your time|the price)", 2.4),
    (r"worth (?:a look|a watch|watching|seeing|your time|the price)", 1.8),
    (r"(?:not|never|hardly) worth (?:a look|a watch|watching|seeing|your time|the price)", -2.1),
    (r"nothing short of (?:a )?(?:masterpiece|brilliant|excellent|amazing|wonderful|extraordinary|spectacular)", 3.1),
    (r"nothing if not (?:entertaining|funny|charming|interesting|engaging|original|clever)", 1.9),
    (r"(?:anything but|far from) (?:boring|dull|bad|ordinary|mediocre|predictable)", 1.9),
    (r"(?:anything but|far from) (?:good|funny|entertaining|interesting|perfect|great)", -1.9),
    (r"(?:not|never) (?:a )?waste of (?:time|money)", 1.5),
    (r"(?:a |the |an? enormous |an? utter |an? complete |an? total )?waste of (?:time|money|talent|potential|resources)", -2.7),
    (r"(?:a )?waste of (?:its |the )?(?:talent|cast|potential)", -2.4),
    (r"(?:one|among) of the (?:very )?best", 2.9),
    (r"one of the (?:very )?best", 2.9),
    (r"one of the (?:very )?worst", -3.0),
    (r"among the (?:very )?best", 2.7),
    (r"among the (?:very )?worst", -2.8),
    (r"(?:at|in) its best", 1.8),
    (r"(?:at|in) its worst", -2.0),
    (r"(?:a |the )?cut above", 1.9),
    (r"head and shoulders above", 2.2),
    (r"well above average", 1.8),
    (r"(?:well )?below average", -1.7),
    (r"not (?:at all |very |particularly |especially )?good", -1.9),
    (r"not (?:at all |very |particularly |especially )?funny", -1.8),
    (r"not (?:at all |very |particularly |especially )?entertaining", -1.8),
    (r"not (?:at all |very |particularly |especially )?interesting", -1.6),
    (r"not (?:at all |very |particularly |especially )?bad", 1.4),
    (r"not a bad (?:film|movie|picture)", 1.4),
    (r"not (?:half )?bad", 1.5),
    (r"not without (?:its |some |a few )?(?:flaws|problems|faults|shortcomings)", 0.8),
    (r"not without (?:its |some )?(?:charm|merit|merits|virtues|pleasures)", 1.1),
    (r"(?:has|have) its (?:share of )?(?:flaws|problems|faults) but", 0.0),
    (r"no (?:small|mean) (?:feat|achievement|accomplishment)", 1.7),
    (r"no lack of (?:charm|talent|humor|humour|fun|entertainment)", 1.6),
    (r"no shortage of (?:charm|talent|humor|humour|fun|entertainment)", 1.6),
    (r"(?:does not|doesn't|did not|didn't|never) disappoint", 1.9),
    (r"(?:does not|doesn't|did not|didn't|never) fail to (?:entertain|please|delight|impress|charm)", 1.9),
    (r"(?:does not|doesn't|did not|didn't) (?:quite )?work", -1.5),
    (r"(?:does not|doesn't|did not|didn't|cannot|can't) (?:quite )?deliver", -1.5),
    (r"(?:does not|doesn't|did not|didn't|cannot|can't) (?:quite )?live up to", -1.5),
    (r"(?:is|was|falls) (?:far |well )?short of (?:expectations|its potential)", -1.7),
    (r"(?:falls|fell) (?:far |well )?short", -1.5),
    (r"leaves? (?:a lot|much|plenty) to be desired", -2.0),
    (r"(?:has|have|there is|there's) (?:little|nothing|not much) to recommend", -1.8),
    (r"(?:little|nothing|not much) to recommend (?:it|this)", -2.0),
    (r"(?:hard|difficult|impossible) to recommend", -1.9),
    (r"(?:hard|difficult|painful) to watch", -1.7),
    (r"(?:hard|difficult) to beat", 1.7),
    (r"(?:easy|hard not) to (?:enjoy|love|like|recommend)", 1.8),
    (r"could(?:n't| not) help but (?:enjoy|love|like|admire)", 1.8),
    (r"(?:can't|cannot|couldn't) help but (?:enjoy|love|like|admire)", 1.8),
    (r"(?:can't|cannot|can not) wait to (?:see|watch)", 1.7),
    (r"(?:little|nothing|not much) (?:new|original|interesting|funny|special)", -1.5),
    (r"nothing special", -1.3),
    (r"nothing (?:more|less) than (?:a )?(?:masterpiece|triumph)", 2.7),
    (r"(?:a )?few (?:good )?laughs", 0.8),
    (r"(?:very |too )?few (?:good )?laughs", -1.2),
    (r"(?:no|not enough|few) laughs", -1.4),
    (r"(?:a )?good time", 1.6),
    (r"(?:a )?great time", 2.2),
    (r"(?:a )?lot of fun", 2.1),
    (r"(?:a )?lot to (?:enjoy|admire|like|love)", 1.8),
    (r"plenty to (?:enjoy|admire|like|love)", 1.8),
    (r"(?:all|more) style (?:and|than) (?:no )?substance", -1.8),
    (r"style over substance", -1.6),
    (r"(?:more|better) than (?:enough|adequate)", 1.3),
    (r"(?:not|never) (?:quite )?enough", -0.8),
    (r"(?:a )?mixed bag", -0.5),
    (r"hit and miss", -0.7),
    (r"(?:by the numbers|paint by numbers|paint-by-numbers)", -1.4),
    (r"(?:by the book|run of the mill|run-of-the-mill)", -1.0),
    (r"(?:tries|tried|trying) too hard", -1.5),
    (r"(?:too|far too|much too) (?:long|slow|loud|dull|boring|predictable)", -1.7),
    (r"(?:too|far too|much too) (?:cute|clever|sentimental) for (?:its|its own) (?:own )?good", -1.4),
    (r"(?:well|beautifully|expertly) (?:acted|directed|written|made|crafted|performed|shot)", 1.7),
    (r"(?:poorly|badly|clumsily) (?:acted|directed|written|made|crafted|performed|shot)", -1.8),
    (r"(?:first|top)[ -]rate", 1.8),
    (r"(?:second|third)[ -]rate", -1.6),
    (r"(?:a )?tour de force", 2.5),
    (r"(?:a )?breath of fresh air", 2.1),
    (r"(?:a )?breath of fresh air", 2.1),
    (r"(?:a )?labor of love", 1.4),
    (r"(?:a )?labour of love", 1.4),
    (r"(?:a )?work of art", 2.2),
    (r"(?:an? )?instant classic", 2.5),
    (r"(?:the )?real deal", 1.8),
    (r"(?:a )?pleasant surprise", 1.8),
    (r"(?:a )?pleasant diversion", 1.3),
    (r"(?:a )?guilty pleasure", 1.4),
    (r"(?:a )?rare treat", 2.0),
    (r"(?:a )?sheer delight", 2.3),
    (r"(?:a )?complete mess", -2.5),
    (r"(?:a )?total mess", -2.5),
    (r"(?:a )?hot mess", -2.1),
    (r"(?:a )?train wreck", -2.5),
    (r"(?:a )?lost cause", -1.9),
    (r"(?:a )?missed opportunity", -1.8),
    (r"too little too late", -1.5),
    (r"not much fun", -1.5),
    (r"no fun", -1.5),
    (r"no sense of (?:humor|humour|fun)", -1.6),
    (r"(?:not|no) (?:a )?masterpiece", -0.8),
    (r"no great shakes", -1.3),
    (r"nothing to write home about", -1.3),
    (r"(?:not|never) for everyone", -0.2),
    (r"(?:not|never) for the faint of heart", 0.1),
]

PHRASE_PATTERNS = [
    (re.compile(r"(?<![a-z])(?:" + pattern + r")(?![a-z])"), value)
    for pattern, value in PHRASES
]

TOKEN_RE = re.compile(r"[a-z]+(?:'[a-z]+)?|\d+|[.,!?;:\-]")
NEGATORS = {
    "not", "no", "never", "neither", "nor", "without", "hardly",
    "barely", "rarely", "seldom", "cannot", "can't", "couldn't",
    "didn't", "doesn't", "don't", "isn't", "aren't", "wasn't", "weren't",
    "won't", "wouldn't", "shouldn't", "hasn't", "haven't", "hadn't",
    "lack", "lacks", "lacking", "lacked",
}
STOPS = {".", "!", "?", ";", ":", ",", "but", "however", "yet", "although", "though"}
BOOSTERS = {
    "very": 1.35, "really": 1.25, "extremely": 1.55, "utterly": 1.5,
    "absolutely": 1.5, "totally": 1.4, "completely": 1.4, "entirely": 1.3,
    "truly": 1.3, "deeply": 1.3, "especially": 1.25, "particularly": 1.2,
    "remarkably": 1.3, "extraordinarily": 1.5, "incredibly": 1.4,
    "exceptionally": 1.4, "highly": 1.3, "genuinely": 1.2,
    "thoroughly": 1.3, "wonderfully": 1.25, "brilliantly": 1.25,
    "quite": 1.15, "so": 1.25, "most": 1.2, "more": 1.1,
}
DIMINISHERS = {
    "somewhat": 0.65, "slightly": 0.55, "mildly": 0.55,
    "rather": 0.85, "fairly": 0.8, "reasonably": 0.8,
    "almost": 0.7, "nearly": 0.75, "partly": 0.75,
}


def _contrast_markers(tokens):
    markers = []
    for i, token in enumerate(tokens):
        if token not in {"but", "however", "yet", "nevertheless", "nonetheless"}:
            continue
        before = tokens[max(0, i - 4):i]
        after = tokens[i + 1:i + 3]
        if token == "but":
            if before and before[-1] in {"anything", "nothing", "all", "help"}:
                continue
            if "only" in before and ("also" in after or "even" in after):
                continue
            if any(tokens[j] == "only" for j in range(max(0, i - 12), i)) and after and after[0] == "also":
                continue
        if token == "yet" and ((before and before[-1] == "not") or (after and after[0] == "another")):
            continue
        markers.append(i)
    return markers


def _subordinate_ranges(tokens):
    ranges = []
    for i, token in enumerate(tokens):
        if token not in {"although", "though", "despite", "whereas", "while"}:
            continue
        # Clause-initial concessive expressions are usually subordinate to
        # the main clause after the next comma.
        if i > 0 and tokens[i - 1] not in {".", "!", "?", ";"}:
            continue
        for j in range(i + 1, min(len(tokens), i + 40)):
            if tokens[j] == ",":
                ranges.append((i, j))
                break
            if tokens[j] in {".", "!", "?", ";"}:
                break
    return ranges


def _modifier(tokens, index, score, phrase_text=""):
    previous = []
    j = index - 1
    while j >= 0 and len(previous) < 5:
        token = tokens[j]
        if token in STOPS:
            break
        previous.append((j, token))
        j -= 1

    factor = 1.0
    for distance, (_, token) in enumerate(previous[:3]):
        if token in BOOSTERS:
            factor *= 1.0 + (BOOSTERS[token] - 1.0) / (1.0 + distance * 0.35)
            break
        if token in DIMINISHERS:
            factor *= DIMINISHERS[token]
            break

    negations = 0
    for j, token in previous:
        if token not in NEGATORS:
            continue
        if token == "not" and j + 1 < len(tokens) and tokens[j + 1] in {"only", "just", "merely"}:
            continue
        if token == "no" and j + 1 < len(tokens) and tokens[j + 1] in {"doubt", "wonder", "question"}:
            continue
        if token in {"lack", "lacks", "lacking", "lacked"} and score < 0:
            continue
        negations += 1

    if negations % 2:
        score = -score * (0.8 if score > 0 else 0.7)

    return score * factor


def predict(state):
    if not isinstance(state, str):
        return {"answer": "positive"}

    text = unicodedata.normalize("NFKC", state).casefold()
    text = text.replace("’", "'").replace("‘", "'")
    matches = list(TOKEN_RE.finditer(text))
    tokens = [match.group() for match in matches]
    if not tokens:
        return {"answer": "positive"}

    starts = [match.start() for match in matches]
    ends = [match.end() for match in matches]
    candidates = []
    for order, (pattern, value) in enumerate(PHRASE_PATTERNS):
        for match in pattern.finditer(text):
            candidates.append((match.start(), match.end(), order, value, match.group()))
    candidates.sort(key=lambda item: (-(item[1] - item[0]), item[2], item[0]))

    occupied = [False] * len(tokens)
    units = []
    for start, end, order, value, phrase in candidates:
        indexes = [i for i in range(len(tokens)) if starts[i] < end and ends[i] > start]
        if not indexes or any(occupied[i] for i in indexes):
            continue
        for i in indexes:
            occupied[i] = True
        units.append((indexes[0], value, phrase))

    for i, token in enumerate(tokens):
        if occupied[i] or token not in LEXICON:
            continue
        value = LEXICON[token]
        if value:
            units.append((i, value, ""))

    contrasts = _contrast_markers(tokens)
    subordinate = _subordinate_ranges(tokens)
    score = 0.0

    for index, value, phrase in units:
        value = _modifier(tokens, index, value, phrase)
        if contrasts:
            if index < contrasts[-1]:
                value *= 0.65
            elif index > contrasts[-1]:
                value *= 1.35
        for start, end in subordinate:
            if start < index < end:
                value *= 0.65
            elif index > end:
                value *= 1.15
        score += value

    # "More X than Y" generally emphasizes X over Y.
    for i, token in enumerate(tokens):
        if token != "than":
            continue
        previous = tokens[max(0, i - 6):i]
        if "more" not in previous and "less" not in previous:
            continue
        left = [(p, v) for p, v, _ in units if max(0, i - 6) <= p < i]
        right = [(p, v) for p, v, _ in units if i < p <= i + 5]
        if left and right:
            if "more" in previous:
                score += 0.2 * left[-1][1] - 0.35 * right[0][1]
            else:
                score -= 0.35 * left[-1][1]
        break

    return {"answer": "negative" if score < -0.05 else "positive"}