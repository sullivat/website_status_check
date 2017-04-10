import configparser
import smtplib
from email.mime.text import MIMEText
import time
import logging
import datetime
import requests

from email_secrets import email_addr, email_password

# enable logging, only logging INFO and higher priority messages
logging.basicConfig(
    filename='my_sites_availability.log',
    level=logging.INFO,
    format='%(asctime)s %(message)s')

# config.ini parsing 
config = configparser.ConfigParser()
config.read('config.ini')
# create a list of sites from the config file
SITES = [config['sites'][k] for k in config['sites']]

def check_website(site_addr):
    """
    check the status of each website provided by the input list of
    site address strings. 
    If 200: log the check.
    If anything else: log the status, send notice of possible site down.
    """

    for site in site_addr:
        logging.info("  CHECKING: {}".format(site))
        r = requests.head(site)
        if r.status_code != 200:
            send_notice(site)
            log_down_site(site, r)
        else:
            logging.info("            {0} status code is {1} ".format(
                site, r.status_code, ))


def send_notice(site):
    """
    Handle the email notice of a down website
    """

    mail_body = """
    Your website {0} is not responding correctly!

    You might want to investigate this further.

    Have a nice day.
    
    error logged at {1}
    """.format(site, datetime.datetime.now())

    msg = MIMEText(mail_body)
    me = "sullivan.timm@gmail.com"

    msg['Subject'] = 'YOUR SITE: {} IS DOWN!!!'.format(site)
    msg['From'] = email_addr
    msg['To'] = me

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_addr, email_password)

    server.sendmail(email_addr, me, msg.as_string())
    server.quit()


def log_down_site(site, site_request):
    logging.warning("            {0} status code is {1} ".format(
        site, site_request.status_code, ))
    logging.warning("            {} is down, an email was sent".format(site, ))


def main():
    
    def send_terminal_clear():
        print(chr(27) + "[2J")

    while True:
        send_terminal_clear()
        print('website check status: checking')
        check_website(SITES)
        send_terminal_clear()
        print('website check status: sleeping for 5 min')
        time.sleep(300)
        send_terminal_clear()


if __name__ == "__main__":
    main()
