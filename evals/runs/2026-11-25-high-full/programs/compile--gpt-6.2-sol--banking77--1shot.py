import re
import unicodedata
from functools import lru_cache


_LABELS = frozenset("""
activate_my_card age_limit apple_pay_or_google_pay atm_support automatic_top_up
balance_not_updated_after_bank_transfer balance_not_updated_after_cheque_or_cash_deposit
beneficiary_not_allowed cancel_transfer card_about_to_expire card_acceptance
card_arrival card_delivery_estimate card_linking card_not_working
card_payment_fee_charged card_payment_not_recognised card_payment_wrong_exchange_rate
card_swallowed cash_withdrawal_charge cash_withdrawal_not_recognised change_pin
compromised_card contactless_not_working country_support declined_card_payment
declined_cash_withdrawal declined_transfer direct_debit_payment_not_recognised
disposable_card_limits edit_personal_details exchange_charge exchange_rate
exchange_via_app extra_charge_on_statement failed_transfer fiat_currency_support
get_disposable_virtual_card get_physical_card getting_spare_card getting_virtual_card
lost_or_stolen_card lost_or_stolen_phone order_physical_card passcode_forgotten
pending_card_payment pending_cash_withdrawal pending_top_up pending_transfer
pin_blocked receiving_money refund_not_showing_up request_refund reverted_card_payment
supported_cards_and_currencies terminate_account top_up_by_bank_transfer_charge
top_up_by_card_charge top_up_by_cash_or_cheque top_up_failed top_up_limits
top_up_reverted topping_up_by_card transaction_charged_twice transfer_fee_charged
transfer_into_account transfer_not_received_by_recipient transfer_timing
unable_to_verify_identity verify_my_identity verify_source_of_funds verify_top_up
virtual_card_not_working visa_or_mastercard why_verify_identity
wrong_amount_of_cash_received wrong_exchange_rate_for_cash_withdrawal
""".split())

_REPLACEMENTS = (
    (r"\b(?:can['’]?t|cannot)\b", "can not"),
    (r"\bwon['’]?t\b", "will not"),
    (r"\bshan['’]?t\b", "shall not"),
    (r"\b(could|would|should|do|does|did|is|are|was|were|have|has|had|must|need)n['’]?t\b", r"\1 not"),
    (r"\b(i|you|we|they)['’](?:ve|ll|re|d|m)\b", r"\1"),
    (r"\b(it|that|there|what|where|who|how)['’]s\b", r"\1 is"),
    (r"\b(?:recognize|recognizes|recognized|recognizing)\b", "recognise"),
    (r"\b(?:unrecognized|unrecognised)\b", "not recognised"),
    (r"\b(?:unauthorized|unauthorised)\b", "not authorised"),
    (r"\b(?:authorize|authorized|authorise)\b", "authorised"),
    (r"\b(?:topup|topups|top ups|top ups?)\b", "top up"),
    (r"\b(?:top uped|topped up|topping up|toping up)\b", "top up"),
    (r"\b(?:withdr[ae]wl|withdral|withdrawl|withdrawels|withdrawals)\b", "withdrawal"),
    (r"\b(?:tranfer|trasnfer|transfert|transfered|transferring|transferr?ing|transferred|transfers)\b", "transfer"),
    (r"\b(?:cheques|checks)\b", "cheques"),
    (r"\b(?:currancy|curency|curreny)\b", "currency"),
    (r"\b(?:decliend|decilned)\b", "declined"),
    (r"\b(?:recieve|recieved|receieved|recving)\b", "received"),
    (r"\b(?:payement|paymant)\b", "payment"),
    (r"\b(?:pendng|panding)\b", "pending"),
    (r"\b(?:master card|mastercards)\b", "mastercard"),
    (r"\b(?:applepay|googlepay|gpay|androidpay|samsungpay)\b",
     lambda m: {"applepay": "apple pay", "googlepay": "google pay", "gpay": "google pay",
                "androidpay": "android pay", "samsungpay": "samsung pay"}[m.group()]),
    (r"\b(?:pass code|passcodes|passwords|pass-code)\b", "passcode"),
    (r"\b(?:contact less|contact-less)\b", "contactless"),
    (r"\bpls\b", "please"),
    (r"\b(?:usdollars|us dollars|u s dollars)\b", "usd"),
)


def _normalize(text):
    text = unicodedata.normalize("NFKC", text).casefold()
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")
    text = re.sub(r"[\-_‐‑‒–—/]+", " ", text)
    for pattern, replacement in _REPLACEMENTS:
        text = re.sub(pattern, replacement, text)
    text = re.sub(r"[^\w'€£$¥%]+", " ", text)
    return " ".join(text.split())


@lru_cache(maxsize=1024)
def _regex(pattern):
    return re.compile(r"(?<!\w)(?:" + pattern + r")(?!\w)")


_FEE = (
    r"fees?|surcharge[ds]?|commission|mark ?up|service charge|extra charges?|"
    r"(?:additional|extra|unexpected|hidden) (?:costs?|amount|money)|"
    r"charged (?:me )?(?:extra|more|too much)|costs? (?:me|anything|extra|more|money)|"
    r"how much (?:is the charge|does it cost|will (?:it|i) (?:cost|pay)|do i (?:pay|have to pay))|"
    r"why (?:was i|am i|have i been|did i get|did you|did it) charg\w*|"
    r"do (?:i|you|they) (?:get charged|charge)|(?:any|a|the) charge for|"
    r"charg(?:e|ed|es|ing) (?:me )?for|charg(?:e|ed|es) (?:me )?(?:[$£€]|[0-9])|"
    r"(?:is it|is this|are they|for) free|free of charge|"
    r"took (?:a cut|a fee|extra|more)|(?:charged|deducted) for this"
)

_UNKNOWN = (
    r"(?:do|did|does|can|could|am|i) not (?:even )?(?:recognis\w+|remember|know about|"
    r"authoris\w+|make|made|take out|initiate|use|approve|agree to)|"
    r"not (?:recognis\w+|mine|my transaction|authoris\w+|made by me|done by me)|"
    r"never (?:made|did|authoris\w+|bought|paid|used|took|withdrew|approved|ordered|signed up)|"
    r"was not me|was not mine|someone (?:else |has )?(?:used|withdrew|took out|bought|paid)|"
    r"unauthori[sz]\w*|unknown|unfamiliar|unrecognis\w*|fraudulent|suspicious|"
    r"(?:not|no idea) (?:sure )?(?:where|who) .{0,40}(?:from|was|is)|"
    r"no idea (?:what|why|where|who)|did not give (?:permission|consent)"
)

_MISSING = (
    r"(?:has|have|had|did|does|do|is|are|was|were|can|could|will) not (?:yet |still |even )?"
    r"(?:arriv\w*|receiv\w*|appear\w*|show\w*|reflect\w*|get|got|see|com[ei]\w*|"
    r"reach\w*|update\w*|chang\w*|credit\w*|added|land\w*|hit|post\w*|register\w*|there)|"
    r"no (?:sign of|record of|change|update|credit)|not (?:been )?(?:show\w*|receiv\w*|"
    r"there|credit\w*|reflect\w*|updat\w*|arriv\w*|applied|delivered|added|visible|in (?:my|the|their|his|her) account)|"
    r"yet to (?:see|receiv\w*|get|arriv\w*)|never (?:arrived|came|got|received|showed up|delivered)|"
    r"nothing (?:has |is )?(?:changed|showing|there|in my|appearing)|"
    r"missing|where (?:is|are) (?:my|the) (?:money|funds|cash|balance|transfer|deposit|refund)|"
    r"(?:balance|amount) (?:is |looks |stayed |remains )?(?:still )?(?:the same|unchanged|zero|0)|"
    r"(?:not|no) (?:yet )?in (?:the|my|his|her|their) (?:account|balance)|"
    r"(?:money|funds|balance|refund) (?:still )?(?:is not|are not) (?:back|there|in)|"
    r"not gone into|did not go into|credited nowhere|balance did not go up"
)

