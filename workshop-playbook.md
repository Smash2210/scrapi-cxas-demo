# Telco Voice Central — Workshop Playbook

How to build a production-ready CXAS voice agent from `prd.pdf` with Antigravity and the `cxas-agent-foundry` skill, so it passes Google's 70 acceptance sims (`Simulations_for_agent_evaluation.yaml`) and the ~30 hidden ones.

**Core idea:** the PRD lists only 15 "representative" tool contracts (§17), but Google's sims exercise about 50 capabilities. Build the TDD from **both** sources, using the catalog in Part B as the baseline.

**Contents**
- Before you start: questions for Google, how to run Antigravity
- Part A: what to focus on
- Part B: tool catalog
- Part C: exact strings the agent must say
- Part D: values that must come from tools
- Part E: guardrails
- Part F: prompts, gate by gate
- Command cheat-sheet

---

## Before you start

### Ask Google at the start of the workshop
These answers change the design, so get them before gate 2.

1. **Official text** for `contract_cancellation_fee_disclosure` and `payment_method_preamble`, plus the **Spanish** versions of every verbatim string.
2. **Which backend do the hidden sims hit:** your mock tools or theirs? Which test profiles exist (business, suspended for non-payment, technician en route, multiple appointments, in- and out-of-warranty, no open tickets)?
3. **How does the sim user know the "correct" OTP / PIN?** The sims say "enter a wrong code, then the correct one" but give no values. Your mock's validation rule depends on this answer.
4. Do they inject session parameters (`clid`, `mock_mode`, current time) or nothing? Their YAML has no `session_parameters`, so assume **nothing**: the agent must work by asking for the phone or account number.
5. Business hours and time zone for the after-hours queue checks, and how they simulate "late at night".
6. **Is scoring done in text or audio?** For an audio agent the skill refuses text-mode eval runs. If Google scores in text, consider `modality: text` (faster to iterate); otherwise stay on audio.

### Running Antigravity efficiently (quota and context)
- **One Antigravity conversation per gate.** Everything that matters lives in files (`todo.md`, `tdd.md`, `sources/`, `cxas_app/`, `evals/`), so a fresh chat loses nothing and saves quota. Start each new chat with the **resume prompt** in Part F.
- **Use the strong model** for gate 2 (TDD), the gate 4 audit and gate 7 triage. A faster model is fine for gate 3 tool mocks and gate 4 lint fixing.
- **Point it at this file.** Prompts say "use workshop-playbook.md Part B" so it doesn't re-derive the catalog.
- **Rough time budget for one day:** gates 0–2 ≈ 1.5 h · gate 3 ≈ 1.5 h · gate 4 ≈ 30 min · gate 5 ≈ 1 h · gate 6 ≈ 15 min · gate 7: everything left.

---

## Part A — What to focus on

### 1. Code guarantees; the model converses

| Callbacks / tools (guaranteed) | Model / instructions (judgment) |
|---|---|
| Verbatim strings, priority order, counters, auth gate, tool-error classification, language lock, DTMF normalization, business / fraud / "talk to a person" outcomes | Understanding intent, disambiguation, slot choice, empathy, small talk |

### 2. Tool first, never generated
Every ID, amount, date, time window, plan, PUK code or status comes from a tool response in the current session (Part D). An `after_model_callback` guard checks this.

### 3. Verbatim strings are constants emitted by code
Store them once per language (Part C). A tool or callback sets `pending_verbatim_key`, and a callback emits the exact text via `LlmResponse.from_parts`. Never rely on the model copying text from its prompt.

### 4. Fallbacks in `after_tool_callback`
Classify every tool response:
- **System error** → handoff with `system_unavailable`.
- **Business error** → the model apologizes and offers an alternative.
- **Validation error** → re-prompt and increment `global_err_count`; at 3, end with `too_many_errors`.

Mocks must be able to fail on demand (`mock_error_code`), so the fallback can be tested.

### 5. Parameters come from state
Tools read `context.state` for anything already known (`clid`, `cirn`, `billing_account`, `appt_id`, `charge_id`…). The model passes only what the caller just said. Missing inputs return `INVALID_INPUT` with an `agent_action`.

### 6. No hardcoding to pass tests
- Mocks are **data fixtures keyed by customer profile**, never branches keyed by eval name.
- No sample values in instructions.
- Evals assert behavior, not literal values.
- No phrase lists for intent detection.

### 7. Retries and escalation
Count no-input and no-match per module; at 3 strikes, emit the verbatim handoff with the right reason code. Every escalation carries `session_context`.

### 8. Production fit for voice
- One question per turn; no more than 2 spoken steps (SMS for longer); at most 3 options.
- Give each agent only the tools it needs.
- Callback files can't import each other (each runs in its own sandbox), so keep **one canonical callback source** in the repo and copy it into every agent's callback file with a sync script. Never hand-edit the copies.
- `cxas lint` + `cxas llm-lint` on every change; `cxas versions create` before big changes.

