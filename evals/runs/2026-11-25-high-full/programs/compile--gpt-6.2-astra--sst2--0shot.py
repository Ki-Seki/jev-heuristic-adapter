import re
import unicodedata
import math


def _text(x):
    if isinstance(x, str):
        return x
    if isinstance(x, dict):
        keys = {str(k).lower().replace("_", " "): k for k in x}
        for k in ("text", "sentence", "review text", "review", "movie review", "snippet",
                  "quote", "quotation", "passage", "content", "input text", "input",
                  "utterance", "excerpt", "statement", "phrase", "document", "comment"):
            if k in keys:
                s = _text(x[keys[k]])
                if s.strip():
                    return s
        return " ".join(_text(v) for k, v in x.items()
                        if str(k).lower() not in ("id", "idx", "index", "label", "split", "source"))
    if isinstance(x, (list, tuple)):
        return " ".join(_text(v) for v in x)
    return ""


def _normalize(s):
    s = s.lower().replace("’", "'").replace("‘", "'").replace("`", "'")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("&amp;", " and ").replace("&lt;", "<").replace("&gt;", ">")
    s = s.replace("&quot;", '"').replace("&#39;", "'").replace("&apos;", "'")
    s = re.sub(r"<br\s*/?>", ". ", s)
    s = re.sub(r"</?[a-z][^>]*>", " ", s)
    s = re.sub(r"[-\u2010\u2011]", " ", s)
    s = re.sub(r"[\u2012\u2013\u2014]", " , ", s)
    s = s.replace("...", " , ").replace("…", " , ")
    s = re.sub(r"\s+n\s*'\s*t\b", "n't", s)
    s = re.sub(r"([a-z])\s*'\s*(s|m|re|ll|ve|d|t)\b", r"\1'\2", s)
    for a, b in (("can't", "cannot"), ("won't", "will not"), ("ain't", "is not"),
                 ("shan't", "shall not"), ("n't", " not"), ("'ll", " will"),
                 ("'re", " are"), ("'ve", " have"), ("'m", " am"), ("'d", " would")):
        s = s.replace(a, b)
    s = re.sub(r"\b(dont|isnt|arent|wasnt|werent|didnt|doesnt|hasnt|havent|hadnt|couldnt|wouldnt|shouldnt|wont|cant)\b",
               lambda m: {"dont":"do", "isnt":"is", "arent":"are", "wasnt":"was", "werent":"were",
                          "didnt":"did", "doesnt":"does", "hasnt":"has", "havent":"have", "hadnt":"had",
                          "couldnt":"could", "wouldnt":"would", "shouldnt":"should", "wont":"will", "cant":"can"}[m[0]] + " not", s)
    s = s.replace("can not", "cannot").replace("could of been", "could have been")
    s = s.replace("film maker", "filmmaker").replace("movie maker", "moviemaker")
    return s


_WORD = {}


def _words(n, s):
    for w in s.split():
        _WORD[w] = n


