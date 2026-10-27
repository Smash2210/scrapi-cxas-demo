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
evaluate_routing_rules — Backend Capability Tool
"""

from typing import Dict, Any


def evaluate_routing_rules(utterance: str = "", entities: dict = {}) -> Dict[str, Any]:
    """Classify caller utterance to resolve routing destination and auth requirements.

    Returns:
        dict: Response payload or error envelope.
    """
    if not utterance:
        return {
            "error": "INVALID_INPUT",
            "message": "Utterance text is required for routing evaluation.",
            "agent_action": "Ask caller how you can help them today.",
        }
    text = utterance.lower()
    if any(k in text for k in ["bill", "charge", "payment", "autopay", "refund", "credit", "dispute"]):
        return {"route": "billing", "confidence": 0.95, "requires_auth": True}
    elif any(k in text for k in ["internet", "wifi", "signal", "tv", "cable", "repair", "outage", "broken"]):
        return {"route": "tech", "confidence": 0.95, "requires_auth": True}
    elif any(k in text for k in ["sales", "plan", "upgrade", "order", "buy", "phone", "device", "warranty"]):
        return {"route": "sales", "confidence": 0.92, "requires_auth": False}
    elif any(k in text for k in ["appointment", "technician", "schedule", "reschedule", "visit"]):
        return {"route": "appointments", "confidence": 0.94, "requires_auth": True}
    elif any(k in text for k in ["password", "reset", "suspend", "restore", "fraud", "mfa", "login", "account"]):
        return {"route": "account", "confidence": 0.95, "requires_auth": False}
    return {"route": "general", "confidence": 0.70, "requires_auth": False}
