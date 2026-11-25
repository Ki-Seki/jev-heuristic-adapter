import re
import unicodedata


_WORD_GROUPS = [
    (4.2, """
        masterpiece masterpieces magnificent phenomenal extraordinary sublime
        perfection flawless unforgettable transcendent superlative
    """),
    (3.5, """
        excellent outstanding superb brilliant amazing fantastic wonderful
        marvelous marvellous fabulous exceptional exquisite spectacular
        breathtaking astonishing awesome splendid sensational riveting
        mesmerizing mesmerising enthralling exhilarating exhilaratingly
    """),
    (2.8, """
        great terrific delightful delicious enthrall engross captivating
        captivatingly compelling poignant profound powerful moving touching
        heartwarming heartfelt inspiring inspirational beautiful gorgeous
        stunning impressive remarkable admirable admirable ingenious
        imaginative inventive original refreshing rewarding satisfying
        satisfying entertaining hilarious hysterical uproarious
        fascinating absorbing gripping suspenseful thrilling exciting
        engrossing enchanting charming endearing lovable loveable
        lovable irresistible impeccable polished accomplished assured
        elegant graceful vibrant vivid luminous dazzling
    """),
    (2.3, """
        enjoy enjoyable enjoyment enjoyed enjoys enjoying entertain entertains
        entertained entertainment delight delights delighted delightful
        love loved loves loving adore adored adores adoring
        recommend recommended recommends recommending
        funny fun pleasure pleasures pleasurable pleasing pleased pleasant
        worthwhile worthy worth watchable rewatchable
        clever smart intelligent insightful perceptive thoughtful
        sensitive nuanced subtle expressive evocative resonant affecting
        authentic convincing believable credible naturalistic realistic
        effective successful success succeeds succeed succeeded
        skillful skilful skillfully skilfully deft deftly dexterous
        talented talent artistry craftsmanship craftsmanship
        witty wit humor humour humorous comical droll
        solid strong engaging interesting appealing attractive
        terrific tremendous lovely sweet tender humane soulful
        earnest sincere sincerity honesty honest
        energetic lively buoyant exuberant spirited vigorous
        fresh innovative creative creativity originality innovation
        richness rich depth substance meaning meaningful
        intimate absorbing haunting heartbreaking harrowing
        resonant resonance emotional emotion emotionful
        inspiring inspired inspiration
        gem gems treasure treasures triumph triumphs triumphant
        achievement achievements accomplishment accomplishments
        classic classics memorable
        satisfying satisfaction
        favorite favourite favorites favourites
        best better superior excellence
        laudable commendable praiseworthy
        underrated underappreciated undervalued
        badass goated slaps
    """),
    (1.5, """
        good fine decent nice likable likeable amusing amusement amused
        amuse amuses amused pleasing enjoyable engaging
        competent capable efficient serviceable respectable
        confident confidence assured assurance
        ambition ambitious audacious bold daring fearless
        unpredictable surprising surprise surprises surprised
        unexpected offbeat quirky idiosyncratic eccentric
        playful buoyancy playfulness exuberance
        affection affectionate warmth warm
        intelligence intellect intellectual literate literary
        intelligence imagination inventiveness ingenuity
        subtlety nuance nuances complexity dimensional multidimensional
        insight insights perception
        grace elegance beauty
        charm charisma charismatic
        laughs laugh laughing laughed chuckles chuckle giggles giggle
        smile smiles smiling grin grinning
        empathy empathetic compassion compassionate
        human humanity humanistic
        excitement thrill thrills tension suspense
        momentum energy verve vitality gusto zest
        funnier funniest finest greatest
        brisk fleet tight taut crisp
        wellcrafted
        professional meticulous detailed precision precise
        articulate eloquent eloquence
        relevant relevance timely important significance significant
        refreshing freshness
        promising promise potential
        comfort comforting soothing reassuring
        optimistic optimism hopeful hope uplifting uplift
        entertainingly
        escapist escapism
        immerse immersive immersion
        hypnotic hypnotize hypnotizes
        startling provocative thoughtfulness
        ambitious ambition
        neatly apt nicely
        justice tribute homage
        rousing robust substantial
        recommendable accessible relatable
        distinctive distinct
        unconventional
        overlooked
        rewatch replay
        approved approve approval
        positive positives
        welcome welcomed
        inventive
        rocks rocked
        gr8 awsome awsm
    """),
    (0.7, """
        okay ok adequate passable tolerable fair modest simple straightforward
        unpretentious unassuming earnestness earnest
        effortlessness effortless easy breezy breeziness
        cute adorable cuddly
        gentle gentleness
        nostalgic nostalgia
        attractive colorful colourful
        competent competence
        amusingly
        challenging challenge
        disturbing unsettling unnerving chilling eerie creepy scary frightening
        scares scare frightened
        brutal visceral gritty grit
        sadness sorrow melancholy melancholic
        tears tearful cry crying cried weep weeping wept
        heart soul
        ambitiousness
        real truth truthful
        watchability
        slick stylish style stylized stylised
        elaborate sumptuous lush lavish
        pleasantness
        consistency consistent
        thematic
        curious curiosity
        special
        romantic
        meditative contemplative
        modestly
        goofy
        works worked
        redeem redeems redeemed redeeming
        redeemable
        alive
        rollicking
        unabashed
        worthwhile
    """),
    (-0.7, """
        uneven unevenness mixed middling average ordinary standard
        familiar conventional predictable
        sentimental sentimentality
        bleak grim gloomy somber sombre
        silly silliness
        absurd
        difficult problematic
        disposable forgettability
        workmanlike routine modestly
        obscure obscurity
        odd peculiar strange weird
        excessive excess
        distracted distracting distraction
        simplistic
        derivative derivation
        indulgence
        obvious
        obscure
        thin
        slow
        strained
        flawed flaws flaw
        preach preachy
        serious-minded
        vapidity
    """),
    (-1.6, """
        mediocre mediocrity bland dull flat drab stale tired tedious
        weak weaker weakest weakness weaknesses
        clumsy clunky awkward cumbersome ungainly
        sluggish plodding lumbering labored laboured laborious
        mechanical perfunctory pedestrian generic formulaic
        superficial shallow empty emptiness hollow
        banal banality trite trivial triviality
        conventionality unimaginative uninspired uninspiring
        unoriginal originalityless
        pretentious pretension pretentions pretenses
        pompous ponderous portentous
        selfimportant
        contrived forced artificial fake phony phoney
        implausible improbable unbelievable unconvincing unpersuasive
        unrealistic inauthentic unnatural inane
        incoherence incongruous inconsistent inconsistency
        incohesive
        complicated confusing confused confusion muddled murky
        convoluted convolutions
        rambling meandering aimless aimlessness directionless
        pointless meaningless purposeless
        unnecessary needless redundant repetitive repetition repetitious
        longwinded overlong overstuffed bloated
        overwrought overheated overblown overdone overbearing overacted
        overact overacts overacting underwhelming underwhelm underwhelmed
        uninteresting unengaging uninvolving disengaged
        indifferent indifference impersonal detached
        soulless heartless lifeless listless lifelessness
        joyless humorless humourless humorlessness
        uninvolving
        manipulative manipulation calculated contrivance contrivances
        cliche cliches clichéd cliched cliché clichés
        corny cornball hokey cheesy cheese campy
        sappy syrupy mawkish maudlin saccharine treacly
        schmaltzy schmaltz
        heavyhanded
        predictable predictability
        obviousness
        simplistic simplification
        unambitious
        pointless
        excessive excessively
        noisy loud shrill cacophonous
        cheap shoddy tacky tawdry shabby
        ugly ugliness
        sour sourness dour
        mean meanest meaner
        cynical cynicism
        insulting offensive offensiveness insensitive
        tasteless crass vulgar vulgarity gratuitous gratuitously
        unnecessary
        irritating irritatingly irksome grating annoying annoyance annoy
        annoyed annoys aggravating aggravate
        tiresome tiring
        sluggishness
        disappointing disappointment disappoint disappoints disappointed
        frustrating frustration frustrate frustrated frustrates
        unsatisfying unsatisfactory unsatisfied
        unfulfilling unsound
        unpleasant unpleasantness
        depressing depressed
        monotonous monotony
        unevenly
        questionable dubious
        questionable
        merely
        wasted wastes wasting waste
        fail fails failed failing failure failures
        missing missed miss misses
        lacking lackluster lacklustre
        careless carelessness lazy laziness
        sloppy sloppiness slapdash amateurish amateur
        inept ineptitude incompetent incompetence
        forgettable
        forgettably
        unfortunate unfortunately regrettably regrettable
        sadly alas
        sorry regret regrets regretted
        disappointing
        unappealing unlikable unlikeable unlovable
        repulsive distasteful
        distaste
        laughable ludicrous ridiculous preposterous
        dubious
        silly
        underdeveloped undeveloped
        unexplained unresolved incomplete unfinished unsolved
        rushed hurried hasty
        disjointed disconnected disorganized disorganised
        dismal dreary dreariness
        pallid paltry pitiful pathetic
        dated outdated antiquated obsolete
        forgettable
        dubious
        recycled rehashed retread rehash
        ripoff
        worse
        negative negatives
        plod plods drag drags dragged dragging
        numb numbing
        intrusive
        unremarkable unexceptional
        meh blah
        gimmick gimmicks gimmicky
        gimmickry
        obnoxious
        pandering pander panders
        exploitative exploitation
        dishonest dishonesty disingenuous
        miscast miscasting misfire misfires misfired
        misjudged misconceived misguided mishandled mishmash
        botched bungled bungle butchered mangled
        botch
        demeaning
        weary weariness
        deflated deflating
    """),
    (-2.8, """
        bad poor poorly boring boredom bored bore bores
        terrible awful horrible dreadful atrocious abysmal appalling
        miserable lousy wretched rotten
        disaster disastrous debacle catastrophe catastrophic
        fiasco mess messy muddle travesty
        dreadful
        pointless worthless useless futile
        unbearable intolerable insufferable
        painful painfully agonizing excruciating torturous tortuous
        unwatchable unendurable
        ineffectual ineffective
        unfunny unamusing
        unentertaining unexciting
        dullest duller dumb dumbest dumber stupid stupidest stupidity
        idiotic idiot idiots idiocy moronic moron morons imbecilic
        brainless witless mindless mindlessness
        senseless nonsensical nonsense
        absurdity
        atrociously horrendously horribly terribly awfully
        hideous horrendous
        detestable despicable deplorable contemptible
        disgusting disgust disgusted nauseating nauseous sickening revolting
        offensive
        despise despised despises loathe loathed loathing
        hate hated hates hating hatred
        dislike disliked dislikes disliking
        abhor abhorred abhorrent
        detest detested
        crap crappy craptastic garbage trash trashy rubbish junk dreck drivel
        schlock schlocky tripe bilge dross hogwash
        bullshit horseshit shit shitty shite
        suck sucks sucked sucking stinks stink stinker stinkers
        stank blows
        worst
        embarrassing embarrassingly embarrassment embarrassed
        cringe cringey cringeworthy cringeworthy cringy
        unmitigated
        irredeemable
        irredeemably
        overrated overhyped
        insult insults
        betrayal betray betrayed
        atrocious
        torture torments torment
        headache headaches
        dud duds flop flops bombed
        pointless
        punishing
        contemptuous contempt
        exploit
        offensive
        unredeemable
        deplorably
        incompetent
    """),
    (2.6, """
        excelente excelentes fantástico fantástica fantastico fantastica
        maravilloso maravillosa estupendo estupenda magnífico magnífica
        magnifico magnifica entretenido entretenida divertido divertida
        emocionante encantador encantadora genial
        bueno buena buen buenísimo buenísima
        superbe magnifique formidable émouvant captivant réussi réussie
        excellent excellente excellents excellentes merveilleux merveilleuse
        beau belle drôle drole intéressant intéressante
        toll großartig grossartig hervorragend wunderbar fantastisch
        spannend unterhaltsam gelungen empfehlenswert
        ótimo ótima otimo otima maravilhoso maravilhosa divertido divertida
        eccellente magnifico magnifica bellissimo bellissima emozionante
    """),
    (-2.6, """
        malo mala malos malas pésimo pésima pesimo pesima aburrido aburrida
        aburrimiento decepcionante decepción decepcion horrible horribles
        terrible terribles basura aburrida
        mauvais mauvaise ennuyeux ennuyeuse nul nulle médiocre mediocre
        décevant décevante déception raté ratée
        schlecht langweilig schrecklich furchtbar enttäuschend enttauschend
        langweilige
        ruim péssimo péssima pessimo pessima chato chata entediante
        decepcionante horrível horrivel
        brutto brutta noioso noiosa pessimo pessima deludente
    """),
]