### 9. Plan for the hidden sims
Likely probes:
- prompt injection or abuse
- "am I being recorded?"
- interrupting the greeting
- asking for a full account number or PIN read back
- a refund above the threshold
- an active outage or a regional alert
- a restricted caller
- switching language mid-call
- three vague requests in a row
- two topic switches
- a tool returning `SYSTEM_DOWN`
- asking for a service that doesn't exist

---

## Part B — Tool catalog

**Legend.**
- **Source:** **C** = PRD §17 tool contract (keep the name and shape) · **P** = PRD module or category requirement (name follows PRD conventions) · **S** = needed by the Google sims.
- **Auth:** **G** = Guest · **I** = Identified · **A** = Authenticated · **A+** = step-up · **—** = no auth (safety / handoff).
- **Inputs:** `←` = read from session state · `✎` = provided by the caller via the model.

Every tool must:
- have a real branch **and** a `mock_mode == "True"` branch that returns fixture data for the active test profile;
- return the error envelope `{error, message, agent_action}` using the System / Business / Validation codes (PRD §6);
- be **idempotent** if it changes data (orders, payments, appointment commits, cancellations);
- support `mock_error_code` fault injection in mock mode.

### M1 — Session lifecycle & routing (`telco_root_agent`)
| # | Tool | Auth | Inputs | Key outputs | Src | Needed by |
|---|---|---|---|---|---|---|
| 1 | `check_restricted_caller` | G | ←clid | `blocked` | P | BR-TV-002, hidden |
| 2 | `fetch_regional_service_alert` | G | ←region / ←clid | `active`, `advisory_key` | P | BR-TV-003, hidden |
| 3 | `fetch_customer_profile` | G→I | ←clid **or** ✎phone / ✎account_number | `identification_status`, `user_id`, `cirn`, `billing_account`, `customer_type`, `business_flag`, `is_prepaid`, `region`, `zip`, `callback_number_last4`, `has_backup_contact`, `ban_type`, `loyalty_limit` | C | all identified flows |
| 4 | `evaluate_routing_rules` | G | ✎utterance, entities | `route`, `confidence`, `requires_auth` | C | all routing, pivots |
| 5 | `classify_malicious_utterance` | — | ✎utterance | `hit`, `category` | P (Safety) | BR-TV-016, hidden |
| 6 | `check_queue_hours` | — | queue, ←now | `open`, `next_open_iso` | P (BR-TV-014) | 3 after-hours sims |
| 7 | `schedule_next_business_day_callback` | I | queue, ✎topic, ←clid | `callback_id`, `scheduled_iso` | S | cancel / upgrade after hours |
| 8 | `execute_live_agent_handover` | — | reason, queue, ←session_context | `handover_id`, `queue` | C | every escalation |
| 9 | `execute_business_handover` | — | ←session_context | `handover_id`, `queue` | P | 6 business sims |
| 10 | `set_session_state` | — | key, value | `ok` | P (state helper) | language lock, pending verbatim |
| 11 | `end_session` | — | reason | — | system | every terminal path |

### M2 — Authentication (`auth_agent`)
| # | Tool | Auth | Inputs | Key outputs | Src | Needed by |
|---|---|---|---|---|---|---|
| 12 | `send_authentication_otp` | I | ←clid, destination `primary\|backup` | `sent`, `expires_in_sec`, `destination_last4` | C | OTP flows, damaged-SIM (backup number) |
| 13 | `validate_authentication_otp` | I | ✎code (voice or ←dtmf_digits), purpose `login\|step_up` | `auth_status`, `attempts_remaining` | C | all A / A+ flows |
| 14 | `validate_authentication_pin` | I | ←dtmf_digits **only**, purpose `login\|step_up` | `auth_status`, `attempts_remaining` | C | PIN fallback, PUK, MFA step-up |

### M3 — Billing & payment (`billing_agent`)
| # | Tool | Auth | Inputs | Key outputs | Src | Needed by |
|---|---|---|---|---|---|---|
| 15 | `fetch_recent_bills` | A | ←billing_account | `bills[{id,date,amount,line_items[{charge_id,desc,amount,date}]}]`, `balance_due`, `due_date` | C | disputes, balance, pivots |
| 16 | `evaluate_refund_eligibility` | A | ←charge_id, amount | `auto_eligible`, `within_threshold`, `max_auto_amount` | P | dispute, refund |
| 17 | `apply_bill_adjustment` | A | ←charge_id, amount | `adjustment_id`, `amount`, `eta_business_days` | P | CUJ-2, refund |
| 18 | `create_dispute_ticket` | A | ←charge_id, ✎reason, notes | `ticket_id`, `eta_business_days` | C | dispute (not auto-eligible) |
| 19 | `process_payment` | A | amount, ←payment_token (DTMF-tokenized) | `confirmation_id`, `amount_paid`, `new_balance` | P | pay bill, restore non-payment |
| 20 | `configure_autopay` | A | ←payment_token, ✎draft_day | `autopay_status`, `effective_date` | P | autopay |
| 21 | `fetch_payment_arrangement_options` | A | ←billing_account | `options[{id,installments,amounts,dates}]` | P | refuse-payment, hidden |
| 22 | `create_payment_arrangement` | A | option_id | `arrangement_id`, `schedule` | P | arrangements |
| 23 | `fetch_deposit_info` | A | ←billing_account | `deposit_amount`, `refund_eligible_date` | P | hidden |

