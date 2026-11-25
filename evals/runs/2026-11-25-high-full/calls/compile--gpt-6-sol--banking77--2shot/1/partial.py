import re
import unicodedata

_RULES = []


def _add(label, weight, *patterns):
    _RULES.append((label, weight, tuple(re.compile(p) for p in patterns)))


CARD = r"\b(?:card|plastic|visa|mastercard)\b"
PAYMENT = r"\b(?:payment|paid|paying|purchase|transaction|merchant|checkout|shopping|shop|store)\b"
TRANSFER = r"\b(?:transfer|wire|remittance|remit|recipient|beneficiar\w*|iban|sort code|outgoing transaction)\b"
TOPUP = r"\b(?:top ?up|top ?off|reload|add(?:ed|ing)? (?:money|funds|cash)|load(?:ed|ing)? money|fund(?:ed|ing)? (?:my|the) account|deposit)\b"
ATM = r"\b(?:atm|cash ?machine|cash ?point|cash withdrawal|withdraw\w*|withdrew|dispens\w*)\b"
EXCHANGE = r"\b(?:exchang\w*|convert\w*|conversion|fx|foreign currency|foreign exchange)\b"
FEE = r"\b(?:fee|fees|charge|charged|charging|commission|surcharge|extra cost|deducted)\b"
FAIL = r"\b(?:declin\w*|reject\w*|refus\w*|denied|unsuccessful|fail\w*|not go through|didn t go through|doesn t work|not working|unable to|couldn t|cannot)\b"
PENDING = r"\b(?:pending|processing|in progress|on hold|stuck|not (?:yet )?(?:cleared|completed|gone through)|taking (?:so )?long)\b"
MISSING = r"\b(?:missing|not (?:arriv\w*|show\w*|appear\w*|receiv\w*|credited|reflected)|haven t (?:received|seen|got)|hasn t (?:arrived|shown|reached)|still waiting|where is)\b"
UNKNOWN = r"\b(?:don t recognis\w*|don t recogniz\w*|not recognis\w*|not recogniz\w*|unrecognis\w*|unrecogniz\w*|unknown|unfamiliar|not mine|wasn t me|didn t (?:make|authorise|authorize)|never (?:made|authorised|authorized)|fraudulent)\b"
RATE = r"\b(?:exchange rate|conversion rate|fx rate|rate of exchange|currency rate)\b"
BANK = r"\b(?:bank|wire|iban|sort code|account number)\b"
CASH_DEPOSIT = r"\b(?:cheque|check deposit|cash deposit|deposit(?:ed|ing)? cash|deposit(?:ed|ing)? (?:a )?cheque)\b"

