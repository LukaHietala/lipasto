package main

import (
	"fmt"
	"log"
	"net/http"
	"strings"

	"github.com/lukahietala/lipasto/git"
)

func main() {
	mux := http.NewServeMux()

	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprint(w, "Hello! 🐹")
		repos, err := git.ListRepositories("/tmp/repos")
		if err != nil {
			http.Error(w, fmt.Sprintf("Failed to fetch repos: %v", err), http.StatusInternalServerError)
			return
		}
		paths := make([]string, 0, len(repos))
		for _, r := range repos {
			paths = append(paths, r.Path)
		}
		fmt.Fprintf(w, "%v", strings.Join(paths, ", "))
	})

	port := ":8080"
	server := &http.Server{
		Addr:    ":8080",
		Handler: mux,
	}
	log.Printf("Listening on %s\n", port)
	log.Fatal(server.ListenAndServe())
}
