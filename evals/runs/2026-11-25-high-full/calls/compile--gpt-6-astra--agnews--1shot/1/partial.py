import re
import unicodedata
from collections import defaultdict

_LABELS = ("business", "sci_tech", "sports", "world")


def _clean(text):
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    for old, new in (
        ("&amp;", "&"), ("&quot;", '"'), ("&apos;", "'"),
        ("&#39;", "'"), ("&nbsp;", " "), ("&lt;", "<"), ("&gt;", ">"),
    ):
        text = text.replace(old, new)
    text = re.sub(r"\bat\s*&\s*t\b", "ATandT", text, flags=re.I)
    text = re.sub(r"\bs\s*&\s*p\b", "SandP", text, flags=re.I)
    text = re.sub(r"\bc\+\+", "cplusplus", text, flags=re.I)
    text = re.sub(r"\bc#", "csharp", text, flags=re.I)
    text = re.sub(r"\.net\b", " dotnet ", text, flags=re.I)
    text = re.sub(
        r"\b(?:[A-Za-z]\.){2,}",
        lambda m: m.group(0).replace(".", ""),
        text,
    )
    text = re.sub(r"\bu\.\s*s\b\.?", "US", text, flags=re.I)
    text = re.sub(r"\bu\.\s*k\b\.?", "UK", text, flags=re.I)
    text = re.sub(r"\bu\.\s*n\b\.?", "UN", text, flags=re.I)
    text = re.sub(r"'s\b", "", text, flags=re.I)
    return text


def _tokens(text):
    return re.findall(r"[a-z0-9]+", _clean(text).lower())


_RULES = {}


def _add(category, weight, entries, role=None, single=False):
    index = _LABELS.index(category)
    terms = entries.split() if single else entries.split("|")
    for term in terms:
        key = tuple(_tokens(term.strip()))
        if not key:
            continue
        if key not in _RULES:
            _RULES[key] = [[0.0, 0.0, 0.0, 0.0], set()]
        weights, roles = _RULES[key]
        weights[index] = max(weights[index], float(weight))
        if role:
            roles.add(role)


def _w(category, weight, entries, role=None):
    _add(category, weight, entries, role, True)


def _p(category, weight, entries, role=None):
    _add(category, weight, entries, role, False)


# Finance, commerce, and the economy.
_w("business", 5.5, """
earnings profits revenue revenues profitability dividend dividends
merger mergers acquisition acquisitions takeover takeovers bankruptcy
bankruptcies recession inflation deflation stagflation
""", "finance")
_w("business", 4.0, """
profit shares shareholders shareholder stockholders stockholder investors
investor investment investments investing equities bonds bond yields
broker brokerage brokerages lender lenders lending mortgage mortgages
banking bankers insurer insurers insurance pensions pension
exports imports export import tariffs tariff commodities commodity
retailer retailers retail automaker automakers airlines airline
""", "finance")
_w("business", 3.0, """
sales earnings forecasts economist economists economic economy economies
unemployment payrolls manufacturing industrial output productivity
valuation valuations securities capitalization capitalisation
conglomerate conglomerates buyout buyouts restructuring insolvency
insolvent liquidation refinancing refinance debt debts creditors creditor
debtor borrowers borrower borrowing credit loan loans
analysts analyst analysts quarterly fiscal finance financial
""")
_w("business", 2.2, """
company companies corporation corporations corporate business businesses
firms firm enterprise enterprises commercial commerce entrepreneur
entrepreneurs entrepreneurial ceo executives executive shareholders
shareholder accounting accountant accountants auditors auditor
audit audited pensioner pensioners workforce layoffs layoff
redundancies jobless wages wage salaries salary paychecks
union unions labor labour workers factories factory
consumer consumers spending spending budgets budget
distributor distributors supplier suppliers shipments shipment
wholesale wholesaler wholesalers franchise franchises
""")
_w("business", 1.2, """
million billion trillion dollars dollar euro euros yen sterling
percent percentage growth grew grow growing gains gain declined decline
rose rises rising fell falling falls climbed climbs losses loss
cost costs costing prices price priced pricing expensive
deal deals contract contracts orders order forecast forecasts
cuts cut industry industries market markets
""")
_w("business", 3.5, """
oil crude petroleum gasoline petrol diesel refinery refineries
opec gold bullion copper aluminium aluminum nickel platinum
soybeans soybean wheat corn coffee cotton sugar cocoa
freight cargo shipping shipbuilding shipyards
""")
_w("business", 2.5, """
shops shopping supermarket supermarkets stores store malls mall
grocer grocers grocery groceries groceries chain chains
restaurants restaurant hospitality hotel hotels tourism tourists
airliner airliners aircraft carmaker carmakers automobiles automobile
automotive automakers vehicle vehicles cars truck trucks
housing property properties realty realtor realtors rentals
construction builder builders homebuilders homebuilder
advertising advertiser advertisers advertisers advertisers
sponsorship sponsorships sponsors sponsor marketing marketer marketers
""")
_w("business", 4.5, """
antitrust monopoly monopolies privatization privatisation
outsourcing outsource outsourced outsourcing deregulation
franchising franchised ecommerce
""")
_w("business", 3.0, "fraud sued lawsuit lawsuits litigation settlement settlements")
_p("business", 8.0, """
stock market | stock markets | stock exchange | stock exchanges |
wall street | dow jones | dow industrials | nasdaq composite |
standard and poor | sandp 500 | s and p 500 | ftse 100 |
nikkei average | hang seng | equity market | equity markets |
financial markets | bond market | bond markets | treasury yields |
oil prices | crude prices | crude oil prices | oil futures |
gold prices | commodity prices | interest rate | interest rates |
federal reserve | central bank | central banks | bank of england |
european central bank | monetary policy | gross domestic product |
trade deficit | trade surplus | consumer price index | producer price index |
retail sales | unemployment rate | jobless claims | consumer confidence |
economic growth | economic recovery | economic slowdown
""", "macro")
_w("business", 6.0, "stocks equities nasdaq ftse nikkei dax bourses", "macro")
_w("business", 5.0, "inflation recession deflation gdp", "macro")
_p("business", 6.0, """
us stocks | european stocks | asian stocks | tokyo stocks | london stocks |
us shares | european shares | asian shares | shares on wall street |
currency markets | foreign exchange | dollar falls | dollar rises |
dollar drops | dollar gains | euro rises | euro falls |
oil price | crude futures | futures market | futures trading |
stock index | stock indexes | stock indices | blue chips |
blue chip stocks | bull market | bear market | market rally |
market selloff | market sell off
""", "macro")
_p("business", 6.0, """
initial public offering | public offering | stock offering |
quarterly earnings | quarterly profit | quarterly profits |
net profit | net profits | net income | net loss |
earnings per share | earnings report | earnings forecast |
profit warning | profit warnings | annual profit | annual earnings |
third quarter profit | fourth quarter profit | first quarter profit |
second quarter profit | earnings growth | operating profit |
operating income | operating loss | pretax profit | pre tax profit |
profit margin | profit margins | sales forecast | sales forecasts |
same store sales | market share | market value | share price |
share prices | stock price | stock prices | dividend payment |
share buyback | stock buyback | share repurchase | capital gains |
stock options | cash flow | cash flows | balance sheet |
financial results | financial statements | accounting fraud |
insider trading | hostile takeover | merger talks | takeover bid |
buyout offer | bankruptcy protection | chapter 11 | chapter eleven |
credit rating | credit ratings | investment bank | investment banks |
investment banking | hedge fund | hedge funds | mutual fund |
mutual funds | private equity | venture capital | venture capitalist
""", "finance")
_p("business", 5.5, """
chief executive | chief financial officer | chief operating officer |
board of directors | boardroom | annual meeting | shareholder meeting |
company chairman | corporate governance | limited liability |
securities and exchange commission | securities exchange commission |
new york stock exchange | london stock exchange |
world trade organization | world trade organisation |
trade talks | trade agreement | trade agreements | free trade |
trade war | trade wars | import duties | export duties |
import tariffs | import ban | export ban | trade barriers |
commerce department | labor department | labour department |
treasury department | finance minister | finance ministry |
world bank | international monetary fund | economic outlook |
job cuts | cutting jobs | cut jobs | eliminate jobs | slashing jobs |
labor union | labour union | pay dispute | on strike | workers strike |
industrial action | minimum wage | pension fund | pension funds |
oil production | oil output | oil exports | oil supplies |
oil reserves | oil company | oil companies | oil industry |
oil and gas | natural gas | gas prices | gasoline prices |
energy prices | heating oil | oil refinery | oil refineries |
real estate | property market | housing market | home sales |
home prices | house prices | mortgage rates | housing starts |
building permits | commercial property | retail chain |
department store | department stores | discount retailer |
consumer spending | holiday shopping | christmas shopping |
holiday sales | auto sales | car sales | vehicle sales |
auto industry | automobile industry | airline industry |
air carrier | air carriers | budget airline | low cost airline |
ticket prices | air fares | fuel costs | fuel prices |
box office | advertising revenue | advertising revenues
""")
_w("business", 5.5, """
nyse ipo ipos imf wto ecb fed greenspan bernanke yellen powell
""")
_p("business", 7.0, """
alan greenspan | ben bernanke | janet yellen | jerome powell |
warren buffett | carlos ghosn | richard branson | rupert murdoch |
jack welch | jamie dimon | lloyd blankfein
""")
_p("business", 7.0, """
goldman sachs | morgan stanley | jp morgan | jpmorgan |
j p morgan | jpmorgan chase | citigroup | citibank |
bank of america | wells fargo | merrill lynch |
deutsche bank | credit suisse | barclays | hsbc | ubs |
lehman brothers | bear stearns | royal bank of scotland |
lloyds bank | standard chartered | santander |
fannie mae | freddie mac | american express |
berkshire hathaway | aig | metlife | prudential |
allianz | allstate | mastercard | visa inc |
charles schwab | fidelity investments | blackrock |
blackstone | carlyle group | kkr | capital one |
enron | parmalat | arthur andersen | tyco
""", "business_firm")
_p("business", 6.5, """
walmart | wal mart | wal-mart | costco | tesco | carrefour |
sainsbury | sainsbury's | kroger | aldi | lidl |
target corp | target stores | target corporation |
sears | kmart | macy | macy's | nordstrom |
jc penney | j c penney | jcpenney | home depot | lowe's |
best buy | staples | office depot | toys r us |
ikea | gap inc | gap stores | h and m | zara |
marks and spencer | whole foods | dollar general |
mcdonald's | mcdonalds | burger king | starbucks |
yum brands | domino's | chipotle | dunkin |
coca cola | pepsi | pepsico | nestle | danone |
kraft | kraft heinz | general mills | kellogg |
unilever | procter and gamble | procter gamble |
colgate palmolive | anheuser busch | heineken |
diageo | sabmiller | altria | philip morris |
nike | adidas | reebok | puma | under armour |
lvmh | louis vuitton | gucci | hermes |
estee lauder | l'oreal | loreal
""", "business_firm")
_p("business", 6.5, """
general motors | gm | ford | toyota | honda | nissan |
renault | peugeot | citroen | volkswagen | bmw |
daimler | chrysler | daimlerchrysler | mercedes benz |
hyundai | kia | tesla | rivian | lucid motors |
stellantis | porsche | ferrari | fiat | volvo |
harley davidson | tata motors | byd |
boeing | airbus | bombardier | embraer |
general electric | ge | honeywell | caterpillar |
deere | john deere | siemens | 3m |
lockheed martin | northrop grumman | raytheon |
united technologies | rolls royce |
exxon | exxonmobil | exxon mobil | chevron |
texaco | conoco | conocophillips | royal dutch shell |
shell oil | bp | british petroleum | totalenergies |
saudi aramco | aramco | petrobras | gazprom |
rosneft | lukoil | halliburton | schlumberger |
bhp | rio tinto | anglo american | alcoa |
du pont | dupont | dow chemical | basf |
arcelormittal | us steel | united states steel
""", "business_firm")
_p("business", 6.5, """
united airlines | american airlines | delta air lines |
delta airlines | southwest airlines | northwest airlines |
continental airlines | us airways | jetblue |
british airways | lufthansa | air france | klm |
air france klm | ryanair | easyjet | qantas |
singapore airlines | cathay pacific | emirates airline |
alitalia | japan airlines | air canada |
virgin atlantic | virgin australia |
fedex | federal express | united parcel service |
dhl | maersk | carnival corp | royal caribbean |
marriott | hilton | intercontinental hotels |
disney | walt disney | time warner | warner bros |
warner brothers | news corp | news corporation |
viacom | paramount | universal studios | dreamworks |
pixar | sony pictures | clear channel | bertelsmann |
vivendi | mgm | directv | dish network |
pearson | penguin random house | gannett |
pfizer | merck | glaxosmithkline | gsk | astrazeneca |
johnson and johnson | eli lilly | bristol myers |
bristol myers squibb | sanofi | novartis | roche |
bayer | abbott | abbvie | amgen | biogen |
genentech | gilead | moderna | biontech |
walgreens | cvs | rite aid | unitedhealth
""", "business_firm")

