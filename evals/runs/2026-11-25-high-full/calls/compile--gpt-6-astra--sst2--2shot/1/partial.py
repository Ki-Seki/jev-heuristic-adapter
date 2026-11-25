import re
import math
import unicodedata
from bisect import bisect_left, bisect_right
from functools import lru_cache


_WORDS = {}
_PHRASES = {}


def _words(score, text):
    for word in text.split():
        _WORDS[word] = float(score)


def _phrases(score, text):
    for phrase in text.split("|"):
        phrase = phrase.strip()
        if phrase:
            _PHRASES[tuple(phrase.split())] = float(score)


_words(3.5, """
masterpiece masterpieces magnificent magnificently superb superbly sublime
sublimely phenomenal phenomenally exceptional exceptionally outstanding
unforgettable breathtaking spellbinding transcendent triumphant flawless
""")

_words(2.9, """
excellent excellence brilliant brilliantly brilliance wonderful wonderfully
marvelous marvelously marvellous marvellously terrific fantastic fantastically
fabulous fabulously awesome stunning stunningly spectacular spectacularly
exquisite exquisitely extraordinary extraordinarily masterful masterfully
riveting mesmerizing mesmerising enthralling exhilarating electrifying
dazzling delightful delightfully hilarious hilariously magnificent
""")

_words(2.5, """
great greatest best perfect perfection beautiful beautifully gorgeous
magnificence delight delights delighted delightful gem gems jewel treasure
treasures triumph triumphs joyous joyfully enthralled captivated engrossed
incredible incredibly astonishing superbness tourdeforce
""")

_words(2.15, """
good enjoyable enjoyably entertaining entertained entertainment fun funny
funnier funniest witty wittily wit engaging engaged compelling compellingly
absorbing engrossing captivating charming charmed charm charms touching
moving moved heartfelt heartwarming poignant poignantly affecting powerful
powerfully potent satisfying satisfied rewarding refreshing inspired
inspiring inspirational innovative creative creatively imaginative
imaginatively inventive inventively intelligent intelligently insightful
perceptive perceptively thoughtful thoughtfully fascinating fascinated
impressive impressively accomplished assured assuredly confident vibrant
vibrantly lively energetic energetically winning lovable endearing endearingly
enjoy enjoys enjoyed enjoyment recommend recommended recommends recommendation
love loved loves loving adored adore adores admire admired admiring
admiration applaud applauded applauds applause celebrate celebrates celebrated
gripping grippingly haunting hauntingly luminous radiant rousing stirring
uplifting unforgettable delicious deliciously exhilaratingly
""")

_words(1.65, """
appealing appeal appeals likable likeable pleasing pleased pleasurable
pleasure pleasures pleasant pleasantly amusing amused amusement humorous
humorously clever cleverly smart intelligently smartly savvy literate
articulate sophisticated sophistication deft deftly skillful skillfully
skilful skilfully skilled stylish stylishly elegant elegantly elegance
graceful gracefully polished handsome seductive sexy sensual rich richly
richness textured nuanced nuance subtleties subtle subtly subtlety sensitive
sensitively sensitivity humane humanistic compassionate compassion tender
tenderly tenderness honest honestly honesty sincere sincerely sincerity
authentic authenticity genuine genuinely naturalistic believable convincing
convincingly credible credibility resonant resonance meaningful meaningfully
worthwhile worth rewarding laudable commendable estimable admirable
original originality fresh freshness audacious audacity bold boldly daring
provocative provocatively challenging challenge challenging ambitious ambition
intimate intimacy expressive expressionistic lyrical lyrically poetic poetry
painterly atmospheric atmosphericness atmospheric suspenseful suspense
thrilling thrills thrill thrillerlike tense tension taut tightly
effective effectively effectiveness effective efficient efficiency
success successful successfully succeeds succeed succeeded
hilariousness hilarity laughter laughs chuckles chuckle chuckling
""")

_words(1.05, """
fine solid decent competently competent capable capably professional
watchable serviceable respectable satisfactory satisfying agreeable
accessible accessible rewarding modestly interesting intrigue intrigues
intriguing intrigued curious curiosity unusual unique distinct distinctive
unpredictable unconventional uncompromising unpretentious unforced unhurried
unassuming unvarnished unabashed unapologetic disarming disarmingly
unsentimental bittersweet heartbreaking heartbroken wrenching
playful playfully playful frolicsome buoyant buoyantly exuberant exuberantly
breezy brisk briskly crisp crisply zesty zippily sprightly nimble nimbly
droll wry wryly ironic irony offbeat quirky quirkiness eccentric eclectic
cool hip neat nifty snappy spunky spirited feisty gutsy gutsy robust muscular
vivid vividly vividness colorful colourful dazzlingly
eerie eerily chilling chillingly scary spooky creepy creepily unnerving
unsettling hypnotic hypnotically meditative contemplative
intricacy intricate complex complexity layered multilayered
coherent cohesive focused astute mature maturity grownup respectful
respectable respectful respect reverent reverence
satisfy satisfies impress impresses impressed entertain entertains
engage engages captivate captivates fascinate fascinates
inspire inspires inspiration dazzle dazzles illuminate illuminates illuminating
enlighten enlightening enlightens enrich enriching enriched
resonate resonates sparkle sparkles sparkling shines shine shining
blossoms blossom flourishes flourish soar soars soaring
amaze amazes amazed delighting astonish astonishes astonished
humor humour heart soul emotional emotions emotion humanity
""")

_words(0.55, """
adequate okay ok fair passable tolerable harmless affable genial amiable
straightforward unadorned unfussy simple simplicity earnest earnestly
earnestness effort effortful ambitiousness potential promise promising
promises promisingly fascinatingness intriguingness
gritty grit realism realistic realism documentarylike true truth truthful
accurate accuracy detailed detail delicacy delicate delicately
romantic romance romanticism romanticized nostalgic nostalgia
adventurous adventure escapist escapism
goofy goofiness oddball anarchic anarchistic irreverent irreverence
subversive subversion mischievous impish perverse perversely
disturbing disturbingly startling surprising surprisingly surprise surprises
surprised unexpected unexpectedly daringly formidable
universal universalness personable charismatic charisma chemistry
inventiveness intelligence imagination creativity energy vitality verve
pizzazz pizzaz gusto momentum pace pacing rhythm rhythmically
comfort comforting comfortable upbeat optimistic optimism hope hopeful
happiness happy happily merry festive celebratory cheerful cheerfulness
adorable cute sweetness sweet sweetly sweetness pretty
intensity intense intensely urgency urgent urgentness
""")

_words(-3.6, """
abysmal atrocious atrociously execrable unwatchable worthless appalling
appallingly horrendous horrendously horrible horribly horrid dreadful
dreadfully awful awfully terrible terribly worst disastrous disastrously
catastrophic catastrophe wretched wretchedly excruciating excruciatingly
insufferable insufferably unbearable unbearably intolerable intolerably
loathsome detestable contemptible abomination travesty garbage rubbish dreck
""")

