import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime


class GoogleSheets:
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "maximal-airfoil-379810-dbff4a26ee65.json", scope
    )

    client = gspread.authorize(creds)

    sheet = client.open_by_key("1pYIriif-iveLxET0wDTl1yNkU93cHM4nT45Mn9sYOYU").sheet1

    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")

    records = sheet.get_all_records()

    def __init__(self, name, entry_type):
        self.name = name
        self.entry_type = entry_type

    def mark_attendance(self):
        if self.entry_type == "attendance":
            self.mark_today_attendance()
        elif self.entry_type == "leave":
            self.mark_today_leave()

    def mark_today_leave(self):
        new_row = [self.name, self.current_date, "leave", "leave"]
        self.sheet.append_row(new_row)

    def mark_today_attendance(self):
        for i, record in enumerate(self.records, start=2):
            if record["Name"] == self.name and record["Date"] == self.current_date:
                if record["Exit Time"] == "":
                    self.sheet.update_cell(i, 4, self.current_time)
                return

        new_row = [self.name, self.current_date, self.current_time, ""]
        self.sheet.append_row(new_row)
