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
fetch_recent_bills — Backend Capability Tool
"""

from typing import Dict, Any


def fetch_recent_bills(billing_account: str = "") -> Dict[str, Any]:
    """Fetch billing history and line items for an account.

    Returns:
        dict: Response payload or error envelope.
    """
    if not billing_account:
        return {
            "error": "INVALID_INPUT",
            "message": "Billing account identifier is required.",
            "agent_action": "Ask caller for their billing account number.",
        }
    return {
        "bills": [
            {
                "id": "BILL-10492",
                "date": "2026-10-15",
                "amount": "$85.50",
                "line_items": [
                    {"id": "LI-101", "description": "Broadband Internet Ultra", "amount": "$60.00"},
                    {"id": "LI-102", "description": "AppleStreaming Subscription", "amount": "$12.50"},
                    {"id": "LI-103", "description": "Taxes and Regulatory Fees", "amount": "$13.00"}
                ]
            }
        ]
    }
