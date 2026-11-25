import re
import unicodedata
from functools import lru_cache

_CATEGORIES = ("business", "sci_tech", "sports", "world")
_B, _T, _S, _W = range(4)


def _normalize(text):
    text = unicodedata.normalize("NFKC", text).lower()
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r"\bu\.\s*s\.?", " us ", text)
    text = re.sub(r"\bu\.\s*k\.?", " uk ", text)
    text = re.sub(r"\bu\.\s*n\.?", " un ", text)
    text = re.sub(r"\be\.\s*u\.?", " eu ", text)
    text = re.sub(r"\bat\s*&\s*t\b", " att ", text)
    text = re.sub(r"\bs\s*&\s*p\b", " sp ", text)
    text = re.sub(r"\bwi[\s-]*fi\b", " wifi ", text)
    text = re.sub(r"\be[\s-]+mail\b", " email ", text)
    text = re.sub(r"\bdot[\s-]*com\b", " dotcom ", text)
    text = text.replace("$", " dollar ").replace("€", " euro ")
    text = text.replace("£", " pound ").replace("¥", " yen ")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return " ".join(re.findall(r"[a-z0-9]+", text))


def _words(text):
    return tuple(_normalize(text).split())


_FEATURES = {}
_ENTITIES = {}


def _add(category, weight, entries, plural=False, tag=None):
    for entry in entries.split("|"):
        entry = entry.strip()
        if not entry:
            continue
        key = _words(entry)
        if not key:
            continue
        values = _FEATURES.setdefault(key, [0.0, 0.0, 0.0, 0.0])
        values[category] = max(values[category], float(weight))
        if tag:
            _ENTITIES.setdefault(key, set()).add(tag)
        if plural and len(key) == 1:
            word = key[0]
            if len(word) > 3 and not word.endswith("s"):
                if word.endswith("y") and len(word) > 1 and word[-2] not in "aeiou":
                    variant = word[:-1] + "ies"
                elif word.endswith(("ch", "sh", "x", "z")):
                    variant = word + "es"
                else:
                    variant = word + "s"
                other = _FEATURES.setdefault((variant,), [0.0, 0.0, 0.0, 0.0])
                other[category] = max(other[category], float(weight))


# Financial, commercial, and macroeconomic vocabulary.
for _weight, _entries in [
    (6.5, "wall street|stock market|stock markets|stock exchange|stock exchanges|"
          "federal reserve|central bank|central banks|interest rates|interest rate|"
          "gross domestic product|trade deficit|trade surplus|foreign exchange|"
          "hedge fund|hedge funds|private equity|chapter 11|initial public offering"),
    (6.0, "dow jones|sp 500|s p 500|standard and poor|new york stock exchange|"
          "world trade organization|international monetary fund|european central bank|"
          "bank of england|bank of japan|bank of china|bank of canada|"
          "consumer price index|producer price index|nonfarm payrolls|"
          "balance of payments|mergers and acquisitions|oil prices|crude prices|"
          "crude oil prices|commodity prices|bond market|currency market"),
    (5.0, "nasdaq|nyse|ftse|nikkei|hang seng|dax|cac 40|sensex|opec|"
          "bankruptcy|bankrupt|buyout|takeover|merger|shareholder|dividend|"
          "inflation|deflation|recession|gdp|commodities|commodity|bullion|"
          "retailer|retailing|foreclosure|privatization|privatisation"),
    (4.5, "economic growth|economic recovery|economic outlook|economic slowdown|"
          "consumer spending|consumer confidence|business confidence|"
          "home prices|house prices|housing market|housing starts|real estate|"
          "rate cut|rate cuts|rate hike|rate hikes|interest rate cut|"
          "free trade|trade agreement|trade talks|trade war|"
          "profit warning|net profit|net income|quarterly earnings|"
          "quarterly profit|quarterly loss|earnings report|"
          "stock prices|share prices|market capitalization|"
          "public offering|venture capital|credit rating|credit crunch|"
          "financial crisis|debt crisis|bailout|financial markets|"
          "oil futures|crude futures|oil price|fuel prices|gas prices|"
          "barrel of oil|barrels of oil|brent crude|light sweet crude"),
    (4.0, "economy|economics|economist|banking|brokerage|equities|mortgage|"
          "lender|currency|currencies|futures|unemployment|jobless|"
          "payroll|manufacturing|acquisition|shareholders|"
          "insurer|supermarket|airline|airlines|airways|"
          "retail|refinancing|refinance|tariff|tariffs|forex|"
          "devaluation|depreciation|conglomerate|stockholder|"
          "inflationary|disinflation|stagflation|deregulation"),
    (3.3, "financial|finance|economic|stock|stocks|shares|securities|"
          "investor|investment|dividends|earnings|profits|profit|"
          "revenue|revenues|bank|banks|bond|bonds|yield|yields|"
          "credit|debt|pension|pensions|insurance|exports|imports|"
          "exporter|importer|factory|factories|manufacturer|"
          "gasoline|petrol|crude|barrel|barrels|brent|"
          "wto|imf|ecb|ipo|ipos|underwriter|underwriting|"
          "soybean|soybeans|cotton|wheat|copper|platinum|"
          "housing|foreclosures|lease|leasing|franchise"),
    (2.5, "dollar|euro|yen|sterling|yuan|renminbi|"
          "broker|trading|trader|analyst|analysts|"
          "quarterly|forecast|forecasts|outlook|"
          "industrial|productivity|employment|"
          "oil|refinery|refineries|petroleum|"
          "commodity|aluminum|aluminium|nickel|"
          "retailers|shopping|supermarkets|"
          "layoff|layoffs|downsizing|redundancies|"
          "buyback|buybacks|auction|auctions|"
          "monopoly|antitrust|subsidy|subsidies|"
          "budget deficit|fiscal deficit|tax cuts|tax cut|"
          "labor union|labour union|labor unions|labour unions|"
          "union workers|unionized|unionised|"
          "financial services|investment bank|investment banking|"
          "money market|capital market|capital markets|"
          "export growth|import growth|consumer prices|wholesale prices"),
    (1.6, "sales|business|businesses|corporate|corporation|"
          "company|companies|ceo|chairman|executive|"
          "fiscal|annual|margin|margins|"
          "acquire|acquiring|acquired|purchase|purchases|"
          "bid|bids|bidding|deal|deals|"
          "fuel|diesel|corn|crop|crops|harvest|"
          "agriculture|agricultural|livestock|"
          "store|stores|shop|shops|"
          "consumer|consumers|spending|"
          "economies|privatize|privatise|"
          "aircraft|aviation|airliner|airliners|"
          "passenger|passengers|"
          "gold|silver|metal|metals|"
          "tax|taxes|taxation|"
          "entrepreneur|entrepreneurs|startup|startups"),
    (1.0, "market|markets|index|indices|indexes|"
          "industry|industries|commercial|"
          "restructuring|employment|"
          "flight|flights|carrier|carriers|"
          "pay|wage|wages|"
          "sale|sold|selling|"
          "loss|losses|"
          "advertising|advertiser|advertisers|"
          "pound|trade|"
          "q1|q2|q3|q4"),
    (5.0, "box office|ticket sales|same store sales|same-store sales|"
          "holiday shopping|christmas shopping|black friday|"
          "chief financial officer|chief executive officer|"
          "corporate earnings|earnings forecast|earnings forecasts|"
          "analyst estimates|analysts estimates|"
          "income tax|corporate tax|sales tax|"
          "annual meeting|shareholder meeting|shareholders meeting"),
]:
    _add(_B, _weight, _entries, plural=True)


