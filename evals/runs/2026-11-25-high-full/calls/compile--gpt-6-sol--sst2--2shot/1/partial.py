import re
import unicodedata


def _words(text):
    return text.split()


_LEXICON = {}


def _add(text, score):
    for word in _words(text):
        _LEXICON[word] = score


_add(
    "masterpiece masterful excellent superb brilliant extraordinary exceptional "
    "outstanding phenomenal magnificent wonderful amazing terrific fantastic "
    "flawless breathtaking exhilarating hilarious unforgettable riveting "
    "captivating enthralling triumphant triumph genius gem dazzling delightful "
    "stunning ingenious",
    3.1,
)
_add(
    "great best perfect marvelous marvellous splendid sensational spectacular "
    "remarkable beautiful compelling engrossing gripping fascinating mesmerizing "
    "mesmerising enchanting inspiring inspired powerful terrific",
    2.7,
)
_add(
    "good enjoyable entertaining engaging charming amusing witty clever smart "
    "imaginative original inventive fresh funny humorous moving touching poignant "
    "heartfelt lovely gorgeous effective satisfying suspenseful thrilling exciting "
    "insightful honest authentic genuine believable convincing accomplished "
    "polished skillful skilful assured deft intelligent perceptive sophisticated "
    "stylish energetic vibrant lively warm humane tender refreshing surprising "
    "unpredictable worthwhile rewarding memorable admirable impressive",
    2.1,
)
_add(
    "fun pleasure delightful thoughtful thought-provoking nuanced subtle sharp "
    "taut brisk rich vivid elegant graceful skillfully beautifully expertly "
    "affecting absorbing involving immersive uplifting joyful likable likeable "
    "sympathetic endearing charismatic appealing entertainingly",
    1.8,
)
_add(
    "solid strong fine decent agreeable pleasant sweet cute interesting intriguing "
    "emotional revealing creative ambitious sincere credible coherent competent "
    "promising enjoyable cleverness depth substance heart humanity charm humor "
    "humour wit imagination originality vitality warmth tenderness insight "
    "intelligence artistry craftsmanship artistry",
    1.25,
)
_add(
    "love loved loves loving adore adores adored favorite favourite recommend "
    "recommended recommends praise praised praises acclaim acclaimed applause "
    "enjoy enjoyed enjoys appreciate appreciated admire admired delight delights "
    "delighted pleasure pleasures entertaining entertainingly",
    2.3,
)
_add(
    "success successful succeeds succeed entertaining engrossing entertainingly "
    "works worked working worthwhile worth effective effectively triumphs "
    "thrills thrilled thrillingly shines shine shining sparkles sparkle "
    "sparkling excels excel excellent",
    1.8,
)

