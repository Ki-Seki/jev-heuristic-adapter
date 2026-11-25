import re
import unicodedata
from collections import Counter

LABELS = [
    "activate_my_card", "age_limit", "apple_pay_or_google_pay", "atm_support",
    "automatic_top_up", "balance_not_updated_after_bank_transfer",
    "balance_not_updated_after_cheque_or_cash_deposit", "beneficiary_not_allowed",
    "cancel_transfer", "card_about_to_expire", "card_acceptance", "card_arrival",
    "card_delivery_estimate", "card_linking", "card_not_working",
    "card_payment_fee_charged", "card_payment_not_recognised",
    "card_payment_wrong_exchange_rate", "card_swallowed", "cash_withdrawal_charge",
    "cash_withdrawal_not_recognised", "change_pin", "compromised_card",
    "contactless_not_working", "country_support", "declined_card_payment",
    "declined_cash_withdrawal", "declined_transfer",
    "direct_debit_payment_not_recognised", "disposable_card_limits",
    "edit_personal_details", "exchange_charge", "exchange_rate",
    "exchange_via_app", "extra_charge_on_statement", "failed_transfer",
    "fiat_currency_support", "get_disposable_virtual_card", "get_physical_card",
    "getting_spare_card", "getting_virtual_card", "lost_or_stolen_card",
    "lost_or_stolen_phone", "order_physical_card", "passcode_forgotten",
    "pending_card_payment", "pending_cash_withdrawal", "pending_top_up",
    "pending_transfer", "pin_blocked", "receiving_money",
    "refund_not_showing_up", "request_refund", "reverted_card_payment",
    "supported_cards_and_currencies", "terminate_account",
    "top_up_by_bank_transfer_charge", "top_up_by_card_charge",
    "top_up_by_cash_or_cheque", "top_up_failed", "top_up_limits",
    "top_up_reverted", "topping_up_by_card", "transaction_charged_twice",
    "transfer_fee_charged", "transfer_into_account",
    "transfer_not_received_by_recipient", "transfer_timing",
    "unable_to_verify_identity", "verify_my_identity", "verify_source_of_funds",
    "verify_top_up", "virtual_card_not_working", "visa_or_mastercard",
    "why_verify_identity", "wrong_amount_of_cash_received",
    "wrong_exchange_rate_for_cash_withdrawal"
]

