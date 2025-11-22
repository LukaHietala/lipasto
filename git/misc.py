import pygit2 as git

def get_version():
    return git.LIBGIT2_VERSION

def validate_repo_name(name):
    if not name or not isinstance(name, str):
        return False
    # no path traversal or hidden dirs
    if '/' in name or '\\' in name or '..' in name or name.startswith('.'):
        return False
    # basic char check
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
    if any(char in name for char in invalid_chars):
        return False
    return True

def validate_ref(repo_path, ref):
    if not ref or not isinstance(ref, str):
        return False
    # attempt to resolve the ref, if fails, invalid
    try:
        repo = git.Repository(repo_path)
        repo.revparse_single(ref.strip())
        return True
    except:
        return False

def validate_ref_as_commit(repo_path, ref):
    # this tries to resolve ref to a commit
    # it only works for commit, tag, and branch refs, since they all point to a commit
    # blobs and trees do not resolve to commits, so they are invalid
    # more about refs: 
    # https://git-scm.com/book/en/v2/Git-Internals-Git-References

    if not validate_ref(repo_path, ref):
        return False
    try:
        repo = git.Repository(repo_path)
        obj = repo.revparse_single(ref.strip())
        if obj.type == git.GIT_OBJECT_COMMIT:
            return True
        obj.peel(git.GIT_OBJECT_COMMIT)
        return True
    except:
        return False

def sanitize_path(path):
    # protects against path traversal and invalid paths
    if not path:
        return ""
    path = path.strip('/')
    if '..' in path:
        raise ValueError("invalid path! contains '..'")
    return path