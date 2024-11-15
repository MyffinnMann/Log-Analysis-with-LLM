from langchain_ollama import OllamaLLM
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
import torch
from datetime import datetime

# Uncomment the following line and line 39-41 if using AMD
#import torch_directml

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
                    temperature=0.3) #sätter temp lågt för mer deterministiskt resultat
    return llm


def setup_embeddings(use_nvidia, use_cpu):
    """Set up embedding model; can toggle between HuggingFace and Ollama embeddings.
    \n Param 1: True if use Nvidia GPU False for AMD
    \n Param 2: True if use CPU will overwrite param 1"""

    if use_nvidia and not use_cpu:
        return HuggingFaceEmbeddings(show_progress=True,
                                    model_kwargs={"device": "cuda"})
    #if not use_nvidia and not use_cpu:
        #return HuggingFaceEmbeddings(show_progress=True,
                                    #model_kwargs={"device": torch_directml.device()})
    if use_cpu:
        return HuggingFaceEmbeddings(show_progress=True)


def load_document(log_file_path):
    """Load the document from a given file path."""
    log_file = Path(log_file_path)
    loader = TextLoader(log_file)
    return loader.load()


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

def load_vector_db(user_id, persist_directory_base="backend/db",
                                collection_name="local",
                                embeddings=None):

    """Load an existing user-specific persistent vector database."""
    persist_directory = Path(f"{persist_directory_base}/{user_id}")
    return Chroma(
        embedding_function=embeddings,
        persist_directory=str(persist_directory),
        collection_name=collection_name
    )

def remove_user_data(vector_db):
    """removes entire db, if loaded or created"""
    vector_db.reset()

def main():
    chat_instruction = "ignore all that include chrome.exe"
    template = """
    You are an AI assistant specialized in analyzing security issues from log files.
    Follow these instructions: {chat_instruction}
    Use the provided log file context to answer the user's current question.
    Focus solely on the current question and avoid referencing previous interactions unless necessary.
    Keep your response under 200 words.

    {context}

    User Question: {query}

    Answer:
    """
    log_file_path = Path(__file__).with_name("Proxifier.log")  # path

    # detta ska sättas här och i api ska inte vara beroende på denna filen om de är de säg till mig /oscar
    use_nvidia = True  # sätt till false för amd
    use_cpu = False # sätt till True om inte har dedikerat GPU

    model_name = "llama3.2:3b" #sätter till denna så den senaste inte matcher den vi har....
    #om ni har latest är de 3b men kommer inte fungera om ni inte pullat 3b specifikt
    # kör detta: ollama pull llama3.2:3b
    base_url = "http://127.0.0.1:11434"
    user_id = get_user_id()

    ollama_instance = setup_ollama_model(base_url=base_url,
                                                                    model=model_name,
                                                                    complete_instruction=template)

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

    conversation_history= []

    # conversation loop
    while True:
        question = input("Ask a question (or type 'exit' to quit):\n")
        if question.lower() == 'exit':
            break

        try:
            relevant_docs = qachain.retriever.get_relevant_documents(question)
            retrieved_context = "\n".join(doc.page_content for doc in relevant_docs)

            history_context = "\n".join([f"Q: {q}\nA: {a}" for q, a in conversation_history])
            full_context = f"{history_context}\n{retrieved_context}"

            formatted_prompt = template.format(chat_instruction=chat_instruction, context=full_context, query=question)
            response = qachain.invoke({"query": formatted_prompt})

            answer = response['result']
            print(f"Answer: {answer}")

            conversation_history.append((question, answer))
            persistent_storage(question, answer, user_id, embeddings, vector_db)

        except Exception as e:
            print("Error during QA chain invocation:", e)
            break

if __name__ == "__main__":
    main()
