"""
Nexus Research Tools
====================
Tools for web search, academic papers, and knowledge retrieval.
"""

import requests
import json
from typing import List, Dict


def duckduckgo_search(query: str) -> Dict:
    """
    A wrapper around DuckDuckGo Search API.
    """
    try:
        response = requests.get(
            'https://api.duckduckgo.com/',
            params={'q': query, 'format': 'json'},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {'error': str(e), 'results': []}


def arxiv_search(query: str, max_results: int = 5) -> List[Dict]:
    """
    Searches Arxiv for scientific papers using the Arxiv API.
    Returns parsed paper metadata (title, authors, summary, link).
    """
    try:
        import xml.etree.ElementTree as ET
        
        url = f'http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}'
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        # Parse XML response
        root = ET.fromstring(response.text)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        entries = []
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns)
            summary = entry.find('atom:summary', ns)
            link = entry.find('atom:id', ns)
            
            authors = []
            for author in entry.findall('atom:author', ns):
                name = author.find('atom:name', ns)
                if name is not None:
                    authors.append(name.text.strip())
            
            entries.append({
                'title': title.text.strip() if title is not None else 'Unknown',
                'authors': authors,
                'summary': (summary.text.strip()[:300] + '...') if summary is not None and len(summary.text.strip()) > 300 else (summary.text.strip() if summary is not None else ''),
                'link': link.text.strip() if link is not None else ''
            })
        
        return entries
    except Exception as e:
        return [{'error': str(e)}]


def wikipedia_search(query: str) -> Dict:
    """
    Searches Wikipedia and returns a summary.
    """
    try:
        response = requests.get(
            'https://en.wikipedia.org/api/rest_v1/page/summary/' + query,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return {
            'title': data.get('title', query),
            'summary': data.get('extract', 'No summary available'),
            'url': data.get('content_urls', {}).get('desktop', {}).get('page', '')
        }
    except Exception as e:
        return {'error': str(e)}


def quick_search(query: str) -> Dict:
    """
    Performs a quick web search via DuckDuckGo.
    """
    return duckduckgo_search(query)


def deep_research(topic: str) -> Dict:
    """
    Performs a multi-step research session on a topic.
    Combines DuckDuckGo, Wikipedia, and Arxiv for comprehensive results.
    """
    try:
        # Step 1: Web search
        web_results = duckduckgo_search(topic)
        
        # Step 2: Wikipedia overview
        wiki_results = wikipedia_search(topic.replace(' ', '_'))
        
        # Step 3: Academic papers
        arxiv_results = arxiv_search(topic, max_results=3)
        
        # Build summary
        summary_parts = []
        
        if wiki_results.get('summary'):
            summary_parts.append(f"**Wikipedia**: {wiki_results['summary']}")
        
        if arxiv_results and not arxiv_results[0].get('error'):
            paper_titles = [p.get('title', '') for p in arxiv_results[:3]]
            summary_parts.append(f"**Related Papers**: {'; '.join(paper_titles)}")
        
        return {
            'topic': topic,
            'web_search': web_results,
            'wikipedia': wiki_results,
            'academic_papers': arxiv_results,
            'summary': '\n'.join(summary_parts) if summary_parts else f'Research completed for {topic}'
        }
    except Exception as e:
        return {'error': str(e)}