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
check_regional_outage — Backend Capability Tool
"""

from typing import Dict, Any


def check_regional_outage(region: str = "", lob: str = "") -> Dict[str, Any]:
    """Check network grid for active outages by region and line of business.

    Returns:
        dict: Response payload or error envelope.
    """
    if not region:
        return {
            "error": "INVALID_INPUT",
            "message": "Region is required to check regional outages.",
            "agent_action": "Determine customer service region from profile before checking outage.",
        }
    mock_mode = str(context.state.get("mock_mode", "False")).lower() == "true"
    if region == "Region-C":
        return {
            "active": True,
            "restoration_eta_iso": "2026-10-28T18:00:00Z",
        }
    return {
        "active": False,
        "restoration_eta_iso": "",
    }
