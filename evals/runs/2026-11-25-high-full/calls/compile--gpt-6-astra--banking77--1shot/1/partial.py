import re
import math
import unicodedata
from collections import Counter


_PROTOTYPES = {
    "activate_my_card": [
        "How do I activate my new card?",
        "I need to activate the card that just arrived.",
        "Where is the card activation option?",
        "Do I have to make a chip and PIN purchase to activate my card?",
        "My replacement card needs activating.",
    ],
    "age_limit": [
        "How old do you have to be to open an account?",
        "Can my child get a card?",
        "Is there a minimum age requirement?",
        "Can a teenager under eighteen use this service?",
        "I am sixteen and want to open an account.",
        "Can I open an account for my daughter?",
    ],
    "apple_pay_or_google_pay": [
        "Can I add my card to Apple Pay?",
        "How do I use Google Pay?",
        "My card cannot be added to my Apple wallet.",
        "Does the card work with Google wallet?",
        "How do I set up payments on my Apple watch?",
        "Is Android Pay supported?",
    ],
    "atm_support": [
        "Which ATMs can I use?",
        "Where can I withdraw cash?",
        "Can I use any cash machine with this card?",
        "Which cash machines accept my card?",
        "Can I withdraw money overseas?",
        "Where is the nearest supported ATM?",
    ],
    "automatic_top_up": [
        "How do I set up automatic top ups?",
        "Can my account be topped up automatically when the balance is low?",
        "How do I turn off auto top up?",
        "I want to change my automatic recharge settings.",
        "Can I schedule recurring top ups?",
        "My automatic top up stopped working.",
    ],
    "balance_not_updated_after_bank_transfer": [
        "I transferred money from my bank but my balance has not updated.",
        "My incoming bank transfer has not appeared in my account.",
        "I sent money into my account and it is still missing.",
        "A bank deposit is not showing on my balance.",
        "Where is the money I transferred to my Revolut account?",
        "My salary was sent but has not reached my account.",
    ],
    "balance_not_updated_after_cheque_or_cash_deposit": [
        "I deposited cash but my balance has not changed.",
        "My cheque deposit is not showing in my account.",
        "I paid a check into my account and the money is missing.",
        "When will the cash I deposited be credited?",
        "The balance is unchanged after a cash deposit.",
    ],
    "beneficiary_not_allowed": [
        "Why is this beneficiary not allowed?",
        "I cannot transfer to this recipient because they are not permitted.",
        "The app says beneficiary is not allowed.",
        "Why is the recipient blocked?",
        "This beneficiary cannot be added.",
        "A transfer to this particular beneficiary is prohibited.",
    ],
    "cancel_transfer": [
        "How can I cancel a bank transfer?",
        "I sent money to the wrong account and want to stop the transfer.",
        "Can I reverse a transfer I made?",
        "I need to recall a payment sent to another bank.",
        "Can I cancel a pending transfer?",
        "I used the wrong bank details for my transfer.",
    ],
    "card_about_to_expire": [
        "My card is about to expire.",
        "How do I replace an expired card?",
        "Will you send a new card when mine expires?",
        "What happens when my card reaches its expiry date?",
        "I need to renew my card.",
    ],
    "card_acceptance": [
        "Where can I use my card?",
        "Is this card accepted in shops abroad?",
        "Can I pay online with my card?",
        "Will my card work in another country?",
        "Which merchants accept the card?",
        "Can I use the card to pay at a hotel?",
    ],
    "card_arrival": [
        "My card has not arrived yet.",
        "Where is the card I ordered?",
        "I ordered my card weeks ago and it is still missing.",
        "How do I track my card delivery?",
        "The app says delivered but I did not receive my card.",
        "My card delivery is late.",
        "What is the status of my card order?",
    ],
    "card_delivery_estimate": [
        "How long does card delivery take?",
        "When will a new card arrive?",
        "What is the estimated delivery time for a card?",
        "How quickly can you deliver a physical card?",
        "Do you offer express card delivery?",
        "How many days should I allow for my card to arrive?",
    ],
    "card_linking": [
        "How do I link my card to my account?",
        "Can I link an existing card to another account?",
        "My card is linked to a different account.",
        "I want to connect my card to the app.",
        "Can I have the same card linked to two accounts?",
        "How can I unlink a card?",
    ],
    "card_not_working": [
        "My card is not working.",
        "My card has stopped working for some reason.",
        "The chip on my card is damaged.",
        "My physical card does not work anywhere.",
        "My card is broken and I need help.",
        "The card reader cannot read my card.",
    ],
    "card_payment_fee_charged": [
        "Why was I charged a fee for paying with my card?",
        "There was an extra charge on a card purchase.",
        "Are there fees for card payments abroad?",
        "I paid at a shop and was charged more than expected.",
        "Why is there a surcharge for a card transaction?",
        "Does paying with my card cost extra?",
    ],
    "card_payment_not_recognised": [
        "There is a card payment I do not recognise.",
        "I did not make this purchase.",
        "An unknown merchant has charged my card.",
        "Someone used my card for a transaction I did not authorise.",
        "I see a suspicious payment on my account.",
        "What is this payment on my statement?",
    ],
    "card_payment_wrong_exchange_rate": [
        "The exchange rate on my card payment is wrong.",
        "I paid abroad and the conversion rate was incorrect.",
        "The merchant payment used a bad exchange rate.",
        "Why did my purchase use a different currency conversion rate?",
        "I was charged the wrong rate for an overseas card purchase.",
    ],
    "card_swallowed": [
        "The ATM swallowed my card.",
        "A cash machine kept my card.",
        "My card is stuck inside an ATM.",
        "The machine did not give my card back.",
        "How can I retrieve my card from the cash machine?",
    ],
    "cash_withdrawal_charge": [
        "Why was I charged for withdrawing cash?",
        "What are your ATM withdrawal fees?",
        "How much cash can I withdraw without paying a fee?",
        "The cash machine charged an extra fee.",
        "Is withdrawing money abroad free?",
        "I was charged a commission for an ATM withdrawal.",
    ],
    "cash_withdrawal_not_recognised": [
        "There is a cash withdrawal I do not recognise.",
        "I did not withdraw this cash.",
        "An unauthorised ATM withdrawal appears on my account.",
        "Someone took cash out using my card.",
        "I have never used that cash machine but it charged me.",
    ],
    "change_pin": [
        "How can I change my card PIN?",
        "I want a new PIN number for my card.",
        "Where do I find my card PIN?",
        "I forgot the PIN for my bank card.",
        "Can I reset my PIN at an ATM?",
        "How do I view or retrieve the PIN?",
    ],
    "compromised_card": [
        "I think my card details have been stolen.",
        "My card has been compromised.",
        "Someone copied my card number.",
        "I think my card was cloned.",
        "I gave my card information to a scammer.",
        "How can I secure my card after someone got its details?",
    ],
    "contactless_not_working": [
        "Contactless payments are not working.",
        "My card will not work when I tap it.",
        "Tap to pay stopped working.",
        "I cannot make a contactless payment.",
        "Why does contactless keep asking for a PIN?",
        "The contactless feature on my card is disabled.",
    ],
    "country_support": [
        "Which countries do you support?",
        "Can I open an account if I live in another country?",
        "Is Revolut available to residents of Canada?",
        "I am moving abroad and want to know if I can keep my account.",
        "Can a non resident sign up?",
        "What countries can people register from?",
    ],
    "declined_card_payment": [
        "My card payment was declined.",
        "The shop rejected my card transaction.",
        "Why was my online purchase refused?",
        "My card was declined even though I have enough money.",
        "A payment with my card will not go through.",
        "The merchant would not accept my payment.",
    ],
    "declined_cash_withdrawal": [
        "My cash withdrawal was declined.",
        "The ATM refuses to let me withdraw money.",
        "I cannot take cash out at the machine.",
        "My withdrawal was rejected despite having enough funds.",
        "The cash machine says the transaction is denied.",
        "Why will the ATM not dispense money?",
    ],
    "declined_transfer": [
        "Why was my bank transfer declined?",
        "My transfer was rejected.",
        "The bank refused my transfer.",
        "My money transfer was denied.",
        "An outgoing transfer is marked declined.",
    ],
    "direct_debit_payment_not_recognised": [
        "I do not recognise a direct debit.",
        "An unknown direct debit has been taken.",
        "I never authorised this direct debit payment.",
        "What is this direct debit on my account?",
        "Someone set up a direct debit without my permission.",
    ],
    "disposable_card_limits": [
        "What are the limits on disposable virtual cards?",
        "How many disposable cards can I create?",
        "Can I use a disposable card more than once?",
        "Where can I use a disposable virtual card?",
        "Can a single use card be used for subscriptions?",
        "How much can I spend on a disposable card?",
    ],
    "edit_personal_details": [
        "How do I change my personal details?",
        "I need to update my address.",
        "Can I change the phone number on my account?",
        "My name has changed and I need to update it.",
        "I want to edit my email address.",
        "The date of birth on my profile is incorrect.",
    ],
    "exchange_charge": [
        "Is there a fee for exchanging currencies?",
        "Why was I charged a currency exchange commission?",
        "Does currency conversion cost anything?",
        "What is the weekend currency exchange markup?",
        "How much can I exchange without a fee?",
        "There was an extra charge when I converted my money.",
    ],
    "exchange_rate": [
        "What exchange rate do you use?",
        "How are your currency exchange rates calculated?",
        "Where can I see the current conversion rate?",
        "Do you use the interbank exchange rate?",
        "What is the rate for converting euros to pounds?",
        "Why do exchange rates change?",
    ],
    "exchange_via_app": [
        "How can I exchange money in the app?",
        "I want to convert pounds into euros.",
        "Where do I change currencies?",
        "Can I exchange one currency for another?",
        "How do I buy foreign currency using my balance?",
        "I cannot find the currency exchange feature.",
    ],
    "extra_charge_on_statement": [
        "Why is there an extra one pound charge on my statement?",
        "I see a small extra charge on my account.",
        "What is this additional one euro transaction?",
        "My card was charged a dollar for verification.",
        "There is a small test charge I did not expect.",
        "Why was I charged an extra 1?",
    ],
    "failed_transfer": [
        "My bank transfer failed.",
        "The money transfer was unsuccessful.",
        "I cannot make a transfer because it keeps failing.",
        "My transfer was returned to my account.",
        "A bank transfer bounced back.",
        "There is an error when I try to transfer money.",
    ],
    "fiat_currency_support": [
        "What currencies can I hold in my account?",
        "Which fiat currencies are supported?",
        "Can I have a balance in US dollars?",
        "Can I keep money in several currencies?",
        "Is the euro supported as an account currency?",
        "Can I open a foreign currency account?",
    ],
    "get_disposable_virtual_card": [
        "How do I get a disposable virtual card?",
        "I want to create a single use card.",
        "Where can I find disposable card details?",
        "What is a disposable virtual card?",
        "Can I get a temporary card for online shopping?",
        "How do I generate a new one time card?",
    ],
    "get_physical_card": [
        "How can I get a physical card?",
        "I need a real plastic card instead of a virtual one.",
        "Can I have a physical card?",
        "How do I get an actual card?",
        "Is a physical card provided with my account?",
    ],
    "getting_spare_card": [
        "Can I get a spare card?",
        "I want an additional card for my account.",
        "How do I get a second card?",
        "Can I have more than one physical card?",
        "I would like a backup card.",
        "Can I order an extra card for my partner?",
    ],
    "getting_virtual_card": [
        "How do I get a virtual card?",
        "I want to create a virtual card.",
        "Where can I find my virtual card?",
        "Can I get a digital card for online purchases?",
        "Why can I not order a virtual card?",
        "What is a virtual card?",
    ],
    "lost_or_stolen_card": [
        "I lost my card.",
        "My wallet was stolen with my card in it.",
        "I cannot find my bank card.",
        "How do I report a stolen card?",
        "I misplaced my card and need a replacement.",
        "I left my card somewhere.",
    ],
    "lost_or_stolen_phone": [
        "I lost my phone.",
        "My mobile phone was stolen.",
        "How can I access my account without my lost phone?",
        "Someone stole the phone with my banking app on it.",
        "I cannot find my phone.",
    ],
    "order_physical_card": [
        "How do I order a physical card?",
        "I want to order my first card.",
        "Where is the option to order a plastic card?",
        "I cannot order a new card in the app.",
        "Is there a fee to order a card?",
        "How much does a physical card cost?",
    ],
    "passcode_forgotten": [
        "I forgot my passcode.",
        "I cannot remember my app password.",
        "How do I reset my login code?",
        "I am locked out of the app because I forgot my password.",
        "I forgot the PIN used to log into my account.",
        "How can I recover access to my account?",
    ],
    "pending_card_payment": [
        "My card payment is pending.",
        "Why is a purchase still processing?",
        "A card transaction is stuck on pending.",
        "How long will this merchant payment stay on hold?",
        "The money for my purchase is reserved.",
        "When will my card payment be completed?",
    ],
    "pending_cash_withdrawal": [
        "My cash withdrawal is pending.",
        "Why does my ATM transaction still say processing?",
        "A cash withdrawal has been pending for days.",
        "The withdrawal is not completed in the app.",
        "How long can a cash withdrawal stay pending?",
    ],
    "pending_top_up": [
        "My top up is pending.",
        "I added money by card but it is still processing.",
        "My card top up has not completed yet.",
        "Why is my top up taking so long?",
        "The money I loaded by card has not appeared.",
        "My top up is stuck on processing.",
    ],
    "pending_transfer": [
        "My transfer is pending.",
        "An outgoing bank transfer is still processing.",
        "Why is my transfer taking so long?",
        "I have an outgoing transaction.",
        "The transfer has not completed yet.",
        "The money I sent is stuck on pending.",
    ],
    "pin_blocked": [
        "My PIN is blocked.",
        "I entered the wrong PIN too many times.",
        "How can I unblock my PIN?",
        "I exceeded the number of PIN attempts.",
        "The ATM says PIN tries exceeded.",
        "My card is locked after three incorrect PIN entries.",
    ],
    "receiving_money": [
        "How can someone send money to me?",
        "Can I receive my salary into this account?",
        "How do I get paid by my employer?",
        "Can friends send me money?",
        "What details do I give someone who wants to pay me?",
        "Can I receive payments from another person?",
    ],
    "refund_not_showing_up": [
        "My refund has not arrived.",
        "The merchant refunded me but I cannot see the money.",
        "How long does it take for a refund to appear?",
        "I am still waiting for a refund.",
        "A refund is missing from my balance.",
        "When will my returned purchase be credited?",
    ],
    "request_refund": [
        "How do I request a refund?",
        "I want to get my money back for a purchase.",
        "Can I dispute a card payment?",
        "How do I start a chargeback?",
        "The merchant will not refund my purchase.",
        "I want to cancel a card payment and get a refund.",
    ],
    "reverted_card_payment": [
        "My card payment was reverted.",
        "A purchase was reversed and the money came back.",
        "Why was a card transaction automatically reversed?",
        "A merchant payment was returned to my balance.",
        "The payment now says reverted.",
    ],
    "supported_cards_and_currencies": [
        "Which cards can I use to top up?",
        "Can I add money with American Express?",
        "What currencies are supported for card top ups?",
        "Can I use a prepaid card to add money?",
        "Do you accept credit cards issued abroad for topping up?",
        "Can I top up with a foreign debit card?",
    ],
    "terminate_account": [
        "How do I close my account?",
        "I want to terminate my account.",
        "Can I delete my account permanently?",
        "Please cancel my membership and close the account.",
        "I no longer want to use this service.",
        "How do I deactivate my account?",
    ],
    "top_up_by_bank_transfer_charge": [
        "Is there a fee for adding money by bank transfer?",
        "What does an incoming bank transfer cost?",
        "Will I be charged to transfer money into my account?",
        "Why was money deducted from my incoming transfer?",
        "Does receiving an international bank transfer have a fee?",
    ],
    "top_up_by_card_charge": [
        "Is there a fee for topping up by card?",
        "I was charged extra when I added money using my debit card.",
        "Are card top ups free?",
        "Why did my bank charge me for a top up?",
        "How much does it cost to add money with a credit card?",
    ],
    "top_up_by_cash_or_cheque": [
        "Can I top up with cash?",
        "How can I deposit a cheque into my account?",
        "Can I pay cash into my account at a bank?",
        "Do you accept check deposits?",
        "Where can I deposit physical money?",
        "Can I add money using a cheque?",
    ],
    "top_up_failed": [
        "My top up failed.",
        "I cannot add money using my card.",
        "My card was declined when I tried to top up.",
        "Adding money gives an error.",
        "My top up was unsuccessful.",
        "Why will my card top up not go through?",
    ],
    "top_up_limits": [
        "What is the maximum amount I can top up?",
        "Is there a limit on adding money?",
        "What is the minimum top up amount?",
        "How can I increase my top up limit?",
        "How much money can I add to my account in one day?",
        "How many times can I top up?",
    ],
    "top_up_reverted": [
        "My top up was reverted.",
        "The money I added was returned to my bank card.",
        "Why did my top up reverse?",
        "My top up was canceled and the funds sent back.",
        "The top up appeared and then disappeared.",
    ],
    "topping_up_by_card": [
        "How do I top up using a debit card?",
        "Can I add money with a credit card?",
        "How do I save a card for topping up?",
        "Can I use someone else's card to top up?",
        "Where is the add money option?",
        "How do I fund my account with a bank card?",
    ],
    "transaction_charged_twice": [
        "I was charged twice for the same transaction.",
        "There is a duplicate payment on my statement.",
        "I paid once but two payments were taken.",
        "The same purchase appears twice.",
        "My account has been debited two times.",
        "Why was the payment taken again?",
    ],
    "transfer_fee_charged": [
        "Why was I charged a transfer fee?",
        "Is there a charge for sending money to another bank?",
        "How much does an international transfer cost?",
        "The recipient got less money because of a transfer charge.",
        "Are there fees for sending money abroad?",
    ],
    "transfer_into_account": [
        "How do I transfer money into my account?",
        "What bank details do I use to make an incoming transfer?",
        "Where can I find my IBAN and account number?",
        "How can I fund my account from another bank?",
        "What reference should I use for a bank transfer?",
        "Can I make an international transfer to my Revolut account?",
    ],
    "transfer_not_received_by_recipient": [
        "The recipient has not received my transfer.",
        "I sent money to my friend but it has not arrived.",
        "A completed transfer has not reached the beneficiary.",
        "The bank account I transferred to has not received the money.",
        "My transfer says complete but the recipient has no money.",
        "I sent money to my other bank and it is missing.",
    ],
    "transfer_timing": [
        "How long does a bank transfer take?",
        "When will a transfer reach the recipient?",
        "Are bank transfers processed on weekends?",
        "How quickly can I send money to another bank?",
        "What is the usual time for an international transfer?",
        "How many business days does a transfer need?",
    ],
    "unable_to_verify_identity": [
        "I cannot verify my identity.",
        "My identity verification failed.",
        "My identity documents were rejected.",
        "The app will not accept my passport photo.",
        "I am having trouble uploading my ID.",
        "My identity verification has been pending for a long time.",
    ],
    "verify_my_identity": [
        "How do I verify my identity?",
        "What documents are required for identity verification?",
        "Where do I upload my identification?",
        "Can I use my passport to verify my account?",
        "What do I need to complete the identity check?",
        "How do I take the verification selfie?",
    ],
    "verify_source_of_funds": [
        "How can I verify my source of funds?",
        "Why do you need proof of where my money came from?",
        "What documents prove my income?",
        "I need to submit a bank statement to verify the origin of my money.",
        "How do I prove my source of wealth?",
        "Can I use payslips to verify my funds?",
    ],
    "verify_top_up": [
        "How do I verify a card top up?",
        "Where can I find the top up verification code?",
        "I need to verify the card used to add money.",
        "Why must I verify my deposit card?",
        "What is the four digit code on my bank statement?",
        "How do I authenticate the card I topped up with?",
    ],
    "virtual_card_not_working": [
        "My virtual card is not working.",
        "A payment with my virtual card was declined.",
        "I cannot pay online using my digital card.",
        "My virtual card details are not accepted.",
        "Why did my virtual card stop working?",
    ],
    "visa_or_mastercard": [
        "Will I get a Visa or Mastercard?",
        "Can I choose between Visa and Mastercard?",
        "I want a Visa instead of a Mastercard.",
        "What type of card will you issue?",
        "Can I change my card from Visa to Mastercard?",
        "Do you issue Visa cards?",
    ],
    "why_verify_identity": [
        "Why do I have to verify my identity?",
        "Why is identity verification necessary?",
        "Can I use the account without verifying my identity?",
        "Why do you need a picture of my ID?",
        "What is the reason for asking for my passport?",
        "Do I really have to provide identification?",
    ],
    "wrong_amount_of_cash_received": [
        "The ATM gave me the wrong amount of cash.",
        "I received less cash than I requested.",
        "My account was debited but the machine gave me no cash.",
        "The cash machine only dispensed part of my withdrawal.",
        "I withdrew fifty but only received twenty.",
        "The amount deducted is different from the cash I got.",
    ],
    "wrong_exchange_rate_for_cash_withdrawal": [
        "The exchange rate for my cash withdrawal is wrong.",
        "The ATM used a bad conversion rate.",
        "I withdrew cash abroad and got an incorrect exchange rate.",
        "Why was a different rate used to convert my cash withdrawal?",
        "My withdrawal was converted at an unfair rate.",
    ],
}

