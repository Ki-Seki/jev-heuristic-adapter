import re
import math
import unicodedata
from collections import Counter

# Short exemplars describe both the subject and the kind of question being asked.
_TEXT = {
"activate_my_card": "How do I activate my new card|My card has arrived what must I do before I can use it|Enable the card I just received|Where is the activation option|I cannot activate this card|Do I need to make a chip and pin payment first",
"age_limit": "What is the minimum age to open an account|Can my child get a card|I'm only seventeen can I sign up|Is there an age restriction|I would like an account for my daughter|Are under 18s eligible|Am I old enough to join|Do you offer accounts for minors",
"apple_pay_or_google_pay": "Can I use Google Pay with my card|How do I add this to Apple wallet|Android pay setup|Pay using my iphone or apple watch|Google pay top up|Why won't my card work with apple pay",
"atm_support": "Which cash machines can I use|Where can I take money out with my card|Do all ATMs accept your card|Find a supported ATM near me|Is there a locator for cash machines|Can I withdraw money overseas|Which banks can I withdraw cash from",
"automatic_top_up": "Set up an automatic top up|How do I stop auto top ups|Automatically add funds when my balance gets too low|Can I change the threshold for recurring top ups|What triggers an auto recharge|Schedule my top ups|I do not want to have to manually add money each time",
"balance_not_updated_after_bank_transfer": "I transferred money to my account and the balance hasn't changed|The bank transfer hasn't appeared in my account|Where is the money I sent from my bank|My incoming transfer is missing|I added money by wire transfer but I can't see it|My salary has not shown up yet|My friend sent me money and it never came through|Bank transfer completed but no funds credited",
"balance_not_updated_after_cheque_or_cash_deposit": "My cash deposit has not appeared in my account|I paid in a cheque but my balance hasn't updated|Why is the check I deposited not showing|I deposited some cash at the bank but it's not reflected on my balance|Where has my cash deposit gone",
"beneficiary_not_allowed": "It says beneficiary not allowed|Why can't I add this beneficiary|Payment to this payee is not permitted|Transfer to a cryptocurrency exchange isn't allowed|What is a restricted beneficiary|I got an error that this recipient isn't supported",
"cancel_transfer": "How do I cancel a transfer|Can I stop a bank transfer I just made|I sent money to the wrong person how can I get it back|I used the wrong account details for my transfer|Recall a transfer|I want to reverse an accidental transfer|Can I change the recipient after sending the money",
"card_about_to_expire": "My card is about to expire what should I do|Will I get a replacement when the card expires|Can I renew my card|Where will the new card be sent once mine has expired|My expiration date is coming up",
"card_acceptance": "Where can I use my card|Will merchants abroad accept my card|Can I pay in any shop with this card|Is my card accepted everywhere|Can I use the card for online purchases|Which countries can I spend in|What places take this card|Can I use my card when I travel",
"card_arrival": "Where is the card I ordered|My card still hasn't arrived|I've been waiting for my new card and it never showed up|How can I track my card delivery|I haven't received my card in the mail|Check the status of my card order|The estimated delivery date has passed|My card was supposed to be here already|Has my new card been dispatched",
"card_delivery_estimate": "How long does it take for a card to arrive|When should I expect delivery of my new card|Can I get express delivery|I need a card as soon as possible|How quickly could you ship a card to me|What are the delivery options for cards|Is there an estimated arrival date|Can I pay more to have the card sent faster",
"card_linking": "How do I link my card to the app|Can I connect an existing card to my account|I already have a card how can I associate it with the app|How many cards can be linked to an account|How do I unlink a card|Can I attach my new card to my existing account|I have two accounts can I link the cards",
"card_not_working": "My card isn't working|My card doesn't work anymore|My physical card is broken|The chip on my card is damaged|Something is wrong with my card|My card cannot be read at all|My card stopped functioning|My card won't work anywhere",
"card_payment_fee_charged": "Why was I charged a fee for making a card payment|An extra fee for buying something with my card|Is there a surcharge for card purchases abroad|I was charged for paying with my card|Why did a merchant charge me a fee when I used my card|Is it free to make card payments",
"card_payment_not_recognised": "I see a card payment that I don't recognise|There is a purchase on my account that I didn't make|Unknown merchant on my statement|I do not remember making this transaction|A payment I never authorized was taken from my card|Money was spent on something I didn't buy|There is a strange payment on my card",
"card_payment_wrong_exchange_rate": "The exchange rate on my card payment is wrong|I bought something abroad and got a poor exchange rate|Why was a different rate applied to my purchase|My card payment used the wrong currency conversion|I paid at a shop but the exchange rate doesn't look right",
"card_swallowed": "The cash machine swallowed my card|ATM retained my card|The machine never gave me my card back|My card got stuck in the ATM|How do I recover my card from a cashpoint|The ATM ate my debit card|Cash machine won't release my card",
"cash_withdrawal_charge": "Why was I charged a fee to withdraw cash|How much does it cost to use an ATM|Free cash withdrawal limit|Additional fees for taking money out abroad|Which withdrawals are free|The cash machine charged me for my withdrawal",
"cash_withdrawal_not_recognised": "There is an ATM withdrawal I don't recognise|I never took out that cash|My account shows a withdrawal that wasn't mine|I didn't make this cash withdrawal|Someone took money out of an ATM with my card|I see a cash withdrawal but I haven't used a cash machine",
"change_pin": "Can I change my PIN|How to set a new PIN for my card|Which cash machines let me change my PIN number|Can I choose my own pin|I want to update my card pin",
"compromised_card": "I think my card details have been stolen|I am concerned my card was compromised|Someone has a copy of my card|My card may have been cloned|My card information has been exposed|Someone else is using my card without permission|How can I protect my account from fraudulent use|I think someone knows my card number",
"contactless_not_working": "Contactless payments aren't working|I cannot tap to pay|My contactless stopped working but chip and pin is fine|Paywave is not working|My card won't let me pay by tapping it|Do I need to enable contactless",
"country_support": "Which countries are supported|Can I open an account if I live in Canada|In what countries are your services available|Do you issue cards to residents of the US|Can someone outside the UK sign up|Where must I live to get an account|I'm not a UK resident can I apply",
"declined_card_payment": "My card payment was declined|A purchase was rejected even though I have enough money|Why did the merchant decline my payment|The card transaction would not go through|I tried paying in a store but it was refused|My online payment failed",
"declined_cash_withdrawal": "My cash withdrawal was declined|The ATM refused my withdrawal|I can't take cash out|Why was my card declined at a cash machine|Withdrawals are being rejected even though I have funds|It won't let me withdraw money",
"declined_transfer": "Why was my transfer declined|My bank transfer was rejected|It says transfer refused|The app won't allow this transfer|My transfer was denied but I have enough money",
"direct_debit_payment_not_recognised": "I don't recognise this direct debit|There is an unknown direct debit from my account|I didn't authorise a direct debit|Why is a company taking a direct debit I never set up|I see a direct debit that isn't mine",
"disposable_card_limits": "What are the limits of a disposable virtual card|How many disposable cards can I use per day|Can a single use card be used more than once|Restrictions on disposable card transactions|Can I pay subscriptions with a disposable card|What is the maximum spend for a single use card|How often can I use the disposable number",
"edit_personal_details": "How do I edit my personal details|I need to change my name on the account|My address has changed where can I update it|Can I correct my date of birth|I got a new phone number|Update email and contact information|I moved house and need to change my address|I got married and changed my surname",
"exchange_charge": "Is there a fee for exchanging currencies|What are your foreign exchange fees|Does currency conversion cost extra on weekends|Is there a markup on the exchange rate|How much can I exchange for free|Commission on money exchange",
"exchange_rate": "What exchange rate do you use|Where do you get your currency exchange rates|How is the exchange rate calculated|Is the rate the interbank rate|What's today's conversion rate for euros|Why do currency rates fluctuate",
"exchange_via_app": "How do I exchange money in the app|Can I convert pounds to euros in my account|Where do I go to exchange currencies|I want to buy foreign currency|Can I switch my dollars into sterling|How can I exchange between balances",
"extra_charge_on_statement": "Why is there a small extra charge on my statement|There is an additional charge of one pound|A small amount was taken from my account following a payment|What is this extra dollar charge on my account|I see a verification charge on my statement|There is an unexpected extra payment on my bill",
"failed_transfer": "My transfer failed|I cannot make a bank transfer|Transfer didn't go through|My attempt to send money was unsuccessful|Getting an error when trying to transfer money|Why did my bank transfer fail|My transfer keeps failing",
"fiat_currency_support": "What fiat currencies can I hold|Which currencies can I have balances in|Can I open a dollar account|Can I keep several different currencies in my account|What currencies do you support|I want a balance in euros|Which local currencies are supported for holding money",
"get_disposable_virtual_card": "How do I get a disposable virtual card|What is a single use card|Can I create a temporary virtual card|Where can I find disposable cards in the app|I want a card whose details change after each purchase|How do disposable cards work",
"get_physical_card": "Can I get a physical card in person|Where can I pick up a card|Can I collect my card at a branch|Is it possible to get a real card|How can I get a physical card instead of a virtual one|Can I get an actual plastic card|Can I get my card directly from your office",
"getting_spare_card": "Can I have a spare card|How do I order a second card|Could I get an extra card as backup|Can I have two cards for the same account|How many physical cards can I have|I want another card for emergencies",
"getting_virtual_card": "How can I get a virtual card|Where is my virtual card in the app|Can I create a digital card for online shopping|Do you offer virtual cards|How does a virtual card work|Do I need to order a virtual card|What is a virtual card",
"lost_or_stolen_card": "I lost my card how can I block it|My wallet was stolen|I can't find my debit card|I think I misplaced my card|How do I report a stolen card|I found the card I reported missing|Someone stole my handbag with my credit cards in it",
"lost_or_stolen_phone": "My phone has been stolen|I lost my mobile what can I do to protect my account|Can't find my phone and someone could use the app|What do I do if my smartphone is missing|I no longer have access to the phone with my app",
"order_physical_card": "How do I order a physical card|Does ordering a card cost anything|Where in the app do I request a card|I would like to order my first debit card|Do I have to pay for a physical card|I signed up how do I order my card now|Can you send me a card",
"passcode_forgotten": "I forgot my passcode|I can't remember the code to log into the app|I lost my password|How do I reset my login code|Locked out of the app as I have forgotten my credentials|I can't get into my account|How to recover a forgotten pass code",
"pending_card_payment": "Why is my card payment still pending|The merchant transaction hasn't completed|My purchase is showing as pending|How long will a pending card transaction take|Why is my money on hold after paying|My payment has not cleared yet",
"pending_cash_withdrawal": "My cash withdrawal is pending|Why does the ATM transaction still show as pending|I got my cash but the app says the withdrawal isn't complete|How long before my cash withdrawal clears",
"pending_top_up": "Why is my top up pending|Topping up is still processing|I added money with my card and it is pending|How long does a pending top up take|Top up has not cleared",
"pending_transfer": "Why is my transfer pending|Bank transfer stuck in processing|How long can a transfer be pending|I sent money but the status is still pending|My transfer hasn't completed yet",
"pin_blocked": "My card PIN is blocked|I entered my pin incorrectly three times|How can I unblock my PIN|Too many incorrect PIN attempts|I got locked out after entering the wrong pin|Reset the pin tries",
"receiving_money": "How can someone send me money|What details do I give someone to pay me|How can my friends transfer money to me|Can I receive my salary here|How do I receive a payment from another user|I want to receive money in my account|Can someone pay me from overseas",
"refund_not_showing_up": "My refund hasn't shown up yet|The merchant refunded me but I haven't received it|Where is the refund I was promised|How long does a refund take to appear|I returned an item but the money is not back in my account|When will a refund be credited",
"request_refund": "How do I request a refund|I want my money back for a purchase|Can you help me get a chargeback|I'd like to dispute a card payment|The goods I bought never arrived|I want to return something and get reimbursed|The seller won't give me my money back",
"reverted_card_payment": "My card payment was reverted|A payment went through then the money came back|Why was my purchase reversed|My transaction is showing as reverted|The merchant didn't claim the funds|A completed card payment was returned to my account",
"supported_cards_and_currencies": "What cards and currencies can I use to top up|Which credit cards are supported for adding funds|Do you accept American Express top ups|Can I add money in another currency|Why is my top up card not supported|Which currencies can I top up with|Do you accept all types of bank cards for funding",
"terminate_account": "I want to close my account|How can I delete my account|Terminate my membership|I no longer want to use your services|Deactivate my account permanently|How do I cancel my account and leave|Please shut down this account",
"top_up_by_bank_transfer_charge": "Is there a fee to top up by bank transfer|Will I be charged for adding money by bank transfer|Why did my bank charge me to transfer money into my account|How much does it cost to fund my account with a wire transfer|Any charges for incoming bank transfers",
"top_up_by_card_charge": "Do I have to pay a fee to top up by card|Why was I charged for adding money with my credit card|Is topping up with my debit card free|Unexpected charge for a card top up|How much does a top up cost",
"top_up_by_cash_or_cheque": "Can I top up with cash or cheque|How do I deposit a paper check|Where can I pay in cash|Can I add cash to my account at a branch|Can you accept cheques for deposits|I would like to load my account with cash",
"top_up_failed": "My top up failed|I can't add money to my account|The app won't let me top up using my card|My top up was declined|My deposit by card didn't go through|Tried adding funds but it didn't work",
"top_up_limits": "Is there a limit on top ups|What is the maximum I can add to my account|How much can I top up in one day|Can I increase my top up limit|Is there a minimum amount for a top up|Any restrictions on how often I can add funds",
"top_up_reverted": "Why was my top up reverted|I added money but it was sent back to my card|Top up reversed after it was successful|My top up disappeared and was refunded|Why was my deposit returned",
"topping_up_by_card": "How do I top up my account with a card|Can I use someone else's credit card to add money|How to add a new top up card|Can I save my debit card for future top ups|How do I add money to my account|How to remove a saved top up card|Can I fund my account with a card",
"transaction_charged_twice": "I was charged twice for the same purchase|The transaction appears two times on my statement|Duplicate card payment|I only paid once but the merchant charged me twice|Why did the payment go through multiple times|There are two identical transactions",
"transfer_fee_charged": "Why did I pay a fee for a transfer|What does it cost to send money abroad|The recipient received less than I sent|I was charged extra for making a bank transfer|Are international transfers free|What commission do you charge on outgoing transfers",
"transfer_into_account": "How do I make a bank transfer into my account|How do I transfer money from my bank account to this account|Where can I find my IBAN and account details|Can I use a bank transfer to add money|How to transfer funds to another bank account|What bank details do I use for a transfer",
"transfer_not_received_by_recipient": "The recipient has not received my transfer|I sent money but it hasn't reached the other account|My friend didn't get the money I sent|Bank transfer says complete but beneficiary still has nothing|Where is the money that I sent to someone|The recipient is still waiting for my payment",
"transfer_timing": "How long does a bank transfer take|When will the money I send arrive|What is the usual time frame for an international transfer|Do transfers go through on weekends|Is there a faster way to send a transfer|How many days does a transfer take to reach the beneficiary",
"unable_to_verify_identity": "I cannot verify my identity|My identity verification failed|My ID is not being accepted|Verification keeps getting rejected|Trouble uploading my passport photo|Why can't my identity be confirmed|The identity check is taking forever",
"verify_my_identity": "How can I verify my identity|What documents do I need to confirm who I am|Can I use my driving licence as ID|Where do I upload my passport|What is the identity verification process|How to prove my identity|What identification do you accept",
"verify_source_of_funds": "Why do you need proof of the source of my funds|How can I verify my source of income|What documents prove where my money came from|I need to provide evidence of my wealth|Why am I asked where my funds come from",
"verify_top_up": "How can I verify my top up|Where do I find the top up verification code|I need the code on my bank statement to verify my deposit|Why do you need to verify my top up card|What is the four digit code for my top up",
"virtual_card_not_working": "My virtual card isn't working|Payment with my virtual card was declined|The virtual card is not accepted online|Why can't I use my digital card|Unable to make a purchase with the virtual card",
"visa_or_mastercard": "Will I receive a Visa or Mastercard|Can I choose between Visa and MasterCard|Which brand is my card|I would prefer a visa instead of a mastercard|Is it possible to switch from Mastercard to Visa|What type of card will be issued",
"why_verify_identity": "Why do I need to verify my identity|Is identity verification necessary|Why do you want a copy of my passport|Do I really have to submit identification|What is the reason for the identity check|Can I use my account without verifying who I am",
"wrong_amount_of_cash_received": "ATM gave me the wrong amount of cash|I withdrew money but only received part of it|The cash machine debited me but no money came out|I asked for 100 but only got 50|The amount dispensed is less than the withdrawal|The machine gave me too little cash",
"wrong_exchange_rate_for_cash_withdrawal": "The exchange rate for my cash withdrawal was wrong|I got a bad conversion rate at the ATM|The cash machine used a different rate when I withdrew money abroad|Why is the withdrawal exchange rate worse than expected",
}