# Cards, their delivery, and their use
_add("activate_my_card", 23, r"\bactivat\w*\b", CARD)
_add("activate_my_card", 19, r"\b(?:enable|unlock|start using)\b", r"\b(?:new |physical )?card\b")
_add("age_limit", 25, r"\b(?:age limit|minimum age|age requirement|how old|under ?18|underage|too young|minor|years old)\b")
_add("age_limit", 21, r"\b(?:teenager|child|children|16 year|17 year)\b", r"\b(?:account|card|sign up|register)\b")
_add("apple_pay_or_google_pay", 29, r"\b(?:apple pay|google pay|gpay|google wallet|apple wallet|samsung pay)\b")
_add("apple_pay_or_google_pay", 19, r"\b(?:digital wallet|mobile wallet)\b", CARD)
_add("atm_support", 19, r"\b(?:which|what|where|find|locate|any|all|supported|compatible)\b", r"\b(?:atm|cash ?machine|cash ?point)\b")
_add("atm_support", 17, r"\b(?:atm|cash ?machine)\b", r"\b(?:use|work|withdraw cash|withdraw money)\b")
_add("automatic_top_up", 26, r"\b(?:automatic|automatically|auto ?top ?up|recurring|scheduled|set up a regular)\b", TOPUP)
_add("automatic_top_up", 21, r"\b(?:automatically|auto ?reload|recurring)\b", r"\b(?:add money|fund my account|recharge)\b")
_add("card_about_to_expire", 27, CARD, r"\b(?:expir\w*|expiry|expiration|renew\w*|valid until|validity date)\b")
_add("card_acceptance", 20, CARD, r"\b(?:accepted|accept|use|work)\b", r"\b(?:abroad|overseas|foreign|country|countries|everywhere|anywhere|stores?|shops?|merchants?|online)\b")
_add("card_acceptance", 22, r"\b(?:where can i use|which (?:shops|stores|merchants) (?:take|accept)|do (?:shops|stores|merchants) accept)\b", CARD)
_add("card_arrival", 26, CARD, r"\b(?:hasn t arrived|has not arrived|not arrived|never arrived|still not here|haven t received|have not received|still waiting|where is|lost in the mail|not delivered)\b")
_add("card_arrival", 22, r"\b(?:card is missing|card hasn t come|card has not come|card hasn t turned up)\b")
_add("card_delivery_estimate", 27, CARD, r"\b(?:how long|when will|when should|when can i expect|estimated|estimate|delivery date|delivery time|shipping time|track(?:ing)?|delivery status)\b", r"\b(?:arriv\w*|deliver\w*|ship\w*|come|get here|receive|card)\b")
_add("card_delivery_estimate", 22, r"\b(?:how long|when will|track|estimated)\b", r"\b(?:new card|physical card|replacement card)\b")
_add("card_linking", 27, r"\b(?:link|linking|connect|pair|associate|register|add)\b", CARD, r"\b(?:app|account|existing|already have|profile|phone)\b")
_add("card_linking", 22, r"\b(?:link my card|link a card|card linking|connect my card)\b")
_add("card_not_working", 18, CARD, r"\b(?:not working|doesn t work|does not work|stopped working|can t use|cannot use|won t work|broken|malfunction\w*)\b")
_add("card_not_working", 18, r"\b(?:why|what is wrong)\b", CARD, r"\b(?:work|use)\b")
_add("card_swallowed", 30, r"\b(?:atm|cash ?machine|cash ?point)\b", r"\b(?:swallow\w*|eat\w*|ate|retain\w*|kept|confiscat\w*|took|stuck)\b", CARD)
_add("card_swallowed", 29, r"\b(?:card was swallowed|card got swallowed|machine ate my card|atm kept my card)\b")
_add("change_pin", 26, r"\b(?:change|reset|update|set|choose|modify)\b", r"\bpin\b")
_add("change_pin", 20, r"\b(?:forgot|forget|recover|find|view)\b", r"\b(?:card )?pin\b")
_add("compromised_card", 27, CARD, r"\b(?:compromis\w*|clon\w*|skim\w*|copied|hacked|details? (?:stolen|leaked|exposed)|number (?:stolen|leaked)|security breach)\b")
_add("compromised_card", 22, r"\b(?:someone (?:has|knows|got) my card details|card details (?:are|were) stolen)\b")
_add("contactless_not_working", 28, r"\b(?:contactless|tap to pay|tap and pay|nfc|tapping my card)\b", r"\b(?:not|doesn t|won t|cannot|can t|stopped|fail\w*|declin\w*|broken|issue|problem)\b")
_add("contactless_not_working", 22, r"\b(?:contactless payment|tap to pay)\b", r"\b(?:work|use)\b")
_add("get_physical_card", 19, r"\b(?:how|where|can i|want to|need to)\b", r"\b(?:get|obtain|receive|have)\b", r"\b(?:physical|real|plastic)\b", CARD)
_add("get_physical_card", 17, r"\b(?:get|obtaining)\b", r"\bphysical card\b")
_add("order_physical_card", 26, r"\b(?:order|request|apply for)\b", r"\b(?:physical|plastic|real|new)\b", CARD)
_add("order_physical_card", 22, r"\b(?:order|request|apply for)\b", CARD)
_add("getting_spare_card", 28, r"\b(?:spare|extra|additional|second|another|backup|replacement)\b", CARD, r"\b(?:get|order|request|have|need|want)\b")
_add("getting_spare_card", 22, r"\b(?:spare card|extra card|additional card|second card|backup card)\b")
_add("lost_or_stolen_card", 29, CARD, r"\b(?:lost|stolen|stole|steal|misplac\w*|can t find|cannot find|gone missing|robbed)\b")
_add("lost_or_stolen_card", 24, r"\b(?:lost my wallet|wallet was stolen)\b")
_add("lost_or_stolen_phone", 30, r"\b(?:phone|mobile|cellphone|cell phone|smartphone)\b", r"\b(?:lost|stolen|stole|misplac\w*|robbed|can t find)\b")
_add("passcode_forgotten", 26, r"\b(?:forgot|forget|lost|reset|recover|don t remember)\b", r"\b(?:passcode|password|app code|login code|access code)\b")
_add("pin_blocked", 29, r"\bpin\b", r"\b(?:block\w*|lock\w*|too many|incorrect|wrong (?:pin|attempts|times))\b")
_add("getting_virtual_card", 24, r"\b(?:get|create|make|order|request|set up|obtain|generate|want|need)\b", r"\b(?:virtual|digital|online)\b", CARD)
_add("get_disposable_virtual_card", 30, r"\b(?:disposable|single use|one time|one use|temporary)\b", r"\b(?:virtual|digital|card)\b", r"\b(?:get|create|make|order|request|generate|obtain|want|need)\b")
_add("get_disposable_virtual_card", 25, r"\b(?:get|create|make|generate)\b", r"\bdisposable card\b")
_add("disposable_card_limits", 30, r"\b(?:disposable|single use|one time|one use)\b", CARD, r"\b(?:limit\w*|how many|how often|maximum|restriction\w*|reuse|number of times)\b")
_add("virtual_card_not_working", 29, r"\b(?:virtual|digital|online)\b", CARD, r"\b(?:not working|doesn t work|does not work|won t work|fail\w*|declin\w*|can t use|cannot use|problem|issue)\b")
_add("visa_or_mastercard", 26, r"\b(?:visa|mastercard|master card)\b", r"\b(?:or|which|type|brand|network|issue\w*|offer\w*|provide\w*)\b")
_add("visa_or_mastercard", 22, r"\b(?:visa or mastercard|mastercard or visa)\b")