# Computing, communications, space, basic science, and medical research.
for _weight, _entries in [
    (7.5, "artificial intelligence|machine learning|deep learning|"
          "large language model|large language models|"
          "operating system|operating systems|"
          "search engine|search engines|"
          "open source|source code|"
          "video game|video games|"
          "virtual reality|augmented reality|"
          "cloud computing|quantum computing|"
          "international space station|space station|space shuttle|"
          "stem cell|stem cells|"
          "clinical trial|clinical trials|"
          "human genome|gene editing|gene therapy|"
          "nuclear fusion|large hadron collider|"
          "james webb space telescope"),
    (6.5, "software|semiconductor|microchip|microprocessor|"
          "chipmaker|chipmakers|supercomputer|"
          "internet|cybersecurity|cyberattack|"
          "malware|ransomware|spyware|phishing|"
          "encryption|cryptography|"
          "smartphone|videogame|videogames|"
          "nanotechnology|nanotech|biotechnology|"
          "genome|genomic|dna|rna|"
          "astronaut|cosmonaut|spacecraft|spaceship|"
          "astronomy|astronomer|astrophysics|"
          "paleontology|palaeontology|archaeology|"
          "neuroscience|neuroscientist|"
          "chatgpt|chatbot|blockchain|"
          "wifi|wimax|bluetooth|ethernet|"
          "antivirus|firewall|"
          "qubit|exoplanet|"
          "crispr|mrna"),
    (5.5, "technology|technologies|science|scientific|scientist|"
          "researcher|computer|computing|laptop|"
          "hardware|firmware|desktop|"
          "processor|mainframe|workstation|"
          "browser|browsing|"
          "programmer|programming|algorithm|"
          "hacker|hacking|hacked|"
          "telecom|telecoms|telecommunications|telephony|"
          "broadband|router|modem|"
          "handset|cellphone|smartphone|"
          "robotics|robot|robotic|"
          "gaming|gamer|console|"
          "telescope|observatory|"
          "lunar|martian|orbital|"
          "asteroid|meteorite|comet|"
          "galaxy|galaxies|cosmic|cosmology|"
          "physics|physicist|chemistry|chemist|"
          "biology|biologist|microbiology|"
          "genetics|genetic|chromosome|"
          "embryonic|cloning|biomedical|"
          "laboratory|laboratories|"
          "fossil|dinosaur|archaeologist|archaeological|"
          "paleontologist|palaeontologist|"
          "quantum|subatomic|"
          "nanotube|graphene|"
          "vaccine|antibody|antibodies|"
          "alzheimer|alzheimers|parkinson|parkinsons|"
          "epidemiology|"
          "cryptocurrency|cryptocurrencies|bitcoin|ethereum"),
    (4.5, "research|discovery|discoveries|"
          "pc|pcs|server|servers|"
          "chip|chips|silicon|"
          "email|spam|spammer|website|websites|"
          "wireless|networking|"
          "cellular|3g|4g|5g|gsm|cdma|voip|"
          "satellite|satellites|"
          "digital|electronics|"
          "hacking|vulnerability|vulnerabilities|"
          "malicious|"
          "geneticist|geneticists|molecular|"
          "gene|genes|protein|proteins|enzyme|"
          "organism|organisms|"
          "experimental|experiment|"
          "clinical|"
          "therapy|therapies|therapeutic|"
          "antibiotic|antiviral|"
          "cancer|diabetes|diabetic|dementia|"
          "cardiovascular|cardiology|"
          "obesity|nutrition|"
          "hiv|aids|malaria|tuberculosis|"
          "transplant|transplants|"
          "fertility|infertility|ivf|embryo|"
          "evolution|evolutionary|"
          "extinction|extinct|biodiversity|"
          "geology|geologist|"
          "planetary|meteor|nebula|"
          "universe|orbit|orbiting|"
          "nuclear reactor|nuclear fission|"
          "renewable energy|"
          "solar cell|solar cells|"
          "fuel cell|fuel cells|"
          "self driving|driverless|"
          "mobile phone|mobile phones|cell phone|cell phones|"
          "smart phone|smart phones|"
          "hard drive|hard drives|"
          "graphics card|graphics cards|"
          "flash memory|"
          "neural network|neural networks|"
          "data breach|data breaches|"
          "patent infringement|intellectual property|"
          "internet explorer|"
          "web browser|web browsers|"
          "voice over internet|"
          "electronic mail|"
          "dotcom|dot com"),
    (3.3, "tech|innovation|innovations|"
          "invention|inventions|invented|"
          "notebook|notebooks|disk|disks|"
          "graphics|gpu|cpu|usb|"
          "web|online|cyberspace|"
          "download|downloads|downloaded|"
          "upload|uploads|"
          "electronic|"
          "mobile|phone|phones|telephone|"
          "biotech|biological|"
          "lab|labs|"
          "medicine|medical|"
          "medication|medications|"
          "treatment|treatments|"
          "cure|cures|"
          "surgical|surgery|"
          "vaccination|vaccinated|"
          "immune|immunity|"
          "polio|sars|influenza|"
          "bird flu|avian flu|swine flu|"
          "coronavirus|covid|covid19|"
          "cardiac|stroke|"
          "diet|dietary|vitamin|"
          "species|habitat|ecosystem|"
          "atom|atomic|molecule|"
          "particle|particles|"
          "botany|zoology|"
          "space|moon|mars|"
          "planet|planets|"
          "rocket|rockets|shuttle|"
          "hydrogen|lithium|battery|batteries|"
          "fusion|fission|"
          "automation|autonomous|drone|"
          "climate|greenhouse|"
          "global warming|climate change|"
          "greenhouse gases|carbon dioxide|"
          "solar panel|solar panels|"
          "solar power|solar energy|"
          "electric vehicle|electric vehicles|"
          "electric car|electric cars|"
          "renewable|"
          "cybercrime|cyberwar|"
          "privacy|copyright|patent|"
          "3d printing|3d printer|"
          "lidar|autopilot|"
          "nft|nfts|crypto"),
    (2.0, "study|studies|studied|"
          "findings|discovered|"
          "professor|"
          "data|network|networks|"
          "memory|storage|"
          "code|coding|"
          "search|"
          "virus|viruses|viral|"
          "worm|worms|trojan|"
          "mice|mouse|rat|rats|"
          "monkey|primate|"
          "drug|drugs|"
          "patient|patients|physician|"
          "disease|diseases|illness|"
          "wildlife|endangered|"
          "excavation|excavated|unearthed|"
          "chemicals|chemical|"
          "energy|"
          "emissions|carbon|"
          "prototype|"
          "sensor|sensors|"
          "handheld|handhelds|"
          "pda|pdas|"
          "it security|"
          "security flaw|security flaws|"
          "clinical study|medical study|"
          "peer reviewed|peer review|"
          "genetically modified|"
          "blood pressure"),
    (1.0, "health|healthcare|hospital|hospitals|doctor|doctors|"
          "infection|infections|"
          "discovered|discovery|"
          "streaming|"
          "security|"
          "trial|trials"),
    (7.0, "new study|study finds|study shows|study suggests|"
          "studies show|research shows|research suggests|"
          "scientists say|scientists find|scientists discover|"
          "researchers found|researchers say|researchers discover|"
          "new research|"
          "cancer research|medical research|scientific research|"
          "space probe|mars rover|lunar rover|"
          "outer space|"
          "silicon valley|"
          "windows xp|windows vista|windows 7|windows 10|windows 11|"
          "mac os|mac os x|"
          "genetically engineered|genome sequencing|"
          "heart disease|heart failure|"
          "new england journal of medicine|"
          "national institutes of health|"
          "national science foundation|"
          "national academy of sciences|"
          "massachusetts institute of technology|"
          "food and drug administration"),
]:
    _add(_T, _weight, _entries, plural=True)


