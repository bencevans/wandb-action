"""
GitHub Action for reporting Weights & Biases metrics.
"""

import os
import sys
import json
from typing import Optional
import subprocess
from github import Github
import wandb


def get_run(api: wandb.Api, path: str, sha: str) -> wandb.apis.public.Run:
    """
    Retrieves a run from wandb given a path and commit sha
    """

    runs = api.runs(
        path=path,
        filters={"commit": sha},
    )
    return runs[0] if len(runs) > 0 else None


def format_commit_message(run: wandb.apis.public.Run) -> str:
    """
    Formats a commit message given a wandb run
    """

    return "\n".join(
        [
            "# WandB Summary",
            "",
            "Metric | Value",
            "------ | -----",
            "{}".format(
                "\n".join(
                    [
                        f"{key} | {run.summary[key]}"
                        for key in sorted(run.summary.keys())
                    ]
                ),
            ),
            "",
            f"- [Open on WandB]({run.url})",
            "",
        ]
    )


def format_pr_message(
    prev_run: Optional[wandb.apis.public.Run],
    prev_ref: str,
    curr_run: wandb.apis.public.Run,
    curr_ref: str,
) -> str:
    """
    Formats a PR message given two wandb runs
    """
    keys = sorted(
        set(prev_run.summary.keys() if prev_run else []).union(
            set(curr_run.summary.keys())
        )
    )

    message = [
        "# WandB Summary",
        "",
        f"{prev_ref}...{curr_ref}",
        "",
        "Metric | Previous | Current",
        "------ | -------- | -------",
    ]

    for key in keys:
        prev_value = (
            prev_run.summary[key]
            if prev_run is not None and key in prev_run.summary
            else "-"
        )
        curr_value = curr_run.summary[key] if key in curr_run.summary else "-"
        message.append(f"{key} | {prev_value} | {curr_value}")

    message.append("")
    if prev_run is not None:
        message.append(f"- [Open Previous on WandB]({prev_run.url})")
    message.append(f"- [Open Current on WandB]({curr_run.url})")
    message.append("")
    return "\n".join(message)


if __name__ == "__main__":
    wandb.login()
    wandb_api = wandb.Api()

    github_token = os.environ["GITHUB_TOKEN"]
    github_repo = os.environ["GITHUB_REPOSITORY"]

    curr_ref = os.environ["GITHUB_SHA"]
    prev_ref = os.environ["GITHUB_BASE_REF"]

    is_pull_request = os.environ["GITHUB_EVENT_NAME"] == "pull_request"
    pull_request_id = (
        int(os.environ["GITHUB_REF"].split("/")[-2]) if is_pull_request else None
    )

    if is_pull_request:
        with open(os.environ["GITHUB_EVENT_PATH"]) as f:
            prev_ref = json.load(f)["pull_request"]["base"]["sha"]

    wandb_entity = (
        os.environ["WANDB_ENTITY"]
        if "WANDB_ENTITY" in os.environ and os.environ["WANDB_ENTITY"] != ""
        else os.environ["GITHUB_REPOSITORY"].split("/")[0]
    )
    wandb_project = (
        os.environ["WANDB_PROJECT"]
        if "WANDB_PROJECT" in os.environ and os.environ["WANDB_PROJECT"] != ""
        else os.environ["GITHUB_REPOSITORY"].split("/")[1]
    )
    wandb_path = wandb_entity + "/" + wandb_project

    print(f"Current ref: '{curr_ref}'")
    print(f"Previous ref: '{prev_ref}'")

    github_api = Github(github_token)
    github_api_repo = github_api.get_repo(github_repo)

    curr_run = get_run(wandb_api, wandb_path, curr_ref)

    if curr_run is None:
        print(f"⚠️ No WandB run found for current ref '{curr_ref}'")
        sys.exit(1)

    if is_pull_request:
        prev_run = get_run(wandb_api, wandb_path, prev_ref)

        # TODO: Comment on PR rather than commit
        print(
            "✍️ Written pull request comment: ",
            github_api_repo.get_pull(pull_request_id)
            .create_issue_comment(
                format_pr_message(prev_run, prev_ref, curr_run, curr_ref)
            )
            .html_url,
        )
    else:
        print(
            "✍️ Written commit comment: ",
            github_api_repo.get_commit(curr_ref)
            .create_comment(format_commit_message(curr_run))
            .html_url,
        )
