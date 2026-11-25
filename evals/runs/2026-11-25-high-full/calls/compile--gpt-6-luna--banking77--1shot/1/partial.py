import re
import unicodedata

CATEGORIES = (
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
    "wrong_exchange_rate_for_cash_withdrawal",
)

def _normalize(value):
    value = unicodedata.normalize("NFKD", value.lower())
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())

_RULES = {}

def _add(category, phrases, weight=6):
    _RULES.setdefault(category, [])
    for phrase in phrases:
        normalized = _normalize(phrase)
        if normalized:
            _RULES[category].append((normalized, weight))

# Direct category names are useful cues, but more detailed phrases below resolve
# cases where several related banking topics appear in the same message.
for _category in CATEGORIES:
    _add(_category, [_category.replace("_", " ")], 11)

_add("activate_my_card", [
    "activate my card", "activate card", "card activation", "card is not activated",
    "how do i activate my new card", "enable my card",
], 8)
_add("age_limit", ["age limit", "minimum age", "old enough to open an account",
                   "age requirement", "how old do i need to be"], 8)
_add("apple_pay_or_google_pay", [
    "apple pay", "google pay", "google wallet", "add card to apple wallet",
    "add card to google wallet", "wallet payment", "pay with my phone",
], 8)
_add("atm_support", [
    "atm support", "supported atm", "which atms", "where can i withdraw cash",
    "cash machine support", "atm near", "atm location", "use my card at an atm",
], 7)
_add("automatic_top_up", [
    "automatic top up", "auto top up", "automatic top-up", "automatically top up",
    "scheduled top up", "recurring top up", "top up automatically",
], 8)
_add("balance_not_updated_after_bank_transfer", [
    "bank transfer has not arrived", "bank transfer not showing", "transfer not showing in my balance",
    "balance not updated after bank transfer", "money sent by bank transfer not showing",
    "bank transfer missing from balance", "bank transfer has not been credited",
], 9)
_add("balance_not_updated_after_cheque_or_cash_deposit", [
    "cash deposit not showing", "cheque deposit not showing", "check deposit not showing",
    "cash deposit missing", "cheque has not cleared", "check has not cleared",
    "balance not updated after cash deposit", "balance not updated after cheque",
    "cash or cheque deposit not credited",
], 9)
_add("beneficiary_not_allowed", [
    "beneficiary not allowed", "cannot add beneficiary", "can't add beneficiary",
    "beneficiary is blocked", "recipient not allowed", "cannot add recipient",
    "payee not allowed", "beneficiary rejected",
], 8)
_add("cancel_transfer", [
    "cancel transfer", "cancel a bank transfer", "stop a transfer", "reverse a transfer",
    "undo transfer", "recall a transfer", "cancel my payment transfer",
], 8)
_add("card_about_to_expire", [
    "card about to expire", "card is expiring", "card expires soon", "expiring card",
    "card expiry", "card expiration", "card expired soon",
], 8)
_add("card_acceptance", [
    "where is my card accepted", "where can i use my card", "places that accept my card",
    "card acceptance", "which merchants accept", "will this card be accepted",
    "card accepted abroad", "shops that accept my card",
], 8)
_add("card_arrival", [
    "where is my card", "card has not arrived", "card hasn't arrived", "card never arrived",
    "waiting for my card", "when will my card arrive", "my card did not arrive",
    "card arrival", "physical card not received",
], 8)
_add("card_delivery_estimate", [
    "card delivery estimate", "delivery time for my card", "how long does card delivery take",
    "card delivery date", "estimated card delivery", "track my card delivery",
    "card shipping time", "when should my card be delivered",
], 9)
_add("card_linking", [
    "link my card", "link a card", "card linking", "connect my card",
    "add another bank card", "add a card to my account", "link external card",
], 8)
_add("card_not_working", [
    "card not working", "card doesn't work", "card does not work", "card stopped working",
    "cannot use my card", "can't use my card", "card is unusable", "card malfunction",
    "card won't work",
], 7)
_add("card_payment_fee_charged", [
    "fee on card payment", "card payment fee", "charged a fee for card payment",
    "fee charged for a card purchase", "card purchase fee",
], 8)
_add("card_payment_not_recognised", [
    "card payment not recognised", "unrecognized card payment", "unrecognised card payment",
    "don't recognise this card payment", "do not recognize this card payment",
    "unknown card transaction", "unknown card payment", "fraudulent card payment",
    "card purchase i did not make",
], 9)
_add("card_payment_wrong_exchange_rate", [
    "wrong exchange rate on card payment", "card payment exchange rate is wrong",
    "wrong rate for card purchase", "card purchase converted at wrong rate",
    "exchange rate on my card transaction",
], 9)
_add("card_swallowed", [
    "card swallowed", "atm swallowed my card", "cash machine kept my card",
    "atm retained my card", "machine ate my card", "card retained by atm",
], 9)
_add("cash_withdrawal_charge", [
    "cash withdrawal charge", "atm withdrawal fee", "charged for cash withdrawal",
    "fee for withdrawing cash", "cash machine fee", "atm charged me a fee",
], 8)
_add("cash_withdrawal_not_recognised", [
    "cash withdrawal not recognised", "unrecognized atm withdrawal",
    "unrecognised cash withdrawal", "withdrawal i did not make",
    "unknown atm transaction", "cash withdrawal fraud",
], 9)
_add("change_pin", [
    "change my pin", "change card pin", "set a new pin", "update my pin",
    "change pin", "forgot my card pin and change it",
], 8)
_add("compromised_card", [
    "card details compromised", "card has been compromised", "someone has my card details",
    "card details stolen", "card security compromised", "card was hacked",
    "someone copied my card",
], 9)
_add("contactless_not_working", [
    "contactless not working", "contactless doesn't work", "tap to pay not working",
    "contactless payment declined", "can't use contactless", "contactless stopped working",
    "tap payment not working",
], 9)
_add("country_support", [
    "supported countries", "country supported", "is my country supported",
    "available in my country", "countries can use this service", "country availability",
    "which countries are supported",
], 8)
_add("declined_card_payment", [
    "card payment declined", "card payment was declined", "card purchase declined",
    "my card was declined", "payment with my card declined", "merchant declined my card",
    "card transaction declined",
], 9)
_add("declined_cash_withdrawal", [
    "cash withdrawal declined", "atm withdrawal declined", "atm declined my withdrawal",
    "cash machine declined", "unable to withdraw cash because it was declined",
], 9)
_add("declined_transfer", [
    "transfer declined", "bank transfer declined", "my transfer was declined",
    "payment transfer rejected", "transfer rejected", "outgoing transfer declined",
], 9)
_add("direct_debit_payment_not_recognised", [
    "direct debit not recognised", "unrecognized direct debit", "unknown direct debit",
    "direct debit i did not set up", "direct debit i did not authorize",
    "don't recognise this direct debit", "unauthorised direct debit",
], 9)
_add("disposable_card_limits", [
    "disposable card limit", "limits on disposable cards", "disposable virtual card limits",
    "how many disposable cards", "disposable card spending limit",
], 8)
_add("edit_personal_details", [
    "change my address", "update my address", "change personal details",
    "edit personal details", "update my name", "change my phone number",
    "update my personal information", "change my email address",
], 8)
_add("exchange_charge", [
    "exchange fee", "currency exchange charge", "charged for exchanging currency",
    "fee for exchanging money", "exchange commission", "foreign exchange fee",
], 8)
_add("exchange_rate", [
    "exchange rate", "currency conversion rate", "what rate will i get",
    "current conversion rate", "rate for exchanging currencies",
], 7)
_add("exchange_via_app", [
    "exchange currency in the app", "exchange money in the app", "how to exchange currency",
    "convert money in app", "exchange via app", "convert currencies in the app",
    "make an exchange in the app",
], 8)
_add("extra_charge_on_statement", [
    "extra charge on my statement", "additional charge on statement",
    "unexpected charge on statement", "extra amount on statement",
    "charge on statement i don't understand", "fee shown on my statement",
], 8)
_add("failed_transfer", [
    "failed transfer", "transfer failed", "bank transfer failed", "my transfer failed",
    "transfer was unsuccessful", "outgoing transfer failed", "payment transfer failed",
], 9)
_add("fiat_currency_support", [
    "fiat currency support", "supported fiat currencies", "which currencies can i hold",
    "currencies available in my account", "does the account support euros",
    "supported account currencies", "currencies supported for balances",
], 8)
_add("get_disposable_virtual_card", [
    "get a disposable virtual card", "create disposable virtual card",
    "how to get a disposable card", "make a disposable card", "disposable card",
], 8)
_add("get_physical_card", [
    "get a physical card", "how do i get a physical card", "obtain physical card",
    "need a physical card", "request a physical card",
], 7)
_add("getting_spare_card", [
    "get a spare card", "spare card", "additional physical card",
    "another physical card", "second card", "extra card for my account",
], 8)
_add("getting_virtual_card", [
    "get a virtual card", "create a virtual card", "how to get virtual card",
    "request virtual card", "make a virtual card", "virtual card availability",
], 8)
_add("lost_or_stolen_card", [
    "lost my card", "card was lost", "card is lost", "stolen card", "card was stolen",
    "card has been stolen", "can't find my card", "cannot find my card",
], 10)
_add("lost_or_stolen_phone", [
    "lost my phone", "phone was stolen", "stolen phone", "lost or stolen phone",
    "my phone is missing", "someone stole my phone",
], 10)
_add("order_physical_card", [
    "order a physical card", "order physical card", "place an order for a card",
    "order a new card", "how do i order a card", "physical card order",
], 8)
_add("passcode_forgotten", [
    "forgot my passcode", "forgotten passcode", "can't remember my passcode",
    "cannot remember my passcode", "forgot app passcode", "reset my passcode",
    "locked out because i forgot my passcode",
], 9)
_add("pending_card_payment", [
    "pending card payment", "card payment pending", "card transaction pending",
    "card purchase pending", "payment is still pending on my card",
    "pending card transaction",
], 9)
_add("pending_cash_withdrawal", [
    "pending cash withdrawal", "atm withdrawal pending", "cash withdrawal is pending",
    "withdrawal still pending", "atm transaction pending", "pending atm transaction",
], 9)
_add("pending_top_up", [
    "pending top up", "top up pending", "top-up pending", "top up is still pending",
    "pending card top up", "top up processing",
], 9)
_add("pending_transfer", [
    "pending transfer", "transfer pending", "transfer is pending", "outgoing transaction",
    "outgoing transfer", "transfer still processing", "transfer processing",
    "money sent is pending", "payment transfer pending", "where is my outgoing payment",
], 8)
_add("pin_blocked", [
    "pin blocked", "blocked pin", "pin is blocked", "entered pin incorrectly too many times",
    "card pin locked", "unblock my pin", "pin attempts exceeded",
], 9)
_add("receiving_money", [
    "receiving money", "receive money", "how can someone pay me",
    "how to receive a payment", "details to receive money", "receive a salary",
    "someone sending me money", "get paid into my account",
], 7)
_add("refund_not_showing_up", [
    "refund not showing", "refund hasn't arrived", "refund has not arrived",
    "refund missing", "waiting for my refund", "refund not received",
    "where is my refund", "refund not in my balance",
], 9)
_add("request_refund", [
    "request a refund", "how to get a refund", "ask for a refund",
    "want to claim a refund", "get my money back from a merchant",
    "merchant won't refund me", "refund from a purchase",
], 8)
_add("reverted_card_payment", [
    "card payment reverted", "reverted card payment", "card payment reversed",
    "card transaction reversed", "card payment was reversed", "reversal of card payment",
], 9)
_add("supported_cards_and_currencies", [
    "supported cards and currencies", "which cards are supported",
    "what cards can i use to top up", "supported card types", "which currency can my card use",
    "currencies supported for card payments", "card and currency support",
], 8)
_add("terminate_account", [
    "close my account", "delete my account", "terminate my account",
    "cancel my account", "shut down my account", "deactivate my account permanently",
], 9)
_add("top_up_by_bank_transfer_charge", [
    "bank transfer top up fee", "fee for topping up by bank transfer",
    "charge for bank transfer top up", "bank transfer deposit charge",
], 9)
_add("top_up_by_card_charge", [
    "card top up fee", "fee for topping up by card", "charge for card top up",
    "fee charged when adding money by card",
], 9)
_add("top_up_by_cash_or_cheque", [
    "top up by cash", "top up by cheque", "top up by check",
    "add money with cash", "add money with a cheque", "cash or cheque top up",
    "deposit a cheque into my account",
], 8)
_add("top_up_failed", [
    "top up failed", "top-up failed", "adding money failed", "card top up failed",
    "could not top up", "unable to add money", "top up unsuccessful",
], 9)
_add("top_up_limits", [
    "top up limit", "top-up limits", "maximum top up", "minimum top up",
    "how much can i top up", "limits for adding money", "deposit limit",
], 8)
_add("top_up_reverted", [
    "top up reverted", "top-up reversed", "top up was reversed",
    "card top up reversed", "top up returned to my bank",
], 9)
_add("topping_up_by_card", [
    "top up by card", "top up with a card", "add money with my card",
    "add money by debit card", "add money by credit card", "topping up by card",
], 7)
_add("transaction_charged_twice", [
    "charged twice", "charged two times", "duplicate transaction",
    "duplicate card payment", "same payment twice", "payment taken twice",
    "double charged", "transaction appears twice",
], 10)
_add("transfer_fee_charged", [
    "transfer fee", "fee for a transfer", "charged for sending a transfer",
    "fee charged on my bank transfer", "international transfer charge",
    "transfer commission",
], 8)
_add("transfer_into_account", [
    "transfer into my account", "bank transfer into my account",
    "add money by bank transfer", "send a bank transfer to my account",
    "how to transfer money into my account", "details for a bank transfer",
    "make a transfer to my account",
], 7)
_add("transfer_not_received_by_recipient", [
    "recipient has not received my transfer", "recipient hasn't received the money",
    "transfer not received by recipient", "beneficiary did not receive transfer",
    "money has not reached the recipient", "recipient says they have not been paid",
    "sent transfer but recipient has not received it",
], 9)
_add("transfer_timing", [
    "how long does a transfer take", "transfer timing", "when will my transfer arrive",
    "time for a bank transfer", "how long for money to transfer",
    "transfer processing time", "when should the transfer reach",
], 8)
_add("unable_to_verify_identity", [
    "unable to verify identity", "can't verify my identity", "cannot verify my identity",
    "identity verification failed", "failed identity check", "verification keeps failing",
    "unable to complete identity check",
], 9)
_add("verify_my_identity", [
    "verify my identity", "how to verify my identity", "identity verification",
    "verify my account", "complete identity verification", "upload identity documents",
    "prove my identity",
], 7)
_add("verify_source_of_funds", [
    "verify source of funds", "source of funds", "proof of funds",
    "where did my money come from", "document source of wealth",
    "asked to prove where my money came from",
], 8)
_add("verify_top_up", [
    "verify top up", "verify my top up", "top up verification",
    "confirm a card top up", "top up requires verification", "verify this deposit",
], 9)
_add("virtual_card_not_working", [
    "virtual card not working", "virtual card doesn't work", "virtual card declined",
    "can't use my virtual card", "cannot use virtual card",
], 9)
_add("visa_or_mastercard", [
    "visa or mastercard", "visa or mastercard", "is it visa or mastercard",
    "visa card or mastercard", "what card network", "card network",
], 8)
_add("why_verify_identity", [
    "why verify my identity", "why do you need my identity", "reason for identity verification",
    "why am i being asked to verify", "why do i need to verify my account",
    "why is identity verification required",
], 9)
_add("wrong_amount_of_cash_received", [
    "wrong amount of cash", "atm gave me the wrong amount", "received less cash",
    "cash machine gave me less", "cash withdrawal amount is wrong",
    "atm dispensed the wrong amount", "cash received does not match",
], 9)
_add("wrong_exchange_rate_for_cash_withdrawal", [
    "wrong exchange rate for cash withdrawal", "atm withdrawal exchange rate",
    "wrong rate on cash withdrawal", "cash withdrawal converted at wrong rate",
    "exchange rate for atm withdrawal is wrong",
], 10)

