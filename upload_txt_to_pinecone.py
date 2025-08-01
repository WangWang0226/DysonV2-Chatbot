import os
from pathlib import Path
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
import sys

# Add the backend directory to the path to import our modules
sys.path.append('backend')
from app.services.vector_store import DysonV2VectorStore

load_dotenv()

def ingest_txt() -> None:
    """
    將 DysonV2 TXT 文件上傳到 Pinecone vector store (使用傳統方式)
    """
    # TXT 文件路徑
    txt_path = "dyson-v2-knowledge.txt"
    
    if not Path(txt_path).exists():
        raise FileNotFoundError(f"TXT file not found: {txt_path}")
    
    print(f"Loading TXT: {txt_path}")
    
    try:
        # 初始化 vector store
        vector_store = DysonV2VectorStore()
        
        # 載入 TXT
        loader = TextLoader(txt_path, encoding='utf-8')
        raw_documents = loader.load()
        print(f"Loaded {len(raw_documents)} documents from TXT")
        
        # 文本分割器
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # 分割文檔
        documents = text_splitter.split_documents(raw_documents)
        print(f"Split into {len(documents)} chunks")
        
        # 為每個文檔塊添加更詳細的 metadata
        for i, doc in enumerate(documents):
            doc.metadata.update({
                "source": "DysonV2.txt",
                "document_type": "knowledge_base",
                "chunk_id": f"chunk_{i}",
                "total_chunks": len(documents)
            })
        
        # 可選：清除舊資料
        print("Do you want to clear existing documents in the vector store? (y/N): ", end="")
        clear_response = input().strip().lower()
        
        if clear_response == 'y':
            print("Clearing existing documents...")
            vector_store.delete_all_documents()
        
        # 上傳文檔到 Pinecone (使用 LangChain 的簡單方式)
        print(f"Starting to upload {len(documents)} document chunks to Pinecone...")
        
        success = vector_store.add_documents(documents)
        
        if success:
            print("****** Successfully uploaded DysonV2 TXT to Pinecone vector store ******")
            print(f"Total chunks uploaded: {len(documents)}")
            
            # 顯示索引統計
            stats = vector_store.get_stats()
            if stats:
                print(f"Index stats: {stats}")
        else:
            print("Failed to upload documents")
        
    except Exception as e:
        print(f"Error during TXT processing: {str(e)}")
        raise


def test_vector_store() -> None:
    """
    測試 vector store 是否正常工作
    """
    print("\n=== Testing Vector Store ===")
    
    try:
        # 初始化 vector store
        vector_store = DysonV2VectorStore()
        
        # 測試搜尋
        test_query = "什麼是 DysonV2"
        results = vector_store.similarity_search(test_query, k=3)
        
        print(f"Test query: '{test_query}'")
        print(f"Found {len(results)} similar documents:")
        
        for i, doc in enumerate(results, 1):
            print(f"\n--- Result {i} ---")
            print(f"Content preview: {doc.page_content[:200]}...")
            print(f"Metadata: {doc.metadata}")
            
    except Exception as e:
        print(f"Error during testing: {str(e)}")


if __name__ == "__main__":
    print("=== DysonV2 TXT to Pinecone Uploader (Traditional Method) ===")
    
    try:
        ingest_txt()
        test_vector_store()
    except Exception as e:
        print(f"Script failed: {str(e)}")
        exit(1)