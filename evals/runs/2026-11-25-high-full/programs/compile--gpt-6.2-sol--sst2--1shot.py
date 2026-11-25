import re
import unicodedata


def _word_table(groups):
    result = {}
    for weight, words in groups:
        for word in words.split():
            result[word] = weight
    return result


_WORDS = _word_table((
    (0.48, """
        adequate adventurous ambitious atmospheric authentic bold brisk bright
        colorful competent conventional crafty credible curious cute dashing
        decent decorative detailed distinctive earnest energetic exotic expressive
        familiar fashionable gentle glossy handsome heartfelt honest hopeful
        idyllic impressive-looking inviting jaunty lighthearted lively lush
        mild novel passable pleasant polished professional promising provocative
        respectable restrained sincere slick sprightly stylish substantial
        sure surprising sweet tactile tidy timely topical unusual vivid
        watchable winsome worthy zesty accessible agreeable serviceable
        assertive arresting breezy picturesque jaunty genial spry thoughtful
        literate manageable offbeat playful quirky savory tasteful qualified
        humane intimate scrappy sturdy quaint unobtrusive plausible
        """),
    (1.45, """
        absorbing accomplished affecting agile agreeable amazes appealing
        assured attractive admirable affectionate alive amusing astute
        beguiling believable beautiful bracing buoyant capable captivating
        charismatic charming cheery cheerful clever coherent comical compelling
        confident convincing cool creative crisply dazzling deft delightful
        delicious dexterous droll dynamic easygoing eccentric effective electric
        elegant eloquent enchanting encouraging endearing engaging engrossing
        enjoyable enterprising entertaining evocative exciting extraordinary
        exuberant fabulous fascinating exhilarating favorable fetching fiery fine
        flavorful fresh friendly fruitful fun funny gripping graceful gracious
        gratifying groovy gutsy happy heartening heartwarming helpful hilarious
        hit humorous imaginative immaculate impeccable impressive incisive
        ingenious insightful intelligent interesting intriguing inventive
        involving irresistible joyous joyful keen likable likeable lovely
        luminous magical marvelous marvellous meaningful meditative
        mesmerizing mesmerising mirthful moving neat nimble nuanced observant
        original perceptive poignant potent powerful precious precise profound
        pulsating punchy purposeful radiant refreshing resonant rewarding rich
        ribald riveting rollicking romantic rousing satisfying savvy seamless
        seductive sensitive sharp shining smart smooth solid soulful sparkling
        spirited splendid stimulating stirring striking strong stunning sublime
        suspenseful sympathetic talented tender terrific thrilling ticklish
        touching transcendent tremendous triumphant tuneful unconventional
        understanding unexpected uplifting vibrant visionary visceral vital
        warm welcome whimsical witty wonderful worthwhile zestful accomplished
        heartrending heartbreaking searing haunting impassioned masterly
        masterful memorable revelatory rare exceptional exemplary standout
        distinctive sophisticated graceful funny winning graceful sprightly
        electrifying disarming penetrating laudable insightful nourishing
        heartwarming engrossing unsettling illuminating informative rewarding
        jubilant ravishing resplendent affecting enjoyable sublime timeless
        convincing toothsome graceful thrilling charitable rewarding alluring
        audacious dauntless purposeful unpretentious understated unaffected
        unforced unflinching unforgettable understated astonishing inspired
        recommend recommends recommended recommending recommendation
        treasures delight delights delighted delights enjoy enjoys enjoyed
        enjoyment entertains entertained engages engaged engages respects
        laugh laughs laughed laughing laughter chuckle chuckled chuckles
        smile smiles smiled smiling relishes relish appreciate appreciated
        admiration admire admires admired applauds applaud applause deserves
        triumph triumphs grace genius chemistry depth intelligence wit humor
        humour charm charms charisma freshness elegance artistry heart warmth
        tenderness poignancy insight suspense vitality energy creativity
        originality honesty restraint finesse magic laughs sincerity appeal
        flair panache verve gusto alacrity brio class resonance soul
        pleasures pleasure satisfaction thrill thrills dazzles shines rocks
        succeeds succeeds success successful successfully works worked
        better improved improvement surpass surpasses exceeded excels
        perfects holds-up winner winners winning delightfully refreshingly
        """),
    (2.55, """
        amazing awesome best brilliant bravura breathtaking excellent
        exquisite fantastic flawless glorious gorgeous grand great incredible
        invaluable magnificent masterpiece masterpieces masterwork miraculous
        outstanding perfect phenomenal remarkable sensational spectacular
        superb superlative supreme ultimate wondrous wondrously unmissable
        impeccable incomparable irresistible stupendous staggering
        landmark gem gems treasure treasures revelation revelations
        favorite favourite favorites favourites love loves loved beloved
        adore adores adored mustsee knockout knockout outstanding triumph
        enthralling splendiferous unforgettable ingenious tremendous
        """),
    (-0.46, """
        amateurish artificial awkward bizarre brash busy callow caustic
        clinical convoluted cranky crudely cynical dated derivative didactic
        formulaic fussy gimmicky grim grating gratuitous groan hackneyed
        hammy heavyhanded hokey implausible inane indulgent labored laboured
        lopsided loud lurid mannered mawkish maudlin meandering melodramatic
        murky noisy obvious odd overblown overdone overlong overplayed
        overripe oversimplified overwrought pat pedestrian preachy predictable
        prosaic pulpy quaint ragged rambling rote sappy schmaltzy scrappy
        sentimental shallow shrill simplistic slight slow smalltime smug
        soapy sophomoric spotty strained strident stilted superficial
        syrupy talky tame trashy uneven unconvincing unexceptional
        unremarkable unrefined unsubtle unsteady unstructured untested
        unwieldy vague vapid verbose vulgar weird wobbly wooden
        clumsy shaky shaky forced mechanical frenetic repetitive
        patronizing condescending milquetoast anachronistic contrived
        overstuffed crowded cluttered disjointed unwieldy excessive
        oversentimental obtrusive dubious suspect silly silliness
        muddled middling trite familiar problematic shaky scattershot
        lethargic creaky flimsy sketchy threadbare tepid tiresome
        arguably imperfections questionable unevenness misjudged
        inflated miscast underdeveloped inessential strained jagged
        uneven oddly miscalculated miscalculation naive foolish mixed
        """),
    (-1.51, """
        abysmal abrasive absurd aggravating aimless airless anemic annoying
        apathetic appalling asinine atrocious awful baffling banal
        befuddled belabored bewildering bland bleak bloated boring
        brainless bumbling bungled careless chaotic charmless cheesy
        childish cliched clichéd clichéd cloying complacent confused
        confusing corny crass crude crummy cruelty cryptic deadening
        deficient depressing desperate dim disagreeable disappointing
        disconcerting disconnected disingenuous dismal dispiriting
        disposable disquieting dissatisfying dogmatic dreadful dreary
        dull dumb egregious embarrass embarrasses embarrassed embarrassing
        empty enervating exasperating exhausting exploitive exploitative
        fails fail failed failure false feeble fitful flat flavorless
        forgettable forgivable fragmented frustrating futile ghastly
        gluey godawful graceless grueling halfhearted halfbaked hapless
        hateful heartless heinous hollow horrible horrid humorless
        humourless idiotic illogical impenetrable improbable impersonal
        incompetent incoherent inconsequential incongruous ineffectual
        ineffective inelegant inept inert infuriating insipid insulting
        intolerable interminable irrelevant irritating joyless leaden
        lifeless limp listless loathsome lousy ludicrous lugubrious
        lukewarm lumpy mangled mediocre megrim meritless miserable
        misguided misbegotten mishandled misinformed misleading misconceived
        mistimed mockery monotonous moribund muddled mumbly musty
        nauseating needless neglect neglects neglected nonsensical
        obnoxious objectionable obscure offputting ominous onerous
        ordinary overbearing overcooked overdirected overproduced
        overreaching overworked painful paltry pathetic perfunctory
        pesky petrified pointless ponderous poor pretentious punishing
        purposeless putrid rancid redundant repellant repellent repulsive
        risible rotten rough rickety ridiculous rudderless sadistic
        sanctimonious scatterbrained schlocky secondrate selfindulgent
        shoddy shonky shortsighted shrivelled shudder sillyish
        simplistic sleazy sleepy sluggish sloppy soulless specious
        stale static sterile stodgy stupid tasteless tawdry tedious
        thin thinly tiresome tonedeaf tortuous torturous tortured
        trite trivial troubled turgid ugly unbearable unbalanced
        uncharacteristic uncinematic uncommercial uncomfortable
        undercooked underwhelmed underwhelming undistinguished
        undramatic unearned uneasy unenjoyable unenlightening
        unentertaining unequal uneven uneventful unfocused unforgivable
        unfunny ungainly unhinged unimaginative unimportant
        unimpressive uninspired unintelligent uninteresting
        unlikable unlikeable unlovable unmemorable unnecessary
        unpleasant unpolished unproductive unpromising unqualified
        unreadable unrewarding unsatisfying unsightly unsettling
        unsuccessful unsuitable unsympathetic unsuspenseful
        unwatchable unwelcome unwise unworthy vapid vile violent-minded
        wacky wasted wasteful weary wearisome weak witless wormy
        wretched wrong worthless wreck wrecked worse worst
        cliche cliché cliches clichés bore bores bored boredom
        drags drag dragged drivel dross dreck dreckish clunker
        dud duds flop bomb stinker stink stinks sucks suck sucked
        mess travesty fiasco disappointment disappoint disappointed
        disappoints disaster disasters mediocrity ineptitude stupidity
        shallowness pretension pretensions contrivance confusion
        repetition drudgery cheesiness smugness shallowness nonsense
        hokum gibberish laziness inertia inanities lethargy clutter
        monotony tedium malice misfire misfires misfired botch botched
        botches bungles bungle panders pandering irritates annoys
        grates grating groans wince winced cringe cringeworthy
        tires drags squander squandered squanders forfeits
        alienating dispirits infuriates grating excruciating unforgiving
        tortures teethgrinding grating unappealing spiritless vacuous
        lackluster lacklustre mediocre hackwork halfass halfassed
        dopey dopy stultifying petrifying malnourished cloyingly
        depressing dispiriting disenchanting exasperated overhyped
        """),
    (-2.55, """
        terrible horrendous hideous abhorrent abomination atrocious
        detestable unforgivable deplorable dreadful godawful execrable
        hate hates hated despise despised loathe loathed worst
        abysmal atrocious unwatchable unbearable catastrophic
        horrendous trulyawful woeful wretched hopeless contemptible
        """),
    (0.37, """
        drama comedy documentary story movie film cinema picture role cast
        """),
    (0.0, """
        drama comedy documentary story movie film cinema picture role cast
        ominous unsettling cruelty glory sure deserves understanding
        happy favorable helpful friendly capable romantic hopeful
        odd bleak grim chaotic dark disturbing graphic violent
        gross tragic wicked hard tragedy terror obscure petrified
        """),
))

