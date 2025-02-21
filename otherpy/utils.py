import time
import os
from dotenv import load_dotenv
import requests
import bcrypt
from flask import (
    render_template,
    Flask,
    request,
    flash,
    url_for,
    redirect,
    jsonify,
    session,
    json,
)
import random
import schedule
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("secretkey")

API_TOKEN = os.getenv("CLASH_API")
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
}

url1 = f"https://api.clashofclans.com/v1/clans/%23GYPU2PVV/members"


member_names = []

def count():
    sum = 0
    member_names.clear()  # Reset the list before adding new names
    response = requests.get(url1, headers=headers)
    if response.status_code == 200:
        clan_info = response.json()
        for member in clan_info.get("items", []):
            member_names.append(member["name"])
            sum += 1  # Cleaner way to increment
    print(sum)
    return sum
