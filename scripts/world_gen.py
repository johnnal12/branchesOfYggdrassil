"""
World Labs Marble API — world generation driver.

Reads WLT_API_KEY from environment. Submits a generation, polls to completion,
downloads all available outputs to assets/maps/<name>/.

Usage:
    python3 scripts/world_gen.py --name field_08_test --prompt "..." --model draft
    python3 scripts/world_gen.py --name field_08_morning --prompt "..." --model standard

Models:
    draft   -> marble-1.0-draft (~230 credits, ~$0.18 per text gen)
    standard -> marble-1.1      (~1,580 credits, ~$1.26 per text gen)
    plus    -> marble-1.1-plus  (1,500-3,100 credits, $1.20-2.48 per gen)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

API_BASE = "https://api.worldlabs.ai/marble/v1"
MODEL_MAP = {
    "draft": "marble-1.0-draft",
    "standard": "marble-1.1",
    "plus": "marble-1.1-plus",
}
CREDIT_RATE_USD = 1.0 / 1250  # $1 per 1,250 credits
EST_CREDITS = {
    "draft": 230,
    "standard": 1580,
    "plus": 1500,
}


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def get_key() -> str:
    key = os.environ.get("WLT_API_KEY", "").strip()
    if not key:
        die("WLT_API_KEY not set in environment")
    if len(key) < 20:
        die(f"WLT_API_KEY looks too short ({len(key)} chars) — placeholder?")
    return key


def submit_generation(key: str, prompt: str, display_name: str, model: str) -> str:
    headers = {"Content-Type": "application/json", "WLT-Api-Key": key}
    payload = {
        "display_name": display_name,
        "model": model,
        "world_prompt": {"type": "text", "text_prompt": prompt},
    }
    url = f"{API_BASE}/worlds:generate"
    print(f"→ POST {url}")
    print(f"  model={model}, name={display_name}")
    print(f"  prompt={prompt[:80]}{'...' if len(prompt) > 80 else ''}")
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    if r.status_code in (401, 403):
        die(f"Auth failed ({r.status_code}): {r.text[:300]}")
    if r.status_code == 402:
        die(f"Payment required / insufficient credits: {r.text[:300]}")
    if not r.ok:
        die(f"Submit failed ({r.status_code}): {r.text[:500]}")
    data = r.json()
    op_id = data.get("operation_id")
    if not op_id:
        die(f"No operation_id in response: {data}")
    print(f"✓ Submitted. operation_id={op_id}")
    return op_id


def poll_operation(key: str, op_id: str, max_wait_s: int = 1800) -> dict:
    headers = {"WLT-Api-Key": key}
    url = f"{API_BASE}/operations/{op_id}"
    started = time.time()
    delay = 30
    while True:
        elapsed = int(time.time() - started)
        if elapsed > max_wait_s:
            die(f"Polling timed out after {elapsed}s")
        r = requests.get(url, headers=headers, timeout=30)
        if not r.ok:
            die(f"Poll failed ({r.status_code}): {r.text[:300]}")
        data = r.json()
        done = data.get("done", False)
        err = data.get("error")
        if err:
            die(f"Generation errored: {err}")
        status = (data.get("metadata") or {}).get("progress", {}).get("status", "?")
        print(f"  [{elapsed}s] done={done} status={status}")
        if done:
            return data
        time.sleep(delay)
        delay = min(delay + 30, 120)  # back off 30s -> 60s -> 90s -> 120s


def download(url: str, dest: Path) -> int:
    r = requests.get(url, timeout=120)
    if not r.ok:
        print(f"  ⚠ Download failed ({r.status_code}) for {url}")
        return 0
    dest.write_bytes(r.content)
    return len(r.content)


def download_assets(response: dict, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    downloaded = {}
    assets = response.get("assets") or {}

    mesh = assets.get("mesh") or {}
    if url := mesh.get("collider_mesh_url"):
        print(f"  → collider.glb")
        size = download(url, out_dir / "collider.glb")
        downloaded["collider.glb"] = size

    imagery = assets.get("imagery") or {}
    if url := imagery.get("pano_url"):
        print(f"  → panorama.jpg")
        size = download(url, out_dir / "panorama.jpg")
        downloaded["panorama.jpg"] = size

    splats = assets.get("splats") or {}
    spz = splats.get("spz_urls") or {}
    # Skip full_res by default (can be huge) — grab 100k for quick preview
    if url := spz.get("100k"):
        print(f"  → splat_100k.spz")
        size = download(url, out_dir / "splat_100k.spz")
        downloaded["splat_100k.spz"] = size

    return downloaded


def write_meta(out_dir: Path, payload: dict) -> None:
    (out_dir / "meta.json").write_text(json.dumps(payload, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Generate a Marble world via API.")
    parser.add_argument("--name", required=True, help="Short name (used for folder + display)")
    parser.add_argument("--prompt", required=True, help="World prompt")
    parser.add_argument("--model", choices=["draft", "standard", "plus"], default="draft")
    parser.add_argument("--out-root", default=os.path.expanduser("~/game-mvp/assets/maps"))
    parser.add_argument("--dry-run", action="store_true", help="Estimate cost, do nothing")
    args = parser.parse_args()

    model_id = MODEL_MAP[args.model]
    est_credits = EST_CREDITS[args.model]
    est_usd = est_credits * CREDIT_RATE_USD

    print(f"=== Marble Generation ===")
    print(f"Name:    {args.name}")
    print(f"Model:   {args.model} ({model_id})")
    print(f"Est cost: ~{est_credits} credits (~${est_usd:.2f})")
    print(f"Prompt:   {args.prompt[:100]}")
    print()

    if args.dry_run:
        print("[dry-run] No API call made.")
        return

    key = get_key()
    out_dir = Path(args.out_root) / args.name

    started = datetime.utcnow().isoformat() + "Z"
    t0 = time.time()
    op_id = submit_generation(key, args.prompt, args.name, model_id)
    response_env = poll_operation(key, op_id)
    response = response_env.get("response") or {}
    world_id = response.get("id")
    elapsed = time.time() - t0

    print(f"\n✓ Generation complete in {elapsed:.0f}s. world_id={world_id}")
    print(f"Downloading assets to {out_dir}/")
    downloaded = download_assets(response, out_dir)

    # Save prompt + meta for reference
    (out_dir / "prompt.txt").write_text(args.prompt)
    write_meta(out_dir, {
        "name": args.name,
        "prompt": args.prompt,
        "model": model_id,
        "operation_id": op_id,
        "world_id": world_id,
        "started_utc": started,
        "elapsed_seconds": round(elapsed, 1),
        "est_credits": est_credits,
        "est_usd": round(est_usd, 4),
        "downloaded": downloaded,
    })

    print(f"\n=== Summary ===")
    print(f"World: {world_id}")
    print(f"Duration: {elapsed:.0f}s")
    print(f"Est cost: ${est_usd:.2f}")
    print(f"Files saved:")
    for name, size in downloaded.items():
        print(f"  {name:20s}  {size/1024:.1f} KB")
    print(f"\nOutput dir: {out_dir}")


if __name__ == "__main__":
    main()
