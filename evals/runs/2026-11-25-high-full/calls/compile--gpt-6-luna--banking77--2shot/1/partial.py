import re
import unicodedata

CATEGORIES = [
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
    "edit_personal_details", "exchange_charge", "exchange_rate", "exchange_via_app",
    "extra_charge_on_statement", "failed_transfer", "fiat_currency_support",
    "get_disposable_virtual_card", "get_physical_card", "getting_spare_card",
    "getting_virtual_card", "lost_or_stolen_card", "lost_or_stolen_phone",
    "order_physical_card", "passcode_forgotten", "pending_card_payment",
    "pending_cash_withdrawal", "pending_top_up", "pending_transfer", "pin_blocked",
    "receiving_money", "refund_not_showing_up", "request_refund",
    "reverted_card_payment", "supported_cards_and_currencies", "terminate_account",
    "top_up_by_bank_transfer_charge", "top_up_by_card_charge",
    "top_up_by_cash_or_cheque", "top_up_failed", "top_up_limits", "top_up_reverted",
    "topping_up_by_card", "transaction_charged_twice", "transfer_fee_charged",
    "transfer_into_account", "transfer_not_received_by_recipient", "transfer_timing",
    "unable_to_verify_identity", "verify_my_identity", "verify_source_of_funds",
    "verify_top_up", "virtual_card_not_working", "visa_or_mastercard",
    "why_verify_identity", "wrong_amount_of_cash_received",
    "wrong_exchange_rate_for_cash_withdrawal"
]

_RULES = {category: [] for category in CATEGORIES}


def _add(category, weight, *patterns):
    for pattern in patterns:
        _RULES[category].append((weight, re.compile(pattern)))


# Specific card and payment issues
_add("card_payment_not_recognised", 11,
     r"\b(unrecognised|unrecognized|unknown|unauthori[sz]ed|fraudulent)\s+(card\s+)?(payment|transaction|purchase)\b",
     r"\b(card\s+)?(payment|transaction|purchase)\s+(i\s+)?(do not|don t|did not|didn t)\s+recognise\b",
     r"\b(payment|transaction)\s+not\s+recognised\b",
     r"\bunknown card transaction\b")
_add("cash_withdrawal_not_recognised", 11,
     r"\b(unrecognised|unrecognized|unknown|unauthori[sz]ed|fraudulent)\s+(atm\s+)?(withdrawal|cash withdrawal)\b",
     r"\b(cash|atm)\s+withdrawal\s+(i\s+)?(do not|don t|did not|didn t)\s+recognise\b")
_add("direct_debit_payment_not_recognised", 11,
     r"\b(unrecognised|unrecognized|unknown|unauthori[sz]ed)\s+direct debit\b",
     r"\bdirect debit\s+(payment\s+)?not recognised\b",
     r"\bdirect debit\s+(i\s+)?(do not|don t|did not|didn t)\s+recognise\b")
_add("transaction_charged_twice", 11,
     r"\b(charged|billed|debited)\s+(twice|two times)\b",
     r"\b(double|duplicate|duplicated)\s+(charge|payment|transaction)\b",
     r"\bcharged twice\b", r"\bcharged two times\b")
_add("card_payment_wrong_exchange_rate", 11,
     r"\b(card|purchase|payment)\b.{0,35}\b(wrong|incorrect|bad|unfair)\b.{0,25}\b(exchange rate|conversion rate|currency conversion)\b",
     r"\b(exchange rate|conversion rate)\b.{0,30}\b(card|purchase|payment)\b")
_add("wrong_exchange_rate_for_cash_withdrawal", 12,
     r"\b(wrong|incorrect|bad|unfair)\b.{0,25}\b(exchange rate|conversion rate)\b.{0,30}\b(cash|atm|withdrawal)\b",
     r"\b(cash|atm)\s+withdrawal\b.{0,40}\b(exchange rate|conversion rate)\b")
_add("wrong_amount_of_cash_received", 12,
     r"\b(wrong|incorrect|different|less|short)\b.{0,30}\b(amount|cash|money)\b.{0,25}\b(withdraw|atm|received|dispens)\b",
     r"\b(atm|cash machine)\b.{0,35}\b(gave|dispensed|received)\b.{0,20}\b(wrong|less|incorrect)\b",
     r"\bwithdrawn\b.{0,25}\b(amount|cash)\b.{0,20}\b(wrong|incorrect)\b")
