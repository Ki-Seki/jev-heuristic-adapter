import re
import unicodedata
from collections import Counter


CATEGORIES = (
    "activate_my_card", "age_limit", "apple_pay_or_google_pay",
    "atm_support", "automatic_top_up",
    "balance_not_updated_after_bank_transfer",
    "balance_not_updated_after_cheque_or_cash_deposit",
    "beneficiary_not_allowed", "cancel_transfer", "card_about_to_expire",
    "card_acceptance", "card_arrival", "card_delivery_estimate",
    "card_linking", "card_not_working", "card_payment_fee_charged",
    "card_payment_not_recognised", "card_payment_wrong_exchange_rate",
    "card_swallowed", "cash_withdrawal_charge",
    "cash_withdrawal_not_recognised", "change_pin", "compromised_card",
    "contactless_not_working", "country_support", "declined_card_payment",
    "declined_cash_withdrawal", "declined_transfer",
    "direct_debit_payment_not_recognised", "disposable_card_limits",
    "edit_personal_details", "exchange_charge", "exchange_rate",
    "exchange_via_app", "extra_charge_on_statement", "failed_transfer",
    "fiat_currency_support", "get_disposable_virtual_card",
    "get_physical_card", "getting_spare_card", "getting_virtual_card",
    "lost_or_stolen_card", "lost_or_stolen_phone", "order_physical_card",
    "passcode_forgotten", "pending_card_payment",
    "pending_cash_withdrawal", "pending_top_up", "pending_transfer",
    "pin_blocked", "receiving_money", "refund_not_showing_up",
    "request_refund", "reverted_card_payment",
    "supported_cards_and_currencies", "terminate_account",
    "top_up_by_bank_transfer_charge", "top_up_by_card_charge",
    "top_up_by_cash_or_cheque", "top_up_failed", "top_up_limits",
    "top_up_reverted", "topping_up_by_card", "transaction_charged_twice",
    "transfer_fee_charged", "transfer_into_account",
    "transfer_not_received_by_recipient", "transfer_timing",
    "unable_to_verify_identity", "verify_my_identity",
    "verify_source_of_funds", "verify_top_up",
    "virtual_card_not_working", "visa_or_mastercard",
    "why_verify_identity", "wrong_amount_of_cash_received",
    "wrong_exchange_rate_for_cash_withdrawal",
)

