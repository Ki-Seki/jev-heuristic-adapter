import re
import math
import unicodedata
from collections import Counter
from functools import lru_cache

# Representative ways of talking about each service. These also provide a
# lexical back-off for very short questions that leave some arguments implicit.
_TEXT = {
    "activate_my_card": "how do I activate my new card|card activation instructions|my card has arrived how do I start using it|enable my new card|unable to activate it|do I need to activate the plastic",
    "age_limit": "how old must I be|can my teenager open an account|minimum age requirement|can I order a card for my child|I am only sixteen|is there an age restriction",
    "apple_pay_or_google_pay": "can I use apple pay|does google pay work|add card to my apple wallet|top up using android pay|can't add my card on my iphone wallet",
    "atm_support": "where can I withdraw cash|which cash machines can I use|is there a list of supported ATMs|how do I know which ATM accepts my card|locations to take money out|where can I find a cashpoint",
    "automatic_top_up": "set up automatic top ups|can you add money automatically|when the balance drops below a threshold|disable auto reload|recurring top up|keep my balance from getting too low",
    "balance_not_updated_after_bank_transfer": "transferred money to my account but my balance has not increased|I sent funds from my bank and they have not arrived in my account|missing incoming bank transfer|added money by transfer but it is not showing|where is my bank transfer deposit",
    "balance_not_updated_after_cheque_or_cash_deposit": "I deposited cash and my balance has not changed|why hasn't my cheque cleared|missing check deposit|I paid cash into my account and it is not showing|how long before my cash deposit shows up",
    "beneficiary_not_allowed": "why is beneficiary not allowed|transfer to this beneficiary isn't permitted|can't add a payee|restricted beneficiary|why is this recipient not supported|transfer to a cryptocurrency exchange",
    "cancel_transfer": "cancel my bank transfer|can I recall a transfer I just made|I transferred to the wrong account|stop money from being sent|reverse a transfer|I entered the wrong bank details for a payment",
    "card_about_to_expire": "my card expires soon|what happens after the expiration date|do I get a replacement on expiry|my card is out of date|renew my card",
    "card_acceptance": "where is my card accepted|can I use this card abroad|which shops take your cards|can I pay with it everywhere|can I use my card for online purchases|in what countries can I use my card",
    "card_arrival": "where is my card|track the card I ordered|still waiting for my card|my new card has not arrived|has my card been sent yet|the delivery date has passed|how can I check my card delivery status",
    "card_delivery_estimate": "how long will it take to deliver my card|can I get my card more quickly|express delivery options|what is the estimated delivery time|can you rush delivery|how soon can I get a new card",
    "card_linking": "how can I link my existing card to the app|associate my card with my account|link two cards|my card won't link|how do I reconnect my old card|can I use my old card with my new account",
    "card_not_working": "my card does not work|my chip is damaged|my card is broken|my new card cannot be used|the card reader won't read my card|my card stopped functioning",
    "card_payment_fee_charged": "fee for paying with my card|additional fee when I bought something|card payment surcharge|cost for making a card payment overseas|why did I pay a fee on a purchase|merchant charged me extra",
    "card_payment_not_recognised": "I don't recognize a payment on my card|a transaction that I didn't make|unfamiliar purchase in my statement|there is a card payment that is not mine|I was billed for something I didn't buy|who is this merchant|I don't know where this transaction came from",
    "card_payment_wrong_exchange_rate": "the conversion rate on my card purchase was incorrect|paid in foreign currency at the wrong exchange rate|your rate didn't match the rate for my purchase|my overseas payment used a bad rate|charged too much after currency conversion",
    "card_swallowed": "ATM swallowed my card|cash machine kept my card|I can't get my card out of the ATM|cashpoint did not return my card|the machine ate it|my card is stuck in the machine",
    "cash_withdrawal_charge": "fee on a cash withdrawal|charged extra for taking money out|how much does withdrawing at an ATM cost|unexpected charge for using cash machine|are cash withdrawals free",
    "cash_withdrawal_not_recognised": "I don't recognize an ATM withdrawal|cash was withdrawn but it wasn't me|someone else withdrew money|there's a cash withdrawal I did not make|I have not used any ATM",
    "change_pin": "how can I change my PIN number|reset my card PIN|change PIN at a cash machine|can I choose a different PIN|is it possible to modify my pin code",
    "compromised_card": "someone has my card details|I think my card has been compromised|my details were stolen|I still have my card but someone is using it|protect my card from fraud|my card was cloned|someone has access to my card",
    "contactless_not_working": "contactless feature doesn't work|tap to pay stopped working|wave payment failing|cannot pay by tapping my card|chip and pin works but not contactless",
    "country_support": "what countries can I get an account in|do you support residents of the US|can I sign up if I live abroad|which countries are you available in|do you issue cards in my country|can someone from Canada apply",
    "declined_card_payment": "my card payment was declined|merchant rejected my card|my purchase didn't go through|transaction refused in a shop|why was my online payment denied|there were enough funds but the payment was refused",
    "declined_cash_withdrawal": "why was my ATM withdrawal declined|cannot withdraw money from a cash machine|cash withdrawal rejected|the ATM refused my card|cash withdrawal failed",
    "declined_transfer": "why did you decline my transfer|bank transfer rejected|transfer was refused|it won't allow me to send this transfer|bank denied my money transfer",
    "direct_debit_payment_not_recognised": "I do not recognize this direct debit|unknown direct debit payment|I didn't set up this direct debit|direct debit taken without my permission|unauthorized automatic debit",
    "disposable_card_limits": "is there a limit on disposable cards|how many times can I use a disposable card|maximum number of disposable payments|restrictions on single use virtual cards|daily spending limit on disposable card",
    "edit_personal_details": "I want to change my personal details|how do I update my address|my name has changed|new phone number|edit my profile|I moved house|change my email address",
    "exchange_charge": "is there a fee for exchanging money|currency exchange commission|does conversion cost extra at the weekend|what charges apply when I exchange currencies|is exchanging currencies free",
    "exchange_rate": "how is the exchange rate calculated|what conversion rate do you use|where do your currency rates come from|current foreign exchange rate|how do I check the interbank rate",
    "exchange_via_app": "how do I exchange currency in the app|can I convert my balance into euros|where is the exchange function|change dollars to pounds|how do I buy foreign currency|exchange between currencies",
    "extra_charge_on_statement": "unexpected extra charge on my statement|why did I get charged an extra dollar|I see a small charge of one pound|what is this extra euro for|temporary verification charge on my account|I see an extra charge on my account",
    "failed_transfer": "my bank transfer failed|transfer didn't go through|what caused an unsuccessful transfer|there is an error when I try to transfer money|trouble making a transfer|my transfer keeps failing",
    "fiat_currency_support": "which currencies can I hold|can I have a balance in more than one currency|list of supported fiat currencies|do you support dollars|can I keep pounds and euros in my account|which currency accounts do you offer",
    "get_disposable_virtual_card": "how do I get a disposable virtual card|what is a disposable card|one time use card|where do I find a single use virtual card|I need a temporary card number",
    "get_physical_card": "how do I get a physical card|can I receive an actual plastic card|where can I get a real card|will I get a PIN with my physical card|I only have a virtual card and need a physical one",
    "getting_spare_card": "can I have a spare card|I need a second card|can I get an extra card on the same account|backup card|can I get another card for my wife|how many cards can I have",
    "getting_virtual_card": "how do I get a virtual card|where is my virtual card|can you issue a digital card|do you offer virtual cards|how much for a virtual card|need a card I can use online immediately",
    "lost_or_stolen_card": "I lost my card|someone stole my wallet|my card was stolen|cannot find my card anywhere|I misplaced my credit card|freeze a missing card|left my card behind",
    "lost_or_stolen_phone": "my phone has been stolen|lost phone with the app on it|my mobile is missing|I no longer have access to my device|I lost my smartphone",
    "order_physical_card": "how do I order a card|cost of ordering a card|how much is the first card|is there a fee to get a card|I would like to order a new physical card|how can I request a card|will I have to pay for delivery",
    "passcode_forgotten": "forgot my app passcode|I don't remember my password|I can't log in to the app|how can I reset my login code|forgot my access code|forgotten app pin",
    "pending_card_payment": "my card payment is pending|why is a purchase still processing|how long can a card payment be pending|pending authorisation from merchant|the transaction is not completed|a payment has been pending for days",
    "pending_cash_withdrawal": "cash withdrawal pending|why is my ATM transaction still pending|my cash withdrawal hasn't been completed yet|withdrawal shows as processing",
    "pending_top_up": "why is my top up pending|added money by card but it is still processing|how long will a pending top up take|my top up has been pending for hours",
    "pending_transfer": "my transfer is still pending|I have an outgoing transaction|outbound payment is processing|why is my bank transfer on hold|money transfer stuck in pending|I made a transfer and it hasn't completed",
    "pin_blocked": "my PIN is blocked|I entered the wrong PIN three times|too many incorrect PIN attempts|how do I unblock my pin|locked out of my card after several attempts",
    "receiving_money": "how can someone send me money|can I receive my salary here|how do I receive a payment from a friend|I want to get money from another person|what information do people need to send me money",
    "refund_not_showing_up": "I am still waiting for a refund|refund from merchant isn't showing up|how long does a refund take|store issued a refund but I haven't received it|where is my refund|I returned an item but the money has not come back",
    "request_refund": "how do I request a refund|I would like my money back for a purchase|dispute a payment|how can I reverse a card payment|the merchant won't refund me|cancel a purchase and get reimbursed",
    "reverted_card_payment": "why was my card payment reverted|money from my purchase came back|merchant payment has been reversed|payment disappeared from my statement and funds are back|payment returned to my account",
    "supported_cards_and_currencies": "which cards and currencies can I use to top up|can I add money using American Express|what cards are supported for top ups|can I use a prepaid card to load money|top up in foreign currency",
    "terminate_account": "please close my account|how do I terminate my account|I don't want to be a customer anymore|cancel my membership|delete my account permanently",
    "top_up_by_bank_transfer_charge": "is there a charge for topping up by bank transfer|fee on incoming transfer|what does adding money from my bank cost|will my bank charge me to top up|fees on a bank transfer into my account",
    "top_up_by_card_charge": "fee for topping up with a card|charge to add money by credit card|how much does a card top up cost|I was charged for loading money using my debit card",
    "top_up_by_cash_or_cheque": "can I deposit cash or a cheque|where do I send a check|top up my account with banknotes|can I add cash at a branch|how do I deposit a cheque",
    "top_up_failed": "my top up failed|can't add money to my account|funding my account by card didn't work|why was my top up declined|top up unsuccessful",
    "top_up_limits": "maximum amount I can top up|is there a limit to how much I can add|minimum top up|daily funding limits|can I increase my top up allowance",
    "top_up_reverted": "my top up was reverted|the top up has been reversed|money I added went back to the original card|why did my top up disappear|my top up was returned",
    "topping_up_by_card": "how do I top up using my debit card|add money with a card|can I top up with someone else's card|how do I put money on my card|using a credit card to fund my account|where do I add money",
    "transaction_charged_twice": "I was charged twice for the same transaction|duplicate card payment|the same payment appears two times|merchant charged me multiple times|billed twice for one purchase",
    "transfer_fee_charged": "fee for sending a transfer|why did my international transfer cost extra|charged for a bank transfer|recipient received less than I sent|is it free to send money abroad",
    "transfer_into_account": "how can I transfer money into my account|what are my bank details for a transfer|where is my IBAN|can I add money by bank transfer|transfer from another bank to this account|do I use swift or sepa",
    "transfer_not_received_by_recipient": "the recipient hasn't received my transfer|I sent money but my friend hasn't got it|transfer completed but not received at other end|beneficiary says the funds never arrived|where is the money I sent to someone",
    "transfer_timing": "how long will a transfer take|when should a bank transfer arrive|how many days to send money internationally|is a bank transfer instant|time for the recipient to get the money",
    "unable_to_verify_identity": "unable to verify my identity|my ID was rejected|verification keeps failing|can't upload my passport|the app won't accept my photo|I am having trouble verifying my account",
    "verify_my_identity": "how do I verify my identity|what documents are required for verification|can I use my driving licence as ID|how to prove who I am|what forms of identification do you accept",
    "verify_source_of_funds": "verify source of funds|how do I prove my income|why do you need my payslip|documents showing where my money comes from|evidence of source of wealth",
    "verify_top_up": "how do I verify a top up|what is the top up verification code|where can I find the four digit code on my statement|card deposit verification|verify my payment card for adding money",
    "virtual_card_not_working": "my virtual card doesn't work|virtual card was declined|I can't pay with my virtual card|trouble using digital card online|virtual card isn't accepted",
    "visa_or_mastercard": "will I get a visa or mastercard|can I choose the card network|do you issue visa cards|I would prefer a mastercard|do you offer both visa and master card",
    "why_verify_identity": "why must I verify my identity|why do you need photo ID|why is identity verification necessary|do I have to prove who I am|why do you need so much personal information",
    "wrong_amount_of_cash_received": "the ATM gave me the wrong amount of cash|account debited but no cash came out|machine only dispensed part of my money|I got less cash than requested|withdrawal amount doesn't match what I received",
    "wrong_exchange_rate_for_cash_withdrawal": "wrong exchange rate for cash withdrawal|I withdrew money and got a bad rate|incorrect conversion at the ATM|bad exchange rate when taking cash out abroad",
}

