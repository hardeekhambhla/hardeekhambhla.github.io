import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from scripts.hashnode_utils import load_state, parse_front_matter, prepare_content, save_state
from scripts.generate_platform_content import export_platform_versions


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


def build_request_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": token,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "github-actions-hashnode-publisher/1.0",
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

    request_payload = {"query": mutation, "variables": variables}
    request_data = json.dumps(request_payload).encode("utf-8")
    endpoint = os.environ.get("HASHNODE_API_URL", "https://gql.hashnode.com")
    print(f"Hashnode endpoint: {endpoint}", file=sys.stderr)
    print(f"Hashnode publication id: {publication_id}", file=sys.stderr)
    print(f"Hashnode title: {payload['title']}", file=sys.stderr)
    request = urllib.request.Request(
        endpoint,
        data=request_data,
        headers=build_request_headers(token),
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw_body = response.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "ignore").strip()
        raise RuntimeError(f"Hashnode API returned {exc.code}: {detail or exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Hashnode request failed: {exc.reason}") from exc

    print(f"Hashnode raw response: {raw_body[:1000]}", file=sys.stderr)
    try:
        body = json.loads(raw_body) if raw_body.strip() else {}
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Hashnode returned non-JSON response: {raw_body[:500]}") from exc

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
    failed_posts: List[str] = []
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
                failed_posts.append(post_path.name)
                print(f"Failed to publish {post_path.name}: {exc}", file=sys.stderr)
                continue
        else:
            state[str(post_path)] = {"slug": payload["slug"], "hash": payload["content_hash"], "status": "exported"}

    save_state(state_path, state)
    if failed_posts:
        print(f"Hashnode publishing failed for {len(failed_posts)} posts: {', '.join(failed_posts)}", file=sys.stderr)
        return 1

    print(f"Processed {len(published_posts)} new or updated posts and exported artifacts for the rest.")
    return 0


if __name__ == "__main__":
    main()
