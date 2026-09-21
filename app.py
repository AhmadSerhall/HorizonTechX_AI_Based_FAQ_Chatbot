"""Streamlit interface for the HorizonTechX Learning Assistant."""

import streamlit as st

from chatbot import get_chatbot_response


WELCOME_MESSAGE = (
    "Hello! I'm the HorizonTechX Learning Assistant. "
    "Ask me about courses, certificates, accounts, payments, technical support, "
    "or learning paths."
)


def reset_conversation():
    """Reset the chat to its initial assistant welcome message."""
    st.session_state.messages = [
        {"role": "assistant", "content": WELCOME_MESSAGE, "details": None}
    ]


def show_match_details(details):
    """Display optional developer information for one assistant response."""
    with st.expander("Match details"):
        if details["is_confident_match"]:
            st.write(f"**Matched FAQ:** {details['matched_question']}")
            st.write(f"**Category:** {details['category']}")
            st.write(f"**Similarity score:** {details['similarity_score']:.2f}")
        elif details["similarity_score"] is None:
            st.write("No match was calculated because the input was empty.")
        else:
            st.write("No FAQ match passed the similarity threshold.")
            st.write(f"**Highest similarity score:** {details['similarity_score']:.2f}")


st.set_page_config(
    page_title="HorizonTechX Learning Assistant",
    page_icon="🎓",
    layout="centered",
)

if "messages" not in st.session_state:
    reset_conversation()

with st.sidebar:
    st.header("About")
    st.write(
        "A FAQ chatbot for HorizonTechX Learning Hub. It uses NLP, TF-IDF, "
        "and cosine similarity to find relevant answers."
    )

    st.divider()
    st.subheader("What you can ask about")
    st.write("Courses, certificates, accounts, payments, technical support, and learning paths.")

    st.subheader("Example questions")
    st.caption("How do I download my certificate?")
    st.caption("Can I study using my phone?")
    st.caption("How can I reset my password?")

    st.divider()
    show_match_details_enabled = st.checkbox("Show match details")

    if st.button("Clear conversation", use_container_width=True):
        reset_conversation()
        st.rerun()

st.title("HorizonTechX Learning Assistant")
st.caption(
    "Ask questions about the learning platform, courses, accounts, certificates, "
    "payments, and related FAQs."
)
st.divider()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if (
            message["role"] == "assistant"
            and show_match_details_enabled
            and message.get("details") is not None
        ):
            show_match_details(message["details"])

if user_query := st.chat_input("Ask a question about HorizonTechX Learning Hub..."):
    st.session_state.messages.append({"role": "user", "content": user_query})

    with st.chat_message("user"):
        st.write(user_query)

    chatbot_result = get_chatbot_response(user_query)
    assistant_message = {
        "role": "assistant",
        "content": chatbot_result["response"],
        "details": chatbot_result,
    }
    st.session_state.messages.append(assistant_message)

    with st.chat_message("assistant"):
        st.write(chatbot_result["response"])
        if show_match_details_enabled:
            show_match_details(chatbot_result)
