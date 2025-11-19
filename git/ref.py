import pygit2 as git

# retrieves all refs (branches, tags) for given repo path
# TODO: handle symbolic refs and situation when HEAD is unborn or pointing to nothing
def get_refs(path):
    repo = git.Repository(path)
    refs = []
    # add head ref manually
    head_ref = repo.head
    refs.append({
        'name': "HEAD",
        'shorthand': "HEAD",
        'target': str(head_ref.target)
    })
    
    for ref_name in repo.listall_references():
        ref = repo.lookup_reference(ref_name)
        refs.append({
            'name': ref.name,
            'shorthand': ref.shorthand,
            # TODO: type, branch or tag
            'target': str(ref.target)
        })
    return refs