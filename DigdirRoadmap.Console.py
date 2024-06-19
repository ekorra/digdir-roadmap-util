from DigdirRoadmap import *
from Helpers import *
from json import JSONEncoder
import json
import argparse
import os
import pickle
import shutil
import datetime
import yaml
import time


parser = argparse.ArgumentParser()
parser.add_argument("--type", default="screen",
                    choices=["json", "csv", "mail", "screen", "all"], help="json|csv|mail|screen|all")
parser.add_argument("--save_binary", action=argparse.BooleanOptionalAction)
parser.add_argument("--testrun", action=argparse.BooleanOptionalAction)
parser.set_defaults(testrun=False)
parser.set_defaults(save_binary=False)
args = parser.parse_args()

authorizationToken = smtp_account = os.getenv("DIGIDIR_ROADMAP_TOKEN")


with open("config_test.yml", "r") as config_objct:
    config = yaml.load(config_objct, Loader=yaml.SafeLoader)
    filter = config["projects"]
    devmode = config["devlop_mode"]

if args.testrun == False:
    starttime = time.perf_counter()

    roadmapItems = getDigdirRoadmap(authorizationToken, filter, devmode)

    endtime = time.perf_counter()
    print(
        f" Total kjøretid getDigdirRoadmap: {endtime - starttime:.2f} seconds")
    if args.save_binary == True:
        with open('output/roadmap.pickle', 'wb') as handle:
            pickle.dump(roadmapItems, handle, protocol=pickle.HIGHEST_PROTOCOL)
else:
    with open('output/roadmap.pickle', 'rb') as handle:
        roadmapItems = pickle.load(handle)

filename = config["report_name"]

if args.type == "csv" or args.type == "all":
    attacement = generate_csv(roadmapItems)
    with open(f"output/{filename}.csv", "w") as stream:
        attacement.seek(0)
        shutil.copyfileobj(attacement, stream)

if args.type == "json" or args.type == "all":
    with open(f"output/{filename}.json", "w") as writer:
        writer.write(json.dumps(roadmapItems, cls=MyJSONEncoder))

if args.type == "mail":
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_ACCOUNT")

    date = datetime.datetime.now()
    formated_date = date.strftime("%d.%m.%Y")
    week = date.strftime("%W")
    subject = f"Digidir roadmap rapport uke {week}"
    body = f"Vedlagt ligger roadmap rapport for uke {week}. Rapporten ble generert {formated_date}"
    recipients = config['mail']['mail_receipients']

    attacement = generate_csv(roadmapItems)
    filename = f"Roadmap rapport uke {week}"

    send_email(subject, body, sender, recipients,
               password, attacement, filename)

if args.type == "screen" or args.type == "all":
    print(json.dumps(roadmapItems, cls=MyJSONEncoder))

print("Done printing " + (str(len(roadmapItems))) + " projects")
