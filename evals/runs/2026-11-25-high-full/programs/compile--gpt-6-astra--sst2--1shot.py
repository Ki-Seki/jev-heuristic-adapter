import re
import unicodedata
from functools import lru_cache

_WORDS = {}
_PHRASES = {}


def _words(value, text):
    for word in text.split():
        _WORDS[word] = float(value)


_words(4.0, """
masterpiece masterpieces masterful magnificent superb phenomenal flawless
""")
_words(3.2, """
excellent outstanding exceptional brilliant wonderful terrific fantastic fabulous
splendid marvelous marvellous amazing awesome exquisite breathtaking unforgettable
extraordinary astonishing astounding spectacular glorious sublime triumphant
hilarious uproarious riveting enthralling exhilarating mesmerizing mesmerising
spellbinding perfection
""")
_words(2.6, """
great best beautiful gorgeous stunning remarkable impressive fascinating compelling
absorbing engrossing captivating gripping thrilling delightful delight delights
delicious irresistible charming enchanting magical poignant moving touching
heartfelt heartwarming inspiring uplifting satisfying rewarding entertaining
enjoyable funny fun gem jewel treasure treat superbly bravura powerhouse
electrifying ravishing luminous resonant revelatory revelation inspired
""")
_words(2.0, """
good better fine wonderfulness memorable admirable accomplished achievement
accomplishments achievements intelligent smart clever witty wit humorous amusing
pleasing pleasant pleasure pleasures enjoyment enjoy enjoys enjoyed lovable
likable likeable endearing winsome appealing engaging involving convincing
affecting effective powerful potent strong solid polished elegant graceful
deft skillful skilful skilled expert expertly inventive imaginative creative
original authentic honest insightful perceptive illuminating enlightening
refreshing fresh vibrant lively spirited energetic buoyant effervescent exuberant
joy joyous joyful exuberance zest humanity humane warmth tenderness tender
sensitive thoughtful thoughtfulness meaningful profound depth nuanced subtle
lyrical poetic rich richness vivid stylish sophisticated sophistication
suspenseful exciting excitement rousing tense chilling scary terrifying
harrowing haunting daring bold audacious courageous brave visionary unique
distinctive important worthwhile worthy recommend recommended recommendation
recommended recommendations triumph triumphs success successful succeeds
succeed accomplishment mastery talented talentful finesse integrity
resonates resonate resonance wonder wondrous marvel marvels
""")
_words(1.4, """
entertain entertains entertained entertainment amuse amuses amused amusement
laugh laughs laughed laughing laughter chuckle chuckles chuckling giggles
smile smiles smiling grinning grin humor humour hilarity
charm charms appeal appeals admire admires admired admiration
interesting interest interested interests intriguing intrigued intrigue
fascinate fascinates fascinated captivate captivates captivated
impress impresses impressed engagingly engross enchant enchants
beauty grace elegance sumptuous lush lavish lovely pretty-looking
sharp crisp snappy nimble agile sprightly spry brisk breezy
competence craftsmanship artistry artful artistic artistry craft
skill skills intelligence imagination creativity inventiveness originality
insight insights nuance nuances subtlety poetry lyricism
reveal reveals revealing informative educational instructive revelation
credible believable realistic realism naturalistic convincingness
sincerity sincere honesty candid candor candour authenticity
humility compassionate compassion affectionate affection empathy empathetic
sympathetic sympatheticness sympathy humanistic humanism
unpretentious unsentimental uncompromising unaffected unforced understated
observant assured confident confidence assuredness restraint restrained
tasteful respectable respectful dignified dignity
tension suspense thrill thrills thrilled shocker
unsettling disturbing provocative provoking challenging stirring
biting incisive irreverent subversive satiric satirical satirically
offbeat quirky unconventional unorthodox unpredictable unpredictability
complex complexity layered textured texture textures
absorbs absorb absorbingness immersion immersive
vital vitality vigor vigour vigorous vivacious verve energy
spirit exuberantly infectious infectiousness intoxicating
dazzling dazzle dazzles dazzled dazzlingly
endearingness engagingness watchable accessible engrossment
decent neat enjoyable entertainingness
succeeds succeed worked works achievement
redeems redeemed redeem redeeming salvages saves saved
improve improves improved improvement improvements
overcomes overcome transcends transcend
underrated underappreciated
""")
_words(0.7, """
ambitious ambition ambitions promising promise promises potential
emotional emotion emotions romantic romance comical comic deadpan
surprising surprise surprises surprised unexpected unusual novelty
eccentric eccentricity quirk quirks quirkiness playful playfulness
modest modesty simple simplicity intimate intimacy delicate delicacy
earnest earnestness heartfeltly heart soul spirit
serious seriousness mature maturity adult maturely
competent adequate serviceable passable okay ok tolerable
cleanness economical efficient efficiency briskness
slick sleek colorful colourful colorfulness colourfulness
grand grandeur epic spectacle spectacleful handsome
sweet sweetness warm warmth gentle gentleness soothing
comfort comfortable comforting nostalgic nostalgia
optimistic optimism hopeful optimisticness
celebration celebrate celebrates celebratory
relevant relevance timely timeliness
interestingness instructive instructiveness
appeal novelty worth value valuable
loving love lovedness fond fondness liking
please pleased pleasingness positive positivity
welcome welcomed welcoming
respect respects respectable
sense coherence coherent lucid clarity clear
accomplish accomplishes achieved achieve achieves
crafted polishedness entertainmentvalue
potentially
""")
_words(0.3, """
adequacy fair familiarities touchingness human ambitiousness
experimental experiment experimentation daringness
bleak brutal stark raw gritty grit restrainedness
darkness grittyness disturbingness troubling horrifying
absurdity absurdist absurdism outrageous outlandish loopy wacky
childlike youthful youthfulness solemn solemnity
minor modestly commercial
""")

