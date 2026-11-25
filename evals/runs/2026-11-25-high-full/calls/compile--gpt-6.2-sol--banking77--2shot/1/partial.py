import math
import re
import unicodedata
from collections import Counter
from functools import lru_cache


_PHRASES = """
activate_my_card:activate my new card|how do i enable the card i just received|where is the activation button|my card is inactive how do i start using it
age_limit:minimum age for an account|how old do i have to be|can a minor sign up|is there an age restriction|i am under 18 can i use this
apple_pay_or_google_pay:can i add my card to apple pay|does it support google wallet|pay with my iphone|use my card in my digital wallet|set up gpay
atm_support:which cash machines can i use|can i get cash from any atm|where is the nearest cashpoint|where can i withdraw money|does the card work in atms overseas
automatic_top_up:set up an automatic top up|add money whenever my balance is low|disable recurring reloads|can my account refill itself
balance_not_updated_after_bank_transfer:i transferred money from my other bank but it is not showing in my balance|an incoming wire has not been credited|where is the money i sent to my own account|external bank sent funds and my balance is still zero
balance_not_updated_after_cheque_or_cash_deposit:i deposited cash but it is not in my balance|my cheque deposit has not appeared|i paid in a check and have not been credited|cash deposit missing
beneficiary_not_allowed:why is my beneficiary not allowed|cannot add a new payee|this recipient is not supported|the app will not let me send money to that account|beneficiary bank is restricted
cancel_transfer:can i stop my bank transfer|please cancel the money i just sent|i sent money to the wrong person|recall a wire|can i undo a transfer
card_about_to_expire:my card is expiring soon|what happens when my debit card expires|my card is past its expiry date|how do i renew my card
card_acceptance:where is my card accepted|can i pay in shops overseas|can i use the card for online purchases|can i use this card at a hotel or for car rental|can i pay with my card abroad
card_arrival:where is the card i ordered|my card has not arrived yet|track my card shipment|the app says my card was delivered but i never got it|my new card is late
card_delivery_estimate:how long does card delivery take|when can i expect my new card|what is the estimated arrival date for my card|is express shipping available for the card|how quickly will the physical card arrive
card_linking:link a card to my account|associate my existing card with the app|attach a new physical card to my profile|can i register the card i have already received
card_not_working:my card does not work|i cannot use my card anymore|my card stopped working|the chip on my card is damaged|my debit card will not work anywhere
card_payment_fee_charged:why have i been charged a fee for paying with my card|there is a surcharge on a card purchase|i was charged a commission when i paid the merchant|why does making a card payment cost extra
card_payment_not_recognised:i do not recognise a card payment|a purchase has appeared that i did not make|what is this unfamiliar merchant on my statement|my account shows an unauthorized transaction|there is a payment i never approved
card_payment_wrong_exchange_rate:the conversion rate was wrong when i paid by card|i got a bad exchange rate on this purchase|i was billed in a different currency at a restaurant|why was the rate on my foreign card payment so high
card_swallowed:the atm kept my card|a cash machine ate my debit card|my card is stuck in the atm|the machine did not give my card back
cash_withdrawal_charge:why was i charged a fee to withdraw cash|is there a fee for using an atm|the cash machine charged me extra|why did i pay a commission on my cash withdrawal
cash_withdrawal_not_recognised:i did not make this cash withdrawal|there is an atm transaction i do not recognise|someone took money out of a cash machine using my card|i see a cash withdrawal that is not mine
change_pin:how do i change my card pin|i forgot the pin for my debit card|where can i see my pin number|reset my cash machine pin|can i choose a different pin
compromised_card:i think somebody has stolen my card details|i think my card has been cloned|i gave my card number to a scammer|my card has been compromised|someone else might have access to my card
contactless_not_working:tapping my card does not work|my contactless payments are being declined|why will my card not tap|the chip works but paywave does not|my card does not work without inserting it
country_support:in which countries can i open an account|can i sign up from canada|is this service available where i live|which countries do you support|can i join as a resident of japan
declined_card_payment:why was my card payment declined|my purchase was rejected at the checkout|the merchant says the payment did not go through|i have enough money but my card was declined|my payment was refused in store
declined_cash_withdrawal:my atm withdrawal was declined|the atm refused to let me take out cash|why was my cash withdrawal rejected|i could not get money from the cashpoint
declined_transfer:why did you decline my transfer|bank rejected the money i tried to send|my wire transfer was refused|what caused the transfer to be denied
direct_debit_payment_not_recognised:i do not recognise this direct debit|an unfamiliar direct debit appeared in my account|i have not authorized this automatic debit|i did not set up this direct debit mandate
disposable_card_limits:how many times can i use a disposable virtual card|is there a limit on my single use card|can i use the disposable card for subscriptions|how many disposable cards can i make per day
edit_personal_details:change the phone number on my account|update my home address|edit my personal information|i need to change my email address|my surname has changed
exchange_charge:do you charge a fee to exchange currency|what is the commission for converting money|is there a markup on exchanging at weekends|is it free to buy euros in the app
exchange_rate:what exchange rate do you use|what is your rate for euros to pounds|what is the current conversion rate|do you use the interbank rate|where can i see the exchange rates
exchange_via_app:how do i convert currencies in the app|how can i change my pounds into euros|i want to swap my dollar balance for pounds|where is the currency exchange feature
extra_charge_on_statement:i was charged an extra dollar on my account|i noticed a small extra charge on my statement|there is an additional amount i do not understand|why is there a one pound charge|why have i paid more than the price
failed_transfer:why did my transfer fail|i get an error when i try to transfer money|unable to complete a bank transfer|my transfer was unsuccessful|i tried to send the money but it did not go through
fiat_currency_support:which fiat currencies are supported|can i hold japanese yen in my account|what currencies can i store|which currencies are available to exchange|can i have a balance in swiss francs
get_disposable_virtual_card:where can i get a disposable virtual card|how do i create a single use card|i want a temporary one time card|what is a disposable card
get_physical_card:how can i get a physical card|can i have a real plastic card|do you provide a physical debit card|i only have a virtual card can i get an actual card
getting_spare_card:can i have a spare card|can i get a second physical card|i would like an additional card|how do i get a backup debit card|can i have more than one card on my account
getting_virtual_card:how do i get a virtual card|can i make a digital debit card|where do i find my virtual card details|i want to create an online only card
lost_or_stolen_card:i lost my card|my debit card was stolen|i cannot find my bank card|my wallet was stolen with my card in it|i misplaced my card and want to block it
lost_or_stolen_phone:my phone was stolen|i lost the phone i use for the app|my mobile is missing|how do i lock my account if i lose my phone
order_physical_card:i want to order a new physical card|where do i go in the app to order a card|can you send me a new debit card|i want to request a plastic card|how do i place an order for the card
passcode_forgotten:i forgot my app passcode|i cannot log in because i forgot the code|how do i reset my password|i am locked out of the app|i cannot remember my login code
pending_card_payment:why is my card payment still pending|the purchase is processing|my card transaction is on hold|what does pending mean next to a payment|the merchant has not collected the payment yet
pending_cash_withdrawal:my cash withdrawal is pending|my atm transaction is still processing|why is the withdrawal showing as pending even though i got the cash
pending_top_up:my top up is pending|i added money by card and it is still processing|why has my top up not shown up yet|i reloaded my account but the funds are not available yet
pending_transfer:my transfer is pending|the outgoing bank transfer is still processing|why is the wire on hold|i have an outgoing transaction|what is the status of the transfer i sent
pin_blocked:i entered the wrong pin too many times|my card pin is blocked|how can i unblock my pin|three incorrect pin attempts|the cash machine says my pin is locked
receiving_money:can i receive money from someone else|can my employer pay my salary into this account|how do i get paid by bank transfer|can my friend send me money|how can i receive payments into this account
refund_not_showing_up:the merchant refunded me but it has not arrived|my refund is not showing in the balance|where is my refund|i am still waiting for the money the shop returned|how long does my refund take to appear
request_refund:i want a refund for a purchase|how can i get my money back from a merchant|can i dispute a card payment|please refund this transaction|i did not get the item i paid for can you get my money back
reverted_card_payment:why was my card payment reverted|my purchase was reversed and the money came back|the payment went back into my balance|the card transaction completed and then was cancelled
supported_cards_and_currencies:which cards can i use to top up|what currencies are supported for top ups|can i add money with an american express card|can i use a credit card from another country to fund my account|which debit cards can i add money with
terminate_account:how can i close my account|please delete my account|i want to cancel my membership|how do i permanently deactivate my profile|i no longer want the account
top_up_by_bank_transfer_charge:is there a fee to top up by bank transfer|my bank charged me to add money by wire|how much does it cost to transfer funds in from another bank|what fees are there for a bank top up
top_up_by_card_charge:what fee is there to top up by card|there is a charge on my card for adding money|is it free to use a credit card to top up|i had to pay extra to reload my balance with my debit card
top_up_by_cash_or_cheque:can i top up with cash or a cheque|how do i deposit notes in my account|can i pay in a check|can i put physical cash in my balance|are cash deposits supported
top_up_failed:my top up failed|why was my card top up declined|i cannot add funds to my account|the app gives me an error when i try to reload|my deposit by card did not go through
top_up_limits:what is the maximum amount i can top up|how much can i add to the account at once|is there a daily limit for adding money|what is the minimum top up|my top up limit is too low
top_up_reverted:my top up was reverted|why did the money i added go back to my bank|the top up was reversed|my card deposit was returned to the original card
topping_up_by_card:how can i top up with my debit card|how do i add money to my account|can i use my personal card to load money|where do i enter my card to add funds
transaction_charged_twice:i was charged twice for the same transaction|my payment was duplicated|a purchase shows up two times on the statement|the merchant took the same amount twice|there are two identical charges
transfer_fee_charged:why was i charged for sending money|is there a fee for an international transfer|my transfer arrived minus a fee|why did the bank deduct a commission from my wire
transfer_into_account:how do i transfer money into my account from my bank|what are the details for topping up by bank transfer|can i fund my account with a wire|how do i move money from my other account into this one
transfer_not_received_by_recipient:i sent money but the recipient never received it|my friend says the transfer did not arrive|the transfer is complete but it is not in their bank account|the beneficiary has not got the money yet
transfer_timing:how long does a bank transfer take|what is the turnaround time for a wire|when will the transfer get there|are transfers instant|do transfers go through on weekends
unable_to_verify_identity:i cannot verify my identity|my passport was rejected by the app|my identity verification is stuck|the app will not accept my selfie|i have tried uploading my id and keep getting an error
verify_my_identity:how do i verify my identity|what documents can i use for identity verification|can i use a driving licence as id|where do i submit my passport and selfie|what do i need for verification
verify_source_of_funds:why do you need proof of income|how do i verify my source of funds|what payslips do i need to show|how do i prove where my money comes from|which documents prove source of wealth
verify_top_up:how can i verify my top up|where is the four digit verification code on my bank statement|why do i need to confirm the card i used to add money|how do i validate my funding card
virtual_card_not_working:my virtual card is not working|my virtual card transaction keeps getting declined|i cannot pay online using the virtual card|my disposable card was rejected at checkout
visa_or_mastercard:is the card visa or mastercard|will i get a visa card|can i choose mastercard instead|which network is my card issued on
why_verify_identity:why do you need to verify my identity|why are you asking me for my id|what is the purpose of uploading my passport|why must i prove who i am
wrong_amount_of_cash_received:the atm gave me less cash than i requested|cash machine took money from my account but did not dispense any notes|i got the wrong amount of cash|only part of the cash came out of the atm
wrong_exchange_rate_for_cash_withdrawal:wrong exchange rate on my cash withdrawal|what conversion rate did the atm use|the cash machine gave me a bad rate when withdrawing abroad|why was my foreign atm withdrawal converted at that rate
"""