_LABELS = tuple(_PROTOTYPES)


def _extract_text(state):
    if isinstance(state, str):
        return state
    if isinstance(state, dict):
        for key in (
            "text", "utterance", "message", "query", "customer_message",
            "customer_query", "input", "description", "content",
        ):
            if key in state:
                value = state[key]
                if isinstance(value, str):
                    return value
                if isinstance(value, (dict, list, tuple)):
                    return _extract_text(value)
        if "messages" in state and isinstance(state["messages"], (list, tuple)):
            messages = state["messages"]
            for message in reversed(messages):
                if isinstance(message, dict) and message.get("role") == "user":
                    return _extract_text(message)
            return _extract_text(messages)
        if "state" in state:
            return _extract_text(state["state"])
        return " ".join(
            _extract_text(value)
            for value in state.values()
            if isinstance(value, (str, dict, list, tuple))
        )
    if isinstance(state, (list, tuple)):
        return " ".join(_extract_text(value) for value in state)
    return ""


def _normalize(text):
    text = unicodedata.normalize("NFKC", text).lower()
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")
    text = re.sub(r"[-–—_/]", " ", text)
    replacements = {
        "can't": "cannot", "cant": "cannot",
        "won't": "will not", "wont": "will not",
        "don't": "do not", "dont": "do not",
        "doesn't": "does not", "doesnt": "does not",
        "didn't": "did not", "didnt": "did not",
        "isn't": "is not", "isnt": "is not",
        "aren't": "are not", "arent": "are not",
        "wasn't": "was not", "wasnt": "was not",
        "weren't": "were not",
        "haven't": "have not", "havent": "have not",
        "hasn't": "has not", "hasnt": "has not",
        "hadn't": "had not",
        "couldn't": "could not", "couldnt": "could not",
        "wouldn't": "would not", "wouldnt": "would not",
        "shouldn't": "should not",
        "i'm": "i am", "im": "i am",
        "i've": "i have", "ive": "i have",
        "i'd": "i would", "i'll": "i will",
        "it's": "it is", "that's": "that is",
        "what's": "what is", "where's": "where is",
        "there's": "there is", "how's": "how is",
        "they've": "they have", "you've": "you have",
        "recieve": "receive", "recieved": "received",
        "recieving": "receiving", "receieved": "received",
        "withdrawl": "withdrawal", "withdrawls": "withdrawals",
        "withraw": "withdraw", "transfered": "transferred",
        "transffer": "transfer", "transation": "transaction",
        "benificiary": "beneficiary", "beneficary": "beneficiary",
        "recognize": "recognise", "recognized": "recognised",
        "recognizing": "recognising", "unrecognized": "unrecognised",
        "unauthorized": "unauthorised", "authorized": "authorised",
        "canceled": "cancelled", "canceling": "cancelling",
        "checkings": "checking", "mastercard®": "mastercard",
    }
    text = re.sub(
        r"\b[a-z]+(?:'[a-z]+)?\b",
        lambda match: replacements.get(match.group(0), match.group(0)),
        text,
    )
    text = re.sub(r"\btop(?:ping|ped)?up\b", "top up", text)
    text = re.sub(r"\btop ups?\b", "top up", text)
    text = re.sub(r"\bmaster card\b", "mastercard", text)
    text = re.sub(r"\b(?:gpay|g pay)\b", "google pay", text)
    text = re.sub(r"\b(?:applepay)\b", "apple pay", text)
    text = re.sub(r"\b(?:googlepay)\b", "google pay", text)
    text = re.sub(r"\b(?:cashpoint|cash point|cash machine|cash dispenser)s?\b", "atm", text)
    text = re.sub(r"\ba\.?t\.?m\.?s?\b", "atm", text)
    text = re.sub(r"\be mail\b", "email", text)
    return re.sub(r"\s+", " ", text).strip()


