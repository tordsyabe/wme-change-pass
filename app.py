from ldap3 import Server, Connection, ALL, NTLM, ALL_ATTRIBUTES
import json

from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import os


server = Server('192.168.0.153', get_info=ALL)
conn = Connection(server, user="jorgie\\administrator",
                  password="Wme.ae123", auto_bind=True)

conn.search('dc=jorgie,dc=local',
            f'(mail=jessa@jeorginallave.online)', attributes=ALL_ATTRIBUTES)
result = json.loads(conn.response_to_json())
print(result["entries"][0]["attributes"]["displayName"])

first_name = result["entries"][0]["attributes"]["givenName"]
last_name = result["entries"][0]["attributes"]["sn"]
full_name = result["entries"][0]["attributes"]["displayName"]
email = result["entries"][0]["attributes"]["mail"]
username = result["entries"][0]["attributes"]["sAMAccountName"]

# if "error" in graph_data.json():
#     flash(graph_data.json()["error"]["message"], "danger")
#     return redirect(url_for('users'))
# else:
document = []
fn = os.path.join(os.path.dirname(os.path.abspath(
    __file__)), 'app/static/assets/wme-logo.png')


data_table_account = [
    ["USER DETAILS"],
    ["EMPLOYEE ID", ""],
    ["EMPLOYEE NAME", f"{last_name.upper()} {first_name}"],
    ["EMAIL ADDRESS", email],
    ["PASSWORD", "thisispassword"],
    ["USERNAME/ PC LOGIN", username],
]

data_table_links = [
    ["USEFUL LINKS"],
    [Paragraph("WEBMAIL URL", style=ParagraphStyle(name="align_center",
               hAlign=TA_CENTER)), "https://outlook.office.com/mail/"],
    ["EGIS INTRANET", "https://myegis.egis.fr"],
    ["WEB TIMESHEET URL", "https://suivi-activite.egis.fr/eTime/#/Home"],
    ["EGIS EXTRANET URL (FOR VPN)", "https://extranet.egis.fr"],
    ["SERVICENOW IT HELPDESK", "https://egisgroup.service-now.com"],
    ["PASSWORD CHANGE URL", "https://mypassword.egis.fr"]

]

data_table_notes = [
    [Paragraph("PROTECTING PASSWORDS")],
    [Paragraph(" - Users may never share their passwords with anyone else in the company, inlcuding co-workers, managers, administrative assistants, IT staff members, etc.")],
    [Paragraph(" - Users may never share their passwords with any outside parties, including those claiming to be representatives of business partner with a legitimate need to access a system.")],
    [Paragraph(" - Users must refarin from writing passwords down and keeping them at their workstations.")],
    [Paragraph(" - Users may not use password manages or other tools to help store and remember passwords without IT's permission.")]
]

style_account = TableStyle([
    ('GRID', (1, 1), (-1, -1), 0.5, colors.lightgrey),
    ('BACKGROUND', (0, 0), (-1, 0), "#e0e0e0"),
    ('BACKGROUND', (0, 1), (0, -1), "#eeeeee")])
table_account = Table(data_table_account,  colWidths=(2.5*inch, 4.5*inch),
                      rowHeights=0.4*inch, hAlign="LEFT", vAlign="MIDDLE")
table_account.setStyle(style_account)

table_links = Table(data_table_links,  colWidths=(2.5*inch, 4.5*inch),
                    rowHeights=0.4*inch, hAlign="LEFT", vAlign="MIDDLE")
style_links = TableStyle([
    ('GRID', (1, 1), (-1, -1), 0.5, colors.lightgrey),
    ('BACKGROUND', (0, 0), (-1, 0), "#e0e0e0"),
    ('BACKGROUND', (0, 1), (0, -1), "#eeeeee")])
table_links.setStyle(style_links)

table_notes = Table(data_table_notes, rowHeights=0.4 *
                    inch, colWidths=7*inch, hAlign="LEFT", vAlign="MIDDLE")
style_notes = TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), "#e0e0e0"),
    ('BACKGROUND', (0, 1), (0, -1), "#eeeeee")])
table_notes.setStyle(style_notes)

document.append(Image(filename=fn, width=1.2*inch,
                      height=0.8*inch, hAlign="LEFT"))
document.append(Spacer(1, 10))
document.append(Paragraph("WME USER ACCOUNT DETAILS"))
document.append(Spacer(1, 30))
document.append(table_account)
document.append(Spacer(1, 30))
document.append(table_links)
document.append(Spacer(1, 30))
document.append(table_notes)


pdf_location = fn = os.path.join(os.path.dirname(os.path.abspath(
    __file__)), 'app/static/pdf/')
SimpleDocTemplate(f"{pdf_location}{full_name}.pdf", pagesize=A4,
                  rightMargin=0.5*inch, leftMargin=0.5*inch, bottomMargin=0.8*inch, topMargin=0.8*inch).build(document)
