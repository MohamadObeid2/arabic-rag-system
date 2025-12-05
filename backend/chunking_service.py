import os
from typing import List, Dict

class ChunkingService:
    def __init__(self, config):
        self.mongo_client = None
        self.chunk_size = config["chunk_size"]
        self.chunk_overlap = config["chunk_overlap"]
    
    def set_mongo_client(self, mongo_client):
        self.mongo_client = mongo_client
    
    def load_text_files(self, folder_path: str) -> List[Dict]:
        documents = []
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        stat = os.stat(file_path)
                        
                        doc = {
                            "content": content,
                            "metadata": {
                                "filename": file,
                                "path": file_path,
                                "size": stat.st_size
                            }
                        }
                        
                        documents.append(doc)
                        
                    except Exception:
                        continue
        
        return documents
    
    def split_text(self, text: str) -> List[str]:
        chunks = []
        
        if not text:
            return chunks
        
        words = text.split()
        if len(words) <= self.chunk_size:
            chunks.append(text)
            return chunks
        
        start = 0
        while start < len(words):
            end = start + self.chunk_size
            
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            chunks.append(chunk_text)
            
            if end >= len(words):
                break
            
            start = end - self.chunk_overlap
        
        return chunks
    
    def create_chunks(self, document):
        text = document["content"]
        metadata = document["metadata"]
        
        text_chunks = self.split_text(text)
        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            chunk_data = {
                "content": chunk_text,
                "metadata": metadata.copy(),
                "chunk_index": i,
                "document_id": f"{metadata['filename']}_{i}"
            }
            chunks.append(chunk_data)
        return chunks
    
    def store_chunks(self, chunks):
        if not self.mongo_client:
            return []
        return self.mongo_client.store_chunks(chunks)