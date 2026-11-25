import math
import re
import unicodedata
from collections import Counter
from functools import lru_cache


PHRASES = {
    "activate_my_card": """
        activate my card | card activation | enable my new card | where is the activation button |
        how do i start using the card i just received | my card is not activated | activate replacement card
    """,
    "age_limit": """
        minimum age to open an account | can my child get an account | can i sign up if i am 17 |
        is there an age restriction | how old do i have to be | account for a minor | maximum age
    """,
    "apple_pay_or_google_pay": """
        add my card to apple pay | can i use google pay | connect card to my iphone wallet |
        does this work with gpay | pay with my apple watch | adding my card to google wallet
    """,
    "atm_support": """
        which atms can i use | where can i withdraw cash | find a supported cash machine |
        can i use any atm | can i take money out of an atm abroad | which cashpoints work with the card
    """,
    "automatic_top_up": """
        set up automatic top up | top up automatically when my balance gets low |
        disable auto reload | a recurring top up | change the threshold for automatic replenishment
    """,
    "balance_not_updated_after_bank_transfer": """
        bank transfer into my account is not showing up | wired money but my balance is unchanged |
        i sent money from my other bank and it has not arrived | incoming transfer missing from my balance |
        my bank confirmed the transfer to my account but i don't see the money |
        money was taken from my other account but not credited here
    """,
    "balance_not_updated_after_cheque_or_cash_deposit": """
        deposited cash but my balance has not updated | cheque deposit missing |
        my check hasn't cleared | cash deposit didn't show up | paid in a cheque but no money in my account
    """,
    "beneficiary_not_allowed": """
        beneficiary not allowed | this recipient is not supported | not permitted to send to this bank |
        app won't let me add a payee | unable to add beneficiary | can i transfer to a crypto exchange |
        what countries are supported for bank transfers | why can't i send money to this account
    """,
    "cancel_transfer": """
        how can i cancel a transfer | sent money by mistake | undo a bank transfer |
        recall money i sent to the wrong account | stop an outgoing transfer | recover money sent to the wrong person
    """,
    "card_about_to_expire": """
        my card is about to expire | when do i get a replacement for an expiring card |
        what happens when my card expires | renew my debit card | the expiration date is next month
    """,
    "card_acceptance": """
        where can i use my card | can i pay abroad with the card | which merchants accept your card |
        will my card work on this website | can i use the card overseas | is this a prepaid card accepted in shops
    """,
    "card_arrival": """
        my card hasn't arrived | where is my card | track my card order | when will my new card get here |
        i am still waiting on my card | card shipped but not delivered | can you check the status of my card delivery |
        my card is late | did you send my card yet | my card was supposed to arrive yesterday
    """,
    "card_delivery_estimate": """
        what is the estimated delivery time for a card | how long does it take for a new card to arrive |
        can i get express shipping | how quickly can you ship a card | how many days for card delivery |
        if i order today when will a card arrive | can i get my card in two days | overnight card delivery
    """,
    "card_linking": """
        link my card to the account | how do i add my new card to the app | associate an existing card |
        i have a card already and want to connect it | link a replacement card | unlink old card from app
    """,
    "card_not_working": """
        my card does not work | physical card stopped working | the chip on my card is damaged |
        my card won't swipe | none of the terminals will read my card | my debit card isn't usable
    """,
    "card_payment_fee_charged": """
        why was i charged a fee for a card payment | fee for paying with my card |
        extra card purchase fee | surcharge for using my card at a store | are there fees for paying abroad
    """,
    "card_payment_not_recognised": """
        card transaction i do not recognize | i didn't make this purchase |
        someone used my card without permission | unauthorized card payment |
        card payment on my statement that is not mine | dispute an unknown merchant transaction
    """,
    "card_payment_wrong_exchange_rate": """
        wrong exchange rate on my card purchase | used my card abroad and got a bad conversion rate |
        merchant applied the wrong currency rate | why was my purchase converted at this rate
    """,
    "card_swallowed": """
        atm swallowed my card | cash machine ate my card | card retained by the atm |
        card stuck in the cashpoint | the machine didn't give my card back
    """,
    "cash_withdrawal_charge": """
        why did the atm charge me | fee for withdrawing cash | charged extra to take money out |
        are atm withdrawals free | withdrawal surcharge | cash machine commission
    """,
    "cash_withdrawal_not_recognised": """
        cash withdrawal that i don't recognize | i did not take cash out from that atm |
        someone withdrew money without my permission | unauthorized cash machine transaction
    """,
    "change_pin": """
        how do i change my pin | reset card pin | where do i find the pin for my card |
        forgot my atm pin | can i choose a new pin number | how do i see my card pin
    """,
    "compromised_card": """
        i think my card has been compromised | someone knows my card details | card number exposed |
        i entered my card details on a scam website | my card information was stolen | card details leaked
    """,
    "contactless_not_working": """
        contactless payment isn't working | my card won't tap | tap to pay stopped working |
        chip and pin works but i can't use contactless | nfc payment doesn't work
    """,
    "country_support": """
        is your service available in my country | can i open an account as a resident of canada |
        which countries can sign up | do you support usa residents | i live overseas can i register |
        can someone from brazil get an account | eligible countries for opening an account
    """,
    "declined_card_payment": """
        why was my card payment declined | my purchase was rejected | card declined at checkout |
        store won't authorize my payment | online card purchase failed | unable to make a payment with my card
    """,
    "declined_cash_withdrawal": """
        declined cash withdrawal | atm cash request was rejected | can't withdraw cash |
        atm refused to let me take out money | cash machine declined my card | withdrawal failed
    """,
    "declined_transfer": """
        my bank transfer was declined | why did you reject my transfer |
        transfer has been refused by the bank | outgoing transfer shows as declined
    """,
    "direct_debit_payment_not_recognised": """
        unknown direct debit | don't recognize this direct debit payment |
        direct debit i haven't authorized | unfamiliar debit mandate | someone set up a direct debit without my permission
    """,
    "disposable_card_limits": """
        how many disposable cards can i use per day | limit on single use virtual cards |
        can i use my disposable card more than once | restrictions on disposable virtual cards |
        can i use a single use card for a subscription | maximum number of disposable card transactions
    """,
    "edit_personal_details": """
        change my name on the account | update my phone number | edit my personal information |
        change the address on my profile | i moved how do i update my address |
        my email address has changed | correct my date of birth | update my account details
    """,
    "exchange_charge": """
        what is the currency exchange fee | charged for exchanging money |
        is there a fee for exchanging currencies on the weekend | conversion commission | any fees for converting funds
    """,
    "exchange_rate": """
        what is your exchange rate | rate for converting euros to dollars | do you use the interbank rate |
        where can i see today's currency rate | how much is a pound in euros | how is the conversion rate calculated
    """,
    "exchange_via_app": """
        how can i exchange currency in the app | change euros to pounds in my account |
        where do i convert my balance | can i buy foreign currency through the app | how do i sell my dollars for euros
    """,
    "extra_charge_on_statement": """
        extra charge on my statement | why is the amount charged higher than my receipt |
        unexplained additional charge | paid more than the price | charged more than i should have been |
        what is this small extra charge on my account | the amount on the receipt and in the app don't match
    """,
    "failed_transfer": """
        my bank transfer failed | why wasn't the transfer successful |
        keep getting an error when i try to send money | transfer didn't go through |
        unable to make a bank transfer | transfer is showing as failed
    """,
    "fiat_currency_support": """
        which fiat currencies are supported | can i keep a balance in japanese yen |
        what currencies can i hold | can i have a euro account | supported currencies for exchange |
        can i open a balance in swiss francs | what currencies are available in the app
    """,
    "get_disposable_virtual_card": """
        how can i get a disposable virtual card | create a one time use card |
        where is the option for a single use card | do you offer disposable cards | generate a temporary card number
    """,
    "get_physical_card": """
        how do i get a physical card | do you provide a real debit card |
        can i get a plastic card | i have a virtual card and want a physical one |
        do i get a bank card with my account | is a physical card available | how much does a physical card cost
    """,
    "getting_spare_card": """
        can i get a spare card | order a second debit card | have two physical cards |
        can i get an additional card for my partner | i want a backup card | add another card to my account
    """,
    "getting_virtual_card": """
        how do i get a virtual card | create a virtual card in the app |
        where can i find my digital card | do you offer virtual debit cards | get a new electronic card
    """,
    "lost_or_stolen_card": """
        i lost my card | my bank card has been stolen | can't find my card |
        someone stole my wallet with the card inside | report my missing debit card | i misplaced my card
    """,
    "lost_or_stolen_phone": """
        my mobile phone was stolen | i lost my phone | somebody took my iphone |
        how can i access my account after losing my phone | my phone is gone and i can't log in
    """,
    "order_physical_card": """
        i want to order a physical card | where can i order my card |
        how do i place an order for a debit card | send me a physical card |
        order a new card from the app | can i get a card sent to my address
    """,
    "passcode_forgotten": """
        i forgot my passcode | reset the passcode for the app | can't remember my password |
        i don't know the pin to log in | forgot my login code | locked out of the app |
        i forgot my account security code | can't sign in to my account
    """,
    "pending_card_payment": """
        why is my card payment pending | purchase stuck on pending |
        merchant payment still processing | card transaction is on hold | when will the preauthorization be released
    """,
    "pending_cash_withdrawal": """
        my cash withdrawal is pending | atm transaction stuck in processing |
        i withdrew cash and it still shows pending | pending transaction from a cashpoint
    """,
    "pending_top_up": """
        top up pending | card top up stuck on processing | my top up hasn't completed yet |
        why is my deposit awaiting confirmation | i added funds by card but the top up is still pending
    """,
    "pending_transfer": """
        bank transfer is still pending | transfer stuck in processing |
        why is my transfer on hold | transfer still awaiting approval | outgoing payment is queued
    """,
    "pin_blocked": """
        pin blocked | entered the wrong pin too many times | unblock my card pin |
        too many incorrect pin attempts | account says pin tries exceeded | how do i unlock my pin
    """,
    "receiving_money": """
        how do i receive money | can someone send me money | can i receive my salary into this account |
        receive a payment from overseas | get paid by my employer | my friend wants to send money to me |
        can i receive international payments | send a request for money
    """,
    "refund_not_showing_up": """
        merchant issued a refund but i haven't got it | refund not showing in my balance |
        i am still waiting for the refund | how long does it take a refund to appear |
        refunded by the shop but no money in my account | where is my refund
    """,
    "request_refund": """
        how can i request a refund | i want my money back from a merchant |
        get a refund for an item i returned | ask for a chargeback | can i dispute a purchase |
        get a refund for a product that never arrived
    """,
    "reverted_card_payment": """
        card payment reverted | completed card payment was reversed | merchant canceled my card transaction |
        why did the money for a card purchase come back | purchase shows as reverted |
        payment disappeared and my balance went back up | card authorization reversed
    """,
    "supported_cards_and_currencies": """
        which cards can i use to top up | which currencies can i use to add money |
        can i top up with american express | do you support credit cards for adding funds |
        supported cards and currencies for deposits | can i use a prepaid card to add money
    """,
    "terminate_account": """
        close my account | delete my account permanently | terminate my account |
        deactivate my profile | how can i cancel my membership | i don't want to use my account anymore
    """,
    "top_up_by_bank_transfer_charge": """
        is there a fee to top up by bank transfer | why was i charged for adding money by bank transfer |
        charge to fund my account from another bank | fee for a bank transfer into my account
    """,
    "top_up_by_card_charge": """
        cost of topping up by credit card | why was i charged for a card top up |
        surcharge to add money using my debit card | does topping up my balance by card cost anything
    """,
    "top_up_by_cash_or_cheque": """
        can i top up by cash | how to deposit a cheque | can i add money at a cash machine |
        can i pay in a check | where can i deposit banknotes | add cash to my account
    """,
    "top_up_failed": """
        my top up failed | card top up was declined | cannot add funds to my balance |
        error when topping up | deposit by card did not go through | app won't let me top up
    """,
    "top_up_limits": """
        what is the top up limit | how much can i add to my account daily |
        maximum amount i can top up | do you have a minimum deposit amount | how many times can i top up
    """,
    "top_up_reverted": """
        my top up was reverted | funds returned to my original card after a top up |
        my deposit was reversed | topping up worked then the money went back to my bank |
        canceled top up | top up was refunded back to my credit card
    """,
    "topping_up_by_card": """
        how do i top up by card | add money using a debit card | fund my balance with a credit card |
        can i use my husband's card to top up | add a new card for top ups | how can i put money on my card
    """,
    "transaction_charged_twice": """
        charged twice for the same thing | i have two identical transactions |
        same payment is listed two times | duplicate charge | my card was debited twice |
        one purchase but it shows up twice | double billed
    """,
    "transfer_fee_charged": """
        why did i pay a fee for sending money | transfer fee appeared on my statement |
        cost of making a bank transfer | recipient got less money due to a transfer fee |
        are there charges for international transfers | fee to move money to another bank
    """,
    "transfer_into_account": """
        how do i transfer money into my account | add money by bank transfer |
        what are my bank details for transferring funds | move money from my external bank to this account |
        where is my iban | what routing number should i use | fund my account by wire
    """,
    "transfer_not_received_by_recipient": """
        transfer completed but recipient did not receive it | my friend hasn't received the money i sent |
        i sent money but it isn't in their account | beneficiary says funds did not arrive |
        money left my account but hasn't reached the other bank | sent a transfer that never reached its destination
    """,
    "transfer_timing": """
        how long does a bank transfer take | when will a transfer clear |
        what is the estimated arrival time for a transfer | are transfers instant |
        how many business days to send money | do transfers go through on weekends
    """,
    "unable_to_verify_identity": """
        i cannot verify my identity | app doesn't accept my passport |
        identity verification failed | my verification documents were rejected |
        can't upload my id or take a selfie | stuck verifying my identity | my id is not being recognized
    """,
    "verify_my_identity": """
        how do i verify my identity | what documents can i use to verify my account |
        can i use my driving licence as id | how to complete the verification process |
        what kind of photo do i need to submit | how long does identity verification take
    """,
    "verify_source_of_funds": """
        prove the source of my funds | why do you need proof of income |
        verify where my money came from | asked for payslips and bank statements |
        source of wealth check | what can i provide to verify my income
    """,
    "verify_top_up": """
        how do i verify my top up card | where do i find the four digit verification code on my statement |
        confirm the card i topped up with | small verification charge to authenticate top up |
        it says verify my deposit | top up card verification
    """,
    "virtual_card_not_working": """
        my virtual card isn't working | virtual card declined when i tried to pay |
        can't make payments with my digital card | online payment failed with my virtual card
    """,
    "visa_or_mastercard": """
        will my card be visa or mastercard | do you issue visa cards | which card network do you use |
        can i choose mastercard | is my debit card a visa | i want a mastercard instead of visa
    """,
    "why_verify_identity": """
        why do i need to verify my identity | why are you asking for my passport |
        do i have to provide my id | why do you require a selfie | why do you need to know who i am |
        can i use my account without verification | is identity verification mandatory
    """,
    "wrong_amount_of_cash_received": """
        atm gave me less cash than requested | cash machine debited me but gave me no money |
        cash dispensed was incorrect | only got part of my withdrawal | cash did not come out but my balance went down |
        atm gave me the wrong amount | machine did not dispense all of the money
    """,
    "wrong_exchange_rate_for_cash_withdrawal": """
        wrong exchange rate on an atm withdrawal | cash machine converted at the wrong rate |
        why was the foreign cash withdrawal converted at this rate | withdrew cash abroad at a bad exchange rate
    """,
}


