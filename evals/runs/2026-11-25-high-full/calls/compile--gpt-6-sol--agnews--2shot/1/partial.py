import re
import unicodedata


def _normalize(text):
    text = unicodedata.normalize("NFKC", text).casefold()
    text = text.replace("&", " and ")
    text = re.sub(r"(?<=\w)'s\b", "", text)
    return re.findall(r"[a-z0-9]+", text)


def _entries(text):
    return [item.strip() for item in text.split("|") if item.strip()]


_FEATURES = {category: {} for category in ("business", "sci_tech", "sports", "world")}


def _add(category, weight, phrases):
    for phrase in _entries(phrases):
        words = tuple(_normalize(phrase))
        if words:
            previous = _FEATURES[category].get(words, 0)
            _FEATURES[category][words] = max(previous, weight)


_add("business", 5.0, """
stock market | stock markets | wall street | dow jones | nasdaq composite |
financial markets | shares fell | shares rose | quarterly earnings |
corporate earnings | oil prices | crude oil | oil futures | interest rates |
federal reserve | central bank | trade deficit | economic growth |
gross domestic product | consumer spending | retail sales |
unemployment rate | profit warning | initial public offering |
merger agreement | bankruptcy protection | financial crisis
""")
_add("business", 3.5, """
stocks | shares | shareholders | stock exchange | stock index | equities |
earnings | profits | revenues | revenue | dividend | dividends | investors |
investment bank | investment banking | bankers | banking | bank stocks |
merger | mergers | acquisition | acquisitions | takeover | buyout |
commodities | commodity | crude | petroleum | gasoline | petrol |
refinery | refineries | natural gas | opec | inflation | recession |
economy | economic | gdp | trade deal | tariffs | imports | exports |
currency | currencies | dollar | euro | yen | bonds | treasury bonds |
interest rate | mortgage rates | housing market | real estate |
consumer confidence | jobless claims | payrolls | bankruptcy | bankrupt |
retailer | retailers | retailing | department store | supermarket |
airline | airlines | air fares | ticket prices | manufacturing output |
automaker | automakers | carmaker | carmakers | car sales | auto sales |
earnings report | quarterly profit | quarterly loss | fiscal year |
financial results | financial report
""")
_add("business", 2.1, """
market | markets | trading | traders | trade | traded | finance |
financial | fiscal | funds | fund | lending | loans | loan | debt |
credit | creditors | budget deficit | deficit | surplus | prices |
sales | costs | cost | consumer | consumers | wages | employment |
jobs report | layoffs | laid off | workforce | factory | factories |
production | industry | industries | corporation | companies | company |
businesses | business | executive | chief executive | ceo | chairman |
bid | bidders | deal | contract | contracts | venture | investment |
investors | growth forecast | forecast | forecasts | outlook |
weak demand | demand | supply | output | property | housing |
restaurant chain | hotel chain | chain stores | stores | shoppers |
shopping | discount retailer | discount stores | food prices |
aircraft orders | passenger traffic | freight | shipping
""")
_add("business", 4.0, """
morgan stanley | goldman sachs | jpmorgan | jp morgan | citigroup |
citibank | bank of america | wells fargo | lehman brothers |
bear stearns | credit suisse | deutsche bank | hsbc | barclays |
ubs | visa | mastercard | walmart | wal mart | target stores |
costco | home depot | lowes | tesco | carrefour | mcdonalds |
starbucks | coca cola | pepsico | pepsi | procter and gamble |
general motors | ford motor | chrysler | toyota motor | honda motor |
volkswagen | bmw | boeing | airbus | delta air lines |
american airlines | united airlines | british airways | lufthansa |
southwest airlines | exxon mobil | exxonmobil | chevron | shell oil |
royal dutch shell | bp plc | british petroleum | conoco phillips |
conocophillips | general electric | ge capital | pfizer | merck and co |
johnson and johnson | nike inc | adidas ag
""")