# Technology companies remain technology stories even in financial or legal news.
_p("sci_tech", 8.0, """
microsoft | google | ibm | intel | amd | nvidia | nvidia corp |
dell | oracle | cisco | cisco systems | emc |
hewlett packard | hewlett packard enterprise | hp | hpe |
sun microsystems | compaq | lenovo | acer | asus |
asustek | toshiba | fujitsu | hitachi | nec |
samsung | lg | lg electronics | panasonic | matsushita |
sony | philips | nokia | motorola | blackberry |
research in motion | palm inc | palmone | palm one |
qualcomm | broadcom | marvell | mediatek |
texas instruments | micron | hynix | sk hynix |
tsmc | taiwan semiconductor | applied materials |
asml | arm holdings | globalfoundries | analog devices |
western digital | seagate | sandisk | kingston technology |
logitech | lexmark | xerox | canon | epson |
adobe | macromedia | autodesk | corel |
symantec | mcafee | kaspersky | trend micro |
crowdstrike | palo alto networks | fortinet |
checkpoint software | check point software |
red hat | canonical | novell | suse |
salesforce | salesforce.com | servicenow | workday |
snowflake | databricks | palantir | splunk |
vmware | citrix | netapp | juniper | arista |
lucent | alcatel | alcatel lucent | nortel |
ericsson | huawei | zte | ntt | ntt docomo |
atandt | at and t | verizon | t mobile |
nextel | sbc | bellsouth | bell south |
qwest | mci | worldcom | world com |
deutsche telekom | france telecom | british telecom |
british telecommunications | bt group | telefonica |
vodafone | telecom italia | orange telecom |
china mobile | china telecom | china unicom |
comcast | charter communications |
yahoo | lycos | ask jeeves | ask.com | altavista |
aol | america online | msn | netscape |
ebay | amazon.com | amazon web services |
facebook | instagram | whatsapp | twitter |
bytedance | tik tok | tiktok | tencent | wechat |
alibaba | baidu | jd.com | rakuten | shopify |
netflix | spotify | pandora media | twitch |
youtube | pinterest | snapchat | snap inc |
reddit | linkedin | discord | zoom video |
dropbox | slack | atlassian | github | gitlab |
cloudflare | akamai | godaddy | godaddy.com |
uber | lyft | airbnb | doordash | instacart |
paypal | stripe | coinbase | robinhood markets |
openai | open ai | anthropic | deepmind | google deepmind |
mistral ai | hugging face | stability ai |
spacex | blue origin | rocket lab |
nintendo | sega | atari | electronic arts | ea games |
activision | blizzard | activision blizzard |
ubisoft | take two interactive | rockstar games |
epic games | valve software | valve corporation |
bethesda | square enix | capcom | konami |
bandai namco | namco | thq | id software
""", "tech_firm")

_w("sci_tech", 6.0, """
software hardware internet broadband wireless telecom telecommunications
semiconductor semiconductors microchip microchips microprocessor
microprocessors processor processors chipset chipsets motherboard
motherboards supercomputer supercomputers computing cybersecurity
cyberattack cyberattacks cybercrime cybercriminal cybercriminals
malware ransomware spyware adware phishing keylogger keyloggers
keylogging trojan trojans botnet botnets rootkit rootkits
cryptography encryption cryptographic encrypted decrypt decryption
""", "technology")
_w("sci_tech", 4.5, """
computer computers laptop laptops notebook notebooks desktop desktops
smartphone smartphones cellphone cellphones handset handsets
tablet tablets smartwatch smartwatches wearable wearables
router routers modem modems server servers datacenter datacenters
networking ethernet wifi wi-fi bluetooth wiimax
firewall firewalls antivirus hacker hackers hacking hacked
browser browsers webpage webpages website websites webmail
email emails emailing e-mail e-mails spam spammers spammer
screensaver screensavers passwords password keystrokes
download downloads downloading uploaded uploading upload
operating operating-system database databases algorithm algorithms
programmer programmers programming coder coders coding
robot robots robotics robotic automation automated
nanotechnology nanotech nanomaterials quantum
""", "technology")
_w("sci_tech", 3.2, """
chip chips digital electronics electronic electronic
technology technologies technological technical hightech
online web cyberspace cyber netbook netbooks
app apps application applications platform platforms
telecoms telephone telephones telephony cellular mobile mobiles
network networks connectivity connected connect
console consoles videogame videogames gaming gamer gamers
virtual virtualization virtualisation pixel pixels resolution
multimedia streaming streamed streams podcast podcasts
codec codecs firmware patch patches patched bug bugs
vulnerability vulnerabilities exploit exploits
opensource open-source linux unix android ios macos
ubuntu debian fedora freebsd solaris dotnet
cplusplus csharp javascript typescript python java
html css sql mysql postgresql mongodb apache
php perl ruby rust kubernetes docker
""")
_w("sci_tech", 2.0, """
innovation innovations innovative invention inventions inventor inventors
invented invent prototype prototypes startup startups
device devices gadget gadgets gadgets camera cameras
battery batteries sensor sensors touchscreen touchscreens
bandwidth storage memory optical laser lasers
audio video dvd dvds cd cds mp3 mp4 hdtv lcd oled led
patent patents patented patenting copyright copyrights
file files sharing interface interfaces search searches
upgrade upgrades upgraded upgrading update updates
released release releases version versions
virus viruses worm worms
""")
_p("sci_tech", 9.0, """
artificial intelligence | machine learning | deep learning |
large language model | large language models | generative ai |
neural network | neural networks | computer vision |
natural language processing | quantum computer | quantum computing |
internet of things | augmented reality | virtual reality |
mixed reality | facial recognition | speech recognition |
voice recognition | self driving | autonomous driving |
driverless car | driverless cars |
mobile phone | mobile phones | cell phone | cell phones |
cellular phone | cellular phones | smart phone | smart phones |
personal computer | personal computers | desktop computer |
desktop computers | laptop computer | laptop computers |
operating system | operating systems | computer system |
computer systems | computer network | computer networks |
computer chip | computer chips | silicon chip | silicon chips |
computer processor | computer processors | computer maker |
computer makers | software maker | software makers |
software company | software companies | tech company |
tech companies | technology company | technology companies |
technology giant | tech giant | tech giants |
internet company | internet companies | internet service |
internet services | internet access | internet connection |
internet provider | internet providers | internet portal |
web browser | web browsers | web search | search engine |
search engines | social media | social network | social networks |
social networking | cloud computing | cloud services |
data center | data centers | data centre | data centres |
wireless network | wireless networks | wireless internet |
wireless broadband | broadband internet | broadband access |
fiber optic | fibre optic | mobile broadband |
video game | video games | computer game | computer games |
online game | online games | online gaming | game console |
games console | gaming console | handheld console
""", "technology")
_p("sci_tech", 8.0, """
computer virus | computer viruses | email virus | e mail virus |
internet worm | computer worm | malicious software |
malicious code | security flaw | security flaws |
security hole | security holes | security vulnerability |
security vulnerabilities | software vulnerability |
software vulnerabilities | computer security | network security |
internet security | data security | cyber security |
data breach | data breaches | data leak | data leaks |
denial of service | distributed denial of service |
ransomware attack | ransomware attacks | cyber attack |
cyber attacks | cyber crime | identity theft |
password theft | phishing attack | phishing attacks |
anti spam | anti virus | anti spyware |
software patch | security patch | security patches |
digital rights management | digital copyright |
peer to peer | file sharing | filesharing | file-sharing |
open source | source code | software code |
software development | web development |
application programming interface | programming language |
programming languages | coding language |
hard disk | hard disks | hard drive | hard drives |
solid state drive | flash memory | flash drive |
graphics card | graphics cards | graphics processor |
graphics processing | central processing unit |
integrated circuit | integrated circuits | circuit board |
printed circuit | microelectronic devices |
liquid crystal display | light emitting diode |
flat panel display | touch screen | touch screens |
digital camera | digital cameras | digital music |
digital media | digital video | digital television |
high definition television | high definition tv |
internet television | internet tv | internet radio |
satellite radio | satellite television | satellite tv |
voice over internet | voice over ip | internet telephony |
3d printing | three dimensional printing | 3d printer |
3d printers | additive manufacturing |
fuel cell | fuel cells | solar cell | solar cells |
lithium ion | battery technology | fusion reactor |
nuclear fusion | clean energy technology
""", "technology")
_p("sci_tech", 7.0, """
windows xp | windows vista | windows 7 | windows 8 |
windows 10 | windows 11 | windows 2000 | windows server |
windows update | microsoft office | office 365 | microsoft 365 |
internet explorer | microsoft edge | google chrome |
mozilla firefox | firefox | mozilla | thunderbird |
safari browser | chrome os | google maps | google earth |
google news | google search | google glass | google play |
gmail | hotmail | outlook.com | yahoo mail |
apple music | apple watch | apple pay | apple tv |
mac os | mac os x | macbook | macbook pro |
macintosh | imac | ipod | iphone | ipad | itunes |
ipados | watchos | airpods | siri | alexa |
kindle | kindle fire | amazon prime | amazon echo |
playstation | play station | ps2 | ps3 | ps4 | ps5 |
xbox | xbox live | xbox 360 | xbox one | xbox series |
gamecube | game boy | gameboy | nintendo ds |
nintendo switch | nintendo wii | steam deck |
halo 2 | halo 3 | half life | half life 2 |
world of warcraft | warcraft | starcraft | minecraft |
grand theft auto | call of duty | fortnite |
chatgpt | chat gpt | gpt 4 | gpt 5 | gpt 3 |
copilot | gemini ai | claude ai |
napster | kazaa | grokster | bittorrent | bit torrent |
the pirate bay | limewire | morpheus software |
bit coin | bitcoin | bitcoins | blockchain |
cryptocurrency | cryptocurrencies | crypto currency |
ethereum | non fungible token | non fungible tokens |
web3 | web 3 | metaverse
""", "technology")
_p("sci_tech", 6.0, """
bill gates | steve ballmer | steve jobs | tim cook |
larry page | sergey brin | eric schmidt | sundar pichai |
satya nadella | mark zuckerberg | jeff bezos |
larry ellison | michael dell | carly fiorina |
meg whitman | jerry yang | david filo | linus torvalds |
steve wozniak | tim berners lee | sam altman |
jensen huang | lisa su | demis hassabis |
jack dorsey | travis kalanick | brian chesky
""")

