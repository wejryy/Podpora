import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)

# Povolení CORS
CORS(app)

# Načtení Gemini API klíče z proměnných prostředí (Render)
api_key = os.environ.get("GEMINI_API_KEY")

@app.get("/")
def home():
    return "VDF Support Backend is running"

@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    student = (data.get("student") or "unknown").strip()

    if not message:
        return jsonify({"error": "message is required"}), 400

    # Kontrola, zda je klíč nastavený v Renderu
    if not api_key:
        return jsonify({"error": "API klíč (GEMINI_API_KEY) není na serveru nastaven."}), 500

    try:
        # Inicializace klienta s API klíčem
        client = genai.Client(api_key=api_key)
        
        # Odeslání dotazu do Gemini 4 Hydrogen včetně systémové instrukce
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=f"Jsi školní podpora (VDF Support). Odpovídáš studentovi jménem {student}. Buď stručný a nápomocný.",
                thinking_config=types.ThinkingConfig(
                    thinking_level="LOW"
                )
            )
        )
        
        # Získání textové odpovědi
        reply = response.text
        return jsonify({"reply": reply})

    except Exception as e:
        print(f"Chyba při komunikaci s Gemini API: {e}")
        return jsonify({"error": "Omlouváme se, podpora je momentálně nedostupná."}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=True)