def _text_from_state(state):
    if isinstance(state, str):
        return state
    if isinstance(state, dict):
        for key in ("text", "message", "query", "question", "content"):
            value = state.get(key)
            if isinstance(value, str):
                return value
        return " ".join(value for value in state.values() if isinstance(value, str))
    if isinstance(state, (list, tuple)):
        return " ".join(value for value in state if isinstance(value, str))
    return ""

def predict(state) -> dict:
    text = _normalize(_text_from_state(state))
    padded = " " + text + " "
    scores = {category: 0 for category in CATEGORIES}

    for category, rules in _RULES.items():
        best = 0
        total = 0
        for phrase, weight in rules:
            if " " + phrase + " " in padded:
                best = max(best, weight)
                total += weight
        if best:
            scores[category] = best + min(total - best, 3)

    # Contextual combinations distinguish short descriptions from generic mentions.
    words = set(text.split())
    def has_any(*terms):
        return any(term in words for term in terms)

    if has_any("pending", "processing", "processing") or "in progress" in padded:
        for category, entities in (
            ("pending_transfer", ("transfer", "transaction", "outgoing", "payment")),
            ("pending_card_payment", ("card", "purchase")),
            ("pending_cash_withdrawal", ("atm", "withdrawal", "cash")),
            ("pending_top_up", ("top", "up", "deposit")),
        ):
            if any(entity in words for entity in entities):
                scores[category] += 5

    if has_any("declined", "rejected"):
        for category, entities in (
            ("declined_card_payment", ("card", "purchase")),
            ("declined_cash_withdrawal", ("atm", "withdrawal", "cash")),
            ("declined_transfer", ("transfer",)),
        ):
            if any(entity in words for entity in entities):
                scores[category] += 5

    if has_any("fee", "charge", "charged", "commission"):
        for category, entities in (
            ("card_payment_fee_charged", ("card", "purchase")),
            ("cash_withdrawal_charge", ("atm", "withdrawal", "cash")),
            ("transfer_fee_charged", ("transfer",)),
            ("exchange_charge", ("exchange", "currency")),
            ("top_up_by_card_charge", ("top", "up", "card")),
            ("top_up_by_bank_transfer_charge", ("top", "up", "transfer")),
        ):
            if all(entity in words for entity in entities):
                scores[category] += 4

    if has_any("unrecognised", "unrecognized", "unauthorised", "unauthorized", "fraudulent"):
        if "direct" in words and "debit" in words:
            scores["direct_debit_payment_not_recognised"] += 7
        elif "withdrawal" in words or "atm" in words:
            scores["cash_withdrawal_not_recognised"] += 7
        elif "card" in words or "payment" in words or "transaction" in words:
            scores["card_payment_not_recognised"] += 5

    if not text:
        result = "pending_transfer"
    else:
        result = max(CATEGORIES, key=lambda category: scores[category])
        if scores[result] == 0:
            result = "pending_transfer"
    return {"answer": result}