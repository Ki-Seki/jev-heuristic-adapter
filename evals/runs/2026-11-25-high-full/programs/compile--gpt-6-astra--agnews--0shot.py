import re
import unicodedata


BUSINESS, SCI_TECH, SPORTS, WORLD = range(4)
_LABELS = ("business", "sci_tech", "sports", "world")

_LEXICON = {}
_TECH_ENTITIES = set()
_BUSINESS_ENTITIES = set()
_SPORT_ENTITIES = set()
_TECH_CORE = set()
_SCIENCE_CORE = set()
_RESEARCH = set()
_SPORT_CORE = set()
_FINANCE = set()
_CORPORATE = set()
_LEGAL = set()
_DISASTERS = set()
_VIOLENCE = set()
_GAMING = set()
_MARKETS = set()


def _decode_entity(match):
    value = match.group(1)
    try:
        number = int(value[1:], 16) if value[:1].lower() == "x" else int(value)
        if 0 <= number <= 1114111:
            return chr(number)
    except (ValueError, OverflowError):
        pass
    return " "


def _normalize(text):
    text = re.sub(r"&#(x[0-9a-fA-F]+|[0-9]+);", _decode_entity, text)
    for old, new in (
        ("&amp;", "&"), ("&quot;", '"'), ("&apos;", "'"),
        ("&nbsp;", " "), ("&lt;", "<"), ("&gt;", ">"),
        ("&#39;", "'"),
    ):
        text = text.replace(old, new)
    text = re.sub(r"<[^>]{1,250}>", " ", text)
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = text.replace("\\n", " ").replace("\\t", " ")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r"\bat\s*&\s*t\b", " att ", text)
    text = re.sub(r"\bu\s*\.\s*s\s*\.?", " us ", text)
    text = re.sub(r"\bu\s*\.\s*k\s*\.?", " uk ", text)
    text = re.sub(r"\bu\s*\.\s*n\s*\.?", " un ", text)
    text = re.sub(r"\be\s*\.\s*u\s*\.?", " eu ", text)
    text = text.replace("c++", " cplusplus ").replace("c#", " csharp ")
    text = re.sub(r"['’]s\b", "", text)
    text = text.replace("'", "").replace("’", "")
    return " ".join(re.findall(r"[a-z0-9]+", text))


def _add(category, weight, phrases, marker=None):
    for phrase in phrases.split("|"):
        term = _normalize(phrase.strip())
        if not term:
            continue
        if term not in _LEXICON:
            _LEXICON[term] = [0.0, 0.0, 0.0, 0.0]
        _LEXICON[term][category] = max(_LEXICON[term][category], weight)
        if marker is not None:
            marker.add(term)


# Financial markets, the economy, and ordinary commerce.
_add(BUSINESS, 5.5,
     "earnings|inflation|recession|deflation|stagflation|unemployment|"
     "bankruptcy|bankruptcies|merger|mergers|takeover|takeovers|"
     "ipo|ipos|dividend|dividends|shareholders|stockholders|"
     "commodities|forex|macroeconomics", _FINANCE)
_add(BUSINESS, 4.1,
     "stocks|shares|equities|profits|profit|revenue|revenues|"
     "economy|economic|economies|economics|jobless|payrolls|"
     "acquisition|acquisitions|buyout|buyouts|"
     "investors|investor|investment|investments|investing|"
     "mortgage|mortgages|banking|insurer|insurers|insurance|"
     "tariffs|tariff|exports|imports|retail|retailer|retailers|"
     "privatization|privatisation|devaluation|austerity|"
     "bullish|bearish|bullion|futures|treasuries|"
     "bankrupt|insolvent|insolvency|liquidation", _FINANCE)
_add(BUSINESS, 3.0,
     "stock|sales|debt|debts|bonds|bond|currency|currencies|"
     "dollar|dollars|yen|euro|sterling|"
     "lenders|lender|loans|loan|bankers|banker|banks|"
     "layoffs|redundancies|downsizing|"
     "pensions|pension|wages|wage|"
     "shareholder|stockholder|brokerage|brokerages|"
     "broker|brokers|traders|trading|"
     "manufacturing|manufacturer|manufacturers|"
     "refinery|refineries|petroleum|crude|gasoline|"
     "commodities|commodity|"
     "trade deficit|trade surplus|"
     "monetary|fiscal|gdp|gdp growth|"
     "ceo|cfo|corporate|entrepreneur|entrepreneurs", _FINANCE)
_add(BUSINESS, 2.1,
     "bank|credit|budget|budgets|tax|taxes|taxation|"
     "spending|consumers|consumer|"
     "markets|marketplace|market|"
     "quarterly|quarter|forecast|forecasts|"
     "restructuring|restructured|restructure|"
     "costs|pricing|prices|price|"
     "business|businesses|commerce|commercial|"
     "shopping|stores|supermarket|supermarkets|"
     "hiring|job cuts|workers|"
     "oil|copper|steel|aluminum|aluminium|"
     "industrial|industry|industries|"
     "economist|economists|valuation|valuations|"
     "fund|funds|finance|financial|financing|"
     "accounting|accountants|auditor|auditors|audit|"
     "yield|yields|productivity|production|"
     "export|import|trade|"
     "lease|leasing|landlord|property prices|"
     "subsidies|subsidy|deficit|surplus")
_add(BUSINESS, 1.0,
     "company|companies|corp|corporation|inc|ltd|"
     "executive|executives|management|"
     "growth|gain|gains|loss|losses|"
     "jobs|employment|store|"
     "gold|silver|coal|wheat|corn|soybeans|sugar|coffee|"
     "contracts|contract|bid|bids|bidding|"
     "assets|asset|stake|stakes|"
     "buy|buying|sell|selling|sold|"
     "expansion|expand|demand|supply|"
     "barrel|barrels|"
     "building|construction|realty")
_add(BUSINESS, 6.8,
     "stock market|stock markets|wall street|dow jones|dow|"
     "s&p 500|nasdaq composite|nyse|"
     "ftse|ftse 100|nikkei|hang seng|"
     "dax|cac 40|russell 2000|"
     "stock exchange|new york stock exchange|"
     "tokyo stock exchange|london stock exchange", _MARKETS)
_add(BUSINESS, 5.0, "nasdaq", _MARKETS)
_add(BUSINESS, 5.2,
     "us stocks|american stocks|asian stocks|european stocks|"
     "japanese stocks|british stocks|global stocks|"
     "asian shares|european shares|japanese shares|"
     "global markets|global shares|"
     "share prices|stock prices|stock index|stock indexes|stock indices|"
     "bond market|bond markets|equity markets|equity market", _MARKETS)
_add(BUSINESS, 7.0,
     "federal reserve|central bank|central banks|"
     "bank of england|bank of japan|european central bank|"
     "interest rates|interest rate|"
     "consumer price index|consumer prices|"
     "gross domestic product|"
     "initial public offering|"
     "balance of trade|"
     "oil prices|oil price|crude oil|"
     "opec|brent crude|west texas intermediate", _FINANCE)
_add(BUSINESS, 5.0,
     "fed|ecb|imf|world bank|"
     "international monetary fund|"
     "world trade organization|world trade organisation|wto|"
     "housing market|real estate|"
     "hedge fund|hedge funds|mutual fund|mutual funds|"
     "private equity|venture capital|"
     "capital gains|capital markets|"
     "rate hike|rate hikes|rate cut|rate cuts|"
     "consumer confidence|consumer spending|"
     "retail sales|"
     "labor market|labour market|"
     "nonfarm payrolls|unemployment rate|"
     "economic growth|economic recovery|"
     "trade deal|trade agreement|free trade|"
     "trade war|trade talks|"
     "natural gas prices|gas prices|"
     "energy prices|fuel prices|"
     "supply chain|supply chains|"
     "balance sheet|cash flow|"
     "credit rating|credit ratings|"
     "credit card|credit cards|"
     "pension fund|pension funds|"
     "cost of living|"
     "financial crisis|debt crisis|"
     "treasury bonds|treasury yields|"
     "quantitative easing|"
     "securities and exchange commission|"
     "securities exchange commission", _FINANCE)
_add(BUSINESS, 4.5,
     "net income|net profit|net profits|"
     "operating profit|operating income|"
     "quarterly earnings|quarterly profit|"
     "earnings report|earnings forecast|"
     "profit warning|profit forecast|"
     "revenue forecast|sales forecast|"
     "earnings per share|"
     "first quarter|second quarter|third quarter|fourth quarter|"
     "full year|fiscal year|"
     "chief executive|chief financial officer|"
     "board of directors|"
     "hostile takeover|"
     "bidding war|price war|"
     "cost cutting|cost cuts|"
     "cut jobs|cuts jobs|slash jobs|"
     "mass layoffs|"
     "accounting scandal|accounting fraud|securities fraud|"
     "insider trading|market manipulation|"
     "antitrust lawsuit|"
     "class action|"
     "same store sales|"
     "box office|film studio|record label|"
     "hotel chain|fast food chain", _CORPORATE)

for _term in (
    "earnings", "profit", "profits", "revenue", "revenues", "quarterly",
    "shares", "stock", "sales", "merger", "mergers", "acquisition",
    "acquisitions", "takeover", "buyout", "layoffs", "dividend",
    "dividends", "shareholders", "bankruptcy", "ipo", "restructuring",
):
    _CORPORATE.add(_term)

_add(BUSINESS, 5.0,
     "airline|airlines|airways|retailing|"
     "automaker|automakers|car maker|car makers|"
     "carmaker|carmakers|auto industry|"
     "oil company|oil companies|"
     "investment bank|investment banks|"
     "department store|department stores|"
     "supermarket chain|"
     "shipping company|freight|logistics|"
     "reinsurance|"
     "hotelier|hoteliers")
_add(BUSINESS, 2.5,
     "airfare|airfares|aviation|"
     "air cargo|air traffic|"
     "automotive|automobile|automobiles|"
     "brewery|brewer|brewers|"
     "tobacco|cigarettes|"
     "mining|miner|miners|"
     "agriculture|agricultural|agribusiness|"
     "tourism|tourists|hotel|hotels|"
     "utilities|utility|"
     "pharmaceutical|pharmaceuticals|drugmaker|drugmakers")

_add(BUSINESS, 6.0,
     "walmart|wal mart|wal-mart|costco|carrefour|tesco|"
     "home depot|lowe's|best buy|"
     "macy's|nordstrom|jc penney|j c penney|"
     "sears|kmart|kroger|safeway|aldi|lidl|"
     "marks and spencer|marks & spencer|"
     "ikea|h&m|zara|inditex|"
     "procter and gamble|procter & gamble|"
     "unilever|nestle|danone|kraft heinz|kraft foods|"
     "coca cola|pepsico|pepsi|"
     "mcdonald's|burger king|wendy's|"
     "starbucks|chipotle|yum brands|"
     "anheuser busch|heineken|diageo|"
     "philip morris|altria|british american tobacco|"
     "gillette|colgate palmolive|"
     "nike|adidas|reebok|under armour|"
     "lvmh|louis vuitton|gucci|prada|kering|"
     "burberry|tiffany|"
     "target corp|target corporation", _BUSINESS_ENTITIES)
