"""Streamlit interface for the FinERP Learning Assistant."""

import io
import json
import re
import time
import uuid
from datetime import datetime
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from chatbot import FAQS, get_chatbot_response


WELCOME_TITLE = "FinERP Learning Assistant"
AI_ICON = "🤖"
WELCOME_TAGLINE = (
    "Learn accounting, finance and ERP concepts through simple questions."
)
WELCOME_MESSAGE = (
    "Hi, I'm FinERP Learning Assistant.\n\n"
    f"{WELCOME_TAGLINE}\n\n"
    "Ask me about accounting, finance, bookkeeping, financial statements, "
    "business processes, and ERP concepts."
)

SUGGESTED_QUESTIONS = [
    "What is the accounting equation?",
    "What is the difference between revenue and profit?",
    "What are accounts receivable?",
    "What is ERP?",
    "What does P2P mean?",
]

TYPING_DELAY_SECONDS = 1.0
FAQ_COUNT = len(FAQS)
TOPIC_NAMES = sorted({faq["category"] for faq in FAQS})
TOPIC_COUNT = len(TOPIC_NAMES)
CONVERSATIONS_FILE = Path(__file__).parent / "data" / "conversations.json"

CUSTOM_CSS = """
<style>
    .block-container {
        max-width: 52rem;
        padding-top: 1.4rem;
        padding-bottom: 6rem;
    }

    div[data-testid="stChatMessage"] {
        background: transparent;
        padding: 0.15rem 0;
    }

    div[data-testid="stChatMessage"]:has(span[data-testid="chatAvatarIcon-user"]) {
        flex-direction: row-reverse;
        justify-content: flex-end;
    }

    div[data-testid="stChatMessage"]:has(span[data-testid="chatAvatarIcon-user"])
        [data-testid="stChatMessageContent"] {
        background: #dbeafe;
        border: 1px solid #bfdbfe;
        border-radius: 1.1rem 1.1rem 0.3rem 1.1rem;
        padding: 0.7rem 0.9rem 0.45rem 0.9rem;
        margin-left: 12%;
    }

    div[data-testid="stChatMessage"]:has(span[data-testid="chatAvatarIcon-assistant"])
        [data-testid="stChatMessageContent"] {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 1.1rem 1.1rem 1.1rem 0.3rem;
        padding: 0.7rem 0.9rem 0.45rem 0.9rem;
        margin-right: 12%;
    }

    .chat-meta {
        color: #64748b;
        font-size: 0.72rem;
        margin-top: 0.15rem;
    }

    .typing-indicator {
        display: inline-flex;
        gap: 0.35rem;
        align-items: center;
        min-height: 1.2rem;
        padding: 0.15rem 0.1rem 0.35rem 0.1rem;
    }

    .typing-indicator span {
        width: 0.42rem;
        height: 0.42rem;
        border-radius: 50%;
        background: #64748b;
        animation: typing-bounce 1.2s infinite ease-in-out;
    }

    .typing-indicator span:nth-child(2) { animation-delay: 0.15s; }
    .typing-indicator span:nth-child(3) { animation-delay: 0.3s; }

    @keyframes typing-bounce {
        0%, 80%, 100% { transform: translateY(0); opacity: 0.35; }
        40% { transform: translateY(-4px); opacity: 1; }
    }

    div[class*="st-key-suggest_"] button,
    div[class*="st-key-side_suggest_"] button {
        border-radius: 999px;
        border: 1px solid #cbd5e1;
        background: #ffffff;
        color: #1e293b;
        font-weight: 500;
        white-space: normal;
        line-height: 1.3;
        padding: 0.45rem 0.8rem;
    }

    [data-testid="stSidebar"] {
        background: #f8fafc;
    }

    .sidebar-stat {
        color: #475569;
        font-size: 0.86rem;
        line-height: 1.45;
    }

    div[class*="st-key-conversation_new_"] button {
        animation: title-reveal 0.5s steps(20, end) both;
        transform-origin: left center;
    }

    @keyframes title-reveal {
        from { clip-path: inset(0 100% 0 0); opacity: 0; }
        to { clip-path: inset(0 0 0 0); opacity: 1; }
    }
</style>
"""

