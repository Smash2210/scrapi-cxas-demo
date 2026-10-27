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
execute_suspend_restore — Backend Capability Tool
"""

from typing import Dict, Any


def execute_suspend_restore(cirn: str = "", action: str = "", reason: str = "") -> Dict[str, Any]:
    """Suspend or restore account service state.

    Returns:
        dict: Response payload or error envelope.
    """
    if not cirn or not action:
        return {
            "error": "INVALID_INPUT",
            "message": "cirn and action (suspend or restore) are required.",
            "agent_action": "Clarify requested service action with the customer.",
        }
    return {
        "new_state": "active" if action.lower() == "restore" else "suspended",
        "effective_iso": "2026-10-27T18:00:00Z",
    }