# Scientific, medical, and space reporting.
_w("sci_tech", 5.5, """
scientist scientists scientific physicist physicists physicists
astronomer astronomers astronomy astrophysics astrophysicist
cosmology cosmologist cosmologists biologist biologists
geneticist geneticists genetic genetics genomic genomics genome
genomes microbiologist microbiology neuroscientist neuroscience
paleontologist paleontology palaeontology archaeologist archaeologists
archaeology archaeology archaeological archaeologic
""", "research")
_w("sci_tech", 4.0, """
science research researcher researchers laboratory laboratories
experiment experiments experimental experimentation discovery
discoveries discovered discovers finding findings breakthrough
breakthroughs fossil fossils fossilized dinosaur dinosaurs
prehistoric evolution evolutionary evolved evolutionary
species biodiversity ecosystem ecosystems ecology ecological
DNA RNA chromosome chromosomes gene genes mutation mutations
molecule molecules molecular cellular cell cells protein proteins
enzyme enzymes bacteria bacterial bacterium microbial microbes
microbe microorganism microorganisms pathogen pathogens
""", "research")
_w("sci_tech", 3.0, """
study studies studied studying evidence theory theories
scientifically biologic biological biology zoology zoologist
botany botanist botanists anthropology anthropologist anthropologists
geology geologist geologists geological geophysics
physics chemistry chemist chemists chemical chemicals
mathematics mathematician mathematicians mathematical
statistics statistical quantum particle particles atom atoms
atomic isotope isotopes antimatter neutrino neutrinos
boson bosons electron electrons proton protons neutron neutrons
photon photons superconductivity superconductor superconductors
telescope telescopes observatory observatories microscope microscopes
laboratories lab labs laboratory
""")
_w("sci_tech", 7.0, """
nasa esa astronaut astronauts cosmonaut cosmonauts spacecraft
spaceflight spacewalk spacewalks spacewalking shuttle
satellite satellites extraterrestrial extraterrestrials
exoplanet exoplanets supernova supernovae asteroid asteroids
comet comets meteor meteorite meteorites nebula nebulae
""", "space")
_w("sci_tech", 4.5, """
space planetary planet planets mars jupiter saturn neptune uranus
pluto venus lunar moon moons martian solar orbit orbits orbital
orbiting orbiter lander rover rovers rocket rockets
galaxy galaxies galactic universe cosmos cosmic starlight
hubble cassini voyager galileo hubble webb
""")
_p("sci_tech", 9.0, """
space station | international space station | space shuttle |
space agency | space agencies | space exploration |
space mission | space missions | space program | space programme |
space telescope | hubble telescope | hubble space telescope |
james webb | james webb space telescope | deep space |
outer space | solar system | milky way | black hole |
black holes | neutron star | neutron stars | big bang |
dark matter | dark energy | gravitational wave |
gravitational waves | event horizon | meteor shower |
mars rover | mars rovers | mars exploration | mars mission |
mars probe | lunar mission | lunar lander | lunar surface |
moon landing | mission to mars | mission to the moon |
life on mars | water on mars | red planet |
launch vehicle | satellite launch | rocket launch |
reusable rocket | falcon 9 | space tourism |
cape canaveral | kennedy space center | jet propulsion laboratory |
johnson space center | european space agency |
rosetta probe | huygens probe | genesis probe |
new horizons | parker solar probe | artemis mission |
chandrayaan | isro | chang e
""", "space")
_p("sci_tech", 8.0, """
scientific research | scientific discovery | scientific discoveries |
scientists discover | researchers discover | scientists found |
researchers found | study finds | study shows | study suggests |
studies show | studies suggest | new study | new research |
research team | research teams | research project |
research projects | research laboratory | research laboratories |
clinical trial | clinical trials | medical trial | medical trials |
human trial | human trials | drug trial | drug trials |
experimental drug | experimental vaccine | experimental treatment |
new vaccine | cancer vaccine | cancer research | medical research |
stem cell | stem cells | stem cell research |
gene therapy | gene editing | genetic engineering |
genetically modified | genetically engineered | human genome |
genome sequencing | genetic code | dna sequencing | dna analysis |
human cloning | therapeutic cloning | cloned embryo |
cloned embryos | cloned animal | cloned animals |
embryonic cells | embryonic stem cells | crispr |
molecular biology | evolutionary biology | synthetic biology |
human evolution | natural selection | species discovered |
new species | mass extinction | fossil record |
archaeological dig | archaeological discovery |
archaeological site | prehistoric human | early humans |
ancient remains | dinosaur bones | dinosaur fossil |
carbon dating | radiocarbon dating |
particle accelerator | particle physics | large hadron collider |
higgs boson | cern | quantum mechanics | quantum entanglement |
theory of relativity | general relativity | string theory |
nobel prize in physics | nobel prize in chemistry |
nobel prize in medicine
""", "research")
_w("sci_tech", 4.5, """
vaccine vaccines vaccination vaccinations antibiotic antibiotics
antiviral antivirals chemotherapy immunotherapy radiotherapy
biotechnology biotech biomedical biomedicine pharmacology
neuroscience neurological alzheimer alzheimers parkinson parkinsons
dementia autism schizophrenia osteoporosis carcinogen carcinogens
carcinogenic cholesterol diabetes diabetic insulin obesity obese
fertility infertility embryos embryo embryonic cloning cloned
transplant transplants transplanting transplantation
""", "research")
_w("sci_tech", 2.3, """
medical medicine medicines medicinal medication medications
health healthcare doctor doctors physician physicians patients patient
hospital hospitals cancer cancers tumor tumors tumour tumours
disease diseases illness illnesses infection infections infected
infectious epidemic epidemics pandemic pandemics
influenza flu hiv aids sars covid covid19 coronavirus
ebola malaria polio measles tuberculosis dengue zika
treatment treatments treating therapy therapies therapeutic
diagnosis diagnostic diagnosed symptom symptoms prevention
preventive immune immunity immunization immunisation
blood brain heart lung lungs liver kidney kidneys
surgery surgical surgeon surgeons neurology cardiology
vitamin vitamins nutrition nutritional diet dietary
smoking tobacco cigarette cigarettes smokers
publications journal journals
""")
_p("sci_tech", 6.0, """
food and drug administration | fda approval | fda approves |
drug approval | approves drug | approved drug |
drug safety | drug treatment | drug treatments |
new drug | new drugs | prescription drug | prescription drugs |
side effect | side effects | birth defect | birth defects |
heart attack | heart attacks | heart disease |
heart failure | blood pressure | high blood pressure |
blood test | blood tests | breast cancer | lung cancer |
prostate cancer | skin cancer | colon cancer |
bird flu vaccine | flu vaccine | flu vaccines |
aids vaccine | hiv vaccine | covid vaccine |
disease control | centers for disease control |
centres for disease control | world health organization |
world health organisation | national institutes of health |
national institute of health | public health study |
mental health research | reproductive medicine |
fertility treatment | in vitro fertilization | ivf |
human brain | brain scan | brain scans | brain cells |
nerve cells | nervous system | immune system |
biological clock | life expectancy | sleep deprivation |
bone marrow | organ transplant | organ donation |
regenerative medicine | personalized medicine |
randomized trial | randomised trial | placebo controlled |
peer reviewed | peer review | meta analysis |
lancet | new england journal of medicine
""", "research")
_w("sci_tech", 3.0, """
climate climatology climatologist climatologists environmental
environment ecology conservation biodiversity extinction endangered
oceanography oceanographer seismology seismologist seismic
glacier glaciers glacial icecap icecaps
""")
_p("sci_tech", 6.0, """
climate change | global warming | greenhouse gas |
greenhouse gases | carbon dioxide | ozone layer |
ozone depletion | melting ice | melting glaciers |
sea level rise | rising sea levels | climate science |
climate scientists | climate research | climate model |
climate models | ocean temperatures | polar ice |
coral reef | coral reefs | coral bleaching |
endangered species | endangered animals | wildlife conservation |
marine biology | marine life | animal behavior | animal behaviour |
renewable energy research | solar energy research
""", "research")

