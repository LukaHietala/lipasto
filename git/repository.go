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

// LastUpdated returns the date when the latest commit was made
func (r *Repository) LastUpdated() time.Time {
	commit, err := r.LatestCommit()
	if err != nil || commit == nil {
		return time.Time{}
	}
	return commit.Author.When
}

// Commits returns a paginated slice of commits and a boolean indicating if more commits exist
func (r *Repository) Commits(hash plumbing.Hash, page int, pageSize int) ([]*Commit, bool, error) {
	cIter, err := r.raw.Log(&gogit.LogOptions{
		From:  hash,
		Order: gogit.LogOrderCommitterTime,
	})
	if err != nil {
		return nil, false, err
	}
	defer cIter.Close()

	var commits []*Commit
	skip := (page - 1) * pageSize
	hasNext := false

	for i := 0; ; i++ {
		c, err := cIter.Next()
		if err != nil {
			if err == io.EOF {
				break
			}
			return nil, false, err
		}

		// Skip commits until on right page
		if i < skip {
			continue
		}

		if len(commits) == pageSize {
			hasNext = true
			break
		}

		commits = append(commits, &Commit{Commit: c})
	}

	return commits, hasNext, nil
}

// GetCommit returns a Commit based on hash
func (r *Repository) GetCommit(hash string) (*Commit, error) {
	h := plumbing.NewHash(hash)

	obj, err := r.raw.CommitObject(h)
	if err != nil {
		return nil, err
	}

	return &Commit{
		Commit: obj,
	}, nil
}

// ResolveRevision resolves a generic string (hash, short branch name, tag, or full ref)
// and returns the corresponding commit
func (r *Repository) ResolveRevision(rev string) (*Commit, error) {
	hash, err := r.raw.ResolveRevision(plumbing.Revision(rev))
	if err != nil {
		return nil, err
	}

	obj, err := r.raw.CommitObject(*hash)
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
