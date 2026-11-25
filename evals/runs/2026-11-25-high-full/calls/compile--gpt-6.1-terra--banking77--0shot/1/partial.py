import math
import re
import unicodedata
from collections import Counter


LABELS = """
activate_my_card
age_limit
apple_pay_or_google_pay
atm_support
automatic_top_up
balance_not_updated_after_bank_transfer
balance_not_updated_after_cheque_or_cash_deposit
beneficiary_not_allowed
cancel_transfer
card_about_to_expire
card_acceptance
card_arrival
card_delivery_estimate
card_linking
card_not_working
card_payment_fee_charged
card_payment_not_recognised
card_payment_wrong_exchange_rate
card_swallowed
cash_withdrawal_charge
cash_withdrawal_not_recognised
change_pin
compromised_card
contactless_not_working
country_support
declined_card_payment
declined_cash_withdrawal
declined_transfer
direct_debit_payment_not_recognised
disposable_card_limits
edit_personal_details
exchange_charge
exchange_rate
exchange_via_app
extra_charge_on_statement
failed_transfer
fiat_currency_support
get_disposable_virtual_card
get_physical_card
getting_spare_card
getting_virtual_card
lost_or_stolen_card
lost_or_stolen_phone
order_physical_card
passcode_forgotten
pending_card_payment
pending_cash_withdrawal
pending_top_up
pending_transfer
pin_blocked
receiving_money
refund_not_showing_up
request_refund
reverted_card_payment
supported_cards_and_currencies
terminate_account
top_up_by_bank_transfer_charge
top_up_by_card_charge
top_up_by_cash_or_cheque
top_up_failed
top_up_limits
top_up_reverted
topping_up_by_card
transaction_charged_twice
transfer_fee_charged
transfer_into_account
transfer_not_received_by_recipient
transfer_timing
unable_to_verify_identity
verify_my_identity
verify_source_of_funds
verify_top_up
virtual_card_not_working
visa_or_mastercard
why_verify_identity
wrong_amount_of_cash_received
wrong_exchange_rate_for_cash_withdrawal
""".strip().split()