# Games, competitions, teams, and athletes.
_w("sports", 7.0, """
football soccer baseball basketball hockey cricket rugby tennis
golf golfing badminton volleyball handball netball softball
lacrosse polo squash racquetball tabletennis
nascar motorsport motorsports motocross speedway
biathlon triathlon heptathlon decathlon pentathlon
bobsled bobsleigh luge curling taekwondo judo karate
wrestling weightlifting gymnastics gymnastic fencing
quarterback quarterbacks linebacker linebackers touchdown touchdowns
shortstop shortstops pitcher pitchers pitching catcher catchers
batsman batsmen batswoman wicket wickets wicketkeeper
goalkeeper goalkeepers goalie goalies striker strikers
""", "sport_topic")
_w("sports", 5.0, """
sport sports sporting athlete athletes athletic athletics
olympic olympics olympian olympians paralympic paralympics
championship championships champion champions tournament tournaments
semifinal semifinals semifinalist semifinalists quarterfinal quarterfinals
playoff playoffs postseason preseason league leagues
cup cups coach coaches coaching coached team teams teammate teammates
captain captains captained umpire umpires referee referees refereeing
stadium stadiums stadia ballpark ballparks arena arenas
match matches matchup matchups rematch fixture fixtures
innings inning bats batting batsmen bowler bowlers bowling
fielder fielders fielding homer homers homered homeplate
rbi rbis bullpen dugout strikeout strikeouts grandstand
dribble dribbles dunk dunks rebounding rebound rebounds
penalties penalty offside offsides foul fouls fouled
hat-trick hattrick par putt putting putts birdie birdies
bogey bogeys eagle eagles fairway fairways tee tees
""")
_w("sports", 3.5, """
player players playing played scored scoring scorer scorers
score scoreboard goals goal goalscorer goalscorers
winning winner winners won wins win victory victories
defeated defeat defeats beating beat beaten upset upsets
rival rivals rivalry defending challenger challengers
title titles medal medals medalist medalists medallist medallists
silver bronze goldmedal sprint sprinting sprinter sprinters
race races racing raced racer racers circuit circuits
podium finish finisher finishers qualifier qualifiers qualifying
qualification relegation relegated promotion promoted
seed seeded unseeded seeding draw drawn tiebreak tiebreaker
round rounds bout bouts boxing boxer boxers kickboxing
knockout knockouts knocked sparring heavyweight welterweight
middleweight lightweight featherweight bantamweight cruiserweight
champ champs debut rookie rookies roster rosters
retired retirement transfer transfers signing signed
""")
_w("sports", 1.3, """
game games season seasons final finals first second third
fourth fifth points point lead leads led lose loses lost
loss losing comeback run runs running runner runners
record records streak unbeaten undefeated warmup warmups
training practice fitness injured injury injuries
fans fan crowd crowds spectators spectator competition
competitions competitive compete competes competed competing
contender contenders contest contests
""")
_p("sports", 11.0, """
world cup | world series | super bowl | superbowl |
olympic games | summer olympics | winter olympics |
olympic gold | olympic medal | olympic medals |
olympic champion | olympic champions | olympic torch |
paralympic games | commonwealth games | asian games |
champions league | europa league | conference league |
premier league | english premier league | premiership |
la liga | serie a | serie b | bundesliga | ligue 1 |
major league baseball | national football league |
national basketball association | national hockey league |
major league soccer | national rugby league |
australian football league | canadian football league |
national collegiate athletic association |
college football | college basketball |
grand slam | us open | u s open | australian open |
french open | british open | wimbledon |
davis cup | fed cup | billie jean king cup |
atp tour | wta tour | pga tour | lpga tour |
ryder cup | presidents cup | masters tournament |
pga championship | tour de france | giro d italia |
vuelta a espana | formula one | formula 1 | f1 |
grand prix | indy 500 | indianapolis 500 | daytona 500 |
kentucky derby | preakness stakes | belmont stakes |
breeders cup | stanley cup | grey cup |
ncaa tournament | march madness | final four |
fa cup | league cup | carabao cup | six nations |
rugby world cup | cricket world cup | indian premier league |
test cricket | test match | test matches | one day international |
one day internationals | twenty20 | t20 cricket |
champions trophy | ashes series | the ashes |
fifa world cup | uefa championship | european championship |
uefa euro | copa america | copa libertadores |
africa cup of nations | african nations cup |
concacaf gold cup | concacaf champions cup |
world athletics championships | world swimming championships
""", "sport_entity")
_w("sports", 9.0, """
nfl nba nhl mlb mls wnba ncaa uefa fifa afc concacaf conmebol
icc bcci pga lpga atp wta ioc usoc nrl afl ufc wwe
""", "sport_entity")
_p("sports", 7.0, """
home run | home runs | grand slam homer | grand slam home run |
three pointer | three pointers | three point | free throw |
free throws | field goal | field goals | penalty kick |
penalty kicks | penalty shootout | penalty shoot out |
penalty shoot out | own goal | own goals | extra time |
injury time | stoppage time | overtime victory |
straight sets | straight set | match point | match points |
set point | tie break | tie breaker | tie breaking |
red card | yellow card | clean sheet | clean sheets |
hat trick | first half | second half | halftime | half time |
first quarter lead | fourth quarter comeback |
batting average | earned run average | no hitter |
perfect game | starting pitcher | relief pitcher |
opening batsman | fast bowler | spin bowler |
batting order | batting lineup | starting lineup |
starting line up | training camp | spring training |
free agent | free agents | free agency | salary cap |
draft pick | draft picks | first round pick |
trade deadline | transfer window | transfer fee |
head coach | assistant coach | offensive coordinator |
defensive coordinator | team manager | club manager |
football club | soccer club | football team | soccer team |
national team | national side | defending champion |
defending champions | world champion | world champions |
world number one | world no 1 | top seed | top seeded |
top scorer | top flight | league title | league leaders |
league championship | championship game | championship match |
championship title | championship bout | championship fight |
gold medal | silver medal | bronze medal |
gold medals | silver medals | bronze medals |
world record | world records | personal best |
pole position | pit stop | pit stops | checkered flag |
chequered flag | race track | race car | racing driver |
racing team | racing circuit | finish line |
under par | over par | golf course | golf club |
tennis court | tennis player | tennis players |
basketball court | football field | playing field |
ice hockey | field hockey | horse racing | horse race |
track and field | road race | cross country |
swimming pool | swimming championships | speed skating |
figure skating | alpine skiing | nordic skiing |
ski jumping | mountain biking | mixed martial arts |
professional wrestling | title fight | title bout |
heavyweight champion | heavyweight title | boxing ring |
anti doping | doping test | doping scandal | performance enhancing |
world anti doping agency
""", "sport_topic")
_p("sports", 8.0, """
new york yankees | boston red sox | chicago white sox |
los angeles dodgers | los angeles angels | anaheim angels |
san francisco giants | san diego padres | oakland athletics |
new york mets | philadelphia phillies | atlanta braves |
houston astros | texas rangers | seattle mariners |
st louis cardinals | saint louis cardinals | chicago cubs |
cincinnati reds | pittsburgh pirates | milwaukee brewers |
minnesota twins | detroit tigers | cleveland indians |
cleveland guardians | kansas city royals | baltimore orioles |
toronto blue jays | tampa bay rays | tampa bay devil rays |
florida marlins | miami marlins | arizona diamondbacks |
colorado rockies | washington nationals | montreal expos |
los angeles lakers | los angeles clippers | boston celtics |
new york knicks | brooklyn nets | new jersey nets |
chicago bulls | detroit pistons | miami heat | orlando magic |
cleveland cavaliers | philadelphia 76ers | philadelphia sixers |
toronto raptors | indiana pacers | milwaukee bucks |
atlanta hawks | charlotte hornets | charlotte bobcats |
washington wizards | golden state warriors | phoenix suns |
san antonio spurs | dallas mavericks | houston rockets |
denver nuggets | utah jazz | sacramento kings |
portland trail blazers | minnesota timberwolves |
oklahoma city thunder | seattle supersonics |
memphis grizzlies | new orleans pelicans | new orleans hornets |
new england patriots | kansas city chiefs | dallas cowboys |
green bay packers | pittsburgh steelers | san francisco 49ers |
new york giants | new york jets | philadelphia eagles |
chicago bears | miami dolphins | buffalo bills |
baltimore ravens | cincinnati bengals | cleveland browns |
indianapolis colts | denver broncos | los angeles rams |
st louis rams | las vegas raiders | oakland raiders |
los angeles chargers | san diego chargers |
seattle seahawks | arizona cardinals | minnesota vikings |
detroit lions | new orleans saints | atlanta falcons |
tampa bay buccaneers | carolina panthers | tennessee titans |
houston texans | jacksonville jaguars | washington commanders |
washington redskins | washington football team |
toronto maple leafs | montreal canadiens | boston bruins |
new york rangers | new york islanders | new jersey devils |
philadelphia flyers | pittsburgh penguins | washington capitals |
detroit red wings | chicago blackhawks | colorado avalanche |
vancouver canucks | edmonton oilers | calgary flames |
ottawa senators | winnipeg jets | buffalo sabres |
los angeles kings | anaheim ducks | anaheim mighty ducks |
san jose sharks | tampa bay lightning | florida panthers |
carolina hurricanes | nashville predators | st louis blues |
columbus blue jackets | minnesota wild | vegas golden knights |
seattle kraken | arizona coyotes | phoenix coyotes
""", "sport_entity")
_w("sports", 6.5, """
yankees mets phillies dodgers astros mariners orioles padres
brewers diamondbacks rockies expos lakers celtics knicks
clippers pistons cavaliers sixers 76ers raptors pacers
mavericks timberwolves supersonics grizzlies
cowboys packers steelers 49ers ravens bengals broncos
seahawks buccaneers texans patriots raiders colts
canadiens bruins canucks oilers sabres blackhawks
""", "sport_entity")
_p("sports", 8.0, """
manchester united | manchester city | man united | man city |
real madrid | atletico madrid | atletico de madrid |
fc barcelona | barcelona fc | barca |
fc bayern | bayern munich | bayern munchen |
borussia dortmund | borussia monchengladbach |
bayer leverkusen | bayer 04 | rb leipzig |
paris saint germain | paris st germain | psg |
olympique lyon | olympique lyonnais | lyon fc |
olympique marseille | as monaco |
ac milan | inter milan | internazionale | juventus |
as roma | ss lazio | atalanta | fiorentina |
tottenham hotspur | tottenham | west ham |
newcastle united | aston villa | everton |
leeds united | leicester city | crystal palace |
nottingham forest | sheffield united | sheffield wednesday |
blackburn rovers | bolton wanderers | wolverhampton wanderers |
wolves fc | west bromwich | middlesbrough |
southampton fc | fulham | sunderland |
birmingham city | portsmouth fc | ipswich town |
glasgow celtic | glasgow rangers | celtic fc | rangers fc |
ajax amsterdam | ajax | psv eindhoven | feyenoord |
fc porto | benfica | sporting lisbon | sporting cp |
galatasaray | fenerbahce | besiktas |
boca juniors | river plate | flamengo | corinthians |
santos fc | palmeiras | fluminense |
inter miami | la galaxy | los angeles galaxy |
new york red bulls | dc united | seattle sounders |
atlanta united | sporting kansas city |
chivas | club america | cruz azul |
al nassr | al hilal | al ittihad |
all blacks | wallabies | springboks | british lions |
british and irish lions | saracens | leicester tigers |
northampton saints | harlequins |
chennai super kings | mumbai indians | delhi capitals |
kolkata knight riders | royal challengers bangalore |
rajasthan royals | sunrisers hyderabad | gujarat titans |
sydney swans | collingwood | brisbane lions |
brisbane broncos | melbourne storm | penrith panthers |
st helens | wigan warriors | leeds rhinos
""", "sport_entity")
_p("sports", 8.0, """
roger federer | rafael nadal | novak djokovic | andy murray |
andre agassi | pete sampras | andy roddick | lleyton hewitt |
marat safin | carlos alcaraz | jannik sinner |
serena williams | venus williams | maria sharapova |
martina hingis | martina navratilova | chris evert |
justine henin | kim clijsters | amelie mauresmo |
lindsay davenport | jennifer capriati | elena dementieva |
naomi osaka | iga swiatek | aryna sabalenka | coco gauff |
tiger woods | phil mickelson | ernie els | vijay singh |
rory mcilroy | jack nicklaus | arnold palmer |
annika sorenstam | michelle wie | lydia ko |
scottie scheffler | brooks koepka | jon rahm |
michael schumacher | ralf schumacher | rubens barrichello |
fernando alonso | kimi raikkonen | juan pablo montoya |
jenson button | lewis hamilton | sebastian vettel |
max verstappen | charles leclerc | lando norris |
dale earnhardt | dale earnhardt jr | jeff gordon |
jimmie johnson | tony stewart | kyle busch |
michael jordan | lebron james | kobe bryant |
shaquille o'neal | shaquille oneal | shaquille o neal |
shaquille | shaq | yao ming | tim duncan |
allen iverson | kevin garnett | tracy mcgrady |
dirk nowitzki | steve nash | jason kidd |
stephen curry | steph curry | kevin durant |
nikola jokic | luka doncic | giannis antetokounmpo |
barry bonds | derek jeter | alex rodriguez |
babe ruth | hank aaron | sammy sosa | mark mcgwire |
roger clemens | pedro martinez | randy johnson |
curt schilling | david ortiz | albert pujols |
shohei ohtani | aaron judge | mike trout |
tom brady | peyton manning | eli manning |
brett favre | michael vick | terrell owens |
randy moss | jerry rice | joe montana |
aaron rodgers | patrick mahomes | josh allen |
cristiano ronaldo | lionel messi | david beckham |
zinedine zidane | ronaldo nazario | ronaldinho |
thierry henry | wayne rooney | michael owen |
david villa | luis figo | raul gonzalez |
ruud van nistelrooy | dennis bergkamp | patrick vieira |
frank lampard | steven gerrard | paul scholes |
ryan giggs | roy keane | rio ferdinand |
roberto carlos | kaka | andriy shevchenko |
samuel eto o | didier drogba | zlatan ibrahimovic |
neymar | kylian mbappe | erling haaland |
mohamed salah | kevin de bruyne | harry kane |
alex ferguson | arsene wenger | jose mourinho |
rafael benitez | carlo ancelotti | pep guardiola |
jurgen klopp | sven goran eriksson |
diego maradona | pele | johan cruyff |
sachin tendulkar | brian lara | shane warne |
ricky ponting | rahul dravid | sourav ganguly |
virender sehwag | adam gilchrist | glenn mcgrath |
muttiah muralitharan | jacques kallis | wasim akram |
shoaib akhtar | inzamam ul haq | virat kohli |
ms dhoni | mahendra singh dhoni | rohit sharma |
ben stokes | joe root | kane williamson |
michael phelps | ian thorpe | katie ledecky |
usain bolt | carl lewis | marion jones | justin gatlin |
mo farah | eliud kipchoge | paula radcliffe |
haile gebrselassie | hicham el guerrouj |
simone biles | nadia comaneci | sunisa lee |
lance armstrong | jan ullrich | floyd landis |
alberto contador | chris froome | tadej pogacar |
muhammad ali | mike tyson | lennox lewis |
evander holyfield | oscar de la hoya |
floyd mayweather | manny pacquiao | bernard hopkins |
wladimir klitschko | vitali klitschko |
tyson fury | oleksandr usyk | anthony joshua |
conor mcgregor | jon jones | khabib nurmagomedov
""", "sport_entity")
_w("sports", 6.0, """
federer nadal djokovic agassi roddick sharapova clijsters
henin mauresmo sampras swiatek alcaraz sabalenka
schumacher raikkonen verstappen barrichello montoya
mickelson sorenstam mcilroy scheffler
beckham messi ronaldo ronaldinho rooney zidane
mourinho wenger ferguson guardiola drogba mbappe haaland
tendulkar ponting sehwag gilchrist muralitharan
mcgrath warne ganguly kohli dhoni
""", "sport_entity")

