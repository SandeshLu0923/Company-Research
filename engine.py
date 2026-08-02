import re
import json
import httpx
import asyncio
from urllib.parse import urlparse
from bs4 import BeautifulSoup

SERPER_URL = "https://google.serper.dev/search"


def run_serper_search(query: str, api_key: str, num: int = 5) -> dict:
    """Queries Serper.dev to find live data or URLs on any target company."""
    if not api_key:
        return {}
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    payload = {"q": query, "num": num}
    try:
        response = httpx.post(SERPER_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception:
        return {}


def cleanly_parse_domain(url: str) -> str:
    """Extracts a clean root domain address string out of any URL input."""
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    host = parsed.netloc or parsed.path
    return host.replace("www.", "")


def ensure_http_url(candidate: str) -> str:
    """Normalizes user input into a usable https link when possible."""
    if not candidate:
        return ""
    candidate = candidate.strip()
    if candidate.startswith(("http://", "https://")):
        return candidate
    return "https://" + candidate


async def fetch_and_clean_page(client: httpx.AsyncClient, url: str) -> tuple[str, str]:
    """Universal Web Extractor: Pulls raw text from any targeted web asset page and returns page title/text."""
    try:
        response = await client.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            timeout=8,
            follow_redirects=True,
        )
        if response.status_code != 200:
            return "", ""
        soup = BeautifulSoup(response.text, "html.parser")
        for junk in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            junk.decompose()
        text = re.sub(r"\s+", " ", soup.get_text(separator=" ").strip())
        title = soup.title.get_text(strip=True) if soup.title else ""
        return title, text[:6000]
    except Exception:
        return "", ""


async def execute_autonomous_crawler(target_base_url: str) -> str:
    """Concurrently scrapes essential business pages and returns a normalized corpus for AI analysis."""
    domain = cleanly_parse_domain(target_base_url)
    if not domain:
        return ""
    base = ensure_http_url(target_base_url)
    routes = ["", "about", "products", "services", "solutions", "contact", "pricing"]
    urls = []
    seen = set()

    for route in routes:
        candidate = f"{base.rstrip('/')}/{route}" if route else base.rstrip('/')
        if candidate not in seen and "login" not in candidate.lower() and "signin" not in candidate.lower():
            seen.add(candidate)
            urls.append(candidate)

    async with httpx.AsyncClient() as client:
        tasks = [fetch_and_clean_page(client, url) for url in urls]
        pages = await asyncio.gather(*tasks)
    corpus = []
    for title, text in pages:
        if text:
            corpus.append(f"{title}: {text}")
    return " ".join(corpus)[:12000]


def extract_company_website(company_input: str, api_key: str) -> tuple[str, str]:
    """Resolve an official company website using Serper if the user supplies a company name."""
    cleaned = company_input.strip()
    if not cleaned:
        return "", ""
    if cleaned.startswith(("http://", "https://")):
        return cleaned, cleanly_parse_domain(cleaned)

    result = run_serper_search(f"{cleaned} official website", api_key, num=3)
    organic = result.get("organic", [])
    if not organic:
        return ensure_http_url(cleaned), cleaned
    selected = organic[0]
    link = selected.get("link") or selected.get("source") or selected.get("url")
    title = selected.get("title") or cleaned
    return ensure_http_url(link), title


def summarize_search_results(name: str, url: str, api_key: str) -> dict:
    """Collect supporting public context from Serper for research enrichment."""
    search_queries = [
        f"{name} company address phone products services",
        f"{name} pain points challenges",
        f"{name} competitors industry",
    ]
    collected = {"company": [], "pain_points": [], "competitors": []}
    for query in search_queries:
        response = run_serper_search(query, api_key, num=4)
        for item in response.get("organic", [])[:4]:
            collected["company"].append(item)
    return collected

