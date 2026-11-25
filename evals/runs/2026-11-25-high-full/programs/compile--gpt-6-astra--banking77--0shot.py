import re
import math
import unicodedata
from collections import Counter

# The phrases provide lexical coverage for short, elliptical, and paraphrased
# questions. Compositional rules below distinguish transaction types and states.
_PHRASES = {
    "activate_my_card": (
        "How do I activate my card|Activate a new card|My card needs activation|"
        "Where is the card activation option|Do I need to activate the replacement card|"
        "I cannot activate my debit card|Make my new card ready to use"
    ),
    "age_limit": (
        "How old must I be to open an account|What is the minimum age|"
        "Can someone under eighteen have an account|Account for my child|"
        "Can a teenager get a card|I am sixteen can I register|Is there an age restriction"
    ),
    "apple_pay_or_google_pay": (
        "Does the card work with Apple Pay|How to set up Google Pay|"
        "Add my card to Apple wallet|Google wallet will not accept my card|"
        "Can I pay with my iPhone|Use the card with my Apple watch|"
        "Android Pay support|Mobile wallet support"
    ),
    "atm_support": (
        "Which ATMs can I use|Where can I withdraw cash|"
        "What cash machines accept this card|Can I use any ATM|"
        "Which banks support cash withdrawals|Find a nearby cashpoint|"
        "Can I withdraw money abroad|ATM withdrawal limits|Can I get cash without a card"
    ),
    "automatic_top_up": (
        "How do I set up automatic top up|Turn off automatic top ups|"
        "Automatically add money when the balance is low|Recurring card top ups|"
        "Change the auto top up amount|My automatic top up stopped working|"
        "Set a threshold for automatic funding|Schedule a regular top up"
    ),
    "balance_not_updated_after_bank_transfer": (
        "My bank transfer has not appeared in my balance|"
        "I transferred money into my account but it is not there|"
        "Incoming bank transfer missing|Bank deposit not credited|"
        "Sent money from my bank to Revolut and my balance is unchanged|"
        "My account has not been updated after a wire transfer|"
        "I am waiting for a bank transfer to reach my account"
    ),
    "balance_not_updated_after_cheque_or_cash_deposit": (
        "My cash deposit is not showing in my balance|"
        "I deposited a cheque but the money has not arrived|"
        "A check deposit has not cleared|Cash paid into the account is missing|"
        "Balance unchanged after depositing cash|When will my deposited cheque be credited"
    ),
    "beneficiary_not_allowed": (
        "The beneficiary is not allowed|Cannot transfer to this beneficiary|"
        "Recipient is not permitted|Why is this beneficiary blocked|"
        "Transfer says beneficiary not allowed|Recipient bank is unsupported|"
        "Can I send money to a cryptocurrency exchange"
    ),
    "cancel_transfer": (
        "Can I cancel a transfer|Stop a bank transfer|Recall money I sent|"
        "Undo an international transfer|Cancel a scheduled transfer|"
        "I sent money to the wrong account|Reverse a transfer made by mistake|"
        "Cancel a standing order|Change the recipient of a transfer"
    ),
    "card_about_to_expire": (
        "My card is about to expire|What happens when my card expires|"
        "Get a replacement for an expired card|Card expiration date|"
        "Renew my debit card|Will you send a new card before expiry|"
        "My card expires next month"
    ),
    "card_acceptance": (
        "Where can I use my card|Which shops accept the card|"
        "Can I use my card abroad|Is the card accepted everywhere|"
        "Can I pay online with this card|Use my card in another country|"
        "Do merchants accept Revolut cards|Can I pay at a petrol station|"
        "Can I use my card in America"
    ),
    "card_arrival": (
        "My card has not arrived|Where is the card I ordered|"
        "Track my card delivery|My card is late|I am still waiting for my card|"
        "The delivery date passed and I have no card|"
        "My card was sent to the wrong address|Card lost in the mail|"
        "Check the shipping status of my ordered card"
    ),
    "card_delivery_estimate": (
        "How long does card delivery take|When will my new card arrive|"
        "What is the estimated delivery time|How quickly can you send a card|"
        "Is express card delivery available|Can I get a card before my holiday|"
        "How many days to receive a card|Delivery options and shipping time"
    ),
    "card_linking": (
        "How do I link a card to my account|Link a replacement card in the app|"
        "My card is linked to another account|Can I link two cards to one account|"
        "Attach an existing card to my account|Cannot link my card|"
        "I found a card and want to link it|Connect my card to the application"
    ),
    "card_not_working": (
        "My card is not working|The card stopped working|"
        "My debit card does not work anywhere|The card reader cannot read my card|"
        "My card is damaged|The chip on my card is broken|"
        "My card is not functioning|Something is wrong with my physical card"
    ),
    "card_payment_fee_charged": (
        "Why was I charged a fee for a card payment|"
        "Extra charge for paying with my card|Do card payments have fees|"
        "Charged more than the purchase price|Card purchase surcharge|"
        "Fee for using my card abroad|A merchant charged an additional fee|"
        "Why did I pay extra when shopping"
    ),
    "card_payment_not_recognised": (
        "I do not recognise a card payment|Unknown purchase on my statement|"
        "Someone made a payment with my card|I did not make this transaction|"
        "There is an unauthorised card charge|Unfamiliar merchant on my account|"
        "I was charged by a shop I have never visited|Fraudulent card transaction"
    ),
    "card_payment_wrong_exchange_rate": (
        "Wrong exchange rate for a card payment|"
        "The conversion rate on my purchase is incorrect|"
        "I paid abroad and got a bad exchange rate|"
        "The exchange rate used by the merchant was different|"
        "My card purchase used the wrong currency conversion|"
        "A foreign card payment cost more because of the exchange rate"
    ),
    "card_swallowed": (
        "The ATM swallowed my card|Cash machine kept my card|"
        "My card is stuck in an ATM|ATM did not return my card|"
        "The machine ate my debit card|How do I recover a card retained by a cashpoint"
    ),
    "cash_withdrawal_charge": (
        "Why was I charged for withdrawing cash|ATM withdrawal fee|"
        "Cash machine charged a commission|Are cash withdrawals free|"
        "Extra charge for taking money out|Withdrawal surcharge abroad|"
        "How much does it cost to withdraw money|Free cash withdrawal allowance"
    ),
    "cash_withdrawal_not_recognised": (
        "I do not recognise a cash withdrawal|"
        "There is an ATM withdrawal I did not make|"
        "Someone withdrew cash from my account|Unauthorised cash withdrawal|"
        "I never took out this money|Unknown cash withdrawal on my statement"
    ),
    "change_pin": (
        "How do I change my card PIN|Reset the PIN on my debit card|"
        "I forgot my card PIN|Where can I find my PIN number|"
        "Can I choose a new card PIN|View my card PIN in the app|"
        "I need a reminder of my PIN|Is it possible to change the PIN at an ATM"
    ),
    "compromised_card": (
        "My card details have been stolen|I think my card has been compromised|"
        "Someone knows my card number|My card was cloned|"
        "I gave my card information to a scammer|Freeze a hacked card|"
        "My card details leaked online|Someone may have access to my card|"
        "My card information is being used without permission"
    ),
    "contactless_not_working": (
        "Contactless is not working|My tap to pay was declined|"
        "The contactless function stopped working|"
        "I cannot pay by tapping my card|Contactless payments fail|"
        "The contactless reader does not recognise my card|"
        "Why do I need to insert my card instead of tapping"
    ),
    "country_support": (
        "Which countries are supported|Can a resident of my country open an account|"
        "Is Revolut available in the United States|"
        "I live outside Europe can I register|Can I open an account in India|"
        "What countries do you operate in|Can a nonresident get an account|"
        "Where do I need to live to be eligible"
    ),
    "declined_card_payment": (
        "My card payment was declined|A purchase was rejected|"
        "The shop refused my card payment|My card was declined despite enough money|"
        "Payment was not authorised|Why is my online payment being rejected|"
        "The card transaction would not go through|My debit card got declined"
    ),
    "declined_cash_withdrawal": (
        "My cash withdrawal was declined|The ATM rejected my withdrawal|"
        "The cash machine will not let me withdraw|"
        "Unable to take money out of an ATM|ATM withdrawal refused|"
        "I have enough money but the cash withdrawal is denied|"
        "I cannot withdraw cash"
    ),
    "declined_transfer": (
        "My bank transfer was declined|Why was my transfer rejected|"
        "A transfer was refused by the bank|Money transfer not authorised|"
        "International transfer declined|The transfer was denied|"
        "My transfer has been blocked"
    ),
    "direct_debit_payment_not_recognised": (
        "I do not recognise a direct debit|Unknown direct debit on my account|"
        "I did not authorise this direct debit payment|"
        "There is a strange direct debit on my statement|"
        "An unfamiliar company took a direct debit|Unauthorised direct debit"
    ),
    "disposable_card_limits": (
        "What are the limits of a disposable virtual card|"
        "How many disposable cards can I have|"
        "Can I use a disposable card more than once|"
        "Where can I use a disposable virtual card|"
        "Can I use a disposable card for subscriptions|"
        "Restrictions on single use cards|How does a disposable card work|"
        "Disposable virtual card payment limit"
    ),
    "edit_personal_details": (
        "How do I change my personal details|Update my address|"
        "Change the phone number on my account|I have a new email address|"
        "My name has changed|Correct my date of birth|"
        "Edit my profile information|I moved house and need to update my address|"
        "The name on my account is wrong"
    ),
    "exchange_charge": (
        "Is there a fee to exchange currencies|Currency conversion commission|"
        "Why was I charged for exchanging money|"
        "Do you charge for converting dollars to euros|"
        "Weekend currency exchange markup|Foreign exchange fees|"
        "Does exchanging currencies in the app cost money"
    ),
    "exchange_rate": (
        "What exchange rate do you use|How are currency exchange rates calculated|"
        "What is the current euro exchange rate|Do you use the interbank rate|"
        "Where can I see the exchange rate|Is the exchange rate live|"
        "What rate will I get when converting currencies"
    ),
    "exchange_via_app": (
        "How do I exchange money in the app|"
        "Convert dollars to euros in my account|Can I exchange currencies|"
        "Where is the exchange function|Change my pounds into dollars|"
        "How to convert my balance to another currency|"
        "Buy foreign currency in the application"
    ),
    "extra_charge_on_statement": (
        "There is an extra small charge on my statement|"
        "Why was I charged one pound|An extra one euro payment appeared|"
        "What is this small verification charge|"
        "A small amount was taken when I added a card|"
        "Why is there an extra dollar charge|Unexpected small card authorisation charge"
    ),
    "failed_transfer": (
        "My transfer failed|An unsuccessful bank transfer|"
        "Why did my transfer fail|Error when making a transfer|"
        "I cannot send a bank transfer|The transfer did not work|"
        "My transfer was returned to my account|"
        "The bank transfer bounced back|Problem sending money"
    ),
    "fiat_currency_support": (
        "Which currencies can I hold|What currencies do you support|"
        "Can I have a dollar account|Supported fiat currencies|"
        "Can I hold several currencies in my account|"
        "Open a balance in euros|Can I keep money in yen|"
        "How many currencies are available|Which currencies can I exchange"
    ),
    "get_disposable_virtual_card": (
        "How can I get a disposable virtual card|"
        "Create a single use virtual card|Where do I find disposable cards|"
        "Order a disposable card|I want a temporary virtual card|"
        "How do I generate a new one time card|Get a disposable card for online shopping"
    ),
    "get_physical_card": (
        "How can I get a physical card|I need a real card|"
        "Where do I get a plastic debit card|Can I have a physical card|"
        "Is a physical card included with my account|"
        "How do I obtain an actual card|Do I need a physical card"
    ),
    "getting_spare_card": (
        "Can I get a spare card|I would like an additional card|"
        "Can I have two physical cards|Order a second card|"
        "Get a backup debit card|How many cards can I have|"
        "I need another card for my account|Can I get an extra card for my wife"
    ),
    "getting_virtual_card": (
        "How do I get a virtual card|Create a virtual debit card|"
        "Where is my virtual card|I would like a digital card|"
        "Can I get a card for online purchases only|"
        "Order another virtual card|View the details of my virtual card|"
        "What is a virtual card"
    ),
    "lost_or_stolen_card": (
        "I lost my card|My card has been stolen|I cannot find my debit card|"
        "My wallet was stolen with my card inside|"
        "Block a missing card|I misplaced my card|"
        "Replace a lost card|Someone stole my handbag and cards|"
        "I left my card somewhere"
    ),
    "lost_or_stolen_phone": (
        "I lost my phone|My mobile phone was stolen|"
        "Someone stole my smartphone|I cannot find my phone|"
        "My phone with the banking app is missing|"
        "How do I protect my account after losing my phone|"
        "My phone was stolen and I cannot access the app"
    ),
    "order_physical_card": (
        "I want to order a physical card|How do I order a physical card|"
        "Order a debit card|Where can I order a plastic card|"
        "How to place an order for a new card|"
        "I cannot order a physical card|Apply for a physical debit card"
    ),
    "passcode_forgotten": (
        "I forgot my passcode|Reset my app password|"
        "I cannot remember my login code|I forgot my account password|"
        "Cannot log in because I forgot the PIN|"
        "How do I recover access to my account|"
        "Forgot the four digit code for the application|My login password does not work"
    ),
    "pending_card_payment": (
        "My card payment is pending|Why is a purchase still processing|"
        "A card transaction has not completed|How long will a card payment be pending|"
        "Money is held for a card payment|Pending merchant transaction|"
        "The payment is stuck on pending|A payment is showing as reserved"
    ),
    "pending_cash_withdrawal": (
        "My cash withdrawal is pending|ATM transaction still processing|"
        "Why does a withdrawal show pending|"
        "A cash withdrawal has not completed|"
        "The money I took out is still shown as pending|"
        "How long does an ATM withdrawal stay pending"
    ),
    "pending_top_up": (
        "My top up is pending|Why is adding money still processing|"
        "A card top up is stuck|How long does a pending top up take|"
        "I added money by card but it has not appeared|"
        "My top up has not completed|"
        "The balance is unchanged after a debit card top up"
    ),
    "pending_transfer": (
        "My bank transfer is pending|A transfer is still processing|"
        "Why is my transfer stuck|The bank transfer is on hold|"
        "How long will a transfer stay pending|"
        "My international transfer has not completed|Transfer status is awaiting processing"
    ),
    "pin_blocked": (
        "My PIN is blocked|Too many incorrect PIN attempts|"
        "I entered the wrong PIN three times|How do I unblock my PIN|"
        "PIN attempts exceeded|My card is locked after entering the PIN incorrectly|"
        "Reset the PIN attempt counter|I have run out of PIN tries"
    ),
    "receiving_money": (
        "How can someone send me money|Can I receive money from a friend|"
        "Can my salary be paid into my account|"
        "Can another person transfer money to me|"
        "Receive payments from my employer|"
        "Can my parents send money to my account|"
        "How do I request money from another user|Can I get paid into Revolut"
    ),
    "refund_not_showing_up": (
        "My refund has not arrived|A refund is not showing in my account|"
        "The merchant refunded me but I have not received it|"
        "Where is my refund|How long does a refund take|"
        "I am waiting for a refund to be credited|"
        "The shop sent a refund days ago and my balance is unchanged|"
        "My refund is pending"
    ),
    "request_refund": (
        "How do I request a refund|Can I get my money back for a purchase|"
        "I want to dispute a card payment|Start a chargeback|"
        "The merchant will not give me a refund|"
        "I paid for something I never received|"
        "How can I cancel a card payment|"
        "I was charged the wrong amount and want a refund"
    ),
    "reverted_card_payment": (
        "My card payment was reverted|Why was my purchase reversed|"
        "Money from a card payment came back to my account|"
        "The merchant payment was automatically cancelled|"
        "My completed payment is now reverted|"
        "A card transaction was reversed but I got the goods|"
        "Why was my purchase money returned"
    ),
    "supported_cards_and_currencies": (
        "Which cards can I use to top up|What top up currencies are supported|"
        "Can I add money using an American Express card|"
        "Can I top up with a prepaid card|Do you accept credit cards for funding|"
        "Is my debit card supported|Can I top up in dollars|"
        "Can I use a foreign bank card to add money|"
        "Supported card types and currencies for top ups"
    ),
    "terminate_account": (
        "How do I close my account|Delete my account permanently|"
        "I want to terminate my account|Cancel my Revolut account|"
        "I no longer want to use this service|"
        "Deactivate my account|Remove my banking account"
    ),
    "top_up_by_bank_transfer_charge": (
        "Is there a charge for topping up by bank transfer|"
        "Fee for incoming bank transfers|"
        "Does transferring money into my account cost anything|"
        "Charged a fee when adding money by wire transfer|"
        "Bank transfer deposit charges|"
        "Will my bank charge me for transferring to Revolut"
    ),
    "top_up_by_card_charge": (
        "Is there a fee for topping up by card|"
        "Why was I charged for adding money with my debit card|"
        "Credit card top up fees|"
        "Adding funds with a card cost extra|"
        "Commission on a card top up|Is topping up by card free"
    ),
    "top_up_by_cash_or_cheque": (
        "Can I top up with cash|How do I deposit a cheque|"
        "Can I pay cash into my account|"
        "Can I add money using a check|Do you accept cash deposits|"
        "Can I deposit cash at a bank branch|"
        "How can I cash a cheque into my account"
    ),
    "top_up_failed": (
        "My top up failed|Why was my card top up declined|"
        "I cannot add money with my card|"
        "Adding money to my account does not work|"
        "Unsuccessful top up|My bank rejected the top up|"
        "Error when trying to top up|The app will not let me add funds"
    ),
    "top_up_limits": (
        "What is my top up limit|How much can I add to my account|"
        "Maximum amount for a card top up|Is there a minimum top up|"
        "Increase my top up allowance|"
        "How many times can I top up each day|"
        "Why have I reached my funding limit|Daily and monthly deposit limits"
    ),
    "top_up_reverted": (
        "My top up was reverted|The top up money went back to my bank|"
        "Why was my card top up reversed|"
        "The money I added disappeared|Top up refunded to the original card|"
        "My deposit was returned|"
        "A completed top up was cancelled and the funds sent back"
    ),
    "topping_up_by_card": (
        "How do I top up by card|Add money using my debit card|"
        "How can I fund my account with a credit card|"
        "Can I use someone else's card to top up|"
        "Can I add funds using a bank card|"
        "Where is the top up option in the app|"
        "How do I add money to my balance|Save a card for topping up"
    ),
    "transaction_charged_twice": (
        "I was charged twice for one transaction|"
        "A payment appears twice on my statement|"
        "The same purchase was charged two times|"
        "Duplicate card transaction|I paid once but got charged double|"
        "There are two identical payments|The merchant took my money twice"
    ),
    "transfer_fee_charged": (
        "Why was I charged a transfer fee|"
        "Does sending money abroad cost anything|"
        "International bank transfer charges|"
        "The recipient received less money than I sent|"
        "Commission for sending a bank transfer|"
        "Unexpected charge for transferring money|Are outgoing transfers free"
    ),
    "transfer_into_account": (
        "How do I transfer money into my account|"
        "What are my bank account details for a transfer|"
        "Where can I find my IBAN and BIC|"
        "Can I transfer money from another bank account|"
        "How do I make a bank transfer|"
        "Move money between my bank and Revolut|"
        "How to transfer money to a bank account|"
        "What sort code and account number do I use"
    ),
    "transfer_not_received_by_recipient": (
        "The recipient has not received my transfer|"
        "I sent money but my friend did not get it|"
        "The transfer is complete but the beneficiary has no money|"
        "Money sent to another bank account has not arrived|"
        "Where is the transfer I sent to someone|"
        "My outgoing bank transfer has not reached the destination|"
        "The receiving bank cannot find my transfer"
    ),
    "transfer_timing": (
        "How long does a bank transfer take|When will my transfer arrive|"
        "How fast are international transfers|"
        "Do bank transfers go through on weekends|"
        "How many days for money to reach another bank|"
        "When will the recipient receive the money|"
        "Are bank transfers instant|Transfer processing times"
    ),
    "unable_to_verify_identity": (
        "I cannot verify my identity|My identity verification failed|"
        "The app will not accept my identity document|"
        "My passport photo was rejected|"
        "Identity verification is stuck|"
        "Trouble uploading my identification|"
        "My selfie is not accepted|"
        "My account verification has been pending for days"
    ),
    "verify_my_identity": (
        "How do I verify my identity|What documents do I need to verify my account|"
        "Where do I upload my passport|"
        "Can I use a driving licence for identification|"
        "How to complete identity verification|"
        "Which identity documents are accepted|"
        "Can you check whether my identity is verified"
    ),
    "verify_source_of_funds": (
        "Why do you need to verify my source of funds|"
        "What documents prove the source of my money|"
        "How do I verify my income|"
        "Proof of salary and source of wealth|"
        "You asked for my payslips and bank statements|"
        "Why do you need information about my employment|"
        "Verify where my money comes from"
    ),
    "verify_top_up": (
        "How do I verify my top up|"
        "Where do I find the verification code for a top up|"
        "Verify the bank card I used to add money|"
        "I cannot verify my deposit card|"
        "What is the card top up authentication code|"
        "Do I need to verify the card used for topping up|"
        "Card ownership verification for adding funds"
    ),
    "virtual_card_not_working": (
        "My virtual card is not working|"
        "My virtual card payment was declined|"
        "The digital card is rejected online|"
        "I cannot pay with my virtual card|"
        "Virtual card details do not work|"
        "A website will not accept my virtual debit card"
    ),
    "visa_or_mastercard": (
        "Will I get a Visa or Mastercard|"
        "Can I choose between Visa and Mastercard|"
        "Do you issue Visa cards|"
        "I want a Mastercard instead of Visa|"
        "What card brand will I receive|"
        "Are your debit cards Visa or MasterCard|"
        "Can I change my card from Mastercard to Visa"
    ),
    "why_verify_identity": (
        "Why do I need to verify my identity|"
        "Why do you need my passport|"
        "Can I use the account without identity verification|"
        "Is identity verification compulsory|"
        "Why must I provide identification|"
        "Why do you ask for a photo of my ID|"
        "Why is it necessary to verify my account"
    ),
    "wrong_amount_of_cash_received": (
        "The ATM gave me the wrong amount of cash|"
        "I withdrew money but no cash came out|"
        "The cash machine dispensed less than I requested|"
        "My account was debited but I did not receive any cash|"
        "I asked for one hundred but only received fifty|"
        "The ATM shortchanged me|"
        "Cash machine did not dispense the money|"
        "The amount withdrawn differs from the cash received"
    ),
    "wrong_exchange_rate_for_cash_withdrawal": (
        "Wrong exchange rate for a cash withdrawal|"
        "The ATM used a bad conversion rate|"
        "I withdrew cash abroad and the exchange rate was incorrect|"
        "Cash withdrawal currency conversion is wrong|"
        "The rate used when taking money out was unfair|"
        "Why was my foreign cash withdrawal converted at a different rate"
    ),
}


