import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime


# --- Extract first email from text ---
def extract_email(text):
    matches = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return matches[0] if matches else None


# --- Scrape email from website ---
def get_email_from_website(domain):
    base_url = "http://" + domain.replace("www.", "").strip()
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        # Try homepage
        response = requests.get(base_url, timeout=20, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            page_text = soup.get_text(separator="\n")
            email = extract_email(page_text)
            if email:
                return email

            # Look for "contact" pages
            contact_links = [a['href'] for a in soup.find_all("a", href=True) if "contact" in a['href'].lower()]
            for link in contact_links:
                if not link.startswith("http"):
                    link = base_url.rstrip("/") + "/" + link.lstrip("/")
                try:
                    contact_page = requests.get(link, timeout=10, headers=headers)
                    if contact_page.status_code == 200:
                        email = extract_email(contact_page.text)
                        if email:
                            return email
                except:
                    continue

    except Exception as e:
        print(f"⚠️ Error fetching {base_url}: {e}")

    return "Not Found"


def enrich_csv_with_emails(input_file, output_file):
    df = pd.read_csv(input_file)

    # Keep unique domains only
    df = df.drop_duplicates(subset=["Domain"], keep="first").reset_index(drop=True)

    # Fetch emails
    df["Email"] = df["Domain"].apply(get_email_from_website)
    today = datetime.today().strftime("%Y-%m-%d")
    df["Date"] = today

    df.to_csv(output_file, index=False)
    print(f"📂 Emails enriched and saved to {output_file}")

if __name__ == "__main__":
    enrich_csv_with_emails(
        r"C:\Users\gaura\OneDrive\Documents\AnayaSD Solutions\Files\estate_agents_data\Chesham_agents.csv",
        "Chesham_with_emails.csv"
    )
