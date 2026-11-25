import re
import math
import unicodedata
from bisect import bisect_left

_WORDS = {}
_PHRASES = {}


def _normalize(text):
    text = unicodedata.normalize("NFKC", text).lower()
    text = text.translate(str.maketrans({
        "\u2019": "'", "\u2018": "'", "\u201b": "'",
        "\u201c": '"', "\u201d": '"', "`": "'",
        "\u2014": ";", "\u2013": "-", "\u2026": " ... "
    }))
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"\b([a-z]+)\s+n\s*'\s*t\b", r"\1n't", text)
    text = re.sub(r"\b([a-z]+)\s+'(s|re|ve|ll|d|m)\b", r"\1'\2", text)
    text = re.sub(r"\b([a-z]+)n\s*'\s*t\b", r"\1n't", text)
    text = re.sub(r"-{2,}", " ; ", text)
    text = text.replace("-", " ")
    return text


def _tokens(text):
    return re.findall(r"[a-z]+(?:'[a-z]+)*|\d+(?:\.\d+)?|[.!?,;:()/]", _normalize(text))


def _add_words(score, words):
    for word in words.split():
        _WORDS[word] = float(score)


def _add_phrases(score, phrases):
    for phrase in phrases.split("|"):
        seq = tuple(_tokens(phrase.strip()))
        if seq:
            _PHRASES[seq] = float(score)


_add_words(3.5, """
masterpiece masterpieces flawless perfection transcendent
""")
_add_words(3.1, """
excellent outstanding superb magnificent phenomenal exceptional
""")
_add_words(2.8, """
brilliant wonderful terrific fantastic fabulous marvelous marvellous
amazing astonishing astounding gorgeous breathtaking spellbinding riveting
unforgettable glorious awesome
""")
_add_words(2.5, """
great beautiful delightful hilarious fascinating engrossing mesmerizing
mesmerising dazzling stunning spectacular extraordinary exquisite
exhilarating enchanting triumphant
""")
_add_words(2.2, """
entertaining enjoyable compelling impressive inventive imaginative
creative ingenious intelligent witty poignant moving touching affecting
powerful profound insightful thoughtful satisfying rewarding charming
thrilling lovely heartfelt heartwarming heartwrenching inspiring
uplifting excellentness
""")
_add_words(1.9, """
good funny engaging absorbing appealing amusing pleasing pleasurable
effective convincing believable memorable exciting clever smart
original fresh lively vibrant dynamic energetic spirited magical
seductive beguiling bewitching hypnotic haunting resonant meaningful
graceful elegant eloquent artful assured accomplished polished
honest genuine authentic humane sincere sensitive perceptive
provocative enlightening illuminating revelatory audacious fearless
daring brave courageous unique distinctive timeless rich
""")
_add_words(1.6, """
solid competent confident warm affectionate attractive likable likeable
lovable loveable endearing winsome tender subtle nuanced intricate
astute observant incisive sharp satirical playful whimsical
rousing stirring visceral vivid colorful colourful vibrant
ambitious bold unflinching uncompromising unpretentious
unaffected understated literate lyrical poetic fluent fluid
coherent cohesive realistic credible plausible revealing informative
educational instructive involving absorbing intriguing interesting
chilling unsettling suspenseful tense taut brisk nimble deft skillful
skilful skillfully skilfully masterful masterfully expert expertly
accomplishment achievement triumph success successful succeeds
""")
_add_words(1.2, """
decent fine nice pleasant watchable serviceable sturdy capable
professional commendable admirable admirable noble valid worthwhile
useful important relevant significant engagingly thoughtfully
delicately gracefully elegantly eloquently artfully vividly
convincingly beautifully wonderfully brilliantly superbly excellently
magnificently gloriously gorgeously lovingly sensitively
charmingly wittily humorously amusingly delightfully
evocative expressive atmospheric atmosphericness intimate personal
human humane humanistic hopeful buoyant upbeat optimistic
refreshing inventive originality imagination intelligence
warmth affection sincerity honesty authenticity humanity
subtlety complexity richness depth resonance vitality energy
wit humor humour laughs laughter pleasure enjoyment entertainment
""")
_add_words(0.8, """
adequate okay ok fair acceptable satisfactory modest simple
earnest promising ambitious potential promise ambition
quirky offbeat eccentric idiosyncratic unusual unconventional
challenging meditative reflective introspective contemplative pensive
nostalgic nostalgia gritty gutsy raw earthy unvarnished unsparing
scary frightening creepy disturbing harrowing heartbreaking bittersweet
sad melancholy tragic emotional emotion emotions
romantic sensual sexy sensuality sexuality
campy camp screwball madcap wild riotous raucous
surprising surprise surprises unexpected unpredictable
inspiration respect respectfulness sympathetic empathy compassion
heart soul spirit tension suspense thrills thrill impact
integrity dignity merit merits insight insights
""")
_add_words(0.4, """
familiar fanciful stylized stylised experimental epic grand spectacle
bleak dark grim savage intense intensity confrontational confronts
novel novelty literary theatrical operatic lush lavish
ambitions promises occasionally sometimes humanity
""")

_add_words(3.5, "best greatest")
_add_words(1.8, "better")
_add_words(2.1, "enjoy enjoys enjoyed enjoying")
_add_words(2.3, "delight delights delighted adore adores adored")
_add_words(2.2, "love loved")
_add_words(1.1, "loves loving")
_add_words(1.8, "entertain entertains entertained amuse amuses amused")
_add_words(1.6, "please pleases pleased appreciate appreciates appreciated")
_add_words(1.9, "impress impresses impressed captivate captivates captivated captivating")
_add_words(2.1, "marvel marvels dazzle dazzles astonish astonishes amaze amazes")
_add_words(1.5, "admire admires admired admireable recommend recommends recommended")
_add_words(1.5, "engage engages engaged move moves moved touch touches touched")
_add_words(1.5, "resonate resonates linger lingers stirring")
_add_words(1.2, "charm charms charmed chuckles chuckle laugh laughing")
_add_words(1.4, "works spark sparkle sparkles sparkling zest zesty zippy")
_add_words(1.2, "fun enjoyment")
_add_words(2.3, "fun")
_add_words(2.6, "perfect")
_add_words(1.4, "gem")
_add_words(1.2, "beauty elegance grace")
_add_words(0.7, "happily fortunately luckily")
_add_words(0.8, "sweet sweetness cute")
_add_words(1.4, "delicious deliciously")