_add("sci_tech", 5.0, """
microsoft | google | alphabet inc | apple computer | apple inc |
ibm | intel | amd | nvidia | qualcomm | oracle | cisco |
hewlett packard | hewlett-packard | hp computers | dell | samsung |
sony | nintendo | playstation | xbox | yahoo | lycos | aol |
facebook | meta platforms | instagram | whatsapp | twitter |
youtube | tiktok | openai | chatgpt | amazon web services |
amazon com | ebay | paypal | netflix | spotify | spacex |
tesla software | nokia | ericsson | blackberry | research in motion |
sun microsystems | red hat | adobe | salesforce | vmware |
windows xp | windows vista | mac os | linux kernel | android operating system |
iphone | ipad | ipod | macbook | galaxy smartphone
""")
_add("sci_tech", 4.2, """
software | hardware | smartphone | smartphones | cellphone |
cellphones | mobile phone | mobile phones | computer | computers |
laptop | laptops | processor | microprocessor | semiconductor |
semiconductors | computer chip | computer chips | microchip | microchips |
chipmaker | chipmakers | operating system | web browser |
search engine | social network | social networking | internet |
world wide web | website | websites | cyberspace | broadband |
wireless network | wi fi | wifi | bluetooth | telecom |
telecommunications | fiber optic | 5g | 4g | mobile network |
video game | video games | videogame | videogames | gaming console |
game console | online gaming | cybersecurity | cyber security |
cyberattack | cyber attack | malware | ransomware | spyware |
computer virus | screensaver | keystrokes | phishing |
artificial intelligence | machine learning | neural network |
robotics | robot | robots | satellite | satellites | spacecraft |
space shuttle | space station | space exploration | nasa |
astronaut | astronauts | telescope | observatory |
scientific research | medical research | clinical trial |
clinical trials | gene therapy | genetic research
""")
_add("sci_tech", 2.8, """
technology | technological | tech | digital | online | web |
app | apps | application software | browser | browsers |
download | downloads | downloading | upload | uploads | email |
emails | e mail | inbox | password | passwords | encryption |
encrypted | hacker | hackers | hacking | database | databases |
server | servers | data center | cloud computing | cloud services |
algorithm | algorithms | programming | developer | developers |
open source | source code | platform | platforms | portal |
tablet | tablets | handset | handsets | touchscreen | touchscreen |
display screen | graphics card | memory chip | hard drive |
storage device | usb | modem | routers | network equipment |
bandwidth | mobile data | text messages | sms | camera phone |
digital camera | mp3 player | dvd player | blu ray |
streaming service | streaming video | virtual reality |
augmented reality | biotechnology | biotech | genome | genomes |
dna | genes | genetic | stem cell | stem cells | vaccine research |
drug trial | laboratory | scientists | physicists | astronomers |
physics | astronomy | geology | fossils | dinosaur | dinosaurs |
planet | planets | mars | moon mission | rocket launch |
solar system | climate research
""")
_add("sci_tech", 1.6, """
research | researchers | science | scientific | scientist |
study | studies | discovered | discovery | discovered |
experiment | experiments | laboratory tests | medical | medicine |
treatment | treatments | vaccine | vaccines | disease |
diagnosis | brain | cancer research | cancer treatment |
drug development | patients | prototype | invention | invented |
innovation | high tech | high technology | electronics |
electronic | devices | device | gadget | gadgets | console |
gaming | gamers | multiplayer | online service | computer industry |
chip | chips | silicon | wireless | cellular | network | networks |
search | search results | privacy | data | digital music |
music downloads | patent | patents | copyright | piracy
""")
_add("sci_tech", 4.1, """
apple | amazon | kindle | fire tablet | google search | google maps |
gmail | chrome browser | windows | office 365 | azure |
android | ios | iphone | ipad | macintosh | imac |
pentium | athlon | geforce | radeon | firefox | mozilla |
safari browser | internet explorer | linux | unix | java software |
playstation 2 | playstation 3 | playstation 4 | playstation 5 |
xbox 360 | xbox one | xbox series | gamecube | nintendo switch |
wii | steam gaming | epic games | activision | electronic arts |
sega | atari | ubisoft | ea games | blizzard entertainment
""")