# Politics, international affairs, conflict, disasters, and ordinary crime.
_w("world", 6.0, """
election elections electoral electors electorate referendum referendums
ballot ballots parliament parliamentary congress congressional senate
senator senators legislator legislators legislature legislatures
democrat democrats democratic republican republicans
diplomat diplomats diplomacy diplomatic ambassador ambassadors
embassy embassies consulate consulates
government governments governing governance regime regimes
politician politicians politics political
""", "politics")
_w("world", 4.0, """
president presidential presidency minister ministers ministerial
premier chancellor governor governors mayor mayors
administration cabinet coalition opposition
campaign campaigns campaigning candidate candidates candidacy
voter voters vote votes voted voting poll polls polling
inauguration inaugurated impeachment impeach impeached
constitution constitutional constitutional amendment amendments
legislation legislative legislating lawmakers lawmaker
treaty treaties summit summits negotiation negotiations negotiator
negotiators negotiate negotiating diplomacy geopolitical geopolitics
sanctions sanction sanctioned sovereignty sovereign independence
separatist separatists separatism autonomy autonomous
""")
_w("world", 2.5, """
federal state states national nation nations country countries
official officials authorities authority agency agencies
policy policies public domestic foreign international
democracy democratic conservative conservatives liberal liberals
socialist socialists socialism communist communists communism
nationalist nationalists nationalism populist populism
activist activists activist activism activist
civil civic rights humanitarian refugee refugees displaced
migrant migrants migration immigrant immigrants immigration
asylum deportation deportations deported deport
demonstrator demonstrators demonstration demonstrations
protest protests protested protesting protester protesters
marchers demonstrators demonstrators rally rallies
""")
_w("world", 7.0, """
war wars warfare wartime invasion invasions invade invaded invading
insurgency insurgencies insurgent insurgents militant militants
terrorism terrorist terrorists terror extremist extremists
bomb bombs bombing bombings bomber bombers bombed
airstrike airstrikes shelling artillery mortar mortars
hostage hostages abducted abduction kidnapping kidnapped
massacre massacred genocide atrocity atrocities
rebels rebel rebellion guerrilla guerrillas guerilla guerillas
assassination assassinated assassinate assassination
""", "crisis")
_w("world", 4.5, """
army armies troops troop soldier soldiers military militia militias
navy naval marines marine airforce forces fighting battle battles
battled battlefield battlefields conflict conflicts offensive
combat fighting fought clashes clash clashed firefight
ceasefire truce peacekeeping peacekeepers peacekeeper
missile missiles ballistic weapon weapons warhead warheads
arms armaments arsenal disarmament nuclear enriched enrichment
pentagon nato insurgents resistance occupation occupied
casualty casualties wounded killed killing killings dead deaths
""")
_w("world", 5.0, """
police policeman policemen policewoman policewomen
officer officers detectives detective sheriff sheriffs
arrest arrests arrested arresting detention detained detainee detainees
prison prisons prisoner prisoners jail jailed jailing
criminal criminals crime crimes homicide murder murdered
murders murderer murderers manslaughter rape raped rapist
robbery robber robberies robbers burglar burglars burglary
theft stolen stealing thief thieves smuggling smuggler smugglers
narcotics cartel cartels trafficking trafficker traffickers
gunman gunmen gunshot gunshots gunfire firearms firearm
shootout stabbing stabbed stabbings arson assault assaulted
""", "crime")
_w("world", 2.6, """
court courts courtroom courthouse judge judges judicial judiciary
justice prosecutor prosecutors prosecution prosecuting
trial trials verdict verdicts juror jurors jury juries
convict convicted conviction convictions acquitted acquittal
sentenced sentencing sentence sentences indictment indicted
indictments charges charged charging suspect suspects suspected
investigation investigations investigating investigated
illegal unlawfully unlawful legality law legal laws
appeal appeals appealed ruling ruled rulings
scandal scandals corruption corrupt bribery bribe bribed
custody extradition extradited execution executed
""")
_w("world", 6.5, """
earthquake earthquakes quake quakes tsunami tsunamis
hurricane hurricanes typhoon typhoons cyclone cyclones
tornado tornadoes tornados flood floods flooding flooded
wildfire wildfires bushfire bushfires blizzard blizzards
landslide landslides mudslide mudslides avalanche avalanches
famine famines drought droughts disaster disasters
catastrophe catastrophic catastrophe devastation devastated
evacuation evacuations evacuated evacuate evacuating
""", "crisis")
_w("world", 3.5, """
storm storms stormy rainfall rainstorm rainstorms torrential
volcano volcanic eruption eruptions eruption erupted lava
rescue rescues rescued rescuers survivor survivors survival
missing trapped injured injuries collision collisions
crash crashes crashed crashing fire fires blaze blazes
explosion explosions exploded explodes blast blasts
accident accidents accidental wreck wreckage derailed derailment
fatal fatalities fatality death toll mourning mourners funeral
""")
_p("world", 9.0, """
prime minister | deputy prime minister | foreign minister |
foreign ministry | foreign secretary | secretary of state |
secretary general | security council | united nations |
un general assembly | general assembly | european union |
european parliament | european commission | white house |
oval office | capitol hill | supreme court | high court |
constitutional court | international criminal court |
international court of justice | human rights |
civil rights | civil liberties | civil war | civil unrest |
peace talks | peace negotiations | peace deal | peace agreement |
peace process | peace treaty | peace plan | peace conference |
peace mission | peacekeeping mission | cease fire |
cease fire agreement | military coup | coup d etat |
state of emergency | martial law | emergency rule |
national security | homeland security | defense ministry |
defence ministry | defense minister | defence minister |
security forces | armed forces | armed conflict |
armed clashes | armed rebels | rebel group | rebel groups |
terrorist attack | terrorist attacks | terror attack |
terror attacks | suicide bombing | suicide bomber |
suicide bombers | car bomb | car bombing | roadside bomb |
roadside bombing | bomb blast | bomb blasts |
bomb attack | bomb attacks | missile strike | missile strikes |
rocket attack | rocket attacks | air strike | air strikes |
nuclear weapons | nuclear weapon | nuclear arms |
nuclear bomb | nuclear bombs | nuclear program | nuclear programme |
uranium enrichment | enriched uranium | atomic bomb |
weapons of mass destruction | weapons inspector |
weapons inspectors | war crimes | war criminal |
ethnic cleansing | ethnic violence | sectarian violence |
religious violence | border dispute | border clashes |
military operation | military operations | ground offensive |
ground invasion | troop withdrawal | military withdrawal |
hostage crisis | hostage taking | hostage release |
prisoner exchange | refugee camp | refugee camps |
asylum seeker | asylum seekers | refugee crisis |
illegal immigration | immigration law | border security |
humanitarian aid | humanitarian crisis | famine relief |
death toll | killed in | people killed | people died |
natural disaster | natural disasters | disaster relief |
earthquake victims | tsunami victims | hurricane victims |
plane crash | air crash | airplane crash | aircraft crash |
train crash | train derailment | bus crash | ferry disaster |
ferry sinking | building collapse | mine disaster |
mining disaster | oil spill | oil slick | heat wave | heatwave |
mass shooting | school shooting | shooting spree |
serial killer | serial murder | murder suspect |
murder charges | murder trial | murder conviction |
death penalty | death sentence | capital punishment |
drug trafficking | drug smuggling | drug cartel |
organized crime | organised crime | human trafficking |
child abuse | sexual abuse | sexual assault | domestic violence
""")
_p("world", 7.5, """
plane crash | air crash | airplane crash | aircraft crash |
train crash | train derailment | bus crash | ferry disaster |
ferry sinking | building collapse | mine disaster |
mining disaster | natural disaster | heat wave | heatwave |
mass shooting | school shooting | shooting spree |
suicide bombing | suicide bomber | car bomb |
roadside bomb | bomb blast | terrorist attack |
terror attack | hostage crisis | oil spill
""", "crisis")
_p("world", 7.0, """
presidential election | parliamentary election | general election |
national election | election campaign | election results |
election victory | election defeat | presidential candidate |
presidential debate | presidential race | presidential campaign |
presidential nomination | presidential nominee |
democratic nominee | republican nominee | democratic party |
republican party | labour party | labor party |
conservative party | liberal party | communist party |
democratic convention | republican convention |
democratic national convention | republican national convention |
party leader | opposition leader | opposition party |
ruling party | governing party | political party |
political parties | political crisis | political reform |
vote of confidence | no confidence | confidence vote |
voter turnout | exit poll | exit polls | opinion poll |
opinion polls | polling station | polling stations |
ballot box | electoral college | electoral commission |
campaign finance | campaign trail | peace prize |
nobel peace prize | supreme leader | military junta |
constitutional amendment | gay marriage | same sex marriage |
abortion rights | gun control | gun rights |
criminal justice | police reform | death row |
social security reform | immigration reform |
health care reform | healthcare reform |
public spending bill | government shutdown | debt ceiling |
state department | justice department | home office |
ministry of interior | interior ministry | interior minister
""", "politics")
_w("world", 7.0, """
nato interpol cia fbi taliban hamas hezbollah hizbollah
hizbullah fatah isis isil daesh
""")
_p("world", 8.0, """
al qaeda | al qaida | al queda | islamic state |
islamic jihad | muslim brotherhood | boko haram |
al shabaab | abu sayyaf | liberation tigers |
tamil tigers | irish republican army |
revolutionary guards | revolutionary guard |
iranian revolutionary guard | palestinian authority |
palestine liberation organization | african union |
arab league | red cross | red crescent |
amnesty international | human rights watch |
international atomic energy agency | iaea |
north atlantic treaty organization | organization for security |
organization of american states
""")
_w("world", 4.0, """
iraq iraqi iraqis baghdad fallujah falluja mosul basra
afghanistan afghan afghans kabul kandahar
palestine palestinian palestinians gaza ramallah
israel israeli israelis jerusalem
iran iranian iranians tehran
syria syrian syrians damascus
darfur sudan sudanese somalia somali mogadishu
chechnya chechen chechens grozny
""")
_p("world", 5.0, """
west bank | gaza strip | middle east | north korea |
south sudan | east timor | east jerusalem |
occupied territories | occupied west bank |
korean peninsula | south china sea | taiwan strait |
strait of hormuz | demilitarized zone |
line of control | disputed territory |
kashmir region | nagorno karabakh
""")
_w("world", 0.8, """
russia russian russians ukraine ukrainian ukrainians
china chinese india indian pakistan pakistani
japan japanese korea korean france french germany german
britain british england english italy italian spain spanish
canada canadian australia australian brazil brazilian
mexico mexican venezuela venezuelan colombia colombian
indonesia indonesian philippines philippine filipino
thailand thai myanmar burma burmese bangladesh bangladeshi
srilanka nepal nepalese tibet tibetan hongkong
egypt egyptian lebanon lebanese saudi saudis
turkey turkish turkiye libya libyan yemen yemeni
nigeria nigerian kenya kenyan ethiopia ethiopian
rwanda rwandan congo congolese zimbabwe zimbabwean
haiti haitian cuba cuban
""")
_w("world", 5.5, """
biden obama trump putin zelensky zelenskyy zelenskiy
netanyahu arafat abbas musharraf karzai
erdogan macron scholz merkel chirac sarkozy hollande
blair sunak starmer berlusconi prodi meloni
modi gandhi vajpayee singh
mugabe mandela zuma ramaphosa
mubarak morsi sisi assad gaddafi khamenei khomeini
ahmadinejad rouhani rouhani raisi
lukashenko milosevic karadzic
fujimori chavez maduro castro
yudhoyono megawati thaksin duterte
""", "politics")
_w("world", 3.0, "bush kerry cheney rumsfeld sharon arafat", "politics")
_p("world", 8.0, """
george bush | george w bush | george h w bush |
john kerry | john edwards | dick cheney |
donald rumsfeld | colin powell | condoleezza rice |
barack obama | joe biden | donald trump |
kamala harris | hillary clinton | bill clinton |
chelsea clinton | gerald ford | jimmy carter |
ronald reagan | nancy pelosi | mike pence |
bernie sanders | mitt romney | john mccain |
tony blair | gordon brown | david cameron |
theresa may | boris johnson | liz truss |
rishi sunak | keir starmer | michael howard |
vladimir putin | dmitry medvedev | vladimir zelensky |
volodymyr zelensky | volodymyr zelenskyy |
xi jinping | hu jintao | jiang zemin | wen jiabao |
li keqiang | li qiang | shinzo abe | junichiro koizumi |
fumio kishida | shigeru ishiba | kim jong un |
kim jong il | kim il sung | roh moo hyun |
lee myung bak | park geun hye | yoon suk yeol |
moon jae in | lai ching te | chen shui bian |
tsai ing wen | ma ying jeou |
narendra modi | manmohan singh | sonia gandhi |
rahul gandhi | atal bihari vajpayee |
pervez musharraf | nawaz sharif | benazir bhutto |
asif ali zardari | imran khan | shehbaz sharif |
hamid karzai | ashraf ghani | abdullah abdullah |
saddam hussein | osama bin laden | bin laden |
abu musab al zarqawi | abu bakr al baghdadi |
ariel sharon | benjamin netanyahu | yasser arafat |
mahmoud abbas | ehud olmert | ehud barak |
yitzhak rabin | shimon peres |
recep tayyip erdogan | bashar al assad |
mahmoud ahmadinejad | ali khamenei | hassan rouhani |
ebrahim raisi | hosni mubarak | abdel fattah al sisi |
jacques chirac | emmanuel macron | angela merkel |
gerhard schroeder | olaf scholz | silvio berlusconi |
jose luis rodriguez zapatero | jose maria aznar |
lula da silva | luiz inacio lula | jair bolsonaro |
hugo chavez | nicolas maduro | fidel castro | raul castro |
nelson mandela | thabo mbeki | robert mugabe |
kofi annan | ban ki moon | antonio guterres |
javier solana | josep borrell | ursula von der leyen |
jose manuel barroso | romano prodi |
pope francis | pope benedict | pope john paul |
john paul ii | dalai lama | ayatollah khamenei |
king charles | queen elizabeth | prince william |
prince harry | king abdullah | king salman |
mohammed bin salman | mohammed bin zayed
""", "politics")
_w("world", 4.0, """
pope papal vatican pontiff church churches cathedral
mosque mosques synagogue synagogues religion religious
catholic catholics christian christians christianity islam islamic
muslim muslims jewish judaism hindu hindus buddhist buddhism
clergy priest priests bishop bishops archbishop rabbi rabbis imam imams
monarch monarchy royal royalty king queen prince princess
""")
_w("world", 1.5, """
culture cultural heritage museum museums art artwork artworks
painting paintings exhibition exhibitions festival festivals
concert concerts celebrity celebrities actor actors actress actresses
singer singers musician musicians author authors novel novels
literature literary book books film films movie movies
""")
_p("world", 4.0, """
academy awards | nobel prize in literature | nobel literature prize |
cannes film festival | venice film festival |
booker prize | cultural heritage | world heritage |
religious freedom | freedom of speech | freedom of expression |
freedom of religion | press freedom | censorship |
human rights abuses | human rights violations |
united nations children fund | unicef | unesco
""")

