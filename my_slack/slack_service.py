from dataclasses import dataclass

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from my_logger import my_logger
from settings import SLACK_BOT_TOKEN, SLACK_LETS_MEET_ID

logger = my_logger(__name__)


@dataclass
class SlackUser:
    slack_id: str
    name: str
    email: str


class SlackService:
    def __init__(self):
        self.client = WebClient(token=SLACK_BOT_TOKEN)
        self.channel_id = SLACK_LETS_MEET_ID

    def get_users(self, channel_id=SLACK_LETS_MEET_ID):
        try:
            response = self.client.conversations_members(channel=channel_id)
            if response["ok"]:
                return response["members"]
            logger.error(f"Error retreiving users")
        except SlackApiError as e:
            logger.error(f"Error retreiving users: {e}")
        return []

    def __get_or_create_private_group(self, users=[]):
        if len(users) < 2:
            return False
        try:
            response = self.client.conversations_open(users=",".join(users))
            if response["ok"]:
                return response['channel']
            logger.error(f"Error retreiving users")
        except SlackApiError as e:
            logger.error(f"Error creating conversation: {e}")

        return False

    def __post_message(self, channel_id, message=""):
        try:
            response = self.client.chat_postMessage(
                channel=channel_id,
                text=message
            )
            if response["ok"]:
                return "ok"
            logger.error(f"Error posting a message")
        except SlackApiError as e:
            logger.error(f"Error posting a message: {e}")

        return False

    def send_message(self, users=[], message=""):
        if (len(users) < 2 or len(message) < 1):
            return False

        channel = self.__get_or_create_private_group(users)
        if(not channel):
            return False

        return self.__post_message(channel["id"], message)

    def user_info(self, user_id):
        if not user_id:
            logger.warning("Invalid user id")
            return False
        logger.info(f"Reading user data from slack: {user_id}")
        try:
            response = self.client.users_info(user=user_id)
            if response["ok"]:
                user = response['user']
                slack_id, name = user["id"], user["real_name"]
                email = user["profile"]["email"]
                return SlackUser(slack_id, name, email)
            else:
                logger.error(f"Error fetching user info: {response}")
                return False
        except SlackApiError as e:
            logger.error(f"Error fetching user info: {e}")
