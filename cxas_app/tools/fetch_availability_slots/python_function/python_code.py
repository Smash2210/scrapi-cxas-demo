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
fetch_availability_slots — Backend Capability Tool
"""

from typing import Dict, Any


def fetch_availability_slots(zip: str = "", service_type: str = "") -> Dict[str, Any]:
    """Query dispatch system for available technician appointment windows.

    Returns:
        dict: Response payload or error envelope.
    """
    if not zip and not service_type:
        return {
            "error": "INVALID_INPUT",
            "message": "Postal zip or service type is required to query technician slots.",
            "agent_action": "Ask caller for their postal zip code or service type.",
        }
    return {
        "slots": [
            {"date": "2026-10-29", "window": "08:00-12:00", "technician_id": "TECH-401"},
            {"date": "2026-10-29", "window": "13:00-17:00", "technician_id": "TECH-402"},
            {"date": "2026-10-30", "window": "08:00-12:00", "technician_id": "TECH-403"}
        ]
    }