_words(-2.7, """
boring bored boredom tedious tediously tedium dull dullness dreary drearily
lifeless listless inert plodding ponderous ponderously leaden lumbering
tiresome tiring wearisome monotonous monotonously monotony numbing soporific
interminable interminably pointless pointlessly purposeless meaningless
vacuous insipid vapid anemic anaemic stale trite hackneyed cliched cliche
cliches banal banality banalities contrived contrivance contrivances
uninspired unoriginal unimaginative uncreative uninteresting unengaging
uninvolving unconvincing unfunny humorless humourless joyless charmless witless
brainless mindless stupid stupidity dumb dumbness idiotic idiotically
moronic asinine inane inanely inept ineptly ineptitude incompetent incompetence
botched bungled bungling mishandled misbegotten miscalculated misfire
incoherent incoherence incomprehensible incomprehensibly incomprehension
mess messes messiness disaster disasters fiasco fiascos fiascoes
pretentious pretentiously pretentiousness pretension pretensions pompous
pompously smug smugly smarmy smarmily soulless hollow shallow superficial
sucks suck sucked stinks stink stunk lousy crap crappy crummy crapola
nauseating nauseous sickening repulsive repellent disgusting disgust
offensive offensively insulting insult insults insulted
unforgivable unforgivably atrociousness
""")

_words(-2.1, """
bad badly poor poorly disappointing disappointed disappoint disappointing
disappoints disappointment disappointments failure failures failed fail fails
flop flops flopped wasted wasting wastes waste squanders squander squandered
forgettable unmemorable disposable mediocre mediocrity mediocrities
weak weakness feeble feebly flimsy thinly sketchy underdeveloped
unfulfilled unrealized unachieved unappealing unlikable unlikeable
unlovable unpleasant disagreeable unsatisfying unsatisfied unrewarding
unimpressive unwatchably underwhelming underwhelmed anticlimactic anticlimax
frustrating frustrated frustration annoying annoyed annoy annoys annoyance
irritating irritated irritation irksome irritatingly grating abrasive
alienating alienated aggravating aggravation obnoxious obnoxiously
tediousness tiresomeness unpleasantness
derivative predictability predictable formulaic formula formulae formulas
recycled recycling rehashed rehash rehashing redundant redundancy repetitive
repetition repetitious monotonousness
wooden woodenness stilted stiltedly awkward awkwardly awkwardness clumsy
clumsily clumsiness amateurish amateurishly amateurism hammy hamfisted
unfocused muddled muddle messy disjointed disconnected choppy
confusing confused confusion muddling bewildering bewilderment
labored laboured labors labours forced strained straining overwrought
overblown overstuffed overlong bloated bloat inflated bombastic bombast
portentous glib glibly slick manipulative manipulation manipulated
mawkish maudlin cloying cloyingly syrupy sappy schmaltzy schmaltz treacly
tacky tasteless crass crassness vulgar vulgarity coarse crudely crudity
puerile sophomoric sophomorically juvenile infantile childish
sexist sexism racist racism homophobic misogynistic misogyny xenophobic
demeaning dehumanizing dehumanising exploitative exploitation exploitive
patronizing patronising condescending condescension
preachy preaching sanctimonious sanctimony moralistic moralizing moralising
dishonest dishonesty disingenuous fraudulent fake phony phoney bogus
artificial artificiality mechanical mechanically generic bland blandness
colorless colourless flavorless flavourless faceless anonymous pedestrian
unnecessary gratuitous gratuitously excessive excesses indulgent indulgence
unbearableness unendurable painful painfully agonizing agonising agonizingly
miserable miserably misery miserable insultingly objectionable
distasteful dismal dismally pitiful pitifully pathetic pathetically
""")

_words(-1.45, """
lacking lacks lack lacked missing misses missed miss losing loses lost
shortcomings shortcoming weaknesses faults fault problems problem trouble
troubles troublesome disappointingness letdown letdowns drawback drawbacks
flawed flaw flaws inconsistent inconsistency inconsistencies uneven unevenly
unevenness erratic erratically patchy spotty clunky cumbersome unwieldy
convoluted convolutions tortuous turgid turgidity lumberingly sluggish
sluggishly slack sagging sags sag drag drags dragging dragged droopy
flat flatness empty emptiness sterile antiseptic inertness
unremarkable unexceptional unambitious conventional unadventurous
contrivances contrivedly contriving stereotypical stereotyped stereotype
stereotypes caricature caricatures caricatured
melodramatic melodrama melodramatics sentimental sentimentality
corny corniness cheesy cheesiness hokey hokum hack hackwork
schlock schlocky trash trashy lurid luridly lowbrow
cynical cynically cynicism cynicalness exploit exploits pandering panders
pander panderingly didactic didacticism simplistic simplistically simplisticness
facile facilely facilely shallowly skimp skimps skimping
unbalanced imbalance baffling baffled bafflement impenetrable inscrutable
inaccessible obtuse opaque opacity
distracting distracted distraction distractions distancing distant cold
chilly unfeeling impersonal unrelatable unsympathetic unenthusiastic
uninspiring uninspirational inertly detached
dubious questionable dubiousness suspiciously iffy suspect
shoddy shoddily sloppy sloppily sloppiness cheap cheapness tawdry seedy
outdated outmoded dated archaic antiquated obsolete
strainedness artificialness preposterous absurdity ludicrous ridiculous
ridiculously risible laughable laughably farfetched implausible implausibility
unbelievable unbelievably incredulous nonsensical nonsense
bafflingly clueless cluelessness irresponsible irresponsiblely
hamstrung crippled sabotaged undermined diminished hampered marred
disappointingly unfortunately regrettably alas sadly
avoid avoids avoiding skip skips skipping
""")

_words(-0.65, """
slow slowly slowness lengthy lengthiness overkill
slight slightness thin bare minimal limited limits limitation limitations
ordinary familiar familiarity routine standard conventionality safe
muted subdued restrained restraint restrainedly austere austerity
obvious obviously obviousness predictablely telegraphed telegraphing
silly silliness foolish foolishly foolishness absurd absurdly
bizarre bizarrely bizarrely odd oddity weird weirdly strange strangely
contradictory contrarian conflicted ambivalent ambivalence
unresolved inconclusive incomplete unfinished underwritten undercooked
overcooked unpolished rough raw roughness ragged raggedly
shameless shamelessly shamelessness
inconsequential negligible trivial triviality trivialities lightweight
needless needlessly fuss fussy fussiness fussily
merely barely hardly scarcely belated belatedly
""")

# Words whose ordinary cinematic sense differs from their everyday polarity.
_words(1.7, """
terrifying terrifyingly horrifying fearsome nervewracking nailbiting
unpredictability unconventionally unpretentiously refreshingly
""")
_words(0.0, """
evil wicked villain villains villainous death dead deadly dying kill killed
killing kills murder murders murdered murderer murderous war wars violent
violence violenceful sad sadness sorrow grief grieving tragic tragedy
tragedies dark darkness bleak grim brutal brutality cruel cruelty suffering
suffer suffers suffered disease sick illness cancer crime criminal criminals
danger dangerous danger dangerously fear fears fearful horror horriblelooking
terror terrorist terrorists terrorize terrorized terriblelooking
blood bloody bloodshed gore gory gruesome grisly grotesque
comedy drama thriller action documentary movie film cinema story plot
character characters actor actors actress actresses director directors
screen screenplay script scripts dialogue dialogs dialogue
like well work
""")
_words(1.7, "liked likes liking")
_words(1.4, "better")
_words(-2.1, "worse")
_words(1.0, "works working")
_words(1.7, "revealing revelation revelatory")
_words(-1.8, "pedestrian")
_words(0.4, "restrained restraint")
_words(1.7, "uncompromising unflinching unflinchingly")
_words(2.0, "invaluable")
_words(1.0, "disturbing")
_words(0.8, "emotional")
_words(2.2, "fun")
_words(2.6, "hilarious")
_words(2.9, "brilliant")
_words(2.8, "great")
_words(3.4, "best")
_words(-3.8, "worst")
_words(2.6, "perfect")
_words(1.1, "interesting")
_words(-0.7, "imperfect imperfections imperfection")
_words(-1.4, "flawed")
_words(0.0, "only just almost nearly rather quite very really enough")


