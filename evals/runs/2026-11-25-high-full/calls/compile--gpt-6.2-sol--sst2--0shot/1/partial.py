import re
import unicodedata
from functools import lru_cache


_TEXT_KEYS = (
    "sentence", "text", "reviewtext", "moviereview", "filmreview", "review",
    "inputtext", "sentencetext", "reviewbody", "excerpt", "utterance", "snippet",
    "statement", "comment", "content", "body", "passage", "document", "phrase",
    "input", "example", "data", "instance", "sample", "payload", "state",
    "tokens", "words", "sentences", "texts", "value",
)
_METADATA = {
    "label", "labels", "answer", "sentiment", "target", "category", "split",
    "type", "id", "idx", "index", "question", "instructions", "criteria",
    "outputschema", "title", "movietitle", "filmtitle", "author", "source",
    "language", "rating", "score", "metadata",
}
_TOKEN_RE = re.compile(r"\d+(?:\.\d+)?|[^\W\d_]+(?:'[^\W\d_]+)*|[.!?,;:]", re.UNICODE)


def _text(value, depth=0):
    if depth > 20:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        keys = {
            re.sub(r"[^a-z0-9]", "", k.lower()): k
            for k in value if isinstance(k, str)
        }
        for preferred in _TEXT_KEYS:
            if preferred in keys:
                found = _text(value[keys[preferred]], depth + 1)
                if found.strip():
                    return found
        parts = []
        for key, item in value.items():
            if isinstance(key, str) and re.sub(r"[^a-z0-9]", "", key.lower()) in _METADATA:
                continue
            found = _text(item, depth + 1)
            if found.strip():
                parts.append(found)
        return " ".join(parts)
    if isinstance(value, (list, tuple)):
        return " ".join(
            result for item in value if (result := _text(item, depth + 1)).strip()
        )
    return ""


_TRANSLATE = str.maketrans({
    "’": "'", "‘": "'", "ʼ": "'", "＇": "'", "“": '"', "”": '"',
    "‐": "-", "‑": "-", "–": " ; ", "—": " ; ", "−": "-",
    "…": "...", "\u200b": "", "\ufeff": "",
})


def _normalize(text):
    text = unicodedata.normalize("NFKC", text).translate(_TRANSLATE).lower()
    text = re.sub(r"<\s*br\s*/?\s*>", ". ", text)
    text = re.sub(r"</?(?:i|b|p|em|strong|span|div)(?:\s+[^<>]*)?>", " ", text)
    text = re.sub(r"&(?:apos|#39|#x27);", "'", text)
    text = re.sub(r"&(?:quot|#34);", '"', text)
    text = text.replace("&amp;", " and ").replace("&nbsp;", " ")
    text = re.sub(r"(?<=\w)\s*n\s*'\s*t\b", "n't", text)
    text = re.sub(r"(?<=\w)\s*'\s*(re|ve|ll|d|m|s)\b", r"'\1", text)
    text = re.sub(r"\b(?:can't|cannot|cant)\b", "can not", text)
    text = re.sub(r"\b(?:won't|wont)\b", "will not", text)
    text = re.sub(r"\b(?:shan't)\b", "shall not", text)
    text = re.sub(r"\bain't\b", "is not", text)
    text = re.sub(r"\b(\w+)n't\b", r"\1 not", text)
    text = re.sub(
        r"\b(did|does|do|is|are|was|were|has|have|had|would|should|could|must)nt\b",
        r"\1 not", text,
    )
    text = re.sub(r"\b(i|you|he|she|we|they|it|that|there|what|who)'(re|ve|ll|d|m|s)\b",
                  _expand, text)
    text = re.sub(r"\b(\w+)'s\b", r"\1", text)
    text = re.sub(r"\b(?:meh+|bleh+)\b", "meh", text)
    text = re.sub(r"\bbo+r+i+n+g+\b", "boring", text)
    text = re.sub(r"\b(?:loo+ve|lo+vve+)\b", "love", text)
    text = re.sub(r"\bama+zi+n+g+\b", "amazing", text)
    text = re.sub(r"(?<=\w)-(?=\w)", " ", text)
    return text


def _expand(match):
    stem, ending = match.groups()
    return stem + " " + {
        "re": "are", "ve": "have", "ll": "will", "d": "would",
        "m": "am", "s": "is",
    }[ending]


