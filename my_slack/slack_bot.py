from google_sheet_service import GoogleSheetService
from my_logger import my_logger
from settings import IS_DEBUG
from utils import random_groups

from .slack_service import SlackService
from .utils import message_text, test_users

logger = my_logger(__name__)


class SlackBot:
    def __init__(self):
        self.ss = SlackService()
        self.gss = GoogleSheetService()
        self.groups = self.__create_mesh_groups()
        self.sheet_title = self.__create_worksheet()

    def __get_contacts(self):
        """
        get all contacts from slack's lets meet channel
        """
        if IS_DEBUG:
            return test_users()

        return self.ss.get_users()

    def __create_mesh_groups(self):
        contacts = self.__get_contacts()
        logger.info("*** All Contacts ***")
        logger.info(contacts)
        logger.info(len(contacts))
        groups = random_groups(contacts)
        return groups

    def __create_worksheet(self):
        res = self.gss.create_worksheet()
        if res:
            return res.title
        return "DefaultSheet"

    def __upload_mesh_groups(self, groups):
        if not groups:
            logger.error("*** Invalid groups ***")
        logger.info("*** Uploading mesh groups on google sheet ***")
        logger.info(self.sheet_title)
        self.gss.upload_data(groups, self.sheet_title)

    def __send_invites(self):
        """
        Send slack direct messages invites to all the particpants
        """
        logger.info("*** Sending slack invites ***")
        successful_groups = []
        for group in self.groups:
            logger.info("*** Mesh Group ***")
            logger.info(group)

            text = message_text(group)
            response = self.ss.send_message(group, text)
            if response:
                logger.info(f"*** Group invite sent. status is {response} ***")
                successful_groups.append(group)
        return successful_groups

    def __update_mesh_cycle_data(self):
        """
        Add user email and name in google sheet along with slack user id
        """
        logger.info("*** Updating worksheet data with name and email ***")
        data = self.gss.read_data(self.sheet_title)
        updated_data = []
        for group in data:
            updated_group = []
            for user_id in group:
                user = self.ss.user_info(user_id)
                updated_group.extend([user.slack_id, user.name, user.email])
            updated_data.append(updated_group)
        logger.info(f"*** Updating sheet with name and email ***")
        self.gss.upload_data(updated_data, self.sheet_title)

    def main(self):
        groups = self.__send_invites()
        self.__upload_mesh_groups(groups)
        self.__update_mesh_cycle_data()