# Sports vocabulary. City names alone are deliberately not treated as teams.
for _weight, _entries in [
    (7.0, "olympics|olympic|paralympics|paralympic|"
          "nba|nfl|nhl|mlb|ncaa|fifa|uefa|"
          "nascar|"
          "world cup|super bowl|stanley cup|"
          "champions league|premier league|"
          "world series|"
          "davis cup|fed cup|ryder cup|"
          "tour de france|giro d italia|"
          "formula one|formula 1|"
          "grand slam|"
          "wimbledon|roland garros|"
          "australian open|french open|"
          "us open|british open|"
          "six nations|"
          "southeastern conference|big ten|"
          "march madness|"
          "major league baseball|national football league|"
          "national basketball association|national hockey league|"
          "indian premier league|"
          "international cricket council"),
    (6.0, "football|soccer|baseball|basketball|cricket|rugby|"
          "tennis|golf|hockey|volleyball|badminton|"
          "softball|lacrosse|snooker|"
          "motorsport|motorsports|"
          "quarterback|touchdown|"
          "goalkeeper|"
          "wicket|wickets|batsman|batsmen|"
          "tournament|"
          "playoff|playoffs|postseason|"
          "quarterfinal|semifinal|"
          "doping|"
          "home run|home runs|"
          "test match|test cricket|"
          "one day international|"
          "match fixing|"
          "red card|yellow card|"
          "penalty shootout|"
          "grand prix|"
          "heavyweight title|"
          "world champion|world champions|"
          "national championship"),
    (4.5, "sports|sport|"
          "athlete|athletics|"
          "championship|championships|"
          "champion|champions|"
          "league|leagues|"
          "coach|coaches|coaching|"
          "striker|midfielder|"
          "pitcher|batter|hitter|"
          "inning|innings|"
          "homer|homers|"
          "bowler|bowling|lbw|"
          "referee|umpire|"
          "stadium|"
          "wrestling|boxing|"
          "cycling|swimming|skiing|skating|"
          "gymnastics|fencing|taekwondo|judo|"
          "weightlifting|rowing|sailing|"
          "triathlon|marathon|"
          "billiards|darts|curling|"
          "handball|water polo|"
          "freestyle|breaststroke|backstroke|"
          "steeplechase|decathlon|heptathlon|"
          "equestrian|dressage|"
          "medal|medals|"
          "podium|pole position|"
          "hat trick|hat-trick|"
          "batting|batswoman|"
          "penalty kick|free kick|"
          "tee off|teeing off|"
          "golf course|golf club|"
          "football club|"
          "major league|minor league|"
          "little league|"
          "high jump|long jump|pole vault"),
    (3.0, "player|players|"
          "teammate|"
          "scorer|scoring|scored|"
          "goal|goals|"
          "defeat|defeated|beaten|"
          "match|matches|"
          "racing|race|races|"
          "racer|"
          "lap|laps|"
          "sprint|sprinter|"
          "runner|"
          "season|seasons|"
          "preseason|"
          "semifinals|quarterfinals|"
          "finalist|finalists|"
          "qualifier|qualifying|qualification|"
          "penalty|penalties|"
          "foul|fouls|"
          "rebound|rebounding|"
          "assist|assists|"
          "linebacker|"
          "outfielder|infielder|shortstop|"
          "dugout|"
          "roster|"
          "relegation|"
          "pitching|"
          "birdie|bogey|"
          "strokes|"
          "touchline|"
          "knockout|"
          "title bout|"
          "batting average|"
          "earned run|"
          "comeback win|"
          "overtime|"
          "shootout|"
          "slam dunk|"
          "break point|match point"),
    (1.8, "team|teams|"
          "game|games|"
          "win|wins|winning|won|"
          "victory|"
          "beat|beats|beating|"
          "score|scores|"
          "final|finals|"
          "club|clubs|"
          "cup|"
          "fan|fans|"
          "captain|"
          "defender|"
          "arena|"
          "bronze|"
          "squad|"
          "tackle|"
          "retirement|"
          "injury|injuries|"
          "injured|"
          "seed|seeded|"
          "driver|drivers|"
          "rival|rivals|"
          "offense|defense|"
          "offensive|defensive|"
          "bat|"
          "puck|"
          "bowl|"
          "tour|"
          "professional|"
          "transfer|"
          "unbeaten|undefeated|"
          "draw|"
          "record holder|"
          "world record|"
          "personal best|"
          "gold medal|silver medal|bronze medal"),
]:
    _add(_S, _weight, _entries, plural=True)


# Politics, international affairs, public safety, and disasters.
for _weight, _entries in [
    (7.0, "united nations|security council|"
          "suicide bombing|suicide bomber|"
          "al qaeda|al qaida|"
          "islamic state|"
          "human rights|"
          "military coup|"
          "plane crash|airliner crash|"
          "earthquake|tsunami|"
          "prime minister|"
          "presidential election|general election|"
          "peace talks|"
          "weapons of mass destruction|"
          "ethnic cleansing|"
          "civil war|"
          "terrorist attack|terrorist attacks|"
          "white house|"
          "state department|"
          "homeland security"),
    (5.5, "election|elections|electoral|"
          "parliament|parliamentary|"
          "constitution|constitutional|"
          "diplomatic|diplomat|embassy|ambassador|"
          "terrorism|terrorist|"
          "insurgent|insurgency|"
          "guerrilla|"
          "hostage|"
          "ceasefire|truce|"
          "peacekeeper|peacekeeping|"
          "genocide|massacre|atrocity|"
          "murder|murdered|homicide|manslaughter|"
          "bombing|gunman|gunmen|"
          "shooting|gunfire|"
          "explosion|"
          "hijack|hijacked|hijacker|"
          "coup|"
          "hurricane|typhoon|cyclone|tornado|"
          "quake|"
          "avalanche|mudslide|"
          "famine|"
          "refugee|"
          "humanitarian|"
          "evacuation|"
          "prosecutor|prosecutors|"
          "convicted|conviction|sentenced|"
          "nato|"
          "pentagon|"
          "taliban|hamas|hezbollah|hizbollah|"
          "isis|isil|"
          "supreme court|"
          "foreign minister|foreign ministry|"
          "foreign policy|"
          "west bank|gaza strip|"
          "september 11|sept 11|"
          "war crimes|"
          "international criminal court|"
          "martial law|"
          "death toll|"
          "search and rescue"),
    (4.0, "politics|political|politician|"
          "government|"
          "voter|voters|ballot|"
          "senate|senator|congressional|lawmakers|"
          "democrats|republicans|"
          "democracy|"
          "referendum|"
          "diplomacy|envoy|"
          "militant|rebel|rebellion|separatist|"
          "troops|soldier|soldiers|marines|"
          "military|army|"
          "warfare|invasion|invaded|"
          "missile|missiles|ballistic|"
          "weapons|weapon|"
          "clashes|conflict|"
          "war|wars|"
          "terror|"
          "bomb|bombs|blast|blasts|"
          "police|policeman|policemen|"
          "arrest|arrested|arrests|"
          "prison|jail|jailed|inmate|"
          "jury|"
          "crime|criminal|"
          "ransom|"
          "killed|killing|"
          "wounded|"
          "casualty|casualties|"
          "disaster|catastrophe|"
          "flood|floods|flooding|"
          "wildfire|wildfires|bushfire|"
          "landslide|"
          "eruption|"
          "rescuer|"
          "evacuated|evacuate|"
          "riot|riots|unrest|"
          "protest|protests|protester|"
          "demonstrator|"
          "asylum|"
          "deportation|"
          "sanction|sanctions|"
          "treaty|"
          "interpol|"
          "fbi|cia|"
          "scotland yard|"
          "european union|"
          "peace accord|"
          "coalition government|"
          "suicide attack|"
          "air strike|air strikes|airstrike|airstrikes|"
          "roadside bomb|"
          "car bomb|"
          "air force|"
          "rebel leader|"
          "opposition leader|"
          "opposition party|"
          "governing party|"
          "ruling party|"
          "election campaign|"
          "presidential race|"
          "democratic convention|republican convention"),
    (2.8, "president|presidential|"
          "minister|"
          "congress|"
          "vote|voted|voting|"
          "campaign|"
          "opposition|coalition|"
          "ambassadors|"
          "judge|judges|court|courts|"
          "trial|trials|"
          "prosecution|"
          "sentence|"
          "suspect|suspects|"
          "detained|detention|"
          "investigation|investigators|"
          "murderer|"
          "killer|"
          "abducted|abduction|kidnapped|kidnapping|"
          "assassination|assassinated|"
          "assault|"
          "rape|"
          "robbery|"
          "gang|"
          "smuggling|"
          "attack|attacks|attacked|"
          "battle|battles|"
          "fighting|"
          "navy|"
          "armed|"
          "gun|guns|"
          "grenade|"
          "combat|"
          "occupation|"
          "peace|"
          "deaths|death|dead|"
          "injured|"
          "survivor|"
          "rescue|rescued|"
          "storm|storms|"
          "drought|"
          "volcano|"
          "migrant|immigrant|immigration|"
          "outbreak|epidemic|pandemic|quarantine|"
          "infection outbreak|"
          "public health emergency|"
          "national emergency|"
          "state of emergency|"
          "tropical storm|"
          "tropical depression|"
          "political party|"
          "legislation|"
          "chancellor|"
          "governor|"
          "monarch|"
          "royal family|"
          "pope|vatican|"
          "bishop|"
          "church|"
          "mosque|"
          "islamist|islamic|"
          "independence|"
          "overthrow|"
          "ousted|"
          "summit|"
          "nuclear weapons|"
          "nuclear program|"
          "nuclear programme|"
          "nuclear talks|"
          "iranian nuclear"),
    (1.3, "leader|leaders|"
          "leadership|"
          "party|"
          "poll|polls|"
          "senior official|"
          "officials|"
          "authorities|"
          "legislative|"
          "democratic|republican|"
          "border|borders|"
          "foreign|"
          "nationalist|"
          "protesters|"
          "threat|threats|"
          "shot|"
          "missing|"
          "relief|"
          "fatal|"
          "charged|charges|"
          "illegal|"
          "corruption|"
          "scandal|"
          "forces|"
          "nuclear|"
          "religious|"
          "christian|muslim|"
          "civilian|civilians|"
          "residents|"
          "died|"
          "witness|"
          "bail|"
          "fugitive|"
          "detainee|"
          "espionage|"
          "sovereignty|"
          "un|eu"),
]:
    _add(_W, _weight, _entries, plural=True)


