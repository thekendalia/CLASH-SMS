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
from repositories import clashuser
from repositories.clashuser import delete_clash_users
from repositories.clash import get_member_th_level
from flask import Flask
from flask_mail import Mail, Message
from twilio.rest import Client
from datetime import datetime, timedelta
import unittest
from unittest.mock import patch, MagicMock
import threading
from otherpy.bot import bot


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("secretkey")

API_TOKEN = os.getenv("CLASH_API")
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
}

clan_tag = os.getenv("clantag")

url1 = f"https://api.clashofclans.com/v1/clans/{clan_tag}/members"
url2 = f"https://api.clashofclans.com/v1/clans/{clan_tag}/warlog"
url3 = f"https://api.clashofclans.com/v1/clans/{clan_tag}"
url4 = f"https://api.clashofclans.com/v1/clans/{clan_tag}/currentwar"
url5 = f"https://api.clashofclans.com/v1/players/%238G89JLV2C"

member_names = []

members = []
skip = []

my_dict = []
choice = []
isname = []
user = {}

app.config["MAIL_SERVER"] = "live.smtp.mailtrap.io"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USERNAME"] = "api"
app.config["MAIL_PASSWORD"] = "702d490955ca004216a567c9bb56923a"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config['MAIL_DEBUG'] = False

mail = Mail(app)

TOKEN = os.getenv("DISCORD_TOKEN")

def start_discord():
    thread = threading.Thread(target=lambda: bot.run(TOKEN), daemon=True)
    thread.start()

# Start the Discord bot in a separate thread
start_discord()

@app.route("/send")
def send(code, email):
    print(code)
    print(email)
    msg = Message(
        f"{code} Password Reset",
        sender=("Clan War SMS Support", "support@darkroseclan.com"),
        recipients=[f"{email}"],
    )
    msg.html = f"""  
    <html>  
        <body>  
            <p>Here is the code to reset your password:</p>  
            <p><b>{code}</b></p> 
            <img src="cid:image1">  
        </body>  
    </html>"""

    with app.open_resource("static/images/clash.gif") as fp:
        msg.attach(
            "clash.gif", "image/gif", fp.read(), headers={"Content-ID": "<image1>"}
        )
    mail.send(msg)
    return "Message sent!"

 
def submit_data(email, phone_number, terms, tag, clan, name):  

    # Process or validate your data as needed  
    data_to_send = {  
        'email': email,  
        'phone_number': phone_number,  
        'is_active': terms, 
        'clan_tag': tag,
        'clan': clan,
        'name': name
    }  
    print(data_to_send)
    response = send_to_make(data_to_send)  # Call function to send data to Make.com  
    return jsonify(response)  

def send_to_make(data):  
    make_url = "https://hook.us1.make.com/jjqxw5n6htjay3irpqiyc5s8ky9911ej"  # Replace with your actual Make.com webhook URL  
    try:  
        response = requests.post(make_url, json=data)  
        if response.status_code == 200:  
            return {'status': 'success', 'data': data}  
        else:  
            return {'status': 'error', 'message': response.text}  
    except Exception as e:  
        return {'status': 'error', 'message': str(e)}  

if __name__ == '__main__':  
    app.run(debug=True)  


@app.get("/")
def home():
    username = dict(session).get("username", None)
    message = request.args.get("message", "")
    return render_template(
        "home.html",
        no_header=False,
        no_search_bar=True,
        username=username,
        message=message,
    )
    

def count():
    sum = 0
    response = requests.get(url1, headers=headers)
    if response.status_code == 200:
        clan_info = response.json()
        for member in clan_info.get("items", []):
            member_names.append(member["name"])
            sum = sum + 1
    return sum


@app.get("/create")
def create():
    message = request.args.get("message", "")
    sitekey = os.getenv("sitekey")
    return render_template("create.html", message=message, sitekey=sitekey)


@app.get("/passreset")
def passreset():
    message = request.args.get("message", "")
    sitekey = os.getenv("sitekey")
    return render_template("reset.html", message=message, sitekey=sitekey)

