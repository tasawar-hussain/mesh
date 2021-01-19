"""
File with entry point to the application
"""

import sys

from my_logger import my_logger
from my_slack.slack_bot import SlackBot

logger = my_logger(__name__)


# from utils import create_random_groups, get_contacts, send_invites


def main(_argv):
    """
    Driver function
    """
    logger.info("******** Main function ************")
    sb = SlackBot()
    sb.main()
    logger.info("******** Done ************")

    # contacts = get_contacts()
    # print("*** All Contacts ***")
    # print(contacts)
    # print(len(contacts))

    # if not contacts:
    #     logging.error("no contacts available")
    #     return

    # group_indexes = create_random_groups(len(contacts))

    # # IMP: update MESH_CYCLE_WORKSHEET_TITLE in .env and uncomment line below and then run service.
    # send_invites(group_indexes, contacts)


if __name__ == "__main__":
    main(sys.argv[1:])
