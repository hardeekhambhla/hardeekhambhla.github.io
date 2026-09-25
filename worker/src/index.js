const MAX_NAME = 40;
const MAX_BODY = 2000;

const sha = async (s) =>
  [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s)))]
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');

export default {
  async fetch(req, env) {
    const origin = req.headers.get('Origin') ?? '';
    const allowed = env.ALLOWED_ORIGINS.split(',').includes(origin);
    const cors = {
      'Access-Control-Allow-Origin': allowed ? origin : 'null',
      'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, X-Device',
      Vary: 'Origin',
    };
    const json = (data, status = 200) =>
      new Response(JSON.stringify(data), { status, headers: { ...cors, 'Content-Type': 'application/json' } });

    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });
    if (!allowed) return json({ error: 'forbidden' }, 403);

    const url = new URL(req.url);
    const device = req.headers.get('X-Device') ?? '';
    const owner = device.length >= 16 ? await sha(device) : '';

    if (req.method === 'GET' && url.pathname === '/comments') {
      const post = url.searchParams.get('post') ?? '';
      const { results } = await env.DB
        .prepare('SELECT id, name, body, created_at, owner FROM comments WHERE post = ? ORDER BY created_at ASC LIMIT 500')
        .bind(post)
        .all();
      return json(results.map(({ owner: o, ...c }) => ({ ...c, mine: !!owner && o === owner })));
    }

    if (req.method === 'POST' && url.pathname === '/comments') {
      if (!owner) return json({ error: 'missing device' }, 400);
      const b = await req.json().catch(() => ({}));
      const post = String(b.post ?? '').slice(0, 300);
      const name = String(b.name ?? '').trim().slice(0, MAX_NAME);
      const body = String(b.body ?? '').trim();
      if (b.website) return json({ ok: true }); // honeypot
      if (!post || !name || !body) return json({ error: 'name and comment required' }, 400);
      if (body.length > MAX_BODY) return json({ error: 'comment too long' }, 400);

      const ip = await sha(req.headers.get('CF-Connecting-IP') ?? 'local');
      const now = Date.now();
      const recent = await env.DB
        .prepare('SELECT COUNT(*) AS n FROM comments WHERE ip = ? AND created_at > ?')
        .bind(ip, now - 60_000)
        .first();
      if (recent.n >= 3) return json({ error: 'slow down a little' }, 429);

      const r = await env.DB
        .prepare('INSERT INTO comments (post, name, body, owner, ip, created_at) VALUES (?, ?, ?, ?, ?, ?)')
        .bind(post, name, body, owner, ip, now)
        .run();
      return json({ id: r.meta.last_row_id, name, body, created_at: now, mine: true }, 201);
    }

    const del = url.pathname.match(/^\/comments\/(\d+)$/);
    if (req.method === 'DELETE' && del) {
      const admin = env.ADMIN_KEY && req.headers.get('Authorization') === `Bearer ${env.ADMIN_KEY}`;
      if (!admin && !owner) return json({ error: 'forbidden' }, 403);
      const r = admin
        ? await env.DB.prepare('DELETE FROM comments WHERE id = ?').bind(del[1]).run()
        : await env.DB.prepare('DELETE FROM comments WHERE id = ? AND owner = ?').bind(del[1], owner).run();
      return json({ deleted: r.meta.changes });
    }

    return json({ error: 'not found' }, 404);
  },
};
