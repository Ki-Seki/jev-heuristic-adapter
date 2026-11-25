import re
import unicodedata


def _normalise(value):
    if not isinstance(value, str):
        if isinstance(value, dict):
            for key in ("text", "message", "state", "query", "utterance"):
                if isinstance(value.get(key), str):
                    value = value[key]
                    break
            else:
                value = ""
        else:
            value = ""
    value = unicodedata.normalize("NFKD", value).casefold()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def _has(text, pattern):
    return re.search(pattern, text) is not None


def _answer(label):
    return {"answer": label}


def predict(state) -> dict:
    t = _normalise(state)

    topup = _has(
        t,
        r"\btop up\b|\btopup\b|\btop ups\b|\btopping up\b|"
        r"\brecharge\b|\badd (?:money|funds|cash)\b|"
        r"\bload (?:money|funds|my card|the card)\b|"
        r"\bfund (?:my|the) account\b",
    )
    transfer = _has(
        t,
        r"\btransfer\b|\bwire\b|\bremittance\b|\bbeneficiar|\brecipient\b|"
        r"\bpayee\b|\biban\b|\bsort code\b|\bswift\b|"
        r"\b(?:send|sent|sending|receive|received|receiving) money\b|"
        r"\bincoming (?:payment|transaction|money|funds)\b|"
        r"\boutgoing (?:payment|transaction|money|funds)\b|"
        r"\bbank account\b|\bbank deposit\b",
    )
    atm = _has(
        t,
        r"\batm\b|\bcash machine\b|\bcashpoint\b|\bcash dispenser\b|"
        r"\bwithdraw|\bwithdrawal\b|\btake (?:out )?cash\b|"
        r"\btake (?:out )?money (?:from|at|out)\b",
    )
    cash_deposit = _has(
        t,
        r"\b(?:cash|cheque|check) deposit\b|\bdeposit (?:cash|a cheque|a check)\b|"
        r"\bpay (?:in|into) (?:cash|a cheque|a check)\b|"
        r"\b(?:cheque|check) (?:payment|paid in)\b",
    )
    card = _has(
        t,
        r"\bcard\b|\bcards\b|\bdebit\b|\bcredit card\b|\bplastic\b|"
        r"\bcontactless\b|\bvisa\b|\bmastercard\b|\bvirtual\b",
    )
    payment = _has(
        t,
        r"\bpayment\b|\bpurchase\b|\btransaction\b|\bmerchant\b|"
        r"\bshop\b|\bstore\b|\b(?:buy|bought|pay|paid|spend|spent) (?:for|with|at|in|online)\b",
    )
    pending = _has(
        t,
        r"\bpending\b|\bprocessing\b|\bin progress\b|\bon hold\b|"
        r"\bwaiting (?:to|for|on|since)\b|\bnot (?:yet )?(?:cleared|completed|processed)\b|"
        r"\bhasn t (?:cleared|completed|processed)\b|\bstill (?:waiting|processing)\b",
    )
    missing = _has(
        t,
        r"\bnot (?:showing|appearing|reflected|credited|received|arrived)\b|"
        r"\b(?:hasn t|haven t|didn t|never) (?:shown|appeared|arrived|received|come through|been credited)\b|"
        r"\bmissing\b|\bno sign of\b|\bnot in my (?:account|balance)\b|"
        r"\bbalance (?:hasn t|isn t|not) (?:updated|changed)\b|"
        r"\bstill (?:not here|not received|not showing|waiting for)\b|"
        r"\bdon t see (?:the|my|it)\b",
    )
    declined = _has(t, r"\bdeclin|\bdenied\b|\brejected\b|\brefused\b")
    failed = _has(
        t,
        r"\bfail|\bunsuccessful\b|\bnot (?:working|work|going through|gone through)\b|"
        r"\b(?:doesn t|didn t|won t) (?:work|go through|let me)\b|"
        r"\b(?:can t|cannot|unable to) (?:make|complete|do|use|send|pay|top up|withdraw|transfer)\b|"
        r"\berror\b",
    )
    unknown = _has(
        t,
        r"\b(?:don t|do not|didn t|did not|cannot|can t) recognis|\bunrecognis|"
        r"\b(?:don t|do not|didn t|did not) know (?:this|what|where|who)\b|"
        r"\bnot (?:mine|my transaction|my payment|my purchase)\b|"
        r"\b(?:never|didn t|did not) (?:make|authorise|authorize|do|withdraw|pay for|buy)\b|"
        r"\bunauthori[sz]|\bfraudulent\b|\bwasn t me\b|\bsomeone else (?:used|made|withdrew)\b",
    )
    fee = _has(
        t,
        r"\bfee\b|\bfees\b|\bcharged\b|\bcharge\b|\bcharges\b|"
        r"\bsurcharge\b|\bcommission\b|\bcost\b|\bextra (?:amount|money)\b",
    )
    rate = _has(
        t,
        r"\bexchange rate\b|\bconversion rate\b|\bcurrency rate\b|"
        r"\bwrong rate\b|\brate (?:used|applied|given)\b",
    )
    limit = _has(
        t,
        r"\blimit\b|\blimits\b|\bmaximum\b|\bminimum\b|\bmax\b|"
        r"\bhow (?:many|much|often)\b|\bcap\b|\bthreshold\b",
    )
    already_sent = _has(
        t,
        r"\b(?:already|just|recently) (?:sent|made|transferred|paid)\b|"
        r"\b(?:sent|made|transferred|paid) (?:a|the|my|some|money|funds|it)\b|"
        r"\btransfer (?:was|is|says|shows) (?:complete|completed|successful|sent)\b",
    )

    if _has(t, r"\b(?:lost|stolen|missing|misplaced) (?:my |the |a )?(?:phone|mobile|cellphone|smartphone)\b|\bphone (?:was|has been|got) stolen\b"):
        return _answer("lost_or_stolen_phone")
    if _has(t, r"\b(?:close|delete|terminate|cancel|shut down) (?:my |the )?(?:account|membership)\b|\bstop using (?:my |the )?account\b"):
        return _answer("terminate_account")
    if _has(t, r"\b(?:change|update|edit|correct) (?:my |the )?(?:personal |profile |account )?(?:details|information|name|address|phone number|email|date of birth)\b"):
        return _answer("edit_personal_details")
    if _has(t, r"\b(?:age limit|minimum age|age requirement|years old|how old|under 18|underage|minor|teenager)\b"):
        return _answer("age_limit")

    if _has(t, r"\b(?:source|origin|proof) of funds\b|\bwhere (?:my|the) (?:money|funds) (?:came|come) from\b"):
        return _answer("verify_source_of_funds")
    if _has(t, r"\bverif|\bidentity\b|\bid document\b|\bpassport\b|\bselfie\b|\bproof of identity\b"):
        if topup and _has(t, r"\bverif|\bauthenticat|\bconfirm\b|\bsecurity code\b"):
            return _answer("verify_top_up")
        if _has(t, r"\bwhy\b|\bwhat (?:is|s) the (?:reason|point)\b|\bdo i (?:need|have) to\b|\bnecessary\b|\basked (?:me|to) (?:for|verify)\b"):
            return _answer("why_verify_identity")
        if _has(t, r"\b(?:can t|cannot|unable to|failed to|trouble|problem|issue|rejected|declined|doesn t work|not working|won t work|unsuccessful)\b"):
            return _answer("unable_to_verify_identity")
        if _has(t, r"\bidentity\b|\bid document\b|\bpassport\b|\bselfie\b|\bverif"):
            return _answer("verify_my_identity")

    if _has(t, r"\b(?:forgot|forgotten|lost|don t remember|can t remember|reset) (?:my |the )?(?:app |login |account )?passcode\b|\bpasscode (?:forgotten|reset|lost)\b"):
        return _answer("passcode_forgotten")
    if _has(t, r"\bpin\b"):
        if _has(t, r"\bblocked\b|\blocked\b|\bfrozen\b|\btoo many\b|\bincorrect\b|\bwrong\b|\btries\b|\battempts\b"):
            return _answer("pin_blocked")
        if _has(t, r"\bchange\b|\breset\b|\bnew\b|\bforgot\b|\bforgotten\b|\bwhere\b|\bfind\b|\bview\b|\bget\b"):
            return _answer("change_pin")

    if _has(t, r"\b(?:apple pay|google pay|gpay|google wallet|apple wallet)\b"):
        return _answer("apple_pay_or_google_pay")
    if _has(t, r"\bcontactless\b|\btap to pay\b|\btap (?:my |the )?card\b|\bnfc\b"):
        if failed or declined or _has(t, r"\bstopped\b|\bissue\b|\bproblem\b"):
            return _answer("contactless_not_working")
        return _answer("contactless_not_working")

    if _has(t, r"\b(?:card|bank card) (?:was |has been |got )?(?:swallowed|eaten|retained|captured)\b|\batm (?:swallowed|ate|kept|retained|captured) (?:my |the )?card\b|\bcard stuck in (?:the |an )?atm\b"):
        return _answer("card_swallowed")
    if card and _has(t, r"\b(?:lost|stolen|missing|misplaced) (?:my |the |a )?(?:physical )?card\b|\bcard (?:is|was|got|has been) (?:lost|stolen|missing)\b"):
        return _answer("lost_or_stolen_card")
    if card and _has(t, r"\b(?:compromised|hacked|cloned|skimmed)\b|\bcard (?:details|number|information) (?:were |have been |are )?(?:stolen|leaked|exposed)\b|\bsomeone (?:has|knows|got) my card (?:details|number)\b"):
        return _answer("compromised_card")

    if _has(t, r"\b(?:charged|billed|debited|paid|taken) (?:me )?twice\b|\bdouble (?:charge|charged|payment|billed|debit)\b|\bduplicate (?:charge|payment|transaction)\b|\bsame (?:payment|transaction|purchase|charge) (?:twice|two times)\b"):
        return _answer("transaction_charged_twice")

    if _has(t, r"\bdirect debit\b|\bstanding order\b"):
        if unknown or _has(t, r"\b(?:don t know|unfamiliar|unexpected|not authorised|not authorized)\b"):
            return _answer("direct_debit_payment_not_recognised")

    if _has(t, r"\brefund\b|\brefunded\b|\bmoney back\b|\breimbursement\b"):
        if missing or pending or _has(
            t,
            r"\bwhere (?:is|s) (?:my|the) (?:refund|money)\b|"
            r"\b(?:still|yet|never) (?:got|received|seen)\b|\bwaiting for\b|"
            r"\brefund (?:hasn t|has not|isn t|is not|didn t|did not)\b",
        ):
            return _answer("refund_not_showing_up")
        return _answer("request_refund")

    if _has(t, r"\b(?:reverted|reversed|reversal|undone)\b"):
        if topup or _has(t, r"\bdeposit\b"):
            return _answer("top_up_reverted")
        if transfer and not card:
            return _answer("failed_transfer")
        return _answer("reverted_card_payment")

    if _has(t, r"\b(?:cheque|check) deposit\b|\bdeposit (?:cash|a cheque|a check)\b") and (missing or pending):
        return _answer("balance_not_updated_after_cheque_or_cash_deposit")
    if cash_deposit and not atm:
        if missing or _has(t, r"\bbalance (?:hasn t|has not|is not|isn t|not) updated\b"):
            return _answer("balance_not_updated_after_cheque_or_cash_deposit")
        return _answer("top_up_by_cash_or_cheque")

    if _has(t, r"\bdisposable\b|\bsingle use\b|\bone time (?:use |payment )?card\b"):
        if limit or _has(t, r"\b(?:number|amount|frequency|frequently|restrictions|restricted)\b"):
            return _answer("disposable_card_limits")
        return _answer("get_disposable_virtual_card")

    if _has(t, r"\b(?:card|cards) (?:is |are |will be |about to )?(?:expir|expired)\b|\bexpir(?:y|ation) (?:date|of|on|coming|soon)\b|\bcard (?:about to|soon to) expire\b"):
        return _answer("card_about_to_expire")

    if topup:
        if _has(t, r"\bautomatic\b|\bautomatically\b|\bauto top\b|\brecurring\b|\bscheduled\b|\bwhen (?:my )?balance (?:is|gets) low\b"):
            return _answer("automatic_top_up")
        if limit:
            return _answer("top_up_limits")
        if _has(t, r"\b(?:bank )?transfer\b|\bwire\b|\bbank account\b"):
            if fee:
                return _answer("top_up_by_bank_transfer_charge")
            if missing or (pending and _has(t, r"\bbalance\b|\baccount\b")):
                return _answer("balance_not_updated_after_bank_transfer")
            if declined or failed:
                return _answer("failed_transfer")
            return _answer("transfer_into_account")
        if _has(t, r"\b(?:cash|cheque|check)\b") and not atm:
            if missing:
                return _answer("balance_not_updated_after_cheque_or_cash_deposit")
            return _answer("top_up_by_cash_or_cheque")
        if _has(t, r"\bverif|\bauthenticat|\bsecurity code\b"):
            return _answer("verify_top_up")
        if fee:
            return _answer("top_up_by_card_charge")
        if _has(t, r"\b(?:supported|accepted|eligible|which|what) (?:bank |debit |credit )?cards?\b|\bwhich currenc|\bwhat currenc"):
            return _answer("supported_cards_and_currencies")
        if pending or (missing and not failed):
            return _answer("pending_top_up")
        if declined or failed:
            return _answer("top_up_failed")
        return _answer("topping_up_by_card")

    if atm:
        if unknown:
            return _answer("cash_withdrawal_not_recognised")
        if rate or _has(t, r"\bconversion\b") and _has(t, r"\bwrong\b|\bincorrect\b|\bbad\b|\bnot right\b"):
            return _answer("wrong_exchange_rate_for_cash_withdrawal")
        if _has(
            t,
            r"\bwrong (?:amount|sum)\b|\b(?:less|fewer|more) (?:cash|money) than\b|"
            r"\b(?:machine|atm) (?:gave|dispensed) (?:me )?(?:too little|too much|nothing|no cash|less)\b|"
            r"\b(?:didn t|did not|never) (?:get|receive) (?:the |any |my )?(?:cash|money)\b|"
            r"\b(?:no|not enough) cash (?:came|dispensed|received)\b",
        ):
            return _answer("wrong_amount_of_cash_received")
        if pending:
            return _answer("pending_cash_withdrawal")
        if declined or failed or _has(t, r"\b(?:couldn t|could not|can t|cannot|unable to) (?:withdraw|take out|get cash)\b"):
            return _answer("declined_cash_withdrawal")
        if fee:
            return _answer("cash_withdrawal_charge")
        return _answer("atm_support")

    if transfer:
        if _has(t, r"\bbeneficiar|\bpayee\b|\brecipient (?:not allowed|not accepted|blocked|invalid)\b"):
            if _has(t, r"\b(?:not allowed|not accepted|invalid|blocked|can t add|cannot add|won t let me add|unable to add|not permitted)\b"):
                return _answer("beneficiary_not_allowed")
        if _has(t, r"\b(?:cancel|stop|recall|undo|reverse) (?:a |my |the |this )?(?:bank |money |wire )?transfer\b|\btransfer (?:cancel|stop|recall)\b"):
            return _answer("cancel_transfer")
        if fee:
            return _answer("transfer_fee_charged")
        if declined:
            return _answer("declined_transfer")
        if failed and not missing and not pending:
            return _answer("failed_transfer")
        incoming = _has(
            t,
            r"\bincoming\b|\binbound\b|\binto (?:my |the )?account\b|"
            r"\bto (?:my |the )?(?:account|balance)\b|\bfrom (?:another|my other|a different|an external) bank\b|"
            r"\bsent (?:me|to me)\b|\breceive\b|\breceiving\b|\breceived\b",
        )
        recipient_missing = _has(
            t,
            r"\b(?:recipient|beneficiary|payee|friend|other person|them|they|he|she) "
            r"(?:hasn t|has not|haven t|have not|didn t|did not|never|still hasn t|still has not) "
            r"(?:received|got|seen)\b|"
            r"\b(?:not|never) (?:received|reached|arrived) (?:by|at|to|in) (?:the |my )?"
            r"(?:recipient|beneficiary|payee|other|destination)\b|"
            r"\b(?:sent|transferred) (?:money|funds|it) (?:to|but) .{0,45}\b"
            r"(?:hasn t|has not|didn t|did not|never|not received|not arrived)\b",
        )
        if recipient_missing:
            return _answer("transfer_not_received_by_recipient")
        if incoming and missing:
            return _answer("balance_not_updated_after_bank_transfer")
        if pending or _has(t, r"\boutgoing transaction\b|\boutgoing payment\b"):
            return _answer("pending_transfer")
        if missing and already_sent:
            if incoming:
                return _answer("balance_not_updated_after_bank_transfer")
            return _answer("transfer_not_received_by_recipient")
        if _has(t, r"\bhow long\b|\bhow many (?:days|hours)\b|\bwhen (?:will|does|should)\b|\btime (?:does|will|to|for)\b|\btiming\b|\bspeed\b|\bfast\b"):
            if missing and already_sent:
                return _answer("transfer_not_received_by_recipient")
            return _answer("transfer_timing")
        if _has(t, r"\b(?:receive|receiving|get) money\b|\b(?:someone|people|others|friend|family) (?:send|pay|transfer) (?:me|money to me)\b|\bhow (?:can|do) (?:i|people) (?:receive|get paid)\b"):
            if _has(t, r"\b(?:from|using|via|through) (?:a |my |another )?bank\b|\binto my account from\b"):
                return _answer("transfer_into_account")
            return _answer("receiving_money")
        if incoming:
            return _answer("transfer_into_account")
        if _has(t, r"\bsend\b|\bsending\b|\btransferring\b|\btransfer money\b"):
            return _answer("pending_transfer")
        return _answer("pending_transfer")

    if _has(t, r"\b(?:visa|mastercard)\b"):
        if _has(t, r"\b(?:top up|topup|supported|accept|use to add money)\b"):
            return _answer("supported_cards_and_currencies")
        return _answer("visa_or_mastercard")

    if card:
        if _has(t, r"\b(?:link|linking|unlink|connect|connecting|pair|register) (?:my |a |the )?(?:new |existing )?card\b|\bcard (?:link|connect|pair|register)\b"):
            return _answer("card_linking")
        if _has(t, r"\b(?:activate|activation|activated|deactivate) (?:my |a |the )?card\b|\bcard activation\b"):
            return _answer("activate_my_card")
        if _has(t, r"\b(?:spare|extra|second|additional|backup) (?:physical )?card\b|\banother card\b"):
            return _answer("getting_spare_card")
        if _has(t, r"\bvirtual\b|\bdigital card\b"):
            if failed or declined or _has(t, r"\b(?:problem|issue|broken|stopped working)\b"):
                return _answer("virtual_card_not_working")
            return _answer("getting_virtual_card")

        delivery = _has(
            t,
            r"\barriv|\bdeliver|\bshipping\b|\bshipment\b|\bpostage\b|"
            r"\bshipped\b|\bmail\b|\bposted\b|\bdispatch\b|\btracking\b",
        )
        if delivery:
            if _has(t, r"\b(?:ordered|order(?:ed)? my|applied|requested|shipped|dispatched|still|not yet|hasn t|has not|haven t|have not|where is|where s|track|tracking|lost in)\b"):
                if not _has(t, r"\bhow long (?:does|will|should) (?:a|the|my)? ?card\b") or missing:
                    return _answer("card_arrival")
            if _has(t, r"\bhow long\b|\bwhen\b|\bestimat|\bexpected\b|\btime\b|\bdays\b|\bweeks\b|\bdate\b"):
                return _answer("card_delivery_estimate")
            return _answer("card_arrival")
        if _has(t, r"\b(?:order|ordering|apply for|request) (?:a |my |the )?(?:new |first )?(?:physical )?card\b"):
            return _answer("order_physical_card")
        if _has(t, r"\bphysical card\b|\breal card\b|\bplastic card\b"):
            return _answer("get_physical_card")

        if _has(t, r"\bexchange rate\b|\bconversion rate\b|\bcurrency rate\b|\bwrong rate\b"):
            return _answer("card_payment_wrong_exchange_rate")
        if unknown:
            return _answer("card_payment_not_recognised")
        if _has(t, r"\bstatement\b") and fee:
            return _answer("extra_charge_on_statement")
        if _has(t, r"\bextra (?:charge|fee|amount|payment)\b|\bcharged (?:more|extra) (?:than|for)\b"):
            if payment:
                return _answer("extra_charge_on_statement")
        if pending:
            return _answer("pending_card_payment")
        if declined or _has(t, r"\b(?:payment|purchase) (?:didn t|did not|doesn t|does not|won t|wouldn t|couldn t|could not) go through\b"):
            return _answer("declined_card_payment")
        if fee and payment:
            return _answer("card_payment_fee_charged")
        if _has(t, r"\b(?:where|which|what|countries|shops|stores|places|merchants) .{0,55}\b(?:accept|use|usable|work)\b|\b(?:accepted|acceptance) (?:at|by|in|everywhere|anywhere)\b"):
            return _answer("card_acceptance")
        if failed or _has(t, r"\b(?:broken|doesn t work|not working|stopped working|won t work)\b"):
            return _answer("card_not_working")
        if payment:
            return _answer("card_payment_not_recognised")
        return _answer("card_not_working")

    if _has(t, r"\bstatement\b|\bextra charge\b|\bunknown charge\b"):
        if unknown:
            return _answer("card_payment_not_recognised")
        return _answer("extra_charge_on_statement")
    if _has(t, r"\bdirect debit\b|\bstanding order\b"):
        return _answer("direct_debit_payment_not_recognised")

    if _has(t, r"\b(?:country|countries|region|regions|nationality|residen|available in|supported in)\b"):
        if _has(t, r"\b(?:open|create|sign up|register|live|resident|account|app|service|supported|available)\b"):
            return _answer("country_support")
    if _has(t, r"\b(?:currenc|currencies|fiat)\b"):
        if _has(t, r"\b(?:supported|available|hold|have|use|offer|which|what)\b") and not rate:
            return _answer("fiat_currency_support")
    if _has(t, r"\bexchange\b|\bconvert\b|\bconversion\b|\bswap\b|\bcurrency\b|\bcurrencies\b|\bforex\b"):
        if fee and _has(t, r"\bexchange\b|\bconvert\b|\bconversion\b|\bforex\b|\bcurrency\b"):
            return _answer("exchange_charge")
        if _has(t, r"\b(?:in|on|using|via|through) (?:the |my )?app\b|\bhow (?:can|do) i (?:exchange|convert|swap)\b|\b(?:exchange|convert|swap) (?:my |some )?(?:money|currenc|funds)\b"):
            return _answer("exchange_via_app")
        return _answer("exchange_rate")

    if _has(t, r"\b(?:deposit|add funds|add money)\b"):
        if _has(t, r"\bcash\b|\bcheque\b|\bcheck\b"):
            return _answer("top_up_by_cash_or_cheque")
        return _answer("transfer_into_account")
    if _has(t, r"\b(?:receive|receiving|get paid)\b"):
        return _answer("receiving_money")
    if _has(t, r"\boutgoing\b"):
        return _answer("pending_transfer")
    if _has(t, r"\bpending\b"):
        return _answer("pending_card_payment")
    return _answer("card_not_working")