def _extract(x):
    if isinstance(x, str):
        return x
    if isinstance(x, dict):
        for k in ("text", "utterance", "customer_text", "customer_query", "customer_message", "query", "message", "input", "content", "sentence", "description", "prompt", "question", "state"):
            if k in x:
                t = _extract(x[k])
                if t:
                    return t
        return " ".join(_extract(v) for v in x.values())
    if isinstance(x, (list, tuple)):
        return " ".join(_extract(v) for v in x)
    return ""

def _norm(t):
    t = unicodedata.normalize("NFKD", t.lower().replace("’","'").replace("‘","'"))
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.replace("_", " ").replace("-"," ")
    t = re.sub(r"\b(?:can't|cant|cannot)\b", "can not", t)
    t = re.sub(r"\bwon'?t\b", "will not", t)
    t = re.sub(r"\b([a-z]+)n'?t\b", lambda m: m[1] + " not" if m[1] in ("did","do","does","is","was","were","are","has","had","have","could","would","should","must") else m[0], t)
    t = t.replace("'ve"," have").replace("'ll"," will").replace("'re"," are").replace("'m"," am").replace("'d"," would").replace("'s", " ")
    t = re.sub(r"[^a-z0-9£€$]+", " ", t)
    t = re.sub(r"\b(?:top *ups?|top *ped *up|top *ping *up|toping up|topoff|reload(?:ed|ing)?|recharg(?:e|ing|ed))\b", "topup", t)
    t = re.sub(r"\b(?:cash *points?|cash *machines?|automatic teller machines?|automated teller machines?|a t m|atms)\b","atm",t)
    t = re.sub(r"\b(?:master card|mastercards)\b","mastercard",t)
    t = re.sub(r"\b(?:recogniz|recognis)(?:e|ed|able)\b","recognise",t)
    t = t.replace("cheques","cheque").replace("pass code","passcode").replace("pay pass","paypass").replace("contact less","contactless")
    return " ".join(t.split())

