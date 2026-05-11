#!/usr/bin/env python3
"""
Web Scraper with Excel Export
Main scraper application
"""

import os
import json
import time
from typing import Dict, List, Any
from datetime import datetime

# Import modules
from parsers.bs4_parser import BeautifulSoupParser
from parsers.selenium_parser import SeleniumParser
from exporters.excel_exporter import ExcelExporter
from utils.data_cleaner import clean_data
from utils.logger import setup_logger

class WebScraper:
    """Main web scraper class"""
    
    def __init__(self, headless: bool = True, browser: str = "chrome"):
        """Initialize scraper with configuration"""
        self.logger = setup_logger(__name__)
        self.headless = headless
        self.browser = browser
        self.selenium_parser = SeleniumParser(headless=headless)
        self.bs4_parser = BeautifulSoupParser()
        self.excel_exporter = ExcelExporter()
        
    def scrape(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Main scraping method
        
        Args:
            config: Scraping configuration dictionary
        
        Returns:
            List of scraped items
        """
        self.logger.info(f"Starting scrape: {config.get('name', 'Unnamed')}")
        
        results = []
        current_url = config['url']
        
        # Handle pagination
        for page in range(1, config.get('pages', 1) + 1):
            self.logger.info(f"Scraping page {page}/{config.get('pages', 1)}")
            
            try:
                # Get page content
                if config.get('use_selenium', False):
                    html = self.selenium_parser.get_page(current_url)
                else:
                    html = self.bs4_parser.get_page(current_url)
                
                # Parse page with selectors
                page_results = self._parse_page(html, config['selectors'])
                results.extend(page_results)
                
                # Update URL for next page if pagination is configured
                if page < config.get('pages', 1) and 'pagination' in config:
                    current_url = self._get_next_page_url(html, config['pagination'])
                    if not current_url:
                        self.logger.info("No more pages found")
                        break
                
                # Respect crawl delay
                time.sleep(config.get('delay', 1))
                
            except Exception as e:
                self.logger.error(f"Error scraping page {page}: {str(e)}")
                continue
        
        self.logger.info(f"Scraped {len(results)} items total")
        return results
        
    def _parse_page(self, html: str, selectors: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse HTML page with given selectors"""
        items = []
        
        try:
            # Use appropriate parser based on HTML source
            if "<html" in html.lower():
                parser = self.bs4_parser
            else:
                parser = self.selenium_parser
            
            # Find all item containers if specified
            container_selector = selectors.get('container', None)
            if container_selector:
                containers = parser.find_elements(html, container_selector)
            else:
                containers = [html]  # Single item
            
            # Process each container
            for container in containers:
                item = {}
                
                for field_name, field_config in selectors.items():
                    if field_name == 'container':
                        continue
                    
                    # Handle different selector types
                    if isinstance(field_config, dict):
                        selector = field_config['selector']
                        field_type = field_config.get('type', 'text')
                        clean_rules = field_config.get('clean', [])
                        regex = field_config.get('regex', None)
                    else:
                        selector = field_config
                        field_type = 'text'
                        clean_rules = []
                        regex = None
                    
                    # Extract data
                    try:
                        if field_type == 'text':
                            value = parser.get_text(container, selector)
                        elif field_type == 'html':
                            value = parser.get_html(container, selector)
                        elif field_type == 'href':
                            value = parser.get_attribute(container, selector, 'href')
                        elif field_type == 'src':
                            value = parser.get_attribute(container, selector, 'src')
                        else:
                            value = parser.get_text(container, selector)
                        
                        # Apply cleaning rules
                        value = clean_data(value, clean_rules, regex)
                        item[field_name] = value
                        
                    except Exception as e:
                        self.logger.warning(f"Field '{field_name}' not found: {str(e)}")
                        item[field_name] = None
                
                items.append(item)
            
        except Exception as e:
            self.logger.error(f"Error parsing page: {str(e)}")
        
        return items
        
    def _get_next_page_url(self, html: str, pagination_config: Dict[str, Any]) -> str:
        """Get URL for next page"""
        try:
            if pagination_config.get('type') == 'css':
                next_button = self.bs4_parser.find_element(html, pagination_config['next_button'])
                if next_button:
                    return self.bs4_parser.get_attribute(next_button, 'href')
            
            # Add more pagination types here
            
        except Exception as e:
            self.logger.warning(f"Pagination error: {str(e)}")
        
        return None
        
    def export_to_excel(self, data: List[Dict[str, Any]], filename: str, 
                       config: Dict[str, Any] = None) -> str:
        """
        Export scraped data to Excel
        
        Args:
            data: List of dictionaries with scraped data
            filename: Output filename
            config: Export configuration
        
        Returns:
            Path to created file
        """
        try:
            # Apply default config if none provided
            if not config:
                config = {
                    'sheet_name': 'Data',
                    'format': {}
                }
            
            # Handle filename templates
            if '{timestamp}' in filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = filename.replace('{timestamp}', timestamp)
            
            # Create output directory if needed
            os.makedirs('output', exist_ok=True)
            full_path = os.path.join('output', filename)
            
            # Export to Excel
            self.excel_exporter.export(data, full_path, config)
            
            self.logger.info(f"Exported to {full_path}")
            return full_path
            
        except Exception as e:
            self.logger.error(f"Export error: {str(e)}")
            raise
            
    def close(self):
        """Clean up resources"""
        try:
            self.selenium_parser.close()
        except:
            pass

# Command line interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python scraper.py <config_file.json>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    try:
        # Load configuration
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Initialize and run scraper
        scraper = WebScraper(headless=config.get('headless', True))
        results = scraper.scrape(config)
        
        # Export results
        if 'output' in config:
            output_config = config['output']
            filename = output_config.get('filename', 'output.xlsx')
            scraper.export_to_excel(results, filename, output_config)
        
        print(f"✅ Scraping completed. Found {len(results)} items.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
    
    finally:
        scraper.close()