def _extract_text(state):
    if isinstance(state, str):
        return state
    if state is None:
        return ""
    if isinstance(state, dict):
        for key in (
            "text", "utterance", "customer_message", "user_message",
            "customer_query", "query", "sentence", "message", "input_text",
            "input", "content", "description", "prompt",
        ):
            if key in state and state[key] is not None:
                value = _extract_text(state[key])
                if value:
                    return value
        for key in ("messages", "conversation", "history"):
            if key in state:
                seq = state[key]
                if isinstance(seq, (list, tuple)):
                    users = [
                        item for item in seq
                        if isinstance(item, dict)
                        and item.get("role", item.get("speaker", "")) in
                        ("user", "customer", "human")
                    ]
                    if users:
                        return _extract_text(users[-1])
                value = _extract_text(seq)
                if value:
                    return value
        for key in ("state", "data", "payload", "customer", "request"):
            if key in state:
                value = _extract_text(state[key])
                if value:
                    return value
        parts = []
        for key, value in state.items():
            if key not in (
                "role", "speaker", "id", "answer", "label", "category",
                "question_name", "intent", "metadata",
            ):
                part = _extract_text(value)
                if part:
                    parts.append(part)
        return " ".join(parts)
    if isinstance(state, (list, tuple)):
        return " ".join(filter(None, (_extract_text(v) for v in state)))
    if isinstance(state, (int, float, bool)):
        return str(state)
    return ""