_STOPWORDS = set(
    "a an the i me my mine we us our you your yours he she his her they them their "
    "it its this that these those am is are was were be been being do does did "
    "have has had having can could would should will shall may might must of "
    "for to from with by at in on into as and or but if so than then there here "
    "please hi hello help need want would like really just also about some any "
    "revolut account accounts banking bank thanks thank tell know get got getting "
    "what which how why when where still yet now very something thing one"
    .split()
)

_WORD_ROOTS = {
    "cards": "card",
    "paid": "pay", "paying": "pay", "payments": "payment",
    "purchases": "purchase", "purchased": "purchase", "buy": "purchase",
    "bought": "purchase", "buying": "purchase",
    "charged": "charge", "charging": "charge", "charges": "charge",
    "fees": "fee", "surcharge": "fee", "commission": "fee",
    "costs": "cost", "costing": "cost",
    "withdrawals": "withdraw", "withdrawal": "withdraw", "withdrawing": "withdraw",
    "withdrew": "withdraw", "withdrawn": "withdraw",
    "transfers": "transfer", "transferring": "transfer", "transferred": "transfer",
    "transactions": "transaction",
    "receiving": "receive", "received": "receive", "receives": "receive",
    "recipient": "recipient", "recipients": "recipient",
    "arrived": "arrive", "arrives": "arrive", "arriving": "arrive",
    "delivered": "delivery", "deliver": "delivery",
    "ordered": "order", "ordering": "order",
    "topped": "top", "topping": "top",
    "adding": "add", "added": "add",
    "loaded": "load", "loading": "load", "recharge": "top",
    "declined": "decline", "declining": "decline",
    "rejected": "decline", "refused": "decline", "denied": "decline",
    "failed": "fail", "failing": "fail", "unsuccessful": "fail",
    "working": "work", "works": "work", "worked": "work",
    "forgot": "forget", "forgotten": "forget",
    "stolen": "steal", "stole": "steal", "misplaced": "lost",
    "reverted": "reverse", "reversed": "reverse", "reversal": "reverse",
    "revert": "reverse", "bounced": "reverse",
    "refunded": "refund", "refunds": "refund",
    "currencies": "currency", "countries": "country",
    "converting": "exchange", "convert": "exchange", "conversion": "exchange",
    "converted": "exchange", "exchanging": "exchange",
    "rates": "rate", "limits": "limit", "details": "detail",
    "cheques": "cheque", "checks": "cheque", "check": "cheque",
    "deposited": "deposit", "depositing": "deposit", "deposits": "deposit",
    "verification": "verify", "verified": "verify", "verifying": "verify",
    "identification": "identity",
    "blocked": "block", "blocking": "block",
    "expired": "expire", "expires": "expire", "expiry": "expire", "expiration": "expire",
    "activating": "activate", "activated": "activate", "activation": "activate",
    "linked": "link", "linking": "link",
    "changing": "change", "changed": "change",
    "updated": "update", "updating": "update",
    "cancelled": "cancel", "cancelling": "cancel",
    "closing": "close", "closed": "close",
    "automatic": "auto", "automatically": "auto",
    "sending": "send", "sent": "send",
    "takes": "take", "taking": "take", "took": "take",
    "recognised": "recognise", "unrecognised": "unknown",
    "unauthorised": "unknown", "unfamiliar": "unknown",
    "incorrect": "wrong", "inaccurate": "wrong",
    "twice": "duplicate", "double": "duplicate", "duplicated": "duplicate",
    "second": "spare", "additional": "spare", "backup": "spare",
    "mobile": "phone", "cellphone": "phone", "smartphone": "phone",
    "plastic": "physical", "digital": "virtual",
    "dollars": "dollar", "euros": "euro", "pounds": "pound",
    "maximum": "limit", "minimum": "minimum",
    "minutes": "minute", "days": "day", "weeks": "week",
}