_WORD_GROUPS = (
    (4.6, """
        masterpiece masterpieces superlative masterclass phenomenal magnificent
        sublime stupendous terrific spectacular outstanding extraordinary
        exceptional exquisite flawless perfect impeccable marvelous marvellous
        stunning unforgettable spellbinding breathtaking peerless transcendent
        brilliant superb fantastic excellent awesome amazing astonishing
        sensational phenomenal tremendous incredible fabulous magnificent
        triumphant faultless unparalleled unequaled unequalled unsurpassed
        love loved loves adored adore adores favorite favourite loved
        mustsee electrifying riveting mesmerizing mesmerising captivating
        spellbound genius
    """),
    (3.25, """
        great wonderful delightful delicious gorgeous beautiful terrific
        impressive remarkable rewarding tremendous terrific admirable
        applaud applause applauseworthy splendid enchanting enthralling
        compelling engrossing absorbing engaging entrancing hypnotic
        hilarious uproarious sideplitting riotous laughoutloud
        fascinating exhilarating thrilling thrillingly rousing stirring
        touching poignant heartwarming heartrending uplifting moving profound
        resonant affecting humane heartfelt soulful tender heartrending
        outstanding enjoyable entertaining pleasurable gratifying satisfying
        endearing charming irresistible lovable loveable likable likeable
        pleasing appealing winning winsome delightful tasty flavorful
        innovative inventive imaginative inspired ingenious creative original
        clever witty smart insightful perceptive observant intelligent canny
        thoughtful articulate eloquent deft deftly assured confident
        accomplished masterful masterly skillful skilful expertly adroit
        polished seamless effortless elegant graceful sumptuous luminous
        radiant resplendent dazzling vibrant vivid dynamic energetic spirited
        infectious effervescent joyous joyful exuberant buoyant playful
        refreshing invigorating audacious bold gutsy fearless ambitious
        memorable indelible iconic essential worthwhile recommend recommended
        relish relished savor savored savour savoured enjoy enjoyed enjoys
        delighted hooked hookedness hookedon hooked worthwhile
        perfection triumph success succeeds successful excel excels
        captivates charmed enthralled thrilled impressed satisfied captivated
        entranced mesmerized entertained moved enchanted enriched
        shines dazzles sparkles soars flourishes crackles sizzles
        wondrous bewitching enchanting refreshing revitalizing
        textured layered nuanced sophisticated incisive razor sharpness
        pleasant comedic hilarious affectionate rapturous
    """),
    (2.0, """
        good goodness fun funny solid fine decent nice strong stronger
        credible believable convincing persuasive authentic genuine honest
        sincere earnest natural realistic truthful truehearted grounded
        charismatic appealing appealingly magnetic handsome attractive
        effective efficient competent capable professional
        respectable substantial worthwhile salutary worthy rich rewarding
        robust hearty lively sprightly breezy brisk zippy snappy nimble
        pacy punchy taut tight economical lean crisp fluid fluidity smooth
        colorful colourful atmospheric evocative stylish stylishly
        lovely sweet sweetness agreeable affable amiable cozy cosy
        accessible inviting welcoming lovable affections affection
        likability likeability charisma wit humor humour laughs laughter
        amused amusing amusement chuckles chuckle smiles smile
        engaging engagement interest interesting intriguing intrigue
        curiosity curious absorbing absorbingness absorbing
        heart empathy humanity grace compassionate compassion
        refreshing fresh freshness inventive invention inventiveness
        audacity originality creativity novelty idiosyncratic distinctive
        unusual unexpected unpredictable surprising surprise surprises
        ambitious ambition adventurous daring welcome
        benefit beneficial worthwhile improvement improves improved
        worthwhile merit merits asset assets strength strengths redeeming
        redeemed redeem charm grace elegance craftsmanship panache verve
        depth substance intelligence insight knowledge observant
        winning winner wins hit succeeds works worked workmanlike
        entertaining entertainment excitement thrill thrills delight
        satisfaction pleasure joy gem affection impact meaningful
        important valuable necessary essential relevant timely instructive
        honest honesty honesty grounded stylish credible credible
        gripping dreamlike magical magic quietly poetic poetry lyrical
        gorgeous exquisitely absorbing playful humourous humorous
        relatable likable loveable like liked liking glad happy
        admirable admirably applaudable respecting respectful
        refreshing tenderly heartfelt earnest
        classic classics cultclassic deserved deserving recommendable
        formidable monumental groundbreaking trailblazing
        amusingly breezily commendable praiseworthy creditable
        watchable rewatchable
    """),
    (0.85, """
        competent competency competent adequately acceptable tolerable
        reasonable fair harmless amiable okay ok alright
        curious intriguing offbeat oddball eccentric quirky idiosyncrasy
        earnest sincere earnestness earnest intent intentions impassioned
        sweetly nostalgic nostalgia slick slickness
        modest slightness unassuming unpretentious unpretentiously
        unorthodox unconventional strange unusual obscure enigmatic
        risk risks experiment experimental experimentation unusual
        disturbing unsettling haunting haunted harrowing wrenching
        heartbreaking unnerving chilling scary frightening chillingly
        sad sadness bittersweet melancholy bittersweetly moody
        darkly edgy provocative challenging jarring uncompromising
        bruising joyous earnest faithful faithfulness
        credible fairness decent enough mild
        relevant timely illuminating informative educational revealing
        colorful scenic comic comical satire satirical
        watch viewing happiness courage courageous
        energy honest honesty promise promising potential ambition
        satisfying visually technically serviceable passably
    """),
    (-0.8, """
        generic standard ordinary typical familiar safe formula convention
        conventional predictable predictability familiar repetition
        uneven unevenness mixed inconsistent inconsistency patchy
        choppy busy distracting distraction overlong longish
        slight thin simple simplistic soft superficial shallower
        sentimental sentimentality schmaltzy schmaltz maudlin saccharine
        corny hokey cheesy cornier kitsch kitschy sappy treacly cloying
        goofy silly silliness childish juvenile juvenilely
        muddled messy messiness sloppy sloppiness ragged raggedly
        cheap cheaply smallish modestly dated quaint
        odd weird kooky bizarre absurd cartoonish cartoonlike outlandish
        confused confusingly dense overcomplicated offputting
        awkward awkwardness clumsy clumsiness hurried rush rushed
        derivative recycled repetitive stock cliches cliche clichéd clichè
        contrivance contrived improbable implausible unbelievable
        selfconscious showy mannered smug smugness pretension
        flashy overblown bombastic overwrought overly overstated
        manipulative manipulates manipulation melodramatic melodrama
        muted subdued flatness talky wordy verbose languid listless
        languorous slow slower slowest leisurely mechanical wooden
        divisive peculiar misjudged tepid lukewarm timid
        disposable inessential unnecessary needlessly needless
        incoherence inconsistency predictable uneven unassuming
        competent forgets forgettable mediocre mediocrity unremarkable
        secondhand derivative perfunctory passable middling average
        dated schmaltz fluff fluffy overkill excessive excess
        convoluted confusing lumpy scattered disjointed irony
        slight superficiality slack slackness strained stilted
        insipid banal pedestrian formulaic bynumbers
    """),
    (-2.35, """
        bad worse poor poorer poorest faulty weak weaker weakest
        lack lacks lacked lacking lackluster lacklustre lackadaisical
        disappoint disappointed disappointing disappointment disappointments
        underwhelm underwhelming underwhelmed anticlimactic anticlimax
        frustrating frustration frustrates frustrated unfulfilling
        unsatisfying unsatisfied unconvincing unpersuasive unappealing
        uncharismatic unattractive unfunny humorless humourless witless
        thankless colorless colourless expressionless charmless
        soulless heartless lifeless spiritless graceless toothless
        joyless pointless aimless directionless meaningless purposeless
        dull drab dreary blah meh hohum bland flavorless flavourless
        boring bored bore boredom tedious tediousness tiresome tiring
        monotonous monotony monotonously plodding lumbering dragging
        drag drags dragged slogs slog slogging torpid lethargic inert
        stagnant ponderous ponderously drearily numbing uninspired
        unoriginal unimaginative uninteresting unengaging undistinguished
        unmemorable unobtrusive unamusing unmoving unaffected
        vapid vacuous empty hollow shallow emptiness hollowness
        silly stupid dumb dopey boneheaded hammy overwrought
        overwrites overwritten underwritten sketchy unfocused
        illogical irrational incoherent incoherently nonsensical
        incomprehensible indecipherable disjointed convoluted jumbled
        muddle muddles muddling muddled muddiness garbled garble
        confused confusing confusion disorienting disorganized
        hamfisted heavyhanded overbearing overacted overacting
        ineffectual ineffective incompetent incompetence inept
        amateurish amateurishness unprofessional misdirected
        genericness preposterous predictable predictably
        formulaic cliched clichéd cliche cliches stereotyped
        stereotypical stereotype stereotypes unimaginatively
        contrived contrivances phony fake falseness dishonest
        crass tacky trashy vulgar tasteless leering puerile sophomoric
        obnoxious annoying annoyed irritating irritated irritatingly
        exasperating exasperated grating grates annoying
        smug selfindulgent indulgent indulgence preening pretentious
        pretentiousness pretentiously ostentatious preachy preachiness
        patronizing patronising condescending sanctimonious sanctimony
        xenophobic racist racism sexist sexism misogynistic misogyny
        offensive offended upsetting exploitative exploitation
        unwatchably painful painfully pain agonizing agonising
        unpleasant disagreeable unsavory repellent repellant repulsive
        distasteful unlikable unlikeable hateful nasty mean spirited
        insufferable unbearable intolerable insupportable
        depressing dreariness morose morbid glum sullen sour dour
        obnoxiously aggravating aggravation unsympathetic abrasive
        sloppy careless haphazard illconsidered misguided misfire
        misfires misfired misstep missteps botched mishandled
        cutrate shoddy threadbare ragged uninvolving undemanding
        secondrate substandard subpar inferior deficient deficiently
        inadequate inadequacy deficient crippled miscast
        squanders squander squandered wasting wasted wastes waste
        squanderer flounders flounder falters falter stumbles stumbles
        collapse collapses flops flop flopped fails fail failed failing
        failure failures unsuccessful lose loses lost losing
        ruined ruins ruin ruined spoil spoils spoiled detracts
        distract detract disastrous forgettable eminentlyforgettable
        sluggish slowness stink stinks stank spoiled labored laboured
        stale staleness shopworn tired tiredness weary wearisome
        exhausting exhausted exhausting tedious uninspired tedious
        tiresome excruciatingly cringey cringy cringe cringeworthy
        flat unexciting regrettable regret regretted regretting
        redundant redundancy repetitious maundering rambling
        irritating underdeveloped overstretched overstuffed
        pedestrian anemic anaemic tepid insipid banal banalities
        disappointing miss misshapen muddled strained unevennness
    """),
    (-4.45, """
        atrocious abominable appalling abhorrent dreadful dreck dross dirge
        awful awfulness horrible horrid horrendous hideous horridly
        terrible terribly wretched wretchedness execrable deplorable
        lousy miserable pathetic pitiful laughable risible ridiculous
        idiotic asinine moronic asinine imbecilic idiocy stupidity
        shameful embarrassing embarrass embarrassment humiliating
        cringeworthy cringeworthy despicable contemptible contempt
        rotten rottenly putrid garbage junk trash rubbish crap crappy
        steaming turd shambles debacle fiasco catastrophe catastrophic
        disaster disastrous abysmal abyss embarrassing trainwreck
        unwatchable unsalvageable unendurable insufferable nauseating
        vomit repugnant odious detestable detested detest
        loathsome loathe loathed loathing hate hated hates
        intolerable tediousness excruciating soulless unbearable
        ineptitude incompetently ineptly atrociously abhorrently
        woeful woe egregious infuriating insult insulting insults
        painful pointless worthless useless wretchedly pitifully
        travesty mockery stinker stinking godawful sewage drivel
        tripe schlock swill dreck claptrap nonsense hogwash bollocks
        insulting unmitigated unredeemable irredeemable horrifically
        pitiless sickening disgust disgusting disgusted unforgivable
        worst poorest bottomfeeder monstrosity trainwreck walkout
    """),
)

_WORDS = {}
for _weight, _items in _WORD_GROUPS:
    for _item in _items.split():
        _WORDS.setdefault(_item, _weight)

# Some words are appreciably stronger or weaker than their nearest group.
_WORDS.update({
    "best": 4.4, "worst": -4.8, "better": 2.45, "worse": -3.35,
    "well": 0.0, "like": 1.75, "liked": 3.25, "okay": 0.45, "ok": 0.45,
    "alright": 0.45, "fine": 1.3, "decent": 1.5, "solid": 2.15, "nice": 1.45,
    "fair": 0.45, "decently": 1.35, "adequate": -0.65, "adequately": 0.35,
    "competent": 0.9, "acceptable": 0.25, "tolerable": -0.5, "serviceable": -0.35,
    "mediocre": -2.9, "forgettable": -2.55, "predictable": -1.65,
    "flat": -2.45, "confusing": -2.45, "generic": -1.5, "conventional": -0.35,
    "corny": -0.85, "slow": -0.85, "long": 0.0, "dated": -1.2, "ordinary": -0.7,
    "superficial": -1.95, "repetitive": -2.15, "melodrama": -0.35,
    "melodramatic": -1.35, "overlong": -2.2, "mixed": -0.4,
    "passable": -0.6, "passably": 0.1, "middling": -1.75, "average": -0.75,
    "unremarkable": -1.9, "bland": -2.85, "wooden": -2.5, "awkward": -1.55,
    "muddled": -2.15, "absurd": -0.75, "disjointed": -2.25,
    "unnecessary": -1.9, "unassuming": 0.65, "ambitious": 1.35, "ambition": 0.7,
    "astonishing": 3.15, "incredible": 3.75, "unbelievable": 0.15,
    "inadequate": -2.25, "wrong": -0.9, "right": 0.45, "problem": -1.6,
    "problems": -1.6, "flaw": -1.65, "flaws": -1.65, "flawed": -1.7,
    "flawlessly": 4.3, "perfectly": 1.2, "pleasant": 2.15, "pretty": 0.95,
    "inspiring": 3.1, "inspirational": 2.6, "inspiration": 1.45, "inspired": 2.7,
    "satisfying": 3.4, "interesting": 2.1, "pleasantly": 1.35,
    "tension": 0.45, "suspense": 1.15, "suspenseful": 2.9, "tensely": 0.65,
    "addictive": 2.8, "gripping": 3.7, "nostalgic": 0.7, "escape": 0.0,
    "relaxing": 2.0, "comforting": 2.0, "soothing": 1.6, "stirring": 2.9,
    "gutwrenching": 1.6, "horrifying": 0.15, "horrific": -0.3, "terrifying": 1.25,
    "bleak": 0.1, "brutal": 0.0, "raw": 0.35, "sad": 0.0, "tragic": 0.1,
    "surreal": 0.5, "silly": -0.6, "dumb": -1.95, "mean": 0.0,
    "powerful": 3.6, "potent": 2.6, "flimsy": -2.65, "toxic": -1.35,
    "safe": -0.35, "standard": -0.45, "derivative": -2.35, "stale": -2.55,
    "original": 1.65, "fearless": 2.0, "energetic": 1.95, "clinical": -0.7,
    "soulless": -3.4, "uninspired": -2.85, "contrived": -2.05, "uninvolving": -2.6,
    "extraneous": -1.6, "hackneyed": -2.7, "trite": -2.6, "overrated": -3.2,
    "underrated": 3.65, "overhyped": -2.8, "underappreciated": 3.1,
    "irritant": -1.7, "letdown": -3.6, "dislike": -2.9, "bother": -0.7,
    "miss": 0.0, "lost": 0.0, "lose": 0.0, "loses": 0.0, "losing": 0.0,
    "watch": 0.0, "viewing": 0.0, "instructive": 1.2, "unobtrusive": 0.35,
    "necessarily": 0.0, "irony": 0.0, "true": 0.0, "truly": 0.0,
    "steaming": 0.0, "pain": -0.25, "loving": 1.65, "lovingly": 2.1,
    "needlessly": -1.65, "smile": 1.55, "laughter": 1.8, "laugh": 0.85,
    "earnest": 0.75, "polished": 2.1, "minor": -0.15, "sick": -0.2,
    "hype": 0.0, "spark": 1.5, "involving": 2.15, "listless": -2.55,
    "woodenness": -2.4, "amateur": -0.85, "subtle": 1.85, "subtlety": 1.75,
    "narrative": 0.0, "documentary": 0.0, "neat": 1.55, "cool": 1.1,
    "funnier": 2.2, "funniest": 3.7, "unfunniest": -3.7, "droll": 1.65,
    "snarky": -0.15, "satire": 0.15, "satirical": 0.3, "comic": 0.15,
    "celebrates": 1.15, "celebration": 1.2, "priceless": 3.15,
    "delivers": 2.5, "deliver": 1.4, "delivered": 1.65,
    "fails": -2.8, "failsafe": 0.0, "score": 0.0, "loveable": 2.8,
    "acted": 0.0, "unintentionally": -1.05, "unfortunately": -1.4,
    "sadly": -1.05, "thankfully": 1.15, "fortunately": 1.15, "mercifully": -0.55,
    "regrettably": -1.5, "disastrously": -2.9, "terribly": -0.5, "horribly": -0.95,
    "painfully": -0.9, "laughably": -1.8, "admittedly": 0.0,
})


