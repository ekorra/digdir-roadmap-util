import logging
import os
import json
from DigdirRoadmap import getDigdirRoadmap, MyJSONEncoder

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    token = os.getenv("DIGIDIR_ROADMAP_TOKEN")
    if (token is None):
        logging.CRITICAL("Missing authorization token")
        return func.HttpResponse("Something went wrong", status_code=500)

    with open("included_projects.txt", "r") as reader:
        filter = reader.read().splitlines()

    roadmapItems = getDigdirRoadmap(token, filter)
    numberOfRoadmapItems = len(roadmapItems)
    if numberOfRoadmapItems > 0:
        return func.HttpResponse(json.dumps(roadmapItems, cls=MyJSONEncoder))
    else:
        return func.HttpResponse("No projects found", status_code=204)
