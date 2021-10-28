import requests
import os
import json
from datetime import date, datetime

# This is the second file in the project
from ip_emailer import emailer

# pip install twilio
from twilio.rest import Client

class ip_updater():
    def __init__(self):
        # Initialize a few global variables for use later in the script
        self.current_ip = ""
        self.saved_ip = ""
        self.counter = 0
        
        # File path for where we will create and access a .json file for date, time, ip, and counter storage
        self.file_path = "<insert file path>/saved_ip.json"

        # Twilio account information initialization
        self.account_sid = "<insert Twilio account side>"
        self.auth_token = "<insert Twilio auth token>"
        self.main()
    
    def main(self):
        time = datetime.now()
        self.check_file_path()
        
        # Execute check_saved_ip function. If change detected, email and text is sent regarding change.
        change, content = self.check_saved_ip()
        if change == True:
            self.send_change_mail(content)
        else:
            # I set my crontab job on my linux server to execut this script every 4 hours
            # As such a 24 hour cycle of execution is 6 iterations. 
            # If 24 hours has passed, send email and text notification that IP has not changed.
            if self.counter >= 6:
                self.counter = 0
                content['Counter'] = self.counter
                with open (self.file_path, 'w') as jsonfile:
                    json.dump(content, jsonfile)
                self.send_same_mail(content)
            else:
                print("[" + time.strftime("%m/%d/%Y %H:%M:%S") + "]: Email not sent because 24 hours haven't elasped.\n")

    # This function checks to see if the .json file is created. If not, creates initial .json file for use later. If there, passes.
    def check_file_path(self):
        try:
            today = date.today()
            time = datetime.now()
            if not os.path.isfile(self.file_path):
                print("\n[" + time.strftime("%m/%d/%Y %H:%M:%S") + "]: File 'saved_ip.json' not found. Creating it for future use...")
                # Create dictionary structure for saved data for later use
                jsondict = {}    
                jsondict['Date'] = today.strftime("%B %d, %Y")
                jsondict['Time'] = time.strftime('%H:%M:%S')
                jsondict['Saved IP'] = self.get_current_ip()
                jsondict['Counter'] = self.counter
                with open (self.file_path, 'a') as jsonfile:
                    json.dump(jsondict, jsonfile)
            else:
                print("\n[" + time.strftime("%m/%d/%Y %H:%M:%S") + "]: IP Checker Script Running...")        
        except Exception as e:
            print("Error creating file: " + str(e))
    
    # Simple function to get current IP
    def get_current_ip(self):
        self.current_ip = requests.get('https://api.ipify.org').text
        return self.current_ip
    
    # Check to see if ip has changed from stored valued within the .json
    def check_saved_ip(self):
        with open (self.file_path, 'r') as jsonfile:
            content = json.load(jsonfile)
        self.current_ip = self.get_current_ip()
        self.saved_ip = content['Saved IP']
        today = date.today()
        time = datetime.now()
        # if IP has changed, execute text and email functions to alert to change
        if self.current_ip != self.saved_ip:
            print("\n[" + time.strftime("%m/%d/%Y %H:%M:%S") + "]: IP has changed since last check on " + content['Date'] + " at " + content['Time'])
            change = True
            content['Saved IP']=self.current_ip
            content['Date']=today.strftime("%B %d, %Y")
            content['Time']=time.strftime('%H:%M:%S')
            content['Counter']=content['Counter'] + 1
            self.counter = content['Counter']
            with open (self.file_path, 'w') as jsonfile:
                json.dump(content, jsonfile)
            print("\n[" + time.strftime("%m/%d/%Y %H:%M:%S") + "]: IP has changed to - " + self.current_ip + "\n")
            
            # Updates Google Domains DNS records with new IP address. You can repeat this as many times as needed for each subdomain/domain
            # Make sure to modify the url below with your information to ensure the API call works properly
            # Print commands are added solely for debugging purposes
            domain_update = requests.post('https://<insert google domain api user key>:<insert google domain api password key>@domains.google.com/nic/update?hostname=<insert sub-domain or domain>&myip={}'.format(self.current_ip))
            if 'good' in domain_update.text:
                print("\n[" + time.strftime("%m/%d/%Y %H:%M:%S") + "]: Subdomain was updated. Google responded with - " + domain_update.text)    
            else:
                print("\n[" + time.strftime("%m/%d/%Y %H:%M:%S") + "]: Attempted to update Subdomain. Google responded with - " + domain_update.text)
        
        # If IP hasn't changed, add to the 24 hour iterator     
        else:
            change=False
            content['Counter']=content['Counter'] + 1
            self.counter = content['Counter']
            with open (self.file_path, 'w') as jsonfile:
                json.dump(content, jsonfile)
            print("\n[" + time.strftime("%m/%d/%Y %H:%M:%S") + "]: IP has not changed")
            print("\n[" + time.strftime("%m/%d/%Y %H:%M:%S") + "]: Last datetime IP changed - " + content['Date'] + ' at ' + content['Time'] + "\n")
        return change, content
    
    # If IP changed, this function executes. Email includes HTML and can be modified however necessary to fit needs.
    def send_change_mail(self, content):
        time = datetime.now()
        html = """
        <html>
            <body style="background-color: #68FEEB;">
                <h1 style="text-align: center;"><span style="color: #ff0000;"><strong>IP Checker Update</strong></span></h1>
                <p style="text-align: center; font-size: 20px;"><span style="color: #000000;">IP has changed.</span></p>
                <p style="text-align: center; font-size: 20px;"><span style="color: #000000;">IP has changed to: <span style="text-decoration: underline;"><strong>{0}</strong></span></span></p>
                <p style="text-align: center; font-size: 20px;"><span style="color: #000000;">Change occured on <span style="text-decoration: underline;"><strong>{1}</strong></span> at <span style="text-decoration: underline;"><strong>{2}</strong></span></span></p>
            </body>
        </html>
        """.format(content['Saved IP'], content['Date'], content['Time'])
        subject = "***ALERT*** IP Address Has Changed ***ALERT***"
        email_send = emailer()
        email_send.subject = subject
        email_send.html = html
        email_send.console_output = "[" + time.strftime("%m/%d/%Y %H:%M:%S") + "]: IP Change Email Sent!\n" 
        email_send.email_connector()
        self.message_body = "On {} at {}, Network IP changed to {}".format(content['Date'], content['Time'], content['Saved IP'])
        self.send_text()
    
    # After 24 hours, if the IP hasn't changed, a text and email are sent to alert administrator. 
    # Used simply to ensure script is still functioning and working as intended. 
    def send_same_mail(self, content):
        time = datetime.now()
        html = """
        <html>
            <body style="background-color: #68FEEB;">
                <h1 style="text-align: center;"><span style="color: #ff0000;"><strong>IP Checker Update</strong></span></h1>
                <p style="text-align: center; font-size: 20px;"><span style="color: #000000;">IP has not changed.</span></p>
                <p style="text-align: center; font-size: 20px;"><span style="color: #000000;">IP is still: <span style="text-decoration: underline;"><strong>{0}</strong></span></span></p>
                <p style="text-align: center; font-size: 20px;"><span style="color: #000000;">IP has been the same since <span style="text-decoration: underline;"><strong>{1}</strong></span> at <span style="text-decoration: underline;"><strong>{2}</strong></span></span></p>
            </body>
        </html>
        """.format(content['Saved IP'], content['Date'], content['Time'])
        subject = "***NOTICE*** IP Address Has Not Changed ***NOTICE***"
        email_send = emailer()
        email_send.subject = subject
        email_send.html = html
        email_send.console_output = "[" + time.strftime("%m/%d/%Y %H:%M:%S") + "]: Email sent showing no IP change!\n"
        email_send.email_connector()
        self.message_body = "Network IP is {} and has not changed since {} at {}".format(content['Saved IP'], content['Date'], content['Time'])
        self.send_text()
    
    # Make sure that you use your twilio number in the from_ variable. This function sends text updates.
    def send_text(self):
        client = Client(self.account_sid, self.auth_token)
        message = client.messages.create(
            to="<insert SMS recipient>",
            from_="<insert SMS sender>",
            body=self.message_body
        )

if __name__ == '__main__':
    ip_updater()