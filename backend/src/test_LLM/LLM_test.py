import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import openpyxl
from LLM import (
    setup_embeddings,
    setup_ollama_model,
    load_document,
    split_documents,
    setup_vector_db,
    setup_qa_chain,
    Path,
    rate_limit,
    time
)

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
    user_id = f"user_{int(time.time())}"

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
    sheet.title = "Test result True Positive" # byt denna till namnet på test varianten
    sheet.append(["Run", "Question", "Answer"])
    for run_number in range(1,51):
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
                answer = response['result']
                sheet.append([run_number, question, answer])
                #  ska in först nedan
                print(f"Run: {run_number}, Q: {question}\nA: {answer}\n")

            except Exception as e:
                print("Error: Unexpected error, try again", e)

    wb.save(excel_path)
    print("filen har sparats")

if __name__ == "__main__":
    log_file_path = Path(__file__).with_name("bruteforcePos.log") # byt denna till filen som du gjort
    questions = [
        "Thoose the log contain a brute force attack?",
        "What configuration shold i add to protect my ssh server?"
    ]
    excel_path = Path("backend/src/test_LLM/Test_Results_TP.xlsx")

    run_test_instance(log_file_path, questions, excel_path)