_add("sports", 5.0, """
world cup | super bowl | olympic games | summer olympics |
winter olympics | champions league | premier league |
national football league | national basketball association |
major league baseball | national hockey league | formula one |
formula 1 | grand slam | wimbledon | us open tennis |
australian open tennis | french open tennis | stanley cup |
world series | nba finals | nfl playoffs | fa cup |
uefa euro | copa america | cricket world cup |
tour de france | ryder cup | masters tournament
""")
_add("sports", 3.7, """
nfl | nba | mlb | nhl | fifa | uefa | ncaa | nascar |
olympics | olympic | paralympics | football | soccer |
basketball | baseball | cricket | rugby | tennis | golf |
hockey | boxing | wrestling | volleyball | badminton |
swimming | athletics | track and field | marathon |
cycling | gymnastics | skiing | snowboard | motorsport |
formula one racing | grand prix | racing driver | race driver |
quarterback | touchdown | home run | home runs | pitcher |
batting | innings | wickets | bowler | goalkeeper | midfielder |
striker | penalty shootout | penalty kick | three pointer |
slam dunk | knockout | title fight | playoff | playoffs |
championship | championships | tournament | tournaments |
league title | cup final | semi final | semifinal |
quarterfinal | quarter final | gold medal | silver medal |
bronze medal | medal tally | world record holder
""")
_add("sports", 2.3, """
athlete | athletes | player | players | team | teams |
coach | coaches | manager | match | matches | game | games |
season | seasons | league | leagues | score | scores |
scored | scoring | points | goal | goals | victory | victories |
defeat | defeated | beat | beaten | wins | won | lost |
draw | tied | final | finals | champion | champions |
title | titles | trophy | trophies | medal | medals |
record | records | transfer | transfers | signed | signing |
draft | rookie | veterans | captain | squad | lineup |
fixtures | referee | umpire | stadium | arena | fans |
club | clubs | rivals | rivalry | seeded | seed |
qualifying | qualifier | training camp | injured | injury |
red card | yellow card | overtime | extra time |
first half | second half | opening round | round of 16
""")
_add("sports", 4.1, """
manchester united | manchester city | liverpool fc | arsenal fc |
chelsea fc | tottenham hotspur | real madrid | barcelona fc |
bayern munich | borussia dortmund | paris saint germain |
juventus | ac milan | inter milan | atletico madrid |
new york yankees | boston red sox | chicago cubs |
los angeles dodgers | san francisco giants | new york mets |
philadelphia phillies | atlanta braves | houston astros |
new york knicks | los angeles lakers | boston celtics |
golden state warriors | chicago bulls | miami heat |
dallas mavericks | cleveland cavaliers | denver nuggets |
new england patriots | dallas cowboys | green bay packers |
kansas city chiefs | philadelphia eagles | san francisco 49ers |
new york giants | pittsburgh steelers | buffalo bills |
new york rangers | boston bruins | toronto maple leafs |
montreal canadiens | detroit red wings | edmonton oilers |
florida panthers | new york islanders |
serena williams | venus williams | roger federer | rafael nadal |
novak djokovic | andy murray | maria sharapova |
tiger woods | rory mcilroy | phil mickelson |
lebron james | michael jordan | kobe bryant | stephen curry |
lionel messi | cristiano ronaldo | david beckham |
neymar | kylian mbappe | mohamed salah | erling haaland |
tom brady | peyton manning | patrick mahomes |
usain bolt | michael phelps | simone biles |
lewis hamilton | max verstappen | michael schumacher
""")

_add("world", 5.0, """
presidential election | general election | election results |
prime minister | foreign minister | foreign ministry |
secretary of state | united nations | security council |
peace talks | peace treaty | cease fire | ceasefire |
terrorist attack | suicide bombing | car bombing |
civil war | war crimes | military coup | coup d etat |
state of emergency | nuclear weapons | nuclear weapon |
weapons of mass destruction | human rights abuses |
natural disaster | earthquake | tsunami | hurricane |
tropical cyclone | volcanic eruption | refugee crisis |
hostage crisis | international relations | foreign policy
""")
_add("world", 3.4, """
president | presidency | election | elections | elected |
vote | voters | voting | ballot | parliament | parliamentary |
congress | congressman | senator | senate | governor |
government | governments | administration | minister |
chancellor | diplomat | diplomatic | diplomats | embassy |
ambassador | summit | treaty | sanctions | sanctions |
opposition | ruling party | political party | politics |
political | campaign | legislature | legislation |
democracy | democratic | dictatorship | regime |
military | troops | soldiers | army | navy | air force |
war | warfare | battle | battles | invasion | invaded |
insurgents | insurgency | militants | militia | rebels |
rebel forces | conflict | clashes | fighting | violence |
killed | casualties | massacre | bombing | bombings |
bomb | bombs | explosives | missile | missiles |
terrorism | terrorist | terrorists | terror | al qaeda |
isis | taliban | hostage | hostages | kidnapped | kidnapping |
police | police officer | arrested | arrest | arrests |
murder | murderer | homicide | criminal | crime | crimes |
court | judge | judges | trial | convicted | sentenced |
prison | jail | prosecutor | prosecutors | investigation |
flood | flooding | floods | storm | storms | tornado |
wildfire | wildfires | drought | landslide | landslides |
disaster | disaster relief | emergency workers |
refugee | refugees | migrants | immigration | asylum
""")
_add("world", 1.9, """
nation | nations | national | international | global |
world leaders | world leader | leaders | leader | authorities |
officials | official | government officials | state |
states | federal | provincial | province | border | borders |
territory | territories | occupied | occupation |
security forces | security | unrest | protests | protest |
protesters | demonstrators | demonstration | strike |
crackdown | crisis | unrest | attack | attacks |
attacked | gunmen | gunman | gunfire | shooting | shootings |
dead | deaths | died | wounded | injured | missing |
survivors | rescue | rescuers | evacuation | evacuated |
aid workers | humanitarian | aid | relief |
inquiry | charges | charged | alleged | accused | suspect |
suspects | lawsuit | legal | law | laws | rights |
constitution | constitutional | referendum |
foreign | bilateral | diplomatic relations |
health emergency | epidemic | pandemic | outbreak
""")
_add("world", 2.0, """
iraq | iraqi | iran | iranian | afghanistan | afghan |
pakistan | pakistani | syria | syrian | israel | israeli |
palestine | palestinian | gaza | west bank | lebanon |
ukraine | ukrainian | russia | russian | crimea |
north korea | south korea | korean peninsula | china |
chinese government | taiwan | tibet | sudan | somalia |
yemen | libya | egypt | haiti | cuba | venezuela |
myanmar | burma | kosovo | serbia | bosnia
""")