_add_words(-3.7, "worst abysmal atrocious execrable")
_add_words(-3.2, """
unwatchable unbearable insufferable intolerable abomination travesty
""")
_add_words(-2.9, """
terrible awful horrible horrid dreadful lousy wretched pathetic
garbage rubbish crap crappy stinker stinkers
""")
_add_words(-2.6, """
boring tedious dull unfunny humorless humourless
disappointing disappointment disappoints disappoint disappointed
disastrous inept incompetent ineptitude incompetence
embarrassing embarrassment disgrace disgraceful
misfire misfires botched bungled
sucks suck sucked stinks stink
""")
_add_words(-2.3, """
bad worse poor weak boringly dreary lifeless soulless
painful excruciating torturous interminable numbing benumbing
annoying irritating grating obnoxious repulsive repugnant repellent
revolting disgusting offensive hideous ugly
stupid dumb idiotic moronic witless brainless
vapid vacuous insipid empty hollow sterile inert
contrived cliched cliche cliches hackneyed trite banal
pretentious ponderous plodding sluggish lethargic listless
uninspired unimaginative unoriginal uninvolving unengaging
uninteresting unappealing charmless unlikable unlikeable
unconvincing incoherent incomprehensible unintelligible
unrewarding unsatisfying dissatisfying unsatisfactory
underwhelming disappointing unimpressive forgettable unmemorable
pointless purposeless worthless useless unnecessary
wasted waste wastes wasting
misguided misbegotten miscalculation miscalculations
sloppy lazy careless amateurish clumsy inelegant
overwrought overblown overdone bloated overlong
""")
_add_words(-1.9, """
flat wooden stiff stilted mechanical robotic artificial phony fake
muddled muddle muddles messy mess disjointed choppy haphazard
confusing confused convoluted illogical implausible preposterous
ludicrous ridiculous nonsensical nonsense absurd
shallow superficial simplistic unsubtle heavyhanded hamfisted hamhanded
derivative formulaic predictable repetitive redundant recycled
retread retreads rehash rehashes reheated tired stale staleness
pedestrian pedantic prosaic mediocre mediocrity ordinary routine
bland blandness dreariness drabness drab dour joyless mirthless
mawkish maudlin cloying saccharine schmaltzy sappy soppiness
cutesy twee preciousness schmaltz
smug smugness pompous pompousness bombastic bombast
condescending condescension patronizing patronising
manipulative exploitative dishonest insincere cynical
mean nasty cruel tasteless crass vulgar tawdry tacky trash
childish juvenile infantile puerile puerility
inadequate ineffective ineffectual unsuccessful failed failure failing
falter falters faltering flounder flounders floundering
underdeveloped underwritten undercooked unfinished unpolished
overproduced overacted overacting overstuffed overwrought
unfocused unfocusedness unfocussed unfunniness
""")
_add_words(-1.5, """
unpleasant unsavory unsavoury irritatingly annoyingly
frustrating frustrated frustration frustrations
baffling befuddling bewildering muddledness
thin slight sketchy meager meagre paltry negligible
awkward awkwardness ungainly unwieldy cumbersome
forced strained labored laboured laborious belabored
dumbed glib facile facilely simplistic simplification
unrealistic unbelievable improbable implausibility
unmotivated arbitrary random rambling meandering aimless
uneven inconsistent inconsistency inconsistencies
flawed flaw flaws faults faulty
conventional unremarkable disposable disposablely forgettably
dated outdated antiquated derivative derivativeness
corny hokey cheesy kitschy kitsch
cheap cheapness cheaply lowbrow trashy junk junky
gross crude crudity rude crudeness
shrill abrasive sour sourness
gratuitous gratuitously excess excessive excesses
fatuous vacuity banalities banality contrivance contrivances
annoy annoyance irritate irritation bother bothers bothersome
tedium boredom snooze snoozer snore yawn yawner yawns
regret regrets regrettable regrettably
""")
_add_words(-1.0, """
slow slowness sluggishly drag drags dragging draggy
somber sombre depressing depressed downbeat
dry chilly cold distant detached remote impersonal
sentimental sentimentality sentimentalism affected mannered
mannerisms mannerism precious arty artsy
cynicism cynically pessimistic pessimism
violently brutal brutality bleakness
unsettled unsatisfactorily
weakness weaknesses limited limitations
unambitious unimportant insignificant
unnecessary unnecessarily
fluff fluffy flimsy lightweight weightless
disconnected disconnection diversionary distracting distraction
trouble troubles troubled problematic problems problem
quibble quibbles reservations reservation
uncomfortable discomfort uncertain uncertainty
""")
_add_words(-1.8, "bore bores bored hate hates hated")
_add_words(-2.5, "loathsome loathe loathed detest detested")
_add_words(-2.1, "dud duds bust misfired misfiring ruin ruins ruined")
_add_words(-1.5, "fail fails lacks lack lacking devoid deficient deficit")
_add_words(-1.2, "unfortunately sadly alas sorry")
_add_words(-2.0, "squander squanders squandered squandering")
_add_words(-2.0, "lazy lazily sloppily ineptly incompetently clumsily")
_add_words(-2.0, "mediocre average")
_add_words(-1.2, "silly silliness absurdity")
_add_words(-1.2, "overrated")
_add_words(2.0, "underrated")
_add_words(1.0, "worth")

# Neutral phrases prevent plot vocabulary and genre names from being
# mistaken for evaluations of the film.
_add_phrases(0, """
special effects | special effect | practical effects | sound effects |
great depression | great war | great britain | great expectations |
good guy | good guys | bad guy | bad guys | bad boy | bad boys |
bad girl | bad girls | good girl | good girls |
good cop | bad cop | good and evil | good versus evil |
love story | love stories | love triangle | love affair |
in love | falls in love | fall in love | falling in love |
romantic comedy | romantic comedies | romantic drama |
disaster movie | disaster film | horror movie | horror film |
dark comedy | black comedy | dark humor | dark humour |
comic book | comic books | funny thing | moving picture | moving pictures |
cold war | cold blood | cold blooded | dead body | dead bodies |
death scene | gross out | gross out comedy |
mean streets | little women | pretty woman |
for good | as well as | as well | works by | works of |
works with | works for | works at | works on |
matter of fact | a matter of time | out of the blue |
a good deal | a great deal | a good many | a great many |
good intentions | best intentions | high hopes | lofty ambitions
""")

