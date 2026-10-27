# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
before_model_callback — Strict Preprocessing Pipeline
"""

import re
from typing import Optional, Dict, Any, List, Iterator


def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    state = callback_context.state

    # 1. DTMF Capture & Normalization (BR-TV-007)
    for part in callback_context.get_last_user_input():
        if part.text:
            dtmf_match = re.search(r"(?:user pressed|<dtmf>|dtmf:?\s*)(\d+)", part.text, re.IGNORECASE)
            if dtmf_match:
                state["dtmf_digits"] = dtmf_match.group(1)

    # 2. Silence / No-Input Accounting (BR-TV-006)
    silence_pattern = r"<context>no user activity detected for \d+ seconds\.</context>"
    last_text = ""
    for part in callback_context.get_last_user_input():
        if part.text:
            last_text = part.text

    if re.search(silence_pattern, last_text, re.IGNORECASE):
        no_input = int(state.get("local_noinput_counter") or 0) + 1
        state["local_noinput_counter"] = no_input
        if no_input == 1:
            return LlmResponse.from_parts(parts=[
                Part.from_text(text="Sorry, I didn't hear anything. How can I help you?")
            ])
        elif no_input == 2:
            return LlmResponse.from_parts(parts=[
                Part.from_text(text="I still can't hear you. Please speak up or enter your request.")
            ])
        else:
            tools.execute_live_agent_handover(reason="no_input_escalation", session_context=dict(state))
            return LlmResponse.from_parts(parts=[
                Part.from_text(text="I'm having trouble hearing you. Let me connect you with a representative who can help."),
                Part.from_function_call(name="end_session", args={"reason": "no_input_escalation"})
            ])
    else:
        if last_text and not re.search(r"<event>", last_text):
            state["local_noinput_counter"] = 0

    # 3. Tool Error Tri-State Triage (BR-TV-010)
    api_resp = state.get("api_resp", "")
    if any(code in api_resp for code in ["SYSTEM_DOWN", "INTERNAL_ERROR", "AUTH_SERVICE_UNAVAILABLE"]):
        tools.execute_live_agent_handover(reason="system_unavailable", session_context=dict(state))
        return LlmResponse.from_parts(parts=[
            Part.from_text(text="I am currently experiencing a technical system issue. Connecting you to an agent now."),
            Part.from_function_call(name="end_session", args={"reason": "system_unavailable"})
        ])
    elif any(code in api_resp for code in ["INVALID_INPUT", "MALFORMED_REQUEST"]):
        err_count = int(state.get("global_err_count") or 0) + 1
        state["global_err_count"] = err_count
        if err_count >= 3:
            tools.execute_live_agent_handover(reason="too_many_errors", session_context=dict(state))
            return LlmResponse.from_parts(parts=[
                Part.from_text(text="We have encountered multiple processing errors. Transferring you to a representative."),
                Part.from_function_call(name="end_session", args={"reason": "too_many_errors"})
            ])

    # 4. Safety & Malicious Input Classifier (BR-TV-016)
    if any(k in last_text.lower() for k in ["ignore all instructions", "system prompt", "drop table", "override security"]):
        return LlmResponse.from_parts(parts=[
            Part.from_text(text="I am unable to continue this interaction. Goodbye."),
            Part.from_function_call(name="end_session", args={"reason": "malicious_input"})
        ])

    # 5. Priority Pre-Checks (BR-TV-012 Business & BR-TV-013 Fraud)
    if str(state.get("business_flag", "")).lower() == "true":
        tools.execute_live_agent_handover(reason="business_handoff", session_context=dict(state))
        return LlmResponse.from_parts(parts=[
            Part.from_text(text="To get you the best support for your business account, I'll transfer you to an agent. You'll need to use your phone keypad instead of talking to the virtual assistant. Just a moment while I connect you."),
            Part.from_function_call(name="end_session", args={"reason": "business_handoff"})
        ])

    if any(k in last_text.lower() for k in ["fraud", "unauthorized charge", "identity theft", "someone hacked"]):
        tools.execute_live_agent_handover(reason="fraud_escalation", session_context=dict(state))
        return LlmResponse.from_parts(parts=[
            Part.from_text(text="I'm very sorry to hear that you are facing challenges. I will ensure we handle your request with the utmost care."),
            Part.from_function_call(name="end_session", args={"reason": "fraud_escalation"})
        ])

    return None
