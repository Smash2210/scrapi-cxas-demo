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
validate_authentication_otp — Backend Capability Tool
"""

from typing import Dict, Any


def validate_authentication_otp(code: str = "") -> Dict[str, Any]:
    """Validate a customer-entered 6-digit one-time passcode.

    Returns:
        dict: Response payload or error envelope.
    """
    if not code:
        return {
            "error": "INVALID_INPUT",
            "message": "OTP passcode is required.",
            "agent_action": "Prompt the caller to speak or enter the 6-digit passcode.",
        }
    mock_mode = str(context.state.get("mock_mode", "False")).lower() == "true"
    if mock_mode:
        if code in ("123456", "654321"):
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
                "message": "Maximum OTP verification attempts exceeded.",
                "agent_action": "Escalate session to live agent with reason auth_failure_handoff.",
            }
        return {
            "auth_status": "Fail",
            "attempts_remaining": rem,
            "error": "VALIDATION_FAILED",
            "message": "Invalid authentication code.",
            "agent_action": "Inform caller the code was incorrect and reprompt for 6-digit code.",
        }
    context.state["auth_status"] = "Pass"
    return {"auth_status": "Pass", "attempts_remaining": 3}
