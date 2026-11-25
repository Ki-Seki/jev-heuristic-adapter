import re
import math
import unicodedata
import difflib
from collections import Counter, defaultdict
from functools import lru_cache


# Short reference utterances for lexical evidence. Each row is one intent.
_REFERENCES = """
activate_my_card|How do I activate my new card?|I just received my card how do I start using it?|My activation didn't work|What do I need to do before using the card for the first time?|Activate this card in the app|I need help with card activation|How can I enable my card?|Got my card in the mail what do I do next?
age_limit|Is there an age limit?|How old do you need to be to open an account?|I am 16 can I have my own card?|Can I get an account for my daughter?|Can my children use your services?|minimum age to sign up|Are minors eligible for an account?|Can a teenager get a card?|Can my son who is under eighteen join?
apple_pay_or_google_pay|Can I use Apple Pay or Google Pay?|Can I connect my card to my apple wallet?|Do you support googlepay?|How do I top up using android pay?|Apple watch payments|Can I pay with my iPhone?|Can I use Google wallet to add funds?|Add my virtual card to Apple pay
atm_support|Which ATMs can I use to withdraw money?|Where can I take cash out?|What cash machines accept this card?|Can I withdraw at any ATM abroad?|Where is the nearest supported ATM?|What ATM network can I use?|Where do I find compatible cashpoints?|Is it possible to withdraw money from a machine using this card?
automatic_top_up|How do I set up automatic top ups?|Can the account top itself up when my balance runs low?|Turn off auto top up|Is there a way to add money automatically?|Set up a recurring topup|Can I schedule regular topups?|Why did auto topup not work?|How can I make sure I never run out of funds?
balance_not_updated_after_bank_transfer|I transferred money from my bank but my balance hasn't changed|My bank transfer is not showing in my account|Someone sent me a transfer but it still isn't there|My incoming transfer has not been credited|Where is the money my bank sent to this account?|Money transferred in is missing from the balance|Made a deposit by bank transfer and my balance hasn't been updated|Why haven't I received my bank transfer?|My salary hasn't arrived in my account|The money left my other bank but hasn't reached this account
balance_not_updated_after_cheque_or_cash_deposit|I deposited a cheque but the money hasn't shown up|My cash deposit hasn't been credited to the account|When will my cheque clear?|Why hasn't the cash I deposited been added to my balance?|I deposited a check a week ago still no money|Where is my cash deposit?|I mailed you a cheque but my balance has not changed
beneficiary_not_allowed|Why is my beneficiary not allowed?|I'm not allowed to transfer to this particular recipient|I can't add the beneficiary|Can I transfer to a cryptocurrency exchange?|Why can't I send money to this beneficiary?|The account I want to transfer to is not supported|It says the merchant account is restricted|Which beneficiaries are not supported for transfers?|Can't transfer to a broker
cancel_transfer|Can I cancel a transfer?|I sent money to the wrong person how do I get it back?|I need to reverse the bank transfer I just made|Can I stop a scheduled transfer?|Wrong account details on my transfer|I made a transfer by mistake can you recall it?|I don't want my transfer to go through|Can a completed transfer be cancelled?|Please stop money I sent from going through
card_about_to_expire|My card is about to expire|Will I get a new card when my old one expires?|The expiration date is next month|Do I have to order a replacement when it runs out?|How do I renew an expired card?|My card is no longer valid past this month|What happens when the expiry date passes?
card_acceptance|Where can I use my card?|Which merchants accept my card?|Can I pay with my card abroad?|Will my card be accepted in every country?|What businesses accept this card?|Can I buy things online with the card?|Are there places I can't use the card?|Can I use my card in the US?|Will shops and restaurants take this card?|Can the card be used anywhere?
card_arrival|My card hasn't arrived yet|Where is the card I ordered?|I have waited weeks and my card is still not here|Can I track the delivery of my card?|What is the status of my card order?|Card appears to be lost in the post|The expected delivery date passed and no card|My card was supposed to be here yesterday|Has my card been sent out yet?|My new card never came|I ordered a card and still haven't received it
card_delivery_estimate|How long does it take for a card to arrive?|What is the estimated delivery time?|When will my new card be delivered?|Can I get express delivery?|Is there a way to get the card faster?|How many days does standard delivery take?|I need a card by Friday can you expedite shipping?|What are my delivery options?|How quickly can you ship me a card?|When can I expect my card?
card_linking|How do I link my card to the app?|Can I link an existing card to this account?|How do I connect a card I already have?|My card doesn't appear in the app|How can I unlink a card?|I found my old card how do I link it again?|Can I associate multiple cards with a single account?|Can I add my card to the app?|I need help pairing my card
card_not_working|My card isn't working|My card stopped working suddenly|Why doesn't my card work anywhere?|I can't get my physical card to work|Card appears to be damaged|Card is broken and won't work|Chip and pin won't work|The terminal won't read my card|I'm having problems using my card|I've tried my card several times but it does not work
card_payment_fee_charged|Why was I charged a fee for paying by card?|Are there fees for card payments?|Merchant charged extra for using my card|I paid with my card and was charged a surcharge|Why is there a fee for my card purchase?|Extra charges for paying abroad by card|I was charged commission for my card transaction|I thought card payments were free
card_payment_not_recognised|I don't recognise this card payment|There's a purchase on my statement that I didn't make|I've never been to this merchant|There is a strange payment on my account|My card has a transaction I know nothing about|There is an unauthorized card payment|I see a charge that is not mine|I didn't buy anything but a payment is showing|I don't remember making this transaction|A payment I never made is showing in the app
card_payment_wrong_exchange_rate|The exchange rate used for my card payment is wrong|I paid in a foreign currency but the conversion rate was terrible|My purchase used a different exchange rate than expected|Wrong rate on a purchase abroad|I paid in euros and the conversion to pounds was incorrect|Why was the conversion rate so high when paying by card?|Wrong currency conversion for a card transaction|The price of something I bought is wrong after conversion
card_swallowed|The ATM swallowed my card|The machine didn't give me my card back|Cash machine kept my card|My card is stuck in an ATM|How do I get my card out of the machine?|The ATM retained my card|The cashpoint ate my card|My card was taken by the cash machine
cash_withdrawal_charge|Is there a charge for withdrawing cash?|Why did the ATM charge a fee?|I got charged extra for taking money out|Are cash withdrawals free?|What are the charges for using a cash machine abroad?|ATM withdrawal fees|How much does it cost to withdraw cash?|Why am I being charged when I get cash?
cash_withdrawal_not_recognised|There's a cash withdrawal I didn't make|I don't recognise an ATM withdrawal|Someone took cash from my account using an ATM|Cash was withdrawn and it wasn't me|I never went to this cash machine|A withdrawal on my statement is not mine|There is an unauthorized cash withdrawal showing|I didn't take any cash out today
change_pin|How do I change my PIN?|Can I choose a new card PIN?|What ATMs let me change my pin?|I want to reset my card pin number|Can I set a different PIN in the app?|Where can I update my PIN?|I would like to use my own PIN
compromised_card|I think my card has been compromised|Someone else has access to my card details|My card has been cloned|My card details were stolen online|I'm afraid someone is using my card without my permission|What should I do if my card has been hacked?|My card information has been exposed|I think someone copied my card|Someone knows my card number|My card security has been compromised
contactless_not_working|Contactless doesn't work|Why is tap to pay not working?|Card works with pin but not by tapping|The contactless feature has stopped working|My contactless payment was declined|Paywave doesn't work on my card|The reader will not accept my contactless card|I cannot pay by tapping the terminal
country_support|Which countries do you support?|Can residents of Australia open an account?|Is your service available in my country?|Can I get an account if I live outside Europe?|Where do I have to live to be eligible?|In which countries can I open an account?|Do you issue cards to US residents?|Can I sign up from abroad?|What countries are you available in?
declined_card_payment|My card payment was declined|My payment in a shop got rejected|I have money but my card purchase was refused|Why can't I make a payment at a merchant?|Online transaction was declined|The terminal declines my payment although I have enough money|My card was declined when trying to buy something|Why wouldn't my payment go through?
declined_cash_withdrawal|Why was my cash withdrawal declined?|ATM won't let me withdraw money|My withdrawal was rejected although I have enough money|I was refused cash at a cashpoint|I can't get money out of the ATM|Cash machine said transaction declined|I tried to take cash out but it failed|The ATM keeps denying my request
declined_transfer|Why was my transfer declined?|My bank transfer was rejected|It says my transfer is declined|The bank refused the transfer|Why would a money transfer be denied?|I have funds but the transfer got declined
direct_debit_payment_not_recognised|I don't recognize a direct debit payment|A direct debit I didn't set up has appeared|I did not authorize this direct debit|Who set up this direct debit on my account?|What is this unknown direct debit?|Direct debit taken without my permission
disposable_card_limits|What are the limits on disposable cards?|How many disposable virtual cards can I use?|How often can I use a disposable card?|What's the maximum spend on a disposable card?|Are there restrictions on single use cards?|How many times can I use one disposable card?|Is there a limit to the number of disposable cards?|What can I use a disposable virtual card for?
edit_personal_details|How do I change my address?|I want to update my personal information|My phone number has changed|Where can I change my email address?|I got married how do I change my name?|My personal details are incorrect|Can I edit my profile details?|My billing address needs to be updated|I've moved house and need to change my address|How can I correct my date of birth?
exchange_charge|How much do you charge for currency exchange?|Is there a fee to exchange currencies?|Are there markups on the exchange rate?|Why was I charged commission on my exchange?|Extra fees for exchanging over the weekend|Is currency conversion free?|How much does it cost to convert pounds to euros?|Are there exchange fees after a certain limit?
exchange_rate|What exchange rate do you use?|How are your foreign exchange rates calculated?|Where can I see the current conversion rate?|What is your rate for dollars to euros?|Is the exchange rate live?|Do you use the interbank exchange rate?|How often is the rate updated?|Where do the exchange rates come from?|Where can I find out what the exchange rate is?
exchange_via_app|How do I exchange money in the app?|Can I change dollars to pounds?|I want to convert my balance to a different currency|How do I make a currency exchange?|Can I exchange currency through the application?|How do I change between currencies?|Can I buy euros in the app?|How do I convert GBP into USD?
extra_charge_on_statement|What is the extra charge on my statement?|There is a small extra amount on my statement|Why is there a one pound charge on my account?|I see an extra small transaction I wasn't expecting|What is the extra dollar that has been taken?|Why am I seeing a small charge after paying?|There is an odd additional charge on my statement|Why was I charged an extra pound at the petrol station?
failed_transfer|My transfer failed|Why did my bank transfer not go through?|I got an error trying to transfer money|My transfer was unsuccessful|My money transfer keeps failing|I tried sending money but it didn't work|My transfer was returned to me|Why can't I complete my transfer?|What are the reasons a transfer might fail?
fiat_currency_support|Which fiat currencies can I hold in my account?|Can I have multiple currencies in one account?|What currencies do you support?|Can I keep a balance in dollars?|Can my account hold euros as well as pounds?|Which currencies are available to hold?|How do I add another currency account?|What currency balances can I open?|Can I hold more than one currency?
get_disposable_virtual_card|How do I get a disposable virtual card?|Where can I order a single use card?|I want to create a disposable card|Can I get a throwaway virtual card?|What is a disposable virtual card?|How do I generate a new disposable card number?|Can you tell me about one time use cards?
get_physical_card|How can I find my card PIN?|Where is the PIN for my physical card?|Will the pin come separately in the post?|I got my card but no PIN|How can I see the PIN number?|I need the pin to my new card|When do I receive my PIN?|Where can I get a PIN for the card?
getting_spare_card|Can I get a spare card?|Is it possible to order a second physical card?|I need an extra card as a backup|How many cards can I have for one account?|Can I have two active cards?|Can I order an additional card for my wife?|Can I get another card linked to my account?|I'd like a duplicate card
getting_virtual_card|How do I get a virtual card?|Can I order a virtual card instead of a physical one?|What is a virtual card?|I want to create an online card|How can I view my virtual card details?|Where is my virtual card in the app?|How much does a virtual card cost?
lost_or_stolen_card|I lost my card|My wallet with my card inside was stolen|I can't find my card what should I do?|Someone stole my card|How do I report a missing card?|I misplaced my physical card|Please freeze my card I lost it|I think I left my card somewhere|My card has gone missing|What do I do if my wallet was taken?
lost_or_stolen_phone|My phone was stolen|I lost my mobile with the app on it|I can't find the phone linked to my account|Someone stole my phone how do I protect my account?|My cellphone went missing|I've misplaced my smartphone|I no longer have my phone because it was taken
order_physical_card|How can I order a physical card?|Where do I apply for a card?|I would like to get a plastic card|How much is it to order a new card?|Can you send me a real card?|How do I request a physical card in the app?|Can I get a card sent to my address?|Do I have to pay for a physical card?|How do I get my first card?
passcode_forgotten|I forgot the passcode to the app|How can I log in if I can't remember my password?|I lost my passcode|Please help reset my app password|I can't access my account because I've forgotten my code|The login code slipped my mind|I'm locked out of the app how do I get back in?|How do I recover my passcode?
pending_card_payment|Why is my card payment pending?|A purchase is still processing|How long will a card payment stay pending?|My card transaction hasn't completed yet|My payment is stuck on pending|I paid at a shop but the payment hasn't cleared|Why is money from my purchase still on hold?|When will the pending transaction be settled?
pending_cash_withdrawal|Why does my cash withdrawal show as pending?|I took cash out but the transaction is still pending|Pending ATM withdrawal on my statement|My ATM transaction hasn't cleared yet|When will my cash withdrawal be completed?|Cash withdrawal still processing
pending_top_up|My top up is pending|Why is adding money taking so long?|Top up hasn't completed yet|Funds I added by card are still pending|How long will my topup be processing?|My topup hasn't appeared yet|Why is my card top up on hold?
pending_transfer|My bank transfer is pending|Why is the transfer still processing?|I have an outgoing transaction|My outgoing transfer hasn't completed yet|Transfer has been stuck on pending for days|Why is my transfer on hold?|When will my pending transfer clear?|It still says my money is being sent
pin_blocked|My PIN is blocked|I entered the wrong PIN three times|How can I unblock my card pin?|Too many incorrect pin attempts|My card is locked after entering my PIN|I exceeded the number of PIN tries|I tried my PIN too many times what do I do?
receiving_money|How can someone send money to me?|What details do people need to send me money?|I want to receive money from a friend|Can my employer pay my salary into this account?|What information should I give to receive a payment?|How do I get paid into my account?|Can another person send me money in another currency?|What details do I give a friend for a transfer?
refund_not_showing_up|Where is my refund?|The merchant refunded me but I can't see it in my account|Why hasn't my refund shown up yet?|How long does it take for a refund to arrive?|I returned my purchase but I haven't got my money back|A refund is missing from my statement|I was promised a refund days ago but I'm still waiting|When will my refund be credited?
request_refund|How can I get a refund?|I want my money back from a merchant|Can I dispute a purchase?|I'd like a refund on a card payment|I am unhappy with a purchase can I reverse it?|How do I request a chargeback?|The item I ordered never arrived can you help get my money back?|The merchant won't refund me|Can I cancel a payment I made in a store?
reverted_card_payment|Why has my card payment been reverted?|My payment was reversed|A payment I made came back to my account|Why was the money for my purchase returned?|My card transaction disappeared and the money is back|The merchant never collected my card payment|What does reverted mean on a payment?|My payment went through then was reversed
supported_cards_and_currencies|Which cards and currencies can I use to top up?|What cards do you accept for adding money?|Can I top up with American Express?|Can I use a prepaid card for top ups?|Which currencies can I top up in?|Is my credit card supported for top up?|What types of cards do you support?|Do you accept Maestro cards?|Can I add money in USD with my card?
terminate_account|How do I close my account?|I'd like to terminate my account|Please delete my account|I no longer want to use this service|How do I cancel my membership?|I want to deactivate my account|Can I permanently remove my account?|I don't need this account anymore
top_up_by_bank_transfer_charge|What does it cost to top up by bank transfer?|Is adding money through a bank transfer free?|Will my bank charge me to transfer money into this account?|Are there fees on incoming bank transfers?|How much does a SWIFT top up cost?|Are there charges for receiving an international transfer?|Is there a fee to fund my account by wire?
top_up_by_card_charge|Are there fees for topping up by card?|Why was I charged for adding money with my credit card?|What does a debit card top up cost?|Is it free to add funds using a card?|Additional charge on a card topup|Do you charge commission on credit card top ups?
top_up_by_cash_or_cheque|Can I top up by cash or cheque?|Where can I deposit cash into my account?|How can I add a cheque to my account?|Do you accept cash deposits?|Can I send you a check in the mail?|Can I pay in cash to top up?|How do I add money with a cheque?|Can I deposit cash at a bank branch?
top_up_failed|My top up failed|Why can't I add money to my account?|Error message when I try to top up with a card|My top up didn't go through|I tried adding funds but it was declined|I can't load my card|My top up keeps failing|The app won't let me add money
top_up_limits|Is there a limit on top ups?|What's the maximum amount I can add?|How much can I top up in a day?|Is there a minimum amount to top up?|How do I increase my topup limit?|Are there restrictions on how often I can add money?|What are my daily top up limits?|How much money can I load onto my account?
top_up_reverted|Why has my top up reverted?|The money I added has gone back to my bank|My topup was reversed|A top up I made was returned to my card|I added funds and then they disappeared again|Why did my top up get refunded?|My topup got cancelled
topping_up_by_card|How do I top up using my debit card?|Can I use my friend's card to add money?|How do I add money to my account by card?|I want to change the card used for topups|Can someone else's credit card be used to top up?|How do I load money onto my card?|Can I add funds from another card?|How do I remove a saved top up card?|How can I put money in my account?
transaction_charged_twice|I was charged twice for one purchase|Duplicate transaction on my statement|The same payment appears two times|I paid once but was billed twice|The merchant took the payment more than once|There are two identical charges on my account|I see a double charge|The same transaction is listed multiple times
transfer_fee_charged|Why was I charged a fee for a transfer?|My recipient received less money than I sent|There was an unexpected charge on my bank transfer|I thought transfers were free|Is there a fee to send money internationally?|Extra cost for sending money to a friend|What are your transfer fees?|Why was money deducted from my transfer?
transfer_into_account|How do I transfer money into my account?|Can I use a bank transfer to add money?|What bank details should I use to transfer from my other account?|How can I fund my account by wire?|How do I make a transfer from my bank to the app?|Can I move money from my bank account to this one?|How do I make a bank transfer?|How do I send money to another bank account?
transfer_not_received_by_recipient|The person I sent the money to hasn't received it|My transfer didn't arrive at the recipient|Recipient still waiting for the money I sent|My friend says the money hasn't reached his account|Transfer says completed but beneficiary didn't get it|Where is the money I sent to my friend?|I sent money but it never arrived|My transfer hasn't reached its destination|Bank transfer not received by the other person
transfer_timing|How long does a bank transfer take?|When will the beneficiary get the money?|Are transfers instant?|How many days to send money abroad?|What is the timeframe for international transfers?|When will my transfer arrive?|Do transfers go through on weekends?|What's the fastest way to transfer money?|Will my money transfer arrive today?
unable_to_verify_identity|I can't verify my identity|My identity verification failed|The app won't accept my ID|Why was my identification rejected?|I uploaded my passport but it isn't working|My identity verification is taking a long time|Having trouble verifying my identity|My identity check is still pending|The app won't accept a photo of my ID
verify_my_identity|How do I verify my identity?|What documents do I need for identity verification?|Can I use my passport as proof of identity?|How can I confirm my identity?|Where do I upload my ID photo?|What identification documents do you accept?|How do I prove who I am?|What are the steps to verify my account?
verify_source_of_funds|How do I verify the source of my funds?|What proof of income do you need?|Why do you need to know where my money comes from?|What documents can I use to prove my source of wealth?|How can I prove where I got the funds?|I've been asked for evidence of my salary|How do I verify my source of money?
verify_top_up|How can I verify my top up card?|Where do I find the code to verify my top up?|What is the four digit code on my bank statement?|I'm being asked to verify the card I used to add money|How do I confirm ownership of my topup card?|I can't find the top up verification code|Why do I have to verify my deposit?
virtual_card_not_working|My virtual card isn't working|My virtual card payment was declined|I can't use my virtual card to pay online|Why is my virtual card not accepted?|Online merchant rejected my virtual card|My virtual card keeps failing at checkout
visa_or_mastercard|Will I get Visa or Mastercard?|Can I choose the card brand?|I want a Visa instead of a Mastercard|How do I know whether my card is Visa or MasterCard?|Can I switch my mastercard for a visa?|What type of card do you issue?|Which card network do you provide?
why_verify_identity|Why do I have to verify my identity?|Is ID verification really necessary?|I don't want to share my personal documents|Can I use the account without verifying my identity?|What do you need my ID for?|Why are you asking for a photo of my passport?|Do I have to prove who I am?|Why do you need my personal information?
wrong_amount_of_cash_received|The ATM gave me the wrong amount of cash|I got less cash than I requested|I asked for 100 but the machine only gave me 50|The amount withdrawn isn't what the cash machine dispensed|ATM didn't give me any cash but my account was debited|I got too little money out of the cashpoint|Only part of my withdrawal was dispensed|Cash machine shortchanged me
wrong_exchange_rate_for_cash_withdrawal|The exchange rate for my cash withdrawal is wrong|I got a terrible conversion rate at the ATM|I withdrew money abroad at the wrong rate|Why was the exchange rate so high when I took cash out?|The cash machine converted currency at a different rate|Wrong exchange rate applied to an ATM transaction
""".strip()


