from flask import Flask, request, jsonify
from flask_cors import CORS
import backend.src.sql as sql
from src.modular import *


#________VARIABLER FÖR TEST O HÅRDKOD_________
model_name = "llama3.1"
base_url = "http://127.0.0.1:11434"
use_nvidia = True
temple = "" #todo

api = Flask(__name__)


#____________LLM startup____________
Ollama = setup_ollama_model(base_url=base_url, model=model_name)
embedding = setup_embeddings()
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

@api.route('/message', methods=['POST'])#få chat
def chat():
    data = request.get_json()
    user_message = data.get('message')

    if user_message:
        # Skicka meddelandet till Ollama-instansen och få ett svar
        chat_instruction = user_message
        if chat_instruction == None:
            chat_instruction = ""
        #bot_response = response.get('result')  # Antag att svaret finns i 'result'

        #return jsonify({"response": bot_response}), 200
        return jsonify({"response": response}), 200
    else:
        return jsonify({"error": "No message provided"}), 400


@api.route('/upload_log', methods=['POST'])
def upload():
    # Kontrollera om en fil har laddats upp
    if 'logfile' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['logfile']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        embeddings = setup_embeddings(use_nvidia=use_nvidia)
        data = load_document(file)

        # Split document and create vector store
        chunks = split_documents(data)
        vector_db = setup_vector_db(chunks, embeddings)
        return jsonify({"message": "File uploaded successfully"}), 200



def start_ollama(chat_instructions):
        complete_instruction = chat_instructions + temple
        ollama_instance = setup_ollama_model(base_url=base_url,
                                                                    model=model_name,
                                                                    complete_instruction=complete_instruction)

@api.route('/todo', methods=['POST'])
def chat(ollama_instance, vector_db ):
    data = request.get_json()
    user_message = data.get('message')

    if user_message:
        # Skicka meddelandet till Ollama-instansen och få ett svar
        qachain = setup_qa_chain(ollama_instance, vector_db)

        question = input("Ask a question\n")
        while(response != "bye"):
            response = qachain({"query": question})
            print(f"Answer: {response['result']}")
        #bot_response = response.get('result')  # Antag att svaret finns i 'result'

        #return jsonify({"response": bot_response}), 200
        return jsonify({"response": response}), 200
    else:
        return jsonify({"error": "No message provided"}), 400





if __name__ == '__main__':
    api.run(debug=True)