_words(-4.0, """
worst abysmal atrocious execrable unwatchable atrociously
""")
_words(-3.3, """
awful terrible horrible horrendous dreadful lousy appalling
boring bore bores bored boredom unfunny
stinker stinks stink sucks suck garbage rubbish crap crappy
abomination atrociousness travesty disaster disastrous
incoherent incomprehensible inept incompetent incompetence
unbearable intolerable insufferable unendurable
""")
_words(-2.7, """
bad worse poor poorly disappointing disappointed disappoint disappoints
disappointment disappointments letdown
dull dullness tedious tedium tiresome dreary lifeless listless
plodding ponderous leaden wooden stilted
stupid idiotic idiocy moronic brainless witless mindnumbing
humorless humourless joyless charmless soulless heartless
pretentious pretentiousness pompous sanctimonious
cloying mawkish maudlin saccharine
annoying annoyingness irritating irritation obnoxious
offensive insulting insult insults repulsive repellent repugnant disgusting
unappealing unengaging uninvolving uninteresting uninspired unimaginative
unconvincing unsatisfying dissatisfying unrewarding
forgettable unmemorable pointless worthless useless
derivative unoriginal contrived hackneyed cliched cliche cliches trite banal
lazy laziness amateurish amateurism shoddy sloppy sloppiness
waste wastes wasted wasting squander squanders squandered squandering
misfire misfires misfired dud duds turkey flop flops
embarrassing embarrassment cringeworthy cringe-worthy
overrated overblown overwrought overlong
vapid vacuous fatuous
""")
_words(-2.0, """
weak weakness weaknesses flat flatness
failure failures failed fails fail failing
mediocre mediocrity inferior substandard secondrate
unnecessary needless gratuitous gratuitousness
unfocused aimless aimlessness meandering meanders meander
drags dragging draggy interminable endless repetitive redundancy redundant
padded padding bloated bloat overstuffed overloaded overkill excessive
clumsy clumsiness clunky clunkiness awkward awkwardness ungainly unwieldy
muddled murky confused confusing confusion incoherence
implausible implausibility unbelievable unpersuasive unmotivated
predictable predictability formulaic formulaically
stale staleness tired routine generic pedestrian
limp inert inertia stagnant static dullard
shallow shallowly thin flimsy threadbare empty emptiness hollow
underwritten underdeveloped undeveloped overwritten
unremarkable undistinguished negligible insignificant
vacuity vapidity banality triviality trivial simplistic
patronizing condescending condescension preachy preachiness
moralizing sermonizing didacticism
cynical cynicism calculated mechanical mechanically robotic
dishonest dishonesty false falseness phony phoney fake fraudulent
manipulative manipulation exploitative exploitive
tasteless tastelessness vulgar vulgarity crude crudeness crass crassness
inane inanity dumb dumbness dimwitted doltish
sillyness ridiculous ridiculousness ludicrous laughable risible preposterous
puerile infantile childish juvenile
unpleasant unpleasantness distasteful objectionable
irresponsible regressive offensive offensiveness
painful painfully miserable misery
frustrating frustration frustrated aggravating
disjointed disconnected disorganized disorganised
raggedy haphazard careless carelessness unprofessional
uneven inconsistent inconsistency unfocusedness
hammy hamfisted hamhanded
cheesy corny hokey schmaltzy schmaltz sentimentality
unsubtle unsubtlety overdone overacted overacting
miscast miscasting misbegotten misguided misjudged mishandled mishmash
botched botches bungled bungles bungle
ruin ruins ruined ruining wreck wrecked
sabotage sabotages undermines undermine undermined
disservice dismal dismally
weakens weakened
annoy annoys annoyed annoyances annoyance irritates irritated irritate
irks irksome irritatingly grating grates grated
aggravates exasperating exasperation exasperated
tepid lukewarm
embarrassed embarrass embarrasses cringey cringy cringe cringing
detest detests detested loathe loathes loathed loathsome
loatheable hateful hated hatredful
unlikable unlikeable unlovable unsympathetic
unrewarding joylessness mirthless
forgettable forgettablely
""")
_words(-1.3, """
slow slowness sluggish sluggishness drag
mess messy messiness muddle muddles murk
convoluted convolution overcomplicated overcomplication
familiar familiarity formula formulas
conventional conventionality conventionalism
derivation recycled recycling rehash rehashed retread retreads
rehashes ripoff ripoffs imitation imitative
cheap cheapness tacky tackiness
bland blandness drab drabness colorless colourless
dry dryness stodgy stodginess stolid
soggy mushy gooey syrupy treacly sentimental
maudlinness mush sentimentality
baffling baffled bewildering bewilderment
strident shrill shouty screechy
portentous bombastic bombast pomp
artificial artificiality affected affectation affectedness
forced strained strain strains straining
problem problems problematic troublingly troublesome
flaw flaws flawed fault faults faulty
distraction distracting distracted distractions distract distracts
detracts detract detraction
misstep missteps mistake mistakes mistaken
fumble fumbles fumbled stumbling stumbles stumble
suffers suffer suffering
shortcoming shortcomings deficiency deficiencies deficient
lack lacks lacking lacked missing
limits limited limitations limiting
friction dissonance incongruous incongruity
lackadaisical indifference indifferent
depressing depressed dispiriting disheartening
unexciting excitementless
unfortunate unfortunately sadly alas regrettably regrettable regret regretted
hopeless hopelessness
frantic franticness frenetic
exhausting exhausted tiring weary wearisome
brutish abrasive nastiness nasty
repellently odious oafish
sickening queasy queasiness nauseating nauseous
strainedness flatly flatlining
unimpressive unamusing unentertaining
dated outmoded antiquated obsolete outworn
inconsequential insubstantial superficial superficiality shallowest
untidy untidiness unpolished
unsound unappealingness
inexplicable inexplicably
""")
_words(-0.6, """
silly silliness absurd bizarre weird ridiculousness
rough roughness ragged thinness sketchy sketchiness
sentimental sentimentality schmaltziness
excess excesses exploit exploitation
stiff stiffness chilly cold chilliness
numb numbness numbing
reluctant reluctance difficult difficulty difficulties
sour sourness bitter bitterness
unoriginality unsurprising unsurprisingly obvious obviousness
redundantly repetitive repetitiveness
contrivance contrivances coincidence coincidences
melodramatic melodrama melodramatics
gimmick gimmicks gimmicky
cutesy precious cuteness
inconsequentiality
hate hates
""")

