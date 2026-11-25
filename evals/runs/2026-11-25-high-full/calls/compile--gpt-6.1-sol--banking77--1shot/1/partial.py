import re
import math
import unicodedata
from collections import Counter

_PROTOTYPES = {
    "activate_my_card": (
        "How do I activate my new card|Activate a physical debit card|"
        "I received my card how do I start using it|Does my card need activation|"
        "Where is the activate card button|My card activation did not work"
    ),
    "age_limit": (
        "What is the minimum age to open an account|How old do you have to be|"
        "Can my child get a card|I am under eighteen can I sign up|"
        "Is there an age restriction|Account for a teenager or minor"
    ),
    "apple_pay_or_google_pay": (
        "Can I use Apple Pay|How do I add my card to Google Pay|"
        "My card will not work with Apple Wallet|Does Google wallet support this card|"
        "Set up Android Pay on my phone|Pay with my smartwatch or Apple watch|"
        "Why is my card not eligible for a mobile wallet"
    ),
    "atm_support": (
        "Which ATMs can I use|Where can I withdraw cash|"
        "Find a supported cash machine near me|What cashpoints accept my card|"
        "Can I use any ATM abroad|Which banks cash machines are supported"
    ),
    "automatic_top_up": (
        "How do I set up automatic top ups|Turn off auto top up|"
        "My automatic recharge did not happen|Change my auto top up threshold|"
        "Automatically add money when my balance is low|Schedule recurring top ups|"
        "Why is my card being topped up automatically"
    ),
    "balance_not_updated_after_bank_transfer": (
        "My bank transfer has not been added to my balance|"
        "I transferred money into my account but it is not showing|"
        "An incoming transfer has not arrived|Bank sent the money but my balance is unchanged|"
        "I sent money from my other bank and have not received it|"
        "My salary bank transfer is missing|Where is the transfer I made to my Revolut account"
    ),
    "balance_not_updated_after_cheque_or_cash_deposit": (
        "I deposited cash but my balance has not updated|"
        "My cheque deposit is not showing in my account|"
        "When will my cash deposit be credited|I paid in a check and the money is missing|"
        "The cash I deposited has not arrived|A cheque has cleared but my balance is wrong"
    ),
    "beneficiary_not_allowed": (
        "Why is my beneficiary not allowed|I cannot add this recipient|"
        "The beneficiary account is not supported|Transfer says recipient not permitted|"
        "Why can I not send money to this beneficiary|This merchant bank recipient is blocked|"
        "I am unable to set up a new payee"
    ),
    "cancel_transfer": (
        "How can I cancel a bank transfer|Stop a transfer I just sent|"
        "I sent money to the wrong account can I get it back|"
        "Recall an outgoing bank payment|Reverse a transfer|"
        "Can I change the recipient after sending a transfer"
    ),
    "card_about_to_expire": (
        "My card is about to expire|How do I renew my expiring card|"
        "My card has expired what should I do|Will you send a replacement before expiry|"
        "The expiry date on my card is next month|Can I still use an expired card"
    ),
    "card_acceptance": (
        "Where can I use my card|Can I pay with my card abroad|"
        "Is the card accepted in shops and restaurants|Can I use this card for online purchases|"
        "Which countries accept the card|Will my card work in another country|"
        "Can I use the card anywhere that accepts debit cards"
    ),
    "card_arrival": (
        "My card has not arrived|I ordered a card weeks ago and it is still missing|"
        "Track the delivery of my card|Where is the card I ordered|"
        "My card delivery is late|The card says delivered but I did not receive it|"
        "Check the shipping status of my replacement card"
    ),
    "card_delivery_estimate": (
        "How long does card delivery take|When will my new card arrive|"
        "What is the estimated delivery date for a card|"
        "How many days to receive a physical card|Do you offer express card delivery|"
        "How quickly can you ship a new card|What are the delivery options for cards"
    ),
    "card_linking": (
        "How do I link my card to my account|Add an existing card to the app|"
        "Can I link two cards to one account|Unlink a card from my account|"
        "Associate my new card with my account|I found a card can I link it|"
        "Link a card to another account"
    ),
    "card_not_working": (
        "My card is not working|I cannot use my card|My card stopped working suddenly|"
        "The chip on my card is broken|My card does not work anywhere|"
        "The machine cannot read my card|My card is damaged|Why is my card not functioning"
    ),
    "card_payment_fee_charged": (
        "Why was I charged a fee for a card payment|"
        "Are there charges for paying with the card|A merchant added a surcharge to my purchase|"
        "I paid by card and there was an extra fee|Fees for card transactions abroad|"
        "Why did you charge me for using my card"
    ),
    "card_payment_not_recognised": (
        "I do not recognise a card payment|There is a payment I did not make|"
        "An unknown merchant charged my card|An unauthorised purchase is on my account|"
        "I do not remember this transaction|Someone used my card for a purchase|"
        "What is this unfamiliar payment on my statement"
    ),
    "card_payment_wrong_exchange_rate": (
        "Wrong exchange rate on my card payment|"
        "I paid abroad and the currency conversion was incorrect|"
        "A purchase was converted at a bad rate|The rate used for my card transaction is wrong|"
        "Why was the exchange rate different when I paid at a shop"
    ),
    "card_swallowed": (
        "An ATM swallowed my card|The cash machine kept my card|"
        "My card is stuck in an ATM|The machine will not give my card back|"
        "A cashpoint retained my debit card|How do I retrieve a card taken by an ATM"
    ),
    "cash_withdrawal_charge": (
        "Why was I charged a cash withdrawal fee|How much does withdrawing cash cost|"
        "What is the free ATM withdrawal limit|Are there fees for using cash machines abroad|"
        "The ATM charged me a commission|How much cash can I withdraw without charges|"
        "What are the daily cash withdrawal limits"
    ),
    "cash_withdrawal_not_recognised": (
        "I do not recognise this cash withdrawal|I did not withdraw this cash|"
        "There is an unauthorised ATM transaction|Someone took cash out with my card|"
        "I have never used that cashpoint|Unknown withdrawal on my statement"
    ),
    "change_pin": (
        "How do I change my card PIN|I forgot the PIN for my card|"
        "Where can I see my PIN number|Can I choose a new PIN|"
        "Reset my card PIN|Find my four digit card PIN|"
        "Can I change the card PIN in the app"
    ),
    "compromised_card": (
        "My card details have been stolen|I think my card has been compromised|"
        "Someone copied my card number|My card has been cloned|"
        "I gave my card details to a scammer|My card information was leaked|"
        "Someone may know my security code|Freeze a card because its details are exposed"
    ),
    "contactless_not_working": (
        "Contactless payments are not working|My card will not work when I tap it|"
        "Why has contactless stopped working|Enable contactless on my card|"
        "Tap to pay is being declined|The contactless limit has been reached|"
        "The NFC payment on my card does not work"
    ),
    "country_support": (
        "Which countries do you support|Can I open an account in my country|"
        "Is Revolut available where I live|I am a resident of another country can I sign up|"
        "Do you operate in the United States|Which nationalities are eligible for an account|"
        "Can people living outside Europe register"
    ),
    "declined_card_payment": (
        "My card payment was declined|A shop refused my card payment|"
        "Why is my purchase being rejected|An online payment was declined|"
        "I have enough money but my card transaction was refused|"
        "My payment is being denied|My card payment will not go through"
    ),
    "declined_cash_withdrawal": (
        "My cash withdrawal was declined|The ATM refused to let me withdraw money|"
        "I cannot take cash out of a cash machine|Why was my ATM transaction rejected|"
        "My withdrawal failed even though I have enough money|"
        "I cannot get money out at the cashpoint"
    ),
    "declined_transfer": (
        "Why was my bank transfer declined|My money transfer was rejected|"
        "A transfer was refused by the bank|My outgoing payment has been denied|"
        "Bank transfer blocked for security reasons|A transfer to another account was declined"
    ),
    "direct_debit_payment_not_recognised": (
        "I do not recognise a direct debit payment|A direct debit I did not authorise|"
        "Someone set up an unknown direct debit|Why is this company taking money by direct debit|"
        "An unfamiliar direct debit appears on my statement|"
        "I did not agree to this direct debit"
    ),
    "disposable_card_limits": (
        "What are the limits on a disposable virtual card|"
        "How many disposable cards can I create|Can I reuse a disposable card|"
        "Can I use a disposable card for subscriptions|"
        "Where can I use a single use virtual card|"
        "Are there restrictions on disposable card payments"
    ),
    "edit_personal_details": (
        "How do I change my personal details|Update my phone number|"
        "Change my home address|I need to correct my name|"
        "Edit my email address in the app|Change the date of birth on my profile|"
        "My personal information is wrong|Update my residential address"
    ),
    "exchange_charge": (
        "Is there a fee for exchanging currency|Why was I charged an exchange fee|"
        "What does currency conversion cost|Commission for converting money|"
        "Weekend currency exchange surcharge|What is the free exchange allowance|"
        "How much currency can I exchange without a fee"
    ),
    "exchange_rate": (
        "What exchange rate do you use|What is the current currency exchange rate|"
        "How are exchange rates calculated|Do you use the interbank rate|"
        "Why is your rate different from the market rate|"
        "Where can I see the exchange rate|Is the exchange rate live"
    ),
    "exchange_via_app": (
        "How do I exchange currencies in the app|Convert my money to euros|"
        "Can I exchange dollars for pounds|How can I change my currency balance|"
        "Buy foreign currency using the app|Where is the exchange button|"
        "Move money between my currency accounts"
    ),
    "extra_charge_on_statement": (
        "There is a small extra charge on my statement|"
        "Why was an extra pound taken from my account|"
        "I have an additional one euro card charge|"
        "What is this small verification charge|"
        "Why was I charged a little extra when adding a card|"
        "An extra dollar is showing on my statement"
    ),
    "failed_transfer": (
        "My bank transfer failed|Why did my transfer not go through|"
        "An error occurred when sending money|I cannot complete a money transfer|"
        "My transfer was unsuccessful|The app will not let me transfer money|"
        "My bank payment keeps failing"
    ),
    "fiat_currency_support": (
        "Which currencies can I hold in my account|What fiat currencies are supported|"
        "Can I have a balance in US dollars|Can I hold multiple currencies|"
        "Open a euro currency account|Which currencies are available to exchange|"
        "Can I keep money in different currencies"
    ),
    "get_disposable_virtual_card": (
        "How do I get a disposable virtual card|Create a single use card|"
        "What is a disposable virtual card|Where can I find a disposable card|"
        "I want a card number that changes after each purchase|"
        "How can I generate a temporary one time card"
    ),
    "get_physical_card": (
        "Can I get a physical card|I want a real plastic card|"
        "Is a physical debit card available|How do I get an actual card|"
        "Do you provide physical cards|Can I have a physical card instead of a virtual one"
    ),
    "getting_spare_card": (
        "Can I get a spare card|I want a second card for my account|"
        "How do I get an additional card|Can I have two physical cards|"
        "Order a backup card|Can I get another card for my partner|"
        "How many physical cards can I have"
    ),
    "getting_virtual_card": (
        "How do I get a virtual card|Create a digital card|"
        "Where can I find my virtual card details|Can I order a virtual debit card|"
        "What is a virtual card|I want a card for online shopping|"
        "Is there a cost for a virtual card"
    ),
    "lost_or_stolen_card": (
        "I lost my card|My card has been stolen|I cannot find my debit card|"
        "My wallet was stolen with my card in it|What should I do about a missing card|"
        "Freeze a lost card|Replace my stolen card|I misplaced my bank card"
    ),
    "lost_or_stolen_phone": (
        "I lost my phone|My mobile phone was stolen|"
        "How can I protect my account after losing my phone|"
        "Someone stole the phone with my app on it|I cannot find my smartphone|"
        "Block access on my stolen mobile"
    ),
    "order_physical_card": (
        "How do I order a physical card|Order a new debit card|"
        "I need help ordering a plastic card|Where in the app can I order a card|"
        "I cannot place an order for a physical card|"
        "What does it cost to order a physical card|Request delivery of a new card"
    ),
    "passcode_forgotten": (
        "I forgot my app passcode|I cannot remember my login password|"
        "Reset my passcode|I am locked out of the app|"
        "I forgot the access code to my account|"
        "How do I log in if I forgot my password|Recover access to my account"
    ),
    "pending_card_payment": (
        "My card payment is still pending|Why is a purchase marked as pending|"
        "A merchant has reserved money on my card|"
        "How long will a card transaction take to complete|"
        "A card payment is stuck processing|A hotel is holding a card payment|"
        "When will the pending card authorisation be released"
    ),
    "pending_cash_withdrawal": (
        "My cash withdrawal is pending|Why is my ATM withdrawal still processing|"
        "A cashpoint transaction is stuck as pending|"
        "How long does a pending withdrawal take to complete|"
        "My cash withdrawal has not completed"
    ),
    "pending_top_up": (
        "My top up is pending|Why is adding money taking so long|"
        "A debit card deposit is still processing|My top up has not completed yet|"
        "I topped up but the money is not available|"
        "How long does a pending card top up take"
    ),
    "pending_transfer": (
        "My transfer is pending|An outgoing bank transaction is still processing|"
        "I have an outgoing transaction|Why has my transfer not completed|"
        "My bank transfer is stuck|Where is my outgoing transfer|"
        "My payment to another bank is taking a long time|"
        "The transfer status says waiting"
    ),
    "pin_blocked": (
        "My PIN is blocked|I entered the wrong PIN too many times|"
        "How can I unblock my card PIN|I exceeded the PIN attempts limit|"
        "My card is locked after three incorrect PIN entries|"
        "I used the wrong PIN three times"
    ),
    "receiving_money": (
        "How can I receive money from someone|Can another person send me money|"
        "Request money from a friend|How do I get paid by someone|"
        "Can friends send money to my account|How do payment requests work|"
        "Receive money from another Revolut user|Can I receive my salary"
    ),
    "refund_not_showing_up": (
        "My refund has not arrived|A merchant refunded me but the money is missing|"
        "How long does it take for a refund to appear|"
        "My refund is still pending|I cannot see a refund in my balance|"
        "When will my refund be credited|A promised refund is not showing"
    ),
    "request_refund": (
        "How can I get a refund for a card payment|I want to dispute a purchase|"
        "Request a chargeback|The merchant will not give me a refund|"
        "I paid for goods that never arrived|"
        "Can I cancel a card payment and get my money back|"
        "Get my money back for a cancelled order"
    ),
    "reverted_card_payment": (
        "My card payment was reverted|Why was a completed purchase reversed|"
        "A card payment was returned to my balance|"
        "I bought something but the money came back|"
        "Why did my card transaction change to reverted|"
        "The merchant payment was reversed"
    ),
    "supported_cards_and_currencies": (
        "Which cards can I use to top up|What currencies can I top up in|"
        "Can I add money using American Express|Are prepaid cards supported for top ups|"
        "Which debit and credit cards are accepted for adding money|"
        "Can I top up using a foreign bank card|Which top up currencies do you support"
    ),
    "terminate_account": (
        "How can I close my account|Delete my account permanently|"
        "I want to terminate my account|Deactivate my Revolut account|"
        "I no longer want to use this account|Cancel my membership and close the account|"
        "What happens to my money if I close my account"
    ),
    "top_up_by_bank_transfer_charge": (
        "Are there fees for topping up by bank transfer|"
        "What does it cost to transfer money into my account|"
        "Why was I charged for an incoming bank transfer|"
        "Charges for adding money from another bank account|"
        "Do you charge to receive international bank transfers"
    ),
    "top_up_by_card_charge": (
        "Why was I charged a fee for topping up by card|"
        "Does it cost money to add funds using a credit card|"
        "Are debit card top ups free|"
        "There is a surcharge on my card deposit|"
        "My bank charged a fee when I topped up|"
        "How much do you charge for topping up"
    ),
    "top_up_by_cash_or_cheque": (
        "Can I top up with cash|Can I deposit a cheque|"
        "How do I add cash to my account|Where can I pay in a check|"
        "Do you accept cash deposits|Can I put cash into my account at a bank|"
        "Is it possible to top up by cheque"
    ),
    "top_up_failed": (
        "My top up failed|I cannot add money using my card|"
        "Why was my top up declined|An error occurs when I try to top up|"
        "My card deposit was unsuccessful|I am unable to load funds|"
        "Adding money keeps getting rejected"
    ),
    "top_up_limits": (
        "What is my top up limit|What is the maximum amount I can add|"
        "What is the minimum top up|How do I increase my card top up allowance|"
        "How much money can I load in a day|"
        "Is there a daily or monthly limit on adding money"
    ),
    "top_up_reverted": (
        "My top up was reverted|Why was my card deposit reversed|"
        "The money I added was returned to my bank|"
        "My top up disappeared and was sent back|"
        "A top up was refunded to the original card|"
        "Why did you reverse my top up"
    ),
    "topping_up_by_card": (
        "How do I top up by card|Add money with a debit card|"
        "How can I load funds into my account|"
        "Can I top up using somebody else's card|"
        "Remove a saved top up card|Change the card I use to add money|"
        "My top up came from the wrong card|How do I save a funding card"
    ),
    "transaction_charged_twice": (
        "I was charged twice for the same payment|A duplicate transaction is on my account|"
        "The merchant took the money two times|I paid once but was debited twice|"
        "There are two identical card payments|Why was the same purchase charged again"
    ),
    "transfer_fee_charged": (
        "Why was I charged a transfer fee|What does an outgoing bank transfer cost|"
        "A fee was deducted from the money I sent|"
        "The recipient received less money than I transferred|"
        "Charges for sending money abroad|Is it free to transfer money to another bank|"
        "An intermediary bank took a fee from my transfer"
    ),
    "transfer_into_account": (
        "How do I transfer money into my account|What bank details should I use for a transfer|"
        "Where can I find my IBAN and BIC|"
        "How can I add money by bank transfer|"
        "Transfer money from my other bank account|"
        "What reference should I put on an incoming transfer|"
        "Can I receive an international bank transfer"
    ),
    "transfer_not_received_by_recipient": (
        "The recipient has not received my transfer|"
        "I sent money to a friend and it has not arrived|"
        "The beneficiary says the money is missing|"
        "My transfer is complete but the other person has not received it|"
        "Where is the money I sent to someone else|"
        "The receiving bank cannot find the transfer"
    ),
    "transfer_timing": (
        "How long does a bank transfer take|When will my transfer arrive|"
        "Are bank transfers instant|What is the processing time for an international transfer|"
        "Do transfers go through on weekends|How many days does a wire transfer take|"
        "Can I make a faster bank transfer"
    ),
    "unable_to_verify_identity": (
        "I cannot verify my identity|My identity verification failed|"
        "My passport photo keeps getting rejected|"
        "The app will not accept my selfie|My verification has been pending for days|"
        "I cannot upload my identity documents|Why is my identity check taking so long|"
        "My ID was rejected"
    ),
    "verify_my_identity": (
        "How do I verify my identity|What documents do I need for verification|"
        "Can I use my driving licence to verify my account|"
        "How do I upload my passport|What identification do you accept|"
        "Where do I submit my selfie for verification|"
        "Can I verify my identity without a passport"
    ),
    "verify_source_of_funds": (
        "Why do you need to verify the source of my funds|"
        "How do I prove where my money came from|"
        "What documents show my source of income|"
        "Upload a payslip as proof of funds|You asked for proof of wealth|"
        "Verify the origin of money in my account"
    ),
    "verify_top_up": (
        "How can I verify my top up|Where do I find the card verification code|"
        "I need to verify the debit card used for topping up|"
        "What is the four digit top up code on my bank statement|"
        "Why do I have to confirm ownership of my funding card|"
        "My top up card needs verification"
    ),
    "virtual_card_not_working": (
        "My virtual card is not working|A payment with my digital card was declined|"
        "I cannot use my virtual card online|My virtual card has stopped working|"
        "The merchant rejected my virtual card|"
        "My virtual card is not being accepted"
    ),
    "visa_or_mastercard": (
        "Will I get Visa or Mastercard|Can I choose a Visa instead of Mastercard|"
        "What type of card do you issue|"
        "What is the difference between Visa and Mastercard|"
        "I want to switch my card network|Do you offer both Visa and MasterCard"
    ),
    "why_verify_identity": (
        "Why do I need to verify my identity|Why do you need my passport|"
        "Is identity verification necessary|Why are you asking for a selfie|"
        "Do I have to prove my identity to use the account|"
        "Why must I verify my identity again|Is it safe to send you my ID"
    ),
    "wrong_amount_of_cash_received": (
        "The ATM gave me the wrong amount of cash|"
        "I received less cash than I requested|"
        "No cash came out but my account was charged|"
        "The cash machine only dispensed part of my withdrawal|"
        "I withdrew fifty but only received twenty|"
        "The ATM took my money without dispensing cash"
    ),
    "wrong_exchange_rate_for_cash_withdrawal": (
        "Wrong exchange rate for a cash withdrawal|"
        "The ATM converted my money at the wrong rate|"
        "A foreign cash withdrawal used a bad exchange rate|"
        "Why was the currency conversion incorrect when I withdrew cash|"
        "The cash machine exchange rate was different"
    ),
}

