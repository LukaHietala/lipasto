package git

import (
	"github.com/go-git/go-git/v6/plumbing/object"
)

type Commit struct {
	*object.Commit
}

// ShortHash returns the first 8 characters of the commit hash
func (c *Commit) ShortHash() string {
	return c.Hash.String()[:8]
}
