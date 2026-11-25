import math
import re
import unicodedata


LABELS = (
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
    "top_up_by_cash_or_cheque", "top_up_failed", "top_up_limits",
    "top_up_reverted", "topping_up_by_card", "transaction_charged_twice",
    "transfer_fee_charged", "transfer_into_account",
    "transfer_not_received_by_recipient", "transfer_timing",
    "unable_to_verify_identity", "verify_my_identity", "verify_source_of_funds",
    "verify_top_up", "virtual_card_not_working", "visa_or_mastercard",
    "why_verify_identity", "wrong_amount_of_cash_received",
    "wrong_exchange_rate_for_cash_withdrawal"
)

PROTOTYPES = {
    "activate_my_card": [
        "activate my new card", "enable my bank card for use", "how do I activate a card"
    ],
    "age_limit": [
        "minimum age to open an account", "how old do I need to be", "account for a child under eighteen"
    ],
    "apple_pay_or_google_pay": [
        "add card to apple pay or google pay", "mobile wallet on iphone android",
        "use samsung pay with card"
    ],
    "atm_support": [
        "can I withdraw money from an atm", "which cash machines can I use",
        "are cash withdrawals supported"
    ],
    "automatic_top_up": [
        "automatically top up when balance is low", "set up recurring automatic reload",
        "turn off auto top up"
    ],
    "balance_not_updated_after_bank_transfer": [
        "bank transfer received but balance not updated", "incoming transfer missing from my account",
        "money sent to me has not appeared in my balance"
    ],
    "balance_not_updated_after_cheque_or_cash_deposit": [
        "cash deposit not showing in balance", "cheque deposited but account balance has not changed"
    ],
    "beneficiary_not_allowed": [
        "beneficiary is not allowed", "cannot add recipient to transfer",
        "recipient is prohibited or unsupported"
    ],
    "cancel_transfer": [
        "cancel a bank transfer", "stop money I sent", "reverse a transfer made by mistake"
    ],
    "card_about_to_expire": [
        "my card expires soon", "renew expired card", "replacement after expiry date"
    ],
    "card_acceptance": [
        "where is the card accepted", "can I pay in shops abroad online",
        "merchant does not accept my card"
    ],
    "card_arrival": [
        "where is my card", "ordered card but it has not arrived", "track delivery of card",
        "my card is late or lost in the post"
    ],
    "card_delivery_estimate": [
        "how long does delivery of a card take", "when will my new card arrive",
        "estimated shipping time for card"
    ],
    "card_linking": [
        "link my card to my account", "attach a card in the app", "associate card with account"
    ],
    "card_not_working": [
        "my physical card is not working", "cannot use my card", "card broken damaged"
    ],
    "card_payment_fee_charged": [
        "fee charged for paying by card", "extra card transaction fee", "why was my card payment charged a fee"
    ],
    "card_payment_not_recognised": [
        "card payment I do not recognise", "unknown purchase on my card",
        "someone made an unauthorised card transaction"
    ],
    "card_payment_wrong_exchange_rate": [
        "wrong exchange rate on card payment", "incorrect conversion when paying abroad",
        "purchase was converted at the wrong currency rate"
    ],
    "card_swallowed": [
        "cash machine swallowed my card", "atm retained or ate my card", "card stuck in cash machine"
    ],
    "cash_withdrawal_charge": [
        "fee for withdrawing cash from atm", "charged for taking money out at cash machine",
        "cash withdrawal surcharge"
    ],
    "cash_withdrawal_not_recognised": [
        "cash withdrawal I do not recognise", "unknown atm transaction",
        "someone withdrew cash without my permission"
    ],
    "change_pin": [
        "change my card pin number", "reset or view card pin", "forgot my pin"
    ],
    "compromised_card": [
        "card details compromised", "someone knows my card number", "card cloned or hacked",
        "suspect my card information has been stolen"
    ],
    "contactless_not_working": [
        "contactless payment is not working", "tap to pay failed",
        "cannot use contactless on my card"
    ],
    "country_support": [
        "which countries are supported", "is the service available in my country",
        "can I open an account as a resident abroad"
    ],
    "declined_card_payment": [
        "my card payment was declined", "purchase rejected at a shop",
        "card transaction did not go through"
    ],
    "declined_cash_withdrawal": [
        "atm declined cash withdrawal", "cash machine rejected my withdrawal",
        "cannot withdraw cash"
    ],
    "declined_transfer": [
        "bank transfer was declined", "transfer rejected by bank", "payment to beneficiary refused"
    ],
    "direct_debit_payment_not_recognised": [
        "unrecognised direct debit", "unknown recurring debit from my account",
        "direct debit I did not authorise"
    ],
    "disposable_card_limits": [
        "disposable virtual card usage limits", "how many single use cards can I create",
        "limit on disposable card transactions"
    ],
    "edit_personal_details": [
        "change my name address phone number or email", "update personal details",
        "edit my profile information"
    ],
    "exchange_charge": [
        "fee for currency exchange", "charged extra to convert currencies",
        "foreign exchange commission markup"
    ],
    "exchange_rate": [
        "what is the currency exchange rate", "where can I find conversion rates",
        "how is the foreign exchange rate calculated"
    ],
    "exchange_via_app": [
        "how to exchange money in the app", "convert one currency into another",
        "exchange currency between balances"
    ],
    "extra_charge_on_statement": [
        "extra dollar charged on my statement", "why was I charged extra",
        "additional small charge on account", "merchant charged more than expected"
    ],
    "failed_transfer": [
        "bank transfer failed", "money transfer unsuccessful", "unable to send a transfer"
    ],
    "fiat_currency_support": [
        "which currencies are supported", "can I hold euros dollars pounds",
        "supported fiat currency accounts"
    ],
    "get_disposable_virtual_card": [
        "create a disposable virtual card", "get a single use card",
        "how to generate one time card"
    ],
    "get_physical_card": [
        "how do I get a physical card", "obtain a plastic debit card",
        "can I have a physical card"
    ],
    "getting_spare_card": [
        "get an extra card", "order a spare or second card", "can I have multiple cards"
    ],
    "getting_virtual_card": [
        "how do I get a virtual card", "create a digital card",
        "issue an online card"
    ],
    "lost_or_stolen_card": [
        "my card was lost or stolen", "lost my wallet with card",
        "someone stole my debit card"
    ],
    "lost_or_stolen_phone": [
        "my phone was lost or stolen", "lost mobile with banking app",
        "someone stole my smartphone"
    ],
    "order_physical_card": [
        "order a new card", "apply for a debit card", "request a card in the app"
    ],
    "passcode_forgotten": [
        "forgot app passcode", "reset login password", "cannot remember my account passcode"
    ],
    "pending_card_payment": [
        "card payment is pending", "purchase is still processing",
        "card transaction not completed"
    ],
    "pending_cash_withdrawal": [
        "cash withdrawal is pending", "atm withdrawal is still processing",
        "why is withdrawal not completed"
    ],
    "pending_top_up": [
        "top up is pending", "card deposit is still processing",
        "money added to account is pending"
    ],
    "pending_transfer": [
        "transfer is pending", "outgoing transaction", "bank transfer is processing",
        "sent money is still pending"
    ],
    "pin_blocked": [
        "card pin is blocked", "too many incorrect pin attempts",
        "unlock pin after wrong tries"
    ],
    "receiving_money": [
        "how can someone send me money", "receive a bank payment from another person",
        "account details for receiving money", "can I receive international transfers"
    ],
    "refund_not_showing_up": [
        "refund has not appeared", "merchant returned my money but refund is missing",
        "where is my pending refund"
    ],
    "request_refund": [
        "how do I request a refund", "get money back from merchant",
        "dispute a purchase and claim refund"
    ],
    "reverted_card_payment": [
        "card payment was reversed", "purchase reverted and money returned",
        "card transaction cancelled by merchant"
    ],
    "supported_cards_and_currencies": [
        "which cards can I use to top up", "supported debit credit cards for adding money",
        "which currencies can I top up with"
    ],
    "terminate_account": [
        "close my account", "delete my account permanently", "terminate membership"
    ],
    "top_up_by_bank_transfer_charge": [
        "fee for topping up by bank transfer", "charged for adding money by bank",
        "incoming bank transfer deposit fee"
    ],
    "top_up_by_card_charge": [
        "fee for topping up by card", "charged extra when adding money using credit card",
        "card deposit surcharge"
    ],
    "top_up_by_cash_or_cheque": [
        "can I deposit cash or cheque", "add money using a check",
        "top up my account with cash"
    ],
    "top_up_failed": [
        "top up failed", "card deposit was declined", "cannot add money using card"
    ],
    "top_up_limits": [
        "top up limit", "maximum amount I can add to my account",
        "minimum and daily deposit limits"
    ],
    "top_up_reverted": [
        "top up was reversed", "money added by card was returned",
        "card deposit reverted"
    ],
    "topping_up_by_card": [
        "how to top up by card", "add money using a debit or credit card",
        "fund account with my bank card"
    ],
    "transaction_charged_twice": [
        "charged twice for the same transaction", "duplicate payment",
        "merchant took money two times"
    ],
    "transfer_fee_charged": [
        "fee for sending a bank transfer", "extra charge on outgoing transfer",
        "international transfer commission"
    ],
    "transfer_into_account": [
        "how to transfer money into my account", "add money by bank transfer",
        "deposit funds from my bank account"
    ],
    "transfer_not_received_by_recipient": [
        "recipient has not received my transfer", "money I sent has not reached beneficiary",
        "friend did not get the payment"
    ],
    "transfer_timing": [
        "how long does a bank transfer take", "when will money reach recipient",
        "transfer processing time"
    ],
    "unable_to_verify_identity": [
        "identity verification failed", "cannot verify my identity",
        "photo ID was rejected", "unable to upload documents"
    ],
    "verify_my_identity": [
        "how to verify my identity", "what documents are needed for identity verification",
        "submit photo id passport"
    ],
    "verify_source_of_funds": [
        "verify source of funds", "proof of income and wealth", "where did my money come from",
        "provide bank statements salary documents"
    ],
    "verify_top_up": [
        "verify a top up card", "confirm card deposit with verification code",
        "authenticate card used to add money"
    ],
    "virtual_card_not_working": [
        "virtual card does not work", "online card payment fails",
        "cannot use my digital card"
    ],
    "visa_or_mastercard": [
        "is the card visa or mastercard", "which card network will I get",
        "choose between mastercard and visa"
    ],
    "why_verify_identity": [
        "why do I need to verify my identity", "reason for requesting identification",
        "why must I provide my passport"
    ],
    "wrong_amount_of_cash_received": [
        "atm gave me wrong amount of cash", "cash machine gave less money than requested",
        "no cash came out but account was debited"
    ],
    "wrong_exchange_rate_for_cash_withdrawal": [
        "wrong exchange rate on cash withdrawal", "atm used incorrect currency conversion",
        "foreign cash withdrawal converted at bad rate"
    ]
}