_STOP = set("the a an to i is my it of in me for on and this have you do what with that be at can am was but so are as some would from has will there if by or how when why get do they your could please help about one like want just need now still had not".split())
_CANON = {}
for _row in [
    "transfer transfers transferred transferring transferral wire wired wiring remittance remit",
    "pay payment payments paid paying pays",
    "card cards", "bank banks banking", "transaction transactions", "fee fees surcharge commission charges charged charging cost costs charge",
    "buy bought buying purchase purchasing purchases purchased", "shop shops store stores retailer merchant merchants retailers",
    "reject rejected declined declining decline denied refused refuses refuses",
    "fail fails failed failing failure unsuccessful",
    "cashwithdraw withdrawal withdrawals withdraw withdrawing withdrew withdrawn",
    "cheque check checks", "receive received receiving recieve recieved gotten got",
    "money funds fund monies", "pending processing awaiting outstanding", "cancel cancelled canceled cancelling stop",
    "return returned refunding returned", "refund refunds reimbursed reimbursement",
    "revert reverted reversed reverse reversion", "duration timeframe time long days hours weeks",
    "country countries", "currency currencies", "exchange exchanged exchanging conversion converting convert fx",
    "foreign overseas abroad international", "rate rates", "balance balances", "account accounts",
    "verify verifying verified verification confirm confirming validate validation",
    "identity id identification", "document documentation documents proof evidence",
    "person details information info", "add adding added load loaded loading deposit deposited depositing",
    "allow allowed permitted permit enable", "limit limits maximum restriction restrictions cap",
    "arrive arrival arriving arrives arrived delivered delivery", "order ordered ordering",
    "send sent sending remit", "beneficiary beneficiaries recipient payee",
    "stolen stole theft robbed", "lost misplaced missing", "working work works functioning function",
    "phone telephone mobile cellphone smartphone", "auto automatic automatically recurring",
    "spare extra additional backup secondary", "second another 2nd", "app application",
    "disposable throwaway temporary", "virtual digital", "wrong incorrect inaccurate bad",
    "express expedited faster urgent urgently quickly", "duplicate twice duplicated double",
    "child kid son daughter teen teenager minor children", "purchase merchandise goods",
    "activate activated activating activation", "expire expiration expiry expires expired expiring",
    "problem trouble difficulty problems issue issues", "update change changing amend edit modify",
    "recognise recognize recognize recognise remember recall", "password passcode login",
]:
    _words = _row.split()
    for _w in _words:
        _CANON.setdefault(_w, _words[0])