_PHRASES = {}


def _add_phrases(weight, entries):
    for entry in entries.strip().split("|"):
        key = tuple(entry.strip().split())
        if key:
            _PHRASES[key] = weight


_add_phrases(0.0, """
    special effects | love story | love stories | love interest | love interests |
    love affair | in love | falls in love | fall in love | falling in love |
    falling out of love | loved one | loved ones | love triangle | love life |
    love letter | puppy love | make love | making love | young love | true love |
    family drama | good guys | good guy | bad guy | bad guys | bad boy |
    bad boys | good versus evil | good and evil | bad things happen |
    dark comedy | bad news bears | worst case scenario | good will hunting |
    best friend | best friends | best supporting | best actress | best actor |
    best picture | best director | better half | bad blood | hard to believe |
    hard times | good fortune | unfortunate events | great depression |
    great britain | great war | great escape | happy ending | happy endings |
    simply red | screen time | art form | a little more | all the same |
    best of intentions | good intentions | noble intentions | well intentioned |
    well meaning | good intentions aside | moving picture | moving pictures |
    moving target | moving on | mental illness | poor family | poor people |
    out of work | get to work | work of fiction | great white | work in progress |
    in the works | getting better | funny looking | funny thing | funny guy |
    perfect stranger | perfect strangers | original film | original version |
    original movie | original story by | fine line | perfect storm |
    strong language | good looking | hot air balloon | rotten tomatoes |
    hilarious consequences as | good grief | laugh track | laugh tracks |
    compelling evidence | sweet sixteen | as luck would have it |
    by no means of | not only | not just | not merely | not simply |
    nothing but | nothing short of | nothing less than | no less than |
    no fewer than | no more and no less | not to mention | make no mistake |
    cannot help but | can not help but | could not help but |
    cannot help feeling | can not help feeling | could not help feeling |
    cannot help liking this | more than just | more than a little |
    in no time | hard pressed | it is no secret | no doubt | without a doubt |
    beyond a doubt | no kidding | not surprisingly | not surprisingly enough |
    not exactly the same | for better or worse | whether good or bad |
    would not be surprised | not everyone | not for everyone | not for all tastes |
    lack thereof | what not | if not more | if not better | little by little |
    how it works | film works by | worth of footage | worth of film |
    one of the few | note perfect as | take a look at | it was about time
    """)
_add_phrases(3.5, """
    a must see | must see | must watch | highly recommended | cannot recommend enough |
    can not recommend enough | cannot recommend it enough | can not recommend it enough |
    two thumbs up | thumbs up | see this movie | go see it | go see this |
    one of the best | one of the finest | nothing short of brilliant |
    deserves to be seen | deserves a wide audience | deserves an audience |
    worth seeing | well worth seeing | worth a look | worth watching |
    worth the price of admission | worth every penny | worth its weight in gold |
    well worth watching | well worth the trip | well worth your time |
    delivers the goods | hits all the right notes | hits the spot |
    on the edge of your seat | on the edge of my seat | steals the show |
    stole the show | blew me away | blew us away | blew my mind |
    takes your breath away | took my breath away | a work of art |
    better than ever | does not get much better | cannot get much better |
    can not get much better | could not be better | could not have been better |
    never a dull moment | never dull | never boring | not a dull moment |
    i was blown away | as good as it gets | everything you could want |
    loved every minute | love every minute | enjoyed every minute |
    firing on all cylinders | a cut above | rises above the crowd |
    a hell of a movie | a hell of a film | earnestly recommended |
    hits it out of the park | knocks it out of the park
    """)
