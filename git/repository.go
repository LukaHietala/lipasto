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

// Git's placeholder description
const defaultDescription = "Unnamed repository; edit this file 'description' to name the repository."

// Description returns the repo description found in file ".git/description" or "description"
func (r *Repository) Description() (string, error) {
	// On bare repos
	descPath := filepath.Join(r.Path, "description")

	// On regular repos (TODO?: Don't support regular repos)
	if _, err := os.Stat(descPath); os.IsNotExist(err) {
		descPath = filepath.Join(r.Path, ".git", "description")
	}

	data, err := os.ReadFile(descPath)
	if err != nil {
		if os.IsNotExist(err) {
			return "", nil
		}
		return "", err
	}
	desc := strings.TrimSpace(string(data))

	if desc == defaultDescription {
		return "", nil
	}

	return desc, nil
}

// Owner returns owner definded in .git/config (gitweb.owner)
func (r *Repository) Owner() (string, error) {
	cfg, err := r.Config()
	if err != nil {
		return "", err
	}

	// Looks for:
	// [gitweb]
	//     owner = "Laukkaava pomeranian"
	return cfg.Raw.Section("gitweb").Option("owner"), nil
}