STOPWORDS = {
    "a", "an", "the", "i", "me", "my", "mine", "you", "your", "we", "our",
    "it", "its", "is", "are", "was", "were", "be", "been", "being", "am",
    "do", "does", "did", "can", "could", "would", "should", "will", "have",
    "has", "had", "to", "of", "for", "in", "on", "at", "by", "with", "from",
    "and", "or", "as", "this", "that", "these", "those", "what", "how",
    "when", "where", "why", "which", "please", "want", "need", "about",
    "there", "here", "if", "some", "any", "just", "tell", "know", "like"
}


def normalize(text):
    text = unicodedata.normalize("NFKC", text).lower()
    text = text.replace("’", "'").replace("`", "'")
    contractions = {
        "can't": "cannot", "won't": "will not", "don't": "do not",
        "doesn't": "does not", "didn't": "did not", "isn't": "is not",
        "aren't": "are not", "wasn't": "was not", "weren't": "were not",
        "hasn't": "has not", "haven't": "have not", "hadn't": "had not",
        "couldn't": "could not", "wouldn't": "would not", "shouldn't": "should not",
        "i've": "i have", "i'm": "i am", "it's": "it is", "that's": "that is",
        "what's": "what is", "there's": "there is"
    }
    for old, new in contractions.items():
        text = text.replace(old, new)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def tokens(text):
    result = set()
    for word in normalize(text).split():
        if word in STOPWORDS or len(word) < 2:
            continue
        if len(word) > 5 and word.endswith("ing"):
            word = word[:-3]
        elif len(word) > 4 and word.endswith("ed"):
            word = word[:-2]
        elif len(word) > 4 and word.endswith("es"):
            word = word[:-2]
        elif len(word) > 4 and word.endswith("s"):
            word = word[:-1]
        result.add(word)
    return result