_add_phrases(1.8, """
    a good time | a great time | a fun time | a laugh riot |
    an absolute blast | a real blast | have a blast | a real treat |
    a real find | a hidden gem | a crowd pleaser | crowd pleasing |
    slow burn | dumb fun | stupid fun | silly fun | good clean fun | pure fun |
    guilty pleasure | so bad it is good | so bad it is actually good |
    so bad it is funny | bad in a good way | cheesy in a good way |
    in a good way | in the best way | in the best sense |
    the right reasons | gets it right | gets so much right |
    holds your attention | holds our attention | held my attention |
    kept my attention | keeps your attention | kept me watching |
    makes you think | makes us think | made me think | thought provoking |
    thought provokingly | eye opening | eye opener | a breath of fresh air |
    laugh out loud | laughed out loud | laughed till i cried |
    laugh a minute | a barrel of laughs | comic timing | a welcome change |
    ring true | rings true | rang true | feels right |
    takes flight | comes alive | come alive | brought to life | brings to life |
    come to life | comes to life | brought it to life |
    holds up | hold up well | stands up well | stand the test of time |
    stands the test of time | stands out | stand out | stood out |
    stand up and cheer | earns its ending | well done | well made |
    well crafted | well told | well written | well acted | well directed |
    well observed | well executed | well shot | well paced | well cast |
    well performed | well staged | well realized | well realised |
    full of life | full of surprises | full of energy | full of heart |
    sense of wonder | sense of humor | sense of humour |
    plenty to like | a lot to like | much to like | something to recommend |
    a pleasure to watch | a joy to watch | easy on the eyes |
    visually striking | visually arresting | beautifully shot |
    deftly handled | assured direction | pitch perfect | note perfect |
    in good hands | an emotional punch | packs a punch | packing a punch |
    pulls it off | pull it off successfully | pulled it off |
    pays off | pay off handsomely | pays dividends | does the trick |
    does what it sets out to do | knows what it is doing | does its job |
    lives up to the hype | lived up to the hype | lives up to its promise |
    does justice to | does it justice | exceeded my expectations |
    more than lives up to | gives it new life | does not disappoint |
    did not disappoint | leaves you wanting more | left me wanting more |
    makes the most of | puts a smile on | brought tears to my eyes |
    not half bad | not too shabby | nothing wrong with that |
    hard not to like | hard not to love | difficult not to like |
    impossible not to like | impossible not to love | no small feat |
    without missing a beat | without a false note | without a hitch |
    does not miss a beat | never misses a beat | did not want it to end |
    wanted it to go on | would watch it again | want to watch it again |
    watch it again and again | do not miss it | cannot wait to see it again |
    can not wait to see it again | beats the original | tops the original |
    does not take itself too seriously | never takes itself too seriously |
    refuses to take itself too seriously | has fun with | has a ball |
    has a great deal going for it | has a lot going for it |
    a refreshing change | manages the impossible | impressive feat |
    better than it has any right to be | better than it ought to be |
    worth the effort | worth a visit | worth it | worth your while
    """)
_add_phrases(-3.6, """
    a waste of time | waste of time | a complete waste | a total waste |
    complete waste of money | waste of money | a waste of talent |
    waste of talent | save your money | save your time | do not bother |
    do not waste your time | do not waste your money | steer clear |
    avoid at all costs | stay away from this | give it a miss | skip this one |
    nothing to recommend | nothing to recommend it | little to recommend |
    not worth seeing | not worth watching | not worth the price of admission |
    not worth your time | cannot recommend it | can not recommend it |
    could not recommend it | hard to recommend | difficult to recommend |
    impossible to recommend | nothing going for it | has nothing going for it |
    worst of all | one of the worst | worse than ever | never gets better |
    turned it off | turn it off | fell asleep | puts you to sleep |
    put me to sleep | put us to sleep | made me fall asleep |
    dozed off | walked out | wanted to walk out | wanted my money back |
    could not finish it | could not sit through | cannot sit through |
    can not sit through | a train wreck | train wreck | a car wreck |
    an absolute mess | a complete mess | a hot mess | an unholy mess |
    does not work at all | fails on every level | on every level it fails |
    bad beyond belief | not a single laugh | not one laugh |
    no redeeming qualities | no redeeming features | without redeeming value |
    little redeeming value | an insult to the audience | made me cringe |
    worse than watching paint dry | like watching paint dry |
    why bother | what a waste | not worth it | leaves a lot to be desired |
    leaves much to be desired | left a lot to be desired | left much to be desired
    """)
_add_phrases(-1.9, """
    by the numbers | paint by numbers | cut and paste | run of the mill |
    been there done that | been there and done that | seen it all before |
    seen this all before | seen it before | seen this before |
    nothing new | brings nothing new | offers nothing new |
    rehash of | knock off | rip off | cheap imitation | cash grab |
    made for tv | straight to video | direct to video | assembly line |
    b movie at best | past its prime | no better than | not any better |
    not much better | no improvement | could have been better |
    should have been better | should know better | could have done better |
    could do better | would have been better | would have worked better |
    with little success | without success | to no avail | too little too late |
    too much of a good thing | too clever for its own good |
    too smart for its own good | too cute for its own good |
    too precious for its own good | too long | far too long |
    too short on | takes too long | runs too long | goes on too long |
    drags on | drags out | no end in sight | overstays its welcome |
    outstays its welcome | never gets going | takes forever |
    takes itself too seriously | took itself too seriously |
    not terribly original | not up to par | not up to scratch |
    does not add up | no point | what is the point |
    makes no sense | does not make sense | made no sense |
    does not hang together | never comes together | does not come together |
    falls apart | fell apart | falls flat | fell flat | fall flat |
    comes up short | fell short | falls short | fall short |
    misses the mark | missed the mark | misses the point |
    off the mark | off key | off putting | off puttingly |
    tone deaf | heavy handed | ham fisted | lead balloon |
    dead on arrival | dead in the water | lifeless on screen |
    flat as a pancake | out of ideas | out of gas | runs out of steam |
    running on fumes | lacks direction | loses its way | loses the plot |
    goes nowhere | go nowhere | went nowhere | going nowhere |
    nothing happens | not much happens | has nothing to say |
    nothing to say | little to say | does not say much |
    lacks substance | little substance | all style and no substance |
    style over substance | all surface | all flash | skin deep |
    paper thin | wafer thin | one dimensional | two dimensional |
    cardboard cutouts | cardboard characters | plot holes | plot hole |
    poorly made | badly made | badly written | badly acted | poorly acted |
    poorly written | badly drawn | badly directed | poorly directed |
    poorly executed | amateur hour | half baked | half hearted |
    self indulgent | self important | second rate | third rate |
    low rent | bargain basement | lowest common denominator |
    cheap laughs | cheap shots | easy target | cheap thrills |
    under the impression that | false note | sour note |
    not much to like | little to like | hard to like | difficult to like |
    hard to love | hard to sit through | hard to enjoy | painful to watch |
    a chore to watch | a chore | hard to watch | hard to care |
    did not care for | did not care about | do not care about |
    cannot bring myself to care | hard to stay awake |
    no fun | no sense of humor | no sense of humour | without a spark |
    strained for laughs | tries too hard | try too hard | trying too hard |
    not funny in the least | never quite works | never really works |
    does not hold up | did not work | does not work | does not quite work |
    not buying it | does not deliver | did not deliver |
    never delivers | fails to deliver | fails to engage | fails as |
    is not saying much | which is not saying much | that is not saying much |
    a bad idea | a big mistake | wrong reasons | in a bad way |
    for all the wrong reasons | in the worst way | lost opportunity |
    missed opportunity | a letdown | a let down | let me down |
    sunk by | hobbled by | weighed down | dragged down | dragged it down |
    brought down by | undone by | short on ideas | no laugh |
    has its moments | had its moments | not much else | and nothing else
    """)
_add_phrases(-1.1, """
    if only | little more than | nothing more than | not much more than |
    no more than a | at best | all it has going for it | the only thing going for it |
    the only good thing | the only redeeming | sole redeeming |
    few redeeming | only saving grace | saving grace | small consolation |
    just another | yet another | merely competent | barely watchable |
    just barely watchable | barely tolerable | just okay | just ok |
    merely adequate | at least it is short | could not care less |
    can not care less | could be worse | not the worst |
    raised my hopes | tries and fails | had potential | had promise |
    wasted potential | wasted opportunity | lost its charm | needs work |
    needs a rewrite | sleep inducing | eye rolling | eye roll |
    head scratching | jaw droppingly bad | no thanks | pass on this |
    a major problem | major flaws | fatal flaw | fatal flaws |
    a few problems | flaws and all | a few flaws | leaves you cold |
    left me cold | bored to tears | bored stiff | bleeds dry |
    again and again and again | wears out its welcome
    """)
