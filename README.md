# TEDxBerkeley-2018
2018 TEDxBerkeley website featuring "You are Here". Infrastructure (Python compile script, workflow) is taken from the [Staging repository](github.com/alvinwan/staging).

# Usage

To make edits to the website, first run the preview.

    make preview

If the staging area matches your expectations, you may then deploy
directly to production. Run the following to publish to
[tedxberkeley.org](http://tedxberkeley.org).

    make deploy m="<message describing change>"

Your edits go live instantaneously.

## Usage Notes

You *must* stage before deployment, as `make staging` will save your
changes to this repository.