def _norm(s):
    s = unicodedata.normalize("NFKC", s).lower().replace("’", "'").replace("`", "'")
    s = re.sub(r"n['’]?t\b", lambda m: " not", s) if False else s
    s = re.sub(r"\b(?:can't|cant|cannot)\b", "can not", s)
    s = re.sub(r"\b(?:won't|wont)\b", "will not", s)
    s = re.sub(r"\b(can|could|would|should|do|does|did|is|are|was|were|have|has|had)n'?t\b", r"\1 not", s)
    s = re.sub(r"\bi'?ve\b", "i have", s)
    s = re.sub(r"\bi'?m\b", "i am", s)
    s = re.sub(r"\b(it|there|that|what|where|who|here|how)'s\b", r"\1 is", s)
    s = s.replace("£", " gbp ").replace("$", " usd ").replace("€", " eur ")
    s = re.sub(r"[-_/]", " ", s)
    s = re.sub(r"\b(topp?ed|topping|top)[ ]*(ups?)\b", r"topup", s)
    s = re.sub(r"\b(auto)\s*topup\b", "auto topup", s)
    s = re.sub(r"\bmaster\s*card\b", "mastercard", s)
    s = re.sub(r"\bpay\s*pass\b", "paypass", s)
    s = re.sub(r"\bpin\s*number\b", "pin", s)
    s = re.sub(r"\ba\.t\.m\.?", "atm", s)
    s = re.sub(r"\bu\.s\.(?:a\.)?", "usa ", s)
    s = re.sub(r"\breciev", "receiv", s)
    s = s.replace("recogniz", "recognis").replace("authoriz", "authoris").replace("beneficary", "beneficiary")
    return " ".join(re.findall(r"[a-z0-9]+|%", s))