_PUNCT = re.compile(r"[^a-z0-9]+")
_REPLACEMENTS = (
    (r"\b(?:can not|can't|cannot|couldn't|won't|wouldn't|shan't)\b",
     lambda m: {"couldn't": "could not", "won't": "will not",
                "wouldn't": "would not", "shan't": "shall not"}.get(m.group(), "can not")),
    (r"\b([a-z]+)n't\b", r"\1 not"),
    (r"\b(i|you|we|they)'(?:ve)\b", r"\1 have"),
    (r"\b(i)'m\b", r"\1 am"),
    (r"\b(you|we|they)'re\b", r"\1 are"),
    (r"\b(i|you|we|they|he|she|it)'ll\b", r"\1 will"),
    (r"\b(it|that|what|there|where|he|she|who)'s\b", r"\1 is"),
    (r"\b(?:dont|doesnt|didnt|isnt|arent|wasnt|werent|havent|hasnt|hadnt|couldnt|wont|wouldnt|cant)\b",
     lambda m: {"dont": "do not", "doesnt": "does not", "didnt": "did not",
                "isnt": "is not", "arent": "are not", "wasnt": "was not",
                "werent": "were not", "havent": "have not", "hasnt": "has not",
                "hadnt": "had not", "couldnt": "could not", "wont": "will not",
                "wouldnt": "would not", "cant": "can not"}[m.group()]),
    (r"\btop[\s_-]*up(s)?\b", r"top up\1"),
    (r"\btopp(ed|ing)[\s_-]+up\b", r"topp\1 up"),
    (r"\b(?:applepay|apple[\s_-]+wallet|ios[\s_-]+wallet)\b", "apple pay"),
    (r"\b(?:googlepay|g[\s_-]*pay|android[\s_-]+pay|google[\s_-]+wallet)\b", "google pay"),
    (r"\bmaster[\s_-]*card\b", "mastercard"),
    (r"\bpass[\s_-]*code(s)?\b", r"passcode\1"),
    (r"\b(?:checks|cheques)\b", "cheques"),
    (r"\b(?:canceled|cancelling|canceling)\b", "cancelled"),
    (r"\b(?:authori[sz]ed|authorised)\b", "authorised"),
    (r"\bunauthori[sz]ed\b", "unauthorised"),
    (r"\brecogniz", "recognis"),
    (r"\bunrecogniz", "unrecognis"),
    (r"\bp[.\s]+i[.\s]+n\b", "pin"),
    (r"\ba[.\s]+t[.\s]+m\b", "atm"),
    (r"\bi[.\s]+d\b", "id"),
    (r"\b(?:cashpoint|cash[\s_-]+point|cash[\s_-]+machine|cash[\s_-]+dispenser|bank[\s_-]+machine|bankomat)s?\b",
     "atm"),
    (r"\b(?:currancy|curreny|curency)\b", "currency"),
    (r"\b(?:recieve|recieved|recieving|recipent|recipiant|transfert|transation|witdrawal|withrawal)\b",
     lambda m: {"recieve": "receive", "recieved": "received", "recieving": "receiving",
                "recipent": "recipient", "recipiant": "recipient", "transfert": "transfer",
                "transation": "transaction", "witdrawal": "withdrawal",
                "withrawal": "withdrawal"}[m.group()]),
)
_REPLACEMENTS = tuple((re.compile(pat), sub) for pat, sub in _REPLACEMENTS)


def _normalise(text):
    text = text.casefold().replace("’", "'").replace("‘", "'").replace("`", "'")
    text = text.replace("£", " gbp ").replace("€", " eur ").replace("$", " dollar ").replace("¥", " yen ")
    text = "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))
    for pattern, replacement in _REPLACEMENTS:
        text = pattern.sub(replacement, text)
    return _PUNCT.sub(" ", text).strip()


@lru_cache(maxsize=768)
def _pattern(pat):
    return re.compile(r"\b(?:" + pat + r")\b")


_STOP = frozenset("""
a an the to and but it is are was were be been being my me i am ive im you your yours
we our us its their they them he she his her of for from in into on with at by as that
this these those have has had can could should would will shall do did does please
tell let know want need just about already there here some what which how when where why
""".split())
_FORMS = {}
for _group in (
    "card cards", "pay payment payments paying paid pays", "purchase purchases purchased",
    "charge charges charged charging", "transfer transfers transferred transferring",
    "send sends sent sending", "receive received receiving receives got get gets getting",
    "arrive arrives arrived arrival arriving", "deliver delivered delivering delivery deliveries",
    "withdraw withdraws withdrawing withdrawal withdrawals withdrew withdrawn",
    "deposit deposited depositing deposits", "add adds added adding load loading loaded loads",
    "fail fails failing failed failure unsuccessful error errors", "decline declined declining declines refused denied rejected",
    "reverse reversal reversed reversing reverted revert reversion",
    "pending processing progress processed",
    "verify verified verifying verification validate validation",
    "exchange exchanging exchanged exchanges convert converts converted converting conversion",
    "currency currencies", "fee fees surcharge surcharges commission",
    "recognise recognised recognising", "unrecognised unknown unfamiliar",
    "activate activated activating activation", "order orders ordering ordered",
    "expire expires expired expiring expiration expiry",
    "refund refunds refunded refunding", "link linked linking attach register",
    "lost lose losing misplaced missing", "steal stolen stole theft",
    "cancel cancelled cancelling cancellation", "account accounts", "balance balances",
    "atm atms cashpoint", "check cheque cheques", "cash notes banknotes",
    "code codes", "limit limits maximum minimum", "block blocked blocking unblock",
    "address addresses", "work working works worked", "document documents documentation",
    "identity id identification", "virtual digital", "physical plastic", "photo photos picture",
    "phone mobile cellphone smartphone", "pound pounds gbp sterling", "euro euros eur",
    "dollar dollars usd", "extra additional", "duplicate duplicated twice",
    "recipient beneficiary payee", "recurring automatic automatically",
):
    _forms = _group.split()
    for _word in _forms:
        _FORMS[_word] = _forms[0]


def _terms(text):
    tokens = [_FORMS.get(w, w) for w in text.split() if w not in _STOP]
    result = set(tokens)
    result.update(a + " " + b for a, b in zip(tokens, tokens[1:]))
    return result


_TITLES = {}
_PROTOTYPES = []
_COUNTS = Counter()
for _line in _PHRASES.strip().splitlines():
    _label, _phrases = _line.split(":", 1)
    _title = _normalise(_label)
    _TITLES[_title] = _label
    _sets = [_terms(_normalise(s)) for s in _phrases.split("|")] + [_terms(_title)]
    _COUNTS.update(set().union(*_sets))
    for _features in _sets:
        _PROTOTYPES.append((_label, _features))
_WEIGHTS = {w: (0.95 if " " not in w else 1.12) *
            (1.0 + math.log((1.0 + len(_TITLES)) / (1.0 + n)))
            for w, n in _COUNTS.items()}
_PROTOTYPES = tuple((label, features, sum(_WEIGHTS[w] for w in features))
                    for label, features in _PROTOTYPES)
_EXAMPLES = {
    _normalise("I have an outgoing transaction"): "pending_transfer",
    _normalise("I was charged an extra dollar on my account and would like to know the reason."):
        "extra_charge_on_statement",
}

_CURRENCY = (r"(?:gbp|eur|usd|aud|cad|chf|jpy|nzd|sek|nok|dkk|zar|try|hkd|sgd|thb|aed|inr|pln|czk|huf|ron|mxn|brl|cny|rmb|ils|krw|idr|vnd|php|uah|rub|sar|"
             r"yen|dollars?|euros?|pounds?|sterling|francs?|rupees?|baht|zlotys?|lira|yuan|krona|kronor|pesos?|dirhams?|won|forints?|ringgit|koruna)")
_PLACE = (r"(?:united states|united kingdom|u s a|usa|uk|u k|eu|europe|european union|america|american|"
          r"australia|canada|england|scotland|wales|ireland|france|germany|spain|portugal|italy|"
          r"poland|romania|hungary|greece|netherlands|belgium|switzerland|austria|sweden|finland|"
          r"norway|denmark|iceland|india|china|japan|korea|singapore|malaysia|vietnam|thailand|"
          r"indonesia|philippines|mexico|argentina|brazil|colombia|chile|peru|new zealand|turkey|"
          r"turkiye|dubai|uae|south africa|pakistan|russia|ukraine|croatia|serbia|israel|hong kong|"
          r"saudi arabia|nigeria|kenya|egypt|taiwan|czech republic|czechia|estonia|latvia|lithuania|"
          r"bulgaria|slovakia|slovenia|malt[a]|cyprus|luxembourg|bangladesh|morocco|qatar|iran|iraq|"
          r"venezuela|uruguay|puerto rico|california|texas|new york|florida)")
_CARD = r"cards?|debit card|credit card|my visa|my mastercard"
_WITHDRAW = r"withdraw(?:s|ing|als?|n)?|withdrew|cash out|withdrawing money|tak(?:e|ing|en|es) (?:out (?:some )?(?:cash|money)|(?:some )?(?:cash|money) out)|took (?:out (?:some )?(?:cash|money)|(?:some )?(?:cash|money) out)"
_FUND = (r"top ups?|topp(?:ed|ing) up|reload(?:s|ed|ing)?|recharg(?:e|ed|ing) (?:my|the) (?:account|balance)|"
         r"(?:add|added|adding|load|loaded|loading|put|putting|deposit|deposited|depositing) "
         r"(?:(?:some|more|my|the|any|in) ){0,2}(?:money|funds|cash|gbp \d+|eur \d+|dollar \d+)|"
         r"fund(?:ing)? (?:my|an?|this|the) (?:account|balance)|(?:deposit|deposited|add|added|put) \d+ " + _CURRENCY)
