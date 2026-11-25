import bisect
import re
import unicodedata

LABELS = ("world", "business", "sci_tech", "sports")

# Each entry has a topic, a family of related evidence, and a strength.
LEXICON = (
    ("sports", "competition", """
6.8: olympic games|olympics|paralympics|super bowl|world series|stanley cup|champions league|premier league|major league baseball|national football league|national basketball association|national hockey league|world cup qualifier|world cup qualifying|grand slam final|formula one|formula 1|nascar|ryder cup|kentucky derby|ncaa tournament
5.4: world cup|uefa cup|europa league|copa america|asian cup|davis cup|fed cup|billie jean king cup|australian open|french open|wimbledon|us open tennis|pga championship|tour de france|vuelta a espana|giro d italia|indianapolis 500|daytona 500|la liga|serie a|bundesliga|ligue 1|scottish premier league|little league|college football|college basketball|minor league baseball|summer games|winter games|major leagues|euro 2004|euro 2024|ncaa|nfl|nhl|nba|mlb|wnba|ufc|wbc title|six nations|ipl cricket|african cup of nations|baseball playoffs
3.9: pga|fifa|uefa|mls cup|mls soccer|us open|masters tournament|final four|fa cup|league cup|carling cup|copa libertadores|commonwealth games|pan american games|arena football|bcs standings|bowl game|exhibition game|preseason game|regular season|postseason|playoffs|playoff berth|grand prix|grand slam|rugby union|rugby league|test series|twenty20|t20 world cup
2.3: league championship|league title|quarterfinals|semi finals|semifinals|quarter finals|semifinal|quarterfinal|championships|championship|relegation|promotion race|friendly match|league match|first division|second division|division title|wild card|training camp|draft pick|first round pick|season opener|opening day|opening round|overtime|extra time|medal table
"""),
    ("sports", "play", """
6.0: scored a hat trick|scored the winning goal|scored twice|scored a touchdown|three run homer|grand slam homer|threw a no hitter|walk off homer|won the gold medal|won the silver medal|set a world record|penalty shootout|pole position|straight sets|test century|maiden century|triple double|sudden death overtime
4.7: touchdown|touchdowns|home runs|home run|homers|homer|innings|inning|starting pitcher|relief pitcher|pitching rotation|strikeouts|struck out|runs batted in|field goal|field goals|running back|quarterback|quarterbacks|wide receiver|linebacker|offensive line|defensive end|batting average|gave up runs|power play|game winning goal|winning goal|equaliser|equalizer|hat trick|own goal|red card|yellow card|free kick|penalty kick|match point|break point|tiebreak|tie break|birdie|birdies|bogey|bogeys|under par|over par|sprint finish|knocked out in the|first leg|second leg|stoppage time|extra innings|team time trial|wickets|wicket|fielded a team
3.0: scored|goalkeeper|goaltender|goals|goal scorer|striker|midfielder|defender|pitcher|catcher|batters|outfielder|shortstop|first baseman|second baseman|designated hitter|rebound|rebounds|assists|aces|rushing yards|passing yards|rushed for|yards passing|yards rushing|passing game|pulled level|drew level|clean sheet|blown save|shutout|victory over|loss to|lost to|win over|puts his side|top seed|seeded|unseeded|starting lineup|team mate|team mates|teammate|teammates|injured reserve|disabled list|club record|season high|personal best|world record holder|course record|relay team
1.7: defeated|beats|beat|outlasted|ousted|edged|routed|cruised past|advanced to|clinched|finished second|finished third|in the final|opening round|won his first|drew with|dropped to|tied for|tied with|drawn against|winning streak|losing streak|scoreless|halftime|half time|first half|second half|final round|innings victory|free agent|free agency|player transfer|transfer fee|transfer window|loan spell|roster|bench|seed|set point|set back|sets|scrimmage|practice squad
"""),
    ("sports", "sport", """
4.5: basketball|baseball|tennis|cricket|soccer|football|softball|volleyball|rugby|ice hockey|hockey|badminton|figure skating|speed skating|cross country skiing|alpine skiing|ski jumping|decathlon|triathlon|gymnastics|motorsport|auto racing|stock car racing|stock car|horse racing|thoroughbred racing|jockey|heavyweight bout|boxing match|marathon runner|touring car|professional wrestling|bobsled|bobsleigh|windsurfing
3.0: athletics|boxing|golf|golfer|golfers|swimmer|swimmers|cyclist|cyclists|sprinter|sprinters|weightlifting|marathon|skiing|snowboarding|skating|wrestling|track and field|distance runner|long jump|high jump|pole vault|pentathlon|breaststroke|freestyle relay|table tennis|water polo|road race|time trial|cup race|race driver|race winner|race car
2.4: athlete|athletes|team captain|manager of the club|head coach|assistant coach|coach|coaches|players union|player of the year|player|players|playmaker|rookie|rookies|team owner|club president|manager was sacked|gold medal|silver medal|bronze medal|medalists|medallist|doping|anti doping|title defense|defending champion|reigning champion
1.0: sports|league|leagues|teams|team|tournament|season|match|matches|contest|captain|champion|cup final|cup tie|title|bouts|games
"""),
    ("sports", "team", """
5.2: new york yankees|boston red sox|chicago white sox|chicago cubs|san francisco giants|los angeles dodgers|new york mets|oakland athletics|philadelphia phillies|atlanta braves|st louis cardinals|houston astros|texas rangers|toronto blue jays|tampa bay devil rays|tampa bay rays|san diego padres|seattle mariners|kansas city royals|pittsburgh pirates|minnesota twins|detroit tigers|cleveland indians|cleveland guardians|seattle supersonics|los angeles lakers|la lakers|los angeles clippers|boston celtics|chicago bulls|new york knicks|houston rockets|miami heat|san antonio spurs|phoenix suns|detroit pistons|golden state warriors|dallas mavericks|minnesota timberwolves|orlando magic|indiana pacers|philadelphia 76ers|new jersey nets|brooklyn nets|portland trail blazers|toronto raptors|new england patriots|dallas cowboys|philadelphia eagles|green bay packers|minnesota vikings|pittsburgh steelers|new york jets|new york giants|san francisco 49ers|indianapolis colts|seattle seahawks|buffalo bills|denver broncos|kansas city chiefs|houston texans|tennessee titans|oakland raiders|las vegas raiders|washington redskins|washington commanders|baltimore ravens|detroit lions|chicago bears|new orleans saints|st louis rams|los angeles rams|cleveland browns|miami dolphins|tampa bay buccaneers|carolina panthers|cincinnati bengals|jacksonville jaguars|san diego chargers|los angeles chargers|atlanta falcons|detroit red wings|toronto maple leafs|montreal canadiens|boston bruins|new jersey devils|new york rangers|new york islanders|edmonton oilers|ottawa senators|calgary flames|vancouver canucks|colorado avalanche|tampa bay lightning|pittsburgh penguins|san jose sharks|philadelphia flyers|washington capitals|manchester united|manchester city|man utd|real madrid|ac milan|inter milan|bayern munich|borussia dortmund|paris saint germain|sporting lisbon|athletic bilbao|atletico madrid|fc barcelona|liverpool fc|arsenal fc|chelsea fc|newcastle united|west ham|aston villa|tottenham hotspur|queens park rangers|glasgow rangers|notre dame football|red bull racing|all blacks|springboks|british and irish lions
4.1: yankees|red sox|white sox|blue jays|devil rays|dodgers|mets|astros|phillies|padres|lakers|celtics|knicks|timberwolves|pacers|trail blazers|mavericks|sixers|76ers|steelers|packers|49ers|seahawks|buccaneers|redskins|bengals|canadiens|maple leafs|red wings|canucks|hotspur|tottenham|juventus|leverkusen|deportivo la coruna|as roma|fiorentina|san lorenzo|boca juniors|crystal palace|man united|man city
2.1: chelsea|arsenal|liverpool|juve|barca|cubs|braves|vikings|broncos|colts|raptors|orioles|brewers|flyers|jaguars|raiders|mclaren|scuderia ferrari|ferrari driver|oilers|bulls|pac ten|pac 10|big ten|big 12|fighting irish|clemson|sooners|cornhuskers|tar heels|hokies|duke blue devils|razorbacks|wolverines|longhorns|aggies
"""),
    ("sports", "person", """
4.4: tiger woods|vijay singh|ernie els|phil mickelson|retief goosen|sergio garcia|michael schumacher|ralf schumacher|rubens barrichello|kimi raikkonen|juan pablo montoya|fernando alonso|jenson button|lewis hamilton|dale earnhardt|jeff gordon|jimmie johnson|roger federer|rafael nadal|serena williams|venus williams|andy roddick|andy murray|novak djokovic|andre agassi|lleyton hewitt|maria sharapova|lindsay davenport|justine henin|kim clijsters|amelie mauresmo|lance armstrong|jan ullrich|michael phelps|ian thorpe|usain bolt|lebron james|kobe bryant|shaquille o neal|shaq|allen iverson|carmelo anthony|yao ming|tim duncan|michael jordan|lionel messi|cristiano ronaldo|david beckham|wayne rooney|ronaldinho|thierry henry|alex ferguson|arsene wenger|jose mourinho|zinedine zidane|ruud van nistelrooy|derek jeter|barry bonds|alex rodriguez|pedro martinez|manny ramirez|david ortiz|roger clemens|randy johnson|ichiro suzuki|sammy sosa|peyton manning|eli manning|tom brady|brett favre|terrell owens|ricky williams|bill belichick|joe gibbs|nick saban|sachin tendulkar|brian lara|shane warne|ricky ponting|rahul dravid|muttiah muralitharan|virender sehwag
2.9: federer|roddick|sharapova|tendulkar|barrichello|schumacher|raikkonen|agassi|mickelson|beckham|ronaldo|messi|mourinho|rooney|favre|clemens|jeter|piniella|belichick|vieira|zidane
"""),
    ("business", "markets", """
6.6: stock market rally|stock market crash|stocks were|stocks rose|stocks fell|stocks rise|stocks fall|stocks slip|stocks climb|shares were mixed|wall street stocks|oil prices|crude prices|price of crude|crude oil futures|crude futures|commodity markets|bond market|currency markets|foreign exchange market
4.8: stock exchange|stock market|stock markets|wall street|dow jones|dow industrials|standard and poor s|s p 500|s p futures|nasdaq composite|nikkei|hang seng index|ftse 100|ftse index|dax index|euro stoxx|blue chips|blue chip stocks|treasury yields|bond yields|mutual funds|hedge funds|investment funds|equity markets|financial markets|market capitalization|share price|stock price|share prices|stock prices|trading session|after hours trading|profit taking|record high for oil|oil futures|barrel of crude|brent crude|west texas intermediate|opec|gold prices|gold futures|wheat futures|copper prices|oil price
3.2: nasdaq|nyse|ftse|dow|hang seng|stocks|equities|bourses|securities trading|securities exchange|investors|shareholders|dividend|dividends|market index|benchmark index|futures contract|shares fell|shares rose|shares rallied|shares jumped|junk bonds|investment bank|brokerage|market volatility|crude oil|oil production|oil output|fuel prices|petrol prices|gasoline prices|commodities|spot price|oil exports|output quotas|barrels a day|barrels per day
1.2: securities|currencies|futures|commodities trading|portfolio|trading|traded|shares|stake|bonds|stock|bullish|bearish|yield|rally|barrels|oil|brent
"""),
    ("business", "economy", """
6.4: federal reserve|interest rate decision|central bank|interest rates|unemployment rate|gross domestic product|consumer price index|balance of trade
4.7: economic growth|economic data|economic slowdown|consumer spending|consumer confidence|consumer prices|producer prices|retail sales|factory orders|industrial production|trade deficit|trade surplus|current account deficit|budget deficit|economic recession|jobless claims|jobless rate|jobs report|nonfarm payrolls|housing starts|home sales|mortgage rates|federal funds rate|bank of england|european central bank|bank of japan|international monetary fund|world bank|world trade organization|wto talks|trade talks|free trade agreement|import tariffs|export tariffs|trade dispute|trade deal|interest rate|rate hike|rate cut|monetary policy|the fed
3.1: unemployment|inflation|recession|downturn|deflation|gdp|economy|economies|labor market|labour market|budget shortfall|economic recovery|economic forecast|fiscal policy|payrolls|home prices|housing market|mortgage|mortgages|foreign investment|us dollar|u s dollar|dollar fell|dollar rose|dollar gains|weaker dollar|stronger dollar|against the dollar|against the euro|against the yen|imports|exports|tariffs|subsidies|devaluation|bank lending|trade barriers|farm subsidies
1.3: economic|jobs|wages|salaries|dollar|yen|euro|currency|taxes|government spending|tax rate|deficit|budget|fiscal|trade
"""),
    ("business", "corporate", """
6.0: quarterly earnings|quarterly profit|quarterly profits|profit warning|initial public offering|chapter 11|bankruptcy protection|hostile takeover|takeover bid|cash and stock deal|net income|earnings per share
4.9: posted a profit|reported a profit|reported a loss|operating profit|operating loss|net profit|net loss|quarterly results|quarterly revenue|quarterly sales|third quarter profit|second quarter profit|fourth quarter profit|first quarter profit|earnings forecast|revenue forecast|profit forecast|raised its forecast|annual results|annual earnings|pretax profit|after tax profit|in the red|public offering|stock offering|ipo|bankruptcy|creditors|accounting scandal|accounting fraud|insider trading|corporate governance|antitrust regulators|merger agreement|buyout offer|stock buyback|share buyback|bid to buy|filed for bankruptcy|business plans|sales outlook
3.3: earnings|profits|profit|profitability|revenues|revenue|profit margins|operating costs|sales growth|sales figures|slumping sales|strong sales|earnings estimates|earnings report|losses widened|cost cutting|job cuts|cut jobs|layoffs|lay off|redundancies|restructuring|turnaround plan|closing stores|store closings|labor costs|labour costs|union contract|labor dispute|labour dispute|credit rating|bond rating|merger|mergers|takeover|buyout|acquisition|acquisitions|bidder|chief executive|chief financial officer|chief operating officer|ceo|board of directors|shareholder meeting|corporate fraud
1.5: company|companies|corporation|firm|firms|business|businesses|sales|debt|debts|borrowers|loans|financing|financed|finance|financial|joint venture|bought|acquire|acquires|agreed to buy|agreed to sell|startup|start up|capital spending|subsidiary|partnership|reorganize|securities and exchange commission|sec filing|fiscal year|third quarter|second quarter|first quarter|fourth quarter
"""),
    ("business", "industry", """
4.9: airline industry|airline shares|low cost carrier|air carriers|air fare|airfares|plane orders|aircraft orders|orders for planes|jumbo jet order|flight attendants union|big box retailer|discount retailer|department store|retail chain|chain stores|investment banking|commercial banking|refinancing|oil cartel|automobile market|automotive industry|car maker|car makers|automobile manufacturer|auto sales|car sales|drug maker|pharmaceutical company|health insurer|insurance premiums|insurance claims|real estate market|property market|credit card company
3.2: airliner orders|airline|airlines|airways|retailer|retailers|retailing|banking|investment banker|bankers|insurance company|insurer|insurers|reinsurer|supermarket|supermarkets|automaker|automakers|carmaker|car companies|automotive|oil company|oil companies|oil giant|oil refinery|natural gas producer|power company|building society|mortgage lender|home builders|homebuilder|shipping company|steelmaker|steel makers|mining company|gold mining|retail|department stores|plane maker|aerospace group|pharmaceuticals|casino operator|hotel chain|consumer goods|manufacturer
1.3: industry|manufacturing|wholesale|retailers|supplier|suppliers|distributor|factory|factories|plants|goods|shopping|commercial|billion dollar|marketing|advertising|customers|client accounts
"""),
    ("business", "company", """
4.4: wal mart|walmart|target corp|home depot|kmart|k mart|sears roebuck|best buy|circuit city|marks and spencer|marks spencer|tesco|sainsbury|carrefour|costco|j c penney|jcpenney|woolworths|gap inc|mcdonald s|starbucks|coca cola|pepsico|pepsi cola|nestle|unilever|procter gamble|procter and gamble|kraft foods|sara lee|general mills|walt disney|time warner|news corp|viacom|berkshire hathaway|merrill lynch|goldman sachs|jpmorgan|jp morgan|morgan stanley|citigroup|citibank|bank of america|wells fargo|deutsche bank|credit suisse|lehman brothers|bear stearns|barclays|hsbc|bn p paribas|bnp paribas|ub s|ubs ag|fannie mae|freddie mac|aig|american international group|hollinger international|enron|halliburton|tyco international|altria|philip morris|ford motor|general motors|daimlerchrysler|daimler chrysler|chrysler|volkswagen|toyota|renault|peugeot|hyundai|fiat|mitsubishi motors|caterpillar inc|general electric|exxon mobil|exxonmobil|royal dutch shell|conocophillips|yukos|chevrontexaco|chevron|gazprom|petrochina|bp plc|british petroleum|rio tinto|bhp billiton|bhp group|united airlines|american airlines|us airways|u s airways|delta air lines|delta airlines|southwest airlines|continental airlines|northwest airlines|singapore airlines|british airways|air france|lufthansa|jetblue|ryanair|easyjet|qantas|alitalia|air canada|china eastern airlines|boeing|airbus|lockheed martin|northrop grumman|pfizer|merck|glaxosmithkline|astrazeneca|eli lilly|johnson johnson|johnson and johnson|bristol myers|novartis|sanofi|bayer ag
2.1: boeing co|bmw|honda|nissan|mazda|alcoa|dupont|dow chemical|macy s|martha stewart living|nabisco|kodak|sony pictures|disney|fedex|dhl|deloitte|kpmg|pricewaterhousecoopers|freddie mac|yukos oil|ups shares
"""),
    ("sci_tech", "techco", """
6.4: microsoft|microsoft corp|google|apple computer|apple inc|apple computers|international business machines|ibm|intel|advanced micro devices|hewlett packard|hewlett packard co|hp inc|dell computer|dell inc|oracle corp|oracle corporation|peoplesoft|salesforce|salesforce com|sun microsystems|nvidia|adobe systems|meta platforms|openai|deepmind|amazon web services|alphabet inc|yahoo|ebay|paypal|facebook|instagram|tiktok|linkedin|twitter|samsung electronics|taiwan semiconductor|tsmc|asml|qualcomm|broadcom|arm holdings|texas instruments|cisco systems|macromedia|mozilla|netscape|red hat|novell|symantec|mcafee|kaspersky|sophos|autodesk|vmware|docusign|snowflake inc|workday inc|servicenow|sap ag|netflix|shopify|atlassian
5.3: blackberry|research in motion|nokia|motorola|ericsson|sony ericsson|fujitsu|toshiba|nec electronics|seagate|western digital|gateway computers|emc corp|compaq|acer inc|asus|lenovo|sco group|sco lawsuit|suse|verisign|realnetworks|napster|lycos|america online|aol|myspace|spotify|snapchat|wikipedia|wikimedia|discord|blizzard entertainment|activision|electronic arts|ubisoft|nintendo|sega|square enix|capcom|rockstar games|take two interactive|valve software|lucent|nortel|alcatel|juniper networks|vodafone|verizon|at t wireless|sbc communications|bellsouth|nextel|t mobile|deutsche telekom|british telecom|telecom italia|telefonica|ntt docomo|ntt do co mo|china mobile|sk telecom|singtel|telstra|kddi|tmobile|skype|comcast|directv|echostar|sirius satellite radio|xm satellite radio|worldcom
3.7: micron technology|palmone|palmsource|acclaim entertainment|infineon|sap software|ncr corp|yahoo japan|samsung|panasonic|matsushita|lg electronics|sanyo|sony|adobe|dell|amd|cisco|mediatek|xiaomi|oppo|bytedance|huawei|baidu|tencent|alibaba|infosys|wipro|flickr|friendster|digg|reddit|youtube|vonage|qwest|virgin mobile|sprint nextel|dish network|mci inc|frontier communications
"""),
    ("sci_tech", "computing", """
6.1: operating system|windows xp|windows vista|windows 11|windows 10|windows server|mac os|mac os x|macos|ios update|android phone|android app|microsoft office|office 365|internet explorer|google chrome|apple watch|snow leopard os|ipod|iphone|ipad|itunes|imac|macbook|power mac|powerbook|linux kernel|linux|ubuntu|chrome os|chromebook|playstation|xbox|gamecube|nintendo switch|nintendo ds|game boy|psp handheld|steam deck|video game console|video game|video games|gaming console|software patch|personal computer|supercomputer|microprocessor|semiconductor|semiconductors|pentium|athlon|geforce|dual core|64 bit processor|graphics processor|computer chips|computer chip|quantum computer|quantum computing|artificial intelligence|generative ai|large language model|chatgpt|machine learning|cloud computing|virtual reality|augmented reality|blockchain technology
4.1: software|computer hardware|computer systems|computer system|computer program|computer games|computer game|computer security|cybersecurity|computers|computer|laptop|laptops|notebook computer|desktop pc|desktop computer|pc maker|pc makers|pc market|chip maker|chipmaker|chipmakers|chip design|chip industry|memory chips|memory chip|processor|processors|op teron|opteron|xeon|arm processor|chipset|apple silicon|hard disk|hard drive|flash memory|flash drive|solid state drive|disk drive|server software|blade server|open source|source code|software developer|application software|software suite|software applications|software maker|programming language|java software|java virtual machine|javascript|database software|database|enterprise software|virtualization|data center|data centre|mobile app|app store|software update|firmware|word processor|digital audio|mp3 player|portable music player|music player|digital camera|digital cameras|digital photography|digital video|digital television|digital tv|hd tv|hdtv|blu ray|dvd recorder|plasma tv|flat panel display|lcd screen|electronic book|e book reader|ebook|electronic ink|touch screen|touchscreen|inkjet printer|laser printer|3d printing|robot|robots|robotic|robotics|gaming|gamers|games console|handheld console|handheld gaming|halo 2|half life 2|grand theft auto san andreas|world of warcraft|counter strike game|pokemon|minecraft|nintendo wii
1.9: tech|tech industry|technology|technologies|technological|high tech|information technology|pc|pcs|gadget|gadgets|chips|webcam|sensors|sensor|algorithm|algorithms|apps|software company|developers|computerized|hardware|servers|server|electronic devices|devices|microchips|digital|display panel|handheld|dvd|cd rom|cds|mp3|electronics|electronic|automated|automation|video gaming|game developer|joystick|headset
"""),
    ("sci_tech", "network", """
6.0: search engine|search engines|world wide web|web browser|web browsers|internet portal|internet service provider|social media platform|mobile operating system|wi fi|wifi|wireless networking|fiber optic network|fibre optic network|voice over internet|voice over ip|internet phone|internet telephony|internet calling|voip|text messaging|instant messaging|instant messenger|online auction|online auctions|web hosting|web server|peer to peer|file sharing|filesharing|music downloads|digital music downloads|online music service|online music store|dot com|e commerce
4.2: internet|website|web site|web sites|websites|world wide web consortium|online search|web search|search results|search technology|keyword advertising|online advertising|online ads|social networking|social media|video streaming|streaming video|music streaming|streaming service|webcast|podcast|podcasting|internet access|broadband access|broadband|dsl|wireless internet|wireless network|wireless service|wireless carrier|mobile network|cellular network|cellular service|cell phone|cell phones|cellphone|mobile phone|mobile phones|mobile handset|smartphone|smartphones|handset|bluetooth|telecom|telecoms|telecommunications|phone company|phone companies|phone service|telephony|cell phone maker|satellite radio|cable modem|cable internet|optical fiber|optical fibre|network equipment|router|routers|wireless spectrum|web services|online store|domain names|domain name|blog|blogs|blogging|online retailer|email service|e mail service|webmail
1.6: cyberspace|cyber|on the web|the web|web|online|download|downloads|downloadable|downloaded|streaming|messaging|email|emails|e mail|wireless|networking|network|networks|carrier network|cellular|mobile data|4g|5g|3g|internet address|digital content|electronic mail|website traffic|on demand
"""),
    ("sci_tech", "security", """
6.4: computer virus|internet worm|computer worm|trojan horse|ransomware|malware|spyware|adware|antivirus software|anti virus software|cyber attack|cyberattack|cyber attacks|denial of service|security patch|zero day|phishing attack|keylogger|keylogging|infected computers|software vulnerability|buffer overflow|data breach|sql injection|computer hacker|computer hackers|spamming|unwanted email|unsolicited email|junk email|spam emails
4.1: antivirus|anti virus|sasser worm|mydoom|netsky|bagle worm|phishing|botnet|botnets|hackers|hacker|hacking|keystrokes|screensaver|screen saver|spammer|spammers|spam|encryption|encrypted|firewall|firewalls|data theft|computers infected|security software|security flaw|security vulnerability|computer networks|computer crime|online piracy|software piracy|digital piracy
1.4: passwords|password|passcode|security breach|identity theft|vulnerability|worm|virus|piracy|infects
"""),
    ("sci_tech", "space", """
6.7: nasa|european space agency|international space station|space station|space shuttle|space probe|space telescope|hubble telescope|hubble space telescope|james webb|mars rover|mars rovers|mars exploration|mars express|rover on mars|life on mars|lunar lander|lunar mission|space tourism|commercial spaceflight|space flight|spaceflight|spaceshipone|spacecraft|astronauts|astronaut|cosmonaut|cosmonauts|interplanetary|exoplanet|exoplanets|asteroid belt|black hole|black holes
4.4: saturn|planet mars|planet venus|planet jupiter|red planet|solar system|milky way|the moon|lunar|mars|cassini|huygens probe|huygens|comet|comets|asteroid|asteroids|near earth object|supernova|supernovae|galaxies|galaxy|astronomy|astronomer|astronomers|telescope|space x|spacex|blue origin|rocket launch|launch vehicle|space launch|rocket booster|satellite launch|satellite launched|orbital flight|into orbit|earth orbit|soyuz|moon landing|moon rocks|space mission|manned mission|unmanned mission|privately funded rocket|x prize|weightlessness|microgravity
1.7: extraterrestrial|planetary|eclipse|solar flare|cosmic|planet|planets|orbit|orbital|space|satellite|satellites|rocket|observatory
"""),
    ("sci_tech", "research", """
5.7: stem cell research|stem cells|embryonic stem cells|human genome|genome sequencing|gene sequencing|gene therapy|genetic engineering|genetically modified|clinical trial|clinical trials|randomized trial|medical research|scientific study|scientific research|published in nature|published in science|new england journal of medicine|journal of the american medical association|peer reviewed study|archaeological discovery|particle accelerator|large hadron collider|fusion reactor|nuclear fusion|gravitational waves|quantum mechanics|dark matter|human cloning|cloning experiment|cloned embryo
4.2: researchers found|researchers report|scientists found|scientists discovered|scientists say|scientists have|study finds|research suggests|study published|research team|laboratory tests|lab experiments|lab tests|test subjects|published in the journal|researchers at|proof of concept|breakthrough in|national institutes of health|scientific journal|geological survey|paleontologists|archaeologists|physicists|biologists|geneticists|neuroscientists|epidemiologists|fossil|fossils|dinosaur|dinosaurs|neanderthal|neanderthals|dna|genome|genomes|genetic mutation|genes|genetics|gene|genetically|protein structure|cancer cells|tumor cells|new vaccine|flu vaccine|new treatment|experimental treatment|experimental drug|vaccine trial|drug trial|vaccine development|antibodies|test vaccine|alzheimer s disease|parkinson s disease|breast cancer risk|diabetes risk|ozone layer|climate models|global warming|renewable energy technology|solar cells|fuel cell|fuel cells|hydrogen fuel cell|hydrogen powered|electric vehicle battery|self driving|driverless car|autonomous vehicle|nanotube|nanotechnology|graphene
2.1: science|scientist|scientists|researcher|researchers|laboratory|labs|biotechnology|biotech|study found|studies show|the study|new study|in a study|statistically significant|experiment|experiments|particle physics|skeleton|excavation|species|rainforest ecosystem|extinct|extinction|biodiversity|climatologists|climate change|atmosphere|emissions research|carbon dioxide|glaciers|coral reef|fossil fuel technology|brain activity|blood pressure|cancer research|carcinogen|vaccines|vaccine|immunization|cholesterol|patients treated|therapy|therapies|medical journal|medicine|diagnostic test|biological|bacteria|pathogen|antibiotic|antibiotics|pandemic research|magnetic resonance|new drug|scientific|engineers developed|prototype
"""),
    ("world", "government", """
6.0: presidential election|general election|parliamentary election|parliamentary elections|presidential campaign|election results|coalition government|prime minister|opposition leader|palestinian authority|un security council|united nations security council|un general assembly|un peacekeepers|united nations|international criminal court|world leaders
4.6: elections|election campaign|election|polling stations|voting booths|polling station|ballot box|ballots|exit polls|voter turnout|election commission|presidential debate|political party|opposition party|opposition parties|ruling party|ruling coalition|party convention|republican national convention|democratic national convention|democratic nominee|democratic candidate|republican candidate|electoral college|presidential race|political campaign|presidential candidate|parliament|house of commons|house of representatives|u s senate|foreign minister|foreign ministry|interior minister|defence minister|defense minister|foreign secretary|secretary of state|president elect|vice president|presidential palace|national assembly|white house|downing street|kremlin|human rights|civil rights|political asylum|asylum seekers|government officials|public officials|state of emergency|state visit|peace summit|red cross|diplomatic relations|diplomatic row|nongovernmental organization|political prisoners
2.8: chancellor|diplomats|diplomat|diplomatic|embassy|embassies|ambassadors|ambassador|president|presidential|premier|governor|mayor|cabinet ministers|cabinet|minister|lawmakers|legislators|legislature|senate|senator|senators|congressman|congresswoman|congressional|congress|democrats|republicans|democratic party|republican party|conservative party|labour party|tory|gop|electoral|referendum|campaign trail|voters|ballot|vote|voting|challenger|incumbent|opposition|protesters|protestors|political crisis|politics|political|immigration|constitution|constitutional|unconstitutional|legislation|legislative|national security|government|governments|public policy|reform bill|embargo|sanctions|arms embargo|nato|european union|eu summit|african union|arab league summit|power sharing
1.2: protests|protest|ministry|administration|activists|leader|leaders|officials|rally against|law|legislative bill|partisan|reform|democracy|privacy law|regulation|administrative order|executive order|legally
"""),
    ("world", "conflict", """
6.4: suicide bombing|suicide bomber|car bomb|car bombing|roadside bomb|terrorist attack|hostage crisis|armed conflict|civil war|war crimes|peace talks|cease fire|ceasefire|weapons of mass destruction|nuclear weapons program|iraq war|war in iraq|u s troops|american troops|israeli troops|israeli forces|israeli army|gaza strip|west bank settlements|occupied territories|osama bin laden|al qaeda|al qaida
4.8: bomb blast|bomb attacks|bomb attack|bombings|bombing|militants|militant groups|insurgent attack|insurgency|insurgents|rebels|guerillas|guerrillas|troops|peacekeeping|peacekeepers|peace process|peace agreement|peace accord|peace deal|air strikes|air strike|airstrikes|artillery fire|exchanged fire|opened fire|gun battle|security forces|coalition forces|us forces|u s forces|us military|u s military|iraqi forces|army offensive|army base|military offensive|missile strike|missile test|ballistic missile|nuclear arms|nuclear disarmament|nuclear talks|nuclear program|nuclear programme|terrorism|terrorist|terrorists|bin laden|taliban|hezbollah|hizbollah|hamas|islamic jihad|isis militants|rebel group|separatist rebels|separatists|armed men|hostage|hostages|west bank|gaza|palestinians|israeli palestinian|refugee camp|refugees|humanitarian crisis|genocide|ethnic cleansing|mass graves|mass grave|massacre
2.4: military|army|soldiers|marines|navy|air force|armed forces|battalion|bomb|bombs|explosions|explosion|gunfire|gunmen|gunman|warplanes|missiles|rockets fired|fighting between|fierce fighting|clashes|clashed|war|wars|battlefield|occupation|resistance fighters|kidnapped|kidnapping|assassination|violence|invaded|invasion|detainees|war prisoner|an act of terrorism|weapons inspectors|nuclear threat
"""),
    ("world", "disaster", """
6.2: plane crash|airliner crash|helicopter crash|air crash|train derailment|derailed train|flash flood|flash floods|tropical storm|forest fire|brush fire|mining accident|mine explosion|mine collapse|mudslide|mudslides|humanitarian aid|death toll|rescue workers|search and rescue|hurricane warning|storm surge|tsunami|tsunamis|deadly earthquake|raging wildfire|wildfire evacuation|bridge collapse
4.6: earthquake|earthquakes|hurricane|hurricanes|typhoon|typhoons|cyclone|tornado|tornadoes|floodwaters|flooding|floods|wildfire|wildfires|bushfire|volcanic eruption|landslide|landslides|heat wave|blizzard|snowstorm|rescue crews|disaster relief|natural disaster|disaster area|evacuated|evacuation|missing feared dead|people missing|people were killed|people were injured|people were rescued|bodies recovered|state of disaster|severe storm|oil spill|chemical spill|passengers aboard|aircraft crashed|crashed into
2.1: disaster|storm|injured|injuries|deadly|survivors|fatalities|killed|stranded|swept away|destroyed homes|flood|aftershocks|magnitude quake|richter scale|quake|collapsed|collapse|levees|wreckage|derailed|crash|crashed|firefighters|fire broke out|rescuers|rescued|power outage|power outages|missing passengers|village was destroyed|famine|drought|disease outbreak|outbreak
"""),
    ("world", "crime", """
6.0: criminal charges|police arrested|police said|murder trial|murder suspect|death penalty|sentenced to life|sentenced to death|armed robbery|mass shooting|serial killer|drug trafficking|drug cartel|organized crime|organised crime|domestic violence|pleaded guilty|pleaded not guilty|prison sentence
4.3: police|prosecutor|prosecutors|murdered|murder|murders|homicide|manslaughter|arrested|arrests|arrest warrant|suspect was|suspects|jail term|prison term|jailed|prisoners|prison|inmates|sentenced|sentencing|convicted|conviction|acquitted|jury found|grand jury|found guilty|accused of killing|shooting spree|shot dead|shot and killed|shooting|stabbing|stabbed|robbery|robberies|robbed|abducted|abduction|hijacking|hijacked|smuggling|trafficking|drug lord|gang members|crime scene|sexual assault|sexual abuse|rape|charged with|held in custody|in custody|indicted|indictment|criminal investigation|criminal court|crimes|crime
2.0: lawsuit|sued|sues|trial|verdict|court|courts|supreme court|appeals court|federal judge|judge|jury|fraud|scam|scandal|allegations of abuse|assault|prosecution|investigators|suspect|execution|executed|arrest|jail|killing|killings
"""),
    ("world", "actor", """
4.1: george w bush|president bush|john kerry|senator kerry|tony blair|vladimir putin|viktor yushchenko|viktor yanukovych|john howard|mark latham|jacques chirac|gerhard schroeder|ariel sharon|yasser arafat|mahmoud abbas|saddam hussein|ayad allawi|kofi annan|hamid karzai|pervez musharraf|fidel castro|hugo chavez|robert mugabe|kim jong il|kim jong un|silvio berlusconi|john edwards|dick cheney|colin powell|condoleezza rice|donald rumsfeld|barack obama|joe biden|donald trump|kamala harris|nelson mandela|thabo mbeki|mahmoud ahmadinejad|benjamin netanyahu|emmanuel macron|boris johnson|rishi sunak|volodymyr zelensky|xi jinping|sudanese refugees|united nations officials
2.2: kerry|arafat|chirac|blair|putin|karzai|musharraf|castro|chavez|schroeder|berlusconi|rumsfeld|cheney|obama|zelensky|saddam|netanyahu|fallujah|najaf|baghdad|darfur|chechnya|beslan|basra|kabul|ramallah|guantanamo|abu ghraib
1.0: iraq|iraqi|iraqis|afghanistan|afghan|afghans|north korea|pyongyang|iran|iranian|israel|israeli|palestinian|sudan|sudanese|haiti|haitian|ukraine|ukrainian|kosovo|syria|yemen|un envoy|un chief|un report
"""),
)

