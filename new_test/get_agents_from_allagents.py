from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import csv

pc = input("Enter Post Code: ")
postcode = pc.upper()


crome_options = Options()

crome_options.add_argument('--window-size=1200,800')
crome_options.add_argument('--disable-blink-features=AutomationControlled')

prefs = {
    'profile.managed_default_content_settings.images': 2,
    'profile.managed_default_content_settings.stylesheets': 2,
    'profile.managed_default_content_settings.fonts': 2
}

crome_options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(options=crome_options)

driver.set_page_load_timeout(60)


url = f'https://www.allagents.co.uk/find-agent/{postcode}'

driver.get(url)


wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'card-body')))

agents_data = []
seen = set()
page_number = 1

def extract_domain_from_href(href):
    if not href:
        return ''
    href = href.strip('/')
    if href.startswith("view-branch/"):
        match = re.search(r'^view-branch/([^/]+)', href)
    else:
        match = re.search(r'^([^/]+)', href)
    
    return match.group(1) if match else ''

while True:
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    cards = soup.find_all('div', class_='card-body')

    print(f'Page {page_number}: Found {len(cards)} agents')

    for card in cards:
        link_elem = card.select_one('.card-title a')
        if not link_elem or not link_elem.get('href'):
            continue

        name_elem = card.select_one('.card-title')
        address_elem = card.select_one('.agentAdd')
        phone_elem = card.select_one('a[href^="tel"]')

        name = name_elem.get_text(strip=True) if name_elem else "N/A"
        address = address_elem.get_text(strip=True) if address_elem else "N/A"
        phone = phone_elem.get_text(strip=True) if phone_elem else "N/A"

        href = link_elem["href"]    # /view-branch/potterandford.co.uk/chesham
        domain = f'www.{extract_domain_from_href(href)}'

        # Extract branch count 
        branch_count = 1
        branch_elems = card.select('.list-btn')

        for elem in branch_elems:
            text = elem.get_text(strip=True)
            if "Branches" in text:
                match = re.search(r'(\d+)', text)
                if match:
                    branch_count = match.group(1)
                break

        unique_key = (name, address)
        if unique_key not in seen:
            seen.add(unique_key)
            agents_data.append({
                'Name': name,
                'Address': address,
                'Phone': phone,
                "Branches": branch_count,
                "Domain": domain
            })

    # Pagination
    try:
        next_button =  wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'button[title="Go to the next page"]')
            )
        )

        # Stop is disabled
        if 'k-disabled' in next_button.get_attribute('class'):
            break

        # Get current cards (for staleness check)
        old_first_agent = driver.find_element(By.CLASS_NAME, "card-title").text

        # Click next
        driver.execute_script('arguments[0].click();', next_button)

        # Wait for page refresh (IMPORTANT)
        wait.until(
            lambda d: d.find_element(By.CLASS_NAME, "card-title").text != old_first_agent
        )
        
        page_number += 1

    except Exception as e:
        print("Pagination Ended or Error", e)
        break

csv_file = f'{pc}_agents.csv'

with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(
        f, 
        fieldnames=["Name", "Address", "Phone", "Branches", "Domain"]
    )

    writer.writeheader()
    writer.writerows(agents_data)

print(f"\n✅ Saved {len(agents_data)} unique agents to {csv_file}")     
driver.quit()
