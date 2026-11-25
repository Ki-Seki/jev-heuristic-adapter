import re
import unicodedata


def _word_groups():
    groups = (
        (3.2, """
            masterpiece masterpieces brilliant superb outstanding excellent exceptional
            phenomenal extraordinary magnificent marvelous marvellous fantastic terrific
            spectacular stunning dazzling exquisite flawless perfect perfection triumph
            triumphant riveting enthralling mesmerizing mesmerising spellbinding gripping
            hilarious ingenious inspired unforgettable remarkable phenomenal
        """),
        (2.1, """
            good great wonderful beautiful delightful delicious enjoyable entertaining
            engaging engrossing compelling impressive effective affecting moving touching
            poignant powerful thoughtful intelligent smart clever witty funny amusing
            charming charm charismatic irresistible fascinating absorbing captivating
            refreshing refreshingly imaginative inventive original innovative insightful
            perceptive authentic sincere heartfelt warm heartwarming uplifting inspiring
            inspirational exhilarating exciting thrilling energetic vibrant lively vivid
            stylish elegant polished accomplished skillful skilful confident assured
            convincing credible believable sensitive tender humane rewarding satisfying
            satisfying pleasurable pleasing fun joy joyful joyous lovely lovable loveable
            likable likeable likable appealing endearing adorable memorable amazing
            awesome sublime masterful magical magic rich nuanced subtle sophisticated
            ambitious daring bold audacious beautiful delightful wellcrafted
            taut crisp sharp incisive engrossed engrosses entertains entertained
            delights delighted succeeds successful succeeds works worthwhile
            recommend recommended recommendable best favorite favourite loved love
            loves adores adored enjoyable enjoyable revealing surprising
        """),
        (1.15, """
            better fine decent solid pleasant agreeable appealing promising interesting
            intriguing involving watchable serviceable adequate competent capable
            enjoyable humor humour laughs laughter laugh smile smiles smiling
            entertainingly entertainingly entertaining enjoyability warmth wit
            charm emotion emotional evocative atmospheric atmospheric
            suspense suspenseful tension tense suspenseful dramatic drama
            romantic romance affection affectionate sweet sweetly gentle
            playful mischievous quirky offbeat whimsical cinematic evocative
            ambitious ambitiousness imaginative imagination creativity creative
            artistry artful graceful fluid credible credibility freshness fresh
            energetic energy momentum stylishly craftsmanship wellmade skill
            crafted nicely nicely successful success appeal satisfying satisfaction
            delivers delivered delivers delivers lovely surprisingly
            appreciation appreciate appreciated favorite favourites
        """),
        (-3.2, """
            awful atrocious abysmal appalling horrible horrid dreadful terrible
            disastrous disaster unwatchable unbearable insufferable excruciating
            unendurable execrable revolting repellent repulsive repugnant
            contemptible detestable abomination travesty catastrophe
            rubbish garbage junk trash worthless abysmal worst
            abysmal
        """),
        (-2.15, """
            bad poor weak lousy lame mediocre dull boring tedious tiresome tiresomely
            tiresome laborious slow plodding sluggish dreary lifeless listless
            flat uninspired uninspiring unoriginal uninteresting unengaging
            unfunny humorless humourless joyless charmless pointless aimless
            purposeless meaningless hollow empty shallow vapid vacuous banal
            bland blandness tedious cliched cliche cliches cliche-ridden
            predictable formulaic derivative conventional trite hackneyed
            stale tired repetitive repetitious monotonous monotonously
            pretentious pompous selfimportant selfindulgent indulgent
            contrived forced artificial manipulative sentimental sappy schmaltzy
            mawkish maudlin corny cheesy hokey cloying saccharine
            incoherent confusing confused muddled messy chaotic disjointed
            unfocused uneven unevenly inconsistent implausible unbelievable
            unconvincing unpersuasive unearned unmotivated underdeveloped
            underwritten overwritten overlong overblown overdone overwrought
            overstuffed overstuffed overbearing overproduced overacted
            underwhelming underwhelmed disappointing disappointed disappoints
            disappointing disappointment failure fails failed failing
            frustrating frustrated frustration irritating annoying obnoxious
            grating aggravating infuriating tedious tediousness
            offensive objectionable exploitative gratuitous exploitative
            embarrassing embarrassingly ridiculous absurd silly stupid idiotic
            dumb moronic witless mindless brainless clumsy inept awkward
            incompetent amateurish sloppy careless shoddy cheap tacky
            ugly ugly-looking ugly-looking flimsy thin flimsy
            unmemorable forgettable forgettable forgettably forgettable
            unsatisfying unsatisfied unrewarding uninvolving unappealing
            unsympathetic unlikeable unlikable unlovable unbearable
            predictable predictability predictable painfully pedestrian
            wooden stiff stilted phony fake dishonest inauthentic
            weakly poorly horribly badly terribly
            squandered wasted waste wasting flounders floundering
            tedious dullness boredom bore bored bores
            sucks suck worthless
        """),
        (-1.1, """
            flawed flaws flaw flaws limited limitation limitations slight slightness
            uneven generic routine ordinary average middling modest
            predictable predictably familiar derivative dated outdated
            obvious simplistic simpleminded superficial sketchy thin
            overfamiliar lightweight minor lackluster lacklustre lacklustre
            unremarkable bland plain weakish undercooked underdeveloped
            questionable questionablely problematic problematic
            unsteady uncertain clunky creaky strained tedious
            predictable sentimentality selfconscious selfconsciously
            disappointment disappointing unspectacular unspecial
            pedestrian conventional conventionality derivative
            disappointing disappointments unfocused slack slackness
            cloying overlong overly overdone overacted
            overfamiliar slight slighter slowish
        """),
    )
    result = {}
    for value, words in groups:
        for word in words.split():
            result[word] = value
    return result


