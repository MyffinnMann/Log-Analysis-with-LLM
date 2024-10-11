from flask import Flask, request, jsonify
from flask_cors import CORS
import sql
import modular as m

#________VARIABLER FÖR TEST O HÅRDKOD_________
model_name = "llama3.1"
base_url = "http://127.0.0.1:11434"

api = Flask(__name__)

#____________LLM startup____________
Ollama = m.setup_ollama_model(base_url=base_url, model=model_name)
embedding = m.setup_embeddings()
CORS(api)

@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    Bo_value = sql.check_login(username, password)
    if Bo_value:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False}), 401

@api.route('/message', methods=['POST'])        #To get questions after analysis
def chat():
    data = request.get_json()
    user_message = data.get('message')
    
    if user_message:
        # Skicka meddelandet till Ollama-instansen och få ett svar
        #response = Ollama(user_message)
        #bot_response = response.get('result')  # Antag att svaret finns i 'result'
    
        #return jsonify({"response": bot_response}), 200
        return jsonify("response"), 200
    else:
        return jsonify({"error": "No message provided"}), 400

@api.route('/upload_log', methods=['POST'])     #TO GET LOG FILE UPLOAD PRE CHAT
def upload():
    global log_file_content
    # Kontrollera om en fil har laddats upp
    if 'logfile' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['logfile']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        log_file_content = file.read()
        test()
        return jsonify({"message": "File uploaded successfully"}), 200

@api.route('/start', methods=['POST'])        #To get chat instruction PRE CHAT
def start():
    data = request.get_json()
    user_message = data.get('message')
    
    if user_message:
        print("START MESSAGE: ", user_message)      #FOR TESTING

        return jsonify("response"), 200             #TO NOTIFY SUCCESS
    else:
        return jsonify({"error": "No message provided"}), 400

def test(): #if file exist
    if log_file_content is not None:
        print("FILE: YES")

if __name__ == '__main__':
    api.run(debug=True)