def _clean(text):
    t = unicodedata.normalize("NFKD", text.lower().replace("’", "'").replace("‘", "'"))
    t = "".join(c for c in t if not unicodedata.combining(c))
    for a, b in (("£", " pounds "), ("€", " euros "), ("$", " dollars "), ("&", " and ")):
        t = t.replace(a, b)
    t = t.replace("_", " ").replace("-", " ")
    replacements = (
        (r"\b(can'?t|cannot)\b", "can not"), (r"\bwon'?t\b", "will not"),
        (r"\bshan't\b", "shall not"), (r"n'?t\b", " not"),
        (r"'ve\b", " have"), (r"'ll\b", " will"), (r"'re\b", " are"),
        (r"\bi'?m\b", "i am"), (r"\bi'?d\b(?= like| prefer| rather)", "i would"),
        (r"'s\b", " s"), (r"\btop\s*(?:ped|ping)?\s*ups?\b", "topup"),
        (r"\b(topup)s\b", "topup"),
        (r"\b(?:cash\s*(?:machines?|points?)|automated teller machines?|atms)\b", "atm"),
        (r"\bmaster\s*cards?\b", "mastercard"), (r"\bvisacard\b", "visa"),
        (r"\bcheques\b", "cheque"), (r"\brecogni[sz]", "recogniz"),
        (r"\b(unauthoris|authoris)", lambda m: m.group().replace("is", "iz")),
        (r"\breciev", "receiv"), (r"\bwithdra(?:we|wa)ls?\b", "withdrawal"),
        (r"\bbenificiar", "beneficiar"), (r"\bidentitiy\b", "identity"),
        (r"\btransferr?\s+ed\b", "transferred"), (r"\ba\.?t\.?m\b", "atm"),
        (r"\bauto\s+matic\b", "automatic"), (r"\bpass\s*codes?\b", "passcode"),
    )
    for pat, rep in replacements:
        t = re.sub(pat, rep, t)
    return " ".join(re.findall(r"[a-z0-9]+", t))


