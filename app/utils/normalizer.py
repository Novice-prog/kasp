from functools import lru_cache
import pymorphy3

morph = pymorphy3.MorphAnalyzer()


@lru_cache(maxsize=10000)
def normalize_word(word: str) -> str:
    return morph.parse(word)[0].normal_form