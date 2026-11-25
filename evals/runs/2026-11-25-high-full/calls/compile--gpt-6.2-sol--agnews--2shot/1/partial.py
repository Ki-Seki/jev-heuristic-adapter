import re
import unicodedata
from collections import defaultdict


_LABELS = ("business", "sci_tech", "sports", "world")

# The groups keep several descriptions of the same event from acting like
# several independent votes. Names and event vocabulary are separate evidence.
_GROUPS = (
    ("business", "markets", 5.6, """
        stock market | equity market | wall street | dow jones | dow industrials |
        nasdaq composite | nikkei average | hang seng | standard and poor |
        s and p 500 | s p 500 | ftse 100 | dax index | cac 40 | sensex |
        bond market | currency market | stock index | blue chip stock |
        initial public offering | share offering | trading session |
        treasury yield | treasury note | treasury bond | junk bond |
        after hours trading | opening bell | closing bell | market capitalization |
        stock exchange | securities exchange | market selloff | market rally |
        mutual fund | hedge fund | exchange traded fund | investment portfolio
    """),
    ("business", "markets", 2.7, """
        stocks | equities | stock | share price | stock price | share buyback |
        market value | investor | index futures | futures contract | benchmark index |
        bank shares | trading volume | brokerage | bond | dividend |
        securities | ipo | nasdaq | nikkei | ftse | tokyo stocks |
        market analyst | shareholder | public offering | short seller |
        floated | gold futures | market maker | advancing issues
    """),
    ("business", "results", 5.0, """
        quarterly earnings | earnings report | earnings forecast | earnings per share |
        net profit | net income | operating profit | quarterly loss | quarterly profit |
        annual profit | same store sales | comparable store sales | quarterly revenue |
        quarterly results | fiscal quarter | fiscal year | reported earnings |
        profit warning | profit margin | sales forecast | annual sales |
        sales growth | revenue growth | full year outlook | analyst estimates
    """),
    ("business", "results", 2.5, """
        earnings | revenue | profit | profitable | profitability | losses |
        business outlook | financial results | financial statement | restructuring charge |
        write down | turnover | pretax | net loss | sales | operating income |
        fiscal | cents a share | per share | forecast | balance sheet
    """),
    ("business", "corporate", 4.1, """
        merger | acquisition | takeover | buyout | corporate bankruptcy |
        chapter 11 | bankruptcy protection | bankruptcy court | takeover bid |
        tender offer | buyout offer | private equity | investment bank |
        accounting fraud | insider trading | accounting scandal | accounting irregularities |
        antitrust approval | hostile bid | corporate debt | federal reserve bank |
        chief financial officer | chief executive officer | credit rating | debt rating |
        venture capital | severance package | business plan | pension fund |
        initial bid | controlling stake | stock split | spinning off
    """),
    ("business", "corporate", 1.65, """
        company | corporation | companies | chairman | board of directors |
        chief executive | ceo | cfo | investment | bid | stake | deal |
        partnership | joint venture | union contract | restructuring |
        bankruptcy | bankrupt | layoffs | cut jobs | job cut | cutbacks |
        competitor | parent company | employer | headquarters | hired |
        consolidating | consolidation | creditors | business | co founder
    """),
    ("business", "economy", 5.1, """
        federal reserve | alan greenspan | european central bank | bank of england |
        bank of japan | monetary policy | interest rate | rate hike | rate cut |
        central bank | unemployment rate | jobless claims | consumer confidence |
        consumer price index | producer price index | gross domestic product |
        economic growth | economic slowdown | trade deficit | current account deficit |
        budget deficit | housing market | home sales | housing starts | mortgage rate |
        manufacturing activity | purchasing managers | industrial production |
        retail sales | holiday shopping | consumer spending | consumer prices |
        labor market | economic recovery | economic data | trade surplus |
        payroll growth | job growth | inflation rate | trade talks | import tariffs |
        world trade organization | doha round | trade agreement | free trade |
        labor department data | employment report | currency intervention
    """),
    ("business", "economy", 2.45, """
        economy | economists | economic | inflation | deflation | recession |
        unemployment | jobless | exchange rate | weaker dollar | stronger dollar |
        benchmark rate | trade | tariffs | exports | imports | retail | wholesale |
        productivity | mortgage | bank lending | budget surplus | tax cuts |
        payrolls | borrowing costs | spending | commodity | purchasing power |
        single currency | yuan | euro zone | eurozone | imf
    """),
    ("business", "commodities", 5.35, """
        oil price | crude oil | oil futures | crude futures | crude price | crude |
        oil market | oil output | oil production | oil supply | oil exports |
        per barrel | a barrel | light sweet crude | brent crude | west texas intermediate |
        opec | nymex | heating oil | gas price | gasoline price | energy price |
        fuel price | fuel costs | oil inventories | natural gas prices | petroleum |
        commodities exchange | commodity prices | gold price | gold bullion |
        world oil | crude supplies | oil producer | oil giant
    """),
    ("business", "commodities", 1.65, """
        oil | gasoline | refinery | refining | barrel | natural gas | coal |
        copper | nickel | wheat | corn | sugar | oilfield | drilling | futures |
        energy demand | pump price | harvest | crop | livestock | commodity trading
    """),
    ("business", "industries", 4.5, """
        airline | air carrier | air fare | air travel | airline industry |
        low cost carrier | discount carrier | aviation industry | passenger jet order |
        automaker | carmaker | car sales | auto sales | auto industry |
        department store | discount retailer | shopping mall | supermarket |
        retail chain | retail giant | drugmaker | drug maker | drug company |
        pharmaceutical company | property developer | insurance broker |
        mortgage lender | commercial bank | consumer goods | fast food |
        investment firm | credit card issuer | car rental | home builder |
        steel maker | steelmaker | oil company | supermarket chain | ad agency
    """),
    ("business", "industries", 2.35, """
        retailer | manufacturer | insurance | insurer | banking | bank |
        pharmacy | pharmaceutical | grocery | restaurant chain | fares |
        factory | shop | shoppers | store chain | bankrupt carrier |
        production plant | shipbuilder | contractor | pilot union | pension
    """),
    ("business", "firms", 5.0, """
        morgan stanley | goldman sachs | lehman brothers | merrill lynch |
        jpmorgan | jp morgan | bank of america | deutsche bank | hsbc |
        citigroup | citibank | bear stearns | barclays | wells fargo | credit suisse |
        ubs | freddie mac | fannie mae | warren buffett | berkshire hathaway |
        standard chartered | wachovia | american express | visa inc | mastercard |
        enron | tyco | worldcom accounting | martha stewart | martha stewart living |
        wal mart | walmart | kmart | k mart | sears | roebuck | jc penney |
        home depot | costco | tesco | safeway | target corp | macy | carrefour |
        marks and spencer | abercrombie | kroger | staples inc | best buy |
        toyota | general motors | gm corp | daimlerchrysler | daimler chrysler |
        ford motor | volkswagen | honda motor | chrysler | hyundai | nissan |
        mitsubishi motors | bmw | renault | fiat | stellantis | tesla motors |
        airbus | boeing | bombardier | delta air lines | delta airlines |
        united airlines | us airways | american airlines | continental airlines |
        northwest airlines | southwest airlines | jetblue | ryanair | easyjet |
        british airways | virgin atlantic | qantas | air france | klm | alitalia |
        singapore airlines | lufthansa | japan airlines | air canada | spirit airlines |
        pfizer | merck | glaxosmithkline | astrazeneca | eli lilly | roche |
        sanofi | novartis | johnson and johnson | bristol myers | abbvie |
        marsh and mclennan | marsh mclennan | aig | allstate | prudent financial |
        prudential financial | aig insurance | eliott spitzer | eliot spitzer |
        exxon | exxonmobil | chevron | chevrontexaco | royal dutch shell |
        conocophillips | halliburton | petrobras | saudi aramco | yukos | gazprom |
        coca cola | pepsico | kraft foods | unilever | procter and gamble |
        nestle | mcdonald | starbucks | wendy | burger king | yum brands |
        walt disney | disney co | comcast bid | viacom | time warner |
        news corp | clear channel | mci creditors | federal deposit insurance |
        ge capital | general electric | alcoa | arcelor | mittal | us steel |
        federal express | fedex | dhl | united parcel service |
        sears holdings | dollar general | dollar tree | wework | evergrande
    """),

    ("sci_tech", "tech_firms", 5.9, """
        microsoft | google | ibm | intel | amd | nvidia | qualcomm |
        apple computer | apple inc | sun microsystems | hewlett packard | compaq |
        cisco | juniper networks | broadcom | texas instruments | advanced micro devices |
        nortel | lucent | alcatel | symantec | mcafee | kaspersky | trend micro |
        red hat | novell | sco group | vmware | suse | mozilla | opera software |
        adobe | macromedia | autodesk | corel | oracle | peoplesoft | siebel |
        salesforce | servicenow | sap ag | s a p | workday | snowflake inc |
        dell | lenovo | gateway computer | acer | asus | logitech | arm holdings |
        nokia | motorola | ericsson | blackberry | research in motion |
        vodafone | verizon | sprint nextel | nextel | bellsouth | sbc communications |
        at and t | t mobile | bt group | british telecom | france telecom |
        deutsche telekom | telecom italia | china mobile | cingular | telecoms operator |
        samsung electronics | lg electronics | sony | panasonic | toshiba |
        hitachi | fujitsu | nec corp | sharp electronics | canon inc | nikon |
        yahoo | america online | aol | netscape | lycos | ask jeeves | msn |
        ebay | paypal | amazon com | amazon web services | alibaba | tencent | baidu |
        facebook | instagram | whatsapp | twitter | tiktok | bytedance | snapchat |
        youtube | meta platforms | openai | anthropic | deepmind | spacex |
        electronic arts | nintendo | activision | blizzard entertainment | ubisoft |
        sega | take two interactive | valve software | rockstar games |
        palantir | broadcom corp | micron technology | taiwan semiconductor | tsmc |
        foxconn | lenovo group | western digital | seagate | sandisk
    """),
    ("sci_tech", "tech_firms", 3.45, """
        apple | samsung | hp | sap | amazon | acer inc | dell computer |
        steve jobs | bill gates | tim cook | mark zuckerberg | steve ballmer |
        larry ellison | linus torvalds | elon musk | jeff bezos | satya nadella |
        sam altman | sheryl sandberg | michael dell | sundar pichai
    """),
    ("sci_tech", "software", 5.4, """
        operating system | source code | open source | software update | security patch |
        word processor | spreadsheet software | office suite | enterprise software |
        database software | software piracy | media player | software developer |
        windows xp | windows vista | windows 11 | windows 10 | windows server |
        microsoft office | microsoft windows | internet explorer | firefox | thunderbird |
        mozilla firefox | linux | ubuntu | unix | debian | solaris | mac os |
        macos | os x | ios | android | chrome os | windows media | service pack |
        adobe flash | virtual machine | virtualization | cloud computing |
        data center | content delivery network | application server | web server |
        cloud service | cloud storage | computer program | software application |
        software patent | digital rights management | artificial intelligence |
        machine learning | neural network | deep learning | generative ai |
        large language model | chatgpt | self driving software | computer vision |
        voice recognition | quantum computing | digital assistant | ai model |
        ai chatbot | semiconductors | microprocessor | computer chip | graphics chip
    """),
    ("sci_tech", "software", 2.65, """
        software | hardware | chipmaker | chip set | chipset | processor | chip |
        computing | computer | programming | programmer | servers | database |
        data processing | apps | application | algorithm | chatbot | robot |
        robotics | automation | tech | technology | operating systems |
        computing power | pc maker | pc industry | graphics card | memory chip | ai
    """),
    ("sci_tech", "hardware", 4.9, """
        personal computer | desktop computer | laptop | notebook computer |
        tablet computer | smartphone | smart phone | ipod | iphone | ipad |
        imac | macbook | powerbook | palm pilot | handheld computer | digital camera |
        digital music player | mp3 player | portable player | dvd recorder |
        blu ray | high definition tv | flat panel | flat screen | digital television |
        computer maker | hard drive | flash memory | solid state drive | usb |
        sound card | mobile device | wearable device | smart watch | headset |
        virtual reality | augmented reality | home automation | consumer electronics |
        battery technology | hydrogen fuel cell | electric vehicle battery |
        nanotechnology | technical specification | drone technology
    """),
    ("sci_tech", "internet", 4.75, """
        search engine | search results | search advertising | web search | internet portal |
        world wide web | web browser | web site | website | web pages | web hosting |
        online advertising | social network | social media | online auction |
        online retailer | online music | file sharing | peer to peer |
        digital download | music download | internet radio | internet access |
        broadband internet | e commerce | ecommerce | internet service provider |
        online service | message board | instant messaging | online privacy |
        blogs | blogging | streaming service | live streaming | domain name |
        top level domain | wikipedia | blog | podcast | online payment
    """),
    ("sci_tech", "internet", 2.5, """
        web | internet | online | email | e mail | digital | broadband |
        download | browser | wireless | broadband access | cyberspace |
        tech industry | silicon valley | startup | data privacy | subscriptions |
        internet users | portal | messaging | instant message | video streaming
    """),
    ("sci_tech", "security", 5.7, """
        computer virus | email virus | e mail virus | computer worm |
        internet worm | malicious software | malicious code | trojan horse |
        trojan | spyware | ransomware | adware | malware | phishing | botnet |
        keylogger | keystroke | cyberattack | cyber attack | cyber security |
        cybersecurity | identity theft online | software flaw | security flaw |
        security vulnerability | security hole | data breach | denial of service |
        computer hacker | hackers | firewall | antivirus | anti virus |
        spam filter | junk email | junk mail | spammer | screensaver | screen saver |
        antivirus software | password theft | security update | encryption |
        online fraud | computer security | digital certificate
    """),
    ("sci_tech", "security", 1.65, """
        spam | password | patch | vulnerability | worm | infected computers |
        encrypted | spam messages | computer files | data theft | user account
    """),
    ("sci_tech", "telecom", 5.05, """
        telecom | telecommunications | telecoms | mobile phone | cell phone |
        cellular phone | mobile network | cellular network | wireless network |
        mobile operator | wireless carrier | phone company | voice over ip |
        internet telephony | internet phone | voip | wifi | wi fi | bluetooth |
        wireless broadband | hotspot | 3g | 4g | 5g | spectrum auction |
        wireless spectrum | fiber optic | fibre optic | dsl | text messaging |
        sms | telephone service | long distance calls | mobile subscriber |
        mobile handset | wireless service | cable modem | broadband provider |
        digital subscriber line | fixed line operator | handset maker | cell tower |
        telecommunications equipment | telecom equipment | network equipment |
        wireless phone | mobile service | telecom regulator
    """),
    ("sci_tech", "telecom", 2.0, """
        cellphone | handset | mobile | cellular | network gear | spectrum |
        network operator | telephone network | roaming | subscribers | sim card
    """),
    ("sci_tech", "games", 5.9, """
        video game | videogame | computer game | online game | gaming console |
        game console | xbox | playstation | gamecube | game boy | nintendo ds |
        nintendo switch | final fantasy | grand theft auto | halo 2 |
        world of warcraft | electronic gaming | video gaming | game developer |
        game publisher | handheld game | minecraft | steam deck | esports | e sports |
        fortnite | call of duty | half life 2 | video game industry
    """),
    ("sci_tech", "games", 2.4, """
        gaming | gamers | gameplay | console | game controller | arcade |
        multiplayer | virtual world | pc game | game release | interactive entertainment
    """),
    ("sci_tech", "space", 6.2, """
        nasa | jet propulsion laboratory | european space agency |
        international space station | space station | space shuttle | space probe |
        space telescope | james webb | hubble | spacecraft | spaceflight | space flight |
        spaceshipone | space ship one | virgin galactic | x prize | ansari |
        rocket launch | launch vehicle | rocket engine | falcon 9 | ariane 5 | soyuz |
        mars rover | mars exploration | red planet | mars express | mars global surveyor |
        cassini | huygens | saturn moon | solar system | space mission | astronaut |
        cosmonaut | lunar lander | lunar mission | moon landing | lunar orbit |
        asteroid | comet | exoplanet | black hole | supernova | interstellar |
        dark matter | dark energy | milky way | astronomy | astronomer |
        solar flare | solar eclipse | meteor shower | gamma ray burst |
        infrared telescope | space tourism | private spacecraft | shuttle launch |
        orbiting satellite | low earth orbit | satellite launch | orbital flight
    """),
    ("sci_tech", "space", 2.35, """
        orbit | orbital | lunar | space | galaxy | galaxies | planet | telescope |
        observatory | saturn | jupiter | mars | moon | satellite | shuttle |
        mars mission | rocket | rover | crater | space agency | life on mars | nebula
    """),
    ("sci_tech", "research", 5.3, """
        scientists | scientific study | new study | study finds | study suggests |
        study shows | study found | researchers | research team | scientific journal |
        stem cell | gene therapy | gene editing | crispr | genetic mutation |
        genetic engineering | genetic research | genetic test | medical research |
        clinical trial | phase iii trial | vaccine trial | drug trial |
        experimental drug | experimental vaccine | drug discovery | vaccine development |
        lancet | new england journal | journal of medicine | peer reviewed |
        human genome | genome project | dna sequence | genome sequencing |
        protein structure | genetically modified | cloned embryo | therapeutic cloning |
        cell biology | lab experiment | laboratory tests | evolutionary biology |
        particle physics | particle accelerator | particle collider | cern |
        nobel prize in physics | nobel prize in chemistry | nobel prize in medicine |
        dinosaur fossil | fossil evidence | fossil remains | archaeological discovery |
        archaeologist | paleontologist | oceanographers | marine biologist |
        climate model | global warming study | research vessel | scientific discovery |
        health study | risk factor | disease transmission study | quantum mechanics |
        nuclear fusion reactor | fusion energy | carbon capture technology |
        emissions technology | solar cell | solar panel technology
    """),
    ("sci_tech", "research", 2.0, """
        research | science | scientist | experiment | laboratory | biology | chemistry |
        physics | genetic | genetics | gene | genome | dna | clone | cloned | cloning |
        fossil | dinosaur | species | discovered | discovery | medical journal |
        treatment | therapy | vaccine | medication | side effect | clinical |
        placebo | molecular | professor | patient | heart attack risk |
        cardiovascular risk | cancer risk | cancer treatment | heart disease |
        drug safety | ecology | endangered species | biodiversity | warming |
        climate change | animals | conservation | geology | geologist |
        seismologist | embryonic | published in the journal | data analysis
    """),

    ("sports", "fixtures", 5.3, """
        season opener | home opener | regular season | postseason | post season |
        playoff | playoffs | championship | semifinal | quarterfinal | semi final |
        quarter final | title defense | title defence | league title | defending champion |
        reigning champion | opening round | third round | second round win | first round win |
        world series | super bowl | stanley cup | world cup qualifier |
        fifa world cup | world cup | european championship | champions league |
        europa league | premier league | premiership | primera liga | la liga |
        serie a | bundesliga | league cup | uefa cup | fa cup | carling cup |
        african cup of nations | copa america | copa libertadores | nations league |
        grand slam | davis cup | fed cup | wimbledon | roland garros |
        french open | australian open | us open | u s open | atp tour |
        wta tour | ryder cup | presidents cup | pga tour | lpga tour | british open |
        tour de france | ncaa tournament | march madness | final four |
        olympic games | summer olympics | winter olympics | paralympics |
        olympics | athens games | timetrial | time trial | grand prix |
        formula one | formula 1 | f1 | indy 500 | daytona 500 | nascar |
        sprint cup | nextel cup | monaco grand prix | world rally championship |
        breeders cup | kentucky derby | preakness stakes | belmont stakes |
        ashes series | cricket world cup | twenty20 | indian premier league |
        rugby world cup | six nations | tri nations | heineken cup
    """),
    ("sports", "fixtures", 2.45, """
        tournament | final | semifinalist | qualifier | title race | runners up |
        opening round | third seed | top seed | seeded | unseeded | ranking |
        league | division title | standings | wild card | wildcard | season |
        home game | away game | debut season | cup final | doubleheader |
        qualifying race | qualifying round | gold medal | silver medal | bronze medal |
        medal table | world record | national record | sporting event | fixture |
        exhibition game | all star | bowl game | test series | pole position
    """),
    ("sports", "sports_language", 5.15, """
        home run | grand slam homer | game winning | walk off | pinch hitter |
        runs batted in | winning pitcher | starting pitcher | batting average |
        shutout | no hitter | perfect game | strikeout | extra innings | double play |
        top of the ninth | bottom of the ninth | earned run | bullpen | major league |
        minor league | baseball team | spring training | stolen base | designated hitter |
        touchdown | quarterback | wide receiver | running back | tight end |
        linebacker | cornerback | offensive line | defensive end | field goal |
        interception return | punt return | kick return | passing yards | fantasy football |
        play action | overtime win | last minute goal | stoppage time |
        injury time | penalty shootout | penalty kick | free kick | corner kick |
        goal difference | scored twice | own goal | clean sheet | red card | yellow card |
        hat trick | equalizer | equaliser | champions league | cup tie | team captain |
        match winning | winning goal | head coach | club manager | transfer fee |
        transfer window | free agent | draft pick | starting lineup | training camp |
        preseason game | starting five | slam dunk | triple double | double double |
        three pointer | three point shot | free throw | buzzer beater |
        penalty box | power play | short handed goal | empty net | stanley cup final |
        match point | straight sets | tie break | tiebreak | match play | stroke play |
        hole in one | under par | over par | back nine | sudden death playoff |
        birdie putt | six wicket | five wicket | test match | one day international |
        half century | opening batsman | fast bowler | wickets | scrum half |
        knockout punch | heavyweight champion | welterweight | middleweight |
        world heavyweight | weigh in | mixed martial arts | title fight |
        photo finish | starting grid | lap record | pit stop | crash out |
        doping ban | anti doping | drug test suspension | medal winner |
        winning streak | losing streak | team owner | players union |
        labor lockout | salary cap | collective bargaining agreement
    """),
    ("sports", "sports_language", 2.8, """
        coach | coaching | coached | athlete | athletics | football | soccer |
        basketball | baseball | hockey | tennis | golfer | golf | cricket |
        rugby | cycling | marathon | gymnast | swimmer | skiing | boxing |
        catcher | pitcher | batter | batting | shortstop | outfielder | inning |
        homer | homered | rbi | glove save | goaltender | goalkeeper | keeper |
        striker | midfielder | winger | defender | forward line | forward pass |
        midfielder | roster | squad | teammate | captaincy | substitution |
        match | game | scored | scoring | scoreless | goalless | goals |
        overtime | rebounds | assists | retire from sport | race winner |
        clinched | clinches | rout | routed | defeated | defeats | edged |
        outplayed | outscored | touchdown pass | injured reserve | hamstring |
        concussion protocol | suspension | relief pitcher | racing driver |
        driver standings | race track | race car | motocross | bowlers | innings |
        batsman | bowled | batting side | wickets | tackle | goalkeeper |
        tie breaker | set point | break point | birdie | bogey | putt | fairway |
        leader board | leaderboard | caddie | track and field | steeplechase |
        freestyle relay | pole vault | discus | long jump | sprinter |
        relay team | medalist | medallist | decathlon | mile race | swimming final
    """),
    ("sports", "weak_sports", 0.85, """
        game | player | team | win | victory | loss | draw | beat | rivalry |
        defending | points | yards | hits | runs | beat | fell | equalized |
        race | racing | winner | unbeaten | unbeaten run | practice | made the cut |
        eliminated | clinch | rematch | comeback | rally | revenge | contest |
        cup | fans | crowd | stadium | arena | locker room | dressing room |
        lap | laps | champion | champions | title | record | seeded | picked |
        commentators | bench | final whistle | match report | injury
    """),
    ("sports", "leagues", 5.5, """
        nfl | nba | wnba | nhl | mlb | mlbpa | ncaa | mls | uefa | fifa |
        afl | pga | lpga | usga | nascar | ioc | ufc | world athletics |
        international olympic committee | fa premier league | pro football |
        national football league | national hockey league | national basketball association |
        major league baseball | major league soccer | national league | american league |
        american league championship | alcs | nlcs | american league east |
        eastern conference | western conference | big ten | big east | big 12 |
        pac 10 | pac 12 | southeastern conference | atlantic coast conference |
        college football | college basketball | division i | bowl championship series | bcs
    """),
    ("sports", "teams", 4.8, """
        red sox | white sox | yankees | boston red sox | new york yankees |
        baltimore orioles | toronto blue jays | blue jays | tampa bay devil rays |
        devil rays | tampa bay rays | minnesota twins | cleveland indians |
        cleveland guardians | detroit tigers | kansas city royals | texas rangers |
        oakland athletics | oakland a | seattle mariners | anaheim angels |
        los angeles angels | houston astros | arizona diamondbacks | diamondbacks |
        milwaukee brewers | chicago cubs | cubs | st louis cardinals |
        pittsburgh pirates | cincinnati reds | new york mets | mets |
        atlanta braves | braves | florida marlins | miami marlins |
        philadelphia phillies | phillies | montreal expos | washington nationals |
        colorado rockies | los angeles dodgers | dodgers | san diego padres |
        san francisco giants | tampa bay buccaneers | new england patriots |
        miami dolphins | buffalo bills | new york jets | new york giants |
        dallas cowboys | oakland raiders | las vegas raiders | los angeles raiders |
        san francisco 49ers | 49ers | washington redskins | washington commanders |
        philadelphia eagles | detroit lions | chicago bears | green bay packers |
        packers | minnesota vikings | atlanta falcons | new orleans saints |
        carolina panthers | seattle seahawks | arizona cardinals | st louis rams |
        los angeles rams | denver broncos | kansas city chiefs | san diego chargers |
        los angeles chargers | pittsburgh steelers | steelers | baltimore ravens |
        cincinnati bengals | cleveland browns | indianapolis colts |
        tennessee titans | jacksonville jaguars | houston texans |
        los angeles lakers | lakers | boston celtics | celtics | new york knicks |
        knicks | miami heat | chicago bulls | detroit pistons | indiana pacers |
        pacers | cleveland cavaliers | toronto raptors | san antonio spurs |
        dallas mavericks | houston rockets | utah jazz | sacramento kings |
        golden state warriors | new jersey nets | brooklyn nets | new orleans hornets |
        los angeles clippers | phoenix suns | minnesota timberwolves |
        seattle supersonics | portland trail blazers | denver nuggets |
        philadelphia 76ers | 76ers | memphis grizzlies | orlando magic |
        toronto maple leafs | maple leafs | new york rangers | new york islanders |
        detroit red wings | colorado avalanche | tampa bay lightning |
        chicago blackhawks | edmonton oilers | calgary flames | ottawa senators |
        montreal canadiens | vancouver canucks | boston bruins | philadelphia flyers |
        pittsburgh penguins | new jersey devils | buffalo sabres | dallas stars |
        manchester united | manchester city | arsenal fc | liverpool fc |
        tottenham | chelsea fc | newcastle united | aston villa | west ham |
        leeds united | everton | blackburn rovers | birmingham city | crystal palace |
        leicester city | bolton wanderers | wolverhampton wanderers | wrexham |
        sporting lisbon | fc porto | benfica | real madrid | fc barcelona |
        atletico madrid | juventus | ac milan | inter milan | bayern munich |
        borussia dortmund | ajax amsterdam | paris saint germain | as roma |
        lazio | deportivo la coruna | athletic bilbao | basel fc |
        glasgow rangers | glasgow celtic | boca juniors | river plate |
        all blacks | springboks | wallabies | british lions |
        fighting irish | ohio state buckeyes | usc trojans | notre dame football |
        oklahoma sooners | texas longhorns | auburn tigers | miami hurricanes |
        florida gators | michigan wolverines | duke blue devils | north carolina tar heels
    """),
    ("sports", "teams", 2.25, """
        arsenal | chelsea | lakers | dodgers | mariners | orioles | expos |
        padres | royals | cardinals | astros | braves | brewers | marlins |
        chargers | bengals | broncos | vikings | rams | ravens | colts | seahawks |
        mavericks | clippers | wizards | pistons | timberwolves | raptors |
        canadiens | canucks | oilers | flames | man utd | man city | spurs |
        red devils | tar heels | sooners | buckeyes | gunners | indianapolis colts
    """),
    ("sports", "athletes", 5.0, """
        tiger woods | ernie els | vijay singh | phil mickelson | annika sorenstam |
        jack nicklaus | rory mcilroy | sergio garcia | colin montgomerie |
        roger federer | federer | rafael nadal | novak djokovic | andy roddick |
        lleyton hewitt | andre agassi | agassi | marat safin | tim henman |
        juan carlos ferrero | maria sharapova | sharapova | lindsay davenport |
        amelie mauresmo | serena williams | venus williams | justine henin |
        jennifer capriati | kim clijsters | martina navratilova | simona halep |
        michael schumacher | schumacher | rubens barrichello | fernando alonso |
        kimi raikkonen | juan pablo montoya | jenson button | lewis hamilton |
        max verstappen | dale earnhardt | jeff gordon | jimmie johnson |
        barry bonds | sammy sosa | alex rodriguez | a rod | derek jeter |
        ichiro suzuki | ichiro | pedro martinez | roger clemens | curt schilling |
        david ortiz | manny ramirez | joe torre | mark mcgwire | shohei ohtani |
        peyton manning | eli manning | tom brady | brett favre | donovan mcnabb |
        ben roethlisberger | michael vick | bill belichick | terrell owens |
        randy moss | jamal lewis | kurt warner | patrick mahomes | aaron rodgers |
        shaquille oneal | shaquille o neal | shaq | kobe bryant | lebron james |
        michael jordan | ray allen | allen iverson | yao ming | tim duncan |
        karl malone | vince carter | stephen curry | kevin garnett | kevin durant |
        david beckham | wayne rooney | thierry henry | cristiano ronaldo |
        lionel messi | ronaldo | ronaldinho | zidane | raul gonzalez |
        alex ferguson | arsene wenger | jose mourinho | pep guardiola |
        ruud van nistelrooy | fifa player | didier drogba | michael owen |
        steven gerrard | gareth bale | kylian mbappe | kylian mbappe |
        andriy shevchenko | frank lampard | ruud van nistelrooy |
        michael phelps | ian thorpe | lance armstrong | usain bolt |
        marion jones | justin gatlin | maurice greene | kelly holmes |
        sachin tendulkar | brian lara | shane warne | ricky ponting | rahul dravid |
        anil kumble | andrew flintoff | murray mexted | jonny wilkinson |
        mike tyson | lennox lewis | oscar de la hoya | vitali klitschko |
        bernard hopkins | evander holyfield | floyd mayweather | fedor emelianenko
    """),

    ("world", "government", 4.9, """
        presidential election | general election | parliamentary election | local elections |
        election campaign | opinion poll | electoral commission | polling station |
        polling place | voter turnout | election results | presidential candidate |
        presidential debate | running mate | republican party | democratic party |
        labor party | labour party | conservative party | liberal party |
        house of representatives | house of commons | parliament vote |
        power sharing | coalition government | cabinet reshuffle | cabinet minister |
        prime minister | foreign minister | foreign secretary | interior minister |
        defense minister | defence minister | secretary of state | home secretary |
        opposition party | opposition leader | ruling party | head of state |
        white house | presidential palace | supreme court ruling | constitutional court |
        constitutional referendum | no confidence | political crisis | coup attempt |
        military coup | state of emergency | human rights | civil rights |
        asylum seeker | refugee camp | immigration policy | border security |
        capital punishment | death penalty | political dissident | political prisoner
    """),
    ("world", "government", 2.2, """
        politics | political | president | presidency | prime ministerial |
        government | parliament | parliamentary | legislature | senator | senate |
        congress | congressional | lobbyist | lawmakers | legislation | bill |
        governor | mayor | cabinet | council | regime | dictatorship |
        ruling coalition | opposition | campaign | election | votes | voting |
        voters | ballot | recount | referendum | protest | protesters |
        demonstrators | rally against | democracy | royal family | civil servant |
        welfare reform | border | migrants | immigrant | asylum | refugee |
        activists | ministry | envoy | ambassador | police minister | constituent
    """),
    ("world", "international", 5.2, """
        united nations | un security council | u n security council | security council |
        un general assembly | un resolution | international atomic energy agency |
        iaea | nuclear program | nuclear programme | nuclear weapons |
        weapons inspectors | nuclear talks | nonproliferation | nuclear standoff |
        arms embargo | international sanctions | economic sanctions | diplomatic ties |
        diplomatic relations | state visit | diplomatic mission | peace talks |
        peace process | peace plan | peace accord | four party talks | six party talks |
        ceasefire | cease fire | truce agreement | peacekeeping troops |
        un peacekeeper | un peacekeeping | european union summit | g8 summit |
        arab league | african union | nato troops | united nations chief |
        kofi annan | antonio guterres | international criminal court | world leaders |
        foreign policy | international aid | humanitarian crisis | relief agency |
        alleged war crimes | international border | territorial dispute |
        expel diplomats | world summit | diplomatic row | disputed territory
    """),
    ("world", "international", 2.1, """
        un | nato | eu commission | european commission | european union |
        peacekeeper | sanctions | diplomacy | diplomatic | diplomats | bilateral |
        summit | envoy | negotiations | humanitarian | peacekeeping | aid workers |
        disarmament | united nation | treaty | state department | foreign ministry |
        foreign affairs | peace deal | ceasefire violation | consulate | embassy
    """),
    ("world", "conflict", 5.25, """
        suicide bombing | suicide bomber | car bomb | truck bomb | road side bomb |
        roadside bomb | bomb attack | bomb blast | bomb explosion | bombs exploded |
        terrorist attack | terror attack | terrorist bombing | al qaeda | al qaida |
        islamic state | isis militants | militant group | islamist militants |
        rebel group | rebel leader | rebel forces | armed rebels | palestinian militants |
        israeli forces | israeli troops | israeli soldiers | israeli military |
        israeli army | west bank | gaza strip | palestinian authority |
        palestinian leader | intifada | israeli settlement | hamas | hezbollah |
        fatah | plo | al aqsa | taliban | kabul government | iraq war |
        iraqi police | iraqi troops | us troops | u s troops | coalition troops |
        british troops | peacekeeping force | northern iraq | war in iraq |
        saddam hussein | abu ghraib | abu musab al zarqawi | al zarqawi |
        fighting in fallujah | shiite militia | shi ite militia | mehdi army |
        senior military officials | rocket attack | missile attack | air strike | airstrike |
        mortar attack | artillery fire | military offensive | mounting offensive |
        ground offensive | military operation | tank fire | cross border attack |
        hostage crisis | hostage takers | hostages released | hostages held |
        hostage release | beheaded | beheading | kidnappers | armed men |
        mass grave | mass killing | war crimes | genocide | ethnic cleansing |
        civil war | armed conflict | guerrilla fighters | armed separatists |
        separatist rebels | rebel insurgency | chechen rebels | liberation tigers |
        tamil tigers | beslan school | school siege | september 11 attacks |
        terrorism suspect | terror suspect | north korean nuclear
    """),
    ("world", "conflict", 2.65, """
        violence | military | army | troops | infantry | soldiers | forces |
        defense ministry | defence ministry | pentagon | afghan forces |
        marines | raid | bomb | blast | blasts | bombing | bomber | bombed |
        armed | assault | ambush | ambushed | shelling | gunfire | gunmen |
        gunman | militants | insurgents | rebels | separatists | mujahideen |
        guerrillas | militia | terrorist | terror | terrorism | war | warfare |
        wartime | battlefield | weapons | gun battle | combat | target killed |
        attack | casualties | killed | deaths | dead | wounded | injured |
        kidnap | kidnapped | kidnapping | abducted | abduction | hostages | hostage |
        torture | unrest | uprising | occupation | invasion | arsenal of weapons |
        fighters | offensive | besieged | siege | clashes | massacre |
        prisoners | detainee | detention | crackdown | truce
    """),
    ("world", "people_places", 3.45, """
        george w bush | president bush | bush administration | john kerry |
        senator kerry | dick cheney | colin powell | condoleezza rice |
        donald rumsfeld | john edwards | barack obama | donald trump | joe biden |
        vice president | kamala harris | tony blair | gordon brown | jacques chirac |
        gerhard schroeder | angela merkel | emmanuel macron | rishi sunak |
        silvio berlusconi | jose luis rodriguez zapatero | vladimir putin |
        kremlin | yasser arafat | arafat | ariel sharon | mahmoud abbas |
        benjamin netanyahu | bashar al assad | moammar gadhafi | muammar gaddafi |
        ayatollah | hosni mubarak | pervez musharraf | manmohan singh | narendra modi |
        hamid karzai | ayad allawi | iyad allawi | moqtada al sadr | al sadr |
        kim jong il | kim jong un | hu jintao | xi jinping | dalai lama |
        roh moo hyun | junichiro koizumi | shinzo abe | shinzo abe |
        viktor yushchenko | yushchenko | viktor yanukovych | yanukovich |
        leonid kuchma | volodymyr zelensky | zelenskyy | alexander lukashenko |
        robert mugabe | thabo mbeki | nelson mandela | hugo chavez | fidel castro |
        lula da silva | john howard | mark latham | gloria macapagal arroyo |
        susilo bambang yudhoyono | megawati | jean bertrand aristide | pope |
        baghdad | fallujah | najaf | karbala | basra | mosul | kirkuk |
        chechnya | chechen | beslan | darfur | khartoum | pyongyang | kabul |
        guantanamo | rafah | ramallah | gaza | palestinian | palestinians |
        karabakh | kashmir | aceh | east timor | south ossetia
    """),
    ("world", "people_places", 1.1, """
        iraq | iraqi | iran | iranian | tehran | afghanistan | afghan |
        north korea | north korean | south korea | israel | israeli | jerusalem |
        sudan | sudanese | haiti | haitian | syria | syrian | damascus |
        lebanon | beirut | ukraine | ukrainian | kiev | kyiv | kosovo |
        russia | russian | moscow | pakistan | pakistani | islamabad |
        nepal | myanmar | burma | somalia | sierra leone | congo | libya |
        libyan | sri lanka | indonesia | venezuela | cuban | saudi |
        bush | kerry | putin | nets government | beijing authorities |
        african nations | kurdish | kurds | sunni | shiite | shia | balkans
    """),
    ("world", "disaster", 5.7, """
        earthquake | aftershock | tsunami | tidal wave | hurricane | typhoon |
        super typhoon | cyclone | tornado | tropical storm | tropical depression |
        flash flood | flooding | flood waters | mudslide | landslide | wildfire |
        forest fire | bushfire | volcanic eruption | volcanic ash | lava flow |
        mount st helens | hurricane ivan | hurricane frances | hurricane katrina |
        hurricane charley | hurricane jeanne | storm surge | bomb hoax |
        natural disaster | state of disaster | drought emergency | widespread drought |
        rescue worker | rescue teams | relief effort | death toll |
        rescue operation | rescue helicopters | search and rescue | ferry sank |
        train crash | plane crash | air crash | fatal crash | crashed plane |
        train derailment | ferry disaster | building collapse | collapsed building |
        death toll rose | trapped miners | mine collapse | mine explosion |
        power blackout | mass evacuation | emergency evacuation | evacuated residents
    """),
    ("world", "disaster", 2.0, """
        storm | floods | flooded | high winds | heavy rains | torrential rain |
        evacuees | evacuated | emergency services | rescue | survivors | homeless |
        crashed | wreckage | sunken | sinking | missing | outbreak | epidemic |
        pandemic | bird flu | avian flu | sars outbreak | cholera outbreak |
        plague outbreak | food shortage | famine | heat wave
    """),
    ("world", "crime", 5.0, """
        murder charge | murder trial | convicted of murder | murder suspect |
        manslaughter | death sentence | sentenced to death | death row |
        prison sentence | police investigation | criminal investigation | felony |
        federal prosecutors | arrested on suspicion | criminal charges |
        police raid | police officers | police chief | broke into | armed robbery |
        mass shooting | school shooting | fatal shooting | convicted killer |
        serial killer | murder case | murder victim | grand jury | drug trafficking |
        human trafficking | prison break | escaped prisoners | jail term |
        corruption charges | corruption scandal | corruption investigation |
        money laundering | bribery charges | indicted on charges | illegal arms |
        missing person | sex abuse | sexual assault | violent crime
    """),
    ("world", "crime", 2.5, """
        police | arrested | arrest | custody | jury | prosecutors | indictment |
        indicted | criminal | charged | pleaded guilty | guilty | acquitted |
        court | judge | trial | convicted | prison | jail | suspect |
        corruption | bribery | smuggling | fugitive | crime | murder |
        murderer | robbery | theft | shot dead | shooting | stabbed |
        gunshot | standoff | execution | executed | inquiry | inquest |
        municipal authorities | investigation | abuse | scandal
    """),
)


