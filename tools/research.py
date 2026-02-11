"""
Nexus Advanced Web Search
==========================
Multi-source web search with URL content extraction,
result caching, and structured output with citations.

Replaces the basic DuckDuckGoSearchRun with a full research toolkit.
"""

import requests
import hashlib
import time
import json
import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from langchain_core.tools import tool
from bs4 import BeautifulSoup
from langchain_community.tools import DuckDuckGoSearchRun

# ==================== CACHE ====================
_search_cache = {}  # {query_hash: {"results": ..., "timestamp": ...}}
CACHE_TTL = 300  # 5 minutes


def _cache_key(query: str) -> str:
    return hashlib.md5(query.lower().strip().encode()).hexdigest()


def _get_cached(query: str) -> Optional[dict]:
    key = _cache_key(query)
    if key in _search_cache:
        entry = _search_cache[key]
        if time.time() - entry["timestamp"] < CACHE_TTL:
            return entry["results"]
    return None


def _set_cache(query: str, results: dict):
    _search_cache[_cache_key(query)] = {
        "results": results,
        "timestamp": time.time()
    }


# ==================== URL EXTRACTION ====================

def _extract_page_content(url: str, max_chars: int = 3000) -> str:
    """Fetches and extracts clean text content from a URL."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Remove scripts, styles, nav, footer
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
            tag.decompose()
        
        # Get text
        text = soup.get_text(separator="\n", strip=True)
        
        # Clean up excessive whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)
        
        return clean_text[:max_chars] if len(clean_text) > max_chars else clean_text
    except Exception as e:
        return f"[Could not fetch: {e}]"


# ==================== SEARCH SOURCES ====================

def _ddg_search(query: str, num_results: int = 5) -> List[Dict]:
    """DuckDuckGo search via the Python library."""
    try:
        ddg = DuckDuckGoSearchRun()
        raw = ddg.invoke(query)
        
        # Parse the raw text results
        results = []
        if raw and isinstance(raw, str):
            results.append({
                "source": "DuckDuckGo",
                "title": f"Web search: {query}",
                "snippet": raw[:800],
                "url": ""
            })
        return results
    except Exception as e:
        return [{"source": "DuckDuckGo", "error": str(e)}]


def _wikipedia_search(query: str) -> Optional[Dict]:
    """Search Wikipedia for a topic summary."""
    try:
        resp = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}",
            timeout=8
        )
        if resp.status_code == 200:
            data = resp.json()
            return {
                "source": "Wikipedia",
                "title": data.get("title", query),
                "snippet": data.get("extract", ""),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
            }
    except Exception:
        pass
    return None


def _arxiv_search(query: str, max_results: int = 3) -> List[Dict]:
    """Search Arxiv for academic papers."""
    try:
        url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
        resp = requests.get(url, timeout=12)
        resp.raise_for_status()
        
        root = ET.fromstring(resp.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        
        papers = []
        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns)
            summary = entry.find("atom:summary", ns)
            link = entry.find("atom:id", ns)
            
            authors = []
            for author in entry.findall("atom:author", ns):
                name = author.find("atom:name", ns)
                if name is not None:
                    authors.append(name.text.strip())
            
            snippet = summary.text.strip()[:300] if summary is not None else ""
            papers.append({
                "source": "Arxiv",
                "title": title.text.strip() if title is not None else "Unknown",
                "snippet": snippet,
                "url": link.text.strip() if link is not None else "",
                "authors": authors[:3]
            })
        
        return papers
    except Exception:
        return []


# ==================== MAIN TOOLS ====================

@tool
def web_search(query: str) -> str:
    """
    Performs a smart web search using DuckDuckGo.
    Returns concise results from the web. Use this for quick lookups,
    current events, and general knowledge queries.
    
    Args:
        query: What to search for (e.g., 'latest AI news', 'Python datetime format')
    """
    # Check cache first
    cached = _get_cached(f"web:{query}")
    if cached:
        return cached
    
    results = _ddg_search(query)
    if results and not results[0].get("error"):
        output = f"🔍 **Web Search: '{query}'**\n\n{results[0].get('snippet', 'No results')}"
    else:
        output = f"Search failed: {results[0].get('error', 'Unknown error')}"
    
    _set_cache(f"web:{query}", output)
    return output


@tool
def read_webpage(url: str) -> str:
    """
    Reads and extracts the main text content from any webpage URL.
    Use this to deeply read an article, documentation page, or any web content.
    
    Args:
        url: The full URL to read (e.g., 'https://example.com/article')
    """
    content = _extract_page_content(url, max_chars=4000)
    return f"📄 **Content from {url}**:\n\n{content}"


@tool
def research_topic(topic: str) -> str:
    """
    Performs comprehensive multi-source research on a topic.
    Combines DuckDuckGo web search, Wikipedia overview, and Arxiv academic papers
    into a structured research report with citations.
    
    Use this for deep research, understanding complex topics, or when you need
    multiple perspectives on a subject.
    
    Args:
        topic: The subject to research (e.g., 'quantum computing advances 2025')
    """
    # Check cache
    cached = _get_cached(f"research:{topic}")
    if cached:
        return cached
    
    sections = []
    citations = []
    
    # 1. Wikipedia Overview
    wiki = _wikipedia_search(topic)
    if wiki and wiki.get("snippet"):
        sections.append(f"## 📚 Overview\n{wiki['snippet']}")
        if wiki.get("url"):
            citations.append(f"[Wikipedia: {wiki['title']}]({wiki['url']})")
    
    # 2. Web Search
    web = _ddg_search(topic, num_results=5)
    if web and not web[0].get("error"):
        sections.append(f"## 🌐 Web Results\n{web[0].get('snippet', '')}")
    
    # 3. Academic Papers
    papers = _arxiv_search(topic, max_results=3)
    if papers:
        paper_list = []
        for p in papers:
            authors = ", ".join(p.get("authors", []))
            paper_list.append(f"- **{p['title']}** ({authors})\n  {p['snippet'][:150]}...")
            if p.get("url"):
                citations.append(f"[{p['title'][:50]}]({p['url']})")
        
        sections.append(f"## 📄 Academic Papers\n" + "\n".join(paper_list))
    
    # Build report
    report = f"# Research: {topic}\n\n"
    report += "\n\n".join(sections) if sections else "No results found."
    
    if citations:
        report += "\n\n---\n## 📌 Sources\n" + "\n".join(f"- {c}" for c in citations)
    
    _set_cache(f"research:{topic}", report)
    return report


@tool 
def search_arxiv(query: str, max_results: int = 5) -> str:
    """
    Search Arxiv for scientific/academic papers on a topic.
    Returns paper titles, authors, summaries, and links.
    
    Args:
        query: Academic search query (e.g., 'transformer architecture attention')
        max_results: Number of papers to return (default 5)
    """
    papers = _arxiv_search(query, max_results=max_results)
    
    if not papers:
        return f"No Arxiv papers found for '{query}'"
    
    output = f"## 🎓 Arxiv Results: '{query}'\n\n"
    for i, p in enumerate(papers, 1):
        authors = ", ".join(p.get("authors", []))
        output += f"### {i}. {p['title']}\n"
        output += f"**Authors**: {authors}\n"
        output += f"**Summary**: {p['snippet']}\n"
        if p.get("url"):
            output += f"**Link**: {p['url']}\n"
        output += "\n"
    
    return output


SEARCH_TOOLS = [web_search, read_webpage, research_topic, search_arxiv]