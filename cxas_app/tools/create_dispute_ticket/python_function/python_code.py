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
create_dispute_ticket — Backend Capability Tool
"""

from typing import Dict, Any


def create_dispute_ticket(charge_id: str = "", reason: str = "", notes: str = "") -> Dict[str, Any]:
    """Create a formal dispute ticket for a questioned charge.

    Returns:
        dict: Response payload or error envelope.
    """
    if not charge_id:
        return {
            "error": "INVALID_INPUT",
            "message": "charge_id is required to open a dispute case.",
            "agent_action": "Identify the charge on the bill before creating dispute ticket.",
        }
    return {
        "ticket_id": "DISP-88201",
        "eta_business_days": 3,
    }