_WORDS.update({
    "fun": 2.5, "funny": 2.6, "interesting": 2.1, "love": 0.5,
    "loved": 2.6, "liked": 1.8, "enjoy": 2.2, "enjoyed": 2.5,
    "silly": -0.7, "absurd": -0.5, "weird": -0.2,
    "sentimental": -0.5, "sentimentality": -1.4,
    "cynical": -0.8, "cynicism": -0.8, "melodrama": -0.2,
    "cold": -0.8, "difficult": -0.2, "darkness": 0.0,
    "slow": -1.1, "slowly": 0.0, "simple": 0.3, "minor": -0.2,
    "failure": -2.6, "failures": -2.6, "failed": -2.1, "fails": -2.1,
    "fail": -2.1, "lacks": -1.2, "lack": -1.2, "missing": -0.8,
    "work": 0.0, "works": 1.5, "worked": 1.1,
    "best": 3.1, "better": 2.3, "worst": -4.1, "worse": -3.1,
    "fine": 1.8, "poor": -2.3, "great": 3.0,
    "spectacle": 0.6, "spectacular": 2.7,
    "unsettling": 1.0, "disturbing": 0.7, "horrifying": 0.5,
    "depressing": -0.9, "painful": -1.6,
    "harrowing": 1.3, "haunting": 2.0, "scary": 1.2, "terrifying": 1.7,
    "brutal": 0.0, "bleak": 0.0, "sad": 0.0, "sadness": 0.0,
    "tragic": 0.0, "tragedy": 0.0, "evil": 0.0, "violent": 0.0,
    "violence": 0.0, "horror": 0.0, "horrific": -0.4,
    "death": 0.0, "dead": 0.0, "kill": 0.0, "killer": 0.0,
    "murder": 0.0, "fear": 0.0, "angry": 0.0, "anger": 0.0,
    "romance": 0.0, "romantic": 0.4, "heart": 0.7,
    "dark": 0.0, "light": 0.0, "real": 0.0, "new": 0.0,
    "novel": 0.0, "pretty": 0.0, "well": 0.0, "right": 0.0,
    "wrong": -1.2, "special": 1.4, "original": 1.7,
    "familiar": -0.6, "commercial": 0.0, "adult": 0.0,
    "serious": 0.3, "emotional": 0.9, "emotions": 0.3,
    "ambitious": 1.0, "ambition": 0.5, "ambitions": 0.4,
    "competent": 0.8, "adequate": 0.4, "passable": 0.4,
    "serviceable": 0.5, "tolerable": 0.3, "watchable": 1.2,
    "okay": 0.5, "ok": 0.5, "decent": 1.2,
    "slick": 0.4, "potential": 0.0, "potentially": 0.0,
    "clear": 0.0, "sense": 0.6, "limited": -0.5,
    "unreal": 0.6, "unpretentious": 1.8, "uncompromising": 1.4,
    "unpredictable": 1.8, "unconventional": 1.2,
    "uncomfortable": 0.0, "unrelenting": 0.0,
    "heartbreaking": 1.6, "heartbroken": 0.0, "devastating": 1.1,
    "searing": 1.6, "piercing": 1.0, "gutless": -2.0,
    "mystery": 0.0, "mysterious": 0.2, "intrigue": 0.8,
    "mess": -2.7, "messy": -1.1, "repetitive": -2.2,
    "chaotic": -0.6, "chaos": -0.4,
    "tearjerker": 0.8, "tearjerking": 0.8,
    "underrated": 2.6, "overrated": -2.8,
    "nonexistent": -1.8, "nonentity": -1.5,
    "refreshingly": 1.0, "surprisingly": 0.0,
    "unfortunately": -1.1, "fortunately": 0.7, "thankfully": 0.6,
    "succeeds": 2.1, "successful": 2.0, "success": 1.8,
    "ineffective": -2.4, "affecting": 2.4,
    "lackluster": -2.7, "lacklustre": -2.7,
    "laughably": -1.7, "laughable": -2.3,
    "notable": 1.0, "noteworthy": 1.4,
    "deft": 2.0, "accomplished": 2.2, "expert": 1.7,
    "talent": 0.7, "talented": 1.6,
    "maladroit": -2.2, "mediocre": -2.4, "mediocrity": -2.4,
    "insipid": -2.7, "sterile": -2.2, "sterility": -1.8,
    "pathetic": -2.6, "pitiful": -2.3, "wretched": -3.0,
    "asinine": -2.8, "abominable": -3.3, "deplorable": -2.7,
    "lame": -2.8, "lameness": -2.6, "limps": -2.0,
    "drivel": -3.0, "twaddle": -2.7, "bilge": -2.8,
    "pablum": -2.3, "pap": -2.0, "baloney": -1.9,
    "nonsense": -1.7, "nonsensical": -1.9,
    "hooey": -1.8, "hooeyness": -1.8,
    "unfulfilled": -1.6, "unfulfilling": -2.1,
    "gratifying": 2.3, "fulfilling": 2.0,
    "refreshment": 1.0, "refresh": 0.7,
    "winning": 2.1, "winner": 2.4, "winners": 2.0,
    "loser": -1.4, "losers": -0.8,
    "loses": -0.7, "lost": 0.0,
    "perfunctory": -2.1, "perfunctorily": -1.7,
    "arbitrary": -1.5, "arbitrariness": -1.5,
    "disposable": -1.6, "dispirited": -1.1,
    "draining": -1.2, "enervating": -2.0, "enervated": -1.5,
    "invigorating": 2.3, "invigorated": 1.5,
    "evocative": 2.0, "evokes": 0.6,
    "transporting": 2.3, "transcendent": 2.7,
    "transcendental": 1.3, "transfixing": 2.3,
    "rhapsodic": 1.6, "rapturous": 2.6,
    "rapture": 2.1, "exuberant": 2.1,
    "delirious": 0.7, "deliriously": 0.7,
    "delightfully": 2.0, "wonderfully": 2.2,
    "beautifully": 2.1, "brilliantly": 2.6,
    "magnificently": 2.7, "gloriously": 2.2,
    "triumphantly": 2.3, "lovingly": 1.3,
    "tortuously": -2.1, "torturous": -2.6,
    "torture": -1.8, "tortured": -0.8,
    "punishing": -0.7, "punishment": -0.8,
    "sterling": 2.2, "sterlingly": 1.8,
    "merit": 1.0, "merits": 1.1, "meritorious": 1.7,
    "redeeming": 0.8, "redeemable": 0.5,
    "irredeemable": -2.4, "unsalvageable": -2.6,
    "enthrall": 2.0, "enthralls": 2.4,
    "enthralled": 2.5, "spellbound": 2.4,
    "seductive": 1.5, "seduces": 1.3,
    "seduced": 1.2, "alluring": 1.6,
    "allure": 1.1, "beguiling": 2.1,
    "beguiles": 1.8, "enchantment": 2.0,
    "disenchantment": -1.5, "disenchanted": -1.5,
    "fizz": 1.3, "fizzy": 1.5, "spark": 1.1,
    "sparkle": 1.7, "sparkles": 1.9, "sparkling": 2.1,
    "sparkless": -1.8, "sparklessness": -1.8,
    "zippy": 1.5, "zestful": 1.7, "zesty": 1.5,
    "punchy": 1.6, "punch": 0.6,
    "gutty": 1.3, "gutsy": 1.6,
    "frivolous": -0.8, "frivolity": -0.4,
    "fluffy": -0.6, "fluff": -1.0,
    "lightweight": -0.7, "weightless": -0.7,
    "weighty": 0.4, "substantial": 1.2,
    "substance": 1.1, "substantive": 1.4,
    "passion": 1.2, "passionate": 1.7,
    "passionless": -2.1, "dispassionate": -0.2,
    "unconvincingly": -2.0, "unimpressed": -2.0,
    "underwhelming": -2.5, "underwhelmed": -2.3,
    "overwhelming": 0.6, "overwhelmed": 0.4,
    "pedantic": -1.9, "pedantry": -1.6,
    "insolent": -0.6, "insensitive": -1.7,
    "sensitivity": 1.3, "sensibility": 0.5,
    "foolish": -1.5, "foolishness": -1.3,
    "idiot": -1.0, "idiots": -0.8,
    "idiotically": -2.0,
})


def _normalize(text):
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")
    text = text.replace("&amp;", " and ").replace("&quot;", '"')
    text = text.replace("&#39;", "'").replace("&apos;", "'")
    text = text.replace("<br />", " . ").replace("<br>", " . ")
    text = re.sub(r"\b(\w+)\s+n\s*'\s*t\b", r"\1n't", text)
    text = re.sub(r"\b(\w+)\s+('(?:s|re|ve|ll|d|m))\b", r"\1\2", text)
    text = re.sub(r"\bcan't\b", "can not", text)
    text = re.sub(r"\bwon't\b", "will not", text)
    text = re.sub(r"\bshan't\b", "shall not", text)
    text = re.sub(r"\bain't\b", "is not", text)
    text = re.sub(r"\bcannot\b", "can not", text)
    text = re.sub(r"\b(\w+)n't\b", r"\1 not", text)
    for old, new in (
        ("it's", "it is"), ("that's", "that is"), ("there's", "there is"),
        ("here's", "here is"), ("what's", "what is"), ("who's", "who is"),
        ("i'm", "i am"), ("let's", "let us"),
    ):
        text = re.sub(r"\b" + re.escape(old) + r"\b", new, text)
    text = re.sub(r"\b(\w+)'re\b", r"\1 are", text)
    text = re.sub(r"\b(\w+)'ve\b", r"\1 have", text)
    text = re.sub(r"\b(\w+)'ll\b", r"\1 will", text)
    text = re.sub(r"\b(\w+)'d\b", r"\1 would", text)
    text = re.sub(r"\b(un|non)-(?=[a-z])", r"\1", text)
    text = re.sub(r"--+|[—–]", " ; ", text)
    text = text.replace("-", " ")
    return text