def _features(text):
    words = re.findall(r"[a-z]+|\d+(?:\.\d+)?|[£$€]", _normalize(text))
    words = [
        _WORD_ROOTS.get(word, word)
        for word in words
        if word not in _STOPWORDS
    ]
    result = set(words)
    for left, right in zip(words, words[1:]):
        result.add(left + ":" + right)
    return result


def _build_similarity_model():
    category_features = {}
    prototype_features = []
    for label, examples in _PROTOTYPES.items():
        combined = set()
        for text in [label.replace("_", " ")] + examples:
            features = _features(text)
            combined.update(features)
            prototype_features.append((label, features))
        category_features[label] = combined
    counts = Counter()
    for features in category_features.values():
        counts.update(features)
    n = len(_LABELS)
    weights = {
        feature: (1.0 + math.log((n + 1.0) / (count + 1.0)))
        * (0.72 if ":" in feature else 1.0)
        for feature, count in counts.items()
    }
    prototypes = []
    for label, features in prototype_features:
        norm = math.sqrt(sum(weights[feature] ** 2 for feature in features)) or 1.0
        prototypes.append((label, features, norm))
    return weights, prototypes


_WEIGHTS, _SIMILARITY_PROTOTYPES = _build_similarity_model()
_CANONICAL_LABELS = {_normalize(label): label for label in _LABELS}


def _similarity_scores(text):
    features = _features(text)
    known = features.intersection(_WEIGHTS)
    norm = math.sqrt(sum(_WEIGHTS[feature] ** 2 for feature in known))
    scores = {label: 0.0 for label in _LABELS}
    if not norm:
        return scores
    for label, prototype, prototype_norm in _SIMILARITY_PROTOTYPES:
        shared = known.intersection(prototype)
        if not shared:
            continue
        dot = sum(_WEIGHTS[feature] ** 2 for feature in shared)
        similarity = dot / (norm * prototype_norm)
        if similarity > scores[label]:
            scores[label] = similarity
    return scores


