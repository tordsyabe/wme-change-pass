from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_session import Session
import requests
import msal
from .forms import AuthForm, NewPassForm

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
    session.clear()
    return render_template("index.html")


@app.route("/auth", methods=["GET", "POST"])
def auth():
    form = AuthForm()

    if request.method == "POST" and form.validate_on_submit():
        email = form.email.data
        password = form.password.data

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
            return redirect(url_for("auth"))
    else:
        if "user" in session:
            return redirect(url_for("newpass"))
        return render_template("auth.html", form=form)


@app.route("/newpass", methods=["GET", "POST"])
def newpass():

    form = NewPassForm()
    if request.method == "POST" and form.validate_on_submit():

        new_pass = form.new_pass.data
        comfirm = form.confirm_pass.data

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
        if form.errors:
            for errors in form.errors["new_pass"]:
                flash(errors)

        if "user" in session:

            return render_template("newpass.html",  user=session["user"], form=form)
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
