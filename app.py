import os
import subprocess
from flask import Flask, render_template, request, abort
from dotenv import load_dotenv

from git.repository import get_bare_repos
from git.commit import get_commits, get_commit
from git.reference import get_references
from git.tree import get_tree_items
from git.blob import get_blob
from git.misc import get_version, validate_repo_name, validate_ref, validate_ref_as_commit, sanitize_path
from git.diff import get_diff
from git.blame import get_blame
from highlight import highlight_diff
from filters import register_filters

load_dotenv()

app = Flask(__name__)

# for base.html
app.jinja_env.globals['request'] = request
register_filters(app)

@app.context_processor
def inject_current_ref():
    ref = request.args.get('ref', 'HEAD').strip()
    # if ref is invalid, default to HEAD to prevent broken links
    repo_name = request.view_args.get('repo_name') if request.view_args else None
    if repo_name:
        try:
            if not validate_ref_as_commit(f"{repo_path}/{repo_name}", ref):
                ref = 'HEAD'
        except:
            ref = 'HEAD'
    return {'current_ref': ref}

repo_path = os.getenv('GIT_REPO_PATH')

@app.route("/")
def index():
    repos = get_bare_repos(repo_path)
    version = get_version()
    return render_template("index.html", repos=repos, version=version)

@app.route("/<repo_name>")
def repo_detail(repo_name):
    if not validate_repo_name(repo_name):
        abort(404)
    ref = request.args.get('ref', 'HEAD').strip()
    if not validate_ref_as_commit(f"{repo_path}/{repo_name}", ref):
        abort(400, "Invalid ref")
    commits = get_commits(f"{repo_path}/{repo_name}", ref=ref, max_count=10)
    refs = get_references(f"{repo_path}/{repo_name}")
    readme = None
    for filename in ['README.md', 'README']:
        try:
            readme_blob = get_blob(f"{repo_path}/{repo_name}", ref, filename)
            if readme_blob:
                readme = readme_blob['content']
                break
        except:
            pass
    return render_template("overview.html", repo_name=repo_name, refs=refs, commits=commits, readme=readme)

@app.route("/<repo_name>/commits")
def repo_commits(repo_name):
    if not validate_repo_name(repo_name):
        abort(404)
    ref = request.args.get('ref', 'HEAD').strip()
    if not validate_ref_as_commit(f"{repo_path}/{repo_name}", ref):
        abort(400, "Invalid ref")
    refs = get_references(f"{repo_path}/{repo_name}")
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
    if not validate_repo_name(repo_name):
        abort(404)
    if not validate_ref_as_commit(f"{repo_path}/{repo_name}", commit_id):
        abort(400, "Invalid commit id")
    commit = get_commit(f"{repo_path}/{repo_name}", commit_id)
    return render_template("commit.html", repo_name=repo_name, commit=commit)

@app.route("/<repo_name>/patch/<commit_id>")
def commit_patch(repo_name, commit_id):
    if not validate_repo_name(repo_name):
        abort(404)
    if not validate_ref_as_commit(f"{repo_path}/{repo_name}", commit_id):
        abort(400, "Invalid commit id")
    # Use git format-patch to generate the patch
    result = subprocess.run(['git', '--git-dir', f"{repo_path}/{repo_name}", 'format-patch', '-1', '--stdout', commit_id], 
                            capture_output=True, text=True, encoding='utf-8')
    # git leaves encoded headers like =?UTF-8?Q?...?=, but that should be fine for patch view for now, TODO 
    if result.returncode != 0:
        abort(500, f"Failed to generate patch: {result.stderr}")
    return result.stdout, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route("/<repo_name>/refs")
def repo_refs(repo_name):
    if not validate_repo_name(repo_name):
        abort(404)
    refs = get_references(f"{repo_path}/{repo_name}")
    return render_template("refs.html", repo_name=repo_name, refs=refs)

@app.route("/<repo_name>/tree", defaults={'path': ''})
@app.route("/<repo_name>/tree/<path:path>")
def repo_tree_path(repo_name, path):
    if not validate_repo_name(repo_name):
        abort(404)
    ref = request.args.get('ref', 'HEAD').strip()
    if not validate_ref(f"{repo_path}/{repo_name}", ref):
        abort(400, "Invalid ref")
    try:
        path = sanitize_path(path)
    except ValueError:
        abort(400, "Invalid path")
    refs = get_references(f"{repo_path}/{repo_name}")
    tree_items = get_tree_items(f"{repo_path}/{repo_name}", ref, path)
    return render_template("tree.html", repo_name=repo_name, ref=ref, path=path, tree_items=tree_items, refs=refs)

@app.route("/<repo_name>/blob/<path:path>")
def repo_blob_path(repo_name, path):
    if not validate_repo_name(repo_name):
        abort(404)
    ref = request.args.get('ref', 'HEAD').strip()
    if not validate_ref(f"{repo_path}/{repo_name}", ref):
        abort(400, "Invalid ref")
    try:
        path = sanitize_path(path)
    except ValueError:
        abort(400, "Invalid path")
    refs = get_references(f"{repo_path}/{repo_name}")
    blob = get_blob(f"{repo_path}/{repo_name}", ref, path)
    return render_template("blob.html", repo_name=repo_name, ref=ref, path=path, blob=blob, refs=refs)

@app.route("/<repo_name>/blame/<path:path>")
def repo_blame_path(repo_name, path):
    if not validate_repo_name(repo_name):
        abort(404)
    ref = request.args.get('ref', 'HEAD').strip()
    if not validate_ref(f"{repo_path}/{repo_name}", ref):
        abort(400, "Invalid ref")
    try:
        path = sanitize_path(path)
    except ValueError:
        abort(400, "Invalid path")
    refs = get_references(f"{repo_path}/{repo_name}")
    
    # if ajax (for loading)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        blame, style = get_blame(f"{repo_path}/{repo_name}", ref, path)
        return {'blame': blame, 'style': style}
    
    # initial
    return render_template("blame.html", repo_name=repo_name, ref=ref, path=path, refs=refs)

@app.route("/<repo_name>/diff")
def repo_diff(repo_name):
    if not validate_repo_name(repo_name):
        abort(404)
    refs = get_references(f"{repo_path}/{repo_name}")
    id1 = request.args.get('id1')
    id2 = request.args.get('id2')
    if id1 and not validate_ref_as_commit(f"{repo_path}/{repo_name}", id1):
        abort(400, "Invalid id1 (reference from)")
    if id2 and not validate_ref_as_commit(f"{repo_path}/{repo_name}", id2):
        abort(400, "Invalid id2 (reference to)")
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