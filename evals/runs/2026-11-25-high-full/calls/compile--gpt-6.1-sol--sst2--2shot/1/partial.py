import re
import unicodedata


def _tokens(text):
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower().replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("&amp;", " and ").replace("&quot;", " ")
    text = text.replace("&lt;", " ").replace("&gt;", " ")
    text = re.sub(r":-?\)", " smiletoken ", text)
    text = re.sub(r":-?\(", " frowntoken ", text)
    text = re.sub(r"\b([a-z]+)\s+n\s*'\s*t\b", r"\1n't", text)
    text = re.sub(r"\b([a-z]+)\s*'\s*(s|re|ve|ll|d|m)\b", r"\1'\2", text)
    text = re.sub(r"\bcan(?:not|'t)\b", "can not", text)
    text = re.sub(r"\bwon't\b", "will not", text)
    text = re.sub(r"\bshan't\b", "shall not", text)
    text = re.sub(r"\bain't\b", "is not", text)
    text = re.sub(r"\b([a-z]+)n't\b", r"\1 not", text)
    text = re.sub(r"\b(it|that|what|there|he|she|who|here)'s\b", r"\1 is", text)
    text = re.sub(r"\b([a-z]+)'s\b", r"\1", text)
    for ending, expansion in (("'re", " are"), ("'ve", " have"),
                              ("'ll", " will"), ("'d", " would"),
                              ("'m", " am")):
        text = text.replace(ending, expansion)
    text = re.sub(r"\b([a-d])\s*\+", r" grade\1plus ", text)
    text = re.sub(r"--+|[\u2013\u2014]", " ; ", text)
    text = text.replace("-", " ").replace("/", " ")
    return re.findall(r"[a-z0-9]+|[.,!?;:()]", text)


_TERMS = {}
_MAX_PHRASE = 1


def _add(term, value):
    global _MAX_PHRASE
    key = tuple(_tokens(term))
    if key:
        _TERMS[key] = float(value)
        _MAX_PHRASE = max(_MAX_PHRASE, len(key))