TYPING_INDICATOR_HTML = """
<div class="typing-indicator" aria-label="Assistant is typing">
    <span></span><span></span><span></span>
</div>
"""


def current_timestamp():
    """Return a compact local time label such as 10:42 PM."""
    return datetime.now().strftime("%I:%M %p").lstrip("0")


def current_datetime():
    """Return a simple local timestamp for saved conversation metadata."""
    return datetime.now().isoformat(timespec="seconds")


def load_conversations():
    """Load local conversation history without failing on a missing file."""
    if not CONVERSATIONS_FILE.exists():
        return []
    try:
        with open(CONVERSATIONS_FILE, "r", encoding="utf-8") as file:
            conversations = json.load(file)
        return conversations if isinstance(conversations, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def write_conversations():
    """Persist the in-memory conversation list only after it changes."""
    CONVERSATIONS_FILE.parent.mkdir(exist_ok=True)
    with open(CONVERSATIONS_FILE, "w", encoding="utf-8") as file:
        json.dump(st.session_state.conversations, file, indent=2)


def conversation_title(question):
    """Create a compact domain title from the first user question."""
    cleaned_question = re.sub(r"[^A-Za-z0-9\s]", " ", question).lower()
    cleaned_question = " ".join(cleaned_question.split())

    def format_words(words):
        abbreviations = {"erp", "p2p", "o2c", "r2r", "fifo", "vat"}
        return " ".join(
            word.upper() if word in abbreviations else word.capitalize()
            for word in words
        )

    if "difference between" in cleaned_question:
        comparison = cleaned_question.split("difference between", 1)[1]
        if " and " in comparison:
            left, right = comparison.split(" and ", 1)
            title = f"{format_words(left.split())} vs {format_words(right.split())}"
            return title[:35].rstrip()

    filler_words = {
        "what", "is", "are", "can", "you", "explain", "tell", "me", "about",
        "how", "does", "do", "work", "mean", "please", "the", "a", "an", "to",
    }
    important_words = [
        word for word in cleaned_question.split() if word not in filler_words
    ]
    title = format_words(important_words[:5]) or "New Conversation"
    return title[:35].rstrip()


def save_active_conversation():
    """Save the selected conversation after a user or assistant message changes it."""
    user_messages = [
        message for message in st.session_state.messages if message["role"] == "user"
    ]
    if not user_messages:
        return

    updated_at = current_datetime()
    active_id = st.session_state.active_conversation_id
    for conversation in st.session_state.conversations:
        if conversation["id"] == active_id:
            conversation["messages"] = list(st.session_state.messages)
            if conversation["title"] == "New Conversation":
                conversation["title"] = conversation_title(user_messages[0]["content"])
                st.session_state.title_animation_id = active_id
            conversation["updated_at"] = updated_at
            write_conversations()
            return

    st.session_state.conversations.insert(
        0,
        {
            "id": active_id,
            "title": conversation_title(user_messages[0]["content"]),
            "messages": list(st.session_state.messages),
            "created_at": updated_at,
            "updated_at": updated_at,
        },
    )
    st.session_state.title_animation_id = active_id
    write_conversations()


def start_new_conversation():
    """Select a fresh local conversation without deleting previous history."""
    save_active_conversation()
    st.session_state.active_conversation_id = str(uuid.uuid4())
    reset_conversation()
    st.session_state.title_animation_id = None
    st.session_state.scroll_to_latest = True


def switch_conversation(conversation):
    """Load one saved conversation into the existing chat UI."""
    st.session_state.active_conversation_id = conversation["id"]
    st.session_state.messages = list(conversation["messages"])
    st.session_state.pending_query = None
    st.session_state.intro_animated = True
    st.session_state.scroll_to_latest = True


def render_scroll_controls(auto_scroll):
    """Add a small browser-side latest-message anchor and down-arrow control."""
    st.markdown('<div id="chat-bottom"></div>', unsafe_allow_html=True)
    components.html(
        f"""
        <script>
        const parentWindow = window.parent;
        const parentDocument = parentWindow.document;
        const anchor = parentDocument.getElementById("chat-bottom");
        let button = parentDocument.getElementById("finerp-scroll-latest");

        if (!button) {{
            button = parentDocument.createElement("button");
            button.id = "finerp-scroll-latest";
            button.type = "button";
            button.textContent = "↓";
            button.title = "Scroll to latest message";
            button.setAttribute("aria-label", "Scroll to latest message");
            button.style.cssText = "position:fixed;right:1.5rem;bottom:5.75rem;z-index:1000;display:none;width:2rem;height:2rem;border:1px solid #cbd5e1;border-radius:50%;background:#ffffff;color:#475569;font-size:1.1rem;cursor:pointer;box-shadow:0 3px 10px rgba(15,23,42,.12);";
            parentDocument.body.appendChild(button);
        }}

        const updateButton = () => {{
            const distanceFromBottom = parentDocument.documentElement.scrollHeight - parentWindow.innerHeight - parentWindow.scrollY;
            button.style.display = distanceFromBottom > 140 ? "flex" : "none";
            button.style.alignItems = "center";
            button.style.justifyContent = "center";
        }};

        button.onclick = () => anchor?.scrollIntoView({{ behavior: "smooth", block: "end" }});
        if (!parentWindow.finerpScrollListenerAdded) {{
            parentWindow.addEventListener("scroll", updateButton, {{ passive: true }});
            parentWindow.finerpScrollListenerAdded = true;
        }}
        updateButton();
        if ({str(auto_scroll).lower()}) {{
            requestAnimationFrame(() => anchor?.scrollIntoView({{ behavior: "smooth", block: "end" }}));
        }}
        </script>
        """,
        height=0,
    )


def reset_conversation():
    """Reset the chat to the welcome message and clear in-progress UI state."""
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": WELCOME_MESSAGE,
            "details": None,
            "timestamp": current_timestamp(),
        }
    ]
    st.session_state.pending_query = None
    st.session_state.voice_transcript = ""
    st.session_state.voice_error = ""
    st.session_state.last_audio_id = None
    st.session_state.intro_animated = False
    st.session_state.pending_composer_text = ""


