import re
import math
import unicodedata
from collections import Counter, defaultdict
from functools import lru_cache
from difflib import get_close_matches


_PROTOTYPES = {
    "activate_my_card": (
        "How do I activate my new card?|My card needs activating|"
        "I received my card how do I start using it?|Where can I activate the physical card?"
    ),
    "age_limit": (
        "How old do I need to be to open an account?|Is there a minimum age limit?|"
        "Can my child have an account?|Can a seventeen year old register?|"
        "Are accounts available for minors and teenagers?"
    ),
    "apple_pay_or_google_pay": (
        "How do I add my card to Apple Pay?|Can I use Google Pay?|"
        "My card will not connect to the Apple wallet|Does the card support Google wallet?"
    ),
    "atm_support": (
        "Which ATMs can I use?|Where can I withdraw cash?|"
        "What cash machines accept my card?|Can I use an ATM abroad?|"
        "Where is the nearest supported cash machine?"
    ),
    "automatic_top_up": (
        "How do I enable automatic top ups?|Stop automatically adding money to my balance|"
        "Can I schedule regular top ups?|Automatically recharge when the balance is low|"
        "Change the amount of my auto top up"
    ),
    "balance_not_updated_after_bank_transfer": (
        "My bank transfer has not been added to my balance|"
        "I transferred money from my bank but my account is still empty|"
        "An incoming bank transfer has not arrived|"
        "The bank sent the money but my Revolut balance has not updated|"
        "Where is the money I deposited by bank transfer?"
    ),
    "balance_not_updated_after_cheque_or_cash_deposit": (
        "I deposited cash but my balance has not updated|"
        "My cheque deposit is not showing in the account|"
        "I paid in a check and the money has not arrived|"
        "The cash I deposited is missing"
    ),
    "beneficiary_not_allowed": (
        "Why is this beneficiary not allowed?|I cannot add this recipient|"
        "Transfers to this beneficiary are not permitted|"
        "The recipient account is unsupported|"
        "Why am I not allowed to send money to this particular beneficiary?"
    ),
    "cancel_transfer": (
        "How do I cancel a bank transfer?|Can I stop a transfer I just sent?|"
        "I sent money to the wrong account can I recall it?|"
        "Reverse my outgoing transfer|Cancel a scheduled money transfer"
    ),
    "card_about_to_expire": (
        "My card is about to expire|What happens when my card expires?|"
        "How do I renew an expired card?|My card expiry date is next month|"
        "Will I get a replacement before my card expires?"
    ),
    "card_acceptance": (
        "Where can I use my card?|Is my card accepted abroad?|"
        "Can I pay online with this card?|Which shops accept the card?|"
        "Can I use my card in another country?|Can I use the card at hotels and petrol stations?"
    ),
    "card_arrival": (
        "Where is the card I ordered?|My card has not arrived yet|"
        "How can I track my card delivery?|My card delivery is late|"
        "I ordered a card weeks ago and still have not received it|"
        "My card was sent to the wrong address"
    ),
    "card_delivery_estimate": (
        "How long does card delivery take?|When will my new card arrive?|"
        "What is the estimated card delivery date?|"
        "How many days will it take to receive a card?|"
        "Is express card delivery available?|Can you deliver my card faster?"
    ),
    "card_linking": (
        "How do I link my card to my account?|Connect my physical card to the app|"
        "My card is already linked to another account|"
        "How can I unlink a card?|Can I associate the new card with my account?"
    ),
    "card_not_working": (
        "My card is not working|My card has stopped functioning|"
        "The card does not work anywhere|There is a problem with my card|"
        "The chip on my card is damaged|My card does not work even though it is activated"
    ),
    "card_payment_fee_charged": (
        "Why was I charged a fee for a card payment?|"
        "There was an extra charge when I paid with my card|"
        "Do card purchases have a fee?|I paid at a shop and was charged a surcharge|"
        "Why does paying abroad with my card cost extra?"
    ),
    "card_payment_not_recognised": (
        "I do not recognise a card payment|There is a purchase I did not make|"
        "An unknown merchant charged my card|"
        "There is an unauthorized payment on my statement|"
        "I did not make this transaction|I have a charge from a shop I never visited"
    ),
    "card_payment_wrong_exchange_rate": (
        "The exchange rate for my card purchase is wrong|"
        "I paid abroad and the currency conversion was incorrect|"
        "My card payment used a bad exchange rate|"
        "The rate applied to my foreign card transaction was different than expected"
    ),
    "card_swallowed": (
        "The ATM swallowed my card|A cash machine kept my card|"
        "My card is stuck inside an ATM|The machine will not give my card back|"
        "The ATM retained my card"
    ),
    "cash_withdrawal_charge": (
        "Why was I charged a cash withdrawal fee?|"
        "Does withdrawing money from an ATM cost anything?|"
        "I was charged extra for taking cash out|What is the free ATM withdrawal allowance?|"
        "The ATM charged a commission"
    ),
    "cash_withdrawal_not_recognised": (
        "I do not recognise this cash withdrawal|"
        "There is an ATM transaction I did not make|"
        "Someone withdrew cash from my account|"
        "I never took this money out of a cash machine"
    ),
    "change_pin": (
        "How do I change my card PIN?|Can I reset the PIN number?|"
        "Where can I find my card PIN?|I forgot the PIN for my card|"
        "I want a different PIN for my debit card"
    ),
    "compromised_card": (
        "I think my card has been compromised|Someone has my card details|"
        "My card was cloned|My card details have been stolen|"
        "I gave my card information to a scammer|"
        "Someone is using my card without my permission|How do I freeze a compromised card?"
    ),
    "contactless_not_working": (
        "My contactless payment is not working|Tap to pay does not work|"
        "The card is not working when I tap it|"
        "Why does contactless keep getting declined?|"
        "The NFC function on my card is not working"
    ),
    "country_support": (
        "Which countries do you support?|Can I open an account in my country?|"
        "Is the service available to residents of Canada?|"
        "I live outside Europe can I register?|"
        "In which countries does Revolut operate?"
    ),
    "declined_card_payment": (
        "My card payment was declined|A shop rejected my card payment|"
        "Why did my online purchase get refused?|"
        "My payment did not go through|"
        "The merchant says my card transaction was declined"
    ),
    "declined_cash_withdrawal": (
        "The ATM declined my cash withdrawal|"
        "I cannot withdraw money from the cash machine|"
        "My cash withdrawal failed|"
        "The ATM rejected my card when I tried taking out money"
    ),
    "declined_transfer": (
        "My bank transfer was declined|Why was my transfer rejected?|"
        "The bank refused my outgoing transfer|"
        "My money transfer was denied|"
        "The transfer was blocked by the receiving bank"
    ),
    "direct_debit_payment_not_recognised": (
        "I do not recognise this direct debit|An unknown direct debit took money|"
        "I did not authorize a direct debit payment|"
        "There is a direct debit I never set up"
    ),
    "disposable_card_limits": (
        "What are the limits of disposable virtual cards?|"
        "How many disposable cards can I create?|"
        "Can I use a disposable card more than once?|"
        "Can I use a disposable virtual card for subscriptions?|"
        "Are there restrictions on single use cards?"
    ),
    "edit_personal_details": (
        "How do I change my personal details?|Update my address|"
        "I need to change my phone number|How do I correct my name?|"
        "Change the email address on my account|"
        "My personal information is wrong|Update my country of residence"
    ),
    "exchange_charge": (
        "Is there a fee for exchanging currencies?|"
        "Why was I charged a currency exchange commission?|"
        "What is the weekend exchange markup?|"
        "How much does converting money cost?|"
        "Are there charges when I exceed the exchange allowance?"
    ),
    "exchange_rate": (
        "What exchange rate do you use?|How are exchange rates calculated?|"
        "What is the current conversion rate?|"
        "Do you use the interbank exchange rate?|"
        "Where can I see the exchange rate between pounds and euros?"
    ),
    "exchange_via_app": (
        "How do I exchange currency in the app?|"
        "Can I convert pounds into euros?|"
        "How can I change money from one currency to another?|"
        "Where is the currency exchange feature?|"
        "Can I sell dollars and buy euros in the application?"
    ),
    "extra_charge_on_statement": (
        "I was charged an extra dollar on my account|"
        "Why is there a small extra charge on my statement?|"
        "There is a one pound verification charge|"
        "I see an additional one euro payment|"
        "Why was I charged one dollar when adding a card?|"
        "What is this small pending authorization charge?"
    ),
    "failed_transfer": (
        "My bank transfer failed|"
        "My transfer could not be completed|"
        "An error occurred when sending money|"
        "The transfer was unsuccessful|"
        "My transfer bounced back|"
        "My bank transfer was returned to my account"
    ),
    "fiat_currency_support": (
        "What currencies can I hold in my account?|"
        "Which fiat currencies are supported?|"
        "Can I keep a balance in dollars and euros?|"
        "Can I have accounts in several currencies?|"
        "Which currencies are available to exchange?"
    ),
    "get_disposable_virtual_card": (
        "How can I get a disposable virtual card?|"
        "Where do I create a single use card?|"
        "I want to generate a disposable card|"
        "What is a disposable virtual card?|"
        "How do I obtain a temporary one time card?"
    ),
    "get_physical_card": (
        "How can I get a physical card?|I want a real plastic card|"
        "Can I obtain a tangible card rather than a virtual one?|"
        "Do you provide physical cards?|"
        "I only have a virtual card how do I get a physical card?"
    ),
    "getting_spare_card": (
        "Can I get a spare card?|"
        "I would like a second card for my account|"
        "How do I order an additional card?|"
        "Can I have more than one physical card?|"
        "I want a backup card|Can I have two cards on one account?"
    ),
    "getting_virtual_card": (
        "How do I get a virtual card?|"
        "Can I create an online only card?|"
        "Where can I order a virtual card?|"
        "How do I generate a digital card number?|"
        "I need a card for online purchases without a physical card"
    ),
    "lost_or_stolen_card": (
        "I lost my card|My card was stolen|I cannot find my card|"
        "My wallet containing my card was stolen|"
        "How do I report a missing card?|"
        "I misplaced my card and need a replacement"
    ),
    "lost_or_stolen_phone": (
        "I lost my phone|My mobile phone was stolen|"
        "Someone stole the phone with my banking app|"
        "What should I do if my phone goes missing?|"
        "I cannot find my mobile"
    ),
    "order_physical_card": (
        "How do I order a physical card?|"
        "I want to order my first debit card|"
        "Can you send me a new card?|"
        "Where do I request a plastic card?|"
        "How much does it cost to order a card?|"
        "I need to apply for a card"
    ),
    "passcode_forgotten": (
        "I forgot my passcode|"
        "I cannot remember the password to log in|"
        "How do I reset my app login PIN?|"
        "I am locked out of my account|"
        "I forgot my security code for accessing the application"
    ),
    "pending_card_payment": (
        "Why is my card payment pending?|"
        "My purchase is still processing|"
        "A merchant payment has not completed|"
        "There is a pending transaction on my card|"
        "My card payment is stuck in authorization"
    ),
    "pending_cash_withdrawal": (
        "My cash withdrawal is still pending|"
        "The ATM transaction is processing|"
        "Why is my cash withdrawal showing as pending?|"
        "A withdrawal is still awaiting completion"
    ),
    "pending_top_up": (
        "My card top up is pending|"
        "The money I added is still processing|"
        "My top up has not reached my balance yet|"
        "Why is my top up taking so long?|"
        "I am waiting for a card deposit to complete"
    ),
    "pending_transfer": (
        "I have an outgoing transaction|"
        "My transfer is pending|"
        "Why is my outgoing transfer still processing?|"
        "The money transfer is stuck|"
        "My bank transfer has not completed yet|"
        "My transfer status says pending"
    ),
    "pin_blocked": (
        "My PIN is blocked|"
        "I entered the wrong PIN too many times|"
        "How do I unblock my card PIN?|"
        "I exceeded the number of PIN attempts|"
        "The card was blocked after three incorrect PIN entries"
    ),
    "receiving_money": (
        "How can I receive money?|"
        "Can someone send money to my account?|"
        "Can I receive my salary here?|"
        "How do I request money from a friend?|"
        "Can my employer pay me into this account?|"
        "Can I receive payments from other people?"
    ),
    "refund_not_showing_up": (
        "My refund has not arrived|"
        "A merchant refunded me but the money is not in my account|"
        "How long does a refund take to appear?|"
        "I returned an item but have not received the refund|"
        "I am still waiting for my refund"
    ),
    "request_refund": (
        "How do I request a refund?|"
        "I want my money back for a purchase|"
        "How do I dispute a card payment?|"
        "Can I get a chargeback?|"
        "I paid for an item that never arrived and want a refund"
    ),
    "reverted_card_payment": (
        "Why was my card payment reverted?|"
        "My completed card purchase was reversed|"
        "A merchant payment was returned to my account|"
        "My card transaction shows as reverted|"
        "The payment was cancelled automatically and the money came back"
    ),
    "supported_cards_and_currencies": (
        "Which cards can I use to top up?|"
        "Can I add money with American Express?|"
        "What currencies are supported for card top ups?|"
        "Are prepaid credit cards accepted for topping up?|"
        "Can I use someone else's debit card to add money?|"
        "Can I top up using a card in a different currency?"
    ),
    "terminate_account": (
        "How do I close my account?|"
        "I want to delete my account permanently|"
        "Cancel my account|"
        "I no longer want this account|"
        "How do I terminate my membership?"
    ),
    "top_up_by_bank_transfer_charge": (
        "Is there a fee to top up by bank transfer?|"
        "I was charged for an incoming bank transfer|"
        "Does adding money from my bank cost anything?|"
        "What are the charges for a bank transfer into my account?|"
        "There is a fee for funding my balance by wire transfer"
    ),
    "top_up_by_card_charge": (
        "Why was I charged for a card top up?|"
        "Is there a fee to add money with a credit card?|"
        "Does topping up by debit card cost extra?|"
        "I was charged commission when adding funds with my card"
    ),
    "top_up_by_cash_or_cheque": (
        "Can I top up by cash or cheque?|"
        "How can I deposit cash into my account?|"
        "Can I pay a check into the account?|"
        "Is cash deposit supported?|"
        "Can I add money at a bank branch with cash?"
    ),
    "top_up_failed": (
        "My card top up failed|"
        "I cannot add money with my debit card|"
        "Why was my top up declined?|"
        "There is an error when topping up|"
        "The app will not let me add funds"
    ),
    "top_up_limits": (
        "What is my top up limit?|"
        "What is the maximum amount I can add to my balance?|"
        "Is there a minimum card deposit?|"
        "How often can I top up?|"
        "How do I increase my funding limit?"
    ),
    "top_up_reverted": (
        "Why was my top up reverted?|"
        "My card top up was reversed|"
        "The money I added went back to my bank card|"
        "My deposit was returned to the original card|"
        "A successful top up was subsequently cancelled"
    ),
    "topping_up_by_card": (
        "How do I top up with a debit card?|"
        "Can I add money using a credit card?|"
        "How do I fund my account with another card?|"
        "Where do I enter my card details to add money?|"
        "How do I change the card I use for top ups?"
    ),
    "transaction_charged_twice": (
        "I was charged twice for the same transaction|"
        "There is a duplicate payment on my statement|"
        "The same purchase appears two times|"
        "A merchant debited my card twice|"
        "I only paid once but there are two charges"
    ),
    "transfer_fee_charged": (
        "Why was I charged a bank transfer fee?|"
        "Does sending money abroad cost extra?|"
        "What are your fees for outgoing transfers?|"
        "The recipient got less money because of a transfer charge|"
        "A commission was deducted from my transfer"
    ),
    "transfer_into_account": (
        "How do I transfer money into my account?|"
        "What bank details should I use for an incoming transfer?|"
        "Where can I find my IBAN and BIC?|"
        "How do I transfer funds from another bank?|"
        "What is my account number and sort code?|"
        "Can I make an international bank transfer to my account?"
    ),
    "transfer_not_received_by_recipient": (
        "The recipient has not received my transfer|"
        "I sent money but my friend has not got it|"
        "The beneficiary says the transfer never arrived|"
        "I transferred money to another bank account and it is missing|"
        "A completed transfer has not reached the recipient"
    ),
    "transfer_timing": (
        "How long does a bank transfer take?|"
        "When will the recipient get the money?|"
        "Are transfers processed on weekends?|"
        "How quickly will an international transfer arrive?|"
        "What time do you process outgoing transfers?"
    ),
    "unable_to_verify_identity": (
        "I cannot verify my identity|"
        "My identity verification failed|"
        "The app rejected my passport|"
        "I cannot upload my identification document|"
        "The identity check keeps getting stuck|"
        "My selfie is not being accepted"
    ),
    "verify_my_identity": (
        "How do I verify my identity?|"
        "What documents do I need for verification?|"
        "Can I use a driving licence as identification?|"
        "How long does identity verification take?|"
        "How do I know if my identity is verified?|"
        "Where do I upload my passport and selfie?"
    ),
    "verify_source_of_funds": (
        "How do I verify my source of funds?|"
        "What proof of income do you need?|"
        "Why must I show where my money came from?|"
        "How do I provide a payslip or bank statement?|"
        "I need to verify the origin of my wealth"
    ),
    "verify_top_up": (
        "How do I verify my top up card?|"
        "Where is the card verification code on my bank statement?|"
        "How can I authenticate the card used to add money?|"
        "My top up needs verification|"
        "I cannot find the four digit top up verification code"
    ),
    "virtual_card_not_working": (
        "My virtual card is not working|"
        "My virtual card payment was declined|"
        "I cannot pay online with the digital card|"
        "My online only card does not work|"
        "My virtual card has been rejected"
    ),
    "visa_or_mastercard": (
        "Will I receive a Visa or Mastercard?|"
        "Can I choose between Visa and Mastercard?|"
        "What card brand do you issue?|"
        "I want a Visa instead of a Mastercard|"
        "Do you offer both Visa and Mastercard?"
    ),
    "why_verify_identity": (
        "Why do I need to verify my identity?|"
        "Why are you asking for my passport?|"
        "Is identity verification mandatory?|"
        "Can I use the account without verifying my identity?|"
        "Why must I upload personal identification documents?"
    ),
    "wrong_amount_of_cash_received": (
        "The ATM gave me the wrong amount of cash|"
        "I received less cash than I requested|"
        "The cash machine did not dispense money but my account was debited|"
        "The ATM gave only part of my withdrawal|"
        "I was charged for a withdrawal but no cash came out"
    ),
    "wrong_exchange_rate_for_cash_withdrawal": (
        "The ATM withdrawal used the wrong exchange rate|"
        "The currency conversion for my cash withdrawal is incorrect|"
        "I got a bad exchange rate when withdrawing abroad|"
        "Why was the cash machine conversion rate different?"
    ),
}


