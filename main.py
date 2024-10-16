import gspread
from oauth2client.service_account import ServiceAccountCredentials
from fastapi.templating import Jinja2Templates
from datetime import datetime
from fastapi import FastAPI, Request
import pyotp
import json


app = FastAPI()

templates = Jinja2Templates(directory="templates")


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


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/new_user")
async def new_user(request: Request):
    return templates.TemplateResponse(request=request, name="new_user.html")


@app.get("/entry")
def verify(request: Request, name, otp):
    users = json.load(open("users.json")) or []
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for user in users:
        if user.get("name") == name:
            totp = pyotp.TOTP(user["key"])
            if otp == totp.now():
                mark_attendance(name)
                res = {"message": f"Attendance marked {name} {current_time}"}
                return templates.TemplateResponse(
                    request=request, name="message.html", context=res
                )
            else:
                res = {"message": "Invalid OTP"}
                return templates.TemplateResponse(
                    request=request, name="message.html", context=res
                )
            break
    else:
        res = {"message": "User not found"}
        return templates.TemplateResponse(
            request=request, name="message.html", context=res
        )