_add(
    "worst terrible awful horrible dreadful abysmal atrocious appalling "
    "abominable execrable unwatchable insufferable intolerable unbearable "
    "worthless disastrous disaster fiasco catastrophe garbage rubbish trash "
    "crap pathetic",
    -3.3,
)
_add(
    "bad poor disappointing disappoints disappointed dismal miserable painful "
    "embarrassing embarrassment tedious tiresome boring dull lifeless joyless "
    "humorless humourless unfunny uninspired unimaginative pointless inept "
    "incompetent amateurish incoherent laughable",
    -2.5,
)
_add(
    "predictable formulaic derivative generic clichéd cliched cliché cliche "
    "corny cheesy schmaltzy manipulative contrived forced strained artificial "
    "phony hollow empty flat shallow superficial flimsy confusing muddled "
    "unfocused sloppy clumsy awkward uneven inconsistent aimless mundane "
    "plodding sluggish dreary stale tired weak forgettable unmemorable "
    "frustrating irritating annoying grating obnoxious offensive insulting "
    "tasteless juvenile puerile stupid dumb idiotic nonsensical ludicrous "
    "preposterous pretentious smug self-indulgent overblown bloated overwrought "
    "excessive overdone heavy-handed preachy didactic sanctimonious ham-fisted "
    "pedestrian mediocre unremarkable unimpressive lackluster lacklustre "
    "halfhearted wooden stilted unconvincing miscast",
    -2.0,
)
_add(
    "repetitive repetition tiresome tedious lengthy overlong interminable "
    "predictability mediocrity cliché cliches clichés banality banal "
    "trite hackneyed shopworn recycled stale derivative cheap shoddy "
    "unoriginal uninventive uninteresting unappealing unsatisfying "
    "unengaging unexciting uninvolving unmoving unpersuasive unbelievable "
    "implausible absurdity absurdities clunkers clunker mess messy "
    "failure fails failed failing flop flops flopped dud duds",
    -2.1,
)
_add(
    "ordinary routine conventional bland dry thin slight slow sluggish "
    "weakly poorly badly flimsy marginal underwhelming underwhelmed "
    "underwhelms underdeveloped underwritten simplistic strained "
    "sappy sentimental silly childish crude vulgar gratuitous grim "
    "depressing bleak hopeless charmless soulless tediousness "
    "unnecessary unnecessaryness forgettable pedestrian",
    -1.25,
)
_add(
    "flaw flaws flawed fault faults problem problems mistake mistakes "
    "shortcoming shortcomings weakness weaknesses disappointment "
    "disappointingness confusion boredom tedium dullness annoyance "
    "irritation pretension pretensions cliche",
    -1.6,
)
_add(
    "waste wasted wastes wasting squander squandered squanders "
    "drag drags dragged dragging bore bores bored boring "
    "annoy annoys annoyed annoying irritate irritates irritated "
    "frustrate frustrates frustrated frustrates "
    "disappoint disappointed disappoints disappointing "
    "fail fails failed failing stumble stumbles stumbled "
    "falter falters faltered flounder flounders floundered "
    "suffer suffers suffered suffering",
    -1.9,
)
_add("good", 2.4)
_add("great", 2.9)
_add("best", 3.2)
_add("perfect", 3.0)
_add("bad", -2.7)
_add("worst", -3.5)
_add("interesting", 1.35)
_add("surprising", 1.9)
_add("revealing", 1.5)
_add("emotional", 0.8)
_add("fun", 2.1)
_add("worth", 1.5)
_add("like likes liked", 1.35)
_add("hate hates hated", -2.5)
_add("dislike dislikes disliked", -1.8)
_add("lacks lack lacking lacked", -1.5)
_add("misses missed missing", -1.0)
_add("redeeming redemption", 1.5)
_add("beautifully wonderfully brilliantly superbly perfectly", 2.3)
_add("unfortunately sadly regrettably alas", -1.6)
_add("fortunately thankfully happily", 1.3)
_add("yes bravo", 1.3)
_add("nope ugh", -1.5)
_add("mediocre", -2.1)
_add("entertain entertains entertained entertaining", 2.0)
_add("engage engages engaged engaging", 1.9)
_add("satisfy satisfies satisfied satisfying", 2.0)
_add("impress impresses impressed impressive", 2.0)
_add("charm charms charmed charming", 2.0)
_add("amuse amuses amused amusing", 1.8)
_add("fascinate fascinates fascinated fascinating", 2.2)
_add("captivate captivates captivated captivating", 2.4)
_add("inspire inspires inspired inspiring", 2.2)
_add("surprise surprises surprised surprising", 1.7)
_add("thrill thrills thrilled thrilling", 2.1)
_add("excite excites excited exciting", 1.9)
_add("interest interests interested interesting", 1.3)
_add("recommend recommends recommended recommending", 2.1)
_add("succeed succeeds succeeded successful", 1.8)
_add("work works worked working", 1.25)

_PHRASES = {}


def _phrase(text, score):
    for item in text.split("|"):
        _PHRASES[tuple(item.strip().split())] = score


_phrase(
    "must see|must watch|well worth|worth watching|worth seeing|"
    "worth your time|worth the time|highly recommended|"
    "strongly recommended|a delight|a pleasure|a joy|"
    "a triumph|a masterpiece|a gem|one of the best|"
    "among the best|at its best|at their best|"
    "a breath of fresh air|breath of fresh air|"
    "a cut above|stands out|stand out|"
    "not to be missed|do not miss|don't miss|"
    "cannot recommend enough|can't recommend enough",
    3.1,
)
_phrase(
    "well done|well made|well written|well acted|well directed|"
    "beautifully shot|beautifully written|beautifully acted|"
    "beautifully directed|beautifully crafted|"
    "strong performances|great performances|excellent performances|"
    "fine performances|solid performances|"
    "pleasant surprise|welcome surprise|"
    "good time|great time|so much fun|"
    "a lot of fun|lots of fun|"
    "laugh out loud|laugh out loud funny|"
    "keeps you guessing|kept me guessing|"
    "keeps you on the edge of your seat|"
    "kept me on the edge of my seat",
    2.3,
)
_phrase(
    "not bad|not half bad|not at all bad|far from bad|"
    "so bad it's good|so bad it is good|"
    "better than expected|better than it sounds|"
    "better than it looks|better than most|"
    "more than the sum of its parts",
    2.3,
)
_phrase(
    "waste of time|waste of money|a waste of|"
    "not worth|not worth watching|not worth seeing|"
    "not worth your time|not recommended|"
    "cannot recommend|can't recommend|"
    "avoid at all costs|stay away|"
    "one of the worst|among the worst|"
    "the worst|a disaster|a mess|"
    "an embarrassment|a disappointment|"
    "missed opportunity|a missed opportunity|"
    "fails to deliver|fails to impress|"
    "falls flat|fall flat|fell flat|"
    "falls apart|fall apart|fell apart|"
    "does not work|doesn't work|"
    "does not deliver|doesn't deliver",
    -3.0,
)
_phrase(
    "too much|too too much|too little|too long|"
    "too slow|too predictable|too sentimental|"
    "too clever by half|too good to be true|"
    "not enough|not very good|not so good|"
    "not particularly good|not that good|"
    "not as good as|no good|"
    "no fun|no laughs|few laughs|"
    "nothing special|nothing new|"
    "more of the same|by the numbers|"
    "paint by numbers|run of the mill|"
    "half baked|half hearted|"
    "a letdown|a let down|"
    "only good thing|only thing going for|"
    "style over substance|all style and no substance|"
    "tries too hard|trying too hard|"
    "takes itself too seriously|"
    "does not live up to|doesn't live up to|"
    "fails to live up to|never lives up to",
    -2.2,
)
_phrase(
    "a bit of a letdown|could have been better|"
    "should have been better|could be better|"
    "had potential|wasted potential|"
    "nothing to recommend|little to recommend|"
    "no redeeming qualities|no redeeming features|"
    "not funny|not interesting|not entertaining|"
    "not convincing|not compelling|"
    "not particularly interesting",
    -2.0,
)
_phrase("not only|not just|not merely|nothing short of|not without", 0.0)
_phrase("without a doubt|no doubt|all but", 0.0)

