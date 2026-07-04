import os, requests
SERPER_URL = "https://google.serper.dev/search"
def find_company_sources(company: str) -> list[dict]:
    queries = [
    f"{company} official website",
    f"{company} company news",
    f"{company} linkedin",
    f"{company} crunchbase funding",
    ]
    results = []
    for q in queries:
        resp = requests.post(
        SERPER_URL,
        headers={"X-API-KEY": os.environ["SERPER_API_KEY"], "Content-Type": "application/json"},
        json={"q": q, "num": 5},
        timeout=15,
        )
        resp.raise_for_status()
        for item in resp.json().get("organic", []):
            results.append({"query": q, "title": item.get("title"), "url": item.get("link")})
    # dedupe by URL
    seen, deduped = set(), []
    for r in results:
        if r["url"] not in seen:
            seen.add(r["url"])
            deduped.append(r)
    return deduped