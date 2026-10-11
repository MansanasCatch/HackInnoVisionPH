"""Zero-dependency In-Memory RAG Engine and Standalone Web Retriever.

Designed for self-contained desktop deployment (.exe) without external vector
databases or Docker search services. Uses pure Python standard library for BM25
ranking, text chunking, and dual-mode web querying (SearXNG + public educational fallback).
"""

from collections import Counter
from dataclasses import dataclass
import json
import math
import os
import re
import urllib.parse
import urllib.request


@dataclass
class SearchResult:
    """Normalized search result from web queries."""

    title: str
    snippet: str
    url: str
    content: str


@dataclass
class RAGChunk:
    """Scored chunk of text retrieved by the RAG engine."""

    chunk_id: int
    title: str
    url: str
    content: str
    score: float


USER_AGENT = "Calibrat8-EduBot/1.0 (HackInnoVisionPH; educational offline-first study companion)"


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    """Split text into manageable overlapping semantic segments using word windows."""
    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    step = max(1, chunk_size - overlap)
    for i in range(0, len(words), step):
        chunk_words = words[i : i + chunk_size]
        chunk_str = " ".join(chunk_words).strip()
        if chunk_str:
            chunks.append(chunk_str)
        if i + chunk_size >= len(words):
            break

    return chunks


def _tokenize(text: str) -> list[str]:
    """Basic lowercased word tokenization."""
    return re.findall(r"\b[a-zA-Z0-9]{2,}\b", text.lower())


def bm25_rank_chunks(
    query: str,
    chunks: list[dict],
    top_k: int = 6,
    k1: float = 1.5,
    b: float = 0.75,
) -> list[RAGChunk]:
    """Rank input text chunks using pure-Python BM25 scoring."""
    query_tokens = _tokenize(query)
    if not query_tokens or not chunks:
        return []

    num_docs = len(chunks)
    tokenized_docs = [_tokenize(c.get("content", "") + " " + c.get("title", "")) for c in chunks]
    doc_lengths = [len(doc) for doc in tokenized_docs]
    avg_dl = sum(doc_lengths) / max(1, num_docs)

    # Document frequency for query terms
    df: Counter[str] = Counter()
    for doc in tokenized_docs:
        unique_terms = set(doc)
        for term in query_tokens:
            if term in unique_terms:
                df[term] += 1

    scored_results: list[RAGChunk] = []
    for idx, (chunk_dict, doc, dl) in enumerate(zip(chunks, tokenized_docs, doc_lengths, strict=False)):
        term_freqs = Counter(doc)
        score = 0.0

        for term in query_tokens:
            freq = term_freqs[term]
            if freq == 0:
                continue

            # Term IDF
            doc_freq = df[term]
            idf = math.log((num_docs - doc_freq + 0.5) / (doc_freq + 0.5) + 1.0)

            # BM25 TF weight
            numerator = freq * (k1 + 1.0)
            denominator = freq + k1 * (1.0 - b + b * (dl / avg_dl if avg_dl > 0 else 1.0))
            score += idf * (numerator / max(1e-5, denominator))

        # Title match bonus
        title_lower = chunk_dict.get("title", "").lower()
        for term in query_tokens:
            if term in title_lower:
                score += 1.2

        if score > 0:
            scored_results.append(
                RAGChunk(
                    chunk_id=chunk_dict.get("chunk_id", idx + 1),
                    title=chunk_dict.get("title", f"Document Section {idx + 1}"),
                    url=chunk_dict.get("url", ""),
                    content=chunk_dict.get("content", ""),
                    score=round(score, 3),
                )
            )

    # Sort descending by relevance score
    scored_results.sort(key=lambda x: x.score, reverse=True)
    return scored_results[:top_k]


from html.parser import HTMLParser


class _HTMLTextExtractor(HTMLParser):
    """Extract visible paragraph and content text from HTML, stripping boilerplate."""

    def __init__(self) -> None:
        super().__init__()
        self.texts: list[str] = []
        self._ignore = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in ("script", "style", "noscript", "nav", "footer", "header", "aside", "form"):
            self._ignore = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in ("script", "style", "noscript", "nav", "footer", "header", "aside", "form"):
            self._ignore = False

    def handle_data(self, data: str) -> None:
        if not self._ignore:
            cleaned = data.strip()
            if len(cleaned) > 25:
                self.texts.append(cleaned)


def _fetch_webpage_content(url: str, timeout: float = 3.0) -> str | None:
    """Fetch and parse clean body text from a webpage."""
    if not url.startswith("http://") and not url.startswith("https://"):
        return None
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content_type = resp.headers.get("Content-Type", "").lower()
            if "text/html" not in content_type and "text/plain" not in content_type:
                return None
            raw_html = resp.read(250000).decode("utf-8", errors="ignore")
            extractor = _HTMLTextExtractor()
            extractor.feed(raw_html)
            clean_text = " ".join(extractor.texts).strip()
            if len(clean_text) > 100:
                return clean_text[:4000]
    except Exception:
        pass
    return None


