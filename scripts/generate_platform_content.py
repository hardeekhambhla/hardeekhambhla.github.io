from html import escape
from pathlib import Path
from typing import Dict, List

from hashnode_utils import parse_front_matter, prepare_content


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

    html_body = f"<article><h1>{escape(title)}</h1>"
    if description:
        html_body += f"<p><em>{escape(description)}</em></p>"
    if date:
        html_body += f"<p><strong>Date:</strong> {escape(date)}</p>"
    if tags:
        html_body += f"<p><strong>Tags:</strong> {escape(tags)}</p>"
    if image:
        html_body += f"<figure><img src=\"{escape(image)}\" alt=\"{escape(title)}\" /></figure>"
    html_body += f"<div>{content}</div></article>"

    return {
        "medium_markdown": markdown_body,
        "substack_markdown": markdown_body.replace("# ", "# ", 1),
        "medium_html": html_body,
        "substack_html": html_body,
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
    written_paths: List[Path] = []
    for suffix, content in {
        f"{post_path.stem}.medium.md": export["medium_markdown"],
        f"{post_path.stem}.substack.md": export["substack_markdown"],
        f"{post_path.stem}.medium.html": export["medium_html"],
        f"{post_path.stem}.substack.html": export["substack_html"],
    }.items():
        output_path = output_dir / suffix
        output_path.write_text(content, encoding="utf-8")
        written_paths.append(output_path)
    return written_paths
