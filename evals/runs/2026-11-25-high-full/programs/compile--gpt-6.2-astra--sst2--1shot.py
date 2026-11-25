import re
import unicodedata
from bisect import bisect_left

# Scores are for use in a review (rather than general emotional valence).
_WORD = {}


def _words(n, s):
    for w in s.split():
        _WORD[w] = n


_words(3.6, """
masterpiece masterwork masterstroke magnum luminous sublime sublimely superb
magnificent magnificent magnificently phenomenal extraordinary extraordinarily
exceptional exquisite exquisitely impeccable impeccably breathtaking
breathtakingly spellbinding spellbound mesmerizing mesmerising mesmerizingly
unforgettable indelible indelibly incomparable transcendent transcendental
revelatory revelation glorious gloriously astounding astonishing astonishingly
stunning stunningly spectacular spectacularly brilliant brilliantly brilliance
triumph triumphant triumphantly tourdeforce flawless flawlessly perfection
dazzling dazzlingly dazzling dazzles knockout landmark unparalleled
marvelous marvellous marvelously marvellously wondrous wondrously wonderful
wonderfully amazing fantastic fabulous splendid sensational terrific excellent
outstanding first rate topnotch sterling superlative best greatest genius
geniality virtuoso virtuosic virtuosity masterful masterfully masterly
masterfully priceless essential indispensable unmissable dynamite exquisite
resplendent enthralling enthralled riveting riveted exhilarating exhilaratingly
electrifying electrified rapturous rapture ecstatic ecstaticly ecstaticness
""")
_words(2.65, """
adorable adored adore admirable admiration admirably accomplished accomplishment
achievement accomplished adept adeptly adroit adroitly affectionately affecting
affectionate affirming affirmation alive alluring appealing appeal appetizing
artful artfully artistic assured assuredly astounding astute astutely
atmospheric attractive audacious audacity auspicious authentic authenticity
beautiful beautifully beauty bewitching bittersweet bold boldly bravura bravo
buoyant buoyancy captivating captivates captivated charismatic charisma
charming charmed charms charm delight delightful delightfully delights
delighted delectable delicious deliciously compelling compulsively confidently
confident conviction convincing convincingly cool crackerjack crackling crisp crisply
creative creativity credible creditable crowdpleaser cunning deft deftly
delicate delicately dazzling distinctive distinguished diverting dreamy dynamic
ebullient effective effectively affecting effortless effortlessly elegant
elegance elegantly eloquent eloquence eloquently enchanting enchantment
endearing endearingly enduring energetic energizing engrossing engrossed
engaging enjoy enjoyable enjoyed enjoyment entertaining entertained
entertainment enthrall enthuse enthusiasm enticing entrancing enveloping
evocative evocatively exciting excited excitement exemplary exhilarating
exuberant exuberance expressive extraordinary eyeopening fabulous fascinating
fascinated fascination faultless fearless fearlessly felicitous festive fine
finely finesse finest firstrate fluid fluidity formidable forthright fresh
freshness fulfilling fun funny funnier funniest gallant gem gems generous
genuine genuinely gifted gleeful gorgeous gorgeously grace graceful gracefully
gratifying great greatly gripping gutsy handsome handsomely haunting
hauntingly heartening heartfelt heartwarming hilarious hilariously hilarity
honest honesty honorable humane humanely humanity humorous humorously
hypnotic hypnotically imaginative imagination imaginatively immersive
immensely impactful impassioned important impressive impressively incisive
incisively incredible incredibly infectious ingeniously ingenious ingenuity
innovative innovation insightful insightfully insight inspiration inspirational
inspired inspiring intelligent intelligently intelligence intense intensely
intensity interesting intriguing intriguingly invigorating irresistible
irresistibly irreverent irreverence joyful joyous joy jubilant juicy keen
layered laudable lavish legendary likable likeable lively liveliness lovable
lovely loving lovingly lyrical lyrically lyricism magical magnificence majestic
mature meaningful memorable memorably meticulous meticulously mighty
miracle miraculous mischievous modestly moving moved multilayered nifty nimble
nuance nuanced observant offbeat originality original outstanding passion
passionate passionately perceptive perceptively persuasive piercing playful
playfully playfulness pleasant pleasantly pleased pleasing pleasure pleasures
plucky poignant poignantly poignancy polished potent powerful powerfully
precision profound profoundly provocative provoking pulsepounding punchy
purposeful radiant rapt refreshing refreshingly relatable remarkable
remarkably resonant resonates resounding resourceful respectful rewarding
rich richly richness riotous robust rollicking romantic rousing satisfying
satisfyingly satisfied scintillating seamless seamlessly seductive sensitive
sensitively sensitivity sensual sharp sharply shimmering shine shines shining
shrewd shrewdly sincere sincerely sincerity skillful skilful skillfully
skilfully skilled slickly smart smartly snappy snazzy solid sophisticated
sophistication soulful sparkling sparkles special spirited sprightly stirring
striking strikingly strong stronger stylish stylishly subtle subtlety
successful successfully succeeds sumptuous sunny surprising surprisingly
surreal suspenseful sweet sweetness sympathetic tantalizing taut tender
tenderly tenderness terrific thoughtful thoughtfully thoughtfulness thrilling
thrills thrilled tickled tickles timely touching transcends transformative
treasure tremendous tremendously tribute truehearted truthful uncanny
uncommonly unconventional unexpected unique unpredictable uproarious
uplifting urgent useful valuable vibrant vibrantly vigorous vividly vivid
warm warmth warmly welcome well welcome winning winsome wise wit wittier
wittiest witty worthwhile worthy wow zesty zest zing zippy
""")
_words(1.65, """
accessible accurate acerbic agile agility agreeable alluring ambitious ambition
ambitions amusing amused amusement applauds applaud appreciation appreciate
approachable arresting assured attention absorbing absorbs accomplished
accomplishes accountable acumen affection alive ambitious arrestingly
attracted attraction balanced balls ballsy believable believably beguiling
benefit benefits bestows better bonkers bouncy bountiful bracing brave bravely
breezy breezily bright brightly brio brisk briskly campy candid candidly
canny careful carefully care craftsmanship celebration celebratory challenging
champion cheeky cheerful chutzpah civilized clarity classy clean clever
cleverly cleverness coherent cohesive colorful colourfully colorful colorful
colourful comfortable comic comical committed commitment compassionate
compassion complex complexity compliment confidence conscientious considerable
consistent consistently constructive contemplative contemporary convincingly
courage courageous courageousness courtesy craftsmanship crafty credible
cultured curiosity curious cute dandy daring dares deadpan decent deft
demonstrates dependable depth depths deserving detailed determined dignified
dignity dimension directness disciplined discovery disarmingly disarming
diversion distinctive doable downbeat earthy economical economy edgy educated
effectiveness efficient electric electricity elemental empathetic empathy
emphatic enchant encouraging encourages endear earnest earnestness earns
enlightening enliven enlivens enormously enriching enrich enriched enjoyably
enterprising entertainingly entertainment enviable epic evocative evolving
exact expressive expansive experienced experimental expert expertly expertise
explosive exquisite extraordinary eyeopener fair faithful faithfully favorite
favourite favorably feisty ferocious fertile feverish fidelity fiery finesse
fit fits flair flamboyant flattering flawless flow fluent focused fond fondly
force forceful forcefully frank frankly freewheeling freshness friendly
frothy fulfilled fully functional funky furious giddy gleam gleefully glowing
good goodness goodwill goodwill graceful grounded grownup guts gutsiness
happy happily happiness hardhitting harmony headlong heady healing healthy
heart heartened hearts hearty help helps heroic highest highlight highlights
hilarious homage hook hooked hopeful hope hopes hot human humanistic humane
humble humor humour humorous ideal idealistic idiosyncratic illuminating
imaginative immediacy immediate impact impish impress impressed improves
improvement incisiveness inclusive independent individual individuality
indulgence ingenuity informative informed insight insights instinct instinctive
intact integral integrity intellectual intended intimacy intimate intimately
inventive inventiveness invention invested inviting ironic irony irrepressible
jazzy jolts journey justice justified kaleidoscopic kinetic knowing knowingly
laugh laughter laughs laughing laughed lead lean liberating liberation
lifelike lighthearted lightning luminous literate live lived livelier logic
longevity lush lushly magic makeshift manic marvel marvels master mastery
meaning meditative mesmerizing meticulous merit merits mettle mischievously
modern modest momentum moments mood moody moral motivation muscular musicality
mysterious mystique natural naturally neat neatly necessary nerve nice nicely
nostalgia nostalgic noteworthy notable novelty nourishment observation
observations oddball openness opportunity optimistic optimism organic
outdoes outlandish outstanding pace pacy painless painterly panoramic
paradise particular perceptiveness personable personality perspective
persuasive pertinent pithy plausible playfulness plenty plus poetry poetic
polish popular positive potency praise praiseworthy presence pretty pristine
professional proficient promising propulsive proud provocative prowess
quality quirky quintessential rapid rapport raucous razor readiness real
realism realistic realistically reassures recognizable recommend recommended
reconcile redemptive redemption redeem redeeming refined reflection reflective
refreshing regal relevance relevant relief remarkable rendering renew
reputable reputation resilience resolute resonate resonance respect respects
restrained restraint revealing revels rewards rewarding rhythm rhythmic right
riot risk risks riveting rooted roots satisfying savvy sensational sensibility
sensible sensuous serious seriousness sexy shapely sheer significance
significant simple simplicity singular slick sly smile smiles smiling smarts
smooth smoothly snap soar soaring sociable solidly somber soul soundly spicy
spirit splash splendidly spontaneous spry spunky standout stature steady
steely stimulates stimulating stimulation straightforward strengths stretch
striking sturdily sturdy style stylistic substance substantive substantial
substantiality succeed success sultry superior supercharged surprise surprises
surprised sustain sustains swashbuckling sweetness sympathy talent talented
tangible taste tasteful tautness teasing technical telling terrific texture
textured thematic thoroughly thrill thunderous tight timely tonic topical
touch touches tough tradition transfix transfixing transporting tricky
trust truth truths unaffected unabashed unafraid unapologetic understated
understatement understands understanding unexpected unfailing unfettered
unflinching unique universal unpretentious unpretentiously unsettling unusual
upbeat upstanding uptempo urgency utterly valid value varied variety veracity
versatile vigor vigour vintage visceral vision visionary vital vitality
vivacious voice vulnerable vulnerability wacky watchable weight welcome
whimsy whimsical wholesome wicked wickedly wild willful winner winners
winningly wins wisdom wistful wonders wizardry worldly worth youthful zeal
zen zestful zinger
""")
# These are weak evidence: often parts of descriptions rather than verdicts.
_words(0.65, """
ambition ambitions attention attractive big camp campy care challenge challenges
chance change cheer classic colorful comic considerable contemporary craft crafts
crafted contemporary courage critical culture curiosity curious cute
dark daring deep delicious devastating difficult discovery distinct dramatic
drama dream effort efforts emotion emotional emotionally emotions epic
experience exploration explore explores exploring extreme eye faith family
famous fan fans fantasy feeling fierce filmic filmmaker fitting focus folk
fond force free friendly funnybones future gain generous gentle gently genre
golden grand gritty grow growth happy heart hearts heavy heroic high homage
hope hopes hot human humanity husband iconic idea ideas identity independent
individual influence influences innocent inspiration intended interest interests
ironies ironic irony journey lead live lived life lifetime light look looks
love loved loves lovers lucky manic memory modern modest moment moments mood
moral music mystery nature new observation ominous opportunity pace particular
personal personality perspective picture political popular pretty professional
psychological questions rare raw real reality recognize reference relationship
reminiscent rendering resonances respect return reverence risk risks roots
sad scares scary screen see seemingly seek serious sheer shock shocking
simple simplicity small social somber songs soul spirit star stark story
strange strength strengths stronghold struggle struggles studied style stylistic
subjects successful surreal technical technique thematic thoughtful tone
tradition tragedy tragic true truthful understanding unorthodox unsettling
usually veteran violence vision voice vulnerable wild wonder wonders world
young youthful
""")
_words(-3.65, """
abomination abominable abominably abhorrent abysmal abysmally agonizingly
amateurish amateurishly appalling appallingly atrocious atrociously atrocity
awful awfully badness banality bankrupt bankruptcy barf blight bomb bombs
botch botched bottomless braindead catastrophe catastrophic charmless
cheapo clunker clunkers contemptible contrived crap crappy craptacular crass
cretinous cringe cringed cringeworthy cruddy crud crapola deadening debacle
deplorable deplorably depressing depressingly derisory despicable detest
detestable detritus dire disappointment disappointing disappointingly
disappointed disaster disastrous disastrously disgrace disgraceful disgust
disgusting dismal dismally disposable dreadful dreadfully dreary dreck
drivel dud duds dumbest dumbfoundingly dullest embarrass embarrassment
embarrassing embarrassingly execrable excruciating excruciatingly exhausting
failure fiasco flaccid flop flops forgettable ghastly godawful godforsaken
grating hackwork hackneyed halfassed hamfisted hamhanded hapless harebrained
hateful hideous hideously hokum horrendous horrendousness horrible horribly
horrid horrifically idiocy idiotic idiotically illiterate imbecilic inept
ineptitude ineptly inexcusable inexcusably infuriating insufferable
insult insulting intolerable irredeemable irredeemably irrelevance
irritating junk laughable laughably laughless lifeless loathsome lousy
ludicrous ludicrously mangled meaningless mediocrity mess misbegotten
misbegotten miscalculated miscalculation miserable miserably misguided mishap
mishmash misfire misfires muddle muddled nauseating obnoxious obnoxiously
offensive overwrought painfully pathetic pathetically pointless pointlessly
ponderous ponderously preposterous preposterously pretentious pretension
puerile purposeless putrid repellent reprehensible repugnant repulsive
revolting ridiculous ridiculously rotten rubbish ruined sappy schlock
shallow shambles shameful shamelessly shit shitty shoddy shoddily sickening
silly slapdash slop sloppy sluggish snooze snoozer soporific soulless stinker
stinkeroo stinks stultifying stupid stupidity stupider stupidest stupidly
suck sucks sucky tedious tediously tedium terrible terribly tiresome torturous
torture trainwreck trash trashy travesty tripe ugly unbearable unbearably
unconvincing underwhelming unpleasant unredeemable unwatchable useless
vacuous vapid vile vomit waste wasted wastes woeful woefully worthless
wretched wretchedly worst wtf yawn yawner
""")
_words(-2.55, """
absurd absurdity abusive abysmal accidental adolescent aggravating agonizing
aimless aimlessly alienates amateur amateurism anachronistic anemic anaemic
angry annoying annoyed annoy annoyance annoyingly antagonizing anticlimactic
anticlimax apathetic apathy arbitrary arbitrarily arid arrogance arrogant
artifice artificial artificially artless asinine ass assault astringent
atrocity audienceless awkward awkwardly awkwardness bad badly banal banally
barren bastardized bathos baffling baffled bafflement belabored belaboured
believability beneath bewildering bias biased bizarre bland blandly blandness
blandly blatant blatantly bleak bloated bloat bloodless blunder blunders blunt
blurry bogus bombast bombastic boredom bore bored boring boringly botches
bothersome bottom brash broken brutal brutish buffoon bungled bungles
burden buried bust busy cacophony calculated calculating callow candycoated
canned cardboard caricature caricatures careless carelessly cartoonish
cartoony cash cynical cynically chafe chaos chaotic characterless cheap cheaply
cheapen cheesy cheerless childish childishness chintzy choppy chore churlish
cliched cliche cliches clichetically cloying cloyingly clueless clumsy
clumsily clutter cluttered coarse cold coldly collapse collapses collapsing
comatose commonplace complacent compromised con contrivance contrivances
contriving contrived convoluted convolution copout copycat corny cornball
corniness corrupt cowardly cowardice counterfeit counterfeit counterproductive
creak creaking creaky creepy crude crudely cruel crumble crumbles crushingly
cumbersome cutesy cuteness cynical cynicism damaged dated dawdle dead deadened
deadly deadweight deafening debased decay deceit deceptive dedicatedly deficient
deficit deflate deflated deflating deflates deformed degrading dehumanizing
delinquent deluded delusion demandingly demeaning derivative derisive
desperate desperately desperation desultory detachment detract detracts
devoid didactic difficult diffuse diluted dim diminishes diminution dingy
directionless dirty disable disappointing disappoint disappoints discomfort
disconnect disconnected disconcerting discordant discourage discrepancy
disdain disfigured disheartening dishwater dishonest disingenuous disjointed
dislike disliked dislikable disorienting disparate dispiriting displease
displeasing dissatisfaction dissatisfied disservice distancing distasteful
distract distracting distraction disturbing dizzy disorganized disorientated
dithering dodgy dog dogs doldrums dopey dorky dour downer downside doze
drab drag dragged dragging drags drains drained draining drawback drawbacks
drawn dreariness drearily drear droning dross drown drowning drowns
dry dubiously dubious dull dullness dumb dumbed dumbness dump dumps
duplicative dusty earnestly earnestness easier egregious egregiously
embarrassed emblematic emptiness empty endanger endless endlessly enervated
enervating enigma erratic error errors estranged evade evokes exaggeration
exaggerated excessive excessively excess excesses excuse excuses exhausted
exhaustion expendable exploit exploitive exploitative exploitation extraneous
extreme facile fade faded fades fail failed failing fails failures failure
fake fakery fallacy falter falters false falsely familiar familiarity farcical
farfetched fastidious fatigue fatigued fault faults faulty faux fawning
feeble feebly filler filth fishy flabby flagging flamboyance flat flatly
flatness flaw flawed flaws flimsy flounder floundering flounders flub flubs
fluff fluffy fluorescent flustered folly fool foolish foolishly foolishness
forced forcibly forget forgettably forgivable formula formulaic fragmented
frantic fraud fraudulent frayed freakish fretful frictionless frivolous
fruitless frustrating frustrated frustrates frustration frustratingly
fumbling fumbles fussy futile futility gimmick gimmicky gimmicks glaring
glassy glib glibness glitzy gloom gloomy glossy glued gloppy glum glut goofy
gratuitous gratuitously gravely grievance grim grimace grisly gross
grotesque grueling gruelling grumpy grungy gruesome hack hacked hackery hacks
hackish halfbaked halfhearted ham hammy hamstrung handicap handling
haphazard haphazardly harangue hardheaded harm harmful harsh hassle hastily
hasty hate hates hatred haunted haywire headache headachey headachy
heavyhanded hectoring hefty hectic hide hinder hinders hoary hocus hollow
hollowness hokey hokily hokiness homely homogeneous hopeless hopelessly
horrifying hostile huff humdrum humorless humourless humiliate humiliation
hung hurl hurried hurt hurts hyperactive hyperbole hyperbolic hypocrisy
hypocritical hysterics icky identical idiot idiots idle ignorant ignorance
ignore ignored ignores ill illogical imbalance imbalanced imitation imitative
immaterial immature immaturity immobile immoral impairs impatience impatient
imperfection imperfect impersonal implausible implausibility implausibly
implosion implodes imposing impossible improbability improbable improvisedly
inability inaccessible inaccuracy inaccurate inadequate inadequately inane
inanity inappropriate inarticulate inattentive incapable incoherent incoherence
incoherently incompetent incompetence incomprehensible inconclusive
inconsequential inconsistency inconsistent inconsiderate incongruous
incongruity inconvenient incorrect incredibility incredulity incredible
indecipherable indecisive indefensible indifferent indifference indistinct
indistinguishable individualistic indolent indulgent indulgently indulgence
indulges ineffective ineffectual inert inertia inevitable inexpressive
inferior inferiority inflated inflexible inglorious ingratiating inhospitable
inhuman inhumanity injudicious innocuous inoffensive insipid insignificant
insinuating insincere insincerity insubstantial insufficient interminable
interminably invasive irrelevant irks irksome irritable irritated irritates
irritation isolated jagged jarring jarringly jejune jerk jerky jumbled
jumpy juvenile kitsch kitschy labored laboured laborious laboriously lack
lacked lacking lacks lackadaisical lackluster lacklustre lag lagging lags lame
lament lamentable languid languishing lapse lapses laughably laziness lazy
lazily leaden leak leaky leering lesser letdown lethargic lethargy
lifelessness limit limitation limitations limited limp listless literal
loathe loathed loneliness lonely longish loopy loose lose loses losing
loss lost loud loutish low lowbrow lowest ludicrous lull lumber lumbering
lumpy lurid lurks lusterless machination maddening maddeningly maim
maladroit malfunction malicious malign maligned mangled manic manipulation
manipulates manipulative manufactured marginal marginally marketable marketing
maudlin meager meagre mean meaner meanest meandering meanders mechanical
mechanically mediocre melodrama melodramatic messes messy middling middlebrow
mindless mindlessly misanthropic miscast miscasting misdirected misdirection
misery misfortune misjudged misjudgment mismanaged mismatch mismatched
misplaced misrepresent miss misses missing mistake mistaken mistakes
mistrust misconceived mixed mockery mocking monotonous monotonously monotony
morbid moronic morons morose muddied muddiness muddling muddy muffled murky
mundane nagging naive naivete narcissistic narcissism narrow navel
nebulous needless needlessly needy negative neglect neglects neglected
neither nervewracking neurotic nitpick noise noisy noisily nonchalant
nonexistent nonplussed nonsense nonsensical nostalgia numbing numbingly
numb oblivious obscure obscures obscured obscurity obsession obvious
obviously oddity odious odors offensive offends offputting offhand okeydoke
oldfashioned omission onanistic onerous opaque opportunistic oppressive
ordeal ordinary ostentatious outdated outlandishly outmoded outraged
outrageous outright outstay outstays overacting overacted overambitious
overbearing overblown overboard overburdened overcooked overcrowded
overdirected overdone overdramatic overdrawn overdrive overearnest overkill
overlong overlong overly overplayed overplotted overpopulated overpraised
overproduced overrated overreach overreaches overridden overripe oversell
oversentimental overshadow overshadowed oversimplified overstated
overstuffed overstuffing overstylized overtaxing overtones overwhelmed
overwhelms overworked overwritten overwrought padded padding pain painful
paltry pandering panders panic paperthin paradox parody passable passe
passive patchy patronizing pedestrian perfunctory perilous perplexing
pessimistic petty phony phoniness piecemeal pitfall pitfalls pitiful pity
plagiarism plastic platitude platitudes playedout plodding plods plotless
pointlessness polemic pompous pompously ponder ponderous poorly poor
portentous pose poseur posturing preachy preachiness preaches preachiness
predictable predictably predictability preposterousness pretender pretense
pretenses pretentiousness pretentious predictable pretensions prettying
pricier primitive problem problematic problems prodding prosaic protracted
pseudointellectual puerility puff puffed pullback pulp punishment punishing
puny pushy putoff putdown puzzled puzzling quaint quandary queasy questionable
questionably ramble rambles rambling rancid random rank rankle rash
raunch raunchy ravaged reactionary reckless recycle recycled recycles
recycling redden redundant redundancy reductive reek reeks refuses regressive
regret regrettable regrettably regrets rehash rehashed rehashes rejects
rejection relentless relentlessly reluctant reluctance remedial remote
remotely remove removed repellant repellently repent repetition repeated
repetitious repetitive repetitively replica reprehensible repress repressed
repulsion resentment resign resigned resistant retch retread retreads
retrograde ridiculousness rigid riskiness robotic rote rough routine
rudimentary rue rueful ruin ruins runny rushed rusty saccharine sadness
sag sagging sags sappy sardonic saturates saturated savage savaged scattershot
scattered schematic scheming schlocky schmaltz schmaltzy schtick scold
scoreless scratchy screeching screwy secondhand secondary seedy seemingly
segmented selfish selfconscious selfimportance selfindulgent selfserious
selling sellout senseless sentimental sentimentality severe shabby shade
shaggy shaky shambles shallow shameless shame shamefully shapeless shallowly
shattered shattering sheepish shoddy shoddy shortcomings shortcoming shortcut
shortfall shrill shrillness shrug shudder shtick sick sickly sidebars
sidelined simplistic simplisticly simplistically sin sins sketchiness sketchy
skewed slap slaps sleazy sleepy slight slightness slimmest slips slogs slog
slogged sloppiness slow slower slowest slowly slowness sludge sluggishly
slumber smug smugly smugness smut snide snoozing snoozy snore soap soapy
sober sobering sodden softheaded soggy solemn solemnity somnolent sophomoric
soporific sorry sour soured soullessness sourness spares sparse specificities
speechifying spinoff spineless spiral spite spiteful spliced spoil spoiled
spoils spotty sprawl sprawling sputter sputtering sputters squanders
squander squandered squeamish stagnant stagy stagey staid stale staleness
stall stalls standard standardized stasis static stereotyped stereotype
stereotypes stereotypical sterile sterility stifle stifled stifling stiff
stiffly stiffness stilted stiltedly stingy stink stinking stodgy stoic
strained strains straining stranded strangely strangled stray stretched
stretches strident strictly stringy struggles studiously stumbles stumbling
stunt stunts stupor stupefying superficial superficially superficiality
superfluous suspect suspicious suspiciously swerve syrupy talkative talkiness
talky tangle tangled tangles tattered tasteless tatters tatty tawdry tediousness
tepid tepidly thin thinly threadbare throwaway thrown thumbsdown ticking
timid tinny tired tiredness tires tiring tiresomely token toothless torpid
torpor tortuous touchy toxic trampled transparent trap trapped traps
trashes trashing treacly treacle trite tritely trivial triviality trivializes
trouble troubled troubling trudge trudging trudges truncated turgid turkeys
turkey turmoil twisty twisted ugly unable unabsorbing unacceptably unacceptable
unaffected unaffecting unamusing unanswered unapologetically unattractive
unauthentic unavailability unaware unbalanced unbearably unbearable
unbelievable unbearably unbending uncalled uncertain unchallenged unchallenging
uncharismatic unclear uncomfortable uncomfortably uncommitted uncompelling
uncompensated uncompleted unconvincingly uncool uncreative undemanding
underachiever underbaked undercut undercuts underdeveloped underdone
underestimates underfed underfunded underlined undermine undermined
undermines undernourished underplayed underripe underused underutilized
underwhelmed underwhelms underwritten undeserved undesirable undetected
undetermined undeveloped undifferentiated undigested undisciplined
undisguised undistinguished undue unearned uneasy unease uneducated
unembellished unemployed unenlightening unentertaining unenthusiastic uneven
unevenly uneventful unexceptional unexciting unexpectedness unexplained
unexplored unexpressive unfair unfairly unfamiliar unfavorable unfinished
unfit unflattering unfocused unfocussed unfortunate unfortunately unfulfilled
unfulfilling unfunny ungainly ungraceful ungracious ungrounded unguarded
unhappy unhealthy unheard unhelpful unintelligent unintelligible unintended
unintentional unintentionally uninteresting uninterested uninviting
uninspired uninspiring unintentionally unkind unknowingly unknown
unlikable unlikeable unlikely unlimited unmemorable unmotivated unnatural
unnecessarily unnecessary unnerving unnoticed unobjectionable unobservant
unoriginal unoriginality unorthodox unpleasantly unpolished unpopular
unpredictably unprepared unproductive unpromising unprovoked unreadable
unrealistic unrealized unreasonable unremarkable unrewarding unrelenting
unrelieved unresolved unresponsive unsatisfying unsatisfied unsatisfactory
unsavory unscary unscripted unseemly unseen unsettled unsettlingly
unsettledness unshakably unshaped unsightly unskilled unsophisticated
unsound unspectacular unstable unsteady unsubstantial unsubtle unsubtly
unsuccessful unsuccessfully unsuitable unsuitable unsuited unsupportable
unsurprising unsuspecting unsustainable unsympathetic untalented untapped
untenable untested unthinkable unthinking untidy untimely untouched
untrained untrue untrustworthy untruthful untutored unwatchably unwelcome
unwieldy unwilling unwise unwisely unwittingly unworthy unyielding
unwitting unwritten vapidity vanity veer veers verbose victim victimized
vicious vileness violation violent volatile vulgar vulgarity wade wallow
wallows wan wane wanes waning wanting warped wary wash washed wasteful
wastefulness wasting watered watery weak weaker weakest weakly weakness
weaknesses weary wearied weariness wears wearisome wearing weirdly whack
whimper whine whining whiny wholly wimpy wince wincing winded windy
withers woebegone wobbly woe woes wooden woolly wordy worn worse worsen
wringing wrong wrongly yank yucky zany zero
""")

