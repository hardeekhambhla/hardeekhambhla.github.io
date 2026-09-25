CREATE TABLE IF NOT EXISTS comments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post TEXT NOT NULL,
  name TEXT NOT NULL,
  body TEXT NOT NULL,
  owner TEXT NOT NULL,       -- sha256 of the browser's device id
  ip TEXT NOT NULL,          -- sha256 of ip, rate limiting only
  created_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_comments_post ON comments (post, created_at);