_WORD_GROUPS = [
    (3.5, "masterpiece masterwork"),
    (3.0, "brilliant superb excellent masterful magnificent outstanding phenomenal"),
    (2.8, "wonderful terrific fantastic fabulous marvelous marvellous extraordinary "
          "unforgettable flawless hilarious triumph spellbinding"),
    (2.6, "riveting gripping fascinating stunning splendid exquisite breathtaking "
          "delightful dazzling enthralling engrossing captivating exhilarating "
          "electrifying exceptional sublime awesome"),
    (2.4, "great gorgeous beautiful remarkable compelling amazing astounding "
          "astonishing sumptuous ravishing mesmerizing mesmerising transcendent "
          "triumphant brilliantness"),
    (2.3, "entertaining enjoyable exciting thrilling impressive satisfying rewarding "
          "heartwarming heartening poignant gem treasure"),
    (2.1, "moving touching affecting powerful effective inspired inspiring imaginative "
          "inventive creative intelligent smart witty charming endearing haunting "
          "thoughtful insightful perceptive provocative memorable wonderfulness "
          "revelatory revelation illuminating enlightening stirring rousing "
          "winning delightful"),
    (2.0, "goodness excellence brilliance delight delights delighted pleasure pleasures "
          "achievement accomplishment accomplished beautifulness success successful "
          "succeeds succeed successfully recommend recommends recommended "
          "convincing engaging absorbing involving engrosses fascinates enchants "
          "captivates dazzles impresses impressed worthwhile lovely ingenious "
          "nuanced elegant gracefulness tenderness heartbroken"),
    (1.9, "good original originality funny amusing enjoy enjoys enjoyed enjoyment "
          "thought-provoking resonant subtle stylish vivid rich assured "
          "masterfully skillful skilful skillfully skilfully adroit adept "
          "unpretentious unforgettable lyricism lyrical poetic magical enchanting "
          "intimate humane heartfelt genuine authentic honest sincerity honestness "
          "worthwhile verve panache veracious"),
    (1.7, "fine charm charms wit fresh freshness appealing attractive admirable "
          "admirably admiration admire admires admired fearless daring audacious "
          "bold imaginative inventiveness creativity innovative innovation "
          "groundbreaking engrossed absorbed hypnosis hypnotic charismatic charisma "
          "magnetic soulful warmth warm gentle graceful gracefully elegance "
          "sincere tenderness tender affectionate affectionately affectionate "
          "bittersweet sweet sweetly sophisticated sophistication complexity "
          "astute incisive sharp sharply observant intelligent intelligence "
          "insights insight depth substantial substantive meaningful relevant "
          "timely classic timeless essential invaluable valuable worthy "
          "pleasing pleasant pleased satisfy satisfies satisfied satisfaction "
          "uncompromising unflinching harrowing heartbreaking evocative atmospheric "
          "atmospherically vibrant vitality lively energetic spirited exuberant "
          "effervescent buoyant joyful joyous joy sparkling sparkle sparkles "
          "zest zesty zestful zestfully feast treat jewel crowdpleaser"),
    (1.5, "interesting intrigue intriguing intrigues intr igue curiosity "
          "empathy empathetic sympathetic likable likeable lovable adorable "
          "likeability likability relatable relatability humanistic humanism "
          "warmhearted warm-hearted uplifting uplifted inspiring inspirational "
          "enthusiasm enthusiastic exuberance affection humanity generosity "
          "generous generousness naturalness authenticity honesty sincerity "
          "realistic realism believable credible credibility natural naturalistic "
          "convincingly coherently lucid clarity coherence coherent "
          "polished polish crisp taut tight tightly brisk briskly fluid fluidity "
          "seamless seamlessly careful carefully meticulous meticulously "
          "skill skilled craftsmanship craft craftily elegantness "
          "competently competentness elegance confidence confident confidently "
          "distinctive unique unconventional offbeat off-beat quirky "
          "droll sly slyly mischievous irreverent irreverence savvy clever cleverly "
          "cleverness smarter smartly wit wittily humorous humourous humorously "
          "amusement fun entertainingly enjoyably beautifully impressively "
          "effectively potently powerfully emotionally-rich "
          "resonance resonates resoundingly "
          "reward rewarded rewards fulfilling passionate passion "
          "informative educational illuminatingly enlightens informed "
          "revealing revealingly absorbingness transport transporting "
          "intensity intense suspense suspenseful chilling scary scarier scariest "
          "terrifying frightening chillingly shivers shivery "
          "stir stirrings stirs dynamic dynamism electric explosive "
          "evokes evocatively visuality "
          "cinematically cinematicness poeticness poetry "
          "disarming disarmingly refreshingly refreshing "
          "engagingly fascinatingly "
          "bestest topnotch delicious deliciously delectable luscious"),
    (1.2, "nice solid decent watchable accessible accessibility appeal appeals "
          "adroitly adeptly talented talent talents "
          "humor humour laughter laughs laughing laugh chuckles chuckle "
          "tension tense creepy creepiness spooky frights fright "
          "imagination invention ambitions ambition ambitious "
          "artistic artistry artful artfully "
          "important importance significant significance "
          "purposeful purposefulness "
          "restrained restraint understated nuance nuances subtlety subtly "
          "delicate delicately textured texture layered "
          "complex profound profundity perception "
          "incisively penetrating astutely "
          "respectful respectable respect respectfulness "
          "courage courageous bravery brave audacity boldly boldness fearlessly "
          "hopeful optimistic optimism upliftingly uplift "
          "comforting soothing relaxing nostalgia nostalgic "
          "fascination fascinated wonders wonder wondrous "
          "marvel marvels "
          "vividly richly lush lushly "
          "stately majestic majestically "
          "grace gracefulness "
          "sweetness gentleness intimacy tenderness "
          "enduring lasting "
          "accomplishes achieves "
          "exceeds transcends transcend "
          "pleasantly satisfyingness "
          "gusto gusto-filled gusto-laden "
          "nimble nimbly deft deftly deftness "
          "delicacy inventively "
          "inventively "
          "gutsy guts spunky sassy spiritedness "
          "stylishly stylishness "
          "assurance disquieting unsettling "
          "sobering devastating gut-wrenching wrenching "
          "absorbs "
          "finesse "
          "perfect perfectly perfection"),
    (0.8, "competent capable capablely passable serviceable adequate entertainingness "
          "promising promise promises potential redeeming redemption redeems redeemed "
          "human heart soul spirit energy magic "
          "emotional emotion emotions "
          "entertain entertainment romance romantic "
          "comical comic "
          "fun-loving "
          "intricate intricacy intricacies "
          "eccentric eccentricity "
          "earnest earnestness sincerity "
          "inviting invitingly "
          "amused smile smiles smiling grin grins "
          "daffy madcap zany goofy goofiness "
          "loved loving lovingly love loves liked liking "
          "succeeds delivers deliver delivery "
          "accomplish craftsmanship "
          "atmosphere "
          "exploration explores examination examines "
          "dramatic "
          "intellectual cerebral "
          "sensitive sensitivity "
          "discovery discover discoveries "
          "refreshes "
          "eye-opening eyeopener "
          "reassuring reassuringly "
          "wry wryly "
          "engage engages "
          "neat neatness "
          "lighthearted light-hearted "
          "lushness sumptuousness "
          "ingeniously "
          "nuance-filled "
          "fearsome "
          "charmer"),
    (0.5, "surprise surprises surprising startles startling "
          "escapist escapism "
          "comfortable "
          "campy "
          "unapologetic "
          "unaffected "
          "unassuming "
          "multifaceted "
          "cinematic "
          "goodhearted good-hearted "
          "gift "
          "plausible "
          "honorable "
          "loopy "
          "romanticism "
          "aesthetic "
          "restful "
          "meditative "
          "mature maturity "
          "poise poised "
          "sober soberness "
          "inventor "
          "earnestly "
          "loyalty "
          "radiant radiance "
          "sensual sensuality "
          "seductive seductivey "
          "hushed "
          "impeccable impeccably "
          "willing "
          "wackiness wacky"),
    (-0.5, "silly silliness familiar conventional ordinary average "
           "melodrama sentimental sentimentality "
           "saccharinity "
           "frivolous trivial frivolity "
           "bleak grim depressing depressed "
           "sad bitter "
           "detached distant remote aloof "
           "brutal gory gore grotesque "
           "weird bizarre "
           "absurd "
           "shameless "
           "slick glossy glib "
           "flashy showy "
           "slight "
           "clinical "
           "heavy "
           "complicated "
           "risky "
           "troubled trouble "
           "flaw imperfect imperfections "
           "uncertain uncertainty "
           "longish "
           "slow"),
    (-0.9, "thin cheap cheaply tame tameness cold coldness "
           "cruel cruelty "
           "cynical cynicism cynically "
           "melodramatic "
           "unbelievable "
           "unreal "
           "obscure obscurity "
           "convoluted convolutions "
           "predictability "
           "theatrical theatricality "
           "contrivance contrivances "
           "cornball corny corniness cheesy hokey hokum "
           "gimmick gimmicks "
           "problem problems "
           "missing missed "
           "fault faults "
           "flaws flawed "
           "overkill "
           "frenetic frenzy "
           "frantic frantically "
           "manipulation calculated "
           "exploitation "
           "preaching "
           "talky wordy "
           "minor marginal "
           "staleish "
           "ridicule "
           "flounders floundering "
           "sputters sputtering "
           "sags sagging "
           "flabby "
           "thinness "
           "stagebound"),
    (-1.3, "weaknesses weakness weak "
           "uninteresting unmemorable "
           "forgettable "
           "uneven unevenness inconsistent inconsistency "
           "familiarity routine predictable conventionality "
           "trivial triviality simplistic simplification "
           "naive naivete unsophisticated "
           "strained straining forced "
           "mannered mannerisms "
           "self-conscious "
           "gimmicky gimmickry "
           "stagy stagey "
           "superficial superficiality shallow "
           "underwritten underdeveloped "
           "unfocused unfocussed "
           "unbalanced incomplete unfinished unformed unresolved "
           "abrupt random arbitrary arbitrarily "
           "opaque opacity impenetrable inaccessible "
           "illogical illogic "
           "implausible implausibility "
           "unrealistic artificial unnatural "
           "stiff awkward awkwardly "
           "tedium-inducing "
           "baggy ragged meandering rambling ramshackle "
           "lengthy endless "
           "tiring exhausting exhaustion "
           "fatuous "
           "insincere insincerity "
           "false fake phony phoniness "
           "pallid limp limpness "
           "tepidness "
           "underwhelms "
           "unfortunate sadly "
           "regret regrets "
           "shortcoming shortcomings "
           "insubstantial substance-free "
           "tasteless tastelessness "
           "juvenile childish immature immaturity "
           "vulgar vulgarity "
           "raunchiness "
           "sanitized sanitised "
           "frustration frustrated "
           "alienating alienates alienated "
           "heartless heartlessness "
           "preachiness preachy "
           "didactic dogmatic "
           "muddiness murky "
           "pointlessness "
           "amateur "
           "trashy schlock schlocky "
           "ludicrousness "
           "inanity inane "
           "inconsequential inconsequentiality "
           "lopsided "
           "humdrum "
           "pedantry pedantic "
           "pedanticness "
           "baffling bewildering puzzling "
           "punishing "
           "craven gutlessness "
           "pretends pretending "
           "overcomplicated overcomplicates "
           "underachieves underachieving "
           "repetition"),
    (-1.8, "bad poor poorly "
           "mediocre mediocrity "
           "pedestrian pedestrianism "
           "stale tired tires tiresome "
           "unoriginal unoriginality derivative "
           "rehash rehashed retread recycled recycling "
           "repetitive repetitious redundant redundancy "
           "cliche cliches cliched cliche-ridden hackneyed trite "
           "banal banality banalities bland blandness insipid insipidity "
           "unremarkable unexceptional "
           "uninspired uninspiring unimaginative uncreative uninventive "
           "unimpressive "
           "unappealing charmless charm-free "
           "unconvincing unconvincingly "
           "unsatisfying unsatisfactory dissatisfying dissatisfied "
           "unfulfilling unrewarding "
           "unnecessary needless needlessly "
           "pointless pointlessly purposeless aimless aimlessness directionless "
           "empty hollow vacuous vacuity vapid vapidity "
           "soulless sterile sterility bloodless lifeless listless "
           "wooden woodenness stilted inert inertness static "
           "flat flatness "
           "clumsy clumsily clumsiness clunky clunkiness "
           "sloppy sloppily carelessly careless "
           "shoddy sluggish sluggishly lazy lazily laziness "
           "labored laboured laborious laboriously "
           "leaden plodding ponderous ponderously ponderousness "
           "dullness drab dreary dreariness "
           "soporific somnolent "
           "monotonous monotonously monotony "
           "drags dragging draggy "
           "slog slogs droning drones "
           "long-winded longwinded verbose "
           "overlong bloated padded padding "
           "overdone overblown overbearing overwrought "
           "overproduced overstylized "
           "disjointed disjointedness choppy muddled confused confusing "
           "incoherence incoherent incomprehensible incomprehensibility "
           "misguided misconceived misbegotten miscalculated miscalculation "
           "ineffective ineffectual impotence impotent "
           "anticlimactic anticlimax letdown "
           "frustrating frustrates "
           "irritating irritates irritation annoying annoys annoyance "
           "grating grates "
           "obnoxious off-putting repellent repellant "
           "unpleasant unpleasantness "
           "unlikable unlikeable unsympathetic "
           "shrill shrillness strident "
           "hammy overacted overacting "
           "histrionic histrionics "
           "manipulative manipulates "
           "pompous pomposity pretentious pretension pretensions "
           "smug smugness self-satisfied self-important self-importance "
           "self-indulgent self-indulgence "
           "pandering panders panderingly "
           "condescending condescension patronizing patronising "
           "preposterous ridiculous ridiculously ludicrous ludicrously "
           "dumb stupid stupidity idiotic idiocy "
           "mindless mindlessly brainless "
           "juvenility puerile sophomoric infantile "
           "crass crassness offensive offensively "
           "insensitive insensitivity "
           "distasteful distastefulness "
           "cloying cloyingly mawkish maudlin saccharine sappy schmaltzy schmaltz "
           "treacly treacle "
           "cornball hokey "
           "dated outdated antiquated "
           "overrated "
           "unimportant irrelevant "
           "meaningless "
           "devoid "
           "lacking lack lacks "
           "disappoint disappoints disappointed disappointing disappointment "
           "failure fail fails failed failing failings "
           "misfire misfires "
           "waste wasted wastes wasting wasteful "
           "squander squanders squandered "
           "ruin ruins ruined "
           "botched botches bungled bungles mangled mangles "
           "undermines undercuts "
           "betrays cheated cheats "
           "unfortunate unfortunately regrettable regrettably alas "
           "hopeless hopelessly "
           "unilluminating uninformative "
           "uninviting "
           "gutless toothless spineless "
           "lukewarm tepid watered-down "
           "disconnected disconnectedness "
           "overfamiliar "
           "inelegant graceless "
           "nonsense nonsensical "
           "drivel twaddle "
           "dreck dross crud "
           "lowbrow "
           "flimsy flimsiness skimpy sketchy "
           "crude crudely "
           "sillyness "
           "inertly "
           "dubious "
           "suffocating "
           "exasperating exasperation "
           "vexing "
           "unsubtle "
           "distracting distracts distraction "
           "miscast "
           "embarrassing embarrassment embarrassed embarrasses "
           "disastrously "
           "groan groans groaning "
           "numbing "
           "stagnant stagnantness "
           "plods "
           "cheats "
           "insult insults insulting "
           "racist sexist homophobic misogynistic "
           "exploitative "
           "mean-spirited "
           "unappealingly "
           "embarrassingly"),
    (-2.4, "boring bore bored boredom boringly dull tedious tediously "
           "awful terrible horrible horrid lousy abysmal atrocious appalling "
           "abominable execrable wretched dreadful "
           "unwatchable unendurable unbearable insufferable intolerable "
           "inept ineptitude incompetent incompetence amateurish "
           "unfunny humorless humourless witless "
           "laughable laughably "
           "disaster disastrous travesty fiasco "
           "mess shambles "
           "dud dudsville turkey flop "
           "trainwreck "
           "snooze snoozer snoozefest snooze-fest snore yawn yawner "
           "interminable interminably "
           "turgid "
           "mind-numbing brain-dead braindead "
           "moronic imbecilic "
           "excruciating excruciatingly torturous tortuous "
           "agonizing agonizingly painful painfully "
           "sucks suck sucked sucky "
           "crap crappy garbage rubbish tripe bilge "
           "stinker stinks stink "
           "shit shitty bullshit "
           "trash junk "
           "revolting repulsive disgusting nauseating "
           "abhorrent loathsome detestable hateful hate hated hates "
           "irredeemable irredeemably "
           "pathetic pitiful "
           "lame lamebrained lamebrain "
           "feeble "
           "lackluster lacklustre "
           "displeasing "
           "botch "
           "meh bleh blah "
           "frowntoken"),
    (1.5, "smiletoken gradebplus gradecplus"),
    (3.0, "gradeaplus"),
    (-1.8, "gradedplus"),
    (1.6, "better"),
    (3.2, "best finest greatest"),
    (-2.3, "worse"),
    (-3.8, "worst"),
]

