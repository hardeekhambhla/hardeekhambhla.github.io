import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const words = z.string().transform((s) => s.split(/\s+/).filter(Boolean));

const posts = defineCollection({
  loader: glob({ pattern: '*.md', base: './_posts' }),
  schema: z.object({
    title: z.string(),
    subtitle: z.string().optional(),
    author: z.string().optional(),
    categories: words.default(''),
    tags: words.default(''),
    image: z.string().optional(),
  }),
});

export const collections = { posts };
