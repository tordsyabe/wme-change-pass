from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_session import Session
import requests
import msal

CLIENT_ID = "c3ef1c35-98fb-40a0-9850-1467a4e33376"

CLIENT_SECRET = "xyE8Q~1tLAzua6-SIw.zyLAPdZURkgbCVspP8aIM"

AUTHORITY = "https://login.microsoftonline.com/ac2c9531-4944-4cb8-b93b-55801c7b8338"
SCOPE = ["User.ReadBasic.All", "Directory.AccessAsUser.All"]
ENDPOINT = "https://graph.microsoft.com/v1.0/me/changePassword"

app = Flask(__name__)

app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = CLIENT_SECRET

Session(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/logon", methods=["GET", "POST"])
def logon():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        msal_app = msal.ClientApplication(
            client_id=CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
        )

        result = None
        # account_in_cache = msal_app.get_accounts(username=email)

        # if account_in_cache:
        #     result = msal_app.acquire_token_silent(scopes=SCOPE,account=account_in_cache[0])

        # if not result:
        result = msal_app.acquire_token_by_username_password(
            username=email, password=password, scopes=SCOPE)
        if "access_token" in result:
            session["access_token"] = result["access_token"]
            session["password"] = password
            session["user"] = result.get("id_token_claims")
            return redirect(url_for("newpass"))
        else:
            flash("Invalid username and password")
            print("Error logging in to graph API")
            return redirect(url_for("logon"))
    else:
        if "user" in session:
            return redirect(url_for("newpass"))
        return render_template("logon.html")


@app.route("/newpass", methods=["GET", "POST"])
def newpass():
    if request.method == "POST":

        new_pass = request.form["newpass"]
        graph_data = requests.post(
            ENDPOINT,
            json={
                "currentPassword": session["password"], "newPassword": new_pass},
            headers={'Authorization': 'Bearer ' + session["access_token"], 'Content-Type': 'application/json'})
        print(graph_data)
        if graph_data.status_code == 204:
            session.clear()
            flash("You have successfully changed your password")
        else:
            session.clear()
            flash("Something went wrong please try again")
        return redirect(url_for("index"))

    else:
        if "user" in session:

            return render_template("newpass.html",  user=session["user"])
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
