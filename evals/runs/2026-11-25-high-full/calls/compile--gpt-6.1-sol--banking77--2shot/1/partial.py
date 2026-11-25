import re
import math
import unicodedata
from collections import Counter
from functools import lru_cache

_LABELS = """
activate_my_card age_limit apple_pay_or_google_pay atm_support automatic_top_up
balance_not_updated_after_bank_transfer
balance_not_updated_after_cheque_or_cash_deposit beneficiary_not_allowed
cancel_transfer card_about_to_expire card_acceptance card_arrival
card_delivery_estimate card_linking card_not_working card_payment_fee_charged
card_payment_not_recognised card_payment_wrong_exchange_rate card_swallowed
cash_withdrawal_charge cash_withdrawal_not_recognised change_pin compromised_card
contactless_not_working country_support declined_card_payment
declined_cash_withdrawal declined_transfer direct_debit_payment_not_recognised
disposable_card_limits edit_personal_details exchange_charge exchange_rate
exchange_via_app extra_charge_on_statement failed_transfer fiat_currency_support
get_disposable_virtual_card get_physical_card getting_spare_card
getting_virtual_card lost_or_stolen_card lost_or_stolen_phone order_physical_card
passcode_forgotten pending_card_payment pending_cash_withdrawal pending_top_up
pending_transfer pin_blocked receiving_money refund_not_showing_up request_refund
reverted_card_payment supported_cards_and_currencies terminate_account
top_up_by_bank_transfer_charge top_up_by_card_charge top_up_by_cash_or_cheque
top_up_failed top_up_limits top_up_reverted topping_up_by_card
transaction_charged_twice transfer_fee_charged transfer_into_account
transfer_not_received_by_recipient transfer_timing unable_to_verify_identity
verify_my_identity verify_source_of_funds verify_top_up virtual_card_not_working
visa_or_mastercard why_verify_identity wrong_amount_of_cash_received
wrong_exchange_rate_for_cash_withdrawal
""".split()

_LABEL_SET = set(_LABELS)

