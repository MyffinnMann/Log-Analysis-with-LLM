import requests
import json
from flask import Flask, request, jsonify
import requests
from flask_cors import CORS  # Import CORS
from flask_cors import CORS
import os
from pathlib import Path
from werkzeug.utils import secure_filename

from langchain_community.llms import Ollama
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings

import sql

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = './logfiles'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ollama_instance = Ollama(base_url="http://127.0.0.1:11434", model="llama3.1")
hf = HuggingFaceEmbeddings(show_progress=True)

vector_db = None # vector database for the log file

# file upload route
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Check if the post request has the file part
        if 'logfile' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['logfile']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            log_file = Path(filepath)
            loader = TextLoader(log_file)
            data = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = text_splitter.split_documents(data)

            global vector_db
            vector_db = Chroma.from_documents(documents=chunks,
                                              embedding=hf,
                                              collection_name="local",
                                              persist_directory=None)

            # den här raden är för att testa om fil uppladning lyckades
            # return jsonify({'response': 'File loaded successfully'}), 200

            # Concatenate log filens innehåll som en string
            log_data_string = " ".join([doc.page_content for doc in chunks])
            prompt_till_ollama = f"Analyze the following log data, {log_data_string}"

            # skicka prompt till ollama
            response = requests.post(
                'http://localhost:11434/api/generate', # här använder jag direkt api request istället for ollama_instance
                json={'model': 'llama3.1', 'prompt': prompt_till_ollama}, 
                stream=True
            )

            app.logger.debug(f"Received response status: {response.status_code}")

            # ollama skickar svar som stream och skickar "done" för att visa den är klar med att svara,
            # så vi väntar innan vi skickar svar till front end
            # vi sammlar alla svar till full_response
            full_response = ""
            for line in response.iter_lines():
                if line:
                    # konvertera line till JSON
                    json_line = json.loads(line.decode('utf-8'))
                    full_response += json_line.get("response", "")
                    
                    # kolla om ollama skickar done
                    if json_line.get("done"):
                        break

        return jsonify({'response': full_response}), 200 # skicka full svar till front end

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# chat route
@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        userMessage = data['userMessage']

        if vector_db is None:
            return jsonify({'error': 'No log file uploaded yet'}), 400

        qachain = RetrievalQA.from_chain_type(ollama_instance, retriever=vector_db.as_retriever())
        answer = qachain({"query": userMessage})
        
        return jsonify({'response': answer['result']}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print(f"Data mottagen från frontend: {data}")  # Debug

    username = data.get('username')
    password = data.get('password')

    print(f"Kontrollerar användarnamn: {username} och lösenord: {password}")  # Debug
    Bo_value = sql.check_login(username, password)
    # Kontrollera om användarnamn och lösenord matchar
    if Bo_value == True:
        print("Inloggning lyckades!")  # Debug
        return jsonify({"success": True}), 200
    else:
        print("Inloggning misslyckades!")  # Debug
        return jsonify({"success": False}), 401


if __name__ == '__main__':
    # directory to store the logfile
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0', port=5000)

