import re
import unicodedata
import math

_WORDS = {}


def _words(score, text):
    for word in text.split():
        _WORDS[word] = float(score)


_words(3.5, """
masterpiece masterwork magnificent phenomenal extraordinary sublime transcendent
""")
_words(3.1, """
excellent wonderful fantastic fabulous marvelous marvellous superb outstanding
exceptional splendid amazing awesome brilliant terrific terrific
""")
_words(2.7, """
delightful hilarious riveting mesmerizing spellbinding enthralling captivating
exhilarating unforgettable irresistible triumphant breathtaking dazzling
""")
_words(2.4, """
great beautiful gorgeous remarkable impressive entertaining enjoyable satisfying
rewarding compelling engrossing absorbing gripping thrilling moving touching
affecting poignant heartwarming uplifting inspiring inspired inventive ingenious
refreshing charming endearing lovable loveable exquisite magnificent
""")
_words(2.1, """
good delightful effective engaging amusing exciting fascinating interesting
powerful stirring rousing heartfelt thoughtful insightful intelligent witty
creative imaginative accomplished masterful assured confident deft skillful
skilful polished elegant graceful vibrant vivid lively energetic spirited
convincing persuasive resonant haunting memorable appealing likable likeable
charismatic adorable meaningful substantial nuanced sophisticated accomplished
""")
_words(1.7, """
fun clever smart fresh original subtle rich sensitive humane compassionate
honest authentic believable sincere genuine warm tender perceptive astute
provocative daring bold audacious innovative unpredictable playful droll wry
stylish artful artistic lyrical poetic atmospheric evocative expressive
exuberant buoyant breezy snappy infectious potent strong solid pleasing
pleasurable pleasant graceful tasteful mature naturalistic realistic
unpretentious unsentimental understated unforced unflinching uncompromising
watchable worthwhile worthy satisfying successful
""")
_words(1.3, """
fine nice decent competent capable able admirable commendable courageous brave
ambitious intriguing surprising unusual distinctive unique eccentric quirky
offbeat nimble brisk crisp efficient economical economical modest unassuming
intimate delicate intricate complex layered textured romantic sweet warm
gentle lighthearted jaunty sprightly rollicking zesty zippy punchy punchier
energetic alive vital sincere accessible involving immersive transporting
enlightening illuminating educational informative revealing relevant timely
important necessary welcome refreshing appealing
""")
_words(0.8, """
adequate serviceable passable acceptable tolerable okay ok fair agreeable
promising interesting respectable amusing amusingly enjoyable nicely
tense suspenseful spooky scary frightening unsettling disturbing harrowing
bittersweet heartbreaking wrenching melancholy wistful
""")
_words(0.4, """
ambition potential promise goofy weird unusual unexpected bizarre odd
familiar earnest sincerity simplicity realism complexity humanity
""")

_words(3.2, """
gem treasure triumph delight joy perfection genius excellence brilliance
""")
_words(2.5, """
love loved loves loving adore adored adores adoring enjoy enjoyed enjoys
enjoying recommend recommended recommends
""")
_words(2.0, """
enjoyment entertainment laughter laughs laugh chuckles chuckle wit charm
charms affection warmth beauty elegance artistry craftsmanship imagination
creativity inventiveness originality ingenuity insight insights intelligence
sensitivity compassion empathy poignancy resonance vitality exuberance
""")
_words(1.5, """
satisfaction achievement accomplishment success succeeds succeed succeeded
succeeding works excel excels excelled excels impress impresses impressed
impressing amazes amazed amazement delights delighted delighting thrills
thrilled thrill excitement exhilaration amuse amused amuses amusements
entertain entertains entertained engage engages engaged engagingly
captivate captivates hypnotic hypnotizing mesmerizingly
""")
_words(1.0, """
depth nuance nuances texture honesty authenticity integrity sincerity dignity
affinity chemistry spirit energy heart soul humor humour emotion emotions
appeal pleasure pleasures strength strengths insight humanity intelligence
""")
_words(1.5, """
resonate resonates resonated admire admires admired applaud applauds applauded
appreciate appreciates appreciated appreciate appreciation
""")
_words(1.2, """
redeem redeems redeemed redeeming rescue rescues salvages
""")
_words(2.7, """
best finest superior classic
""")
_words(1.5, """
better stronger richer smarter sharper
""")
_words(2.0, """
funny humorous comical amusing enjoyable entertaining
""")
_words(2.2, """
talented gifted accomplished virtuosic virtuoso cinematic
""")
_words(1.4, """
skill skills talent talents professionalism restraint precision fluidity
""")
_words(1.7, """
lovely luscious lush sumptuous ravishing radiant luminous stunning spectacular
handsome photogenic picturesque beautiful
""")
_words(1.4, """
cool slick funky groovy hip neat nifty
""")
_words(2.8, """
rocks badass awesomeness
""")

