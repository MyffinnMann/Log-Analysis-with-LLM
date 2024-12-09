"""Config file (LLM, hardware etc.)"""
# Configure hardware or software acceleration for embedding (NVIDIA, AMD, CPU)
# - For NVIDIA use: "use_nvidia = True" and "use_cpu = False"
# - For AMD use: "use_nvidia = False" and "use_cpu = False"
# - For CPU use: "use_nvidia = False" and "use_cpu = True"
use_nvidia = False
use_cpu = True


# Configure LLM
model_name = "llama3.2"
base_url = "http://127.0.0.1:11434"
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
LOGIN_LIMIT = 3