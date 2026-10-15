from urllib.parse import urlparse
from .models import Evidence

QUERIES = [
    '"{company}" company industry products services',
    '"{company}" cloud data analytics AI automation',
    '"{company}" company location employees'
]

def research_company(company: str, max_results: int = 5) -> tuple[list[Evidence], list[str]]:
    """Run live public web searches. Search provider availability/rate limits can vary."""
    warnings = []
    try:
        from ddgs import DDGS
        ddgs = DDGS(timeout=10)
        collected, seen = [], set()
        for template in QUERIES:
            query = template.format(company=company.replace('"', ''))
            try:
                results = ddgs.text(query, max_results=max_results, region="wt-wt")
                for item in results or []:
                    url = str(item.get("href") or item.get("url") or "").strip()
                    title = str(item.get("title") or "Untitled search result").strip()
                    snippet = str(item.get("body") or item.get("snippet") or "").strip()
                    if not url.startswith("http") or url in seen:
                        continue
                    seen.add(url)
                    collected.append(Evidence(title=title, url=url, snippet=snippet,
                                              source_domain=urlparse(url).netloc.lower().removeprefix("www.")))
            except Exception as exc:
                warnings.append(f"One search query for {company} failed: {type(exc).__name__}.")
        if not collected:
            warnings.append(f"No live search results found for {company}; score will remain conservative.")
        return collected[:12], warnings
    except Exception as exc:
        return [], [f"Live search unavailable for {company} ({type(exc).__name__}). Check internet access or DDGS provider availability."]