PROTOTYPES = {
    "activate_my_card": "activate enable start using new physical card activation",
    "age_limit": "minimum age old child minor under eighteen eligible account",
    "apple_pay_or_google_pay": "apple pay google pay wallet add card phone",
    "atm_support": "which atm cash machine support use withdraw compatible",
    "automatic_top_up": "automatic recurring auto top up add money schedule",
    "balance_not_updated_after_bank_transfer": "incoming bank transfer deposit balance not received missing",
    "balance_not_updated_after_cheque_or_cash_deposit": "cash cheque check deposit balance not received missing",
    "beneficiary_not_allowed": "recipient beneficiary not allowed supported cannot send money",
    "cancel_transfer": "cancel stop reverse bank transfer sent payment",
    "card_about_to_expire": "card expires expiry expiration expired renew replacement",
    "card_acceptance": "where can use card accepted merchant online abroad payment",
    "card_arrival": "ordered card not arrived delivery missing where is card",
    "card_delivery_estimate": "how long card delivery shipping arrive estimated date",
    "card_linking": "link connect card account app",
    "card_not_working": "card does not work broken damaged unable pay",
    "card_payment_fee_charged": "card purchase payment fee charged commission",
    "card_payment_not_recognised": "unrecognised unknown card transaction purchase fraud",
    "card_payment_wrong_exchange_rate": "wrong currency exchange conversion rate card payment",
    "card_swallowed": "atm swallowed retained kept captured card",
    "cash_withdrawal_charge": "atm cash withdrawal fee charge commission",
    "cash_withdrawal_not_recognised": "unrecognised unknown cash withdrawal atm",
    "change_pin": "change reset find view card pin number",
    "compromised_card": "card details exposed compromised hacked security fraud",
    "contactless_not_working": "contactless tap card payment not working",
    "country_support": "country region resident live supported available open account",
    "declined_card_payment": "card purchase payment declined rejected refused",
    "declined_cash_withdrawal": "cash withdrawal atm declined rejected refused",
    "declined_transfer": "bank transfer declined rejected refused",
    "direct_debit_payment_not_recognised": "unrecognised unknown direct debit payment",
    "disposable_card_limits": "disposable single use virtual card limit maximum",
    "edit_personal_details": "change update personal details name address phone email",
    "exchange_charge": "currency exchange conversion fee charge",
    "exchange_rate": "currency exchange rate conversion price",
    "exchange_via_app": "exchange convert currencies money in app",
    "extra_charge_on_statement": "extra charge card payment statement amount",
    "failed_transfer": "bank transfer failed bounced returned unsuccessful",
    "fiat_currency_support": "supported fiat currency currencies hold account",
    "get_disposable_virtual_card": "get create disposable single use virtual card",
    "get_physical_card": "how get physical plastic debit card",
    "getting_spare_card": "extra spare second additional card",
    "getting_virtual_card": "get create virtual digital online card",
    "lost_or_stolen_card": "lost stolen missing card freeze block",
    "lost_or_stolen_phone": "lost stolen phone mobile device",
    "order_physical_card": "order request physical plastic card",
    "passcode_forgotten": "forgot app passcode password login access",
    "pending_card_payment": "card payment transaction pending processing",
    "pending_cash_withdrawal": "cash withdrawal atm pending processing",
    "pending_top_up": "top up card deposit pending processing",
    "pending_transfer": "outgoing bank transfer transaction pending processing",
    "pin_blocked": "pin blocked locked attempts wrong unblock",
    "receiving_money": "receive money account details iban someone send me",
    "refund_not_showing_up": "refund missing not received pending balance",
    "request_refund": "request get refund money back merchant",
    "reverted_card_payment": "card payment reversed reverted returned cancelled",
    "supported_cards_and_currencies": "supported bank cards currencies use top up",
    "terminate_account": "close terminate delete deactivate account",
    "top_up_by_bank_transfer_charge": "fee charge add money bank transfer deposit",
    "top_up_by_card_charge": "fee charge top up debit credit card",
    "top_up_by_cash_or_cheque": "top up deposit add money cash cheque check",
    "top_up_failed": "top up add money card failed declined rejected",
    "top_up_limits": "top up maximum minimum limit amount",
    "top_up_reverted": "top up reversed reverted returned",
    "topping_up_by_card": "how top up add money using card",
    "transaction_charged_twice": "charged twice duplicate payment double transaction",
    "transfer_fee_charged": "bank transfer fee charge sending money",
    "transfer_into_account": "add money transfer into account bank deposit",
    "transfer_not_received_by_recipient": "sent transfer beneficiary recipient has not received money",
    "transfer_timing": "how long bank transfer take arrive time",
    "unable_to_verify_identity": "cannot verify identity documents verification failed",
    "verify_my_identity": "how verify identity documents identification",
    "verify_source_of_funds": "verify prove source of funds money income",
    "verify_top_up": "verify card top up verification code charge",
    "virtual_card_not_working": "virtual digital card not working online payment",
    "visa_or_mastercard": "visa mastercard card network type",
    "why_verify_identity": "why need verify identity documents",
    "wrong_amount_of_cash_received": "atm gave wrong amount cash less money withdrawn",
    "wrong_exchange_rate_for_cash_withdrawal": "wrong exchange rate cash withdrawal atm"
}

STOPWORDS = {
    "a", "an", "the", "i", "me", "my", "mine", "you", "your", "we", "our",
    "it", "its", "is", "are", "was", "were", "be", "been", "being", "do",
    "does", "did", "have", "has", "had", "can", "could", "would", "should",
    "will", "shall", "may", "might", "to", "of", "for", "on", "in", "at",
    "by", "with", "from", "and", "or", "but", "this", "that", "these",
    "those", "what", "how", "why", "when", "where", "which", "who", "about",
    "please", "help", "want", "need", "would", "like", "there", "some"
}


