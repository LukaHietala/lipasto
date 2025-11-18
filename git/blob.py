import pygit2 as git

# retrieves a blob content for given ref and path
def get_blob(repo_path, ref="HEAD", blob_path=""):
    repo = git.Repository(repo_path)
    obj = repo.revparse_single(ref)
    if obj.type == git.GIT_OBJECT_COMMIT:
        tree = obj.tree
    elif obj.type == git.GIT_OBJECT_TREE:
        tree = obj
    else:
        commit = obj.peel(git.GIT_OBJECT_COMMIT)
        tree = commit.tree

    # traverse to the blob path
    # TODO: improve the code, just quick and dirty
    if blob_path:
        parts = blob_path.rstrip('/').split('/')
        for part in parts:
            found = False
            for entry in tree:
                if entry.name == part:
                    if entry.type == git.GIT_OBJECT_BLOB:
                        blob = repo.get(entry.id)
                        return {
                            'name': entry.name,
                            'id': str(entry.id),
                            'path': blob_path,
                            'size': blob.size,
                            'is_binary': blob.is_binary,
                            'content': blob.data.decode('utf-8', errors='replace')
                        }
                    elif entry.type == git.GIT_OBJECT_TREE:
                        tree = repo.get(entry.id)
                        found = True
                        break
            if not found:
                return None  # path not found
    return None  # blob not found
