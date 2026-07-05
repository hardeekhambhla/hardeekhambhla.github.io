import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

from hashnode_utils import load_state, parse_front_matter, prepare_content, save_state
from generate_platform_content import export_platform_versions


def build_payload(post_path: Path, state: Dict[str, Any]) -> Dict[str, Any]:
    markdown = post_path.read_text(encoding="utf-8")
    metadata = parse_front_matter(markdown)
    title = metadata.get("title", post_path.stem)
    description = metadata.get("description", "")
    tags = metadata.get("tags", [])
    image = metadata.get("image", "")
    body = prepare_content(markdown)

    slug = post_path.stem
    content_hash = hashlib.sha256(markdown.encode("utf-8")).hexdigest()
    previous = state.get(str(post_path))
    if previous and previous.get("hash") == content_hash:
        return {"skip": True, "reason": "unchanged", "slug": slug}

    return {
        "skip": False,
        "reason": "publish",
        "slug": slug,
        "content_hash": content_hash,
        "title": title,
        "description": description,
        "tags": tags,
        "image": image,
        "body": body,
    }


def publish_to_hashnode(payload: Dict[str, Any], token: str, publication_id: str) -> Dict[str, Any]:
    mutation = """
    mutation PublishPost($input: PublishPostInput!) {
      publishPost(input: $input) {
        post {
          slug
          title
        }
      }
    }
    """

    variables = {
        "input": {
            "publicationId": publication_id,
            "title": payload["title"],
            "contentMarkdown": payload["body"],
            "tags": payload["tags"],
            "coverImage": payload.get("image", ""),
        }
    }

    request_data = json.dumps({"query": mutation, "variables": variables}).encode("utf-8")
    request = urllib.request.Request(
        "https://gql.hashnode.com",
        data=request_data,
        headers={"Authorization": token, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        body = json.loads(response.read().decode("utf-8"))

    if "errors" in body:
        raise RuntimeError(json.dumps(body["errors"], indent=2))

    return body["data"]["publishPost"]["post"]


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    posts_dir = repo_root / "_posts"
    state_path = repo_root / ".hashnode-state.json"
    artifacts_dir = repo_root / "artifacts"
    state = load_state(state_path)

    token = os.environ.get("HASHNODE_TOKEN", "")
    publication_id = os.environ.get("HASHNODE_PUBLICATION_ID", "")
    if not token or not publication_id:
        print("Missing HASHNODE_TOKEN or HASHNODE_PUBLICATION_ID; exporting content only and skipping Hashnode publish.", file=sys.stderr)

    published_posts: List[Path] = []
    for post_path in sorted(posts_dir.glob("*.md")):
        payload = build_payload(post_path, state)
        if payload.get("skip"):
            print(f"Skipping unchanged post: {post_path.name}")
            continue

        print(f"Preparing export for post: {post_path.name}")
        export_platform_versions(post_path, artifacts_dir)

        if token and publication_id:
            print(f"Publishing post: {post_path.name}")
            try:
                result = publish_to_hashnode(payload, token, publication_id)
                print(f"Published successfully: {result['slug']}")
                state[str(post_path)] = {"slug": result["slug"], "hash": payload["content_hash"]}
                published_posts.append(post_path)
            except Exception as exc:
                print(f"Failed to publish {post_path.name}: {exc}", file=sys.stderr)
                continue
        else:
            state[str(post_path)] = {"slug": payload["slug"], "hash": payload["content_hash"], "status": "exported"}

    save_state(state_path, state)
    print(f"Processed {len(published_posts)} new or updated posts and exported artifacts for the rest.")
    return 0


if __name__ == "__main__":
    main()
