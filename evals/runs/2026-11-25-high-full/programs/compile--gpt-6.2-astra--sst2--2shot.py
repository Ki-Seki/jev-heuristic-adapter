import re
import unicodedata
from functools import lru_cache


def _tokens(s):
    s = s.lower().replace("&amp;", " and ").replace("&quot;", '"')
    s = s.replace("&#39;", "'").replace("&apos;", "'").replace("&lt;", "<").replace("&gt;", ">")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("’", "'").replace("‘", "'").replace("`", "'")
    s = s.replace("…", "...").replace("–", " -- ").replace("—", " -- ")
    s = s.replace("-lrb-", " ( ").replace("-rrb-", " ) ").replace("-lcb-", " ( ").replace("-rcb-", " ) ")
    s = re.sub(r"\bca\s*n\s*'\s*t\b|\bcannot\b|\bcant\b", "can not", s)
    s = re.sub(r"\bwo\s*n\s*'\s*t\b|\bwont\b", "will not", s)
    s = re.sub(r"\bai\s*n\s*'\s*t\b", "is not", s)
    s = re.sub(r"n\s*'\s*t\b", " not", s)
    s = re.sub(r"\b(did|does|do|is|was|are|were|has|have|had|could|should|would)nt\b", r"\1 not", s)
    s = re.sub(r"\s*'\s*(ve|ll|re|d|m)\b",
               lambda m: " " + {"ve": "have", "ll": "will", "re": "are", "d": "would", "m": "am"}[m[1]], s)
    s = re.sub(r"\b(it|that|there|what|who|he|she|here|how|when|where|everything|something)\s*'\s*s\b", r"\1 is", s)
    s = re.sub(r"\blet\s*'\s*s\b", "let us", s)
    s = re.sub(r"\s*'\s*s\b", "", s)
    s = s.replace("'", "").replace('"', "").replace("&", " and ")
    s = s.replace("a.i.", "ai").replace("o.k.", "okay")
    s = re.sub(r"-{2,}", " — ", s).replace("-", " ")
    return re.findall(r"[a-z]+|\d+(?:\.\d+)?|\.{2,}|[^\w\s]", s)


# Scores pertain to words in film criticism (for example, 'haunting' and
# 'unsettling' usually describe an achievement rather than a complaint).
_WORD = {}


def _words(value, s):
    for w in s.split():
        _WORD[w] = value