# Technology enterprises retain the technology label when reporting their
# finances or corporate litigation.
_add(_T, 8.5, """
microsoft|google|ibm|intel|nvidia|openai|deepmind|
hewlett packard|hewlett-packard|cisco|cisco systems|
sun microsystems|advanced micro devices|texas instruments|
taiwan semiconductor|tsmc|asml|qualcomm|broadcom|
computer associates|ca technologies|bea systems|
red hat|novell|symantec|mcafee|kaspersky|
apple computer|apple inc|amazon web services|
research in motion|america online|netscape|
aol time warner|yahoo|alibaba|baidu|tencent|
huawei|zte|xiaomi|bytedance|
samsung|nokia|motorola|ericsson|nortel|alcatel|lucent|
deutsche telekom|france telecom|british telecom|
att|verizon|bellsouth|vodafone|nextel|
sbc communications|worldcom|qwest|
ntt docomo|china mobile|china telecom|china unicom|
electronic arts|activision|ubisoft|nintendo|
""", tag="tech_company")

_add(_T, 7.0, """
apple|amazon|dell|hp|lenovo|acer|asus|asustek|compaq|
oracle|sap|salesforce|adobe|macromedia|autodesk|corel|
vmware|citrix|intuit|servicenow|workday|palantir|databricks|
peopleSoft|siebel|sybase|borland|informix|veritas|
emc|netapp|network appliance|akamai|verisign|
seagate|western digital|sandisk|rambus|transmeta|
amd|ati|ati technologies|micron|infineon|stMicroelectronics|
mediatek|marvell|applied materials|arm holdings|
sony|panasonic|toshiba|hitachi|fujitsu|nec|sanyo|philips|
lg electronics|lg|samsung electronics|
sprint|palm|palmone|gateway|blackberry|
facebook|meta|instagram|whatsapp|tiktok|youtube|twitter|
linkedin|pinterest|snapchat|reddit|tumblr|myspace|
ebay|paypal|aol|msn|ask jeeves|altavista|lycos|
mozilla|skype|zoom|dropbox|box inc|slack|
uber|lyft|airbnb|doordash|instacart|
netflix|spotify|shopify|square inc|block inc|
telefonica|telstra|t mobile|tmobile|telecom italia|
bt|ntt|docomo|softbank|airtel|bharti airtel|jio|reliance jio|
comcast|charter communications|echostar|dish network|directv|
mci|juniper networks|juniper|
sco|sco group|suse|canonical|
blizzard|bungie|rockstar games|sega|konami|capcom|
square enix|namco|take two interactive|epic games|zynga|roblox|
valve software|tesla|waymo|spacex|blue origin|
sharp corp|sharp corporation|kingston technology|
trend micro|palo alto networks|crowdstrike|fortinet|
""", tag="tech_company")

_add(_T, 7.0, """
windows|linux|unix|ubuntu|debian|freebsd|android|ios|macos|
macintosh|macbook|imac|iphone|ipad|ipod|itunes|
firefox|google chrome|internet explorer|safari browser|
playstation|xbox|gamecube|gameboy|game boy|wii|nintendo switch|
steam deck|steam platform|steam gaming|
kindle|alexa|treo|symbian|
fortnite|minecraft|warcraft|world of warcraft|
blu ray|dvd|hd dvd|mpeg|
perl|python programming|javascript|java software|java programming|
html|http|https|xml|
""", tag="tech_product")

_add(_T, 7.5, """
nasa|esa|cern|fermilab|hubble|cassini|huygens|
james webb|chandra|james webb telescope|
national aeronautics and space administration|
jet propulsion laboratory|european space agency|
mars express|mars exploration rover|mars reconnaissance orbiter|
large hadron collider|lhc|
""", tag="science_entity")

_add(_T, 4.5, """
fda|cdc|lancet|bmj|caltech|mit|
world health organization|centers for disease control|
national cancer institute|national institutes of health|
royal society|american medical association|
""", tag="science_entity")

# Named commercial enterprises outside the technology industry.
_add(_B, 6.0, """
walmart|wal mart|wal-mart|costco|kmart|sears|tesco|carrefour|
sainsbury|sainsbury s|marks and spencer|marks spencer|
home depot|lowe s|lowes|jc penney|j c penney|best buy|
target corp|target corporation|gap inc|tiffany|
mcdonald s|mcdonalds|burger king|wendy s|wendys|starbucks|
coca cola|coca-cola|pepsi|pepsico|kraft|nestle|unilever|
procter and gamble|procter gamble|p g|heinz|danone|
anheuser busch|inbev|diageo|
general motors|gm|ford|toyota|honda|nissan|renault|
daimlerchrysler|daimler chrysler|daimler|chrysler|
volkswagen|vw|bmw|mercedes benz|mercedes|fiat|porsche|hyundai|kia|
boeing|airbus|embraer|bombardier|
exxon|exxonmobil|exxon mobil|chevron|texaco|conocophillips|
royal dutch shell|shell oil|shell plc|bp|halliburton|schlumberger|
marathon oil|valero|totalenergies|petrochina|petrobras|saudi aramco|
citigroup|citibank|jpmorgan|jp morgan|j p morgan|
goldman sachs|morgan stanley|merrill lynch|lehman brothers|
bank of america|wells fargo|wachovia|bank one|
barclays|hsbc|ubs|deutsche bank|credit suisse|bear stearns|
royal bank of scotland|lloyds|santander|bnp paribas|
aig|american international group|prudential|metlife|
berkshire hathaway|warren buffett|geico|
general electric|honeywell|3m|siemens energy|
caterpillar|deere|john deere|dupont|dow chemical|basf|
pfizer|merck|glaxosmithkline|glaxo|gsk|eli lilly|
astrazeneca|novartis|roche|sanofi|johnson and johnson|
johnson johnson|bristol myers squibb|wyeth|abbott|
amgen|genentech|gilead|biogen|moderna|
procter gamble|gillette|colgate palmolive|
united airlines|american airlines|delta air lines|delta airlines|
northwest airlines|continental airlines|southwest airlines|
us airways|british airways|air france|klm|lufthansa|alitalia|
ryanair|easyjet|jetblue|qantas|singapore airlines|
cathay pacific|emirates airline|virgin atlantic|
amr corp|ual corp|
fedex|united parcel service|ups|
marriott|hilton|hyatt|carnival corp|royal caribbean|
disney|walt disney|viacom|news corp|news corporation|
time warner|bertelsmann|vivendi|paramount|
macy s|macys|nordstrom|neiman marcus|saks|
lvmh|louis vuitton|gucci|prada|hermes|burberry|
nike|adidas|reebok|puma|under armour|
""", tag="business_company")

