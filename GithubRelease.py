import logging
import logging.handlers
import os
import shutil
import datetime
import yaml
from Helpers import generate_csv
from DigdirRoadmap import getDigdirRoadmap

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

try:
    roadmap_token = os.environ["DIGIDIR_ROADMAP_TOKEN"]
except KeyError:
    roadmap_token = "Token not available!"
    logger.error("Token not available!")
    # raise


date = datetime.datetime.now()
formated_date = date.strftime("%d%m%Y_%H%S")
week = date.strftime("%W")


def main() -> any:
    with open("config.yml", "r") as config_objct:
        config = yaml.load(config_objct, Loader=yaml.SafeLoader)
        filter = config["projects"]

    roadmap_issues = getDigdirRoadmap(roadmap_token, filter)
    csvfile = generate_csv(roadmap_issues)
    reportname = config["report_name"]
    filename = f'output/{reportname}.csv'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as stream:
        csvfile.seek(0)
        shutil.copyfileobj(csvfile, stream)


if __name__ == "__main__":
    logger.info(f"Token value: {roadmap_token}")
    main()