_add_phrases(4.2, """
one of the best | among the best | one of the finest |
one of the greatest | an absolute masterpiece | a true masterpiece |
a minor masterpiece | pure cinematic magic |
two thumbs up | highest recommendation
""")
_add_phrases(3.4, """
must see | must watch | not to be missed | do not miss |
don't miss | cannot be missed | can't be missed |
a little gem | a real gem | a rare gem | an absolute delight |
a complete delight | a sheer delight | a pure delight |
a total delight | sheer brilliance | sheer joy | pure joy |
pure pleasure | pure entertainment | cinematic gold |
tour de force | tour-de-force |
work of art | work of genius | stroke of genius |
a knockout | a knock out | a home run |
best of the year | finest of the year | film of the year |
movie of the year | a triumph | an unqualified success
""")
_add_phrases(2.7, """
well made | well crafted | well acted | well directed |
well written | well performed | well executed | well conceived |
well paced | well observed | well realized | well realised |
well worth | worth seeing | worth watching | worth a look |
worth the trip | worth the price | worth your time |
worth the effort | worth seeking out | worth checking out |
highly recommended | wholeheartedly recommend | heartily recommend |
strongly recommend | go see it | go and see it |
a pleasure to watch | a joy to watch | a delight to watch |
pleasure to behold | joy to behold | feast for the eyes |
visual feast | visually stunning | visually striking |
visually dazzling | visually splendid | visually gorgeous |
beautifully shot | beautifully filmed | beautifully made |
beautifully acted | beautifully written | beautifully crafted |
superbly acted | superbly directed | wonderfully acted |
wonderfully entertaining | hugely entertaining |
highly entertaining | thoroughly enjoyable |
laugh out loud | laugh aloud | laugh riot | laugh a minute |
laugh your head off | laugh yourself silly |
laugh until you cry | funny as hell |
edge of your seat | on the edge of my seat |
keeps you guessing | keeps us guessing |
packs a punch | packs an emotional punch |
emotionally powerful | emotionally resonant |
deeply moving | deeply affecting | genuinely moving |
heart and soul | heart in the right place |
hard to resist | difficult to resist | impossible to resist |
hard not to like | hard not to love | impossible not to like |
impossible not to love | impossible to dislike |
a cut above | head and shoulders above |
breath of fresh air | fresh and original |
thought provoking | mind blowing | eye opening |
pleasant surprise | welcome surprise | pleasant diversion |
a winner | a winning | a keeper | a winner's |
hits the mark | hits the spot | hits all the right notes |
delivers the goods | delivers on its promise |
lives up to its promise | lives up to expectations |
does not disappoint | doesn't disappoint |
never disappoints | never fails to entertain |
never fails to engage | never fails to amuse
""")
_add_phrases(1.8, """
a lot of fun | lots of fun | great fun | good fun |
silly fun | dumb fun | mindless fun | harmless fun |
goofy fun | giddy fun | guilty pleasure | guilty pleasures |
good time | great time | grand time | fine time |
a fun ride | a wild ride | a good ride | an enjoyable ride |
a fun movie | a fun film |
good enough | funny enough | entertaining enough |
more than adequate | more than satisfactory |
better than average | above average |
not half bad | not too bad | not all bad | not so bad |
not a total loss | not a complete loss |
good but not great | funny but not hilarious |
far from a failure | far from terrible |
no ordinary | no mere | anything but ordinary |
nothing short of brilliant | nothing short of amazing |
nothing short of wonderful | nothing less than brilliant |
nothing less than extraordinary |
nothing but fun | nothing but pleasure | nothing but praise |
no small achievement | no small feat |
never a dull moment | never boring | never dull |
rarely boring | never less than entertaining |
never less than compelling |
can't go wrong | cannot go wrong |
couldn't be better | could not be better |
never been better | never looked better |
couldn't ask for more | could not ask for more |
what more could you want | what more can you ask |
what's not to like | what is not to like |
what's not to love | what is not to love |
against the odds | against all odds |
surprisingly effective | surprisingly good |
better than expected | exceeds expectations |
a welcome addition | a welcome change |
holds your attention | held my attention |
holds our attention | holds up well |
gets it right | gets things right | gets the job done |
does the job | does its job |
has its charms | has its moments | has a lot going for it |
has much to offer | much to recommend |
nothing wrong with | no complaints |
easy to like | easy to enjoy |
love letter | labour of love | labor of love |
slow burn | slow burning | dry wit | dry humor | dry humour |
old fashioned charm | self deprecating | self aware |
down to earth | larger than life | tongue in cheek |
straight from the heart | wears its heart on its sleeve |
brings to life | brings it to life | brings them to life |
touch of genius | sense of wonder |
appealing cast | engaging cast | strong cast | fine cast |
winning performance | winning performances |
strong performance | strong performances |
fine performance | fine performances |
first rate | top notch | top drawer | top flight |
finely tuned | finely crafted | sure footed |
sure handed | fast paced | quick witted | razor sharp |
wickedly funny | wickedly amusing | wickedly entertaining
""")
_add_phrases(0.8, """
a few laughs | a few good laughs | some good laughs |
some laughs | some funny moments | a few funny moments |
a few good moments | enough laughs |
at its best | for once | for a change |
not perfect | not quite perfect | far from perfect |
not a masterpiece | not the best |
small pleasures | modest pleasures |
old fashioned | familiar territory |
no doubt | without a doubt | without question |
not without merit | not without charm | not without its charms |
not without interest | not without humor | not without humour
""")

