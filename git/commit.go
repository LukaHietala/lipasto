package git

import (
	"github.com/go-git/go-git/v6/plumbing/object"
)

type Commit struct {
	*object.Commit
}

func (c *Commit) ShortHash() string {
	return c.Hash.String()[:8]
}
