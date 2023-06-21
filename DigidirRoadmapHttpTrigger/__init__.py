import logging
from DigdirRoadmap import * 

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    roadmapItems = getDigdirRoadmap()
    return func.HttpResponse(f"Hello, {roadmapItems}. This HTTP triggered function executed successfully.")
    # if len(roadmapItems) > 0:
    #     return func.HttpResponse(roadmapItems)
    # else:
    #return func.HttpResponse("No projects found", status_code=204)

   # if name:
    # return func.HttpResponse(f"Hello, {roadmapItems}. This HTTP triggered function executed successfully.")
    # else:
    #     return func.HttpResponse(
        #      "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
        #      status_code=200
        # )
