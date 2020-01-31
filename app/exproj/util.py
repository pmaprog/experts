import random
import string
import smtplib
from email.message import EmailMessage

from exproj import cfg


def random_string_digits(str_len=8):
    """Generate a random string of letters and digits """
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.SystemRandom().choice(letters_and_digits) for i in range(str_len))


def send_email(mail, link):
    server = smtplib.SMTP_SSL(cfg.SMTP_HOST, 465)
    server.login(cfg.MAIL_LOGIN, cfg.MAIL_PASSWORD)
    message = cfg.SITE_ADDR + "/confirm/" + link

    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = "confirmation link"
    msg['From'] = cfg.MAIL_LOGIN
    msg['To'] = mail
    server.send_message(msg)
    server.quit()
