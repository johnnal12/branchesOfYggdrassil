"""
Tripo 3D API — asset generation driver.

Reads TRIPO_API_KEY from environment. Uploads a reference image, submits
image-to-3D task, polls until complete, downloads GLB + PBR GLB.

Usage:
    python3 scripts/asset_gen.py --name poring --ref assets/concepts/poring_ref.jpg
    python3 scripts/asset_gen.py --name hunter --ref assets/concepts/hunter.jpg --quality detailed --quad --face-limit 15000

Pricing (credits, confirmed Apr 2026):
    standard (base): 20
    detailed texture: +40
    quad remesh:     +10
    face-limit > 10k: no extra cost
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

API_BASE = "https://api.tripo3d.ai/v2/openapi"
UPLOAD_URL = f"{API_BASE}/upload/sts"
TASK_URL = f"{API_BASE}/task"

CREDIT_RATE_USD = 0.01  # $0.01 per credit


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def get_key() -> str:
    key = os.environ.get("TRIPO_API_KEY", "").strip()
    if not key:
        die("TRIPO_API_KEY not set in environment")
    if len(key) < 20:
        die(f"TRIPO_API_KEY too short ({len(key)} chars) — placeholder?")
    return key


def estimate_cost(quality: str, quad: bool) -> int:
    base = 20
    if quality == "detailed":
        base += 40
    if quad:
        base += 10
    return base


def upload_image(key: str, image_path: Path) -> str:
    if not image_path.exists():
        die(f"Image not found: {image_path}")
    if image_path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
        die(f"Unsupported image type: {image_path.suffix} (must be jpg/png/webp)")

    print(f"→ Uploading {image_path.name} to Tripo...")
    headers = {"Authorization": f"Bearer {key}"}
    with open(image_path, "rb") as f:
        files = {"file": (image_path.name, f, f"image/{image_path.suffix[1:].lower()}")}
        r = requests.post(UPLOAD_URL, headers=headers, files=files, timeout=60)

    if r.status_code in (401, 403):
        die(f"Auth failed ({r.status_code}): {r.text[:300]}")
    if not r.ok:
        die(f"Upload failed ({r.status_code}): {r.text[:500]}")

    data = r.json()
    if data.get("code") != 0:
        die(f"Upload error code {data.get('code')}: {data.get('message', data)}")
    image_token = data.get("data", {}).get("image_token")
    if not image_token:
        die(f"No image_token in upload response: {data}")
    print(f"✓ Uploaded. image_token={image_token[:16]}...")
    return image_token


def submit_task(key: str, image_token: str, quality: str, quad: bool, face_limit: int, model_version: str) -> str:
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "type": "image_to_model",
        "model_version": model_version,
        "file": {"type": "jpg", "file_token": image_token},
        "texture_quality": quality,
        "auto_scale": True,
        "face_limit": face_limit,
    }
    if quad:
        payload["quad"] = True

    print(f"→ Submitting image_to_model task...")
    print(f"  quality={quality}, quad={quad}, face_limit={face_limit}, model={model_version}")
    r = requests.post(TASK_URL, headers=headers, json=payload, timeout=30)
    if not r.ok:
        die(f"Task submit failed ({r.status_code}): {r.text[:500]}")
    data = r.json()
    if data.get("code") != 0:
        die(f"Submit error code {data.get('code')}: {data.get('message', data)}")
    task_id = data.get("data", {}).get("task_id")
    if not task_id:
        die(f"No task_id in submit response: {data}")
    print(f"✓ Submitted. task_id={task_id}")
    return task_id


def poll_task(key: str, task_id: str, max_wait_s: int = 600) -> dict:
    headers = {"Authorization": f"Bearer {key}"}
    url = f"{TASK_URL}/{task_id}"
    started = time.time()
    delay = 5
    while True:
        elapsed = int(time.time() - started)
        if elapsed > max_wait_s:
            die(f"Polling timed out after {elapsed}s")
        r = requests.get(url, headers=headers, timeout=30)
        if not r.ok:
            die(f"Poll failed ({r.status_code}): {r.text[:300]}")
        data = r.json()
        if data.get("code") != 0:
            die(f"Poll error code {data.get('code')}: {data.get('message', data)}")
        task = data.get("data", {})
        status = task.get("status", "?")
        progress = task.get("progress", "?")
        print(f"  [{elapsed}s] status={status} progress={progress}")
        if status == "success":
            return task
        if status in ("failed", "cancelled", "banned"):
            die(f"Task ended with status={status}: {task}")
        time.sleep(delay)
        delay = min(delay + 5, 20)


def download(url: str, dest: Path) -> int:
    r = requests.get(url, timeout=120)
    if not r.ok:
        print(f"  ⚠ Download failed ({r.status_code}) for {url}")
        return 0
    dest.write_bytes(r.content)
    return len(r.content)


def download_outputs(task: dict, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    downloaded = {}
    output = task.get("output") or {}

    if url := output.get("model"):
        print(f"  → model.glb")
        size = download(url, out_dir / "model.glb")
        downloaded["model.glb"] = size

    if url := output.get("pbr_model"):
        print(f"  → pbr_model.glb")
        size = download(url, out_dir / "pbr_model.glb")
        downloaded["pbr_model.glb"] = size

    if url := output.get("rendered_image"):
        print(f"  → preview.png")
        size = download(url, out_dir / "preview.png")
        downloaded["preview.png"] = size

    return downloaded


def main():
    parser = argparse.ArgumentParser(description="Generate a 3D asset via Tripo API.")
    parser.add_argument("--name", required=True)
    parser.add_argument("--ref", required=True, help="Reference image path")
    parser.add_argument("--quality", choices=["standard", "detailed"], default="standard")
    parser.add_argument("--quad", action="store_true", help="Quad remesh (+10 credits)")
    parser.add_argument("--face-limit", type=int, default=10000)
    parser.add_argument("--model-version", default="v3.0-20250812",
                        help="Tripo model. Valid: P1-20260311, v3.1-20260211, v3.0-20250812, v2.5-20250123, Turbo-v1.0-20250506")
    parser.add_argument("--out-root", default=os.path.expanduser("~/game-mvp/assets/models"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    est = estimate_cost(args.quality, args.quad)
    est_usd = est * CREDIT_RATE_USD

    print(f"=== Tripo Asset Generation ===")
    print(f"Name:       {args.name}")
    print(f"Reference:  {args.ref}")
    print(f"Quality:    {args.quality} (+{40 if args.quality == 'detailed' else 0})")
    print(f"Quad:       {args.quad} (+{10 if args.quad else 0})")
    print(f"Face limit: {args.face_limit}")
    print(f"Est cost:   {est} credits (~${est_usd:.2f})")
    print()

    if args.dry_run:
        print("[dry-run] no API call")
        return

    key = get_key()
    ref = Path(args.ref).expanduser().resolve()
    out_dir = Path(args.out_root) / args.name

    t0 = time.time()
    image_token = upload_image(key, ref)
    task_id = submit_task(key, image_token, args.quality, args.quad, args.face_limit, args.model_version)
    task = poll_task(key, task_id)
    elapsed = time.time() - t0

    print(f"\n✓ Generation complete in {elapsed:.0f}s")
    print(f"Downloading to {out_dir}/")
    downloaded = download_outputs(task, out_dir)

    # Save ref copy + meta
    ref_copy = out_dir / f"source_ref{ref.suffix}"
    ref_copy.write_bytes(ref.read_bytes())

    meta = {
        "name": args.name,
        "reference_image": str(ref),
        "task_id": task_id,
        "image_token": image_token,
        "settings": {
            "quality": args.quality,
            "quad": args.quad,
            "face_limit": args.face_limit,
            "model_version": args.model_version,
        },
        "est_credits": est,
        "est_usd": round(est_usd, 4),
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(elapsed, 1),
        "downloaded": downloaded,
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2))

    print(f"\n=== Summary ===")
    print(f"Task: {task_id}")
    print(f"Duration: {elapsed:.0f}s")
    print(f"Est cost: {est} credits (~${est_usd:.2f})")
    print(f"Files:")
    for name, size in downloaded.items():
        print(f"  {name:20s} {size/1024:.1f} KB")
    print(f"\nOutput dir: {out_dir}")


if __name__ == "__main__":
    main()