_PHRASE_GROUPS = (
    (0.0, """
        love story | love stories | in love | falls in love | fell in love | fall in love |
        falling in love | love interest | young love | love triangle | love affair |
        making love | make love | true love | puppy love | unrequited love |
        love letter | good guy | good guys | bad guy | bad guys | bad boy | bad boys |
        good girl | bad girl | bad girls | good and evil | right and wrong |
        feel like | feels like | felt like | look like | looks like | looked like |
        sounds like | sound like | seems like | seem like | seemed like |
        something like | anything like | nothing like | just like | just as |
        unlike any other | a great deal | a good deal | a good number | a good many |
        a great many | a great amount | pretty much | pretty well | for good |
        fine line | fine lines | good looks | good looking | play it safe |
        fine arts | good fortune | for better or worse | better or worse |
        lost his | lost her | first love | miss the | miss a | without a doubt |
        no doubt | without doubt | no question that | no denying | there is no denying |
        no wonder | no matter | whether or not | if not | no less than |
        not only | not just | not merely | not simply | not to mention |
        not unlike | not to be confused with | not sure | do not know why |
        as well as | as well | might as well | good intentions |
        special effects | visual effects | best friend | best friends |
        make fun of | makes fun of | making fun of | made fun of | poke fun at |
        pokes fun at | crush on | mixed with | dark comedy | black comedy |
        horror comedy | action comedy | romantic comedy | screwball comedy |
        of interest to | person of interest | based on a true story |
        dry humor | dry humour | sense of humor | sense of humour |
        a series of | in the dark | to be sure | for the most part |
        how well | how good | on the right | pretty soon | when it comes to |
        not necessarily | like a film | felt a need | feel good about himself |
        the original | the original film | the original movie | from the original |
        despite himself | despite herself | despite itself | better known |
        a waste product | no thanks to | but for | and yet to |
        i wish to | best known | is fine with | fine with me |
        bad dreams | good times and bad | good and bad | dark and stormy |
        sensitive subject | bad news bears | star wars | fine print | good will hunting
    """),
    (5.2, """
        a must see | must see | must watch | must watch movie | an absolute must |
        a must for | see this movie | see this film | do not miss | do not miss it |
        not to be missed | can not be missed | can not miss | should not miss |
        can not recommend it enough | can not recommend this enough |
        can not recommend enough | could not recommend it enough |
        can not recommend it highly enough | highly recommend | wholeheartedly recommend |
        strongly recommend | recommend to anyone | recommend it to anyone |
        worth seeing | worth watching | worth a watch | worth the watch |
        worth another look | worth a look | worth a second look | well worth |
        worth your time | worth my time | worth the time | worth every minute |
        worth the price of admission | worth the ticket price |
        worth the wait | worth seeking out | worth checking out |
        worth checking | worth catching | worth renting | worth revisiting |
        worth sitting through | deserves to be seen | deserves a wider audience |
        run to see | go see it | go see this | go watch it | check it out |
        deserves every | two thumbs up | thumbs up | blew me away | blows you away |
        blown away | knocked my socks off | knocked it out of the park |
        knocks it out of the park | hits it out of the park | hit it out of the park |
        on the edge of my seat | at the edge of my seat | on the edge of your seat |
        edge of your seat | edge of my seat | could not take my eyes off |
        can not take your eyes off | glued to the screen | glued to my seat |
        can not stop watching | could not stop watching | could not look away |
        can not look away | never a dull moment | not a dull moment |
        can not stop laughing | could not stop laughing | never laughed so hard |
        did not want it to end | did not want the movie to end |
        never wanted it to end | could watch it again | will watch it again |
        would watch it again | would see it again | watch this again |
        want to watch it again | seen it more than once | watch over and over |
        love every minute | loved every minute | loved every second |
        enjoyed every minute | enjoyed every bit | loved it | love it |
        loved this movie | love this movie | loved this film | love this film |
        so bad it is good | so bad it is actually good | so bad it is kind of good |
        so bad it was good | so bad it becomes good | so bad it is fun |
        could not be better | does not get any better | does not get much better |
        it does not get better than this | could not ask for more |
        can not ask for more | can not fault | hard to fault | hard to resist |
        impossible to resist | hard not to love | impossible not to love |
        can not help but love | impossible not to enjoy | hard not to like |
        what is not to like | what is not to love | nothing not to like |
        nothing to dislike | no complaints | no complaints here |
        will not be disappointed | would not be disappointed | was not disappointed |
        did not disappoint | does not disappoint | never disappoints |
        nothing short of a masterpiece | tour de force | tour de forces |
        stands the test of time | stand the test of time | has aged well |
        one of a kind | had a blast | have a blast | had a great time |
        a great time at the movies | the time of my life | a ton of fun |
        a lot of fun | lots of fun | bucketloads of fun | more fun than |
        in a good way | in the best way | in the best sense | in the best possible way |
        for all the right reasons | hit all the right notes | hits all the right notes |
        all the right ingredients | exceeded my expectations | surpassed my expectations |
        surpasses expectations | exceeded expectations | exceeds expectations |
        lives up to the hype | lived up to the hype | lives up to its promise |
        better than i expected | better than expected | better than it has any right to be |
        much better than expected | goes above and beyond | an instant classic |
        a modern classic | a hidden gem | an underrated gem | chef is kiss |
        a work of art | a thing of beauty | restored my faith | takes your breath away |
        took my breath away | stole the show | steals the show | has it all
    """),
    (2.85, """
        well acted | very well acted | well cast | well made | well done |
        well crafted | well written | well directed | well shot | well paced |
        well staged | well mounted | well realized | well realised | well executed |
        well told | well developed | well constructed | well handled | well observed |
        well produced | well designed | well deserved | well worth watching |
        made me laugh | makes me laugh | make you laugh | makes you laugh |
        made us laugh | made me smile | makes you smile | put a smile on my face |
        brings a smile | left me smiling | laughing out loud | laughed out loud |
        laugh out loud | laugh a minute | laughed all the way through |
        made me cry | makes you cry | brought tears to my eyes | moved me to tears |
        pulled at my heartstrings | tugs at the heartstrings | warmed my heart |
        stole my heart | found myself caring | cares about its characters |
        root for | rooting for | draws you in | drew me in | sucked me in |
        held my attention | holds your attention | keeps you interested |
        kept me guessing | keeps you guessing | keeps the audience guessing |
        kept me engaged | had me hooked | gets under your skin |
        sticks with you | stays with you | stays with me | linger in the mind |
        lingered in my mind | left me thinking | made me think | makes you think |
        got me thinking | food for thought | provokes thought | thought provoking |
        mind blowing | eye opening | jaw dropping | jaw droppingly | breath of fresh air |
        put together well | crafted with care | an act of love | a labor of love |
        a labour of love | holds up | held up | still holds up | stand out |
        standout performance | stand out performance | a standout |
        takes chances | takes risks | takes real chances | breaks new ground |
        dares to be different | defies expectations | subverts expectations |
        a cut above | heads and shoulders above | head and shoulders above |
        punches above its weight | rises above | defies convention | makes it work |
        it works | actually works | just works | works on every level |
        it all works | does the trick | gets the job done | does its job |
        delivers the goods | delivered the goods | gets it right | gets a lot right |
        gets everything right | got it right | hits the mark | hits home |
        finds its footing | comes together | came together | comes to life |
        springs to life | breathes life into | comes alive | leaps off the screen |
        pulls it off | pulled it off | manages to pull off | does what it sets out to do |
        has something to say | much to say | injects new life |
        has a heart | has heart | wears its heart on its sleeve |
        heart in the right place | full of heart | full of life | bursting with life |
        larger than life | full of surprises | full of charm | oozes charm |
        plenty to like | a lot to like | much to like | much to recommend |
        something for everyone | has its moments | had its moments |
        hit the spot | hits the spot | time flew | flew by | goes by quickly |
        moves along nicely | moves at a brisk pace | moves at a good clip |
        does not outstay its welcome | does not overstay its welcome |
        never takes itself too seriously | does not take itself too seriously |
        knew what it was | knows what it is | knows exactly what it is |
        grows on you | grew on me | won me over | wins you over |
        better than most | better than average | a pleasant surprise |
        pleasantly surprised | proved me wrong | not half bad | not bad at all |
        not bad | not too bad | not all bad | far from bad | anything but boring |
        not without charm | not without its charms | not without merit |
        not without merits | not without its merits | not without laughs |
        no shortage of | no lack of | more than enough |
        not lacking in | no small feat | not too shabby | beats the odds |
        nothing wrong with | no reason not to | credit where credit is due |
        on repeat | on point | top notch | first rate | top drawer |
        high quality | worth it | worth a damn | worth a second watch |
        worth the trouble | give it a chance | give it a shot | a fun ride |
        roller coaster ride | popcorn fun | edge of the seat | crowd pleaser |
        crowd pleasing | crowd pleasingly | a feel good | feel good movie |
        feel good film | feel good | good clean fun | dumb fun | mindless fun |
        guilty pleasure | part of the charm | all in good fun |
        good for what it is | great for what it is | fun for what it is |
        fun to watch | a joy to watch | a pleasure to watch | easy to watch |
        easy on the eyes | easy to like | easy to recommend | easy to love |
        nice to see | nice touch | nice touches | honest to goodness |
        not a dry eye | does not put a foot wrong | comes highly recommended |
        in fine form | a step up | better and better | from strength to strength |
        good enough | perfectly fine | pretty darn good | rather good |
        nothing to complain about | exactly what i wanted | just what i needed |
        take the kids | a treat | a real treat | cinematic treat |
        smartly written | beautifully shot | beautifully made | visually striking |
        sheer delight | sheer pleasure | pure joy | pure delight | pure magic |
        goes down easy | crazy in a good way | deliciously absurd |
        highly effective | serves its purpose | positively surprised |
        better late than never | better than the original | a worthy sequel
    """),
    (-5.45, """
        waste of time | waste of my time | waste of your time | wasting your time |
        waste my time | waste your time | waste of money | waste of my money |
        waste of your money | wasted my time | wasted my money | money down the drain |
        waste of talent | waste of a good cast | wasted opportunity |
        squanders its potential | squandered potential | squandered opportunity |
        should have stayed home | save your money | save your time |
        save your patience | do not waste your money | do not waste your time |
        i want my money back | want my money back | want my time back |
        want my two hours back | want those two hours back | give me my money back |
        wish i had not watched | regret watching | regretted watching |
        wish i had walked out | walked out | walk out | walkout worthy |
        left the theater early | left the theatre early | turned it off |
        switched it off | turned this off | could not finish | could not get through |
        can not finish | can not sit through | could not sit through |
        hard to sit through | difficult to sit through | painful to watch |
        painful to sit through | a chore to watch | a chore to sit through |
        i fell asleep | fell asleep | puts you to sleep | put me to sleep |
        sent me to sleep | cure for insomnia | watching paint dry |
        watch paint dry | paint drying | grass grow | like pulling teeth |
        like nails on a chalkboard | nails on a chalkboard | look at my watch |
        kept checking my watch | kept looking at my watch |
        could not wait for it to end | could not wait for the credits |
        thank god it is over | could not end soon enough | feels like forever |
        thought it would never end | it never ends | long two hours |
        runs out of steam | runs out of ideas | wears out its welcome |
        overstays its welcome | outstays its welcome | feels twice as long |
        goes on forever | feels endless | stop watching |
        do not bother | do not bother with | do not bother watching |
        do not watch | do not watch this | do not see this |
        can not recommend | could not recommend | would not recommend |
        would never recommend | hard to recommend | difficult to recommend |
        impossible to recommend | hesitate to recommend | zero stars |
        thumbs down | two thumbs down | avoid at all costs | avoid this movie |
        avoid this film | skip it | skip this | skip this one | give it a miss |
        give this a miss | stay away | steer clear | not worth seeing |
        not worth watching | not worth a watch | not worth the watch |
        not worth your time | not worth my time | not worth the time |
        not worth the effort | not worth the trouble | not worth it |
        hardly worth | barely worth | not worth | not even worth |
        not worth a dime | not worth a second | not worth the price of admission |
        not worth the paper | nothing of value | nothing worth seeing |
        nothing worth watching | nothing to recommend | nothing to like |
        nothing to see here | no redeeming qualities | no redeeming features |
        no redeeming value | without a single redeeming | quality control |
        nothing redeeming | no saving grace | no saving graces |
        utter garbage | hot garbage | complete garbage | a complete disaster |
        total disaster | a complete mess | a total mess | a hot mess |
        total train wreck | train wreck | train wreck of a movie |
        pile of garbage | pile of trash | steaming pile | pile of junk |
        piece of crap | piece of garbage | piece of junk | piece of trash |
        bottom of the barrel | scraping the bottom | scrape the bottom |
        a new low | not even a movie | not even so bad it is good |
        not so bad it is good | so bad it is not even funny |
        in a bad way | in the worst way | in the worst possible way |
        for all the wrong reasons | for the wrong reasons | all the wrong notes |
        full of holes | plot full of holes | riddled with holes | riddled with cliches |
        plot holes | gaping plot holes | paper thin plot | wafer thin plot |
        joke is on the audience | insults the intelligence | insults your intelligence |
        an insult to | insult to the audience | insult to intelligence |
        a sad excuse | a poor excuse | a sorry excuse | a lame excuse |
        i hated it | hated every minute | hated it | hate it | hate this movie |
        hated this movie | this is not funny | it is not funny |
        it is not even funny | not a single laugh | not one laugh |
        did not laugh once | never laughed once | did not even crack a smile |
        not scary at all | not the least bit scary | no suspense whatsoever
    """),
    (-2.95, """
        tries too hard | try too hard | trying too hard | too hard to watch |
        tries and fails | tried and failed | falls short | fell short |
        falls far short | fell far short | come up short | comes up short |
        came up short | falls flat | fell flat | fall flat | landed with a thud |
        does not work | did not work | never works | nothing works | it does not work |
        never quite works | does not quite work | does not hold up | did not hold up |
        has not aged well | is not holding up | fails to deliver | failed to deliver |
        does not deliver | did not deliver | cannot deliver | does not pay off |
        failed to impress | fails to impress | left me cold | leaves you cold |
        leaves me cold | leaves the viewer cold | left me indifferent |
        leaves you indifferent | left me bored | leaves a bad taste |
        left a bad taste | had high hopes | had such high hopes | expected more |
        expected better | i was expecting more | i was hoping for more |
        had hoped for more | i wanted to like | wanted to like it | wanted to love it |
        there was potential | had potential | had some potential |
        all potential | so much potential | missed opportunity | missed the mark |
        misses the mark | misses the point | missed the point | lose the plot |
        loses the plot | lost the plot | loses its way | lost its way |
        lost interest | lose interest | lost my interest | loses momentum |
        loses steam | out of steam | goes nowhere | go nowhere | went nowhere |
        never goes anywhere | going nowhere | leads nowhere | adds up to nothing |
        does not add up | never adds up | did not add up | makes no sense |
        make no sense | made no sense | did not make sense | does not make sense |
        never makes sense | what was the point | what is the point |
        what is the point of | so what | nothing happens | virtually nothing happens |
        barely anything happens | nothing much happens | never gets going |
        never takes off | never gets off the ground | does not go anywhere |
        never comes alive | never comes to life | never finds its footing |
        gets off to a promising start | starts out promising | looks promising at first |
        lacking in | low on | short on | short of ideas | no originality |
        no ideas | no substance | no character development | no real character development |
        no personality | no soul | no charm | no depth | no energy | no imagination |
        no fun | no effort | not enough | without much | has very little to offer |
        little to offer | little to recommend | little to like |
        not much to like | not much to recommend | leaves much to be desired |
        leaves a lot to be desired | left a lot to be desired | wanting more |
        left wanting | comes up wanting | found it wanting |
        only redeeming | only saving grace | sole redeeming | sole saving grace |
        the one good thing | the only good thing | the only thing i liked |
        the best thing about this movie is the end | best part was the credits |
        best thing about it is the credits | the best part is the credits |
        starts strong and ends | ends with a whimper | ends in a whimper |
        unable to care | did not care about | do not care about its characters |
        could not care less | could care less | not care less |
        i could not connect | never care | never made me care |
        left me unmoved | leaves me unmoved | laugh at it | laugh at the movie |
        laughing at it | unintentionally funny | laughably bad | a bad joke |
        bad acting | poor acting | wooden acting | badly acted | badly cast |
        poorly acted | poorly cast | poorly made | poorly written | badly written |
        badly made | poorly paced | unevenly paced | poorly directed |
        badly directed | poorly executed | badly executed | poorly handled |
        badly edited | low effort | low grade | low quality | a bad script |
        weak script | paper thin | wafer thin | razor thin | one dimensional |
        two dimensional | cardboard cutouts | cardboard characters |
        paint by numbers | by the numbers | seen it all before | seen this all before |
        nothing new | nothing fresh | nothing original | nothing special |
        just another | yet another | same old | been done before | been there done that |
        more of the same | done to death | beaten to death | old hat |
        all style and no substance | no style | style over substance |
        all surface | an empty shell | a hollow shell | shallow imitation |
        a pale imitation | pale imitation | pales in comparison |
        does not compare | does not live up | does not live up to the hype |
        did not live up to | falls short of expectations | no match for |
        rip off | ripoff | cheap knockoff | cash grab | a quick cash grab |
        goes through the motions | go through the motions | going through the motions |
        phones it in | phoned it in | half baked | half hearted | cookie cutter |
        ham fisted | heavy handed | over the top in a bad way | self indulgent |
        self important | self congratulatory | too full of itself |
        too clever for its own good | too smart for its own good |
        takes itself too seriously | take itself too seriously |
        takes itself way too seriously | too serious for its own good |
        forced humor | forced humour | forced comedy | forced jokes | forced laughs |
        strained humor | labored humor | obvious jokes | predictably so |
        painfully slow | terribly slow | painfully obvious | deadly dull |
        dead on arrival | sucked the life out | sucks the life out |
        sucking the life out | sucked all the life out | flat as a pancake |
        a slog | a tough sit | feels like a chore | feels like homework |
        non event | a non starter | grinding halt | grinds to a halt |
        stuck in neutral | stuck in first gear | goes off the rails |
        went off the rails | falls apart | fell apart | falling apart |
        does not come together | all over the place | at war with itself |
        tonally inconsistent | tonal whiplash | uneven tone | a jumbled mess |
        it wants to be | not sure what it wants | does not know what it wants |
        can not decide what it wants | does not know what to do |
        do not know what to make of | not quite there | not quite right |
        not nearly enough | never quite hits | never really gets |
        fails on every level | fails at every level | no such luck |
        should be better | should have known better | could have done better |
        better than nothing | could not be worse | was expecting better |
        only marginally better | only slightly better than |
        less than mediocre | less than stellar | less than impressive |
        less than enjoyable | less than satisfying | less than compelling |
        less than meets the eye | leaves little impression | not very good |
        not that good | not particularly good | not so good | not terribly good |
        not great | not so great | not all that great | not all that good |
        just okay | just ok | merely okay | just average | just barely |
        not much fun | not a lot of fun | far from perfect | far from great |
        far from good | a far cry from | in need of a rewrite |
        tossed together | thrown together | slapped together | cut and paste |
        straight to video | straight to dvd | made for tv | insultingly bad |
        worse and worse | the original was better | the book was better |
        the first was better | a step down | have seen better | seen better |
        the actors deserve better | the cast deserves better | the cast deserved better |
        deserves better material | let me down | lets me down |
        let the audience down | lets the audience down | to no avail |
        cheap thrills | cheap laughs | cheap sentiment | cheap shots | no payoff |
        never pays off | never went anywhere | thinner than |
        all talk and no | under its own weight | a missed chance |
        long winded | long winding | airless | hard to enjoy | hard to like |
        hard to love | hard to care | hard to follow | impossible to follow |
        hard to understand | had me rolling my eyes | rolling my eyes | eye rolling |
        rolls its eyes | try again | a bad time at the movies |
        badly in need | as subtle as a sledgehammer | not in a good way |
        looks good on paper | better on paper | more interesting on paper |
        little more than | nothing more than | less a film than |
        no better than a | an exercise in futility | an exercise in boredom
    """),
    (0.95, """
        not terrible | nothing terrible | not dreadful | not awful | not horrible |
        could be worse | could have been worse | it could have been worse |
        not the worst | not the worst thing | not the worst movie |
        does the job | did the job | passes the time | pass the time |
        it is fine | it was fine | was fine | it is okay | it was okay |
        has its charms | has some charm | moment or two | a few good moments |
        looks good | looked good | something to like | one nice thing |
        more or less works | more than a little | goes for broke |
        has a point | familiar but fun | good enough for |
        give it credit | a few laughs | some laughs | good company |
        a little gem | low key | stripped down | slow burn | slow burner |
        coming to life | down to earth | a lively cast | a gentle comedy
    """),
    (-1.3, """
        at least it is short | at least the credits | at least it ends |
        best forgotten | shrug it off | mild diversion | faint praise |
        uneven at best | at best passable | at best forgettable |
        barely passable | marginally entertaining | occasionally amusing |
        somewhat amusing | mildly amusing | somewhat entertaining |
        almost works | almost worked | could almost work |
        so so | all right i guess | okay i guess | just fine |
        only okay | only decent | only passable | not enough to save |
        no great shakes | a bit much | over the top | over the top acting |
        not a patch on | overstay its welcome | no one to root for |
        as an afterthought | mostly forgettable | a mixed bag |
        mixed bag | could use some | needs work | needed more | needed a lot more |
        self conscious | emotional manipulation | cheap looking | slow paced |
        down to a crawl | more of an endurance test | a lot of nothing |
        bad enough | nothing spectacular | nothing amazing | nothing extraordinary |
        nothing groundbreaking | nothing to write home about | far from flawless |
        computer generated mess | weight of its own | by committee | test screening
    """),
)