# Only regular or otherwise unambiguous forms useful for these topics are
# normalized here. General stemming would conflate several team and place names.
_PLURALS = """
    prices:price markets:market reports:report forecasts:forecast
    profits:profit incomes:income warnings:warning margins:margin
    quarters:quarter years:year stores:store costs:cost rates:rate
    bonds:bond notes:note dividends:dividend investors:investor
    shareholders:shareholder indices:index indexes:index exchanges:exchange
    sessions:session contracts:contract analysts:analyst brokerages:brokerage
    mergers:merger acquisitions:acquisition takeovers:takeover buyouts:buyout
    offers:offer bids:bid companies:company corporations:corporation makers:maker
    firms:firm retailers:retailer airlines:airline carriers:carrier automakers:automaker
    carmakers:carmaker brokers:broker banks:bank factories:factory
    shops:shop lenders:lender insurers:insurer cuts:cut surpluses:surplus
    deficits:deficit barrels:barrel fields:field plants:plant
    tariffs:tariff prices:price wages:wage commodities:commodity crops:crop
    computers:computer programs:program processors:processor chips:chip
    chipmakers:chipmaker semiconductors:semiconductor servers:server
    systems:system databases:database updates:update patches:patch
    flaws:flaw vulnerabilities:vulnerability messages:message worms:worm
    viruses:virus trojans:trojan breaches:breach filters:filter passwords:password
    screensavers:screensaver keystrokes:keystroke spammers:spammer
    apps:app tools:tool devices:device phones:phone smartphones:smartphone
    cameras:camera laptops:laptop tablets:tablet consoles:console
    browsers:browser sites:site websites:website pages:page auctions:auction
    networks:network services:service providers:provider operators:operator
    emails:email downloads:download algorithms:algorithm chatbots:chatbot models:model
    robots:robot towers:tower games:game gamers:gamer publishers:publisher
    handsets:handset components:component drives:drive graphics:graphics
    scientists:scientist researchers:researcher experiments:experiment
    laboratories:laboratory studies:study trials:trial therapies:therapy treatments:treatment
    patients:patient vaccines:vaccine genes:gene genomes:genome cells:cell
    tumors:tumor mutations:mutation proteins:protein journals:journal
    fossils:fossil dinosaurs:dinosaur archaeologists:archaeologist
    astronomers:astronomer astronauts:astronaut cosmonauts:cosmonaut
    moons:moon planets:planet rovers:rover satellites:satellite probes:probe
    launches:launch rockets:rocket observatories:observatory telescopes:telescope
    comets:comet asteroids:asteroid craters:crater galaxies:galaxy
    teams:team matches:match leagues:league players:player athletes:athlete
    coaches:coach champions:champion championships:championship
    tournaments:tournament playoffs:playoff fixtures:fixture
    semifinals:semifinal quarterfinals:quarterfinal rounds:round sets:set
    seasons:season scores:score yards:yard innings:inning
    touchdowns:touchdown quarterbacks:quarterback receivers:receiver
    goals:goal pitches:pitch pitchers:pitcher homeruns:homerun homers:homer
    catches:catch kickoffs:kickoff penalties:penalty rebounds:rebound assists:assist
    wickets:wicket runs:run strokes:stroke putts:putt birdies:birdie bogeys:bogey
    medals:medal races:race titles:title records:record bouts:bout
    streaks:streak injuries:injury transfers:transfer qualifiers:qualifier
    elections:election votes:vote voters:voter ballots:ballot polls:poll
    campaigns:campaign candidates:candidate parliaments:parliament
    lawmakers:lawmaker governments:government ministers:minister
    diplomats:diplomat summits:summit treaties:treaty leaders:leader
    protests:protest protesters:protester protestors:protester
    demonstrators:demonstrator activists:activist refugees:refugee
    immigrants:immigrant migrants:migrant ambassadors:ambassador
    embassies:embassy insurgents:insurgent militants:militant
    rebels:rebel separatists:separatist guerrillas:guerrilla soldiers:soldier
    peacekeepers:peacekeeper fighters:fighter armies:army
    attacks:attack bombings:bombing bombers:bomber bombs:bomb blasts:blast
    explosions:explosion strikes:strike missiles:missile weapons:weapon
    hostages:hostage kidnappings:kidnapping kidnappers:kidnapper
    casualties:casualty deaths:death victims:victim survivors:survivor
    earthquakes:earthquake typhoons:typhoon hurricanes:hurricane
    storms:storm floods:flood wildfires:wildfire droughts:drought
    landslides:landslide aftershocks:aftershock eruptions:eruption
    arrests:arrest robberies:robbery prosecutors:prosecutor
    suspects:suspect courts:court judges:judge crimes:crime charges:charge
    gunmen:gunman shootings:shooting murders:murder prisoners:prisoner
    sentences:sentence officers:officer allegations:allegation
"""
_FORM = dict(pair.split(":") for pair in _PLURALS.split())
_FORM.update({
    "internet's": "internet",
    "soccers": "soccer",
    "cyberattacks": "cyberattack",
    "startups": "startup",
    "telecoms": "telecom",
    "cellphones": "cellphone",
    "video-games": "video game",
})