_words(3.65, """
masterpiece masterwork masterstroke triumph triumphant tourdeforce classic
outstanding magnificent magnificence superb superlative exceptional phenomenal
sensational extraordinary breathtaking breathtakingly spellbinding enthralling
exhilarating exhilaratingly terrific tremendous fantastic fabulous marvelous
marvellous wonderful brilliant brilliance sublime sublimity splendid stellar
excellent excellence exquisite unforgettable unmissable incomparable unparalleled
peerless astonishing astonishingly astounding stupendous spectacular glorious
genius ingenious perfection flawless faultless bravura virtuoso virtuosity
transcendent transcends transcending transcendance transcendency dazzling dazzlingly
masterful masterfully masterly masterclass powerhouse riveting mesmerizing
mesmerising mesmerizingly hypnotic rapturous exhilarating electrifying
enchanting enchantingness enthralls indispensable essential gem treasure
best greatest favorite favourite favorites favourites perfection
""")
_words(2.70, """
great amazing beautiful beauty beautifully gorgeous lovely loveliness
delight delightful delightfully delights delighted delicious deliciously delectable
enjoyable enjoyably enjoyment enjoys enjoyed entertaining entertainment entertains
engrossing engrossed absorbing engrosses absorbs captivating captivates captivated
compelling compellingly fascinating fascinates fascinated endlessly-inventive
rewarding satisfying satisfies satisfied gratifying gratification fulfilling
moving affecting poignant poignancy touching heartfelt heartwarming heartening
endearing endearingly lovable loveable adorable affable appealing appeal charms
charming charismatic charisma irresistible irresistibly winsome winning winner
seductive seductive seductively seductive seductive beguiling alluring entrancing
haunting hauntingly soulstirring evocative evokes poetic lyrical lyricism
powerful powerfully potent potency profound profundity resonant resonates resonance
stirring rousing uplifting inspiring inspired inspiration inspirational
invigorating invigorates exhilarating energizing energising galvanizing
exciting excitement thrilling thrills thrillerish exhilarating breathless
gripping gripped suspenseful suspense terrifically dynamite crackerjack
funny funniest hilarious hilariously hilarity hysterically uproarious uproariously
riotous sidesplitting wittily witty wittiest wit droll drollery uproar
laughs bellylaughs rollicking riot ribald effervescent exuberant exuberance
joy joyful joyous joyously enjoy fun playful playfully pleasurable pleasure
pleases pleasing enchanting magical magic wondrous enchanting spellbound
intelligent intelligently intelligence smart savvy clever cleverly cleverness
perceptive penetrating observant insightful insight incisive astute thoughtfulness
thoughtful thoughtprovoking provocative provoking illuminating illuminates
revelation revelatory revealing edifying enlightening instructive
inventive inventiveness imaginative imagination creativity creative original originality
innovative innovation groundbreaking groundbreaking audacious audacity daring bold
visionary inspired refreshing refreshingly freshness fresh vibrant vitality vibrant
lively liveliness vivacious energetic energy zest zestful zesty gusto
crisp brisk sprightly snappy jaunty buoyant buoyancy sparkling sparkles
rich riches richness textured nuanced nuance subtle subtlety sophisticated sophistication
elegant elegance stylish style stylized sumptuous lush ravishing ravishingly
striking stunning arresting eyeopening picturesque sumptuous resplendent
impressive impresses impressed impressively admirable admirably admire admiration
accomplished accomplishment assured assurance confident confidence consummate
expert expertly skillful skilful skillfully skilfully deft deftly deftness
polished precision impeccably impeccable seamless seamlessly virtuosity
effective effectively credible believable convincing convinces authentic authenticity
genuine genuinely honest honesty truthful truthfulness sincerity sincere
sensitive sensitively compassionate compassion humane humanity humanistic
tender tenderness affectionate affection empathetic empathy heartfelt
recommend recommended recommends worthwhile worthy admirable laudable commendable
kudos bravo bravos praise praiseworthy applauded applause applaud deservedly
success successful succeeds succeeded triumphs excels excels excellence
outdoes outshines outdid surpass surpasses delivers delivered satisfying
outdid excels aces perfect perfectly ideal enchanting
""")
_words(1.80, """
good better fine finer finest verygood solid strong stronger strength strengths
fascinate engross captivate enthrall mesmerize enchant amaze delight dazzle
excel succeed entertain transfix transfixes transfixing magnetic magnetism
engaging engaged engages engagement involving involves invested involvingly
interesting interests intriguing intrigue intrigues intrigued curious curiosity
surprising surprisingly surprises surprise unexpected unpredictable unpredictability
memorable indelible memorable noteworthy notable remarkable remarkably
distinctive distinct distinguished unique unusual singular idiosyncratic
appeal appeals engagingly amiable agreeable agreeable pleasant pleasantly
likable likeable liked likes admired attractive attraction charismatic
enjoy amuse amusing amused amuses amusement comical comic comedically
funnier laugh laughter laughing chuckle chuckles chuckling giggles giggling
smile smiles smiling grin grinning cheer cheering cheers cheerfully merry
cheery cheerful joyous lark hoot blast treat romp frolic bubbly bouncy breezy
gleeful glee giddy giddily bliss blissful satisfying enough-to-satisfy
funkiest funky cool hip hipper sassy saucy sexy sexiness sensual sensuality
spirited spunky plucky feisty pluck spunk cheeky impish mischievous sly wry
acerbic mordant sardonic irreverent irreverence subversive subverts satiric
pointed pointedly biting barbed edgy crackling crackles zing zippy zip punchy
punch punches kick kicks kinetic dynamic propulsive momentum adrenaline
tense tension taut tautly tight tightly lean economical efficient nimble
fastest snazzy slickest fluid flowing graceful grace gracefully
handsome prettily pleasing gorgeous photographic painterly picturesque
colorful colourful colorful vibrant vividly vivid vividness atmospheric atmosphere
immersive visceral tactile evocatively expressive expressive expressiveness
spiritual soulful soulfulness humanity heartfelt warmth warm warmly heart
depth deep deeper layered layers complex complexity intricate intricacy
intimate intimacy personal universal meaningful substance substantial
subtle nuanced mature maturely maturity grownup adult intelligent
resonates resonate linger lingers lingering enduring timeless classic
involving absorbing rewatchable quotable quoteworthy watchable absorbing
sturdy respectable pleasing satisfying satisfying gratifying nifty neat adept
able adroit adroitly capable proficient competence competent assuredly expert
commendable intelligent elegant tasteful tastefully class classy
faithful fidelity realism realistic naturalism naturalistic lifelike
true truth emotionally emotional honest directness frank frankness candid
unflinching unblinking uncompromising unpretentious unassuming understated
understatement restrained restraint spare spareness economical concise
unconventional ambitious ambition enterprising challenging challenge
courage courageously courageous fearless fearlessly brave bravery
fierce intensity intense intensely passion passionate passionately
fervent fervor urgency urgent immediacy vital vivacity robust muscular
intricately slyly shrewd shrewdly perceptiveness balanced balance
magical whimsical whimsy offbeat quirky quirkiness eccentric eccentricity
oddity tantalizing tantalising tantalizes tempting inviting accessible
absorbed addictive addicting absorbing satisfying satisfying exhilaration
harrowing chilling chills shivers shivery frightening scares scary terrifying
spooky unnerving unsettling disturbing sobering searing wrenching heartrending
heartbreaking devastating shattering heartbreaking bittersweet melancholy
hypnotizes hypnotises reenjoyable engagingly electric electricity spark
chemistry rapport ensemble standout standouts highlight highlights
standout revelation rediscovery discovery landmark milestone achievement
achieves achievement accomplishments exemplary model memorable
underrated underappreciated overlooked auspicious promising promise
promises potential talent talents talented gifted gifts flair panache finesse
craftsmanship craft artistry artistic artful elegance intelligence
inventiveness inventively resourceful resourcefulness dexterity dexterous
respect respects respectability respectworthy credit deserves laud worth
admirer admirers loved loves adores adored adoration adore affectionately
welcome welcomed welcomes grateful gratitude gratifying worthwhile
superior substantial satisfying richer richest rewarding cherish cherished
""")
_words(0.92, """
decent passable serviceable okay ok adequate fair modest modestly
competently professional workmanlike functional tolerable harmless inoffensive
diverting diversion distraction distracting respite agreeable
interesting curiosity odd curious peculiar eccentric weird strange bizarre
unorthodox experimental surreal surrealism dreamlike dreamy ethereal
natural simple simplicity comforting comfortable accessible familiar
bittersweet wistful nostalgia nostalgic nostalgic fond fondly affection
gentle gently graceful relaxed leisurely placid mellow sweet sweetness
cute cuddly endear charismatic chutzpah mischievous perverse wicked wickedly
extravagant epic ambitious ambition lavish grand sweeping operatic mythic
meditative meditation reflective philosophical probing exploration explores
explore examination examines examines glimpse portrait study tribute homage
document documents chronicle chronicles captures capture captured depicts
evokes conjures articulate articulate portraiture recreate recreation
recreates recreating celebrates celebration celebratory addresses uncover
unearth unearths reveals confront confronts tackles questions examines
essence spirit soul morality truths ideas observations details detail
characterization characterizations themes thematic relationships interaction
humor humour humorous human humanist humanity humane heart humanity
emotions affection innocence heartache sorrow poignant melancholy
dramatic theatrical cinematic literate literary cultural social political
intellectual quiet contemplative haunting elegance quality value message
appeal musicality rhythm music melodies melodic choreography
meticulous painstaking painstakingly carefully careful detail meticulous
credible fidelity documentary authenticity conviction integrity commitment
boldness imagination daring bravely expertly twist twists surprises
vision perspective texture impact presence originality personality
spirit spirit generosity generous lovingly loving love care caring
appreciate appreciated appreciation satisfies satisfy success
guts gutsy gutsiness attitude eccentricities ambition ambition
edge energetic stylish chic pop pizzazz pizzaz vim verve lively
relief wit verity acumen ingenuity polish crafted fashioned
succeeds manage manages managed delivers works worked worth
stylish picturesque sunlit handsome prettiness graceful
undeniable undeniably certainly unquestionably surely happily thankfully
darkest darkness eerie eerily creepy creepiness ominous primal brutal
raw gritty grittiness unvarnished stark piercing austere
eccentric evocative ponder consider considerately
""")
_words(-3.70, """
awful atrocious horrible horrid horrendous abominable terrible dreadful
abysmal execrable appalling appallingly wretched miserable misery
atrocity travesty disaster disastrous catastrophe catastrophic debacle
fiasco failure abomination disgrace disgraceful embarrassment embarrassing
embarrassingly embarrassed humiliating pathetic pathetically pitiful pitifully
lousy rotten woeful woefully laughable laughably ridiculous ridiculously
ludicrous ludicrously preposterous rubbish garbage trash crap crappy crud
sucks sucked stinks stinker stinkers reek reeks turd dreck drek junk
godawful ghastly unforgivable inexcusable intolerable insufferable unbearable
unwatchable unendurable excruciating excruciatingly interminable interminably
torturous tortuous torture agonizing agonising painful painfully punishing
deplorable reprehensible repellent repugnant offensive offensively odious
vile loathsome contemptible despicable hateful disgusting disgust repulsive
worst worsts atrociously hopeless hopelessly worthless useless pointless
inept ineptitude incompetent incompetence idiocy idiotic moronic imbecilic
brainless witless mindless mindlessness lifeless lifelessness soulless
unfunny humorless humourless charmless joyless worthless execrable
deadening deadeningly unmitigated irredeemable irredeemably unforgivably
bombed bomb botch botched butchered mangled squandered wasted squanders
snoozer snoozefest borefest boreathon dud duds dudsville clunker clinker
""")
_words(-2.66, """
bad badly poor poorly inferior subpar substandard shoddy shabby secondhand
mediocre mediocrity middling belowaverage bland blandness dull dullness dulled
boring boringly bored boredom bore bores tedious tediousness tedium tiresome
tiring weary wearying wearisome dreary dreariness drab dreck leaden plodding
plods plod stodgy sluggish slogs slog drag drags dragging draggy lethargic
languid listless limp inert sluggishness soporific sleepinducing sleepy
monotonous monotony repetitive repetition repetitious redundant redundancy
overlong overlengthy overlength bloated bloat padded padding overblown
pretentious pretension pretensions pompous pomposity portentous ponderous
laborious labored laboured laboriously lumbering cumbersome belabored forced
strained straining contrived contrivance contrivances contrivance artificial
phony phoney fake bogus fraudulent insincere dishonest dishonest disingenuous
unconvincing unpersuasive unlikely implausible implausibility improbable
unbelievable farfetched ludicrous nonsensical nonsense senseless incoherent
incoherence incomprehensible unintelligible confusing confused confusion
muddled muddle muddles murky clutter cluttered messy mess disorganized
disjointed disjointedly uneven unevenness erratic haphazard chaotic scattered
scattershot unfocused unfocussed unfocused formless shapeless aimless
directionless pointless purposeless unnecessary needless gratuitous gratuitously
unsatisfying dissatisfied unsatisfied disappointing disappoints disappointed
disappointment disappoint letdown anticlimactic anticlimax underwhelming
underwhelms underwhelm uninspiring uninspired uninteresting disinteresting
uninvolving unengaging unappealing unappealingly unlikable unlikeable unpleasant
unlovable unsympathetic irritating irritates irritated irritation annoying
annoys annoyed annoyance aggravating aggravates grating grates gratingly
frustrating frustrated frustration frustrates infuriating infuriates infuriated
alienating alienates alienated alienation offputting distancing distracting
distracts distractions intrusive distracting obtrusive obnoxious obnoxiously
objectionable distasteful tasteless crass crude vulgar vulgarity tacky tawdry
sleazy sleaze sordid smarmy smug smugness smirking smirk sneering snide
meanish nasty nastiness meanest petty spiteful vindictive cruel exploitative
exploits exploitation manipulative manipulation manipulates calculating calculated
cynical cynicism contempt contemptuous pandering panders panders panders
paternalistic patronizing patronising condescending condescension insults
insult insulting insultingly offensive offends offended sexist sexist misogynistic
misogyny racist racism homophobic slur stereotypical stereotyped stereotype
stereotypes caricature caricatures cardboard caricaturish caricatured
cookiecutter generic formula formulaic formulaically predictable predictability
foreseeable telegraphed obvious blatantly blatant simplistic oversimplified
shallow shallowness superficial superficiality thin thinnest flimsy flimsiness
sketchy underwritten underdeveloped undeveloped hollow empty emptiness vacant
vacuous vacuity vapid vapidity inane inanity insipid infantile juvenile jejune
stupid stupidity dopey dumb dumbest dumber dumbed dumbness dimwitted dimwit
silly silliness goofy goofiness foolish foolishness absurd absurdity absurdities
credulous clumsy clumsily clumsiness clunky clumsily awkward awkwardly awkwardness
hammy hamfisted heavyhanded leadfooted wooden stilted stiff stagy stagey
stagestruck amateurish amateurism amateur amateurishly maladroit inelegant
hampered hamstrings hamstrung undermines undermined undermining undone
flounders floundering falters faltering stumbles stumbles stumbling founders
misfires misfire misfired misbegotten misguided misjudged miscalculated
miscalculation mistake mistakes mistaken miscast miscasting mishandled
misses missed missing miss failure fails failed fail failing failings
weak weaker weakest weakness weaknesses feeble feebleness frail anemic anaemic
toothless toothlessness spineless flabby flaccid flaccidity limp impotent
uninspired unoriginal unoriginality derivative derivativeness recycled retread
rehash rehashes rehashing ripoff ripoffs imitation imitative copycat knockoff
hack hackwork hacked hackneyed cliched cliche cliches shopworn shopworn
wornout tired threadbare threadworn stale staleness musty moldy dusty
rehashed outmoded outdated dated antiquated oldhat secondhand recycled
predictable conventional conventionality routine pedestrian unremarkable
unmemorable forgettable forgettably forgetful disposable dispensable
unnecessary superfluous negligible inconsequential irrelevant immaterial
underwhelmed unexciting unexceptional undistinguished lackluster lacklustre
lackadaisical halfhearted slapdash slipshod sloppy sloppiness careless
hasty rushed choppy patchy patchwork ungainly graceless artless
turgid stolid stultifying stultifies numbing numbed numb numbingly
deadwood deadweight deadened drudgery torpor torpid inertness arid
soulless sterile antiseptic bloodless passionless impersonal anonymous
overripe overwrought overcooked overdone overkill overload overloaded
excessive excesses excess extraneous superfluous overwriting overwritten
overacting overacted overplayed overplay overbearing overstuffed overextended
indulgent indulgence indulgences selfindulgent overindulgent overindulgence
melodramatic maudlin mawkish sappy syrupy schmaltz schmaltzy treacly treacle
saccharine sugary syrup cloying cloys gooey mushy hokey hokum corny cornball
cheesy cheesiness campiness campy kitschy schmaltzy bathetic sentimentalism
sentimentality overemotional histrionic histrionics hyperactive hysterics
preachy preachiness preach didactic sermonizing lecturing sanctimonious
moralizing moralistic sanctimony hectoring whiny whining shrill shrillness
noisy noise raucous cacophonous bombastic bombast overbearing blaring
overstated overstating overstatement ostentatious overwieldy unwieldy
provincial tasteless ineffectual ineffective ineffective unworkable
outlandish farcical risible laughably embarrassing cringeworthy cringey cringe
cringes wince winces squirm squirming cringeing cringing groan groans groaner
groaners groaning yawn yawns yawning snooze snoozing snore snoring nap
depressing depressingly dismal dismally grimness grimy drear dreary
nauseating sickening queasy queasiness icky ick yucky yuck gross grossest
exploit exploitive exploitation exploitable trashy lowbrow trashiness
dumbfounding puzzling perplexing baffling baffled inscrutable impenetrable
unintended unintentional unintentionally laughably accidentally
squander squanders wastes waste wasting wasted wasteland pointless
""")
_words(-1.63, """
flat flatness falls downfall fault faults faulty flaw flaws flawed problems
problem problematic troubled troubles trouble suffers suffering suffer
lacks lack lacking lacked shortage devoid bereft absent absence missing
loss loses lose lost squander sacrifice sacrifices compromised compromises
overlooks overlooks overlook neglect neglects neglected ignores ignored
risks risk peril dangers dubious doubtful questionable suspect suspicious
flimsy sketchier thinly sketchiness scant skimpy meager meagre paltry puny
minor lesser least weakish pale pales pallid pallor muted remote detached
aloof lifeless frigid chilly cold coldly lukewarm tepid halfhearted halfbaked
lackadaisically apathetic indifferent indifference disengaged disconnected
distant distancing distancing unfulfilled unfulfilling unresolved incomplete
unsuccessful unsuccessfully disservice disconcerting disheartening dismaying
unfortunate unfortunately regrettably regret regrettable sadly alas sadder
unrewarding unworthy unwelcome uninformed unappealing unhelpful unimportant
resistant resistant offends alienation discomfort uncomfortable unpleasantness
detracts detract distractions distract discordant discord dissonant uneven
stereotyping oversimplification oversimplifies simplified caricaturing
convenient convenience trite triteness banal banality banalities platitudes
mothball mothballed familiar familiarity common commonplace unadventurous
undemanding unambitious uninventive pedestrian ploddingly lumber lumbers
monochromatic formulae repetitive tires tired tiresome fatigued fatigue
slowness slowing slow slower slowest lengthiness lengthy endless endlessly
exhausting exhausted gruelling grueling punishing brutalizing puny aimlessly
bombards bombard bombardment busy hectic frantic frenetic frenzied
hyperkinetic hysterical hysterics clutter disarray disorienting disoriented
gimmick gimmicks gimmicky contraption gimmickry tricks trickery
gaps holes loopholes inconsistencies inconsistent inconsistency lapses lapse
flaws flawlessnessless shortcomings shortcoming drawbacks drawback
obligatory perfunctory mechanical mechanically rote mechanical contrivances
disbelief illogical illogic irrational illconceived outlandish implausibly
trivial trivializes triviality trivialities slight slightness inconsequential
expendable forgettable uninvolved bored boring chronic mediocrity
disposable extraneous overkill annoying weary pointless deficient deficiency
shortchanged cheats cheat cheated cheating copout copouts shameless shamelessly
plagiarized pilfered contrived strained derivative mimics cribbed borrowed
wobbly wobble shaky shaky faltering slapdash uneven unfashionable
conflicting conflicted ambiguous muddiness perplexed bafflement
lacklustre comedown letdowns shortcomings misstep missteps miscue miscues
backfire backfires backfired crumbles collapses collapse implodes sinks sinking
derails derailed derailing deteriorates degenerates devolves fizzles flops flop
sags sagging sag bogged wallows wallowing succumbs resorts struggles struggling
meanders meandering rambling rambles wandering wanders drifts drifting
lost lostness overload fuss fussy fusty stuffy stiffly stifling
strained stretches stretching stretch inflated inflation forced forcefed
desperate desperately desperation blatancy overselling oversells
guilty guilt vacillates compromised corrupted shallow careless incoherently
overburdened burdensome burden weighed plagued marred mars saddled beset
undercuts undercut smothered smothers sabotages sabotaged hampered
insufficient inadequacy inadequate ineffectiveness inertia
sanitized watered diluted muted truncated hurried hurriedly
irritant abhorrent tackiness glib glibness smugly facile facilely
narcissism narcissistic egotistical conceit conceited egocentric
vulgarities puerile sophomoric potty smutty smut prurient juvenile juvenilia
brash juvenile crass abrasive tiresomely laboured laborious
ripoff rejects rejection backlash resentment loathing loathe hate hated
detest detested dislike disliked despise despised exasperating exasperation
belittles betrays betrayal betraying undermines despairs
""")
_words(-0.70, """
reservations reservation quibbles quibble caveats caveat misgivings unevenly
occasionally occasional somewhat mildly marginal marginally relatively merely
barely almost rather seems seemingly purported purportedly allegedly
ostensibly supposed wannabe wouldbe wannabes wanna attempts tries trying
oddly strangely frustratingly curiously strangely bothered bother bothers
conflict bitter bitterness bleak grim gloomy depressive depressing sadness
fear afraid angry anger banal mechanical commercial commercialism mainstream
teenybopper sitcom sitcoms shallowish televisionish sitcomish
longer loudly loud bigotry brutality violent violence nasty grossed blood
messier chaotic strange strangeness lunacy madness chaos cramped
unsettled harden incomprehension questionable gimmick imitation excess
difficult difficulty doubt doubts questionable instead lacking
""")

