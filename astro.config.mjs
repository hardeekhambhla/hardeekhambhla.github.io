import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { fileURLToPath } from 'node:url';
import fs from 'node:fs';
import path from 'node:path';

// Keep old Jekyll URLs (…/slug.html) as real files, not slug.html/index.html
const flatHtml = {
  name: 'flat-html',
  hooks: {
    'astro:build:done': ({ dir }) => {
      const walk = (d) => {
        for (const e of fs.readdirSync(d, { withFileTypes: true })) {
          const p = path.join(d, e.name);
          if (!e.isDirectory()) continue;
          walk(p);
          if (e.name.endsWith('.html') && fs.existsSync(path.join(p, 'index.html'))) {
            fs.renameSync(path.join(p, 'index.html'), p + '.tmp');
            fs.rmdirSync(p);
            fs.renameSync(p + '.tmp', p);
          }
        }
      };
      walk(fileURLToPath(dir));
    },
  },
};

export default defineConfig({
  site: 'https://hardeekhambhla.github.io',
  integrations: [sitemap(), flatHtml],
  devToolbar: { enabled: false },
  image: { domains: ['raw.githubusercontent.com', 'github.com'] },
  redirects: { '/categories': '/tags', '/archives': '/' },
});
