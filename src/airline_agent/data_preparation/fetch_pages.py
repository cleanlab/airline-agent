import argparse
import json
import subprocess
import time
import urllib.parse

import requests
from bs4 import BeautifulSoup
from requests.exceptions import MissingSchema
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tqdm.auto import tqdm

from airline_agent.data_preparation.utils import rel_to_abs_url
from airline_agent.types.knowledge_base import KBArticle, Metadata

FAQ_URL = "https://faq.flyfrontier.com/help"
HOME_URL = "https://www.flyfrontier.com"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, help="Path to save the fetched FAQs", required=True)
    args = parser.parse_args()

    faq_urls = get_all_faq_urls()
    home_urls = get_home_urls()
    all_urls = faq_urls + home_urls

    entries: list[KBArticle] = []
    for url in tqdm(all_urls, desc="fetching pages"):
        try:
            entries.append(fetch_page(url))
        except MissingSchema:
            continue

    with open(args.path, "w") as f:
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
    """Get all relevant URLs from the main www.flyfrontier.com site using Selenium."""

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(HOME_URL)
    time.sleep(1)
    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html5lib")
    all_links = soup.find_all("a", href=True)

    home_urls = set()
    for link in all_links:
        href = link.get("href", "")
        if not href or not isinstance(href, str):
            continue

        _, netloc, _, _, _ = urllib.parse.urlsplit(href)

        if netloc == "www.flyfrontier.com":
            url = href.rstrip("/")
            if url != HOME_URL:
                home_urls.add(url)

    return list(home_urls)


if __name__ == "__main__":
    main()
