package main

import (
	"html/template"
	"log"
	"net/http"
	"time"

	"github.com/dustin/go-humanize"
	"github.com/lukahietala/lipasto/git"
)

type loggingResponseWriter struct {
	http.ResponseWriter
	statusCode int
}

// TODO: Hacky method shadowing so maybe refactor if possible
func (lrw *loggingResponseWriter) WriteHeader(code int) {
	lrw.statusCode = code
	lrw.ResponseWriter.WriteHeader(code)
}

func logger(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()

		lrw := &loggingResponseWriter{w, http.StatusOK}

		next.ServeHTTP(lrw, r)

		log.Printf(
			"%s %s %d %s",
			r.Method,
			r.URL.Path,
			lrw.statusCode,
			time.Since(start),
		)
	})
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

	mux := http.NewServeMux()

	fs := http.FileServer(http.Dir("./static"))
	mux.Handle("/static/", http.StripPrefix("/static/", fs))

	mux.HandleFunc("GET /{$}", func(w http.ResponseWriter, r *http.Request) {
		repos, err := git.ListRepositories("/tmp/git-test/")
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		err = tmpl.ExecuteTemplate(w, "index.html", map[string]any{
			"Repos": repos,
		})
		if err != nil {
			log.Printf("%v", err)
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
	})

	port := ":8080"
	server := &http.Server{
		Addr:    port,
		Handler: logger(mux),
	}

	log.Printf("Listening on %s\n", port)
	log.Fatal(server.ListenAndServe())
}