_words(-3.6, """
abysmal atrocious execrable abominable horrendous
""")
_words(-3.1, """
awful terrible horrible horrid appalling dreadful wretched unwatchable
unbearable intolerable unendurable excruciating disastrous deplorable
""")
_words(-2.7, """
bad worst lousy pathetic pitiful miserable ghastly woeful inept incompetent
moronic idiotic asinine insulting infuriating obnoxious repugnant detestable
""")
_words(-2.4, """
boring tedious tiresome dull dreary monotonous unfunny laughless witless
disappointing underwhelming uninspired uninspiring uninteresting unengaging
unappealing unconvincing unbelievable pretentious pointless stupid vacuous
vapid insipid worthless useless joyless soulless lifeless listless inert
""")
_words(-2.0, """
poor weak flat bland banal trite cliched cliche formulaic derivative generic
predictable stale tired repetitive plodding ponderous turgid leaden sluggish
interminable overlong overblown overwrought overdone overstuffed overcooked
amateurish clumsy awkward clunky wooden stilted contrived forced artificial
phony fake shallow superficial hollow empty incoherent incomprehensible
confused confusing muddled disjointed unfocused scattershot haphazard
annoying irritating grating aggravating offensive tasteless repulsive
disgusting repellent unpleasant unlikable unlikeable unsympathetic smug
smarmy sanctimonious preachy condescending patronizing exploitative
manipulative mawkish sappy saccharine treacly schmaltzy syrupy syrupy
sententious pompous bombastic bombast ponderous
""")
_words(-1.6, """
forgettable disposable unnecessary needless redundant mediocre middling
underwhelmed underwhelms disappoint disappoints disappointed disappointing
strained implausible improbable implausibility illogical nonsensical
corny hokey hackneyed hackneyed familiar formulaic formula routine mechanical
pedestrian perfunctory unimaginative unoriginal unambitious unadventurous
inauthentic dishonest insincere unearned unmotivated unmotivating
unmoving uninvolving unemotional emotionless cold heartless humorless humourless
charmless graceless artless soulless uninspired
""")
_words(-1.3, """
slow sluggish slack uneven inconsistent patchy unevenness ungainly lumbering
bloated rambling meandering wandering shapeless aimless directionless
underwritten overwritten miscast misbegotten misguided misjudged miscalculated
overacted overacting underacting hammy hamfisted hamhanded heavyhanded
crass crude vulgar juvenile puerile immature infantile childish
sentimental sentimentality cutesy cute simplistic simplistic
cheap tacky tawdry trashy schlocky shoddy sloppy slipshod
wasteful wasted squanders squandered squandering
""")
_words(-0.8, """
silly dumb absurd ridiculous ridiculousness cynical grim bleak gloomy
drab murky muddy ugly harsh abrasive shrill loud noisy frantic frenetic
fussy excessive excess dated conventional ordinary standard derivative
foolish awkwardness obvious obviousness predictable predictability
overwrought overkill lightweight thin slight limited flawed flaws flaw
problems problem trouble troubling troublesome difficulty
""")
_words(-0.4, """
oddity oddities unevenness mixed minor small minimal familiar
""")
_words(-3.1, """
disaster travesty fiasco debacle catastrophe dreck drivel garbage rubbish crap
crappy bullshit shitty
""")
_words(-2.6, """
bore boredom bores bored torture torturous mess failure dud stink stinks stinker
sucks sucked suck sucky failure disappointment
""")
_words(-2.2, """
muddle muddles mishmash hodgepodge flop flops bomb botch botched bungled
bungles bungling mishandled misfire misfires misfired misfiring
trash junk schlock tripe slop crapola
""")
_words(-1.8, """
waste wastes wasting squander squanders drag drags dragged dragging
dullness tedium monotony repetition cliches cliche banality blandness
pretension pretensions pretentiousness ineptitude incompetence stupidity
idiocy inanity inanities incoherence confusion chaos laziness
""")
_words(-1.4, """
fails fail failed failing lacks lack lacking missing misspent
dislike disliked dislikes hate hated hates hating loathe loathed despise
despised detest detested cringe cringes cringeworthy cringey cringeinducing
irritates irritated annoy annoys annoyed frustrates frustrating frustrated
frustration disappointments
""")
_words(-2.8, """
hatred loathsome hateful contemptible
""")
_words(-2.0, """
worse inferior lesser secondrate thirdrate unworthy ineffectual ineffective
unrewarding unrewarded unfulfilling unsatisfying unsatisfactory unremarkable
unmemorable forgettable forgets forget
""")
_words(-1.0, """
letdown letdowns drawback drawbacks shortcomings shortcoming weakness weaknesses
fault faults failings failure disappointment
""")
_words(0.0, """
novel comedy drama thriller horror action violence murder death dead kill
killer killing evil villain villainous tragedy tragic sad sadness sorrow
fear terror pain loss grief suffering serious seriously dark darkness
""")

# These adjectives describe desired effects as often as undesirable ones.
_words(1.1, "terrifying chilling creepy eerie suspenseful tense nailbiting harrowing")
_words(1.6, "heartbreaking haunting moving affecting touching")
_words(0.0, "worked work like mean special positive negative pretty simply")
_words(-2.6, "disappointment failure")
_words(-2.1, "unbelievable")
_words(0.9, "ambitious quirky")
_words(-0.3, "sentimental")
_words(-1.8, "sentimentality")
_words(1.5, "charm wit")
_words(0.3, "heart soul")
_words(0.5, "emotion emotions humor humour")
_words(1.8, "cinematic")
_words(1.1, "cute")
_words(-1.2, "familiar")
_words(0.0, "small minor limited ordinary standard")


def _normalize(text):
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")
    text = text.replace("&amp;", " and ").replace("&quot;", '"')
    text = text.replace("&#39;", "'").replace("&apos;", "'")
    text = re.sub(r"<\s*br\s*/?\s*>", ". ", text, flags=re.I)
    text = re.sub(r"<[^>]*>", " ", text)
    text = text.lower()
    for symbol in ("😍", "🥰", "😊", "😀", "😃", "❤", "♥", "👍", "💖"):
        text = text.replace(symbol, " wonderful ")
    for symbol in ("😡", "😠", "🤮", "👎", "😞", "😒", "💩"):
        text = text.replace(symbol, " awful ")
    text = re.sub(r"[:;=]-?[)D]+", " delightful ", text)
    text = re.sub(r"[:=]-?\(+", " disappointing ", text)
    text = text.replace("won't", "will not").replace("can't", "can not")
    text = text.replace("shan't", "shall not").replace("ain't", "is not")
    text = re.sub(r"\bcannot\b", "can not", text)
    text = re.sub(r"n[' ]?t\b", " not", text) if "n't" in text else text
    contractions = {
        "dont": "do not", "doesnt": "does not", "didnt": "did not",
        "isnt": "is not", "wasnt": "was not", "werent": "were not",
        "arent": "are not", "havent": "have not", "hasnt": "has not",
        "hadnt": "had not", "couldnt": "could not",
        "wouldnt": "would not", "shouldnt": "should not",
        "cant": "can not", "wont": "will not",
    }
    text = re.sub(
        r"\b(?:dont|doesnt|didnt|isnt|wasnt|werent|arent|havent|hasnt|hadnt|couldnt|wouldnt|shouldnt|cant|wont)\b",
        lambda m: contractions[m.group(0)], text
    )
    text = re.sub(r"\b(it|that|there|here|he|she|what|who|how|where)'s\b",
                  r"\1 is", text)
    text = re.sub(r"'re\b", " are", text)
    text = re.sub(r"'ve\b", " have", text)
    text = re.sub(r"'ll\b", " will", text)
    text = re.sub(r"'d\b", " would", text)
    text = re.sub(r"'m\b", " am", text)
    text = re.sub(r"'s\b", " s", text)
    text = text.replace("n't", " not")
    text = "".join(c for c in unicodedata.normalize("NFD", text)
                   if unicodedata.category(c) != "Mn")
    text = re.sub(r"[-–—_/]+", " ", text)
    text = text.replace("…", ".")
    return re.findall(r"[a-z]+(?:'[a-z]+)?|\d+(?:\.\d+)?|[.!?,;:]", text)


_PHRASES = {}


def _phrases(score, text):
    for phrase in text.split("|"):
        tokens = tuple(_normalize(phrase.strip()))
        if tokens:
            _PHRASES[tokens] = float(score)


