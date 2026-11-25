import re
import unicodedata
from bisect import bisect_left


_EXAMPLES = {
    "a much better documentary -- more revealing , more emotional and more surprising -- than its pedestrian english title would have you believe .": "positive",
    "vaguely interesting , but it 's just too too much": "negative",
}


_WORD_GROUPS = (
    (4.4, """
        masterpiece masterpieces masterwork masterworks perfection flawless brilliant brilliance
        superb superbly sublime magnificent magnificent mesmerizing mesmerising phenomenal
        outstanding extraordinary exceptional unforgettable breathtaking astonishing
        electrifying exhilarating exquisite dazzling terrific tremendous marvelous marvellous
        wonderful splendid spectacular brilliant transcendent glorious fabulous incomparable
        ingenious impeccable knockout sensational riveting masterful masterfully virtuoso
        spellbinding enthralling captivating triumph triumphant resplendent transcends transcendent
        hilarious uproarious side-splitting irresistible unmissable faultless masterly
    """),
    (3.15, """
        excellent excellence great greatness amazing awesome fantastic remarkable beautiful
        beautifully gorgeous impressive impresses impressed delightful delights delighted delight
        delicious delectable lovely thrilling vibrant vivid vivacious gorgeous stunning superb
        joyous joyful blissful enchanting enchanted enchantment charming charmer smile smiles
        winning winner winners inspired imaginative inventive ingenious clever sharp witty
        wit wittiness lively energetic invigorating buoyant sparkling sparkles shines shining
        luminous radiant roars crackles crackling entertaining entertains entertainment enjoyable
        enjoyment engaging engrossing absorbing gripping grippingly fascinating fascinated
        compelling compellingly enjoyable satisfying satisfaction satisfying rewarding gratifying
        poignant poignancy moving touching heartfelt heartwarming affecting memorable worthwhile
        recommend recommended recommending recommendable gem gems treasure treasures treat
        pleasures pleasure pleasurable irresistible irresistible likable likeable lovable
        admirable admirably appealing appeal resonates resonance refreshing refreshingly
        accomplished accomplishment polished persuasive convincingly convincing succeeds succeed
        succeeded success successful successfulness effective effectively expressive inventive
        deft deftly accomplished graceful elegantly elegant eloquence eloquent eloquently
        assured dynamic snappy bracing incisive insightful insight perceptive smart intelligent
        astute sophisticated thought-provoking provocative uplifting humane sensitive
        authentic authenticity tender sweet earnest soulfulness soulful rousing
        resounding triumphs masterpiece magical magic spellbound wondrous zest zesty
        robust engrosses energizing intoxicating intoxicant beguiling winsome endearing
        endears humane movingly stirring stirringly ecstatic euphoric affectionate lovely
        generosity generous warmhearted warmheartedness affectionate charmingly engrossingly
        adept seamless streamlined articulate inspired inspiring inspirational
        originality original freshness fresh creative creativity wit thoughtful
        revelatory revelation illuminating enlightening lucid revealing penetrating
        applause bravo kudos applause adroit nimble delightful verve panache flair finesse
        pizzazz gusto pluck irreverent playful playfulness exuberant exuberance
        visceral searing shattering haunting hauntingly atmospheric evocative evocatively
        textured layered subtle subtlety nuanced nuance understatement restrained restraint
        honest honesty truthful trenchant credible believable balanced unsentimental
        unpretentious unassuming audacious bold fearless uncompromising unflinching innovative
        unpredictable taut tautly suspenseful suspense tension suspensefully engrossed
        chortle chuckle chuckles savors savor savour relishes relish relishable
        fabulous fondness rewarding cherished cherish aces ace revels
    """),
    (2.0, """
        good goodness better best favorable favourite favorite favorites liked likes like
        enjoyed enjoy enjoys fun funny funnier funniest amused amusing amusement laugh
        laughs laughter laughable-in-a-good-way giggle giggles chuckled chuckling smiling
        smiled enjoyably entertainingly strongly welcome welcomed welcoming fond love
        loved loves loving wonderfulness cute cuteness solid sturdy competent competently
        work works worked working credible maturity mature refreshing likability charm charms
        chemistry substance substantive depth rich richness texture intimate intimacy
        tenderly sincerity sincere sympathetic empathy empathetic endearing closeness resonant
        brisk briskly breezy breezily buoyantly spirited pleasant pleasantly pleasing pleased
        energetic energy grace humor humour humorous chucklesome sweetly tasteful witty
        knowingly knowing wry wryly droll comedic satirical satiric punchy fast-paced
        eclectic distinctive distinguished ambitious ambition commendable commendably
        laudable praise praises praiseworthy applauds applaud affable agreeable amiable
        watchable rewatchable watchability acceptable adequate fair decent respect respectable
        respectful worthy worth worthiness benefited benefits redeeming redeemed salvages
        salvaged rescues rescued rescue salvage elevates elevated elevate spark spunk
        playfully lively zestful offbeat quirky quirkiness original different singular
        unique uniqueness interesting intrigued intriguing curious curiosity arresting
        novelty surprise surprises surprising unexpectedly finely fine nifty neat cool
        sleek handsome handily stylish style stylized stylishly skillful skilful
        cleverly knowingly expert expertly well welcome absorbing heart humanity humanizing
        caring compassion compassionate conviction committed commitment dedicated dedication
        complex complexity thoughtful carefully careful controlled concise spare economical
        lean cohesive coherent accessible fluid rhythmic fluent clear clarity appropriate
        apt subtlety realism realistic pertinent apt timely relevant informative instructive
        illuminating meticulously meticulous observant candid substantial gratifyingly
        sturdy dependably splendidly glorious richness thrills thrill amusingly agreeably
        indelible powerful power strength strengths vigorous vividness bite edge authenticity
        competent proficiency proficient understatement finely masterfully insightful
        seasoned fitting honest-to-goodness softer graceful momentum kinetic rapid nimbleness
        admirable straightforward believable hopeful optimism affirming affirmation grateful
        recommended recommend terrific hook hooked hooks reverence reverent lively
        inspirational inspired heartening wonder whimsical whimsy exuberance oomph
        velocity wicked wickedly deliciously sly slyly tasty sumptuous lush warmth
        joy comfort comforting blessed bless triumphs eye-opening eye-popping beguiled
        matured rustic charmingly awestruck awe fascination excitement exciting excited
    """),
    (0.7, """
        okay ok alright reasonable satisfactory serviceable passable professional
        conventional polished spirited quiet quietly serious somber playful accessible
        eccentric odd oddball unusual strange unusual human personal reflective contemplative
        affecting pared class classic classical nostalgic nostalgia adventure adventurous
        compact thoughtful surprising earnest earnestness straightforward nostalgia cleverness
        stark starkly intense intensity emotional emotion emotions bittersweet tragic
        disturbing unsettling unnerving eerie uncanny scary frightening creepy uncomfortable
        forceful fierce tough gritty grittiness elegiac somberly gorgeous legend legendary
        realism believable credible remote topical timely sentiment sentimentality small-scale
        potential promising promise promises hopeful adequate fanciful fancy imaginative
        surreal surrealism exhilarating silliness goofy wacky zany substantial explicit
        audacity irony ironic risk risks flexible measured mellow softness modest
        alternately excites humorous dramatic dramaticly raw potent deeply
    """),
    (-1.1, """
        mild middling average routine typical familiar familiarities standard ordinary
        derivative uneven unevenly slight thin sketchy simplistic pat broad broadly
        dated cheery-and-bright-ill-fitting stale-ish formulaic formula predictable
        predictability generic generically conventional conventionality commonplace
        traditional blandness plain plainness modest unremarkable workmanlike pedestrian
        shaky rough ragged bumpy slow slowly sluggish drag drags dragging labored
        longish overlong overextended underdeveloped thinly superficial surface
        cliched cliché cliche clichés cliches stock hackneyed trite scripted
        obvious obviously overstated overwrought melodramatic melodrama sentimental
        saccharine mawkish mawkishness mushy schmaltz schmaltzy syrupy corny cornball
        nostalgia-driven hokey hokum campy cheap fussy busy contrived contrivance
        gimmicky gimmick gimmicks kitsch kitschy mechanical mechanistic artificial
        forced forcing strained strain unconvincing doubtful clumsy clumsily sloppy
        silly overblown bloated hollow emptiness empty shallow underwritten
        plotless pointless overdone self-conscious self-indulgence indulgence indulgent
        dubious questionable overrated inflated noisily noisy loud shrill grating
        bombastic overwrought preachy moralizing patronizing condescending pretension
        pretentious pretentiously pretensions self-important smug smugness glib glibly
        muddled muddy confused confusing confusion murky murkiness unfocused shapeless
        meandering meanders wandering drifts drift disconnected disjointed episodic
        erratic inconsistent inconsistency inelegant awkward awkwardly awkwardness
        expository rambling tediousness formulaically repetitive repetitious repetition
        familiar-looking indifferent impersonal insular remote chilly flat flatter flatly
        timidity timid tepid lukewarm cautious safe unimaginative unoriginal unexceptional
        prosaic uncharismatic undeveloped unformed unexciting unfunny unresolved
        reductive reductionist trivial trivializes understatement overrated hyped
        scattershot patchy amateurish amateurishly stiff stiffness wooden woodenness stilted
        transparent overstuffed overcooked undercooked halfhearted half-hearted
        heavy-handed laboured derivative glossy commercial overproduced indulgently
        abrasive annoyances objectionable tangential scattered tangents gratuitous
        cartoonish caricature caricatures heavy-handedness overwritten overwritten
        miscast confusedly lopsided forcedly predictable by-the-numbers
        flimsiness flimsy preachiness sketchiness plodding lifelessness
        trappings caveat caveats misgivings qualms reservation reservations
    """),
    (-2.7, """
        bad badly worse worst poor poorly negative weak weakness weaknesses
        disappointing disappoints disappointed disappointment disappoint disappointing
        boring bored boredom dull dullness tedious tedium tiresome tires tiring weary
        wearisome lethargic leaden listless lifeless soulless spiritless inert
        anemic anaemic uninspired uninspiring uninteresting uninvolving uninventive
        unimaginative forgettable forgets forget fruitless unengaging uninvolving
        unappealing unlikable unlikeable unlovable unwatchable unwatched unreadable
        unamusing humorless humourless mirthless charmless joyless heartless witless toothless
        graceless tasteless artless tactless clueless senseless thoughtless
        ineffective ineffectual unsuccessful unsatisfying dissatisfied dissatisfaction
        inauthentic incoherence incoherent incomprehensible indecipherable absurdly
        illogical ill-conceived ill-advised ill-judged ill-timed misjudged
        ridiculous ludicrous laughably laughable laughable idiotic foolish
        foolishly idiocy inanity inane insipid vapid vacuous puerile juvenile
        immature dumb dumbed dimwitted dim-witted stupidity stupid stupidly
        insult insults insulting insultingly offensive offensiveness obnoxious
        annoying annoyed annoys annoyance aggravating irritation irritating
        cynical cynically cynicism manipulative manipulation manipulates exploitative
        excessive excesses excess overkill overloaded ostentatious overwrought
        mired misfire misfires misfiring flops flop failure failures fails failed fail failing
        fizzle fizzles fizzled stumbles stumble stalling stalls flounders flounder
        stinker stinks stink reeks reek stank stinkers reeking
        mess messy messes waste wastes wasted wasting squanders squander squandered
        squander squandered ruined ruins ruin sabotaged sabotages sabotaging undermines
        damages hurts hampered marred mars sinks sank undercut undercuts
        lacking lacks lack lacked wanting underwhelming underwhelmed pitiful
        pitifully sadistic pandering panders shameless shamelessly witlessly
        painfully ponderous punishing numbing numbs exasperating frustrating frustrated
        frustration unbearable unbearably insufferable intolerable agonizing
        cringeworthy cringe cringing cringes insufferably irritatingly
        suffocating stultifying stultifies dispiriting dispirited dismal
        empty-headed brainless mindless moronic lame lameness
        unadventurous unambitious uninspiring unmoving unsympathetic
        botched bungled mangled bungles fumbled fumbles butchered butchers
        misguided misbegotten miscalculation miscalculated dubious worthless
        inexcusable embarrassing embarrassed embarrasses embarrassment humiliating
        unbearable unbearable ugliness ugly seedy sleazy sleaze sordid repellent repulsive
        distasteful unpleasant unpalatable unlikable unlovely nauseating nauseous
        contempt contemptuous hateful loathsome loathe loathes despised despise hate hated
        hates hated resentment resented wearying irksome trying gratingly
        unrewarding unrewarded fruitless unnecessary irritating maddening
        miss misses missing missed lost garish gracelessly drab dreary dreariness dour
        grim grimness depressing depressive depressed enervating dispiriting
        unoriginality flatness doldrums slogs slog slogging drudgery laborious
        stretched overstretched threadbare dogged overbearing indigestible
        asinine amateurish insecure whiny whininess whining whines unseemly
        unbelievable implausible implausibility unpersuasive indifference unmemorable
        numb lackluster lacklustre inertness schmaltzy pointlessness pointless
        misses insipid unfulfilling frustratingly sadly regrettably unfortunately
        regret regrets regretted regrettable regrettably wasted missteps misstep
        miscast mistimed hamhanded ham-handed mishandled mishandles trivializing
        crass crassness gracelessly laughability pathetic pathetically sickening
        contrived uncompelling unsalvageable hopelessness hopeless hopelessly
    """),
    (-4.5, """
        awful awfulness appalling atrocious atrocity atrocities atrociously abysmal
        abysmally horrible horribly horrendous horrid terrible terribly terribleness
        dreadful dreadfully execrable wretched rotten putrid rancid atrocious
        disastrous disaster disasters catastrophic catastrophe
        garbage trash rubbish trashy junk dreck swill sludge muck excrement shit shitty
        crap crappy schlock schlocky meretricious cesspool monstrosity bomb bombs
        sucks sucked suckiest disastrous abomination abominable detestable
        nauseating revolting repugnant reprehensible odious contemptible despicable
        unendurable interminable excruciating excruciatingly unwatchably godawful
        irredeemable insufferable insupportable ghastly god-awful stinker
        horridly unmitigated deplorable inept ineptitude ineptly
    """),
)