_LEXICON = {}
for _score, _words in _WORD_GROUPS:
    for _word in _words.split():
        _LEXICON[_word] = _score

_LEXICON.update({
    "good": 2.1, "great": 3.1, "bad": -2.8, "poor": -2.5,
    "boring": -3.6, "bored": -3.2, "boredom": -3.4,
    "excellent": 3.7, "masterpiece": 4.5, "worst": -4.4,
    "best": 3.4, "better": 2.4, "worse": -3.0,
    "awful": -4.0, "terrible": -4.0, "horrible": -4.0,
    "unwatchable": -4.4, "disappointing": -3.0,
    "disappointed": -3.0, "disappoint": -2.8, "disappointment": -3.0,
    "waste": -3.2, "wasted": -2.8, "forgettable": -2.5,
    "dull": -2.8, "tedious": -2.9, "dreadful": -3.7,
    "stupid": -3.1, "dumb": -2.3, "silly": -0.8,
    "predictable": -2.0, "formulaic": -2.4,
    "fun": 2.6, "funny": 2.8, "hilarious": 3.4,
    "love": 3.0, "loved": 3.3, "hate": -3.7, "hated": -3.9,
    "enjoy": 2.5, "enjoyable": 2.7, "entertaining": 2.9,
    "wonderful": 3.6, "beautiful": 2.8, "moving": 2.6,
    "flawed": -1.1, "flaws": -1.0, "flaw": -1.0,
    "slow": -1.0, "sad": -0.2, "sadly": -1.4,
    "complex": 1.3, "complicated": -0.4,
    "romantic": 0.35, "special": 0.6, "heart": 0.8,
    "merely": 0.0, "modestly": 0.0, "mean": -0.4,
    "familiar": -0.35, "strange": 0.0, "weird": -0.2,
    "odd": -0.2, "peculiar": -0.2, "promise": 0.6,
    "potential": 0.4, "promising": 1.2, "ambitious": 1.3,
    "emotion": 0.5, "emotional": 1.6, "work": 0.3,
    "works": 1.7, "worked": 1.4, "working": 0.2,
    "like": 1.8, "liked": 2.5, "liking": 1.8, "likes": 1.5,
    "fail": -2.0, "fails": -2.0, "failed": -2.0, "failing": -2.0,
    "sucks": -3.8, "sucked": -3.8, "garbage": -4.0,
    "trash": -3.6, "shit": -3.2, "meh": -2.2,
    "average": -0.8, "okay": 0.5, "ok": 0.5,
    "fine": 1.0, "decent": 1.3, "adequate": 0.2,
    "mediocre": -2.3, "cinematic": 0.5,
    "coherent": 1.8, "coherence": 1.5, "incoherent": -3.0,
    "original": 1.7, "originality": 1.8,
    "depth": 1.6, "substance": 1.5, "point": 0.0,
    "sense": 0.0, "plot": 0.0, "story": 0.0,
    "acting": 0.0, "cinematography": 0.0, "direction": 0.0,
    "violent": 0.0, "violence": 0.0, "horror": 0.0,
    "dark": 0.0, "evil": 0.0, "death": 0.0, "dead": 0.0,
    "sick": -0.5, "disturbing": 0.6, "frightening": 1.0,
    "disturbed": -0.8, "terrifying": 1.2,
    "tedium": -3.0, "breathtaking": 3.7,
})