def _text(state):
    if isinstance(state, str):
        return state
    if isinstance(state, dict):
        for key in ("text", "message", "query", "question", "utterance", "content", "state"):
            value = state.get(key)
            if isinstance(value, str):
                return value
        return " ".join(str(value) for value in state.values() if isinstance(value, str))
    if isinstance(state, (list, tuple)):
        return " ".join(str(value) for value in state if isinstance(value, str))
    return str(state) if state is not None else ""


def _normalize(text):
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.replace("’", "'").replace("_", " ")
    substitutions = [
        (r"\bcan't\b", "cannot"),
        (r"\bcannot\b", "can not"),
        (r"\bwon't\b", "will not"),
        (r"\bdoesn't\b", "does not"),
        (r"\bdon't\b", "do not"),
        (r"\bdidn't\b", "did not"),
        (r"\bisn't\b", "is not"),
        (r"\baren't\b", "are not"),
        (r"\bwasn't\b", "was not"),
        (r"\bhasn't\b", "has not"),
        (r"\bhaven't\b", "have not"),
        (r"\bwouldn't\b", "would not"),
        (r"\bi'm\b", "i am"),
        (r"\bi've\b", "i have"),
        (r"\bit's\b", "it is"),
        (r"\bwhat's\b", "what is"),
        (r"\btop[\s-]*up", "top up"),
        (r"\bmaster\s*card\b", "mastercard"),
        (r"\bcheques?\b", "cheque"),
        (r"\bchecks?\b(?=\s+(?:deposit|deposited|payment))", "cheque"),
    ]
    for pattern, replacement in substitutions:
        text = re.sub(pattern, replacement, text)
    return re.sub(r"\s+", " ", text).strip()


def _has(text, pattern):
    return re.search(pattern, text) is not None


def _tokens(text):
    words = re.findall(r"[a-z0-9]+", text)
    result = []
    aliases = {
        "payments": "payment", "paid": "payment", "paying": "payment",
        "transfers": "transfer", "transferred": "transfer", "transferring": "transfer",
        "cards": "card", "currencies": "currency", "exchanging": "exchange",
        "withdrawals": "withdrawal", "withdrawn": "withdrawal", "withdrawing": "withdrawal",
        "fees": "fee", "charges": "charge", "charged": "charge", "charging": "charge",
        "deposited": "deposit", "deposits": "deposit", "recipient": "beneficiary",
        "receiving": "receive", "received": "receive", "arrived": "arrive",
        "arrival": "arrive", "arriving": "arrive", "verification": "verify",
        "verified": "verify", "verifying": "verify", "identity": "identity",
        "failed": "fail", "failure": "fail", "working": "work",
        "recognized": "unrecognised", "recognised": "unrecognised",
        "unrecognized": "unrecognised", "reversed": "reverted",
        "refunds": "refund", "details": "detail", "documents": "document",
        "money": "money", "cashpoint": "atm", "cashpoints": "atm",
    }
    for word in words:
        if word not in STOPWORDS:
            result.append(aliases.get(word, word))
    return result


def _fallback(text):
    query = Counter(_tokens(text))
    best = "pending_transfer"
    best_score = 0.0
    for label, prototype in PROTOTYPES.items():
        target = Counter(_tokens(prototype))
        overlap = sum(min(count, target.get(word, 0)) for word, count in query.items())
        if not overlap:
            continue
        score = overlap / (len(target) ** 0.5)
        score += overlap / max(1, sum(query.values())) * 0.7
        if score > best_score:
            best_score = score
            best = label
    return best


