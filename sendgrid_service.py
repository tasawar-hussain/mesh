import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from settings import FROM_EMAIL, IS_DEBUG, SENDGRID_API_KEY, TEMPLATE_ID


class SendgridService:
    def __init__(self):
        self.sendgrid_client = SendGridAPIClient(SENDGRID_API_KEY)
        self.template_id = TEMPLATE_ID
        self.sender = FROM_EMAIL

    def send_email(self, template_data, receipient):
        if receipient:
            message = Mail(from_email=self.sender, to_emails=receipient)
            message.dynamic_template_data = template_data
            message.template_id = self.template_id
            message.mail_settings = {"sandbox_mode": {"enable": IS_DEBUG}}
            try:
                response = self.sendgrid_client.send(message)
                return response
            except Exception as e:
                print(str(e.message))
                return -1
