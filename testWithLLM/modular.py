from langchain_community.llms import Ollama
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Adjusted import path
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
import torch

def setup_ollama_model(complete_instruction,
                                        base_url="http://127.0.0.1:11434",
                                        model="llama3.1",):
    """Set up the Ollama LLM model instance."""

    llm = Ollama(base_url=base_url, model=model, template=complete_instruction)
    return llm


def setup_embeddings(use_nvidia=True):
    """Set up embedding model; can toggle between HuggingFace and Ollama embeddings."""
    if use_nvidia:
        return HuggingFaceEmbeddings(show_progress=True, model_kwargs={"device": "cuda"})
    else:
        return HuggingFaceEmbeddings(show_progress=True, model_kwargs={"device": torch.device()})


def load_document(log_file_path):
    """Load the document from a given file path."""
    log_file = Path(log_file_path)
    loader = TextLoader(log_file)
    return loader.load()


def split_documents(data, chunk_size=1000, chunk_overlap=200):
    """Split the loaded documents into chunks."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return text_splitter.split_documents(data)


def setup_vector_db(chunks, embeddings, collection_name="local"):
    """Create a vector database from document chunks and embeddings."""
    return Chroma.from_documents(documents=chunks, embedding=embeddings, collection_name=collection_name)


def setup_qa_chain(llm_instance, vector_db):
    """Set up the RetrievalQA chain using the LLM instance and vector database retriever."""
    return RetrievalQA.from_chain_type(llm_instance, retriever=vector_db.as_retriever())

def main():
    # Configuration
    #generell vet inte hur denna ska komma från användaren
    chat_instruction = "ignore all that include chrome.exe"
    template = "You are a network administrator and your job is to find threats inside log files, be thorough and keep the system secure"
    complete_instruction = f"{template} {chat_instruction}"

    log_file_path = Path(__file__).with_name("Proxifier.log")  # path
    use_nvidia = True  # sätt till false för amd
    model_name = "llama3.1"
    base_url = "http://127.0.0.1:11434"


    # Setup LLM, embeddings, and data
    ollama_instance = setup_ollama_model(base_url=base_url,
                                                                    model=model_name,
                                                                    complete_instruction=complete_instruction)


    embeddings = setup_embeddings(use_nvidia=use_nvidia)
    data = load_document(log_file_path)


    # Split document and create vector store
    chunks = split_documents(data)
    vector_db = setup_vector_db(chunks, embeddings)

    # Setup QA chain
    qachain = setup_qa_chain(ollama_instance, vector_db)

    question = input("Ask a question\n")
    response = qachain({"query": question})
    print(f"Answer: {response['result']}")

if __name__ == "__main__":
    main()