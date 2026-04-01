import os
from dotenv import find_dotenv, load_dotenv
from bs4 import BeautifulSoup
import requests
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import time
import random
import pandas as pd
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid
from datetime import datetime


dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

SENT_LOG = os.getenv("SENT_LOG_PATH")
SIGNATURE_PATH = os.getenv("SIGNATURE_PATH")

MAX_SCRAPE_WORKERS = 10
MAX_EMAIL_WORKERS = 3



# Logging Setup

logging.basicConfig(
    filename='Automation.log',
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

HEADERS = {'User-Agent': "Mozilla/5.0"}

def extract_email(text):
    matches = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return matches[0] if matches else None


def is_valid_email(email):
    return isinstance(email, str) and "@" in email and "." in email


def extract_number(val):
    match = re.search(r"\d+", str(val))
    return int(match.group()) if match else 0


def safe_request(url, retries=3):
    for attempt in range(retries):
        try:
            time.sleep(random.uniform(0.5, 1.5))
            response = requests.get(url, timeout=10, headers=HEADERS)
            if response.status_code == 200:
                return response

        except Exception as e:
            logging.warning(f'Retry {attempt+1} failed for {url}: {e}')
        
    return None


def get_email_from_website(domain):
    base_url = f'https://{domain.replace('www.', '').strip()}'

    try:
        response = safe_request(base_url)
        if not response:
            return "Not Found"
        
        soup = BeautifulSoup(response.text, 'lxml')
        text = soup.get_text(separator='\n')

        email = extract_email(text)

        if email:
            return email
        
        for a in soup.find_all('s', href=True):
            if 'contact' in a['href'].lower():
                link = a['href']
                if link.startwith('http'):
                    link = base_url.rstrip('/') + '/' + link.lstrip('/')

                contact_res = safe_request(link)
                if contact_res:
                    email = extract_email(contact_res.text)
                    if email:
                        return email

    except Exception as e:
        logging.error(f'Scrapping failed for {domain}: {e}')

    return "Not Found"


# Parallel Scrapping

def fetch_emails_parallel(domains):
    results = []

    with ThreadPoolExecutor(max_workers=MAX_SCRAPE_WORKERS) as executor:
        future_to_domain = {
            executor.submit(get_email_from_website, domain): domain
            for domain in domains
        }

        for future in as_completed(future_to_domain):
            domain = future_to_domain[future]
            try:
                email = future.result()
                results.append((domain, email))
                logging.info(f"Scraped: {domain} → {email}")
            except Exception as e:
                logging.error(f"Error for {domain}: {e}")
                results.append((domain, "Not Found"))

    return dict(results)


# ---------- LOG HANDLING ----------

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

# ---------- EMAIL SENDER ----------

def send_email(to_email):
    try:
        msg = EmailMessage()
        sig_cid = make_msgid()

        msg["Subject"] = "Earn 25% Commission on Every Mortgage Referral"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email

        msg.set_content("Please view this email in HTML format.")

        msg.add_alternative(f"""
        <html>
        <body>
        <p>Dear Sir/Madam,</p>
        <p>We offer mortgage referral partnerships with 25% commission.</p>
        <p>Let’s collaborate!</p>
        <p>Regards,<br><b>AAI Financials</b></p>
        <img src="cid:{sig_cid[1:-1]}" width="250">
        </body>
        </html>
        """, subtype="html")

        if SIGNATURE_PATH and os.path.exists(SIGNATURE_PATH):
            with open(SIGNATURE_PATH, "rb") as img:
                msg.get_payload()[1].add_related(
                    img.read(), "image", "png", cid=sig_cid
                )

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        logging.info(f"Email sent to {to_email}")

    except Exception as e:
        logging.error(f"Email failed for {to_email}: {e}")


# ---------- PARALLEL EMAIL SENDING ----------

def send_emails_parallel(email_list):
    with ThreadPoolExecutor(max_workers=MAX_EMAIL_WORKERS) as executor:
        executor.map(send_email, email_list)


# ---------- LOG HANDLING ----------

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



def normalize_domain(domain):             # www.clements-estate-agents
    domain = str(domain).strip().lower()

    # remove protocol
    domain = domain.replace("http://", "").replace("https://", "")      # http://www.clements-estate-agents

    # remove www
    domain = domain.replace("www.", "")

    # remove brackets content
    domain = re.sub(r"\(.*?\)", "", domain)

    # remove spaces
    domain = domain.replace(" ", "")

    # remove trailing slash
    domain = domain.rstrip("/")

    return domain


def is_valid_domain(domain):
    domain = normalize_domain(domain)

    # strict domain regex
    pattern = r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"

    if re.match(pattern, domain):
        return domain
    return None


# ---------- MAIN PIPELINE ----------

def enrich_and_send(input_file, output_file):
    df = pd.read_csv(input_file)

    # 🔥 CLEAN + VALIDATE DOMAINS
    df["Domain"] = df["Domain"].apply(is_valid_domain)

    # Remove invalid domains
    invalid_count = df["Domain"].isna().sum()

    if invalid_count > 0:
        logging.warning(f"Skipped {invalid_count} invalid domains")
    
    

    df = df.drop_duplicates(subset=["Domain"])
    df = df[df["Domain"].notna()].reset_index(drop=True)

    sent_df = load_sent_emails()
    already_sent = set(sent_df["Domain"].tolist())

    df = df[~df["Domain"].isin(already_sent)]

    if df.empty:
        logging.info("No new domains to process.")
        return

    # ---- SCRAPE EMAILS ----
    email_map = fetch_emails_parallel(df["Domain"].tolist())
    df["Email"] = df["Domain"].map(email_map)

    today = datetime.today().strftime("%Y-%m-%d")
    df["Date"] = today

    df.to_csv(output_file, index=False)

    # ---- FILTER FOR SENDING ----
    valid_rows = []

    for _, row in df.iterrows():
        branches = extract_number(row.get("Branches", 0))
        email = row["Email"]

        if branches < 10 and is_valid_email(email):
            valid_rows.append(row)

    emails_to_send = [row["Email"] for row in valid_rows]

    # ---- SEND EMAILS ----
    # send_emails_parallel(emails_to_send)

    # ---- SAVE LOG ----
    sent_now = pd.DataFrame([
        {"Domain": row["Domain"], "Email": row["Email"], "DateSent": today}
        for row in valid_rows
    ])

    if not sent_now.empty:
        save_sent_emails(sent_now)

    logging.info("Process completed successfully.")


# ---------- RUN ----------

if __name__ == "__main__":
    enrich_and_send(
        input_file="hp1_agents.csv",
        output_file="hp1_agents_with_emails.csv"
    )