_add(BUSINESS, 6.0,
     "exxon|exxonmobil|exxon mobil|"
     "chevron|chevrontexaco|texaco|"
     "royal dutch shell|shell oil|"
     "bp plc|british petroleum|"
     "conocophillips|conoco|phillips 66|"
     "totalenergies|totalfinaelf|"
     "saudi aramco|aramco|"
     "petrobras|petrochina|sinopec|cnooc|"
     "gazprom|rosneft|lukoil|yukos|"
     "halliburton|schlumberger|"
     "enron|duke energy|"
     "bhp|bhp billiton|rio tinto|glencore|"
     "anglo american|arcelormittal|"
     "alcoa|us steel|united states steel|"
     "newmont|barrick gold|"
     "dow chemical|dupont|basf", _BUSINESS_ENTITIES)
_add(BUSINESS, 6.0,
     "general motors|gm|ford motor|ford|"
     "toyota|honda|nissan|hyundai|kia|"
     "volkswagen|vw|"
     "daimler|daimlerchrysler|chrysler|stellantis|"
     "renault|peugeot|citroen|"
     "bmw|mercedes benz|"
     "porsche|ferrari|volvo|"
     "land rover|jaguar land rover|"
     "rivian|lucid motors|"
     "general electric|ge capital|"
     "3m|caterpillar|deere|john deere|"
     "honeywell|"
     "boeing|airbus|embraer|bombardier|"
     "lockheed martin|northrop grumman|raytheon|"
     "rolls royce", _BUSINESS_ENTITIES)
_add(BUSINESS, 6.0,
     "united airlines|american airlines|"
     "us airways|southwest airlines|"
     "delta air lines|delta airlines|"
     "continental airlines|northwest airlines|"
     "jetblue|ryanair|easyjet|"
     "air france|klm|lufthansa|"
     "british airways|virgin atlantic|"
     "qantas|air canada|alitalia|"
     "singapore airlines|cathay pacific|"
     "emirates airline|qatar airways|"
     "turkish airlines|"
     "fedex|federal express|united parcel service|"
     "dhl|maersk|"
     "marriott|hilton hotels|hyatt|"
     "carnival corp|royal caribbean", _BUSINESS_ENTITIES)
_add(BUSINESS, 6.0,
     "goldman sachs|morgan stanley|"
     "jpmorgan|jp morgan|j p morgan|"
     "jpmorgan chase|"
     "bank of america|citigroup|citibank|"
     "wells fargo|wachovia|"
     "merrill lynch|lehman brothers|bear stearns|"
     "hsbc|barclays|lloyds|"
     "royal bank of scotland|"
     "deutsche bank|commerzbank|"
     "credit suisse|ubs|"
     "bnp paribas|societe generale|"
     "santander|unicredit|"
     "berkshire hathaway|"
     "blackrock|blackstone|vanguard|"
     "fidelity investments|charles schwab|"
     "american express|mastercard|"
     "prudential|metlife|allstate|aig|"
     "american international group|"
     "allianz|axa|zurich insurance|"
     "munich re|swiss re|"
     "fannie mae|freddie mac|"
     "countrywide financial|"
     "capital one|discover financial", _BUSINESS_ENTITIES)
_add(BUSINESS, 5.5,
     "pfizer|merck|glaxosmithkline|gsk|"
     "astrazeneca|novartis|roche|sanofi|"
     "bristol myers squibb|eli lilly|"
     "johnson and johnson|johnson & johnson|"
     "abbott laboratories|abbvie|"
     "bayer|boehringer ingelheim|"
     "amgen|genentech|gilead|biogen|"
     "moderna|biontech|"
     "cvs|walgreens|unitedhealth|"
     "cigna|humana|aetna|"
     "disney|walt disney|"
     "time warner|warner bros|warner music|"
     "viacom|paramount|mgm|"
     "news corp|news corporation|"
     "bertelsmann|vivendi|"
     "universal music|sony pictures|"
     "wpp|publicis|omnicom|"
     "warren buffett|alan greenspan|"
     "ben bernanke|jerome powell|janet yellen", _BUSINESS_ENTITIES)

# Computing, communications, electronics, and technology products.
_add(SCI_TECH, 6.0,
     "software|hardware|computer|computers|computing|"
     "semiconductor|semiconductors|microprocessor|microprocessors|"
     "internet|broadband|telecommunications|telecom|"
     "smartphone|smartphones|"
     "cybersecurity|malware|ransomware|spyware|"
     "robotics|algorithm|algorithms|"
     "nanotechnology|"
     "blockchain|"
     "chatbot|chatbots|"
     "supercomputer|supercomputers", _TECH_CORE)
_add(SCI_TECH, 4.7,
     "processor|processors|chipset|chipsets|"
     "laptop|laptops|notebook computer|"
     "desktop|desktops|server|servers|database|databases|"
     "browser|browsers|"
     "wireless|wifi|wi fi|"
     "cellphone|cellphones|handset|handsets|"
     "tablet|tablets|"
     "gadget|gadgets|electronics|"
     "hacker|hackers|hacking|hacked|"
     "cyberattack|cyberattacks|cybercrime|"
     "phishing|firewall|firewalls|"
     "spam|spammer|spammers|"
     "encryption|cryptography|"
     "programmer|programmers|programming|"
     "codebase|compiler|debugging|"
     "robot|robots|"
     "microchip|microchips|"
     "chipmaker|chipmakers|"
     "microelectronics|"
     "touchscreen|touchscreens|"
     "oled|lcd|"
     "bluetooth|"
     "5g|4g|3g|"
     "telephony|voip|"
     "bandwidth|"
     "wearable|wearables|"
     "smartwatch|smartwatches|"
     "app|apps|"
     "appstore|"
     "ecommerce|"
     "fintech|"
     "metaverse|"
     "3d printing|"
     "virtualization|virtualisation", _TECH_CORE)
_add(SCI_TECH, 3.0,
     "web|website|websites|"
     "email|e mail|emails|"
     "digital|"
     "phone|phones|mobile|"
     "chip|chips|"
     "pc|pcs|"
     "disk|disks|"
     "printer|printers|"
     "scanner|scanners|"
     "router|routers|"
     "modem|modems|"
     "electronic|"
     "download|downloads|downloading|"
     "upload|uploads|"
     "streaming|"
     "blog|blogs|blogger|bloggers|"
     "podcast|podcasts|"
     "webcam|webcams|"
     "patent|patents|"
     "invention|inventions|"
     "automation|"
     "drones|drone|"
     "ai|"
     "3d|"
     "gpu|gpus|cpu|cpus|"
     "ssd|"
     "usb|"
     "dvd|blu ray|"
     "mp3|"
     "startup|startups", _TECH_CORE)
_add(SCI_TECH, 1.3,
     "online|network|networks|networking|"
     "device|devices|"
     "technical|technological|technology|technologies|"
     "innovation|innovative|"
     "memory|"
     "privacy|"
     "cyber|"
     "platform|platforms|"
     "connectivity|"
     "developers|developer|"
     "virtual|"
     "video|"
     "sensor|sensors|"
     "battery|batteries")
_add(SCI_TECH, 7.0,
     "artificial intelligence|machine learning|deep learning|"
     "neural network|neural networks|"
     "large language model|large language models|"
     "generative ai|"
     "operating system|operating systems|"
     "search engine|search engines|"
     "cloud computing|cloud storage|"
     "data center|data centers|data centre|data centres|"
     "data breach|data breaches|"
     "computer virus|computer viruses|"
     "computer worm|computer worms|"
     "computer security|network security|"
     "security flaw|security flaws|"
     "security patch|security patches|"
     "zero day|"
     "denial of service|"
     "open source|"
     "source code|"
     "web browser|web browsers|"
     "social media|social network|social networks|"
     "mobile phone|mobile phones|"
     "cell phone|cell phones|"
     "cellular phone|cellular phones|"
     "mobile internet|"
     "mobile app|mobile apps|"
     "personal computer|personal computers|"
     "hard drive|hard drives|"
     "disk drive|disk drives|"
     "flash memory|"
     "quantum computing|quantum computer|"
     "virtual reality|augmented reality|"
     "self driving|autonomous driving|"
     "self driving car|driverless car|"
     "autonomous vehicle|autonomous vehicles|"
     "internet of things|"
     "fiber optic|fibre optic|"
     "information technology|"
     "it industry|it services|it spending|"
     "e commerce|"
     "electronic payment|electronic payments|"
     "digital wallet|"
     "patent infringement|software patent|"
     "software patents", _TECH_CORE)
_add(SCI_TECH, 5.5,
     "linux|unix|android|ios|macos|"
     "windows xp|windows vista|windows 95|windows 98|"
     "windows 2000|windows 7|windows 8|windows 10|windows 11|"
     "microsoft office|powerpoint|"
     "javascript|typescript|cplusplus|csharp|"
     "python programming|java programming|"
     "html|xml|php|"
     "sql|mysql|postgresql|"
     "kubernetes|docker|"
     "git|github|gitlab|"
     "firefox|mozilla|netscape|"
     "internet explorer|google chrome|"
     "wordpress|"
     "photoshop|acrobat|"
     "autocad|"
     "trojan horse|"
     "usb c|"
     "hd dvd|"
     "mp3 player|dvd player|"
     "file sharing|peer to peer|"
     "music download|music downloads|"
     "digital music|online music|"
     "bittorrent|napster|kazaa|grokster|"
     "itunes|"
     "instant messaging|"
     "text messaging|"
     "voice over internet|"
     "wifi hotspot|wi fi hotspot", _TECH_CORE)
_add(SCI_TECH, 2.5,
     "windows|java|python|perl|"
     "bitcoin|ethereum|cryptocurrency|cryptocurrencies|crypto|"
     "nft|nfts|"
     "llm|llms")
_add(BUSINESS, 2.8,
     "bitcoin|ethereum|cryptocurrency|cryptocurrencies|crypto|"
     "cryptocurrency market|crypto market|"
     "exchange traded fund|exchange traded funds|etf|etfs")

_add(SCI_TECH, 7.0,
     "microsoft|google|ibm|intel|"
     "nvidia|amd|advanced micro devices|"
     "apple inc|apple computer|apple computers|"
     "amazon com|amazon web services|aws|"
     "alphabet inc|meta platforms|"
     "facebook|instagram|whatsapp|"
     "twitter|tiktok|bytedance|"
     "yahoo|ebay|paypal|"
     "youtube|"
     "linkedin|reddit|pinterest|snapchat|"
     "baidu|alibaba|tencent|wechat|"
     "netflix|spotify|roku|"
     "openai|chatgpt|anthropic|deepmind|"
     "hugging face|"
     "dell|hewlett packard|hewlett packard enterprise|"
     "hp|hpe|"
     "lenovo|acer|asus|asustek|"
     "toshiba|fujitsu|nec|"
     "samsung|sony|panasonic|"
     "lg electronics|lg display|"
     "philips|"
     "huawei|zte|xiaomi|oneplus|"
     "motorola|nokia|ericsson|"
     "blackberry|research in motion|"
     "palmone|palmsource|"
     "cisco|cisco systems|juniper networks|"
     "qualcomm|broadcom|"
     "texas instruments|micron|"
     "tsmc|taiwan semiconductor|"
     "asml|infineon|stmicroelectronics|"
     "marvell technology|"
     "ati technologies|"
     "arm holdings|arm ltd|"
     "sun microsystems|"
     "adobe|autodesk|intuit|"
     "salesforce|servicenow|"
     "oracle corp|oracle corporation|"
     "sap|"
     "symantec|mcafee|norton antivirus|"
     "crowdstrike|"
     "palo alto networks|"
     "fortinet|"
     "novell|red hat|suse|"
     "sco group|sco|"
     "computer associates|"
     "borland|bea systems|"
     "verisign|veritas software|"
     "emc|vmware|citrix|netapp|"
     "seagate|western digital|sandisk|"
     "kingston technology|"
     "epson|lexmark|xerox|"
     "akamai|cloudflare|"
     "dropbox|"
     "atlassian|"
     "snowflake inc|"
     "palantir|"
     "infosys|wipro|tata consultancy|"
     "accenture|"
     "softbank|"
     "garmin|fitbit|gopro|"
     "logitech|"
     "dji|"
     "uber|lyft|airbnb|"
     "doordash|instacart|"
     "stripe|square inc|block inc|"
     "shopify|"
     "tivo", _TECH_ENTITIES)