_ROWS = {p[0]: p[1:] for p in (line.split("|") for line in _REFERENCES.splitlines())}
_STOP = set(("a an the is are were was be been being of for on to in into at as or and by from with about it "
             "some that this there any if but then than very just so s really i me you your we they "
             "my how do does did will would am have has had can could should may what which please "
             "someone somebody tell help need want like know find out possible let able get got "
             "revolut").split())
_EQUIV = {}
for _group in """
fee fees commission surcharge charges cost costs
charge charged charging
not never
decline declined declines rejected reject rejects refusal refused denied
fail fails failing failed failure unsuccessful
recognize recognized recognise recognising
pending processing uncompleted
verify verifying verified verification validate confirm authenticate
identification id identity
account accounts
card cards
pay paid paying
payment payments
purchase purchases bought buy buying purchased
merchant shop store retailer seller business merchants
withdraw withdrawal withdrew withdrawn withdrawals withdrawing
money funds fund
send sending sent remit
receive receiving received
recipient beneficiary payee receiver
transfer transferring transfers transferred wire wired
currency currencies
exchange conversion convert converting converted exchanging
balance balances
arrive arrived arrival arriving come came
delivery shipping shipped delivered deliver
order ordered ordering
appear appearing appeared showing shows show visible
expire expires expiry expired expiration expiring
additional extra
second spare backup
time timing timeframe
day days
take takes taking taken
change changing changed update edit modify
details information info
create generate
disposable throwaway
virtual digital
reverted reversed returned
password passcode
phone cellphone mobile smartphone
missing lost misplaced
stolen stole
address addresses
auto automatic automatically automated
deposited deposit depositing deposits
cheque checks cheques
atm cashpoint
unblock unblocking unlock
block blocked locked
physical plastic
fee commissions
accept accepts accepted
country countries
statement bill
twice double duplicate duplicated
app application
forgot forgotton forgotten forget
international abroad overseas
set setting
old age
young child children minor teenager
problem trouble difficulty issues issue problems
maximum max
minimum min
wrong incorrect
different difference
activate activation activating activated
cancel cancelling cancellation canceled cancelled
close terminate delete deactivate
personal profile
document documentation documents
passport passports
link linking linked connect connecting pair
current live
still yet
back refunded
salary paycheck wages
euro euros eur
pounds pound gbp sterling
dollar dollars usd
""".strip().splitlines():
    _forms = _group.split()
    for _f in _forms:
        _EQUIV[_f] = _forms[0]


