from scraper.scraper import Scraper


def main():
    domains_list = ["https://www.bbc.com/", "https://www.voanews.com/", "https://en.wikipedia.org/wiki/Big_Bang"]
    THREADS_COUNT_BEING_USED = 2
    MAX_NUMBER_PAGES = 100
    scraper = Scraper(domains_list, MAX_NUMBER_PAGES, THREADS_COUNT_BEING_USED)
    scraper.start()


if __name__ == "__main__":
    main()
