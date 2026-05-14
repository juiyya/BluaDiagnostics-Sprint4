import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

KB_DIR = "./data/knowledge_base"
DB_DIR = "./data/chroma_db"

embeddings = OllamaEmbeddings(model="nomic-embed-text")

def obter_retriever():
    print("[INFO] Inicializando Vector Store (ChromaDB) com Ollama...")
    
    if not os.path.exists(KB_DIR) or not os.listdir(KB_DIR):
        print(f"[AVISO] Pasta {KB_DIR} vazia ou não encontrada.")
        return None

    loader = DirectoryLoader(KB_DIR, glob="**/*.md", loader_cls=TextLoader)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(docs)

    vectorstore = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    
    return vectorstore.as_retriever(search_kwargs={"k": 3})

if __name__ == "__main__":
    print("Iniciando setup manual do ChromaDB...")
    retriever = obter_retriever()
    if retriever:
        print("OK! Banco vetorial criado na pasta data/chroma_db usando nomic-embed-text.")