WORD = re.compile(r"[^\W_]+")
SOURCE = re.compile(
    r"\((?:reuters|ap|afp|associated press|upi|dpa|pa|xinhuanet|xinhua|bloomberg|ansa|kyodo)\)"
    r"|\b(?:reuters|associated press|afp|bloomberg|xinhua)\s*[-–—]",
    re.I,
)
TAGS = re.compile(r"</?(?:b|i|p|em|strong|br|div|a|span|h[1-6])\b[^>]*>", re.I)
ENTITY = re.compile(r"&(#x[0-9a-f]+|#[0-9]+|[a-z]+);|(?<!\w)#(39|36|34);", re.I)
ENTITY_NAMES = {
    "amp": "&", "lt": "<", "gt": ">", "quot": '"', "apos": "'", "nbsp": " ",
    "mdash": "—", "ndash": "–", "rsquo": "'", "lsquo": "'", "rdquo": '"',
    "ldquo": '"', "dollar": "$", "pound": "£", "euro": "€",
    "percnt": "%", "hellip": "...", "trade": " ", "reg": " ", "copy": " ",
}
TREE = {}
for category, family, lines in LEXICON:
    for line in lines.strip().splitlines():
        strength, expressions = line.split(":", 1)
        strength = float(strength)
        for expression in expressions.strip().split("|"):
            node = TREE
            for word in expression.strip().split():
                node = node.setdefault(word, {})
            node.setdefault(None, []).append((category, family, strength, expression.strip()))


