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
fetch_plan_catalog — Backend Capability Tool
"""

from typing import Dict, Any


def fetch_plan_catalog(lob: str = "", customer_type: str = "") -> Dict[str, Any]:
    """Retrieve available service rate plans from sales catalog.

    Returns:
        dict: Response payload or error envelope.
    """
    if not lob and not customer_type:
        return {
            "error": "INVALID_INPUT",
            "message": "Line of business or customer type is required to fetch catalog.",
            "agent_action": "Ask caller which product or service line they want to explore.",
        }
    return {
        "plans": [
            {
                "id": "PLAN-ULTRA-TV",
                "name": "Ultra Streaming TV",
                "price": "$65/mo",
                "key_features": "150+ live channels, 4K streaming, cloud DVR included"
            },
            {
                "id": "PLAN-PREMIER-TV",
                "name": "Premier Satellite TV",
                "price": "$85/mo",
                "key_features": "250+ live channels, premium sports pass, whole-home DVR"
            }
        ]
    }
