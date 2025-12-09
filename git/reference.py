import pygit2 as git


def get_references(path):
    repo = git.Repository(path)
    refs = []

    for ref_name in repo.listall_references():
        try:
            ref = repo.lookup_reference(ref_name).resolve()
        except git.GitError:
            continue

        author = None
        commit_time = None
        try:
            target_obj = repo[ref.target]
            commit_obj = None
            if isinstance(target_obj, git.Commit):
                commit_obj = target_obj
            elif isinstance(target_obj, git.Tag):
                # annotated tag, peel to commit
                commit_obj = target_obj.peel(git.Commit)

            if commit_obj is not None:
                author = commit_obj.author
                commit_time = commit_obj.author.time
        except Exception:
            pass

        refs.append(
            {
                "name": ref.name,
                "shorthand": ref.shorthand,
                "target": str(ref.target),
                "author": author,
                "date": commit_time,
            }
        )
    refs.sort(key=lambda ref: ref["date"] or 0, reverse=True)
    return refs
