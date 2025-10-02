import argparse
import json
import subprocess
import urllib.parse

import requests
from bs4 import BeautifulSoup
from tqdm.auto import tqdm

from airline_agent.types.knowledge_base import KBArticle, Metadata

TOP_URL = "https://faq.flyfrontier.com/help"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, help="Path to save the fetched FAQs", required=True)
    args = parser.parse_args()

    all_faq_urls = get_all_faq_urls()
    entries: list[KBArticle] = []
    for url in tqdm(all_faq_urls, desc="fetching faqs"):
        entries.append(fetch_faq(url))  # noqa: PERF401

    with open(args.path, "w") as f:
        json.dump([entry.model_dump() for entry in entries], f, indent=2)


def fetch_faq(url: str) -> KBArticle:
    html = requests.get(url).text  # noqa: S113
    soup = BeautifulSoup(html, "html5lib")
    title_elem = soup.select_one(".hg-article-title")
    if title_elem is None:
        msg = f"title not found for URL: {url}"
        raise ValueError(msg)
    title = title_elem.text.strip()
    body = soup.select_one(".hg-article-body")
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


def rel_to_abs_url(rel_url: str) -> str:
    return urllib.parse.urljoin(TOP_URL, rel_url)


def get_all_faq_urls() -> list[str]:
    html = requests.get(TOP_URL).text  # noqa: S113
    soup = BeautifulSoup(html, "html5lib")
    all_rel_urls = [str(elem.attrs["href"]) for elem in soup.select(".article-link")]
    return [rel_to_abs_url(rel_url) for rel_url in all_rel_urls]


if __name__ == "__main__":
    main()
