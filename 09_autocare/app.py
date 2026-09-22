import os
from flask import Flask, jsonify, render_template, request, session
from dotenv import load_dotenv
from google import genai
from config import TITLE, DOMAIN, SYSTEM_PROMPT, WELCOME_MESSAGE, THEME, PORT, SECRET_KEY, MAX_HISTORY

load_dotenv()

app = Flask(__name__)
app.config.update(
    SECRET_KEY=SECRET_KEY,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("COOKIE_SECURE", "0") == "1",
    MAX_CONTENT_LENGTH=64 * 1024,
)

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite").strip()

def history():
    value = session.get("chat_history", [])
    return value if isinstance(value, list) else []

def call_gemini(items, message):
    if not API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured.")
    client = genai.Client(api_key=API_KEY)
    contents = []
    for item in items[-MAX_HISTORY:]:
        contents.append({
            "role": "user" if item["role"] == "user" else "model",
            "parts": [{"text": item["content"]}]
        })
    contents.append({"role": "user", "parts": [{"text": message}]})
    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config={"system_instruction": SYSTEM_PROMPT, "temperature": 0.3},
    )
    answer = getattr(response, "text", None)
    if not answer:
        raise RuntimeError("Gemini returned an empty response.")
    return answer.strip()

@app.get("/")
def home():
    return render_template("index.html", title=TITLE, domain=DOMAIN,
                           welcome=WELCOME_MESSAGE, theme=THEME)

@app.get("/health")
def health():
    return jsonify(status="ok", service=TITLE)

@app.get("/api/history")
def api_history():
    return jsonify(messages=history())

@app.post("/api/chat")
def api_chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    if not message:
        return jsonify(error="Please enter a message."), 400
    if len(message) > 4000:
        return jsonify(error="Message must be 4000 characters or fewer."), 400

    # Conservative local gate: short greetings are allowed; obvious unrelated
    # requests are rejected by the domain-focused model instruction as well.
    if message.lower() in {"hi", "hello", "hey", "thanks", "thank you"}:
        reply = WELCOME_MESSAGE
    else:
        try:
            reply = call_gemini(history(), message)
        except Exception:
            app.logger.exception("Gemini request failed")
            return jsonify(error="Assistant service is unavailable. Check the API key and model configuration."), 502

    items = history()
    items.extend([{"role":"user","content":message},
                  {"role":"assistant","content":reply}])
    session["chat_history"] = items[-MAX_HISTORY:]
    session.modified = True
    return jsonify(reply=reply)

@app.post("/api/clear")
def api_clear():
    session.pop("chat_history", None)
    return jsonify(status="cleared")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)
