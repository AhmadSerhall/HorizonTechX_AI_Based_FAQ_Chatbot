"""FAQ loading and TF-IDF matching for the HorizonTechX FAQ chatbot."""

import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from preprocess import preprocess_text


DATA_FILE = Path(__file__).parent / "data" / "faqs.json"


def load_faqs(file_path=DATA_FILE):
    """Load and return the FAQ list stored in the JSON dataset."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def build_faq_vectorizer(faqs):
    """Preprocess FAQ questions and create their TF-IDF vectors."""
    faq_questions = [faq["question"] for faq in faqs]
    processed_questions = [preprocess_text(question) for question in faq_questions]

    vectorizer = TfidfVectorizer()
    faq_vectors = vectorizer.fit_transform(processed_questions)

    return vectorizer, faq_vectors, processed_questions


def find_best_match(user_query, faqs, vectorizer, faq_vectors):
    """Return the FAQ with the highest cosine-similarity score for a user query."""
    processed_query = preprocess_text(user_query)
    query_vector = vectorizer.transform([processed_query])
    similarity_scores = cosine_similarity(query_vector, faq_vectors)[0]

    best_match_index = similarity_scores.argmax()
    matched_faq = faqs[best_match_index]

    return {
        "matched_question": matched_faq["question"],
        "answer": matched_faq["answer"],
        "category": matched_faq["category"],
        "similarity_score": float(similarity_scores[best_match_index]),
    }


def print_match_result(user_query, result):
    """Print one match result clearly for manual Phase 3 testing."""
    print(f"User query:\n{user_query}")
    print(f"\nBest matched FAQ:\n{result['matched_question']}")
    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nCategory:\n{result['category']}")
    print(f"\nSimilarity score:\n{result['similarity_score']:.2f}")


if __name__ == "__main__":
    faqs = load_faqs()
    vectorizer, faq_vectors, processed_questions = build_faq_vectorizer(faqs)

    print(f"Loaded and vectorized {len(faqs)} FAQ questions.")
    print(f"TF-IDF vocabulary size: {len(vectorizer.get_feature_names_out())}\n")

    test_queries = [
        "How do I download my certificate?",
        "Can I study using my phone?",
        "certificate after course",
    ]

    for query in test_queries:
        result = find_best_match(query, faqs, vectorizer, faq_vectors)
        print_match_result(query, result)
        print("\n" + "-" * 60 + "\n")
