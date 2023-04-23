from flask import Flask, render_template, request, url_for, redirect, session, flash, send_file
from flask_session import Session
import requests
import msal
from .forms import AuthForm, NewPassForm, UserDetailForm

from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os

CLIENT_ID = "c3ef1c35-98fb-40a0-9850-1467a4e33376"

CLIENT_SECRET = "xyE8Q~1tLAzua6-SIw.zyLAPdZURkgbCVspP8aIM"

AUTHORITY = "https://login.microsoftonline.com/ac2c9531-4944-4cb8-b93b-55801c7b8338"
SCOPE = ["User.ReadBasic.All", "Directory.AccessAsUser.All"]
ENDPOINT_PASS = "https://graph.microsoft.com/v1.0/me/changePassword"
ENDPOINT_USERS = "https://graph.microsoft.com/v1.0/users"


app = Flask(__name__)

app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = CLIENT_SECRET
app.config["RECAPTCHA_PUBLIC_KEY"] = "6LcU_KIlAAAAAA9FPWrCkS5dMet-mNOdJEcaQ8vz"
app.config["RECAPTCHA_PRIVATE_KEY"] = "6LcU_KIlAAAAAI6pngKFafRXszHZR6Z3T4WHd06l"

Session(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/users", methods=["GET", "POST"])
def users():

    form = UserDetailForm()
    if request.method == "POST" and form.validate_on_submit():

        graph_data = requests.get(  # Use token to call downstream service
            f"{ENDPOINT_USERS}/{form.user_email.data}",
            headers={'Authorization': 'Bearer ' + session["access_token"]},
        )

        user = graph_data.json()
        print(graph_data)
        print(user)
        if "error" in graph_data.json():
            flash(graph_data.json()["error"]["message"], "danger")
            return redirect(url_for('users'))
        else:
            document = []
            fn = os.path.join(os.path.dirname(os.path.abspath(
                __file__)), 'static/assets/wme-logo.png')

            document.append(Image(filename=fn, width=1.5*inch,
                            height=1*inch, hAlign="LEFT"))
            document.append(Spacer(1, 40))
            # document.append(Paragraph(
            #     f"First Name: {user['givenName']}", ParagraphStyle(name="name", fontFamily="Helvetica", fontSize=12)))
            # document.append(Spacer(1, 20))
            # document.append(Paragraph(
            #     f"Last Name: {user['surname'].upper()}", ParagraphStyle(name="name", fontFamily="Helvetica", fontSize=12)))
            # document.append(Spacer(1, 20))
            # document.append(Paragraph(
            #     f"Email Address: {user['userPrincipalName']}", ParagraphStyle(name="name", fontFamily="Helvetica", fontSize=12)))
            # document.append(Spacer(1, 20))
            # document.append(Paragraph(
            #     f"Password: {form.user_password.data}", ParagraphStyle(name="name", fontFamily="Helvetica", fontSize=12)))

            data_table = [
                ["Firstname", "John John"],
                ["Lastname", "LLAVE"],
                ["Email Address", "john.llave@jeorginallave.online"],
                ["Password", "Hs19&1Znk"]
            ]

            table = Table(data_table, colWidths=3*inch, hAlign="LEFT")

            document.append(table)

            pdf_location = fn = os.path.join(os.path.dirname(os.path.abspath(
                __file__)), 'static/pdf/')
            SimpleDocTemplate(f"{pdf_location}{user['displayName']}.pdf", pagesize=A4,
                              rightMargin=0.5*inch, leftMargin=0.5*inch, bottomMargin=0.5*inch, topMargin=0.5*inch).build(document)
            flash(
                f"User details for {user['displayName']} was generated", "info")
            return send_file(f"{pdf_location}{user['displayName']}.pdf", as_attachment=True)

    return render_template('userdetails.html', form=form)


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
        try:
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
        except ValueError:
            flash("Invalid username and password/ using public domain")
            return redirect(url_for("auth"))

    else:
        if form.errors:
            for errors in form.errors["recaptcha"]:
                flash(errors)
        if "user" in session:
            return redirect(url_for("newpass"))
        return render_template("auth.html", form=form)


@app.route("/newpass", methods=["GET", "POST"])
def newpass():

    form = NewPassForm()
    if request.method == "POST" and form.validate_on_submit():

        new_pass = form.new_pass.data

        graph_data = requests.post(
            ENDPOINT_PASS,
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
