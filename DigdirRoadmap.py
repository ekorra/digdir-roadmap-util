from GithubGraphQL import getGithubProjectNodes
from json import JSONEncoder
from datetime import datetime
from bs4 import BeautifulSoup
import json
import os.path


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
        self.progresjon = None
        self.numberOfTrackedIssues = 0
        self.numberOfSovedIssues = 0
        self.state = None
        self.estimerte_ukesverk = None
        self.body_html = None
        self.dependencies = None
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
            "progretion": self.progresjon,
            "state": self.state,
            "tracked": self.numberOfTrackedIssues,
            "solved": self.numberOfSovedIssues,
            "estimated_work": self.estimerte_ukesverk,
            "dependencies": self.dependencies,
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
        elif key_lower == "progresjon (%)":
            self.progresjon = value
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
        elif key_lower == "estimerte ukesverk":
            self.estimerte_ukesverk = value

    def setTrackedIssues(self, trackedIssue):
        self.numberOfTrackedIssues = trackedIssue["totalCount"]

        closed = 0
        for x in trackedIssue["nodes"]:
            if x is None:
                pass
            elif x['state'] == 'CLOSED':
                closed += 1

        self.numberOfSovedIssues = closed


def getDigdirRoadmap(authorizationToken: str, filter: list, save_github_response=False):
    if (save_github_response):
        filename = f'githubresponse_{datetime.now().strftime("%d%m%y")}'
        if (os.path.isfile(f'output/{filename}')):

            with open(f'output/{filename}', 'r') as openfile:
                githubProjectNodes = json.load(openfile)
        else:
            githubProjectNodes = getGithubProjectNodes(authorizationToken)
            githubProjectNodes_json = json.dumps(githubProjectNodes)
            with open(f'output/{filename}', "w") as outfile:
                outfile.write(githubProjectNodes_json)
    else:
        githubProjectNodes = getGithubProjectNodes(authorizationToken)

    roadmapItems = []
    for github_project_node in githubProjectNodes:
        includeItem = False
        roadmapItem = DigdirRoadmapItem(
            github_project_node["content"]["title"], "", "")

        for fieldValue_node in github_project_node["fieldValues"]["nodes"]:
            if fieldValue_node["__typename"] == "ProjectV2ItemFieldLabelValue":
                labels = []
                for labels_node in fieldValue_node["labels"]["nodes"]:
                    if "product/" in labels_node["name"]:
                        if labels_node["name"] in filter:
                            includeItem = True
                        else:
                            break
                        roadmapItem.set_value("product", labels_node["name"])
                    roadmapItem.set_value("labels", labels_node["name"])
                    labels.append(labels_node["name"])
            elif fieldValue_node["__typename"] == "ProjectV2ItemFieldSingleSelectValue":
                roadmapItem.set_value(
                    fieldValue_node["field"]["name"], fieldValue_node["name"])
            elif fieldValue_node["__typename"] == "ProjectV2ItemFieldTextValue":
                roadmapItem.set_value(
                    fieldValue_node["field"]["name"], fieldValue_node["text"])
            elif fieldValue_node["__typename"] == "ProjectV2ItemFieldNumberValue":
                roadmapItem.set_value(
                    fieldValue_node["field"]["name"], fieldValue_node["number"])
            elif fieldValue_node["__typename"] == "ProjectV2ItemFieldDateValue":
                roadmapItem.set_value(
                    fieldValue_node["field"]["name"], fieldValue_node["date"])
            elif fieldValue_node["__typename"] == "ProjectV2ItemFieldMilestoneValue":
                roadmapItem.set_value(
                    fieldValue_node["field"]["name"], fieldValue_node["milestone"]["title"])

        if "state" in github_project_node["content"]:
            roadmapItem.set_value(
                "state", github_project_node["content"]["state"])

        if "trackedIssues" in github_project_node["content"]:
            if (github_project_node["content"]["trackedIssues"]["totalCount"] > 0):
                roadmapItem.setTrackedIssues(
                    github_project_node["content"]["trackedIssues"])

        if "bodyHTML" in github_project_node["content"]:
            body_html = github_project_node["content"]["bodyHTML"]
            beatifullSoap = BeautifulSoup(body_html, 'html.parser')
            roadmapItem.dependencies = get_dependencies(beatifullSoap)
            roadmapItem.task_summary = get_task_summary(beatifullSoap)

        if "url" in github_project_node["content"]:
            roadmapItem.set_value("url", github_project_node["content"]["url"])

        if (includeItem):
            roadmapItems.append(roadmapItem)
    return roadmapItems


def get_csvfield_with_newline(fieldvalues: list):

    text = ""
    for i, item in enumerate(fieldvalues):
        if i:
            text += '\n'
        text += item

    return text


def get_task_summary(soup: BeautifulSoup):
    beskrivelse = ''
    overorndet_beskrivelse = soup.find(
        ['h1', 'h2', 'h3'], string='Overordnet beskrivelse')
    if overorndet_beskrivelse is not None:
        paragraps = []
        for sibling in overorndet_beskrivelse.next_siblings:
            # print(repr(sibling))
            if sibling.name == 'p':
                paragraps.append(sibling.text)
            if sibling.name in ['h1', 'h2', 'h3']:
                break

        beskrivelse = get_csvfield_with_newline(paragraps)

    return beskrivelse


def get_dependencies(soup: BeautifulSoup):
    dependencies = ''
    avhengigheter_header = soup.find('h3', string='Avhengigheter')
    if (avhengigheter_header is not None):
        tacking_section = avhengigheter_header.find_parent("tracking-block")
        if tacking_section is None:
            return dependencies

        links = tacking_section.findAll('a')
        dependencies_list = []
        # each issue has two spans name and id#repo
        for link in links:
            text = ''
            spans = link.findAll('span')
            for i, span in enumerate(spans):
                if i:
                    text += ' - '
                text += span.string
            dependencies_list.append(text)

            # for span in spans:
            #     text = text + " - " + span.string

            # dependencies_list.append(text)

        dependencies = get_csvfield_with_newline(dependencies_list)

    return dependencies