# Athletes and named sports organizations.
_add(_S, 7.0, """
roger federer|federer|rafael nadal|nadal|novak djokovic|djokovic|
serena williams|venus williams|serena|
andre agassi|agassi|pete sampras|sampras|andy roddick|roddick|
lleyton hewitt|hewitt|tim henman|henman|marat safin|safin|
maria sharapova|sharapova|lindsay davenport|davenport|
justine henin|henin|amelie mauresmo|mauresmo|kim clijsters|clijsters|
martina navratilova|navratilova|kournikova|
svetlana kuznetsova|kuznetsova|elena dementieva|dementieva|
andy murray|carlos alcaraz|alcaraz|jannik sinner|
naomi osaka|iga swiatek|coco gauff|
tiger woods|vijay singh|phil mickelson|mickelson|
ernie els|rory mcilroy|mcilroy|scottie scheffler|
michael jordan|lebron james|lebron|kobe bryant|kobe|
shaquille o neal|shaquille|shaquille oneal|
dwyane wade|tim duncan|kevin garnett|
stephen curry|steph curry|kevin durant|
yao ming|allen iverson|tracy mcgrady|steve nash|
carmelo anthony|dirk nowitzki|jason kidd|
michael phelps|ian thorpe|usain bolt|simone biles|
katie ledecky|eliud kipchoge|
david beckham|beckham|cristiano ronaldo|ronaldo|ronaldinho|
lionel messi|messi|zinedine zidane|zidane|
wayne rooney|rooney|thierry henry|roy keane|michael owen|
steven gerrard|frank lampard|david moyes|alex ferguson|
jose mourinho|mourinho|arsene wenger|wenger|rafael benitez|
pep guardiola|jurgen klopp|kylian mbappe|mbappe|erling haaland|haaland|
sachin tendulkar|tendulkar|brian lara|ricky ponting|ponting|
shane warne|warne|sourav ganguly|ganguly|
rahul dravid|dravid|virender sehwag|sehwag|
muttiah muralitharan|muralitharan|jacques kallis|kallis|
andrew flintoff|flintoff|shoaib akhtar|wasim akram|
inzamam ul haq|virat kohli|kohli|ms dhoni|dhoni|
lance armstrong|michael schumacher|schumacher|
lewis hamilton|max verstappen|verstappen|fernando alonso|
jenson button|kimi raikkonen|raikkonen|rubens barrichello|
dale earnhardt|dale earnhardt jr|jeff gordon|jimmie johnson|
barry bonds|alex rodriguez|derek jeter|randy johnson|
curt schilling|pedro martinez|roger clemens|sammy sosa|
ichiro|hideki matsui|manny ramirez|david ortiz|
shohei ohtani|ohtani|aaron judge|
peyton manning|eli manning|tom brady|brett favre|favre|
donovan mcnabb|mcnabb|michael vick|patrick mahomes|
wayne gretzky|sidney crosby|alex ovechkin|mario lemieux|
mike tyson|muhammad ali|lennox lewis|floyd mayweather|
oscar de la hoya|manny pacquiao|pacquiao|
""", tag="sport_person")

_add(_S, 7.0, """
new york yankees|yankees|boston red sox|red sox|
chicago white sox|white sox|chicago cubs|
new york mets|los angeles dodgers|san francisco giants|
houston astros|st louis cardinals|atlanta braves|
baltimore orioles|toronto blue jays|blue jays|
seattle mariners|oakland athletics|texas rangers|
philadelphia phillies|cleveland indians|cleveland guardians|
detroit tigers|minnesota twins|kansas city royals|
san diego padres|pittsburgh pirates|cincinnati reds|
milwaukee brewers|colorado rockies|arizona diamondbacks|
florida marlins|miami marlins|tampa bay rays|
los angeles angels|anaheim angels|montreal expos|washington nationals|
los angeles lakers|lakers|boston celtics|celtics|
new york knicks|knicks|indiana pacers|pacers|
detroit pistons|pistons|san antonio spurs|
new jersey nets|brooklyn nets|new york nets|
minnesota timberwolves|timberwolves|
dallas mavericks|houston rockets|denver nuggets|
miami heat|orlando magic|chicago bulls|golden state warriors|
cleveland cavaliers|memphis grizzlies|philadelphia 76ers|
philadelphia sixers|76ers|sixers|milwaukee bucks|toronto raptors|
sacramento kings|phoenix suns|utah jazz|portland trail blazers|
oklahoma city thunder|new orleans pelicans|
new england patriots|philadelphia eagles|chicago bears|
green bay packers|packers|pittsburgh steelers|steelers|
dallas cowboys|oakland raiders|las vegas raiders|
kansas city chiefs|minnesota vikings|denver broncos|broncos|
miami dolphins|seattle seahawks|seahawks|atlanta falcons|
san diego chargers|los angeles chargers|cincinnati bengals|bengals|
baltimore ravens|new york jets|jacksonville jaguars|
tampa bay buccaneers|tennessee titans|buffalo bills|
washington redskins|redskins|washington commanders|
san francisco 49ers|49ers|new york giants|
detroit lions|cleveland browns|new orleans saints|
st louis rams|los angeles rams|carolina panthers|
indianapolis colts|arizona cardinals|houston texans|
toronto maple leafs|maple leafs|montreal canadiens|canadiens|
ottawa senators|boston bruins|bruins|new york rangers|
new york islanders|new jersey devils|philadelphia flyers|
pittsburgh penguins|washington capitals|detroit red wings|red wings|
chicago blackhawks|blackhawks|colorado avalanche|
vancouver canucks|canucks|calgary flames|edmonton oilers|oilers|
tampa bay lightning|san jose sharks|los angeles kings|
anaheim ducks|mighty ducks|nashville predators|
""", tag="sport_team")

_add(_S, 7.0, """
manchester united|manchester city|real madrid|atletico madrid|
bayern munich|bayern munchen|borussia dortmund|bayer leverkusen|
inter milan|ac milan|a c milan|
paris saint germain|paris st germain|
newcastle united|aston villa|west ham|west ham united|
blackburn rovers|leeds united|bolton wanderers|
crystal palace|west bromwich|leicester city|
wolverhampton wanderers|nottingham forest|ipswich town|
queens park rangers|sheffield united|sheffield wednesday|
athletic bilbao|real sociedad|real betis|deportivo la coruna|
sporting lisbon|sporting cp|psv eindhoven|
boca juniors|river plate|red bull racing|
mclaren|scuderia ferrari|ferrari f1|
""", tag="sport_team")

_add(_S, 4.5, """
arsenal|chelsea|liverpool|everton|tottenham|fulham|
juventus|fiorentina|lazio|barcelona|barca|schalke|
benfica|galatasaray|fenerbahce|olympiakos|olympiacos|
corinthians|flamengo|cruzeiro|celtic|rangers|ajax|
psg|bundesliga|serie a|la liga|ligue 1|
yankees|mets|dodgers|astros|orioles|padres|phillies|
braves|mariners|diamondbacks|marlins|expos|
spurs|mavericks|cavaliers|grizzlies|raptors|
buccaneers|raiders|patriots|chargers|
""", tag="sport_team")

# Political figures and places that are especially diagnostic of
# international-affairs reporting.
_add(_W, 6.0, """
george w bush|george bush|john kerry|tony blair|
vladimir putin|volodymyr zelensky|volodymyr zelenskiy|
joe biden|donald trump|barack obama|kamala harris|
bill clinton|hillary clinton|
kim jong un|kim jong il|kim il sung|
saddam hussein|saddam|osama bin laden|bin laden|
yasser arafat|arafat|ariel sharon|benjamin netanyahu|netanyahu|
mahmoud abbas|mahmoud ahmadinejad|ayatollah khamenei|
kofi annan|annan|ban ki moon|antonio guterres|
pervez musharraf|musharraf|hamid karzai|karzai|
robert mugabe|mugabe|muammar gaddafi|gaddafi|qaddafi|
slobodan milosevic|milosevic|radovan karadzic|
jacques chirac|chirac|gerhard schroeder|schroeder|
angela merkel|merkel|emmanuel macron|macron|
silvio berlusconi|berlusconi|romano prodi|
junichiro koizumi|koizumi|hu jintao|wen jiabao|xi jinping|
narendra modi|manmohan singh|atal bihari vajpayee|
recep tayyip erdogan|erdogan|bashar al assad|assad|
hugo chavez|chavez|nicolas maduro|maduro|
fidel castro|raul castro|
ariel sharon|ehud olmert|ehud barak|
colin powell|condoleezza rice|donald rumsfeld|
dick cheney|cheney|john edwards|howard dean|
john howard|paul martin|stephen harper|justin trudeau|
dalai lama|pope john paul|pope benedict|pope francis|
""", tag="world_person")

_add(_W, 3.0, """
bush|kerry|blair|putin|zelensky|zelenskiy|trump|biden|obama|
hussein|baghdad|fallujah|falluja|mosul|najaf|kirkuk|
iraq|iraqi|afghanistan|afghan|kabul|kandahar|
gaza|palestinian|palestine|jerusalem|ramallah|
darfur|khartoum|kosovo|pyongyang|tehran|chechnya|chechen|
north korea|north korean|south ossetia|
""", tag="world_context")

_add(_W, 1.4, """
israel|israeli|iran|iranian|sudan|sudanese|rwanda|
ukraine|ukrainian|russia|russian|syria|syrian|
lebanon|lebanese|pakistan|pakistani|
""", tag="world_context")