for _value, _words in _WORD_GROUPS:
    for _word in _words.split():
        _add(_word, _value)


_PHRASE_GROUPS = [
    (0, """love story; love stories; love triangle; love affair; love interest;
        good guy; good guys; bad guy; bad guys; bad boy; bad boys;
        good cop; bad cop; good friend; best friend; best friends;
        good man; good woman; great depression; great war; great britain;
        great deal; great many; a good deal; good old; good ol;
        good intentions; best intentions; good looks;
        fine line; fine print; nice guy; nice guys;
        special effects; special effect; special agent; special forces;
        romantic comedy; romantic comedies; romantic drama;
        dark comedy; black comedy; horror movie; horror film;
        low budget; big budget; high concept; box office;
        academy award; academy awards; film festival;
        as well as; as good as; as bad as;
        at best; at worst;
        more or less; so far so good;
        not only; not just; not merely; not simply;
        not to mention; whether or not; no wonder; no doubt;
        without doubt; without question; without a doubt;
        nothing but; nothing less than; nothing short of;
        no less than; no ordinary;
        can not help but; could not help but; can not help;
        hard not to; difficult not to; impossible not to;
        not unlike;
        pretty much; a little bit; a bit of;
        slow motion; slow mo;
        to die for; death scene; death scenes;
        serious illness; serious disease;
        real life; real world; true story;
        bad language; bad behavior; bad behaviour;
        good versus evil; good vs evil;
        the good the bad and the ugly"""),
    (0.3, """well intentioned; well meaning; earnest effort; interesting premise;
        promising premise; intriguing premise; good premise; great premise;
        good idea; interesting idea; interesting ideas; promising idea;
        best picture; award winning; in love; fall in love; falls in love;
        falling in love; fallen in love"""),
    (0.8, """slow burn; slow burning; low key; old fashioned;
        guilty fun; an acquired taste; acquired taste;
        has its moments; have their moments; has its charms;
        pass the time; passes the time; time passer;
        easy on the eyes; easy to watch;
        better than nothing; not entirely bad;
        worth considering; worth a rental;
        brings to mind; to its credit; to his credit; to her credit"""),
    (1.5, """good looking; well acted; well performed; well shot;
        well paced; well told; well constructed; well cast;
        well directed; well written; well realized; well realised;
        well executed; well developed; well observed; well observed;
        well worth; well done; well made;
        works well; works nicely; it works; really works;
        comes alive; come alive; brings to life; brought to life;
        has heart; has a heart; with heart;
        a heart; a soul;
        cheap thrills; guilty pleasure; guilty pleasures;
        mindless fun; dumb fun; stupid fun; silly fun;
        goofy fun; ridiculous fun; preposterous fun;
        mindless entertainment; harmless fun; harmless entertainment;
        painful fun; painfully funny;
        good enough; funny enough; entertaining enough;
        more than adequate; more than competent;
        better than expected; better than average;
        worth a look; worth a peek; worth checking out;
        holds up; hold up; holds together; hold together;
        hit the mark; hits the mark; on the mark;
        hits its mark; hits all the right notes;
        hits the right notes; right on target;
        stands out; stand out; stand apart; stands apart;
        something to say; has something to say;
        says something; saying something;
        food for thought; makes you think; make you think;
        plenty to admire; much to admire;
        gets it right; get it right; gets things right;
        does justice to; do justice to;
        not half bad; not too bad; not so bad;
        could have been worse; could be worse;
        not a bad; not bad; no slouch;
        nothing wrong with; nothing wrong;
        all right; thumbs up; two thumbs up;
        positive note; high note; high point;
        can do worse; could do worse;
        worth the effort; worth the trip;
        stays with you; stay with you; lingers in the mind;
        linger in the mind; under your skin; under the skin;
        gets the job done; does the job;
        more to offer; much to offer;
        a breath of fresh air; breath of fresh air"""),
    (2.3, """a lot of fun; lots of fun; great fun; much fun; too much fun;
        fun to watch; fun to see; fun to be had;
        great entertainment; pure entertainment; sheer entertainment;
        fine entertainment; solid entertainment;
        good time; great time; wonderful time;
        feel good; feel great; feel-good;
        feel good movie; feel good film;
        worth seeing; worth watching; worth renting;
        worth your time; worth the time; worth my time;
        worth the money; worth your money;
        worth the price; worth the price of admission;
        worth the admission; worth the wait;
        worth seeking out; worth tracking down;
        worth a visit; worth revisiting;
        reason enough to see; reasons to see;
        delivers the goods; deliver the goods; delivers on its promise;
        lives up to; live up to; living up to;
        rises above; rise above;
        pleasantly surprised; pleasant surprise;
        exceeds expectations; exceeded expectations; surpasses expectations;
        top notch; first rate; first class; world class;
        high quality; top quality;
        well crafted; finely crafted; beautifully crafted;
        beautifully shot; beautifully made; beautifully filmed;
        lovingly crafted; lovingly made; expertly crafted; expertly made;
        finely tuned; finely wrought;
        richly rewarding; emotionally satisfying; emotionally resonant;
        emotionally powerful; deeply moving; deeply affecting;
        highly entertaining; thoroughly entertaining; thoroughly enjoyable;
        utterly engaging; enormously entertaining; immensely entertaining;
        consistently funny; genuinely funny; very funny;
        laugh out loud; laugh aloud; laugh a minute;
        side splitting; gut busting; rib tickling;
        tickles the funny bone; tickle your funny bone;
        barrels of laughs; plenty of laughs; lots of laughs;
        packs a punch; pack a punch; powerful punch; emotional punch;
        can not stop laughing; could not stop laughing;
        can not wait to see;
        one to remember; one for the ages;
        a cut above; cut above the rest;
        film making at its best; cinema at its best;
        a real treat; a rare treat; a special treat;
        small gem; little gem; hidden gem; absolute gem;
        minor classic; instant classic; modern classic;
        oscar worthy; oscar caliber; award worthy;
        work of art; piece of art; cinematic art;
        sheer poetry; pure poetry;
        achingly beautiful; drop dead gorgeous;
        knocks it out of the park; knock it out of the park;
        firing on all cylinders;
        something special; something wonderful;
        not to be missed; should not be missed;
        deserves to be seen; deserves an audience;
        well worth seeing; well worth watching;
        better than it has any right to be;
        more than the sum of its parts;
        triumph of the human spirit;
        strikes a chord; strike a chord;
        rings true; ring true; has the ring of truth;
        speaks volumes; speaks to the heart;
        strikes gold; strike gold;
        does not disappoint; never disappoints"""),
    (3.2, """must see; must watch; must-see; a must;
        do not miss; do not miss it; do not pass up;
        run do not walk; do yourself a favor; do yourself a favour;
        highly recommended; wholeheartedly recommended;
        recommend it highly; recommend it wholeheartedly;
        can not recommend it enough; can not recommend this enough;
        could not recommend it more; can not recommend it more;
        tour de force; minor masterpiece; absolute masterpiece;
        pure delight; sheer delight; sheer joy; pure joy;
        best of the year; best films of the year; best movies of the year;
        one of the best; one of the finest; among the best;
        one of the great; one of the greatest;
        a great film; a great movie; an excellent film; an excellent movie;
        a wonderful film; a wonderful movie;
        four stars; five stars; ten out of ten;
        time well spent; money well spent;
        what is not to like; what is not to love;
        what more could you want; what more could one ask;
        heart and soul"""),
    (-0.9, """faint praise; faintly amusing; mildly amusing;
        intermittently amusing; occasionally amusing;
        nothing special; nothing exceptional; nothing extraordinary;
        nothing remarkable; nothing memorable; little new;
        not much new; not particularly; not especially;
        not entirely successful;
        seen better; seen it before; heard it before;
        goes on and on; on and on and on;
        hit and miss; hit or miss; mixed bag;
        mixed results; mixed blessing;
        guilty of; lack of;
        falls apart; fall apart;
        wears thin; wear thin; wearing thin;
        wearing out its welcome; overstays its welcome;
        overstay its welcome;
        goes through the motions; going through the motions;
        by turns; at times;
        made for television; made for tv;
        soap opera; soap operatic; music video;
        not a complete disaster;
        simply adequate; merely adequate;
        in spite of itself; despite itself;
        no great shakes; no big deal;
        a long way from; leaves something to be desired"""),
    (-1.6, """too much; too many; too little; too few;
        too long; too slow; too loud; too busy; too talky;
        too silly; too thin; too obvious; too easy;
        too clever; too cute; too neat; too pat;
        too familiar; too sentimental; too predictable;
        all too familiar; all too predictable;
        nothing new; nothing original; nothing interesting;
        little interest; little humor; little humour;
        little to recommend; little to offer; little to say;
        not enough; never enough; not quite enough;
        less than satisfying; less than compelling;
        less than impressive; less than inspired;
        just another; yet another; just about any;
        nothing more than; little more than; no more than;
        much ado about nothing;
        so what; who cares; why bother; what is the point;
        what is the point of;
        is that all; is this it;
        not saying much; does not say much;
        that is not saying much;
        could be better; could have been better; should have been better;
        leaves you cold; leave you cold; left me cold; leaves me cold;
        leaves us cold; left us cold; left you cold;
        cold fish; cold turkey;
        goes wrong; go wrong; went wrong;
        fails to deliver; failure to deliver;
        fails to convince; fails to engage;
        missed opportunity; missed opportunities; wasted opportunity;
        wasted opportunities; wasted potential;
        unfulfilled potential;
        a missed chance; misses the point; miss the point;
        misses its mark; miss its mark;
        loses its way; lose its way; lost its way;
        loses steam; runs out of steam; ran out of steam;
        running out of steam; out of ideas; runs out of ideas;
        falls short; fall short; falling short; fell short;
        takes forever; seems endless; feels endless;
        hard going; rough going; tough going;
        low rent; low point; second hand;
        straight to video; direct to video;
        only good thing; only bright spot; sole bright spot;
        one good thing; saving grace;
        sleep inducing; yawn inducing; coma inducing;
        slow moving; slow paced; sluggish pace;
        short on; thin on; light on;
        style over substance; style without substance;
        not worth; not worthwhile; can not recommend;
        do not recommend; would not recommend;
        has no idea; have no idea; does not have a clue;
        no idea how; no idea what;
        feels forced; feels false; rings false; ring false;
        rings hollow; ring hollow;
        in name only; for no reason;
        painful to watch; hard to watch;
        tries too hard; try too hard; trying too hard;
        works too hard; working too hard;
        stretches credibility; strains credibility;
        stretch credibility; strain credibility;
        poor excuse; pale imitation; weak imitation;
        warmed over; watered down;
        just sits there; sits there;
        so much noise; all noise;
        all over the place;
        has been done before; been there done that;
        seen that before;
        plot holes; plot hole; gaping holes;
        joins the ranks of; fails on;
        unintentional laughs; unintentionally funny;
        unintentionally hilarious;
        half baked; half hearted; half assed;
        dead end; going nowhere;
        under the impression;
        lack of imagination; lack of originality"""),
    (-2.4, """waste of time; waste your time; waste my time; wastes your time;
        wasting your time; waste of money; waste your money;
        wasted my time; wasted time; time wasted;
        not worth seeing; not worth watching;
        not worth the time; not worth your time; not worth my time;
        not worth the money; not worth your money;
        not worth the effort; not worth the price;
        nothing to recommend; nothing to recommend it;
        nothing going for it; nothing going for;
        nothing happens; nothing much happens;
        nothing works; does not work; do not work;
        never works; does not come together;
        fails miserably; fails utterly;
        falls flat; fall flat; fell flat; falling flat;
        falls completely flat;
        falls to pieces; fall to pieces;
        dead in the water; dead on arrival;
        crash and burn; crashes and burns;
        do not bother; do not bother seeing; do not bother watching;
        do not waste; do not waste your money; do not waste your time;
        skip it; skip this; avoid it; avoid this;
        stay away; steer clear; give it a miss; give this a miss;
        leave it alone; pass on this;
        stay home; stay at home; stayed home;
        better off at home; better off staying home;
        should have stayed home;
        watch something else; see something else;
        save your money; save your time; save yourself;
        no fun; no laughs; no laughter; not a laugh;
        without laughs; without a laugh;
        laugh free; laugh-free; comedy free;
        not remotely funny; not even funny;
        no plot; no story; no point; no heart; no soul;
        no redeeming qualities; no redeeming features; no redeeming value;
        without redeeming; without merit;
        no reason to see; no reason to watch;
        second rate; third rate; fourth rate; fifth rate;
        bargain basement; bottom of the barrel;
        scraping the bottom; scrape the bottom;
        by the numbers; paint by numbers; connect the dots;
        cookie cutter; cut and paste; cut from the same cloth;
        assembly line; formula driven; formula ridden;
        cliche ridden; cliche laden;
        cinematic equivalent of; cinematic dead end;
        mind numbingly; bone crushingly dull;
        dull as dishwater; dull as ditchwater;
        boring as hell; dull as hell;
        bad movie; bad film; poor movie; poor film;
        sorry excuse; excuse for a movie; excuse for a film;
        too clever by half; too cute by half;
        for its own good; pretentious mess;
        self serving; self congratulatory; self congratulation;
        mean spirited; mean spiritedness;
        heavy handed; heavy handedness; ham fisted; ham handed;
        brain dead; mind numbing;
        point of no return;
        leaves much to be desired; a lot to be desired; much to be desired;
        more bad than good; more misses than hits;
        more tedious than; more boring than;
        goes nowhere; go nowhere; went nowhere; gets nowhere;
        would be better off; should know better;
        should have known better;
        embarrassing failure; abject failure;
        tries and fails; try and fail;
        too smart for its own good;
        gives you a headache; gave me a headache;
        headache inducing;
        made me cringe; makes you cringe; cringe worthy;
        groan inducing; groan worthy;
        eye rolling; roll your eyes; rolling my eyes;
        rolling their eyes;
        goes downhill; downhill from there;
        not a good; not very good; no good;
        not good enough; not funny enough;
        plotless mess; unholy mess"""),
    (-3.4, """one of the worst; among the worst; absolute worst;
        worst of the year; worst movies of the year; worst films of the year;
        worst movie; worst film;
        complete waste of time; total waste of time;
        utter waste of time; colossal waste of time;
        complete disaster; utter disaster; unmitigated disaster;
        complete failure; total failure;
        complete mess; incoherent mess;
        piece of crap; piece of garbage; piece of junk;
        piece of trash; piece of shit; pile of crap; pile of garbage;
        zero stars; no stars; one out of ten;
        cinematic atrocity; crime against cinema;
        insult to the intelligence; insult to your intelligence;
        insults your intelligence; insults the intelligence;
        beneath contempt; beyond redemption;
        avoid at all costs; avoid like the plague;
        worst thing; horrible movie; terrible movie;
        awful movie; terrible film; awful film;
        unwatchable mess"""),
]

