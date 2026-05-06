import json
import requests
import os

class SimpleChatbot:
    def __init__(self, papers_file="papers_database.json"):
        """Load papers from JSON file"""
        print("Loading papers...")
        
        # Load papers
        with open(papers_file, 'r', encoding='utf-8') as f:
            self.papers = json.load(f)
        
        print(f"✅ Loaded {len(self.papers)} papers")
        
        # Get Groq key
        self.groq_key = os.environ.get("GROQ_API_KEY")
        if not self.groq_key:
            raise ValueError("Set GROQ_API_KEY environment variable")
    
    def search_papers(self, query, max_results=3):
        """Simple keyword search"""
        query_lower = query.lower()
        results = []
        
        for paper in self.papers:
            # Simple relevance: count keyword matches
            content_lower = paper['content'].lower()
            
            # Count how many query words appear
            query_words = query_lower.split()
            matches = sum(1 for word in query_words if word in content_lower)
            
            if matches > 0:
                results.append({
                    'paper': paper,
                    'score': matches
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top results
        return [r['paper'] for r in results[:max_results]]
    
    def query(self, user_question):
        """Answer question using papers"""
        
        # Search for relevant papers
        relevant_papers = self.search_papers(user_question, max_results=3)
        
        if not relevant_papers:
            return {
                'answer': "I couldn't find relevant papers for your question.",
                'sources': []
            }
        
        # Build context (truncate papers to avoid token limits)
        context_parts = []
        for paper in relevant_papers:
            # Take first 2000 characters of each paper
            snippet = paper['content'][:2000]
            context_parts.append(f"Paper: {paper['filename']}\n{snippet}\n")
        
        context = "\n---\n".join(context_parts)
        
        # Call Groq
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
                            "content": "You are a physics research assistant. Answer based on the provided papers."
                        },
                        {
                            "role": "user",
                            "content": f"Papers:\n{context}\n\nQuestion: {user_question}"
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1500
                }
            )
            
            answer = response.json()['choices'][0]['message']['content']
            
        except Exception as e:
            answer = f"Error: {str(e)}"
        
        # Prepare sources
        sources = [
            {
                'filename': p['filename'],
                'paper_id': p['paper_id']
            } for p in relevant_papers
        ]
        
        return {
            'answer': answer,
            'sources': sources
        }