def _features(text):
    words = _norm(text).split()
    c = Counter()
    seq = []
    for w in words:
        if w not in _STOP:
            n = _CANON.get(w,w)
            c["w:"+n] += 1
            seq.append(n)
    for a,b in zip(seq,seq[1:]):
        c["b:"+a+" "+b] += 1
    for a,b in zip(words,words[1:]):
        if a not in _STOP or b not in _STOP:
            c["p:"+a+" "+b] += 1
    return c

def _index():
    docs = []
    counts = Counter()
    for k, s in _TEXT.items():
        for phrase in [k.replace("_"," ")] + s.split("|"):
            f = _features(phrase)
            docs.append((k, f))
            counts.update(f.keys())
    idf = {w:(1+math.log((1+len(docs))/(1+n)))**0.78 * (1.0 if w.startswith("w:") else .65) for w,n in counts.items()}
    ind = {}
    for k,f in docs:
        norm = math.sqrt(sum(idf[w]**2 * (1+math.log(n))**2 for w,n in f.items())) or 1
        for w,n in f.items():
            ind.setdefault(w,[]).append((k,len(ind) if False else 0)) if False else None
    post = {}
    labels = []
    for j,(k,f) in enumerate(docs):
        labels.append(k)
        norm = math.sqrt(sum(idf[w]**2*(1+math.log(n))**2 for w,n in f.items())) or 1
        for w,n in f.items():
            post.setdefault(w,[]).append((j,idf[w]**2*(1+math.log(n))/norm))
    return idf,post,labels

_IDF,_POST,_LABELS = _index()

def _similar(t):
    f = {w:n for w,n in _features(t).items() if w in _IDF}
    norm = math.sqrt(sum(_IDF[w]**2*(1+math.log(n))**2 for w,n in f.items())) or 1
    v = Counter()
    for w,n in f.items():
        for j,s in _POST[w]:
            v[j] += s*(1+math.log(n))/norm
    best = {}
    for j,s in v.items():
        k = _LABELS[j]
        best.setdefault(k, []).append(s)
    out = {}
    for k,vals in best.items():
        vals.sort(reverse=True)
        out[k] = vals[0]*5.2 + sum(vals[1:4])*.42
    return out