for _value, _phrases in _PHRASE_GROUPS:
    for _phrase in _phrases.split(";"):
        _add(_phrase.strip(), _value)


_INTENSIFIERS = {
    "very": 1.22, "really": 1.15, "extremely": 1.4,
    "incredibly": 1.3, "exceptionally": 1.32, "highly": 1.3,
    "utterly": 1.4, "absolutely": 1.35, "totally": 1.3,
    "completely": 1.25, "entirely": 1.15, "thoroughly": 1.3,
    "enormously": 1.35, "immensely": 1.35, "terribly": 1.25,
    "awfully": 1.2, "particularly": 1.15, "especially": 1.17,
    "remarkably": 1.2, "surprisingly": 1.15, "unexpectedly": 1.12,
    "genuinely": 1.2, "truly": 1.25, "deeply": 1.22,
    "profoundly": 1.25, "quite": 1.12, "rather": 1.08,
    "pretty": 1.08, "so": 1.2, "such": 1.12, "simply": 1.12,
    "unusually": 1.12, "decidedly": 1.15, "downright": 1.25,
    "plain": 1.1, "flatly": 1.15, "wholly": 1.25,
    "unbelievably": 1.3, "exceedingly": 1.3,
    "vaguely": 0.42, "mildly": 0.5, "faintly": 0.45,
    "slightly": 0.6, "somewhat": 0.65, "moderately": 0.65,
    "occasionally": 0.6, "sporadically": 0.45,
    "intermittently": 0.55, "sometimes": 0.7,
    "fairly": 0.8, "reasonably": 0.8, "relatively": 0.8,
    "almost": 0.6, "nearly": 0.7, "partly": 0.65,
    "partially": 0.65, "arguably": 0.85,
    "sorta": 0.65, "kinda": 0.65,
}

