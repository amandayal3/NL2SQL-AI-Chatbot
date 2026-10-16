# NL2SQL AI Chatbot

Streamlit application that converts natural-language questions about the ecommerce dataset into SQL queries and presents the results.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your API key values to `.env`, then start the app:

```bash
streamlit run src/app.py
```

The raw and processed datasets, local SQLite database, virtual environment, and API keys are intentionally excluded from Git. Generate or provide those files locally as needed.
