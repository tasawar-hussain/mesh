"""
File with entry point to the application
"""

import logging
import sys

from settings import CURL_FILE_PATH
from utils import get_contacts, groupize, send_invites


def main(_argv):
    """
    Driver function
    """
    contacts = get_contacts()
    contacts_count = len(contacts)

    if contacts_count < 1:
        logging.error("no contacts found")
        return

    chunks_idxs = groupize(contacts_count)
    groups_data = send_invites(chunks_idxs, contacts)
    print("group data", groups_data)


if __name__ == "__main__":
    main(sys.argv[1:])
