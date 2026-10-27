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
execute_live_agent_handover — Backend Capability Tool
"""

from typing import Dict, Any


def execute_live_agent_handover(reason: str = "", session_context: dict = {}) -> Dict[str, Any]:
    """Escalate conversation to live agent ACD queue with full session context.

    Returns:
        dict: Response payload or error envelope.
    """
    if not reason:
        return {
            "error": "INVALID_INPUT",
            "message": "Escalation reason is required for live agent handover.",
            "agent_action": "Specify reason for handover before escalating.",
        }
    queue = "ACD-General-Queue"
    if "billing" in reason.lower():
        queue = "ACD-Billing-Queue"
    elif "tech" in reason.lower() or "outage" in reason.lower():
        queue = "ACD-TechSupport-Queue"
    elif "fraud" in reason.lower():
        queue = "ACD-Fraud-Queue"
    elif "business" in reason.lower():
        queue = "ACD-Business-Queue"
    return {
        "handover_id": "HO-99182",
        "queue": queue,
    }