# Explicit adjustments where neighboring words or senses above differ.
_words(3.15, """
brilliant phenomenal fabulous riveting exhilarating breathtaking mesmerizing
enjoyable engrossing delightful hilarious wonderful irresistible superb
terrific masterpiece masterpieces masterworks ingenious ingenuity genius
gem gems triumph triumphs spectacular sublime brilliant brilliance
excellent unforgettable extraordinary beautifully magnificent best
magnificently bravissimo electrifies magical mesmerizingly uproarious hilarious
unforgettable enthralling deserves-an-oscar transcends astonishing
effortless effortlessly flawless spellbinding
""")
_words(2.35, """
touching moving funny poignant creative clever imaginative compelling
succeeds insightful charming fascinating intriguing engaging sweet fun
amusing moving affectionately tenderness tense crafted expertly artistry
scares scary thrilling witty entertaining entertain entertainment satisfying
richly engrossed colorful heartfelt warm emotional evocative meaningful
impressive inventive surprise surprising delightful reward rewards
stylish haunting stylishness handsome beautifully enjoyable deft
accomplished exceptional memorable enjoy enjoyed rewatchable worthwhile
pleasures enchanting transfix transfixes stunning inspires inspired
wellbeing wows wow amazing amazes raves ravishing revels jubilation
daring dynamism graceful hook hooks hooked mesmerism glorious excellence
resuscitates redeems redeemed redeeming salvages redeem crackerjack
ferocious ferociously steely tenacity bravely gallant eyeopener generosity
illuminating evocative unforced unhurried unerring uncommonly understated
unaffected keen keenly perspicacious artistry crispness eloquent eloquence
unpretentious unassuming unflinching disarming disarmingly
acerbity infectious contagious restorative buoyant convivial spiffy
sparkling dazzler naturalism assured accomplished impress praise
likable likeable refreshing inspiration originality commended laudatory
spectacle enthrallment excitement exhilaration endearment
""")
_words(1.18, """
heart human chemistry warmth charm talent talents craft crafted care
skill works works admire appealingly unflappable compassionate sympathy
poetry flesh genuine advances above artfulness reasons laud humility
catharsis cathartic provocative provocation unnerving unnerves shaken
stark brutal unsettling chills shudders scary haunting eerie cautionary
devotion irony satires perceptiveness thematic compassion rich imaginative
merits merit saving save savior rescues redeemed promising endures
plays engagingly insight perspective captures indelibly generously generosity
""")
_words(-3.20, """
bad awful inept worst wretched terrible tedious boring uninspired dull
waste wastes wasted pointless fails failure unfunny stupid dreadful
disappointment disappointing disappoint disappointed stale cliche cliched
predictable bland insipid trite banal vapid hackneyed pitiful contrived
ludicrous ridiculous laughable embarrassing sham shameless spineless
abysmal obnoxious annoying mess boringly repellent dreary tired
cartoonish amateurish overblown gimmicky soporific snooze lousy
insulting appalls appalled disgusts drivel piffle baloney hooey bunk
malarkey twaddle dross offal stink stinkeroo turkey clunker dumpster
brain-dead manques stinkbomb monstrosity unpleasantry oafish dumbbell
blandly appallingly pedestrian pedestrianism hackneyed
""")
_words(-2.22, """
frustrating frustration misguided too-little distracting distracted
clumsy shameless unintentional unintentionally manipulative silly weak
underused underutilized underused unearned unearned undeserved
uninteresting pointless squander flails flailing fumbles fumble muffed
sinking sinks stalled stagnant stagnates plummets collapses
pales pallid paltry skimpy formulaic formulary irrelevance
backwards miscalculates bungled bungles bungle bungling bumbling
crippled cripple cripples hobbles hobbled hinders detriment detrimental
ridicule repulsed disappointed dour tedious flat flatly affectless
expressionless one-note cardboard contrives ludicrous overindulgent
exploitative perversity undesirable unattractive unaffecting unexcited
unimaginative unimaginative uncreative unimaginatively unimaginably
unadornedness unsteady unbalanced unappealing dissatisfying
sloganeering pandering pander pontificating lecturing snobbery
deadpanlessness churlish childish childishly clueless cluelessness
irrelevance thinly plodding lifelessness laziness lazy lazily
disastrously ruin ruins ruined ruinous drivel burdens bellyflop
unwieldy bumpy detritus flotsam derivative stale staleness
charades mystifying disjointed infuriates miserable rawnessless
incoherently tangential meandering terminally mercilessly relentlessly
utterly-empty redundant stuck stranded wasted misguided
fatuous fatuity gratuitous misguided inexcusable unrewarding offensive
overrated overhyped unlikeable overwrought undramatic uncinematic
bludgeon bludgeons betters-it-not mangles inertness cutesy coy cloying
oblivious objectionable derivative inelegant unrelenting pretends
tedium ditzy cynical facetious obnoxious tawdriness anachronistic
""")
_words(-1.02, """
oddly darkly cramped haphazard meritless wallow
outstays exceeds preposterously struggling uncomfortably confines
spinelessly estranged despair laughably disinterest overly overmuch
crassness leering leers gratuitously detours distracting convoluted
unexplained sensibilityless scatterbrained crankiness crabby
parodying selfconscious nonsensical needless artificially
transparent stolid ungainly reworking imitating unbalanced
neglected alienates overwhelmed overwhelming excessive
""")
# Context-neutral or double-edged expressions.
_words(0.0, """
attempts trying tries works-at plays reasons above that commercial social
television fear sadness blood violence violent cultural political madness
anger conflict questions darkly dark drama movie picture film horror thriller
dramatic comedy comicbook end ending filmmaker actor romantic minutes
character characters evil dead death killing killed killer die murder crime
suffering victim loss sad fight war girl losing true-story family
instead entirely utterly very certainly just undeniable undeniably
extraordinarily incredibly thoroughly perfectly rather relatively
genuinely amazingly surprisingly remarkably extremely completely
intensely strikingly sadly-not darkly grimly somewhat suitably
grossed concerns challenge alienation longer human study details
hard real trip adult direct apparently considerable certainly work
losing mean familiar music supposed rarely hardly unlike scare
try least overly allegedly seemingly merely barely marginally
""")
_words(0.5, """comic documentary comicbook humor humour humanity genre-bending harsh unrelenting overwhelming""")
_words(1.45, """scary shocking disturbing emotional heartbreaking intense accurate works managed laud entertainingly""")

# A little non-English review vocabulary (also handles accents by normalization).
_words(2.9, """
excelente excelente extraordinaria extraordinario magnifica magnifico estupendo
estupenda maravillosa maravilloso maravillosa esplendida esplendido brillante
magnifique formidable excellent excellente reussi reussie chefdoeuvre
genial fabulosa fabuloso fantastica fantastico sobresaliente inolvidable
divertida divertido entretenida entretenido emocionante conmovedora
conmovedor espectacular fascinante encantadora impresionante recomendable
superbe remarquable genial genialissime meilleur meilleure captivant
ottimo eccellente bellissimo wunderbar wunderbarste grossartig
""")
_words(1.7, """
buena bueno buenos buenas mejor mejores bella bello interesante interesante
eficaz inteligente sensibilidad intenso intensa atractiva atractivo humoristico
hermosa hermoso talento habil magistral ingeniosa ingenioso sorprendente
disfrutable tierna profundo profunda graciosa gracioso poderosa entretenida
jolie joli beau belle bon bonne amusant drole emouvant amusante passionnant
bello bella interessante divertente buon gut unterhaltsam
""")
_words(-2.8, """
malo mala malos malas peor peores aburrida aburrido aburrimiento aburridisima
horrible terriblemente decepcionante decepcion pesima pesimo lamentable
mediocre flojo floja tonta tonto estupida estupido ridicula ridiculo
predecible convencional fallida falla fracasa fracaso tediosa fastidiosa
insipida patetica pretenciosa absurda innecesaria pesimamente
mauvais mauvaise ennuyeux ennuyeuse nul nulle decevant penible
brutto noioso schlecht langweilig
""")