# These paraphrases also provide a lexical backstop for unusual formulations.
_PHRASES = {
    "activate_my_card": """
        How do I activate my new card|My card needs activation|
        Can I start using the card before activating it|
        Activate a replacement debit card|Where is the activate card button
    """,
    "age_limit": """
        How old must I be to open an account|What is the minimum age|
        Can a child have an account|I am under eighteen|
        Can my teenage daughter get a card|Is there an age restriction
    """,
    "apple_pay_or_google_pay": """
        Add my card to Apple Pay|Does Google Pay work|
        Set up Google Wallet|Use Apple Wallet on my phone|
        My Google Pay transaction failed|Can I pay using my smartwatch
    """,
    "atm_support": """
        Which ATMs can I use|Where can I withdraw cash|
        Find a supported cash machine near me|Is this ATM supported|
        What is the maximum ATM withdrawal amount|Which cashpoints accept the card
    """,
    "automatic_top_up": """
        Set up automatic top up|Disable auto top up|
        My automatic recharge did not work|Change automatic funding settings|
        Automatically add money when the balance is low|Cancel recurring top ups
    """,
    "balance_not_updated_after_bank_transfer": """
        I made a bank transfer but my balance has not changed|
        Incoming bank transfer has not appeared in my account|
        Money sent from my bank has not arrived in Revolut|
        My bank deposit is missing|Transferred funds are not showing in the balance
    """,
    "balance_not_updated_after_cheque_or_cash_deposit": """
        Cash deposit not showing in my balance|
        I paid in a cheque but my account has not been credited|
        Where is the cash I deposited|My check deposit has not appeared|
        Account balance unchanged after depositing cash
    """,
    "beneficiary_not_allowed": """
        Why is this beneficiary not allowed|Cannot add this beneficiary|
        Transfer to this recipient is not permitted|
        Is it possible to transfer to a cryptocurrency exchange|
        Which beneficiaries are restricted|Recipient account is unsupported
    """,
    "cancel_transfer": """
        Can I cancel a bank transfer|Stop a transfer I sent|
        Recall money sent to the wrong account|Reverse my outgoing transfer|
        I want to cancel a scheduled transfer
    """,
    "card_about_to_expire": """
        My card expires soon|What happens when my card expires|
        Will you send a new card before the expiry date|
        Renew my expired card|My card is due to expire
    """,
    "card_acceptance": """
        Where can I use my card|Can I use the card abroad|
        Are cards accepted in shops overseas|Can I pay online using this card|
        Does my card work in other countries|Which merchants accept the card
    """,
    "card_arrival": """
        My card has not arrived|Where is the card I ordered|
        Track my card delivery|Still waiting for my card|
        My card is late|Check the delivery status of my card|
        I ordered a card weeks ago and it is missing
    """,
    "card_delivery_estimate": """
        How long does card delivery take|When will my new card arrive|
        What is the estimated delivery time for a card|
        Can I get express delivery|How quickly can you deliver a card|
        When should I expect to receive my card
    """,
    "card_linking": """
        How do I link a card to my account|Link my existing card to the app|
        My new card is not showing in the app|Associate my card with my account|
        Can I link another card|My card is linked to a different account
    """,
    "card_not_working": """
        My card does not work|My card stopped working|
        I cannot use my card anywhere|There is a problem with my debit card|
        The chip on my card is damaged|My card is broken
    """,
    "card_payment_fee_charged": """
        Why was I charged a fee for a card payment|
        Extra charge for paying by card|Merchant charged a card payment surcharge|
        Are there fees for purchases with my card|
        I paid with my card and was charged more
    """,
    "card_payment_not_recognised": """
        I do not recognise a card payment|Unknown payment on my statement|
        There is a purchase I did not make|An unauthorized card transaction|
        I have never shopped at this merchant|A payment is not mine
    """,
    "card_payment_wrong_exchange_rate": """
        Wrong exchange rate on my card payment|
        Currency conversion for my purchase is incorrect|
        I paid abroad and got a bad exchange rate|
        The exchange rate applied to my card transaction is wrong
    """,
    "card_swallowed": """
        The ATM swallowed my card|Cash machine retained my card|
        My card is stuck inside an ATM|The machine will not return my card|
        The cashpoint kept my debit card
    """,
    "cash_withdrawal_charge": """
        Why was I charged for withdrawing cash|ATM withdrawal fee|
        Is there a fee to take out cash|Extra charge at the cash machine|
        What are the free cash withdrawal limits
    """,
    "cash_withdrawal_not_recognised": """
        I do not recognise a cash withdrawal|An ATM withdrawal I did not make|
        Unauthorized cash withdrawal on my account|
        Someone withdrew cash without my permission
    """,
    "change_pin": """
        How do I change my card PIN|I forgot my card PIN|
        Where can I see my PIN number|Reset my debit card PIN|
        Can I choose a different PIN|Retrieve my four digit card PIN
    """,
    "compromised_card": """
        My card details were stolen|I think my card has been cloned|
        Someone has my card number|My card was compromised|
        I gave my card details to a scammer|Someone may be using a copy of my card
    """,
    "contactless_not_working": """
        Contactless payment is not working|My card will not work when I tap|
        Tap to pay has stopped working|Contactless was declined|
        Why can I not pay by contactless|The contactless chip is broken
    """,
    "country_support": """
        Which countries are supported|Can I open an account in my country|
        I live in the United States can I register|
        Is Revolut available to residents of my country|
        What countries can sign up|Can a non resident open an account
    """,
    "declined_card_payment": """
        My card payment was declined|A purchase was rejected|
        Why was my payment refused at the shop|
        My card transaction was not authorized|My payment did not go through
    """,
    "declined_cash_withdrawal": """
        My cash withdrawal was declined|ATM rejected my withdrawal|
        I cannot withdraw money at the ATM|Cash machine refused my transaction|
        My card is declined when I try to take out cash
    """,
    "declined_transfer": """
        My bank transfer was declined|Why was my transfer rejected|
        The bank refused my outgoing transfer|
        My transfer was not authorized|Transfer declined by recipient bank
    """,
    "direct_debit_payment_not_recognised": """
        I do not recognise this direct debit|
        Unauthorized direct debit payment|An unknown direct debit was taken|
        I did not authorize this direct debit mandate
    """,
    "disposable_card_limits": """
        What are the limits of disposable virtual cards|
        Can a disposable card be used more than once|
        Can I pay subscriptions with a disposable card|
        How many disposable cards can I create|
        What are the restrictions on a single use card|
        How does a disposable virtual card work
    """,
    "edit_personal_details": """
        Change my phone number|Update my home address|
        How do I change my email|Correct my name or birth date|
        Edit my personal details|I moved and need to update my address
    """,
    "exchange_charge": """
        Are there currency exchange fees|Why was I charged for exchanging money|
        Commission on currency conversion|Weekend exchange surcharge|
        What is the free currency exchange limit|How much does exchanging money cost
    """,
    "exchange_rate": """
        What exchange rate do you use|What is the current conversion rate|
        How are foreign exchange rates calculated|
        Is your exchange rate the interbank rate|
        What rate will I get when exchanging pounds to euros
    """,
    "exchange_via_app": """
        How do I exchange currencies in the app|Convert pounds into euros|
        Can I change my dollars to another currency|
        Where is the exchange currency option|How can I buy foreign currency|
        Can I exchange money automatically
    """,
    "extra_charge_on_statement": """
        I was charged an extra dollar|There is a small extra charge on my statement|
        Why was one pound taken from my account|
        A one euro verification charge appeared|
        I have an extra small transaction|Why is there a tiny card authorization charge
    """,
    "failed_transfer": """
        My transfer failed|Why did my bank transfer fail|
        The transfer bounced back|Money transfer was unsuccessful|
        The bank returned my transfer|My transfer did not go through
    """,
    "fiat_currency_support": """
        Which currencies can I hold|What fiat currencies are supported|
        Can I have a dollar balance|Can I hold several currencies in my account|
        Which currencies can I exchange|What currencies are available
    """,
    "get_disposable_virtual_card": """
        How do I get a disposable virtual card|
        Create a single use card|Where can I generate a disposable card|
        I want a disposable card|How can I obtain a throwaway virtual card
    """,
    "get_physical_card": """
        How can I get a physical card|I need a real plastic card|
        Can I have a physical debit card|Where do I get an actual card|
        Get a physical card instead of a virtual card
    """,
    "getting_spare_card": """
        Can I have a spare card|How do I get a second card|
        I want another card for the same account|
        Can I order an extra backup card|How many cards can I have|
        Get a replacement card for a damaged card
    """,
    "getting_virtual_card": """
        How do I get a virtual card|Create an online card|
        Where can I find my virtual card|Can I have a digital debit card|
        How much does a virtual card cost|Set up a virtual card in the app
    """,
    "lost_or_stolen_card": """
        I lost my card|My debit card was stolen|I cannot find my card|
        Freeze my missing card|My wallet was stolen with my card|
        What should I do if my card is lost
    """,
    "lost_or_stolen_phone": """
        I lost my phone|My mobile phone was stolen|
        Someone stole my phone with the app|Cannot access my account after losing my phone|
        What should I do about a missing phone
    """,
    "order_physical_card": """
        How do I order a physical card|I want to order a debit card|
        Where can I order a new plastic card|Order my first physical card|
        I need help ordering a card
    """,
    "passcode_forgotten": """
        I forgot my app passcode|I cannot remember my login password|
        Reset the passcode to access my account|
        I am locked out of the app|Forgot my security code for signing in
    """,
    "pending_card_payment": """
        My card payment is pending|A purchase is still processing|
        Why is my card transaction on hold|
        How long do pending card payments take|
        My payment has not completed|A merchant payment is stuck
    """,
    "pending_cash_withdrawal": """
        My cash withdrawal is pending|ATM transaction is still processing|
        Why is my withdrawal showing as pending|
        My cash withdrawal has not completed
    """,
    "pending_top_up": """
        My top up is pending|Adding money is still processing|
        My card was charged but top up has not arrived|
        How long does a pending top up take|
        The top up amount is not showing in my balance
    """,
    "pending_transfer": """
        My transfer is pending|An outgoing transaction|
        Bank transfer is still processing|My transfer is taking too long|
        Why is my transfer stuck|The outgoing transfer is not complete
    """,
    "pin_blocked": """
        My card PIN is blocked|I entered the wrong PIN too many times|
        Unblock my PIN after three incorrect attempts|
        I exceeded the PIN tries limit|My PIN attempts are exhausted
    """,
    "receiving_money": """
        How can I receive money from someone|Can my friend send me money|
        How do I request money from friends|Can I receive my salary|
        Can someone else pay money into my account|
        Send a payment request link|Can my employer pay me
    """,
    "refund_not_showing_up": """
        My refund has not arrived|I am waiting for a merchant refund|
        How long does a refund take|A refund is missing from my account|
        The merchant refunded me but my balance has not changed|
        Where is the refund I was promised
    """,
    "request_refund": """
        How do I get a refund|I want to dispute a card payment|
        Request a chargeback|Get my money back for a purchase|
        The merchant refuses to refund me|I paid for goods that never arrived
    """,
    "reverted_card_payment": """
        My card payment was reverted|Why was my purchase reversed|
        A completed card payment was returned to my account|
        The merchant reversed my card transaction|
        My card payment automatically reverted
    """,
    "supported_cards_and_currencies": """
        Which cards can I use to top up|Are American Express cards supported|
        Can I add money using a prepaid card|
        Which currencies can I use for a card top up|
        Can I top up with a credit card|Is Maestro supported for adding money
    """,
    "terminate_account": """
        How do I close my account|Delete my account permanently|
        I want to terminate my account|Cancel my membership|
        I no longer want an account|Deactivate my account
    """,
    "top_up_by_bank_transfer_charge": """
        Is there a charge for topping up by bank transfer|
        Incoming bank transfer fee|Fees for adding money from my bank|
        Will I be charged for receiving an international transfer|
        Cost of funding my account by bank transfer
    """,
    "top_up_by_card_charge": """
        Is there a fee for topping up by card|
        I was charged for adding money with a credit card|
        Why is there a card top up surcharge|
        How much does it cost to top up|Are card top ups free
    """,
    "top_up_by_cash_or_cheque": """
        Can I top up with cash|Can I deposit a cheque|
        Where can I pay cash into my account|
        Do you accept check deposits|How do I add cash to my account
    """,
    "top_up_failed": """
        My card top up failed|I cannot add money to my account|
        My top up was declined|Error when topping up|
        Adding money with my card does not work|
        My card was rejected when I tried to top up
    """,
    "top_up_limits": """
        What is my top up limit|Maximum amount I can add|
        Is there a minimum top up|How much can I top up per day|
        Increase my card funding limit|How often can I add money
    """,
    "top_up_reverted": """
        My top up was reverted|The top up money was returned to my bank card|
        Why was my top up reversed|My deposit was refunded|
        A card top up bounced back
    """,
    "topping_up_by_card": """
        How do I top up with a bank card|Add money using my debit card|
        Where do I enter card details to add money|
        How do card top ups work|Can I use a saved card to top up|
        How do I add money to my account
    """,
    "transaction_charged_twice": """
        I was charged twice for one payment|Duplicate card transaction|
        The same purchase appears twice|I paid once but two charges appeared|
        Why was the amount deducted twice|A transaction was double charged
    """,
    "transfer_fee_charged": """
        Why was I charged for a transfer|Are international transfers free|
        Extra fee when sending money|What does a bank transfer cost|
        Recipient received less because of transfer fees|
        Commission for an outgoing transfer
    """,
    "transfer_into_account": """
        How do I transfer money into my account|
        Where can I find my bank account details|
        What is my IBAN and BIC|Add money by bank transfer|
        How can I transfer from my bank account to Revolut|
        Where do I find the sort code and account number
    """,
    "transfer_not_received_by_recipient": """
        The recipient has not received my transfer|
        My friend has not got the money I sent|
        The beneficiary did not receive the payment|
        Transfer completed but the money has not reached the recipient|
        Money I sent to another account is missing
    """,
    "transfer_timing": """
        How long does a bank transfer take|When will a transfer arrive|
        What is the usual international transfer time|
        How many days to send money to another bank|
        Do transfers arrive on weekends|Are bank transfers instant
    """,
    "unable_to_verify_identity": """
        I cannot verify my identity|Identity verification failed|
        The app will not accept my passport|My ID was rejected|
        Verification is stuck pending|Unable to upload my identity documents|
        My selfie verification does not work
    """,
    "verify_my_identity": """
        How do I verify my identity|Which identity documents do I need|
        Can I use my driving licence for verification|
        Where do I upload my passport|How long does identity verification take|
        What documents are accepted for account verification
    """,
    "verify_source_of_funds": """
        How do I verify the source of my funds|
        What proof of income do you need|Documents to show where my money came from|
        Verify my source of wealth|Do you need my payslip or bank statement
    """,
    "verify_top_up": """
        How do I verify my top up card|Where is the card verification code|
        I cannot find the four digit code on my bank statement|
        Verify the debit card used to add money|
        Why do I have to verify a top up
    """,
    "virtual_card_not_working": """
        My virtual card is not working|Virtual card payment was declined|
        I cannot pay with my virtual card|The online card is rejected|
        My digital card stopped working
    """,
    "visa_or_mastercard": """
        Will I receive a Visa or Mastercard|Can I choose Visa instead of Mastercard|
        What card brand do you issue|Why did I get Mastercard and not Visa|
        Can I request a specific card network
    """,
    "why_verify_identity": """
        Why do I need to verify my identity|
        Why do you need my passport|Why is identity verification required|
        Can I use the account without verifying myself|
        Is it mandatory to provide identification|
        Why do I have to send a selfie
    """,
    "wrong_amount_of_cash_received": """
        The ATM gave me the wrong amount of cash|
        My account was charged but the ATM gave no money|
        I received less cash than I requested|
        Cash machine only dispensed part of the money|
        No cash came out but my balance was deducted
    """,
    "wrong_exchange_rate_for_cash_withdrawal": """
        Wrong exchange rate on an ATM withdrawal|
        I withdrew cash abroad and got a poor conversion rate|
        The currency conversion for my cash withdrawal was incorrect|
        Why was the rate on my ATM transaction different
    """,
}