def _tokens(text):
    return re.findall(r"[a-z]+(?:'[a-z]+)?|\d+(?:\.\d+)?|[.,;:!?()]", _normalize(text))


def _phrases(value, text):
    for phrase in text.split("|"):
        phrase = phrase.strip()
        if phrase:
            key = tuple(_tokens(phrase))
            if key:
                _PHRASES[key] = float(value)


_phrases(0.0, """
special effects | special effect | sound effects | visual effects |
love story | love stories | love triangle | love affair | love interest |
in love | falls in love | falling in love | true love |
romantic comedy | romantic comedies | romantic drama |
bad guy | bad guys | bad boy | bad boys | bad girl | bad girls |
good guy | good guys | good and evil | good versus evil |
good cop | bad cop | good old boy | good old boys |
best friend | best friends | best known | best selling | best seller |
great depression | great britain | great wall | great war |
cold war | cold blood | cold blooded | cold case |
disaster movie | disaster movies | disaster film | disaster films |
horror movie | horror film | horror comedy | horror story |
dead end street | death wish | true crime | cruel world |
black comedy | dark comedy | dark humor | dark humour |
gross out | gross out comedy | gross out humor |
funny business | funny money | funny bone |
fine line | flat out | awful lot | awful lot of |
low budget | big budget | high budget | b movie | b movies |
real life | real world | sad story | tragic story |
not only | not just | not merely | not simply |
nothing but | nothing short of | nothing less than |
no less than | no more than | no doubt | no wonder | no question |
without a doubt | without doubt | without question | without fail |
without reservation | without reservations | without sacrificing |
not to mention | no denying | no mere |
can not help but | can not help | could not help but | could not help |
can not deny | do not get me wrong |
""")

