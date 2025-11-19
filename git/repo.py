from pathlib import Path
import pygit2 as git

# scans given path for bare git repos and list their names and paths
def get_bare_repos(path):
    repos = []

    repo_path = Path(path)

    for item in repo_path.iterdir():
        if item.is_dir():
            try:
                repo = git.Repository(str(item))
                if repo.is_bare:
                    repo_info = {
                        "name": item.name,
                        "path": str(item.resolve())
                    }
                    repos.append(repo_info)
            except git.GitError:
                continue
    return repos
