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

## Comments

Cloudflare Worker + D1 in `worker/`, deployed automatically by the workflow. No login: commenters pick a name, saved in the browser with a private device id (used to delete their own comments).

One-time setup: in Cloudflare create an API token (My Profile -> API Tokens -> "Edit Cloudflare Workers" template, plus Account -> D1 -> Edit), then add GitHub repo secrets `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`. Every push to `master` then creates the database, deploys the Worker and points the site at it. Without the secrets, comments are simply hidden.

Custom domain: add it to `ALLOWED_ORIGINS` in `worker/wrangler.toml`.
Local dev: `npm run db:local && npm run dev` in `worker/`, plus `npm run dev` at the root (uses `.env.development`).
Delete any comment: set an `ADMIN_KEY` secret on the Worker, then `curl -X DELETE -H "Authorization: Bearer $KEY" -H "Origin: https://hardeekhambhla.github.io" $API/comments/<id>`.
