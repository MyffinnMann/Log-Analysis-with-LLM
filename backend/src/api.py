from flask import Flask, request, jsonify, send_from_directory, url_for, redirect, session
from flask_cors import CORS
import DB
from modular import *
from datetime import timedelta

# flask application startup
api = Flask(__name__)
CORS(api, supports_credentials=True)

user_data = {}

# create db
DB_PATH = Path("/backend/db/securelang.db")
if not DB_PATH.exists():
    DB.create_tables()
    DB.insert_test_values()

api.secret_key = "hello"
api.permanent_session_lifetime = timedelta(minutes=60)
HTML_DIR = Path("../../frontend/html")

# route to index.html (located in frontend folder)
@api.route('/')
def index():
    return send_from_directory(HTML_DIR, 'index.html')

@api.route('/login.html')
def login_html():
    return send_from_directory(HTML_DIR, 'login.html')

@api.route('/chat.html')
def chat_html():
    return send_from_directory(HTML_DIR, 'chat.html')

@api.route('/PRE_chat.html')
def pre_chat():
    return send_from_directory(HTML_DIR, 'PRE_chat.html')

# login
@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    session["username"] = username
    session["password"] = password

    Bo_value = DB.check_login(username, password)
    if Bo_value:
        user_id = DB.get_user_id_DB(username)
        session["user_id"] = user_id
        user_directory = Path(f"../db/{user_id}")

        # Store user session data
        if user_id not in user_data:
            user_data[user_id] = {
                'user_directory': user_directory,
                'vector_db': None,
                'ollama_instance': None
            }

        return jsonify({"success": True, "user_id": user_id}), 200
    else:
        return jsonify({"success": False}), 401

# pre chat
@api.route('/setup', methods=['POST'])
def setup():
    chat_instruction = request.form.get('chat-instruction')
    user_id = session.get("user_id")

    if 'logfile' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["logfile"]

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if user_id not in user_data:
        return jsonify({"error": "User not logged in"}), 401 # ha denna som reroute till login.html ist?

    # conf
    model_name = "llama3.2"
    base_url = "http://127.0.0.1:11434"
    template = ""
    complete_instruction = f"{template} {chat_instruction}"

    # Setup Ollama model
    ollama_instance = setup_ollama_model(complete_instruction, base_url=base_url, model=model_name)

    # Setup embeddings
    use_nvidia = True  # Change based on the system you use
    use_cpu = False
    embedding = setup_embeddings(use_nvidia=use_nvidia, use_cpu=use_cpu)

    print(user_data)
    # Förbered filen för vektorlagring
    log_file_path = Path(file.filename)
    file.save(log_file_path)
    user_directory = user_data[user_id]['user_directory']
    data = load_document(log_file_path)
    chunks = split_documents(data)
    if user_directory.exists():
        vector_db = load_vector_db(session["user_id"], embedding)
    else:
        vector_db = setup_vector_db(chunks, embedding, persist_directory=user_directory)

    # update user_sessions per user
    user_data[user_id]['ollama_instance'] = ollama_instance
    user_data[user_id]['vector_db'] = vector_db

    return jsonify({"success": True, "message": "Setup complete. Ready to chat."}), 200

# Chat Route
@api.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_id = data.get('user_id')
    user_message = data.get('message')

    if user_id not in user_data:
        return jsonify({"error": "User not logged in"}), 401 # igen kanske reroute här

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Retrieve the model and vector DB from the session
    ollama_instance = user_data[user_id]["ollama_instance"]
    vector_db = user_data[user_id]["vector_db"]
    embeddings = setup_embeddings()

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