_WORDS = _word_groups()

# Multiword judgments have priority over their component words.
_PHRASE_DATA = """
one of the best|4
one of the worst|-4
among the best|3.5
among the worst|-3.5
the best film|3.5
the worst film|-4
a must see|3.5
must see|3
must watch|3
must be seen|3
do not miss|3
don't miss|3
not to be missed|3
well worth seeing|3
well worth watching|3
worth seeing|2.5
worth watching|2.5
worth a look|2
worth your time|2.5
worth the time|2.5
worth the price|2
worth the ticket|2
worth a watch|2.5
worth revisiting|2
worth the effort|2
worthwhile experience|2
well worth|2.5
not worth seeing|-3
not worth watching|-3
not worth a look|-2.5
not worth your time|-3
not worth the time|-3
not worth the price|-2.5
not worth the ticket|-2.5
not worth a watch|-3
not worth the effort|-2.5
not worth it|-3
is worth it|2.5
waste of time|-3.5
waste of money|-3.5
waste of talent|-2.8
waste of talents|-2.8
waste of a good cast|-3
complete waste|-3
a waste|-2
not a waste of time|2
is no waste of time|2
time well spent|2.5
money well spent|2.5
a pleasure to watch|3
a pleasure to see|3
a joy to watch|3
a joy to behold|3
a treat to watch|3
a treat to see|3
pure pleasure|3
pure joy|3
a delight|2.8
a treat|2.5
a gem|3
hidden gem|3
rare gem|3
a winner|2.5
a triumph|3
a masterpiece|3.5
an instant classic|3.5
a classic|2.5
a great film|3
a great movie|3
a good film|2
a good movie|2
good entertainment|2
great entertainment|2.8
highly recommended|3.5
highly recommend|3.5
strongly recommended|3
strongly recommend|3
cannot recommend it enough|4
can't recommend it enough|4
easy to recommend|2.5
hard to recommend|-2.5
difficult to recommend|-2.5
would recommend|2
would not recommend|-3
wouldn't recommend|-3
not recommended|-2.5
have to see|2
have to watch|2
should see it|2
should watch it|2
stay away|-3
avoid at all costs|-4
best avoided|-3
avoid this movie|-3
avoid this film|-3
don't bother|-3
do not bother|-3
not worth bothering|-3
save your money|-3
save your time|-3
skip this movie|-2.5
skip this film|-2.5
give it a miss|-2.5
can do without|-2
could do without|-2
no reason to see|-2.5
no reason to watch|-2.5
little reason to see|-2.5
little reason to watch|-2.5
no reason to care|-2.5
hard to care|-2.5
difficult to care|-2.5
hard to sit through|-3
difficult to sit through|-3
hard to watch|-2
a chore to watch|-3
a chore to sit through|-3
a chore to sit through|-3
a struggle to sit through|-3
a slog to watch|-3
a slog to sit through|-3
puts you to sleep|-3
put me to sleep|-3
falls asleep|-1.5
fell asleep|-2.5
didn't care|-2
did not care|-2
couldn't care less|-2.5
could not care less|-2.5
no fun|-2.5
isn't fun|-2
not fun|-2
not funny|-2.8
isn't funny|-2.8
not very funny|-2.5
not particularly funny|-2.5
not funny enough|-2.5
funny enough|1.6
very funny|3
genuinely funny|3
laugh out loud|2.8
laugh out loud funny|3.3
laugh a minute|2.5
lots of laughs|2.5
plenty of laughs|2.5
few laughs|-2
very few laughs|-3
not many laughs|-2.5
no laughs|-2.5
barely a laugh|-2.5
never raises a laugh|-3
laughs are few|-2
falls flat|-2.5
fall flat|-2.5
fell flat|-2.5
falls short|-2.5
fall short|-2.5
fell short|-2.5
comes up short|-2.5
comes up empty|-2.5
comes up dry|-2
leaves much to be desired|-3
left much to be desired|-3
a lot to be desired|-2
nothing to offer|-3
little to offer|-2.5
has little to offer|-3
has nothing to offer|-3.5
doesn't have much to offer|-3
does not have much to offer|-3
not much to offer|-2.5
no substance|-2.5
little substance|-2
lacks substance|-2.5
lacking in substance|-2.5
no depth|-2
lacks depth|-2
lacking in depth|-2
lack of imagination|-2.5
lack of originality|-2.5
lack of ideas|-2.5
lack of focus|-2
lack of energy|-2
lack of humor|-2.5
lack of humour|-2.5
lacks imagination|-2.5
lacks originality|-2.5
lacks ideas|-2.5
lacks focus|-2
lacks energy|-2
lacks humor|-2.5
lacks humour|-2.5
lacks charm|-2.5
no shortage of humor|2.5
no shortage of humour|2.5
no shortage of charm|2.5
no lack of charm|2.5
has no idea|-2
have no idea|-2
doesn't know what it wants to be|-3
does not know what it wants to be|-3
doesn't know what to do|-2.5
does not know what to do|-2.5
has its moments|0.8
has some moments|0.6
has a few moments|0.4
has its charms|1
has its virtues|1
has its merits|1
has its pleasures|1.2
not without its charms|1.5
not without charm|1.5
not without its merits|1.5
not without its pleasures|1.5
not without merit|1.5
nothing short of brilliant|3.5
nothing short of wonderful|3
nothing short of amazing|3.5
nothing short of a masterpiece|4
nothing less than a masterpiece|4
nothing if not entertaining|2
nothing if not enjoyable|2
anything but entertaining|-2.5
anything but enjoyable|-2.5
anything but funny|-2.5
anything but original|-2
anything but dull|2
anything but boring|2
far from perfect|-1.5
far from great|-2
far from good|-2
far from bad|1.7
far from boring|2
far from dull|2
not half bad|2
not so bad|1.8
not that bad|1.8
not all bad|1.4
not too bad|1.6
not bad at all|2.5
not bad|1.5
is no masterpiece|-2
not a masterpiece|-2
no masterpiece|-2
not a classic|-1.7
no classic|-1.7
not a great movie|-2
not a great film|-2
not a good movie|-2
not a good film|-2
not very good|-2
not particularly good|-2
not that good|-2
not good enough|-2.5
isn't good enough|-2.5
not good|-2
no good|-2
not great|-1.8
isn't great|-1.8
not particularly interesting|-2
not interesting|-2
not very interesting|-2
not entertaining|-2.5
not particularly entertaining|-2.2
not enjoyable|-2.5
not compelling|-2
not engaging|-2
not convincing|-2
not satisfying|-2
not enough to save|-2.5
not enough to rescue|-2.5
not enough to make up for|-2.5
not nearly enough|-2
not enough|-1
too little too late|-2.5
too little|-1.3
too much of a good thing|-1.5
too much for its own good|-2
tries too hard|-2
trying too hard|-2
too clever for its own good|-2
too cute for its own good|-2
too long for its own good|-2
too long|-1.8
drags on|-2.5
drags along|-2.2
goes on too long|-2.5
outstays its welcome|-2.5
overstays its welcome|-2.5
wears out its welcome|-2.5
runs out of steam|-2.5
loses steam|-2
loses its way|-2.5
loses its momentum|-2
loses focus|-2
never quite takes off|-2.5
doesn't quite work|-2
does not quite work|-2
doesn't work|-2.5
does not work|-2.5
doesn't really work|-2.5
does not really work|-2.5
doesn't add up|-2
does not add up|-2
doesn't deliver|-2.5
does not deliver|-2.5
fails to deliver|-2.8
fails to impress|-2.5
fails to entertain|-3
fails to engage|-2.5
fails to convince|-2.5
fails to satisfy|-2.5
fails to move|-2
fails to live up to|-2.5
doesn't live up to|-2.5
does not live up to|-2.5
doesn't measure up|-2.5
does not measure up|-2.5
doesn't hold up|-2
does not hold up|-2
doesn't pay off|-2
does not pay off|-2
doesn't go anywhere|-2.5
does not go anywhere|-2.5
goes nowhere|-2.5
leads nowhere|-2
amounts to nothing|-2.5
amounts to very little|-2
doesn't amount to much|-2
does not amount to much|-2
could have been better|-2.5
could be better|-1.5
should have been better|-2.5
deserved better|-2.5
better than nothing|0.3
better than most|2
better than expected|2
better than it sounds|2
better than it looks|2
better than its title|2
better than the title|2
better than the trailer|2
better than the original|2
better than the average|2
better than average|2
worse than expected|-2.5
worse than it sounds|-2
worse than the original|-2.5
worse than average|-2
much worse|-2.5
much better|2.5
no better than|-2
little better than|-2
no worse than|0.8
more of the same|-1.3
nothing new|-1.5
nothing new to offer|-2.5
nothing special|-2
nothing to write home about|-2
nothing memorable|-2
easily forgotten|-2
easily forgettable|-2
instantly forgettable|-2.5
forgettable experience|-2
pleasant surprise|2.5
nice surprise|2
welcome surprise|2
a breath of fresh air|3
breath of fresh air|2.5
a fresh take|2
a new twist|1.5
pleasant enough|0.8
good enough|1.2
entertaining enough|1.2
well enough|0.7
just enough|0.4
only just|0
barely watchable|-1.7
barely tolerable|-2
barely entertaining|-2
barely funny|-2
barely interesting|-2
hardly entertaining|-2
hardly funny|-2
hardly interesting|-2
sorely lacking|-2.2
badly needed|-1
a guilty pleasure|1.5
guilty pleasure|1.5
so bad it's good|1
so bad it is good|1
so bad that it's good|1
so bad that it is good|1
laughably bad|-2.5
unintentionally funny|-2
unintentionally hilarious|-2
in a good way|1.2
in a bad way|-1.5
for all its flaws|0
despite its flaws|0
in spite of its flaws|0
despite its shortcomings|0
for all its shortcomings|0
makes up for its flaws|2
more than makes up for|2.5
makes up for|1.5
redeems itself|2
saving grace|1
only saving grace|-1.5
redeeming quality|0.8
few redeeming qualities|-2.5
no redeeming qualities|-3
without a single redeeming quality|-3.5
more style than substance|-2
style over substance|-2
all style and no substance|-2.8
all surface and no substance|-2.5
form over substance|-2
empty spectacle|-2
visual feast|2
feast for the eyes|2.5
a feast for the eyes|2.5
beautifully shot|2.5
beautifully filmed|2.5
beautifully directed|2.5
beautifully written|2.5
beautifully acted|2.5
well acted|2
well written|2
well directed|2
well made|2
well executed|2
well crafted|2
well paced|2
well told|2
well conceived|2
well played|1.5
well done|2
poorly acted|-2.5
poorly written|-2.5
poorly directed|-2.5
poorly made|-2.5
poorly executed|-2.5
poorly paced|-2
badly acted|-2.5
badly written|-2.5
badly directed|-2.5
badly made|-2.5
beautiful to look at|2
great to look at|1.5
nothing to look at|-1.5
a joy to behold|3
a sight to behold|2
on the edge of your seat|2.5
edge of your seat|2
keeps you guessing|2
kept me guessing|2
keeps you interested|2
holds your attention|2
held my attention|2
holds our attention|2
keeps your attention|2
keeps the audience engaged|2
keeps you entertained|2.5
keeps you laughing|2.5
kept me laughing|2.5
never a dull moment|2.5
never dull|2
never boring|2
not boring|1.4
not dull|1.3
never disappoints|2
does not disappoint|2.5
doesn't disappoint|2.5
didn't disappoint|2.5
did not disappoint|2.5
won't disappoint|2.5
will not disappoint|2.5
doesn't fail to impress|2.5
does not fail to impress|2.5
fails to disappoint|2
never fails to entertain|2.5
never fails to amuse|2.5
hard not to like|2
impossible not to like|2.5
hard not to love|2.5
impossible not to love|3
can't help but like|2
cannot help but like|2
can't help but love|2.5
cannot help but love|2.5
hard to resist|2
impossible to resist|2.5
no denying its charm|2
no denying its appeal|2
can't resist|1.5
cannot resist|1.5
can't help smiling|2
cannot help smiling|2
puts a smile on your face|2.5
put a smile on my face|2.5
warms the heart|2
tugs at the heartstrings|1
rings true|2
hits the mark|2
hits all the right notes|2.5
strikes the right balance|2
gets it right|2
gets everything right|3
gets it wrong|-2
gets everything wrong|-3
misses the mark|-2.5
misses the point|-2.5
missed opportunity|-2.5
a missed opportunity|-2.5
wasted opportunity|-2.5
lost opportunity|-2
wasted potential|-2.5
squanders its potential|-2.5
doesn't fulfill its potential|-2
does not fulfill its potential|-2
lives up to its potential|2
lives up to expectations|2
lived up to expectations|2
exceeds expectations|2.5
exceeded expectations|2.5
surpasses expectations|2.5
"""

