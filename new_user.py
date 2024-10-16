import pyotp
import qrcode
import json

users = json.load(open("users.json")) or []

name = input("Enter new user: ")

for user in users:
    if user.get("name") == name:
        totp = pyotp.TOTP(user["key"])
        print("Enter the code: ", totp.now())
        break
else:
    key = pyotp.random_base32()
    url = pyotp.totp.TOTP(key).provisioning_uri(name=name)
    users.append({"name": name, "key": key})
    json.dump(users, open("users.json", "w"))
    qrcode.make(url).save(f"{name}.png")
