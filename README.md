# SecureLang Logs (SLL)

SecureLang Logs (SLL) is a secure logging and chat application designed to handle user authentication, secure communication, and custom log analysis through an intuitive web-based interface.

## Deployment

Follow these steps to set up and run the application:

1. **Installations**:
   - Install dependencies: `pip install -r requirements.txt`.
   - GPU acceleration:
      - With Nvidia use Cuda: https://pytorch.org/
      - AMD solution works with windows only
   - Download and run Ollama on local machine: https://ollama.com/download
      - Run a model on ollama and match it's information in the config file. Recommended model llama3.2:3B

2. **Database Setup**:
   - vi behöver göra en riktig fil som bara gör detta

3. **Run**
   - Run api.py, this is run on the local machine so go to http://127.0.0.1:5000/ or http://localhost:5000/
   - Add username and password in database file or use existing


gör requirements för AMD och nvidia? dock är de fucked med linux
nginx? om de ska vara med måste de vara riktigt simpelt att göra och fungera på windows och linux och gärna vara i en fil vi "styr".