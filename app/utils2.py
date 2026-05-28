import re

def clean_text(text):

    if not text:
        return ""

    # Remove URLs
    text = re.sub(r'http\S+|www\S+', ' ', text)

    # Remove excessive whitespace/newlines/tabs
    text = re.sub(r'\s+', ' ', text)

    # Remove repeated special characters
    text = re.sub(r'[-=]{2,}', ' ', text)

    # Keep useful punctuation for LLM understanding
    text = re.sub(r'[^\w\s.,:;!?()/#+-]', ' ', text)

    # Final whitespace cleanup
    text = text.strip()

    return text

