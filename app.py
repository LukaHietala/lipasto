import os
from flask import Flask, render_template, request
from datetime import datetime
from dotenv import load_dotenv

from git.repo import get_bare_repos
from git.commit import get_commits, get_commit
from git.ref import get_refs
from git.tree import get_tree_items
from git.blob import get_blob
from git.misc import get_version
from git.diff import get_diff
from git.blame import get_blame
from highlight import highlight_diff

load_dotenv()

app = Flask(__name__)

# for base.html
app.jinja_env.globals['request'] = request

@app.context_processor
def inject_current_ref():
    return {'current_ref': request.args.get('ref', 'HEAD')}

repo_path = os.getenv('GIT_REPO_PATH')

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

# age filter to show relative time like "2 days ago" 
def age_filter(value):
    if isinstance(value, (int, float)):
        dt = datetime.fromtimestamp(value)
    elif isinstance(value, datetime):
        dt = value
    else:
        return value
    now = datetime.now()
    diff = now - dt
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "just now"

app.jinja_env.filters['datetime'] = datetime_filter
app.jinja_env.filters['age'] = age_filter

@app.route("/")
def index():
    repos = get_bare_repos(repo_path)
    version = get_version()
    return render_template("index.html", repos=repos, version=version)

@app.route("/<repo_name>")
def repo_detail(repo_name):
    commits = get_commits(f"{repo_path}/{repo_name}", ref="HEAD", max_count=10)
    refs = get_refs(f"{repo_path}/{repo_name}")
    return render_template("repo.html", repo_name=repo_name, refs=refs, commits=commits)

@app.route("/<repo_name>/commits")
def repo_commits(repo_name):
    ref = request.args.get('ref', 'HEAD')
    refs = get_refs(f"{repo_path}/{repo_name}")
    page = int(request.args.get('page', 0))
    # maybe pages are not the wisest way to do this?
    per_page = 50
    skip = page * per_page

    commits = get_commits(f"{repo_path}/{repo_name}", ref=ref, max_count=per_page, skip=skip)
    has_next = len(commits) == per_page
    has_prev = page > 0
    return render_template("commits.html", repo_name=repo_name, commits=commits, page=page, has_next=has_next, has_prev=has_prev, ref=ref, refs=refs)

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
    refs = get_refs(f"{repo_path}/{repo_name}")
    tree_items = get_tree_items(f"{repo_path}/{repo_name}", ref, path)
    return render_template("tree.html", repo_name=repo_name, ref=ref, path=path, tree_items=tree_items, refs=refs)

@app.route("/<repo_name>/blob/<path:path>")
def repo_blob_path(repo_name, path):
    ref = request.args.get('ref', 'HEAD')
    refs = get_refs(f"{repo_path}/{repo_name}")
    blob = get_blob(f"{repo_path}/{repo_name}", ref, path)
    return render_template("blob.html", repo_name=repo_name, ref=ref, path=path, blob=blob, refs=refs)

@app.route("/<repo_name>/blame/<path:path>")
def repo_blame_path(repo_name, path):
    ref = request.args.get('ref', 'HEAD')
    refs = get_refs(f"{repo_path}/{repo_name}")
    blame, style = get_blame(f"{repo_path}/{repo_name}", ref, path)
    return render_template("blame.html", repo_name=repo_name, ref=ref, path=path, blame=blame, refs=refs, style=style)

@app.route("/<repo_name>/diff")
def repo_diff(repo_name):
    refs = get_refs(f"{repo_path}/{repo_name}")
    id1 = request.args.get('id1')
    id2 = request.args.get('id2')
    context_lines = int(request.args.get('context_lines', 3))
    interhunk_lines = int(request.args.get('interhunk_lines', 0))
    # TODO: ADD ERROR HANDLING EVERYWHERE!!
    try:
        diff = get_diff(f"{repo_path}/{repo_name}", id1=id1, id2=id2, context_lines=context_lines, interhunk_lines=interhunk_lines)
        highlighted_patch = highlight_diff(diff['patch'])
        return render_template("diff.html", diff=diff, refs=refs, context_lines=context_lines, interhunk_lines=interhunk_lines, highlighted_patch=highlighted_patch)
    except ValueError as e:
        return render_template("diff.html", error=str(e), refs=refs, context_lines=context_lines, interhunk_lines=interhunk_lines)
    except Exception as e:
        return render_template("diff.html", error="Server error", refs=refs, context_lines=context_lines, interhunk_lines=interhunk_lines)
if __name__ == "__main__":
    app.run(debug=True)