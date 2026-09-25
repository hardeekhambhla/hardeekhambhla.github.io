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

- Site build and deploy: see Site section above.

## Site

Astro static site, iOS Notes style. Posts live in `_posts/` (Markdown, `YYYY-MM-DD-slug.md`); old Jekyll URLs are preserved.

```bash
npm install
npm run dev      # local
npm run build    # -> dist/
```

Deploys via GitHub Actions (`.github/workflows/deploy.yml`). In repo Settings → Pages, set Source to **GitHub Actions**.
