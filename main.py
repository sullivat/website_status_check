"""
- website status alerts -

check websites for 200 (ok) status, if the site is down or not ok, send a message to recipients.

before using, BUILD A 'config.ini' file with your secrets and info!
I suggest using a throwaway gmail for this program, as I don't think 2-factor auth can
be enabled.

'config_template.ini' is provided as a template to create the config.ini file
with your own sites and email credentials.




Timothy Sullivan, 2017
"""


import configparser
import smtplib
from email.mime.text import MIMEText
import time
import logging
import datetime
import requests

####################
##    SETTINGS    ##
####################

# Parsing 'config.ini' settings
config = configparser.ConfigParser()
config.read('config.ini')
# create a list of sites from the config file
SITES = [config['sites'][k] for k in config['sites']]
# parse the email sending account from cofig.ini
SMTP_host = config['email']['host']
SMTP_port = int(config['email']['port'])
email_addr = config['email']['sender address']
email_password = config['email']['sender password']
recipients = config['email']['recipients']

# Set up logging, only logging INFO and higher priority messages
logging.basicConfig(
    filename=config['log']['filename'],
    level=logging.INFO,
    format='%(asctime)s %(message)s')


#####################
##    FUNCTIONS    ##
#####################


def check_website(site_addr):
    """
    check the status of each website provided by the input list of
    site address strings. 
    If 200: log the check.
    If anything else: log the status, send notice of possible site down.
    """

    for site in site_addr:
        logging.info("  CHECKING: {}".format(site))
        try:
            r = requests.head(site)
            if r.status_code != 200:
                send_notice(site)
                log_down_site(site, r)
            else:
                logging.info("            {0} status code is {1} ".format(
                    site, r.status_code, ))
        except requests.ConnectionError:
            send_notice(site)
            log_down_site(site, r)


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

    msg['Subject'] = 'YOUR SITE: {} IS DOWN!!!'.format(site)
    msg['From'] = email_addr
    msg['To'] = recipients

    server = smtplib.SMTP(SMTP_host, SMTP_port)
    server.starttls()
    server.login(email_addr, email_password)

    server.sendmail(email_addr, recipients, msg.as_string())
    server.quit()


def log_down_site(site, site_request):
    """ Logging message if a site does not respond correctly. """
    logging.warning("            {0} status code is {1} ".format(
        site, site_request.status_code, ))
    logging.warning("            {} is down, an email was sent".format(site, ))


def main():
    """ Main program to run. """
    while True:
        logging.debug('website check status: checking')
        check_website(SITES)
        logging.debug('website check status: sleeping for 5 min')
        time.sleep(300)



if __name__ == "__main__":
    main()