_add_phrases(-4.2, """
one of the worst | among the worst | one of the dullest |
one of the most boring | worst of the year |
worst film of the year | worst movie of the year |
two thumbs down | an absolute disaster | a complete disaster |
a total disaster | an unmitigated disaster |
an utter disaster | an absolute mess | a complete mess |
a total mess | a colossal waste | utterly unwatchable |
a complete failure | a total failure |
insult to the audience | insult to your intelligence |
insults your intelligence | insult the intelligence |
insults the intelligence
""")
_add_phrases(-3.3, """
waste of time | waste your time | wastes your time |
wasting your time | waste my time | wasted my time |
waste of money | waste your money | wastes your money |
waste of talent | wasted talent | wastes the talents |
squandered talent | squandered talents |
time you'll never get back | time you will never get back |
hours you'll never get back | hours you will never get back |
don't bother | do not bother | don't waste |
do not waste | not worth seeing | not worth watching |
not worth your time | not worth the time |
not worth the effort | isn't worth seeing |
isn't worth watching | isn't worth your time |
isn't worth the effort | isn't worth the money |
not worth a look | not worth it | isn't worth it |
avoid at all costs | stay away from | give it a miss |
skip this one | skip it | pass on this one |
couldn't care less | could not care less |
couldn't be worse | could not be worse |
can't recommend | cannot recommend | couldn't recommend |
can not recommend | can't recommend it |
can't recommend this | cannot recommend it |
can't recommend this movie | cannot recommend this movie |
nothing to recommend | little to recommend |
nothing to recommend it | no redeeming qualities |
no redeeming value | no saving grace |
devoid of charm | devoid of humor | devoid of humour |
devoid of wit | devoid of imagination |
utterly pointless | utterly boring |
dead on arrival | dead in the water |
painfully unfunny | painfully dull | painfully boring |
excruciatingly dull | excruciatingly boring |
mind numbing | mind numbingly | brain dead |
as dull as dishwater | watching paint dry |
watch paint dry | like watching grass grow |
falls flat on its face | fall flat on its face |
an endurance test | exercise in tedium |
exercise in futility | exercise in boredom |
a chore to watch | a chore to sit through |
a pain to watch | painful to watch |
torture to watch | torture to sit through |
miserable excuse | poor excuse | sorry excuse |
barely watchable | virtually unwatchable |
wretched mess | incoherent mess | dreadful mess |
badly made | badly written | badly acted | badly directed |
poorly made | poorly written | poorly acted | poorly directed |
poorly conceived | poorly executed | poorly developed |
ineptly directed | ineptly written |
laughably bad | laughably inept |
so bad it's bad | so bad it is bad
""")
_add_phrases(-2.5, """
falls flat | fall flat | fell flat | fallen flat |
runs out of steam | run out of steam | ran out of steam |
outstays its welcome | overstays its welcome |
wears out its welcome | wears thin | wear thin |
goes nowhere | go nowhere | going nowhere |
leads nowhere | lead nowhere |
goes on forever | goes on and on | goes through the motions |
going through the motions | by the numbers | by the book |
paint by numbers | paint by number | connect the dots |
style over substance | style without substance |
all style and no substance | all style no substance |
much ado about nothing | sound and fury signifying nothing |
nothing new | nothing original | nothing special |
nothing interesting | nothing worthwhile | nothing of interest |
nothing much | nothing more than | little more than |
not much more than | no more than |
no fun | not fun | isn't fun | not funny |
no laughs | few laughs | precious few laughs |
little humor | little humour | little wit |
short on laughs | short on humor | short on humour |
short on wit | short on imagination |
lacking in imagination | lacking in originality |
lacking in substance | lacking in charm |
a lack of imagination | a lack of originality |
lack of substance | lack of suspense | lack of tension |
lacks the charm | lacks the wit | lacks the imagination |
not enough laughs | not enough fun |
has little to offer | has nothing to offer |
offers little | offers nothing |
leaves much to be desired | leaves a lot to be desired |
leaves you cold | left me cold | leaves me cold |
left us cold | leaves us cold |
neither here nor there | neither fish nor fowl |
less than compelling | less than satisfying |
less than convincing | less than entertaining |
less than interesting | less than funny |
better left unseen | better off without |
better than nothing | no better than |
not much better than | not any better than |
more of the same | same old thing | same old story |
same old same old | been there done that |
seen it all before | seen this all before |
seen it before | seen this before |
not a good movie | not a good film |
not very good | isn't very good | not particularly good |
not especially good | not much good |
not very funny | not particularly funny |
not especially funny | isn't very funny |
not very interesting | not particularly interesting |
not particularly entertaining | not very entertaining |
doesn't work | does not work | never works |
doesn't deliver | does not deliver |
fails to deliver | failed to deliver |
fails to engage | fails to entertain |
fails to convince | fails to satisfy |
tries too hard | trying too hard | tried too hard |
too hard to follow | hard to follow | difficult to follow |
impossible to follow | hard to care | difficult to care |
impossible to care | hard to stay awake |
struggles to engage | struggles to entertain |
too clever for its own good | too cute for its own good |
too long | far too long | way too long |
too slow | far too slow | too little too late |
too much of a mess | too much going on |
not nearly enough | simply not enough |
heavy handed | ham fisted | ham handed |
self indulgent | self important | self satisfied |
self congratulatory | self aggrandizing |
mean spirited | mean spirit | one note |
one dimensional | two dimensional | paper thin |
thinly drawn | thinly written | half baked | half assed |
half hearted | halfhearted | slap dash |
ill conceived | ill advised | ill executed |
ill judged | ill suited | ill fitting |
low rent | bottom of the barrel | rock bottom |
straight to video | direct to video |
dull as dishwater | dull as dirt |
going downhill | went wrong | goes wrong |
what went wrong | misses the mark | miss the mark |
misses the point | missed opportunity | missed opportunities |
lost opportunity | squandered opportunity |
lost in translation | lost its way | loses its way |
disappointing mess | dull mess |
a bad joke | bad taste | leaves a bad taste |
bad acting | bad writing | bad dialogue | bad direction |
weak script | weak screenplay | weak dialogue |
wooden acting | wooden performances |
stilted dialogue | clunky dialogue | clunky script |
why bother | who cares | who could care |
who needs | what's the point | what is the point
""")
_add_phrases(-1.5, """
only good thing | only saving grace | sole saving grace |
only redeeming quality | only redeeming feature |
only bright spot | few bright spots |
a bit of a mess | something of a mess |
at best | little else | too familiar |
overly familiar | overly sentimental | overly simplistic |
too sentimental | too predictable | too contrived |
too obvious | too silly | too stupid | too dumb |
too smug | too slick | too earnest |
overly earnest | overly ambitious |
trying to be funny | tries to be funny |
tries to be clever | tries to be smart |
wants to be funny | wants to be clever |
strains for laughs | strained humor | forced humor |
forced humour | cheap laughs | cheap thrills |
a pale imitation | pale imitation | pale shadow |
tired formula | tired cliches | tired old |
less interesting | less entertaining | less compelling |
less satisfying | below average |
bare minimum | merely adequate | barely adequate |
merely competent | merely watchable |
all over the place | uneven mess |
not for everyone | not for everybody |
hard to recommend | difficult to recommend |
cannot quite | can't quite |
good idea on paper | looks good on paper
""")
_add_phrases(-0.6, """
mixed bag | hit and miss | hit or miss |
a little slow | a bit slow | rough around the edges |
not entirely successful | not entirely convincing |
more ambitious than successful | more ambitious than effective |
not quite there | not quite right |
not as good | not nearly as good
""")

