from flask import Flask, request, jsonify
from flask_cors import CORS
import sql as sql
from modular import *

# flask application startup
api = Flask(__name__)
CORS(api)

# håll info för session
user_sessions= {}

# login
@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    Bo_value = sql.check_login(username, password)
    if Bo_value:
        user_id = get_user_id() # TEMP VET INTE VAR DENNA SKA KOMMA FRÅN
        user_directory = Path("backend/db") / user_id

        user_sessions[user_id] = {
            "user_directory": user_directory,
            "vector_db": None,  # håller
            "ollama_instance": None  # håller
        }

        return jsonify({"success": True, "user_id": user_id}), 200
    else:
        return jsonify({"success": False}), 401

# pre chat
@api.route('/setup', methods=['POST'])
def setup_for_chat():
    user_id = request.args.get('user_id')
    chat_instruction = request.form.get('chat-instruction')  # Ska komma från web interface

    # Kontrollera om user_id är giltigt (om du väljer att aktivera den koden igen)
    # if user_id is None or user_id not in user_sessions:
    #     return jsonify({"error": "User not logged in or user_id is invalid"}), 401

    # Kontrollera om en fil har laddats upp
    if 'logfile' not in request.files:
        print("No file part")
        return jsonify({"error": "No file part"}), 400

    file = request.files['logfile']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Skriv ut chat-instruktioner och filnamn
    print(f"Chat Instruction: {chat_instruction}")
    print(f"Uploaded File: {file.filename}")

    # conf
    model_name = "llama3.2"
    base_url = "http://127.0.0.1:11434"
    template = ""
    complete_instruction = f"{template} {chat_instruction}"

    # Setup Ollama model
    ollama_instance = setup_ollama_model(complete_instruction, base_url=base_url, model=model_name)

    # Setup embeddings
    use_nvidia = False  # Change based on the system you use
    use_cpu = False
    embedding = setup_embeddings(use_nvidia=use_nvidia, use_cpu=use_cpu)

    # Förbered filen för vektorlagring
    log_file_path = Path(file.filename)
    file.save(log_file_path)  # Spara filen temporärt
    data = load_document(log_file_path)
    chunks = split_documents(data)

    # Spara info om användaren
    #user_sessions[user_id]['ollama_instance'] = ollama_instance

    return jsonify({"message": "File uploaded successfully"}), 200



# Chat Route
@api.route('/chat', methods=['POST'])
def chat():
    user_id = request.args.get('user_id')

    if user_id not in user_sessions:
        return jsonify({"error": "User not logged in"}), 401

    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Retrieve the model and vector DB from the session
    ollama_instance = user_sessions[user_id]['ollama_instance']
    vector_db = user_sessions[user_id]['vector_db']
    embeddings = setup_embeddings() # spelar ingen roll att denna skapas igen

    if ollama_instance is None or vector_db is None:
        return jsonify({"error": "Model or Vector DB not initialized"}), 500

    # Set up QA chain
    qachain = setup_qa_chain(ollama_instance, vector_db)

    # conversation loop
    while True:
        question = input("Ask a question (or type 'exit' to quit):\n")
        if question.lower() == 'exit':
            break

        # get response
        response = qachain({"query": user_message})

        # get answer
        answer = response['result']
        print(f"Answer: {answer}")

    # Store the interaction in the vector DB
    persistent_storage(user_message, answer, user_id, embeddings, vector_db)

    return jsonify({"response": answer}), 200


if __name__ == '__main__':
    api.run(debug=True)