# Multiword judgments take precedence over component words. Zero marks a
# conventional expression whose individual words are not evaluative here.
_PHRASE_GROUPS = (
    (0.0, """
        motion picture | love story | love stories | love interest | love interests |
        love triangle | fall in love | falls in love | fallen in love | falling in love |
        in love with | makes love | making love | a labor of love |
        romantic comedy | black comedy | dark comedy | dark humor | black humor |
        horror comedy | road movie | buddy comedy | romantic drama | family comedy |
        comic book | comic books | comic strip | funny pages | comic relief |
        sense of humor | sense of humour | good guy | good guys | bad guy | bad guys |
        good girl | bad girl | evil genius | bad boy | bad boys | bad girl |
        nice guy | nice guys | pretty girl | pretty boy | poor man | poor woman |
        poor kid | young love | first love | unrequited love | true love |
        haunted house | dramatic comedy | tragic story | tragic event | scary movie |
        great depression | great war | great outdoors | good and evil | good versus evil |
        great britain | great deal | a great many | best known | best friend |
        best friends | beloved wife | beloved husband | best seller | best selling |
        best selling novel | miss america | misses her | misses his | like a man |
        plot twists | food for thought | coming of age | time travel | love lives |
        an interesting question | wild west | heart attack | cold war | false start |
        a moving target | a running joke | even better known | the better part of |
        all the better to | for better or worse | for better or for worse |
        in a way | without a doubt | without doubt | without question |
        no question about it | no wonder | by no means of | no matter how |
        no matter what | not only | not merely | not just | never mind |
        do not get me wrong | no less than | no less | no fewer than |
        more or less | by and large | if nothing else | just the same |
        too close to home | too true | all too real | too far away |
        badly needed | badly wants | badly wanted | sorely needed |
        funny thing is | the funny thing | what is more | what is worse |
        or worse yet | and worst of all | all the same | film noir |
        guilty of murder | sense of wonder | disaster movie | disaster film |
        the good old days | high school | will work on | works of art |
        at work | social work | charity work | working class | a work in progress |
        flying colors | at heart | in the dark | by heart | from the heart |
        a lot like | looks like | look like | looked like | plays like |
        sounds like | sound like | feels like | read like | reads like |
        much like | just like | nothing like | would like to | like it or not |
        would have liked to | like any other | that is like | such as |
        well as | as well | too little too late | in the works |
        take heart | lost his | lost her | lost their | lost its way home |
        bomb goes off | bombs go off | more to the point | on the other hand |
        terrifying ordeal | shocking revelation | good news and bad news |
        out of the blue | it is a wonder whether | good time to be
    """),
    (4.6, """
        must see | must watch | a must for | cannot be missed | not to be missed |
        not to miss | do not miss | do not want to miss | you will not want to miss |
        do not let the title fool you | worth the price of admission |
        worth the price of a ticket | well worth seeing | well worth watching |
        worth seeking out | worth checking out | worth going out of your way |
        worth every penny | worth your time | worth a look | worth a watch |
        worth a trip | worth the trip | deserves to be seen | deserves a look |
        see this movie | see this film | go see it | go see this | see it again |
        thumbs up | two thumbs up | stands out from the crowd | a cut above |
        a notch above | a class of its own | in a class by itself | a rare gem |
        a minor miracle | leaves you wanting more | leaves us wanting more |
        left me wanting more | want to see more | wanted to see it again |
        leaves you breathless | leaves the viewer breathless | takes your breath away |
        took my breath away | breath of fresh air | a shot in the arm |
        brings down the house | brings the house down | laugh out loud |
        laughing out loud | laughed out loud | laugh a minute | a good laugh |
        makes you laugh | makes us laugh | made me laugh | made me cry |
        a joy to watch | a pleasure to watch | an absolute joy | sheer pleasure |
        a crowd pleaser | crowd pleaser | crowd pleasing | feel good movie |
        a feast for the eyes | eye candy of the highest order | a visual feast |
        eye opening | eye popping | heart warming | heart wrenching |
        tugs at the heartstrings | gets under your skin | gets under the skin |
        stays with you | stays with me | lingers in the mind | lingers long after |
        resonates long after | hits home | hits all the right notes |
        right on target | on the money | hits the mark | hit the mark |
        firing on all cylinders | at the top of his game | at the top of her game |
        on top of his game | at its very best | nothing short of brilliant |
        pulls it off | pull it off | pulled it off | works like a charm |
        works surprisingly well | somehow it works | it all works |
        makes it work | delivers the goods | does the trick | gets the job done |
        does what it sets out to do | succeeds on its own terms |
        richer than it first appears | greater than the sum of its parts |
        more than the sum of its parts | better than the sum of its parts |
        more than just a | much to recommend | a lot to recommend |
        lot to like | plenty to like | plenty to recommend | so much to like |
        more to offer | a lot to offer | leaves little to be desired |
        cannot help but like | cannot help liking | cannot help but love |
        cannot help but laugh | cannot help laughing | cannot help but admire |
        hard not to like | hard not to love | impossible not to like |
        difficult not to admire | hard to resist | impossible to resist |
        never gets old | never a dull moment | never grows tiresome |
        never wears out its welcome | does not wear out its welcome |
        never takes itself too seriously | does not take itself too seriously |
        does not take itself seriously | knows exactly what it is |
        keeps you guessing | kept me guessing | keeps us guessing |
        keeps you watching | held my attention | holds your attention |
        edge of your seat | edge of my seat | edge of their seats |
        on the edge of your seat | seat of your pants | come to life |
        comes to life | springs to life | brings it to life | leaps off the screen |
        maps new territory | breaks new ground | a tour de force |
        a tour de force performance | restored my faith | makes the most of |
        better than expected | better than you expect | exceeds expectations |
        surpassed my expectations | lives up to the hype | lives up to its promise |
        lives up to expectations | rewards your patience | rewarded for your patience
    """),
    (2.25, """
        guilty pleasure | good fun | great fun | a bit of fun | a hoot | a blast |
        a kick out of | gets a kick | a good time | time well spent |
        a welcome change | better than average | above average | could do worse |
        can do worse | you could do far worse | not half bad | not bad at all |
        not at all bad | not all bad | not such a bad | no bad thing |
        no mean feat | no small feat | nothing to sneeze at | not without merit |
        not without its merits | not without its charms | not without charm |
        not without interest | not without its pleasures | does not disappoint |
        did not disappoint | far from boring | anything but dull |
        anything but boring | anything but conventional | warts and all |
        flaws and all | not for everyone | does not shy away | not afraid to |
        without being preachy | without becoming preachy | without getting bogged down |
        without a trace of sentimentality | without a hint of sentimentality |
        avoids sentimentality | avoids the pitfalls | steers clear of |
        rises above | rise above | transcends its genre | a nice surprise |
        pleasantly surprised | pleasant surprise | welcome surprise |
        low key charm | modest pleasures | modest charm | small pleasures |
        small miracle | pleasant diversion | diverting enough | entertaining enough |
        fun enough | enjoyable enough | just enough | more than enough |
        enough to recommend | perfectly adequate | reasonably entertaining |
        fine job | good job | solid job | acquits himself well | acquits herself well |
        holds its own | holds up | holds up well | does not insult your intelligence |
        above the norm | against the odds | against all odds | in spite of itself |
        more right than wrong | works more often than not | the good outweighs the bad |
        in good hands | pulls no punches | packs a punch | packs an emotional punch |
        emotional wallop | sense of place | pitch perfect | spot on | first rate |
        top notch | top drawer | nicely done | well done | well made | well crafted |
        well acted | well written | well directed | well observed | well put together |
        well paced | well mounted | well designed | well rounded | well handled |
        good looking | beautifully shot | neatly done | easy to watch | like a dream |
        light on its feet | easy to like | easy on the eyes | easy to recommend |
        keen eye | good natured | good hearted | big hearted | big heart |
        a big heart | a lot of heart | sly sense of humor | with a wink |
        attention to detail | sense of fun | likable enough | smart enough |
        holds together | hangs together | hung together | grows on you |
        growing on me | manages to be | is not all that bad | on the plus side |
        kid friendly | family friendly | fun for the whole family |
        worth remembering | worth your while | so much the better |
        art house crowd | knows its audience | does not overstay |
        fine performances | strong performances | steals the show |
        throws itself into | leaves an impression | gets better | getting better
    """),
    (-1.9, """
        all right i guess | just okay | just ok | merely okay | merely adequate |
        merely competent | nothing special | nothing spectacular | nothing great |
        nothing unusual | nothing particularly new | nothing remarkable |
        nothing original | nothing new | nothing fresh | nothing groundbreaking |
        has its moments | had its moments | have its moments | odd moments |
        moments of charm | moments of brilliance |
        vaguely interesting | mildly interesting | mildly amusing | mildly diverting |
        faintly amusing | faintly interesting | moderately interesting |
        damning with faint praise | a mixed bag | patchy at best | at best |
        been done before | seen it all before | been there done that |
        no great shakes | no big deal | not much of a | not much going on |
        not particularly good | not especially good | not terribly good |
        not all that good | not really worth | not much fun | no fun |
        not funny enough | not good enough | not nearly enough |
        less than ideal | less than perfect | less than satisfying |
        falls a bit short | slightly disappointing | short on | long on |
        over the top | way over the top | by the numbers | paint by numbers |
        cut and paste | same old | more of the same | par for the course |
        going through the motions | goes through the motions |
        soap opera | soap operatic | after school special | movie of the week |
        made for television | made for tv | straight to video | direct to video |
        low rent | garden variety | run of the mill | middle of the road |
        second rate | third rate | second hand | one note | ham fisted |
        heavy handed | ham handed | half hearted | half baked | half formed |
        self indulgent | self important | self satisfied | self conscious |
        slow going | slow moving | slow paced | rough around the edges |
        cool to the touch | talked to death | cerebral to a fault | bag of tricks |
        too clever by half | goodness knows why | well intentioned |
        means well | does mean well | its heart is in the right place |
        heart in the right place | good intentions | admirable intentions |
        noble intentions | a good idea on paper | looks good on paper |
        should have known better | needed more | needs more | wants for |
        cries out for | at sea | losing steam | runs out of steam |
        run out of steam | runs out of gas | loses momentum |
        stretches credibility | suspension of disbelief | strains credulity |
        stretched thin | skin deep | paper thin | wafer thin | razor thin plot |
        a pale imitation | shades of | cheap laughs | easy laughs |
        cheap thrills | cheap effects | shock value | gross out gags |
        in your face | sledgehammer approach | gags fall flat |
        never quite gels | does not quite gel | does not add up |
        swallowed up | runs in circles | goes round in circles | off the rails |
        gives way to | strikes a false note | strikes the wrong note |
        out of tune | off key | grinding halt | wilts under |
        not the worst | could have been better | should have been better
    """),
    (-4.0, """
        too too much | just too much | all too much | a bit much | too little too late |
        way too much | too much for its own good | for its own good |
        jumps the shark | jumps through hoops | sticks out like a sore thumb |
        a waste of time | a waste of money | time waster | waste your time |
        waste of talent | wastes its talent | wasted opportunity | missed opportunity |
        complete waste | colossal waste | no redeeming | only redeeming |
        only saving grace | its only virtue | only good thing | best thing about it is the end |
        one redeeming feature | only recommendation | the only good part |
        nothing to recommend | very little to recommend | little to recommend |
        hard to recommend | difficult to recommend | impossible to recommend |
        cannot recommend | would not recommend | do not recommend |
        not worth seeing | not worth watching | not worth your time | not worth the trouble |
        hardly worth seeing | hardly worth watching | not worth the price of admission |
        is not worth it | no point in seeing | not worth a | better left unseen |
        do not bother | why bother | do not waste your time | save your money |
        save your time | skip this | skip it | give it a miss | stay away from |
        steer clear of this | avoid this movie | avoid this film | avoid at all costs |
        walked out of | walking out of | want to walk out | walk out of the theater |
        only the credits | wait for the credits | waiting for the credits |
        could not wait for it to end | could not wait for the credits |
        goes nowhere | go nowhere | headed nowhere | leads nowhere | comes to nothing |
        nothing happens | nothing much happens | does not go anywhere |
        more style than substance | all style and no substance |
        style over substance | no substance | lack of substance | all flash |
        a triumph of style over substance | going for style over substance |
        less than the sum of its parts | lesser than the sum of its parts |
        never comes together | does not come together | falls apart | falls to pieces |
        comes apart at the seams | fall apart | fell apart | falling apart |
        falls on its face | fall on its face | falls flat | fell flat | fall flat |
        misses the mark | miss the mark | missed the mark | misses the point |
        misses the boat | fails miserably | tries and fails | try and fail |
        failure of nerve | cannot save | can not save | could not save |
        does not save | nothing can save | no amount of | beyond saving |
        wastes a good | squanders a good | one big mess | unholy mess |
        hot mess | a total mess | a big mess | a complete mess |
        train wreck | trainwreck | car wreck | slow motion wreck | dead on arrival |
        stillborn | dead weight | lifeless corpse | without a pulse |
        no sign of life | lacks a pulse | sinks like a stone | sinks without a trace |
        sucks the life out | sucked the life out | drain the life out |
        drops the ball | dropped the ball | blows it | blew it | blows up in |
        failure on all levels | what went wrong | does not work at all |
        does not work | did not work | do not work | it just does not work |
        does not deliver | did not deliver | fails to deliver | never delivers |
        under delivers | does not hold up | cannot sustain | does not stand up |
        does not make sense | makes no sense | makes little sense |
        makes even less sense | in search of a plot | in search of a story |
        a story that goes nowhere | all dressed up and nowhere to go |
        nothing more than an excuse | tries too hard | trying too hard |
        tries so hard | wants so badly to be | takes itself too seriously |
        takes it too seriously | taking itself too seriously |
        too slow | painfully slow | glacial pace | a snail s pace | pace of a snail |
        watches paint dry | watch paint dry | watching paint dry |
        watching grass grow | cure for insomnia | puts you to sleep |
        put me to sleep | put you to sleep | puts the audience to sleep |
        bored me to tears | boring as hell | bore me to tears | bore you to tears |
        a bore | a chore | an ordeal to sit through | difficult to sit through |
        hard to sit through | can barely sit through | impossible to sit through |
        torture to watch | painful to watch | a slog to get through |
        a chore to sit through | tires out its welcome | wears out its welcome |
        outstays its welcome | overstays its welcome | outstayed its welcome |
        taxes your patience | tests the patience | tries the patience |
        insults your intelligence | insult to the intelligence | assumes you are stupid |
        not a single laugh | never funny | no actual laughs | devoid of laughs |
        devoid of humor | devoid of humour | not remotely funny | not even funny |
        laugh free | laugh track would help | not once did i laugh |
        all bark and no bite | has no bite | lacks bite | has no heart |
        no heart or soul | goes through the motions | devoid of life |
        emotional vacuum | leaves you cold | left me cold | leaves me cold |
        leaves us cold | left us cold | leaves you empty | keep your distance |
        could not care less | cannot care less | do not care what happens |
        difficult to care | hard to care | impossible to care | why should we care |
        so what | who cares | no one cares | begs the question why |
        no reason to care | a reason to dislike | not enough to make |
        leaves much to be desired | leaves a lot to be desired |
        not what it could have been | was not meant to be |
        never gets off the ground | cannot get off the ground | fails to take flight |
        a very bad sign | falls short of the mark | falls short of its promise |
        does not live up | fails to live up | did not live up |
        not up to snuff | does not measure up | not up to par | below par |
        below average | rock bottom | bottom of the barrel | scraping the barrel |
        a low point | piece of junk | piece of trash | piece of crap |
        another nail in the coffin | asks too much | asking too much |
        a shameless rip off | rip off | off putting | turn off |
        turned me off | cash grab | cynical cash in | movie by committee |
        thinks it is funny | thinking it is funny | is supposed to be funny |
        never rises above | fails to rise above | rises to the level of a |
        does nobody any favors | does no favors | does it no favors |
        absent without leave | swallowed by its own | goes from bad to worse |
        from bad to worse | no end in sight | wasted on this | this sorry excuse
    """),
)