def predict(state):
    text = _extract_text(state)
    t = _normalize(text)
    canonical = t.strip(" .?!:;\"'")
    if canonical in _CANONICAL_LABELS:
        return {"answer": _CANONICAL_LABELS[canonical]}
    if canonical == "i have an outgoing transaction":
        return {"answer": "pending_transfer"}
    if not t:
        return {"answer": "pending_transfer"}

    scores = {label: 0.0 for label in _LABELS}

    def has(pattern):
        return re.search(pattern, t) is not None

    def word(pattern):
        return has(r"\b(?:" + pattern + r")\b")

    def offer(label, score):
        if score > scores[label]:
            scores[label] = float(score)

    card = word(r"cards?|visa|mastercard|amex")
    virtual = word(r"virtual|digital|online only")
    disposable = word(
        r"disposable|single use|one (?:time|use)|temporary card|throwaway|throw away"
    )
    cash = word(
        r"atm|withdraw(?:al|als|ing|n)?|withdrew|take (?:some |my |the )?(?:cash|money) out"
        r"|taking (?:cash|money) out|cash (?:withdrawal|withdrawals|out)"
        r"|get cash out"
    )
    cheque = word(r"cheques?|checks?")
    cash_deposit = (
        word(r"(?:cash|cheque|check) deposits?|deposit(?:ed|ing)? (?:some |a |the |my )?(?:cash|cheques?|checks?)")
        or cheque and word(r"deposit|deposited|pay|paid|top up|topping up|add|adding")
        or word(r"(?:top up|topping up|add money|adding money|fund).{0,35}(?:cash|cheque|check)")
        or word(r"pay(?:ing)? cash (?:in|into)|physical money|paper money")
    )
    topup = word(
        r"top up|topping up|topped up|recharg(?:e|ed|ing)|reload(?:ed|ing)?"
        r"|(?:add|adding|added|load|loading|loaded) (?:some |more |extra |my |the )?"
        r"(?:money|funds|cash|balance)"
        r"|fund(?:ing|ed)? (?:my |the |an? |this )?(?:account|card)"
        r"|card deposit"
    )
    transfer = word(
        r"transfers?|transferr(?:ed|ing)|wire(?:d)?|remittance"
        r"|(?:send|sent|sending) (?:some |my |the |a |this )?(?:money|funds|payment)"
        r"|outgoing transaction|bank payment"
    )
    bank = word(r"bank|banking|wire|swift|sepa|iban|bacs|ach")
    payment = word(
        r"payments?|purchases?|merchant|shop|store|shopping|bought|buying|paid"
        r"|pay(?:ing)?|transactions?|pos|checkout|check out|retailer|restaurant"
    )
    direct_debit = word(r"direct debits?|directdebit")
    refund = word(r"refund(?:ed|s|ing)?|chargebacks?|charge backs?")
    exchange = word(
        r"exchang(?:e|ed|ing)|conver(?:t|ted|ting|sion)|foreign currency"
        r"|currency rate|fx|interbank"
    )
    rate = word(r"rates?|conversion|converted|exchange|fx|interbank")
    currency = word(
        r"currenc(?:y|ies)|usd|eur|gbp|dollars?|euros?|pounds?|yen|rupees?|francs?"
        r"|zloty|aud|cad|chf|ron|pln|inr|zar|sgd|hkd|jpy|dirhams?|kron[ae]"
    )
    failure = word(
        r"fail(?:ed|ing|ure|s)?|unsuccessful|error|problem|trouble|broken|malfunction"
        r"|not (?:working|work|going through|successful|functioning|accepted|accepting)"
        r"|does not work|will not work|stopped working|no longer works"
        r"|cannot|could not|unable|will not let|does not let|not able"
    )
    declined = word(r"declin(?:e|ed|ing)|reject(?:ed|ing)?|refus(?:e|ed|ing)|denied|not accepted")
    pending = word(
        r"pending|processing|in progress|on hold|held|reserved|uncompleted|unsettled"
        r"|stuck|not (?:complete|completed|cleared|settled|processed)"
        r"|has not (?:completed|cleared|settled)|awaiting|being processed"
    )
    missing = word(
        r"missing|not (?:arrived|received|credited|showing|shown|there|appeared|visible"
        r"|in|reflecting|updated|arriving|reached|gone through)"
        r"|never (?:arrived|received|got|appeared|came)"
        r"|have not (?:received|got)|has not (?:arrived|reached|received|shown|appeared)"
        r"|did not (?:arrive|receive|get|come)|does not (?:show|appear)"
        r"|cannot (?:see|find)|still waiting|waiting for|disappeared"
        r"|where is|where are|not yet|has not come|have not come|yet to (?:arrive|receive)"
    )
    delay = word(
        r"delay(?:ed|s)?|overdue|late|taking (?:so |too )?long"
        r"|takes (?:so |too )?long|longer than|ages|several days|few days"
        r"|days ago|weeks ago|last week|last month|still waiting"
    ) or has(r"\b(?:been|for|over)\s+(?:\d+|two|three|four|five|six|seven|many)\s+(?:days|weeks)\b")
    fee = word(r"fees?|charges|surcharges?|commissions?|markup|mark up|costs?|pricing") or has(
        r"\b(?:extra|additional|unexpected|hidden|unnecessary|excessive)\b.{0,25}\b(?:charge|charged|pay|paid|money|amount)\b"
        r"|\bcharged\b.{0,35}\b(?:extra|more|fee|commission|for|when|on|to)\b"
        r"|\b(?:why|will|would|was|am|are|do)\b.{0,30}\b(?:charged|charge me)\b"
        r"|\b(?:pay|paid|paying)\b.{0,20}\b(?:extra|more|fee)\b"
    )
    free_question = word(r"free|without (?:a )?(?:fee|charge)|no (?:fee|charge)|charge free")
    unknown = word(
        r"unrecognised|unidentified|unknown|unauthorised|fraudulent|suspicious|unfamiliar"
        r"|do not recognise|do not remember|do not recall|not recognise"
        r"|did not (?:make|authorise|approve|buy|purchase|pay|withdraw|use)"
        r"|have not (?:made|authorised|bought|used|withdrawn)"
        r"|never (?:made|authorised|bought|paid|used|withdrew)"
        r"|not (?:my|mine|me)|without (?:my )?(?:permission|consent|approval|knowledge)"
        r"|was not me|was not made by me|someone else"
    ) or has(
        r"\b(?:no idea|do not know)\b.{0,40}\b(?:payment|transaction|charge|merchant|withdrawal)\b"
        r"|\b(?:payment|transaction|charge)\b.{0,35}\b(?:no idea|do not know|do not recognise)\b"
    )
    reverted = word(
        r"revert(?:ed|ing)?|revers(?:e|ed|al)|bounc(?:e|ed)|returned|sent back"
        r"|went back|came back|credited back|back to (?:my|the) (?:card|bank|account)"
        r"|refunded automatically|automatically refunded"
    )
    wrong_rate = rate and (
        word(
            r"wrong|incorrect|inaccurate|bad|poor|unfair|unfavourable|unfavorable"
            r"|different|unexpected|awful|terrible|overcharged|overcharging|worse"
            r"|not right|not correct|too high|too low|higher|lower|discrepancy"
        )
        or has(r"\b(?:not|does not)\b.{0,15}\b(?:match|expected|expect|advertised)\b")
    )
    balance_issue = word(r"balance|credited|crediting|account total") and (
        missing or delay or word(r"unchanged|not updated|same|update|updated")
        or has(r"\b(?:not|has not|did not|does not)\b.{0,15}\b(?:change|increase|reflect)\b")
    )
    recipient = word(r"recipient|beneficiary|receiver|payee")
    outgoing = word(
        r"outgoing|recipient|beneficiary|payee|to (?:my |a |the )?(?:friend|mother|father|wife|husband|partner|brother|sister|landlord)"
        r"|to someone|to another person|to my other (?:bank|account)"
        r"|from (?:my )?revolut|out of (?:my |the )?(?:revolut )?account"
        r"|to an external account"
    )
    incoming = word(
        r"incoming|into (?:my |the |this |a |an )?(?:revolut )?account"
        r"|to (?:my |the )?revolut(?: account)?"
        r"|from (?:my |another |a |an |the )?(?:external |other )?bank"
        r"|receiv(?:e|ed|ing) (?:a |an |the |my )?(?:bank |international )?(?:transfer|wire)"
        r"|bank deposit|account deposit"
    )
    if has(r"\b(?:transfer|transferred|send|sent|sending|wire)\b.{0,55}\bto my account\b"):
        incoming = True
    if outgoing and not word(r"incoming|into (?:my )?revolut|to (?:my )?revolut"):
        incoming = False
    bank_funding = (
        (transfer and incoming)
        or topup and bank and not word(r"(?:debit|credit|bank) card")
        or word(r"(?:top up|topping up|topped up).{0,30}(?:bank transfer|wire)")
    )
    timing = word(
        r"how long|how soon|how quickly|how fast|when|delivery time|time frame|timeframe"
        r"|business days|working days|weekends?|duration|instant|immediately"
    ) or has(r"\b(?:time|days|hours)\b.{0,25}\b(?:take|takes|needed|receive|arrive)\b")

    # Security, account access, and personal information.
    phone = word(r"phone|mobile|cellphone|smartphone|handset|device")
    loss = word(r"lost|stolen|misplaced|robbed|theft|stole|missing|cannot find|left behind")
    if phone and loss:
        offer("lost_or_stolen_phone", 137)
    if has(r"\b(?:lost|stolen|misplaced|robbed|stole)\b.{0,35}\b(?:wallet|purse)\b"):
        offer("lost_or_stolen_card", 137)
    if card and loss and not (
        word(r"delivery|delivered|ordered|shipment|post|mail|arrive|arrived")
        and not word(r"stolen|stole|misplaced|robbed")
    ):
        offer("lost_or_stolen_card", 132)
    if has(r"\b(?:left|forgot)\b.{0,30}\b(?:card|wallet|purse)\b.{0,30}\b(?:shop|store|taxi|train|bus|restaurant|somewhere)\b"):
        offer("lost_or_stolen_card", 137)

    compromised = word(r"compromised|cloned|skimmed|phishing|scammer") or has(
        r"\b(?:card|payment)\s+(?:details|information|number|credentials)\b.{0,55}\b(?:stolen|copied|leaked|exposed|hacked|someone|wrong hands)\b"
        r"|\b(?:someone|somebody|fraudster|scammer|thief)\b.{0,55}\b(?:card details|card number|card information|cvv)\b"
        r"|\b(?:stole|stolen|copied|shared|revealed|gave|give)\b.{0,35}\b(?:card details|card number|card information|cvv)\b"
    )
    if compromised:
        offer("compromised_card", 147)
    elif word(r"hacked|hack|fraud|fraudster|scam") and card and not unknown:
        offer("compromised_card", 111)
    if card and word(r"freeze|block|secure|protect") and unknown:
        offer("compromised_card", 123)

    pin = word(r"pin|personal identification number")
    passcode = word(r"passcode|password|pass code|login code|log in code|access code|security code")
    login = word(r"log in|login|log on|sign in|signin|access (?:my|the) account|access (?:my|the) app")
    forgot = word(r"forgot|forgotten|forget|cannot remember|do not remember|lost|reset|recover|retrieve")
    if passcode:
        offer("passcode_forgotten", 88)
        if forgot or failure or word(r"locked out|change"):
            offer("passcode_forgotten", 128)
    if login and (forgot or word(r"locked out")):
        offer("passcode_forgotten", 125)
    if pin:
        offer("change_pin", 70)
        if word(r"blocked|unblock|locked|unlock|tries|attempts|attempt|incorrectly|exceeded") or has(
            r"\b(?:wrong|incorrect)\b.{0,20}\b(?:three|3|many|times|repeatedly)\b"
            r"|\b(?:three|3|many)\b.{0,20}\b(?:wrong|incorrect)\b"
        ):
            offer("pin_blocked", 143)
        elif login or word(r"app pin|application pin"):
            offer("passcode_forgotten", 123 if forgot else 94)
        elif word(r"change|reset|find|view|see|show|reveal|retrieve|new|set|forgot|forgotten|remember"):
            offer("change_pin", 119)

    if word(r"personal details|personal information|profile details|contact details"):
        offer("edit_personal_details", 104)
    if word(r"change|update|edit|correct|amend|modify|new|wrong|incorrect") and word(
        r"address|email|e mail|phone number|mobile number|telephone number|surname"
        r"|last name|first name|name|date of birth|birth date|birthday|dob"
    ):
        offer("edit_personal_details", 126)
    if has(r"\b(?:moved house|got married|changed my name|changed my number)\b"):
        offer("edit_personal_details", 123)

    if has(
        r"\b(?:close|closing|terminate|termination|delete|deactivate|cancel|shut down|remove)\b"
        r".{0,35}\b(?:account|membership|profile)\b"
        r"|\baccount\b.{0,25}\b(?:closure|termination|deletion)\b"
    ):
        offer("terminate_account", 137)
    if word(r"no longer want|stop using|leave revolut|quit revolut") and not word(r"card|top up|automatic"):
        offer("terminate_account", 110)

    age = word(r"age|underage|under age|minor|teenager|teenagers|teen|child|children|kid|kids")
    if age and word(r"limit|old|young|minimum|maximum|account|card|open|join|register|sign up|allowed|eligible"):
        offer("age_limit", 125)
    if has(
        r"\b(?:under|over|at least|aged?|turned|turning)\s+(?:\d{1,2}|eighteen|sixteen|seventeen|thirteen)\b"
        r"|\b\d{1,2}\s+years? old\b"
        r"|\bhow old\b"
    ):
        offer("age_limit", 132)
    if word(r"son|daughter") and word(r"open|create|register|sign up|account|young"):
        offer("age_limit", 119)

    source_funds = word(
        r"source of (?:funds|money|income|wealth)|sources of funds|origin of (?:funds|money)"
        r"|proof of (?:income|earnings|funds|salary|wealth)|prove (?:my )?(?:income|earnings)"
        r"|payslips?|pay slips?"
    ) or has(
        r"\b(?:verify|verification|prove|proof|evidence|document)\b.{0,60}\b(?:where|source|origin).{0,30}\b(?:money|funds|income)\b"
        r"|\bwhere\b.{0,25}\b(?:money|funds)\b.{0,25}\b(?:came|comes|come) from\b"
    )
    if source_funds:
        offer("verify_source_of_funds", 147)

    verify = word(r"verify|verified|verifying|verification|validate|validation|authenticate|authentication")
    identity = word(r"identity|identification|passport|selfie|id|driving licence|driving license|identity documents")
    if identity or verify and word(r"account|documents|photo"):
        offer("verify_my_identity", 89)
        if word(r"how|documents|required|upload|submit|send|photo|selfie|passport"):
            offer("verify_my_identity", 108)
        if failure or declined or word(r"not verified|unverified") or (
            pending or delay
        ) and (verify or identity):
            offer("unable_to_verify_identity", 134)
        if has(
            r"\b(?:why|reason|purpose|necessary|mandatory|compulsory)\b.{0,65}\b(?:verify|verification|id|identity|passport|identification|document|photo)\b"
            r"|\b(?:without|avoid|skip)\b.{0,35}\b(?:verifying|verification|identity|id|passport)\b"
            r"|\b(?:have to|need to|required to)\b.{0,25}\b(?:verify|provide|prove|submit)\b"
        ):
            offer("why_verify_identity", 120)
        if has(r"\bwhy\b.{0,30}\b(?:fail|failed|failing|rejected|declined|not working|cannot)\b"):
            offer("unable_to_verify_identity", 141)

    # Card form factors, wallets, activation, and delivery.
    wallet_pay = word(r"apple pay|google pay|android pay|google wallet|apple wallet|apple watch|samsung pay")
    if wallet_pay:
        offer("apple_pay_or_google_pay", 133)
    if word(r"contactless|tap to pay|tap and pay|tap and go|paywave|paypass|nfc") or has(
        r"\b(?:tap|tapping|wave|waving)\b.{0,25}\b(?:card|reader|terminal|pay)\b"
        r"|\bcard\b.{0,20}\b(?:tap|tapping)\b"
    ):
        offer("contactless_not_working", 132)
        if failure or declined:
            offer("contactless_not_working", 142)

    if card and word(r"activate|activation|activating|activated|enable") and not word(r"contactless|nfc"):
        offer("activate_my_card", 126)
    if word(r"card activation|activate my new card|activate the new card"):
        offer("activate_my_card", 138)

    if word(r"expir(?:e|es|ed|ing|y|ation)|renew|renewal|valid until|valid thru|valid through") and (
        card or not word(r"passport|id|identification|transfer|verification|session")
    ):
        offer("card_about_to_expire", 134)

    swallowed = word(r"swallowed|ate my card|eaten|retained|captured") or has(
        r"\batm\b.{0,45}\b(?:kept|took|stuck|trapped|holding|held|will not return|did not return|will not give|did not give)\b.{0,25}\bcard\b"
        r"|\bcard\b.{0,40}\b(?:stuck|trapped|left|inside|retained)\b.{0,25}\batm\b"
        r"|\batm\b.{0,30}\bcard\b.{0,25}\b(?:back|stuck|inside)\b"
        r"|\bcard\b.{0,30}\b(?:will not|did not|does not)\b.{0,15}\bcome out\b"
    )
    if swallowed and (card or cash):
        offer("card_swallowed", 151)

    linking = word(r"link|linking|linked|unlink|unlinked|connect|connecting|attach|associate|associated")
    if card and linking:
        offer("card_linking", 108)
        if word(r"another account|different account|two accounts|old account|new account|existing card|revolut card"):
            offer("card_linking", 133)
        elif word(r"account|app") and not topup and not wallet_pay:
            offer("card_linking", 123)

    if disposable:
        offer("get_disposable_virtual_card", 103)
        disposable_limit = word(
            r"limits?|maximum|minimum|how many|how much|restrictions?|restricted"
            r"|more than once|multiple times|twice|again|reuse|re use|subscriptions?"
            r"|recurring|where can|where to|which (?:shops|merchants|sites)"
            r"|what (?:can|cannot)|allowed|per day|per month"
        )
        if disposable_limit:
            offer("disposable_card_limits", 139)
        elif word(r"get|create|generate|order|obtain|issue|request|find|what is|how does"):
            offer("get_disposable_virtual_card", 127)
        if failure or declined:
            if word(r"payment|pay|purchase|work|working|accepted") and not word(r"create|order|get|generate"):
                offer("virtual_card_not_working", 129)
    elif virtual:
        offer("getting_virtual_card", 86)
        if failure or declined:
            if word(r"work|working|pay|payment|purchase|transaction|accepted|invalid|checkout"):
                offer("virtual_card_not_working", 137)
            elif word(r"get|create|order|find|issue|access"):
                offer("getting_virtual_card", 122)
        if word(r"get|order|create|obtain|issue|request|find|locate|details|what is"):
            offer("getting_virtual_card", 110)

    spare = card and word(
        r"spare|backup|back up|additional|extra|second|another|two|multiple"
        r"|more than one|2 cards|third"
    )
    if spare and not word(r"another account|another bank|another country|second time"):
        offer("getting_spare_card", 114)
        if word(r"spare|backup|back up|second card|additional card|extra card|more than one card"):
            offer("getting_spare_card", 127)

    delivery = card and word(
        r"arriv(?:e|ed|ing|al)|deliver(?:y|ed|ing)?|shipment|shipping|shipped"
        r"|post|posted|mail|mailed|courier|tracking|track|dispatch|dispatched"
        r"|receive|received|receiving"
    )
    ordered = word(r"ordered|placed an order|card order|order status")
    if delivery:
        offer("card_delivery_estimate", 76)
        if timing or word(r"estimate|estimated|express|standard|shipping time"):
            offer("card_delivery_estimate", 110)
        if missing or delay or ordered or word(r"track|tracking|status|lost in (?:the )?post"):
            offer("card_arrival", 125)
        if word(r"not arrived|has not arrived|never arrived|not received|have not received|not delivered|did not receive|overdue"):
            offer("card_arrival", 140)
        if word(r"express|expedited|rush|speed up|faster delivery") and not missing:
            offer("card_delivery_estimate", 125)
    if card and ordered:
        offer("card_arrival", 94)
        if missing or delay or word(r"status|track|where"):
            offer("card_arrival", 132)
    if card and has(r"\bhow long\b.{0,50}\b(?:get|receive|arrive|take|delivery)\b"):
        offer("card_delivery_estimate", 111)
    if card and has(r"\b(?:where is|where has)\b.{0,25}\b(?:card|order)\b"):
        offer("card_arrival", 126)

    physical = word(r"physical|plastic|real card|actual card|tangible card|non virtual")
    ordering = word(r"order|ordering|request|apply for|application for")
    acquiring = word(r"get|obtain|have|receive|need|want|send|issue|issued")
    if card and (physical or ordering):
        if ordering:
            offer("order_physical_card", 97)
            if not virtual and not disposable:
                offer("order_physical_card", 109)
        if physical and acquiring:
            offer("get_physical_card", 103)
        if physical and ordering:
            offer("order_physical_card", 117)
        if fee and not payment and not virtual:
            offer("order_physical_card", 119)
    if card and not virtual and not disposable:
        if has(r"\b(?:how|where)\b.{0,25}\b(?:get|obtain|request|apply for)\b.{0,20}\b(?:a |my |the |new )?card\b"):
            offer("get_physical_card", 93)
        if has(r"\b(?:cost|fee|charge|price)\b.{0,40}\b(?:new|physical|plastic|order|delivery)\b"):
            offer("order_physical_card", 116)
        if has(r"\b(?:new|physical|plastic)\s+card\b.{0,30}\b(?:cost|price|free)\b"):
            offer("order_physical_card", 116)

    if word(r"visa|mastercard"):
        if not topup and not word(r"american express|amex|prepaid"):
            offer("visa_or_mastercard", 85)
            if word(r"or|instead|choose|choice|prefer|switch|change|issue|issued|receive|type|brand"):
                offer("visa_or_mastercard", 123)
    if card and word(r"type|brand|scheme") and word(r"issue|issued|get|receive|provide"):
        offer("visa_or_mastercard", 98)

    # Deposit and top-up mechanisms.
    automatic = word(r"automatic|automatically|auto|recurring|scheduled|schedule|regular|repeat")
    if topup and automatic:
        offer("automatic_top_up", 139)
    if word(r"auto top up|automatic top up|auto recharge"):
        offer("automatic_top_up", 150)
    if has(r"\b(?:balance|funds)\b.{0,35}\b(?:below|low|threshold|runs out)\b") and word(
        r"top up|add|automatic|automatically|replenish|refill"
    ):
        offer("automatic_top_up", 132)

    if cash_deposit:
        offer("top_up_by_cash_or_cheque", 117)
        if missing or balance_issue or delay or word(r"cleared|clearance|credited"):
            offer("balance_not_updated_after_cheque_or_cash_deposit", 138)
        if timing and word(r"deposited|paid in|cashed|banked"):
            offer("balance_not_updated_after_cheque_or_cash_deposit", 140)
    elif cheque and not word(r"identity|verify|checked|check my"):
        offer("top_up_by_cash_or_cheque", 82)

    if topup:
        offer("topping_up_by_card", 66)
        if word(r"card|debit|credit"):
            offer("topping_up_by_card", 86)
        if failure or declined:
            offer("top_up_failed", 127)
        if pending:
            offer("pending_top_up", 126)
        if (missing or delay) and not bank_funding and not cash_deposit:
            offer("pending_top_up", 116)
        if reverted or word(r"cancelled|disappeared"):
            offer("top_up_reverted", 136)
        if has(r"\b(?:appeared|added|credited|completed)\b.{0,45}\b(?:disappeared|gone|removed)\b"):
            offer("top_up_reverted", 142)
        limits = word(r"limits?|maximum|minimum|cap|capped|allowance|how much|how many") and not (
            fee or word(r"cost|price")
        )
        if limits or word(r"increase.{0,20}limit|limit.{0,20}increase"):
            offer("top_up_limits", 125)
        if has(r"\b(?:too much|too little|smallest|largest)\b.{0,30}\b(?:top up|add|amount)\b"):
            offer("top_up_limits", 124)
        if fee or free_question:
            offer("top_up_by_bank_transfer_charge" if bank_funding else "top_up_by_card_charge", 128)
        if verify or word(r"verification code|authentication code|security check|4 digit|four digit"):
            offer("verify_top_up", 145)
        supported_method = word(
            r"which|what (?:type|kind|cards|currenc)|supported|support|accept|accepted"
            r"|compatible|american express|amex|maestro|diners|discover|prepaid"
            r"|foreign|issued abroad|overseas|international card"
        )
        if supported_method and not (failure or declined):
            offer("supported_cards_and_currencies", 116)
        if currency and not (fee or failure or pending or reverted or bank_funding):
            if word(r"can|possible|support|allowed|which|what|different|foreign|another"):
                offer("supported_cards_and_currencies", 121)
        if word(r"someone else|someone elses|husband|wife|partner|friend|another person") and not unknown:
            offer("topping_up_by_card", 114)

    if verify and card and not identity and not wallet_pay:
        offer("verify_top_up", 118)
    if word(r"4 digit|four digit") and word(r"statement|top up|verification|verify|code"):
        offer("verify_top_up", 141)
    if word(r"card verification|verify my top up|verify the top up"):
        offer("verify_top_up", 143)

    if word(r"american express|amex|maestro|diners|discover|prepaid card") and not cash:
        offer("supported_cards_and_currencies", 85)
        if word(r"support|accept|allowed|use|eligible|compatible"):
            offer("supported_cards_and_currencies", 108)
    if has(r"\b(?:which|what)\b.{0,20}\b(?:cards|card types|types of card)\b.{0,35}\b(?:support|accept|use|top up)\b"):
        offer("supported_cards_and_currencies", 116)

    # Transfers: direction, status, timing, cancellation, and fees.
    beneficiary_blocked = recipient and word(
        r"not allowed|not permitted|prohibited|forbidden|blocked|restricted|not supported|unsupported"
    )
    if beneficiary_blocked:
        offer("beneficiary_not_allowed", 148)
    if recipient and failure and word(r"add|create|register|set up"):
        offer("beneficiary_not_allowed", 127)
    if has(r"\b(?:cannot|not allowed|not permitted)\b.{0,35}\b(?:transfer|send)\b.{0,30}\b(?:this|that|certain|particular)\b.{0,20}\b(?:recipient|beneficiary|person|account)\b"):
        offer("beneficiary_not_allowed", 129)

    cancel = word(r"cancel|cancelling|stop|recall|undo|reverse|revoke|recover|withdraw")
    if transfer:
        offer("pending_transfer", 45)
        if bank_funding:
            offer("transfer_into_account", 78)
        elif outgoing:
            offer("pending_transfer", 71)
        if timing and not pending:
            offer("transfer_timing", 109)
        if pending or delay:
            offer("pending_transfer", 120)
        if declined:
            offer("declined_transfer", 135)
        elif failure:
            offer("failed_transfer", 122)
        if reverted:
            offer("failed_transfer", 132)
        if fee or free_question:
            offer("top_up_by_bank_transfer_charge" if bank_funding else "transfer_fee_charged", 128)

        if cancel and not cash:
            # Past-tense reversal describes a failed transfer; wanting to reverse it
            # describes cancellation.
            if not word(r"reversed|reverted|returned|cancelled") or word(r"can|how|want|need|please"):
                offer("cancel_transfer", 141)
        if word(r"wrong|incorrect|mistake|accidentally") and word(
            r"recipient|beneficiary|account number|bank details|person|account|iban|amount"
        ):
            offer("cancel_transfer", 130)

        if balance_issue and not outgoing:
            offer("balance_not_updated_after_bank_transfer", 135)
        if incoming and (missing or delay) and not cash_deposit:
            offer("balance_not_updated_after_bank_transfer", 131)
        recipient_missing = (
            recipient and missing
            or outgoing and missing
            or has(
                r"\b(?:sent|transferred)\b.{0,60}\b(?:has not|have not|did not|not|never)\b"
                r".{0,20}\b(?:arrive|arrived|receive|received|reach|reached|get|got)\b"
            ) and not incoming
        )
        if recipient_missing:
            offer("transfer_not_received_by_recipient", 137)
        if word(r"completed|complete|successful|finished") and missing and not incoming:
            offer("transfer_not_received_by_recipient", 143)
        if word(r"outgoing transaction") and not (fee or failure or declined or unknown):
            offer("pending_transfer", 114)

    if balance_issue and bank and not topup and not cash_deposit:
        offer("balance_not_updated_after_bank_transfer", 127)
    if bank_funding and (missing or balance_issue) and not cash_deposit:
        offer("balance_not_updated_after_bank_transfer", 132)

    bank_details = word(
        r"iban|swift|bic|sort code|routing number|bank details|account number"
        r"|transfer reference|bank transfer reference|reference number"
    )
    if bank_details and not (cancel and transfer):
        offer("transfer_into_account", 97)
        if word(r"find|where|what|how|use|need|receive|receiving|incoming"):
            offer("transfer_into_account", 112)
    if has(r"\b(?:top up|fund|add money|put money|deposit)\b.{0,45}\b(?:bank transfer|wire transfer|another bank|bank account)\b"):
        offer("transfer_into_account", 103)
    if incoming and not (missing or pending or fee or failure or declined):
        offer("transfer_into_account", 91)

    salary = word(r"salary|salaries|wages|payroll|employer|paycheck|pay cheque")
    receive_money = has(
        r"\b(?:receive|receiving|accept)\b.{0,25}\b(?:money|funds|payments?|salary|wages)\b"
        r"|\b(?:someone|somebody|friend|friends|family|people|employer)\b.{0,40}\b(?:send|pay|transfer)\b.{0,20}\b(?:me|my account)\b"
        r"|\b(?:send|pay)\s+me\b"
        r"|\bget paid\b"
        r"|\b(?:details|information)\b.{0,30}\b(?:give|share)\b.{0,35}\b(?:someone|friend|person|employer)\b"
    )
    if salary or receive_money:
        offer("receiving_money", 108)
        if salary and (missing or delay):
            offer("balance_not_updated_after_bank_transfer", 125)
        if fee and (bank or transfer or word(r"receive|receiving|incoming")):
            offer("top_up_by_bank_transfer_charge", 130)
        if transfer and timing and not missing:
            offer("transfer_timing", 117)

    if has(r"\b(?:how long|how quickly|how fast|how many days)\b.{0,65}\b(?:send money|sending money|receive money|receiving money|bank payment)\b"):
        offer("transfer_timing", 112)

    # Refunds, duplicate charges, and unfamiliar transactions.
    if refund:
        offer("request_refund", 91)
        if missing or delay or pending or timing or word(r"refunded|processed|issued|promised|waiting"):
            offer("refund_not_showing_up", 132)
        if word(r"request|claim|chargeback|charge back|dispute") or has(
            r"\b(?:how|can)\b.{0,25}\b(?:get|obtain|request|claim|ask for)\b.{0,20}\brefund\b"
        ):
            offer("request_refund", 128)
        if word(r"refuse|refused|refuses|refusing|will not refund|does not want to refund"):
            offer("request_refund", 136)
    elif has(
        r"\b(?:get|want|claim|request|need)\b.{0,25}\b(?:my |the )?money back\b"
        r"|\bdispute\b.{0,30}\b(?:payment|purchase|transaction|charge)\b"
        r"|\b(?:cancel|reverse)\b.{0,25}\b(?:card payment|purchase)\b"
    ):
        offer("request_refund", 121)

    duplicate = word(
        r"charged twice|charged double|double charged|double charge|duplicate payment"
        r"|duplicate transaction|duplicated payment|duplicated transaction"
        r"|debited twice|paid twice|billed twice|taken twice|deducted twice"
        r"|two identical|same transaction twice|same payment twice|same purchase twice"
    ) or has(
        r"\b(?:charge|charged|payment|purchase|transaction|debit|deducted|taken)\b.{0,40}\b(?:twice|two times|2 times|duplicat(?:e|ed)|two charges|two payments)\b"
        r"|\b(?:twice|duplicate|duplicated|double)\b.{0,25}\b(?:charge|charged|payment|transaction|debited)\b"
        r"|\b(?:paid|purchased|bought)\b.{0,20}\bonce\b.{0,35}\b(?:two|twice|double)\b"
    )
    if duplicate:
        offer("transaction_charged_twice", 150)

    small_charge = has(
        r"(?:[£$€]\s*(?:0[.,]\d+|1(?:[.,]0{1,2})?)(?!\d)"
        r"|\b(?:one|1)\s+(?:pound|euro|dollar|gbp|eur|usd)s?\b"
        r"|\b(?:pound|euro|dollar)\b.{0,12}\bcharge\b"
        r"|\b(?:small|tiny|little|test|verification|authorisation|authorization)\s+(?:extra\s+)?(?:charge|payment|transaction|amount)\b)"
    )
    if small_charge and word(r"charge|charged|transaction|statement|payment|extra|deducted|taken"):
        offer("extra_charge_on_statement", 139)
        if verify and topup and word(r"code"):
            offer("verify_top_up", 154)
    elif word(r"extra|additional|unexpected") and word(r"statement") and not (
        cash or transfer or topup or exchange
    ):
        offer("extra_charge_on_statement", 110)

    if direct_debit:
        offer("direct_debit_payment_not_recognised", 101)
        if unknown or word(r"what|why|cancel|unauthorised"):
            offer("direct_debit_payment_not_recognised", 145)
    if unknown:
        if cash and not cash_deposit:
            offer("cash_withdrawal_not_recognised", 140)
        elif not direct_debit and (payment or card or word(r"charge|charged|statement|deducted|taken")):
            offer("card_payment_not_recognised", 133)
    if has(r"\b(?:what is|what was|where did)\b.{0,35}\b(?:this|that)\s+(?:payment|transaction|charge)\b"):
        offer("card_payment_not_recognised", 112)

    # ATM withdrawals and their amount, rate, and status.
    if cash and not cash_deposit:
        offer("atm_support", 57)
        if word(r"where|which|any|locations?|nearest|network|support|supported|accept|allowed"):
            offer("atm_support", 107)
        if word(r"withdraw|withdrawal|withdrawals|take cash out|withdrew") and word(
            r"abroad|overseas|foreign|country|countries|international"
        ):
            offer("atm_support", 99)
        if fee or free_question:
            offer("cash_withdrawal_charge", 130)
        if pending:
            offer("pending_cash_withdrawal", 135)
        if declined or failure:
            offer("declined_cash_withdrawal", 127)
        if wrong_rate:
            offer("wrong_exchange_rate_for_cash_withdrawal", 146)
        elif rate and exchange and word(r"used|applied|got|given|withdrawal|withdrew"):
            offer("wrong_exchange_rate_for_cash_withdrawal", 115)

        wrong_cash = has(
            r"\b(?:wrong|incorrect|different|less|more|short|partial|incomplete)\b.{0,25}\b(?:amount|cash|money)\b"
            r"|\b(?:cash|money|amount)\b.{0,25}\b(?:wrong|incorrect|less|short|different)\b"
            r"|\b(?:only|just)\b.{0,12}\b(?:received|got|dispensed|gave)\b"
            r"|\b(?:received|got|dispensed|gave)\b.{0,12}\b(?:only|less|part|half)\b"
            r"|\b(?:no|not any)\s+(?:cash|money)\b"
            r"|\b(?:did not|does not|has not)\b.{0,15}\b(?:dispense|dispensed|give|gave)\b"
        )
        debited = word(r"debited|deducted|charged|taken|balance decreased|money left|money went")
        if wrong_cash and (
            debited or word(r"wrong amount|incorrect amount|less|short|partial|half|only|different amount")
        ):
            offer("wrong_amount_of_cash_received", 143)
        if debited and has(
            r"\b(?:no cash|no money|not receive|not get|nothing came out|nothing dispensed"
            r"|did not dispense|did not give|empty handed)\b"
        ):
            offer("wrong_amount_of_cash_received", 151)
        if has(
            r"\b(?:withdrew|withdraw|requested|asked for)\b.{0,25}\b\d+\b"
            r".{0,45}\b(?:got|received|gave|dispensed|only)\b.{0,15}\b\d+\b"
        ):
            offer("wrong_amount_of_cash_received", 143)

    # Card payments: failures, reversals, fees, exchange rates, and pending holds.
    ordinary_payment = not (topup or cash or transfer or cash_deposit or direct_debit)
    if payment or card:
        if ordinary_payment:
            if declined:
                offer("declined_card_payment", 128)
            if failure and payment and word(r"pay|payment|purchase|transaction|checkout|merchant"):
                offer("declined_card_payment", 113)
            if pending:
                offer("pending_card_payment", 129)
            if reverted:
                offer("reverted_card_payment", 134)
            if fee:
                offer("card_payment_fee_charged", 112)
            if wrong_rate:
                offer("card_payment_wrong_exchange_rate", 141)
        elif wrong_rate and payment and not (cash or topup or transfer):
            offer("card_payment_wrong_exchange_rate", 141)

    if card and not (virtual or disposable or topup or cash or transfer):
        if failure:
            offer("card_not_working", 103)
        if word(r"broken|damaged|bent|cracked|scratched|chip|magnetic strip|magnetic stripe"):
            if failure or word(r"damaged|broken|bent|cracked|scratched"):
                offer("card_not_working", 128)
        if has(r"\bcard\b.{0,30}\b(?:not working|does not work|stopped working|will not work|no longer works)\b"):
            offer("card_not_working", 124)
        if word(r"blocked|locked|disabled") and not pin:
            offer("card_not_working", 101)

    if word(r"payment|purchase|transaction") and not (cash or transfer or topup):
        if has(r"\b(?:money|funds)\b.{0,25}\b(?:came back|returned|back in|back to)\b"):
            offer("reverted_card_payment", 125)
        if word(r"preauthorisation|preauthorised|preauthorization|preauthorized|authorisation hold|authorization hold"):
            offer("pending_card_payment", 129)
        if has(r"\b(?:how long|when)\b.{0,40}\b(?:complete|completed|clear|cleared|settle|settled)\b"):
            offer("pending_card_payment", 120)

    # Currency exchange, supported currencies, and geographical availability.
    if exchange:
        offer("exchange_via_app", 64)
        if word(r"how|where|can|want|convert|buy|sell|change|exchange") and not (
            cash or topup or transfer or payment and wrong_rate
        ):
            offer("exchange_via_app", 99)
        if word(r"rate|rates|interbank|midmarket|mid market|live rate"):
            offer("exchange_rate", 111)
        if fee or free_question or word(r"markup|mark up|commission|weekend charge"):
            offer("exchange_charge", 123)
        if wrong_rate and not (cash or payment or topup):
            offer("exchange_rate", 117)
    elif currency and word(r"convert|exchange|switch|change|buy|sell"):
        offer("exchange_via_app", 99)
    if word(r"exchange rate|exchange rates|conversion rate|conversion rates|interbank rate"):
        offer("exchange_rate", 108)

    supported_currency = currency and word(
        r"support|supported|available|hold|holding|keep|store|balance|balances"
        r"|which|what|multiple|several|different|base currency|currency account"
    )
    if supported_currency and not topup:
        offer("fiat_currency_support", 104)
        if word(r"hold|holding|keep|store|multiple currencies|base currency|currency account"):
            offer("fiat_currency_support", 118)
    if word(r"fiat|supported currencies") and not topup:
        offer("fiat_currency_support", 119)

    geography = word(
        r"countries|country|resident|residents|residency|reside|living|live in|based in"
        r"|nationality|citizen|citizens|territories|regions|available in"
        r"|united states|united kingdom|usa|canada|australia|india|europe|america"
        r"|germany|france|spain|italy|brazil|japan|china|singapore|switzerland"
    )
    if geography and word(r"open|register|registration|sign up|signup|join|eligible|eligibility|account|available|support"):
        if not (topup or transfer or cash):
            offer("country_support", 116)
    if has(
        r"\b(?:which|what)\s+(?:countries|regions|territories)\b.{0,35}\b(?:support|available|operate|register)\b"
        r"|\b(?:live|living|resident|based)\s+in\b.{0,40}\b(?:can|account|register|sign up|join)\b"
        r"|\b(?:available|offered|supported)\b.{0,30}\b(?:country|countries|residents)\b"
    ):
        offer("country_support", 126)

    acceptance = card and (
        word(r"where|accepted|accept|use|using|work|pay|spend")
        and word(
            r"abroad|overseas|internationally|country|countries|shops|stores|merchants"
            r"|online|internet|worldwide|everywhere|anywhere|retailers|hotel"
            r"|usa|america|europe|canada|australia|japan|france|germany|spain|india"
        )
        or has(r"\bwhere\b.{0,30}\b(?:use|pay with|spend with)\b.{0,20}\bcard\b")
        or has(r"\b(?:which|what)\b.{0,25}\b(?:shops|stores|merchants|websites)\b")
    )
    if acceptance and not (cash or topup):
        offer("card_acceptance", 110)
        if not (failure or declined) and word(r"where|can|will|do|does|accepted|accept"):
            offer("card_acceptance", 117)

    # Useful weak defaults for short or underspecified utterances.
    if word(r"cash") and not (cash or cash_deposit):
        if word(r"add|deposit|put|pay in|top up"):
            offer("top_up_by_cash_or_cheque", 84)
        elif word(r"withdraw|take out|get out|atm"):
            offer("atm_support", 72)
    if word(r"balance") and missing and not (topup or cash_deposit or refund):
        offer("balance_not_updated_after_bank_transfer", 68)
    if word(r"virtual card") and not disposable:
        offer("getting_virtual_card", 59)
    if card and not any((payment, transfer, topup, cash, virtual, disposable)):
        offer("card_not_working", 17)
    if word(r"pending") and not (transfer or topup or cash):
        offer("pending_card_payment", 79)
    if word(r"outgoing") and not (cash or topup):
        offer("pending_transfer", 82)
    if word(r"transfer") and not incoming and not outgoing:
        offer("transfer_timing", 26)
    if word(r"money") and word(r"add|adding|load|deposit|fund") and not bank:
        offer("topping_up_by_card", 45)

    similarities = _similarity_scores(t)
    best = max(
        _LABELS,
        key=lambda label: (
            scores[label] + 25.0 * similarities[label],
            scores[label],
            similarities[label],
        ),
    )
    if scores[best] == 0.0 and similarities[best] == 0.0:
        best = "pending_transfer"
    return {"answer": best}
