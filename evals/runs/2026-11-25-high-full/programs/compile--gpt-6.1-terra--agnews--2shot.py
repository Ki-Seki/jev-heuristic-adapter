import re


def _compile_terms(text):
    terms = [term.strip().casefold() for term in text.split("|") if term.strip()]
    patterns = []
    for term in sorted(set(terms), key=len, reverse=True):
        parts = re.split(r"[\s-]+", term)
        pattern = r"[\s-]+".join(re.escape(part) for part in parts)
        last = parts[-1]
        if len(last) > 3 and last.isalpha() and not last.endswith(("s", "x", "y")):
            pattern += r"(?:s|es)?"
        patterns.append(pattern)
    return re.compile(r"(?<!\w)(?:" + "|".join(patterns) + r")(?!\w)")


_RULES = {
    "sports": [
        (3.0, 30, """
            super bowl|world series|stanley cup|nba finals|nfl draft|
            champions league|premier league|major league baseball|national football league|
            national basketball association|national hockey league|world cup|
            ryder cup|davis cup|fed cup|tour de france|formula one|formula 1|
            grand slam|wimbledon|roland garros|australian open|us open tennis|
            indianapolis 500|daytona 500|kentucky derby|olympic games|olympics|
            paralympics|uefa|fifa|ncaa|mlb|nba|wnba|nfl|nhl|nascar|pga tour|
            la liga|bundesliga|serie a|fa cup|six nations
        """),
        (2.1, 25, """
            baseball|basketball|football|soccer|tennis|hockey|cricket|rugby|
            volleyball|softball|badminton|golf|golfer|golfing|boxing|boxer|
            wrestling|wrestler|motorsport|motorsports|cycling|cyclist|
            gymnastics|gymnast|swimming|swimmer|skating|skater|skiing|skier|
            snowboard|snowboarding|athletics|decathlon|triathlon|marathon|
            racecourse|racetrack|horse racing|horse race|race car|racing driver|
            martial arts|heavyweight|middleweight|welterweight|featherweight|
            quarterback|running back|wide receiver|linebacker|touchdown|
            quarterbacked|pitcher|pitching|bullpen|shortstop|home run|
            home runs|homer|homered|grand slam homer|strikeout|strikeouts|
            inning|innings|batter|batting|dugout|goalkeeper|goalie|striker|
            midfielder|defender|hat trick|penalty shootout|penalty kick|
            free kick|field goal|three pointer|three point|rebound|dunk|
            pole position|pit stop|rbi|runs batted in|yard touchdown|
            fixture list|transfer window|transfer fee|loan deal|playoffs|
            postseason|semifinal|semifinals|quarterfinal|quarterfinals|
            tie breaker|tiebreaker|match point|set point|deuce|knockout stage|
            league title|league championship|championship game|title game|
            world champion|world championship|gold medal|silver medal|bronze medal|
            medalist|medallist|podium finish|seeded player|top seed|top seeded|
            sportswriter|sports league|sporting event|sports team|sports season
        """),
        (2.0, 25, """
            new york yankees|boston red sox|chicago cubs|chicago white sox|
            los angeles dodgers|san francisco giants|new york mets|atlanta braves|
            st louis cardinals|detroit tigers|philadelphia phillies|houston astros|
            texas rangers|oakland athletics|seattle mariners|toronto blue jays|
            cleveland indians|cleveland guardians|baltimore orioles|
            new england patriots|dallas cowboys|new york giants|new york jets|
            green bay packers|pittsburgh steelers|philadelphia eagles|
            san francisco 49ers|kansas city chiefs|denver broncos|
            indianapolis colts|miami dolphins|chicago bears|detroit lions|
            minnesota vikings|baltimore ravens|buffalo bills|las vegas raiders|
            oakland raiders|new orleans saints|tampa bay buccaneers|
            los angeles lakers|boston celtics|chicago bulls|miami heat|
            golden state warriors|san antonio spurs|cleveland cavaliers|
            detroit pistons|new york knicks|houston rockets|phoenix suns|
            toronto maple leafs|montreal canadiens|detroit red wings|
            manchester united|manchester city|real madrid|atletico madrid|
            barcelona fc|fc barcelona|bayern munich|borussia dortmund|
            liverpool fc|arsenal fc|chelsea fc|tottenham hotspur|
            juventus|ac milan|inter milan|paris saint germain|
            all blacks|new zealand all blacks
        """),
        (1.8, 25, """
            yankees|red sox|dodgers|mets|phillies|astros|orioles|blue jays|
            packers|steelers|cowboys|broncos|colts|49ers|buccaneers|
            celtics|lakers|knicks|cavaliers|warriors|pistons|
            maple leafs|canadiens|red wings|arsenal|liverpool|chelsea|
            michael jordan|lebron james|kobe bryant|shaquille o'neal|
            tiger woods|phil mickelson|serena williams|venus williams|
            roger federer|rafael nadal|novak djokovic|andy roddick|
            andy murray|maria sharapova|andre agassi|pete sampras|
            michael schumacher|lewis hamilton|max verstappen|
            lance armstrong|usain bolt|michael phelps|
            david beckham|lionel messi|cristiano ronaldo|ronaldo|pele|
            wayne rooney|zinedine zidane|diego maradona|
            tom brady|peyton manning|patrick mahomes|joe montana|
            barry bonds|alex rodriguez|derek jeter|babe ruth|
            mike tyson|muhammad ali|floyd mayweather|manny pacquiao
        """),
        (1.0, 18, """
            sport|sports|athlete|athletes|player|players|coach|coaching|
            referee|umpire|opponent|teammate|squad|roster|league|
            tournament|match|matches|rematch|game|games|season|
            scored|scoring|scoreboard|final score|goals|goal|
            victory|defeat|defeated|beat|beats|beaten|edged|
            championship|champion|champions|finalist|finals|
            playoff|playoff berth|qualifying round|qualifier|
            unbeaten|undefeated|winning streak|losing streak|
            extra time|overtime|injury time|halftime|half time|
            first half|second half|first round|second round|
            third round|fourth round|last inning|opening day|
            defending champion|title contender|captain|fans|
            win over|victory over|loss to|lost to|wins over
        """),
    ],
    "business": [
        (3.0, 28, """
            stock market|stock markets|stock exchange|stock index|stock indexes|
            stock indices|share market|share price|share prices|stock price|
            stock prices|wall street|dow jones|dow industrials|s&p 500|
            standard and poor's|nasdaq composite|nasdaq index|ftse 100|
            nikkei average|nikkei index|bond market|bond yield|treasury yield|
            treasury bond|initial public offering|ipo|economic growth|
            gross domestic product|consumer price index|producer price index|
            interest rate|interest rates|federal reserve|central bank|
            federal funds rate|monetary policy|trade deficit|trade surplus|
            budget deficit|unemployment rate|jobless rate|nonfarm payrolls|
            payroll report|employment report|economic outlook|economic data|
            consumer spending|retail sales|housing market|home sales|
            crude oil|oil price|oil prices|oil futures|oil market|
            oil barrel|barrel of oil|price of oil|natural gas prices|
            commodity prices|commodities market|merger agreement|
            merger deal|takeover bid|takeover offer|hostile takeover|
            acquisition deal|bankruptcy protection|chapter 11 bankruptcy|
            quarterly earnings|quarterly profit|quarterly loss|
            earnings report|earnings forecast|profit forecast|profit warning|
            revenue forecast|sales forecast|financial results|
            fiscal quarter|fiscal year|annual profit|net income|
            net profit|net loss|operating profit|operating loss
        """),
        (2.0, 28, """
            shares|shareholders|shareholder|stockholder|stockholders|
            equities|equity market|investor|investors|investment bank|
            investment banking|brokerage|stockbroker|broker|trading session|
            market trading|market rally|market selloff|market sell off|
            stocks rose|stocks fell|stocks gain|stocks decline|stocks tumble|
            shares rose|shares fell|shares gain|shares decline|
            share buyback|stock buyback|dividend|dividends|bond yields|
            futures trading|crude futures|oil futures|gold futures|
            currency market|foreign exchange|exchange rate|dollar fell|
            dollar rose|weak dollar|strong dollar|yen rose|euro rose|
            inflation|deflation|recession|economic slowdown|economic recovery|
            consumer confidence|business confidence|manufacturing activity|
            manufacturing sector|manufacturing output|factory orders|
            industrial production|mortgage rate|mortgage lender|
            foreclosure|homebuyer|homebuilder|housing prices|
            earnings|earnings per share|profits|profit|revenue|revenues|
            sales revenue|turnover|dividend payment|quarterly results|
            financial report|balance sheet|cash flow|fiscal|
            merger|mergers|acquisition|acquisitions|takeover|buyout|
            private equity|venture capital|hedge fund|mutual fund|
            bankruptcy|bankrupt|insolvency|creditor|debt restructuring|
            antitrust regulator|securities regulator|securities fraud|
            accounting scandal|accounting fraud|insider trading|
            labor market|labour market|jobless claims|job cuts|
            layoffs|layoff|job losses|job creation|wage growth|
            consumer prices|wholesale prices|oil producer|oil production|
            petroleum|opec|oil refinery|oil reserves|barrel|
            airline industry|airline carrier|airline passenger|
            commercial airline|air carrier|flight bookings|
            retail chain|retailer|retailing|department store|
            retail giant|shopping mall|automaker|automobile manufacturer|
            carmaker|auto industry|car industry|vehicle sales|
            manufacturing plant|factory workers|trade agreement|
            world trade organization|tariff|tariffs|trade dispute|
            import duties|export growth|exports|imports|commodity|
            commodities|corporate restructuring|business deal|
            financial services|insurance company|insurance industry
        """),
        (1.9, 25, """
            morgan stanley|goldman sachs|jpmorgan|jp morgan|citigroup|
            citibank|bank of america|wells fargo|lehman brothers|
            merrill lynch|credit suisse|deutsche bank|barclays|hsbc|
            american express|mastercard|visa inc|berkshire hathaway|
            general motors|ford motor|toyota|honda motor|volkswagen|
            daimlerchrysler|daimler|chrysler|boeing|airbus|
            exxonmobil|exxon mobil|chevron|conocophillips|royal dutch shell|
            british petroleum|saudi aramco|halliburton|
            walmart|wal mart|costco|home depot|kroger|tesco|
            coca cola|pepsico|mcdonald's|starbucks|procter and gamble|
            general electric|general mills|johnson and johnson|
            pfizer|merck|glaxosmithkline|astrazeneca|
            united airlines|american airlines|delta air lines|
            southwest airlines|british airways|lufthansa|
            northwest airlines|continental airlines|us airways|
            world bank|international monetary fund
        """),
        (0.9, 15, """
            economy|economic|financial|finance|business|businesses|
            company|companies|corporation|corporate|industry|industrial|
            commercial|market|markets|stock|stocks|share|bank|banks|
            banker|banking|lender|loan|loans|credit|debt|fund|funds|
            investment|investments|investing|capital|assets|asset|
            sales|sale|sold|buy|buying|purchase|purchased|
            price|prices|cost|costs|revenue|income|loss|losses|
            employment|unemployment|wages|jobs|workers|employer|
            factory|factories|production|supply|demand|distribution|
            consumer|consumers|customer|customers|retail|wholesale|
            airline|airlines|airfare|airfares|flight cancellations|
            trade|trading|export|import|tariff|shipping|
            oil|gasoline|petrol|diesel|fuel|energy prices|
            dollar|dollars|euro|yen|pound sterling
        """),
    ],
    "sci_tech": [
        (3.0, 30, """
            microsoft|google|alphabet inc|ibm|intel|amd|nvidia|
            advanced micro devices|cisco systems|cisco|oracle corp|oracle|
            adobe systems|adobe|salesforce|hewlett packard|hewlett-packard|
            hewlett packard enterprise|hpe|dell computer|dell inc|dell|
            sun microsystems|sun microsystems inc|red hat|
            yahoo|lycos|aol|america online|netscape|mozilla|
            facebook|instagram|whatsapp|youtube|tiktok|twitter|linkedin|
            netflix|spotify|ebay|paypal|tencent|alibaba|baidu|
            samsung electronics|samsung|sony playstation|nintendo|
            electronic arts|ea sports|activision|ubisoft|sega|
            qualcomm|broadcom|arm holdings|tsmc|taiwan semiconductor|
            nokia|ericsson|motorola|blackberry|research in motion|
            huawei|xiaomi|oneplus|openai|chatgpt|anthropic|
            spaceX|spacex|blue origin|nasa|european space agency
        """),
        (2.5, 30, """
            computer virus|computer viruses|computer worm|computer worms|
            cyber attack|cyber attacks|cyberattack|cyberattacks|cybersecurity|
            computer security|network security|security vulnerability|
            security flaw|software flaw|data breach|data breaches|
            malware|ransomware|spyware|phishing|keylogger|keystrokes|
            password theft|stolen passwords|screensaver|
            computer software|software update|software patch|software bug|
            operating system|windows xp|windows vista|windows 10|windows 11|
            microsoft windows|windows operating system|linux|macos|
            android operating system|ios operating system|open source|
            web browser|internet browser|search engine|search engines|
            search results|world wide web|web site|website|websites|
            web page|web pages|online search|online advertising|
            social media|social network|social networking|
            internet service|internet access|internet provider|broadband|
            wireless internet|wi fi|wifi|wi-fi|bluetooth|
            computer network|computer networks|wireless network|
            mobile network|telecommunications|telecoms|telecom industry|
            mobile phone|mobile phones|cell phone|cell phones|cellphone|
            smartphone|smartphones|smart phone|smart phones|
            iphone|ipad|ipod|macbook|imac|apple watch|apple computer|
            android phone|android phones|tablet computer|
            personal computer|desktop computer|laptop computer|
            laptop|laptops|pc maker|computer maker|computer makers|
            computer chip|computer chips|microchip|microprocessor|
            semiconductor|semiconductors|chip maker|chipmaker|chip makers|
            graphics processor|graphics card|computer processor|
            computer hardware|hard drive|hard disk|memory chip|
            flash memory|data center|data centre|cloud computing|
            artificial intelligence|machine learning|generative ai|
            neural network|large language model|language models|
            robotics|robotic|robots|virtual reality|augmented reality|
            video game|video games|videogame|videogames|gaming console|
            game console|game consoles|playstation|xbox|gamecube|
            virtual world|online gaming|computer game|computer games|
            digital camera|digital cameras|digital music|mp3 player|
            email|e mail|electronic mail|text message|text messaging|
            download|downloads|downloaded|downloading|upload|
            internet auction|online auction|e commerce|ecommerce|
            software developer|software developers|software company|
            technology company|technology companies|tech company|tech companies|
            information technology|information security|computer programming|
            programming language|source code|computer code|computer system|
            computer systems|personal computers|computer user|computer users
        """),
        (2.3, 30, """
            scientific research|medical research|medical study|scientific study|
            clinical trial|clinical trials|human trial|drug trial|drug trials|
            laboratory experiment|laboratory tests|peer reviewed|
            journal of medicine|medical journal|science journal|
            researchers found|researchers have found|researchers say|
            scientists found|scientists have found|scientists say|
            genome|genomics|genetic mutation|genetic mutations|
            genetic engineering|gene therapy|gene editing|crispr|
            dna sequence|dna sequencing|stem cell|stem cells|
            embryo|embryonic|cloning|cloned|biotechnology|biotech|
            cancer treatment|cancer therapy|cancer vaccine|cancer drug|
            cancer research|breast cancer|lung cancer|prostate cancer|
            alzheimer's disease|alzheimer disease|parkinson's disease|
            hiv vaccine|vaccine trial|new vaccine|experimental vaccine|
            experimental drug|new drug|drug discovery|drug development|
            drug approval|fda approval|food and drug administration approval|
            medical device|new treatment|experimental treatment|
            human brain|brain cells|brain scan|brain imaging|
            blood cells|blood test|immune system|antibody|antibodies|
            pathogen|pathogens|bacteria|bacterial|microbe|microbial|
            telescope|observatory|astronomer|astronomers|astronomy|
            astrophysics|cosmology|planetary science|solar system|
            spacecraft|space shuttle|space station|space probe|space mission|
            space exploration|space telescope|space flight|spaceflight|
            rocket launch|rocket launched|mars rover|mars mission|
            lunar mission|moon landing|moon mission|astronaut|astronauts|
            satellite launch|exoplanet|black hole|neutron star|
            distant galaxy|galaxies|galaxy|universe|asteroid|comet|
            dinosaur|fossil|fossils|paleontology|palaeontology|
            archaeologist|archaeologists|archaeology|archaeological|
            evolution|evolutionary|species discovery|new species|
            quantum computing|quantum computer|quantum physics|
            nuclear physics|particle physics|particle accelerator|
            scientific discovery|scientific breakthrough|medical breakthrough
        """),
        (1.1, 20, """
            technology|technological|tech|software|hardware|computer|
            computers|computing|internet|online|digital|cyber|hacker|
            hackers|hacking|hacked|password|passwords|encryption|
            encrypted|database|databases|algorithm|algorithms|app|apps|
            application software|operating systems|browser|browsers|
            website|websites|webmaster|webmasters|web|server|servers|
            chip|chips|processor|processors|silicon|microchip|
            handset|handsets|telecom|wireless|broadband|
            gadget|gadgets|electronics|electronic device|
            satellite|satellites|rocket|rockets|spacecraft|
            planet|planets|mars|jupiter|saturn|asteroid|
            science|scientific|scientist|scientists|researcher|researchers|
            laboratory|laboratories|experiment|experiments|
            biomedical|medical research|medicine|medical|treatment|
            genetics|genetic|gene|genes|dna|protein|molecule|molecules|
            cells|cellular|virus|viruses|viral|vaccine|vaccines|
            disease|diseases|cancer|diabetes|infection|infections|
            patients|patient|therapy|therapies|drug|drugs|
            physics|physicist|chemistry|chemist|biology|biologist|
            neuroscience|ecology|climate science|climate change research|
            research study|new study|study found|study finds
        """),
    ],
    "world": [
        (2.7, 30, """
            presidential election|presidential candidate|presidential campaign|
            general election|parliamentary election|national election|
            election campaign|election results|election result|
            election victory|election day|polling station|polling stations|
            political party|opposition party|ruling party|voter turnout|
            prime minister|foreign minister|defense minister|defence minister|
            interior minister|finance minister|foreign secretary|
            secretary of state|head of state|head of government|
            white house|white house spokesman|oval office|
            united nations|united nations security council|security council|
            european union|european commission|european parliament|
            north atlantic treaty organization|nato|
            peace talks|peace deal|peace treaty|ceasefire|cease fire|
            peace process|peace agreement|peace negotiations|
            military forces|armed forces|army troops|military operation|
            military offensive|ground offensive|air strike|air strikes|airstrike|
            airstrikes|missile strike|rocket attack|suicide bomber|
            suicide bombing|car bomb|roadside bomb|bomb blast|bomb explosion|
            terrorist attack|terrorist attacks|terror attack|terror attacks|
            terror group|terrorist group|terrorism|terrorist|terrorists|
            civil war|war zone|war crimes|war crime|armed conflict|
            insurgent|insurgents|insurgency|militant|militants|
            rebel forces|rebel fighters|rebel group|rebel groups|
            invasion|invaded|occupation forces|troop withdrawal|
            soldiers killed|troops killed|civilians killed|
            police investigation|police officer|police officers|
            law enforcement|criminal investigation|murder investigation|
            murder suspect|murder trial|murder charge|murder charges|
            charged with murder|charged with killing|charged with rape|
            found guilty|guilty verdict|death sentence|death penalty|
            prison sentence|sentenced to prison|sentenced to death|
            mass shooting|school shooting|hostage crisis|hostage taking|
            natural disaster|earthquake|earthquakes|tsunami|tsunamis|
            hurricane|hurricanes|typhoon|typhoons|tornado|tornadoes|
            volcanic eruption|major flooding|flash flood|floodwaters|
            plane crash|airplane crash|aircraft crash|train crash|
            train derailment|train collision|shipwreck|ferry disaster|
            building collapse|rescue workers|emergency services
        """),
        (1.8, 27, """
            election|elections|elected|reelection|re election|ballot|
            ballots|polls|polling|referendum|voters|voting|vote count|
            campaign trail|presidential debate|political debate|
            democratic candidate|republican candidate|democrats|republicans|
            congress|congressional|parliament|parliamentary|legislature|
            senate|senator|senators|governor|governors|mayor|mayors|
            president|presidential|premier|chancellor|cabinet minister|
            government|governments|government officials|government spokesman|
            politician|politicians|political|politics|diplomatic|diplomacy|
            diplomat|diplomats|ambassador|embassy|consulate|
            bilateral talks|foreign policy|international relations|
            international sanctions|economic sanctions|sanctions imposed|
            human rights|civil rights|constitution|constitutional|
            supreme court|high court ruling|judge ruled|court ruling|
            indictment|indicted|prosecutor|prosecutors|prosecution|
            arrested|arrest|arrests|detained|detention|prisoner|prisoners|
            convicted|conviction|sentenced|sentencing|criminal charges|
            suspect|suspects|murder|murdered|homicide|rape|robbery|
            kidnapping|kidnapped|abducted|hostage|hostages|
            gunman|gunmen|shooter|shooting|shootings|stabbed|
            police|policeman|policewoman|detectives|
            bomb|bombs|bombed|bombing|bombings|explosion|explosions|
            gunfire|shelling|missile attack|missiles fired|
            soldiers|troops|military|army|navy|air force|
            battlefield|fighting|combat|warfare|war|
            rebel|rebels|guerrilla|guerrillas|jihadist|
            refugees|refugee|displaced people|civilian casualties|
            dead|deaths|death toll|killed|wounded|casualties|
            disaster|disasters|flooding|floods|wildfire|wildfires|
            landslide|landslides|mudslide|drought|storm|storms|
            evacuees|evacuation|evacuated|rescue teams|firefighters|
            cyclone|cyclones|blizzard|avalanche|eruption
        """),
        (1.5, 24, """
            george w bush|george bush|president bush|bush administration|
            john kerry|kerry campaign|barack obama|president obama|
            donald trump|president trump|joe biden|president biden|
            bill clinton|hillary clinton|president clinton|
            tony blair|gordon brown|rishi sunak|keir starmer|
            vladimir putin|president putin|volodymyr zelensky|
            xi jinping|kim jong un|kim jong il|saddam hussein|
            osama bin laden|bin laden|al qaeda|al qaida|isis|islamic state|
            taliban|hamas|hezbollah|hezbollah fighters|
            benjamin netanyahu|ariel sharon|yasser arafat|
            mahmoud abbas|pope francis|pope john paul|
            iraqi forces|iraqi government|iraq war|war in iraq|
            afghan forces|afghan government|war in afghanistan|
            israeli forces|israeli military|palestinian militants|
            gaza strip|west bank|middle east conflict|
            russian forces|ukrainian forces|russian invasion
        """),
        (0.8, 12, """
            iraq|iraqi|afghanistan|afghan|iran|iranian|
            israel|israeli|palestine|palestinian|palestinians|gaza|
            syria|syrian|lebanon|lebanese|pakistan|pakistani|
            ukraine|ukrainian|russia|russian|north korea|south korea|
            sudan|darfur|somalia|yemen|libya|haiti|
            baghdad|kabul|jerusalem|beirut|damascus|
            washington|united nations|international community|
            authorities|officials|official said|police said|
            voters|protest|protests|protesters|demonstration|
            protesters|demonstrators|rally against|humanitarian|
            treaty|diplomatic relations|border dispute
        """),
    ],
}


