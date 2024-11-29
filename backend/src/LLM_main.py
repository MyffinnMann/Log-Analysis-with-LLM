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
    user_directory = Path("backend/db/vector_db") / user_id
    if user_directory.exists():
        vector_db = load_vector_db(user_id=user_id, embeddings=embeddings)
    else:
        vector_db = setup_vector_db(chunks, embeddings, persist_directory=user_directory)

    # Setup QA chain
    qachain = setup_qa_chain(ollama_instance, vector_db)
    conversation_history= []
    last_call_time = time.time()

    # conversation loop
    while True:
        question = sanitize_input(input("Ask a question (or type 'exit' to quit):\n"))
        if question.lower() == 'exit':
            break
        last_call_time = rate_limit(last_call_time)

        try:
            relevant_docs = qachain.retriever.get_relevant_documents(question)
            retrieved_context = "\n".join(doc.page_content for doc in relevant_docs)
            history_context = "\n".join([f"Q: {q}\nA: {a}" for q, a in conversation_history[-3:]])
            full_context = f"{history_context}\n{retrieved_context}"

            formatted_prompt = template.format(chat_instruction=chat_instruction, context=full_context, query=question)
            response = qachain.invoke({"query": formatted_prompt})

            answer = response['result']
            filtered_answer= filter_answer(answer)
            print(f"Answer: {filtered_answer}")

            if question and filtered_answer:
                conversation_history = [(question, filtered_answer)]
            persistent_storage(question, answer, user_id, embeddings, vector_db)

        except Exception as e:
            print("Error: Unexpected error, try again", e)
        except ValueError as ve:
            print("Error: input error", ve)
            break

if __name__ == "__main__":
    main()
