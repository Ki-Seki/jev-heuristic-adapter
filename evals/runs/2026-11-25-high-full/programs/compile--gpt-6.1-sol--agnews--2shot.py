import re
import math
import unicodedata
from collections import Counter

_LABELS = ("business", "sci_tech", "sports", "world")


def _normalize(text):
    text = unicodedata.normalize("NFKC", text).lower()
    text = re.sub(r"&(?:amp|#38);", " and ", text)
    text = re.sub(r"&(?:quot|#34);", " ", text)
    text = re.sub(r"&(?:apos|#39);", " ", text)
    text = re.sub(r"&[a-z]+;", " ", text)
    text = re.sub(r"<[^>]*>", " ", text)
    text = re.sub(r"\b(?:[a-z]\.){2,}", lambda m: m.group().replace(".", ""), text)
    text = re.sub(r"\be[\s-]+mail\b", "email", text)
    text = re.sub(r"\bon[\s-]+line\b", "online", text)
    text = re.sub(r"\bwi[\s-]+fi\b", "wifi", text)
    text = re.sub(r"\bweb[\s-]+site\b", "website", text)
    text = text.replace("&", " and ")
    text = text.replace("$", " dollar ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


_WORD_GROUPS = {
    "business": [
        (5.4, """
            merger acquisition bankruptcy recession inflation deflation
            dividend shareholder stockholder economist brokerage
            privatization privatisation insolvency liquidation
        """),
        (4.5, """
            earnings profit revenue stock equity equities bond commodity
            currency forex banking banker insurer mortgage
            acquisition takeover buyout bailout divestiture
            unemployment payroll inflationary restructuring
            automaker retailer wholesaler
        """),
        (3.4, """
            economy economic financial finance fiscal monetary
            investor investment investing trading trader
            shares shareholding shareholder profitability
            sales sale pricing priced price crude petroleum gasoline
            gold bullion copper steel aluminum aluminium
            dollar yen euro sterling yuan rupee
            insurer insurance pension retirement
            deficit surplus budget lender lending
            airline airlines aviation bankruptcy bankrupt
            retail corporate corporation
            accountant accounting audit auditor
            broker brokerage futures securities
            factory manufacturing manufacturer
            export import tariff
            labor labour unionized unionised
        """),
        (2.5, """
            market money bank credit debt loan
            business commerce commercial industry industrial
            oil energy fuel diesel opec
            entrepreneur entrepreneurship startup
            employment jobless workforce layoffs layoff downsizing
            wages salary salaries compensation
            consumer spending consumption
            economists analysts analyst forecasts forecast
            expenditure expenditures productivity output
            merger merged merge acquired acquiring
            franchising franchise supermarket
            cash cashflow liquidity capital
            conglomerate monopoly cartel
            antitrust auction bid bidding
            carrier freight shipping shipbuilding
            tourism tourist hotel hotels
            pharmaceuticals pharmaceutical drugmaker
            quarterly quarter
            textiles agriculture agricultural farming crop harvest
        """),
        (1.5, """
            company companies firm firms enterprise enterprises
            employer employee worker staff union
            chief executive ceo cfo
            deal contract purchase purchased
            sell selling sold buy buying bought
            negotiate negotiations negotiation
            tax taxation taxes
            growth slowdown recovery confidence
            loss losses outlook
            revenue revenues proceeds
            regulatory regulator regulators
            fine fined settlement
            fare fares passenger passengers
            automotive dealership
            advertising advertisement advertiser
            franchise distributor distribution
            producer production supply demand
            businessweek forbes
            transaction payment payable payable
            earnings report
        """),
        (0.65, """
            million billion trillion percent percentage pct
            annual yearend rose rise rising fell falling
            expensive cheap cheaper discount
            plan plans strategy strategic
            costs cost cut cuts
            expansion expand worldwide global
            film movie hollywood entertainment
        """),
    ],
    "sci_tech": [
        (6.0, """
            software hardware internet cyberspace broadband
            spyware malware phishing ransomware cyberattack
            hacker hacking cybersecurity
            genome genomics biotechnology nanotechnology
            astronaut spacecraft exoplanet astrophysics
            neuroscience
        """),
        (5.0, """
            computer computing programmer programming
            browser searchengine website
            semiconductor microprocessor chipset
            telecom telecommunications
            wireless wifi bluetooth
            linux unix
            spam spammer worm trojan
            supercomputer supercomputing
            scientist scientific
            astronomer astronomy astrophysicist
            palaeontology paleontology archaeology
            cloning cloned
            nasa esa
            robotics robotic
            videogame videogames
        """),
        (4.0, """
            technology technological tech
            network networking router server
            desktop laptop notebook workstation mainframe
            processor microchip chipmaker
            database encryption encrypted cryptography
            download upload firewall antivirus
            podcast blogging blogger blog
            email web online
            broadband modem ethernet
            cellphone smartphone handset
            nanotech biotech
            dna rna genetic genetics
            researcher research
            experiment experimental laboratory
            physicist physics
            satellite orbit orbital
            astronaut cosmonaut
            lunar martian
            telescope observatory
            rover lander
            fossil dinosaur
            quantum particle
            vaccine vaccination
            neuroscientist
            algorithm
        """),
        (3.0, """
            chip chips silicon memory
            console joystick playstation xbox gamecube
            dvd cdrom hdtv lcd oled
            digital electronic electronics
            cellphone cellular mobile
            telecommunication telephony voicemail
            voip 3g 4g 5g
            itunes ipod iphone ipad macintosh
            android app apps
            screensaver keystroke password
            cybercrime cybercriminal
            virus infected infection
            security vulnerability exploit
            pixel megapixel camera camcorder
            wireless
            space spaceflight aerospace
            shuttle rocket spacecraft
            mars saturn jupiter venus neptune pluto
            cassini huygens hubble
            galaxy galactic universe cosmology
            comet asteroid meteor meteorite
            discovery discoveries
            biologist biology biological
            geologist geology geological
            ecology ecological ecosystem
            evolution evolutionary
            molecule molecular protein
            enzyme chromosome
            embryo embryonic
            neuron neurological
            medical medicine biomedical
            clinical therapeutic therapy
            cancer diabetes alzheimer parkinson
            nutrition nutritional
            fda
            archaeologist archaeological
            paleontologist prehistoric
            seismologist seismic
            climate climatologist
            renewable photovoltaic
            mathematician mathematics
            robot
            touchscreen
            softwaremaker
        """),
        (2.0, """
            science technical
            application applications
            data database
            computing
            internet
            portal
            search
            storage
            disk disc
            portable
            developer development
            keyboard mouse printer scanner
            download downloaded
            video audio multimedia
            graphics graphic
            touchscreen
            touchscreen
            patent patented
            innovation innovative invention inventor
            electronic
            device gadget
            compatibility compatible
            communications communication
            connectivity
            wireless
            research
            study studies
            health healthcare
            drug pharmaceutical
            treatment diagnostic diagnosis
            disease hiv aids flu
            fertility reproductive
            stemcell
            obesity obese
            bacteria bacterial
            antibiotic antibiotics
            surgery surgical
            dementia
            longevity
            laboratory lab
            radiation radioactive
            hydrogen
            energy
            carbon greenhouse
            species extinction extinct
            primate
            ocean oceanography
            environmental environment
            antarctic arctic
            expedition
            solar
            earth
            probe
            artificial
            bot
            browser
        """),
        (0.75, """
            test testing tested
            university institute
            student
            mathematics math
            doctor physician
            hospital
            engineers engineer engineering
            experiment
            computerised computerized
            animation
            music
            internetbased
            electric
        """),
    ],
    "sports": [
        (6.0, """
            football soccer baseball basketball hockey tennis
            cricket rugby golf badminton volleyball
            handball softball lacrosse
            olympics paralympics
            nfl nba nhl mlb ncaa fifa uefa
            nascar
            touchdown quarterback linebacker
            wicket batsman bowler
            homer homerun
            triathlon decathlon pentathlon
        """),
        (5.0, """
            sport sports sporting athlete athletic
            olympic paralympic
            championship tournament champion
            coach coached coaching
            goalkeeper striker midfielder defender
            playoffs postseason
            medal medallist medalist
            grandprix
            doping
            referee umpire
            scorer striker
            jockey
            sprinter
            formulaone
            swimming swimmer
            gymnastics gymnast
            weightlifting wrestling wrestler
            boxing boxer
            cycling cyclist
            racing racer
            motocross
            skiing skier
            snowboarding snowboarder
            fencing fencer
            archery
            taekwondo judo karate
            rowing rower
            equestrian
            netball
        """),
        (4.0, """
            league
            match matches
            tournament
            defeat defeated
            semifinal semifinalist quarterfinal quarterfinalist
            finalist
            team teammate
            playoff
            cup
            trophy
            victory
            stadium ballpark
            arena
            roster
            franchise
            kickoff
            linebacker receiver
            interception fumble
            inning innings
            pitcher pitching catcher
            outfielder infielder shortstop
            baseball
            batter batting
            bullpen
            strikeout
            fastball
            slam
            ace aces
            seeded
            serve backhand forehand
            puck
            goaltender
            skater skating
            lockout
            championship
            preseason
            wicketkeeper
            bowled bowling
            overs
            innings
            lbw
            birdie birdies bogey eagle putt putting
            tee fairway
            golfer
            marathon
            sprint hurdles hurdle relay
            velodrome
            podium
            qualifying qualifier
        """),
        (2.8, """
            season
            player
            game
            captain skipper
            score scoring scorer
            goal
            win wins winner winning
            unbeaten undefeated
            beat beats beating
            defeat defeats
            final finals
            penalty
            offensive offense defensive defense
            coach
            club
            homefield
            overtime
            rebound
            assist
            dunk
            slugger
            baserunner
            yardage
            gridiron
            testmatch
            cricketer
            century
            wicket
            pace bowler
            roadrace
            rallying
            racetrack speedway raceway
            grandstand
            reins
            playoff
            injured injury
            comeback
            retiring retirement
            suspension suspended
            transfer
        """),
        (1.3, """
            race
            record
            round
            lead
            draw drew
            tie tied
            match
            rival rivalry
            contest
            rookie veteran
            debut
            fan fans
            crowd
            field
            bench
            net
            strike
            shot
            set sets
            run runs
            warmup
            practice training
            trainer
            performance
            fitness
            doubles singles
            open
            giants jets rangers kings bulls twins
            patriots yankees mets cubs reds braves astros
            lakers celtics knicks
            redskins steelers raiders packers eagles
            dodgers brewers marlins phillies
            canadiens penguins
            ferrari
            chelsea arsenal liverpool everton
            juventus inter
            ajax
            postseason
        """),
    ],
    "world": [
        (6.0, """
            terrorist terrorism
            assassination assassinated
            insurgent insurgency
            bombing bomber
            massacre genocide
            hostage kidnapping
            earthquake tsunami
            referendum
            coup
        """),
        (5.0, """
            war warfare
            troop troops
            military soldier
            rebel militant guerrilla
            bomb explosives explosion
            gunman gunmen
            killed killing
            murder murderer
            police
            election electoral
            parliament parliamentary
            diplomat diplomacy diplomatic
            hurricane typhoon cyclone
            flood flooding
            ceasefire
            refugee
            peacekeeping peacekeeper
            insurgents
            gunfire firefight
            terrorist
            prosecution prosecutor
            prison prisoner
            courtmartial
        """),
        (4.0, """
            president presidential
            minister premier
            government governmental
            politics political politician
            senate senator
            congress congressional
            lawmaker
            governor
            democrat republican
            democracy democratic
            campaign campaigning
            ballot
            vote voter voting
            elected reelection
            constitution constitutional
            cabinet
            embassy ambassador
            army navy naval
            marines
            pentagon
            missile nuclear
            weapons weapon
            armed
            attack assault ambush
            raid
            invasion occupation
            coalition
            rebellion
            terror
            palestinian israeli
            iraq iraqi afghanistan afghan
            taliban hamas hezbollah hizbollah
            qaeda
            gaza baghdad kabul
            darfur
            wounded injured casualties casualty
            arrest arrested
            charged
            convicted conviction
            sentencing sentenced
            crime criminal
            robbery rape
            jail jailed
            riot unrest
            protest protester
            disaster devastation
            evacuated evacuation
            wildfire
            famine
            humanitarian
        """),
        (2.7, """
            diplomat
            foreign
            nationalists nationalist
            independence
            autonomy
            opposition
            insurgency
            peace
            summit
            treaty
            sanctions sanction
            talks
            security
            defense defence
            border
            crossing
            checkpoint
            combat fighting battle
            troops
            killed
            dead death died dying
            violence violent
            shooting
            casualty
            explosion
            blast
            hostage
            rescue
            suspect suspected
            trial
            judge
            jury
            justice
            testimony witness
            indictment
            fugitive
            extradition
            corruption bribery
            scandal
            activist
            rights
            immigrant immigration
            asylum
            deportation
            islam islamic islamist
            muslim
            religious religion
            church catholic vatican pope
            bishop cardinal
            un nato
            iran iranian
            syria syrian
            lebanon lebanese
            palestine
            chechen chechnya
            sudan sudanese
            rwanda
            somalia somali
            serbia serbian
            kosovo
            jerusalem
            fallujah najaf mosul ramadi
            basra
            karachi islamabad
            beirut damascus
            tehran pyongyang
            kashmir
            belgrade
            storm
            eruption
            landslide avalanche
            drought
            crash collision
            funeral
            epidemic pandemic
        """),
        (1.5, """
            world international
            federal
            state
            public
            authority authorities official officials
            leader leadership
            legislation legislative law legal
            ruling
            regime
            decision
            court
            treaty
            coalition
            national
            municipal mayor
            council
            reform
            policy policies
            sanction
            relation relations
            meeting
            spy espionage
            intelligence
            gun rifle ammunition
            shot
            fire
            ship
            aid relief
            redcross
            civilian
            riot
            rally demonstration
            march
            surrender
            rebel
            jungle
            population
            school education student
            teacher
            hospital
            health
            outbreak
            infection
            rescue
            passenger
            victim
            death
            missing
            family
            couple
            resident
            singer actor actress celebrity
            filmstar
            festival
            religion
            ethnic
            tribal
            culture cultural
            heritage
            museum
            monarch monarchy king queen
            prince princess
            royal
            russia russian
            pakistan pakistani
            israel
            china chinese
            ukraine ukrainian
            indonesia indonesian
            philippine philippines
            taiwan taiwanese
            venezuela venezuelan
            haiti haitian
            nepal nepalese
            bangladesh bangladeshi
            myanmar burma
            zimbabwe
            liberia liberian
            ivory
            congo
            nigeria nigerian
        """),
        (0.65, """
            country nation
            british britain english england
            france french germany german
            europe european
            japan japanese
            india indian
            canada canadian
            australia australian
            spain spanish
            italy italian
            mexico mexican
            brazil brazilian
            argentina argentine
            ireland irish
            greece greek
            turkey turkish
            egypt egyptian
            morocco moroccan
            algeria algerian
            thailand thai
            malaysia malaysian
            singapore
            vietnam vietnamese
            cambodia cambodian
            laos
            southafrica
            kenya kenyan
            ethiopia ethiopian
            uganda
            tanzania
            london paris berlin tokyo beijing moscow
            rome madrid athens seoul
            washington
            brussels
            delhi
        """),
    ],
}

_PHRASE_GROUPS = {
    "business": [
        (8.0, """
            stock market|stock markets|stock exchange|wall street|
            federal reserve|interest rates|interest rate|
            crude oil prices|oil prices|oil price|
            trade deficit|trade surplus|gross domestic product|
            consumer prices|consumer price index|
            quarterly earnings|quarterly profit|quarterly profits|
            earnings per share|earnings forecast|profit warning|
            files for bankruptcy|filed for bankruptcy|bankruptcy protection|
            initial public offering|public offering|ipo market|
            retail sales|consumer spending|consumer confidence|
            box office
        """),
        (6.0, """
            dow jones|nasdaq composite|nikkei average|nikkei index|
            hang seng|s and p 500|ftse 100|blue chip|blue chips|
            stock prices|share prices|share price|stock price|
            oil futures|crude futures|oil market|barrel of oil|
            a barrel|per barrel|energy prices|gas prices|
            foreign exchange|exchange rate|exchange rates|
            central bank|bank of england|bank of japan|european central bank|
            trade talks|free trade|world trade organization|
            jobless claims|payroll report|jobs report|unemployment rate|
            labor market|labour market|employment report|
            net income|net profit|net loss|operating profit|
            financial results|financial markets|financial services|
            annual profit|full year profit|first quarter|second quarter|
            third quarter|fourth quarter|
            investment bank|investment banking|hedge fund|mutual fund|
            bond market|treasury bonds|treasury yields|
            budget deficit|budget surplus|
            housing market|home sales|home prices|house prices|
            real estate|mortgage rates|
            labor union|labour union|workers strike|
            annual meeting|shareholder meeting|
            credit rating|credit card|credit cards|
            chief financial officer|
            cost cutting|job cuts|cut jobs|cuts jobs|cutting jobs|
            business confidence|business outlook|
            raises bid|takeover bid|merger talks|
            market share|market value|market capitalization|
            supply chain|supply and demand
        """),
        (3.5, """
            chief executive officer|chief executive|chief financial|
            board of directors|corporate governance|
            sales rose|sales rise|sales fell|sales fall|
            sales growth|revenue growth|profit growth|
            earnings rose|earnings rise|earnings fall|
            profits rose|profits rise|profits fall|
            shares rose|shares rise|shares fell|shares fall|
            shares jumped|shares slid|shares dropped|
            stocks rose|stocks rise|stocks fell|stocks fall|
            beat estimates|beats estimates|beat expectations|beats expectations|
            earnings report|profit report|quarterly results|
            quarterly revenue|quarterly sales|
            percent stake|majority stake|minority stake|
            private equity|venture capital|
            buy back|share buyback|stock buyback|
            tax cuts|tax cut|tax rates|tax rate|
            economic growth|economic recovery|economic slowdown|
            economic outlook|economic data|economic indicators|
            manufacturing sector|service sector|business activity|
            airline industry|auto industry|automobile industry|
            insurance company|retail chain|department store|
            holiday shopping|christmas shopping|holiday sales|
            christmas sales|back to school sales|
            shopping mall|supermarket chain|
            price war|price hike|price increase|
            petroleum exporting countries|
            crude oil|natural gas|heating oil|jet fuel|
            us dollar|american dollar|us currency|
            commodity prices|gold prices|
            dollar higher|dollar lower|
            business plan|business model|
            mortgage lender|commercial bank|
            air fares|airline fares|
            wall street journal
        """),
    ],
    "sci_tech": [
        (8.0, """
            artificial intelligence|machine learning|deep learning|
            personal computer|personal computers|operating system|
            computer virus|computer worm|internet worm|
            computer security|internet security|cyber security|
            computer network|computer networks|
            search engine|search engines|web browser|web browsers|
            internet service provider|internet service providers|
            stem cell|stem cells|human cloning|
            human genome|gene therapy|genetic engineering|
            clinical trial|clinical trials|
            space station|space shuttle|space telescope|
            international space station|solar system|
            big bang|black hole|black holes|
            scientific research|medical research|
            video game|video games|computer game|computer games|
            mobile phone|mobile phones|cell phone|cell phones|
            cellular phone|cellular phones|
            wireless internet|wireless network|wireless networks|
            open source|source code|
            high tech|high technology|information technology|
            information technologies|
            data breach|data breaches|
            internet explorer|
            e commerce|e business
        """),
        (6.0, """
            hard drive|hard disk|flash memory|memory chip|
            memory chips|silicon chip|silicon chips|
            micro computer|micro processor|
            chip maker|chip makers|software maker|software makers|
            software company|software companies|computer maker|
            computer makers|pc maker|pc makers|
            web site|web sites|web page|web pages|
            web search|internet search|desktop search|
            internet portal|web portal|online search|
            online music|digital music|music download|music downloads|
            file sharing|file swapping|peer to peer|
            online gaming|online game|online games|
            gaming console|game console|games console|
            digital camera|digital cameras|
            digital television|digital tv|
            high definition|liquid crystal|
            flat panel|flat screen|plasma screen|
            mobile computing|wireless broadband|
            broadband service|broadband services|
            voice over internet|voice over ip|internet telephony|
            third generation|mobile operator|
            telecom equipment|telecom industry|
            telephone network|phone network|
            electronic mail|email message|
            identity theft|online fraud|internet fraud|
            denial of service|denial service|
            security hole|security holes|security flaw|security flaws|
            security patch|security patches|
            malicious code|malicious software|
            anti virus|anti spam|anti spyware|
            software piracy|internet piracy|
            patent infringement|software patent|
            intellectual property rights|
            technology company|tech company|technology companies|
            technology giant|software giant|internet giant|
            tech giant|chip giant|computer giant|
            internet users|web users|
            mars rover|mars rovers|red planet|
            space agency|space mission|space exploration|
            manned space|unmanned space|
            rocket launch|satellite launch|
            launch vehicle|launch pad|
            moon mission|lunar mission|
            distant planet|distant galaxy|outer space|
            solar wind|solar flare|
            global warming|climate change|
            greenhouse gas|greenhouse gases|
            carbon dioxide|ozone layer|
            renewable energy|solar energy|solar power|
            wind power|fuel cell|fuel cells|
            hydrogen fuel|nuclear fusion|
            fossil record|dinosaur fossil|
            dna evidence|dna test|dna testing|
            genetic code|genetic mutation|
            food and drug administration|
            drug trial|drug trials|new drug|new drugs|
            experimental drug|experimental treatment|
            cancer drug|cancer treatment|breast cancer|
            lung cancer|prostate cancer|
            flu vaccine|aids vaccine|hiv vaccine|
            bird flu vaccine|
            flu vaccination|vaccine shortage|
            heart disease|heart attack risk|
            hormone therapy|fertility treatment|
            transplant surgery|organ transplant|
            mad cow disease|bovine spongiform|
            human embryos|human embryo|
            avian influenza virus|
            public library of science|
            new scientist|nature journal|science journal|
            journal nature|journal science|
            research team|scientists say|scientists have|
            researchers say|researchers have|
            study finds|study found|study shows|study suggests|
            new study|new research|
            ancient fossil|ancient fossils|
            carbon dating|archaeological dig|
            speed of light|particle accelerator|
            large hadron collider|higgs boson|
            quantum computer|quantum computing|
            virtual reality|augmented reality|
            3d printing|three dimensional printing
        """),
        (3.0, """
            online service|online services|online store|online retailer|
            online auction|online auctions|
            consumer electronics|electronics maker|
            research and development|
            information security|network security|
            computer users|pc users|
            software update|software upgrade|
            web based|internet based|
            digital divide|digital rights|
            mobile device|mobile devices|
            patent office|patent suit|
            anti trust|
            internet access|broadband access|
            medical journal|health study|
            the lancet|new england journal of medicine|
            world health organization|
            human brain|brain cells|
            life expectancy|blood pressure|
            birth control|weight loss|
            antarctic ice|arctic ice|polar ice|
            endangered species|new species|
            national science foundation|
            national institutes of health|
            science fiction|
            popular science|
            pc world|pc magazine|cnet news|cnet news com|
            computer weekly|computerworld|infoworld|slashdot|
            space com|scientific american
        """),
    ],
    "sports": [
        (9.0, """
            world cup|world series|super bowl|
            olympic games|olympic gold|olympic champion|
            olympic medal|olympic medals|
            grand slam|grand prix|
            us open|u s open|french open|australian open|
            british open|pga tour|lpga tour|ryder cup|presidents cup|
            davis cup|fed cup|
            premier league|premiership|champions league|
            uefa cup|fa cup|carling cup|la liga|serie a|bundesliga|
            national football league|national basketball association|
            national hockey league|major league baseball|
            major league soccer|college football|college basketball|
            test cricket|test match|one day international|
            formula one|formula 1|indy 500|
            tour de france|tour of spain|
            stanley cup|heisman trophy|
            little league|march madness
        """),
        (6.0, """
            gold medal|silver medal|bronze medal|
            gold medallist|gold medalist|
            gold medals|silver medals|bronze medals|
            world champion|world champions|world championship|
            world championships|defending champion|defending champions|
            national champion|league champion|
            championship game|championship final|championship title|
            title race|title defence|title defense|
            semi final|semi finals|quarter final|quarter finals|
            final round|final four|final whistle|
            head coach|assistant coach|team manager|
            national team|home team|visiting team|
            home run|home runs|home plate|
            batting average|earned run average|
            starting pitcher|relief pitcher|
            designated hitter|free agent|free agents|
            free agency|salary cap|trade deadline|
            training camp|spring training|
            hat trick|clean sheet|extra time|
            penalty kick|penalty shootout|
            penalty shoot out|penalty shot|
            injury time|stoppage time|
            field goal|field goals|touchdown pass|
            end zone|running back|wide receiver|tight end|
            first down|fourth quarter comeback|
            three pointer|three pointers|free throw|free throws|
            triple double|double double|
            straight sets|straight set|tie break|tiebreak|
            match point|break point|service game|
            first serve|second serve|
            pole position|pit stop|motor racing|auto racing|
            horse racing|horse race|thoroughbred racing|
            kentucky derby|breeders cup|
            track and field|track meet|
            men s singles|women s singles|
            men s doubles|women s doubles|
            mixed doubles|
            world record|personal best|
            batting lineup|opening batsman|
            test series|cricket board|
            first innings|second innings|
            wicket win|wicket victory|
            rugby union|rugby league|six nations|
            new zealand rugby|all blacks|
            six nations championship|
            professional football|professional basketball|
            american football|australian rules|
            national collegiate|southeastern conference
        """),
        (3.0, """
            season opener|season opening|regular season|new season|
            last season|next season|this season|
            first half|second half|half time|
            fourth inning|ninth inning|
            two goals|three goals|scored twice|scored once|
            scored a|scored the|scored his|
            goals against|goal difference|
            winning streak|losing streak|unbeaten run|
            home win|away win|home defeat|
            home victory|away victory|
            victory over|win over|triumph over|
            win against|defeat against|
            season high|career high|career best|
            defending title|defend his title|defend her title|
            league leaders|league lead|
            playoff berth|playoff spot|
            injury list|disabled list|
            knee injury|ankle injury|hamstring injury|
            achilles tendon|torn ligament|
            doping test|drug test|drug testing|
            performance enhancing|banned substance|
            sports car|sports cars|
            team usa|team gb|
            top seed|second seed|third seed|fourth seed|
            seeded player|opening round|
            third round|fourth round|
            round robin|knockout stage|
            athletics federation|football association|
            football federation|basketball federation|
            international olympic committee|
            national olympic committee|
            sports illustrated|espn com|
            associated press sports
        """),
    ],
    "world": [
        (9.0, """
            united nations|security council|
            white house|state department|
            prime minister|foreign minister|defense minister|defence minister|
            presidential election|general election|presidential campaign|
            presidential race|presidential candidate|
            election campaign|election results|
            suicide bomber|suicide bombing|car bomb|car bombing|
            roadside bomb|roadside bombing|
            al qaeda|al qaida|
            nuclear weapons|weapons of mass destruction|
            weapons inspector|weapons inspectors|
            peace talks|peace deal|peace agreement|
            cease fire|cease fire agreement|
            war crimes|war crime|
            human rights|
            civil war|civil unrest|
            gaza strip|west bank|
            north korea|north korean|
            european union|
            middle east|middle eastern|
            military operation|military offensive|
            rebel group|rebel groups|
            death toll|death sentence|
            terror attack|terror attacks|
            terrorist attack|terrorist attacks|
            hurricane ivan|hurricane frances|hurricane charley|
            hurricane jeanne|hurricane katrina
        """),
        (6.0, """
            us troops|american troops|british troops|iraqi troops|
            israeli troops|israeli army|iraqi army|
            us military|american military|
            us forces|american forces|coalition forces|
            armed forces|armed group|armed men|
            us led|american led|
            military base|army base|
            military strike|air strike|air strikes|airstrike|
            missile strike|missile attack|
            insurgent attack|insurgent attacks|
            rebel attack|rebel attacks|
            militant group|militant groups|
            islamic militants|islamic militant|
            shiite muslim|shiite muslims|sunni muslim|
            anti war|war on terror|war on terrorism|
            war in iraq|iraq war|
            occupied territories|occupied territory|
            palestinian leader|palestinian president|
            peace process|peace plan|peace envoy|
            peace deal|truce agreement|
            nuclear program|nuclear programme|
            nuclear threat|nuclear test|
            foreign policy|foreign affairs|
            home secretary|interior minister|
            deputy prime minister|vice president|
            head of state|heads of state|
            secretary of state|secretary general|
            national security|homeland security|
            political party|political parties|opposition party|
            opposition leader|opposition candidate|
            ruling party|ruling coalition|
            democratic party|republican party|
            labor party|labour party|conservative party|
            democratic convention|republican convention|
            party convention|national convention|
            electoral college|electoral commission|
            swing state|swing states|
            opinion poll|opinion polls|exit poll|exit polls|
            voting station|polling station|polling stations|
            presidential debate|presidential debates|
            election day|election victory|
            running mate|reelection campaign|
            peace accord|peace accords|
            diplomatic relations|diplomatic row|
            human trafficking|drug trafficking|
            drug smuggling|drug cartel|
            organized crime|organised crime|
            serial killer|murder trial|rape trial|
            criminal trial|criminal charges|criminal investigation|
            pleaded guilty|pleads guilty|not guilty|
            found guilty|life sentence|life in prison|
            death penalty|capital punishment|
            supreme court|high court|appeals court|
            arrest warrant|arrest warrants|
            law enforcement|police officer|police officers|
            police chief|police station|
            riot police|security forces|
            plane crash|air crash|helicopter crash|train crash|
            bus crash|ferry disaster|
            natural disaster|natural disasters|
            tropical storm|tropical depression|
            flash flood|flash floods|
            forest fire|forest fires|
            rescue workers|rescue operation|
            emergency services|state of emergency|
            torrential rain|heavy rains|heavy rain|
            relief effort|relief efforts|relief workers|
            bird flu outbreak|flu outbreak|
            avian flu outbreak|sars outbreak|
            refugee camp|refugee camps|
            international atomic energy agency|
            roman catholic|catholic church|
            pope john paul|dalai lama|
            gay marriage|same sex marriage|
            civil rights|civil liberties|
            immigration policy|border control|
            middle eastern|sri lankan rebels|
            tamil tigers|
            red cross|red crescent
        """),
        (3.0, """
            north atlantic treaty|african union|
            south africa|south african|
            south korea|south korean|
            saudi arabia|saudi arabian|
            united arab emirates|
            latin america|latin american|
            central america|central american|
            central asia|central asian|
            southeast asia|southeast asian|
            east timor|east timorese|
            ivory coast|sierra leone|
            democratic republic of congo|
            sri lanka|new delhi|
            the kremlin|downing street|
            buckingham palace|
            british government|french government|
            chinese government|russian government|
            us government|federal government|
            national assembly|house of representatives|
            house of commons|house of lords|
            congressional committee|
            international community|
            public opinion|
            relief aid|food aid|humanitarian aid|
            missing persons|missing person|
            human remains|
            hurricane warning|storm warning|
            powerful earthquake|strong earthquake|
            national guard|
            anti government|anti american|
            diplomatic mission|
            foreign ministers|
            face charges|faces charges|
            charged with|arrested for|arrested on|
            convicted of|accused of|sentenced to|
            suspected of|
            shot dead|gunned down|opened fire|
            killed in|killed by|killing of|
            people died|people dead|people killed|
            injured in|wounded in|
            death of|
            two state solution|
            church leader|religious leader|
            school siege|hostage crisis|
            united states president|
            health officials|public health|
            bird flu|avian flu
        """),
    ],
}

_TECH_ENTITIES = [
    (10.0, """
        microsoft|google|apple computer|apple inc|ibm|
        international business machines|intel|advanced micro devices|
        hewlett packard|hewlett packard enterprise|
        sun microsystems|cisco systems|cisco|
        oracle|dell|dell computer|dell computers|
        nvidia|qualcomm|broadcom|
        motorola|nokia|ericsson|sony ericsson|
        samsung|samsung electronics|
        research in motion|blackberry|
        yahoo|yahoo inc|amazon com|amazon|
        ebay|e bay|paypal|
        america online|aol|
        nintendo|sony computer entertainment|
        sony playstation|microsoft xbox|
        symantec|mcafee|kaspersky|
        red hat|novell|adobe|macromedia|
        salesforce|vmware|
        facebook|meta platforms|twitter|tiktok|
        openai|anthropic|chatgpt
    """),
    (7.5, """
        apple|amd|hp|compaq|emc|
        xerox|seagate|western digital|
        sandisk|toshiba|fujitsu|nec|
        hitachi|matsushita|panasonic|
        lenovo|acer|asus|asustek|
        taiwan semiconductor|tsmc|
        texas instruments|national semiconductor|
        infineon|stmicroelectronics|micron technology|
        arm holdings|arm ltd|
        applied materials|kla tencor|
        alcatel|lucent|alcatel lucent|nortel|
        ciena|juniper networks|juniper|
        veritas software|borland|sybase|
        bea systems|peoplesoft|people soft|sap|
        siebel|intuit|autodesk|
        realnetworks|real networks|realplayer|
        roxio|napster|kazaa|grokster|morpheus|
        skype|vonage|
        lycos|ask jeeves|altavista|infoseek|
        overture|doubleclick|akamai|
        earthlink|netzero|united online|
        verisign|verisign inc|
        checkpointsystems|check point|computer associates|
        trend micro|sophos|
        electronic arts|activision|blizzard|ubisoft|
        thq|take two interactive|take two|
        square enix|konami|capcom|sega|atari|
        eidos|acclaim entertainment|
        valve software|valve corp|id software|
        mozilla|firefox|opera software|
        netscape|netscape communications|
        bitdefender|panda software|
        priceline|expedia|travelocity|orbitz|
        netflix|spotify|
        alibaba|baidu|tencent|
        huawei|zte|xiaomi|
        nokia siemens|
        sony|philips|sharp electronics|canon|
        olympus|nikon|kodak|
        palmone|palm one|palm source|palmsource|
        handspring|palm inc|palm os|
        rim blackberry|
        at and t|at and t wireless|cingular|
        verizon|sprint|nextel|sprint nextel|
        t mobile|tmobile|vodafone|
        deutsche telekom|france telecom|telecom italia|
        telefonica|telefonos de mexico|telmex|
        british telecom|bt group|
        ntt|ntt docomo|ntt do co mo|kddi|
        china mobile|china telecom|china unicom|
        singtel|singapore telecommunications|
        telstra|optus|telia|telenor|
        sk telecom|kt corp|
        bell canada|bce|bellsouth|bell south|
        qwest|sbc communications|sbc|
        alltel|us cellular|virgin mobile|
        comcast|cablevision|cox communications|
        broadwing|global crossing|level 3 communications|
        microsoft windows|windows xp|windows vista|windows 7|
        windows 10|windows 11|windows server|
        microsoft office|office 365|microsoft word|microsoft excel|
        microsoft outlook|microsoft teams|
        mac os|os x|macbook|imac|powerbook|powermac|
        ipod|iphone|ipad|itunes|
        pentium|celeron|itanium|xeon|athlon|opteron|sempron|
        centrino|powerpc|power processor|
        playstation|playstation 2|ps2|ps3|ps4|ps5|
        xbox|xbox 360|gamecube|game boy|gameboy|
        nintendo ds|nintendo switch|n gage|
        world of warcraft|warcraft|half life|doom 3|halo 2|
        grand theft auto|the sims|sims 2|
        everquest|final fantasy|counter strike|
        ubuntu|debian|fedora|suse|openoffice|
        bittorrent|bittorrent inc|
        winzip|winamp|quicktime|acrobat|
        aapl|msft|goog|googl|intc|
        bill gates|steve ballmer|steve jobs|tim cook|
        larry ellison|larry page|sergey brin|eric schmidt|
        michael dell|carly fiorina|meg whitman|jeff bezos|
        steve wozniak|linus torvalds|
        marc andreessen|mark zuckerberg|
        world wide web consortium|w3c|
        internet corporation for assigned names|icann|
        federal communications commission|fcc|
        european space agency|japan aerospace exploration agency|
        jet propulsion laboratory|jpl|
        spacex|blue origin|virgin galactic|
        nasa|hubble|cassini|huygens|
        bert rutan|scaled composites|spaceshipone|spaceship one|
        ansari x prize|x prize|
        spirit rover|opportunity rover|
        deep impact spacecraft|
        beagle 2|genesis probe|
        european southern observatory|
        los alamos national laboratory|
        lawrence livermore|
        massachusetts institute of technology|caltech|
        human genome project
    """),
]

_BUSINESS_ENTITIES = [
    (7.0, """
        general motors|daimlerchrysler|daimler chrysler|
        ford motor|toyota motor|honda motor|
        nissan motor|hyundai motor|
        volkswagen|bmw|
        wal mart|walmart|walgreen|walgreens|
        home depot|lowe s|lowes|
        mcdonald s|mcdonalds|burger king|
        coca cola|pepsico|pepsi|
        procter and gamble|procter gamble|unilever|
        general electric|general mills|
        berkshire hathaway|
        citigroup|citibank|bank of america|
        jp morgan|jpmorgan|j p morgan|
        morgan stanley|goldman sachs|
        merrill lynch|lehman brothers|
        credit suisse|deutsche bank|ubs|
        hsbc|barclays|royal bank of scotland|
        wells fargo|wachovia|bank one|
        american express|capital one|
        fannie mae|freddie mac|
        american international group|aig|
        metlife|prudential financial|
        countrywide financial|
        new york stock exchange|nasdaq stock market|
        chicago mercantile exchange|
        enron|arthur andersen|
        united airlines|us airways|american airlines|
        delta air lines|delta airlines|northwest airlines|
        continental airlines|southwest airlines|
        jetblue|air canada|british airways|
        air france|klm|lufthansa|alitalia|
        ryanair|easyjet|qantas|
        singapore airlines|cathay pacific|
        virgin atlantic|
        federal express|fedex|united parcel service|
        exxon|exxon mobil|exxonmobil|
        chevron|chevrontexaco|conocophillips|
        royal dutch shell|royal dutch|bp plc|
        halliburton|schlumberger|baker hughes|
        saudi aramco|aramco|
        bhp billiton|rio tinto|alcoa|
        arcelor mittal|arcelormittal|
        opec|
        boeing|airbus|eads|
        lockheed martin|northrop grumman|raytheon|
        caterpillar|deere|
        harley davidson|
        sears roebuck|kmart|sears|
        best buy|circuit city|costco|
        target corp|jc penney|j c penney|j c penny|
        marks and spencer|tesco|sainsbury|
        safeway|kroger|albertsons|ahold|
        starbucks|yukos|gazprom|
        fda approved earnings|
        martha stewart living|martha stewart|
        tyco|parmalat|adel phia|adelphia|
        altria|philip morris|
        ryder systems|union pacific|
        berkshire|warren buffett|alan greenspan|
        ben bernanke|janet yellen|
        international monetary fund|world bank|
        standard and poor s|moody s|fitch ratings
    """),
    (4.0, """
        ford|toyota|honda|nissan|hyundai|kia|
        fiat|peugeot|citroen|renault|volvo|
        porsche|daimler|chrysler|
        toyota motor corp|
        general electric co|
        gm|
        walt disney|disney|pixar|
        viacom|time warner|news corp|news corporation|
        universal studios|warner bros|
        dreamworks|metro goldwyn mayer|mgm|
        sony pictures|bertelsmann|
        clear channel|gannett|
        dow chemical|dupont|du pont|
        basf|bayer|
        merck|pfizer|glaxosmithkline|glaxo|
        astrazeneca|eli lilly|johnson and johnson|
        bristol myers squibb|wyeth|novartis|roche|
        sanofi|aventis|schering plough|
        amgen|genentech|biogen|
        anheuser busch|sabre holdings|
        colgate palmolive|kimberly clark|
        heinz|kraft foods|kellogg|nestle|
        hilton|marriott|intercontinental hotels|
        carnival corp|royal caribbean|
        nike|reebok|adidas|puma|
        gap inc|abercrombie|tommy hilfiger|
        liz claiborne|
        british petroleum|repsol|total sa|
        bnp paribas|societe generale|
        abn amro|ing group|fortis|
        santander|bbva|
        bank of china|icbc|
        sumitomo mitsui|mitsubishi tokyo|
        mufg|mizuho|
        sovereign debt|
        rupert murdoch|michael eisner|
        richard branson|donald trump|
        richard grasso|dick grasso|
        john snow|henry paulson|
        carlyle group|blackstone|kohlberg kravis roberts|
        kkr|cerberus|
        lazard|bear stearns|
        berkshire hathaway inc
    """),
]

_SPORTS_ENTITIES = [
    (8.0, """
        tiger woods|phil mickelson|vijay singh|ernie els|
        retief goosen|sergio garcia|davis love|davis love iii|
        mike weir|david duval|colin montgomerie|darren clarke|
        nick faldo|jack nicklaus|arnold palmer|
        annika sorenstam|michelle wie|grace park|
        se ri pak|lorena ochoa|
        roger federer|andy roddick|andre agassi|
        lleyton hewitt|tim henman|marat safin|
        david nalbandian|guillermo coria|carlos moya|
        juan carlos ferrero|juan martin del potro|
        rafael nadal|novak djokovic|andy murray|
        pete sampras|john mcenroe|boris becker|
        serena williams|venus williams|
        maria sharapova|lindsay davenport|jennifer capriati|
        amelie mauresmo|justine henin|kim clijsters|
        elena dementieva|svetlana kuznetsova|
        anastasia myskina|martina hingis|martina navratilova|
        michael schumacher|ralf schumacher|rubens barrichello|
        kimi raikkonen|fernando alonso|jenson button|
        david coulthard|juan pablo montoya|jacques villeneuve|
        lewis hamilton|max verstappen|
        dale earnhardt|dale earnhardt jr|
        jeff gordon|jimmie johnson|tony stewart|
        kurt busch|kyle busch|matt kenseth|
        mark martin|dale jarrett|richard petty|
        lance armstrong|jan ullrich|ivan basso|
        tyler hamilton|floyd landis|
        michael phelps|ian thorpe|pieter van den hoogenband|
        grant hackett|amanda beard|natalie coughlin|
        kosuke kitajima|jenny thompson|
        marion jones|tim montgomery|justin gatlin|
        maurice greene|asafa powell|usain bolt|
        justin gatlin|carl lewis|ben johnson|
        kelly holmes|paula radcliffe|
        hicham el guerrouj|haile gebrselassie|
        kenenisa bekele|elvan abeylegesse|
        liu xiang|yuriy borzakovskiy|
        jeremy wariner|shawn crawford|
        yao ming|yao|
        michael jordan|lebron james|kobe bryant|
        shaquille o neal|shaquille oneal|
        shaquille|sha q|
        tracy mcgrady|allen iverson|kevin garnett|
        tim duncan|dirk nowitzki|steve nash|
        jason kidd|vince carter|paul pierce|
        carmelo anthony|dwyane wade|
        amare stoudemire|pau gasol|manu ginobili|
        reggie miller|karl malone|john stockton|
        magic johnson|larry bird|
        phil jackson|larry brown|gregg popovich|
        pat riley|jeff van gundy|
        barry bonds|sammy sosa|mark mcgwire|
        alex rodriguez|derek jeter|babe ruth|
        albert pujols|manny ramirez|david ortiz|
        gary sheffield|jason giambi|
        ichiro suzuki|hideki matsui|
        pedro martinez|roger clemens|randy johnson|
        curt schilling|greg maddux|tom glavine|
        johan santana|mariano rivera|
        mike piazza|ivan rodriguez|carlos beltran|
        scott rolen|andruw jones|
        bobby cox|joe torre|tony la russa|
        peyton manning|eli manning|brett favre|
        tom brady|donovan mcnabb|michael vick|
        ben roethlisberger|drew brees|dante culpepper|
        daunte culpepper|chad pennington|
        steve mcnair|kurt warner|trent green|
        terrell owens|randy moss|jerry rice|
        ray lewis|brian urlacher|warren sapp|
        priest holmes|ladainian tomlinson|curtis martin|
        clinton portis|tiki barber|jamal lewis|
        emmitt smith|walter payton|
        bill belichick|andy reid|bill parcells|
        joe gibbs|mike shanahan|
        sachin tendulkar|rahul dravid|sourav ganguly|
        virender sehwag|anil kumble|vvs laxman|
        mahendra singh dhoni|ms dhoni|virat kohli|
        ricky ponting|adam gilchrist|matthew hayden|
        justin langer|damien martyn|michael clarke|
        shane warne|glenn mcgrath|brett lee|
        brian lara|shivnarine chanderpaul|chris gayle|
        andrew flintoff|michael vaughan|
        marcus trescothick|steve harmison|andrew strauss|
        kevin pietersen|graham thorpe|
        shoaib akhtar|inzamam ul haq|yousuf youhana|
        shahid afridi|waqar younis|wasim akram|
        muthiah muralitharan|muttiah muralitharan|
        chaminda vaas|sanath jayasuriya|marvan atapattu|
        kumar sangakkara|mahela jayawardene|
        stephen fleming|daniel vettori|
        graeme smith|jacques kallis|shaun pollock|
        herschelle gibbs|michael ntini|makhaya ntini|
        david beckham|wayne rooney|michael owen|
        cristiano ronaldo|lionel messi|
        ronaldo|ronaldinho|rivaldo|kaka|
        zinedine zidane|zidane|
        thierry henry|patrick vieira|robert pires|
        dennis bergkamp|ruud van nistelrooy|
        arjen robben|robin van persie|
        didier drogba|frank lampard|john terry|
        steven gerrard|jamie carragher|
        fernando torres|xabi alonso|
        raul gonzalez|luis figo|roberto carlos|
        david trezeguet|alessandro del piero|
        francesco totti|andriy shevchenko|
        alessandro nesta|paolo maldini|gianluigi buffon|
        oliver kahn|michael ballack|
        alex ferguson|arsene wenger|jose mourinho|
        rafael benitez|sven goran eriksson|kevin keegan|
        bobby robson|brian clough|
        martin johnson|jonny wilkinson|jason robinson|
        clive woodward|brian o driscoll|
        doug howlett|dan carter|richie mccaw|
        george gregan|stephen larkham|
        wayne gretzky|mario lemieux|mark messier|
        steve yzerman|brett hull|jeremy roenick|
        jaromir jagr|joe sakic|peter forsberg|
        martin brodeur|patrick roy|dominik hasek|
        sidney crosby|alex ovechkin|
        bob goodenow|gary bettman|
        mike tyson|lennox lewis|vitali klitschko|
        wladimir klitschko|bernard hopkins|
        oscar de la hoya|roy jones jr|
        floyd mayweather|manny pacquiao|
        felix trinidad|shane mosley|
        amir khan|joe calzaghe|ricky hatton
    """),
    (7.0, """
        new york yankees|boston red sox|red sox|chicago white sox|white sox|
        new york mets|chicago cubs|st louis cardinals|
        atlanta braves|los angeles dodgers|san francisco giants|
        oakland athletics|anaheim angels|los angeles angels|
        minnesota twins|cleveland indians|cleveland guardians|
        detroit tigers|kansas city royals|toronto blue jays|blue jays|
        baltimore orioles|tampa bay devil rays|devil rays|
        tampa bay rays|texas rangers|
        seattle mariners|colorado rockies|arizona diamondbacks|
        san diego padres|philadelphia phillies|pittsburgh pirates|
        milwaukee brewers|houston astros|cincinnati reds|
        florida marlins|miami marlins|montreal expos|washington nationals|
        new england patriots|new york jets|new york giants|
        buffalo bills|miami dolphins|pittsburgh steelers|
        baltimore ravens|cincinnati bengals|cleveland browns|
        indianapolis colts|tennessee titans|houston texans|
        jacksonville jaguars|denver broncos|san diego chargers|
        los angeles chargers|kansas city chiefs|oakland raiders|
        las vegas raiders|dallas cowboys|washington redskins|
        washington commanders|philadelphia eagles|
        green bay packers|chicago bears|minnesota vikings|
        detroit lions|atlanta falcons|new orleans saints|
        carolina panthers|tampa bay buccaneers|
        seattle seahawks|st louis rams|los angeles rams|
        arizona cardinals|san francisco 49ers|
        los angeles lakers|los angeles clippers|
        sacramento kings|golden state warriors|
        phoenix suns|portland trail blazers|seattle supersonics|
        utah jazz|denver nuggets|minnesota timberwolves|
        dallas mavericks|san antonio spurs|houston rockets|
        memphis grizzlies|new orleans hornets|charlotte bobcats|
        charlotte hornets|miami heat|orlando magic|atlanta hawks|
        washington wizards|boston celtics|new york knicks|
        new jersey nets|brooklyn nets|philadelphia 76ers|
        toronto raptors|chicago bulls|detroit pistons|
        cleveland cavaliers|indiana pacers|milwaukee bucks|
        oklahoma city thunder|
        detroit red wings|red wings|toronto maple leafs|maple leafs|
        montreal canadiens|boston bruins|new york rangers|
        new york islanders|new jersey devils|
        ottawa senators|philadelphia flyers|pittsburgh penguins|
        tampa bay lightning|florida panthers|carolina hurricanes|
        washington capitals|atlanta thrashers|
        chicago blackhawks|st louis blues|nashville predators|
        columbus blue jackets|minnesota wild|colorado avalanche|
        vancouver canucks|calgary flames|edmonton oilers|
        los angeles kings|san jose sharks|anaheim ducks|
        mighty ducks|phoenix coyotes|dallas stars|
        manchester united|manchester city|newcastle united|
        west ham|west ham united|tottenham hotspur|tottenham|
        aston villa|birmingham city|blackburn rovers|
        bolton wanderers|west bromwich|west brom|
        crystal palace|portsmouth fc|southampton fc|
        charlton athletic|middlesbrough|fulham|
        leeds united|nottingham forest|
        real madrid|atletico madrid|fc barcelona|barcelona|
        deportivo la coruna|valencia cf|real betis|
        bayern munich|borussia dortmund|bayer leverkusen|
        ac milan|inter milan|internazionale|juventus|
        as roma|lazio|
        paris st germain|paris saint germain|
        olympique lyon|olympique marseille|as monaco|
        celtic fc|glasgow celtic|glasgow rangers|
        rangers fc|feyenoord|psv eindhoven|ajax amsterdam|
        fc porto|sporting lisbon|benfica|
        dinamo kiev|dynamo kiev|cska moscow|
        real salt lake|dc united|la galaxy|los angeles galaxy|
        new york red bulls|chicago fire soccer|
        columbus crew|san jose earthquakes|
        all blacks|wallabies|springboks|
        notre dame|fighting irish|usc trojans|trojans|
        oklahoma sooners|sooners|texas longhorns|longhorns|
        florida gators|gators|ohio state buckeyes|buckeyes|
        michigan wolverines|penn state nittany lions|
        lsu tigers|alabama crimson tide|crimson tide|
        auburn tigers|tennessee volunteers|
        virginia tech hokies|hokies|
        florida state seminoles|seminoles|
        duke blue devils|blue devils|north carolina tar heels|tar heels|
        connecticut huskies|uconn|
        wimbledon|roland garros|flushing meadows|
        all england club|augusta national|
        st andrews golf|bethpage black|
        twickenham|lord s cricket|lords cricket|
        wankhede|eden gardens|the oval|
        old trafford|stamford bridge|anfield|highbury|
        santiago bernabeu|camp nou|nou camp|
        yankee stadium|fenway park|wrigley field|
        madison square garden|
        international cricket council|icc cricket|
        bcci|cricket australia|england and wales cricket board|
        international association of athletics federations|iaaf|
        fia|fifa|uefa|atp|wta|pga|lpga|
        ioc|usoc|
        mclaren|williams bmw|bar honda|
        minardi|sauber|jordan ford|
        red bull racing|scuderia ferrari|
        team discovery channel|us postal cycling|
        west indies
    """),
    (5.0, """
        federer|roddick|agassi|hewitt|henman|safin|
        sampras|nadal|djokovic|mauresmo|sharapova|
        davenport|capriati|clijsters|henin|dementieva|
        kuznetsova|myskina|navratilova|hingis|
        schumacher|barrichello|raikkonen|coulthard|montoya|
        alonso|villeneuve|verstappen|
        earnhardt|kenseth|
        mickelson|sorenstam|montgomerie|goosen|
        phelps|thorpe|
        tendulkar|dravid|ganguly|sehwag|kumble|
        gilchrist|ponting|warne|mcgrath|
        flintoff|harmison|trescothick|pietersen|
        muralitharan|muralidaran|sangakkara|jayawardene|
        jayasuriya|kallis|pollock|vettori|
        inzamam|afridi|
        beckham|rooney|ronaldinho|zidane|
        mourinho|wenger|shevchenko|drogba|
        gerrard|lampard|trezeguet|bergkamp|
        klinsmann|eriksson|capello|ancelotti|
        bryant|iverson|garnett|mcgrady|nowitzki|
        stoudemire|marbury|ginobili|
        roethlisberger|favre|mcnabb|pennington|
        tomlinson|
        jeter|clemens|schilling|maddux|piazza|pujols|
        sosa|ichiro|
        gretzky|lemieux|jagr|brodeur|forsberg|
        klitschko|mayweather|pacquiao|
        hopkins|tyson|
        seahawks|steelers|packers|patriots|
        yankees|lakers|celtics|knicks|pistons|
        dodgers|astros|phillies|orioles|mariners|
        padres|diamondbacks|buccaneers|
        cavaliers|mavericks|spurs|timberwolves|
        canadiens|canucks|oilers|bruins|
        blackhawks|penguins|
        juventus|arsenal|chelsea|liverpool|
        everton|newcastle|birmingham|
        celtic|fenerbahce|galatasaray|
        panathinaikos|olympiakos|olympiacos|
        shakhtar|anderlecht|
        tri nations|super 12|super 14|
        aintree|epsom|ascot|cheltenham|goodwood|
        belmont stakes|preakness stakes|melbourne cup|
        keeneland|churchill downs|saratoga race|
        daytona|talladega|indianapolis 500|
        monza|silverstone|nurburgring|hockenheim|
        suzuka|magny cours|interlagos|
        motogp|moto gp|world superbike|
        valentino rossi|max biaggi|sete gibernau|
        rally championship
    """),
]

_WORLD_ENTITIES = [
    (7.0, """
        george bush|george w bush|president bush|
        john kerry|senator kerry|
        dick cheney|richard cheney|
        john edwards|howard dean|
        barack obama|joe biden|kamala harris|
        hillary clinton|bill clinton|
        al gore|john mccain|
        donald rumsfeld|paul wolfowitz|
        condoleezza rice|colin powell|
        colin l powell|
        tony blair|gordon brown|gordon smith|
        michael howard|charles kennedy|
        jacques chirac|nicolas sarkozy|
        gerhard schroeder|angela merkel|
        vladimir putin|dmitry medvedev|
        boris yeltsin|mikhail gorbachev|
        silvio berlusconi|romano prodi|
        jose luis rodriguez zapatero|jose maria aznar|
        kofi annan|ban ki moon|antonio guterres|
        hans blix|mohamed elbaradei|
        saddam hussein|saddam|
        osama bin laden|bin laden|
        abu musab al zarqawi|al zarqawi|zarqawi|
        ayman al zawahri|al zawahri|zawahiri|
        ayad allawi|iyad allawi|
        ahmed chalabi|ahmad chalabi|
        ali al sistani|ayatollah sistani|al sistani|
        moqtada al sadr|muqtada al sadr|al sadr|
        hamid karzai|pervez musharraf|
        benazir bhutto|asif ali zardari|
        nawaz sharif|
        yasser arafat|yasir arafat|arafat|
        mahmoud abbas|mahmud abbas|
        ariel sharon|benjamin netanyahu|
        shimon peres|ehud olmert|ehud barak|
        ahmed yassin|abdel aziz rantisi|
        mahmoud ahmadinejad|mohammad khatami|
        ali khamenei|ayatollah khamenei|
        bashar assad|bashar al assad|
        rafik hariri|emile lahoud|
        hosni mubarak|muammar gaddafi|moammar gadhafi|
        omar al bashir|
        robert mugabe|thabo mbeki|nelson mandela|
        morgan tsvangirai|
        hugo chavez|fidel castro|raul castro|
        luis inacio lula|luiz inacio lula|lula da silva|
        nestor kirchner|alvaro uribe|
        vicente fox|ricardo lagos|
        junichiro koizumi|shinzo abe|
        hu jintao|jiang zemin|wen jiabao|xi jinping|
        kim jong il|kim jong un|
        roh moo hyun|lee myung bak|
        chen shui bian|lien chan|
        manmohan singh|atal bihari vajpayee|
        sonia gandhi|rahul gandhi|narendra modi|
        susilo bambang yudhoyono|megawati sukarnoputri|
        gloria macapagal arroyo|gloria arroyo|
        thaksin shinawatra|mahatir mohamad|mahathir mohamad|
        mahinda rajapaksa|chandrika kumaratunga|
        ranil wickremesinghe|velupillai prabhakaran|
        king gyanendra|
        john howard|kevin rudd|helen clark|
        paul martin|jean chretien|stephen harper|
        bertie ahern|ian paisley|gerry adams|
        john hume|david trimble|
        viktor yushchenko|viktor yanukovich|viktor yanukovych|
        yulia tymoshenko|leonid kuchma|
        alexander lukashenko|
        mikheil saakashvili|eduard shevardnadze|
        aslan maskhadov|shamil basayev|
        ahmad kadyrov|ramzan kadyrov|
        slobodan milosevic|radovan karadzic|
        ratko mladic|
        pope john paul|pope benedict|pope francis|
        dalai lama|mother teresa|
        queen elizabeth|prince charles|king charles|
        prince william|prince harry|
        scott peterson|laci peterson|
        oscar pistorius trial|
        beslan|abu ghraib|guantanamo bay|
        guantanamo|abu sayyaf|
        jemaah islamiyah|jemaah islamiah|
        boko haram|islamic state|
        hezbollah|hizbollah|hamas|fatah|
        fatah movement|palestinian authority|
        palestine liberation organization|
        fatah al islam|islamic jihad|
        ira|irish republican army|
        eta separatists|basque separatists|
        farc|shining path|
        national league for democracy|
        aung san suu kyi|
        g7 summit|g8 summit|g20 summit|
        international criminal court|
        international court of justice|
        osce|unhcr|unicef|unrwa|iaea|
        nato|un security council|
        human rights watch|amnesty international|
        doctors without borders|medecins sans frontieres|
        oxfam|
        hurricane ivan|hurricane frances|hurricane charley|
        hurricane jeanne|hurricane katrina|
        indian ocean tsunami|
        orange revolution|rose revolution|
        tiananmen square|tiananmen|
        tiananmen massacre|
        9 11 attacks|september 11 attacks|sept 11 attacks|
        september 11 commission|9 11 commission
    """),
    (4.0, """
        bush|kerry|cheney|blair|chirac|schroeder|
        putin|merkel|berlusconi|koizumi|
        musharraf|karzai|mubarak|gaddafi|gadhafi|
        khatami|ahmadinejad|
        castro|chavez|mugabe|mbeki|
        allawi|chalabi|sistani|
        sharon|netanyahu|arafat|abbas|
        rumsfeld|wolfowitz|condoleezza|
        annan|elbaradei|milosevic|
        yushchenko|yanukovych|yanukovich|
        tymoshenko|kuchma|
        yudhoyono|megawati|arroyo|thaksin|
        vajpayee|
        zapatero|
        obama|biden|trump|
        clinton|ratzinger|
        belmarsh|
        downing street|
        kremlin|
        duma|knesset|bundestag|
        republican national committee|
        democratic national committee|
        salvation army relief|
        stormont|holy see|
        toba eruption|mount st helens eruption
    """),
]


def _make_words():
    result = {}
    for label, groups in _WORD_GROUPS.items():
        for weight, words in groups:
            for word in words.split():
                key = _normalize(word)
                if not key or " " in key:
                    continue
                entry = result.setdefault(key, {})
                entry[label] = max(weight, entry.get(label, 0.0))
    return result


def _make_phrases(groups):
    result = {}
    for weight, text in groups:
        for phrase in text.split("|"):
            phrase = _normalize(phrase.strip())
            if phrase:
                result[phrase] = max(weight, result.get(phrase, 0.0))
    return tuple(result.items())


_WORDS = _make_words()
_PHRASES = {
    label: _make_phrases(groups)
    for label, groups in _PHRASE_GROUPS.items()
}
_TECH = _make_phrases(_TECH_ENTITIES)
_BUSINESS = _make_phrases(_BUSINESS_ENTITIES)
_SPORTS = _make_phrases(_SPORTS_ENTITIES)
_WORLD = _make_phrases(_WORLD_ENTITIES)

_MARKET_FRAME = re.compile(
    r"\b(?:stock markets?|share markets?|equity markets?|"
    r"wall street|dow jones|nikkei|ftse|hang seng|"
    r"s and p 500|nasdaq composite|"
    r"(?:us|u s|american|asian|european|global|world|"
    r"japanese|tokyo|london|chinese|technology|tech) stocks|"
    r"stocks (?:rise|rises|rose|fall|falls|fell|gain|gains|"
    r"rally|rallied|rallies|drop|drops|jump|climb|slip|slide|"
    r"edge|end|close|open|higher|lower|mixed|up|down)|"
    r"nasdaq (?:falls|fell|rises|rose|ends|opens|closes|"
    r"gains|drops|slips|up|down|hits|higher|lower)|"
    r"world markets|asian markets|european markets)\b"
)

_FINANCE_WORDS = re.compile(
    r"\b(?:earnings|profits?|revenues?|sales|shares?|"
    r"stocks?|quarterly|dividends?|forecasts?|"
    r"buyout|takeover|merger|acquisition|layoffs?|"
    r"bankruptcy|antitrust|lawsuit|sued)\b"
)

_AIR_DISASTER = re.compile(
    r"\b(?:plane crash|air crash|airliner crash|aircraft crash|"
    r"jet crash|flight crash|airline crash|"
    r"plane crashes|airliner crashes|helicopter crash|"
    r"plane plunged|plane went down|"
    r"airliner went down|air disaster)\b"
)

_CYBER = re.compile(
    r"\b(?:malware|spyware|ransomware|phishing|"
    r"computer virus|internet worm|computer worm|"
    r"cyber attack|cyberattack|cybercrime|cyber security|"
    r"computer hacker|hackers|data breach|"
    r"denial of service|spam email|spam emails|"
    r"software piracy|internet piracy)\b"
)

_RESEARCH = re.compile(
    r"\b(?:scientists?|researchers?|astronomers?|"
    r"physicists?|biologists?|archaeologists?|"
    r"paleontologists?|geneticists?|"
    r"study (?:finds|shows|suggests|reveals|links)|"
    r"new study|new research|clinical trials?|"
    r"experimental (?:drug|treatment|vaccine)|"
    r"stem cells?|gene therapy)\b"
)

_POLITICAL = re.compile(
    r"\b(?:presidential|election|elections|prime minister|"
    r"foreign minister|white house|republican|democrat|"
    r"democratic party|parliament|senate|congress|"
    r"political|government|ballot|voters?)\b"
)

_SPORT_RESULT = re.compile(
    r"\b(?:beat|beats|defeated|defeats|upset|routed|"
    r"thrashed|ousted|outplayed|outlasted|edged|"
    r"blanked|crushed|trounced|drew|draw|tie|won|lost)\b"
)

_RULES = [
    ("sports", 5.0, r"\b(?:won|win|wins|lost|lose|loses) by (?:a |an )?\d+\b"),
    ("sports", 5.0, r"\b(?:\d+ wicket|\d+ wickets|\d+ run victory|\d+ run win)\b"),
    ("sports", 4.0, r"\b(?:\d+ yard|\d+ yards|\d+ under par|\d+ shot lead)\b"),
    ("sports", 5.0, r"\b(?:knocked out|booked (?:his|her|their|a) (?:place|spot))\b"),
    ("sports", 4.0, r"\b(?:reach|reaches|reached|into|in) (?:the )?(?:finals|semifinals|quarterfinals)\b"),
    ("sports", 4.0, r"\b(?:premier league|first division|second division|championship) (?:title|leaders|club|side)\b"),
    ("sports", 3.5, r"\b(?:scored|netted|fired|struck) (?:a |the )?(?:winner|equaliser|equalizer|opener|goals?|hat trick)\b"),
    ("sports", 4.0, r"\b(?:\d+ for \d+|\d+ not out)\b"),
    ("sports", 3.0, r"\b(?:world|olympic|national|european) (?:champions?|championships?|record)\b"),
    ("business", 4.0, r"\b(?:profit|earnings|revenue|sales) (?:beat|beats|miss|misses|missed|exceed|exceeds|exceeded)\b"),
    ("business", 4.0, r"\b(?:raised|raises|raise|cuts|cut|lowered|lowers) (?:its )?(?:earnings|profit|revenue|sales) (?:outlook|forecast)\b"),
    ("business", 4.0, r"\b(?:million|billion) (?:dollar )?(?:deal|merger|bid|takeover|acquisition)\b"),
    ("business", 4.0, r"\b(?:oil|crude|gold|copper|gasoline) (?:rose|rises|fell|falls|soars|surges|hits|hit|prices)\b"),
    ("business", 3.0, r"\b(?:factory|plant) (?:closure|closures|shutdown|workers)\b"),
    ("business", 3.0, r"\b(?:workers|pilots|employees|machinists) (?:strike|walkout|union|walk)\b"),
    ("business", 3.5, r"\b(?:to buy|buys|to acquire|acquires) (?:rival|competitor)\b"),
    ("business", 3.5, r"\b(?:stock|share) (?:split|offering|sale|float|buyback)\b"),
    ("sci_tech", 4.0, r"\b(?:launches|unveils|releases|introduces|debuts) (?:its |a |the |new )*(?:software|chip|processor|laptop|computer|phone|handset|browser|console|server)\b"),
    ("sci_tech", 4.0, r"\b(?:researchers|scientists) (?:have |has )?(?:found|find|discovered|discover|identified|developed|created|say|said|unveil|report)\b"),
    ("sci_tech", 4.0, r"\b(?:approved|approves|approval) (?:of |for )?(?:a |the |an |new )*(?:drug|vaccine|treatment)\b"),
    ("sci_tech", 4.0, r"\b(?:drug|vaccine|treatment) (?:approved|approval|trial|trials|research|study)\b"),
    ("sci_tech", 4.0, r"\b(?:planet|comet|asteroid|galaxy|star|spacecraft) (?:discovered|discovery|detected|found|orbit)\b"),
    ("sci_tech", 4.0, r"\b(?:nasa|esa) (?:probe|rover|mission|scientists|shuttle|spacecraft)\b"),
    ("world", 5.0, r"\b(?:bomb|blast|explosion|attack|raid) (?:has |had )?(?:kills|killed|wounds|wounded)\b"),
    ("world", 5.0, r"\b(?:kills|killed|wounds|wounded) (?:at least |more than |some )?\d+ (?:people|civilians|soldiers|policemen|police|children)\b"),
    ("world", 4.0, r"\b(?:rebels|militants|insurgents|gunmen) (?:have |had )?(?:killed|attacked|seized|kidnapped|released|freed)\b"),
    ("world", 4.0, r"\b(?:wins|won|lose|lost|win) (?:the |a |an )?(?:election|vote|referendum|presidency)\b"),
    ("world", 4.0, r"\b(?:accused|charged|convicted) (?:him |her |them )?(?:of|with) (?:murder|rape|terrorism|treason|espionage)\b"),
    ("world", 4.0, r"\b(?:hurricane|typhoon|tsunami|earthquake|floods?) (?:has |had )?(?:killed|kills|hits|hit|strikes|struck|leaves|left)\b"),
    ("world", 4.0, r"\b(?:troops|forces|army) (?:have |has )?(?:attacked|launched|killed|stormed|invaded|withdrawn|seized)\b"),
]
_RULES = tuple((label, weight, re.compile(pattern)) for label, weight, pattern in _RULES)


def _forms(word):
    found = {word}
    frontier = [word]
    for _ in range(2):
        new = []
        for term in frontier:
            candidates = []
            if len(term) > 4 and term.endswith("ies"):
                candidates.append(term[:-3] + "y")
            if len(term) > 4 and term.endswith("s") and not term.endswith(("ss", "us", "is")):
                candidates.append(term[:-1])
            if len(term) > 5 and term.endswith(("sses", "ches", "shes", "xes", "zes")):
                candidates.append(term[:-2])
            if len(term) > 5 and term.endswith("ed"):
                root = term[:-2]
                candidates.extend((root, root + "e"))
                if len(root) > 2 and root[-1] == root[-2]:
                    candidates.append(root[:-1])
            if len(term) > 6 and term.endswith("ing"):
                root = term[:-3]
                candidates.extend((root, root + "e"))
                if len(root) > 2 and root[-1] == root[-2]:
                    candidates.append(root[:-1])
            for candidate in candidates:
                if candidate not in found:
                    found.add(candidate)
                    new.append(candidate)
        frontier = new
    return found


def _position_weight(position, title_limit):
    if position < title_limit:
        return 1.55
    if position < max(230, title_limit + 95):
        return 1.12
    return 1.0


def _match_features(padded, features):
    matches = []
    for phrase, weight in features:
        needle = " " + phrase + " "
        position = padded.find(needle)
        if position >= 0:
            matches.append((phrase, weight, position))
    return matches


def _entity_score(matches, title_limit, multiplier=1.0):
    ordered = sorted(matches, key=lambda item: (-len(item[0]), -item[1]))
    retained = []
    for phrase, weight, position in ordered:
        covered = False
        end = position + len(phrase)
        for longer, longer_weight, longer_position in retained:
            if (
                longer_position <= position
                and longer_position + len(longer) >= end
                and longer_weight >= weight * 0.8
            ):
                covered = True
                break
        if not covered:
            retained.append((phrase, weight, position))
    total = 0.0
    focal = False
    for phrase, weight, position in retained:
        if position < title_limit + 25:
            factor = 1.5
            focal = True
        elif position < 235:
            factor = 1.0
        else:
            factor = 0.72
        total += weight * factor * multiplier
    return total, focal, retained


def _extract_text(state):
    if isinstance(state, str):
        return state
    if isinstance(state, dict):
        pieces = []
        for key in ("title", "headline", "text", "description", "content", "article", "body"):
            value = state.get(key)
            if isinstance(value, str) and value and value not in pieces:
                pieces.append(value)
        return "\n".join(pieces)
    if isinstance(state, (list, tuple)):
        return "\n".join(value for value in state if isinstance(value, str))
    return ""


def predict(state):
    original = _extract_text(state)
    if not original or not original.strip():
        return {"answer": "world"}

    # Exchange annotations are metadata, not an article's subject.
    cleaned = re.sub(
        r"\((?:NASDAQ|NYSE|AMEX|OTC(?:BB)?|LSE|TSX|ASX)"
        r"\s*(?::|/)\s*[^)]{0,90}\)",
        " ",
        original,
        flags=re.I,
    )
    text = _normalize(cleaned)
    if not text:
        return {"answer": "world"}
    padded = " " + text + " "

    first_line = cleaned.strip().split("\n")[0]
    normalized_line = _normalize(first_line)
    if "\n" in cleaned.strip() and 15 <= len(normalized_line) <= 200:
        title_limit = len(normalized_line)
    else:
        tokens = list(re.finditer(r"\S+", text))
        if len(tokens) > 15:
            title_limit = min(160, max(65, tokens[14].end()))
        else:
            title_limit = min(135, len(text))
    headline = text[:max(100, title_limit + 25)]
    market_frame = bool(_MARKET_FRAME.search(text[:max(175, title_limit + 45)]))
    air_disaster = bool(_AIR_DISASTER.search(text[:350]))

    scores = {label: 0.0 for label in _LABELS}
    head_scores = {label: 0.0 for label in _LABELS}

    counts = Counter(text.split())
    positions = {}
    for match in re.finditer(r"\b[a-z0-9]+\b", text):
        positions.setdefault(match.group(), match.start())

    # Closely related inflected forms share one feature.
    word_evidence = {label: {} for label in _LABELS}
    for word, count in counts.items():
        alternatives = _forms(word)
        best = {}
        for alternative in alternatives:
            values = _WORDS.get(alternative)
            if values:
                for label, weight in values.items():
                    if label not in best or weight > best[label][0]:
                        best[label] = (weight, alternative)
        for label, (weight, canonical) in best.items():
            position = positions.get(word, len(text))
            previous = word_evidence[label].get(canonical)
            if previous is None:
                word_evidence[label][canonical] = [weight, count, position]
            else:
                previous[0] = max(previous[0], weight)
                previous[1] += count
                previous[2] = min(previous[2], position)

    for label, evidence in word_evidence.items():
        for canonical, (weight, count, position) in evidence.items():
            factor = 1.0 + 0.15 * min(3, count - 1)
            contribution = weight * factor * _position_weight(position, title_limit)
            # A corporate president is not, by that title alone, a politician.
            if label == "world" and canonical in ("president", "presidential"):
                if (
                    re.search(r"\b(?:president and (?:chief|ceo)|vice president of|company president|corporate president)\b", text)
                    and not _POLITICAL.search(text.replace("presidential", ""))
                ):
                    contribution *= 0.18
            # Security is shared by military and computing language.
            if label == "world" and canonical == "security":
                if _CYBER.search(text) or re.search(r"\b(?:computer|internet|network|software) security\b", text):
                    contribution *= 0.1
            # Development, health and energy are weak without subject evidence.
            if label == "sci_tech" and canonical in ("development", "energy", "health", "student"):
                contribution *= 0.45
            # Retirement and suspension often occur outside sports.
            if label == "sports" and canonical in ("retirement", "retire", "suspension", "suspended", "transfer", "club", "franchise", "open", "injured", "injury"):
                contribution *= 0.6
            scores[label] += contribution
            if position < title_limit:
                head_scores[label] += weight

    for label, features in _PHRASES.items():
        matches = _match_features(padded, features)
        for phrase, weight, position in matches:
            # A newspaper attribution does not turn a technology story into finance.
            if phrase == "wall street" and " wall street journal " in padded:
                continue
            if phrase == "wall street journal":
                weight = 0.6
            if phrase == "world health organization" and not _RESEARCH.search(text):
                weight = 1.0
            value = weight * _position_weight(position, title_limit)
            scores[label] += value
            if position < title_limit:
                head_scores[label] += weight

    tech_matches = _match_features(padded, _TECH)
    business_matches = _match_features(padded, _BUSINESS)
    sports_matches = _match_features(padded, _SPORTS)
    world_matches = _match_features(padded, _WORLD)

    # Apple fruit and the ordinary adjective "sharp" are not technology firms.
    if re.search(r"\b(?:apple (?:growers|orchards?|crop|harvest|juice|cider)|apples and|apple trees?)\b", text):
        if not re.search(r"\b(?:ipod|iphone|itunes|macintosh|macbook|computer|steve jobs)\b", text):
            tech_matches = [m for m in tech_matches if m[0] != "apple"]

    # Names occurring as parts of other names should not provide opposing evidence.
    sports_names = {m[0] for m in sports_matches}
    if "jerry rice" in sports_names:
        world_matches = [m for m in world_matches if m[0] != "rice"]
    if "james blake" in padded:
        scores["sports"] += 6.0
    if re.search(r"\b(?:gerald ford|president ford)\b", text):
        business_matches = [m for m in business_matches if m[0] == "ford motor"]
        scores["world"] += 8.0
    if "donald trump" in text and _POLITICAL.search(text):
        business_matches = [m for m in business_matches if m[0] != "donald trump"]

    tech_multiplier = 0.40 if market_frame else 1.0
    tech_value, tech_focal, tech_retained = _entity_score(tech_matches, title_limit, tech_multiplier)
    business_value, business_focal, _ = _entity_score(business_matches, title_limit, 0.45 if air_disaster else 1.0)
    sports_value, sports_focal, _ = _entity_score(sports_matches, title_limit)
    world_value, world_focal, _ = _entity_score(world_matches, title_limit)

    scores["sci_tech"] += tech_value
    scores["business"] += business_value
    scores["sports"] += sports_value
    scores["world"] += world_value

    if tech_focal and not market_frame:
        scores["sci_tech"] += 4.0
    if sports_focal:
        scores["sports"] += 2.0
    if world_focal and _POLITICAL.search(text[:260]):
        scores["world"] += 3.0

    for label, weight, pattern in _RULES:
        match = pattern.search(text)
        if match:
            scores[label] += weight * _position_weight(match.start(), title_limit)

    if market_frame:
        scores["business"] += 12.0
        if re.search(r"\b(?:stocks?|shares?|index|indexes|indices|markets?|dow|nasdaq)\b", headline):
            scores["business"] += 4.0

    if air_disaster:
        scores["world"] += 14.0

    if _CYBER.search(text):
        scores["sci_tech"] += 6.0
        if _CYBER.search(headline):
            scores["sci_tech"] += 4.0

    if _RESEARCH.search(headline):
        scores["sci_tech"] += 4.5
    if re.match(r"^(?:study|research|scientists|researchers|science)\b", text):
        scores["sci_tech"] += 3.0

    # A company's financial or legal story remains technology news when
    # the company itself is a technology, internet, or telecom company.
    if tech_focal and not market_frame and _FINANCE_WORDS.search(text):
        financial_weight = scores["business"]
        scores["sci_tech"] += min(20.0, financial_weight * 0.65)
        scores["business"] *= 0.65
        if re.search(r"\b(?:sued|lawsuit|antitrust|patent|court)\b", text):
            scores["sci_tech"] += 3.0

    # Explicit computing context is more informative than incidental legal
    # and law-enforcement vocabulary.
    if (
        _CYBER.search(text)
        and re.search(r"\b(?:internet|computer|software|network|email|website|online)\b", text)
        and not re.search(r"\b(?:terrorist attack|car bomb|suicide bombing|troops)\b", headline)
    ):
        scores["sci_tech"] += min(9.0, scores["world"] * 0.22)

    # Scorelines, pars, yards, and wickets distinguish results from politics
    # and from financial uses of words such as "beat" and "rally".
    scoreline = re.search(r"(?<!\d)\d{1,2}\s*[-:]\s*\d{1,2}(?!\d)", original)
    if scoreline:
        if scores["sports"] >= 7 or _SPORT_RESULT.search(text):
            scores["sports"] += 5.0
    if re.search(r"\b(?:6 0|6 1|6 2|6 3|6 4|7 5|7 6)\b", text):
        if re.search(r"\b(?:tennis|sets?|federer|roddick|agassi|sharapova|wimbledon|open)\b", text):
            scores["sports"] += 5.0
    if re.search(r"\b(?:bonds|giants|rangers|twins|jets|kings|heat|magic|rockets)\b", headline):
        if re.search(r"\b(?:homer|home run|inning|pitcher|baseball|basketball|football|nba|nfl|nhl|mlb|playoff|scored|touchdown|goal)\b", text):
            scores["sports"] += 5.0

    # Governmental and military "strikes" should not be read as labor news.
    if re.search(r"\b(?:air strike|air strikes|military strike|missile strike)\b", text):
        scores["world"] += 3.0
    if re.search(r"\b(?:peace deal|ceasefire deal|cease fire deal)\b", text):
        scores["world"] += 3.0

    # A medical company reporting finances is business unless the substance
    # is a discovery, medicine, safety decision, or clinical research.
    pharma = re.search(
        r"\b(?:merck|pfizer|glaxosmithkline|astrazeneca|eli lilly|"
        r"wyeth|novartis|roche|sanofi|aventis|amgen|genentech)\b", text
    )
    if pharma:
        medical_event = re.search(
            r"\b(?:clinical|trial|trials|vaccine|research|study|"
            r"approved|approves|approval|recall|recalls|withdraw|withdraws|"
            r"pulled|pulls|vioxx|safety|side effects|treatment|"
            r"experimental|cancer|arthritis)\b", text
        )
        if medical_event:
            scores["sci_tech"] += 5.0
        elif _FINANCE_WORDS.search(headline):
            scores["business"] += 6.0

    # A space company's commercial contract can still be fundamentally a
    # space story; ordinary commercial aircraft manufacturing is business.
    if re.search(r"\b(?:boeing|airbus|lockheed martin)\b", headline):
        if re.search(r"\b(?:spacecraft|nasa|space station|satellite|rocket|lunar|mars)\b", text):
            scores["sci_tech"] += 8.0

    # Weather and outbreaks without scientific investigation are public news.
    if re.search(r"\b(?:outbreak|epidemic|pandemic)\b", text):
        if not _RESEARCH.search(text) and not re.search(r"\b(?:vaccine|vaccination|genome|genetic|laboratory|experimental)\b", text):
            scores["world"] += 4.0

    # Additional modest headline emphasis makes incidental background
    # references less likely to defeat the article's main subject.
    for label in _LABELS:
        scores[label] += min(14.0, head_scores[label] * 0.23)

    highest = max(scores.values())
    if highest < 2.4:
        return {"answer": "world"}

    # World is the residual category rather than a positive geographic tag.
    ranking = sorted(_LABELS, key=lambda label: scores[label], reverse=True)
    best = ranking[0]
    if best == "world" and scores["world"] < 8.0:
        for candidate in ("sports", "sci_tech", "business"):
            if scores[candidate] >= 5.0 and scores[candidate] >= scores["world"] * 0.88:
                best = candidate
                break

    return {"answer": best}