import datetime
import logging
import os
from DigdirRoadmap import *

import azure.functions as func


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    
    token = os.getenv("DIGIDIR_ROADMAP_TOKEN")
    if(token == None):
        logging.CRITICAL("Missing authorization token")

    roadmapItems = getDigdirRoadmap(token)
    numberOfRoadmapItems = len(roadmapItems)

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
