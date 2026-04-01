from email.message import EmailMessage
import smtplib
from email.utils import make_msgid


email_address = "vishal@aaifinancials.com"
email_password = "Vishal-2025"

def send_email(to_email):
    msg = EmailMessage()
    sig_cid = make_msgid()
    subject = "Earn 25% Commission on Every Mortgage Referral with AAI Financials"
    body = '''
Dear Sir/Madam,

I hope this email finds you well. I’m reaching out to introduce our proposition and explore the opportunity of working together. At AAI Financials, we specialise in providing expert mortgage and protection advice, and we’re excited about the potential to support your clients and become a trusted partner.

Here’s why estate agents like you choose us:
No-fee service – Clients receive expert mortgage and protection advice at zero cost, making the process stress-free and attractive.
Highly competitive commission (25%) – We offer one of the most rewarding commission structures in the market.
End-to-end client support – Backed by our advanced integrated system, both you and your clients can track the progress of each mortgage application in real-time.
Faster completions – Close lender relationships and proactive updates help transactions move smoothly.
Stronger client loyalty – A no-fee, hassle-free experience builds trust and increases referrals.

We believe our combination of no client fees, a top-tier commission package, and a technology-driven client experience sets us apart and ensures a win–win partnership.

I’d love the chance to discuss how we can support your business and clients. Please let me know a convenient time to connect.
Kind regards,
Vishal Dhoke
AAI Financials
Sign up as an Introducer: https://aaifinancials.com/app/introducer/sign-up
Watch Introducer App Guide Video: https://youtu.be/s-EYrBHtuX8
'''
    msg["Subject"] = subject
    msg["From"] = email_address
    msg["To"] = to_email

    msg.set_content(body)
    msg.add_alternative(f"""
<html>
  <body style="margin:0; padding:0; background-color:#f9f9f9;">
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" bgcolor="#f9f9f9">
      <tr>
        <td align="center" style="padding:20px;">
			<table style="max-width:750px; width:100%; background:#ffffff; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.1);" cellspacing="0" cellpadding="0" border="0">
			  <tr>
				<td style="padding:25px; font-family: Arial, sans-serif; font-size: 15px; color:#333;">
					<p style="font-size:16px; color:#2E4053;">Dear Sir/Madam,</p>

					<p style="line-height:1.6; color:#444;">
			        	I hope this email finds you well. I’m reaching out to introduce our proposition and explore the opportunity of working together.
						At <a href="https://www.aaifinancials.com" style="text-decoration: none; color:#B22222; font-weight: bold">AAI Financials</a>, we specialise as an <b>Independent Mortgage and Protection Advisor</b>, providing expert guidance with access to <b>Whole of Market Research</b>. We’re excited about the potential to support your clients and become a trusted partner.
					</p>

				    <h3 style="color:#884EA0; margin-top:25px;">Here’s why estate agents like you choose us:</h3>
					<ul style="font-size:15px; line-height:1.7; color:#444; padding-left:18px;">
				    	<li><b style="color:#2F4F4F;">No-fee service</b> – Clients receive expert mortgage and protection advice at zero cost, making the process stress-free and attractive.</li>
						<li><b style="color:#2F4F4F;">Highly competitive commission (25%)</b> – We offer one of the most rewarding commission structures in the market.</li>
						<li><b style="color:#2F4F4F;">End-to-end client support</b> – Backed by our advanced integrated system, both you and your clients can track the progress of each mortgage application in real-time.</li>
						<li><b style="color:#2F4F4F;">Faster completions</b> – Close lender relationships and proactive updates help transactions move smoothly.</li>
						<li><b style="color:#2F4F4F;">Stronger client loyalty</b> – A no-fee, hassle-free experience builds trust and increases referrals.</li>
					</ul>

					<p style="line-height:1.6; margin-top:20px; color:#333;">
					   We believe our combination of no client fees, a top-tier commission package, and a technology-driven client experience sets us apart and ensures a win–win partnership.
					</p>

					<p style="line-height:1.6; color:#333;">
				    	I’d love the chance to discuss how we can support your business and clients. Please let me know a convenient time to connect.
					</p>

				    <p style="margin-top:30px; font-size:15px; color:#2E4053;">
					   Kind regards,<br>
						<b style="color:#884EA0;">Vishal Dhoke</b><br>
						<a href="https://www.aaifinancials.com" style="text-decoration: none; color: blue;">
						  AAI Financials
						</a>
	    			</p>

					 <!-- Links section -->
					  <div style="margin-top:10px; font-size:15px; color:#333;">
						<p>
						📝 Become an Introducer – 
						<a href="https://aaifinancials.com/app/introducer/sign-up" style="color:blue; text-decoration:none;">
						  Sign-up
						</a>
						</p>
					  <p>
						📹 Watch our short 
						<a href="https://youtu.be/s-EYrBHtuX8" style="color:blue; text-decoration:none;">
						  Introducer App Guide Video
						</a>
						</p>
					  </div>

					  <!-- Inline signature image -->
					  <p style="margin-top:15px;">
						<img src="cid:{sig_cid[1:-1]}" alt="AAI Financials Signature" style="width:300px;">
					  </p>

					  <!-- Confidentiality Notice -->
					  <div style="font-size: 12px; color: #777; margin-top:30px; line-height:1.5; border-top:1px solid #ddd; padding-top:15px;">
						<p>
						  This e-mail is private and confidential. Access by or disclosure to anyone other than the 
						  intended recipient for any reason other than the business purpose for which the message is 
						  intended, is unauthorised. This e-mail and any views or opinions contained in it are subject 
						  to any terms and conditions agreed between the AAI Financials of companies and the recipient. 
						  If you receive this communication in error, please notify us immediately and delete any copies. 
						  All reasonable precautions have been taken to ensure no viruses are present in this e-mail. 
						  AAI Financials cannot accept responsibility for loss or damage arising from the use of this e-mail.
						</p>
						<p>
						  AAI Financials is a trading name of ANYASD Limited. Registered in England and Wales No 09674951. 
						  Registered Office: 15 Crabbe Crescent, Chesham, HP5 3DD. Authorised and regulated by the 
						  Financial Conduct Authority under registration number 1036617.
						</p>
					  </div>
					</td>
				 </tr>
			</table>
		</td>
	  </tr>		
    </table>
  </body>
</html>
""", subtype="html")
    
    with open("C:\\Users\\gaura\\OneDrive\\Documents\\AnayaSD Solutions\\Files\\estate_agents_data\\signature.png", "rb") as img:
        msg.get_payload()[1].add_related(img.read(), "image", "png", cid=sig_cid, filename="AAI_Signature.png")

    try:
        with smtplib.SMTP_SSL("smtp.hostinger.com", 465) as server:
            server.login(email_address, email_password)
            server.send_message(msg)
            print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"Failed: {e}")


email = input("Enter the Email: ")
send_email(email)