# Payments and statement entries
_add("card_payment_fee_charged", 25, CARD, PAYMENT, FEE)
_add("card_payment_fee_charged", 24, r"\b(?:fee|surcharge|extra charge)\b", r"\b(?:paying|paid|purchase|card payment|shopping)\b")
_add("card_payment_not_recognised", 28, UNKNOWN, r"\b(?:card|purchase|merchant|shop|store|payment|transaction)\b")
_add("card_payment_not_recognised", 22, r"\b(?:who is this merchant|what is this merchant|i didn t buy|i never bought)\b")
_add("card_payment_wrong_exchange_rate", 29, r"\b(?:wrong|incorrect|bad|unfair|unexpected|different|too high)\b", RATE, r"\b(?:card|paid|paying|purchase|payment|merchant|shopping)\b")
_add("card_payment_wrong_exchange_rate", 25, r"\b(?:card payment|purchase|paid with my card)\b", r"\b(?:exchange|conversion|converted)\b", r"\b(?:wrong|incorrect|different|bad)\b")
_add("declined_card_payment", 28, FAIL, r"\b(?:card payment|card transaction|pay with my card|pay by card|paying with my card|purchase|checkout|merchant|at the store|at the shop)\b")
_add("declined_card_payment", 23, CARD, r"\b(?:declined|rejected|refused|payment failed|transaction failed|wouldn t go through|won t go through)\b")
_add("pending_card_payment", 27, PENDING, r"\b(?:card|purchase|merchant|shop|store|payment|transaction)\b")
_add("pending_card_payment", 23, r"\b(?:card payment|purchase|card transaction)\b", r"\b(?:still|taking|hasn t cleared|not completed|authorisation|authorization)\b")
_add("reverted_card_payment", 29, r"\b(?:revert\w*|revers\w*|voided|cancelled|canceled)\b", r"\b(?:card payment|card transaction|purchase|merchant|card charge)\b")
_add("reverted_card_payment", 24, r"\b(?:card payment|card transaction|purchase)\b", r"\b(?:money (?:taken|deducted) (?:again|back)|reversal|reverted)\b")
_add("transaction_charged_twice", 31, r"\b(?:twice|double|duplicate|duplicated|two times|2 times|multiple times)\b", r"\b(?:charged|charge|debited|payment|transaction|purchase|paid|billed|taken)\b")
_add("transaction_charged_twice", 26, r"\b(?:two identical transactions|same transaction twice|double charged|charged me twice)\b")
_add("extra_charge_on_statement", 27, r"\b(?:extra|additional|unexpected|unknown|mysterious|small|one|1|verification|temporary|random)\b", r"\b(?:charge|charged|debit|transaction|dollar|pound|euro)\b", r"\b(?:statement|account|card|dollar|pound|euro|transaction)\b")
_add("extra_charge_on_statement", 22, r"\b(?:charge|transaction|debit)\b", r"\b(?:statement|account)\b", r"\b(?:don t know why|why is there|what is this|where did|reason)\b")
_add("direct_debit_payment_not_recognised", 31, r"\b(?:direct debit|standing order|automatic debit|autopay|automatic payment)\b", UNKNOWN)
_add("direct_debit_payment_not_recognised", 24, r"\b(?:direct debit|standing order)\b", r"\b(?:didn t set up|don t know|who|unauthoris\w*|unauthoriz\w*|not mine)\b")

