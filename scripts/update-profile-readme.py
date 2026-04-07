#!/usr/bin/env python3
import json
import urllib.request
from pathlib import Path

USERNAME = "cclintw"
README_PATH = Path("README.md")
START_MARKER = "<!-- repo-list:start -->"
END_MARKER = "<!-- repo-list:end -->"
SKIP_REPOS = {"cclintw"}

def fetch_repos(username):
    url = f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"{username}-profile-readme-updater"
        }
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))

def build_repo_lines(repos):
    lines = []
    filtered = []

    for repo in repos:
        if repo["name"] in SKIP_REPOS:
            continue
        if repo.get("fork"):
            continue
        filtered.append(repo)

    filtered.sort(key=lambda r: r.get("pushed_at") or "", reverse=True)

    for repo in filtered:
        name = repo["name"]
        url = repo["html_url"]
        desc = (repo.get("description") or "").strip()
        lang = repo.get("language") or "Unknown"

        if desc:
            line = f"- [{name}]({url}) - {desc} ({lang})"
        else:
            line = f"- [{name}]({url}) ({lang})"

        lines.append(line)

    return "\n".join(lines)

def update_readme():
    content = README_PATH.read_text(encoding="utf-8")

    if START_MARKER not in content or END_MARKER not in content:
        raise ValueError("README.md does not contain repo list markers.")

    repos = fetch_repos(USERNAME)
    repo_list = build_repo_lines(repos)

    start_index = content.index(START_MARKER) + len(START_MARKER)
    end_index = content.index(END_MARKER)

    new_content = (
        content[:start_index]
        + "\n"
        + repo_list
        + "\n"
        + content[end_index:]
    )

    README_PATH.write_text(new_content, encoding="utf-8")

if __name__ == "__main__":
    update_readme()