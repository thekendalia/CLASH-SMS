import requests
import time
import os
from repositories import clashuser
from otherpy.send_sms import send_sms
from repositories.db import get_pool

API_TOKEN = os.getenv("CLASH_API")
CLAN_TAG = "%232GLR0J9LQ"  # Replace with your actual clan tag
BASE_URL = f"https://api.clashofclans.com/v1/clans/{CLAN_TAG}/currentwar"

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}


def get_war_status():
    """Fetches the full war status for all clans."""
    war_statuses = {}

    war = clashuser.war_status()
    print(war)
    for clan in war:
        clan_tag = clan[1][1:]  # Remove '#' from tag
        response = requests.get(f"https://api.clashofclans.com/v1/clans/%23{clan_tag}/currentwar", headers=HEADERS)
        print(response)

        if response.status_code == 200:
            war_data = response.json()
            war_statuses[clan_tag] = {
                "state": war_data.get("state", "unknown"),
                "endTime": war_data.get("endTime"),
                "opponent": war_data.get("opponent", {}).get("name"),
                "clan_members": war_data["clan"]["members"]
            }
        else:
            print(f"Error fetching data for {clan_tag}: {response.status_code} - {response.text}")
            war_statuses[clan_tag] = {"state": "error"}

    return war_statuses  # Returns a dictionary with full war data


def send_war_reminder(id, phone, username, attacks):
    """Function triggered when there are 2 hours left in the war."""
    print("Sending war reminder...")
    send_sms(id, phone, username, attacks)
    

import datetime
import time
import requests
from dateutil import parser

import psycopg

def monitor_war():
    pool = get_pool()  # Get the shared connection pool
    while True:
        try:
            with pool.connection() as conn:  # Properly get a connection from the pool
                with conn.cursor() as cursor:
                    war_status = get_war_status()  # Fetch war data for all clans

                    for clan_tag, war_data in war_status.items():
                        if war_data["state"] == "inWar":
                            print(war_data["state"])
                            war_end_time = war_data["endTime"]
                            enemy_name = war_data["opponent"]
                            print(enemy_name)
                            clan_members = war_data["clan_members"]

                            # Store player attacks in a dictionary for faster lookup
                            player_attacks = {player["tag"]: len(player.get("attacks", [])) for player in clan_members}
                            print(player_attacks)
                            
                            war = clashuser.war_status(cursor)  # Pass cursor instead of opening a new connection each time
                            print(war)

                            for player_tag in war:
                                tag = player_tag[2]
                                print(tag)
                                if tag in player_attacks:
                                    attacks_left = player_attacks[tag]
                                    print(True, attacks_left)

                                    war_end_time_dt = parser.isoparse(war_end_time)
                                    current_time = datetime.datetime.now(datetime.timezone.utc)
                                    time_difference = (war_end_time_dt - current_time).total_seconds()

                                    print(time_difference)

                                    if player_tag[5] == enemy_name:
                                        print("Already Alerted!")
                                        continue
                                    elif 0 < time_difference <= 7200 and (attacks_left == 0 or attacks_left == 1):
                                        clashuser.update_enemy_clan(player_tag[0], enemy_name, cursor)
                                        attacks = 2 - attacks_left
                                        send_war_reminder(player_tag[0], player_tag[3], player_tag[4], attacks)

            time.sleep(300)  # Check every 5 minutes

        except Exception as e:
            print(f"Error in war monitoring thread: {e}")