def _normalize(text):
    text = unicodedata.normalize("NFKC", text).lower()
    text = text.replace("’", "'").replace("`", "'")
    substitutions = (
        (r"\bcan't\b", "cannot"),
        (r"\bwon't\b", "will not"),
        (r"\bshan't\b", "shall not"),
        (r"\bain't\b", "is not"),
        (r"\b([a-z]+)n't\b", r"\1 not"),
        (r"\bi'm\b", "i am"),
        (r"\b([a-z]+)'ve\b", r"\1 have"),
        (r"\b([a-z]+)'ll\b", r"\1 will"),
        (r"\b([a-z]+)'re\b", r"\1 are"),
        (r"\bit's\b", "it is"),
        (r"\bwhat's\b", "what is"),
        (r"\bwhere's\b", "where is"),
        (r"\bthere's\b", "there is"),
        (r"\btop[\s_-]?(?:up|ups)\b", "top up"),
        (r"\btopp(?:ing|ed)[\s_-]*up\b", "top up"),
        (r"\bmaster[\s-]+card\b", "mastercard"),
        (r"\bgooglepay\b", "google pay"),
        (r"\bapplepay\b", "apple pay"),
        (r"\bwithdrawl(?:s)?\b", "withdrawal"),
        (r"\breciev(?:e|ed|ing)\b", "receive"),
        (r"\brecipent\b", "recipient"),
    )
    for pattern, replacement in substitutions:
        text = re.sub(pattern, replacement, text)
    text = re.sub(r"[_/-]", " ", text)
    text = re.sub(r"[^a-z0-9£€$'?., ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


_STOP = set("""
a an the i me my mine we us our ours you your yours he him his she her
it its they them their this that these those is am are was were be been being
do does did have has had having of for to from in on at by with as and or
so please can could would should will may might shall just really very some
any about there here then than also now much many want need like know tell
help thanks thank thankyou hi hello hey get got getting make made
""".split())

_WORD_MAP = {
    "recognise": "recognize", "recognised": "recognize",
    "recognized": "recognize", "recognizing": "recognize",
    "unrecognised": "unknown", "unrecognized": "unknown",
    "unfamiliar": "unknown",
    "unauthorised": "unauthorized",
    "authorisation": "authorization",
    "topped": "top", "topping": "top",
    "withdrawals": "withdraw", "withdrawal": "withdraw",
    "withdrawing": "withdraw", "withdrawn": "withdraw", "withdrew": "withdraw",
    "transferred": "transfer", "transferring": "transfer", "transfers": "transfer",
    "received": "receive", "receiving": "receive", "receives": "receive",
    "arrived": "arrive", "arriving": "arrive", "arrival": "arrive",
    "payments": "payment", "paying": "payment", "paid": "payment", "pay": "payment",
    "purchases": "purchase", "purchased": "purchase",
    "buy": "purchase", "bought": "purchase", "buying": "purchase",
    "shops": "merchant", "shop": "merchant", "store": "merchant",
    "retailer": "merchant",
    "charges": "charge", "charged": "charge", "charging": "charge",
    "fees": "fee", "commission": "fee", "surcharge": "fee",
    "costs": "cost", "costing": "cost",
    "declined": "decline", "rejected": "decline", "refused": "decline",
    "denied": "decline", "reject": "decline", "refuse": "decline",
    "failed": "fail", "failing": "fail", "unsuccessful": "fail",
    "working": "work", "works": "work", "worked": "work",
    "stopped": "stop",
    "forgot": "forget", "forgotten": "forget",
    "expired": "expire", "expires": "expire", "expiring": "expire",
    "expiry": "expire", "expiration": "expire",
    "activated": "activate", "activation": "activate", "activating": "activate",
    "currencies": "currency",
    "converted": "convert", "converting": "convert", "conversion": "convert",
    "exchanging": "exchange", "exchanged": "exchange",
    "verification": "verify", "verified": "verify", "verifying": "verify",
    "identification": "identity", "id": "identity",
    "cheques": "cheque", "checks": "cheque",
    "smartphone": "phone", "mobile": "phone",
    "cashpoint": "atm", "cashpoints": "atm", "atms": "atm",
    "automatically": "automatic", "auto": "automatic",
    "cancelled": "cancel", "canceled": "cancel", "cancelling": "cancel",
    "cancellation": "cancel",
    "reverted": "revert", "reversed": "revert", "reversal": "revert",
    "returned": "return",
    "delivered": "delivery", "delivering": "delivery", "shipping": "delivery",
    "ordered": "order", "ordering": "order",
    "additional": "spare", "backup": "spare",
    "digital": "virtual",
    "minimum": "minimum", "maximum": "maximum",
    "blocked": "block", "blocking": "block",
    "stolen": "steal", "stole": "steal", "theft": "steal",
    "misplaced": "lost", "losing": "lost", "lose": "lost",
    "swallowed": "swallow", "retained": "swallow",
    "register": "signup", "registration": "signup",
    "residents": "resident", "residing": "resident",
    "accepted": "accept", "accepts": "accept",
    "supported": "support", "supports": "support",
    "details": "detail",
}


def _tokens(text):
    text = _normalize(text)
    text = re.sub(r"\bcash (?:machine|point)s?\b", "atm", text)
    text = re.sub(r"\b(?:single|one) (?:time|use)\b", "disposable", text)
    text = re.sub(r"\b(?:log in|sign in)\b", "login", text)
    words = []
    for word in re.findall(r"[a-z]+|[0-9]+", text):
        if word in _STOP:
            continue
        if word in _WORD_MAP:
            word = _WORD_MAP[word]
        elif len(word) > 5 and word.endswith("ies"):
            word = word[:-3] + "y"
        elif len(word) > 5 and word.endswith("s") and not word.endswith(("ss", "ous")):
            word = word[:-1]
        words.append(word)
    features = Counter(words)
    for a, b in zip(words, words[1:]):
        features[a + ":" + b] += 0.65
    return features


def _build_lexicon():
    raw = []
    frequency = Counter()
    for label, phrases in _PHRASES.items():
        sentences = [label.replace("_", " ")] + phrases.split("|")
        for sentence in sentences:
            tokens = _tokens(sentence)
            raw.append((label, tokens))
            frequency.update(tokens.keys())
    count = len(raw)
    weights = {
        word: 1.0 + math.log((count + 1.0) / (freq + 1.0))
        for word, freq in frequency.items()
    }
    documents = []
    for label, tokens in raw:
        vector = {w: min(n, 2.0) * weights[w] for w, n in tokens.items()}
        norm = math.sqrt(sum(v * v for v in vector.values())) or 1.0
        documents.append((label, vector, norm))
    return weights, documents


_IDF, _DOCUMENTS = _build_lexicon()


def _lexical_scores(text):
    tokens = _tokens(text)
    vector = {
        w: min(n, 2.0) * _IDF[w]
        for w, n in tokens.items() if w in _IDF
    }
    norm = math.sqrt(sum(v * v for v in vector.values())) or 1.0
    best = {label: 0.0 for label in _PHRASES}
    second = {label: 0.0 for label in _PHRASES}
    for label, doc, doc_norm in _DOCUMENTS:
        dot = sum(value * vector.get(word, 0.0) for word, value in doc.items())
        similarity = dot / (norm * doc_norm)
        if similarity > best[label]:
            second[label] = best[label]
            best[label] = similarity
        elif similarity > second[label]:
            second[label] = similarity
    return {label: 7.0 * best[label] + second[label] for label in _PHRASES}


def predict(state):
    text = _normalize(_extract_text(state))
    literal = re.sub(r"[^a-z0-9 ]", " ", text)
    literal = re.sub(r"\s+", " ", literal).strip()
    for label in _PHRASES:
        if literal == label.replace("_", " "):
            return {"answer": label}

    scores = _lexical_scores(text)

    def has(pattern):
        return re.search(pattern, text) is not None

    def add(label, amount):
        scores[label] += amount

    card = has(r"\b(?:cards?|plastic|debit|credit)\b")
    virtual = has(r"\b(?:virtual|digital|non physical|online only)\b")
    disposable = has(
        r"\bdisposable\b|\b(?:single|one)[ -](?:use|time)\b|"
        r"\btemporary (?:virtual )?card\b"
    )
    atm = has(
        r"\b(?:atms?|cash ?points?|cash machines?|withdraw\w*|withdrew)\b|"
        r"\b(?:take|taking|taken|took|get|getting|got) (?:some |any |the |my )?"
        r"(?:cash|money) out\b|"
        r"\b(?:get|getting|obtain|access) cash\b"
    )
    topup = has(
        r"\btop up\b|\breload\w*\b|\brecharge\b|"
        r"\badd(?:ing|ed|s)? (?:some |more |any |extra |the |my |new )?"
        r"(?:money|funds|cash|balance)\b|"
        r"\bload(?:ed|ing)? (?:money|funds|cash)\b|"
        r"\bfund(?:ing|ed)? (?:my |the |an? |your )?account\b|"
        r"\b(?:card|debit|credit) deposit\b|"
        r"\bdeposit(?:ing)? (?:money |funds )?(?:using|with|by) (?:a |my )?"
        r"(?:debit |credit |bank )?card\b"
    )
    bank = has(r"\b(?:bank|wire|swift|sepa|ach|bacs|iban|bic|sort code)\b")
    transfer = has(
        r"\btransfer\w*\b|\bremittance\b|\bwire\b|"
        r"\b(?:send|sending|sent|remit)(?: .{0,35})?\b(?:money|funds|payment)\b|"
        r"\b(?:bank|international|overseas|cross border) payments?\b|"
        r"\b(?:money|funds) (?:i |we )?(?:sent|sending)\b"
    )
    cheque = has(
        r"\bcheques?\b|\b(?:a|my|the|by|via|using|with) check\b|"
        r"\bchecks?\b.{0,30}\b(?:deposit|cash|clear|account)\b|"
        r"\b(?:deposit|cash|clear)(?:ing|ed)?\b.{0,30}\bchecks?\b"
    )
    cash_deposit = has(
        r"\bcash deposit\b|\bdeposit\w*\b.{0,35}\bcash\b|"
        r"\bcash\b.{0,35}\b(?:deposit|top up|into (?:my |the |an? )?account)\b|"
        r"\btop up\b.{0,40}\b(?:cash|notes|coins)\b|"
        r"\b(?:add|pay|paying|paid|put|putting)\b.{0,15}\bcash\b.{0,35}\baccount\b"
    )
    deposit = has(r"\bdeposit\w*\b|\bpaid in\b|\bpay in\b")
    cash_or_cheque = cheque or cash_deposit

    purchase = has(
        r"\b(?:payments?|purchases?|purchased|merchant|retailer|shopping|shop|"
        r"bought|buying|paid|paying|transaction|transactions|charged)\b"
    )
    retail = has(
        r"\b(?:merchant|retailer|restaurant|supermarket|shop|store|shopping|"
        r"purchase|purchased|bought|online payment|card payment|card transaction)\b"
    )
    pending = has(
        r"\bpending\b|\bprocessing\b|\bin progress\b|\bon hold\b|"
        r"\bstuck\b|\bqueued\b|\bawaiting\b|\breserved\b|"
        r"\bnot (?:yet )?completed\b|\buncompleted\b|\bheld\b"
    )
    declined = has(
        r"\b(?:declin\w*|reject\w*|refus\w*|denied|deny|blocked)\b|"
        r"\bnot (?:being )?(?:accepted|allowed|authori[sz]ed|approved)\b|"
        r"\b(?:will|would|does|did) not (?:go through|accept|let me)\b"
    )
    failed = has(
        r"\bfail\w*\b|\bunsuccessful\b|\berrors?\b|\bproblems?\b|\btrouble\b|"
        r"\b(?:cannot|unable|could not)\b|"
        r"\b(?:does|did|is|are|will|would|has) not (?:work\w*|go through|let|allow|gone through)\b|"
        r"\bno longer work\w*\b|\bstopped work\w*\b|\bnot working\b|"
        r"\bnot able\b|\bwill not\b"
    )
    missing = has(
        r"\b(?:missing|delayed|overdue|disappeared|unchanged)\b|"
        r"\b(?:not|never|yet to|still not)\b.{0,35}"
        r"\b(?:receiv\w*|arriv\w*|appear\w*|show\w*|credit\w*|updat\w*|"
        r"reflect\w*|reach\w*|clear\w*|come|came|got|get|there)\b|"
        r"\bstill (?:waiting|nothing|no)\b|\bwhere (?:is|are)\b|"
        r"\bhas not come\b|\bhave not come\b|\bno (?:money|funds|cash)\b|"
        r"\bbalance (?:is |stayed |remains? )?(?:the same|zero|0)\b|"
        r"\bnot (?:in|on) my (?:account|balance)\b"
    )
    fee = has(
        r"\b(?:fees?|charges?|costs?|costing|commission|surcharge|markup|"
        r"mark up|pricing|price)\b|"
        r"\bcharged\b.{0,20}\b(?:extra|more|additional|unexpected)\b|"
        r"\b(?:extra|additional|unexpected)\b.{0,20}\bcharged\b|"
        r"\b(?:extra|additional) (?:money|amount|payment)\b|"
        r"\bovercharg\w*\b|\bfree\b"
    )
    timing = has(
        r"\bhow (?:long|soon|fast|quickly)\b|\bwhen\b|\btime\b|"
        r"\b(?:days|hours|weeks|duration|eta|instant|instantly|immediately)\b|"
        r"\b(?:weekend|weekends|working day|business day|bank holiday)\b"
    )
    limit = has(
        r"\blimits?\b|\blimited\b|\bmaximum\b|\bminimum\b|\bmax\b|\bmin\b|"
        r"\bhow (?:much|many|often)\b|\bcap\b|\brestrictions?\b|\ballowance\b|"
        r"\bnumber of\b|\bmore than\b"
    )
    reverted = has(
        r"\brevert\w*\b|\brevers(?:ed|al)\b|\bbounced\b|\breturned\b|"
        r"\bsent back\b|\bwent back\b|\bcome back\b|\bcame back\b|"
        r"\btaken back\b|\bput back\b|\brefunded\b"
    )
    cancel = has(r"\b(?:cancel\w*|recall|undo|abort|reverse|stop|halt)\b")
    unrecognized = has(
        r"\bunrecogni[sz]\w*\b|\bunknown\b|\bunfamiliar\b|\bunauthori[sz]ed\b|"
        r"\bfraudulent\b|\bdo not (?:recogni[sz]e|recall|remember|know)\b|"
        r"\bdoes not (?:look familiar|belong to me)\b|"
        r"\b(?:did|have|was|were) not\b.{0,25}"
        r"\b(?:make|made|authori[sz]e|approve|withdraw|purchase|pay|use|using|buy)\b|"
        r"\bnever\b.{0,25}\b(?:made|used|bought|paid|visited|been|withdrew|withdrawn)\b|"
        r"\bnot (?:mine|me|my transaction|my purchase|my payment)\b|"
        r"\bsome(?:one|body)(?: else)?\b.{0,35}\b(?:used|using|made|spent|withdrew|took|paid)\b|"
        r"\bwithout (?:my )?(?:permission|consent|knowledge|authorization)\b|"
        r"\bno idea\b|\bnot aware\b|\bstrange (?:payment|transaction|charge)\b"
    )
    currency = has(
        r"\bcurrenc\w*\b|\bforex\b|\bforeign exchange\b|"
        r"\b(?:euros?|dollars?|pounds?|yen|rupees?|zloty|francs?|"
        r"usd|eur|gbp|aud|cad|chf|jpy|ron|pln|nzd|huf|inr|brl|sek|nok|dkk)\b"
    )
    exchange = has(r"\b(?:exchang\w*|convert\w*|conversion|forex|fx)\b")
    rate = has(r"\brates?\b") and (exchange or currency or atm or purchase)
    wrong = has(
        r"\b(?:wrong|incorrect|inaccurate|unfair|bad|poor|awful|different|"
        r"higher|lower|worse|discrepancy|excessive|outrageous)\b|"
        r"\btoo (?:high|low|much)\b|\bnot (?:right|correct|match)\b|"
        r"\bdoes not match\b|\bovercharg\w*\b"
    )
    verification = has(
        r"\bverif\w*\b|\bauthenticat\w*\b|\bvalidation\b|\bvalidate\b|"
        r"\bconfirm (?:my |the )?(?:identity|card|account|top up)\b"
    )
    identity = has(
        r"\bidentit\w*\b|\bidentification\b|\bid\b|\bpassport\b|"
        r"\b(?:driving|driver|drivers|driver's) licen[cs]e\b|"
        r"\bselfie\b|\bkyc\b|\bproof of (?:address|residen\w*)\b|"
        r"\bpersonal documents?\b"
    )
    incoming = has(
        r"\b(?:into|to) (?:my |the |your |a |an )?"
        r"(?:revolut|this|own) (?:bank )?account\b|"
        r"\b(?:into|to) (?:my |your )?revolut\b|"
        r"\binto (?:my |the |your )?(?:bank )?account\b|"
        r"\bfrom (?:my |a |another |the |an external )?(?:other )?bank\b|"
        r"\bincoming\b|\bmy balance\b|\baccount (?:balance |has )?not\b|"
        r"\bbalance (?:has|is|was|did|does|stayed|remains?)\b|"
        r"\b(?:credited|credit) (?:to )?my account\b"
    )
    recipient = has(
        r"\b(?:recipient|beneficiar\w*|receiving bank|destination|payee)\b|"
        r"\b(?:my|a|the) (?:friend|mother|father|mum|mom|dad|brother|sister|"
        r"wife|husband|landlord|son|daughter|partner)\b|"
        r"\b(?:other|another) person\b|\bperson i (?:sent|paid)\b|"
        r"\bto (?:someone|somebody)\b|\btheir (?:bank )?account\b"
    )
    outgoing = recipient or has(
        r"\boutgoing\b|\boutbound\b|\bto (?:another|a different|an external) bank\b|"
        r"\bfrom (?:my )?revolut\b|\bto my (?:other |external )?bank account\b"
    )

    # Security, identity, account administration.
    if has(r"\bdirect debits?\b"):
        add("direct_debit_payment_not_recognised", 46 if unrecognized else 25)

    duplicated = has(
        r"\btwice\b|\bduplicate[ds]?\b|\bdouble charg\w*\b|\bcharged double\b|"
        r"\b(?:charged|debited|billed|paid)\b.{0,30}\b(?:two|2) times\b|"
        r"\b(?:two|2) (?:identical|same) (?:payments?|transactions?|charges?)\b|"
        r"\bsame (?:payment|transaction|purchase)\b.{0,30}\b(?:two|2)\b|"
        r"\bpayment\b.{0,25}\bduplicat\w*\b"
    )
    if duplicated and not has(r"\b(?:pin|password|passcode) (?:attempt|tries)\b"):
        add("transaction_charged_twice", 57)

    if has(
        r"\bswallow\w*\b|\b(?:ate|eaten|retained) (?:my |the |a )?card\b|"
        r"\bcard\b.{0,35}\b(?:stuck|trapped|retained)\b|"
        r"\b(?:atm|machine|cashpoint)\b.{0,40}\b(?:kept|keep|ate|eaten|took|retained)\b|"
        r"\b(?:atm|machine)\b.{0,45}\bnot\b.{0,15}\b(?:return|give|release|eject)\b|"
        r"\bcard\b.{0,25}\b(?:not come out|will not come out)\b"
    ) and (card or atm):
        add("card_swallowed", 68)

    lost = has(
        r"\blost\b|\bstolen\b|\bstole\b|\blosing\b|\bmisplac\w*\b|"
        r"\bmissing\b|\bcannot find\b|\bcan not find\b|\bcould not find\b|"
        r"\b(?:left|forgot) (?:my |the )?(?:card|phone|wallet|purse)\b|"
        r"\brobbed\b|\bpickpocket\w*\b"
    )
    phone = has(r"\b(?:phone|mobile|smartphone|iphone|handset|cellphone)\b")
    lost_phone = has(
        r"\b(?:lost|stolen|misplaced|missing|stole|losing)\b.{0,30}"
        r"\b(?:phone|mobile|smartphone|iphone|handset)\b|"
        r"\b(?:phone|mobile|smartphone|iphone|handset)\b.{0,35}"
        r"\b(?:lost|stolen|missing|misplaced|robbed)\b|"
        r"\bcannot find\b.{0,20}\b(?:phone|mobile)\b"
    )
    if lost_phone:
        add("lost_or_stolen_phone", 65)

    details_compromised = has(
        r"\b(?:compromis\w*|cloned|cloning|skimmed|skimming|hacked|hacking|"
        r"phishing|scammer|scammed|leaked)\b|"
        r"\b(?:card|bank)\b.{0,15}\b(?:details|information|number|credentials)\b"
        r".{0,35}\b(?:stolen|stole|exposed|taken|someone|shared)\b|"
        r"\b(?:someone|somebody|stranger)\b.{0,40}"
        r"\b(?:knows|has|obtained|got|access)\b.{0,30}\b(?:card|details|number)\b|"
        r"\bgave\b.{0,30}\bcard\b.{0,35}\b(?:scam|fraud|stranger|fake)\b"
    )
    if details_compromised:
        add("compromised_card", 58)
    elif has(r"\b(?:fraud|fraudster|fraudsters|suspicious)\b") and card and not purchase:
        add("compromised_card", 36)

    if lost and (card or has(r"\b(?:wallet|purse|handbag)\b")):
        if not details_compromised and not (lost_phone and not has(r"\b(?:wallet|purse)\b")):
            if not (has(r"\b(?:post|mail|delivery|shipping|ordered)\b") and not has(r"\bstolen\b")):
                add("lost_or_stolen_card", 59)
    if has(r"\b(?:freeze|block|secure)\b.{0,25}\b(?:my )?card\b") and not lost:
        add("compromised_card", 23)

    pin = has(r"\bpin\b|\bpins\b|\bpersonal identification number\b")
    login = has(
        r"\b(?:passcode|password|login|log in|sign in|log into|sign into|"
        r"access code|app code|security code)\b"
    )
    forgotten = has(
        r"\bforgot\w*\b|\bcannot remember\b|\bdo not remember\b|"
        r"\breset\b|\brecover\b|\blocked out\b|\blost\b"
    )
    pin_lock = has(
        r"\b(?:blocked|block|unblock|locked|unlock|exceeded|incorrect|wrong|"
        r"attempts|tries|tried|three|3|counter)\b"
    )
    if pin:
        add("change_pin", 20)
        if pin_lock and has(
            r"\b(?:blocked|locked|unblock|unlock|attempts|tries|three|3|counter|exceeded)\b"
        ):
            add("pin_blocked", 53)
        elif has(r"\b(?:change|reset|view|see|find|forgot|remember|choose|new|retrieve)\b"):
            add("change_pin", 27)
        if (login or has(r"\b(?:app|application|log)\b")) and forgotten:
            if not has(r"\b(?:card pin|pin (?:for|of|on) (?:my |the )?card)\b"):
                add("passcode_forgotten", 58)
    if login:
        add("passcode_forgotten", 21)
        if forgotten or failed or has(r"\b(?:change|wrong|incorrect)\b"):
            add("passcode_forgotten", 34)
    if has(r"\b(?:cannot|unable to)\b.{0,18}\b(?:access|log|sign)\b.{0,20}\baccount\b"):
        add("passcode_forgotten", 27)

    if has(
        r"\b(?:close|closing|delete|deleting|terminate|terminating|deactivate|"
        r"cancel|canceling|cancelling|shut down|remove)\b.{0,30}"
        r"\b(?:account|membership|profile)\b|"
        r"\baccount\b.{0,20}\b(?:closure|termination|deletion|closed)\b|"
        r"\bno longer\b.{0,25}\b(?:use|want|need)\b.{0,20}\b(?:revolut|account|service)\b"
    ):
        add("terminate_account", 57)

    personal = has(
        r"\b(?:address|surname|last name|first name|name|phone number|"
        r"mobile number|telephone number|email|e mail|date of birth|"
        r"birth date|birthday|personal details|profile|personal information)\b"
    )
    edit = has(
        r"\b(?:change|changing|changed|update|updating|edit|correct|amend|"
        r"wrong|incorrect|new|different|married|moved)\b"
    )
    if personal and edit and not identity:
        add("edit_personal_details", 48)
        if has(r"\b(?:delivery|shipping|card)\b") and has(r"\b(?:sent|delivered|arrived)\b"):
            add("edit_personal_details", -22)

    if has(
        r"\bage (?:limit|restriction|requirement)\b|\bminimum age\b|"
        r"\bhow old\b|\bunderage\b|\bminor\b|\bteen(?:ager|agers|age)?\b|"
        r"\bunder (?:18|eighteen|16|sixteen)\b|"
        r"\b(?:child|children|kid|kids)\b.{0,40}\b(?:account|card|join|sign)\b|"
        r"\b(?:account|card)\b.{0,35}\b(?:child|children|kid|kids)\b|"
        r"\b(?:years? old|age of)\b|"
        r"\b(?:i am|i'm) (?:1[0-7]|thirteen|fourteen|fifteen|sixteen|seventeen)\b"
    ):
        if not has(r"\bhow old (?:is|can|must|should) (?:my|the|a) card\b"):
            add("age_limit", 56)

    residence = has(
        r"\b(?:resident|residency|residence|reside|residing|live|living|"
        r"citizen|citizenship|nationality|nonresident)\b"
    )
    account_open = has(
        r"\b(?:open|opening|create|creating|register|registration|"
        r"sign up|signup|join|eligible|eligibility|available|availability|operate|offer)\b"
    )
    country_word = has(
        r"\bcountr(?:y|ies)\b|\b(?:usa|us|uk|europe|european|america|american|"
        r"united states|united kingdom|india|indian|canada|australia|"
        r"japan|china|brazil|germany|france|spain|italy|poland|switzerland|"
        r"russia|africa|asia|singapore|mexico|new zealand|romania|ireland)\b"
    )
    if residence and (account_open or country_word or has(r"\baccount\b")):
        add("country_support", 48)
    elif country_word and account_open and not has(r"\b(?:atm|exchange|currency|currencies)\b"):
        add("country_support", 36)
    if has(r"\b(?:supported|eligible|available) countries\b|\bwhich countries\b") and not (
        card or atm or currency or transfer
    ):
        add("country_support", 45)

    funds_proof = has(
        r"\bsource of (?:funds|money|income|wealth)\b|"
        r"\bproof of (?:funds|income|salary|earnings|wealth)\b|"
        r"\b(?:verify|verifying|verification|prove)\b.{0,30}"
        r"\b(?:income|earnings|salary|funds|wealth|employment)\b|"
        r"\b(?:payslips?|pay slips?|paystubs?|pay stubs?)\b|"
        r"\bwhere (?:my|the|your) money (?:comes?|came) from\b"
    )
    if funds_proof:
        add("verify_source_of_funds", 65)
    if verification and (topup or has(r"\b(?:funding card|deposit card|card ownership)\b")):
        add("verify_top_up", 61)
    elif verification and card and not identity and has(
        r"\b(?:code|statement|bank card|debit card|credit card|ownership)\b"
    ):
        add("verify_top_up", 48)

    identity_context = identity or (
        verification and has(r"\b(?:account|documents?|personal|myself|me)\b")
        and not topup and not funds_proof
    )
    if identity_context:
        add("verify_my_identity", 24)
        if verification:
            add("verify_my_identity", 7)
        if failed or declined or pending or has(
            r"\b(?:not verified|not accepted|taking so long|still waiting|"
            r"does not accept|will not accept|keeps asking|cannot upload|blurry|invalid)\b"
        ):
            add("unable_to_verify_identity", 48)
        if has(
            r"\bwhy\b|\b(?:necessary|required|compulsory|mandatory|obligatory)\b|"
            r"\bwithout\b.{0,25}\b(?:verif\w*|id|passport|identification)\b|"
            r"\b(?:have|need) to (?:verify|provide|show|submit|send)\b"
        ):
            add("why_verify_identity", 38)
            if has(r"\bwhy\b"):
                add("why_verify_identity", 11)
        if has(r"\bwhat\b.{0,20}\b(?:documents?|id|identification)\b|\bhow\b"):
            add("verify_my_identity", 8)

    # Card lifecycle and card products.
    if has(r"\b(?:activate|activating|activation|unactivated)\b"):
        add("activate_my_card", 51)
    elif has(r"\bnot (?:yet )?activated\b"):
        add("activate_my_card", 43)
    if has(r"\b(?:expiry|expiration|expired|expires|expiring|expire|renew|renewal)\b") and (
        card or not has(r"\b(?:passport|id|password|passcode)\b")
    ):
        add("card_about_to_expire", 57)

    if has(r"\b(?:apple pay|google pay|android pay|google wallet|apple wallet|g pay|gpay)\b"):
        add("apple_pay_or_google_pay", 55)
    elif has(r"\b(?:iphone|apple watch|smartwatch|phone)\b") and has(
        r"\b(?:pay|paying|payment|wallet|nfc)\b"
    ):
        add("apple_pay_or_google_pay", 34)

    contactless = has(r"\b(?:contactless|tap to pay|tap and go|paywave|paypass)\b") or (
        card and has(r"\b(?:tap|tapping|tapped|wave|waving)\b")
    )
    if contactless:
        add("contactless_not_working", 42)
        if failed or declined:
            add("contactless_not_working", 16)

    if card and has(
        r"\b(?:link|linking|linked|unlink|connect|connecting|attach|associate)\b|"
        r"\b(?:two|2|multiple|another) accounts?\b"
    ) and not has(r"\b(?:apple pay|google pay|wallet)\b"):
        add("card_linking", 45)
        if topup and not has(r"\blink\w*\b"):
            add("card_linking", -20)

    delivery = has(
        r"\b(?:delivery|deliver|delivered|arriv\w*|shipping|shipped|shipment|"
        r"courier|postage|mail|post|tracking|track|dispatch\w*)\b"
    )
    card_delivery = (card and (delivery or missing)) or (
        delivery and has(r"\b(?:ordered|order|plastic)\b")
    )
    if card_delivery and not (atm or topup or transfer or cheque or currency):
        if missing or has(
            r"\b(?:late|overdue|delayed|lost in|track|tracking|where is|where's)\b|"
            r"\b(?:ordered|sent|shipped)\b.{0,40}\b(?:ago|last week|last month)\b"
        ):
            add("card_arrival", 49)
        if timing or has(r"\b(?:estimate|estimated|express|expedited|rush|delivery options)\b"):
            add("card_delivery_estimate", 35)
        if not missing and not has(r"\b(?:late|overdue|tracking|track)\b"):
            add("card_delivery_estimate", 12)
        if has(r"\b(?:not arrived|not received|still waiting|has not come)\b"):
            add("card_arrival", 12)

    if disposable:
        add("get_disposable_virtual_card", 32)
        disposable_usage = has(
            r"\b(?:limits?|restrictions?|maximum|minimum|subscriptions?|"
            r"recurring|reuse|reusable|repeatedly|multiple|twice|once|atm)\b|"
            r"\bhow (?:many|much|often)\b|\bmore than\b|"
            r"\b(?:where|when) can\b|\bcan i (?:use|pay|withdraw)\b|"
            r"\bhow (?:do|does).{0,30}\bwork\b"
        )
        if disposable_usage:
            add("disposable_card_limits", 51)
        elif has(r"\b(?:get|create|order|generate|obtain|find|issue|want|need)\b"):
            add("get_disposable_virtual_card", 20)
        else:
            add("disposable_card_limits", 13)
    elif virtual:
        add("getting_virtual_card", 28)
        if failed or declined or has(r"\b(?:invalid|broken|not accepted)\b"):
            add("virtual_card_not_working", 56)
        elif has(r"\b(?:get|create|order|find|details|view|generate|want|need)\b"):
            add("getting_virtual_card", 16)

    spare = has(
        r"\b(?:spare|backup|back up|additional|extra|second|another) (?:physical |debit |bank )?cards?\b|"
        r"\b(?:two|2|multiple|several) (?:physical |debit |bank )?cards?\b|"
        r"\bhow many cards\b"
    )
    if spare and not virtual and not disposable and not has(r"\b(?:stolen|lost|expired)\b"):
        add("getting_spare_card", 48)

    physical_request = card and has(
        r"\b(?:get|obtain|acquire|request|order|ordering|apply|send me|want|need|"
        r"purchase|buy|physical|plastic|real|actual)\b"
    )
    if physical_request and not virtual and not disposable:
        add("get_physical_card", 13)
        if has(r"\b(?:physical|plastic|real|actual)\b"):
            add("get_physical_card", 13)
        if has(r"\b(?:order|ordering|place an order|apply for)\b"):
            add("order_physical_card", 32)
        elif has(r"\b(?:get|obtain|acquire|request|send me|want|need)\b"):
            add("get_physical_card", 12)

    visa = has(r"\bvisa\b")
    mastercard = has(r"\bmastercard\b")
    card_type_support = has(
        r"\b(?:amex|american express|maestro|prepaid|pre paid|diners|discover|"
        r"unionpay|jcb|credit cards?|foreign cards?|foreign bank card|"
        r"international cards?)\b|"
        r"\b(?:which|what) (?:types? of )?cards?\b|"
        r"\bcard types?\b"
    )
    supported = has(
        r"\b(?:support\w*|accept\w*|allow\w*|eligible|permitted|possible|"
        r"can i use|can i add|can i top up|can i hold|can i have)\b"
    )
    if (visa or mastercard) and not topup:
        add("visa_or_mastercard", 25)
        if (visa and mastercard) or has(
            r"\b(?:choose|choice|issue|issued|receive|instead|switch|brand|"
            r"provide|offer|prefer|change|get|order)\b"
        ):
            add("visa_or_mastercard", 24)
    if card_type_support and (supported or topup):
        add("supported_cards_and_currencies", 33)
    if topup and (currency or card_type_support or visa or mastercard) and supported:
        add("supported_cards_and_currencies", 20)

    acceptance = has(
        r"\b(?:where|everywhere|anywhere|which shops|which stores|which merchants|"
        r"accepted|accept|use abroad|use overseas|internationally)\b|"
        r"\b(?:can|could) i (?:use|pay)\b"
    )
    if card and not topup and not atm and not transfer:
        if acceptance and not declined and not failed:
            add("card_acceptance", 29)
            if has(r"\b(?:shops?|stores?|merchants?|abroad|overseas|countries|online|worldwide)\b"):
                add("card_acceptance", 13)
        if failed or has(r"\b(?:damaged|broken|faulty|malfunction|unreadable)\b"):
            add("card_not_working", 29)
        if has(r"\b(?:chip|magnetic strip|card reader|damaged|broken|faulty)\b"):
            add("card_not_working", 18)

    # Cash and cheque funding are separate from card funding and withdrawals.
    if cash_or_cheque:
        add("top_up_by_cash_or_cheque", 34)
        if missing or pending or has(r"\b(?:cleared|clearing)\b"):
            add("balance_not_updated_after_cheque_or_cash_deposit", 53)
        elif has(r"\b(?:can|how|possible|accept|deposit|add|top up)\b"):
            add("top_up_by_cash_or_cheque", 11)

    auto = has(
        r"\b(?:automatic|automatically|auto|recurring|scheduled|regular)\b|"
        r"\b(?:each|every) (?:day|week|month)\b|"
        r"\bwhen\b.{0,25}\b(?:balance|low|below|runs out)\b|"
        r"\bthreshold\b"
    )
    if topup and auto:
        add("automatic_top_up", 61)
    elif has(r"\bauto (?:reload|recharge|funding)\b|\bautomatic funding\b"):
        add("automatic_top_up", 58)

    if topup and not cash_or_cheque:
        bank_topup = bank and transfer and not has(
            r"\b(?:with|using|by|from) (?:my |a |the )?(?:debit |credit |bank )?card\b"
        )
        add("topping_up_by_card", 12 if not bank_topup else 0)
        if limit:
            add("top_up_limits", 43)
        if pending:
            add("pending_top_up", 47 if not bank_topup else 17)
        if missing and not bank_topup:
            add("pending_top_up", 30)
        if failed or declined:
            add("top_up_failed", 43 if not bank_topup else 18)
        if reverted or has(
            r"\b(?:money|funds|top up)\b.{0,35}\b(?:disappeared|gone back|taken away)\b"
        ):
            add("top_up_reverted", 52)
        if fee:
            add("top_up_by_bank_transfer_charge" if bank_topup else "top_up_by_card_charge", 46)
        if bank_topup and missing:
            add("balance_not_updated_after_bank_transfer", 45)
        if not (failed or declined or pending or missing or reverted or fee or limit):
            add("topping_up_by_card", 13 if not bank_topup else 0)
            if bank_topup:
                add("transfer_into_account", 30)

    if deposit and limit and not cash_or_cheque and not atm:
        add("top_up_limits", 32)

    # ATM events: distinguish a rejected request from a completed withdrawal
    # that dispensed the wrong amount.
    if atm:
        add("atm_support", 15)
        if unrecognized:
            add("cash_withdrawal_not_recognised", 61)
        if pending:
            add("pending_cash_withdrawal", 51)
        if declined or failed:
            add("declined_cash_withdrawal", 44)
        if fee:
            add("cash_withdrawal_charge", 45)
        if exchange or rate:
            add("wrong_exchange_rate_for_cash_withdrawal", 39)
            if wrong:
                add("wrong_exchange_rate_for_cash_withdrawal", 19)
        wrong_cash = has(
            r"\b(?:wrong|incorrect|different|less|fewer|short|partial)\b.{0,30}"
            r"\b(?:amount|cash|money|notes|received|dispensed)\b|"
            r"\b(?:cash|money|amount)\b.{0,30}\b(?:wrong|incorrect|less|different)\b|"
            r"\bshortchang\w*\b|"
            r"\b(?:no|not any|not enough|only some) cash\b|"
            r"\b(?:did|does|would|has) not\b.{0,20}\b(?:dispense|give|release|receive|come out)\b|"
            r"\b(?:cash|money)\b.{0,30}\b(?:not come out|never came out|did not come out)\b|"
            r"\bcharged\b.{0,45}\b(?:not receive|no cash|no money)\b|"
            r"\b(?:debited|deducted|taken)\b.{0,45}\b(?:no cash|no money|not receive)\b|"
            r"\b(?:requested|asked for|withdrew)\b.{0,40}\b(?:only|instead|but got|but received)\b"
        )
        if wrong_cash:
            add("wrong_amount_of_cash_received", 60)
        if has(
            r"\b(?:where|which|nearby|nearest|locate|find|supported|support|"
            r"locations|any atm|any cash|what atm)\b"
        ) and not (declined or failed or missing):
            add("atm_support", 24)
        if limit and not fee and not wrong_cash:
            add("atm_support", 13)

    # Transfers: incoming account funding versus money sent to a recipient.
    if transfer and not cash_or_cheque:
        add("transfer_into_account", 15)
        beneficiary_block = has(
            r"\bbeneficiar\w*\b.{0,40}\b(?:not allowed|not permitted|not supported|"
            r"blocked|prohibited|disallowed|cannot|denied|rejected)\b|"
            r"\b(?:not allowed|not permitted|not supported|blocked|unsupported)\b"
            r".{0,30}\b(?:beneficiar\w*|recipient|recipient bank)\b|"
            r"\brecipient\b.{0,30}\b(?:not allowed|not supported|not permitted)\b"
        )
        if beneficiary_block:
            add("beneficiary_not_allowed", 68)
        if has(r"\b(?:crypto|cryptocurrency|bitcoin)\b") and (
            declined or has(r"\b(?:can|allowed|possible)\b")
        ):
            add("beneficiary_not_allowed", 40)
        if cancel or has(
            r"\b(?:wrong|incorrect|mistaken)\b.{0,20}\b(?:account|recipient|beneficiary|person|details)\b|"
            r"\bsent\b.{0,30}\bby mistake\b"
        ):
            add("cancel_transfer", 52)
        if pending:
            add("pending_transfer", 49)
        if declined:
            add("declined_transfer", 49)
        if failed:
            add("failed_transfer", 38)
        if reverted:
            add("failed_transfer", 44)
        if fee:
            if (incoming or topup or deposit) and not outgoing:
                add("top_up_by_bank_transfer_charge", 49)
            else:
                add("transfer_fee_charged", 45)
        if has(
            r"\b(?:less|smaller|short|deducted|missing)\b.{0,30}\b(?:amount|money|received|sent|funds)\b|"
            r"\b(?:recipient|beneficiary)\b.{0,35}\b(?:less|short|smaller)\b|"
            r"\b(?:received|got)\b.{0,20}\bless\b"
        ) and outgoing and not has(r"\bnot received\b"):
            add("transfer_fee_charged", 38)
        if timing:
            add("transfer_timing", 31)
            if not missing and not pending and not failed and not declined:
                add("transfer_timing", 12)
        if missing:
            if recipient or outgoing:
                add("transfer_not_received_by_recipient", 46 if not pending else 24)
            elif incoming or bank or topup:
                add("balance_not_updated_after_bank_transfer", 45 if not pending else 24)
            else:
                add("transfer_not_received_by_recipient", 28)
                add("balance_not_updated_after_bank_transfer", 24)
        if has(r"\b(?:completed|complete|successful|sent successfully)\b") and missing and outgoing:
            add("transfer_not_received_by_recipient", 14)
        if incoming and not (missing or pending or failed or declined or fee):
            add("transfer_into_account", 13)

    if has(r"\b(?:iban|bic|swift code|sort code|routing number|account number|bank details)\b"):
        add("transfer_into_account", 31)
        if missing and transfer:
            add("transfer_into_account", -16)
    if bank and deposit and missing and not cash_or_cheque:
        add("balance_not_updated_after_bank_transfer", 45)

    receiving = has(
        r"\b(?:salary|wages|paycheck|pay cheque|paycheque|employer|payroll|"
        r"paid into|receive money|receiving money|receive payments|"
        r"receiving payments|request money)\b|"
        r"\b(?:someone|somebody|friend|parents|mother|father|person|people)\b"
        r".{0,45}\b(?:send|pay|transfer|give)\b.{0,25}\b(?:me|my account|to me)\b|"
        r"\b(?:send|transfer|pay)\b.{0,25}\b(?:me|to me)\b"
    )
    if receiving and not funds_proof:
        add("receiving_money", 34)
        if not (pending or missing or failed or declined or fee):
            add("receiving_money", 12)
    if has(r"\b(?:can|could|how)\b.{0,40}\b(?:other people|third part\w*|someone else|another person)\b") and (
        transfer or has(r"\b(?:receive|pay|fund)\b")
    ) and not topup:
        add("receiving_money", 40)

    # Purchases and card transaction states.
    card_transaction = not (atm or cash_or_cheque) and (
        purchase or card or has(r"\bstatement\b")
    )
    topup_is_background = topup and retail and has(
        r"\b(?:but|however|now)\b.{0,65}\b(?:payment|purchase|card|shop|pay)\b"
    )
    payment_context = card_transaction and (not transfer) and (
        not topup or topup_is_background
    )
    if payment_context:
        if unrecognized:
            add("card_payment_not_recognised", 56)
        if declined:
            add("declined_card_payment", 47)
        if pending:
            add("pending_card_payment", 45)
        if reverted:
            add("reverted_card_payment", 44)
        if fee:
            add("card_payment_fee_charged", 32)
        if exchange or rate:
            add("card_payment_wrong_exchange_rate", 26)
            if wrong:
                add("card_payment_wrong_exchange_rate", 26)
        if has(r"\b(?:does not|did not|will not|cannot|unable to)\b.{0,25}\b(?:pay|payment|purchase)\b"):
            add("declined_card_payment", 29)
        if has(r"\b(?:charged|paid)\b.{0,25}\b(?:more|extra)\b") and retail and not rate:
            add("card_payment_fee_charged", 14)

    if unrecognized and not (atm or transfer or topup) and not has(r"\bdirect debit\b"):
        if purchase or has(r"\b(?:statement|charge|money|account activity)\b"):
            add("card_payment_not_recognised", 19)
        elif card:
            add("compromised_card", 32)

    if has(r"\b(?:refund|refunded|refunding|reimbursement|reimbursed|chargeback|charge back)\b"):
        if not (topup or (transfer and not retail)):
            add("request_refund", 26)
            if missing or pending or timing or has(
                r"\b(?:waiting|promised|issued|processed|already|sent|due|expecting)\b|"
                r"\b(?:merchant|shop|store|retailer)\b.{0,25}\brefunded\b"
            ):
                add("refund_not_showing_up", 53)
            if has(
                r"\b(?:request|ask for|want|need|apply for|initiate|start|"
                r"get a refund|obtain a refund|chargeback|charge back|refuses|refused)\b"
            ):
                add("request_refund", 24)
            if has(r"\b(?:will|would|does) not (?:refund|give me a refund)\b"):
                add("request_refund", 23)
    if has(
        r"\b(?:get|want|need|claim|request)\b.{0,25}\b(?:money back|reimbursement)\b|"
        r"\bdisput(?:e|ing)\b.{0,25}\b(?:payment|transaction|charge|purchase)\b|"
        r"\b(?:cancel|reverse|undo)\b.{0,25}\b(?:card payment|purchase|card transaction)\b|"
        r"\b(?:goods|item|order|product)\b.{0,30}\b(?:not received|never arrived|not delivered)\b"
    ) and not (atm or topup or transfer):
        add("request_refund", 49)

    small_charge = has(
        r"\b(?:small|tiny|little|verification|authorization|authorisation|temporary)\b"
        r".{0,20}\b(?:charge|payment|amount|transaction)\b|"
        r"(?:£|€|\$)\s*(?:0[.,]\d+|1(?:[.,]00)?)(?!\d)|"
        r"\b(?:one|1)\s*(?:pound|euro|dollar|gbp|eur|usd)\b|"
        r"\b(?:pound|euro|dollar)\b.{0,15}\b(?:charge|charged|extra)\b"
    )
    if small_charge and has(r"\b(?:charge|charged|statement|payment|debited|taken|deducted|extra)\b"):
        add("extra_charge_on_statement", 58)
    elif has(r"\bextra charge\b") and has(r"\bstatement\b") and not (
        atm or transfer or topup or retail
    ):
        add("extra_charge_on_statement", 39)

    # Currency selection, conversion instructions, pricing, and exchange rates.
    if exchange or rate:
        if rate:
            add("exchange_rate", 29)
            if not atm and not (payment_context and (wrong or retail)):
                add("exchange_rate", 9)
        if exchange and not rate:
            add("exchange_via_app", 24)
            if has(r"\b(?:how|can i|where|app|application|convert|change|buy|sell)\b"):
                add("exchange_via_app", 12)
        if fee and exchange and not atm and not topup:
            add("exchange_charge", 39)
            if not retail:
                add("exchange_charge", 10)
        if has(r"\b(?:weekend|fair usage|markup|mark up|commission)\b") and fee and not atm:
            add("exchange_charge", 13)

    currency_support = currency and has(
        r"\b(?:support\w*|available|hold|holding|keep|balance|balances|"
        r"accounts|currencies|accept|accepted|offer)\b"
    )
    if currency_support and not topup:
        add("fiat_currency_support", 26)
        if has(
            r"\b(?:which|what|how many|multiple|several|supported|support|"
            r"hold|holding|keep|multi currency)\b"
        ):
            add("fiat_currency_support", 16)
        if exchange and has(r"\bhow (?:do|can|to)\b") and not has(
            r"\bwhich currenc|\bwhat currenc|\bhow many\b"
        ):
            add("fiat_currency_support", -16)
        if missing or pending or wrong:
            add("fiat_currency_support", -16)
    if currency and has(r"\b(?:open|create|have|get)\b.{0,20}\b(?:account|balance)\b") and not (
        transfer or topup or missing
    ):
        add("fiat_currency_support", 36)

    # Strong explicit constructions settle common overlaps.
    if has(r"\bbeneficiar\w* not allowed\b"):
        add("beneficiary_not_allowed", 55)
    if has(r"\b(?:cash|cheque|check) deposit\b") and missing:
        add("balance_not_updated_after_cheque_or_cash_deposit", 15)
    if has(r"\bbank transfer\b") and has(
        r"\bbalance\b.{0,25}\b(?:not|unchanged|same|missing)\b|"
        r"\bnot\b.{0,20}\b(?:updated|credited|reflected)\b"
    ):
        add("balance_not_updated_after_bank_transfer", 19)
    if has(r"\bvirtual card\b") and has(r"\b(?:not working|declined|rejected)\b"):
        add("virtual_card_not_working", 14)
    if has(r"\bcard payment\b") and has(r"\bdeclined\b") and not topup:
        add("declined_card_payment", 12)
    if has(r"\b(?:refund|refunded)\b") and reverted and not topup:
        if not has(r"\b(?:reverted|reversed|reversal)\b"):
            add("reverted_card_payment", -20)
    if identity_context and has(r"\bwhy\b") and has(
        r"\b(?:failed|rejected|declined|not working|not accepted|stuck|pending|taking so long)\b"
    ):
        add("unable_to_verify_identity", 20)
    if topup_is_background and (declined or failed):
        add("declined_card_payment", 24)
        add("top_up_failed", -23)

    answer = max(scores, key=scores.get)
    return {"answer": answer}