_add_phrases(0.9, """
    above average | not bad at all | could do a lot worse | not without merit |
    not without its charms | not without charm | not without interest |
    not without appeal | not without its pleasures | not without pleasures |
    not without its rewards | not without rewards | more revealing |
    highly watchable | better than expected | better than you might expect |
    on its own terms | still going strong | film lover | film lovers |
    stands on its own | gets the job done | keeps things moving |
    has something to say | offers something new | makes an impression |
    nearly perfect | easy to watch | perfectly adequate | good enough
    """)

_PHRASE_INDEX = {}
for _phrase, _value in _PHRASES.items():
    _PHRASE_INDEX.setdefault(_phrase[0], []).append((_phrase, _value))
for _rows in _PHRASE_INDEX.values():
    _rows.sort(key=lambda row: len(row[0]), reverse=True)

_INTENSITY = _word_table((
    (1.16, "quite rather pretty truly really particularly especially nicely"),
    (1.36, "very decidedly genuinely highly utterly entirely pure purely deeply plainly perfectly totally"),
    (1.58, "absolutely astonishingly exceptionally enormously extremely incredibly amazingly completely remarkably thoroughly singularly overwhelmingly"),
    (1.25, "so such much far fiercely wonderfully beautifully brilliantly awfully terribly damn darn wickedly deliciously surprisingly shamelessly"),
    (0.66, "somewhat slightly marginally mildly relatively moderately faintly sortof kindof"),
    (0.59, "almost nearly partially arguably intermittently occasionally sometimes technically sporadically"),
    (0.75, "fairly merely only simply superficially just"),
))

_DEGREE_PHRASES = {
    ("a", "bit"): 0.68, ("a", "little"): 0.66, ("a", "tad"): 0.64,
    ("kind", "of"): 0.70, ("sort", "of"): 0.70, ("a", "touch"): 0.68,
    ("more", "than", "a", "little"): 1.33, ("a", "great", "deal"): 1.22,
    ("by", "far"): 1.4, ("all", "too"): 1.35, ("at", "times"): 0.72,
    ("more", "or", "less"): 0.74, ("a", "lot", "more"): 1.36,
}

_CUE_GROUPS = (
    (-1.0, """
        not | never | no | none | without | neither | nor | nothing |
        hardly | scarcely | barely | seldom | anything but | far from |
        nowhere near | no kind of | not even remotely | no longer |
        not remotely | not really | not exactly | not particularly |
        not especially | not terribly | not very | not quite | never quite |
        never really | never truly | less | less than | short on | short of |
        no trace of | free of | devoid of | bereft of | empty of | without any |
        stripped of | lacking | lacks | lack of | lacking in | absence of |
        missing | missing any | need for | in need of | could use |
        avoids | avoid | avoiding | avoided | spared | escapes | sidesteps |
        steers clear of | refuses to | refuse to | fails to | failed to |
        failing to | fail to | failure to | unable to | inability to |
        incapable of | cannot | can not | could not | could never |
        does not | do not | did not | is not | are not | was not | were not |
        has not | have not | had not | has never | have never | had never |
        will not | would not | won't | would never | no amount of |
        cannot even | can not even | does not even | does not really
        """),
    (-0.75, """
        little | few | too little | too few | tries to be | trying to be |
        tries to | tries for | aspires to | aspires to be | strives to be |
        aims to be | aims for | means to be | wants to be | wanted to be |
        wishes to be | wishes it were | hopes to be | thinks it is |
        purports to be | pretends to be | purportedly | supposed to be |
        promises to be | promises more | attempts to be | seeks to be |
        ought to have been | should have been | could have been |
        would have been | might have been | should be |
        could have made | could have used | would have worked with |
        if only | had hoped for | wished for | needed more |
        not enough | never enough | not nearly enough
        """),
)
_CUES = {}
for _weight, _entries in _CUE_GROUPS:
    for _entry in _entries.split("|"):
        _key = tuple(_entry.strip().split())
        if _key:
            _CUES[_key] = _weight

_CUE_INDEX = {}
for _key in _CUES:
    _CUE_INDEX.setdefault(_key[0], []).append(_key)
for _rows in _CUE_INDEX.values():
    _rows.sort(key=len, reverse=True)

_CUE_FALLBACK = {
    "fail": -1.5, "fails": -1.5, "failed": -1.5, "failure": -1.5,
    "failing": -1.4, "lacks": -1.3, "lack": -1.2, "lacking": -1.2,
    "devoid": -1.5, "bereft": -1.4, "missing": -0.95,
    "unable": -1.35, "inability": -1.4, "incapable": -1.3,
    "tries": -0.60, "trying": -0.58, "attempts": -0.48,
    "pretends": -0.85, "supposed": -0.6, "wishes": -0.63,
    "could have been": -0.78, "might have been": -0.67,
    "should have been": -0.83, "would have been": -0.70,
    "not enough": -1.4, "never enough": -1.4, "not nearly enough": -1.55,
    "if only": -1.08, "no amount of": -0.55, "refuses": -0.61,
}

_POS_ENDINGS = (
    "ableness", "ingly", "fulness", "ousness", "iveness", "iness", "ness",
    "ments", "ment", "ation", "ities", "ity", "lessly", "edly", "ly",
    "iest", "ier", "est", "ing", "ied", "ies", "ed", "es", "s",
)
_DERIVE_SKIP = set("""
    news series species politics economics movies moving actor actress pictures
    business address dresses different generally singly simply really actually
    mostly usually nearly barely hardly merely certainly necessarily specifically
    things tickets minutes hours reviews characters character directed directing
    directed director works worker work worked due darkly courage reality reality
    liability commentary viewers tricks lives leavings ending beginning starring
    lies died raised based seemingly points heights goodly tires wars tears
    flattery maturity identity identity identity partly company society friendly
    worldly ghostly deadly timely early lovely likely unlikely nightly deadly
    trial trying besting reported reports story stories movie starring frankly
    keeping looking watching interestingly book books books doing thinking chilly
    """.split())


def _lexical(w):
    if w in _WORDS:
        return _WORDS[w]
    if len(w) < 4 or w in _DERIVE_SKIP:
        return 0.0
    for suffix in _POS_ENDINGS:
        if not w.endswith(suffix) or len(w) - len(suffix) < 3:
            continue
        base = w[:-len(suffix)]
        if suffix in ("iness", "iest", "ier", "ied", "ies"):
            bases = (base + "y", base, base + "ie")
        elif suffix in ("ly", "ity", "ation"):
            bases = (base, base + "e", base + "y", base + "le")
        elif suffix == "iveness":
            bases = (base + "ive",)
        elif suffix == "ousness":
            bases = (base + "ous",)
        elif suffix == "fulness":
            bases = (base + "ful",)
        elif suffix == "lessly":
            bases = (base + "less",)
        elif suffix == "ableness":
            bases = (base + "able",)
        elif suffix in ("ed", "ing", "ingly", "er", "est", "edly"):
            bases = (base, base + "e", base[:-1] if len(base) > 2 and base[-1] == base[-2] else "")
        else:
            bases = (base, base + "e")
        for root in bases:
            if root in _WORDS and _WORDS[root]:
                return _WORDS[root] * (0.84 if suffix in ("ly", "ingly", "edly") else 0.94)
    if w.startswith("un") and len(w) >= 7 and w[2:] in _WORDS:
        return -0.81 * _WORDS[w[2:]]
    if w.startswith("over") and len(w) >= 8 and _WORDS.get(w[4:], 0.0) > 0.4:
        return -0.8
    if w.startswith("under") and len(w) >= 9 and _WORDS.get(w[5:], 0.0) > 0.4:
        return -0.85
    return 0.0


