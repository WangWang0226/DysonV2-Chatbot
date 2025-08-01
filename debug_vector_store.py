import os
import sys
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.append('backend')
from app.services.vector_store import DysonV2VectorStore

load_dotenv()

def debug_vector_store():
    """Debug vector store issues"""
    print("=== Debugging Vector Store ===")
    
    try:
        # Initialize vector store
        vector_store = DysonV2VectorStore()
        
        # Check index stats
        print("\n1. Checking index statistics...")
        stats = vector_store.get_stats()
        if stats:
            print(f"Index stats: {stats}")
            print(f"Total vectors: {stats.total_vector_count}")
            print(f"Dimension: {stats.dimension}")
        else:
            print("Could not get index stats")
            
        # Try a simple test document
        print("\n2. Testing with a simple document...")
        from langchain.schema import Document
        
        test_doc = Document(
            page_content="DysonV2 是一個測試文檔",
            metadata={"source": "test", "type": "debug"}
        )
        
        # Add test document
        success = vector_store.add_documents([test_doc])
        print(f"Added test document: {success}")
        
        # Check stats again
        stats = vector_store.get_stats()
        if stats:
            print(f"New total vectors: {stats.total_vector_count}")
            
        # Test search
        print("\n3. Testing search...")
        results = vector_store.similarity_search("DysonV2", k=3)
        print(f"Found {len(results)} documents")
        
        for i, doc in enumerate(results):
            print(f"Document {i+1}: {doc.page_content[:100]}...")
            print(f"Metadata: {doc.metadata}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_vector_store()