# Productive word families complement the explicit vocabulary.
_STEM_GROUPS = [
    (_B, 4.0, "bankrupt|sharehold|stockhold|mortgag|privatis|privatiz|"
               "retail|brokerag|refinanc|devalu|inflation|unemploy"),
    (_B, 3.0, "econom|financ|investor|manufactur|export|import|"
               "refiner|restructur|acquisit|conglomer|dividend"),
    (_T, 5.5, "semiconduct|microprocess|microchip|chipmak|supercomput|"
               "nanotech|nanotub|astrophys|astronom|archaeolog|archeolog|"
               "palaeont|paleont|neuroscien|biotechnolog|cryptograph|"
               "cryptocurrenc|cybersecur|cyberattack|ransomwar"),
    (_T, 4.5, "scientis|scientif|researcher|genomic|chromosom|molecul|"
               "biomedic|microbiolog|epidemiolog|physicist|"
               "robotic|telecommunic|programm|"
               "antibod|vaccin|antibiot|antiviral|"
               "alzheimer|parkinson|"
               "paleontolog|archaeolog|"
               "experimental|laborator"),
    (_T, 3.0, "technolog|comput|genetic|neuronal|cardiovascul|"
               "therapeut|transplant|download|upload|"
               "encrypt|decrypt|"
               "exoplanet|planetar|"
               "electronic|"
               "geolog|climatolog"),
    (_S, 5.0, "quarterback|touchdown|goalkeep|midfield|"
               "championship|quarterfinal|semifinal|"
               "olympi|paralympi|"
               "snowboard|skateboard|"
               "weightlift|powerlift|"
               "triathl|decathl|heptathl"),
    (_S, 3.5, "athlet|football|basketball|baseball|"
               "cricket|volleybal|badminton|"
               "gymnast|wrestl|"
               "skier|skiing|swimm|"
               "sprinter|"
               "playoff|relegat|"
               "batting|bowler|"
               "striker|teammat|"
               "referee|umpir"),
    (_W, 5.0, "terroris|insurgen|guerrill|"
               "peacekeep|"
               "earthquak|"
               "hurrican|"
               "kidnapp|"
               "assassinat|"
               "hijack|"
               "prosecut|"
               "genocid|"
               "separatis"),
    (_W, 3.5, "parliament|diplomat|"
               "elector|"
               "politic|"
               "militan|"
               "refugee|"
               "humanitarian|"
               "evacuat|"
               "demonstrat|"
               "deport|"
               "immigra|"
               "bombard|"
               "bombing|"
               "murder|"
               "extradit"),
]
_STEMS = {}
for _cat, _weight, _prefixes in _STEM_GROUPS:
    for _prefix in _prefixes.split("|"):
        _STEMS.setdefault(_prefix[:3], []).append((_prefix, _cat, _weight))

_MAX_NGRAM = max(len(k) for k in _FEATURES)


@lru_cache(maxsize=18000)
def _single_weights(token):
    result = list(_FEATURES.get((token,), (0.0, 0.0, 0.0, 0.0)))
    for prefix, category, weight in _STEMS.get(token[:3], ()):
        if token.startswith(prefix):
            result[category] = max(result[category], weight)
    return tuple(result)


_TITLE_KEYS = {
    "title", "headline", "heading", "subject", "news_title",
    "article_title", "headline_text"
}
_TEXT_KEYS = {
    "text", "content", "body", "description", "article", "news", "story",
    "sentence", "passage", "document", "snippet", "summary", "abstract",
    "article_text", "news_text", "full_text", "fulltext", "body_text",
    "input", "inputs", "data", "payload", "value", "message", "query",
    "review", "paragraph", "lead", "caption"
}
_IGNORE_KEYS = {
    "answer", "label", "labels", "category", "categories", "class",
    "target", "expected", "expected_answer", "question", "questions",
    "task", "task_definition", "instructions", "criteria", "output_schema",
    "id", "index", "url", "link", "source", "author", "date", "timestamp",
    "published", "published_at", "language", "lang", "image", "image_url",
    "candidate_labels", "choices", "options", "metadata"
}


def _extract_text(state):
    titles = []
    pieces = []

    def walk(value, as_title=False, depth=0):
        if depth > 14:
            return
        if isinstance(value, str):
            if value.strip():
                (titles if as_title else pieces).append(value)
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                walk(item, as_title, depth + 1)
            return
        if not isinstance(value, dict):
            return

        recognized = False
        for key, item in value.items():
            if not isinstance(key, str):
                continue
            name = key.lower().strip().replace("-", "_").replace(" ", "_")
            if name in _TITLE_KEYS:
                walk(item, True, depth + 1)
                recognized = True
            elif name in _TEXT_KEYS:
                walk(item, as_title, depth + 1)
                recognized = True

        if not recognized:
            for key, item in value.items():
                if isinstance(key, str):
                    name = key.lower().strip().replace("-", "_").replace(" ", "_")
                    if name in _IGNORE_KEYS:
                        continue
                if isinstance(item, (str, dict, list, tuple)):
                    walk(item, as_title, depth + 1)

    walk(state)
    seen = set()
    clean_titles = []
    clean_pieces = []
    for collection, destination in ((titles, clean_titles), (pieces, clean_pieces)):
        for item in collection:
            key = item.strip()
            if key not in seen:
                destination.append(key)
                seen.add(key)
    title = " ".join(clean_titles)
    body = " ".join(clean_pieces)
    return title, body


_CORPORATE_CUES = set("""
earnings profit profits revenue revenues sales quarterly fiscal shares
shareholders stockholders acquisition acquisitions takeover merger mergers
buyout dividend dividends ceo corporation company corporate analyst analysts
forecast forecasts outlook business investment ipo bankruptcy
""".split())

_TECH_CONTEXT = set("""
software hardware computer computers pc pcs laptop laptops computing chip chips
processor processors semiconductor semiconductors internet online web website
phone phones handset handsets mobile wireless telecom telecommunications
broadband smartphone smartphones cellphone cellphones pda handheld treo palmone
windows linux macintosh macbook ipod iphone ipad ios android browser server
servers database databases networking electronics electronic programming
retailer retailers ecommerce ecom retail kindle aws alexa streaming
""".split())

_RESEARCH_CUES = set("""
research researcher researchers scientist scientists scientific study studies
studied experiment experiments experimental laboratory laboratories lab labs
clinical trial trials findings discovered discovery discoveries genome genetic
dna rna protein proteins vaccine vaccines antibodies sequencing journal
physicist physicists astronomer astronomers telescope telescopes
""".split())

_VIOLENT_CRIME = set("""
murder murdered killing killed homicide rape raped assault assaulted shooting
gunman gunmen kidnapping kidnapped hostage hostages terrorist terrorism bombing
bomb massacre genocide
""".split())

_LEGAL_CUES = {
    "antitrust": 4.0, "lawsuit": 3.5, "lawsuits": 3.5,
    "sued": 3.0, "sue": 2.5, "suing": 3.0,
    "patent": 4.0, "patents": 4.0, "copyright": 4.0,
    "copyrights": 4.0, "infringement": 4.0,
    "settlement": 3.0, "settles": 2.5, "settled": 2.5,
    "court": 2.0, "judge": 2.0, "ruling": 2.0,
    "regulator": 2.0, "regulators": 2.0, "regulatory": 1.5,
    "competition": 1.0, "monopoly": 3.0, "privacy": 3.5,
    "litigation": 4.0, "ftc": 3.0, "doj": 2.0
}

_AMBIGUOUS_TECH = {
    "sprint", "palm", "gateway", "zoom", "apple", "amazon", "sap",
    "juniper", "meta"
}


