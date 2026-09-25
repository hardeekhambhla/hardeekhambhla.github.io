# Blog export pipeline

This repository keeps GitHub Pages as the canonical publishing destination. It also supports generating platform-ready Markdown exports for Medium and Substack from posts under `_posts/**`.

## What it does

- Reads Jekyll posts from `_posts/**`.
- Parses front matter for title, description, tags, date, and image.
- Produces clean Markdown exports for Medium and Substack.
- Writes the exports into dedicated folders under `artifacts/medium/` and `artifacts/substack/`.

## Local testing

Run the export helpers locally:

```bash
python -m pytest -q tests/test_platform_export.py
python scripts/generate_platform_content.py
```

The export script writes Markdown files into the `artifacts/medium/` and `artifacts/substack/` directories.

## Notes

- The existing Jekyll build and GitHub Pages deployment workflow remain unchanged.