_NEGATORS = {
    "not", "never", "no", "neither", "nor", "without",
    "hardly", "barely", "scarcely", "seldom", "rarely",
    "nothing", "nowhere", "nobody", "none",
}
_LACK_WORDS = {
    "lack", "lacks", "lacking", "devoid", "deprived",
    "fail", "fails", "failed", "failing", "unable",
}
_BREAKS = {".", ",", "!", "?", ";", ":", "(", ")"}
_SCOPE_BREAKS = _BREAKS | {
    "but", "however", "though", "although", "yet", "whereas",
    "nevertheless", "nonetheless", "despite", "except",
}
_NEUTRAL_WORDS = {
    "film", "films", "movie", "movies", "cinema", "picture", "pictures",
    "screen", "actor", "actors", "actress", "actresses", "performance",
    "performances", "character", "characters", "director", "directors",
    "script", "screenplay", "story", "stories", "plot", "plots",
    "scene", "scenes", "acting", "writing", "directing", "shot", "shots",
    "editing", "camera", "cinematography", "music", "soundtrack",
    "documentary", "comedy", "drama", "thriller", "horror", "action",
    "audience", "audiences", "viewer", "viewers", "people", "person",
    "life", "death", "war", "murder", "violence", "crime", "sex",
    "said", "says", "say", "tells", "told", "telling", "tale",
    "new", "old", "young", "man", "woman", "boy", "girl", "child",
    "children", "family", "father", "mother", "son", "daughter",
    "friend", "friends", "time", "times", "year", "years", "day",
    "days", "night", "world", "american", "english", "french",
    "hollywood", "independent", "foreign", "true", "real",
    "hard", "difficult", "impossible", "little", "few", "less",
    "just", "only", "even", "much", "many", "more", "most",
    "kind", "kindly", "interest", "interests", "work", "working",
    "works", "part", "parts", "thing", "things", "well", "far",
    "big", "small", "long", "short", "high", "low", "black", "white",
    "dark", "light", "mean", "means", "dead", "serious", "certain",
    "experience", "experiences", "look", "looks", "looking",
    "badly", "title", "premise",
}


