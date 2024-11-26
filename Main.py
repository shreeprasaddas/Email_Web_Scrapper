import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import html
import time

def extract_emails(soup):
    mailto_emails = set()
    text_emails = set()
    for tag in soup.find_all('a', href=True):
        href = tag.get('href', '')
        if href.startswith('mailto:'):
            email = href.split(':')[1].strip().lower()
            mailto_emails.add(email)
    page_text = soup.get_text()
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    text_emails.update(re.findall(email_pattern, page_text))
    obfuscated_pattern = r'[a-zA-Z0-9._%+-]+ \[at\] [a-zA-Z0-9.-]+ \[dot\] [a-zA-Z]{2,}'
    obfuscated_emails = re.findall(obfuscated_pattern, page_text)
    for obfuscated_email in obfuscated_emails:
        decoded_email = obfuscated_email.replace(' [at] ', '@').replace(' [dot] ', '.')
        text_emails.add(decoded_email.lower())
    html_entities_emails = re.findall(r'([a-zA-Z0-9._%+-]+&#64;[a-zA-Z0-9.-]+)', page_text)
    for html_email in html_entities_emails:
        decoded_email = html.unescape(html_email).lower()
        text_emails.add(decoded_email)
    return mailto_emails.union(text_emails)

def extract_links(base_url, soup, keywords):
    relevant_links = set()
    all_links = set()
    for tag in soup.find_all('a', href=True):
        url = urljoin(base_url, tag['href'])
        if base_url in url:
            if any(keyword in url.lower() for keyword in keywords):
                relevant_links.add(url.split('#')[0])
            all_links.add(url.split('#')[0])
    return list(relevant_links), list(all_links)

def fetch_with_requests(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def create_driver():
    options = Options()
    options.headless = True
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('window-size=1200x600')
    driver = webdriver.Chrome(options=options)
    return driver

def get_email_selenium(driver, base_url, keywords=["contact", "about", "support"], max_pages=20):
    visited = set()
    emails_found = set()
    queue = [base_url]
    while queue and len(visited) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        print(f"Scraping: {url}")
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            page_source = driver.page_source
            emails = extract_emails(BeautifulSoup(page_source, 'html.parser'))
            emails_found.update(emails)
            priority_links, other_links = extract_links(base_url, BeautifulSoup(page_source, 'html.parser'), keywords)
            for link in priority_links:
                if link not in visited:
                    queue.append(link)
            if not emails_found and len(visited) < max_pages:
                for link in other_links:
                    if link not in visited:
                        queue.append(link)
        except Exception as e:
            print(f"Error while scraping {url}: {e}")
            continue
    driver.quit()
    return list(emails_found)

def smart_email_scraper(base_url, keywords=["contact", "about", "support", "footer"], max_pages=20):
    try:
        response = fetch_with_requests(base_url)
        if response is None:
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        emails_found = extract_emails(soup)
        if not emails_found:
            print(f"No emails found with BeautifulSoup. Trying Selenium...")
            driver = create_driver()
            emails_found = get_email_selenium(driver, base_url, keywords, max_pages)
        return emails_found
    except requests.exceptions.RequestException as e:
        print(f"Error using requests: {e}. Attempting Selenium...")
        driver = create_driver()
        return get_email_selenium(driver, base_url, keywords, max_pages)

if __name__ == "__main__":
    websites = [
        "https://www.badolatorefrigerationnj.com/",
        "https://www.ageneralsewer.com/",
        "https://alpinegreen.net/",
        "http://www.doctorrooterplumbing.com/",
        "http://dependableappliancesi.com/",
        "https://positiverepair.com/",
        "https://www.homedepot.com/l/Old-Bridge-II/NJ/Old-Bridge/08857/957?emt=MSGMBGoogleMaps",
        "https://www.appliancerepairmiddletown.com/",
        "https://www.walmart.com/store/4153-old-bridge-nj/walmart-tech-services",
        "https://www.njpipedr.com/?utm_source=+GBP+Matawan",
        "http://gandmacr.com/"
    ]
    results = []
    all_emails = set()
    for website in websites:
        print(f"Starting scrape for: {website}")
        emails = smart_email_scraper(website, max_pages=20)
        emails_list = list(emails)
        if emails_list:
            email = emails_list[0]
            if email not in all_emails:
                all_emails.add(email)
                results.append({"Website": website, "Email": email})
        else:
            results.append({"Website": website, "Email": "N/A"})
    df = pd.DataFrame(results)
    df.to_csv('scraped_email_1.csv', index=False)
    print("Scraping completed. Results saved to 'scraped_emails_with_fallback.csv'")