_phrases(4.0, """
a must see | must see | must watch | not to be missed |
one of the best | among the best | as good as it gets |
tour de force | tour de forces | a triumph | cinematic triumph |
movie magic | cinematic magic | instant classic | modern classic |
pure delight | sheer delight | absolute delight |
could not be better | could not have been better |
can not get any better | can not get much better |
can not recommend it enough | can not recommend this enough |
can not recommend it highly enough | can not praise it enough
""")
_phrases(3.0, """
first rate | top notch | top drawer | first class | world class |
pitch perfect | near perfect | nearly perfect | almost perfect |
well worth seeing | well worth watching | well worth your time |
worth every penny | worth the price of admission |
worth the admission price | worth the ticket price |
highly recommended | heartily recommended | strongly recommended |
do not miss it | do not miss this | do not miss |
a real gem | a little gem | little gem | hidden gem | small gem |
a real treat | a rare treat | a wonderful time |
great fun | good clean fun | pure fun | sheer fun |
laugh out loud | laughing out loud | laugh a minute |
side splitting | gut busting | belly laughs |
blown away | blows you away | blew me away | blew us away |
knocks it out of the park | hits a home run |
on all cylinders | firing on all cylinders |
edge of your seat | edge of my seat |
a breath of fresh air | breath of fresh air |
so bad it is good | so bad they are good |
so bad that it is good | so bad it is great
""")
_phrases(2.2, """
worth seeing | worth watching | worth a watch | worth a look |
worth a viewing | worth checking out | worth catching |
worth seeking out | worth your time | worth the time |
worth seeing again | worth a visit | worth the effort |
well worth | very worthwhile | worth it |
fun to watch | fun to see | a lot of fun | lots of fun |
good time | great time | a good movie | good film | good movie |
good entertainment | solid entertainment | fine entertainment |
good stuff | the real deal | a cut above | above average |
above par | better than average | pleasantly surprised |
pleasant surprise | pleasant surprises | surprising pleasure |
exceeded my expectations | exceeds expectations |
exceeds its ambitions | more than delivers |
crowd pleaser | crowd pleasing | audience pleaser |
feel good | feels good | guilty pleasure | guilty pleasures |
delivers the goods | delivers on its promise |
packs a punch | packs an emotional punch | packed with laughs |
hits the mark | hits the right notes | hits all the right notes |
strikes the right notes | gets it right | gets things right |
does it right | right on target | dead on |
comes alive | come alive | springs to life | full of life |
full of energy | full of charm | full of surprises |
with flying colors | with flying colours |
well acted | well directed | well written | well made |
well crafted | well executed | well paced | well plotted |
well constructed | well realized | fully realized |
finely crafted | finely tuned | beautifully shot |
beautifully filmed | beautifully acted | beautifully made |
skillfully made | skilfully made | intelligently written |
richly rewarding | emotionally satisfying | deeply satisfying |
emotionally involving | emotionally engaging | emotionally resonant |
emotionally powerful | deeply moving | genuinely moving |
thought provoking | thought provokingly | food for thought |
eye opening | mind blowing | jaw dropping |
gut wrenching | heart wrenching | soul stirring |
hard hitting | tough minded | high spirited |
light on its feet | light footed | sure footed |
rock solid | good natured | warm hearted | big hearted |
open hearted | tender hearted | good humored | good humoured |
unabashed fun | unpretentious fun | harmless fun |
dumb fun | stupid fun | mindless fun | silly fun |
cheap thrills | campy fun | trashy fun |
painfully funny | wickedly funny | brutally honest |
painfully honest | brutally funny |
cliche free | free of cliches | free from cliches |
a delight to watch | a pleasure to watch |
never fails to entertain | never fails to amuse |
does not disappoint | never disappoints |
fails to disappoint | fail to disappoint |
can not go wrong | hard to beat | tough to beat |
stand up and cheer | standing ovation |
two thumbs up | thumbs up | thumbs way up
""")
_phrases(1.3, """
not bad | not too bad | not so bad | not half bad |
not at all bad | not a bad film | not a bad movie |
not a bad way | not nearly as bad |
not boring | never boring | never dull | not dull |
no dull moments | not a dull moment | never a dull moment |
not without charm | not without its charms | not without merits |
not without merit | not without interest | not without humor |
no lack of | no shortage of |
has a lot to offer | much to recommend | plenty to recommend |
something to offer | something special | something new |
a nice surprise | refreshing change |
holds your attention | holds my attention | holds the attention |
keeps you interested | kept me interested | keeps you engaged |
held my interest | holds your interest | holds interest |
kept me entertained | kept us entertained |
keeps you guessing | keeps us guessing |
gets under your skin | stays with you | sticks with you |
lingers in the mind | linger in the mind |
more than adequate | more than competent | more than passable |
better than expected | better than it sounds | better than it looks |
better than it has any right to be |
good enough | enjoyable enough | amusing enough |
easy to like | easy to enjoy | easy on the eyes |
a welcome change | welcome change | worthy effort |
worthwhile effort | solid effort | solid performance |
has heart | has a heart | has its heart |
in good hands | in capable hands |
attention to detail | care and attention |
smartly done | nicely done | nicely made |
fleshed out | well rounded | well drawn |
slow burn | slow burning |
old fashioned charm | old fashioned fun |
tear jerker | tear jerking |
i like it | i like this | i like the film | i like the movie |
i liked | i loved | i enjoyed | i recommend |
you will love | you will enjoy | you will like |
you could do worse | could do a lot worse |
could have been worse | might have been worse |
not unlike | should be seen | deserves to be seen |
deserves an audience | deserves a look | deserves attention
""")
_phrases(0.4, """
has its moments | have their moments | has moments |
moments of interest | some nice moments | some good moments |
good intentions | best intentions | well intentioned | well meaning |
heart in the right place | heart is in the right place |
heart is in the right spot |
not for everyone | not for everybody | not for all tastes |
old fashioned | tries its best | does its best |
technically proficient | technically accomplished | technically competent |
pretty pictures | pretty movie | pretty film |
cheap laughs | light entertainment | harmless entertainment |
a few laughs | some laughs | a few chuckles
""")
_phrases(-0.9, """
not perfect | far from perfect | less than perfect |
not entirely successful | not completely successful |
not entirely satisfying | not entirely convincing |
at best | only occasionally | only sporadically |
merely competent | merely adequate | merely serviceable |
just adequate | just passable | just okay |
over the top | too much | too many |
slow paced | slow moving | self conscious |
on the nose | by itself | for the most part nothing |
less than stellar | less than ideal
""")
_phrases(-1.8, """
not great | not much fun | not much of a movie |
not much to offer | little to offer | little to recommend |
nothing to recommend | nothing to write home about |
nothing special | nothing new | nothing fresh | nothing original |
nothing remarkable | little new | little originality |
not enough | hardly enough | barely enough |
not good enough | not nearly enough |
not quite enough | never enough |
could be better | should be better | could have been better |
should have been better | might have been better |
deserves better | deserved better | deserve better |
not as good as | not nearly as good | not quite as good |
not half as good | not much better | no better than |
too long | too slow | too easy | too neat | too pat |
too cute | too slick | too clever | too precious | too self conscious |
too earnest | too serious | too familiar | too obvious |
too predictable | too sentimental | too contrived |
too many cliches | too little | too late |
too much of a good thing |
second hand | second rate | third rate |
run of the mill | garden variety | same old | tired old |
by the numbers | paint by numbers | painting by numbers |
off the shelf | off the rack | standard issue |
nothing happens | not much happens | little happens |
no story | no plot | no point | no purpose | no substance |
no emotional impact | without substance | without a point |
thinly drawn | paper thin | cardboard characters | cardboard cutouts |
one note | one dimensional | two dimensional |
thin on plot | thin on character | short on laughs |
short on humor | short on humour | short on ideas |
short on imagination | short on originality |
lacking in imagination | lacks originality | lacks imagination |
long in the tooth | out of date | past its prime |
hard to care | difficult to care | impossible to care |
hard to like | difficult to like | tough to like |
hard to love | hard to recommend | difficult to recommend |
hard to watch | difficult to watch | tough going |
tries too hard | trying too hard | trying much too hard |
tries to do too much | trying to do too much |
trying too much | strains too hard |
falls short | fall short | comes up short |
falls apart | fall apart | comes apart |
misses the point | misses the mark | off the mark |
goes astray | goes awry | loses its way | loses focus |
never comes together | does not come together |
does not add up | fails to add up |
not very good | less than compelling | less than satisfying |
less than entertaining | less than funny |
almost funny | almost good | almost works | nearly works |
would be funny | supposed to be funny |
attempts at humor | attempts at humour |
strained humor | strained humour | forced humor | forced humour |
struggles to | struggles with | struggling to |
all style | style over substance | style without substance |
emotionally distant | emotionally remote | emotionally empty |
emotional vacuum | emotional dead end |
leaves you cold | left me cold | leaves me cold |
leaves us cold | leaves the audience cold |
what is the point | what was the point |
who cares | so what | why bother | who needs |
not for me | i wanted to like | wanted to love |
does little | does very little | does nothing for |
more of the same | far cry from |
little more than | nothing more than |
better suited to television | made for television |
straight to video | straight to dvd | direct to video |
bargain basement | low rent |
pretends to be | pretending to be
""")
_phrases(-2.8, """
bad movie | bad film | bad acting | bad writing |
not good | no good | not any good | not at all good |
not entertaining | not funny | not interesting |
not worth it | not worth watching | not worth seeing |
not worth your time | not worth the time | not worth the effort |
not worth a look | not worth the money |
worth missing | worth avoiding |
do not bother | do not bother watching | do not bother seeing |
do not waste your time | do not waste your money |
save your money | save your time | save yourself the trouble |
stay away | steer clear | give it a miss | give this a miss |
skip it | skip this | avoid it | avoid this |
you can skip | you should skip |
waste of time | waste of money | waste of talent |
waste of energy | waste of film | wasting your time |
wastes your time | wasted time | wasted effort | wasted talent |
wasted opportunity | wasted opportunities | missed opportunity |
missed opportunities | lost opportunity |
squanders its potential | wastes its potential |
could not be worse | could not have been worse |
can not get any worse | can not get much worse |
can not save | can not rescue | can not redeem |
could not save | could not rescue | could not redeem |
unable to save | unable to rescue | unable to redeem |
does not save | does not rescue | does not redeem |
will not save | will not rescue | will not redeem |
can not compensate | does not compensate |
fails to deliver | failed to deliver | does not deliver |
does not work | did not work | never works | just does not work |
does not succeed | fails miserably | fails completely |
a complete failure | complete failure | abject failure |
a total mess | total mess | utter mess | incoherent mess |
a complete mess | a muddled mess | a bloated mess |
pointless exercise | empty exercise | hollow exercise |
exercise in futility | exercise in tedium | exercise in boredom |
dead on arrival | dead in the water |
falls flat | fall flat | fell flat |
goes nowhere | go nowhere | going nowhere | went nowhere |
never goes anywhere | never gets anywhere |
never takes off | fails to take off |
never gets off the ground | never comes alive |
going through the motions | goes through the motions |
treading water | spinning its wheels | spins its wheels |
been there done that | seen it all before |
seen this all before | seen it before | seen that before |
all too familiar | all too predictable |
pale imitation | poor imitation | pale shadow |
pales in comparison | pales beside | poor man |
watered down | warmed over | warmed up leftovers |
sour taste | bad taste in your mouth | bad aftertaste |
bad joke | sick joke | cruel joke |
laugh free | laughless | no laughs | zero laughs |
few and far between | laughs are few |
painfully unfunny | painfully dull | painfully boring |
mind numbing | mind numbingly | brain dead |
ham fisted | ham handed | heavy handed | leaden footed |
mean spirited | mean spirit | empty headed |
self important | self importance | self indulgent | self indulgence |
navel gazing | self satisfied | self congratulatory |
shameless manipulation | cheap manipulation | cheap sentiment |
emotional manipulation | shamelessly manipulative |
insults the intelligence | insults your intelligence |
insult to the intelligence | insult to your intelligence |
insult to the audience | treats the audience like idiots |
not a single laugh | not one laugh |
not a moment of | not an ounce of |
only redeeming feature | only saving grace |
no redeeming qualities | no redeeming value | no redeeming features |
without redeeming value |
a sad excuse | sad excuse | sorry excuse | poor excuse |
sorry mess | sad mess |
more boring than | more tedious than |
less than the sum of its parts |
worse than the sum of its parts |
never fulfills its promise | never lives up to |
fails to live up to | does not live up to |
overstays its welcome | overstay its welcome | overstayed its welcome |
wears out its welcome | wears thin | worn out its welcome |
what were they thinking | what was he thinking |
not my idea of fun | no fun at all
""")
_phrases(-3.8, """
one of the worst | among the worst | worst movie ever |
worst film ever | worst of the year |
avoid at all costs | a waste of two hours |
two hours of my life | hours of my life back |
watching paint dry | watch paint dry |
root canal | cinematic atrocity | cinematic disaster |
an unmitigated disaster | unmitigated disaster |
thumbs down | two thumbs down |
absolute garbage | utter garbage | complete garbage |
absolute rubbish | utter rubbish | complete rubbish
""")