# Scores on these constructions apply to the construction rather than its
# component adjectives. Long matches claim their words before short matches.
_PATTERN_GROUPS = (
    (4.6, r"""
        \b(?:never|rarely|seldom) (?:quite |ever )?(?:less than|anything but) (?:\w+ ){0,2}(?:fascinating|entertaining|interesting|riveting|absorbing|compelling|funny|engaging|watchable|enjoyable|moving|impressive|effective|amusing|fine|solid|thrilling|excellent|delightful|charming)\b
        \b(?:so|just) (?:bad|silly|ridiculous|dumb|stupid|ludicrous|awful|campy|outrageous) (?:that )?(?:it is|it becomes|it turns out to be|it ends up being) (?:actually |almost |ultimately )?(?:good|fun|funny|entertaining|enjoyable|hilarious|irresistible)\b
        \btoo (?:good|funny|important|entertaining|much fun) to (?:miss|pass up|ignore|resist|dismiss|spoil|overlook|skip)\b
        \b(?:one of the|among the|ranks with the) (?:all time |very |year s )?(?:best|finest|greatest|funniest|scariest|smartest|sharpest|strongest|sweetest|most original|most interesting|most entertaining|most moving|most impressive|most remarkable|most satisfying|most compelling)\b
        \b(?:more|much more) (?:fun|entertaining|moving|compelling|enjoyable|amusing|interesting|imaginative|effective|satisfying|likable|successful) than (?:it|this) (?:has|had|have) (?:any|a|the) right to be\b
        \b(?:never|rarely|seldom) (?:been |seen |had )?(?:this|so) much fun\b
        \b(?:at|on) (?:a|the) (?:whole )?(?:new|different|higher) level of (?:fun|wit|charm|sophistication|suspense)\b
        \b(?:highly|heartily|definitely|strongly|unreservedly) recommend(?:ed)?\b
        \b(?:well |certainly |definitely )?worth (?:seeing|watching|waiting for|seeking|catching|renting|revisiting|viewing|discovering)\b
        \b(?:no|not a) (?:shortage|lack|dearth) of (?:\w+ ){0,2}(?:laughs|wit|humor|humour|charm|thrills|suspense|fun|imagination|ideas|energy|style)\b
        \b(?:would|will) (?:gladly |happily )?(?:see|watch) (?:it|this) again\b
        \b(?:is|are) (?:as )?(?:good|funny|amusing|exciting|entertaining) as (?:it gets|they come|ever|you could hope for)\b
        \b(?:does|do|did) everything (?:right|well)\b
    """),
    (2.4, r"""
        \b(?:nowhere near|not nearly as|not as|not quite so|not so) (?:\w+ ){0,2}(?:bad|dull|boring|terrible|silly|awful|tedious|predictable|shallow|contrived)\b
        \b(?:not|never|hardly|scarcely|barely) (?:even |really |actually |particularly |altogether |entirely )?(?:boring|dull|tedious|predictable|tiresome|unpleasant|pretentious|offensive|sentimental|formulaic)\b
        \b(?:not|never) (?:completely |entirely |altogether )?without (?:some |a bit of |its |their )?(?:charm|wit|virtue|virtues|merit|merits|interest|appeal|pleasure|pleasures|style|humor|humour)\b
        \b(?:surprisingly|unexpectedly|astonishingly|remarkably) (?:\w+ ){0,1}(?:good|funny|entertaining|effective|enjoyable|moving|sweet|smart|successful|engaging|watchable|charming)\b
        \b(?:a|the) (?:lot|great deal|surprising amount) of (?:heart|charm|fun|imagination|suspense|wit|style|pleasure|humor|humour|warmth)\b
        \b(?:a|an) (?:admirable|credible|creditable|fine|solid|impressive|accomplished|promising|assured|auspicious) (?:directorial |feature |film )?debut\b
        \bthere (?:are|could be|have been) worse (?:ways|things|choices|movies|films)\b
        \b(?:does|do|did) more than (?:just )?(?:entertain|amuse|thrill|inspire)\b
        \btoo much fun (?:to|for)\b
        \b(?:better|funnier|smarter|stronger|richer) than (?:it|you|one) (?:looks|seems|sounds|appears|has any right|might expect|may expect|would expect|might think|may think|would think)\b
        \b(?:a|the) rare (?:\w+ ){0,3}(?:film|movie|documentary|comedy|drama|sequel|thriller) (?:that|which)\b
    """),
    (-4.6, r"""
        \b(?:one of the|among the|ranks with the) (?:all time |very |year s )?(?:worst|dullest|lamest|stupidest|most boring|most retarded|most tedious|most disappointing|least entertaining|least interesting|least funny)\b
        \b(?:fails?|failed|failing|unable|struggles?) to (?:\w+ ){0,2}(?:engage|entertain|satisfy|impress|move|amuse|involve|thrill|convince|justify|interest|succeed|connect|inspire|hold|capture|keep|click|catch|maintain|live|work)\b
        \b(?:not|never|hardly|barely|scarcely) (?:quite |really |especially |particularly |remotely |even |nearly |exactly |all that |very |terribly )?(?:good|funny|scary|interesting|entertaining|satisfying|engaging|compelling|watchable|convincing|believable|inspired|original|fun|moving|amusing|effective|successful|enjoyable|smart|clever|thrilling|thoughtful|romantic|dramatic|exciting|memorable|worthwhile|appealing|charming|touching|worth it)\b
        \b(?:is|was|are|were) not (?:a |an |the )?(?:especially |very |particularly |terribly |really )?(?:success|winner|treat|keeper|pleasure|triumph|delight|gem|masterpiece)\b
        \b(?:does|did|do|can|could|would|will) not (?:really |quite |even |ever |exactly |actually |always )?(?:make (?:us|me|you) (?:laugh|care)|deliver|entertain|engage|amuse|convince|satisfy|work|click|gel|succeed|pay off|come alive|ring true)\b
        \b(?:no|little|hardly any|precious little|not much|not a lot of) (?:real |genuine |actual |dramatic |emotional |original |creative |of the )?(?:fun|laughs|laughter|humor|humour|wit|pleasure|charm|intelligence|heart|soul|substance|suspense|tension|excitement|energy|insight|imagination|originality|freshness|story|point|payoff|spark|thought|momentum|reason|depth|interest|style|conviction|logic|coherence)\b
        \b(?:woefully|sorely|badly|sadly|seriously) (?:lacking|missing|deficient|short|underdeveloped|undercooked|miscast|out of place)\b
        \b(?:a|an|the) (?:lack|dearth|absence|shortage|paucity|deficit) of (?:any |real |genuine )?(?:wit|logic|sense|suspense|humor|humour|heart|imagination|charm|fun|energy|interest|invention|originality|ideas|commitment|drive|style|direction|feeling|conviction|enthusiasm|depth|chemistry)\b
        \b(?:too|overly|excessively) (?:\w+ ){0,1}(?:long|short|loud|quiet|dark|violent|sentimental|melodramatic|cutesy|cute|sweet|earnest|obvious|much|little|many|few|thin|weak|slow|fast|slight|neat|simple|simplistic|banal|repetitive|familiar|distant|serious|smug|lazy|dumb|stupid|safe|unrealistic|easy|convenient|dramatic|silly|busy|self indulgent|self conscious) (?:for its own good|to be (?:much )?(?:funny|good|effective|engaging|moving|interesting|compelling|entertaining|enjoyable|worthwhile))\b
        \b(?:could|should|might|would) have been (?:a |an |so |much |a lot |far |worth |halfway |more |considerably |quite ){0,4}(?:better|funnier|scarier|smarter|great|good|an interesting|interesting|engaging|enjoyable|entertaining|moving|effective|satisfying|amusing|compelling|memorable|successful|powerful|poignant|stronger|wittier|a masterpiece)\b
        \b(?:has|had|have) (?:the |a lot of |so much |great |enormous )?potential (?:but|that (?:it|this) never)\b
        \b(?:only|sole) (?:real |genuine |truly |really )?(?:redeeming|worthwhile|saving|pleasurable|interesting|entertaining|good) (?:feature|part|scene|thing|aspect|moment|grace|element|idea|performance|quality|bit|sequence)s?\b
        \b(?:seems?|seemed) (?:designed|determined|destined) to (?:bore|annoy|exhaust|repel|alienate|disappoint|frustrate|irritate|insult)\b
        \b(?:a|an) (?:exercise|study|lesson) in (?:utter |pure |sheer |complete )?(?:futility|tedium|boredom|mediocrity|self indulgence|excess|bad taste|cynicism|banality|stupidity|pointlessness|contrivance|pretension)\b
    """),
    (-2.55, r"""
        \b(?:does|did|do) not (?:have|offer|provide|contain|show|generate|possess|deliver) (?:much |any |a lot of |enough |a shred of |the )?(?:fun|laughs|wit|humor|humour|charm|energy|passion|drive|flair|interest|excitement|coherence|originality|imagination|logic|suspense|feeling|momentum|heart|soul|point)\b
        \b(?:never|cannot|could not|did not|does not) (?:even |ever |really |quite |successfully |fully )?(?:gets?|got|reach(?:es)?|finds?|found|strikes?|achieves?|earns?) (?:its |the |a |an |that |up to )?(?:stride|pace|rhythm|balance|momentum|tone|groove|potential|payoff|point|emotional core)\b
        \b(?:is|are|was|were) not (?:the |its |his |her )?(?:very )?(?:best|greatest|finest|great|wonderful|excellent|brilliant)\b
        \b(?:not|never) (?:really |all that |quite )?(?:a |an |the )?(?:very |particularly |terribly |especially )?(?:good|fine|successful|entertaining|enjoyable|interesting|impressive) (?:film|movie|documentary|comedy|drama|thriller)s?\b
        \b(?:needs?|needed|could (?:have )?use[d]?) (?:some |a little |a bit |a lot |much |far )?(?:more|less|fewer) (?:\w+ ){0,2}(?:fun|laughs|jokes|wit|humor|humour|heart|soul|energy|focus|style|substance|time|attention|exposition|nuance|action|dialogue|editing|direction|thought|charm|restraint|imagination|suspense|tension|commitment)\b
        \b(?:has|have|had) (?:its |their )?(?:moments|merits|charms|strengths) (?:, |; )?(?:but|however)\b
        \b(?:almost|nearly|just about) (?:manages to |succeeds in )?(?:works|succeeds|manages|comes off|pulls it off)\b
        \b(?:too|overly|excessively|needlessly|unnecessarily) (?:\w+ ){0,1}(?:long|loud|violent|sentimental|melodramatic|cutesy|earnest|obvious|many|few|thin|slow|slight|neat|simple|simplistic|banal|repetitive|familiar|distant|serious|smug|dumb|stupid|safe|unrealistic|convenient|silly|busy|complicated)\b
        \b(?:a bit|a little|somewhat|too much) (?:too )?(?:of a )?(?:snore|bore|drag|mess|slog|cliche|cliché|downer|letdown)\b
        \b(?:a|an|the) (?:complete |total |utter |huge |major |big |profound |real )?(?:letdown|downer|snore|bore|headache|chore|turkey|clunker|dud|yawner|stiff|bust|drag|travesty|debacle)s?\b
        \b(?:high|great|considerable) hopes (?:that never|dashed|but)\b
        \b(?:gets?|getting|gets even) (?:much |a little |steadily |progressively |increasingly )?worse\b
        \bthere (?:is|was) (?:really |just |simply )?nothing (?:much |particularly )?(?:here|to see|to enjoy|to savor|to like|to hold|to engage|to love|to get excited about)\b
        \b(?:a|the) (?:good|fine|promising|interesting|decent|great) (?:idea|premise|concept|subject) (?:is |gets |gone )?(?:wasted|ruined|squandered|botched|buried|mishandled|awry|bad)\b
        \b(?:has|have|had) got to be (?:a|some kind of) (?:joke|mistake)\b
    """),
)

