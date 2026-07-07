import json
import time

from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY
from src.prompts import (
    INSPECTION_EXTRACTION_PROMPT,
    THERMAL_EXTRACTION_PROMPT,
)


class AIExtractor:

    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = "gemini-2.5-flash"

    def _generate_json(self, prompt):

        last_exception = None

        for attempt in range(3):

            try:

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0,
                        response_mime_type="application/json",
                    ),
                )

                return json.loads(response.text)

            except Exception as e:

                last_exception = e

                print(f"\nAttempt {attempt + 1} failed")
                print(type(e).__name__)
                print(e)

                time.sleep(2)

        raise last_exception

    def extract_inspection_chunk(self, chunk):

        document = f"""
Pages:
{chunk["pages"]}

Inspection Report:

{chunk["text"]}
"""

        prompt = INSPECTION_EXTRACTION_PROMPT.replace(
            "<<DOCUMENT>>",
            document,
        )

        return self._generate_json(prompt)

    def extract_thermal_chunk(self, chunk):

        document = f"""
Pages:
{chunk["pages"]}

Thermal Report:

{chunk["text"]}
"""

        prompt = THERMAL_EXTRACTION_PROMPT.replace(
            "<<DOCUMENT>>",
            document,
        )

        return self._generate_json(prompt)