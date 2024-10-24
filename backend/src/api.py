from flask import Flask, request, jsonify, send_from_directory, url_for, redirect, session
from flask_cors import CORS
import DB
from modular import *
from datetime import timedelta

# flask application startup
api = Flask(__name__)
CORS(api)

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
    if "user_id" in session:
        return send_from_directory(HTML_DIR, 'PRE_chat.html')
    else:
        return send_from_directory(HTML_DIR, 'login.html')

@api.route('/chat.html')
def chat_html():
    if "user_id" in session:
        return jsonify({"error": "User not logged in"}), 400
    return send_from_directory(HTML_DIR, 'chat.html')

@api.route('/PRE_chat.html')
def pre_chat():
    if "user_id" in session:
        return send_from_directory(HTML_DIR, 'PRE_chat.html')
    else:
        return send_from_directory(HTML_DIR, 'login.html')

# login
@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    Bo_value = DB.check_login(username, password)
    if Bo_value:
        global user_id
        user_id = DB.get_user_id_DB(username)
        user_directory = Path(f"../backend/db/{user_id}")

        # Store user session data
        session['user_directory'] = str(user_directory)
        session['vector_db'] = None
        session['ollama_instance'] = None

        return jsonify({"success": True, "user_id": user_id}), 200
    else:
        return jsonify({"success": False}), 401

# pre chat
@api.route('/setup', methods=['POST'])
def setup_for_chat():
    user_id = request.get('user_id')
    chat_instruction = request.form.get('chat-instruction')  # Ska komma från web interface

    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    if 'logfile' not in request.files:
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
    use_nvidia = True  # Change based on the system you use
    use_cpu = False
    embedding = setup_embeddings(use_nvidia=use_nvidia, use_cpu=use_cpu)

    # Förbered filen för vektorlagring
    log_file_path = Path(file.filename)
    file.save(log_file_path)  # Spara filen temporärt
    data = load_document(log_file_path)
    chunks = split_documents(data)

    user_directory = Path(session["user_directory"])
    if user_directory.exists():
        vector_db = load_vector_db(user_id, embedding)
    else:
        vector_db = setup_vector_db(chunks, embedding, persist_directory=user_directory)

    # update user_sessions per user
    session['ollama_instance'] = ollama_instance
    session['vector_db'] = vector_db

# Chat Route
@api.route('/chat', methods=['POST'])
def chat():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Retrieve the model and vector DB from the session
    ollama_instance = session.get('ollama_instance')
    vector_db = session.get('vector_db')
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