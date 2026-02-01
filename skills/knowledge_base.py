
from skills.loader import skill
import wikipedia
import arxiv

@skill
def wikipedia_search(query: str):
    """
    Searches Wikipedia and returns a summary.
    Use this for General Knowledge, Biography, History, and Definitions.
    """
    try:
        # Search for page match
        search_results = wikipedia.search(query)
        if not search_results:
            return "No Wikipedia results found."
        
        # Get summary of first result
        summary = wikipedia.summary(search_results[0], sentences=4)
        return f"📚 **Wikipedia ({search_results[0]}):**\n{summary}\n[Link]({wikipedia.page(search_results[0]).url})"
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Topic ambiguous. Did you mean: {e.options[:5]}?"
    except Exception as e:
        return f"Wikipedia Error: {e}"

@skill
def arxiv_search(query: str, max_results: int = 3):
    """
    Searches Arxiv for scientific papers (CS, AI, Physics).
    Returns Title, Author, and Abstract.
    """
    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        results = []
        for r in client.results(search):
            results.append(f"📄 **{r.title}**\n   *Authors*: {[a.name for a in r.authors]}\n   *Abstract*: {r.summary[:300]}...\n   [PDF]({r.pdf_url})")
            
        return "\n\n".join(results) if results else "No papers found."
    except Exception as e:
        return f"Arxiv Error: {e}"