def _blocked_features(tokens, token_set):
    blocked = set()
    corporate = len(token_set & _CORPORATE_CUES)
    technical = len(token_set & _TECH_CONTEXT)

    if "sprint" in token_set:
        if not (
            token_set & {
                "telecom", "telecommunications", "phone", "phones", "wireless",
                "nextel", "mobile", "handset", "verizon", "att", "pcs",
                "cellular", "broadband", "network"
            }
            or corporate >= 2
            or "sprint corp" in " ".join(tokens)
        ):
            blocked.add(("sprint",))

    if "palm" in token_set:
        if not (
            token_set & {
                "pda", "pdas", "handheld", "handhelds", "treo", "palmone",
                "software", "computer", "computers", "smartphone", "handset"
            }
            or corporate >= 2
        ):
            blocked.add(("palm",))

    if "gateway" in token_set and not (technical >= 1 or corporate >= 2):
        blocked.add(("gateway",))

    if "zoom" in token_set and not (
        token_set & {
            "video", "videoconferencing", "conference", "conferencing",
            "software", "meeting", "meetings", "platform"
        }
        or corporate >= 2
    ):
        blocked.add(("zoom",))

    if "apple" in token_set:
        fruit = token_set & {
            "fruit", "fruits", "orchard", "orchards", "growers", "cider",
            "juice", "harvest", "crops", "crop", "apples"
        }
        if fruit and not token_set & {
            "iphone", "ipad", "ipod", "mac", "macintosh", "macbook", "itunes",
            "ios", "software", "computer", "computers", "jobs", "cook"
        }:
            blocked.add(("apple",))

    if "amazon" in token_set:
        forest = token_set & {
            "rainforest", "rainforests", "jungle", "river", "basin",
            "deforestation", "tribe", "tribes", "indigenous"
        }
        if forest and not token_set & {
            "kindle", "aws", "bezos", "ecommerce", "retailer", "retailing",
            "shares", "earnings", "revenue", "revenues", "online"
        }:
            blocked.add(("amazon",))

    if "sap" in token_set and token_set & {"tree", "trees", "maple", "syrup"}:
        if not (corporate >= 2 or technical >= 2):
            blocked.add(("sap",))

    if "juniper" in token_set and token_set & {
        "tree", "trees", "forest", "plant", "plants", "berries"
    }:
        if technical == 0:
            blocked.add(("juniper",))

    if "bp" in token_set and {"blood", "pressure"} <= token_set:
        if not token_set & {"oil", "crude", "petroleum", "earnings"}:
            blocked.add(("bp",))

    # Literal architectural windows are not a software product.
    if "windows" in token_set:
        building_context = token_set & {
            "shattered", "broken", "shattering", "glass", "building",
            "buildings", "house", "houses", "windshield"
        }
        if building_context and not token_set & {
            "microsoft", "software", "computer", "computers", "pc", "pcs",
            "xp", "vista", "operating", "linux", "malware", "security",
            "browser", "server"
        }:
            blocked.add(("windows",))

    return blocked


_MARKET_MOVEMENT = set("""
rise rises rising rose gain gains gained gaining rally rallies rallied
surge surges surged climb climbs climbed jump jumps jumped advance advances
advanced fall falls falling fell drop drops dropped decline declines declined
slip slips slipped slump slumps slumped tumble tumbles tumbled slide slides
slid lower higher down up flat mixed steady rebound rebounds rebounded
retreat retreats retreated open opens opened close closes closed end ends
ended finish finishes finished hit hits record records weaken weakens
weakened strengthen strengthens strengthened soar soars soared
""".split())

_INDEX_WORDS = {
    "nasdaq", "nikkei", "ftse", "dax", "sensex", "nyse", "dow"
}

_COMMODITIES = {
    "oil", "crude", "gold", "silver", "copper", "wheat", "soybeans",
    "gasoline", "petrol", "dollar", "euro", "yen", "sterling", "bonds"
}


def _broad_market(tokens, tech_positions, title_length):
    lead_end = min(len(tokens), title_length if title_length else 30)
    lead = tokens[:lead_end]
    lead_set = set(lead)
    joined = " ".join(tokens[:60])
    lead_joined = " ".join(lead)
    motion = bool(set(tokens[:60]) & _MARKET_MOVEMENT)
    first_tech = min(tech_positions) if tech_positions else 100000

    broad = False
    phrases = (
        "stock market", "stock markets", "world stocks", "global stocks",
        "asian stocks", "european stocks", "us stocks", "u s stocks",
        "japanese stocks", "tokyo stocks", "london stocks",
        "european shares", "asian shares", "tokyo shares", "london shares",
        "us shares", "world shares", "global shares",
        "stock futures", "equity markets", "financial markets"
    )
    if any(p in lead_joined for p in phrases):
        broad = motion or bool(lead_set & {"stocks", "shares", "markets"})
    if len(set(tokens[:65]) & _INDEX_WORDS) >= 2 and motion:
        broad = True

    for noun in ("stocks", "equities", "bourses"):
        if noun in lead:
            position = lead.index(noun)
            if position < first_tech and motion:
                broad = True

    if "wall street" in lead_joined and motion:
        if not re.search(
            r"wall street (?:expects|analysts|analyst|estimates|forecast|forecasts|"
            r"journal|firms|firm|banks|bank)", lead_joined
        ):
            wall_pos = lead.index("wall") if "wall" in lead else 1000
            if wall_pos <= first_tech:
                broad = True
    return broad


def _commodity_focus(tokens, title_length):
    size = title_length if title_length else min(24, len(tokens))
    lead = tokens[:size]
    lead_set = set(lead)
    movement = bool(set(tokens[:55]) & _MARKET_MOVEMENT)
    if not movement:
        return False
    financial_context = bool(set(tokens[:60]) & {
        "prices", "price", "futures", "barrel", "barrels", "trading", "traders",
        "record", "demand", "supply", "dollar", "dollars", "euro", "yen",
        "yields", "rates", "percent", "cent", "cents"
    })
    if not financial_context:
        return False
    for i, token in enumerate(lead):
        if token in _COMMODITIES and i < 12:
            before = set(lead[:i])
            if not before & {
                "bomb", "bombs", "bombing", "attack", "attacks", "attackers",
                "rebels", "insurgents", "militants", "troops", "killed",
                "hurricane", "earthquake", "spill", "spills"
            }:
                return True
    return False