def decode_entity(match):
    code = (match.group(1) or "#" + match.group(2)).lower()
    if code.startswith("#") and len(code) < 10:
        try:
            number = int(code[2:], 16) if code.startswith("#x") else int(code[1:])
            if 0 <= number <= 0x10ffff:
                return chr(number)
        except ValueError:
            pass
    return ENTITY_NAMES.get(code, " ")


def normalize(text):
    for _ in range(2):
        text = ENTITY.sub(decode_entity, text)
    text = re.sub(r"<br\s*/?>|</p\s*>|</h[1-6]\s*>", "\n", text, flags=re.I)
    text = TAGS.sub(" ", text)
    text = text.replace("\\n", "\n").replace("\\r", "\n").replace("\\", " ")
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c))


# Contextual and grammatical signals. Patterns here use token-spaced text;
# punctuation-sensitive shapes are handled separately.
PATTERN_SPECS = (
    ("sports", "play", 4.8, "match result",
     r"\b(?:won|win|lost|loss|beat|beats|beating|defeated|downed|edged|routed|tied|drew|victory|fell|swept)\b"
     r"(?: [a-z]+){0,7} \d{1,3} \d{1,3}\b"),
    ("sports", "play", 4.3, "point performance",
     r"\b(?:had|scored|tallied|added|knocked in|gave up|threw for|ran for|hit|made|recorded|finished with)"
     r"(?: [a-z]+){0,3} \d{1,3} (?:points|goals|assists|rebounds|yards|touchdowns|home runs|homers|runs|wickets|strikeouts|saves|aces)\b"),
    ("sports", "play", 4.4, "fixture action",
     r"\b(?:won|wins|lost|loses|took|takes|captured|clinched|sealed|secured|reached|advanced to|reaches|into)"
     r"(?: [a-z0-9]+){0,5} (?:quarterfinals|semifinals|quarter finals|semi finals|playoffs|playoff berth|"
     r"the final|the finals|the title|the pennant|the gold|gold medal|silver medal|bronze medal|final set|final round)\b"),
    ("sports", "play", 4.0, "squad move",
     r"\b(?:signed|signs|traded|trades|benched|acquired|released|drafted|called up)"
     r"(?: [a-z0-9]+){0,5} (?:forward|guard|center|centre|quarterback|midfielder|striker|pitcher|receiver|defender|goalkeeper|outfielder|shortstop|free agent|rookie)\b"),
    ("sports", "play", 3.6, "playing conditions",
     r"\b(?:top|bottom|start|end|rest|opening|first|second|third|fourth|final|ninth|eighth|seventh)"
     r"(?: [a-z]+){0,2} (?:inning|innings|set|lap|period|half|quarter|game|round|leg) (?:of the match|of play|of the game|of the season|against|lead|lead over)\b"),
    ("sports", "play", 3.1, "player injury",
     r"\b(?:miss|misses|will miss|out for|return to|sidelined for) (?:[a-z0-9]+ ){0,4}(?:game|games|season|match|matches|weeks with|months with)\b"),
    ("sports", "sport", 3.7, "sport bracket",
     r"\b(?:men|women|boys|girls) s (?:singles|doubles|final|quarterfinal|semifinal|100 meters|100 metres|200 meters|200 metres|400 meters|400 metres)\b"),
    ("business", "corporate", 4.8, "reported results",
     r"\b(?:reported|posted|posts|reports|announced|said|recorded|earned) (?:[a-z0-9]+ ){0,6}(?:profit|profits|quarterly loss|net loss|net income|earnings|revenue) (?:of|rose|fell|increased|declined|dropped|for|jumped|tumbled|was|were|at|to|more|less|up|down)\b"),
    ("business", "corporate", 3.9, "change in results",
     r"\b(?:profit|profits|earnings|revenues|revenue|sales|income|operating loss|net loss) (?:[a-z]+ ){0,2}(?:rose|grew|soared|jumped|plunged|fell|climbed|was down|were down|was up|were up|doubled|tripled|halved|shrank|tumbled|surged|declined|dropped|slid|slipped|cut|forecast)\b"),
    ("business", "corporate", 3.7, "deal announcement",
     r"\b(?:agreed|offered|offers|plans|bid|bids|deal|agreement|approves|approved|proposal) (?:[a-z0-9]+ ){0,4}(?:to buy|to acquire|to purchase|to merge|to sell|the merger|the takeover|the buyout|its stake)\b"),
    ("business", "corporate", 3.1, "quarter reporting",
     r"\b(?:for the|in the|during the|its) (?:first|second|third|fourth|latest|fiscal|last|current|next) quarter\b"),
    ("business", "markets", 5.6, "market moves",
     r"\b(?:stocks|stock markets?|stock indexes|equities|dow|nasdaq|nikkei|ftse|major indexes|crude oil prices|oil futures|treasuries)"
     r" (?:[a-z]+ ){0,3}(?:rose|gain|gained|fall|fell|drop|dropped|jumped|slumped|climbed|finished|rebounded|rallied|slid|slipped|soared|settled|closed|mixed|opened|tumbled|were higher|were lower|inch higher|inch lower|close higher|close lower|higher|lower|edge up|edge down)\b"),
    ("business", "markets", 4.0, "shares move",
     r"\b(?:stock|shares|bonds|the dollar|euro|the yen) (?:[a-z]+ ){0,2}(?:rose|gained|declined|fell|dropped|jumped|slumped|climbed|slid|slipped|soared|closed|opened|tumbled|surged|traded|are up|are down)\b"),
    ("business", "markets", 3.6, "oil pricing",
     r"\b(?:a|per) barrel\b|\b(?:barrels of|price of|prices of) (?:us |u s )?(?:oil|crude|petroleum)\b"),
    ("business", "economy", 3.7, "trade negotiations",
     r"\b(?:trade|export|import) (?:[a-z]+ ){0,2}(?:negotiators|negotiations|agreement|agreements|restrictions|quota|quotas|surplus|tariffs|duties|sanctions)\b"),
    ("sci_tech", "security", 4.7, "digital infection",
     r"\b(?:virus|worm|trojan|infected|infecting|infects|security flaw|security hole|steals|stealing|masquerading)"
     r"(?: [a-z0-9]+){0,10} (?:emails?|e mail|windows|screensaver|keystrokes|passwords?|files|computers?|attachments?)\b"),
    ("sci_tech", "security", 4.6, "digital intrusion report",
     r"\b(?:hacked|breached|attacked|compromised|infected)(?: [a-z0-9]+){0,5} (?:servers?|computers?|software|network|networks|website|web site|windows|passwords?|accounts|emails?)\b"),
    ("sci_tech", "computing", 3.8, "technology release",
     r"\b(?:launches|launched|released|releases|unveiled|unveils|announces|announced|introduced|rolled out|rolls out)"
     r"(?: [a-z0-9]+){0,9} (?:software|processors?|smartphones?|mobile phones?|cell phones?|handsets?|apps?|"
     r"operating system|computer chips?|tablets?|laptops?|pcs|new chip|video game|games console|gaming console|new browser|new search engine|wireless service|online service)\b"),
    ("sci_tech", "research", 4.9, "experimental outcome",
     r"\b(?:scientists|researchers|astronomers|physicists|a team of scientists|engineers) (?:[a-z0-9]+ ){0,6}"
     r"(?:discovered|developed|identified|detected|observed|sequenced|demonstrated|invented|mapped|cloned|have found|built a new|uncovered)\b"),
    ("sci_tech", "research", 4.2, "medical outcome",
     r"\b(?:found|finds|reduce|reduces|reduced|lower|lowers|increases|increased|higher|less|greater)"
     r"(?: [a-z0-9]+){0,6} (?:risk of (?:cancer|a heart attack|heart disease|diabetes|stroke|dementia|developing)|survival rates?|blood pressure|cholesterol levels)\b"),
    ("sci_tech", "research", 3.4, "experimental method",
     r"\b(?:experiment|experiments|patients|animals|mice|subjects|volunteers|specimens) (?:[a-z0-9]+ ){0,7}(?:placebo|underwent|randomly assigned|cell samples|specimens|control group|study found|biopsies|genetic markers|scans)\b"),
    ("world", "government", 4.7, "election action",
     r"\b(?:run for|running for|runs for|elected|re elected|voted|vote|voting|resigned as|resigns as|sworn in as|took office as)"
     r"(?: [a-z0-9]+){0,5} (?:president|senator|governor|mayor|chancellor|parliament|prime minister|office|congress)\b"),
    ("world", "government", 3.7, "political action",
     r"\b(?:president|prime minister|parliament|senate|congress|government|ministry) (?:[a-z]+ ){0,6}"
     r"(?:vetoed|proposed legislation|resigned|resigns|passed a bill|called an election|"
     r"ordered an inquiry|declared a state of|dissolved parliament|faces a vote|won re election)\b"),
    ("world", "conflict", 4.7, "conflict action",
     r"\b(?:troops|soldiers|militants|insurgents|rebels|army|terrorists|gunmen) (?:[a-z0-9]+ ){0,6}"
     r"(?:were killed|bombed|kidnapped|fired|shot|attacked|raided|stormed|ambushed|seized|opened fire|took hostages|launched an offensive|withdrew)\b"),
    ("world", "disaster", 4.8, "disaster casualties",
     r"\b(?:killed|died|missing|injured|feared dead|dead) (?:[a-z0-9]+ ){0,7}"
     r"(?:in a fire|in a crash|in the crash|in an air crash|in a plane crash|after a crash|in the earthquake|"
     r"in the storm|in floods|in flooding|in a landslide|after the quake|in the floods|when a plane|when a train|when a ferry)\b"),
    ("world", "crime", 4.1, "police action",
     r"\b(?:police|detectives|investigators|prosecutors) (?:[a-z0-9]+ ){0,7}(?:arrested|arrest|charged|are investigating|searched|raided|"
     r"questioned|detained|have identified|opened an investigation|found the bodies)\b"),
)