_phrases(3.5, """
one of the best|one of the year's best|one of the years best|
best film of the year|best movie of the year|a masterpiece|
a work of genius|a work of art|a cinematic triumph|an absolute delight|
a sheer delight|a total delight|pure cinematic pleasure|
a real gem|a little gem|an absolute gem|a rare gem|
laugh out loud funny|riotously funny|screamingly funny|
a must see|must see|must watch|essential viewing|required viewing|
not to be missed|not be missed|do not miss|must not miss
""")
_phrases(2.7, """
laugh out loud|laugh aloud|laugh riot|laugh a minute|non stop laughs|
very funny|very entertaining|very enjoyable|very moving|
wonderfully funny|wickedly funny|genuinely funny|genuinely moving|
genuinely touching|emotionally powerful|emotionally satisfying|
deeply moving|deeply affecting|deeply felt|deeply satisfying|
beautifully acted|beautifully made|beautifully directed|beautifully written|
beautifully filmed|beautifully shot|beautifully crafted|beautifully realized|
superbly acted|superbly made|superbly directed|superbly written|
brilliantly acted|brilliantly made|brilliantly directed|brilliantly written|
perfectly cast|impeccably cast|impeccably acted|a tour de force|
tour de force|top notch|first rate|top drawer|second to none|
edge of your seat|edge of the seat|pulse pounding|nail biting|
a breath of fresh air|breath of fresh air|a joy to watch|
a pleasure to watch|a delight to watch|a treat to watch|
a wonderful time|a great time|great fun|good clean fun|sheer fun|pure fun|
pure joy|pure delight|pure pleasure|pure entertainment|
worth every penny|worth the price of admission|worth the admission price|
worth the trip|worth your time|well worth seeing|well worth watching|
well worth a look|well worth the time|worth seeking out|
highly recommended|wholeheartedly recommend|enthusiastically recommend|
kicks ass|kick ass|knocks it out of the park|
hits all the right notes|gets everything right|does everything right|
as good as it gets|as good as they come
""")
_phrases(2.0, """
a good time|good time at the movies|a lot of fun|lots of fun|
much fun|plenty of fun|more fun|enormous fun|some fun|
good fun|silly fun|goofy fun|mindless fun|mindlessly entertaining|
unpretentious fun|unadulterated fun|guilty pleasure|guilty pleasures|
a hoot|a blast|a treat|a winner|a keeper|an enjoyable time|
well made|well acted|well directed|well written|well crafted|
well executed|well paced|well plotted|well observed|well told|
well staged|well cast|well performed|well conceived|well realized|
finely acted|finely tuned|finely crafted|finely observed|
expertly directed|expertly made|expertly crafted|expertly staged|
skillfully made|skillfully directed|skillfully crafted|
deftly handled|deftly directed|lovingly crafted|lovingly made|
sure footed|sure handed|sure footedly|sure handedly|
in good hands|in capable hands|inspired casting|perfect casting|
solid performances|strong performances|fine performances|
strong performance|fine performance|good performances|good performance|
good acting|great acting|excellent acting|terrific acting|
good direction|great direction|strong direction|
good storytelling|great storytelling|excellent storytelling|
a strong script|a good script|a great script|
plenty of laughs|lots of laughs|big laughs|real laughs|
some good laughs|a few good laughs|a few laughs|
a sense of wonder|sense of wonder|a sense of fun|
food for thought|thought provoking|thought provokingly|
an eye opener|eye opening|opens your eyes|
breaks new ground|break new ground|new ground|
something special|something wonderful|something worthwhile|
something to say|a lot to say|much to say|
ring true|rings true|feels true|feels real|feels authentic|
comes alive|come alive|brings to life|brought to life|
come to life|comes to life|spring to life|springs to life|
stands out|stand out|stands apart|stand apart|
stays with you|stay with you|sticks with you|stick with you|
gets under your skin|get under your skin|lingers in the mind|
packs a punch|pack a punch|packs an emotional punch|
pulls it off|pull it off|pulled it off|
hits the mark|hit the mark|hits its mark|hit its mark|
does justice|do justice|does it justice|
worth seeing|worth watching|worth a look|worth checking out|
worth the effort|worth the wait|worth a visit|worth a try|
worthwhile viewing|deserves to be seen|deserves an audience|
deserves a wider audience|deserves your attention|
thumbs up|two thumbs up|give it a chance|
it works|this works|that works|does work|
it delivers|this delivers|delivers the goods|delivers on its promise|
more than delivers|lives up to expectations|lives up to its promise|
lives up to the hype|exceeds expectations|exceeded expectations|
better than expected|better than i expected|better than you expect|
better than it sounds|better than it has any right to be|
surprisingly good|surprisingly effective|surprisingly entertaining|
pleasant surprise|pleasantly surprised|
a cut above|above average|above the average|above the norm|
heart in the right place|heart is in the right place|
has its heart in the right place|has a heart|
both funny and moving|funny and touching|
warm hearted|big hearted|light hearted|good natured|
good humored|good humoured|high spirited|
darkly funny|darkly comic|wickedly comic|wickedly amusing|
blackly funny|blackly comic|painfully funny|achingly funny|
painfully honest|brutally honest|brutal honesty|
emotionally honest|emotionally true|emotionally rich|
richly rewarding|richly entertaining|
off beat|ground breaking|groundbreaking|
visually stunning|visually dazzling|visually spectacular|
visually arresting|visually striking|visual feast|a feast for the eyes|
a feast for the senses|jaw dropping|breathtakingly beautiful
""")
_phrases(1.1, """
has its moments|have their moments|has moments|moments of brilliance|
moments of beauty|moments of grace|moments of humor|
moments of humour|moments of genuine|has its pleasures|
some charm|considerable charm|considerable wit|
some appeal|some laughs|several laughs|
easy to watch|easy viewing|easy on the eyes|
beautiful to look at|nice to look at|pretty to look at|
pleasing to the eye|good to look at|lovely to look at|
eye candy|visual candy|beautiful images|
for what it is|for all its flaws|flaws and all|warts and all|
not half bad|not so bad|not too bad|not that bad|
not at all bad|none too shabby|not too shabby|
could do worse|you could do worse|
more than adequate|more than competent|more than passable|
perfectly fine|perfectly good|perfectly enjoyable|
perfectly acceptable|perfectly serviceable|
reasonably entertaining|reasonably enjoyable|
works well|works nicely|works surprisingly well|
worthwhile effort|worthy effort|solid effort|
a step forward|a step in the right direction|
on the right track|up to the task|
gives it life|gives it heart|with heart|
a human touch|human touch|down to earth|
a labor of love|a labour of love|labor of love|labour of love|
love letter|a love letter|
old fashioned entertainment|old fashioned fun|
old fashioned charm|old fashioned storytelling|
clever twists|ingenious twists|unpredictable twists|
keeps you guessing|keep you guessing
""")
_phrases(0.3, """
not for everyone|not for everybody|not for all tastes|
not everyone's cup of tea|not everybody's cup of tea|
not exactly a masterpiece|not a masterpiece|
not without flaws|not without its flaws|not without problems|
not without its problems|not entirely successful|
not always successful|not completely successful|
an interesting premise|interesting premise|intriguing premise|
promising premise|good intentions|noble intentions|
best intentions|well intentioned|well meaning|
at its best|in its best moments|has potential|
shows promise|shows some promise|some promise|
""")
_phrases(-0.6, """
at best|at its worst|in theory|on paper|in name only|
nice try|a nice try|a good try|an ambitious failure|
a noble failure|an honorable failure|an interesting failure|
too much of a good thing|mixed bag|a mixed bag|hit and miss|
hit or miss|missed opportunities|an acquired taste|
could be worse|could have been worse
""")
_phrases(-1.5, """
nothing new|nothing original|nothing special|nothing remarkable|
nothing memorable|nothing fresh|nothing surprising|
nothing of interest|nothing of substance|
little substance|little depth|little insight|little imagination|
little originality|little charm|little wit|little humor|little humour|
little fun|little excitement|little suspense|little tension|
little interest|little energy|little life|little emotion|
few laughs|few surprises|few pleasures|
a few bright spots|a few good moments|a few nice moments|
not much fun|not much of anything|not much else|
not much to say|not much to offer|not much to see|
not enough laughs|not enough fun|not enough substance|
not funny enough|not interesting enough|not good enough|
not nearly enough|not nearly as good|not as good|
could have been better|should have been better|ought to be better|
could be better|should be better|should have been more|
should have been fun|should have been funny|
less than satisfying|less than compelling|less than convincing|
less than entertaining|less than thrilling|less than impressive|
less than the sum of its parts|
leaves something to be desired|leave something to be desired|
leaves much to be desired|leave much to be desired|
does little|offers little|adds little|brings little|
offers nothing|adds nothing|brings nothing|
does nothing new|adds nothing new|brings nothing new|
plays it safe|play it safe|by the book|by the numbers|
paint by numbers|paint by number|cookie cutter|
run of the mill|garden variety|middle of the road|
by rote|going through the motions|goes through the motions|
go through the motions|phoning it in|phones it in|phoned in|
straight to video|straight to dvd|made for television|
low rent|second hand|secondhand|third hand|
too long|too slow|too short|too much|too little|
too familiar|too predictable|too obvious|too neat|
too cute|too clever|too pleased with itself|
too earnest|too sentimental|too simplistic|too simple|
overly sentimental|overly familiar|overly simplistic|
overly earnest|overly ambitious|
over the top|trying too hard|tries too hard|try too hard|
more is less|less is more than this|
lacks focus|lacks direction|lacks purpose|
lack of focus|lack of direction|lack of purpose|
lacks a point|lacks a plot|lacks a story|
without a plot|without a story|without a point|
out of place|out of touch|out of tune|
all over the place|out of control|
in spite of itself|despite itself
""")
_phrases(-2.3, """
waste of time|wastes your time|wasting your time|waste your time|
waste of money|waste of talent|waste of film|waste of celluloid|
waste of space|wasted opportunity|missed opportunity|
a waste|total waste|complete waste|utter waste|
a bore|a dull affair|a tedious affair|a sorry excuse|
a pale imitation|pale imitation|a poor imitation|poor imitation|
a pale shadow|pales in comparison|pale in comparison|
falls flat|fall flat|fell flat|falls apart|fall apart|fell apart|
falls short|fall short|fell short|comes up short|come up short|
misses the mark|miss the mark|missed the mark|
misses its mark|misses the point|miss the point|
loses its way|lost its way|loses the plot|lost the plot|
loses steam|loses momentum|runs out of steam|run out of steam|
runs out of ideas|run out of ideas|runs out of gas|
goes nowhere|go nowhere|going nowhere|gets nowhere|
goes on and on|drags on|drag on|drags along|
gets bogged down|bogged down|gets lost|gets tiresome|
never gets going|never gets off the ground|never takes off|
fails to take off|fails to launch|
fails to deliver|fail to deliver|failed to deliver|
fails to engage|fails to entertain|fails to convince|
fails to connect|fails to impress|fails to satisfy|
failure to launch|failure of imagination|
a chore|a slog|a drag|a dud|a dud of|
painful to watch|painful viewing|hard to sit through|
difficult to sit through|tough to sit through|
hard to recommend|difficult to recommend|impossible to recommend|
hard to enjoy|difficult to enjoy|impossible to enjoy|
hard to care|difficult to care|impossible to care|
hard to like|difficult to like|impossible to like|
hard to love|difficult to love|impossible to love|
no fun|no laughs|no wit|no charm|no imagination|
no originality|no suspense|no tension|no excitement|
no emotion|no soul|no heart|no depth|no substance|
no point|no reason to exist|no reason to see|
nothing to offer|nothing to recommend|little to recommend|
nothing going for it|not going for it|not worth|
worth neither|not worth seeing|not worth watching|
not worth your time|not worth the time|not worth the effort|
not worth the money|not worth the price|
does not work|do not work|did not work|does not deliver|
never works|never worked|it does not|
cannot save|can not save|could not save|unable to save|
can not rescue|could not rescue|
no amount of|not even the|
only redeeming feature|only redeeming quality|only saving grace|
only good thing|the one good thing|only bright spot|
style over substance|all style and no substance|
more style than substance|more noise than|
emotionally empty|emotionally hollow|emotionally dead|
emotionally cold|emotionally distant|emotionally flat|
leaves you cold|leave you cold|left me cold|leaves me cold|
leave me cold|leaves us cold|left us cold|
leaves you numb|falls on deaf ears|
heavy handed|ham fisted|ham handed|heavy handedness|
self important|self importance|self indulgent|self indulgence|
self satisfied|self satisfaction|self congratulatory|
mean spirited|mean spiritedness|small minded|
brain dead|mind numbing|mind numbingly|mindless drivel|
laugh free|humor free|humour free|laughs are few|
laughs are scarce|laughs are nonexistent|
cheap shot|cheap shots|cheap sentiment|cheap sentimentality|
cheap imitation|cheap trick|cheap tricks|
bad taste|badly acted|badly made|badly directed|
badly written|badly paced|badly plotted|poorly acted|
poorly made|poorly directed|poorly written|poorly paced|
poorly conceived|poorly executed|poorly developed|
sloppily made|sloppily written|sloppily directed|
clumsily made|clumsily directed|clumsily written|
thinly drawn|thinly written|thinly plotted|
one dimensional|two dimensional|cardboard characters|
cardboard character|stock characters|stock character|
walking cliches|walking cliche|cliche ridden|
cliche filled|cliche infested|full of cliches|
lacks originality|lacks imagination|lack of originality|
lack of imagination|lack of substance|lack of depth|
lack of heart|lack of soul|lack of humor|lack of humour|
lack of wit|lack of charm|lack of suspense|
a step backward|a step backwards|a step down|
sinks to|scrapes the bottom|bottom of the barrel|
scraping the bottom|scraping the barrel|
been there done that|seen it all before|seen this before|
seen that before|seen a hundred times|seen a thousand times|
nothing we have not seen before|nothing you have not seen before|
less than meets the eye|not all that good|
all dressed up with nowhere to go|treading water|treads water|
promises more than it delivers|more than it can deliver
""")
_phrases(-3.3, """
one of the worst|worst film of the year|worst movie of the year|
worst film ever|worst movie ever|as bad as it gets|
as bad as they come|an unmitigated disaster|a complete disaster|
a total disaster|an absolute disaster|a colossal waste|
a complete mess|a total mess|an unholy mess|a godawful mess|
a train wreck|train wreck|trainwreck|dead on arrival|
dead in the water|cinematic disaster|utter garbage|
complete garbage|absolute garbage|total garbage|
utter rubbish|complete rubbish|absolute rubbish|
utter crap|total crap|complete crap|absolute crap|
bored to tears|bored to death|boring as hell|
boring as watching paint dry|watching paint dry|
about as funny as|about as entertaining as|
less fun than|less entertaining than|
a new low|an all time low|all time low|
insult to the intelligence|insult to your intelligence|
insults your intelligence|insults the audience|
an insult to|a slap in the face|
save your money|save yourself the trouble|
do not bother|do not waste your time|do not waste your money|
do not waste money|not bother seeing|not bother watching|
stay away|avoid at all costs|avoid this movie|avoid this film|
skip it|skip this|give it a miss|give this a miss|
wish i had not|wish i never|want my money back|
i want my time back|hours of my life back|
could not care less|can not care less|
who cares|why bother|what is the point|what was the point|
why was this made|why this was made|should never have been made|
should not have been made|should not exist|
the emperor has no clothes|emperor has no clothes|
a bad joke|a sick joke
""")
_phrases(1.6, """
so bad it is good|so bad that it is good|so bad they are good|
so bad it is fun|so bad it is funny|bad in a good way|
enjoyably bad|delightfully silly|delightfully goofy|
delightfully absurd|wonderfully silly|gloriously silly|
gloriously ridiculous|gloriously over the top|
unabashedly entertaining|unashamedly entertaining|
cheap thrills|silly but fun|dumb but fun|
bad guys to root for
""")
_phrases(2.6, """
can not wait to see|can not wait to watch|
could not stop laughing|can not stop laughing|
could not stop smiling|can not stop smiling|
could not take my eyes off|can not take your eyes off|
can not take my eyes off|could not take your eyes off|
will not soon forget|will not forget|can not forget|
never less than entertaining|never less than interesting|
never a dull moment|not a dull moment|
nothing short of brilliant|nothing short of superb|
nothing short of amazing|nothing short of wonderful|
nothing short of magnificent|nothing short of a masterpiece|
nothing short of spectacular|nothing short of remarkable|
nothing less than brilliant|nothing less than wonderful|
as close to perfect as|close to perfection
""")