_WORD = re.compile(r"[a-z]+[0-9]+[a-z0-9]*|[0-9]+[a-z]+[a-z0-9]*|[a-z]+|[0-9]+")
_ENTITY = re.compile(r"&(?:#(x[0-9a-f]+|[0-9]+)|(amp|quot|apos|nbsp|lt|gt|dollar|pound|euro));", re.I)
_ENTITY_VALUES = {
    "amp": "&", "quot": '"', "apos": "'", "nbsp": " ", "lt": "<",
    "gt": ">", "dollar": "$", "pound": "£", "euro": "€",
}
_DOTS = re.compile(r"(?<![A-Za-z])(?:[A-Za-z]\.){2,}(?:[A-Za-z](?![A-Za-z]))?")
_WIRE = re.compile(r"\((?:reuters|ap|afp|upi|associated press|bloomberg|dow jones)\)", re.I)


def _entity_value(match):
    number, name = match.groups()
    if name:
        return _ENTITY_VALUES[name.lower()]
    try:
        value = int(number[1:], 16) if number.lower().startswith("x") else int(number)
        return chr(value) if 0 < value <= 0x10ffff else " "
    except ValueError:
        return " "


def _clean(text):
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"(?<!&)#(32|34|36|38|39|160);", r"&#\1;", text)
    text = _ENTITY.sub(_entity_value, text)
    text = re.sub(r"</?(?:b|i|p|em|strong|br|div|a|span)(?:\s+[^<>]*)?\s*/?>",
                  " ", text, flags=re.I)
    text = re.sub(r"(?:\\r\\n|\\n|\\r)", "\n", text)
    text = text.replace("\\$", "$").replace("\\'", "'")
    text = text.translate(str.maketrans("’‘‐‑‒–—", "''-----"))
    text = "".join(c for c in unicodedata.normalize("NFKD", text)
                   if not unicodedata.combining(c))
    text = _DOTS.sub(lambda m: m.group().replace(".", ""), text)
    return text


