import pygit2 as git

# retrieves commit history for given repo path and reference
def get_commits(path, ref="HEAD", max_count=None):
    repo = git.Repository(path)
    commits = []
    walker = repo.walk(repo.revparse_single(ref).id, git.GIT_SORT_TIME)

    n = 0
    for commit in walker:
        if max_count is not None and n >= max_count:
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

# retrieves a single commit by its hash
def get_commit(path, commit_hash):
    repo = git.Repository(path)
    commit = repo.revparse_single(commit_hash)

    if len(commit.parents) > 0:
        diff = repo.diff(commit.parents[0], commit)
        stats = diff.stats
        diff_stats = {
            'insertions': stats.insertions,
            'deletions': stats.deletions,
            'files_changed': stats.files_changed
        }
    else:
        diff_stats = {
            'insertions': 0,
            'deletions': 0,
            'files_changed': 0
        }
        diff = None

    commit_info = {
        'id': str(commit.id),
        'message': commit.message.strip(),
        'author': commit.author,
        'committer': commit.committer,
        'date': commit.commit_time,
        'diff_stats': diff_stats,
        'diff': diff.patch if diff else None
    }
    return commit_info