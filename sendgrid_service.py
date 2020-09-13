import logging
import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import From, Mail, MailSettings, SandBoxMode, To

from settings import (FROM_EMAIL, IS_DEBUG, SENDGRID_API_KEY, SG_SANDBOX_MODE,
                      TEMPLATE_ID)


class SendgridService:
    def __init__(self):
        self.sendgrid_client = SendGridAPIClient(SENDGRID_API_KEY)

    def send_email(self, template_data, receipient):
        if receipient:
            from_email = From(email=FROM_EMAIL, name="Tasawar Hussain")
            to_emails = To(receipient)
            message = Mail(from_email=from_email, to_emails=to_emails)
            message.template_id = TEMPLATE_ID
            message.dynamic_template_data = template_data
            sandbox_mode = SandBoxMode(enable=SG_SANDBOX_MODE)
            message.mail_settings = MailSettings(sandbox_mode=sandbox_mode)
            try:
                response = self.sendgrid_client.send(message)
                return response
            except Exception as e:
                logging.error(str(e))
                return None