@app.route("/sms")
def sms():
    email = dict(session).get("email", None)
    istrue, id, username, cemail, clan_tag, terms, phone, clan = clashuser.user_data(email)
    if email == None:
        return redirect(url_for("home"))
    return render_template("sms.html", terms=terms)

@app.post("/phone")
def phone():
    email = dict(session).get("email", None)
    country = request.form['country']
    phone = request.form['phone']
    number = country + " " + phone
    clashuser.update_phone(email, number)
    istrue, id, username, cemail, clan_tag, terms, phone, clan = clashuser.user_data(email)
    print(phone)
    print(terms)
    submit_data(email, phone, terms, clan_tag, clan, username)
    return redirect(url_for('account'))

@app.route('/error')
def error():
    return render_template('error.html')

@app.route('/gone_fishing')
def maintenance():
    return render_template('maintenance.html')

@app.route('/error_msg')
def error_msg():
    msg = Message(
        f"Error Reported!",
        sender=("Clan War SMS", "support@darkroseclan.com"),
        recipients=[f"kenbazonct14@gmail.com"],
    )
    msg.html = f"""  
    <html>  
        <body>  
            <p>Error message pressed! Check the logs!</p>
            <img src="cid:image1">  
        </body>  
    </html>"""
    mail.send(msg)
    return redirect(url_for('home'))



@app.route("/delete_phone")
def delete_phone():
    email = dict(session).get("email", None)
    istrue, id, username, cemail, clan_tag, terms, phone, clan = clashuser.user_data(email)
    submit_data(email, 0, False, 0, 0, 0)
    clashuser.update_term_status_false(email)
    clashuser.update_phone(email, "0")
    return redirect(url_for('account'))

@app.post("/accept_terms")
def accept_terms():
    email = dict(session).get("email", None)
    terms_accept = request.form.get('terms')
    if terms_accept == None:
        return redirect(url_for('sms'))
    else:
        clashuser.update_term_status_true(email)
    return render_template("sms.html")


@app.post("/forgot_password")
def forgot_password():
    try:
        random_number = random.randint(1000, 9999)
        email = request.form["email"]
        captcha_response = request.form["g-recaptcha-response"]
        email_lower = email.lower()
        check = clashuser.existingemail(email_lower)
        if check and is_human(captcha_response):
            print(random_number)
            print(email)
            session["verify"] = email_lower
            clashuser.update_user_code(random_number, email_lower)
            send(random_number, email)
            return redirect(url_for("code"))
        elif is_human(captcha_response) == False:
            return redirect(
                url_for("passreset", submitted=True, message="You forgot Captcha!")
            )
        else:
            return redirect(
                url_for("passreset", submitted=True, message="Email not registered")
            )
    except Exception as e:
        print(f"Error during login: {e}")  # Log the error for debugging
        return redirect(url_for("error", message="An unexpected error occurred. Please try again."))


def is_human(captcha_response):

    secret = os.getenv("secret")
    payload = {"response": captcha_response, "secret": secret}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", payload)
    response_text = json.loads(response.text)
    return response_text["success"]


@app.get("/login")
def login():
    message = request.args.get("message", "")
    return render_template("login.html", message=message)


@app.get("/cwl")
def index():
    member_names.clear()
    sum = 0
    response = requests.get(url1, headers=headers)
    if response.status_code == 200:
        clan_info = response.json()
        for member in clan_info.get("items", []):
            member_names.append(member["name"])
            sum = sum + 1
    message = request.args.get("message", "")
    # Loads the Home Page.
    if my_dict != None:
        my_dict.clear()
    roseusers = clashuser.get_clash_users()
    print(roseusers)
    first = choice[0] if choice else None
    popname = isname[0] if isname else None
    if choice != None:
        choice.clear()
    if isname != None:
        isname.clear()
    return render_template(
        "index.html",
        member_names=member_names,
        response=first,
        nummems=sum,
        names=popname,
        message=message,
    )


