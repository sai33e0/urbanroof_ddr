import json

from google import genai

from src.config import GEMINI_API_KEY
from src.prompts import DDR_GENERATION_PROMPT


class DDRGenerator:

    def __init__(self):

        self.client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        self.model = "gemini-2.5-flash"

    def generate(self, validated_data):

        prompt = DDR_GENERATION_PROMPT.format(
            data=json.dumps(
                validated_data,
                indent=2
            )
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        return response.text