import os
import re
import time
import random
import logging
import requests
import pandas as pd
import smtplib

from bs4 import BeautifulSoup
from dotenv import load_dotenv, find_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from email.message import EmailMessage
from email.utils import make_msgid
from datetime import datetime

# ================== CONFIG ==================

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))

SENT_LOG = os.getenv("SENT_LOG_PATH")
SIGNATURE_PATH = os.getenv("SIGNATURE_PATH")

MAX_SCRAPE_WORKERS = 10
MAX_EMAIL_WORKERS = 3

HEADERS = {"User-Agent": "Mozilla/5.0"}

# Logging
logging.basicConfig(
    filename="Automation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ================== VALIDATION ==================

def normalize_domain(domain):
    domain = str(domain).strip().lower()
    domain = re.sub(r"\(.*?\)", "", domain)
    domain = domain.replace(" ", "")
    domain = domain.replace("http://", "").replace("https://", "")
    domain = domain.replace("www.", "")
    return domain


def is_valid_domain(domain):
    pattern = r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"
    return domain if re.match(pattern, domain) else None


def clean_domains(df):
    df["Domain"] = df["Domain"].apply(normalize_domain)
    df["Domain"] = df["Domain"].apply(is_valid_domain)

    before = len(df)
    df = df[df["Domain"].notna()].reset_index(drop=True)
    after = len(df)

    logging.info(f"Removed {before - after} invalid domains")
    return df


# ================== UTILITIES ==================

def extract_email(text):
    matches = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return matches[0] if matches else None


def is_valid_email(email):
    return isinstance(email, str) and "@" in email and "." in email


def extract_number(val):
    match = re.search(r"\d+", str(val))
    return int(match.group()) if match else 0


# ================== REQUEST ==================

def safe_request(url, retries=3):
    for attempt in range(retries):
        try:
            time.sleep(random.uniform(0.5, 1.5))
            response = requests.get(url, timeout=10, headers=HEADERS)
            if response.status_code == 200:
                return response
        except Exception as e:
            logging.warning(f"Retry {attempt+1} failed for {url}: {e}")
    return None


def try_urls(domain):
    urls = [
        f"https://{domain}",
        f"http://{domain}",
        f"https://www.{domain}",
        f"http://www.{domain}",
    ]

    for url in urls:
        response = safe_request(url)
        if response:
            return response, url

    return None, None


# ================== SCRAPER ==================

def get_email_from_website(domain):
    try:
        response, base_url = try_urls(domain)
        if not response:
            return "Not Found"

        # parser fallback
        try:
            soup = BeautifulSoup(response.text, "lxml")
        except:
            soup = BeautifulSoup(response.text, "html.parser")

        text = soup.get_text(separator="\n")

        # direct email
        email = extract_email(text)
        if email:
            return email

        # mailto links
        for a in soup.find_all("a", href=True):
            if "mailto:" in a["href"]:
                return a["href"].replace("mailto:", "").strip()

        # contact page
        for a in soup.find_all("a", href=True):
            if "contact" in a["href"].lower():
                link = a["href"]

                if not link.startswith("http"):
                    link = base_url.rstrip("/") + "/" + link.lstrip("/")

                contact_res = safe_request(link)
                if contact_res:
                    email = extract_email(contact_res.text)
                    if email:
                        return email

    except Exception as e:
        logging.error(f"Scraping failed for {domain}: {e}")

    return "Not Found"


# ================== PARALLEL SCRAPING ==================

def fetch_emails_parallel(domains):
    results = {}

    with ThreadPoolExecutor(max_workers=MAX_SCRAPE_WORKERS) as executor:
        future_to_domain = {
            executor.submit(get_email_from_website, d): d for d in domains
        }

        for future in as_completed(future_to_domain):
            domain = future_to_domain[future]
            try:
                email = future.result()
                results[domain] = email
                logging.info(f"Scraped: {domain} → {email}")
            except Exception as e:
                results[domain] = "Not Found"
                logging.error(f"Error for {domain}: {e}")

    return results


# ================== LOG ==================

def load_sent_emails():
    if SENT_LOG and os.path.exists(SENT_LOG):
        return pd.read_csv(SENT_LOG)
    return pd.DataFrame(columns=["Domain", "Email", "DateSent"])


def save_sent_emails(df_new):
    if SENT_LOG and os.path.exists(SENT_LOG):
        df_old = pd.read_csv(SENT_LOG)
        df_all = pd.concat([df_old, df_new]).drop_duplicates(
            subset=["Domain", "Email"]
        )
    else:
        df_all = df_new

    df_all.to_csv(SENT_LOG, index=False)


# ================== MAIN ==================

def enrich_and_send(input_file, output_file):
    df = pd.read_csv(input_file)

    df = df.drop_duplicates(subset=["Domain"])

    # ✅ CLEAN DOMAINS HERE
    df = clean_domains(df)

    sent_df = load_sent_emails()
    already_sent = set(sent_df["Domain"].tolist())

    df = df[~df["Domain"].isin(already_sent)]

    if df.empty:
        logging.info("No valid domains to process.")
        return

    # ---- SCRAPE ----
    email_map = fetch_emails_parallel(df["Domain"].tolist())
    df["Email"] = df["Domain"].map(email_map)

    today = datetime.today().strftime("%Y-%m-%d")
    df["Date"] = today

    df.to_csv(output_file, index=False)

    # ---- FILTER ----
    valid_rows = []

    for _, row in df.iterrows():
        branches = extract_number(row.get("Branches", 0))
        email = row["Email"]

        if branches < 10 and is_valid_email(email):
            valid_rows.append(row)

    # ---- LOG ----
    sent_now = pd.DataFrame([
        {"Domain": row["Domain"], "Email": row["Email"], "DateSent": today}
        for row in valid_rows
    ])

    if not sent_now.empty:
        save_sent_emails(sent_now)

    logging.info("Process completed successfully.")


# ================== RUN ==================

if __name__ == "__main__":
    enrich_and_send(
        input_file="hp1_agents.csv",
        output_file="hp1_agents_with_emails.csv"
    )