_COMPILED = {
    category: [(weight, cap, _compile_terms(terms)) for weight, cap, terms in groups]
    for category, groups in _RULES.items()
}

_TECH_COMPANY = re.compile(
    r"\b(?:microsoft|google|ibm|intel|nvidia|amd|cisco|oracle|adobe|"
    r"yahoo|lycos|aol|mozilla|facebook|instagram|whatsapp|youtube|"
    r"tiktok|twitter|linkedin|netflix|spotify|ebay|paypal|tencent|"
    r"alibaba|baidu|samsung|nintendo|qualcomm|broadcom|nokia|"
    r"ericsson|motorola|blackberry|huawei|openai|spacex|dell)\b"
)
_MARKET_ROUNDUP = re.compile(
    r"\b(?:stock markets?|stocks|wall street|dow jones|nasdaq|"
    r"equities|shares|financial markets?)\b"
)
_SPORT_ANCHOR = re.compile(
    r"\b(?:sports?|football|soccer|baseball|basketball|tennis|hockey|"
    r"cricket|rugby|golf|league|team|player|match|tournament|"
    r"nfl|nba|nhl|mlb|fifa|uefa|ncaa|olympics|innings?|goal|"
    r"playoffs?|quarterback|pitcher|coach)\b"
)
_SPORT_LEAGUE = re.compile(
    r"\b(?:nfl|nba|nhl|mlb|fifa|uefa|ncaa|wimbledon|"
    r"premier league|champions league|world cup|super bowl|world series)\b"
)
_GAME_TECH = re.compile(
    r"\b(?:video games?|videogames?|computer games?|gaming console|"
    r"game console|playstation|xbox|nintendo|electronic arts|ea sports)\b"
)
_CYBER = re.compile(
    r"\b(?:cyber|computer|internet|software|malware|ransomware|"
    r"spyware|phishing|hackers?|hacking|passwords?|screensaver)\b"
)
_RESEARCH = re.compile(
    r"\b(?:researchers?|scientists?|clinical|laboratory|experiment|"
    r"medical study|scientific study|medical research|scientific research)\b"
)
_SCI_SUBJECT = re.compile(
    r"\b(?:health|medical|medicine|patients?|disease|cancer|treatment|"
    r"vaccines?|drugs?|genes?|genetic|dna|brain|cells?|biology|"
    r"species|animals?|plants?|fossils?|climate|physics|chemistry|"
    r"planets?|space|astronomy|universe|materials?|energy|virus|viruses)\b"
)


