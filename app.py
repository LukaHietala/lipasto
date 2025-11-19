from flask import Flask, render_template, request
from datetime import datetime

from git.repo import get_bare_repos
from git.commit import get_commits, get_commit
from git.ref import get_refs
from git.tree import get_tree_items
from git.blob import get_blob
from git.misc import get_version
from git.diff import get_diff
from git.blame import get_blame

app = Flask(__name__)

def datetime_filter(value, format='%Y-%m-%d %H:%M:%S'):
    if isinstance(value, datetime):
        # format regular datetime 
        return value.strftime(format)
    elif isinstance(value, (int, float)):
        # if not datetime, but number, try to convert
        # just assume its unix timestamp, git uses that
        dt = datetime.fromtimestamp(value)
        return dt.strftime(format)
    return value

app.jinja_env.filters['datetime'] = datetime_filter

repo_path = "/home/lhietala/git-webview/repos-example"
@app.route("/")
def index():
    repos = get_bare_repos(repo_path)
    version = get_version()
    return render_template("index.html", repos=repos, version=version)

@app.route("/<repo_name>/commits")
def repo_commits(repo_name):
    ref = request.args.get('ref', 'HEAD')
    page = int(request.args.get('page', 0))
    # maybe pages are not the wisest way to do this?
    per_page = 50
    skip = page * per_page

    commits = get_commits(f"{repo_path}/{repo_name}", ref=ref, max_count=per_page, skip=skip)
    has_next = len(commits) == per_page
    has_prev = page > 0
    return render_template("commits.html", repo_name=repo_name, commits=commits, page=page, has_next=has_next, has_prev=has_prev, ref=ref)

@app.route("/<repo_name>/commits/<commit_id>")
def commit_detail(repo_name, commit_id):
    commit = get_commit(f"{repo_path}/{repo_name}", commit_id)
    return render_template("commit.html", repo_name=repo_name, commit=commit)

@app.route("/<repo_name>/refs")
def repo_refs(repo_name):
    refs = get_refs(f"{repo_path}/{repo_name}")
    return render_template("refs.html", repo_name=repo_name, refs=refs)

@app.route("/<repo_name>/tree", defaults={'path': ''})
@app.route("/<repo_name>/tree/<path:path>")
def repo_tree_path(repo_name, path):
    ref = request.args.get('ref', 'HEAD')
    tree_items = get_tree_items(f"{repo_path}/{repo_name}", ref, path)
    return render_template("tree.html", repo_name=repo_name, ref=ref, path=path, tree_items=tree_items)

@app.route("/<repo_name>/blob/<path:path>")
def repo_blob_path(repo_name, path):
    ref = request.args.get('ref', 'HEAD')
    blob = get_blob(f"{repo_path}/{repo_name}", ref, path)
    return render_template("blob.html", repo_name=repo_name, ref=ref, path=path, blob=blob)

@app.route("/<repo_name>/blame/<path:path>")
def repo_blame_path(repo_name, path):
    ref = request.args.get('ref', 'HEAD')
    blame = get_blame(f"{repo_path}/{repo_name}", ref, path)
    return render_template("blame.html", repo_name=repo_name, ref=ref, path=path, blame=blame)

@app.route("/<repo_name>/diff")
def repo_diff(repo_name):
    id1 = request.args.get('id1', 'HEAD')
    id2 = request.args.get('id2', 'HEAD')
    diff = get_diff(f"{repo_path}/{repo_name}", id1=id1, id2=id2)
    return render_template("diff.html", diff=diff)
    
if __name__ == "__main__":
    app.run(debug=True)