PATTERNS = tuple((cat, fam, val, key, re.compile(pat))
                 for cat, fam, val, key, pat in PATTERN_SPECS)

SCORELINE = re.compile(r"(?<![\d\w])(\d{1,3})\s*[-–—:]\s*(\d{1,3})(?![\d\w])")
MONEY = re.compile(
    r"[$€£¥]\s*\d[\d,.]*(?:\s*(?:billion|million|trillion|bn)\b)?"
    r"|\b\d[\d,.]*\s+(?:(?:million|billion|trillion)\s+)?(?:dollars|euros|yen)\b",
    re.I,
)
PERCENT = re.compile(r"\d[\d,.]*\s*(?:%|percent\b|per\s+cent\b)", re.I)
NETWORK_COMPANIES = re.compile(r"\b(?:telecoms?|telecommunications|wireless carriers?|mobile operators?|phone compan(?:y|ies)|cellular carriers?)\b")
FINANCE_HOOK = re.compile(
    r"\b(?:earnings|profits?|revenue|sales|quarterly|quarter|shares|stock|ipo|initial public offering|"
    r"financial results|forecast|dividends?|buybacks?|takeover|acquisition|merger|buyout|bankrupt(?:cy)?|"
    r"acquir(?:e[sd]?|ing)|buy(?:ing|s)?|agreed to sell|purchase[d]?|bid|stake|"
    r"invest(?:s|ed|ment|ing)|launches|contract|chief executive|ceo|layoffs?|job cuts|"
    r"antitrust|lawsuit|suit|sue[sd]?|settlement|litigation|court|patents?|fines?|fined|regulators)\b"
)
CROP = re.compile(
    r"\b(?:apple (?:crop|crops|growers|orchard|orchards|juice|cider|trees|harvest|pie|picking)|"
    r"apple and pear|apples and oranges|big apple)\b"
)
PHYSICAL_AIR = re.compile(
    r"\b(?:airliner|airplane|aircraft|airbus|boeing|passenger jet|commercial jet|helicopter|plane|"
    r"flight|jetliner|airlines?|airways)\b"
)
ACCIDENT = re.compile(
    r"\b(?:crashed|crash|wreckage|hijacked|hijacking|went down|went missing|forced landing|emergency landing|"
    r"bodies recovered|crash victims|crash site|fatal accident)\b"
)
MARKET_LEAD = re.compile(
    r"\b(?:wall street|world stocks|us stocks|u s stocks|european stocks|asian stocks|japanese stocks|"
    r"stocks (?:rise|fall|jump|drop|climb|slip|rally|slide|gain|mixed|end|close|open|edge)|"
    r"stock markets?|dow jones|the dow|nasdaq composite|nikkei|ftse 100|"
    r"crude(?: oil)? (?:price|prices|futures)|oil (?:price|prices|futures))\b"
)
MATCH_VERBS = re.compile(
    r"\b(?:beat|beats|beating|lost|loses|defeated|defeat|won|win|wins|draw|drew|edged|"
    r"trounced|outlasted|scored|clinched|advanced|routed|tied|lead|leads|victory)\b"
)
TITLE_EVENT = re.compile(
    r"\b(?:season|game|games|match|matches|goals?|team|teams|cup|series|points|sets|league|"
    r"semifinals|quarterfinals|finals|playoffs|title|medal|race|coach|player|open|"
    r"homers?|tournament|roster|injury|pennant|record)\b"
)
TEAM_CASE = re.compile(
    r"\b(?:Giants|Cardinals|Rangers|Tigers|Royals|Pirates|Reds|Nationals|Indians|Twins|"
    r"Mariners|Rockies|Expos|Senators|Flyers|Penguins|Panthers|Lions|Bears|Eagles|Hawks|"
    r"Spurs|Suns|Rockets|Heat|Nets|Magic|Jazz|Warriors|Wizards|Jets|Bills|Chiefs|"
    r"Cowboys|Packers|Vikings|Texans|Chargers|Dolphins|Falcons|Titans|Ravens|Browns|"
    r"Saints|Rams|Patriots|Hurricanes|Lightning|Devils|Blues|Predators|Sharks|Canucks|"
    r"United|City|Rangers|Celtic|Reds|Gunners|Wolves|Cavaliers|Kings|Clippers)\b"
)
GOV_PUBLIC = re.compile(
    r"\b(?:election|elections|voters|referendum|parliament|prime minister|voted|opposition party|"
    r"ceasefire|peace talks|presidential|troops|rebels|militants|human rights|protesters|"
    r"political|arms talks|diplomats|constitution|veto|inauguration|cabinet|diplomatic)\b"
)
GENERIC_STUDY_TOPICS = re.compile(
    r"\b(?:consumer confidence|polling|voters|election|economic growth|economic survey|consumer spending|"
    r"school funding|public opinion|opinion poll|house prices|retail sales|gasoline prices|corporate spending|"
    r"neighborhood crime|crime rates|police statistics|housing market|income inequality|wage growth)\b"
)


