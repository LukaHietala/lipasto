package main

import (
	"html/template"
	"log"
	"net/http"

	"github.com/lukahietala/lipasto/git"
)

func main() {
	tmpl, err := template.ParseGlob("./templates/*.html")
	if err != nil {
		log.Fatalf("Unable to parse templates: %v\n", err)
	}

	mux := http.NewServeMux()

	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		repos, err := git.ListRepositories("/tmp/repos")
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
		Handler: mux,
	}

	log.Printf("Listening on %s\n", port)
	log.Fatal(server.ListenAndServe())
}
