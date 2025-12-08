import pygit2 as git


def get_repo_owner(repo_path: str) -> str | None:
    """Return lipasto.owner from repo config, None when missing or on error."""
    try:
        repo = git.Repository(str(repo_path))
    except git.GitError:
        return None

    try:
        config = repo.config
    except git.GitError:
        return None

    try:
        return config["lipasto.owner"]
    except KeyError:
        return None
    except git.GitError:
        return None