for _adjective in (
    "like", "love", "enjoy", "admire", "appreciate", "recommend",
    "be charmed", "be moved", "be impressed", "be entertained"
):
    _phrases(2.4, "hard not to " + _adjective + "|difficult not to " + _adjective)
    _phrases(2.8, "impossible not to " + _adjective)
for _adjective in ("like", "love", "enjoy", "admire"):
    _phrases(2.0, "easy to " + _adjective)
for _adjective in ("dislike", "hate", "resist"):
    _phrases(2.0, "hard to " + _adjective + "|difficult to " + _adjective)
    _phrases(2.5, "impossible to " + _adjective)

# Neutral spans prevent ordinary plot descriptions and idioms from being
# mistaken for judgments of a film.
_phrases(0.0, """
special effects|visual effects|practical effects|sound effects|
special effect|visual effect|sound effect|
romantic comedy|romantic comedies|romantic drama|romantic dramas|
dark comedy|black comedy|dark humor|black humor|gallows humor|
dark humour|black humour|gallows humour|
comic book|comic books|comic strip|comic strips|
science fiction|science fictional|sci fi|
love story|love stories|love triangle|love triangles|
love scene|love scenes|love interest|love interests|
love affair|love affairs|love life|love lives|true love|
young love|first love|lost love|unrequited love|
fall in love|falls in love|fell in love|falling in love|
make love|makes love|making love|
love and loss|pain and loss|pain and suffering|grief and loss|
good guy|good guys|bad guy|bad guys|good cop|bad cop|
good guys and bad guys|good versus evil|good vs evil|
good and evil|battle of good and evil|
best friend|best friends|best man|best known|
good old boy|good old boys|good old days|
bad boy|bad boys|bad girl|bad girls|bad santa|
good girl|the good girl|the good thief|the good shepherd|
good will hunting|a beautiful mind|beautiful mind|
pretty woman|pretty women|pretty boy|pretty boys|
pretty much|pretty well|pretty soon|pretty nearly|
die hard|dirty dancing|true lies|love actually|
little miss sunshine|bad news bears|
the great depression|great depression|great war|
great britain|great expectations|great deal|good deal|
a good deal|a great deal|for good|as well as|
as well|well as|well being|well known|well off|
well to do|well worn|well established|
all too|all but|but then again|
not only|not just|not merely|not simply|not necessarily|
not to mention|not least|not least of all|
no doubt|no doubts|no question|no questions|
no wonder|no less than|no less|no small|
without a doubt|without doubt|without question|
without reservation|without reservations|without hesitation|
without fail|without further ado|
nothing but|anything but ordinary|
nothing if not|nothing short of|nothing less than|
never before|never again|never mind|
no matter|no matter how|no matter what|
no one|no person|no stranger|no strangers|
not yet|not sure|not certain|
of little|a little bit|a little|a bit|bit of a|
at least|at last|in the least|
flat out|flat screen|flat screens|
dead end|dead ends|dead man|dead men|dead woman|
dead people|dead body|dead bodies|living dead|
dead serious|dead set|dead ringer|
cold war|cold blood|cold blooded|cold case|
cold mountain|the cold light of day|
hard work|hard working|hard boiled|hard core|
hard rock|rock and roll|rock n roll|
low budget|small budget|big budget|high budget|
low cost|low key|high concept|
working class|middle class|upper class|
social class|social classes|class struggle|
evil dead|the evil dead|resident evil|
murder mystery|serial killer|serial killers|
atomic bomb|nuclear bomb|time bomb|bomb threat|
horror movie|horror film|horror movies|horror films|
action movie|action film|action movies|action films|
disaster movie|disaster film|disaster movies|disaster films|
bad language|strong language|graphic violence|
adult themes|adult content|sexual content|
serious subject|serious subject matter|serious issues|
serious issue|serious topic|serious themes|
based on a novel|based on the novel|original version|
original film|original movie|the original|
works of|works by|works for|works at|
moving from|moving to|moving into|moving out|
back and forth|back story|back stories|
all right|alright
""")
_phrases(1.0, "all right|alright")
_phrases(-1.3, "anything but ordinary")
_phrases(0.0, "anything but ordinary")
_phrases(2.0, "anything but boring|anything but dull|anything but predictable")