def predict(state):
    title, body = _extract_text(state)
    title_tokens = _words(title)
    body_tokens = _words(body)
    tokens = (title_tokens + body_tokens)[:5500]
    if not tokens:
        return {"answer": "world"}

    title_length = min(len(title_tokens), len(tokens))
    token_set = set(tokens)
    normalized = " ".join(tokens)
    raw_text = title + "\n" + body
    blocked = _blocked_features(tokens, token_set)

    # A feature contributes once, at its most prominent occurrence, rather
    # than receiving an unbounded bonus for repetition or duplicated headlines.
    feature_scores = {}
    entity_hits = {}
    lead_scores = [0.0] * 4

    def prominence(position):
        if title_length and position < title_length:
            return 1.55
        if position < (title_length + 22 if title_length else 22):
            return 1.22
        if position < (title_length + 45 if title_length else 45):
            return 1.08
        return 1.0

    for position, token in enumerate(tokens):
        factor = prominence(position)
        key = (token,)
        weights = _single_weights(token)
        if key in blocked:
            weights = (0.0, 0.0, 0.0, 0.0)
            # "Sprint" still denotes an athletic event when it is not the
            # telecommunications company.
            if token == "sprint":
                weights = (0.0, 0.0, 3.0, 0.0)

        for category, weight in enumerate(weights):
            if weight:
                score_key = (key, category)
                value = weight * factor
                feature_scores[score_key] = max(
                    feature_scores.get(score_key, 0.0), value
                )

        if key not in blocked and key in _ENTITIES:
            for tag in _ENTITIES[key]:
                entity_hits.setdefault(tag, {})[key] = min(
                    position, entity_hits.get(tag, {}).get(key, position)
                )

        for length in range(2, min(_MAX_NGRAM, len(tokens) - position) + 1):
            phrase = tokens[position:position + length]
            weights = _FEATURES.get(phrase)
            if weights is None:
                continue
            for category, weight in enumerate(weights):
                if weight:
                    score_key = (phrase, category)
                    value = weight * factor
                    feature_scores[score_key] = max(
                        feature_scores.get(score_key, 0.0), value
                    )
            if phrase in _ENTITIES:
                for tag in _ENTITIES[phrase]:
                    entity_hits.setdefault(tag, {})[phrase] = min(
                        position, entity_hits.get(tag, {}).get(phrase, position)
                    )

    scores = [0.0, 0.25, 0.0, 0.5]
    for (phrase, category), value in feature_scores.items():
        scores[category] += value
        base = _FEATURES.get(phrase)
        base_value = base[category] if base else 0.0
        if base_value and value >= base_value * (1.5 if title_length else 1.2):
            lead_scores[category] += value

    tech_entities = entity_hits.get("tech_company", {})
    tech_positions = list(tech_entities.values())
    sport_people = entity_hits.get("sport_person", {})
    sport_teams = entity_hits.get("sport_team", {})
    sport_positions = list(sport_people.values()) + list(sport_teams.values())

    broad_market = _broad_market(tokens, tech_positions, title_length)
    commodity_focus = _commodity_focus(tokens, title_length)
    corporate_count = len(token_set & _CORPORATE_CUES)
    earliest_tech = min(tech_positions) if tech_positions else 100000
    lead_limit = title_length if title_length else 24
    tech_in_lead = earliest_tech < max(lead_limit, 12)

    # The same financial vocabulary describes every industry. For a named
    # technology company it supports, rather than reverses, the technology
    # classification, unless the article is about the overall stock market.
    if tech_entities and not broad_market:
        if corporate_count >= 2:
            inherited = min(27.0, scores[_B] * (0.77 if tech_in_lead else 0.45))
            scores[_T] += inherited + (4.5 if tech_in_lead else 0.0)
        elif corporate_count == 1 and tech_in_lead:
            scores[_T] += min(9.0, scores[_B] * 0.5) + 2.0

        legal_strength = sum(
            weight for word, weight in _LEGAL_CUES.items() if word in token_set
        )
        corporate_legal = bool(token_set & {
            "antitrust", "lawsuit", "lawsuits", "sued", "suing",
            "patent", "patents", "copyright", "copyrights", "infringement",
            "litigation", "settlement", "monopoly", "ftc", "privacy"
        })
        if corporate_legal and not (token_set & _VIOLENT_CRIME):
            scores[_T] += min(28.0, legal_strength * 0.95)
            if tech_in_lead:
                scores[_T] += min(12.0, scores[_W] * 0.22)

    if broad_market:
        scores[_B] += 15.0
        if len(set(tokens[:75]) & _INDEX_WORDS) >= 2:
            scores[_B] += 7.0
        if tech_entities and not tech_in_lead:
            scores[_B] += min(12.0, scores[_T] * 0.17)

    if commodity_focus:
        scores[_B] += 14.0
        # Conflict, weather, and diplomacy often explain a price movement;
        # they do not change the financial subject of that report.
        scores[_B] += min(12.0, scores[_W] * 0.17)

    # Research reports can discuss crime, disasters, disease, or government
    # policy as their subject matter. Explicit research framing is diagnostic.
    research_count = len(token_set & _RESEARCH_CUES)
    first_section = set(tokens[:max(title_length, 25)])
    research_framing = bool(first_section & {
        "study", "studies", "scientists", "scientist", "researchers",
        "researcher", "research", "discovery", "discovers", "experiment"
    })
    if research_framing and research_count >= 2:
        scores[_T] += 6.0
    if (
        ("clinical trial" in normalized or "clinical trials" in normalized)
        and token_set & {
            "drug", "drugs", "vaccine", "vaccines", "therapy", "treatment",
            "cancer", "patients", "medicine"
        }
    ):
        scores[_T] += 8.0

    # A public-health emergency without a research or treatment-development
    # focus is a world event rather than automatically a science story.
    outbreak_terms = token_set & {
        "outbreak", "outbreaks", "epidemic", "epidemics", "pandemic",
        "quarantine", "quarantined"
    }
    if outbreak_terms and not research_framing:
        scores[_W] += 8.0 + min(6.0, len(outbreak_terms) * 2.0)
        if token_set & {"killed", "dead", "deaths", "died", "toll"}:
            scores[_W] += 4.0
    if (
        not research_framing
        and token_set & {"flu", "ebola", "cholera", "sars", "coronavirus", "covid"}
        and token_set & {"spreads", "spreading", "outbreak", "quarantine", "toll"}
        and not token_set & {"vaccine", "vaccines", "trial", "trials", "drug"}
    ):
        scores[_W] += 7.0

    # Airline finances belong to business; accidents, evacuations, and
    # fatalities belong to world news.
    aviation_accident = (
        any(p in normalized for p in (
            "plane crash", "airliner crash", "aircraft crash",
            "plane crashes", "airliner crashes", "helicopter crash",
            "jet crashes", "jet crash", "crashed plane"
        ))
        or (
            token_set & {"plane", "airliner", "aircraft", "helicopter", "flight"}
            and token_set & {"crashed", "crash", "crashes"}
            and token_set & {
                "killed", "dead", "deaths", "passengers", "aboard",
                "survivors", "missing", "injured"
            }
        )
    )
    if aviation_accident and not broad_market and not commodity_focus:
        if not token_set & {"spacecraft", "shuttle", "mars", "lunar", "nasa"}:
            scores[_W] += 13.0

    # Sport remains the subject of player contracts, club takeovers, and
    # athletes' personal legal proceedings.
    if sport_positions:
        earliest_sport = min(sport_positions)
        sport_in_lead = earliest_sport < max(lead_limit, 14)
        sport_context = len(token_set & {
            "sports", "sport", "player", "players", "coach", "team", "teams",
            "match", "matches", "game", "games", "league", "season", "win",
            "wins", "won", "beat", "cup", "tournament", "championship",
            "football", "soccer", "baseball", "basketball", "tennis",
            "cricket", "golf", "hockey", "olympic", "olympics"
        })
        if sport_in_lead and sport_context:
            scores[_S] += 5.0
        if sport_in_lead and token_set & {
            "transfer", "transfers", "contract", "contracts", "signing",
            "signed", "signs", "takeover", "bid", "salary", "salaries",
            "traded", "trade", "deal"
        }:
            scores[_S] += min(16.0, scores[_B] * 0.5) + 4.0
        if sport_people and sport_in_lead:
            if token_set & {
                "trial", "court", "judge", "lawsuit", "rape", "arrested",
                "charged", "charges", "hearing", "surgery", "injury",
                "injured", "retirement", "retires", "retire"
            }:
                scores[_S] += min(18.0, (scores[_W] + scores[_T]) * 0.35)
        if sport_in_lead and token_set & {
            "injury", "injured", "surgery", "treatment", "rehabilitation",
            "fitness", "doping", "steroids", "suspended", "suspension"
        }:
            scores[_S] += 6.0

    # Sports scores and result notation provide evidence that simple lexical
    # methods otherwise miss.
    numeric_scores = re.findall(
        r"(?<!\d)(\d{1,3})\s*[-–]\s*(\d{1,3})(?!\d)", raw_text
    )
    if numeric_scores:
        plausible = [(int(a), int(b)) for a, b in numeric_scores]
        plausible = [(a, b) for a, b in plausible if a <= 160 and b <= 160]
        sports_context = token_set & {
            "beat", "beats", "defeated", "win", "wins", "won", "victory",
            "match", "matches", "game", "games", "set", "sets", "inning",
            "innings", "goals", "scored", "final", "quarterfinal",
            "semifinal", "league", "series", "tennis", "football", "soccer"
        }
        if plausible and sports_context:
            scores[_S] += min(10.0, 4.0 + len(plausible) * 1.5)

    # Disambiguate gaming and computer-security reports from ordinary
    # sporting games or physical attacks.
    gaming_focus = (
        "video game" in normalized or "video games" in normalized
        or "computer game" in normalized or "computer games" in normalized
        or token_set & {"playstation", "xbox", "gamecube", "nintendo", "videogames"}
    )
    if gaming_focus:
        scores[_T] += 6.0
        if tech_entities:
            scores[_T] += min(10.0, scores[_S] * 0.2)

    cyber_focus = token_set & {
        "malware", "ransomware", "spyware", "phishing", "cyberattack",
        "cyberattacks", "cybersecurity", "hacker", "hackers", "hacking",
        "hacked", "antivirus"
    }
    if cyber_focus:
        scores[_T] += 5.0
        if token_set & {"internet", "computer", "computers", "software", "data"}:
            scores[_T] += min(12.0, scores[_W] * 0.22)

    # Election races are not athletic races; a political figure's use of an
    # Internet service does not by itself make an election report technology.
    political_election = token_set & {
        "election", "elections", "presidential", "parliament", "ballot",
        "voters", "senate", "senator", "democrats", "republicans"
    }
    if political_election:
        if token_set & {"race", "races", "campaign", "poll", "polls", "vote"}:
            scores[_W] += 5.0
        if (
            entity_hits.get("world_person")
            and not research_framing
            and not corporate_count >= 3
            and not token_set & {
                "software", "hardware", "chip", "chips", "browser",
                "broadband", "cybersecurity", "hacking", "antitrust"
            }
        ):
            scores[_W] += 5.0

    # Explicit headline evidence is especially useful for long stories with
    # substantial contextual background.
    if title_length:
        strongest_lead = max(lead_scores)
        if strongest_lead >= 12.0:
            lead_category = max(range(4), key=lambda i: lead_scores[i])
            runner_up = sorted(lead_scores, reverse=True)[1]
            if strongest_lead > runner_up * 1.6 + 3.0:
                scores[lead_category] += min(
                    10.0, (strongest_lead - runner_up) * 0.18
                )

    best = max(range(4), key=lambda i: scores[i])
    return {"answer": _CATEGORIES[best]}