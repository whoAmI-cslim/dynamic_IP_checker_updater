import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64

class emailer():
    def __init__(self):
        self.port = 465 # I use SMTP_SSL for my emails, therefore I use port 465. You can change to tls if you'd like, but I recommend SSL
        # I recommend creating a Gmail account solely for the purpose of sending these emails. I created one named <lastnamehomentwork@gmail.com>
        self.sender_email = "<insert created gmail account>"
        self.receiver_email = "<insert normal gmail account>"
        self.html = ""
        self.subject = ""
        self.console_output = ""
        
    def email_connector(self):
        self.user = "<insert created gmail account or username>"
        # I used base64 for my pw. It's not really secure at all. It's not recommended to hardcode your passwords. 
        # One can use a getpassword() or input() function if they're manually running it. 
        # I am using a cron job, and therefore simply hardcoded the password in base64 to at least try to obfuscate it somewhat.  
        base64_message = "<base64 version of gmail account password>"
        base64_bytes = base64_message.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        self.password = message_bytes.decode('ascii')
        self.context = ssl.create_default_context()
        self.message = MIMEMultipart('alternative')

        # These values are passed from the send_same_mail() and the send_change_mail() functions from ip_checker.py 
        self.message['Subject'] = self.subject
        self.message['From'] = self.sender_email
        self.message['To'] = self.receiver_email

        content = MIMEText(self.html, 'html')
        self.message.attach(content)

        with smtplib.SMTP_SSL('smtp.gmail.com', self.port, context=self.context) as server:
            server.login(self.user, self.password)
            server.sendmail(self.sender_email, self.receiver_email, self.message.as_string())
        
        print(self.console_output)

if __name__ == '__main__':
    emailer()