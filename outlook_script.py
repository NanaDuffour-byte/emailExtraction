import imaplib
import email 
from email.header import decode_header

def safe_decode(body, encoding='utf-8'):
    try:
        return body.decode(encoding)
    except UnicodeDecodeError:
        try:
            return body.decode('latin-1')  
        except UnicodeDecodeError:
            return body.decode('utf-8', errors='ignore')  

# Gmail credentials
username = "mdtester7@gmail.com"
password = "anbd ycny svmt lsul"  

# Gmail IMAP server
server = "imap.gmail.com"
mail = imaplib.IMAP4_SSL(server)

try:
    # Log in to Gmail
    mail.login(username, password)
    
   
    mail.select("inbox")

    status, messages = mail.search(None, '(SUBJECT "Aktivierung Ihrer digitalen Gesundheitsanwendung" FROM "n.duffour@minddistrict.com")')

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
                
                # Print subject and sender
                print(f"Subject: {subject}")
                print(f"From: {from_}")
                
                # Check if the email is multipart (i.e., has both plain text and HTML parts)
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()  # Get the content type of each part
                        content_disposition = str(part.get("Content-Disposition"))  # Check for attachments
                        
                        # If there's no attachment, and the content type is plain text
                        if "attachment" not in content_disposition:
                            if content_type == "text/plain":
                                # Decode the body of the email safely
                                body = part.get_payload(decode=True)
                                print(f"Body: {safe_decode(body)}")
                else:
                    # If the email is not multipart (only plain text), decode the body safely
                    body = msg.get_payload(decode=True)
                    print(f"Body: {safe_decode(body)}")
        
        print("-" * 50)

except Exception as e:
    print(f"Error: {e}")
finally:
    # Logout and close the connection
    mail.logout()
