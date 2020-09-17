"""
Utility functions
"""

import datetime
import json
import logging
import random
from itertools import combinations
from collections import deque
from pathlib import Path

import requests
import uncurl
from faker import Faker

from google_sheet_service import GoogleSheetService
from my_logger import my_logger
from gspread.exceptions import APIError
from sendgrid_service import SendgridService
from settings import (CURL_COMMAND_FILE_PATH, DEFAULT_HEADERS, GROUP_COUNT, IS_DEBUG,
                      TEST_WORKSHEET_TITLE, TOTAL_CONTACTS, WORKSHEET_TITLE)

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
    prased_curl = {}
    if curl_str:
        try:
            context = uncurl.parse_context(curl_str)
        except:
            print("Invalid curl string")
            return prased_curl
        cookies = dict(context.cookies)
        url = context.url
        headers = dict(context.headers)
        data = context.data
        cookies_list = [f"{k}={v}" for k, v in cookies.items()]
        cookies_str = "; ".join(cookies_list)
        headers['cookie'] = cookies_str
        data = json.loads(data)
        data['count'] = TOTAL_CONTACTS
        prased_curl["url"] = url
        prased_curl['headers'] = headers
        prased_curl['data'] = data
    return prased_curl


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
        return create_test_contacts_data(4)


    slack_contacts_request_config = create_request_config()
    if not slack_contacts_request_config:
        return None

    return get_slack_contacts(slack_contacts_request_config)

    # slack_contacts = get_slack_contacts(slack_contacts_request_config)
    #upload_slack_contacts_on_google_sheet(slack_contacts)

    # if IS_DEBUG:
    #     slack_contacts = gss.read_data(TEST_WORKSHEET_TITLE)
    #     if (len(slack_contacts) < 2):
    #         data = create_test_data()
    #         data.insert(0, DEFAULT_HEADERS)
    #         gss.upload_data(data, TEST_WORKSHEET_TITLE)
    #         slack_contacts = gss.read_data(TEST_WORKSHEET_TITLE)
    #         return slack_contacts[1:]
    # else:
    #     slack_contacts = gss.read_data(WORKSHEET_TITLE)

    # return slack_contacts[1:]  # Skip headers


def create_test_contacts_data(count=5):
    test_contacts = []
    for x in range(count):
        test_contacts.append(["user{}".format(x) , "user{}@yopmail.com".format(x)])
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


def upload_slack_contacts_on_google_sheet(slack_contacts):
    slack_contacts.insert(0, DEFAULT_HEADERS)
    gss = GoogleSheetService()
    gss.upload_data(slack_contacts, WORKSHEET_TITLE)


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
    #if remainder == 0 or remainder > 1:
    #     return group_indexes
    # elif remainder == 1:
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
    print(contact_indexes)
    if total_contacts_count <= group_count:
        return contact_indexes
    # suffling indexes
    random.shuffle(contact_indexes)
    group_indexes = list(chunks(contact_indexes, group_count))
    print(group_indexes)
    group_indexes = optimize_groups(total_contacts_count, group_count, group_indexes)
    print(group_indexes)
    return group_indexes


def create_group(count):
    """
    [0, 1, 2]
    returns {2: [0, 1], 1: [0, 2], 0: [1, 2]}
    """
    if (count > 1):
        res = {}
        d = deque(range(count))
        for i in range(len(d)):
            res[list(d)[0]] = list(d)[1:]
            d.rotate(-1)
        return res
    else:
        return {}


def form_group(group):
    """
    craete data required to send email
    """
    count = len(group) # 3
    pairs = create_group(count)
    # count = len(group)  # 3
    # pairs = get_pairs(count)
    group_data = []

    for pair in pairs.items():
        data = {}
        item = pair[1]
        for index, val in enumerate(item):
            data[f"group{index}"] = {
                "name": group[val][0],
                "email": group[val][1]
            }
        partcipant_email = group[pair[0]][1]
        group_data.append({"email": partcipant_email, "members": data})
    return group_data


def send_invites(chunks_idxs, contacts):
    """
    Send email to particpants given the list of contacts and groups
    """
    sent_emails = []
    groups = []
    sg_service = SendgridService()
    for chunk in chunks_idxs:
        gp = [contacts[idx] for idx in chunk]
        group_data = form_group(gp)
        for contact in group_data:
            print(f"\nsending email to: {contact['email']}")
            resp = sg_service.send_email(contact["members"], contact["email"])
            if resp and resp.status_code >= 200 and resp.status_code < 300:
                for member in gp:
                    if member[1] == contact['email']:
                        member.append(True)
                        break
            else:
                print(f"Error sending email to {contact['email']}")

        groups.append(gp)
    return groups

# def send_invites(chunks_idxs, contacts):
#     """
#     Send email to particpants given the list of contacts and groups
#     """
#     sent_emails = []
#     groups = []
#     sg_service = SendgridService()
#     for chunk in chunks_idxs:
#         gp = [contacts[idx] for idx in chunk]
#         group_data = form_group(gp)
#         for contact in group_data:
#             # pass
#             resp = sg_service.send_email(contact["members"], contact["email"])
#             if resp != -1 and resp.status_code >= 200:
#                 sent_emails.append(contact["email"])
#         groups.append(gp)
#     return (groups, sent_emails)


test_email = lambda n: f"tasawarhussain{n}@yopmail.com"


def create_test_data(count=10):
    fake.seed_instance(datetime.datetime.now())
    data = []
    for i in range(1, count):
        contact = [fake.name(), test_email(i)]
        data.append(contact)
    return data