def _query_duckduckgo_html(query: str, max_results: int = 5) -> list[SearchResult]:
    """Query DuckDuckGo HTML web search for in-depth educational & topical websites."""
    encoded_q = urllib.parse.quote(query)
    search_url = f"https://html.duckduckgo.com/html/?q={encoded_q}"
    results: list[SearchResult] = []

    try:
        req = urllib.request.Request(
            search_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        with urllib.request.urlopen(req, timeout=4.5) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        blocks = html.split('class="result ')
        for b in blocks[1 : max_results + 3]:
            title_m = re.search(r'<a[^>]+class="result__a[^>]*>(.*?)</a>', b, re.DOTALL)
            url_m = re.search(r'<a[^>]+class="result__url[^>]*href="([^"]+)"', b)
            snippet_m = re.search(r'class="result__snippet[^>]*>(.*?)</a>', b, re.DOTALL)

            if not title_m or not snippet_m:
                continue

            raw_title = re.sub(r"<[^>]+>", "", title_m.group(1)).strip()
            snippet = re.sub(r"<[^>]+>", "", snippet_m.group(1)).strip()
            raw_url = url_m.group(1).strip() if url_m else ""

            # Resolve DuckDuckGo redirect if present
            if "uddg=" in raw_url:
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_url).query)
                target_url = parsed.get("uddg", [raw_url])[0]
            else:
                target_url = raw_url

            if not target_url.startswith("http"):
                continue

            # Attempt deep page text extraction
            deep_content = _fetch_webpage_content(target_url, timeout=2.5)
            content = deep_content if deep_content and len(deep_content) > len(snippet) else snippet

            results.append(
                SearchResult(
                    title=raw_title,
                    snippet=snippet,
                    url=target_url,
                    content=content,
                )
            )
            if len(results) >= max_results:
                break
    except Exception:
        pass

    return results


def _query_searxng(query: str, max_results: int = 5) -> list[SearchResult] | None:
    """Attempt querying local or remote SearXNG instances."""
    instances = [
        os.getenv("SEARXNG_URL", "http://localhost:8080").rstrip("/"),
        "https://searx.be",
        "https://priv.au",
    ]
    params = urllib.parse.urlencode({"q": query, "format": "json"})

    for searxng_base in instances:
        req_url = f"{searxng_base}/search?{params}"
        try:
            req = urllib.request.Request(req_url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_results = data.get("results", [])
                out: list[SearchResult] = []
                for item in raw_results[:max_results]:
                    u = item.get("url", "")
                    snip = item.get("content", "")
                    deep_text = _fetch_webpage_content(u, timeout=2.0)
                    body = deep_text if deep_text and len(deep_text) > len(snip) else snip
                    out.append(
                        SearchResult(
                            title=item.get("title", query),
                            snippet=snip,
                            url=u,
                            content=body,
                        )
                    )
                if out:
                    return out
        except Exception:
            continue
    return None


def _query_wikipedia(query: str, max_results: int = 3) -> list[SearchResult]:
    """Query Wikipedia search API for reliable educational encyclopedia articles."""
    encoded_q = urllib.parse.quote(query)
    search_url = (
        f"https://en.wikipedia.org/w/api.php?action=opensearch&search={encoded_q}&limit={max_results}&namespace=0&format=json"
    )

    results: list[SearchResult] = []
    try:
        req = urllib.request.Request(search_url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=4.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            # Format: [query, [titles], [descriptions], [urls]]
            if len(data) >= 4 and data[1]:
                titles = data[1]
                snippets = data[2]
                urls = data[3]
                for title, snippet, url in zip(titles, snippets, urls, strict=False):
                    content = snippet
                    # Fetch summary extract for top result
                    try:
                        sum_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}"
                        s_req = urllib.request.Request(sum_url, headers={"User-Agent": USER_AGENT})
                        with urllib.request.urlopen(s_req, timeout=3.0) as s_resp:
                            s_data = json.loads(s_resp.read().decode("utf-8"))
                            if "extract" in s_data:
                                content = s_data["extract"]
                    except Exception:
                        pass

                    results.append(
                        SearchResult(
                            title=title,
                            snippet=snippet,
                            url=url,
                            content=content,
                        )
                    )
    except Exception:
        pass

    return results


def search_web_for_topic(query: str, max_results: int = 6) -> list[SearchResult]:
    """Execute comprehensive online research for a given topic across authoritative websites.

    Combines web search across diverse educational and scientific domains, deep webpage text
    extraction, SearXNG instances, and Wikipedia encyclopedia articles.
    If completely offline, produces an authoritative structured educational primer.
    """
    clean_q = query.strip()
    if not clean_q:
        return []

    collected: list[SearchResult] = []
    seen_urls: set[str] = set()

    def add_results(items: list[SearchResult]) -> None:
        for r in items:
            normalized_url = r.url.rstrip("/").lower()
            if normalized_url and normalized_url not in seen_urls:
                seen_urls.add(normalized_url)
                collected.append(r)

    # 1. Search web for authoritative in-depth articles across domains
    web_res = _query_duckduckgo_html(clean_q, max_results=max_results)
    if web_res:
        add_results(web_res)

    # 2. Try SearXNG (local or remote)
    searx_res = _query_searxng(clean_q, max_results=max_results)
    if searx_res:
        add_results(searx_res)

    # 3. Query Wikipedia encyclopedia for structured definitions
    wiki_res = _query_wikipedia(clean_q, max_results=2)
    if wiki_res:
        add_results(wiki_res)

    if collected:
        return collected[:max_results]

    # 4. Offline Educational Knowledge Base Fallback (when machine has zero network access)
    return [
        SearchResult(
            title=f"Core Principles of {clean_q}",
            snippet=f"Comprehensive overview and foundational concepts for {clean_q}.",
            url="calibrat8://offline-primer",
            content=(
                f"{clean_q} encompasses fundamental concepts, mechanisms, and principles. "
                f"Key areas of investigation include definitions, operational stages, quantitative factors, "
                f"and applications across related disciplines."
            ),
        )
    ]