# Overrides for expressions whose literal component words are misleading.
_phrases(2.2, """
wonderfully silly | delightfully silly | gloriously silly |
wonderfully absurd | delightfully absurd | gloriously absurd |
endearingly ridiculous | delightfully ridiculous | gloriously ridiculous |
hilariously ridiculous | wonderfully ridiculous |
wonderfully dumb | delightfully dumb | gloriously dumb |
enjoyably stupid | hilariously stupid | gloriously stupid |
delightfully cheesy | gloriously cheesy | wonderfully trashy |
too much fun | too good to miss | too good to pass up |
not to be underestimated | should not be missed |
no reason not to see | no reason not to enjoy |
not a waste of time | not a waste of money |
""")
_phrases(1.5, """
it works | works well | work well | works beautifully |
works wonderfully | works nicely | does work |
worth the wait | worth waiting for |
a movie to savor | a film to savor |
good looking | visually arresting | visually striking |
visually stunning | visually spectacular | visually sumptuous |
""")

_PHRASE_INDEX = {}
for _key, _value in _PHRASES.items():
    _PHRASE_INDEX.setdefault(_key[0], []).append((_key, _value))
for _first in _PHRASE_INDEX:
    _PHRASE_INDEX[_first].sort(key=lambda item: len(item[0]), reverse=True)

_PUNCT = {".", ",", ";", ":", "!", "?", "(", ")"}
_HARD = {".", ";", "!", "?"}
_ADVERSATIVES = {"but", "however", "yet", "nevertheless", "nonetheless", "whereas"}

_INTENSIFIERS = {
    "very": 1.25, "really": 1.18, "extremely": 1.45,
    "utterly": 1.4, "absolutely": 1.4, "completely": 1.3,
    "totally": 1.3, "thoroughly": 1.3, "entirely": 1.15,
    "deeply": 1.3, "highly": 1.3, "especially": 1.2,
    "particularly": 1.2, "incredibly": 1.35, "unbelievably": 1.35,
    "amazingly": 1.3, "astonishingly": 1.3, "astoundingly": 1.3,
    "remarkably": 1.25, "extraordinarily": 1.35,
    "surprisingly": 1.1, "unexpectedly": 1.1,
    "awfully": 1.25, "terribly": 1.25, "horribly": 1.25,
    "painfully": 1.3, "shockingly": 1.25, "ridiculously": 1.2,
    "frightfully": 1.2, "devastatingly": 1.2,
    "wickedly": 1.2, "insanely": 1.3,
    "hugely": 1.3, "massively": 1.3, "overwhelmingly": 1.3,
    "wonderfully": 1.25, "delightfully": 1.25, "gloriously": 1.25,
    "beautifully": 1.25, "brilliantly": 1.25, "magnificently": 1.3,
    "hilariously": 1.2, "endearingly": 1.15, "enjoyably": 1.15,
    "perfectly": 1.15, "genuinely": 1.2, "truly": 1.2,
    "exceptionally": 1.35, "unusually": 1.1,
    "so": 1.15, "such": 1.1, "quite": 1.1,
    "rather": 0.95, "fairly": 0.8, "reasonably": 0.8,
    "somewhat": 0.7, "slightly": 0.65, "mildly": 0.65,
    "moderately": 0.7, "partly": 0.65, "partially": 0.65,
    "occasionally": 0.55, "sporadically": 0.5,
    "intermittently": 0.55, "sometimes": 0.65,
    "almost": 0.7, "nearly": 0.8,
}

_NEGATORS = {
    "not", "never", "no", "neither", "nor", "without", "nothing",
    "hardly", "scarcely", "barely", "rarely", "seldom",
    "lack", "lacks", "lacked", "lacking", "devoid", "missing",
    "unable", "fail", "fails", "failed", "failing",
    "avoid", "avoids", "avoided", "avoiding",
    "eschew", "eschews", "eschewing", "sidesteps", "sidestep",
    "resist", "resists", "resisted", "resisting",
    "transcend", "transcends", "transcended",
    "overcome", "overcomes", "overcoming",
    "defy", "defies", "defied", "eliminates", "eliminate",
}

_ABSENCE_NOUNS = {
    "fun", "humor", "humour", "entertainment", "interest", "charm",
    "wit", "energy", "depth", "substance", "intelligence", "sense",
    "coherence", "suspense", "tension", "originality", "insight",
    "inspiration", "style", "life", "joy", "delight", "credibility",
    "warmth", "appeal", "laughs", "laugh", "thrills", "surprises",
    "pleasure", "pleasures", "merit", "merits", "value", "reason",
    "excitement", "imagination", "creativity", "heart", "soul",
    "resonance", "emotion", "emotional",
}

_PLOT_NOUNS = {
    "man", "woman", "boy", "girl", "guy", "guys", "kid", "kids",
    "person", "people", "father", "mother", "husband", "wife",
    "parents", "parent", "boss", "marriage", "relationship",
    "childhood", "child", "children", "criminal", "criminals",
    "villain", "villains", "world", "war", "crime",
}

_PARTS = {
    "cast", "actor", "actors", "actress", "actresses", "performance",
    "performances", "acting", "visuals", "photography", "cinematography",
    "soundtrack", "score", "music", "scenery", "landscape", "landscapes",
    "costumes", "costume", "production", "sets",
}

_PLAYFUL_NEGATIVES = {
    "silly", "absurd", "ridiculous", "dumb", "stupid", "cheesy",
    "trashy", "ludicrous", "outrageous", "crazy", "loopy", "wacky",
    "weird", "eccentric", "bizarre", "preposterous",
}
_PLAYFUL_MODIFIERS = {
    "wonderfully", "delightfully", "gloriously", "hilariously",
    "endearingly", "enjoyably",
}


