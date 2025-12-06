import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader

class ChunkingService:
    def __init__(self, config):
        self.config = config
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
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
        
        chunk_docs = []
        for i, chunk in enumerate(chunks):
            chunk_docs.append({
                "content": chunk.page_content,
                "metadata": {
                    "filename": os.path.basename(chunk.metadata["source"]),
                    "path": chunk.metadata["source"],
                    "chunk_index": i
                }
            })
        
        return chunk_docs