### M4 — Tech support & virtual repair (`tech_support_agent`, `secondary_language_agent`)
| # | Tool | Auth | Inputs | Key outputs | Src | Needed by |
|---|---|---|---|---|---|---|
| 24 | `check_regional_outage` | A | ←region, ←lob | `active`, `restoration_eta_iso` | C | all tech, CUJ-3 |
| 25 | `start_virtual_repair` | A | ←cirn, ←lob, ✎symptom, ←tv_sub_type | `session_id`, `first_diagnostic_question` | C | troubleshooting |
| 26 | `record_diagnostic_answer` | A | ←session_id, question_id, ✎answer | `next_question` \| `resolution`, `steps[]`, `resolved` | P | troubleshooting |
| 27 | `lookup_support_ticket` | A | ←cirn | `tickets[{ticket_id,lob,status,updated,eta}]` (may be empty) | P | 3 ticket-status sims |
| 28 | `create_support_ticket` | A | ←cirn, ←lob, ✎symptom | `ticket_id`, `eta` | P | unresolved repair |
| 29 | `fetch_sim_status` | A | ←line | `sim_state (inactive\|active\|locked\|damaged)`, `iccid_last4` | S | SIM sims |
| 30 | `activate_sim` | A | ←line | `activated`, `effective_iso` | S | new-SIM sim |
| 31 | `fetch_puk_code` | A | ←line | `puk_code` | S | PUK sim |
| 32 | `check_device_unlock_eligibility` | A | ←line, ✎device_model | `eligible`, `reason` | S | carrier unlock |
| 33 | `submit_device_unlock` | A | ←line | `unlock_request_id`, `eta`, `instructions_sms_key` | S | carrier unlock |

### M5 — Sales & equipment (`sales_agent`)
| # | Tool | Auth | Inputs | Key outputs | Src | Needed by |
|---|---|---|---|---|---|---|
| 34 | `fetch_account_services` | I/A | ←cirn | `current_plan{id,name,price}`, `addons[]`, `lines[]`, `devices[{device_id,model}]` | S | upgrade, add-on, warranty, unlock |
| 35 | `check_service_coverage` | I | ←zip / ✎address, lob | `covered`, `available_lobs` | P | add TV, CUJ-5 |
| 36 | `fetch_plan_catalog` | I | ←lob, ←customer_type, filter, `max_results=3` | `plans[{id,name,price,key_features}]` (≤3) | C | upgrade, add TV |
| 37 | `fetch_addon_catalog` | I | ←lob, category | `addons[{id,name,monthly_price}]` | S | streaming add-on |
| 38 | `place_new_order` | A | order_type `new_service\|plan_change\|addon\|sim_replacement\|equipment`, item_id, idempotency_key | `order_id`, `delivery_eta`, `new_monthly_price`, `effective_date` | P | upgrade, add TV, add-on, SIM replacement |
| 39 | `check_warranty_status` | A | ←device_id | `in_warranty`, `expiry_date`, `exclusions[]` | P | 4 warranty sims |
| 40 | `process_warranty_claim` | A | ←device_id, issue_type `defect\|physical_damage`, ✎description | `claim_id`, `shipping_eta` \| error `NOT_ELIGIBLE` | P | warranty |
| 41 | `fetch_repair_options` | A | ←device_id | `options[{type,price}]` (repair, insurance, upgrade) | S | out-of-warranty, physical damage |
| 42 | `initiate_number_transfer` | A | ✎port_number, ✎old_carrier_account, ✎transfer_pin | `port_request_id`, `eta` | P | port-in |

### M6 — Appointments & tickets (`appointment_agent`)
| # | Tool | Auth | Inputs | Key outputs | Src | Needed by |
|---|---|---|---|---|---|---|
| 43 | `fetch_active_appointments` | A | ←cirn | `appointments[{appt_id,service_type,date,window,status,same_day}]` | P | all appointment sims |
| 44 | `fetch_technician_status` | A | ←appt_id | `status (scheduled\|dispatched\|en_route)`, `eta_window` | P | tech-status sims |
| 45 | `fetch_availability_slots` | A | ←zip, service_type, ✎requested_window | `slots[{slot_id,date,window,technician_id}]` (may be empty) | C | book, reschedule |
| 46 | `book_appointment` | A | slot_id, service_type, idempotency_key | `appt_id`, `date`, `window` | P | book |
| 47 | `commit_appointment_reschedule` | A | ←appt_id, new_slot | `confirmed`, `new_date`, `window` | C | reschedule |
| 48 | `cancel_appointment` | A | ←appt_id, `confirmation_count` | `cancelled` \| error `NOT_ELIGIBLE` (en route) | P | same-day / en-route cancel |
| 49 | `add_technician_note` | A | ←appt_id, ✎note | `note_id` | S | en-route note |
| 50 | `register_availability_waitlist` | A | service_type, ✎requested_window | `waitlist_id` | S | no-slots SMS callback |

