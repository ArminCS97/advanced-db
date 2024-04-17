from urllib.parse import urlparse

import validators
from bs4 import BeautifulSoup

MAX_CHARS_LIMIT_FOR_PAGE_URL = 512


# Each url must never end in /.
def normalize_url(url: str):
    if "www" not in url:
        url = urlparse(url).scheme + "://www." + urlparse(url).netloc + urlparse(url).path
    if url is None:
        return None
    if url[-1] == "/":
        return url[0:-1]
    return url


def can_add_page_url(page_url):
    if page_url is None:
        return False
    invalid_chars = ['#', '$', '[', ']', '?']
    for char in invalid_chars:
        if char in page_url:
            return False
    if not validators.url(page_url):
        return False
    if "javascript:" in page_url:
        return False
    if "mailto:" in page_url:
        return False
    if "tel:" in page_url:
        return False
    if page_url.count(".") > 2:
        return False
    if len(page_url) > MAX_CHARS_LIMIT_FOR_PAGE_URL:
        return False
    return True


# All the links that this function returns are absolute urls and normalized (not ended in /)
def extract_all_links(parsed_html: BeautifulSoup) -> set:
    all_links_from_page = parsed_html.find_all("a")
    links = set()
    for link in all_links_from_page:
        page = link.get("href", None)
        # If page_url="https://www.example.com/page1", we are good but if the page_url=/page1
        if can_add_page_url(page):
            links.add(page)
    return links
