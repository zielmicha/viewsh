import unicodedata

LETTER = 'L'
NUMBER = 'N'

def main_category(letter):
    return unicodedata.category(letter)[0]

def _prevnext_word(text, pos, direction):
    while pos < len(text) and pos >= 0 and main_category(text[pos]) not in (LETTER, NUMBER):
        # skip all non-letters
        pos += direction

    while pos < len(text) and pos >= 0 and main_category(text[pos]) in (LETTER, NUMBER):
        # skip all letters and digits
        pos += direction

    return pos

def next_word(text, pos):
    return _prevnext_word(text, pos, 1)

def prev_word(text, pos):
    return _prevnext_word(text, pos - 1, -1) + 1
