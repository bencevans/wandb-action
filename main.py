import os
import wandb
import random
import os

wandb.login()
api = wandb.Api()

runs_current = api.runs(
    path="bencevans/wandb-action",
    filters={"commit": os.environ["GITHUB_SHA"]},
)
run_current = runs_current[0] if len(runs_current) > 0 else None

runs_previous = api.runs(
    path="bencevans/wandb-action",
    filters={"commit": os.environ["GITHUB_SHA"]},
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

print("Key | Previous | Current")
print("--- | --- | ---")
for key in sorted(list(all_keys)):
    print(f"{key} | {run_previous.summary[key]} | {run_current.summary[key]}")
