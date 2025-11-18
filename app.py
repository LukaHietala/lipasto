from flask import Flask, render_template, request

from git.repo import get_bare_repos
from git.commit import get_commits, get_commit

app = Flask(__name__)

repo_path = "/home/lhietala/git-webview/repos-example"
@app.route("/")
def index():
    repos = get_bare_repos(repo_path)
    return render_template("index.html", repos=repos)

@app.route("/<repo_name>/commits")
def repo_commits(repo_name):
    ref = request.args.get('ref', 'HEAD')

    commits = get_commits(f"{repo_path}/{repo_name}", ref=ref, max_count=50)
    return render_template("commits.html", repo_name=repo_name, commits=commits)

@app.route("/<repo_name>/commits/<commit_hash>")
def commit_detail(repo_name, commit_hash):
    commit = get_commit(f"{repo_path}/{repo_name}", commit_hash)
    return render_template("commit.html", repo_name=repo_name, commit=commit)

if __name__ == "__main__":
    app.run(debug=True)