def get_heading_end(text, spans):
    marker = SOURCE.search(text)
    if marker and marker.start() < 210:
        end = marker.start()
        front = text[:end]
        # AP-style datelines may be attached to the end of a headline.
        if front.rstrip().endswith(","):
            front = front.rstrip()[:-1]
        dateline = re.search(r"(?:^|\s)(?:[A-Z]{2,}[A-Z.,'\-]*\s*){1,4}$", front)
        if dateline:
            end = dateline.start()
        count = bisect.bisect_left(spans, end)
        if 3 <= count <= 25:
            return count
    m = re.search(r"\S[^\n]*\n", text)
    if m and m.end() < 190 and text[m.end():].strip():
        count = bisect.bisect_left(spans, m.end())
        if 2 <= count <= 24:
            return count
    return 0


def weight_at(index, heading):
    if heading and index < heading:
        return 1.48 if index < 7 else 1.34
    begin = heading or 0
    offset = index - begin
    if offset < 7:
        return 1.29 if not heading else 1.13
    if offset < 17:
        return 1.15 if not heading else 1.07
    if offset < 33:
        return 1.04
    if offset < 62:
        return 0.94
    return 0.84


def add_signal(records, category, family, val, name, start, end, heading):
    evidence = (val * weight_at(start, heading), val, family, name, start, end)
    old = records[category].get(name)
    if old is None or old[0] < evidence[0]:
        records[category][name] = evidence


