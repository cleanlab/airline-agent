import argparse
import json
import subprocess
import urllib.parse
from typing import Any

import pydantic
import requests
from bs4 import BeautifulSoup
from tqdm.auto import tqdm

TOP_URL = "https://faq.flyfrontier.com/help"


class KBEntry(pydantic.BaseModel):
    path: str
    metadata: dict[str, Any] = {}
    content: str


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, help="Path to save the fetched FAQs", required=True)
    args = parser.parse_args()

    all_faq_urls = get_all_faq_urls()
    entries: list[KBEntry] = []
    for url in tqdm(all_faq_urls, desc="fetching faqs"):
        entries.append(fetch_faq(url))

    with open(args.path, "w") as f:
        json.dump([entry.model_dump() for entry in entries], f, indent=2)


def fetch_faq(url: str) -> KBEntry:
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html5lib")
    title_elem = soup.select_one(".hg-article-title")
    assert title_elem is not None
    title = title_elem.text.strip()
    body = soup.select_one(".hg-article-body")
    proc = subprocess.run(['pandoc', '-f', 'html', '-t', 'gfm-raw_html', '--wrap=none'],
        input=str(body),
        capture_output=True,
        text=True,
        check=True
    )
    body_content = proc.stdout
    content = f"# {title}\n\n{body_content}".strip()
    path = urllib.parse.urlparse(url).path
    return KBEntry(path=path, metadata={"title": title}, content=content)


def rel_to_abs_url(rel_url: str) -> str:
    return urllib.parse.urljoin(TOP_URL, rel_url)


def get_all_faq_urls() -> list[str]:
    html = requests.get(TOP_URL).text
    soup = BeautifulSoup(html, "html5lib")
    all_rel_urls = [str(elem.attrs['href']) for elem in soup.select(".article-link")]
    return [rel_to_abs_url(rel_url) for rel_url in all_rel_urls]

if __name__ == "__main__":
    main()
