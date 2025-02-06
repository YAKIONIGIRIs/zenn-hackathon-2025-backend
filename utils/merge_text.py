import difflib

def merge(original_text, new_text):
    matcher = difflib.SequenceMatcher(None, original_text, new_text)
    matching_blocks = matcher.get_matching_blocks()

    # Extract matching text only first block
    index_match_head = matching_blocks[0].a
    
    archive_text = new_text
    confirmed_text = original_text[:index_match_head]

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
        "まま文章を終了します。ありがとうございました。",
        ""
    ]

    # Test
    for get_text in test_list:
        new_text = get_text

        print("original_text: {}, new_text: {}".format(original_text, new_text))
        confirmed_text, archive_text = merge(original_text, new_text)
        
        print("confirmed_text: {}".format(confirmed_text))
        print("archive_text: {}".format(archive_text))

        confirmed_buffer += confirmed_text
        original_text = archive_text

    print("confirmed_buffer: {}".format(confirmed_buffer))