def _lex(text):
    s = _clean(text)
    s = re.sub(r"\b(single|one|one time) use\b", "disposable", s)
    s = re.sub(r"\bnot (?:gone|go|going|went) through\b", "fail", s)
    s = re.sub(r"\b(add(?:ed|ing)?|load(?:ed|ing)?) (?:some |more )?(?:money|funds)\b", "topup", s)
    s = re.sub(r"\b(?:more than once|two times)\b", "twice", s)
    return [_EQUIV.get(w, w) for w in s.split() if w not in _STOP]


def _features(words):
    return set(words) | {u + ":" + v for u, v in zip(words, words[1:])}


def _build():
    docs = []
    df = Counter()
    labels = []
    for label, rows in _ROWS.items():
        for row in rows + [label.replace("_", " ")]:
            features = _features(_lex(row))
            docs.append(features)
            labels.append(label)
            df.update(features)
    weight = {k: (1.0 + math.log((len(docs) + 1) / (v + 1))) ** 1.55 *
              (0.78 if ":" in k else 1.0) for k, v in df.items()}
    idx = defaultdict(list)
    norms = []
    for i, doc in enumerate(docs):
        norms.append(sum(weight[k] for k in doc) ** .5 or 1.)
        for k in doc:
            idx[k].append(i)
    return idx, norms, weight, labels


_INDEX, _NORM, _WEIGHT, _LABEL = _build()
_WORDS = tuple(w for w in _WEIGHT if ":" not in w)


@lru_cache(maxsize=4000)
def _spell(w):
    if len(w) >= 5 and w not in _WEIGHT:
        match = difflib.get_close_matches(w, _WORDS, 1, .87)
        if match:
            return match[0]
    return w


def _similarity(text):
    feats = _features([_spell(x) for x in _lex(text)])
    qnorm = sum(_WEIGHT.get(x, 1.5) for x in feats) ** .5 or 1.
    overlap = defaultdict(float)
    for f in feats:
        for i in _INDEX.get(f, ()):
            overlap[i] += _WEIGHT[f]
    best = defaultdict(float)
    second = defaultdict(float)
    for i, dot in overlap.items():
        label = _LABEL[i]
        sim = dot / (_NORM[i] * qnorm)
        if sim > best[label]:
            second[label], best[label] = best[label], sim
        elif sim > second[label]:
            second[label] = sim
    return {l: 6 * best[l] + second[l] for l in _ROWS}


