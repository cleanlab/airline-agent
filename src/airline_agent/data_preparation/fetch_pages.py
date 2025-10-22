import json
import pathlib
import subprocess
import urllib.parse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from tqdm.auto import tqdm

from airline_agent.data_preparation.utils import rel_to_abs_url
from airline_agent.types.knowledge_base import KBArticle, Metadata

FAQ_URL = "https://faq.flyfrontier.com/help"
HOME_URL = "https://www.flyfrontier.com"


def main() -> None:
    load_dotenv()

    project_root = pathlib.Path(__file__).resolve().parents[3]
    output_path = project_root / "data" / "kb.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    faq_urls = get_all_faq_urls()
    home_urls = get_home_urls()
    all_urls = faq_urls + home_urls

    entries: list[KBArticle] = [fetch_page(url) for url in tqdm(all_urls, desc="fetching pages")]

    with output_path.open("w") as f:
        json.dump([entry.model_dump() for entry in entries], f, indent=2)


def fetch_page(url: str) -> KBArticle:
    """Fetch a page and convert it to a KBArticle."""
    # Determine selectors based on URL
    if "faq.flyfrontier.com" in url:
        title_selector = ".hg-article-title"
        body_selector = ".hg-article-body"
    else:
        title_selector = "title"
        body_selector = ".main-torso"

    html = requests.get(url).text  # noqa: S113
    soup = BeautifulSoup(html, "html5lib")

    title_elem = soup.select_one(title_selector)
    if title_elem is None:
        msg = f"title not found for URL: {url}"
        raise ValueError(msg)
    title = title_elem.text.strip()

    body = soup.select_one(body_selector)
    proc = subprocess.run(
        ["pandoc", "-f", "html", "-t", "gfm-raw_html", "--wrap=none"],  # noqa: S607
        input=str(body),
        capture_output=True,
        text=True,
        check=True,
    )
    body_content = proc.stdout
    content = f"# {title}\n\n{body_content}".strip()
    path = urllib.parse.urlparse(url).path
    return KBArticle(path=path, metadata=Metadata(title=title), content=content)


def get_all_faq_urls() -> list[str]:
    """Get all FAQ article URLs from faq.flyfrontier.com."""
    html = requests.get(FAQ_URL).text  # noqa: S113
    soup = BeautifulSoup(html, "html5lib")
    all_rel_urls = [str(elem.attrs["href"]) for elem in soup.select(".article-link")]
    return [rel_to_abs_url(rel_url, FAQ_URL) for rel_url in all_rel_urls]


def get_home_urls() -> list[str]:
    """Retrieve all relevant URLs from the main FlyFrontier website.

    Uses Selenium to load the www.flyfrontier.com homepage and allow JavaScript
    to fully render dynamic content before collecting all available URLs.
    """

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(HOME_URL)
        WebDriverWait(driver, 10).until(  # wait up to 10 seconds
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, "div.nav-desktop-container.horizontal.center.around.nav-desktop")
            )
        )
        html = driver.page_source
    finally:
        driver.quit()

    soup = BeautifulSoup(html, "html5lib")
    all_links = soup.find_all("a", href=True)

    home_urls = set()
    for link in all_links:
        href = link.get("href", "")
        if not href or not isinstance(href, str):
            continue

        if href.startswith("//"):
            href = "https:" + href

        _, netloc, _, _, _ = urllib.parse.urlsplit(href)

        if netloc == "www.flyfrontier.com":
            url = href.rstrip("/")
            if url != HOME_URL:
                home_urls.add(url)

    return list(home_urls)


if __name__ == "__main__":
    main()