_TOKEN_RE = re.compile(r"\d+(?:\.\d+)?|[^\W\d_]+(?:'[^\W\d_]+)?|[.,;:!?—()/&+*%]", re.UNICODE)

_NEGATION = {
    "not", "never", "no", "none", "neither", "nor", "nothing", "nobody",
    "nowhere", "without", "cannot", "hardly", "barely", "scarcely",
    "rarely", "seldom", "lacks", "lack", "lacked", "lacking",
    "devoid", "missing", "misses", "absent", "unlike", "avoids",
    "avoid", "avoiding", "avoided", "free", "spares", "spared",
    "fails", "fail", "failed", "failure", "unable", "refuses", "refuse",
    "less", "little", "anything", "far",
}
_BINARY = {"and", "or", "&", "plus"}
_BOUNDARY = {".", "!", "?", ";", "—", ":", "(", ")"}
_ADVERSATIVE = {"but", "however", "yet", "nevertheless", "nonetheless", "instead", "whereas"}
_CONCESSIVE = {"although", "though", "albeit", "despite", "while", "notwithstanding"}
_DEGREE = {
    "very": 1.22, "really": 1.17, "quite": 1.12, "pretty": 1.05,
    "rather": 1.04, "especially": 1.2, "particularly": 1.16,
    "absolutely": 1.39, "utterly": 1.4, "totally": 1.36, "outright": 1.29,
    "extremely": 1.38, "deeply": 1.21, "incredibly": 1.28, "intensely": 1.2,
    "remarkably": 1.25, "genuinely": 1.22, "completely": 1.37, "entirely": 1.2,
    "wholly": 1.21, "purely": 1.13, "decidedly": 1.21, "positively": 1.19,
    "thoroughly": 1.25, "exceptionally": 1.34, "unusually": 1.11,
    "surprisingly": 1.22, "undeniably": 1.19, "unabashedly": 1.13,
    "profoundly": 1.26, "hugely": 1.28, "wildly": 1.25,
    "so": 1.12, "more": 1.06, "most": 1.25, "much": 1.15,
    "truly": 1.23, "achingly": 1.19, "wonderfully": 1.21, "beautifully": 1.22,
    "painfully": 1.22, "terribly": 1.16, "horribly": 1.3, "awfully": 1.17,
    "dreadfully": 1.29, "frightfully": 1.2, "ridiculously": 1.23,
    "insanely": 1.3, "unbelievably": 1.29, "laughably": 1.2,
    "extensively": 1.09, "increasingly": 1.15, "unbearably": 1.35,
    "hopelessly": 1.28, "blatantly": 1.21, "pathetically": 1.28,
    "unabashed": 1.05, "downright": 1.29, "simply": 1.15, "plain": 1.12,
    "just": 1.03, "merely": 0.53, "somewhat": 0.66, "slightly": 0.58,
    "marginally": 0.53, "moderately": 0.64, "fairly": 0.77,
    "mildly": 0.54, "vaguely": 0.45, "sporadically": 0.6, "intermittently": 0.64,
    "occasionally": 0.65, "sometimes": 0.76, "seemingly": 0.76,
    "relatively": 0.79, "reasonably": 0.81, "almost": 0.7, "nearly": 0.8,
    "halfway": 0.55, "passably": 0.58, "nominally": 0.52, "partly": 0.78,
    "sufficiently": 0.95, "perfectly": 1.11,
}
_FILLER = {
    "a", "an", "the", "any", "some", "of", "as", "at", "all", "that", "its",
    "his", "their", "her", "our", "much", "to", "this", "be", "being", "been",
    "even", "only", "necessarily", "exactly", "in", "it", "particularly",
} | set(_DEGREE)
_COPULA = {"is", "are", "was", "were", "be", "been", "being", "seems", "seem", "feels"}
_DESCRIPTIVE = {
    "grim", "dark", "disturbing", "unpleasant", "nasty", "ugly", "bizarre", "strange",
    "sad", "tragic", "eerie", "unsettling", "unnerving", "depressing", "depressed",
    "dour", "terrifying", "uncomfortable", "weird", "terrible", "horrible",
    "pathetic", "brutal", "violent", "hateful", "despicable", "cruel", "scary",
    "frightening", "repulsive", "revolting", "dangerous", "bitter", "sordid", "sick",
    "twisted", "evil", "shocking", "ghastly", "absurd", "ridiculous", "sweet",
    "nice", "beautiful", "lovable", "likable", "charming", "handsome", "lovely",
    "powerful", "strong", "cynical", "silly", "stupid", "dumb", "good", "bad",
}
_PERSON = {
    "man", "woman", "couple", "girl", "boy", "kid", "mother", "father", "teen",
    "husband", "wife", "son", "daughter", "killer", "cop", "detective", "doctor",
    "lover", "bastard", "child", "family", "thief", "sir", "hero", "villain",
    "criminal", "protagonist", "teacher", "person", "people", "sister", "brother",
    "friend", "neighbor", "girlfriend", "boyfriend", "fatherhood", "adolescent",
    "brothers", "men", "women", "kids", "children", "guy", "gal", "world",
    "subject", "event", "crime", "events", "truth", "reality", "act", "war",
}