def _text(state):
    if isinstance(state, str):
        return state
    if isinstance(state, (list, tuple)):
        if state and all(isinstance(item, str) for item in state):
            return " ".join(state)
        preferred = []
        others = []
        for item in state:
            if isinstance(item, dict):
                role = str(item.get("role", item.get("speaker", ""))).lower()
                if role in ("assistant", "agent", "system", "developer", "bot", "support"):
                    continue
                if role in ("user", "customer", "human", "client"):
                    preferred.append(_text(item))
                    continue
            others.append(_text(item))
        return next((t for t in reversed(preferred or others) if t.strip()), "")
    if isinstance(state, dict):
        fields = {k.lower().replace("-", "_"): v for k, v in state.items() if isinstance(k, str)}
        for key in (
            "utterance", "customer_utterance", "customer_text", "user_text", "text",
            "customer_message", "user_message", "message", "content", "query", "input_text",
            "customer_query", "user_query", "sentence", "customer_question", "question",
            "request", "prompt", "input", "body", "description", "messages", "conversation",
            "state", "data", "example",
        ):
            if key in fields:
                t = _text(fields[key])
                if t.strip():
                    return t
        values = [_text(v) for k, v in fields.items()
                  if k not in ("role", "id", "answer", "label", "intent", "category", "instructions", "type", "speaker")]
        return " ".join(v for v in values if v.strip())
    return ""


def _normalize(text):
    t = unicodedata.normalize("NFKC", text).casefold()
    t = "".join(c for c in unicodedata.normalize("NFKD", t)
                if not unicodedata.combining(c))
    t = t.translate(str.maketrans({"’": "'", "‘": "'", "`": "'", "€": " eur ",
                                  "£": " gbp ", "¥": " yen ", "$": " dollar "}))
    replacements = (
        (r"\bcan['’]?t\b|\bcannot\b", "can not"),
        (r"\bwon['’]?t\b", "will not"),
        (r"\bain['’]?t\b", "is not"),
        (r"\b([a-z]+)n't\b", r"\1 not"),
        (r"\bi'm\b|\bim\b", "i am"),
        (r"\b(i|we|they|you)'ve\b", r"\1 have"),
        (r"\b(i|we|they|you|it)'ll\b", r"\1 will"),
        (r"\b(i|we|they|you)'d\b", r"\1 would"),
        (r"\b(it|that|what|where|there|who)'s\b", r"\1 is"),
        (r"\b(?:dont|didnt|doesnt|hasnt|havent|isnt|wasnt|wont|cant)\b",
         lambda m: {"dont": "do not", "didnt": "did not", "doesnt": "does not",
                    "hasnt": "has not", "havent": "have not", "isnt": "is not",
                    "wasnt": "was not", "wont": "will not", "cant": "can not"}[m[0]]),
        (r"[^a-z0-9]+", " "),
        (r"\btop\s*ups\b|\btopping\s*up\b|\btopped\s*up\b|\btop\s*up\b", "top up"),
        (r"\bauto\s+(?:recharge|reload|replenish)\b|\bauto\s*top\s*up\b", "automatic top up"),
        (r"\bcontact\s+less\b", "contactless"),
        (r"\bmaster\s+card\b", "mastercard"),
        (r"\bpass\s+code\b", "passcode"),
        (r"\brecognis", "recogniz"),
        (r"\bauthoris", "authoriz"),
        (r"\bunauthoris", "unauthoriz"),
        (r"\bunauthorised\b", "unauthorized"),
        (r"\bcancell(ed|ing|ation)\b", r"cancel\1"),
        (r"\bcash\s*points?\b", "atm"),
        (r"\b(?:cash|bank|teller) machines?\b", "atm"),
        (r"\bapplepay\b", "apple pay"),
        (r"\bgooglepay\b|\bgpay\b", "google pay"),
        (r"\bcardholder\b", "card holder"),
        (r"\bbank\s+wire\b", "bank transfer"),
    )
    for p, q in replacements:
        t = re.sub(p, q, t)
    return " ".join(t.split())