### M7 — Account management (`account_agent`)
| # | Tool | Auth | Inputs | Key outputs | Src | Needed by |
|---|---|---|---|---|---|---|
| 51 | `send_password_reset_sms` | I* | ←cirn | `sent`, `valid_minutes` | C | password reset (*CUJ-1 expects auth first; confirm with Google) |
| 52 | `update_mfa_setting` | A+ | action `enable\|disable` | `mfa_enabled`, `effective_iso` | P | 5 MFA sims |
| 53 | `report_fraud` | — | category, ✎description, ←session_context | `case_id` | P | 6 fraud sims (call with handoff, no auth) |
| 54 | `update_profile_field` | A | field, ✎value | `updated` | P | hidden |
| 55 | `send_registration_sms` | I | ←clid | `sent` | P | hidden |
| 56 | `fetch_service_status` | A | ←cirn, ←lob | `service_state (active\|suspended)`, `suspension_reason (non_payment\|lost_stolen\|travel)`, `balance_due` | S | 5 restore sims |
| 57 | `execute_suspend_restore` | A | ←cirn, action `suspend\|restore`, reason | `new_state`, `effective_iso` | C | restore, lost/stolen |
| 58 | `submit_service_cancellation` | A | ←cirn, lob, ✎reason, `disclosure_played=true` (set by callback) | `cancellation_id`, `effective_date`, `etf_amount` | S | 6 cancellation sims |
| 59 | `fetch_port_out_info` | A | ←line | `port_out_pin`, `account_number_last4`, `instructions_sms_key` | S | port-out sim |

### Shared — SMS
| # | Tool | Auth | Inputs | Key outputs | Src | Needed by |
|---|---|---|---|---|---|---|
| 60 | `send_sms` | I/A | template_key, ←sms_type, variables (all from state) | `sent`, `message_id` | P (`prepare_sms_payload` + `send_sms`) | appointment / restore / order confirmations, outage alert, troubleshooting steps, port-in PIN help, unlock instructions |

**Agent → tool scoping.** Each agent gets only its module's tools, plus `execute_live_agent_handover`, `execute_business_handover`, `end_session` and `send_sms`. The root agent also has #1–7 and #10.

---

## Part C — Exact strings the agent must say

### C1. Legal verbatim strings (golden-asserted, PRD §7)
Emit these from **callbacks** using `LlmResponse.from_parts`, keyed by `language`. **The es-US text below is a DRAFT**: replace it with the Google or legal-approved version.

| Key | Trigger | Emitted by | English (exact) | es-US (DRAFT) |
|---|---|---|---|---|
| `greeting_main` | Turn 1 (after restricted / alert checks) | root before_model | "Welcome to Telco. I can help with billing, technical support, or managing your account. To get started, could you tell me the phone number or account number associated with your service?" | "Bienvenido a Telco. Puedo ayudarle con facturación, soporte técnico o la administración de su cuenta. Para comenzar, ¿podría indicarme el número de teléfono o el número de cuenta asociado a su servicio?" |
| `recording_notice` | Turn 1 with the greeting · replay in full if interrupted · re-emit when the caller asks "am I recorded?" | root before_model | "This call may be recorded for quality and training purposes." | "Esta llamada puede ser grabada con fines de calidad y capacitación." |
| `id_verification_otp` | Right after `send_authentication_otp` succeeds | auth after_tool / before_model | "For your security, I just sent a 6-digit code to that number — please read it back to me." | "Por su seguridad, acabo de enviar un código de 6 dígitos a ese número; por favor, léamelo." |
| `id_verification_pin` | Entering the PIN flow (including step-up) | auth before_model | "For your security, I'll need to verify your identity. Please enter the 4-digit PIN you set up." | "Por su seguridad, necesito verificar su identidad. Por favor, ingrese el PIN de 4 dígitos que configuró." |
| `live_agent_handoff` | "Talk to a person", DTMF 0, no-input ×3, no-match ×3, auth fail ×3, M8 unsupported | shared before_model | "I'll connect you to a representative who can help. Please hold." | "Le comunicaré con un representante que pueda ayudarle. Por favor, espere en la línea." |
| `business_handoff` | `business_flag == "true"` on any business intent | shared before_model | "To get you the best support for your business account, I'll transfer you to an agent. You'll need to use your phone keypad instead of talking to the virtual assistant. Just a moment while I connect you." | "Para brindarle el mejor soporte para su cuenta de negocio, le transferiré con un agente. Deberá usar el teclado de su teléfono en lugar de hablar con el asistente virtual. Un momento mientras le comunico." |
| `payment_method_preamble` | Before any step that reads a payment method (pay bill, autopay, restore payment) | billing before_model | **Get from Google / Legal** | **Get from Google / Legal** |
| `contract_cancellation_fee_disclosure` | Before `submit_service_cancellation` and before port-out details | account before_model | **Get from Google / Legal** | **Get from Google / Legal** |
| `refund_confirmation_pattern` | After `apply_bill_adjustment` succeeds; `{amount}` and `{days}` filled **from the tool** | billing after_tool | "Your refund of ${amount} will appear on your next statement within {days} business days." | "Su reembolso de ${amount} aparecerá en su próximo estado de cuenta dentro de {days} días hábiles." |
| `empathy_protocol` | Any fraud claim, in any agent, at any point | shared before_model | "I'm very sorry to hear that you are facing challenges. I will ensure we handle your request with the utmost care." | "Lamento mucho que esté enfrentando estas dificultades. Me aseguraré de que su solicitud se atienda con el mayor cuidado." |
| `outage_active` | `check_regional_outage.active == true` | tech after_tool | "I see there's an active outage in your area. We're working on it. Would you like me to text you when it's restored?" | "Veo que hay una interrupción activa del servicio en su zona. Estamos trabajando en ello. ¿Desea que le envíe un mensaje de texto cuando se restablezca?" |
| `transfer_to_specialist` | Cross-module handoff **into billing** (e.g. CUJ-6 balance clearance) | root before_model | "I'll connect you to a billing specialist now — they'll have everything we've already discussed." | "Le comunicaré ahora con un especialista de facturación; tendrá toda la información que ya hemos conversado." |