def _extract(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        if not value:
            return ""
        user_messages = []
        for item in value:
            if isinstance(item, dict):
                role = str(item.get("role", item.get("speaker", ""))).lower()
                if role in ("user", "customer", "human", "client"):
                    text = _extract(item)
                    if text:
                        user_messages.append(text)
        if user_messages:
            return user_messages[-1]
        texts = [_extract(item) for item in value]
        return " ".join(x for x in texts if x)
    if isinstance(value, dict):
        for key in (
            "text", "utterance", "query", "customer_message", "user_message",
            "message", "content", "input", "question", "request", "description",
        ):
            if key in value:
                text = _extract(value[key])
                if text:
                    return text
        for key in ("messages", "conversation", "history", "dialogue", "dialog"):
            if key in value:
                text = _extract(value[key])
                if text:
                    return text
        parts = []
        for key, item in value.items():
            if key not in ("role", "speaker", "id", "type", "name"):
                text = _extract(item)
                if text:
                    parts.append(text)
        return " ".join(parts)
    return ""


def _normalize(text):
    text = unicodedata.normalize("NFKC", text).lower()
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r"\b(can)[' ]?t\b", "cannot", text)
    text = re.sub(r"\bwon[' ]?t\b", "will not", text)
    text = re.sub(r"\bshan[' ]?t\b", "shall not", text)
    text = re.sub(r"n['’]t\b", " not", text)
    text = re.sub(r"\b(i|you|we|they)['’]ve\b", r"\1 have", text)
    text = re.sub(r"\b(i|you|we|they)['’]re\b", r"\1 are", text)
    text = re.sub(r"\bi['’]m\b", "i am", text)
    text = re.sub(r"\b(it|that|what|where|who)['’]s\b", r"\1 is", text)
    text = re.sub(r"[_\-–—/]+", " ", text)
    text = re.sub(r"[^a-z0-9\s£$€]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _has(text, pattern):
    return re.search(pattern, text) is not None


def _fallback(text):
    examples = {
        "activate_my_card": "activate enable start using new physical card activation",
        "age_limit": "minimum maximum age old minor child teenager eligibility",
        "apple_pay_or_google_pay": "apple pay google pay wallet mobile nfc phone",
        "atm_support": "atm cashpoint cash machine location find withdraw supported",
        "automatic_top_up": "automatic recurring scheduled top up balance threshold",
        "balance_not_updated_after_bank_transfer": "incoming bank transfer money missing balance not updated received",
        "balance_not_updated_after_cheque_or_cash_deposit": "cash cheque deposit balance missing not updated",
        "beneficiary_not_allowed": "beneficiary recipient payee not allowed prohibited unsupported",
        "cancel_transfer": "cancel stop reverse recall bank transfer sent",
        "card_about_to_expire": "card expiring expiration expiry date replacement expired",
        "card_acceptance": "where card accepted use merchant shop abroad online",
        "card_arrival": "ordered card not arrived missing delivery waiting",
        "card_delivery_estimate": "how long card delivery arrive shipping time estimate",
        "card_linking": "link connect associate card account app",
        "card_not_working": "card not working broken damaged faulty problem",
        "card_payment_fee_charged": "fee charge cost paying card purchase merchant payment",
        "card_payment_not_recognised": "unrecognised unknown fraudulent card purchase payment transaction",
        "card_payment_wrong_exchange_rate": "card payment wrong foreign currency exchange rate",
        "card_swallowed": "atm swallowed retained ate kept stuck card",
        "cash_withdrawal_charge": "cash withdrawal atm fee charge cost",
        "cash_withdrawal_not_recognised": "unrecognised cash withdrawal atm unknown unauthorized",
        "change_pin": "change reset choose new card pin number",
        "compromised_card": "card details stolen compromised hacked copied security fraud",
        "contactless_not_working": "contactless tap nfc card payment does not work",
        "country_support": "supported countries country residence available sign up service",
        "declined_card_payment": "card payment declined rejected refused transaction",
        "declined_cash_withdrawal": "cash withdrawal atm declined rejected failed",
        "declined_transfer": "bank transfer declined rejected refused",
        "direct_debit_payment_not_recognised": "unrecognised unknown direct debit payment",
        "disposable_card_limits": "disposable single use virtual card limit number",
        "edit_personal_details": "change update personal details name address email phone",
        "exchange_charge": "currency exchange conversion fee charge cost",
        "exchange_rate": "currency exchange conversion rate price",
        "exchange_via_app": "exchange convert currency money in app",
        "extra_charge_on_statement": "extra charge payment statement more than expected",
        "failed_transfer": "bank transfer failed unsuccessful error",
        "fiat_currency_support": "supported fiat currencies currency account hold",
        "get_disposable_virtual_card": "get create disposable single use virtual card",
        "get_physical_card": "get physical plastic real card",
        "getting_spare_card": "extra spare additional second card",
        "getting_virtual_card": "get create virtual digital card",
        "lost_or_stolen_card": "lost stolen missing card theft",
        "lost_or_stolen_phone": "lost stolen missing phone mobile device",
        "order_physical_card": "order request physical plastic card",
        "passcode_forgotten": "forgot forgotten app password passcode login",
        "pending_card_payment": "card payment pending processing incomplete",
        "pending_cash_withdrawal": "cash withdrawal atm pending processing",
        "pending_top_up": "card top up deposit pending processing",
        "pending_transfer": "bank transfer pending processing",
        "pin_blocked": "card pin blocked locked too many attempts",
        "receiving_money": "receive money someone payment account",
        "refund_not_showing_up": "refund missing not received pending money back",
        "request_refund": "request refund return money purchase",
        "reverted_card_payment": "card payment reverted reversed returned",
        "supported_cards_and_currencies": "supported cards currencies top up visa mastercard",
        "terminate_account": "close delete terminate account cancel membership",
        "top_up_by_bank_transfer_charge": "fee charge adding money bank transfer top up",
        "top_up_by_card_charge": "fee charge adding money debit credit card top up",
        "top_up_by_cash_or_cheque": "add deposit top up cash cheque check",
        "top_up_failed": "adding money card top up failed declined",
        "top_up_limits": "top up limit maximum minimum amount",
        "top_up_reverted": "top up reversed reverted refunded returned",
        "topping_up_by_card": "add money top up using debit credit card",
        "transaction_charged_twice": "charged twice duplicate payment transaction double",
        "transfer_fee_charged": "bank transfer fee charge cost",
        "transfer_into_account": "bank transfer into account details iban swift",
        "transfer_not_received_by_recipient": "sent transfer recipient beneficiary not received missing",
        "transfer_timing": "how long bank transfer take time arrive",
        "unable_to_verify_identity": "identity verification failed cannot verify documents",
        "verify_my_identity": "how verify identity identification documents",
        "verify_source_of_funds": "verify prove source origin funds wealth income",
        "verify_top_up": "verify card top up verification code",
        "virtual_card_not_working": "virtual digital card not working failed",
        "visa_or_mastercard": "card visa or mastercard network",
        "why_verify_identity": "why verify identity need identification",
        "wrong_amount_of_cash_received": "atm wrong amount cash dispensed received less",
        "wrong_exchange_rate_for_cash_withdrawal": "atm cash withdrawal wrong currency exchange rate",
    }
    stop = {
        "a", "an", "the", "i", "me", "my", "you", "your", "we", "our",
        "is", "are", "was", "were", "be", "been", "to", "of", "for", "on",
        "in", "at", "by", "and", "or", "it", "this", "that", "do", "does",
        "did", "can", "could", "would", "should", "what", "how", "why",
        "where", "when", "with", "from", "have", "has", "had", "as", "if",
        "please", "about", "want", "need", "tell", "get", "make", "use",
    }

    def words(s):
        result = []
        for word in re.findall(r"[a-z0-9]+", s):
            if word in stop:
                continue
            if len(word) > 5 and word.endswith("ing"):
                word = word[:-3]
            elif len(word) > 4 and word.endswith("ed"):
                word = word[:-2]
            elif len(word) > 4 and word.endswith("s"):
                word = word[:-1]
            result.append(word)
        return result

    docs = {label: set(words(value)) for label, value in examples.items()}
    frequencies = Counter()
    for doc in docs.values():
        frequencies.update(doc)
    query = set(words(text))
    best_label = "card_not_working"
    best_score = 0.0
    for label in LABELS:
        doc = docs[label]
        overlap = query & doc
        score = sum(math.log(1 + len(docs) / (1 + frequencies[w])) for w in overlap)
        if score > best_score:
            best_score = score
            best_label = label
    return best_label


def predict(state):
    raw = _extract(state)
    text = _normalize(raw)
    exact = text.replace(" ", "_")
    if exact in LABELS:
        return {"answer": exact}

    def h(pattern):
        return _has(text, pattern)

    def answer(label):
        return {"answer": label}

    card = h(r"\b(card|cards|plastic)\b")
    virtual = h(r"\b(virtual|digital|online only)\b")
    disposable = h(r"\b(disposable|single use|one time|one use|one off)\b")
    phone = h(r"\b(phone|mobile|iphone|android|handset|device)\b")
    atm = h(r"\b(atm|cashpoint|cash machine|cash dispenser|cashpoint machine)\b")
    cash = h(r"\b(cash|cashpoint|atm|banknote|banknotes|notes)\b")
    cheque = h(r"\b(cheque|cheques|check|checks)\b")
    withdrawal = h(
        r"\b(withdraw|withdrawal|withdrawing|withdrawn|withdrew|"
        r"take out|taking out|took out|taken out|dispens\w*|"
        r"cash out|cashout)\b"
    )
    transfer = h(
        r"\b(transfer\w*|transferred|wire\w*|remittance|"
        r"bank payment|banking payment|sepa|swift|iban|beneficiary|payee|recipient)\b"
    )
    topup = h(
        r"\b(top up|topping up|topped up|topups|topup|recharg\w*|"
        r"load(?:ing|ed)? (?:my |the |some )?(?:account|balance|money|funds|card)|"
        r"add(?:ing|ed)? (?:some |more |my |the )?(?:money|funds|cash|balance)|"
        r"put(?:ting)? (?:some |more |my |the )?(?:money|funds|cash) "
        r"(?:in|into|on)|deposit(?:ing|ed)?|fund(?:ing)? my account)\b"
    )
    bank = h(r"\b(bank|banking|wire|sepa|swift|iban|account number|sort code)\b")
    payment = h(
        r"\b(payment|payments|paid|paying|purchase|purchased|transaction|"
        r"transactions|merchant|shop|shopping|bought|buy|pay)\b"
    )
    fee = h(r"\b(fee|fees|charge|charges|charged|charging|commission|cost|costs)\b")
    explicit_fee = h(r"\b(fee|fees|commission|surcharge|service charge|cost of)\b")
    pending = h(r"\b(pending|processing|in progress|in process|still processing|authori[sz]ation hold)\b")
    failed = h(
        r"\b(fail\w*|declin\w*|reject\w*|refus\w*|denied|unsuccessful|"
        r"not successful|not working|does not work|did not work|"
        r"cannot|unable|not able|could not|would not|won not|"
        r"not go through|not going through|not gone through|"
        r"not went through|problem|error)\b"
    )
    declined = h(r"\b(declin\w*|reject\w*|refus\w*|denied|not authori[sz]ed)\b")
    reversed_tx = h(r"\b(revert\w*|revers\w*|returned|sent back|bounced back|rolled back)\b")
    missing = h(
        r"\b(not (?:yet )?(?:received|arrived|shown|showing|appear\w*|"
        r"credited|updated|there|come|came|gone through)|"
        r"has not (?:arrived|come|shown|appeared)|"
        r"have not (?:received|got)|haven t|missing|"
        r"not in (?:my|the|their) account|never (?:received|arrived|came)|"
        r"still waiting|waiting for|where is|where are|"
        r"no sign of|not reflected|does not show|did not arrive)\b"
    )
    unknown = h(
        r"\b(unrecogni[sz]\w*|not recogni[sz]\w*|do not recogni[sz]\w*|"
        r"did not recogni[sz]\w*|unknown|unauthori[sz]\w*|"
        r"not authori[sz]\w*|did not (?:make|do|authori[sz]e|approve)|"
        r"never (?:made|did|authori[sz]ed)|was not me|not mine|"
        r"not my (?:payment|transaction|purchase|withdrawal)|"
        r"no idea (?:what|where|who)|suspicious|fraudulent|"
        r"fraud|strange (?:payment|transaction|charge|withdrawal))\b"
    )
    exchange = h(r"\b(exchange|conversion|convert|converted|converting|fx|forex)\b")
    rate = h(r"\b(rate|rates|exchange rate|conversion rate)\b")
    foreign = h(r"\b(foreign|abroad|overseas|international|currency|currencies)\b")
    wrong = h(r"\b(wrong|incorrect|inaccurate|unfair|bad|different|poor|not right|too (?:high|low))\b")
    limit = h(r"\b(limit|limits|limited|maximum|minimum|max|min|how many|how much|cap)\b")
    duration = h(
        r"\b(how long|how many (?:days|hours|weeks)|when (?:will|can|should|does)|"
        r"time (?:does|will|to|for|it)|delivery time|arrival time|"
        r"take to|takes to|taking (?:so |too )?long|long does|"
        r"estimated|estimate|expected arrival)\b"
    )
    lost = h(r"\b(lost|stolen|steal|theft|misplaced|missing|left behind)\b")
    change = h(r"\b(change|changing|update|updating|edit|correct|modify|replace|reset|new)\b")
    verify = h(r"\b(verif\w*|validat\w*|authenticat\w*|confirm\w*|proof|prove|evidence)\b")

    if h(r"\b(apple pay|google pay|gpay|google wallet|apple wallet|samsung pay)\b"):
        return answer("apple_pay_or_google_pay")

    if atm and card and h(r"\b(swallow\w*|ate|eaten|retain\w*|kept|confiscat\w*|"
                          r"stuck|trapped|not give (?:me )?back|did not return)\b"):
        return answer("card_swallowed")
    if card and h(r"\b(card (?:was |is |got |has been )?(?:swallowed|retained|eaten))\b"):
        return answer("card_swallowed")

    if phone and lost:
        return answer("lost_or_stolen_phone")
    if card and h(r"\b(compromis\w*|clon\w*|hacked|hacking|copied|"
                  r"card details (?:were |are |have been )?(?:stolen|leaked|exposed)|"
                  r"someone (?:has|knows|stole) my card (?:details|number))\b"):
        return answer("compromised_card")
    if card and lost and not h(r"\b(delivery|deliver|arriv\w*|post|mail|ship\w*)\b"):
        return answer("lost_or_stolen_card")

    if h(r"\b(age limit|minimum age|maximum age|old enough|how old|"
         r"underage|under age|minor|teenager|teen|child|children|"
         r"years old|year old|aged? \d+|age requirement)\b"):
        return answer("age_limit")

    if h(r"\b(passcode|pass code|password|login code|log in code|app code)\b"):
        if h(r"\b(forgot\w*|forgotten|remember|lost|reset|recover|locked out|"
             r"cannot (?:log|sign)|unable to (?:log|sign))\b"):
            return answer("passcode_forgotten")
    if h(r"\b(pin|pin code|pin number)\b"):
        if h(r"\b(block\w*|lock\w*|too many|wrong (?:pin|attempt)|"
             r"incorrect (?:pin|attempt)|exceed\w*|tries|attempts)\b"):
            return answer("pin_blocked")
        if change or h(r"\b(forgot\w*|remember|choose|set|find|see|view)\b"):
            return answer("change_pin")

    if h(r"\b(source of (?:my |the )?(?:funds|money|wealth|income)|"
         r"where (?:my |the )?(?:funds|money|income) (?:came|come) from|"
         r"proof of (?:income|funds|wealth|salary)|"
         r"(?:verify|verification of|prove) (?:my )?(?:income|salary|wealth|funds))\b"):
        return answer("verify_source_of_funds")

    identity = h(r"\b(identity|identification|id verification|verify (?:my |the )?id|"
                 r"personal id|passport|selfie|identity document|"
                 r"photo id|driving licen[cs]e|identity check)\b")
    if identity and (verify or h(r"\b(id|identification|identity check|selfie)\b")):
        if h(r"\b(why|what (?:is the )?reason|what for|purpose|"
             r"necessary|need to|have to|required|requirement)\b") and not failed:
            return answer("why_verify_identity")
        if failed or h(r"\b(not accepted|not recognised|not recognized|"
                        r"not verified|keeps failing|not verify)\b"):
            return answer("unable_to_verify_identity")
        return answer("verify_my_identity")

    if verify and (topup or card) and h(
        r"\b(card|top up|topup|deposit|fund|verification|security|code|"
        r"statement|authori[sz]ation|confirm)\b"
    ):
        return answer("verify_top_up")

    if h(r"\b(close|closing|terminate|termination|delete|deleting|"
         r"shut down|deactivate|cancel|cancellation)\b") and h(
        r"\b(account|membership|profile|subscription)\b"
    ) and not transfer:
        return answer("terminate_account")

    if change and h(
        r"\b(personal (?:detail|information|data)|details|address|"
        r"phone number|mobile number|email|e mail|surname|last name|"
        r"first name|legal name|date of birth|home address)\b"
    ) and not h(r"\b(card number|pin number)\b"):
        return answer("edit_personal_details")

    if h(r"\b(twice|double charged|charged double|duplicate|duplicated|"
         r"two times|2 times|multiple times|charged me two|"
         r"charged me twice|same (?:payment|transaction) twice)\b"):
        return answer("transaction_charged_twice")

    if h(r"\b(direct debit|direct debits|directdebit)\b") and unknown:
        return answer("direct_debit_payment_not_recognised")

    if h(r"\b(refund|refunded|money back|reimbursement|reimbursed)\b"):
        if missing or pending or h(r"\b(not (?:got|given|paid)|still (?:not|waiting)|"
                                   r"late|delay\w*|taking (?:a |too |so )?long|"
                                   r"when (?:will|does|can)|how long)\b"):
            return answer("refund_not_showing_up")
        if not (topup and reversed_tx):
            return answer("request_refund")

    if disposable:
        if limit:
            return answer("disposable_card_limits")
        if failed and card:
            return answer("virtual_card_not_working")
        return answer("get_disposable_virtual_card")

    if card and h(r"\b(expir\w*|expiry|expiration|expire date|valid until|"
                  r"renew\w*|renewal)\b"):
        return answer("card_about_to_expire")

    if card and h(r"\b(contactless|tap(?:ping)? (?:to |and )?pay|"
                  r"tap my card|tap payment|nfc)\b") and (
        failed or h(r"\b(not|issue|problem|broken|declin\w*)\b")
    ):
        return answer("contactless_not_working")

    if h(r"\b(automatic|automatically|auto|recurring|recurrent|"
         r"scheduled|schedule|periodic|regularly)\b") and (
        topup or h(r"\b(balance|money|funds)\b")
    ):
        return answer("automatic_top_up")

    if cash and cheque and h(r"\b(deposit|add|put|top up|topping|pay in)\b") and not missing:
        return answer("top_up_by_cash_or_cheque")

    if (cash or cheque) and not withdrawal and not atm:
        deposit_context = topup or h(r"\b(paid in|pay in|deposit|deposited|"
                                    r"lodged|credited|account|balance)\b")
        if deposit_context and (missing or h(r"\b(balance.*not|not.*balance|"
                                             r"balance.*unchanged|not credited|"
                                             r"still (?:not|waiting))\b")):
            return answer("balance_not_updated_after_cheque_or_cash_deposit")
        if deposit_context:
            return answer("top_up_by_cash_or_cheque")

    if atm or withdrawal:
        cash_context = cash or atm or h(r"\b(withdraw|withdrawal|withdrawing|withdrew)\b")
        if cash_context:
            if exchange and (rate or wrong or foreign):
                return answer("wrong_exchange_rate_for_cash_withdrawal")
            if unknown:
                return answer("cash_withdrawal_not_recognised")
            if h(r"\b(wrong amount|incorrect amount|less (?:cash|money|than)|"
                 r"not enough (?:cash|money)|only (?:gave|received|got)|"
                 r"did not (?:give|dispense)|dispensed (?:less|wrong|only)|"
                 r"received (?:less|wrong)|more (?:deducted|debited)|"
                 r"shortchanged|short changed)\b"):
                return answer("wrong_amount_of_cash_received")
            if pending:
                return answer("pending_cash_withdrawal")
            if fee and not h(r"\b(not charged|without (?:a )?fee)\b"):
                return answer("cash_withdrawal_charge")
            if failed or h(r"\b(not (?:dispens\w*|withdraw\w*)|"
                           r"could not (?:get|take|withdraw))\b"):
                return answer("declined_cash_withdrawal")
            return answer("atm_support")

    if h(r"\b(visa|mastercard|master card)\b"):
        supported_topup = (topup or h(r"\b(top up|topup|funding|debit card|credit card)\b")) and h(
            r"\b(which|what|support\w*|accept\w*|can i use|allowed|"
            r"types|kinds)\b"
        )
        if supported_topup:
            return answer("supported_cards_and_currencies")
        return answer("visa_or_mastercard")

    if card and h(r"\b(supported|support|accept\w*|which|what|types|kinds)\b") and (
        topup or h(r"\b(funding|debit card|credit card|cards and currencies|"
                   r"currencies and cards)\b")
    ):
        return answer("supported_cards_and_currencies")

    if h(r"\b(beneficiary|payee|recipient)\b") and h(
        r"\b(not allowed|not permitted|unsupported|not supported|"
        r"cannot (?:send|transfer|add)|unable|prohibited|ineligible|"
        r"restricted|not eligible|not accept)\b"
    ):
        return answer("beneficiary_not_allowed")

    incoming = h(
        r"\b(into my account|to my account|into (?:the|this) account|"
        r"to (?:the|this) account|my balance|my account balance|"
        r"receive|receiving|received|incoming|sent me|send me|"
        r"someone (?:sent|send|transferred)|from my bank|from another bank|"
        r"from (?:my |a )?bank account|deposit)\b"
    )
    outgoing = h(
        r"\b(recipient|beneficiary|payee|person i sent|"
        r"person i transferred|i sent|i have sent|i transferred|"
        r"sent (?:money|funds|a transfer) to|"
        r"transfer(?:red)? (?:money|funds) to (?:a |the |another |his |her |their ))\b"
    )

    if (bank or transfer) and incoming and not outgoing and (
        missing or h(r"\b(balance (?:has |is |was )?not|balance.*"
                     r"(?:unchanged|not updated|not increased|wrong)|"
                     r"not (?:credited|added|showing)|still waiting)\b")
    ):
        return answer("balance_not_updated_after_bank_transfer")

    if topup:
        if verify and h(r"\b(card|code|confirm|verification)\b"):
            return answer("verify_top_up")
        if limit:
            return answer("top_up_limits")
        if pending:
            return answer("pending_top_up")
        if reversed_tx:
            return answer("top_up_reverted")
        if failed:
            return answer("top_up_failed")
        if fee:
            if bank or (transfer and not card):
                return answer("top_up_by_bank_transfer_charge")
            return answer("top_up_by_card_charge")
        if bank or (transfer and not card):
            return answer("transfer_into_account")
        return answer("topping_up_by_card")

    if transfer or (bank and h(r"\b(send|sending|sent|payment|money|funds)\b")):
        if h(r"\b(cancel|cancell\w*|stop|recall|undo|abort)\b"):
            return answer("cancel_transfer")
        if outgoing and (missing or h(
            r"\b(not (?:got|receive\w*|arriv\w*|showing|credited)|"
            r"has not (?:got|receive\w*|arriv\w*)|"
            r"have not (?:got|receive\w*)|never (?:got|received)|"
            r"not reached|not gone to|where (?:is|are))\b"
        )):
            return answer("transfer_not_received_by_recipient")
        if declined:
            return answer("declined_transfer")
        if h(r"\b(fail\w*|unsuccessful|error|did not go through|"
             r"not successful|not gone through)\b"):
            return answer("failed_transfer")
        if pending:
            return answer("pending_transfer")
        if fee:
            if incoming and (bank or h(r"\b(add|fund|deposit|load)\b")):
                return answer("top_up_by_bank_transfer_charge")
            return answer("transfer_fee_charged")
        if missing and not incoming:
            return answer("transfer_not_received_by_recipient")
        if duration:
            return answer("transfer_timing")
        if incoming:
            if h(r"\b(iban|swift|sort code|account number|bank details|"
                 r"bank transfer|wire transfer|from my bank|into my account|"
                 r"to my account from)\b"):
                return answer("transfer_into_account")
            return answer("receiving_money")
        if h(r"\b(how long|time|days|hours|when)\b"):
            return answer("transfer_timing")
        if h(r"\b(cannot|unable|not able|not possible)\b"):
            return answer("failed_transfer")
        return answer("transfer_timing")

    if h(r"\b(receive|receiving|get|getting)\b") and h(
        r"\b(money|funds|payment|payments|salary|wages|paid)\b"
    ) and not card:
        return answer("receiving_money")

    if exchange or rate:
        if (card or payment) and (wrong or h(r"\b(charged|applied|used)\b")) and rate:
            return answer("card_payment_wrong_exchange_rate")
        if fee and not h(r"\b(no fee|without (?:a )?fee)\b"):
            return answer("exchange_charge")
        if rate or h(r"\b(what|which|how much|price)\b"):
            return answer("exchange_rate")
        return answer("exchange_via_app")

    if h(r"\b(currency|currencies|fiat|pounds|euros|dollars)\b") and h(
        r"\b(support\w*|available|which|what|hold|account|balance)\b"
    ):
        return answer("fiat_currency_support")

    if h(r"\b(country|countries|residen\w*|live in|living in|"
         r"available in|supported in|available where|which regions)\b") and (
        h(r"\b(support\w*|available|open|account|sign up|register|"
          r"eligible|service|use|work|country|countries)\b")
    ):
        if card and h(r"\b(use (?:my |the )?card|pay (?:with|using)|"
                      r"card (?:work|accepted))\b"):
            return answer("card_acceptance")
        return answer("country_support")

    if virtual and card:
        if failed or h(r"\b(broken|problem|issue|not usable)\b"):
            return answer("virtual_card_not_working")
        return answer("getting_virtual_card")

    if card and h(r"\b(extra card|spare card|additional card|second card|"
                  r"another card|multiple cards|two cards|2 cards|"
                  r"more than one card)\b"):
        return answer("getting_spare_card")

    if card and h(r"\b(activat\w*|activation|enable (?:my |the )?card|"
                  r"start using (?:my |the )?card)\b"):
        return answer("activate_my_card")

    if card and h(r"\b(link|linking|linked|connect|connecting|associate|"
                  r"attach|pair|pairing)\b") and not payment:
        return answer("card_linking")

    delivery = h(
        r"\b(deliver\w*|arriv\w*|ship\w*|mail\w*|post(?:ed|age)?|"
        r"sent out|dispatch\w*|in the post|in the mail|"
        r"track(?:ing)?|courier)\b"
    )
    if card and (delivery or (missing and h(r"\b(order\w*|card)\b"))):
        if missing or h(r"\b(late|delay\w*|overdue|still waiting|"
                        r"not (?:here|delivered|arrived)|where is)\b"):
            return answer("card_arrival")
        if duration or h(r"\b(when|long|time|days|weeks|estimate)\b"):
            return answer("card_delivery_estimate")
        return answer("card_arrival")

    if card and h(r"\b(order|ordering|ordered|request|requesting)\b") and not payment:
        return answer("order_physical_card")
    if card and h(r"\b(physical|plastic|real card|actual card|"
                  r"tangible|card in person)\b") and h(
        r"\b(get|getting|obtain|have|need|want|receive|available|"
        r"physical|plastic)\b"
    ) and not payment:
        return answer("get_physical_card")

    if card and h(r"\b(where|which|anywhere|everywhere|abroad|overseas|"
                  r"internationally|online|merchant|shop|store)\b") and h(
        r"\b(accept\w*|use|usable|work|valid|pay|spend|supported)\b"
    ) and not (declined or unknown):
        return answer("card_acceptance")

    if unknown and (card or payment or h(r"\b(charge|transaction)\b")):
        return answer("card_payment_not_recognised")

    if payment or card:
        if pending:
            return answer("pending_card_payment")
        if reversed_tx:
            return answer("reverted_card_payment")
        if declined:
            return answer("declined_card_payment")
        if h(r"\b(extra (?:charge|amount|payment|money)|"
             r"additional (?:charge|amount)|charged (?:me )?more|"
             r"more (?:than|money than) (?:i|the|expected)|"
             r"unexpected (?:charge|amount)|"
             r"charge on (?:my |the )?statement)\b"):
            return answer("extra_charge_on_statement")
        if explicit_fee or (fee and h(r"\b(fee|for (?:a |the )?(?:card )?payment|"
                                      r"for paying|using (?:my |the )?card|"
                                      r"cost of paying)\b")):
            return answer("card_payment_fee_charged")
        if card and failed:
            if payment and h(r"\b(pay|purchase|transaction|merchant)\b"):
                return answer("declined_card_payment")
            return answer("card_not_working")
        if card and h(r"\b(damaged|broken|faulty|defective|worn|"
                      r"chip|magnetic strip|not work\w*|issue|problem)\b"):
            return answer("card_not_working")
        if card and h(r"\b(get|getting|obtain|have|need|want|apply|application)\b"):
            return answer("get_physical_card")
        if card and h(r"\b(link|connect|associate|attach)\b"):
            return answer("card_linking")

    return answer(_fallback(text))