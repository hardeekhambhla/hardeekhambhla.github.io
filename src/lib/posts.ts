import { getCollection, type CollectionEntry } from 'astro:content';

export type Note = CollectionEntry<'posts'> & {
  date: Date;
  slug: string;
  url: string;
};

// Filenames are YYYY-MM-DD-slug.md; URLs keep the old Jekyll shape.
export async function getNotes(): Promise<Note[]> {
  const entries = await getCollection('posts');
  return entries
    .map((e) => {
      const [, y, m, d, slug] = e.id.match(/^(\d{4})-(\d\d)-(\d\d)-(.+)$/)!;
      const path = [...e.data.categories, y, m, d, `${slug}.html`].join('/');
      return { ...e, date: new Date(`${y}-${m}-${d}T12:00:00Z`), slug, url: `/${path}` };
    })
    .sort((a, b) => b.date.getTime() - a.date.getTime());
}

export const fmtDate = (d: Date) =>
  d.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric', timeZone: 'UTC' });

export const folders = (notes: Note[]) => {
  const map = new Map<string, number>();
  notes.forEach((n) => n.data.categories.forEach((c) => map.set(c, (map.get(c) ?? 0) + 1)));
  return [...map].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
};

export const cap = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

export const HOME_BANNER = 'https://raw.githubusercontent.com/hardeekhambhla/blog-assets/refs/heads/main/home3.JPG';