# Recalibrate polysemous words. Narrative content is not in itself a verdict.
_words(0, """
a and as but nor not no than if is was only well rate first see look looks
lover lovers extreme interest chance change family life look big folk
lead live lived story picture movie film screen see world social political
young return music subjects struggle struggles independent director intended
drama nature themes thematic usually new identity home songs dark war
innocent free means mean meant manner ordinary culture mystery mood family
feel feeling explore explores experience hope hopes idea ideas love affair
famous husband seemingly
cash bottom beyond fair dead dirty left busy trying would had doing just
high low difficult difficultly easier say says told telling taken handling
parody haunted savage weary mock mocking fate grimace harm hasty desperate
hide hurt hurts moral ill bitter hate tired ragged sad lonely loneliness
fool fooling oddity strict strictly literal dim dogs dog angry troubled haunted
dedicatedly raw unknown panic dark unexplained unknown unanswered unlikely
teenage juvenile intentional reference horror exclude full human emotional
tragedy death dies violence violent victim evil tragically comic drama
classic vintage afraid dream sick sickly jerk kill killer shock
chaos chaotic nasty cruel cruelty corrupt bloody horrible humanity twisty
twisted stoic audienceless throws thrown hung sidebars spare spares
heavy dizzy hefty isolated dirty odd angry selling difficult ignore
accept conform fat literate individualistic right supposed somewhere middle
kind dark ideology contemporary particular faithful serious seriousness
badness ill old heart hearts pure thinly earnestly earnestness laboredly
removed repeated inevitable challenge obscure irony bleak disturbing irony
surprised discomfort sad sadness watched deadpan adult comic
drowning drown late wake mix sin sins refuses risk risks falsely sick
grandly giddy outraged specificities mixed young musical vulnerable often
navel nervous troubling offended moral panic suspense unease sorrow pain
emotionally look unexpectedness duly drawn skin shot look lead tick
attitude forcedly innocent bewildered sketchiness secondary busy trick
hysteria do implores impossible obviously removes unexpectedly melancholy
wondered hard seriously grave more most exceedingly thoroughly immensely utterly
genuinely greatly enormously terribly incredibly awfully merely almost
intricately wildly astonishingly wholly experience outright fluidly
purpose obsession interest obsession merely removed absent critical
""")
_words(-0.85, """
gray grey slow scary slight little simpleminded difficult thin weird
gratuitous familiar familiarity flaws flaw flawed grim bleak predictable
sentimental earnestness remote adolescent excessive frenetic goofy
horrifying disturbing uncomfortable sickly unpleasant violent ordinary
long standard formula ambitiousness excess loopy absurd bizarre mixed
impossible loud lowbrow childish grimy kitsch silly sadness loss lost
overwhelmed overwhelming reluctant rawness tacky obvious oddity lesser
lumpy dry grim twisted manic promiscuous dread surrealistic
melodrama rough innocuous inoffensive downer darkly stiff explicit shock
""")
_words(1.35, """
favorite favourite gritty generous bleakly offbeat literary effective
fitting intimate haunting grimly movingly recommended truth daunting
suspense scares scary frightening terrifying scary heartbreaking
heartbreaking heartrending harrowing powerful devastating devastatingly
chilling spinechilling disturbing sensitive provocative challenging
darkly wicked wickedly eccentric eccentricity daffy nervy zany
unsettling subversive sardonic satiric satirical deftly understated
incredible hugely playful imagination ambitious audacious risky remains
appreciate grownups adulthood effortless lean admirable complex confident
imagination craft crafted laughter subtext subtleties revelatory
irony ironic unorthodox understated unflinching hauntingly understated
ambiguous ambiguity enigmatic mysterious gritty poignant romantic
""")
_words(2.8, """
heartbreakingly resonant incredible great funny beautiful enjoy strong
terrific riveting best riveting highpoint praising dynamism vivacity
pizzazz elan acutely incisive bravado aplomb affection humane humanistic
effective worthwhile rich heartwarming heartwrenching sublime lovely
expertly superb marvelous joy originality originality flawless
uncompromising timeless lush irresistible unpredictability effortlessly
unforgettable underrated cracker unforgettable uncanny dexterity fabulous
enjoys dazzled delightful wizard winning riveting shines recommend recommended
outshines excels excellent excelling excels topnotch extraordinary
unpretentious resounding perceptive imaginative breezy sparkling richly
thoughtfulness applaud triumphs hauntingly worthiness fittingly
""")
_words(-3.2, """
silly lousy rubbish dreck contrived cloying mechanical inelegant incompetent
predictable limp maudlin flat cliched slowgoing drear waste trash poorly
obviousness uninteresting torpid inept sleaze leaden unwieldy mediocre
tedious preposterous manipulative unimaginative unengaging unappealing
unnecessary uninvolving unmoving uninspired uninspired infuriating
tedium repellent tiredness insubstantial unlikable contemptuous contempt
hamhanded unconvincing cardboard fails disappoints squandered vapid dull
mindnumbing tiresome unsurprising disappointing disastrous dismal
misogynistic misogyny racist homophobic revolting clunkiness clunky
unfocused misanthropy regurgitated recyclings tacked incomprehensible
slog meanders unpalatable irredeemably irredeemable interminable flatfooted
unimpressive unlikeliest uninspired muddled witless joyless charmfree
tensionless retread dud sucks pigheaded witlessly ludicrous
abject fizzle fizzles misjudges woeful travesty embarassing
""")
_words(0.0, "unlikeliest remains awfully")
_words(0.85, "well love feeling solidly emotional passion passion emotion heart depth moments")
_words(2.1, "solid entertaining clever wit satisfying stylish refreshing lovingly fresh polished wellmade")
_words(-2.35, "silly predictable formula predictable tired fails bad painfully familiar flat thin lacks")