_WAIT = (
    r"pending|in progress|in process|processing|in transit|on hold|queued|"
    r"still (?:waiting|not completed|says pending|going through|being processed|not (?:through|complete))|"
    r"waiting (?:on|for)|(?:taking|taken) (?:so long|too long|forever|longer than)|"
    r"not (?:been )?(?:completed|cleared|processed|settled) yet|"
    r"has yet to (?:go through|clear|complete)|not yet (?:complete|process\w*|settl\w*)|"
    r"status of|stuck|unconfirmed|awaiting|delayed"
)

_TIMING = (
    r"how (?:much time|many (?:days|weeks|hours)|long|soon|fast|quickly)|"
    r"when (?:can|should|will|do|would|does|is|can i expect)|"
    r"(?:expected|estimate[ds]?|typical|usual|standard|delivery|processing|transit) "
    r"(?:date|time|times|duration|days|window|estimate)|"
    r"time (?:frame|scale|line)|turnaround|eta|"
    r"does it take|instant(?:ly)?|same day|business days|working days|within (?:a|one|two|three|\d+) (?:day|hour|week)"
)

_DECLINED = r"declin\w*|reject\w*|refus\w*|denied|not (?:been )?approved|disallow\w*|disapproved"
_FAILED = (
    r"fail\w*|unsuccessful|not successful|error|problem|issue|trouble|"
    r"not (?:working|work|went through|go through|going through|let(?:ting)? me|able to|accepting)|"
    r"unable to|will not (?:let|allow|work|go through|accept)|"
    r"went wrong|not possible|nothing happen\w*|not getting through|"
    r"did not (?:complete|process|happen)|keep\w* getting|no luck"
)
_REVERSED = (
    r"revert\w*|revers(?:al|ed|ing|e)|bounc(?:ed|e|ing)|"
    r"(?:returned|sent|transfer|credited|put|given|gone|went|came|got) (?:it |the money |the funds )?back|"
    r"back (?:in|into|to) (?:my |the )?(?:balance|account|card)|"
    r"refund(?:ed)? (?:itself|automatically|back)|no longer (?:on|in|showing)|"
    r"(?:payment|transaction) (?:was |has )?(?:disappear\w*|cancelled|canceled)"
)

_CURRENCY = (
    r"currenc(?:y|ies)|fiat|foreign money|fx|"
    r"usd|eur|gbp|chf|jpy|cad|aud|nzd|sek|nok|dkk|cny|rmb|inr|pln|czk|huf|ron|"
    r"zar|hkd|sgd|aed|sar|bgn|try lira|thb|rub|uah|brl|mxn|krw|ils|"
    r"euros?|dollars?|pounds?|sterling|rupees?|yuan|yen|zloty|dirhams?|francs?|baht|krona|lira"
)