_add("card_payment_fee_charged", 10,
     r"\b(card|card payment|purchase)\b.{0,35}\b(fee|charge|commission)\b",
     r"\b(fee|commission)\b.{0,25}\b(card payment|card purchase|card transaction)\b")
_add("cash_withdrawal_charge", 10,
     r"\b(atm|cash|cash withdrawal|withdrawal)\b.{0,35}\b(fee|charge|commission)\b",
     r"\b(fee|charge|commission)\b.{0,25}\b(atm|cash withdrawal)\b")
_add("exchange_charge", 10,
     r"\b(exchange|currency conversion|convert(?:ing)?)\b.{0,30}\b(fee|charge|commission)\b",
     r"\b(fee|charge|commission)\b.{0,25}\b(exchange|currency conversion)\b")
_add("transfer_fee_charged", 10,
     r"\b(transfer|bank transfer|international transfer)\b.{0,35}\b(fee|charge|commission|cost)\b",
     r"\b(fee|charge|commission)\b.{0,25}\b(transfer|sending money)\b")
_add("top_up_by_bank_transfer_charge", 11,
     r"\b(bank transfer|bank)\b.{0,30}\b(top up|top-up|add money)\b.{0,30}\b(fee|charge|commission)\b",
     r"\b(top up|top-up|add money)\b.{0,30}\b(bank transfer|bank)\b.{0,25}\b(fee|charge)\b")
_add("top_up_by_card_charge", 11,
     r"\b(card|debit card|credit card)\b.{0,30}\b(top up|top-up|add money)\b.{0,30}\b(fee|charge|commission)\b",
     r"\b(top up|top-up|add money)\b.{0,30}\b(card)\b.{0,25}\b(fee|charge)\b")
_add("extra_charge_on_statement", 9,
     r"\b(extra|additional|unexpected|unexplained|mystery|unknown)\s+(charge|dollar|amount|fee|payment)\b",
     r"\b(charged|billed|debited)\s+(an?\s+)?(extra|additional|unexpected)\b",
     r"\b(extra|additional)\s+(money|amount)\s+(was\s+)?(taken|charged)\b",
     r"\bcharge on (my )?(account|statement)\b",
     r"\bwhy (was|were) i charged\b")
_add("declined_card_payment", 9,
     r"\b(card|card payment|purchase|payment)\b.{0,30}\b(declin(?:ed|ing)|refus(?:ed|al)|reject(?:ed)?)\b",
     r"\b(declin(?:ed|ing)|refus(?:ed|al)|reject(?:ed)?)\b.{0,25}\b(card|payment|purchase)\b",
     r"\bcard was declined\b")
_add("declined_cash_withdrawal", 10,
     r"\b(atm|cash|cash withdrawal|withdrawal)\b.{0,30}\b(declin(?:ed|ing)|fail(?:ed)?|reject(?:ed)?)\b",
     r"\b(declin(?:ed|ing)|fail(?:ed)?|reject(?:ed)?)\b.{0,25}\b(atm|cash withdrawal)\b")
_add("declined_transfer", 9,
     r"\b(transfer|bank transfer|money transfer)\b.{0,30}\b(declin(?:ed|ing)|reject(?:ed)?|refus(?:ed|al))\b",
     r"\b(declin(?:ed|ing)|reject(?:ed)?|refus(?:ed|al))\b.{0,25}\b(transfer|bank transfer)\b")
_add("failed_transfer", 8,
     r"\b(failed|failure|unsuccessful|did not go through)\b.{0,25}\b(transfer|bank transfer|payment)\b",
     r"\b(transfer|bank transfer)\b.{0,25}\b(failed|failure|unsuccessful)\b")
_add("cancel_transfer", 10,
     r"\b(cancel|cancell?ation|stop|undo|recall)\b.{0,30}\b(transfer|bank transfer|payment)\b",
     r"\b(transfer|bank transfer)\b.{0,30}\b(cancel|cancell?ation|stop|undo)\b")
_add("transfer_not_received_by_recipient", 10,
     r"\b(recipient|beneficiar(?:y|ies)|person i sent)\b.{0,40}\b(not received|hasn t received|haven t received|never received|missing)\b",
     r"\b(sent|made)\b.{0,30}\b(transfer|money)\b.{0,30}\b(not arrived|not received|recipient)\b",
     r"\btransfer\b.{0,30}\b(recipient|beneficiary)\b.{0,30}\b(not received|not arrived|missing)\b")
