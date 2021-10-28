# dynamic_IP_checker_updater
A python3 script written to be used in dynamic ISP environments. It checks your public IP then notifies the administrator (email and SMS) if the public IP has changed and updates Google Domain DNS records as needed.  

# Requirements

## Twilio
This script uses Twilio as the SMS provider to send automated texts. It cost me $1.00 a month to procure a Twilio number.

Python dependency:
`pip install twilio`

The following provides additional guidance for setup and use of Twilio SMS services:
https://www.twilio.com/docs/libraries/python

## Gmail
This script uses SMTP_SSL to send emails using Gmail.

It is recommended that you create a gmail account soley for sending the required emails. When doing so, you'll have to "Allow Less Secure Apps" in your Gmail settings for the SMTP services to function properly.

## Google Domains
This script is setup to use the Google Domains API as a means to alter DNS A records. 

You will have to change the following in the script to work with your domains:
1. `<Google Domains Dynamic DNS username>:<Google Domains Dynamic DNS password>`
2. `<domain or sub-domain>`

Example:
`https://<Google Domains Dynamic DNS username>:<Google Domains Dynamic DNS password>@domains.google.com/nic/update?hostname=<domain or sub-domain>&myip={}`

Additional information for the Google Domains Dynamic DNS API is here:
https://support.google.com/domains/answer/6147083?hl=en#zippy=%2Cuse-the-api-to-update-your-dynamic-dns-record

## Linux Scheduling
I used this script in a cronjob to make sure it was run every 4 hours. 

Tested using Ubuntu server 20

Simply edit `/etc/crontab` for system wide execution or use `crontab -e` for individual users.

Add this to the bottom of the file:
`0 */4   * * *   root    cd <path to script directory> && python3 ip_checker.py`