@app.get("/clanstats")
def clanstats():
    try:
        email = dict(session).get("email", None)
        istrue, id, username, cemail, clan_tag, terms, phone, user_clan = clashuser.user_data(email)
        if clan_tag == '0':
            session['tab'] = "clanstats"
            return redirect(url_for("accounttag"))
        clanshort = clan_tag[1:]
        clantag = requests.get(f"https://api.clashofclans.com/v1/players/%23{clanshort}", headers=headers)
        playerdata = clantag.json()
        player_clan = playerdata['clan']['tag'][1:]
        response2 = requests.get(f"https://api.clashofclans.com/v1/clans/%23{player_clan}/warlog", headers=headers)
        response3 = requests.get(f"https://api.clashofclans.com/v1/clans/%23{player_clan}", headers=headers)
        warlog = response2.json()
        clan = response3.json()
        wars = warlog.get("items", [])
        drose = "Dark Rose"
        return render_template("clan_stats.html", drose=drose, wars=wars, clandata=clan)
    except Exception as e:
        print(f"Error during login: {e}")  # Log the error for debugging
        return redirect(url_for("error", message="An unexpected error occurred. Please try again."))


@app.route("/api/member-names")
def get_member_names():
    return jsonify(member_names)


@app.route("/api/member-names")
def get_members():
    return jsonify(members)

@app.route("/accounttag", methods=['GET', 'POST'])
def accounttag():
    try:
        message = request.args.get("message", "")
        if request.method == 'POST':
            email = dict(session).get("email", None)
            tab = dict(session).get("tab", None)
            tag = request.form['tag']
            modifiedtag = tag[1:]
            session['tag'] = modifiedtag
            response4 = requests.get(f"https://api.clashofclans.com/v1/players/%23{modifiedtag}", headers=headers)
            clanwar = response4.json()
            if clanwar.get('reason') == 'notFound':
                return redirect(url_for('accounttag', submitted=True, message="Account not found, try again!"))
            else:
                player_clan = clanwar['clan']['tag']
                if player_clan == None:
                    player_clan = 0
                clashuser.update_clan_tag(tag, email, player_clan)
            print(tab)
            return redirect(url_for(tab))
        return render_template("entertag.html", message=message)
    except Exception as e:
        print(f"Error during login: {e}")  # Log the error for debugging
        return redirect(url_for("error", message="An unexpected error occurred. Please try again."))

@app.get('/users')  
def users():
    email = dict(session).get("email", None)
    if email != "admin@darkrose.com":
        return redirect(url_for("home"))
    users = clashuser.users()  
    filtered_users = [user for user in users if user[1] != "admin"]
    num = len(filtered_users) 
    return render_template("users.html", users=filtered_users, num=num)



@app.get("/account")
def account():
        email = dict(session).get("email", None)
        istrue, id, username, cemail, clan_tag, terms, phone, clan = clashuser.user_data(email)
        if clan_tag == '0':
            session['tab'] = "account"
            return redirect(url_for("accounttag"))
        print(clan_tag)
        tag = clan_tag[1:]
        response4 = requests.get(f"https://api.clashofclans.com/v1/players/%23{tag}", headers=headers)
        clanwar = response4.json()
        player_clan = clanwar['clan']['tag'][1:]
        response4 = requests.get(f"https://api.clashofclans.com/v1/clans/%23{player_clan}/currentwar", headers=headers)
        war_log = response4.json()
        if war_log.get('reason') == 'accessDenied':
            disabled = True
        else:
            disabled = False
        if email == None:
            return redirect(url_for("home"))
        if skip and skip[0] == "Not Set":
            player = "Not Set"
            skip.clear()
            return render_template("account.html", username=username, email=cemail, tag=clan_tag, player=player, terms=terms, phone=phone)
        if clan_tag == "0":
            return redirect(url_for("accounttag"))
        return render_template("account.html", username=username, email=cemail, tag=clan_tag, player=clanwar,terms=terms, phone=phone, disabled=disabled)
    
@app.get("/accountskip")
def accountskip():
    email = dict(session).get("email", None)
    tab = dict(session).get("tab", None)
    skip.append("Not Set")
    if email == None:
        return redirect(url_for("home"))
    return redirect(url_for(tab))

@app.get("/delete")
def delete():
    email = dict(session).get("email", None)
    clashuser.delete_account(email)
    return redirect(url_for("logout"))