def _lexical_text(text):
    text = _WIRE.sub(" ", text).lower()
    text = re.sub(r"(?<=[a-z0-9])'s\b", "", text)
    text = text.replace("&", " and ")
    text = re.sub(r"\bhome[ -]?runs?\b", "home run", text)
    text = re.sub(r"\b(?:e|electronic)[ -]?mails?\b", "email", text)
    text = re.sub(r"\b(?:dot\s+com|web\s+site)s?\b", "website", text)
    return text


def _tokens(text):
    return tuple(_FORM.get(word, word) for word in _WORD.findall(_lexical_text(text)))


def _compile():
    entries = {}
    for label, group, weight, values in _GROUPS:
        for phrase in values.split("|"):
            key = _tokens(phrase)
            if key:
                scores = entries.setdefault(key, {})
                scores[(label, group)] = max(weight, scores.get((label, group), 0.0))
    by_start = defaultdict(set)
    for key in entries:
        by_start[key[0]].add(len(key))
    return entries, {key: tuple(sorted(value, reverse=True)) for key, value in by_start.items()}


_ENTRIES, _LENGTHS = _compile()

_DATELINE = re.compile(
    r"\b[A-Z][A-Z .,'-]{2,32}(?:(?:,\s*)?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|"
    r"Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}(?:,\s*\d{4})?)?"
    r"\s*(?:\((?:AP|AFP|Reuters|UPI|Bloomberg)\)\s*(?:--?|:)?|--\s)",
    re.I,
)
_CAPITAL_DATELINE = re.compile(
    r"\b[A-Z]{2,}(?:[ .,'-]+[A-Z]{2,}){0,4}\s*(?:,?\s*"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?"
    r"\s+\d{1,2}(?:,\s*\d{4})?)?\s*(?:\([A-Za-z .]+\)\s*-?|--\s)"
)
_SOURCE_START = re.compile(
    r"^(?:update\s*\d*|roundup\s*\d*|wrapup\s*\d*|corrected|breaking|"
    r"news alert|reuters|associated press|afp|ap)\s*(?:[-:]\s*|\s+)",
    re.I,
)
_ATTRIBUTION = re.compile(
    r"^(?:By\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\s*[,|-]\s*)"
)
_LEAD_START = re.compile(
    r"\s+(?=(?:A|An|The|In|On|At|After|With|Police|Researchers|Scientists|"
    r"Officials|Shares|Stocks)\s+[a-z])"
)


