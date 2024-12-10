# SecureLang Logs (SLL)

SecureLang Logs (SLL) is a secure logging and chat application designed to handle user authentication, secure communication, and custom log analysis through an intuitive web-based interface.

---

## Project Structure

### **DB.py**
This file handles the SQLite-based user-credential database. It includes:
- User creation and credential storage using Argon2 password hashing.
- Functions for verifying login credentials.
- Session ID generation and mapping functions.
- Creation and management of SQLite tables.

---

### **Login.html**
The login page for the application. It:
- Accepts the username and password.
- Sends login credentials to the backend API for validation.
- Redirects authenticated users to the pre-chat setup page (`PRE_chat.html`).

---

### **Index.html**
The entry point of the application. It:
- Displays the application branding.
- Provides a navigation link to the login page.

---

### **Chat.html**
The main chat interface for users. Features include:
- A bot conversation interface.
- Predefined question buttons for quick queries.
- Handles user-inputted messages and receives bot responses.
- Logout functionality.

---

### **Pre_Chat.html**
The pre-chat setup page where users can:
- Upload log files.
- Provide specific instructions for the chat session.
- Proceed to the chat interface.

---

### **Modular.py**
Handles modular functionalities of the application, making the project extensible and organized. Contains reusable utility functions, which may include:
- File handling utilities.
- Generic helper methods for processing chat data or system configurations.
- Reusable abstractions for modularity.

---

### **API.py**
The Flask-based backend API powering the application. Key features:
- **Login Endpoint**: Validates user credentials and manages sessions.
- **File Upload Endpoint**: Handles log file uploads and integrates instructions for chat analysis.
- **Chat Endpoint**: Processes user messages and returns bot responses.
- **Logout Endpoint**: Terminates active user sessions.
- Provides robust error handling and session management.

---

### **Style.css**
Defines the visual design for the application. Provides consistent styling for:
- Headers, buttons, and forms.
- Chat messages and predefined questions.
- Animations like lock effects on the index page.

---

### **.gitignore**
Specifies which files and directories should be ignored by Git. Includes:
- Caches (`__pycache__`).
- Debugging files.
- Database files (`vector_db`, `user_db`).

---

## Deployment

Follow these steps to set up and run the application:

1. **Database Setup**:
   - Run `create_tables()` in `DB.py` to initialize the database.

2. **Backend**:
   - Install dependencies: `pip install -r requirements.txt`.
   - Start the API server: `python API.py`.

3. **Frontend**:
   - Place all HTML files and `style.css` in the appropriate directories.
   - Open `Index.html` in your browser.

---

## Future Enhancements

- Extend modular utilities to support advanced analytics.
- Enhance API functionality for multi-user environments.
- Refactor frontend for better responsiveness and accessibility.

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