_add(SCI_TECH, 6.5,
     "aol|america online|"
     "att|at and t|"
     "verizon|vodafone|"
     "t mobile|"
     "sprint nextel|nextel|"
     "deutsche telekom|"
     "france telecom|"
     "british telecom|bt group|"
     "telefonica|"
     "telecom italia|"
     "ntt|ntt docomo|"
     "china mobile|china telecom|"
     "singtel|"
     "telstra|"
     "rogers communications|"
     "bce inc|bell canada|"
     "qwest|mci|worldcom|"
     "lucent|alcatel|alcatel lucent|"
     "nortel|"
     "siemens|"
     "comcast|charter communications|"
     "time warner cable|cablevision|"
     "directv|dish network|"
     "echostar", _TECH_ENTITIES)
_add(SCI_TECH, 6.3,
     "apple|amazon|alphabet|meta|oracle|"
     "zoom|sprint|palm|gateway|orange|sharp|arm", _TECH_ENTITIES)
_add(SCI_TECH, 6.0,
     "iphone|ipad|ipod|imac|macbook|macintosh|"
     "apple watch|airpods|"
     "surface pro|"
     "google pixel|google glass|"
     "samsung galaxy|"
     "blackberry phone|"
     "palm pilot|treo|"
     "kindle|"
     "alexa|siri|"
     "oculus|meta quest|"
     "vision pro|"
     "chromebook|"
     "raspberry pi|"
     "beos|"
     "symbian|"
     "bill gates|steve ballmer|"
     "steve jobs|tim cook|"
     "larry page|sergey brin|sundar pichai|"
     "mark zuckerberg|"
     "satya nadella|"
     "larry ellison|"
     "michael dell|"
     "jeff bezos|"
     "jensen huang|"
     "sam altman", _TECH_ENTITIES)
_add(SCI_TECH, 5.0,
     "tesla|spacex|blue origin|rocket lab|"
     "neuralink|"
     "elon musk", _TECH_ENTITIES)

# Video games are technology, including sports-themed software.
_add(SCI_TECH, 8.0,
     "video game|video games|"
     "computer game|computer games|"
     "playstation|xbox|nintendo|"
     "gamecube|game boy|gameboy|"
     "wii|switch console|"
     "electronic arts|ea sports|"
     "activision|blizzard entertainment|"
     "ubisoft|"
     "sega|atari|"
     "rockstar games|"
     "epic games|"
     "riot games|"
     "bethesda|"
     "square enix|"
     "capcom|konami|namco|"
     "bandai namco|"
     "take two interactive|"
     "valve software|valve corporation|"
     "steam deck|"
     "unreal engine|"
     "unity engine|"
     "grand theft auto|"
     "world of warcraft|warcraft|"
     "fortnite|minecraft|roblox|"
     "call of duty|counter strike|"
     "halo 2|halo 3|halo infinite|"
     "doom 3|doom eternal|"
     "final fantasy|"
     "legend of zelda|"
     "super mario|"
     "pokemon|"
     "the sims|"
     "half life|"
     "league of legends|"
     "dota 2|"
     "elden ring|"
     "baldur's gate|"
     "cyberpunk 2077|"
     "assassin's creed|"
     "fifa 23|fifa 24|ea sports fc|"
     "nba 2k|madden nfl", _GAMING)
_add(SCI_TECH, 4.5,
     "gaming|gamer|gamers|"
     "console|consoles|"
     "gameplay|multiplayer|"
     "mmorpg|"
     "esports|e sports|"
     "joystick|"
     "game developer|game developers|"
     "game publisher|"
     "game engine|"
     "tetris", _GAMING)

# Natural sciences, space, engineering research, and medicine.
_add(SCI_TECH, 6.0,
     "scientist|scientists|"
     "researcher|researchers|"
     "scientific|"
     "astronomer|astronomers|astronomy|"
     "astrophysicist|astrophysicists|astrophysics|"
     "physicist|physicists|"
     "biologist|biologists|"
     "geneticist|geneticists|"
     "neuroscientist|neuroscientists|"
     "paleontologist|paleontologists|paleontology|"
     "archaeologist|archaeologists|archaeology|"
     "geologist|geologists|"
     "oceanographer|oceanographers|"
     "ecologist|ecologists|"
     "chemist|chemists|"
     "epidemiologist|epidemiologists", _RESEARCH)
_add(SCI_TECH, 3.2,
     "science|research|"
     "laboratory|laboratories|"
     "experiment|experiments|experimental|"
     "discovery|discoveries|"
     "biology|biological|"
     "physics|chemistry|"
     "geology|ecology|"
     "neuroscience|"
     "biochemistry|"
     "biotechnology|biotech|"
     "biomedical|"
     "engineering|"
     "theoretical|"
     "peer reviewed|"
     "clinical|"
     "medical research", _RESEARCH)
_add(SCI_TECH, 2.2, "study|studies|"
     "findings|"
     "laboratory test|"
     "published in", _RESEARCH)
_add(SCI_TECH, 5.5,
     "study finds|study shows|study suggests|"
     "studies show|"
     "research shows|research finds|"
     "research team|"
     "new study|"
     "scientific study|"
     "clinical trial|clinical trials|"
     "randomized trial|randomised trial|"
     "journal nature|journal science|"
     "new england journal of medicine|"
     "the lancet|"
     "nobel prize in physics|nobel prize in chemistry|"
     "nobel prize in medicine|"
     "national institutes of health|"
     "national science foundation|"
     "massachusetts institute of technology|"
     "caltech", _RESEARCH)
_add(SCI_TECH, 6.0,
     "dna|rna|genome|genomes|genomics|"
     "genetics|"
     "stem cell|stem cells|"
     "gene editing|gene therapy|"
     "crispr|"
     "cloning|"
     "quantum|"
     "higgs|higgs boson|"
     "cern|large hadron collider|"
     "particle accelerator|"
     "nuclear fusion|fusion reactor|"
     "nuclear physics|"
     "superconductivity|superconductor|"
     "gravitational waves|"
     "dark matter|dark energy|"
     "antimatter|"
     "nanoparticle|nanoparticles|"
     "graphene", _SCIENCE_CORE)
_add(SCI_TECH, 3.8,
     "genetic|gene|genes|"
     "chromosome|chromosomes|"
     "mutation|mutations|"
     "molecule|molecules|molecular|"
     "protein|proteins|"
     "enzyme|enzymes|"
     "microbe|microbes|"
     "bacteria|bacterial|"
     "microbial|"
     "microbiome|"
     "neuron|neurons|"
     "neural|"
     "cognitive|"
     "embryo|embryos|embryonic|"
     "cloned|"
     "fossil|fossils|"
     "dinosaur|dinosaurs|"
     "evolution|evolutionary|"
     "biodiversity|"
     "extinction|"
     "ecosystem|ecosystems|"
     "photosynthesis|"
     "seismology|"
     "tectonic|tectonics|"
     "paleolithic|"
     "hominid|hominids|"
     "neanderthal|neanderthals|"
     "exoplanet|exoplanets|"
     "photon|photons|"
     "electron|electrons|"
     "particle|particles|"
     "isotope|isotopes|"
     "laser|lasers|"
     "radiocarbon|"
     "carbon dating", _SCIENCE_CORE)
_add(SCI_TECH, 2.0,
     "species|"
     "habitat|habitats|"
     "mammal|mammals|"
     "primate|primates|"
     "chimpanzee|chimpanzees|"
     "insects|"
     "coral|"
     "organism|organisms|"
     "anatomy|"
     "physiology|"
     "brain|brains|"
     "cells|cellular|"
     "tissue|tissues|"
     "radiation|"
     "magnetic|magnetism|"
     "microscope|microscopy|"
     "artifact|artifacts|artefact|artefacts|"
     "excavation|"
     "pyramid|pyramids|"
     "mummy|mummies|"
     "prehistoric|"
     "hydrogen|helium|"
     "antibiotic|antibiotics|"
     "antibody|antibodies|"
     "pathogen|pathogens|"
     "virus|viruses", _SCIENCE_CORE)
_add(SCI_TECH, 7.0,
     "nasa|esa space|european space agency|"
     "space station|international space station|"
     "space shuttle|"
     "space telescope|hubble|james webb|"
     "astronaut|astronauts|cosmonaut|cosmonauts|"
     "spacecraft|"
     "spaceflight|space flight|"
     "manned mission|crewed mission|"
     "moon landing|lunar landing|"
     "mars rover|"
     "mars exploration|"
     "deep space|outer space|"
     "solar system|"
     "black hole|black holes|"
     "big bang|"
     "cassini|huygens|"
     "chandra|"
     "perseverance rover|"
     "curiosity rover|"
     "artemis mission|"
     "voyager 1|voyager 2", _SCIENCE_CORE)
_add(SCI_TECH, 4.5,
     "astronomical|cosmic|cosmology|"
     "galaxy|galaxies|"
     "nebula|nebulae|"
     "supernova|supernovae|"
     "pulsar|pulsars|"
     "quasar|quasars|"
     "asteroid|asteroids|"
     "comet|comets|"
     "meteorite|meteorites|"
     "meteor|meteors|"
     "planet|planets|planetary|"
     "mars|jupiter|pluto|neptune|uranus|"
     "lunar|"
     "orbit|orbital|orbiting|"
     "satellite|satellites|"
     "telescope|telescopes|"
     "rover|"
     "spacewalk|"
     "interstellar|"
     "eclipse|eclipses|"
     "aurora|auroras|"
     "observatory|"
     "galileo|"
     "soyuz|shenzhou|"
     "starliner", _SCIENCE_CORE)
_add(SCI_TECH, 2.3,
     "space|rocket|rockets|"
     "moon|moons|"
     "solar|"
     "starlight|"
     "launchpad|"
     "cosmos|"
     "solar flare|solar flares|"
     "zero gravity|"
     "meteor shower", _SCIENCE_CORE)