_PHRASES = {}
for _weight, _group in _PHRASE_GROUPS:
    for _phrase in _group.split("|"):
        _phrase_words = tuple(_TOKEN_RE.findall(_phrase))
        if _phrase_words:
            _PHRASES[_phrase_words] = _weight

# Exact expressions that may be split by punctuation in review transcripts.
_PHRASES.update({
    ("so", "bad", ",", "it", "is", "good"): 4.4,
    ("so", "bad", ",", "it", "was", "good"): 4.4,
    ("funny", ",", "in", "a", "bad", "way"): -3.1,
    ("been", "there", ",", "done", "that"): -2.4,
    ("please", ",", "do", "not", "bother"): -4.4,
    ("no", ",", "thank", "you"): -2.8,
    ("no", "thank", "you"): -2.65,
})
_PHRASE_STARTS = {}
for _key, _weight in _PHRASES.items():
    _PHRASE_STARTS.setdefault(_key[0], []).append((_key, _weight))
for _entries in _PHRASE_STARTS.values():
    _entries.sort(key=lambda entry: -len(entry[0]))


def _phrase_at(tokens, index):
    for words, score in _PHRASE_STARTS.get(tokens[index], ()):
        end = index + len(words)
        if tokens[index:end] == words:
            return end, score
    return None


