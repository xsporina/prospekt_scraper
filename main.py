from scraper.scraper import ProspektScraper

if __name__ == "__main__":
    scraper = ProspektScraper("https://www.prospektmaschine.de/hypermarkte/")
    scraper.run()