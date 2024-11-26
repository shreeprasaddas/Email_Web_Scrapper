# Email Web Scraper

This project is an email web scraper designed to extract email addresses from web pages. It leverages Python libraries like BeautifulSoup, Selenium, and pandas for parsing and handling web content.

## Features
- Scrape email addresses from webpages.
- Handles both static and dynamic content.
- Supports exporting scraped data to CSV or other formats.

## Requirements
This project requires the following Python libraries:

- `beautifulsoup4`: For parsing HTML and extracting email addresses.
- `requests`: To make HTTP requests and fetch static HTML content.
- `selenium`: For handling dynamic webpages that require JavaScript execution.
- `pandas`: For handling and exporting data in tabular formats.
- `urllib3`: Utility for URL parsing and handling requests.
- `html5lib`: Alternative parser for BeautifulSoup.

To install all dependencies, run:

```bash
pip install -r requirements.txt