_STEM_BLOCK = {
    "thing", "things", "anything", "everything", "something", "nothing",
    "here", "there", "once", "ones", "using", "doing", "going", "having",
    "hollywood", "director", "directors", "actor", "actors", "writer", "writers",
    "story", "stories", "underlying", "ears", "eyes", "shows", "showing",
    "starring", "takes", "stakes", "interestingly", "really", "generally",
    "even", "ever", "every", "somewhat", "dead", "death", "violence", "harmlessly",
    "utter", "utterly", "totally", "completely", "simply", "extremely", "quite",
    "very", "rather", "mostly", "film", "movie", "plot", "performances",
    "viewer", "moviegoers", "record", "adults", "characters", "person",
}
_STEM_RULES = (
    ("ability", ("able",)), ("ibility", ("ible",)),
    ("iness", ("y",)), ("ness", ("",)), ("fulness", ("ful",)),
    ("lessly", ("less",)), ("ically", ("ic", "ical")), ("ily", ("y",)),
    ("edly", ("ed", "")), ("ingly", ("ing", "")), ("ally", ("al", "")),
    ("ly", ("", "le")), ("ies", ("y",)), ("ves", ("ve", "f")),
    ("es", ("", "e")), ("s", ("",)), ("ied", ("y",)), ("ed", ("", "e")),
    ("ing", ("", "e", "y")), ("iest", ("y",)), ("ier", ("y",)),
    ("est", ("", "e")), ("er", ("", "e")), ("ation", ("ate",)),
    ("ments", ("ment", "")), ("ment", ("",)), ("ity", ("", "e")),
)


@lru_cache(maxsize=8192)
def _word_score(word):
    if word in _WORDS:
        return _WORDS[word]
    if word in _STEM_BLOCK or len(word) < 4 or not word.isalpha():
        return 0.0
    for old, endings in _STEM_RULES:
        if not word.endswith(old) or len(word) - len(old) < 3:
            continue
        stem = word[:-len(old)]
        for ending in endings:
            formed = stem + ending
            if formed in _WORDS:
                return _WORDS[formed] * (0.87 if old.endswith("ly") else 0.93)
        if old in {"ed", "ing", "er", "est"} and stem[-1] == stem[-2]:
            if stem[:-1] in _WORDS:
                return _WORDS[stem[:-1]] * 0.92
    for prefix in ("un", "non"):
        if word.startswith(prefix) and len(word) >= len(prefix) + 5:
            base = _WORDS.get(word[len(prefix):], 0.0)
            if base > 1.25:
                return -min(3.0, base * 0.85)
    return 0.0


_TERMINALS = {".", "!", "?"}
_PUNCT = _TERMINALS | {",", ";", ":"}
_CONTRAST = {"but", "however", "nevertheless", "nonetheless", "except", "yet", "whereas"}
_CONCESSION = {"although", "though", "despite", "while", "albeit"}
_CONCLUSION = (
    ("ultimately",), ("overall",), ("in", "the", "end"), ("on", "the", "whole"),
    ("all", "in", "all"), ("at", "the", "end", "of", "the", "day"),
    ("on", "balance"), ("in", "the", "final", "analysis"),
    ("bottom", "line"), ("taken", "as", "a", "whole"),
)
_NEGATORS = {
    "not", "no", "never", "neither", "nor", "without", "hardly", "barely",
    "scarcely", "cannot", "lacks", "lacked", "lacking", "insufficiently", "nowhere",
}
_SCOPE_BREAK = {
    "but", "yet", "however", "although", "though", "and", "because", "since",
    "whereas", "instead", "therefore", "except", "then", "than", "rather",
}
_NEG_SKIP = {
    ("not", "only"), ("not", "just"), ("not", "simply"), ("not", "merely"),
    ("not", "unlike"), ("not", "to", "mention"), ("not", "sure"),
    ("not", "to", "be", "confused", "with"), ("not", "only", "that"),
    ("not", "know", "why"), ("not", "know", "how"), ("not", "expect", "to", "be"),
    ("no", "doubt"), ("no", "matter"), ("no", "wonder"), ("no", "less", "than"),
    ("no", "shortage", "of"), ("no", "lack", "of"), ("no", "question"),
    ("no", "denying"), ("no", "reason", "not", "to"), ("not", "without"),
    ("without", "a", "doubt"), ("without", "doubt"), ("not", "believe", "how"),
    ("not", "realize", "how"), ("not", "believe", "it", "was", "so"),
    ("not", "necessarily"), ("without", "question"),
}
_NEG_SKIP_BY_WORD = {}
for _seq in _NEG_SKIP:
    _NEG_SKIP_BY_WORD.setdefault(_seq[0], []).append(_seq)

