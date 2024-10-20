from fastapi.templating import Jinja2Templates
from datetime import datetime
from fastapi import FastAPI, Request
from utils import GoogleSheets
import pyotp
import qrcode
import json


app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root(request: Request):
    users = json.load(open("users.json"))
    names = [user.get("name") for user in users]
    return templates.TemplateResponse(request=request, name="index.html", context={"names": names})


@app.get("/new_user")
async def new_user(request: Request):
    data = request.data
    name = data.get("name")

    users = json.load(open("users.json")) or []

    if name not in [user.get("name") for user in users]:
        key = pyotp.random_base32()
        url = pyotp.totp.TOTP(key).provisioning_uri(name=name)

        users.append({"name": name, "key": key})

        json.dump(users, open("users.json", "w"))
        qrcode.make(url).save(f"{name}.png")

    return templates.TemplateResponse(request=request, name="new_user.html")


@app.get("/entry")
def verify(request: Request, name, otp, entry_type="attendance"):
    res = dict()
    users = json.load(open("users.json")) or []

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def response_template(res):
        return templates.TemplateResponse(
            request=request, name="message.html", context=res
        )

    for user in users:
        if user.get("name") == name:
            totp = pyotp.TOTP(user["key"])

            if otp == totp.now():
                gs = GoogleSheets(name, entry_type)
                gs.mark_attendance()

                res["message"] = f"Attendance marked {name} {current_time}"
                res["status"] = True
                return response_template(res)

            else:
                res["message"] = "Invalid OTP"
                res["status"] = False
                return response_template(res)

            break

    res["message"] = "User not found"
    res["status"] = False
    return response_template(res)