# Each expression describes evidence for the corresponding intent. Expressions
# are also used for less explicit questions that do not satisfy a shortcut below.
PATTERNS = {
    "activate_my_card": [
        r"activat\w* (?:my |the |a |new )?card",
        r"card.{0,30}(?:activat|enable)",
        r"(?:start|begin) using (?:my |the )?(?:new )?card",
    ],
    "age_limit": [
        r"age (?:limit|requirement|restriction)",
        r"(?:minimum|how old|underage|under 18|minor|too young)",
        r"(?:years old|at what age).{0,35}(?:account|card|join|sign up)",
    ],
    "apple_pay_or_google_pay": [
        r"apple pay|google pay|google wallet|apple wallet",
        r"(?:add|link|use).{0,35}(?:wallet|pay on my phone|phone to pay)",
        r"(?:pay|payment).{0,20}(?:iphone|android|smartphone)",
    ],
    "atm_support": [
        r"which atms?|what atms?|atm (?:support|network|availability)",
        r"(?:use|work|accepted).{0,35}(?:atms?|cash machines?)",
        r"(?:where|which banks?).{0,35}(?:withdraw|cash machines?|atms?)",
    ],
    "automatic_top_up": [
        r"(?:automatic|automated|auto|recurring|scheduled) top up",
        r"top up.{0,30}(?:automatically|recurring|on its own)",
        r"(?:automatically|regularly).{0,30}(?:add funds|add money|recharge)",
    ],
    "balance_not_updated_after_bank_transfer": [
        r"(?:bank transfer|wire transfer).{0,65}(?:balance|not showing|not credited|not arrived|not received|missing)",
        r"(?:balance|account).{0,65}(?:bank transfer|wire transfer).{0,25}(?:not|missing)",
        r"(?:sent|transferred).{0,40}(?:to my account|into my account).{0,35}(?:not|missing|where)",
    ],
    "balance_not_updated_after_cheque_or_cash_deposit": [
        r"(?:cash|cheque|check) deposit.{0,60}(?:not|missing|balance|where)",
        r"(?:deposit|deposited).{0,25}(?:cash|cheque|check).{0,40}(?:not|missing|balance)",
        r"(?:balance|account).{0,45}(?:cash|cheque|check) deposit",
    ],
    "beneficiary_not_allowed": [
        r"beneficiar\w*.{0,35}(?:not allowed|cannot|cant|unable|blocked|ineligible|invalid)",
        r"(?:not allowed|unable|cannot|cant).{0,35}(?:beneficiar|recipient|payee)",
        r"(?:recipient|beneficiar|payee).{0,35}(?:not supported|not permitted|not eligible)",
    ],
    "cancel_transfer": [
        r"(?:cancel|stop|recall|undo|reverse).{0,35}(?:transfer|wire|payment to|money sent)",
        r"(?:transfer|wire).{0,30}(?:cancel|stop|recall|undo)",
    ],
    "card_about_to_expire": [
        r"(?:card|plastic).{0,30}(?:expir|expiry|expiration|out of date)",
        r"(?:expir|expiry|expiration).{0,30}card",
        r"(?:renew|replace).{0,25}(?:expiring|expired) card",
    ],
    "card_acceptance": [
        r"where.{0,30}(?:card).{0,25}(?:accepted|use|work)",
        r"(?:card).{0,30}(?:accepted|usable).{0,25}(?:shops|stores|merchants|abroad|online)",
        r"(?:can i|will it).{0,25}(?:use|pay).{0,25}(?:card).{0,30}(?:abroad|overseas|in shops|online)",
        r"(?:merchant|shop|store).{0,30}(?:accept|take).{0,20}card",
    ],
    "card_arrival": [
        r"(?:card|delivery).{0,35}(?:hasnt|has not|not|never|still).{0,20}(?:arriv|come|delivered)",
        r"(?:where is|where s|track).{0,25}(?:my |the )?card",
        r"(?:ordered|requested).{0,25}card.{0,35}(?:still waiting|not received|not arrived|missing)",
        r"card.{0,25}(?:lost in the mail|lost in transit|delivery is late)",
    ],
    "card_delivery_estimate": [
        r"(?:how long|when|estimated|estimate|delivery time|shipping time).{0,45}(?:card|deliver|arriv|ship)",
        r"(?:card|deliver|ship).{0,40}(?:how long|when|estimated|estimate|days|weeks)",
        r"(?:when should|when will).{0,25}card.{0,15}(?:arrive|come)",
    ],
    "card_linking": [
        r"(?:link|connect|pair|add|register).{0,30}(?:physical |new )?card.{0,30}(?:app|account|profile)?",
        r"card.{0,30}(?:link|connect|pair).{0,25}(?:app|account)",
    ],
    "card_not_working": [
        r"(?:physical |bank |my )?card.{0,35}(?:not working|doesnt work|does not work|stopped working|broken|malfunction)",
        r"(?:cannot|cant|unable to).{0,20}use.{0,15}card",
        r"card.{0,25}(?:damaged|defective|not functioning)",
    ],
    "card_payment_fee_charged": [
        r"(?:card payment|card purchase|paid with my card).{0,45}(?:fee|surcharge|commission|extra charge)",
        r"(?:fee|surcharge|commission).{0,35}(?:card payment|card purchase|paying by card)",
    ],
    "card_payment_not_recognised": [
        r"(?:card payment|card transaction|card purchase).{0,40}(?:dont recognise|dont recognize|not mine|unauthori|unknown|unfamiliar)",
        r"(?:dont recognise|dont recognize|not mine|unauthori|unknown|unfamiliar).{0,40}(?:card payment|card transaction|purchase)",
        r"(?:someone else|i never|i did not|i didnt).{0,35}(?:use my card|made? (?:this |a )?(?:card )?(?:payment|purchase|transaction))",
    ],
    "card_payment_wrong_exchange_rate": [
        r"(?:card payment|card purchase|paid with my card).{0,55}(?:exchange rate|conversion rate|wrong rate|fx rate)",
        r"(?:exchange rate|conversion rate|wrong rate|fx rate).{0,45}(?:card payment|card purchase|card transaction)",
    ],
    "card_swallowed": [
        r"(?:atm|cash machine|cashpoint).{0,35}(?:swallow|kept|retain|eat|took|captur|seiz).{0,20}card",
        r"card.{0,25}(?:swallow|kept|retain|eat|captur|seiz).{0,25}(?:atm|machine)",
        r"(?:atm|machine).{0,25}(?:wont|will not|didnt|did not).{0,15}(?:return|give back).{0,15}card",
    ],
    "cash_withdrawal_charge": [
        r"(?:atm|cash withdrawal|withdraw(?:ing)? cash).{0,45}(?:fee|charge|commission|cost|surcharge)",
        r"(?:fee|charge|commission|cost|surcharge).{0,45}(?:atm|cash withdrawal|withdraw(?:ing)? cash)",
    ],
    "cash_withdrawal_not_recognised": [
        r"(?:atm|cash withdrawal).{0,45}(?:dont recogni|not mine|unauthori|unknown|didnt make|never made)",
        r"(?:dont recogni|not mine|unauthori|unknown|didnt make|never made).{0,45}(?:atm|cash withdrawal)",
        r"(?:i didnt|i did not|i never).{0,25}withdraw.{0,15}cash",
    ],
    "change_pin": [
        r"(?:change|reset|update|modify|choose|set).{0,25}(?:my |the )?(?:card )?pin",
        r"(?:pin|pin number).{0,25}(?:change|reset|update|modify)",
        r"(?:forgot|dont know|find|retrieve).{0,25}(?:card )?pin",
    ],
    "compromised_card": [
        r"(?:card|card details|card number).{0,35}(?:compromis|clon|hack|skim|expos|leak)",
        r"(?:compromis|clon|hack|skim|expos|leak).{0,35}(?:card|card details|card number)",
        r"(?:someone|stranger).{0,25}(?:has|knows|got).{0,25}(?:card number|card details)",
    ],
    "contactless_not_working": [
        r"(?:contactless|tap to pay|tap and pay|nfc).{0,35}(?:not working|doesnt work|does not work|failed|declined|unable|broken)",
        r"(?:cannot|cant|unable to).{0,25}(?:tap|use contactless|pay contactless)",
        r"(?:tap|contactless).{0,30}(?:stopped working|not accepted)",
    ],
    "country_support": [
        r"(?:which|what|supported|available).{0,35}countries",
        r"(?:country|countries).{0,35}(?:support|available|eligible|open an account|sign up)",
        r"(?:live|resident|reside).{0,30}(?:country|abroad|outside).{0,30}(?:account|sign up|join)",
    ],
    "declined_card_payment": [
        r"(?:card payment|card transaction|purchase|payment by card).{0,35}(?:declin|reject|refus|denied)",
        r"(?:declin|reject|refus|denied).{0,35}(?:card payment|card transaction|purchase|payment by card)",
        r"(?:card|payment).{0,25}(?:declin|reject|refus|denied).{0,25}(?:shop|store|merchant|online|checkout)",
    ],
    "declined_cash_withdrawal": [
        r"(?:atm|cash withdrawal|withdraw cash).{0,35}(?:declin|reject|refus|denied)",
        r"(?:declin|reject|refus|denied).{0,35}(?:atm|cash withdrawal|withdraw cash)",
        r"(?:atm|cash machine).{0,35}(?:wouldnt|would not|wont|will not).{0,20}(?:dispense|let me withdraw|give me cash)",
    ],
    "declined_transfer": [
        r"(?:transfer|bank payment|wire).{0,35}(?:declin|reject|refus|denied)",
        r"(?:declin|reject|refus|denied).{0,35}(?:transfer|bank payment|wire)",
    ],
    "direct_debit_payment_not_recognised": [
        r"(?:direct debit|autopay|automatic debit).{0,45}(?:dont recogni|not mine|unauthori|unknown|unfamiliar|never set up)",
        r"(?:dont recogni|not mine|unauthori|unknown|unfamiliar).{0,45}(?:direct debit|autopay|automatic debit)",
    ],
    "disposable_card_limits": [
        r"(?:disposable|single use|one time).{0,35}(?:card).{0,35}(?:limit|maximum|how many|restriction)",
        r"(?:limit|maximum|how many|restriction).{0,40}(?:disposable|single use|one time).{0,15}card",
    ],
    "edit_personal_details": [
        r"(?:change|update|edit|correct).{0,30}(?:name|address|phone number|email|personal details|personal information|date of birth)",
        r"(?:name|address|phone number|email|personal details|personal information|date of birth).{0,30}(?:change|update|edit|incorrect|wrong)",
    ],
    "exchange_charge": [
        r"(?:exchange|convert|conversion|foreign currency|currency exchange).{0,45}(?:fee|charge|commission|cost|surcharge)",
        r"(?:fee|charge|commission|cost|surcharge).{0,45}(?:exchange|convert|conversion|foreign currency)",
    ],
    "exchange_rate": [
        r"(?:exchange|conversion|fx|currency) rate",
        r"(?:rate|value).{0,30}(?:exchange|convert|conversion|currenc)",
        r"(?:how much|what rate).{0,30}(?:currency|euros?|dollars?|pounds?)",
    ],
    "exchange_via_app": [
        r"(?:exchange|convert|swap).{0,35}(?:currenc|money|funds).{0,35}(?:app|account)?",
        r"(?:app).{0,40}(?:exchange|convert|swap).{0,20}(?:currenc|money)",
        r"(?:buy|sell).{0,25}(?:foreign currency|euros?|dollars?)",
    ],
    "extra_charge_on_statement": [
        r"(?:extra|additional|unexpected|mysterious).{0,30}(?:charge|transaction|debit).{0,35}(?:statement|account|card)?",
        r"(?:statement|account).{0,35}(?:extra|additional|unexpected|mysterious).{0,20}(?:charge|transaction)",
        r"(?:charged|debited).{0,20}(?:more than|extra).{0,25}(?:statement|bill|receipt)",
    ],
    "failed_transfer": [
        r"(?:transfer|wire|bank payment).{0,35}(?:fail|error|unsuccessful|wont go through|didnt go through)",
        r"(?:fail|error|unsuccessful|wont go through|didnt go through).{0,35}(?:transfer|wire|bank payment)",
    ],
    "fiat_currency_support": [
        r"(?:which|what|supported|available).{0,25}(?:fiat )?currenc",
        r"(?:currenc|fiat).{0,35}(?:support|available|hold|account|exchange)",
        r"(?:hold|keep|store|open an account in).{0,20}(?:euros?|dollars?|pounds?|currenc)",
    ],
    "get_disposable_virtual_card": [
        r"(?:get|create|make|generate|obtain|order).{0,35}(?:disposable|single use|one time).{0,20}(?:virtual )?card",
        r"(?:disposable|single use|one time).{0,25}(?:virtual )?card.{0,30}(?:get|create|make|generate|obtain)",
    ],
    "get_physical_card": [
        r"(?:how|where).{0,15}(?:get|obtain|receive).{0,25}(?:physical|plastic|real) card",
        r"(?:get|obtain|receive).{0,20}(?:physical|plastic|real) card",
    ],
    "getting_spare_card": [
        r"(?:spare|second|extra|additional|backup|replacement).{0,20}(?:physical )?card",
        r"(?:another|more than one|multiple).{0,20}(?:physical )?cards?",
    ],
    "getting_virtual_card": [
        r"(?:get|create|make|generate|obtain|order).{0,30}(?:virtual|digital) card",
        r"(?:virtual|digital) card.{0,30}(?:get|create|make|generate|obtain|order)",
    ],
    "lost_or_stolen_card": [
        r"(?:lost|stolen|misplaced|missing|robbed|theft).{0,25}(?:card|wallet)",
        r"(?:card|wallet).{0,30}(?:lost|stolen|misplaced|missing|taken|theft)",
    ],
    "lost_or_stolen_phone": [
        r"(?:lost|stolen|misplaced|missing|robbed|theft).{0,25}(?:phone|mobile|iphone|handset)",
        r"(?:phone|mobile|iphone|handset).{0,25}(?:lost|stolen|misplaced|missing|taken)",
    ],
    "order_physical_card": [
        r"(?:order|request|apply for).{0,25}(?:physical|plastic|new|real) card",
        r"(?:physical|plastic|new) card.{0,25}(?:order|request|apply for)",
    ],
    "passcode_forgotten": [
        r"(?:forgot|forgotten|lost|dont remember|cant remember).{0,25}(?:passcode|password|login code|app code)",
        r"(?:passcode|password|login code|app code).{0,25}(?:forgot|forgotten|reset|lost)",
        r"(?:locked out|cant log in|cannot log in).{0,30}(?:app|account|passcode)",
    ],
    "pending_card_payment": [
        r"(?:card payment|card transaction|purchase).{0,40}(?:pending|processing|on hold|still waiting)",
        r"(?:pending|processing|on hold).{0,40}(?:card payment|card transaction|purchase)",
    ],
    "pending_cash_withdrawal": [
        r"(?:atm|cash withdrawal).{0,40}(?:pending|processing|on hold|still waiting)",
        r"(?:pending|processing|on hold).{0,40}(?:atm|cash withdrawal)",
    ],
    "pending_top_up": [
        r"(?:top up|recharge).{0,40}(?:pending|processing|on hold|still waiting)",
        r"(?:pending|processing|on hold).{0,40}(?:top up|recharge)",
    ],
    "pending_transfer": [
        r"(?:transfer|wire|bank payment).{0,40}(?:pending|processing|on hold|still waiting)",
        r"(?:pending|processing|on hold).{0,40}(?:transfer|wire|bank payment)",
    ],
    "pin_blocked": [
        r"(?:pin|pin number).{0,30}(?:block|lock|too many attempts|incorrect too many times)",
        r"(?:block|lock).{0,25}(?:pin|pin number)",
        r"(?:entered|typed).{0,25}(?:wrong|incorrect) pin.{0,30}(?:times|attempts|block)",
    ],
    "receiving_money": [
        r"(?:receive|get|accept).{0,25}(?:money|funds|payments).{0,25}(?:someone|friend|another user|people)?",
        r"(?:someone|friend|another person).{0,25}(?:send|pay|transfer).{0,20}(?:me|money to me)",
    ],
    "refund_not_showing_up": [
        r"(?:refund|reimbursement).{0,45}(?:not showing|not received|not arrived|missing|where|waiting|hasnt|has not)",
        r"(?:not showing|not received|not arrived|missing|where).{0,35}(?:refund|reimbursement)",
    ],
    "request_refund": [
        r"(?:request|ask for|get|claim|apply for).{0,25}(?:a |my )?refund",
        r"(?:refund).{0,25}(?:request|ask|claim|how do i get)",
        r"(?:merchant|seller|shop).{0,30}(?:refund|return my money)",
    ],
    "reverted_card_payment": [
        r"(?:card payment|card transaction|purchase).{0,35}(?:revert|revers|returned|cancelled by merchant)",
        r"(?:revert|revers).{0,35}(?:card payment|card transaction|purchase)",
    ],
    "supported_cards_and_currencies": [
        r"(?:which|what|supported).{0,40}(?:cards? and currenc|cards? (?:or|and) currenc)",
        r"(?:which|what).{0,35}(?:cards?|currenc).{0,35}(?:top up|add money)",
        r"(?:top up|add money).{0,45}(?:supported cards?|which currenc|card types?|card networks?)",
    ],
    "terminate_account": [
        r"(?:close|delete|terminate|deactivate|cancel|shut down).{0,25}(?:my |the )?account",
        r"(?:account).{0,25}(?:close|delete|terminate|deactivate|cancel|shut down)",
    ],
    "top_up_by_bank_transfer_charge": [
        r"(?:top up|fund|add money).{0,35}(?:bank transfer|wire).{0,35}(?:fee|charge|cost)",
        r"(?:bank transfer|wire).{0,35}(?:top up|fund|add money).{0,35}(?:fee|charge|cost)",
        r"(?:fee|charge|cost).{0,40}(?:bank transfer|wire).{0,35}(?:top up|add money)",
    ],
    "top_up_by_card_charge": [
        r"(?:top up|recharge|add money).{0,35}(?:debit card|credit card|bank card|by card).{0,35}(?:fee|charge|cost)",
        r"(?:fee|charge|cost).{0,40}(?:card top up|top up by card|topping up by card)",
    ],
    "top_up_by_cash_or_cheque": [
        r"(?:top up|add money|fund|deposit).{0,35}(?:cash|cheque|check)",
        r"(?:cash|cheque|check).{0,35}(?:top up|add money|fund|deposit)",
    ],
    "top_up_failed": [
        r"(?:top up|recharge|add money).{0,35}(?:fail|declin|reject|unsuccessful|error|wont work)",
        r"(?:fail|declin|reject|unsuccessful|error).{0,35}(?:top up|recharge)",
    ],
    "top_up_limits": [
        r"(?:top up|recharge|add money).{0,35}(?:limit|maximum|minimum|cap|how much|how many)",
        r"(?:limit|maximum|minimum|cap).{0,35}(?:top up|recharge|add money)",
    ],
    "top_up_reverted": [
        r"(?:top up|recharge).{0,35}(?:revert|revers|returned|refunded|bounc|taken back)",
        r"(?:revert|revers|returned|bounc).{0,35}(?:top up|recharge)",
    ],
    "topping_up_by_card": [
        r"(?:top up|recharge|add money|fund).{0,35}(?:debit card|credit card|bank card|another card|by card|with a card)",
        r"(?:debit card|credit card|bank card).{0,35}(?:top up|recharge|add money|fund)",
    ],
    "transaction_charged_twice": [
        r"(?:charg|debit|bill|pay).{0,35}(?:twice|two times|double|multiple times)",
        r"(?:same|one) (?:transaction|payment|purchase).{0,35}(?:twice|two times|double|duplicate)",
        r"(?:duplicate|double).{0,25}(?:charge|transaction|payment|debit)",
    ],
    "transfer_fee_charged": [
        r"(?:transfer|wire|send money|sending money).{0,35}(?:fee|charge|commission|cost)",
        r"(?:fee|charge|commission|cost).{0,35}(?:transfer|wire|send money|sending money)",
    ],
    "transfer_into_account": [
        r"(?:transfer|wire|send|deposit).{0,40}(?:into|to) (?:my |the )?(?:account|bank account)",
        r"(?:bank details|iban|account details).{0,35}(?:receive|incoming|transfer|deposit)",
        r"(?:incoming|inbound).{0,20}(?:bank )?transfer",
    ],
    "transfer_not_received_by_recipient": [
        r"(?:recipient|beneficiar|payee|friend|other person).{0,40}(?:not received|hasnt received|has not received|didnt receive|no money|still waiting)",
        r"(?:transfer|money i sent|sent money).{0,45}(?:not received|hasnt received|has not received|didnt receive|not arrived).{0,35}(?:recipient|beneficiar|payee|friend|them|their account)?",
    ],
    "transfer_timing": [
        r"(?:how long|when|time|days|weeks|speed).{0,35}(?:transfer|wire|send money)",
        r"(?:transfer|wire|send money).{0,35}(?:how long|when|time|days|weeks|speed|arrive)",
    ],
    "unable_to_verify_identity": [
        r"(?:cannot|cant|unable|fail|failed|problem|error|reject).{0,40}(?:verif|identity|id document)",
        r"(?:verif|identity|id document).{0,40}(?:cannot|cant|unable|fail|failed|problem|error|reject)",
    ],
    "verify_my_identity": [
        r"(?:how|need|want|trying).{0,25}(?:verif|prove|confirm).{0,20}(?:my )?(?:identity|id|myself)",
        r"(?:identity|id).{0,25}(?:verification|verify|document|passport|selfie)",
        r"(?:submit|upload).{0,25}(?:passport|identity document|id card|selfie)",
    ],
    "verify_source_of_funds": [
        r"(?:verif|prove|confirm|document|evidence).{0,35}(?:source|origin).{0,20}(?:funds|money|income)",
        r"(?:source|origin).{0,20}(?:funds|money|income).{0,35}(?:verif|prove|confirm|document|evidence)",
        r"(?:proof|evidence).{0,25}(?:income|where my money|where the money)",
    ],
    "verify_top_up": [
        r"(?:verif|confirm|authenticat).{0,30}(?:top up|recharge|funding card)",
        r"(?:top up|recharge).{0,30}(?:verif|confirm|authenticat)",
        r"(?:small|test) (?:charge|payment|deposit).{0,35}(?:top up|card verification)",
    ],
    "virtual_card_not_working": [
        r"(?:virtual|digital) card.{0,35}(?:not working|doesnt work|does not work|fail|declin|broken|unable)",
        r"(?:not working|doesnt work|does not work|fail|declin|broken).{0,35}(?:virtual|digital) card",
    ],
    "visa_or_mastercard": [
        r"\bvisa\b|\bmastercard\b|\bmaster card\b",
        r"(?:card network|card scheme).{0,25}(?:card|use|which)",
    ],
    "why_verify_identity": [
        r"(?:why|reason|purpose).{0,35}(?:verif|prove|confirm).{0,20}(?:identity|id|myself)",
        r"(?:why|reason|purpose).{0,35}(?:identity verification|passport|id document)",
    ],
    "wrong_amount_of_cash_received": [
        r"(?:atm|cash machine|withdraw).{0,50}(?:wrong amount|not enough|less cash|too little|only gave|didnt dispense|did not dispense)",
        r"(?:wrong amount|not enough|less cash|too little|only gave).{0,45}(?:atm|cash machine|withdraw|cash)",
        r"(?:atm|cash machine).{0,35}(?:dispensed|gave).{0,20}(?:less|wrong|only)",
    ],
    "wrong_exchange_rate_for_cash_withdrawal": [
        r"(?:atm|cash withdrawal|withdraw).{0,50}(?:exchange rate|conversion rate|wrong rate|fx rate)",
        r"(?:exchange rate|conversion rate|wrong rate|fx rate).{0,45}(?:atm|cash withdrawal|withdraw)",
    ],
}