# Higher order constructions override the words making up the construction.
# Patterns operate on a space-separated, decontracted token stream.
_PH = []


def _pat(v, s):
    for line in s.strip().splitlines():
        line = line.strip()
        if line:
            _PH.append((re.compile(r"(?<!\w)(?:" + line + r")(?!\w)"), v))


_pat(4.4, r"""
tour de force|force of nature|work of (?:art|genius)|stroke of genius|instant classic
(?:one|among|some) of (?:the |this |his |her |its |their |[a-z]+ s |all |cinema s ){0,4}(?:best|greatest|finest|most (?:moving|exciting|compelling|memorable|inventive|important|entertaining|original|enjoyable|satisfying|powerful|rewarding|beautiful))
(?:year|season|summer|decade|century) s (?:very |absolute )?(?:finest|best|funniest|greatest)
(?:at|in) (?:its|his|her|their|the) (?:very )?(?:peak|best|finest|element)
(?:best|funniest|most entertaining) (?:film|movie|comedy|thriller|documentary|picture|time)(?: of| since| ever| this| in)?
must (?:see|watch)|not to be missed|(?:do|should) not miss (?:it|this|out)|unqualified success
(?:two )?thumbs up|(?:four|five) stars|top (?:notch|drawer|flight|shelf)|first (?:rate|class)
(?:worth|worthwhile) (?:every|the full) (?:penny|minute|second|cent)|worth (?:seeing|watching|seeking out|a look|the trip|the wait|your (?:time|money|while)|checking out|the price of admission)
(?:cannot|can not|could not) (?:recommend|praise) [a-z ]{0,35}(?:highly enough|enough|more highly)
(?:a|the) (?:real |sheer |pure |rare |small |little |cinematic )?(?:gem|treat|delight|joy|triumph|masterpiece|classic|hoot|miracle|treasure|revelation|winner|pleasure|knockout|beauty|marvel)
(?:nothing|little) short of (?:a )?(?:brilliant|spectacular|remarkable|miraculous|amazing|magnificent|genius|astonishing|wonderful|stunning|masterpiece|revelation)
as good as (?:it gets|they come|anything)|cannot get enough|can not get enough
(?:highly|heartily|wholeheartedly|enthusiastically|unreservedly) recommend(?:ed)?
deserves? (?:a[n]? )?(?:oscar|award|applause|praise|recognition|medal|standing ovation|wide audience|wider audience)
(?:take|takes|took) (?:my|your|our|the viewer s) breath away
(?:blow|blows|blew) (?:me|us|you|the audience) away|(?:brought|brings) (?:me|us|you) to tears
(?:on|at) the edge of (?:my|our|your|their) seats?
breath of fresh air|feast for (?:the|your) (?:eyes|senses)|a cut above|a class (?:of its own|by itself|apart)
""")
_pat(2.95, r"""
(?:a )?(?:good|great|terrific|wonderful|satisfying|rousing|enjoyable|entertaining|fun|grand|fine|rewarding|pleasant|wild|exciting|rollicking|fascinating) (?:time|fun|ride|surprise|romp|diversion|entertainment|movie|film|reason|way to|piece of|yarn|story|line|deal of fun|sense of humor)
(?:worth|merits?|rewards?) (?:a |the |another |repeated )?(?:visit|viewing|attention|seeing|watching|look|consideration)
worth (?:sitting|staying|waiting|the effort)|well worth|worthwhile experience
(?:something|a (?:lot|great deal|thing or two)|much|plenty) to (?:admire|offer|like|love|enjoy|recommend|say|treasure|chew on)
(?:go|goes|going|went) (?:straight )?(?:for|to) (?:the|your|our) (?:heart|jugular|gut)
gets? (?:it|things|so much|everything|the details|all the details) right|(?:does|did) (?:it|so much|everything) right
(?:gets?|got|will get) (?:deep )?under (?:the|your|my|our) skin
(?:sticks?|stays?|lingers?) (?:on )?(?:in|with) (?:my|the|your|you|us|me|our) (?:head|mind|memory|long|after)?
(?:keeps?|kept|holds?|held|grabs?|commands?|rewards?) (?:your|our|my|the viewer s|the audience s|one s) (?:attention|interest)
(?:keeps?|kept|has|had) (?:me|you|us|the audience) (?:guessing|laughing|interested|watching|wanting|in stitches|engaged|entertained|hooked|on edge)
(?:makes?|made) (?:you|me|us|one|the audience) (?:laugh|smile|think|feel|care|forget|believe)
(?:had|left|leaves?) (?:us|you|me) (?:laughing|smiling|wanting more|breathless|shaken|moved)
(?:long|well) after (?:the (?:end|credits|lights|movie|film)|you leave)|resonates? (?:long|with)
(?:rings?|rang) true|(?:comes?|came|brings? it) alive|comes? (?:fully )?to life
(?:does|did|can do) (?:the trick|wonders|justice)|(?:does|do|doing) justice to|pulls? (?:it|this|that|them) off|carries? it off
(?:succeeds?|works?) (?:beautifully|nicely|well|very well|like a charm|on (?:all|many|every|several) levels|wonders|surprisingly well)
(?:does|somehow|really|actually|still|largely|mostly|certainly|ultimately|even|it) works?(?: [.!]|$)
(?:well|beautifully|superbly|expertly|finely|carefully|tightly|masterfully|deftly|brilliantly) (?:made|written|observed|crafted|acted|told|drawn|directed|cast|executed|done|paced|balanced|deserved|conceived|shot|put together|constructed|served|suited|developed|rendered|realized|mounted|played|wrought|choreographed|photographed)
(?:sure|assured|surefooted|light|nimble|deft|delicate) (?:hand|touch|footed)
(?:eye|ear) for (?:detail|dialogue|talent|the absurd)|attention to detail
a (?:strong|sharp|keen|good|great|wonderful|refreshing|wicked) (?:sense|eye|ear|performance)
full of (?:life|heart|humor|wit|surprises|energy|insight|charm|feeling|ideas)|plenty of (?:laughs|heart|wit|humor|surprises|fun|charm)
(?:brings?|brought|gives?) (?:fresh |new )?(?:life|depth|energy|warmth|insight|meaning|humanity|something new) to
(?:has|with|of) (?:real |great |unusual |considerable )?(?:depth|substance|power|integrity|heart|grace|resonance|nuance|style to spare)
(?:dead|spot|right) on|hits? (?:the (?:right notes|spot|mark|target|bull s eye)|home|hard|all the right)|strikes? (?:a chord|just the right|a balance)
(?:is|are|remains|seems|feels) (?:a (?:big |pleasant |genuine )?surprise|something special|a natural|the real (?:thing|deal)|in (?:fine|top|peak|great) form)
(?:an?|the) (?:unexpected|pleasant|welcome|refreshing|nice|delightful|rare|genuine|happy) (?:change|exception|surprise|departure|find|reminder|relief|pleasure|treat)
(?:a )?(?:guilty|unalloyed|unadulterated|simple|sheer|pure) (?:pleasure|entertainment|joy|fun)|pure cinema
against (?:all )?(?:odds|expectations)|exceeds? (?:all |my |our |your )?expectations
(?:more|better|funnier|smarter) than (?:you |one |we |i )?(?:might |would |could |would have |might have )?(?:think|expect|imagine|hope|believe)
(?:that rare|the rare|a rare) (?:thing|film|movie|case|example|gift|combination|breed)
(?:never|seldom|rarely) (?:gets? |becomes? |feels? |seems? |is )?(?:dull|boring|stale|tiresome|predictable|maudlin|cloying|sentimental|preachy|heavy handed|less than|loses? (?:its|his|her) (?:grip|balance|way))
(?:you |we |one |i )?(?:can not|cannot|could not) (?:help but |help |resist |stop )?(?:but )?(?:laughing|smiling|loving|liking|admiring|enjoying|watching|feeling|marveling|cheering|rooting)
(?:easy|hard not|impossible not|difficult not) to (?:like|love|enjoy|admire|appreciate|care|root for)
(?:can not|cannot|could not) (?:look (?:away|away from)|take (?:my|your|our) eyes off|ask for (?:more|a better|much more))
what more (?:could|can) (?:one|you|we|anyone) ask|(?:something|fun) for (?:almost )?everyone
no (?:small|mean|easy) (?:feat|achievement|task)|(?:more|far) than (?:just )?(?:a |an |another )?(?:sum of its parts|pretty face|mere|cheap|typical|average|run of the mill)
(?:firing|fires?) on all cylinders|(?:stands?|stood) out|stands? (?:head and shoulders|on its own)|in a league of its own
steals? the (?:show|movie|film)|steals? (?:every|each) scene|(?:at|on) the top of (?:his|her|their|its) game
(?:is|are|proves? to be) (?:more than )?(?:up to the task|equal to the task|a revelation|a pleasure)
(?:a |the )?labor of love|love letter to|a fitting tribute|in good hands
laugh (?:out loud|a minute)|laughing out loud|laugh out loud funny|side splitting|knee slapp(?:er|ing)|a barrel of laughs
eye (?:opening|popping|opener|catching)|jaw dropping|mind blowing|thought provoking|thought provoker|heart (?:warming|stopping|pounding|wrenching|rending|tugging|breaking)|gut (?:busting|wrenching)|nail bit(?:er|ing)|spine (?:tingling|chilling)|edge of (?:your|the) seat
feel good|crowd pleas(?:er|ing)|crowd pleaser|crowdpleasing|rousing good|action packed|character driven|fast paced|fast moving|fun filled|fun loving|life affirming
tongue (?:firmly )?in cheek|tongue in cheek|larger than life|slice of life|no holds barred
(?:a )?return to form|raises? the bar|sets? a new standard|pays? off|big payoff|packs? (?:a|an|quite a) (?:emotional |powerful |real )?(?:punch|wallop)
(?:deliver|delivers|delivered) (?:the goods|the laughs|on (?:its|his|her|all)|a punch)|never (?:lets? up|lets? go|flags?|falters?|disappoints?|misses? a beat)
(?:manages?|managed) to (?:avoid|transcend|capture|create|convey|balance|pull off|make|keep|turn|combine|remain|find|bring|give)
(?:fun|joy|a pleasure|a delight|a treat|a blast|a ball) to (?:see|watch|behold|experience|look at|sit through)
(?:well|much|far|considerably|infinitely|surprisingly) better|(?:a|far|much) (?:cut |notch )?above (?:the )?(?:average|rest|usual|ordinary|norm|competition)
not (?:half |too |at all |so )?bad|(?:could|can) do (?:a lot |much |far )?worse|(?:could have been|have seen) (?:much |far )?worse
not without (?:its |some |a certain )?(?:charm|merit|pleasure|interest|appeal|rewards)|(?:anything but|far from) (?:dull|boring|ordinary|predictable)
a (?:good|great|wonderful|rare|welcome|refreshing) example|silver screen magic|two thumbs way up
""")
_pat(-4.55, r"""
(?:one|among) of (?:the |this |his |her |their |its |[a-z]+ s ){0,4}(?:worst|dullest|dumbest|most (?:boring|tedious|unpleasant|unnecessary|disappointing|painful))
(?:worst|dullest|dumbest|most boring) (?:film|movie|picture|comedy|thriller|thing|experience)|year s worst
(?:a |an )?(?:(?:complete|utter|total|unmitigated|dismal|miserable|colossal|absolute|royal|bloody|godawful|incoherent) )?(?:waste of (?:time|talent|money|film|celluloid|effort|energy|space|a)|piece of (?:junk|crap|garbage|shit|trash|dreck)|train wreck|disaster of a|steaming pile)
(?:not|hardly|scarcely) worth (?:the |a |your |my |our |watching|seeing|sitting|it)|not (?:even )?worthwhile
(?:do not|never|should not) bother|(?:spare|save) (?:yourself|your (?:time|money)|us the)
(?:avoid|skip) (?:this|it|the film|the movie|at all costs)|(?:a film|one|a movie|something) to (?:skip|avoid|miss|forget)
(?:do not|does not|will not|would not|would never|can not|cannot|could not) recommend
(?:an? )?(?:new|all time|career) low|bottom of the barrel|scrap(?:es|ing) the bottom
thumbs down|two left feet|dead on arrival|dead in the water
(?:rather|better off) (?:staying|watching paint|watch paint|watching grass|waiting for|renting|skipping|seeing something)|watch(?:ing)? paint dry
(?:lose|lost|get back) (?:two hours|[0-9]+ minutes) of (?:my|your|our) life|(?:want|wanted) my money back
no redeeming|without (?:a |one )?(?:single )?redeeming|(?:utterly|completely|totally) (?:devoid|lacking)
so bad (?:that )?(?:it is|it s) (?:not even|painful)|gives? (?:\w+ ){1,3}a bad name
""")
_pat(-3.25, r"""
(?:falls?|fell) (?:painfully |woefully |well )?(?:short|flat|apart|to pieces|on its face|into (?:the|a) trap)|comes? up (?:short|empty)|miss(?:es|ed)? the (?:mark|point|boat|target)
(?:never|not|hardly) (?:quite |really |remotely |even |very |particularly |as )*(?:works?|comes? (?:together|alive|close)|gets? going|catches? fire|takes? off|comes? to life|gets? off the ground|adds? up|pays? off|makes? sense|amounts? to|engages?|lives? up|measures? up|holds? together|convince|clicks?|jells?|gels?)
(?:little|nothing|not much|precious little) (?:there |here |new |much |left |else )?to (?:like|love|enjoy|admire|recommend|offer|say|care about|root for|show|do with|distinguish|sustain|hold|engage|interest|amuse|redeem|make)
(?:not|hardly|scarcely|never) (?:much|any|enough|nearly enough) (?:of a |of an |in the way of )?(?:story|reason|film|movie|life|heart|interest|fun|laughs|sense|plot|point|suspense|excitement|depth|charm|tension|time|substance|feeling)
(?:not|never|hardly|scarcely) (?:half |even |nearly |quite |really |remotely |very |particularly |all that |especially )*(?:as good|as funny|good enough|interesting enough|particularly good|worth|good|funny|enough|interesting|engaging|compelling|entertaining|scary|convincing|much fun|entirely successful)
(?:can not|cannot|can never|could not|never) (?:quite |really |possibly )?(?:save|salvage|redeem|overcome|rescue|compensate for|sustain|match|decide|justify|make up for|muster|rise above|escape|deliver|shake|find its|figure out|bring [a-z]+ to care)
(?:do|does|did|is|are|has|have|was) not (?:quite |really |even |much )?(?:care|live up|add up|stand a chance|have (?:the|much|enough|any|a clue)|make (?:a lick of|much|any|the grade)|cut it|work|deliver|hold up|do justice|up to|buy (?:it|a|the)|earned|matter|reason enough)
nothing (?:very |particularly )?(?:new|special|remarkable|original|interesting|fresh|more than|going for)|nothing (?:else |much )?happens|nothing (?:but |of )?(?:noise|consequence|substance|note|interest)
(?:plays?|reads?|looks?|sounds?|feels?) like (?:an? )?(?:bad|cheap|poor|second rate|made for|movie of the week|tv movie|sitcom|television|student film|retread|rip off|retread|infomercial|long|extended|episode of|parody of|rehash|exercise in)|(?:is|like) a bad (?:episode|case|version|joke|dream)
(?:seen|heard|done) (?:it |this |that |all |it all |it done |this done |all this |the same thing )?(?:(?:many times|a thousand times|a million times|too many times|much better|far better|well) )?before
(?:same old|same tired|all too familiar|overly familiar|been there ,? ?done that|more of the same|by the numbers|by numbers|run of the mill|paint by numbers|connect the dots|going through the motions)
(?:leaves?|left) (?:me|you|us|the audience|one|this viewer) (?:cold|numb|wondering why|bored|indifferent|frustrated|unsatisfied|disappointed|unmoved|scratching)
(?:put|puts|lulls?) (?:me|you|us|the audience) to sleep|(?:hard|difficult|painful|impossible|tough) to (?:sit through|watch|swallow|take seriously|stomach|endure|believe|follow|care|recommend|root for|warm to|like|stay awake)
(?:who|why should (?:we|you|i|anyone)|as if (?:we|anyone)) cares?|what s the point|what is the point|why bother|what were they thinking
(?:no|little|precious little|very little|without any|lacks? (?:any |a )?|lacking (?:in )?) (?:real |discernible |genuine |apparent |redeeming |compelling |visible )?(?:sense of|reason|point|purpose|life|heart|soul|pulse|weight|interest|charm|energy|coherence|logic|focus|direction|substance|depth|wit|humor|feeling|imagination|merit|suspense|tension|payoff|chemistry|originality|personality|appeal|clue|conviction|business|laughs|redeeming value)
(?:few|too few|very few|precious few|not enough) (?:and far between|laughs|reasons|surprises|redeeming|moments)|too little too late
(?:less|rather|barely|hardly|scarcely|little) (?:a |an |more )?than (?:the sum|meets the eye|it should|it could|satisfying|compelling|convincing|impressive|a collection|an excuse|a series|a string)|(?:not|hardly) (?:much |anything )?more than
(?:not|never) (?:goes?|rises?|amounts?) (?:far |much )?(?:beyond|above|anywhere|to much)|(?:goes?|leads?) nowhere|to no (?:avail|effect|purpose)|(?:without|with no) (?:ever )?(?:really )?(?:saying|offering|giving|achieving|revealing|anything)
(?:too|so) (?:bad|much|many|little|few|long|late|often|obvious|slow|self conscious|serious|cute|predictable|heavy|busy|hard|easy|familiar|pat|calculated|thin|simple|earnest|loud|tame|contrived) (?!fun|to like)
(?:less|more) (?:fun|interesting|entertaining|enjoyable) (?:to watch |to make )?than (?:watching|making)|more fun (?:to make|than the movie)
(?:wants?|tries?|trying|works?|strains?) (?:a little |just )?too hard|more than (?:it|they) can chew|collapses? (?:under|in)|own worst enemy
(?:sinks?|sunk|bogged|mired|drowned|drowning|lost) (?:down )?(?:in|by|under|beneath) (?:its|a sea of|an ocean of|cliche)
(?:has|have|deserved|deserves?) (?:been done |seen )?(?:much |far )?better|deserves? (?:a )?better|(?:could|should) have been (?:much |so much |a lot |far )?(?:more|better|funnier|great|good|interesting|fun|made|left)
missed opportunity|wasted opportunity|wastes? (?:the |its |a )?(?:talents?|potential|time|premise|opportunity)
(?:a |the )?(?:complete |absolute |total |real |big |major |huge |crushing |bitter |colossal )?(?:let ?down|misfire|misstep|miscalculation|disappointment|failure|disaster|wreck|fiasco|bore|snooze|stinker|turkey|mess|shambles|miscarriage)
(?:sorely|badly|sadly|desperately) (?:needs?|lacks?|lacking|short|missing|wanting)|(?:something|much|a lot) (?:is )?(?:sorely |sadly )?missing|a shame|a pity|what a waste|a sad (?:excuse|attempt|imitation)
(?:nothing|not much) (?:but|more than)|thinly (?:veiled|disguised)|paper thin|cardboard cutouts?|one (?:dimensional|note|joke|trick)|all (?:style|flash|surface|sound|noise) (?:and|,)|style over substance
(?:second|third|fourth) (?:rate|hand|tier)|heavy handed|ham (?:fisted|handed)|half (?:assed|baked|hearted|formed|cooked)|ill (?:conceived|advised|judged|suited|defined|considered)|hit and miss
(?:self )?(?:indulgent|important|congratulatory|satisfied|conscious|serving|serious) (?:exercise|mess|effort)|self (?:important|indulgence|indulgent|congratulatory|serious|satisfied)
(?:mind|brain|butt) numbing|low rent|low grade|cut rate|bottom feeding|bottom feeder|bargain basement|straight to video|direct to video|made for tv|tv movie of the week
(?:heavy|long|big) on .{1,45}? (?:and |but )?(?:short|light) on|(?:short|light) on (?:wit|laughs|plot|substance|originality|story|ideas|character)
(?:take|takes|taking) itself (?:way |far )?too seriously|(?:does|do) not (?:even )?(?:try|bother|begin to)
(?:lose|loses|lost) (?:its|their|the) (?:way|steam|nerve|momentum|focus|interest|edge|grip)|out of (?:ideas|gas|steam|its depth|his depth|touch)|runs? out of|spins? its wheels|dead horse
(?:walk|walked|walking) out of|checks? (?:my|your|one s) watch|look(?:ing|ed)? at (?:my|your) watch|count(?:ing|ed)? the minutes|seems? (?:to last |like )?(?:forever|an eternity)
leave[sd]? (?:much|a lot|something) to be desired|least of (?:its|the film s) problems|does a disservice|fails? on (?:all|every)
(?:better|best) (?:left|forgotten|suited (?:for|to) (?:television|the small screen))|less (?:fun|successful|interesting|engaging|impressive|entertaining|exciting|effective|satisfying|than stellar)
(?:nobody|no one) (?:really )?(?:cares?|needs?|asked for)|only (?:a mother|the most (?:ardent|undemanding|forgiving|die hard)|die hard fans)
what (?:could|might|should) have been|if only|alas|unfortunately|would that|too bad|sorry to (?:say|report)
the only (?:good|interesting|funny|bright|redeeming|saving|reason|thing worth)|only saving grace|one redeeming (?:quality|feature)
no great shakes|no big deal|no better than|not my (?:idea|cup|kind|type)|hardly a (?:classic|masterpiece|surprise)|leave it to|phoned? (?:it|this one) in|on autopilot
""")
# Idioms in which an apparent reversal, a criticism, or a compliment is spurious.
_pat(0, r"""
not (?:only|merely|just|simply|necessarily|unlike|to mention|to say)|(?:whether|believe it) or not
no (?:doubt|wonder|matter|longer|stranger|less than|less a|need to)|nothing if not|nothing less than
(?:does|do|did) not (?:shy|flinch|pull (?:any )?punches|take itself too seriously)
little (?:boy|girl|kid|town|bit|screen)|small town|long (?:island|ago|haul)|bad (?:guys?|boys?|taste|cops?|news bears|behavior|seed|dreams?)|good (?:guys?|guys? and bad guys?|deeds?|looks|intentions|ol[de]? boys?|versus evil|and evil)
(?:the |a |his |her |an )?(?:love|success|horror|crime|ghost|war|coming of age) stor(?:y|ies)|(?:in|out of|falling in|falls? in|fell in|make|making) love|love (?:affair|triangle|life|interest|scenes?)|(?:romantic|black|dark) comedy|special effects
pretty (?:much|well)|rather than|as well as|might as well|best (?:friend|selling|seller|friends)|at best|of course|for good measure
a great deal|the great depression|the good (?:book|lord)|a number of|(?:good|better) (?:luck|yet)|in order to|take care of
""")
_pat(2.3, r"""
slow (?:burn|burning)|sick (?:sense of )?humor|bad ass|takes? (?:a )?risk|takes? (?:a )?chance|(?:is|was|are|were) never (?:dull|boring)
(?:never|not) (?:mawkish|sentimental|condescending|dull|dumb|pretentious|predictable|patronizing|manipulative|less than)
(?:do|does|did) not have to be|you owe it to yourself|do yourself a favor|do not let .{1,28}? fool you
(?:i|we|you) (?:will |really |absolutely )?(?:love|like|loved|liked|enjoy|enjoyed) (?:it|this|the|every|what|that)
manages? (?:the |a )?(?:rare|tricky|difficult|impossible|delicate|neat) (?:feat|task|trick|balance)|makes? the most of
the big screen|on many levels|something to behold|like no other|in (?:fine|rare) form|a ball|a blast|a gas
""")

