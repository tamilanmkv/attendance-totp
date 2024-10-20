import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime


def mark_attendance(name):
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
    for i, record in enumerate(records, start=2):
        if record["Name"] == name and record["Date"] == current_date:
            if record["Exit Time"] == "":
                sheet.update_cell(i, 4, current_time)
                print(f"Exit time marked for {name} at {current_time}")
            else:
                print(f"Exit time already marked for {name} today.")
            return

    new_row = [name, current_date, current_time, ""]
    sheet.append_row(new_row)
    print(f"Entry time marked for {name} at {current_time}")