_CONTRACTIONS = {
    "won't": "will not", "can't": "can not", "shan't": "shall not",
    "ain't": "is not", "let's": "let us", "i'm": "i am",
    "it's": "it is", "that's": "that is", "what's": "what is",
    "who's": "who is", "here's": "here is", "there's": "there is",
    "movie's": "movie", "film's": "film", "director's": "director",
    "he's": "he is", "she's": "she is", "you've": "you have",
}

_TOKEN = re.compile(r"\d+(?:\.\d+)?|[^\W\d_]+(?:'[^\W\d_]+)?|[,.!?;:()]|👍|👎|[★☆]", re.UNICODE)


def _prepare(state):
    s = unicodedata.normalize("NFKC", state).casefold()
    s = s.translate(str.maketrans({"’": "'", "‘": "'", "`": "'", "“": '"', "”": '"',
                                   "−": "-", "–": ";", "—": ";", "…": "."}))
    s = re.sub(r"\b([a-z]+)\s+n\s*'\s*t\b", r"\1n't", s)
    s = re.sub(r"\b([a-z]+)\s+n['’]t\b", r"\1n't", s)
    s = re.sub(r"\b(i|it|he|she|that|there|what|who|you|we|they)\s+'\s*(m|s|ve|re|ll|d)\b",
               r"\1'\2", s)
    s = re.sub(r"\b([a-z]+)\s*'\s*([a-z]+)\b",
               lambda m: m[1] + "'" + m[2] if m[2] in ("t", "m", "s", "ve", "re", "ll", "d") else m[0],
               s)
    s = re.sub(r"\b[a-z]+(?:'[a-z]+)\b", _expand_contraction, s)
    s = s.replace("cannot", "can not")
    s = re.sub(r"\b(?:well[- ]?worth)\b", "well worth", s)
    s = re.sub(r"(?<=\w)-(?=\w)", " ", s)
    s = re.sub(r"-{2,}", " ; ", s)
    s = re.sub(r"\bkind\s+of(?=\s+\w)", "kind of", s)
    return s


def _expand_contraction(match):
    w = match[0]
    if w in _CONTRACTIONS:
        return _CONTRACTIONS[w]
    if w.endswith("n't"):
        return w[:-3] + " not"
    for tail, expansion in (("'ve", " have"), ("'re", " are"), ("'ll", " will"), ("'d", " would")):
        if w.endswith(tail):
            return w[:-len(tail)] + expansion
    if w.endswith("'s"):
        return w[:-2]
    return w


_PREPOSED = (
    ("in", "spite", "of"), ("even", "though"), ("even", "if"), ("despite", "the", "fact", "that"),
    ("although",), ("though",), ("despite",), ("while",), ("albeit",),
    ("granted",), ("admittedly",), ("if",),
)
_SWITCH = (
    ("on", "the", "other", "hand"), ("having", "said", "that"),
    ("that", "said"), ("even", "so"), ("except", "that"),
    ("the", "trouble", "is"), ("the", "problem", "is"),
    ("the", "good", "news", "is"), ("the", "bad", "news", "is"),
    ("but",), ("however",), ("nevertheless",), ("nonetheless",), ("yet",),
)
_SUMMARY = (
    ("when", "all", "is", "said", "and", "done"), ("in", "the", "end"),
    ("all", "things", "considered"), ("all", "in", "all"), ("on", "the", "whole"),
    ("at", "the", "end", "of", "the", "day"), ("on", "balance"), ("overall",),
    ("ultimately",), ("bottom", "line"),
)
_BASELINE = (
    ("as", "opposed", "to"), ("in", "contrast", "to"), ("compared", "with"),
    ("compared", "to"), ("instead", "of"), ("rather", "than"), ("unlike",),
)
_DECOR = {"(", ")", ",", ":", ";", "!", "?", "."}
_HARD = {";", "!", "?", "."}
_LINKS = {"and", "or", "nor", "but", "yet"}
_MAIN_SUBJECT = {
    ("the", "film"), ("this", "film"), ("the", "movie"), ("this", "movie"),
    ("the", "picture"), ("this", "picture"), ("the", "documentary"),
}
_PRONOUNS = {"i", "you", "he", "she", "it", "we", "they", "one", "that", "this", "there"}
_ASSERT = {"is", "are", "am", "has", "have", "was", "were", "does", "do", "did",
           "will", "would", "can", "could", "should", "makes", "made", "seems", "feels"}
_TARGET_HEADS = {"film", "movie", "picture", "documentary", "comedy", "thriller", "screenplay",
                 "script", "direction", "acting", "dialogue", "characters", "plot", "story",
                 "performances", "ending", "jokes", "writing", "review", "cinematography",
                 "animation", "music", "remake", "sequel", "pacing", "soundtrack", "cast"}
_COMPARATIVE_WORDS = {"better", "worse", "less", "more", "rather", "greater", "funnier",
                      "stronger", "weaker", "easier", "harder", "slower", "faster", "longer",
                      "shorter", "nicer", "rarer", "duller", "smarter", "prettier"}


def _match(t, i, patterns):
    for k in patterns:
        if t[i:i + len(k)] == k:
            return k
    return ()


def _phrase(t, i):
    for key, value in _PHRASE_INDEX.get(t[i], ()):
        if t[i:i + len(key)] == key:
            return len(key), value
    return 0, 0.0


