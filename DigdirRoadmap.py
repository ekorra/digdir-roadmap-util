from GithubGraphQL import getGithubProjectNodes
from json import JSONEncoder
import json
import re
import os.path

# regex pattern will match header tags with following paragraph tags from Github project item
MAIN_SECTIONS_REGEX_PATTERN = '<(h\d) dir=\\"auto\\">(.*?)<\/(h\d)>(\n|\\n)*(<p dir=\\"auto\\">(.*?)<\/p>)*'
# regex pattern will match paragraph from Github project item
DISCRIPTION_REGEX_PATTERN = '(<p dir="auto">(.*?)<\/p>)'


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
        self.task_summary = None
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
            "task_summary": self.task_summary,
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
        elif key_lower == "task_summary":
            self.task_summary = value
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

        closed = 0
        for x in trackedIssue["nodes"]:
            if x is None:
                pass
            elif x['state'] == 'CLOSED':
                closed += 1

        self.numberOfSovedIssues = closed


def getDigdirRoadmap(authorizationToken: str, filter: list):
    # TODO: use settings to enable this
    # if (os.path.isfile('sample.json')):
    #     with open('sample.json', 'r') as openfile:
    #         githubProjectNodes = json.load(openfile)

    # else:
    #     githubProjectNodes = getGithubProjectNodes(authorizationToken)
    #     githubProjectNodes_json = json.dumps(githubProjectNodes)
    #     with open("sample.json", "w") as outfile:
    #         outfile.write(githubProjectNodes_json)

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

        if "bodyHTML" in node["content"]:
            roadmapItem.task_summary = get_text_from_bodyHtml(
                node["content"]["bodyHTML"], 'Overordnet beskrivelse')

        if "url" in node["content"]:
            roadmapItem.set_value("url", node["content"]["url"])

        includeItem = False
        for n in node["fieldValues"]["nodes"]:
            if n["__typename"] == "ProjectV2ItemFieldLabelValue":
                labels = []
                for nn in n["labels"]["nodes"]:
                    if "product/" in nn["name"]:
                        if nn["name"] in filter:
                            includeItem = True
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

        if (includeItem):
            roadmapItems.append(roadmapItem)

        includeItem = True

    return roadmapItems


def get_text_from_bodyHtml(html: str, section_header: str):

    main_section = re.compile(MAIN_SECTIONS_REGEX_PATTERN)
    main_section_matches = main_section.findall(html)

    for header_with_description_group in main_section_matches:
        if header_with_description_group[1] == section_header:
            for group_item in header_with_description_group:
                discription = re.findall(DISCRIPTION_REGEX_PATTERN, group_item)
                if discription:
                    return discription[0][1]