# Index phrases for efficient longest-span matching.
_PHRASE_INDEX = {}
for _key, _value in _PHRASES.items():
    _PHRASE_INDEX.setdefault(_key[0], []).append((_key, _value))
for _key in _PHRASE_INDEX:
    _PHRASE_INDEX[_key].sort(key=lambda entry: len(entry[0]), reverse=True)

_BOUNDARIES = {".", "!", "?", ";", ":", ","}
_SENTENCE_BOUNDARIES = {".", "!", "?", ";"}
_NEGATORS = {
    "not", "never", "no", "neither", "nor", "without", "hardly",
    "scarcely", "barely", "nothing", "nobody", "nowhere",
    "lack", "lacks", "lacking", "lacked", "fail", "fails", "failed", "failing",
}
_CONTRAST = {"but", "yet", "however", "nevertheless", "nonetheless"}
_INTENSITY = {
    "very": 1.28, "really": 1.18, "extremely": 1.5, "incredibly": 1.45,
    "unbelievably": 1.4, "utterly": 1.45, "totally": 1.3,
    "completely": 1.3, "absolutely": 1.45, "thoroughly": 1.3,
    "deeply": 1.3, "highly": 1.3, "immensely": 1.4,
    "exceptionally": 1.4, "remarkably": 1.25, "particularly": 1.15,
    "especially": 1.2, "so": 1.2, "such": 1.15, "quite": 1.1,
    "rather": 0.95, "pretty": 1.08, "genuinely": 1.2,
    "truly": 1.25, "perfectly": 1.2, "wonderfully": 1.2,
    "beautifully": 1.15, "surprisingly": 1.15, "positively": 1.2,
    "simply": 1.15, "downright": 1.3, "plain": 1.15,
    "plainly": 1.1, "just": 1.0, "almost": 0.55, "nearly": 0.65,
    "somewhat": 0.65, "slightly": 0.6, "mildly": 0.65,
    "fairly": 0.8, "reasonably": 0.8, "relatively": 0.8,
    "moderately": 0.7, "occasionally": 0.65, "sometimes": 0.75,
    "sporadically": 0.55, "intermittently": 0.6,
}
_EXCESS_POSITIVE = {
    "clever", "cute", "smart", "earnest", "sentimental", "sweet",
    "simple", "neat", "polished", "slick", "ambitious", "serious",
    "sincere", "quirky", "quirkiness", "stylish", "artistic",
    "selfconscious", "busy", "complex", "complicated", "subtle",
    "restrained", "gentle", "tasteful", "respectful", "respectable",
}
_COMPONENTS = {
    "actor", "actors", "actress", "actresses", "performance", "performances",
    "cast", "casting", "cinematography", "photography", "soundtrack", "score",
    "visuals", "costumes", "sets", "scenery", "landscapes",
}
_MAIN_TARGETS = {"film", "movie", "picture", "experience", "entertainment"}


