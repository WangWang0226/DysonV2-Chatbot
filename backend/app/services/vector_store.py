from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

class DysonV2VectorStore:
    def __init__(self):
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX_NAME")
        
        if not all([self.pinecone_api_key, self.openai_api_key, self.index_name]):
            raise ValueError("Missing required environment variables: PINECONE_API_KEY, OPENAI_API_KEY, PINECONE_INDEX_NAME")
        
        # Initialize Pinecone
        pc = Pinecone(api_key=self.pinecone_api_key)
        
        # Create index if it doesn't exist
        if self.index_name not in pc.list_indexes().names():
            print(f"Creating index: {self.index_name}")
            pc.create_index(
                name=self.index_name,
                dimension=1536,  # dimensionality of text-embedding-3-small
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            print(f"Index {self.index_name} created successfully")
        else:
            print(f"Using existing index: {self.index_name}")

        self.index = pc.Index(self.index_name)
        
        # Initialize embeddings with OpenAI
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=self.openai_api_key
        )
        
        # Initialize LangChain PineconeVectorStore
        self.vector_store = PineconeVectorStore(
            index=self.index, 
            embedding=self.embeddings, 
            text_key="text"
        )

    def add_documents(self, documents):
        """Add documents to the vector store"""
        try:
            self.vector_store.add_documents(documents)
            print(f"Successfully added {len(documents)} documents to vector store")
            return True
        except Exception as e:
            print(f"Error adding documents: {str(e)}")
            return False

    def similarity_search(self, query, k=5):
        """Perform similarity search"""
        try:
            return self.vector_store.similarity_search(query, k=k)
        except Exception as e:
            print(f"Error performing similarity search: {str(e)}")
            return []
    
    def as_retriever(self, k=5):
        """Return as LangChain retriever"""
        return self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )

    def delete_all_documents(self):
        """Delete all documents from the Pinecone index"""
        try:
            # Delete all vectors in the index
            self.index.delete(delete_all=True)
            print(f"Successfully deleted all documents from index: {self.index_name}")
            return True
        except Exception as e:
            print(f"Error deleting documents from index: {str(e)}")
            return False
    
    def get_stats(self):
        """Get index statistics"""
        try:
            stats = self.index.describe_index_stats()
            return stats
        except Exception as e:
            print(f"Error getting index stats: {str(e)}")
            return None