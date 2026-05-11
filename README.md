# Web Scraper with Excel Export 🕷️📊

**Professional web scraping tool with Excel export functionality**

## Features
- 🕸️ Scrape websites using BeautifulSoup and Selenium
- 📊 Export data to Excel (XLSX) with formatting
- 🔍 CSS selector and XPath support
- 📁 Multiple page scraping with pagination
- 📈 Data cleaning and transformation
- 📦 Configurable scraping profiles

## Tech Stack
- Python 3.9+
- BeautifulSoup4 for HTML parsing
- Selenium for JavaScript-heavy sites
- Pandas for data manipulation
- OpenPyXL for Excel export
- Requests for HTTP operations

## Installation

```bash
# Clone repository
git clone https://github.com/blistartunivers-afk/web-scraper-excel.git
cd web-scraper-excel

# Install dependencies
pip install beautifulsoup4 selenium pandas openpyxl requests python-dotenv

# Install ChromeDriver (for Selenium)
# Download from https://chromedriver.chromium.org/
# Or use: webdriver-manager (auto-download)

# Run example
python scraper.py examples/amazon_profile.json
```

## Quick Start

### Basic Usage
```python
from scraper import WebScraper

# Initialize scraper
scraper = WebScraper(headless=True)

# Scrape a simple page
url = "https://example.com/products"
selectors = {
    "title": "h1.product-title",
    "price": "span.price",
    "description": "div.description"
}

results = scraper.scrape(url, selectors)
print(results)

# Export to Excel
scraper.export_to_excel(results, "output.xlsx")
```

### Configuration File
Create a JSON configuration file:
```json
{
  "name": "Amazon Product Scraper",
  "url": "https://www.amazon.com/s?k={query}",
  "pages": 3,
  "selectors": {
    "title": {
      "selector": "h2.a-size-mini",
      "type": "text"
    },
    "price": {
      "selector": "span.a-offscreen",
      "type": "text",
      "clean": ["[^0-9.]", ""]
    },
    "rating": {
      "selector": "span.a-icon-alt",
      "type": "text",
      "regex": "([0-9.]+)"
    },
    "url": {
      "selector": "a.a-link-normal",
      "type": "href"
    }
  },
  "pagination": {
    "next_button": "a.s-pagination-next",
    "delay": 2
  },
  "output": {
    "filename": "amazon_products_{timestamp}.xlsx",
    "sheet_name": "Products",
    "format": {
      "header": {
        "bold": true,
        "background": "#4472C4",
        "color": "#FFFFFF"
      }
    }
  }
}
```

## Project Structure
```
web-scraper-excel/
├── scraper.py                # Main scraper class
├── config.py                # Configuration loader
├── exporters/               # Export modules
│   ├── excel_exporter.py    # Excel export functionality
│   ├── csv_exporter.py      # CSV export
│   └── json_exporter.py     # JSON export
├── parsers/                 # HTML parsers
│   ├── bs4_parser.py        # BeautifulSoup parser
│   └── selenium_parser.py   # Selenium parser
├── utils/                   # Utilities
│   ├── data_cleaner.py      # Data cleaning functions
│   ├── logger.py            # Logging setup
│   └── helpers.py           # Helper functions
├── examples/                # Example configurations
│   ├── amazon_profile.json  # Amazon scraping profile
│   ├── ecommerce_profile.json # Generic e-commerce
│   └── news_profile.json    # News scraping profile
├── output/                  # Output directory (created automatically)
├── .env.example             # Environment template
├── requirements.txt         # Dependencies
└── README.md                # This file
```

## Advanced Features

### Pagination Support
```json
"pagination": {
  "type": "css",
  "next_button": "a.next-page",
  "max_pages": 10,
  "delay": 1.5
}
```

### Data Cleaning
```json
"clean": [
  ["[^0-9.]", ""],      # Remove non-numeric characters
  ["^\s+|\s+$", ""],   # Trim whitespace
  ["(\$|€)", ""],       # Remove currency symbols
  ["\.00$", ""]         # Remove .00 from prices
]
```

### Excel Formatting
```json
"format": {
  "header": {
    "bold": true,
    "background": "#4472C4",
    "color": "#FFFFFF",
    "font_size": 12
  },
  "columns": {
    "price": {
      "number_format": "$#,##0.00",
      "width": 15
    },
    "rating": {
      "number_format": "0.0",
      "width": 10
    }
  }
}
```

## Examples

### Example 1: Simple Product Scraper
```python
from scraper import WebScraper

config = {
    "url": "https://webscraper.io/test-sites/e-commerce/allinone",
    "selectors": {
        "name": "a.title",
        "price": "h4.price",
        "description": "p.description"
    }
}

scraper = WebScraper()
results = scraper.scrape(config)
scraper.export_to_excel(results, "products.xlsx")
```

### Example 2: Paginated Scraping
```python
config = {
    "url": "https://webscraper.io/test-sites/e-commerce/allinone/computers",
    "pages": 3,
    "selectors": {
        "name": "a.title",
        "price": "h4.price"
    },
    "pagination": {
        "next_button": "a.page-link[rel='next']"
    }
}

scraper = WebScraper(headless=True)
results = scraper.scrape(config)
print(f"Scraped {len(results)} items from {config['pages']} pages")
```

## Error Handling

The scraper includes comprehensive error handling:
- Connection timeouts
- Invalid selectors
- CAPTCHA detection
- Rate limiting
- Element not found

## Performance Optimization

- **Caching**: Cache responses to avoid duplicate requests
- **Concurrency**: Use threading for multiple pages
- **Lazy Loading**: Scroll to load dynamic content
- **Headless Mode**: Run browser in background

## Deployment

### Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "scraper.py", "examples/amazon_profile.json"]
```

Build and run:
```bash
docker build -t web-scraper .
docker run -v $(pwd)/output:/app/output web-scraper
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License - See [LICENSE](LICENSE) for details.

## Contact

**blistartunivers-afk** - [GitHub Profile](https://github.com/blistartunivers-afk)

Project Link: [https://github.com/blistartunivers-afk/web-scraper-excel](https://github.com/blistartunivers-afk/web-scraper-excel)

---