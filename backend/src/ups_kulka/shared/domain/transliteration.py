"""Official Ukrainian-Latin transliteration (Cabinet of Ministers resolution No. 55, 2010).

Used to build URL slugs from Ukrainian names, e.g. "Рожевий шик" -> "rozhevyi-shyk".
"""

import re

_BASE = {
    "а": "a", "б": "b", "в": "v", "г": "h", "ґ": "g", "д": "d", "е": "e", "є": "ie",
    "ж": "zh", "з": "z", "и": "y", "і": "i", "ї": "i", "й": "i", "к": "k", "л": "l",
    "м": "m", "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "kh", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "shch", "ь": "",
    "ю": "iu", "я": "ia",
    # Russian-only letters that still appear in legacy product names.
    "ё": "io", "ы": "y", "э": "e", "ъ": "",
}  # fmt: skip
# Letters spelled differently at the start of a word.
_WORD_START = {"є": "ye", "ї": "yi", "й": "y", "ю": "yu", "я": "ya"}
_APOSTROPHES = "'ʼ’`"  # Ukrainian apostrophe variants
_NON_SLUG = re.compile(r"[^a-z0-9]+")


def transliterate(text: str) -> str:
    result: list[str] = []
    previous = ""
    for char in text.lower():
        if char in _APOSTROPHES:
            continue
        at_word_start = not previous.isalpha()
        if char == "г" and previous == "з":
            result.append("gh")  # "зг" -> "zgh" to keep it apart from "ж" (zh)
        elif at_word_start and char in _WORD_START:
            result.append(_WORD_START[char])
        else:
            result.append(_BASE.get(char, char))
        previous = char
    return "".join(result)


def to_slug(text: str) -> str:
    """Lower-case Latin slug: letters, digits and single hyphens."""
    return _NON_SLUG.sub("-", transliterate(text)).strip("-")