_CONTRACTIONS = {
    "can't": "can not", "cannot": "can not", "cant": "can not",
    "won't": "will not", "wont": "will not",
    "shan't": "shall not", "ain't": "is not",
    "isn't": "is not", "isnt": "is not",
    "aren't": "are not", "arent": "are not",
    "wasn't": "was not", "wasnt": "was not",
    "weren't": "were not", "werent": "were not",
    "don't": "do not", "dont": "do not",
    "doesn't": "does not", "doesnt": "does not",
    "didn't": "did not", "didnt": "did not",
    "couldn't": "could not", "couldnt": "could not",
    "wouldn't": "would not", "wouldnt": "would not",
    "shouldn't": "should not", "shouldnt": "should not",
    "haven't": "have not", "havent": "have not",
    "hasn't": "has not", "hasnt": "has not",
    "hadn't": "had not", "hadnt": "had not",
    "mustn't": "must not", "needn't": "need not",
    "it's": "it is", "that's": "that is", "there's": "there is",
    "what's": "what is", "here's": "here is",
    "he's": "he is", "she's": "she is",
    "i'm": "i am", "im": "i am",
    "you're": "you are", "we're": "we are", "they're": "they are",
    "i've": "i have", "you've": "you have", "we've": "we have",
    "they've": "they have",
    "i'd": "i would", "you'd": "you would", "we'd": "we would",
    "i'll": "i will", "you'll": "you will", "we'll": "we will",
    "it'll": "it will", "they'll": "they will",
}
_CONTRACTION_RE = re.compile(
    r"\b(?:" + "|".join(re.escape(x) for x in
                         sorted(_CONTRACTIONS, key=len, reverse=True)) + r")\b"
)
_TOKEN_RE = re.compile(
    r"[^\W\d_]+(?:'[^\W\d_]+)*|\d+(?:\.\d+)?|[^\s\w]",
    re.UNICODE
)


def _normalize(text):
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")
    text = text.replace("–", " ; ").replace("—", " ; ")
    text = text.replace("-", " ")
    text = text.lower()
    text = _CONTRACTION_RE.sub(lambda m: _CONTRACTIONS[m.group(0)], text)
    text = re.sub(r"\b([a-z]+)n't\b", r"\1 not", text)
    return text


def _tokens(text):
    return _TOKEN_RE.findall(_normalize(text))


