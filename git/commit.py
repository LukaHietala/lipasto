import pygit2 as git

# map libgit2 delta status to human readable
status_map = {
    git.GIT_DELTA_ADDED: 'added',
    git.GIT_DELTA_DELETED: 'deleted',
    git.GIT_DELTA_MODIFIED: 'modified',
    git.GIT_DELTA_RENAMED: 'renamed',
    git.GIT_DELTA_COPIED: 'copied',
    git.GIT_DELTA_IGNORED: 'ignored',
    git.GIT_DELTA_UNTRACKED: 'untracked',
    git.GIT_DELTA_TYPECHANGE: 'typechange',
    git.GIT_DELTA_UNREADABLE: 'unreadable',
    git.GIT_DELTA_CONFLICTED: 'conflicted'
}

# retrieves commit history for given repo path and reference
def get_commits(path, ref="HEAD", max_count=None, skip=0):
    repo = git.Repository(path)
    commits = []
    # TODO: accept blob oids to filter commits that touch specific blobs
    obj = repo.revparse_single(ref)
    if obj.type == git.GIT_OBJECT_COMMIT:
        commit = obj
    else:
        commit = obj.peel(git.GIT_OBJECT_COMMIT)
    walker = repo.walk(commit.id, git.GIT_SORT_TIME)

    n = 0
    for commit in walker:
        # pagination, 50 per page, walk until skip, then collect commits until max_count
        if n < skip:
            n += 1
            continue
        if max_count is not None and (n - skip) >= max_count:
            break
        if len(commit.parents) > 0:
            # get diif stats against first parent
            # libgit2 has very fast diff stats calculation, using that here
            diff = repo.diff(commit.parents[0], commit)
            stats = diff.stats
            diff_stats = {
                'insertions': stats.insertions,
                'deletions': stats.deletions,
                'files_changed': stats.files_changed
            }
        else:
            # TODO: compare to NULL_TREE
            diff_stats = {
                'insertions': 0,
                'deletions': 0,
                'files_changed': 0
            }
        commit_info = {
            'id': str(commit.id),
            'message': commit.message.strip(),
            'author': commit.author,
            'committer': commit.committer,
            'date': commit.commit_time,
            'diff_stats': diff_stats
        }
        commits.append(commit_info)
        n += 1
    return commits

# retrieves a single commit by its id
def get_commit(path, commit_id):
    repo = git.Repository(path)
    commit = repo.revparse_single(commit_id)

    if len(commit.parents) > 0:
        diff = repo.diff(commit.parents[0], commit)
        stats = diff.stats
        diff_stats = {
            'insertions': stats.insertions,
            'deletions': stats.deletions,
            'files_changed': stats.files_changed
        }
        # detect renames and copies
        diff.find_similar()
        patches = list(diff)
        deltas = diff.deltas
        changed_files = []
        for i, delta in enumerate(deltas):
            patch = patches[i]
            file_path = delta.new_file.path if delta.new_file.path else delta.old_file.path
            _, additions, deletions = patch.line_stats
            status_str = status_map.get(delta.status, 'unknown')
            changed_files.append({
                'file': file_path,
                'additions': additions,
                'deletions': deletions,
                'status': status_str
            })
    else:
        diff_stats = {
            'insertions': 0,
            'deletions': 0,
            'files_changed': 0
        }
        diff = None
        changed_files = []

    commit_info = {
        'id': str(commit.id),
        'message': commit.message.strip(),
        'author': commit.author,
        'committer': commit.committer,
        'tree_id': str(commit.tree.id),
        'parent_id': str(commit.parents[0].id) if commit.parents else None,
        'date': commit.commit_time,
        'diff_stats': diff_stats,
        'diff': diff.patch if diff else None,
        'changed_files': changed_files
    }
    return commit_info