_words(3.9, """
masterpiece masterwork tourdeforce classic perfection flawless impeccable superlative
magnificent magnificent magisterial extraordinary exceptional exquisite superb supreme
sublime outstanding astonishing astounding breathtaking phenomenal spectacular
brilliant magnificent marvelous marvellous wonderful terrific fantastic excellent
amazing incredible awesome unforgettable incomparable unparalleled unrivaled
unrivalled unmissable unmissable transcendent transcendental triumphant triumph
revelation revelatory landmark groundbreaking genius bravura virtuoso virtuosic
stupendous sensational splendid tremendous electrifying exhilarating riveting enthralling
mesmerizing mesmerising spellbinding captivating entrancing spellbound knockout
masterful masterly masterfully dazzling dazzlingly incandescent luminous resplendent
hilarious uproarious sidesplitting riotous priceless irresistible irresistible
exhilaration exhilaratingly enthralled enthralls
""")
_words(2.7, """
great best better fine finest good enjoyable entertaining delightful delight delights
delighted delightful delicious deliciously delectable satisfying inspired inspiring
inspirational inventive invention imaginative imagination innovative inventive ingenious ingenuity
creative creativity original originality refreshing refreshed fresh funny fun funnier funniest
amusing amusement amused witty wittier wittiest wit humorous humor humour laugh laughs
charming charmer charms charm charismatic charisma likable likeable lovable loveable
endearing engaging engrossing absorbing involving immersive fascinating fascination
intriguing compelling persuasive convincing believable credible authentic authenticity
heartfelt heartwarming heartening heartwrenching heartrending heartbreaking affecting poignant
poignancy moving touching tender tenderness insightful insight perceptive astute thoughtful
intelligent intelligence smart savvy shrewd sophisticated sophistication elegant elegance
graceful grace gracious beautiful beauty lovely gorgeous sumptuous lush lushly sumptuous
stylish dazzling handsome picturesque painterly stunning striking ravishing luscious
lyrical lyricism poetic poetry evocative expressive atmospheric haunting hypnotic
thrilling thrills exciting excitement exhilarating suspenseful tension taut tense gripping
powerful powerhouse potent profound profundity meaningful resonant resonance resonating
rewarding worthwhile worthy admirable admired admirable admirable admirable admiration
accomplished skillful skilful skilled adept assured confident polished slick
effective effectiveness excellent impressive impress impressed shines shining
talented talent versatile gifted stellar solid remarkable memorable indelible
distinctive unique unusual ambitious ambition daring audacious audacity bold courageous
honest honesty sincere sincerity genuine humane humanity humanistic compassionate compassion
sensitive sensitivity nuanced subtle subtlety understated restrained restraint delicate delicacy
deep depth layered complex complexity rich richness textured texture robust
alive lively invigorating energetic energy exuberant exuberance spirited buoyant effervescent
vibrant vitality zest zesty verve flair panache gusto infectious joyous joyful joy
sweet sweetness warm warmth affectionate affection romantic sensual sexy seductive
playful playful breezy brisk briskly nimble sprightly sparkling sparkles sparkle
colorful colourful vivid vividly vibrant dynamic kinetic rousing rollicking rambunctious
rousing resonant stirring uplifting uplift exhilarates entices enchanting enchanted enchantment
unpredictable unexpected surprising surprise surprises satisfy pleases pleased pleasing
pleasurable pleasure pleasures appealing appeal attractive alluring winsome winning winner
commendable praiseworthy phenomenal engagingly captivatingly approachable accessible
entertains entertains entertain entertainments entertainment recommend recommended
recommendable recommendation applaud applause kudos bravo hooray gem gems treasure treat
keeper wonder wonders wonderful magic magical bewitching entranced accomplished assured
accomplishment achievement success successful succeeds triumphs excel excels excels
courage audacity fearlessness fearless gutsy gutsiness absorbing inimitable hilarious
adorable awesome badass exquisite luscious lusciousness enchanting beguiling seductive
mesmerizes crackling crackles exuberantly masterstroke standout standout standouts
showstopper showstopping powerhouse captivating crowdpleaser
""")
_words(1.4, """
nice neat interesting interest interested watchable decent passable agreeable pleasant
pleasantry cozy comforting comfort comfortable cheery cheerful upbeat optimistic optimism
hopeful hope sentiment emotional emotion feelings feeling humanity humanistic
engross entertains diversion diversionary diverting enjoyable
engages involving immerse immersed attentive attention merits merit plus asset
able capable competent professional efficient economical economical
craft crafted craftsmanship artistry artful artistic artistry
inventiveness directionality precision precise meticulous detailed ambitious eccentric
unconventional offbeat quirky idiosyncratic oddball eccentricity irreverent irreverence
spunky spunk mischievous mischief impish sly wry dry satirical satiric satire blackly
provocative provoking thoughtful arresting challenging challenging uncompromising unflinching
fearless fearless frank candid edgy daring risky risk subversive anarchic irreverent 
unsettling disturbing harrowing chilling creepy spooky scary unnerving scary eerie
gritty raw visceral visceral jolting shocking intense intensity haunting mournful elegiac
bittersweet bittersweet melancholy wistful nostalgia nostalgic sad poignant sobering
romance intimacy intimate personal perceptible credible plausible realistic realism
natural naturalistic spontaneous unaffected unassuming unpretentious unassuming simple
modest modesty lowkey straightforward easy relaxed relaxing leisurely languid mellow
deliberate measured quietly assured robust hearty substantial substance substantial
important importance relevant timely necessary essential singular special rare ambitious
clever cleverness crafty deft dexterous agile fluid smooth seamless slick stylish
cool hip saucy saucy cheeky cute cuddly jaunty sunny lighthearted lightness
laughing chuckles chuckle giggle giggles hilarity laughter smiling smile grins grin
enjoy enjoyed enjoyment fond favorite favourite favorites favourites memorable
reward rewards worthwhile engrossing alluring enliven enlivens elevate elevates
flourish flourishes flair effusive ebullient feisty perky bouncy bubbly
splendor splendour splendiferous elegance dainty fanciful whimsical whimsy
aplomb finesse care careful precision economy assuredness
affinity enthusiasm enthusiasm enthusiastic conviction integrity dignity respectful
heart soul brains heartstrings resonance gravitas credibility
insights revelations discoveries discoveries bravery humanity affection
sensibility disarming humorous warmth goodhearted empathetic empathy sympathetic
rivets magnetism magnetic appealingly ideal perfect distinguished superior
promise promising potential worthy works succeeds praise liked appreciation
bonus refreshing satisfactions satisfied uplifting buoyancy beguiles
punch punchy kick kicks blast romp hoot riot delightfully gleeful glee
tasty potently pungent razor acerbic droll drollery deadpan sardonic zing zingers
funkiest funky nifty snappy snazzy sassy spiffy nifty fab fabulous
invent lively illuminating illuminates enlightening educational informative absorbing
absorbs fleshed resonated penetrates absorbing sumptuous alluring fondness
surpasses outdoes outshines deserves earned deserving endures enduring
revel revels relish relish feast celebration celebrates embrace embraces
watchability accomplished accomplished valentine homage hypnotizes
""")
_words(3.1, """
clever delightful intelligent deft perfect deftly satisfying satisfying luminous delicious
irresistible triumphantly electrifies charmingly heartfelt impressive masterful 
accomplished superior fabulous joyous stellar inspired remarkable exemplary topnotch magnificent
perfectly indelibly wondrous sumptuous virtuosity dazzling masterfully laudable exquisite
addictive engrosses transfixing transporting transporting transcends fascinating enthralls
""")
_words(0.55, """
love loved heart romantic drama comedy adventure adventures mystery suspense
action humanity family friendship friends life human tale music colorful fairy
explore exploration portrait examines portrays beautifully inventive
earnest earnestness sentimental sentiment nostalgia emotions meditative contemplative
serious seriousness weighty quiet gentleness gentle respect earnest conventional
accessible colorful slick weird bizarre strange absurd outrageous overblown baroque
unabashed unapologetic unabashedly documentary intimate classical minimalist 
curiously sly subtlety slow unfolding cerebral ambitious stylish modest
promises attempts examines playful unpredictability eccentric sophisticated
crafts lends offers brings welcome contribution tribute
fear terrifying frightening tears cry tearful melancholy painful painful sorrow sadness
intensity darkness dark grim disturbing brutal brutality uncompromising gritty violent
audience laughs laugh sweet funnily lovers loved devotion
tragedy tragic troubled disturbing bizarre moody mood evocative handsome
plausibly lovingly carefully affectionately tenderness timely
""")
_words(-3.95, """
terrible horrible awful atrocious abysmal appalling execrable dreadful horrible horrid
horrendous disastrous disaster catastrophe catastrophic travesty fiasco debacle
misfire turkey stinker dud flop failure disappointment disappointing
unwatchable unbearable intolerable insufferable excruciating agonizing painful
torture torturous tortuous interminable interminably interminability
wretched wretchedness miserable atrociously pathetic pitiful contemptible
despicable odious loathsome hateful repulsive repugnant revolting disgusting disgusting
abhorrent abominable detestable detest loathe loathed repellent vile offensive
offensively insulting insult insults affront insulting inexcusable unforgivable
horrifically atrocious inept ineptitude incompetent incompetence amateurish
embarrassing embarrassment embarrassed shameful laughable risible ridiculous ludicrous
preposterous asinine idiotic idiocy imbecilic moronic stupid stupidity dumb dumbest
brainless witless mindless boneheaded lame lamest lamer
worthless pointless purposeless useless worthless hopeless hopelessly lifeless soulless
heartless artless joyless charmless mirthless humorless humourless laughless
uninspired uninspiring unoriginal unfunny uninteresting unengaging unappealing
insipid vapid inane banal banality banalities trite hackneyed hackwork hackneyed
boring bored boredom tedious tedium tiresome dreary dreariness drab dull dullest
unbearably atrociously painfully excruciatingly mindnumbing numbing soporific
yawn yawner snooze snoozer snoozefest snore bore bores snoozefest
worst worse lousy crappy crap crummy rotten trash garbage rubbish junk
sucks sucked suck stinks stank stunk stink stinkbomb blows bombed
mess messes muddle messiness shambles mishmash hodgepodge drivel dreck schlock
tripe twaddle dross sludge swill bilge hogwash dreariness rubbish slop
cretinous puerile repugnance embarrassing insufferably
""")
_words(-2.55, """
bad poor poorly weak weaker weakest weakness weaknesses inferior secondrate mediocre
mediocrity subpar substandard lacking lacks lacked lack fails failed failing fail
failures unsuccessfully unsuccessful falters faltering stumbles stumbles collapses
squanders squander wasted wastes waste wasted wasting squandered squander
miscast miscasting misbegotten misguided misjudged miscalculation miscalculated misconceived
illconceived misstep missteps mismanaged botched bungled bungle flubbed mishandled
mistake mistakes error errors flawed flaws flaw faults fault shortcomings shortcoming
disappoint disappoints disappointed underwhelming underwhelmed letdown frustrating
frustration frustrated aggravating exasperating aggravation irritating irritant irritation
irritated irritates annoying annoyance annoyed annoys grating grates gratingly
tires tired tiring exhausting exhausted stale staleness musty shopworn threadbare
corny cornball hokey hokum cheesy cheesiness cheeseball tacky tawdry trashy kitschy
cliched cliche cliches rehashed recycled retread ripoff knockoff derivative familiar
formula formulaic predictable predictability obvious transparent telegraphed unimaginative
unimaginative uninventive routine generic standard stock stereotyped stereotypes stereotype
stereotypical caricature caricatures contrived contrivance contrivances forced artificial
phony phoney fake false falseness implausible implausibility implausibly improbable
unbelievable unconvincing inauthentic unrealistic unpersuasive unmotivated
inconsistent incoherent incoherence incomprehensible incomprehensibility incomprehensibly
illogical logicless confusing convoluted muddled murky messy jumbled disjointed
chaotic scattershot unfocused unfocussed aimless meandering meanders rambling rambles
ambling sluggish lumbering lethargic inert inertia static plodding plods drags dragged
drag dragging lagging slowest ponderous ponderously leaden heavy sluggishly dullness
flat flatness bland blandness flavorless tasteless colorless colourless pallid pale
listless lackluster lacklustre tepid lukewarm limp flabby flaccid soggy stodgy
stiff stilted wooden cardboard lifeless stagy stagey creaky awkward awkwardness
clumsy clumsiness clunky clunkiness clunker clunks hamfisted hammy ham copout
sloppy sloppiness careless lazy laziness perfunctory pedestrian prosaic unimaginative
overwrought overworked overlong overlength overblown overdone overdone overkill
overstuffed overburdened overloaded overcomplicated overcomplicates overplotted
overwritten overwriting overdirected overbearing overplays overplayed overplaying overacted
overacting oversentimental overearnest overwrought hyperactive frantic frenzied shrill
hysterics hysteria noisy noise noisome loud deafening chaotic bombast bombastic
bloated bloat bloats excessive excess excesses indulgent indulgence gratuitous gratuitously
mawkish maudlin saccharine sappy schmaltz schmaltzy syrupy cloying sentimentality
weepie manipulative manipulation melodramatic melodrama melodramatics histrionic histrionics
pretentious pretension pretensions portentous pompous grandiose smug smugness smarmy
smugly condescending condescension patronizing patronising pandering panders panders
preachy preachiness sermonizes didactic moralizing heavyhanded hamhanded
shallow shallowness superficial superficiality glib glibness hollow emptiness empty
vacuous meaningless forgettable disposable forgettability unmemorable inconsequential
insubstantial slightness weightless lightweight inconsequential frivolous trivial
simplistic oversimplified reductive childish juvenile sophomoric adolescent immature
vulgar vulgarity crude crass crassness coarse gross tasteless tastelessness lewd
exploitative exploitation exploitive exploitatively voyeuristic prurient sleazy sordid
sexist misogynist misogynistic racist bigoted offensive stereotypes homophobic
cynical cynicism mean meanspirited nasty nastiness cruel ugly ugliness nihilistic
depressing bleak downbeat dour sour sourness unpleasant disagreeable offputting
unlikable unlikeable unsympathetic unsatisfying unsatisfied unfulfilling unfulfilled
uncomfortable discomfort disconcerting disjointed soured tiresomeness bleakness grimness
rushed hurried sketchy sketchiness underwritten underdeveloped undeveloped undercooked
unfocused halfhearted halfbaked halfassed jarring choppy uneven unevenness patchy
unnecessary needless unnecessarily needlessly dispensable pointless irrelevant irrelevance
derail derails undermines undermined detracts detract diminishes hampers hobbled hampered
bogged bogs marred mars saddled burdened plagued suffering suffers suffers burden
problem problems problematic trouble troublesome unfortunate unfortunately alas pity shame
desperate desperately desperation strained straining laborious labored laboured laboring
labours belabored belaboured unappealing charmless uncharismatic unremarkable
unsurprising uninvolving uninvolved aloof distancing detached coldness coldly
tediously drearily woeful woefully dismal dismally somber sluggishly weakly badly
misogyny unintentional unintentionally unintelligible impenetrable baffling bafflement
annoy disinterest disinterested apathetic apathy distracted distracting distraction
disappointingly depressingly maddening maddeningly infuriating infuriatingly
punishing punishingly queasy squander embarrassment fiascos
groaner groan groans groaning wince wincing cringe cringeworthy cringing winces
obnoxious obnoxiously irritatingly irritating tiresomely tiresome torturously hopelessness
misses misfires misfiring flatlined flatlines fizzles fizzled fizz outstays overstays
pales pales pales ripoffs copycat derivative strained tediously
""")
_words(-1.25, """
mixed uneven unevenly flaws unfortunate alas dubious suspect questionable
ordinary unexceptional commonplace conventional unexceptional average unexciting
overrated overrated underratedly hyperbole hype hyped contrivances routine
repetitive repeats repeating redundant repetition repetitious repetitiveness rehash
retelling remake reworking rehashes recycled watered diluted imitation imitates
imitative mimic gimmick gimmicks gimmicky gimmickry gimmickiness gimmicky
filler formula formulas byproduct commercial product calculated calculating manufactured
synthetic mechanical mechanically rote mechanical gimmicky tricks gloss glossy glitzy
flashy showy ostentatious strident flashy frenetic cluttered clutter noisy laboured
anemic anaemic wan meek timid tame tentative blandly thin thinnest sketchily
flimsy slight minor negligible smallish barely limited limits limitation limitations
miss missing lost loses losing loss miss forget forgets forgotten forgettable
short shrift struggles struggle struggled struggling tries trying attempt attempts
instead despite although lackluster stretches stretch excessive crowded scatterbrained
fluff fluffy fluffiness cotton candy schmaltzy sap soap soapy treacle treacly
melancholic grim bleak gruesome grisly gore gory disgusting grimy brutalized bleakly
gruesomeness grotesque lurid luridly unsettling unpleasantness poky pokey
difficult difficulty hard hardship hollowly exhausted weariness weary wearisome stale
overly overmuch tires tiresomely monotonous monotony repetitively interminably
suffer suffering headache headaches nauseating sickening sick offensiveness
embarrass embarrasses embarrassment baffled bewildering confusing confused confusion
inarticulate unfinished unresolved unanswered disconnected contrived implausibilities
abrasive jaded cynically dated outdated anachronistic antiquated mustiness warmed
conspicuous lack pretends pretending pretended borrow borrows copied copying
mockery mocking ponder ponderously sketch stylistics preposterously ridiculously
stoops stunted smothers suffocates disservice disjoint abruptly unfortunate
retreads boilerplate hack hacks schtick shtick schlocky ersatz derivative reheated
shortchanges shortchanged unforgiving pitiless overwrought lachrymose
tedium overstay bomb bummer clunkers junky hokier schlockmeister
""")
_words(0, """instead despite although short hard mean heavy simple simple heavy tries trying
attempts attempt sad tears fear standard lost problems suffering product dark grim
repeats struggle ordinary familiar typical conventional brutal violent hilariousness
quiet raw weird strange odd little slow dry problematicity promise flashy grossly
unintentional forget tension tale drama comedy going film movie family friends""")
_words(0.55, """fun laughs sad quiet raw dark grim brave honest quirky laughs tale
mystery darkly absorbing explored explores compellingly acutely achingly gorgeously""")
_words(2.6, """fun laughs funny fascinating honest deft moving touching tension compellingly
deliciously resonance vividly subtlety witty genius wow dazzles wins excels endorsement
bravo goodness greatness excellence marvel marvels marvelous magnificence splendour
intelligent smarter smartest inspired crackles beautifully gorgeously fireworks
recommend highly entertainingly engagingly lovable adore adored adoration
masterpieces classics accomplished restrained effective cinematically""")
_words(-2.1, """problem problems symptomatic symptomatic ugly unworthy uninspired unsuited
ineffective unearned oblivious tasteless recoil protestations offensive insult crud cruddy
stultifying deadening unendurable unendurably stodginess lacks slogs slog slogging
sags sagging sags sag outlandish desperate conventionality familiarity nondescript
apathetic apathetically forgettable forgettably cloy unimaginably platitudes platitudinous
obnoxiousness disjointedness trashiness triteness predictably hackneyed
flounders floundering flail flails drones drone deadwood overambitious obtrusive
wrongly amateur amateurs misused wasted unlikeliest ludicrously ridiculousness
piffle dreck mess nonsensical nonsense senseless botch forgettable gratingness""")
_words(1, """intrigue curiosity admirable respect commend sincerity sweep scale feeling
truth truths affectionate strength strengths insight humanity exhilaration interestingly
texture frisson brio spice spicily engagingness earnestness prickly valiant daringly
illuminating accessible emotional heart genuine truthful perceptively worthwhile""")

