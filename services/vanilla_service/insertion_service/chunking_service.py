import os
from typing import List, Dict

class ChunkingService:
    def __init__(self, config):
        self.chunk_size = config["chunk_size"]
        self.chunk_overlap = config["chunk_overlap"]
    
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
        text = document["content"]
        metadata = document["metadata"]
        chunks = []
        start = 0
        index = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            chunks.append({
                "content": chunk_text,
                "metadata": metadata.copy(),
                "chunk_index": index,
                "document_id": f"{metadata['filename']}_{index}"
            })
            start += self.chunk_size - self.chunk_overlap
            index += 1
        return chunks