def _extract_text(state):
    if isinstance(state, str):
        return state
    if isinstance(state, dict):
        for key in ("text", "message", "utterance", "query", "content", "input", "state"):
            if key in state:
                value = state[key]
                if isinstance(value, str):
                    return value
                if isinstance(value, (dict, list, tuple)):
                    found = _extract_text(value)
                    if found:
                        return found
        parts = [v for v in state.values() if isinstance(v, str)]
        return " ".join(parts)
    if isinstance(state, (list, tuple)):
        return " ".join(_extract_text(part) for part in state)
    return ""


def _normalize(text):
    text = unicodedata.normalize("NFKC", text).lower()
    text = "".join(c for c in unicodedata.normalize("NFKD", text)
                   if not unicodedata.combining(c))
    text = text.replace("’", "'").replace("`", "'")
    text = re.sub(r"\bcan[' ]?t\b", "cannot", text)
    text = re.sub(r"\bwon't\b", "will not", text)
    text = re.sub(r"\bshan't\b", "shall not", text)
    text = re.sub(r"\bain't\b", "is not", text)
    text = re.sub(r"\b(\w+)n't\b", r"\1 not", text)
    text = re.sub(r"\b(\w+)'ve\b", r"\1 have", text)
    text = re.sub(r"\b(\w+)'re\b", r"\1 are", text)
    text = re.sub(r"\b(\w+)'ll\b", r"\1 will", text)
    text = re.sub(r"\bi'm\b", "i am", text)
    text = re.sub(r"\b(\w+)'d\b", r"\1 would", text)
    text = re.sub(r"\b(\w+)'s\b", r"\1 is", text)
    text = re.sub(r"[_‐‑–—-]", " ", text)
    text = re.sub(r"\b(?:topup|topups|top\s+ups|topping\s+up|topped\s+up|tops\s+up)\b",
                  "top up", text)
    replacements = {
        "recieve": "receive", "recieved": "received", "recieving": "receiving",
        "recepient": "recipient", "recipent": "recipient",
        "benificiary": "beneficiary", "beneficary": "beneficiary",
        "transation": "transaction", "transction": "transaction",
        "tranfer": "transfer", "transferred": "transferred",
        "withdrawl": "withdrawal", "withdrawls": "withdrawals",
        "withdrewal": "withdrawal", "withdrwal": "withdrawal",
        "verfication": "verification", "verifcation": "verification",
        "identitiy": "identity", "adress": "address",
        "dident": "did not", "cant": "cannot", "dont": "do not",
        "doesnt": "does not", "isnt": "is not", "havent": "have not",
        "hasnt": "has not", "didnt": "did not", "wont": "will not",
        "applepay": "apple pay", "googlepay": "google pay", "gpay": "google pay",
        "mastercard": "mastercard", "cashpoint": "atm", "cashpoints": "atms",
        "paywave": "contactless", "paypass": "contactless",
        "recognize": "recognise", "recognized": "recognised",
        "unrecognized": "unrecognised", "unauthorized": "unauthorised",
        "canceled": "cancelled", "canceling": "cancelling",
        "checkbook": "chequebook", "prepaid": "prepaid",
    }
    text = re.sub(r"\b[a-z]+\b", lambda m: replacements.get(m.group(), m.group()), text)
    text = re.sub(r"\bmaster\s+card\b", "mastercard", text)
    text = re.sub(r"\bcontact\s+less\b", "contactless", text)
    text = re.sub(r"\bpre\s+paid\b", "prepaid", text)
    return re.sub(r"\s+", " ", text).strip()


