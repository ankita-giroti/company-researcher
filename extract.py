import os, json
from openai import OpenAI
from pydantic import BaseModel, Field

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

class CompanyProfile(BaseModel):
    name: str
    industry: str | None = None
    hq_location: str | None = None
    founded_year: int | None = None
    employee_count_estimate: str | None = None
    products_services: list[str] = Field(default_factory=list)
    key_people: list[str] = Field(default_factory=list)
    funding_summary: str | None = None
    recent_news: list[str] = Field(default_factory=list)
    competitors: list[str] = Field(default_factory=list)
    summary: str | None = None

SCHEMA_HINT = CompanyProfile.model_json_schema()

def extract_profile(company: str, crawled_pages: dict[str, str]) -> CompanyProfile:
    combined = "\n\n".join(f"SOURCE: {url}\n{text}" for url, text in crawled_pages.items())
    combined = combined[:24000] # trim to fit context budget
    
    prompt = f"""
    You are a research analyst. Using ONLY the source text below, extract information about "{company}".
    Return STRICT JSON matching this schema (no prose, no markdown fences):
    {json.dumps(SCHEMA_HINT)}
    If a field is unknown, use null or an empty list. Do not invent facts.
    SOURCES:
    {combined}
    """
    
    resp = client.chat.completions.create(
        model=os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=2000,
    )
    raw = resp.choices[0].message.content.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return CompanyProfile.model_validate(json.loads(raw))