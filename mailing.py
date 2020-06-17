from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP

from flask import current_app


class Mailsender:
    def __init__(self):
        self.smtp = SMTP(
            host='smtp.gmail.com',
            port=587,
        )
        self.registry_template = current_app.jinja_env.get_or_select_template('mail/register.html')
        self.registry_template_plain = current_app.jinja_env.get_or_select_template('mail/register_plain.html')
        self.smtp.starttls()
        self.smtp.login(current_app.config['GMAIL']['username'],
                        current_app.config['GMAIL']['password'])
        self.from_email = current_app.config['GMAIL']['from']

    def send_registration_email(self,
                                to_email: str,
                                username: str,
                                password: str):
        mime = MIMEMultipart("alternative")
        mime['Subject'] = "Ready To Go Out Event Administrator Registration"
        mime['From'] = self.from_email
        mime['To'] = to_email
        data_dict = dict(
            email=to_email,
            username=username,
            password=password,
        )
        mime.attach(MIMEText(self.registry_template_plain.render(data_dict), 'plain'))
        mime.attach(MIMEText(self.registry_template.render(data_dict), 'html'))
        self.smtp.sendmail(self.from_email, to_email, mime.as_string())

    def __enter__(self) -> 'Mailsender':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.smtp.close()
