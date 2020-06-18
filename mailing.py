import typing
from abc import ABC, abstractmethod
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP

from flask import current_app, g

if typing.TYPE_CHECKING:
    from database import Application


def plain_template(path: str) -> tuple:
    return path, 'plain'


def html_template(path: str) -> tuple:
    return path, 'html'


class Mailjob(ABC):
    templates = []
    subject = None

    def __init__(self, sender: typing.Optional['Mailsender'] = None):
        if sender is None:
            try:
                sender = g.mail_senders[-1]
            except:
                raise TypeError("Either provide a Mailsender, or run this in a Mailsender context.")
        self.templates = [(current_app.jinja_env.get_or_select_template(template), mime_type)
                          for template, mime_type in self.__class__.templates]
        self.sender = sender

    def _get_message(self, to_email: str, data: dict) -> MIMEMultipart:
        mime = MIMEMultipart("alternative")
        mime['Subject'] = self.subject
        mime['From'] = self.sender.from_email
        mime['To'] = to_email
        for template, mime_type in self.templates:
            mime.attach(MIMEText(template.render(data), mime_type))
        return mime

    def _send_message(self, to_email: str, **data):
        data.update(email=to_email)
        mime = self._get_message(to_email, data)
        self.sender.send_mime(to_email, mime)

    @abstractmethod
    def send(self, **kwargs):
        return NotImplemented


class RegistrationMail(Mailjob):
    subject = 'Ready To Go Out Event Administrator Registration'
    templates = [
        plain_template('mail/register_plain.html'),
        html_template('mail/register.html'),
    ]

    def send(self, to_email: str, username: str, password: str):
        super()._send_message(to_email=to_email, username=username, password=password)


class ApplicationSentMail(Mailjob):
    subject = 'Ready To Go Out Event Application'
    templates = [
        plain_template('mail/application_sent_plain.html'),
        html_template('mail/application_sent.html')
    ]

    def send(self, to_email: str):
        super()._send_message(to_email=to_email)


class NewApplicationMail(Mailjob):
    subject = 'New Ready To Go Out Event Application'
    templates = [
        plain_template('mail/new_application_plain.html'),
        html_template('mail/new_application.html'),
    ]

    def send(self, to_email: str, application: 'Application'):
        super()._send_message(to_email=to_email, application=application)


class Mailsender:
    def __init__(self):
        if current_app.config['GMAIL'] == 'log':
            self.smtp = SMTP(
                host='smtp.gmail.com',
                port=587,
            )
            self.smtp.starttls()
            self.smtp.login(current_app.config['GMAIL']['username'],
                            current_app.config['GMAIL']['password'])
            self.from_email = current_app.config['GMAIL']['from']
        else:
            self.smtp = None
            self.log = True

    def send_mime(self, to_email: str, mime: MIMEBase):
        if self.smtp:
            self.smtp.sendmail(self.from_email, to_email, mime.as_string())
        if self.log:
            print('SENDING EMAIL')
            print('=' * 20)
            print(mime.as_string())
            print('=' * 20)

    def __enter__(self) -> 'Mailsender':
        if 'mail_senders' not in g:
            g.mail_senders = []
        g.mail_senders.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.smtp:
            self.smtp.close()
        del g.mail_senders[-1]
