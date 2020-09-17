"""
File with entry point to the application
"""

import logging
import sys

from settings import CURL_COMMAND_FILE_PATH
from utils import get_contacts, create_random_groups, send_invites


def main(_argv):
    """
    Driver function
    """
    contacts = get_contacts()
    print(contacts)
    print(len(contacts))

    if not contacts:
        logging.error("no contacts available")
        return

    group_indexes = create_random_groups(len(contacts))
    #groups_data = send_invites(group_indexes, contacts)
    # print("group data", groups_data)



if __name__ == "__main__":
    main(sys.argv[1:])