# Multiword expressions are handled as individual evaluations, before single words.
_P = {}


def _phr(n, s):
    for p in s.strip().split("|"):
        t = tuple(p.strip().split())
        if t:
            _P[t] = n


_phr(4.7, """
must see|must watch|not to be missed|cannot be missed|do not miss|not to miss|do not want to miss|cannot recommend it enough|cannot recommend this enough|cannot recommend it highly enough|two thumbs up|thumbs up|standing ovation|tour de force|tour de forces|instant classic|modern classic|a masterpiece|piece of genius|work of genius|work of art|one of the best|one of the year's best|among the best|year's best|best of the year|best of its kind|best in years|best films|best movies|cinema at its best|filmmaking at its best|top notch|first rate|top drawer|top flight|world class|five stars|four stars|highest recommendation|highest praise|highly recommended|highly recommend|strongly recommend|wholeheartedly recommend|takes your breath away|took my breath away|knocks your socks off|blew me away|blown away|blew my mind|out of this world|knocks it out of the park|a home run|hits a home run|fires on all cylinders|master class|master class in|masterwork of|a triumph|a revelation|standing ovation|knockout punch|lightning in a bottle
""")
_phr(3.15, """
see it|go see|worth seeing|worth watching|well worth|worth a look|worth your time|worth the time|worth my time|worth every penny|worth the wait|worth the price|worth the trip|worth checking out|worth seeking out|worth a trip|worth a visit|worth making|worthwhile viewing|worthwhile experience|high praise|pleasant surprise|pleasantly surprised|breath of fresh air|fresh air|breathes new life|new lease on life|one of a kind|in a class by itself|something special|above average|above par|cut above|stands out|stand out|stands apart|sets it apart|rises above|rise above|rises to the occasion|transcends its|defies expectations|exceeds expectations|better than expected|better than you might expect|more than delivers|delivers the goods|comes through|gets it right|gets it just right|got it right|gets right|pulls it off|pull it off|pays off|pay off|hits the mark|hits the spot|hits all the right|hit the mark|right on target|on the mark|on the money|pitch perfect|note perfect|perfectly pitched|just right|spot on|right notes|rings true|ring true|feels real|feels authentic|comes alive|come alive|springs to life|come to life|comes to life|comes together|works beautifully|works wonders|works surprisingly well|works well|works its magic|does wonders|all the better|better for it|easy to recommend|hard to resist|hard to forget|impossible to resist|impossible to forget|impossible not to|a joy|pure joy|pure fun|pure pleasure|great fun|good fun|good time|good times|a delight|a treat|what a blast|a blast|a ball|a hoot|a riot|a scream|laugh out loud|laugh aloud|laughed out loud|laughing out loud|laugh yourself silly|laugh a minute|laugh riot|belly laughs|big laughs|many laughs|plenty of laughs|lots of laughs|had me laughing|made me laugh|makes you laugh|will make you laugh|make you smile|made me smile|touches the heart|tugs at|tug at|moves you|moved me|moved to tears|bring tears|on the edge of|edge of your seat|edge of my seat|edge of the seat|on the edge of your seat|nail biter|nail biting|heart pounding|pulse pounding|white knuckle|on the edge of my seat|kept me guessing|keeps you guessing|keeps you hooked|hooked me|held my attention|kept my attention|demands your attention|can't look away|cannot look away|cannot take your eyes|could not take my eyes|stays with you|stay with you|stuck with me|under your skin|gets under the skin|makes you think|makes us think|food for thought|thought provoking|eye opening|mind blowing|jaw dropping|heart warming|heart breaking|heart rending|gut wrenching|gut busting|rib tickling|side splitting|side splitter|feel good|feelgood movie|crowd pleasing|crowd pleaser|crowd pleasure|guilty pleasure|surprisingly good|surprisingly effective|surprisingly well|surprisingly entertaining|happy to report|good news|the real thing|real deal|just the ticket|just what the doctor ordered
""")
_phr(2.5, """
well made|well crafted|well conceived|well constructed|well executed|well directed|well acted|well written|well played|well paced|well told|well rounded|well plotted|well cast|well shot|well done|well developed|well drawn|well observed|well tuned|well worth|well earned|well chosen|well handled|well realized|beautifully shot|finely tuned|finely wrought|finely drawn|fully realized|sure handed|sure footed|sure hand|assured hand|steady hand|light touch|deft touch|knows how to|knows exactly|knows what|has a knack|right balance|balance between|labor of love|labour of love|high point|high points|highlight of|steals the show|steals every scene|steals the movie|scene stealer|star turn|star making|at the top of|at their best|at its finest|never better|in top form|in fine form|fine form|great shape|finest hour|takes flight|soars above|brings to life|breathes life|bring to life|raises the bar|finds its footing|packs a punch|packs an emotional|emotional punch|emotional wallop|emotional depth|emotional resonance|packs more|strikes a chord|hits home|punch line lands|a kick|a keeper|a winner|a natural|winning combination|winning formula|a winner|is a plus|richly rewarding|richly textured|razor sharp|razor edged|fast paced|action packed|high octane|high energy|fast moving|zips along|moves along|brisk pace|breakneck pace|seat of your pants|wickedly funny|wicked sense|sense of humor|sense of humour|great chemistry|real chemistry|good chemistry|clicks into place|work so well|works so well|works on every|a charmer|charm to spare|easy charm|has heart|has a heart|its heart in the right place|heart is in the right place|full of life|full of surprises|full of heart|full of energy|full of wit|surprisingly moving|a lot to like|much to admire|much to recommend|much to enjoy|something for everyone|for all ages|whole family|the entire family|kids will love|audiences will love|fans will love|should please|will please|a great deal of|a good deal of fun|good old fashioned|old fashioned charm|warm hearted|big hearted|good hearted|light hearted|three dimensional|larger than life|true to life|slice of life|true to its|rings of truth|ahead of its time|stands the test of time|holds up|hold up well|ages well|in a good way|for good reason|the right reasons|cannot wait|can hardly wait|not soon forget|will not soon forget|hard to beat|no small feat|no easy feat|not an easy feat|no mean feat|no small achievement|not a dull moment|never a dull|never dull|never boring|anything but dull|far from dull|anything but boring|not half bad|not bad|not too bad|not so bad|not all bad|not bad at all|could do worse|could be worse|not without its|not without charm|not without merit|not without interest|no complaints|few complaints|i loved|i love|i liked|i like this|i enjoyed|love this movie|love this film|fell in love with|you will love|will like|will enjoy|really liked|one to see|well worth seeing|worthwhile film
""")
_phr(-5, """
do not bother|do not waste|waste of time|waste of money|waste of celluloid|waste of film|waste your time|wasted my time|time i will never get back|hours of my life back|give me my money back|skip it|skip this|avoid it|avoid this|avoid at all costs|stay away from|steer clear|thumbs down|two thumbs down|zero stars|no stars|one of the worst|among the worst|year's worst|worst of the year|worst movie|worst film|all time low|new low|bottom of the barrel|scraping the bottom|piece of junk|piece of crap|piece of trash|pile of garbage|total mess|a complete mess|train wreck|trainwreck|dead on arrival|dead in the water|utter failure|a disaster|unmitigated disaster|cinematic equivalent of watching paint dry|watching paint dry|avoid like the plague|not worth watching|not worth seeing|not worth the price|not worth your time|not worth my time|do not recommend|cannot recommend|would not recommend|not recommended|no redeeming|nothing to recommend|nothing going for it|no reason to see|no reason to watch|wish i had not|so bad it hurts
""")
_phr(-3.2, """
not very good|not that good|not good|no good|little good|not much good|not very funny|not so funny|not funny|never funny|no fun|not much fun|little fun|not a lot of fun|not very interesting|not very convincing|not very compelling|not up to|not nearly as good|not nearly enough|not enough|not quite enough|not a patch on|pales in comparison|pale imitation|poor imitation|poor man's|poor man's version|a far cry from|far short|falls short|fall short|fell short|comes up short|came up short|fails to deliver|failed to deliver|does not deliver|never delivers|never quite works|does not work|does not really work|did not work|never works|nothing works|does not cut it|does not add up|does not hold together|cannot hold together|loses its way|loses its footing|loses its nerve|lost its way|gone wrong|goes wrong|go wrong|wrong turn|wrong turns|misses the mark|miss the mark|missed the mark|misses the point|lost the point|drops the ball|falls flat|fall flat|fell flat|falls apart|fall apart|comes apart|falls to pieces|rings false|ring false|rings hollow|ring hollow|falls victim|doomed from the start|never takes off|never gets off the ground|never comes to life|goes nowhere|going nowhere|go nowhere|leads nowhere|gets nowhere|nowhere to go|runs out of steam|run out of steam|loses steam|loses momentum|runs out of gas|spins its wheels|spinning its wheels|stuck in neutral|wears thin|wear thin|wears out|wear out|outstays its welcome|overstays its welcome|worn out|worn thin|beats a dead horse|drags on|goes on and on|never ending|seems endless|feels endless|too long|way too long|far too long|too much|too many|nothing new|anything new|nothing original|nothing fresh|seen it all before|seen it before|seen this before|seen before|been done before|been there done that|more of the same|same old|same tired|by the numbers|paint by numbers|connect the dots|cookie cutter|run of the mill|garden variety|nothing special|nothing remarkable|nothing memorable|nothing much|not much of a|not much to|little to recommend|little to offer|little to show|little to do|little more than|no more than|nothing more than|nothing but|merely a|poor excuse|a bad joke|unfunny comedy|minus the laughs|without the laughs|short on laughs|few laughs|too few laughs|laughs are few|few and far between|missed opportunity|missed opportunities|wasted opportunity|squandered opportunity|wasted potential|wasted talent|waste of talent|wastes the talents|deserves better|deserved better|could have been so much|should have been better|should be better|could be better|could have been better|leaves much to be desired|left much to be desired|leaves a lot to be desired|something to be desired|much to be desired|hard to sit through|hard to care|hard to swallow|hard to follow|hard to take|difficult to care|difficult to sit through|tough to sit through|cannot care|could not care less|could not wait for it to end|cannot wait for it to end|wanted it to end|fast forward|fell asleep|put me to sleep|puts you to sleep|put you to sleep|walked out|walk out|stay home|save your money|save your time|save yourself|wait for the video|wait for video|watch something else|better off|rather watch|not worth it|not worth|is not for everyone except
""")
_phr(-2.8, """
heavy handed|heavy handedness|ham handed|ham fisted|iron fist|hits you over the head|beats you over the head|beat you over the head|tone deaf|lead footed|lead foot|flat footed|wrong headed|ill advised|ill conceived|ill suited|ill fitting|ill executed|ill defined|ill considered|bad taste|poor taste|sour taste|cheap shot|cheap shots|cheap laughs|cheap thrills|low rent|bargain basement|bottom feeding|cut rate|second rate|third rate|fourth rate|second hand|half baked|half hearted|half assed|half formed|half finished|badly acted|badly written|poorly acted|poorly written|wooden acting|one note|one dimensional|two dimensional|paper thin|razor thin|wafer thin|stick figures|cardboard cutouts|cardboard characters|all over the place|all dressed up|all style|style over substance|no substance|all surface|sound and fury|empty headed|all too familiar|over the top|over the hill|way overboard|goes overboard|top heavy|self indulgent|self indulgence|self important|self importance|self conscious|self consciously|self consciousness|self satisfied|self satisfaction|self congratulatory|navel gazing|takes itself too seriously|take itself too seriously|trying too hard|tries too hard|trying hard|strains for|strains to|strained attempt|dumbed down|lowest common denominator|low brow|lowbrow humor|bad idea|bad movie|bad film|bad acting|bad writing|bad dialogue|wrong reasons|for all the wrong reasons|for no reason|for no apparent reason|makes no sense|makes little sense|make sense of|does not make sense|lack of focus|no point|what is the point|what's the point|tall order|tough sell|hard sell|an also ran|too bad|too little|too late|more is the pity|sad to say|sadly not|the sad thing|the bad news|problem is|trouble is|the only good|the best thing about|only saving grace|its only virtue|only redeeming|not saying much|isn't saying much|no great shakes|not saying a lot|that is not saying|not a compliment|backhanded compliment|damning with faint praise|sitting through|suffer through|endure this|sit through|not for a minute|stretched thin|stretches credibility|strains credibility|strains credulity|suspension of disbelief|goes through the motions|going through the motions|phones it in|phoned in|asleep at the wheel|on autopilot|on automatic pilot|no match for|not even close|does not come close|never comes close|less than stellar|leaden pace|slow going|glacial pace|takes forever|drags its feet|interminably long|beyond belief|too obvious|sorely lacking|leaves you cold|left me cold|left cold|leaves one cold|at arm's length|keeps its distance|an acquired taste|an endurance test|a chore|a drag|a bore|a slog|a mess|in a bad way|wrong with|same mistake|rubs you the wrong|rubs me the wrong|hardly worth|money back|cash grab|cash in|rip off|carbon copy|knock off|watered down|dead weight|dead end|dead ends|non stop barrage|fart jokes|toilet humor|bathroom humor|potty humor|gross out gags|below average|below par|not for me|did not like|do not like|i hate|i hated|i dislike|hated it|a headache|hour too long|stale jokes|hits a wall|out of place|out of sync|out of touch|out of ideas|without a clue|not a clue|opportunity lost|i give up|a shame|what a shame|what a pity
""")
_phr(0, """
not only|not just|not merely|not necessarily|not always|not entirely unlike|cannot deny|cannot be denied|not to mention|not least|no less|nevertheless|no matter|whether or not|no doubt|without doubt|without a doubt|no question|no wonder|little wonder|not unlike|not surprisingly|nothing if not|not so much|more often than not|no longer|as if|so called|at all|if nothing else|at least|at its best|in the face of|at best|bad guy|bad guys|bad boy|bad boys|bad girl|bad girls|bad cop|bad man|evil man|good guy|good guys|good cop|good girl|good boy|best friend|best friends|best seller|best selling|good looks|good looking|romantic comedy|love story|love stories|love affair|love triangle|in love|fall in love|falls in love|love interest|love life|heart attack|heart disease|broken heart|civil war|world war|bad luck|bad dream|bad dreams|bad news bears|good will hunting|high school|old school|real life|box office|big screen|big budget|low budget|little girl|little boy|too often|of course|no one|no longer|no doubt about|not to be confused|bad taste in his|martial arts|special effects|practical effects|social problems|problem solving|horror movie|horror film|scary movie|terrible events|worst fears|difficult subject|difficult subject matter|hard work|hard times|hard life|hard edged|difficult life|cold war|cold blooded|dead body|dead man|dead bodies|classic novel|great depression|great expectations|great britain|world of trouble|mean streets|funny thing is|funny how|no holds barred|never before|for the first time|at first|good intentions|well intentioned|well meaning|bad behavior|grim reality|musical comedy|comedy drama|black comedy|dark comedy|comedies of|one night stand|nice guy|united states
""")
_phr(1.7, """
not for everyone|not for all tastes|not for the faint of heart|not for the faint hearted|worthwhile look|good natured|tongue in cheek|twists and turns|of its own|something new|something different|turns out to be|holds its own|in its own way|in its own right|gets the job done|do the trick|does the trick|more than enough|more often than not|for the most part works|nothing wrong with|nothing wrong|no slouch|no exception|no shortage of|no lack of|in spades|a plus|cannot go wrong|does no wrong|does justice|does justice to|love letter|loving tribute|a sense of place|attention to detail|refreshing change|nice change|takes risks|takes chances|big ideas|unexpected ways|strong sense of|strong performance|strong performances|hard hitting|hard won|touch of class|breathing room|room to breathe|flesh and blood|heart and soul|full bodied|three dimensions|a human face|human condition|stays true|true to form|in full force|puts a face|small gem|takes its time|easy on the eyes|eye candy|visual feast|visually arresting|visually stunning|eye for|ear for|no easy answers|easy to see why|takes on a life|is its own reward|has its moments|had its moments|moments of grace|nice little|neat little|delivers on|leaves you wanting more|leaves you thinking|find yourself rooting|rooting for|root for|cares about|a lot going for|a lot of heart|infectious energy|fun to watch|fun watching|true original|stands on its own|like no other|apart from the pack|more than meets the eye|with a twist|lost in the best|a kick out of|cannot get enough|bound to please
""")
_phr(-1.6, """
if only|only wish|if only it|is supposed to|was supposed to|is meant to be|wants to be|wants desperately|would be nice|would have liked|intended to be|a would be|wannabe|would be more|could use|could do with|in need of|in dire need|if it were|had it been|lacks even|short of|falls prey|miss the days|over its head|bit off more|bitten off more|does not seem|never mind|aspires to|strives to|attempts to|tries to|aims to|less a movie|less a film|so much for|if you must|in spite of itself|only so much|too easy|too pat|too neat|too neat and tidy|a bit much|a bit thin|in search of|so so|hit and miss|hit or miss|starts to feel|not my cup of tea|no excuse|no substitute|at a loss|saddled with|creaks under|under the weight|in the first place|why bother|who cares|who on earth|for undemanding|undemanding viewers|for die hard fans only|fans only|straight to video|made for tv|movie of the week|would be better|was hoping|had hoped|looks suspiciously|suspiciously like|all but forgotten|vaguely reminiscent|sounds better|on paper|better movies|seen better|hard pressed|left wondering|leaves you wondering why
""")
_phr(0, "turns out to be|over the top rope|short of breath|best picture|not long before|very little girl|too much fun to|more or less|give or take|to name but|but then again")
_phr(2.3, "so bad it's good|so bad it is good|bad in a good way|too good|too good to miss|delivers what it promises|never once flags|not a false note|hard not to like|hard not to love|well enough|worthy of|do not be fooled|pure cinema|a minor miracle|not to love|could watch|could not stop laughing|could not stop watching|never lets up|never loses sight|never loses its|never falters|a force to be reckoned with")
_phr(-2.5, "all the charm of|with all the charm of|good idea for a|no one cares|nobody cares|no one seems|no one would|only intermittently|fall asleep|falling asleep|crash and burn|rather be watching|too little too late|leaves something to be desired|a tin ear|tin eared|unintended laughs|unintentional laughs|strictly for fans|not for the better|leaves out|one joke|one trick pony|action for its own sake|nearly enough|i wish i could|a total loss|i wanted to like|neither of which|as funny as a|if you insist|if you have nothing better|no cigar|mildly amusing|mildly entertaining")
_phr(1.35, "strong cast|visual style|cares enough|hard act to follow|not to say|when it works|do not let|well suited|ideal for|designed for kids|stand up and cheer|hold your interest|deserves to be seen|deserves a look|had a good|takes you inside|feels like a real|good deal more|stand the test|step up|step forward|do yourself a favor")
_phr(0, "not to say|do not let|but for|all but|would be lovers|better or worse|good or bad|good and evil|bad things|big trouble|anything goes|laugh track|laugh tracks|stand up comic|stand up comedy|not since|no such thing|not the least of|nothing less than|nothing short of|nothing like|no less than|no fewer than|not the only|hard to believe that|not long ago|too many cooks")

