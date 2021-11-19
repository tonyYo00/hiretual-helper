#!/usr/bin/python3

import requests, json
from requests.auth import HTTPBasicAuth
import calendar
from datetime import datetime
from pprint import pprint
import webbrowser
import json
from pathlib import Path
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-label", "-l", help="set lable", default="BMC")
args = parser.parse_args()


# config
label = args.label

now = datetime.now()
dateBefore = datetime(now.year, now.month, 1).strftime("%Y-%m-%d")
dateAfter = datetime(
    now.year, now.month, calendar.monthrange(now.year, now.month)[1]
).strftime("%Y-%m-%d")
status = ["Approved & Closed", "Released"]


home = str(Path.home())
configFileName = f"{home}/.pts_config.json"
try:
    f = open(configFileName, "r")
    apiToken = json.load(f)["apiToken"]
except:
    webbrowser.open("https://id.atlassian.com/manage-profile/security/api-tokens")
    apiToken = input("Please enter api token: ")
    print("You entered: " + apiToken)
    config = {"apiToken": apiToken}
    with open(configFileName, "w") as f:
        json.dump(config, f)
    pass


statusStr = ", ".join([f'"{elem}"' for elem in status])
statusCategoryChangedDateBeteenJQL = f"statusCategoryChangedDate >= {dateBefore} AND statusCategoryChangedDate <= {dateAfter}"
statusJQL = f"status in ({statusStr})"
# labelsJQL = f"labels = {label}"
params = [statusCategoryChangedDateBeteenJQL, statusJQL]
if label != "":
    params.append(f"labels = {label}")

orderJQL = "ORDER BY priority DESC, status ASC"
jql = " AND ".join(params) + " " + orderJQL


url = "https://hiretual.atlassian.net/rest/api/3/search"
sptKey = "customfield_10014"
deleloper = "customfield_10065"
# priority = 'priority.name'
# status
# statuscategorychangedate

reuireTest = "customfield_10064"
auth = HTTPBasicAuth("tonglin@hiretual.com", apiToken)

headers = {"Accept": "application/json"}
response = requests.get(url, params={"jql": jql}, auth=auth, headers=headers)

data = json.loads(response.text)
issues = data["issues"]


def get_res_map(item):
    fields = item["fields"]
    return {
        "key": item["key"],
        # "statuscategorychangedate": fields["statuscategorychangedate"],
        "status": fields["status"]["name"],
        "story_point": fields["customfield_10014"],
        # "displayName": fields["assignee"]["displayName"],
        "require test": fields[reuireTest]["value"] == "Require Test",
        "deleloper": fields[deleloper]["displayName"],
        # "priority": fields["priority"]["name"],
    }


outData = {}
for item in issues:
    data = get_res_map(item)
    name = data["deleloper"]
    value = outData.setdefault(name, {"total": 0, "data": []})
    value["total"] += data["story_point"]
    value["data"].append({"key": data["key"], "story_point": data["story_point"]})


pprint(outData)
