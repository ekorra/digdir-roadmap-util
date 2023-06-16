from DigdirRoadmap import *
from json import JSONEncoder
import json
import csv
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--file", default="roadmap", type=str,
                    help="filename of generated file")
parser.add_argument("--type", default="screen",
                    choices=["json", "csv", "screen", "all"], help="json|csv|screen|all")
parser.add_argument("--product", help="name of product in roadmap")
parser.add_argument("--token", required=True,
                    help="Toeken required \"Bearer ghp_AbdcaADF...\"")
args = parser.parse_args()

os.environ['DIGIDIR_ROADMAP_TOKEN'] = args.token

roadmapItems = getDigdirRoadmap()

filename = args.file

if args.type == "csv" or args.type == "all":
    with open(filename+".csv", "w") as stream:
        writer = csv.writer(stream)
        writer.writerow(["Tittel", "Produkt", "Status", "Start", "End",
                        "Progresjon (%)", "Storypoints", "Issues", "Closed"])
        for p in roadmapItems:
            writer.writerow([p.title, p.product, p.status, p.start,
                            p.end, p.progresjon, p.storypoints, p.numberOfTrackedIssues, p.numberOfSovedIssues])

if args.type == "json" or args.type == "all":
    with open(filename+"json", "w") as writer:
        writer.write(json.dumps(roadmapItems, cls=MyJSONEncoder))

if args.type == "screen" or args.type == "all":
    print(json.dumps(roadmapItems, cls=MyJSONEncoder))

print("Done printing " + (str(len(roadmapItems))) + " projects")