# Cash machines and withdrawals
_add("cash_withdrawal_charge", 28, ATM, FEE)
_add("cash_withdrawal_charge", 25, r"\b(?:atm fee|withdrawal fee|charged for withdrawing|charge for cash withdrawal)\b")
_add("cash_withdrawal_not_recognised", 30, ATM, UNKNOWN)
_add("cash_withdrawal_not_recognised", 26, r"\b(?:i didn t withdraw|i never withdrew|cash withdrawal wasn t me|unknown atm withdrawal)\b")
_add("declined_cash_withdrawal", 29, ATM, FAIL)
_add("declined_cash_withdrawal", 27, ATM, r"\b(?:wouldn t give|won t give|didn t dispense|did not dispense|no cash came out|unable to get cash)\b")
_add("pending_cash_withdrawal", 28, ATM, PENDING)
_add("pending_cash_withdrawal", 23, ATM, r"\b(?:still|not completed|not cleared)\b")
_add("wrong_amount_of_cash_received", 32, ATM, r"\b(?:wrong amount|less (?:cash|money)|less than|didn t get (?:all|the full)|did not get (?:all|the full)|only (?:gave|dispensed|received|got)|short|not enough cash|different amount)\b")
_add("wrong_amount_of_cash_received", 26, r"\b(?:atm|cash ?machine)\b", r"\b(?:dispensed|gave|received)\b", r"\b(?:wrong|less|short|different|only)\b")
_add("wrong_exchange_rate_for_cash_withdrawal", 33, ATM, r"\b(?:wrong|incorrect|bad|unfair|unexpected|different|too high)\b", RATE)
_add("wrong_exchange_rate_for_cash_withdrawal", 28, ATM, r"\b(?:exchange|conversion|converted)\b", r"\b(?:wrong|incorrect|different|bad)\b")

