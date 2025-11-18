from flask import Flask, render_template

from git.repo import get_bare_repos

app = Flask(__name__)

@app.route("/")
def index():
    repos = get_bare_repos("/home/lhietala/git-webview/repos-example")
    return render_template("index.html", repos=repos)

if __name__ == "__main__":
    app.run(debug=True)