_STOPWORDS = set(
    "a an the i me my mine we us our ours you your yours they them their theirs "
    "he him his she her hers it its is are am was were be been being "
    "do does did have has had having will would could should shall may might "
    "can please just really very also still already even actually recently "
    "to of for on in at by with from as and or but if then that this these those "
    "there here any some something anything about regarding into through "
    "how what which who whom where why want wants wanted need needs needed "
    "like know tell help thanks thank hello hi hey now get getting got".split()
)

_TOKEN_ALIASES = {
    "cards": "card", "debits": "debit", "credits": "credit",
    "physical": "physical", "plastic": "physical", "tangible": "physical",
    "payments": "payment", "purchases": "purchase", "bought": "purchase",
    "shopping": "purchase", "purchasing": "purchase", "paid": "pay",
    "paying": "pay", "transactions": "transaction",
    "charged": "charge", "charging": "charge", "charges": "charge",
    "fees": "fee", "cost": "fee", "costs": "fee", "commission": "fee",
    "surcharge": "fee", "surcharges": "fee",
    "withdrawals": "withdrawal", "withdrawing": "withdrawal",
    "withdraw": "withdrawal", "withdrew": "withdrawal", "withdrawn": "withdrawal",
    "atms": "atm",
    "transfers": "transfer", "transferred": "transfer", "transferring": "transfer",
    "remittance": "transfer", "remittances": "transfer", "wire": "bank transfer",
    "sent": "send", "sending": "send", "funds": "money", "fund": "money",
    "adding": "add", "added": "add", "loading": "add", "loaded": "add",
    "recharge": "top up", "reload": "top up",
    "depositing": "deposit", "deposited": "deposit", "deposits": "deposit",
    "cheques": "cheque", "checks": "cheque",
    "declined": "decline", "reject": "decline", "rejected": "decline",
    "refused": "decline", "denied": "decline",
    "failed": "fail", "fails": "fail", "failure": "fail", "failing": "fail",
    "unsuccessful": "fail", "errors": "error",
    "working": "work", "works": "work", "functioning": "work", "function": "work",
    "unable": "cannot",
    "processing": "pending", "unsettled": "pending",
    "reverted": "revert", "reversed": "revert", "reversal": "revert",
    "refunded": "refund", "refunds": "refund", "refunding": "refund",
    "received": "receive", "receiving": "receive",
    "arrived": "arrive", "arrival": "arrive", "arriving": "arrive",
    "delivered": "delivery", "deliver": "delivery", "delivering": "delivery",
    "shipping": "delivery", "shipment": "delivery", "shipped": "delivery",
    "tracking": "track",
    "ordered": "order", "ordering": "order", "requesting": "request",
    "activate": "activate", "activating": "activate", "activation": "activate",
    "activated": "activate", "activates": "activate",
    "verify": "verify", "verification": "verify", "verified": "verify",
    "verifying": "verify", "authenticate": "verify", "authentication": "verify",
    "identification": "identity", "id": "identity", "kyc": "identity",
    "documents": "document", "photos": "photo", "photograph": "photo",
    "changing": "change", "changed": "change", "edit": "change",
    "editing": "change", "update": "change", "updating": "change",
    "details": "detail", "information": "detail",
    "password": "passcode", "passwords": "passcode", "passcodes": "passcode",
    "forgotten": "forget", "forgot": "forget", "remember": "remember",
    "stolen": "lost", "misplaced": "lost", "missing": "missing",
    "mobiles": "phone", "mobile": "phone", "smartphone": "phone",
    "expiring": "expire", "expired": "expire", "expires": "expire",
    "expiry": "expire", "expiration": "expire",
    "limits": "limit", "maximum": "limit", "minimum": "limit",
    "restriction": "limit", "restrictions": "limit",
    "currencies": "currency", "conversion": "exchange", "convert": "exchange",
    "converting": "exchange", "converted": "exchange", "exchanging": "exchange",
    "rates": "rate", "dollars": "dollar", "pounds": "pound", "euros": "euro",
    "supported": "support", "supports": "support",
    "accepts": "accept", "accepted": "accept", "acceptance": "accept",
    "available": "support",
    "countries": "country", "residents": "resident", "residing": "resident",
    "abroad": "international", "overseas": "international",
    "beneficiary": "recipient", "beneficiaries": "recipient",
    "recipients": "recipient",
    "unrecognised": "unknown", "unrecognizable": "unknown",
    "unauthorised": "unknown", "unfamiliar": "unknown",
    "fraudulent": "fraud", "fraudster": "fraud", "scammer": "fraud",
    "incorrect": "wrong", "inaccurate": "wrong",
    "duplicate": "twice", "duplicated": "twice", "double": "twice",
    "automatically": "automatic", "auto": "automatic",
    "spare": "spare", "backup": "spare", "additional": "extra",
    "terminate": "close", "termination": "close", "delete": "close",
    "closing": "close", "deleting": "close", "closed": "close",
    "swallowed": "swallow", "retained": "swallow", "eaten": "swallow",
    "blocked": "block", "blocking": "block",
    "linking": "link", "linked": "link", "associate": "link", "connect": "link",
    "accounts": "account", "balances": "balance", "statements": "statement",
    "merchants": "merchant", "shops": "shop", "stores": "shop",
    "cancelled": "cancel", "cancelling": "cancel",
}