def is_welcome_only_chat():
    """Return True when the conversation still contains only the welcome message."""
    return (
        len(st.session_state.messages) == 1
        and st.session_state.messages[0]["role"] == "assistant"
        and st.session_state.pending_query is None
    )


def queue_user_query(user_query):
    """Store a user message and wait for the next run to answer it."""
    cleaned_query = user_query.strip() if isinstance(user_query, str) else ""
    st.session_state.messages.append(
        {
            "role": "user",
            "content": cleaned_query or user_query,
            "timestamp": current_timestamp(),
        }
    )
    st.session_state.pending_query = cleaned_query or user_query
    st.session_state.voice_transcript = ""
    st.session_state.voice_error = ""
    st.session_state.scroll_to_latest = True
    save_active_conversation()
    st.rerun()


def transcribe_recorded_audio(audio_file):
    """Convert a Streamlit microphone recording into text, if possible."""
    try:
        import speech_recognition as sr
    except ImportError:
        return (
            None,
            "Microphone recording works, but speech-to-text is unavailable "
            "because the SpeechRecognition package is not installed.",
        )

    recognizer = sr.Recognizer()
    audio_bytes = audio_file.getvalue()
    wav_buffer = io.BytesIO(audio_bytes)

    try:
        with sr.AudioFile(wav_buffer) as source:
            recorded_audio = recognizer.record(source)
        recognized_text = recognizer.recognize_google(recorded_audio)
    except sr.UnknownValueError:
        return (
            None,
            "I couldn't understand that recording. Please try again, or type the question.",
        )
    except sr.RequestError:
        return (
            None,
            "Speech recognition is temporarily unavailable. Please type your question instead.",
        )
    except Exception:
        return (
            None,
            "The recording could not be transcribed. Please type your question instead.",
        )

    recognized_text = (recognized_text or "").strip()
    if not recognized_text:
        return (
            None,
            "I couldn't understand that recording. Please try again, or type the question.",
        )
    return recognized_text, ""


