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

Cloudflare Worker + D1 in `worker/`. No login: commenters pick a name, saved in the browser with a private device id (used to delete their own comments).

```bash
cd worker && npm i
npx wrangler d1 create comments      # paste database_id into wrangler.toml
npm run db:remote
npx wrangler secret put ADMIN_KEY    # optional, lets you delete any comment
npm run deploy                       # prints https://hardee-comments.<you>.workers.dev
```

Then set the repo variable `COMMENTS_API` (Settings → Variables) to that URL. Local dev: `npm run db:local && npm run dev` in `worker/`, plus `npm run dev` at the root (uses `.env.development`).
Delete any comment: `curl -X DELETE -H "Authorization: Bearer $ADMIN_KEY" $API/comments/<id>` with an allowed `Origin` header.
