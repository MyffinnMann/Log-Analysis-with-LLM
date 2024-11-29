from LLM import(
    setup_embeddings,
    Path,
    setup_ollama_model,
    load_document,
    split_documents,
    setup_vector_db,
    setup_qa_chain,
    filter_answer,
    get_user_id,
    rate_limit,
    time
)
import openpyxl

def run_test_instance(log_file_path, questions, excel_path):
    """Runs an one instance of ollama with a specific question"""
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
    vector_db = setup_vector_db(chunks, embeddings, persist_directory=user_directory)

    qachain = setup_qa_chain(ollama_instance, vector_db)

    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = "Test result" # byt denna till namnet på test varianten
    sheet.append(["Question", "Answer"])

    for question in questions:
        try:
            last_call_time = time.time()
            last_call_time = rate_limit(last_call_time)
            relevant_docs = qachain.retriever.get_relevant_documents(question)
            retrieved_context = "\n".join(doc.page_content for doc in relevant_docs)

            formatted_prompt = template.format(chat_instruction=chat_instruction,
                                                                    context=retrieved_context,
                                                                    query=question)
            response = qachain.invoke({"query": formatted_prompt})
            filtered_answer= filter_answer( response['result'])
            sheet.append([question, filtered_answer])
            print(f"Q: {question}\nA: {filtered_answer}\n")

        except Exception as e:
            print("Error: Unexpected error, try again", e)

    wb.save(excel_path)
    print("filen har sparats")

if __name__ == "__main__":
    log_file_path = Path(__file__).with_name("Proxifier.log") # byt denna till filen som du gjort
    questions = [
        "brute force?",
        "vad kan jag göra på en ssh server?"
    ]
    excel_path = "Test_Results.xlsx"

    run_test_instance(log_file_path, questions, excel_path)


# koluument a1 s1 a2 s2
# kör 50 gng typ
# de olika logfilerna
# frågor