_add(SCI_TECH, 4.0,
     "global warming|climate change|"
     "greenhouse gas|greenhouse gases|"
     "ozone layer|ozone hole|"
     "ocean acidification|"
     "carbon capture|"
     "climate model|climate models|"
     "climate science|"
     "renewable technology|"
     "solar cell|solar cells|"
     "photovoltaic|photovoltaics|"
     "fuel cell|fuel cells|"
     "battery technology", _SCIENCE_CORE)
_add(SCI_TECH, 4.5,
     "vaccine|vaccines|"
     "vaccinology|"
     "immunotherapy|"
     "chemotherapy|"
     "radiotherapy|"
     "alzheimer|alzheimer's|"
     "parkinson|parkinson's|"
     "hiv|"
     "insulin|"
     "diabetes|"
     "tumor|tumors|tumour|tumours|"
     "oncology|"
     "transplant|transplants|"
     "prosthetic|prosthetics|"
     "fertility treatment|"
     "in vitro fertilization|ivf|"
     "drug discovery|"
     "fda approves|fda approval|drug approval|"
     "experimental drug|experimental treatment", _SCIENCE_CORE)
_add(SCI_TECH, 2.8,
     "cancer|leukemia|leukaemia|"
     "aids|"
     "ebola|"
     "covid|covid 19|coronavirus|"
     "sars|"
     "influenza|"
     "bird flu|avian flu|"
     "swine flu|"
     "malaria|tuberculosis|"
     "dementia|"
     "obesity|"
     "asthma|"
     "autism|"
     "arthritis|"
     "cardiovascular|"
     "heart disease|"
     "blood pressure|"
     "cholesterol|"
     "surgery|surgical|"
     "medical|medicine|"
     "treatment|treatments|therapeutic|therapy|therapies|"
     "patients|"
     "diagnosis|diagnostic|"
     "screening|"
     "nutrition|nutritional|"
     "vaccination|"
     "immunity|immune|"
     "fda|"
     "public health research", _SCIENCE_CORE)
_add(SCI_TECH, 1.1,
     "health|healthy|"
     "drug|drugs|"
     "patient|hospital|hospitals|"
     "doctor|doctors|"
     "disease|diseases|"
     "infection|infections|"
     "infectious|"
     "symptoms|"
     "diet|"
     "cdc|"
     "world health organization|world health organisation")

# Sporting disciplines, results, competitions, clubs, and athletes.
_add(SPORTS, 7.0,
     "football|soccer|baseball|basketball|"
     "hockey|tennis|golf|rugby|cricket|"
     "volleyball|badminton|gymnastics|"
     "taekwondo|judo|"
     "biathlon|triathlon|"
     "motogp|nascar|indycar|"
     "formula one|formula 1|f1|"
     "grand prix|"
     "nba|wnba|nfl|mlb|nhl|"
     "ncaa|pga|lpga|wta|"
     "ufc|mma|"
     "olympics|olympic|paralympics|paralympic|"
     "super bowl|world series|"
     "world cup|"
     "champions league|europa league|"
     "premier league|premiership|"
     "la liga|serie a|bundesliga|ligue 1|"
     "major league baseball|major league soccer|"
     "national football league|national basketball association|"
     "national hockey league|"
     "australian football|"
     "aussie rules|"
     "six nations|"
     "wimbledon|"
     "us open|australian open|french open|"
     "roland garros|"
     "ryder cup|presidents cup|solheim cup|"
     "davis cup|billie jean king cup|"
     "tour de france|giro d italia|vuelta a espana|"
     "indianapolis 500|indy 500|daytona 500|"
     "kentucky derby|belmont stakes|preakness|breeders cup", _SPORT_CORE)
_add(SPORTS, 5.0,
     "sports|sporting|athlete|athletes|"
     "tournament|tournaments|"
     "championship|championships|"
     "playoff|playoffs|postseason|preseason|"
     "semifinal|semifinals|semi final|semi finals|"
     "quarterfinal|quarterfinals|quarter final|quarter finals|"
     "quarterback|quarterbacks|"
     "pitcher|pitchers|"
     "goalkeeper|goalkeepers|"
     "linebacker|"
     "touchdown|touchdowns|"
     "inning|innings|"
     "wicket|wickets|"
     "batsman|batsmen|"
     "bullpen|"
     "strikeout|strikeouts|"
     "rbi|rbis|"
     "shutout|shutouts|"
     "birdie|birdies|bogey|bogeys|"
     "putt|putts|"
     "puck|"
     "hat trick|"
     "slam dunk|"
     "free throw|free throws|"
     "three pointer|"
     "home run|home runs|"
     "penalty shootout|"
     "red card|"
     "offside|"
     "test match|test matches|"
     "tie break|tiebreak|"
     "under par|over par|"
     "hole in one|"
     "batting average|"
     "wide receiver|"
     "running back|"
     "offensive line|defensive line|"
     "line of scrimmage|"
     "grand slam|"
     "gold medal|silver medal|bronze medal|"
     "doping|anti doping|"
     "wada|balco|"
     "fifa|uefa|fiba|iaaf|"
     "international olympic committee|ioc", _SPORT_CORE)
_add(SPORTS, 3.5,
     "coach|coaches|coaching|"
     "athletics|athletic|"
     "cycling|swimming|boxing|wrestling|"
     "skiing|snowboarding|"
     "marathon|rowing|sailing|"
     "martial arts|"
     "racing|racer|racers|"
     "sprinter|sprinters|"
     "swimmer|swimmers|"
     "cyclist|cyclists|"
     "gymnast|gymnasts|"
     "golfer|golfers|"
     "boxer|boxers|"
     "wrestler|wrestlers|"
     "striker|strikers|"
     "midfielder|midfielders|"
     "defender|defenders|"
     "footballer|footballers|"
     "referee|referees|"
     "umpire|umpires|"
     "league|leagues|"
     "champion|champions|"
     "finals|"
     "roster|"
     "medal|medals|"
     "scorer|scorers|"
     "batting|"
     "homer|homers|"
     "dugout|"
     "relegation|promoted club|"
     "rebound|rebounds|"
     "dunk|dunks|"
     "racquet|racket|"
     "penalties|"
     "overtime|"
     "tiebreaker|"
     "overs|"
     "decathlon|"
     "pole vault|high jump|long jump|"
     "shot put|"
     "steeplechase|"
     "rink|"
     "stadium|ballpark|"
     "transfer fee|loan deal|"
     "season opener|"
     "defending champion|"
     "match point|"
     "world record|"
     "personal best", _SPORT_CORE)
_add(SPORTS, 1.4,
     "sport|"
     "player|players|"
     "team|teams|"
     "match|matches|"
     "game|games|"
     "season|"
     "goal|goals|"
     "scored|scoring|"
     "opener|"
     "captain|"
     "club|clubs|"
     "fixture|fixtures|"
     "standings|"
     "seeded|unseeded|"
     "squad|"
     "sidelined|"
     "comeback|"
     "knockout|"
     "bat|batter|"
     "pitching|"
     "contest|"
     "runners|"
     "surfing|"
     "sparring|"
     "training camp|"
     "contract extension|"
     "free agent|free agency|"
     "transfer|transfers|"
     "starting lineup|"
     "steroids|steroid|"
     "atp")
_add(SPORTS, 0.65,
     "win|wins|winning|won|"
     "victory|victories|"
     "beat|beats|beaten|"
     "defeat|defeated|defeats|"
     "rival|rivals|"
     "final|"
     "fans|fan|"
     "cup|"
     "round|"
     "rally|"
     "race|"
     "score|scores|"
     "lead|"
     "defending|"
     "champ|"
     "traded")

_add(SPORTS, 7.0,
     "new york yankees|boston red sox|chicago white sox|"
     "los angeles dodgers|san francisco giants|"
     "san diego padres|"
     "new york mets|"
     "chicago cubs|"
     "st louis cardinals|"
     "houston astros|"
     "atlanta braves|"
     "philadelphia phillies|"
     "baltimore orioles|"
     "tampa bay rays|tampa bay devil rays|"
     "toronto blue jays|"
     "oakland athletics|"
     "seattle mariners|"
     "texas rangers|"
     "los angeles angels|anaheim angels|"
     "minnesota twins|"
     "detroit tigers|"
     "cleveland indians|cleveland guardians|"
     "kansas city royals|"
     "milwaukee brewers|"
     "pittsburgh pirates|"
     "cincinnati reds|"
     "colorado rockies|"
     "arizona diamondbacks|"
     "miami marlins|florida marlins|"
     "montreal expos|washington nationals|"
     "los angeles lakers|los angeles clippers|"
     "boston celtics|"
     "new york knicks|"
     "brooklyn nets|new jersey nets|"
     "philadelphia 76ers|"
     "toronto raptors|"
     "chicago bulls|"
     "cleveland cavaliers|"
     "detroit pistons|"
     "indiana pacers|"
     "milwaukee bucks|"
     "miami heat|"
     "orlando magic|"
     "atlanta hawks|"
     "washington wizards|"
     "charlotte hornets|charlotte bobcats|"
     "new orleans pelicans|new orleans hornets|"
     "dallas mavericks|"
     "houston rockets|"
     "san antonio spurs|"
     "denver nuggets|"
     "minnesota timberwolves|"
     "oklahoma city thunder|"
     "seattle supersonics|"
     "portland trail blazers|"
     "utah jazz|"
     "golden state warriors|"
     "sacramento kings|"
     "phoenix suns|"
     "memphis grizzlies|"
     "seattle storm|las vegas aces|"
     "new york liberty|indiana fever", _SPORT_ENTITIES)
_add(SPORTS, 7.0,
     "new england patriots|"
     "buffalo bills|"
     "miami dolphins|"
     "new york jets|"
     "new york giants|"
     "philadelphia eagles|"
     "dallas cowboys|"
     "washington commanders|washington redskins|"
     "pittsburgh steelers|"
     "baltimore ravens|"
     "cleveland browns|"
     "cincinnati bengals|"
     "green bay packers|"
     "chicago bears|"
     "detroit lions|"
     "minnesota vikings|"
     "indianapolis colts|"
     "houston texans|"
     "tennessee titans|"
     "jacksonville jaguars|"
     "new orleans saints|"
     "atlanta falcons|"
     "carolina panthers|"
     "tampa bay buccaneers|"
     "kansas city chiefs|"
     "denver broncos|"
     "las vegas raiders|oakland raiders|"
     "los angeles chargers|san diego chargers|"
     "san francisco 49ers|"
     "seattle seahawks|"
     "arizona cardinals|"
     "los angeles rams|st louis rams|"
     "toronto maple leafs|"
     "montreal canadiens|"
     "ottawa senators|"
     "vancouver canucks|"
     "edmonton oilers|"
     "calgary flames|"
     "winnipeg jets|"
     "boston bruins|"
     "new york rangers|new york islanders|"
     "new jersey devils|"
     "philadelphia flyers|"
     "pittsburgh penguins|"
     "washington capitals|"
     "detroit red wings|"
     "chicago blackhawks|"
     "colorado avalanche|"
     "dallas stars|"
     "st louis blues|"
     "tampa bay lightning|"
     "carolina hurricanes|"
     "florida panthers|"
     "buffalo sabres|"
     "columbus blue jackets|"
     "nashville predators|"
     "minnesota wild|"
     "san jose sharks|"
     "los angeles kings|"
     "anaheim ducks|"
     "vegas golden knights", _SPORT_ENTITIES)
