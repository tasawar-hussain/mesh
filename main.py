"""
File with entry point to the application
"""

import logging
import sys

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
    send_invites(group_indexes, contacts)


if __name__ == "__main__":
    main(sys.argv[1:])