_TRANSFER = r"transfers?|transfer(?:red|ring)|wires?|wired|wiring|remittance|sepa|swift transfer|ach|bank payment|bank to bank"
_SEND_MONEY = r"(?:send|sent|sending|move|moved|moving) (?:(?:some|the|my|any|them|him|her|more|over) ){0,3}(?:money|funds|" + _CURRENCY + r"|\d+)"
_BANK_RAIL = r"bank transfers?|bank account|another bank|other bank|external bank|my bank|wire(?:s|d| transfer)?|sepa|ach|swift|iban|sort code|routing number"
_PAYMENT = r"payments?|paying|paid|pay|purchases?|checkout|point of sale|pos purchase|merchant|bought|buying|charged|spent|spending"
_PURCHASE = r"merchant|purchases?|checkout|point of sale|pos purchase|card (?:payments?|transactions?|purchases?)|using (?:my|the) card to pay|paid (?:for|with|by)|paid (?:a|the) (?:shop|seller|merchant)|bought|shopping|(?:spent|spending) (?:money|abroad)|(?:at|in) (?:a|the) (?:shop|store|restaurant|supermarket)"
_FAILURE = r"fail(?:s|ed|ures?|ing)?|unsuccessful|error(?:s| message)?|did not go through|does not go through|will not go through|would not go through|could not (?:complete|make|finish)|can not (?:complete|make|finish)|did not work|does not work"
_DECLINE = r"declin(?:e|ed|es|ing)|reject(?:ed|s|ion|ing)?|refus(?:e|ed|es|al)|denied|denies|denial|not approved|not authorised|disallowed"
_PENDING = (r"pending|in progress|(?:still |being )processing|being processed|processing status|"
            r"awaiting (?:approval|confirmation|processing|completion)|stuck|on hold|under review|"
            r"not yet (?:complete|completed|processed|cleared|gone through)|has not (?:cleared|gone through|completed|processed) yet|waiting to (?:clear|go through)|taking (?:so|too) long")
_MISSING = (r"miss(?:ing|ed)|(?:not|never) (?:yet )?(?:arriv(?:e|ed)|received?|reach(?:ed)?|come|came|shown?(?: up)?|showing(?: up)?|appeared?|credited|paid in|added|updated|reflected|applied|hit|made it)|"
            r"not (?:there|here|in (?:my|the|their|his|her) (?:bank|account|balance))|"
            r"(?:do|does|did|can|could) not (?:got|get|see|find|have|receive)|nothing (?:in|is showing|has come|has arrived|has changed|changed|showed up|came through|has shown up)|"
            r"still (?:waiting|the same|zero|has not|have not|no)|balance (?:is|stays|remains) (?:the same|unchanged|zero)|where (?:is|are) (?:it|the money|my money|the funds)|not showing|not appearing")
_REVERSE = (r"revert(?:ed|s|ing)?|revers(?:ed|al|ing)|returned|rolled back|bounced(?: back)?|sent back|"
            r"(?:money|funds|amount|it|payment) (?:has |have )?(?:gone|went|come|came|got) back|"
            r"back (?:in|into|to|on) (?:my|the) (?:original |other |source )?(?:account|bank|card|balance)|undone")
_UNKNOWN = (r"unrecognised|unauthorised|unfamiliar|unknown|suspicious|fraudulent|"
            r"(?:do|does|did|can|could) not (?:recognis\w*|remember|recall|authoris\w*|approve|know (?:what|who)|make (?:it|this|that|any|the|a)|withdraw)|"
            r"(?:never|not) (?:made|authorised|approved|initiated|used|withdrew|set up|bought)|"
            r"(?:have|has) not (?:made|authorised|approved|initiated|used|withdrawn|set up|bought|ordered)|"
            r"(?:is|are|was|were) not (?:mine|me|my transaction|my payment)|"
            r"not (?:a payment |a transaction |an expense |something )?i (?:made|approved|authorised|recognise)|"
            r"i did not (?:do|pay for|buy|take out|order|spend|set up)|i know nothing about|someone (?:else )?(?:used my card|made a payment|withdrew)|"
            r"what (?:is|was) this (?:transaction|payment|purchase)|out of nowhere")
_FEE = (r"fees?|surcharges?|commissions?|mark ?ups?|levy|service charges?|handling charges?|"
        r"(?:charge|charges|charged|charging) (?:me |us )?(?:extra|additional|for|to use|interest)|"
        r"(?:extra|additional|unexpected|unexplained|hidden|small) (?:amount|cost|charge|charges|charging|fee|debit)|"
        r"charg(?:e|ed|ing) (?:me )?more|cost(?:s|ing)? (?:me |us )?(?:for|to|anything|extra)|"
        r"how much (?:is (?:it|the charge)|do (?:i|you) charg\w*|(?:does|will) it cost)|"
        r"(?:is it|for) free|free of charge|fee free")
_TIMING = (r"how long|how (?:many|much) (?:[a-z]+ )?(?:days|hours|weeks|time)|how (?:soon|quickly|fast)|"
           r"when (?:will|would|can|do|should|am i|is|does)|what (?:is|are) the (?:wait|delivery|shipping|estimated|expected|turnaround)|"
           r"time (?:frame|estimate|to deliver|to arrive|does it take|will it take)|eta|estimated (?:delivery|arrival|time|date)|"
           r"expected (?:arrival|delivery|date)|delivery (?:times?|estimate)|shipping times?|how quick|instant|turnaround|same day")
_ELAPSED = (r"(?:[0-9]+|a few|several|one|two|three|four|five|six|seven|ten|a couple of) (?:business |working )?"
            r"(?:days?|weeks?|months?|hours?) ago|last (?:week|month|monday|tuesday|wednesday|thursday|friday|saturday|sunday)|"
            r"overdue|late|taking (?:too|so) long|(?:already |it has )?been (?:over |more than )?(?:an?|[0-9]+|one|two|three|four|five|several|a few|a couple of) "
            r"(?:business |working )?(?:days?|weeks?|months?|hours?)")
_EXCHANGE = r"exchange(?:d|s)?|exchanging|conver(?:t|ted|ts|ting|sion)|forex|fx|foreign exchange|swap currenc\w*"
_RATE = r"(?:exchange|conversion|interbank|market|foreign|currency|fx|forex) rates?|rate of exchange|exchange at|rate (?:did|was|were|used|is|do|does|for|on)|(?:bad|wrong|better|real|poor|unfair|mid market|different|higher|lower|best|live) rate|conversion factor|dynamic currency conversion|dcc"
_LIMIT = r"limits?|limited|maximum|minimum|max|min|cap|ceiling|allowed per|how (?:much|many)(?: [a-z]+){0,4} (?:can|may|am|are|at once|per day)|(?:most|least) i can|up to how much"
_TROUBLE = (r"not (?:working|work|able|going through|recognised|accepted|letting|valid)|"
            r"can not|could not|will not|would not|unable|unable to|does not let|did not let|"
            r"stopped working|quit working|having (?:an? |some )?(?:trouble|problems?|issues?)|problem with|something (?:has gone|went|is) wrong|broken|damaged|"
            + _DECLINE + "|" + _FAILURE)
_LOST = r"lost|mis(?:laid|placed)|stolen|stole|missing|robbed|pickpocketed|can not find|could not find|left (?:it |my [a-z]+ )?(?:in|at|on)"
_REQUEST = r"how (?:can|do|would|should|to)|where (?:can|do|should)|can (?:i|you|we)|i (?:want|wish|would like|need)|please|is (?:it|there a way) possible|is there a way|help me|could (?:i|you)"
   


