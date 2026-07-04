from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import asyncio
import time


def build_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("user-agent=Mozilla/5.0 (Research-Bot/1.0)")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

def crawl_page(driver, url: str, wait: float = 2.5) -> str:
    try:
        driver.get(url)
        time.sleep(wait) # let JS render; swap for WebDriverWait on real selectors
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = " ".join(soup.get_text(separator=" ").split())
        return text[:8000] # cap per-page text to control LLM token cost
    except Exception as e:
        return f"[ERROR crawling {url}: {e}]"
    
async def _crawl_all(urls: list[str], concurrency: int = 4) -> dict[str, str]:
    pages = {}
    semaphore = asyncio.Semaphore(concurrency)

    # Note: Your crawl_page function will need to accept the 'driver' instead of 'context'
    async def bound_crawl(url):
        async with semaphore:
            # Create a driver instance per concurrent task to avoid thread-safety issues
            # asyncio.to_thread runs the blocking synchronous Selenium code in a separate thread
            driver = await asyncio.to_thread(build_driver)
            try:
                pages[url] = await asyncio.to_thread(crawl_page, driver, url)
            finally:
                # Always ensure the browser closes even if the crawl fails
                await asyncio.to_thread(driver.quit)

    # Run all tasks concurrently up to the semaphore limit
    await asyncio.gather(*(bound_crawl(u) for u in urls))
    return pages

def crawl_sources(urls: list[str]) -> dict[str, str]:
    driver = build_driver()
    pages = {}
    try:
        for url in urls:
            pages[url] = crawl_page(driver, url)
    finally:
        driver.quit()
    return pages