def fallback(text):
    query = tokens(text)
    if not query:
        return "pending_transfer"
    document_frequency = {}
    prepared = {}
    for label, phrases in PROTOTYPES.items():
        rows = [tokens(phrase) for phrase in phrases]
        prepared[label] = rows
        all_words = set()
        for row in rows:
            all_words.update(row)
        for word in all_words:
            document_frequency[word] = document_frequency.get(word, 0) + 1

    total = len(PROTOTYPES)

    def weight(word):
        return 1.0 + math.log((total + 1.0) / (document_frequency.get(word, 0) + 1.0))

    best_label = "pending_transfer"
    best_score = 0.0
    for label, rows in prepared.items():
        for row in rows:
            common = query & row
            if not common:
                continue
            shared = sum(weight(word) for word in common)
            qweight = sum(weight(word) for word in query)
            rweight = sum(weight(word) for word in row)
            score = 2.0 * shared / (qweight + rweight)
            if len(common) >= 2:
                score += 0.04
            if score > best_score:
                best_score = score
                best_label = label
    return best_label


def classify(text):
    s = normalize(text)
    for label in LABELS:
        if s == label.replace("_", " "):
            return label

    def has(pattern):
        return re.search(pattern, s) is not None

    card = has(r"\b(card|cards|debit card|credit card|plastic)\b")
    virtual = has(r"\b(virtual|digital|online card|e card)\b")
    disposable = has(r"\b(disposable|single use|one use|one time|one off)\b")
    phone = has(r"\b(phone|mobile|smartphone|iphone|android|handset)\b")
    lost = has(r"\b(lost|lose|missing|stolen|steal|stole|theft|misplaced)\b")
    topup = has(
        r"\b(top ?up|topping up|topped up|reload|reloading|recharge|"
        r"add(?:ing|ed)? (?:some )?(?:money|funds|cash|balance)|"
        r"load(?:ing|ed)? (?:my |the )?(?:account|balance|card)|"
        r"fund(?:ing)? (?:my |the )?account|card deposit)\b"
    )
    transfer = has(r"\b(transfer|transfers|transferred|transferring|wire|remittance|bank payment)\b")
    cash = has(r"\b(atm|cash machine|cashpoint|cash withdrawal|withdraw(?:al|ing)? (?:cash|money)|withdrew|cash out)\b")
    cheque = has(r"\b(cheque|cheques|check deposit|deposit(?:ing|ed)? (?:a |the |my )?check)\b")
    deposit_cash = has(r"\b(cash deposit|deposit(?:ing|ed)? (?:some |my |the )?cash|pay (?:in |with )?cash)\b")
    payment = has(r"\b(payment|payments|purchase|purchases|paid|paying|pay|transaction|transactions|merchant|shop|store|charged|charge|billed|debit)\b")
    fee = has(r"\b(fee|fees|commission|surcharge|markup|costs?|charged extra|extra charge|additional charge|charged|charge)\b")
    explicit_fee = has(r"\b(fee|fees|commission|surcharge|markup)\b")
    pending = has(r"\b(pending|processing|in progress|not completed|not complete|being processed|still waiting|on hold|awaiting|outstanding)\b")
    failed = has(r"\b(fail(?:ed|ure|ing)?|unsuccessful|not successful|cannot|unable|not working|does not work|will not work|could not|not going through|did not go through|not go through|problem|error)\b")
    declined = has(r"\b(declin(?:e|ed|ing)|reject(?:ed|ion)?|refused|denied|not accepted)\b")
    reversed_ = has(r"\b(revers(?:ed|al|e)|revert(?:ed|s)?|returned|rolled back|cancelled automatically)\b")
    unknown = has(
        r"\b(not recogni[sz]e|do not recogni[sz]e|does not recogni[sz]e|"
        r"unrecogni[sz]ed|unknown|unfamiliar|unauthori[sz]ed|"
        r"not authori[sz]ed|did not (?:make|authori[sz]e|approve|do)|"
        r"never (?:made|authori[sz]ed|used)|not mine|fraudulent)\b"
    )
    missing = has(
        r"\b(not (?:received|arrived|showing|appeared|credited|reflected|there)|"
        r"has not (?:arrived|appeared|shown|come|reached|received)|"
        r"have not (?:received|got|seen)|did not (?:receive|get|arrive|show)|"
        r"does not (?:show|appear)|missing|not in (?:my |the )?account|"
        r"not showing up|where is|still waiting|yet to (?:arrive|appear))\b"
    )
    timing = has(r"\b(how long|when (?:will|can|should|does|do|is)|time(?:frame)?|how many (?:days|hours|weeks)|estimated|estimate|delivery date)\b")
    limit = has(r"\b(limit|limits|maximum|minimum|how much|how many|cap|allowance|restriction)\b")
    identity = has(r"\b(identity|identification|id verification|verify (?:my |the )?(?:id|identity)|passport|photo id|proof of identity|selfie|kyc)\b")
    verify = has(r"\b(verif(?:y|ied|ication|ying)|validat(?:e|ion)|confirm|authenticat(?:e|ion)|prove|proof|documents?)\b")

    if has(r"\b(source of (?:my )?(?:funds|money|wealth)|proof of (?:income|funds|wealth)|"
           r"where (?:did|does) (?:my |the )?money come from|salary documents|"
           r"verify (?:my )?(?:income|funds|wealth))\b"):
        return "verify_source_of_funds"

    if identity and (verify or has(r"\b(passport|photo id|selfie|identity check)\b")):
        if has(r"\b(why|reason|necessary|have to|need to|must i|required)\b") and not failed:
            return "why_verify_identity"
        if failed or declined or has(r"\b(not verif(?:ied|ying)|cannot upload|not accepted|blurry|invalid)\b"):
            return "unable_to_verify_identity"
        return "verify_my_identity"

    if phone and lost and not has(r"\b(phone number|mobile number)\b"):
        return "lost_or_stolen_phone"
    if card and lost and not has(r"\b(card (?:delivery|in the post)|lost in (?:the )?(?:post|mail))\b"):
        if has(r"\b(details|number|information|data)\b") and not has(r"\b(physical card|wallet|my card (?:is |was )?(?:lost|stolen))\b"):
            return "compromised_card"
        return "lost_or_stolen_card"
    if card and has(r"\b(compromised|cloned|hacked|breach|card details (?:stolen|leaked)|someone (?:has|knows|used) my card details)\b"):
        return "compromised_card"

    if has(r"\b(pin|pin number)\b") and not has(r"\b(passcode|app password)\b"):
        if has(r"\b(blocked|locked|unlock|too many|incorrect attempts|wrong (?:pin|attempts)|tries|attempts exceeded)\b"):
            return "pin_blocked"
        return "change_pin"
    if has(r"\b(passcode|password|login code|app code|log in code)\b") and has(
        r"\b(forgot|forgotten|forget|reset|remember|lost|locked|change|recover)\b"
    ):
        return "passcode_forgotten"

    if has(r"\b(close|closing|terminate|termination|delete|deactivate|shut down|cancel)\b") and has(
        r"\b(account|membership|profile)\b"
    ) and not transfer:
        return "terminate_account"
    if has(r"\b(age limit|minimum age|how old|underage|under 18|under eighteen|minor|child|years old)\b"):
        return "age_limit"
    if has(r"\b(change|update|edit|correct|modify|new)\b") and has(
        r"\b(address|email|e mail|phone number|mobile number|personal details|personal information|"
        r"profile details|name|surname|date of birth|residential details)\b"
    ):
        return "edit_personal_details"

    if has(r"\b(apple pay|google pay|samsung pay|mobile wallet|digital wallet|gpay|apple wallet|google wallet)\b"):
        return "apple_pay_or_google_pay"

    if has(r"\b(direct debit|direct debits)\b"):
        if unknown or has(r"\b(what is|who|why|dispute|recognise|recognize)\b"):
            return "direct_debit_payment_not_recognised"

    if has(r"\b(twice|double charged|double charge|duplicate|duplicated|two times|charged two|"
           r"same (?:payment|transaction|purchase) twice|charged me twice)\b") and (payment or topup or transfer):
        return "transaction_charged_twice"

    if has(r"\b(refund|refunded|money back|reimbursement|reimburse)\b"):
        if missing or pending or has(r"\b(not (?:got|getting)|still (?:not|waiting)|where|how long|when)\b"):
            return "refund_not_showing_up"
        return "request_refund"

    if has(r"\b(beneficiary|recipient|payee)\b") and has(
        r"\b(not allowed|cannot add|unable to add|not supported|unsupported|prohibited|restricted|not eligible|invalid beneficiary)\b"
    ):
        return "beneficiary_not_allowed"

    if (cash or has(r"\b(cash machine|atm)\b")) and card and has(
        r"\b(swallowed|swallow|retained|kept|stuck|ate|eaten|captured|did not return|not returned)\b"
    ):
        return "card_swallowed"

    if cheque or deposit_cash:
        if missing or has(r"\b(balance (?:has |is )?not|not updated|not credited|not reflected|"
                          r"balance (?:is |has )?(?:wrong|unchanged)|did not update)\b"):
            return "balance_not_updated_after_cheque_or_cash_deposit"
        return "top_up_by_cash_or_cheque"

    if cash:
        if has(r"\b(exchange rate|conversion rate|currency conversion|converted|wrong rate|"
               r"bad rate|foreign exchange|fx rate)\b"):
            return "wrong_exchange_rate_for_cash_withdrawal"
        if unknown:
            return "cash_withdrawal_not_recognised"
        if has(r"\b(wrong amount|incorrect amount|less (?:money|cash)|not enough (?:cash|money)|"
               r"short changed|shortchanged|did not (?:give|dispense)|no (?:cash|money) (?:came|dispensed)|"
               r"nothing (?:came|dispensed)|only (?:gave|received)|dispensed (?:less|wrong))\b"):
            return "wrong_amount_of_cash_received"
        if declined or failed or has(r"\b(cannot withdraw|unable to withdraw|withdrawal refused)\b"):
            return "declined_cash_withdrawal"
        if pending:
            return "pending_cash_withdrawal"
        if fee:
            return "cash_withdrawal_charge"
        return "atm_support"

    if disposable:
        if limit:
            return "disposable_card_limits"
        return "get_disposable_virtual_card"

    if has(r"\b(visa|mastercard|master card)\b"):
        if topup or has(r"\b(top up|supported cards|which cards (?:can|are)|use (?:my|a) (?:visa|mastercard) to)\b"):
            return "supported_cards_and_currencies"
        return "visa_or_mastercard"

    if topup or (has(r"\b(deposit|add funds|adding funds)\b") and card and not transfer):
        if verify and not identity:
            return "verify_top_up"
        if has(r"\b(auto(?:matic(?:ally)?)?|recurring|scheduled|repeat|whenever balance)\b"):
            return "automatic_top_up"
        if has(r"\b(which|what|supported|support|eligible|accept(?:ed)?|can i use)\b") and has(
            r"\b(cards?|currenc(?:y|ies)|visa|mastercard|credit|debit)\b"
        ) and not has(r"\b(how (?:do|can) i|how to)\b"):
            return "supported_cards_and_currencies"
        if limit:
            return "top_up_limits"
        if reversed_:
            return "top_up_reverted"
        if pending:
            return "pending_top_up"
        if declined or failed:
            return "top_up_failed"
        if fee:
            if transfer or has(r"\b(bank transfer|wire|from (?:my )?bank account)\b"):
                return "top_up_by_bank_transfer_charge"
            return "top_up_by_card_charge"
        if transfer or has(r"\b(bank transfer|wire|from (?:my )?bank account)\b"):
            return "transfer_into_account"
        if card:
            return "topping_up_by_card"
        if has(r"\b(cash|cheque|check)\b"):
            return "top_up_by_cash_or_cheque"
        return "topping_up_by_card"

    if has(r"\b(contactless|tap to pay|tapping|tap payment|tap my card)\b"):
        return "contactless_not_working"

    if card and has(r"\b(expir(?:e|es|ed|ing|y|ation)|renew(?:al|ing)?)\b"):
        return "card_about_to_expire"

    if card and has(r"\b(activat(?:e|ion|ing)|enable my (?:new )?card)\b"):
        return "activate_my_card"

    if card and has(r"\b(link|linking|linked|connect|attach|associate|pair)\b") and not payment:
        return "card_linking"

    if card and has(r"\b(spare|second|another|additional|extra card|multiple cards|more than one card)\b"):
        return "getting_spare_card"

    delivery = has(r"\b(deliver(?:y|ed|ing)?|ship(?:ping|ped)?|arriv(?:e|al|ed|ing)|"
                   r"postage|postal|in the post|in the mail|tracking|track my card)\b")
    if card and (delivery or has(r"\b(where is my card|card has not come|card not received)\b")):
        if missing or has(r"\b(late|delayed|delay|already ordered|ordered .* ago|long overdue|track|tracking|lost in)\b"):
            return "card_arrival"
        if timing:
            return "card_delivery_estimate"
        return "card_arrival"

    if virtual and (card or has(r"\b(virtual|digital)\b")):
        if failed or declined or has(r"\b(not work|does not work|not usable|cannot use|unable to use)\b"):
            return "virtual_card_not_working"
        return "getting_virtual_card"

    if has(r"\b(exchange|exchanging|conversion|convert(?:ing|ed)?|forex|foreign exchange|fx rate)\b") or has(
        r"\b(exchange rate|conversion rate|currency rate)\b"
    ):
        if card and payment and has(r"\b(wrong|incorrect|bad|unfair|different|high|rate|conversion)\b"):
            return "card_payment_wrong_exchange_rate"
        if explicit_fee or has(r"\b(charged|charge|cost|commission|markup)\b"):
            return "exchange_charge"
        if has(r"\b(rate|rates|how much (?:is|will)|what is .* worth)\b"):
            return "exchange_rate"
        return "exchange_via_app"

    incoming = has(
        r"\b(incoming|receive|receiving|received|sent to me|sent me|send me|"
        r"someone (?:sent|sends|send)|my (?:friend|employer|salary)|"
        r"into my account|to my account|to (?:my |the )?balance)\b"
    )
    recipient = has(r"\b(recipient|beneficiary|payee|person i sent|person i paid|"
                    r"friend i sent|them|they|their account|his account|her account)\b")

    if transfer or has(r"\b(outgoing transaction|outgoing payment|bank wire|money i sent|"
                       r"sent money|send money|money transfer|bank details|iban|swift)\b"):
        if has(r"\b(cancel|stop|recall|undo|reverse)\b") and not reversed_:
            return "cancel_transfer"
        if fee:
            if incoming and has(r"\b(top|deposit|adding|funding|receive|receiving|incoming)\b"):
                return "top_up_by_bank_transfer_charge"
            return "transfer_fee_charged"
        if incoming and (missing or has(r"\b(balance (?:has |is )?not|not updated|not credited|"
                                        r"not reflected|balance unchanged|did not update)\b")) and not recipient:
            return "balance_not_updated_after_bank_transfer"
        if recipient and (missing or has(r"\b(not (?:got|received)|has not (?:got|received)|"
                                         r"did not (?:get|receive)|never (?:got|received)|not reached)\b")):
            return "transfer_not_received_by_recipient"
        if declined:
            return "declined_transfer"
        if failed or reversed_:
            return "failed_transfer"
        if pending:
            return "pending_transfer"
        if timing:
            return "transfer_timing"
        if incoming or has(r"\b(bank details|iban|swift|account number|receive|receiving)\b"):
            if has(r"\b(my (?:other )?bank|from (?:my |another )?bank|into my account|"
                   r"transfer (?:money |funds )?(?:into|to) my account|"
                   r"add money|deposit|fund my account)\b"):
                return "transfer_into_account"
            return "receiving_money"
        return "pending_transfer"

    if has(r"\b(receive money|receiving money|someone (?:send|sending|sends) me money|"
           r"get paid|receive (?:a |an )?(?:payment|salary|wages))\b"):
        return "receiving_money"

    if has(r"\b(supported|support|available|availability|operate|open an account|sign up|use (?:the )?service)\b") and has(
        r"\b(country|countries|region|residents?|live|living|abroad|internationally)\b"
    ) and not card:
        return "country_support"

    if has(r"\b(currenc(?:y|ies)|dollars?|euros?|pounds?|fiat)\b") and has(
        r"\b(support(?:ed)?|available|hold|account|accept(?:ed)?|which|what)\b"
    ):
        return "fiat_currency_support"

    if card and has(r"\b(accept(?:ed|ance)?|where can i use|use (?:it|my card) (?:in|at|abroad|online)|"
                    r"work (?:in|at|abroad)|shops? (?:accept|take)|merchant accept)\b") and not declined:
        return "card_acceptance"

    if payment or card:
        if unknown:
            return "card_payment_not_recognised"
        if has(r"\b(extra (?:dollar|pound|euro|amount|money|charge)|"
               r"charged (?:an? )?extra|charged more|more than (?:i|the)|"
               r"additional (?:dollar|pound|euro|amount|charge)|"
               r"small (?:charge|amount)|statement.*extra)\b") and not explicit_fee:
            return "extra_charge_on_statement"
        if reversed_:
            return "reverted_card_payment"
        if declined:
            return "declined_card_payment"
        if pending:
            return "pending_card_payment"
        if explicit_fee and (card or payment):
            return "card_payment_fee_charged"
        if card and failed:
            return "card_not_working"
        if card and has(r"\b(broken|damaged|does not work|not working|cannot use|unable to use)\b"):
            return "card_not_working"
        if card and has(r"\b(order|ordered|request|apply|application)\b"):
            return "order_physical_card"
        if card and has(r"\b(get|getting|obtain|have|need|receive|issue|physical|plastic)\b") and not payment:
            if has(r"\b(physical|plastic)\b"):
                return "get_physical_card"
            return "order_physical_card"
        if has(r"\b(extra|unexpected|additional|strange|unusual)\b") and has(r"\b(charge|charged|statement)\b"):
            return "extra_charge_on_statement"
        if failed and payment:
            return "declined_card_payment"

    if has(r"\b(country|countries|region)\b"):
        return "country_support"
    if has(r"\b(card|cards)\b"):
        return "get_physical_card"
    return fallback(text)


def predict(state):
    if isinstance(state, str):
        text = state
    elif isinstance(state, dict):
        parts = []
        for key in ("text", "message", "query", "question", "utterance", "state"):
            value = state.get(key)
            if isinstance(value, str):
                parts.append(value)
        if parts:
            text = " ".join(parts)
        else:
            text = " ".join(str(value) for value in state.values() if isinstance(value, str))
    else:
        text = str(state)
    return {"answer": classify(text)}