def _rule_scores(s):
    def h(pattern):
        return _pattern(pattern).search(s) is not None

    def seq(first, second, gap=5):
        return h(r"(?:" + first + r")(?: [a-z0-9]+){0," + str(gap) + r"} (?:" + second + r")")

    def near(first, second, gap=5):
        return seq(first, second, gap) or seq(second, first, gap)

    scores = {}

    def put(label, points, condition=True):
        if condition and points > scores.get(label, 0):
            scores[label] = points

    card = h(_CARD)
    virtual = h(r"virtual(?: debit| credit)? card|e card|digital (?:debit |credit )?card|online only card|electronic card")
    disposable = h(r"disposable|single use (?:virtual )?card|one (?:time|off) (?:use |virtual )?card|temporary virtual card|burner card|throwaway card")
    physical = h(r"physical|plastic|real card|actual card|tangible card|hard copy card")
    atm = h(r"atms?")
    withdraw = h(_WITHDRAW)
    cash_out = withdraw or atm or h(r"cash (?:dispensed|did not come out|never came out)|dispens(?:e|ed|ing) (?:any |the |my )?(?:money|notes|cash)|atm transaction")
    digital_wallet = h(r"apple pay|google pay|samsung pay|wallet app|digital wallet|mobile wallet|android wallet|pay (?:using|with) my (?:phone|iphone|watch)|contactless with my (?:phone|iphone|watch)")
    top = h(_FUND)
    explicit_top = h(r"top ups?|topp(?:ed|ing) up|reload(?:ed|s|ing)?")
    bank_rail = h(_BANK_RAIL)
    transfer = h(_TRANSFER) or h(_SEND_MONEY) or h(r"outgoing (?:transaction|payment)|incoming transfer|bank to bank")
    bank_transfer = h(r"bank transfers?|wire(?:s|d| transfer)?|sepa|ach|swift transfer|transferred from (?:a|my|another|an|the) (?:[a-z]+ ){0,3}bank")
    payment = h(_PAYMENT)
    purchase = h(_PURCHASE)
    direct_debit = h(r"direct debits?|debit mandate|automatic (?:bank )?debit|debit order")
    refund = h(r"refund(?:s|ed|ing)?|chargeback|money back from (?:the|a) (?:merchant|seller|shop)|(?:merchant|seller|shop) (?:gave|giving|sent|sending|has sent) (?:the |my )?money back")
    declined = h(_DECLINE)
    failed = h(_FAILURE)
    trouble = h(_TROUBLE)
    pending = h(_PENDING)
    missing = h(_MISSING)
    reversed_payment = h(_REVERSE)
    unknown = h(_UNKNOWN)
    why = h(r"why|what (?:is|was) the (?:reason|purpose)|what (?:made|caused)|reason (?:for|why)|how come|explain|what for")
    ask = h(_REQUEST)
    timing = h(_TIMING)
    elapsed = h(_ELAPSED)
    fees = h(_FEE)
    limits = h(_LIMIT)
    fx = h(_EXCHANGE)
    rate = h(_RATE)
    currency = h(_CURRENCY + r"|currenc(?:y|ies)|foreign (?:money|denomination)|fiat")
    location = h(_PLACE + r"|countr(?:y|ies)|abroad|overseas|international(?:ly)?|territor(?:y|ies)|region")
    statement = h(r"statements?|transaction (?:list|history|log)|payment history|charged to my account")
    posted = h(r"charged|debited|deducted|taken (?:the )?(?:money|amount)|money (?:was )?taken|(?:came|gone|went) out of (?:my|the) account")
    balance = h(r"balances?|(?:my|this|your|the) account|in (?:the|my|your|this) app|funds available")
    supported = h(r"support(?:s|ed)?|accept(?:ed|s)?|allow(?:ed|s)?|compatible|available|eligible|possible|which|what (?:type|kind|cards|currencies|countries)|can i use")
    generic_currency_list = h(r"(?:which|what|supported|available|different|all|many|multiple|list of) (?:fiat |foreign )?currenc(?:y|ies)")
    cash_in = h(r"(?:cheque|cheques|paper check|bank check|check deposit|deposit(?:ing|ed)? (?:a |the |my )?check|check (?:in|into) (?:my|the) account|"
                r"cash deposits?|deposit(?:s|ed|ing)? (?:some |my |physical |in )?cash|pay(?:ing)? (?:cash|notes|a check|a cheque) (?:in|into)|"
                r"(?:pay|paid|paying) in (?:cash|notes|a check|a cheque)|cash or (?:a )?(?:cheques?|checks?)|"
                r"cash to (?:top up|fund|load)|top up (?:via|by|with|using|in) (?:physical )?cash|"
                r"(?:add|put|load) (?:some |physical |my )?(?:cash|banknotes|notes) (?:in|into|on|to)|"
                r"put cash in|physical money into|fund(?:ing)? (?:my|the) account with cash)")
    if cash_in and h(r"pay(?:ing)? in cash") and (cash_out or purchase) and not h(r"deposit|top up|account|cheque"):
        cash_in = False

    # Account access, registration, personal data, and checks.
    login = h(r"log(?: ?in|ging in)|sign(?: ?in|ing in)|unlock (?:the|my) app|access (?:the|my) (?:app|profile|account)")
    forgotten = h(r"forg(?:ot(?:ten)?|et)|can not remember|do not remember|do not know|lost|where (?:is|can i find)|reset|new code|recover|retrieve")
    passcode = h(r"passcodes?|passwords?|(?:login|log in|sign in|access|app|security|unlock) (?:pin|code)|code to (?:open|access|log)")
    pin = h(r"pin(?: number| code)?|personal identification number")
    verify = h(r"verif(?:y|ied|ies|ication|ying)|validat(?:e|ing|ion)|authentication|authenticat(?:e|ing)|confirm(?:ation|ing)?|prove|proof|kyc")
    identity = h(r"identit(?:y|ies)|identif(?:ication|y) (?:me|myself)|kyc|who i am|id checks?|photo id|(?:my|an|a|the|your|upload) id|id (?:verification|cards?|documents?|photo|is|be)|passports?|selfies?|national identity|driv(?:ing|er s|ers) licen[cs]e")
    source = h(r"source of (?:funds|wealth|money|income)|proof of (?:income|earnings|funds|salary|wealth)|payslips?|pay slips?|"
               r"(?:where|how) (?:my|the|this|your) (?:money|funds|income|wealth) (?:comes?|came|is coming|originat\w*|was earned)|"
               r"(?:origin|origins|provenance) of (?:my|the|your) (?:money|funds|wealth)|(?:salary|employment|income) (?:statements?|documents?|verification)")
    put("verify_source_of_funds", 113, source)

    age = h(r"age (?:limit|restriction|requirement)|(?:minimum|maximum|legal|old enough|at what) age|how old|under ?age|"
            r"under (?:the age of )?(?:16|17|18|19|21)|(?:over|be|at least) (?:the age of )?(?:16|18|21) to (?:apply|use|get|open|join|sign)|"
            r"(?:for|as) (?:a |an )?(?:minor|child|children|kids|teens?|teenagers?)|"
            r"(?:age|aged) (?:1[0-9]|20|21)|(?:i am|is|am) (?:only |just )?(?:1[0-9]|20|21) years? old|"
            r"(?:i am|am) (?:only |just )?1[0-9](?: and| can| do| may| will| is|$)|(?:child|teen|minor) account")
    put("age_limit", 104, age)

    details = r"(?:phone|mobile|contact|telephone) (?:number|details)|address|post ?code|zip code|e ?mail(?: address)?|(?:personal|profile|contact|account) (?:information|data|details)|(?:first|last|full|legal|married) name|surname|date of birth|birthdate|name on (?:my|the) account"
    edit = r"chang(?:e|ed|ing)|edit(?:ing)?|updat(?:e|ed|ing)|correct(?:ed|ing)?|amend|modify|wrong|incorrect|mistake|new"
    changing_details = near(edit, details, 5) or h(r"(?:change|edit|update) my name|moved (?:house|to a new)|got married|different address now")
    put("edit_personal_details", 98, changing_details)
    put("edit_personal_details", 64, h(details) and h(r"profile|settings|personal information") and ask)

    close_action = r"close|closing|terminate|terminating|delete|deleting|deactivate|shut down|shut|cancel|cancellation|remove|end|get rid of"
    close_account = seq(close_action, r"account|profile|membership", 5) or h(r"no longer (?:use|using|want|need) (?:this|the|my) (?:account|profile)|stop using (?:the|this|my) (?:service|account|app)")
    put("terminate_account", 109, close_account and not h(r"delete (?:my |the )?(?:old )?(?:phone|email|number|card)|close (?:a |the |my )?(?:transfer|transaction)"))

    put("passcode_forgotten", 109, passcode and (forgotten or trouble or login))
    put("passcode_forgotten", 97, login and forgotten and h(r"code|credentials|can not log|can not access"))
    put("passcode_forgotten", 82, h(r"locked out of (?:the |my )?(?:app|account)|can not log in|forgot (?:my )?login") and not identity)
    put("passcode_forgotten", 66, passcode)

    lost_phone = near(_LOST, r"(?:my|a|the) (?:mobile phone|mobile device|phone|mobile|smartphone|iphone|android|cell phone|cellphone|device)", 4)
    lost_phone = lost_phone and not h(r"forgot|lost my (?:phone|mobile) number|lost access to (?:my )?(?:phone|mobile) number")
    lost_card = near(_LOST, r"(?:my|a|the|our|your) (?:physical |debit |credit |bank |new )?cards?", 4)
    lost_card = lost_card and not (not atm and h(r"shipped|delivered|in the mail|on its way|being delivered|courier|shipment|never arrived"))
    put("lost_or_stolen_phone", 118, lost_phone)
    put("lost_or_stolen_card", 112, lost_card or h(r"(?:my )?wallet (?:was |has been |got )?(?:lost|stolen)|(?:stolen|lost|misplaced) (?:debit |credit |bank )?card|(?:my )?card (?:was |has been |got )?stolen"))
    put("lost_or_stolen_card", 70, card and h(r"(?:freeze|block) my card|report my card") and not (unknown or trouble))

    pin_locked = (pin and (h(r"unblock|unlock|blocked|locked|blocked pin|lockout|pin tries|pin attempts|too many (?:tries|attempts|times)|exceeded") or
                            h(r"(?:wrong|incorrect) (?:pin|number|code).{0,45}(?:twice|three|3|multiple|many|several|times)|entered (?:it |my pin )?(?:wrong|incorrectly).{0,35}(?:3|three|times)"))) and not login
    put("pin_blocked", 113, pin_locked)
    put("pin_blocked", 99, h(r"(?:three|3|too many) (?:failed|wrong|incorrect) (?:attempts|tries|pins)|pin (?:is )?block\w*"))
    put("pin_blocked", 76, h(r"unblock (?:my |the )?card"))
    put("change_pin", 104, pin and not (pin_locked or login or passcode) and
        (forgotten or h(r"chang(?:e|ing)|set|setting|pick|choose|view|see|show|find|check|personalise|create|what (?:is|was)")))
    put("change_pin", 70, pin and not pin_locked and not login)

    top_verify = verify and (top or h(r"funding card|source card|card used to (?:load|add|deposit)|top up verification"))
    verification_code = h(r"verification code|confirmation code|security code|(?:four|4) digit (?:code|number)|code on (?:my|the) (?:bank )?statement")
    put("verify_top_up", 109, top_verify)
    put("verify_top_up", 104, verification_code and (statement or top or h(r"verify (?:my |the )?card")))
    put("verify_top_up", 74, verification_code and not (identity or login or pin or passcode))

    id_context = identity or (verify and h(r"verify (?:me|myself|my profile|my account)|account verification|verification (?:process|status|documents?)") and not top_verify)
    id_problem = trouble or pending or missing or h(r"fail(?:s|ed|ing)?|keeps? (?:asking|rejecting)|(?:verification|upload) (?:did not|does not)|not (?:verif\w*|clear|valid enough|matching)|still (?:unverified|being verified)|expired|blurry|unreadable|camera is not")
    id_reason = h(r"why (?:do|does|did|am|are|should|must|is|would|have|can) |what (?:is|s) the (?:reason|purpose)|why verify|for what purpose|why need") and (
        verify or identity or h(r"upload|submit|send"))
    put("unable_to_verify_identity", 106, id_context and id_problem and not (source or top_verify))
    put("why_verify_identity", 102, id_context and id_reason and not id_problem)
    put("why_verify_identity", 104, id_context and h(r"why (?:do|would|must|should) (?:i|you|we) (?:need|have|want|ask)|why (?:the|an?|my) (?:id|passport|selfie)|why (?:is|are) .{0,32}(?:necessary|required)") and not id_problem)
    put("verify_my_identity", 89, id_context)
    put("verify_my_identity", 97, id_context and h(r"what (?:kind|type|sort|forms?|documents?)|which (?:documents?|id)|use (?:a|an|my) .{0,28}(?:as id|to verify)|(?:how|where).{0,24}(?:verify|upload|submit|prove)"))
    put("verify_my_identity", 73, verify and h(r"upload|documents?|photo|picture|licen[cs]e") and not (top_verify or source))

    enrollment = h(r"sign up|register|join|open (?:up )?(?:a|an|my|the|this) account|creat(?:e|ing) (?:a|an|my|the|this) account|set up (?:a|an|my|the|this) account|get (?:a|an|my) account|eligible|residen(?:t|ce|cy|ts)|citizen(?:s|ship)?")
    lives = h(r"i (?:live|reside|am living|am based|am from|come from)|my country|where i live|resident of|based in")
    put("country_support", 107, (location or lives) and enrollment and not (transfer or age))
    put("country_support", 101, h(r"(?:which|what|supported|available|list of) countr(?:y|ies)|countr(?:y|ies) (?:are|is) (?:supported|eligible)|in my country") and not (cash_out or transfer or purchase or explicit_top or h(r"cards? (?:work|accepted)|use (?:my|the) card")))
    put("country_support", 93, location and not (cash_out or purchase or transfer or top or card) and (supported or ask or lives))
    put("country_support", 94, lives and (ask or supported) and not (cash_out or transfer or top or purchase))

    # Card hardware, ordering, and everyday use.
    stole_details = near(r"card (?:details|information|number|data|credentials)|my cvv", r"stolen|stole|leak(?:ed)?|exposed|scam|scammer|phish(?:ed|ing)?|hacked|compromised|has access|got (?:hold of|access)|gave|give|shared|share|someone has|someone got|somebody has|somebody got", 8)
    compromise = h(r"compromised|cloned|skimmed|card skimming|card cloning|copied my card|my card (?:has been |was |is |got )?(?:hacked|skimmed|cloned|copied)|"
                   r"(?:someone|somebody) (?:else )?(?:(?:may|might|could) (?:have |be )?|is )?(?:using|have used|has used|use|has been using) my card|"
                   r"(?:someone|somebody) (?:has|had|knows|got) my card (?:number|details)")
    put("compromised_card", 117, stole_details or (compromise and (card or not h(r"phone|email|password|account was hacked"))))
    put("compromised_card", 96, card and h(r"card fraud|report fraud|fraud on my card|block (?:my|the) card.{0,28}fraud") and not h(r"this (?:payment|transaction|purchase)|a (?:transaction|purchase)"))
    if stole_details:
        scores.pop("lost_or_stolen_card", None)

    swallow = h(r"swallow(?:ed|ing|s)?|ate|eaten|retain(?:ed|s|ing)?|keep(?:s|ing)?|kept|held on to|took|taken|stuck|jammed|trapped|"
                r"not (?:return|release|give|eject|spit out|get|take)(?: [a-z]+){0,4} (?:card|it)|"
                r"(?:card|it) (?:did not|will not|does not|never) come out")
    put("card_swallowed", 121, atm and card and swallow and
        (near(r"swallow(?:ed|ing|s)?|ate|eaten|retain(?:ed|s|ing)?|keep(?:s|ing)?|kept|took|taken|stuck|jammed|trapped|return|release|give|eject|spit out|come out",
              r"card", 6) or h(r"card in (?:an?|the) atm")))
    put("card_swallowed", 104, card and near(r"swallow(?:ed|ing|s)?|ate|eaten", r"card", 6))

    expired = h(r"expir(?:y|ation|e|ed|es|ing)|renew(?:al)?|out of date|valid until|valid thru|validity date")
    put("card_about_to_expire", 108, (card or virtual) and expired and not (identity or explicit_top or h(r"expired (?:passcode|code)|(?:card|payment) (?:authorization|authorisation) expired")))
    put("card_about_to_expire", 94, h(r"(?:renew|expir\w*) .{0,20}card|card .{0,20}(?:expir\w*|renew)"))

    activate = h(r"activat(?:e|ing|ed|ion)|inactive|not active|enable (?:my|the|a) (?:new )?(?:physical )?card|start using .{0,20}(?:new|first) card|make .{0,20}card active")
    link = h(r"\blink(?:s|ed|ing)?|attach(?:ed|ing)?|associat(?:e|ed|ing)|pair(?:ed|ing)?|connect(?:ing|ed)?|register|bind")
    put("activate_my_card", 107, activate and (card or h(r"activate it|activation code")) and not digital_wallet)
    put("card_linking", 103, link and card and not (digital_wallet or (top and h(r"use|top up with|fund|verification"))))
    put("card_linking", 91, card and not top and h(r"(?:add|register|attach) (?:an?|my|the) (?:new |existing |old |physical |debit |bank |credit )?card (?:to|in|on) (?:my|the|this) (?:account|app|profile)"))
    put("card_linking", 78, card and not top and h(r"add (?:a|my|another) (?:new )?card") and not (virtual or disposable or digital_wallet or physical))

    delivered = h(r"deliver(?:ed|s|ing|y)?|shipp?(?:ed|ing|ment)?|send out|sent out|dispatch(?:ed)?|in the (?:mail|post)|mail(?:ed|ing)? (?:my |the )?card|post(?:ed|ing|al)? (?:my |the )?card|courier|parcel|package|arriv(?:al|e|es|ed|ing)|track(?:ing)?|card order status|has not (?:come|received)|(?:receive|received|get|got) (?:my|the) (?:new |physical )?card")
    ordered = h(r"ordered|requested|order (?:for|has|is)|placed (?:my |an |the )?order|sent me (?:a|the) card")
    card_where = h(r"where (?:is|are) (?:my|the) (?:new |physical |ordered |debit )?cards?|where (?:has|did) (?:my|the) card|track(?:ing)? (?:my |the |number|a )?card|card (?:order|delivery) status")
    card_delay = h(r"not (?:got|had|received|arrived|come|delivered|shipped)|never (?:got|received|arrived|come|came|delivered)|lost in (?:the )?(?:post|mail)|still (?:no|waiting)|did not (?:get|receive|come|arrive)|arrived (?:late|at the wrong)|delivered to (?:the )?wrong|marked (?:as )?delivered|delivery (?:failed|delayed)|past (?:the|its) delivery")
    put("card_arrival", 115, card and (card_where or ((delivered or ordered) and (card_delay or (missing and not timing) or (elapsed and not timing)))) and not (virtual and not physical))
    put("card_arrival", 103, card and delivered and h(r"track|tracking|where (?:is|has|did)|not (?:arrive|arrived|received|come)|overdue|standing of") and not virtual)
    put("card_delivery_estimate", 105, card and (delivered or timing or ordered) and not (virtual or payment and not delivered or transfer and not delivered) and
        (timing or h(r"delivery time|express|expedited|fast(?:er|est) (?:delivery|shipping)|speed up|delivery date|shipping date|arrive by")))
    put("card_delivery_estimate", 91, card and delivered and h(r"how (?:long|soon|quickly)|when|what day|what date|estimate") and not cash_out)
    put("card_arrival", 82, card and delivered and (ordered or h(r"deliver|delivered|sent|shipped")) and not (timing or activate or link))
    put("card_delivery_estimate", 79, card and delivered and not (ordered or missing or elapsed or cash_out))

    spare = h(r"(?:spare|extra|additional|second|backup|back up|supplementary|another|multiple|two|2|several) (?:physical |debit |bank |credit )?cards?|"
              r"more than one (?:physical |debit )?card|(?:another|extra|additional|spare|second) one (?:of|for|in case)|"
              r"(?:two|multiple|more) (?:cards|cardholders) (?:on|for|linked)|get a card for (?:my|someone)")
    card_order = h(r"(?:order|ordering|request(?:ing)?|apply for|reorder|replace) (?:me )?(?:a |my |the |your |an )?(?:new |replacement |first |physical |plastic |debit |bank |credit ){0,3}cards?|"
                   r"place (?:a|an|my|the) (?:physical |debit )?card order|send (?:me |us )?(?:my |a |the )?(?:new |physical |plastic |replacement |debit |bank ){0,3}card|"
                   r"get my card sent|replacement (?:debit |physical |bank |credit )?card")
    card_get = h(r"(?:get|getting|obtain|acquire|have|offers?|provides?|issue|comes? with|give|eligible for) (?:me )?(?:a |an |my |the |your |any )?(?:new |first |real |actual |physical |plastic |debit |bank |credit ){0,3}cards?")
    put("getting_spare_card", 108, spare and not (disposable or virtual))
    put("order_physical_card", 103, card_order and not (virtual and not physical or disposable))
    put("get_physical_card", 101, physical and card and (card_get or ask or supported or h(r"instead of|from virtual|actual|real")) and not card_order)
    put("get_physical_card", 92, card_get and not (spare or card_order or (virtual or disposable) and not physical))
    put("get_physical_card", 70, physical and card)
    put("order_physical_card", 83, card and h(r"card order|ordering|reorder") and not (virtual or disposable))

    use_count = limits or h(r"how often|how many times|multiple (?:times|uses)|reuse|re use|reusable|more than once|used twice|"
                            r"subscriptions?|recurring (?:payment|payments|purchase)|only once|per (?:payment|purchase|transaction)|what .{0,20}restrictions")
    put("disposable_card_limits", 109, disposable and use_count)
    put("disposable_card_limits", 101, disposable and h(r"(?:can|could|may) i use|(?:are|is) (?:it|they) allowed"))
    put("get_disposable_virtual_card", 98, disposable)
    recent_attempt = h(r"tried|attempted|trying|keeps?|kept|every time|refused|rejected|declined|stopped|suddenly|used it|has not worked")
    put("virtual_card_not_working", 112, (virtual or disposable) and trouble and
        not (h(r"get a virtual card|create a virtual card|generate a virtual card|find my virtual card|see my virtual card") and not (payment or recent_attempt)) and
        not (physical and card_get))
    put("getting_virtual_card", 99, virtual and not physical and (ask or h(r"create|generate|issue|show|find|details|set up|open|make") or card_get))
    put("getting_virtual_card", 80, virtual and not physical)

    contactless = h(r"contactless|tap(?:ped|ping)? (?:my|the|to pay|and pay|a)|tap to pay|paywave|pay wave|paypass|pay pass|nfc|without (?:entering (?:my|the) pin|insert(?:ing)? (?:the|my) card)")
    put("contactless_not_working", 111, contactless and trouble and not digital_wallet)
    put("contactless_not_working", 82, contactless and not digital_wallet)
    put("apple_pay_or_google_pay", 113, digital_wallet and not (top and (fees or pending or declined or failed or reversed_payment)))
    put("apple_pay_or_google_pay", 82, digital_wallet)

    network = h(r"visa|mastercard|card network|visa branding")
    network_choice = h(r"visa or mastercard|mastercard or visa|which (?:network|brand)|either visa|issue(?:d)?|is (?:it|my card|the card|this card)|do (?:you|i) (?:get|give|have|offer|provide)|(?:can|may) i (?:get|have|request|choose|order|pick|switch)|i (?:want|prefer|would like)|instead of|will i (?:get|receive)|difference between")
    put("visa_or_mastercard", 108, network and network_choice and not (top or identity and not h(r"mastercard")))
    put("visa_or_mastercard", 89, network and not (top or identity or cash_out or h(r"travel visa|work visa|student visa|visa application")))
    card_usage = h(r"use (?:my|the|a|this|your) (?:[a-z]+ ){0,2}card|(?:card|cards) (?:work|accepted|usable|take[n]?|be used)|pay (?:with|by|using) (?:my|the|a|this|your)? ?card|accept (?:my|the|this|your) card|where (?:can|do) i (?:use|pay)|can i (?:make .*card payment|pay (?:online|abroad|in shops|in stores))")
    card_venue = h(r"online|online shopping|international(?:ly)?|abroad|overseas|worldwide|in stores?|e ?commerce|shops?|restaurant|hotel|car rental|rent (?:a )?car|gas station|abroad|on holiday|during travel")
    put("card_acceptance", 97, (card_usage or card and card_venue) and not (top or cash_out or transfer or trouble or declined or virtual or digital_wallet) and (ask or supported or card_venue or h(r"where|anywhere|everywhere")))
    put("card_acceptance", 87, card and card_venue and location and not (fee_context := (fees and (payment or posted))) and not (top or cash_out or transfer or recent_attempt or pending))
    put("card_not_working", 86, card and trouble and not (top or transfer or cash_out or digital_wallet or purchase and declined))
    put("card_not_working", 94, card and h(r"(?:card|chip|stripe) (?:is |has |got |was )?(?:broken|damaged|not working|not reading|stopped working|bent|scratched)|card (?:does|will|did) not work") and not (top or transfer or cash_out or digital_wallet))
    put("card_not_working", 77, card and h(r"blocked|frozen|suspended") and not (top or pin_locked or withdraw or unknown or lost_card))

    # Fee, exchange, and statement issues.
    duplicate = h(r"duplicate(?:d)?|double (?:charge|charged|charging|debit|payment|transaction|billing|billed)|"
                  r"(?:charged|paid|debited|billed|processed|deducted|taken|went through|shows? up|appears?|shows?) (?:me |it |again |for (?:it|this|that|the same [a-z]+) )?(?:twice|two times|2 times|a second time)|"
                  r"twice for (?:one|a|the|this|that|the same)|same (?:payment|charge|amount|purchase|transaction|merchant|item|thing|money) .{0,40}(?:twice|two times|again|second time)|"
                  r"(?:two|2) (?:identical|duplicate|of the same|matching) (?:transactions?|payments?|charges?|withdrawals?)|"
                  r"(?:two|2) (?:charges?|payments?|transactions?|debits?) (?:for|on) (?:the same|one|a single)|"
                  r"twice (?:on my statement|on my account|as much|in my transactions)|charged two times")
    put("transaction_charged_twice", 122, duplicate and not h(r"(?:twice|two times) (?:a day|a week|a month|per day|per week|per month)|double check"))
    put("transaction_charged_twice", 110, h(r"(?:charged|deducted|debited|billed|purchase|transaction|payment).{0,30}(?:twice|a second time|two times)|(?:twice|double) .{0,18}(?:charged|debited|billed)") and not h(r"twice (?:a|per)|double check|tried.{0,12}twice|pay (?:twice|two times) (?:with|using) (?:a |my )?(?:disposable|single use)"))

    unexpected_fee = h(r"(?:extra|additional|small|unexpected|unexplained|mystery|random|strange|weird|odd|unknown) (?:fee|sum|amount|dollar|pound|charge|transaction|debit)|"
                       r"charged (?:me )?(?:an? )?(?:extra|more|too much)|more (?:than|money than) (?:i |the |it |what )?(?:should|expected|paid|spent|actual|price|total)|"
                       r"price (?:does not match|is different)|overcharged|overcharged me|small (?:deduction|payment)|extra (?:\d+|" + _CURRENCY + ")")
    small_auth = h(r"(?:gbp|dollar|eur|usd|pound|euro) 1(?: 0{1,2})?|(?:1|one) (?:gbp|dollars?|eur|usd|pounds?|euros?)|(?:a |one )?(?:dollar|pound|euro) charge|small charge|nominal charge|test charge")
    put("extra_charge_on_statement", 107, small_auth and (posted or fees or statement or unexpected_fee) and not (top_verify or duplicate))
    put("extra_charge_on_statement", 97, unexpected_fee and not (cash_out or explicit_top or transfer) and (statement or posted or fees))
    put("extra_charge_on_statement", 85, (statement or balance) and posted and (why or fees))
    put("extra_charge_on_statement", 76, unexpected_fee or fees and not (cash_out or top or fx or transfer or purchase))

    money_rate = ((rate or fx or h(r"converted|conversion|charged in (?:a )?different currency")) and
                  (currency or cash_out or card or payment or why or ask or rate))
    foreign = h(r"foreign|abroad|overseas|international|different currency|local currency|converted|conversion|exchange")
    currency_tokens = set(_pattern(_CURRENCY).findall(s))
    bad_rate = h(r"bad rate|wrong rate|unfair rate|off rate|rate .{0,24}(?:wrong|off|incorrect|bad|poor|different|higher|lower|terrible)|"
                 r"(?:wrong|bad|incorrect|poor|terrible|different|unexpected) (?:exchange|conversion|fx|currency|amount|rate)|"
                 r"(?:billed|charged|paid|converted) in (?:the )?(?:wrong|different) currency|overcharged")
    past_payment = posted or h(r"paid|bought|got|withdrawn|withdrew|took|used|made|last|yesterday|recent(?:ly)?|was|were|did|applied")
    put("wrong_exchange_rate_for_cash_withdrawal", 116, cash_out and (money_rate or foreign and bad_rate) and (bad_rate or past_payment or why))
    put("wrong_exchange_rate_for_cash_withdrawal", 100, cash_out and (money_rate or foreign and h(r"rate|converted")) and not cash_in)
    put("card_payment_wrong_exchange_rate", 116, not cash_out and not (transfer or top) and
        ((money_rate and (purchase or card or payment) and (bad_rate or past_payment or why)) or
         (len(currency_tokens) >= 2 and (purchase or card) and posted and (why or bad_rate or foreign))))
    put("card_payment_wrong_exchange_rate", 102, not (cash_out or transfer or top) and (bad_rate or money_rate and past_payment) and (card or purchase or payment))

    exchange_action = (h(r"(?:how|where|want|need|can i|trying|way to|steps|in the app|on the app|via the app)") and
                       (fx or h(r"(?:change|swap|buy|sell|switch) (?:my |some |the )?" + _CURRENCY)))
    put("exchange_charge", 105, (fx or currency and h(r"changing|converting|weekend|mark ?up|interbank")) and fees and not (cash_out or top or transfer or purchase and past_payment and bad_rate))
    put("exchange_charge", 92, rate and h(r"weekends?|mark ?up|surcharge|fees?|commission") and not (cash_out or top or transfer))
    put("exchange_rate", 95, rate and not (cash_out or bad_rate and (card or purchase or payment)))
    put("exchange_rate", 101, rate and h(r"what (?:is|are|rate)|which rate|interbank|mid market|see (?:my |the |your )?rates|rate (?:do|does) (?:you|it) use|rates? (?:today|right now)") and not (cash_out or fees or past_payment and (card or purchase or payment)))
    put("exchange_rate", 83, fx and h(r"rate|value|worth|how much|current|best|market|today|history") and not top)
    put("exchange_via_app", 100, exchange_action and not fees and not (rate or cash_out or top or transfer or purchase and past_payment or generic_currency_list))
    put("exchange_via_app", 85, fx and h(r"convert my|exchange money|currency conversion|exchanging money|foreign exchange|convert money|between currencies") and not (rate or fees or cash_out))
    put("exchange_via_app", 66, fx)
    put("fiat_currency_support", 104, generic_currency_list and not (explicit_top or cash_out or received_currency_context(s)))
    put("fiat_currency_support", 101, currency and h(r"hold|store|keep|maintain|create|open|balances?|accounts? in|denominated in|wallet in|support(?:s|ed)?|availab\w*|fiat") and not (fees or rate or top or transfer or cash_out or purchase))
    put("fiat_currency_support", 92, currency and supported and not (rate or top or transfer or cash_out or card_usage))
    put("fiat_currency_support", 76, currency and not (top or fees or cash_out or rate or fx or cash_in))

    # Cash withdrawals and other card-payment states.
    if cash_out:
        no_cash = h(r"(?:no|not any|zero) (?:cash|money|notes)(?: (?:came|dispensed))?|"
                    r"(?:(?:did|does|could|would|will) not|never|failed to) (?:dispense|give(?: me)?|get|receive|release|hand out|get out|come out) (?:any |my |the |some )?(?:cash|money|notes|banknotes)|"
                    r"(?:cash|money|notes) (?:never|(?:did|does) not) (?:come|came|come out)|"
                    r"dispensed nothing|without (?:giving|dispensing|receiving|getting) (?:me )?(?:any |my |the )?(?:cash|money)")
        wrong_cash = h(r"wrong (?:amount|sum|number of notes)|(?:less|fewer|more) (?:cash|money|notes|than (?:i|requested|expected))|"
                       r"(?:only|just) (?:gave|dispensed|received|got|got back)|(?:gave|dispensed) (?:me )?(?:only|just)|"
                       r"shortchang(?:ed|ing)|did not (?:give|dispense|get|receive) (?:me )?(?:all|the full amount|the (?:correct|right) amount)|"
                       r"partial (?:cash|dispense|amount|withdrawal)|difference between .{0,40}(?:withdraw\w*|notes)|amount .{0,20}(?:different|incorrect)")
        put("cash_withdrawal_not_recognised", 115, unknown and not h(r"withdrawal (?:was|is) (?:not authorised|refused|denied)") and
            (withdraw or h(r"cash|atm transaction") or posted))
        put("wrong_amount_of_cash_received", 114, wrong_cash and not (bad_rate or fees and not h(r"dispensed|gave me|i got|received|notes")))
        put("wrong_amount_of_cash_received", 113, no_cash and (posted or h(r"deducted|my balance|went through|successful|completed|account shows")))
        put("wrong_amount_of_cash_received", 91, no_cash and atm and not (declined or failed))
        put("cash_withdrawal_charge", 108, fees and not (cash_in and not withdraw) and not (wrong_cash and h(r"dispensed|gave me|notes")))
        put("cash_withdrawal_charge", 101, posted and unexpected_fee and not (wrong_cash or small_auth or cash_in))
        put("pending_cash_withdrawal", 109, pending and not (cash_in and not withdraw))
        put("pending_cash_withdrawal", 88, withdraw and (missing or h(r"not completed|still waiting for it")) and not (wrong_cash or no_cash))
        put("declined_cash_withdrawal", 108, (declined or failed or withdraw and trouble) and not (cash_in and not withdraw))
        put("declined_cash_withdrawal", 104, no_cash and not posted and h(r"tried|trying|can not|would not|refused"))
        put("atm_support", 90, not cash_in and (ask or supported or location or limits or h(r"where|which|find|nearest|near me|all atms|any atm")) and not (card_get or card_order or pin))
        put("atm_support", 70, not cash_in)

    put("direct_debit_payment_not_recognised", 116, direct_debit and (unknown or statement or posted or why))
    put("direct_debit_payment_not_recognised", 89, direct_debit)
    if not (top or transfer or cash_out and not purchase or direct_debit):
        put("card_payment_not_recognised", 108, unknown and (payment or statement or h(r"transactions?|charges?|debit|debits|taken from")))
        put("card_payment_not_recognised", 98, unknown and (card or balance))
        put("card_payment_not_recognised", 94, statement and h(r"what (?:is|was) (?:this|that|the) (?:charge|payment|purchase)|do not understand this (?:charge|payment)|a charge i do not"))
        put("card_payment_fee_charged", 109, fees and (purchase or card and payment) and not small_auth and not bad_rate)
        put("card_payment_fee_charged", 101, fees and card and not (card_get or card_order or small_auth or bad_rate) and h(r"charged|using|paying|spending|charge for|use my card"))
        put("card_payment_fee_charged", 95, fees and payment and not small_auth)
        put("reverted_card_payment", 110, (reversed_payment or h(r"(?:was|got|has been) (?:automatically )?cancelled|cancelled itself")) and not refund and (payment or card or h(r"transaction")))
        put("reverted_card_payment", 96, reversed_payment and balance and not refund)
        put("pending_card_payment", 108, pending and (purchase or payment or h(r"transactions?")))
        put("pending_card_payment", 89, pending and not (identity or cash_in or refund))
        put("declined_card_payment", 107, (declined or failed or trouble) and (purchase or payment and not (unknown or refund)))
        put("declined_card_payment", 105, declined and card)
        put("declined_card_payment", 100, declined and h(r"declined (?:at|in|when)|(?:store|shop|restaurant|online|website|transaction).{0,24}declin"))
        put("declined_card_payment", 81, declined)
        put("pending_card_payment", 62, payment or h(r"transactions?"))

    # Refunds: requesting one versus following up on one already issued.
    refund_where = h(r"where (?:is|are) (?:my|the) refund|status of (?:my|the) refund|when (?:will|should|do) i (?:get|see|receive) (?:my |the |a )?refund|"
                     r"refund .{0,24}(?:how long|not (?:showing|appearing|received)|has not|still pending|not in)|waiting for (?:my |the |a )?refund")
    refund_issued = h(r"refunded|issued (?:me )?(?:a|the|my) refund|refund (?:was|has been|went|is being) (?:issued|sent|processed|made)|"
                      r"sent (?:me )?(?:the|a|my) refund|(?:merchant|shop|seller|company|retailer) .{0,30}(?:returned|gave|sent) .{0,25}(?:refund|money back)|"
                      r"(?:promised|approved|confirmed|processed) (?:that |me )?(?:a |my |the )?refund")
    refund_request = h(r"(?:want|need|would like|request|claim|get|obtain|issue|give me|ask for|arrange|make) (?:a |my |the )?refund|refund (?:me|my payment|this purchase|my money|this transaction)|"
                       r"take (?:my |the )?money back|(?:get|want|need|give me) (?:my |the )?money back|disput(?:e|ing) (?:a|this|the|my) (?:payment|transaction|charge)|chargeback|reverse (?:a|the|this|my) (?:payment|charge|purchase)")
    put("refund_not_showing_up", 115, refund and (refund_where or refund_issued and (missing or pending or timing or why or elapsed)))
    put("refund_not_showing_up", 109, refund and (missing or (pending and not transfer) or (timing and not h(r"request|apply for|want to|ask for"))))
    put("refund_not_showing_up", 95, refund and refund_issued and not (top or cash_in))
    put("request_refund", 110, refund_request and not (refund_issued or refund_where or transfer and not refund))
    put("request_refund", 92, refund and not (top and reversed_payment and not refund_request))
    put("request_refund", 83, purchase and h(r"never (?:got|received) (?:it|the item|my order|the product)|(?:order|product|item) .{0,22}(?:not (?:arrived|received|delivered)|never arrived)"))

    # Funding and bank transfers; direction distinguishes balance from recipient issues.
    bank_in = h(r"(?:from|via|using) (?:my |a |an |another |the |an? external |my other |my regular |my own |my old ){0,2}(?:[a-z]+ ){0,2}bank(?: account)?|"
                r"from (?:my|another|an|the) (?:other |own |external |different |old |regular |separate |savings |checking )?(?:accounts?|bank)|"
                r"into (?:my|this|your|the) (?:account|balance)|to (?:my|this|your) (?:own |new |current )?account|"
                r"incoming (?:funds?|payment|transaction|(?:bank )?transfer|wire)|(?:bank |wire )?transfer(?:red)? (?:to|for) me|"
                r"money (?:sent|wired|transferred|coming) (?:to|for) me|(?:sent|wired|transferred) (?:me|myself) (?:some |the )?(?:money|funds|a transfer|a payment)|"
                r"(?:sent|wired|paid|transfer(?:red)?) into my account|(?:sepa|wire|swift|bank transfer) .{0,30}(?:my balance|in the app)")
    bank_out = h(r"outgoing|to (?:the |my |a |an |another )?(?:recipient|beneficiary|payee|friend|partner|seller|brother|sister|customer|landlord|husband|wife|mother|father|son|daughter)|"
                 r"(?:into|to|in) (?:their|his|her|someone else s) (?:bank |payment )?account|sent (?:him|her|them) (?:money|funds|the)|"
                 r"(?:from|out of) (?:my|this) (?:app|balance|account) (?:to|into) (?:an? |my |the )?(?:other |external |another |different )")
    receiver = h(r"beneficiar(?:y|ies)|recipients?|payees?|(?:my|a) (?:friend|wife|husband|partner|brother|sister|parents?|mother|father|son|daughter)|"
                 r"person (?:i|who|that)|people i (?:paid|sent)|their (?:account|end|side|bank)|his (?:account|bank)|her (?:account|bank)|"
                 r"(?:they|he|she) (?:did|do|does|have|has|can|could|is|are) (?:still )?not|other (?:person|party|side|end)")
    third_party_in = h(r"receiv(?:e|ed|ing) (?:my |a |an |some |the )?(?:salary|payments?|money|transfers?|funds|bank transfer)|"
                       r"(?:someone|somebody|anyone|a friend|my friend|another person|my employer|my company|my client|people|customers|friends|family) "
                       r"(?:can |could |has |have |will |would |just |is trying to ){0,2}(?:send|sent|pay|paid|transfer|transferred|wire|wired)"
                       r"|(?:send|transfer|wire) (?:(?:me|money|funds|some|any|cash) ){1,4}(?:from|to me)|"
                       r"get paid|pay my (?:salary|wages)|receive (?:a |my )?(?:paycheck|wages)|"
                       r"(?:my|a) (?:salary|wages|payroll|paycheck|pension)|payment (?:from|sent by) (?:someone|my employer|my client)|"
                       r"(?:money|payments|transfers) from (?:other people|other users|friends|family|clients|customers)|incoming (?:payment|transaction)")
    relevant_top = top and not (cash_in and not explicit_top)
    bank_funding = relevant_top and (bank_transfer or bank_rail and not h(r"(?:by|with|using|via) (?:my |a |an |the )?(?:debit |credit |bank )?card"))
    fund_card = relevant_top and not bank_funding or top and h(r"top up (?:by|with|via|using) (?:a |an |my |the )?(?:debit |credit |bank )?card")
    deposit_balance_issue = missing or h(r"(?:balance|account) (?:still |has |is )?(?:not updated|not changed|unchanged|still zero)|(?:i have|i see|balance is) the same (?:balance|amount)|where (?:is|has) (?:my|the) (?:deposit|cheque|check|cash)")
    incoming_balance_issue = (missing or h(r"balance (?:did|does|has) not (?:change|update|reflect)|where (?:is|has) (?:my|the) incoming")) and not bank_out
    bank_credit_issue = (bank_in and (transfer or bank_rail or third_party_in) or bank_funding or
                         third_party_in and balance and not explicit_top or bank_transfer and balance and not bank_out)
    put("balance_not_updated_after_cheque_or_cash_deposit", 116, cash_in and deposit_balance_issue)
    put("top_up_by_cash_or_cheque", 104, cash_in)
    put("balance_not_updated_after_bank_transfer", 111, bank_credit_issue and incoming_balance_issue and not (cash_in or reversed_payment or declined or failed and not missing))
    put("balance_not_updated_after_bank_transfer", 107, bank_credit_issue and h(r"balance .{0,26}(?:no change|still the same|did not go up|not increased|has not (?:gone up|changed)|zero)|not credited to (?:my|the) account") and not cash_in)

    auto_reload = h(r"auto (?:top up|reload|fund|add)|automatic(?:ally)? (?:top|reload|fund|add|deposit|put)|"
                    r"(?:top up|add (?:funds|money)|reload) automatic(?:ally)?|recurring (?:top up|reload|deposit|fund)|scheduled (?:top up|reload)|"
                    r"(?:set|set up|enable|turn on|disable|turn off) .{0,15}auto(?:matic)?|"
                    r"when(?:ever)? (?:my |the )?balance (?:gets low|is low|runs low|drops|falls|goes under|goes below|reaches)|replenish(?:es)? (?:the|my) balance")
    put("automatic_top_up", 115, auto_reload and (top or balance or h(r"top up|reload|falls below|drops below")))

    if relevant_top:
        put("top_up_limits", 109, limits and not (withdraw or disposable) and not h(r"withdrawal limit|card payment limit"))
        put("top_up_by_bank_transfer_charge", 113, fees and bank_funding)
        put("top_up_by_card_charge", 111, fees and fund_card)
        put("top_up_reverted", 116, (reversed_payment or h(r"(?:was|got|has been) (?:automatically )?cancelled|cancelled itself|refunded to (?:the|my) (?:bank|card)")) and not (refund_where or h(r"not (?:reversed|returned|reverted)")))
        put("top_up_failed", 112, declined or failed or trouble and h(r"can not|unable|will not|does not let|tried|rejected|refused|not working"))
        put("pending_top_up", 112 if explicit_top and not bank_funding else 105, pending)
        put("pending_top_up", 108 if not bank_funding else 93, missing and not (declined or failed or reversed_payment))
        put("pending_top_up", 102, h(r"charged my card|debited (?:my|the) card|taken from (?:my|the) (?:credit |debit )?card") and (missing or pending))
        funding_card_types = h(r"(?:what|which|type of|kind of|any|supported|accept(?:ed|s)?|all) (?:payment |bank |debit |credit )?cards?|"
                               r"american express|amex|prepaid|maestro|diners club|discover card|unionpay|visa|mastercard|"
                               r"foreign (?:credit |debit |bank )?card|(?:someone|somebody|another person) else s card|"
                               r"card (?:issued |from |in )?(?:abroad|overseas|another country|the us|the uk)|"
                               r"credit (?:or|and) debit|debit (?:or|and) credit")
        put("supported_cards_and_currencies", 107, (funding_card_types or generic_currency_list) and not (pending or reversed_payment) and
            (supported or ask or h(r"cards? (?:are|do)|american express|amex|currency|currencies")))
        put("supported_cards_and_currencies", 101, currency and supported and h(r"top up (?:in|using|with)|funds? in|currenc\w* can i|which currenc\w*|card is in|card in") and not fees)
        put("transfer_into_account", 103, bank_funding and not (fees or declined or failed or missing or pending))
        put("topping_up_by_card", 95, fund_card and (card or digital_wallet))
        put("topping_up_by_card", 89, fund_card)
        put("topping_up_by_card", 65)

    payee = h(r"beneficiar(?:y|ies)|recipient|payee|destination (?:bank|account)|(?:the|this|that) (?:recipient s|beneficiary s)? ?(?:bank|account) (?:is|was) not")
    restricted = h(r"not (?:allowed|supported|permitted|valid|eligible|available|accepted)|disallowed|restricted|blocked|invalid|blacklist\w*|cannot be made to|can not be made to|unable to .{0,24}(?:add|recipient|beneficiary)|(?:country|bank) .{0,16}unsupported|unsupported")
    cannot_add_payee = near(r"can not|could not|unable|will not|does not let|error|rejected|problem", r"add(?:ing)? (?:a |an |my |this |the |any |new ){0,3}(?:payee|recipient|beneficiary)", 6)
    put("beneficiary_not_allowed", 114, payee and (restricted or cannot_add_payee))
    put("beneficiary_not_allowed", 108, transfer and (restricted and h(r"destination|to this (?:bank|account)|to that (?:bank|account|person)|to (?:this|that|the) country|account details|bank details not accepted") or cannot_add_payee))
    put("beneficiary_not_allowed", 77, payee and h(r"add(?:ing)? (?:a |an |my |the |any |new ){0,3}(?:payee|recipient|beneficiary)") and not third_party_in)

    cancel_verb = r"cancel(?:ling|lation)?|stop|undo|recall|rescind|call back|take back|retract|reverse|abort|remove"
    cancel_intent = seq(cancel_verb, _TRANSFER + r"|money i sent|payment i sent|(?:outgoing|bank) (?:payment|transaction)|(?:money|the money) (?:sent|wired)", 7)
    cancel_intent = cancel_intent and not h(r"(?:did (?:you|it|the bank)|the bank|you|automatically) (?:cancel|cancelled)|(?:was|has been|got) cancelled|what (?:has|was) cancelled")
    wrong_destination = h(r"wrong (?:recipient|beneficiary|payee|person|account|iban|bank|number|details)|incorrect (?:recipient|account number|iban|sort code|beneficiary)|accidentally (?:sent|transferred|wired)|(?:sent|transferred) .{0,25}by mistake")
    put("cancel_transfer", 119, transfer and (cancel_intent or wrong_destination or h(r"(?:get|want|need) (?:the |my )?money back|cancel it|stop it|recall it|reverse it") and not refund))
    put("cancel_transfer", 116, cancel_intent and not reversed_payment)

    recipient_missing = (receiver or bank_out) and (
        missing or h(r"(?:they|he|she|the recipient|the beneficiary) (?:are|is) (?:still )?waiting|"
                     r"(?:they|he|she) (?:have|has) yet to (?:get|receive|see)|money (?:is|was) not (?:with them|with him|with her)"))
    sent_before = h(r"sent|wired|made (?:a|the|an|my) transfer|transferred|confirmed|successfully|complete(?:d)?|went through|left my account")
    put("transfer_not_received_by_recipient", 116, transfer and recipient_missing and not (bank_in and not bank_out and not h(r"their account|recipient|beneficiary")))
    put("transfer_not_received_by_recipient", 102, transfer and sent_before and missing and not (bank_in or third_party_in or explicit_top or pending or cash_in or h(r"my balance")))
    put("transfer_not_received_by_recipient", 101, h(r"(?:they|he|she|the recipient|the beneficiary|my friend) (?:did|does|do|has|have|can) not (?:get|receive|have|see) (?:it|the money|the funds|the transfer|anything)") and not refund)

    if transfer and not (explicit_top and not h(r"outgoing|money i sent|to (?:the |my )?recipient")):
        put("declined_transfer", 111, declined or h(r"transfer (?:was|got|has been) blocked|bank (?:blocked|declined|rejected|refused)"))
        put("failed_transfer", 109, failed or h(r"can not (?:send|transfer|wire)|(?:not|unable to) (?:send|transfer|wire)|trouble (?:sending|transferring)|not letting me (?:send|transfer)|transfer (?:would|will|does) not go through"))
        put("failed_transfer", 104, reversed_payment or h(r"transfer (?:was|got|has been) cancelled|not going through"))
        put("pending_transfer", 112, pending and not (bank_in and incoming_balance_issue) and not (declined or h(r"failed|unsuccessful")))
        put("pending_transfer", 106, h(r"status of (?:my|the) (?:bank )?(?:transfer|wire)|track (?:my|the) (?:bank )?(?:transfer|wire)|where (?:is|has) (?:my|the) (?:outgoing |bank )?(?:transfer|wire)|still waiting") and not (bank_in and incoming_balance_issue))
        put("pending_transfer", 101, sent_before and (missing or elapsed and h(r"when|yet|wait")) and not (bank_in or recipient_missing))
        put("pending_transfer", 97, h(r"outgoing (?:transaction|payment|transfer)|(?:has|did) (?:my |the )?transfer (?:go through|gone through|clear|cleared)|transfer .{0,22}not (?:complete|completed|finished)"))
        put("transfer_timing", 105, (timing or h(r"banking days|working days|business days|go through on (?:weekends|saturdays|sundays|holidays)")) and
            not (pending or recipient_missing or missing and not h(r"usually|normally|typically|in general")) and not fees)
        put("transfer_timing", 96, timing)
        put("transfer_fee_charged", 110, fees and not (bank_funding or cash_out or fx and not bank_rail))
        put("transfer_fee_charged", 103, h(r"(?:received|got|arrived with) less|(?:amount|transfer) .{0,24}(?:deducted|minus|discounted|short)") and not (cash_out or relevant_top))
        put("transfer_into_account", 98, (bank_in or bank_funding) and not (third_party_in or missing or cash_in) and (ask or h(r"how|from|via|into|fund")))
        put("pending_transfer", 69, not bank_in)
        put("transfer_into_account", 70, bank_in)

    bank_details = h(r"iban|bic|sort code|routing number|account number|bank details|account details|swift(?: code)?")
    put("receiving_money", 102, third_party_in and not (missing or declined or failed or cash_in or
        h(r"i (?:sent|wired|transferred) (?:some |the )?(?:money|funds) to (?:my friend|another person)")))
    put("receiving_money", 99, h(r"(?:can|could) (?:someone|somebody|another person|people|my (?:friend|employer|family)) .{0,32}(?:send|transfer|pay)|"
                              r"(?:can|how do|how can|how will) i (?:receive|get paid|accept payments)|receive (?:money|payments|funds) from") and not (missing or failed or declined))
    put("receiving_money", 93, bank_details and (ask or h(r"where|find|what|which|share")) and not (explicit_top or wrong_destination or declined or failed))
    put("receiving_money", 85, h(r"incoming (?:funds|money|transaction|payment|transfer)") and not missing)
    put("transfer_into_account", 102, bank_details and (bank_funding or h(r"to top up|for (?:topping|funding|loading)|from my (?:other|own|regular|external) (?:bank|account)")))
    put("transfer_into_account", 99, not (cash_in or third_party_in or money_rate or missing) and
        (h(r"(?:fund|load|add funds to) (?:this|my|the) account (?:from|by|via) (?:[a-z]+ ){0,3}bank|"
           r"mov(?:e|ing) .{0,26}from .{0,20}account to .{0,15}account") or bank_transfer and h(r"can i (?:add|load|deposit|fund)|top up via bank|transfer (?:to|into) my account")))
    put("supported_cards_and_currencies", 92, not (card_order or card_get or card_usage or digital_wallet) and
        h(r"which (?:credit |debit |payment )?cards (?:do you accept|are supported|can i use)|"
          r"what (?:types? of )?(?:credit |debit |payment )?cards (?:do you (?:support|accept)|are supported|can i use)|"
          r"supported cards|accept (?:amex|american express|maestro)|(?:cards? and currencies|currencies and cards)"))
    return scores


