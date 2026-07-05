import re
from pathlib import Path
from typing import Any, Dict


def parse_front_matter(markdown: str) -> Dict[str, Any]:
    lines = markdown.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    metadata: Dict[str, Any] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key == "tags":
            metadata[key] = [item.strip() for item in value.split() if item.strip()]
        else:
            metadata[key] = value
    return metadata


def prepare_content(markdown: str) -> str:
    content = markdown
    lines = content.splitlines()
    if lines and lines[0].strip() == "---":
        for index, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                content = "\n".join(lines[index + 1 :])
                break

    content = re.sub(r"<figure[^>]*>", "", content, flags=re.IGNORECASE)
    content = re.sub(r"</figure>", "", content, flags=re.IGNORECASE)
    content = re.sub(r"<figcaption[^>]*>", "", content, flags=re.IGNORECASE)
    content = re.sub(r"</figcaption>", "", content, flags=re.IGNORECASE)
    content = re.sub(r"<br\s*/?>", "\n", content, flags=re.IGNORECASE)

    def replace_img(match: re.Match[str]) -> str:
        src = match.group(1)
        alt = match.group(2) if match.group(2) else ""
        alt_text = alt.strip() if alt else ""
        return f"![{alt_text}]({src})" if alt_text else f"![]({src})"

    content = re.sub(
        r"<img\s+src=['\"]([^'\"]+)['\"](?:\s+alt=['\"]([^'\"]*)['\"])?\s*/?>",
        replace_img,
        content,
        flags=re.IGNORECASE,
    )
    content = re.sub(r"<p[^>]*>", "", content, flags=re.IGNORECASE)
    content = re.sub(r"</p>", "\n\n", content, flags=re.IGNORECASE)
    content = re.sub(r"\n{3,}", "\n\n", content)
    return content.strip()
