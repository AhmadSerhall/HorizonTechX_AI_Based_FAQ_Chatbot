"""Reusable NLTK text preprocessing for the FAQ chatbot."""

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

NLTK_RESOURCES = {
    "tokenizers/punkt": "punkt",
    "tokenizers/punkt_tab": "punkt_tab",
    "corpora/stopwords": "stopwords",
    "corpora/wordnet.zip": "wordnet",
    "corpora/omw-1.4.zip": "omw-1.4",
}


def ensure_nltk_resources():
    """Download required NLTK data only when it is not already installed."""
    for resource_path, package_name in NLTK_RESOURCES.items():
        try:
            nltk.data.find(resource_path)
        except LookupError:
            nltk.download(package_name, quiet=True)


ensure_nltk_resources()
STOP_WORDS = set(stopwords.words("english"))
LEMMATIZER = WordNetLemmatizer()


def get_preprocessing_steps(text):
    """Return the intermediate results used to preprocess one text string."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    lowercase_text = text.lower()
    tokens = word_tokenize(lowercase_text)
    meaningful_tokens = [
        token
        for token in tokens
        if token.isalpha()
        or (
            token.isalnum()
            and any(character.isalpha() for character in token)
            and any(character.isdigit() for character in token)
        )
    ]
    tokens_without_stopwords = [
        token for token in meaningful_tokens if token not in STOP_WORDS
    ]
    lemmatized_tokens = [
        LEMMATIZER.lemmatize(token) for token in tokens_without_stopwords
    ]

    return {
        "original": text,
        "lowercase": lowercase_text,
        "tokens": tokens,
        "meaningful_tokens": meaningful_tokens,
        "tokens_without_stopwords": tokens_without_stopwords,
        "lemmatized_tokens": lemmatized_tokens,
        "processed_text": " ".join(lemmatized_tokens),
    }


def preprocess_text(text):
    """Convert raw text into cleaned words joined by spaces for later TF-IDF use."""
    return get_preprocessing_steps(text)["processed_text"]


def print_preprocessing_steps(text):
    """Print a beginner-friendly view of each preprocessing stage."""
    steps = get_preprocessing_steps(text)
    print(f"Original sentence: {steps['original']}")
    print(f"Lowercase: {steps['lowercase']}")
    print(f"Tokenization: {steps['tokens']}")
    print(f"Remove punctuation/non-meaningful tokens: {steps['meaningful_tokens']}")
    print(f"Remove stopwords: {steps['tokens_without_stopwords']}")
    print(f"Lemmatization: {steps['lemmatized_tokens']}")
    print(f"Final processed result: {steps['processed_text']}")


if __name__ == "__main__":
    example_sentences = [
        "How do I reset my passwords for the courses?",
        "Can I download course videos on my mobile phone?",
        "Why is the course video not playing?",
        "What payment methods do you accept?",
    ]
    print("Detailed example:\n")
    print_preprocessing_steps(example_sentences[0])
    print("\nAdditional examples:")
    for sentence in example_sentences[1:]:
        print(f"- {sentence} -> {preprocess_text(sentence)}")