def _heading_length(text, words):
    # Descriptions frequently follow the headline without a newline.
    n = len(words)
    if n <= 13:
        return n, False
    for m in re.finditer(r"\n+|\t+|\s+[|]\s+", text[:230]):
        k = len(_tokens(text[:m.start()]))
        if 3 <= k <= 23:
            return k, True
    m = _CAPITAL_DATELINE.search(text[:220])
    if m:
        k = len(_tokens(text[:m.start()]))
        if 3 <= k <= 23:
            return k, True
    # Wire stories also use title-case place names without a leading line break.
    m = _WIRE.search(text[:210])
    if m:
        left = text[:m.start()].rstrip()
        last = re.search(r"\b(?:[A-Z][a-z]+|[A-Z]{2,})(?:[ ,]+(?:[A-Z][a-z]+|[A-Z]{2,})){0,3}[ ,]*$", left)
        end = last.start() if last else m.start()
        k = len(_tokens(text[:end]))
        if 3 <= k <= 23:
            return k, True
    m = _DATELINE.search(text[:180])
    if m and m.group()[:3].isupper():
        k = len(_tokens(text[:m.start()]))
        if 3 <= k <= 20:
            return k, True
    for m in re.finditer(r"[!?]\s+|(?<=[a-z0-9])\.\s+(?=[A-Z])", text[:175]):
        k = len(_tokens(text[:m.start()]))
        if 4 <= k <= 18:
            return k, True
    for m in _LEAD_START.finditer(text[:135]):
        k = len(_tokens(text[:m.start()]))
        if 5 <= k <= 15:
            return k, False
    return min(10, n), False


