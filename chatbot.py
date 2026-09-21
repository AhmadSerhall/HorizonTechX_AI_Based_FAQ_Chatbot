"""FAQ loading and TF-IDF matching for the FinERP educational assistant."""

import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from preprocess import preprocess_text


DATA_FILE = Path(__file__).parent / "data" / "faqs.json"
SIMILARITY_THRESHOLD = 0.50

FALLBACK_RESPONSE = (
    "I'm sorry, I couldn't find a relevant answer to that question. "
    "Try asking about accounting, finance, bookkeeping, financial statements, "
    "business processes, inventory, or ERP concepts."
)

EMPTY_QUERY_RESPONSE = (
    "Please enter a question for the FinERP Learning Assistant. "
    "For example, you can ask about accounting, finance, bookkeeping, or ERP."
)


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


def get_chatbot_response(user_query):
    """Return a safe, UI-ready response dictionary for one user query."""
    if not isinstance(user_query, str) or not user_query.strip():
        return {
            "response": EMPTY_QUERY_RESPONSE,
            "matched_question": None,
            "category": None,
            "similarity_score": None,
            "is_confident_match": False,
        }

    if not preprocess_text(user_query):
        return {
            "response": EMPTY_QUERY_RESPONSE,
            "matched_question": None,
            "category": None,
            "similarity_score": None,
            "is_confident_match": False,
        }

    best_match = find_best_match(user_query, FAQS, VECTORIZER, FAQ_VECTORS)

    if best_match["similarity_score"] < SIMILARITY_THRESHOLD:
        return {
            "response": FALLBACK_RESPONSE,
            "matched_question": None,
            "category": None,
            "similarity_score": best_match["similarity_score"],
            "is_confident_match": False,
        }

    return {
        "response": best_match["answer"],
        "matched_question": best_match["matched_question"],
        "category": best_match["category"],
        "similarity_score": best_match["similarity_score"],
        "is_confident_match": True,
    }


def print_match_result(user_query, result):
    """Print one match result clearly for manual Phase 3 testing."""
    print(f"User query:\n{user_query}")
    print(f"\nBest matched FAQ:\n{result['matched_question']}")
    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nCategory:\n{result['category']}")
    print(f"\nSimilarity score:\n{result['similarity_score']:.2f}")


def print_chatbot_response(user_query, result):
    """Print one Phase 4 chatbot response clearly for manual testing."""
    print(f"User query:\n{user_query!r}")
    print(f"\nResponse:\n{result['response']}")
    print(f"\nConfident match:\n{result['is_confident_match']}")
    print(f"\nMatched FAQ:\n{result['matched_question']}")
    print(f"\nCategory:\n{result['category']}")

    if result["similarity_score"] is None:
        print("\nSimilarity score:\nNot calculated for empty input")
    else:
        print(f"\nSimilarity score:\n{result['similarity_score']:.2f}")


FAQS = load_faqs()
VECTORIZER, FAQ_VECTORS, PROCESSED_FAQ_QUESTIONS = build_faq_vectorizer(FAQS)


if __name__ == "__main__":
    print(f"Loaded and vectorized {len(FAQS)} FAQ questions.")
    print(f"TF-IDF vocabulary size: {len(VECTORIZER.get_feature_names_out())}")
    print(f"Similarity threshold: {SIMILARITY_THRESHOLD:.2f}\n")

    test_queries = [
        "What is the accounting equation?",
        "What does a company own?",
        "What's the difference between revenue and profit?",
        "customer owes us money",
        "What is ERP?",
        "What does P2P mean?",
        "What is the weather in Beirut?",
        "",
    ]

    for query in test_queries:
        result = get_chatbot_response(query)
        print_chatbot_response(query, result)
        print("\n" + "-" * 60 + "\n")