_add("pending_transfer", 8,
     r"\b(pending|processing|in progress|still going through)\b.{0,25}\b(transfer|bank transfer|payment)\b",
     r"\b(transfer|bank transfer)\b.{0,25}\b(pending|processing|in progress)\b",
     r"\boutgoing transaction\b", r"\bmy transfer is pending\b")
_add("transfer_timing", 7,
     r"\bhow long\b.{0,30}\b(transfer|send money|bank transfer)\b",
     r"\b(when|how soon)\b.{0,30}\b(transfer|money)\b.{0,30}\b(arrive|reach|show up|come through)\b",
     r"\btransfer\b.{0,30}\b(take|taking)\b.{0,20}\b(long|time)\b")
_add("beneficiary_not_allowed", 10,
     r"\b(beneficiar(?:y|ies)|recipient|payee)\b.{0,35}\b(not allowed|not permitted|can t|cannot|unable|not supported)\b",
     r"\b(can t|cannot|unable to)\b.{0,25}\b(add|select|use)\b.{0,20}\b(beneficiar(?:y|ies)|recipient|payee)\b")
_add("transfer_into_account", 7,
     r"\b(transfer|send|move)\b.{0,25}\b(money|funds)\b.{0,25}\b(into|to)\b.{0,20}\b(account|revolut)\b",
     r"\b(bank transfer)\b.{0,25}\b(into|to)\b.{0,20}\b(my )?account\b",
     r"\bhow (do i|can i)\b.{0,30}\b(transfer|send)\b.{0,20}\b(into|to)\b.{0,20}\b(account|revolut)\b")
_add("receiving_money", 7,
     r"\b(receive|receiving|get|accept)\b.{0,20}\b(money|funds|payment)\b",
     r"\bhow (can|do) i\b.{0,25}\b(receive|get)\b.{0,15}\b(money|funds)\b",
     r"\b(details| iban|account number)\b.{0,20}\b(receive|incoming)\b")
_add("balance_not_updated_after_bank_transfer", 10,
     r"\b(balance|money|funds)\b.{0,35}\b(not|hasn t|haven t|didn t|did not)\b.{0,25}\b(show|appear|arrive|update|reflect)\b.{0,30}\b(bank )?transfer\b",
     r"\b(bank )?transfer\b.{0,35}\b(balance|money|funds)\b.{0,30}\b(not updated|not showing|missing|hasn t arrived)\b")
_add("balance_not_updated_after_cheque_or_cash_deposit", 10,
     r"\b(balance|money|funds|deposit)\b.{0,35}\b(not|hasn t|haven t|didn t|did not)\b.{0,25}\b(show|appear|arrive|update|reflect)\b.{0,30}\b(cheque|check|cash deposit)\b",
     r"\b(cheque|check|cash deposit)\b.{0,35}\b(balance|money|funds)\b.{0,30}\b(not updated|not showing|missing)\b")
_add("pending_card_payment", 8,
     r"\b(pending|processing|authori[sz]ation)\b.{0,25}\b(card payment|card transaction|purchase|payment)\b",
     r"\b(card payment|card transaction|purchase)\b.{0,25}\b(pending|processing)\b")
_add("pending_cash_withdrawal", 9,
     r"\b(pending|processing)\b.{0,25}\b(cash withdrawal|atm withdrawal|withdrawal)\b",
     r"\b(cash withdrawal|atm withdrawal|withdrawal)\b.{0,25}\b(pending|processing)\b")
_add("pending_top_up", 9,
     r"\b(pending|processing)\b.{0,20}\b(top up|top-up|topup|adding money)\b",
     r"\b(top up|top-up|topup)\b.{0,20}\b(pending|processing)\b")
_add("reverted_card_payment", 9,
     r"\b(card payment|card transaction|purchase)\b.{0,30}\b(reverted|reversal|reversed|refunded back)\b",
     r"\b(reverted|reversed)\b.{0,25}\b(card payment|card transaction|purchase)\b")
_add("refund_not_showing_up", 10,
     r"\b(refund|money back)\b.{0,35}\b(not (showing|appearing|arrived|received)|missing|where is|hasn t|haven t)\b",
     r"\b(refunded|refund)\b.{0,25}\b(not (in|on|showing)|missing|not received)\b")
_add("request_refund", 8,
     r"\b(request|ask for|get|want|need)\b.{0,20}\b(a )?refund\b",
     r"\b(refund|money back)\b.{0,20}\b(request|claim|ask)\b")
