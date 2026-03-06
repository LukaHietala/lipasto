package git

import (
	"os"
	"path/filepath"
	"testing"

	gogit "github.com/go-git/go-git/v6"
)

func TestListRepositories(t *testing.T) {
	tmpRoot := t.TempDir()

	// Valid repo
	repoPath := filepath.Join(tmpRoot, "real-repo")
	_, err := gogit.PlainInit(repoPath, false)
	if err != nil {
		t.Fatalf("Failed to init git repo: %v", err)
	}

	// Regular dir
	plainPath := filepath.Join(tmpRoot, "non-repo")
	if err := os.Mkdir(plainPath, 0755); err != nil {
		t.Fatalf("Failed to create plain dir: %v", err)
	}

	repos, err := ListRepositories(tmpRoot)
	if err != nil {
		t.Errorf("Function returned error: %v", err)
	}

	// Only one real repo should be found
	if len(repos) != 1 {
		t.Errorf("Expected 1 repo, but found %d", len(repos))
	}

	if len(repos) > 0 && repos[0].Path != repoPath {
		t.Errorf("Expected to find %s, but found %s", repoPath, repos[0].Path)
	}
}