_phrases(3.5, """
must see | must watch | not to be missed | a work of art | work of art |
tour de force | cinematic masterpiece | instant classic | modern classic |
all time great | one of the best | among the best | absolute delight |
pure delight | sheer delight | sheer pleasure | pure pleasure |
nothing short of brilliant | nothing short of amazing |
nothing short of spectacular | nothing short of magnificent |
as good as it gets | at the top of his game | at the top of her game |
a triumph of filmmaking | filmmaking at its finest |
cannot recommend it enough | can not recommend it enough |
can not recommend this enough | could not recommend it more
""")

_phrases(2.6, """
worth seeing | worth watching | worth seeking out | worth a look |
worth your time | worth the time | worth the money | worth the price |
worth the price of admission | worth every penny | worth the effort |
well worth | highly recommended | wholeheartedly recommend |
wholeheartedly recommend | strongly recommend | heartily recommend |
two thumbs up | thumbs up | crowd pleaser | crowd pleasing |
a real treat | a rare treat | a special treat | a real gem | hidden gem |
a little gem | a small gem | great fun | good fun | lots of fun |
a lot of fun | a great deal of fun | tremendous fun | enormous fun |
terrific fun | wicked fun | riotously funny | laugh out loud |
laugh out loud funny | laugh riot | comic gold | comedy gold |
laugh a minute | laugh your head off | laugh yourself silly |
laugh until you cry | laughs aplenty | plenty of laughs |
deeply moving | deeply affecting | genuinely moving | genuinely funny |
truly funny | truly original | immensely entertaining |
hugely entertaining | thoroughly entertaining | highly entertaining |
sheer entertainment | pure entertainment | marvelous entertainment |
edge of your seat | edge of the seat | keeps you guessing |
kept me guessing | keeps us guessing | nail biting | nerve wracking |
pulse pounding | heart pounding | spine tingling | spine chilling |
packs a punch | packs an emotional punch | emotional wallop |
emotional powerhouse | emotional tour de force |
breath of fresh air | breath taking | a joy to watch | joy to behold |
pleasure to watch | pleasure to behold | treat to watch |
gets everything right | gets it right | hits all the right notes |
hits the right notes | firing on all cylinders | fires on all cylinders |
never a dull moment | not a dull moment | no dull moments |
never less than entertaining | never less than compelling |
never less than fascinating | never less than engaging |
never fails to entertain | never fails to amuse |
never ceases to amaze | never ceases to entertain |
never been better | never looked better | never been funnier |
could not be better | could not have been better |
could not be happier | could not have been more entertaining |
could not ask for more | could not ask for a better |
do not miss it | do not miss this | do not miss out |
do not pass this up | do yourself a favor | do yourself a favour
""")

_phrases(1.8, """
well made | well crafted | well constructed | well executed |
well acted | well directed | well written | well told | well paced |
well plotted | well played | well observed | well realized | well realised |
well rounded | well conceived | well cast | well done | well worth seeing |
finely crafted | finely tuned | finely observed | finely etched |
beautifully made | beautifully crafted | beautifully realized |
beautifully realised | beautifully written | beautifully acted |
skillfully made | skillfully directed | skillfully crafted |
expertly made | expertly directed | expertly crafted |
intelligently written | intelligently directed | sharply written |
sharply observed | sharp witted | quick witted | razor sharp |
first rate | top notch | top drawer | top flight | top class |
high quality | high caliber | high calibre |
a cut above | above average | better than average |
better than expected | better than you expect | better than it sounds |
better than it has any right to be |
more than the sum of its parts | greater than the sum of its parts |
a pleasant surprise | pleasant surprise | happy surprise |
holds your attention | holds the attention | held my attention |
commands attention | rewards attention | rewards the viewer |
stands out | stand out | stands apart | stands up | holds up |
stands the test of time | stand the test of time |
leaves an impression | leaves a lasting impression |
stays with you | stay with you | lingers in the mind |
gets under your skin | gets under the skin |
makes you think | make you think | food for thought | thought provoking |
raises interesting questions | asks important questions |
emotional depth | emotional resonance | emotional impact |
emotional punch | emotional heft | emotional power |
ring of truth | rings true | ring true | feels true | feels real |
true to life | true to itself | human touch | human warmth |
heart and soul | full of heart | has heart | has a heart |
full of life | full of energy | full of surprises |
sense of wonder | sense of discovery | sense of fun |
sense of humor | sense of humour | sense of wit |
good time | good times | a grand time | having a ball |
enough laughs | enough wit | enough charm |
infectious enthusiasm | infectious energy | infectious fun |
infectiously funny | delightfully funny | effortlessly funny |
endlessly fascinating | endlessly entertaining |
escapist fun | harmless fun | unpretentious fun | old fashioned fun |
guilty pleasure | guilty pleasures | guilty fun |
not half bad | none too shabby | not too shabby |
not a bad movie | not a bad film | not a bad effort |
not bad | not at all bad | not so bad | not that bad |
not remotely boring | anything but boring | anything but dull |
anything but predictable | anything but ordinary |
not your average | no ordinary | no small feat | no mean feat |
has a lot to offer | much to offer | a lot to recommend |
much to recommend | a lot going for it | plenty to like |
much to like | plenty to enjoy | much to enjoy |
worthy of attention | worthy of your attention |
deserves to be seen | deserves an audience | deserves a wider audience |
can not go wrong | cannot go wrong | you can do a lot worse |
you could do a lot worse | hard to resist | difficult to resist |
impossible to resist | impossible not to like | hard not to like |
hard not to love | hard not to enjoy | difficult not to like |
difficult not to admire | hard not to admire |
easy to like | easy to love | easy to enjoy |
painfully honest | painfully truthful | painfully real |
so bad it is good | so bad it is great | so bad that it is good |
bad in a good way | ridiculous in a good way |
does not take itself too seriously | do not take themselves too seriously |
never takes itself too seriously | tongue in cheek | tongue firmly in cheek
""")

_phrases(1.0, """
beautifully shot | beautifully photographed | beautifully filmed |
gorgeously shot | gorgeously photographed | visually beautiful |
visually stunning | visually striking | visually arresting |
visual splendor | visual splendour | visual feast | feast for the eyes |
easy on the eyes | handsome production | production values |
good looking | great looking | good natured | good hearted |
warm hearted | warmhearted | big hearted | open hearted |
light hearted | lighthearted | light on its feet |
high spirited | high spirits | high energy | high octane |
fast paced | fast moving | briskly paced | slow burn | slow burning |
low key | deadpan humor | dry wit | dry humor | dry humour |
old fashioned | old school | film buff | movie lover | cinema lover |
solid entertainment | decent entertainment | passable entertainment |
modest pleasures | small pleasures | simple pleasures |
mildly amusing | mildly entertaining | somewhat entertaining |
fairly entertaining | reasonably entertaining | reasonably good |
good enough | more than adequate | more than watchable |
not perfect | not quite perfect | far from perfect |
not without its flaws | not without flaws |
some nice moments | some good moments | a few good laughs |
a few laughs | has its moments | has moments | have their moments |
has something to say | something to say |
a labor of love | a labour of love | labor of love | labour of love |
love letter | loving tribute | affectionate tribute |
a good effort | an honest effort | good intentions |
in fine form | fine form | at his best | at her best | at their best |
grows on you | grow on you | wins you over | won me over
""")