def predict(state) -> dict:
    t = _norm(_extract(state))
    sim = _similar(t)
    strength = {}
    def h(p):
        return re.search(r"\b(?:" + p + r")\b", t) is not None
    def vote(k, s, cond=True):
        if cond:
            strength[k] = max(strength.get(k,0),s)

    card = h(r"cards?|debit|credit|prepaid|visa|mastercard")
    atm = h("atm|teller machine|cash dispenser|bank machine|bancomat")
    withdrawal = atm or h(r"withdraw\w*|withdr[ea]w|withdrawing|(?:take|taking|taken|took|get|getting|pull|pulling|draw|drawing) (?:some |any |my |the |more )?(?:money|cash|funds) out|(?:take|taking|taken|took|get|getting|pull|draw|drawing) out .{0,16}(?:cash|money|funds)|cash out|dispens(?:e|ed|ing)")
    cash = h("cash|coins|notes|banknotes|bills")
    check = h(r"cheque|(?:a|by|with|via|my|the|paper|mailed|deposit|deposited|cash or) check|check deposit|checks")
    deposit = h(r"deposit\w*|paid in|pay in|paying in")
    transfer = h(r"transf[ea]r\w*|wires?|wiring|wired|swift|sepa|remit\w*|iban|bic|sort code|recipient|beneficiar\w*|payee|sending|sent|send|bank payment|bank to bank")
    literaltransfer = h(r"transf[ea]r\w*|wire transfer|bank wire|wired|sepa|swift")
    add = h(r"(?:add(?:ed|ing)?|load(?:ed|ing)?|put(?:ting)?|putting in) .{0,24}(?:funds|money|cash|balance|account|card)|(?:fund|funding|credit|load) (?:my|the|this|an) (?:account|card|balance)|(?:put|pay) money in")
    top = h("topup") or add or deposit
    explicit_top = h("topup")
    purchase = h(r"pay(?:ment|ments|ing|s)?|paid|bought|buy\w*|spent|spend\w*|purchas\w*|store|shop\w*|merchant|retailer|restaurant|transaction\w*|point of sale|checkout")
    merchant = h(r"merchant|retailer|store|shop|supermarket|restaurant|seller|vendor|retail|terminal")
    currency = h(r"currenc\w*|fiat|usd|gbp|euros?|eur|dollars?|pounds?|sterling|zloty|rupees?|yen|francs?|aud|cad|pln|bitcoin")
    exchange = h(r"exchange\w*|exchanging|conversion|convert\w*|forex|fx|rates?|interbank|mark ?up")
    rate = h(r"rates?|conversion|converted|fx|interbank")
    fee = h(r"fees?|surcharg\w*|commission|costs?|pricing|price|expensive|free|charges|charging|charged|charge|extra|deducted|deduction|additional (?:money|payment|amount)|pay for|not the full amount")
    fee_strong = h(r"fees?|surcharges?|commission|costs?|free|mark ?up|extra|additional|more than|overcharg\w*|unexpected charge|hidden charges?|service charge|charged (?:me )?for")
    rejected = h(r"declin\w*|reject\w*|refus\w*|deni(?:al|ed)|deny|not authori[sz]ed|turned down")
    failure = h(r"fail\w*|unsuccessful\w*|not (?:go|going|gone|work\w*|function\w*|success\w*|able|allow\w*|letting|let|accept\w*|complet\w*|process\w*)|stopped working|no longer work\w*|never works?|can not|could not|unable|error|trouble|difficult\w*|problems?|issues?|broken|damaged|not possible")
    pending = h(r"pend\w*|processing|on hold|not (?:yet )?(?:complete[d]?|cleared|finali[sz]ed)|still (?:not complete|in progress|being processed|waiting to clear)|stuck in|uncleared")
    revert = h(r"revert\w*|revers\w*|bounced? back|returned|back (?:in|into|on|to) my (?:account|card|balance)|came back|sent back|money (?:is |went )?back|unclaimed|did not (?:claim|collect)")
    timing = h(r"how (?:long|much time|fast|soon|quickly|many (?:days|weeks|hours))|when|time ?frame|timescale|estimate\w*|time (?:does|will|should|it takes)|time (?:for|to)|duration|weekends?|working days?|business days?|speed|days? (?:does|will|for)|take long|fastest|quickest")
    missing = h(r"not .{0,28}(?:arriv\w*|receiv\w*|reciev\w*|show\w*|appear\w*|reflect\w*|updat\w*|credit\w*|got\w*|reached?|get|see|seen|come|came|found|landed|changed|there|in my|in the|on my|in their|on the)|never .{0,20}(?:got|came|appeared|received|arrived|reached|showed|credited|gotten)|missing|disappear\w*|not there|still waiting|yet to receive|nothing|not heard|no sign|no money|no funds|no trace|no change|balance (?:is |remains |stayed )?(?:unchanged|the same|wrong|incorrect)|where (?:is|are) (?:my|the) (?:money|funds|deposit|transfer)")
    unknown = h(r"not .{0,24}(?:recogni\w*|remember|recall|recognize|mine|me\b|my transaction|make|made|authori[sz]e|approve|consent|myself|participate|purchase|buy|buying|use|do\b|take out|withdraw|know|done by me)|unrecogni\w*|unauthori\w*|unfamiliar|unknown|without my (?:permission|knowledge|consent|approval|authori\w*)|was not (?:mine|me|by me)|never .{0,18}(?:made|used|been|bought|spent|withdrew|withdraw|visited|purchased|approved|authori[sz]\w*)|someone (?:else )?(?:made|took|withdrew|bought|paid)|no (?:idea|recollection|record)|strange (?:transaction|payment|purchase|withdrawal|charge)|did not do|not made by me|not sure (?:what|where)|mysterious")
    suspicious = h(r"fraud\w*|suspicious|stolen details|hacked|hack\w*|scam\w*|compromis\w*")
    limited = h(r"limits?|limitation\w*|maximum|max|minimum|min|restrict\w*|cap|capped|how (?:much|many|often)|number of times|more than once|multiple times|per day|unlimited|allowance|at once")
    inbound = h(r"(?:in|into|to|on) (?:my|this|our) (?:new |own |revolut |current )?(?:account|balance|card|wallet)|(?:from|through|via|using) my bank|incoming|inbound|to myself|to me|sent me|my balance|my salary|my wages|i (?:have |still |did |do |am )*(?:not (?:received?|got|get|see)|waiting for)")
    outgoing = h(r"beneficiar\w*|recipients?|payee|destination|their (?:account|bank|end|balance)|to (?:someone|somebody|another|a friend|a different|him|her|them|the other|my friend|my brother|my sister|my mother|my father|my son|my daughter|my wife|my husband)|person i (?:sent|transferred)|other (?:account|person|bank)|they (?:have|did|still|say)|i (?:sent|transferred) .{0,28} to")
    # Distinguish an actual credit that is missing from how-to questions.
    cashin = check or (cash and (top or h(r"(?:send|mail|put|pay|add|accept|using|use|with|via|by|in|from|bring|take) (?:physical |some |my )?cash|cash (?:to|into|in|at|deposit)|physical money")) and not h(r"cash withdrawal"))
    cashin = cashin and not (withdrawal and not deposit and not check and not explicit_top)
    if cashin:
        vote("top_up_by_cash_or_cheque",9)
        vote("balance_not_updated_after_cheque_or_cash_deposit",13, missing or pending or h(r"(?:cashed|deposited|paid in|lodged) .{0,32}(?:ago|yesterday)|how long|where .{0,18} deposit|what happened|waiting|still"))
    if transfer or inbound:
        vote("transfer_into_account",3.4, literaltransfer or h("iban|bic|sort code|routing number|bank details"))
        vote("transfer_into_account",7,(literaltransfer and (top or inbound)) or h("iban|bic|routing number|bank details|account number and sort code"))
        vote("transfer_timing",8,timing and transfer and not (missing and outgoing))
        vote("pending_transfer",10,transfer and pending)
        vote("declined_transfer",10,transfer and rejected)
        vote("failed_transfer",8,transfer and failure and not missing and not rejected)
        vote("failed_transfer",10,transfer and h("failed|failing|failure|unsuccessful|did not go through"))
        vote("beneficiary_not_allowed",15,h(r"beneficiar\w*|recipient|payee") and h(r"not (?:be )?(?:allowed|supported|permitted|accepted)|disallowed|prohibited|restricted|can not add|unable to add|invalid beneficiary"))
        vote("beneficiary_not_allowed",11,h(r"crypto\w*|bitcoin|exchange platform") and transfer and (failure or rejected))
        vote("cancel_transfer",14,transfer and h(r"cancel\w*|recall|revoke|stop (?:a|my|this|the|an)|undo|call back|take .{0,10} back|changed my mind|wrong (?:person|account|beneficiary|details|recipient|bank|amount)|incorrect (?:details|account|beneficiary)|(?:accidentally|mistakenly) (?:sent|transferred)|mistake|reverse (?:a|my|the|this)|get (?:it|my money|the money) back"))
        vote("balance_not_updated_after_bank_transfer",9.8,missing and (transfer or inbound) and not outgoing)
        vote("balance_not_updated_after_bank_transfer",12,missing and literaltransfer and inbound and not h(r"recipient|beneficiary|their account|my friend .{0,12} not (?:received|get|got)"))
        vote("transfer_not_received_by_recipient",12,missing and outgoing)
        vote("transfer_not_received_by_recipient",10,missing and transfer and h(r"i (?:have |had )?(?:sent|transferred)|sent .{0,18} ago|transfer .{0,20} complete") and not inbound)
        vote("transfer_fee_charged",9,transfer and fee and not (missing and not fee_strong))
        vote("transfer_fee_charged",11,transfer and h(r"less (?:money )?than|not (?:get|receive) the full|deducted|short of"))
        vote("top_up_by_bank_transfer_charge",12,fee and (explicit_top or add or deposit or inbound) and literaltransfer and not outgoing)
    receive = h(r"receiv(?:e|ing) (?:a |some |my |bank |international |regular )?(?:money|payments?|transfers?|salary|funds)|(?:send|pay|transfer|give) me|(?:send|transfer|pay) .{0,22} to me|someone .{0,18} (?:send|pay|transfer)|get paid|salary|paycheck|wages|pay cheque|payroll|money from (?:someone|a friend|my friend|other)|details .{0,28} (?:give|share)|someone .{0,15} (?:deposit|pay)")
    vote("receiving_money",8,receive)
    vote("receiving_money",7,h(r"(?:friend|someone|employer|family|others?)") and inbound and not missing and transfer)
    if top:
        vote("topping_up_by_card",5.2)
        vote("topping_up_by_card",7,card and not literaltransfer)
        vote("automatic_top_up",14,h(r"auto\w*|recurr\w*|threshold|schedule\w*|runs? low|below|every (?:week|month|time)|falls? (?:under|below)|drops? (?:under|below)|minimum balance|regularly|repeating"))
        vote("pending_top_up",12,pending)
        vote("top_up_reverted",13,revert or h("refunded|bounced|money was taken back"))
        vote("top_up_failed",10,(failure or rejected or h(r"not (?:go|going) through")) and not cashin)
        vote("top_up_by_card_charge",10,fee and (fee_strong or explicit_top) and not literaltransfer)
        vote("top_up_limits",11,limited and not h("how much .{0,20}(?:cost|charged|fee)|how many cards"))
        vote("verify_top_up",14,h(r"verif\w*|authenticat\w*|confirmation code|(?:four|4) digit|security code|statement code") and not h("identity|passport|source of"))
        vote("supported_cards_and_currencies",12,(currency and not fee and not literaltransfer) or h(r"types? of cards?|what (?:bank |credit |debit )?cards|which (?:bank |debit |credit )?cards|cards? .{0,16} supported|cards? .{0,14} accept\w*|american express|amex|maestro|diners club|discover card|prepaid|supported cards"))
        vote("balance_not_updated_after_bank_transfer",10,missing and not cashin and (literaltransfer or not explicit_top and not card))
    vote("automatic_top_up",11,h(r"auto\w* .{0,20}(?:add|fund|deposit|refill|topup|balance)|(?:balance|account) .{0,24}(?:too low|below .{0,10} amount)|auto top"))
    vote("verify_top_up",10,h(r"(?:four|4) digit .{0,12} code|code .{0,18} statement|statement .{0,12} code") and not h("pin|passcode|log in"))
    vote("supported_cards_and_currencies",10,h("american express|amex|diners club|maestro|discover card|supported cards|cards and currencies"))
    if withdrawal:
        vote("atm_support",5.5)
        vote("atm_support",8,h(r"which|where|locator|nearest|find (?:an|a)|supported|accept|use any|any atm|what atm"))
        vote("pending_cash_withdrawal",13,pending)
        vote("declined_cash_withdrawal",10,failure or rejected or h("unsuccessful|would not give|not letting"))
        vote("cash_withdrawal_charge",11,fee or h(r"withdraw .{0,20} without|free withdrawals?|atm limit"))
        vote("wrong_exchange_rate_for_cash_withdrawal",14,exchange)
        vote("cash_withdrawal_not_recognised",15,unknown or suspicious)
        vote("wrong_amount_of_cash_received",15,h(r"wrong amount|incorrect amount|not (?:the |as )?(?:right|correct|full|same|much) amount|less (?:cash |money )?than|more (?:cash |money )?than|short(?:ed|changed)?|not .{0,16}(?:dispense|dispensed|give me|enough cash)|only (?:gave|got|received|dispensed)|(?:gave|got|received) .{0,12} (?:less|instead)|not (?:give|get|receive) .{0,8}(?:cash|money)|nothing came|no (?:cash|money) (?:came|was dispensed|came out)|did not come out|partial|too (?:little|much)|asked for .{0,32} (?:got|gave|received)|amount .{0,18} (?:different|wrong|incorrect)|(?:debited|deducted|charged|taken from).{0,40}(?:no cash|no money|nothing)|(?:no cash|no money|nothing).{0,40}(?:debited|deducted|charged|taken from)"))
        vote("card_swallowed",18,h(r"swallow\w*|retain\w*|stuck|trapped|capture\w*|ate|eaten|kept|keeping|took my card|not .{0,16}(?:return|release|give|spit|eject) .{0,12}(?:card|back)|(?:card|it) (?:back|out) .{0,8}(?:from|of)|card .{0,12}not .{0,12}(?:back|out)|left my card|did not get my card back"))
    vote("card_swallowed",17,card and h("swallow\\w*|ate my card|retained my card|my card was retained"))
    if purchase or card or not (top or withdrawal or transfer):
        vote("declined_card_payment",8,(rejected or (purchase and failure)) and not (top or withdrawal or literaltransfer))
        vote("card_not_working",8,card and failure and not (rejected or purchase or top or withdrawal))
        vote("card_not_working",10,card and h("damaged|broken|chip .{0,18}(?:work|read)|card (?:has |just )?stopped working|card (?:is |does )?not work\\w*"))
        vote("pending_card_payment",9,pending)
        vote("reverted_card_payment",10,revert and not (top or literaltransfer) and not h("refund|item|goods|product"))
        vote("card_payment_not_recognised",10,unknown and not (top or withdrawal or literaltransfer))
        vote("card_payment_not_recognised",8,suspicious and purchase)
        vote("card_payment_fee_charged",8,fee and purchase and not (top or transfer or withdrawal))
        vote("card_payment_fee_charged",10,fee_strong and (merchant or h(r"card pay\w*|pay\w* .{0,10} (?:my|the|a) card|us(?:e|ed|ing) my card|(?:purchase|bought|buying)")))
        vote("card_payment_wrong_exchange_rate",10,exchange and (purchase or h(r"used my card|on my card")) and not withdrawal)
    vote("direct_debit_payment_not_recognised",17,h("direct debit|directdeb\\w*|direct deduction") and not h("debit card"))
    vote("extra_charge_on_statement",11,h(r"(?:small|little|extra|additional|odd|strange|unexpected) (?:amount|payment|transaction|charge|sum)|charge .{0,22} (?:on my statement|on the statement)") and not (top or withdrawal or literaltransfer))
    vote("extra_charge_on_statement",16,h(r"(?:[£€$] *1\b|(?:one|1|single|a) (?:pound|dollar|euro)\b|1 ?gbp|small (?:sum|charge|amount)|tiny amount|micro ?charge|test charge)") and (fee or purchase or h("statement|deducted|taken")) and not top)
    vote("transaction_charged_twice",17,h(r"twice|duplicat\w*|two times|double (?:billed|charged|charge|payment)|charged double|two (?:identical|same)|multiple times|same .{0,20} (?:two|more than once|multiple)|more than once|(?:charged|paid|billed) (?:me )?(?:2|two|three|several) times|two (?:charges|payments|transactions) .{0,20}(?:one|same)|appears? (?:two|2) times") and not (h("disposable") or limited and explicit_top))
    if exchange:
        vote("exchange_rate",6.5)
        vote("exchange_rate",8.4,rate)
        vote("exchange_charge",11.5,fee and not withdrawal)
        vote("exchange_via_app",9.2,not rate and not fee and not (purchase and card) or h(r"in (?:the |my |this )?app|via .{0,8}app|with .{0,8}app|on .{0,8}app") and not rate and not fee)
        vote("card_payment_wrong_exchange_rate",13,not withdrawal and (purchase or card) and h("wrong|incorrect|different|expected|poor|bad|worse|higher|too much|overcharged|not right|not correct|not match|charged more"))
    vote("exchange_via_app",9,currency and h(r"(?:dollars?|pounds?|euros?|gbp|usd|eur|sterling) (?:in)?to|(?:change|switch|buy|sell) .{0,20}(?:currency|currencies|euros|dollars|pounds)"))
    vote("fiat_currency_support",8,currency and not(prohibit_currency := (top or exchange or withdrawal or transfer or purchase)))
    vote("fiat_currency_support",12,currency and h(r"hold|carry|store|keep|fiat|balances|open (?:an?|another) .{0,14}account") and not explicit_top)

    pin = h("pin|pins|p i n|personal identification number")
    if pin:
        vote("change_pin",7)
        vote("change_pin",12,h(r"chang\w*|set|choos\w*|customi[zs]e|modify|new pin|updat\w*|reset"))
        vote("pin_blocked",16,h(r"block\w*|unblock\w*|lock\w*|unlock\w*|(?:three|3|too many|several|multiple) (?:incorrect |wrong )?(?:times|tries|attempts)|incorrect\w*|wrong pin|wrong .{0,8} times|pin tries"))
    vote("pin_blocked",14,h(r"(?:three|3|too many) (?:wrong |incorrect )?(?:tries|attempts)|(?:incorrect|wrong) .{0,24}(?:three|3) times"))
    vote("passcode_forgotten",13,h(r"passcodes?|password|pass word|login code|log ?in details|access code") and not h("topup"))
    vote("passcode_forgotten",11,h(r"(?:forgot\w*|not remember|lost|reset) .{0,24}(?:code|log ?in|credentials)|locked out .{0,12}(?:account|app)|(?:not|unable to) (?:log ?in|log on|sign in|access the app)"))
    vote("activate_my_card",15,h(r"activat\w*") and not h(r"deactivat\w*|contactless|topup"))
    vote("activate_my_card",9,card and h(r"start using|first use|use it for the first time|enable (?:my|the) (?:new )?card"))
    vote("age_limit",16,h(r"age limit|age restriction|old enough|under ?age|teen\w*|minors?|minimum age|maximum age|years? old|(?:under|over|turned|turning|only|aged|am) (?:1[0-9]|eighteen|sixteen|seventeen)|(?:what|which) age|how old|at least 18|kids?|child(?:ren)?|youth|youngster|too young") or (h("son|daughter|grandchild") and not transfer))
    vote("apple_pay_or_google_pay",16,h(r"(?:apple|google|android|samsung) ?(?:pay|wallet|watch)|gpay|i ?pay|iwatch|pay .{0,12}(?:iphone|watch)|mobile wallet"))
    vote("card_about_to_expire",16,h(r"expir\w*|renew(?:al|ed|ing)?|valid thru|out of date") and not h("passport|id card|transfer expired"))
    vote("card_linking",15,h(r"(?:link|unlink|linked|linking|connect|connect(?:ed|ing)|associate|attach|pair|sync|register) .{0,32}(?:cards?|app|account)|card .{0,16}(?:link|linked|registered|connected|associated|attached)") and card and not explicit_top)
    vote("card_linking",12,card and h(r"(?:add|added|adding) .{0,24}card .{0,12}(?:app|account)|existing card|already have a card") and not top)
    vote("contactless_not_working",16,h(r"contactless|touchless|paypass|paywave|tap (?:and|to) pay|tap (?:my|the) card|tapping|tap feature|nfc|wave .{0,10}card"))
    vote("visa_or_mastercard",14,h("visa") and h("mastercard") and not explicit_top)
    vote("visa_or_mastercard",10,h("visa|mastercard") and h("choose|select|instead|prefer|decide|switch|type of card|why .{0,12} (?:given|sent|issued)"))
    virtual = h("virtual|digital card|online only card|non physical card")
    disposable = h(r"dispos\w*|single use|one (?:time|use)|throw ?away|temporary card|use once|changes? .{0,10}(?:after|every) .{0,10}(?:purchase|transaction|use)")
    if virtual:
        vote("getting_virtual_card",10)
        vote("virtual_card_not_working",15,(failure or rejected) and not h("can not (?:find|locate|see|get|order) .{0,12}(?:card|virtual)"))
    if disposable:
        vote("get_disposable_virtual_card",14)
        vote("disposable_card_limits",17,limited or h(r"subscriptions?|recur\w*|where can|what (?:can|can not)|use .{0,10} (?:again|for)|reus\w*|spending|expire|can i use (?:my|a|the) disposable .{0,12}(?:at|to|for)|only once"))
    lost = h(r"lost|lose|losing|stolen|stole|robbed|theft|misplac\w*|missing|can not (?:find|locate)|no longer .{0,8}(?:have|access)|disappeared|taken from|pickpocket\w*|left .{0,12}(?:on|at) the")
    phone = h(r"phone|mobile|cellphone|smartphone|iphone|android|device|cell phone|handset")
    vote("lost_or_stolen_phone",17,lost and phone and not h("phone number|forgot|passcode|password"))
    vote("lost_or_stolen_card",13,lost and (card or h("wallet|purse|handbag")) and not (virtual or missing and (purchase or top or transfer) and not h("stolen|misplaced|lost .{0,12}card")))
    vote("lost_or_stolen_card",10,h(r"(?:block|freeze|cancel|deactivate) (?:my|the|a) (?:bank |debit |credit )?card"))
    vote("compromised_card",17,h(r"compromis\w*|cloned?|copied|skimmed|hack\w*|security breach|(?:stole|stolen|has|got|knows|access to) .{0,12}(?:my |card )(?:details|information|number)|(?:details|information|number) .{0,24}(?:stolen|exposed|leaked|unsafe)|someone (?:else )?(?:is |has been |might be |may be )?(?:using|used) my card|wrong hands"))
    vote("compromised_card",10,suspicious and not unknown and not withdrawal)
    vote("getting_spare_card",15,(card or h("spare|backup")) and h(r"spare|back ?up|extra card|additional .{0,12}card|(?:second|2nd|another|multiple|two|several|more than one) (?:physical |debit |bank )?cards?|how many .{0,12}cards|two of .{0,8}cards") and not h("account .{0,12} another card|transaction"))
    vote("edit_personal_details",15,h(r"(?:chang\w*|updat\w*|edit|modify|correct|wrong|new|incorrect|reset|amend) .{0,26}(?:personal|profile|phone number|mobile number|address|name|surname|birth|email|e mail|contact details|account details|number on my account)|(?:name|address|phone number|details|email|surname) .{0,20}(?:change\w*|incorrect|wrong|update\w*)|moved (?:house|home|recently)|got married") and not h("card deliver|card shipped"))
    vote("terminate_account",16,h(r"(?:clos\w*|delet\w*|terminat\w*|shut\w*|deactivat\w*|cancel\w*|remov\w*|suspend|end) .{0,25}(?:account|membership|service|profile)|no longer (?:want|need|use) .{0,15}(?:account|service)|not (?:want|need) .{0,18}account any ?more|leave (?:revolut|your bank)"))
    source = h(r"(?:source|origin|proof|evidence) of (?:my |the |these )?(?:funds|money|income|funding|wealth|earnings)|where .{0,18}(?:money|funds|income|wealth) .{0,12}(?:come|came|comes|originat\w*)|(?:prove|verify|justify|confirm|explain) .{0,18}(?:income|earnings|wealth|funding|where .{0,15}money)|payslips?|pay slips?|source of my deposit")
    vote("verify_source_of_funds",19,source)
    identity = h(r"identit\w*|identif\w*|id|passport|licen[cs]e|who i am|proof of address|verif\w*|kyc|documents?|selfie")
    if identity and not (top and not h("identity|passport|licen[cs]e")):
        vote("verify_my_identity",8.5)
        vote("why_verify_identity",13,h(r"why|what .{0,12} (?:reason|purpose)|necessary|really need|do i (?:have|need) to (?:verify|prove|identify|confirm|provide|give)|mandatory|what .{0,16} (?:needed|required) for|without .{0,12}(?:verif\w*|id)|required to (?:verify|identify)|is it required") and not (rejected or failure))
        vote("unable_to_verify_identity",14,(failure or rejected or pending or h("not verified|not been verified|not verifying|not validate|not recognising|keeps asking|taking .{0,8}long|verification .{0,16} not|will not verify|not being verified")))
    refund = h(r"refund\w*|charge ?back|reimburs\w*|money back|disput\w*")
    if refund:
        vote("request_refund",10)
        vote("refund_not_showing_up",14,missing or timing or pending or h(r"refunded|been issued|waiting|was promised|yet|not .{0,16} (?:back|refund)|merchant .{0,20}(?:issued|processed)|told .{0,24} refunded|refund .{0,14} ago"))
    vote("refund_not_showing_up",11,h(r"(?:returned|sent back) .{0,16}(?:item|purchase|product|goods|merchandise)") and missing)
    vote("request_refund",10,h(r"not (?:happy|satisfied)|faulty goods|item .{0,16}never arrived|did not receive .{0,12}(?:goods|order|item)|seller .{0,18} (?:cancelled|scam)|cancel (?:a |my |the )?(?:purchase|card payment)"))
    delivery = h(r"deliver\w*|shipp\w*|arrival|arriv\w*|mail|post|track\w*|dispatch\w*|waiting for my card|receive my .{0,8}card")
    ordered = h("ordered|requested|applied for|order status|waiting|not received|not arrived|not gotten|not got")
    if (card or delivery) and not (literaltransfer or withdrawal or refund):
        vote("card_arrival",8,delivery and not timing or ordered and missing)
        vote("card_arrival",13,h(r"track\w*|where .{0,16}(?:my|the) .{0,12}card|not (?:yet )?(?:got|received|arrived|come)|never .{0,12}(?:arrived|came|received)|still (?:not|no|waiting)|taking so long|already .{0,16}(?:week|days)|(?:days?|weeks?) ago|not .{0,8}delivered|has not .{0,8}(?:turned|shown) up|late|overdue") and (card or delivery) and not h(r"where .{0,10}(?:use|get|find|change|see)"))
        vote("card_delivery_estimate",10,delivery and timing or card and h(r"how long .{0,30}(?:get|receive)|when .{0,20}(?:get|expect|receive)"))
        vote("card_delivery_estimate",15,h(r"express|expedit\w*|faster|fastest|urgent\w*|as soon as possible|rush|speed up|delivery options|delivery times?|next day|quicker|quickly") and (delivery or card))
        vote("get_physical_card",14,h(r"in person|collect|pick ?up|at (?:your|a|the) (?:branch|office)|in a branch|in store") and not merchant)
        vote("order_physical_card",8,h(r"order|request|apply for|send me|send .{0,10}card|cost .{0,20}card|pay for .{0,12}card|card .{0,12}(?:cost|free)"))
        vote("get_physical_card",7,h("physical|actual|plastic|real card") and not ordered)
    countries = h(r"countr\w*|territor\w*|nation\w*|region\w*|residen\w*|citizen\w*|live|living|based|reside|uk|us|usa|europe|india|france|spain|germany|australia|united states|canada|united kingdom|america|worldwide|abroad|international")
    vote("country_support",8,countries and not (purchase or top or transfer or withdrawal or exchange))
    vote("country_support",12,countries and h(r"open|register|sign up|offer|services?|available|supported|resident|residents|live|living|based|citizen|apply|reside|get an account") and not (withdrawal or explicit_top))
    vote("card_acceptance",11,(card or merchant) and h(r"where .{0,25}(?:use|spend|pay)|accept(?:s|ed)?|places?|everywhere|anywhere|worldwide|around the world|travel\w*|on holiday|in other countries|abroad|overseas|can i (?:pay|spend|use)|online shopping") and not (withdrawal or top or exchange or rejected or failure or virtual))
    return {"answer": max(_TEXT, key=lambda k: strength.get(k,0) + sim.get(k,0))}
