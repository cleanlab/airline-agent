import urllib.parse


def rel_to_abs_url(rel_url: str, base_url: str) -> str:
    """Convert a relative URL to an absolute URL."""
    return urllib.parse.urljoin(base_url, rel_url)
