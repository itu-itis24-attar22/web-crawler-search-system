import re

def normalize_word(word: str) -> str:
    word = word.lower().strip()
    word = re.sub(r'[^a-z0-9]', '', word)
    return word if word else ""

def tokenize_text(text: str) -> list[str]:
    text = text.lower()
    raw_tokens = re.split(r'[^a-z0-9]+', text)
    tokens = []
    for t in raw_tokens:
        t = normalize_word(t)
        if len(t) >= 2:
            tokens.append(t)
    return tokens

def count_words(text: str) -> dict:
    tokens = tokenize_text(text)
    counts = {}
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1
    return counts
