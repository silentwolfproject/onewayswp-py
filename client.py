from onewayswp import Client
import time

client = Client()
client.public_key = "OWSWP-pub-002M6NcBGL8viFX2eQ3ur5JHNUbSc5jedBbnWS_BSGs"


if not client.is_active():
    token = input("Masukan token: ")
    info = client.validate_key(token)
    if info["status"]:
        print(info)
    else:
        print(info)
        exit()

verify = client.protection_verify()
if verify["status"]:
    if verify["type"] == "duration":
        remaining_sec = verify["remaining_hours"] * 3600
        print(f"Remaining: {remaining_sec:.0f} seconds")
    elif verify["type"] == "credit":
        print(f"Remaining credits: {verify['remaining_credits']}")
    elif verify["type"] == "date":
        print(f"Expires: {verify['expired']}")
        print(f"Remaining days: {verify['remaining_days']}")