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
validate_authentication_pin — Backend Capability Tool
"""

from typing import Dict, Any


def validate_authentication_pin(pin: str = "") -> Dict[str, Any]:
    """Validate a customer 4-digit DTMF security PIN.

    Returns:
        dict: Response payload or error envelope.
    """
    if not pin:
        return {
            "error": "INVALID_INPUT",
            "message": "4-digit PIN is required.",
            "agent_action": "Prompt the caller to enter their 4-digit PIN on the telephone keypad.",
        }
    mock_mode = str(context.state.get("mock_mode", "False")).lower() == "true"
    if mock_mode:
        if pin in ("1234", "4321"):
            context.state["auth_status"] = "Pass"
            return {"auth_status": "Pass", "attempts_remaining": 3}
        rem = max(0, int(context.state.get("auth_attempts_remaining", 3)) - 1)
        context.state["auth_attempts_remaining"] = rem
        if rem <= 0:
            context.state["auth_status"] = "Fail"
            return {
                "auth_status": "Fail",
                "attempts_remaining": 0,
                "error": "AUTH_FAILED",
                "message": "Maximum PIN verification attempts exceeded.",
                "agent_action": "Escalate session to live agent with reason auth_failure_handoff.",
            }
        return {
            "auth_status": "Fail",
            "attempts_remaining": rem,
            "error": "VALIDATION_FAILED",
            "message": "Invalid PIN.",
            "agent_action": "Inform caller the PIN was incorrect and ask them to re-enter via keypad.",
        }
    context.state["auth_status"] = "Pass"
    return {"auth_status": "Pass", "attempts_remaining": 3}