_STOP = set("a an the i me mine my of in on with or and not that this there it if is was be are as at for can could do does did have has had you your to will would please how why what some so just from am".split())

def _features(s):
    words = _norm(s).split()
    feat = Counter()
    last = ""
    for w in words:
        if w in _STOP:
            continue
        if len(w) > 5:
            w = re.sub(r"(ing|ed|s)$", "", w)
        feat[w] += 1.0
        if last:
            feat[last + ":" + w] += 0.75
        last = w
        if len(w) >= 4:
            for i in range(len(w)-2):
                feat["~" + w[i:i+3]] += .20
    return feat

@lru_cache(maxsize=1)
def _index():
    rows = []
    df = Counter()
    for label, phrases in _TEXT.items():
        for phrase in [label.replace("_", " ")] + phrases.split("|"):
            f = _features(phrase)
            df.update(f.keys())
            rows.append((label, f))
    idf = {k: math.log(1 + len(rows)/(1+v)) for k, v in df.items()}
    indexed = []
    for lab, f in rows:
        wt = {k: v*idf[k] for k,v in f.items()}
        indexed.append((lab, wt, math.sqrt(sum(v*v for v in wt.values())) or 1.0))
    return indexed, idf

def _nearest(t):
    rows, idf = _index()
    f = {k: v*idf[k] for k,v in _features(t).items() if k in idf}
    scores = {}
    for lab, wt, n in rows:
        s = sum(v*f.get(k, 0) for k,v in wt.items())/n
        hi, lo = scores.get(lab,(0,0))
        if s >= hi:
            hi, lo = s, hi
        elif s > lo:
            lo = s
        scores[lab] = hi,lo
    return max(scores, key=lambda k: scores[k][0]+.14*scores[k][1])

