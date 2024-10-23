from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import os
import DB
from modular import *
from datetime import timedelta

# flask application startup
api = Flask(__name__)
api.secret_key = 'Key'  # **Added line: Set a secret key for session management**
CORS(api)

if("securelang.db" not in os.listdir("backend/db")):
    DB.create_tables()
    DB.insert_test_values()
# håll info för session
# user_sessions = {}  # **Removed line: Using Flask's session instead**
api.secret_key = "hello"
api.permanent_session_lifetime = timedelta(minutes=5)
HTML_DIR = r"C:\Users\46763\OneDrive\Skrivbord\s01\git\Log-Analysis-with-LLM\frontend\html"

## route to index.html (located in frontend folder)
@api.route('/')
def index():
    return send_from_directory(HTML_DIR, 'index.html')

@api.route('/login.html')
def login_html():
    if 'user_id' in session:
       return send_from_directory(HTML_DIR, 'chat.html')
    else:
        return send_from_directory(HTML_DIR, 'login.html')

@api.route('/chat.html')
def chat_html():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 400
    return send_from_directory(HTML_DIR, 'chat.html')

# login
@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    Bo_value = DB.check_login(username, password)
    if Bo_value:
        user_id = get_user_id() 
        #user_id = DB.get_user_id_DB(username) # TEMP VET INTE VAR DENNA SKA KOMMA FRÅN
        user_directory = Path("backend/db") / user_id
        # **Changed line: Storing user info in the session**
        session['user_directory'] = str(user_directory)
        session['user_id'] = user_id
        session['vector_db'] = None  # håller
        session['ollama_instance'] = None  # håller
        print("login")
        print(session)
        return jsonify({"success": True, "user_id": user_id}), 200
    else:
        return jsonify({"success": False}), 401

# pre chat
@api.route('/setup', methods=['POST'])
def setup_for_chat():
    # **Changed line: Getting user_id from session instead of request args**
    user_id = session.get('user_id')
    chat_instruction = request.form.get('chat_instruction')  # ska komma från web interface

    if user_id is None:
        return jsonify({"error": "User not logged in"}), 401

    # Kontrollera om en fil har laddats upp
    if 'logfile' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['logfile']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # conf
    model_name = "llama3.2"
    base_url = "http://127.0.0.1:11434"
    template = ""
    complete_instruction = f"{template} {chat_instruction}"

    # Setup Ollama model
    ollama_instance = setup_ollama_model(complete_instruction, base_url=base_url, model=model_name)

    # Setup embeddings
    use_nvidia = False  # Change based on the system you use
    use_cpu = True
    embedding = setup_embeddings(use_nvidia=use_nvidia, use_cpu=use_cpu)

    # prepare file for vector storage
    log_file_path = Path(file.filename)
    file.save(log_file_path)  # Save file temporarily
    data = load_document(log_file_path)
    chunks = split_documents(data)

    # **Changed line: Accessing user_directory from session**
    user_directory = Path(session['user_directory'])
    if user_directory.exists():
        vector_db = load_vector_db(get_user_id(), embedding)
    else:
        vector_db = setup_vector_db(chunks, embedding, persist_directory=user_directory)

    # **Changed lines: Storing info in the session**
    session['ollama_instance'] = ollama_instance
    session['vector_db'] = vector_db

    return jsonify({"message": "File uploaded successfully"}), 200


# Chat Route
@api.route('/chat', methods=['POST'])
def chat():
    ## check if session is set 
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 400

    # **Changed line: Getting user_id from session instead of request args**
    print("chat")
    print(session)
    user_id = session.get('user_id')

    if user_id is None:
        return jsonify({"error": "User not logged in"}), 401

    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # **Changed lines: Retrieving model and vector DB from session**
    ollama_instance = session.get('ollama_instance')
    vector_db = session.get('vector_db')
    embeddings = setup_embeddings()  # spelar ingen roll att denna skapas igen

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
