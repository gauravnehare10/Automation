import os
import re
import smtplib
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from email.message import EmailMessage
from email.utils import make_msgid

# ================== CONFIG ==================
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

SENT_LOG = r"C:\Users\gaura\onedrive\documents\AnayaSD Solutions\Files\estate_agents_data\sent_emails.csv"
SIGNATURE_PATH = r"C:\Users\gaura\OneDrive\Documents\AnayaSD Solutions\Files\estate_agents_data\signature.png"
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
    subject = "I’ve found the perfect property… but what about the mortgage?"
    body = '''
Dear Sir/Madam,

You’ve probably had a buyer say something like this:
“I’ve found the perfect property, but I’m worried I won’t be approved for a mortgage. What should I do?”

As estate agents, you’re the first point of contact when clients share these concerns. While property is your focus, arranging mortgages and protection is ours.

At AAI Financials, we partner with estate agents to support buyers in situations like these by providing expert mortgage and protection advice. We specialise as an Independent Mortgage and Protection Advisor providing expert guidance with access to the Whole of Market.

Here’s why estate agents like you choose us:
- No-fee service – Clients receive expert mortgage and protection advice at zero cost, making the process stress-free and attractive.
- Highly competitive commission (25%) – We offer one of the most rewarding commission structures in the market.
- End-to-end client support – Backed by our advanced integrated system, both you and your clients can track the progress of each mortgage application in real-time.
- Faster completions – Close lender relationships and proactive updates help transactions move smoothly.
- Stronger client loyalty – A no-fee, hassle-free experience builds trust and increases referrals.

We believe our combination of no client fees, a top-tier commission package, and a technology-driven client experience sets us apart and ensures a win–win partnership.

I’d love the chance to discuss how we can support your business and clients. Please let me know a convenient time to connect.

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
  <body style="font-family: Arial, sans-serif; font-size:15px; color:#333; line-height:1.6;">
    <p>Dear Sir/Madam,</p>

    <p>You’ve probably had a buyer say something like this:<br>
    <i>“I’ve found the perfect property, but I’m worried I won’t be approved for a mortgage. What should I do?”</i></p>

    <p>As estate agents, you’re the first point of contact when clients share these concerns. While property is your focus, arranging mortgages and protection is ours.</p>

    <p>At <b>AAI Financials</b>, we partner with estate agents to support buyers in situations like these by providing expert mortgage and protection advice. 
    We specialise as an <strong>Independent Mortgage and Protection Advisor</strong> providing expert guidance with access to the Whole of Market.</p>

    <p><b>Here’s why estate agents like you choose us:</b></p>
    <ul>
      <li>No-fee service – Clients receive expert mortgage and protection advice at zero cost, making the process stress-free and attractive.</li>
      <li>Highly competitive commission (25%) – One of the most rewarding commission structures in the market.</li>
      <li>End-to-end client support – Both you and your clients can track applications in real-time.</li>
      <li>Faster completions – Strong lender relationships and proactive updates ensure smooth transactions.</li>
      <li>Stronger client loyalty – A no-fee, hassle-free experience builds trust and increases referrals.</li>
    </ul>

    <p>We believe our combination of no client fees, a top-tier commission package, and a technology-driven client experience sets us apart and ensures a win–win partnership.</p>

    <p>I’d love the chance to discuss how we can support your business and clients.<br>
    Please let me know a convenient time to connect.</p>

    <p>Kind regards,<br>
    <b>Vishal Dhoke</b><br>
    <a href="https://www.aaifinancials.com">AAI Financials</a></p>

    <p>📝 <a href="https://aaifinancials.com/app/introducer/sign-up">Sign up as an Introducer</a><br>
    📹 <a href="https://youtu.be/s-EYrBHtuX8">Watch Guide Video</a></p>

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
  </body>
</html>
""", subtype="html")

    # Attach signature
    if os.path.exists(SIGNATURE_PATH):
        with open(SIGNATURE_PATH, "rb") as img:
            msg.get_payload()[1].add_related(img.read(), "image", "png", cid=sig_cid, filename="AAI_Signature.png", disposition="inline" )

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

    # sent_now = []

    # # Send only valid emails & few branches
    # for _, row in df.iterrows():
    #     try:
    #         branches = int(row["Branches"]) if str(row["Branches"]).isdigit() else 0
    #         if branches < 10 and row["Email"] not in ["Not Found", None, ""]:
    #             send_email(row["Email"])
    #             sent_now.append({"Domain": row["Domain"], "Email": row["Email"], "DateSent": today})
    #     except Exception as e:
    #         print(f"⚠️ Skipped {row['Domain']} due to error: {e}")

    # # Update log
    # if sent_now:
    #     save_sent_emails(pd.DataFrame(sent_now))
    #     print(f"📝 Log updated → {SENT_LOG}")


# --- Run Example ---
if __name__ == "__main__":
    enrich_csv_with_emails(
        r"C:\Users\gaura\OneDrive\Documents\AnayaSD Solutions\Files\estate_agents_data\Chesham_agents.csv",
        "Chesham_with_emails.csv"
    )