# These are concessions, not wholehearted praise.
_phrases(-0.6, """
not perfect | not quite perfect | far from perfect | no masterpiece |
not a masterpiece | not the best | not quite a masterpiece |
not a great movie | not a great film | has its flaws | has some flaws |
flawed film | flawed movie | rough around the edges |
at best | in theory | on paper | good on paper |
best intentions | noble intentions | admirable intentions |
well intentioned | well meaning | means well | meant well |
ambitious failure | noble failure | honorable failure | honourable failure |
some nice moments but | a missed chance
""")

_phrases(-3.6, """
waste of time | waste of your time | waste of my time |
waste of money | waste of your money | waste of talent |
waste of celluloid | waste of film | wastes your time |
wastes our time | wasted opportunity | complete waste |
utter waste | total waste | cinematic disaster | cinematic atrocity |
one of the worst | among the worst | worst movie | worst film |
worst of the year | bottom of the barrel | scraping the bottom |
insult to the audience | insults the audience | insults your intelligence |
insult to your intelligence | insult to our intelligence |
insults our intelligence | an endurance test | endurance test |
exercise in tedium | exercise in boredom | exercise in futility |
avoid at all costs | avoid like the plague | stay away |
save your money | save your time | save yourself the trouble |
do not waste your money | do not waste your time |
do not bother | not worth seeing | not worth watching |
not worth the time | not worth your time | not worth the money |
not worth the price | not worth the effort | not worth a look |
a must miss | must avoid | thumbs down | two thumbs down |
dead on arrival | dead in the water | falls flat on its face |
painful to watch | painful to sit through | agony to watch |
torture to watch | unbearable to watch | impossible to watch
""")

_phrases(-2.65, """
not funny | never funny | no laughs | without laughs |
devoid of laughs | devoid of humor | devoid of humour |
without humor | without humour | no humor | no humour |
no wit | no charm | no heart | no soul | no substance |
no depth | no imagination | no originality | no suspense |
no tension | no excitement | no entertainment |
nothing to recommend | little to recommend | nothing to offer |
nothing to say | nothing worth | nothing worthwhile |
nothing interesting | nothing remotely interesting |
nothing special | nothing new | nothing original |
nothing fresh | nothing memorable | nothing compelling |
nothing but cliches | nothing but clichés |
not a single laugh | not one laugh | nary a laugh |
few laughs | precious few laughs | very few laughs |
too few laughs | few and far between | laughs are scarce |
laughs are few | fails to deliver | failed to deliver |
fails to engage | fails to entertain | fails to convince |
fails to connect | fails to satisfy | fails to impress |
fails on every level | misses the mark | missed the mark |
falls short | falls flat | fall flat | fell flat |
rings false | ring false | rings hollow | ring hollow |
feels false | feels fake | feels forced | feels contrived |
does not work | do not work | did not work |
does not deliver | does not hold up |
does not add up | do not add up | does not make sense |
makes no sense | make no sense | made no sense |
makes little sense | makes precious little sense |
runs out of steam | run out of steam | ran out of steam |
runs out of ideas | runs out of gas | outstays its welcome |
overstays its welcome | outstays its novelty |
goes nowhere | go nowhere | going nowhere | leads nowhere |
goes on and on | drags on | drags on and on |
goes through the motions | going through the motions |
by the numbers | paint by numbers | connect the dots |
been there done that | seen it all before | seen this before |
seen it before | seen that before | seen a hundred times |
same old story | same old thing | same old same old |
tired old | old hat | warmed over | warmed up |
half baked | half assed | half cocked | slap dash | slapdash |
ham fisted | ham handed | heavy handed | heavy handedness |
self indulgent | self indulgence | self important | self importance |
self satisfied | self satisfaction | self congratulatory |
self conscious | self consciously | overly familiar |
paper thin | wafer thin | one dimensional | two dimensional |
cardboard characters | cardboard character | cardboard cutouts |
cardboard cutout | stick figures | stock characters |
wooden acting | wooden performances | wooden performance |
bad acting | poor acting | flat performances | flat performance |
badly acted | badly written | badly directed | badly made |
poorly acted | poorly written | poorly directed | poorly made |
poorly executed | poorly conceived | poorly developed |
clumsily executed | clumsily directed | sloppily made |
emotionally empty | emotionally hollow | emotionally manipulative |
emotionally inert | emotionally sterile | emotionally dead |
dramatically inert | dramatically flat | dramatically empty |
dramatically unsatisfying | visually dull |
brain dead | brain numbing | mind numbing | soul deadening |
sleep inducing | yawn inducing | cringe inducing |
groan inducing | headache inducing | stomach turning |
hard to sit through | difficult to sit through |
hard to watch | difficult to watch |
hard to like | difficult to like | impossible to like |
hard to enjoy | impossible to enjoy | difficult to enjoy |
hard to recommend | difficult to recommend | impossible to recommend |
could not care less | can not care less | could care less |
who cares | why bother | what is the point |
what were they thinking | what was the point |
not in a good way | in the worst way | for all the wrong reasons |
for the wrong reasons | unintentionally funny | unintentionally hilarious |
inadvertently funny | accidentally funny | laughably bad |
hilariously bad | hilariously inept | laughably inept |
too little too late | too little , too late |
too much of a mess | a hot mess | hot mess | a train wreck |
train wreck | car wreck | trainwreck
""")

_phrases(-1.8, """
too much | too too much | far too much | way too much |
too many | far too many | way too many |
too long | much too long | far too long | way too long |
too slow | too dull | too boring | too predictable |
too obvious | too familiar | too formulaic | too conventional |
too sentimental | overly sentimental | too cute | too clever |
too smart for its own good | too clever for its own good |
too cute for its own good | too slick | too glossy |
too contrived | too convoluted | too confusing |
too ambitious | overly ambitious | over ambitious |
tries too hard | trying too hard | try too hard |
tries much too hard | trying much too hard |
takes itself too seriously | take itself too seriously |
take themselves too seriously | taking itself too seriously |
takes itself seriously | wants it both ways | have it both ways |
less than the sum of its parts | less than meets the eye |
leaves you cold | left me cold | leaves me cold |
leaves us cold | leaves one cold | leaves a bad taste |
leaves a sour taste | bad taste in your mouth |
a bitter disappointment | a major disappointment |
a missed opportunity | missed opportunity | missed opportunities |
a wasted opportunity | squandered opportunity |
a step backward | a step backwards | a step down |
not much fun | not much good | not very good | not so good |
no good | little good | little fun | little charm |
little wit | little humor | little humour | little suspense |
little tension | little originality | little imagination |
little substance | little depth | little heart |
less than compelling | less than entertaining | less than satisfying |
less than thrilling | less than impressive | less than convincing |
less than inspired | short on laughs | short on humor |
short on humour | short on charm | short on originality |
short on substance | short on ideas | short on imagination |
lack of focus | lack of direction | lack of purpose |
lack of a plot | lacks a plot | without a plot |
has no plot | no plot | no story | no point |
style over substance | style without substance |
all style and no substance | all flash and no substance |
all flash | all surface | empty spectacle | hollow spectacle |
more of the same | nothing more than | little more than |
just another | yet another | a pale imitation | pale imitation |
poor imitation | inferior imitation | cheap imitation |
poor substitute | poor excuse | lame excuse |
second rate | third rate | fourth rate | sub par | sub standard |
below average | below par | low quality | cheap looking |
made for tv | made for television |
straight to video | direct to video | straight to dvd |
wait for video | wait for cable | wait for the dvd |
better off watching | better off renting | better off staying |
better left unseen | better left unsaid | should have stayed |
deserves better | deserved better | deserve better |
should know better | should have known better |
could have been better | should have been better |
could be better | could do better | should be better |
not much better | little better than | barely better than |
not good enough | not nearly enough | not enough |
barely watchable | barely tolerable | barely amusing |
barely entertaining | barely funny | hardly funny | hardly entertaining |
only mildly amusing | only mildly entertaining |
mildly interesting at best | interesting only in theory |
mercifully short | mercifully brief | thankfully short |
at least it is short | at least it is brief |
only saving grace | only redeeming feature | sole redeeming feature |
the only good thing | the only good part | small consolation |
damning with faint praise | faint praise | a chore to watch |
a chore to sit through | like watching paint dry |
watching paint dry | watching grass grow | put you to sleep |
puts you to sleep | put me to sleep | sends you to sleep |
test your patience | tests your patience | testing your patience |
strains credibility | stretches credibility | strains credulity |
stretches credulity | suspension of disbelief |
loses its way | loses its focus | loses its appeal |
loses its charm | lost its charm | loses steam |
squanders its potential | wastes its potential |
misses the point | missing the point | missed the point |
off putting | offputting | ill advised | ill conceived |
ill judged | ill timed | ill served | ill suited |
not my cup of tea | not for me | not my taste
""")

