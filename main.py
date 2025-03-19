from app.scraper import ProspektScraper

if __name__ == "__main__":
    scrape_url = "https://www.prospektmaschine.de/hypermarkte/"
    scraper = ProspektScraper(scrape_url)
    scraper.run()