_PHRASES = []
for _line in _PHRASE_DATA.strip().splitlines():
    _phrase, _value = _line.rsplit("|", 1)
    _PHRASES.append((tuple(_phrase.strip().replace("'", "").split()), float(_value)))
_PHRASES.sort(key=lambda item: len(item[0]), reverse=True)
_PHRASES_BY_FIRST = {}
for _phrase, _value in _PHRASES:
    _PHRASES_BY_FIRST.setdefault(_phrase[0], []).append((_phrase, _value))

_STEMS = (
    ("disappoint", -2.2), ("entertain", 1.8), ("enjoy", 1.8),
    ("engross", 2), ("enthrall", 2.4), ("captivat", 2.2),
    ("fascinat", 1.8), ("mesmeriz", 2.5), ("mesmeris", 2.5),
    ("riveting", 2.8), ("compell", 1.8), ("impress", 1.9),
    ("charm", 1.8), ("delight", 2.1), ("amuse", 1.7),
    ("amus", 1.7), ("hilar", 2.7), ("inspir", 2),
    ("exhilarat", 2.5), ("thrill", 1.8), ("mov", 0),
    ("heartwarm", 2.1), ("touch", 0), ("satisf", 1.8),
    ("reward", 1.7), ("recommend", 2), ("refresh", 1.5),
    ("surpris", 1.2), ("reveal", 1.1), ("convinc", 1.7),
    ("imaginat", 1.6), ("invent", 1.5), ("masterpiec", 3.2),
    ("brillian", 3), ("wonderf", 2.6), ("beautif", 2.2),
    ("stunn", 2.5), ("astonish", 2.3), ("frustrat", -2),
    ("irritat", -2), ("annoy", -2), ("bore", -2.1),
    ("boring", -2.1), ("tedious", -2), ("confus", -1.6),
    ("predictab", -1.8), ("pretenti", -2),
    ("contriv", -2), ("fail", -1.8), ("flaw", -1),
    ("clich", -1.8), ("sentimentalis", -1.3),
    ("sentimentaliz", -1.3), ("unwatchab", -3),
    ("forgettable", -2), ("underwhelm", -2),
    ("overwhelm", 0), ("squander", -2.2),
)
_INTENSIFIERS = {
    "very": 1.3, "really": 1.25, "truly": 1.3, "extremely": 1.5,
    "incredibly": 1.45, "utterly": 1.45, "absolutely": 1.45,
    "completely": 1.35, "totally": 1.35, "thoroughly": 1.3,
    "particularly": 1.2, "especially": 1.25, "remarkably": 1.25,
    "surprisingly": 1.15, "quite": 1.12, "pretty": 1.12,
    "so": 1.2, "highly": 1.25, "deeply": 1.2, "much": 1.25,
    "far": 1.2, "more": 1.15, "most": 1.2, "rather": 1.08,
}
_DIMINISHERS = {
    "somewhat": 0.75, "slightly": 0.65, "mildly": 0.7,
    "occasionally": 0.75, "sometimes": 0.8, "almost": 0.8,
    "barely": 0.45, "hardly": 0.4,
}
_NEGATORS = {
    "not", "never", "no", "without", "neither", "nor", "hardly",
    "rarely", "scarcely", "barely", "cannot",
}
_BOUNDARIES = {".", "!", "?", ";", ",", ":", "--"}


