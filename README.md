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