def _normalize(text):
    text = text.casefold()
    text = text.replace("&#39;", "'").replace("&#039;", "'")
    text = text.replace("&apos;", "'").replace("&quot;", '"')
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("–", "-").replace("—", "-")
    text = text.replace("\\$", "$").replace("\\n", " ")
    return re.sub(r"\s+", " ", text).strip()


def _get_text(state):
    if isinstance(state, str):
        return state
    if isinstance(state, dict):
        for key in ("text", "article", "content", "description", "headline"):
            value = state.get(key)
            if isinstance(value, str):
                return value
    return ""


def predict(state):
    text = _normalize(_get_text(state))
    if not text:
        return {"answer": "world"}

    words = list(re.finditer(r"\S+", text))
    headline_end = words[min(17, len(words) - 1)].end()
    scores = {category: 0.0 for category in _COMPILED}

    for category, groups in _COMPILED.items():
        for weight, cap, pattern in groups:
            seen = set()
            subtotal = 0.0
            for match in pattern.finditer(text):
                term = match.group()
                if term in seen:
                    continue
                seen.add(term)
                multiplier = 1.3 if match.start() < headline_end else 1.0
                subtotal += weight * multiplier
                if subtotal >= cap:
                    subtotal = cap
                    break
            scores[category] += subtotal

    first = text[:headline_end]
    first_100 = text[:100]
    tech_company = _TECH_COMPANY.search(text)
    if tech_company:
        bonus = 2.0
        if tech_company.start() < headline_end:
            bonus += 2.0
        if _MARKET_ROUNDUP.search(first_100) and tech_company.start() >= headline_end:
            bonus -= 1.5
        scores["sci_tech"] += bonus

    if re.search(r"\bapple\b", text):
        if re.search(
            r"\b(?:iphone|ipad|ipod|macbook|macintosh|app store|"
            r"tim cook|steve jobs|computer|technology|tech|software|"
            r"electronics|shares|stock|earnings|company|inc)\b",
            text,
        ):
            scores["sci_tech"] += 5.0 if re.search(r"\bapple\b", first) else 3.0
        elif not re.search(r"\b(?:fruit|orchard|growers?|harvest|juice|trees?)\b", text):
            scores["sci_tech"] += 1.5

    if re.search(r"\bamazon\b", text):
        if re.search(
            r"\b(?:rainforest|rain forest|river|jungle|forest|basin|"
            r"deforestation|indigenous)\b",
            text,
        ):
            pass
        elif re.search(
            r"\b(?:online|internet|web|retailer|shopping|cloud|"
            r"aws|kindle|bezos|e commerce|company|shares|stock|"
            r"earnings|com|customers?)\b",
            text,
        ):
            scores["sci_tech"] += 4.0 if re.search(r"\bamazon\b", first) else 2.5
        else:
            scores["sci_tech"] += 1.0

    if _SPORT_LEAGUE.search(first):
        scores["sports"] += 2.0

    if _SPORT_ANCHOR.search(text):
        if re.search(r"(?<!\d)\d{1,3}\s*[-:]\s*\d{1,3}(?!\d)", text):
            scores["sports"] += 2.5
        if re.search(
            r"\b(?:beat|beats|defeated|edged|routed|outscored|"
            r"overtime|playoff|semifinal|quarterfinal|touchdown|inning)\b",
            text,
        ):
            scores["sports"] += 1.5

    if _GAME_TECH.search(text):
        scores["sci_tech"] += 3.0
        if _GAME_TECH.search(first):
            scores["sci_tech"] += 1.5

    if _CYBER.search(text):
        scores["sci_tech"] += 1.5
        if re.search(r"\b(?:virus|worm|attack|security|breach|infected)\b", text):
            scores["sci_tech"] += 1.5

    if _RESEARCH.search(text) and _SCI_SUBJECT.search(text):
        scores["sci_tech"] += 2.0

    if _MARKET_ROUNDUP.search(first_100):
        if re.search(
            r"\b(?:rose|fell|fall|rise|rally|rallied|gained|gain|"
            r"declined|decline|dropped|drop|higher|lower|"
            r"surged|tumbled|trading|investors)\b",
            text,
        ):
            scores["business"] += 2.5

    if re.search(
        r"\b(?:oil|crude|gasoline|petrol|fuel)\b", first_100
    ) and re.search(
        r"\b(?:prices?|barrel|futures|market|trading|cost|"
        r"surged|rose|fell|rise|fall)\b",
        text,
    ):
        scores["business"] += 2.0

    if re.search(
        r"\b(?:killed|dead|murdered|arrested|bombing|election|"
        r"earthquake|hurricane|tsunami|shooting)\b",
        first_100,
    ):
        scores["world"] += 1.0

    # In a tie, favor the broad news category over an unsupported guess.
    order = ("world", "business", "sci_tech", "sports")
    answer = max(order, key=lambda category: scores[category])
    return {"answer": answer}