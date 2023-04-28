
from flask import Flask, render_template, request, url_for, redirect, session, flash, send_file
from flask_session import Session
import requests
import msal
from .forms import AuthForm, ChangePassForm, UserDetailForm
from app.decorators import login_required


from ldap3 import Server, Connection, ALL, NTLM, ALL_ATTRIBUTES
import json

from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
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


@app.route("/auth", methods=["GET", "POST"])
def auth():
    form = AuthForm()

    if request.method == "POST" and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        redirect_page = request.form.get('redirect')

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

                if redirect_page:
                    return redirect(redirect_page)
                return redirect(url_for("index"))
            else:
                flash("Invalid username and password", "danger")
                print("Error logging in to graph API")
                return redirect(url_for("auth"))
        except ValueError:
            flash("Invalid username and password/ using public domain", "danger")
            return redirect(url_for("auth"))

    else:
        if form.errors:
            for error in form.errors:
                flash(form.errors[error][0], "danger")
        if "user" in session:
            return redirect(url_for("index"))
        return render_template("auth.html", form=form)


@app.route("/users", methods=["GET", "POST"])
def users():

    form = UserDetailForm()
    if request.method == "POST" and form.validate_on_submit():

        # graph_data = requests.get(  # Use token to call downstream service
        #     f"{ENDPOINT_USERS}/{form.user_email.data}",
        #     headers={'Authorization': 'Bearer ' + session["access_token"]},
        # )

        server = Server('192.168.0.154', get_info=ALL)
        conn = Connection(server, user="jorgie\\administrator",
                          password="Wme.ae123", auto_bind=True)

        conn.search('dc=jorgie,dc=local',
                    f'(mail={form.user_email.data})', attributes=ALL_ATTRIBUTES)
        result = json.loads(conn.response_to_json())

        if len(result["entries"]) == 0:
            flash(f"User account details does not exists - {form.user_email.data}", "danger")
            return redirect(url_for("users"))

        first_name = result["entries"][0]["attributes"]["givenName"]
        last_name = result["entries"][0]["attributes"]["sn"]
        full_name = result["entries"][0]["attributes"]["displayName"]
        wme_email = result["entries"][0]["attributes"]["mail"]
        username = result["entries"][0]["attributes"]["sAMAccountName"]
        egis_email = wme_email.split("@")[0] + "@egis-group.com"

        # if "error" in graph_data.json():
        #     flash(graph_data.json()["error"]["message"], "danger")
        #     return redirect(url_for('users'))
        # else:
        document = []
        fn = os.path.join(os.path.dirname(os.path.abspath(
            __file__)), 'static/assets/wme-logo.png')

        data_table_account = [
            [Paragraph("<b><font color='#616161'>USER DETAIL</font></b>")],
            ["EMPLOYEE ID", ""],
            ["EMPLOYEE NAME", f"{last_name.upper()} {first_name}"],
            ["WME EMAIL", wme_email],
            ["EGIS EMAIL", egis_email],
            ["PASSWORD", form.user_password.data],
            ["USERNAME/ PC LOGIN", username],
        ]

        data_table_links = [
            [Paragraph("<b><font color='#616161'>USEFUL LINKS</font></b>")],
            ["WEBMAIL", "https://outlook.office.com/mail"],
            ["EGIS INTRANET", "https://myegis.egis.fr"],
            ["WEB TIMESHEET URL", "https://suivi-activite.egis.fr/eTime/#/Home"],
            ["EGIS EXTRANET URL (FOR VPN)", "https://extranet.egis.fr"],
            ["SERVICENOW IT HELPDESK", "https://egisgroup.service-now.com"],
            ["WME IT HELPDESK", "https://helpdesk.wmeglobal.com"],
            ["PASSWORD CHANGE URL", "https://mypassword.egis.fr"]

        ]

        data_table_notes = [
            [Paragraph("<b><font color='#616161'>PROTECTING PASSWORDS</font></b>")],
            [Paragraph("<font color='#616161'><bullet>&bull;</bullet>Users may never share their passwords with anyone else in the company, inlcuding co-workers, managers, administrative assistants, IT staff members, etc.</font>")],
            [Paragraph("<font color='#616161'><bullet>&bull;</bullet>Users may never share their passwords with any outside parties, including those claiming to be representatives of business partner with a legitimate need to access a system.</font>")],
            [Paragraph("<font color='#616161'><bullet>&bull;</bullet>Users must refrain from writing passwords down and keeping them at their workstations.</font>")],
            [Paragraph("<font color='#616161'><bullet>&bull;</bullet>Users may not use password manages or other tools to help store and remember passwords without IT's permission.</font>")]
        ]

        style_account = TableStyle([
            ('TEXTCOLOR', (0, 1), (-1, -1), '#424242'),
            ('GRID', (1, 1), (-1, -1), 0.5, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, 0), "#e0e0e0"),
            ('BACKGROUND', (0, 1), (0, -1), "#eeeeee")])
        table_account = Table(data_table_account,  colWidths=(2.5*inch, 4.5*inch),
                              rowHeights=0.4*inch, hAlign="LEFT", vAlign="MIDDLE")
        table_account.setStyle(style_account)

        table_links = Table(data_table_links,  colWidths=(2.5*inch, 4.5*inch),
                            rowHeights=0.4*inch, hAlign="LEFT", vAlign="MIDDLE")
        style_links = TableStyle([
            ('TEXTCOLOR', (0, 1), (-1, -1), '#424242'),
            ('GRID', (1, 1), (-1, -1), 0.5, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, 0), "#e0e0e0"),
            ('BACKGROUND', (0, 1), (0, -1), "#eeeeee")])
        table_links.setStyle(style_links)

        table_notes = Table(data_table_notes, rowHeights=[
                            0.4*inch, 0.5*inch, 0.5*inch, 0.5*inch, 0.5*inch], colWidths=7*inch, hAlign="LEFT", vAlign="MIDDLE")
        style_notes = TableStyle([
            ('TEXTCOLOR', (0, 1), (-1, -1), '#424242'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, 0), "#e0e0e0"),
            ('BACKGROUND', (0, 1), (0, -1), "#eeeeee")])
        table_notes.setStyle(style_notes)

        document.append(Image(filename=fn, width=1.2*inch,
                              height=0.8*inch, hAlign="LEFT"))
        document.append(Spacer(1, 10))
        document.append(
            Paragraph("<b><font color='#616161'>WME USER ACCOUNT DETAILS</font></b>"))
        document.append(Spacer(1, 20))
        document.append(table_account)
        document.append(Spacer(1, 20))
        document.append(table_links)
        document.append(Spacer(1, 20))
        document.append(table_notes)

        pdf_location = fn = os.path.join(os.path.dirname(os.path.abspath(
            __file__)), 'static/pdf/')
        SimpleDocTemplate(f"{pdf_location}{full_name}.pdf", title=f"{full_name} Account Details", pagesize=A4,
                          rightMargin=0.5*inch, leftMargin=0.5*inch, bottomMargin=0.5*inch, topMargin=0.5*inch).build(document)
        # flash(f"User details for {full_name} was generated", "success")
        return send_file(f"{pdf_location}{full_name}.pdf", as_attachment=True)
    if form.errors:
        for error in form.errors:
            flash(form.errors[error][0], "danger")
    return render_template('userdetails.html', form=form)


@ app.route("/changepass", methods=["GET", "POST"])
@ login_required
def changepass():

    form = ChangePassForm()
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
            flash("You have successfully changed your password", "success")
        else:
            session.clear()
            flash(flash(graph_data.json()["error"]["message"], "danger"))
        return redirect(url_for("index"))

    if form.errors:
        for errors in form.errors["new_pass"]:
            flash(errors, "danger")

    return render_template("changepass.html",  user=session["user"], form=form)


if __name__ == "__main__":
    app.run(debug=True)
