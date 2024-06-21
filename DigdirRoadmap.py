from GithubGraphQL import get_github_projects
from GithubGraphQL import get_github_issue
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
    def __init__(self, title, number=0):
        self.title = title
        self.task_summary = None
        self.number = number
        self.product = None
        self.url = None
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
        self.milestone = None
        self.labels = []
        self.closed_datetime = None
        self.closed_by = None

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
            "milestone": self.milestone,
            "labels": self.labels,
            "closed_datetime": self.closed_datetime,
            "closed_by": self.closed_by
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
        elif key_lower == "sluttdato":
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
        elif key_lower == "milestone":
            self.milestone = value
        elif key_lower == "closed_datetime":
            self.closed_datetime = value

    def __setTrackedIssues(self, trackedIssue):
        self.numberOfTrackedIssues = trackedIssue["totalCount"]

        closed = 0
        for x in trackedIssue["nodes"]:
            if x is None:
                pass
            elif x['state'] == 'CLOSED':
                closed += 1

        self.numberOfSovedIssues = closed

    def set_closed_Info(self, timeline_items):
        closed_at = None
        closed_by = None

        for timeline_item_node in timeline_items["nodes"]:
            if timeline_item_node is not None and timeline_item_node['__typename'] == 'ClosedEvent':
                if closed_at is None:
                    closed_at = datetime.strptime(
                        timeline_item_node['createdAt'], '%Y-%m-%dT%H:%M:%SZ')
                    closed_by = timeline_item_node['actor']['login']
                else:
                    tmp_closed_at = datetime.strptime(
                        timeline_item_node['createdAt'], '%Y-%m-%dT%H:%M:%SZ')

                    if tmp_closed_at > closed_at:
                        closed_at = tmp_closed_at
                        closed_by = timeline_item_node['actor']['login']

        self.closed_datetime = closed_at
        self.closed_by = closed_by

    def get_issue_info(self, authorizationToken: str):
        issue = get_github_issue(authorizationToken, self.number)

        if "trackedIssues" in issue:
            if (issue["trackedIssues"]["totalCount"] > 0):
                self.__setTrackedIssues(
                    issue["trackedIssues"])

        if "bodyHTML" in issue:
            body_html = issue["bodyHTML"]
            beatifullSoap = BeautifulSoup(body_html, 'html.parser')
            self.dependencies = get_dependencies(beatifullSoap)
            self.task_summary = get_task_summary(beatifullSoap)

        if "url" in issue:
            self.set_value("url", issue["url"])

        if "timelineItems" in issue:
            self.set_closed_Info(issue['timelineItems'])


def getDigdirRoadmap(authorizationToken: str, filter: list, save_github_response=False):
    if (save_github_response):
        filename = f'githubresponse_{datetime.now().strftime("%d%m%y")}'
        if (os.path.isfile(f'output/{filename}')):

            with open(f'output/{filename}', 'r') as openfile:
                githubProjectNodes = json.load(openfile)
        else:
            githubProjectNodes = get_github_projects(authorizationToken)
            githubProjectNodes_json = json.dumps(githubProjectNodes)
            with open(f'output/{filename}', "w") as outfile:
                outfile.write(githubProjectNodes_json)
    else:
        githubProjectNodes = get_github_projects(authorizationToken)

    roadmapItems = []
    for github_project_node in githubProjectNodes:
        includeItem = False
        issuenumber = 0
        if ('number' in github_project_node["content"]):
            issuenumber = github_project_node["content"]["number"]
        roadmapItem = DigdirRoadmapItem(

            github_project_node["content"]["title"], issuenumber)

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

        if (includeItem):
            if (roadmapItem.number != 0):
                roadmapItem.get_issue_info(authorizationToken)
            else:
                print(f'Roadmapissue mangler nummeer - {roadmapItem.title}')
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