@app.get("/admin")
def admin():
    username = dict(session).get("username", None)
    print("User " + username)
    if username == "admin":
        roseusers = clashuser.get_clash_users()

        return render_template(
            "admin.html", rose=roseusers, no_search_bar=True, homeie=True
        )
    else:
        return redirect(url_for("index"))


@app.get("/auth")
def auth():
    name = session["name"]
    opt_choice = session["opt_choice"]
    lvl = get_member_th_level(name)
    response = int(request.args.get("thlvl"))
    if response == lvl:
        if clashuser.check_user_exists(name.lower()):
            return redirect(url_for("index", submitted=True, message="Status Updated"))
        elif opt_choice == "1":
            isin = True
            choice.append("in")
            isname.append(name)
            clashuser.insert_clash_users(name.lower(), isin)
            return redirect(
                url_for("index", submitted=True, message=f"{name} has opted in!")
            )
        elif opt_choice == "2":
            isin = False
            choice.append("out")
            isname.append(name)
            clashuser.insert_clash_users(name.lower(), isin)
            return redirect(
                url_for("index", submitted=True, message=f"{name} has opted out!")
            )
    if response != lvl:
        return redirect(
            url_for("index", submitted=True, message="Security Failed: incorrect TH")
        )


@app.get("/currentwar")
def current_war():
    try: 
        email = dict(session).get("email", None)
        istrue, id, username, cemail, clan_tag, terms, phone, clan = clashuser.user_data(email)
        if clan_tag == '0':
            session['tab'] = "clanstats"
            return redirect(url_for("accounttag"))
        clanshort = clan_tag[1:]
        clantag = requests.get(f"https://api.clashofclans.com/v1/players/%23{clanshort}", headers=headers)
        playerdata = clantag.json()
        player_clan = playerdata['clan']['tag'][1:]
        response4 = requests.get(f"https://api.clashofclans.com/v1/clans/%23{player_clan}/currentwar", headers=headers)
        clanwar = response4.json()
        if clanwar.get('reason') == 'accessDenied':
            return redirect(url_for('home', message="Your clan needs public war logs for this function to work"))
        print(clanwar)
        zero, one, two, three = 0, 0, 0, 0
        oppzero, oppone, opptwo, oppthree = 0, 0, 0, 0
        if clanwar["state"] == "notInWar":
            clan = "notInWar"
            return render_template("current_war.html", clan=clanwar)
        else:
            for member in clanwar["clan"]["members"]:
                if "attacks" in member:
                    for attack in member["attacks"]:
                        stars = attack["stars"]
                        if stars == 0:
                            zero += 1
                        elif stars == 1:
                            one += 1
                        elif stars == 2:
                            two += 1
                        elif stars == 3:
                            three += 1
            for member in clanwar["opponent"]["members"]:
                if "attacks" in member:
                    for attack in member["attacks"]:
                        stars = attack["stars"]
                        if stars == 0:
                            oppzero += 1
                        elif stars == 1:
                            oppone += 1
                        elif stars == 2:
                            opptwo += 1
                        elif stars == 3:
                            oppthree += 1
            members_info = []

            for member in clanwar["clan"]["members"]:
                attacks_left = 2
                if "attacks" in member:
                    attacks_left -= len(member["attacks"])

                new_dict = {
                    "name": member["name"],
                    "position": member.get("mapPosition", float("inf")),
                    "attacks_left": attacks_left,
                }
                members_info.append(new_dict)

            members_info = sorted(members_info, key=lambda x: x["position"])

            return render_template(
                "current_war.html",
                clan=clanwar,
                three=three,
                two=two,
                one=one,
                zero=zero,
                oppzero=oppzero,
                oppone=oppone,
                opptwo=opptwo,
                oppthree=oppthree,
                clanmem=clanwar["clan"],
                members_info=members_info,
            )
    except Exception as e:
        print(f"Error during login: {e}")  # Log the error for debugging
        return redirect(url_for("error", message="An unexpected error occurred. Please try again."))


@app.get("/security_check")
def security_check():
    name = session["name"]
    return render_template("auth.html", name=name)


@app.get("/addhome")
def addhome():
    return render_template("/addhome.html")