_INDEX = defaultdict(list)
for _key, (_weights, _roles) in _RULES.items():
    _INDEX[_key[0]].append((_key, tuple(_weights), tuple(_roles)))


_FINANCE_WORDS = set("""
earnings profit profits revenue revenues sales shares shareholder shareholders
stock stocks dividend dividends merger mergers acquisition acquisitions
takeover takeovers buyout buyouts bankruptcy layoffs layoff restructuring
quarterly valuation valuations antitrust monopoly monopolies
""".split())

_LEGAL_WORDS = set("""
sue sued suing lawsuit lawsuits litigation antitrust monopoly monopolies
patent patents copyright copyrights infringement settlement settlements
regulator regulators regulation regulatory court courts judge judges
fined fine fines ruling appeal appeals probe probes investigation
""".split())

_SPORT_CONTEXT = set("""
sport sports football soccer baseball basketball hockey tennis golf cricket
rugby league leagues team teams coach coaches player players game games match
matches win wins won winning beat beats beating defeated defeat championship
champion champions tournament playoffs playoff scored scoring goal goals
season season opener innings inning pitcher touchdown quarterback points
medal medals olympic olympics cup roster trade traded transfer signing
stadium racing race grand prix f1 nba nfl mlb nhl ncaa uefa fifa
""".split())