def _word_value(word):
    key = (word,)
    if key in _TERMS:
        return _TERMS[key]
    if word in _INTENSIFIERS or word in _NEGATORS or word in _NEUTRAL_WORDS:
        return None
    candidates = []
    if word.endswith("ly") and len(word) > 5:
        candidates.extend((word[:-2], word[:-3] + "y", word[:-2] + "e"))
    if word.endswith("ness") and len(word) > 7:
        candidates.extend((word[:-4], word[:-5] + "y"))
    if word.endswith("s") and len(word) > 4:
        candidates.append(word[:-1])
    if word.endswith("es") and len(word) > 5:
        candidates.append(word[:-2])
    if word.endswith("ies") and len(word) > 5:
        candidates.append(word[:-3] + "y")
    for candidate in candidates:
        value = _TERMS.get((candidate,))
        if value is not None and abs(value) >= 0.8:
            return value * 0.9
    if word.startswith("un") and len(word) > 5:
        root = _TERMS.get((word[2:],))
        if root is not None and root >= 1.0:
            return -min(2.8, root + 0.2)
    return None


def _find_events(tokens):
    events = []
    masked = set()
    i = 0
    while i < len(tokens):
        found = False
        for size in range(min(_MAX_PHRASE, len(tokens) - i), 1, -1):
            key = tuple(tokens[i:i + size])
            if key in _TERMS:
                value = _TERMS[key]
                events.append((i, i + size, value))
                if value == 0:
                    masked.update(range(i, i + size))
                i += size
                found = True
                break
        if found:
            continue
        word = tokens[i]
        if word not in _INTENSIFIERS:
            value = _word_value(word)
            if value is not None:
                events.append((i, i + 1, value))
        i += 1
    return events, masked