_add("top_up_reverted", 9,
     r"\b(top up|top-up|topup)\b.{0,30}\b(reverted|reversed|returned|sent back)\b",
     r"\b(reverted|reversed|returned)\b.{0,25}\b(top up|top-up|topup)\b")
_add("top_up_failed", 8,
     r"\b(top up|top-up|topup|add money)\b.{0,25}\b(failed|failure|declined|did not work|not working|unsuccessful)\b",
     r"\b(failed|declined|unsuccessful)\b.{0,25}\b(top up|top-up|topup)\b")
_add("top_up_by_cash_or_cheque", 9,
     r"\b(top up|top-up|add money|deposit)\b.{0,30}\b(cash|cheque|check)\b",
     r"\b(cash|cheque|check)\b.{0,25}\b(top up|top-up|add money|deposit)\b")
_add("top_up_limits", 9,
     r"\b(top up|top-up|topup|add money)\b.{0,30}\b(limit|maximum|minimum|how much|amount limit)\b",
     r"\b(limit|maximum|minimum)\b.{0,25}\b(top up|top-up|topup)\b")
_add("automatic_top_up", 10,
     r"\b(automatic|automatically|auto)\b.{0,20}\b(top up|top-up|topup|add money)\b",
     r"\b(top up|top-up|topup)\b.{0,20}\b(automatic|automatically|auto)\b")
_add("topping_up_by_card", 7,
     r"\b(top up|top-up|topup|add money)\b.{0,25}\b(card|debit card|credit card)\b",
     r"\b(card|debit card|credit card)\b.{0,25}\b(top up|top-up|topup|add money)\b")
_add("verify_top_up", 9,
     r"\b(verify|verification|confirm|proof)\b.{0,25}\b(top up|top-up|topup|deposit)\b",
     r"\b(top up|top-up|topup)\b.{0,25}\b(verify|verification|confirm|proof)\b")

# Identity and account administration
_add("unable_to_verify_identity", 10,
     r"\b(can t|cannot|unable to|failed to)\b.{0,25}\b(verify|verification|confirm)\b.{0,20}\b(identity|id|myself)\b",
     r"\b(identity verification)\b.{0,25}\b(failed|not working|problem|issue)\b")
_add("verify_source_of_funds", 10,
     r"\b(source of funds|source of wealth|proof of funds|origin of (my )?money)\b",
     r"\b(verify|verification|prove|proof)\b.{0,25}\b(funds|wealth|income)\b")
_add("why_verify_identity", 9,
     r"\b(why|reason)\b.{0,30}\b(verify|verification|confirm)\b.{0,20}\b(identity|id|myself)\b",
     r"\bwhy (do i|must i|are you asking me to)\b.{0,25}\b(verify|identity|id)\b")
_add("verify_my_identity", 8,
     r"\b(verify|verification|confirm|prove)\b.{0,20}\b(my )?(identity|id|who i am)\b",
     r"\b(identity|id)\b.{0,20}\b(verification|verify|confirm)\b")
_add("passcode_forgotten", 10,
     r"\b(forgot|forgotten|forget|don t remember|cannot remember|can t remember)\b.{0,25}\b(passcode|pass code|app code|login code)\b",
     r"\b(passcode|pass code)\b.{0,25}\b(forgot|forgotten|reset|can t access)\b")
_add("pin_blocked", 10,
     r"\b(pin|card pin)\b.{0,25}\b(blocked|locked|tries exceeded|blocked after)\b",
     r"\b(blocked|locked)\b.{0,20}\b(pin|card pin)\b")
_add("change_pin", 8,
     r"\b(change|reset|set|update)\b.{0,20}\b(pin|card pin)\b",
     r"\b(pin|card pin)\b.{0,20}\b(change|reset|set|update)\b")
_add("edit_personal_details", 8,
     r"\b(change|edit|update|correct)\b.{0,25}\b(personal details|personal information|address|phone number|email|name|date of birth)\b",
     r"\b(update|change)\b.{0,20}\b(my )?(address|phone|email|name)\b")
_add("terminate_account", 9,
     r"\b(close|delete|terminate|deactivate|cancel)\b.{0,25}\b(account|my account)\b",
     r"\b(account)\b.{0,20}\b(close|delete|terminate|deactivate)\b",
     r"\bstop using\b.{0,20}\b(account|service)\b")

# Card ordering, status, and functionality
_add("lost_or_stolen_phone", 11,
     r"\b(lost|stolen|missing)\b.{0,20}\b(phone|mobile|smartphone|device)\b",
     r"\b(phone|mobile|smartphone)\b.{0,20}\b(lost|stolen)\b")
