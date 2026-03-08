package git

import (
	"os"
	"path/filepath"
	"strings"

	gogit "github.com/go-git/go-git/v6"
)

type Repository struct {
	// Name of the repository, derived from Path
	Name string
	// Path to the repo on disk
	Path string
	// Gogit repository representation
	*gogit.Repository
}

// ListRepositories finds all repos in a directory
func ListRepositories(root string) ([]*Repository, error) {
	var repos []*Repository

	paths, err := os.ReadDir(root)
	if err != nil {
		return nil, err
	}

	for _, path := range paths {
		if !path.IsDir() {
			continue
		}
		repoPath := filepath.Join(root, path.Name())

		r, err := gogit.PlainOpen(repoPath)
		if err == nil {
			repos = append(repos, &Repository{
				// TODO?: With .git it looks cooler, so maybe change
				Name:       strings.TrimSuffix(path.Name(), ".git"),
				Path:       repoPath,
				Repository: r,
			})
		}
	}

	return repos, nil
}

// LatestCommit returns the latest commit pointed to by HEAD
func (r *Repository) LatestCommit() (*Commit, error) {
	ref, err := r.Head()
	if err != nil {
		return nil, err
	}

	obj, err := r.CommitObject(ref.Hash())
	if err != nil {
		return nil, err
	}

	return &Commit{
		Commit: obj,
	}, nil
}
