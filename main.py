from app.scraper import ProspektScraper

if __name__ == "__main__":
    scrape_url = "https://www.prospektmaschine.de/hypermarkte/"
    date_format = "%Y-%m-%d"
    
    scraper = ProspektScraper(scrape_url, date_format)
    scraper.run()