# Literal constructions, consumed as units, so e.g. 'a waste of talent'
# cannot be scored as praise for the talent.
_PH = {}


def _phr(v, s):
    for p in s.replace("\n", "|").split("|"):
        p = p.strip()
        if p:
            t = tuple(_tokens(p))
            if t:
                _PH.setdefault(t[0], {})[t] = v


_phr(4.2, """
tour de force|tour de force performance|force of nature|a must see|a must-see movie
must see|must viewing|required viewing|essential viewing|not to be missed|do not miss
should not be missed|shouldn't be missed|not to miss|unmissable experience
one of the best|one of this year's best|one of the year's best|among the best
best of the year|best films of|best movies of|best movie of|best film of|best thing since
instant classic|modern classic|minor classic|minor masterpiece|small masterpiece
work of art|works of art|work of genius|works of genius|piece of genius
pure gold|pure delight|pure pleasure|sheer pleasure|sheer delight|pure joy|sheer joy
a standout|a revelation|a triumph|an absolute delight|an absolute joy|a knockout|a knock out
a stunner|a winner|a corker|a dazzler|a humdinger|a hummer|a humbling experience
a crowd pleaser|crowd pleasing|standing ovation|two thumbs up|thumbs up|four stars
blew me away|blow you away|blows you away|knocks your socks off|knocks it out of the park
worth every penny|worth the price of admission|worth the ticket price|worth seeking out
deserves to be seen|demands to be seen|needs to be seen|ought to be seen|should be seen
cannot recommend it enough|can not recommend it enough|can not say enough good|highest recommendation
highly recommend|wholeheartedly recommend|highly recommended|not soon forget|will not soon forget
sticks with you|stays with you|will stay with you|gets under your skin|under your skin
edge of your seat|edge of my seat|on the edge of our seats|edge of their seats|white knuckle
left me breathless|takes your breath away|take your breath away|breath of fresh air
a home run|home run|home-run|hits the mark|hits its mark|hits the spot|hits the jackpot
fires on all cylinders|firing on all cylinders|pulls it off|pull it off|brings down the house
is a natural|are a joy|have a ball|having a ball|electric charge
""")
_phr(2.95, """
worth seeing|worth a look|worth a watch|worth watching|worth checking out|worth the trip
worth catching|worth a visit|worth your time|worth the time|worth the wait|worth the effort
worth a ticket|worth the ride|worth noting|well worth|well worth watching|well worth seeing
worthwhile experience|time well spent|money well spent|well spent|worth revisiting
worthwhile diversion|pleasant diversion|great time|good time|good times|fine time
a good movie|a good film|better movie than|a fine film|a fine movie|feel good|feels good
one of a kind|stands out|stand out|stands apart|in a class by itself|stands above
head and shoulders above|cut above|a cut above|leaps and bounds|ahead of its time
best in|at its best|at their best|at his best|at her best|in top form|top form|fine form
first rate|first class|top notch|top drawer|top flight|top shelf|top of the line
world class|grade a|a list|five star|blue ribbon|award worthy|oscar worthy
oscar caliber|award winning|prize winning|well deserved|well earned|deserves credit|credit is due
more than delivers|come through|comes through|comes alive|come alive|comes to life
come to life|give life to|brings to life|bring to life|breathes life|breathes new life
rings true|ring true|feels true|feels real|feel real|hits home|hit home|truth to it
on target|on the mark|gets it right|get it right|gets this right|gets everything right
right on target|just right|right note|right notes|right balance|strikes a balance
finely tuned|finely honed|finely observed|finely wrought|keenly observed|closely observed
sharply observed|well observed|carefully observed|acutely observed|deeply felt|deeply affecting
finely acted|well acted|well directed|well constructed|well paced|well conceived|well done
well crafted|well written|well told|well made|well executed|well shot|well photographed
well designed|well mounted|well handled|well played|well cast|well worth|well realized
well drawn|well rounded|well developed|fully realized|fully formed|richly detailed
expertly crafted|meticulously crafted|lovingly crafted|beautifully shot|beautifully acted
fast paced|quick witted|sharp witted|razor sharp|razor wit|rapier wit|razor edged
thought provoking|eye opening|eye opener|eye popping|eye candy|visually arresting
jaw dropping|jaw dropper|mind blowing|mind bending|mind expanding|mind boggling
gut wrenching|heart wrenching|heart rending|heart warming|heart stopping|heart pounding
soul searching|soul stirring|heart felt|tugs at|tug at|tug on|lump in your throat
fun to watch|fun to see|joy to watch|pleasure to watch|pleasure to see|delight to watch
laugh out loud|laugh aloud|laugh aloud funny|laughed out loud|laughing out loud
belly laughs|belly laugh|big laughs|big laugh|good laughs|good laugh|real laughs
plenty of laughs|a lot of laughs|lots of laughs|a laugh riot|a hoot|a riot|a gas
a kick|a blast|a treat|a delight|a pleasure|a joy|an unexpected pleasure
great fun|good fun|much fun|loads of fun|lots of fun|a lot of fun|all kinds of fun
light on its feet|light touch|sure hand|sure handed|sure footed|deft touch
feast for the eyes|visual feast|feast for|sight to behold|worth the price
pitch perfect|note perfect|near perfect|dead on|spot on|dead right|picture perfect
knockout performance|winning performance|strong performances|perfectly cast
scene stealer|steals the show|steals the movie|steals every scene|steals the film
has it all|have it all|has a lot to offer|has plenty to offer|has something to say
something to say|has its own voice|finds its voice|makes its mark|makes an impression
leaves an impression|leaves a lasting impression|leaves its mark|makes you think
food for thought|much to admire|much to enjoy|much to like|much to recommend|a lot to like
plenty to like|plenty to enjoy|plenty to admire|a lot going for|goes a long way
goes beyond|above average|above the average|raise the bar|raises the bar
more than the sum|greater than the sum|more than skin deep|works on every level
will not be disappointed|won't disappoint|does not disappoint|never disappoints
not disappointed|will not regret|did not want it to end|do not want it to end
does not let up|never lets up|not a dull moment|never a dull moment|never boring
never dull|never less than|never ceases to amaze|never fails to impress
never fails to entertain|could not be better|could not be more timely|can do no wrong
can not go wrong|can not take your eyes off|can not take my eyes off|hard to resist
impossible to resist|hard to forget|hard to beat|hard to top|hard to fault
hard not to admire|hard not to like|impossible not to like|impossible not to love
cannot help but like|could not help but like|will love|fell in love|in love with this
pleasant surprise|pleasantly surprised|better than expected|better than you might expect
exceeds expectations|exceeds your expectations|exceeded my expectations|exceeds its grasp
keeps you guessing|keep you guessing|keeps us guessing|keeps you watching
held my attention|holds your attention|holds the attention|commands attention
kept me interested|kept me watching|kept me guessing|kept me laughing
makes me want to see|want to see it again|see it again|go see it|go see this
run out and see|do yourself a favor|take a chance on|check it out|seek it out
see this movie|see this film|high marks|gets my vote|gets my nod|give it a chance
an old friend|like a charm|succeeds on its own terms|works on its own terms
labor of love|labour of love|triumph of|rich in|rewarded with|rewards the
without a false note|not a false note|without missing a beat|never misses a beat
brings out the best|brings out the child|can not wait to see|glad i saw
worthy of attention|well worth your while|worth your while|a rare bird|a rare treat
""")
_phr(1.70, """
not bad|not half bad|not too bad|not so bad|not all bad|not a bad|not such a bad
not awful|not terrible|not the worst|no slouch|not without|is not without
has its moments|has moments|had its moments|have their moments|has its charms
has its pleasures|does have its moments|does the job|gets the job done
does its job|does its best|fits the bill|serves its purpose|just enough
good enough|enough to recommend|easy to like|easy to enjoy|easy on the eyes
can not help but|can not help liking|can not help feeling|hard not to|difficult not to
nothing wrong with|not much wrong|no complaints|not complaining|nothing to sneeze at
not to be confused|goes down easily|goes down easy|makes up for|make up for
more than makes up|saves the movie|saves the film|saving grace|saves the day
give it credit|to its credit|to his credit|to her credit|to their credit
guilty pleasure|guilty pleasures|good natured|good humored|good humoured|good hearted
big heart|big hearted|heart in the right place|has a heart|a lot of heart
at heart|from the heart|in good hands|safe hands|steady hand|knowing wink
tongue in cheek|tongue firmly in cheek|does not take itself|never takes itself
not take itself|sense of humor|sense of humour|sense of fun|sense of wonder
sense of place|sense of purpose|sense of urgency|sense of dread|air of mystery
slice of life|three dimensional|flesh and blood|larger than life|a human face
pays tribute|love letter|love song to|pays homage|pays off|pay off|payoff is worth
steeped in|true to life|true to its|true to the|attention to detail|a fresh look
new life|fresh life|fresh perspective|fresh spin|new spin|fresh take|new twist
broke new ground|breaks new ground|break new ground|ahead of the pack
brings something new|something different|dares to|dare to|takes risks|takes chances
under the surface|beneath the surface|gets to the heart|holds up|hold up well
old fashioned fun|old fashioned entertainment|old fashioned charm|old school charm
small gem|little gem|hidden gem|pleasant enough|fair enough|easygoing charm
have a good time|can do worse|could do worse|could be worse|far worse
never loses sight|never loses its|not lose sight|not afraid|never afraid
refuses to shy away|does not shy away|does not flinch|pulls no punches
never stoops to|never resorts to|does not resort to|avoids the pitfalls
refuses to compromise|without condescension|without preaching|without sentimentality
leaves you wanting more|leaves us wanting more|wanting more|keeps it real
find an audience|find its audience|well suited|like it|liked it|love it|loved it
like this movie|like this film|love this movie|love this film|had me laughing
win you over|wins you over|won me over|won over|wins us over|found myself laughing
engages the|warmed by|fun for|right stuff|staying power|in fine|a ball
turn your brain off and enjoy|suspend disbelief|made me cry
""")
_phr(-4.20, """
one of the worst|among the worst|worst movies|worst films|worst movie|worst film
worst of the year|worst of all|new low|all time low|rock bottom|bottom of the barrel
a waste|total waste|complete waste|waste of time|waste of money|waste of talent
waste of a good|wastes the talents|wastes the talent|wasting the talent|wasted talent
wasted opportunity|waste of celluloid|want my money back|money back|hours of my life back
two hours of my life|get those two hours back|wish i had not|wish i hadn't
avoid at all costs|at all costs avoid|to be avoided|stay away|steer clear
do not bother|why bother|do not waste|do not go see|do not see this|do not see it
save your money|save your time|save yourself|skip it|skip this|give it a miss|give it a pass
not worth seeing|not worth watching|not worth your|not worth the|not even worth
nothing to recommend|little to recommend|nothing to like|nothing to enjoy|nothing works
redeeming feature|no redeeming|no saving grace|without merit|no reason to see
not a single laugh|not one laugh|not even funny|not remotely funny|not funny
dead on arrival|dead in the water|dies on the screen|dies on screen
falls flat on its face|falls on its face|flat on its face|falls apart|fall apart
unmitigated disaster|train wreck|car wreck|a turkey|a stinker|a disaster|a misfire
the pits|the dregs|piece of junk|piece of crap|pile of junk|pile of crap|pile of garbage
a complete mess|an unholy mess|a total mess|god awful|mind numbing|brain numbing
jaw droppingly bad|so bad it is|so bad that|as bad as|an insult to|insults the intelligence
beneath contempt|beyond belief|absolutely nothing|no business being|an exercise in futility
watching paint dry|watching grass grow|root canal|stick needles|poking needles
run screaming|theater in disgust|make it stop|make you gag|turns your stomach
two thumbs down|thumbs down|zero stars|what a mess|what a waste
""")
_phr(-2.95, """
miss the mark|misses the mark|misses its mark|missed the mark|wide of the mark
misses the point|miss the point|fails to deliver|does not deliver|falls short|fall short
comes up short|come up short|comes up empty|comes up wanting|found wanting
falls flat|fall flat|fell flat|lands flat|lands with a thud|with a thud|just lies there
falls to pieces|fall to pieces|never takes off|fails to take off|does not take off
never gets off|does not get off the ground|off the rails|off the tracks|loses its way
lose its way|loses its nerve|runs out of steam|run out of steam|runs out of gas
out of gas|out of ideas|out of control|runs aground|spins its wheels|going nowhere
goes nowhere|go nowhere|headed nowhere|gets nowhere|never goes anywhere|never gets going
never catches fire|does not catch fire|fails to catch|never comes to life|never quite gels
does not work|does not quite work|does not really work|did not work|never works
does not add up|never adds up|never comes together|does not come together|never gels
not up to|not equal to|not good enough|not very good|not that good|not so good
no good|not any good|is not good|not nearly enough|not enough|never enough
far from good|leaves much to be desired|leaves a lot to be desired|something to be desired
a shame|a pity|what a shame|what a pity|too bad|too little too late|too little
too much|too many|too few|goes on too long|much too long|way too long
far too long|goes on and on|on and on|drags on|drags along|interminably long
overstays its welcome|overstay its welcome|wears out its welcome|wears thin|wear thin
gets old|gets tiresome|asleep at|fall asleep|fell asleep|stay awake|staying awake
keep awake|keep my eyes open|checking my watch|look at your watch|checking your watch
have trouble caring|hard to care|difficult to care|impossible to care|who cares
could not care less|could care less|could not care|do not care|did not care
care less about|nothing to care about|no one cares|nobody cares|no one to care
do not believe|hard to believe|impossible to believe|hard to swallow|hard to buy
strains credulity|strains credibility|stretch credibility|stretches credibility
does not make sense|makes no sense|make no sense|little sense|no sense
no chemistry|zero chemistry|little chemistry|no tension|no suspense|no surprises
no laughs|few laughs|no fun|not much fun|not much of anything|not much else
nothing much|not much there|not much here|little else|nothing new|little new
nothing original|nothing fresh|nothing special|nothing more than|not much more than
not much better|not much of a|nothing going on|nothing happens|not a lot happens
not really about anything|nothing to say|little to say|not saying much|says little
so what|what is the point|what was the point|what is the use|what were they thinking
no point|serves no purpose|no reason|for no apparent reason|no payoff|no pay off
for all the wrong reasons|going through the motions|goes through the motions
by the numbers|by numbers|by the book|paint by numbers|connect the dots
cookie cutter|assembly line|off the shelf|off the rack|off the peg|bargain basement
run of the mill|garden variety|dime a dozen|par for the course|more of the same
same old|seen it all before|seen it before|seen before|been done before|been done better
been there done that|been there|done to death|done better|over and over|yet another
all too familiar|overly familiar|awfully familiar|over familiar|way too familiar
a poor man's|poor man's|poor imitation|pale imitation|watered down|knock off|rip off
second rate|third rate|fourth rate|second string|second hand|cut rate|low rent
cut and paste|bottom drawer|straight to video|direct to video|made for tv movie
sitcom pilot|sitcom episode|tv sitcom|very special episode|movie of the week
one dimensional|two dimensional|one note|one trick pony|paper thin|wafer thin
thinly drawn|thinly sketched|thin on|skimps on|short on|sketchily drawn
cardboard cutouts|cardboard cut outs|cardboard characters|stock characters|walking cliches
plot holes|plot hole|holes in the plot|holes big enough|swiss cheese|idiot plot
heavy handed|ham handed|ham fisted|ham fistedness|heavy going|lead footed
flat footed|tone deaf|tin ear|tin eared|out of tune|off key|false note|rings false
ring false|rings hollow|ring hollow|feels false|feels forced|feels like work
going for it is|only saving grace|only redeeming|the only good thing|one good thing
tries too hard|trying too hard|tries so hard|trying so hard|too hard to|too hard for
hard to follow|hard to sit through|hard to watch|hard to take|hard to tell
pain in the|chore to|slog through|sit through|endure the|test of endurance
wear you down|beats you over the head|over the head with|hit over the head|hit you over the head
brain dead|dead weight|dead end|dead ends|dead horse|deadening effect|leaves me cold
leaves you cold|leaves us cold|leave you cold|left me cold|leaves one cold
lack of interest|loses interest|lose interest|lost interest|loses steam|loses focus
all over the place|all over the map|out of focus|mixed bag|a let down|let down by
does a disservice|disservice to|disappointing results|a missed opportunity|missed opportunity
missed the boat|let the audience down|lets us down|is a bust|is a washout
laugh at it|laughing at it|unintentional laughs|unintentional comedy|unintentionally funny
so called|wants to be|pretends to be|tries to pass|tries to convince|wish it were
should have been|should have stayed|should have made|should know better|deserve better
deserves better|deserved better|have seen better|seen better|better left|best left|better off
have been better|would rather watch|rather be watching|rather have seen|better things to do
wanted to like|wanted to love|tried to like|wanted to enjoy|wish i could say
not for a minute|not in a good way|in the worst way|at its worst|at their worst
did we need|do we need|last thing we need|last thing the world|last thing we needed
does no favors|no favors|at the expense of|worse for|for the worse|not helping
out of place|out of touch|off putting|off puttingly|in bad taste|in poor taste
in name only|only in name|little more than|hardly more than|never rises above
rarely rises above|does not rise above|never amounts to|does not amount to|amounts to little
leave well enough alone|does not do justice|does not live up|fails to live up|never lives up
no substitute|no match for|not hold a candle|not even close|not a patch on
should have stayed home|stay home|wait for video|wait for the video|wait for the dvd
not worth it|do not recommend|can not recommend|not recommended|not going to recommend
have been avoided|left unmade|less than meets the eye|loses something in translation
outstays its welcome|gets bogged down|bogged down|buckles under|collapses under
deadly dull|deadly serious|terminal illness of|heavy sledding|glacial pace|snail's pace
in slow motion|embarrassment to|exercise in tedium|never mind the|filmmaking by committee
""")
_phr(-1.75, """
not great|not a great|not the best|not perfect|far from perfect|less than perfect
no masterpiece|not a masterpiece|not exactly|no classic|not a classic|does not always work
has its share of problems|not without flaws|has its faults|has its flaws|not without problems
only occasionally|only intermittently|only sporadically|only fitfully|mildly amusing
mildly entertaining|mildly diverting|marginally entertaining|moderately funny|all too often
only marginally|only mildly|at best|at its weakest|at worst|for the most part not
at a loss|without much|there is not much|left wanting|left wondering|leaves me wondering
leaves you wondering|left scratching|scratch your head|scratching my head|never quite
only a few|less than stellar|less than one|far less than|all surface|on the surface only
style over substance|style than substance|style and no substance|all style|all flash
not for everyone|not for everybody|acquired taste|can not decide|does not know whether
never decides|never sure|not sure what|not sure why|do not know why|lost on me
may not be for|may well be too|not my|not my idea|not everyone's|not much|
in search of a movie|in search of a plot|in need of|needs more|needed more|could use some
could have used|could use a|could do with|would have benefited|would have been nice
if only|if it had|if it were only|if only it|would have liked|i wish|one wishes
so little|precious little|very little|very few|so few|not a lot of|too often|too early
for its own good|worse still|worse yet|even worse|worse than|less successful|not quite as
not nearly as|nowhere near|not as much|a bit much|bit too|little too
not helped by|despite the best|despite the efforts|not really sure|bears little
loses points|fails on|is the problem|the problem is|the trouble is|problem with
does not help|no help|too seriously|takes itself too|take itself too|self serious
self important|self indulgent|self indulgence|self satisfied|self satisfaction
self congratulatory|self conscious|navel gazing|navel gazer|one sided|by rote
half baked|half hearted|half formed|half finished|half assed|half cocked|half measures
ill advised|ill conceived|ill served|ill suited|ill defined|ill at ease
bad taste in|sour taste|soap opera|after school special|laugh track|potty humor
toilet humor|bathroom humor|body fluids|body fluid|fart jokes|gross out
going nowhere|on autopilot|on automatic pilot|running on empty|left over|left out
at arm's length|at a distance|kept at a distance|nothing approaching
too cute|played out|dried up|worn out|long in the tooth|in the first place
all wrong|did not need|no need for|trying to be|tries to be|ought to have|could have made
just another|just one more|just a bunch|just so much|merely a|just going through
all dressed up|does not even|can not even|no amount of|you have to wonder
""")
_phr(0.0, """
not only|not just|not simply|not merely|not necessarily|not so much a|not so much an
not so much the|whether or not|like it or not|believe it or not|if not more
not to mention|not unlike|not unlike a|not long ago|not since|not least|not least because
never before|never before seen|never say never|never seen before|no longer|no dialogue
no doubt|without a doubt|no doubt about|there is no denying|can not deny|no matter how
no matter what|no matter who|no matter which|no matter where|like no other|no less than
no one else|no sooner|no stranger to|for no other reason|nothing if not|nothing short of
nothing less than|nothing but|anything but ordinary|anything but dull|none other than
all but|all the more|not all that often|more often than not|not to say|that is not to say
as well as|may well|might well|could well|well before|all too real|all too human
too many to|too good to be true|none too soon|none the less|not a little
fall in love|falls in love|fell in love with her|love affair|in love with|love story
hate crime|bad guys|bad guy|bad boy|bad boys|bad girl|bad girls|bad cop|bad seed
bad taste comedy|big bad|evil dead|dead man|dead end job|end of the world|good guy
good guys|good cop|good boy|good girl|best friend|best friends|best man|best known
better known|better half|worst enemy|worst nightmare|good and evil|good vs evil
poor little|poor old|poor man|poor woman|poor kid|poor boy|poor girl
human suffering|human rights|social problems|learning to love|special effects
lost love|lost souls|cold war|world war|civil war|sweet home alabama|bad company
high school|high tech|not rated|do not ask|who knows|in fact|but also|but rather
on the other hand|a little bit|all sorts of|kind of a|goes to show
""")
_phr(0.35, """
well intentioned|good intentions|best intentions|good looking|big budget|low budget
old fashioned|old school|well meaning|saving the world|in the right place|over the top
out of this world|larger than life|happy ending|happy endings|hard to imagine|so bad it is good
""")
_phr(2.05, "anything but dull|anything but ordinary|not at all bad|not at all boring|never feels forced|no easy feat|no small feat|not an easy feat|no mean feat")
_phr(-2.1, "worse|worst case|loses its appeal|not make you care|a far cry from|odd man out|dopey eyed|put you to sleep")
_phr(1.75, "old fashioned storytelling|well used|human scale|a keeper|aging well|a real find|the real thing|never flags|in full flower|made my day")
_phr(0.0, "if nothing else|if nothing more|even more|most of all|few and far between them|a no brainer")
_PH = {k: sorted(d.items(), key=lambda item: -len(item[0])) for k, d in _PH.items()}

