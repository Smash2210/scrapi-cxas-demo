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
send_password_reset_sms — Backend Capability Tool
"""

from typing import Dict, Any


def send_password_reset_sms(cirn: str = "") -> Dict[str, Any]:
    """Send self-serve portal password reset link via SMS.

    Returns:
        dict: Response payload or error envelope.
    """
    if not cirn:
        return {
            "error": "INVALID_INPUT",
            "message": "CIRN customer identifier is required to send password reset SMS.",
            "agent_action": "Identify the caller before dispatching password reset link.",
        }
    return {
        "sent": True,
        "valid_minutes": 30,
    }