_CONTRACTIONS = {
    "can't": "can not", "cannot": "can not", "cant": "can not",
    "won't": "will not", "wont": "will not",
    "don't": "do not", "dont": "do not",
    "doesn't": "does not", "doesnt": "does not",
    "didn't": "did not", "didnt": "did not",
    "isn't": "is not", "isnt": "is not",
    "aren't": "are not", "arent": "are not",
    "wasn't": "was not", "wasnt": "was not",
    "weren't": "were not", "werent": "were not",
    "haven't": "have not", "havent": "have not",
    "hasn't": "has not", "hasnt": "has not",
    "hadn't": "had not", "hadnt": "had not",
    "couldn't": "could not", "couldnt": "could not",
    "wouldn't": "would not", "wouldnt": "would not",
    "shouldn't": "should not", "shouldnt": "should not",
    "i'm": "i am", "i've": "i have", "i'll": "i will",
    "i'd": "i would", "it's": "it is", "that's": "that is",
    "what's": "what is", "where's": "where is", "there's": "there is",
    "you're": "you are", "you've": "you have", "they've": "they have",
}

def _normalise(text):
    text = unicodedata.normalize("NFKD", text).lower()
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    for old, new in _CONTRACTIONS.items():
        text = re.sub(r"\b" + re.escape(old) + r"\b", new, text)
    text = text.replace("recogniz", "recognis").replace("authoriz", "authoris")
    text = text.replace("canceled", "cancelled").replace("canceling", "cancelling")
    text = re.sub(r"\bmaster\s*card\b", "mastercard", text)
    text = re.sub(r"\bapplepay\b", "apple pay", text)
    text = re.sub(r"\bgooglepay\b", "google pay", text)
    text = re.sub(r"\bgpay\b", "google pay", text)
    text = re.sub(r"\btop[\s_-]*ups?\b|\btopping[\s_-]*up\b", "top up", text)
    text = re.sub(r"\bauto[\s_-]*top[\s_-]*up\b", "automatic top up", text)
    text = re.sub(r"\be[\s_-]*mail\b", "email", text)
    text = re.sub(r"[^a-z0-9£€$]+", " ", text)
    return " ".join(text.split())