_STOP = {".", "!", "?", ";", ":", ","}
_CLAUSE = _STOP | set("but however yet although though while whereas because despite except unless instead nevertheless".split())
_NEG = set("not never neither nor hardly scarcely barely without cannot nothing nobody nowhere no lacks lack lacking minus absent".split())
_BOOST = set("truly quite really extraordinarily unusually extremely very highly genuinely deeply thoroughly surprisingly astonishingly utterly absolutely wonderfully remarkably terribly enormously immensely richly exceptionally profoundly undeniably incredibly particularly tremendously so much too".split())
_HEDGE = set("somewhat reasonably moderately relatively occasionally sporadically partly partially sometimes mildly fairly nearly almost potentially rather".split())
_BG = set("his her their earlier original previous last other better some classic greatest famous classic legendary critically earlier previous once before prior".split())


def _tokens(s):
    s = unicodedata.normalize("NFKD", s.lower().replace("’", "'").replace("`", "'"))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\bn\s*'\s*t\b", "n't", s)
    s = re.sub(r"\s+n't\b", "n't", s)
    s = re.sub(r"\s*'\s*(s|re|ve|d|ll|m)\b", r"'\1", s)
    for a, b in (("won't", "will not"), ("can't", "can not"), ("cannot", "can not"),
                 ("shan't", "shall not"), ("ain't", "is not"), ("n't", " not"),
                 ("'re", " are"), ("'ll", " will"), ("'ve", " have"), ("'d", " would"),
                 ("'m", " am")):
        s = s.replace(a, b)
    s = re.sub(r"\b(it|he|she|that|here|there|what|who|how|where)'s\b", r"\1 is", s)
    s = re.sub(r"\bits (?=(?:not |a |an |so (?:good|bad)|the kind of))", "it is ", s)
    s = re.sub(r"\b(?:don|doesn|isn|wasn|wouldn|couldn|shouldn|didn|aren|weren|hasn|haven|hadn)t\b",
               lambda m: m.group()[:-2] + " not", s)
    s = re.sub(r"--+|[—–]", " ; ", s)
    s = re.sub(r"(?:\.\s*){2,}", " ; ", s)
    return re.findall(r"[a-z]+|[0-9]+|[.,;:!?]", s)