# Short hints supplement the relational expressions when a customer writes
# only a terse topic rather than a complete sentence.
HINTS = {
    "activate_my_card": "card activation enable new card",
    "age_limit": "minimum age old enough eligible minor",
    "apple_pay_or_google_pay": "mobile wallet phone payment apple google",
    "atm_support": "supported atm cash machine network",
    "automatic_top_up": "auto recurring scheduled top up",
    "balance_not_updated_after_bank_transfer": "incoming bank transfer missing balance",
    "balance_not_updated_after_cheque_or_cash_deposit": "cash cheque deposit missing balance",
    "beneficiary_not_allowed": "beneficiary recipient payee prohibited",
    "cancel_transfer": "cancel undo recall transfer",
    "card_about_to_expire": "expiring expired card renewal",
    "card_acceptance": "where card accepted merchant shops abroad",
    "card_arrival": "card not arrived delivery late tracking",
    "card_delivery_estimate": "card delivery estimate shipping how long",
    "card_linking": "link connect card account app",
    "card_not_working": "card broken unusable not working",
    "card_payment_fee_charged": "card purchase payment fee surcharge",
    "card_payment_not_recognised": "unauthorized unfamiliar card purchase",
    "card_payment_wrong_exchange_rate": "wrong conversion exchange rate card purchase",
    "card_swallowed": "atm swallowed retained card",
    "cash_withdrawal_charge": "atm withdrawal fee charge",
    "cash_withdrawal_not_recognised": "unauthorized atm cash withdrawal",
    "change_pin": "change reset card pin",
    "compromised_card": "card details leaked cloned skimmed",
    "contactless_not_working": "tap contactless nfc failing",
    "country_support": "supported countries account available residence",
    "declined_card_payment": "card payment declined rejected",
    "declined_cash_withdrawal": "atm withdrawal declined rejected",
    "declined_transfer": "bank transfer declined rejected",
    "direct_debit_payment_not_recognised": "unfamiliar unauthorized direct debit",
    "disposable_card_limits": "disposable single use card limit",
    "edit_personal_details": "edit name address phone email personal details",
    "exchange_charge": "currency exchange conversion fee",
    "exchange_rate": "currency conversion exchange rate",
    "exchange_via_app": "exchange convert currencies inside app",
    "extra_charge_on_statement": "additional unexpected charge statement",
    "failed_transfer": "transfer failed error",
    "fiat_currency_support": "supported fiat currencies hold account",
    "get_disposable_virtual_card": "create disposable virtual card",
    "get_physical_card": "get physical plastic card",
    "getting_spare_card": "additional spare second card",
    "getting_virtual_card": "create digital virtual card",
    "lost_or_stolen_card": "lost stolen missing card",
    "lost_or_stolen_phone": "lost stolen missing phone",
    "order_physical_card": "order physical plastic card",
    "passcode_forgotten": "forgot app password passcode",
    "pending_card_payment": "pending card payment transaction",
    "pending_cash_withdrawal": "pending atm cash withdrawal",
    "pending_top_up": "pending top up",
    "pending_transfer": "pending bank transfer",
    "pin_blocked": "blocked locked card pin",
    "receiving_money": "receive money from someone",
    "refund_not_showing_up": "refund missing not received",
    "request_refund": "request claim refund",
    "reverted_card_payment": "reversed reverted card purchase",
    "supported_cards_and_currencies": "cards currencies supported top up",
    "terminate_account": "close delete account",
    "top_up_by_bank_transfer_charge": "bank transfer top up fee",
    "top_up_by_card_charge": "debit credit card top up fee",
    "top_up_by_cash_or_cheque": "cash cheque top up deposit",
    "top_up_failed": "top up declined failed",
    "top_up_limits": "top up maximum limit",
    "top_up_reverted": "top up reversed reverted",
    "topping_up_by_card": "top up using debit credit card",
    "transaction_charged_twice": "duplicate double charge paid twice",
    "transfer_fee_charged": "outgoing transfer fee charged",
    "transfer_into_account": "incoming bank transfer into account",
    "transfer_not_received_by_recipient": "recipient not received sent transfer",
    "transfer_timing": "transfer how long arrival time",
    "unable_to_verify_identity": "identity verification failed rejected",
    "verify_my_identity": "verify identity passport document selfie",
    "verify_source_of_funds": "prove source of funds income",
    "verify_top_up": "verify confirm top up",
    "virtual_card_not_working": "virtual card failed not working",
    "visa_or_mastercard": "visa mastercard card network",
    "why_verify_identity": "why need identity verification",
    "wrong_amount_of_cash_received": "atm dispensed wrong amount cash",
    "wrong_exchange_rate_for_cash_withdrawal": "atm withdrawal wrong exchange rate",
}