def _classify(text):
    def h(*patterns):
        return any(_regex(pattern).search(text) for pattern in patterns)

    if text == "i have an outgoing transaction":
        return "pending_transfer"

    fee = h(_FEE)
    unknown = h(_UNKNOWN)
    missing = h(_MISSING)
    waiting = h(_WAIT)
    timing = h(_TIMING)
    declined = h(_DECLINED)
    failed = h(_FAILED)
    reversed_payment = h(_REVERSED)
    question_why = h(r"why|what (?:is|was) the (?:reason|point)|reason for|purpose of|what for|"
                     r"what do you need .{0,35} for|is it (?:really )?necessary")
    explicit_pending = h(r"pending|processing|in (?:progress|process)|queued|on hold|still being processed")
    completed = h(r"completed|successful(?:ly)?|marked as (?:sent|complete)|went through|"
                  r"(?:says|shows|shows as) (?:done|complete|successful|sent)|left my account|already sent")
    not_working = h(r"not (?:work\w*|function\w*|accept\w*|read\w*|usable|being accepted)|"
                    r"stop\w* working|does nothing|broken|faulty|damaged|blocked|frozen|disabled|"
                    r"invalid|cannot be used|can not use|unable to use|wonky|unusable")
    currency = h(_CURRENCY, r"[$£€¥]")
    fx = h(r"exchange|convert\w*|convers(?:ion|ions)|foreign exchange|fx|interbank|"
           r"currenc(?:y|ies) (?:swap|change|rate)|(?:sell|buy|swap) .{0,24}(?:currency|euros|usd|gbp|eur)")
    rate = h(r"rates?|converted at|exchange value|conversion value|parity")
    wrong_rate = h(r"wrong|incorrect|offered|different|worse|lower|higher|bad|terrible|poor|"
                   r"unfair|does not match|not (?:what|the same as|correct)|expected|"
                   r"(?:too|so) (?:much|little)|less than|more than|why (?:did|was|is|have|have i)|"
                   r"used (?:a|the) .{0,16} rate")
    card = h(r"cards?|plastic|mastercard|visa (?:debit|credit)|credit card|debit card")
    virtual = h(r"virtual|digital card|electronic card|e card|online only card|vcc")
    disposable = h(r"disposable|single use|one (?:time|use) (?:virtual |digital )?card|"
                   r"throwaway|temporary (?:virtual )?card|self destruct\w*")
    physical = h(r"physical|plastic|tangible|real card|actual card|hard copy|non virtual")
    wallet = h(r"(?:apple|google|android|samsung) (?:pay|wallet)|apple watch|applepay|googlepay|"
               r"(?:add|link|use|set up).{0,35}(?:wallet app|(?:my|an) iphone wallet)|"
               r"pay (?:with|using|by) (?:my |the )?(?:iphone|apple watch|android|smartwatch|phone)")
    direct = h(r"direct debit\w*|debit mandate|(?:unauthori\w+|unknown) standing order|"
               r"automatic debit|merchant debited|ach debit")
    beneficiary = h(r"beneficiar\w*|payees?|recipients?|destination account")
    deposit_cash = h(r"(?:cash|cheques?|banknotes?|notes and coins|paper money) (?:deposit\w*|top up|"
                     r"paid in|payment into)|deposit\w* .{0,36}(?:cash|cheques?|banknotes?|paper money)|"
                     r"(?:pay|paid|put|add|top up|load) .{0,32}(?:with|by|in|using) (?:a |my )?(?:cash|cheques?)|"
                     r"(?:paid|paying|pay|put) (?:in |a )?(?:cash|cheques?) (?:in|into)|"
                     r"(?:paid|pay|paying) (?:a |my )?cheque in|"
                     r"(?:cash|cheques?) (?:into|in to) .{0,24}account|"
                     r"deposit had (?:cash|a check)|deposit (?:a |my |the )?check|"
                     r"(?:by|with|using|cash|depositing) (?:a |my )?(?:paper |bank )?check|"
                     r"(?:cash|cheque) (?:at a branch|at the post office)|"
                     r"cash (?:and|or) (?:a |cheques?|checks?)")
    atm = h(r"atms?|cash (?:machines?|points?|dispensers?)|cashpoints?|bankomat|"
            r"(?:automated|automatic) teller(?: machine)?|hole in the wall")
    withdrawal = h(r"withdraw\w*|withdrew|withdrawn|withdrawing|"
                   r"(?:pull|get|take|took|take out|get out|took out|taking out|got|draw|drew) "
                   r"(?:some |my |the |any |out )?(?:cash|money) (?:out|from|at)|"
                   r"(?:get|take|get out|take out|taking out|took out) (?:some |my |the )?cash|cash out|cash advance")
    cash_out = (withdrawal or atm) and not deposit_cash
    topup = h(r"top up|reload\w*|recharge\w*|refill\w*|"
              r"(?:add\w*|load\w*|put|deposit\w*|fund\w*|credit\w*) "
              r"(?:more |some |any |my |the |extra )?(?:money|funds|cash|credit|balance) "
              r"(?:on|to|into|onto|in) (?:my |the |this |a )?(?:revolut|account|balance|card|wallet)|"
              r"(?:add|adding|added|load|loading|loaded) (?:some |more |my |the )?(?:money|funds)|"
              r"(?:fund|funding|funded|replenish|load|loading|reloading) (?:up )?(?:my |this |the )?(?:account|wallet|balance|card)|"
              r"add funds|add cash (?:to|into|in)|(?:deposit|deposited) (?:money|funds)|"
              r"(?:put|deposit|putting) money (?:in|into|on|onto)")
    bank = h(r"bank transfer|wire\w*|sepa|swift|bacs|chaps|faster payments|"
             r"bank to bank|(?:another|external|other|my) bank(?: account)?|"
             r"by bank|via bank|through (?:my |the )?bank|"
             r"(?:iban|sort code|routing number)|standing order|ach (?:transfer|credit)")
    inbound = h(r"incoming|inbound|receive money|receiving money|"
                r"(?:receive|receiv\w*|sent|pay|paid|transfer) .{0,30}(?:to me|into my|to my (?:account|balance|revolut|bank))|"
                r"(?:sent|transfer|paid|send|sending|pay|put) (?:me|into my account|to my account)|"
                r"(?:money|funds|transfer|payment) (?:to|for) me|"
                r"(?:to|into|in) my (?:revolut|account|bank account)|"
                r"(?:from|by) (?:my|a) (?:employer|friend|client|customer|relative)|"
                r"from another (?:bank|account)|"
                r"(?:my|the) (?:balance|account) (?:is |has |was |did )?(?:not |never |still )?"
                r"(?:update\w*|credit\w*|change\w*|the same|zero)")
    external_payer = h(r"someone (?:else |has )?(?:send|sent|pay|paid|transfer)|"
                       r"(?:friend|family|employer|company|customer|client|mother|dad|father|"
                       r"sister|brother|husband|wife|they|he|she) (?:has |have |can |could |wants? to )?"
                       r"(?:sent|send|pay|paid|transfer|deposit)|"
                       r"(?:get|receive|receiv\w*) (?:my )?(?:salary|wages|payroll|pension|"
                       r"money from someone|money from other people)|"
                       r"(?:from|by) (?:someone|a third party|other people|friends|my employer)")
    outbound = h(r"outgoing|outbound|to (?:a |my |the )?(?:friend|family|payee|beneficiary|recipient|"
                 r"someone|another person|someone else|other people)|"
                 r"to (?:my mother|my father|my sister|my brother|my wife|my husband)|"
                 r"(?:sent|send|transfer) .{0,40} (?:to him|to her|to them|to their account|to his account|to her account)|"
                 r"(?:he|she|they|recipient|payee|beneficiary) .{0,30}(?:received|got|see|arrived|there)|"
                 r"(?:leave|left|out of) my account|to (?:an |my |another |a )?(?:external|other|different) (?:bank|account)|"
                 r"send(?:ing)? money abroad|send (?:someone|my friend) money")
    transfer = h(r"transfer|remittance|wiring|wired|wire|bank payment|"
                 r"(?:send|sending|sent|move|moving|moved) .{0,31}(?:money|funds|to (?:a |my )?bank)|"
                 r"(?:inward|outward|outgoing|incoming|cross border) (?:payment|transaction)|"
                 r"sent .{0,20}(?:[$£€]\s*\d+|\d+ (?:to|euros|dollars|pounds))") or (
                     external_payer and h(r"sent|send|receiv\w*|pay|paid|deposit") and not h(r"merchant|seller|refund")
                 )
    payment = h(r"payments?|purchases?|transactions?|(?:i|was) paid|bought|buying|checkout|"
                r"paid (?:for|with|using|by|at|online)|pay (?:with|using|by|at|online|for (?:an?|the|my))|"
                r"bill|merchant|store|shop|retailer|restaurant|point of sale")
    card_funding = h(r"(?:by|with|using|from|via|on|through) (?:an? |my |the |another |someone else's )?(?:"
                     r"credit |debit |bank |prepaid |other )?(?:cards?|mastercard|visa|amex|american express)|"
                     r"card (?:top up|deposit)|(?:debit|credit|prepaid|bank) card|"
                     r"top up .{0,24}(?:cards?|mastercard|visa|amex|american express)")
    proof_funds = h(r"source of (?:my |your |the )?(?:funds|money|income|wealth)|"
                    r"proof of (?:my |your |the )?(?:income|salary|funds|wealth|earnings)|"
                    r"where .{0,40}(?:money|funds|income) (?:come|came|comes) from|"
                    r"how i (?:earned|make|made) (?:my |the )?money|"
                    r"(?:verify|verification|prove|validate|explain|document) .{0,36}"
                    r"(?:source|salary|income|earnings|funds)|payslips?|pay slips|"
                    r"evidence of (?:income|funds)|source of deposit")
    proof_id = h(r"identity|my id|your id|photo id|national id|id (?:card|document|verification|check)|"
                 r"passport|selfie|identification|residency permit|driver'?s? licen[cs]e|kyc|"
                 r"(?:verify|confirm|prove|check) (?:who i am|myself|my age)|"
                 r"(?:identity|proof of) (?:address|residency)|proof of (?:address|residence)|"
                 r"verify (?:my |an |the )?(?:account|profile)|account verification|"
                 r"verification (?:of my account|of my profile)")
    verify = h(r"verif\w*|validat\w*|authenticat\w*|confirm\w*|prove|proof|"
               r"submit|upload|scan|documents?|evidence")
    phone_lost = h(r"(?:lost|stolen|misplac\w*|missing|snatched|can not find) .{0,28}"
                   r"(?:phone|iphone|smartphone|mobile|handset|device)|"
                   r"(?:phone|iphone|smartphone|mobile|handset|device) .{0,28}"
                   r"(?:stolen|lost|missing|went missing|snatched)|"
                   r"someone stole .{0,28}(?:phone|iphone|mobile)|no longer have (?:my |that |the )?(?:phone|device)")
    card_lost = h(r"(?:lost|stolen|misplac\w*|missing|can not find|can not locate) "
                  r".{0,28}(?:cards?|wallet|purse)|"
                  r"(?:cards?|wallet|purse) .{0,22}(?:stolen|lost|gone missing|missing)|"
                  r"(?:someone|they) stole .{0,30}(?:cards?|wallet|purse)|left my card (?:in|at|on)")
    swallowed = h(r"swallow\w*|ate my card|eaten my card|gobbled|retained my card|"
                  r"(?:took|kept|held|captured|retained|trapped|confiscated|snatched) (?:my |the )?card|"
                  r"card (?:is |was |got |has been |has got )?(?:stuck|eaten|retained|trapped|swallowed|kept)|"
                  r"(?:did|will) not (?:give|return|spit|eject) .{0,22}(?:card|back)|card .{0,20}will not come out")
    if swallowed and (card or atm):
        return "card_swallowed"
    if phone_lost:
        return "lost_or_stolen_phone"
    if card_lost and not h(r"card (?:details|number|information|data) .{0,20}(?:stolen|leak)"):
        return "lost_or_stolen_card"

    if h(r"(?:close|closing|delete|deleting|terminate|termination|cancel|cancelling|canceling|"
         r"shut down|deactivate|remove|get rid of) (?:down |out |my |the |this |a |my revolut ){0,3}account|"
         r"account (?:closure|termination|deletion)|no longer (?:want|need) (?:my |this |the )?account|"
         r"stop using (?:revolut|your service)|end my membership|leave revolut|"
         r"(?:opt|sign) out (?:of|from) (?:revolut|the service)|(?:unsubscribe|unregister) from revolut"):
        return "terminate_account"

    pin = h(r"pin|pins|pin number|personal identification number")
    login = h(r"passcode|password|login code|log in code|security code for the app|unlock code|"
              r"sign in code|app access code|(?:4|four) digit (?:app |login )?passcode")
    if login and not topup and not h(r"cvv|cvc|3d secure|merchant|card security code"):
        return "passcode_forgotten"
    if pin and h(r"(?:wrong|incorrect|bad|invalid|wrongly) (?:card )?pin|"
                 r"pin .{0,26}(?:blocked|locked|frozen|disabled|incorrect|too many|failed)|"
                 r"too many (?:wrong |incorrect |failed )?(?:pin|attempts|tries)|"
                 r"(?:unblock|unlock|blocked|locked) .{0,23}(?:pin|pin tries)|"
                 r"(?:3|three|several|multiple) (?:times|attempts|tries)|"
                 r"(?:entered|typed|put in) .{0,14}pin (?:incorrectly|wrong)|exceeded .{0,19}(?:tries|attempts)"):
        if not (h(r"change|reset|new pin") and h(r"forgot\w*|do not remember") and
                not h(r"locked|blocked|times|attempts|tries")):
            return "pin_blocked"
    if pin and (h(r"change|reset|set|update|choose|create|new|forgot\w*|remember|recover|retrieve|"
                  r"find|view|see|know|where|what is|different|custom") or not (payment or cash_out)):
        return "change_pin"

    if proof_funds:
        return "verify_source_of_funds"
    if h(r"(?:minimum|maximum|required|legal) age|age (?:limit|restriction|requirement)|"
         r"how old|old enough|years old|year old|under ?18|younger than|minor(?:s)?|"
         r"(?:i am|i m|my son is|my daughter is|my child is) (?:only )?(?:1[0-9]|[6-9])|"
         r"(?:children|teens?|teenagers?|kids?) .{0,25}(?:account|sign up|card|use revolut)|"
         r"(?:open|create|set up|get) .{0,25}(?:account|card) for my (?:child|kid|son|daughter)"):
        return "age_limit"
    if topup and (verify or h(r"(?:verification|confirmation|4 digit|four digit|security) code")):
        if not (proof_id and not h(r"top up .{0,50}(?:verif|confirm|validat)|"
                                   r"(?:verify|confirm|validate) .{0,35}(?:card|top up)")):
            return "verify_top_up"
    if h(r"(?:4|four) digit (?:verification |confirmation )?code .{0,50}(?:statement|transaction|charge)|"
         r"verification code .{0,28}(?:deposit|statement|bank card)|"
         r"(?:verify|verifying|verification of|confirm) (?:my |a |the )?(?:top up|funding card|"
         r"(?:debit |credit |bank )?card (?:i used|used to|for adding money|for top up))"):
        return "verify_top_up"
    if proof_id or h(r"verif\w* me|(?:identity|account) verification|(?:proof|verify) of who i am"):
        if failed or declined or not_working or h(r"not (?:verified|verifying|accepted|being approved|able to verify)|"
                                                  r"verification .{0,35}(?:pending|stuck|taking|rejected)|"
                                                  r"(?:will|would|does) not (?:scan|upload|verify|accept)|"
                                                  r"having (?:problems|difficulty)|blurry|"
                                                  r"(?:lost|do not have|no) (?:my |a )?(?:photo id|passport|id)"):
            if not (question_why and h(r"need (?:my|to)|have to|require|necessary|asking for")
                    and not h(r"rejected|declined|failed|not accept\w*|can not|not able")):
                return "unable_to_verify_identity"
        if question_why or h(r"do i (?:really )?(?:have to|need to) (?:verify|provide|upload|prove|show)|"
                             r"what happens if i do not verify|why .{0,35}(?:personal documents|passport|selfie)"):
            return "why_verify_identity"
        return "verify_my_identity"

    if h(r"(?:change|update|edit|correct|switch|modify|replace|amend|alter|new|wrong|different) "
         r".{0,41}(?:phone number|mobile number|e ?mail(?: address)?|(?:home|billing|residential|mailing) address|"
         r"date of birth|personal (?:details|information|data)|name on|surname|family name|full name|"
         r"first name|last name|username|my name|my address|profile details|contact details)|"
         r"(?:phone number|mobile number|email|e mail|address|personal details|my name|surname|"
         r"last name|date of birth|profile) .{0,23}(?:changed|change it|update|incorrect|wrong|"
         r"need changing|different|out of date|mistake)|moved (?:to a new|house|home)|"
         r"(?:i |got )married .{0,43}(?:change|name)|edit (?:my |the )?profile"):
        return "edit_personal_details"

    if h(r"compromis\w*|skimmed|cloned|card cloning|hacked|phish\w*|identity theft|"
         r"(?:card (?:details|number|data|information)|cvv) .{0,32}(?:stolen|leak\w*|exposed|"
         r"known|got out|shared|got into)|someone .{0,26}(?:has|knows|got|copied) "
         r".{0,24}(?:my card|card details|card number)|fraud protection|freeze my card|block my card") and (
             not unknown or not (payment or cash_out or direct) or
             h(r"compromis\w*|card details|cloned|skimmed|hacked|phish\w*")):
        return "compromised_card"

    refund = h(r"refund\w*|chargeback|charge back|reimburs\w*|money back|get back my money|"
               r"(?:get|want|give|return|pay) .{0,18}(?:my|the) money back")
    if refund:
        refund_expected = h(r"(?:merchant|seller|store|shop|retailer|company|they) .{0,41}"
                            r"(?:refund\w*|returned the money|sent .{0,13} back)|"
                            r"(?:refund|reimbursement) (?:was |has been |already |is )?"
                            r"(?:sent|issued|processed|promised|pending|made|approved|confirmed)|"
                            r"(?:issued|processed|promised|approved|initiated) (?:me |a |my |the )?refund|"
                            r"(?:where is|waiting for|still waiting on|expecting|supposed to get|"
                            r"due to receive|never got|did not get) (?:a |my |the )?refund|"
                            r"refund(?:ed)? .{0,35}(?:days? ago|weeks? ago|yesterday)|"
                            r"(?:take|long|until|before) .{0,30}refund .{0,22}(?:appear|show|credited|arrive|reach)")
        if not (topup and reversed_payment and not refund_expected):
            if refund_expected or missing or explicit_pending:
                if not (h(r"(?:refused|refuse|denied|will not|does not|did not|not willing to) "
                          r".{0,15}(?:refund|reimburse)|can (?:i|you) get (?:a |my )?refund") and
                        not (missing and refund_expected)):
                    return "refund_not_showing_up"
            if not (reversed_payment and not h(r"want|ask|request|how|can i|can you|need|should|would like")):
                return "request_refund"

    if direct and (unknown or h(r"why .{0,25}(?:taken|deducted|debit\w*|charge\w*)|"
                               r"unexpected|disput\w*|without (?:my )?(?:permission|consent)|"
                               r"what is (?:this|the) direct debit")):
        return "direct_debit_payment_not_recognised"
    if cash_out and unknown:
        return "cash_withdrawal_not_recognised"

    if h(r"twice|double (?:charge\w*|debit\w*|payment|transaction)|"
         r"charged double|duplicat\w*|two identical|charged (?:two|three|\d+) times|"
         r"same .{0,22}(?:charged again|two times|twice)|"
         r"(?:two|2) (?:payments|charges|withdrawals|transactions|debits) "
         r"(?:for (?:the )?same|instead of one)|(?:billed|debited|charged|paid) "
         r".{0,24}(?:more than once|a second time|2x)|"
         r"charged both .{0,36}(?:cash|card)") and (
             payment or card or fee or cash_out or h(r"charged|debited|billed|taken out|money was taken|paid")):
        return "transaction_charged_twice"

    small_check_charge = h(r"pre ?auth\w*|temp(?:orary)? (?:hold|charge)|"
                           r"(?:small|test|verification|random|strange|odd|extra|additional|unexpected) "
                           r"(?:little )?(?:fee |card )?(?:charge|hold|amount|transaction)|"
                           r"(?:one|1) (?:pound|dollar|euro) charge|[$£€]\s*1(?: 00)? (?:charge|transaction|fee)|"
                           r"charge .{0,15}(?:on (?:my|the) statement|on my bill)|"
                           r"(?:statement|bill) .{0,25}(?:extra|additional|unexpected|small|strange)")
    if unknown and (payment or h(r"charg\w*|debit\w*|activity|taken out|deducted")) and not (
            transfer and h(r"bank transfer|wire|beneficiary|recipient")):
        if direct:
            return "direct_debit_payment_not_recognised"
        if small_check_charge and not h(r"not (?:authoris\w*|make|made|mine)|"
                                        r"someone (?:else|used|bought)|fraud|stolen|did not buy"):
            return "extra_charge_on_statement"
        return "card_payment_not_recognised"

    if wallet and not (topup and not card and not h(r"add .{0,20}card|link")):
        return "apple_pay_or_google_pay"

    if h(r"contactless|tap to pay|(?:tap|tapping|wave|waving) (?:my |the )?card|"
         r"(?:tap|tapping) (?:not|does|did|will) not|nfc|paywave|paypass|"
         r"contact free|touch to pay|touchless") and not (explicit_pending or (fee and not (failed or not_working))):
        return "contactless_not_working"

    if h(r"(?:card|cards) .{0,32}(?:expir\w*|expiration|expiry|valid until|validity ran out)|"
         r"(?:expir\w*|expiration|expiry|out of date) .{0,23}(?:my |the )?cards?|"
         r"(?:renew|renewal) (?:my |the )?card|getting a replacement .{0,22}expir") and not (
             topup and h(r"(?:my|a) (?:external|credit|bank) card")):
        return "card_about_to_expire"

    shipping = h(r"deliver\w*|shipp\w*|postage|courier|dispatch\w*|"
                 r"arriv\w*|in (?:the )?(?:post|mail)|(?:send|sent|receive|received|get) .{0,22}"
                 r"(?:my |the |a )?card (?:to|in|by|yet)|tracking|track .{0,25}card|"
                 r"where (?:is|has|did) my .{0,13}card")
    ordered = h(r"(?:i |already |just |have |recently |previously )ordered|"
                r"(?:i |already |just |have )requested|"
                r"ordered .{0,25}(?:ago|last week|on monday|last month|yesterday)|"
                r"placed (?:my |an |the )?order|(?:my|the) card order|since ordering")
    not_delivered = h(r"(?:no|without a) card yet|card .{0,22}(?:not|never|still|missing)|"
                      r"not (?:received|got|gotten|seen|delivered) .{0,26}(?:card|plastic)|"
                      r"still waiting .{0,28}(?:card|plastic)|where (?:is|has|did) .{0,21}(?:card|plastic)|"
                      r"card .{0,20}(?:late|lost in the mail|lost in transit)|"
                      r"wait\w* .{0,35}(?:ages|weeks|days|so long)|track (?:my |the )?card")
    if (card or physical) and not (virtual or cash_out or topup) and (
            not_delivered or (shipping and (timing or missing or waiting or ordered)) or
            (ordered and (missing or waiting)) or
            (timing and h(r"(?:get|receive|take|obtain) .{0,20}(?:my|the|a|physical) .{0,16}card"))):
        if not_delivered or (missing and not h(r"when (?:ordering|i order)|if i order")) or (
                ordered and waiting and not h(r"how long (?:does|will|should) .* take")):
            return "card_arrival"
        if timing:
            return "card_delivery_estimate"
        if ordered or waiting:
            return "card_arrival"
        return "card_delivery_estimate"

    if card and h(r"activat\w*|enable (?:my |the |this )?(?:new |physical )?card|"
                  r"card .{0,20}(?:not active|inactive|activation)|"
                  r"start using (?:my |the )?(?:new |physical )?card|"
                  r"make (?:my |the )?(?:new )?card active") and not (
            h(r"deactivat\w*|contactless|(?:re|un)freeze") and not h(r"activation|activate")):
        return "activate_my_card"

    network = h(r"mastercard|visa|amex|american express|maestro|discover|diners club|union ?pay")
    if network and not topup and h(r"visa (?:or|and|versus|vs) mastercard|mastercard (?:or|and|versus|vs) visa|"
                                   r"which (?:network|brand)|card network|"
                                   r"(?:is|will|are) (?:it|this|my|the|your|a) .{0,30}(?:visa|mastercard)|"
                                   r"(?:get|issue|receive|offer|provide|send|do you have) .{0,23}(?:a |your |any )?"
                                   r"(?:visa|mastercard) (?:credit |debit )?card|"
                                   r"can i (?:choose|pick|select|switch) .{0,30}(?:visa|mastercard)"):
        if not h(r"(?:link|add|register|attach|already have) .{0,25}(?:my|a) .{0,13}(?:visa|mastercard)|"
                 r"top up|accept (?:my |a )?(?:visa|mastercard)|payment declined"):
            return "visa_or_mastercard"

    if h(r"(?:link|pair|connect|attach|register|associate|bind|add) .{0,35}"
         r"(?:my |a |the |new |another |existing )?(?:physical |bank |revolut |debit |credit )?cards? "
         r".{0,19}(?:account|app|profile|paypal|revolut)|"
         r"(?:link|pair|connect|attach|register|associate|bind) .{0,29}(?:my |the |a )?cards?|"
         r"card (?:linking|linkage|linked|pairing)|card .{0,24}linked to") and not (
             topup and not h(r"my new card|physical card|revolut card|link my accounts")):
        return "card_linking"

    limits = h(r"limits?|limitations?|maximum|minimum|at most|at least|smallest amount|largest amount|"
               r"how many|how much can i|how much am i allowed|"
               r"how (?:often|frequently)|cap on|capped|unlimited|"
               r"(?:daily|monthly|weekly|annual) (?:restrict\w*|threshold|amount)")
    if disposable and limits:
        return "disposable_card_limits"
    if virtual or disposable:
        if not_working or declined or failed or h(r"card does not exist|invalid card number|disappeared"):
            if not (topup and not h(r"my (?:virtual|disposable) card .{0,24}(?:work|valid|accept)")):
                return "virtual_card_not_working"
        if disposable and not (fee and payment) and not explicit_pending:
            return "get_disposable_virtual_card"
        if h(r"get|create|generate|make|setup|set up|order|apply|issue|offer|find|obtain|"
             r"what (?:is|are)|where|sign up|need|want|add|access|use|available") and not (
                 payment and (fee or reversed_payment or explicit_pending)):
            return "getting_virtual_card"

    if card and h(r"spare|back ?up|second (?:physical |revolut )?card|extra (?:physical |revolut )?card|"
                  r"additional (?:physical |revolut )?card|"
                  r"(?:have|order|get|obtain|need|want|use) (?:an? )?(?:other|another|multiple|two|2|more than one) "
                  r"(?:physical |revolut )?cards?|"
                  r"(?:two|2|multiple|several|more than one) (?:physical |revolut )?cards?|"
                  r"how many (?:physical |revolut )?cards") and not (
            h(r"lost|stolen|expir|forgot|replace|replacement")):
        return "getting_spare_card"

    registration = h(r"(?:open|create|set up|start|have|register for|get|eligible for|apply for) "
                     r".{0,22}(?:account|revolut account)|"
                     r"sign (?:me )?up|registrat\w*|register|become (?:a|your) (?:customer|member)|"
                     r"do you operate|(?:revolut|service|your app) .{0,22}available")
    geography = h(r"countr(?:y|ies)|region|resid\w*|citizen\w*|nationalit\w*|"
                  r"(?:live|living|located|based|resident|reside|from) (?:in |the )?|"
                  r"uk|usa|united states|america|canada|australia|europe|"
                  r"japan|china|india|germany|france|spain|mexico|switzerland|singapore|"
                  r"south africa|ireland|poland|brazil|denmark|sweden|turkey|portugal|"
                  r"netherlands|norway|romania|hungary|italy|new zealand|malaysia|thailand|"
                  r"philippines|argentina|colombia|russia|ukraine|uae|hong kong|"
                  r"pakistan|indonesia|greece|czech|israel|belgium|austria|finland|"
                  r"abroad|overseas|worldwide|internationally|outside (?:of |the )?")
    if (registration and geography and not (currency and not h(r"live|resid\w*|country|based|citizen"))) or (
        h(r"(?:what|which|supported|eligible|accepted|available) .{0,28}(?:countr(?:y|ies)|nationalities)|"
          r"(?:my|this|which) country .{0,29}(?:supported|available)|"
          r"(?:revolut|your service|your app) .{0,24}(?:work|available|supported|used|use) (?:in|from)|"
          r"(?:available|launch\w*|expand\w*) (?:in|to) my country|"
          r"(?:live|am from|am based) in .{0,28}(?:can i (?:join|use revolut|sign up)|eligible)") and
        not (payment or card or transfer or topup or cash_out)
    ):
        return "country_support"

    cancelled = h(r"cancel\w*|call off|stop|recall|undo|take back|rescind|pull back|"
                  r"reverse (?:a|my|the|this)|sent .{0,24}by (?:mistake|accident)|"
                  r"accidentally (?:sent|transfer)|wrong (?:person|account|beneficiary|recipient)|"
                  r"do not want (?:it|this|the transfer) to go through")
    if (transfer or beneficiary) and cancelled and not (
            h(r"cancelled|canceled|cancellation") and not h(r"how|can i|can you|want|need|could|"
                                                           r"please|possible|would like|try to")):
        return "cancel_transfer"
    if beneficiary and h(r"not allowed|not supported|not available|not eligible|restricted|invalid|"
                         r"permission|blacklist\w*|block\w*|not (?:let|allow|able)|"
                         r"add .{0,25}(?:error|failed)|can not|cannot|unable|rejected|denied|"
                         r"why .{0,29}(?:payee|beneficiary|recipient)|beneficiary not allowed"):
        if not (missing and not (failed or declined) and h(r"received|arrived|show\w*|got")):
            return "beneficiary_not_allowed"

    actual_payment = h(r"i (?:have )?(?:paid|bought|made|used|tried)|was (?:charged|billed|debited)|"
                       r"(?:my|this|the) (?:card )?(?:payment|purchase|transaction)|"
                       r"paid .{0,26}(?:abroad|using|online|in|at)|"
                       r"paying with (?:it|my card)|on my statement|"
                       r"charged .{0,28}(?:euros|pounds|dollars|usd|eur|gbp)")
    fx_dispute = (fx or rate or (
        currency and h(r"converted|different currenc\w*|wrong currenc\w*|exchange|"
                       r"(?:charged|taken|deducted) .{0,45} (?:instead of|more than|but)"))) and wrong_rate
    if cash_out:
        atm_cash_problem = h(r"(?:did|does|has|have|would) not (?:actually )?"
                             r"(?:dispense|give(?: me)?|get|got|receiv\w*|issue|release|spit out|deliver) "
                             r".{0,27}(?:cash|money|anything|full amount|notes|banknotes|requested amount)|"
                             r"(?:no|zero|not any|not enough|less|too little) (?:cash|money|notes) "
                             r"(?:was|came|out|received|dispens\w*)|"
                             r"(?:no|zero) cash|nothing (?:came|was dispensed)|empty (?:atm|cash machine)|"
                             r"wrong (?:amount|sum|number of notes)|incorrect amount|"
                             r"(?:dispensed|gave (?:me )?|got|received|came out) .{0,32}"
                             r"(?:less|too little|not enough|only|wrong|different)|"
                             r"less (?:cash|money)|short changed|shortchanged|"
                             r"(?:amount|cash|money) .{0,29}(?:did not come out|was not dispensed|"
                             r"not (?:correct|right|the right|the correct)|missing from)|"
                             r"charged (?:me )?(?:but|even though) .{0,38}(?:no cash|nothing|did not get|"
                             r"did not receive|did not dispense)|only .{0,28}(?:came out|was dispensed)")
        if atm_cash_problem and not ((failed or declined) and not h(r"charged|debited|deducted|"
                                                                    r"took|dispens\w*|amount|balance")):
            return "wrong_amount_of_cash_received"
        if fx_dispute and not h(r"atm fee|withdrawal fee|separate fee|cash withdrawal charge"):
            return "wrong_exchange_rate_for_cash_withdrawal"
        if fee:
            return "cash_withdrawal_charge"
        if explicit_pending or (waiting and withdrawal and not (declined or failed)):
            return "pending_cash_withdrawal"
        if declined or failed or not_working or h(r"reverted|blocked|unsuccessful|not allowed|"
                                                   r"rejected|no longer (?:get|take out)"):
            return "declined_cash_withdrawal"
        if missing and (completed or h(r"charged|debited|deducted|account|balance")):
            if h(r"money|cash|notes") and not h(r"not (?:show|appear|reflect|updated)"):
                return "wrong_amount_of_cash_received"
            return "pending_cash_withdrawal"
        if (fx or rate) and not h(r"which atms|where|what atms|can i use"):
            return "exchange_rate"
        if limits:
            return "cash_withdrawal_charge"
        return "atm_support"

    if deposit_cash:
        if missing or explicit_pending or h(r"(?:i |already |just |have )deposited|"
                                             r"(?:i |already |just |have )paid in|"
                                             r"cash went in|cheque (?:cleared|has cleared|deposited)|"
                                             r"waiting for .{0,25}(?:deposit|cheque)"):
            if missing or waiting or timing:
                return "balance_not_updated_after_cheque_or_cash_deposit"
        return "top_up_by_cash_or_cheque"

    card_transaction = (payment and not (transfer or topup or direct)) or (
        card and h(r"purchase|merchant|paid|checkout|paying|payment|dining|bill|pos") and
        not (topup or direct or h(r"(?:bank|wire) transfer|beneficiary"))
    )
    if card_transaction and fx_dispute and actual_payment and not h(r"(?:card|payment|transaction) fee|"
                                                                    r"separate (?:charge|fee)"):
        return "card_payment_wrong_exchange_rate"

    card_query = h(r"what (?:kind|type|kinds|types|sort|cards|currenc\w*)|"
                   r"which (?:cards|currenc\w*|bank cards|card types|payment methods)|"
                   r"support\w*|accept\w*|(?:can|may|could) i (?:use|add .{0,18}using|top up (?:by|with|from|using|via))|"
                   r"(?:any|other|foreign|international) (?:credit |debit )?cards|"
                   r"prepaid|amex|american express|maestro|union ?pay|visa|mastercard")
    automatic = h(r"auto ?(?:matic(?:ally)? )?top up|auto ?(?:reload|recharge|refill)|"
                  r"automat\w*|(?:schedule|scheduled|recurring) .{0,25}(?:top up|add|deposit)|"
                  r"(?:whenever|when|once|if) .{0,26}(?:balance|money|funds) "
                  r".{0,20}(?:low|below|under|fall|drops)|"
                  r"top up .{0,40}(?:threshold|when (?:it|i) (?:drops|run)|every (?:week|month|day))")
    if topup or h(r"automatic (?:funding|reload|recharge)") or (
        automatic and h(r"balance .{0,22}(?:low|below|under|fall|drops)|auto top up|auto reload")
    ):
        if automatic:
            return "automatic_top_up"
        if limits:
            return "top_up_limits"
        if fee:
            if bank and not h(r"(?:with|using|by|via) (?:a |my |the )?(?:credit|debit|bank) card"):
                return "top_up_by_bank_transfer_charge"
            if small_check_charge and not h(r"(?:fee|surcharge) .{0,26}(?:top up|load)|"
                                             r"why .{0,30}charged (?:me )?for (?:my |the )?top up"):
                return "extra_charge_on_statement"
            return "top_up_by_card_charge"
        if reversed_payment or h(r"refund(?:ed)? (?:my |the )?top up|top up .{0,27}refund"):
            return "top_up_reverted"
        if explicit_pending and not (declined or h(r"failed|unsuccessful")):
            if bank and missing and not card_funding:
                return "balance_not_updated_after_bank_transfer"
            return "pending_top_up"
        if declined or failed:
            if missing and not h(r"declined|reject\w*|failed|error|not (?:working|let\w*|go through)") and (
                completed or h(r"charged|deducted|already")
            ):
                if bank and not card_funding:
                    return "balance_not_updated_after_bank_transfer"
                return "pending_top_up"
            return "top_up_failed"
        if bank and not card_funding:
            if missing or (waiting and not timing):
                return "balance_not_updated_after_bank_transfer"
            if timing and (transfer or h(r"bank deposit")):
                return "transfer_timing"
            return "transfer_into_account"
        if missing or waiting or timing and h(r"top up .{0,18}(?:arrive|clear|show|appear|take)|"
                                               r"until .{0,18}(?:balance|credited)"):
            return "pending_top_up"
        if (card_query and (card or currency or network)) or h(r"what .{0,14}currenc\w*|"
                                                                r"from (?:an? |my )?(?:international|foreign) card"):
            return "supported_cards_and_currencies"
        return "topping_up_by_card"

    if transfer or (beneficiary and not card) or (bank and (inbound or fee or missing)):
        transfer_done = completed or h(r"(?:i|we|they|he|she|someone|my friend|my employer) "
                                        r"(?:have |has |already |just )?(?:sent|transfer|paid|wired|made)|"
                                        r"transfer .{0,20}(?:yesterday|ago|last week|earlier|this morning)|"
                                        r"(?:made|sent|initiated|did) (?:a |my |the )?(?:bank )?transfer")
        recipient_missing = h(r"(?:has|have|did|can) not .{0,25}(?:receiv\w*|see|get|got)|"
                              r"(?:has not|did not|never) (?:arriv\w*|reach\w*|com\w*)|"
                              r"not (?:been )?(?:received|arrived|reached|credited)|"
                              r"not (?:show\w*|appear\w*|in (?:his|her|their))|"
                              r"still (?:waiting|not there|nothing)|where is .{0,22}money|no sign")
        if fee:
            if h(r"(?:top up|funding|to (?:add|deposit|load) (?:money|funds))") and not outbound:
                return "top_up_by_bank_transfer_charge"
            return "transfer_fee_charged"
        if declined:
            return "declined_transfer"
        if h(r"\b(?:failed|unsuccessful|failure|error)\b") or (
                failed and not (missing or explicit_pending or (transfer_done and waiting))):
            return "failed_transfer"
        if reversed_payment:
            return "failed_transfer"
        if explicit_pending and not completed:
            if inbound and not outbound and missing and bank and h(r"(?:balance|account) .{0,18}"
                                                                     r"(?:not|unchanged|same)"):
                return "balance_not_updated_after_bank_transfer"
            return "pending_transfer"
        if (missing or recipient_missing or (waiting and completed)) and (outbound or (
                completed and not inbound and h(r"received|arriv\w*|reach\w*|recipient|another account"))):
            return "transfer_not_received_by_recipient"
        if (missing or (waiting and not timing)) and inbound:
            return "balance_not_updated_after_bank_transfer"
        if missing and h(r"(?:my |revolut )?balance|credited|deposit|incoming") and not outbound:
            return "balance_not_updated_after_bank_transfer"
        if timing:
            return "transfer_timing"
        if missing or waiting:
            if completed and not inbound:
                return "transfer_not_received_by_recipient"
            return "pending_transfer"
        if external_payer or h(r"pay (?:me|my salary)|send (?:me|money to me)|"
                               r"receive (?:a |any |international )?(?:transfer|payment|money|funds)|"
                               r"receiving (?:from|money|funds|transfer|payments)|"
                               r"(?:give|share|provide) .{0,28}(?:details|iban|number)"):
            return "receiving_money"
        if inbound or h(r"add money|how (?:to|can i|do i)|how does|fund|deposit|"
                        r"make (?:a|an) (?:bank )?transfer|can i (?:transfer|send|wire)"):
            if outbound and not inbound:
                return "pending_transfer"
            return "transfer_into_account"
        return "pending_transfer"

    if fx or rate and (currency or h(r"interbank|foreign")):
        if fee:
            return "exchange_charge"
        if rate or h(r"how many|how much .{0,25}(?:get|for|worth)|worth|value of|"
                     r"difference between|rate compared|best time|fluctuat\w*|today'?s|"
                     r"how is .{0,22}(?:calculat\w*|determin\w*|set)|interbank|"
                     r"what .{0,16}(?:rate|converted at)"):
            return "exchange_rate"
        if h(r"(?:what|which|available|supported) .{0,27}currenc\w*|"
             r"currenc\w* .{0,25}(?:support\w*|available|can i|can be|are allowed)|"
             r"support\w* .{0,24}(?:exchange|hold|currenc\w*)|"
             r"(?:hold|store|keep|maintain|open) .{0,27}(?:currenc\w*|balance|account)|"
             r"fiat|all currenc\w*|any currenc\w*"):
            return "fiat_currency_support"
        if currency or h(r"app|how|can i|where|change my|exchange money|convert money|"
                         r"convert funds|currency exchange"):
            return "exchange_via_app"
        return "exchange_rate"

    if card_transaction or payment or (card and (declined or explicit_pending or reversed_payment or fee)):
        if small_check_charge and not h(r"(?:payment|card|transaction) fees?|"
                                        r"(?:fee|surcharge) (?:for|on|when) (?:pay\w*|using|making a payment)"):
            return "extra_charge_on_statement"
        if declined:
            return "declined_card_payment"
        if reversed_payment or h(r"(?:card )?payment .{0,24}(?:cancelled|canceled|disappeared)|"
                                 r"(?:merchant|store) .{0,26}cancel\w* .{0,13}(?:charge|payment)"):
            return "reverted_card_payment"
        if explicit_pending or (waiting and not (declined or failed)) or (
                missing and h(r"not (?:appear\w*|show\w*)|not yet|not received")):
            return "pending_card_payment"
        if fee:
            return "card_payment_fee_charged" if card or actual_payment else "extra_charge_on_statement"
        if cancelled:
            return "request_refund"
        acceptance_question = h(r"accept\w*|can i (?:use|pay|buy|shop)|where (?:can|can not|is|are)|"
                                r"anywhere|everywhere|places|abroad|overseas|international\w*|"
                                r"work in|work at|use .{0,19}(?:online|in stores)|"
                                r"can (?:it|my card) be used")
        if failed or not_working:
            if card and h(r"(?:card|it) (?:has |had )?(?:stopped working|does not work anywhere|"
                          r"does not work at all|is not working at all|never works|is broken|is damaged)|"
                          r"everywhere|anywhere|all (?:stores|transactions|payments)|"
                          r"(?:chip|magnetic strip|magstripe) .{0,19}(?:not work\w*|damage|broken)"):
                return "card_not_working"
            return "declined_card_payment"
        if acceptance_question:
            return "card_acceptance"

    if card and not virtual and h(r"(?:order|ordering|apply for|request|send me|ship me|mail me|"
                                     r"post me|deliver me|buy|purchase|replace|replacement) .{0,28}"
                                     r"(?:cards?|plastic)|"
                                     r"card (?:order|application)|(?:order|ordering) (?:one|it)|"
                                     r"need .{0,12}new card") and not h(r"not working|broken|damaged|blocked"):
        return "order_physical_card"
    if card and (not_working or failed or h(r"will not swipe|card does not read|"
                                            r"chip|magnetic strip|magstripe|frozen|"
                                            r"cannot use my card|can not use my card")):
        if h(r"where (?:can|is)|do you accept|can i use my card (?:in|at|abroad)") and not (
                h(r"not work\w*|damage\w*|problem|tried|blocked")):
            return "card_acceptance"
        return "card_not_working"
    if card and h(r"accept\w*|(?:use|work) (?:it )?(?:in|at|abroad|overseas|online|"
                  r"internationally|everywhere|anywhere|worldwide)|"
                  r"where can i (?:use|pay)|(?:(?:pay|spend) abroad)|"
                  r"can (?:i use|it be used|my card be used)|using .{0,18}card (?:in|at|on)|"
                  r"can i travel|international use|can i take my card"):
        return "card_acceptance"
    if (card or physical) and h(r"physical|plastic|have|need|want|get|"
                                r"get one|obtain|how can i|how do i|sign up for|available|"
                                r"do (?:i|you)|receive|send|pricing|free|cost"):
        return "get_physical_card"
    if (external_payer or inbound or bank or h(r"account details|bank details|iban|sort code|routing number")) and not (
        currency and h(r"hold|store|currenc\w* balance|multi currency")
    ):
        if missing or explicit_pending and inbound:
            return "balance_not_updated_after_bank_transfer"
        if external_payer or not h(r"(?:add|deposit|put|transfer) (?:money|funds)"):
            return "receiving_money"
        return "transfer_into_account"
    if currency or h(r"foreign denominations|local denomination|multiple balances"):
        if h(r"(?:with|using|what|which|supported) .{0,24}(?:cards?|mastercard|visa)|"
             r"add money|fund my (?:account|card)|reloading"):
            return "supported_cards_and_currencies"
        return "fiat_currency_support"
    if wallet:
        return "apple_pay_or_google_pay"
    if direct:
        return "direct_debit_payment_not_recognised"
    if unknown:
        return "card_payment_not_recognised"
    if small_check_charge or fee or h(r"charg\w*|bill\w*|deduct\w*|(?:bank|account|card) statement"):
        return "extra_charge_on_statement"
    if cancelled and not card:
        return "cancel_transfer"
    if reversed_payment:
        return "reverted_card_payment"
    if timing and card:
        return "card_delivery_estimate"
    if ordered or (shipping and missing):
        return "card_arrival"
    if virtual:
        return "getting_virtual_card"
    if geography and h(r"can i (?:use|join|register|get)|available|support\w*|"
                       r"live in|living in|based in|does .{0,21}operate"):
        return "country_support"
    if h(r"forgot\w*|log ?in|logg\w* in|sign in|access my account|locked out"):
        return "passcode_forgotten"
    if h(r"fraud|scam\w*|stole|suspicious"):
        return "compromised_card"
    if verify:
        if failed or declined:
            return "unable_to_verify_identity"
        return "why_verify_identity" if question_why else "verify_my_identity"
    if payment:
        if failed:
            return "declined_card_payment"
        return "pending_card_payment"
    if card:
        if network:
            return "visa_or_mastercard"
        return "card_not_working" if failed else "get_physical_card"
    if h(r"receive|receiving|salary|paid into|inbound"):
        return "receiving_money"
    if timing:
        return "transfer_timing"
    if declined:
        return "declined_transfer"
    if failed:
        return "failed_transfer"
    return "pending_transfer"


def predict(state) -> dict:
    text = _normalize(state)
    canonical = text.replace(" ", "_")
    if canonical in _LABELS:
        return {"answer": canonical}
    return {"answer": _classify(text)}