def _lex(w):
    if w in _WORD:
        return _WORD[w]
    options = []
    if w.endswith("ily"):
        options.append(w[:-3] + "y")
    if w.endswith("ly"):
        options.extend((w[:-2], w[:-2] + "e"))
    if w.endswith("iness"):
        options.append(w[:-5] + "y")
    if w.endswith("ness"):
        options.append(w[:-4])
    if w.endswith("iest") or w.endswith("ier") or w.endswith("ies") or w.endswith("ied"):
        options.append(w[:-(4 if w.endswith("iest") else 3)] + "y")
    for suf in ("ing", "ed", "es", "s", "er", "est"):
        if w.endswith(suf) and len(w) > len(suf) + 2:
            root = w[:-len(suf)]
            options.extend((root, root + "e"))
            if len(root) >= 2 and root[-1] == root[-2]:
                options.append(root[:-1])
    for opt in options:
        if opt in _WORD:
            return _WORD[opt] * 0.92
    if w.startswith("un") and _WORD.get(w[2:], 0) >= 1.5:
        return -2.2
    return 0.0


def _phrase_events(t):
    text = " ".join(t)
    starts = []
    k = 0
    for w in t:
        starts.append(k)
        k += len(w) + 1
    spans = []
    for p, v in _PH:
        for m in p.finditer(text):
            i = bisect_left(starts, m.start())
            j = bisect_left(starts, m.end())
            spans.append((i-j, -abs(v), i, j, v))
    used = [False] * len(t)
    vals = {}
    for _, __, i, j, v in sorted(spans):
        if not any(used[i:j]):
            used[i:j] = [True] * (j-i)
            vals[i] = (j, v)
    return used, vals


