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
after_model_callback — PII Redaction & Verbatim Compliance
"""

import re
from typing import Optional, Dict, Any, List


def after_model_callback(callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]:
    state = callback_context.state

    # 1. Inspect generated parts
    modified = False
    new_parts = []

    for part in llm_response.content.parts:
        text = part.text_or_transcript() if hasattr(part, "text_or_transcript") else part.text
        if text:
            # PII Redaction Audit (BR-TV-009): Redact 10-digit BAN / phone numbers to last 4
            masked_text = re.sub(r"\b(\d{6})(\d{4})\b", r"ending in \2", text)
            if masked_text != text:
                modified = True
                new_parts.append(Part.from_text(text=masked_text))
            else:
                new_parts.append(part)
        else:
            new_parts.append(part)

    if modified:
        return LlmResponse.from_parts(parts=new_parts)

    return None