_COMPARATIVES = {
    "better", "worse", "funnier", "duller", "greater", "weaker", "stronger",
    "smarter", "deeper", "quicker", "slower", "scarier", "tighter", "shorter",
    "longer", "richer", "brighter", "more", "less", "nicer", "faster",
    "cheaper", "sharper", "sweeter", "easier", "harder",
}
_PRONOUNS = {"i", "me", "you", "we", "he", "she", "it", "they", "this", "that"}
_ARTICLES = {"a", "an", "the", "this", "these", "those", "its", "their", "some"}
_BE = {"is", "are", "was", "were", "be", "been", "being", "am"}


def _has_sequence(tokens, phrases):
    return any(
        tokens[index:index + len(phrase)] == phrase
        for phrase in phrases for index in range(len(tokens) - len(phrase) + 1)
    )


def _clauses(tokens):
    out = []
    current = []
    scale = 1.0
    after_comma = None
    sentence_start = 0
    sentence_begun = False
    last_punct = ""

    def flush(punct=""):
        if current:
            out.append((tuple(current), scale, punct))
            current.clear()

    i = 0
    while i < len(tokens):
        word = tokens[i]
        prev = tokens[i - 1] if i else ""
        nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
        phr = _phrase_at(tokens, i)
        if phr is not None and phr[0] > i + 1:
            end = phr[0]
            current.extend(tokens[i:end])
            last_punct = ""
            sentence_begun = True
            i = end
            continue
        i += 1
        if word in _PUNCT:
            if word == "," and current and nxt in {"or", "and", "nor"}:
                if any(w in _NEGATORS for w in current[-7:]):
                    if nxt in {"or", "nor"}:
                        continue
            flush(word)
            if word in _TERMINALS:
                scale = 1.0
                after_comma = None
                sentence_start = len(out)
                sentence_begun = False
            elif after_comma is not None:
                scale = after_comma
                after_comma = None
            last_punct = word
            continue

        if word == "even" and nxt == "though":
            continue
        if word == "in" and tokens[i:i + 2] == ("spite", "of"):
            word = "despite"
            i += 2

        if word == "but" and (
            prev in {"anything", "nothing", "everything", "all", "none", "help", "cannot"}
            or nxt == "also"
            or _has_sequence(tuple(current[-24:]), (("not", "only"), ("not", "just")))
        ):
            current.append(word)
            sentence_begun = True
            last_punct = ""
            continue
        if word == "yet" and (prev in {"not", "as", "has", "have", "had", "best", "worst"} or
                              nxt in {"to", "", ".", "!", "?"}):
            current.append(word)
            sentence_begun = True
            last_punct = ""
            continue

        if word in _CONTRAST or (
            word == "still" and not current and out and last_punct in {".", ";", ","}
        ):
            flush()
            if word == "except" and nxt in {"for", "that"}:
                i += 1
                scale = 0.65 if nxt == "for" else 0.85
            elif word == "whereas":
                scale = 1.10
            else:
                # If a conclusion begins a new sentence, apply the contrast
                # to its immediately preceding clause, not the entire review.
                start = sentence_start if len(out) > sentence_start else max(0, len(out) - 1)
                for j in range(start, len(out)):
                    part, factor, punct = out[j]
                    out[j] = part, factor * (0.59 if word == "but" else 0.68), punct
                scale = 1.27 if word in {"yet", "still"} else 1.39
            after_comma = None
            sentence_begun = True
            last_punct = ""
            if i < len(tokens) and tokens[i] == ",":
                i += 1
            continue

        genuine_while = word != "while" or (
            prev not in _ARTICLES | {"little", "long", "whole", "short", "all", "for"}
            and (not sentence_begun or nxt in _ARTICLES | _PRONOUNS)
        )
        genuine_though = not (word == "though" and nxt in _PUNCT | {""})
        if word in _CONCESSION and genuine_while and genuine_though:
            flush()
            if not sentence_begun:
                scale = 0.57
                after_comma = 1.19
            else:
                scale = 0.70 if word != "while" else 0.95
                after_comma = None
            sentence_begun = True
            last_punct = ""
            continue

        if word == "if" and nxt in _PRONOUNS | {"only", "the"} and not sentence_begun:
            scale = 0.70 if nxt == "only" else 0.43
            after_comma = 1.12

        if (word == "than" and prev not in {"rather", "other", "more", "less"} and
                current and any(w in _COMPARATIVES for w in current[-8:]) and
                nxt not in {"enough", "ever"}):
            flush()
            scale *= 0.34
            last_punct = ""
            continue

        current.append(word)
        sentence_begun = True
        last_punct = ""

    flush()
    return out


_NEGATED_BY_FAILURE = {"fail", "fails", "failed", "failing", "unable", "struggle",
                       "struggles", "struggled", "refuses", "refused"}
_SOFT_NEGATION = {"hardly", "barely", "scarcely"}
_DEGREE = {
    "very": 1.28, "really": 1.20, "extremely": 1.48, "incredibly": 1.43,
    "remarkably": 1.25, "exceptionally": 1.39, "absolutely": 1.48,
    "utterly": 1.46, "totally": 1.35, "completely": 1.35, "entirely": 1.23,
    "intensely": 1.24, "genuinely": 1.31, "seriously": 1.26, "truly": 1.38,
    "deeply": 1.28, "thoroughly": 1.35, "purely": 1.05, "wildly": 1.28,
    "persistently": 1.17, "consistently": 1.23, "so": 1.14, "such": 1.14,
    "quite": 1.09, "rather": 0.92, "fairly": 0.83, "somewhat": 0.63,
    "oddly": 0.94, "slightly": 0.62, "occasionally": 0.67,
    "moderately": 0.72, "marginally": 0.55, "intermittently": 0.66,
    "little": 0.78, "kinda": 0.72, "pretty": 1.06, "particularly": 1.15,
    "decidedly": 1.16, "noticeably": 1.15, "especially": 1.20, "awfully": 1.18,
    "terribly": 1.16, "damn": 1.30, "darn": 1.21, "downright": 1.35,
    "unabashedly": 1.19, "unapologetically": 1.12, "enormously": 1.35,
    "almost": 0.63, "nearly": 0.66, "slightly": 0.63, "just": 0.87,
    "merely": 0.63, "only": 0.72, "mostly": 0.94, "sorta": 0.65,
    "excessively": 1.16, "painfully": 1.21, "creepily": 1.05,
    "ridiculously": 1.26, "amazingly": 1.21, "surprisingly": 1.13,
    "disappointingly": 1.11, "laughably": 1.18, "unexpectedly": 1.14,
}
_EXCESS = {
    "long", "slow", "short", "loud", "quiet", "dark", "light", "soft", "hard",
    "serious", "conventional", "safe", "familiar", "simple", "complicated",
    "silly", "goofy", "cute", "sweet", "precious", "quirky", "cutesy",
    "earnest", "ambitious", "clever", "smart", "slick", "polished", "stylized",
    "subtle", "heavy", "obvious", "sentimental", "violent", "intense", "repetitive",
    "much", "little", "late", "overwrought", "talky", "messy", "predictable",
    "noisy", "busy", "weird", "thin", "self", "dry", "serene", "difficult",
    "easy", "cold", "cheesy", "stupid", "gory", "far", "bland", "nasty",
}
_THINGS = {"movie", "film", "flick", "picture", "feature", "sequel", "remake",
           "comedy", "thriller", "documentary", "drama", "adaptation", "production",
           "experience", "cinema", "watch"}
_ASPECTS = {
    "cast", "casting", "actor", "actors", "actress", "acting", "performances",
    "performance", "score", "soundtrack", "music", "costumes", "costume",
    "sets", "casting", "visuals", "cinematography", "lighting", "scenery",
    "photography", "effects", "photographed", "shots", "premise", "concept",
    "opening", "dialogue", "design", "supporting", "voice", "animation",
    "ideas", "idea", "moments", "cameo",
}
_WEAK_CONTENT = {
    "terrifying", "harrowing", "poignant", "horrifying", "heartbreaking",
    "disturbing", "dark", "bleak", "scary", "tragic", "quirky", "haunting",
    "chilling", "unnerving", "painful", "nasty", "ugly", "brutal", "pathetic",
    "beautiful", "violent", "unpleasant", "mean", "horrible", "awful", "cruel",
    "creepy", "miserable", "sad", "depressing", "scary", "evil", "funny",
}
_STORY_OBJECTS = {
    "world", "death", "crime", "crimes", "war", "violence", "accident", "past",
    "incident", "relationship", "childhood", "fate", "life", "lives",
    "woman", "man", "people", "girl", "boy", "family", "marriage", "thing",
    "look", "event", "events", "person", "truth", "topic", "material", "subject",
    "secret", "story", "tale", "experience", "circumstances", "character",
    "characters", "hero", "villain", "situation", "place", "times", "journey",
    "loss", "problem", "problems", "case",
}
_REPORT = re.compile(
    r"\b(?:"
    r"(?:could|should|would|might) have (?:been|become|made|worked|had|offered|delivered)"
    r"|(?:wants?|wanted|tries|trying|tried|attempts?|attempted|pretends?|pretending|aspires?) to"
    r"|(?:was|were|is|are) supposed to"
    r"|(?:wish|wished) (?:it|this|the|there|that|they|he|she)"
    r"|if only|in order to|aims? to|aspires? to|has the potential to"
    r"|expected (?:it|this|the film|the movie) to"
    r")\b"
)
_APPARENT = re.compile(
    r"\b(?:"
    r"thought (?:the (?:film|movie)|it|this) (?:would|might|was going to) "
    r"|(?:did not|never) (?:think|expect) (?:the (?:film|movie)|it|this|i) "
    r"|(?:(?:going|went) in )?(?:expecting|prepared for|braced for) "
    r"|marketed as |advertised as |described as "
    r")"
)
_INTRO_CONTENT = re.compile(
    r"\b(?:about|depicts?|documents?|chronicles?|follows?|portrays?|portrayal of|"
    r"tells? the story of|story of|tale of|based on|deals? with|centers? on|"
    r"centres? on|account of|look at|focus(?:es)? on|explores?)\b"
)
_SUSPICION = re.compile(
    r"\b(?:what (?:were|was) (?:they|he|she|the filmmakers?) thinking|"
    r"how did (?:this|it) get made|why did (?:i|we) (?:even )?(?:watch|bother)|"
    r"is (?:this|it) supposed to be (?:funny|scary|entertaining|a comedy)|"
    r"who (?:thought|thinks) (?:this|that) was a good idea|"
    r"does anyone (?:actually )?(?:care|like this)|if you can call it a (?:movie|film))\b"
)
_SUCCESS = {"good", "great", "excellent", "amazing", "awesome", "fine", "better",
            "well", "brilliant", "terrible", "awful", "bad", "horrible", "boring",
            "funny", "interesting", "entertaining", "pretentious", "perfect",
            "ridiculous", "terrific", "wonderful", "weak", "strong", "slow",
            "painful", "dull", "fun", "scary", "sweet", "bland", "overrated"}


