import os
import json
import sys

import vertexai
from vertexai.generative_models import GenerationConfig, GenerativeModel

# Set the project and location
project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
location = os.getenv('GOOGLE_CLOUD_REGION')

# Initialize Vertex AI
vertexai.init(project=project_id, location=location)
model = GenerativeModel("gemini-1.5-flash-002")

def word_extraction(role: str, text: str) -> list[dict]:
    """
    Ask Gemini to extract words that need additional information
    :param text: str
    :return: response: list[dict]
    """
    response_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {"word": {"type": "string"}, "description": {"type": "string"}},
            "required": ["word", "description"],
        },
    }
    ask_sentence = f"""
        下記文章には補足が必要な単語がある可能性があります。
        - 補足が必要な単語を抽出してください。
        - 各単語ごとに補足を書いてください。
        - 読み手が{role}であるため、抽出する単語に注意してください。
        【文章】
        {text}
    """

    # This function should call the Gemini API to get the words that need additional information
    generation_config = GenerationConfig(response_mime_type="application/json", response_schema=response_schema)
    response = model.generate_content(ask_sentence, generation_config=generation_config)

    # Convert the response to a list of dictionaries
    response = json.loads(response.text)
    # Return the result
    return response

def adjust_text(saved_text: str, recv_text: str) -> str:
    """
    Adjust the saved text and receive the additional text
    :param saved_text: str
    :param recv_text: str
    :return: text: str
    """
    response_schema = {
        "type": "object",
        "properties": {"text": {"type": "string"}}
    }
    ask_sentence = f"""
        ストリーミングデータを受け取り、下記文章に追加する文章を生成してください。
        - 文章自体は変更をあまり加えず、体裁を整えるようにしてください。
        - 生成する文章は、受け取った文章を結合した文章としてください。改行は必要ありません。
        【結合前の文章】
        {saved_text}
        【追加する文章】
        {recv_text}
    """

    # This function should call the Gemini API to adjust the saved text and receive the additional text
    generation_config = GenerationConfig(response_mime_type="application/json", response_schema=response_schema)
    response = model.generate_content(ask_sentence, generation_config=generation_config)

    # Convert the response to a dictionary
    response = json.loads(response.text)
    
    # Check if the response contains the expected text
    if "text" in response:
        return response["text"]
    else:
        raise ValueError("Cannot get the response text. The candidate is likely blocked by the safety filters.")

def main():
    # Sample sentence
    text = """
    家賃の安さや、色んな国と人と交流が持てるとの理由が人気を呼び、今ゲストハウスを利用する人が増えて
    います。ゲストハウスを利用するメリットととしては、1つは費用面です。東京近辺でも家賃が5万円程度
    で済む場合もありますし、賃貸しのアパートやマンションでかかる、敷金や礼金も掛からないことがほとんど
    です。とにかく、家賃を安く済ませたという方には非常におすすめです。
    2つ目は出会いの場になる点です。実家を出て、一人暮らしを始めると最初は友達も出来ず、なかなか心細い
    状態になりがちです。新しい環境で積極的にいろんな人に声を掛けるのも難しいと思います。
    しかしゲストハウスはその家賃の安さから、海外の方、色んな年齢の方が利用しており、家にいながら沢山の人
    とコミュニケーションをとることが出来ます。ゲストハウスで知り合って結婚した、というカップルも少なく
    ありません。女性の方でセキュリティ面で心配に思う方がいれば、女性専用のゲストハウスに住むのもよいで
    しょう。
    ゲストハウスを利用する際の注意点としては、いろんな方が共同で暮らし、水周りを共有する事になるので、
    そのゲストハウスに設けられたルールに従わなければならないという点です。好きな時間にご飯を作ったりは
    出来ないかもしれませんし、シャワーの設置数が少ない場合は自分の好きなときに入ることはできません。
    もちろん共同で使いますので、汚したり散らかしたりするのはご法度。あとの人が気持ちよく使えるよう、
    共同施設は綺麗に使う必要があります。また、これはゲストハウスに限ったことではありませんが、友達を
    連れてきて夜中まで騒ぐなども出来ません。
    このように一緒に暮らす人に迷惑をかけないように生活しなければなりませんので、自分の思い通りにしたい人
    にはあまり向きません。ゲストハウスは良い点も沢山ありますが、共同生活ならではの注意点もあります。
    ゲストハウスで暮らすことを検討する際には、この暮らしのスタイルが本当に自分にあっているかどうかをまず
    確かめてからにするようにしましょう。
    """

    role = "主婦"

    # Example usage
    response = word_extraction(role, text)
    print(response)

    role = "不動産経営者"

    # Example usage
    response = word_extraction(role, text)
    print(response)
    
if __name__ == "__main__":
    main()
