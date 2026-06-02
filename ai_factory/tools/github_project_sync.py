#!/usr/bin/env python3
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import requests

GITHUB_API = "https://api.github.com/graphql"

STATUS_MAP = {
    "DONE": "Done",
    "✅ DONE": "Done",
    "IN_PROGRESS": "In Progress",
    "⏳ IN_PROGRESS": "In Progress",
    "ACTIVE": "In Progress",
    "IN PROGRESS": "In Progress",
    "TODO": "Todo",
    "📝 TODO": "Todo",
    "READY_FOR_DEVELOPMENT": "Todo",
    "PENDING": "Todo",
}


@dataclass
class ProjectTask:
    title: str
    body: str
    status: str


def load_backlog(backlog_path: Path) -> list[ProjectTask]:
    if not backlog_path.exists():
        return []

    with backlog_path.open("r", encoding="utf-8") as fh:
        backlog = json.load(fh)

    tasks: list[ProjectTask] = []
    for record in backlog:
        task_id = record.get("task_id") or record.get("id") or "backlog-item"
        title = f"Backlog: {task_id}"
        user_story = record.get("user_story", "No user story provided.")
        acceptance = record.get("acceptance_criteria", [])
        status = normalize_status(record.get("status", "Todo"))
        body = (
            f"### Backlog Item: {task_id}\n"
            f"**Component**: {record.get('component', 'unknown')}\n"
            f"**Status**: {status}\n\n"
            f"**User Story**:\n{user_story}\n\n"
            f"**Acceptance Criteria**:\n"
        )
        for item in acceptance:
            body += f"- {item}\n"
        context = record.get("context_anchor")
        if context:
            body += f"\n**Context**: {context}\n"
        tasks.append(ProjectTask(title=title, body=body, status=status))
    return tasks


def load_project_status(status_path: Path) -> list[ProjectTask]:
    if not status_path.exists():
        return []

    lines = status_path.read_text(encoding="utf-8").splitlines()
    table_started = False
    tasks: list[ProjectTask] = []

    for line in lines:
        if line.startswith("| Task ID"):
            table_started = True
            continue
        if table_started:
            if line.startswith("| :---"):
                continue
            if not line.startswith("|") or line.strip() == "|":
                break

            columns = [col.strip() for col in line.strip().strip("|").split("|")]
            if len(columns) < 6:
                continue
            task_id, component, description, assigned, status_text, notes = columns[:6]
            if task_id.lower().startswith("task id"):
                continue
            title = f"Status: {task_id}"
            body = (
                f"### Project Status Task: {task_id}\n"
                f"**Component**: {component}\n"
                f"**Description**: {description}\n"
                f"**Assigned**: {assigned}\n"
                f"**Notes**: {notes}\n"
            )
            status = normalize_status(status_text)
            tasks.append(ProjectTask(title=title, body=body, status=status))
    return tasks


def normalize_status(status: str) -> str:
    if not status:
        return "Todo"

    status_key = status.strip()
    if status_key in STATUS_MAP:
        return STATUS_MAP[status_key]

    upper = status_key.upper()
    if "DONE" in upper or "✅" in status_key:
        return "Done"
    if "IN_PROGRESS" in upper or "IN PROGRESS" in upper or "ACTIVE" in upper:
        return "In Progress"
    return "Todo"


def graphql_request(token: str, query: str, variables: dict) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        GITHUB_API,
        headers=headers,
        json={"query": query, "variables": variables},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("errors"):
        raise RuntimeError(f"GitHub GraphQL errors: {payload['errors']}")
    return payload["data"]