def show_match_details(details):
    """Display optional developer information for one assistant response."""
    with st.expander("Match details"):
        if details.get("is_confident_match"):
            st.write(f"**Matched FAQ:** {details['matched_question']}")
            st.write(f"**Category:** {details['category']}")
            st.write(f"**Similarity score:** {details['similarity_score']:.2f}")
        elif details.get("similarity_score") is None:
            st.write("No match was calculated because the input was empty.")
        else:
            st.write("No FAQ match passed the similarity threshold.")
            st.write(f"**Highest similarity score:** {details['similarity_score']:.2f}")

        processed_query = details.get("processed_query")
        if processed_query:
            st.write(f"**Processed query:** `{processed_query}`")
        elif details.get("similarity_score") is None or processed_query == "":
            st.write("**Processed query:** *(empty after preprocessing)*")


def render_message(message, message_index, show_match_details_enabled):
    """Render one chat bubble with optional timestamp and debug details."""
    avatar = AI_ICON if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        timestamp = message.get("timestamp")
        if timestamp:
            st.markdown(
                f'<div class="chat-meta">{timestamp}</div>',
                unsafe_allow_html=True,
            )
        if (
            message["role"] == "assistant"
            and show_match_details_enabled
            and message.get("details") is not None
        ):
            show_match_details(message["details"])


def render_suggested_questions(disabled, key_prefix):
    """Render clickable example questions that use the normal chatbot pipeline."""
    columns = st.columns(1)
    for index, question in enumerate(SUGGESTED_QUESTIONS):
        if columns[0].button(
            question,
            key=f"{key_prefix}_{index}",
            use_container_width=True,
            disabled=disabled,
        ):
            queue_user_query(question)


def render_welcome_message(show_match_details_enabled):
    """Show the first assistant message with a one-time typewriter effect."""
    welcome_message = st.session_state.messages[0]
    with st.chat_message("assistant", avatar=AI_ICON):
        if not st.session_state.intro_animated:
            message_placeholder = st.empty()
            typed_text = ""
            for character in WELCOME_MESSAGE:
                typed_text += character
                message_placeholder.markdown(f"{typed_text}▌")
                time.sleep(0.008)
            message_placeholder.markdown(WELCOME_MESSAGE)
            st.session_state.intro_animated = True
        else:
            st.markdown(welcome_message["content"])

        st.markdown(
            f'<div class="chat-meta">{welcome_message["timestamp"]}</div>',
            unsafe_allow_html=True,
        )
        if show_match_details_enabled and welcome_message.get("details") is not None:
            show_match_details(welcome_message["details"])


st.set_page_config(
    page_title="FinERP Learning Assistant",
    page_icon=AI_ICON,
    layout="centered",
)

if "conversations" not in st.session_state:
    st.session_state.conversations = load_conversations()

if st.session_state.get("chatbot_domain") != "finerp":
    st.session_state.chatbot_domain = "finerp"

if "active_conversation_id" not in st.session_state:
    if st.session_state.conversations:
        switch_conversation(st.session_state.conversations[0])
    elif "messages" in st.session_state and any(
        message["role"] == "user" for message in st.session_state.messages
    ):
        st.session_state.active_conversation_id = str(uuid.uuid4())
        save_active_conversation()
    else:
        reset_conversation()
        st.session_state.active_conversation_id = str(uuid.uuid4())

for state_key, default_value in (
    ("pending_query", None),
    ("voice_transcript", ""),
    ("voice_error", ""),
    ("last_audio_id", None),
    ("intro_animated", False),
    ("pending_composer_text", ""),
    ("scroll_to_latest", False),
    ("title_animation_id", None),
):
    if state_key not in st.session_state:
        st.session_state[state_key] = default_value

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