# Constructions where ordinary short-range negation is misleading.
_REGEX_RULES_RAW = [
    (r"\b(?:can't|cannot|couldn't|can not|could not) "
     r"(?:[a-z']+ ){0,3}recommend (?:[a-z']+ ){0,5}"
     r"(?:enough|too highly)\b", 3.8),
    (r"\b(?:can't|cannot|couldn't|can not|could not) "
     r"(?:[a-z']+ ){0,2}recommend (?:[a-z']+ ){0,3}highly enough\b", 3.8),
    (r"\b(?:so|such a) bad (?:movie |film )?"
     r"(?:that )?(?:it's|it is|its) (?:actually |almost |really )?"
     r"(?:good|fun|funny|entertaining)\b", 1.9),
    (r"\bso bad (?:that )?(?:it's|it is) (?:almost |actually )?"
     r"(?:good|fun|funny|entertaining)\b", 1.9),
    (r"\btoo (?:[a-z']+ ){0,3}for (?:its|their|his|her) own good\b", -2.6),
    (r"\b(?:not|isn't|wasn't|isnt|wasnt) (?:[a-z']+ ){0,3}"
     r"(?:good|funny|interesting|entertaining|compelling|clever|smart|"
     r"engaging|original|exciting|convincing|effective|scary|satisfying) enough\b", -2.7),
    (r"\b(?:no|not any) amount of (?:[a-z']+ ){0,7}"
     r"(?:can|could|will|would) (?:save|rescue|redeem)\b", -3.5),
    (r"\b(?:not even|even) (?:[a-z']+ ){0,5}"
     r"(?:can't|cannot|couldn't|can not|could not) "
     r"(?:save|rescue|redeem)\b", -3.5),
    (r"\bnot even (?:[a-z']+ ){0,5}(?:can|could) "
     r"(?:save|rescue|redeem)\b", -3.5),
    (r"\b(?:the )?best (?:thing|part) (?:[a-z']+ ){0,6}"
     r"(?:end credits|when it ends|when it's over|when it is over)\b", -3.7),
    (r"\b(?:one of|among) (?:[a-z']+ ){0,4}"
     r"(?:best|finest|greatest) (?:movies|films|comedies|thrillers|"
     r"documentaries|dramas|pictures)\b", 4.3),
    (r"\b(?:one of|among) (?:[a-z']+ ){0,4}"
     r"(?:worst|dullest|lousiest) (?:movies|films|comedies|thrillers|"
     r"documentaries|dramas|pictures)\b", -4.4),
    (r"\b(?:doesn't|does not|never) "
     r"(?:quite |really |ever )?live up to (?:its |the )?"
     r"(?:promise|potential|expectations|hype)\b", -2.9),
    (r"\b(?:doesn't|does not|never) "
     r"(?:quite |really |ever )?come (?:to life|alive|together)\b", -2.8),
    (r"\b(?:can't|cannot|couldn't|can not|could not) "
     r"(?:take|tear) (?:your|my|our|one's) eyes (?:off|away)\b", 3.0),
    (r"\b(?:can't|cannot|couldn't|can not|could not) "
     r"(?:wait for|wait until) (?:[a-z']+ ){0,4}"
     r"(?:end|ends|over)\b", -3.4),
    (r"\b(?:makes|made|make) (?:you|me|us) "
     r"(?:feel |really |actually )?(?:care|laugh|smile)\b", 2.3),
    (r"\b(?:doesn't|does not|never|can't|cannot|couldn't) "
     r"(?:make|makes|made) (?:you|me|us) "
     r"(?:feel |really |actually )?(?:care|laugh|smile)\b", -2.7),
    (r"\b(?:wish|wished) (?:[a-z']+ ){0,3}"
     r"(?:were|was|had been) better\b", -2.1),
]
_REGEX_RULES = [(re.compile(pattern), value) for pattern, value in _REGEX_RULES_RAW]

_PHRASE_INDEX = {}
for _seq, _value in _PHRASES.items():
    _PHRASE_INDEX.setdefault(_seq[0], []).append((_seq, _value))
for _first in _PHRASE_INDEX:
    _PHRASE_INDEX[_first].sort(key=lambda item: -len(item[0]))

