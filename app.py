import os
import json
from flask import Flask, request, jsonify
import google.generativeai as genai
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# --- Environment Variables ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MONGO_URI = os.environ.get("MONGO_URI")

# --- Setup Gemini AI ---
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Warning: GEMINI_API_KEY is missing!")
model = genai.GenerativeModel('gemini-pro')

# --- Setup MongoDB ---
db = None
if MONGO_URI:
    try:
        client = MongoClient(MONGO_URI)
        db = client['element_mixer_db']
        combinations_collection = db['combinations']
        print("MongoDB connected successfully!")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
else:
    print("Warning: MONGO_URI is missing!")

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Element Mixer API with MongoDB is running!"}), 200

@app.route('/api/mix', methods=['POST'])
def mix_elements():
    try:
        data = request.get_json()
        element_1 = data.get('element_1')
        element_2 = data.get('element_2')
        
        if not element_1 or not element_2:
            return jsonify({"error": "Both elements are required."}), 400
            
        # Sort elements alphabetically to ensure "Fire+Water" is the same as "Water+Fire"
        elements = sorted([element_1.strip().lower(), element_2.strip().lower()])
        combo_id = f"{elements[0]}_{elements[1]}"
        
        # 1. Check if combination already exists in MongoDB
        if db is not None:
            existing_combo = combinations_collection.find_one({"_id": combo_id})
            if existing_combo:
                return jsonify({
                    "success": True,
                    "result_name": existing_combo["result_name"],
                    "result_emoji": existing_combo["result_emoji"],
                    "is_new_discovery": False
                }), 200

        # 2. If not found, ask Gemini to create a new one
        prompt = f"""
        You are a creative game logic engine for an 'Element Mixer' game.
        Combine '{elements[0]}' and '{elements[1]}' into a single, logical new item, concept, or creature.
        Be creative but make sense.
        Return ONLY a valid JSON object in this exact format (no markdown, no extra text):
        {{"result_name": "New Item Name", "result_emoji": "🎨"}}
        """
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
            
        result_data = json.loads(response_text)
        new_name = result_data.get("result_name", "Unknown")
        new_emoji = result_data.get("result_emoji", "❓")
        
        # 3. Save the new discovery to MongoDB
        if db is not None:
            combinations_collection.insert_one({
                "_id": combo_id,
                "element_1": elements[0],
                "element_2": elements[1],
                "result_name": new_name,
                "result_emoji": new_emoji,
                "discovered_at": datetime.utcnow()
            })
            
        return jsonify({
            "success": True,
            "result_name": new_name,
            "result_emoji": new_emoji,
            "is_new_discovery": True
        }), 200
        
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to parse AI response. Try again."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