def select_signals(records):
    ordered = sorted(records.values(), reverse=True)
    kept = []
    for e in ordered:
        _, _, _, _, start, end = e
        if any(k[4] <= start and end <= k[5] and (k[4] < start or end < k[5])
               for k in kept):
            continue
        kept.append(e)
    return kept


def evidence_score(evidence):
    multipliers = (1.0, 0.80, 0.66, 0.53, 0.43, 0.35, 0.28, 0.23,
                   0.19, 0.15, 0.12, 0.10, 0.08, 0.065, 0.05, 0.04)
    score = 0.0
    family_counts = {}
    for e, mul in zip(evidence, multipliers):
        family = e[2]
        count = family_counts.get(family, 0)
        family_counts[family] = count + 1
        # Repetition within one narrow aspect matters less than several
        # mutually consistent types of information.
        score += e[0] * mul * (1.0 if count < 2 else 0.84 if count < 4 else 0.69)
    return score


def family_peak(evidence, families, stop=None):
    return max((e[1] for e in evidence
                if e[2] in families and (stop is None or e[4] < stop)), default=0.0)


def first_strong(evidence, families, threshold):
    return min((e[4] for e in evidence if e[2] in families and e[1] >= threshold),
               default=1000000)


def raw_pos(spans, point):
    return max(0, bisect.bisect_right(spans, point) - 1)