def _local_negation(tokens, start, value, apparent_start, apparent_end):
    flags = []
    low = max(0, start - 7)
    for j in range(start - 1, low - 1, -1):
        w = tokens[j]
        if w in _PUNCT or w in _SCOPE_BREAK:
            break
        tail = tokens[j + 1:start]
        nxt = tokens[j + 1] if j + 1 < len(tokens) else ""
        if w == "or" and not any(x in _NEGATORS for x in tokens[max(low, j - 4):j]):
            break
        if w in {"it", "this", "that", "they", "i", "he", "she", "we", "you"} and (
            j > low and tokens[j - 1] in {"reason", "why", "way", "time", "part"}
        ):
            break
        if apparent_start <= j < apparent_end and w in _NEGATORS:
            continue
        if w == "but" and j > 0 and tokens[j - 1] == "anything":
            flags.append("not")
        if w == "far" and nxt == "from":
            flags.append("not")
        if w == "less" and nxt == "than":
            flags.append("not")
        if w == "little" and (j == 0 or tokens[j - 1] not in {"a", "this", "that", "so"}):
            if len(tail) <= 3 and value > 0 and nxt not in {"bit", "by", "movie", "film"}:
                flags.append("barely")
        if w in _NEGATED_BY_FAILURE and nxt == "to" and len(tail) <= 5:
            flags.append("not")
        if w in _NEGATORS:
            if w == "nor" and "neither" in tokens[low:j]:
                break
            if any(tokens[j:j + len(seq)] == seq for seq in _NEG_SKIP_BY_WORD.get(w, ())):
                continue
            if w == "no" and nxt in {"one", "body"} and "to" not in tail:
                continue
            if w in {"not", "never", "no", "without"} and len(tail) >= 4:
                if any(x in {"but", "although", "though", "when", "because"} for x in tail):
                    continue
                if "the" in tail and any(x in _BE for x in tail[tail.index("the") + 1:]):
                    continue
            if w in {"not", "never"} and nxt == "too" and value < 0:
                flags.append("barely")
            else:
                flags.append(w)
    if start >= 2 and tokens[start - 2:start] == ("anything", "but"):
        flags.append("not")
    if start < len(tokens) and tokens[start] != "not":
        if tokens[start + 1:start + 2] == ("not",) and tokens[start + 2:start + 3] in {
            (), ("!",), (".",)
        }:
            flags.append("not")
    if len(flags) % 2:
        if value < 0:
            value *= -0.69 if any(flag in _SOFT_NEGATION for flag in flags) else -0.78
        else:
            value *= -0.87 if any(flag in _SOFT_NEGATION for flag in flags) else -0.98
    elif flags:
        value *= 0.78
    return value


def _interpret_word(tokens, i, score, terminator):
    word = tokens[i]
    prev = tokens[i - 1] if i else ""
    prev2 = tokens[i - 2] if i > 1 else ""
    nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
    nxt2 = tokens[i + 2] if i + 2 < len(tokens) else ""
    if word == "like":
        if not (prev in _PRONOUNS | _NEGATORS | {"really", "do", "did", "does", "actually",
                                               "would", "could", "quite", "always", "much",
                                               "enough", "still", "even", "also", "to"}):
            return 0.0
        if prev in {"would", "could", "to"} and nxt in {"to", "see", "say"}:
            return 0.0
        if prev in {"you", "we"} and prev2 in {"if", "whether"}:
            return 0.2
    if word == "works" and (prev in _ARTICLES or nxt in {"as", "for", "at", "by", "in", "of"}):
        if nxt not in {"as", "for"} or prev in {"who", "she", "he", "that"}:
            return 0.0
        return score * 0.65
    if word == "worked" and nxt in {"at", "for", "with", "on", "as"}:
        return 0.0
    if word in {"well", "properly", "nicely"} and prev in {
        "done", "acted", "made", "shot", "written", "directed", "executed",
        "constructed", "staged", "told", "edited", "works", "worked", "work",
        "plays", "played", "performed", "paced", "cast", "delivered", "put",
        "aged", "handled", "flows", "blends",
    }:
        return 2.25
    if word in {"poorly", "badly"} and nxt in _PRONOUNS | {"want", "wanted"}:
        return 0.0
    if word == "pretty" and (nxt in _SUCCESS or _word_score(nxt) != 0.0 or nxt in _EXCESS):
        return 0.0
    if word == "moving" and (nxt in {"to", "from", "toward", "away", "picture", "pictures", "on", "through"}
                              or prev in {"keep", "keeps", "kept", "starts", "start"}):
        return 0.0
    if word == "original" and nxt in {"version", "material", "novel", "book", "score", "title",
                                      "series", "work", "source", "screenplay"}:
        return 0.0
    if word in {"delivers", "deliver", "delivered"} and nxt in {"a", "an", "the", "his", "her", "their"}:
        if nxt2 in {"package", "letter", "message", "speech", "baby", "line", "lines", "mail"}:
            return 0.0
        if _word_score(nxt2) != 0:
            return 0.25
    if word in {"win", "wins", "winner", "winning", "successful"} and nxt in {
        "the", "an", "a", "game", "race", "election", "contest", "war", "politician", "businessman",
    }:
        return score * 0.27
    if word in {"cold", "flat", "dry", "wooden", "rich", "weak", "cheap", "violent", "strong"}:
        if nxt in {"war", "weather", "coffee", "table", "plate", "land", "chair",
                   "floor", "desk", "house", "man", "woman", "sister", "father",
                   "mother", "family", "neighborhood", "beer", "wine"}:
            return score * 0.17
    if word in {"bad", "good", "evil", "terrible", "awful", "miserable", "tragic"} and nxt in _STORY_OBJECTS:
        if nxt not in {"experience", "story", "tale", "character", "characters", "look"}:
            return score * 0.34
    if word in {"laugh", "laughs", "laughed"} and nxt == "at" and nxt2 in {"it", "this", "the"}:
        return -0.9
    if word in {"perfect", "great", "good", "fine", "sweet", "lovely"} and prev == "oh":
        return score * (0.70 if terminator != "?" else 0.15)
    if word == "perfection" and prev in {"to", "with"}:
        return 4.2
    if word in _DEGREE and _word_score(nxt) != 0:
        if word in {"disappointingly", "laughably", "painfully"} and _word_score(nxt) > 0:
            return score
        return 0.0
    if word in {"missed", "misses", "missing", "miss"} and prev in {"can", "not", "never"}:
        return -0.65
    if word in {"tired", "bored", "excited"} and nxt == "of":
        return score * 1.25
    return score


def _unit_weight(tokens, start, end, value):
    left = tokens[max(0, start - 5):start]
    right = tokens[end:end + 4]
    if any(word in _ASPECTS for word in right[:2]):
        if not any(word in _THINGS for word in right[:1]):
            value *= 0.84
    elif any(word in _ASPECTS for word in left[-4:]):
        if not any(word in _THINGS for word in left[-4:]):
            value *= 0.86
    if left and left[-1] in _DEGREE:
        value *= _DEGREE[left[-1]]
        if len(left) > 1 and left[-2] in {"very", "really", "so", "a"}:
            if left[-2] == "a" and left[-1] == "little":
                value *= 0.88
            elif left[-2] != "a":
                value *= 1.11
    elif left[-2:] in {("a", "bit"), ("kind", "of"), ("sort", "of")}:
        value *= 0.72
    if left and left[-1] in {"too", "overly", "excessively", "unduly"}:
        if tokens[start] in _EXCESS:
            value = -max(abs(value) * 1.12, 1.95)
        elif value < 0:
            value *= 1.23
    if left and left[-1] == "less" and value != 0.0:
        value *= -0.74
    if left and left[-1] == "more" and right[:1] == ("than",):
        value *= 1.12
    if right and right[0] == "enough" and value > 0:
        value *= 0.8
    if left[-2:] in {("at", "least"), ("at", "best")} and value > 0:
        value *= 0.44
    if left[-2:] == ("at", "worst") and value < 0:
        value *= 0.55
    if left[-2:] in {("if", "only"), ("instead", "of"), ("rather", "than")} and value > 0:
        value *= -0.85
    if tokens[start] == "only" and end - start > 1 and value < 0 and (
        right and right[0] in {"problem", "flaw", "complaint", "gripe"}
    ):
        value *= 0.45
    return value


def _span_positions(tokens):
    starts = []
    offset = 0
    for token in tokens:
        starts.append(offset)
        offset += len(token) + 1
    return starts


def _width_group(values):
    if not values:
        return 0.0
    values.sort(reverse=True)
    return values[0] + sum(
        value * (0.79 if index < 3 else 0.55 if index < 6 else 0.37)
        for index, value in enumerate(values[1:], 1)
    )


