import re
import math
import unicodedata
from collections import Counter, defaultdict
from functools import lru_cache


_EXAMPLES = {
    "activate_my_card": (
        "How do I activate my new card?|I received my card and need to enable it|"
        "My replacement card needs activating|Where is the card activation button?|"
        "Can I activate a card before it arrives?|The app will not let me activate my card"
    ),
    "age_limit": (
        "How old must I be to open an account?|Can someone under eighteen join?|"
        "Is there a minimum age limit?|Can my teenage son have an account?|"
        "I am sixteen can I get a card?|Are children allowed to use this service?"
    ),
    "apple_pay_or_google_pay": (
        "Can I add my card to Apple Pay?|Does Google Pay work with your cards?|"
        "How do I set up Google Wallet?|My Apple wallet payment does not work|"
        "Can I use my phone to pay with Android Pay?|How do I add a card to my iPhone wallet?"
    ),
    "atm_support": (
        "Which ATMs can I use?|Where can I withdraw cash?|"
        "Find a nearby cash machine that accepts my card|What ATM networks are supported?|"
        "Can I use any bank cashpoint?|Can I withdraw money abroad?|"
        "Which cash machines accept the card?"
    ),
    "automatic_top_up": (
        "How do I enable automatic top ups?|Can I automatically add money when my balance is low?|"
        "How do I turn off auto top up?|My recurring top up is not working|"
        "Can I schedule regular card deposits?|Change my automatic top up amount"
    ),
    "balance_not_updated_after_bank_transfer": (
        "My bank transfer has not appeared in my balance|I sent money to Revolut but it has not arrived|"
        "An incoming bank transfer is missing|My salary has not reached my account|"
        "My balance has not changed after a bank transfer|I transferred money from my bank but cannot see it|"
        "Why has the money sent to my account not been credited?"
    ),
    "balance_not_updated_after_cheque_or_cash_deposit": (
        "My cash deposit is not showing in my account|I deposited a cheque and my balance has not changed|"
        "Where is the cash I paid in yesterday?|The check I deposited has not cleared|"
        "I added cash but the money is missing|My cash or cheque deposit has not been credited"
    ),
    "beneficiary_not_allowed": (
        "Why is this beneficiary not allowed?|The recipient is not permitted|"
        "I cannot add a beneficiary|The app says beneficiary is not allowed|"
        "Why can I not transfer to this payee?|My recipient account is unsupported|"
        "Can I transfer money to a cryptocurrency exchange?"
    ),
    "cancel_transfer": (
        "How can I cancel a bank transfer?|Can I reverse money I sent to the wrong account?|"
        "I want to stop a pending transfer|Recall my transfer|"
        "I entered the wrong bank details can I get the transfer back?|Cancel a scheduled bank payment"
    ),
    "card_about_to_expire": (
        "My card is about to expire|How do I renew an expired card?|"
        "When will you replace my expiring card?|My card expires next month|"
        "Will I receive a new card before the expiry date?|What happens when my card expires?"
    ),
    "card_acceptance": (
        "Where can I use my card?|Can I pay with my card abroad?|"
        "Which shops accept your card?|Is the card accepted online?|"
        "Can I use my card in another country?|Can I pay at petrol stations and hotels?|"
        "Will this card work on Amazon or PayPal?|Can I use the card worldwide?"
    ),
    "card_arrival": (
        "My card has not arrived yet|Where is the card I ordered?|"
        "How do I track my card delivery?|My card delivery is late|"
        "I ordered a card two weeks ago and still have not received it|"
        "The app says delivered but my card is missing|What is the status of my card delivery?"
    ),
    "card_delivery_estimate": (
        "How long does card delivery take?|When will my new card arrive?|"
        "What is the estimated delivery time for a card?|"
        "Can you deliver my card faster?|How long is express card delivery?|"
        "How many days does it take to receive a card?|When should I order a card before travelling?"
    ),
    "card_linking": (
        "How do I link my card to my account?|I cannot link my existing card|"
        "Can I add my card to another Revolut account?|How do I pair my card with the app?|"
        "I found a card how do I link it?|Link a replacement card to my account|"
        "My card is linked to a different account"
    ),
    "card_not_working": (
        "My card is not working|My card stopped working|"
        "My physical card does not work anymore|My card chip is damaged|"
        "The machine cannot read my card|My card does not work in shops or at ATMs|"
        "Why is my bank card unusable?"
    ),
    "card_payment_fee_charged": (
        "Why was I charged a fee for a card payment?|A merchant charged extra for paying by card|"
        "There is a surcharge on my card purchase|Why did I pay more than the purchase price?|"
        "Do card payments have a fee?|I was charged a transaction fee when buying something"
    ),
    "card_payment_not_recognised": (
        "I do not recognise a card payment|There is a purchase I did not make|"
        "Someone used my card for an unauthorized transaction|An unknown merchant charged me|"
        "I see a suspicious card transaction|What is this payment on my statement?|"
        "I was charged for something I never bought"
    ),
    "card_payment_wrong_exchange_rate": (
        "The exchange rate on my card payment is wrong|I paid abroad and the conversion rate was incorrect|"
        "Why was a bad exchange rate used for my purchase?|"
        "My foreign currency card purchase used the wrong rate|"
        "Which exchange rate was applied to my card transaction?"
    ),
    "card_swallowed": (
        "The ATM swallowed my card|A cash machine kept my card|"
        "The cashpoint did not return my card|My card is stuck inside an ATM|"
        "How do I recover a retained card?|The ATM ate my bank card"
    ),
    "cash_withdrawal_charge": (
        "Why was I charged for withdrawing cash?|What are the ATM withdrawal fees?|"
        "How much cash can I withdraw for free?|I was charged a cashpoint fee|"
        "What is the monthly free withdrawal allowance?|Do you charge for withdrawing money abroad?|"
        "What is the cash withdrawal limit?"
    ),
    "cash_withdrawal_not_recognised": (
        "I do not recognise a cash withdrawal|There is an ATM transaction I did not make|"
        "Someone withdrew cash using my card|An unknown cash withdrawal is on my statement|"
        "I never took money out but my account shows a withdrawal"
    ),
    "change_pin": (
        "How do I change my card PIN?|Where can I see my PIN number?|"
        "I forgot my card PIN|Can I reset my card PIN?|"
        "Where can I find my four digit card code?|I want a different PIN|"
        "Can I view my card PIN in the app?"
    ),
    "compromised_card": (
        "I think my card details have been stolen|Someone knows my card number and security code|"
        "My card has been compromised|I gave my card details to a scammer|"
        "I suspect my card was cloned|Someone has access to my card information|"
        "How do I freeze my card after a phishing scam?"
    ),
    "contactless_not_working": (
        "My contactless payment does not work|I cannot pay by tapping my card|"
        "Why is contactless disabled?|The tap and go feature stopped working|"
        "My card works with chip and PIN but not contactless|"
        "How do I enable contactless payments?"
    ),
    "country_support": (
        "Which countries do you support?|Can I open an account if I live in the United States?|"
        "Is your service available in my country?|Can residents of India sign up?|"
        "Which nationalities are eligible for an account?|I live outside Europe can I join?|"
        "Do you operate in Canada?"
    ),
    "declined_card_payment": (
        "My card payment was declined|Why was my purchase rejected?|"
        "A shop refused my card transaction|My online payment failed|"
        "The payment terminal says declined|Why was my card payment unsuccessful?|"
        "I have enough money but my payment was refused"
    ),
    "declined_cash_withdrawal": (
        "My ATM withdrawal was declined|The cash machine refused to let me withdraw|"
        "Why can I not take cash out?|The ATM says transaction declined|"
        "My cash withdrawal failed despite sufficient funds|"
        "I cannot withdraw money at the cashpoint"
    ),
    "declined_transfer": (
        "Why was my bank transfer declined?|My transfer was rejected|"
        "The recipient bank refused my transfer|My money transfer has been denied|"
        "Why will you not allow my transfer?|A transfer payment was declined"
    ),
    "direct_debit_payment_not_recognised": (
        "I do not recognise a direct debit|An unauthorized direct debit was taken|"
        "What is this direct debit payment?|I did not set up this direct debit|"
        "There is an unknown direct debit on my account|An unexpected standing order took my money"
    ),
    "disposable_card_limits": (
        "What are the limits for disposable cards?|Can I use a disposable card more than once?|"
        "How many disposable virtual cards can I create?|Can I make recurring payments with a disposable card?|"
        "Is there a spending limit on a single use card?|"
        "Can I use a disposable card for subscriptions?|Why did my disposable card number change?"
    ),
    "edit_personal_details": (
        "How do I change my phone number?|I need to update my address|"
        "Can I change my personal details?|How do I edit my name?|"
        "I moved to a new address|My email address has changed|"
        "Correct my date of birth|Update the surname on my account"
    ),
    "exchange_charge": (
        "Is there a fee for exchanging currencies?|Why was I charged a currency conversion fee?|"
        "What are your foreign exchange charges?|Is currency exchange free on weekends?|"
        "What is the exchange allowance?|I was charged commission when converting money|"
        "Do I pay a markup when exchanging currency?"
    ),
    "exchange_rate": (
        "What exchange rate do you use?|Where can I see the current exchange rate?|"
        "How are your currency exchange rates calculated?|"
        "Is the rate the same as the interbank rate?|Why is the exchange rate different?|"
        "What is the euro dollar exchange rate today?"
    ),
    "exchange_via_app": (
        "How do I exchange money in the app?|How can I convert my pounds to euros?|"
        "Where is the currency exchange function?|Can I buy dollars with my balance?|"
        "How do I sell a currency?|How do I switch money between currency accounts?|"
        "I want to exchange currencies using the application"
    ),
    "extra_charge_on_statement": (
        "Why is there an extra one pound charge on my statement?|"
        "Why did you take an extra euro from my card?|What is this small additional card charge?|"
        "There is an extra dollar on my statement|Why did I get charged one pound when I added a card?|"
        "Is the small card authorization charge refundable?"
    ),
    "failed_transfer": (
        "My bank transfer failed|Why did my transfer not go through?|"
        "I get an error when sending a bank transfer|I am unable to make a transfer|"
        "My bank transfer was returned to me|A transfer bounced back into my account|"
        "I cannot send money to another bank"
    ),
    "fiat_currency_support": (
        "Which currencies can I hold in my account?|What fiat currencies are supported?|"
        "Can I have a US dollar balance?|Can I open an account in euros?|"
        "How many currency accounts can I have?|Is the Swiss franc supported?|"
        "What currencies are available to exchange?|Can I keep money in different currencies?"
    ),
    "get_disposable_virtual_card": (
        "How do I get a disposable virtual card?|Can I create a single use card?|"
        "Where do I find a disposable card?|What is a disposable virtual card?|"
        "I would like a temporary one time use card|How do disposable cards work?"
    ),
    "get_physical_card": (
        "How do I get a physical card?|I need an actual plastic card|"
        "Can I get a physical card as well as my virtual card?|"
        "How can I obtain a real bank card?|Is a physical card available?|"
        "I only have a virtual card and want a physical one"
    ),
    "getting_spare_card": (
        "Can I get a spare card?|I need a second card for my account|"
        "Can I have two physical cards?|How do I get an additional card?|"
        "I want a backup card|Can I get another card for my partner?|"
        "How many cards can I have?"
    ),
    "getting_virtual_card": (
        "How do I get a virtual card?|Where can I create a virtual card?|"
        "I want an online card without a physical one|What is a virtual card?|"
        "How do I order a virtual debit card?|Can I have a digital card?|"
        "Where are my virtual card details?"
    ),
    "lost_or_stolen_card": (
        "I lost my card|My card has been stolen|My wallet was stolen with my card inside|"
        "I cannot find my card|What should I do if my card goes missing?|"
        "How do I replace a lost card?|Please block my stolen card"
    ),
    "lost_or_stolen_phone": (
        "My phone was stolen|I lost my phone and cannot access the app|"
        "What do I do if I lose my mobile?|Someone stole my phone|"
        "I no longer have my phone|How do I secure my account after losing my phone?"
    ),
    "order_physical_card": (
        "How do I order a card?|I want to order a new physical card|"
        "Where can I order my first bank card?|How much does ordering a card cost?|"
        "I cannot order a debit card in the app|Please send me a bank card|"
        "How can I request a new card?"
    ),
    "passcode_forgotten": (
        "I forgot my passcode|I cannot remember my app password|"
        "How do I reset my login code?|I am locked out of the app|"
        "I cannot log in to my account|My password does not work|"
        "I have forgotten my security code for signing in"
    ),
    "pending_card_payment": (
        "Why is my card payment pending?|My purchase is still processing|"
        "How long will a pending card transaction take?|"
        "The merchant payment has not completed|There is a pending payment on my account|"
        "Why is money reserved for my card payment?|When will the card authorization be released?"
    ),
    "pending_cash_withdrawal": (
        "Why is my cash withdrawal pending?|My ATM transaction is still processing|"
        "How long will a pending withdrawal take?|The cash withdrawal has not completed|"
        "A cashpoint withdrawal is stuck in pending status"
    ),
    "pending_top_up": (
        "My top up is pending|Why is my card top up still processing?|"
        "The money I added by card is not showing|How long does a card top up take?|"
        "My bank card was charged but my balance has not updated|"
        "My card deposit is stuck pending"
    ),
    "pending_transfer": (
        "My bank transfer is pending|Why is my transfer still processing?|"
        "A money transfer is stuck in progress|How long does a pending transfer take?|"
        "My bank payment is waiting to be processed"
    ),
    "pin_blocked": (
        "My PIN is blocked|I entered the wrong PIN three times|"
        "How do I unblock my card PIN?|I exceeded the number of PIN attempts|"
        "The ATM says PIN tries exceeded|My card was locked after incorrect PIN entries"
    ),
    "receiving_money": (
        "How can someone send me money?|How do I receive money from a friend?|"
        "Can I receive a transfer in another currency?|Which currencies can I receive money in?|"
        "How do I request a payment from another user?|Can someone pay me using a link?|"
        "How can a friend without an account send money to me?"
    ),
    "refund_not_showing_up": (
        "My refund has not arrived|A merchant refunded me but my balance has not changed|"
        "Where is my refund?|How long does a refund take to appear?|"
        "I am still waiting for a refund from a shop|The refund is missing from my account|"
        "My refund is pending"
    ),
    "request_refund": (
        "How do I request a refund?|I want to dispute a card purchase|"
        "How do I get a chargeback?|Can you refund this payment?|"
        "I paid for goods that never arrived|The merchant will not give me my money back|"
        "I cancelled my order and want a refund"
    ),
    "reverted_card_payment": (
        "Why was my card payment reverted?|A card payment was reversed|"
        "The money for my purchase came back to my account|"
        "A completed card payment now says reverted|My card purchase was cancelled and returned|"
        "Why did my merchant payment get reversed?"
    ),
    "supported_cards_and_currencies": (
        "Which cards can I use to top up?|Can I add money with an American Express card?|"
        "What currencies can I top up in?|Do you accept prepaid cards for deposits?|"
        "Can I use a credit card issued abroad to top up?|Which bank cards are supported?|"
        "Can I top up with a debit card in another currency?"
    ),
    "terminate_account": (
        "How do I close my account?|I want to delete my account permanently|"
        "Please terminate my account|I no longer want to use your service|"
        "Can I deactivate my account?|I want to cancel my membership"
    ),
    "top_up_by_bank_transfer_charge": (
        "Is there a fee for topping up by bank transfer?|"
        "Will I be charged for transferring money into my account?|"
        "Why was I charged for an incoming bank transfer?|"
        "What does it cost to add money from my bank account?|"
        "Are bank transfer deposits free?"
    ),
    "top_up_by_card_charge": (
        "Is there a fee for topping up by card?|Why was I charged to add money by debit card?|"
        "What are the credit card top up charges?|"
        "I paid a fee when loading my account with a card|"
        "Are card top ups free?|My bank charged me for a card top up"
    ),
    "top_up_by_cash_or_cheque": (
        "Can I top up with cash?|Can I deposit a cheque into my account?|"
        "How do I pay cash into my balance?|Do you accept checks?|"
        "Can I add money at a bank branch?|Can I send you cash to deposit?"
    ),
    "top_up_failed": (
        "My top up failed|I cannot add money with my card|"
        "My card deposit was declined|Why was my top up unsuccessful?|"
        "I get an error when topping up|My debit card will not let me add funds|"
        "I am unable to load money into my account"
    ),
    "top_up_limits": (
        "What is my top up limit?|How much money can I add to my account?|"
        "What is the maximum card deposit?|Is there a minimum top up amount?|"
        "How do I increase my top up limit?|How many times per day can I top up?|"
        "Is there a daily limit on adding funds?"
    ),
    "top_up_reverted": (
        "My top up was reverted|Why was the money I added returned to my card?|"
        "My card top up has been reversed|The deposit bounced back to my bank card|"
        "The money I topped up disappeared and went back to my bank|"
        "Why did you refund my top up?"
    ),
    "topping_up_by_card": (
        "How do I top up by card?|How do I add money to my account?|"
        "Can I use someone else's bank card to add funds?|How do I change my top up card?|"
        "How do I remove a saved debit card?|Can I top up using a credit card?|"
        "I want to load money with my bank card"
    ),
    "transaction_charged_twice": (
        "I was charged twice for the same transaction|My card payment is duplicated|"
        "I paid once but two payments appear|A merchant took the money twice|"
        "Why was my account debited two times?|I have duplicate charges for one purchase"
    ),
    "transfer_fee_charged": (
        "Why was I charged a transfer fee?|What does it cost to send a bank transfer?|"
        "The recipient received less money than I sent|Are international transfers free?|"
        "Why did an intermediary bank deduct a fee?|How much do you charge to transfer money?"
    ),
    "transfer_into_account": (
        "How do I transfer money into my account?|Where can I find my IBAN and bank details?|"
        "Can I have my salary paid into my account?|"
        "How do I make a bank transfer from my other bank to Revolut?|"
        "What bank details should I use to deposit money?|"
        "How can I fund my account by bank transfer?"
    ),
    "transfer_not_received_by_recipient": (
        "The recipient has not received my transfer|I sent money but it never arrived at the destination|"
        "My friend has not got the money I sent|A completed transfer did not reach the beneficiary|"
        "Where is the transfer I made to my bank account?|"
        "I sent money yesterday and the recipient still cannot see it"
    ),
    "transfer_timing": (
        "How long does a bank transfer take?|When will my international transfer arrive?|"
        "Are transfers instant?|Do transfers go through on weekends?|"
        "How many days does it take to send money overseas?|"
        "When will the beneficiary receive the transfer?"
    ),
    "unable_to_verify_identity": (
        "I cannot verify my identity|My identity verification failed|"
        "The app will not accept my passport|My selfie keeps getting rejected|"
        "My documents have been refused|Identity verification is stuck pending|"
        "I am having trouble uploading my ID|My identity has not been approved"
    ),
    "verify_my_identity": (
        "How do I verify my identity?|What documents do I need for identity verification?|"
        "How do I upload my passport?|Where do I send my ID?|"
        "How do I take a verification selfie?|Can I use my driving licence to verify my account?|"
        "Do I need proof of address?"
    ),
    "verify_source_of_funds": (
        "How do I verify my source of funds?|Why do you need proof of my income?|"
        "What documents prove where my money came from?|"
        "How do I upload a bank statement to prove my income?|"
        "Why are you asking about the origin of my funds?|I need to verify my wealth"
    ),
    "verify_top_up": (
        "How do I verify my top up card?|Where is the card verification code?|"
        "I cannot find the code on my bank statement|How do I confirm ownership of my debit card?|"
        "Why do I need to verify a card used for top ups?|"
        "How do I verify a deposit?|What amount do I enter to verify my card?"
    ),
    "virtual_card_not_working": (
        "My virtual card does not work|A payment with my virtual card failed|"
        "My virtual card was declined online|I cannot pay with my digital card|"
        "The virtual card details are not accepted|Why has my virtual card stopped working?"
    ),
    "visa_or_mastercard": (
        "Will I get a Visa or Mastercard?|Can I choose between Visa and MasterCard?|"
        "Which card brand do you issue?|Can I change my Visa card to a Mastercard?|"
        "Do you offer both Visa and Mastercard?|I want a Visa instead of a Mastercard"
    ),
    "why_verify_identity": (
        "Why do I need to verify my identity?|Why do you need my passport?|"
        "Why are you asking for a selfie?|Do I have to provide identification?|"
        "Can I use my account without verifying my identity?|"
        "Why is identity verification required?"
    ),
    "wrong_amount_of_cash_received": (
        "The ATM gave me the wrong amount of cash|I was charged but no cash came out|"
        "The cash machine dispensed less money than I requested|"
        "I withdrew money but the ATM gave me nothing|"
        "My account was debited but I did not receive any cash|"
        "The cashpoint gave me too much money"
    ),
    "wrong_exchange_rate_for_cash_withdrawal": (
        "The exchange rate for my ATM withdrawal is wrong|"
        "I withdrew cash abroad and got a bad conversion rate|"
        "Why was the wrong exchange rate used for my cash withdrawal?|"
        "What exchange rate was applied when I took money out?|"
        "The ATM converted my withdrawal at an incorrect rate"
    ),
}