# Neutral multiword expressions prevent misleading individual-word matches.
_phrases(0.0, """
not only | not just | not merely | not simply |
no doubt | no wonder | no question | no matter | no one |
nothing but | nothing short of | no less than | no less |
not without | no shortage of | without losing | without sacrificing |
at worst | for better or worse | for good or ill |
as well as | well as | as well | well then |
good guy | good guys | bad guy | bad guys | bad boy | bad boys |
good cop | bad cop | good girl | bad girl | good girls | bad girls |
evil dead | beautiful mind | perfect storm |
love story | love stories | love triangle | love triangles |
love affair | love affairs | love interest | love interests |
love life | love scene | love scenes | love song | love songs |
love and loss | love and death | love and hate | love hate |
fall in love | falls in love | falling in love | fell in love |
in love with | making love | make love |
happy ending | happy endings | sad ending | tragic ending |
happy family | broken heart | broken hearts |
mental illness | mental hospital | sick child | dying mother |
dark comedy | black comedy | dark humor | dark humour |
bad news | bad weather | bad luck | bad taste |
good news | good luck | good fortune | good reason | good reasons |
good deal of | a good deal | great deal of | a great deal |
great depression | cold war | cold blood | in cold blood |
big screen | small screen | silver screen |
low budget | high budget | big budget | small budget |
low concept | high concept | special effects |
working class | middle class | upper class |
real life | real world | true story | true stories |
feature film | feature length | feature debut |
little girl | little boy | little girls | little boys |
young love | tough guy | tough guys |
dead serious | deadly serious | dead end | dead ends |
free will | free time | free world |
in spite of | rather than | more or less
""")

# Some unusual or disreputable qualities are praise when explicitly celebrated.
for _adverb in (
    "delightfully", "wonderfully", "gloriously", "charmingly", "endearingly",
    "gleefully", "joyously", "entertainingly", "exuberantly", "deliciously"
):
    for _adjective in (
        "silly", "goofy", "absurd", "ridiculous", "outrageous", "cheesy",
        "trashy", "schlocky", "dumb", "stupid", "nasty", "perverse",
        "macabre", "overblown", "excessive", "eccentric", "bizarre"
    ):
        _PHRASES[(_adverb, _adjective)] = 2.0

for _adverb in ("wonderfully", "brilliantly", "beautifully", "expertly", "superbly"):
    for _participle in ("acted", "directed", "written", "crafted", "made", "executed"):
        _PHRASES[(_adverb, _participle)] = 2.5

for _adjective in ("great", "good", "funny", "entertaining", "enjoyable", "compelling"):
    _PHRASES[("almost", _adjective)] = -0.6
    _PHRASES[("not", "quite", _adjective)] = -1.1

_PHRASE_INDEX = {}
for _phrase, _value in _PHRASES.items():
    _PHRASE_INDEX.setdefault(_phrase[0], []).append((_phrase, _value))
for _first in _PHRASE_INDEX:
    _PHRASE_INDEX[_first].sort(key=lambda item: -len(item[0]))


_SPELLING = {
    "favourite": "favorite",
    "favourites": "favorites",
    "humour": "humor",
    "humourless": "humorless",
    "colourful": "colorful",
    "colourless": "colorless",
    "flavourless": "flavorless",
    "realised": "realized",
    "realise": "realize",
    "realises": "realizes",
    "realising": "realizing",
    "organised": "organized",
    "centre": "center",
    "centres": "centers",
    "theatre": "theater",
    "theatres": "theaters",
    "sceptical": "skeptical",
    "scepticism": "skepticism",
    "honourable": "honorable",
    "favour": "favor",
    "labour": "labor",
    "laboured": "labored",
    "labours": "labors",
    "mesmerising": "mesmerizing",
    "patronising": "patronizing",
    "moralising": "moralizing",
    "dehumanising": "dehumanizing",
}

_BOOSTERS = {
    "very": 1.22, "really": 1.18, "extremely": 1.5, "utterly": 1.45,
    "absolutely": 1.4, "completely": 1.35, "totally": 1.3,
    "thoroughly": 1.35, "entirely": 1.25, "particularly": 1.18,
    "especially": 1.2, "remarkably": 1.3, "exceptionally": 1.35,
    "incredibly": 1.35, "amazingly": 1.3, "astonishingly": 1.3,
    "deeply": 1.25, "profoundly": 1.35, "immensely": 1.4,
    "hugely": 1.4, "enormously": 1.4, "highly": 1.3,
    "genuinely": 1.2, "truly": 1.25, "unusually": 1.15,
    "terribly": 1.2, "awfully": 1.2, "seriously": 1.15,
    "so": 1.15, "such": 1.1, "more": 1.1, "most": 1.25,
    "much": 1.12, "far": 1.15, "quite": 1.1,
    "somewhat": 0.6, "slightly": 0.55, "mildly": 0.4,
    "vaguely": 0.25, "moderately": 0.65, "reasonably": 0.75,
    "fairly": 0.7, "pretty": 0.8, "sorta": 0.55,
    "occasionally": 0.5, "sometimes": 0.65, "sporadically": 0.4,
    "intermittently": 0.5, "fitfully": 0.45, "passably": 0.6,
    "partly": 0.65, "partially": 0.6, "merely": 0.65,
    "almost": 0.65, "nearly": 0.75,
}

_ABSENCE = {
    "lack", "lacks", "lacked", "lacking", "missing",
    "fail", "fails", "failed", "failing", "failure",
    "avoid", "avoids", "avoided", "avoiding",
    "eschew", "eschews", "eschewing",
    "devoid", "bereft", "without", "lose", "loses", "losing",
}

_ASPECT_NOUNS = {
    "cast", "actor", "actors", "actress", "actresses", "acting",
    "performance", "performances", "cinematography", "photography",
    "photographed", "shot", "visuals", "effects", "soundtrack",
    "costumes", "costume", "scenery", "locations", "design",
    "premise", "concept", "idea", "ideas", "intentions",
}
_OUTSIDE_ASPECTS = {"title", "trailer", "poster", "marketing", "advertising"}
_THEME_WORDS = {
    "love", "loves", "loving", "hate", "hates", "hated", "happy",
    "happiness", "hope", "hopeful", "romance", "romantic",
    "sweet", "sweetness", "beautiful", "gorgeous", "cute",
}
_STRONG_BOUNDARIES = {".", "!", "?", ";", ":"}
_SCOPE_BOUNDARIES = _STRONG_BOUNDARIES | {",", "however", "although", "though", "nevertheless", "nonetheless"}
_SUBJECTS = {"i", "we", "you", "they", "audiences", "viewers", "critics"}
_FAIL_FORMS = {"fail", "fails", "failed", "failing", "failure"}


