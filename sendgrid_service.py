import logging

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import From, Mail, MailSettings, SandBoxMode

from settings import FROM_EMAIL, SENDGRID_API_KEY, TEMPLATE_ID


class SendgridService:
    def __init__(self):
        self.sendgrid_client = SendGridAPIClient(SENDGRID_API_KEY)

    def send_email_to_group(self, group_member_names, group_member_emails):
        if not group_member_emails:
            logging.info("No email recipients")
            return None

        print("*** To emails: ***")
        print(group_member_emails)
        from_email = From(email=FROM_EMAIL, name="Mesh")
        to_emails = group_member_emails

        message = Mail(from_email=from_email, to_emails=to_emails)
        message.template_id = TEMPLATE_ID
        message.dynamic_template_data = {"group_members": ', '.join(
            [str(elem) for elem in group_member_names])}

        message.mail_settings = MailSettings(sandbox_mode=SandBoxMode(enable=False))
        try:
            response = self.sendgrid_client.send(message)
            return response
        except Exception as e:
            logging.error(str(e))
            return None