def _normalize(text):
    text = unicodedata.normalize("NFKD", str(text).lower())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("’", "'").replace("`", "'")
    text = re.sub(r"\b(can't|cant)\b", "cannot", text)
    text = re.sub(r"\b(won't|wont)\b", "will not", text)
    text = re.sub(r"\b(ain't|aint)\b", "is not", text)
    text = re.sub(r"\b([a-z]+)n't\b", r"\1 not", text)
    text = re.sub(r"\b([a-z]+)'re\b", r"\1 are", text)
    text = re.sub(r"\b([a-z]+)'ve\b", r"\1 have", text)
    text = re.sub(r"\b([a-z]+)'ll\b", r"\1 will", text)
    text = re.sub(r"\b([a-z]+)'d\b", r"\1 would", text)
    text = re.sub(r"\b([a-z]+)'s\b", r"\1 is", text)
    return text


def _tokenize(text):
    return re.findall(r"[a-z]+|--|[.!?;,:\-]", text)


def _lexical_value(word):
    value = _WORDS.get(word)
    if value is not None:
        return value
    if word.endswith("ly") and len(word) > 5:
        base = word[:-2]
        if base in _WORDS:
            return _WORDS[base] * 0.85
        if base.endswith("i") and base[:-1] + "y" in _WORDS:
            return _WORDS[base[:-1] + "y"] * 0.85
    for stem, score in _STEMS:
        if score and word.startswith(stem) and len(word) - len(stem) <= 7:
            return score
    return 0.0


