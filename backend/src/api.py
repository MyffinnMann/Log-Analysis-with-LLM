"""File to connect backend with frontend"""
from flask import(
    Flask,
    request,
    jsonify,
    send_from_directory,
    session,
)
from flask_cors import CORS
import DB
from datetime import timedelta
from modular import(
    setup_embeddings,
    persistent_storage,
    logging, Path,
    os,
    setup_ollama_model,
    load_document,
    load_vector_db,
    split_documents,
    setup_vector_db,
    sanitize_input,
    setup_qa_chain,
    filter_answer,
    delete_vector_db
)
from config import(
    template,
    base_url,
    model_name,
    use_cpu,
    use_nvidia,
)

# flask application startup
api = Flask(__name__)
CORS(api)

user_data = {}
logging.basicConfig(level=logging.INFO) # ta bort denna om ni har något bättre
keywords = ["password", "username", "user_id"] # fyll på denna medan vi testar

# create db
DB_PATH = Path("backend/db/securelang.db")
if("securelang.db" not in os.listdir("backend/db")):
    DB.create_tables()
    DB.insert_test_values("test_user", "test")
    DB.insert_test_values("user_1", "user_1")
    DB.insert_test_values("user_2", "user_2")

api.secret_key = "hello"
api.permanent_session_lifetime = timedelta(minutes=60)
HTML_DIR = Path("../../frontend/html")
CSS_DIR = Path("../../frontend/html/css")
# route to index.html (located in frontend folder)

@api.route('/css/style.css', methods=["GET"])
def getStylecss():
    return send_from_directory(CSS_DIR, 'style.css')

@api.route('/css/chat.css', methods=["GET"])
def getChatcss():
    return send_from_directory(CSS_DIR, 'chat.css')

@api.route('/css/index.css', methods=["GET"])
def getIndexcss():
    return send_from_directory(CSS_DIR, 'index.css')

@api.route('/css/login.css', methods=["GET"])
def getLogincss():
    return send_from_directory(CSS_DIR, 'login.css')

@api.route('/')
def index():
    return send_from_directory(HTML_DIR, 'index.html')

@api.route('/login.html', methods=['GET'])
def login_html():
    if "user_id" in session:
        return send_from_directory(HTML_DIR, 'PRE_chat.html')
    else:
        return send_from_directory(HTML_DIR, 'login.html')

@api.route('/chat.html', methods=['GET'])
def chat_html():
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 400
    return send_from_directory(HTML_DIR, 'chat.html')

@api.route('/PRE_chat.html', methods=['GET'])
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
        user_id = username
        user_directory = Path(f"../backend/db/user_db/{user_id}")

        # Store user session data
        session["user_id"] = user_id
        session['user_directory'] = str(user_directory)

        return jsonify({"success": True, "user_id": user_id}), 200
    else:
        return jsonify({"success": False}), 401

# pre chat
@api.route('/setup', methods=['POST'])
def setup():
    user_id = session["user_id"]
    user_data[user_id] = {}
    chat_instruction = request.form.get('chat-instruction')

    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    if 'logfile' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["logfile"]

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400 #test #vad är detta för test? /oscar

    # Setup Ollama model
    ollama_instance = setup_ollama_model(f"{template} {chat_instruction}", base_url=base_url, model=model_name)

    # Setup embeddings
    embedding = setup_embeddings(use_nvidia, use_cpu)

    # Förbered filen för vektorlagring
    log_file_path = Path(file.filename)
    file.save(log_file_path)  # Spara filen temporärt
    data = load_document(log_file_path)
    chunks = split_documents(data)

    user_directory = Path(f"backend/db/vector_db/{user_id}") # Path(session["user_directory"])    FUNKAR I VSC OCH MAN KÖR TERMINAL I FOLDER UTANFÖR BACKEND ETT STEG 
    if user_directory.exists():
        vector_db = load_vector_db(user_id=user_id, embeddings=embedding)
    else:
        vector_db = setup_vector_db(chunks, embedding, persist_directory=user_directory)

    # vi kör på detta
    user_data[user_id] = {
        'user_directory': user_directory,
        'vector_db': vector_db,
        'ollama_instance': ollama_instance,
        "chat-instruction": chat_instruction # behöver ha denna senare sätter den här
    }
    return jsonify({"Success": True}), 200 # kod 200 att det lyckades

# Chat Route
@api.route('/chat', methods=['POST'])
def chat():
    user_id = session["user_id"]

    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    data = request.get_json()
    question = sanitize_input(data.get('message'))

    if not question:
        return jsonify({"error": "No message provided"}), 400

    # ta fram information vi har från setup
    ollama_instance = user_data[user_id]["ollama_instance"]
    vector_db = user_data[user_id]["vector_db"]
    embeddings = setup_embeddings(False, True) # param 1 = nvidia, param 2 = cpu

    if ollama_instance is None or vector_db is None:
        return jsonify({"error": "Model or Vector DB not initialized"}), 500

    # Set up QA chain
    qachain = setup_qa_chain(ollama_instance, vector_db)
    conversation_history = user_data[user_id].get("conversation-history", [])
    chat_instruction = user_data[user_id]["chat-instruction"]

    # conversation loop
    try:
        relevant_docs = qachain.retriever.get_relevant_documents(question)
        retrieved_context = "\n".join(doc.page_content for doc in relevant_docs)

        history_context = "\n".join([f"Q: {q}\nA: {a}" for q, a in conversation_history[-3:]])
        full_context = f"{history_context}\n{retrieved_context}"

        formatted_prompt = template.format(chat_instruction=chat_instruction, context=full_context, query=question)

        # get response
        response = qachain({"query": formatted_prompt})
        answer = response['result']
        filtered_answer = filter_answer(answer)

        print(filtered_answer)

        # Store the interaction in the vector DB
        persistent_storage(question, answer, user_id, embeddings, vector_db)
        if question and filtered_answer:
            conversation_history = [(question, filtered_answer)]
        user_data[user_id]["conversation_history"] = conversation_history

        return jsonify({"response": answer}), 200

    except Exception as e:
        logging.error("Error: Unexpected error, try again", e)
        return jsonify({"error": "Internal server error"}), 500
    except ValueError as ve:
        logging.error("Error: input error", ve)
        return jsonify({"error": "Internal server error"}), 500

@api.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True}), 200

@api.route('/delete_me', methods=['POST'])
def delete_me():
    vector_db=user_data[user_id]["vector_db"]
    delete_vector_db(vector_db)
    #________FUNKTION FÖR att ta bort användare i db__________?
    return jsonify({"success": True}), 200

if __name__ == '__main__':
    api.run(host='0.0.0.0', port=5000, debug=True)
