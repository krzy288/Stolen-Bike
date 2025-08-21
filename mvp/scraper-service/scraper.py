import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, date, timedelta
import re
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)

class StolenBikeScraper:
    def __init__(self, config):
        self.config = config
        self.base_url = "https://www.olx.pl"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.results = []

    def search(self, mode="quick"):
        """Main search method"""
        search_terms = ["Rockrider EXPL 500", "Rockrider EXPL", "Rockrider"]
        
        if mode == "quick":
            pages = 1
            locations = self.config.locations[:3]  # First 3 locations for quick mode
            search_terms = search_terms[:3]  # First 3 search terms
        else:
            pages = 3
            locations = self.config.locations
        
        all_results = []
        
        logger.info(f"🔍 Searching {len(locations)} locations with {len(search_terms)} terms")
        
        for location in locations:
            logger.info(f"📍 Searching in: {location}")
            for term in search_terms:
                results = self.search_location(term, location, pages)
                all_results.extend(results)
                time.sleep(2)  # Be nice to OLX
        
        unique_results = self.remove_duplicates(all_results)
        logger.info(f"✅ Found {len(unique_results)} unique results after deduplication")
        
        return unique_results

    def search_location(self, search_term, location, pages):
        """Search in specific location"""
        results = []
        
        for page in range(1, pages + 1):
            url = self.build_search_url(search_term, location, page)
            logger.info(f"🔗 Searching URL: {url}")
            
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all ad containers
                ads = soup.find_all('div', {'data-cy': 'l-card'})
                if not ads:
                    # Try alternative selectors
                    ads = soup.find_all('div', class_=re.compile(r'css-.*'))[:40]  # Fallback
                
                page_results = []
                theft_date_results = []
                
                for ad in ads:
                    bike_data = self.extract_ad_data(ad)
                    if bike_data:
                        page_results.append(bike_data)
                        if self.is_posted_after_theft(ad):
                            theft_date_results.append(bike_data)
                
                # Only keep ads posted after theft date
                results.extend(theft_date_results)
                logger.info(f"📄 Page {page}: {len(page_results)} total ads, {len(theft_date_results)} posted after theft")
                
                if not ads:
                    logger.warning("No ads found on this page")
                    break
                    
            except Exception as e:
                logger.error(f"❌ Error scraping {url}: {e}")
                continue
        
        return results

    def build_search_url(self, query, location, page=1):
        """Build search URL with correct OLX format"""
        # Replace spaces with dashes for the query parameter
        encoded_query = query.replace(" ", "-")
        
        # Build URL with location before query
        url = f"{self.base_url}/sport-hobby/rowery/{location}/q-{encoded_query}/"
        
        # Add filters
        params = []
        # Sort by newest first
        params.append("search%5Border%5D=created_at:desc")
        
        # Add price filters with correct syntax
        if self.config.min_price:
            params.append(f"search%5Bfilter_float_price:from%5D={self.config.min_price}")
        if self.config.max_price:
            params.append(f"search%5Bfilter_float_price:to%5D={self.config.max_price}")
        
        if page > 1:
            params.append(f"page={page}")
            
        if params:
            url += "?" + "&".join(params)
            
        return url

    def extract_ad_data(self, ad_element):
        """Extract ad data from HTML element"""
        try:
            # Try multiple selectors for title
            title_elem = ad_element.find('h6') or ad_element.find('h4') or ad_element.find('a', class_=re.compile(r'.*title.*'))
            if not title_elem:
                return None
                
            title = title_elem.get_text(strip=True)
            if not title:
                return None
            
            # Extract URL
            link_elem = ad_element.find('a', href=True)
            if not link_elem:
                return None
            url = urljoin(self.base_url, link_elem['href'])
            
            # Extract price
            price_elem = ad_element.find('p', {'data-testid': 'ad-price'}) or ad_element.find(string=re.compile(r'\d+.*zł'))
            price = "No price"
            if price_elem:
                if hasattr(price_elem, 'get_text'):
                    price = price_elem.get_text(strip=True)
                else:
                    price = str(price_elem).strip()
            
            # Extract location and date
            location_elem = ad_element.find('p', {'data-testid': 'location-date'}) or ad_element.find(string=re.compile(r'.*[0-9]+.*'))
            location_date = "No location"
            if location_elem:
                if hasattr(location_elem, 'get_text'):
                    location_date = location_elem.get_text(strip=True)
                else:
                    location_date = str(location_elem).strip()
            
            relevance_score = self.calculate_relevance(title)
            
            return {
                "title": title,
                "url": url,
                "price": price,
                "location_date": location_date,
                "relevance_score": relevance_score,
                "posted_after_theft": self.is_posted_after_theft(ad_element)
            }
            
        except Exception as e:
            logger.error(f"❌ Error extracting ad data: {e}")
            return None

    def is_posted_after_theft(self, ad_element):
        """Check if ad was posted on or after the theft date"""
        try:
            # Look for date indicators
            location_date_elem = ad_element.find('p', {'data-testid': 'location-date'})
            if not location_date_elem:
                # Fallback: look for any element containing date info
                location_date_elem = ad_element.find(string=re.compile(r'dziś|wczoraj|today|yesterday|[0-9]+ (sierp|aug|sie)'))
            
            if location_date_elem:
                text = location_date_elem.get_text(strip=True).lower() if hasattr(location_date_elem, 'get_text') else str(location_date_elem).lower()
                
                # Check for recent posts (since theft was on 13.08.2025, we're looking for posts from that date onward)
                recent_indicators = ['dziś', 'today', 'wczoraj', 'yesterday']
                if any(indicator in text for indicator in recent_indicators):
                    return True
                
                # Check for specific date patterns
                if '13 sie' in text or '14 sie' in text or '15 sie' in text:
                    return True
                    
                # For now, be conservative and mark recent-sounding posts
                if any(word in text for word in ['sierpnia', 'sierp', 'aug']):
                    # Try to extract day number
                    day_match = re.search(r'(\d+)', text)
                    if day_match:
                        day = int(day_match.group(1))
                        if day >= 13:  # Posted on or after theft date
                            return True
            
            return False  # If we can't determine, assume it's old
            
        except Exception as e:
            logger.error(f"❌ Error checking theft date: {e}")
            return False

    def calculate_relevance(self, title):
        """Calculate relevance score for the bike ad"""
        score = 0
        title_lower = title.lower()
        
        # Brand matching
        if 'rockrider' in title_lower:
            score += 3
        
        # Model matching
        if 'expl' in title_lower:
            score += 2
        if '500' in title_lower:
            score += 2
        
        # Color matching
        if any(color in title_lower for color in ['black', 'czarny', 'czarna']):
            score += 1
        
        # Type matching
        if any(bike_type in title_lower for bike_type in ['mtb', 'mountain', 'górski']):
            score += 1
            
        # Brand indicators
        if 'decathlon' in title_lower:
            score += 1
            
        return score

    def remove_duplicates(self, results):
        """Remove duplicate ads based on URL"""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            if result['url'] not in seen_urls:
                unique_results.append(result)
                seen_urls.add(result['url'])
                
        return unique_results
