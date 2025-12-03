import os
from typing import List, Dict

class ChunkingService:
    def __init__(self):
        self.mongo_service = None
    
    def set_mongo_service(self, mongo_service):
        self.mongo_service = mongo_service
    
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
    
    def split_text(self, text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
        chunks = []
        
        if not text:
            return chunks
        
        words = text.split()
        
        if len(words) <= chunk_size:
            chunks.append(text)
            return chunks
        
        start = 0
        while start < len(words):
            end = start + chunk_size
            
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            chunks.append(chunk_text)
            
            if end >= len(words):
                break
            
            start = end - chunk_overlap
        
        return chunks
    
    def create_chunks(self, document, chunk_size=500, chunk_overlap=50):
        text = document["content"]
        metadata = document["metadata"]
        
        text_chunks = self.split_text(text, chunk_size, chunk_overlap)
        
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
        if not self.mongo_service:
            return []
        return self.mongo_service.store_chunks(chunks)