@lru_cache(maxsize=12000)
def _word_score(word):
    if word in _WORDS:
        return _WORDS[word]
    if word.endswith("'s"):
        word = word[:-2]
        if word in _WORDS:
            return _WORDS[word]
    candidates = []
    if len(word) > 4 and word.endswith("ies"):
        candidates.append((word[:-3] + "y", 0.95))
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        candidates.append((word[:-1], 0.95))
        if word.endswith("es"):
            candidates.append((word[:-2], 0.95))
    if len(word) > 5 and word.endswith("ly"):
        candidates.append((word[:-2], 0.82))
        if word.endswith("ily"):
            candidates.append((word[:-3] + "y", 0.82))
    if len(word) > 6 and word.endswith("ness"):
        candidates.append((word[:-4], 0.9))
        if word.endswith("iness"):
            candidates.append((word[:-5] + "y", 0.9))
    if len(word) > 5 and word.endswith("ing"):
        stem = word[:-3]
        candidates.extend(((stem, 0.9), (stem + "e", 0.9)))
        if len(stem) > 2 and stem[-1] == stem[-2]:
            candidates.append((stem[:-1], 0.9))
    if len(word) > 4 and word.endswith("ed"):
        stem = word[:-2]
        candidates.extend(((stem, 0.9), (word[:-1], 0.9)))
        if stem.endswith("i"):
            candidates.append((stem[:-1] + "y", 0.9))
        if len(stem) > 2 and stem[-1] == stem[-2]:
            candidates.append((stem[:-1], 0.9))
    if len(word) > 5 and word.endswith("est"):
        candidates.extend(((word[:-3], 1.2), (word[:-3] + "e", 1.2)))
        if word.endswith("iest"):
            candidates.append((word[:-4] + "y", 1.2))
    if len(word) > 4 and word.endswith("er"):
        candidates.extend(((word[:-2], 1.05), (word[:-1], 1.05)))
        if word.endswith("ier"):
            candidates.append((word[:-3] + "y", 1.05))
    for stem, scale in candidates:
        if stem in _WORDS:
            return _WORDS[stem] * scale
    for prefix in ("un", "non", "dis"):
        if word.startswith(prefix):
            stem = word[len(prefix):]
            if stem in _WORDS and abs(_WORDS[stem]) >= 1.2:
                return -0.9 * _WORDS[stem]
    return 0.0


def _phrase_at(tokens, index):
    for key, value in _PHRASE_INDEX.get(tokens[index], ()):
        end = index + len(key)
        if end <= len(tokens) and tuple(tokens[index:end]) == key:
            return end, value
    return None


def _is_contrast(tokens, index):
    word = tokens[index]
    before = tokens[max(0, index - 6):index]
    if word == "but":
        if before and before[-1] in {"anything", "nothing", "all", "help"}:
            return False
        if any(before[k:k + 2] in (["not", "only"], ["not", "just"],
                                  ["not", "merely"], ["not", "simply"])
               for k in range(max(0, len(before) - 1))):
            return False
    if word == "yet" and any(t in {"not", "never", "no"} for t in before[-3:]):
        return False
    return word in _ADVERSATIVES


def _clause_weights(tokens):
    weights = [1.0] * len(tokens)
    start = 0
    boundaries = [i for i, t in enumerate(tokens) if t in _HARD]
    boundaries.append(len(tokens))
    for end in boundaries:
        if end <= start:
            start = end + 1
            continue
        for i in range(start, end):
            word = tokens[i]
            if _is_contrast(tokens, i) and i > start:
                for j in range(start, i):
                    weights[j] *= 0.62
                for j in range(i + 1, end):
                    weights[j] *= 1.22
            if word in {"although", "though", "despite", "while", "whilst"}:
                initial = i <= start + 2
                if initial:
                    comma = next((j for j in range(i + 1, end)
                                  if tokens[j] == ","), None)
                    if comma is not None:
                        for j in range(i + 1, comma):
                            weights[j] *= 0.55
                        for j in range(comma + 1, end):
                            weights[j] *= 1.16
                elif word != "while" and word != "whilst" and i + 1 < end:
                    for j in range(start, i):
                        weights[j] *= 1.08
                    for j in range(i + 1, end):
                        weights[j] *= 0.58
            if word == "if" and i > start and tokens[i - 1] == "even":
                for j in range(i + 1, end):
                    weights[j] *= 0.65
            if word in {"ultimately", "overall"}:
                for j in range(i + 1, end):
                    weights[j] *= 1.28
            if word == "than":
                before = tokens[max(start, i - 9):i]
                if any(t in {"better", "worse", "more", "less"} for t in before):
                    for j in range(i + 1, end):
                        if tokens[j] in {",", "but", "however", "yet"}:
                            break
                        weights[j] *= 0.58
        start = end + 1
    return weights


def _external_negation(tokens, start, protected, head):
    found = []
    words_seen = 0
    conjunction = None
    for j in range(start - 1, max(-1, start - 13), -1):
        word = tokens[j]
        if word in _PUNCT:
            break
        if word in {"although", "though", "whereas", "because", "than"}:
            break
        if word in _ADVERSATIVES:
            if word == "but" and j > 0 and tokens[j - 1] == "anything":
                found.append(("not", j))
            break
        if word == "and":
            conjunction = j
        words_seen += 1
        if words_seen > 7:
            break
        if protected[j]:
            continue
        negator = word in _NEGATORS
        if word in {"little", "few"} and head in _ABSENCE_NOUNS:
            if start - j <= 4:
                negator = not (j > 0 and tokens[j - 1] in {"a", "the"})
        if word == "less" and start - j <= 3:
            negator = True
        if not negator:
            continue
        if word == "not" and j + 1 < len(tokens):
            if tokens[j + 1] in {"only", "just", "merely", "simply"}:
                continue
        if word in {"no", "nothing"} and j + 1 < len(tokens):
            if tokens[j + 1] in {"doubt", "wonder", "but", "short", "less"}:
                continue
        if conjunction is not None and j < conjunction:
            intervening = tokens[j + 1:conjunction]
            if any(_word_score(t) < -0.8 for t in intervening):
                break
        found.append((word, j))
        # Nearby double negation, such as "never fails to entertain".
        for k in range(j - 1, max(-1, j - 4), -1):
            if tokens[k] in _PUNCT or tokens[k] in _ADVERSATIVES:
                break
            if protected[k]:
                continue
            if tokens[k] in {"not", "never", "no", "without", "hardly"}:
                found.append((tokens[k], k))
                break
        break
    return found


def _context_before(tokens, index, window=9):
    begin = max(0, index - window)
    for j in range(index - 1, begin - 1, -1):
        if tokens[j] in _PUNCT or tokens[j] in _ADVERSATIVES:
            begin = j + 1
            break
    return tokens[begin:index]


def _modifier_scale(tokens, start, head, value):
    scale = 1.0
    playful = False
    count = 0
    for j in range(start - 1, max(-1, start - 4), -1):
        word = tokens[j]
        if word in _PUNCT or word in _ADVERSATIVES:
            break
        if word in _INTENSIFIERS:
            scale *= _INTENSIFIERS[word]
            count += 1
            if word in _PLAYFUL_MODIFIERS and head in _PLAYFUL_NEGATIVES:
                playful = True
            if count >= 2:
                break
        elif word not in {"a", "an", "the", "and", "so", "much", "more", "less"}:
            break
    value *= min(1.8, max(0.35, scale))
    if playful and value < 0:
        value = abs(value) * 0.8
    return value


