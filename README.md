# 🗺️ AI Learning Roadmap Generator

A Streamlit web app that creates a personalised, week-by-week learning roadmap.
Choose your skill level (Beginner, Intermediate, Advanced), set how many hours per
week and how many weeks you can commit, and get a complete plan with topics,
resources, mini projects, capstone ideas and checkpoints.

## Features

- Three skill levels: Beginner, Intermediate, Advanced
- Custom study time: hours per week and number of weeks
- Optional goal field (career switch, internship, project, etc.)
- Works for any topic, with AI/ML as the default
- Automatic retries and a fallback model when the API is busy (503 errors)
- Result caching to avoid repeated API calls
- Download the roadmap as a Markdown file

## Tech Stack

- [Streamlit](https://streamlit.io/) for the UI and deployment
- [Google Gemini API](https://ai.google.dev/) via the `google-genai` SDK

## Project Structure

```
ai-learning-roadmap/
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Run Locally

1. Clone the repository

   ```bash
   git clone https://github.com/<your-username>/ai-learning-roadmap.git
   cd ai-learning-roadmap
   ```

2. Create a virtual environment and install dependencies

   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

4. Create the file `.streamlit/secrets.toml` and add your key:

   ```toml
   GEMINI_API_KEY = "your-api-key-here"
   ```

5. Start the app

   ```bash
   streamlit run app.py
   ```

## Deploy on Streamlit Community Cloud

1. Push this project to a GitHub repository (never commit your API key).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **Create app**, choose your repository, branch `main`, and main file `app.py`.
4. Open **Advanced settings → Secrets** and paste:

   ```toml
   GEMINI_API_KEY = "your-api-key-here"
   ```

5. Click **Deploy**.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `503 UNAVAILABLE` | The model is overloaded. The app retries automatically; if it still fails, wait a minute and try again. |
| `API key not found` | Check that `GEMINI_API_KEY` is set in secrets. |
| `429` error | You hit the free-tier rate limit. Wait and retry. |
| Model not found | Model names change over time. Update `PRIMARY_MODEL` and `FALLBACK_MODEL` in `app.py`. |

## License

MIT
