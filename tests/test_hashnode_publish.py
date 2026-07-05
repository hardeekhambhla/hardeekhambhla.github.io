import os
import tempfile
import unittest
from pathlib import Path

from scripts.hashnode_utils import parse_front_matter, prepare_content, load_state, save_state
from scripts.publish_hashnode import build_request_headers


class HashnodePublishTests(unittest.TestCase):
    def test_parse_front_matter_extracts_metadata(self):
        sample = """---
title: My Test Post
description: A short summary.
tags: one two three
date: 2026-07-05 12:00:00 +0000
image: https://example.com/cover.jpg
---

Hello world.
"""

        metadata = parse_front_matter(sample)
        self.assertEqual(metadata["title"], "My Test Post")
        self.assertEqual(metadata["description"], "A short summary.")
        self.assertEqual(metadata["tags"], ["one", "two", "three"])
        self.assertEqual(metadata["date"], "2026-07-05 12:00:00 +0000")
        self.assertEqual(metadata["image"], "https://example.com/cover.jpg")

    def test_prepare_content_removes_front_matter_and_converts_figures(self):
        sample = """---
title: My Test Post
---

Here is a paragraph.

<figure>
  <img src=\"https://example.com/photo.jpg\" alt=\"Example photo\" />
  <figcaption>Example caption</figcaption>
</figure>

```python
print('hi')
```
"""
        cleaned = prepare_content(sample)
        self.assertIn("Here is a paragraph.", cleaned)
        self.assertIn("![Example photo](https://example.com/photo.jpg)", cleaned)
        self.assertIn("```python", cleaned)
        self.assertNotIn("---", cleaned)

    def test_state_round_trip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"
            save_state(state_path, {"post-1": {"slug": "my-post", "hash": "abc"}})
            state = load_state(state_path)
            self.assertEqual(state["post-1"]["slug"], "my-post")

    def test_build_request_headers_use_raw_token(self):
        headers = build_request_headers("demo-token")
        self.assertEqual(headers["Authorization"], "demo-token")
        self.assertEqual(headers["Content-Type"], "application/json")


if __name__ == "__main__":
    unittest.main()
