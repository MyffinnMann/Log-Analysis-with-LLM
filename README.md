# SecureLang Logs (SLL)

SecureLang Logs (SLL) is a secure logging and chat application designed to handle user authentication, secure communication, and custom log analysis through an intuitive web-based interface.

## Team Members
- Ibrahim Abd Ulrahman
- Samuel Ek
- Natnael Kidane
- Mikael Strandlund
- Melvin Ferdinandsson
- Oscar Lövkvist Larsson

## Project Folder Structure
- Backend: Contains the server-side code for the application.
- Oscar fortsätter 

Follow these steps to set up and run the application:

1. **Installations**:
   - Install dependencies: `pip install -r requirements.txt`.
   - GPU acceleration:
      - With Nvidia use Cuda: https://pytorch.org/
      - AMD solution works with windows only
   - Download and run Ollama on local machine: https://ollama.com/download
      - Run a model on ollama and match it's information in the config file. Recommended model llama3.2:3B
   - Optional
      - Set-up nginx as reverse proxy. Check file nginx.md for more information

2. **Database Setup**:
   - vi behöver göra en riktig fil som bara gör detta

3. **Run**
   - Run api.py, this is run on the local machine so go to http://127.0.0.1:5000/ or http://localhost:5000/
   - Add username and password in database file or use existing

---

## Libraries used in the project:
- **[Flask](https://pypi.org/project/Flask/)**: Flask is a lightweight python web application framework.
- **[Langchain](https://pypi.org/project/langchain/)**: LangChain is a framework for developing applications powered by large language models (LLMs).
- **[langchain-community](https://pypi.org/project/langchain-community/)**: LangChain Community contains third-party integrations that implement the base interfaces defined in LangChain Core, making them ready-to-use in any LangChain application.
- **[langchain-ollama](https://pypi.org/project/langchain-ollama/)**: This package contains the LangChain integration with Ollama. Ollama needs to run locally.
- **[langchain-chroma](https://pypi.org/project/langchain-chroma/)**: This package contains the LangChain integration with Chroma.
- **[langchain-huggingface](https://pypi.org/project/langchain-huggingface/)**: This package contains the LangChain integrations for huggingface related classes.
- **[torch](https://pypi.org/project/torch/)**: Tensors and Dynamic neural networks in Python with strong GPU acceleration
- **[torch-directml](https://pypi.org/project/torch-directml/)**: A DirectML backend for hardware acceleration in PyTorch.
- **[torchvision](https://pypi.org/project/torchvision/)**: Image and video datasets and models for torch deep learning
- **[torchaudio](https://pypi.org/project/torchaudio/)**: An audio package for PyTorch
- **[chromadb](https://pypi.org/project/chromadb/)**: Open-source embedding database.
- **[huggingface-hub](https://pypi.org/project/huggingface-hub/)**: Client library to download and publish models, datasets and other repos on the huggingface.co hub
- **[argon2-cffi](https://pypi.org/project/argon2-cffi/)**: Argon2 for Python
- **[Flask-Limiter](https://pypi.org/project/Flask-Limiter/)**: Rate limiting for flask applications

---