_NEGATORS = {
    "not", "no", "never", "neither", "nor", "without", "hardly", "barely",
    "scarcely", "nothing", "nobody", "nowhere", "cannot", "can't", "couldn't",
    "don't", "doesn't", "didn't", "isn't", "aren't", "wasn't", "weren't",
    "won't", "wouldn't", "shouldn't", "hasn't", "haven't", "hadn't",
    "mustn't", "ain't", "cant", "couldnt", "dont", "doesnt", "didnt",
    "isnt", "arent", "wasnt", "werent", "wont", "wouldnt", "shouldnt",
    "hasnt", "havent", "hadnt"
}
_ABSENCE = {
    "lack", "lacks", "lacked", "lacking", "devoid", "deprived", "missing",
    "fails", "fail", "failed", "failing", "unable", "inability"
}
_BOUNDARY = {".", "!", "?", ";", ":", ",", "(", ")"}
_HARD_BOUNDARY = {".", "!", "?", ";", ":"}
_INTENSIFIERS = {
    "very": 1.27, "really": 1.22, "extremely": 1.5, "incredibly": 1.4,
    "utterly": 1.45, "totally": 1.35, "completely": 1.3, "absolutely": 1.5,
    "thoroughly": 1.3, "deeply": 1.3, "highly": 1.3, "so": 1.22,
    "quite": 1.1, "pretty": 1.04, "especially": 1.18, "particularly": 1.17,
    "exceptionally": 1.4, "enormously": 1.4, "immensely": 1.4,
    "hugely": 1.4, "genuinely": 1.2, "truly": 1.22, "decidedly": 1.2,
    "remarkably": 1.25, "surprisingly": 1.2, "refreshingly": 1.2,
    "unusually": 1.2, "uncommonly": 1.2, "extraordinarily": 1.4,
    "unbelievably": 1.4, "amazingly": 1.3, "astonishingly": 1.35,
    "staggeringly": 1.35, "spectacularly": 1.35, "stunningly": 1.3,
    "wonderfully": 1.25, "delightfully": 1.2, "beautifully": 1.2,
    "brilliantly": 1.3, "superbly": 1.3, "gloriously": 1.25,
    "terribly": 1.3, "awfully": 1.25, "horribly": 1.3,
    "painfully": 1.3, "excruciatingly": 1.35, "embarrassingly": 1.3,
    "laughably": 1.3, "ridiculously": 1.3, "relentlessly": 1.2,
    "unbearably": 1.35, "insufferably": 1.35, "interminably": 1.3,
    "frustratingly": 1.2, "disappointingly": 1.2,
    "consistently": 1.15, "uniformly": 1.2, "entirely": 1.15
}
_ATTENUATORS = {
    "somewhat": 0.65, "slightly": 0.62, "mildly": 0.65, "moderately": 0.7,
    "fairly": 0.8, "relatively": 0.8, "reasonably": 0.85,
    "occasionally": 0.65, "sometimes": 0.72, "intermittently": 0.6,
    "sporadically": 0.55, "partly": 0.7, "partially": 0.7,
    "almost": 0.65, "nearly": 0.7, "merely": 0.5, "just": 0.9,
    "potentially": 0.5, "supposedly": 0.35, "ostensibly": 0.4,
    "arguably": 0.85, "passably": 0.7
}
_ADVERB_MODIFIERS = set(_INTENSIFIERS) | set(_ATTENUATORS)
_EXTREME_PRAISE = {
    "perfect", "perfection", "masterpiece", "masterpieces", "great", "greatest",
    "best", "brilliant", "excellent", "flawless", "superb", "classic",
    "wonderful", "fantastic", "outstanding", "amazing"
}
_POSITIVE_QUANTITIES = {
    "fun", "humor", "humour", "wit", "laugh", "laughs", "laughter", "joy",
    "pleasure", "enjoyment", "entertainment", "heart", "soul", "spirit",
    "charm", "interest", "interesting", "originality", "imagination",
    "intelligence", "tension", "suspense", "excitement", "thrills", "depth",
    "substance", "merit", "merits", "insight", "insights", "energy", "vitality",
    "warmth", "emotion", "emotions", "feeling", "feelings", "reason",
    "redeeming", "good", "funny"
}


def _word_value(word):
    if word in _WORDS:
        return _WORDS[word]
    candidates = []
    if len(word) > 5:
        if word.endswith("ly"):
            candidates.extend((word[:-2], word[:-3] + "y" if word.endswith("ily") else ""))
        if word.endswith("ness"):
            base = word[:-4]
            candidates.extend((base, base[:-1] + "y" if base.endswith("i") else ""))
        if word.endswith("ing"):
            base = word[:-3]
            candidates.extend((base, base + "e"))
            if len(base) > 2 and base[-1:] == base[-2:-1]:
                candidates.append(base[:-1])
        if word.endswith("ed"):
            base = word[:-2]
            candidates.extend((base, base + "e"))
            if len(base) > 2 and base[-1:] == base[-2:-1]:
                candidates.append(base[:-1])
        if word.endswith("ies"):
            candidates.append(word[:-3] + "y")
        if word.endswith("es"):
            candidates.append(word[:-2])
    if len(word) > 4 and word.endswith("s") and not word.endswith("ss"):
        candidates.append(word[:-1])
    for candidate in candidates:
        if candidate in _WORDS:
            return 0.88 * _WORDS[candidate]
    if word.startswith("un") and len(word) > 6:
        base = word[2:]
        if base in _WORDS and _WORDS[base] > 0.8:
            return -0.95 * _WORDS[base]
    return 0.0


def _is_contrast(tokens, i):
    word = tokens[i]
    if word == "but":
        if i and tokens[i - 1] in {"anything", "nothing", "all", "help"}:
            return False
        if i + 1 < len(tokens) and tokens[i + 1] == "for":
            return False
        begin = max(0, i - 14)
        if "only" in tokens[begin:i] or "merely" in tokens[begin:i]:
            for j in range(begin, i - 1):
                if tokens[j] in {"not", "isn't", "wasn't"} and tokens[j + 1] in {
                    "only", "just", "merely"
                }:
                    return False
        return True
    if word == "yet":
        if i and tokens[i - 1] in {"not", "as", "has", "have", "had"}:
            return False
        if i + 1 < len(tokens) and tokens[i + 1] == "to":
            return False
        return i == 0 or tokens[i - 1] in _BOUNDARY or i > 4
    return word in {"however", "nevertheless", "nonetheless"}