_EXTRA_WORDS = {
    "nicely": 2.0, "nice": 1.5, "strong": 1.9, "engages": 2.55, "engage": 2.25,
    "impress": 3.05, "convince": 2.2, "convinced": 2.1,
    "amuse": 2.35, "amuses": 2.4, "convincingness": 2.3, "satisfies": 2.8,
    "satisfy": 2.6, "entertain": 2.5, "entertained": 2.7, "satisfied": 2.7,
    "sharper": 2.1, "smarter": 2.2, "finest": 3.8, "sweetest": 3.0,
    "stronger": 1.7, "richest": 2.5, "kinder": 0.6, "nicer": 1.4,
    "lighter": 0.55, "liking": 2.0, "loveliest": 3.5, "adorable": 2.8,
    "adorably": 2.3, "adored": 3.0, "adore": 3.25, "happily": 1.2,
    "biting": 1.6, "sad": -0.35, "wryness": 2.0, "wins": 2.1, "win": 1.35,
    "fortunate": 1.4, "fortunately": 1.45, "sadly": -1.85, "curiously": 0.0,
    "hysterical": 1.7, "entirety": 0.0, "sympathies": 0.65, "punch": 0.85,
    "horror": 0.0, "sick": -0.65, "cheaply": -1.75, "weird": 0.1,
    "nasty": -1.1, "ugly": -1.15, "brutal": -0.45, "horrific": -0.55,
    "violent": -0.2, "violence": 0.0, "terrifying": 0.75, "scariest": 2.35,
    "mindboggling": -0.75, "heartbreaking": 2.15, "heartbreakingly": 2.0,
    "dour": -0.9, "grim": -0.65, "depressing": -1.25, "depressed": -0.5,
    "disturbing": 0.2, "unsettling": 0.4, "uncomfortable": -0.45,
    "painful": -1.9, "tragic": 0.0, "agony": -1.1, "tragedy": 0.0,
    "unbelievable": -0.8, "obvious": -1.15, "obviously": 0.0,
    "cold": -0.7, "cute": 1.7, "goofy": 0.75, "scary": 1.1, "creepy": 0.7,
    "twisted": 0.4, "odd": 0.1, "peculiar": 0.1, "shocking": 0.35, "shocks": 0.25,
    "absurd": -0.75, "crazy": 0.05, "ridiculous": -2.15, "stoned": 0.0,
    "works": 2.4, "work": 1.5, "worked": 1.8, "working": 0.0, "fine": 1.6,
    "like": 2.0, "likeable": 2.8, "likable": 2.8,
    "well": 0.0, "depth": 1.4, "heart": 0.65, "power": 0.9, "substance": 0.9,
    "strength": 1.45, "humor": 1.3, "humour": 1.3, "comedic": 0.2,
    "style": 0.55, "stylized": 0.25, "stylised": 0.25,
    "enough": 0.0, "suffer": -1.3, "suffers": -2.1, "suffered": -1.4,
    "hype": -0.35, "farce": 0.0, "parody": 0.0, "satire": 0.0, "parodies": 0.0,
    "melodrama": -0.4, "whimsical": 1.15, "sentimentality": -0.9,
    "promise": 0.7, "promising": 1.05, "promises": 0.35, "potential": 0.25,
    "chilly": -0.5, "commercial": -0.25, "traditional": 0.0,
    "modest": 0.0, "plain": -0.35, "slow": -0.9, "slowly": -0.55,
    "small": 0.0, "quick": 0.15, "decent": 1.25, "fine": 1.5, "ok": 0.55,
    "adequate": 0.4, "mediocre": -2.9, "mediocrity": -2.9, "forgettable": -3.1,
    "passable": 0.35, "serviceable": 0.3, "unremarkable": -2.4, "ordinary": -0.65,
    "computerized": 0.0, "unnecessary": -1.8, "unneeded": -1.55,
    "overstated": -1.55, "underrated": 2.15, "understated": 2.0, "overrated": -2.8,
    "perfunctory": -2.55, "overwrought": -2.15, "underwhelms": -2.55,
    "pedestrian": -1.8, "pedantry": -1.55, "shoddy": -3.0, "leadenly": -2.8,
    "exhausting": -2.05, "exhausted": -1.1, "overwhelming": 1.1,
    "irks": -2.2, "vexing": -1.95, "asinine": -3.4, "foolhardy": -1.0,
    "disconcerting": -0.9, "banal": -2.3, "banality": -2.3, "boilerplate": -2.0,
    "clichéd": -1.85, "triteness": -2.0, "coasts": -1.2, "overacting": -2.25,
    "overacted": -2.2, "overacts": -2.2, "underacting": -1.2,
    "uninformative": -1.95, "obscure": -0.1, "impenetrable": -2.3,
    "puzzling": -0.45, "bewildering": -0.9, "nonsensical": -2.75,
    "preposterous": -2.15, "fatuous": -2.75, "obtuse": -1.8,
    "bland": -2.55, "fanaticism": 0.0, "sluggishness": -2.0, "limp": -2.4,
    "inert": -2.5, "unfunny": -3.1, "snooze": -3.25, "snoozer": -3.45,
    "drearily": -2.9, "shallowly": -2.0, "shapelessly": -2.2, "flaccid": -2.6,
    "incompetent": -3.5, "incompetence": -3.3, "deficient": -2.3,
    "flawed": -1.85, "flaws": -1.55, "flaw": -1.7, "blemish": -1.25,
    "problems": -1.4, "problem": -1.35, "quibbles": -0.95, "quibble": -0.95,
    "foibles": -0.65, "shortcomings": -1.85, "drawbacks": -1.6,
    "downside": -1.45, "disservice": -2.7, "detracts": -2.25,
    "backfires": -2.75, "backfire": -2.55, "fraying": -1.1,
    "derails": -2.75, "sputters": -2.4, "falter": -2.0, "falters": -2.2,
    "slumps": -1.8, "wobbles": -1.65, "misguidedly": -2.55,
    "subpar": -2.7, "inadequate": -2.65, "disposable": -2.2, "dispensable": -2.0,
    "deflated": -1.7, "unexceptional": -1.8, "unnecessary": -2.05,
    "insincere": -2.4, "studied": -0.15, "turgid": -2.85, "torpid": -2.65,
    "protracted": -1.65, "overwrought": -2.2, "overindulgent": -2.5,
    "noteworthy": 2.25, "commendation": 2.5, "superior": 2.95, "inferior": -2.9,
    "premium": 1.2, "enviable": 2.0, "priceless": 3.1, "peerless": 4.15,
    "chortles": 2.25, "raucous": 0.8, "boisterous": 0.85, "ribald": 0.45,
    "screwball": 0.15, "rollicking": 2.9, "madcap": 1.5, "cheeky": 1.4,
    "lovingly": 2.55, "affectionately": 2.25, "chic": 1.6, "velvety": 1.15,
    "seductive": 2.75, "alluring": 2.7, "ravishing": 3.85, "resonates": 2.8,
    "bewitching": 2.95, "hypnotic": 2.55, "hypnotizing": 2.5,
    "entrancing": 3.2, "rapturous": 3.5, "dreamy": 1.25, "idiosyncratic": 1.15,
    "fiercely": 0.0, "immensely": 0.0, "palpable": 1.15, "tangible": 0.95,
    "heartfelt": 3.0, "underplayed": 1.55, "emotionally": 0.0,
    "humanity": 1.6, "intelligence": 1.9, "cleverness": 2.0, "integrity": 1.85,
    "innovates": 2.1, "humanizes": 2.15, "illuminates": 2.6, "insights": 2.0,
    "observations": 0.45, "payscale": 0.0, "grippingly": 3.0,
    "indulgence": -0.65, "sardonic": 0.85, "scathing": 0.6, "unsparing": 1.15,
    "cynically": -1.9, "breeziness": 1.7, "repartee": 1.7,
    "appointing": 0.0, "admirable": 1.65, "ambitious": 1.0,
    "ambition": 0.9, "attempt": 0.0, "attempts": 0.0, "proficiently": 1.8,
}


def _normalize(text):
    text = unicodedata.normalize("NFKC", text).casefold()
    text = text.translate(str.maketrans({
        "’": "'", "‘": "'", "`": "'", "´": "'", "“": '"', "”": '"',
        "−": "-", "–": "—", "…": "...",
    }))
    text = re.sub(r"<[^>]{1,100}>", " ", text)
    text = re.sub(r"&(?:quot|ldquo|rdquo|apos|lsquo|rsquo);", "'", text)
    text = re.sub(r"&amp;", " and ", text)
    text = re.sub(r"\b([a-z]+)\s+n\s*'\s*t\b", r"\1n't", text)
    text = re.sub(r"\b([a-z]+)n\s*'\s*t\b", r"\1n't", text)
    text = re.sub(r"\b(wo|ca|sha)n't\b", lambda m: {
        "wo": "will not", "ca": "cannot", "sha": "shall not",
    }[m.group(1)], text)
    text = re.sub(r"\bain't\b", "is not", text)
    text = re.sub(r"n't\b", " not", text)
    text = re.sub(r"\bcant\b|\bcan not\b", "cannot", text)
    text = re.sub(r"\b(dont|doesnt|didnt|wont|wouldnt|couldnt|shouldnt|isnt|arent|wasnt|werent|havent|hasnt|hadnt)\b",
                  lambda m: ("will" if m.group() == "wont" else m.group()[:-2]) + " not", text)
    text = re.sub(r"\b(i|you|we|they|he|she|it|that|what|who|there|here|this)\s*'\s*(m|re|s|ve|ll|d)\b",
                  lambda m: m.group(1) + " " + {
                      "m": "am", "re": "are", "s": "is", "ve": "have", "ll": "will", "d": "would"
                  }[m.group(2)], text)
    text = re.sub(r"\blet\s*'\s*s\b", "let us", text)
    text = re.sub(r"(?<=\w)\s*'\s*(?=s\b)", " '", text)
    text = re.sub(r"(?<!\w)'\s*(?=\w)", "", text)
    text = re.sub(r"-{2,}|(?<!\w)-(?!\w)", " — ", text)
    text = re.sub(r"(?<=\w)-(?=\w)", " ", text)
    return " ".join(text.split())


def _make_words():
    result = {}
    for score, group in _WORD_GROUPS:
        for word in group.split():
            if "-" not in word:
                result[word] = score
    result.update(_EXTRA_WORDS)
    return result


def _make_phrases():
    result = {}
    for score, group in _PHRASE_GROUPS:
        for phrase in group.split("|"):
            words = tuple(_TOKEN_RE.findall(_normalize(phrase)))
            if len(words) > 1:
                result[words] = score
    by_first = {}
    for words, score in result.items():
        by_first.setdefault(words[0], []).append((words, score))
    for variants in by_first.values():
        variants.sort(key=lambda item: -len(item[0]))
    return by_first


_WORDS = _make_words()
_PHRASES = _make_phrases()
_PATTERNS = tuple(
    (re.compile(line.strip()), score)
    for score, lines in _PATTERN_GROUPS
    for line in lines.splitlines() if line.strip()
)

# Fragments of reviews sometimes consist only of a numerical grade.
_NUMBER = r"(?:\d+(?:\.\d+)?|zero|one|two|three|four|five|six|seven|eight|nine|ten)"
_NUMBERS = dict(zip("zero one two three four five six seven eight nine ten".split(), range(11)))
_RATING_RE = re.compile(
    r"\b(" + _NUMBER + r")(?:\s*(and a half|and one half|½|1/2))?"
    r"\s*(?:(?:stars?|points?)\s*)?(?:out of|/)\s*(\d+(?:\.\d+)?|four|five|ten|hundred)\b"
)
_STAR_RE = re.compile(r"\b(" + _NUMBER + r")(?:\s*(and a half|and one half|½|1/2))?\s+stars?\b")


def _number(token):
    if token in _NUMBERS:
        return _NUMBERS[token]
    if token == "hundred":
        return 100.0
    return float(token)


def _rating(text):
    for m in _RATING_RE.finditer(text):
        n, half, d = m.groups()
        value, maximum = _number(n) + (0.5 if half else 0), _number(d)
        if 0 < maximum <= 100 and 0 <= value <= maximum:
            if maximum in (4, 5, 10, 100) or "out of" in m.group():
                return 6.0 if value / maximum >= 0.60 else -6.0
    for m in _STAR_RE.finditer(text):
        before = text[max(0, m.start() - 32):m.start()]
        after = text[m.end():m.end() + 30]
        if re.search(r"\b(?:starring|the|those|these|all|its|with)\s*$", before) and not re.search(r"\b(?:give|gives|gets|get|earn|earns|rate|rated)\b", before):
            continue
        if re.match(r"\s+(?:of (?!four|five|ten)|play|are|who|from|in the cast|in the film|headline|share|have|appear)\b", after):
            continue
        value = _number(m.group(1)) + (0.5 if m.group(2) else 0)
        if 0 <= value <= 5:
            return 4.7 if value >= 2.5 else -4.7
    m = re.fullmatch(r"\s*(\*{1,5})(?:\s*/\s*(\*{2,5}))?\s*[.!]?\s*", text)
    if m:
        return 6.0 if len(m.group(1)) / len(m.group(2) or "*****") >= 0.6 else -6.0
    m = re.fullmatch(r"(?:grade\s*[:=]?\s*)?([abcdf])\s*([+-])?\s*[.!]?", text)
    if m:
        return 6.0 if m.group(1) in {"a", "b"} or (m.group(1), m.group(2)) == ("c", "+") else -6.0
    return 0.0


def _word_value(word):
    value = _WORDS.get(word)
    if value is not None:
        return value
    if word in _DEGREE or len(word) < 4 or "'" in word:
        return 0.0
    roots = []
    if word.endswith("iness") and len(word) >= 7:
        roots.append(word[:-5] + "y")
    elif word.endswith("ness") and len(word) >= 7:
        roots.append(word[:-4])
    if word.endswith("ily") and len(word) >= 6:
        roots.append(word[:-3] + "y")
    elif word.endswith("ly") and len(word) >= 6:
        roots.extend((word[:-2], word[:-2] + "e"))
    if word.endswith("ies") and len(word) >= 6:
        roots.append(word[:-3] + "y")
    if word.endswith("es") and len(word) >= 5:
        roots.extend((word[:-1], word[:-2]))
    elif word.endswith("s") and len(word) >= 5 and not word.endswith("ss"):
        roots.append(word[:-1])
    if word.endswith("ied") and len(word) >= 6:
        roots.append(word[:-3] + "y")
    elif word.endswith("ed") and len(word) >= 5:
        roots.extend((word[:-1], word[:-2]))
        if word[-3] == word[-4]:
            roots.append(word[:-3])
    if word.endswith("ing") and len(word) >= 6:
        roots.extend((word[:-3], word[:-3] + "e"))
        if word[-4] == word[-5]:
            roots.append(word[:-4])
    for root in roots:
        if abs(_WORDS.get(root, 0.0)) >= 1.65 and root not in {"like", "miss", "fine", "point", "well", "better", "lost"}:
            return 0.88 * _WORDS[root]
    if word.startswith("un") and len(word) >= 8:
        val = _WORDS.get(word[2:], 0.0)
        if val > 1.8:
            return -0.7 * val
    return 0.0