_GROUP_FACTORS = (1.0, 0.63, 0.46, 0.34, 0.27, 0.22, 0.18, 0.15, 0.12, 0.10)


def _score_features(words, heading, definite):
    by_key = {}
    for i, word in enumerate(words):
        for size in _LENGTHS.get(word, ()):
            if i + size > len(words):
                continue
            key = words[i:i + size]
            if key in _ENTRIES:
                if key in by_key:
                    old_i, count = by_key[key]
                    by_key[key] = (old_i, count + 1)
                else:
                    by_key[key] = (i, 1)
    candidate = defaultdict(list)
    for key, (i, count) in by_key.items():
        for (label, group), weight in _ENTRIES[key].items():
            candidate[label].append((i, i + len(key), group, weight, count, key))

    score = dict.fromkeys(_LABELS, 0.0)
    groups = {}
    first = {}
    for label, hits in candidate.items():
        hits.sort(key=lambda hit: (-hit[3], -(hit[1] - hit[0]), hit[0], hit[2], hit[5]))
        accepted = {}
        accepted_at = defaultdict(list)
        amounts = defaultdict(list)
        for i, end, group, weight, count, key in hits:
            is_nested = False
            for seen_i, seen_end, seen_weight in accepted_at.get(i, ()):
                if seen_i <= i and end <= seen_end and seen_weight >= weight * 0.85:
                    is_nested = True
                    break
            if not is_nested:
                accepted[(i, end, key)] = True
                for j in range(i, end):
                    accepted_at[j].append((i, end, weight))
            elif (i, end, key) in accepted:
                # An identical cue entered in two groups is not independent.
                continue
            if i < heading:
                if definite:
                    position = 1.55 if end <= heading else 1.18
                else:
                    position = 1.5 - 0.21 * i / max(1, heading)
            elif i < heading + 13:
                position = 1.11
            else:
                position = 1.0 if i < 100 else 0.88
            repeat = 1.0 + 0.08 * min(count - 1, 2)
            strength = weight * position * repeat * (0.28 if is_nested else 1.0)
            amounts[group].append(strength)
            if not is_nested:
                first[group] = min(i, first.get(group, i))
        for group, values in amounts.items():
            values.sort(reverse=True)
            total = sum(a * b for a, b in zip(values, _GROUP_FACTORS))
            groups[group] = total
            score[label] += total
    return score, groups, first


