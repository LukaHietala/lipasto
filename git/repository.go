package git

import (
	gogit "github.com/go-git/go-git/v6"
	"io/fs"
	"path/filepath"
)

type Repository struct {
	// Path to the repo on disk
	Path string
	// Gogit repository representation
	gogitRepo *gogit.Repository
}

// Returns a slice of all repositories in spesified directory
func ListRepositories(root string) ([]*Repository, error) {
	var repos []*Repository
	err := filepath.WalkDir(root, func(path string, d fs.DirEntry, err error) error {
		if err != nil || !d.IsDir() {
			return nil
		}
		// Make sure it's a valid git repo
		r, err := gogit.PlainOpen(path)
		if err == nil {
			repos = append(repos, &Repository{
				Path:      path,
				gogitRepo: r,
			})
			// Don't go any deeper
			return filepath.SkipDir
		}
		return nil
	})
	return repos, err
}