# Additional productive evaluative constructions, including polarity idioms.
_PATTERNS = [
    (r"\b(?:can(?:not)|could not|can not)\s+(?:really |quite )?(?:help|resist) (?:but )?", " "),
    (r"\b(?:hard|difficult|impossible) (?:for \w+ )?not to\b", " easy to "),
    (r"\b(?:never|rarely|seldom) fails? to\b", " always "),
    (r"\b(?:do|does|did|will|would|need) not (?:really )?(?:have|need) to (?:be|like|love|know|understand)\b[^.;:!?]{0,78}?\bto (?:enjoy|appreciate|admire)\b", " easy to enjoy "),
    (r"\b(?:not|never) (?:as|quite as) (funny|good|entertaining|exciting|smart|clever|compelling|interesting|effective|engaging|powerful|witty|satisfying)\b", " not very good "),
    (r"\b(?:not|never) (?:as|quite as) (bad|boring|awful|dull|tedious)\b", " not so bad "),
    (r"\b(?:not|never) (?:even )?(?:half |remotely |particularly )?(?:so |as )?good (?:as|enough)\b", " disappointing "),
    (r"\b(?:not|never) (?:nearly |quite )?(?:as |so )?(?:bad|awful) as\b", " surprisingly decent compared to "),
    (r"\b(?:there(?:'s| is) )?(?:little|not much|nothing) (?:here |in (?:it|this film|this movie) )?(?:to (?:admire|enjoy|like|love|recommend|celebrate|distinguish|offer|interest)|worth (?:watching|seeing))\b", " disappointing "),
    (r"\b(?:offers?|brings?|adds?) (?:absolutely )?nothing (?:new|to)\b", " uninspired "),
    (r"\b(?:does|did) not (?:really |quite |even )?(?:manage to |seem to )?(?:live up to|measure up to|come together|make the grade|stand up|hold up|convince|come close|hold (?:our|your|my) (?:interest|attention)|add much|come off)\b", " disappointing "),
    (r"\b(?:never|cannot|could not) (?:really |quite |even )?(?:manage[s]? to )?(?:bring[s]? (?:itself|the story) to life|come[s]? (?:to life|together|alive)|get[s]? (?:going|off the ground)|get[s]? (?:it|there|much) right|decide[s]? (?:whether|what)|make[s]? us care|find[s]? (?:its footing|a rhythm))\b", " disappointing "),
    (r"\b(?:does|did|is|was) not (?:really |quite |exactly )?(?:a (?:complete |total )?)?(?:waste of time|disaster|failure|disappointment)\b", " passable "),
    (r"\b(?:a|the) (?:complete|total|colossal|monumental|criminal) waste\b", " a disaster "),
    (r"\b(?:would|could|should|might) have (?:made|been) (?:a |an |for a |for an )?(?:(?:really|very|much|far|so much) )?(?:good|great|better|terrific|interesting|effective|decent|nice|entertaining|fun|excellent|fine|amusing|compelling|fascinating)\b", " missed opportunity "),
    (r"\b(?:would|could|should) (?:make|be) (?:a |an )?(?:much |far )?(?:better|more interesting|more entertaining)\b", " missed opportunity "),
    (r"\b(?:not|hardly|never) (?:a |an )?(?:total|complete|unmitigated) (?:success|triumph)\b", " mixed disappointment "),
    (r"\b(?:not|hardly|never) (?:a |an )?(?:total|complete|unmitigated) (?:failure|disaster|loss)\b", " passable "),
    (r"\b(?:is|was|are|were|feel|feels|seems?|becomes?) (?:just |simply )?(?:too|overly) (?:good|smart|clever|talented) (?:for|to (?:be )?(?:waste|wasted|spend))\b", " feels wasted "),
    (r"\b(?:more|a lot more|way more) (?:fun|entertaining|enjoyable|interesting|effective) than (?:it (?:has any right|ought|deserves)|you (?:would|might) expect)\b", " surprisingly entertaining "),
    (r"\b(?:does|do|did) not (?:always )?(?:quite )?(?:reach|match|achieve) (?:the|its) (?:heights|potential)\b", " falls short "),
    (r"\b(?:makes?|made) (?:you|me|us|one) (?:want to )?(?:squirm|groan|cringe|wince|yawn|vomit|puke|leave|run for)\b", " cringe "),
    (r"\b(?:makes?|made) (?:you|me|us|one) (?:want to )?(?:cheer|smile|think|care|laugh|cry)\b", " touching "),
    (r"\b(?:had|kept|has) (?:me|us|you) (?:in stitches|laughing|gripped|riveted|engrossed|on edge|hooked)\b", " riveting "),
    (r"\b(?:the|a) (?:sole|only) (?:saving grace|reason to (?:see|watch)|reason for (?:seeing|watching)|good (?:thing|part)|bright spot|redeeming (?:feature|quality))\b", " the only saving grace "),
    (r"\b(?:not|no) (?:even )?(?:\w+ ){0,3}(?:can|could) (?:save|rescue|redeem)\b", " cannot be saved by "),
    (r"\b(?:unable|fails?|failed|neglects?|struggles?|refuses?) to (?:engage|entertain|convince|impress|sustain|inspire|deliver|generate|excite|capture|convey|evoke|elicit|live up)\b", " disappointing "),
    (r"\b(?:does not|did not|never|cannot|could not) (?:quite |really |even )?(?:engage|entertain|convince|impress|inspire|deliver|resonate|excite|satisfy)\b", " disappointing "),
    (r"\b(?:instantly|soon|immediately|quickly|easily) (?:forgotten|forget)\b", " forgettable "),
    (r"\b(?:cannot|will not|could not) (?:easily |soon )?forget\b", " unforgettable "),
    (r"\b(?:will not|does not|did not|never) (?:ever )?(?:insult|bore|patronize|condescend|pander)\b", " commendable "),
    (r"\b(?:does not|never) (?:outstay|overstay|wear out)s? its welcome\b", " enjoyable "),
    (r"\b(?:does not|never|without) (?:resort(?:s|ing)? to|descend(?:s|ing)? into|devolve(?:s|ing)? into|laps(?:ing|e|es) into|becom(?:ing|es?)|get(?:ting|s)?) (?:too |overly |unduly )?(?:maudlin|sentimental|cloying|mawkish|melodramatic|preachy|sappy|boring|dull|boring|tedious|syrupy|schmaltzy|cliches?)\b", " admirable restraint "),
    (r"\b(?:not|never) (?:just |merely )?(?:another|your (?:average|typical|ordinary))\b", " distinctive "),
    (r"\b(?:better|more fun|more entertaining) than (?:most|average|the original|its predecessor|expected)\b", " superior "),
    (r"\b(?:not|hardly|scarcely|barely) (?:ever )?(?:worth|worthy of) (?:a |the |your |my )?(?:time|effort|price|money|look)\b", " waste of time "),
    (r"\b(?:does not|did not|never) (?:for (?:a|one) (?:minute|second|moment) )?(?:disappoint|let me down|let us down)\b", " satisfying "),
    (r"\b(?:i|we) (?:can|could) (?:hardly|barely) (?:keep|stay) awake\b", " boring "),
    (r"\b(?:against|despite) (?:all|the) odds\b", " surprisingly "),
    (r"\b(?:will|would|could) not (?:have )?(?:miss(?:ed)?|trade(?:d)?) (?:it|this) for\b", " unmissable "),
    (r"\b(?:far|anything) (?:from|but) (?:perfect|a masterpiece)\b", " flawed "),
    (r"\b(?:too|so) (?:bad|awful) (?:that )?(?:it is|it's) (?:funny|good|fun)\b", " guilty pleasure "),
    (r"\b(?:not|never) (?:really |quite )?sure (?:what|whether|why|how)\b", " confused "),
    (r"\b(?:you|one) (?:could|can) do (?:a lot |far |much )?worse\b", " worthwhile "),
    (r"\b(?:you|one) (?:could|can) do (?:a lot |far |much )?better\b", " disappointing "),
    (r"\b(?:i |you )?(?:cannot|could not) (?:help but )?(?:admire|fault|praise) (?:it|this|the film) (?:enough|too highly)\b", " outstanding "),
    (r"\b(?:not|never) (?:exactly |quite |entirely |especially |particularly |very )?(?:my |a |the )?(?:cup of tea|strong suit|high point|masterpiece|classic|success|triumph|favorite|favourite)\b", " disappointing "),
    (r"\b(?:i|we) (?:only )?wish (?:i|we) (?:could|liked|had enjoyed)\b", " disappointed "),
    (r"\b(?:offers?|has|brings?) (?:precious |very )?little (?:else |new |of interest |to (?:offer|say)|in the way)\b", " uninspired "),
    (r"\b(?:no|little) (?:real |discernible |dramatic |emotional )?(?:depth|life|wit|point|logic|purpose|focus|insight|chemistry|originality|personality|sense|imagination|passion|heart|soul|energy|tension|suspense|conviction|impact|connection|interest|reason|charisma|coherence|redeeming qualities|appeal)\b", " lacking "),
    (r"\b(?:despite|for all|notwithstanding) its (?:many )?(?:faults|flaws|problems|shortcomings|weaknesses|imperfections)\b", " overall "),
    (r"\b(?:a |the )?(?:film|movie|story|plot|screenplay) (?:with |has )?(?:more )?holes\b", " plot holes "),
    (r"\b(?:long|roller) coaster ride\b", " thrilling ride "),
    (r"\b(?:the )?credits (?:finally )?roll\b", " credits roll "),
    (r"\b(?:direct(?:ed)?|produc(?:ed|tion)|perform(?:ed|ance)|act(?:ed|ing)|writ(?:ing|ten)|filmmaking|film|cast) (?:at (?:its|their|his|her) (?:very )?best)\b", " outstanding "),
]
_PATTERNS = [(re.compile(p), v) for p, v in _PATTERNS]
_INDEX = {}
for _t, _v in _P.items():
    _INDEX.setdefault(_t[0], []).append((_t, _v))
