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
template = ""
