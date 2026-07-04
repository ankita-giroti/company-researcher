from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import asyncio
import time
import tempfile
import uuid

CHROMEDRIVER_PATH = "/usr/bin/chromedriver"
CHROME_BINARY_PATH = "/usr/bin/google-chrome"

def build_driver():
    opts = Options()
    opts.binary_location = CHROME_BINARY_PATH
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("user-agent=Mozilla/5.0 (Research-Bot/1.0)")
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    opts.add_argument("--ignore-certificate-errors")
    opts.add_argument("--ignore-ssl-errors=yes")
    opts.add_argument("--log-level=3")

    user_data_dir = tempfile.mkdtemp(prefix=f"chrome-profile-{uuid.uuid4().hex}-")
    opts.add_argument(f"--user-data-dir={user_data_dir}")

    return webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=opts)


def crawl_page(driver, url: str, wait: float = 2.5) -> str:
    try:
        driver.get(url)
        time.sleep(wait)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = " ".join(soup.get_text(separator=" ").split())
        return text[:8000]
    except Exception as e:
        return f"[ERROR crawling {url}: {e}]"


async def _crawl_all(urls: list[str], concurrency: int = 4) -> dict[str, str]:
    pages = {}
    semaphore = asyncio.Semaphore(concurrency)

    async def bound_crawl(url):
        async with semaphore:
            driver = await asyncio.to_thread(build_driver)
            try:
                pages[url] = await asyncio.to_thread(crawl_page, driver, url)
            finally:
                await asyncio.to_thread(driver.quit)

    await asyncio.gather(*(bound_crawl(u) for u in urls))
    return pages
