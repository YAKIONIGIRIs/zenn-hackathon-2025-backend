import json
import sys

import vertexai
from vertexai.generative_models import GenerationConfig, GenerativeModel

project_id = "ykongrs-zenn-hackathon-2025"
location = "us-central1"

class GeminiHelper:
    def __init__(self):
        self.input_text = ""
        self.word_list = []

        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel("gemini-1.5-flash-002")

    def add_text(self, text: str) -> None:
        self.input_text += text

    def ask_gemini(self) -> list[dict]:
        return_data = []

        response_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "word": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["word", "description"]
            }
        }
        ask_sentence = f"""
            下記文章には補足が必要な単語がある可能性があります。
            - 補足が必要な単語を抽出してください。
            - 各単語ごとに補足を書いてください。
            【文章】
            {self.input_text}
        """

        # This function should call the Gemini API to get the words that need additional information
        generation_config = GenerationConfig(
            response_mime_type="application/json",
            response_schema=response_schema
        )
        response = self.model.generate_content(ask_sentence, generation_config=generation_config)
        print(response.text)
        # Assuming the response is a JSON string
        response_json = json.loads(response.text)
        # Extract the words that need additional information
        for word_data in response_json:
            if (word_data["word"] in self.word_list):
                pass
            else:
                return_data.append(word_data)
                self.word_list.append(word_data["word"])
        return return_data

def main():
    input_data = json.load(sys.stdin)
    text = input_data.get("text", "")

    gemini_helper = GeminiHelper()
    gemini_helper.add_text(text)
    result = gemini_helper.ask_gemini()

    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()