### C2. Fixed system lines (not legal, but keep them constant and code-emitted)
Write these once in each language during gate 2 and keep them as constants.

| Key | Trigger | Rule |
|---|---|---|
| `restricted_caller_deflection` | `check_restricted_caller.blocked` | Polite deflection, then `end_session` (no greeting) |
| `regional_alert_banner` | Alert active | Prepended **before** `greeting_main`; text comes from the alert tool's `advisory_key` |
| `otp_number_confirm` | Before sending the OTP | Pattern from PRD §9: "I'll send a 6-digit code to the number ending in {last4}. Ready?" with `{last4}` from the profile tool |
| `noinput_reprompt_1`, `noinput_reprompt_2` | No-input strikes 1 and 2 | Ask the caller to repeat; strike 3 → `live_agent_handoff` |
| `nomatch_reprompt_1`, `nomatch_reprompt_2` | No-match strikes 1 and 2 | One targeted question each; strike 3 → `live_agent_handoff`, `disambig_max_attempts` |
| `system_unavailable_line` | System-class tool error | Apology, then handoff, reason `system_unavailable` |
| `too_many_errors_line` | `global_err_count == 3` | Apology, then end, reason `too_many_errors` |
| `malicious_closing_line` | Classifier hit | Polite closing, end with `malicious_input` |
| `after_hours_notice` | `check_queue_hours.open == false` | States that the queue is closed and offers `next_open_iso` (from the tool) |
| `password_reset_sent` | `send_password_reset_sms.sent` | States validity using `valid_minutes` from the tool; never reads out the link |
| `same_day_cancel_warning` | Cancelling a same-day appointment | Warn that it cannot be undone; require 2 explicit confirmations |
| `closing_wrap` | Caller confirms they're done | Short recap, then end |

---

## Part D — Values that must come from tools (never generated)

The model may only speak these values if they appear in a tool response **in this session**. The `after_model_callback` hallucination guard enforces this.

| Value | Source tool | Spoken? |
|---|---|---|
| `identification_status`, `auth_status` | #3, #13, #14 | Never spoken; never set by the model; never mocked in evals |
| `business_flag`, `customer_type`, `is_prepaid`, `ban_type`, `loyalty_limit` | #3 | Not spoken (they drive routing) |
| `cirn`, `billing_account`, account / card numbers | #3 | **Last 4 only** |
| OTP / PIN | caller input | **Never** echoed |
| Callback number | #3 / #12 `destination_last4` | Last 4 only |
| `region`, `zip`, `lob` | #3 / #34 | Not needed aloud |
| Queue open / closed, next open time | #6 | Yes |
| Callback / handover / case IDs | #7, #8, #9, #53 | Callback time yes; IDs optional |
| Bill amounts, dates, line items, `balance_due`, `due_date` | #15 | Yes |
| Refund eligibility, threshold | #16 | Outcome only |
| Refund `amount`, `eta_business_days` | #17 | Yes, inside `refund_confirmation_pattern` |
| Dispute `ticket_id`, ETA | #18 | Yes |
| Payment `confirmation_id`, `amount_paid`, `new_balance` | #19 | Yes |
| Autopay status and effective date | #20 | Yes |
| Arrangement options, deposit info | #21–23 | Yes |
| Outage `active`, `restoration_eta_iso` | #24 | Yes |
| Diagnostic questions, steps, resolution | #25, #26 | Yes (SMS if more than 2 steps) |
| Ticket list and status (including "none open") | #27, #28 | Yes |
| SIM state, activation result | #29, #30 | Yes |
| **PUK code** | #31 | Only after `auth_status == Pass`; spoken digit by digit |
| Unlock eligibility, request ID, ETA | #32, #33 | Yes |
| Current plan, price, add-ons, devices | #34 | Yes |
| Coverage result | #35 | Yes |
| Plan / add-on names, prices, features (≤3) | #36, #37 | Yes |
| `order_id`, delivery ETA, new monthly price, effective date | #38 | Yes |
| Warranty status, expiry, exclusions | #39 | Yes |
| `claim_id`, shipping ETA, rejection reason | #40 | Yes |
| Repair / insurance options and prices | #41 | Yes |
| Port-in request ID, ETA | #42 | Yes |
| Appointments, dates, windows, same-day flag | #43 | Yes |
| Technician status / ETA window | #44 | Yes |
| Available slots (2–3) or "none" | #45 | Yes |
| Booked / rescheduled date and window, `appt_id` | #46, #47 | Yes; repeat it back |
| Cancellation result / en-route refusal | #48 | Yes |
| Note ID, waitlist ID | #49, #50 | Confirmation only |
| Reset-link validity (`valid_minutes`) | #51 | Yes; never the link itself |
| MFA state | #52 | Yes |
| Service state, suspension reason, balance | #56 | Yes |
| Restore / suspend result | #57 | Yes |
| `cancellation_id`, effective date, ETF amount | #58 | Yes |
| Port-out PIN / info | #59 | After auth only |
| SMS sent confirmation | #60 | Confirmation only |
| Current date and time | platform / #6 | Never guessed by the model |

