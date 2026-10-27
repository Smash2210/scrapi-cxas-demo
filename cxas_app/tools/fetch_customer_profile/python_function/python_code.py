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
fetch_customer_profile — Customer Profile Lookup Tool
"""

from typing import Dict, Any


def fetch_customer_profile(clid: str = "") -> Dict[str, Any]:
    """Look up customer account profile using the caller telephone number (CLID).

    Args:
        clid: 10-digit caller phone number.

    Returns:
        dict: Customer account profile details or structured error envelope.
    """
    if not clid:
        return {
            "error": "INVALID_INPUT",
            "message": "CLID parameter is required to fetch customer profile.",
            "agent_action": "Ask caller to provide their 10-digit telephone number or billing account number.",
        }

    mock_mode = str(context.state.get("mock_mode", "False")).lower() == "true"

    if mock_mode:
        profiles = {
            "5550100000": {
                "identification_status": "Pass",
                "customer_type": "New",
                "business_flag": "false",
                "is_prepaid": "false",
                "region": "Region-A",
                "cirn": "0000000000",
                "billing_account": "0000000000",
                "ban_type": "ConsumerPostpaid",
                "loyalty_limit": 0,
            },
            "5550118899": {
                "identification_status": "Pass",
                "customer_type": "Existing",
                "business_flag": "true",
                "is_prepaid": "false",
                "region": "Region-B",
                "cirn": "5529102837",
                "billing_account": "4440018899",
                "ban_type": "SMB",
                "loyalty_limit": 50,
            },
            "5550124982": {
                "identification_status": "Pass",
                "customer_type": "Existing",
                "business_flag": "false",
                "is_prepaid": "false",
                "region": "Region-B",
                "cirn": "8829104821",
                "billing_account": "4440024982",
                "ban_type": "ConsumerPostpaid",
                "loyalty_limit": 25,
            },
            "5550149922": {
                "identification_status": "Pass",
                "customer_type": "Existing",
                "business_flag": "false",
                "is_prepaid": "false",
                "region": "Region-A",
                "cirn": "7720194821",
                "billing_account": "4440049922",
                "ban_type": "ConsumerPostpaid",
                "loyalty_limit": 25,
            },
            "5550168391": {
                "identification_status": "Pass",
                "customer_type": "Existing",
                "business_flag": "false",
                "is_prepaid": "false",
                "region": "Region-C",
                "cirn": "6629103948",
                "billing_account": "4440068391",
                "ban_type": "ConsumerPostpaid",
                "loyalty_limit": 25,
            },
            "5550177744": {
                "identification_status": "Pass",
                "customer_type": "Existing",
                "business_flag": "false",
                "is_prepaid": "false",
                "region": "Region-B",
                "cirn": "4429107744",
                "billing_account": "4440077744",
                "ban_type": "ConsumerPostpaid",
                "loyalty_limit": 25,
            },
            "5550133311": {
                "identification_status": "Pass",
                "customer_type": "Existing",
                "business_flag": "false",
                "is_prepaid": "false",
                "region": "Region-A",
                "cirn": "3329103311",
                "billing_account": "4440033311",
                "ban_type": "ConsumerPostpaid",
                "loyalty_limit": 25,
            },
        }
        return profiles.get(
            clid,
            {
                "identification_status": "Pass",
                "customer_type": "Existing",
                "business_flag": "false",
                "is_prepaid": "false",
                "region": "Region-A",
                "cirn": "9820598207",
                "billing_account": "4440019283",
                "ban_type": "ConsumerPostpaid",
                "loyalty_limit": 25,
            },
        )

    return {
        "identification_status": "Pass",
        "customer_type": "Existing",
        "business_flag": "false",
        "is_prepaid": "false",
        "region": "Region-A",
        "cirn": "9820598207",
        "billing_account": "4440019283",
        "ban_type": "ConsumerPostpaid",
        "loyalty_limit": 25,
    }
