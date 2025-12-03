import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing /health...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_system_config():
    print("Testing /api/system GET...")
    response = requests.get(f"{BASE_URL}/api/system")
    print(f"Status: {response.status_code}")
    config = response.json()
    print(f"Config: {json.dumps(config, indent=2)}")
    print()
    
    print("Testing /api/system POST...")
    new_config = {
        "chunk_size": 600,
        "chunk_overlap": 100,
        "top_k": 3,
        "similarity_threshold": 0.4
    }
    response = requests.post(f"{BASE_URL}/api/system", json=new_config)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_chat():
    print("Testing /api/chat...")
    chat_data = {"question": "ما هو الذكاء الاصطناعي؟"}
    response = requests.post(f"{BASE_URL}/api/chat", json=chat_data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Answer: {result.get('answer', '')[:100]}...")
    print(f"Sources count: {len(result.get('sources', []))}")
    print()

def test_search():
    print("Testing /api/search...")
    response = requests.get(f"{BASE_URL}/api/search", params={"query": "تعلم آلي", "top_k": 2})
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Results: {len(result.get('results', []))}")
    print()

def test_documents():
    print("Testing /api/documents...")
    response = requests.get(f"{BASE_URL}/api/documents")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Documents: {len(result.get('documents', []))}")
    print()

def test_all():
    print("=" * 50)
    print("Testing Arabic RAG System APIs")
    print("=" * 50)
    
    try:
        test_health()
        time.sleep(1)
        test_system_config()
        time.sleep(1)
        test_chat()
        time.sleep(1)
        test_search()
        time.sleep(1)
        test_documents()
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to server. Make sure it's running.")
        print("Run: uvicorn backend.main:app --reload")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_all()