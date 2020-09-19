"""
Constants used in application
"""
import os

from dotenv import load_dotenv

load_dotenv(verbose=True)

TOTAL_CONTACTS = int(os.getenv("TOTAL_CONTACTS"))
GROUP_COUNT = int(os.getenv("GROUP_COUNT"))
IS_DEBUG = True if int(os.getenv("IS_DEBUG")) else False
SG_SANDBOX_MODE = True if int(os.getenv("SG_SANDBOX_MODE")) else False

CURL_COMMAND_FILE_PATH = os.getenv("CURL_FILE_PATH")

GOOGLE_KEY_PATH = os.getenv("GOOGLE_KEY_PATH")

SHEET_ID = os.getenv("SHEET_ID")

MESH_CYCLE_WORKSHEET_TITLE = os.getenv("MESH_CYCLE_WORKSHEET_TITLE")

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
TEMPLATE_ID = os.getenv("TEMPLATE_ID")
FROM_EMAIL = os.getenv("FROM_EMAIL")

DEFAULT_HEADERS = ['Slack Name', 'Arbisoft Email']