_add("lost_or_stolen_card", 11,
     r"\b(lost|stolen|missing)\b.{0,20}\b(card|bank card|debit card)\b",
     r"\b(card|bank card|debit card)\b.{0,20}\b(lost|stolen)\b")
_add("compromised_card", 10,
     r"\b(compromised|hacked|copied|skimmed)\b.{0,20}\b(card|card details)\b",
     r"\b(card|card details)\b.{0,20}\b(compromised|hacked|copied|skimmed)\b",
     r"\bsomeone (has )?(my )?card details\b")
_add("card_swallowed", 10,
     r"\b(atm|cash machine)\b.{0,25}\b(swallowed|kept|retained)\b.{0,15}\b(card)\b",
     r"\b(card)\b.{0,20}\b(swallowed|retained|stuck in)\b.{0,20}\b(atm|cash machine)\b")
_add("activate_my_card", 9,
     r"\b(activate|activation|activate my)\b.{0,20}\b(card)\b",
     r"\b(card)\b.{0,20}\b(activate|activation)\b")
_add("card_about_to_expire", 9,
     r"\b(card)\b.{0,25}\b(expir(?:e|es|ing|ation)|expires soon|about to expire)\b",
     r"\b(expiring|expires soon)\b.{0,20}\b(card)\b")
_add("card_arrival", 7,
     r"\b(card)\b.{0,20}\b(arriv(?:e|al|ed)|hasn t arrived|not arrived)\b",
     r"\b(where is|waiting for)\b.{0,20}\b(card)\b")
_add("card_delivery_estimate", 8,
     r"\b(delivery|deliver|shipping)\b.{0,30}\b(how long|when|estimate|take|arrive)\b",
     r"\b(how long|when)\b.{0,25}\b(card)\b.{0,20}\b(arrive|deliver)\b",
     r"\b(card delivery|delivery of my card)\b")
_add("getting_spare_card", 9,
     r"\b(spare|replacement|second)\b.{0,20}\b(card)\b",
     r"\b(another|extra)\b.{0,20}\b(card)\b")
_add("order_physical_card", 9,
     r"\b(order|request|buy)\b.{0,20}\b(physical|plastic|bank|debit)\s+card\b",
     r"\b(order|request)\b.{0,20}\b(card)\b")
_add("get_physical_card", 8,
     r"\b(get|obtain|receive)\b.{0,20}\b(physical|plastic)\s+card\b",
     r"\bphysical card\b")
_add("get_disposable_virtual_card", 10,
     r"\b(get|create|make|obtain|order)\b.{0,25}\b(disposable|single use|single-use)\b.{0,20}\b(virtual|digital)?\s*card\b",
     r"\b(disposable|single use|single-use)\s+(virtual\s+)?card\b")
_add("getting_virtual_card", 8,
     r"\b(get|create|make|obtain|order)\b.{0,20}\b(virtual|digital)\s+card\b",
     r"\b(virtual|digital)\s+card\b.{0,20}\b(get|create|make|obtain)\b")
_add("card_linking", 8,
     r"\b(link|linking|connect|add)\b.{0,25}\b(card)\b.{0,25}\b(account|app|revolut)\b",
     r"\b(card)\b.{0,25}\b(link|linked|connect|add)\b.{0,20}\b(account|app)\b")
_add("contactless_not_working", 10,
     r"\b(contactless|tap to pay|tap payment|paywave)\b.{0,30}\b(not working|doesn t work|won t work|fail|problem|issue|declined)\b",
     r"\b(not working|doesn t work|won t work|fail)\b.{0,25}\b(contactless|tap to pay)\b")
_add("virtual_card_not_working", 10,
     r"\b(virtual|digital)\s+card\b.{0,30}\b(not working|doesn t work|won t work|fail|problem|issue|declined)\b",
     r"\b(not working|doesn t work|won t work)\b.{0,25}\b(virtual|digital)\s+card\b")
_add("card_not_working", 8,
     r"\b(card)\b.{0,25}\b(not working|doesn t work|won t work|broken|problem|issue)\b",
     r"\b(can t|cannot|unable to)\b.{0,20}\b(use|pay with)\b.{0,15}\b(card)\b")
_add("apple_pay_or_google_pay", 9,
     r"\b(apple pay|google pay|apple wallet|google wallet|gpay)\b",
     r"\b(add|use|pay with)\b.{0,20}\b(apple pay|google pay)\b")
