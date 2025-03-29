#!/usr/bin/env python3
import sys
import requests
import json

def search_pubmed(query, max_results=10, sort="relevance", since_year=None):
    """
    Search PubMed and return Claude-friendly formatted results
    """
    url = "http://localhost:8000/api/claude_format"
    
    data = {
        "query": query,
        "max_results": max_results,
        "sort": sort
    }
    
    if since_year:
        data["since_year"] = since_year
    
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            return response.json()["formatted_text"]
        else:
            return f"Error: {response.status_code}\n{response.text}"
            
    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to PubMed Assistant server. Make sure it's running with 'python run.py' first."

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: fastmcp_pubmed.py <query> [max_results] [sort] [since_year]")
        sys.exit(1)
    
    query = sys.argv[1]
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    sort = sys.argv[3] if len(sys.argv) > 3 else "relevance"
    since_year = sys.argv[4] if len(sys.argv) > 4 else None
    
    result = search_pubmed(query, max_results, sort, since_year)
    print(result)
