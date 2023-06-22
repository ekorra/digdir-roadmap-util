from DigdirRoadmap import *
from Helpers import *
from json import JSONEncoder
import json
import argparse
import os
import pickle
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("--file", default="roadmap", type=str,
                    help="filename of generated file")
parser.add_argument("--type", default="screen",
                    choices=["json", "csv", "mail", "screen", "all"], help="json|csv|mail|screen|all")
parser.add_argument("--product", help="name of product in roadmap")
parser.add_argument("--save_binary", action=argparse.BooleanOptionalAction)
parser.add_argument("--testrun", action=argparse.BooleanOptionalAction)
parser.set_defaults(testrun=False)
parser.set_defaults(save_binarly=False)
args = parser.parse_args()

authorizationToken = smtp_account = os.getenv("DIGIDIR_ROADMAP_TOKEN")

if args.testrun == False:
    roadmapItems = getDigdirRoadmap(authorizationToken)
    if args.save_binary == True:
        with open('roadmap.pickle', 'wb') as handle:
            pickle.dump(roadmapItems, handle, protocol=pickle.HIGHEST_PROTOCOL)
else:
    with open('roadmap.pickle', 'rb') as handle:
        roadmapItems = pickle.load(handle)

filename = args.file

if args.type == "csv" or args.type == "all":
    attacement = generate_csv(roadmapItems)
    with open(filename+".csv", "w") as stream:
        attacement.seek(0)
        shutil.copyfileobj(attacement, stream)

if args.type == "json" or args.type == "all":
    with open(filename+"json", "w") as writer:
        writer.write(json.dumps(roadmapItems, cls=MyJSONEncoder))

if args.type == "mail":
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_account = os.getenv("SMTP_ACCOUNT")

    subject = "Digdir roadmap report"
    body = "Vedlagt ligger roadmap rapport"
    sender = smtp_account
    recipients = ["espen.korra@digdir.no"]
    password = smtp_password

    attacement = generate_csv(roadmapItems)
    send_email(subject, body, sender, recipients, password, attacement)

if args.type == "screen" or args.type == "all":
    print(json.dumps(roadmapItems, cls=MyJSONEncoder))

print("Done printing " + (str(len(roadmapItems))) + " projects")