def _normalize(text):
    text = unicodedata.normalize("NFKC", text).lower()
    text = text.replace("\u2019", "'").replace("\u2018", "'").replace("`", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2014", " ; ").replace("\u2013", " - ")
    text = re.sub(r"-{2,}", " ; ", text)
    text = re.sub(r"\bwo\s*n\s*'\s*t\b", "will not", text)
    text = re.sub(r"\bsha\s*n\s*'\s*t\b", "shall not", text)
    text = re.sub(r"\bai\s*n\s*'\s*t\b", "is not", text)
    text = re.sub(r"\bca\s*n\s*'\s*t\b", "can not", text)
    text = re.sub(r"\b([a-z]+)\s*n\s*'\s*t\b", r"\1 not", text)
    text = re.sub(r"\bcannot\b", "can not", text)
    text = re.sub(r"\b([a-z]+)\s*'\s*(re|ve|ll|d|m)\b", _expand_contraction, text)
    text = re.sub(
        r"\b(it|that|there|here|what|who|he|she|how|where)\s*'\s*s\b",
        r"\1 is", text
    )
    text = re.sub(r"\b([a-z]+)\s*'\s*s\b", r"\1 s", text)
    text = re.sub(r"\b(kinda)\b", "kind of", text)
    text = re.sub(r"\b(sortof)\b", "sort of", text)
    text = text.replace("&", " and ")
    text = text.replace("-lrb-", " ( ").replace("-rrb-", " ) ")
    text = text.replace("-", " ")
    text = "".join(
        char for char in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(char)
    )
    return text


def _expand_contraction(match):
    expansions = {"re": "are", "ve": "have", "ll": "will", "d": "would", "m": "am"}
    return match.group(1) + " " + expansions[match.group(2)]


@lru_cache(maxsize=12000)
def _word_value(word):
    if word in _WORDS:
        return _WORDS[word]
    candidates = []
    if word.endswith("ies") and len(word) > 4:
        candidates.append(word[:-3] + "y")
    if word.endswith("ied") and len(word) > 4:
        candidates.append(word[:-3] + "y")
    if word.endswith("ily") and len(word) > 5:
        candidates.append(word[:-3] + "y")
    if word.endswith("ly") and len(word) > 5:
        candidates.extend((word[:-2], word[:-2] + "e"))
    if word.endswith("ing") and len(word) > 6:
        root = word[:-3]
        candidates.extend((root, root + "e"))
        if len(root) > 3 and root[-1:] == root[-2:-1]:
            candidates.append(root[:-1])
    if word.endswith("ed") and len(word) > 5:
        root = word[:-2]
        candidates.extend((root, word[:-1]))
        if len(root) > 3 and root[-1:] == root[-2:-1]:
            candidates.append(root[:-1])
    if word.endswith("ness") and len(word) > 7:
        root = word[:-4]
        candidates.append(root)
        if root.endswith("i"):
            candidates.append(root[:-1] + "y")
    if word.endswith("es") and len(word) > 5:
        candidates.extend((word[:-1], word[:-2]))
    elif word.endswith("s") and not word.endswith("ss") and len(word) > 4:
        candidates.append(word[:-1])
    for root in candidates:
        if root in _WORDS:
            return _WORDS[root]
    for prefix in ("un", "non", "dis"):
        if word.startswith(prefix) and len(word) >= len(prefix) + 5:
            root = word[len(prefix):]
            if root in _WORDS and _WORDS[root]:
                return -0.85 * _WORDS[root]
    return 0.0


_PATTERN_RULES = [
    (
        r"\b(?:makes?|made) (?:[^.!?;, ]+ ){0,13}look (?:like (?:a |an )?"
        r"(?:masterpiece|work of art|classic|great film|great movie)|good|brilliant|excellent)\b",
        -3.4,
    ),
    (
        r"\b(?:best|funniest|most enjoyable|most entertaining|most interesting) "
        r"(?:thing|part|moment) (?:[^.!?; ]+ ){0,11}"
        r"(?:end credits|closing credits|trailer|is over|it ends)\b",
        -3.0,
    ),
    (
        r"\b(?:only|sole) (?:reason|incentive) (?:[^.!?;, ]+ ){0,4}"
        r"(?:watch|see|sit through)\b",
        -1.4,
    ),
    (
        r"\b(?:can|could) not (?:[^.!?;, ]+ ){0,3}recommend "
        r"(?:it |this |the movie |the film )?(?:highly |strongly )?enough\b",
        3.2,
    ),
    (
        r"\b(?:can|could) not (?:be|have been) "
        r"(?:any |much |a lot )?(?:better|funnier|more enjoyable|more entertaining)\b",
        3.0,
    ),
    (
        r"\b(?:can|could) not (?:be|have been) "
        r"(?:any |much )?(?:worse|more boring|less interesting|less entertaining)\b",
        -3.2,
    ),
    (
        r"\b(?:hard|difficult|impossible) not to "
        r"(?:really )?(?:like|love|enjoy|admire|appreciate|recommend)\b",
        2.3,
    ),
    (
        r"\b(?:do|does|did) not (?:ever |really )?take "
        r"(?:itself|themselves) (?:all )?too seriously\b",
        1.8,
    ),
    (
        r"\b(?:not|never) (?:even |remotely |particularly |very |really |at all )?"
        r"(?:as |that |all that )?(?:good|funny|entertaining|interesting|enjoyable) "
        r"as (?:it |you |one |the premise )?(?:sounds|looks|should|could|might|promises)\b",
        -2.2,
    ),
    (
        r"\b(?:so|such a) (?:bad|stupid|ridiculous|terrible|awful) "
        r"(?:movie |film )?(?:that )?it is (?:actually |almost )?(?:good|fun|funny|enjoyable)\b",
        2.0,
    ),
    (
        r"\b(?:more|better) (?:fun|entertainment|laughs|enjoyment) "
        r"(?:[^.!?;, ]+ ){0,5}(?:watching paint dry|watching grass grow)\b",
        -3.0,
    ),
    (
        r"\b(?:would|could) have been (?:a |an )?"
        r"(?:great|good|wonderful|excellent|terrific|interesting|entertaining) "
        r"(?:movie|film)\b",
        -1.8,
    ),
    (
        r"\b(?:never|not) (?:[^.!?;, ]+ ){0,3}(?:a single|one decent) laugh\b",
        -2.7,
    ),
    (
        r"\b(?:nothing|little) (?:[^.!?;, ]+ ){0,3}to "
        r"(?:like|love|enjoy|admire|recommend)\b",
        -2.4,
    ),
]
_PATTERN_RULES = [(re.compile(pattern), value) for pattern, value in _PATTERN_RULES]


def _pattern_events(tokens):
    joined = " ".join(tokens)
    starts = []
    offset = 0
    for token in tokens:
        starts.append(offset)
        offset += len(token) + 1
    candidates = []
    for pattern, value in _PATTERN_RULES:
        for match in pattern.finditer(joined):
            start = max(0, bisect_right(starts, match.start()) - 1)
            end = bisect_left(starts, match.end())
            if end > start:
                candidates.append((start, end, value))
    candidates.sort(key=lambda item: (-(item[1] - item[0]), item[0]))
    occupied = set()
    events = []
    for start, end, value in candidates:
        if not any(index in occupied for index in range(start, end)):
            occupied.update(range(start, end))
            events.append((start, end, value, True))
    return events, occupied


def _contrast_at(tokens, index):
    word = tokens[index]
    previous = tokens[index - 1] if index else ""
    following = tokens[index + 1] if index + 1 < len(tokens) else ""
    if word == "but":
        if previous in {"nothing", "anything", "everything", "all"}:
            return False
        if following in {"also", "rather"}:
            return False
        before = tokens[max(0, index - 18):index]
        if "not" in before and any(w in before for w in ("only", "just", "merely")):
            return False
        return True
    if word == "yet":
        return previous not in {"not", "as", "has", "have", "had"} and following != "another"
    return word in {"however", "nevertheless", "nonetheless"}


def _scope_prefix(tokens, start):
    result = []
    for index in range(start - 1, max(-1, start - 12), -1):
        word = tokens[index]
        if word in _SCOPE_BOUNDARIES or _contrast_at(tokens, index):
            break
        result.append(index)
    result.reverse()
    return result


def _lexical_event(tokens, index):
    word = tokens[index]
    before = tokens[max(0, index - 4):index]
    after = tokens[index + 1:index + 5]
    if word == "like":
        if before and (
            before[-1] in _SUBJECTS
            or before[-1] in {"not", "never", "really", "quite", "will", "would", "do", "did"}
            or (len(before) > 1 and before[-2] in _SUBJECTS)
        ):
            return 1.6
        return 0.0
    if word == "work":
        if before and before[-1] in {
            "not", "never", "does", "did", "will", "can", "could", "should",
            "really", "actually", "to"
        }:
            return 1.1
        return 0.0
    if word in {"working", "works"}:
        if after and after[0] in {"class", "of", "on", "at", "for", "with", "as"}:
            return 0.0
    if word == "pretty" and after and _word_value(after[0]) != 0:
        return 0.0
    if word in _BOOSTERS and after and _word_value(after[0]) != 0:
        if word.endswith("ly") or word in {"quite", "really", "very", "so", "more", "most"}:
            return 0.0
    if word in {"original", "great"} and after and after[0] in {
        "novel", "book", "version", "series", "depression"
    }:
        return 0.0
    if word in {"love", "loves", "loving", "romantic"}:
        if any(w in before for w in ("about", "between", "story", "tale")):
            return 0.0
    return _word_value(word)


def _collect_events(tokens):
    events, protected = _pattern_events(tokens)
    occupied = set(protected)
    index = 0
    while index < len(tokens):
        if index in occupied:
            index += 1
            continue
        matched = False
        for phrase, score in _PHRASE_INDEX.get(tokens[index], ()):
            end = index + len(phrase)
            if end > len(tokens) or any(j in occupied for j in range(index, end)):
                continue
            if tuple(tokens[index:end]) == phrase:
                occupied.update(range(index, end))
                protected.update(range(index, end))
                if score:
                    events.append((index, end, score, True))
                index = end
                matched = True
                break
        if matched:
            continue
        value = _lexical_event(tokens, index)
        if value:
            events.append((index, index + 1, value, False))
        index += 1
    events.sort(key=lambda item: item[0])
    return events, protected


def _negation_count(tokens, indices, start, protected):
    count = 0
    for index in indices:
        if index in protected:
            continue
        word = tokens[index]
        following = tokens[index + 1] if index + 1 < len(tokens) else ""
        previous = tokens[index - 1] if index else ""
        distance = start - index
        if word in {"not", "never", "neither", "nor", "without", "hardly", "scarcely", "barely"}:
            if word == "not" and following in {"only", "just", "merely", "simply"}:
                continue
            if word == "not" and previous == "should" and "have" in tokens[index + 1:start]:
                continue
            if word == "not" and following == "to" and previous in {"try", "tries", "trying"}:
                continue
            count += 1
        elif word == "no":
            if following not in {"matter", "doubt", "wonder", "question", "one", "less"}:
                count += 1
        elif word in {"nothing", "nowhere", "nobody", "none"}:
            if following not in {"but", "short", "less"}:
                count += 1
        elif word == "anything" and following == "but":
            count += 1
        elif word == "far" and following == "from":
            count += 1
        elif word == "less" and distance <= 4:
            if previous not in {"no", "not", "or"}:
                count += 1
        elif word in {"few", "little"} and distance <= 3:
            if previous not in {"a", "the", "this", "that", "some", "every"}:
                count += 1
        elif word in _ABSENCE and distance <= 7:
            if word in _FAIL_FORMS:
                if "to" in tokens[index + 1:start]:
                    count += 1
            else:
                count += 1
        elif word == "free" and following in {"of", "from"} and distance <= 6:
            count += 1
    return count


def _local_aspect(tokens, start, end):
    left = max(0, start - 3)
    right = min(len(tokens), end + 4)
    for index in range(start - 1, left - 1, -1):
        if tokens[index] in _SCOPE_BOUNDARIES or _contrast_at(tokens, index):
            left = index + 1
            break
    for index in range(end, right):
        if tokens[index] in _SCOPE_BOUNDARIES or _contrast_at(tokens, index):
            right = index
            break
    nearby = set(tokens[left:right])
    if nearby & _OUTSIDE_ASPECTS:
        return 0.4, True
    if nearby & _ASPECT_NOUNS:
        return 0.78, True
    return 1.0, False


def _modify_event(event, tokens, protected, events):
    start, end, value, phrase = event
    prefix_indices = _scope_prefix(tokens, start)
    prefix = [tokens[index] for index in prefix_indices]
    prefix_text = " ".join(prefix)
    local = tokens[start:end]

    # "Lacks originality" should be evaluated as absence of originality,
    # not as two unrelated judgments.
    if not phrase and tokens[start] in _ABSENCE:
        for other_start, other_end, other_value, other_phrase in events:
            if start < other_start <= start + 7:
                middle = tokens[start + 1:other_start]
                if not any(
                    word in _SCOPE_BOUNDARIES or word in {"but", "yet"}
                    for word in middle
                ):
                    value *= 0.18
                    break

    negations = _negation_count(tokens, prefix_indices, start, protected)
    if negations % 2:
        value *= -0.85

    factor = 1.0
    for index in prefix_indices[-3:]:
        if index in protected:
            continue
        word = tokens[index]
        if word in _BOOSTERS:
            factor *= _BOOSTERS[word]
    if len(prefix) >= 2 and prefix[-2:] in (["sort", "of"], ["kind", "of"]):
        factor *= 0.55
    if "at least" in prefix_text:
        factor *= 0.75
    value *= max(0.18, min(factor, 1.85))

    if not phrase:
        base = _word_value(tokens[start])
        if base > 0 and negations % 2 == 0:
            if re.search(
                r"\b(?:tr(?:y|ies|ied|ying)|want(?:s|ed)?|aim(?:s|ed)?|"
                r"attempt(?:s|ed)?|aspire(?:s|d)?|striv(?:e|es|ing)) "
                r"(?:hard )?to (?:be |seem |feel )?$",
                prefix_text,
            ):
                value *= -0.35
            if re.search(r"\b(?:supposed|meant|intended) to (?:be )?$", prefix_text):
                value *= -0.35
            if "so called" in prefix_text:
                value *= -0.65
            if "too" in prefix[-3:] and tokens[start] not in {
                "good", "great", "funny", "entertaining", "enjoyable",
                "beautiful", "wonderful", "excellent"
            }:
                value *= -0.65

        if re.search(r"\b(?:could|should|would|might) (?:\w+ )?have been\b", prefix_text):
            if negations % 2 == 0:
                value *= -0.7
        elif re.search(r"\bshould (?:really )?be\b", prefix_text) and base > 0:
            value *= 0.3

        if tokens[start] in _THEME_WORDS:
            earlier = tokens[max(0, start - 8):start]
            if any(word in earlier for word in {"about", "tale", "chronicles", "follows"}):
                value *= 0.3

    aspect_factor, aspect = _local_aspect(tokens, start, end)
    value *= aspect_factor

    # Merely imagining a better film is not praise of the film under review.
    if "wish" in prefix or "wished" in prefix:
        if value > 0:
            value *= -0.65

    # A character's "good" or "bad" nature is not necessarily a review.
    if len(local) == 1 and local[0] in {"good", "bad", "evil", "sweet"}:
        following = tokens[end:end + 2]
        if following and following[0] in {
            "person", "man", "woman", "kid", "child", "father", "mother",
            "husband", "wife", "people"
        }:
            value *= 0.25

    return start, end, value, aspect


def _concession_weights(tokens):
    weights = [1.0] * len(tokens)
    for index, word in enumerate(tokens):
        if word not in {"although", "though", "despite", "while", "albeit"}:
            continue
        if word == "though" and index + 1 < len(tokens) and tokens[index + 1] == ",":
            continue
        if word == "while":
            following = tokens[index + 1:index + 7]
            if not any(w in following for w in ("it", "the", "this", "a", "an", "its")):
                continue
        end = len(tokens)
        for position in range(index + 1, len(tokens)):
            if tokens[position] in {",", ".", "!", "?", ";"} or _contrast_at(tokens, position):
                end = position
                break
        # A leading concessive phrase without a comma often ends at a new subject.
        if end == len(tokens) and index <= 2:
            for position in range(index + 3, min(len(tokens), index + 15)):
                if tokens[position] in {"it", "this", "there", "nevertheless", "still"}:
                    end = position
                    break
        for position in range(index + 1, end):
            weights[position] *= 0.55
    for index in range(len(tokens) - 2):
        if tokens[index:index + 3] in (["for", "all", "its"], ["in", "spite", "of"]):
            end = min(len(tokens), index + 13)
            for position in range(index + 3, end):
                if tokens[position] in {",", ";", ".", "but"}:
                    end = position
                    break
            for position in range(index + 3, end):
                weights[position] *= 0.6
    return weights


def _rating_score(text):
    score = 0.0
    ratings = list(re.finditer(
        r"\b(\d+(?:\.\d+)?)\s*(?:/|out\s+of)\s*(4|5|10|100)\b", text
    ))
    if ratings:
        match = ratings[-1]
        value = float(match.group(1))
        scale = float(match.group(2))
        if 0 <= value <= scale:
            fraction = value / scale
            return 4.0 if fraction >= 0.6 else -4.0
    star_match = re.search(
        r"\b(zero|one|two|three|four|five|[0-5])"
        r"(?:\s+and\s+a\s+half|\s*[½])?\s+stars?\b",
        text
    )
    if star_match:
        number_words = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
        number = star_match.group(1)
        value = number_words[number] if number in number_words else int(number)
        if "half" in star_match.group(0) or "½" in star_match.group(0):
            value += 0.5
        score += 3.5 if value >= 2.5 else -3.5
    grade_match = re.search(r"\b(?:grade|rating)\s*:\s*([a-f])([+-]?)(?:\s|$|[.,;])", text)
    if grade_match:
        score += 3.5 if grade_match.group(1) in {"a", "b"} else -3.5
    return score


def _fallback(tokens, score, events):
    joined = " ".join(tokens)
    negative_patterns = (
        r"\bwhy (?:would|should|does|did) (?:anyone|anybody|someone)\b",
        r"\bwhat (?:was|is|were) .* thinking\b",
        r"\bhow did .* get made\b",
        r"\bif only\b",
        r"\bshould have\b",
        r"\bcould have\b",
        r"\bwould rather\b",
        r"\bspare (?:us|me|yourself)\b",
        r"\bnot much\b",
        r"\bnot even\b",
        r"\bso what\b",
        r"\bwho needs\b",
        r"\bwhat a waste\b",
        r"\bnot for everyone\b",
    )
    if any(re.search(pattern, joined) for pattern in negative_patterns):
        return "negative"
    if events:
        last_value = events[-1][2]
        if abs(last_value) >= 0.4:
            return "positive" if last_value > 0 else "negative"
    return "positive" if score >= 0 else "negative"


def predict(state) -> dict:
    if isinstance(state, str):
        text = state
    else:
        # The task's runtime state is a sentence. This also handles a missing
        # sentence without changing the required return type.
        text = "" if state is None else str(state)

    normalized = _normalize(text)
    tokens = re.findall(r"[a-z]+|\d+(?:\.\d+)?|[.,;:!?()/]", normalized)
    tokens = [_SPELLING.get(token, token) for token in tokens]

    if not tokens:
        return {"answer": "positive"}

    events, protected = _collect_events(tokens)
    modified = [
        _modify_event(event, tokens, protected, events)
        for event in events
    ]
    concession_weights = _concession_weights(tokens)
    contrasts = [
        index for index in range(len(tokens))
        if _contrast_at(tokens, index) and index not in protected
    ]

    weights = [1.0] * len(tokens)
    if contrasts:
        # Usually the clause following "but" contains the final judgment.
        last = contrasts[-1]
        earlier = [event for event in modified if event[0] < last]
        later = [event for event in modified if event[0] > last]
        earlier_score = sum(event[2] for event in earlier)
        later_positive = [event for event in later if event[2] > 0.25]
        cosmetic_exception = (
            earlier_score < -1.0
            and later_positive
            and all(event[3] for event in later_positive)
            and not any(event[2] < -0.5 for event in later)
        )
        before_weight = 0.85 if cosmetic_exception else 0.45
        after_weight = 0.8 if cosmetic_exception else 1.5
        for index in range(len(tokens)):
            weights[index] *= before_weight if index < last else after_weight
        # An opening "but" does not make the whole sentence artificially stronger.
        if last <= 1:
            weights = [1.0] * len(tokens)

    total = 0.0
    weighted_events = []
    for start, end, value, aspect in modified:
        position = min(start, len(tokens) - 1)
        value *= weights[position] * concession_weights[position]
        value *= 0.93 + 0.14 * (position / max(1, len(tokens) - 1))
        total += value
        weighted_events.append((start, end, value, aspect))

    total += _rating_score(normalized)

    # These constructions express disappointed expectations even when their
    # object is not in the sentiment lexicon.
    joined = " ".join(tokens)
    if re.search(r"\b(?:all|much) (?:the )?(?:effort|talent|potential) .* (?:wasted|squandered)\b", joined):
        total -= 1.0
    if re.search(r"\b(?:more|much) (?:is |was )?(?:promised|promises) than .*deliver", joined):
        total -= 1.5
    if re.search(r"\b(?:not|never) (?:quite )?(?:lives|live|lived) up to\b", joined):
        total -= 2.0
    elif re.search(r"\b(?:lives|live|lived) up to (?:its |the )?(?:promise|potential|expectations|hype)\b", joined):
        total += 2.0
    if re.search(r"\b(?:does|do|did) not (?:seem to )?(?:know|decide) (?:what|whether)\b", joined):
        total -= 1.5
    if re.search(r"\b(?:i|we) (?:want|wanted|wish|wished) to (?:like|love|enjoy)\b", joined):
        total -= 1.8

    if total > 0.12:
        answer = "positive"
    elif total < -0.12:
        answer = "negative"
    else:
        answer = _fallback(tokens, total, weighted_events)
    return {"answer": answer}