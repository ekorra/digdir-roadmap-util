import logging
import logging.handlers
import yaml
import datetime
import requests
import os
from Helpers import send_email

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    "status.log",
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)


def main() -> None:
    with open("config.yml", "r") as stream:
        config = yaml.safe_load(stream)

    if config is not None:
        reciepients = config["mail_receipients"]
        shold_send_mail = config["send_notification_mail"]
        release_url = config["latest_release_url"]

    if (shold_send_mail is None or reciepients is None or release_url is None):
        return

    response = requests.get(release_url)
    if response.status_code != 200:
        return

    response_json = response.json()
    release_name = response_json["name"]
    report_link = response_json["assets"][0]["browser_download_url"]
    release_link = response_json["html_url"]

    date = datetime.datetime.now()
    week = date.strftime("%W")
    subject = f"Digidir roadmap rapport uke {week}"
    body = f"{release_name}<br>Rapport for uke {week} kan lastes ned ved å trykke <a href={report_link}>her</a><br>Eventult kan du gå <a href={release_link}>hit</a> og laste den ned"

    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_ACCOUNT")

    if not password or not sender:
        print("sender: "+sender)
        raise Exception("SMTP_PASSWORD of SMTP_ACCOUNT missing")

    send_email(subject, body, sender, reciepients, password)


if __name__ == "__main__":
    main()
