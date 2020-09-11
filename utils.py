"""
Utility functions
"""

import datetime
import json
import logging
import random
from itertools import combinations
from pathlib import Path

import requests
import uncurl
from faker import Faker

from google_sheet_service import GoogleSheetService
from gspread.exceptions import APIError
from sendgrid_service import SendgridService
from settings import (CURL_FILE_PATH, GROUP_COUNT, IS_DEBUG,
                      TEST_WORKSHEET_TITLE, TOTAL_CONTACTS, WORKSHEET_TITLE)

fake = Faker()


def read_file(file_path=CURL_FILE_PATH):
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
    Given a curl string, parses it and return dictionary conating all request info
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
    Given all the request info, get all the slack conatcts from channel
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
    get all conatcts from slack's lets meet channel
    """
    contacts = []
    curl_data = read_file(CURL_FILE_PATH)
    if not curl_data:
        logging.error("invalid curl command")
        return contacts
    request_config = parse_curl(curl_data)
    if len(request_config) < 3:
        logging.error("invalid curl command")
        return contacts

    contacts = get_slack_contacts(request_config)

    gss = GoogleSheetService()
    gss.set_worksheet(WORKSHEET_TITLE)
    gss.upload_contacts_to_sheet(contacts)
    if IS_DEBUG:
        gss.set_worksheet(TEST_WORKSHEET_TITLE)
        contacts = gss.read_contacts_from_sheet()
        if (len(contacts) < 2):
            create_test_data(gss)
            contacts = gss.read_contacts_from_sheet()
            return contacts[1:]

    contacts = gss.read_contacts_from_sheet()
    return contacts[1:]


def chunks(items, size=3):
    """
    function to make groups of size records
    """

    for i in range(0, len(items), size):
        yield items[i:i + size]


def optimize_groups(size, items, group_count):
    """
    Optimize groups to adjust single item
    """

    remainder = size % group_count
    if remainder == 0 or remainder > 1:
        return items
    elif remainder == 1:
        new_list = items.copy()
        new_list[-1].append(new_list[-2].pop())
        return new_list
    return items


def groupize(count, group_count=GROUP_COUNT):
    """
    Given counts of items and group size,
    returns array of arrays containing random groups
    """

    idx_list = list(range(count))
    if count < 4:
        return idx_list
    # suffling indexes
    random.shuffle(idx_list)
    idxs = list(chunks(idx_list, group_count))
    final = optimize_groups(count, idxs, group_count)
    return final


def get_pairs(count=3):
    items = list(range(count))
    """
    returns {2: (0, 1), 1: (0, 2), 0: (1, 2)}
    """
    pairs = list(combinations(items, 2))
    total = (count * (count - 1)) // 2  # 3
    data = {}
    for pair in pairs:
        val = total - pair[0] - pair[1]
        data[val] = pair
    return data


def form_group(group):
    """
    craete data required to send email
    """
    count = len(group)  # 3
    pairs = get_pairs(count)
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
            # pass
            resp = sg_service.send_email(contact["members"], contact["email"])
            if resp != -1 and resp.status_code >= 200:
                sent_emails.append(contact["email"])
        groups.append(gp)
    return (groups, sent_emails)


test_email = lambda n: f"tasawarhussain{n}@yopmail.com"


def create_test_data(gss):
    fake.seed_instance(datetime.datetime.now())
    n = 1
    count = 5
    base_email = f"tasawarhussain{n}@yopmail.com"
    data = []
    while n <= 5:
        contact = [fake.name(), test_email(n)]
        data.append(contact)
        n += 1
    try:
        gss.create_worksheet(TEST_WORKSHEET_TITLE)
    except APIError as error:
        logging.error(str(error))
    gss.set_worksheet(TEST_WORKSHEET_TITLE)
    gss.upload_contacts_to_sheet(data)
