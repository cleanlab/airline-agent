import threading
import time
import urllib

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

_thread_data = threading.local()
_all_drivers = set()


def get_driver():
    if not hasattr(_thread_data, "driver") or _thread_data.driver is None:
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        _thread_data.driver = driver
        _all_drivers.add(driver)
    return _thread_data.driver


def close_drivers():
    for driver in list(_all_drivers):
        try:
            driver.quit()
        except Exception:
            pass
        finally:
            _all_drivers.discard(driver)


def fetch_html_with_js(url: str) -> str:
    """Fetch HTML from a URL using Selenium to render JavaScript."""
    driver = get_driver()  # Reuse existing driver for this thread
    driver.get(url)
    time.sleep(1)
    return driver.page_source


def rel_to_abs_url(rel_url: str, base_url: str) -> str:
    """Convert a relative URL to an absolute URL."""
    return urllib.parse.urljoin(base_url, rel_url)