_add("atm_support", 8,
     r"\b(atm|cash machine)\b.{0,30}\b(support|supported|use|withdraw|available)\b",
     r"\b(where|which)\b.{0,25}\b(atm|cash machine)\b")
_add("card_acceptance", 8,
     r"\b(where|which places|what places|shops)\b.{0,25}\b(accept|accepted)\b.{0,20}\b(card)\b",
     r"\b(card)\b.{0,20}\b(accepted|acceptance)\b",
     r"\b(can i pay)\b.{0,20}\b(card)\b")
_add("visa_or_mastercard", 9,
     r"\b(visa|mastercard|master card)\b",
     r"\b(which card network|card network)\b")
_add("supported_cards_and_currencies", 8,
     r"\b(supported|support)\b.{0,25}\b(cards|currencies|currency)\b",
     r"\b(which|what)\b.{0,25}\b(cards|currencies|currency)\b.{0,20}\b(support|supported|use)\b")
_add("disposable_card_limits", 9,
     r"\b(disposable|single use|single-use)\b.{0,25}\b(card)\b.{0,25}\b(limit|limits|maximum|how many)\b",
     r"\b(limit|limits)\b.{0,20}\b(disposable|single use)\b")
_add("card_not_working", 5,
     r"\bmy card\b")
_add("fiat_currency_support", 8,
     r"\b(fiat currency|fiat currencies|fiat money)\b",
     r"\b(supported|support)\b.{0,20}\b(fiat|currency|currencies)\b")
_add("country_support", 7,
     r"\b(supported|support|available)\b.{0,25}\b(country|countries|live|reside)\b",
     r"\b(which|what)\b.{0,25}\b(country|countries)\b.{0,20}\b(available|supported|use)\b")
_add("age_limit", 8,
     r"\b(age limit|minimum age|old enough|how old|underage|minimum age requirement)\b",
     r"\b(age|years old)\b.{0,25}\b(open|create|sign up|account)\b")

# Currency exchange and miscellaneous service questions
_add("exchange_via_app", 9,
     r"\b(exchange|convert|conversion)\b.{0,25}\b(in the app|via the app|using the app|in app)\b",
     r"\bhow (do i|can i)\b.{0,20}\b(exchange|convert)\b.{0,20}\b(currency|money)\b")
_add("exchange_rate", 8,
     r"\b(exchange rate|conversion rate|currency rate)\b",
     r"\b(rate)\b.{0,20}\b(exchange|currency)\b")
_add("top_up_by_cash_or_cheque", 5,
     r"\bcheque deposit\b")
_add("automatic_top_up", 5,
     r"\bauto top up\b")
_add("country_support", 4,
     r"\b(country|countries)\b")
_add("supported_cards_and_currencies", 4,
     r"\b(supported currencies|currencies supported|which currencies)\b")
_add("visa_or_mastercard", 4,
     r"\bvisa or mastercard\b")


def _normalize(value):
    if not isinstance(value, str):
        value = str(value)
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower().replace("’", "'")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def predict(state) -> dict:
    text = _normalize(state)
    scores = {category: 0 for category in CATEGORIES}
    for category in CATEGORIES:
        for weight, pattern in _RULES[category]:
            if pattern.search(text):
                scores[category] = max(scores[category], weight)

    # Resolve common broad-topic overlaps in favor of the more specific issue.
    if "pending" in text or "processing" in text or "in progress" in text:
        if "transfer" in text and scores["pending_transfer"]:
            scores["pending_transfer"] += 2
        if ("card" in text or "purchase" in text) and scores["pending_card_payment"]:
            scores["pending_card_payment"] += 2
        if ("top up" in text or "topup" in text) and scores["pending_top_up"]:
            scores["pending_top_up"] += 2
        if ("withdrawal" in text or "atm" in text) and scores["pending_cash_withdrawal"]:
            scores["pending_cash_withdrawal"] += 2

    if ("transfer" in text or "bank transfer" in text) and (
        "recipient" in text or "beneficiary" in text
    ):
        if any(word in text for word in ("not received", "not arrived", "missing", "hasn t received")):
            scores["transfer_not_received_by_recipient"] += 3

    # Stable tie-breaking uses the declared category order.
    answer = max(CATEGORIES, key=lambda category: scores[category])
    if scores[answer] == 0:
        answer = "pending_transfer"
    return {"answer": answer}