for _l in _INDEX.values():
    _l.sort(key=lambda pair: -len(pair[0]))

_NEG = set("no not never neither nor cannot hardly scarcely barely without lacking lacks lacked lack fails fail failed failing unable anythingbut hardly nowhere nobody nothing none seldom rarely".split())
_LIMIT = set("but yet however although though because whereas while despite unless instead except if who which with when where then until that than".split())
_PUNCT = set(".,:;!?()")
_UP = set("very really truly particularly incredibly amazingly extremely absolutely remarkably unusually entirely thoroughly totally terrifically especially extraordinarily exceptionally outrageously hugely enormously immensely decidedly supremely surprisingly deeply wonderfully quite utterly wildly incredibly highly genuinely totally vastly downright flatly relentlessly seriously painfully hopelessly shamefully woefully unforgivably appallingly breathtakingly awfully jolly sheer pure so".split())
_DOWN = set("somewhat fairly reasonably almost slightly rather occasionally intermittently sometimes moderately sporadically partially marginally relatively mildly fleetingly partly momentarily".split())
_DESIRE = set("tries try trying tried hoped hoping wants wanted wishes strives aspires attempts attempting supposed meant potential strives aiming aimed struggling struggles intended intended".split())
_NEG_BARE = {"not":-0.65, "no":-0.4, "little":-0.15, "never":-0.2, "cannot":-0.55,
             "too":-0.75, "hardly":-1.0, "barely":-0.85, "only":-0.35, "unfortunately":-2.4, "sadly":-1.8,
             "instead":-0.35, "alas":-2.3, "why":-0.4, "supposed":-0.7, "without":-0.15}

