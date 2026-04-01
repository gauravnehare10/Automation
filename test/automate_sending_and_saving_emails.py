import os
import re
import smtplib
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from email.message import EmailMessage
from email.utils import make_msgid
from dotenv import find_dotenv, load_dotenv

# ================== CONFIG ==================

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")


SENT_LOG = os.getenv("SENT_LOG_PATH")
SIGNATURE_PATH = os.getenv("SIGNATURE_PATH")
# ============================================


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


# --- Email Sending Function ---
def send_email(to_email):
    msg = EmailMessage()
    sig_cid = make_msgid()
    subject = "Earn 25% Commission on Every Mortgage Referral with AAI Financials"
    body = '''
Dear Sir/Madam,

I hope this email finds you well. I’m reaching out to introduce our proposition and explore the opportunity of working together. At AAI Financials, we specialise in providing expert mortgage and protection advice, and we’re excited about the potential to support your clients and become a trusted partner.

Here’s why estate agents like you choose us:
- No-fee service – Clients receive expert mortgage and protection advice at zero cost.
- Highly competitive commission (25%).
- End-to-end client support with real-time tracking.
- Faster completions due to close lender relationships.
- Stronger client loyalty with hassle-free experience.

I’d love the chance to discuss how we can support your business and clients. 
Kind regards,
Vishal Dhoke
AAI Financials
Sign up as an Introducer: https://aaifinancials.com/app/introducer/sign-up
Watch Introducer App Guide Video: https://youtu.be/s-EYrBHtuX8
'''
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    msg.set_content(body)
    msg.add_alternative(f"""
<html>
  <body style="margin:0; padding:0; background-color:#f9f9f9;">
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" bgcolor="#f9f9f9">
      <tr>
        <td align="center" style="padding:20px;">
          <table style="max-width:750px; width:100%; background:#ffffff; border-radius:8px; 
                        box-shadow:0 2px 8px rgba(0,0,0,0.1);" cellspacing="0" cellpadding="0" border="0">
            <tr>
              <td style="padding:25px; font-family: Arial, sans-serif; font-size: 15px; color:#333;">
                <p style="font-size:16px; color:#2E4053;">Dear Sir/Madam,</p>
                <p style="line-height:1.6; color:#444;">
                  I hope this email finds you well. At 
                  <a href="https://www.aaifinancials.com" style="color:#B22222; font-weight:bold">AAI Financials</a>, 
                  we specialise as an <b>Independent Mortgage and Protection Advisor</b>, 
                  providing expert guidance with access to the <b>Whole of Market</b>.
                </p>
                <h3 style="color:#884EA0;">Why estate agents choose us:</h3>
                <ul style="line-height:1.7; color:#444;">
                  <li><b>No-fee service</b> – Clients get advice at zero cost.</li>
                  <li><b>25% Commission</b> – One of the most rewarding packages.</li>
                  <li><b>End-to-end support</b> with real-time tracking.</li>
                  <li><b>Faster completions</b> due to strong lender ties.</li>
                  <li><b>Stronger loyalty</b> – Hassle-free experience builds trust.</li>
                </ul>
                <p style="margin-top:20px; color:#333;">
                  I’d love the chance to discuss how we can support your business and clients.
                </p>
                <p style="margin-top:30px; color:#2E4053;">
                  Kind regards,<br><b style="color:#884EA0;">Vishal Dhoke</b><br>
                  <a href="https://www.aaifinancials.com" style="color:blue;">AAI Financials</a>
                </p>
                <p>📝 <a href="https://aaifinancials.com/app/introducer/sign-up">Become an Introducer</a></p>
                <p>📹 <a href="https://youtu.be/s-EYrBHtuX8">Watch Guide Video</a></p>
                <p><img src="cid:{sig_cid[1:-1]}" style="width:300px;"></p>
                <hr style="margin:20px 0; border:0; border-top:1px solid #ccc;">
                <p style="font-size:12px; color:#777; line-height:1.5;">
                This e-mail is private and confidential. Access by or disclosure to anyone other than the intended recipient for any reason other than the business purpose for which the message is intended, is unauthorised. This e-mail and any views or opinions contained in it are subject to any terms and conditions agreed between the AAI Financials of companies and the recipient. 
                If you receive this communication in error, please notify us immediately and delete any copies. All reasonable precautions have been taken to ensure no viruses are present in this e-mail. AAI Financials cannot accept responsibility for loss or damage arising from the use of this e-mail.
                </p>
                <p style="font-size:12px; color:#777;">
                AAI Financials is a trading name of ANYASD Limited. Registered in England and Wales No 09674951. 
                Registered Office: 15 Crabbe Crescent, Chesham, HP5 3DD. Authorised and regulated by the Financial Conduct Authority under registration number 1036617.
                </p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
""", subtype="html")

    # Attach signature
    if os.path.exists(SIGNATURE_PATH):
        with open(SIGNATURE_PATH, "rb") as img:
            msg.get_payload()[1].add_related(img.read(), "image", "png", cid=sig_cid, filename="AAI_Signature.png")

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")


# --- Load & Save Sent Emails ---
def load_sent_emails():
    if os.path.exists(SENT_LOG):
        return pd.read_csv(SENT_LOG)
    return pd.DataFrame(columns=["Domain", "Email", "DateSent"])

def save_sent_emails(df_new):
    if os.path.exists(SENT_LOG):
        df_old = pd.read_csv(SENT_LOG)
        df_all = pd.concat([df_old, df_new], ignore_index=True).drop_duplicates(subset=["Domain", "Email"])
    else:
        df_all = df_new
    df_all.to_csv(SENT_LOG, index=False)


# --- Main Function ---
def enrich_csv_with_emails(input_file, output_file):
    df = pd.read_csv(input_file)

    # Keep unique domains only
    df = df.drop_duplicates(subset=["Domain"], keep="first").reset_index(drop=True)

    # Load already sent
    sent_df = load_sent_emails()
    already_sent_domains = set(sent_df["Domain"].tolist())

    # Exclude already contacted
    df = df[~df["Domain"].isin(already_sent_domains)].reset_index(drop=True)

    if df.empty:
        print(f"✅ All agents in {input_file} already contacted. No new emails sent.")
        return

    # Fetch emails
    df["Email"] = df["Domain"].apply(get_email_from_website)
    today = datetime.today().strftime("%Y-%m-%d")
    df["Date"] = today

    df.to_csv(output_file, index=False)
    print(f"📂 Emails enriched and saved to {output_file}")

    sent_now = []

    # Send only valid emails & few branches
    for _, row in df.iterrows():
        try:
            branches = int(row["Branches"]) if str(row["Branches"]).isdigit() else 0
            if branches < 10 and row["Email"] not in ["Not Found", None, ""]:
                send_email(row["Email"])
                sent_now.append({"Domain": row["Domain"], "Email": row["Email"], "DateSent": today})
        except Exception as e:
            print(f"⚠️ Skipped {row['Domain']} due to error: {e}")

    # Update log
    if sent_now:
        save_sent_emails(pd.DataFrame(sent_now))
        print(f"📝 Log updated → {SENT_LOG}")


# --- Run Example ---
if __name__ == "__main__":
    enrich_csv_with_emails(
        r"C:\Users\gaura\OneDrive\Documents\AnayaSD Solutions\Files\estate_agents_data\hp5_agents.csv",
        "hp5_agents_with_emails.csv"
    )
