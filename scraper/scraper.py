import concurrent.futures
import threading
from typing import List

from bs4 import BeautifulSoup
from prettytable import PrettyTable

from information_extractor.information_extractor import count_number_of_distinct_words
from playwright_utils.link_extractor import extract_all_links
from playwright_utils.playwright_utils import playwright_scraper

lock = threading.RLock()  # we use Rlock so that self._queue and self._visited_pages can be acquired more than once by the same thread


class Scraper:
    def __init__(self, domains: List[str], limit: int, threads_num_used: int):
        self._limit = limit
        self._threads_num_used = threads_num_used
        self._counter = 0
        self._visited_pages = set()
        self._queue = [d for d in domains]
        self._cursor = 0  # helps us access the pages in self._queue
        self._results = {}

    def _store_scraped_page_result(self, parsed_html: BeautifulSoup, page: str):
        text = parsed_html.get_text(separator=' ')
        words = text.split()
        global lock
        with lock:
            self._results[page] = count_number_of_distinct_words(words)
            with open("results.txt", "w") as f:
                table = PrettyTable()
                table.field_names = ["Page", "Distinct Words Count"]
                # Now we sort the dictionary
                sorted_result = dict(sorted(self._results.items(), reverse=True, key=lambda i: i[1]))
                for page, count in sorted_result.items():
                    table.add_row([page, count])
                f.write(str(table))

    # MUST BE ADDED TO REPORT
    def _get_pages_for_threads_num(self):  # Adds as many not visited pages as the number of threads
        pages_extracted = []
        while True:
            if self._cursor >= len(self._queue):
                return pages_extracted  # Cursor exceeds the size of the self._queue
            if len(pages_extracted) == self._threads_num_used:
                return pages_extracted
            page = self._queue[self._cursor]
            global lock
            with lock:
                # page is accessed and so we increment the cursor
                self._cursor += 1
                if page not in self._visited_pages:
                    pages_extracted.append(page)

    def _add_page_to_visited(self, page):
        global lock
        with lock:
            self._visited_pages.add(page)

    def _extract_and_add_links_from_page(self, parsed_html: BeautifulSoup, page: str):
        global lock
        with lock:
            pages = extract_all_links(parsed_html)
            counter = 0
            for page in pages:
                if page not in self._visited_pages:
                    self._queue.append(page)
                    counter += 1
            print(f"{counter} new and unique pages are extracted from {page}")

    def _start(self):
        # The "with sync_playwright() as playwright" must be in the same thread. If "with sync_playwright() as playwright" is
        # in thead 1 and we spawn a new thread t2 from it, it will be problematic and we cannot swicth threads in playwright

        while self._counter <= self._limit and self._queue and self._cursor < len(self._queue):
            pages_extracted = self._get_pages_for_threads_num()
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(pages_extracted)) as executor:
                futures = [executor.submit(playwright_scraper, pages_extracted[i], i) for i in range(len(pages_extracted))]
                # Wait for all futures to complete and get the results
                for future in futures:
                    parsed_html, response, page = future.result()
                    self._add_page_to_visited(page)
                    self._counter += 1
                    print(f"Queue length is {len(self._queue)}")
                    print(f"Page {page} was scraped.")
                    self._store_scraped_page_result(parsed_html, page)
                    self._extract_and_add_links_from_page(parsed_html, page)

    def start(self):
        self._start()
