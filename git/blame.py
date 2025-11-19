import pygit2 as git

# discourage using blame because its very expensive, especially on repos with long commits history
# retrieves blame information for a file at given ref and path
def get_blame(repo_path, ref="HEAD", file_path=""):
    repo = git.Repository(repo_path)
    obj = repo.revparse_single(ref)
    # TODO: doesnt work with tree refs
    if obj.type == git.GIT_OBJECT_COMMIT:
        commit = obj
    else:
        commit = obj.peel(git.GIT_OBJECT_COMMIT)

    # traverse to the blob path
    # TODO: make this common across more modules
    tree = commit.tree
    blob = None
    if file_path:
        parts = file_path.rstrip('/').split('/')
        for part in parts:
            found = False
            for entry in tree:
                if entry.name == part:
                    if entry.type == git.GIT_OBJECT_BLOB:
                        blob = repo.get(entry.id)
                        found = True
                        break
                    elif entry.type == git.GIT_OBJECT_TREE:
                        tree = repo.get(entry.id)
                        found = True
                        break
            if not found:
                return None  # path not found
    if blob is None:
        return None

    blame = repo.blame(file_path)
    
    # get blob content lines directly. maybe later use lines_in_hunk
    content_lines = blob.data.decode('utf-8', errors='replace').splitlines()
    
    # create a list to hold blame info per line
    blame_lines = [None] * len(content_lines)
    for hunk in blame:
        # https://libgit2.org/docs/reference/main/blame/git_blame_hunk.html
        start = hunk.final_start_line_number - 1  # to 0 index, since using python lists
        end = start + hunk.lines_in_hunk
        commit = repo.get(hunk.final_commit_id)  # last commit oid
        # TODO: more info if needed
        info = {
            'commit_id': str(hunk.final_commit_id),
            'author': commit.author,
        }
        # fill premade info for lines in this hunk
        for i in range(start, min(end, len(blame_lines))): # prevent index overflow, with min
            blame_lines[i] = info
    
    # combine content lines with their blame info
    result = []
    for i, line in enumerate(content_lines):
        result.append({
            'line_num': i + 1,
            'content': line,
            'blame': blame_lines[i]
        })
    
    return result