_PHRASE_GROUPS = [
    (0.0, """
        not only; not just; not merely; not to mention; whether or not;
        no doubt; without a doubt; without doubt; without question;
        beyond doubt; beyond question; no question about;
        no matter; no wonder; no idea;
        nothing but; nothing short of; nothing less than; nothing if not;
        no less than; all but; all too; more or less;
        can not help but; can not help; could not help but; could not help;
        hard not to; difficult not to; impossible not to;
        could not be more; can not be more;
        if not;
        love story; love stories; love triangle; love triangles;
        love affair; love affairs; love interest; love interests;
        romantic comedy; romantic comedies; romantic drama;
        special effects; special effect; visual effects;
        good guy; good guys; bad guy; bad guys;
        good cop; bad cop; evil genius;
        bad boy; bad boys; good girl; bad girl; mean girls;
        good versus evil; good and evil; good vs evil;
        good luck; bad luck; good fortune; bad things; good things;
        happy ending; happy endings; happy ever after; happily ever after;
        guilty of murder; guilty verdict; guilty conscience;
        terrible crime; horrible crime; terrible tragedy;
        cold war; great war; great depression;
        low budget; big budget; high budget;
        big screen; small screen; silver screen;
        short film; long shot; real life; true story;
        coming of age; based on a true story;
        the likes of; looks like; look like; looking like; sounds like;
        working class; work of fiction; works of fiction;
        hard working; hard work;
    """),
    (4.4, """
        not to be missed; not be missed; do not miss this;
        do not miss it; do not miss; must see; a must watch; must watch;
        one of the best; among the best;
        can not recommend it highly enough; can not recommend highly enough;
        can not recommend this enough; can not recommend it enough;
        could not recommend it more; could not recommend this more;
        can not praise it enough;
        could not have been better; could not be better;
        does not get any better; does not get better than this;
        does not get much better;
        blew me away; blown away; knocked my socks off;
        cinema at its best; filmmaking at its best;
        best movie ever; best film ever; best film of the year;
        best movie of the year;
    """),
    (3.2, """
        highly recommend; strongly recommend; heartily recommend;
        worth watching; worth seeing; well worth watching; well worth seeing;
        worth your time; worth my time; worth the time; worth the money;
        worth every penny; worth the price of admission;
        a joy to watch; a pleasure to watch; pure pleasure; pure joy;
        sheer delight; pure delight; absolute delight;
        great fun; good fun; so much fun; too much fun;
        lots of fun; a lot of fun; loads of fun;
        a great time; had a blast; a total blast;
        laugh out loud; laughing out loud; laughed out loud;
        laugh a minute; laugh riot; laugh fest;
        wickedly funny; darkly funny; terribly funny; painfully funny;
        seriously funny; riotously funny;
        edge of your seat; edge of my seat;
        on the edge of my seat;
        a breath of fresh air; breath of fresh air;
        tour de force; a class act; first rate; top notch; top tier;
        top quality; world class; five star;
        pitch perfect; note perfect; spot on;
        hit all the right notes; hits all the right notes;
        fires on all cylinders; firing on all cylinders;
        knock it out of the park; knocks it out of the park;
        knocked it out of the park;
        stands the test of time; stood the test of time;
        better than ever; better than expected;
        exceeded my expectations; exceeds expectations; exceeded expectations;
        surpassed my expectations; more than delivers;
        two thumbs up; thumbs way up;
        can not get enough; could not get enough;
        can not wait to watch it again; can not wait to see it again;
        would watch again; will watch again;
        not a dull moment; never a dull moment;
        not a dry eye; not leave a dry eye;
        no small feat; no mean feat;
    """),
    (2.2, """
        well made; well directed; well acted; well written; well crafted;
        well executed; well developed; well paced; well staged; well told;
        well shot; well cast; well performed; well produced; well done;
        well worth; worth a watch; worth a look; worth a viewing;
        worth checking out; worth a visit; worth the effort;
        well rounded; finely tuned; finely crafted;
        good acting; good performances; good performance;
        great acting; great performances; great performance;
        good story; good storytelling; good script;
        good movie; good film;
        good looking; beautifully shot; beautifully filmed;
        beautifully realized; beautifully realised;
        emotionally resonant; emotionally satisfying; emotional resonance;
        rich in detail; rich with detail;
        attention to detail;
        easy to enjoy; easy to like; hard to resist;
        wins you over; won me over; wins us over;
        won my heart; warms the heart; warm hearted;
        big hearted; good natured; good humored; good humoured;
        feel good; feelgood; made me smile; makes you smile;
        made me laugh; makes you laugh; made us laugh; makes us laugh;
        made me cry; moved me; moved to tears;
        laugh and cry; laughed and cried;
        fell in love; fall in love; falling in love;
        full of life; full of heart; full of energy;
        full of surprises; packed with laughs;
        brings to life; brought to life;
        comes alive; come alive;
        comes to life; come to life;
        comes together; come together;
        holds up; still holds up; holds your attention;
        held my attention; holds the attention; kept my attention;
        kept me interested; kept me engaged; kept me entertained;
        kept me hooked; had me hooked;
        stands out; stand out;
        delivers the goods; deliver the goods;
        does its job; does the job;
        gets it right; got it right;
        hits the mark; hit the mark;
        hits the spot; hit the spot;
        hits home; hit home;
        right on target;
        plenty of laughs; plenty to enjoy; much to enjoy; much to admire;
        a lot to like; much to like; lots to like;
        nothing to dislike; little to dislike;
        what is not to like; what is not to love;
        what not to love; what not to like;
        how can you not love; how can you not like;
        can not go wrong; could not go wrong;
        does not disappoint; did not disappoint; never disappoints;
        will not disappoint; did not let me down;
        lives up to; lived up to; living up to;
        more than meets the eye;
        go see it; go see this; see this movie;
        check it out; watch this movie;
        thumbs up;
        guilty pleasure; guilty pleasures;
        deliciously bad; so bad it is good; so bad it is great;
        so bad , it is good; so bad it is funny;
        awfully good; terribly good; frighteningly good;
        frighteningly funny; frighteningly effective;
        not bad; not at all bad; not that bad; not too bad; not so bad;
        not half bad; is not half bad; none too shabby; not too shabby;
        far from bad; far from boring;
        no complaints; can not complain;
        not boring; never boring;
        never less than entertaining; never less than interesting;
        slow burn; slow burning;
        thought provoking; thought provokingly; mind blowing;
        eye opening; eye opener;
        nerve wracking; nail biting; spine tingling;
        heart wrenching; gut wrenching;
        high spirited; free wheeling; sure footed;
        a cut above; above average; above the average;
        a hidden gem; hidden gem;
        critically acclaimed; award winning; oscar worthy;
        kick ass; kicks ass; kicking ass; the shit;
        is fire; was fire; is lit; was lit;
        pas mal;
    """),
    (1.1, """
        good enough; more than adequate; more than decent;
        entertaining enough; funny enough;
        good but not great; good , but not great;
        no masterpiece but; not a masterpiece but;
        silly fun; dumb fun; mindless fun; dumb but fun;
        dumb , but fun; silly but fun; silly , but fun;
        harmless fun; light entertainment;
        a pleasant surprise; pleasant surprise;
        has its charms; has some charm;
        some good laughs; a few laughs; a few good laughs;
        a few chuckles; some laughs;
        moments of brilliance; moments of beauty;
        has its moments; has their moments; has its good moments;
        has a heart; heart in the right place;
        heart is in the right place;
        worth considering;
        at its best; at their best;
        not without charm; not without merit; not without its charms;
        not without its pleasures;
        not the worst; not as bad as;
        no worse than;
        reasonably entertaining; reasonably enjoyable;
        mildly amusing; mildly entertaining;
        better than nothing;
        can not wait;
        self aware; tongue in cheek;
        does what it sets out to do; does what it promises;
        knows what it is doing; knows what it wants to be;
    """),
    (-0.6, """
        not perfect; not quite perfect; not entirely perfect;
        not flawless; far from perfect;
        not a masterpiece; no masterpiece;
        not the best; not brilliant;
        not groundbreaking; nothing groundbreaking;
        does not break new ground; breaks no new ground;
        nothing revolutionary;
        not for everyone; will not be for everyone;
        not for everybody; not everyone will like;
        well intentioned; good intentions; best intentions;
        at its worst; at their worst;
        some good ideas; has potential;
        mixed bag; a mixed bag; hit and miss;
        hit or miss;
        could have been; should have been; might have been;
        unintentionally funny; unintentional comedy;
        by the numbers;
    """),
    (-1.6, """
        not great; not very good; not particularly good;
        not especially good; not all that good; not much good;
        not very interesting; not particularly interesting;
        not quite enough; not enough;
        nothing new; nothing special; nothing remarkable;
        nothing original; nothing memorable;
        nothing to write home about; little to write home about;
        not much to recommend; little to recommend;
        little to offer; not much to offer;
        too familiar; too obvious; too easy; too simplistic;
        too sentimental; too sweet; too cute;
        too slow; too long; goes on too long; far too long;
        too much going on; too many characters;
        little more than; nothing more than;
        only occasionally; only intermittently;
        not much fun; little fun; few laughs; very few laughs;
        only a few laughs; only a few good moments;
        leaves something to be desired; leaves much to be desired;
        leave something to be desired;
        lost something in translation;
        does not add up; does not amount to much;
        not up to par; below par; below average;
        less than satisfying; less than compelling;
        less than impressive; less than thrilling;
        less than stellar; less than successful;
        less than the sum of its parts;
        just another; yet another;
        run of the mill; garden variety; paint by numbers;
        going through the motions; goes through the motions;
        goes through familiar motions;
        seen it all before; seen this all before;
        seen it before; been there done that;
        been there , done that;
        too clever by half; too clever for its own good;
        too smart for its own good;
        only saving grace; sole saving grace;
        only good thing; only good part; only redeeming feature;
        only redeeming quality;
        cheap laughs; cheap thrills;
        paper thin; one note; one dimensional; two dimensional;
        heavy handed; heavy handedness;
        self important; self indulgent; self indulgence;
        self conscious; self satisfied;
        trying too hard; tries too hard; try too hard;
        tries hard to be funny;
        all style and no substance; style over substance;
        style over story;
        over the top;
        so so; ho hum;
        is mid; was mid; pretty mid;
    """),
    (-2.8, """
        no fun; no laughs; no charm; no heart; no soul;
        no depth; no substance; no energy; no tension; no suspense;
        no imagination; no originality; no creativity;
        no plot; no story; no point; no purpose;
        no sense; makes no sense; made no sense;
        no chemistry; zero chemistry; zero laughs;
        no payoff; without a payoff;
        without substance; without purpose;
        no redeeming qualities; no redeeming quality;
        no redeeming features;
        nothing works; nothing happens; not much happens;
        not worth; not worthwhile; not worth it;
        not worth watching; not worth seeing;
        not worth the time; not worth your time; not worth my time;
        not worth the money; not worth the effort;
        waste of time; waste of money; waste of talent;
        wasted potential; wasted opportunity; missed opportunity;
        lost opportunity; wastes its potential;
        wasted my time; wastes your time; wasting your time;
        wants to be; wishes it were;
        can not recommend; could not recommend;
        would not recommend; do not recommend; would not recommend it;
        do not bother; does not bother;
        do not bother watching; do not bother seeing;
        why bother; why did they bother;
        give it a miss; give this a miss;
        skip it; skip this; skip this one; skip this movie;
        avoid it; avoid this; avoid this movie;
        save your money; save your time; save yourself the trouble;
        leave it alone;
        thumbs down; two thumbs down;
        does not work; did not work; do not work;
        fails to work; does not deliver; fails to deliver;
        falls flat; fall flat; fell flat; falling flat;
        falls short; fall short; fell short; falling short;
        falls apart; fall apart; fell apart; falling apart;
        falls to pieces;
        loses steam; runs out of steam; ran out of steam;
        loses its way; lost its way; loses the plot;
        misses the mark; missed the mark; misses the point;
        off the mark;
        goes nowhere; going nowhere; went nowhere;
        dead on arrival; dead in the water;
        left me cold; leaves me cold; leaves you cold;
        leaves us cold; left us cold; left cold;
        left me bored; left me disappointed;
        leaves a bad taste; left a bad taste;
        leaves you wanting; left me wanting;
        bad taste in my mouth;
        leaves no impression; left no impression;
        lost interest; lose interest; losing interest;
        lost my interest; bored me;
        put me to sleep; puts me to sleep; put you to sleep;
        puts you to sleep; put us to sleep;
        fell asleep; falling asleep; nodding off;
        walked out; walk out; walking out;
        turned it off; switched it off; could not finish;
        could not sit through; can not sit through;
        could not stay awake;
        wanted to like; want to like; wanted to love;
        wish i liked; wish i could like;
        expected better; hoped for more; hoped for better;
        could do better; should be better;
        should have been better; could have been better;
        does not live up; did not live up; do not live up;
        fails to live up; failed to live up; never lives up;
        does not measure up; failed to meet expectations;
        let me down; lets you down; letdown; let down;
        big disappointment; huge disappointment;
        bad acting; poor acting; wooden acting; wooden performances;
        wooden performance; stilted dialogue; bad dialogue;
        poorly written; poorly acted; poorly directed; poorly made;
        poorly executed; poorly paced; poorly edited; poorly developed;
        badly written; badly acted; badly directed; badly made;
        badly executed; badly paced; badly edited;
        badly miscast; horribly miscast;
        bad movie; bad film; lousy movie; lousy film;
        hard to watch; difficult to watch; painful to watch;
        hard to care; difficult to care; impossible to care;
        hard to like; difficult to like; impossible to like;
        hard to enjoy; difficult to enjoy;
        laugh at rather than; laugh at instead of;
        do not care; did not care; does not care;
        could not care less; can not care less;
        who cares;
        not for me; is not my thing; not my cup of tea;
        does nothing for me; did nothing for me;
        no reason to watch; no reason to see; no reason to like;
        no reason to care;
        no excuse for; sorry excuse for;
        all over the place;
        empty headed; muddle headed; muddleheaded;
        mind numbing; mind numbingly;
        soul crushing; soul sucking;
        ham fisted; ham handed; hammy acting;
        half baked; half assed; half hearted;
        laugh free; charm free; humor free; humour free;
        devoid of life;
    """),
    (-4.2, """
        avoid at all costs; steer clear; stay away from this;
        stay away from it;
        one of the worst; among the worst;
        worst movie ever; worst film ever;
        worst movie of the year; worst film of the year;
        could not be worse; could not have been worse;
        can not get any worse;
        complete waste of time; total waste of time;
        utter waste of time; absolute waste of time;
        complete waste of money; total waste of money;
        two hours of my life; hours of my life back;
        want my money back; wanted my money back;
        want my time back; give me my money back;
        bored to tears; bored to death; boring as hell;
        dull as dishwater; dull as ditchwater;
        watching paint dry; watch paint dry;
        watching grass grow;
        piece of crap; pile of crap; load of crap;
        piece of shit; pile of shit; steaming pile;
        utter garbage; complete garbage; absolute garbage;
        complete rubbish; total rubbish; utter rubbish;
        absolute trash; complete trash; total trash;
        insult to the audience; insult to the viewer;
        insult to your intelligence; insults your intelligence;
        insults the intelligence; insult the intelligence;
        insults my intelligence; insulting the audience;
        treats the audience like idiots; treats viewers like idiots;
        bottom of the barrel; scraping the bottom;
        no redeeming value; without any redeeming qualities;
        can not save; could not save; can not rescue; could not rescue;
        can not redeem; could not redeem;
        unable to save; unable to rescue;
        nothing can save; nothing could save;
        even worse than; worse than bad;
        not even funny; not remotely funny; not remotely entertaining;
        not in a good way;
        so bad it hurts; so bad it is painful;
        too bad to be good;
        a complete disaster; a total disaster; an unmitigated disaster;
        cinematic disaster; cinematic catastrophe;
        masterpiece of garbage; masterpiece of stupidity;
    """),
]