def predict(state):
    text = normalize(state)
    matches = list(WORD.finditer(text))
    if not matches:
        return {"answer": "world"}
    raw_words = [m.group() for m in matches]
    words = [w.casefold() for w in raw_words]
    spans = [m.start() for m in matches]
    heading = get_heading_end(text, spans)
    lead_end = max(24, heading + 13)
    core_end = heading if heading >= 5 else min(12, len(words))
    body = " ".join(words)
    lead = " ".join(words[:lead_end])
    core = " ".join(words[:core_end])
    span_b = []
    p = 0
    for word in words:
        span_b.append(p)
        p += len(word) + 1
    records = {label: {} for label in LABELS}

    for start, word in enumerate(words):
        node = TREE.get(word)
        end = start + 1
        while node is not None:
            for cat, fam, val, key in node.get(None, ()):
                if key == "aig" and raw_words[start] != "AIG":
                    continue
                if key == "dow" and raw_words[start].islower():
                    if not re.search(r"\b(?:stocks|nasdaq|index|jones|shares|points|wall street)\b", lead):
                        continue
                if key == "mars" and end < len(words) and words[end] in ("inc", "candy", "chocolate"):
                    continue
                if key == "arsenal" and not re.search(r"\b(?:team|league|club|chelsea|united|football|match|against|wenger|premiership|gunners|henry|beat|goal|win|champions|arsenal fc)\b", body):
                    continue
                if key == "blackberry" and end < len(words) and words[end] in ("pie", "jam", "crop"):
                    continue
                add_signal(records, cat, fam, val, key, start, end, heading)
            if end == len(words):
                break
            node = node.get(words[end])
            end += 1

    for cat, fam, val, key, pattern in PATTERNS:
        match = pattern.search(body)
        if match:
            start = raw_pos(span_b, match.start())
            end = bisect.bisect_left(span_b, match.end())
            add_signal(records, cat, fam, val, key, start, end, heading)

    tech_neighbors = re.compile(
        r"\b(?:computer|computers|mac|macs|iphone|ipod|ipad|itunes|software|laptop|chip|chips|"
        r"semiconductor|internet|servers?|java|linux|microsoft|cloud|mobile|web|online|device|"
        r"devices|data center|database|ebooks?|kindle|e reader|prime video|aws)\b"
    ).search(body)
    finance_hook = FINANCE_HOOK.search(lead)
    for i, word in enumerate(words):
        nxt = words[i + 1:i + 4]
        prev = words[i - 1] if i else ""
        original = raw_words[i]
        near = " ".join(words[max(0, i - 4):i + 6])
        fam = "techco"
        val = 0
        if word == "apple" and not CROP.search(near):
            if (original in ("Apple", "APPLE") or
                re.search(r"\bapple (?:s |inc |computer )?(?:watch|music|pay|store|vision pro|silicon|mac|earnings|shares|stock|releases|launches)\b", near) or
                (tech_neighbors and (i < 5 or nxt[:1] in (["s"], ["computer"], ["inc"])))):
                if tech_neighbors or (i < 17 and finance_hook) or re.search(
                    r"\bapple (?:s )?(?:unveils|unveiled|introduces|introduced|says|announced|announces|"
                    r"releases|released|launches|adds|store|music|pay|vision|watch|computer|inc)\b", near
                ):
                    val = 6.3
                elif original in ("Apple", "APPLE") and i < 3 and len(words) <= 5 and not nxt[:1] == ["tree"]:
                    val = 3.2
        elif word == "oracle":
            if original in ("Oracle", "ORACLE") or tech_neighbors or finance_hook:
                val = 6.1
        elif word == "amazon":
            if not re.search(r"\b(?:amazon river|amazon basin|amazon rainforest|amazon forest|the brazilian amazon)\b", near):
                if nxt[:1] == ["com"] or tech_neighbors or (
                    original in ("Amazon", "AMAZON") and (finance_hook or i < 3)
                    and not re.search(r"\b(?:rainforest|deforestation|indigenous|jungle|tributary)\b", lead)
                ):
                    val = 5.5
        elif word == "sun" and original in ("Sun", "SUN"):
            if tech_neighbors or re.search(r"\bsun (?:s )?(?:microsystems|java|servers|unveils|shares|earnings|software|buyout|acquires)\b", near):
                if not re.search(r"\b(?:the sun|sun journal|sun times|sun herald|solar system|newspaper)\b", near):
                    val = 5.7
        elif word == "palm" and original in ("Palm", "PALM"):
            if tech_neighbors or re.search(r"\b(?:handheld|handhelds|pda|treo|palm os|palm inc)\b", body):
                if not nxt[:1] in (["beach"], ["springs"], ["oil"], ["tree"]):
                    val = 4.8
        elif word == "meta" and original in ("Meta", "META"):
            if finance_hook or tech_neighbors or re.search(r"\b(?:zuckerberg|instagram|facebook|platforms)\b", lead):
                if nxt[:1] != ["analysis"]:
                    val = 5.4
        elif word in ("sprint", "bell", "mci", "bt", "att", "telewest", "ntl"):
            if original[:1].isupper() and (
                re.search(r"\b(?:telecoms?|telecommunications|wireless|long distance|broadband|phone|mobile|"
                          r"vodafone|verizon|bellsouth|nextel|network operator)\b", body) or
                (word in ("mci", "telewest", "ntl") and finance_hook)
            ):
                val = 4.8
        elif word == "hp" and original in ("HP", "Hp"):
            if tech_neighbors or finance_hook or i <= 2:
                val = 5.6
        elif word == "sco" and original == "SCO" and (tech_neighbors or finance_hook):
            val = 5.1
        elif word == "at" and nxt[:1] == ["t"]:
            if re.match(r"AT\s*&\s*T\b", text[spans[i]:], flags=re.I):
                val = 5.9
        elif word == "arm" and original == "ARM" and tech_neighbors:
            val = 5.0
        elif word == "ford" and original in ("Ford", "FORD"):
            if finance_hook or re.search(r"\b(?:car|automaker|vehicle|vehicles|motor|mustang|sedan|truck|auto)\b", body):
                fam, val = "company", 4.2
        elif word in ("delta", "united", "continental", "southwest"):
            if original[:1].isupper() and re.search(r"\b(?:airline|airlines|airways|air fares|airfare|carrier|flights)\b", body):
                if nxt[:1] != ["states"] and prev != "theater":
                    fam, val = "company", 3.7
        elif word == "target" and original in ("Target", "TARGET"):
            if re.search(r"\b(?:retail|retailer|stores|discount chain|wal mart|quarterly earnings)\b", body):
                fam, val = "company", 3.8
        elif word in ("ups", "bp", "gm", "ge", "ubs", "hsbc", "sec", "aig"):
            if original == word.upper():
                fam, val = "company", 3.3 if word != "sec" else 2.1
                if word == "sec" and re.search(r"\b(?:ncaa|college football|touchdowns|southeastern conference)\b", body):
                    val = 0
        if val:
            cat = "sci_tech" if fam == "techco" else "business"
            add_signal(records, cat, fam, val, word, i, i + 1, heading)

    early_sport = family_peak(records["sports"].values(), ("competition", "sport", "person", "team"), lead_end)
    any_sport = family_peak(records["sports"].values(), ("competition", "sport", "person", "team"))
    if MATCH_VERBS.search(lead) or (early_sport >= 2.1 and TITLE_EVENT.search(lead)):
        for m in TEAM_CASE.finditer(text):
            i = raw_pos(spans, m.start())
            if i >= lead_end + 10:
                break
            word = words[i]
            if word == "united" and (i + 1 < len(words) and words[i + 1] in (
                "states", "kingdom", "nations", "airlines", "arab", "way"
            )):
                continue
            if word in ("city", "bills", "heat", "giants", "united", "chiefs", "hurricanes", "lightning"):
                if early_sport < 2.1:
                    continue
            add_signal(records, "sports", "team", 2.6, "team " + word, i, i + 1, heading)

    had_score = False
    for m in SCORELINE.finditer(text):
        i = raw_pos(spans, m.start())
        a, b = int(m.group(1)), int(m.group(2))
        context = " ".join(words[max(0, i - 8):i + 8])
        if (a >= 190 or b >= 190 or "%" in text[m.end():m.end() + 4] or
            re.search(r"\b(?:aged|years old|year old|percent|million|billion|age group|pages|hours|barrel)\b", context)):
            continue
        if MATCH_VERBS.search(context) or any_sport >= 3.9 or (
            a <= 10 and b <= 10 and (TITLE_EVENT.search(context) or early_sport >= 2.1)
        ):
            val = 5.9 if MATCH_VERBS.search(context) or early_sport >= 2.1 else 3.5
            add_signal(records, "sports", "play", val, "numeric scoreline", i, i + 2, heading)
            had_score = True

    # Suppress the weak plain-number score cue unless supported by an actual
    # score or independent evidence. This avoids dates and market figures.
    if not had_score and early_sport < 2.1:
        records["sports"].pop("match result", None)

    cash = MONEY.search(text)
    if cash:
        i = raw_pos(spans, cash.start())
        val = 1.7 if re.search(r"million|billion|trillion", cash.group(), re.I) else 1.1
        add_signal(records, "business", "corporate", val, "money figure", i, i + 1, heading)
    pct = PERCENT.search(text)
    if pct and family_peak(records["business"].values(), ("economy", "markets", "corporate")) >= 2.5:
        i = raw_pos(spans, pct.start())
        add_signal(records, "business", "economy", 1.5, "percentage figure", i, i + 1, heading)

    aircraft_accident = False
    if PHYSICAL_AIR.search(lead) and ACCIDENT.search(lead):
        if not re.search(r"\b(?:avoid a crash|avoided a crash|crash test|mock crash|stock market crash)\b", lead):
            aircraft_accident = True
            p = min(PHYSICAL_AIR.search(lead).start(), ACCIDENT.search(lead).start())
            i = raw_pos(span_b, p)
            add_signal(records, "world", "disaster", 8.1, "aviation emergency", i, i + 1, heading)
    if re.search(r"\b(?:sars|bird flu|avian flu|ebola|cholera|pandemic|flu outbreak|flu epidemic)\b", lead):
        if re.search(r"\b(?:outbreak|epidemic|cases|deaths|killed|spread|quarantine|death toll)\b", lead):
            m = re.search(r"\b(?:sars|bird flu|avian flu|ebola|cholera|pandemic|flu outbreak|flu epidemic)\b", lead)
            i = raw_pos(span_b, m.start())
            add_signal(records, "world", "disaster", 4.2, "outbreak report", i, i + 1, heading)

    signals = {cat: select_signals(records[cat]) for cat in LABELS}
    score = {cat: evidence_score(signals[cat]) for cat in LABELS}
    score["world"] += 0.85
    sport = signals["sports"]
    tech = signals["sci_tech"]
    biz = signals["business"]
    world = signals["world"]
    tech_names = records["sci_tech"].values()
    tech_lead = first_strong(tech_names, ("techco",), 3.6)
    biz_lead = first_strong(records["business"].values(), ("company",), 3.3)
    business_finance = family_peak(biz, ("corporate", "markets", "economy"), lead_end)
    market = MARKET_LEAD.search(core)
    market_first = raw_pos(span_b, market.start()) if market else 1000000
    tech_primary = tech_lead < core_end and tech_lead <= biz_lead
    tech_products = family_peak(tech, ("computing", "network", "security"), lead_end)
    tech_research = family_peak(tech, ("research", "space"), lead_end)
    severe_world_first = first_strong(world, ("conflict", "disaster", "crime"), 4.2)

    # A report about a tech firm's own earnings, deals or legal affairs is
    # tech. A market-wide report does not change topic because it names a
    # tech stock or because the index contains tech stocks.
    if finance_hook and not (market_first < tech_lead and market_first <= 3):
        if tech_primary:
            score["sci_tech"] += 3.5
            score["business"] *= 0.66 if tech_lead <= 5 else 0.81
            if re.search(r"\b(?:lawsuit|sue[sd]?|antitrust|court|trial|patents?|settlement)\b", lead):
                score["world"] *= 0.84
        elif tech_lead < lead_end and biz_lead > tech_lead and business_finance >= 3.0:
            if market_first > tech_lead and not GOV_PUBLIC.search(core):
                score["sci_tech"] += 2.2
                score["business"] *= 0.85
        elif NETWORK_COMPANIES.search(core) and biz_lead > core_end:
            score["sci_tech"] += 2.2
            score["business"] *= 0.79

    if market and market_first <= 6:
        score["business"] += 2.8
        if market_first < tech_lead and tech_research < 4.2:
            score["sci_tech"] *= 0.89
    economy_lead = family_peak(biz, ("economy",), core_end)
    if economy_lead >= 4.6 and not GOV_PUBLIC.search(core):
        score["business"] += 1.9

    # A study about voters, sales, housing, etc. is not necessarily a science
    # story. Discount generic research language when evidence is only of that
    # kind, not actual findings in scientific or medical subject areas.
    research_topic = any(
        e[2] == "space" and e[1] >= 4.0 or
        e[2] == "research" and e[1] >= 4.0 and e[3] not in (
            "researchers found", "researchers report", "scientists found",
            "scientists discovered", "scientists say", "scientists have",
            "study finds", "research suggests", "study published", "research team",
            "researchers at", "breakthrough in", "experimental outcome",
            "scientific study", "scientific research",
        ) for e in tech
    )
    if GENERIC_STUDY_TOPICS.search(lead) and not research_topic and tech_products < 3.5 and tech_lead >= lead_end:
        score["sci_tech"] *= 0.57

    if aircraft_accident:
        score["business"] *= 0.61
        score["world"] += 2.8
    elif severe_world_first < core_end and tech_research < 4.2 and not market:
        if family_peak(biz, ("corporate",), core_end) < 3.2:
            score["world"] += 1.25

    if tech_products >= 4.0 and biz_lead >= lead_end and not market and not aircraft_accident:
        if family_peak(tech, ("computing", "network", "security"), core_end) >= 4.0:
            score["sci_tech"] += 1.6
    if tech_research >= 4.2 and research_topic:
        if family_peak(tech, ("research", "space"), core_end) >= 4.2:
            score["sci_tech"] += 1.45

    # Distinguish a game/competition from isolated sports vocabulary
    # (season, race, match, etc.) in another kind of news.
    team_strength = family_peak(sport, ("team", "person"), lead_end)
    sport_strength = family_peak(sport, ("sport", "competition"), lead_end)
    play_strength = family_peak(sport, ("play",), lead_end)
    if (team_strength >= 2.1 or sport_strength >= 2.4) and play_strength >= 2.9:
        score["sports"] += 2.4
    if had_score and (team_strength >= 2.1 or sport_strength >= 2.4):
        score["sports"] += 1.9
    if team_strength < 2.1 and sport_strength < 2.4 and play_strength < 3.5:
        score["sports"] *= 0.66

    # Prioritize the concrete event when offices or companies merely supply
    # background. Conversely, legal words on their own do not turn corporate
    # litigation or a competition disciplinary story into general crime news.
    if GOV_PUBLIC.search(core) and severe_world_first < lead_end:
        score["world"] += 1.4
    if biz_lead < core_end and business_finance >= 3.0 and not aircraft_accident:
        if severe_world_first > biz_lead and not GOV_PUBLIC.search(core):
            score["business"] += 2.0
    if tech_lead < core_end and severe_world_first > tech_lead:
        if re.search(r"\b(?:patents?|antitrust|copyright|licensing|lawsuit|sue[sd]?|settlement)\b", lead):
            score["sci_tech"] += 2.1
    if team_strength >= 4.0 and family_peak(sport, ("team", "person"), core_end) >= 4.0:
        if re.search(r"\b(?:suspended|benched|traded|signs|signed|retires|retired|contract|knee|injur(?:y|ed)|coach|return|debut|season)\b", lead):
            score["sports"] += 1.8

    return {"answer": max(LABELS, key=score.get)}