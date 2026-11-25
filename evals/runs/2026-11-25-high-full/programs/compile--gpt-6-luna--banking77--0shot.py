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
    "wrong_exchange_rate_for_cash_withdrawal",
]

# Representative ways customers describe each of the fixed task's intents.
# These are phrase matches, not instructions supplied at runtime.
_ALIAS_TEXT = {
    "activate_my_card": """
        activate my card|activate card|card activation|how do i activate|how to activate
        |unfreeze my card|unfreeze card|turn my card back on|enable my card
    """,
    "age_limit": """
        age limit|minimum age|minimum age to open|how old do i have to be
        |how old must i be|under 18|too young to open|age requirement
    """,
    "apple_pay_or_google_pay": """
        apple pay|google pay|add card to apple wallet|add card to google wallet
        |pay with my phone|mobile wallet|apple wallet|google wallet
    """,
    "atm_support": """
        atm support|use an atm|use my card at an atm|which atms|supported atms
        |can i withdraw at an atm|cash machine support|find an atm
    """,
    "automatic_top_up": """
        automatic top up|automatic top-up|auto top up|auto top-up|automatic topup
        |automatically top up|automatic payment top up|scheduled top up
    """,
    "balance_not_updated_after_bank_transfer": """
        balance not updated after bank transfer|bank transfer not showing
        |bank transfer has not arrived|bank transfer hasn't arrived
        |bank transfer not received|money from bank transfer missing
        |transfer into my account not showing|incoming bank transfer missing
        |bank transfer pending in my account|where is my bank transfer
    """,
    "balance_not_updated_after_cheque_or_cash_deposit": """
        balance not updated after cash deposit|cash deposit not showing
        |cash deposit not received|cheque deposit not showing
        |check deposit not showing|cheque not credited|cash deposit missing
        |money from cheque not showing|cash or cheque deposit missing
    """,
    "beneficiary_not_allowed": """
        beneficiary not allowed|beneficiary is not allowed|recipient not allowed
        |cannot add beneficiary|can't add beneficiary|can't add recipient
        |unable to add beneficiary|beneficiary cannot be added
        |recipient cannot be added|beneficiary unavailable
    """,
    "cancel_transfer": """
        cancel transfer|cancel a transfer|cancel my transfer|stop a transfer
        |stop my transfer|undo a transfer|reverse a transfer|cancel bank transfer
    """,
    "card_about_to_expire": """
        card about to expire|card is expiring|my card expires|card expiry
        |card expiration|renew my card|replace expiring card|new card before expiry
    """,
    "card_acceptance": """
        card acceptance|where is my card accepted|where can i use my card
        |merchant does not accept my card|shop won't accept my card
        |card not accepted by merchant|places that accept my card
    """,
    "card_arrival": """
        card has not arrived|card hasn't arrived|where is my card
        |physical card not arrived|my card never arrived|waiting for my card
        |card delivery missing|ordered card not received|card hasn't been delivered
    """,
    "card_delivery_estimate": """
        card delivery estimate|how long for my card|how long does card delivery take
        |when will my card arrive|when should my card arrive|card delivery time
        |delivery time for my card|estimated card delivery|how long to receive my card
    """,
    "card_linking": """
        link my card|link a card|link card to account|link card to my account
        |connect my card|add existing card|linking a card|card linked to account
    """,
    "card_not_working": """
        card not working|my card doesn't work|my card does not work
        |card won't work|card will not work|problem with my card
        |card not functioning|can't use my card|unable to use my card
    """,
    "card_payment_fee_charged": """
        card payment fee|fee on card payment|charged a fee for card payment
        |card purchase fee|fee for a card transaction|extra fee for card payment
    """,
    "card_payment_not_recognised": """
        card payment not recognised|card payment not recognized
        |unrecognised card payment|unrecognized card payment
        |unknown card transaction|unknown card payment|don't recognise this card payment
        |don't recognize this card payment|unauthorised card payment
        |unauthorized card payment|fraudulent card payment|card transaction i did not make
        |card purchase i don't recognise|card purchase i don't recognize
    """,
    "card_payment_wrong_exchange_rate": """
        card payment wrong exchange rate|wrong exchange rate on card payment
        |incorrect card exchange rate|bad exchange rate for card purchase
        |wrong rate for card transaction|exchange rate on my card purchase is wrong
    """,
    "card_swallowed": """
        card swallowed|atm swallowed my card|cash machine swallowed my card
        |card got stuck in atm|atm kept my card|machine retained my card
    """,
    "cash_withdrawal_charge": """
        cash withdrawal charge|atm withdrawal fee|fee for withdrawing cash
        |charged for cash withdrawal|cash machine charge|atm charged me a fee
        |fee on my cash withdrawal
    """,
    "cash_withdrawal_not_recognised": """
        cash withdrawal not recognised|cash withdrawal not recognized
        |unknown atm withdrawal|unrecognised cash withdrawal|unrecognized cash withdrawal
        |atm withdrawal i did not make|cash withdrawal i don't recognise
        |cash withdrawal i don't recognize|unauthorised cash withdrawal
        |unauthorized cash withdrawal
    """,
    "change_pin": """
        change my pin|change pin|set a new pin|update my pin|how to change pin
        |change card pin|reset my pin
    """,
    "compromised_card": """
        compromised card|card details compromised|card details exposed
        |someone has my card details|card information stolen|card has been cloned
        |my card was cloned|card security compromised|freeze compromised card
    """,
    "contactless_not_working": """
        contactless not working|contactless doesn't work|contactless does not work
        |contactless payment failed|can't pay contactlessly|tap to pay not working
        |contactless stopped working|tap payment not working
    """,
    "country_support": """
        country support|supported countries|is my country supported
        |available in my country|available in my country|which countries are supported
        |use the service abroad|countries can i use|service available in
    """,
    "declined_card_payment": """
        declined card payment|card payment declined|card was declined|payment was declined
        |card purchase declined|my card was rejected|card payment rejected
        |why was my card declined|why is my card being declined
    """,
    "declined_cash_withdrawal": """
        declined cash withdrawal|atm withdrawal declined|cash withdrawal declined
        |atm declined my card|cash machine declined|withdrawal was declined
        |cash withdrawal rejected|atm transaction declined
    """,
    "declined_transfer": """
        declined transfer|transfer was declined|bank transfer declined
        |my transfer was rejected|transfer rejected|why was my transfer declined
        |payment transfer declined
    """,
    "direct_debit_payment_not_recognised": """
        direct debit not recognised|direct debit not recognized
        |unknown direct debit|unrecognised direct debit|unrecognized direct debit
        |direct debit i did not make|direct debit i don't recognise
        |direct debit i don't recognize|unauthorised direct debit
        |unauthorized direct debit
    """,
    "disposable_card_limits": """
        disposable card limit|disposable card limits|limit for disposable card
        |how many disposable cards|disposable virtual card limit
        |disposable card usage limit|disposable card restrictions
    """,
    "edit_personal_details": """
        edit personal details|change personal details|update personal details
        |change my address|update my address|change my name|update my name
        |change phone number|update phone number|edit my profile details
        |change my personal information
    """,
    "exchange_charge": """
        exchange charge|currency exchange fee|fee for exchanging currency
        |charged for exchanging|exchange fee|foreign exchange charge
        |currency conversion fee|charge to exchange money
    """,
    "exchange_rate": """
        exchange rate|currency rate|what rate will i get|current exchange rates
        |rate for exchanging currency|how is the exchange rate calculated
        |exchange rates|currency conversion rate
    """,
    "exchange_via_app": """
        exchange currency in the app|exchange money in the app|how to exchange currency
        |how do i exchange|convert money in the app|convert currency in the app
        |exchange currencies|exchange between currencies|currency exchange in app
    """,
    "extra_charge_on_statement": """
        extra charge on statement|unexpected charge on statement
        |unrecognised charge on statement|unrecognized charge on statement
        |unknown charge on my statement|extra transaction on statement
        |mystery charge|charge i don't understand|unexplained charge
    """,
    "failed_transfer": """
        failed transfer|transfer failed|my transfer has failed|transfer didn't go through
        |transfer did not go through|unable to make a transfer|can't make a transfer
        |problem sending a transfer|transfer unsuccessful|transfer error
    """,
    "fiat_currency_support": """
        fiat currency support|supported fiat currencies|which currencies are supported
        |currencies supported for my account|supported currencies in my account
        |can i hold this currency|hold different currencies|available account currencies
    """,
    "get_disposable_virtual_card": """
        get disposable virtual card|create disposable virtual card
        |make a disposable card|how to get a disposable card
        |request disposable virtual card|create a disposable card
        |disposable card setup
    """,
    "get_physical_card": """
        get a physical card|how to get a physical card|request a physical card
        |get physical card|obtain a physical card|need a physical card
        |physical card for my account
    """,
    "getting_spare_card": """
        get a spare card|getting a spare card|request a spare card
        |order a spare card|additional physical card|extra physical card
        |second card for my account|another physical card
    """,
    "getting_virtual_card": """
        get a virtual card|getting a virtual card|create a virtual card
        |how to get a virtual card|request a virtual card|make a virtual card
        |virtual card for my account
    """,
    "lost_or_stolen_card": """
        lost my card|card is lost|lost card|stolen card|card was stolen
        |card has been stolen|lost or stolen card|can't find my card
        |can't find my debit card|my card is missing|report a lost card
    """,
    "lost_or_stolen_phone": """
        lost my phone|phone was stolen|stolen phone|lost or stolen phone
        |phone is missing|can't find my phone|someone stole my phone
        |lost my mobile phone|lost device
    """,
    "order_physical_card": """
        order physical card|order a physical card|order new card
        |place an order for a card|how to order a card|order a debit card
        |buy a physical card
    """,
    "passcode_forgotten": """
        forgot passcode|forgot my passcode|passcode forgotten|can't remember passcode
        |forgot app passcode|forgot my app code|forgot my login passcode
        |reset forgotten passcode
    """,
    "pending_card_payment": """
        pending card payment|card payment pending|card transaction pending
        |card purchase pending|payment stuck as pending|card payment still pending
    """,
    "pending_cash_withdrawal": """
        pending cash withdrawal|atm withdrawal pending|cash withdrawal pending
        |atm transaction pending|withdrawal stuck as pending|cash withdrawal still pending
    """,
    "pending_top_up": """
        pending top up|pending top-up|top up pending|top-up pending
        |top up is pending|topup pending|top up stuck|top up still pending
    """,
    "pending_transfer": """
        pending transfer|transfer pending|bank transfer pending
        |transfer is pending|transfer stuck as pending|transfer still pending
        |money transfer pending
    """,
    "pin_blocked": """
        pin blocked|blocked pin|pin has been blocked|blocked my pin
        |too many pin attempts|pin attempts exceeded|unblock my pin
        |card pin blocked
    """,
    "receiving_money": """
        receiving money|receive money|how can someone pay me|how to receive money
        |how can i receive|someone send me money|details to receive money
        |account details for receiving|share my bank details|getting paid into my account
    """,
    "refund_not_showing_up": """
        refund not showing|refund not received|refund hasn't arrived
        |refund has not arrived|where is my refund|waiting for my refund
        |refund missing|refund not in my account|money from refund not showing
    """,
    "request_refund": """
        request a refund|how to request a refund|ask for a refund
        |get a refund from merchant|want to get my money back|claim a refund
        |refund from a purchase|return a purchase for refund
    """,
    "reverted_card_payment": """
        reverted card payment|card payment reverted|card payment reversed
        |reversed card transaction|card payment was reversed|card purchase reverted
        |card payment returned to my balance
    """,
    "supported_cards_and_currencies": """
        supported cards and currencies|which cards can i use|cards accepted for top up
        |cards supported for top up|what cards are supported|which card types are supported
        |supported card types|currencies accepted for card top up
    """,
    "terminate_account": """
        terminate account|close my account|delete my account|shut down my account
        |cancel my account|deactivate my account|account closure|close account permanently
    """,
    "top_up_by_bank_transfer_charge": """
        bank transfer top up fee|fee for bank transfer top up
        |charge for topping up by bank transfer|charged to top up by bank transfer
        |bank transfer top up charge|fee to add money by bank transfer
    """,
    "top_up_by_card_charge": """
        card top up fee|fee for card top up|charge for topping up by card
        |charged to top up by card|fee to add money by card|card top up charge
    """,
    "top_up_by_cash_or_cheque": """
        top up by cash|top up by cheque|top up by check|add cash to my account
        |add money by cheque|add money by check|cash or cheque top up
        |deposit cash to my account|top up with cash
    """,
    "top_up_failed": """
        top up failed|top-up failed|topup failed|my top up was declined
        |top up didn't work|top up did not work|unable to top up|can't top up
        |problem topping up|top up unsuccessful|adding money failed
    """,
    "top_up_limits": """
        top up limits|top-up limit|maximum top up|maximum top-up|minimum top up
        |how much can i top up|limit for adding money|top up allowance
        |limits on topping up
    """,
    "top_up_reverted": """
        top up reverted|top-up reverted|topup reverted|top up reversed
        |top-up reversed|money from top up was returned|top up returned to card
        |reverted card top up
    """,
    "topping_up_by_card": """
        top up by card|top-up by card|topping up by card|add money by card
        |add money with a card|how to top up with card|top up using my card
        |make a card top up|fund my account by card
    """,
    "transaction_charged_twice": """
        charged twice|charged two times|double charged|duplicate charge
        |same transaction twice|transaction appears twice|payment taken twice
        |charged more than once|duplicate transaction|paid twice
    """,
    "transfer_fee_charged": """
        transfer fee|fee for a transfer|charged for transfer|charge on my transfer
        |fee to send money|international transfer fee|transfer charge
        |why was i charged to transfer
    """,
    "transfer_into_account": """
        transfer into account|transfer money into my account|send money to my account
        |make a bank transfer into|add money by bank transfer|fund account by transfer
        |how to transfer money to my account|bank transfer details to add money
    """,
    "transfer_not_received_by_recipient": """
        recipient has not received transfer|recipient hasn't received transfer
        |transfer not received by recipient|transfer not arrived for recipient
        |money not received by recipient|beneficiary didn't receive transfer
        |recipient is missing my transfer|sent transfer but not received
    """,
    "transfer_timing": """
        transfer timing|how long does a transfer take|how long will my transfer take
        |when will my transfer arrive|transfer arrival time|transfer processing time
        |how long for bank transfer|when does a transfer arrive|transfer time
    """,
    "unable_to_verify_identity": """
        unable to verify identity|can't verify my identity|cannot verify identity
        |identity verification failed|failed identity check|verification won't work
        |unable to complete verification|can't pass identity verification
    """,
    "verify_my_identity": """
        verify my identity|verify identity|identity verification|how do i verify myself
        |how to verify my account|complete identity check|submit identity documents
        |verify my account identity
    """,
    "verify_source_of_funds": """
        verify source of funds|source of funds verification|proof of source of funds
        |prove where my money came from|proof of funds|verify where money came from
        |source of wealth documents
    """,
    "verify_top_up": """
        verify top up|verify top-up|verify a top up|verification for top up
        |confirm my top up|top up verification|prove my top up
        |verify card top up
    """,
    "virtual_card_not_working": """
        virtual card not working|virtual card doesn't work|virtual card does not work
        |virtual card declined|can't use virtual card|virtual card payment failed
        |problem with my virtual card
    """,
    "visa_or_mastercard": """
        visa or mastercard|visa or mastercard|visa mastercard|is it visa or mastercard
        |is my card visa|is my card mastercard|card network|visa card or mastercard
    """,
    "why_verify_identity": """
        why verify identity|why do i need to verify|why identity verification
        |reason for identity check|why do you need my identity|why verify my account
        |purpose of verification|why am i being asked to verify
    """,
    "wrong_amount_of_cash_received": """
        wrong amount of cash received|atm gave me the wrong amount
        |cash machine gave me the wrong amount|received less cash than requested
        |received more cash than requested|atm dispensed wrong amount
        |cash withdrawal amount is wrong|cash withdrawal short
    """,
    "wrong_exchange_rate_for_cash_withdrawal": """
        wrong exchange rate for cash withdrawal|wrong atm exchange rate
        |incorrect exchange rate on cash withdrawal|bad exchange rate at atm
        |wrong rate for atm withdrawal|cash withdrawal exchange rate is wrong
        |wrong currency conversion at atm
    """,
}