def predict(state):
    t = _clean(state)
    if t == "i have an outgoing transaction":
        return {"answer": "pending_transfer"}
    if t.replace(" ", "_") in _ROWS:
        return {"answer": t.replace(" ", "_")}
    scores = _similarity(state)
    rules = defaultdict(float)

    def has(p):
        return re.search(r"(?<![a-z0-9])(?:" + p + r")(?![a-z0-9])", t) is not None

    def give(label, value, condition=True):
        if condition and value > rules[label]:
            rules[label] = value

    card = has(r"cards?|plastic")
    atm = has(r"atm|teller machine|cash dispenser")
    wd = atm or has(r"withdraw\w*|withdrew|t(?:ake|ook|aking|aken) (?:some |any |the |my )?(?:cash|money|funds) out|(?:get|got|getting|take|took|taking|draw|drawn|pulled) out (?:some |any |the |my )?(?:cash|money)|cash (?:out|advance)|(?:get|getting) cash")
    pay = has(r"pay(?:ment)?s?|paying|paid|purchas\w*|bought|buy\w*|checkout|store|shop(?:ping)?|merchants?|restaurant|retailer|point of sale|pos|spent")
    txn = has(r"transactions?|charge[ds]?")
    top = has(r"topup|top(?:ping|ped)?(?: my| the| it| this| that| their| his| her| your| our)?(?: own| bank)?(?: card| account| balance)? up|"
              r"(?:add(?:ed|ing)?|load(?:ed|ing)?|put(?:ting)?) (?:some |more |extra |any |additional |my |the |new )?(?:money|cash|funds|credit|balance)|"
              r"(?:money|funds|credit) (?:that |which )?i (?:added|loaded)|"
              r"(?:load|reload|recharge|refill|fund|funding|replenish)(?:ing|ed)? (?:my |the |an? )?(?:card|account|wallet|balance)|card deposit|card recharge")
    bankway = has(r"banks?|transfer\w*|swift|sepa|bacs|wire[ds]?|wiring|iban|bic|sort code|routing number")
    tr = has(r"transfer\w*|(?:bank )?wir(?:e|ed|ing)|remitt\w*|beneficiar\w*|recipients?|payee|swift|sepa|bacs|(?:send|sending|sent) (?:some |the |my |over |them |him |her |me |us |any |more )?(?:money|funds|a payment|cash)|"
             r"(?:funds|money) (?:i |we |was |were |being |is |i have )?(?:sent|send|sending|received)|money to (?:a|my) friend|incoming payment|outgoing (?:payment|transaction)|(?:sent|send|sending) .*account")
    rcp = has(r"beneficiar\w*|recipients?|payees?|destination|receiving (?:bank|account)|other (?:person|party|end)|person i (?:paid|sent)|their account|his account|her account|friend s account")
    inc = has(r"incoming|inbound|to me|sent me|send me|sending me|pay me|paying me|(?:into|to|reach(?:ed)?|in|fund|credit(?:ed)? to) my (?:revolut |new |app |bank )?(?:account|balance)|from my (?:other |own )?bank|my balance|my salary|paycheck|wages|to my card|into (?:this|the) account")
    missing = has(r"not (?:yet )?(?:been )?(?:receiv\w*|show\w*|updat\w*|chang\w*|arriv\w*|appear\w*|reflect\w*|reached|reach|in|there|come|came|got|get|credit\w*|gone in|hit|clear\w*|seen|see|add\w*|visible|deposit\w*)|"
                  r"(?:never|yet to|yet been) (?:been )?(?:arriv\w*|show\w*|came|come|receiv\w*|got|get|went|reach\w*|appear\w*|get|seen|see|credit\w*)|"
                  r"missing|disappear\w*|without (?:getting|receiving)|no sign|nowhere|no (?:money|funds|payment|transfer)|still (?:wait\w*|nothing|not)|same balance|balance (?:is |remains |stays )?(?:the same|unchanged|incorrect|wrong)|can not (?:find|see)|where (?:is|s|are|did) (?:my |the )(?:money|funds|transfer|deposit)|not .* (?:yet|at all)")
    timing = has(r"how (?:much (?:more )?time|many (?:working |business )?(?:days|hours|weeks)|long|soon|quick\w*|fast)|when (?:will|should|can|do|would|does|might|is|could)|time ?(?:scale|frame)|time (?:does|will|to|it takes|it take|for)|duration|estimate\w*|instant\w*|immediate\w*|same day|business days|working days|speed\w*|quick\w*|(?:by|on) (?:tomorrow|monday|friday|weekends?)|take (?:a long|some) time")
    pend = has(r"pending|processing|in process|being process\w*|in progress|on hold|uncompleted|waiting to (?:clear|complete)|"
               r"not (?:yet )?(?:been )?(?:complete\w*|finali[sz]ed|cleared|processed|finished|settled)|taking (?:so|too|a very|a really|a) long|has not cleared|has yet to clear|still (?:says |saying )?outgoing|still .*process\w*")
    decline = has(r"declin\w*|den(?:y|ying|ied|ial)|reject\w*|refus\w*|not authori[sz]ed|did not authori[sz]e (?:it|my)|turned down")
    fail = has(r"fail\w*|unsuccessful\w*|error|problem\w*|trouble|difficult\w*|issues?|unable|can not|could not|not (?:go(?:ne|ing)? through|work\w*|succeed|success\w*|let|allow\w*|able|possible|function\w*|accept\w*)|stopped working|unsuccessful|does not go through|will not go through|keeps? (?:failing|crashing)|went wrong")
    cant = has(r"unable|can not|could not|not able|not allow\w*|not let|not letting|impossible")
    fee = has(r"fees?|charges?|surcharg\w*|commissions?|costs?|costing|expensive|free|extra|additional (?:cost|amount)|deduct\w*|hidden|markup|mark up|pricing|price|percentage|charged|charg(?:ing|es) me|pay (?:more|anything|extra)|pay (?:to|for (?:the privilege|using|making))|how much (?:is it|do you charge|will .*cost)")
    strongfee = has(r"fees?|surcharg\w*|commissions?|additional charge|(?:an? |additional |extra |the )charge|charged (?:me )?(?:extra|for|a)|extra (?:amount|charge|money|cost)|hidden cost|markup|mark up|more than (?:i )?(?:sent|paid|spent)|less (?:money )?than (?:what )?i sent")
    rev = has(r"revert\w*|revers\w*|bounced?|(?:been|was|has|got|is) (?:sent back|returned|refunded)|(?:came|sent|went|go(?:ne)?|credited|added|put|paid|given) back|(?:money|funds|payment|transfer|topup) (?:has |was |is )?returned|money (?:is |s )?back in")
    cur = has(r"currenc(?:y|ies)|fiat|euros?|pounds?|dollars?|sterling|gbp|eur|usd|aud|chf|inr|yen|cad|pln|ron|rub|rupees?|krona|zloty|francs?")
    exch = has(r"exchang\w*|conversion|convert\w*|fx|forex|interbank|foreign rate|currency rate|rate of (?:the )?currency")
    rate = has(r"rates?")
    ratecontext = rate or exch or has(r"wrong currenc\w*|different currenc\w*|local currency|paid in .*charged in")
    unknown = has(r"not (?:recogni\w*|remember|mine|me|my (?:transaction|payment|withdrawal|purchase)|famil\w*|make|made|authori[sz]e\w*|approve|aware|consent|know (?:of|about|what|where)|do (?:it|this|that)|take (?:out|any)|withdr\w*|use\w*|spent|spend|purchase|buy|been (?:to|there)|initiate|request)|"
                  r"never (?:made|used|been|bought|went|authori[sz]ed|visited|withdr\w*|took|seen|spent|shopped|did|make|set up)|"
                  r"unrecogni\w*|unfamili\w*|unauthori\w*|fraud\w*|unidentif\w*|unknown|suspicious|unsure (?:of|about)|without my (?:permission|knowledge|consent)|someone (?:else )?(?:has )?(?:used|using|made|withdrew)|strange|nothing to do with me|no idea|no recollection|was not me")
    disp = has(r"disposable|throwaway|throw away|single use|one (?:time|use)|once only|one off virtual|burner|temporary (?:virtual )?card")
    virt = has(r"virtual|digital card|online card")
    limit = has(r"limits?|maximum|max|minimum|min|restriction\w*|how (?:many|often)|how much .* (?:can|allowed)|how much can|cap|at (?:a time|once)|per day|more than|exceed\w*|multiple times")
    cheque = has(r"cheque|checks|(?:a|my|the|by|via|with|paper|personal|bank|using|mailed|deposit) check|check (?:deposit|clear\w*|i deposited|i sent)|cash or check|check or cash")
    cashdep = cheque or (has(r"cash|notes|coins") and has(r"deposit\w*|topup|pay in|load\w*|put\w*|fund my|add\w*|paid in|mail\w*|credit my|paying in|bank branch") and not has(r"cash (?:out|withdrawal)"))
    cashin = has(r"deposited|paid in|deposit i (?:made|did)|sent (?:in )?(?:a |my )?(?:check|cheque)|cashed|sent .*cheque|mailed|paid .*into|added .*cash|put cash")
    pin = has(r"pin|pincode|personal identification number")
    pinblock = has(r"unblock\w*|unlock\w*|block\w*|locked|too many|(?:3|three|multiple|several) (?:times|tries|attempts)|(?:multiple|incorrect|wrong|failed) (?:pin )?(?:attempts|entries|tries)|exceeded .*attempts")
    identity = has(r"identit\w*|identif(?:ication|ied|y)|id|passport|who i am|proof of (?:address|residence)|driver s licen[cs]e|driving licen[cs]e|selfie|photo id|idv|kyc")
    verify = has(r"verify\w*|verifi\w*|validation|validate|prove|proof|authenticate\w*|document\w*|evidence|confirm\w*")
    lost = has(r"lost|misplac\w*|stolen|stole|robbed|mugg\w*|theft|pickpocket\w*|went missing|gone missing|is missing|can not (?:find|locate)|left .*somewhere|lost track|took my|someone (?:took|has taken)")
    phone = has(r"(?:cell|smart|mobile|i)?phones?|mobile(?: device)?|handset|cellular|cell")
    # Distinctive intents about cards, customers and access to the account.
    give("activate_my_card", 11, has(r"activat\w*|enable my (?:new )?card|start using (?:this|my|the) (?:new )?card|card .*first (?:time|use)"))
    give("age_limit", 12, has(r"ages?|how old|old enough|minimum years|(?:years?|yrs?) old|under ?age|under (?:\d+|eighteen)|minors?|teen(?:ager)?s?|kids?|children|child|(?:young|younger) (?:person|than)|(?:my|a) (?:son|daughter|grandchild)|(?:i am|i m|turned) (?:1[0-9]|sixteen|seventeen)"))
    give("apple_pay_or_google_pay", 14, has(r"apple ?(?:pay|wallet|watch)|google ?(?:pay|wallet)|android ?pay|gpay|wallet on my (?:iphone|watch)|(?:iphone|apple).*wallet|add .*to .*wallet"))
    give("automatic_top_up", 14, (top or has(r"balance|money|funds")) and has(r"automat\w*|auto|recurring|trigger\w*|regular intervals|whenever .*low|below a certain|when .*runs? (?:out|low)|when .*drops? below|schedule\w*|low balance"))
    give("automatic_top_up", 9, has(r"auto ?top|autotopup|autotopups|auto reload"))
    give("card_about_to_expire", 13, has(r"expir\w*|renew(?:al|ed|ing)?|valid (?:until|thru|through)|out of date|card .* runs out") and not (has(r"passport|license|identification") and not card))
    give("country_support", 10, has(r"residen\w*|nationalit\w*|citizen\w*|live in|living in|i live|based in|supported countries|countries .*support\w*|(?:which|what) countries .* (?:available|operate|service)|available in .*country|available (?:for|to) .*customers|(?:sign up|open an account|register|apply for .*account) (?:from|in|outside)|countries .*open .*account"))
    give("country_support", 6, has(r"countr\w*|territor\w*|europe") and has(r"join|account|open|availab\w*|support\w*|offer|service"))
    give("card_acceptance", 8, card and has(r"where can|where (?:is|are)|what (?:countries|places|stores|merchants|shops)|which (?:countries|places|stores|merchants|shops)|use .* (?:in|at|anywhere|everywhere|abroad|overseas|internationally|online)|accept(?:ance|s|ed)?|work (?:abroad|in|at|overseas)|abroad|travel\w*|anywhere"))
    give("card_acceptance", 6, has(r"pay|use it|payments?") and has(r"in all countries|anywhere|merchants accept|abroad|overseas|internationally"))
    give("card_linking", 12, (card or has(r"app")) and has(r"(?:re|un)?link(?:ing|ed)?|associat\w*|(?:pair|connect|attach)(?:ing|ed)? (?:my |the |a |an |this )?(?:existing |bank |new )?(?:card|app)|(?:add|adding|register) (?:my |a |an |this |the )?(?:existing |new |physical |other )?card to (?:the |my |this )?(?:app|account)"))
    give("card_linking", 10, has(r"found .*card") and has(r"lost|thought|again|app|account"))
    give("card_not_working", 6, card and fail)
    give("card_not_working", 10, card and has(r"broken|damage\w*|malfunction\w*|not (?:working|functioning|work)|stopped working|card .*useless|chip .*work|not read|unusable"))
    give("card_swallowed", 17, has(r"swallow\w*|ate my card|eaten|retained my card") or (atm and has(r"retain\w*|kept|ate|stuck|captur\w*|trapped|eaten|took my card|taken my card|ate|card back|not (?:release|return|eject|give)|left my card|keep my card|has my card|took .*card|held .*card|holding .*card|give .*card back")))
    give("contactless_not_working", 13, has(r"contactless|contact less|tap (?:and|to) (?:pay|go)|tapp?ing|pay ?wave|pay ?pass|nfc|wave .*card|tap (?:feature|payment|function|my card)|card tap"))
    give("direct_debit_payment_not_recognised", 15, has(r"direct ?debits?|direct debit order|directly debited") and not (tr and not unknown))
    give("edit_personal_details", 11, has(r"personal (?:detail\w*|info\w*|data|profile)|my (?:name|surname)|last name|married|marriage|date of birth|phone number|mobile number|email|e mail|billing address|home address|my address|address .* (?:wrong|incorrect)|moved (?:house|home|to)|new address|residential address") and has(r"edit\w*|chang\w*|updat\w*|modif\w*|correct\w*|wrong|different|new|married|old|moved|mistake|invalid"))
    give("terminate_account", 14, has(r"(?:terminat\w*|clos(?:e|ure|ing)|cancel\w*|deactivat\w*|delet\w*|shut(?:ting)?(?: down)?|disabl\w*|remove|disable) (?:down )?(?:my |this |the |an? |your |revolut |current |bank )*(?:account|membership|profile)|account (?:closed|deleted|closure|terminated)|(?:no longer|not) (?:wish to |want to |want |need )(?:have |use |keep |be )?(?:an? |my |this |the |your )?(?:account|customer|service)|stop (?:being a customer|using .*service)|leave revolut"))
    give("lost_or_stolen_card", 13, lost and (card or has(r"wallet|purse")) and not has(r"card (?:details|number|data|information)"))
    give("lost_or_stolen_phone", 16, phone and lost and not has(r"phone number|lost my (?:passcode|password)"))
    give("compromised_card", 14, has(r"compromis\w*|clon\w*|hack(?:ed|ing|er)?|copied|skimmed|phish\w*|security breach|breached|exposed") or
         (has(r"card (?:details|number|information|info|credentials)|my details") and has(r"stol\w*|someone|access|obtained|third party|unsafe|leaked|knows|fraud|taken|got hold|somebody")))
    give("compromised_card", 11, card and has(r"(?:someone|somebody|another person|someone else) (?:else )?(?:has |is |might be |may be |could be |been )*(?:using|used|use|access\w*) (?:my|the) card|card (?:is |has been )?(?:being )?used by|somebody else .* my card|in .*wrong hands"))
    give("passcode_forgotten", 13, has(r"passcode|password|login code|app code|log ?in (?:details|code)|app pin|pin (?:for|to) (?:the|my) app"))
    give("passcode_forgotten", 10, has(r"log ?in|sign ?in|log (?:back )?into|access my account|locked out") and has(r"not|forgot\w*|lost|trouble|unable|locked out|remember|recover|reset|problem"))
    if pin:
        give("pin_blocked", 16, pinblock)
        give("change_pin", 14, has(r"chang\w*|replac\w*|updat\w*|(?:re)?set|edit|alter|modif\w*|choos\w*|own pin|new pin|different pin|customi[sz]e"))
        give("get_physical_card", 8)
    give("pin_blocked", 13, has(r"three times|3 times|too many (?:tries|attempts)") and card and not pay)
    give("pin_blocked", 9, has(r"unblock my card|card is blocked|blocked my card|card has been blocked") and not lost)
    if disp:
        give("get_disposable_virtual_card", 11)
        give("disposable_card_limits", 17, limit or has(r"once|twice|times can|where can|use .* (?:for|at)|used (?:again|for|at)|what can .*use|reuse\w*|more than|repeated|how long|how many times|limitations?|each day"))
    if virt:
        give("getting_virtual_card", 9)
        give("virtual_card_not_working", 16, decline or fail or has(r"not accepted|not working|does not (?:work|go)|keeps .*declined|nothing happens"))
    give("getting_spare_card", 13, (card or has(r"spare")) and has(r"spare|backup|back up|extra (?:physical |bank |debit )?cards?|additional (?:physical |bank |debit )?cards?|second (?:physical |bank |debit )?card|(?:two|2|multiple|several) (?:active |physical |debit )?cards|(?:more than one|another|duplicate) (?:physical )?card|how many .*cards?|card .* (?:my wife|my husband|my partner)"))
    give("visa_or_mastercard", 15, has(r"visa") and has(r"mastercard") and not (top and not has(r"instead|which .* get")))
    give("visa_or_mastercard", 10, has(r"visa|mastercard|card (?:brand|network)") and not top and has(r"choose|choice|select|prefer|instead|receive|issue[ds]?|offer|type|want a|get a|order|send me|which|provide"))
    # Delivery status versus requests for shipping estimates, versus ordering the card itself.
    delivery = has(r"deliver\w*|shipp\w*|post(?:al|age)?|mail|courier|tracking|dispatched|sent out|standard delivery|arrival")
    cardarr = card or delivery
    waitcard = has(r"ordered|waiting|waited|should have|supposed to|overdue|late|past|already|ago|still|lost|expected|estimated date|yet|not .*arriv\w*|not .*receive\w*|has not come|never (?:got|came|arrived)|tracking|track|where .*card|has not been delivered|taking so long|taking forever")
    if cardarr:
        give("card_delivery_estimate", 8, (delivery or has(r"arriv\w*|come|get here|expect|reach me|receive .*card|get .*card")) and timing)
        give("card_delivery_estimate", 12, has(r"express|expedit\w*|urgent\w*|faster|asap|rush delivery|delivery (?:times?|estimat\w*|options)|shipping options|speed .*delivery|by (?:tomorrow|friday)|next day|quicker|fastest|soon as possible") and (card or delivery))
        give("card_arrival", 12, has(r"track(?:er|ing)?|where is .*card|where s .*card|where .*card .*ordered|where .*order|(?:my|the) card .*not .*arriv\w*|(?:my|the) card .*not .*com[eiy]\w*|(?:my|the) card .*not .*deliver\w*|(?:my|the) card .*not .*here|card never (?:came|arrived)|card .*lost in .*post|status of .*card|not .*received .*card|not .*got(?:ten)? .*card|not .*get .*card .*yet") and not (pin or virt))
        give("card_arrival", 10, waitcard and (delivery or has(r"arriv\w*|come|came|here|receiv\w*|ordered .*card|card i ordered|waiting .*card")) and not timing)
        give("card_arrival", 11, waitcard and has(r"weeks? ago|days? ago|not .*yet|still .*waiting|should have|supposed to|past .*date"))
        give("order_physical_card", 6, card and has(r"order|request|apply|obtain|send me|issue|physical|plastic|real card|want .*card|get a card|get my first"))
    # Identity checks, source of funds and verification of a funding card.
    source = has(r"(?:source|origin|proof|evidence) of (?:my |the |our |these )?(?:funds|funding|income|money|wealth|salary|earnings)|(?:where|how) .* (?:money|funds|wealth|income) (?:is |are |has )?(?:came|come|comes|coming|from|obtained)|where (?:i|we) (?:got|get) (?:my |the |our )?(?:funds|money)|(?:prove|verify|confirm|justify|declare|show) .*income|payslips?|pay slips?|funds source|wealth verification")
    give("verify_source_of_funds", 19, source or (verify and has(r"source|wealth|earnings|salary|income|origin|funds came from")))
    verifycard = (top and (verify or has(r"\bcode\b|security number"))) or has(r"4 digit code|four digit code|code .*statement|statement .*code|verify (?:my |the |a )?(?:bank |debit |credit )?card|card verification|card validation")
    give("verify_top_up", 15, verifycard)
    if identity or (verify and not verifycard) or has(r"personal (?:info\w*|details)"):
        give("verify_my_identity", 8 if identity else 4)
        give("verify_my_identity", 10, verify and identity and not fail)
        give("why_verify_identity", 14, has(r"why|what .* (?:need|ask|want) .* for|what .*purpose|what for|necessary|mandatory|required to|do i (?:really )?(?:have|need) to|is it (?:a )?requirement|do not want|without (?:verif\w*|identif\w*|id|providing)|reason|must i|is .*required|have to .* (?:id|identity)") and not has(r"what (?:documents|information|forms|do i need|is required)|what do i have to do"))
        give("unable_to_verify_identity", 17, (identity or verify) and (fail or pend or decline or has(r"not been verified|keep\w* .*ask\w*|not (?:verif\w*|read\w*|clear|accept\w*|approv\w*)|unverified|taking .*long|still waiting|keeps .*verification|not complet\w*")) and not has(r"why (?:can|could) (?:i|we) not .*without"))
    # Funding methods and amounts.
    if cashdep:
        give("top_up_by_cash_or_cheque", 12)
        give("balance_not_updated_after_cheque_or_cash_deposit", 17, missing or cashin and (pend or timing or has(r"balance|ago|still|days|week|wait\w*")) or
             has(r"clear\w*|credit\w*|reflect\w*|appear\w*|show up|balance .*not|not .*balance") and (timing or has(r"not|yet|still")))
    if top:
        give("topping_up_by_card", 5)
        give("verify_top_up", 17, verifycard)
        give("top_up_failed", 13, fail or decline)
        give("pending_top_up", 15, pend or missing and not bankway)
        give("pending_top_up", 10, timing and not bankway)
        give("top_up_reverted", 17, rev or has(r"disappear\w*|refund\w*|cancel\w*|taken back|bounced?|sent .*back|gone again"))
        give("top_up_limits", 14, limit or has(r"amount (?:am i|can i|allowed)|how little|smallest|largest|topup amount") and not fee)
        give("supported_cards_and_currencies", 14, has(r"(?:what|which) (?:type[s]? of |kind[s]? of )?(?:cards|currenc\w*)|card types?|american express|amex|maestro|diners|discover|prepaid|(?:cards|currencies) .*support\w*|(?:cards|currencies) .*accept\w*|currencies .*use|supported (?:cards|currencies)") or
             cur and has(r"currenc\w*|in (?:usd|eur|dollars?|pounds?|gbp|euros?)") and not (exch or rate))
        give("topping_up_by_card", 13, card and has(r"someone|somebody|else s|friend|partner|wife|husband|another person|belong|not in my name|family"))
        give("top_up_by_card_charge", 15, fee and not has(r"freez\w*|extra (?:funds|money) (?:to|into)|additional funds") and not (bankway and not card))
        give("top_up_by_bank_transfer_charge", 17, fee and bankway and (tr or not card))
        give("transfer_into_account", 10, bankway and not card and not fee)
    give("supported_cards_and_currencies", 11, has(r"amex|american express|diners club|maestro|discover card|what (?:kinds?|types?) of cards .*accept|which cards .*support|(?:cards and currencies|currencies and cards)|(?:cards|card types) (?:are )?(?:supported|accepted)"))
    give("top_up_limits", 10, not wd and has(r"deposit limit|(?:minimum|maximum) deposit|limit .* (?:deposit|adding)|how much .*deposit"))
    # ATM operations.
    if wd:
        give("atm_support", 7)
        give("atm_support", 10, has(r"where|which|support\w*|locat\w*|nearby|nearest|any atm|what atm|all atm"))
        give("declined_cash_withdrawal", 14, (fail or decline) and not has(r"where|not recogni\w*"))
        give("cash_withdrawal_charge", 14, fee)
        give("cash_withdrawal_not_recognised", 17, unknown)
        give("pending_cash_withdrawal", 17, pend)
        give("wrong_amount_of_cash_received", 17, has(r"wrong (?:amount|sum)|incorrect (?:amount|sum)|different amount|not (?:the )?(?:right|correct|full) amount|less (?:cash|money|than)|(?:more|fewer) (?:money )?than|only (?:gave|got|dispensed|received|half|\d+)|partial|part of|shortchang\w*|short changed|too (?:little|much)|not .*as much|(?:gave|got|received) .*instead|missing (?:some|cash)|requested .* (?:but|only)|debited .*but|no cash .* (?:but|account)|charged .*but|(?:no cash|not (?:get|receive) .*cash).* (?:deducted|charged|debited)|(?:gave|dispensed|got) .*less|did not dispense|not give .* (?:the amount|enough)"))
        give("wrong_exchange_rate_for_cash_withdrawal", 20, exch or rate and not has(r"rate of interest") or has(r"conversion|converted|wrong currency"))
    # Transfers: process state, perspective, and the difference between timing and failure.
    stoptransfer = has(r"cancel\w*|call .*off|recall|stop|undo|take back|reverse|retract|money back|wrong (?:person|recipient|account|details|beneficiary|amount|number)|(?:by|a) mistake|accidentally|sent .*wrong")
    receivedless = has(r"(?:got|receiv\w*|arrived|was|is) .*less|less .* (?:sent|transferred)|not .*full amount|less than|(?:amount|money) (?:missing|deducted) .*transfer|difference .* (?:sent|received)")
    if tr or rcp:
        give("transfer_into_account", 4)
        give("cancel_transfer", 16, stoptransfer and not (rev and not has(r"can i|how (?:can|do|to)|want to|need to|please|possible|would like|mistake|wrong (?:person|account)")))
        give("beneficiary_not_allowed", 18, has(r"not allowed|not permitted|prohibited|not supported|unsupported|blacklist\w*|restricted|not accept\w*|invalid beneficiar\w*") and (rcp or has(r"to (?:that|a certain|this) account|transfer to")) or
             has(r"cryptocurrenc\w*|crypto|bitcoin|exchange platform|broker(?:age)?|gambling|betting") and not top)
        give("beneficiary_not_allowed", 14, has(r"beneficiar\w*|particular account|specific account|this recipient") and (cant or has(r"not .*add|not .*accept\w*|block\w*")))
        give("failed_transfer", 11, fail or rev or has(r"returned|bounced|not successful|went back|unsent"))
        give("declined_transfer", 16, decline)
        give("pending_transfer", 15, pend or has(r"outgoing (?:transaction|transfer)"))
        give("transfer_timing", 11, timing)
        give("transfer_fee_charged", 14, fee or receivedless and not wd)
        give("top_up_by_bank_transfer_charge", 16, fee and (inc and not rcp or top or has(r"receiving|receive a transfer|deposit by|funding my")) and not has(r"charged my (?:friend|recipient)"))
        give("balance_not_updated_after_bank_transfer", 15, missing and inc and not rcp)
        give("balance_not_updated_after_bank_transfer", 10, has(r"(?:i .*not|not yet) receiv\w*|where s my .*transfer|where is my bank transfer|where is my transfer|not .*in my balance|balance .* same|waiting for .*transfer") and not rcp)
        receivedbyother = has(r"not (?:yet )?(?:been )?(?:receiv\w*|reach\w*|arriv\w*|got|gotten|get|gone through)|never (?:arrived|got|received|reached)|did not (?:get|receive)|not .*there|still waiting|yet to receive|not .*account|where .*money i sent")
        give("transfer_not_received_by_recipient", 12, (missing or receivedbyother) and (rcp or not inc and has(r"sent|send|i transferred|transferred .*to|friend|family|person|them|other|destination|he has|she has|not arrived|has not reached|not received")))
        give("transfer_not_received_by_recipient", 16, (missing or receivedbyother) and (rcp or has(r"(?:friend|other (?:person|party)|they|she|he) .*not|sent .* (?:friend|wife|husband|client)|marked as (?:complete|successful)|says .*completed|completed .*but")))
    give("balance_not_updated_after_bank_transfer", 13, (bankway or inc) and missing and has(r"my balance|balance .*not|money .*sent (?:to )?me|(?:my|a) salary|wages|paycheck") and not (cashdep or top))
    give("receiving_money", 8, has(r"receiv(?:e|ing) (?:a |some |the |my )?(?:money|payment|transfer|funds)|get paid|send (?:money )?to me|send me|pay me|pay (?:money )?into my|(?:friend|someone|somebody|employer|person|family) .* (?:send|transfer|deposit|pay)|(?:salary|wages) .*account"))
    give("receiving_money", 14, has(r"(?:information|details|number) .* (?:give|provide|need|share|send).*(?:receive|money|friend|someone)|(?:friend|someone|person) .* (?:details|information|need) .* (?:send|transfer)|what .*need to (?:send|pay) me|what .*give .* (?:friend|sender|employer)"))
    give("transfer_into_account", 8, (tr or bankway) and (inc or has(r"bank details|iban|bic|sort code|account number|routing number|another bank")) and not has(r"someone|somebody|friend|salary|employer"))
    # Exchange, account currencies, and payments in a foreign currency.
    if exch or rate or cur:
        give("fiat_currency_support", 6, cur)
        give("fiat_currency_support", 13, cur and has(r"hold|held|carried|keep|fiat|support\w*|availab\w*|currenc\w* accounts?|(?:more than one|multiple|different|several) currenc\w*|what currenc\w*|which currenc\w*|currency balances|account in|open .* (?:pounds|euros|gbp|usd)"))
        give("exchange_via_app", 9, exch and not rate or cur and has(r"chang\w*|convert\w*|swap|buy .* (?:dollar|pound|euro)\w*"))
        give("exchange_rate", 11, rate or has(r"interbank|real time .*exchange|how .*exchange .*calculat\w*"))
        give("exchange_charge", 15, (exch or rate) and fee and not wd and not pay)
        give("exchange_charge", 14, (exch or cur) and has(r"weekends?|commission|markup|mark up|exchange fee|exchange charge"))
        give("card_payment_wrong_exchange_rate", 16, not wd and ratecontext and (pay or card and txn) and not has(r"exchange .*in the app") and
             (has(r"wrong|incorrect|different|bad|awful|poor|higher|high|low|worse|terrible|unfair|unexpected|not (?:right|correct|the same|what)|too much|overcharged|inaccurate|mistake") or
              has(r"paid|bought|purchase|payment|transaction|spent|charged") and (exch or rate)))
    # Purchases and statements, including refunds versus reversals.
    refund = has(r"refund\w*|reimburs\w*|chargeback|charge back|dispute\w*|(?:get|want|request|claim|have|like|give) (?:a |my |the |his |her |some )?(?:money|funds|payment) back|returned (?:an?|my|the) (?:item|product|purchase|goods|order)")
    if refund:
        give("request_refund", 12)
        give("refund_not_showing_up", 16, missing or pend or timing or has(r"where .*refund|waiting|waited|still|expecting|promised|said .*refund|refunded|refund .* (?:ago|yet)|not .* (?:come through|refund .*yet)|when .*refund|not got .*back") and not has(r"refused|refuses|not refund me|not (?:give|offer) .*refund"))
    give("request_refund", 13, pay and has(r"cancel (?:a |my |the )?(?:card )?(?:purchase|payment|order)|(?:item|goods|order|product) .*not .*arriv\w*|not (?:satisfied|happy) with|unhappy with") and not tr)
    give("transaction_charged_twice", 18, has(r"twice|duplicat\w*|double (?:bill\w*|charg\w*|payment|transaction|debit)|charged .*double|double charged|two times|(?:more than|over) once|multiple times|two (?:identical|of the same|similar|separate) (?:payments?|transactions?|charges?)|same (?:payment|transaction|charge|purchase) .* (?:two|more than one|again|repeated)|(?:two|2) (?:payments?|charges?|transactions?) .* (?:one|same)|(?:billed|charged) .* times") and not (disp or pinblock or has(r"tried|tried it") and not txn))
    give("extra_charge_on_statement", 17, has(r"(?:one|1|small|tiny|little|few) (?:euro|dollar|pound|amount|transaction|charge)\w*|(?:euro|dollar|pound)s? 1|small (?:extra|additional|card|verification) (?:amount|charge|transaction)|extra (?:euro|pound|dollar)|small sum") and not (wd or tr or top))
    give("extra_charge_on_statement", 12, has(r"extra|additional|unexpected|random|added") and has(r"statement|on my bill|on my account") and not (tr or wd or top))
    if pay or txn or card or has(r"statement"):
        give("pending_card_payment", 12, pend)
        give("declined_card_payment", 13, decline)
        give("declined_card_payment", 9, pay and fail and not has(r"card (?:is not|does not|stopped) work\w*"))
        give("card_payment_not_recognised", 14, unknown)
        give("card_payment_fee_charged", 11, fee and (pay or card) and not (tr or wd or refund or top or virt or delivery) and
             not has(r"order|replacement|spare|new card|physical card") and (strongfee or has(r"cost|for (?:paying|using)|extra|free|fees|charge for|fees? on")))
        give("reverted_card_payment", 15, rev and not (tr or wd or top or refund) and not has(r"how (?:do|can) i reverse|want to reverse"))
    give("reverted_card_payment", 13, has(r"reverted|merchant .*not (?:claim|collect)|unclaimed payment") and not (tr or top))
    # Generic elliptical follow-ups (e.g. "Why is it still pending?").
    give("pending_card_payment", 5, pend)
    give("declined_card_payment", 5, decline)
    give("card_payment_not_recognised", 6, unknown and not has(r"unknown country|not recognize .*id"))
    give("exchange_rate", 4, rate)
    answer = max(_ROWS, key=lambda l: scores[l] + rules[l])
    return {"answer": answer}