def select_repository_project(token: str, owner: str, repo: str) -> dict | None:
    query = """
    query($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        projectsV2(first: 20) {
          nodes {
            id
            title
            fields(first: 50) {
              nodes {
                ... on ProjectV2Field {
                  id
                  name
                }
                ... on ProjectV2SingleSelectField {
                  id
                  name
                  settings {
                    options {
                      id
                      name
                    }
                  }
                }
              }
            }
            items(first: 100) {
              nodes {
                id
                content {
                  ... on Issue {
                    id
                    title
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    data = graphql_request(token, query, {"owner": owner, "name": repo})
    repo_node = data.get("repository")
    if not repo_node:
        return None
    projects = repo_node.get("projectsV2", {}).get("nodes", [])
    if projects:
        return projects[0]
    return None


def create_repository_project(token: str, owner: str, repo: str) -> dict:
    mutation = """
    mutation($input: CreateProjectV2Input!) {
      createProjectV2(input: $input) {
        projectV2 {
          id
          title
        }
      }
    }
    """
    title = "TCDP Backlog Sync"
    body = "Project board automatically created by GitHub Actions for TCDP backlog synchronization."
    input_data = {
        "ownerId": owner,
        "title": title,
        "public": False,
        "body": body,
    }
    data = graphql_request(token, mutation, {"input": input_data})
    return data["createProjectV2"]["projectV2"]


def find_status_field(project: dict) -> tuple[str, dict] | tuple[None, None]:
    for field in project.get("fields", {}).get("nodes", []):
        if field.get("name", "").lower() == "status":
            options = []
            if field.get("settings"):
                options = field["settings"].get("options", [])
            return field["id"], {option["name"]: option["id"] for option in options}
    return None, {}


def find_existing_item(project: dict, title: str) -> dict | None:
    for item in project.get("items", {}).get("nodes", []):
        content = item.get("content")
        if content and content.get("title") == title:
            return item
    return None


def create_draft_issue(token: str, project_id: str, title: str, body: str) -> dict:
    mutation = """
    mutation($input: AddProjectV2DraftIssueInput!) {
      addProjectV2DraftIssue(input: $input) {
        item {
          id
        }
      }
    }
    """
    input_data = {
        "projectId": project_id,
        "title": title,
        "body": body,
    }
    data = graphql_request(token, mutation, {"input": input_data})
    return data["addProjectV2DraftIssue"]["item"]


def update_item_status(token: str, project_id: str, item_id: str, field_id: str, option_id: str) -> None:
    mutation = """
    mutation($input: UpdateProjectV2ItemFieldValueInput!) {
      updateProjectV2ItemFieldValue(input: $input) {
        projectV2Item {
          id
        }
      }
    }
    """
    input_data = {
        "projectId": project_id,
        "itemId": item_id,
        "fieldId": field_id,
        "value": json.dumps({"singleSelectOptionId": option_id}),
    }
    graphql_request(token, mutation, {"input": input_data})


def sync_project_items(token: str, owner: str, repo: str, items: list[ProjectTask]) -> None:
    project = select_repository_project(token, owner, repo)
    if project is None:
        print("No repository Projects V2 board found. Creating a new project board.")
        project = create_repository_project(token, owner, repo)

    project_id = project["id"]
    field_id, options = find_status_field(project)
    if field_id is None or not options:
        raise RuntimeError("Unable to locate a Status single-select field in the target project board.")

    for task in items:
        title = task.title
        existing_item = find_existing_item(project, title)
        if existing_item:
            item_id = existing_item["id"]
            print(f"Updating existing project item: {title}")
        else:
            print(f"Creating new project item: {title}")
            new_item = create_draft_issue(token, project_id, title, task.body)
            item_id = new_item["id"]

        option_id = options.get(task.status)
        if not option_id:
            raise RuntimeError(f"Project status option '{task.status}' not found on board.")
        update_item_status(token, project_id, item_id, field_id, option_id)


def main() -> int:
    token = os.environ.get("PROJECT_RECON_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not token:
        print("ERROR: PROJECT_RECON_TOKEN is not set.")
        return 1
    if not repo or "/" not in repo:
        print("ERROR: GITHUB_REPOSITORY is not set or invalid.")
        return 1

    owner, name = repo.split("/", 1)
    backlog = load_backlog(Path("ai_factory/shared_memory/sprint_backlog.json"))
    status_items = load_project_status(Path("ai_factory/shared_memory/project_status.md"))
    all_items = backlog + status_items
    if not all_items:
        print("No project items found to synchronize.")
        return 0

    sync_project_items(token, owner, name, all_items)
    print("GitHub Projects synchronization completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