def _negation_multiplier(tokens, start, end, value):
    lower = max(0, start - 6)
    for j in range(start - 1, lower - 1, -1):
        if tokens[j] in _BOUNDARY or _is_contrast(tokens, j):
            lower = j + 1
            break
    negations = []
    partial = False
    for j in range(lower, start):
        word = tokens[j]
        following = tokens[j + 1:start]
        if word in _NEGATORS:
            if word == "no" and following and following[0] in {
                "matter", "doubt", "wonder", "less", "other", "small"
            }:
                continue
            if word == "not" and following and following[0] in {
                "only", "just", "merely"
            }:
                continue
            if word == "nothing" and following and following[0] in {
                "but", "short", "less"
            }:
                continue
            if word == "without" and following:
                if following[0] in {"doubt", "question", "fail", "reservation", "reservations"}:
                    continue
                if following[:2] == ["a", "doubt"]:
                    continue
            if word in {"can't", "cannot", "couldn't"} and "help" in following[:2]:
                continue
            if word == "never" and following and following[0] == "before":
                continue
            if word in {"hardly", "barely", "scarcely"}:
                partial = True
            if any(w in {"entirely", "completely", "necessarily", "always", "quite"}
                   for w in following):
                partial = True
            negations.append((j, word))
        elif word in _ABSENCE:
            if word.startswith("fail"):
                if j + 1 >= start or tokens[j + 1] not in {"to", "at", "in"}:
                    continue
            negations.append((j, word))
        elif word == "less":
            if j > 0 and tokens[j - 1] in {"no", "or"}:
                continue
            negations.append((j, word))
            partial = True
        elif word == "from" and j > 0 and tokens[j - 1] == "far":
            negations.append((j, word))
        elif word == "but" and j > 0 and tokens[j - 1] == "anything":
            negations.append((j, word))
        elif word in {"little", "few"}:
            if j > 0 and tokens[j - 1] in {"a", "the", "his", "her", "their", "these"}:
                continue
            if value > 0 and any(w in _POSITIVE_QUANTITIES for w in tokens[start:end]):
                negations.append((j, word))
    if not negations:
        return 1.0
    # Parallel neither/nor is one negative construction, not a double negative.
    if any(w == "neither" for _, w in negations):
        negations = [(j, w) for j, w in negations if w != "nor"]
    if len(negations) % 2 == 0:
        return 0.85
    if value < 0:
        return -0.73 if not partial else -0.55
    if any(w in _EXTREME_PRAISE for w in tokens[start:end]):
        return -0.43
    return -0.68 if partial else -0.95


def _modifier_multiplier(tokens, start, end):
    multiplier = 1.0
    for j in range(max(0, start - 3), start):
        if any(t in _BOUNDARY for t in tokens[j:start]):
            continue
        word = tokens[j]
        distance = start - j
        if word in _INTENSIFIERS and distance <= 2:
            multiplier *= _INTENSIFIERS[word]
        elif word in _ATTENUATORS and distance <= 2:
            multiplier *= _ATTENUATORS[word]
    window = tokens[max(0, start - 4):start]
    if window[-2:] in (["a", "bit"], ["a", "little"], ["kind", "of"], ["sort", "of"]):
        multiplier *= 0.7
    if window[-2:] == ["more", "than"]:
        multiplier *= 1.15
    if window[-1:] == ["more"]:
        multiplier *= 1.1
    if window[-1:] == ["most"]:
        multiplier *= 1.2
    return min(1.9, max(0.3, multiplier))


def _clause_multiplier(tokens, start, end, contrasts):
    factor = 1.0
    if contrasts:
        preceding = [j for j in contrasts if j < start]
        following = [j for j in contrasts if j >= end]
        if preceding:
            last = preceding[-1]
            if not any(t in _HARD_BOUNDARY for t in tokens[last + 1:start]):
                factor *= 1.4
        if following:
            nxt = following[0]
            if not any(t in _HARD_BOUNDARY for t in tokens[end:nxt]):
                factor *= 0.62

    # Concessive subordinate clauses generally carry less evaluative weight.
    for j, word in enumerate(tokens):
        if word not in {"although", "though", "despite", "while", "albeit"}:
            continue
        if word == "though" and j >= len(tokens) - 2:
            continue
        if word == "while" and j > 2 and tokens[j - 1] not in _BOUNDARY:
            continue
        stop = len(tokens)
        for k in range(j + 1, len(tokens)):
            if tokens[k] in _BOUNDARY:
                stop = k
                break
        if j < start < stop:
            factor *= 0.66
        elif stop < start and j < 3:
            factor *= 1.15

    # Sentiment about the object of a comparison is not the main judgment.
    for j in range(max(0, start - 20), start):
        if tokens[j] != "than":
            continue
        if any(t in _HARD_BOUNDARY for t in tokens[j + 1:start]):
            continue
        if j and tokens[j - 1] in {"more", "less", "other"}:
            continue
        if any(t in {"better", "worse", "more", "less", "rather", "different"}
               for t in tokens[max(0, j - 12):j]):
            factor *= 0.32
            break
    for j in range(max(0, start - 9), start - 1):
        if tokens[j:j + 2] == ["instead", "of"]:
            if not any(t in _BOUNDARY for t in tokens[j + 2:start]):
                factor *= 0.35
                break

    # "For all its flaws, ..." explicitly concedes the flaws.
    for j in range(max(0, start - 7), start):
        if tokens[j:j + 3] in (["for", "all", "its"], ["for", "all", "the"]):
            if not any(t in _BOUNDARY for t in tokens[j:start]):
                factor *= 0.5
    return factor


def _extract_text(state):
    if isinstance(state, str):
        return state
    if isinstance(state, dict):
        for key in ("text", "sentence", "review", "content", "input"):
            if key in state and isinstance(state[key], str):
                return state[key]
        for value in state.values():
            if isinstance(value, str):
                return value
    if isinstance(state, (list, tuple)):
        return " ".join(x for x in state if isinstance(x, str))
    return "" if state is None else str(state)


def _rating_score(text):
    score = 0.0
    for match in re.finditer(
        r"\b(\d+(?:\.\d+)?)\s*(?:/|out of)\s*(4|5|10)\b", text
    ):
        rating = float(match.group(1))
        maximum = float(match.group(2))
        if rating <= maximum:
            fraction = rating / maximum
            if fraction >= 0.7:
                score += 3.5
            elif fraction >= 0.6:
                score += 1.5
            elif fraction <= 0.4:
                score -= 3.5
            else:
                score -= 0.7
    for match in re.finditer(r"\b(zero|one|two|three|four|five)\s+stars?\b", text):
        number = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5}[
            match.group(1)
        ]
        if number >= 3:
            score += 2.8
        elif number <= 1:
            score -= 3.2
        else:
            score -= 1.0
    return score