_TECH_COMPANIES = {
    "microsoft", "google", "alphabet", "apple", "ibm", "intel", "amd",
    "nvidia", "qualcomm", "oracle", "cisco", "dell", "samsung", "sony",
    "nintendo", "yahoo", "lycos", "aol", "facebook", "instagram",
    "whatsapp", "twitter", "youtube", "tiktok", "openai", "amazon",
    "ebay", "paypal", "netflix", "spotify", "spacex", "nokia",
    "ericsson", "blackberry", "adobe", "salesforce", "vmware",
    "tesla", "meta",
}

_FINANCIAL_TERMS = {
    "earnings", "profit", "profits", "revenue", "revenues", "shares",
    "stock", "stocks", "investors", "sales", "merger", "mergers",
    "acquisition", "acquisitions", "takeover", "lawsuit", "sued",
    "quarterly", "financial",
}

_SPORT_CONTEXT = {
    "game", "games", "match", "matches", "team", "teams", "league",
    "season", "scored", "score", "goals", "goal", "coach", "players",
    "player", "tournament", "championship", "cup", "playoffs",
    "final", "finals", "beat", "defeated", "won",
}


def _get_text(state):
    if isinstance(state, str):
        return state
    if isinstance(state, dict):
        parts = []
        for key in ("title", "headline", "text", "description", "body", "content"):
            value = state.get(key)
            if isinstance(value, str):
                parts.append(value)
        return " ".join(parts)
    return ""


def predict(state) -> dict:
    words = _normalize(_get_text(state))
    if not words:
        return {"answer": "world"}

    scores = {category: 0.0 for category in _FEATURES}
    counts = {}
    max_length = 5

    for start in range(len(words)):
        for length in range(1, min(max_length, len(words) - start) + 1):
            phrase = tuple(words[start:start + length])
            for category, features in _FEATURES.items():
                weight = features.get(phrase)
                if weight is None:
                    continue
                key = (category, phrase)
                occurrence = counts.get(key, 0)
                if occurrence >= 2:
                    continue
                counts[key] = occurrence + 1
                position_factor = 1.5 if start < 16 else 1.0
                repetition_factor = 1.0 if occurrence == 0 else 0.3
                scores[category] += weight * position_factor * repetition_factor

    word_set = set(words)
    tech_company_positions = [
        i for i, word in enumerate(words) if word in _TECH_COMPANIES
    ]
    if tech_company_positions:
        if any(i < 20 for i in tech_company_positions):
            scores["sci_tech"] += 1.7
        if word_set & _FINANCIAL_TERMS:
            scores["sci_tech"] += 4.8
        if "patent" in word_set or "patents" in word_set:
            scores["sci_tech"] += 2.0

    # A numerical game score is supporting evidence only when the text also
    # contains a sporting term; dates and financial figures have the same form.
    if word_set & _SPORT_CONTEXT:
        if re.search(r"\b\d{1,3}\s*(?:-|to)\s*\d{1,3}\b", " ".join(words[:45])):
            scores["sports"] += 2.0

    if "video" in word_set and ("game" in word_set or "games" in word_set):
        scores["sci_tech"] += 4.0

    priority = {"world": 0, "business": 1, "sports": 2, "sci_tech": 3}
    answer = max(scores, key=lambda category: (scores[category], priority[category]))
    return {"answer": answer}