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


            """
            när jag concatenate log fil innehåll med en fråga och sen skicka som prompt till ollama
            jag får error:
            Argument `prompt` is expected to be a string. Instead found .
            If you want to run the LLM on multiple prompts, use `generate` instead.
            så jag sparar log fil innehåll som string i log_data_string och skicka till ollama
            """
            # Concatenate log filens innehåll som en string
            log_data_string = " ".join([doc.page_content for doc in chunks])
            print("#########################################################")
            print(type(log_data_string))
            print("#########################################################")

            # skicka till ollama med promp att analysera log filen som är i chuncks
            response = ollama_instance({"prompt": f"Analyze the following log data: {log_data_string}"})
            return jsonify({'response': 'File loaded and analyzed successfully', 'ollama_analysis': response['content']}), 200


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

if __name__ == '__main__':
    # directory to store the logfile
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0', port=5000)