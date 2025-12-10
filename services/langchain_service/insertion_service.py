import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Milvus
from pymilvus import connections
import shutil
import torch
import os
import tempfile

class InsertionService:
    def __init__(self, config):
        self.config = config
        self.embdedding_model = config.embedding_model
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap
        )
        
        device = get_best_device()
        self.model = HuggingFaceEmbeddings(
            model_name=self.embdedding_model,
            model_kwargs={"device": device},
            encode_kwargs={"normalize_embeddings": True}
        )
        
        connections.connect(
            host=config.milvus_host,
            port=config.milvus_port
        )
        
        self.collection_name = "arabic_docs_langchain"
        self.init_collection()

    def init_collection(self):
        self.vector_store = Milvus(
            embedding_function=self.model,
            collection_name=self.collection_name,
            connection_args={
                "host": self.config.milvus_host,
                "port": self.config.milvus_port
            },
            auto_id=True
        )

    def load_and_split_documents(self, folder_path):
        loader = DirectoryLoader(
            folder_path,
            glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        
        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)
        return chunks

    def embed_text(self, text):
        return self.model.embed_query(text)

    def embed_documents(self, documents):
        texts = [doc["content"] for doc in documents]
        return self.model.embed_documents(texts)
    
    async def upload(self, files):
        temp_dir = tempfile.mkdtemp()
        uploaded_files = []
        for file in files:
            if file.filename.endswith('.txt'):
                file_path = os.path.join(temp_dir, file.filename)
                content = await file.read()
                with open(file_path, "wb") as f:
                    f.write(content)
                uploaded_files.append({
                    "filename": file.filename,
                    "size": len(content)
                })
        
        chunks = self.load_and_split_documents(temp_dir)
        self.store(chunks)
        
        shutil.rmtree(temp_dir)
        
        return {
            "success": True,
            "message": f"تم معالجة {len(uploaded_files)} وثيقة و {len(chunks)} جزء",
            "files": uploaded_files
        }

    def store(self, chunks):
        texts = [chunk.page_content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        
        self.vector_store.add_texts(
            texts=texts,
            metadatas=metadatas
        )
    
def get_best_device():
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"