@lru_cache(maxsize=768)
def _pattern(p):
    return re.compile(r"\b(?:" + p + r")\b")


STOP = set("""
a an the i me my mine we our ours you your they them their he she his her it its
this that these those there is are am be being been was were do does did done has
have had can could may might will would should shall to of on at from for with in
into by about as and or some any just please help want know tell thanks hello hi
what why how where when which who if get got getting use using make making
""".split())

EQUIVALENTS = {
    "charged": "charge", "charging": "charge", "charges": "charge", "billed": "charge",
    "fees": "fee", "surcharge": "fee", "commission": "fee",
    "withdrawing": "withdraw", "withdrawal": "withdraw", "withdrawals": "withdraw", "withdrew": "withdraw",
    "funds": "money", "funding": "fund", "funded": "fund",
    "transfers": "transfer", "transferred": "transfer", "transferring": "transfer",
    "wire": "transfer", "wired": "transfer", "wiring": "transfer", "remittance": "transfer",
    "paid": "pay", "paying": "pay", "payments": "payment", "purchases": "purchase",
    "cards": "card", "accounts": "account", "atms": "atm",
    "transactions": "transaction", "deposited": "deposit", "deposits": "deposit",
    "currencies": "currency", "rates": "rate", "converting": "convert", "converted": "convert",
    "conversion": "convert", "conversions": "convert", "exchanging": "exchange",
    "expired": "expire", "expiring": "expire", "expires": "expire", "expiration": "expire", "expiry": "expire",
    "rejected": "decline", "declined": "decline", "refused": "decline",
    "reversed": "revert", "reverted": "revert", "reversal": "revert",
    "delivered": "deliver", "delivery": "deliver", "shipping": "ship", "shipped": "ship",
    "arrived": "arrive", "arrival": "arrive", "received": "receive", "receiving": "receive",
    "working": "work", "works": "work", "stopped": "stop",
    "sent": "send", "sending": "send", "added": "add", "adding": "add",
    "authorization": "authorize", "authorized": "authorize", "authorizing": "authorize",
    "verified": "verify", "verification": "verify", "verifying": "verify",
    "activated": "activate", "activation": "activate", "activating": "activate",
    "refunded": "refund", "refunds": "refund",
    "ordered": "order", "ordering": "order", "orders": "order",
    "lost": "lost", "misplaced": "lost", "stolen": "steal", "stole": "steal",
    "limits": "limit", "restricted": "restriction", "restrictions": "restriction",
    "pounds": "gbp", "euros": "eur", "dollars": "dollar", "digital": "virtual",
    "recipient": "beneficiary", "recipients": "beneficiary", "payee": "beneficiary",
    "details": "details", "recognized": "recognize", "recognizing": "recognize",
    "failed": "fail", "failure": "fail", "unsuccessful": "fail",
    "duplicated": "duplicate", "processing": "process", "pending": "pending",
}


def _features(text):
    words = [EQUIVALENTS.get(w, w) for w in text.split() if w not in STOP]
    features = Counter(words)
    features.update(a + " " + b for a, b in zip(words, words[1:]))
    return features


EXACT = {}
_RAW = {}
_DOCS = Counter()
for _label, _phrases in PHRASES.items():
    _lines = [_normalize(x) for x in _phrases.split("|")]
    _lines.append(_normalize(_label))
    for _line in _lines:
        EXACT.setdefault(_line, _label)
    _RAW[_label] = [_features(x) for x in _lines]
    _DOCS.update(set().union(*(x.keys() for x in _RAW[_label])))

_IDF = {w: (1.0 + math.log((len(PHRASES) + 1) / (count + 1))) *
        (1.25 if " " in w else 1.0) for w, count in _DOCS.items()}


def _weighted(features):
    return {w: _IDF[w] * (1.0 + 0.25 * min(2, n - 1))
            for w, n in features.items() if w in _IDF}


_MODELS = {}
for _label, _vectors in _RAW.items():
    _MODELS[_label] = []
    for _featureset in _vectors:
        _vector = _weighted(_featureset)
        _norm = math.sqrt(sum(v * v for v in _vector.values()))
        if _norm:
            _MODELS[_label].append({w: v / _norm for w, v in _vector.items()})


def _lexical(text):
    query = _weighted(_features(text))
    norm = math.sqrt(sum(v * v for v in query.values())) or 1.0
    result = {}
    for label, vectors in _MODELS.items():
        best = second = 0.0
        for vector in vectors:
            value = sum(weight * query.get(word, 0.0) for word, weight in vector.items())
            if value > best:
                best, second = value, best
            elif value > second:
                second = value
        result[label] = (0.85 * best + 0.15 * second) / norm
    return result


