import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

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
        # Konfigurace klíče
        genai.configure(api_key=api_key)
        
        # Vytvoření instance modelu včetně systémové instrukce pro kontext
        model = genai.GenerativeModel(
            model_name="gemini-3.6-flash",
            system_instruction=f"Jsi školní podpora (VDF Support). Odpovídáš studentovi jménem {student}. Buď stručný a nápomocný."
        )
        
        # Odeslání dotazu do Gemini
        response = model.generate_content(message)
        
        # Získání textové odpovědi
        reply = response.text
        return jsonify({"reply": reply})

    except Exception as e:
        print(f"Chyba při komunikaci s Gemini API: {e}")
        return jsonify({"error": "Omlouváme se, podpora je momentálně nedostupná."}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=True)
