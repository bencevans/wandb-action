import os
import wandb
import random
import os
from github import Github

wandb.login()
api = wandb.Api()

github = Github(os.environ["GITHUB_TOKEN"])

ref_current = os.environ["GITHUB_SHA"]
ref_previous = os.environ["GITHUB_BASE_REF"]

print("Current ref: ", ref_current)
print("Previous ref: ", ref_previous)

runs_current = api.runs(
    path="bencevans/wandb-action",
    filters={"commit": ref_current},
)
run_current = runs_current[0] if len(runs_current) > 0 else None

runs_previous = api.runs(
    path="bencevans/wandb-action",
    filters={"commit": ref_previous},
)
run_previous = runs_previous[0] if len(runs_previous) > 0 else None

if run_current is None:
    print("No current run")

if run_previous is None:
    print("No previous run")

all_keys = set()
if run_current is not None:
    for key in run_current.summary.keys():
        all_keys.add(key)

if run_previous is not None:
    for key in run_previous.summary.keys():
        all_keys.add(key)

github_commit = github.get_repo("bencevans/wandb-action").get_commit(ref_current)

comment = github_commit.create_comment(
    """
# Summary

Metric | Result
------ | ------
{}

{}
""".format(
        "\n".join([f"{key} | {run_current.summary[key]}" for key in sorted(all_keys)]),
        "https://app.wandb.ai/bencevans/wandb-action/runs/{}".format(run_current.id),
    )
)

print("✍️ Written commit comment: ", comment.html_url)

# print("Key | Previous | Current")
# print("--- | --- | ---")
# for key in sorted(list(all_keys)):
#     previous = (
#         run_previous.summary[key]
#         if run_previous is not None and key in run_previous.summary
#         else ""
#     )
#     current = (
#         run_current.summary[key]
#         if run_current is not None and key in run_current.summary
#         else ""
#     )
#     print(f"{key} | {previous} | {current}")