def _extract_text(state):
    if isinstance(state, str):
        return state
    if isinstance(state, dict):
        for key in (
            "text", "message", "utterance", "query", "user_input",
            "customer_message", "customer_text", "input", "content",
        ):
            if key in state:
                value = _extract_text(state[key])
                if value:
                    return value
        if "messages" in state:
            return _extract_text(state["messages"])
        if "state" in state:
            return _extract_text(state["state"])
        parts = []
        for key, value in state.items():
            if key not in (
                "role", "id", "label", "answer", "intent", "category",
                "timestamp", "metadata",
            ):
                part = _extract_text(value)
                if part:
                    parts.append(part)
        return " ".join(parts)
    if isinstance(state, (list, tuple)):
        user_messages = [
            item for item in state
            if isinstance(item, dict) and item.get("role") == "user"
        ]
        if user_messages:
            return _extract_text(user_messages[-1])
        return " ".join(
            part for item in state
            if (part := _extract_text(item))
        )
    return ""


def _normalize(text):
    text = unicodedata.normalize("NFKD", text).lower()
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.replace("top-up", "top up").replace("topup", "top up")
    text = text.replace("cash-out", "cash withdrawal")
    text = text.replace("master card", "mastercard")
    text = re.sub(r"['\u2018\u2019]", "", text)
    text = text.replace("_", " ")
    return " ".join(re.findall(r"[a-z0-9]+", text))


