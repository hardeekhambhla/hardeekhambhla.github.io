# Blog publishing pipeline

This repository keeps GitHub Pages as the canonical publishing destination. It now also supports an automated publishing pipeline for Hashnode that is triggered by changes under `_posts/**`.

## What it does

- Watches the repository for changes to posts under `_posts/**`.
- Parses Jekyll front matter for title, description, tags, date, and image.
- Produces clean Markdown and HTML exports for Medium/Substack-style publishing.
- Publishes new or updated posts to Hashnode through its GraphQL API.
- Reuses a local state file to skip posts that were already published.
- Uploads generated platform versions as GitHub Actions artifacts.

## Required GitHub Actions secrets

Add these repository secrets in GitHub:

- `HASHNODE_TOKEN`: your Hashnode personal access token from the developer settings.
- `HASHNODE_PUBLICATION_ID`: the publication ID that should receive the posts.

> Hashnode now requires GraphQL write access for the publication to be on a Pro plan. If the publication is not Pro or the token does not belong to an account that can write to that publication, the publish step will return 403.

## Local testing

Run the parser and export helpers locally:

```bash
python -m pytest -q tests/test_hashnode_publish.py
python scripts/publish_hashnode.py
```

The publish script will export Markdown and HTML files into the `artifacts/` directory and write state to `.hashnode-state.json`.

## Notes

- The existing Jekyll build and GitHub Pages deployment workflow are unchanged.
- If the Hashnode secrets are missing, the workflow will export the platform versions and skip the remote publish step gracefully.
