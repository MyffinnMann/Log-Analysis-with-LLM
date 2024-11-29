from LLM import(
    setup_embeddings,
    persistent_storage,
    Path,
    setup_ollama_model,
    load_document,
    load_vector_db,
    split_documents,
    setup_vector_db,
    sanitize_input,
    setup_qa_chain,
    filter_answer,
    get_user_id,
    rate_limit,
    time
)

def main():
    chat_instruction = ""
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

    log_file_path = Path(__file__).with_name("Proxifier.log")  # gör filer efter dokument

    use_nvidia = True
    use_cpu = False

    model_name = "llama3.2:3b"
    base_url = "http://127.0.0.1:11434"
    user_id = get_user_id()

    ollama_instance = setup_ollama_model(base_url=base_url,
                                                        model=model_name,
                                                        complete_instruction=template)

    embeddings = setup_embeddings(use_nvidia=use_nvidia,
                                                            use_cpu=use_cpu)
    data = load_document(log_file_path)
    chunks = split_documents(data)

    user_directory = Path("backend/db/vector_db") / user_id
    if user_directory.exists():
        vector_db = load_vector_db(user_id=user_id, embeddings=embeddings)
    else:
        vector_db = setup_vector_db(chunks, embeddings, persist_directory=user_directory)

    qachain = setup_qa_chain(ollama_instance, vector_db)
    conversation_history= []
    last_call_time = time.time()
