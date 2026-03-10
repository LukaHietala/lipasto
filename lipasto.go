package main

import (
	"bytes"
	"errors"
	"html/template"
	"log"
	"net/http"
	"time"

	"github.com/dustin/go-humanize"
	"github.com/go-git/go-git/v6/plumbing"
	"github.com/lukahietala/lipasto/git"
)

// TODO: Common error handling

const root = "/tmp/git-test/"

type app struct {
	tmpl *template.Template
}

func (app *app) handleIndex(w http.ResponseWriter, r *http.Request) {
	repos, err := git.ListRepositories(root)
	if err != nil {
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		log.Printf("%v", err)
		return
	}

	var buf bytes.Buffer
	err = app.tmpl.ExecuteTemplate(&buf, "index.html", map[string]any{
		"Repos": repos,
	})
	if err != nil {
		log.Printf("%v", err)
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	buf.WriteTo(w)
}

func (app *app) handleCommits(w http.ResponseWriter, r *http.Request) {
	name := r.PathValue("repo")

	repo, err := git.FindRepository(root, name)
	if err != nil {
		if errors.Is(err, git.ErrRepositoryNotFound) {
			http.Error(w, "Repository not found", http.StatusBadRequest)
		} else {
			log.Printf("%v", err)
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		}
		return
	}

	var commits []*git.Commit
	// TODO: Make resolve ref and take ?ref query param
	head, err := repo.CurrentHead()
	if err != nil {
		if errors.Is(err, plumbing.ErrReferenceNotFound) {
			head = nil
		} else {
			// Should not happen
			http.Error(w, "Could not determine HEAD", http.StatusInternalServerError)
			return
		}
	}

	if head != nil {
		commits, err = repo.Commits(head)
		if err != nil {
			http.Error(w, "Unable to list commits", http.StatusInternalServerError)
			return
		}
	}
	var buf bytes.Buffer
	err = app.tmpl.ExecuteTemplate(&buf, "commits.html", map[string]any{
		"Commits": commits,
	})
	if err != nil {
		log.Printf("%v", err)
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}

	buf.WriteTo(w)
}

func humanizeTime(t time.Time) string {
	if t.IsZero() {
		return "never"
	}
	return humanize.Time(t)
}

func main() {
	funcMap := template.FuncMap{
		"humanizeTime":  humanizeTime,
		"humanizeBytes": humanize.Bytes,
	}

	tmpl, err := template.New("base").Funcs(funcMap).ParseGlob("./templates/*.html")
	if err != nil {
		log.Fatalf("Unable to parse templates: %v\n", err)
	}

	app := &app{
		tmpl: tmpl,
	}

	mux := http.NewServeMux()

	fs := http.FileServer(http.Dir("./static"))
	mux.Handle("GET /static/", http.StripPrefix("/static/", fs))

	mux.HandleFunc("GET /{$}", app.handleIndex)
	// Mux screams about conflict with static if not promoted to /r/
	mux.HandleFunc("GET /r/{repo}/commits/{$}", app.handleCommits)

	port := ":8080"
	server := &http.Server{
		Addr:    port,
		Handler: withLogging(mux),
	}

	log.Printf("Listening on %s\n", port)
	if err := server.ListenAndServe(); err != nil {
		log.Fatalf("%v", err)
	}
}
