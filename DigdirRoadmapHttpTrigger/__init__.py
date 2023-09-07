import logging
import os
import json
import yaml
from DigdirRoadmap import getDigdirRoadmap, MyJSONEncoder

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    token = os.getenv("DIGIDIR_ROADMAP_TOKEN")
    if (token is None):
        logging.CRITICAL("Missing authorization token")
        return func.HttpResponse("Something went wrong", status_code=500)

    with open("config.yml", "r") as config_objct:
        config = yaml.load(config_objct, Loader=yaml.SafeLoader)
        filter = config["projects"]

    roadmapItems = getDigdirRoadmap(token, filter)
    numberOfRoadmapItems = len(roadmapItems)
    if numberOfRoadmapItems > 0:
        return func.HttpResponse(json.dumps(roadmapItems, cls=MyJSONEncoder))
    else:
        return func.HttpResponse("No projects found", status_code=204)
