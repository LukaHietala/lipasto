package main 

import (
	"net/http"
	"fmt"
	"log"
)

func main() {
	mux := http.NewServeMux()
	
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprint(w, "Hello! 🐹")
    })

	port := ":8080"
	server := &http.Server{
		Addr: ":8080",
		Handler: mux,
	}
	log.Printf("Listening on %s\n", port)
	log.Fatal(server.ListenAndServe())
}

