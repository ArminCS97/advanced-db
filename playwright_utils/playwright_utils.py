from typing import Tuple

from bs4 import BeautifulSoup
from playwright.sync_api import Response, sync_playwright

from playwright_utils.scroll_to_bottom_js_function import scroll_to_bottom_js_function

TIMEOUT = 30000


def playwright_scraper(page: str, thread) -> Tuple[BeautifulSoup, Response, str]:
    try:
        with sync_playwright() as playwright:
            browser = playwright.firefox.launch(headless=True)
            context = browser.new_context()
            # 1: Scrape the page based on the JS functions
            print(f"Page {page} is about to be scraped by Thread {thread}")
            playwright_page = context.new_page()
            response = playwright_page.goto(page, timeout=TIMEOUT)
            playwright_page.wait_for_timeout(2000)
            playwright_page.wait_for_selector("body", timeout=TIMEOUT)
            playwright_page.evaluate(scroll_to_bottom_js_function)
            html = playwright_page.content()

            # Now we close the page to release the thread on which this page was being scraped
            playwright_page.close()
            # 2: Extract the needed data
            parsed_html = BeautifulSoup(html, 'html.parser')
            context.close()
            browser.close()
            return parsed_html, response, page
    except Exception as e:
        print(repr(e), page)
        context.close()
        browser.close()
