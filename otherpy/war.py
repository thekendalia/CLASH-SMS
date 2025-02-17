import requests
import time
import os
from repositories import clashuser
from otherpy.send_sms import send_sms

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

def monitor_war():
    """Monitors the war status in a background thread."""
    while True:
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
                war = clashuser.war_status()
                print(war)
                # Match player tags
                for player_tag in war:
                    tag = player_tag[2]  # Extract the tag from the list/dictionary
                    print(tag)  # Prints the tag being checked
                    if tag in player_attacks:  # Check if the tag exists in the dictionary
                        attacks_left = player_attacks[tag]  # Get the number of attacks left
                        print(True, attacks_left)
                        war_end_time_dt = parser.isoparse(war_end_time)
                        current_time = datetime.datetime.now(datetime.timezone.utc)
                        time_difference = (war_end_time_dt - current_time).total_seconds()

                        print(time_difference)

                # If 2 hours (7200 seconds) left, send a reminder
                        if player_tag[5] == enemy_name:
                            print("Already Alerted!")
                            continue
                        elif 0 < time_difference <= 7200 and attacks_left > 0:
                            clashuser.update_enemy_clan(player_tag[0], enemy_name)
                            send_war_reminder(player_tag[0],player_tag[3],player_tag[4], attacks_left)

        time.sleep(120)  # Check every minute