def _word_score(word):
    if word in _WORDS:
        return _WORDS[word]
    candidates = []
    if word.endswith("ly") and len(word) > 5:
        candidates.extend((word[:-2], word[:-3] + "y"))
    if word.endswith("ies") and len(word) > 5:
        candidates.append(word[:-3] + "y")
    if word.endswith("s") and len(word) > 4 and not word.endswith("ss"):
        candidates.append(word[:-1])
        if word.endswith("es"):
            candidates.append(word[:-2])
    if word.endswith("ed") and len(word) > 5:
        candidates.extend((word[:-2], word[:-1], word[:-3]))
        if word.endswith("ied"):
            candidates.append(word[:-3] + "y")
    if word.endswith("ing") and len(word) > 6:
        candidates.extend((word[:-3], word[:-3] + "e"))
        if word[-4:-3] == word[-5:-4]:
            candidates.append(word[:-4])
    if word.endswith("ness") and len(word) > 7:
        candidates.extend((word[:-4], word[:-5] + "y"))
    for candidate in candidates:
        if candidate in _WORDS:
            return _WORDS[candidate] * 0.9
    if re.search(r"(.)\1\1", word):
        for reduced in (
            re.sub(r"(.)\1{2,}", r"\1\1", word),
            re.sub(r"(.)\1{2,}", r"\1", word)):
            if reduced in _WORDS:
                return _WORDS[reduced]
    return 0.0


def _extract_text(state, depth=0):
    if depth > 12:
        return ""
    if isinstance(state, str):
        return state
    if isinstance(state, dict):
        priorities = (
            "text", "sentence", "review", "review_text", "movie_review",
            "input_text", "sentence_text", "content", "document", "utterance",
            "passage", "comment", "message", "input", "data", "state", "example",
        )
        for key in priorities:
            if key in state:
                text = _extract_text(state[key], depth + 1)
                if text:
                    return text
        parts = []
        excluded = {
            "answer", "label", "sentiment", "id", "index", "question",
            "question_name", "question_id", "task", "task_definition",
            "instructions", "criteria", "output_schema", "type", "name",
        }
        for key, value in state.items():
            if key not in excluded:
                text = _extract_text(value, depth + 1)
                if text:
                    parts.append(text)
        return " ".join(parts)
    if isinstance(state, (list, tuple)):
        return " ".join(_extract_text(item, depth + 1) for item in state)
    return ""


def _find_events(tokens):
    events = []
    neutralized = set()
    i = 0
    n = len(tokens)
    while i < n:
        match = None
        for phrase, score in _PHRASE_INDEX.get(tokens[i], ()):
            length = len(phrase)
            if tuple(tokens[i:i + length]) == phrase:
                match = (length, score, phrase)
                break
        if match is not None:
            length, score, phrase = match
            for j in range(i, i + length):
                if tokens[j] in _NEGATORS:
                    neutralized.add(j)
            if score:
                events.append((i, i + length, score, phrase))
            i += length
            continue
        score = _word_score(tokens[i])
        if tokens[i] in _INTENSITY:
            nearby = tokens[i + 1:i + 4]
            if any(_word_score(t) for t in nearby):
                score = 0.0
        if tokens[i] in {"fail", "fails", "failed", "failing"}:
            if "to" in tokens[i + 1:i + 3]:
                score = 0.0
        if tokens[i] in {"lack", "lacks", "lacking", "lacked"}:
            following = tokens[i + 1:i + 6]
            if any(_word_score(t) > 0.5 for t in following):
                score = 0.0
        if score:
            events.append((i, i + 1, score, (tokens[i],)))
        i += 1
    return events, neutralized