def _clause_weights(tokens, masked):
    n = len(tokens)
    weights = [1.0] * n

    def scale(start, end, factor):
        for j in range(max(0, start), min(n, end)):
            weights[j] *= factor

    def following_comma(start):
        for j in range(start + 1, n):
            if tokens[j] in {",", ";", ".", "!", "?"}:
                return j
        return n

    for i, word in enumerate(tokens):
        if i in masked:
            continue
        if word in {"but", "however", "nevertheless", "nonetheless"}:
            if i and tokens[i - 1] in {"anything", "all", "nothing"}:
                continue
            scale(0, i, 0.62)
            scale(i + 1, n, 1.28)
        elif word == "yet":
            if (i and tokens[i - 1] == "not") or (
                    i + 1 < n and tokens[i + 1] == "another"):
                continue
            if i > 1:
                scale(0, i, 0.72)
                scale(i + 1, n, 1.22)
        elif word in {"although", "though", "while", "whereas"}:
            if i >= n - 2:
                continue
            if i <= 2 or (i == 3 and tokens[0] == "even"):
                comma = following_comma(i)
                if comma < n:
                    scale(i + 1, comma, 0.62)
                    scale(comma + 1, n, 1.16)
            else:
                scale(0, i, 1.13)
                scale(i + 1, following_comma(i), 0.65)
        elif word == "despite" or (
                word == "spite" and i and tokens[i - 1] == "in"):
            if i <= 2:
                comma = following_comma(i)
                if comma < n:
                    scale(i + 1, comma, 0.5)
                    scale(comma + 1, n, 1.18)
            else:
                scale(0, i, 1.17)
                scale(i + 1, following_comma(i), 0.55)
        elif word == "except":
            scale(i + 1, following_comma(i), 0.7)
        elif word in {"ultimately", "overall"}:
            scale(i + 1, following_comma(i), 1.28)
        elif word == "if" and i + 1 < n and tokens[i + 1] in {
                "somewhat", "occasionally", "rather", "sometimes", "a"}:
            if i > 2:
                scale(i + 1, following_comma(i), 0.7)
    return [min(2.2, max(0.22, w)) for w in weights]


def _negation_factor(tokens, start, masked):
    preceding = []
    for j in range(start - 1, max(-1, start - 7), -1):
        if tokens[j] in _SCOPE_BREAKS:
            break
        preceding.append(j)
    negations = []
    for j in preceding:
        if j in masked:
            continue
        word = tokens[j]
        distance = start - j
        if word in _NEGATORS:
            if distance > 5:
                continue
            if word == "not":
                if j + 1 < len(tokens) and tokens[j + 1] in {
                    "only", "just", "merely", "simply"
                }:
                    continue
                if j >= 1 and tokens[j - 1] in {
                    "hard", "difficult", "impossible"
                }:
                    continue
            if word == "no" and j + 1 < len(tokens) and tokens[j + 1] in {
                "doubt", "wonder", "less", "ordinary"
            }:
                continue
            negations.append(word)
        elif word in _LACK_WORDS and distance <= 5:
            if word in {"fail", "fails", "failed", "failing", "unable"}:
                if "to" not in tokens[j + 1:start]:
                    continue
            negations.append(word)
        elif word in {"little", "few"} and distance <= 3:
            if j > 0 and tokens[j - 1] in {"a", "the", "his", "her", "their"}:
                continue
            negations.append(word)
        elif word == "less" and distance <= 3:
            if j and tokens[j - 1] in {"no", "nothing"}:
                continue
            negations.append(word)
        elif word in {"hard", "difficult", "impossible", "tough"} and distance <= 4:
            if "to" in tokens[j + 1:start]:
                negations.append(word)
        elif word == "but" and j and tokens[j - 1] == "anything":
            negations.append(word)
    if len(negations) % 2:
        if any(w in {"hardly", "barely", "scarcely", "seldom", "rarely",
                     "less", "little", "few"} for w in negations):
            return -0.72
        return -0.88
    if negations:
        return 0.85
    return 1.0


def _is_embedded_failure(tokens, start, end, events):
    if end != start + 1 or tokens[start] not in _LACK_WORDS:
        return False
    for other_start, other_end, value in events:
        if other_start <= start or other_start > start + 6 or value == 0:
            continue
        if any(t in _SCOPE_BREAKS for t in tokens[end:other_start]):
            break
        if tokens[start] in {"fail", "fails", "failed", "failing", "unable"}:
            if "to" not in tokens[end:other_start]:
                continue
        return True
    return False