_PHRASES = {}
for _score, _phrase_text in _PHRASE_GROUPS:
    for _phrase in _phrase_text.split(";"):
        _phrase_tokens = tuple(_tokens(_phrase.strip()))
        if _phrase_tokens:
            _PHRASES[_phrase_tokens] = _score

_PHRASE_INDEX = {}
for _phrase_tokens, _score in _PHRASES.items():
    _PHRASE_INDEX.setdefault(_phrase_tokens[0], []).append(
        (_phrase_tokens, _score)
    )
for _first in _PHRASE_INDEX:
    _PHRASE_INDEX[_first].sort(key=lambda item: len(item[0]), reverse=True)

_INTENSIFIERS = {
    "very": 1.3, "really": 1.25, "extremely": 1.6, "utterly": 1.6,
    "absolutely": 1.6, "completely": 1.4, "totally": 1.4,
    "thoroughly": 1.4, "incredibly": 1.5, "amazingly": 1.3,
    "remarkably": 1.35, "wildly": 1.4, "so": 1.25, "such": 1.15,
    "quite": 1.1, "rather": 0.9, "somewhat": 0.7, "fairly": 0.8,
    "mildly": 0.55, "slightly": 0.6, "occasionally": 0.6,
    "intermittently": 0.6, "sporadically": 0.6, "almost": 0.5,
    "nearly": 0.55, "partially": 0.6, "mostly": 0.9,
    "pretty": 1.1, "surprisingly": 1.15, "unexpectedly": 1.15,
    "too": 1.2, "damn": 1.35, "fucking": 1.5, "bloody": 1.25,
    "awfully": 1.35, "terribly": 1.35, "painfully": 1.35,
    "ridiculously": 1.4, "exceptionally": 1.4, "especially": 1.2,
    "particularly": 1.15, "truly": 1.25, "genuinely": 1.2,
    "unbelievably": 1.45, "unusually": 1.15, "exceedingly": 1.45,
    "deeply": 1.25, "profoundly": 1.35, "relentlessly": 1.25,
    "consistently": 1.2, "simply": 1.15,
}
_NEGATORS = {
    "not", "never", "no", "neither", "nor", "without", "nothing",
    "hardly", "barely", "scarcely", "seldom", "rarely",
    "lack", "lacks", "lacked", "lacking",
    "fail", "fails", "failed", "failing",
    "unable", "unable", "devoid", "bereft",
    "avoid", "avoids", "avoided", "avoiding",
    "eschew", "eschews", "eschewed", "eschewing",
    "refuse", "refuses", "refused", "refusing",
    "nicht", "kein", "keine", "keinen", "keiner",
    "não", "nao", "nunca", "jamais", "pas", "non",
}
_NEGATION_BOUNDARIES = {
    ".", "!", "?", ";", ":", "but", "yet", "however", "although", "though",
    "despite", "because", "whereas", "while", "and", "until", "unless",
    "except", "instead", "nevertheless", "nonetheless",
}
_SENTENCE_BOUNDARIES = {".", "!", "?", ";"}
_ASPECT_NOUNS = {
    "fun", "humor", "humour", "wit", "charm", "depth", "substance",
    "originality", "imagination", "creativity", "energy", "tension",
    "suspense", "laughs", "laugh", "entertainment", "pleasure",
    "interest", "heart", "soul", "coherence", "intelligence", "meaning",
    "chemistry", "payoff", "appeal", "merit", "value",
}