def _normalize(value):
    s = unicodedata.normalize("NFKD", str(value)).lower()
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("’", "'").replace("`", "'")
    s = s.replace("£", " gbp ").replace("€", " eur ").replace("$", " usd ")
    s = s.replace("&", " and ")
    replacements = {
        "can't": "cannot", "cant": "cannot", "won't": "will not",
        "don't": "do not", "dont": "do not", "doesn't": "does not",
        "doesnt": "does not", "didn't": "did not", "didnt": "did not",
        "isn't": "is not", "isnt": "is not", "aren't": "are not",
        "wasn't": "was not", "wasnt": "was not", "weren't": "were not",
        "haven't": "have not", "havent": "have not", "hasn't": "has not",
        "hasnt": "has not", "couldn't": "could not", "wouldn't": "would not",
        "i'm": "i am", "i've": "i have", "i'd": "i would",
        "it's": "it is", "what's": "what is", "where's": "where is",
        "there's": "there is", "i'll": "i will", "you're": "you are",
        "you've": "you have", "they've": "they have",
    }
    for old, new in replacements.items():
        s = re.sub(r"\b" + re.escape(old) + r"\b", new, s)
    s = re.sub(r"\btop[\s_-]*ups?\b", "top up", s)
    s = re.sub(r"\btopping[\s_-]*up\b", "top up", s)
    s = re.sub(r"\bmaster\s+card\b", "mastercard", s)
    s = re.sub(r"\bapplepay\b", "apple pay", s)
    s = re.sub(r"\bgooglepay\b", "google pay", s)
    s = re.sub(r"\b(?:cashpoint|cashpoints)\b", "cash machine", s)
    s = re.sub(r"\batms\b", "atm", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _extract_text(state):
    if isinstance(state, str):
        return state
    if isinstance(state, dict):
        for key in (
            "text", "utterance", "query", "customer_text", "customer_message",
            "user_message", "user_input", "message", "input", "sentence",
            "content", "request", "description", "prompt",
        ):
            if key in state and state[key] is not None:
                result = _extract_text(state[key])
                if result:
                    return result
        for key in ("messages", "conversation", "history"):
            if key in state and isinstance(state[key], (list, tuple)):
                messages = state[key]
                for message in reversed(messages):
                    if isinstance(message, dict) and message.get("role") in ("user", "customer", "human"):
                        result = _extract_text(message)
                        if result:
                            return result
                result = _extract_text(messages)
                if result:
                    return result
        for key in ("state", "data", "question", "value"):
            if key in state:
                result = _extract_text(state[key])
                if result:
                    return result
        values = []
        for key, value in state.items():
            if key not in ("role", "id", "type", "label", "answer", "category"):
                if isinstance(value, (str, dict, list, tuple)):
                    result = _extract_text(value)
                    if result:
                        values.append(result)
        return " ".join(values)
    if isinstance(state, (list, tuple)):
        for item in reversed(state):
            result = _extract_text(item)
            if result:
                return result
    return ""


_STOP = set(
    "a an the i me my mine we our us you your yours it its he his she her they their "
    "this that these those of for to from in on at with by and or is are am was were "
    "be been being have has had do does did would could should please can will "
    "there here just really very some any as if so about into out".split()
)

_SYNONYMS = {
    "recognised": "recognize", "recognized": "recognize",
    "recognise": "recognize", "recognising": "recognize",
    "unauthorised": "unauthorized",
    "cheque": "check", "cheques": "check", "checks": "check",
    "euros": "eur", "euro": "eur", "pounds": "gbp", "pound": "gbp",
    "dollars": "usd", "dollar": "usd",
    "currencies": "currency",
    "payments": "payment", "purchases": "purchase",
    "transactions": "transaction", "transfers": "transfer",
    "withdrawals": "withdrawal", "withdraw": "withdrawal",
    "withdrawing": "withdrawal", "withdrew": "withdrawal", "withdrawn": "withdrawal",
    "received": "receive", "receiving": "receive", "receives": "receive",
    "arrived": "arrive", "arrives": "arrive", "arrival": "arrive",
    "delivered": "delivery", "deliver": "delivery",
    "charged": "charge", "charges": "charge", "charging": "charge",
    "fees": "fee", "costs": "cost", "costing": "cost",
    "blocked": "block", "blocking": "block",
    "declined": "decline", "declining": "decline",
    "rejected": "reject", "refused": "reject", "denied": "reject",
    "failed": "fail", "failing": "fail", "failure": "fail",
    "reversed": "revert", "reverted": "revert", "reversal": "revert",
    "changing": "change", "changed": "change",
    "updated": "update", "updating": "update", "upgraded": "update",
    "forgot": "forget", "forgotten": "forget",
    "stolen": "steal", "stole": "steal",
    "lost": "lose", "losing": "lose",
    "details": "detail", "documents": "document",
    "verification": "verify", "verified": "verify", "verifying": "verify",
    "activating": "activate", "activated": "activate", "activation": "activate",
    "working": "work", "works": "work", "worked": "work",
    "supported": "support", "supports": "support",
    "accepted": "accept", "accepts": "accept",
    "limits": "limit", "limited": "limit",
    "ordering": "order", "ordered": "order",
    "cards": "card", "accounts": "account", "banks": "bank",
    "details": "detail", "funds": "money", "fund": "money",
    "balance": "balance", "depositing": "deposit", "deposited": "deposit",
    "deposits": "deposit", "adding": "add", "added": "add",
    "enabled": "enable", "enabling": "enable", "disable": "disable",
    "sending": "send", "sent": "send",
    "exchanging": "exchange", "exchanged": "exchange",
    "conversion": "convert", "converted": "convert", "converting": "convert",
    "expired": "expire", "expiring": "expire", "expires": "expire",
    "renewal": "renew", "renewing": "renew",
    "children": "child", "kids": "child", "kid": "child",
    "mobile": "phone", "telephone": "phone", "cellphone": "phone",
    "application": "app", "passcodes": "passcode",
    "passwords": "password", "identification": "identity",
    "id": "identity", "selfies": "selfie",
    "refunds": "refund", "refunded": "refund", "refunding": "refund",
    "canceled": "cancel", "cancelled": "cancel", "cancelling": "cancel",
    "cancellation": "cancel", "canceling": "cancel",
    "closing": "close", "closed": "close",
    "extra": "extra", "additional": "extra",
    "duplicate": "duplicate", "duplicated": "duplicate",
    "spare": "spare", "backup": "spare",
    "temporary": "disposable", "digital": "virtual",
    "international": "abroad", "overseas": "abroad",
    "foreign": "abroad", "countries": "country",
    "allowed": "allow", "permitted": "allow",
    "beneficiaries": "beneficiary", "payee": "beneficiary",
    "incorrect": "wrong", "inaccurate": "wrong",
    "twice": "twice", "double": "twice", "doubled": "twice",
    "minimum": "minimum", "maximum": "maximum",
}


def _features(text):
    words = []
    for word in _normalize(text).split():
        if word not in _STOP:
            words.append(_SYNONYMS.get(word, word))
    result = Counter()
    for word in words:
        result[word] = 1.0
    for left, right in zip(words, words[1:]):
        result[left + "~" + right] = 0.75
    return result


@lru_cache(maxsize=1)
def _language_index():
    docs = []
    frequency = Counter()
    for label, phrases in _EXAMPLES.items():
        for phrase in phrases.split("|"):
            features = _features(phrase)
            docs.append((label, features))
            frequency.update(features.keys())
    count = len(docs)
    idf = {word: 1.0 + math.log((count + 1.0) / (freq + 1.0))
           for word, freq in frequency.items()}
    vectors = []
    for label, features in docs:
        vector = {word: value * idf[word] for word, value in features.items()}
        norm = math.sqrt(sum(v * v for v in vector.values())) or 1.0
        vectors.append((label, vector, norm))
    return idf, vectors


def _similarity_scores(text):
    idf, vectors = _language_index()
    query = {word: value * idf[word] for word, value in _features(text).items()
             if word in idf}
    norm = math.sqrt(sum(v * v for v in query.values())) or 1.0
    best = defaultdict(list)
    for label, vector, vnorm in vectors:
        dot = sum(value * query.get(word, 0.0) for word, value in vector.items())
        similarity = dot / (norm * vnorm)
        best[label].append(similarity)
    scores = {}
    for label in _EXAMPLES:
        values = sorted(best[label], reverse=True)
        scores[label] = 7.0 * values[0] + 0.8 * sum(values[:3]) / 3.0
    return scores


def predict(state) -> dict:
    text = _extract_text(state)
    t = _normalize(text)

    for label in _EXAMPLES:
        if t == label.replace("_", " "):
            return {"answer": label}

    scores = _similarity_scores(t)
    evidence = defaultdict(float)

    def has(pattern):
        return re.search(pattern, t) is not None

    def put(label, strength, condition=True):
        if condition and strength > evidence[label]:
            evidence[label] = strength

    card = has(r"\bcard\b|\bcards\b")
    atm = has(r"\batm\b|\bcash machine\b|\bcashpoint\b")
    withdrawal = atm or has(
        r"\bwithdraw\w*\b|\bwithdrew\b|\btak(?:e|ing|en) (?:some |any |my |the )?(?:cash|money) out\b|"
        r"\b(?:cash|money) (?:out|withdrawal)\b|\bdraw(?:ing)? (?:out )?cash\b"
    )
    transfer = has(
        r"\btransfers?\b|\bwire\b|\bswift\b|\bsepa\b|\bremittance\b|"
        r"\bsen[dt](?:ing)? (?:some |the |my |a |any )?(?:money|funds|payment)\b|"
        r"\bbank payments?\b"
    )
    topup = has(
        r"\btop up\b|\btopups?\b|\bcharg(?:e|ing) up\b|\bload(?:ed|ing)?\b|"
        r"\badd(?:ed|ing)? (?:some |any |more |my |the |a |additional )?(?:money|funds|cash)\b|"
        r"\bfund(?:ing|ed)? (?:my |the |an? |your )?account\b|"
        r"\b(?:card|debit|credit) deposit\b"
    )
    cash_deposit = has(r"\b(?:cash|cheque|check)\b") and (
        has(r"\bdeposit\w*|pay(?:ing|ed)? in\b|\bpaid in\b|\btop up\b|\badd\w*\b|\bcredit\w*\b|\bclear\w*\b")
        or has(r"\b(?:cash|cheque|check) (?:to|into) (?:my |the )?account\b")
    )
    cheque = has(r"\bcheques?\b|\bchecks?\b")
    if cheque and not has(r"\bcheck (?:my|the|your|if|whether|on)\b"):
        cash_deposit = True

    virtual = has(r"\bvirtual\b|\bdigital card\b|\bonline only card\b")
    disposable = has(r"\bdisposable\b|\bsingle use\b|\bone (?:time|use)\b|\bthrowaway\b|\btemporary (?:virtual )?card\b")
    physical = has(r"\bphysical\b|\bplastic\b|\breal (?:bank )?card\b|\bactual (?:bank )?card\b")

    payment = has(
        r"\bpayments?\b|\bpurchases?\b|\bpaid\b|\bpay(?:ing)?\b|\bmerchant\b|"
        r"\bshop\b|\bstore\b|\btransaction\b|\bpos\b|\bcheckout\b|\bbought\b|\bbuy\w*\b"
    )
    direct_debit = has(r"\bdirect debit\b|\bstanding order\b")
    bank_transfer = transfer or has(r"\bbank (?:deposit|account details)\b")
    bank_card = has(r"\b(?:debit|credit|prepaid|bank|external) card\b")
    card_funding = (topup or has(r"\bdeposit\b")) and not cash_deposit

    pending = has(
        r"\bpending\b|\bprocessing\b|\bin progress\b|\bawaiting\b|\buncompleted\b|"
        r"\bnot (?:yet )?(?:complete|completed|processed|settled)\b|"
        r"\bstill (?:being processed|reserved|unprocessed)\b"
    )
    declined = has(r"\bdeclin\w*\b|\breject\w*\b|\brefus\w*\b|\bdenied\b|\bnot authori[sz]ed\b")
    failed = has(
        r"\bfail\w*\b|\bunsuccessful\b|\berrors?\b|\bnot (?:going|go|gone) through\b|"
        r"\bnot work\w*\b|\bstopped work\w*\b|\bdoes not work\b|\bwent wrong\b"
    )
    cannot = has(
        r"\bcannot\b|\bcan not\b|\bunable\b|\bwill not (?:let|allow|work)\b|\bnot able\b|"
        r"\btrouble\b|\bdifficulty\b|\bproblems?\b|\bdoes not let\b"
    )
    missing = has(
        r"\bnot (?:yet )?(?:arriv\w*|receiv\w*|show\w*|appear\w*|reach\w*|credit\w*|reflect\w*)\b|"
        r"\bnever (?:arriv\w*|receiv\w*|got|show\w*|reach\w*)\b|"
        r"\bmissing\b|\bdisappear\w*\b|\bwhere (?:is|are|has)\b|\bnot in\b|"
        r"\bstill (?:waiting|not)\b|\bhas not (?:been )?(?:updated|changed)\b|"
        r"\b(?:balance|account) (?:is |has |was )?(?:not |un)(?:updated|changed)\b|"
        r"\bno (?:money|funds|payment|transfer|deposit|cash|refund)\b"
    )
    waiting = missing or has(
        r"\bwaiting\b|\bdelayed\b|\boverdue\b|\btaking (?:so |too )?long\b|\blate\b|"
        r"\bnot got\b|\bdid not get\b|\bhave not got\b|\bstill (?:nothing|no)\b"
    )
    timing = has(
        r"\bhow (?:long|soon|fast|quick\w*)\b|\bwhen (?:will|can|should|would|do|does|is|am)\b|"
        r"\b(?:delivery|arrival|processing|transfer) (?:time|estimate)\b|"
        r"\bhow many (?:working |business )?(?:days|hours|weeks)\b|\binstant\b|\bimmediate\w*\b|"
        r"\bweekends?\b|\bbusiness days\b|\btime (?:frame|scale)\b|\btimeframe\b|\bspeed\b"
    )
    fee = has(
        r"\bfees?\b|\bcharg(?:e|ed|es|ing)\b|\bcost\w*\b|\bcommission\b|\bsurcharg\w*\b|"
        r"\bmarkup\b|\bmark up\b|\bfree\b|\bextra\b|\bexpensive\b|\bpricing\b"
    )
    fee_question = has(
        r"\bfees?\b|\bcommission\b|\bsurcharg\w*\b|\bmarkup\b|\bmark up\b|\bcost\w*\b|"
        r"\bfree\b|\bextra\b|\bexpensive\b|\bcharg\w*.{0,25}\b(?:for|fee|more|extra)\b|"
        r"\bwhy.{0,25}\bcharg\w*\b|\bhow much.{0,25}\bcharg\w*\b"
    )
    reversed_ = has(
        r"\brevert\w*\b|\brevers\w*\b|\bbounc\w* back\b|\breturn\w* (?:back )?to\b|"
        r"\b(?:money|funds|payment|deposit|transfer|top up).{0,25}\b(?:came|come|went|sent|paid) back\b|"
        r"\b(?:refunded|returned) (?:my |the )?top up\b|\btop up.{0,25}\brefund\w*\b"
    )
    unknown = has(
        r"\bunrecogni[sz]\w*\b|\bnot recogni[sz]\w*\b|\bdo not know\b|\bunknown\b|"
        r"\bunfamiliar\b|\bunauthori[sz]\w*\b|\bnot authori[sz]\w*\b|\bsuspicious\b|"
        r"\bnot (?:me|mine)\b|\b(?:never|not) (?:made|make|paid|buy|bought|withdrawn|withdrew|took|used|set up)\b|"
        r"\bwithout (?:my )?(?:permission|knowledge|consent)\b|\bdid not do\b|"
        r"\bsomeone (?:else )?(?:used|made|withdrew|has used|has withdrawn)\b"
    )
    exchange = has(
        r"\bexchang\w*\b|\bconver[st]\w*\b|\bforex\b|\bfx\b|\binterbank\b|"
        r"\bchang(?:e|ing) .{0,20}\b(?:eur|usd|gbp|currency|currencies)\b"
    )
    rate = has(r"\brates?\b|\binterbank\b")
    refund = has(r"\brefund\w*\b|\bchargeback\b|\bcharge back\b")
    incoming_explicit = has(
        r"\bincoming\b|\binbound\b|\bsalary\b|\bwages\b|\bemployer\b|\bpaycheck\b|"
        r"\bpayroll\b|\bpaid into\b|\bto (?:my |the |your )?revolut\b|"
        r"\b(?:from|using) (?:my |the |another |a |an )?(?:other |external |regular |local )?bank(?: account)?\b|"
        r"\b(?:into|to) (?:my |the |your )?(?:revolut )?(?:balance|account)\b"
    )
    outgoing_explicit = has(
        r"\brecipient\b|\bbeneficiary\b|\bpayee\b|\boutgoing\b|\boutbound\b|"
        r"\bto (?:a |my |the |another |an? )?(?:friend|someone|person|other bank|external|different|relative|brother|sister|mother|father|partner)\b|"
        r"\bfrom (?:my |the )?revolut\b|\bto my (?:other |external |personal )?bank(?: account)?\b|"
        r"\bto another (?:bank |person|account|user)\b"
    )
    incoming = incoming_explicit and not outgoing_explicit
    bank_funding = bank_transfer and (incoming or topup)

    # Account eligibility, access, and personal information.
    put("age_limit", 55, has(
        r"\bage (?:limit|restriction|requirement)\b|\bminimum age\b|\bhow old\b|"
        r"\bunder (?:18|eighteen|16|sixteen|age)\b|\b(?:teenager|teenage|minor|children|child|kids?)\b|"
        r"\b(?:[1-9]|1[0-7]) (?:year|years|yr|yrs) old\b|\btoo young\b"
    ))
    put("terminate_account", 52, has(
        r"\b(?:close|closing|delete|deleting|terminate|deactivate|cancel|shut)\b.{0,35}\b(?:account|profile|membership)\b|"
        r"\b(?:account|profile).{0,20}\b(?:closed|deleted|terminated|closure)\b|"
        r"\bno longer (?:want|need).{0,25}\b(?:account|service)\b|"
        r"\bleave revolut\b|\bstop using (?:revolut|your service)\b"
    ))
    personal_detail = has(
        r"\b(?:phone|mobile|telephone) number\b|\baddress\b|\be ?mail\b|\bsurname\b|\blast name\b|"
        r"\bfirst name\b|\bfull name\b|\bmy name\b|\bpersonal (?:details|information|data)\b|"
        r"\bdate of birth\b|\bbirthday\b|\bdob\b|\bcountry of residence\b"
    )
    edit = has(r"\bchang\w*\b|\bupdat\w*\b|\bedit\w*\b|\bcorrect\w*\b|\bmodif\w*\b|\bnew\b|\bmoved\b|\bmarried\b|\bwrong\b")
    put("edit_personal_details", 49, personal_detail and edit and not has(r"\b(?:ip|bank|beneficiary|recipient) address\b"))
    put("edit_personal_details", 23, has(r"\bpersonal details\b|\bprofile details\b"))

    lost = has(r"\blost\b|\bstolen\b|\bstole\b|\blose\b|\blosing\b|\bmisplac\w*\b|\bcannot find\b|\bgone missing\b|\bno longer have\b")
    phone = has(r"\bphone\b|\bmobile\b|\bhandset\b|\bcellphone\b|\biphone\b|\bandroid\b")
    phone_lost = (
        has(r"\b(?:lost|stolen|lose|losing|misplaced).{0,20}\b(?:phone|mobile|handset|iphone)\b|"
            r"\b(?:phone|mobile|handset|iphone).{0,25}\b(?:lost|stolen|missing|stole)\b|"
            r"\b(?:no longer have|cannot find).{0,20}\b(?:phone|mobile)\b")
    )
    put("lost_or_stolen_phone", 61, phone_lost)
    put("lost_or_stolen_card", 54, (
        card and lost and not has(r"\b(?:card details|card information|card number)\b")
        and not (phone_lost and not has(r"\bcard.{0,20}\b(?:lost|stolen)\b|\b(?:lost|stolen).{0,12}\bcard\b"))
    ) or has(r"\b(?:wallet|purse).{0,25}\b(?:lost|stolen|missing)\b|\b(?:lost|stolen).{0,25}\b(?:wallet|purse)\b"))
    put("lost_or_stolen_card", 33, card and has(r"\b(?:freeze|block|lock|unfreeze|unblock) (?:my |the )?card\b") and not has(r"\bpin\b"))

    compromised = has(
        r"\bcompromis\w*\b|\bclon\w*\b|\bphishing\b|\bscammer\b|"
        r"\b(?:card|banking) (?:details|information|number).{0,35}\b(?:stolen|leak\w*|someone|wrong hands|exposed)\b|"
        r"\b(?:someone|somebody|fraudster|stranger).{0,30}\b(?:details|card number|security code|access|cvv)\b|"
        r"\b(?:gave|given|shared|sent).{0,35}\b(?:card details|card number|security code|cvv)\b|"
        r"\bcard details.{0,25}\b(?:hacked|copied)\b|\bcard.{0,10}\bhacked\b"
    )
    put("compromised_card", 58, compromised)
    put("compromised_card", 30, has(r"\bfraud\b|\bhacked\b") and not unknown)

    pin = has(r"\bpin\b")
    login = has(r"\blog ?in\b|\blogging\b|\bsign ?in\b|\bapp\b|\bapplication\b|\baccount access\b")
    passcode = has(r"\bpasscode\b|\bpassword\b|\blogin code\b|\blog in code\b|\baccess code\b")
    put("passcode_forgotten", 52, passcode and (
        has(r"\bforgot\w*\b|\bforget\w*\b|\breset\b|\bremember\b|\bwrong\b|\bincorrect\b|\brecover\b|\bchang\w*\b")
        or cannot or failed
    ))
    put("passcode_forgotten", 39, login and (
        cannot or has(r"\blocked out\b|\bnot log\b|\bnot sign\b|\bforgot\w*\b|\breset\b")
    ) and not phone_lost and not has(r"\bverif\w*\b"))
    pin_block = pin and has(
        r"\bblock\w*\b|\block\w*\b|\bunblock\w*\b|\bexceed\w*\b|\btoo many\b|"
        r"\bthree\b|\b3 times\b|\bthird\b|\btries\b|\battempts\b"
    )
    put("pin_blocked", 62, pin_block)
    put("change_pin", 47, pin and not passcode and (
        has(r"\bchang\w*\b|\breset\b|\bforgot\w*\b|\bforget\w*\b|\bremember\b|\bview\b|\bsee\b|"
            r"\bfind\b|\bwhere\b|\bshow\b|\bretrieve\b|\bget\b|\bknow\b|\bnew\b|\bcheck\b|\bwhat\b")
    ))
    put("change_pin", 25, pin and not passcode and not pin_block)

    # Verification has three separate objects: identity, income, and funding card.
    identity = has(
        r"\bidentity\b|\bidentification\b|\bpassport\b|\bselfie\b|\bdriv(?:ing|er|ers) licen[cs]e\b|"
        r"\bnational id\b|\bmy id\b|\bphoto id\b|\bid card\b|\bproof of address\b|"
        r"\bverif\w*.{0,12}\b(?:account|documents)\b"
    )
    verify = has(r"\bverif\w*\b|\bauthenticat\w*\b|\bconfirm\w*\b|\bprove\b|\bvalidat\w*\b")
    funds_proof = has(
        r"\bsource of (?:funds|money|income|wealth)\b|\borigin of (?:my |the )?(?:funds|money)\b|"
        r"\bproof of (?:income|funds|wealth|earnings)\b|\bprove.{0,25}\b(?:income|money came|funds)\b|"
        r"\bwhere (?:my |the |your )?money (?:came|comes|is coming) from\b|"
        r"\b(?:verif\w*|document\w*|proof|evidence).{0,30}\b(?:salary|income|wealth|earnings)\b"
    )
    put("verify_source_of_funds", 64, funds_proof)
    top_verify = (
        (verify and (topup or has(r"\b(?:debit|credit|bank|funding|top up) card\b")))
        or has(r"\b(?:card|top up) verif\w*\b|\bownership.{0,20}\bcard\b|"
               r"\b(?:verification|four digit|4 digit).{0,12}\bcode\b.{0,40}\bstatement\b|"
               r"\bcode.{0,35}\b(?:bank statement|card statement)\b")
    )
    put("verify_top_up", 58, top_verify and not identity)
    put("verify_top_up", 53, verify and has(r"\bdeposit\b") and not identity and not funds_proof)
    why_identity = has(r"\bwhy\b|\bnecessary\b|\bmandatory\b|\brequired\b|\bwithout\b|\bdo i (?:really )?(?:need|have) to\b|\bmust i\b")
    identity_problem = (
        declined or failed or cannot or pending
        or has(r"\bnot (?:been )?(?:verified|approved|accepted)\b|\btoo long\b|\bstuck\b|\bkeeps\b|"
               r"\bnot let\b|\bnot recogn\w*\b|\bnot accept\w*\b|\bnot verif\w*\b")
    )
    put("unable_to_verify_identity", 54, identity and identity_problem)
    put("why_verify_identity", 52, identity and why_identity and not identity_problem)
    put("verify_my_identity", 37, identity)
    put("unable_to_verify_identity", 34, verify and identity_problem and not top_verify and not funds_proof)
    put("verify_my_identity", 24, verify and not top_verify and not funds_proof)
    put("verify_my_identity", 33, has(r"\b(?:what|which).{0,20}\bdocuments\b|\bupload.{0,20}\bdocuments\b") and not funds_proof)

    # Card provisioning and delivery.
    wallet = has(r"\bapple pay\b|\bgoogle pay\b|\bandroid pay\b|\bgoogle wallet\b|\bapple wallet\b|\bsamsung pay\b")
    put("apple_pay_or_google_pay", 60, wallet)
    put("card_swallowed", 68, (
        atm and has(r"\bswallow\w*\b|\bate\b|\beaten\b|\bstuck\b|\bretain\w*\b|\bkept\b|\bkeep\b|\bcaptured\b|"
                    r"\bnot (?:give|return|release|come) (?:my |the |it )?(?:card|back|out)\b|"
                    r"\bnot (?:get|got) (?:my |the )?card back\b")
    ) or has(r"\b(?:swallowed|retained|trapped) (?:my |the )?card\b"))

    put("activate_my_card", 53, card and has(r"\bactivat\w*\b|\binactive\b|\bstart using\b|\benable\b")
        and not has(r"\bcontactless\b|\bdeactivat\w*\b"))
    put("card_about_to_expire", 57, card and has(r"\bexpir\w*\b|\brenew\w*\b|\bvalidity\b|\bvalid (?:until|through)\b"))

    delivery = has(r"\bdeliver\w*\b|\bshipping\b|\bshipped\b|\bdispatch\w*\b|\bpost(?:ed|age)?\b|\bmail\w*\b")
    card_arrive = card and has(r"\barriv\w*\b|\breceiv\w*\b|\bturn(?:ed)? up\b|\bget here\b|\bcome\b")
    already_ordered = has(r"\bordered\b|\brequested\b|\bsent out\b|\bdispatched\b|\bshipped\b|\btracking\b|\btrack\b")
    card_overdue = (
        has(r"\bnot (?:yet )?(?:arriv\w*|receiv\w*|deliver\w*|come)\b|\bnever (?:arriv\w*|receiv\w*|came)\b|"
            r"\bstill waiting\b|\blate\b|\boverdue\b|\bdelayed\b|\bwhere.{0,25}\bcard\b|"
            r"\bcard.{0,25}\bwhere\b|\btrack\w*\b|\bdelivery status\b|\bstatus.{0,15}\bcard\b")
        or (already_ordered and waiting)
    )
    put("card_arrival", 54, card and card_overdue and (delivery or card_arrive or already_ordered or has(r"\bwhere\b")))
    put("card_arrival", 43, card and already_ordered and not has(r"\bhow (?:do|can|to)\b") and not timing)
    put("card_delivery_estimate", 44, card and timing and (delivery or card_arrive or has(r"\bget\b|\bcome\b|\bwait\b")))
    put("card_delivery_estimate", 47, card and delivery and has(r"\bexpress\b|\burgent\b|\bfaster\b|\bexpedit\w*\b") and not card_overdue)
    put("card_delivery_estimate", 28, card and delivery and not card_overdue)
    put("card_arrival", 38, has(r"\bwhere is my (?:new |replacement |physical )?card\b"))

    linking = has(r"\blink\w*\b|\bpair\w*\b|\bconnect\w*\b|\bassociate\w*\b")
    put("card_linking", 49, card and linking and not wallet and not has(r"\bpayment link\b"))
    put("card_linking", 50, card and has(r"\b(?:different|another|other|two|multiple) (?:revolut )?accounts?\b") and not topup)
    put("getting_spare_card", 49, card and has(
        r"\bspare\b|\bbackup\b|\bback up\b|\bsecond\b|\badditional\b|\bextra\b|\btwo\b|\bmultiple\b|"
        r"\bmore than one\b|\bhow many\b|\banother (?:physical |plastic )?card\b"
    ) and not fee and not has(r"\bexpir\w*\b|\bvirtual\b"))
    put("getting_spare_card", 45, card and has(r"\bfor (?:my )?(?:wife|husband|partner|spouse)\b") and not topup)
    disposable_limits = disposable and has(
        r"\blimit\w*\b|\bhow many\b|\bhow much\b|\bmaximum\b|\bminimum\b|\bmore than once\b|"
        r"\bagain\b|\breus\w*\b|\brecurring\b|\bsubscription\b|\bnumber.{0,15}\bchang\w*\b|"
        r"\bchang\w*.{0,15}\bnumber\b|\bmultiple\b|\bonly once\b|\brestriction\b"
    )
    put("disposable_card_limits", 57, disposable_limits)
    put("get_disposable_virtual_card", 42, disposable)
    put("getting_virtual_card", 35, virtual and not disposable)
    put("get_physical_card", 35, physical)
    order = has(r"\border\b|\brequest\b|\bget\b|\bobtain\b|\bapply\b|\bsend\b|\bbuy\b|\bneed\b|\bwant\b|\bissue\b")
    put("order_physical_card", 36, card and order and not virtual and not disposable and not physical
        and not (payment or transfer or topup or withdrawal))
    put("order_physical_card", 42, card and has(r"\border\b|\bordering\b")
        and not virtual and not disposable and not already_ordered)
    put("order_physical_card", 44, card and fee and has(r"\border\b|\bordering\b|\bget a\b|\bgetting\b|\bdelivery\b")
        and not (payment or topup or withdrawal))
    put("get_physical_card", 45, physical and virtual and has(r"\bget\b|\bwant\b|\bneed\b|\bhow\b") and not failed)
    put("order_physical_card", 39, has(r"\bsend me (?:a |my |the )?(?:new |physical |debit |bank )?card\b"))

    put("visa_or_mastercard", 45, has(r"\bvisa\b|\bmastercard\b") and not topup
        and not has(r"\baccept\w*\b.{0,20}\b(?:deposit|add money)\b"))
    put("visa_or_mastercard", 56, has(r"\bvisa\b") and has(r"\bmastercard\b") and not topup
        and not has(r"\bwhich (?:atm|shop|store)\b"))

    # Card functionality and purchase disputes.
    contactless = has(r"\bcontactless\b|\bpaywave\b|\bpaypass\b|\bnfc\b|\btap (?:and|to|my|the|your)\b|\btapping\b|\btouch and go\b")
    put("contactless_not_working", 56, contactless and not wallet)
    virtual_issue = virtual and (declined or failed or cannot or has(r"\bnot accepted\b|\bnot accept\b|\bblocked\b|\bunusable\b"))
    put("virtual_card_not_working", 57, virtual_issue and not disposable_limits and not has(r"\b(?:get|create|order) (?:a |my |the )?virtual card\b"))
    put("virtual_card_not_working", 43, virtual_issue)
    put("card_not_working", 37, card and (failed or cannot or has(r"\bbroken\b|\bdamaged\b|\bnot read\b|\bunusable\b|\bmalfunction\w*\b"))
        and not (topup or transfer or refund or virtual or disposable))
    put("card_not_working", 46, card and has(r"\bchip\b|\bmagnetic\b|\bstripe\b|\bbent\b|\bsnapped\b|\bcracked\b|\bdamaged\b|\bcard reader\b")
        and (failed or cannot or has(r"\bbroken\b|\bdamaged\b|\bbent\b|\bsnapped\b|\bcracked\b")))
    put("declined_card_payment", 46, declined and (card or payment) and not (withdrawal or topup or transfer or identity))
    put("declined_card_payment", 43, payment and (failed or cannot) and not (withdrawal or topup or transfer or refund or identity)
        and not has(r"\bcard (?:does not|is not|stopped) work\b"))
    put("declined_card_payment", 34, has(r"\b(?:online|internet|shop|store|merchant) payment\b") and (failed or cannot))
    put("pending_card_payment", 48, pending and (payment or card) and not (withdrawal or transfer or topup or identity))
    put("pending_card_payment", 43, has(r"\b(?:reserved|earmarked|on hold|authorization hold|authorisation hold)\b") and not (topup or transfer or withdrawal))
    put("pending_card_payment", 33, payment and timing and not (withdrawal or transfer or topup or refund or exchange))
    put("reverted_card_payment", 51, reversed_ and (card or payment) and not (topup or transfer or withdrawal))
    put("card_payment_not_recognised", 52, unknown and (payment or card or has(r"\bstatement\b|\bcharged\b|\bdebited\b"))
        and not (withdrawal or direct_debit or topup or transfer))
    put("card_payment_not_recognised", 48, has(r"\bwhat is this (?:card )?(?:payment|transaction|charge)\b")
        and not (withdrawal or direct_debit or topup))
    put("card_payment_not_recognised", 47, has(r"\b(?:payment|purchase|transaction|charge).{0,25}\bnot mine\b"))

    duplicated = has(
        r"\btwice\b|\bdouble(?:d)?\b|\bduplicat\w*\b|\btwo times\b|\b2 times\b|"
        r"\b(?:two|2) (?:identical |same )?(?:payments|charges|transactions)\b|"
        r"\bcharged.{0,12}\btwo\b|\b(?:paid|charged).{0,12}\bagain\b"
    )
    put("transaction_charged_twice", 58, duplicated and (payment or fee or has(r"\bdebited\b|\bdeducted\b")))

    small_charge = (
        has(r"\b(?:1|one|a single)\s*(?:gbp|eur|usd|penny|cent)\b|"
            r"\b(?:gbp|eur|usd)\s*(?:1|one)\b|\b(?:small|tiny|little|test|nominal) (?:extra |additional )?(?:amount|charge|payment|transaction)\b")
        and (fee or has(r"\bstatement\b|\bdebited\b|\btaken\b|\bdeducted\b|\btransaction\b"))
    )
    put("extra_charge_on_statement", 56, small_charge and not (withdrawal or transfer))
    put("extra_charge_on_statement", 40, has(r"\bextra charge on (?:my |the )?statement\b"))
    put("card_payment_fee_charged", 40, fee_question and (payment or card)
        and not (withdrawal or topup or transfer or exchange or refund)
        and not has(r"\border\b|\bdelivery\b|\bspare\b|\bsecond\b"))
    put("card_payment_fee_charged", 45, has(r"\b(?:card payment|purchase|merchant|paying by card).{0,35}\b(?:fee|extra|surcharge)\b|"
                                           r"\b(?:fee|surcharge).{0,30}\b(?:card payment|purchase)\b"))
    put("card_payment_fee_charged", 39, payment and has(r"\b(?:charged|paid|debited) more\b|\bmore than (?:the|my|i)\b")
        and not (withdrawal or transfer or topup or exchange))

    put("direct_debit_payment_not_recognised", 60, direct_debit)
    put("request_refund", 43, refund and not topup)
    put("request_refund", 52, has(r"\bchargeback\b|\bcharge back\b|\bdisput\w*\b") and not (topup or transfer))
    put("request_refund", 43, has(
        r"\b(?:goods|items|order|product|parcel).{0,30}\b(?:not arrived|never arrived|not received|never received|not delivered|never delivered)\b|"
        r"\bmerchant.{0,25}\b(?:will not refund|refuses? to refund)\b"
    ))
    refund_missing = refund and (
        waiting or pending or timing or has(r"\bwhere\b|\bnot updated\b|\bnot changed\b|\bhas not\b|\brefunded me\b|\bissued\b")
    )
    put("refund_not_showing_up", 57, refund_missing and not (topup and not payment))
    put("refund_not_showing_up", 51, refund and has(r"\bmerchant.{0,20}\brefunded\b|\brefund.{0,25}\bnot\b"))

    # Cash machines: the event type determines the appropriate status category.
    put("atm_support", 24, withdrawal)
    put("atm_support", 44, withdrawal and has(
        r"\bwhich\b|\bwhere\b|\bnearest\b|\bnearby\b|\blocat\w*\b|\bnetwork\b|\bany atm\b|"
        r"\bany cash machine\b|\bwhat atm\b|\bsupported\b|\baccept\w*\b"
    ) and not (unknown or waiting or declined or failed or reversed_ or fee_question or exchange))
    put("atm_support", 33, withdrawal and has(r"\bcan i\b|\bpossible\b|\babroad\b|\boverseas\b") and not fee_question)
    put("declined_cash_withdrawal", 49, withdrawal and (declined or failed or cannot)
        and not has(r"\bcard (?:is not|does not|stopped) working\b"))
    put("pending_cash_withdrawal", 54, withdrawal and pending)
    put("cash_withdrawal_not_recognised", 59, withdrawal and unknown)
    no_cash = has(
        r"\bno cash\b|\bno money (?:came|come|was)\b|\bnot dispens\w*\b|\bdid not dispens\w*\b|"
        r"\bnothing (?:came|come) out\b|\bgave me nothing\b|\bnot (?:give|given|receive|received|get|got).{0,20}\bcash\b|"
        r"\bcash.{0,15}\bnot (?:come|came|dispens\w*)\b|\bnot (?:give|given|receive|received|get|got).{0,12}\b(?:money|anything)\b"
    )
    cash_amount_wrong = has(
        r"\bwrong (?:cash |money )?amount\b|\bless (?:cash|money|than)\b|\btoo (?:much|little)\b|"
        r"\bshort changed\b|\bshortchanged\b|\bnot (?:the )?full amount\b|\b(?:only|partially) dispens\w*\b|"
        r"\bdifferent amount\b"
    )
    debited = has(r"\bcharg\w*\b|\bdebit\w*\b|\bdeduct\w*\b|\btaken from\b|\btook.{0,12}\baccount\b|\bbalance.{0,15}\bdown\b")
    put("wrong_amount_of_cash_received", 61, withdrawal and cash_amount_wrong)
    put("wrong_amount_of_cash_received", 60, withdrawal and no_cash and (debited or has(r"\bdispens\w*\b|\bcame out\b|\bgave\b")))
    put("wrong_amount_of_cash_received", 46, withdrawal and no_cash and not declined)
    put("cash_withdrawal_charge", 49, withdrawal and fee_question and not exchange)
    put("cash_withdrawal_charge", 46, withdrawal and has(r"\blimit\b|\ballowance\b|\bhow much\b|\bmaximum\b|\bmonthly\b") and not cash_amount_wrong)
    put("wrong_exchange_rate_for_cash_withdrawal", 59, withdrawal and (exchange or rate))
    put("cash_withdrawal_charge", 54, withdrawal and exchange and has(r"\bfee\b|\bcommission\b|\bsurcharge\b|\bcharge for\b") and not rate)

    # Cash/cheque deposits are not withdrawals or ordinary bank transfers.
    put("top_up_by_cash_or_cheque", 42, cash_deposit and not withdrawal)
    put("balance_not_updated_after_cheque_or_cash_deposit", 58, cash_deposit and not withdrawal
        and (waiting or pending or has(r"\bnot (?:changed|updated|credited|cleared)\b|\bnot clear\w*\b")))
    put("top_up_by_cash_or_cheque", 39, has(r"\b(?:deposit|top up|pay in).{0,25}\b(?:cash|cheque)\b") and not withdrawal)

    # Card-funded additions to the account.
    nonbank_topup = card_funding and not (bank_funding and not bank_card)
    put("topping_up_by_card", 23, nonbank_topup)
    put("topping_up_by_card", 34, topup and not (bank_transfer or cash_deposit))
    put("topping_up_by_card", 38, has(r"\b(?:remove|delete|change|save).{0,25}\b(?:top up|debit|credit|saved|funding) card\b"))
    put("topping_up_by_card", 39, topup and has(r"\bsomeone else\b|\banother person\b|\bfriends? card\b|\bpartner.s? card\b"))
    put("automatic_top_up", 61, (topup or has(r"\badd money\b|\bfund\w*\b|\breplenish\w*\b|\brefill\w*\b"))
        and has(r"\bautomat\w*\b|\bauto\b|\brecurring\b|\bregular\b|\bschedul\w*\b|\blow balance\b|\bbelow\b"))
    put("automatic_top_up", 55, has(r"\bauto (?:reload|refill|top)\b|\bautomatic (?:reload|refill)\b"))
    put("top_up_limits", 53, (topup or (has(r"\bdeposit\b") and not cash_deposit))
        and has(r"\blimit\w*\b|\bmaximum\b|\bminimum\b|\bhow much\b|\bhow many\b|\blargest\b|\bsmallest\b|\btoo much\b"))
    put("top_up_by_card_charge", 49, nonbank_topup and fee_question)
    put("top_up_failed", 49, nonbank_topup and (declined or failed or cannot))
    put("pending_top_up", 49, nonbank_topup and (pending or waiting or timing))
    put("pending_top_up", 55, has(r"\b(?:card|bank).{0,20}\b(?:charged|debited)\b") and
        has(r"\bbalance.{0,25}\b(?:not|unchanged)\b|\bnot.{0,18}\b(?:balance|account|credited)\b") and not bank_transfer)
    put("top_up_reverted", 57, nonbank_topup and reversed_)
    put("top_up_reverted", 58, topup and has(r"\b(?:returned|refunded|back) to (?:my |the )?(?:bank|card)\b|\breverted\b|\breversed\b"))

    # Which funding instruments/currencies are supported is distinct from paying
    # a merchant with the issued card.
    support_question = has(r"\bwhich\b|\bwhat\b|\bsupport\w*\b|\baccept\w*\b|\bcan i\b|\bpossible\b|\ballow\w*\b|\bus(?:e|ing)\b")
    funding_type = has(
        r"\bamerican express\b|\bamex\b|\bprepaid\b|\bmaestro\b|\bdiners\b|\bdiscover\b|"
        r"\b(?:credit|debit) cards\b|\bforeign card\b|\bcard issued\b|\bissued abroad\b|\btypes? of cards?\b|"
        r"\bwhich (?:bank )?cards?\b|\bwhat (?:bank )?cards?\b"
    )
    put("supported_cards_and_currencies", 49, support_question and funding_type and
        (topup or has(r"\bdeposit\b|\badd\b|\baccept\b|\bsupport\b|\bfund\b")))
    put("supported_cards_and_currencies", 46, topup and has(r"\bcurrenc\w*\b|\b(?:in|with) (?:eur|usd|gbp|dollars|euros|pounds|yen)\b"))
    put("supported_cards_and_currencies", 35, funding_type and support_question and not withdrawal
        and not has(r"\byour card\b|\bmy revolut card\b|\bvisa or mastercard\b"))
    put("topping_up_by_card", 41, topup and has(r"\b(?:a |my )?(?:credit|debit|bank) card\b") and
        not has(r"\bwhich\b|\bwhat\b|\bsupport\w*\b|\bprepaid\b|\bamex\b|\bamerican express\b|\bcurrenc\w*\b"))

    # Incoming and outgoing bank transfers.
    recipient_missing = (
        has(r"\b(?:recipient|beneficiary|payee|friend|person).{0,50}\b(?:not|never|waiting|missing|nothing)\b")
        or (outgoing_explicit and waiting)
    )
    put("transfer_into_account", 32, bank_transfer and incoming)
    put("transfer_into_account", 40, has(
        r"\biban\b|\bbic\b|\bsort code\b|\brouting number\b|\baccount number\b|"
        r"\bbank details\b|\bbeneficiary details\b"
    ) and not has(r"\bwrong\b|\bincorrect\b|\bnot allowed\b|\brejected\b|\bdeclined\b")
        and not has(r"\b(?:change|edit|update).{0,15}\bbeneficiary\b"))
    put("transfer_into_account", 43, has(r"\bsalary\b|\bwages\b|\bpaycheck\b|\bemployer\b") and not waiting)
    put("top_up_by_bank_transfer_charge", 53, bank_funding and fee_question)
    put("top_up_by_bank_transfer_charge", 53, transfer and incoming and fee_question)
    put("transfer_fee_charged", 48, transfer and fee_question and not incoming and not topup)
    put("transfer_fee_charged", 56, transfer and has(
        r"\breceiv\w* less\b|\bless (?:money|than)\b|\bintermediar\w*\b|\bcorrespondent bank\b|"
        r"\bdeduct\w*\b.{0,20}\b(?:fee|transfer)\b"
    ) and not incoming)
    put("transfer_timing", 45, transfer and timing and not pending)
    put("transfer_timing", 40, transfer and has(r"\bhow long\b|\bhow many days\b|\binstant\b|\bweekend\b"))
    put("balance_not_updated_after_bank_transfer", 54, bank_transfer and incoming and waiting and not pending)
    put("balance_not_updated_after_bank_transfer", 53, has(r"\bsalary\b|\bwages\b|\bpaycheck\b") and waiting)
    put("balance_not_updated_after_bank_transfer", 49, transfer and waiting and not outgoing_explicit
        and not has(r"\b(?:i|we) (?:sent|transferred)\b") and not pending)
    put("balance_not_updated_after_bank_transfer", 56, transfer and has(
        r"\b(?:balance|account).{0,30}\b(?:not updated|not changed|unchanged|not credited)\b|"
        r"\bnot (?:showing|appearing|reflected).{0,20}\b(?:balance|revolut)\b"
    ) and not outgoing_explicit)
    put("transfer_not_received_by_recipient", 55, transfer and recipient_missing and not pending)
    put("transfer_not_received_by_recipient", 49, transfer and waiting and has(r"\b(?:i|we) (?:sent|transferred)\b")
        and not incoming and not pending)
    put("pending_transfer", 55, transfer and pending)
    put("declined_transfer", 56, transfer and declined and not topup and not identity)
    put("failed_transfer", 51, transfer and (failed or cannot) and not topup and not identity)
    put("failed_transfer", 54, transfer and reversed_ and not topup)
    put("cancel_transfer", 59, transfer and has(
        r"\bcancel\w*\b|\bstop\b|\brecall\b|\brevoke\b|\bundo\b|\bcall back\b|"
        r"\bcan i (?:reverse|recover)\b|\bwant.{0,12}\breverse\b|\bget.{0,15}\bback\b"
    ) and not has(r"\bwhy.{0,25}\bcancelled\b"))
    put("cancel_transfer", 52, transfer and has(r"\bwrong (?:account|person|recipient|details|iban|amount)\b"))
    beneficiary_blocked = has(
        r"\bbeneficiar\w*.{0,30}\b(?:not allowed|not permitted|blocked|unsupported|not supported|cannot|unable)\b|"
        r"\b(?:not allowed|not permitted|cannot add|unable to add|cannot create|cannot set up).{0,30}\b(?:beneficiar\w*|payee|recipient)\b|"
        r"\brecipient.{0,25}\b(?:not allowed|not supported|not permitted|unsupported)\b"
    )
    put("beneficiary_not_allowed", 63, beneficiary_blocked)
    put("beneficiary_not_allowed", 48, transfer and has(r"\bcrypto\w*\b|\bbitcoin\b|\bexchange platform\b") and (cannot or support_question))
    put("beneficiary_not_allowed", 52, has(r"\b(?:add|create|set up).{0,25}\b(?:beneficiary|recipient|payee)\b") and (cannot or declined or failed))

    # Receiving from another person, including receiving foreign currencies.
    receiving = has(r"\breceiv\w*\b|\bget paid\b|\bsend me\b|\bsend money to me\b|\bpay me\b")
    request_money = has(
        r"\brequest (?:some |a |the )?(?:money|payment|funds)\b|\bpayment link\b|"
        r"\bshare.{0,20}\blink\b|\brevolut me\b|\bsplit (?:a |the )?bill\b"
    )
    put("receiving_money", 38, receiving and not waiting and not (refund or card_arrive or withdrawal))
    put("receiving_money", 49, receiving and has(
        r"\bcurrenc\w*\b|\b(?:eur|usd|gbp|euros|dollars|pounds|yen)\b|\b(?:friend|someone|person|user)\b"
    ) and not waiting and not (refund or withdrawal or card_arrive))
    put("receiving_money", 50, request_money and not refund and not topup)
    put("receiving_money", 47, has(r"\b(?:someone|friend|person|anyone).{0,25}\b(?:send|pay|transfer).{0,20}\b(?:me|my account)\b")
        and not waiting and not has(r"\b(?:bank|swift|iban)\b"))

    # Currency exchange: rate, price, and how-to are different requests.
    currency = has(
        r"\bcurrenc\w*\b|\bfiat\b|\b(?:eur|usd|gbp|euros|dollars|pounds|yen|rupees|francs|zloty|krona|aud|cad|chf|inr|jpy)\b"
    )
    put("exchange_rate", 32, rate and (exchange or currency))
    put("exchange_rate", 37, exchange and rate and not (withdrawal or topup))
    put("exchange_charge", 49, exchange and fee_question and not (withdrawal or topup or transfer))
    put("exchange_charge", 45, exchange and has(r"\ballowance\b|\blimit\b|\bweekend\b|\bfair usage\b|\bmarkup\b|\bcommission\b") and not withdrawal)
    put("exchange_via_app", 38, exchange and has(r"\bhow\b|\bwhere\b|\bwant\b|\bcan i\b|\bpossible\b|\bneed\b") and not (rate or fee_question or withdrawal or topup or transfer))
    put("exchange_via_app", 46, exchange and has(r"\bin (?:the |my )?app\b|\busing (?:the |my )?app\b|\bbetween.{0,20}\baccounts\b")
        and not (rate or fee_question))
    put("exchange_via_app", 40, currency and has(r"\b(?:buy|sell|convert|exchange|change).{0,25}\b(?:eur|usd|gbp|euros|dollars|pounds|yen)\b")
        and not (withdrawal or topup or transfer or fee_question or rate))
    put("card_payment_wrong_exchange_rate", 55, exchange and (rate or has(r"\bwrong\b|\bincorrect\b|\bunfair\b|\bbad\b|\bdifferent\b"))
        and payment and not (withdrawal or topup or transfer or refund))
    put("card_payment_wrong_exchange_rate", 51, has(r"\b(?:card|purchase|paid|bought).{0,35}\b(?:exchange rate|conversion rate)\b") and not (topup or withdrawal))
    put("fiat_currency_support", 39, currency and has(
        r"\bsupport\w*\b|\bavailable\b|\bhold\b|\bkeep\b|\bstore\b|\bwhich\b|\bwhat\b|"
        r"\bopen.{0,15}\baccount\b|\bbalance\b|\bwallet\b"
    ) and not (topup or withdrawal or receiving or rate or fee_question))
    put("fiat_currency_support", 47, has(
        r"\b(?:which|what|supported|available) (?:fiat )?currencies\b|"
        r"\b(?:hold|keep|store).{0,25}\b(?:currenc\w*|dollars|euros|pounds)\b|"
        r"\b(?:currency|eur|usd|gbp|dollar|euro|pound) accounts?\b"
    ) and not (topup or receiving or withdrawal))
    put("fiat_currency_support", 44, has(r"\bfiat\b") and not topup)

    # Eligibility by residence must not be confused with using the issued card
    # overseas or holding a foreign currency.
    country_question = has(
        r"\bcountr(?:y|ies)\b|\bresiden\w*\b|\blive\b|\bliving\b|\bnationalit\w*\b|"
        r"\bcitizen\b|\bavailable in\b|\boperate in\b|\boffer.{0,15}\bin\b"
    )
    signup = has(r"\bopen\b|\bregister\b|\bsign up\b|\bjoin\b|\baccount\b|\bservice\b|\beligib\w*\b|\bsupport\b|\bavailable\b")
    put("country_support", 46, country_question and signup and not personal_detail
        and not (topup or withdrawal or transfer or exchange))
    put("country_support", 44, has(r"\bwhich countries\b|\bwhat countries\b|\bsupported countries\b|\bavailable countries\b")
        and not (card or transfer or topup or withdrawal))
    put("country_support", 37, has(r"\bcan i (?:open|create|register|sign up|join)\b") and has(
        r"\b(?:us|usa|united states|america|india|canada|australia|europe|uk|united kingdom|brazil|singapore|switzerland|germany|france|pakistan|nigeria)\b"
    ) and not currency)
    put("card_acceptance", 35, card and has(r"\bwhere\b|\bwhich (?:shops|stores|countries)\b|\baccept\w*\b|\babroad\b|\boverseas\b|\bworldwide\b|\binternational\w*\b")
        and not (topup or withdrawal or transfer or linking or virtual_issue))
    put("card_acceptance", 42, card and has(r"\bcan i use\b|\bcan i pay\b|\bwill.{0,15}\bwork in\b|\bpossible to (?:use|pay)\b")
        and not (topup or withdrawal or transfer or exchange or virtual or disposable or contactless))
    put("card_acceptance", 42, has(
        r"\b(?:paypal|amazon|ebay|petrol station|gas station|hotel|car rental|online shops|online stores)\b"
    ) and (card or payment) and not (failed or declined or unknown or topup or refund))
    put("card_acceptance", 40, has(r"\bcard.{0,25}\baccepted\b") and not (declined or cannot or failed or topup or virtual or withdrawal))

    # A few relational corrections where generic words otherwise give a
    # misleading domain (for example "charged" does not itself mean a fee).
    if withdrawal:
        for label in (
            "card_payment_fee_charged", "card_payment_not_recognised",
            "declined_card_payment", "pending_card_payment",
            "card_payment_wrong_exchange_rate",
        ):
            evidence[label] = min(evidence[label], 15)
    if nonbank_topup:
        for label in ("declined_card_payment", "pending_card_payment", "card_payment_fee_charged"):
            evidence[label] = min(evidence[label], 15)
    if identity or funds_proof:
        if not top_verify:
            evidence["verify_top_up"] = min(evidence["verify_top_up"], 15)
    if disposable_limits:
        evidence["virtual_card_not_working"] = min(evidence["virtual_card_not_working"], 35)
    if has(r"\bcard (?:has |was |is )?(?:lost|stolen)\b|\b(?:lost|stolen) my card\b") and card_overdue:
        evidence["lost_or_stolen_card"] = max(evidence["lost_or_stolen_card"], 54)
    elif card_overdue and already_ordered:
        evidence["lost_or_stolen_card"] = min(evidence["lost_or_stolen_card"], 20)

    # How-to verification is not a request to see an unexplained charge.
    if top_verify and has(r"\bcode\b|\bverify\b|\bverification\b|\bconfirm\b"):
        evidence["extra_charge_on_statement"] = min(evidence["extra_charge_on_statement"], 35)

    for label, value in evidence.items():
        scores[label] += value

    answer = max(_EXAMPLES, key=lambda label: scores[label])
    return {"answer": answer}