# Patterns for productive constructions which cannot be handled by inflecting
# the terms of a dictionary.
_RX = []


def _rx(value, s):
    for line in s.strip().splitlines():
        line = line.strip()
        if line:
            _RX.append((re.compile(r"(?<!\S)(?:" + line + r")(?!\S)"), value))


_rx(-3.7, r"""
(?:a |another )?(?:total |complete |colossal |unforgivable |criminal |monumental )?waste of (?:good |great |considerable |perfectly good |the |your |my |our )?(?:actors|talent|talents|celluloid|money|time|effort|film)
(?:nothing|little|not (?:a lot|much)) (?:here |there |else |much )?to (?:admire|recommend|enjoy|love|like|praise|savor)
(?:has|have|offers|with) (?:next to |almost |virtually )?nothing (?:new |fresh |interesting |original |worthwhile )?to (?:say|offer|contribute)
(?:worst|lamest|dumbest|dullest|stupidest|most (?:boring|painful|pointless|tedious)) (?:[a-z]+ ){0,2}(?:movies?|films?|pictures?|comedies|sequels)
(?:not|hardly|scarcely|barely) worth (?:even |the |a |your |my |our |any )?(?:effort|hassle|time|price|money|look|seeing|watching|bother|while)
(?:does|is|has|offers|contains|brings) (?:absolutely |almost |virtually |precious )?nothing (?:of (?:interest|value|note)|new|fresh|original|special)
(?:you|we|i) (?:would |will )?be better off
(?:save|spare) (?:yourself|yourselves|us) (?:the |a )?(?:money|time|trouble|agony|ordeal|pain)
(?:give|get|want) (?:me |my |those |the |two |these |\d+ ){1,4}(?:hours?|minutes?) back
(?:more|about as much) fun (?:watching|to watch) (?:paint|grass)
(?:as (?:interesting|entertaining|exciting|fun|much fun|thrilling)) as (?:watching paint|watching grass|a root canal|root canal|a trip to the dentist)
(?:asleep|walked out) (?:halfway|half way|during|in the middle)
(?:could not|can not|could barely) (?:wait for (?:it|this|the movie|the film) to end|keep my eyes open|stand (?:it|this film))
(?:no|not a single|not one) (?:genuine |real |good |honest )?(?:laugh|reason to watch|reason to see|redeeming feature)
""")
_rx(-2.65, r"""
(?:one|the only|its only|the sole) (?:really |remotely )?(?:good|funny|interesting|enjoyable|worthwhile|redeeming) (?:bit|thing|part|moment|scene|aspect|feature)
(?:despite|with) (?:all |only )?(?:the |its |their |his |her )?best (?:intentions|efforts)
(?:not|never|hardly) (?:quite |nearly |remotely |even |half )?(?:as (?:funny|good|great|entertaining|exciting|involving|interesting|moving|smart|successful|clever)|good enough|funny enough|interesting enough)
(?:are|is|has) (?:too |so )?(?:few|little) (?:and far between|to (?:offer|say|recommend))
(?:laughs|pleasures|rewards|good bits|good moments|highlights) (?:[a-z]+ ){0,3}few and far between
few (?:precious |genuine |hearty |honest |real |good |easy |decent )?(?:laughs|rewards|pleasures|thrills|surprises|scares)
(?:more|much) (?:[a-z]+ ){0,2}(?:than (?:it|you|anyone|anybody|we) (?:needs?|wants?|can stand|could want))
(?:barely|hardly|never|fails? to|can not) (?:even |quite )?(?:register|sustain|rise above|generate|come to life|get started|hold (?:my|your|our) (?:interest|attention))
(?:is|becomes|feels|plays) (?:an? |like a )?(?:real |total |complete )?(?:chore|bore|drag|slog|misfire|dud|stinker|letdown)
(?:plays|looks|feels) like (?:a |an |some )?(?:bad|poor|long|extended|overlong|overextended|second rate|third rate|made for tv|tv movie|sitcom)
(?:little|nothing|not much|less) more than (?:just |a |an )?
(?:fail(?:s|ed)?|struggl(?:es|ed)|unable|inability) to (?:deliver|entertain|engage|excite|amuse|convince|connect|evoke|elicit|satisfy|generate|achieve)
(?:lacks?|lacking|without|no|devoid of|deprived of) (?:any |much |real |the |even |a |single |genuine ){0,3}(?:appeal|depth|substance|heart|humanity|insight|wit|wits|humou?r|charm|focus|purpose|laughs|thrills|surprises|warmth|fun|originality|conviction|feeling|coherence|sense|direction|chemistry)
(?:has|have|shows|offers) (?:precious |very |too )?little (?:of (?:the|that) )?(?:energy|charm|humou?r|appeal|wit|purpose|to offer|to say|else|insight|tension|interest)
(?:displays?|exhibits?|shows?) (?:no|little|scant) (?:[a-z]+ ){0,2}(?:sense|interest|talent|imagination|flair|ability)
(?:could|should|would|might) have been (?:a |an |much |so much |so |far |even |considerably ){0,3}(?:better|great|good|terrific|interesting|fun|successful|enjoyable|exciting|effective|funny)
(?:might|could|would|should) have made (?:a |an |for a |for an )?(?:better|good|great|decent|interesting|fine|terrific)
(?:could|would|should) (?:have been|be) (?:a lot |so much |much |considerably |far )better
(?:is|was|seems) (?:much |far |a lot )?less (?:interesting|enjoyable|effective|entertaining|exciting|satisfying|engaging|successful)
(?:not|never) (?:very |particularly |terribly |all that |remotely |especially |even )?(?:funny|interesting|enjoyable|entertaining|convincing|good|involving|effective|exciting|engaging|satisfying|compelling)
(?:too|so) (?:[a-z]+ ){1,2}(?:to be (?:funny|entertaining|fun|good|true|effective|believable|interesting)|for (?:its|his|her|their) own good)
(?:thinks|believes|pretends) (?:that |itself )?(?:it is |to be )?(?:clever|smart|funny|witty|hip|profound|deep)
(?:not|never) (?:half |nearly )?as (?:clever|smart|funny|witty|hip|profound|deep|good)
(?:leaves?|left) (?:me|us|one|viewers?|the audience|you) (?:feeling )?(?:cold|bored|empty|numb|exhausted|indifferent|wondering why|unmoved|unsatisfied|unmoved|frustrated)
(?:no|little) (?:discernible |apparent )?(?:rhyme|reason|point|plot|coherence|purpose)
(?:wears?|wore) (?:a (?:little|bit) |awfully |really |very )?(?:thin|out (?:its|the) welcome)
(?:missed|wasted|loses|squanders?) (?:a |an |the |every |its |his |her |their |great |good |golden ){1,3}(?:chance|opportunity|potential)
(?:cannot|could not|can not|did not|do not) (?:really |honestly |in good conscience )?recommend
(?:strains?|stretches?) (?:the (?:bounds|limits) of )?(?:credulity|credibility|believability)
(?:no|not a|hardly a) (?:patch on|match for|substitute for)
(?:a|the) (?:poor|weak|bad|pale|lame|second rate) (?:substitute|copy|imitation|attempt|excuse|knock off)
(?:more fun|better|more interesting|more entertaining) (?:than|to (?:watch|see) than) (?:this|the movie|the film)
""")
_rx(3.35, r"""
(?:one of|among) (?:the |this |my |our |his |her |its |their |year is |year |s |very ){0,5}(?:best|greatest|funniest|finest|smartest|strongest|loveliest|most (?:enjoyable|entertaining|moving|original|memorable|beautiful|compelling|affecting|satisfying|inventive|exciting))
(?:the|a) (?:[a-z]+ ){0,1}(?:best|funniest|finest|greatest) (?:[a-z]+ ){0,2}(?:film|movie|comedy|picture|thriller|work|performance|ever)
(?:breathes?|infuses?|injects?) (?:it |them |the [a-z]+ )?(?:with )?(?:some |much needed |fresh |new )?(?:life|vitality)
(?:is|was|comes as|proves to be) (?:a |an )?(?:very |most |particularly |really )?(?:pleasant|welcome|delightful|unexpected|wonderful|marvelous|nice) surprise
(?:leaves?|left) (?:me|us|one|the viewer|viewers?|the audience|you) (?:feeling )?(?:moved|stunned|breathless|shaken|wanting more|thinking|exhilarated|satisfied|smiling)
(?:keeps?|kept) (?:me|us|one|the viewer|viewers?|the audience|you) (?:guessing|laughing|on edge|on the edge|absorbed|engaged|riveted|interested|in suspense|watching)
(?:a|offers|provides) (?:[a-z]+ ){0,2}(?:feast for the (?:eyes|senses)|tour de force)
(?:worth|repays?|rewards?) (?:every |the |a |your |our |my )?(?:visit|effort|wait|time|watch|viewing|admission|ticket|price of admission)
(?:makes?|made) (?:me|you|us|one) (?:laugh|smile|cry|think|want to see)
(?:can not|could not|will not|never) (?:quite |soon |easily )?(?:forget|take (?:my|your|our) eyes (?:off|away))
(?:can not|could not|will not) (?:help|resist) (?:but )?(?:lov(?:e|ing)|lik(?:e|ing)|enjoy(?:ing)?|admir(?:e|ing)|smil(?:e|ing)|laugh(?:ing)?)
(?:well|more than) worth (?:a |the |your )?(?:ticket|price|admission|trip|time|watch|look|effort)
(?:will|should|ought to) (?:please|delight|satisfy|thrill|entertain|captivate|entrance|enchant|appeal to)
(?:without|never|not) (?:a (?:single )?|one )?(?:dull moment|false note|wasted moment)
(?:packed|filled|brimming|brims|bristles|bursting|bursts|alive|shines) with (?:[a-z]+ ){0,2}(?:energy|life|charm|humou?r|wit|ideas|intelligence|insights|passion|vitality|fun|feeling)
(?:do not|never|does not|without) (?:ever |once )?(?:disappoint(?:ing)?|condescend(?:ing)?|preach(?:ing)?|flag(?:ging)?|pander(?:ing)?|resort(?:ing)? to)
""")
_rx(2.0, r"""
(?:better|funnier|more (?:interesting|fun|entertaining|exciting|original)) than (?:you|one|i|we|most|it has any right|it should|expected)
(?:no|not a) (?:small|mean|easy) (?:feat|achievement|task|accomplishment)
(?:never|not) (?:quite |really |even |once )?(?:boring|dull|predictable|uninteresting|tedious|forced|a bore)
(?:avoids?|sidesteps?|transcends?|overcomes?|surmounts?) (?:the |most |its |all |many |those ){0,3}(?:flaws|pitfalls|problems|cliches|limitations|traps|conventions|shortcomings)
(?:never|without) (?:ever |once )?(?:fall(?:ing|s)?|lapse?s?|lapsing|stoop(?:ing|s)?) (?:in)?to
(?:will|should) (?:find|have) (?:its|a|an appreciative|a receptive) audience
(?:plenty|lots|a (?:great deal|lot)) (?:here |there )?(?:of |to )?(?:laughs|fun|charm|energy|heart|like|recommend|enjoy|admire)
(?:enough|sufficient) (?:[a-z]+ ){0,2}to (?:satisfy|entertain|engage|overcome|please|compensate)
(?:rises?|rising) (?:well )?above (?:the|its|their|his|her)
""")