_MARKET_ROUNDUP = re.compile(
    r"\b(?:stock market|wall street|stock index|equity market|"
    r"(?:us|european|asian|tokyo|japanese|london|hong kong|global|world|"
    r"chinese|australian|indian|german|french|canadian|uk|british) stocks|"
    r"dow jones|nasdaq composite|nikkei average|ftse 100|s and p 500|"
    r"stocks (?:rose|fell|fall|rally|rallied|rise|gain|gained|drop|dropped|"
    r"climb|climbed|tumble|tumbled|end|ended|close|closed|open|opened|"
    r"surge|slump|slid|slide|slipped|jump|jumped|dip|soar|sink|mixed|lower|higher))\b"
)
_INDEX = re.compile(r"\b(?:dow|nasdaq|nikkei|ftse|s and p 500|s p 500|hang seng|cac 40|dax)\b")
_MONEY = re.compile(
    r"(?:[$€£¥]\s*\d|\b\d+(?:[.,]\d+)?\s+(?:million|billion|trillion)?\s*"
    r"(?:dollars|euros|pounds sterling|yen|yuan|cents a share|cents per share)\b)"
)
_SCORE = re.compile(r"(?<![\d.$])(?:[0-9]{1,3})\s*[-:]\s*(?:[0-9]{1,3})(?![\d.%])")
_SCORE_CONTEXT = re.compile(
    r"\b(?:beat|beats|beaten|defeat|defeats|defeated|win|wins|won|loses|lost|"
    r"loss|victory|score|scored|draw|drew|game|match|set|sets|season|record|"
    r"inning|innings|final|lead|led|points|overtime|goals|routed|thrashed|"
    r"edged|blanked|topped|upset|trailing|chance|capped|advance|advances)\b"
)
_EXCLUDED_SCORE = re.compile(
    r"\b(?:voted|vote|ruling|court|judges|jury|poll|senate|house|"
    r"referendum|lawmakers|council|parliament|committee|ratio|percent|"
    r"hours|weeks|months|years|decades|gmt|am|pm|magnitude)\b"
)
_RESULT_VERB = re.compile(
    r"\b(?:beat|beats|defeat|defeats|defeated|edges|edged|routs|routed|"
    r"trounces|trounced|downed|downs|tops|topped|holds off|knocks out|"
    r"outlasts|outlasted|ousts|ousted|clinch|clinches|clinched|"
    r"advances|advanced|wins|won|prevails|falls to|loses to)\b"
)
_FINANCIAL_EVENT = re.compile(
    r"\b(?:quarter|fiscal|earnings|profits?|revenue|shareholders?|sales|shares|"
    r"dividend|forecast|results|merger|takeover|buyout|acquisition|acquire[sd]?|"
    r"ipo|initial public offering|stake|chapter 11|bankruptcy|layoffs?|"
    r"jobs|antitrust|suit|lawsuit|sued|settlement|buy(?:s|ing)?|purchase[sd]?)\b"
)
_PRODUCT_EVENT = re.compile(
    r"\b(?:unveil(?:s|ed)?|roll(?:s|ed)? out|launch(?:es|ed)?|introduc(?:es|ed)|"
    r"upgrad(?:e|es|ed)|releas(?:e|es|ed)|new version|new model|"
    r"debuts?|announc(?:e|es|ed)|develop(?:s|ed|ing)?|prototype)\b"
)
_OIL_EVENT = re.compile(
    r"\b(?:oil|crude|brent|gasoline|fuel)\b.{0,68}\b"
    r"(?:price[ds]?|futures|barrel|inventories|oil output|demand|supplies|supply)\b"
    r"|\b(?:price[ds]?|demand|futures)\b.{0,46}\b(?:oil|crude|gasoline)\b"
)
_SCIENCE_FINDING = re.compile(
    r"\b(?:scientists?|researchers?|astronomers?|physicists?|study|studies|"
    r"analysis|experiment|test results|clinical trial)\b.{0,120}\b"
    r"(?:discover(?:y|ed|s)?|find(?:s|ing|ings)?|found|show(?:s|ed|n)?|"
    r"evidence|suggest(?:s|ed)?|reveal(?:s|ed)?|conclud(?:e|ed)|identified|"
    r"develop(?:s|ed)|detect(?:s|ed)|measure(?:s|d|ment)|link(?:s|ed)|"
    r"published|report(?:s|ed)?)\b"
)
_CONFLICT_EVENT = re.compile(
    r"\b(?:bomb|militant|rebel|troops|soldier|police|insurgent|terrorist|gunmen|"
    r"explosion|suicide|gunman|airstrike|gunfire|gunshots|shelling)s?\b"
    r".{0,105}\b(?:killed?|kills|died|dead|wounded|attack(?:s|ed)?|"
    r"raided|opened fire|explod(?:e|ed|es)|detonat(?:ed|es)|fired|"
    r"arrest(?:s|ed)?|seized|capture[ds]?)\b"
)
_GOV_EVENT = re.compile(
    r"\b(?:government|president|parliament|voters|lawmakers|cabinet|senate|"
    r"congress|court|judges|minister|opposition|leaders)\b.{0,95}\b"
    r"(?:voted?|approved|ban(?:s|ned)?|condemn(?:ed|s)?|resign(?:s|ed)?|"
    r"elected|rejected|accus(?:ed|es)|inaugurated|sworn in|pledged|"
    r"sanctions|peace talks|executive order|government policy|elections?)\b"
)
_FOOD_APPLE = re.compile(
    r"\b(?:apple(?:s)?\s+(?:harvest|crop|growers?|orchards?|juice|picking|"
    r"fruit|pie|cider)|(?:growers?|orchards?)\s+(?:of\s+)?apples|"
    r"apple(?:s)?\b.{0,35}\b(?:pears|oranges|bushel|fruit trees))\b"
)
_AMAZON_REGION = re.compile(
    r"\b(?:amazon rain ?forest|amazon basin|amazon river|amazon jungle|"
    r"amazonian|amazon forest|amazon region)\b"
)
_TECH_PRODUCT_GROUPS = (
    "software", "hardware", "internet", "security", "telecom", "games", "space"
)
_ACTIVE_SPORTS = ("fixtures", "sports_language", "leagues", "teams", "athletes")


