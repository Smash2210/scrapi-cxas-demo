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
commit_appointment_reschedule — Backend Capability Tool
"""

from typing import Dict, Any


def commit_appointment_reschedule(appt_id: str = "", new_slot: str = "") -> Dict[str, Any]:
    """Commit appointment reschedule to field service dispatch.

    Returns:
        dict: Response payload or error envelope.
    """
    if not appt_id or not new_slot:
        return {
            "error": "INVALID_INPUT",
            "message": "Both appt_id and new_slot are required to reschedule appointment.",
            "agent_action": "Confirm appointment ID and selected time slot with caller.",
        }
    return {
        "confirmed": True,
        "new_date": new_slot,
    }