_CORPORATE_CONTEXT = set("""
shares stock stocks earnings revenue revenues profit profits sales company
corporation corp inc ltd ceo merger acquisition takeover quarterly
executive software hardware computers computer chip chips semiconductor
smartphone smartphones phone phones mobile telecom wireless broadband
announced launches launched launch unveil unveils unveiled
""".split())

_AMBIGUOUS_TEAMS = set("""
Arsenal Chelsea Liverpool Barcelona Rangers Reds Ravens Bears Jets Eagles
Dolphins Panthers Saints Chargers Titans Chiefs Pirates Twins Royals
Athletics Magic Heat Suns Jazz Bucks Pacers Blazers Kings Wizards Warriors
Bulls Rockets Braves Tigers Cardinals Cubs Giants Hawks Pelicans Nuggets
Spurs Lightning Hurricanes Ducks Sharks Flames Senators Capitals Flyers
Penguins Predators Wild Coyotes Thunder Hornets Lions Jaguars Vikings
""".split())


def _position_weight(pos):
    if pos < 12:
        return 1.40
    if pos < 30:
        return 1.20
    if pos < 65:
        return 1.0
    return max(0.35, 1.0 / (1.0 + (pos - 65) / 220.0))


def _first(role_hits, role, default=1000000):
    hits = role_hits.get(role)
    if not hits:
        return default
    return min(item[0] for item in hits)


def _strength(role_hits, role):
    return sum(item[1] for item in role_hits.get(role, ()))


def _extra(scores, role_hits, category, weight, pos, role=None):
    amount = weight * _position_weight(pos)
    scores[category] += amount
    if role:
        role_hits[role].append((pos, amount))


def _extract_text(state):
    if isinstance(state, str):
        return state
    if isinstance(state, dict):
        pieces = []
        for key in ("title", "headline", "text", "description", "summary", "body", "article", "content"):
            value = state.get(key)
            if isinstance(value, str) and value and value not in pieces:
                pieces.append(value)
        if pieces:
            return " ".join(pieces)
        for key in ("state", "input", "news"):
            if key in state:
                return _extract_text(state[key])
        return ""
    if isinstance(state, (list, tuple)):
        return " ".join(_extract_text(item) for item in state)
    return ""