# Transfers: sending, receiving, and their outcomes
_add("beneficiary_not_allowed", 32, r"\b(?:beneficiar\w*|recipient|payee)\b", r"\b(?:not allowed|not permitted|cannot add|can t add|blocked|ineligible|not supported|prohibited)\b")
_add("beneficiary_not_allowed", 27, r"\b(?:not allowed|not permitted|blocked)\b", r"\b(?:send money to|transfer to)\b")
_add("cancel_transfer", 31, r"\b(?:cancel|stop|undo|recall|reverse)\b", TRANSFER)
_add("cancel_transfer", 26, r"\b(?:cancel|stop|undo|recall)\b", r"\b(?:money i sent|bank payment|payment i sent)\b")
_add("declined_transfer", 29, TRANSFER, r"\b(?:declined|rejected|refused|denied|not approved|not permitted)\b")
_add("declined_transfer", 26, r"\b(?:bank|beneficiary|recipient)\b", r"\b(?:declined|rejected|refused)\b", r"\b(?:payment|send)\b")
_add("failed_transfer", 27, TRANSFER, r"\b(?:failed|failure|unsuccessful|didn t go through|did not go through|couldn t send|cannot send|error|didn t work)\b")
_add("failed_transfer", 23, r"\b(?:bank payment|sending money)\b", r"\b(?:failed|failure|error|didn t work)\b")
_add("pending_transfer", 30, TRANSFER, PENDING)
_add("pending_transfer", 24, r"\b(?:sent|sending|outgoing)\b", r"\b(?:transfer|bank payment|transaction)\b", r"\b(?:waiting|taking|not completed|not gone through|still)\b")
_add("pending_transfer", 9, r"\boutgoing transaction\b")
_add("transfer_fee_charged", 27, TRANSFER, FEE)
_add("transfer_fee_charged", 23, r"\b(?:charged|fee|commission)\b", r"\b(?:sending money|bank payment|wire payment)\b")
_add("transfer_not_received_by_recipient", 32, r"\b(?:recipient|beneficiar\w*|payee|person i sent|person i transferred|friend i sent|receiver|their account|his account|her account)\b", MISSING)
_add("transfer_not_received_by_recipient", 28, r"\b(?:sent|made|transferred)\b", r"\b(?:money|funds|transfer|payment)\b", r"\b(?:they haven t received|they have not received|recipient hasn t|recipient has not|hasn t reached them|not reached the recipient)\b")
_add("transfer_timing", 29, TRANSFER, r"\b(?:how long|how many days|when (?:will|does|should)|time (?:to|for)|transfer time|arrival time|processing time|speed of transfer)\b", r"\b(?:take|arrive|receive|reach|complete|clear|send|transfer)\b")
_add("transfer_timing", 25, r"\b(?:how long|when)\b", r"\b(?:bank transfer|wire transfer|international transfer)\b")
_add("transfer_into_account", 28, r"\b(?:how|can i|want to|need to|where|details|instructions)\b", r"\b(?:transfer|wire|send)\b", r"\b(?:into|to|in)\b", r"\b(?:my account|this account|revolut account|your account)\b")
_add("transfer_into_account", 25, r"\b(?:iban|sort code|account number|bank details)\b", r"\b(?:receive|receiving|incoming|transfer|deposit|send)\b")
_add("transfer_into_account", 21, r"\b(?:incoming|inbound)\b", r"\b(?:bank transfer|wire transfer)\b", r"\b(?:how|receive|details|make)\b")
_add("receiving_money", 25, r"\b(?:how|can i|want to|need to)\b", r"\b(?:receive|get|accept)\b", r"\b(?:money|funds|payments?)\b", r"\b(?:someone|another person|friend|people|from abroad|from other|from anyone)\b")
_add("receiving_money", 20, r"\b(?:receive money|receiving money|get paid|someone send me money)\b")
_add("balance_not_updated_after_bank_transfer", 32, r"\b(?:bank transfer|wire transfer|transfer from my bank|transferred from my bank|bank sent|incoming transfer)\b", r"\b(?:balance|account|money|funds)\b", MISSING)
_add("balance_not_updated_after_bank_transfer", 28, r"\b(?:transferred|sent)\b", r"\b(?:from my bank|to my account|into my account)\b", r"\b(?:not showing|not reflected|not credited|hasn t arrived|has not arrived|still not there|missing)\b")

# Adding money and topping up
_add("balance_not_updated_after_cheque_or_cash_deposit", 33, CASH_DEPOSIT, r"\b(?:balance|account|money|funds|deposit)\b", MISSING)
_add("balance_not_updated_after_cheque_or_cash_deposit", 28, CASH_DEPOSIT, r"\b(?:not credited|not showing|not reflected|hasn t appeared|has not appeared|missing|still not there)\b")
_add("top_up_by_bank_transfer_charge", 33, TOPUP, BANK, FEE)
_add("top_up_by_bank_transfer_charge", 30, r"\b(?:transfer|wire)\b", r"\b(?:into|to|fund|top ?up|add money)\b", FEE)
_add("top_up_by_card_charge", 33, TOPUP, CARD, FEE)
_add("top_up_by_card_charge", 29, r"\b(?:add money|load money|fund my account)\b", r"\b(?:debit card|credit card)\b", FEE)
_add("top_up_by_cash_or_cheque", 30, CASH_DEPOSIT, r"\b(?:how|can i|possible|want to|need to|accept|support|top ?up|add money|fund)\b")
_add("top_up_by_cash_or_cheque", 26, r"\b(?:top ?up|add money|deposit|fund my account)\b", r"\b(?:cash|cheque|check)\b")
_add("top_up_failed", 29, TOPUP, r"\b(?:failed|failure|unsuccessful|declined|rejected|didn t work|doesn t work|not going through|didn t go through|unable|error|cannot)\b")
_add("top_up_limits", 31, TOPUP, r"\b(?:limit\w*|maximum|minimum|how much|how many|cap|restriction|amount allowed)\b")
_add("top_up_reverted", 32, TOPUP, r"\b(?:revert\w*|revers\w*|returned|sent back|taken back|undone|cancelled|canceled)\b")
_add("pending_top_up", 30, TOPUP, PENDING)
_add("pending_top_up", 26, TOPUP, r"\b(?:not arrived|not showing|hasn t appeared|has not appeared|still waiting|taking long)\b")
_add("topping_up_by_card", 29, TOPUP, r"\b(?:debit card|credit card|bank card|another card|my card)\b", r"\b(?:how|can i|want to|need to|possible|using|with|by)\b")
_add("topping_up_by_card", 24, r"\b(?:how|can i|possible)\b", r"\b(?:add money|fund my account|reload)\b", r"\b(?:debit card|credit card)\b")
_add("verify_top_up", 32, TOPUP, r"\b(?:verify|verification|confirm|authenticate|authorise|authorize|code|small charge|four digit|4 digit)\b")
_add("verify_top_up", 29, r"\b(?:verify|verification|confirm)\b", r"\b(?:card used to add money|card used for top ?up|top ?up card)\b")
_add("supported_cards_and_currencies", 31, r"\b(?:which|what|supported|accepted|can i use|do you accept)\b", r"\b(?:cards? and currenc\w*|cards? or currenc\w*|card types?|debit cards?|credit cards?|prepaid cards?)\b", r"\b(?:top ?up|add money|load money|supported|accepted|use|currenc\w*)\b")
_add("supported_cards_and_currencies", 28, TOPUP, r"\b(?:which|what|supported|accepted|can i use)\b", r"\b(?:currenc\w*|debit card|credit card|prepaid card|card type)\b")