_NEGATORS = {
    "not", "no", "never", "neither", "nor", "without", "hardly",
    "barely", "scarcely", "rarely", "seldom", "cannot", "aint",
    "lack", "lacks", "lacked", "lacking",
}
_WEAKENERS = {"somewhat", "slightly", "mildly", "rather", "fairly", "kindof"}
_BOOSTERS = {
    "very", "really", "extremely", "incredibly", "utterly",
    "absolutely", "completely", "totally", "deeply", "highly",
    "especially", "particularly", "exceptionally", "remarkably",
    "immensely", "intensely", "so", "truly", "more", "most",
}
_STOPS = {".", "!", "?", ";", ":", ",", "--"}
_CONTRAST = {"but", "however", "yet", "nevertheless", "nonetheless"}
_CONCESSIONS = {"although", "though", "despite", "while"}


def _tokens(text):
    text = unicodedata.normalize("NFKC", text).lower()
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r"n[' ]t\b", " not", text)
    return re.findall(r"[a-z]+(?:'[a-z]+)*|[0-9]+|--|[.!?;,:]", text)


def _position_weights(tokens):
    weights = [1.0] * len(tokens)
    pivot = None
    for i, word in enumerate(tokens):
        if word in _CONTRAST and 0 < i < len(tokens) - 1:
            if tokens[i - 1] not in {"all", "nothing", "anything", "everything"}:
                pivot = i
    if pivot is not None:
        for i in range(pivot):
            weights[i] *= 0.78
        for i in range(pivot + 1, len(tokens)):
            weights[i] *= 1.5

    for i, word in enumerate(tokens):
        if word not in _CONCESSIONS:
            continue
        comma = next(
            (j for j in range(i + 1, len(tokens))
             if tokens[j] in {",", ";", ".", "!", "?"}),
            None,
        )
        if i <= 2 and comma is not None:
            for j in range(i + 1, comma):
                weights[j] *= 0.67
            for j in range(comma + 1, len(tokens)):
                weights[j] *= 1.3
        elif i > 2:
            for j in range(i + 1, len(tokens)):
                weights[j] *= 0.7
    return weights


def _negated(tokens, start):
    count = 0
    seen = 0
    for j in range(start - 1, -1, -1):
        word = tokens[j]
        if word in _STOPS or word in _CONTRAST:
            break
        if word in {"and", "or"} and seen >= 2:
            break
        if word in {"only", "just", "merely"} and j > 0 and tokens[j - 1] == "not":
            continue
        if word in _NEGATORS:
            if word == "not" and j + 1 < len(tokens) and tokens[j + 1] in {
                "only", "just", "merely",
            }:
                continue
            count += 1
        seen += 1
        if seen >= 4:
            break
    return count % 2 == 1


def _word_score(tokens, i):
    word = tokens[i]
    value = _LEXICON.get(word, 0.0)
    if not value:
        return 0.0

    previous = tokens[max(0, i - 3):i]
    if previous and previous[-1] in _BOOSTERS:
        value *= 1.32
    elif len(previous) >= 2 and previous[-2] in _BOOSTERS and previous[-1] not in _STOPS:
        value *= 1.18
    if previous and previous[-1] in _WEAKENERS:
        value *= 0.72

    if _negated(tokens, i):
        value *= -0.9

    if previous and previous[-1] == "less" and word not in {"bad", "poor", "worse", "worst"}:
        value *= -0.85
    if previous and previous[-1] == "too":
        if value < 0:
            value *= 1.35
        elif word not in {"funny", "hilarious", "good", "great", "wonderful", "excellent"}:
            value = -max(1.1, value * 0.8)
    return value


def predict(state) -> dict:
    text = state if isinstance(state, str) else ""
    tokens = _tokens(text)
    if not tokens:
        return {"answer": "negative"}

    weights = _position_weights(tokens)
    total = 0.0
    i = 0
    while i < len(tokens):
        match_length = 0
        phrase_score = 0.0
        for length in range(min(9, len(tokens) - i), 1, -1):
            phrase = tuple(tokens[i:i + length])
            if phrase in _PHRASES:
                match_length = length
                phrase_score = _PHRASES[phrase]
                break
        if match_length:
            if phrase_score:
                total += phrase_score * max(weights[i:i + match_length])
            i += match_length
        else:
            total += _word_score(tokens, i) * weights[i]
            i += 1

    return {"answer": "positive" if total > 0 else "negative"}