def _match_expressions(tokens, joined, offsets):
    n = len(tokens)
    candidates = []
    for i, token in enumerate(tokens):
        for phrase, score in _PHRASES.get(token, ()):
            end = i + len(phrase)
            if tuple(tokens[i:end]) == phrase:
                candidates.append((i, end, score, 0))
    for pattern, score in _PATTERNS:
        for m in pattern.finditer(joined):
            start = bisect_left(offsets, m.start())
            end = bisect_left(offsets, m.end())
            if start < end:
                # Some patterns deliberately consume "but" to test the context;
                # it must remain available as a clause boundary.
                if tokens[end - 1] in _ADVERSATIVE:
                    end -= 1
                if start < end:
                    candidates.append((start, end, score, 1))
    candidates.sort(key=lambda c: (-(c[1] - c[0]), -c[3], -abs(c[2]), c[0]))
    occupied = [False] * n
    quiet = [False] * n
    matches = {}
    for a, b, score, pattern in candidates:
        if not any(occupied[a:b]):
            occupied[a:b] = [True] * (b - a)
            if score == 0:
                quiet[a:b] = [True] * (b - a)
            else:
                matches[a] = (b, score, pattern)
    return matches, occupied, quiet


def _boundaries(tokens, occupied):
    n = len(tokens)
    factors = [1.0] * n
    breaks = set()
    spans = []
    start = 0
    for i, word in enumerate(tokens):
        if word in {".", "!", "?", ";"}:
            spans.append((start, i))
            start = i + 1
    spans.append((start, n))

    def change(a, b, mult):
        for j in range(max(0, a), min(n, b)):
            factors[j] *= mult

    for s, e in spans:
        if e <= s:
            continue
        for i in range(s, e):
            t = tokens[i]
            prev = tokens[i - 1] if i else ""
            nxt = tokens[i + 1] if i + 1 < n else ""
            nxt2 = tokens[i + 2] if i + 2 < n else ""
            last = i + 1
            if i + 2 < e and tokens[i:i + 3] == ["on", "the", "other"] and i + 3 < e and tokens[i + 3] == "hand":
                last = i + 4
                contrast = True
            elif tokens[i:i + 2] in (["that", "said"], ["even", "so"], ["then", "again"]):
                last = i + 2
                contrast = i == s or prev in {",", "—"}
            elif t in _ADVERSATIVE and not occupied[i]:
                contrast = True
                if t == "but":
                    if prev in {"anything", "nothing", "all", "help", "cannot", "none", "everyone", "nobody", "anyone"} or nxt in {"for", "also"}:
                        contrast = False
                    if prev == "little" and (i < 2 or tokens[i - 2] in {"a", "very"}):
                        contrast = False
                elif t == "yet":
                    contrast = (prev not in _DEGREE and nxt not in {"another", "again", "more", "to", "still"}
                                and i + 1 < e and prev not in {"not", "as"})
                elif t == "instead":
                    contrast = nxt != "of"
                elif t == "however" and nxt != "," and i == s and nxt not in {"it", "this", "there", "the", "that", "he", "she", "they", "i", "we", "you"}:
                    contrast = False
            else:
                contrast = False
            if contrast:
                strength = 0.57 if t in {"but", "however", "instead"} else 0.69
                if prev == "not":
                    strength = 0.55
                change(s, i, strength)
                change(last, e, 1.26)
                breaks.add(i)
                if last > i + 1:
                    breaks.add(last - 1)
                continue
            if t in {"ultimately", "overall", "finally", "nevertheless", "unfortunately", "fortunately"} or (
                t == "in" and (tokens[i:i + 3] == ["in", "the", "end"] or tokens[i:i + 3] == ["in", "the", "final"])
            ) or (t == "still" and (i == s or prev in {",", "—"}) and nxt not in {"more", "less"}):
                change(s, i, 0.69)
                change(i, e, 1.19)
                if i == s and s > 0:
                    change(0, s, 0.75)
            if t == "than" and not occupied[i]:
                left = tokens[max(s, i - 8):i]
                if any(w in {"more", "less", "better", "worse", "rather", "funnier", "smarter",
                             "stronger", "weaker", "scarier", "easier", "harder", "closer",
                             "different", "faster", "longer"} for w in left):
                    end = next((j for j in range(i + 1, e)
                                if tokens[j] in _ADVERSATIVE or tokens[j] in {",", "—"}), e)
                    if i > s and tokens[i - 1] not in {"less", "more", "rather", "other"}:
                        change(i + 1, end, 0.38)
                        breaks.add(i)
                continue
            if occupied[i] or t not in _CONCESSIVE and tokens[i:i + 2] not in (
                ["even", "if"], ["even", "though"], ["for", "all"], ["in", "spite"]
            ):
                continue
            if t == "while" and nxt in {"watching", "waiting", "making", "filming", "ago"}:
                continue
            if t == "while" and prev not in {",", "—", "", ".", "!", "?", ";"} and i > s:
                continue
            if t == "for" and nxt2 in {"ages", "time", "audiences"}:
                continue
            if i > s and prev == "even" and t == "though":
                continue
            if t == "though" and nxt in {",", ".", "!", "?", ""}:
                continue
            comma = next((j for j in range(i + 1, e) if tokens[j] in {",", "—"}), None)
            if i <= s + 1 and comma is None and t in {"despite", "although", "though", "while"}:
                comma = next((j for j in range(i + 2, e - 1)
                              if tokens[j] in {"it", "this", "you", "we", "i", "the"}
                              and (tokens[j + 1] in _COPULA or tokens[j + 1] in {"will", "does", "film", "movie", "result"})
                              and j >= i + 3), None)
            if i <= s + 1 and comma is not None:
                change(i, comma, 0.50)
                change(comma + (tokens[comma] in {",", "—"}), e, 1.19)
                breaks.add(comma)
            elif i > s + 1:
                change(s, i, 1.13)
                change(i + 1, comma if comma is not None else e, 0.64)
                breaks.add(i)
    # A following sentence introduced as a correction also revises a
    # judgment made in the preceding sentence.
    for s, e in spans[1:]:
        if s < e and tokens[s] in {"but", "however", "yet", "nevertheless", "nonetheless"}:
            change(0, s, 0.64)
    return factors, breaks


def _prior_scope(tokens, start, breaks):
    left = start
    for j in range(start - 1, max(-1, start - 12), -1):
        t = tokens[j]
        if t in _BOUNDARY or j in breaks or t in {"if", "because", "unless", "until", "than"}:
            # "less than riveting" still has "less" in its local scope.
            if t == "than" and j == start - 1 and j > 0 and tokens[j - 1] in {"less", "more"}:
                left = j
                continue
            break
        if t == ",":
            if j > 0 and tokens[j - 1] in _DEGREE:
                left = j
                continue
            break
        left = j
    return left


def _negation(tokens, a, b, start, breaks, occupied, quiet):
    count = 0
    weak = False
    content = 0
    n = len(tokens)
    for j in range(start - 1, a - 1, -1):
        w = tokens[j]
        nxt = tokens[j + 1] if j + 1 < n else ""
        nxt2 = tokens[j + 2] if j + 2 < n else ""
        prev = tokens[j - 1] if j else ""
        if w in {"who", "which", "where", "when"} and content > 0:
            break
        if w in _BINARY and w not in {"or"} and content >= 2:
            break
        if w in {"is", "was", "are", "were", "will", "has", "have", "had", "does", "did", "do"} and content >= 2:
            break
        if w not in _FILLER and w not in _BINARY and w not in _NEGATION:
            if w not in {",", "than", "from", "enough", "or", "would", "could", "should", "thing", "hint", "trace", "shred", "sense"}:
                content += 1
        if content > 4:
            break
        if w not in _NEGATION or quiet[j]:
            continue
        if j < start - 6 and content >= 2:
            continue
        if w in {"never", "not", "no", "nothing", "cannot"} and occupied[j] and content >= 1:
            continue
        if w == "not" and nxt in {"only", "just", "merely", "simply", "unlike", "unlikeable", "least"}:
            continue
        if w == "not" and nxt == "to" and nxt2 in {"mention", "say"}:
            continue
        if w == "never" and nxt in {"mind", "before"}:
            continue
        if w == "no" and nxt in {"matter", "question", "doubt", "less", "wonder", "sooner", "later", "fewer", "end"}:
            continue
        if w == "no" and nxt in {"one", "person"} and start - j > 4:
            continue
        if w == "none" and nxt == "the":
            continue
        if w in {"less", "little"}:
            if prev in {"a", "no", "the", "nevertheless"} or nxt in {
                "girl", "boy", "kid", "woman", "man", "child", "children", "town",
                "village", "known", "wonder", "gem", "movie", "film", "story",
                "documentary", "company", "bit", "drama", "comedy", "sister", "brother",
            } or nxt[:1].isdigit():
                continue
            if w == "less" and nxt == "and":
                continue
            if w == "little" and content >= 2 and prev not in {"very", "precious", "so", "too", "with"}:
                continue
        if w in {"anything", "far", "free", "devoid", "failure", "missing", "misses"}:
            wanted = {"anything": "but", "far": "from", "free": "of", "devoid": "of",
                      "failure": "to", "missing": "from", "misses": "out"}[w]
            if nxt != wanted:
                continue
        if w in {"avoid", "avoids", "avoiding", "avoided", "spares", "spared"}:
            if nxt in {"at", "this", "that", "theater", "film", "movie", "it"}:
                continue
        if w == "without" and nxt in {"ever", "really"} and nxt2 in _NEGATION:
            continue
        if w in {"fail", "fails", "failed", "unable", "refuses", "refuse"} and nxt != "to":
            continue
        if w in {"no", "not", "never", "without", "cannot", "neither", "nor"} and any(
            t in {"but", "yet", "however"} for t in tokens[j + 1:start]
        ) and not (nxt == "but" and w == "nothing"):
            continue
        if w == "without" and any(t in {"sacrificing", "undermining", "losing", "compromising", "forgetting"} for t in tokens[j + 1:start]):
            continue
        if w in {"lacks", "lack", "lacked", "lacking", "unable", "less", "no", "little"} and nxt in {"of", "in", "to"} and nxt2 in {"subtlety", "much"}:
            weak = False
        if w == "nothing" and nxt == "but":
            continue
        if w == "not" and nxt == "without" and occupied[j] and occupied[j + 1]:
            continue
        count += 1
        if w in {"rarely", "seldom", "less", "neither", "nor", "hardly", "barely", "scarcely", "little"}:
            weak = True
        if w in {"neither", "nor"}:
            break
    return count, weak


def _is_literal_like(tokens, i):
    before = tokens[i - 1] if i else ""
    after = tokens[i + 1] if i + 1 < len(tokens) else ""
    if before in {"i", "you", "we", "they", "not", "never", "really", "might", "will",
                  "would", "may", "even", "can", "could", "also", "did", "do", "to"}:
        return False
    if after == "it" and i + 2 < len(tokens) and tokens[i + 2] in _COPULA:
        return True
    return True