def _classify(t):
    normalized_label = re.sub(r"[^a-z0-9]+", "_", t).strip("_")
    if normalized_label in LABELS:
        return normalized_label

    card = _has(t, r"\b(card|cards|debit card|credit card|plastic)\b")
    virtual = _has(t, r"\b(virtual|digital|disposable|single[ -]use|one[ -]time)\b")
    disposable = _has(t, r"\b(disposable|single[ -]use|one[ -]time|one use)\b")
    phone = _has(t, r"\b(phone|mobile|handset|device|cellphone)\b")
    atm = _has(t, r"\b(atm|cashpoint|cash point|cash machine|cash dispenser)\b")
    withdrawal = atm or _has(t, r"\b(withdraw|withdrawal|withdrew|withdrawn|taking out cash|take out cash|cash out)\b")
    cash = _has(t, r"\b(cash|notes|banknotes|bank notes)\b")
    cheque = _has(t, r"\b(cheque|check deposit|paper check)\b")
    bank = _has(t, r"\b(bank|wire|swift|sepa|iban|bacs|ach)\b")
    transfer = _has(t, r"\b(transfer|transferred|transferring|wire|remittance|sent money|send money|sent funds|send funds)\b")
    topup = _has(t, r"\b(top up|topping up|topped up|recharge|reload|load(?:ing)? money|add(?:ed|ing)? (?:some )?(?:money|funds|balance)|fund(?:ing)? my account)\b")
    payment = _has(t, r"\b(payment|paying|paid|purchase|transaction|purchase|merchant|shop|spent|spending)\b")
    direct_debit = _has(t, r"\b(direct debit|directdebit)\b")
    fee = _has(t, r"\b(fee|fees|charge|charges|charged|charging|commission|cost|costs|expensive|surcharge)\b")
    rate = _has(t, r"\b(exchange rate|conversion rate|currency rate|forex rate|fx rate|wrong rate|bad rate)\b")
    exchange = rate or _has(t, r"\b(exchange|exchanging|convert|conversion|converted|converting|foreign currency|forex)\b")
    pending = _has(t, r"\b(pending|processing|in progress|still (?:being )?processed|not completed|not complete|uncompleted|awaiting|on hold|stuck|waiting|taking too long)\b")
    fail = _has(t, r"\b(fail|failed|failing|unsuccessful|not successful|not working|does not work|do not work|will not work|cannot|can not|unable|could not|error|problem|trouble|issue)\b")
    declined = _has(t, r"\b(declin\w*|reject\w*|refus\w*|denied|denial)\b")
    reversed_ = _has(t, r"\b(revert\w*|revers\w*|returned|bounced|sent back|brought back|rolled back)\b")
    missing = _has(t, r"\b(not (?:yet )?(?:received|arrived|showing|showing up|appeared|credited|reflected|updated|come|there)|never (?:received|arrived|got|came)|has not (?:been )?(?:received|arrived|shown|appeared|credited|updated|come)|have not (?:been )?(?:received|arrived|shown|credited|got)|missing|not there|not showing|did not (?:arrive|receive|get|show)|where is|where are|still waiting|waiting for)\b")
    unknown = _has(t, r"\b(unrecogni[sz]ed|unfamiliar|unauthori[sz]ed|unknown|not recogni[sz]e|do not recogni[sz]e|did not (?:make|authori[sz]e|pay|withdraw)|not mine|not my|never (?:made|authori[sz]ed)|someone else|fraudulent|fraud|scam|suspicious)\b")
    timing = _has(t, r"\b(how long|how much time|when will|when can|when should|how soon|time (?:does|will|to|for|it takes)|how many (?:days|hours)|estimated|estimate|delivery date|arrival date|eta)\b")
    limit = _has(t, r"\b(limit|limits|maximum|minimum|max|min|how much|how many|cap|allowance)\b")
    card_failure = fail or declined or _has(t, r"\b(broken|damaged|faulty|not accepted|not functioning|not usable)\b")

    if phone and _has(t, r"\b(lost|stolen|steal|missing|theft|misplaced|robbed)\b"):
        return "lost_or_stolen_phone"
    if card and _has(t, r"\b(lost|stolen|steal|misplaced|theft|robbed)\b"):
        return "lost_or_stolen_card"
    if card and _has(t, r"\b(compromised|hacked|card details (?:were|are|have been) (?:stolen|leaked|exposed)|someone (?:has|got) my card details)\b"):
        return "compromised_card"
    if card and _has(t, r"\b(swallowed|retained|captured|ate my card|eaten my card|kept my card|took my card|stuck in (?:the )?(?:atm|machine))\b"):
        return "card_swallowed"

    if _has(t, r"\b(source of (?:my )?(?:funds|money|wealth|income)|proof of (?:income|funds|wealth)|where (?:my|the) money (?:came|comes) from|prove (?:where|the origin))\b"):
        return "verify_source_of_funds"
    identity = _has(t, r"\b(identity|identification|verify (?:myself|me|my account)|verify my (?:id|identity)|identity verification|proof of identity|id verification|passport|selfie|proof of address|verify (?:my )?documents?)\b")
    if identity:
        if _has(t, r"\b(why|what (?:is the )?reason|purpose|necessary|have to|need to|must i)\b") and not fail:
            return "why_verify_identity"
        if fail or declined or _has(t, r"\b(not verified|verification failed|verification problem|verification rejected)\b"):
            return "unable_to_verify_identity"
        return "verify_my_identity"

    if _has(t, r"\b(age limit|minimum age|maximum age|how old|years old|under ?18|under eighteen|minor|child|teenager)\b"):
        return "age_limit"
    if _has(t, r"\b(apple pay|google pay|gpay|android pay|apple wallet|google wallet)\b"):
        return "apple_pay_or_google_pay"

    if _has(t, r"\b(pin|pin number|card code|cash machine code)\b"):
        if _has(t, r"\b(blocked|locked|lockout|unblock|unlock|too many|wrong attempts|incorrect attempts|tries)\b"):
            return "pin_blocked"
        return "change_pin"
    if _has(t, r"\b(passcode|pass code|password|login code|log in code)\b") and _has(t, r"\b(forgot|forgotten|lost|reset|remember|recover|access|change)\b"):
        return "passcode_forgotten"

    if _has(t, r"\b(close|closing|closed|terminate|termination|delete|deactivate|shut down|cancel)\b") and _has(t, r"\b(account|profile|membership)\b"):
        return "terminate_account"
    if _has(t, r"\b(change|edit|update|correct|modify|new|wrong)\b") and _has(t, r"\b(personal details|personal information|personal data|my name|surname|address|email|e mail|phone number|mobile number|date of birth|residential address)\b"):
        return "edit_personal_details"

    if _has(t, r"\b(refund|refunded|reimbursement)\b"):
        if missing or pending or _has(t, r"\b(how long|still|where|not in|not on|no refund|did not get)\b"):
            return "refund_not_showing_up"
        return "request_refund"

    if _has(t, r"\b(charged twice|charged me twice|charged two times|double charged|double charge|duplicate(?:d)? (?:payment|transaction|charge)|paid twice|taken twice|two identical|same (?:payment|transaction) twice|twice for)\b"):
        return "transaction_charged_twice"

    if direct_debit and unknown:
        return "direct_debit_payment_not_recognised"

    if card and _has(t, r"\b(expir\w*|expiry|expiration|renew(?:al|ing)?|out of date)\b"):
        return "card_about_to_expire"
    if card and _has(t, r"\b(activat\w*|enable my (?:new )?card|start using my (?:new )?card)\b"):
        return "activate_my_card"
    if _has(t, r"\b(contactless|tap(?:ping)? (?:to pay|my card|and pay)|tap payment|nfc)\b") and (card_failure or _has(t, r"\b(not|problem|issue|unable)\b")):
        return "contactless_not_working"

    if card and _has(t, r"\b(visa|mastercard|master card)\b"):
        return "visa_or_mastercard"
    if _has(t, r"\b(visa or mastercard|visa or master card|mastercard or visa)\b"):
        return "visa_or_mastercard"

    if disposable:
        if limit:
            return "disposable_card_limits"
        if card_failure and not _has(t, r"\b(get|create|order|issue)\b"):
            return "virtual_card_not_working"
        return "get_disposable_virtual_card"

    if _has(t, r"\b(automatic|automatically|auto|recurring|scheduled|schedule)\b") and (topup or _has(t, r"\b(add money|add funds|balance)\b")):
        return "automatic_top_up"

    if _has(t, r"\b(supported|accepted|which|what|types? of|kind of|can i use)\b") and _has(t, r"\b(cards? and currencies|currencies and cards?|cards? (?:can|are|do|to|for|used)|debit or credit card|credit or debit card)\b") and (topup or _has(t, r"\b(top up|fund|deposit|supported|accepted)\b")):
        return "supported_cards_and_currencies"

    if cheque or (cash and not withdrawal and _has(t, r"\b(deposit|top up|add|pay in|paid in|put|balance)\b")):
        if missing or pending or _has(t, r"\b(balance (?:has not|is not|not|unchanged)|not (?:been )?(?:added|credited|updated)|did not (?:show|appear))\b"):
            return "balance_not_updated_after_cheque_or_cash_deposit"
        return "top_up_by_cash_or_cheque"

    if withdrawal:
        if rate or (exchange and _has(t, r"\b(wrong|bad|incorrect|different|poor|unfair)\b")):
            return "wrong_exchange_rate_for_cash_withdrawal"
        if unknown:
            return "cash_withdrawal_not_recognised"
        if _has(t, r"\b(wrong amount|incorrect amount|less (?:cash|money|than)|not enough (?:cash|money)|did not (?:give|dispense)|gave me (?:less|no|the wrong)|dispensed (?:less|no|the wrong)|short(?:changed)?|amount (?:is|was) wrong|no cash|did not receive (?:the )?(?:cash|money))\b"):
            return "wrong_amount_of_cash_received"
        if declined or (fail and _has(t, r"\b(withdraw|withdrawal|cash|money)\b")):
            return "declined_cash_withdrawal"
        if pending:
            return "pending_cash_withdrawal"
        if fee:
            return "cash_withdrawal_charge"
        if atm:
            return "atm_support"
        if _has(t, r"\b(how|where|which|can i)\b"):
            return "atm_support"

    if rate and (card or payment) and not topup:
        return "card_payment_wrong_exchange_rate"
    if exchange:
        if fee:
            return "exchange_charge"
        if rate or _has(t, r"\b(rate|price|how much .* (?:worth|exchange)|what .* worth)\b"):
            return "exchange_rate"
        return "exchange_via_app"

    if _has(t, r"\b(countr(?:y|ies)|region|where (?:is|are) (?:you|your|the service)|live in|resident of|residency|available in|supported in)\b"):
        if card and _has(t, r"\b(use|accepted|work|pay|travel|abroad|overseas)\b"):
            return "card_acceptance"
        if not transfer and not payment:
            return "country_support"
    if _has(t, r"\b(currenc(?:y|ies)|fiat|gbp|eur|usd)\b") and _has(t, r"\b(support|supported|available|hold|keep|which|what|accept)\b") and not transfer:
        return "fiat_currency_support"

    if _has(t, r"\b(beneficiary|recipient|payee)\b") and _has(t, r"\b(not allowed|not supported|ineligible|prohibited|restricted|not eligible|cannot send|can not send|unable to send)\b"):
        return "beneficiary_not_allowed"
    if transfer and _has(t, r"\b(cancel|cancell?ing|cancell?ation|stop|recall|undo)\b"):
        return "cancel_transfer"

    incoming = _has(t, r"\b(into my account|to my account|into (?:the|this|my) account|to (?:the|this) account|incoming|to me|sent me|send me|receive|receiving|received|deposit|my balance|bank transfer to (?:my|the) account)\b")
    outgoing = _has(t, r"\b(outgoing|sent (?:a |the |my )?(?:transfer|payment|money|funds)|send(?:ing)? (?:a |the |my )?(?:transfer|payment|money|funds)|beneficiary|recipient|payee|to (?:another|someone|a friend|my friend|their account)\b")
    if (transfer or bank) and incoming and not outgoing:
        if missing or pending or _has(t, r"\b(balance (?:has not|is not|not|unchanged)|not (?:been )?(?:added|credited|updated)|did not (?:show|appear))\b"):
            return "balance_not_updated_after_bank_transfer"
        if fee:
            return "top_up_by_bank_transfer_charge"
        if _has(t, r"\b(someone|somebody|other people|receive|receiving|received|account details|iban|swift|send me)\b") and not topup and not _has(t, r"\b(from my (?:other )?bank|my bank account|transfer (?:money )?into)\b"):
            return "receiving_money"
        return "transfer_into_account"

    if topup or (_has(t, r"\b(deposit|adding funds|add funds)\b") and card):
        if _has(t, r"\b(verif\w*|authentication|authenticate|confirm (?:my )?card|confirmation code|verification code)\b"):
            return "verify_top_up"
        if limit:
            return "top_up_limits"
        if reversed_:
            return "top_up_reverted"
        if declined or fail:
            return "top_up_failed"
        if pending:
            return "pending_top_up"
        if fee:
            if bank and not card:
                return "top_up_by_bank_transfer_charge"
            return "top_up_by_card_charge"
        if bank and not card:
            return "transfer_into_account"
        return "topping_up_by_card"

    if _has(t, r"\b(verif\w*|confirm|authentication)\b") and card and _has(t, r"\b(top up|deposit|charge|code|fund|bank card)\b"):
        return "verify_top_up"

    if transfer or outgoing:
        if _has(t, r"\b(not allowed|not supported|prohibited|restricted)\b") and _has(t, r"\b(recipient|beneficiary|payee|country)\b"):
            return "beneficiary_not_allowed"
        if declined:
            return "declined_transfer"
        if fail or reversed_:
            return "failed_transfer"
        if fee:
            return "transfer_fee_charged"
        if (missing or _has(t, r"\b(not (?:yet )?(?:arrived|received)|has not (?:got|received)|have not (?:got|received))\b")) and outgoing:
            return "transfer_not_received_by_recipient"
        if pending:
            return "pending_transfer"
        if timing:
            return "transfer_timing"
        if incoming and not outgoing:
            return "transfer_into_account"
        return "pending_transfer"

    if _has(t, r"\b(receive money|receiving money|receive a payment|receive payments|account details|iban|bank details)\b"):
        return "receiving_money"

    if virtual and card:
        if card_failure or _has(t, r"\b(not accepted|not usable|not able to (?:pay|use))\b"):
            return "virtual_card_not_working"
        return "getting_virtual_card"

    if card and _has(t, r"\b(link|linking|connect|connecting|attach|add my card to (?:my )?account)\b"):
        return "card_linking"

    delivery = _has(t, r"\b(deliver\w*|ship\w*|post(?:ed|al|age)?|mail(?:ed)?|arriv\w*|ordered|order|dispatch\w*|track\w*|where is my card|where is the card)\b")
    if card and delivery:
        if missing or _has(t, r"\b(late|delayed|delay|still waiting|not here|never came|not come|where is|where's)\b"):
            return "card_arrival"
        if timing:
            return "card_delivery_estimate"
        if _has(t, r"\b(order|ordered|ordering|request)\b"):
            return "order_physical_card"
        return "card_arrival"

    if card and _has(t, r"\b(spare|extra|additional|second|another|multiple|more than one|two cards)\b") and not payment:
        return "getting_spare_card"

    if card and (payment or _has(t, r"\b(pay|paid|purchase|transaction)\b")):
        if unknown:
            return "card_payment_not_recognised"
        if declined:
            return "declined_card_payment"
        if reversed_:
            return "reverted_card_payment"
        if pending:
            return "pending_card_payment"
        if fee:
            if _has(t, r"\b(statement|extra|more than|different amount|additional amount|too much|higher amount)\b") and not _has(t, r"\b(fee|commission|surcharge)\b"):
                return "extra_charge_on_statement"
            return "card_payment_fee_charged"
        if card_failure:
            return "card_not_working"

    if _has(t, r"\b(statement|transaction|payment|purchase)\b") and _has(t, r"\b(extra charge|additional charge|charged extra|charged more|more than (?:i|the)|wrong amount|higher amount)\b"):
        return "extra_charge_on_statement"
    if payment and unknown:
        return "card_payment_not_recognised"
    if payment and declined:
        return "declined_card_payment"
    if payment and reversed_:
        return "reverted_card_payment"
    if payment and pending:
        return "pending_card_payment"

    if card:
        if card_failure:
            return "card_not_working"
        if _has(t, r"\b(accept\w*|where (?:can|could|do)|use (?:my |the )?card|pay (?:with|using)|abroad|overseas|merchant|online|shop|store)\b"):
            return "card_acceptance"
        if _has(t, r"\b(order|ordering|request)\b"):
            return "order_physical_card"
        if _has(t, r"\b(get|getting|obtain|receive|need|want|physical|plastic|new card)\b"):
            return "get_physical_card"
        if pending:
            return "pending_card_payment"

    if _has(t, r"\b(automatic|automatically)\b"):
        return "automatic_top_up"
    return _fallback(t)


def predict(state):
    return {"answer": _classify(_normalize(_text(state)))}