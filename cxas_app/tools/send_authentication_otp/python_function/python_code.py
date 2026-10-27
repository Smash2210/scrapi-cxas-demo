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
send_authentication_otp — Backend Capability Tool
"""

from typing import Dict, Any


def send_authentication_otp(clid: str = "") -> Dict[str, Any]:
    """Send an authentication OTP code to caller mobile phone.

    Returns:
        dict: Response payload or error envelope.
    """
    if not clid:
        return {
            "error": "INVALID_INPUT",
            "message": "CLID phone number is required to send authentication OTP.",
            "agent_action": "Ask the caller for their registered mobile number.",
        }
    return {
        "sent": True,
        "expires_in_sec": 300,
    }
