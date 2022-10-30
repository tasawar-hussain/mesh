"""
Utility functions
"""
import json
import logging
import random
from pathlib import Path

import requests
import uncurl
from faker import Faker

from google_sheet_service import GoogleSheetService
from my_logger import my_logger
from sendgrid_service import SendgridService
from settings import (CURL_COMMAND_FILE_PATH, GROUP_COUNT, IS_DEBUG,
                      MESH_CYCLE_WORKSHEET_TITLE, TOTAL_CONTACTS)

logger = my_logger(__name__)
fake = Faker()


def read_file(file_path=CURL_COMMAND_FILE_PATH):
    """
    Read's file from given path and removes line breaks
    """
    txt = ''
    try:
        txt = Path(file_path).read_text()
    except FileNotFoundError:
        print("Invalid file path")
        return -1
    txt = txt.replace('\\', '')
    txt = txt.replace('\n', '')
    return txt


def parse_curl(curl_str):
    """
    Given a curl string, parses it and return dictionary containing all request info
    """
    parsed_curl = {}
    if curl_str:
        try:
            context = uncurl.parse_context(curl_str)
        except:
            print("Invalid curl string")
            return parsed_curl
        cookies = dict(context.cookies)
        url = context.url
        headers = dict(context.headers)
        data = context.data
        cookies_list = [f"{k}={v}" for k, v in cookies.items()]
        cookies_str = "; ".join(cookies_list)
        headers['cookie'] = cookies_str
        data = json.loads(data)
        data['count'] = TOTAL_CONTACTS
        parsed_curl["url"] = url
        parsed_curl['headers'] = headers
        parsed_curl['data'] = data
    return parsed_curl


def get_slack_contacts(request_config):
    """
    Given all the request info, get all the slack contacts from channel
    """
    contacts = []
    if request_config:
        url = request_config['url']
        data = request_config['data']
        headers = request_config['headers']
        response = requests.post(url, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            users = response.json()
            if users['ok'] and 'results' in users and 'errors' not in users:
                users = users['results']
                for user in users:
                    profile = user['profile']
                    name = profile['real_name_normalized']
                    email = profile['email']
                    contacts.append([name, email])
            else:
                logging.error("error", users)
        else:
            logging.error("invalid response from slack api")

    return contacts


def get_contacts():
    """
    get all contacts from slack's lets meet channel
    """

    if IS_DEBUG:
        return create_test_contacts_data()

    slack_contacts_request_config = create_request_config()
    if not slack_contacts_request_config:
        return None

    return get_slack_contacts(slack_contacts_request_config)


def create_test_contacts_data(count=5):
    test_contacts = []
    username = "mesh_user_"
    for x in range(count):
        test_contacts.append([f"{username}{x}", f"{username}{x}@yopmail.com"])

    test_contacts.append(["Wjia", "wajeeha.khalid@arbisoft.com"])
    test_contacts.append(["Jia", "jia.khalid7@gmail.com"])
    return test_contacts


def create_request_config():
    curl_command = read_file(CURL_COMMAND_FILE_PATH)
    if not curl_command:
        logging.error("invalid curl command")
        return None
    slack_contacts_request_config = parse_curl(curl_command)
    if len(slack_contacts_request_config) < 3:
        logging.error("invalid curl command")
        return None
    return slack_contacts_request_config


def chunks(items, size=3):
    """
    returns list of sublists with size
    """
    for i in range(0, len(items), size):
        yield items[i:i + size]


def optimize_groups(total_contacts_count, group_count, group_indexes):
    """
    Optimize groups to adjust last (one member) group
    """
    remainder = total_contacts_count % group_count
    if remainder == 1:
        new_list = group_indexes.copy()
        new_list[-1].append(new_list[-2].pop())
        return new_list
    return group_indexes


def create_random_groups(total_contacts_count, group_count=GROUP_COUNT):
    """
    Given counts of items and group size,
    returns array of arrays containing random groups
    """
    contact_indexes = list(range(total_contacts_count))
    print("*** Random Contacts Indexes ***")
    print(contact_indexes)

    if total_contacts_count <= group_count:
        return [contact_indexes]

    # shuffling indexes
    random.shuffle(contact_indexes)
    group_indexes = list(chunks(contact_indexes, group_count))
    print("*** Random Group Indexes ***")
    print(group_indexes)

    group_indexes = optimize_groups(
        total_contacts_count, group_count, group_indexes)
    print("*** Random Group Indexes with Adjustment***")
    print(group_indexes)

    return group_indexes


def random_groups(contacts):
    group_indexes = create_random_groups(len(contacts))
    groups = [[contacts[idx] for idx in gi] for gi in group_indexes]
    return groups


def create_email_template_data(mesh_group):
    recipients_emails = []
    recipients_names = []
    for contact in mesh_group:
        recipients_emails.append((contact[1], contact[0]))
        recipients_names.append(contact[0])

    return recipients_names, recipients_emails


def send_invites(group_indexes, contacts):
    """
    Send email to particpants given the list of contacts and groups
    """
    groups = []
    sg_service = SendgridService()
    gss = GoogleSheetService()

    print("*** Mesh cycle is {} ***".format(MESH_CYCLE_WORKSHEET_TITLE))
    for group_index in group_indexes:
        mesh_group = [contacts[idx] for idx in group_index]
        print("*** Mesh Group ***")
        print(mesh_group)

        group_members_names, group_members_emails = create_email_template_data(
            mesh_group)
        response = sg_service.send_email_to_group(
            group_members_names, group_members_emails)
        print("*** email sent status is {} ***".format(response.status_code))

        print("*** Uploading this mesh group on google sheet ***")
        gss.upload_cycle_data(mesh_group)

        groups.append(mesh_group)
    return groups