_words(1.9, """strong strengths well engrossment delights elucidates worthwhile relatable humane
resonates riveting engrossingly sincerely champion commend sustains delivers delivered
enthral enamored enamoured applause applauding compellingly soaring soars
refreshingly pleasingly attractively outstandingly masterliness illuminatingly
captivate captivates seduces satisfies surpass amuse amuses admire admired garnered
recommendations accolades award awards oscarworthy acclaimed praise praiseworthy
respected eminently invaluable invaluable astonishingly breathtakingly 
worth respectful respectably impressive resounding lively upbeat vibrancy loyalty
bountiful tenderness glamour glamourous glamorous spell irrepressible enraptured excellence
vigorous lustrous stirringly virtuosos composure legerdemain buoyed finesse""")
_words(-2, """unflattering insipidly alienating alienates undercut undercuts prevents detriment
cumbersome tiresomely flatly underwhelms overestimates contempt disdain ripoff
unimpressed unexcited unacceptably disheartening demoralizing dispiriting dismay
vapidly cookiecutter stiffly lunkheaded scatterbrained execrably cripples crippled
doomed problematic draggy overblown lumber clunks belabors intrudes distraction grinds
reeks reeks squandered mimicry mugging rickety cutesy preciousness arty artsy cloy
devoid devoid dispenses forsakes foregoes paucity shortage dearth deficiencies deficient
derails overextends insufficient contrivance repetitious redundant underwhelms underachieves
rubbishy stupefying hamstrung undercuts unentertaining hamfisted unexciting obfuscation
hodgepodge disheartens unpolished incongruous hokiness uncooked pretense phoniness
sadly tires squirm haphazard haphazardly amateurishly intermittently intermittent oblique
whiny whiny whimper whimpering unappealingly vacuity emptyheaded overwrought
overladen derivative chintzy obviousness outlandishly snail sluggish confusingly
stereotyping slovenly opaque regurgitates lackadaisical flops vapidity droning
limps lurches lifelessly carelessly disjointedly absence detriment unmerited
unnecessary ignored baffled miserable flounder regrettable regressive
marginally rehashing ridiculousness formulaically overambition disillusioned""")
_words(-1.3, "oddly merely curiously suspiciously contrives ostensibly pretends disappointments regret cloyingly regrettably sadly")
_words(1.6, "eerie chilling frightening terrifying believable zaniness exuberance spry enriching enriched enriches satisfying captivatingly freshen")
_words(0, "well only instead when awards delivered glamour drama feels tries nearly")
_words(-0.8, "hate hated hates uglier wrong cheap mush trashing boringly nonsense sleepy snoozing evil pity")
_words(-3, "hate hated dislike disliked dislikable brainless churlish atrociously justlymaligned")