def predict(state):
    text = _extract_text(state)
    normalized = _normalize(text)
    tokens = _tokens(text)
    if not tokens:
        return {"answer": "positive"}

    n = len(tokens)
    candidates = []

    for i, token in enumerate(tokens):
        for sequence, value in _PHRASE_INDEX.get(token, ()):
            length = len(sequence)
            if tuple(tokens[i:i + length]) == sequence:
                candidates.append((i, i + length, value, 1))

    joined = " ".join(tokens)
    starts = []
    cursor = 0
    for token in tokens:
        starts.append(cursor)
        cursor += len(token) + 1

    for pattern, value in _REGEX_RULES:
        for match in pattern.finditer(joined):
            left = bisect_left(starts, match.start())
            right = bisect_left(starts, match.end())
            if left < right:
                candidates.append((left, right, value, 2))

    candidates.sort(key=lambda item: (
        -item[3], -(item[1] - item[0]), -abs(item[2]), item[0]
    ))
    occupied = [False] * n
    events = []
    for left, right, value, kind in candidates:
        if not any(occupied[left:right]):
            for j in range(left, right):
                occupied[j] = True
            if value:
                events.append((left, right, value, kind))

    for i, token in enumerate(tokens):
        if occupied[i]:
            continue
        value = _word_value(token)
        if not value:
            continue
        # Intensifying adverbs should not add their own opposite sentiment.
        if token in _ADVERB_MODIFIERS:
            nearby = False
            for j in range(i + 1, min(n, i + 3)):
                if tokens[j] in _BOUNDARY:
                    break
                if _word_value(tokens[j]):
                    nearby = True
                    break
            if nearby:
                continue
        if token == "works" and i + 1 < n and tokens[i + 1] in {
            "hard", "harder", "tirelessly"
        }:
            value = 0.2
        if token in {"love", "loves", "loving"}:
            if i and tokens[i - 1] in {"of", "about", "between", "their", "his", "her"}:
                value *= 0.35
        if token in {"mean", "cruel", "nasty", "ugly", "brutal"}:
            # These words frequently describe characters, not artistic quality.
            value *= 0.65
        if token in {"problem", "problems", "trouble", "troubles"}:
            if i and tokens[i - 1] in {"her", "his", "their", "personal", "family"}:
                value *= 0.15
        events.append((i, i + 1, value, 0))

    events.sort(key=lambda item: item[0])
    contrasts = [i for i in range(n) if _is_contrast(tokens, i)]
    total = _rating_score(normalized)
    positive = 0.0
    negative = 0.0
    repetitions = {}

    for start, end, base, kind in events:
        value = base
        value *= _negation_multiplier(tokens, start, end, value)
        value *= _modifier_multiplier(tokens, start, end)
        value *= _clause_multiplier(tokens, start, end, contrasts)

        prior = tokens[max(0, start - 6):start]
        if kind == 0 and value > 0:
            if any(w in {"tries", "trying", "attempts", "attempting", "aspires",
                         "aspiring", "wants", "wanted", "strives", "striving"}
                   for w in prior):
                if "to" in prior:
                    value *= 0.3
            if prior[-3:] in (
                ["could", "have", "been"], ["should", "have", "been"],
                ["might", "have", "been"], ["would", "have", "been"]
            ):
                value *= -0.65
            if prior[-2:] in (["supposed", "to"], ["meant", "to"]):
                value *= 0.25
            if "only" in prior[-3:] and any(
                t in {"good", "redeeming", "bright"} for t in tokens[start:end]
            ):
                value *= -0.6

        # "Too" usually criticizes excess, except for conventional praise
        # such as "too funny" or "too good to miss."
        if kind == 0 and "too" in prior[-2:] and base > 0:
            if tokens[start] in {
                "clever", "cute", "slick", "sweet", "earnest", "ambitious",
                "sentimental", "simple", "complex", "complicated", "precious"
            }:
                value = -abs(value) * 0.8

        key = tuple(tokens[start:end])
        count = repetitions.get(key, 0)
        repetitions[key] = count + 1
        if count:
            value *= 1.0 / math.sqrt(count + 1)

        total += value
        if value > 0:
            positive += value
        else:
            negative -= value

    # Evaluative constructions that need no sentiment adjective.
    if re.search(r"\b(?:i|we|you) (?:want|wanted|wish|wished) to like\b", joined):
        total -= 2.3
    if re.search(r"\b(?:not|isn't|wasn't) (?:[a-z']+ ){0,2}my cup of tea\b", joined):
        total -= 2.3
    if re.search(r"\b(?:my|our) cup of tea\b", joined) and "not" not in tokens:
        total += 1.3
    if re.search(r"\b(?:can|could|should) (?:do|have done) better\b", joined):
        total -= 1.5
    if re.search(r"\b(?:you|we) deserve better\b", joined):
        total -= 2.2
    if re.search(r"\b(?:save|saves|rescue|rescues|redeem|redeems) "
                 r"(?:the|this|a) (?:movie|film|picture)\b", joined):
        total -= 0.4
    if re.search(r"\b(?:nothing|little) (?:[a-z']+ ){0,2}"
                 r"(?:happens|happening)\b", joined):
        total -= 1.7
    if re.search(r"\b(?:all|just|only) (?:[a-z']+ ){0,2}"
                 r"(?:cliches|cliche|formula|filler)\b", joined):
        total -= 1.2
    if re.search(r"\b(?:yawn|zzz|zzzz|zzzzz)\b", joined):
        total -= 1.8

    # Imperatives are useful when the review is a short recommendation.
    if abs(total) < 1.0:
        if re.search(r"\b(?:see|watch|rent|catch) (?:it|this one)\b", joined):
            if re.search(r"\b(?:don't|do not|never|wouldn't|would not) "
                         r"(?:bother to )?(?:see|watch|rent|catch)\b", joined):
                total -= 2.0
            else:
                total += 0.8

    # Near-neutral reviews usually recommend a film if they contain some
    # pleasure and no substantial criticism.
    if abs(total) < 0.12:
        if negative > positive:
            total = -0.15
        else:
            total = 0.15

    return {"answer": "positive" if total >= 0 else "negative"}