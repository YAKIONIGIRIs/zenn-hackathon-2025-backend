import vertexai
from vertexai.generative_models import GenerationConfig, GenerativeModel

# Vertex AI の初期化
PROJECT_ID = "ykongrs-zenn-hackathon-2025"
vertexai.init(project=PROJECT_ID, location="us-central1")

# 応答のスキーマ定義
response_schema = {
    "type": "object",
    "properties": {
        "tts_summary": {
            "type": "string",
            "description": "会議の内容を自然な会話調で要約したもの",
        },
        "bullet_points": {
            "type": "array",
            "items": {"type": "string"},
            "description": "会議の重要ポイントを箇条書きにしたもの",
        },
        "action_items": {
            "type": "array",
            "items": {"type": "string"},
            "description": "会議で決定されたアクションアイテム",
        },
    },
    "required": ["tts_summary", "bullet_points", "action_items"],
}


class MeetingSummarizer:
    def __init__(self):
        self.model = GenerativeModel("gemini-1.5-pro-002")

    def summarize(self, meeting_text: str) -> dict:
        """
        会議内容を要約する

        Args:
            meeting_text: 会議の内容テキスト

        Returns:
            dict: 生成された要約（TTSサマリー、箇条書き、アクションアイテム）
        """
        prompt = f"""
        以下の会議内容を要約してください。
        - 全体の要約は自然な日本語で
        - 重要なポイントは箇条書きで
        - アクションアイテムは具体的なTodoとして

        会議内容:
        {meeting_text}
        """

        response = self.model.generate_content(
            prompt,
            generation_config=GenerationConfig(response_mime_type="application/json", response_schema=response_schema),
        )

        return response.text