@app.post("/adduser")
def adduser():
    session["name"] = request.form["name"]
    session["opt_choice"] = request.form["opt_choice"]
    return redirect(url_for("security_check"))


from flask import request, redirect, url_for, render_template
import bcrypt


@app.post("/createacc")
def create_acc():
    try:
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirmpass = request.form["confirm-password"]
        captcha_response = request.form["g-recaptcha-response"]
        user = username.lower()
        lower_email = email.lower()
        if password != confirmpass:
            return redirect(
                url_for("create", submitted=True, message="Mismatched Password")
            )
        exists = clashuser.existingaccount(user)
        email_exists = clashuser.existingemail(lower_email)
        if exists:
            return redirect(url_for("create", submitted=True, message="Username taken"))
        if email_exists:
            return redirect(
                url_for(
                    "create",
                    submitted=True,
                    message="An account with that email already exists!",
                )
            )
        if is_human(captcha_response) == False:
            return redirect(url_for("create", submitted=True, message="Captcha Failed!"))
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
            "utf-8"
        )
        clashuser.new_account(username, email, hashed_password)

        return redirect(url_for("login"))
    except Exception as e:
        print(f"Error during login: {e}")  # Log the error for debugging
        return redirect(url_for("error", message="An unexpected error occurred. Please try again."))


@app.post("/userlogin")
def userlogin():
    try:
        username = request.form["username"]
        password = request.form["password"]
        user = username.lower()
        print(f"Trying to log in: {user}")
        log, id, user_name, email = clashuser.login_user(user, password)

        if log == False:
            return redirect(url_for("login", submitted=True, message="Incorrect Password"))

        session["username"] = user_name
        session["email"] = email
        return redirect(url_for("home"))

    except Exception as e:
        print(f"Error during login: {e}")  # Log the error for debugging
        return redirect(url_for("error", message="An unexpected error occurred. Please try again."))



@app.post("/adminlogin")
def admin_pass():
    adpass = request.form.get("adminpass")
    setpass = os.getenv("adminpassword")
    if adpass == setpass:
        my_dict.append(1)
        return redirect(url_for("admin"))
    else:
        flash("Wrong Password Homie")

    return redirect(url_for("home"))


@app.post("/delete")
def delete_user():
    entry_id = request.form["entry_id"]
    delete_clash_users(entry_id)
    return redirect(url_for("admin"))


@app.route("/logout")
def logout():
    for key in list(session.keys()):
        session.pop(key)
    flash("You have been logged out.")
    return redirect(url_for("home"))


@app.post("/email")
def email():
    random_number = random.randint(1000, 9999)
    email = request.form["email"]
    captcha_response = request.form["g-recaptcha-response"]
    if is_human(captcha_response):
        message = "Captcha Passed!"
    else:
        message = "Captcha Failed!"
    flash(message)
    email_lower = email.lower()
    check = clashuser.existingemail(email_lower)
    if check:
        print(email_lower)
        session["verify"] = email_lower
        clashuser.update_user_code(random_number, email_lower)
        send(random_number, email)
        return redirect(url_for("code"))
    else:
        return redirect(
            url_for("home", submitted=True, message="No account with that email :(")
        )


@app.get("/code")
def code():
    return render_template("code.html")


@app.post("/code_check")
def code_check():
    code = request.form["code"]
    email = dict(session).get("verify", None)
    check = clashuser.check_code(email)
    print(code)
    print(check)
    if int(code) == int(check):
        return redirect(url_for("newpassword"))
    else:
        return redirect(url_for("home", submitted=True, message="Code incorrect"))


@app.route("/newpassword")
def newpassword():
    return render_template("newpass.html")


@app.post("/update_password")
def update_password():
    password = request.form["password"]
    cpassword = request.form["cpassword"]
    message = request.args.get("message", "")
    if password == cpassword:
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        email = dict(session).get("verify", None)
        clashuser.update_password(hashed_password, email)
        return redirect(
            url_for("home", submitted=True, message="Password has been updated!")
        )
    return redirect(url_for("home", submitted=True, message="Password doesn't match"))


@app.route("/disabled")
def disabled():
    return redirect(url_for("home", message="This function is not ready yet!"))
    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)