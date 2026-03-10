package git

import (
	"errors"
	"io"
	"os"
	"path/filepath"
	"strings"
	"time"

	gogit "github.com/go-git/go-git/v6"
	"github.com/go-git/go-git/v6/plumbing"
)

var (
	ErrRepositoryNotFound = errors.New("repository not found")
)

type Repository struct {
	// Name of the repository, derived from Path
	Name string
	// Path to the repo on disk
	Path string
	// Gogit repository representation
	raw *gogit.Repository
}

// CurrentHead returns HEAD reference
func (r *Repository) CurrentHead() (*Reference, error) {
	ref, err := r.raw.Head()
	if err != nil {
		return nil, err
	}
	return &Reference{Reference: ref}, nil
}

// LatestCommit returns the latest commit pointed to by HEAD
func (r *Repository) LatestCommit() (*Commit, error) {
	ref, err := r.raw.Head()
	if err != nil {
		if errors.Is(err, plumbing.ErrReferenceNotFound) {
			return nil, nil // Empty repo
		}
		return nil, err
	}

	obj, err := r.raw.CommitObject(ref.Hash())
	if err != nil {
		return nil, err
	}

	return &Commit{
		Commit: obj,
	}, nil
}

func (r *Repository) LastUpdated() time.Time {
	commit, err := r.LatestCommit()
	if err != nil || commit == nil {
		return time.Time{}
	}
	return commit.Author.When
}

// TODO: Add pagination
// Commits returns slice of commits in repo reference
func (r *Repository) Commits(ref *Reference) ([]*Commit, error) {
	cIter, err := r.raw.Log(&gogit.LogOptions{
		From:  ref.Hash(),
		Order: gogit.LogOrderCommitterTime,
	})
	if err != nil {
		return nil, err
	}
	defer cIter.Close()

	var commits []*Commit

	// Normally go-git's ForEach shoud be used but that's disgusting
	for {
		c, err := cIter.Next()
		if err != nil {
			if err == io.EOF {
				break
			}
			return nil, err
		}

		commits = append(commits, &Commit{
			Commit: c,
		})
	}

	return commits, nil
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
	cfg, err := r.raw.Config()
	if err != nil {
		return "", err
	}

	// Looks for:
	// [gitweb]
	//     owner = "Laukkaava pomeranian"
	return cfg.Raw.Section("gitweb").Option("owner"), nil
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
				Name: strings.TrimSuffix(path.Name(), ".git"),
				Path: repoPath,
				raw:  r,
			})
		}
	}

	return repos, nil
}

// TODO: Slow and unreliable garbage
// FindRepository tries to find repository from directory
func FindRepository(root string, name string) (*Repository, error) {
	repos, err := ListRepositories(root)
	if err != nil {
		return nil, err
	}
	for _, repo := range repos {
		if repo.Name == name {
			return repo, nil
		}
	}
	return nil, ErrRepositoryNotFound
}
