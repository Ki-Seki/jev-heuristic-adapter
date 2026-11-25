import re
import unicodedata
from bisect import bisect_left


def _text(x):
    if isinstance(x, str):
        return x
    if isinstance(x, dict):
        keys = {str(k).lower().replace("_", " "): k for k in x}
        for k in ("sentence", "text", "review", "review text", "movie review",
                  "content", "excerpt", "quote", "snippet", "phrase", "comment",
                  "input", "passage", "document", "utterance"):
            if k in keys:
                t = _text(x[keys[k]])
                if t:
                    return t
        return " ".join(t for k, v in x.items()
                        if str(k).lower() not in ("label", "id", "idx", "index", "sentiment", "title")
                        for t in [_text(v)] if t)
    if isinstance(x, (tuple, list)):
        return " ".join(_text(v) for v in x)
    return ""


def _tokens(text):
    t = unicodedata.normalize("NFKD", text.casefold())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.replace("’", "'").replace("‘", "'").replace("`", "'")
    t = t.replace("&amp;", " and ").replace("&quot;", '"').replace("&#39;", "'").replace("&", " and ")
    t = re.sub(r"<br\s*/?>|</p>", " . ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = t.replace("-lrb-", "(").replace("-rrb-", ")")
    t = re.sub(r"\s+n\s*'\s*t\b", "n't", t)
    t = re.sub(r"\s*'\s*(ll|ve|re|d|m|s)\b", r"'\1", t)
    t = re.sub(r"\b(can't|cannot|cant)\b", "can not", t)
    t = re.sub(r"\b(won't|wont)\b", "will not", t)
    t = re.sub(r"\b(ain't|aint)\b", "is not", t)
    t = re.sub(r"n't\b", " not", t)
    t = re.sub(r"\b(did|do|does|is|was|are|were|could|would|should|has|have|had)nt\b", r"\1 not", t)
    t = re.sub(r"'(ll|ve|re|d|m|s)\b",
               lambda m: " " + {"ll": "will", "ve": "have", "re": "are",
                                 "d": "would", "m": "am", "s": "is"}[m[1]], t)
    t = t.replace("—", " ; ").replace("–", " - ").replace("...", " … ")
    return re.findall(r"[a-z0-9]+|[.!?,;:…()/]", t)


_LEX = {}


def _words(score, words):
    for w in words.split():
        _LEX[w] = score


_words(3.8, """
masterpiece masterwork masterpieces masterworks triumph triumphant tourdeforce
outstanding extraordinary exceptional superb superlative sublime magnificent
magnificence marvelous marvellous wonderful wondrous brilliant brilliance
ingenious genius sensational phenomenal exhilarating exhilaration breathtaking
stunning spectacular spellbinding mesmerizing mesmerising riveting enthralling
unforgettable impeccable incomparable peerless matchless unparalleled
unmissable unassailable perfect flawless transcendent transcendental
astonishing astounding amazing fabulous fantastic terrific tremendous
glorious resplendent ravishing rapturous dazzling exquisite exquisite
splendid stellar topnotch magnificent scintillating classic
""")
_words(2.95, """
great excellent excellence impressive impresses impressed impressive
beautiful beauty gorgeous handsome lovely loveliness beauteous
enchanting enchanted enthralled captivated captivating spellbound transporting
engrossing engrossed absorbing immersive involving magnetic compelling
inspired inspiration inspirational inspiring inventive inventiveness
imaginative imagination creative creativity innovative innovation visionary
exuberant exuberance joyous joyful joy joyously delight delights
delighted delightful delicious delectable luscious lusciousness
uproarious hilarious hilarity hysterical sidesplitting riotous
entertaining entertainment enjoyable enjoyment enjoyed enjoy enjoys
lovable loveable adorable endearing irresistible beguiling winning
charming charmed charm charismatic charisma effervescent ebullient
appealing appealingly engaging engaged addictive exciting excitement
thrilling thrilled thrills suspenseful suspense nailbiter gripping
powerful powerhouse potent potency electrifying electric invigorating bracing
refreshing refreshingly fresh freshness original originality originality
poignant poignancy affecting moving heartfelt heartrending heartwarming
heartbreaking heartbreaking stirring soulful uplifting uplift buoyant
resonant resonance resonance resonates resonated stirring
satisfying satisfied satisfaction gratifying gratifyingly rewarding worthwhile
accomplished masterful masterly masterfully virtuosic virtuoso virtuosity
skillful skilful skillfully skilfully adept adroit assured assuredly
polished elegant elegance graceful grace finesse artistry artistry
excellent distinguished exemplary praiseworthy commendable laudable
praise applaud applause bravo kudos admiration admire admired admirable
topflight firstclass invaluable indispensable essential landmark gem gems
treasure treasures treat revelation revelatory revelation knockout winner
triumphs excels excel excelled outdoes surpassed surpasses
sensational fabulous fantastic phenomenal sumptuous sumptuousness
hypnotic lyrical lyricism poetic poetry luminous luminescent radiant
multifaceted multilayered nuanced nuance subtlety subtle subtleties
intelligent intelligence smart clever cleverness witty wit wittiest
insightful insight perceptive observant astute thoughtful thoughtfulness
incisive incisiveness penetrating profound profundity enlightening
trenchant provocative evocative expressive empathetic compassionate
audacious daring courageous fearless bold audacity audaciousness bravura
credible believable convincing convinced persuasive authentic authenticity
realistic humane humanity humanistic honest honesty truthful truthfulness
unpretentious accomplished assured dexterous deft dexterity deftness
seasoned memorable indelible memorable distinctive singular
fascinating fascination intriguing intrigued engross evocative
resonates riveting transfixing entrancing enthralling enthralls
mesmerizes shines shone excel enthralls delights enlightens astonishes
enriching enriching rich richness textured vibrant vivid vibrancy
alive lively liveliness vitality vivacious energetic energized energizing
kinetic dynamism dynamic sparkles sparkling sparkle crackling crackles
funny fun funniest laughs laughter laughablezzz chuckles chuckle giggles
amusing amusement amused droll playful playfulness winsome
wry cheeky saucy sassy mischievous irreverent irreverence exuberance
solid terrific satisfying taut tight brisk punchy zippy zesty zingy
nimble snappy crisp breezy breeziness buoyancy rollicking rousing
acclaimed acclaimed accomplished praiseworthy unforgettable crowdpleaser
unpredictable unpredictable surprising surprises surprised
enticing tantalizing intoxicating intoxicant exhilarating exhilarated
beautifully wonderfully perfectly excellently splendidly brilliantly
superbly sublimely magnificently delightfully memorably marvelously
miraculously miraculously remarkably impressively ingeniously
fearlessly dazzlingly astonishingly spectacularly exceptionally
""")
_words(1.85, """
good better nice positive positives likeable likable amiable affable
pleasant pleasing pleased pleasure pleasures pleasurable engaging
diverting diversion agreeable accessible watchable rewatchable
readable appealing appealingly decent respectable serviceable worthwhile
worthy merit merits meritorious successful success succeeds succeed succeeded
effective effectively effectual works worked functional competent
capable convincing solid confident confidence fluent fluency apt
consistent coherent coherence cohesive legible lucid clarity clear
balanced balance assuredness mature maturity restrained restraint economical
economy efficient lean sleek smooth polished professionalism professional
expert expertly expertise craftsmanship crafted craftsman craft
meticulous precise precision detail detailed attentive careful
stylish style stylistic stylized fashionable chic hip cool
interesting interest interested curiosity curious tantalizing intriguing
ambitious ambition ambitiousness scope epic sweeping expansive intimate
intimacy sensitivity sensitive delicacy delicate tenderness tender
gentle warmth warm sweet sweetness touching touched poignant wistful
sympathetic sympathy empathic empathy compassion generosity generous kindhearted
caring thoughtful sincerity sincere earnest earnestness affectionate affection
passionate passion ardor spirited verve vigor vigour vigorous zest gusto
enthusiastic enthusiasm spunk plucky spunky gusto ebullience
personable appealing comely attractive sexy sensual sensuality luscious
fanciful magical magic enchanting enchanted fairytale dreamlike dreamy
haunting hauntingly atmospheric moody evocative impressionistic
meditative contemplative understated understatedness quietude
elegiac melancholy bittersweet nostalgic nostalgia mournful
moving haunting stirring arresting striking sharp pointed
pungent piquant pungency acerbic satirical satiric sardonic deftly
edgy nervy ballsy gutsy daring bold fearless guts nerve
quirky offbeat eccentric idiosyncratic offkilter oddball funky
unusual unexpected unconventional refreshing unorthodox unpredictable
distinct different unique rarity rare unconventional individual
intense intensity visceral raw gritty grit unflinching stark uncompromising
uncompromised uncompromisingly fearless fearless searing scathing
disturbing chilling scary terrifying creepy eerie unsettling unnerving
harrowing wrenching devastating chillingly spooky claustrophobic
fast entertaining stylish kinetic rambunctious infectious contagious
vibrant colorful colourful colorful spiffy slick eyeopener
appeal appeals elicited conveys captures captures captured capturing
conjures conveys illuminates illuminating explores exploring exploration
examination examines mines probing probes delves tackles
revealing revealingly reveals richly layered perceptively perceptiveness
complex complexity depth dimension dimensionality substance substantial
contentment grounded groundedness natural naturalistic spontaneous
naturalism spontaneity candid candor frank frankness unforced unaffected
unassuming lowkey modest nimble spry breezy spirited
refresh revived reinvigorates revives renewed renews reinvents
superior outperform outperforms exceeds improves improved improvement
complements elevates elevated enhances enhanced distinguishes distinguished
redeems redeeming redeems compensates compensate compensates resonates
deliver delivers delivered pays rewards rewarded
overcomes overcame transcends transcend transcending salvages redeems
happily happy merriment merry merrily smile smiles smiling grin grinning
tickled tickles tickling ticklish tickler giddy giddiness
laugh laughing chuckling hilarious zany madcap antic anarchic raucous
energetic energy verve momentum rhythm flow
grandeur majesty majestic stately lush lavish grand gorgeous soaring
imposing widescreen panoramic enticing appetizing appetising
fidelity faithful faithfully superior importance important necessary
valuable value pertinent relevant relevance timeliness timely
recommend recommends recommended recommending endorsement endorses
favorite favorites favourite favourites keeper keepers standout standouts
highlight highlights standout highlight strength strengths strong stronger
sturdy robust resilient solidly neatly nicely deftly cleverly expertly
skilled talented talent talents gifted versatile versatility
starshine bonanza feast banquet homage tribute celebration celebrates
tribute ode valentine miracle marvel marvels wonders riches
killer dynamite corker crackerjack blast hoot riot romp lark delight
charmer cutie crowdpleasing grin gold treasure goldmine
""")
_words(0.7, """
human universal personal personality unusual intriguing unusual
watchable adequate okay fine fair passable tolerable reasonable
potential promising promise promises opportunity
big small quiet simple simplicity unadorned spare minimal minimalist
direct straightforward muscular muscularity assuredness unadulterated
clean frank true truth truths real recognizable recognisable familiar
emotional emotion emotions characterizations characterization
heart soul spirit feeling feelings thought thoughts ideas idea
mood atmosphere vision sensibility sensibilities
relationship relationships portrait portraiture portraits fable
parable allegory metaphor meditation evocation study examination tale
journey odyssey saga adventure encounter tribute
insights observant perfectly focused focus
engagement discovery discover find finds
succeeds achievement achievements effort ambitions
art artful artist filmmaker filmmaking cinematic cinema
adult adults family families children kid kids audience audiences
fans fan buffs festival entertainment entertainer
love loves liked liked grace character actor actors cast
experience experiences moments moment scenes sequence sequences
laughs laughs amusing laugh smile
modern contemporary historical history tradition traditions
special different right enough fascinating improbable
risk risks challenge challenges challenging demanding tricky difficult
unsettle shocks shock confounds defies haunting
wild crazy strange weird odd curious bizarre surreal surrealistic
dark darkness haunting sadness sad melancholy bittersweet
subversive subverts subversion irony ironic tension tense tensions
pacing dramatic drama comic comedy musical romantic romance
breakthrough veritable lovingly lovingly lovingly
""")
# Avoid giving evaluative weight to the ordinary vocabulary of film synopses.
for _w in """
big small actors actor character fan adults adult family families children kid kids
audience audiences cinema cinematic film filmmaking filmmaker cast comic comedy
drama musical romantic romance scenes scene sequence sequences moment moments
experience experiences contemporary modern historical history tradition traditions
right enough true real find finds simple difficult focus challenge challenging
dark darkness sadness sad quiet strange weird odd curious bizarre crazy
relationship relationships tale study saga journey feeling emotions emotion
idea ideas love loves special art pacing shock shocks drama entertainer
""".split():
    _LEX.pop(_w, None)

_words(-3.9, """
awful horrible horrifyingly horrid horrendous terrible abysmal atrocious
atrocity appalling appalled abhorrent repellent repellant repugnant
repulsive disgusting despicable reprehensible loathsome execrable
dreadful dismal miserable wretched ghastly godawful deplorable pitiful
pathetic laughable ludicrous risible ridiculous preposterous asinine
inane idiotic idiocy idiot imbecilic moronic moron sophomoric insipid
insufferable unbearable unwatchable unendurable excruciating torturous
torture agonizing agonising painfulzzz abominable atrociously
inexcusable indefensible unforgivable unredeemable irredeemable
worthless useless pointless disastrous disaster catastrophe catastrophic
travesty fiasco debacle failure flop flops flopped bombed turkey stink
stinker stinks stank stunk sucks sucked suckage crap crappy crummy
garbage rubbish drivel dreck drek tripe trashy junk schlock shlock
abomination monstrosity bilge hooey baloney bunk hogwash
worst lousy vile odious offensive insulting insult insultingly
hated detest detested loathe loathed despise despised
unfunniest unfunny humorless humourless charmless witless
""")
_words(-2.95, """
bad badly worse inferior poor poorer poorest poorly shoddy sloppy
amateurish amateurism inept ineptitude incompetent incompetence bungled
bungling botched botch mangled mishandled mishandles mismanaged
misjudged misguided misconceived misbegotten misfire misfires misfired
misstep missteps miscalculation miscalculations mistake mistakes
disappoint disappoints disappointed disappointing disappointment letdown
underwhelming underwhelmed unsatisfying unsatisfied unsatisfactory
unrewarding unfulfilling uninspiring uninspired uninvolving unengaging
uninteresting unentertaining unexciting unappealing unappealingly
unimpressive unimpressed unremarkable undistinguished lackluster lacklustre
forgettable forgotten forgettably forgettable disposable dispensable
unmemorable ordinary mediocre mediocrity middling subpar substandard secondrate
tedious tedium tiresome tiring tiringly tired boring boredom bored bore
bores boringly dull dullness dullest duller drab dreary dreariness
monotonous monotony repetitive repetitious repetition redundant
interminable endless interminably overlong overlengthy overlength
sluggish sluggishness lethargic lethargy leaden lumbering labored laboured
laborious laboriously plodding plods plod ponderous ponderously ponderousness
inert inertia lifeless listless listlessness limp flaccid flatness
soporific sleepy sleepwalking drowsy narcoleptic comatose numbing numbed
wearisome wearying weary tediousness grating irritating irritated irritant
irritates irksome obnoxious annoying annoys annoyed annoyance
aggravating exhausting exasperating frustrating frustrated frustration
infuriating infuriated alienating alienated distancing distancingly
offputting unpleasant unlikable unlikeable unlovable unsympathetic
shrill strident abrasive grating whiny whining screechy screeching
graceless clumsy clumsiness clumsily awkward awkwardness awkwardly
ungainly ungainliness clunky clunkiness clunks klunky hamfisted
heavyhanded heavyhandedness hammy hammily hamming hamminess overacting
overacted overacts overwrought overblown overbearing overplayed
overdone overdoing overcooked overripe overstuffed overloaded bloated
excessive excesses overkill gratuitous gratuitously extraneous
overwhelmzzz overwhelmingzzz excessive excess overlong overextended
undercooked underwritten underdeveloped undeveloped undernourished
underpowered underwhelms disjointed disconnected incoherent incoherence
incomprehensible unintelligible impenetrable muddle muddled muddles
muddling muddy murky convoluted contrived contrivance contrivances
implausible implausibility implausibilities improbable unconvincing
unbelievable unpersuasive unconvincingly unearned unmotivated
arbitrary illogical illogic nonsensical nonsense senseless absurdity
confused confusing confusion confuses confounding unfocused aimless
aimlessness meandering meanders meander wandering rambling ramshackle
uneven unevenness patchy spotty scattershot haphazard chaotic choppy
sloppy slipshod unstructured incoherently mess messy messiness
flimsy thinness thin thinner shallow shallowness superficial superficiality
empty emptiness hollow soulless heartless synthetic artificial phony phoney
fake forced strained stilted stiff stiffness wooden cardboard one dimensionalzzz
unrealistic unoriginal derivative derivativeness recycled derivative
uninventive unimaginative unimaginatively uncreative imitative imitation
unadventurous predictable predictability formula formulaic formulaically
formulaically hackneyed hackwork hack hacks hackish cliche cliches cliched
trite banal banalities banality stale staleness shopworn threadbare
wornout tired tiresome rehashed rehash retread retreads rehashes ripoff
knockoff copycat warmedover generic bland blandness nondescript
tasteless tastelessness tacky cheap cheaper tawdry chintzy cheesy cheesiness
corny cornball hokey hokum hokiness kitschy schlocky campiness
saccharine syrupy sugary sappy maudlin mawkish cloying schmaltz schmaltzy
melodramatic melodramazzz contrivances manipulative manipulation
exploitative exploitation pandering panders patronizing patronising
condescending condescension preachy preachiness sermonizing didactic
pedantic pretentious pretension pretensions pretentiousness pompous pomposity
selfimportant selfindulgent smug smugness smugly conceited arrogant
cynical cynicism crass crassness crude crudeness vulgar vulgarity lewd
tasteless gross grossout juvenile infantile immature childish puerile
silly silliness stupid stupidity dumb dumbest dumbed dumber dimwitted
emptyheaded brainless mindless moronic idiotic idiocies inanities inanity
foolish fatuous feeble weak weakness weaknesses weaker lame lamest
ludicrously laughably embarrassingly embarrassing embarrassed embarrassment
humiliating humiliation embarrassing cringe cringeworthy cringing cringeinducing
obvious obviousness painfully painful laughably implausibly transparently
glaring egregious unfortunate unfortunately sadly alas regret regrettably
flaws flawed problematic problem problems troubling troublesome
fails failed fail failing failure failures falters faltering falter
founders flounders floundering flounder flails flailing
stumbles stumbling fumbles fumbled fumbling fizzles fizzled fizzles
sags sagging sag drag drags dragged dragging lag lags lagging
sinks sank sinking sours spoils spoiled ruins ruined ruin undermines
detracts distracts distracting distraction intrudes hinders hindered hampers
squanders squander squandered squandering wastes wasted wasting waste
betrays betraying betrays cheats cheating shortchanges shortchanged
disservice tarnishes mars marred saddled plagued hampered crippled
sabotages sabotaged suffers suffering suffers afflicts bogged weighed
flounders unbalanced unrelentingzzz unrelieved unexceptional unspectacular
unnecessary superfluous pointless pointlessness meaningless inconsequential
irrelevant immaterial unimportant insignificant trivial triviality trifling
inadequate insufficiency insufficient lacking lacks lack devoid bereft
shortcomings shortcoming faults drawback drawbacks downside pitfalls
mishmash hodgepodge mishap jumble jumbled mucks morass mishmosh
vapid vacuous vapidity vacuity airless bloodless toothless spineless
soulless joyless drearily lifeless pallid anemic anaemic puny pale
pallor wan tame tepid lukewarm halfhearted halfbaked watered diluted
waterlogged bankrupt pathetic pitiful pitiable sorry sorryass
repellent alienates offends revolting nauseating nauseous unpalatable
sexist racist misogynistic misogyny homophobic stereotypes stereotyped
stereotypical caricatured caricatures caricature exploitative insensitive
irresponsible dishonest dishonestyy disingenuous disheartening
""")
_words(-1.45, """
low lesser minor slight slightness modest middling marginal scant thinly
limited limitations limits shortfalls limitations missed miss misses
struggles struggle struggling stumbles uneven rickety rough shaky
iffy questionable dubious doubtful ambivalent lukewarm mixed
iffy erratic inconsistent inconsistency inconsistencies patchwork
conflicted puzzling perplexing bewildering elusive obscure opaque
unwieldy diffuse scattered sprawling overambitious derivative
indulgent indulgence excess excesses gimmick gimmicks gimmicky
trickery gimmickry shtick schtick routine stock standard recycled
familiar conventional convention conventionality cliches obligatory
obligatory typical cliched rote mechanical mechanicality perfunctory
mechanically predictable predictably unsurprising uninspired conventional
unimaginatively sanitized sugarcoated glossy glib slick slickness
superficially surface heavy bloated heavygoing lumber sluggish
contrivance convenient contrived manipulations forced strained
calculated calculating commercial commercialism product packaged
forgettable forgets forgot forget neglect neglects omits omission
unexplained unresolved disjointed confusingly noticeably conspicuously
uncomfortable discomfort uneasy unpleasant disconcerting alienation
relentless relentlessly bleak bleakness grim grimness grimly gloomy
depressing depressed downbeat downer dour sour nasty nastiness ugly
unkind cruel cruelty unpleasantly grueling gruelling hardgoing harsh
violent gratuitous exploitative gory goriness gore blunt sentimental
sentimentality excessive mawkishness oversentimental melodramatics
phony contrived artificiality affected mannered mannerism mannerisms
shticky precious preciousness overly overtly exaggerates exaggerated
exaggeration bombast bombastic bombarded noisy noisiness noisome
cacophony loud louder frenzy frantic frenetic frenzied numbing
numb repetitiveness trash junky junkfood bottom barrel lowbrow
tires tiredness wear thin exhausted exhausting overstay overstays
irritations disinterest disinterested indifferent indifference yawn
yawns yawning snore snooze snoozer snoozefest slumber interminable
groan groans groaning groaner wince winces wincing groanworthy
desperate desperation desperately tries trying attempts attempting
imitates borrows stolen steals derivative pretends pretending poses
wannabe aspiring wannabes apparent apparently presumably supposed
merely simplyzzz barely hardly scarcely rarely almostzzz
halfway partially occasionally sporadic sporadically fitfully
artifice contraption exercise concoction pretender copy clone
puzzle muddles baffling incomprehensibility impenetrability nonsensically
soupy sticky icky yucky pandering leering lewdness perverse
disjoint unwitting unintentionally unintentional inadvertently dubious
pedestrian prosaic monotonously repetitive ordinariness unambitious
distract diluted diluted thinly flat dry predictably
hazards danger risks risk hitandmiss erratic loose endszzz
""")

# Phrases are treated as semantic units, so that their constituents need
# not have the same polarity as the whole expression.
_P = {}


def _phr(score, strings):
    for p in re.split(r"\||\n", strings):
        key = tuple(_tokens(p.strip()))
        if key:
            _P[key] = score


_phr(4.25, """
tour de force|tour de forces|must see|must watch|not to be missed|do not miss|don't miss it
see it twice|highly recommend|very highly recommended|two thumbs up|thumbs up|standing ovation
top notch|top drawer|top flight|top of the line|best of the year|year's best|one of the best
among the best|one of the finest|best movies|best films|best comedies|best pictures
an instant classic|a minor classic|a modern classic|a new classic|a class of its own|in a class by itself
leaps off the screen|leap off the screen|blows you away|blow you away|blown away|blew me away
knocks it out of the park|knocks your socks off|knock your socks off|will blow you away
worth every penny|worth every minute|worth the price of admission|worth the ticket price
does not get much better|doesn't get any better|as good as it gets|nothing like it
a breath of fresh air|breath of fresh air|a joy to behold|a wonder to behold|a sight to behold
more fun than a barrel of monkeys|a feast for the eyes|feast for the senses|a thing of beauty
edge of my seat|edge of your seat|edge of their seats|edge of our seats|edge of the seat|edge of its seat
can't take your eyes off|cannot take my eyes off|couldn't take my eyes off|will not be disappointed
can't go wrong|could not be better|couldn't be better|can't get enough|couldn't get enough
""")
_phr(3.15, """
well done|well made|well crafted|well acted|well directed|well written|well told|well shot|well observed
well conceived|well constructed|well developed|well rounded|well cast|well drawn|well executed
well deserved|well paced|well staged|well played|well worth|well realized|well realised|well tuned
well worth seeing|well worth watching|finely crafted|finely tuned|finely wrought|finely drawn
first rate|first class|first tier|high caliber|high calibre|first order|a cut above|several cuts above
state of the art|world class|oscar worthy|award worthy|award winning|award winner|best picture
pitch perfect|note perfect|letter perfect|dead on|spot on|right on target|hits the mark|on the mark
on the money|right on the money|hits home|rings true|ring true|feels true|feels real|feels alive
comes alive|come alive|bring to life|brings to life|brought to life|breathes life|breathes new life
worth seeing|worth watching|worth a watch|worth a look|worth checking out|worth seeking out|worth a trip
worth the trip|worth your time|worth the effort|worth the wait|worth catching|worth visiting
won me over|wins you over|won my heart|won't regret|will not regret|highly entertaining
a good time|a great time|a grand time|a swell time|good fun|great fun|pure fun|sheer fun
loads of fun|lots of fun|more fun|so much fun|a lot of fun|fun to watch|fun to see|a real treat
real deal|real thing|good stuff|great stuff|the right stuff|goods to back|delivers the goods
gets it right|gets everything right|gets things right|gets the job done|pulls it off|pull it off
all the right notes|right notes|pushes all the right|clicks into place|comes together
hits its stride|finds its footing|in its stride|finds a rhythm|fires on all cylinders
stands out|stand out|stands apart|stands up well|holds up|hold up well|holds its own
out of the ordinary|one of a kind|breaks new ground|break new ground|breaking new ground
new ground|a fresh take|a fresh look|a fresh spin|a fresh twist|something new|something special
pleasant surprise|nice surprise|pleasantly surprised|unexpected pleasure|exceeds expectations
better than expected|better than it sounds|better than it looks|exceeded my expectations
more than meets the eye|more than the sum|greater than the sum|overcomes its|rises above|rise above
a winning combination|winning performance|steals the show|steal the show|steals every scene
scene stealing|scene stealer|star making|at the top of his game|at the top of her game|in top form
in fine form|in great form|at his best|at her best|at their best|never been better
big screen|cinematic experience|visual feast|eye candy|visually arresting|visual treat
eye popping|jaw dropping|mouth watering|drop dead gorgeous|larger than life
mind blowing|mind bending|thought provoking|thought provokingly|food for thought|makes you think
makes us think|gets you thinking|stays with you|stay with you|sticks with you|gets under your skin
under my skin|under the skin|lingers long after|long after the credits|long after it ends
on the edge|heart pounding|pulse pounding|white knuckle|nail biting|nerve jangling|spine tingling
keeps you guessing|keeps us guessing|keeps you on|keeps you hooked|keeps you interested
never lets go|never lets up|never let go|doesn't let go|does not let up|doesn't let up
never flags|never flag|never drags|never lags|never falters|never wavers|never loses sight
holds your attention|holds my attention|holds our attention|commands attention|grabs you|grabbed me
packs a punch|pack a punch|packs an emotional punch|emotional punch|a wallop|a knockout
hits you|hit home|strikes a chord|struck a chord|tugs at|pulls at|tug at|heart strings|heartstrings
tear jerker|tearjerker|moved to tears|brought me to tears|bring you to tears|leaves you breathless
full of heart|has heart|with heart|a big heart|its heart in the right place|heart in the right place
labor of love|labour of love|clearly cares|cares deeply|loving tribute|love letter|true to life
slice of life|human touch|all too human|down to earth|warts and all|fully realized|flesh and blood
three dimensional|multi dimensional|multi layered|fully formed|well fleshed out|fleshed out
feel good|feelgood|crowd pleaser|crowd pleasing|audience pleaser|family friendly|for all ages
kids will love|children will love|you will love|you'll love|will love it|will like it|will enjoy
will not disappoint|does not disappoint|did not disappoint|never disappoints|never disappointed
not disappoint|does not hurt|never hurts|no mean feat|no small feat|no easy feat|no mean achievement
no slouch|no accident|no denying|cannot be denied|can't be denied|impossible to resist|hard to resist
hard not to like|hard to dislike|impossible not to like|hard not to love|can't help but love
nothing wrong with|nothing wrong|not half bad|not too bad|isn't half bad|ain't half bad|none too shabby
no complaints|never a dull moment|not a dull moment|never dull|never boring|anything but boring
far from dull|anything but dull|anything but predictable|anything but ordinary
laugh out loud|laugh out loud funny|laugh aloud|laugh a lot|belly laugh|belly laughs|bellylaughs
big laughs|big laugh|genuine laughs|real laughs|good laughs|good laugh|had me laughing
made me laugh|made me smile|had me smiling|smile on your face|laugh yourself silly
wickedly funny|wicked fun|wickedly entertaining|wicked sense of humor|sharp wit|razor sharp
tongue in cheek|witty one liners|deadpan humor|dry humor|black humor|dark humor|black comedy
guilty pleasure|guilty pleasures|infectious energy|sheer energy|high energy|great chemistry
comic timing|great comic|comic genius|comic gold|comedic gold|bona fide|soars above|flies by
time flies|fly by|moves like|moves along|moves briskly|never outstays|doesn't overstay
fast paced|well oiled|quick witted|fast moving|action packed|fun filled|high spirited|high spirits
roller coaster ride|roller coaster|a great ride|a wild ride|a fun ride|a heck of a|a hell of a
slam bang|rip roaring|rip snorting|old fashioned fun|knockout performance|hidden gem|little gem
a kick out of|a kick to watch|get a kick|get a thrill|can't wait to see|deserves to be seen
deserves an audience|deserves a wider audience|go see it|run out and see|go and see|go see this
should see|don't let the|do yourself a favor|put a smile|puts a smile
""")
_phr(1.6, """
not bad|not terrible|not awful|isn't bad|wasn't bad|not a bad|not without|not entirely without
not for everyone|not for everybody|not everyone's|not your typical|not your average
more often than not|more often than it doesn't|better than most|better than average|above average
for the most part|for once|for a change|at its best|when it works|what works|on its own terms
makes up for|makes the most|make the most|has its moments|have their moments|has its charms
in a good way|in the best sense|in the best possible way|in its own way|does its job
gives us|offers us|takes us|invites us|reminds us|shows us|allows us|lets us
casts a spell|works its magic|works its way|much to admire|a lot to like|plenty to like|much to like
plenty of|more than enough|no shortage of|in good hands|in capable hands|thanks to
hold together|hangs together|works well|works as|pays off|pay off|paid off
a welcome change|takes risks|takes chances|not afraid|unafraid to|takes a chance|dares to
does justice|did justice|does credit|to its credit|to his credit|to her credit
old school|old fashioned|low key|small scale|a sense of|its share of
stylishly shot|worthwhile viewing|good looking|good natured|easy going|light hearted|big hearted
dry wit|wry humor|even handed|sure handed|sure footed|sure hand|light touch|sure touch|nice touch
""")
_phr(-4.3, """
waste of time|waste of money|waste your time|wasting your time|a total waste|a complete waste
waste of talent|waste of celluloid|waste of film|wasted opportunity|minutes of my life
want my money back|want my time back|save your money|save your time|stay away|avoid at all costs
steer clear|give it a miss|give this a miss|skip it|skip this one|thumbs down|two thumbs down
not worth seeing|not worth watching|not worth the|not worth your|not worth it|not worth a|no redeeming
nothing to recommend|little to recommend|cannot recommend|hard to recommend|cannot be recommended
could not recommend|not recommended|no reason to see|no reason to watch|not much reason to
worst of the year|one of the worst|all time low|a new low|bottom of the barrel|scraping the bottom
as bad as it gets|so bad it hurts|too awful|dead on arrival|train wreck|trainwreck|unmitigated disaster
piece of crap|piece of junk|piece of garbage|piece of shit|pile of crap|pile of junk|pile of garbage
a bad movie|a bad film|makes no sense|make no sense|makes absolutely no sense|mind numbingly
mind numbing|numbingly dull|boring as hell|watching paint dry|watching grass grow|root canal
boring as watching|put me to sleep|puts you to sleep|put you to sleep|bored to tears|bored stiff
painful to watch|pain to watch|chore to watch|hard to sit through|a chore to sit through
hard to stay awake|stay awake|fight to stay awake|checking my watch|looking at my watch
wanted to walk out|walked out|cannot wait for it to end|can't wait for it to end
cannot end soon enough|couldn't end soon enough|end soon enough|over soon enough
not funny|isn't funny|wasn't funny|never funny|not even funny|no laughs|not a laugh|never a laugh
could not care less|couldn't care less|who cares|who could care|i don't care|you won't care
""")
_phr(-3.15, """
not very good|not particularly good|not that good|not much good|not any good|isn't very good
not good enough|isn't good enough|not enough to save|not enough to make|can't save|cannot save
can't rescue|could not save|can not quite save|can't salvage|cannot redeem|beyond redemption
not even close|not even remotely|not much of a|not much of an|not much more than|not much else
not up to|not nearly enough|not quite enough|never quite|doesn't quite|doesn't really work
doesn't work|does not work|didn't work|never works|never really works|never comes|never gets
never makes|never manages|never catches|never finds|never finds its footing|never achieves
never rises|never takes off|doesn't take off|fails to take off|never gets off the ground
never adds up|doesn't add up|does not add up|never pays off|does not pay off
doesn't deliver|fails to deliver|fails to live up|doesn't live up|never lives up
misses the mark|miss the mark|off the mark|falls short|fall short|comes up short|falls flat
fall flat|fell flat|falls apart|fall apart|comes apart|falls to pieces|loses its way|lose its way
loses steam|runs out of steam|runs out of gas|runs out of ideas|goes nowhere|go nowhere
goes on forever|goes on and on|way too long|far too long|much too long|too long|too little too late
wears thin|wear thin|grows tiresome|wears out its welcome|wear out its welcome|overstays its welcome
outstays its welcome|bogs down|bogged down|gets bogged|weighed down|drags on|drag on
dead in the water|dead weight|dead end|dead on its feet|going through the motions|go through the motions
by the numbers|by numbers|paint by numbers|connect the dots|assembly line|cookie cutter
cut and paste|off the shelf|run of the mill|garden variety|same old|same tired|same thing
been done before|all been done|been there done that|seen it all before|seen before|seen it before
have seen before|seen a hundred times|seen a thousand times|nothing new|nothing original
offers nothing|adds nothing|nothing more than|nothing but|little more than|no more than
poor man's|poor imitation|pale imitation|watered down|pales in comparison|pale in comparison
not nearly as|nowhere near as|not in the same league|second rate|third rate|fourth rate|cut rate
low rent|low grade|b movie knockoff|bottom drawer|poorly made|badly made|bad acting
bad writing|bad taste|leaves a bad taste|in bad taste|in poor taste|ill conceived|ill advised
ill suited|half baked|half hearted|half assed|half cooked|paper thin|wafer thin|razor thin
one dimensional|two dimensional|one note|one trick|cardboard cutouts|stick figures
thin on|short on|long on|devoid of|devoid of any|woefully short|sorely lacking|lacking in
full of holes|plot holes|gaping holes|holes in the plot|loose ends|all over the place
all over the map|doesn't know what|can't decide|cannot decide|identity crisis|mixed bag
no idea|no clue|no point|little point|what's the point|no good reason|no apparent reason
no discernible|no real|no sense of|has no|have no|with no|far too|way too|much too
too many|too much|too bad|too late|too little|too few|too often|all too often|tries too hard
trying too hard|try too hard|strains for|strains to|strain to|labors to|tries desperately
takes itself too seriously|take itself too seriously|takes itself seriously|self serious
self important|self importance|self indulgence|self indulgent|self satisfied|self congratulatory
heavy handed|heavy handedness|ham fisted|ham handed|heavy going|hard going|hard slog
hard to follow|hard to believe|hard to care|hard to tell|hard to imagine|hard to sit|hard to swallow
difficult to follow|difficult to care|impossible to care|nothing to care|couldn't care
little to care|hardly worth|hard pressed|tough to sit|leaves much to be desired|left much to be desired
leaves a lot to be desired|to be desired|at a loss|in over his head|out of his depth|off the rails
wants to be|wants desperately|does its best to|could have been|could have used|could use
would have been|should have been|should have stayed|better off|better left|better served
better suited|better suited to|would be better|deserved better|deserves better|seen better
seen worse|a better film|a better movie|a better script|all the wrong reasons|for the wrong reasons
for all the wrong|what went wrong|went wrong|wrong with|doesn't belong|unfortunate enough
a good idea on paper|sounds better on paper|looked good on paper|good on paper|looks good on paper
good intentions|best intentions|best of intentions|its intentions|noble intentions|well intentioned
well meaning|wasted on|talent on display is wasted|waste of|more is the pity|a pity
a shame|too bad|sad to say|sad to report|toxic waste|cheap shot|cheap shots|cheap laughs
low common denominator|lowest common denominator|dumb down|dumbing down|dumbed down
insult to|insult the intelligence|insults the intelligence|intelligence of the audience
cringe inducing|eye rolling|roll your eyes|rolling your eyes|rolled my eyes|eye roll
laughing at it|unintentional laughs|unintentionally funny|unintended laughs|laugh for the wrong
at best|at worst|only saving grace|only good thing|only reason to see|only reason to watch
best thing about|only bright spot|only redeeming|only thing worth|only thing good
don't bother|need not bother|cannot be bothered|better things to do|should have known better
made for tv|direct to video|straight to video|made for cable|movie of the week|tv movie
straight to dvd|movie of the week|sitcom pilot|after school special|afterschool special
music video|video game|all style|style over substance|more style than substance|dime a dozen
would be funny if|can't even|doesn't even|didn't even|not even the|only in the movies
one big yawn|big yawn|a bust|a dud|a clunker|a dog|a stiff|no fun|not fun|isn't fun
""")
_phr(-1.7, """
less than|rather than|instead of|if only|only if|as if|as though|seems like|seems to be
seems to think|seem to think|have to wonder|makes you wonder|one wonders|makes one wonder
not sure|not clear|not certain|a bit of a|a little too|a bit too|kind of a mess
except for|apart from|in spite of itself|in spite of himself|on the surface
just another|yet another|yet one more|just a little|little else|for the sake of|for its own sake
at times|a few moments|off and on|here and there|more of the same|goes through
a long way from|a far cry from|a step down|a missed|seems content|content to
would like to have|i wish|you wish|you might wish|would rather|expect more|expected more
you expect|you would expect|as expected|as usual|this time around|for die hard|die hard fans
fans only|probably best|only fans|may appeal to|might appeal to|only for
bites off more|bit off more|off more than|formula picture|simply a|tries to be
an excuse|serves as an excuse|an attempt|attempt at|long stretches|at arm's length
leaves you cold|leaves me cold|left me cold|keeps you at|straight face|hardly a
left wondering|what might have been|not my idea|expects us to|wants us to|asks us to|meant to be
""")
# Non-evaluative idioms and common misleading collocations.
_phr(0.0, """
not only|not just|not merely|not simply|not to mention|not so much|not unlike|not least
no matter|no doubt|no doubt about|no wonder|no less|no less than|nothing less than|nothing short of
little short of|all but|all too human|if not|whether or not|like it or not|believe it or not
no longer|never mind|no sooner|not necessarily|no other|no one|no one else|no two
not to say|not to be confused|no pun intended|lest we forget|in no time|have no doubt
not surprisingly|not surprisingly enough|never before|nothing if not|nothing quite like|without a doubt
without doubt|without question|without fail|without ever|whether you like|not the only
can hardly wait|can not help but|can not help|can not help feeling|can not help thinking
can not help wondering|could not help but|could not help|hard not to|impossible not to
cannot help but|can not deny|can not be accused|no stranger|no strangers|does not shy away
doesn't shy|not afraid to|nothing to do with|without further ado|the last thing|no holds barred
of the worst|bad guy|bad guys|bad boy|bad boys|bad girl|bad girls|bad cop|bad taste in|bad news
good guy|good guys|good girl|good and evil|good old boy|good old boys|good cop
too good to be true|worst nightmare|worst fears|worst enemy|best friend|best friends
best known|best selling|best seller|best laid|better known|better half
love story|love stories|love affair|love interest|love life|in love|falls in love|fall in love
make love|lost love|unrequited love|first love|love triangle|hate crime|hate crimes
tough guy|tough guys|white trash|serial killer|serial killers|killer instinct|shooting star
cheap seats|hard times|hard time|hard life|hard work|heavy metal|heavy weight
high school|low budget|low cost|big budget|big screen|small screen|small town
too late to|too soon to|can do no|take no|lose no|loses no|need no
kind of|sort of|a kind of|a sort of|like a|like an|like the|looks like|look like|much like
would like to|would love to|in the end|bad things|terrible things|terrible events
special effects|visual effects|sound effects|comic book|comic books|graphic novel
film noir|hard boiled|dead body|dead bodies|dead man|evil spirits|evil spirit|death penalty
killer whale|killer shark|of evil|pretty girl|pretty face|pretty boy|great depression
world war|civil war|true story|based on|working class|middle class|upper class
""")
# Additional lexical distinctions.
_words(3.1, """
best finest loved adore adored adores favorite favourite favorites favourites
uncommonly surpass unsurpassed uncommonly consummate consummately
succeeds successful remarkable remarkably splendor splendour grandiosezzz
crowdpleasing showstopper showstopping showpiece standout spellbinder
entranced enchantment galloping buoyantly pleasurably pleasurable
welcome welcomed freshness reinvention gleeful gleefully smartly intelligent
sophisticated sophistication simplyzzz cooler coolest nifty terrific
jewel jewels nifty crackerjack knockabout kickass badass rollicking
unnervezzz entrancing uncommonly absorbing arresting beguilingly
fearlessness irrepressible irrepressibly captivatingly beguiles
magnanimous exhilaratingly super superlatives stupendous wonderfulness
deliciously darklyzzz inspired inspiredly compellingly watchability
resounding perfection immaculately immaculate laudably dazzling bolsters
deftness lucidity sublimity spellbinds spellbind luminous bliss blissful
tantalizes charms charmingly polished triumphantly excellent toweringly
richly pleasurably exceedinglyzzz admirable humbling masterstroke
hysterically hilariously funnier wittier cleverer smarter reinvigorating
""")
_words(1.7, """
love loves likeable liked fond enjoyably candidly handsomely
strikingly quietlyzzz measurably aplomb panache flair gusto brio élan elan
flair flair flourishes flourishing marveling marvelous wondrously
tasty tastier sunnily sunny brightly bright brightly zestful zestfully
palpable tangible immersion immediacy immediateness vitality vital
crafts staging pictorial painterly literate literary philosophical literate
idiosyncrasy idiosyncrasies quirkiness quirk individualistic iconoclastic
fearlessness alchemy ingenuity inventively ingenious exuberantly
crowdpleasing highbrow innocuous wholesome lovable familyfriendly
sweetly sweetened sassiness eccentricity pleasantness uninhibited
robustly boldness straightforwardness briskly fastpaced breathless
disturbingly wondrously chilling chills shivers goosebumps gooseflesh
uncanny eerily spooky dread suspense shocks deftly
tense tension scary scares unnerves frightening frighteningly
mystique mystery mysticism hypnotically hauntingly
longing empathy pathos humanism gravitas perspective perspectives
meaningful meaningfully touching touches humane humanity charitable
enlightenment understanding enlightening entertains entertain entertained
entertainments merrily meditate romancezzz revel revels relish relishes
larkish merrymaking studious playful playfully zingers zinger spark sparks
winking wickedly irreverently absurdist absurdism endearingly
deadpan deadpanned hilariously satirizes lampoons skewers skewering
provokes provocation provoke provoking discussion provocative
tickle respite tonic tasty tasty crowdpleasing flamboyant flamboyance
tasty topnotch straightforward classy classiest classy
grandly grand gigantic dazzlingly extravaganza spectacle spectacularly
fittingly fitting neatly sharpness exacting shrewd shrewdly keen keenly
neatly effortless effortlessly seamless seamlessly fluid fluidity
revels infuses infusing suffused brims brimming bristles exudes
heartening poignant redemptive redeem invigorates conveys excitingly
honors pays homage respectful respect respectfulness legitimately
clearsighted satirist endurably enduring lasting timeless timely
twisty twisty twists intricacies intricate delicately delicacy
franklyzzz goodnatured humane magnified maintains prevails
laughs laugh snickers chuckles smiles startling revelatory rhapsodic
""")
_words(-3.1, """
worst awfulness awfully horridly horribly abject abjection abyss
puerility triteness hackneyed hackwork hackney subliterate illiterate
rippingoff junkpile trashcan stinkbomb stinker snoozefest sleepwalk sleepwalks
blandly blandest dully stultifying stupefying stupefy stultifies
lackadaisical lackadaisically slothful languishes languish lifelessly
cobwebbed mothballed moldy mouldy musty dusty mustiness
icky ickiness queasy nausea nauseated distaste distasteful distastefully
skimpy sketchy underbaked underdone threadbare shopworn shabbily shabby
threadbare slapdash sloppiness lumpy haphazardly hamhanded overearnest
unrelatable unappealingly ostentatious archlyzzz condescends patronize
gimmickridden derivative overcomplicated overwrites overwritten
unfathomable unfathomably incomprehensibly confusingly slogs slog
dissipates dissipated lurches lurching screeches screamszzz careens
unexcitingly unforgivably bummer bummer bumbling unpromising
dismally miserably dreadfully pathetically hideous hideously grotesquely
unpleasantly lamentable lamentably woeful woefully hopeless hopelessly
badness awfulness anachronisms shameless shamelessly shame shameful
obnoxiously repulsively rankle rankles rankling aggravates maddening
offensively intolerably intolerable unpalatable toxic noxious pernicous
unintentional awfulness irritable irritatingly dullsville agonizingly
overrated overrated oversold oversells overreaches undeserving unworthy
cloaked boggles botches bollocks shambles scrambled slipshod
shudderingly creaky creakiness creaking wheezy wheezing moldy
muddledness artificial contrivance fraudulent fakery fakest
ballisticzzz ineffectual ineffective ineffectively unjustified
sleazy sleaze turgid torpid drear oafish leadenness deadening
flabby fatty padded padding bloats slack slackness slackens
wanly pointless futile fruitless wasteful abyssal desultory
revoltingly contemptible appallingly lament mournzzz unmitigatedzzz
delusional deplores exploitive unamusing unexcited disenchant
unintentionally uninspired insincerity insincere insipidly
gruesomely problematic letdowns
""")
_words(-1.65, """
mediocrity miscast miscasting castingzzz miscasting wrongheaded
overkill hollowly solemnity superficialities overbusy overelaborate
hyperactive hyperactivity hyperkinetic hyperbole overweening leadenly
excessively overburdened crammed overburdens burdens burdened
overfamiliar overexposed unnecessary unnecessarily wasted needlessly needless
filler clutter cluttered overextended overstretched protracted prolonged
unfocused muddiness ramble rambles meanderingly stumbles missteps
faulty unevenly oddly inexplicable inexplicably illogical inexplicable
implausibly preposterously inexplicable implodes steals appropriates
thinly veiled shallowly hype hyped overhyped commercialized crassly
frenzied hurried hurriedly rushed disorganized disorganised unconvincingly
artless artlessly gracelessly clunkily gracelessness sketchiness flatly
formulae formulaic patly pat glibly flimsily unavoidably instantlyzzz
pallidly cutesy cutezzz coy coyly coyness cutesiness gratingly
noisily blaring blares squanders overstays outstays
unfocused subplots overpopulated unexplored truncated unresolved
unabashedlyzzz bluntlyzzz sermon sermonize sermonizing propagandistic
propaganda moralizing moralistic dogmatic liberalzzz
embarrass embarrasses ridiculousness sillier silliest erratic
reckless incompetently dubious dubiously desperation formless shapeless
rudderless solipsistic indulgences solipsism narcissism narcissistic
underscoreszzz apathy apathetic reluctant reluctantly ambivalence weary
dispiriting dispirited tiresomely evasive emptyhanded
indecipherable unintentionally scattered predictably
hijinkszzz debased disposable disposability who-cares
deficiency deficient deficiencies nonexistent lumberingly
unjust unappealingly lameness disappointment overlookedzzz
""")
# The same word can have both genre/descriptive and evaluative senses.
# Keep only weak evidence for these when no more specific phrase matched.
_words(0.38, """mystery respect crafts twists maintains study journey even intimate
quietly drama moviegoers cinematic portrait study human personal tension
raw epic characterizations stark chills sad melancholy disturbing violentzzz
sadness powerfulzzz scope romanticzzz naturalistic daringzzz
""")
_words(-0.55, """sentimental bleak grim cold risk risks harsh slight apparent
uncomfortable gory violent cruel supposedly routine heavy loud grimly surface
difficult tricks cheap glossy flat dry familiar bleakness
""")
_words(2.2, """depth surprising laughs laugh finestzzz intelligent interestzzz unusual
oftenzzz charmingzzz delightfulzzz engagingzzz admirablezzz smartly resonant deftly
resonance special specialness affectionate wholeheartedly pluck wit hilariously
winner fresh enoughzzz worthwhile works solid courage achievement grip grips
enthrall enthralls awed awestruck eyeopening innocence innocently
captures savors savours undeniable undeniably honest tender touchingly
lovingly lively likeable keenly beautifully moving thoughtful captivating
prettyzzz likability likeability inviting livewire relish rivetingly
""")
_words(-2.3, """flat flatness precious affected wrong wrongheaded ridiculous
unbelievably unbelievable unbelievablezzz disappointing missing missingness
dated outdated empty elusive mess lags ploddingly tediousness
dated gimmicks badness offensivezzz stale cheaply stagey stagy amateur
""")
# Delete scope operators; they will be evaluated with their complements.
for _w in ("lacks lack lacks lacking devoid bereft hardly scarcely barely rarely "
           "simply almost overly enough less only never not without too more").split():
    _LEX.pop(_w, None)

# Context templates that address constructions which cannot be fully described
# by a fixed adjacent phrase. Patterns run on a space-tokenized sentence.
_RE_RULES = []


def _rx(v, patterns):
    for pattern in patterns.strip().splitlines():
        pattern = pattern.strip()
        if pattern:
            _RE_RULES.append((re.compile(r"(?<!\S)(?:" + pattern + r")(?!\S)"), v))


_rx(3.6, r"""
(?:one|among|ranks among|easily one) of (?:the|this year is|[a-z]+ is) (?:very |all time )?(?:best|finest|greatest|funniest|smartest|most enjoyable|most entertaining|most effective)
one of the (?:most|more) (?:original|enjoyable|inventive|convincing|striking|engaging|moving|entertaining|accomplished|interesting|memorable|thoughtful|beautiful|powerful|touching|affecting|intelligent|exciting|witty|charming)
(?:well |certainly |definitely )?worth (?:the |your |a |re)?(?:price of admission|trip to the (?:cinema|theater|theatre)|time and money|watching|seeing|a look|seeking out)
(?:a|an) (?:real |genuine |rare |absolute |sheer |pure |unexpected |total )?(?:joy|pleasure|delight|treat|blast|hoot|riot|revelation) (?:to watch|to behold|from start to finish)
(?:hard|difficult|tough|impossible) (?:for [a-z]+ )?not to (?:smile|like|enjoy|love|laugh|admire|be moved|be impressed|appreciate|respect|be charmed)
(?:impossible|hard|difficult|tough) to (?:resist|dislike|fault|forget|beat|top)
(?:never|not) (?:once |ever |remotely |even |for a moment )?(?:dull|boring|tedious|predictable|disappoints|disappointing|boring|cloying|mawkish)
(?:never|rarely) (?:loses|lets go of) (?:its grip|your attention|its hold|its momentum|sight of)
(?:not|never) (?:be |even |at all |remotely )?(?:disappointed|bored)
(?:does not|did not|will not|never|rarely) (?:ever |really )?(?:disappoint|overstay|outstay|succumb|resort to|sacrifice|condescend|feel forced|feel contrived|feel stale)
(?:succeeds|manages|works) (?:brilliantly|wonderfully|beautifully|surprisingly well|admirably)
(?:can not|could not|hard to|impossible to) (?:take|tear|keep) (?:my|your|our|one is) eyes (?:off|away)
(?:will|would|can|should|to|is sure to|is likely to) (?:keep|leave|have) (?:you|viewers|audiences|us) (?:guessing|wanting more|in stitches|laughing|thinking|smiling|cheering|breathless|hooked)
(?:will )?(?:leave|leaves|left|puts|put) (?:you|us|me|viewers) (?:with a smile|breathless|wanting more|in awe|in stitches)
(?:you|we|i) (?:will |may |just might )?(?:want to|will want to) (?:see|watch) (?:it|this|this one) again
(?:justifies|worth|worthwhile for) (?:the )?(?:ticket|price of admission)
(?:never|rarely|seldom) (?:has|have) [a-z]+ (?:been|looked|seemed|sounded|done) (?:so |this |as )?(?:good|better|alive|beautiful|funny|convincing|entertaining|appealing)
(?:makes|made|making) (?:you|us|me) (?:laugh|think|smile|care|feel|want to see)
(?:i|we) (?:absolutely |really |just )?(?:loved|love|enjoyed|liked|adored|recommend) (?:it|this|the film|the movie|every)
(?:many|much|a lot|plenty|lots|something|so much) (?:here |about it )?to (?:like|love|admire|recommend|enjoy|appreciate|savor)
(?:even |far |much )?better than (?:it sounds|it looks|you expect|you might expect|expected|most|the original|average|it has (?:any|a) right)
""")
_rx(-3.8, r"""
(?:one|among) of the (?:very )?(?:worst|dullest|lamest|least|most disappointing|most boring|most tedious|most offensive)
(?:nothing|little|not much) (?:here |in it )?to (?:like|admire|recommend|enjoy|savor|care about|praise|love|appreciate|offer|say)
(?:i |one |you )?(?:wish|wished) (?:i |it |this |there |they |he |she |someone |the (?:movie|film|script) )(?:had|were|was|would|could|had been)
(?:a|an|another) (?:total |utter |complete |terrible |criminal |colossal |shameful )?waste of (?:your |our |my |its |a |the )?(?:time|money|talent|effort|film|celluloid|energy|opportunity|space|resources)
(?:as |about as )?(?:interesting|entertaining|exciting|much fun|funny|appealing|enjoyable) as (?:watching|a root canal|a trip to the dentist|a trip to the dmv|a tax audit|a headache|a funeral|a wet)
(?:the |a )?(?:only|best) (?:really |remotely )?(?:good |decent |funny |interesting |enjoyable )?(?:thing|part|reason) (?:about|in|of|to (?:see|watch))
(?:can not|could not|does not|did not|never) (?:even |quite |really |possibly |begin to )?(?:save|salvage|redeem|rescue|compensate|make up for|make up|work|add up|engage|convince|persuade|entertain|muster|overcome|sustain|cohere|come together|take off)
(?:the |its |even the )?(?:best|fine|good|great|talented|appealing|terrific) (?:cast|actors|performances?|efforts?) (?:can not|could not|are wasted)
(?:even|not even) (?:a |an |the |its )?(?:[a-z]+ ){0,3}(?:cast|performance|actor|actress|director|script|ending) (?:can not|could not|can save|can rescue|could save)
(?:leaves|left|leaving|keeps) (?:me|you|us|viewers|audiences) (?:cold|indifferent|wondering why|wanting|bored|scratching|unmoved|unconvinced|frustrated)
(?:too (?:much|little)|not (?:nearly )?enough) (?:of a |of an |of the )?(?:good thing|reason|story|plot|humor|humour|laughs|wit|charm|energy|substance|talent|interest|suspense|originality|fun|entertainment)
(?:sorely |sadly |seriously |conspicuously |noticeably )?(?:lacking|missing|absent) (?:in|here|from|is) (?:any |the |real )?(?:wit|energy|charm|fun|interest|laughs|humor|humour|subtlety|depth|originality|heart|magic|spark|imagination)
(?:where|what) (?:is|are|happened to) the (?:laughs|humor|humour|fun|jokes|charm|story|plot|wit)
(?:no|few|little|not many|not enough|a lack of|an absence of) (?:real |genuine |discernible |sustained |emotional |redeeming )?(?:reason|reasons|sense|point|tension|suspense|chemistry|wit|humou?r|belly laughs|laughs|grace|heart|soul|redeeming|fun|originality|depth|value|interest|surprises|surprise|coherence|plot|personality|substance|talent|qualities|excitement|appeal|entertainment|imagination|charm|energy)
(?:is|are|was|were|feels|seems|becomes) (?:just |simply |ultimately |far |much |entirely |a little |a bit )?too (?:long|much|little|late|thin|obvious|easy|slick|familiar|pat|predictable|slow|broad|cute|self|loud|busy|confusing|conventional|sentimental|contrived)
(?:more|less) (?:annoying|irritating|boring|tedious|frustrating|offensive|depressing|confusing|tiresome|predictable) than (?:it is )?(?:amusing|engaging|entertaining|interesting|fun|funny|exciting|moving)
(?:never|hardly|rarely|not once) (?:really |quite |truly |even )?(?:comes to life|takes off|gels|catches fire|sparks|registers|comes together|gets going|engages|engrosses|connects|reaches|understands|explores|provides|achieves|transcends|rises above|manages|escapes|generates|establishes|delivers|pays off|finds|lets us|lets you)
(?:not|never) (?:nearly |remotely |particularly |especially |all that |very |even |half )?(?:funny|good|interesting|entertaining|convincing|exciting|appealing|scary|engaging|compelling|enjoyable|satisfying|as good|as funny|worth)
(?:strains|tries|works) (?:so |far |way )?too hard
(?:i|you|we) (?:had |would |might |should |could )?(?:rather|sooner) (?:be|have|see|watch|sit)
(?:hard|difficult|impossible) to (?:sit through|stomach|fathom|swallow|recommend|admire|like|enjoy|appreciate|love|sympathize|care|stay awake|keep track|root for|believe)
(?:is|was|has been) (?:not |never )?supposed to be (?:funny|scary|sad|exciting|moving|entertaining)
(?:do|did|does|can|could|would) not (?:really |even |particularly )?(?:care|buy it|buy this|understand why|need another|deserve|hold up|measure up|seem to care|seem to know|care for)
(?:better|best) (?:to |if you )?(?:rent|wait for|avoid|skip|stick with|stay home)
(?:fit|suited|destined) for (?:the )?(?:small screen|video|cable|television|late night)
(?:could|should|might|would) have (?:been |made )(?:a |an |for a )?(?:much |really |very |pretty )?(?:better|good|great|terrific|wonderful|interesting|compelling|funny|fun|entertaining|fine|enjoyable|fascinating|decent|intriguing)
(?:should|could) have (?:used|done|benefited|benefitted|stayed)
(?:not|hardly) (?:a |an |the )?(?:particularly |remotely |very |great |whole )?(?:deal of|success|masterpiece|classic|good movie|good film)
""")
_rx(0, r"""
(?:not|never) (?:only|just|merely|simply)
(?:never|nothing|no) (?:anything )?less than
(?:is not|are not|was not|were not|not) (?:without|devoid of)
(?:without|avoids?|avoiding|eschews?) (?:ever |once |quite |being |becoming |getting |seeming |feeling |resorting to |succumbing to )*(?:mawkish|sentimental|sappy|cloying|overly sentimental|too sentimental|preachy|didactic|melodrama|melodramatic|preachiness|cliche|cliches|condescension|pretension|boring|dull|mushy|cheesy|trite)
(?:not|never) (?:so much|to say|as yet)
nothing (?:else |quite )?like
(?:not|never) (?:going to be |meant to be |intended to be )?(?:for everyone|for everybody|your typical)
(?:do|does|did|will|would|could|can) not (?:have to|need to)
""")
_rx(1.65, r"""
(?:avoids?|eschews?|defies|subverts) (?:all |most |many |the |usual |of |its )*(?:pitfalls|conventions|cliches|traps|stereotypes|expectations|formula)
(?:more|better|funnier|smarter) than (?:just |merely |your |the )?(?:average|usual|typical|most)
(?:as (?:much|good|funny|enjoyable|exciting|entertaining|effective|original)) as
(?:not|never) (?:a |an )?(?:total|complete|utter) (?:loss|failure|waste|disaster)
(?:may|might) not (?:sound|look|seem) (?:like much|promising|appealing)
(?:not|hardly) (?:a |an )?(?:earthshaking|great|perfect|flawless|major) (?:piece of |work of )?(?:cinema|film|movie|art)
""")
_rx(-1.8, r"""
(?:too|more) (?:much|often|many) (?:of |like )?(?:a |an |the )?
(?:any|a) resemblance to (?:a |an )?(?:real|good|actual)
(?:pretends|purports|aspires|aims|tries|sets out) to (?:be|say|do|imitate|make)
(?:only|just) (?:occasionally|rarely|sporadically|intermittently|fitfully)
(?:despite|for all) (?:the |its |their |some |his |her )?(?:charm|energy|wit|appeal|talent|virtues|strengths|ambition|good intentions|promise)
(?:an|a) (?:admirable|worthy|noble|honest) (?:try|attempt|effort|failure)
(?:in|with) (?:a |the )?(?:better|more skilled|more capable) (?:hands|script|director)
(?:not|never) (?:really |quite )?(?:clear|sure) (?:why|how|whether|what)
(?:might|may|could|can) (?:have |well )?(?:appeal to|satisfy|please|amuse) (?:die hard|hard core|hardcore|undemanding)
""")

_NEG = set("""not never hardly scarcely barely neither nor no without lacks lack lacking lacked
devoid bereft fails failed failing fail unable cannot missing misses missing absent avoids avoid
avoiding eschews defies shuns resists ignores forsakes sacrifices forgets forgot forgotten
sacrifice squander squanders wasted wastes wasting denies refuses struggles""".split())
_STRONG_NEG = set("no not never neither nor without lacks lack lacking lacked devoid bereft hardly scarcely unable fails failed avoid avoids avoiding".split())
_INTENS = {"very": 1.25, "quite": 1.08, "so": 1.15, "too": 1.28, "extremely": 1.5,
           "rather": .92, "somewhat": .72, "slightly": .68, "pretty": 1.07,
           "fairly": .82, "completely": 1.35, "wholly": 1.28, "totally": 1.35,
           "truly": 1.23, "really": 1.18, "absolutely": 1.48, "utterly": 1.44,
           "terribly": 1.28, "especially": 1.21, "deeply": 1.32, "incredibly": 1.35,
           "remarkably": 1.22, "surprisingly": 1.18, "particularly": 1.14,
           "occasionally": .57, "sporadically": .57, "intermittently": .57,
           "sometimes": .72, "mildly": .55, "moderately": .65, "painfully": 1.23,
           "reasonably": .77, "merely": .6, "only": .72, "more": 1.12, "most": 1.25}
_BOUND = set(".,;:!?()…")
_STOPNEG = _BOUND | set("but however although though despite yet nevertheless except whereas because since which who that while so then if".split())
_AUX = set("be is was are were been being does did do have has had should could would can may might will must".split())
_FUNC = _AUX | _STOPNEG | set("a an the only one and or of as you me us it i its his their he she they to for with on in from into when at by than any some my this those these there every other what how all much more most many still even ever really very entirely particularly quite just enough".split())
_MAX_P = max(len(p) for p in _P)


def _lex(w):
    if w in _LEX:
        return _LEX[w]
    if w in _FUNC or len(w) < 4:
        return 0
    roots = []
    if w.endswith("ies") or w.endswith("ied"):
        roots.append(w[:-3] + "y")
    if w.endswith("s"):
        roots.append(w[:-1])
    if w.endswith("es"):
        roots.append(w[:-2])
    if w.endswith("ly"):
        roots += [w[:-2], w[:-3] + "y", w[:-1] + "e"]
    if w.endswith("ness"):
        roots += [w[:-4], w[:-5] + "y"]
    if w.endswith("ing") or w.endswith("ed"):
        a = w[:-3] if w.endswith("ing") else w[:-2]
        roots += [a, a + "e", a[:-1] if len(a) > 2 and a[-1] == a[-2] else a]
    if w.endswith("est") or w.endswith("er"):
        a = w[:-3] if w.endswith("est") else w[:-2]
        roots += [a, a + "e", a[:-1] + "y" if a.endswith("i") else a]
    for r in roots:
        if r in _LEX and len(r) >= 3:
            return _LEX[r] * .9
    for pref in ("un", "non", "dis"):
        if w.startswith(pref) and w[len(pref):] in _LEX:
            return -.88 * _LEX[w[len(pref):]]
    return 0


def _units(ts):
    s = " ".join(ts)
    starts = []
    pos = 0
    for t in ts:
        starts.append(pos)
        pos += len(t) + 1
    opts = {}
    for pattern, score in _RE_RULES:
        for m in pattern.finditer(s):
            a, b = bisect_left(starts, m.start()), bisect_left(starts, m.end())
            if b > opts.get(a, (a, 0))[0]:
                opts[a] = (b, score)
    result = []
    i = 0
    while i < len(ts):
        j, val = opts.get(i, (i, 0.0))
        for k in range(min(len(ts), i + _MAX_P), max(i, j - 1), -1):
            key = tuple(ts[i:k])
            if key in _P:
                j, val = k, _P[key]
                break
        if j == i:
            j = i + 1
            val = _lex(ts[i])
        result.append((i, j, val))
        i = j
    return result


def _segments(ts, units):
    weight = [1.0] * len(ts)
    start = 0
    i = 0
    while i <= len(ts):
        if i == len(ts) or ts[i] in (".", "!", "?", ";"):
            sub = ts[start:i]
            for k in range(start, i):
                w = ts[k]
                if w in ("but", "however", "yet", "nevertheless", "nonetheless", "alas", "unfortunately", "thankfully", "fortunately"):
                    if (w == "but" and (ts[max(start, k-1):k] in (["anything"], ["nothing"], ["all"], ["help"]))
                        or w == "yet" and ts[k+1:k+2] in (["another"], ["to"]))
                    :
                        continue
                    if w == "but" and any(tuple(ts[z:z+2]) in {("not", "only"), ("not", "just"), ("not", "merely")} for z in range(start, k)):
                        continue
                    for z in range(start, k):
                        weight[z] *= .50
                    for z in range(k, i):
                        weight[z] *= 1.28
                if w in ("although", "though", "despite", "while", "whereas", "albeit"):
                    end = next((z for z in range(k+1, i) if ts[z] == ","), i)
                    if end == k+1 and w == "though":
                        continue
                    for z in range(k, end):
                        weight[z] *= .60
                if ts[k:k+2] == ["even", "if"]:
                    end = next((z for z in range(k+2, i) if ts[z] == ","), i)
                    for z in range(k, end):
                        weight[z] *= .58
            start = i + 1
        i += 1
    return weight


def _score(ts):
    units = _units(ts)
    weight = _segments(ts, units)
    blocked = set()
    for a, b, val in units:
        if b > a + 1:
            # Composite expressions normally exhaust their internal operators.
            # A few ("has no", "too little", etc.) introduce a complement.
            for p in range(a, b):
                if (p == b - 1 and ts[p] in ("no", "not")) or (ts[a:b] in (["devoid","of"], ["lacking","in"], ["never","quite"], ["does","not","quite"], ["fails","to"])):
                    continue
                blocked.add(p)
    events = []
    used_neg = set()
    for idx, (a, b, v) in enumerate(units):
        w = ts[a]
        left = ts[max(0, a-9):a]
        right = ts[b:b+5]
        if b == a+1:
            if w in _NEG:
                # Lexical verbs of failure etc. are also scope operators.
                if w in ("lack", "lacks", "lacking", "lacked", "devoid", "bereft", "fails", "failed", "failing", "fail", "squanders", "wastes", "wasted", "unable", "struggles"):
                    v = -2.4
                elif w in ("misses", "missing", "forgot", "forgets", "sacrifices", "ignores"):
                    v = -1.55
                elif w in ("avoids", "avoid", "avoiding", "eschews", "resists", "shuns", "defies"):
                    v = .60
                else:
                    v = 0.
            if w == "like":
                v = 2.0 if (left and left[-1] in ("i", "we", "will", "really", "not", "to", "actually", "quite")) else 0.
            if w in ("like", "love", "loves", "loved", "enjoy", "enjoyed") and left[-1:] in (["you"], ["i"], ["we"]) and "if" in left[-4:]:
                v *= .38
            if w == "funny" and right[:1] in (["how"], ["thing"]):
                v *= .50
            if w == "pretty" and right and not _lex(right[0]):
                v = 1.
            if w in ("slow", "slower", "slowly"):
                v = -.95
            if w == "long" and ("minutes" in left or "hours" in left):
                v = -1.2
            if w == "redeeming" and "only" in left:
                v = -1.9
            if w in ("mean", "means") and right[:1] == ["spirited"]:
                v = -5.
            if w == "lack" and left[-1:] == ["not"]:
                v = -2.3
            if w == "worth" and "what" not in left[-3:]:
                v = 1.65
            if w == "deserves" and right[:1] in (["credit"], ["praise"], ["attention"]):
                v = 1.8
            if w == "credits" and "end" in left[-3:]:
                v = 0
            if w == "enough":
                v = .45 if left and _lex(left[-1]) > 0 else 0.
            if w in _INTENS and right and _lex(right[0]):
                v = min(.3, max(-.3, v))
            if w == "too" and (not right or right[0] not in _BOUND):
                v = -1.1
            if w == "little" and (a == 0 or ts[a-1] not in ("a","the","this","his","her","their","that","my","with","charming","funny","nice","sweet","good")):
                v = -1.1
            if w == "few" and (a == 0 or ts[a-1] not in ("a","the","precious","his","her","those","these")):
                v = -1.0
            if w in ("better", "good", "great", "interesting", "fascinating", "funny", "fun", "important", "engaging", "promising", "noble", "intriguing"):
                if any(t in ("premise", "idea", "intentions", "concept", "potential") for t in right[:2]):
                    v *= .35
            if w in ("sad", "terrifying", "scary", "funny", "horrifying", "horrible", "wonderful", "beautiful") and right[:1] in (["world"], ["woman"], ["past"], ["memories"], ["wife"]):
                v *= .30
            if w == "best" and right[:1] in (["efforts"], ["intentions"]):
                v = -1.25
            if w == "better" and right[:1] in (["movies"], ["films"], ["movies"], ["off"]):
                v = -1.35
        if not v:
            continue
        # Don't propagate an operator through a new finite predicate, a
        # comparison boundary or an adversative; do propagate through a list.
        negs = []
        for j in range(a-1, max(-1, a-9), -1):
            t = ts[j]
            if t in _STOPNEG and j not in blocked:
                break
            if t in ("than", "as") and j < a-1:
                break
            if t in _NEG and j not in blocked:
                negs.append(j)
                if len(negs) >= 2:
                    break
            if t in ("and","or") and j < a-1 and any(x in _AUX or x in ("it","they","she","he") for x in ts[j+1:a]):
                break
            if t in ("a", "the", "an") and j > 0 and (ts[j-1] == "of" and a-j > 2):
                break
            if t in _AUX and j < a-1 and (j < 1 or ts[j-1] not in ("not", "never", "hardly", "would","could","should","will","might","can")) and t not in ("be","been","have"):
                break
        if negs:
            used_neg.update(negs)
            if len(negs) % 2:
                # Negating praise is clearer disapproval than negating criticism
                # is approval (e.g. 'not the worst').
                v *= -1.02 if v > 0 else -.80
        elif v > 0:
            # Counterfactual or merely intended praise.
            context = []
            for t in reversed(ts[max(0,a-10):a]):
                if t in _STOPNEG:
                    break
                context.insert(0,t)
            st = " ".join(context)
            if re.search(r"\b(?:(?:could|should|would|might) have (?:been|made)|ought to (?:have been|be)|(?:trying|tries|attempts|supposed|strives|wants) to be|would have liked|(?:needs|needed|deserves|deserved) (?:a|to be)|if only|wish it (?:was|were|had))\b", st):
                v *= -.8
            elif re.search(r"\b(?:far from|less than|anything but|rather than|instead of|short on|little in the way of)\s*(?:(?:being|a|as|the|very|particularly|entirely|that) *)*$", st):
                v *= -.95
            elif re.search(r"\b(?:too (?:little|few)|not enough|not much|little|few)$", st) and not re.search(r"\b(?:a|some|quite a) (?:little|few)$",st):
                v *= -.85
            elif left[-1:] == ["less"] and not (a>1 and ts[a-2] == "no"):
                v *= -.85
            elif left[-1:] == ["too"] and w not in ("funny","good","delicious","beautiful"):
                v *= -.72
            elif right and right[0] in ("is","are","gets","seems") and len(right)>1 and right[1] in ("lost","wasted","gone","missing","lacking","absent"):
                v *= -.85
            elif "if" in ts[b:b+3] and "would" in left[-6:]:
                v *= -.8
            elif left[-1:] in (["occasional"], ["intermittent"], ["fitful"]):
                v *= .35
        if left:
            v *= _INTENS.get(left[-1], 1.)
        # In comparisons the reference point doesn't give independent praise.
        if "than" in left[-4:] and w not in ("expected","most"):
            v *= .52
        if "rather" in left[-6:] and "than" in left[-5:]:
            v *= .55
        if a and ts[a-1] == "despite":
            v *= .55
        events.append((a, v))
    for a, b, _ in units:
        if b == a + 1 and a not in used_neg:
            t = ts[a]
            if t in ("not","never","no","barely","hardly","neither","scarcely"):
                events.append((a,-1.05 if t != "never" else -.92))
    pos = sum(weight[i]*v for i,v in events if v > 0)
    neg = sum(weight[i]*-v for i,v in events if v < 0)
    score = pos - neg
    # Overall discourse cues, particularly useful for short rhetorical blurbs.
    s = " ".join(ts)
    if "?" in ts:
        if re.search(r"\b(?:why (?:did|does|would|bother|on earth|make)|what (?:were|was) they thinking|who (?:needs|wants|cares)|how many more|do we (?:really )?need|what is the point|what happened to|what went wrong|is that all|when will .* (?:end|over)|how did .* get made)\b", s):
            score -= 4.6
        elif re.search(r"\b(?:what more (?:could|can)|who could (?:resist|ask for)|what is not to (?:like|love)|how can you (?:resist|not))\b", s):
            score += 5.3
        else:
            score -= .85
    if re.search(r"\b(?:too bad|a shame|a pity|unfortunate) (?:that|it|the|there)\b|\bif only\b", s):
        score -= 2.45
    if re.search(r"\b(?:not|never) (?:nearly |really |quite |half )?as [a-z]+ as (?:it|the|one|you|its)\b", s):
        score -= 2.2
    if re.search(r"\b(?:might|could|would) (?:have been|have made|be) (?:a |an )?(?:[a-z]+ ){0,2}(?:movie|film|story|comedy) (?:if|in)\b", s):
        score -= 2.9
    if re.search(r"\b(?:only|occasional|one|few) (?:brief |fleeting |bright )?(?:moments|flashes|glimpses|saving grace)\b", s):
        score -= 1.6
    if re.search(r"\b(?:all|just|only|about) (?:you|we|i) (?:could|can) (?:want|ask for|hope for)\b", s):
        score += 3.
    if re.search(r"\b(?:not|never|nothing) (?:quite |nearly |remotely |really )?(?:enough|as good|works)\b", s):
        score -= 1.8
    if re.search(r"\b(?:save|spare) (?:us|yourself|me) (?:from|the)\b|\bdo not waste\b",s):
        score -= 2.8
    if re.search(r"\b(?:not|never) enough\b.{0,40}\b(?:save|redeem|salvage|overcome|compensate|sustain)\b",s):
        score -= 4.
    if re.search(r"\bmore [a-z]+ than (?:a |an |it is )?(?:entertaining|funny|engaging|movie|film|compelling|interesting)\b", s):
        score -= 1.8
    if re.search(r"\b(?:a |one )?(?:star|point)s? (?:out )?of (?:four|five|ten|4|5|10)\b",s):
        score -= 1.8
    for m in re.finditer(r"\b(\d+(?: \. \d+)?) (?:stars? )?(?:/|out of) (\d+)\b", s):
        den = int(m[2])
        if den in (4,5,10,100):
            ratio = float(m[1].replace(" ", ""))/den
            if ratio <= 1:
                score += max(-7, min(7, (ratio - .56)*18))
    if abs(score) < 1.4:
        if re.search(r"\b(?:anyone|everyone|everybody) (?:who |can |will |should )|\b(?:manages to|reminds me of|what makes .* work|has something to say|makes sense|takes you|invites you|draws you|it is a pleasure)\b",s):
            score += 1.25
        if re.search(r"\b(?:what is supposed to|for some reason|we are (?:expected|supposed)|i guess|no one seems|big deal|in theory|that is about it|what is left|seems like|walk out|asks too much|why bother|could be worse)\b",s):
            score -= 1.75
    return score


def predict(state) -> dict:
    tokens = _tokens(_text(state))
    score = _score(tokens)
    return {"answer": "positive" if score >= 0 else "negative"}