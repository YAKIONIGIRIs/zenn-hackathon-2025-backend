import difflib

def merge(original_text, new_text):
    archive_text = ""
    confirmed_text = ""

    # Remove punctuation marks from the texts for comparison
    punctuation_marks = "、。！？"
    translation_table = str.maketrans("", "", punctuation_marks)
    original_text_no_punctuation = original_text.translate(translation_table)
    new_text_no_punctuation = new_text.translate(translation_table)


    matcher = difflib.SequenceMatcher(None, original_text_no_punctuation, new_text_no_punctuation)
    longest_match = matcher.find_longest_match(0, len(original_text_no_punctuation), 0, len(new_text_no_punctuation))
    print("longest_match: {}".format(longest_match))

    if longest_match.b != 0:
        archive_text = new_text_no_punctuation
        confirmed_text = original_text_no_punctuation

    else:
        # Extract matching text only first block
        index_match_head = longest_match.a
        index_match_tail = longest_match.a + longest_match.size
        print("match: {}".format(original_text_no_punctuation[index_match_head:index_match_tail]))
        
        archive_text = new_text_no_punctuation
        confirmed_text = original_text_no_punctuation[:index_match_head]

    return confirmed_text, archive_text

if __name__ == "__main__":
    # Test list
    original_text = ""
    new_text = ""
    confirmed_buffer = ""
    test_list = [
        "変更前の文字列です。この文字列は語尾だけ変更されます",
        "文字列です。この文字列は語尾だけ変更されました。変更後の文字列です",
        "文字列です。この文字列は語尾だけ変更されました。変更後の文字列です",
        "語尾だけ変更されました。変更後の文字列です。このまま文章を終了します。あり",
        "まま文章を終了します。ありがとうございました。今後",
        "。今後ともよろしくお願いいたします。",
        "。うれしいです。",
        ""
    ]

    # Test
    for get_text in test_list:
        new_text = get_text

        # print("original_text: {}, new_text: {}".format(original_text, new_text))
        confirmed_text, archive_text = merge(original_text, new_text)
        
        # print("confirmed_text: {}".format(confirmed_text))
        # print("archive_text: {}".format(archive_text))

        confirmed_buffer += confirmed_text
        original_text = archive_text

    print("confirmed_buffer: {}".format(confirmed_buffer))