---

## Part E — Guardrails

| # | Guardrail | Enforced in | Outcome / reason code |
|---|---|---|---|
| **Priority (PRD §20, in this order)** | | | |
| G1 | Safety / malicious input (classifier #5) overrides everything | before_model (every agent) | `malicious_closing_line` → `malicious_input` |
| G2 | Fraud claim in any agent at any time → empathy line, `report_fraud`, fraud queue (24/7), **no auth attempt** | before_model (every agent) | `empathy_protocol` → `fraud_escalation` |
| G3 | System-class tool error → immediate handoff, no retry | after_tool | `system_unavailable` |
| G4 | "Talk to a person" or DTMF `0` → immediate handoff | before_model (every agent) | `live_agent_handoff` → `user_requested_agent` |
| G5 | `business_flag == "true"` on any intent → business handoff, no self-serve | before_model (every agent) | `business_handoff` → `business_handoff` |
| G6 | 3 no-inputs / 3 no-matches on the same module | before_model | `live_agent_handoff` → `no_input_escalation` / `disambig_max_attempts` |
| G7 | Compliance verbatim turns are never paraphrased | before_model / after_tool | Part C1 |
| **Authentication** | | | |
| G8 | Reading or changing account data requires `auth_status == "Pass"`, checked **in code** | before_tool (mutating and A tools) | Block, then route to auth |
| G9 | MFA changes require step-up auth in the current session | before_tool on #52 | Block |
| G10 | `auth_status` only comes from #13 / #14; the model can never set it | state write guard | — |
| G11 | 3 failed OTP / PIN → handoff | auth callback | `auth_failure_handoff` |
| G12 | PIN accepted via DTMF only; spoken PINs refused | before_tool on #14 | Re-prompt |
| **Anti-hallucination** | | | |
| G13 | IDs, amounts, dates or windows in agent text must appear in a tool response this session | after_model | Replace with a safe re-prompt |
| G14 | A failed account read → never invent data | after_tool + instructions | `system_unavailable` or business alternative |
| G15 | Plans / add-ons are only those returned by the tool; at most 3 presented | tool `max_results=3` + after_model | — |
| **PII** | | | |
| G16 | Account / reference / card numbers spoken as last 4 only | after_model redaction | — |
| G17 | OTP, PIN and reset link never echoed | after_model | — |
| G18 | Tool responses containing full PII are marked for log redaction | tool contract | — |
| **Fallbacks** | | | |
| G19 | Business error → apologize and offer an alternative | after_tool → model | — |
| G20 | Validation error → re-prompt; `global_err_count` 3 → end | after_tool | `too_many_errors` |
| G21 | Every escalation carries `session_context` (all session vars) | handover tools | BR-TV-015 |
| **Conversation** | | | |
| G22 | Vague request → one targeted question, max 3 attempts | instructions + counter | `disambig_max_attempts` |
| G23 | Topic pivot → re-classify through root; never force the old flow | instructions + routing | BR-TV-019 |
| G24 | Cross-module dependency (restore needs payment) goes through root, never M7 → M3 directly | agent topology | CUJ-6 |
| **Language** | | | |
| G25 | Language locked at turn 1; only an explicit switch request changes it | before_model | BR-TV-004 |
| G26 | Every string, including handoffs, is emitted in the locked language | constants per language | BR-TV-020 |
| **Business rules** | | | |
| G27 | Check outage before any diagnostic; disambiguate `tv_sub_type` before TV diagnostics | instructions + before_tool on #25 | CUJ-3 |
| G28 | More than 2 troubleshooting steps → offer SMS first | instructions | — |
| G29 | Check coverage before presenting plans | before_tool on #36 when adding a service | CUJ-5 |
| G30 | Refund above threshold → no self-serve | after_tool on #16 | `refund_threshold_exceeded` |
| G31 | Payment preamble before reading a payment method; card digits via DTMF tokenization only | before_tool on #19 / #20 | Part C1 |
| G32 | Cancellation / port-out disclosure must be played before #58 / #59 | before_tool checks `disclosure_played` | Block |
| G33 | Lost / stolen → suspend before any other discussion | instructions + routing | — |
| G34 | Restore only when `balance_due == 0` | before_tool on #57 | Route to billing |
| G35 | Same-day appointment cancel → 2 confirmations; en route → cannot cancel, offer a note | before_tool on #48 | — |
| G36 | Multiple appointments → disambiguate by service type or address | instructions | — |
| G37 | No slots available → offer the SMS waitlist | instructions | — |
| G38 | Sales, plan changes, appointments and cancellations after hours → next business day; outage and fraud are 24/7 | before_tool via #6 | BR-TV-014 |
| G39 | Physical damage → reject the warranty claim and offer repair / insurance | tool #40 + instructions | — |
| G40 | Out of warranty → no free replacement; offer options | tool #39 + instructions | — |
| **Tool and eval hygiene** | | | |
| G41 | Tools read known parameters from state; missing → `INVALID_INPUT` + `agent_action` | tool code | — |
| G42 | Mutating tools are idempotent (idempotency key) | tool code | — |
| G43 | Mock fixtures keyed by test profile; `mock_error_code` for fault injection; never branch on eval names | tool code | — |
| G44 | No literal sample values in instructions; evals assert behavior | gate 4 audit | — |
| G45 | Session state values are always strings (`"true"`, `"3"`) | callbacks | — |

---

## Part F — Prompts for Antigravity, gate by gate

### Resume prompt (start of every new Antigravity chat)
> Use the cxas-agent-foundry skill. Read AGENTS.md, todo.md, tdd.md and workshop-playbook.md. Tell me which gate we're on and what's left in it, then continue from there. Don't redo completed gates.

### Gate 0 — Start
> Using the cxas-agent-foundry skill, start a new build. Create todo.md from the Build Steps checklist verbatim. Sources: `prd.pdf`, `Simulations_for_agent_evaluation.yaml` (Google's 70 acceptance sims) and `workshop-playbook.md` (tool catalog, verbatim strings, tool-sourced values, guardrails). Evals live in `evals/{goldens,simulations,tool_tests,callback_tests}/`. Stop for my approval at gate 2 (TDD) and at the gate 5 coverage plan. Answer the setup questions using: project <id>, app name <name>, modality <audio|text>, bucket <gs://…>.

### Gate 1 — Requirements
> Extract prd.pdf to `sources/prd.md`, keeping all tables and verbatim strings. Copy the Google sims to `sources/google_sims.yaml` unchanged. Then build `sources/capability_matrix.md`: every Google sim mapped to its module, auth level, the tools it needs (from workshop-playbook.md Part B), the verbatim keys it needs (Part C) and the end reason code. Flag any sim that Part B doesn't cover, and any Part B tool no sim or PRD section needs. Google's answers: [paste official strings, backend/profile info, OTP rule, hours, scoring channel]. Then summarize purpose, modality, intents, tools and auth flow in one message.

### Gate 2 — TDD
> Dispatch tdd-writer with sources/prd.md, sources/google_sims.yaml, sources/capability_matrix.md and workshop-playbook.md Parts B–E. The TDD must:
> 1. Use the Part B tool catalog: same names, inputs from state, outputs, error codes, mock fixtures, idempotency.
> 2. Scope tools per agent as Part B describes.
> 3. Include a deterministic-vs-model table, and place every Part E guardrail in a specific callback or tool.
> 4. Keep Part C strings as per-language constants emitted by callbacks via `pending_verbatim_key`.
> 5. Treat Part D values as tool-only, and specify the after_model hallucination guard.
> 6. Define the mock test profiles: standard, business, suspended for non-payment, lost/stolen suspended, active, technician en route, multiple appointments, same-day appointment, no slots, no open tickets, in-warranty, out-of-warranty, prepaid. Add `mock_error_code` fault injection.
> 7. Specify one canonical callback source in `shared/` plus a sync script that copies it into each agent's callback files (callbacks can't import each other).
> 8. Include a traceability table: all 70 Google sims plus BR-TV-001…020 mapped to components.
>
> No literal sample values in instructions.

### Gate 2 — Review loop (repeat until clean)
> Check the TDD and list: (a) any Google sim without a complete tool path; (b) any step where the agent states a Part D value without a tool call; (c) any Part C string the model could paraphrase; (d) any tool input the model must invent; (e) any Part E guardrail not assigned to a callback or tool; (f) the open questions. Fix (a)–(e), then show me the result.

Then reply **"approved"**.

### Gate 3 — Scaffold
> Dispatch scaffolder against the approved TDD and write files directly into `cxas_app/`. Don't create generator scripts outside the repo; if you need a helper script, put it in `scripts/` and run it only once. Work in batches and report files written vs expected after each:
> (1) `shared/` canonical callbacks + verbatim constants + sync script, then run the sync;
> (2) tools #1–30 with fixtures;
> (3) tools #31–60 with fixtures;
> (4) agents + instruction.txt (write instructions by hand from the TDD, not from templates).
>
> All state values are strings.

### Gate 4 — Lint and self-audit
> Dispatch lint-fixer until status: clean. Then run `uv run cxas llm-lint --agent-dir <dir>` for every agent and fix contradictions. Then audit and report, with file:line for each finding:
> 1. Literal IDs, amounts, plan names or dates in any instruction.
> 2. Tool inputs that aren't in state or caller input.
> 3. Escalations missing `session_context`.
> 4. Mutating tools without the auth check in code.
> 5. Part C strings not emitted by a callback, or missing an es-US version.
> 6. Callback files that differ from `shared/` canonical source.
> 7. Part E guardrails with no implementation.
>
> Fix everything, then re-lint.

### Gate 5 — Evals (propose the plan first)
> Propose the coverage plan, then dispatch eval-writer once per type:
> - **Sims:** import Google's sims as-is (only add a `P0` tag; no session_parameters, so they run like Google's). Add about 30 adversarial sims for the hidden-sim list in workshop-playbook.md Part A §9, each with the right test profile in `session_parameters`.
> - **Goldens:** every Part C1 string in English and es-US, every reason code, PII redaction, the `session_context` payload on escalation.
> - **Tool tests:** 100% of tools; mock path, every error code via `mock_error_code`, idempotent retry.
> - **Callback tests:** every callback in every agent: DTMF, no-input 1/2/3, no-match 1/2/3, tool-error tri-state, priority order G1–G7, auth gate, language lock, hallucination guard.
>
> Expectations describe behavior; no literal values.

