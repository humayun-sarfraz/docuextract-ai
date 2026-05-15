import json
import logging
from openai import OpenAI, APITimeoutError, APIError
from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.schemas import FieldDefinition

logger = logging.getLogger("docuextract.ai")

SYSTEM_PROMPT = (
    "You are a document data extraction assistant. "
    "Extract only the requested fields from the provided document text. "
    "Do not invent values. If a field is not present, return null. "
    "Always return valid JSON. "
    "For each field, include value, confidence from 0 to 1, and a short evidence snippet from the document when available."
)

MAX_RETRIES = 2
TIMEOUT_SECONDS = 60


def extract_fields(document_text: str, fields: list[FieldDefinition]) -> dict:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not configured. Set it in your .env file.")

    client = OpenAI(api_key=OPENAI_API_KEY, timeout=TIMEOUT_SECONDS)

    fields_description = [
        {
            "name": f.name,
            "description": f.description,
            "type": f.type.value,
            "required": f.required,
        }
        for f in fields
    ]

    user_prompt = f"""Document text:
---
{document_text[:15000]}
---

Extract the following fields and return a JSON object where each key is the field name and the value is an object with "value", "confidence" (0 to 1), and "evidence" (short snippet from the document).

Fields to extract:
{json.dumps(fields_description, indent=2)}

Return ONLY valid JSON, no markdown, no explanation. Example format:
{{
  "field_name": {{
    "value": "extracted value or null",
    "confidence": 0.95,
    "evidence": "relevant text snippet"
  }}
}}"""

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info("AI extraction attempt %d/%d (model=%s)", attempt, MAX_RETRIES, OPENAI_MODEL)
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            result = json.loads(content)
            logger.info("AI extraction succeeded: %d fields returned", len(result))
            return result

        except json.JSONDecodeError as e:
            last_error = e
            logger.warning("AI returned invalid JSON on attempt %d: %s", attempt, e)
        except APITimeoutError as e:
            last_error = e
            logger.warning("OpenAI API timeout on attempt %d", attempt)
        except APIError as e:
            last_error = e
            logger.error("OpenAI API error on attempt %d: %s", attempt, e.message)

    raise RuntimeError(f"AI extraction failed after {MAX_RETRIES} attempts: {last_error}")