def _segments(t):
    records = []
    buf = []
    group_start = 0
    weight = 1.0
    mode = ""
    comparative = False
    cover_to = 0
    last_event = ""
    additive = False

    def flush():
        if buf:
            records.append([tuple(buf), weight])
            buf.clear()

    i = 0
    while i < len(t):
        w = t[i]
        if w in _DECOR:
            if w == "," and t[i + 1:i + 2] == ("and",) and mode == "":
                pass
            else:
                flush()
            if w == "," or w == ":":
                if mode in ("front_sub", "back_sub", "base", "aside", "connect"):
                    weight, mode = 1.0, ""
            elif w in _HARD:
                if mode not in ("summary", "contrast") or not records or i + 1 == len(t):
                    weight, mode = 1.0, ""
                else:
                    weight, mode = 1.0, ""
                if w != ";" or t[i + 1:i + 2] not in (("but",), ("however",), ("yet",)):
                    group_start = len(records)
                    additive = False
                if w != ";":
                    comparative = False
            elif w == "(":
                weight, mode = weight * 0.72, "aside"
            elif w == ")":
                weight, mode = 1.0, ""
            last_event = w
            i += 1
            continue

        if i < cover_to:
            buf.append(w)
            i += 1
            continue

        if mode in ("front_sub", "base") and len(buf) >= 3:
            is_subject = t[i:i + 2] in _MAIN_SUBJECT
            explicit_pronoun = (w in ("i", "it", "we") and i + 1 < len(t)
                                and t[i + 1] in _ASSERT
                                and t[i - 1] not in ("that", "than", "how", "as", "because", "if"))
            if is_subject or explicit_pronoun:
                flush()
                weight, mode = 1.0, ""
                comparative = False

        plen, pval = _phrase(t, i)
        if plen:
            if t[i:i + 2] in (("not", "only"), ("not", "just"), ("not", "merely"),
                               ("not", "simply"), ("more", "than")):
                additive = True
            if w in _COMPARATIVE_WORDS and "than" not in t[i:i + plen]:
                comparative = True
            cover_to = i + plen
            buf.append(w)
            i += 1
            continue

        marker = _match(t, i, _SWITCH)
        if marker == ("yet",):
            if (not buf and last_event not in _DECOR and i != 0) or (
                buf and (i == len(t) - 1 or buf[-1] in
                         ("have", "has", "had", "not", "never", "as", "another", "one"))
            ):
                marker = ()
        if marker == ("but",) and i and t[i - 1] in (
            "anything", "everything", "nothing", "all", "none", "everyone", "everybody",
            "nobody", "anybody", "anyone", "little", "help", "except", "least", "last"
        ):
            marker = ()
        if marker:
            flush()
            add = additive or t[i + len(marker):i + len(marker) + 1] == ("also",)
            if not add:
                for rec in records[group_start:]:
                    rec[1] *= 0.64
                if group_start == len(records) and records:
                    records[-1][1] *= 0.82
                weight, mode = 1.43, "contrast"
            else:
                weight, mode = 1.11, "contrast"
            additive = False
            comparative = False
            last_event = ""
            i += len(marker)
            continue

        marker = _match(t, i, _SUMMARY)
        if marker:
            flush()
            weight, mode = 1.48, "summary"
            i += len(marker)
            continue

        marker = _match(t, i, _PREPOSED)
        if marker:
            prev = t[i - 1] if i else ""
            if marker == ("if",) and (prev in ("as", "even", "only", "wonder", "wondering",
                                               "sure", "decide", "know", "doubt", "see") or
                                       t[i + 1:i + 2] in (("not",), ("anything",))):
                marker = ()
            if marker == ("while",) and prev in ("a", "the", "little", "long", "worth"):
                marker = ()
            if marker == ("though",) and prev == "as":
                marker = ()
        if marker:
            front = not buf and len(records) == group_start
            if marker == ("while",) and not front and last_event != ",":
                if not (i + 2 < len(t) and t[i + 1] in _PRONOUNS and t[i + 2] in _ASSERT):
                    marker = ()
        if marker:
            flush()
            front = len(records) == group_start
            weight, mode = (0.55 if front else 0.62), ("front_sub" if front else "back_sub")
            i += len(marker)
            continue

        marker = _match(t, i, _BASELINE)
        if not marker and w == "than" and comparative:
            marker = ("than",)
        if marker:
            flush()
            weight, mode = 0.12, "base"
            comparative = False
            i += len(marker)
            continue

        if w in ("unfortunately", "alas", "regrettably", "sadly") and not buf:
            weight = max(weight, 1.22)
            buf.append(w)
        elif w in ("fortunately", "thankfully") and not buf:
            weight = max(weight, 1.16)
            buf.append(w)
        elif w == "still" and not buf and (records or last_event in _HARD):
            if records:
                records[-1][1] *= 0.80
            weight, mode = max(weight, 1.25), "contrast"
        elif w == "and" and mode in ("base", "back_sub") and i + 2 < len(t) and (
            (t[i + 1] in _PRONOUNS and t[i + 2] in _ASSERT) or
            t[i + 1:i + 3] in _MAIN_SUBJECT
        ):
            flush()
            weight, mode = 1.0, ""
        else:
            buf.append(w)
            if w in _COMPARATIVE_WORDS or (
                len(w) > 4 and w.endswith(("ier", "er")) and _lexical(w) != 0
            ):
                comparative = True
        last_event = ""
        i += 1
    flush()
    return records


_CONCEPT_PHRASES = (
    ("is", "about"), ("are", "about"), ("story", "of"), ("tale", "of"),
    ("tale", "about"), ("film", "about"), ("movie", "about"),
    ("documentary", "about"), ("account", "of"), ("portrait", "of"),
    ("depiction", "of"), ("chronicle", "of"), ("exploration", "of"),
    ("examination", "of"), ("study", "of"), ("look", "at"),
    ("subject", "of"), ("theme", "of"), ("themes", "of"),
    ("based", "on"), ("deals", "with"), ("plays", "a"), ("played", "by"),
)
_THEME_WORDS = set("""
    poverty rich poor violent violence criminal criminals crime cruelty
    dead deadly death dying kill killer serial abusive abuse sexual
    unpleasant miserable awful horrible horrific hateful hate dumb stupidity
    depressed depressing depressing tragedy traumatic painful grief loss abuse
    empty loneliness bad evil corrupt sad unhappy fear dark kindness corrupt
    heartless terrible horrifying scary torment destructive gruesome sick
    eccentric bizarre weird compassionate fate sadistic ruthless evil
    romance happy happiness loved loves love heartbreak harrowing ugly
    damaged wicked toxic difficult difficult terrifying harsh alienating
    beautiful beloved unconventional
    """.split())

_BREAK_SCOPE = set("""
    because therefore hence whereas while although though unless despite instead
    since but however yet except whenever where when who whose whom plus
    """.split())
_SCOPE_LIGHT = set("""
    a an the as any that this those these all at its their his her my our your
    much many more less too very really even just merely only exactly quite so
    by nearly simply possibly remotely particularly especially neither nor
    seem seems seemed feel feels feeling felt appear appears look looks
    sounded sounds sound to be being become becoming been it they he she i we
    there is are was were am have has had did do does can could would will
    may might enough lot lots of well possibly perhaps actually anymore
    genuinely somewhat nothing and or away ever necessarily terribly few
    wholly little bit sense hints hints of bit almost overly so remotely
    """.split())

_POSITIVE_NOUNS = set("""
    fun laughs laugh wit humor humour intelligence cleverness charm elegance sense
    imagination energy life heart magic purpose characterization tension depth
    warmth impact insight suspense originality interest pleasure action cohesion
    coherence pacing excitement conviction imagination subtlety merit grace joy
    character style surprise freshness payoff effort weight chemistry reason
    point surprises feeling results redeeming
    """.split())
_SCOPED_POS = set("""
    fun laugh laughing interest sense energy life point payoff action
    entertainment depth passion ideas intelligence imagination subtlety
    logic tension pace reason humor humour wit humanity suspense meaning
    momentum substance grace sophistication heart animation joy freshness
    coherence originality emotion insight surprises point entertainment
    wonder warmth personality charm feeling edge timing pleasure appeal
    satisfaction good interest redemption talent merit characters dialogue
    chemistry empathy redeeming substance direction
    """.split())


