import tempfile
import unittest
from pathlib import Path

from scripts.content_utils import parse_front_matter, prepare_content
from scripts.generate_platform_content import export_platform_versions


class PlatformExportTests(unittest.TestCase):
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

    def test_export_platform_versions_writes_to_dedicated_folders(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            post_path = repo_root / "_posts" / "2026-07-05-test-post.md"
            post_path.parent.mkdir(parents=True, exist_ok=True)
            post_path.write_text(
                """---
title: My Test Post
description: A short summary.
tags: one two
image: https://example.com/cover.jpg
---

Hello world.
""",
                encoding="utf-8",
            )

            output_dir = repo_root / "artifacts"
            written_paths = export_platform_versions(post_path, output_dir)

            self.assertEqual(len(written_paths), 2)
            self.assertTrue((output_dir / "medium" / f"{post_path.stem}.md").exists())
            self.assertTrue((output_dir / "substack" / f"{post_path.stem}.md").exists())


if __name__ == "__main__":
    unittest.main()