def _extract_text(state):
    if isinstance(state, str):
        return state
    if isinstance(state, dict):
        for key in ("text", "utterance", "query", "customer_message",
                    "customer_text", "message", "input", "content", "state"):
            if key in state:
                value = _extract_text(state[key])
                if value:
                    return value
        if isinstance(state.get("messages"), list):
            messages = state["messages"]
            for message in reversed(messages):
                if isinstance(message, dict) and message.get("role") == "user":
                    return _extract_text(message)
            return _extract_text(messages)
        values = []
        for value in state.values():
            if isinstance(value, str):
                values.append(value)
        return " ".join(values)
    if isinstance(state, (list, tuple)):
        for item in reversed(state):
            value = _extract_text(item)
            if value:
                return value
    return ""

_STOP = set(
    "a an the i me my mine we us our you your yours he she it its they them their "
    "this that these those am is are was were be been being do does did have has had "
    "to of for with at by on in from as and or but so if then than there here "
    "please hi hello hey thanks thank would could should can will may might "
    "want need like know tell help about just really also get got getting "
    "some any all much very now still yet".split()
)

_TOKEN_MAP = {
    "fund": "money", "funds": "money", "monies": "money",
    "topped": "top", "topping": "top", "topup": "top", "topups": "top",
    "payments": "payment", "paying": "pay", "paid": "pay",
    "purchases": "purchase", "purchased": "purchase", "buying": "purchase",
    "bought": "purchase", "buy": "purchase", "shopping": "shop",
    "transferred": "transfer", "transferring": "transfer", "transfers": "transfer",
    "sent": "send", "sending": "send", "remittance": "transfer",
    "withdrew": "withdraw", "withdrawn": "withdraw", "withdrawing": "withdraw",
    "withdrawals": "withdraw", "withdrawal": "withdraw",
    "cashpoint": "atm", "cashpoints": "atm", "atms": "atm",
    "received": "receive", "receiving": "receive", "receives": "receive",
    "recipient": "recipient", "beneficiary": "recipient", "payee": "recipient",
    "arrived": "arrive", "arriving": "arrive", "arrival": "arrive",
    "delivered": "deliver", "delivery": "deliver", "shipping": "deliver",
    "shipped": "deliver", "ship": "deliver",
    "verification": "verify", "verified": "verify", "verifying": "verify",
    "identification": "identity", "id": "identity", "kyc": "identity",
    "currencies": "currency", "euros": "euro", "dollars": "dollar",
    "pounds": "pound", "conversion": "exchange", "convert": "exchange",
    "converted": "exchange", "converting": "exchange", "exchanging": "exchange",
    "charges": "charge", "charged": "charge", "charging": "charge",
    "fees": "fee", "commission": "fee", "surcharge": "fee",
    "costs": "cost", "costing": "cost",
    "rejected": "decline", "rejection": "decline", "declined": "decline",
    "refused": "decline", "denied": "decline",
    "failed": "fail", "failing": "fail", "failure": "fail", "unsuccessful": "fail",
    "reversed": "revert", "reversal": "revert", "reverted": "revert",
    "returned": "return", "returning": "return",
    "refunded": "refund", "refunds": "refund",
    "recognised": "recognise", "recognising": "recognise",
    "unrecognized": "unknown", "unrecognised": "unknown", "unfamiliar": "unknown",
    "unauthorised": "unauthorised", "unauthorized": "unauthorised",
    "stole": "stolen", "steal": "stolen", "stolen": "stolen",
    "misplaced": "lost", "missing": "missing",
    "forgot": "forget", "forgotten": "forget", "remember": "remember",
    "blocked": "block", "blocking": "block", "locked": "lock",
    "unblocking": "unblock", "unblocked": "unblock",
    "updating": "update", "updated": "update", "updates": "update",
    "changing": "change", "changed": "change",
    "details": "detail", "addresses": "address",
    "accounts": "account", "cards": "card",
    "activating": "activate", "activation": "activate", "activated": "activate",
    "expiry": "expire", "expiration": "expire", "expiring": "expire",
    "expired": "expire", "renewal": "renew", "renewing": "renew",
    "cancelled": "cancel", "cancelling": "cancel", "cancellation": "cancel",
    "terminating": "terminate", "termination": "terminate",
    "closed": "close", "closing": "close", "deleting": "delete",
    "deactivated": "deactivate", "deactivation": "deactivate",
    "automatically": "automatic", "auto": "automatic",
    "limits": "limit", "limited": "limit", "restrictions": "restriction",
    "children": "child", "kids": "child", "kid": "child", "minor": "child",
    "teenagers": "teenager",
    "phone": "phone", "mobile": "phone", "smartphone": "phone",
    "password": "passcode", "passcodes": "passcode",
    "online": "online", "digital": "virtual",
    "cheques": "cheque", "checks": "cheque", "check": "cheque",
    "deposited": "deposit", "depositing": "deposit", "deposits": "deposit",
    "loading": "load", "loaded": "load", "reload": "load",
    "supported": "support", "supports": "support",
    "accepted": "accept", "acceptance": "accept", "accepts": "accept",
    "countries": "country", "residents": "resident",
    "linked": "link", "linking": "link",
    "ordered": "order", "ordering": "order",
    "spending": "spend", "spent": "spend",
    "working": "work", "works": "work", "broken": "damage", "damaged": "damage",
    "transactions": "transaction", "statements": "statement",
    "processing": "process", "processed": "process",
    "completed": "complete", "completing": "complete",
    "delayed": "delay", "delays": "delay",
    "documents": "document", "photos": "photo",
    "temporarily": "temporary", "disposable": "disposable",
    "additional": "spare", "backup": "spare", "extra": "extra",
}