def _context_value(t, i, topic_start, active_cues):
    w = t[i]
    prev = t[max(0, i - 3):i]
    next2 = t[i + 1:i + 3]
    val = _lexical(w)
    if w in ("like", "likes", "liked", "liking"):
        if w == "like" and (
            (next2 and next2[0] == "a" and any(x in ("feels", "looks", "sounds", "seems", "plays") for x in prev))
            or (not any(x in _PRONOUNS or x in ("really", "not", "to", "quite", "will", "should") for x in prev)
                and not active_cues)
            or next2[:1] == ("to",)
        ):
            return 0.0
        val = 1.36 if w != "like" else 1.30
    elif w in ("dislike", "dislikes", "disliked", "disliking"):
        val = -1.5
    elif w == "well":
        if next2 and next2[0].endswith("ed"):
            val = 0.82
        elif prev and prev[-1] in ("performed", "plays", "play", "played", "acts", "acted", "work", "works", "done", "did"):
            val = 0.6
        else:
            val = 0.0
    elif w in ("work", "works", "worked", "working"):
        if (next2[:1] in (("of",), ("for",)) and prev[-1:] in (("a",), ("the",), ("to",))) or (
                prev and prev[-1] in ("body", "whose", "own", "previous", "their", "his", "her", "at", "to", "of", "a", "the")):
            if active_cues and prev[-1:] == ("to",):
                val = 1.05
            else:
                val = 0.0
        elif w == "work" and not active_cues and not prev:
            val = 0.0
        elif w == "working" and not active_cues:
            val = 0.0
        else:
            val = 1.16
    elif w in ("badly", "poorly"):
        val = -1.16
    elif w == "bad" or w == "poor":
        if next2 and next2[0] in ("boy", "boys", "guy", "guys", "girl", "girls", "woman",
                                  "man", "men", "people", "family", "families", "neighborhood"):
            val = 0.0
        else:
            val = -1.85 if w == "bad" else -1.55
    elif w in ("good", "great"):
        val = 1.85 if w == "good" else 2.4
        if next2 and next2[0] in ("deal", "many", "distance", "length", "number"):
            val = 0.0
    elif w in ("moving", "moves", "moved"):
        if next2 and next2[0] in ("on", "along", "from", "into", "out", "away", "through",
                                  "scene", "images", "picture", "pictures"):
            val = 0.15 if next2[0] == "along" else 0.0
        elif w in ("moved", "moves") and (not next2 or next2[0] not in ("me", "you", "us", "them", "viewers")):
            val = 0.0
        else:
            val = 1.56
    elif w in ("cried", "crying", "tears", "tearjerker", "tearjerking"):
        val = 0.51 if any(x in ("me", "made", "kept", "my", "moved", "to", "i") for x in prev) else 0.0
    elif w in ("hard", "difficult", "tough"):
        if next2[:1] == ("to",) and next2[1:] in (
            ("follow",), ("believe",), ("understand",), ("finish",), ("take",), ("swallow",), ("endure",)
        ):
            val = -1.25
    elif w in ("recommendable", "recommended", "recommend", "recommending", "recommends"):
        if next2[:1] == ("for",):
            val = 0.92
        else:
            val = 2.05
    elif w in ("hate", "hates", "hated") and next2[:1] in (("to",), ("crimes",), ("crime",)):
        val = 0.0
    elif w in ("waste", "wastes", "wasted", "wasting"):
        val = -2.0
    elif w in ("problem", "problems", "flaw", "flaws", "shortcomings", "weakness", "weaknesses"):
        val = -1.0
    elif w in ("ok", "okay", "fine"):
        val = 0.42 if w != "fine" else 0.72
    elif w in ("flawed", "cliched", "clichéd"):
        val = -1.15
    elif w in ("enough", "sufficient") and active_cues:
        val = 0.81
    elif w in ("unfortunately", "alas", "regrettably", "sadly"):
        val = -0.60
    elif w in ("fortunately", "thankfully", "luckily"):
        val = 0.48
    elif w in ("interesting", "exciting", "boring") and next2[:1] == ("enough",):
        val *= 0.90
    elif w == "👍":
        val = 3.0
    elif w == "👎":
        val = -3.0

    if not val and active_cues and w in _SCOPED_POS:
        val = 1.03
    if val and topic_start >= 0 and i >= topic_start:
        if w in _THEME_WORDS:
            val *= 0.18
        elif i < topic_start + 5 and not any(x in _ASSERT for x in t[topic_start:i]):
            val *= 0.41
    if val and i + 1 < len(t) and t[i + 1] in (
        "title", "titles", "trailer", "trailers", "poster", "posters", "marketing", "publicity",
        "reputation", "advertising", "cover", "packaging"
    ):
        val *= 0.37
    if val and w in ("original", "classic") and next2[:1] in (
        ("version",), ("original",), ("one",), ("novel",), ("book",), ("series",)
    ):
        val *= 0.27
    return val


def _long_cue(t, i):
    for key in _CUE_INDEX.get(t[i], ()):
        if t[i:i + len(key)] != key:
            continue
        if key == ("little",) and i and t[i - 1] in ("a", "this", "that", "the", "some"):
            continue
        if key == ("few",) and i and t[i - 1] in ("a", "the", "this", "these", "very"):
            continue
        if key == ("missing",) and t[i + 1:i + 2] in (("person",), ("child",), ("persons",), ("children",)):
            continue
        if key == ("less",) and i and t[i - 1] in ("or", "nonetheless"):
            continue
        if key in (("no",), ("nothing",)) and t[i + 1:i + 2] in (("one",), ("body",), ("matter",)):
            continue
        return key
    return ()


def _clause(t):
    evidence = []
    cues = []
    used = set()
    topic_start = -1
    skip_mod = set()
    i = 0
    last_i = -20
    last_val = 0.0

    def close_cues():
        for start, stop, key in cues:
            if start not in used:
                k = " ".join(key)
                v = _CUE_FALLBACK.get(k, _CUE_FALLBACK.get(key[0], 0.0))
                if v:
                    evidence.append((start, v))
                    used.add(start)
        cues.clear()

    while i < len(t):
        w = t[i]
        if w in _BREAK_SCOPE:
            close_cues()
            if w != "who":
                topic_start = -1
        if w in _TARGET_HEADS and i + 1 < len(t) and t[i + 1] in _ASSERT:
            topic_start = -1
        theme = _match(t, i, _CONCEPT_PHRASES)
        if theme:
            topic_start = i + len(theme)

        n, val = _phrase(t, i)
        if not n:
            cue = _long_cue(t, i)
            if cue:
                cues.append((i, i + len(cue), cue))
                i += len(cue)
                continue
        else:
            if not val:
                if t[i:i + n] in _DEGREE_PHRASES or t[i:i + n] in (
                    ("nothing", "short", "of"), ("nothing", "less", "than"),
                    ("more", "than", "just"), ("nothing", "but"),
                ):
                    pass
                else:
                    skip_mod.update(range(i, i + n))
                if t[i:i + n] in (("not", "only"), ("not", "just"), ("not", "merely")):
                    close_cues()
                i += n
                continue

        relevant = []
        restore = []
        for c in cues:
            start, stop, key = c
            gap = t[stop:i]
            limit = 8 if start not in used else 13
            if len(gap) > limit:
                v = _CUE_FALLBACK.get(" ".join(key), _CUE_FALLBACK.get(key[0], 0.0))
                if v and start not in used:
                    evidence.append((start, v))
                    used.add(start)
                continue
            restore.append(c)
            if any(x in _BREAK_SCOPE for x in gap):
                continue
            if start in used:
                after = t[last_i + 1:i]
                continuation = any(x in ("or", "nor") for x in after) or (
                    "and" in after and not any(x in _ASSERT or x in _PRONOUNS for x in after)
                    and len(after) <= 3
                )
                if not continuation:
                    continue
                if any(x in _PRONOUNS for x in after) and any(x in _ASSERT for x in after):
                    continue
                if key in (("less",), ("more",)) and "and" in after:
                    continue
            elif any(gap[j] in _PRONOUNS and gap[j + 1] in _ASSERT for j in range(len(gap) - 1)):
                if key not in (("if", "only"), ("no", "amount", "of")) and not (
                    ("that" in gap or "it" in gap) and key[0] in ("not", "never")
                ):
                    continue
            elif len(gap) >= 4 and key in (("no",), ("without",), ("less",), ("little",), ("few",)):
                if not any(x in _SCOPE_LIGHT for x in gap[:2]):
                    continue
            if key == ("less",) and gap and gap[0] == "than":
                if any(x in ("minute", "minutes", "hour", "hours", "days", "percent") or x[0].isdigit() for x in gap):
                    continue
            relevant.append(c)
        cues = restore

        if not n:
            val = _context_value(t, i, topic_start, relevant)
            n = 1
            if w in _INTENSITY and i + 1 < len(t) and _lexical(t[i + 1]) and w.endswith(("ly", "y")):
                val = 0.0
        if not val:
            i += n
            continue

        original_val = val
        modifier = 1.0
        nearest = max(0, i - 4)
        consumed = set()
        for size in (4, 3, 2):
            for start in range(nearest, i - size + 1):
                stop = start + size
                key = t[start:stop]
                if key in _DEGREE_PHRASES and not any(j in consumed for j in range(start, stop)):
                    if stop == i or all(x in _SCOPE_LIGHT or x in _INTENSITY for x in t[stop:i]):
                        modifier *= _DEGREE_PHRASES[key]
                        consumed.update(range(start, stop))
        for j in range(max(0, i - 3), i):
            if j in consumed or j in skip_mod:
                continue
            if j + 1 == i or all(x in _INTENSITY or x in ("a", "an", "much", "more", "less", "of") for x in t[j + 1:i]):
                modifier *= _INTENSITY.get(t[j], 1.0)
        modifier = max(0.42, min(2.1, modifier))
        val *= modifier

        if i and t[i - 1] == "too":
            if val < 0:
                val *= 1.28
            elif t[i + n:i + n + 1] != ("to",):
                val *= -0.67
            elif t[i + n + 1:i + n + 2] in (("miss",), ("resist",), ("ignore",), ("dislike",)):
                val *= 1.24
            else:
                val *= -0.64
        elif i and t[i - 1] == "overly":
            val = -max(0.70, abs(val)) * 0.93

        if w in ("slow", "long", "short", "loud", "dark", "serious", "familiar", "soft", "sentimental",
                 "cute", "slick", "subtle", "busy", "safe", "simple", "complicated", "obvious") and \
                i and t[i - 1] in ("too", "overly") and abs(val) < 0.85:
            val = -1.07

        for start, stop, key in relevant:
            if start in used and "and" in t[last_i + 1:i] and "or" not in t[last_i + 1:i]:
                if original_val < 0 and last_val < 0 and i - last_i >= 2:
                    continue
            influence = _CUES[key]
            if key == ("no", "amount", "of"):
                influence = -0.64
            if key in (("less",), ("less", "than"), ("tries", "to"), ("could", "have", "been"),
                       ("should", "have", "been"), ("would", "have", "been"),
                       ("supposed", "to", "be"), ("wants", "to", "be")) and val < 0:
                if key[:1] == ("less",):
                    influence = -0.59
                else:
                    influence = 0.52
            elif val < 0:
                influence *= 0.78
                if w in ("perfect", "great", "masterpiece"):
                    influence *= 0.87
            else:
                if key in (("not", "quite"), ("far", "from")) and w in ("perfect", "masterpiece", "great", "brilliant", "best"):
                    influence *= 0.55
            val *= influence
            used.add(start)

        end = i + n
        if end + 1 < len(t) and t[end:end + 2] in (("at", "best"), ("in", "spots"), ("at", "times")):
            val *= 0.68 if val > 0 else 0.82
        if t[end:end + 2] in (("enough", "to"), ("enough", "for")) and val > 0:
            val *= 1.11
        if i > 1 and t[i - 2:i] in (("only", "occasionally"), ("only", "marginally")):
            val *= 0.78

        if abs(val) >= 0.095:
            evidence.append((i, val))
            last_i, last_val = end - 1, val
        i = end
    close_cues()
    evidence.sort()
    return evidence


