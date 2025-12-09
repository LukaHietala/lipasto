from pathlib import Path
import pygit2 as git

from .config import get_repo_owner


# scans given path for bare git repos and list their names and paths
def get_bare_repos(path):
    if not path:
        return []

    repo_path = Path(path)
    if not repo_path.exists() or not repo_path.is_dir():
        return []

    repos = []

    for item in repo_path.iterdir():
        if not item.is_dir():
            continue

        repo = _safe_repository(item)
        if not repo or not repo.is_bare:
            continue

        description = _read_description(item / "description")
        owner = get_repo_owner(item)
        repos.append(
            {
                "name": item.name,
                "path": str(item.resolve()),
                "description": description,
                "owner": owner,
            }
        )

    repos.sort(
        # sort by owner (empty last), then by owner name, then by repo name
        key=lambda repo: (
            not (repo.get("owner") or "").strip(),
            (repo.get("owner") or "").lower(),
            repo["name"].lower(),
        )
    )
    return repos


def _safe_repository(path):
    try:
        return git.Repository(str(path))
    except git.GitError:
        return None


def _read_description(desc_file):
    if not desc_file.exists():
        return ""
    try:
        desc_buf = desc_file.read_text().strip()
        # if no description, git writes "Unnamed repository; edit this file 'description' to name the repository."
        if desc_buf.startswith("Unnamed repository;"):
            return ""
        return desc_buf
    except Exception:
        return ""
