# utf-8로 쓰지 못하는 특수문자가 들어왔을 때 이를 적절하게 치환
def replace_special_characters(file_path):
    special_characters = {
        ',': '',
        '/': '_',
        '\\': '_',
        '|': '_',
        '?': '',
        '*': '',
        '<': '',
        '>': '',
        '\n': '',
        '\\n': '',
        ':': '',
        '"': '',
        "'": ''
    }

    for char, replacement in special_characters.items():
        file_path = file_path.replace(char, replacement)

    return file_path