_PREFIX = ("un", "non", "over")


def _lex(w):
    if w in _WORD:
        return _WORD[w]
    alts = []
    if len(w) > 4 and w.endswith("s"):
        alts.append(w[:-1])
        if w.endswith("ies"):
            alts.append(w[:-3] + "y")
        if w.endswith("es"):
            alts.append(w[:-2])
    for suffix in ("ness", "lessly", "fully", "ly", "ing", "ed", "er", "est"):
        if w.endswith(suffix) and len(w) > len(suffix) + 2:
            base = w[:-len(suffix)]
            alts.extend((base, base+"e"))
            if base.endswith("i"):
                alts.append(base[:-1] + "y")
            if len(base) > 2 and base[-1] == base[-2]:
                alts.append(base[:-1])
            if suffix == "ly" and base.endswith("ab"):
                alts.append(base+"le")
    for a in alts:
        if a in _WORD:
            return _WORD[a] * 0.91
    if w.startswith("un") and _WORD.get(w[2:], 0) > 0.8:
        return -2.5
    return 0


def _numeric(s):
    scores = []
    for m in re.finditer(r"\b(10|[0-9](?:\.\d+)?)\s*(?:/|out of)\s*(10|100|5|4)\b", s):
        a, b = float(m[1]), int(m[2])
        if a <= b:
            scores.append((a/b-0.55)*22)
    for m in re.finditer(r"\b([0-5](?:\.5)?|one|two|three|four|five|zero)\s*(?:out of (?:4|5|four|five) )?stars?\b", s):
        vals = dict(zero=0, one=1, two=2, three=3, four=4, five=5)
        n = vals[m[1]] if m[1] in vals else float(m[1])
        scores.append((n-2.55)*3.6)
    m = re.search(r"\b(?:grade|rating)\s*[:=]\s*([abcdef])\s*([+-]?)\b", s)
    if m:
        scores.append({"a":6,"b":3.8,"c":-1,"d":-5,"e":-6,"f":-7}[m[1]])
    return sum(scores)


def _segments(ts):
    out = []
    i = 0
    while i < len(ts):
        w = ts[i]
        for t, v in _INDEX.get(w, ()):
            if tuple(ts[i:i+len(t)]) == t:
                out.append((i, i+len(t), " ".join(t), v))
                i += len(t)
                break
        else:
            out.append((i, i+1, w, _lex(w)))
            i += 1
    return out