def _word_value(word):
    if word in _LEXICON:
        return _LEXICON[word]
    candidates = []
    if word.endswith("ly") and len(word) > 4:
        candidates.extend((word[:-2], word[:-1] + "e"))
        if word.endswith("ily"):
            candidates.append(word[:-3] + "y")
    if word.endswith("ies") and len(word) > 4:
        candidates.append(word[:-3] + "y")
    if word.endswith("s") and len(word) > 3:
        candidates.append(word[:-1])
        if word.endswith("es"):
            candidates.append(word[:-2])
    if word.endswith("ed") and len(word) > 4:
        root = word[:-2]
        candidates.extend((root, root + "e"))
        if len(root) > 2 and root[-1] == root[-2]:
            candidates.append(root[:-1])
        if root.endswith("i"):
            candidates.append(root[:-1] + "y")
    if word.endswith("ing") and len(word) > 5:
        root = word[:-3]
        candidates.extend((root, root + "e"))
        if len(root) > 2 and root[-1] == root[-2]:
            candidates.append(root[:-1])
    if word.endswith("ness") and len(word) > 6:
        root = word[:-4]
        candidates.append(root)
        if root.endswith("i"):
            candidates.append(root[:-1] + "y")
    for candidate in candidates:
        if candidate in _LEXICON:
            return _LEXICON[candidate]
    if re.search(r"(.)\1{2,}", word):
        for count in (2, 1):
            candidate = re.sub(r"(.)\1{2,}", lambda m: m.group(1) * count, word)
            if candidate in _LEXICON:
                return _LEXICON[candidate]
    return 0.0