def predict(state):
    text = _extract_text(state)
    clean = _clean(text)
    original_tokens = re.findall(r"[A-Za-z0-9]+", clean)
    tokens = [word.lower() for word in original_tokens]
    if not tokens:
        return {"answer": "world"}

    vocabulary = set(tokens)
    positions = {}
    for pos, token in enumerate(tokens):
        if token not in positions:
            positions[token] = pos

    matched = {}
    for pos, token in enumerate(tokens):
        for key, weights, roles in _INDEX.get(token, ()):
            length = len(key)
            if length == 1 or tuple(tokens[pos:pos + length]) == key:
                if key in matched:
                    matched[key][0] += 1
                else:
                    matched[key] = [1, pos, weights, roles]

    scores = [0.25, 0.15, 0.05, 0.40]
    role_hits = defaultdict(list)
    for count, pos, weights, roles in matched.values():
        multiplier = _position_weight(pos) * (1.0 + 0.22 * min(count - 1, 3))
        for index, weight in enumerate(weights):
            scores[index] += weight * multiplier
        strength = max(weights) * multiplier
        for role in roles:
            role_hits[role].append((pos, strength))

    finance_context = bool(vocabulary & _FINANCE_WORDS)
    legal_context = bool(vocabulary & _LEGAL_WORDS)
    corporate_context = bool(vocabulary & _CORPORATE_CONTEXT)
    sports_context = bool(vocabulary & _SPORT_CONTEXT)

    # Names that are also ordinary words require contextual interpretation.
    fruit = bool(vocabulary & {
        "orchard", "orchards", "grower", "growers", "fruit", "fruits",
        "apples", "cider", "harvest", "orcharding", "juice",
    })
    apple_technology = bool(vocabulary & {
        "iphone", "ipad", "ipod", "mac", "macintosh", "macbook", "imac",
        "itunes", "ios", "software", "computers", "smartphone", "smartphones",
        "earnings", "shares", "antitrust", "ceo", "revenue", "airpods",
    })
    if "apple" in positions and (not fruit or apple_technology):
        p = positions["apple"]
        if original_tokens[p][:1].isupper() or corporate_context or apple_technology:
            _extra(scores, role_hits, 1, 8.0, p, "tech_firm")

    amazon_geography = bool(vocabulary & {
        "rainforest", "rainforests", "river", "basin", "jungle",
        "deforestation", "indigenous", "tribe", "tribes",
    })
    amazon_company = bool(vocabulary & {
        "kindle", "aws", "bezos", "ecommerce", "retailer", "retailing",
        "earnings", "shares", "prime", "cloud", "alexa",
    })
    if "amazon" in positions and (not amazon_geography or amazon_company):
        p = positions["amazon"]
        if original_tokens[p][:1].isupper() or corporate_context:
            _extra(scores, role_hits, 1, 8.0, p, "tech_firm")

    for term in ("alphabet", "meta"):
        if term in positions:
            p = positions[term]
            related = vocabulary & {
                "google", "facebook", "instagram", "threads", "whatsapp",
                "zuckerberg", "pichai", "advertising", "social",
            }
            if original_tokens[p][:1].isupper() and (corporate_context or related):
                _extra(scores, role_hits, 1, 8.0, p, "tech_firm")

    telecom_context = bool(vocabulary & {
        "telecom", "telecommunications", "phone", "phones", "mobile",
        "wireless", "nextel", "broadband", "cellular", "handset", "handsets",
    })
    for term in ("sprint", "orange"):
        if term in positions:
            p = positions[term]
            if telecom_context or (
                term == "sprint" and original_tokens[p][:1].isupper()
                and finance_context
            ):
                _extra(scores, role_hits, 1, 8.0, p, "tech_firm")

    if "sun" in positions:
        p = positions["sun"]
        if original_tokens[p][:1].isupper() and (
            finance_context or vocabulary & {
                "microsystems", "servers", "java", "solaris", "workstations",
                "software", "semiconductor",
            }
        ):
            _extra(scores, role_hits, 1, 7.5, p, "tech_firm")
        elif vocabulary & {
            "solar", "astronomers", "astronomer", "orbit", "planet",
            "eclipse", "sunspot", "sunspots", "corona",
        }:
            _extra(scores, role_hits, 1, 4.0, p, "space")

    for term in ("sap", "rim", "arm", "sharp"):
        if term not in positions:
            continue
        p = positions[term]
        capitalized = original_tokens[p][:1].isupper()
        related = False
        if term == "sap":
            related = original_tokens[p] == "SAP" or bool(
                vocabulary & {"software", "enterprise", "oracle", "erp"}
            )
        elif term == "rim":
            related = original_tokens[p] == "RIM" and (
                corporate_context or "blackberry" in vocabulary
            )
        elif term == "arm":
            related = capitalized and (
                finance_context or bool(vocabulary & {
                    "chip", "chips", "semiconductor", "processor", "processors",
                    "holdings", "nvidia", "architecture",
                })
            )
        else:
            related = capitalized and bool(vocabulary & {
                "electronics", "lcd", "oled", "televisions", "display", "displays",
                "earnings", "revenue", "shares",
            })
        if related:
            _extra(scores, role_hits, 1, 7.5, p, "tech_firm")

    if "windows" in positions:
        p = positions["windows"]
        literal_windows = bool(vocabulary & {
            "shattered", "smashed", "stained", "broken", "burglar",
            "glazing", "windowpanes", "blown",
        })
        computing_context = bool(vocabulary & {
            "microsoft", "software", "operating", "xp", "vista", "pc", "pcs",
            "computer", "computers", "browser", "patch", "security", "update",
        })
        if computing_context or (
            original_tokens[p] == "Windows" and not literal_windows
        ):
            _extra(scores, role_hits, 1, 6.5, p, "technology")

    if "shell" in positions and vocabulary & {
        "oil", "petroleum", "gas", "refinery", "refineries", "earnings",
        "shares", "profits", "barrel", "barrels",
    }:
        _extra(scores, role_hits, 0, 6.5, positions["shell"], "business_firm")

    if "mars" in positions and vocabulary & {
        "chocolate", "candy", "confectionery", "snickers", "confectioner",
    }:
        scores[1] = max(0.0, scores[1] - 4.5 * _position_weight(positions["mars"]))
        _extra(scores, role_hits, 0, 6.5, positions["mars"], "business_firm")

    seen_teams = set()
    for pos, original in enumerate(original_tokens):
        if original not in _AMBIGUOUS_TEAMS or original in seen_teams:
            continue
        seen_teams.add(original)
        lower = original.lower()
        if lower == "chelsea" and "clinton" in vocabulary:
            continue
        if lower == "arsenal" and not sports_context and vocabulary & {
            "nuclear", "weapons", "military", "missiles", "arms", "warheads",
        }:
            continue
        if lower in {"heat", "magic", "jazz", "kings", "royals", "bulls", "wild"}:
            weight = 3.5 if sports_context else 0.0
        elif lower in {"arsenal", "chelsea", "liverpool", "barcelona"}:
            weight = 6.0 if sports_context else 3.0
        else:
            weight = 4.0 if sports_context else 0.8
        if weight:
            _extra(scores, role_hits, 2, weight, pos, "sport_entity")

    # Explicit scores and competition records supply useful evidence independent
    # of the particular participants' names.
    score_matches = re.findall(
        r"(?<![\d./])(\d{1,3})\s*[-:]\s*(\d{1,3})(?![\d./])", clean
    )
    plausible_scores = []
    for a, b in score_matches:
        x, y = int(a), int(b)
        if x <= 160 and y <= 160 and not (x == 0 and y == 0):
            plausible_scores.append((x, y))
    if plausible_scores:
        if sports_context or scores[2] >= 8:
            scores[2] += min(13.0, 5.0 + 2.0 * len(plausible_scores))
        elif len(plausible_scores) >= 2 and all(
            x <= 15 and y <= 15 for x, y in plausible_scores
        ):
            scores[2] += 9.0
        elif not vocabulary & {
            "vote", "voted", "votes", "court", "senate", "percent",
            "percentage", "hours", "years", "months", "ratio",
        }:
            scores[2] += 2.0

    if re.search(r"[$\u00a3\u20ac]\s*\d", text):
        scores[0] += 2.2
    if re.search(r"\d(?:\.\d+)?\s*%", text) and finance_context:
        scores[0] += 2.0

    tech_firm_first = _first(role_hits, "tech_firm")
    business_firm_first = _first(role_hits, "business_firm")
    technology_first = _first(role_hits, "technology")
    research_first = _first(role_hits, "research")
    sport_first = _first(role_hits, "sport_entity")
    macro_first = _first(role_hits, "macro")
    crisis_first = _first(role_hits, "crisis")

    financial_positions = [
        positions[word] for word in _FINANCE_WORDS if word in positions
    ]
    financial_first = min(financial_positions, default=1000000)
    legal_positions = [
        positions[word] for word in _LEGAL_WORDS if word in positions
    ]
    legal_first = min(legal_positions, default=1000000)

    # Broad market coverage is business, even when individual technology
    # companies are cited as the cause of an index's movement.
    macro_primary = (
        macro_first <= 16
        and (
            macro_first < tech_firm_first
            or (macro_first <= 3 and tech_firm_first > 3)
        )
        and not (
            technology_first < macro_first
            and _strength(role_hits, "technology") >= 12
        )
    )
    if macro_primary:
        scores[0] += 5.0
        firm_evidence = _strength(role_hits, "tech_firm")
        if firm_evidence:
            scores[1] = max(0.0, scores[1] - 0.45 * firm_evidence)
            scores[0] += min(13.0, 0.45 * firm_evidence)

    # For a technology-company story, profits, acquisitions, and lawsuits
    # describe the event, rather than changing the sector of the story.
    tech_focus = tech_firm_first <= 30 or (
        technology_first <= 20
        and _strength(role_hits, "technology") >= 9
        and tech_firm_first <= 75
    )
    unnamed_tech_focus = (
        technology_first <= 17
        and _strength(role_hits, "technology") >= 11
        and business_firm_first > 24
    )
    outside_company_primary = (
        business_firm_first < tech_firm_first
        and business_firm_first <= 15
        and technology_first > business_firm_first
        and _strength(role_hits, "business_firm")
        > 1.25 * _strength(role_hits, "tech_firm")
    )
    if not macro_primary and not outside_company_primary:
        if (tech_focus or unnamed_tech_focus) and finance_context:
            scores[1] += min(40.0, 0.90 * scores[0])
            scores[0] *= 0.82
        if (tech_focus or unnamed_tech_focus) and legal_context:
            scores[1] += min(22.0, 0.48 * scores[3])
        if (
            technology_first <= 18
            and _strength(role_hits, "technology") >= 13
            and legal_context
            and crisis_first > 20
        ):
            scores[1] += min(12.0, 0.28 * scores[3])

    # A medical or scientific study is distinct from a general outbreak,
    # disaster, or public-policy article that merely mentions science.
    if (
        research_first <= 22
        and _strength(role_hits, "research") >= 12
        and research_first < crisis_first
    ):
        scores[1] += min(9.0, 0.20 * scores[3])

    # Ordinary companies' financial results are business even when their
    # products happen to have a medical or athletic application.
    if (
        business_firm_first <= 24
        and financial_first <= 16
        and tech_firm_first > 35
        and research_first > financial_first
        and not macro_primary
    ):
        scores[0] += min(12.0, 0.25 * scores[1] + 0.15 * scores[2])

    if (
        sport_first <= 17 and sports_context
        and not (
            business_firm_first < sport_first
            and financial_first <= 12
        )
    ):
        scores[2] += 2.5
        if finance_context and business_firm_first > sport_first:
            scores[2] += min(7.0, 0.22 * scores[0])

    # Console and computer-game reporting is technology, not competitive sport.
    gaming_phrases = (
        ("video", "game"), ("video", "games"), ("computer", "game"),
        ("computer", "games"), ("game", "console"), ("gaming", "console"),
    )
    if any(phrase in matched for phrase in gaming_phrases):
        if technology_first <= 22 and tech_firm_first <= 35:
            scores[1] += min(10.0, 0.25 * scores[2])

    # Catastrophes involving commercial carriers remain disaster news unless
    # the leading subject is their financial impact.
    if (
        crisis_first <= 15
        and financial_first >= crisis_first
        and not macro_primary
    ):
        scores[3] += 5.0
        if vocabulary & {
            "passengers", "passenger", "airliner", "airlines", "airline",
            "ferry", "derailed", "derailment",
        }:
            scores[3] += 3.5

    # Some abbreviations are informative only with the appropriate context.
    if "sec" in vocabulary and finance_context and not sports_context:
        scores[0] += 3.0
    if "ai" in vocabulary and (
        corporate_context
        or vocabulary & {
            "model", "models", "intelligence", "chatbot", "chatbots",
            "generative", "neural", "training", "technology", "robot",
        }
    ):
        scores[1] += 6.0
    if "pc" in vocabulary or "pcs" in vocabulary:
        if vocabulary & {
            "computer", "computers", "sales", "software", "windows",
            "gaming", "hardware", "dell", "hp", "ibm", "intel",
        }:
            scores[1] += 5.0
    if "fda" in vocabulary and vocabulary & {
        "drug", "drugs", "vaccine", "vaccines", "approval", "approves",
        "approved", "safety", "treatment", "patients", "clinical",
    }:
        scores[1] += 5.0

    best = max(range(4), key=lambda index: scores[index])
    return {"answer": _LABELS[best]}