def _score(s):
    rating = _numeric(s)
    for pat, sub in _PATTERNS:
        s = pat.sub(sub, s)
    s = re.sub(r"\b(?:anything but|far from|less than)\b", " anythingbut ", s)
    s = re.sub(r"\b(?:is|was|seems|seemed|looks|looked) like (?:a |an )?", " resembles ", s)
    ts = re.findall(r"[a-z]+(?:'[a-z]+)?|\d+(?:\.\d+)?|[.,()!?;:]", s)
    seg = _segments(ts)
    values = []
    turns = [j for j, (_, _, w, _) in enumerate(seg)
             if w in ("but", "however", "yet", "instead", "ultimately", "nevertheless", "still")
             and not (w in ("yet", "still") and (j < 1 or seg[j-1][2] not in {",", ".", "and", ";"}))]
    for j, (i, end, w, val) in enumerate(seg):
        v = val
        if w in _PUNCT or w in _UP and len(w.split()) == 1:
            continue
        prev = []
        for k in range(j-1, max(-1, j-9), -1):
            u = seg[k][2]
            if u in _PUNCT or u in _LIMIT or i - seg[k][1] > 8:
                break
            prev.append(u)
        nxt = [a[2] for a in seg[j+1:j+6]]
        if w == "like" and prev and prev[0] in {"i", "you", "really", "did", "not"}:
            v = 1.9
        if w in {"lack", "lacks", "lacking", "without", "no", "not", "never", "cannot", "barely", "hardly"}:
            if any(a[3] and a[2] not in _PUNCT for a in seg[j+1:j+4]):
                v = min(0, v) * 0.28
            elif not v:
                v = _NEG_BARE.get(w, 0)
        if w in {"too", "only", "supposed", "why"}:
            v = _NEG_BARE.get(w, 0)
        if w == "little" and nxt and nxt[0] in {"girl", "boy", "town", "movie", "film", "gem"}:
            v = 0
        if not v:
            continue
        # Negation and privation, bounded by the local syntactic unit.
        negatives = []
        for h, u in enumerate(prev):
            if u in _NEG:
                if "and" in prev[:h] and h > 4:
                    break
                negatives.append(h)
            if u == "little" and not (h+1 < len(prev) and prev[h+1] in ("a", "this", "nice", "charming")):
                negatives.append(h)
            if u in ("devoid", "absence", "dearth", "shortage", "deprived", "devoid of") and h <= 3:
                negatives.append(h)
            if u in ("avoids", "avoiding", "avoid", "eschews", "eschewing", "avoided", "resists", "foregoes") and v < 0:
                negatives.append(h)
            if u in ("nothing but", "no more than", "little more than"):
                break
        if negatives and len(negatives) % 2 == 1:
            h = min(negatives)
            if h <= 3 or not any(_lex(a) for a in prev[:h]):
                v *= -0.90 if v > 0 else -0.76
        if v > 0 and (any(u in _DESIRE or u in ("tries to", "aims to", "attempts to", "strives to", "wants to be", "aspires to", "was supposed to", "is supposed to") for u in prev[:5])):
            v *= -0.35
        if v > 0 and any(u in ("would have", "should have") for u in prev):
            v *= -0.6
        if v > 0 and "if only" in prev:
            v *= -0.55
        if v > 0 and w in ("good", "great", "brilliant", "fine", "interesting", "fun", "charming", "funny", "exciting", "scary", "entertaining", "fresh", "original") and "enough" in nxt[:2]:
            if any(u in _NEG for u in prev):
                v = -abs(v)
            else:
                v *= 0.76
        if prev:
            if any(u in _UP for u in prev[:2]):
                v *= 1.32
            if any(u in _DOWN for u in prev[:2]):
                v *= 0.62
            if any(u in ("too", "overly", "excessively") for u in prev[:2]):
                v = -abs(v)*1.15
            if prev[0] in ("marginally", "mildly", "occasionally") and val > 1:
                v -= 0.75
        # Qualifications introduced by 'but' tend to carry the conclusion.
        weight = 1.
        for k in turns:
            if k > j and not any(a[2] in ".!?" for a in seg[j+1:k] if len(a[2]) == 1):
                weight *= 0.57
                break
            if k < j and not any(a[2] in {".","!","?"} for a in seg[k+1:j]):
                weight *= 1.19
                break
        left = [a[2] for a in seg[max(0, j-16):j]]
        cut = max([n for n,u in enumerate(left) if u in {".", ";", ",", "!", "?", "but"}] or [-1])
        clause = left[cut+1:]
        if any(u in {"despite", "although", "though", "while", "albeit", "whereas", "notwithstanding"} for u in clause):
            weight *= 0.58
        if w == "only saving grace" or w.startswith("only redeeming") or w == "the best thing about":
            weight *= 1.35
        if i and i/len(ts) > 0.7:
            weight *= 1.075
        values.append((w, v*weight))
    # Discount repeated words and weak genre/subject cues when stronger
    # evaluations are present.
    top = max([abs(x[1]) for x in values] or [0])
    total = 0
    seen = {}
    for w, v in values:
        if abs(v) < 1.0 and top > 1.7:
            v *= 0.45
        if abs(v) < 1.6 and top > 3:
            v *= 0.8
        n = seen.get(w, 0)
        seen[w] = n+1
        total += v / math.sqrt(1+n)
    if re.search(r"\b(?:what were they thinking|how (?:bad|much worse) can|who (?:really )?cares|why (?:on earth|bother)|is this (?:really )?(?:necessary|supposed to)|when will it end)\b", s):
        total -= 4
    if re.search(r"\b(?:high time|about time) (?:someone|somebody|we)\b", s):
        total += 1.65
    if re.search(r"\b(?:as |more )(?:fun|exciting|appealing|entertaining|interesting|enjoyable|funny) (?:as|than) (?:a (?:root canal|trip to the dentist|tax audit)|watching (?:paint|grass)|doing (?:laundry|taxes))", s):
        total -= 9
    if re.search(r"\b(?:too (?:bad|damn bad)|unfortunately|if only|alas|sadly)\b", s):
        total -= 1
    if re.search(r"\b(?:has|have|with) (?:all )?the (?:depth|subtlety|intelligence|charm|wit|personality|appeal|emotional range) of (?:a|an)\b", s):
        total -= 7
    if re.search(r"\b(?:want(?:ed)?|hop(?:e|ed)|would (?:have )?like(?:d)?) to (?:like|love|enjoy) (?:it|this)\b", s):
        total -= 4
    if re.search(r"\b(?:nothing|not much|little) (?:else )?(?:here|there) (?:for|to|that)\b", s):
        total -= 2.6
    if re.search(r"\b(?:not|never) (?:quite |even )?(?:lives?|living|lived) up\b|\bnot (?:a |an )?(?:very )?(?:good|pretty) (?:sign|thing)\b", s):
        total -= 3.8
    if re.search(r"\b(?:ambitions?|reach) (?:far )?(?:exceeds?|outstrips?|exceeds?|exceeding) (?:its |his |her |the director's )?(?:grasp|ability|execution)\b", s):
        total -= 4
    if re.search(r"\b(?:what|everything|all) (?:a|an) .{1,40} (?:film|movie|comedy|thriller) should be\b", s):
        total += 3
    if re.search(r"\b(?:i|you|we) (?:will |would |could |may )?(?:never|not) (?:want (?:it|this) to end|want to leave)\b", s):
        total += 4.4
    if re.search(r"\b(?:hate|hated) (?:to see|seeing) (?:it|this) end\b", s):
        total += 7
    if re.search(r"\b(?:best|most (?:enjoyable|entertaining|moving|original|exciting|powerful|beautiful|affecting)) .{0,45}\b(?:of the year|in years|i have (?:ever )?seen|in recent memory)\b", s):
        total += 4
    if abs(total) < 1.2:
        if re.search(r"\b(?:plot|script|dialogue) holes?\b|\b(?:ought to|supposed to|what happened|should have|could have|wishes it|has no|does little|if only|where is|where's|why did|why do|spare me|who needs)\b", s):
            total -= 1.5
        if re.search(r"\b(?:invites|reminds us|allows us|captures|evokes|takes us|you feel|gets at|gets to the heart|never lets|will appeal|worth|can appreciate|will appreciate|discover|revels in|thankfully|fortunately|thank goodness|at last)\b", s):
            total += 1.4
        if "?" in s and not re.search(r"\b(?:who could (?:ask|want)|what(?:'s| is) not to|what more|who knew|why not)\b", s):
            total -= 0.55
    return rating + total


def predict(state) -> dict:
    text = _normalize(_text(state))
    return {"answer": "positive" if _score(text) >= 0 else "negative"}