def _classify(t):
    def q(rx):
        return re.search(r"\b(?:" + rx + r")\b", t) is not None

    card = q(r"cards?|debit|credit|visa|mastercard|plastic")
    virt = q(r"virtual|digital card|online only card|electronic card")
    disposable = q(r"dispos\w*|throwaway|throw away|single use|one (?:time|use)|temporary (?:virtual )?card|use once")
    cashout = q(r"atms?|a t m|cashpoints?|cash point|cash (?:machine|dispenser|withdraw\w*)|teller machine|withdraw\w*|withdrew|withdrawing|took out|taking out|(?:take|taking|took|get|getting|got|pull\w*) (?:any |some |my |the |more |enough )?(?:cash|money|funds) out|(?:take|get|taking|getting|pulling) out (?:some |my |any |more )?(?:cash|money|funds)")
    xfer = q(r"transfer\w*|wired?|wiring|remit\w*|iban|swift|bacs|sepa|beneficiar\w*|payee|recipients?|outgoing|outbound|(?:send|sent|sending|move|moving|moved) (?:my |some |the |any |a |more )?(?:money|cash|payment|funds|gbp|usd|eur)|(?:money|funds) (?:i )?(?:sent|send)|sent .{0,30}(?:money|funds|bank account)|(?:pay|paid|paying) (?:my |a )?(?:friend|relative)")
    top = q(r"topup|top ups?|top .{1,30} up|topped .{1,30} up|topping .{1,30} up|load\w*|reload\w*|recharg\w*|(?:add|adding|added|put|putting|deposit\w*) (?:more |some |any |additional |extra |enough |my |the |new )?(?:money|funds|cash|balance|gbp|usd|eur)|fund(?:ing|ed)? (?:the |my |this |an? )?(?:account|card|wallet)|funding card|(?:add|added|adding) to (?:my |the )?(?:account|balance|card)")
    bank = q(r"banks?|banking|wire|iban|swift|sepa|ach|transfers?|transferring|transferred")
    cashdep = q(r"cheques?|checks? deposit|deposit(?:ed|ing)? (?:a |the |my |this |some )?checks?|(?:a|by|with|my|via|personal|paper|in a) check|checks|notes and coins|banknotes?|paper money|physical (?:cash|money)|cash deposits?|deposit(?:ed|ing|s)? (?:my |some |the |in |with )?cash|cash (?:or|and) check|(?:via|using|by|with|through) cash|(?:pay|put|add|load)(?:ing|ed)? (?:some )?cash (?:in|into|to|at|on)|cash (?:in|into) my account")
    exch = q(r"exchange|conversion|convert\w*|forex|foreign exchange|fx|interbank|exchanged|exchanging|converted")
    rate = q(r"rates?")
    fee = q(r"fees?|commissions?|surcharge\w*|cost\w*|charg(?:ing|e|ed|es)|pricing|price|free|expensive|pay extra|extra (?:money|amount)|deducted extra|how much .*pay|do i (?:have|need) to pay|is there .* to pay|any .*pay for")
    bad = q(r"fail\w*|unsuccessful\w*|unable|problem\w*|trouble|difficult\w*|error|issues?|can not|could not|will not|would not|did not (?:work|go through|succeed)|not (?:working|work|function\w*|going through|successful|accepted)|stopped working|does not (?:work|go through|let|allow)|unsuccessful|not able|impossible|no luck|nothing happens|not letting")
    decline = q(r"declin\w*|reject\w*|den(?:y|ied|ying)|refus\w*|not (?:accept\w*|authorised|approved|permitted)|not allow\w*|not being accepted|turned down")
    pending = q(r"pending|processing|on hold|in progress|stuck|still (?:being |not )?(?:processed|completed|incomplete)|not (?:complete[d]?|gone through) yet|has not (?:gone through|completed)|taking (?:so|too|a long|longer)|not been (?:processed|completed)|has not cleared|not (?:been )?cleared|remains incomplete|waiting to (?:clear|complete)")
    reverse = q(r"revert\w*|reversal|reversed|bounced? back|sent back|return(?:ed)?|back (?:on|in|into|to) my (?:account|balance|card)|(?:money|payment|funds|topup) (?:went|came|is|was credited|was sent) back|credited back|disappeared")
    timing = q(r"how (?:long|soon|fast|quickly|much time|many (?:business |working )?(?:days|hours|weeks))|when (?:can|will|should|would|do|does|might|am|is)|time ?(?:frame|scale|limit)|duration|length of time|what time|take long|long .*take|instant(?:ly|aneous)?|how late|what.*(?:time|day) .*arrive|what is the .*time|fastest|quicker|faster|speed up|days .*take|usually take|normally take")
    missing = q(r"not (?:yet |been |seem to |actually |still )?(?:receiv\w*|see\w*|show\w*|appear\w*|arriv\w*|reflect\w*|chang\w*|updat\w*|increas\w*|credit\w*|add\w*|get|got\w*|go(?:ne)? (?:in|through)|com(?:e|ing)|reach\w*|clear\w*|there|in my account)|never|yet to|still waiting|where (?:is|are|did)|missing|not .*balance|nothing|no (?:money|funds|sign|change|record)|did not get|not.*(?:arrived|landed|received)|not hit")
    unknown = q(r"recogni\w*|unrecogni\w*|unfamiliar|unknown|unauthoris\w*|fraud\w*|suspicious|not (?:me|mine|my transaction|my payment|remember|recall|know|make|made|buy|purchase|spend|use|withdraw|authorise|do this|do that|do it|do any)|never (?:made|used|bought|purchased|spent|withdrew|authorised|been|shopped|went|visited)|not .*by me|without (?:my )?(?:knowledge|permission|consent|authorisation)|someone (?:else )?(?:used|made|withdrew|has used|took)|did not .*make|no idea|not sure (?:who|where|what)|strange|was not (?:at|in)|not even (?:in|been)|not been (?:to|at)|have not (?:bought|used|made|withdrawn)|never .*there")
    limit = q(r"limits?|limited|limitations?|maximum|max|minimum|min|how (?:many|often|much)|number of|restrictions?|restrict\w*|cap(?:ped)?|more than|less than|at (?:once|a time)|per (?:day|week|month)|each (?:day|week|month)|times (?:can|a|per)|allowance|upper bound")
    use = q(r"payments?|purchas\w*|bought|buy\w*|paid|paying|merchant|retailer|shop\w*|store|spent|spend\w*|transactions?|pay")

    # Certain objects have their own support queue irrespective of the
    # operation (wallet integration, direct debit, trapped cards, etc).
    if q(r"apple ?pay|google ?pay|android ?pay|g ?pay|apple wallet|google wallet|pay with (?:my )?iphone|wallet (?:on|to) my iphone"):
        return "apple_pay_or_google_pay"
    if q(r"direct debits?|directdebit|(?:unauthorised|unrecognised) (?:automatic|recurring) debit"):
        return "direct_debit_payment_not_recognised"
    if q(r"swallow\w*|(?:machine|atm|cashpoint) .{0,40}(?:ate|eaten|eat|eats|kept|keep|retained|captured|took|held|trap\w*|will not (?:release|return|give)|did not (?:return|give)) .{0,20}card|card .{0,55}(?:stuck|trapped|eaten|retained|captured|left|jammed) .{0,20}(?:machine|atm|cashpoint)|(?:machine|atm|cashpoint) .{0,20}(?:has|still has|eats?) my card|(?:get|give|got|have|want) my card (?:out|back)") and (cashout or q(r"machine|swallow\w*|ate my card")):
        return "card_swallowed"
    if cashout and card and q(r"not (?:return|eject|release)|not come (?:back )?out|left .{0,12}card in|not get .{0,10}card back|took my card|not give .*card back|not spit|stuck in|remained in"):
        return "card_swallowed"
    if q(r"contactless|contact less|tap (?:and|to) pay|paywave|paypass|wave (?:the|my) card|tapp?ing (?:the|my) card|tap (?:the|my) card|nfc|pay by (?:touch|tap)|touch and go"):
        return "contactless_not_working"
    if disposable and (card or virt or q(r"disposable")):
        if limit and not q(r"how much (?:is|does|will .*cost)|how much .*cost"):
            return "disposable_card_limits"
        if virt and (bad or decline) and not q(r"get|order|create"):
            return "virtual_card_not_working"
        return "get_disposable_virtual_card"
    if q(r"auto(?:matic\w*)? (?:card |bank )?(?:topup|reload|recharge|funding)|auto ?reload|recurring topup") or (top and q(r"automatic\w*|auto|regularly|recurring|threshold|whenever|runs? low|drops? below|falls? below|low balance|certain (?:amount|balance)|schedule\w*|set .*trigger")):
        return "automatic_top_up"

    if q(r"(?:source|origin|proof|evidence|provenance) of (?:my |the |these |one s )?(?:funds|funding|wealth|income|earnings|money|salary)|(?:verify|prove|justify|confirm|validate|document) .{0,25}(?:income|salary|earnings|funding source)|where .{0,25}(?:funds|money|income|funding) (?:came|comes|is coming|originat\w*) from|pay ?slips?|income (?:verification|proof)|source of my deposit"):
        return "verify_source_of_funds"
    if q(r"expir\w*|renew\w*|out of date|valid thru|valid through|runs out (?:soon|next|this)") and not q(r"passport|licen[cs]e|identification|disposable|topup|verification code"):
        return "card_about_to_expire"
    if q(r"(?:age|ages|aged|underage|minor|teenager|teenage|teens?|child|children|kid|kids|daughter|son|guardian|parental|under 18|under eighteen|over 18|turn 18|turn eighteen|years? old|how old|youngest|youth|adolescent|sixteen|seventeen)") and not q(r"(?:stole|used|sent|transfer|bought|charged)"):
        return "age_limit"
    if q(r"(?:close|closing|closed|delete|deleting|terminate|terminating|deactivate|cancel|shut|remove|disable|discontinue) .{0,26}(?:account|membership|profile)|account (?:closure|termination|cancellation)|no longer (?:need|want|use) .{0,14}(?:account|service)|(?:not|no longer) (?:want|wish) to (?:be a customer|have an account|use .{0,14}service)|stop (?:being a customer|using .{0,12}service)|leave (?:revolut|your bank)"):
        return "terminate_account"

    lost = q(r"lost|loss|stolen|stole|steal\w*|misplaced|missing|disappeared|pickpocket\w*|robbed|mugged|taken|snatched|not find|not locate|left .*behind|forgot .{0,16}(?:at|in)|no longer have|not have .*anymore")
    if q(r"phone|mobile|cellphone|smartphone|cell phone|handset|iphone|device") and (lost or q(r"not have access|no access|not access|someone .*has my|not in my possession")) and not q(r"(?:forgot|lost) .{0,16}(?:passcode|password)|(?:tracking|card) .* (?:phone|app).*missing"):
        return "lost_or_stolen_phone"
    if q(r"passcode|password|pass code|pass word|log ?in|log ?on|sign in|app (?:access )?(?:pin|code)|access code|locked out of .{0,14}(?:app|account)") and not q(r"verif\w*|identit\w*|topup") and (not card or q(r"forgot\w*|passcode|password|log ?in")):
        return "passcode_forgotten"
    if q(r"pin|personal identification number|pinblock|wrong code|incorrect code|tried .*times") and q(r"block\w*|unblock\w*|locked|unlock\w*|3 times|three times|thrice|attempts|too many|tries|multiple times|wrong .*times|incorrect .*times|exceeded"):
        return "pin_blocked"
    if q(r"pin|personal identification number") and q(r"chang\w*|reset|new pin|modify|different pin|choose|set .{0,15}pin|update|alter|replace|custom\w*") and not q(r"new pin .*arriv|new pin .*mail"):
        return "change_pin"
    if q(r"activat\w*|enable my (?:new )?card") and not q(r"activated .{0,20}(?:but|and now)") and not top:
        return "activate_my_card"
    if q(r"phone number|surname|last name|maiden name|personal (?:details|info\w*|data)|home address|residential address|date of birth|email|e mail|my name|contact (?:information|details)|my address|married|my profile|moved (?:house|home|address|recently|to)|new (?:address|number)|birth date") and not q(r"why .*need|card .*deliver\w*|transfer|send money") and not q(r"verif\w*|identity"):
        return "edit_personal_details"

    if (top or q(r"(?:credit|debit|payment|funding) card|card (?:deposit|statement)|bank statement")) and q(r"verif\w*|confirm\w* code|authenticat\w*|(?:digit|security|topup) code") and not q(r"identity|passport|small charge|(?:gbp|usd|eur) 1\b"):
        return "verify_top_up"
    if q(r"identity|identification|verify|verification|verifying|verified|my id|an id|photo id|passport|national id|driv\w* licen[cs]e|proof of address|proof of id|proof of residence|prove (?:it is me|who i am)|selfie|id card|id document|kyc") or q(r"(?:what|which|submit|upload) documents|documents (?:are )?(?:required|needed)|why .*personal (?:info\w*|data|details)"):
        if bad or decline or q(r"not (?:verify|verified|match|valid|recognis\w*|verifying|let me|being verified)|keeps asking|taking so long|still waiting|not .*accept|verification .*stuck"):
            return "unable_to_verify_identity"
        if q(r"why|what .*reason|reason for|necessary|really (?:need|have) to|do i (?:have|need) to|is it (?:mandatory|required)|purpose|is .*required|without (?:verif\w*|id)|must i"):
            return "why_verify_identity"
        return "verify_my_identity"

    if q(r"compromis\w*|clon(?:e|ed|ing)|hack\w*|skimmed|copied|(?:card|account) (?:information|info|details|number) .{0,24}(?:stolen|taken|exposed|leaked)|(?:stole|stolen|has|have|knows?|using|used|got|copied|obtained) (?:hold of )?(?:my|the) (?:card|account) (?:information|info|details|number)|(?:someone|somebody|another person) .{0,38}(?:using|access to|used|uses) my card|card .{0,22}(?:used|using) .{0,12}(?:someone|somebody)|in .{0,10}possession .*used"):
        if not (cashout and unknown):
            return "compromised_card"
    if (lost and q(r"card|wallet|purse")) and not q(r"missing (?:payment|transfer|transaction)|missing .{0,10}balance|not find .{0,18}(?:virtual|pin|code|option)|details|in the (?:mail|post)|delivery|not arrived|never arrived|new card .*missing") and not (xfer or cashout or top or virt or unknown or reverse) and not q(r"refund|money .*missing|missing money|money .*lost"):
        return "lost_or_stolen_card"
    if q(r"(?:freeze|report|block) my (?:stolen |missing |lost )?card") and not q(r"fraud|compromised|pin|payment"):
        return "lost_or_stolen_card"

    if q(r"beneficiar\w*|payee|recipient") and q(r"not allowed|not (?:supported|allowing|permitted|authorised|valid|eligible)|unsupported|forbidden|restricted|invalid|not add|can not add|unable to add|will not let me|can not send|not able to send|not allow|not accept|not letting"):
        return "beneficiary_not_allowed"
    if xfer and q(r"cryptocurrenc\w*|crypto|bitcoin|gambling|betting|broker|restricted account|not allowed to (?:send|transfer)|beneficiary is blocked"):
        return "beneficiary_not_allowed"
    if xfer and q(r"cancel\w*|recall\w*|revoke|undo|call back|retract|stop .{0,24}(?:transfer|being sent|payment)|wrong (?:account|recipient|bank|person|beneficiary|details|amount)|mistak\w*|accidental\w*|changed my mind|reverse (?:my|a|this|the) transfer|get (?:it|the money|my money) back"):
        return "cancel_transfer"
    if q(r"twice|double (?:charged|charge|billed|payment|transaction)|doubl[ey] (?:debit\w*|bill\w*|charg\w*)|duplicates?|duplicated|charged .* (?:two|2|multiple|several|three|3) times|paid (?:two|2) times|more than once|two (?:identical|of the same)|same (?:payment|purchase|transaction|amount) .*(?:times|again|repeat)|two (?:payments|transactions|charges) .* (?:one|same)|(?:billed|charged) double|charged me double|charged .*again") and not q(r"pin|topup limit"):
        return "transaction_charged_twice"

    # Split timing, tracking, price and ordering questions on the same object.
    deliver = q(r"deliver\w*|shipping|shipped|ship|shipment|courier|postage|mail|post|dispatch\w*|tracking|track|arriv\w*|receive my (?:new |replacement )?card|get my (?:new )?card")
    if (card or not (xfer or cashout or top or use or q(r"refund|money|balance|funds|cheque|check|deposit"))) and deliver and not virt and not (q(r"pin|refund|send money|bank transfer|payment arrived") or cashout):
        if q(r"track\w*|where .{0,25}card|card .{0,12}where|not (?:yet |been )?(?:got|received|arrived|come|here|delivered|shown)|still (?:not|waiting)|already|waiting .*days|overdue|late|never (?:came|arrived|received|delivered)|yet to|not .*my card yet|long ago|has .{0,16}card been (?:sent|posted|shipped|dispatched)"):
            return "card_arrival"
        if timing or q(r"express|urgent\w*|hurry|expedite\w*|rush|priority|asap|overnight|next day|faster|sooner|earlier|quick\w*|estimate\w*|expected|delivery (?:time|options|date)|longest|fast delivery"):
            return "card_delivery_estimate"
        if q(r"delivery|shipping|mail|dispatch\w*|shipped|arrived|tracking|shipment|delivered") and not (fee or q(r"address|order a|order my|how .*order|activate")):
            return "card_arrival"
    if card and q(r"still waiting|not (?:get|received|gotten|got) my (?:new )?card|ordered .* (?:days|weeks|months) ago|where is my (?:new |replacement )?card|card .*not here|card has not come") and not (virt or cashout):
        return "card_arrival"
    if card and timing and q(r"order|receive|get|receiving|wait") and not (xfer or use or cashout or top or virt):
        return "card_delivery_estimate"
    if q(r"(?:re)?link(?:ed|ing)?|associat\w*|connect .{0,18}card|pair .{0,12}card|add (?:my |an? |the )?(?:existing |old |new )?card to (?:the |my )?(?:app|account)|old card .*(?:new|app|account)|(?:existing|already have a) card .*account") and card and not top:
        return "card_linking"
    if virt:
        if (bad or decline) and not q(r"(?:can not|could not|unable to) (?:get|find|order|create|see|locate)") or q(r"stopped working"):
            return "virtual_card_not_working"
        if not q(r"(?:get|want|need|order|receive) .{0,15}(?:physical|plastic|real)"):
            return "getting_virtual_card"
    if card and q(r"spare|second|2nd|back ?up|additional|extra card|another card|(?:2|two|several|multiple|more than one|more than 1|different) cards|how many cards|for my (?:wife|husband|partner)|more than one .*card") and not q(r"charg\w*|transactions?|payment|multiple times|exchange rate|extra (?:fee|dollar|pound|euro)") and not top:
        return "getting_spare_card"

    if q(r"refund\w*|reimburs\w*|money back|chargeback|charge back|(?:get|claim) .*back .*purchase|dispute|cancel .{0,20}(?:card payment|purchase|order)|returned (?:an? |the |some |my )(?:item|purchase|goods|product)|return (?:an? |the |some |my )(?:item|purchase|goods|product)") and not (top or cashout or xfer):
        if timing or q(r"still|waiting|where is|not (?:yet |been )?(?:received|getting|got|appeared|showing|arrived|here|credited|refunded|show|visible)|not (?:see|find) .*refund|never (?:got|arrived|received)|not .*account|was refunded|was issued|already|have refunded|processed|said .*refund|been refunded|expecting|promised|yet to|not .*come|did not get|not got .*back|has not|have not|returned .*but"):
            return "refund_not_showing_up"
        return "request_refund"

    if cashdep and not cashout and not q(r"check (?:the|my) (?:status|balance)"):
        if missing or pending or q(r"balance .*same|deposited|cashed|paid in|credited|balanced? .*update|update.*balance|not gone|not posted|has not cleared|account .*same|not been added"):
            return "balance_not_updated_after_cheque_or_cash_deposit"
        return "top_up_by_cash_or_cheque"

    if cashout:
        if exch or rate or q(r"conversion"):
            if not (fee and not (rate or q(r"incorrect|wrong|bad exchange"))):
                return "wrong_exchange_rate_for_cash_withdrawal"
        if unknown and not q(r"not know (?:how|why|where (?:can|to))|not recognise my card|not know (?:which|what) atm") and not (q(r"not get|did not (?:dispense|receive)|cash did not|no cash|money did not come") and not q(r"fraud|unauthorised")):
            return "cash_withdrawal_not_recognised"
        if pending:
            return "pending_cash_withdrawal"
        if q(r"wrong amount|incorrect amount|less (?:cash|money|than)|more (?:cash|money|than)|short(?:ed|changed)?|only (?:got|gave|received|dispensed|gotten|part)|(?:gave|dispensed|received|got) (?:me )?(?:only|too|less|more|half)|no (?:cash|money|bills|notes)|not (?:receive|dispense|get|give|given|come out)|never (?:dispensed|got|came out)|nothing came out|different amount|(?:debit\w*|deduct\w*|charged|taken) .*but|but .* (?:debited|deducted|charged|taken)|not the (?:right|correct|full|same) amount|missing (?:some|cash|money)|not (?:enough|all|the full amount)|nothing .*dispensed|amount .*not (?:match|right|correct)|requested .* but|asked for .* but") and not q(r"did not get .*(?:declined|fee)|not get .*work"):
            if not (decline and not q(r"debited|deducted|charged|amount|dispensed|less|short|but")):
                return "wrong_amount_of_cash_received"
        if decline or bad and not q(r"where|which|not know"):
            return "declined_cash_withdrawal"
        if fee:
            return "cash_withdrawal_charge"
        if q(r"pin") and not q(r"forgot"):
            return "change_pin"
        if q(r"foreign currency|currency rate|converted"):
            return "wrong_exchange_rate_for_cash_withdrawal"
        if not (top or q(r"deposit|physical card .*atm|physical card .*withdraw")):
            return "atm_support"

    small = q(r"(?:gbp|usd|eur) (?:1|one)(?: 00)?\b|(?:1|one|an extra|a single) (?:gbp|usd|eur|pound|dollar|euro)|(?:a|extra|another) (?:dollar|pound|euro)|small (?:amount|charge|payment|transaction)|tiny (?:charge|amount)|micro ?charge|verification charge")
    if small and (fee or use or missing or q(r"statement|account|taken")) and not q(r"maximum|minimum|exchange rate"):
        return "extra_charge_on_statement"
    # Fiat balances, exchange quotes and actually performing an exchange
    # are different requests. A rate disputed on a finished payment is not
    # a request for a quote.
    fxwrong = q(r"wrong|bad|poor|incorrect|inaccurate|differ\w*|too (?:high|low|much)|unfair|terrible|awful|overcharg\w*|badly|worse|not (?:right|correct|accurate|fair|the same|expect\w*|match)|higher|lower|not (?:the rate|what)|off|mismatch|charged more|discrepancy|mistake")
    if (exch or rate) and not (top or q(r"bitcoin|cryptocurrency exchange|transfer .*exchange")):
        if (fxwrong and not (q(r"why .* (?:fluctuate|vary)|different currencies") and not use)) or (use and rate and q(r"applied|purchase|bought|paid|used .*card|payment|transaction") and not q(r"how .*calculat|what .* rate .*use|fee for")):
            return "card_payment_wrong_exchange_rate"
        if fee and not q(r"at what (?:exchange )?rate|rate .*charged|exchange rate .*charge|rate (?:will|am|was) i .*charged") and (exch or rate) and not q(r"free account .*rate|interest rate"):
            return "exchange_charge"
        if rate or q(r"interbank|market price|calculate|calculated"):
            return "exchange_rate"
        if not q(r"hold|store|carry .*(?:currenc|account)"):
            return "exchange_via_app"

    deposit_missing = missing or q(r"not .* (?:reflected|visible|increased|updated|added|credited)|balance .* (?:same|unchanged|wrong|incorrect|low)|balance (?:is|has|did|does|was|still) not|not .*my balance|where .*deposit|nothing .*account")
    recipient = q(r"beneficiar\w*|recipient\w*|payee|receiver|other (?:person|end|account|bank)|destination|to (?:a |my |another )?(?:friend|colleague|person|brother|sister|wife|husband|mum|mom|mother|dad|father|son|daughter|partner|relative|someone|somebody|customer|supplier)|(?:they|he|she) (?:has|have|did|does|is|can|still|never)|their (?:bank |new )?account|friend .* (?:has|did|does|not|never)|person i (?:sent|paid)|to him|to her|to them|person .*sent")
    incoming = q(r"incoming|inbound|into (?:this|my|the|your|an) account|(?:to|into|in) my (?:revolut |new |app |current |personal |bank )?(?:account|balance|wallet)|from my (?:other |old |bank|current|external)|my balance|my account balance|on my balance|i (?:have not|did not|never|still have not) (?:got|received)|(?:sent|transferred|send|wired) (?:it |money |funds )?to me|(?:sent|transferred|wired) me|not (?:in|showing in|appeared in) the app|my account .* (?:updated|credited)")
    if top or xfer or (bank and incoming) or q(r"added (?:it|the amount) to|my deposit"):
        if top and q(r"verif\w*|confirmation code|digit code"):
            return "verify_top_up"
        inbound_bank = bank and (top or incoming) and not (q(r"by card|with (?:my |a )?(?:debit|credit) card") and not xfer)
        if top and reverse and not q(r"can i return|in return"):
            return "top_up_reverted"
        if fee and not q(r"not been charged|balance|pending|not received|did not receive|not arrived|failed|declined|still waiting") and not (limit and q(r"maximum|minimum|limit")):
            if inbound_bank:
                return "top_up_by_bank_transfer_charge"
            if top:
                return "top_up_by_card_charge"
            if xfer:
                return "transfer_fee_charged"
        if (decline or bad) and not (deposit_missing and not q(r"fail\w*|declined|reject\w*|refused|denied")) and not q(r"not know how"):
            if top and not (xfer and not decline):
                return "top_up_failed"
            if xfer:
                return "declined_transfer" if decline else "failed_transfer"
        if recipient and xfer and not (incoming and not q(r"other end|their account|recipient .*not|beneficiary .*not")) and (deposit_missing or q(r"not .*reached|lost|not .*got|not .*go through|not .*there|not .*delivered|claim\w*|completed .*but")) and not (timing and not q(r"not|never|still")):
            return "transfer_not_received_by_recipient"
        if pending or q(r"outgoing transaction|outbound transaction"):
            if top and not q(r"incoming bank transfer"):
                return "pending_top_up"
            if not (incoming and not q(r"pending|processing|on hold|in progress")):
                return "pending_transfer"
        if inbound_bank and deposit_missing and not q(r"where (?:is|are) my (?:account details|bank details|iban)") and not (timing and not q(r"still|not|never")):
            return "balance_not_updated_after_bank_transfer"
        if top:
            if q(r"which|types? of|what (?:kind|card|currenc)|currenc\w*|support\w*|accept\w*|american express|amex|maestro|mastercard|visa|diners|prepaid|pre paid|gift card") and not q(r"not (?:accept|work)|what .*limit|fee|verification"):
                return "supported_cards_and_currencies"
            if limit and not fee:
                return "top_up_limits"
            if deposit_missing and not q(r"where .* (?:can|how|should)|where is the .*(?:button|option)"):
                return "balance_not_updated_after_bank_transfer" if bank else "pending_top_up"
            return "transfer_into_account" if inbound_bank else "topping_up_by_card"
        if xfer and timing:
            return "transfer_timing"
        if xfer and deposit_missing and not q(r"where .* (?:details|iban|number|code)") and not (timing or q(r"where .* (?:can|how|should)")):
            if recipient or q(r"i sent|outgoing|i have sent|i transferred"):
                return "transfer_not_received_by_recipient"
            return "balance_not_updated_after_bank_transfer"
        if xfer and q(r"less|short|full amount|not the same amount|deducted"):
            return "transfer_fee_charged"
        if q(r"iban|swift|bic|routing|sort code|local account details|bank details|account number") or inbound_bank:
            if not (q(r"send me|receive|someone|friend") and not q(r"iban|swift|bic|bank details")):
                return "transfer_into_account"
        if xfer and q(r"receive|receiving|someone|friend|send me|to me|family|paid into|salary") and not q(r"i sent|i transferred"):
            return "receiving_money"
        if xfer:
            if q(r"outgoing|status|taking|incomplete"):
                return "pending_transfer"
            return _nearest(t)
    if q(r"receiv\w* .{0,18}(?:funds|money|payment|salary)|paycheck|pay cheque|salary|send me|pay me|money .*to me|paid into my account|someone .*send|from (?:a|my) friend"):
        return "receiving_money"
    if q(r"bic|sort code|routing number|account details|bank details"):
        return "transfer_into_account"
    if q(r"supported cards|what (?:kind|type|kinds|types) of cards .*accept|which cards .*accept|american express|amex|diners club"):
        return "supported_cards_and_currencies"
    if q(r"visa|mastercard") and not (use and bad) and not q(r"currency|currencies|in what countries"):
        return "visa_or_mastercard"
    if q(r"currenc\w*|fiat|euros?|dollars?|pounds?|gbp|usd|eur") and not (fee or small or (card and use)):
        if q(r"(?:dollars?|usd|pounds?|gbp|eur|euros?) (?:to|into|for) (?:dollars?|usd|pounds?|gbp|eur|euros?)|change .* (?:into|to)|switch .*currenc\w*|buy .*currenc\w*"):
            return "exchange_via_app"
        if q(r"can i|possible|hold|balance|support\w*|accept\w*|store|keep|what|different|which|multiple|currencies|offer\w*|available|account"):
            return "fiat_currency_support"
    if pending:
        return "pending_card_payment"
    if decline and not q(r"which|where|countries|anywhere|everywhere") and (use or card or q(r"declined|refused|rejected|denied")):
        if not (q(r"not accepted") and q(r"what|are there")):
            return "declined_card_payment"
    if reverse and (use or card or q(r"money|funds|balance")) and not q(r"replacement|card .*return .*mail"):
        return "reverted_card_payment"
    if unknown and (use or card or q(r"statement|charge|charged|money|debit|activity|deduction|taken|account")) and not q(r"do not know (?:how|if|where .*card|which|what .*pin)|i do not recognise my pin"):
        return "card_payment_not_recognised"
    if q(r"fraud|security breach|card security|somebody .*my card|someone .*my card"):
        return "compromised_card"
    if q(r"live|living|based|resid\w*|citizen\w*|nationality|eligib\w*|apply|applicant|sign up|signing up|open an account|supported countries|countries .*support|support .*countr\w*|what countries .*available|which countries .*available|countries .*issue|available in|offer .* in|can .* from .*get|country .*get a card|ship .*to|deliver .*to .*country|i am from") and not q(r"use my card|pay with|personal details|delivery address|cash deposit"):
        return "country_support"
    if q(r"where .* (?:use|accepted|pay with)|anywhere|everywhere|worldwide|accept\w*|abroad|overseas|countries|retailer\w*|locations?|internationally|in other countr\w*|what (?:shops|stores|businesses)|can i (?:use|pay with) .{0,20}card (?:in|at|on|for|when)") and not (fee or (bad and not q(r"not know"))):
        return "card_acceptance"
    if fee:
        if q(r"order|delivery|first card|physical card|new card|shipping|plastic card|get a card|card itself|send me a card|issuing|issue a card|cost .*card|card cost|card free"):
            return "order_physical_card"
        if (card and use or q(r"merchant|bought|purchase|shopping|card payment|paying|paid with|used my card")) and not q(r"statement|extra (?:dollar|pound|euro)|another transaction"):
            return "card_payment_fee_charged"
        if q(r"extra|extra charge|additional|statement|charged|charge|taken out"):
            return "extra_charge_on_statement"
    if bad and (card or use):
        if q(r"payment|transaction|purchase|paying|at .*store|not go through|merchant|online payment"):
            return "declined_card_payment"
        return "card_not_working"
    if q(r"broken|damaged|defective|malfunction\w*|chip .*not|stopped functioning|not usable"):
        return "card_not_working"
    if q(r"order|ordering|request a card") and card:
        return "order_physical_card"
    if q(r"physical|plastic|actual card|real card|pin .*card|card .*pin"):
        return "get_physical_card"
    return _nearest(t)

def predict(state) -> dict:
    if isinstance(state, str):
        text = state
    elif isinstance(state, dict):
        text = next((state[k] for k in ("text", "utterance", "message", "query", "question", "input") if isinstance(state.get(k), str)), "")
    else:
        text = str(state)
    if text.strip() in _TEXT:
        return {"answer": text.strip()}
    t = _norm(text)
    for key in _TEXT:
        if t == _norm(key.replace("_", " ")):
            return {"answer": key}
    return {"answer": _classify(t)}