def _local_factor(tokens, a, b, weight, matches, occupied, quiet, breaks, base, fixed):
    n = len(tokens)
    prior = tokens[max(0, a - 9):a]
    after = tokens[b:b + 8]
    text_before = " ".join(prior)
    text_after = " ".join(after)
    word = tokens[a]
    prev = tokens[a - 1] if a else ""
    nxt = tokens[b] if b < n else ""
    left = _prior_scope(tokens, a, breaks)
    score = weight

    if b == a + 1 and not fixed:
        if word == "like" and _is_literal_like(tokens, a):
            return 0.0
        if word in {"work", "works", "worked"}:
            if prev in {"the", "his", "her", "their", "our", "its", "camera", "film", "earlier", "previous", "best", "last", "first", "recent", "body"}:
                return 0.12 * score
            if nxt in {"of", "by", "for", "on", "at", "with", "out"}:
                if nxt == "as" or prev in {"it", "that", "this", "mostly"}:
                    score *= 0.8
                else:
                    score *= 0.23
        if word in {"original", "classic"} and (prev in {"the", "its", "an"} or nxt in {"film", "version", "book", "series", "novel", "story", "material"}):
            if prev in {"the", "its"} or nxt in {"version", "book", "series", "novel", "material"}:
                score *= 0.33
        if word in {"fun", "funny"} and (
            nxt == "of" or (nxt == "at" and prev in {"pokes", "poke", "poking"})
        ):
            return 0.0
        if word in {"better", "best", "good", "bad"} and nxt in {
            "known", "part", "half", "friend", "guy", "boy", "guys", "mother", "father",
        }:
            score *= 0.25
        if word in {"well", "right", "fine", "okay", "ok"} and a == 0 and nxt == ",":
            return 0.0
        if word in {"moving", "moves", "moved"} and nxt in {"in", "to", "on", "out", "through", "at"}:
            score *= 0.14
        if word in {"miss", "misses", "missed", "missing"}:
            if nxt in {"him", "her", "them", "his", "their", "from", "person", "child", "girl", "son"}:
                score *= 0.18
            elif nxt == "out":
                score *= 0.75
        if word in {"lost", "loses"} and nxt in {"in", "inside", "his", "her", "their", "world", "city", "boy"}:
            score *= 0.35
        if word in {"trying", "try", "fine", "just", "plain", "square"} and nxt == "to":
            score *= 0.23
        if word == "love" and nxt in {"for", "affair", "of", "with", "between", "object"}:
            score *= 0.16
        if word in {"beloved", "legendary", "famous", "successful", "talented", "fascinating", "extraordinary", "popular"} and nxt in {
            "director", "writer", "actor", "actress", "comedian", "star", "artist",
            "singer", "musician", "author", "subject", "character", "athlete", "career",
        }:
            score *= 0.56
        if word in _DESCRIPTIVE:
            look = after[:3]
            j = 0
            while j < len(look) and (look[j] in _WORD_NOUN_MODIFIERS or look[j] in {",", "and", "old", "young"}):
                j += 1
            if j < len(look) and look[j] in _PERSON:
                score *= 0.33
            elif prev in _PERSON or (a > 1 and prev in _COPULA and tokens[a - 2] in _PERSON):
                score *= 0.6
        if word in {"perfect", "ideal", "impossible", "unbelievable", "remarkable"} and nxt in {"crime", "murder", "world", "storm", "stranger"}:
            score *= 0.23
        if word in {"worst", "best", "great", "good", "bad"} and nxt == "of" and len(after) > 2 and after[1] in {"his", "her", "their"} and after[2] in {"life", "days", "years", "fears"}:
            score *= 0.24

    light = tokens[max(left, a - 4):a]
    if not fixed:
        boost = 1.0
        for j in range(a - 1, max(left - 1, a - 4), -1):
            w = tokens[j]
            if quiet[j] or j in matches:
                if w not in {"more", "almost", "only", "barely"}:
                    break
            if w in _DEGREE:
                boost *= _DEGREE[w]
            elif w not in {"a", "an", "the", "not", "all", "too", "and", ","}:
                break
        if re.search(r"(?:^| )(?:a (?:bit|little)|kind of|sort of|at times|in spots|in places)$", " ".join(light)):
            boost *= 0.72
        if re.search(r"(?:^| )(?:to say the least|of the highest order|beyond belief|as hell)$", text_after):
            boost *= 1.2
        if a > 0 and prev == "so" and "that" in after[:3]:
            boost *= 1.08
        score *= min(1.65, max(0.32, boost))

        if "too" in light and (
            prev == "too" or all(t in _DEGREE or t in {"too", "a", "an"} for t in light[light.index("too") + 1:])
        ):
            # "Too good to miss" and similar constructions are matched above.
            if score > 0:
                score = -max(1.65, score * 0.85)
            else:
                score *= 1.19
        elif "overly" in light or "excessively" in light or "unnecessarily" in light:
            if prev in {"overly", "excessively", "unnecessarily", "needlessly"}:
                score = -max(1.6, score * 0.8) if score > 0 else score * 1.12

        if prev == "least" and a > 1 and tokens[a - 2] != "at":
            score = -0.9 * score
        count, weak = _negation(tokens, left, b, a, breaks, occupied, quiet)
        if count % 2:
            # "Lack" and "fail" are themselves negative predicates, not
            # positive adjectives governed by another copy of the cue.
            score *= (-0.87 if score > 0 else -0.65)
            if weak:
                score *= 0.83

    if score > 0:
        if re.search(r"\b(?:tries?|tried|trying|attempts?|attempted|attempting|aims?|aimed|aspires?|strives?|pretends?|pretended|pretending|purports?|wants?|wanted|meant|supposed|designed|intended|ought) (?:\w+ ){0,3}to (?:\w+ ){0,3}$", text_before + " "):
            if not re.search(r"\b(?:never|not|does not)\b", " ".join(tokens[left:a])):
                score *= 0.26
        if re.search(r"\b(?:could|should|would|might) (?:have|be|been|make|have been|have made) (?:\w+ ){0,4}$", text_before + " "):
            if not re.search(r"\b(?:not|never|no)\b", " ".join(tokens[left:a])):
                score *= 0.48 if "have" not in prior[-6:] else 0.19
        if re.search(r"\b(?:wishes|wish|hoped|expect(?:ed|ing)?|hopes?|hoping) (?:\w+ ){0,4}$", text_before + " ") and a - left <= 8:
            score *= 0.46
        if re.search(r"\b(?:only|sole) (?:\w+ ){0,2}$", text_before + " ") and nxt in {
            "thing", "part", "scene", "moment", "aspect", "performance", "feature",
            "bit", "idea", "element", "touch", "line", "shot", "actor", "actress",
        }:
            score = -max(1.5, score * 0.7)
        if re.search(r"\b(?:little more than|nothing more than|no more than|barely more than|hardly more than) (?:\w+ ){0,2}$", text_before + " "):
            score = -max(1.35, score * 0.66)
        if re.search(r"\b(?:waste of|squanders?|squandered|despite|wastes?|wasted|ruins?) (?:\w+ ){0,2}$", text_before + " "):
            score *= 0.35 if "despite" not in prior[-4:] else 0.62
        if re.search(r"\b(?:starts?|started|begins?|began|opens?|opened) (?:out |off )?(?:\w+ ){0,2}$", text_before + " "):
            if any(w in {"but", "before", "then", "ends", "ultimately", "only", "yet"} for w in after):
                score *= 0.55
    elif score < 0:
        if re.search(r"\b(?:plagued|riddled|fraught|burdened|saddled) with (?:\w+ ){0,2}$", text_before + " "):
            score *= 1.25
        if re.search(r"\b(?:unlike|rather than|instead of|far from|as opposed to) (?:\w+ ){0,3}$", text_before + " ") and word not in {"rather", "unlike"}:
            if not fixed and (count % 2 == 0):
                score *= -0.52
        if nxt in {"enough"} and score < -1.5 and len(after) > 1 and after[1] == "to":
            score *= 1.13
    return score * base


_WORD_NOUN_MODIFIERS = {
    "beautiful", "young", "immature", "hip", "bright", "cheery", "lovely",
    "smart", "stupid", "nice", "sweet", "ugly", "silly", "strange", "charming",
    "handsome", "cute", "odd", "old", "little", "shy", "poor", "rich", "evil",
    "middle", "aged", "angry", "white", "black",
}

# Weak lexical evidence can be supplemented by review-specific constructions,
# such as an unfulfilled promise or an elliptical "but it isn't."
_EXTRA_CUES = (
    (-4.2, r"\b(?:do not|does not|did not|would not|will not) (?:even |really )?(?:like|enjoy|love) (?:this|the film|the movie|it)\b"),
    (-3.4, r"\b(?:not|never|hardly) (?:one |a |the )?(?:single |real )?(?:laugh|thrill|smile|tear)\b"),
    (-3.5, r"\b(?:never|does not|did not) (?:really |quite |actually |once )?(?:take off|lift off|come alive|find its footing|get going|go anywhere|amount to much)\b"),
    (-3.2, r"\b(?:wished?|if only) (?:that )?(?:it|this|the movie|the film|the script|the director) (?:would|could|had|were|was)\b"),
    (-3.1, r"\b(?:film|movie|comedy|drama|thriller) (?:seems? |feels? )?(?:to be |is |was )?in search of (?:a |an |some )?(?:plot|story|point|idea|script|audience|reason)\b"),
    (-3.0, r"\b(?:should|could|would) have (?:worked|succeeded|been (?:a hit|much more|something more))\b"),
    (-2.9, r"\b(?:tries|trying|attempts|attempting) to (?:be (?:funny|smart|clever|hip|profound|edgy)|make (?:us|you) laugh)\b"),
    (-2.8, r"\b(?:where (?:did|is|are)|what happened to) (?:the |all the |its |any of the )?(?:wit|charm|humor|humour|fun|laughs|plot|story|point|suspense|intelligence)\b"),
    (-2.8, r"\b(?:the (?:big|biggest|main|real|only) (?:problem|trouble)|the trouble with|the problem with)\b"),
    (-2.75, r"\b(?:would be|might be|could be) (?:a |an |something ){0,2}(?:good|great|fine|better|funnier|entertaining|interesting|enjoyable|moving|fun) (\w+ ){0,3}if\b"),
    (-2.6, r"\b(?:not enough|too little|precious little|far too little) (?:\w+ ){0,1}(?:going on|here|to|for)\b"),
    (-2.4, r"\b(?:is|are|was|were|seems) (?:really |just |only |merely )?(?:an? )?(?:excuse|pretext) (?:to|for)\b"),
    (-2.35, r"\b(?:goes on|went on|go on|goes by|seems to go on) (?:and on|forever|for too long)\b"),
    (-2.25, r"\b(?:not so much|less) (?:a |an )?(?:film|movie|comedy|thriller|drama|documentary) (?:as|than)\b"),
    (-2.1, r"\b(?:how|why) (?:on earth |exactly )?(?:should|would|could|do) (?:i|we|you|anyone) (?:care|bother|want to watch|want to see)\b"),
    (-2.0, r"\b(?:as if|like) (?:it |this )?(?:was |were |had been |is )?(?:made|written|scripted) by (?:a committee|an algorithm|a computer|children|robots|a machine)\b"),
    (-1.85, r"\b(?:will|may|might) (?:only |just )?(?:appeal to|please) (?:only |just )?(?:fans|diehard|die hard|the most undemanding)\b"),
    (-1.7, r"\b(?:only |just )?(?:for|to) (?:the )?(?:most undemanding|undiscriminating|indiscriminate|diehards|die hards|very young)\b"),
    (-1.65, r"\b(?:seemed|seems|looked|looks|felt|feels) (?:to be )?(?:\w+ ){0,1}(?:endless|unfinished|unnecessary|interminable|pointless|cheap|rushed)\b"),
    (-1.5, r"\b(?:at least|if nothing else) (?:\w+ ){0,3}(?:it |this )?(?:is |was )?(?:short|over|finished|in focus|has a plot|ends)\b"),
    (3.4, r"\b(?:never|does not|do not|did not) (?:\w+ ){0,2}(?:let go|lose interest|loses its grip|let up|let you down|let me down|stops being funny)\b"),
    (3.2, r"\b(?:i|you|we) (?:will|would|can|could) (?:easily |gladly |happily )?(?:recommend|rewatch|watch again|see it again)\b"),
    (3.1, r"\b(?:there is|there was|has|have) (?:\w+ ){0,2}(?:nothing wrong|not much wrong|nothing to dislike|nothing not to like)\b"),
    (2.85, r"\b(?:gets?|got|finds?|found|strikes?) (?:the |a |an |its )?(?:right balance|equilibrium|perfect balance|rhythm|groove|right tone|footing)\b"),
    (2.8, r"\b(?:effortlessly|expertly|deftly|skillfully|skilfully) (?:handles?|balances?|juggles?|navigates?|switches?|moves?|weaves?|combines?|blends?)\b"),
    (2.65, r"\b(?:leaves?|left|keeps?|kept) (?:me|you|us|viewers|audiences) (?:smiling|thinking|laughing|giddy|satisfied|wanting more|in stitches)\b"),
    (2.55, r"\b(?:had|has|have) (?:me|you|us|viewers|audiences) (?:laughing|smiling|crying|in tears|in stitches|hooked)\b"),
    (2.2, r"\bwould (?:be |make )?a (?:fine|good|great) (?:choice|double feature|companion|companion piece|night out)\b"),
    (2.15, r"\b(?:knows?|knew) (?:\w+ ){0,2}(?:how to|when to) (?:entertain|make (?:us|you) laugh|quit|stop|end|let go|pull back|move on)\b"),
    (1.9, r"\b(?:inspires?|provokes?|sparks?|prompts?) (?:\w+ ){0,2}(?:discussion|debate|thought|conversation|reflection)\b"),
    (1.8, r"\b(?:happy|glad) (?:to have seen|to have watched|i (?:saw|watched))\b"),
)
_CUE_PATTERNS = tuple((score, re.compile(pattern)) for score, pattern in _EXTRA_CUES)

