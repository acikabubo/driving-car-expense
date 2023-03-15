#!/usr/bin/env python3
import json
import argparse
import requests
import subprocess
from collections import defaultdict
from pip._vendor import pkg_resources
from pipdeptree import PackageDAG, render_json
from tabulate import tabulate
from packaging import version


MATTERMOST_BOTNAME = "WsHub Pkg Updater"
MATTERMOST_CHANNEL = "https://mattermost.ved.mk:15444/hooks/pqqnni145fb1mxip49hob1iopy"
MATTERMOST_MESSAGE = """
**The following python packages have newer version:**

| Package  | Current | Available | Required | Required by |
|:---------|:--------|:----------|:---------|:------------|
"""

parser = argparse.ArgumentParser()
parser.add_argument(
    '-l', '--local', action='store_true', default=False,
    help=(
        "Generate table with outdated packages "
        "for development purposes. Don't send "
        "request to mattermost channel")
)
parser.add_argument(
    '-f', '--file', action='store_true', default=False,
    help=(
        "Generate table with outdated packages "
        "for development purposes. Write it to file")
)
args = parser.parse_args()

tree = PackageDAG.from_pkgs(list(pkg_resources.working_set))
reversed = tree.reverse()

# Collect package version conditions
pkg_req_versions = defaultdict(list)
for item in list(reversed.items()):
    pkg_req_versions[item[0].project_name] = []

    specs = item[0]._obj.specs
    if not specs:
        continue

    for spec in specs:
        pkg_req_versions[item[0].project_name].append(spec)

# Reformat packages
packages = {}
for item in json.loads(render_json(reversed, indent=True)):
    package = item.get('package', {})

    pkg_name = package.get('package_name', '')

    packages[pkg_name] = item

output = subprocess.run(
    ["pip", "list", "--outdated", "--format", "json"],
    capture_output=True)

table = [['Package', 'Current', 'Available', 'Required', 'Required by']]

cannot = set()


def check_version(current_version, required_version, operator):
    _ = "==, !=, >, <, >=, <="

    x = version.parse(current_version)
    y = version.parse(required_version)

    return eval(f"x {operator} y")


for pkg in json.loads(output.stdout):
    pkg_name = pkg['name']
    current_version = pkg['version']
    latest_version = pkg['latest_version']

    item = packages.get(pkg_name)

    if not item:
        continue

    package = item.get('package', {})
    required_version = package.get('required_version', '')

    # Get required package from dependencies
    required_by = ', '.join([
        dep.get('key', '')
        for dep in item.get('dependencies', [{}])
    ])

    # Check if pkg can be updated
    versions = pkg_req_versions[pkg_name.lower()]
    if required_version is not None and versions:
        for operator, r_version in versions:
            can_be_updated = check_version(
                latest_version, r_version, operator)

            if not can_be_updated and required_by:
                cannot.add(pkg_name)
                continue

    required_version = \
        required_version if required_by else ""

    pkg_name = f'*{pkg_name}' if pkg_name in cannot else pkg_name

    # Format mattermost message
    MATTERMOST_MESSAGE += (
        f"|{pkg_name}"
        f"|{current_version}"
        f"|{latest_version}"
        f"|`{required_version}`"
        f"|{required_by}|\n")

    # if args.local:
    table.append([
        pkg_name,
        current_version,
        latest_version,
        required_version,
        required_by
    ])


footer_msg = \
    'INFO: Packages starting with * cannot be updated!'

print()
print(tabulate(table, headers='firstrow', tablefmt='grid'))
print()
print(footer_msg)
print()

# if args.local:
#     print()
#     print(tabulate(table, headers='firstrow', tablefmt='grid'))
#     print()
#     print(footer_msg)
#     print()
# elif args.file:
#     with open('wshub-reqs.txt', 'w') as f:
#         f.write(tabulate(table, headers='firstrow', tablefmt='grid'))
#         f.write('\n\n')
#         f.write(footer_msg)
# else:
#     MATTERMOST_MESSAGE += f'\n{footer_msg}\n'
#     requests.post(
#         MATTERMOST_CHANNEL,
#         json={
#             'text': MATTERMOST_MESSAGE,
#             'username': MATTERMOST_BOTNAME
#         }
#     )