_add(SPORTS, 6.5,
     "yankees|red sox|white sox|dodgers|mets|"
     "padres|astros|phillies|orioles|"
     "mariners|diamondbacks|marlins|expos|"
     "lakers|celtics|knicks|"
     "76ers|sixers|"
     "raptors|pistons|pacers|"
     "mavericks|"
     "timberwolves|"
     "trail blazers|"
     "supersonics|"
     "steelers|packers|"
     "49ers|"
     "seahawks|"
     "buccaneers|"
     "canadiens|canucks|"
     "oilers|"
     "bruins|"
     "blackhawks|"
     "red wings|"
     "maple leafs|"
     "sabres", _SPORT_ENTITIES)
_add(SPORTS, 7.0,
     "manchester united|manchester city|"
     "real madrid|atletico madrid|"
     "fc barcelona|"
     "bayern munich|bayern munchen|"
     "borussia dortmund|"
     "bayer leverkusen|"
     "paris saint germain|psg|"
     "ac milan|inter milan|internazionale|"
     "as roma|"
     "juventus|"
     "fiorentina|"
     "napoli|"
     "tottenham hotspur|tottenham|"
     "newcastle united|"
     "west ham|west brom|"
     "aston villa|"
     "blackburn rovers|"
     "bolton wanderers|"
     "wolverhampton wanderers|"
     "nottingham forest|"
     "leeds united|"
     "leicester city|"
     "sheffield united|sheffield wednesday|"
     "crystal palace|"
     "birmingham city|"
     "glasgow celtic|glasgow rangers|"
     "sporting lisbon|sporting cp|"
     "fc porto|"
     "psv eindhoven|"
     "ajax amsterdam|"
     "real sociedad|real betis|"
     "athletic bilbao|"
     "deportivo la coruna|"
     "olympique lyon|olympique marseille|"
     "boca juniors|river plate|"
     "la galaxy|inter miami|"
     "new york red bulls|"
     "dc united|"
     "seattle sounders|"
     "celtic fc|rangers fc|"
     "arsenal fc|chelsea fc|liverpool fc", _SPORT_ENTITIES)
_add(SPORTS, 4.2,
     "arsenal|chelsea|liverpool|everton|"
     "fulham|middlesbrough|"
     "sunderland|"
     "benfica|feyenoord|"
     "anderlecht|"
     "galatasaray|fenerbahce|"
     "besiktas|"
     "schalke|"
     "hertha berlin|"
     "werder bremen|"
     "villarreal|"
     "flamengo|palmeiras|"
     "corinthians|"
     "santos fc", _SPORT_ENTITIES)
_add(SPORTS, 7.0,
     "roger federer|rafael nadal|novak djokovic|"
     "serena williams|venus williams|"
     "andre agassi|pete sampras|"
     "andy roddick|lleyton hewitt|"
     "marat safin|"
     "maria sharapova|"
     "justine henin|kim clijsters|"
     "lindsay davenport|amelie mauresmo|"
     "andy murray|"
     "naomi osaka|iga swiatek|"
     "coco gauff|"
     "carlos alcaraz|jannik sinner|"
     "tiger woods|phil mickelson|"
     "ernie els|vijay singh|"
     "retief goosen|"
     "annika sorenstam|"
     "rory mcilroy|"
     "scottie scheffler|"
     "michael phelps|ian thorpe|"
     "katie ledecky|"
     "lance armstrong|jan ullrich|"
     "tadej pogacar|"
     "usain bolt|"
     "carl lewis|"
     "simone biles|"
     "michael schumacher|ralf schumacher|"
     "fernando alonso|kimi raikkonen|"
     "juan pablo montoya|"
     "lewis hamilton|max verstappen|"
     "valentino rossi|"
     "dale earnhardt|dale earnhardt jr|"
     "jeff gordon|jimmie johnson|"
     "tony stewart|"
     "michael jordan|"
     "lebron james|"
     "kobe bryant|"
     "shaquille o'neal|"
     "tim duncan|"
     "kevin garnett|"
     "allen iverson|"
     "yao ming|"
     "dwyane wade|"
     "carmelo anthony|"
     "stephen curry|steph curry|"
     "kevin durant|"
     "nikola jokic|luka doncic|"
     "giannis antetokounmpo|"
     "tom brady|"
     "peyton manning|eli manning|"
     "brett favre|"
     "patrick mahomes|"
     "aaron rodgers|"
     "barry bonds|"
     "sammy sosa|"
     "derek jeter|"
     "alex rodriguez|"
     "david ortiz|"
     "pedro martinez|"
     "roger clemens|"
     "randy johnson|"
     "curt schilling|"
     "ichiro suzuki|"
     "shohei ohtani|"
     "mike trout|"
     "wayne gretzky|"
     "mario lemieux|"
     "sidney crosby|"
     "alex ovechkin|"
     "connor mcdavid", _SPORT_ENTITIES)
_add(SPORTS, 6.8,
     "david beckham|wayne rooney|"
     "cristiano ronaldo|lionel messi|"
     "ronaldinho|zinedine zidane|"
     "thierry henry|patrick vieira|"
     "ruud van nistelrooy|"
     "michael owen|"
     "steven gerrard|frank lampard|"
     "didier drogba|"
     "andriy shevchenko|"
     "paolo maldini|"
     "roberto carlos|"
     "kylian mbappe|erling haaland|"
     "neymar|"
     "mohamed salah|"
     "harry kane|"
     "jude bellingham|"
     "jose mourinho|arsene wenger|"
     "alex ferguson|"
     "pep guardiola|jurgen klopp|"
     "carlo ancelotti|"
     "sachin tendulkar|"
     "brian lara|"
     "ricky ponting|"
     "shane warne|"
     "muttiah muralitharan|"
     "virat kohli|"
     "ms dhoni|m s dhoni|"
     "ben stokes|"
     "mike tyson|"
     "muhammad ali|"
     "floyd mayweather|"
     "manny pacquiao|"
     "lennox lewis|"
     "oscar de la hoya|"
     "conor mcgregor|"
     "ronda rousey|"
     "tyson fury|"
     "oleksandr usyk", _SPORT_ENTITIES)
_add(SPORTS, 4.5,
     "federer|nadal|djokovic|"
     "agassi|sampras|roddick|hewitt|"
     "sharapova|mauresmo|clijsters|"
     "mickelson|sorenstam|"
     "mcilroy|"
     "schumacher|raikkonen|"
     "verstappen|"
     "beckham|rooney|ronaldo|messi|"
     "ronaldinho|zidane|"
     "mourinho|wenger|"
     "guardiola|"
     "mbappe|haaland|"
     "tendulkar|"
     "pacquiao|"
     "mayweather", _SPORT_ENTITIES)

# Governments, international affairs, conflict, crime, and disasters.
_add(WORLD, 6.0,
     "election|elections|"
     "referendum|referendums|"
     "parliament|parliamentary|"
     "terrorism|terrorist|terrorists|"
     "insurgency|"
     "genocide|"
     "ceasefire|"
     "coup|"
     "hostage|hostages|"
     "kidnapping|kidnapped|"
     "assassination|assassinated|"
     "airstrike|airstrikes|"
     "air strike|air strikes|"
     "suicide bomber|suicide bombing|"
     "car bomb|car bombing|"
     "civil war|"
     "war crime|war crimes|"
     "ethnic cleansing|"
     "human rights|"
     "peace talks|peace deal|peace agreement|"
     "peacekeeping|peacekeepers")
_add(WORLD, 4.0,
     "politics|political|"
     "electoral|"
     "ballot|ballots|"
     "voters|voter|voting|"
     "legislature|legislators|"
     "senate|senator|senators|"
     "congress|congressional|"
     "diplomacy|diplomatic|diplomat|diplomats|"
     "ambassador|ambassadors|"
     "embassy|embassies|"
     "immigration|immigrant|immigrants|"
     "asylum|deportation|deported|"
     "refugee|refugees|"
     "insurgent|insurgents|"
     "militant|militants|"
     "rebels|rebel|"
     "militia|militias|"
     "troops|soldiers|"
     "military|"
     "invasion|invaded|"
     "occupation|"
     "bombing|bombings|"
     "bomb|bombs|"
     "missile|missiles|"
     "artillery|"
     "shelling|"
     "gunfire|"
     "gunman|gunmen|"
     "guerilla|guerrilla|guerrillas|"
     "terror|"
     "protesters|protestor|protestors|"
     "demonstrators|"
     "riot|riots|"
     "unrest|"
     "clashes|"
     "massacre|"
     "apartheid|"
     "separatist|separatists|"
     "nationalist|nationalists|"
     "constitution|constitutional|"
     "impeachment|"
     "democracy|democratic reform|"
     "dictator|dictatorship|"
     "ruling party|opposition party")
_add(WORLD, 2.4,
     "president|presidential|"
     "minister|ministers|"
     "premier|"
     "government|governments|"
     "cabinet|"
     "governor|"
     "mayor|"
     "politician|politicians|"
     "campaign|campaigning|"
     "candidate|candidates|"
     "vote|votes|"
     "polls|"
     "legislation|"
     "lawmakers|lawmaker|"
     "legislative|"
     "republican|republicans|"
     "democrat|democrats|"
     "conservative|conservatives|"
     "liberal|liberals|"
     "labour party|labor party|"
     "democratic party|republican party|"
     "diplomatic relations|"
     "sanctions|"
     "embargo|"
     "border|borders|"
     "protest|protests|"
     "marchers|"
     "activist|activists|"
     "war|wars|warfare|"
     "conflict|conflicts|"
     "army|navy|"
     "battle|battles|"
     "combat|"
     "weapons|weapon|"
     "nuclear|"
     "defense ministry|defence ministry|"
     "air force|"
     "pentagon|"
     "national security|"
     "intelligence agency|"
     "cia|fbi|"
     "detainee|detainees|"
     "detained|"
     "interrogation|"
     "torture|"
     "disarmament|"
     "humanitarian|"
     "aid workers|"
     "sovereignty|"
     "independence|"
     "peace|"
     "bilateral|"
     "multilateral")
_add(WORLD, 1.0,
     "federal|"
     "official|officials|"
     "authorities|"
     "opposition|"
     "leadership|"
     "summit|"
     "negotiations|"
     "talks|"
     "treaty|"
     "reform|reforms|"
     "public policy|"
     "demonstration|demonstrations|"
     "attack|attacks|attacked|"
     "strike|strikes|"
     "security|"
     "crisis|"
     "religion|religious|"
     "church|"
     "mosque|"
     "cleric|clerics|"
     "pope|vatican|"
     "pilgrims|pilgrimage|"
     "catholic|islamic|"
     "school|schools|"
     "education|"
     "teacher|teachers|"
     "students|"
     "campus")
