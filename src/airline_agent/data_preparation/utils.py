import threading
import time
import urllib
from typing import cast

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver

_thread_local = threading.local()
_all_drivers: set[WebDriver] = set()


def get_driver() -> WebDriver:
    if not hasattr(_thread_local, "driver") or _thread_local.driver is None:
        options = Options()
        options.add_argument("--headless")
        driver: WebDriver = webdriver.Chrome(options=options)
        _thread_local.driver = driver
        _all_drivers.add(driver)
    return cast(WebDriver, _thread_local.driver)


def close_driver() -> None:
    driver: WebDriver | None = getattr(_thread_local, "driver", None)
    if driver:
        driver.quit()
        del _thread_local.driver


def fetch_html_with_js(driver: WebDriver, url: str) -> str:
    """Fetch HTML from a URL using Selenium to render JavaScript."""
    driver.get(url)
    time.sleep(1)
    return driver.page_source


def rel_to_abs_url(rel_url: str, base_url: str) -> str:
    """Convert a relative URL to an absolute URL."""
    return urllib.parse.urljoin(base_url, rel_url)
