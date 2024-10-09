from langchain_community.llms import Ollama
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import  OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
import torch

ollama_instance = Ollama(base_url = "http://127.0.0.1:11434", model = "llama3.1")

hf = HuggingFaceEmbeddings(show_progress = True, model_kwargs = {"device" : "cuda"})




# log_file = Path(__file__).with_name("SSH.log") # 20mb
# loader = TextLoader(log_file)

prox_log = Path(__file__).with_name("Proxifier.log") # 2mb
loader = TextLoader(prox_log)

#test_log = Path(__file__).with_name("test.log") # 10 rader
#loader = TextLoader(test_log)

data = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(data)

vector_db = Chroma.from_documents(documents=chunks, embedding=hf,collection_name="local")

qachain = RetrievalQA.from_chain_type(ollama_instance, retriever=vector_db.as_retriever())

question = input("Ask a question\n")
print(qachain({"query": question}))