def received_currency_context(s):
    return _pattern(r"receiv(?:e|ing) (?:payments?|money|funds|transfers?)|someone (?:can |will )?(?:send|pay)|get paid").search(s) is not None


def _lexical_scores(s):
    features = _terms(s).intersection(_WEIGHTS)
    if not features:
        return {}
    mass = sum(_WEIGHTS[w] for w in features)
    best = {}
    for label, other, other_mass in _PROTOTYPES:
        common = features.intersection(other)
        if common:
            overlap = sum(_WEIGHTS[w] for w in common)
            similarity = (1.85 * overlap / (mass + other_mass) +
                          0.15 * overlap / other_mass)
            if similarity > best.get(label, 0.0):
                best[label] = similarity
    return best


def predict(state) -> dict:
    if not isinstance(state, str):
        return {"answer": "pending_card_payment"}
    s = _normalise(state)
    exact = _EXAMPLES.get(s) or _TITLES.get(s)
    if exact:
        return {"answer": exact}
    scores = _rule_scores(s)
    if scores:
        ranked = sorted(scores, key=scores.get, reverse=True)
        leader = ranked[0]
        high = scores[leader]
        if high >= 91 and (len(ranked) == 1 or high - scores[ranked[1]] >= 8):
            return {"answer": leader}
    else:
        high = 0
        leader = "pending_card_payment"
    lexical = _lexical_scores(s)
    if high >= 88:
        candidates = [k for k in scores if scores[k] >= high - 7]
        answer = max(candidates, key=lambda k: scores[k] + 13.0 * lexical.get(k, 0.0))
    elif high:
        answer = max(set(scores).union(lexical), key=lambda k: (
            scores.get(k, 38) + 47.0 * lexical.get(k, 0.0), k == leader, k))
    elif lexical:
        answer = max(lexical, key=lambda k: (lexical[k], k))
    else:
        answer = leader
    return {"answer": answer}