def _normalise(value):
    value = unicodedata.normalize("NFKD", str(value))
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower().replace("’", "'").replace("‘", "'")
    value = value.replace("'", "")
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


ALIASES = {}
for _category, _text in _ALIAS_TEXT.items():
    ALIASES[_category] = [_normalise(part) for part in _text.split("|") if part.strip()]


def _extract_strings(state):
    found = []
    preferred = {
        "text", "message", "query", "utterance", "question", "user_message",
        "content", "input", "state", "prompt",
    }

    def walk(obj):
        if isinstance(obj, str):
            found.append(obj)
        elif isinstance(obj, dict):
            role = str(obj.get("role", "")).lower()
            if role and role not in ("user", "human", "customer"):
                return
            keys = [key for key in obj if isinstance(key, str)]
            selected = [key for key in keys if key.lower() in preferred]
            if selected:
                for key in selected:
                    walk(obj[key])
                for key in keys:
                    if key.lower() not in preferred and key.lower() not in ("role", "name"):
                        walk(obj[key])
            else:
                for key in keys:
                    if key.lower() not in ("role", "name"):
                        walk(obj[key])
        elif isinstance(obj, (list, tuple)):
            for item in obj:
                walk(item)

    walk(state)
    return " ".join(found)


def _contains(text, phrase):
    return bool(re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text))