def _features(text):
    words = []
    for word in re.findall(r"[a-z]+|\d+(?:\.\d+)?", text):
        if word in _STOPWORDS:
            continue
        replacement = _TOKEN_ALIASES.get(word, word)
        for part in replacement.split():
            if part not in _STOPWORDS:
                words.append(part)
    counts = Counter(words)
    for a, b in zip(words, words[1:]):
        counts[a + "~" + b] += 0.65
    if re.search(r"\b(?:how long|how many days|when will|delivery time)\b", text):
        counts["timing"] += 1
    if re.search(r"\b(?:not|never|no)\b.{0,30}\b(?:arriv\w*|receiv\w*|show\w*)\b", text):
        counts["missing"] += 1
    if re.search(r"\b(?:do not|cannot)\s+recognise\b", text):
        counts["unknown"] += 1
    return counts


@lru_cache(maxsize=1)
def _prototype_model():
    label_features = {}
    document_frequency = Counter()
    vocabulary = set()
    for label, phrases in _PROTOTYPES.items():
        rows = [_features(_normalize(p)) for p in phrases.split("|")]
        label_features[label] = rows
        present = set()
        for row in rows:
            present.update(row)
            vocabulary.update(w for w in row if "~" not in w)
        document_frequency.update(present)
    n = len(_PROTOTYPES)
    idf = {w: 1.0 + math.log((n + 1.0) / (freq + 1.0))
           for w, freq in document_frequency.items()}
    vectors = {}
    for label, rows in label_features.items():
        vectors[label] = []
        for row in rows:
            vector = {w: math.sqrt(v) * idf[w] for w, v in row.items()}
            norm = math.sqrt(sum(v * v for v in vector.values())) or 1.0
            vectors[label].append({w: v / norm for w, v in vector.items()})
    return idf, vectors, tuple(sorted(vocabulary))


def _nearest_intent(text):
    idf, vectors, vocabulary = _prototype_model()
    counts = _features(text)
    corrected = Counter()
    for word, count in counts.items():
        if word in idf:
            corrected[word] += count
        elif "~" not in word and len(word) >= 5:
            close = get_close_matches(word, vocabulary, n=1, cutoff=0.88)
            if close:
                corrected[close[0]] += count * 0.75
    query = {w: math.sqrt(v) * idf[w] for w, v in corrected.items()}
    norm = math.sqrt(sum(v * v for v in query.values())) or 1.0
    query = {w: v / norm for w, v in query.items()}
    best_label = "pending_transfer"
    best_score = 0.0
    for label, rows in vectors.items():
        scores = sorted(
            (sum(v * row.get(w, 0.0) for w, v in query.items()) for row in rows),
            reverse=True,
        )
        score = scores[0]
        if len(scores) > 1:
            score += 0.12 * scores[1]
        if len(scores) > 2:
            score += 0.04 * scores[2]
        if score > best_score:
            best_score = score
            best_label = label
    return best_label