_add(WORLD, 6.0,
     "white house|"
     "prime minister|"
     "foreign minister|"
     "foreign ministry|"
     "foreign secretary|"
     "secretary of state|"
     "united nations|"
     "un security council|security council|"
     "general assembly|"
     "nato|"
     "african union|"
     "arab league|"
     "league of nations|"
     "european parliament|"
     "european council|"
     "european union summit|"
     "state department|"
     "department of state|"
     "house of representatives|"
     "house of commons|"
     "downing street|"
     "peace process|"
     "middle east|"
     "west bank|gaza strip|"
     "nuclear weapons|nuclear weapon|"
     "nuclear program|nuclear programme|"
     "nuclear talks|"
     "weapons of mass destruction|"
     "arms embargo|"
     "ballistic missile|ballistic missiles|"
     "chemical weapons|"
     "biological weapons|"
     "terror attack|terror attacks|"
     "terrorist attack|terrorist attacks|"
     "september 11|9/11|"
     "war on terror|"
     "islamic state|"
     "al qaeda|al qaida|"
     "taliban|"
     "hamas|hezbollah|hizbollah|"
     "houthi|houthis|"
     "boko haram|"
     "irish republican army|"
     "iraqi insurgents|"
     "abu ghraib|"
     "guantanamo|"
     "climate summit|"
     "climate treaty|"
     "paris climate agreement")
_add(WORLD, 3.3,
     "european union|"
     "european commission|"
     "brussels summit|"
     "commonwealth summit|"
     "g7 summit|g8 summit|g20 summit|"
     "amnesty international|"
     "human rights watch|"
     "international criminal court|"
     "red cross|red crescent|"
     "peace corps|"
     "sinn fein|"
     "likud|"
     "fatah|"
     "bjp|bharatiya janata party|"
     "african national congress|"
     "communist party|"
     "kremlin|"
     "knesset|"
     "bundestag|"
     "elysee")

_add(WORLD, 5.3,
     "murder|murdered|homicide|"
     "rape|raped|"
     "robbery|robberies|"
     "kidnap|"
     "shooting|shootings|"
     "stabbing|stabbed|"
     "arson|"
     "manslaughter|"
     "mass shooting|"
     "serial killer|"
     "bank robbery|"
     "armed robbery|"
     "human trafficking|"
     "drug trafficking|"
     "drug cartel|drug cartels|"
     "sex trafficking|"
     "child abuse|"
     "domestic violence", _VIOLENCE)
_add(WORLD, 3.5,
     "police|"
     "arrest|arrests|arrested|"
     "prison|prisons|"
     "jail|jailed|"
     "criminal|criminals|"
     "crime|crimes|"
     "fugitive|fugitives|"
     "suspect|suspects|"
     "gang|gangs|"
     "gangster|"
     "smuggling|smuggler|"
     "cocaine|heroin|methamphetamine|"
     "killed|"
     "wounded|"
     "slain|"
     "fatal|"
     "fatalities|"
     "casualties|"
     "dead|"
     "death toll", _VIOLENCE)
_add(WORLD, 2.5,
     "court|courts|"
     "judge|judges|"
     "judicial|judiciary|"
     "prosecutor|prosecutors|"
     "prosecution|"
     "defendant|defendants|"
     "jury|"
     "indicted|indictment|"
     "convicted|conviction|"
     "verdict|"
     "sentenced|sentencing|"
     "acquitted|acquittal|"
     "bail|"
     "litigation|"
     "injunction|"
     "lawsuit|lawsuits|"
     "sued|"
     "appeal court|appeals court|"
     "court ruling|"
     "legal battle|"
     "criminal trial", _LEGAL)
_add(WORLD, 1.3,
     "trial|trials|"
     "ruling|"
     "appeal|appeals|"
     "law|laws|"
     "lawyer|lawyers|"
     "attorney|attorneys|"
     "settlement|"
     "fraud|"
     "investigation|investigators|"
     "corruption|"
     "bribery|"
     "charges|charged|"
     "antitrust|"
     "regulators|regulation", _LEGAL)
_add(WORLD, 6.0,
     "supreme court|"
     "constitutional court|"
     "international court of justice|"
     "war crimes tribunal|"
     "death penalty|capital punishment|"
     "death sentence|"
     "life imprisonment|"
     "prison sentence")
_add(BUSINESS, 1.5,
     "antitrust|regulators|regulation|"
     "settlement|lawsuit|lawsuits|fraud")

_add(WORLD, 6.0,
     "earthquake|earthquakes|"
     "tsunami|tsunamis|"
     "hurricane|"
     "typhoon|typhoons|"
     "tornado|tornadoes|tornados|"
     "wildfire|wildfires|"
     "forest fire|forest fires|"
     "bushfire|bushfires|"
     "mudslide|mudslides|"
     "landslide|landslides|"
     "avalanche|"
     "flooding|floods|"
     "volcanic eruption|"
     "plane crash|plane crashes|"
     "airliner crash|"
     "jet crash|jet crashes|"
     "helicopter crash|"
     "train crash|train derailment|"
     "ferry disaster|ferry sinking|"
     "building collapse|"
     "dam collapse|dam burst|"
     "mine collapse|"
     "industrial explosion|"
     "mass evacuation", _DISASTERS)
_add(WORLD, 3.6,
     "disaster|disasters|"
     "flood|"
     "drought|droughts|"
     "famine|"
     "cyclone|cyclones|"
     "blizzard|blizzards|"
     "heatwave|heat wave|"
     "volcano|"
     "eruption|"
     "aftershock|aftershocks|"
     "evacuate|evacuated|evacuation|evacuations|"
     "rescuers|rescue workers|"
     "derailed|derailment|"
     "shipwreck|"
     "capsized|"
     "explosion|explosions|"
     "blackout|blackouts|"
     "power outage|power outages", _DISASTERS)
_add(WORLD, 1.8,
     "storm|storms|hurricanes|"
     "weather|"
     "torrential rain|heavy rain|"
     "fatal accident|"
     "crash|crashed|crashes|"
     "rescue|rescued|"
     "emergency|"
     "death|deaths|"
     "injured|injuries|"
     "missing|"
     "survivors|"
     "outbreak|outbreaks|"
     "epidemic|epidemics|"
     "pandemic|"
     "quarantine|"
     "lockdown|"
     "public health emergency|"
     "disease outbreak|"
     "aid agencies|"
     "humanitarian aid")
_add(WORLD, 4.8,
     "george bush|george w bush|george w. bush|"
     "george h w bush|"
     "dick cheney|"
     "john kerry|"
     "john edwards|"
     "barack obama|"
     "joe biden|"
     "donald trump|"
     "kamala harris|"
     "hillary clinton|bill clinton|"
     "nancy pelosi|"
     "bernie sanders|"
     "ron desantis|"
     "mitch mcconnell|"
     "john mccain|"
     "condoleezza rice|"
     "colin powell|"
     "donald rumsfeld|"
     "tony blair|"
     "gordon brown|"
     "david cameron|"
     "boris johnson|"
     "rishi sunak|"
     "keir starmer|"
     "vladimir putin|"
     "dmitry medvedev|"
     "volodymyr zelensky|volodymyr zelenskyy|"
     "jacques chirac|"
     "gerhard schroeder|gerhard schroder|"
     "angela merkel|olaf scholz|"
     "emmanuel macron|"
     "silvio berlusconi|giorgia meloni|"
     "jose luis rodriguez zapatero|"
     "pedro sanchez|"
     "benjamin netanyahu|"
     "ariel sharon|"
     "yasser arafat|"
     "mahmoud abbas|"
     "ehud olmert|"
     "saddam hussein|"
     "ayatollah khamenei|"
     "ali khamenei|"
     "hassan rouhani|"
     "hosni mubarak|"
     "muammar gaddafi|"
     "bashar assad|bashar al assad|"
     "recep tayyip erdogan|"
     "osama bin laden|"
     "kofi annan|ban ki moon|antonio guterres|"
     "hu jintao|jiang zemin|wen jiabao|"
     "xi jinping|"
     "junichiro koizumi|shinzo abe|"
     "kim jong il|kim jong un|"
     "roh moo hyun|"
     "pervez musharraf|"
     "hamid karzai|"
     "manmohan singh|"
     "sonia gandhi|"
     "narendra modi|"
     "atal bihari vajpayee|"
     "john howard|"
     "justin trudeau|"
     "nelson mandela|thabo mbeki|"
     "robert mugabe|"
     "hugo chavez|"
     "fidel castro|"
     "lula da silva|"
     "jair bolsonaro|"
     "javier milei|"
     "geraldo alckmin|"
     "dalai lama")
_add(WORLD, 2.8,
     "bush|kerry|cheney|"
     "obama|biden|trump|"
     "clinton|"
     "blair|"
     "putin|"
     "zelensky|zelenskyy|"
     "chirac|"
     "schroeder|"
     "merkel|macron|"
     "berlusconi|"
     "netanyahu|"
     "arafat|"
     "musharraf|karzai|"
     "mubarak|"
     "gaddafi|"
     "erdogan|"
     "mugabe|"
     "bin laden|"
     "saddam|"
     "khamenei|"
     "ayatollah")
_add(WORLD, 1.4,
     "iraq|iraqi|"
     "afghanistan|afghan|"
     "palestinian|palestinians|palestine|"
     "israeli|israel|"
     "gaza|"
     "darfur|"
     "chechnya|chechen|"
     "kashmir|"
     "north korea|north korean|"
     "ukraine|ukrainian|"
     "syria|syrian|"
     "yemen|yemeni|"
     "baghdad|kabul|"
     "fallujah|najaf|"
     "beirut|jerusalem")
_add(WORLD, 0.35,
     "china|chinese|"
     "russia|russian|"
     "iran|iranian|"
     "pakistan|pakistani|"
     "india|indian|"
     "france|french|"
     "germany|german|"
     "britain|british|"
     "japan|japanese|"
     "korea|korean|"
     "indonesia|indonesian|"
     "taiwan|taiwanese|"
     "thailand|thai|"
     "philippines|"
     "venezuela|cuba|"
     "mexico|mexican|"
     "brazil|brazilian|"
     "nigeria|nigerian|"
     "sudan|sudanese|"
     "somalia|somali|"
     "congo|congolese|"
     "egypt|egyptian|"
     "saudi arabia|"
     "turkey|turkish|"
     "lebanon|lebanese")

# Context-sensitive company names.
_add(BUSINESS, 5.7, "target|shell|bp", _BUSINESS_ENTITIES)

_MAX_WORDS = max(len(term.split()) for term in _LEXICON)
_START_LENGTHS = {}
for _term in _LEXICON:
    _words = _term.split()
    _START_LENGTHS.setdefault(_words[0], set()).add(len(_words))
for _term in list(_START_LENGTHS):
    _START_LENGTHS[_term] = tuple(sorted(_START_LENGTHS[_term]))

_AMBIGUOUS_TEAMS = {
    "giants", "eagles", "bears", "lions", "tigers", "rangers",
    "kings", "blues", "reds", "heat", "magic", "thunder", "lightning",
    "hurricanes", "avalanche", "wild", "stars", "capitals", "senators",
    "nationals", "jets", "saints", "cardinals", "panthers", "titans",
    "jaguars", "falcons", "ravens", "rockets", "warriors", "suns",
    "hawks", "nets", "bulls", "bucks", "cubs", "pirates", "twins",
    "royals", "angels", "rays", "guardians", "brewers", "braves",
    "cowboys", "patriots", "dolphins", "browns", "bengals", "vikings",
    "colts", "texans", "chiefs", "broncos", "raiders", "chargers",
    "rams", "penguins", "devils", "islanders", "ducks", "flames",
    "sharks", "predators", "spurs", "cavaliers", "grizzlies",
    "nuggets", "jazz", "clippers",
}