def _rating(s):
    grade = re.search(r"\b(?:grade|rating|rated|score)\s*[:=]?\s*([a-f])([+-]?)(?=\s|[.!?,;]|$)", s)
    if grade:
        letter, sign = grade.groups()
        if letter != "a" or sign or s[grade.end():].lstrip().startswith((".", "!", "?", ",")) or not s[grade.end():].strip():
            score = {"a": 3.8, "b": 2.7, "c": -0.9, "d": -3.0, "e": -3.7, "f": -4.0}[letter]
            return score + (0.42 if sign == "+" else -0.42 if sign == "-" else 0.0)
    nums = re.findall(r"(?<![\w.])(\d+(?:\.\d+)?)\s*(?:stars?\s*)?(?:/|out of)\s*(4|5|10|100)(?![\w.])", s)
    if nums:
        marks = [float(a) / int(b) for a, b in nums if 0 <= float(a) <= int(b)]
        if marks:
            p = marks[-1]
            return (p - 0.59) * 9.5
    stars = re.search(r"[★☆]{2,5}", s)
    if stars:
        mark = stars[0]
        return (mark.count("★") / max(4, len(mark)) - 0.59) * 7.0
    explicit = re.search(r"\b(?:rating|rated|score)\s*[:=]?\s*(\d(?:\.\d+)?)\s+stars?\b", s)
    if explicit and float(explicit[1]) <= 5.0:
        return (float(explicit[1]) / 5.0 - 0.53) * 8.0
    return 0.0


def _weak_judgment(s, t):
    if re.search(r"\b(?:not|never|hardly)\b.{0,24}\b(?:enough|care|careful|buy it|get it)\b", s):
        return -1.0
    if re.search(r"\b(?:why|what reason)\b.{0,45}\b(?:bother|make this|was this made|would anyone watch)\b", s):
        return -0.9
    if re.search(r"\b(?:who cares|who asked for|this again|if you must|if you insist|at your own risk|for diehards only)\b", s):
        return -0.9
    if re.search(r"\b(?:wait for (?:video|dvd|streaming|cable)|check your watch|look at my watch|looked at my watch|more of the same)\b", s):
        return -0.9
    if re.search(r"\b(?:give (?:it|this) a chance|check (?:it|this) out|go and see|catch it while you can|go see|worth a|something special)\b", s):
        return 0.9
    if re.search(r"\b(?:makes (?:me|you|us) (?:feel|think|laugh)|you will (?:laugh|cry|cheer)|keeps (?:me|you|us) guessing)\b", s):
        return 0.8
    if re.search(r"\b(?:nothing to see|nothing happens|going through the motions|sitting through|just sits there|has no business|little to offer|much ado about nothing)\b", s):
        return -0.9
    if re.search(r"\b(?:so what|who knew|what were they thinking|what on earth|what a shame)\b", s):
        return -0.7
    if re.search(r"\b(?:seems like forever|felt like hours|two hours of my life|wish i had not|want my .{0,15} back)\b", s):
        return -0.9
    if any(x in t for x in ("if", "could", "would")) and any(x in t for x in ("only", "instead", "should", "wish", "enough")):
        return -0.35
    if any(x in t for x in ("cheer", "cheering", "enjoy", "enjoyed", "applaud", "gift", "hoo", "hurray")):
        return 0.65
    return 0.0


def predict(state) -> dict:
    s = _prepare(state)
    t = tuple(_TOKEN.findall(s))
    segments = _segments(t)
    positives = 0.0
    negatives = 0.0
    votes = []
    count = len(segments)
    for j, (tokens, weight) in enumerate(segments):
        items = _clause(tokens)
        if not items:
            continue
        p = sum(v for _, v in items if v > 0)
        n = -sum(v for _, v in items if v < 0)
        if p > 3.0:
            p = 3.0 + (p - 3.0) * 0.68
        if n > 3.0:
            n = 3.0 + (n - 3.0) * 0.68
        weight *= 0.93 + 0.14 * (j + 1) / max(count, 1)
        if j == 0 and len(items) == 1 and tokens[:1] in (("yes",), ("no",)):
            weight *= 0.94
        positives += p * weight
        negatives += n * weight
        for index, v in items:
            votes.append((abs(v * weight), j, index, v))
    rating = _rating(s)
    score = positives - negatives + rating
    if abs(score) < 0.72:
        score += _weak_judgment(s, t) * (0.60 if votes else 1.0)
    if abs(score) < 0.12 and votes:
        strongest = max(votes, key=lambda e: (round(e[0], 1), e[1], e[2]))
        score = 0.12 if strongest[3] > 0 else -0.12
    return {"answer": "negative" if score < 0 else "positive"}