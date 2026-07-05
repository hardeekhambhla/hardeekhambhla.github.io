import sys
from pathlib import Path
from typing import Dict, List

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from scripts.content_utils import parse_front_matter, prepare_content


def _build_export(payload: Dict[str, object], slug: str) -> Dict[str, str]:
    title = str(payload.get("title", slug))
    description = str(payload.get("description", ""))
    tags = ", ".join([str(tag) for tag in payload.get("tags", [])])
    content = str(payload.get("body", ""))
    image = str(payload.get("image", ""))
    date = str(payload.get("date", ""))

    meta_lines = [f"# {title}", ""]
    if description:
        meta_lines.append(description)
    if date:
        meta_lines.append(f"Date: {date}")
    if tags:
        meta_lines.append(f"Tags: {tags}")
    meta_lines.append("")

    markdown_body = "\n".join(meta_lines) + content + "\n"
    if image:
        markdown_body = f"![cover]({image})\n\n" + markdown_body

    return {
        "medium_markdown": markdown_body,
        "substack_markdown": markdown_body,
    }


def export_platform_versions(post_path: Path, output_dir: Path) -> List[Path]:
    markdown = post_path.read_text(encoding="utf-8")
    metadata = parse_front_matter(markdown)
    payload = {
        "title": metadata.get("title", post_path.stem),
        "description": metadata.get("description", ""),
        "tags": metadata.get("tags", []),
        "image": metadata.get("image", ""),
        "date": metadata.get("date", ""),
        "body": prepare_content(markdown),
    }
    export = _build_export(payload, post_path.stem)

    output_dir.mkdir(parents=True, exist_ok=True)
    medium_dir = output_dir / "medium"
    substack_dir = output_dir / "substack"
    medium_dir.mkdir(parents=True, exist_ok=True)
    substack_dir.mkdir(parents=True, exist_ok=True)

    written_paths: List[Path] = []
    for target_dir, content in {
        medium_dir: export["medium_markdown"],
        substack_dir: export["substack_markdown"],
    }.items():
        output_path = target_dir / f"{post_path.stem}.md"
        output_path.write_text(content, encoding="utf-8")
        written_paths.append(output_path)
    return written_paths
