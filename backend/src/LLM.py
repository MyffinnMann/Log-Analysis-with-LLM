"""LLM backend"""
from langchain_ollama import OllamaLLM
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
import torch
import torch_directml # för windows lösningen för cross-platform ser bara weird ut ni är dömda till att ta cpu, sätt de i api denna filen har ingen påverkan för de, obs mikael kommentera ut 37-39 om du kör
# ctr + * för att kommentera ut om jag får be
from datetime import datetime
import re
import os
import time
import logging
import shutil

logging.basicConfig(level=logging.INFO) # detta kanske är onödigt, FREDAG
keywords = ["password", "username", "user_id"] #fyll på denna med vad ni tänker att den inte säga eller ens interagera med

def get_user_id():
    """Used for testing of llm should not be used in api"""
    return "User_1"

def setup_ollama_model(complete_instruction, base_url, model,):
    """Set up the Ollama LLM model instance.
    \n Param 1: instruction witch will be guidance for LLM behavior
    \n Param 2: url and port where Ollama is running
    \n Param 3: model of the running ollama"""

    llm = OllamaLLM(base_url=base_url,
                    model=model,
                    template=complete_instruction,
                    temperature=0.3, # sätter temp lågt för mer deterministiskt resultat
                    max_tokens = 500)
    return llm

def setup_embeddings(use_nvidia, use_cpu):
    """Set up embedding model; can toggle between HuggingFace and Ollama embeddings.
    \n Param 1: True if use Nvidia GPU False for AMD
    \n Param 2: True if use CPU will overwrite param 1"""

    if use_nvidia and not use_cpu:
        return HuggingFaceEmbeddings(show_progress=True,
                                    model_kwargs={"device": "cuda"})
    if not use_nvidia and not use_cpu:
        return HuggingFaceEmbeddings(show_progress=True,
                                    model_kwargs={"device": torch_directml.device()})
    if use_cpu:
        return HuggingFaceEmbeddings(show_progress=True)


def load_document(log_file_path):
    """Load the document from a given file path."""
    log_file = Path(log_file_path)
    if not log_file.exists() or not log_file.is_file():
        raise FileNotFoundError(f"Log file not found: {log_file}")
    loader = TextLoader(log_file)
    try:
        return loader.load()
    except Exception as e:
        raise IOError(f"Error loading document: {e}")


def split_documents(data, chunk_size=1000,
                                chunk_overlap=0):

    """Split the loaded documents into chunks."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,
                                                                            chunk_overlap=chunk_overlap)
    return text_splitter.split_documents(data)


def setup_vector_db(chunks,
                                embeddings, collection_name="local",
                                persist_directory=None):
    """Create a vector database from document chunks and embeddings."""
    return Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=collection_name,
            persist_directory=str(persist_directory)
    )

def delete_vector_db(vector_db):
    """delete the database for a specific user.\nparam: vector db"""
    vector_db.reset_collection()

def setup_qa_chain(llm_instance,
                                vector_db,
                                context_window = 3):

    """Set up the RetrievalQA chain using the LLM instance and vector database retriever."""
    return RetrievalQA.from_chain_type(llm_instance,
                                                            retriever=vector_db.as_retriever(search_type = "mmr",
                                                                                                                search_kwargs={"k" : context_window}))

def persistent_storage(question, answer, user_id, embeddings, vector_db):
    """Store relevant information on a user so that communication can be personalized"""
    timestamp = str(datetime.now())

    # create embedding so they can be stored
    question_text = f"Q: {question}\n"
    answer_text = f"A: {answer}\n"
    question_embedding = embeddings.embed_query(question_text)
    answer_embedding = embeddings.embed_query(answer_text)

    vector_db.add_texts(
        texts=[question_text],
        embeddings=[question_embedding],
        metadatas=[{"user_id": user_id, "interaction_type": "question", "timestamp": timestamp}]
    )
    vector_db.add_texts(
        texts=[answer_text],
        embeddings=[answer_embedding],
        metadatas=[{"user_id": user_id, "interaction_type": "answer", "timestamp": timestamp}]
    )

def load_vector_db(user_id, persist_directory_base="backend/db/vector_db",
                                collection_name="local",
                                embeddings=None):

    """Load an existing user-specific persistent vector database."""
    persist_directory = Path(f"{persist_directory_base}/{user_id}")
    if not persist_directory.exists():
        raise FileNotFoundError(f"User-specific database not found: {persist_directory}")
    return Chroma(
        embedding_function=embeddings,
        persist_directory=str(persist_directory),
        collection_name=collection_name
    )

def sanitize_input(user_input):
    """sanitize and filter user input"""
    sanitized = re.sub(r"[^\w\s\?\!.,-]", "", user_input).strip()
    for keyword in keywords:
        if keyword.lower() in sanitized.lower():
            logging.warning(f"keyword in input: {keyword}")
            return "input contains restricted information."
    return sanitized

def filter_answer(answer):
    """filter the response for keywords before returning it."""
    for keyword in keywords:
        if keyword.lower() in answer.lower():
            logging.warning(f"sensitive content detected in response: {keyword}")
            answer = "can't assist with that request."
    return answer

def rate_limit(last_call_time, rate_limit_sec=1):
    """implement rate limiting"""
    elapsed_time = time.time() - last_call_time
    if elapsed_time < rate_limit_sec:
        time.sleep(rate_limit_sec - elapsed_time)
    return time.time()