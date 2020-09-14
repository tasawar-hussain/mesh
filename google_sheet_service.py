import datetime

import gspread
from settings import GOOGLE_KEY_PATH, SHEET_ID, WORKSHEET_ID, WORKSHEET_TITLE


class GoogleSheetService:
    def __init__(self):
        gc = gspread.service_account(filename=GOOGLE_KEY_PATH)
        sheet = gc.open_by_key(SHEET_ID)
        worksheet = sheet.worksheet(WORKSHEET_TITLE)
        if not worksheet:
            worksheet = sheet.get_worksheet(0)
        self.__sheet = sheet
        self.__worksheet = worksheet

    def get_worksheet_by_title(self, title=WORKSHEET_TITLE):
        return self.get_sheet().worksheet(title)

    def get_sheet(self):
        return self.__sheet

    def get_worksheet(self):
        return self.__worksheet

    def set_worksheet(self, title):
        self.__worksheet = self.get_worksheet_by_title(title)

    def get_worksheet_id(self, title=WORKSHEET_TITLE):
        worksheet_list = self.get_sheet().worksheets()
        worksheet = [x for x in worksheet_list if x.title == title]
        if worksheet:
            worksheet = worksheet[0]
        else:
            worksheet = worksheet_list[0]
        return worksheet.id

    def upload_contacts_to_sheet(self, contacts):
        worksheet = self.get_worksheet()
        worksheet.update('A1:B1', [['Slack Name', 'Arbisoft Email']])
        worksheet.format('A1:B1', {'textFormat': {'bold': True}})
        count = len(contacts) + 1  # One more for headers
        sheet_range = f"A2:B{count}"
        worksheet.update(sheet_range, contacts)

    def read_contacts_from_sheet(self):
        return self.__worksheet.get_all_values()

    def create_worksheet(self, title, rows=100, cols=10):
        if not title:
            title = str(datetime.datetime.now().timestamp())
        return self.get_sheet().add_worksheet(title=title,
                                              rows=rows,
                                              cols=cols)