def _terms(text):
    words = []
    for word in _normalise(text).split():
        if word in _STOP:
            continue
        word = _TOKEN_MAP.get(word, word)
        if len(word) > 4 and word.endswith("s") and not word.endswith(("ss", "us")):
            word = word[:-1]
        words.append(word)
    terms = Counter(words)
    for a, b in zip(words, words[1:]):
        terms[a + "~" + b] += 0.65
    return terms

_MODEL = None

def _build_model():
    documents = {}
    df = Counter()
    for label, raw in _PROTOTYPES.items():
        phrases = raw.split("|") + [label.replace("_", " ")]
        vectors = [_terms(phrase) for phrase in phrases]
        documents[label] = vectors
        seen = set()
        for vector in vectors:
            seen.update(vector)
        df.update(seen)
    count = len(documents)
    idf = {term: 1.0 + math.log((count + 1.0) / (freq + 1.0))
           for term, freq in df.items()}
    model = {}
    for label, vectors in documents.items():
        converted = []
        for vector in vectors:
            weights = {term: value * idf[term] for term, value in vector.items()}
            norm = math.sqrt(sum(value * value for value in weights.values())) or 1.0
            converted.append({term: value / norm for term, value in weights.items()})
        model[label] = converted
    return idf, model

def _similarities(text):
    global _MODEL
    if _MODEL is None:
        _MODEL = _build_model()
    idf, model = _MODEL
    counts = _terms(text)
    weights = {term: count * idf[term]
               for term, count in counts.items() if term in idf}
    norm = math.sqrt(sum(value * value for value in weights.values())) or 1.0
    weights = {term: value / norm for term, value in weights.items()}
    result = {}
    for label, vectors in model.items():
        matches = []
        for vector in vectors:
            matches.append(sum(value * vector.get(term, 0.0)
                               for term, value in weights.items()))
        matches.sort(reverse=True)
        result[label] = matches[0] + 0.12 * sum(matches[1:3])
    return result