def _extract_text(state, depth=0):
    if isinstance(state, str):
        return state
    if depth > 10 or state is None:
        return ""
    if isinstance(state, dict):
        keys = {str(k).lower(): k for k in state}
        preferred = (
            "text", "sentence", "review", "review_text", "reviewtext",
            "movie_review", "movie_review_text", "review_body",
            "input_text", "input_sentence", "sentence_text",
            "utterance", "comment", "content", "body", "passage",
            "document", "message", "description", "input", "value",
        )
        for key in preferred:
            if key in keys:
                result = _extract_text(state[keys[key]], depth + 1)
                if result:
                    return result
        for key in ("data", "state", "example", "instance", "inputs", "payload"):
            if key in keys:
                result = _extract_text(state[keys[key]], depth + 1)
                if result:
                    return result
        excluded = {
            "id", "index", "label", "answer", "sentiment", "category",
            "question", "question_name", "instructions", "criteria",
            "output_schema", "type", "task", "metadata", "title", "name",
            "language", "source", "role",
        }
        parts = []
        for key, value in state.items():
            if str(key).lower() not in excluded:
                result = _extract_text(value, depth + 1)
                if result:
                    parts.append(result)
        if parts:
            return "\n".join(parts)
        if len(state) == 1:
            return _extract_text(next(iter(state.values())), depth + 1)
        return ""
    if isinstance(state, (list, tuple)):
        return "\n".join(
            part for part in
            (_extract_text(value, depth + 1) for value in state)
            if part
        )
    return ""


def _events(tokens):
    events = []
    masked = [False] * len(tokens)
    i = 0
    while i < len(tokens):
        found = False
        for phrase, value in _PHRASE_INDEX.get(tokens[i], ()):
            end = i + len(phrase)
            if end <= len(tokens) and tuple(tokens[i:end]) == phrase:
                for j in range(i, end):
                    masked[j] = True
                if value:
                    events.append((i, end, value, True))
                i = end
                found = True
                break
        if found:
            continue
        word = tokens[i]
        value = _word_value(word)
        if value:
            if word in {"like", "likes"}:
                previous = tokens[max(0, i - 3):i]
                if not any(x in previous for x in
                           ("i", "we", "you", "they", "not", "never", "really",
                            "absolutely", "would", "will", "did", "do")):
                    value = 0.0
            if word in _INTENSIFIERS:
                for j in range(i + 1, min(len(tokens), i + 3)):
                    if tokens[j] in _SENTENCE_BOUNDARIES or tokens[j] == ",":
                        break
                    if _word_value(tokens[j]):
                        value = 0.0
                        break
            if word == "original" and i > 0 and tokens[i - 1] == "the":
                if i + 1 == len(tokens) or tokens[i + 1] in {
                    "film", "movie", "version", "one", ".", ",", "!", "?"
                }:
                    value = 0.0
            if value:
                events.append((i, i + 1, value, False))
        i += 1
    return events, masked


def _sentence_extent(tokens, index):
    start = index
    while start > 0 and tokens[start - 1] not in _SENTENCE_BOUNDARIES:
        start -= 1
    end = index + 1
    while end < len(tokens) and tokens[end] not in _SENTENCE_BOUNDARIES:
        end += 1
    return start, end


def _discourse_weights(tokens, masked):
    n = len(tokens)
    weights = [1.0] * n
    last_start = 0
    for i, word in enumerate(tokens):
        if word in _SENTENCE_BOUNDARIES and i + 1 < n:
            if any(t.isalpha() for t in tokens[i + 1:]):
                last_start = i + 1
    if last_start:
        for j in range(last_start, n):
            weights[j] *= 1.12

    for i, word in enumerate(tokens):
        if masked[i]:
            continue
        if word in {"but", "yet", "however", "nevertheless", "nonetheless"}:
            previous = tokens[max(0, i - 2):i]
            if word == "but" and previous and previous[-1] in {
                "anything", "nothing", "all", "help"
            }:
                continue
            if word == "yet" and any(x in previous for x in ("not", "as")):
                continue
            lookback = tokens[max(0, i - 12):i]
            if word == "but" and any(
                lookback[k:k + 2] in (["not", "only"], ["not", "just"],
                                      ["not", "merely"])
                for k in range(max(0, len(lookback) - 1))
            ):
                continue
            start, end = _sentence_extent(tokens, i)
            for j in range(start, i):
                weights[j] *= 0.65
            for j in range(i + 1, end):
                weights[j] *= 1.25
            if i - start <= 1 and start > 0:
                previous_start, _ = _sentence_extent(tokens, max(0, start - 2))
                for j in range(previous_start, start):
                    weights[j] *= 0.8
        elif word in {"although", "though", "despite", "albeit", "unlike"}:
            start, end = _sentence_extent(tokens, i)
            if i - start <= 2:
                comma = None
                for j in range(i + 1, end):
                    if tokens[j] == ",":
                        comma = j
                        break
                if comma is not None:
                    for j in range(i + 1, comma):
                        weights[j] *= 0.55
                    for j in range(comma + 1, end):
                        weights[j] *= 1.15
            else:
                for j in range(i + 1, end):
                    weights[j] *= 0.65
                for j in range(start, i):
                    weights[j] *= 1.08
        elif word in {"overall", "ultimately", "ultimately", "unfortunately"}:
            _, end = _sentence_extent(tokens, i)
            for j in range(i, end):
                weights[j] *= 1.2
    return weights


def _negation_factor(tokens, start, value, masked):
    count = 0
    words_seen = 0
    target = tokens[start]
    j = start - 1
    while j >= 0 and words_seen < 8:
        word = tokens[j]
        if word in _NEGATION_BOUNDARIES:
            if word == "but" and j > 0 and tokens[j - 1] == "anything":
                count += 1
            break
        if word in {"(", ")", "[", "]"}:
            break
        if word == ",":
            following = tokens[j + 1:start]
            if following and following[0] not in {"or", "nor"}:
                break
            j -= 1
            continue
        if word.isalpha():
            words_seen += 1
        if masked[j]:
            j -= 1
            continue
        if word in _NEGATORS:
            if word == "no" and j + 1 < len(tokens) and tokens[j + 1] in {
                "more", "less", "later", "earlier"
            }:
                j -= 1
                continue
            count += 1
        elif word == "less" and words_seen <= 4:
            if not (j > 0 and tokens[j - 1] in {"at", "no"}):
                count += 1
        elif word in {"little", "few"} and target in _ASPECT_NOUNS:
            if not (j > 0 and tokens[j - 1] in {"a", "the", "those", "these"}):
                count += 1
        elif word == "from" and j > 0 and tokens[j - 1] == "far":
            count += 1
        elif word == "of" and j > 0 and tokens[j - 1] in {"free", "short"}:
            count += 1
        j -= 1
    if count % 2:
        return -0.82 if value > 0 else -0.78
    return 1.0