def _hypothetical_adjustment(tokens, start, value):
    before = _context_before(tokens, start, 10)
    context = " ".join(before)
    unrealized = (
        "could have been", "should have been", "would have been",
        "might have been", "ought to have been", "could have",
        "should have", "would have",
    )
    if any(context.endswith(p) or p + " " in context for p in unrealized):
        if "not" not in before:
            return -0.65 * value
    attempted = (
        "tries to be", "trying to be", "tried to be",
        "attempts to be", "attempting to be", "attempted to be",
        "wants to be", "wanted to be", "pretends to be",
        "pretending to be", "strains to be", "straining to be",
        "supposed to be", "meant to be",
    )
    if value > 0 and any(context.endswith(p) for p in attempted):
        return -0.5 * value
    if value > 0 and any(context.endswith(p) for p in (
        "if it were", "if it was", "if only it were", "if only it was",
    )):
        return -0.7 * value
    return value


def _get_text(state):
    if isinstance(state, str):
        return state
    if isinstance(state, dict):
        for key in ("text", "sentence", "review", "content", "input"):
            if key in state and isinstance(state[key], str):
                return state[key]
        for key in ("state", "data"):
            if key in state:
                result = _get_text(state[key])
                if result:
                    return result
    if isinstance(state, (list, tuple)):
        return " ".join(item for item in state if isinstance(item, str))
    return ""


def predict(state):
    text = _get_text(state)
    tokens = _tokens(text)
    if not tokens:
        return {"answer": "positive"}

    protected = [False] * len(tokens)
    events = []
    i = 0
    while i < len(tokens):
        match = _phrase_at(tokens, i)
        if match is not None:
            end, value = match
            for j in range(i, end):
                protected[j] = True
            if value:
                events.append((i, end, value, True))
            i = end
            continue

        word = tokens[i]
        value = _word_score(word)
        if word in _INTENSIFIERS:
            # In "remarkably bad", the adverb strengthens "bad"; it does
            # not contribute an independent positive evaluation.
            for j in range(i + 1, min(len(tokens), i + 4)):
                if tokens[j] in _PUNCT:
                    break
                if _word_score(tokens[j]) != 0:
                    value = 0.0
                    break
                if tokens[j] not in {"very", "rather", "quite", "so", "truly"}:
                    break
        if word == "moving" and i + 1 < len(tokens):
            if tokens[i + 1] in {"to", "into", "out", "from", "toward", "towards", "along"}:
                if tokens[i + 1:i + 3] != ["to", "tears"]:
                    value = 0.0
        if word == "touching" and i + 1 < len(tokens) and tokens[i + 1] == "on":
            value = 0.0
        if word in {"novel", "original"} and i + 1 < len(tokens):
            if tokens[i + 1] in {"novel", "book", "version", "release", "screenplay"}:
                if word == "original":
                    value *= 0.25
        if value:
            events.append((i, i + 1, value, False))
        i += 1

    weights = _clause_weights(tokens)
    scores = []
    for start, end, base, is_phrase in events:
        head = tokens[start]
        value = _modifier_scale(tokens, start, head, base)
        before = _context_before(tokens, start, 10)

        negators = _external_negation(tokens, start, protected, head)
        if len(negators) % 2:
            kind = negators[0][0]
            if value > 0:
                value *= -0.95
                if kind in {"barely", "hardly", "scarcely", "rarely", "seldom"}:
                    value *= 0.85
            else:
                value *= -0.75

        # Negative superlatives can be sincere praise when preceded by
        # "couldn't be more": "couldn't be more engaging".
        context = " ".join(before)
        if re.search(r"(?:can|could) not (?:have been|be) (?:any )?more$", context):
            value = abs(base)
        elif re.search(r"(?:can|could) not (?:have been|be) (?:any )?less$", context):
            value = -abs(base)

        if not is_phrase:
            value = _hypothetical_adjustment(tokens, start, value)

        if end < len(tokens) and tokens[end] == "free" and base < 0:
            value = abs(value) * 0.8
        if end + 1 < len(tokens) and tokens[end:end + 2] in (
            ["is", "absent"], ["are", "absent"], ["is", "missing"],
            ["are", "missing"],
        ):
            value = -0.9 * value

        if not is_phrase:
            following = tokens[end:min(len(tokens), end + 3)]
            if base < 0 and following:
                if following[0] in _PLOT_NOUNS and head in {
                    "bad", "poor", "miserable", "nasty", "hateful",
                    "cold", "bitter", "crude", "unpleasant", "stupid",
                    "dumb", "pathetic", "awkward", "odious", "silly",
                }:
                    value *= 0.35
            nearby = tokens[max(0, start - 2):min(len(tokens), end + 3)]
            if value > 0 and any(t in _PARTS for t in nearby):
                value *= 0.82
            if "title" in nearby or "poster" in nearby or "trailer" in nearby:
                value *= 0.45

        weight = sum(weights[start:end]) / max(1, end - start)
        scores.append((value * weight, start, end))

    total = sum(item[0] for item in scores)

    # A few common verdicts have no ordinary evaluative adjective.
    normalized = " ".join(tokens)
    if re.search(r"\b(?:want|wanted|give|need) (?:me |us )?(?:my|our) "
                 r"(?:money|time|two hours|90 minutes) back\b", normalized):
        total -= 4.0
    if re.search(r"\b(?:no|not one|not a single) (?:reason|excuse) "
                 r"to (?:watch|see|recommend)\b", normalized):
        total -= 2.8
    if re.search(r"\b(?:rather|better off) (?:stay|staying|watch|watching|rent|renting)\b",
                 normalized):
        total -= 1.5
    if re.search(r"\b(?:only|sole) (?:thing|reason|aspect).{0,45}"
                 r"\b(?:good|worthwhile|enjoyable|watchable)\b", normalized):
        total -= 1.4
    if re.search(r"\b(?:i|we) (?:walked|walk|walking) out\b", normalized):
        total -= 2.4
    if re.search(r"\b(?:put|puts|sent|send|sends) (?:me|you|us) to sleep\b", normalized):
        total -= 2.8
    if re.search(r"\b(?:fell|fall|falling) asleep\b", normalized):
        total -= 2.0

    # Interpret explicit review ratings when present.
    rating = re.search(
        r"\b(\d+(?:\.\d+)?)\s*(?:/|out\s+of)\s*(4|5|10)\b", text.lower()
    )
    if rating:
        numerator = float(rating.group(1))
        denominator = float(rating.group(2))
        if 0 <= numerator <= denominator:
            ratio = numerator / denominator
            if ratio >= 0.65:
                total += 4.0
            elif ratio <= 0.45:
                total -= 4.0

    if abs(total) < 0.12 and scores:
        strongest = max(scores, key=lambda item: (abs(item[0]), item[1]))
        if abs(strongest[0]) >= 1.0:
            total = strongest[0]
        else:
            total = scores[-1][0]

    return {"answer": "negative" if total < 0 else "positive"}