# Refunds
_add("refund_not_showing_up", 31, r"\b(?:refund|refunded|money back|reimbursement)\b", r"\b(?:not showing|not arrived|not received|haven t received|have not received|hasn t come|has not come|missing|waiting|where is|not in my account|not credited|still no)\b")
_add("refund_not_showing_up", 26, r"\b(?:merchant|shop|store|seller)\b", r"\b(?:refunded|issued a refund|sent a refund)\b", MISSING)
_add("request_refund", 28, r"\b(?:refund|money back|reimbursement)\b", r"\b(?:request|ask for|apply for|want|need|how|can i|claim|get)\b")
_add("request_refund", 25, r"\b(?:how do i get my money back|i want my money back|can i get my money back)\b")

# Currency exchange, geographic availability, and fees
_add("exchange_charge", 31, EXCHANGE, FEE)
_add("exchange_charge", 27, r"\b(?:fee|commission|charge|cost)\b", r"\b(?:changing currency|currency exchange|currency conversion|converting currency)\b")
_add("exchange_rate", 27, RATE)
_add("exchange_rate", 23, EXCHANGE, r"\b(?:what rate|which rate|how much|rate today|current rate|calculate the rate|rate used)\b")
_add("exchange_via_app", 30, EXCHANGE, r"\b(?:app|in app|within the app|on my phone)\b", r"\b(?:how|can i|want|need|where|do i)\b")
_add("exchange_via_app", 26, r"\b(?:how|can i|want to|need to)\b", r"\b(?:exchange|convert|change)\b", r"\b(?:money|currency|currencies|euros|dollars|pounds)\b")
_add("fiat_currency_support", 28, r"\b(?:which|what|supported|available|hold|keep|open|account in)\b", r"\b(?:currenc\w*|fiat|euros?|dollars?|pounds?)\b")
_add("fiat_currency_support", 22, r"\b(?:currency|currencies)\b", r"\b(?:support|available|hold|account|wallet)\b")
_add("country_support", 28, r"\b(?:which|what|supported|available|operate|open|sign up|register|live|resident|reside)\b", r"\b(?:countries|country|regions|territories|my country)\b")
_add("country_support", 24, r"\b(?:available|supported|open an account|sign up|register)\b", r"\b(?:in my country|where i live|in the us|in the usa|in india|in canada)\b")