is_waiting_for_answer = st.session_state.pending_query is not None

with st.sidebar:
    st.header("About")
    st.write(
        "An educational FAQ assistant for accounting, finance, business, and ERP."
    )

    st.subheader("Topics")
    st.caption(" • ".join(TOPIC_NAMES))

    st.subheader("Example questions")
    render_suggested_questions(is_waiting_for_answer, "side_suggest")

    st.divider()
    show_match_details_enabled = st.checkbox(
        "Show match details",
        help="Optional NLP demo view: matched FAQ, category, similarity score, and processed query.",
    )

    conversation_heading, new_conversation_control = st.columns([5, 1])
    with conversation_heading:
        st.subheader("Conversations")
    with new_conversation_control:
        if st.button("+", key="new_conversation", help="New conversation"):
            start_new_conversation()
            st.rerun()

    if st.session_state.conversations:
        for conversation in st.session_state.conversations[:8]:
            is_new_title = (
                conversation["id"] == st.session_state.title_animation_id
            )
            if st.button(
                conversation["title"],
                key=(
                    f"conversation_new_{conversation['id']}"
                    if is_new_title
                    else f"conversation_{conversation['id']}"
                ),
                use_container_width=True,
            ):
                switch_conversation(conversation)
                st.rerun()

            if is_new_title:
                st.session_state.title_animation_id = None

st.title(WELCOME_TITLE)
st.caption(WELCOME_TAGLINE)

if is_welcome_only_chat():
    render_welcome_message(show_match_details_enabled)
else:
    for index, message in enumerate(st.session_state.messages):
        render_message(message, index, show_match_details_enabled)

if is_waiting_for_answer:
    with st.chat_message("assistant", avatar=AI_ICON):
        st.markdown(TYPING_INDICATOR_HTML, unsafe_allow_html=True)

render_scroll_controls(st.session_state.scroll_to_latest)
st.session_state.scroll_to_latest = False

if st.session_state.voice_error:
    st.caption(st.session_state.voice_error)

if st.session_state.pending_composer_text:
    st.session_state.user_chat_input = st.session_state.pending_composer_text
    st.session_state.pending_composer_text = ""

chat_submission = st.chat_input(
    "Ask an accounting, finance, or ERP question...",
    key="user_chat_input",
    disabled=is_waiting_for_answer,
    accept_audio=True,
    audio_sample_rate=16000,
)

if chat_submission and not is_waiting_for_answer:
    if isinstance(chat_submission, str):
        queue_user_query(chat_submission)
    elif chat_submission.text:
        queue_user_query(chat_submission.text)
    elif chat_submission.audio is not None:
        recorded_audio = chat_submission.audio
        audio_id = f"{recorded_audio.name}-{recorded_audio.size}-{recorded_audio.type}"
        if audio_id != st.session_state.last_audio_id:
            st.session_state.last_audio_id = audio_id
            recognized_text, voice_error = transcribe_recorded_audio(recorded_audio)
            st.session_state.voice_error = voice_error
            st.session_state.voice_transcript = ""
            if recognized_text:
                st.session_state.pending_composer_text = recognized_text
            st.rerun()

if is_waiting_for_answer:
    time.sleep(TYPING_DELAY_SECONDS)
    try:
        chatbot_result = get_chatbot_response(st.session_state.pending_query)
    except Exception:
        chatbot_result = {
            "response": (
                "Something went wrong while answering that question. "
                "Please try again, or rephrase it."
            ),
            "matched_question": None,
            "category": None,
            "similarity_score": None,
            "is_confident_match": False,
            "processed_query": "",
        }

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": chatbot_result["response"],
            "details": chatbot_result,
            "timestamp": current_timestamp(),
        }
    )
    st.session_state.pending_query = None
    st.session_state.scroll_to_latest = True
    save_active_conversation()
    st.rerun()