def _clause_score(tokens, scale, terminator):
    joined = " ".join(tokens)
    positions = _span_positions(tokens)
    apparent = list(_APPARENT.finditer(joined))
    reports = list(_REPORT.finditer(joined))
    story = list(_INTRO_CONTENT.finditer(joined))
    if _has_sequence(tokens, _CONCLUSION):
        scale *= 1.27
    if tokens[:2] == ("at", "first") or tokens[:3] == ("in", "the", "beginning"):
        scale *= 0.74
    if tokens[:3] in {("the", "only", "problem"), ("my", "only", "complaint"),
                      ("my", "only", "gripe"), ("the", "only", "flaw")}:
        scale *= 0.61
    if tokens[:2] == ("at", "least") or tokens[:2] == ("at", "best"):
        scale *= 0.67
    positives = []
    negatives = []
    seen = {}
    i = 0
    while i < len(tokens):
        item = _phrase_at(tokens, i)
        word = tokens[i]
        prev = tokens[i - 1] if i else ""
        if item is not None:
            end, value = item
        else:
            end = i + 1
            value = _interpret_word(tokens, i, _word_score(word), terminator)
            if word in _EXCESS and prev in {"too", "overly", "excessively", "unduly"}:
                if value == 0:
                    value = -1.95
            if word == "work" and (prev in {"not", "never", "really", "does", "did"} or
                                   tokens[i + 1:i + 3] == ("at", "all")):
                value = 1.85
            if word == "sense" and prev in {"any", "much", "little"}:
                if "make" in tokens[max(0, i - 4):i] or "makes" in tokens[max(0, i - 4):i]:
                    value = 1.55
            if word in {"care", "connect", "engage", "laugh", "smile"} and (
                tokens[max(0, i - 2):i] in {("make", "me"), ("made", "me")}
            ):
                value = 2.05
            if word == "funny" and terminator == "?" and "supposed" in tokens[:i]:
                value = -1.7
            if word in {"star", "stars", "thumbs", "spoiler", "view", "movie", "film"}:
                value = 0.0
            if word in {"unfortunately", "sadly", "mercifully"} and " " + word + " " in " " + joined + " ":
                if value < 0 and len(tokens) <= 2:
                    value *= 0.7

        if value != 0.0:
            value = _unit_weight(tokens, i, end, value)
            a_start = a_end = -1
            for match in reversed(apparent):
                if match.end() <= positions[i] <= match.end() + 40:
                    a_start = sum(position < match.start() for position in positions)
                    a_end = sum(position < match.end() for position in positions)
                    break
            value = _local_negation(tokens, i, value, a_start, a_end)

            for match in reversed(reports):
                if match.end() <= positions[i] <= match.end() + 34:
                    trail = joined[match.end():positions[i]]
                    if not re.search(r"\b(?:and|or|until|then|so|because)\b", trail):
                        if value > 0:
                            value *= -0.78
                        elif "have" in match.group() or "supposed" in match.group():
                            value *= 0.23
                        break
            if a_start >= 0:
                # An adjective inside a prediction or an advertisement is
                # weaker evidence than a direct judgment by the reviewer.
                neg_in_prediction = any(t in _NEGATORS for t in tokens[a_start:a_end])
                if neg_in_prediction and value > 0 and any(
                    t in {"this", "so", "such"} for t in tokens[a_end:i]
                ):
                    value *= 1.02
                else:
                    value *= 0.38

            if item is None and word in _WEAK_CONTENT and story:
                if any(m.end() <= positions[i] <= m.end() + 43 for m in story):
                    value *= 0.26

            signature = tokens[i:end]
            count = seen.get(signature, 0)
            seen[signature] = count + 1
            if count > 0:
                value *= 0.82 if count == 1 else 0.55
            if value > 0:
                positives.append(value)
            elif value < 0:
                negatives.append(-value)

        i = end

    if _SUSPICION.search(joined):
        negatives.append(4.1)
    if not positives and not negatives:
        if tokens[:2] in {("watch", "it"), ("see", "it")} and len(tokens) <= 7:
            positives.append(2.3)
        elif tokens[:1] == ("avoid",) and len(tokens) <= 7:
            negatives.append(2.75)
        elif tokens[:1] in {("skip",), ("pass",)} and (
            len(tokens) == 1 or tokens[1] in {"on", "the", "this", "it"}
        ):
            negatives.append(2.9)
        elif tokens[:3] in {("give", "me", "a"), ("spare", "me", "the")} and (
            tokens[3:4] == ("break",) or tokens[:1] == ("spare",)
        ):
            negatives.append(2.4)
    return _width_group(positives) * scale, _width_group(negatives) * scale


_RATING_RE = re.compile(
    r"(?<![\w\d.])(\d+(?:\.\d+)?)\s*(?:/|out\s+of)\s*(5|10|100|4)\b",
    re.I,
)
_STAR_RE = re.compile(r"\b(zero|one|two|three|four|five|\d(?:\.\d+)?)\s*(?:-\s*)?stars?\b", re.I)
_GRADE_RE = re.compile(r"(?:\b(?:grade|rating)\s*[:=]\s*|^\s*|[\[(])([A-F][+-]?)(?=\s*(?:[.!]?\s*$|[\])]))")


def _rating_value(ratio):
    if ratio >= 0.93:
        return 5.3
    if ratio >= 0.76:
        return 4.05
    if ratio >= 0.65:
        return 2.7
    if ratio >= 0.60:
        return 1.45
    if ratio >= 0.50:
        return -0.55
    if ratio >= 0.40:
        return -2.6
    if ratio >= 0.26:
        return -3.9
    return -5.25


def _rating(text):
    matches = list(_RATING_RE.finditer(text))
    for match in reversed(matches):
        value, denominator = map(float, match.groups())
        if value <= denominator:
            return _rating_value(value / denominator)
    stars = list(_STAR_RE.finditer(text))
    for match in reversed(stars):
        tail = text[match.end():]
        head = text[max(0, match.start() - 38):match.start()]
        if not (re.match(r"^\s*[!.?)]*\s*$", tail) or
                re.search(r"\b(?:give|gave|giving|rating|rate|rated|only|solid|award)\b", head, re.I)):
            continue
        number = match.group(1).lower()
        if number == "one" and re.match(r"\s+(?:of|in|from|plays|who|is)\b", tail, re.I):
            continue
        number = {"zero": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5"}.get(number, number)
        number = float(number)
        if number <= 5:
            return _rating_value(number / 5)
    match = _GRADE_RE.search(text)
    if match:
        grade = match.group(1)
        score = {"A": 4.8, "B": 2.8, "C": -1.0, "D": -3.7, "E": -4.6, "F": -5.1}[grade[0]]
        return score + (0.55 if grade.endswith("+") else -0.55 if grade.endswith("-") else 0)
    return 0.0


_EMOTIONS = {
    "😍": 3.8, "🥰": 3.6, "❤️": 3.2, "❤": 3.1, "👍": 3.0, "👏": 2.85,
    "🤩": 3.7, "😊": 2.2, "😀": 2.2, "😄": 2.35, "😁": 2.35, "🙂": 1.35,
    "😂": 1.2, "🤣": 1.3, "👎": -3.7, "🤮": -4.4, "🤢": -3.9,
    "😡": -3.2, "😠": -3.0, "🙄": -2.55, "😴": -2.75, "💩": -4.3,
    "😒": -2.7, "☹": -2.8, "😞": -2.8, "😑": -2.1, "😕": -1.6,
}
_EXPECTATION_REVERSAL = re.compile(
    r"(?P<setup>\b(?:i|we) (?:thought|assumed|figured|feared|expected)\b[^.;!?]{1,120}?)"
    r"[, ]+\bbut (?:i|we) (?:was|were) (?:so |very |dead )?wrong\b"
)
_AFTER_ANTITHESIS = re.compile(r"(?:[,;.!]\s*|\s+)\b(?:just kidding|yeah right)\s*[.!?]*$")
_STOPWORD_NEG = re.compile(r"(?:^|[,;.!?]\s*)not\s*[!.]*\s*$")
_SECOND_OPTION = re.compile(
    r"\b(?:it|this|the (?:film|movie)) (?:is|was) (?:no more than|at best)\b"
)


def _emoji_score(text):
    text = text.replace("❤️", "❤")
    value = 0.0
    for char, score in _EMOTIONS.items():
        count = text.count(char)
        if count:
            value += score * (1.0 + 0.25 * min(count - 1, 3))
    value += 1.9 * min(2, len(re.findall(r"(?<!\w)(?::|;)-?[)D]", text)))
    value -= 2.25 * min(2, len(re.findall(r"(?<!\w)(?::|;)-?\(", text)))
    return max(-8.0, min(8.0, value))


def _evaluate(text):
    tokens = tuple(_TOKEN_RE.findall(text))
    clauses = _clauses(tokens)
    pos = neg = 0.0
    recent = []
    for words, scale, terminator in clauses:
        p, n = _clause_score(words, scale, terminator)
        pos += p
        neg += n
        if p or n:
            recent.append(p - n)
    return pos, neg, recent


def predict(state) -> dict:
    original = _text(state)
    normalized = _normalize(original)
    positive, negative, judgments = _evaluate(normalized)
    score = positive - negative

    if len(judgments) > 1 and positive and negative:
        # Favor the latest actual judgment in a close mixed review, while
        # keeping a minor afterthought from overwhelming a clear verdict.
        score += 0.19 * max(-5.0, min(5.0, judgments[-1]))

    reversal = _EXPECTATION_REVERSAL.search(normalized)
    if reversal is not None:
        p, n, _ = _evaluate(reversal.group("setup"))
        implied = max(-4.4, min(4.4, (n - p) * 1.7))
        score += implied

    if _SECOND_OPTION.search(normalized) and abs(score) < 2.0:
        score -= 0.65

    emoji = _emoji_score(original)
    grade = _rating(original)
    if re.search(r"(?<!\w)/s\s*[.!]?\s*$", original, re.I) or _AFTER_ANTITHESIS.search(normalized):
        score = -score if abs(score) > 0.1 else -1.25
    elif _STOPWORD_NEG.search(normalized) and score > 0:
        score = -score
    score += emoji + grade * 1.15

    if score > 0.0:
        return {"answer": "positive"}
    if score < 0.0:
        return {"answer": "negative"}

    if re.search(r"\b(?:alas|ugh+|yuck|boo+|blech|unfortunately|regrettably)\b", normalized):
        return {"answer": "negative"}
    if judgments and judgments[-1] < 0:
        return {"answer": "negative"}
    return {"answer": "positive"}