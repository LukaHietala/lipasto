package main

import (
	"bytes"
	"html/template"
	"log"
	"net/http"

	"github.com/dustin/go-humanize"
	"github.com/lukahietala/lipasto/git"
)

// TODO: Common error handling

type app struct {
	tmpl *template.Template
}

func (app *app) handleIndex(w http.ResponseWriter, r *http.Request) {
	repos, err := git.ListRepositories("/tmp/git-test/")
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

func main() {
	funcMap := template.FuncMap{
		"humanizeTime":  humanize.Time,
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
	mux.Handle("/static/", http.StripPrefix("/static/", fs))

	mux.HandleFunc("GET /{$}", app.handleIndex)

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
