import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re

pc = input("Enter Postcode: ")
postcode = pc.upper()

# ===== Selenium setup =====
chrome_options = Options()
# chrome_options.add_argument("--headless=new")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--window-size=1200,800")
# chrome_options.add_argument("--log-level=3")
# chrome_options.add_argument("--disable-logging")

chrome_options.add_argument("--window-size=1200,800")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# Block images & CSS to speed up
prefs = {
    "profile.managed_default_content_settings.images": 2,
    "profile.managed_default_content_settings.stylesheets": 2
}
chrome_options.add_experimental_option("prefs", prefs)

def extract_agent_domain_from_href(href):
    if not href:
        return ""
    href = href.strip("/")
    if href.startswith("view-branch/"):
        match = re.search(r'^view-branch/([^/]+)', href)
        return match.group(1) if match else ""
    else:
        match = re.search(r'^([^/]+)', href)
        return match.group(1) if match else ""

driver = webdriver.Chrome(options=chrome_options)
driver.set_page_load_timeout(300)  # 5 minutes

# ===== Load main page =====
url = f"https://www.allagents.co.uk/find-agent/{postcode}"
driver.get(url)
time.sleep(3)

agent_data = []
seen = set()   # <-- To track unique agents
page_number = 1

while True:
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    cards = soup.find_all("div", class_="card-body")
    print(f"Found {len(cards)} agent cards on page {page_number}.")

    for card in cards:
        link_elem = card.select_one(".card-title a")
        if not link_elem or not link_elem.get("href"):
            continue

        name_elem = card.select_one(".card-title")
        address_elem = card.select_one(".agentAdd")
        phone_elem = card.select_one('a[href^="tel"]')

        name = name_elem.get_text(strip=True) if name_elem else "N/A"
        address = address_elem.get_text(strip=True) if address_elem else "N/A"
        phone = phone_elem.get_text(strip=True) if phone_elem else "N/A"

        href = link_elem["href"]
        domain = f"www.{extract_agent_domain_from_href(href)}"

        branch_elems = card.select('.list-btn')
        branch_count = "1"
        for elem in branch_elems:
            text = elem.get_text(strip=True)
            if "Branches" in text:
                match = re.search(r'(\d+)', text)
                if match:
                    branch_count = match.group(1)
                break

        # Unique key = Name + Address (avoids duplicates)
        unique_key = (name, address)

        if unique_key not in seen:
            seen.add(unique_key)
            agent_data.append({
                "Name": name,
                "Address": address,
                "Phone": phone,
                "Branches": branch_count,
                "Domain": domain
            })

    # ===== Try going to next page =====
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, 'button[title="Go to the next page"]')
        if "k-disabled" in next_button.get_attribute("class"):
            break  # No more pages

        # Scroll into view & click
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        driver.execute_script("arguments[0].click();", next_button)

        # Wait for page to change
        new_page = page_number + 1
        for _ in range(10):  # wait up to 10s
            time.sleep(1)
            if str(new_page) in driver.page_source:
                break
        page_number = new_page
        print(page_number)
    except Exception:
        break

# ===== Save to CSV =====
csv_file = f"new_test/{pc}_agents.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Name", "Address", "Phone", "Branches", "Domain"])
    writer.writeheader()
    writer.writerows(agent_data)

print(f"Saved {len(agent_data)} unique agents to {csv_file}")
driver.quit()
