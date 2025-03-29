import httpx
import asyncio
import json
from typing import Dict, List, Optional, Any
import urllib.parse

class PubMedClient:
    """Client for interacting with the PubMed E-utilities API"""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def search(self, query: str, max_results: int = 10, 
                    sort: str = "relevance", date_range: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Search PubMed for articles matching the query
        
        Args:
            query: The search query using PubMed syntax
            max_results: Maximum number of results to return
            sort: Sort order - "relevance" or "date"
            date_range: Optional date range filter {"from": "YYYY/MM/DD", "to": "YYYY/MM/DD"}
            
        Returns:
            List of article data
        """
        # Step 1: Use esearch to get IDs
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "usehistory": "y",
            "retmode": "json"
        }
        
        if self.api_key:
            search_params["api_key"] = self.api_key
        
        # Add date range if provided
        if date_range:
            if "from" in date_range and "to" in date_range:
                search_params["datetype"] = "pdat"  # Publication date
                search_params["mindate"] = date_range["from"].replace("/", "")
                search_params["maxdate"] = date_range["to"].replace("/", "")
        
        # Add sort order
        if sort == "date":
            search_params["sort"] = "pub date"
        
        # Execute search
        search_url = f"{self.BASE_URL}/esearch.fcgi"
        search_response = await self.client.get(search_url, params=search_params)
        search_response.raise_for_status()
        search_data = search_response.json()
        
        # Extract IDs and WebEnv, QueryKey for history server
        id_list = search_data["esearchresult"]["idlist"]
        web_env = search_data["esearchresult"]["webenv"]
        query_key = search_data["esearchresult"]["querykey"]
        
        if not id_list:
            return []
        
        # Step 2: Use efetch to get full article data
        fetch_params = {
            "db": "pubmed",
            "query_key": query_key,
            "WebEnv": web_env,
            "retmax": max_results,
            "retmode": "xml",
        }
        
        if self.api_key:
            fetch_params["api_key"] = self.api_key
        
        fetch_url = f"{self.BASE_URL}/efetch.fcgi"
        fetch_response = await self.client.get(fetch_url, params=fetch_params)
        fetch_response.raise_for_status()
        
        xml_content = fetch_response.text
        articles = self._process_xml_response(xml_content, id_list)
        
        return articles
    
    def _extract_xml_tag(self, xml: str, tag_name: str, start_idx: int = 0) -> str:
        """Extract content from an XML tag"""
        start_tag = f"<{tag_name}>"
        end_tag = f"</{tag_name}>"
        
        start = xml.find(start_tag, start_idx)
        if start == -1:
            # Try with attributes
            start = xml.find(f"<{tag_name} ", start_idx)
            if start == -1:
                return ""
                
            # Find the closing >
            start = xml.find(">", start)
            if start == -1:
                return ""
            start += 1
        else:
            start += len(start_tag)
            
        end = xml.find(end_tag, start)
        if end == -1:
            return ""
            
        return xml[start:end].strip()
    
    def _process_xml_response(self, xml_content: str, id_list: List[str]) -> List[Dict[str, Any]]:
        """Process XML response from PubMed"""
        articles = []
        
        for pmid in id_list:
            # Find article section
            article_start = xml_content.find(f"<PubmedArticle>")
            if article_start == -1:
                continue
                
            article_end = xml_content.find("</PubmedArticle>", article_start)
            if article_end == -1:
                continue
                
            article_xml = xml_content[article_start:article_end + 16]
            
            # Extract basic information
            title = self._extract_xml_tag(article_xml, "ArticleTitle")
            abstract = self._extract_xml_tag(article_xml, "AbstractText")
            journal = self._extract_xml_tag(article_xml, "Title")
            year = self._extract_xml_tag(article_xml, "Year")
            month = self._extract_xml_tag(article_xml, "Month")
            
            # Extract authors
            authors = []
            author_idx = 0
            while True:
                last_name = self._extract_xml_tag(article_xml, "LastName", start_idx=author_idx)
                if not last_name:
                    break
                    
                fore_name = self._extract_xml_tag(article_xml, "ForeName", start_idx=author_idx)
                authors.append(f"{fore_name} {last_name}".strip())
                
                author_idx = article_xml.find("LastName", author_idx + 1)
                if author_idx == -1:
                    break
            
            # Extract DOI if available
            doi = ""
            doi_idx = article_xml.find("<ArticleId IdType=\"doi\">")
            if doi_idx != -1:
                doi_start = doi_idx + len("<ArticleId IdType=\"doi\">")
                doi_end = article_xml.find("</ArticleId>", doi_start)
                if doi_end != -1:
                    doi = article_xml[doi_start:doi_end].strip()
            
            # Extract keywords if available
            keywords = []
            keyword_idx = 0
            while True:
                keyword = self._extract_xml_tag(article_xml, "Keyword", start_idx=keyword_idx)
                if not keyword:
                    break
                    
                keywords.append(keyword)
                keyword_idx = article_xml.find("<Keyword", keyword_idx + 1)
                if keyword_idx == -1:
                    break
            
            article_data = {
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "journal": journal,
                "publication_date": f"{year} {month}".strip(),
                "authors": authors,
                "doi": doi,
                "keywords": keywords,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "doi_url": f"https://doi.org/{doi}" if doi else ""
            }
            
            articles.append(article_data)
            
            # Remove this article from the XML to process the next one
            xml_content = xml_content[article_end + 16:]
        
        return articles
    
    async def get_article_details(self, pmid: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific article by PMID
        
        Args:
            pmid: PubMed ID of the article
            
        Returns:
            Dictionary with article details
        """
        params = {
            "db": "pubmed",
            "id": pmid,
            "retmode": "xml",
            "rettype": "abstract"
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
        
        url = f"{self.BASE_URL}/efetch.fcgi"
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        
        xml_content = response.text
        
        # Extract article details
        title = self._extract_xml_tag(xml_content, "ArticleTitle")
        abstract = self._extract_xml_tag(xml_content, "AbstractText")
        journal = self._extract_xml_tag(xml_content, "Title")
        year = self._extract_xml_tag(xml_content, "Year")
        month = self._extract_xml_tag(xml_content, "Month")
        
        # Extract authors
        authors = []
        author_idx = 0
        while True:
            last_name = self._extract_xml_tag(xml_content, "LastName", start_idx=author_idx)
            if not last_name:
                break
                
            fore_name = self._extract_xml_tag(xml_content, "ForeName", start_idx=author_idx)
            authors.append(f"{fore_name} {last_name}".strip())
            
            author_idx = xml_content.find("LastName", author_idx + 1)
            if author_idx == -1:
                break
        
        # Extract DOI if available
        doi = ""
        doi_idx = xml_content.find("<ArticleId IdType=\"doi\">")
        if doi_idx != -1:
            doi_start = doi_idx + len("<ArticleId IdType=\"doi\">")
            doi_end = xml_content.find("</ArticleId>", doi_start)
            if doi_end != -1:
                doi = xml_content[doi_start:doi_end].strip()
        
        # Extract keywords if available
        keywords = []
        keyword_idx = 0
        while True:
            keyword = self._extract_xml_tag(xml_content, "Keyword", start_idx=keyword_idx)
            if not keyword:
                break
                
            keywords.append(keyword)
            keyword_idx = xml_content.find("<Keyword", keyword_idx + 1)
            if keyword_idx == -1:
                break
        
        return {
            "pmid": pmid,
            "title": title,
            "abstract": abstract,
            "journal": journal,
            "publication_date": f"{year} {month}".strip(),
            "authors": authors,
            "doi": doi,
            "keywords": keywords,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "doi_url": f"https://doi.org/{doi}" if doi else ""
        }