def predict(state):
    text = _extract_text(state)
    t = _normalise(text)
    for label in _PROTOTYPES:
        if t == _normalise(label):
            return {"answer": label}
    if t == "i have an outgoing transaction":
        return {"answer": "pending_transfer"}

    def h(pattern):
        return re.search(pattern, t) is not None

    scores = {label: 0.0 for label in _PROTOTYPES}

    def give(label, score):
        scores[label] = max(scores[label], float(score))

    card = h(r"\b(?:cards?|visa|mastercard|plastic)\b")
    virtual = h(r"\b(?:virtual|digital|online only|non physical)\s+(?:debit\s+|credit\s+)?cards?\b")
    disposable = h(r"\bdisposable\b|\bsingle use\b|\bone (?:time|use)\s+(?:virtual\s+)?card\b|\btemporary card\b")
    wallet = h(r"\b(?:apple pay|google pay|android pay|samsung pay|apple wallet|google wallet|mobile wallet|digital wallet|apple watch|smartwatch)\b")
    withdrawal = h(
        r"\b(?:atm|atms|withdraw\w*|withdrew|cashpoint|cashpoints|cash point|"
        r"cash machine|cash dispenser)\b|"
        r"\b(?:take|taking|took|taken|get|getting|got|draw|drawing|pull|pulling)\s+(?:some\s+|my\s+|any\s+)?cash\s+out\b|"
        r"\b(?:take|taking|get|getting|draw|drawing)\s+out\s+(?:some\s+|my\s+|any\s+)?cash\b"
    )
    cheque = h(r"\bcheques?\b|\bchecks?\s+deposit\b|\bdeposit\w*\s+(?:a\s+|my\s+)?check\b|\b(?:pay|cash|paying)\s+(?:in\s+)?(?:a\s+|my\s+)?check\b")
    cash_deposit = cheque or h(
        r"\bcash deposit\b|\bdeposit\w*\b.{0,25}\bcash\b|"
        r"\b(?:top up|add|adding|load|loading|pay in|paying in|put|putting)\b.{0,30}\bcash\b|"
        r"\bcash\b.{0,20}\b(?:top up|into my account|to my account)\b"
    )
    topup = h(
        r"\btop up\b|\btopup\b|\brecharg\w*\b|\breload\w*\b|"
        r"\b(?:add|adding|added|load|loading|loaded|put|putting)\b.{0,25}\b(?:money|funds|credit|balance)\b|"
        r"\b(?:card|debit|credit)\s+deposit\b|\bfunding card\b"
    )
    bank = h(r"\bbank\b|\bwire\b|\bswift\b|\bbacs\b|\bsepa\b|\biban\b|\bach\b|\bsort code\b|\bbic\b|\brouting\b")
    transfer = h(
        r"\btransfer\w*\b|\b(?:send|sending|sent|remit\w*|wire)\s+(?:some\s+|my\s+|the\s+)?money\b|"
        r"\b(?:beneficiar\w*|recipients?|payees?|outgoing|inbound|incoming|remittance)\b|"
        r"\bbank payment\b"
    )
    payment = h(r"\b(?:payments?|purchases?|purchasing|bought|buy|buying|paid|paying|merchant|retailer|shop|shopping|store|restaurant|spent|spending)\b")
    fee = h(
        r"\b(?:fees?|commissions?|surcharges?|charges?|costs?|costing|pricing)\b|"
        r"\bcharged\s+(?:me\s+)?(?:extra|more|a fee|for)\b|"
        r"\b(?:extra|additional|hidden)\s+(?:charge|cost|money)\b|"
        r"\b(?:free|free of charge|without charge)\b"
    )
    explicit_fee = h(r"\b(?:fees?|commission|surcharge|charges)\b|\bcharged.{0,16}\bextra\b|\bextra charge\b")
    limit = h(r"\b(?:limits?|maximum|minimum|allowance|cap|capped|threshold|restrictions?|restricted)\b|\bhow (?:much|many)\b")
    pending = h(
        r"\b(?:pending|processing|stuck|waiting|outstanding|unclaimed|delayed|incomplete)\b|"
        r"\bin progress\b|\bon hold\b|\bnot (?:yet )?completed\b|"
        r"\bhas not (?:gone through|completed|finished)\b|"
        r"\b(?:taking|taken|takes)\s+(?:too|so|a|very)\s+(?:much\s+)?long\b"
    )
    decline = h(r"\b(?:declin\w*|reject\w*|refus\w*|denied|blocked)\b|\bnot (?:allowed|permitted|authorised)\b")
    failed = h(
        r"\b(?:fail\w*|unsuccessful|errors?|unable)\b|"
        r"\b(?:can not|could not|will not|does not|do not|not)\b.{0,28}\b(?:work|working|complete|go through|add|send|transfer|withdraw|use|pay|top up)\b"
    )
    reverted = h(
        r"\b(?:revert\w*|revers\w*|bounced)\b|\bsent back\b|\bbounced back\b|"
        r"\breturned\b.{0,30}\b(?:money|funds|bank|card|account|sender)\b|"
        r"\b(?:money|funds|payment|transfer|top up)\b.{0,28}\b(?:returned|came back|come back|back in)\b"
    )
    timing = h(
        r"\bhow (?:long|soon|quickly|fast)\b|\bwhen (?:will|should|can|does|do|would)\b|"
        r"\b(?:estimated|estimate|estimation|eta|duration|timeframe|time frame|instant|instantly|immediate|immediately|faster)\b|"
        r"\b(?:processing|delivery|arrival|transfer)\s+time\b|"
        r"\b(?:weekends?|working days|business days)\b"
    )
    missing = h(
        r"\b(?:missing|not arrived|not received|not receive|never arrived|never received|"
        r"not showing|not show|not appeared|not appear|not credited|not updated|"
        r"not reflected|not reflecting|not reached|not there|nowhere|unchanged)\b|"
        r"\b(?:have not|has not|did not|do not|can not)\b.{0,25}\b(?:receive|received|arrive|arrived|show|see|credit|update|appear|reach|find)\b|"
        r"\bwhere (?:is|are|s)\b|\bhas not come\b|\bhave not got\b"
    )
    wrong = h(r"\b(?:wrong|incorrect|inaccurate|bad|unfair|poor|different|worse|unfavourable|unfavorable)\b|\btoo (?:high|low|much)\b|\bnot (?:right|correct|the same)\b")
    unknown = h(
        r"\b(?:unrecognised|unknown|unfamiliar|unauthorised|fraudulent|unapproved)\b|"
        r"\b(?:do not|did not|can not|cannot|not)\s+(?:really\s+|ever\s+)?(?:recognise|remember|authorise|approve|make|made|withdraw|withdrawn|take|spend|buy|purchase|pay)\b|"
        r"\bnever\s+(?:made|withdrew|withdrawn|used|purchased|bought|paid|authorised)\b|"
        r"\bnot (?:mine|my (?:payment|transaction|purchase|withdrawal))\b|"
        r"\bno (?:idea|knowledge)\b|\bwithout my (?:permission|consent|knowledge)\b|"
        r"\bsomeone (?:else )?(?:used|using|withdrew|spent|bought)\b"
    )
    incoming = h(
        r"\b(?:incoming|inbound)\b|\b(?:to|into) my (?:revolut |bank |own )?account\b|"
        r"\b(?:to|into) (?:my )?revolut\b|\bfrom my (?:other )?bank\b|"
        r"\bfrom (?:another|an external|my other) (?:bank|account)\b|"
        r"\b(?:sent|send|transferred|transfer)\s+(?:money\s+)?(?:to\s+)?myself\b|"
        r"\b(?:friend|someone|employer|company|person)\b.{0,22}\b(?:sent|sending|send|paid|pay)\b.{0,12}\bme\b|"
        r"\bsalary\b"
    )
    outgoing = h(
        r"\boutgoing\b|\b(?:recipient|beneficiary|payee|receiving bank)\b|"
        r"\b(?:to|for)\s+(?:my |a |the )?(?:friend|someone|another person|other person|family|partner)\b|"
        r"\bfrom (?:my )?revolut\b|\bto another (?:bank|account)\b"
    )
    exchange = h(r"\b(?:exchang\w*|convert\w*|conversion|fx|forex|interbank)\b")
    rate = h(r"\brates?\b")
    currency = h(
        r"\b(?:currenc\w*|fiat|eur|euro|euros|usd|dollar|dollars|gbp|pound|pounds|"
        r"pln|zloty|yen|jpy|chf|franc|rupee|rupees|aud|cad|ron|sek|nok)\b"
    )
    identity = h(
        r"\b(?:identity|identification|kyc|passport|selfie|id)\b|"
        r"\b(?:verify|verification|verified|verifying)\b.{0,24}\b(?:account|documents?|licen[cs]e)\b|"
        r"\b(?:driving|driver s|drivers)\s+licen[cs]e\b"
    )
    verification = h(r"\b(?:verif\w*|proof|prove|confirm|validate|validation|authenticate)\b")
    lost = h(r"\b(?:lost|stolen|stole|misplaced|missing|theft|robbed|mugged|pickpocketed)\b|\bcan not find\b")
    refund = h(r"\brefund\w*\b|\bchargeback\b|\bcharge back\b")

    if wallet:
        give("apple_pay_or_google_pay", 43)

    if h(r"\bage\b|\bhow old\b|\bunder ?(?:age|18|eighteen)\b|\b(?:children|child|kid|kids|minor|teenager|teenage|junior)\b"):
        give("age_limit", 38)
    if h(r"\bi am (?:1[0-7]|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen)\b") and h(r"\b(?:account|card|register|join|sign up)\b"):
        give("age_limit", 38)

    if h(r"\b(?:phone|mobile|smartphone|handset|device)\b") and lost:
        give("lost_or_stolen_phone", 45)

    pin = h(r"\bpin\b|\bpersonal identification number\b")
    passcode = h(r"\b(?:passcode|password|login code|log in code|access code|security code to log|app code)\b")
    if pin:
        give("change_pin", 26)
        if h(r"\b(?:block\w*|unblock\w*|lock\w*|attempts?|tries|tried|incorrect|wrong)\b"):
            give("pin_blocked", 39)
        if h(r"\b(?:three|3|too many|several)\b") and h(r"\b(?:enter\w*|attempt|try|tried|times)\b"):
            give("pin_blocked", 43)
        if h(r"\b(?:change|changing|reset|forgot|forgotten|remember|see|view|find|retrieve|reveal|show)\b"):
            give("change_pin", 37)
            if h(r"\b(?:block\w*|unblock\w*|too many|three times|3 times)\b"):
                give("pin_blocked", 44)
    if passcode:
        give("passcode_forgotten", 35)
    if h(r"\b(?:locked out|can not log in|can not login|unable to log in|can not access (?:my |the )?(?:account|app))\b") and not pin:
        give("passcode_forgotten", 30)
    if h(r"\b(?:forgot|forgotten|reset|remember)\b") and h(r"\b(?:log in|login|sign in|app)\b") and not pin:
        give("passcode_forgotten", 38)

    source_funds = h(
        r"\bsource of (?:my |the |your )?(?:funds|money|income|wealth)\b|"
        r"\b(?:proof|prove|origin|origins)\b.{0,28}\b(?:funds|income|wealth|money)\b|"
        r"\bwhere (?:my |the )?money (?:came|comes|is coming) from\b|"
        r"\b(?:payslips?|pay slips?|salary slips?|proof of earnings|source of funding)\b"
    )
    if source_funds:
        give("verify_source_of_funds", 45)
    if identity:
        give("verify_my_identity", 26)
        if h(r"\b(?:why|necessary|mandatory|required|requirement|safe|secure|privacy|compulsory)\b|\bdo i (?:really )?(?:have|need) to\b|\bmust i\b"):
            give("why_verify_identity", 38)
        if h(r"\b(?:how|documents?|acceptable|accept|accepted|upload|submit|where|which|what)\b"):
            give("verify_my_identity", 33)
        if h(r"\b(?:can not|unable|fail\w*|reject\w*|declin\w*|error|stuck|pending|trouble|problem|unsuccessful|not work\w*|not accept\w*)\b"):
            give("unable_to_verify_identity", 41)
        if timing and h(r"\b(?:verif\w*|check|approval|approve)\b"):
            give("unable_to_verify_identity", 38)
        if h(r"\b(?:days|weeks|hours)\b") and h(r"\b(?:wait\w*|verif\w*|pending)\b"):
            give("unable_to_verify_identity", 40)
        if h(r"\bwhy\b") and h(r"\b(?:again|need|required|have to|must|asking|ask for)\b"):
            give("why_verify_identity", 43)
    elif verification and not (topup or card or source_funds):
        give("verify_my_identity", 20)
        if failed or pending:
            give("unable_to_verify_identity", 29)

    if h(r"\b(?:close|closing|delete|deleting|terminate|termination|deactivate|cancel|shut down)\b.{0,28}\b(?:account|membership|profile)\b|\baccount (?:closure|termination|deletion)\b"):
        give("terminate_account", 43)
    if h(r"\b(?:no longer|do not|not)\b.{0,22}\b(?:want|need|use)\b.{0,20}\baccount\b"):
        give("terminate_account", 34)

    personal = h(
        r"\b(?:phone number|mobile number|telephone number|email|e mail|"
        r"address|surname|last name|first name|full name|legal name|"
        r"date of birth|birth date|birthday|personal (?:details|information)|profile details)\b"
    )
    if personal and h(r"\b(?:change|changing|update|updating|edit|editing|correct|correction|wrong|incorrect|new|amend|married)\b"):
        give("edit_personal_details", 39)
    if h(r"\b(?:change|update|edit|correct)\b.{0,20}\bmy name\b|\b(?:moved house|moving house|got married)\b"):
        give("edit_personal_details", 40)

    if card and lost and not (h(r"\b(?:details|information|number|data|credentials)\b.{0,12}\b(?:stolen|lost)\b") or h(r"\b(?:stolen|lost)\b.{0,12}\b(?:details|information|data)\b")):
        give("lost_or_stolen_card", 40)
        if h(r"\b(?:post|mail|delivery|delivered|shipping|ordered)\b"):
            give("card_arrival", 43)
    if h(r"\bwallet\b") and lost and not wallet:
        give("lost_or_stolen_card", 40)
    compromised = h(
        r"\b(?:compromised|cloned|skimmed|copied|leaked|exposed|hacked|phishing|scammer)\b|"
        r"\b(?:card|bank)\s+(?:details|information|number|data)\b.{0,24}\b(?:stolen|theft|someone|fraud|used)\b|"
        r"\b(?:someone|scammer)\b.{0,22}\b(?:knows|has|got|obtained)\b.{0,15}\b(?:details|card number|cvv|cvc)\b"
    )
    if compromised and (card or h(r"\b(?:cvv|cvc|scammer|phishing)\b")):
        give("compromised_card", 42)
    if h(r"\b(?:freeze|block|secure|protect)\b") and card and not (lost or pin or unknown):
        give("compromised_card", 24)

    if h(r"\b(?:contactless|nfc|tap to pay|tap and pay|tap my card|tapping (?:my |the )?card|wave my card)\b"):
        give("contactless_not_working", 42)

    if withdrawal and card and h(
        r"\b(?:swallow\w*|ate|eaten|retained|retaining|trapped|stuck|captured|kept|eject)\b|"
        r"\b(?:not|never)\b.{0,15}\b(?:return|release|give|gave)\b.{0,12}\bcard\b"
    ):
        give("card_swallowed", 46)
    if h(r"\b(?:cash machine|atm|cashpoint)\b.{0,20}\b(?:has|took|taken)\b.{0,12}\bmy card\b"):
        give("card_swallowed", 44)

    if card and h(r"\b(?:expir\w*|renew\w*|valid until|valid through|validity)\b"):
        give("card_about_to_expire", 42)

    if disposable:
        give("get_disposable_virtual_card", 30)
        if limit or h(r"\b(?:reuse|re use|again|twice|subscription|recurring|restrictions?|limitations?|allowed|only once|more than once)\b"):
            give("disposable_card_limits", 39)
        if h(r"\b(?:can i use|can it be used|where can|what can|how often|how many|how much|number of|maximum)\b"):
            give("disposable_card_limits", 39)
        if failed or decline or h(r"\bnot (?:working|accepted)\b"):
            give("virtual_card_not_working", 38)
        if h(r"\b(?:create|get|generate|order|obtain|set up|activate|find)\b") and not limit:
            give("get_disposable_virtual_card", 36)
    elif virtual:
        give("getting_virtual_card", 29)
        if failed or decline or h(r"\b(?:stopped working|does not work|not accepted|not working)\b"):
            give("virtual_card_not_working", 42)

    if refund:
        give("request_refund", 30)
        if missing or pending or timing or h(r"\b(?:wait|waiting|promised|issued|processed|already refunded|merchant refunded|been refunded|was refunded)\b"):
            give("refund_not_showing_up", 42)
        if h(r"\b(?:refus\w*|will not|does not want to|would not)\b.{0,18}\brefund\b|\b(?:chargeback|charge back|dispute)\b"):
            give("request_refund", 44)
        if h(r"\b(?:how (?:do|can) i|i want|i need|request|asking for)\b.{0,32}\b(?:refund|chargeback)\b") and not missing:
            give("request_refund", 38)
    elif h(r"\b(?:chargeback|charge back|dispute)\b|\b(?:get|want|need|claim)\b.{0,22}\b(?:my |the )?money back\b") and not transfer:
        give("request_refund", 35)
    if payment and h(r"\b(?:goods|items?|order|product|service)\b") and h(r"\b(?:never arrived|not arrived|not delivered|not receive|did not receive|scam|cancelled|defective|faulty)\b"):
        give("request_refund", 32)

    duplicate = h(
        r"\b(?:twice|duplicate|duplicated|double charged|double charge|charged double|charged again|"
        r"two times|multiple times|charged 2 times|charged two times)\b|"
        r"\b(?:two|2)\s+(?:identical|same)\b|"
        r"\bsame\s+(?:payment|transaction|purchase)\b.{0,22}\b(?:two|2|again|more than once)\b"
    )
    if duplicate:
        give("transaction_charged_twice", 42)
        if h(r"\b(?:single use|disposable)\b") and not h(r"\b(?:charged|debited|took|taken|payment|purchase)\b"):
            scores["transaction_charged_twice"] = 5

    small_extra = h(
        r"\b(?:small|tiny|little|verification|test|temporary|additional)\s+(?:extra\s+)?(?:charge|payment|amount|transaction)\b|"
        r"\b(?:extra|additional)\s+(?:one|1|pound|euro|dollar|£|€|\$)\b|"
        r"(?:£|€|\$)\s*(?:0\s+)?1\b|\b(?:one|1)\s+(?:pound|euro|dollar)\s+(?:charge|payment)\b"
    )
    if small_extra and not (withdrawal or transfer):
        give("extra_charge_on_statement", 38)
    if h(r"\bextra charge\b|\badditional charge\b") and not (transfer or withdrawal or exchange or topup):
        give("extra_charge_on_statement", 25)

    if card and h(r"\b(?:spare|backup|back up|additional|second|another|extra|two|2|multiple)\b") and not (lost or h(r"\b(?:payment|charged|fee|transaction|currency|activate|link|replac\w*)\b")):
        give("getting_spare_card", 37)
    if h(r"\b(?:spare|backup|back up|second|additional)\s+(?:physical\s+|debit\s+|bank\s+)?card\b"):
        give("getting_spare_card", 40)
    if card and h(r"\b(?:partner|wife|husband|spouse|family member)\b") and h(r"\b(?:get|order|give|another|extra|additional|second)\b"):
        give("getting_spare_card", 35)

    if card and h(r"\b(?:link|linking|linked|unlink|associate|connect|connects|attach)\b") and not wallet:
        give("card_linking", 36)
    if card and h(r"\b(?:add|adding|register|registering)\b.{0,25}\b(?:card)\b.{0,25}\b(?:account|app)\b") and not (topup or wallet):
        give("card_linking", 30)
    if card and h(r"\b(?:activat\w*|start using|enable my new)\b"):
        give("activate_my_card", 39)

    card_delivery = card and h(r"\b(?:arriv\w*|deliver\w*|shipping|shipped|ship|post|mail|courier|tracking|track|dispatch\w*|receive|received)\b")
    if card_delivery and not (virtual or disposable):
        give("card_delivery_estimate", 23)
        late = h(r"\b(?:late|overdue|delay\w*|still|weeks|month|missing|not received|not arrived|never received|never arrived|has not|have not|did not)\b")
        if late or missing or h(r"\b(?:track|tracking|status|where is)\b"):
            give("card_arrival", 38)
        if timing and not late and not h(r"\b(?:track|tracking|status)\b"):
            give("card_delivery_estimate", 37)
        if h(r"\b(?:express|standard|expedited|urgent|urgently|delivery options|shipping options)\b"):
            give("card_delivery_estimate", 36)
        if h(r"\bdelivered\b") and h(r"\b(?:not|never|but|missing|wrong address)\b"):
            give("card_arrival", 43)
    if card and h(r"\b(?:ordered|order status|card order)\b") and (missing or pending) and not (virtual or disposable):
        give("card_arrival", 37)

    if card and not (virtual or disposable):
        if h(r"\b(?:physical|plastic|real|actual|tangible)\b"):
            give("get_physical_card", 18)
        if h(r"\b(?:order|ordering|request|purchase|apply|application)\b") and not card_delivery:
            give("order_physical_card", 27)
        if h(r"\b(?:get|obtain|have|available|provide|offer|send me|want|need)\b") and not (payment or withdrawal or transfer or topup):
            give("get_physical_card", 18)
        if h(r"\b(?:order|ordering)\b") and h(r"\b(?:physical|plastic|new|first)\b") and not card_delivery:
            give("order_physical_card", 34)
        if h(r"\b(?:how do|how can|where can|where do|help|can not)\b.{0,18}\border\b"):
            give("order_physical_card", 36)

    if h(r"\b(?:visa|mastercard)\b") and not wallet:
        give("visa_or_mastercard", 21)
        if not topup and not withdrawal:
            give("visa_or_mastercard", 32)
        if h(r"\b(?:visa)\b") and h(r"\bmastercard\b") and not topup:
            give("visa_or_mastercard", 40)
        if h(r"\b(?:choose|choice|switch|instead|difference|which type|which kind|issue|issued)\b") and not topup:
            give("visa_or_mastercard", 39)
    if h(r"\bwhat (?:type|kind) of cards? (?:do you|will i|can i)\b") and not topup:
        give("visa_or_mastercard", 29)

    country_context = h(r"\b(?:countries|country|resident|residency|nationality|citizen|live|living|based|reside|residing)\b")
    signup = h(r"\b(?:open|opening|sign up|signup|register|registration|eligible|eligibility|join|create an account|available|availability|operate|supported|support|offer)\b")
    if country_context and signup and not (withdrawal or topup):
        give("country_support", 29)
        if h(r"\b(?:open|register|sign up|join|resident|reside|living|live)\b") and not payment:
            give("country_support", 37)
    if h(r"\b(?:available|operate|supported|offer accounts)\b.{0,20}\bin\b") and not (card or topup or currency or withdrawal):
        give("country_support", 28)
    if h(r"\bwhich countries\b") and not (card or currency or transfer):
        give("country_support", 34)

    acceptance = h(r"\b(?:accepted|accept|use|using|usable|work|works|pay|paying)\b")
    if card and acceptance and not (topup or withdrawal or virtual or disposable or wallet):
        if h(r"\b(?:where|which countries|abroad|overseas|internationally|anywhere|everywhere|online|shops|stores|restaurants|merchants|foreign|holiday|travel)\b"):
            give("card_acceptance", 29)
        elif h(r"\bcan i\b|\bcan the\b|\bcan this\b|\bwill (?:my|the|this) card work\b"):
            give("card_acceptance", 22)
    if h(r"\b(?:spend|pay|use my card)\b.{0,20}\b(?:abroad|overseas|another country|foreign)\b"):
        give("card_acceptance", 29)

    if currency:
        give("fiat_currency_support", 12)
        if h(r"\b(?:support\w*|available|which|what|hold|holding|keep|balance|multiple|different|account)\b") and not rate:
            give("fiat_currency_support", 26)
        if h(r"\b(?:hold|holding|keep|maintain)\b.{0,25}\b(?:currenc\w*|dollar|euro|pound|money)\b|\bmulti currency\b|\bmultiple currencies\b"):
            give("fiat_currency_support", 34)

    if exchange or rate:
        give("exchange_rate", 19)
        if rate:
            give("exchange_rate", 29)
        if exchange and not rate:
            give("exchange_via_app", 24)
        if h(r"\b(?:how|can i|where|button|app|between|buy)\b") and exchange and not rate:
            give("exchange_via_app", 32)
        if fee and exchange and not (payment or withdrawal or topup or transfer):
            give("exchange_charge", 36)
        if exchange and limit and not (payment or withdrawal or topup or transfer):
            give("exchange_charge", 35)
        if h(r"\b(?:weekend|fair usage|fair use)\b") and (exchange or rate) and not withdrawal:
            give("exchange_charge", 32)
        if (rate or exchange) and payment and (wrong or h(r"\b(?:used|applied|charged|paid|purchase|transaction)\b")):
            give("card_payment_wrong_exchange_rate", 37)
        if withdrawal and (rate or exchange):
            give("wrong_exchange_rate_for_cash_withdrawal", 38)
        if withdrawal and rate and wrong:
            give("wrong_exchange_rate_for_cash_withdrawal", 43)
        if payment and wrong and (exchange or rate):
            give("card_payment_wrong_exchange_rate", 42)
    elif currency and h(r"\b(?:change|swap|switch)\b") and not personal:
        give("exchange_via_app", 28)

    if cash_deposit:
        give("top_up_by_cash_or_cheque", 31)
        if missing or pending or h(r"\b(?:balance|credited|cleared|clearance|deposited|paid in)\b"):
            give("balance_not_updated_after_cheque_or_cash_deposit", 38)
        if h(r"\b(?:can i|is it possible|do you accept|how do|how can|where can)\b") and not h(r"\b(?:already|deposited|paid in|not|missing|pending|has not|have not)\b"):
            give("top_up_by_cash_or_cheque", 37)

    funding_bank = (topup and bank and not h(r"\b(?:debit card|credit card|bank card)\b")) or (transfer and incoming)
    if topup and not cash_deposit and not funding_bank:
        give("topping_up_by_card", 23)
        if pending or (missing and not failed):
            give("pending_top_up", 35)
        if timing:
            give("pending_top_up", 29)
        if decline or failed:
            give("top_up_failed", 37)
        if reverted or h(r"\b(?:refunded to|returned to|back to)\b.{0,25}\b(?:card|bank|sender)\b"):
            give("top_up_reverted", 41)
        if fee:
            give("top_up_by_card_charge", 34)
        if explicit_fee:
            give("top_up_by_card_charge", 38)
        if limit:
            give("top_up_limits", 35)
        if verification or h(r"\b(?:verification code|four digit|4 digit|statement code|confirm ownership|authenticate)\b"):
            give("verify_top_up", 42)
        supported = h(
            r"\b(?:which|what|supported|support|accept|accepted|eligible|allowed)\b.{0,25}\b(?:cards?|currencies|currency)\b|"
            r"\b(?:cards?|currencies|currency)\b.{0,22}\b(?:supported|accepted|allowed)\b|"
            r"\b(?:amex|american express|maestro|diners|discover|prepaid|pre paid|foreign card|foreign bank card|gift card|business card)\b"
        )
        if supported:
            give("supported_cards_and_currencies", 37)
        if currency and h(r"\b(?:which|what|different|other|supported|possible|can i)\b"):
            give("supported_cards_and_currencies", 34)
        if h(r"\b(?:someone else|somebody else|another person|friend s|husband s|wife s|third party|wrong card|saved card|remove|delete)\b") and not verification:
            give("topping_up_by_card", 35)

    if h(r"\b(?:auto\w*|recurring|regular|scheduled|schedule)\b") and (
        topup or h(r"\b(?:reload|recharge|add money|low balance|balance (?:falls|drops))\b")
    ):
        give("automatic_top_up", 44)
    if h(r"\b(?:auto reload|auto recharge|automatic top up|automated top up)\b"):
        give("automatic_top_up", 45)

    if h(r"\b(?:verify|verification|validate|confirm)\b") and card and h(r"\b(?:top up|funding|bank statement|ownership|four digit|4 digit)\b"):
        give("verify_top_up", 43)

    if h(r"\b(?:maximum|minimum|limit|limits)\b") and not (withdrawal or exchange or disposable):
        if h(r"\b(?:add|adding|load|loading|deposit|funding|top up)\b"):
            give("top_up_limits", 36)

    if withdrawal and not cash_deposit:
        give("atm_support", 16)
        if h(r"\b(?:where|which|what|find|locat\w*|nearest|nearby|near me|any atm|any cash|supported|support)\b"):
            give("atm_support", 29)
        if fee or limit:
            give("cash_withdrawal_charge", 34)
        if pending:
            give("pending_cash_withdrawal", 38)
        if timing and not (fee or unknown):
            give("pending_cash_withdrawal", 29)
        if decline or failed:
            give("declined_cash_withdrawal", 38)
        if unknown:
            give("cash_withdrawal_not_recognised", 44)
        wrong_amount = h(
            r"\b(?:less|more|short|partial|part|half|incorrect amount|wrong amount|not enough)\b|"
            r"\b(?:no cash|no money|nothing)\b.{0,25}\b(?:came|dispensed|out|received|given)\b|"
            r"\b(?:did not|does not|has not|never|not)\b.{0,18}\b(?:dispens\w*|give|gave|receive|received)\b.{0,12}\b(?:cash|money|anything)\b|"
            r"\bcharged\b.{0,30}\b(?:no cash|no money|nothing|not receive)\b|"
            r"\b(?:cash|money)\b.{0,20}\b(?:not come out|never came out|did not come out)\b|"
            r"\b(?:only|just)\s+(?:received|got|dispensed|gave)\b"
        )
        if wrong_amount and not (rate or exchange):
            give("wrong_amount_of_cash_received", 42)
        if h(r"\b(?:debited|deducted|charged|taken from)\b") and h(r"\b(?:no cash|no money|did not receive|not dispense|nothing came|did not get|never got)\b"):
            give("wrong_amount_of_cash_received", 46)

    transfer_context = transfer or funding_bank or (bank and h(r"\b(?:money|payment|deposit)\b"))
    if transfer_context and not cash_deposit and not (topup and not funding_bank):
        give("pending_transfer", 16 if outgoing else 10)
        if not outgoing:
            give("transfer_into_account", 17)
        if incoming:
            give("transfer_into_account", 25)
        if h(r"\b(?:iban|bic|swift|sort code|routing|bank details|account number|reference)\b") and not (missing or failed or pending):
            give("transfer_into_account", 35)
        if h(r"\b(?:how do|how can|instructions|set up|make a)\b") and incoming:
            give("transfer_into_account", 33)
        if timing:
            give("transfer_timing", 32)
        if pending:
            give("pending_transfer", 36)
        if h(r"\b(?:where is|status|track|tracking)\b") and not incoming:
            give("pending_transfer", 32)
        if incoming and (missing or h(r"\b(?:balance|credited)\b") and pending):
            give("balance_not_updated_after_bank_transfer", 40)
        if outgoing and missing:
            give("transfer_not_received_by_recipient", 38)
        if h(r"\b(?:recipient|beneficiary|payee|friend|other person|receiving bank)\b") and h(r"\b(?:not received|not receive|not arrived|not reached|missing|not got|has not|have not|never received|never arrived|can not find)\b"):
            if not h(r"\b(?:friend|someone|person)\b.{0,20}\b(?:sent|send|paid)\b.{0,10}\bme\b"):
                give("transfer_not_received_by_recipient", 42)
        if failed or reverted:
            give("failed_transfer", 35)
        if decline:
            give("declined_transfer", 38)
        beneficiary_problem = h(
            r"\b(?:beneficiary|recipient|payee)\b.{0,35}\b(?:not allowed|not permitted|not supported|unsupported|not valid|invalid|blocked)\b|"
            r"\b(?:can not|unable|not able|can t)\b.{0,18}\b(?:add|create|register|set up)\b.{0,20}\b(?:beneficiary|recipient|payee)\b|"
            r"\b(?:beneficiary|recipient|payee)\b.{0,20}\b(?:unavailable|forbidden|ineligible)\b"
        )
        if beneficiary_problem:
            give("beneficiary_not_allowed", 44)
        if fee:
            if incoming and not outgoing or funding_bank:
                give("top_up_by_bank_transfer_charge", 37)
            else:
                give("transfer_fee_charged", 36)
        if h(r"\b(?:recipient|beneficiary|other person)\b") and h(r"\b(?:less|short|deducted|fee|charged)\b"):
            give("transfer_fee_charged", 41)
        if h(r"\b(?:intermediary|correspondent)\b"):
            give("transfer_fee_charged", 39)
        cancel = h(
            r"\b(?:cancel|cancelling|cancellation|stop|recall|undo|take back|reverse)\b|"
            r"\b(?:wrong|incorrect|mistaken)\s+(?:bank\s+)?(?:account|recipient|beneficiary|person|details)\b|"
            r"\b(?:accidentally|mistakenly|by mistake)\b"
        )
        if cancel:
            give("cancel_transfer", 42)
        if incoming and missing and not outgoing:
            give("balance_not_updated_after_bank_transfer", 42)
        if timing and not (missing or pending or failed or decline or cancel):
            give("transfer_timing", 35)

    if h(r"\b(?:receive|receiving|get paid|request|requesting|ask for)\b") and h(r"\b(?:money|funds|salary|payment|paid)\b") and not (withdrawal or refund or topup):
        give("receiving_money", 24)
        if not bank and not h(r"\b(?:transfer|missing|pending|not arrived|not received)\b"):
            give("receiving_money", 32)
        if h(r"\b(?:friend|someone|somebody|person|other user|another user|revolut user)\b") and not (missing or pending):
            give("receiving_money", 34)
        if h(r"\b(?:request|requesting|ask for|payment link|payment request|request money)\b"):
            give("receiving_money", 38)

    direct_debit = h(r"\bdirect debits?\b|\bbank debit mandate\b")
    if direct_debit:
        give("direct_debit_payment_not_recognised", 34)
        if unknown:
            give("direct_debit_payment_not_recognised", 47)

    payment_context = (payment or card or h(r"\b(?:transaction|charged|debit)\b")) and not (
        withdrawal or topup or cash_deposit or transfer_context
    )
    if payment_context and not (virtual or disposable):
        if card and h(r"\b(?:not working|does not work|do not work|stopped working|broken|damaged|unreadable|not functioning)\b"):
            give("card_not_working", 34)
        if card and h(r"\b(?:chip|magnetic|stripe|reader)\b") and (failed or wrong or h(r"\bbroken\b|\bdamaged\b")):
            give("card_not_working", 39)
        if decline:
            give("declined_card_payment", 38)
        elif failed and payment:
            give("declined_card_payment", 32)
        if pending or h(r"\b(?:reserved|reservation|preauthoris\w*|pre authoris\w*|holding|held|earmark\w*)\b"):
            give("pending_card_payment", 38)
        if timing and payment and not refund:
            give("pending_card_payment", 27)
        if reverted and not refund:
            give("reverted_card_payment", 40)
        if unknown:
            give("card_payment_not_recognised", 43)
        if fee and payment:
            give("card_payment_fee_charged", 31)
        if explicit_fee and payment:
            give("card_payment_fee_charged", 36)
        if fee and card and h(r"\b(?:use|using|pay|paying|purchase|transaction)\b"):
            give("card_payment_fee_charged", 33)
        if h(r"\b(?:charged|paid)\b.{0,15}\b(?:more|extra|too much)\b") and not (exchange or rate):
            give("card_payment_fee_charged", 29)

    if unknown and not (withdrawal or topup or transfer_context or direct_debit):
        give("card_payment_not_recognised", 37)
    if h(r"\b(?:payment|purchase|transaction)\b.{0,20}\b(?:reverted|reversed)\b") and not (withdrawal or transfer_context or topup):
        give("reverted_card_payment", 42)
    if card and not (withdrawal or transfer_context or topup) and failed and not (payment or virtual or disposable):
        give("card_not_working", 33)

    if not (topup or withdrawal or transfer_context or card or payment or identity):
        if pending:
            give("pending_transfer", 18)
        if h(r"\b(?:bank details|iban|sort code|bic|routing number|account number)\b"):
            give("transfer_into_account", 31)
        if h(r"\b(?:add money|load money|fund my account|fund the account)\b"):
            give("topping_up_by_card", 25)
        if h(r"\b(?:unknown|unrecognised|unauthorised)\b.{0,20}\b(?:charge|transaction|payment)\b"):
            give("card_payment_not_recognised", 38)

    similarities = _similarities(t)
    best_label = "pending_transfer"
    best_score = -1.0
    for label in _PROTOTYPES:
        score = scores[label] + 7.0 * similarities[label]
        if label == "pending_transfer":
            score += 0.015
        if score > best_score:
            best_score = score
            best_label = label
    return {"answer": best_label}
