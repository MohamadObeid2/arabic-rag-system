import os
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ChunkingService:
    def __init__(self, config):
        self.chunk_size = config["chunk_size"]
        self.chunk_overlap = config["chunk_overlap"]
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
    
    def load_text_files(self, folder_path: str) -> List[Dict]:
        documents = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.txt'):
                    path = os.path.join(root, file)
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    stat = os.stat(path)
                    documents.append({
                        "content": content,
                        "metadata": {
                            "filename": file,
                            "path": path,
                            "size": stat.st_size
                        }
                    })
        return documents
    
    def create_chunks(self, document) -> List[Dict]:
        text_chunks = self.text_splitter.split_text(document["content"])
        metadata = document["metadata"]
        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            chunks.append({
                "content": chunk_text,
                "metadata": metadata.copy(),
                "chunk_index": i,
                "document_id": f"{metadata['filename']}_{i}"
            })
        return chunks