def _is_contrast(tokens, j):
    word = tokens[j]
    if word not in _CONTRAST:
        return False
    before = tokens[max(0, j - 3):j]
    if word == "but":
        if before and before[-1] in {
            "anything", "nothing", "everything", "all", "help", "little"
        }:
            return False
        if "only" in tokens[max(0, j - 18):j]:
            start = max(0, j - 18)
            for k in range(start, j - 1):
                if tokens[k:k + 2] in (["not", "only"], ["not", "just"]):
                    return False
    if word == "yet":
        if before and before[-1] in {"not", "best", "finest", "worst", "as"}:
            return False
        if j < 2:
            return False
    return True


def _position_weights(tokens):
    n = len(tokens)
    weights = [1.0] * n
    for j in range(n):
        if _is_contrast(tokens, j):
            left = j - 1
            while left >= 0 and tokens[left] not in _SENTENCE_BOUNDARIES:
                left -= 1
            right = j + 1
            while right < n and tokens[right] not in _SENTENCE_BOUNDARIES:
                right += 1
            for k in range(left + 1, j):
                weights[k] *= 0.58
            for k in range(j + 1, right):
                weights[k] *= 1.32
    for j, word in enumerate(tokens):
        if word not in {"although", "though", "despite", "albeit", "while"}:
            continue
        if word == "while":
            if j + 1 < n and tokens[j + 1] in {"watching", "viewing", "filming"}:
                continue
        start = j - 1
        while start >= 0 and tokens[start] not in _SENTENCE_BOUNDARIES:
            start -= 1
        end = j + 1
        while end < n and tokens[end] not in _SENTENCE_BOUNDARIES:
            end += 1
        comma = None
        for k in range(j + 1, end):
            if tokens[k] == ",":
                comma = k
                break
        initial = j - start <= 3
        if initial and comma is not None:
            for k in range(j, comma):
                weights[k] *= 0.58
            for k in range(comma + 1, end):
                weights[k] *= 1.16
        elif not initial:
            for k in range(j, end):
                weights[k] *= 0.58
        elif word in {"despite", "albeit"}:
            for k in range(j, min(end, j + 9)):
                weights[k] *= 0.75
    # Explicit concluding assessments generally dominate supporting details.
    for j, word in enumerate(tokens):
        conclusion = word in {"ultimately", "overall"}
        if tuple(tokens[j:j + 4]) == ("in", "the", "end", ","):
            conclusion = True
        if tuple(tokens[j:j + 3]) in {
            ("all", "in", "all"), ("on", "the", "whole"),
            ("on", "balance", ","),
        }:
            conclusion = True
        if conclusion:
            for k in range(j):
                weights[k] *= 0.85
            for k in range(j, n):
                weights[k] *= 1.2
    return weights


def _left_context(tokens, i, limit=7):
    start = max(0, i - limit)
    for j in range(i - 1, start - 1, -1):
        if tokens[j] in _BOUNDARIES or _is_contrast(tokens, j):
            start = j + 1
            break
    return start, tokens[start:i]


def _negation_factor(tokens, i, end, neutralized, base):
    start, context = _left_context(tokens, i)
    count = 0
    for j in range(start, i):
        if j in neutralized:
            continue
        word = tokens[j]
        if word not in _NEGATORS:
            continue
        following = tokens[j + 1:i]
        if word == "not" and following:
            if following[0] in {"only", "just", "merely", "simply", "necessarily"}:
                continue
            if following[:2] == ["to", "mention"]:
                continue
        if word == "no" and following:
            if following[0] in {"doubt", "wonder", "question", "less", "matter", "one"}:
                continue
        if word == "without" and following:
            if following[0] in {"doubt", "question", "reservation", "reservations",
                                "hesitation", "fail"}:
                continue
            if following[:2] == ["a", "doubt"]:
                continue
        if word == "nothing" and following:
            if following[0] in {"but", "short", "less"}:
                continue
        if word == "never" and following:
            if following[0] in {"before", "mind", "less"}:
                continue
        count += 1
    # "Anything but" and "far from" have negative scope despite "but"
    # normally ending an ordinary negation's scope.
    prefix = tokens[max(0, i - 7):i]
    joined = " ".join(prefix)
    if re.search(r"(?:anything but|far from|a far cry from)(?: \w+){0,3}$", joined):
        count += 1
    if context and context[-1] in {"less", "minus"}:
        if len(context) < 2 or context[-2] not in {"no", "nothing"}:
            count += 1
    if re.search(r"(?:could|can) not be less(?: \w+){0,2}$", joined):
        return -1.3
    if re.search(r"(?:could|can) not be more(?: \w+){0,2}$", joined):
        return 1.35
    # "I cannot recommend it highly enough" is emphatic praise.
    if base > 0 and any(t.startswith("recommend") for t in tokens[i:end]):
        if "enough" in tokens[end:min(len(tokens), end + 7)]:
            if count:
                return 1.35
    if "help" in context and "not" in context:
        if "but" in prefix or "can" in prefix or "could" in prefix:
            return 1.0
    if count % 2:
        # Negating an extreme compliment is generally milder than making
        # an extreme criticism; negating a criticism is qualified praise.
        return -0.85 if base > 0 else -0.72
    if count:
        return 0.85
    return 1.0


def _context_factor(tokens, i, end, base):
    start, before = _left_context(tokens, i, 5)
    factor = 1.0
    for word in before[-3:]:
        factor *= _INTENSITY.get(word, 1.0)
    factor = min(1.85, max(0.35, factor))
    last_words = before[-3:]
    if "too" in last_words or "overly" in last_words or "excessively" in last_words:
        if base < 0:
            factor *= 1.2
        elif tokens[i] in _EXCESS_POSITIVE:
            factor *= -0.95
    if base > 0:
        joined = " ".join(before)
        if re.search(r"(?:tries|trying|strives|striving|strains|straining|wants) to be(?: \w+){0,2}$",
                     joined):
            factor *= -0.55
        if re.search(r"(?:could|should|would|might|ought) (?:have been|have|be|to be)(?: \w+){0,2}$",
                     joined):
            factor *= -0.65
        if "almost" in before[-2:] and "not" not in before:
            factor *= -0.4
        if "supposed" in before and "be" in before:
            factor *= -0.65
        if "pretends" in before or "pretending" in before:
            factor *= -0.6
        if "only" in before[-2:] and tokens[i] in {
            "occasionally", "sometimes", "intermittently"
        }:
            factor *= 0.55
    if end < len(tokens) and tokens[end] == "!":
        factor *= 1.08
    # Adjectives attached to the film itself are slightly more informative
    # than compliments to a supporting technical element.
    nearby = tokens[end:min(len(tokens), end + 4)]
    for word in nearby:
        if word in _BOUNDARIES or word in {"but", "and", "or", "than"}:
            break
        if word in _MAIN_TARGETS:
            factor *= 1.13
            break
        if word in _COMPONENTS:
            factor *= 0.88
            break
    return factor