def _discourse(t, used):
    n = len(t)
    weights = [1.0] * n
    start = 0
    for i, w in enumerate(t):
        if w in (".", "!", "?", ";"):
            start = i+1
            continue
        if w not in {"but", "yet", "however", "though", "although", "while", "despite", "notwithstanding", "nevertheless", "still", "unlike", "whereas", "than"}:
            continue
        end = next((k for k in range(i+1, n) if t[k] in {".", "?", "!", ";"}), n)
        if w in {"but", "yet", "however", "nevertheless", "still"}:
            if used[i] or (w == "but" and (t[i-1:i] in (["anything"], ["all"], ["nothing"]) or t[i+1:i+2] == ["also"])):
                continue
            if w == "yet" and (t[i+1:i+2] in (["another"], ["to"]) or t[i-1:i] == ["not"]):
                continue
            if w == "still" and i > 0 and t[i-1] not in _STOP and not any(x in {"while","despite","though"} for x in t[start:i]):
                continue
            for k in range(start, i):
                weights[k] *= 0.62
            for k in range(i+1, end):
                weights[k] *= 1.15
        elif w == "than":
            if i and t[i-1] in {"better", "more", "worse", "less", "rather", "other"}:
                for k in range(i+1, end):
                    if t[k] in _CLAUSE:
                        break
                    weights[k] *= 0.68
        else:
            if w == "though" and t[i+1:i+2] in ([","], ["."], [";"]):
                continue
            for k in range(i+1, end):
                if t[k] in _CLAUSE:
                    break
                weights[k] *= 0.55
    return weights