def _negation_before(tokens, start, covered):
    seen = 0
    for j in range(start - 1, max(-1, start - 6), -1):
        word = tokens[j]
        if word in _BOUNDARIES:
            break
        if word in {"but", "however", "although", "though", "yet", "because"}:
            break
        if word in {"not", "no", "never"}:
            if j + 1 < len(tokens) and tokens[j + 1] in {"only", "just", "merely"}:
                continue
            if word == "no" and j + 1 < len(tokens) and tokens[j + 1] in {
                "matter", "wonder", "doubt", "longer",
            }:
                continue
            if word == "never" and j + 1 < len(tokens) and tokens[j + 1] in {
                "fails", "failed", "fail",
            }:
                continue
            return True
        if word in {"without", "neither", "nor", "hardly", "scarcely", "barely", "cannot"}:
            return True
        if word in {"lack", "lacks", "lacking"}:
            return True
        seen += 1
        if seen >= 4:
            break
    return False


def _reverse(value):
    if value > 0:
        return -max(1.25, abs(value) * 0.85)
    if value < 0:
        return max(1.15, abs(value) * 0.7)
    return 0.0


def _contrast_weights(tokens):
    n = len(tokens)
    weights = [1.0] * n
    positions = []
    for i, word in enumerate(tokens):
        if word in {"but", "however", "yet", "nevertheless", "nonetheless"}:
            if word == "but" and (
                "nothing" in tokens[max(0, i - 3):i]
                or "anything" in tokens[max(0, i - 3):i]
                or "help" in tokens[max(0, i - 3):i]
            ):
                continue
            positions.append((i, "later"))
        elif word in {"although", "though", "whereas"}:
            positions.append((i, "later"))
        elif word == "despite":
            positions.append((i, "despite"))
    if positions:
        index, kind = positions[-1]
        if kind == "despite":
            # After an initial "despite ...," the main clause matters more.
            comma = next((i for i in range(index + 1, n) if tokens[i] == ","), None)
            if index <= 2 and comma is not None:
                for i in range(n):
                    weights[i] = 0.57 if i <= comma else 1.45
            else:
                for i in range(n):
                    weights[i] = 1.3 if i < index else 0.55
        elif index < n - 2:
            for i in range(n):
                weights[i] = 0.65 if i < index else 1.45
    return weights


