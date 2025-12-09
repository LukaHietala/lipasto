import pygit2 as git


def get_references(path):
    repo = git.Repository(path)
    refs = []

    for ref_name in repo.listall_references():
        try:
            ref = repo.lookup_reference(ref_name).resolve()
        except git.GitError:
            continue

        refs.append(
            {"name": ref.name, "shorthand": ref.shorthand, "target": str(ref.target)}
        )
    return refs
