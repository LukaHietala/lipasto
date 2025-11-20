import pygit2 as git

# compares two refs and return diff stats per file and full patch
def get_diff(path, id1, id2, context_lines=3, interhunk_lines=0, **options):
    repo = git.Repository(path)
    if not id1:
        id1 = 'HEAD~1' # default to previous commit
    if not id2:
        id2 = 'HEAD'
    try:
        ref_one = repo.revparse_single(id1).peel(git.Commit)  # potential older, HOPEFULLY
        ref_two = repo.revparse_single(id2).peel(git.Commit)  # potential newer, HOPEFULLY
    except Exception as e:
        raise ValueError(f"Invalid ref: {id1} or {id2}. Error: {str(e)}")
    
    # make sure that ref_one (from) is older than ref_two (to), swap if necessary
    if ref_one.commit_time > ref_two.commit_time:
        ref_one, ref_two = ref_two, ref_one
        id1, id2 = id2, id1
    
    diff = repo.diff(ref_one, ref_two, context_lines=context_lines, interhunk_lines=interhunk_lines, **options)

    # detect renames and copies, if not they are just deletions and additions
    # rename and copy thresholds are 50% by default in libgit2
    # https://libgit2.org/docs/reference/main/diff/git_diff_find_options.html
    # debating whether to keep or remove this, but for now it's useful. or atleast alter the default thresholds
    diff.find_similar()

    # map libgit2 delta status to human readable, most not used, but good to have them all here
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

    patches = list(diff)
    deltas = diff.deltas
    changed_files = []

    for i, delta in enumerate(deltas):
        patch = patches[i]
        file_path = delta.new_file.path if delta.new_file.path else delta.old_file.path
        # insertions and deletions in diff stats and additions and deletions in delta line stats. little confusing 
        _, additions, deletions = patch.line_stats # (context, additions, deletions)
        status_str = status_map.get(delta.status, 'unknown')
        changed_files.append({
            'file': file_path,
            'additions': additions,
            'deletions': deletions,
            'status': status_str
        })

    return {
        'patch': diff.patch,
        'files': changed_files,
        'ref1_id': str(ref_one.id),
        'ref2_id': str(ref_two.id),
        'ref1': id1,
        'ref2': id2
    }