_CLAUSE = {".", "!", "?", ";", ":", "—", "..."}
_STOP = _CLAUSE | {",", "(", ")", "but", "yet", "however", "although", "though", "whereas",
                   "despite", "because", "which", "who", "whose", "where", "when", "than",
                   "instead", "nevertheless", "nonetheless", "and"}
_NEG = set("""not never neither nor no nothing nobody nowhere without hardly scarcely barely
rarely seldom hardly lacking lacks lack lacked devoid bereft missing absent minus prevents
prevent preventable avoids avoid avoiding avoided eschews eschew eschewing resists resist
fails fail failed failing unable inability refuses refuse refused refuses omits
stops short insufficient insufficiently less least little few zero nada ningun ninguna sin
jamais sans keineswegs nicht kaum""".split())
_NEG_WEAK = {"seldom", "rarely", "scarcely", "barely", "hardly", "few", "little", "less", "least"}
_NEG_VERBS = {"avoid", "avoids", "avoiding", "avoided", "eschew", "eschews", "eschewing",
              "resists", "resist", "refuse", "refuses", "refused"}
_NEG.discard("stops")
_NEG.discard("short")
_BOOST = set("""very really highly truly so thoroughly extremely exceedingly astonishingly
utterly absolutely incredibly remarkably exceptionally enormously immensely extraordinarily
particularly quite deeply supremely sublimely entirely wholly totally marvelously hugely
intensely genuinely most pure sheer downright damned damn wonderfully wildly painfully
criminally ridiculously hopelessly desperately terribly woefully disgustingly profoundly
hugely surprisingly especially consistently undeniably fiercely tremendously amazingly
completely distinctly unusually much far considerably vastly even plenty""".split())
_DIM = set("""somewhat rather slightly mildly marginally fitfully intermittently occasionally
vaguely sporadically modestly passably reasonably fairly faintly moderately potentially
relatively remotely briefly doubly-not unevenly""".split())

