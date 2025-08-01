import os
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.schema import Document
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict
from .vector_store import DysonV2VectorStore

class GraphState(TypedDict):
    messages: Annotated[list, add_messages]
    question: str
    documents: List[Document]
    generation: str

class RAGService:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("Missing required environment variable: OPENAI_API_KEY")
        
        # Initialize vector store (handles Pinecone setup internally)
        self.vector_store = DysonV2VectorStore()
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            openai_api_key=self.openai_api_key
        )
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _retrieve_documents(self, state: GraphState) -> GraphState:
        """Retrieve relevant documents from Pinecone"""
        question = state["question"]
        
        # Perform similarity search using our vector store
        documents = self.vector_store.similarity_search(question, k=5)
        
        return {"documents": documents}
    
    def _generate_response(self, state: GraphState) -> GraphState:
        """Generate response using retrieved documents"""
        question = state["question"]
        documents = state["documents"]
        
        if not documents:
            return {"generation": "抱歉，我找不到相關的資料來回答您的問題。請確認您的問題與 DysonV2 相關。"}
        
        # Format context from documents
        context = "\n\n".join([
            f"【來源: {doc.metadata.get('source', 'Unknown')}】\n{doc.page_content}"
            for doc in documents
        ])
        
        # Create prompt
        prompt = f"""你是一個專門回答 DysonV2 相關問題的 AI 助手。請根據以下的參考資料回答用戶的問題。

參考資料：
{context}

用戶問題：{question}

請用繁體中文回答，並且要：
1. 基於提供的參考資料回答
2. 如果參考資料不足以回答問題，請誠實地說明
3. 回答要詳細且有用
4. 保持專業和友好的語調
5. 使用 Markdown 格式，包括：
   - 標題使用 # ## ### 
   - 粗體使用 **文字**
   - 清單使用 - 或 1. 
   - 數學公式使用 LaTeX 語法，單行公式用 $$...$$，行內公式用 $...$
   - 程式碼使用 `code` 或 ```語言

回答："""
        
        try:
            # Generate response
            response = self.llm.invoke(prompt)
            return {"generation": response.content}
        except Exception as e:
            return {"generation": f"生成回答時發生錯誤：{str(e)}"}
    
    def _build_graph(self) -> StateGraph:
        """Build the RAG workflow graph"""
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("retrieve", self._retrieve_documents)
        workflow.add_node("generate", self._generate_response)
        
        # Add edges
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)
        
        return workflow.compile()
    
    async def get_response(self, question: str) -> Dict[str, Any]:
        """Get response for a question using RAG"""
        try:
            # Run the graph
            result = self.graph.invoke({
                "question": question,
                "messages": []
            })
            
            # Extract sources
            sources = []
            if "documents" in result and result["documents"]:
                sources = [
                    f"{doc.metadata.get('source', 'Unknown')} - {doc.metadata.get('chunk_id', 'chunk')}"
                    for doc in result["documents"]
                ]
            
            return {
                "response": result.get("generation", "抱歉，我無法生成回答。"),
                "sources": sources
            }
            
        except Exception as e:
            return {
                "response": f"處理問題時發生錯誤：{str(e)}",
                "sources": []
            }