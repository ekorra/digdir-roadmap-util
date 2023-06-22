from DigdirRoadmap import *
from json import JSONEncoder
import json
import csv
import argparse
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import io
import pickle

subject = "Email Subject"
body = "This is the body of the text message"
sender = "ekorra@gmail.com"
recipients = ["espen.korra@digdir.no"]
password = "" 

def send_email(subject, body, sender, recipients, password):
    
    with open("test.txt", "rb") as attachment:
        # Add the attachment to the message
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= test.txt",)

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    
    html_part = MIMEText(body)
    msg.attach(html_part)
    msg.attach(part)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")

#  send_email(subject,body, sender, recipients,password)
m = ["lkjadf", "laksdjl"]
with open('test.pickle', 'wb') as handle:
    pickle.dump(m, handle, protocol=pickle.HIGHEST_PROTOCOL)

parser = argparse.ArgumentParser()
parser.add_argument("--file", default="roadmap", type=str,
                    help="filename of generated file")
parser.add_argument("--type", default="screen",
                    choices=["json", "csv", "mail", "screen", "all"], help="json|csv|mail|screen|all")
parser.add_argument("--product", help="name of product in roadmap")
parser.add_argument("--token", required=True,
                    help="Toeken required \"Bearer ghp_AbdcaADF...\"")
parser.add_argument("--save_binary", action=argparse.BooleanOptionalAction)
parser.add_argument("--testrun", action=argparse.BooleanOptionalAction)
parser.set_defaults(testrun=False)
parser.set_defaults(save_binarly=False)
args = parser.parse_args()

authorizationToken = args.token

# roadmapItems = getDigdirRoadmap(authorizationToken)


if args.testrun == False:
    roadmapItems = getDigdirRoadmap(authorizationToken)
    if args.save_binary == True:
        with open('roadmap.pickle', 'wb') as handle:
            pickle.dump(roadmapItems, handle, protocol=pickle.HIGHEST_PROTOCOL)
else: 
    with open('roadmap.pickle', 'rb') as handle:
        roadmapItems = pickle.load(handle)


# https://digdir.sharepoint.com/:f:/r/sites/Autorisasjonogformidling/Delte%20dokumenter/Team%20Tilgangsinfo?csf=1&web=1&e=I07hoN

def generate_csv(roadmapitems):
    csv_output = io.StringIO()
    csv_writer = csv.writer(csv_output)
    csv_writer.writerow(["Tittel", "Produkt", "Status", "Start", "End", "Progresjon (%)", "Storypoints", "Issues", "Closed"])
    for p in roadmapItems:
            csv_writer.writerow([p.title, p.product, p.status, p.start,
                            p.end, p.progresjon, p.storypoints, p.numberOfTrackedIssues, p.numberOfSovedIssues])
    csv_output.seek(0)
    return csv_output


filename = args.file

if args.type == "csv" or args.type == "all":
    with open(filename+".csv", "w") as stream:
        writer = csv.writer(stream)
        writer.writerow(["Tittel", "Produkt", "Status", "Start", "End",
                        "Progresjon (%)", "Storypoints", "Issues", "Closed"])
        for p in roadmapItems:
            writer.writerow([p.title, p.product, p.status, p.start,
                            p.end, p.progresjon, p.storypoints, p.numberOfTrackedIssues, p.numberOfSovedIssues])

if args.type == "json" or args.type == "all":
    with open(filename+"json", "w") as writer:
        writer.write(json.dumps(roadmapItems, cls=MyJSONEncoder))

if args.type == "screen" or args.type == "all":
    print(json.dumps(roadmapItems, cls=MyJSONEncoder))

print("Done printing " + (str(len(roadmapItems))) + " projects")
