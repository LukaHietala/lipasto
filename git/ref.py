import pygit2 as git

# retrieves all refs (branches, tags) for given repo path
def get_refs(path):
    repo = git.Repository(path)
    refs = []
    for ref_name in repo.listall_references():
        ref = repo.lookup_reference(ref_name)
        refs.append({
            'name': ref.name,
            'shorthand': ref.shorthand,
            # TODO: type, branch or tag
            'target': str(ref.target)
        })
    return refs