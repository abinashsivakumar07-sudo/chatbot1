# DesignDock

**Domain:** UI/UX & Graphic Design

This chatbot has a unique visual identity #19 and is configured in `config.py`.

## Local setup
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```
Put your Gemini key in `.env`, then:
```bash
python app.py
```
Open `http://127.0.0.1:5000`.

## Render
Build command:
`pip install -r requirements.txt`

Start command:
`gunicorn app:app`

Set `GEMINI_API_KEY` and `FLASK_SECRET_KEY` in Render. The app reads Render's `PORT` automatically.

## Included
`app.py`, `config.py`, `.env.example`, `.gitignore`, `requirements.txt`, `README.md`, `templates/index.html`.

## Session privacy
No accounts are used. Temporary history is stored in the signed Flask session for the current browser session. Do not put secrets in frontend code. For larger multi-instance deployments, use a server-side session store such as Redis.
