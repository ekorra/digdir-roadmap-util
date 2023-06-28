from GithubGraphQL import *
from json import JSONEncoder
import json


class MyJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, DigdirRoadmapItem):
            return o.__dict__
        return MyJSONEncoder(self, o)


def default(obj):
    if hasattr(obj, 'to_json'):
        return obj.to_json()
    raise TypeError(
        f'Object of type {obj.__class__.__name__} is not JSON serializable')


class DigdirRoadmapItem:
    def __init__(self, title, number, url, state=None):
        self.title = title
        self.number = number
        self.product = None
        self.url = url
        self.start = None
        self.end = None
        self.status = None
        self.storypoints = None
        self.progresjon = None
        self.totalt_estimert = None
        self.numberOfTrackedIssues = 0
        self.numberOfSovedIssues = 0
        self.state = None
        self.labels = []

    def __str__(self):
        return json.dumps(dict(self), ensure_ascii=False)

    def __iter__(self):
        yield from {
            "title": self.title,
            "product": self.product,
            "number":  self.number,
            "url":  self.url,
            "start": self.start,
            "end": self.end,
            "status": self.status,
            "storypoints":  self.storypoints,
            "progretion": self.progresjon,
            "estimated_total": self.totalt_estimert,
            "state": self.state,
            "tracked": self.numberOfTrackedIssues,
            "solved": self.numberOfSovedIssues,
            "labels": self.labels
        }.items()

    def __repr__(self) -> str:
        return self.__str__()

    def to_json(self):
        return self.__str__()

    def set_value(self, key, value):
        key_lower = key.lower()
        if key_lower == "title":
            self.title = value
        elif key_lower == "start":
            self.start = value
        elif key_lower == "end":
            self.end = value
        elif key_lower == "status":
            self.status = value
        elif key_lower == "storypoints":
            self.storypoints = value
        elif key_lower == "progresjon (%)":
            self.progresjon = value
        elif key_lower == "totalt estimert":
            self.totalt_estimert = value
        elif key_lower == "labels":
            self.labels.append(value)
        elif key_lower == "url":
            self.url = value
        elif key_lower == "product":
            if "/" in value:
                self.product = value.split("/")[1]
            else:
                self.product == value
        elif key_lower == "state":
            self.state = value

    def setTrackedIssues(self, trackedIssue):
        self.numberOfTrackedIssues = trackedIssue["totalCount"]
        #stauses = trackedIssue["nodes"]
        closed = [x for x in trackedIssue["nodes"] if x['state'] == 'CLOSED']
        self.numberOfSovedIssues = len(closed)


def getDigdirRoadmap(authorizationToken):
    githubProjectNodes = getGithubProjectNodes(authorizationToken)

    roadmapItems = []
    for node in githubProjectNodes:
        roadmapItem = DigdirRoadmapItem(
            node["content"]["title"], "", "")

        if "state" in node["content"]:
            roadmapItem.set_value("state", node["content"]["state"])

        if "trackedIssues" in node["content"]:
            if (node["content"]["trackedIssues"]["totalCount"] > 0):
                roadmapItem.setTrackedIssues(node["content"]["trackedIssues"])

        if "url" in node["content"]:
            roadmapItem.set_value("url", node["content"]["url"])

        includeItem = True
        for n in node["fieldValues"]["nodes"]:
            if n["__typename"] == "ProjectV2ItemFieldLabelValue":
                labels = []
                for nn in n["labels"]["nodes"]:
                    if "product/" in nn["name"]:
                        # if nn["name"] == args.product:
                        #    includeItem = True
                        roadmapItem.set_value("product", nn["name"])
                    roadmapItem.set_value("labels", nn["name"])
                    labels.append(nn["name"])
            elif n["__typename"] == "ProjectV2ItemFieldSingleSelectValue":
                roadmapItem.set_value(n["field"]["name"], n["name"])
            elif n["__typename"] == "ProjectV2ItemFieldTextValue":
                roadmapItem.set_value(n["field"]["name"], n["text"])
            elif n["__typename"] == "ProjectV2ItemFieldNumberValue":
                roadmapItem.set_value(n["field"]["name"], n["number"])
            elif n["__typename"] == "ProjectV2ItemFieldDateValue":
                roadmapItem.set_value(n["field"]["name"], n["date"])
            elif n["__typename"] == "ProjectV2ItemFieldMilestoneValue":
                roadmapItem.set_value(
                    n["field"]["name"], n["milestone"]["title"])

        if (includeItem == True):
            roadmapItems.append(roadmapItem)

        includeItem = True

    return roadmapItems