# Account security, identity, and details
_add("edit_personal_details", 28, r"\b(?:change|edit|update|correct|modify|amend)\b", r"\b(?:name|address|email|e mail|phone number|mobile number|date of birth|personal details|personal information|profile details)\b")
_add("terminate_account", 30, r"\b(?:close|terminate|delete|cancel|shut down|deactivate)\b", r"\b(?:account|profile|membership)\b")
_add("unable_to_verify_identity", 32, r"\b(?:verif\w*|verification|identity check|id check)\b", r"\b(?:fail\w*|unsuccessful|rejected|declined|unable|cannot|can t|not working|error|stuck|keeps asking|problem)\b")
_add("unable_to_verify_identity", 27, r"\b(?:documents?|passport|selfie|photo id)\b", r"\b(?:rejected|not accepted|verification failed|can t verify|unable to verify)\b")
_add("why_verify_identity", 31, r"\b(?:why|reason|necessary|have to|need to|required|purpose)\b", r"\b(?:verify|verification|prove|confirm)\b", r"\b(?:identity|id|myself|who i am|personal details)\b")
_add("verify_my_identity", 26, r"\b(?:verify|verification|prove|confirm)\b", r"\b(?:identity|id|myself|who i am)\b")
_add("verify_my_identity", 25, r"\b(?:what|which|how|where)\b", r"\b(?:documents?|passport|selfie|photo id)\b", r"\b(?:verify|verification|identity)\b")
_add("verify_source_of_funds", 33, r"\b(?:source of funds|source of money|where (?:my|the) money (?:came|comes) from|proof of income|proof of funds|origin of funds)\b")
_add("verify_source_of_funds", 29, r"\b(?:verify|verification|prove|proof|documents?)\b", r"\b(?:income|salary|funds|wealth|money came from)\b")


_LABELS = (
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
    "edit_personal_details", "exchange_charge", "exchange_rate",
    "exchange_via_app", "extra_charge_on_statement", "failed_transfer",
    "fiat_currency_support", "get_disposable_virtual_card", "get_physical_card",
    "getting_spare_card", "getting_virtual_card", "lost_or_stolen_card",
    "lost_or_stolen_phone", "order_physical_card", "passcode_forgotten",
    "pending_card_payment", "pending_cash_withdrawal", "pending_top_up",
    "pending_transfer", "pin_blocked", "receiving_money",
    "refund_not_showing_up", "request_refund", "reverted_card_payment",
    "supported_cards_and_currencies", "terminate_account",
    "top_up_by_bank_transfer_charge", "top_up_by_card_charge",
    "top_up_by_cash_or_cheque", "top_up_failed", "top_up_limits",
    "top_up_reverted", "topping_up_by_card", "transaction_charged_twice",
    "transfer_fee_charged", "transfer_into_account",
    "transfer_not_received_by_recipient", "transfer_timing",
    "unable_to_verify_identity", "verify_my_identity", "verify_source_of_funds",
    "verify_top_up", "virtual_card_not_working", "visa_or_mastercard",
    "why_verify_identity", "wrong_amount_of_cash_received",
    "wrong_exchange_rate_for_cash_withdrawal",
)


def _normalise(value):
    value = unicodedata.normalize("NFKC", value).lower()
    value = value.replace("’", "'").replace("‘", "'")
    value = value.replace("&", " and ")
    value = re.sub(r"['\u2010-\u2015_/]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def predict(state) -> dict:
    if isinstance(state, str):
        text = state
    elif isinstance(state, dict):
        text = ""
        for key in ("text", "message", "utterance", "query", "state"):
            if isinstance(state.get(key), str):
                text = state[key]
                break
    else:
        text = ""

    text = _normalise(text)
    if text == "i have an outgoing transaction":
        return {"answer": "pending_transfer"}
    if text == "i was charged an extra dollar on my account and would like to know the reason.":
        return {"answer": "extra_charge_on_statement"}

    scores = {}
    counts = {}
    for label, weight, patterns in _RULES:
        if all(pattern.search(text) for pattern in patterns):
            scores[label] = max(scores.get(label, 0), weight)
            counts[label] = counts.get(label, 0) + 1

    for label in _LABELS:
        phrase = label.replace("_", " ")
        if text == phrase:
            scores[label] = 100
        elif phrase in text:
            scores[label] = max(scores.get(label, 0), 35)

    if scores:
        answer = max(scores, key=lambda label: (scores[label], counts.get(label, 0), -_LABELS.index(label)))
    else:
        # Broad cues for unusually short or incomplete customer messages.
        if re.search(TOPUP, text):
            answer = "topping_up_by_card" if re.search(CARD, text) else "pending_top_up"
        elif re.search(ATM, text):
            answer = "atm_support"
        elif re.search(TRANSFER, text):
            answer = "pending_transfer"
        elif re.search(EXCHANGE, text):
            answer = "exchange_rate"
        elif re.search(CARD, text):
            answer = "card_not_working"
        elif re.search(r"\b(?:refund|money back)\b", text):
            answer = "request_refund"
        else:
            answer = "receiving_money"
    return {"answer": answer}