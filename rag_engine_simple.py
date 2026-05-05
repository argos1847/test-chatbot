from langchain_community.vectorstores import Chroma
import requests
import os
import json

class PhysicsChatbot:
    def __init__(self, chroma_db_path="./chroma_db"):
        print("Loading chatbot...")
        
        # Load your vector database WITHOUT embeddings
        # We'll do simple text matching instead
        self.db_path = chroma_db_path
        
        # Load the raw data
        try:
            # ChromaDB stores data in parquet files
            # We'll load them directly
            from chromadb import Client
            from chromadb.config import Settings
            
            self.client = Client(Settings(
                persist_directory=chroma_db_path,
                anonymized_telemetry=False
            ))
            
            # Get your collection
            collections = self.client.list_collections()
            if collections:
                self.collection = collections[0]
                print(f"✅ Loaded collection: {self.collection.name}")
            else:
                raise ValueError("No collections found in ChromaDB")
                
        except Exception as e:
            print(f"Error loading ChromaDB: {e}")
            raise
        
        # Get Groq key
        self.groq_key = os.environ.get("GROQ_API_KEY")
        if not self.groq_key:
            print("⚠️ GROQ_API_KEY not set!")
            print("Get free key at: https://console.groq.com")
            raise ValueError("Need GROQ_API_KEY")
        
        print("✅ Chatbot ready!")
    
    def retrieve_context(self, query, k=5):
        """Get relevant papers using simple text search"""
        try:
            # Query the collection
            results = self.collection.query(
                query_texts=[query],
                n_results=k
            )
            
            # Extract documents and metadata
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            
            sources = []
            for i, (doc, meta) in enumerate(zip(documents, metadatas)):
                sources.append({
                    'content': doc,
                    'title': meta.get('title', 'Unknown'),
                    'paper_id': meta.get('paper_id', 'Unknown'),
                    'authors': meta.get('authors', 'Unknown')
                })
            
            # Build context string
            context_parts = []
            for source in sources:
                context_parts.append(f"[{source['title']}]\n{source['content']}\n")
            
            context = "\n---\n".join(context_parts)
            return context, sources
            
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return "", []
    
    def query(self, user_question):
        """Answer question using Groq"""
        
        # Get context from papers
        context, sources = self.retrieve_context(user_question, k=5)
        
        if not context:
            return {
                'answer': "Sorry, I couldn't find relevant papers to answer your question.",
                'sources': []
            }
        
        # Call Groq API
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.groq_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-70b-versatile",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a physics research assistant. Answer questions based on the provided research papers. Cite papers by title when referencing them."
                        },
                        {
                            "role": "user",
                            "content": f"""Research Papers Context:
{context}

Question: {user_question}

Provide a detailed answer based on the papers above. Cite the paper titles when relevant."""
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content']
            else:
                answer = f"Error calling Groq API: {response.status_code} - {response.text}"
            
        except Exception as e:
            answer = f"Error: {str(e)}"
        
        return {
            'answer': answer,
            'sources': sources
        }