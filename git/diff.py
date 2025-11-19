import pygit2 as git

# compares two refs and return diff
# TODO: per file, now just full hunk, per file stats, and no changes to compare.
def get_diff(path, id1="HEAD", id2="HEAD"):
    repo = git.Repository(path)
    ref_one = repo.revparse_single(id1)
    ref_two = repo.revparse_single(id2)
    diff = repo.diff(ref_one, ref_two)

    return diff.patch