def _interaction_scores(text, words, heading, score, groups, first):
    lower = _lexical_text(text)
    lead = lower[:420]
    top = lower[:240]
    near = heading + 3

    def strength(*names):
        return sum(groups.get(name, 0.0) for name in names)

    def early(*names):
        return any(first.get(name, len(words)) < near for name in names)

    # Index-wide reporting is about the market even if one technology stock
    # is identified as the cause of the day's movement.
    general_market = bool(_MARKET_ROUNDUP.search(top))
    if general_market:
        score["business"] += 3.0
        if len(set(_INDEX.findall(lead))) >= 2:
            score["business"] += 2.8
    if _OIL_EVENT.search(lead):
        score["business"] += 2.6
    if _MONEY.search(lead):
        if strength("corporate", "markets", "economy", "commodities", "results", "firms") >= 3:
            score["business"] += 1.0
        elif re.search(r"\b(?:price|valued|costs?|worth|invest(?:s|ment|ed)?|"
                       r"budget|sales|loan|funding|spend(?:s|ing)?)\b", lead):
            score["business"] += 0.9
    if re.search(r"\b\d+(?:\.\d+)?\s*(?:percent|per cent|%)", lead):
        if strength("results", "markets", "economy") >= 3:
            score["business"] += 0.9

    # Company-specific earnings, mergers and legal disputes are categorized
    # by sector. General company vocabulary is not itself a sector cue.
    tech_firm = groups.get("tech_firms", 0.0)
    if _FOOD_APPLE.search(lead) and not re.search(r"\b(?:iphone|ipad|macbook|apple inc)\b", lead):
        removed = min(tech_firm, 5.3)
        score["sci_tech"] -= removed
        tech_firm -= removed
        score["business"] += 2.0
    if _AMAZON_REGION.search(lead) and not re.search(r"\b(?:amazon com|aws|amazon prime)\b", lead):
        removed = min(tech_firm, 5.3)
        score["sci_tech"] -= removed
        tech_firm -= removed
    technology_focus = (
        tech_firm >= 3.2 and early("tech_firms")
        or strength("telecom", "software", "hardware", "games") >= 6.0
        and early("telecom", "software", "hardware", "games")
        or strength("internet") >= 6.0 and early("internet")
    )
    if technology_focus and not general_market and _FINANCIAL_EVENT.search(lead):
        if not (early("firms") and not early("tech_firms") and strength("firms") >= 6):
            company_finance = strength("results", "corporate", "markets")
            score["sci_tech"] += 2.6 + min(4.5, company_finance * 0.33)
            if not early("commodities", "economy"):
                score["business"] -= min(4.0, company_finance * 0.21)
    if early(*_TECH_PRODUCT_GROUPS) and strength(*_TECH_PRODUCT_GROUPS) >= 5.0:
        if _PRODUCT_EVENT.search(lead):
            score["sci_tech"] += 1.6
    if strength("research") >= 3.5 and _SCIENCE_FINDING.search(lead):
        score["sci_tech"] += 3.35
    if early("space") and strength("space") >= 6.0:
        if re.search(r"\b(?:orbit|astronaut|mission|surface|spacecraft|rover|"
                     r"capsule|lunar|telescope|space|launch)\b", lead):
            score["sci_tech"] += 1.55

    sport_anchor = strength(*_ACTIVE_SPORTS)
    if sport_anchor >= 4.2 and early(*_ACTIVE_SPORTS) and _RESULT_VERB.search(lead):
        score["sports"] += 1.6
    for m in _SCORE.finditer(lead):
        around = lead[max(0, m.start() - 45):m.end() + 40]
        if re.search(r"\b(?:ap|afp)\b\s*-\s*$", lead[max(0, m.start() - 12):m.start()]):
            continue
        if re.match(r"\s*(?:year|month|week|hour|minute|day|kilomet|mile|percent|"
                    r"billion|million|dollar)", lead[m.end():]):
            continue
        if _EXCLUDED_SCORE.search(around) and sport_anchor < 6.0:
            continue
        if sport_anchor >= 4.2 or _SCORE_CONTEXT.search(around):
            score["sports"] += 3.3 if sport_anchor >= 4.2 else 2.2
            if sport_anchor >= 4.2 and re.search(r"\d\s*-\s*\d", m.group()):
                score["sports"] += 0.7
            break
    if early("athletes", "teams", "leagues") and sport_anchor >= 8.0:
        if re.search(r"\b(?:signed|signs|traded|trades|transfer|contract|"
                     r"drafted|fired|hired|retired|retires|suspended|"
                     r"banned|injured|injury|lockout)\b", lead):
            score["sports"] += 1.45

    if strength("conflict", "crime") >= 4.5 and _CONFLICT_EVENT.search(lead):
        score["world"] += 2.35
    if strength("government", "international") >= 4.0 and _GOV_EVENT.search(lead):
        score["world"] += 1.65

    # A product maker or a club can occur only as the setting for a disaster
    # or a criminal incident, rather than being the subject of a sector story.
    if early("disaster") and strength("disaster") >= 6.0:
        if re.search(r"\b(?:crashed|plane crash|air crash|derailment|killed|"
                     r"evacuated|destroyed|landfall|sank|rescue|death toll)\b", top):
            score["world"] += 2.1
    if early("crime") and strength("crime") >= 7.0:
        if re.search(r"\b(?:murder|arrested|shot dead|robbery|sentenced|"
                     r"gunman|convicted)\b", top) and not technology_focus:
            score["world"] += 1.3

    # A named technical system and a computer-security event take precedence
    # over generic references to crime, accounts, viruses or security.
    if early("security") and strength("security") >= 6.0:
        score["sci_tech"] += 1.55

    if re.search(r"\b(?:techweb|newsfactor|infoworld|pc world|zdnet|cnet|"
                 r"slashdot|space com|ars technica)\b", lead):
        score["sci_tech"] += 1.45
    if re.search(r"\b(?:motley fool|investor business daily|marketwatch|"
                 r"financial times|business wire)\b", lead):
        score["business"] += 1.1

    score["world"] += 0.55


def predict(state) -> dict:
    if not isinstance(state, str) or not state.strip():
        return {"answer": "world"}
    text = _clean(state).strip()
    text = _SOURCE_START.sub("", text, count=1)
    text = _ATTRIBUTION.sub("", text, count=1)
    words = _tokens(text)
    if not words:
        return {"answer": "world"}
    heading, definite = _heading_length(text, words)
    score, groups, first = _score_features(words, heading, definite)
    _interaction_scores(text, words, heading, score, groups, first)
    return {"answer": max(_LABELS, key=score.get)}