def _hypothetical_factor(tokens, start):
    left = tokens[max(0, start - 10):start]
    for j in range(len(left) - 3):
        if (left[j] in {"could", "should", "would", "might"}
                and left[j + 1:j + 4] == ["have", "been", "a"]):
            if not any(t in _SCOPE_BREAKS for t in left[j + 3:]):
                return 0.25, -0.55
    for j in range(len(left) - 2):
        if (left[j] in {"could", "should", "would", "might"}
                and left[j + 1:j + 3] == ["have", "been"]):
            if not any(t in _SCOPE_BREAKS for t in left[j + 3:]):
                return 0.3, -0.55
    for j, word in enumerate(left):
        if word in {
            "tries", "try", "trying", "tried", "attempts", "attempt",
            "attempting", "attempted", "wants", "wanted", "aspires",
            "aspiring", "strives", "striving", "strains"
        }:
            after = left[j + 1:]
            if "to" in after[:3] and not any(t in _SCOPE_BREAKS for t in after):
                if not any(t in {"succeeds", "succeed", "successfully", "manages"}
                           for t in after):
                    return 0.45, -0.25
    return 1.0, 0.0


def _score(tokens):
    events, masked = _find_events(tokens)
    weights = _clause_weights(tokens, masked)
    total = 0.0
    used = 0
    hypothetical_penalties = set()
    for start, end, raw in events:
        if raw == 0:
            continue
        if _is_embedded_failure(tokens, start, end, events):
            continue
        value = raw
        negation = _negation_factor(tokens, start, masked)
        value *= negation

        for distance in (1, 2):
            j = start - distance
            if j < 0 or tokens[j] in _SCOPE_BREAKS:
                break
            if j in masked:
                continue
            modifier = _INTENSIFIERS.get(tokens[j])
            if modifier is not None:
                value *= 1 + (modifier - 1) * (1 if distance == 1 else 0.6)
            if distance == 1 and tokens[j] == "too" and raw < 0:
                value *= 1.2

        before = tokens[max(0, start - 5):start]
        after = tokens[end:min(len(tokens), end + 5)]

        if raw > 0 and negation > 0:
            hypothetical, penalty = _hypothetical_factor(tokens, start)
            value *= hypothetical
            if penalty:
                key = max(0, start // 8)
                if key not in hypothetical_penalties:
                    total += penalty
                    hypothetical_penalties.add(key)
            if "than" in before:
                k = len(before) - 1 - before[::-1].index("than")
                earlier = tokens[max(0, start - 12):start - len(before) + k]
                if any(w in {"better", "worse", "more", "less"} for w in earlier):
                    value *= 0.45
            if before[-2:] == ["a", "few"] or before[-2:] == ["a", "little"]:
                value *= 0.65
            if "only" in before[-2:] and any(w in {"thing", "part", "reason"}
                                            for w in after[:2]):
                value = -max(1.2, abs(value) * 0.8)

        if any(w in {"title", "premise", "concept", "idea", "intentions"}
               for w in after[:3]):
            value *= 0.6
        if any(w in {"movie", "film", "picture"} for w in after[:2]):
            if abs(raw) >= 1.7:
                value *= 1.12

        if start >= 2 and tokens[start - 2:start] == ["at", "least"]:
            value *= 0.8
        if start >= 2 and tokens[start - 2:start] in (
                ["kind", "of"], ["sort", "of"]):
            value *= 0.65

        if end - start == 1 and tokens[start] in {"love", "loves", "loved", "hate",
                                                "hates", "hated", "liked"}:
            if any(w in {"i", "we", "you"} for w in before[-3:]):
                value *= 1.7

        if raw < 0 and negation > 0:
            if any(w in {"than"} for w in before[-2:]):
                prior = tokens[max(0, start - 10):start]
                if "better" in prior:
                    value *= 0.4

        local_weight = sum(weights[start:end]) / max(1, end - start)
        if value < 0:
            value *= 1.035
        total += value * local_weight
        used += 1

    text = " " + " ".join(tokens) + " "
    if re.search(r"\bcan not recommend\b.{0,35}\benough\b", text):
        total += 5.5
    if re.search(r"\b(?:hard|difficult|impossible) not to (?:like|love|enjoy|admire)\b", text):
        total += 1.8
    if re.search(r"\b(?:nothing|little) (?:else )?to (?:offer|recommend|say)\b", text):
        total -= 1.4
    if re.search(r"\b(?:not|never) (?:quite |really |even )?(?:comes|come|gets|get) (?:alive|going|off the ground)\b", text):
        total -= 2.0
    if re.search(r"\b(?:wish|wished) .{0,30}\b(?:better|more|less)\b", text):
        total -= 1.0
    if re.search(r"\b(?:too|so) .{0,25}\bfor (?:its|his|her|their) own good\b", text):
        total -= 0.8
    if re.search(r"\b(?:all|only) (?:noise|surface|style|spectacle) (?:and|with|without)\b", text):
        total -= 1.0
    if re.search(r"\b(?:not|never) (?:even |remotely |particularly )?(?:scary|frightening|funny|interesting|entertaining)\b", text):
        total -= 0.35
    if re.search(r"\b(?:it|this|that) (?:is|was) (?:just|merely|only) a (?:movie|film)\b", text):
        total -= 0.8

    return total, used


def _extract_text(state):
    if isinstance(state, str):
        return state
    if isinstance(state, dict):
        for key in ("text", "sentence", "review", "content", "input", "state"):
            if key in state:
                value = state[key]
                if isinstance(value, str):
                    return value
        return " ".join(value for value in state.values() if isinstance(value, str))
    if isinstance(state, (list, tuple)):
        return " ".join(value for value in state if isinstance(value, str))
    return ""


def predict(state):
    text = _extract_text(state)
    tokens = _tokens(text)
    if not tokens:
        return {"answer": "negative"}
    score, used = _score(tokens)
    if used == 0:
        joined = " ".join(tokens)
        if re.search(r"\b(?:why|whatever|huh|ugh|hmm|blah|meh)\b", joined):
            answer = "negative"
        elif re.search(r"\b(?:portrait|meditation|study|journey|chronicle|exploration|ode|tribute|celebration)\b", joined):
            answer = "positive"
        elif len(tokens) <= 5 and any(w in {"just", "only", "another", "again"}
                                     for w in tokens):
            answer = "negative"
        elif re.search(r"\b(?:minutes|hours|hour|minute)\b", joined) and any(
                w in {"long", "feels", "seems", "lasts"} for w in tokens):
            answer = "negative"
        else:
            answer = "positive"
    else:
        answer = "positive" if score > 0.05 else "negative"
    return {"answer": answer}