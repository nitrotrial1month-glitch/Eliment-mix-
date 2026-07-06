from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Basic route to check if the server is running
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "success",
        "message": "Element Mixer Server is running on Render!"
    }), 200

# Route to handle element mixing requests from Flutter
@app.route('/api/mix', methods=['POST'])
def mix_elements():
    try:
        data = request.get_json()
        
        element_1 = data.get('element_1')
        element_2 = data.get('element_2')
        
        if not element_1 or not element_2:
            return jsonify({"error": "Both elements are required."}), 400
            
        # TODO: Here we will add the Gemini API logic to generate the new element
        # For now, returning a mock response for testing
        mock_result_name = f"{element_1}-{element_2} Object"
        mock_result_emoji = "✨"
        
        return jsonify({
            "success": True,
            "result_name": mock_result_name,
            "result_emoji": mock_result_emoji,
            "is_new_discovery": True
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
  
