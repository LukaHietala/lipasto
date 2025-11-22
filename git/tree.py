import pygit2 as git

# retrieves the tree items for a given ref and path
def get_tree_items(repo_path, ref="HEAD", tree_path=""):
    repo = git.Repository(repo_path)
    # TODO: dwim for ref
    obj = repo.revparse_single(ref)
    if obj.type == git.GIT_OBJECT_COMMIT:
        tree = obj.tree
    elif obj.type == git.GIT_OBJECT_TREE:
        tree = obj
    else:
        # for other refs like tags, branches
        commit = obj.peel(git.GIT_OBJECT_COMMIT)
        tree = commit.tree

    # TODO: optimize path traversal, if possible
    if tree_path:
        # go down the tree to right path
        parts = tree_path.rstrip('/').split('/')
        for part in parts:
            found = False
            for entry in tree:
                # look for matching tree entry
                # if found, go to it
                if entry.name == part and entry.type == git.GIT_OBJECT_TREE:
                    tree = repo.get(entry.id)
                    found = True
                    break
            if not found:
                return []  # path not found

    items = []
    for entry in tree:
        item = {
            'name': entry.name,
            'type': 'tree' if entry.type == git.GIT_OBJECT_TREE else 'blob',
            'size': entry.size if entry.type == git.GIT_OBJECT_BLOB else None,
            'id': str(entry.id),
            'path': entry.name if not tree_path else f"{tree_path}/{entry.name}"
        }
        items.append(item)

    # dirs first, then files, both alphabetically
    items.sort(key=lambda x: (0 if x['type'] == 'tree' else 1, x['name'].lower()))
    
    return items