def _comparison_weights(tokens, events):
    weights = [1.0] * len(events)
    for j in range(1, len(events)):
        i, end, base, phrase = events[j]
        pi, pend, pbase, pphrase = events[j - 1]
        between = tokens[pend:i]
        if len(between) > 7 or any(w in _BOUNDARIES for w in between):
            continue
        if "than" in between:
            earlier = tokens[max(0, pi - 4):pi]
            if any(w in {"more", "less", "rather"} for w in earlier):
                weights[j] *= 0.25
            elif pbase * base < 0 and (
                tokens[pi] in {"better", "worse"} or
                "rather" in between
            ):
                weights[j] *= 0.35
        if "rather" in between and "than" in between:
            weights[j] *= 0.35
    return weights


def _special_adjustment(tokens):
    text = " ".join(tokens)
    score = 0.0
    if re.search(r"\b(?:unfortunately|sadly|regrettably|alas)\b", text):
        score -= 0.8
    if re.search(r"\b(?:fortunately|thankfully|happily)\b", text):
        score += 0.7
    if re.search(r"\b(?:if only|what a pity|what a shame|such a shame)\b", text):
        score -= 1.3
    if re.search(r"\b(?:i|we|you) (?:deserve|deserved) better\b", text):
        score -= 2.0
    if re.search(r"\b(?:deserves|deserved) (?:a )?better (?:film|movie|script|director)\b", text):
        score -= 1.8
    if re.search(r"\b(?:why|who) (?:\w+ ){0,5}(?:think|thought) (?:\w+ ){0,3}good idea\b", text):
        score -= 3.5
    if re.search(r"\b(?:more|better) suited (?:\w+ ){0,3}(?:television|tv|video)\b", text):
        score -= 1.0
    if re.search(r"\b(?:a|an) (?:movie|film) (?:that|which) (?:\w+ ){0,3}(?:nobody|no one) (?:needs|needed|asked)\b", text):
        score -= 2.0
    if re.search(r"\b(?:the|its) (?:best|funniest|most enjoyable) (?:thing|part|moment) (?:\w+ ){0,6}(?:end|ending|credits|over)\b", text):
        score -= 4.0
    if re.search(r"\b(?:only|sole) (?:\w+ ){0,2}(?:reason|thing) (?:\w+ ){0,4}(?:see|watch)\b", text):
        score -= 0.8
    if re.search(r"\b(?:can|could) not (?:\w+ ){0,3}(?:save|rescue|salvage)\b", text):
        score -= 0.9
    if re.search(r"\b(?:wastes|wasting|squanders|squandering) (?:\w+ ){0,3}(?:talent|talents|cast|premise|potential)\b", text):
        score -= 1.0
    if re.search(r"\b(?:do|does|did) not (?:\w+ ){0,2}(?:live|lives) up to\b", text):
        score -= 2.0
    if re.search(r"\b(?:not|never) (?:\w+ ){0,2}(?:a|the) (?:\w+ ){0,1}(?:dull|boring) moment\b", text):
        score += 1.2
    if re.search(r"\b(?:could|can) not (?:have been|be) (?:\w+ ){0,1}better\b", text):
        score += 2.8
    if re.search(r"\b(?:could|can) not (?:have been|be) (?:\w+ ){0,1}worse\b", text):
        score -= 3.0
    if re.search(r"\b(?:not|never) (?:remotely|even|at all|especially|particularly)? ?(?:funny|entertaining|interesting|engaging)\b", text):
        score -= 0.5
    if re.search(r"\b(?:would|will) (?:rather|sooner) (?:watch|see|sit)\b", text):
        score -= 1.5
    if re.search(r"\b(?:made|makes) (?:me|us) (?:want to )?(?:leave|walk out|sleep|fall asleep)\b", text):
        score -= 2.2
    if re.search(r"\b(?:fell|falling|fall) asleep\b", text):
        score -= 1.7
    if re.search(r"\b(?:walked|walking) out\b", text):
        score -= 1.0
    if re.search(r"\b(?:kept|keeps|keep) (?:me|you|us) (?:riveted|engaged|entertained|guessing|hooked)\b", text):
        score += 1.0
    if re.search(r"\b(?:will|would) (?:gladly |happily )?(?:watch|see) (?:it|this|the film|the movie) again\b", text):
        if not re.search(r"\b(?:not|never)\b", text):
            score += 1.8
    if re.search(r"\b(?:wish|wished) (?:it|the movie|the film) (?:were|was|had been) (?:longer|not over)\b", text):
        score += 1.7
    if re.search(r"\b(?:wish|wished) (?:it|the movie|the film) (?:were|was|had been) (?:shorter|over)\b", text):
        score -= 1.7
    # Numeric review grades are a useful independent signal.
    for match in re.finditer(r"\b(\d+(?:\.\d+)?)\s*(?:out of)\s*(\d+(?:\.\d+)?)\b", text):
        value = float(match.group(1))
        maximum = float(match.group(2))
        if maximum in {4.0, 5.0, 10.0, 100.0} and 0 <= value <= maximum:
            ratio = value / maximum
            score += (ratio - 0.55) * 9.0
    return score


def predict(state):
    raw = _extract_text(state)
    tokens = _normalize(raw)
    if not tokens:
        return {"answer": "positive"}
    events, neutralized = _find_events(tokens)
    position = _position_weights(tokens)
    comparison = _comparison_weights(tokens, events)
    total = 0.12
    strong_positive = 0.0
    strong_negative = 0.0
    for index, (i, end, base, phrase) in enumerate(events):
        negation = _negation_factor(tokens, i, end, neutralized, base)
        context = _context_factor(tokens, i, end, base)
        weight = position[i] * comparison[index]
        value = base * negation * context * weight
        total += value
        if value > strong_positive:
            strong_positive = value
        if value < strong_negative:
            strong_negative = value
    total += _special_adjustment(tokens)

    # Slash-based ratings are read from the original string because slashes
    # are also ordinary token separators in running prose.
    for match in re.finditer(r"(?<!\d)(\d+(?:\.\d+)?)\s*/\s*(10|5|4|100)(?!\d)", raw):
        numerator = float(match.group(1))
        denominator = float(match.group(2))
        if 0 <= numerator <= denominator:
            total += (numerator / denominator - 0.55) * 9.0
    if re.search(r"\b(?:zero|no|one|1)\s+stars?\b", raw.lower()):
        total -= 2.0
    if re.search(r"\b(?:four|five|4|5)\s+stars?\b", raw.lower()):
        total += 2.0

    return {"answer": "positive" if total >= 0 else "negative"}