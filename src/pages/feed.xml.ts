import rss from '@astrojs/rss';
import type { APIContext } from 'astro';
import { getNotes } from '../lib/posts';

export async function GET(ctx: APIContext) {
  const notes = await getNotes();
  return rss({
    title: 'Hardee Khambhla',
    description: "hi, I'm Hardee. I enjoy listening to other people's stories and sharing my own.",
    site: ctx.site!,
    items: notes.map((n) => ({
      title: n.data.title,
      description: n.data.subtitle,
      pubDate: n.date,
      link: n.url,
    })),
  });
}