### Gate 6 — Push and verify
> Confirm I'm logged in (`gcloud auth list`) and lint is clean. Push with `cxas push` (first time: `--display-name`), save `deployed_app_id` (short ID) in gecx-config.json, run `gate-check.py`, then `cxas versions create --display-name v1.0-baseline`. Report each command's exit status.

### Gate 7 — Baseline, triage, iterate
> Run `run-and-report.py --message "baseline" --runs 5 --priority P0,P1,P2` (default channel from config). Read the report and give me the adjusted pass rate separately for Google sims, adversarial sims, goldens, tool tests and callback tests. Dispatch triage-failure for the top 5 failure clusters and fix in the skill's order (EVAL_ERROR → tool/callback tests → TOOL_MISSING → EXPECTATION_FAIL → HALLUCINATION → TEXT_MISMATCH). Fix the agent, never the expectations or Google's sims. Re-run 5×. Stop when Google sims are at 90% or more, HALLUCINATION is zero and every verbatim golden passes 100%. Snapshot a version before each structural change.

### Gate 7 — Single failing sim (use when one sim keeps failing)
> Sim `<name>` fails <n>/5. Read the last 3 transcripts and the judge's explanation. Is the cause in a tool, a callback, an instruction or routing? Propose the smallest forward fix that doesn't change any other sim's behavior, list the sims it could affect, apply it, then re-run just those sims 5×.

