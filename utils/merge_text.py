import MeCab

# 形態素解析の初期化
mecab = MeCab.Tagger()

# 形態素解析して単語のリストを取得
def tokenize(text):
    parsed = mecab.parse(text)
    return [line.split("\t")[0] for line in parsed.splitlines() if "\t" in line]

def merge(meetId: str, comparison_text: str, new_text: str) -> str:
    """
    
    """
    # 返り値の初期化
    confirmed_text = ""
    archive_text = ""

    # 既存の重複検知用バッファと新しいテキストを形態素解析
    existing_tokens = tokenize(comparison_text)
    new_tokens = tokenize(new_text)
    if len(existing_tokens) == 0:
        existing_tokens = [""] # 重複検知用バッファが空の場合の対策
    if len(new_tokens) == 0:
        new_tokens = [""] # 新しいテキストが空の場合の対策

    # 重複部分の検出
    overlap_index = 0
    flag = 0
    for index, existing_token in enumerate(existing_tokens):
        # 消えたトークンを検知
        if flag == 0:
            if existing_token == new_tokens[0]:
                overlap_index = index
                flag = 1
        elif flag == 1 and flag == 2:
            if existing_token == new_tokens[flag]:
                flag += 1
            else:
                flag = 0
                overlap_index = 0
        elif flag == 3:
            break
        else:
            pass

    # 消えたトークンを文章確定用変数に追加
    if overlap_index > 0:
        confirmed_text += "".join(existing_tokens[:overlap_index])
    elif overlap_index == 0 and new_tokens[0] == "":
        confirmed_text += comparison_text

    # 重複検知用のバッファを新しいテキストで更新（新しい情報を優先）
    archive_text = new_text

    return [confirmed_text, archive_text]

if __name__ == "__main__":
    # 送られてくるテキスト例
    texts = [
        "",
        "これは最初の文です。次に続く内容があります。",
        "次に続く内容があります。さらに新しい情報も追加されます。",
        "さらに新しい情報も追加されます。最後の部分です。",
        ""
    ]

    # 初期の比較テキスト
    comparison_text = texts[0]
    meetId = "example_meet_id"

    for new_text in texts[1:]:
        confirmed_text, archive_text = merge(meetId, comparison_text, new_text)
        print("Confirmed Text: ", confirmed_text)
        print("Archive Text: ", archive_text)
        comparison_text = archive_text

