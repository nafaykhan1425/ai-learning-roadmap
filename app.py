import os
import time
import random

import streamlit as st
from google import genai
from google.genai import errors

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Learning Roadmap Generator",
    page_icon="🗺️",
    layout="centered",
)

# Models are tried in order. If one is busy (503) or retired (404), the app
# moves on to the next. Check https://ai.google.dev/gemini-api/docs/models
# for current names and update this list when models change.
MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
]
RETRYABLE_CODES = {429, 500, 503, 504}
SKIP_MODEL_CODES = {404}


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------
def get_api_key() -> str | None:
    """Read the key from Streamlit secrets first, then environment variables."""
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return os.getenv("GEMINI_API_KEY")


def build_prompt(topic: str, level: str, hours_per_week: int, weeks: int, goal: str) -> str:
    total_hours = hours_per_week * weeks
    goal_line = goal.strip() if goal.strip() else "Build strong practical skills"
    return f"""
You are an expert mentor and curriculum designer.

Create a complete, realistic learning roadmap with these details:
- Topic: {topic}
- Current skill level: {level}
- Time available: {hours_per_week} hours per week for {weeks} weeks (about {total_hours} hours in total)
- Learner's goal: {goal_line}

Format the answer in Markdown with these sections:

## 1. Overview
Two or three sentences on what the learner will achieve and a skill-level assessment.

## 2. Prerequisites
What to know before starting (write "None" if nothing is needed).

## 3. Week-by-Week Plan
For EVERY week from 1 to {weeks}, give:
- **Week N: Theme**
- Topics to cover
- Recommended free resources (courses, docs, books, YouTube channels)
- A hands-on task or mini project
- Estimated hours (must fit within {hours_per_week} hours)

## 4. Capstone Projects
Two or three portfolio-worthy projects matched to the {level} level.

## 5. Tools & Technologies
Languages, libraries and platforms to learn.

## 6. Progress Checkpoints
How the learner can test themselves at the end of each phase.

## 7. Next Steps After This Roadmap
What to learn next.

Rules: be specific, avoid filler, keep the pace realistic for the {level} level,
and do not invent URLs. Name resources by title and author or platform instead.
""".strip()


def generate_with_retry(client, prompt: str, max_retries: int = 3) -> str:
    """Call Gemini with exponential backoff, falling back through MODELS."""
    last_error = None
    for model in MODELS:
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(model=model, contents=prompt)
                if response.text:
                    return response.text
                raise RuntimeError("The model returned an empty response.")
            except errors.APIError as err:
                last_error = err
                if err.code in SKIP_MODEL_CODES:
                    break  # model retired or unavailable: try the next one
                if err.code not in RETRYABLE_CODES:
                    raise
                time.sleep((2 ** attempt) + random.random())
    raise last_error if last_error else RuntimeError("Unknown error")


@st.cache_data(show_spinner=False, ttl=3600)
def get_roadmap(api_key: str, topic: str, level: str, hours: int, weeks: int, goal: str) -> str:
    client = genai.Client(api_key=api_key)
    prompt = build_prompt(topic, level, hours, weeks, goal)
    return generate_with_retry(client, prompt)


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
st.title("🗺️ AI Learning Roadmap Generator")
st.write(
    "Tell me your level and how much time you have, and I'll build a "
    "personalised week-by-week learning plan."
)

api_key = get_api_key()
if not api_key:
    st.error(
        "Gemini API key not found. Add `GEMINI_API_KEY` to `.streamlit/secrets.toml` "
        "locally, or to the Secrets section on Streamlit Community Cloud."
    )
    st.stop()

with st.form("roadmap_form"):
    topic = st.text_input(
        "What do you want to learn?",
        value="Artificial Intelligence & Machine Learning",
    )
    level = st.selectbox("Your current level", ["Beginner", "Intermediate", "Advanced"])

    col1, col2 = st.columns(2)
    with col1:
        hours = st.slider("Hours per week", min_value=1, max_value=40, value=8)
    with col2:
        weeks = st.slider("Number of weeks", min_value=2, max_value=24, value=8)

    goal = st.text_area(
        "Your goal (optional)",
        placeholder="e.g. Get an ML internship, build a chatbot, switch careers...",
    )
    submitted = st.form_submit_button("Generate Roadmap 🚀")

if submitted:
    if not topic.strip():
        st.warning("Please enter a topic.")
        st.stop()

    with st.spinner("Building your roadmap... this can take up to a minute."):
        try:
            roadmap = get_roadmap(api_key, topic.strip(), level, hours, weeks, goal)
        except errors.APIError as err:
            if err.code in RETRYABLE_CODES:
                st.error("The AI service is busy right now. Please try again in a minute.")
            else:
                st.error(f"API error ({err.code}): {err.message}")
            st.stop()
        except Exception as err:
            st.error(f"Something went wrong: {err}")
            st.stop()

    st.success(f"Your {level} roadmap: {hours} h/week for {weeks} weeks")
    st.markdown(roadmap)
    st.download_button(
        "⬇️ Download as Markdown",
        data=roadmap,
        file_name="learning_roadmap.md",
        mime="text/markdown",
    )

st.caption("Built with Streamlit and Google Gemini.")
