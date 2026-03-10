package git

import (
	"github.com/go-git/go-git/v6/plumbing"
)

type Reference struct {
	*plumbing.Reference
}
