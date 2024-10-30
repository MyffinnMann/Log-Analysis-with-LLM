# from langchain_community.llms import Ollama
from langchain_ollama import OllamaLLM
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
import torch
# import torch_directml
from datetime import datetime

def get_user_id(): # detta id kan vara token?
    return "User_1"

def setup_ollama_model(complete_instruction,
                                        base_url="http://127.0.0.1:11434",
                                        model="llama3.1:latest",):
    """Set up the Ollama LLM model instance."""

    llm = OllamaLLM(base_url=base_url,
                model=model,
                template=complete_instruction)
    return llm


def setup_embeddings(use_nvidia=False, use_cpu=True):
    """Set up embedding model; can toggle between HuggingFace and Ollama embeddings."""
    if use_nvidia and not use_cpu:
        return HuggingFaceEmbeddings(show_progress=True,
                                    model_kwargs={"device": "cuda"})
    if not use_nvidia and not use_cpu:
        return HuggingFaceEmbeddings(show_progress=True,
                                    model_kwargs={"device": "cpu"})
    if use_cpu:
        return HuggingFaceEmbeddings(show_progress=True)


def load_document(log_file_path):
    """Load the document from a given file path."""
    log_file = Path(log_file_path)
    loader = TextLoader(log_file)
    return loader.load()


def split_documents(data, chunk_size=1000, chunk_overlap=200): # göra test med denna för optimering på dator vi ska använda vid demo?
    """Split the loaded documents into chunks."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,
                                                                            chunk_overlap=chunk_overlap)
    return text_splitter.split_documents(data)


def setup_vector_db(chunks, embeddings, collection_name="local", persist_directory=None):
    """Create a vector database from document chunks and embeddings."""
    return Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=collection_name,
            persist_directory=str(persist_directory)
    )


def setup_qa_chain(llm_instance, vector_db):
    """Set up the RetrievalQA chain using the LLM instance and vector database retriever."""
    return RetrievalQA.from_chain_type(llm_instance, retriever=vector_db.as_retriever())

def persistent_storage(question, answer, user_id, embeddings, vector_db):
    """Store relevant information on a user so that communication can be personalized"""
    timestamp = str(datetime.now())

    # create embedding so they can be stored
    question_embedding = embeddings.embed_query(question)
    answer_embedding = embeddings.embed_query(answer)

    # Store question
    vector_db.add_texts(
        texts=[question],
        embeddings=[question_embedding],
        metadatas=[{"user_id": user_id, "interaction_type": "question", "timestamp": timestamp}]
    )

    # Store answer
    vector_db.add_texts(
        texts=[answer],
        embeddings=[answer_embedding],
        metadatas=[{"user_id": user_id, "interaction_type": "answer", "timestamp": timestamp}]
    )


def load_vector_db(user_id, persist_directory_base="backend/db", collection_name="local", embeddings=None):
    """Load an existing user-specific persistent vector database."""
    persist_directory = Path(f"{persist_directory_base}/{user_id}")
    return Chroma(
        embedding_function=embeddings,
        persist_directory=str(persist_directory),
        collection_name=collection_name
    )

def remove_user_data(vector_db):
    """removes entire db"""
    vector_db.reset()

def main():
    # Configuration
    #generell vet inte hur denna ska komma från användaren
    chat_instruction = "ignore all that include chrome.exe"
    template = "You are a network administrator and your job is to find threats inside log files, be thorough and keep the system secure"
    complete_instruction = f"{template} {chat_instruction}"

    log_file_path = Path(__file__).with_name("test.log")  # path
    use_nvidia = False  # sätt till false för amd
    use_cpu = True # sätt till True om inte har dedikerat GPU
    model_name = "llama3.1:latest"
    base_url = "http://127.0.0.1:11434"
    user_id = get_user_id()


    # Setup LLM, embeddings, and data
    ollama_instance = setup_ollama_model(base_url=base_url,
                                                                    model=model_name,
                                                                    complete_instruction=complete_instruction)


    embeddings = setup_embeddings(use_nvidia=use_nvidia,
                                                            use_cpu=use_cpu)
    data = load_document(log_file_path)
    chunks = split_documents(data)

    # load existing or create a new one
    user_directory = Path("backend/db") / user_id
    if user_directory.exists():
        vector_db = load_vector_db(user_id=user_id, embeddings=embeddings)
    else:
        vector_db = setup_vector_db(chunks, embeddings, persist_directory=user_directory)

    # Setup QA chain
    qachain = setup_qa_chain(ollama_instance, vector_db)

    # conversation loop
    while True:
        question = input("Ask a question (or type 'exit' to quit):\n")
        if question.lower() == 'exit':
            break

        try:
            # Use invoke to ensure compatibility with the updated method
            response = qachain.invoke({"query": question})
            print("Raw response from QA chain:", response)

            # Extract answer and print it
            answer = response['result']
            print(f"Answer: {answer}")

            # Store interaction in Chroma DB
            persistent_storage(question, answer, user_id, embeddings, vector_db)

        except Exception as e:
            print("Error during QA chain invocation:", e)
            break

if __name__ == "__main__":
    main()