def _classify(text):
    t = _normalize(text)
    plain = re.sub(r"[^\w ]+", "", t).strip()
    if plain == "i have an outgoing transaction":
        return "pending_transfer"
    for label in _PROTOTYPES:
        if plain == label.replace("_", " "):
            return label

    def h(pattern):
        return re.search(pattern, t) is not None

    card = h(r"\b(?:cards?|visa|mastercard|amex|american express|plastic)\b")
    physical = h(r"\b(?:physical|plastic|tangible|real|actual)\s+(?:debit\s+|bank\s+)?card\b")
    virtual = h(r"\bvirtual\b|\bdigital\s+card\b|\bonline only\s+card\b")
    disposable = h(r"\bdisposable\b|\b(?:single|one|1)\s+(?:use|time)\s+(?:virtual\s+)?card\b|\btemporary\s+(?:virtual\s+)?card\b")
    payment = h(r"\b(?:payments?|purchases?|transactions?|merchant|retailer|shopping|checkout|bought)\b|\bpaid\b|\bpay(?:ing)?\s+(?:with|by|for|at|online|in)\b")
    withdrawal = h(r"\b(?:withdraw\w*|withdrew|atms?)\b|\bcash\s+(?:machine|point)\b|\b(?:take|taking|took|taken|get|getting|got|pull|pulling)\s+(?:some\s+|my\s+|the\s+)?(?:money|cash)\s+out\b|\b(?:take|taking|took)\s+out\s+(?:some\s+|the\s+)?(?:cash|money)\b")
    top_explicit = h(r"\btop\s+up\b|\b(?:recharge|reload)\b")
    adding = h(r"\b(?:add|adding|added|load|loading|loaded|deposit|depositing|deposited|put|putting)\b.{0,45}\b(?:money|funds|balance|account|revolut)\b|\b(?:fund|funding)\s+(?:my|the|an?|your|this)\s+(?:revolut\s+)?account\b")
    cash_deposit = h(r"\bcheques?\b|\bchecks?\s+(?:deposit|into|to\s+(?:my|the)\s+account)\b|\b(?:deposit|depositing|deposited|cash|cashing|pay|paid|put)\s+(?:in\s+)?(?:a\s+|my\s+|the\s+)?check\b|\b(?:cash\s+deposit|deposit\w*\s+(?:some\s+|my\s+|the\s+)?cash)\b|\b(?:add|adding|added|pay|paying|paid|put|putting|load|loading|fund|funding)\b.{0,25}\bcash\b.{0,35}\b(?:account|balance|into|onto|revolut)\b|\bcash\b.{0,20}\b(?:into|to|in)\s+(?:my|an?|the)\s+(?:revolut\s+)?account\b")
    if top_explicit and h(r"\b(?:cash|cheques?|checks?)\b") and not withdrawal:
        cash_deposit = True
    transfer = h(r"\b(?:transfers?|transferred|transferring|remittance|wire|wired|wiring|iban|bic|swift|beneficiar\w*|recipient)\b|\bbank\s+payment\b|\b(?:sort|routing)\s+(?:code|number)\b|\b(?:send|sending|sent)\b.{0,30}\b(?:money|funds|payment)\b|\b(?:outgoing|incoming)\s+transaction\b")
    bank_method = h(r"\bbank\s+(?:wire\s+)?transfer\b|\bwire(?:d)?\b|\bswift\b|\btransfer\w*\b.{0,35}\b(?:bank|iban)\b|\b(?:bank|iban)\b.{0,35}\btransfer\w*\b")
    incoming = h(r"\bincoming\b|\binbound\b|\b(?:into|to)\s+my\s+(?:revolut\s+)?(?:account|balance)\b|\b(?:from|via)\s+my\s+(?:other\s+|external\s+)?bank\b|\bfrom\s+(?:another|an external|a different)\s+bank\b|\b(?:fund|funding|top up)\b|\b(?:add|adding|added)\s+(?:money|funds)\b")
    outgoing = h(r"\boutgoing\b|\boutbound\b|\b(?:send|sending|sent)\b|\b(?:to|into)\s+(?:another|an external|a different|my other)\s+(?:bank\s+)?account\b|\bto\s+my\s+(?:other\s+)?bank\b")
    recipient = h(r"\b(?:recipient|beneficiary|receiver|receiving bank|destination account)\b|\b(?:my|a|the)\s+(?:friend|mate|brother|sister|mother|father|partner|wife|husband|landlord|supplier)\b|\b(?:person|someone)\s+(?:i|who|that)\s+(?:sent|paid)\b")
    topup = top_explicit or (adding and not cash_deposit and not bank_method)
    bank_funding = transfer and (incoming or top_explicit or (adding and bank_method))

    positive_status = re.sub(
        r"\b(?:not|never)\s+(?:been\s+)?(?:declined|rejected|failed|blocked)\b", "", t
    )
    declined = re.search(r"\b(?:declin\w*|reject\w*|refus\w*|denied)\b", positive_status) is not None
    declined = declined or h(r"\bnot\s+(?:being\s+)?accepted\b")
    failed = h(r"\b(?:fail\w*|unsuccessful|error|errors|malfunction\w*|broken|damaged)\b|\b(?:not|no longer|never)\s+(?:seem\s+to\s+)?work\w*\b|\bstopp?ed\s+(?:working|functioning)\b|\b(?:cannot|unable to|will not|does not|did not|could not)\b.{0,25}\b(?:pay|make|complete|work|use|withdraw|add|top up|send|transfer|load|deposit|verify|upload|process)\b|\b(?:not|never)\s+(?:go|going|gone|went)\s+through\b|\b(?:problem|trouble|issue)\b")
    pending = h(r"\b(?:pending|processing|unsettled|in progress|on hold|awaiting|stuck)\b|\bnot\s+(?:yet\s+)?(?:completed|cleared|processed|settled)\b|\bstill\s+(?:waiting|incomplete)\b|\b(?:taking|takes|taken)\s+(?:so|too|a very)\s+long\b")
    reverted = h(r"\b(?:revert\w*|revers\w*|bounced?)\b|\b(?:returned|sent|went|going|credited|paid)\s+back\b|\breturned\s+to\b|\b(?:cancelled|canceled)\s+automatically\b")
    missing = h(r"\b(?:not|never|no|nothing)\b.{0,45}\b(?:receiv\w*|arriv\w*|reach\w*|show\w*|appear\w*|reflect\w*|credit\w*|updat\w*|come|came|happen\w*)\b|\b(?:have|has|is|are|was|were)\s+not\s+(?:there|here)\b|\b(?:missing|disappeared|vanished|empty)\b|\bwhere\s+(?:is|are)\s+(?:my|the)\s+(?:money|funds|deposit|transfer)\b|\bbalance\b.{0,25}\b(?:same|unchanged|zero)\b|\b(?:have|got|received)\s+not?hing\b")
    timing = h(r"\bhow\s+(?:long|soon|quickly|fast|many\s+(?:days|hours|weeks))\b|\bwhen\b|\b(?:timeframe|timescale|eta|estimated|estimate|duration)\b|\b(?:delivery|processing|transfer|arrival)\s+(?:time|date|speed)\b|\b(?:weekends?|working days|business days|bank holidays)\b")
    fees = h(r"\b(?:fees?|surcharges?|commissions?|costs?|pricing|markup|mark up|charges)\b|\b(?:extra|additional|unexpected|hidden|excess|higher)\s+(?:charge|payment|money|amount|deduction)\b|\b(?:charged|debited|deducted|paying|paid|pay)\s+(?:me\s+)?(?:an?\s+)?(?:extra|more|additional)\b|\bovercharg\w*\b|\bcharge\s+(?:me\s+)?(?:for|to)\b|\bcharged\s+(?:me\s+)?for\b|\b(?:free|free of charge)\b|\bhow much\b.{0,20}\b(?:charge|pay|cost)\b")
    extra = h(r"\b(?:extra|additional|unexpected|hidden|more|excess|surcharge|overcharg\w*)\b")
    limits = h(r"\b(?:limits?|maximum|minimum|restrictions?|threshold|ceiling|cap|capped|allowance)\b|\bhow\s+(?:much|many|often)\b|\bmore than once\b|\b(?:increase|raise)\b.{0,20}\b(?:amount|add|deposit)\b")
    exchange = h(r"\b(?:exchange|exchanging|convert\w*|conversion|fx|interbank|forex)\b|\b(?:currency|foreign)\s+rate\b|\brate\b")
    wrong = h(r"\b(?:wrong|incorrect|inaccurate|bad|poor|unfair|unexpected|different|unfavourable|unfavorable|awful|terrible|worse|rip off|ripped off|too high|too low)\b|\b(?:higher|lower|more|less)\b.{0,25}\b(?:expected|shown|advertised|supposed)\b")
    unknown = h(r"\b(?:unrecognised|unauthorised|unknown|unfamiliar|unapproved|fraudulent|suspicious)\b|\b(?:do not|did not|cannot|does not)\s+recognise\b|\b(?:never|not)\s+(?:made|make|authorised|authorize|authorise|approved|approve|bought|purchased|visited|paid|used|withdrawn|withdrew)\b|\b(?:did not|never)\s+(?:buy|purchase|pay|use|withdraw|make|take out|shop|visit)\b|\bnot\s+(?:my|mine)\b|\bno\s+(?:idea|clue)\b.{0,35}\b(?:charge|payment|transaction|merchant)\b|\b(?:someone|somebody)\s+(?:else\s+)?(?:withdrew|withdrawn|took)\b")
    issue = failed or declined or missing or pending

    # Account access, security, and explicit administrative requests.
    if h(r"\b(?:phone|mobile|cellphone|smartphone|device)\b") and h(
        r"\b(?:lost|stolen|stole|misplaced|missing|robbed)\b|\b(?:cannot|can not)\s+find\b"
    ):
        if not h(r"\b(?:lost|forgot)\s+(?:my\s+)?(?:passcode|password|pin|login)\b") or h(
            r"\b(?:phone|mobile)\b.{0,15}\b(?:lost|stolen|missing)\b|\b(?:lost|stolen)\b.{0,15}\b(?:phone|mobile)\b"
        ):
            return "lost_or_stolen_phone"

    if withdrawal and card and h(
        r"\b(?:swallow\w*|retain\w*|ate|eaten|eats|captur\w*|confiscat\w*|trapped)\b|"
        r"\b(?:kept|keep|keeps|stuck|left)\b.{0,30}\b(?:card|atm|machine)\b|"
        r"\b(?:atm|machine)\b.{0,25}\b(?:kept|keep|stuck|took)\b|"
        r"\b(?:not|never|cannot)\b.{0,25}\b(?:return|give|retrieve|release|eject)\b"
    ):
        return "card_swallowed"

    if h(r"\b(?:close|closing|delete|deleting|terminate|terminating|cancel|deactivate|shut|remove)\b.{0,40}\b(?:account|membership|profile)\b|\b(?:account|membership)\b.{0,25}\b(?:closure|termination|deletion)\b|\bno longer\s+(?:want|need)\b.{0,20}\baccount\b"):
        return "terminate_account"

    if h(r"\b(?:age|old enough|too young|minor|minors|underage|teenager|teenagers|teen|child|children|junior)\b|\b\d{1,2}\s+(?:years?\s+old|yr\s+old)\b|\b(?:under|over|below|above)\s+(?:18|eighteen|16|sixteen)\b|\bhow old\b"):
        if not h(r"\b(?:card|transfer|payment)\s+(?:age|is old)\b"):
            return "age_limit"

    if h(r"\b(?:apple\s*(?:pay|wallet)|google\s*(?:pay|wallet)|android pay|samsung pay)\b"):
        return "apple_pay_or_google_pay"

    if h(r"\b(?:automatic|automatically|auto|scheduled|recurring|regular)\b.{0,45}\b(?:top up|recharge|reload|add|fund|deposit)\b|\b(?:top up|recharge|reload)\b.{0,45}\b(?:automatic|automatically|auto|schedule|scheduled|recurring|low|threshold)\b|\b(?:balance|funds)\b.{0,30}\b(?:falls?|drops?|below|runs? low)\b") and not (transfer and not topup):
        return "automatic_top_up"

    if h(r"\bdirect\s+debits?\b|\bdd\s+payment\b"):
        return "direct_debit_payment_not_recognised"

    if h(r"\b(?:change|changing|edit|editing|update|updating|correct|correction|amend|replace|new|wrong|incorrect)\b") and h(
        r"\b(?:personal\s+(?:details|information|data)|name|surname|last name|first name|married name|address|email|e mail|phone number|telephone number|mobile number|date of birth|birth date|dob|country of residence|residential|nationality|citizenship)\b"
    ):
        if not h(r"\b(?:recipient|beneficiary|merchant)\s+(?:name|address|details)\b"):
            return "edit_personal_details"

    login = h(r"\b(?:passcode|password|login|log in|sign in|logging in|access the app|access my account|locked out|unlock the app)\b")
    if login and (h(r"\b(?:forgot|forgotten|forget|lost|reset|recover|change|cannot|unable|blocked|locked|wrong|incorrect)\b") or not transfer):
        if not (h(r"\b(?:verification|verify|identity)\b") and not h(r"\b(?:passcode|password|forgot|forgotten)\b")):
            return "passcode_forgotten"

    if h(r"\bpin\b"):
        if h(r"\b(?:block\w*|unblock\w*|lock\w*|unlock\w*|tries|attempts|attempted|exceeded)\b|\b(?:three|3|too many|several|multiple)\s+(?:times|wrong|incorrect)\b"):
            return "pin_blocked"
        if h(r"\b(?:change|reset|new|different|forgot|forget|forgotten|remember|find|view|see|retrieve|show)\b|\bwhat\s+is\s+my\b"):
            return "change_pin"

    # Identity and funding verification are distinct from card activation.
    if h(r"\b(?:source|origin)\s+of\s+(?:my\s+|the\s+)?(?:funds|money|wealth|income)\b|\b(?:proof|prove|verify|verification|evidence)\b.{0,35}\b(?:income|earnings|salary|wealth|funds|funding)\b|\b(?:payslip|pay slip|proof of income)\b|\bwhere\b.{0,20}\b(?:money|funds)\b.{0,20}\b(?:come|came|coming)\s+from\b"):
        return "verify_source_of_funds"

    verification = h(r"\b(?:verif\w*|authenticat\w*|confirm\w*|validation|validate)\b")
    identity = h(r"\b(?:identity|identification|passport|selfie|kyc|id|driving licen[cs]e|driver licen[cs]e|drivers licen[cs]e|residence permit)\b|\b(?:identity|document)\s+check\b")
    if (verification and (topup or h(r"\b(?:bank|debit|credit|payment|top up)\s+card\b"))) or h(
        r"\b(?:four|4)\s+digit\b.{0,30}\b(?:statement|verification|top up|bank)\b|"
        r"\b(?:verification|confirmation|authentication|security)\s+code\b.{0,40}\b(?:statement|top up|bank card)\b|"
        r"\b(?:statement|top up)\b.{0,40}\b(?:verification|confirmation|four digit|4 digit)\b|"
        r"\bverify\s+(?:my|the|a|your)\s+card\b"
    ):
        if not identity:
            return "verify_top_up"

    if identity or (verification and not (card or transfer or payment or topup)):
        identity_failure = h(
            r"\b(?:fail\w*|reject\w*|declin\w*|error|stuck|unsuccessful|problem|trouble|issue)\b|"
            r"\b(?:cannot|unable|will not|does not|did not|could not)\b.{0,40}\b(?:verify|upload|scan|accept|recognise|complete|take|submit|work|pass)\b|"
            r"\bnot\s+(?:working|accepted|accepting|recognised|going through)\b|"
            r"\b(?:verification|identity check)\b.{0,25}\b(?:too long|taking ages|days ago|weeks)\b"
        )
        if identity_failure:
            return "unable_to_verify_identity"
        if h(r"\b(?:why|reason|purpose|necessary|mandatory|compulsory|obligatory|required|privacy|without)\b") and not h(
            r"\b(?:what|which)\s+(?:documents?|id|identification|proof)\b"
        ):
            return "why_verify_identity"
        return "verify_my_identity"

    # Physical loss and compromise are different security problems.
    compromised = h(
        r"\b(?:compromis\w*|clon\w*|skim\w*|hack\w*|phish\w*|leak\w*)\b|"
        r"\bcard\s+(?:details|information|number|data)\b.{0,40}\b(?:stolen|exposed|someone|somebody|fraud|scam|obtained|shared)\b|"
        r"\b(?:someone|somebody|scammer|fraudster)\b.{0,35}\b(?:card details|card information|card number|using my card|used my card|access to my card)\b|"
        r"\b(?:gave|shared|sent)\b.{0,20}\bcard\s+(?:details|information|number)\b|"
        r"\b(?:stolen|stole)\b.{0,15}\bcard\s+(?:details|information|number)\b"
    )
    if compromised and not (withdrawal and unknown):
        return "compromised_card"

    loss = h(
        r"\b(?:lost|stolen|misplaced|missing)\s+(?:my\s+|the\s+|a\s+|bank\s+|debit\s+|credit\s+|physical\s+)*card\b|"
        r"\b(?:lost|misplaced)\s+my\s+wallet\b|"
        r"\b(?:card|wallet|purse)\b.{0,25}\b(?:lost|stolen|misplaced|missing|robbed)\b|"
        r"\b(?:cannot|could not)\s+find\b.{0,20}\b(?:card|wallet)\b|"
        r"\b(?:someone|somebody|thief)\b.{0,20}\b(?:stole|taken|took)\b.{0,15}\bcard\b"
    )
    if loss and not h(r"\b(?:not lost|not stolen|still have my card|have my card with me|card in my possession)\b"):
        if not h(r"\b(?:delivery|delivered|ordered|shipment|post|mail|not arrived|never arrived)\b"):
            return "lost_or_stolen_card"

    if card and h(r"\b(?:expir\w*|out of date|valid until|valid thru|renew|renewal)\b"):
        if not topup or h(r"\b(?:renew|replacement|replace|new card)\b"):
            return "card_about_to_expire"

    # Duplicate and small authorization charges have their own intents.
    if h(r"\b(?:twice|duplicate|duplicated|double charged|double billed|double payment|two times|more than once)\b") and h(
        r"\b(?:charge\w*|payment|transaction|purchase|debit\w*|paid|billed)\b"
    ):
        return "transaction_charged_twice"
    if h(r"\b(?:two|2)\s+(?:identical|same|separate)?\s*(?:charges|payments|transactions)\b|\b(?:same|one|single)\s+(?:purchase|transaction|payment)\b.{0,45}\b(?:two|2|double)\b|\bpaid\s+once\b.{0,35}\b(?:two|2|double)\b"):
        return "transaction_charged_twice"

    small_charge = h(
        r"(?:[$£€]\s*(?:1(?:\.00)?|0\.0[01]))\b|"
        r"\b(?:1(?:\.00)?|one|an? extra|an? additional|extra|additional)\s+(?:dollar|pound|euro)\b|"
        r"\b(?:1|one)\s+(?:usd|gbp|eur)\b|"
        r"\b(?:small|tiny|nominal|test|verification|authorisation|authorization)\s+(?:extra\s+)?(?:charge|payment|transaction|amount|fee)\b"
    )
    if small_charge and not withdrawal:
        if h(r"\b(?:charg\w*|statement|debit\w*|payment|transaction|deduct\w*|verif\w*|extra|additional|authoris\w*|authoriz\w*)\b"):
            return "extra_charge_on_statement"

    if h(r"\bcontactless\b|\bnfc\b|\btap\s+(?:to\s+pay|and\s+(?:pay|go))\b|\b(?:tap|tapping|tapped|wave|waving)\b.{0,20}\b(?:card|reader|terminal)\b"):
        if not h(r"\bcontactless\s+(?:works|is working|worked fine)\b") or issue:
            return "contactless_not_working"

    # Refunds refer either to obtaining one or to an already expected credit.
    refund = h(r"\brefund\w*\b|\bcharge\s*back\b|\bchargeback\b|\bmoney\s+back\b|\bdispute\b")
    if refund and not (topup and reverted and not h(r"\brefund\b")):
        refund_wait = h(
            r"\b(?:refunded|refund issued|refund processed|refund confirmed|awaiting.*refund|waiting.*refund|pending.*refund)\b|"
            r"\b(?:merchant|shop|store|retailer|seller)\b.{0,45}\b(?:refunded|issued|processed|promised|sent|returned)\b|"
            r"\brefund\b.{0,45}\b(?:not|never|missing|pending|late|where|waiting|processing|arrive|appear|show|take|takes|taking)\b|"
            r"\b(?:where|when|how long)\b.{0,60}\brefund\b|"
            r"\breturned\b.{0,35}\b(?:item|goods|purchase|product)\b"
        )
        if refund_wait or (h(r"\brefund\w*\b") and (missing or pending)):
            return "refund_not_showing_up"
        if not (unknown and not h(r"\b(?:request|want|need|chargeback|dispute|get)\b.{0,25}\b(?:refund|money back)\b")):
            return "request_refund"

    # Transfer restrictions and recall requests should not become generic failures.
    if transfer and (
        h(r"\b(?:cancel|stop|recall|reverse|undo|revoke|abort)\b")
        or h(r"\b(?:sent|transferred)\b.{0,40}\bwrong\s+(?:account|person|recipient|beneficiary)\b")
    ):
        if not h(r"\b(?:was|is|been|automatically|got)\s+(?:automatically\s+)?(?:cancelled|reversed|stopped)\b") or h(
            r"\b(?:how|can i|could i|want|need|please)\b.{0,35}\b(?:cancel|stop|recall|reverse|undo)\b"
        ):
            return "cancel_transfer"

    if h(r"\b(?:beneficiary|recipient|receiving account|destination account)\b") and h(
        r"\b(?:not allowed|not permitted|not supported|unsupported|not eligible|forbidden|restricted|blacklisted|blocked|invalid)\b|"
        r"\b(?:cannot|unable to|will not let me|does not let me)\b.{0,20}\b(?:add|create|set up|save)\b"
    ):
        return "beneficiary_not_allowed"
    if h(r"\bbeneficiary\b") and h(r"\b(?:not|cannot|unable|problem|error|refused|rejected)\b") and not h(r"\btransfer\s+(?:was|is|got|has been)\s+(?:declined|rejected)\b"):
        return "beneficiary_not_allowed"

    if disposable:
        if limits or h(r"\b(?:reuse|re use|use again|multiple times|once|subscriptions?|recurring payments?|cash|atm|restrictions?|allowed|per day|daily|monthly|per month)\b"):
            if not h(r"\b(?:single|one)\s+(?:use|time)\s+card\b") or limits or h(r"\b(?:again|subscriptions?|recurring|multiple|atm|per day)\b"):
                return "disposable_card_limits"
        if issue and not h(r"\b(?:get|create|order|generate|obtain)\b"):
            return "virtual_card_not_working"
        return "get_disposable_virtual_card"

    if virtual and issue and not topup and not transfer:
        if not h(r"\b(?:get|create|order|generate|obtain)\b") or declined or h(r"\b(?:payment|pay|purchase|work|working|rejected)\b"):
            return "virtual_card_not_working"

    if card and h(r"\b(?:link|linking|linked|unlink|unlinking|associate|connect|attach|pair|register)\b") and not topup:
        if not (h(r"\bregister\b") and h(r"\b(?:account|country|resident)\b") and not h(r"\b(?:card|link)\b")):
            return "card_linking"

    if card and h(r"\b(?:activat\w*|not active|inactive|enable my card|start using|begin using)\b") and not topup:
        if not h(r"\b(?:already activated|already active|activated it|activated my card)\b") or not issue:
            return "activate_my_card"

    # Shipping queries distinguish a late/missing shipment from a delivery estimate.
    shipping = card and h(
        r"\b(?:delivery|deliver\w*|ship\w*|post\w*|mail\w*|track\w*|dispatch\w*)\b|"
        r"\b(?:arriv\w*|receiv\w*)\b|"
        r"\bwhere\b.{0,25}\bcard\b|\bcard\b.{0,25}\b(?:not here|not there)\b|"
        r"\bwaiting\b.{0,25}\bcard\b"
    )
    if shipping and not (withdrawal or topup or transfer) and not (payment and not h(r"\b(?:delivery|shipment|tracking|dispatch)\b")):
        late_card = missing or h(r"\b(?:late|overdue|delayed|delay|lost in|weeks ago|month ago|months ago|wrong address|wrong country|track|tracking|where is|where are)\b")
        if late_card:
            return "card_arrival"
        if timing or h(r"\b(?:express|expedited|faster|speed up|urgent|urgently|priority|next day)\b"):
            return "card_delivery_estimate"
        if h(r"\b(?:status|tracking|shipment|dispatch|still waiting|not received|never received)\b"):
            return "card_arrival"
        if not issue and not h(r"\b(?:just received|just arrived|have received|has arrived|received my card|card arrived)\b"):
            if h(r"\b(?:order|request|apply)\b") and h(r"\b(?:how|can i|want|would like)\b"):
                return "order_physical_card"
            return "card_delivery_estimate"

    if card and h(r"\b(?:spare|backup|back up|second|additional|extra|another|multiple|several|two|2)\b|\bmore than one\b"):
        if not (topup or transfer or withdrawal or payment or fees or unknown or virtual):
            if not h(r"\b(?:extra charge|another country|second hand)\b"):
                return "getting_spare_card"
        if h(r"\b(?:spare|backup|back up)\s+card\b"):
            return "getting_spare_card"

    if virtual and not topup and not transfer and not withdrawal:
        if h(r"\b(?:get|create|order|generate|obtain|request|want|need|provide|offer|apply|where|how|available|cost)\b") or not payment:
            return "getting_virtual_card"

    # Cash and cheque deposits are not card top ups or cash withdrawals.
    if cash_deposit and not withdrawal:
        if missing or pending or h(r"\b(?:deposited|paid in|cashed)\b.{0,45}\b(?:where|balance|waiting|nothing|not)\b"):
            return "balance_not_updated_after_cheque_or_cash_deposit"
        return "top_up_by_cash_or_cheque"

    # Cash-machine events.
    if withdrawal:
        if unknown:
            return "cash_withdrawal_not_recognised"
        if exchange:
            return "wrong_exchange_rate_for_cash_withdrawal"
        wrong_cash = h(
            r"\b(?:wrong|incorrect|different)\s+(?:amount|sum|cash)\b|"
            r"\b(?:less|more|fewer|short|shorter|partial|part of|only half|not enough)\b.{0,30}\b(?:cash|money|amount|notes|bills|requested|asked|withdrawn)\b|"
            r"\b(?:cash|money|amount)\b.{0,30}\b(?:less|short|wrong|incorrect|different|only half)\b|"
            r"\b(?:no|not any|none|zero)\s+(?:cash|money)\b|"
            r"\b(?:did not|does not|never|not)\b.{0,20}\bdispens\w*\b|"
            r"\b(?:dispensed|gave|received|got)\b.{0,25}\b(?:nothing|only|none)\b|"
            r"\b(?:no|not)\b.{0,15}\b(?:cash|money)\b.{0,15}\b(?:came|come|out)\b"
        )
        if wrong_cash:
            if not declined or h(r"\b(?:debited|deducted|charged|dispensed|balance|account)\b"):
                return "wrong_amount_of_cash_received"
        if pending:
            return "pending_cash_withdrawal"
        if fees:
            return "cash_withdrawal_charge"
        if declined or failed or h(r"\b(?:cannot|unable|refuses|refused)\b.{0,25}\b(?:cash|money|withdraw|withdrawal)\b"):
            return "declined_cash_withdrawal"
        if wrong_cash:
            return "wrong_amount_of_cash_received"
        return "atm_support"

    # Bank-transfer funding is distinguished from card funding.
    if bank_funding and not (topup and card and not bank_method):
        if fees:
            return "top_up_by_bank_transfer_charge"
        if declined:
            return "declined_transfer"
        if failed and not missing and not pending:
            return "failed_transfer"
        if pending and not missing and not h(r"\bbalance\b"):
            return "pending_transfer"
        if missing:
            if recipient or (outgoing and not h(r"\b(?:to|into)\s+my\s+revolut\b")):
                return "transfer_not_received_by_recipient"
            return "balance_not_updated_after_bank_transfer"
        if limits and top_explicit:
            return "top_up_limits"
        if timing:
            return "transfer_timing"
        return "transfer_into_account"

    # Card top ups, including card/currency eligibility.
    if topup:
        if reverted or h(r"\btop up\b.{0,30}\b(?:returned|cancelled|refunded)\b"):
            return "top_up_reverted"
        if declined or (failed and not pending and not missing):
            return "top_up_failed"
        if pending or missing or h(r"\bwaiting\b|\bnot\b.{0,20}\b(?:credited|added|gone through)\b"):
            return "pending_top_up"
        if limits:
            return "top_up_limits"
        if fees:
            if bank_method:
                return "top_up_by_bank_transfer_charge"
            return "top_up_by_card_charge"
        if h(r"\b(?:currenc\w*|dollars?|euros?|pounds?|usd|eur|gbp|aud|cad|chf|jpy|yen|rupees?|rubles?|roubles?|zloty)\b") or h(
            r"\b(?:which|what|supported|accepted|accept|allowed|eligible|types?|kinds?|prepaid|amex|american express|maestro|discover|diners|visa|mastercard|someone else|another person|other people|third party)\b.{0,35}\b(?:cards?|use|top up)\b|"
            r"\b(?:cards?)\b.{0,30}\b(?:supported|accepted|allowed|eligible|someone else)\b"
        ):
            if not h(r"\b(?:how|where)\b.{0,25}\b(?:add|top up|load|fund)\b") or h(r"\b(?:currenc\w*|prepaid|amex|american express|maestro|discover|visa|mastercard|someone else|which|types?|kinds?)\b"):
                return "supported_cards_and_currencies"
        return "topping_up_by_card"

    # Remaining bank transfers.
    if transfer:
        if fees:
            if incoming and not outgoing:
                return "top_up_by_bank_transfer_charge"
            return "transfer_fee_charged"
        if declined:
            return "declined_transfer"
        if reverted:
            return "failed_transfer"
        if recipient and (missing or h(r"\b(?:has not got|did not get|cannot see|has not come|not there|not landed)\b")):
            return "transfer_not_received_by_recipient"
        if pending:
            return "pending_transfer"
        if failed and not missing:
            return "failed_transfer"
        if missing:
            if outgoing or recipient or h(r"\bcompleted\b"):
                return "transfer_not_received_by_recipient"
            return "balance_not_updated_after_bank_transfer"
        if timing:
            return "transfer_timing"
        if h(r"\b(?:iban|bic|swift|sort code|routing number|account number|bank details)\b"):
            return "transfer_into_account"
        if h(r"\b(?:receive|receiving|salary|wages|payroll|employer|pension)\b") and not h(r"\bfrom\s+my\s+bank\b"):
            return "receiving_money"
        if incoming or h(r"\b(?:how|can)\b.{0,35}\btransfer\b.{0,30}\b(?:account|revolut)\b"):
            return "transfer_into_account"
        if outgoing or h(r"\btransfer\b"):
            return "pending_transfer"

    # Card-payment events.
    if unknown and (payment or card or h(r"\b(?:charge|debit|statement|money|account)\b")):
        return "card_payment_not_recognised"
    if h(r"\b(?:someone|somebody)\b.{0,25}\b(?:using|used|has access to)\b.{0,20}\bcard\b"):
        return "compromised_card"

    if exchange and (card or payment) and wrong:
        return "card_payment_wrong_exchange_rate"

    if (card or payment) and reverted:
        return "reverted_card_payment"
    if (card or payment) and pending:
        return "pending_card_payment"

    if declined and (card or payment or h(r"\b(?:shop|store|restaurant|online|pay)\b")):
        return "declined_card_payment"
    if payment and failed and not h(r"\b(?:card|chip)\b.{0,20}\b(?:damaged|broken|not working|stopped working)\b"):
        return "declined_card_payment"

    if fees and (card or payment) and not h(r"\b(?:order|delivery|replacement|spare|issue|issuance)\b"):
        if not exchange or h(r"\b(?:purchase|purchases|pay|paid|payment|shopping|merchant|shop)\b"):
            if h(r"\b(?:statement|account)\b") and extra and not h(r"\b(?:purchase|paid|paying|shop|merchant|using|abroad|foreign)\b"):
                return "extra_charge_on_statement"
            return "card_payment_fee_charged"

    if card and failed:
        return "card_not_working"

    # Issuance, card types, and acceptance.
    if h(r"\b(?:visa|mastercard)\b") and not (topup or withdrawal):
        if h(r"\b(?:visa)\b") and h(r"\bmastercard\b"):
            return "visa_or_mastercard"
        if h(r"\b(?:issue|issued|offer|provide|choose|choice|instead|switch|brand|type of card|which card|receive|send me)\b"):
            return "visa_or_mastercard"

    if card and h(r"\b(?:order|request|apply|buy|purchase)\b") and not h(r"\b(?:shop|merchant|online purchase|transaction)\b"):
        return "order_physical_card"
    if physical and not payment:
        if h(r"\b(?:get|obtain|receive|provide|offer|want|need|available|possible|real|rather than|instead of)\b"):
            return "get_physical_card"
    if card and h(r"\b(?:send me|send a|send my|new card|first card|request a card|apply for a card)\b"):
        return "order_physical_card"

    if card and h(r"\b(?:accepted|accept|use|usable|work|pay|spend|supported)\b") and h(
        r"\b(?:where|which|countries|country|abroad|overseas|international|online|shop|shops|store|stores|merchant|merchants|hotel|hotels|petrol|gas station|everywhere|anywhere|travel|holiday|vacation)\b"
    ):
        return "card_acceptance"

    # Exchange and supported currencies.
    currency_support = h(
        r"\b(?:currencies|currency)\b.{0,35}\b(?:support\w*|hold|available|account|balance|accept\w*|keep)\b|"
        r"\b(?:support\w*|hold|holding|keep|keeping|available|accept\w*)\b.{0,35}\b(?:currencies|currency|dollars?|euros?|pounds?|usd|eur|gbp)\b|"
        r"\b(?:multi currency|multicurrency|fiat|currency accounts|currency balances)\b|"
        r"\b(?:account|balance)\s+in\s+(?:usd|eur|gbp|dollars?|euros?|pounds?|yen|rupees?)\b"
    )
    if currency_support and not (exchange and (fees or wrong)):
        if card and h(r"\b(?:fund|funding|add|load|deposit|supported cards)\b"):
            return "supported_cards_and_currencies"
        return "fiat_currency_support"

    if exchange:
        if fees or h(r"\b(?:weekend|fair usage|allowance|spread)\b"):
            return "exchange_charge"
        if h(r"\brate\b|\brates\b|\binterbank\b|\bhow much\b.{0,25}\b(?:get|worth|equal)\b"):
            return "exchange_rate"
        return "exchange_via_app"

    if fees and h(r"\b(?:statement|account|charge|charged|payment)\b"):
        return "extra_charge_on_statement"

    if h(r"\b(?:countries|country|resident|residents|reside|residing|citizen|citizenship|nationality|live|living|based)\b") and h(
        r"\b(?:support|supported|available|availability|operate|operating|register|registration|sign up|signup|open|account|join|service|eligible|allowed|use revolut)\b"
    ):
        return "country_support"
    if not card and h(r"\b(?:available|operate|supported|sign up|register|open an account)\b.{0,40}\b(?:in|from|outside|across)\b"):
        return "country_support"

    if h(r"\b(?:salary|wages|payroll|employer|pension|paycheck|pay cheque)\b|\b(?:receive|receiving|accept)\s+(?:some\s+|my\s+|the\s+)?(?:money|funds|payments)\b|\brequest\s+(?:some\s+)?money\b|\b(?:someone|somebody|friend|person|people)\b.{0,35}\b(?:pay me|send me|send money|pay into)\b"):
        return "receiving_money"

    if card and h(r"\b(?:supported|accepted|accept|which|what type|what kind|prepaid|amex|american express|maestro|discover|diners)\b"):
        if h(r"\b(?:cards|prepaid|amex|american express|maestro|discover|diners)\b"):
            return "supported_cards_and_currencies"
        return "card_acceptance"

    if card and h(r"\b(?:how|can|want|need|obtain|get)\b") and not payment:
        if physical:
            return "get_physical_card"
        if h(r"\b(?:get|obtain|want|need)\b"):
            return "order_physical_card"

    return _nearest_intent(t)


def predict(state) -> dict:
    return {"answer": _classify(_extract_text(state))}