def _score(text):
    tokens = _tokenize(_normalize(text))
    if not tokens:
        return 0.0
    clean = [word.replace("'", "") for word in tokens]
    n = len(clean)
    covered = [False] * n
    contributions = []

    # Match the longest available judgment at each position, reserving its words.
    for i in range(n):
        if covered[i] or clean[i] in _BOUNDARIES:
            continue
        for phrase, value in _PHRASES_BY_FIRST.get(clean[i], ()):
            end = i + len(phrase)
            if end > n or any(covered[i:end]) or tuple(clean[i:end]) != phrase:
                continue
            if any(word in _BOUNDARIES for word in clean[i:end]):
                continue
            for j in range(i, end):
                covered[j] = True
            if phrase[0] not in {"not", "no", "never", "without", "hardly"}:
                if _negation_before(clean, i, covered):
                    value = _reverse(value)
            contributions.append((i, value))
            break

    for i, word in enumerate(clean):
        if covered[i] or word in _BOUNDARIES:
            continue
        value = _lexical_value(word)
        if not value:
            continue

        # These words commonly describe the subject or genre, not its quality.
        if word in {"emotional", "emotion", "romantic", "romance", "dramatic",
                    "drama", "suspense", "tension", "tense"}:
            value *= 0.55
        if word in {"laugh", "laughs", "laughter", "smile", "smiles"}:
            if i > 0 and clean[i - 1] in {"few", "no", "without", "barely"}:
                value *= 0.3

        if i > 0 and clean[i - 1] in _INTENSIFIERS:
            value *= _INTENSIFIERS[clean[i - 1]]
        elif i > 0 and clean[i - 1] in _DIMINISHERS and clean[i - 1] not in _NEGATORS:
            value *= _DIMINISHERS[clean[i - 1]]

        if _negation_before(clean, i, covered):
            value = _reverse(value)
        contributions.append((i, value))

    weights = _contrast_weights(clean)
    score = sum(value * weights[position] for position, value in contributions)

    # In an explicit comparison with a title or marketing, criticism of the
    # title is less indicative of the critic's opinion of the movie.
    if "than" in clean and any(w in clean for w in ("title", "trailer", "poster")):
        comparison = clean.index("than")
        target_positions = [
            i for i in range(comparison + 1, n)
            if clean[i] in {"title", "trailer", "poster"}
        ]
        if target_positions:
            target = target_positions[0]
            for position, value in contributions:
                if comparison < position <= target and value < 0:
                    score += (-value * weights[position]) * 0.55

    if not contributions:
        if re.search(r"\b(i|we)\s+(?:liked|loved|enjoyed|recommend)\b", " ".join(clean)):
            return 2.0
        if re.search(r"\b(i|we)\s+(?:hated|disliked|regretted)\b", " ".join(clean)):
            return -2.0
    return score


def predict(state) -> dict:
    text = state if isinstance(state, str) else ""
    return {"answer": "positive" if _score(text) > 0.05 else "negative"}