_SPORT_WEAK = {
    "player", "players", "team", "teams", "match", "matches",
    "game", "games", "season", "goal", "goals", "fans", "fan",
    "round", "race", "rally", "win", "wins", "winning", "won",
    "victory", "victories", "beat", "beats", "final", "cup",
    "score", "scores", "lead", "defending", "traded", "transfer",
    "transfers", "contract extension",
}

_METADATA_KEYS = {
    "id", "index", "label", "labels", "answer", "answers", "category",
    "categories", "output", "expected", "prediction", "source",
    "url", "link", "date", "time", "timestamp", "author", "byline",
    "language", "lang", "question", "question_name", "question_id",
    "instructions", "criteria", "options", "choices", "output_schema",
}
_TITLE_KEYS = {"title", "headline", "heading", "news_title", "article_title"}
_CONTENT_KEYS = {
    "text", "body", "content", "article", "document", "news",
    "story", "passage", "sentence", "summary", "description",
    "subtitle", "subheading", "abstract", "deck", "message",
    "news_text", "article_text", "full_text", "fulltext",
    "article_body", "news_content", "snippet",
}
_WRAPPER_KEYS = {
    "input", "data", "state", "payload", "instance", "item",
    "sample", "record", "value",
}


def _extract_parts(state):
    parts = []
    seen = set()

    def add(value, title=False):
        if not isinstance(value, str):
            return
        value = value.strip()
        if not value or value in seen:
            return
        seen.add(value)
        parts.append((value, title))

    def walk(value, title=False, depth=0):
        if depth > 12:
            return
        if isinstance(value, str):
            add(value, title)
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                walk(item, title, depth + 1)
            return
        if not isinstance(value, dict):
            return
        keyed = {}
        for key, item in value.items():
            if isinstance(key, str):
                normalized_key = key.strip().lower().replace("-", "_")
                keyed[normalized_key] = item
        used = set()
        for key in keyed:
            if key in _TITLE_KEYS:
                walk(keyed[key], True, depth + 1)
                used.add(key)
        for key in keyed:
            if key in _CONTENT_KEYS:
                walk(keyed[key], False, depth + 1)
                used.add(key)
        for key in keyed:
            if key in _WRAPPER_KEYS:
                walk(keyed[key], False, depth + 1)
                used.add(key)
        if not used:
            for key, item in keyed.items():
                if key not in _METADATA_KEYS:
                    walk(item, title, depth + 1)

    walk(state)
    result = []
    has_title = any(title for _, title in parts)
    for text, title in parts:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if (
            not has_title and not title and len(lines) > 1
            and 3 <= len(lines[0].split()) <= 28
            and len(lines[0]) <= 200
        ):
            result.append((lines[0], True))
            result.append(("\n".join(lines[1:]), False))
            has_title = True
        else:
            result.append((text, title))
    return result


def _has(text, terms):
    padded = " " + text + " "
    return any(" " + term + " " in padded for term in terms)


def _scan(parts):
    found = {}
    tokens = []
    raw_parts = []
    normalized_parts = []
    title_parts = []

    for raw, is_title in parts:
        normalized = _normalize(raw)
        words = normalized.split()
        if not words:
            continue
        raw_parts.append(raw)
        normalized_parts.append(normalized)
        if is_title:
            title_parts.append(normalized)
        offset = len(tokens)
        tokens.extend(words)
        for i, word in enumerate(words):
            lengths = _START_LENGTHS.get(word)
            if not lengths:
                continue
            if is_title:
                quality = 1.50
            elif i < 32:
                quality = 1.22
            elif i < 100:
                quality = 1.06
            elif i < 350:
                quality = 0.85
            else:
                quality = 0.65
            for length in lengths:
                if i + length > len(words):
                    continue
                term = " ".join(words[i:i + length])
                if term not in _LEXICON:
                    continue
                position = offset + i
                if term in found:
                    entry = found[term]
                    entry[1] = max(entry[1], quality)
                    entry[2] += 1
                else:
                    found[term] = [position, quality, 1]
    return (
        found, tokens, " ".join(normalized_parts),
        "\n".join(raw_parts), " ".join(title_parts),
    )


def _disambiguate(found, tokens, text, raw):
    words = set(tokens)

    def drop(term):
        found.pop(term, None)

    apple_nature = {
        "orchard", "orchards", "cider", "apples", "fruit", "fruits",
        "growers", "harvest", "juice", "pesticide", "pesticides",
    }
    apple_tech = {
        "iphone", "ipad", "ipod", "macbook", "macintosh", "imac",
        "ios", "itunes", "airpods", "cupertino",
    }
    if words & apple_nature and not words & apple_tech:
        if not _has(text, ("tim cook", "steve jobs", "apple inc", "apple computer")):
            drop("apple")

    amazon_nature = {
        "rainforest", "rainforests", "amazonian", "tributary",
        "tributaries", "jungle", "deforestation", "basin",
    }
    amazon_commerce = {
        "bezos", "aws", "ecommerce", "kindle", "retailer",
        "retailing", "alexa", "jassy",
    }
    if words & amazon_nature or _has(text, ("amazon river",)):
        if not words & amazon_commerce and not _has(
            text, ("amazon com", "amazon web services", "e commerce")
        ):
            drop("amazon")

    if _has(text, ("meta analysis", "meta analyses", "meta analytic")):
        if not words & {"facebook", "zuckerberg", "instagram", "whatsapp", "metaverse"}:
            drop("meta")
    if "alphabet" in found:
        if not words & {
            "google", "earnings", "shares", "stock", "revenue", "profits",
            "ceo", "company", "antitrust", "search", "technology",
        }:
            drop("alphabet")

    if "oracle" in found and words & {"delphi", "mythology", "ancient", "prophecy"}:
        if not words & {"software", "database", "ellison", "shares", "earnings"}:
            drop("oracle")

    if "zoom" in found and not words & {
        "video", "videoconferencing", "meeting", "meetings", "conference",
        "conferencing", "software", "earnings", "shares", "revenue", "app",
    }:
        drop("zoom")

    if "sprint" in found:
        telecom = words & {
            "telecom", "telecommunications", "nextel", "wireless", "phone",
            "phones", "mobile", "cellular", "verizon", "merger", "carrier",
            "subscribers", "broadband",
        }
        if not telecom:
            drop("sprint")

    if "palm" in found and not words & {
        "treo", "pda", "pdas", "handheld", "handhelds", "palmone",
        "palmsource", "phone", "smartphone", "software", "computers",
    } and not _has(text, ("palm pilot", "palm inc")):
        drop("palm")

    if "gateway" in found and not words & {
        "computer", "computers", "pc", "pcs", "laptop", "desktops",
        "dell", "hewlett", "emachines",
    } and not _has(text, ("gateway inc", "gateway computer")):
        drop("gateway")

    if "orange" in found:
        telecom = words & {
            "telecom", "telecommunications", "wireless", "mobile", "phones",
            "broadband", "subscribers", "handset", "telefonica", "vodafone",
        }
        if not telecom and not _has(text, ("orange sa", "orange telecom")):
            drop("orange")

    if "sharp" in found and not words & {
        "electronics", "electronic", "lcd", "oled", "televisions",
        "tv", "displays", "panel", "panels", "foxconn",
    } and not _has(text, ("sharp corp", "sharp corporation")):
        drop("sharp")

    if "arm" in found:
        chip_context = words & {
            "chip", "chips", "chipmaker", "processor", "processors",
            "semiconductor", "semiconductors", "nvidia", "softbank",
        }
        corporate_caps = bool(re.search(r"\bARM\b", raw)) and bool(
            words & {"shares", "stock", "earnings", "revenue", "ipo", "acquisition"}
        )
        if not chip_context and not corporate_caps and not _has(text, ("arm holdings",)):
            drop("arm")

    if "target" in found:
        retail = words & {
            "retail", "retailer", "retailers", "stores", "shopping",
            "walmart", "costco", "merchandise", "shopper", "shoppers",
        }
        if not retail and not _has(text, ("target corp", "target corporation")):
            drop("target")
    if "shell" in found:
        oil_company = words & {
            "oil", "crude", "petroleum", "refinery", "refineries",
            "earnings", "dividend", "profits", "shareholders", "lng",
        }
        if not oil_company and not _has(text, ("royal dutch", "shell plc")):
            drop("shell")
    if "bp" in found and not words & {
        "oil", "crude", "petroleum", "energy", "refinery", "spill",
        "profits", "earnings", "shares", "dividend", "gas",
    }:
        drop("bp")

    if _has(text, ("gerald ford", "harrison ford", "ford foundation")):
        if not words & {"automaker", "cars", "vehicles", "motor"}:
            drop("ford")
    if _has(text, ("land rover", "range rover")):
        if not words & {"mars", "lunar", "nasa", "planet", "spacecraft"}:
            drop("rover")
    if "mars" in found and (
        _has(text, ("mars inc", "mars incorporated", "mars candy"))
        or words & {"snickers", "confectionery", "confectioner"}
    ):
        if not words & {"nasa", "planet", "rover", "space", "mission"}:
            drop("mars")
    if _has(text, ("arab league", "league of nations")):
        if not words & {"football", "soccer", "basketball", "baseball", "champions"}:
            drop("league")
    if _has(text, ("coach inc", "coach handbags", "coach bags")):
        if not words & {"team", "football", "basketball", "players"}:
            drop("coach")
    if _has(text, ("price war", "bidding war", "browser war", "console war", "trade war")):
        if not words & {
            "troops", "soldiers", "military", "invasion", "killed", "missile",
            "bombing", "insurgents", "ceasefire",
        }:
            drop("war")
    if _has(text, ("heart attack", "heart attacks", "cyber attack", "cyber attacks")):
        if not words & {"militants", "terrorists", "troops", "bomb", "gunman"}:
            drop("attack")
            drop("attacks")
    if _has(text, ("clinical trial", "clinical trials", "randomized trial")):
        if not words & {"judge", "court", "prosecutor", "defendant", "jury"}:
            drop("trial")
            drop("trials")
    if _has(text, ("carolina hurricanes", "colorado avalanche", "seattle storm")):
        drop("hurricanes")
        drop("avalanche")
        drop("storm")

    if "windows" in found and not words & {
        "microsoft", "software", "computer", "computers", "pc",
        "pcs", "linux", "xp", "vista", "browser", "server", "operating",
    }:
        if words & {"shattered", "broken", "building", "bomb", "glass", "house"}:
            drop("windows")


def _quality(entry):
    return entry[1] + min(4, entry[2] - 1) * 0.07


def _sum_marked(found, marker, category):
    return sum(
        _LEXICON[term][category] * _quality(entry)
        for term, entry in found.items()
        if term in marker
    )


def _first(found, marker, default=1000000):
    return min(
        (entry[0] for term, entry in found.items() if term in marker),
        default=default,
    )


def _mark_count(found, marker):
    return sum(1 for term in found if term in marker)


