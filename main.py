"""
GitHub Action for reporting Weights & Biases metrics.
"""

import os
import wandb
import random
import os
from github import Github


def get_run(api: wandb.Api, wandb_path: str, sha: str) -> wandb.apis.public.Run:
    """
    Retrieves a run from wandb given a path and commit sha
    """

    runs = api.runs(
        path=wandb_path,
        filters={"commit": sha},
    )
    return runs[0] if len(runs) > 0 else None


def format_commit_message(run: wandb.apis.public.Run) -> str:
    """
    Formats a commit message given a wandb run
    """

    return """
    # WandB Summary

    Metric | Result
    ------ | ------
    {}

    {}
    """.format(
        "\n".join(
            [
                f"{key} | {run_current.summary[key]}"
                for key in sorted(run.summary.keys())
            ]
        ),
        run.url,
    )


def format_pr_message(
    prev_run: wandb.apis.public.Run, curr_run: wandb.apis.public.Run
) -> str:
    """
    Formats a PR message given two wandb runs
    """
    return """
    # WandB Summary

    Metric | Previous | Current
    ------ | -------- | -------
    {}

    - [Previous Run]({prev_run_url})
    - [Current Run]({curr_run_url})
    """.format(
        "\n".join(
            [
                f"{key} | {prev_run.summary[key]} | {curr_run.summary[key]}"
                for key in sorted(
                    set(prev_run.summary.keys()).union(set(curr_run.summary.keys()))
                )
            ]
        ),
        prev_run_url=prev_run.url,
        curr_run_url=curr_run.url,
    )


if __name__ == "__main__":
    wandb.login()
    wandb_api = wandb.Api()

    github_token = os.environ["GITHUB_TOKEN"]
    github_repo = os.environ["GITHUB_REPOSITORY"]

    ref_current = os.environ["GITHUB_SHA"]
    ref_previous = os.environ["GITHUB_BASE_REF"]

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

    print("Current ref: ", ref_current)
    print("Previous ref: ", ref_previous)

    github_api = Github(github_token)
    github_api_repo = github_api.get_repo(github_repo)

    runs_current = get_run(wandb_api, wandb_path, ref_current)
    runs_previous = get_run(wandb_api, wandb_path, ref_previous)

    if runs_current is None:
        print(f"⚠️ No run found for current ref {ref_current}")
        exit(1)

    if runs_previous is None:
        print(f"⚠️ No run found for previous ref {ref_previous}")

    print(
        "✍️ Written commit comment: ",
        github_api_repo.get_commit(ref_current)
        .create_comment(format_commit_message(run_current))
        .html_url,
    )

    if run_previous is not None:
        print(
            "✍️ Written pull request comment: ",
            github_api_repo.get_issue(run_previous.pull_request.number)
            .create_issue_comment(format_pr_message(run_previous))
            .html_url,
        )