def _has(s, expression):
    return re.search(expression, s) is not None


def _clear_intent(s):
    h = lambda pattern: _has(s, pattern)
    card = h(r"\bcard\b|\bplastic\b")
    phone = h(r"\bphone\b|\bmobile\b|\biphone\b|\bhandset\b")
    atm = h(r"\batm\b|\bwithdraw\w*\b|\bcash machine\b|\bcashpoint\b|\bcash dispenser\b|\btook out cash\b")
    top = h(r"\btop up\b|\brecharge\b|\badd (?:money|funds|cash)\b|\bload (?:money|funds)\b|\bfund (?:my |the )?account\b")
    transfer = h(r"\btransfer\w*\b|\bwire\b|\biban\b|\bswift\b|\bbeneficiar\w*\b|\brecipient\b|\bpayee\b|\bsend money\b|\bsent money\b")
    card_payment = h(r"\bcard payment\b|\bcard transaction\b|\bcard purchase\b|\bpaid (?:with|by|using) (?:my |the |a )?card\b|\bpay(?:ing)? (?:with|by|using) (?:my |the |a )?card\b")
    debit = h(r"\bdirect debit\b|\bautopay\b|\bautomatic debit\b")
    virtual = h(r"\bvirtual\b|\bdigital card\b")
    disposable = h(r"\bdisposable\b|\bsingle use\b|\bone time (?:use |virtual )?card\b")
    missing = h(r"\bnot (?:received|arrived|showing|credited|appearing)\b|\bhasnt (?:arrived|come|shown|been credited|received)\b|\bdidnt (?:arrive|show|receive)\b|\bmissing\b|\bstill waiting\b|\bwhere is\b|\bwhere has\b")
    pending = h(r"\bpending\b|\bprocessing\b|\bin progress\b|\bon hold\b|\bstuck\b")
    decline = h(r"\bdeclin\w*\b|\breject\w*\b|\bdenied\b|\brefus\w*\b")
    failure = h(r"\bfail\w*\b|\berror\b|\bunsuccessful\b|\bnot going through\b|\bwont go through\b|\bdidnt go through\b")
    fee = h(r"\bfees?\b|\bcommission\b|\bsurcharge\b|\bextra charge\b|\bcharged (?:me |for |a fee)\b|\bcharges? for\b|\bcost of\b")
    rate = h(r"\bexchange rate\b|\bconversion rate\b|\bfx rate\b|\bcurrency rate\b|\bwrong rate\b|\bbad rate\b")
    unknown = h(r"\b(?:dont|do not|didnt|did not) recogni[sz]e\b|\bunrecogni[sz]ed\b|\bunfamiliar\b|\bunauthori[sz]ed\b|\bnot mine\b|\bnever (?:made|authori[sz]ed|did)\b|\bunknown (?:payment|transaction|charge|withdrawal|debit)\b")
    reversal = h(r"\brevert\w*\b|\brevers\w*\b|\bbounc\w*\b")
    recipient = h(r"\brecipient\b|\bbeneficiar\w*\b|\bpayee\b|\btheir account\b|\bfriend\b|\bthem\b|\bperson i sent\b")
    account_in = h(r"\bmy (?:bank )?account\b|\binto (?:the |my )?account\b|\bmy balance\b|\bbalance\b")
    time_question = h(r"\bhow long\b|\bwhen (?:will|does|should|can)\b|\bestimat\w*\b|\bdelivery time\b|\bshipping time\b|\bdays?\b|\bweeks?\b")
    limit = h(r"\blimits?\b|\bmaximum\b|\bminimum\b|\bhow many\b|\bhow much (?:can|am i allowed|money)\b|\bcap\b")

    if h(r"\bapple pay\b|\bgoogle pay\b|\bgoogle wallet\b|\bapple wallet\b"):
        return "apple_pay_or_google_pay"
    if h(r"\b(?:close|delete|terminate|shut down|deactivate) (?:my |the )?account\b"):
        return "terminate_account"
    if h(r"\b(?:minimum age|age limit|age requirement|underage|under 18)\b"):
        return "age_limit"
    if h(r"\b(?:lost|stolen|misplaced|missing)\b") and phone:
        return "lost_or_stolen_phone"
    if h(r"\b(?:lost|stolen|misplaced)\b") and card:
        return "lost_or_stolen_card"
    if card and h(r"\b(?:swallow\w*|retain\w*|captur\w*|seiz\w*)\b") and atm:
        return "card_swallowed"
    if card and h(r"\bexpir\w*\b|\bexpiry\b|\bexpiration\b"):
        return "card_about_to_expire"
    if card and h(r"\bcompromis\w*\b|\bclon\w*\b|\bskim\w*\b|\bleak\w*\b|\bcard details (?:stolen|exposed)\b"):
        return "compromised_card"
    if h(r"\b(?:source|origin) of (?:my |the )?(?:funds|money|income)\b"):
        return "verify_source_of_funds"
    if h(r"\b(?:pin|pin number)\b"):
        if h(r"\bblock\w*\b|\block\w*\b|\btoo many (?:attempts|tries)\b"):
            return "pin_blocked"
        if h(r"\b(?:change|reset|update|modify|forgot|forgotten|retrieve|find) (?:my |the )?(?:card )?pin\b|\bpin.{0,20}(?:change|reset|forgot)\b"):
            return "change_pin"
    if h(r"\b(?:forgot|forgotten|reset|lost) (?:my |the )?(?:passcode|password|login code|app code)\b"):
        return "passcode_forgotten"
    if h(r"\b(?:why|reason|purpose)\b") and h(r"\bverif\w*\b|\bidentity\b") and h(r"\bidentity\b|\bid\b|\bpassport\b"):
        return "why_verify_identity"
    if h(r"\bverif\w*\b|\bidentity\b|\bid document\b") and h(r"\b(?:unable|cannot|cant|failed|failing|rejected|error|problem)\b"):
        return "unable_to_verify_identity"
    if h(r"\b(?:verify|verification|prove|confirm) (?:my |the )?(?:identity|id|myself)\b|\bidentity verification\b|\bsubmit (?:my |an? )?(?:passport|id document|selfie)\b"):
        return "verify_my_identity"
    if h(r"\b(?:change|edit|update|correct) (?:my |the )?(?:name|address|email|phone number|personal details|personal information|date of birth)\b"):
        return "edit_personal_details"

    if debit and unknown:
        return "direct_debit_payment_not_recognised"
    if h(r"\b(?:charged|debited|billed|paid) (?:me |for |my card )?(?:twice|two times|double)\b|\b(?:duplicate|double) (?:charge|transaction|payment|debit)\b"):
        return "transaction_charged_twice"
    if h(r"\brefund\b|\breimbursement\b"):
        if missing or h(r"\b(?:not|never) (?:got|received|seen)\b|\bwhere\b|\bwaiting\b|\bhasnt\b"):
            return "refund_not_showing_up"
        if h(r"\b(?:request|ask|claim|get|want|need|apply|how)\b"):
            return "request_refund"

    if atm:
        if h(r"\b(?:swallow\w*|retain\w*)\b") and card:
            return "card_swallowed"
        if h(r"\bwrong amount\b|\bnot enough (?:cash|money)\b|\bless (?:cash|money)\b|\bonly (?:gave|dispensed|received)\b|\bdidnt dispense\b|\bdid not dispense\b"):
            return "wrong_amount_of_cash_received"
        if rate:
            return "wrong_exchange_rate_for_cash_withdrawal"
        if unknown:
            return "cash_withdrawal_not_recognised"
        if pending:
            return "pending_cash_withdrawal"
        if decline or (failure and h(r"\b(?:withdraw|dispense|cash)\b")):
            return "declined_cash_withdrawal"
        if fee:
            return "cash_withdrawal_charge"

    if disposable and card:
        if limit:
            return "disposable_card_limits"
        if h(r"\b(?:get|create|make|generate|obtain|order|new|need|want)\b"):
            return "get_disposable_virtual_card"
    if virtual and card:
        if h(r"\bnot working\b|\bdoesnt work\b|\bdoes not work\b|\bfail\w*\b|\bdeclin\w*\b|\bproblem\b|\bunable\b|\bcant use\b"):
            return "virtual_card_not_working"
        if h(r"\b(?:get|create|make|generate|obtain|order|new|need|want)\b"):
            return "getting_virtual_card"
    if h(r"\bcontactless\b|\btap to pay\b|\bnfc\b"):
        if h(r"\b(?:not working|doesnt work|does not work|failed|declined|unable|cant|cannot|stopped)\b"):
            return "contactless_not_working"
    if card and h(r"\b(?:activate|activation|activating)\b"):
        return "activate_my_card"
    if card and h(r"\b(?:link|connect|pair|register)\b") and h(r"\b(?:app|account|card)\b"):
        return "card_linking"

    if h(r"\b(?:cash|cheque|check) deposit\b|\bdeposited (?:cash|a cheque|a check)\b"):
        if missing or h(r"\b(?:balance|not credited)\b"):
            return "balance_not_updated_after_cheque_or_cash_deposit"
        if top or h(r"\b(?:can i|how|possible)\b"):
            return "top_up_by_cash_or_cheque"

    if top:
        if h(r"\b(?:automatically|automatic|automated|auto|recurring|scheduled)\b"):
            return "automatic_top_up"
        if h(r"\b(?:verify|verification|confirm|authenticate)\b"):
            return "verify_top_up"
        if pending:
            return "pending_top_up"
        if reversal or h(r"\breturned (?:to|back)\b|\btaken back\b"):
            return "top_up_reverted"
        if limit:
            return "top_up_limits"
        if failure or decline:
            return "top_up_failed"
        if fee:
            if h(r"\bbank transfer\b|\bwire\b"):
                return "top_up_by_bank_transfer_charge"
            if card or h(r"\bdebit\b|\bcredit\b"):
                return "top_up_by_card_charge"
        if h(r"\b(?:cash|cheque|check)\b"):
            return "top_up_by_cash_or_cheque"
        if h(r"\b(?:supported|which|what) (?:debit |credit )?cards?\b|\bwhich currenc\w*\b|\bcard types?\b"):
            return "supported_cards_and_currencies"
        if h(r"\b(?:debit card|credit card|bank card|by card|with (?:a |my )?card)\b"):
            return "topping_up_by_card"

    if transfer:
        if h(r"\b(?:cancel|stop|recall|undo) (?:my |the |a )?(?:transfer|wire|payment)\b|\b(?:transfer|wire).{0,25}(?:cancel|recall|undo)\b"):
            return "cancel_transfer"
        if recipient and h(r"\b(?:not allowed|not permitted|not eligible|not supported|cant|cannot|unable|invalid|blocked)\b"):
            return "beneficiary_not_allowed"
        if pending:
            return "pending_transfer"
        if missing and recipient:
            return "transfer_not_received_by_recipient"
        if missing and account_in and h(r"\bbank transfer\b|\bwire\b|\btransfer(?:red)? (?:to|into) (?:my |the )?account\b|\bincoming\b"):
            return "balance_not_updated_after_bank_transfer"
        if decline:
            return "declined_transfer"
        if failure:
            return "failed_transfer"
        if fee and not top:
            return "transfer_fee_charged"
        if time_question and not top:
            return "transfer_timing"
        if h(r"\b(?:into|to) (?:my |the )?(?:bank )?account\b|\bincoming\b|\binbound\b|\biban\b|\bbank details\b"):
            return "transfer_into_account"

    if card_payment or (card and h(r"\b(?:purchase|payment|transaction|checkout|paid|paying)\b")):
        if unknown:
            return "card_payment_not_recognised"
        if pending:
            return "pending_card_payment"
        if reversal:
            return "reverted_card_payment"
        if rate:
            return "card_payment_wrong_exchange_rate"
        if decline:
            return "declined_card_payment"
        if fee:
            return "card_payment_fee_charged"

    if card and h(r"\b(?:not working|doesnt work|does not work|stopped working|broken|damaged|unusable)\b"):
        return "card_not_working"
    if card and h(r"\b(?:not arrived|hasnt arrived|never arrived|not delivered|where is my card|lost in the mail)\b"):
        return "card_arrival"
    if card and time_question and h(r"\b(?:arriv|deliver|ship|receiv|come)\w*\b"):
        return "card_delivery_estimate"
    if card and h(r"\b(?:spare|second|another|extra|additional|backup)\b"):
        return "getting_spare_card"
    if card and h(r"\b(?:order|request|apply for)\b") and h(r"\b(?:physical|plastic|new)\b"):
        return "order_physical_card"
    if card and h(r"\b(?:physical|plastic|real)\b") and h(r"\b(?:get|obtain|receive|want|need)\b"):
        return "get_physical_card"
    if h(r"\b(?:visa|mastercard)\b") and h(r"\b(?:card|which|whether|do you|is it|issue)\b"):
        return "visa_or_mastercard"
    if h(r"\b(?:countries|country)\b") and h(r"\b(?:supported|available|eligible|sign up|open an account|live|resident)\b"):
        return "country_support"
    if h(r"\b(?:exchange|convert|conversion|foreign currency)\b"):
        if fee:
            return "exchange_charge"
        if rate:
            return "exchange_rate"
        if h(r"\b(?:app|exchange|convert|swap|buy|sell)\b"):
            return "exchange_via_app"
    if h(r"\b(?:receive|get) money\b|\bsend me money\b"):
        return "receiving_money"
    if h(r"\b(?:extra|additional|unexpected|mysterious) (?:charge|debit|transaction)\b"):
        return "extra_charge_on_statement"
    return None


def _scored_intent(s):
    scores = Counter()
    for category, patterns in PATTERNS.items():
        for pattern in patterns:
            if _has(s, pattern):
                scores[category] += 9
        phrase = category.replace("_", " ")
        if phrase in s:
            scores[category] += 24

    words = set(s.split())
    common = {
        "my", "the", "a", "an", "to", "of", "and", "by", "for", "or",
        "get", "card", "payment", "money", "account", "how", "can",
        "is", "not", "with", "after", "up", "on", "in",
    }
    for category in CATEGORIES:
        hint_words = set(HINTS[category].split()) - common
        matches = words & hint_words
        scores[category] += len(matches) * 1.6
        if hint_words and len(matches) >= 2:
            scores[category] += 2
    if not scores:
        return "card_not_working"
    return max(CATEGORIES, key=lambda category: scores[category])


def predict(state) -> dict:
    text = _extract_text(state)
    s = _normalize(text)
    if s in {category.replace("_", " ") for category in CATEGORIES}:
        for category in CATEGORIES:
            if s == category.replace("_", " "):
                return {"answer": category}
    answer = _clear_intent(s)
    if answer is None:
        answer = _scored_intent(s)
    return {"answer": answer}