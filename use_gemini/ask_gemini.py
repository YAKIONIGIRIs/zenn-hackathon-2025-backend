import requests
import json
import sys

from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel, ChatSession

project_id = "ykongrs-zenn-hackathon-2025"
location = "us-central1"

class GeminiHelper:
    def __init__(self):
        self.input_text = ""

        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=location)
        self.model = GenerativeModel("gemini-1.5-flash-002")
        self.chat = self.model.start_chat()

    def add_text(self, text: str):
        self.input_text += text

    def ask_gemini(self, text: str):
        ask_sentence = "下記文章から補足が必要な単語だけをJSON形式のwords配列で返して。\n" + text
        # This function should call the Gemini API to get the words that need additional information
        response = self.chat.send_message(ask_sentence, stream=False)
        print(response)
        # Assuming the response is a JSON string
        response_json = json.loads(response.text)
        # Extract the words that need additional information
        words = response_json.get("words", [])
        return words

    def get_additional_info(self, words: list):
        # This function should call the Gemini API to get additional information for each word
        descriptions = []
        for word in words:
            ask_sentence = f"単語 '{word}' の補足情報を端的に教えて。"
            response = self.chat.send_message(ask_sentence, stream=False, response_schema)
            print(response)
            # logging.info(response)
            description = response.json().get("description", "")
            descriptions.append({"word": word, "description": description})
        return descriptions

    def process_text(self):
        words = self.ask_gemini(self.input_text)
        additional_info = self.get_additional_info(words)
        return additional_info

def main():
    input_data = json.load(sys.stdin)
    text = input_data.get("text", "")

    gemini_helper = GeminiHelper()
    gemini_helper.add_text(text)
    result = gemini_helper.process_text()

    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()