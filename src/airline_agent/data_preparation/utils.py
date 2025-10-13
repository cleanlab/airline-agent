import threading
import time
import urllib

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

thread_local = threading.local()


def get_driver() -> webdriver.Chrome:
    """Get or create a WebDriver instance for the current thread."""
    if not hasattr(thread_local, "driver"):
        options = Options()
        options.add_argument("--headless")
        thread_local.driver = webdriver.Chrome(options=options)
    return thread_local.driver  # type: ignore[no-any-return]


def fetch_html_with_js(url: str) -> str:
    """Fetch HTML from a URL using Selenium to render JavaScript."""
    driver = get_driver()  # Reuse existing driver for this thread
    driver.get(url)
    time.sleep(1)
    return driver.page_source


def cleanup_driver() -> None:
    """Clean up the WebDriver for the current thread."""
    if hasattr(thread_local, "driver"):
        thread_local.driver.quit()
        delattr(thread_local, "driver")


def rel_to_abs_url(rel_url: str, base_url: str) -> str:
    """Convert a relative URL to an absolute URL."""
    return urllib.parse.urljoin(base_url, rel_url)
