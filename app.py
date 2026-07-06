import os
import json
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Fetch the API key from Render Environment Variables
API_KEY = os.environ.get("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("Warning: GEMINI_API_KEY environment variable is missing!")

# Setup the Gemini Model
model = genai.GenerativeModel('gemini-pro')

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Server is running perfectly!"}), 200

@app.route('/api/mix', methods=['POST'])
def mix_elements():
    try:
        data = request.get_json()
        element_1 = data.get('element_1')
        element_2 = data.get('element_2')
        
        if not element_1 or not element_2:
            return jsonify({"error": "Both elements are required."}), 400
            
        # The strict prompt for Gemini to return only JSON
        prompt = f"""
        You are a creative game logic engine for an 'Element Mixer' game.
        Combine '{element_1}' and '{element_2}' into a single, logical new item, concept, or creature.
        Be creative but make sense.
        Return ONLY a valid JSON object in this exact format (no markdown, no extra text):
        {{"result_name": "New Item Name", "result_emoji": "🎨"}}
        """
        
        # Call Gemini API
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Remove any Markdown code block formatting if Gemini adds it accidentally
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
            
        # Parse the JSON response
        result_data = json.loads(response_text)
        
        return jsonify({
            "success": True,
            "result_name": result_data.get("result_name", "Unknown"),
            "result_emoji": result_data.get("result_emoji", "❓"),
            "is_new_discovery": True # Later, we will check the database to set this True/False
        }), 200
        
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to parse AI response. Try again."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
