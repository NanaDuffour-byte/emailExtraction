import imaplib
import email 
import webbrowser
import re
import time # to allow time before it closes
from playwright.sync_api import sync_playwright 
from email.header import decode_header

def safe_decode(body, encoding='utf-8'):
    try:
        return body.decode(encoding)
    except UnicodeDecodeError:
        try:
            return body.decode('latin-1')  
        except UnicodeDecodeError:
            return body.decode('utf-8', errors='ignore')  

# this function that extracts only the activation link
def extract_activation_link(text):
    url_pattern = r"https?://[^\s<>\"']+"  
    urls = re.findall(url_pattern, text)
    
    for url in urls:
        if "/activate/" in url:  # this filters via /activate/ to get the activation link  in isolation
            return url
    return None

# Gmail credentials
username = "mdtester7@gmail.com"
password = "anbd ycny svmt lsul"  

# Gmail IMAP server
server = "imap.gmail.com"
mail = imaplib.IMAP4_SSL(server)

try:
    # logging in to Gmail
    mail.login(username, password)
    
    # Select from inbox or spam
    #mail.select("inbox")
    mail.select("[Gmail]/Spam")

    status, messages = mail.search(None, '(SUBJECT "Aktivierung Ihrer digitalen Gesundheitsanwendung" FROM "do-not-reply@minddistrict.dev")')

    email_ids = messages[0].split()

    for email_id in email_ids: 
        
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                
                # Decode the subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")
                
                # Get the sender's email
                from_ = msg.get("From")
                
                print(f"Subject: {subject}")
                print(f"From: {from_}")
                
                email_body = ""

                # Check if the email is multipart (i.e., has both plain text and HTML parts)
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))

                        # Extract text if it is not an attachment
                        if "attachment" not in content_disposition and content_type in ["text/plain", "text/html"]:
                            body = part.get_payload(decode=True)
                            email_body += safe_decode(body) + "\n"
                else:
                    body = msg.get_payload(decode=True)
                    email_body += safe_decode(body)

                # Extract the activation link
                activation_link = extract_activation_link(email_body)

                if activation_link:
                    print("Activation Link:", activation_link)

                    #open the activation link
                    with sync_playwright() as p:
                        browser = p.chromium.launch(headless=False)
                        page = browser.new_page()
                        page.goto(activation_link)

                        #wait for 5 seconds to ensure page loads correctly
                        time.sleep(5)

                        #close the browser
                        browser.close()


                else:
                    print("No activation link found in the email.")

        print("-" * 50)

except Exception as e:
    print(f"Error: {e}")
finally:
    # Logout and close the connection
    mail.logout()