def _rules(t):
    def has(p):
        return bool(_pattern(p).search(t))

    scores = {}

    def give(label, score, condition=True):
        if condition and score > scores.get(label, 0):
            scores[label] = score

    def near(a, b, n=7):
        gap = r"(?: [a-z0-9]+){0," + str(n) + r"} "
        return has(r"(?:" + a + r")" + gap + r"(?:" + b + r")|(?:" + b + r")" + gap + r"(?:" + a + r")")

    card = has(r"cards?|debit card|credit card")
    card_payment = has(r"card (?:payment|transaction|purchase)s?|(?:pay|paid|paying|purchase|purchase[d]?) (?:with|using|on|by) (?:my |a |the |your )?(?:debit |credit |virtual )?card")
    cash = has(r"cash|banknotes?|notes|bills|atm[s]?")
    atm = has(r"atms?")
    withdraw = has(r"withdraw(?:al|als|ing|n|s)?|withdrew|cash out|(?:take|took|taking|get|got|pull) (?:some |any |my |the )?(?:money|cash) out|take out (?:some )?(?:cash|money)|(?:get|got|take|took|taking|getting) (?:some )?cash (?:out|from)|dispens(?:e[ds]?|ing)")
    payment = card_payment or has(r"payment[s]?|purchas(?:e[ds]?|ing)|transaction[s]?|paid|checkout|pay(?:s|ing)?|merchant|point of sale")
    explicit_transfer = has(r"transfer(?:s|red|ring)?|wire(?:d|s| transfer)?|wiring|remittance[s]?|sepa|swift transfer|ach")
    send = has(r"send(?:s|ing)?|sent|moved?|moving|paid|pay(?:ing)?")
    transfer = explicit_transfer or (
        not card_payment and not withdraw and
        (has(r"(?:send|sending|sent|move|moving|moved) (?:some |any |the |my )?(?:money|funds|cash)") or
         near(r"send|sending|sent|paying|paid", r"beneficiary|recipient|another (?:bank|account)", 5)))
    top = has(r"top up|reload(?:ed|ing)?|recharg(?:e[ds]?|ing)|add(?:ed|ing)? (?:some |more |any |the )?(?:money|funds|cash)|(?:add|put|load|deposit|putting|depositing) (?:money|funds|cash) (?:on|onto|into|in)|fund(?:ed|ing)? (?:my|the|this|your) (?:account|balance|wallet)|add to my balance")
    deposit = has(r"deposit(?:ed|s|ing)?|paid in|pay in")
    cheque = has(r"cheques?|paper checks?|bank checks?|check deposit|deposit(?:ed|ing)? (?:a |my |the )?check|pay (?:in|by|with) (?:a |my |the )?check|(?:my|the|a) check (?:has|was|is|did|will|cleared)")
    cash_deposit = cheque or (
        has(r"cash deposits?|deposit machine|banknotes?") or
        near(r"deposit(?:ed|ing|s)?|top up|add|adding|added|pay in|paid in|put|load", r"cash|banknotes", 5))
    if not cash_deposit and deposit and cash and atm and not withdraw:
        cash_deposit = True
    withdrawal = withdraw or (atm and not cash_deposit and not deposit and
                               not near(r"link|activate|change|reset|unblock|blocked", r"pin|card", 3))
    direct = has(r"direct debit[s]?|debit mandate|ach debit|autopay mandate")
    virtual = has(r"virtual|digital card|electronic card|online only card|e card|ecard")
    disposable = has(r"disposabl[e]?|single use|one time (?:use|card)|one use|throwaway|temporary (?:virtual )?card|burner card")
    physical = has(r"physical|plastic|tangible|real (?:debit |credit )?card|hard copy")
    fee = has(r"fees?|surcharge[s]?|commission[s]?|cost[s]?|charged extra|extra charge[s]?|additional charge[s]?|service charge[s]?|charged for|charge (?:me |you )?for|charged me for|charges for|is it free|for free|free of charge")
    rate = has(r"exchange rate[s]?|conversion rate[s]?|currency rate[s]?|forex rate[s]?|interbank rate[s]?|fx rate[s]?|rate (?:of exchange|of conversion|for converting)|(?:exchange|conversion) ratio")
    currency = has(r"currenc(?:y|ies)|fiat|forex|fx|usd|eur|gbp|cad|aud|inr|chf|jpy|cny|pln|hkd|aed|s(?:g|e)k|dollars?|euros?|pounds?|yen|rupees?|zloty|francs?|krona|kronor|dirhams?|pesos?|baht|rubles?|yuan|rand|kroner")
    exchange = rate or has(r"currency exchang(?:e|ing)|foreign exchange|convert(?:ed|ing|s)?|conver[st]ion[s]?|exchang(?:e[ds]?|ing) (?:my |some |the |one |between |foreign )?(?:currency|currencies|money|eur|gbp|usd|dollars?|funds|cash|pounds?)|fx")
    abroad = has(r"abroad|overseas|international(?:ly)?|foreign|outside (?:the|my)|another country|different countr(?:y|ies)")
    fee_only = fee and not has(r"exchange rate|conversion rate|converted at|exchange was|rate used|exchange rate used")
    declined = has(r"declin(?:e[ds]?|ing)|reject(?:ed|s|ion)?|refus(?:e[ds]?|ing)|denied|not (?:being )?(?:accepted|authorized|approved|honored)|disallowed")
    failed = has(r"fail(?:ed|ure|s|ing)?|unsuccessful|error[s]?|not (?:\w+ ){0,2}(?:work(?:ing)?|go(?:ing)? through|gone through)|unable|can not|not able|will not (?:let|allow|process)|problem[s]? (?:with|when)|trouble (?:with|trying|using)|does not let")
    pending = has(r"pending|in progress|still (?:being )?(?:processed|processing|under review|queued)|processing (?:for|since|status)|(?:is|says|shows|status) processing|on hold|awaiting (?:confirmation|approval|processing)|pre ?authori[sz]ation|pre authorized|not yet (?:completed|processed|settled)|stuck (?:on|in|at)")
    reverted = has(r"revert(?:ed|s|ing)?|revers(?:al|e[ds]?|ing)|void(?:ed)?|rolled back|(?:money|funds|amount|payment|charge) (?:was |got |has been )?(?:returned|credited back|sent back)|money (?:went|came) back|refunded back|was canceled|got canceled|has been canceled|bounce[ds]? back")
    duplicate = has(r"twice|thrice|three times|two times|double (?:charge[d]?|transaction|payment|debit|billed)|duplicat(?:ed?|ion)|(?:same|identical) (?:charge|transaction|payment|purchase)s? (?:twice|two|more than once)|charged (?:me )?(?:two|2) times|one purchase (?:but|and) (?:two|2)|(?:two|2) (?:charges|transactions|payments) for (?:the )?(?:same|one)")
    unauthorized = has(r"unauthorized|fraud(?:ulent)?|unfamiliar|unknown|unrecognized|unrecognizable|do not (?:even )?(?:recognize|recall|remember)|(?:not|never) (?:recogniz\w+|authoriz\w+)|did not (?:\w+ ){0,2}(?:make|do|pay|withdraw|buy|spend|authoriz\w+|take out|use)|never (?:\w+ ){0,2}(?:made|bought|paid|withdrew|purchased|authorized)|not (?:me|mine|my (?:purchase|transaction|payment|withdrawal))|without (?:my |any )?(?:permission|authorization|consent)|someone (?:else )?used my card|not know what (?:this|the) (?:payment|transaction|purchase|charge) is")
    missing = has(r"(?:(?:is|has|have|had|was|do|does|did|were|are|can|could) )?not (?:\w+ ){0,3}(?:arriv(?:e|ed|ing)|receiv(?:e|ed|ing)|show(?:n|s|ing)?|appear(?:ed|ing)?|reflect(?:ed|ing)?|credit(?:ed)?|reach(?:ed)?|deliver(?:ed)?|updated)|never (?:\w+ ){0,2}(?:arriv\w+|receiv\w+|got|reach\w+|show\w+|credit\w+)|missing|still waiting|nowhere (?:to be seen|in)|no sign|no (?:money|funds|deposit|credit) (?:in|on|yet)|balance (?:is )?(?:unchanged|the same)|balance (?:has |did )?not (?:changed?|updated?|gone up)|do not see (?:it|the|my|any)|have not got|did not get|yet to (?:receive|arrive|reach|show)|not in (?:my|his|her|their|the) (?:bank|account|balance)|overdue")
    timing = has(r"how (?:much time|long|many (?:business |working )?(?:days|hours|weeks))|when (?:will|would|should|can|do|does|to|is|am)|time ?(?:frame|scale|line)|turnaround|how (?:fast|quickly|soon)|estimate[d]?|what time|take(?:s)? to (?:arrive|show|clear|complete|process|deliver)|instant(?:ly)?|same day")
    wrong = has(r"wrong|incorrect|inaccurate|bad rate|different rate|terrible rate|lower rate|higher rate|unexpected|unfair|poor rate|(?:less|more|different|higher|lower) than (?:i |it |the )?(?:expected|quoted|agreed|advertised)|not (?:the same|correct|right|accurate)|does not match|discrepancy")
    limit = has(r"limit(?:ed|s|ation|ations)?|restrict(?:ed|ion|ions)?|max(?:imum)?|min(?:imum)?|threshold|cap|ceiling|how (?:many|much)|(?:once|twice|uses) per|how often")
    how = has(r"how (?:do|can|could|should|to|would)|what (?:do|should) i (?:do|provide|need)|where (?:do|can|is|to)")
    supported = has(r"support(?:ed|s)?|accept(?:ed|s)?|allow(?:ed|s)?|eligib(?:le|ility)|compatib(?:le|ility)|available|which|what (?:type|kind|sort|countries|currencies|cards)|can (?:i|we|you)|is it possible")
    inbound = has(r"(?:into|in to|to) (?:my|this|the|your|our) (?:\w+ ){0,2}(?:account|balance|wallet)|incoming|inbound|from (?:my |the )?(?:other|external|own|another) (?:bank|account)|to me|(?:receive|received|receiving) (?:a |the |an |any )?(?:payment|transfer|money|funds)")
    outbound = has(r"outgoing|outbound|from (?:this|the app|here)|from my (?:account|balance|wallet) to|to (?:him|her|them|my (?:friend|wife|husband|son|daughter)|another (?:bank|account)|a (?:friend|recipient)|someone else)")
    recipient = has(r"recipient[s]?|beneficiar(?:y|ies)|payee[s]?|receiving (?:bank|account|end)|other (?:end|person|party)|destination account")
    credited = has(r"debited|deducted|charged|took (?:the |my )?money|taken (?:out|from)|left my account|came out of|balance (?:went down|decreased)|(?:account|balance) (?:has been |was )?charged")
    self_fund = top or has(r"from my (?:other |external |own )?(?:bank|checking|savings|credit union)|my other account|from another bank|fund my account")
    actually_done = has(r"deposited|paid in|i (?:have |already )?(?:sent|made|put|added|wired|transferred)|was (?:sent|deposited|paid|completed|processed)|confirmed|completed|cleared|left my|deducted|debited|took my|still waiting|did not go|not showing|not updated")
    order = has(r"order(?:ed|ing)?|requested|placed (?:an |my )?order")
    card_shipping = has(r"deliver(?:ed|y|ies|ing)?|shipp(?:ed|ing)|ship|dispatch(?:ed)?|mail(?:ed|ing)?|post(?:ed|age)|arriv(?:e[ds]?|ing|al)|track(?:ed|ing)?|send out|sent out|on (?:its|the) way|come in|get here")
    before_order = has(r"if i (?:order|request|get|apply)|before (?:i |placing )(?:order|order\w+|apply)|once i (?:order|apply)|after (?:i order|ordering)|from (?:placing )?(?:the )?order|would it take")
    explicit_status = has(r"shows? (?:as |up as )?(?:failed|declined|pending|reverted|processing)|says (?:failed|declined|pending|reverted|processing)|marked (?:as )?(?:failed|declined|pending|reverted)|status (?:is |says )?(?:pending|failed|declined|reverted|processing)")

    # Card ownership, security, and delivery.
    pin = has(r"pin[s]?|personal identification number")
    login = has(r"log ?in|log ?on|sign in|access (?:to )?(?:the |my )?(?:app|account)|app (?:code|pin|passcode|login)|account (?:login|passcode|password)|unlock (?:the |my )?app")
    passcode = has(r"passcode[s]?|password[s]?|login code|access code|security code (?:for|to) (?:the |my )?(?:app|account)")
    old_secret = has(r"forgot(?:ten)?|do not (?:recall|remember|know)|can not remember|reset|recover|locked out|lost|wrong|incorrect")
    blocked = has(r"block(?:ed|ing)?|lock(?:ed|ing)?|unblock(?:ed|ing)?|unlock(?:ed|ing)?|too many|(?:tries|attempts) exceeded|exceeded (?:my |the )?attempts")
    give("passcode_forgotten", 18, passcode and (old_secret or login))
    give("passcode_forgotten", 12, passcode)
    give("passcode_forgotten", 13, login and (failed or old_secret or pin))
    give("passcode_forgotten", 19, pin and login and not has(r"card pin|atm pin"))
    give("pin_blocked", 23, pin and blocked and not (login and not card and not atm))
    give("pin_blocked", 24, pin and has(r"(?:wrong|incorrect) pin (?:three|3|multiple|too many|several)|pin (?:tries|attempts|retry)"))
    give("change_pin", 16, pin and not login and (old_secret or how or
          has(r"change|choose|find|view|see|set|new|locate|modify|where")))
    give("change_pin", 7, pin and not login)
    swallowed = has(r"swallow(?:ed|s|ing)?|ate|eaten|kept|retained|held on to|trapped|stuck (?:in|inside)|did not (?:\w+ ){0,2}(?:return|give back|give me back|release|eject)|will not (?:return|give back|release|eject)")
    give("card_swallowed", 26, atm and swallowed and (card or not has(r"deposit|cash (?:is )?stuck")))
    give("card_swallowed", 22, card and has(r"card (?:was |is |got |has been )?(?:swallowed|eaten|retained|stuck in)"))
    activate = has(r"activat(?:e[ds]?|ion|ing)|unactivated|enable (?:the |my |this |a )?card")
    give("activate_my_card", 19, activate and (card or not has(r"account|app|profile")))
    give("activate_my_card", 17, card and has(r"start using|first time using|ready to use|make (?:the |my )?card active"))
    expiry = has(r"expir(?:e[ds]?|y|ation|ing)|valid until|renew(?:al|ing)?|validity")
    give("card_about_to_expire", 22, card and expiry and
         not has(r"(?:where|how) (?:is|do i find|can i see) (?:the |my )?(?:expiry|expiration)|(?:top up|added money) with (?:an |my )?expired"))
    give("card_about_to_expire", 16, expiry and has(r"replace(?:ment)?|new card|renew"))
    phone = has(r"phone[s]?|mobile[s]?|iphone|handset|android device|smartphone|cellphone")
    lost = has(r"lost|losing|stol(?:e|en)|theft|misplac(?:e[ds]?|ing)|can not (?:\w+ ){0,2}(?:find|locate)|gone missing|missing (?:card|phone)|no longer have|left (?:it|my (?:card|phone)) (?:in|at|on)")
    exposure = has(r"compromis(?:e[ds]?|ing)|leak(?:ed|s)?|expos(?:e[ds]?|ure)|phish(?:ing)?|scam(?:med)?|hack(?:ed|ing)?|card (?:details|data|number|info(?:rmation)?) (?:were |was |are |is |have been |has been )?(?:stolen|copied|cloned|shared)|someone (?:has|knows|got|took) my card (?:details|info|number)|copied my card")
    give("lost_or_stolen_phone", 24, phone and (near(r"phone|mobile|iphone|handset|smartphone|cellphone", r"lost|stolen|stole|misplaced|missing|broken|destroyed", 5) or
         (lost and not card and not has(r"phone number (?:changed|is wrong)"))))
    give("lost_or_stolen_card", 23, card and lost and not exposure and
         not (card_shipping or has(r"never (?:\w+ ){0,2}(?:arrived|received|got|delivered)|not (?:\w+ ){0,2}(?:arrived|received|got|delivered)")))
    give("lost_or_stolen_card", 10, has(r"freeze (?:my |the )?card|stolen wallet|report (?:a |my )?lost card"))
    give("compromised_card", 24 if not (unauthorized and (payment or withdraw)) else 19,
         exposure and (card or has(r"details|banking|fraud|security")))
    give("compromised_card", 10, card and has(r"security alert|identity theft|card fraud|suspect fraud"))
    give("card_arrival", 23, card and (card_shipping or order) and missing and not before_order)
    give("card_arrival", 21, card and has(r"where (?:is|has) (?:\w+ ){0,4}card|track(?:ing)? (?:\w+ ){0,5}(?:card|delivery|shipment)|card (?:is )?(?:late|overdue)|delivery status|status of (?:my |the )?(?:card|order)|card never came") and not before_order)
    give("card_arrival", 19, card_shipping and has(r"still waiting|not arrived|not delivered|tracking number|where is my (?:order|delivery)"))
    give("card_arrival", 17, card and card_shipping and order and actually_done and not before_order)
    give("card_arrival", 17, card and missing and has(r"(?:received|receive|get|got) (?:my|the|a|any) (?:new |physical |debit |plastic )?card") and not before_order)
    give("card_arrival", 17, card and has(r"when will (?:my|the) (?:new |physical |replacement |debit )?card (?:arrive|come|be delivered|get here|be here)|when will i (?:get|receive) my (?:new |physical |replacement |debit )?card") and not before_order)
    give("card_delivery_estimate", 23, (card or card_shipping) and has(r"(?:express|expedited|priority|overnight|next day|faster|rush|speed up) (?:\w+ ){0,3}(?:delivery|shipping|ship|send|card|postage)|(?:delivery|shipping) options") and not (missing and actually_done))
    give("card_delivery_estimate", 22, card and card_shipping and before_order)
    give("card_delivery_estimate", 19, card and timing and (card_shipping or has(r"take (?:to get|to receive|for (?:my|a|the))|time (?:will it take|to get)|get (?:my |a |the )?card in \d+")))
    give("card_delivery_estimate", 13, card_shipping and timing and not transfer)
    wallet = has(r"apple pay|google pay|iphone wallet|apple wallet|google wallet|android pay|apple watch|samsung (?:pay|wallet)|mobile wallet|pay (?:with|using|via|from) (?:my |the |an? )?(?:iphone|phone|android|smartwatch)")
    give("apple_pay_or_google_pay", 23, wallet)
    contactless = has(r"contactless|tap(?:ping)? (?:to pay|my card|the card|pay|payment)|nfc|wave (?:my |the )?card")
    give("contactless_not_working", 22, contactless and (failed or declined or has(r"stopped|not going|disabled|does not|not letting|does not respond")))
    give("contactless_not_working", 14, contactless)
    give("card_linking", 18, card and not top and not wallet and
         has(r"link(?:ed|ing)?|unlink|pair(?:ing)?|associat(?:e|ed|ing)|connect(?:ed|ing)?|attach(?:ed|ing)?"))
    give("card_linking", 16, card and not top and not wallet and
         near(r"add(?:ed|ing)?|register|set up|attach", r"(?:to|on|in|with) (?:my |the |this )?(?:app|account)|existing card", 5))
    give("getting_spare_card", 22, card and has(r"spare|backup|back up|additional|extra card|second|2nd|multiple cards|two (?:physical |debit |credit )?cards|more than one (?:physical |debit )?card|card for (?:my|a) (?:partner|spouse|wife|husband|friend|family)"))
    give("getting_spare_card", 16, card and has(r"get another (?:physical |debit )?card|add another (?:physical |debit )?card") and not (lost or expiry or top))
    give("disposable_card_limits", 23, disposable and (limit or
         has(r"how (?:does|do) (?:it|they|these|disposable|single use|my disposable)|more than once|multiple (?:payments|times|transactions)|use (?:it|them) again|use (?:for|at|with|on|them for|it for)|subscriptions?|recurring|what (?:are|can i use)|after (?:a |every |each )?(?:payment|purchase|use)")))
    give("get_disposable_virtual_card", 19, disposable)
    give("get_disposable_virtual_card", 21, disposable and has(r"creat(?:e|ing)|generat(?:e|ing)|get (?:a |my )?(?:disposable|single use)|set up|order|where (?:do|can|is)"))
    give("virtual_card_not_working", 23, (virtual or disposable) and (failed or declined) and
         not has(r"can not (?:\w+ ){0,2}(?:create|find|see|get|generate|order|add) (?:a |the |my )?(?:virtual|disposable|digital)"))
    give("getting_virtual_card", 17, virtual and not disposable and not (physical and has(r"(?:want|need|get|order|send) (?:a |the |my )?physical|from virtual to physical")))
    give("get_physical_card", 16, physical and card and not top)
    give("get_physical_card", 18, physical and card and has(r"can i get|how (?:do|can|to) (?:i )?get|do (?:you|i) (?:give|offer|get|provide)|have a physical|cost of|only (?:a )?virtual"))
    give("order_physical_card", 19, card and not (virtual or disposable or missing or card_shipping) and
         (order or has(r"place an order|send me (?:a |the |my )?(?:new |physical |debit )?card|mail me|request (?:a |my )?(?:new |physical )?card")))
    give("order_physical_card", 18, card and order and near(r"send|ship|mail", r"address|to me") and not (missing or timing))
    give("get_physical_card", 11, card and has(r"(?:get|apply for|need|want|obtain|provide) (?:a |my |the )?(?:new |bank |debit |credit |plastic )?card") and not top)
    visa = has(r"visa|mastercard|card network|card scheme")
    give("visa_or_mastercard", 19, visa and not top and
         (card or not has(r"immigration|country|travel visa|tourist visa|residen\w+|live in")))
    give("visa_or_mastercard", 22, visa and not top and has(r"visa or mastercard|mastercard or visa|instead of (?:visa|mastercard)|choose (?:a |between )?(?:visa|mastercard)|(?:is|will) (?:it|my card) (?:be )?(?:visa|mastercard)"))

    # Access to the service and verification.
    identity = has(r"identit(?:y|ies)|kyc|identification|passport[s]?|selfie[s]?|national id|photo id|identity card|driver s licen[cs]e|driving licen[cs]e|(?:my|an|your|the) id|id (?:card|check|document|verification|verification process)|verif(?:y|ying|ication|ied) (?:my |the |this )?(?:account|profile|id|identification)|proof of address")
    verify = has(r"verif(?:y|ying|ication|ied)|validat(?:e|ed|ion|ing)|confirm(?:ation|ing)?|authenticat(?:e|ion|ing)|prov(?:e|ing)")
    necessity = has(r"why (?:\w+ ){0,6}(?:need|require|ask|request|verify|have to|send|upload|provide|give|show|submit)|is (?:it|verification|id) (?:required|necessary|mandatory)|do i (?:really )?(?:have to|need to|need an? |need my)|without (?:verifying|verification|id|(?:an? |my )?passport|identification|a selfie)|mandatory|compulsory|privacy")
    source = has(r"source of (?:my |the |these |your )?(?:funds|money|income|wealth)|where (?:my|the|this|your) (?:money|funds|income) (?:came|comes|is|are) from|proof of (?:income|funds|earnings|salary|wealth)|payslips?|pay slips?|salary slips?|income verification|verify (?:my |the )?(?:source|income|salary)|origin of (?:the |my )?(?:cash|funds|money)")
    give("verify_source_of_funds", 25, source)
    give("unable_to_verify_identity", 24, identity and (failed or declined or
         has(r"not verified|did not pass|would not accept|not accepting|will not accept|can not upload|can not take|stuck|keeps asking|keeps failing|blurry|verification (?:is )?(?:pending|incomplete)|unable to upload")) and
         not has(r"why (?:do|must|should|would) (?:i|you) (?:have to|need to|need|require|provide)"))
    give("why_verify_identity", 22, (identity or has(r"verify myself|send a picture of myself")) and necessity)
    give("verify_my_identity", 17, identity and (verify or how or supported or
         has(r"documents?|photo|picture|proof|selfie|passport|licen[cs]e")))
    give("verify_my_identity", 11, verify and not (top or source or payment or transfer or card))
    give("verify_top_up", 24, verify and (top or has(r"verification (?:charge|code) (?:on|in|from) (?:my |the )?(?:bank |card )?statement|(?:4|four) digit (?:security |verification |confirm\w+ )?code (?:\w+ ){0,6}(?:statement|transaction)|verify (?:my |a |the )?(?:credit |debit |payment )?card|card verification code")) and not identity)
    give("verify_top_up", 18, card and verify and has(r"code|statement|small (?:payment|charge)|confirm ownership"))
    age = has(r"(?:minimum|maximum|min|max|age) (?:age|limit|requirement|restriction)|age (?:do|can|must|to|for)|how old|under ?age|under (?:the age of )?(?:16|17|18|21|eighteen|sixteen)|(?:\d+|sixteen|seventeen|eighteen|nineteen) years old|i am (?:1[0-9]|2[0-1]|sixteen|seventeen|eighteen)|minor[s]?|teen(?:ager|agers)?|child(?:ren)?|(?:my|a) (?:son|daughter|kids?|child) (?:get|open|sign|register|have)")
    give("age_limit", 23, age)
    give("edit_personal_details", 22, has(r"(?:change|edit|update|correct|modify|amend|replace|alter|switch) (?:\w+ ){0,4}(?:personal (?:info(?:rmation)?|details)|address|phone number|mobile number|email|e mail|name|profile|date of birth|dob|account details|contact details|residency|nationality|tax residence)") and
         not has(r"delivery address for (?:this|my) (?:order|card)|recipient details"))
    give("edit_personal_details", 19, has(r"moved house|new phone number|new email address|(?:name|address|email|number) (?:has )?changed|wrong (?:name|email|address|birth date) (?:in|on) my (?:profile|account)"))
    give("terminate_account", 24, has(r"(?:clos(?:e|ing)|delet(?:e|ing)|terminat(?:e|ion|ing)|deactivat(?:e|ion|ing)|cancel(?:ing|lation)?|remov(?:e|ing)|shut down|stop using|get rid of) (?:\w+ ){0,4}(?:account|membership|profile)|(?:account|profile) (?:permanently |fully )?(?:closure|termination|deletion)|do not want (?:to have |to use |to keep )?(?:this |an |my |the )?account") and not has(r"(?:cancel|undo) (?:a |my |the )?(?:bank )?transfer"))
    residence = has(r"countr(?:y|ies)|resident[s]?|residenc(?:e|y)|citizen[s]?|nationality|region[s]?|(?:i|we) (?:am |are )?(?:liv(?:e|ing)|located|based|from)|expat|moved to|non resident")
    join = has(r"sign ?up|regist(?:er|ration)|open(?:ing)? an? account|(?:create|set up|start|get|have) an? account|become a customer|join|use (?:your|this|the) (?:service|app)|operate")
    give("country_support", 22, residence and join and not age)
    give("country_support", 18, residence and not (card_payment or transfer or withdraw or top) and
         has(r"available|support(?:ed)?|eligible|can (?:i|we)|do you (?:work|operate)|which countries|what countries"))
    give("country_support", 17, join and has(r"(?:can|could) i|available|supported") and not (age or identity or currency))

    # Transaction disputes and refunds.
    refund = has(r"refund(?:s|ed|ing)?|charge ?back[s]?|money back|reimburse(?:ment|d)?")
    requested_refund = has(r"(?:request|ask for|claim|apply for|initiate|get) (?:\w+ ){0,3}(?:refund|charge ?back)|i (?:want|need|would like) (?:\w+ ){0,4}(?:refund|money back)|dispute|claim my money")
    issued_refund = has(r"(?:already |was |been |got |they |merchant |store |shop |seller )refunded|(?:sent|issued|processed|made|approved|promised|expecting|received|waiting for) (?:me |my |a |the |an )?refund|refund (?:was |has been )?(?:sent|issued|processed|approved|due|pending)|where is (?:my|the) refund")
    give("refund_not_showing_up", 23, refund and (missing or (issued_refund and (timing or pending))) and
         not has(r"(?:item|product|parcel|package|goods|order) (?:has |was |is |did )?not (?:been )?(?:arrived?|deliver\w+|received)|refund (?:because|for an? (?:item|product|order))"))
    give("refund_not_showing_up", 19, refund and (issued_refund or (timing and not requested_refund)) and not (top and reverted))
    give("request_refund", 17, refund or has(r"dispute (?:a|the|this) (?:purchase|payment|transaction|charge)"))
    give("request_refund", 20, requested_refund and not (unauthorized or duplicate or issued_refund))
    cancel_transfer = has(r"cancel(?:ed|ing|lation)?|stop|recall|undo|reverse|take back|abort|revoke|retract|recover|retrieve|withdraw (?:the |my )?transfer")
    transfer_error = has(r"by (?:mistake|accident)|accidental(?:ly)?|wrong (?:bank|account|person|details|recipient|beneficiary|iban|sort code|amount)|meant to send|typed (?:\w+ ){0,2}wrong")
    give("cancel_transfer", 25, transfer and (transfer_error or
         (cancel_transfer and (how or has(r"can|want|need|please|let me|possible|should|would like|help")))) and
         not has(r"why (?:\w+ ){0,4}(?:was |got |been )(?:cancel|revers)"))
    give("cancel_transfer", 18, transfer and has(r"cancel (?:this |the |my |a )?(?:bank |pending )?transfer|recall (?:the |my |a )?transfer"))
    give("transaction_charged_twice", 26, duplicate and
         (payment or credited or card or top or has(r"charge[s]?|debit(?:ed)?|billed|bill|statement")) and
         not (disposable and not has(r"charged|billed|deducted|duplicate|debited")))
    give("direct_debit_payment_not_recognised", 26, direct and unauthorized)
    give("direct_debit_payment_not_recognised", 11, direct)
    give("cash_withdrawal_not_recognised", 25, withdrawal and unauthorized and
         not has(r"did not (?:get|receive) (?:any |the |my )?(?:cash|money)|did not (?:give|dispense|release)"))
    give("card_payment_not_recognised", 24, unauthorized and not direct and not (withdrawal and not card_payment) and
         (card_payment or payment or credited or has(r"charge[s]?|bill|statement")) and
         not has(r"did not make it|did not pay (?:any|a) (?:fee|charge)"))
    give("card_payment_not_recognised", 15, has(r"what is (?:this|the) (?:payment|transaction|charge)|something (?:on|in) my statement") and not fee)

    # ATMs, withdrawals, and exchange rates applied to transactions.
    cash_short = has(r"(?:wrong|incorrect|different|less|more|fewer|partial|short) (?:\w+ ){0,2}(?:amount|cash|notes|money)|(?:only|just) (?:gave|dispensed|received|got) (?:part|half|\d+)|(?:got|gave me|dispensed|received) (?:only |just )?(?:part|half|less|nothing)|ate my money|kept the cash|not (?:\w+ ){0,2}(?:give|dispense|release) (?:me |any |the )?(?:cash|money|notes|anything)|no (?:cash|money|notes) (?:came|was dispensed)|received no (?:cash|money)|not (?:get|receive) (?:any |the |my )?(?:cash|money)|cash (?:did not|never) come out|no cash but|dispensed (?:no|less|too little)|(?:paid|took out|requested) \d+ (?:\w+ ){0,4}but (?:got|only|received)")
    cash_zero = has(r"not (?:get|receive) (?:any |the |my )?(?:cash|money)|not (?:\w+ ){0,2}(?:give|dispense|release)|no (?:cash|money)|nothing|never (?:got|came)")
    give("wrong_amount_of_cash_received", 23, withdrawal and cash_short and
         not ((pending or declined) and cash_zero and not credited) and
         not (unauthorized and not credited) and not (fee and not credited and not has(r"dispens|got|gave")))
    give("pending_cash_withdrawal", 24 if explicit_status else 22, withdrawal and pending and not cash_deposit)
    give("declined_cash_withdrawal", 21, withdrawal and (declined or failed) and not cash_deposit and
         not (supported and not atm and has(r"where|which|any|can i|am i able") and not has(r"can not|unable|failed|declined|reject")))
    give("declined_cash_withdrawal", 17, withdrawal and cash_zero and not credited and not cash_short)
    give("cash_withdrawal_charge", 22, withdrawal and fee_only and not cash_deposit)
    give("wrong_exchange_rate_for_cash_withdrawal", 24, withdrawal and
         (rate or (exchange and (wrong or abroad))) and not (fee_only or cash_deposit))
    give("atm_support", 13, withdrawal and not cash_deposit)
    give("atm_support", 18, withdrawal and supported and
         has(r"which|what|where|any atm|can i use|nearest|find|locat|abroad|overseas|network"))
    rate_on_payment = card_payment or (payment and has(r"merchant|bought|purchase|shop|store|paid|checkout|booked|hotel"))
    give("card_payment_wrong_exchange_rate", 24, rate_on_payment and not withdrawal and not top and
         (rate or (exchange and (wrong or abroad or currency))) and not fee_only)
    give("card_payment_wrong_exchange_rate", 18, card and rate and not (top or withdrawal or transfer or fee_only))
    give("card_payment_fee_charged", 21, fee_only and not (top or withdrawal or transfer or refund) and
         (card_payment or near(r"fee[s]?|charged extra|surcharge|commission|charge for", r"pay(?:ment|ing)?|paid|card|purchase|merchant|store|checkout", 5)))
    extra = has(r"extra charge[s]?|additional charge[s]?|charged (?:me )?(?:extra|more|too much|a different|the wrong)|overcharg(?:e[ds]?|ing)|higher amount|different amount|amount (?:is )?(?:higher|different|wrong)|more than (?:the|i|what)|receipt (?:does not|did not|is different)|amount (?:does not|did not) match|small charge[s]?|separate charge|unexpected charge|charge (?:on|in) my statement")
    give("extra_charge_on_statement", 18, extra and not (duplicate or withdrawal or top or
         (exchange and (currency or rate)) or unauthorized))
    give("extra_charge_on_statement", 23, (payment or credited or has(r"receipt|statement")) and
         has(r"charged (?:me )?(?:too much|more than|the wrong amount|a higher amount)|amount (?:\w+ ){0,3}(?:higher than|does not match) (?:\w+ ){0,4}(?:receipt|bill|price)|different (?:\w+ ){0,2}amount (?:on|than)|(?:amount|price) (?:on|in) (?:my |the )?receipt") and
         not (exchange or rate or withdrawal or duplicate or unauthorized))
    give("pending_card_payment", 21, pending and not (transfer or top or withdrawal or refund) and (payment or card or credited))
    give("pending_card_payment", 23, pending and card_payment and not (top or withdrawal))
    give("reverted_card_payment", 23, reverted and not (transfer or top or withdrawal) and
         (card_payment or (payment and not issued_refund) or has(r"reverted|reversal")))
    give("declined_card_payment", 22 if declined else 19, (declined or failed) and (card_payment or payment or (card and declined)) and
         not (top or withdrawal or transfer or direct or refund or (pending and not declined)))
    give("card_not_working", 16, card and failed and not (card_shipping or lost))
    give("card_not_working", 20, card and
         has(r"chip|magnetic strip[e]?|damag(?:ed|e)|bent|broken|cracked|not readable|unreadable|not (?:\w+ ){0,2}read(?:ing)?|stopped working|will not swipe") and
         not (contactless or atm or pin and blocked))
    give("card_not_working", 19, card and has(r"card (?:is |has )?(?:not working|stopped working|will not work|does not work)") and not (payment or withdraw or top))
    give("card_acceptance", 17, card and not (top or withdrawal or declined or contactless) and
         has(r"accept(?:s|ed|ance)?|where (?:do|can|could)|everywhere|anywhere|merchants?|places|retailers?|stores?|shops?|will (?:my|a|the) (?:\w+ ){0,3}card work|can i (?:pay|use|buy)|use (?:\w+ ){0,3}card (?:in|at|on|abroad|overseas)"))
    give("card_acceptance", 19, (card or payment) and abroad and supported and not (withdrawal or rate or fee or top or transfer))
    give("card_acceptance", 12, card and payment and not (top or withdraw))

    # Funding an account.
    cash_in_action = cash_deposit and (actually_done or
        has(r"paid (?:by|with) (?:a |my |the )?(?:cheque|check)|put (?:\w+ ){0,5}cash|my (?:cash deposit|check|cheque)") or
        near(r"deposit|cheque|check|cash", r"balance|cleared|clear|credited|went in", 5) and missing)
    give("balance_not_updated_after_cheque_or_cash_deposit", 25, cash_in_action and
         (missing or pending or timing or has(r"not cleared|not clear|has not come|never cleared|balance (?:is )?still")))
    give("top_up_by_cash_or_cheque", 21, cash_deposit and not (cash_in_action and (missing or pending)))
    give("top_up_by_cash_or_cheque", 15, deposit and not withdrawal and has(r"where|how|can i") and not (card or transfer))
    auto = has(r"automatic(?:ally)?|recurr(?:ing|ence)|auto reload|auto recharge|automate|scheduled|every time (?:\w+ ){0,5}(?:low|below)|whenever (?:it|my balance) (?:drops|falls|goes)")
    give("automatic_top_up", 24, top and auto)
    give("automatic_top_up", 20, auto and has(r"balance (?:is |gets |goes |falls )?(?:low|below)|replenish|reload|recharge"))
    top_context = top or (deposit and not (cash_deposit or withdraw))
    by_transfer = explicit_transfer or has(r"via (?:my |the |a )?bank|from my bank account|using (?:my|a) bank account")
    card_fund = card or has(r"amex|american express|visa|mastercard|maestro|prepaid|credit or debit")
    add_compat = has(r"which|what (?:credit|debit|prepaid|bank|type|kind|sort|cards?|currenc)|types? of|list of|supported|accepted|compatible|amex|american express|visa|mastercard|maestro|prepaid|credit or debit|debit or credit")
    give("top_up_reverted", 24, top_context and (reverted or has(r"top up (?:was |is |got )?refund(?:ed)?|(?:top up|deposit) disappeared|top up (?:was )?taken back|back to (?:my |the )?(?:original |debit |credit )?card")))
    give("pending_top_up", 23 if explicit_status else 22, top_context and pending and not cash_deposit)
    give("pending_top_up", 19, top_context and missing and actually_done and not by_transfer and not cash_deposit)
    give("top_up_failed", 22, top_context and (failed or declined) and not (cash_deposit or reverted or (pending and not declined)) and
         not has(r"(?:when|why) can i not (?:use|top up) (?:\w+ ){0,5}(?:amex|prepaid|american express)|not (?:accept|support) (?:\w+ ){0,3}(?:prepaid|amex)"))
    give("top_up_limits", 22, top_context and limit and not (rate or (fee and not has(r"limit|minimum|maximum|cap"))))
    give("top_up_by_bank_transfer_charge", 24, fee and by_transfer and not cash_deposit and
         (top_context or (inbound and not outbound)))
    give("top_up_by_card_charge", 23, fee and top_context and not (by_transfer or cash_deposit) and (card_fund or not currency))
    give("supported_cards_and_currencies", 21, top_context and add_compat and
         (card_fund or currency or has(r"types? of cards|which cards|what cards|which payments")) and
         not (fee or reverted or duplicate or pending))
    give("supported_cards_and_currencies", 20, top_context and currency and supported and not (exchange or fee or missing or pending))
    give("supported_cards_and_currencies", 17, card_fund and has(r"which (?:credit |debit |bank )?cards (?:are|do|can)|do you (?:accept|support) (?:\w+ ){0,2}(?:amex|prepaid cards|american express)|supported cards and currencies") and not (card_payment or virtual))
    give("topping_up_by_card", 17, top_context and card_fund and not (by_transfer or cash_deposit))
    give("topping_up_by_card", 12, top_context and not (by_transfer or cash_deposit))
    give("topping_up_by_card", 18, card_fund and has(r"(?:use|using) (?:someone else s|another person s|my (?:wife|husband|friend) s) (?:\w+ ){0,2}card|(?:change|remove|save|add) (?:a |the |my |another )?(?:credit |debit )?card (?:for|to) top up") and not fee)

    # Bank transfers and incoming money.
    sent_by_other = has(r"(?:someone|somebody|a friend|my (?:friend|employer|boss|wife|husband)|they|he|she) (?:\w+ ){0,3}(?:sent|transferred|wired|paid) (?:\w+ ){0,5}(?:me|to my)|(?:sent|transferred|wired|paid) me (?:some |the |my )?(?:money|funds|cash)|(?:money|payment|transfer) (?:from my|sent to me)")
    recipient_missing = recipient and missing or has(r"(?:he|she|they|my (?:friend|wife|husband|recipient)|the other person|the bank) (?:\w+ ){0,3}(?:not|never) (?:\w+ ){0,3}(?:receiv|got|get|see|arriv)|(?:his|her|their) (?:bank |other )?account|at the other end|has not gone (?:into|to) (?:the other|their|his|her)")
    actual_recipient = has(r"(?:he|she|they|my (?:friend|wife|husband|recipient)|the recipient|the beneficiary) (?:\w+ ){0,3}(?:not|never) (?:\w+ ){0,3}(?:receive[d]?|got|get|see|arrive[d]?)|(?:his|her|their) (?:bank |other )?account|completed (?:but|and)|shows (?:as )?(?:completed|successful)|money left my account")
    not_allowed = has(r"not (?:allowed|permitted|authorized|supported|accepted|eligible)|unsupported|prohibited|blocked|banned|blacklist(?:ed)?|restricted|restriction[s]?|can not (?:add|register|save|create)|will not let me (?:add|register|save|create)|invalid beneficiary|invalid payee")
    specific_destination = has(r"cryptocurrency|crypto(?:currency)? exchange|coinbase|binance|bitcoin|this bank|that bank|this (?:recipient|beneficiary|account)|that (?:recipient|beneficiary|account)|certain (?:banks|countries|accounts)|countries (?:can|do|are) (?:\w+ ){0,4}(?:send|transfer|support)|which (?:banks|countries|destinations)|destination countr(?:y|ies)")
    give("beneficiary_not_allowed", 24, (recipient and (not_allowed or
         near(r"can not|unable|failed|error|will not let", r"add|create|register|save", 4))) or
         (transfer and specific_destination and (not_allowed or failed or supported)))
    give("beneficiary_not_allowed", 19, (transfer or recipient) and
         has(r"(?:unable|can not) to send (?:\w+ ){0,4}(?:recipient|beneficiary)|(?:add|set up|allow|register) (?:a |my |the |new )?(?:beneficiary|recipient|payee)|(?:destination|recipient|beneficiary) (?:is )?not"))
    give("beneficiary_not_allowed", 14, recipient and not (missing or pending or timing))
    incoming_missing = (inbound or sent_by_other or self_fund) and not (outbound or recipient_missing)
    give("balance_not_updated_after_bank_transfer", 24, (explicit_transfer or sent_by_other or by_transfer) and
         missing and incoming_missing and not cash_deposit and not (pending and explicit_status))
    give("balance_not_updated_after_bank_transfer", 22, explicit_transfer and missing and
         has(r"my (?:account|balance) (?:has |is |was |did )?(?:not|unchanged|the same)|from my (?:other |external )?(?:bank|account)|(?:not|never) (?:\w+ ){0,3}credited to me|(?:has|have) not received (?:a |my |the )?(?:bank |incoming )?transfer") and not outbound)
    give("transfer_not_received_by_recipient", 25, transfer and recipient_missing and
         (not pending or actual_recipient) and not sent_by_other and not transfer_error)
    give("transfer_not_received_by_recipient", 23, transfer and missing and
         (outbound or (actually_done and not incoming_missing)) and not pending and not (declined or reverted or transfer_error))
    give("transfer_not_received_by_recipient", 20, transfer and missing and recipient and not transfer_error and
         not has(r"(?:how|when) (?:do|will|does) (?:i|it|the transfer)"))
    give("pending_transfer", 24 if explicit_status else 22, transfer and pending and not cash_deposit)
    give("declined_transfer", 22, transfer and declined and not recipient_missing)
    give("failed_transfer", 21, transfer and (failed or reverted) and
         not (declined or pending or recipient_missing or transfer_error or (missing and incoming_missing)))
    give("failed_transfer", 16, transfer and has(r"having (?:an? )?(?:issue|problem)|something went wrong|can not send|unable to transfer"))
    give("transfer_fee_charged", 22, transfer and fee and not cash_deposit and
         not ((top_context or inbound) and not outbound))
    give("transfer_fee_charged", 23, transfer and fee and
         has(r"(?:recipient|beneficiary) (?:\w+ ){0,4}(?:less|deduct|fee)|intermediary bank|fees? (?:for|on) (?:outgoing|sending)|charged (?:me )?to send"))
    give("transfer_timing", 20, transfer and timing and not (pending or declined or failed or missing or fee or transfer_error))
    give("transfer_timing", 18, transfer and has(r"business days|working days|on (?:weekends?|saturdays?|sundays?|holidays?)|how long|arriv(?:e|al) time") and not pending)
    account_details = has(r"iban|bic|sort code|routing number|account number|bank (?:details|coordinates)|swift code|account details (?:for|to)|deposit instructions")
    give("transfer_into_account", 20, (transfer or top_context) and inbound and (self_fund or not sent_by_other) and
         not (missing or pending or fee or declined or reverted))
    give("transfer_into_account", 21, account_details and not (fee or failed or declined or transfer_error or
         has(r"change|update|edit (?:my |the )?account details")))
    give("transfer_into_account", 20, top_context and by_transfer and not (failed or declined or pending or reverted or missing or fee))
    give("transfer_into_account", 12, explicit_transfer and not (missing or pending or fee or failed or declined or timing))
    receive = has(r"receiv(?:e[ds]?|ing)|be paid|get paid|accept (?:money|payments)|send (?:\w+ ){0,4}to me|send me (?:some |the )?(?:money|funds)|payments? into my account|collect money|request money|inbound|incoming|salary|payroll|wages|direct deposit|employer")
    external_sender = has(r"someone|somebody|another person|a friend|my (?:friend|wife|husband|employer|company|boss)|people|clients?|third part(?:y|ies)|customers?|employer|from (?:overseas|abroad|another country)|salary|payroll|wages|paid into")
    give("receiving_money", 23, receive and external_sender and not (missing or pending or actually_done or account_details or fee or (timing and explicit_transfer)))
    give("receiving_money", 20, receive and not (card_shipping or cash_deposit or card_payment or refund or exchange or
         missing or pending or fee or account_details or self_fund) and
         (inbound or external_sender or has(r"receiv(?:e|ing) (?:any |some )?(?:money|funds|payments)|request money|get paid")))
    give("receiving_money", 16, sent_by_other and not missing)

    # General currency capabilities and exchange.
    hold = has(r"hold(?:ing)?|keep|store|maintain|(?:have|open|create|set up) (?:a |an )?(?:\w+ ){0,3}(?:balance|(?:currency|eur|gbp|usd|dollar|euro) account)|multi currency|multicurrency|fiat|currency balance|different currency accounts")
    give("fiat_currency_support", 21, currency and hold and not (top_context or card_payment or fee or rate or wrong))
    give("fiat_currency_support", 18, currency and
         has(r"(?:what|which|list of|types of|supported|available) (?:\w+ ){0,3}currencies|currencies (?:are )?(?:supported|available)|support (?:\w+ ){0,2}(?:currenc|fiat)|can i (?:hold|keep|store)") and
         not (top_context or rate or fee or withdrawal))
    give("fiat_currency_support", 13, currency and supported and not (top_context or payment or transfer or rate or fee))
    give("exchange_charge", 22, exchange and fee_only and not (withdrawal or rate_on_payment or top_context or transfer))
    give("exchange_rate", 20, rate and not (withdrawal or rate_on_payment or card or fee_only or top_context))
    give("exchange_rate", 17, exchange and has(r"rate|how much (?:is|will|would)|how many (?:eur|gbp|usd|dollars|euros)|interbank|mid market|wholesale|calculated") and
         not (withdrawal or rate_on_payment or fee_only))
    give("exchange_via_app", 19, (exchange or
         (currency and has(r"(?:swap|change|buy|sell) (?:\w+ ){0,3}(?:currency|currencies|eur|gbp|usd|dollars?|euros?|pounds?|yen)|(?:to|for|into) (?:eur|gbp|usd|euros?|pounds?|dollars?)"))) and
         not (withdrawal or rate_on_payment or rate or fee or transfer) and
         (how or currency or has(r"in (?:the |my )?app|exchange money")))
    give("exchange_via_app", 11, exchange and not (rate or fee))
    give("exchange_rate", 12, currency and has(r"rate|worth|value"))
    return scores


def predict(state) -> dict:
    text = _normalize(_text(state))
    if not text:
        return {"answer": "card_not_working"}
    exact = EXACT.get(text)
    if exact is not None:
        return {"answer": exact}
    rules = _rules(text)
    lexical = _lexical(text)
    if rules:
        answer = max(PHRASES, key=lambda name: rules.get(name, 0) + 5.0 * lexical[name])
    else:
        answer = max(PHRASES, key=lexical.get)
        if lexical[answer] == 0:
            answer = "card_not_working"
    return {"answer": answer}