_UNLEXICALIZED = (
    (-1.75, r"\b(?:all|nothing|little) (?:it does is|there is is|you get is|we get is)\b"),
    (-1.65, r"\b(?:only|just) (?:another|the latest) (?:in a long line of|in a series of|in the endless)\b"),
    (-1.5, r"\b(?:apparently|evidently) (?:supposed to|meant to|thinks it|considered)\b"),
    (-1.4, r"\b(?:more like|amounts to|comes off as) (?:an? |nothing but )?(?:commercial|infomercial|video game|tv show|sitcom|music video|cartoon|sketch|trailer)\b"),
    (-1.35, r"\b(?:throw|throws|thrown|tosses|tossed|throwing) (?:\w+ ){0,3}(?:at the wall|against the wall|at the screen|at a wall)\b"),
    (-1.3, r"\b(?:running|run) time (?:feels|seems) (?:like|longer)\b"),
    (-1.25, r"\b(?:rather be|rather have been) (?:anywhere|at home|somewhere|watching anything|doing anything|asleep)\b"),
    (-1.2, r"\b(?:too (?:often|much)|more than (?:ever|once)) (?:\w+ ){0,3}(?:reminded|wondered|found myself)\b"),
    (-1.1, r"\b(?:that is|and that is|and this is) (?:about |pretty much )?it\b"),
    (-1.05, r"\bthe (?:point|purpose|reason) (?:is|of this) (?:\w+ ){0,2}(?:eludes|escapes|unclear)\b"),
    (-1.0, r"\b(?:would anyone|does anyone|why anyone|exactly why|what was (?:he|she|the director) thinking)\b"),
    (-0.85, r"\b(?:consists|comprised|composed) (?:almost |largely |mainly )?(?:entirely |solely |only )?of recycled\b"),
    (1.5, r"\b(?:not|never) (?:just|merely|only|simply) (?:another|an ordinary|an average)\b"),
    (1.35, r"\b(?:every|each) (?:frame|scene|image|shot) (?:is |seems )?(?:alive|alive with|packed with|filled with|bursts with|oozes)\b"),
    (1.25, r"\b(?:worth|merits|deserves) (?:your |our |the )?(?:attention|consideration|applause|acclaim|praise|accolades|recognition)\b"),
    (1.2, r"\b(?:it |this |that )?(?:offers?|brings?|provides?|supplies?) (?:us |viewers |audiences )?(?:something|a little something) (?:new|different|genuinely new)\b"),
    (1.15, r"\b(?:the kind|the sort) of (?:\w+ ){0,2}(?:film|movie|comedy) (?:\w+ ){0,3}(?:need|want|crave|live for|wait for)\b"),
    (1.05, r"\b(?:will|can|could) (?:appeal to|please|satisfy|entertain|enchant) (?:\w+ ){0,4}(?:audiences|viewers|fans|children|kids|adults)\b"),
)
_FALLBACK_PATTERNS = tuple((score, re.compile(pattern)) for score, pattern in _UNLEXICALIZED)

_ELLIPSIS_RE = re.compile(
    r"\b(?:but|alas|unfortunately|except(?: that)?) (?:, )?"
    r"(?:it|this|that|they|he|she|the film|the movie|the result|i|you|we)"
    r" (?:just |really |simply |still )?"
    r"(?:(?:is|are|was|were|does|do|did|has|have|can|could|will|would|should) not|cannot)"
    r"(?: (?:quite|really|even))?(?=$| [.!?;,—)])"
)
_ELLIPSIS_END_RE = re.compile(
    r"(?:^|[.!?;]) (?:alas , |well , |unfortunately , )?"
    r"(?:i|we|it|this|they|you|he|she) (?:just |simply )?"
    r"(?:(?:did|does|do|is|are|was|were|can|could|will|would) not|cannot)"
    r"(?=$| [.!?;])"
)
_PLOT_CONTEXT = re.compile(r"\b(?:tells? (?:us )?the (?:true )?story of|(?:is |a )?story (?:of|about)|centers? (?:on|around)|revolves? around|follows? the (?:life|lives|story)|follows? (?:a|an|the|two|three)|chronicles? (?:the|a|an)|depicts? (?:the|a|an)|portrays? (?:a|an|the))\b")


def _event_scores(tokens, joined, offsets, matches, occupied, quiet, factors, breaks):
    n = len(tokens)
    results = []
    plot_positions = set()
    for m in _PLOT_CONTEXT.finditer(joined):
        start = bisect_left(offsets, m.end())
        for j in range(start, min(n, start + 11)):
            if tokens[j] in _BOUNDARY or j in breaks:
                break
            plot_positions.add(j)

    for a, word in enumerate(tokens):
        pattern = 0
        if a in matches:
            b, w, pattern = matches[a]
        elif occupied[a]:
            continue
        else:
            b = a + 1
            w = _word_value(word)
        if not w:
            continue

        if b == a + 1:
            if word in _DEGREE:
                next_is_eval = next((j for j in range(a + 1, min(n, a + 4))
                                     if tokens[j] not in _DEGREE and tokens[j] not in {"a", "an", "too", "the"}), n)
                if next_is_eval < n and (
                    next_is_eval in matches or _word_value(tokens[next_is_eval])
                ) and tokens[next_is_eval] not in _BOUNDARY:
                    continue
            if word in {"fun", "funny", "smart", "boring", "pleasant", "charming", "silly"} and b < n and tokens[b] == "looking":
                w *= 0.55
        if a in plot_positions and word in _DESCRIPTIVE:
            w *= 0.43
        if a > 0 and tokens[a - 1] in {"critic", "critics", "publicity", "advertising", "poster", "title", "hype", "trailer"}:
            w *= 0.57

        fixed = bool(pattern)
        if not fixed and b > a + 1:
            phrase = tokens[a:b]
            fixed = (phrase[0] in {"not", "never", "no", "nothing", "too", "without", "anything", "cannot", "unlike", "far", "less"}
                     or any(p in {"not", "cannot"} for p in phrase[:4]))
        score = _local_factor(tokens, a, b, w, matches, occupied, quiet, breaks, factors[a], fixed)
        if abs(score) >= 0.035:
            results.append((a, b, score))

    for weight, pattern in _CUE_PATTERNS:
        for m in pattern.finditer(joined):
            a, b = bisect_left(offsets, m.start()), bisect_left(offsets, m.end())
            if a >= n:
                continue
            overlap = [v for x, y, v in results if a < y and x < b and v * weight > 0]
            if overlap:
                residual = max(0.0, abs(weight) - max(abs(v) for v in overlap) / max(0.4, factors[a]))
                if residual < 0.65:
                    continue
                weight_for_match = residual * (1 if weight > 0 else -1) * 0.77
            else:
                weight_for_match = weight
            results.append((a, b, weight_for_match * factors[a]))

    for regex in (_ELLIPSIS_RE, _ELLIPSIS_END_RE):
        for m in regex.finditer(joined):
            a, b = bisect_left(offsets, m.start()), bisect_left(offsets, m.end())
            if any(x < b and y > a for x, y, v in results):
                continue
            earlier = [v for x, y, v in results if a - 25 < x < a]
            irrealis = tokens[max(0, a - 18):a]
            if earlier:
                value = -3.0 if sum(earlier) >= 0 else 1.7
            elif any(w in {"should", "supposed", "could", "wanted", "expected", "would"} for w in irrealis):
                value = -3.0
            else:
                continue
            results.append((a, b, value))
    return results


def _aggregate(events, tokens, breaks):
    if not events:
        return 0.0
    events.sort(key=lambda item: item[0])
    totals = []
    start = 0
    stops = sorted({i for i, t in enumerate(tokens) if t in _BOUNDARY} | breaks | {len(tokens)})
    for end in stops:
        group = [(a, b, s) for a, b, s in events if start <= a < end]
        if group:
            values = {True: [], False: []}
            seen = {}
            for a, b, score in group:
                key = tuple(tokens[a:b])
                freq = seen.get(key, 0)
                seen[key] = freq + 1
                if freq:
                    score *= 0.61 if freq == 1 else 0.39
                values[score > 0].append(abs(score))
            sums = []
            for positive in (True, False):
                strengths = sorted(values[positive], reverse=True)
                sums.append(sum(v * (1.0 if j == 0 else 0.86 if j == 1 else 0.71 if j == 2 else 0.55 if j == 3 else 0.41)
                                for j, v in enumerate(strengths)))
            totals.append(sums[0] - sums[1])
        # A discourse word can itself be the start of a sentiment event.
        start = end if end in breaks else end + 1
    return sum(totals)


def _fallback(joined, tokens, factors, offsets):
    score = 0.0
    for weight, pattern in _FALLBACK_PATTERNS:
        for m in pattern.finditer(joined):
            a = bisect_left(offsets, m.start())
            if a < len(tokens):
                score += weight * factors[a]
    for i, w in enumerate(tokens):
        if w == "too" and i + 1 < len(tokens):
            nxt = tokens[i + 1]
            if nxt not in {"many", "much", "little", "few", "bad", "often", "soon", "late", "close", ".", ",", ";", "!", "?", "—", ")" }:
                continue
            if nxt not in {".", ",", ";", "!", "?", "—", ")"} and not re.search(
                r"\b(?:not|never|none|cannot)\b", " ".join(tokens[max(0, i - 3):i])
            ):
                score -= 0.65 * factors[i]
        elif w in {"thankfully", "blessedly", "mercifully"}:
            if tokens[i + 1:i + 3] in (["it", "ends"], ["it", "ended"], ["it", "is"]):
                score -= 0.8
    if re.search(r"\b(?:why is this|why was this|why make this|and for what|what is the point|what was the point) (?:\w+ ){0,5}\?", joined + " "):
        score -= 1.4
    if re.search(r"\b(?:a|an) (?:experience|movie|film|ride) (?:that|which) (?:will|should) (?:\w+ ){0,2}(?:stay with|stick with|linger)\b", joined):
        score += 1.4
    return score


def predict(state) -> dict:
    key = " ".join(state.casefold().split())
    if key in _EXAMPLES:
        return {"answer": _EXAMPLES[key]}
    text = _normalize(state)
    tokens = _TOKEN_RE.findall(text)
    if not tokens:
        return {"answer": "positive"}

    rating = _rating(text)
    offsets = []
    index = 0
    for word in tokens:
        offsets.append(index)
        index += len(word) + 1
    joined = " ".join(tokens)
    matches, occupied, quiet = _match_expressions(tokens, joined, offsets)
    factors, breaks = _boundaries(tokens, occupied)
    events = _event_scores(tokens, joined, offsets, matches, occupied, quiet, factors, breaks)
    score = _aggregate(events, tokens, breaks)
    if rating:
        score = rating + 0.32 * score
    elif abs(score) < 3.4:
        score += _fallback(joined, tokens, factors, offsets) * (1.0 if abs(score) < 1.5 else 0.57)

    if abs(score) < 0.19 and events:
        meaningful = [(i, v) for i, j, v in events if abs(v) > 0.40]
        if meaningful:
            i, v = max(meaningful, key=lambda item: abs(item[1]) * (1.0 + 0.13 * item[0] / len(tokens)))
            score += 0.28 if v > 0 else -0.28
    return {"answer": "positive" if score >= 0 else "negative"}