def _extract_text(state):
    if isinstance(state, str):
        return state
    if isinstance(state, dict):
        for key in (
            "text", "utterance", "query", "message", "customer_message",
            "sentence", "input", "content", "state"
        ):
            if key in state:
                value = state[key]
                if isinstance(value, (str, dict, list, tuple)):
                    return _extract_text(value)
        if "messages" in state and isinstance(state["messages"], (list, tuple)):
            messages = state["messages"]
            for item in reversed(messages):
                if isinstance(item, dict) and item.get("role") == "user":
                    return _extract_text(item)
            return _extract_text(messages)
        return " ".join(_extract_text(v) for v in state.values())
    if isinstance(state, (list, tuple)):
        return " ".join(_extract_text(v) for v in state)
    if state is None:
        return ""
    return str(state)


@lru_cache(maxsize=4096)
def _normalize(text):
    text = unicodedata.normalize("NFKC", text).lower()
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")
    replacements = {
        "can't": "cannot", "can not": "cannot", "won't": "will not",
        "shan't": "shall not", "ain't": "is not",
        "i'm": "i am", "i've": "i have", "i'd": "i would",
        "it's": "it is", "that's": "that is", "what's": "what is",
        "where's": "where is", "there's": "there is",
        "how's": "how is", "i'll": "i will",
    }
    for old, new in replacements.items():
        text = re.sub(r"\b" + re.escape(old) + r"\b", new, text)
    text = re.sub(r"n['’]t\b", " not", text)
    text = re.sub(r"\b([a-z]+)['’]ve\b", r"\1 have", text)
    text = re.sub(r"\b([a-z]+)['’]ll\b", r"\1 will", text)
    text = text.replace("_", " ")
    text = re.sub(r"[-‐‑–—/]", " ", text)
    text = re.sub(r"\ba\.?\s*t\.?\s*m\.?\b", "atm", text)
    text = re.sub(r"\b(?:cashpoints?|cash machines?)\b", "atm", text)
    text = re.sub(r"\b(?:topup|topups|top ups|topping up|topped up)\b", "top up", text)
    fixes = {
        "withrawal": "withdrawal", "withdrawl": "withdrawal",
        "withdrawls": "withdrawals", "withdrawel": "withdrawal",
        "recieve": "receive", "recieved": "received",
        "recieving": "receiving", "recipent": "recipient",
        "reciepient": "recipient", "benificiary": "beneficiary",
        "beneficary": "beneficiary", "benficiary": "beneficiary",
        "verfication": "verification", "verfiy": "verify",
        "verfication": "verification", "identitiy": "identity",
        "transacion": "transaction", "transation": "transaction",
        "transfered": "transferred", "canceled": "cancelled",
        "cancelation": "cancellation", "master card": "mastercard",
        "contact less": "contactless", "paypass": "contactless",
        "paywave": "contactless", "gpay": "google pay",
        "g pay": "google pay", "applepay": "apple pay",
        "googlepay": "google pay", "revolute": "revolut",
        "unrecognised": "unrecognized", "recognise": "recognize",
        "recognised": "recognized", "recognising": "recognizing",
        "authorised": "authorized", "unauthorised": "unauthorized",
        "authorisation": "authorization", "cheques": "cheque",
    }
    for old, new in fixes.items():
        text = re.sub(r"\b" + re.escape(old) + r"\b", new, text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


_STOP = set("""
a an the i me my mine we us our ours you your yours he she his her they them
their it its this that these those am is are was were be been being have has
had do does did will would shall should can could may might must please
thanks thank hello hi hey want wanted need needs would like kindly tell
about with of for to from into on in at by as and or but so if then than
there here any some also just really very much because since regarding
revolut account accounts card cards money funds transaction transactions
""".split())

_CANON = {
    "payments": "payment", "paying": "pay", "paid": "pay",
    "purchases": "purchase", "purchased": "purchase", "buying": "purchase",
    "bought": "purchase", "shopping": "purchase", "merchant": "shop",
    "merchants": "shop", "shops": "shop",
    "arriving": "arrive", "arrived": "arrive", "arrival": "arrive",
    "delivery": "deliver", "delivered": "deliver", "delivering": "deliver",
    "receiving": "receive", "received": "receive", "receives": "receive",
    "getting": "get", "got": "get", "obtain": "get",
    "sending": "send", "sent": "send", "transfers": "transfer",
    "transferring": "transfer", "transferred": "transfer",
    "withdraw": "withdrawal", "withdrawing": "withdrawal",
    "withdrew": "withdrawal", "withdrawn": "withdrawal",
    "withdrawals": "withdrawal",
    "declined": "decline", "declining": "decline",
    "rejected": "decline", "reject": "decline", "refused": "decline",
    "failed": "fail", "failing": "fail", "failure": "fail",
    "charged": "charge", "charges": "charge", "charging": "charge",
    "fees": "fee", "commission": "fee", "surcharge": "fee",
    "costs": "cost", "costing": "cost",
    "verification": "verify", "verified": "verify", "verifying": "verify",
    "identification": "identity", "id": "identity",
    "documents": "document", "details": "detail",
    "forgotten": "forget", "forgot": "forget", "remember": "remember",
    "stopped": "stop", "stopping": "stop",
    "blocked": "block", "blocking": "block",
    "working": "work", "works": "work",
    "currencies": "currency", "exchanging": "exchange",
    "exchanged": "exchange", "conversion": "exchange",
    "convert": "exchange", "converting": "exchange",
    "dollars": "dollar", "pounds": "pound", "euros": "euro",
    "supported": "support", "supports": "support",
    "allowed": "allow", "permitted": "allow",
    "changed": "change", "changing": "change",
    "update": "change", "updating": "change", "updated": "change",
    "stolen": "steal", "stole": "steal", "lost": "lose", "losing": "lose",
    "refunds": "refund", "refunded": "refund", "refunding": "refund",
    "reversed": "revert", "reverted": "revert", "returned": "return",
    "cancelled": "cancel", "cancelling": "cancel", "cancellation": "cancel",
    "terminate": "close", "delete": "close", "closing": "close",
    "activated": "activate", "activating": "activate", "activation": "activate",
    "expired": "expire", "expires": "expire", "expiring": "expire",
    "expiry": "expire", "expiration": "expire",
    "automatically": "automatic", "auto": "automatic",
    "virtual": "virtual", "digital": "virtual",
    "plastic": "physical", "real": "physical",
    "spare": "extra", "backup": "extra", "additional": "extra",
    "twice": "duplicate", "double": "duplicate", "duplicated": "duplicate",
    "linked": "link", "linking": "link", "associate": "link",
    "countries": "country", "residents": "resident",
    "unrecognized": "unknown", "unauthorized": "unknown",
    "unfamiliar": "unknown", "recognize": "recognize",
    "minimum": "minimum", "maximum": "maximum", "limits": "limit",
    "phone": "phone", "mobile": "phone",
    "cheques": "cheque", "check": "cheque", "checks": "cheque",
    "deposited": "deposit", "depositing": "deposit", "deposits": "deposit",
    "pending": "pending", "processing": "pending",
    "swallowed": "retain", "retained": "retain", "kept": "retain",
}


def _features(text):
    words = re.findall(r"[a-z0-9]+", _normalize(text))
    words = [_CANON.get(w, w) for w in words if w not in _STOP]
    counts = Counter(words)
    for a, b in zip(words, words[1:]):
        counts[a + ":" + b] += 0.65
    return counts


@lru_cache(maxsize=1)
def _lexical_model():
    raw = {}
    document_frequency = Counter()
    for label in _LABELS:
        phrases = [label.replace("_", " ")]
        phrases.extend(p.strip() for p in _PHRASES.get(label, "").split("|") if p.strip())
        vectors = [_features(p) for p in phrases]
        raw[label] = vectors
        vocabulary = set()
        for vector in vectors:
            vocabulary.update(vector)
        document_frequency.update(vocabulary)
    weights = {
        word: math.log((len(_LABELS) + 1) / (frequency + 1)) + 0.7
        for word, frequency in document_frequency.items()
    }
    model = {}
    for label, vectors in raw.items():
        transformed = []
        for vector in vectors:
            weighted = {w: min(n, 2) * weights[w] for w, n in vector.items()}
            norm = math.sqrt(sum(v * v for v in weighted.values())) or 1.0
            transformed.append((weighted, norm))
        model[label] = transformed
    return weights, model


def _nearest(text, candidates=None):
    weights, model = _lexical_model()
    features = _features(text)
    query = {w: min(n, 2) * weights.get(w, 1.3) for w, n in features.items()}
    norm = math.sqrt(sum(v * v for v in query.values())) or 1.0
    best_label = "card_not_working"
    best_score = -1.0
    for label in candidates if candidates is not None else _LABELS:
        scores = []
        for vector, vector_norm in model[label]:
            dot = sum(value * vector.get(word, 0.0) for word, value in query.items())
            scores.append(dot / (norm * vector_norm))
        scores.sort(reverse=True)
        score = scores[0]
        if len(scores) > 1:
            score += 0.10 * scores[1]
        if len(scores) > 2:
            score += 0.04 * scores[2]
        if score > best_score:
            best_score = score
            best_label = label
    return best_label


def _classify(text):
    stripped = text.strip().lower()
    if stripped in _LABEL_SET:
        return stripped
    t = _normalize(text)
    if t == "i have an outgoing transaction":
        return "pending_transfer"

    def w(pattern):
        return re.search(r"\b(?:" + pattern + r")\b", t) is not None

    card = w(r"cards?|debit|credit|visa|mastercard|plastic")
    phone = w(r"phones?|mobile|smartphone|iphone|android|handset|device")
    atm = w(
        r"atm|withdraw(?:al|als|ing|n|s)?|withdrew|cash out|"
        r"take (?:out )?cash|taking (?:out )?cash|"
        r"(?:get|getting|take|taking) (?:some )?(?:cash|money) out"
    )
    topup = w(
        r"top up|recharg(?:e|ed|ing)|reload(?:ed|ing)?|"
        r"card (?:deposit|funding)|fund(?:ing)? (?:my|the|an?) account"
    )
    adding = w(
        r"(?:add(?:ed|ing)?|load(?:ed|ing)?|put(?:ting)?) "
        r"(?:some |more |extra |any |the |my )?(?:money|funds|cash)|"
        r"(?:add(?:ed|ing)?|load(?:ed|ing)?) (?:to |up )?(?:my |the )?balance"
    )
    topup = topup or adding
    bank_transfer = w(
        r"transfers?|transferred|transferring|wire|wiring|remittance|"
        r"beneficiar(?:y|ies)|recipients?|iban|bic|swift|sort code|"
        r"account number|incoming|outgoing|bank deposit|"
        r"(?:send|sending|sent) (?:some |the |my |a |any )?(?:money|funds)|"
        r"money (?:sent|send|transfer)|direct deposit"
    )
    purchase = w(
        r"payments?|purchases?|merchant|shop(?:ping)?|store|restaurant|"
        r"paid|paying|bought|buy|buying|spent|spending|retailer|checkout|pos"
    )
    declined = w(
        r"declin(?:e|ed|ing)|reject(?:ed|ing|ion)?|refus(?:e|ed|ing)|"
        r"denied|not authori[sz]ed|not approved"
    )
    failure = declined or w(
        r"fail(?:ed|ing|ure)?|unsuccessful|error|errors|"
        r"not (?:working|work|successful|going through)|"
        r"(?:does|did|will|would) not (?:work|go through|let me)|"
        r"cannot|unable|trouble|problem|issues?"
    )
    pending = w(
        r"pending|processing|in progress|on hold|queued|stuck|"
        r"unfinished|incomplete|not (?:yet )?(?:complete|completed|processed)|"
        r"taking (?:so |too |a )?long|taking ages|still going"
    )
    fee = w(
        r"fees?|commission|surcharges?|charges|costs?|costing|"
        r"extra|additional|overcharg(?:e|ed|ing)|free|"
        r"charge for|charged for|charge me|charge to|charge on|"
        r"charged (?:a|an|some|any)|charging for|how much (?:is|does|do|will)"
    )
    strong_fee = w(
        r"fees?|commission|surcharges?|extra|additional|"
        r"overcharg(?:e|ed|ing)|costs?|free|charge for|charged for|charges"
    )
    unknown = w(
        r"unrecognized|unknown|unfamiliar|unauthorized|unapproved|"
        r"not (?:my|mine|me)|not recognize|not remember|not recall|"
        r"(?:do|does|did|have|can) not (?:really )?"
        r"(?:recognize|remember|recall|know|identify)|"
        r"never (?:made|bought|been|used|paid|withdrew|visited|authorized)|"
        r"did not (?:make|buy|pay|withdraw|authorize|do)|"
        r"was not me|no idea|no recollection|without my (?:permission|consent)|"
        r"not sure (?:what|where|who)|fraudulent"
    )
    missing = w(
        r"missing|not (?:yet )?(?:been )?(?:received|arrived|credited|updated|"
        r"showing|shown|appeared|reflected|reached|in my account|in the account)|"
        r"never (?:arrived|received|came|reached)|"
        r"(?:has|have|is|are|was|were|did|does) not.{0,25}"
        r"(?:arrive|receive|reach|show|appear|update|change|come)|"
        r"still waiting|waiting for|where is|where are|not there|"
        r"not get|not got|no sign|no money|nothing.{0,12}(?:account|balance)"
    )
    lost = w(
        r"lost|stolen|stole|misplaced|robbed|missing|"
        r"cannot (?:find|locate)|not know where"
    )
    exchange = w(
        r"exchang(?:e|ed|ing)|conversion|convert(?:ed|ing)?|"
        r"forex|fx|interbank|exchange rates?|conversion rates?"
    )
    rate = w(r"rates?|conversion|converted|exchange")
    wrong_rate = w(
        r"wrong|incorrect|inaccurate|bad|poor|unfair|worse|different|"
        r"not right|discrepancy|miscalculat(?:ed|ion)|"
        r"overcharg(?:e|ed|ing)|less than|lower than|higher than|"
        r"too (?:high|low)|rip off|ripped off"
    )
    incoming = w(
        r"incoming|inbound|receiving|receive a transfer|"
        r"(?:to|into) (?:my|the|this|a) (?:revolut )?account|"
        r"(?:to|into) revolut|from (?:my|another|a|the) bank|"
        r"bank (?:deposit|top up)|deposit into|add money|fund my account"
    )
    outgoing = w(
        r"outgoing|outbound|to (?:another|a different|my other) (?:bank|account)|"
        r"from (?:my )?revolut|sent (?:money )?to|send (?:money )?to"
    )

    # Account access and identity.
    if phone and lost:
        return "lost_or_stolen_phone"

    if w(
        r"source of (?:my |the |your )?(?:funds|income|money|wealth)|"
        r"proof of (?:income|funds|earnings|wealth)|"
        r"where (?:my|the|your) money (?:comes|came) from|"
        r"verify (?:my )?(?:income|salary|funds)|"
        r"payslips?|pay slips?|proof of salary"
    ):
        return "verify_source_of_funds"

    verification = w(
        r"verif(?:y|ied|ication|ying)|validat(?:e|ion)|confirm|"
        r"verification code|security check"
    )
    identity = w(
        r"identity|identification|passport|driving licen[cs]e|driver.?s? licen[cs]e|"
        r"id|selfie|photo id|identity documents?|proof of address|"
        r"residence permit|national id|kyc"
    )
    topup_verification = (
        w(r"(?:four|4) digit|bank statement code|card verification|verify.{0,20}card")
        or (verification and (topup or (card and not identity)))
        or (
            w(r"code") and w(r"statement|bank statement|top up|verification charge")
            and not w(r"login|log in|sms|phone|passcode")
        )
    )
    if topup_verification and not (identity and not topup):
        return "verify_top_up"

    if w(
        r"(?:close|closing|delete|deleting|terminate|terminating|cancel|"
        r"deactivate|shut down|remove) (?:down )?(?:my |the |this |an? )?"
        r"(?:revolut |bank )?account|"
        r"(?:account|membership).{0,16}(?:closure|closed|termination|deleted)|"
        r"no longer (?:want|need).{0,15}account|stop using revolut|leave revolut"
    ):
        return "terminate_account"

    if w(
        r"age limit|minimum age|maximum age|age restriction|how old|"
        r"under ?(?:age|18|eighteen|16|sixteen)|"
        r"(?:child|children|teenager|teenage|minor|son|daughter).{0,35}"
        r"(?:account|card|sign up|register)|"
        r"(?:1[0-7]|seventeen|sixteen|fifteen|fourteen|thirteen) years? old|"
        r"old enough"
    ):
        return "age_limit"

    if identity or (verification and not (topup or card or bank_transfer)):
        if w(
            r"why|what for|reason|necessary|mandatory|compulsory|required|"
            r"have to|need to|without|do i (?:really )?need|"
            r"do you need|you (?:asking|ask|require)|safe to"
        ) and not w(
            r"what (?:documents?|id|identification|proof)|"
            r"which (?:documents?|id)|documents? (?:are |is )?required|"
            r"how (?:do|can|to)|how long"
        ):
            return "why_verify_identity"
        if failure or pending or w(
            r"not accept|not recognized|not clear|keeps asking|"
            r"taking (?:too |so )?long|not (?:been )?verified|"
            r"still (?:not |un)?verified|verification.{0,20}not|"
            r"upload.{0,20}(?:problem|error)|repeatedly|blurry|rejected"
        ):
            return "unable_to_verify_identity"
        return "verify_my_identity"

    if w(r"passcode|password|login code|log in code|app pin|security code") and (
        failure or w(r"forgot|forgotten|forget|reset|lost|remember|change|recover|locked")
    ):
        return "passcode_forgotten"
    if w(r"locked out|cannot log ?in|cannot sign in|forgot.{0,20}(?:login|log in)"):
        return "passcode_forgotten"

    if w(
        r"(?:change|edit|update|correct|amend|replace|changing|updating|wrong|new)"
        r".{0,35}(?:personal details|profile|phone number|telephone number|"
        r"mobile number|email|e mail|address|surname|last name|first name|"
        r"legal name|my name|date of birth|birthday|birth date)|"
        r"(?:phone number|email|e mail|personal details|home address|surname)"
        r".{0,35}(?:change|edit|update|wrong|incorrect)|"
        r"got married|changed my name|moved house|moved to a new address"
    ):
        return "edit_personal_details"

    if w(r"apple pay|google pay|apple wallet|google wallet|android pay|samsung pay|smartwatch"):
        return "apple_pay_or_google_pay"

    if w(r"automatic|automatically|auto|recurring|scheduled") and (
        topup or w(r"recharge|low balance|balance (?:gets|falls|drops)|add money")
    ):
        return "automatic_top_up"

    # Security and highly distinctive card operations.
    if w(r"direct debit|direct debits|directdebit"):
        return "direct_debit_payment_not_recognised"

    if atm and w(
        r"swallow(?:ed)?|retain(?:ed)?|kept|ate|eaten|stuck|"
        r"not (?:give|giving|return|returning).{0,15}card|"
        r"took my card|trapped|confiscated|captured"
    ):
        return "card_swallowed"

    delivery_context = w(
        r"deliver|delivery|arriv(?:e|ed|al|ing)|post|mail|shipment|shipping|"
        r"ordered|order.{0,10}(?:ago|week|day)|tracking|dispatched"
    )
    if (card or w(r"wallet|purse")) and lost and not (
        delivery_context and not w(r"stolen|stole|robbed|lost my|i lost|misplaced")
    ):
        return "lost_or_stolen_card"

    if w(
        r"compromis(?:e|ed)|clon(?:e|ed|ing)|skim(?:med|ming)|"
        r"(?:card|banking) (?:details|number|information).{0,30}"
        r"(?:stolen|stole|leaked|exposed|hacked)|"
        r"(?:someone|somebody|scammer).{0,30}"
        r"(?:has|have|knows|got|copied).{0,20}(?:card|details)|"
        r"(?:gave|shared|entered).{0,35}(?:scammer|scam|phishing|fake website)|"
        r"card security (?:breach|compromised)|someone (?:else )?using my card"
    ):
        return "compromised_card"
    if w(r"hacked|fraud|scam|stolen details") and card and not (
        unknown and purchase
    ):
        return "compromised_card"

    if w(r"\bpin\b|pin number|personal identification number"):
        if w(
            r"block(?:ed)?|unblock|too many|attempt|tries|"
            r"(?:three|3) (?:times|wrong|incorrect)|exceeded|locked"
        ):
            return "pin_blocked"
        return "change_pin"

    if w(r"activat(?:e|ed|ing|ion)") and (card or not w(r"account|auto")):
        return "activate_my_card"

    if w(r"contactless|tap to pay|tap and (?:go|pay)|tapping|touch and pay|pay by tap"):
        return "contactless_not_working"

    if w(r"expir(?:e|ed|es|ing|y|ation)|renew(?:al|ing)?") and (
        card or not bank_transfer
    ):
        return "card_about_to_expire"

    # A small test authorization is not a general purchase or top-up fee.
    small_charge = (
        re.search(r"(?:[$£€]\s*1(?:[.,]0{1,2})?(?!\d)|\b1(?:[.,]00)?\s*[$£€])", t)
        is not None
        or w(r"(?:one|1|a|an) (?:extra )?(?:dollar|pound|euro|quid)")
        or w(
            r"small (?:extra |additional |verification |test )?"
            r"(?:charge|payment|transaction|amount)|"
            r"tiny (?:charge|payment)|test charge|verification charge|"
            r"extra dollar|extra pound|extra euro"
        )
    )
    if small_charge and w(
        r"charg(?:e|ed|es)|deduct(?:ed|ion)?|taken|statement|"
        r"transaction|payment|extra|verification"
    ) and not w(r"per (?:withdrawal|transfer)|withdrawal fee|monthly fee"):
        return "extra_charge_on_statement"

    if w(
        r"twice|duplicate(?:d)?|double (?:charged|charge|payment|transaction)|"
        r"charged double|two charges|two payments for|"
        r"(?:charged|debited|deducted|paid) (?:me )?(?:two|2) times|"
        r"same (?:payment|transaction|purchase).{0,25}(?:two|2|double)|"
        r"(?:two|2) (?:identical|same) (?:transactions|payments)|"
        r"paid once.{0,35}(?:two|twice|double)"
    ) and not w(r"two factor|twice a (?:day|week|month)|two cards"):
        return "transaction_charged_twice"

    if unknown:
        if atm:
            return "cash_withdrawal_not_recognised"
        if purchase or card or w(r"transaction|statement|charged|charge|deducted"):
            return "card_payment_not_recognised"

    # Virtual-card questions have priority over generic card payments.
    virtual = w(r"virtual|digital card|online card|disposable|single use|throwaway")
    disposable = w(r"disposable|single use|throwaway|one time (?:use )?card")
    if virtual:
        if (
            declined or w(r"not work|not working|stopped working|does not work|not accepted")
            or (failure and w(r"pay|payment|purchase|use|using|transaction"))
        ) and not w(r"cannot (?:get|create|order|generate)"):
            return "virtual_card_not_working"
        if disposable:
            creation = w(r"get|create|generate|obtain|order|apply|set up|enable|activate")
            limits = w(
                r"limits?|restrict(?:ed|ions?)?|recurring|subscription|"
                r"how (?:many|often)|maximum|minimum|"
                r"more than once|multiple|reuse|re use|"
                r"what (?:can|are)|how.{0,20}work|where.{0,20}use|"
                r"can i use|can (?:a |the )?disposable|last|valid"
            )
            if limits and not (
                creation and not w(r"how (?:many|often)|limit|restriction")
            ):
                return "disposable_card_limits"
            return "get_disposable_virtual_card"
        if not w(r"physical|plastic|real card") or w(r"get.{0,20}virtual|create.{0,20}virtual"):
            return "getting_virtual_card"

    # Cash and cheque deposits are separate from ATM withdrawals.
    cash_deposit = w(r"cheque|checks?|cash deposit|deposit cash|depositing cash|deposited cash")
    cash_deposit = cash_deposit or (
        w(r"cash") and not atm and w(r"deposit|pay in|paid in|top up|add|adding")
    )
    if cash_deposit and not (w(r"check") and not w(r"deposit|cash|cheque|paid in|top up")):
        actual_deposit = w(r"deposited|paid in|made.{0,15}deposit|cashed")
        if missing or pending or (
            actual_deposit and w(r"balance|credited|not|still|yet|days|week")
        ):
            return "balance_not_updated_after_cheque_or_cash_deposit"
        return "top_up_by_cash_or_cheque"

    # Exchange problems are specific to the channel in which conversion happened.
    if exchange or (rate and w(r"currency|abroad|foreign|atm|purchase")):
        if atm and (wrong_rate or w(r"rate|conversion")) and not (
            strong_fee and not wrong_rate and not w(r"wrong rate|exchange rate")
        ):
            return "wrong_exchange_rate_for_cash_withdrawal"
        if (purchase or card) and not topup and not bank_transfer:
            if wrong_rate or w(r"(?:exchange|conversion) rate.{0,25}(?:payment|purchase)"):
                return "card_payment_wrong_exchange_rate"

    # Top-ups by card, including their verification, restrictions and failures.
    bank_funding = bank_transfer and (
        incoming or w(r"top up.{0,25}(?:bank|transfer)|(?:bank|transfer).{0,25}top up")
    )
    if topup and not bank_funding:
        if w(r"revert(?:ed)?|revers(?:e|ed|al)|refund(?:ed)?|returned|bounced|sent back|gone back"):
            return "top_up_reverted"
        if verification or w(r"verification code|four digit|4 digit"):
            return "verify_top_up"
        if w(
            r"limits?|maximum|minimum|how much|how many|how often|"
            r"largest|smallest|allowed amount|amount.{0,12}allowed|"
            r"daily allowance|per day|per month"
        ) and not (failure and not w(r"limit|maximum|minimum")):
            if not strong_fee or w(r"top up limit|maximum top up|minimum top up"):
                return "top_up_limits"
        if w(
            r"supported|accepted|which cards?|what (?:type|kind|cards?|currencies)|"
            r"american express|amex|maestro|diners|discover|prepaid|"
            r"can i use.{0,20}(?:credit|debit|bank|visa|mastercard)|"
            r"foreign card|foreign currency|different currency"
        ) and not (declined or w(r"failed|not work|error")):
            return "supported_cards_and_currencies"
        if strong_fee or w(r"charge.{0,20}top up|top up.{0,20}charg"):
            return "top_up_by_card_charge"
        if declined or w(
            r"fail(?:ed|ure|ing)?|error|unsuccessful|"
            r"cannot (?:add|top|load|put)|unable to|"
            r"not (?:work|working|go through|successful)|"
            r"does not (?:work|let)|did not (?:work|go through)"
        ):
            return "top_up_failed"
        if pending or missing or w(
            r"(?:charged|debited|deducted|taken).{0,55}(?:but|not|nothing)|"
            r"how long|taking|where.{0,15}(?:top up|money)"
        ):
            return "pending_top_up"
        return "topping_up_by_card"

    # Cash withdrawal problems.
    if atm:
        no_cash = w(
            r"no cash|no money|nothing came out|did not (?:dispense|give|receive|get)|"
            r"not (?:dispense|give|receive|get)|"
            r"(?:less|more|wrong|incorrect|different|partial|part of).{0,20}"
            r"(?:cash|amount|money)|"
            r"(?:cash|amount|money).{0,20}(?:short|wrong|incorrect|missing)|"
            r"only (?:gave|got|received|dispensed)|"
            r"not the (?:full|right|correct) amount|"
            r"debited but|charged but|deducted but|empty handed"
        )
        debited = w(r"charged|debited|deducted|taken|balance.{0,15}(?:down|reduced)|lost")
        if no_cash and (
            debited or not (declined or w(r"cannot withdraw|unable to withdraw"))
        ):
            return "wrong_amount_of_cash_received"
        if strong_fee or w(
            r"charge.{0,25}(?:withdraw|atm|cash)|"
            r"(?:withdrawal|atm).{0,25}charg|"
            r"free withdrawal|withdraw.{0,25}free"
        ):
            return "cash_withdrawal_charge"
        if pending:
            return "pending_cash_withdrawal"
        if declined or failure or w(r"will not (?:dispense|give)|cannot take"):
            return "declined_cash_withdrawal"
        if no_cash:
            return "wrong_amount_of_cash_received"
        if exchange or (rate and wrong_rate):
            return "wrong_exchange_rate_for_cash_withdrawal"
        return "atm_support"

    # Transfers: direction, actual status, and information requests are distinct.
    if bank_transfer:
        if w(
            r"cancel|cancellation|stop|recall|undo|reverse|"
            r"sent.{0,30}(?:wrong|incorrect)|wrong (?:account|recipient|beneficiary)"
        ) and not w(r"cancelled by|was cancelled|has been cancelled|reversed by"):
            return "cancel_transfer"

        restricted_beneficiary = w(
            r"beneficiary.{0,25}(?:not allowed|not permitted|unsupported|blocked|not supported)|"
            r"(?:not allowed|not permitted|unsupported|blocked|not supported).{0,30}"
            r"(?:beneficiary|recipient)|"
            r"cannot (?:add|create|set up).{0,20}(?:beneficiary|recipient)|"
            r"beneficiary not|not possible.{0,25}beneficiary|"
            r"cryptocurrency exchange|crypto exchange|gambling|betting|"
            r"brokerage|supported beneficiar|allowed beneficiar|restricted beneficiar"
        )
        if restricted_beneficiary or (
            w(r"beneficiar(?:y|ies)") and w(r"allow|allowed|permitted|supported|not allow")
        ):
            return "beneficiary_not_allowed"

        if strong_fee or w(r"charged.{0,25}transfer|transfer.{0,25}charg"):
            if incoming and not (
                outgoing and w(r"recipient|beneficiary|sending|sent")
            ):
                return "top_up_by_bank_transfer_charge"
            return "transfer_fee_charged"

        if declined:
            return "declined_transfer"
        if w(
            r"fail(?:ed|ure|ing)?|unsuccessful|bounc(?:e|ed|ing)|"
            r"returned|sent back|revert(?:ed)?|reversed|"
            r"did not go through|not gone through|not successful|"
            r"cancelled by|was cancelled|has been cancelled"
        ):
            return "failed_transfer"

        recipient_missing = (
            w(r"recipient|beneficiary") and missing
        ) or w(
            r"(?:friend|mother|father|brother|sister|wife|husband|person|"
            r"other person|someone|they|he|she).{0,45}"
            r"(?:not received|not get|not got|never received|still waiting|waiting for)|"
            r"(?:sent|transferred).{0,65}(?:not reached|not arrived|not received)|"
            r"completed.{0,45}(?:not received|not arrived|missing)|"
            r"not (?:received|arrived).{0,35}(?:recipient|beneficiary|friend)"
        )
        # Explicit incoming wording beats the generic "sent but not arrived".
        if recipient_missing and not (
            incoming and not outgoing and w(r"my (?:revolut )?(?:account|balance)|into revolut")
        ):
            return "transfer_not_received_by_recipient"

        if incoming and (
            missing or w(r"balance.{0,25}(?:same|unchanged|not)|not.{0,20}balance")
        ):
            return "balance_not_updated_after_bank_transfer"
        if w(r"balance") and w(
            r"not|unchanged|same|missing|update|updated|reflect|appear"
        ) and not outgoing:
            return "balance_not_updated_after_bank_transfer"

        if pending or w(r"taking too long|taking longer|delayed|still waiting"):
            if incoming and missing and not outgoing:
                return "balance_not_updated_after_bank_transfer"
            return "pending_transfer"

        if w(
            r"how long|how soon|how fast|how many (?:days|hours)|"
            r"when (?:will|does|do|should|can)|time (?:does|will|for)|"
            r"transfer (?:time|duration)|instant|weekends?|business days|"
            r"working days|normally take|usually take"
        ):
            return "transfer_timing"

        if missing:
            if outgoing or w(r"recipient|beneficiary|sent"):
                return "transfer_not_received_by_recipient"
            return "balance_not_updated_after_bank_transfer"

        if w(r"iban|bic|swift|sort code|account number|bank details"):
            return "transfer_into_account"
        if w(r"request|someone|somebody|friends?|employer|salary|wages|paycheck|pay cheque") and (
            w(r"receive|receiving|send me|pay me|to me|into my|request")
        ):
            return "receiving_money"
        if incoming or w(
            r"how (?:do|can|to)|make a (?:bank )?transfer|"
            r"transfer money|bank transfer"
        ):
            return "transfer_into_account"
        if w(r"outgoing|outbound|sent|processing"):
            return "pending_transfer"
        return _nearest(t, (
            "transfer_into_account", "receiving_money", "pending_transfer",
            "transfer_timing", "beneficiary_not_allowed", "failed_transfer",
            "transfer_not_received_by_recipient"
        ))

    # Refunds and merchant reversals.
    if w(r"refund|refunds|refunded|chargeback|charge back|dispute|money back|reimbursement"):
        if w(
            r"not (?:yet )?(?:received|arrived|showing|appeared)|"
            r"waiting|pending|missing|where|how long|when|"
            r"already|issued|processed|promised|merchant refunded|"
            r"been refunded|was refunded|has refunded|"
            r"refund.{0,25}(?:not|never)|balance.{0,25}(?:not|unchanged)"
        ):
            return "refund_not_showing_up"
        return "request_refund"
    if w(r"reverted|reversed|reversal|returned to my account") and (
        card or purchase or w(r"payment|transaction")
    ):
        return "reverted_card_payment"
    if w(
        r"goods.{0,25}not arrived|purchase.{0,25}not arrived|"
        r"item.{0,25}never arrived|"
        r"cancel (?:a |my |the )?(?:card )?payment|"
        r"charged for.{0,25}(?:cancelled|not receive)|"
        r"merchant.{0,30}(?:refus|not refund)"
    ):
        return "request_refund"

    # Delivery and physical-card acquisition.
    if card and delivery_context:
        delayed = w(
            r"not arriv|not arrived|never arrived|not received|"
            r"still (?:waiting|not)|late|delayed|overdue|"
            r"track|tracking|status|where is|where are|"
            r"days ago|weeks ago|week ago|month ago|"
            r"ordered.{0,30}ago|delivery date.{0,20}(?:passed|gone)|"
            r"should have arrived|has not come|did not come"
        )
        if delayed:
            return "card_arrival"
        if w(
            r"how long|how soon|how fast|when|estimate|expected|"
            r"express|expedit|quick|faster|delivery time|"
            r"how many days|before|by (?:friday|monday|tuesday|wednesday|thursday|saturday|sunday)"
        ):
            return "card_delivery_estimate"
        if w(r"arriv|arrival|delivery|shipping|shipment|post|mail"):
            return "card_arrival"

    if card and w(
        r"link|linked|linking|associate|connect.{0,20}(?:account|app)|"
        r"not (?:showing|shown|visible|appearing).{0,20}app|"
        r"not (?:in|on) my (?:app|account)|"
        r"add.{0,20}(?:card|existing card).{0,20}(?:app|account)"
    ):
        return "card_linking"

    if card and w(
        r"spare|backup|back up|second|extra|additional|another|"
        r"more than one|multiple|two cards|2 cards|"
        r"how many cards|replacement|replace|damaged"
    ) and not w(r"card payment|extra charge|extra fee|charged extra"):
        if w(r"damaged|broken") and not w(r"replacement|replace|new|another|spare"):
            return "card_not_working"
        return "getting_spare_card"

    # Card brand selection is different from cards accepted for top-ups.
    if w(r"visa|mastercard|card brand|card network") and not topup:
        if w(
            r"visa (?:or|and|instead of|rather than) mastercard|"
            r"mastercard (?:or|and|instead of|rather than) visa|"
            r"choose|choice|prefer|request|issued|issue|which (?:one|card)|"
            r"get a visa|get a mastercard|card brand|card network|"
            r"why.{0,35}(?:visa|mastercard)"
        ):
            return "visa_or_mastercard"

    if w(
        r"american express|amex|maestro|diners|discover|"
        r"supported cards|which cards|what cards|prepaid card|"
        r"credit cards? accepted|debit cards? accepted|"
        r"currencies.{0,25}top up"
    ):
        return "supported_cards_and_currencies"

    # Currency availability precedes generic exchange instructions.
    currency_support = w(
        r"which currencies|what currencies|supported currencies|"
        r"currencies.{0,15}(?:supported|available|hold)|"
        r"(?:hold|holding|keep|store|balance|balances|account).{0,25}"
        r"(?:currencies|dollars|euros|pounds|usd|eur|gbp|aud|cad|chf|yen)|"
        r"multi currency|multicurrency|fiat currenc|"
        r"currency (?:accounts?|support|supported|available)|"
        r"(?:dollar|euro|pound|usd|eur|gbp) (?:account|balance)"
    )
    if currency_support and not (exchange and strong_fee):
        return "fiat_currency_support"

    if exchange:
        if strong_fee or w(r"charge|charged|charging|commission|weekend|fair usage"):
            return "exchange_charge"
        if w(
            r"exchange rate|conversion rate|interbank|rates|"
            r"what rate|which rate|rate do|rate is|rate will|"
            r"rate you|rate used|current rate"
        ):
            return "exchange_rate"
        if wrong_rate and rate:
            return "exchange_rate"
        return "exchange_via_app"

    if w(
        r"change.{0,15}(?:pounds?|dollars?|euros?|usd|eur|gbp)|"
        r"(?:pounds?|dollars?|euros?|usd|eur|gbp).{0,15}"
        r"(?:to|into|for) (?:pounds?|dollars?|euros?|usd|eur|gbp)|"
        r"buy (?:foreign )?currency"
    ):
        return "exchange_via_app"

    # Account eligibility versus using an already-issued card abroad.
    country_eligibility = w(
        r"which countries|what countries|countries.{0,20}support|"
        r"country.{0,20}(?:supported|available)|"
        r"available in|operate in|resident|residency|citizen|citizenship|"
        r"live in|living in|based in|nationality|"
        r"open.{0,20}account.{0,30}(?:in|from)|"
        r"sign up.{0,25}(?:country|in)|register.{0,25}(?:country|in)"
    )
    if country_eligibility and not (
        card and w(r"use|using|pay|paying|accepted|acceptance|travel|abroad")
    ):
        return "country_support"

    # Ordinary payment status and failures.
    if purchase or (card and (declined or failure or pending)):
        if declined:
            return "declined_card_payment"
        if pending:
            return "pending_card_payment"
        if strong_fee and (purchase or w(r"charged")):
            return "card_payment_fee_charged"
        if failure and purchase:
            return "declined_card_payment"
        if card and failure:
            return "card_not_working"
        if w(r"not completed|not gone through|not processed|taking too long"):
            return "pending_card_payment"

    if w(
        r"request money|payment request|request a payment|"
        r"receive money|receiving money|send me money|"
        r"salary|wages|paycheck|pay cheque|employer|pay me|"
        r"someone.{0,25}(?:send|pay)|friend.{0,25}(?:send|pay)"
    ):
        return "receiving_money"

    if card and w(
        r"use|using|accepted|accept|work|pay|abroad|overseas|"
        r"international|foreign|anywhere|everywhere|online|countries"
    ) and not (failure or declined):
        return "card_acceptance"

    if card and w(r"order|ordering|apply|application"):
        return "order_physical_card"
    if w(r"physical card|plastic card|real card|actual card|tangible card"):
        return "get_physical_card"
    if card and w(r"get|obtain|have|need|want|receive"):
        return "get_physical_card"
    if card and (failure or w(r"broken|damaged|stopped|not functioning")):
        return "card_not_working"

    if fee and w(r"statement|charged|charge|account") and not purchase:
        return "extra_charge_on_statement"
    if w(r"outgoing"):
        return "pending_transfer"
    if pending and w(r"transaction|payment"):
        return "pending_card_payment"
    if w(r"login|log in|sign in|access") and failure:
        return "passcode_forgotten"

    return _nearest(t)


def predict(state) -> dict:
    text = _extract_text(state)
    answer = _classify(text)
    return {"answer": answer}