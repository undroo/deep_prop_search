import requests
from bs4 import BeautifulSoup
import json
from typing import Dict, Optional
from datetime import datetime
import random
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import logging

logger = logging.getLogger(__name__)

class DomainScraper:
    def __init__(self):
        """Initialize the Domain.com.au scraper with required headers and configuration."""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        }
        self.session = requests.Session()
        
        # Initialize Chrome options for Selenium
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=chrome_options)

    def get_property_data(self, url: str) -> Optional[Dict]:
        """
        Scrape property information from a Domain.com.au listing URL.
        
        Args:
            url: The Domain.com.au property listing URL
            
        Returns:
            Dictionary containing property details or None if failed
        """
        try:
            # Add a random delay between requests (1-3 seconds)
            time.sleep(random.uniform(1, 3))
            
            # Use Selenium to get the page content with JavaScript executed
            self.driver.get(url)
            
            # Wait for the page to load and expand the description
            wait = WebDriverWait(self.driver, 10)
            try:
                # Try to find and click the "Read more" button
                read_more_button = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="listing-details__description"] button'))
                )
                read_more_button.click()
                # Wait for the content to expand
                time.sleep(2)
            except:
                # If no "Read more" button is found, continue
                pass
            
            # Get the page source after JavaScript execution
            page_source = self.driver.page_source
            
            # Parse the HTML
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract property information
            property_data = {
                "basic_info": {
                    "url": url,
                    "title": self._get_text(soup, 'h3[data-testid="listing-details__description-headline"]'),
                    "property_type": self._get_property_type(soup),
                    "price": None  # Initialize price as None
                },
                "address": {
                    "full_address": self._get_address(soup),
                },
                "features": {
                    "bedrooms": self._get_feature_value(soup, "Bed"),
                    "bathrooms": self._get_feature_value(soup, "Bath"),
                    "parking": self._get_feature_value(soup, "Parking"),
                    "property_size": self._clean_size(self._get_text(soup, '[data-testid="listing-details__floor-area"]')),
                    "land_size": self._clean_size(self._get_text(soup, '[data-testid="listing-details__land-area"]')),
                },
                "description": self._get_text(soup, '[data-testid="listing-details__description"]'),
                "agent_details": {
                    "agency_name": self._get_text(soup, '[data-testid="listing-details__agent-agency-name"]'),
                    "agent_name": self._get_text(soup, '[data-testid="listing-details__agent-enquiry-agent-profile-link"]'),
                },
                "inspection_times": self._get_inspection_times(soup),
                "images": self._get_images(),  # Changed to use Selenium directly
            }
            
            # Try different price selectors
            price_selectors = [
                '[data-testid="listing-details__summary-title"]',
                '[data-testid="listing-details__price"]',
                '[data-testid="listing-details__price-text"]',
                '.listing-price',
            ]

            # Try each selector until we find a valid price
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price = self._clean_price(price_element.get_text(strip=True))
                    if price:  # Only set if we got a valid price
                        property_data["basic_info"]["price"] = price
                        break
            
            return property_data
            
        except Exception as e:
            print(f"Error scraping property data: {e}")
            return None
        finally:
            # Close the browser
            self.driver.quit()

    def _get_text(self, soup: BeautifulSoup, selector: str) -> str:
        """Extract text from an element if it exists."""
        element = soup.select_one(selector)
        if not element:
            return ""
        
        return element.get_text(strip=True)

    def _get_property_type(self, soup: BeautifulSoup) -> str:
        """Extract property type using multiple possible selectors."""
        # Try different possible selectors for property type
        selectors = [
            'div[data-testid="listing-summary-property-type"]',
            'span[data-testid="property-features-feature-property_type"]',
            'div.property-info__property-type'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return ""

    def _get_address(self, soup: BeautifulSoup) -> str:
        """Extract full address using multiple possible selectors."""
        # Try different possible selectors for address
        selectors = [
            'h1[data-testid="listing-details__button-copy-link"]',
            'div[data-testid="listing-details__button-copy-wrapper"]',
            'div[data-testid="listing-summary-address"]',
            'h1.property-info__address'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return ""

    def _get_feature_value(self, soup: BeautifulSoup, feature_name: str) -> Optional[int]:
        """
        Extract numeric feature value (beds, baths, parking) from the property features.
        Returns an integer or None if no valid number is found.
        
        Args:
            soup: BeautifulSoup object
            feature_name: Base name of the feature (e.g., "Bed" for "Bed" or "Beds")
        """
        # Define variations of feature names
        variations = {
            "Bed": ["Bed", "Beds", "Bedroom", "Bedrooms"],
            "Bath": ["Bath", "Baths", "Bathroom", "Bathrooms"],
            "Parking": ["Parking", "Car Space", "Car Spaces", "Garage", "Garages"]
        }
        
        # Get the appropriate variations for the feature
        feature_variations = variations.get(feature_name, [feature_name])
        
        # Try each variation
        for variation in feature_variations:
            # Try to find the feature text
            feature = soup.find('span', string=lambda text: text and variation.lower() in (text.lower() if text else ""))
            if feature:
                # First try to find the value in a previous sibling span
                value = feature.find_previous('span')
                if value:
                    number = re.search(r'\d+', value.get_text(strip=True))
                    if number:
                        return int(number.group())
                
                # If not found, try to find the number in the feature text itself
                number = re.search(r'\d+', feature.get_text(strip=True))
                if number:
                    return int(number.group())
        
        return None

    def _clean_price(self, price_text: str) -> Optional[int]:
        """
        Clean price text and convert to integer.
        Example: "$1,500,000" -> 1500000
        """
        if not price_text:
            return None
        
        try:
            # Make sure we're dealing with a price string
            if not any(char in price_text.lower() for char in ['$', 'price', 'from', 'offers']):
                return None
            
            # Remove common price-related words
            price_text = price_text.lower()
            price_text = price_text.replace('from', '')
            price_text = price_text.replace('offers above', '')
            price_text = price_text.replace('offers over', '')
            price_text = price_text.replace('guide', '')
            
            # Extract numbers, ensuring we have a dollar sign or price indicator
            if '$' in price_text:
                # Get the text after the dollar sign
                price_part = price_text.split('$')[1].strip()
                # Remove any text after numbers and decimals
                price_part = ''.join(char for char in price_part if char.isdigit() or char == '.' or char == ',')
                # Remove commas and convert to integer
                if price_part:
                    return int(price_part.replace(',', '').split('.')[0])
            
            return None
            
        except Exception as e:
            print(f"Error cleaning price: {e}")
            return None

    def _clean_size(self, size_text: str) -> Optional[float]:
        """
        Clean size text and convert to float (in square meters).
        Example: "150m²" -> 150.0
        """
        if not size_text:
            return None
        
        # Extract the numeric value
        number = re.search(r'[\d.]+', size_text)
        if number:
            try:
                return float(number.group())
            except ValueError:
                return None
        return None

    def _get_inspection_times(self, soup: BeautifulSoup) -> list:
        """Extract inspection times if available."""
        times = []
        inspection_elements = soup.select('[data-testid="listing-details__inspection-time"]')
        for element in inspection_elements:
            times.append(element.get_text(strip=True))
        return times

    def _get_images(self) -> list:
        """Extract property images using Selenium to handle dynamic loading."""
        images = []
        try:
            logger.info("Starting image extraction process...")
            wait = WebDriverWait(self.driver, 10)
            
            # Find and click the Photos button
            logger.info("Looking for Photos button...")
            photos_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="listing-details__toolbar-icon photos"]'))
            )
            logger.info("Found Photos button, clicking it...")
            photos_button.click()
            
            # Wait for the gallery to load
            logger.info("Waiting for gallery to initialize...")
            time.sleep(2)  # Give time for the gallery to initialize
            
            # Find the next button for navigation using its title
            logger.info("Looking for Next button...")
            next_button = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button[title="Next (arrow right)"]'))
            )
            logger.info("Found Next button")
            
            # Keep track of seen images to avoid duplicates
            seen_images = set()
            image_count = 0
            no_new_images_count = 0  # Track how many times we've seen no new images
            
            while True:
                image_count += 1
                logger.info(f"\nProcessing image #{image_count}")
                
                # Get all visible images and take the last one (rightmost)
                logger.info("Looking for visible image elements...")
                visible_images = self.driver.find_elements(By.CSS_SELECTOR, 'img[class="pswp__img"]')
                if not visible_images:
                    logger.info("No visible images found")
                    break
                    
                # Get the last (rightmost) image
                last_img = visible_images[-1]
                src = last_img.get_attribute('src')
                alt = last_img.get_attribute('alt')
                logger.info(f"Processing last image - src: {src}, alt: {alt}")
                
                # Only add if we have a valid src and haven't seen it before
                if src and src not in seen_images:
                    images.append(src)
                    seen_images.add(src)
                    no_new_images_count = 0  # Reset counter when we find a new image
                    logger.info(f"Added new image to collection. Total unique images: {len(images)}")
                else:
                    no_new_images_count += 1
                    logger.info(f"No new image found. Consecutive no-new-images count: {no_new_images_count}")
                
                # If we haven't found any new images in 5 consecutive attempts, we're done
                if no_new_images_count >= 5:
                    logger.info("No new images found in 5 consecutive attempts - finished with gallery")
                    break
                
                # Try to click next button
                try:
                    logger.info("Attempting to click Next button...")
                    next_button.click()
                    logger.info("Successfully clicked Next button")
                    time.sleep(0.5)  # Wait for the next image to load
                except Exception as e:
                    logger.info(f"Could not click Next button: {str(e)}")
                    logger.info("Reached end of gallery")
                    break
            
            logger.info(f"\nImage extraction complete:")
            logger.info(f"Total images processed: {image_count}")
            logger.info(f"Total unique images found: {len(images)}")
            
            # Close the gallery modal
            logger.info("Looking for close button...")
            close_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="pswp-header-btn-close"]'))
            )
            logger.info("Found close button, clicking it...")
            close_button.click()
            logger.info("Gallery closed successfully")
            
        except Exception as e:
            logger.error(f"Error in image extraction: {str(e)}")
            logger.error("Full error details:", exc_info=True)
        
        return images

    def save_results(self, results: Dict, filename: str):
        """
        Save scraping results to a JSON file in the outputs directory.
        
        Args:
            results: Dictionary containing scraping results
            filename: Base filename to save results to
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Ensure outputs directory exists
        os.makedirs("outputs", exist_ok=True)
        output_file = f"outputs/{filename}_raw_{timestamp}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"✓ Raw data saved to {output_file}")
        except Exception as e:
            print(f"⚠ Error saving raw data: {e}")



