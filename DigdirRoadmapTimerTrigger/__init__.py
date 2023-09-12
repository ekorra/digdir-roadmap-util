import datetime
import logging
import os
import yaml
from DigdirRoadmap import getDigdirRoadmap
from Helpers import send_email, generate_csv

import azure.functions as func

# 0 12 * * mon - Runs on every monday 12:00
app = func.FunctionApp()


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    token = os.getenv("DIGIDIR_ROADMAP_TOKEN")
    if (token is None):
        logging.CRITICAL("Missing authorization token")
    password = os.getenv("SMTP_PASSWORD")
    if (token is None):
        logging.CRITICAL("Missing smtp password")
    sender = os.getenv("SMTP_ACCOUNT")
    if (token is None):
        logging.CRITICAL("Missing smtp account")

    with open("config_test.yml", "r") as config_objct:
        config = yaml.load(config_objct, Loader=yaml.SafeLoader)
        filter = config["projects"]

    roadmapItems = getDigdirRoadmap(token, filter)

    date = datetime.datetime.now()
    formated_date = date.strftime("%d.%m.%Y")
    week = date.strftime("%W")
    subject = f"Digidir roadmap rapport uke {week}"
    body = f"Vedlagt ligger roadmap rapport for uke {week}. Rapporten ble generert {formated_date}"

    with open("config.yml", "r") as config_objct:
        config = yaml.load(config_objct, Loader=yaml.SafeLoader)
        recipients = config['mail']['mail_receipients']
        print(recipients)

    attacement = generate_csv(roadmapItems)
    filename = f"Roadmap rapport uke {week}"

    send_email(subject, body, sender, recipients,
               password, attacement, filename)

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