_IRREG = {
    "better": 1.9, "best": 2.9, "worse": -2.8, "worst": -4.1,
    "won": 1.0, "wonkiness": -.5, "nice": 1.95, "nicely": 2.0,
    "greatness": 2.8, "grandeur": 2.0, "euphoria": 2.6, "wonder": 1.1,
    "patience": -.1, "pathetic": -3.35, "distinction": 1.2, "neither": 0,
    "truly": 0, "happiness": 1.8, "happy": 1.65, "happier": 1.75,
    "renown": 1.7, "renowned": 2, "excellence": 3.1, "oversimplification": -2,
    "triumphantly": 3, "wondrously": 2.8, "swimmingly": 2.5,
    "artificiality": -2.4, "competency": 1.45, "cuteness": .3,
    "blunt": -.3, "hard": 0, "moral": .3, "morals": .2, "morale": 0,
    "worthier": 2, "dread": -.2, "dreadfully": -1.5, "daringly": 2.1,
    "horror": 0, "classic": 2.6, "classics": 2.1, "song": 0,
    "winningly": 2.5, "top": .9, "tops": 1.1, "wondering": -.15,
    "wonders": .25, "colossal": -.1, "uneasy": .1, "wicked": .9,
    "bloody": -.1, "prettier": 1.5, "should": 0, "right": .45, "wrong": -1.65,
    "sustain": .35, "sustains": 1.0, "touch": .45, "touches": .55,
    "important": 1.7, "importance": 1.1, "relevant": 1.75, "painless": 1.5,
    "open": .05, "liking": 1.4, "strangely": 0, "harder": -.35, "cried": .5,
    "humor": 1.4, "humour": 1.4, "comic": .5, "loving": 1.35, "love": .95,
    "touchy": -.25, "surprises": 1.85, "unsettles": 1.2,
    "fatal": -1.0, "deadly": -.8, "survival": 0, "romance": .1,
    "darkness": .1, "darkest": .15, "hope": .5, "hopes": .25,
    "redemption": 1.0, "daring": 2.0, "intoxicating": 2.8,
    "filmed": 0, "youngest": 0, "tears": .5, "borrows": -.8, "borrowed": -.95,
    "unlike": 0, "unlikeable": -2.2, "likely": 0, "like": 0, "pretty": .95,
    "ridiculously": -1.0, "keeps": .15, "likes": .95, "scare": .9, "moments": .25,
    "wrongheaded": -2.4, "sick": -.55, "sickly": -1.5, "sicker": -.8,
    "warmer": 1.8, "miss": -.65, "missed": -1.65, "misses": -1.65,
    "sucker": -.4, "suited": 1.2, "falls": -.3, "fall": 0, "fallen": -.15,
    "animated": .2, "dramatically": .15, "reel": 0, "reels": 0, "brother": 0,
    "thinner": -1.4, "angel": .1, "anguish": -.25, "funniest": 3.1,
    "half": 0, "mean": 0, "means": 0, "treats": .4, "treatment": .1,
    "bent": 0, "tenser": 1.6, "funnily": 1, "originally": 0,
    "adaptation": 0, "missy": 0, "interest": 1.0, "interested": 1.2,
    "seems": 0, "successfully": 2.6, "benefit": 1.1, "benefits": 1.4,
    "execution": .1, "recommendation": 2.1, "unfavorably": -2.3,
    "favorably": 2.1, "favorable": 2.3, "unfavorable": -2.3,
    "badness": -2.6, "goodness": 1.6, "no": 0, "laughter": 2.1,
    "acute": 1.45, "master": 2.25, "masters": 1.65, "mint": .1,
    "deserves": .9, "deserved": .45, "sharp": 2.0, "sharper": 2.1,
    "sharply": 1.4, "fury": 0, "dragged": -2.15, "daringness": 2.1,
    "credits": 0, "fairly": 0, "extreme": -.2, "sadly": -1.2,
    "further": 0, "fewer": -.5, "drive": .25, "driven": .75
}
_WORD.update(_IRREG)


@lru_cache(maxsize=12000)
def _lex(w):
    if w in _WORD:
        return _WORD[w]
    if len(w) < 4 or not w.isalpha():
        return 0.
    cand = []
    if w.endswith("ies") or w.endswith("ied"):
        cand.append(w[:-3] + "y")
    for suf in ("ing", "ed", "est", "er"):
        if w.endswith(suf):
            b = w[:-len(suf)]
            cand.extend((b, b + "e"))
            if len(b) > 2 and b[-1] == b[-2]:
                cand.append(b[:-1])
            if b.endswith("i"):
                cand.append(b[:-1] + "y")
    if w.endswith("s"):
        cand.append(w[:-1])
        if w.endswith("es"):
            cand.append(w[:-2])
    if w.endswith("ly"):
        b = w[:-2]
        cand.extend((b, b + "e", w[:-1] + "e"))
        if b.endswith("i"):
            cand.append(b[:-1] + "y")
        if b.endswith("al"):
            cand.append(b[:-2])
    if w.endswith("ness"):
        cand.append(w[:-4])
        if w.endswith("iness"):
            cand.append(w[:-5] + "y")
    if w.endswith("ingly"):
        cand.extend((w[:-2], w[:-5], w[:-5] + "e"))
    if w.endswith("ity"):
        cand.extend((w[:-3], w[:-3] + "e"))
    for x in cand:
        if x in _WORD:
            return _WORD[x] * .93
    for pref in ("un", "non", "dis", "in", "im", "ir"):
        if w.startswith(pref) and w[len(pref):] in _WORD:
            return -0.86 * _WORD[w[len(pref):]]
    if w.startswith("over") and len(w) >= 8 and w.endswith(("ed", "ing", "ity")):
        return -1.65
    if w.endswith("less") and _WORD.get(w[:-4], 0) > .7:
        return -2.15
    return 0.


def _events(t):
    n = len(t)
    spans = {}
    for i, w in enumerate(t):
        for p, v in _PH.get(w, ()):
            if t[i:i+len(p)] == p:
                spans[i] = (i + len(p), v)
                break
    text = " ".join(t)
    offsets = {}
    c = 0
    for i, w in enumerate(t):
        offsets[c] = i
        c += len(w) + 1
    offsets[c] = n
    for pattern, v in _RX:
        for m in pattern.finditer(text):
            i = offsets.get(m.start())
            j = offsets.get(m.end() + 1)
            if i is not None and j is not None and j > spans.get(i, (i, 0))[0]:
                spans[i] = (j, v)
    covered = set()
    ev = []
    i = 0
    while i < n:
        if i in spans:
            j, v = spans[i]
            if j > i + 1:
                covered.update(range(i, j))
        else:
            j = i + 1
            w = t[i]
            v = _lex(w)
            if w == "like" and i and t[i-1] in ("i", "we", "you", "not", "really", "will", "actually", "quite"):
                v = 2.
            if w in ("better", "best", "good") and t[j:j+1] in (("luck",), ("friends",), ("friend",)):
                v = .1
            if w in ("liked", "loved") and i and t[i-1] in ("would", "have") and "would" in t[max(0,i-4):i]:
                v = -.8
            if w == "love" and i and t[i-1] in ("i", "will", "absolutely", "really", "we"):
                v = 2.8
            if w == "well":
                if t[j:j+1] and t[j].endswith(("ed", "en")):
                    v = 1.9
                elif i and t[i-1] in ("works", "plays", "very", "quite", "extremely"):
                    v = 1.3
            if w in ("only", "solely", "merely", "just") and t[j:j+1] and t[j] in ("marginally", "mildly", "sporadically", "briefly"):
                v = -1.6
            if w == "pretty" and j < n and (_lex(t[j]) or t[j] in _BOOST):
                v = 0.
            if w == "much" and t[max(0,i-2):i] == ("not", "so"):
                v = 0.
            if w == "enough" and i and t[i-1] in ("entertaining", "engaging", "satisfying", "clever", "funny", "sweet"):
                v = .2
            if w == "fans" and "only" in t[max(0, i-3):i]:
                v = -1.0
            if w == "too" and (j < n and t[j].isalpha() and t[j] not in ("good", "funny", "bad", "is", "can", "has", "well", "does", "has", "have", "soon", "often", "will", "late")):
                v = -1.75
            if w in ("overly", "excessively", "wannabe"):
                v = -1.65
            if w == "should" and t[j:j+2] in (("have", "known"), ("be", "ashamed")):
                v = -2.4
            if w in _DIM and j < n and _lex(t[j]) != 0:
                v = 0.
            if w in _BOOST and j < n and abs(_lex(t[j])) >= .7:
                v = 0.
        if v:
            ev.append((i, j, v))
        i = j
    return ev, covered


