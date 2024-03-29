from datetime import datetime

import gspread
from gspread.exceptions import APIError

from my_logger import my_logger
from settings import (GOOGLE_KEY_PATH, MESH_CYCLE_WORKSHEET_TITLE,
                      SHEET_DATE_FORMAT, SHEET_ID)

logger = my_logger(__name__)


# TODO: need to refactor definitions and setters and getters.
# TODO: need to make class definitions more generic and adaptable.
class GoogleSheetService:
    def __init__(self):
        gc = gspread.service_account(filename=GOOGLE_KEY_PATH)
        sheet = gc.open_by_key(SHEET_ID)
        cycle_worksheet = sheet.worksheet(MESH_CYCLE_WORKSHEET_TITLE)
        self.__sheet = sheet
        self.__worksheet = cycle_worksheet

    def get_worksheet_by_title(self, title=MESH_CYCLE_WORKSHEET_TITLE):
        return self.get_sheet().worksheet(title)

    def get_sheet(self):
        return self.__sheet

    def get_worksheet(self):
        return self.__worksheet

    def set_worksheet(self, title):
        self.__worksheet = self.get_worksheet_by_title(title)

    def get_worksheet_id(self, title=MESH_CYCLE_WORKSHEET_TITLE):
        worksheet_list = self.get_sheet().worksheets()
        worksheet = [x for x in worksheet_list if x.title == title]
        if worksheet:
            worksheet = worksheet[0]
        else:
            worksheet = worksheet_list[0]
        return worksheet.id

    def upload_data(self, data, worksheet_name):
        worksheet = self.get_worksheet()
        if not worksheet_name:
            logger.error(f"No sheet name given using {worksheet}")
        else:
            self.set_worksheet(worksheet_name)

        worksheet = self.get_worksheet()
        columns_count = len(data[0])
        col_char = chr(ord('A') + columns_count - 1)
        rows_count = len(data)
        sheet_range = f"A1:{col_char}{rows_count}"
        worksheet.update(sheet_range, data)
        # worksheet.format("A1:B1", {'textFormat': {'bold': True}})

    def upload_cycle_data(self, data):
        row_values = []
        for x in data:
            row_values.append(x[0])
            row_values.append(x[1])
        self.__worksheet.append_row(row_values)

    def read_data(self, worksheet_name=None):
        worksheet = self.get_worksheet()
        if not worksheet_name:
            logger.error(f"No sheet name given using {worksheet}")
        else:
            self.set_worksheet(worksheet_name)

        worksheet = self.get_worksheet()
        logger.info(f"reading data from {worksheet}")
        data = self.get_worksheet().get_all_values()
        logger.info(f"{len(data) -1} contacts imported from {worksheet}")
        return data

    def create_worksheet(self, title=None, rows=100, cols=10):
        title = title or datetime.now().strftime(SHEET_DATE_FORMAT)
        logger.info(f"creating worksheet with title: {title}")
        try:
            res = self.get_sheet().add_worksheet(title=title,
                                                 rows=rows,
                                                 cols=cols)
            logger.info(f"Sheet created with title: {res.title}")
            return res
        except APIError as e:
            logger.error(e)
