from app.scraper import ProspektScraper

if __name__ == "__main__":
    scrape_url = "https://www.prospektmaschine.de/hypermarkte/"
    date_format = "%Y-%m-%d" # Date format of valid_from and valid_to
    output_file="output/output.json"

    scraper = ProspektScraper(scrape_url, date_format, output_file)
    scraper.run()