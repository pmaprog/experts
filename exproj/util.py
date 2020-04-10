import random
import string
import smtplib
from email.message import EmailMessage

from exproj import config
from exproj.db import Question, Article, Comment


def routes(bp, types, rule='', **options):
    def decorator(f):
        for type in types:
            endpoint = options.pop('endpoint', f.__name__)
            bp.add_url_rule(f'/{type}{rule}', endpoint, f, **options)
        return f
    return decorator


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


def send_reset_email(email, new_password):
    server = smtplib.SMTP_SSL(config.SMTP_HOST, 465)
    server.login(config.MAIL_LOGIN, config.MAIL_PASSWORD)
    message = 'Your new password - ' + new_password

    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = "Your new password link"
    msg['From'] = config.MAIL_LOGIN
    msg['To'] = email
    server.send_message(msg)
    server.quit()


def send_500_email(error):
    server = smtplib.SMTP_SSL(config.SMTP_HOST, 465)
    server.login(config.MAIL_LOGIN, config.MAIL_PASSWORD)
    message = str(error)

    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = "Your new password link"
    msg['From'] = config.MAIL_LOGIN
    msg['To'] = config.SUPER_ADMIN_MAIL
    server.send_message(msg)
    server.quit()