def _intensity(tokens, start):
    factor = 1.0
    for j in range(start - 1, max(-1, start - 4), -1):
        word = tokens[j]
        if word in _NEGATION_BOUNDARIES or word in {",", "(", ")"}:
            break
        if word in _INTENSIFIERS:
            factor *= _INTENSIFIERS[word]
    return min(2.0, max(0.35, factor))


def _unrealized_factor(tokens, start, end, value):
    if value <= 0:
        return 1.0
    a = start
    while a > 0 and start - a < 11:
        if tokens[a - 1] in _SENTENCE_BOUNDARIES or tokens[a - 1] in {
            ",", "but", "however", "yet", "although", "though"
        }:
            break
        a -= 1
    previous = tokens[a:start]
    joined = " ".join(previous)
    if re.search(r"\b(?:could|should|would|might) have (?:been|made|felt|had)\b",
                 joined):
        return -0.65
    if any(phrase in joined for phrase in (
        "supposed to be", "meant to be", "ought to be", "should have",
        "wish it was", "wish it were", "wished it was", "if only",
    )):
        return -0.55
    if re.search(
        r"\b(?:try|tries|trying|tried|attempt|attempts|attempting|strives|striving)"
        r"(?: \w+){0,3} to(?: be)?\b", joined
    ):
        return -0.25
    following = tokens[end:min(len(tokens), end + 10)]
    if "would be" in joined and "if" in following:
        return -0.55
    return 1.0


def _comparison_weight(tokens, start):
    left = max(0, start - 10)
    for j in range(start - 1, left - 1, -1):
        if tokens[j] in _SENTENCE_BOUNDARIES or tokens[j] in {
            ",", "but", "however", "yet"
        }:
            break
        if tokens[j] == "than":
            previous = tokens[max(left, j - 6):j]
            if any(x in previous for x in
                   ("better", "worse", "funnier", "superior", "inferior")):
                return 0.3
    return 1.0


def _rating_score(text):
    normalized = unicodedata.normalize("NFKC", text).lower()
    word_numbers = {
        "zero": "0", "one": "1", "two": "2", "three": "3",
        "four": "4", "five": "5", "six": "6", "seven": "7",
        "eight": "8", "nine": "9", "ten": "10",
    }
    number_text = re.sub(
        r"\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten)\b",
        lambda m: word_numbers[m.group(0)], normalized
    )
    values = []
    spans = []
    pattern = re.compile(
        r"(?<![\d.])(\d+(?:\.\d+)?)\s*"
        r"(?:/\s*|out\s+of\s+|of\s+)"
        r"(10|5|4)\b"
    )
    for match in pattern.finditer(number_text):
        numerator = float(match.group(1))
        denominator = float(match.group(2))
        if 0 <= numerator <= denominator:
            fraction = numerator / denominator
            if fraction >= 0.6:
                values.append(2.0 + 6.0 * (fraction - 0.6))
            else:
                values.append(-1.5 - 6.0 * (0.6 - fraction))
            spans.append((match.start(), match.end()))
    for match in re.finditer(
        r"\b([0-5](?:\.\d+)?)\s*(?:-\s*)?stars?\b", number_text
    ):
        if any(a <= match.start() < b for a, b in spans):
            continue
        stars = float(match.group(1))
        if stars >= 3:
            values.append(2.0 + (stars - 3) * 1.3)
        else:
            values.append(-1.8 - (3 - stars) * 1.1)
    if not values:
        return 0.0
    return sum(values) / len(values) * 1.4


def _symbol_score(text):
    positive = ("😍", "🥰", "❤️", "❤", "💖", "💗", "🤩", "👍", "😊", "😁", "😄")
    negative = ("👎", "🤮", "🤢", "😡", "😠", "😒", "🙄", "😑", "💩")
    value = 0.0
    for symbol in positive:
        value += min(text.count(symbol), 3) * 1.4
    for symbol in negative:
        value -= min(text.count(symbol), 3) * 1.6
    value += 1.4 * len(re.findall(r"(?<!\w)(?::|;|=)-?[)D](?!\w)", text))
    value -= 1.6 * len(re.findall(r"(?<!\w)(?::|=)-?[(](?!\w)", text))
    return value


def predict(state) -> dict:
    text = _extract_text(state)
    tokens = _tokens(text)
    if not tokens:
        return {"answer": "positive"}

    events, masked = _events(tokens)
    weights = _discourse_weights(tokens, masked)
    total = 0.0
    contributions = []

    for start, end, base, is_phrase in events:
        value = base
        word = tokens[start]
        if not is_phrase and word in {"fail", "fails", "failed", "failing"}:
            upcoming = tokens[end:min(len(tokens), end + 6)]
            if "to" in upcoming and any(_word_value(t) < -0.5 for t in upcoming):
                value = 0.0
        value *= _negation_factor(tokens, start, value, masked)
        value *= _intensity(tokens, start)
        if base > 0 and value > 0:
            value *= _unrealized_factor(tokens, start, end, base)
        value *= _comparison_weight(tokens, start)
        if end > start:
            value *= sum(weights[start:end]) / (end - start)
        total += value
        contributions.append((start, value))

    total += _rating_score(text)
    total += _symbol_score(text)

    normalized = _normalize(text)
    if re.search(r"\b(?:yeah|oh)\s*,?\s*right\b", normalized):
        total -= 1.5
    if re.search(r"\b(?:great|wonderful|fantastic)\s*[,!]\s*another\b", normalized):
        total -= 4.5
    if re.search(r"(?:^|\s)/s(?:\s|$|[.!])", text.lower()) and total > 0:
        total = -max(2.0, total * 0.8)

    if not contributions and not total:
        words = [t for t in tokens if t.isalpha()]
        if words and len(words) <= 8:
            if any(t in {"no", "nope", "nah", "avoid", "skip", "pass"} for t in words):
                total = -1.0
            elif any(t in {"yes", "yep", "yup", "wow", "bravo"} for t in words):
                total = 1.0

    return {"answer": "negative" if total < -0.15 else "positive"}