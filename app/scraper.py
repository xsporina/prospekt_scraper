import json
import random
import time
from typing import Dict, List, Optional
from models.brochure import Brochure
from playwright.sync_api import sync_playwright, Locator

from utils.date_utils import extract_dates, is_valid_now, reformat_dates

class ProspektScraper:
    """ Scraper for prospektmaschine.de."""

    def __init__(self, hypermarket_url, date_format="%Y-%m-%d", output_file="output/output.json"):
        """ Initialize scraper.
        
        Args:
            hypermarket_url: URL to scrape
            output_file: Optional file name and/or path
        
        """
        self.hypermarket_url = hypermarket_url
        self.output_file = output_file
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        self.page = self.context.new_page()
        self.date_format = date_format
    
    def run(self):
        """ Main execution
        
        """
        try:
            self.navigate_to(self.hypermarket_url)
            sidebar_urls = self.get_sidebar_urls()
            results = self.process_all_shops(sidebar_urls)
            self.save_results(results)
        except Exception as e:
            print(f"Error occured: {e}")
        finally:
            self.close_browser()
    
    def navigate_to(self, url):
        """ Navigate to URL while imitating human behavior.
        
        """
        self.page.goto(url, wait_until="networkidle", timeout=30000)

        # Imitate human behavior with random delay and scrolling
        time.sleep(random.uniform(0.5, 1))
        self.page.evaluate("""async () => {
            window.scrollBy(0, 500);
            await new Promise(resolve => setTimeout(resolve, 200));
            window.scrollBy(0, document.body.scrollHeight * 0.7);
        }""")
            
    def get_sidebar_urls(self) -> Dict[str, str]:
        """ Get all URLs of shops from sidebar.
        
        Returns:
            Dictionary of shop names and their URLs { 'shop_name' : 'url' }

        """
        links = {}

        # Get sidebar and it's elements
        sidebar = self.page.locator("#left-category-shops")
        a_elements = sidebar.locator("a").all()

        for a in a_elements:
            shop_name = a.text_content()
            shop_href = a.get_attribute("href")

            if shop_name and shop_href:
                shop_url = "https://www.prospektmaschine.de" + shop_href
                links[shop_name.strip()] = shop_url

        return links
    
    def process_all_shops(self, sidebar_urls: Dict[str, str]) -> List[Brochure]:
        """ Process all shops on the sidebar.
        
        Args:
            sidebar_urls: Dictionary of shop names and URLs
        
        Returns:
            List of all valid brochures
        
        """
        all_valid_brochures = []

        for shop_name, url in sidebar_urls.items():
            if shop_name == "Kaufland":
                shop_brochures = self.process_shop(shop_name, url)
                all_valid_brochures.extend(shop_brochures)

        return all_valid_brochures
    
    def process_shop(self, shop_name: str, url: str) -> List[Brochure]:
        """ Process a single shop page.
        
        Args:
            shop_name: Name of the shop
            url: URL of the shop
        
        Returns:
            List of valid brochures from shop

        """
        print("Processing:", shop_name)
        try:
            self.navigate_to(url)

            # Select all the brochures on shop page
            page_brochures = self.page.locator(".page-body .brochure-thumb").all()
            if not page_brochures:
                return []
            
            # Find out which brochures are valid
            valid_brochures = []

            for brochure in page_brochures:
                # Parse brochure
                parsed_brochure = self.parse_brochure(brochure, shop_name)

                # If brochure is valid, append it to the list
                if parsed_brochure:
                    valid_brochures.append(parsed_brochure)
            
            return valid_brochures
        
        except Exception as e:
            print(f"Error while processing shop {shop_name}: {e}")
            return []
    
    def parse_brochure(self, brochure: Locator, shop_name: str) -> Optional[Brochure]:
        """ Parse brochure data.

        Args:
            brochure: Locator for brochure element
            shop_name: Name of the shop
        
        Returns:
            Brochure object if brochure is valid, else None
        
        """
        # Check if brochure is marked as 'old' by website
        if brochure.locator(".grid-item-old").count() > 1:
            return None
        
        # Get title and thumbnail
        title = brochure.locator("strong").text_content() or ""
        thumbnail = brochure.locator("img").get_attribute("src") or ""

        # Get text of the element with the dates
        date_text = brochure.locator(".grid-item-content small.hidden-sm").text_content()
        dates = extract_dates(date_text or "")
        
        # Format dates to yyyy-mm-dd
        if self.date_format != "%d.%m.%Y":
            dates = reformat_dates(dates, "%d.%m.%Y", self.date_format)

        # Check if date is currently valid
        if not is_valid_now(dates[0], dates[1], self.date_format):
            return None
        
        return Brochure(
            title= title,
            thumbnail= thumbnail,
            shop_name= shop_name,
            valid_from= dates[0],
            valid_to= dates[1]
        )

    def save_results(self, results: List[Brochure]):
        """ Save brochures to JSON file.
        
        Args:
            results: List of brochure objects

        """
        # print(len(results))

        # Convert dictionaries to JSON
        json_list = [b.__dict__ for b in results]
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(json_list, f, ensure_ascii=False, indent=4)
    
    def close_browser(self):
        """ Close browser and playwright. 
        
        """
        self.browser.close()
        self.playwright.stop()