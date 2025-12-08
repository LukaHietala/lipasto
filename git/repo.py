from pathlib import Path
import pygit2 as git

from .config import get_repo_owner

# scans given path for bare git repos and list their names and paths
def get_bare_repos(path):
    repos = []

    repo_path = Path(path)

    for item in repo_path.iterdir():
        if item.is_dir():
            try:
                repo = git.Repository(str(item))
                if repo.is_bare:
                    description = ""
                    desc_file = item / "description"
                    if desc_file.exists():
                        try:
                            description = desc_file.read_text().strip()
                        except:
                            pass
                    owner = get_repo_owner(item)
                    repo_info = {
                        "name": item.name,
                        "path": str(item.resolve()),
                        "description": description,
                        "owner": owner
                    }
                    repos.append(repo_info)
            except git.GitError:
                continue
    return repos
