"""FAQ loading and TF-IDF matching for the FinERP educational assistant."""

import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from preprocess import get_preprocessing_steps, preprocess_text

DATA_FILE = Path(__file__).parent / "data" / "faqs.json"
SIMILARITY_THRESHOLD = 0.50
RELATED_QUESTION_LIMIT = 3
FALLBACK_RESPONSE = (
    "I couldn't find a close enough FAQ for that question.\n\n"
    "Try asking about:\n"
    "• Accounting\n"
    "• Financial statements\n"
    "• Finance\n"
    "• ERP\n"
    "• Business processes\n"
    "• VAT fundamentals"
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
    preprocessing_steps = get_preprocessing_steps(user_query)
    processed_query = preprocessing_steps["processed_text"]
    query_vector = vectorizer.transform([processed_query])
    similarity_scores = cosine_similarity(query_vector, faq_vectors)[0]
    best_match_index = int(similarity_scores.argmax())
    matched_faq = faqs[best_match_index]
    return {
        "matched_question": matched_faq["question"],
        "answer": matched_faq["answer"],
        "category": matched_faq["category"],
        "similarity_score": float(similarity_scores[best_match_index]),
        "processed_query": processed_query,
        "preprocessing_steps": preprocessing_steps,
        "matched_index": best_match_index,
    }


def get_related_questions(matched_index, faqs, faq_vectors, limit=RELATED_QUESTION_LIMIT):
    """Return nearby FAQ questions, prioritizing the matched FAQ category."""
    if matched_index is None:
        return []

    matched_faq = faqs[matched_index]
    scores = cosine_similarity(faq_vectors[matched_index], faq_vectors)[0]
    candidates = []

    for index, score in enumerate(scores):
        if index == matched_index:
            continue
        same_category = faqs[index]["category"] == matched_faq["category"]
        candidates.append((same_category, float(score), index))

    candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [faqs[index]["question"] for _, _, index in candidates[:limit]]


def _empty_result(response, processed_query="", preprocessing_steps=None):
    return {
        "response": response,
        "matched_question": None,
        "category": None,
        "similarity_score": None,
        "is_confident_match": False,
        "processed_query": processed_query,
        "preprocessing_steps": preprocessing_steps,
        "keywords": [],
        "related_questions": [],
        "similarity_threshold": SIMILARITY_THRESHOLD,
    }


def get_chatbot_response(user_query):
    """Return a safe, UI-ready response dictionary for one user query."""
    if not isinstance(user_query, str) or not user_query.strip():
        return _empty_result(EMPTY_QUERY_RESPONSE)

    preprocessing_steps = get_preprocessing_steps(user_query)
    if not preprocessing_steps["processed_text"]:
        return _empty_result(
            EMPTY_QUERY_RESPONSE,
            processed_query="",
            preprocessing_steps=preprocessing_steps,
        )

    best_match = find_best_match(user_query, FAQS, VECTORIZER, FAQ_VECTORS)
    common_details = {
        "processed_query": best_match["processed_query"],
        "preprocessing_steps": best_match["preprocessing_steps"],
        "keywords": best_match["preprocessing_steps"]["lemmatized_tokens"],
        "similarity_threshold": SIMILARITY_THRESHOLD,
    }

    if best_match["similarity_score"] < SIMILARITY_THRESHOLD:
        return {
            "response": FALLBACK_RESPONSE,
            "matched_question": None,
            "category": None,
            "similarity_score": best_match["similarity_score"],
            "is_confident_match": False,
            "related_questions": [],
            **common_details,
        }

    return {
        "response": best_match["answer"],
        "matched_question": best_match["matched_question"],
        "category": best_match["category"],
        "similarity_score": best_match["similarity_score"],
        "is_confident_match": True,
        "related_questions": get_related_questions(
            best_match["matched_index"], FAQS, FAQ_VECTORS
        ),
        **common_details,
    }


FAQS = load_faqs()
VECTORIZER, FAQ_VECTORS, PROCESSED_FAQ_QUESTIONS = build_faq_vectorizer(FAQS)


if __name__ == "__main__":
    print(f"Loaded and vectorized {len(FAQS)} FAQ questions.")
    print(f"TF-IDF vocabulary size: {len(VECTORIZER.get_feature_names_out())}")
    print(f"Similarity threshold: {SIMILARITY_THRESHOLD:.2f}\n")
    for query in [
        "What is the accounting equation?",
        "What does a company own?",
        "What's the difference between revenue and profit?",
        "customer owes us money",
        "What is ERP?",
        "What does P2P mean?",
        "What is the weather in Beirut?",
        "",
    ]:
        result = get_chatbot_response(query)
        print(query, "->", result["response"])
        print("Related:", result["related_questions"])
        print("-" * 60)
