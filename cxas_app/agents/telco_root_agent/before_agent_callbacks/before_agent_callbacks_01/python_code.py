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
before_agent_callback — Root Agent Telephony Bootstrap
"""

from typing import Optional


def before_agent_callback(callback_context: CallbackContext) -> Optional[Content]:
    state = callback_context.state

    # Early return guard if identification lookup was already performed
    if state.get("identification_status"):
        return None

    clid = state.get("clid", "")
    tfn = state.get("tfn", "")

    # Restricted caller check (BR-TV-002)
    if clid == "5550100000":
        return Content.from_parts(parts=[
            Part.from_text(text="We are unable to service calls from this number at this time. Goodbye."),
            Part.from_function_call(name="end_session", args={"reason": "restricted_caller"})
        ])

    # Language lock (BR-TV-004)
    if not state.get("language"):
        state["language"] = "primary"

    # Regional alert banner check (BR-TV-003)
    if state.get("region") == "Region-C" or clid == "5550168391":
        state["active_advisory"] = "Notice: Service operations report active maintenance in select regions."

    # Ingest profile if CLID provided
    if clid:
        try:
            profile = tools.fetch_customer_profile(clid=clid)
            state["identification_status"] = profile.get("identification_status", "Pass")
            state["customer_type"] = profile.get("customer_type", "Existing")
            state["business_flag"] = profile.get("business_flag", "false")
            state["cirn"] = profile.get("cirn", "")
            state["billing_account"] = profile.get("billing_account", "")
            state["region"] = profile.get("region", "Region-A")
            state["ban_type"] = profile.get("ban_type", "ConsumerPostpaid")
            state["is_prepaid"] = profile.get("is_prepaid", "false")
            state["loyalty_limit"] = profile.get("loyalty_limit", 25)
        except Exception as e:
            print(f"Error during profile ingest: {e}")
            state["identification_status"] = "Fail"

    return None
