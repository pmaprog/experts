import random
import string
import smtplib
from email.message import EmailMessage

from . import config
from .db import *


def get_post_class(path):
    if 'question' in path:
        return Question
    if 'article' in path:
        return Article
    if 'comment' in path:
        return Comment
    raise ValueError('Can\'t determine class')


def random_string_digits(str_len=8):
    """Generate a random string of letters and digits """
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.SystemRandom().choice(letters_and_digits) for i in range(str_len))


def send_email(mail, link):
    server = smtplib.SMTP_SSL(config.SMTP_HOST, 465)
    server.login(config.MAIL_LOGIN, config.MAIL_PASSWORD)
    message = config.SITE_ADDR + "/confirm/" + link

    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = "confirmation link"
    msg['From'] = config.MAIL_LOGIN
    msg['To'] = mail
    server.send_message(msg)
    server.quit()