def predict(state) -> dict:
    t = _tokens(state)
    if not t:
        return {"answer": "positive"}
    used, phrases = _phrase_events(t)
    weights = _discourse(t, used)
    total = 0.16
    n = len(t)
    for i, w in enumerate(t):
        if i in phrases:
            j, v = phrases[i]
        elif used[i] or w in _STOP:
            continue
        else:
            j = i+1
            v = _lex(w)
            if w in {"too", "overly", "excessively"} and j < n and t[j] not in (_STOP | {"bad","much","many","little","few","often","long"}):
                v = -1.75
            elif w in {"tries", "trying", "tried", "attempts", "strives", "struggles", "pretends", "aspires", "aims", "wants", "wanted"} and t[j:j+1] == ["to"]:
                v = -1.45
            elif w in {"should", "might", "could", "would"} and t[j:j+2] == ["have", "been"]:
                v = -2.7
            elif w in {"wish", "wished", "supposed", "wannabe", "wannabes", "strained", "misused"}:
                v = -2.65
            elif w == "only" and t[j:j+1] in (["intermittently"], ["occasionally"], ["sporadically"]):
                v = -2.8
            elif w == "yet" and t[j:j+1] == ["another"]:
                v = -2.45
            elif w == "another" and t[j:j+1] in (["example"], ["exercise"], ["attempt"], ["ripoff"], ["rehash"]):
                v = -1.75
            elif w in {"needed","needs"} and any(x in {"more","better","less","work","badly"} for x in t[j:j+4]):
                v = -2.6
            elif w == "like" and i and t[i-1] in {"really","i","we","actually","will"}:
                v = 1.8
            elif w in {"i", "we", "you"} and t[j:j+1] == ["could"] and "less" in t[j:j+4]:
                v = -1.5
            elif w == "wants" and t[j:j+2] == ["it", "both"]:
                v = -2
            elif w in {"works", "worked"}:
                v = 1.3
            elif w in {"not","never","no","without","neither","hardly"}:
                v = -0.35
            elif w == "enough":
                v = 0.65
        if not v:
            continue
        prior = []
        neg = False
        for k in range(i-1, max(-1, i-8), -1):
            if t[k] in _CLAUSE:
                break
            if k < i-1 and t[k] in {"is","are","was","were","has","have","gives","makes","makes","which","that","because","when","then"} and not (k and t[k-1] in {"it","ever"}):
                break
            prior.insert(0, t[k])
            if used[k]:
                continue
            if t[k] in _NEG:
                if t[k] == "no" and k and t[k-1] == "or":
                    continue
                neg = not neg
                if k > 0 and t[k-1] == "not" and t[k] == "without":
                    neg = not neg
                break
            if t[k] == "less" and i-k <= 3 and v > 0:
                neg = True
                break
            if t[k] == "anything" and t[k+1:k+2] == ["but"]:
                neg = True
                break
        ctx = " ".join(prior)
        if i >= 2 and t[i-2:i] == ["anything", "but"]:
            neg = True
        # Conditions and failed aspirations are not assertions of their objects.
        if v > 0 and re.search(r"\b(?:fail(?:s|ed)? to|(?:tries|tried|trying|try|attempts?|strains?|pretends?|aspires?|strives?|supposed|wanted|wants) to|straining for|(?:could|should|would|might) have been|(?:wishes|thinks) it (?:is|was|were)|idea of|meant to be|hopes to be)\b", ctx):
            v *= -0.48
            neg = False
        elif v > 0 and re.search(r"\b(?:struggles? to|instead of|in search of|for want of|short on|devoid of|missing|absence of|far from)\b", ctx):
            v *= -0.83
            neg = False
        elif v > 0 and any(x in {"few","little","scant"} for x in prior[-3:]) and not any(x in {"a","precious","every","some"} for x in prior[-4:]):
            neg = True
        if neg:
            v *= -0.91
        if prior and prior[-1] in _BOOST and not used[i-1]:
            v *= 1.30
        if any(x in _HEDGE for x in prior[-2:]):
            v *= 0.73
        if w in {"well", "pretty"} and j < n and (_lex(t[j]) or t[j] in {"as","over","under","before","much"}):
            v = 0
        if v > 0 and t[j:j+1] in (["intentions"], ["idea"], ["premise"], ["potential"], ["concept"], ["cast"], ["opportunity"]):
            v *= 0.65
        if v > 0 and w in {"talent","talented","talents","cast","actors","promising","premise","potential"}:
            v *= 0.67
        if v > 0 and any(x in {"too","overly","excessively"} for x in prior[-2:]) and not used[i-1]:
            v *= -0.72
        if v > 0 and any(x in {"unintentionally","unintended","supposedly","ostensibly","allegedly","accidentally"} for x in prior[-2:]):
            v *= -0.84
        if v > 0 and j < n and t[j] == "than" and "less" in prior[-2:]:
            v = -abs(v)
        if w in {"should","could","would","might"} and j == i+1 and t[j:j+2] == ["have", "been"] and any(_lex(x) < -1 for x in t[j+2:j+5]):
            v = 0.6
        # Emphasize an assessment of the whole movie, and the conclusion.
        weight = weights[i] * (0.96 + 0.11*i/max(n-1, 1))
        if j < n and t[j] in {"movie", "film", "documentary", "experience", "picture", "entertainment"}:
            weight *= 1.18
        total += weight*v
    if t[-1] == "?" and total < 1.8:
        total -= 1.35
    return {"answer": "positive" if total >= 0 else "negative"}