def predict(state) -> dict:
    text = _normalise(_extract_strings(state))
    scores = {category: 0.0 for category in CATEGORIES}

    for category, phrases in ALIASES.items():
        for phrase in phrases:
            if _contains(text, phrase):
                # Longer, more specific expressions modestly outrank short matches.
                score = 5.0 + min(len(phrase.split()), 7) * 0.24
                if score > scores[category]:
                    scores[category] = score

    def has(*phrases):
        return any(_contains(text, _normalise(phrase)) for phrase in phrases)

    def award(category, score):
        if category in scores and score > scores[category]:
            scores[category] = score

    # Resolve common intents whose wording may not match one of the stored phrases.
    pending = has("pending", "still processing", "stuck pending", "awaiting")
    declined = has("declined", "rejected", "was refused", "refused")
    not_recognised = has(
        "not recognised", "not recognized", "unrecognised", "unrecognized",
        "unauthorised", "unauthorized", "fraudulent", "did not make",
        "dont recognise", "dont recognize", "unknown transaction",
    )
    failed = has("failed", "failure", "did not go through", "didnt go through")
    transfer = has("transfer", "bank transfer", "money transfer", "beneficiary", "recipient")
    top_up = has("top up", "topup", "top-up", "topping up", "add money")
    card_payment = has("card payment", "card purchase", "card transaction", "payment by card")
    cash_withdrawal = has(
        "cash withdrawal", "atm withdrawal", "cash machine withdrawal", "withdrawing cash"
    )

    if not_recognised:
        if has("direct debit"):
            award("direct_debit_payment_not_recognised", 9.0)
        elif cash_withdrawal or has("atm", "cash machine"):
            award("cash_withdrawal_not_recognised", 8.8)
        elif card_payment or has("card", "purchase", "transaction", "payment"):
            award("card_payment_not_recognised", 8.7)

    if pending:
        if cash_withdrawal:
            award("pending_cash_withdrawal", 8.0)
        elif top_up:
            award("pending_top_up", 8.0)
        elif transfer:
            award("pending_transfer", 8.0)
        elif card_payment or has("card payment", "purchase"):
            award("pending_card_payment", 8.0)

    if declined:
        if cash_withdrawal or has("atm", "cash machine"):
            award("declined_cash_withdrawal", 8.2)
        elif transfer:
            award("declined_transfer", 8.2)
        elif card_payment or has("card", "purchase", "payment"):
            award("declined_card_payment", 8.2)
        elif top_up:
            award("top_up_failed", 7.8)

    if failed:
        if top_up:
            award("top_up_failed", 8.1)
        elif transfer:
            award("failed_transfer", 8.1)
        elif cash_withdrawal:
            award("declined_cash_withdrawal", 7.3)
        elif card_payment:
            award("declined_card_payment", 7.3)

    if has("reverted", "reversed", "returned to my card"):
        if top_up:
            award("top_up_reverted", 8.4)
        elif card_payment:
            award("reverted_card_payment", 8.4)

    if has("wrong exchange rate", "incorrect exchange rate", "bad exchange rate"):
        if cash_withdrawal or has("atm", "cash machine", "withdrawal"):
            award("wrong_exchange_rate_for_cash_withdrawal", 8.7)
        elif card_payment or has("card purchase", "card transaction"):
            award("card_payment_wrong_exchange_rate", 8.6)
        else:
            award("exchange_rate", 7.8)

    if has("charged twice", "charged two times", "duplicate charge", "transaction appears twice"):
        award("transaction_charged_twice", 9.0)

    if has("refund", "money back"):
        if has("not showing", "not received", "not arrived", "still waiting", "missing"):
            award("refund_not_showing_up", 8.5)
        elif has("request", "claim", "ask for", "want a refund", "get a refund"):
            award("request_refund", 7.9)

    if has("fee", "charge", "charged", "extra cost"):
        if transfer and not has("top up", "topup", "top-up"):
            award("transfer_fee_charged", 7.7)
        if top_up:
            if has("bank transfer", "bank top up", "bank top-up"):
                award("top_up_by_bank_transfer_charge", 8.0)
            elif has("card", "debit card", "credit card"):
                award("top_up_by_card_charge", 8.0)
        if cash_withdrawal:
            award("cash_withdrawal_charge", 7.8)
        if card_payment and not has("exchange", "exchange rate"):
            award("card_payment_fee_charged", 7.8)
        if has("exchange", "currency conversion", "foreign exchange"):
            award("exchange_charge", 7.7)

    if has("not arrived", "not received", "hasnt arrived", "has not arrived", "missing"):
        if transfer and has("recipient", "beneficiary", "they", "their account"):
            award("transfer_not_received_by_recipient", 8.1)
        elif has("bank transfer", "incoming transfer") and has("balance", "account"):
            award("balance_not_updated_after_bank_transfer", 8.0)

    # Distinguish an actual missing ordered card from a question about delivery duration.
    if has("card", "physical card"):
        if has("how long", "delivery time", "delivery estimate", "estimated delivery"):
            award("card_delivery_estimate", 8.0)
        elif has("where is my card", "not arrived", "hasnt arrived", "has not arrived"):
            award("card_arrival", 8.0)

    # Use token overlap with category names as a useful fallback for paraphrases.
    if max(scores.values(), default=0.0) < 5.0 and text:
        words = set(text.split())
        for category in CATEGORIES:
            label_words = set(category.replace("_", " ").split())
            overlap = len(words & label_words)
            if overlap:
                scores[category] = max(scores[category], 1.0 + overlap)

    # A valid category is required even for empty or wholly out-of-domain input.
    answer = max(CATEGORIES, key=lambda category: scores[category])
    return {"answer": answer}