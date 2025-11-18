import pygit2 as git

def get_refs(path):
    repo = git.Repository(path)
    refs = []
    for ref_name in repo.listall_references():
        ref = repo.lookup_reference(ref_name)
        refs.append({
            'name': ref.name,
            'target': str(ref.target)
        })
    return refs