def _importance(t, blocked):
    n = len(t)
    a = [1.] * n
    lo = 0
    for i, w in enumerate(t):
        if w in (".", "!", "?", ";"):
            lo = i+1
        if i in blocked:
            continue
        if w in ("but", "however", "yet", "nevertheless", "nonetheless", "unfortunately", "alas",
                 "thankfully", "ultimately", "instead", "still"):
            if w == "but" and (i and t[i-1] in ("anything", "all", "nothing", "everything", "help", "else")):
                continue
            if w == "yet" and (i == 0 and t[i+1:i+2] == ("another",) or i and t[i-1] not in _CLAUSE | {","}):
                continue
            if w == "still" and i and t[i-1] not in _CLAUSE | {",", "but"}:
                continue
            if w == "instead" and t[i+1:i+2] == ("of",):
                continue
            for k in range(lo, i):
                a[k] = max(.28, a[k] * (.54 if w in ("but", "however", "yet") else .76))
            for k in range(i, n):
                if t[k] in (".", "!", "?", ";"):
                    break
                a[k] = min(1.65, a[k] * 1.23)
        if w in ("despite", "although", "though", "while", "whereas", "albeit", "whereas") or (w == "spite" and i and t[i-1] == "in") or (w == "granted" and i == lo):
            if w == "while" and (i and t[i-1] in ("a", "the", "mean", "little", "long", "short", "your")):
                continue
            j = i + 1
            if t[j:j+1] == (",",) and w == "though":
                continue
            while j < n and t[j] not in _CLAUSE | {",", "but"}:
                a[j] *= .53 if w != "while" else .65
                j += 1
        if (w == "rather" or w == "more") and t[i+1:i+2] == ("than",):
            if w == "rather":
                j = i + 2
                while j < n and t[j] not in _STOP:
                    a[j] *= .38
                    j += 1
        if w == "than":
            # A rather than B; more A than B. B is the foil, not the verdict.
            prev = t[max(lo, i-10):i]
            if any(z in prev for z in ("more", "better", "worse", "rather", "funnier", "less")):
                for k in range(i+1, min(n, i+14)):
                    if t[k] in _CLAUSE | {",", "but"}:
                        break
                    a[k] *= .48
    return a


def _governs(t, k, i, blocked):
    w = t[k]
    if k in blocked:
        return False
    if w == "but" and k and t[k-1] == "anything":
        return True
    if w not in _NEG:
        return False
    if w in ("few", "little"):
        if k and t[k-1] in ("a", "every", "this", "that", "his", "her", "my", "these", "those", "our", "what"):
            return False
        if t[k+1:k+2] in (("by",), ("girl",), ("boy",), ("kid",), ("man",), ("woman",), ("film",), ("movie",), ("time",)):
            return False
    if w == "less" and t[k+1:k+2] == ("than",) and i-k > 3:
        return False
    if w == "never" and t[k+1:k+2] in (("before",), ("again",)):
        return False
    if w == "missing" and t[k+1:k+2] in (("child",), ("person",), ("girl",), ("boy",)):
        return False
    if w in ("refuse", "refuses", "refused", "fail", "fails", "failed", "failing") and "to" not in t[k+1:i]:
        return False
    if w == "no" and t[k+1:k+2] in (("one",), ("matter",), ("doubt",)):
        return False
    if w == "least" and (k == 0 or t[k-1] != "the"):
        return False
    return True


def _rating(text):
    # Interpret explicit numerical grades but not dates or aspect ratios.
    text = text.lower()
    m = re.search(r"(?<![\d./])(\d+(?:\.\d+)?)\s*(?:/\s*|(?:stars?\s+)?out of\s+)(4|5|10|100)\b(?!\s*/)", text)
    if m:
        x, y = float(m[1]), int(m[2])
        if x <= y:
            return 4.8 if x/y >= .61 else -3.6 if x/y <= .5 else .4
    if re.search(r"\b(?:half a star|one star|zero stars|no stars)\b", text):
        return -3.3
    return 0.


def predict(state):
    t = tuple(_tokens(state))
    n = len(t)
    ev, blocked = _events(t)
    weight = _importance(t, blocked)
    usedneg = set()
    score = _rating(state)
    for i, j, v in ev:
        l = max(0, i-7)
        k = i-1
        neg = []
        while k >= l:
            if _governs(t, k, i, blocked):
                if i-k <= 5 or t[k] in ("not", "neither", "without", "no", "never", "anything", "lack", "lacks"):
                    neg.append(k)
            if t[k] in _STOP:
                break
            if i-k >= 2 and t[k] in ("is", "was", "are", "were") and t[k-1:k] in (("it",), ("film",), ("movie",), ("story",)):
                break
            k -= 1
        k = max(k+1, 0)
        left = t[k:i]
        ls = " ".join(left)
        mult = 1.
        if neg:
            usedneg.update(neg)
            # neither ... nor is a single negation, as is a concordant
            # 'not ... nor'. Other paired reversals can cancel each other.
            if len(neg) % 2 or t[neg[0]] == "nor":
                v *= -.84 if v >= 0 else -.75
        if i and t[i-1] in _BOOST:
            mult *= 1.34
        elif i >= 2 and t[i-2] in _BOOST and t[i-1] in ("a", "an", "very", "quite"):
            mult *= 1.22
        if i and t[i-1] in _DIM:
            mult *= .49
        if i and t[i-1] in ("occasional", "minor", "small", "slight", "isolated", "potential"):
            mult *= .57
        if t[max(0,i-2):i] in (("a", "bit"), ("a", "little"), ("sort", "of"), ("kind", "of")):
            mult *= .66
        if v > 0 and i and t[i-1] == "too" and t[i] not in ("good", "funny", "well", "much", "bad", "little", "often", "many"):
            v *= -.53
        # Praise of a hypothetical film, or of filmmakers' aspirations, is
        # not necessarily praise of what reached the screen.
        if not neg:
            if re.search(r"(?:could|should|would|might) have (?:been|made|used|had|provided|offered|given)(?: |$)", ls):
                v *= -.71 if v > 0 else -.34
            elif re.search(r"(?:tries|trying|attempts|attempting|wants|wanted|strives|struggles|aspires|pretends|pretending|aiming) to (?:be|make|seem|appear|look|sound|become)(?: |$)|(?:supposed|meant|intended) to be(?: |$)", ls):
                if v > 0:
                    v *= -.44
            elif re.search(r"(?:should|could|might) be (?:much |so much |far )?$", ls + " ") and v > 0:
                v *= -.38
            if v > 0 and (re.search(r"(?:needs?|needed|lacks?|lacked|missing|wishing for|wish for|instead of|rather than) (?:a |the |any |some |more |much |bit |of |real |genuine )*$", ls+" ")):
                v *= -.74
            if v > 0 and "to be" in ls and "hard" in left and "tries" in left:
                v *= -.7
        if v > 0 and j < n and t[j:j+3] in (("it", "is", "not"), ("this", "is", "not")):
            v = -v
        if t[j:j+2] == ("or", "not"):
            mult *= .4
        score += v * mult * weight[i]

    for k, w in enumerate(t):
        if k in blocked or k in usedneg:
            continue
        if w in ("not", "never", "no", "nothing", "neither", "barely", "hardly", "without", "rarely", "scarcely", "little", "few"):
            if not _governs(t, k, min(k+2, n), blocked):
                continue
            if w == "not" and t[k+1:k+2] in (("want",), ("forget",), ("stop",)):
                continue
            if w == "never" and t[k+1:k+2] in (("seen",), ("forget",), ("seen",), ("know",)):
                continue
            score -= weight[k] * (.75 if w in ("not", "nothing", "neither", "hardly") else .48)
        if w == "only" and t[k+1:k+2] in (("for",), ("fans",), ("diehard",), ("die",)):
            score -= 1.65 * weight[k]
    # Subtle pragmatic cues for pieces without an explicit evaluation.
    s = " ".join(t)
    if re.search(r"\b(?:why (?:did|do|does|would|should|bother|make)|who (?:asked|wanted|needs|cares)|what (?:was|is) the point|is (?:this|that) (?:really|supposed to be)|do we really|what on earth)\b", s):
        score -= 1.9
    if re.search(r"\b(?:fans of|lovers of|anyone (?:interested in|who (?:loves|enjoys)))\b", s) and "only" not in t and "except" not in t:
        score += .57
    if re.search(r"\b(?:if (?:only|you must|you insist)|another in a (?:long|seemingly)|on and on|at least it is short|what went wrong|how (?:did|could) .* go wrong)\b", s):
        score -= 1.85
    if re.search(r"\b(?:too \w+ (?:and too \w+ )?to|why .* was made|as if .* not bad enough|would rather have|the best (?:part|thing) .* (?:credits|when it ends))\b", s):
        score -= 1.55
    if re.search(r"\b(?:not (?:only|just) .* but|from (?:start to finish|beginning to end)|for years to come|does what it sets out to do)\b", s):
        score += .58
    if abs(score) < .62:
        if re.search(r"\b(?:like a|as if|as though|so much for|you would think|you would expect|you have to ask|anybody really|must have been|sit through|left over|remake of a|an excuse|at least|do we|another)\b", s):
            score -= .65
        elif re.search(r"\b(?:about (?:the|what|how|life)|takes us|shows us|lets us|reminds us|reminds you|a look (?:at|inside)|study of|portrait of|captures|puts you|an experience|at once|will find|comes from|brings us|reflects|transports|makes us|allows us|invites|gives us)\b", s):
            score += .8
        elif "?" in t:
            score -= .45
    return {"answer": "positive" if score >= 0 else "negative"}