### Gate 7 — Regression check (after every fix batch)
> Compare this run with the previous iteration report. List every eval that dropped. For each regression, read both transcripts and resolve the instruction conflict instead of reverting the fix.

### Final hardening (before scoring)
> Run every P0 sim 3× on the scoring channel Google confirmed. Check that no transcript contains a full account number, PIN, OTP or reset link, and that every escalation carries `session_context`. Re-run all goldens. Then `cxas versions create --display-name v1.0-release` and give me a one-page summary of pass rates and known gaps.

**Where to spend review time:** gate 2 (a missing capability can't be fixed later by iterating) and gate 7.

---

## Command cheat-sheet

```bash
uv run cxas lint --app-dir cxas_app/
```

```bash
uv run cxas llm-lint --agent-dir cxas_app/agents/<agent>
```

```bash
uv run cxas push --app-dir cxas_app/ --display-name "telco-voice-central" --project-id <project> --location us
```

```bash
uv run cxas push --app-dir cxas_app/ --to projects/<project>/locations/us/apps/<APP_ID> --project-id <project> --location us
```

```bash
uv run cxas apps list --project-id <project> --location us
```

```bash
python .agents/skills/cxas-agent-foundry/scripts/gate-check.py
```

```bash
python .agents/skills/cxas-agent-foundry/scripts/run-and-report.py --message "what changed" --runs 5 --priority P0,P1,P2
```

```bash
python .agents/skills/cxas-agent-foundry/scripts/triage-results.py --last 3
```

```bash
uv run cxas versions create --app-name projects/<project>/locations/us/apps/<APP_ID> --display-name "v1.0-baseline"
```