def predict(state):
    parts = _extract_parts(state)
    if not parts:
        return {"answer": "world"}

    found, tokens, text, raw, title = _scan(parts)
    if not tokens:
        return {"answer": "world"}
    _disambiguate(found, tokens, text, raw)

    words = set(tokens)
    scores = [0.0, 0.0, 0.0, 0.0]
    tech_core = _sum_marked(found, _TECH_CORE, SCI_TECH)
    science = _sum_marked(found, _SCIENCE_CORE, SCI_TECH)
    research = _sum_marked(found, _RESEARCH, SCI_TECH)
    sport_core = _sum_marked(found, _SPORT_CORE, SPORTS)
    sport_entities = _sum_marked(found, _SPORT_ENTITIES, SPORTS)
    gaming = _sum_marked(found, _GAMING, SCI_TECH)
    finance = _sum_marked(found, _FINANCE, BUSINESS)
    corporate = _sum_marked(found, _CORPORATE, BUSINESS)
    legal = _sum_marked(found, _LEGAL, WORLD)
    violence = _sum_marked(found, _VIOLENCE, WORLD)
    disasters = _sum_marked(found, _DISASTERS, WORLD)

    technical_context = tech_core + science + research + gaming
    for term, entry in found.items():
        weights = _LEXICON[term]
        quality = _quality(entry)
        for category in range(4):
            contribution = weights[category] * quality
            if category == SPORTS and term in _SPORT_WEAK:
                if technical_context >= 10 and sport_core + sport_entities < 8:
                    contribution *= 0.22
            scores[category] += contribution

    # Team nicknames only become strong sporting evidence in a sporting context.
    ambiguous_teams = words & _AMBIGUOUS_TEAMS
    if ambiguous_teams:
        sports_actions = words & {
            "beat", "beats", "defeat", "defeated", "defeats", "win", "wins",
            "won", "coach", "coaches", "scored", "scoring", "playoff",
            "playoffs", "championship", "roster", "quarterback", "pitcher",
            "inning", "innings", "goal", "goals", "touchdown", "vs",
            "versus", "overtime", "sign", "signs", "traded",
        }
        real_sport = sport_core + sport_entities >= 5
        if real_sport or (
            sports_actions and not (technical_context > 15 and sport_core < 3)
        ):
            scores[SPORTS] += min(15.0, 4.5 * len(ambiguous_teams))
            sport_entities += min(12.0, 4.0 * len(ambiguous_teams))

    # Numeric scores, especially successive tennis-set scores.
    score_patterns = re.findall(r"\b(\d{1,3})\s*[-–]\s*(\d{1,3})\b", raw)
    plausible_scores = [
        (int(a), int(b)) for a, b in score_patterns
        if int(a) <= 160 and int(b) <= 160
    ]
    if plausible_scores:
        voting_context = words & {
            "vote", "votes", "voted", "senate", "parliament", "referendum",
            "ballot", "election", "supreme",
        }
        if not voting_context:
            if sport_core + sport_entities >= 3 or words & {
                "match", "game", "won", "beat", "defeated", "victory", "win",
            }:
                scores[SPORTS] += min(9.0, 3.5 * len(plausible_scores))
            if sum(1 for a, b in plausible_scores if 0 <= a <= 7 and 0 <= b <= 7) >= 2:
                scores[SPORTS] += 6.0

    tech_first = _first(found, _TECH_ENTITIES)
    business_first = _first(found, _BUSINESS_ENTITIES)
    sport_first = _first(found, _SPORT_ENTITIES)
    tech_entities = _sum_marked(found, _TECH_ENTITIES, SCI_TECH)
    market_first = _first(found, _MARKETS)
    market_count = _mark_count(found, _MARKETS)
    financial_first = _first(found, _FINANCE)
    research_first = _first(found, _RESEARCH)
    disaster_first = _first(found, _DISASTERS)
    gaming_first = _first(found, _GAMING)

    lead = " ".join(tokens[:70])
    focus = title if title else " ".join(tokens[:30])

    # A market roundup remains business even if Intel or Microsoft is mentioned.
    generic_market_match = re.search(
        r"\b(?:stocks|equities|stock markets|stock market|wall street|"
        r"dow jones|dow|nasdaq composite|s p 500|"
        r"asian shares|european shares|japanese shares|global markets|"
        r"global shares|us stocks|oil prices|crude oil prices)\b",
        " ".join(tokens[:50]),
    )
    generic_market_position = 1000000
    if generic_market_match:
        generic_market_position = len(
            " ".join(tokens[:50])[:generic_market_match.start()].split()
        )
    market_roundup = (
        generic_market_position < 28
        and generic_market_position <= tech_first
    )
    if market_first < 28 and market_first < tech_first and finance >= 5:
        market_roundup = True
    if market_count >= 3 and tech_first > 35 and finance > technical_context:
        market_roundup = True
    if market_roundup:
        scores[BUSINESS] += 5.0 + min(9.0, tech_entities * 0.35)
        scores[SCI_TECH] -= tech_entities * 0.35

    # The category of a technology company does not change merely because the
    # story concerns its earnings, acquisition, antitrust case, or other lawsuit.
    relevant_tech_entity = (
        tech_first < 55
        or (tech_first < 120 and _mark_count(found, _TECH_ENTITIES) >= 2)
        or (tech_first < 180 and tech_core >= 12)
    )
    if tech_entities > 0 and relevant_tech_entity and not market_roundup:
        if corporate >= 3 or finance >= 5 or tech_core >= 4 or legal >= 3:
            relevance = 1.00 if tech_first < 32 else 0.83
            if business_first + 18 < tech_first and tech_core < 7:
                relevance *= 0.60
            scores[SCI_TECH] += scores[BUSINESS] * relevance
            if violence < 18:
                scores[SCI_TECH] += legal * 0.95
            else:
                scores[SCI_TECH] += legal * 0.35

    # Ordinary corporate litigation and accounting cases remain business.
    if business_first < 55 and legal >= 3 and tech_entities == 0:
        corporate_legal = _has(text, (
            "accounting fraud", "accounting scandal", "securities fraud",
            "insider trading", "class action", "antitrust", "shareholders",
            "lawsuit", "lawsuits", "bankruptcy", "settlement",
        ))
        if corporate_legal and violence < 10:
            scores[BUSINESS] += legal * 0.85

    # Contracts, team sales, labor disputes, and doping are sporting topics.
    if sport_entities >= 5:
        sport_relevant = sport_first < 60 or (
            ambiguous_teams and sport_core >= 5
        )
        if sport_relevant:
            if corporate >= 4 or _has(text, (
                "transfer fee", "contract extension", "free agent",
                "salary cap", "collective bargaining", "team owner",
                "club owner", "buys club", "buys team",
            )):
                scores[SPORTS] += scores[BUSINESS] * 0.82
            if legal >= 3 and (sport_core >= 3 or sport_first < 30):
                scores[SPORTS] += min(16.0, legal * 0.65)

    # Names such as FIFA and NBA inside a game product name do not turn a
    # software announcement into a report about a real match.
    if gaming >= 6 and gaming_first < 65:
        game_product_focus = _has(text, (
            "video game", "video games", "computer game", "computer games",
            "playstation", "xbox", "nintendo", "ea sports", "nba 2k",
            "electronic arts", "gameplay", "game developer", "game console",
            "madden nfl", "fifa 23", "fifa 24",
        ))
        if game_product_focus:
            scores[SCI_TECH] += min(45.0, scores[SPORTS] * 0.75)

    # Research on a disease or a natural hazard is distinguished from a report
    # on casualties, evacuation, or an ongoing emergency.
    if research >= 6 and science >= 4:
        scores[SCI_TECH] += 5.0
    research_disaster = (
        research_first < 30 and research >= 6 and violence < 8
        and _has(text, (
            "study", "research", "scientists", "researchers", "geologists",
            "climate model", "predict", "prediction", "discovered",
        ))
    )
    finance_in_focus = _has(focus, (
        "earnings", "profit", "profits", "revenue", "shares", "stocks",
        "oil prices", "oil price", "crude prices", "gas prices",
        "insurance", "insurers", "stock market", "economy",
        "economic impact", "economic growth", "costs", "losses",
    ))
    if disasters >= 5 and disaster_first < 65:
        obvious_sports_event = sport_core + sport_entities >= 15
        space_test = (
            _has(text, ("spacex", "nasa", "blue origin", "rocket lab"))
            and words & {"test", "testing", "flight", "launch", "prototype"}
        )
        if not research_disaster and not obvious_sports_event and not space_test:
            if not finance_in_focus or violence >= 12:
                scores[WORLD] += 6.0 + min(7.0, scores[BUSINESS] * 0.25)
        elif research_disaster:
            scores[SCI_TECH] += 5.0

    # Strong criminal-event phrases override incidental references to banks,
    # stores, airlines, or other businesses.
    if _has(lead, (
        "bank robbery", "armed robbery", "mass shooting", "serial killer",
        "human trafficking", "drug cartel", "drug trafficking",
    )):
        scores[WORLD] += 8.0

    # Cryptocurrency price and investment reports are financial news; protocol
    # development and cryptographic technology are handled by the tech lexicon.
    if words & {"bitcoin", "ethereum", "cryptocurrency", "cryptocurrencies", "crypto"}:
        if _has(focus, (
            "price", "prices", "rallies", "rally", "surges", "surge",
            "plunges", "slumps", "record high", "record highs",
            "etf", "etfs", "trading", "investors", "market",
        )):
            scores[BUSINESS] += 8.0
        if _has(text, (
            "blockchain technology", "software upgrade", "protocol upgrade",
            "cryptographic", "decentralized application", "smart contract",
        )):
            scores[SCI_TECH] += 7.0

    # Public-health emergencies are world events unless research or treatment
    # development is the central subject.
    epidemic = words & {
        "outbreak", "outbreaks", "epidemic", "pandemic", "quarantine", "lockdown",
    }
    if epidemic and research < 6:
        if words & {"killed", "dead", "deaths", "emergency", "government", "borders"}:
            scores[WORLD] += 5.0
        if _has(text, (
            "develops vaccine", "new vaccine", "vaccine trial",
            "experimental vaccine", "clinical trial",
        )):
            scores[SCI_TECH] += 6.0

    # Explicit sector phrases help terse headlines with very few named entities.
    if _has(text, (
        "internet company", "technology company", "technology companies",
        "tech company", "tech companies", "software company",
        "chip maker", "chip makers", "mobile operator", "telecom operator",
    )):
        scores[SCI_TECH] += 7.0
        if not market_roundup and corporate >= 3:
            scores[SCI_TECH] += scores[BUSINESS] * 0.65

    if _has(text, (
        "football club", "soccer club", "baseball team", "basketball team",
        "tennis player", "golf tournament", "cricket team", "rugby team",
    )):
        scores[SPORTS] += 5.0

    # With no substantive evidence, general news belongs in the residual class.
    if max(scores) < 1.5:
        return {"answer": "world"}

    # Stable tie-breaking favors the residual class only for exact ties.
    priority = {WORLD: 3, SPORTS: 2, SCI_TECH: 1, BUSINESS: 0}
    winner = max(range(4), key=lambda category: (scores[category], priority[category]))
    return {"answer": _LABELS[winner]}
