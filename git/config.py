import pygit2 as git


def get_repo_owner(repo_path: str) -> str | None:
    config = _load_repo_config(repo_path)
    if not config:
        return None

    try:
        return config["lipasto.owner"]
    except KeyError:
        return None
    except git.GitError:
        return None


def is_repo_hidden(repo_path: str) -> bool:
    config = _load_repo_config(repo_path)
    if not config:
        return False

    try:
        raw_value = config["lipasto.hidden"]
    except KeyError:
        return False
    except git.GitError:
        return False

    return str(raw_value).strip().lower() == "true"


def _load_repo_config(repo_path: str):
    try:
        repo = git.Repository(str(repo_path))
    except git.GitError:
        return None

    try:
        return repo.config
    except git.GitError:
        return None

