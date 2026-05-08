#!/usr/bin/env python3
"""Generate ThermaForge voiceovers from a CSV queue via ElevenLabs.

Secrets are read from environment variables only. Do not commit API keys.

Required:
  ELEVENLABS_API_KEY
  Voice ID env vars referenced by the queue, for example:
    ELEVENLABS_OPERATOR_VOICE_ID
    ELEVENLABS_AD_VOICE_ID
    ELEVENLABS_EXPLAINER_VOICE_ID

Example:
  ELEVENLABS_API_KEY=... ELEVENLABS_OPERATOR_VOICE_ID=... \
  python3 scripts/generate_elevenlabs_voiceovers.py \
    --queue marketing/thermaforge-elevenlabs-voiceover-queue.csv \
    --limit 5
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API_BASE = "https://api.elevenlabs.io/v1/text-to-speech"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def request_voiceover(api_key: str, voice_id: str, text: str, model_id: str, output_format: str) -> bytes:
    url = f"{API_BASE}/{voice_id}?output_format={output_format}"
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.58,
            "similarity_boost": 0.78,
            "style": 0.18,
            "use_speaker_boost": True,
        },
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "xi-api-key": api_key,
            "content-type": "application/json",
            "accept": "audio/mpeg",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        fail(f"ElevenLabs HTTP {exc.code}: {body}")
    except urllib.error.URLError as exc:
        fail(f"ElevenLabs request failed: {exc.reason}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate ThermaForge ElevenLabs voiceovers from CSV.")
    parser.add_argument("--queue", default="marketing/thermaforge-elevenlabs-voiceover-queue.csv")
    parser.add_argument("--limit", type=int, default=0, help="Maximum rows to generate. 0 means all queued rows.")
    parser.add_argument("--dry-run", action="store_true", help="Validate queue and print planned outputs without calling ElevenLabs.")
    parser.add_argument("--overwrite", action="store_true", help="Regenerate files that already exist.")
    parser.add_argument("--sleep", type=float, default=0.25, help="Seconds to sleep between requests.")
    args = parser.parse_args()

    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not api_key and not args.dry_run:
        fail("ELEVENLABS_API_KEY is required unless --dry-run is used.")

    queue_path = Path(args.queue)
    if not queue_path.exists():
        fail(f"Queue not found: {queue_path}")

    rows = list(csv.DictReader(queue_path.open(newline="")))
    queued = [row for row in rows if row.get("status", "queued").lower() in {"queued", "ready", ""}]
    if args.limit:
        queued = queued[: args.limit]

    generated = 0
    for row in queued:
        voice_env = row["voice_id_env"]
        voice_id = os.environ.get(voice_env, "").strip()
        if not voice_id and not args.dry_run:
            fail(f"{voice_env} is required for row {row.get('id')}")

        output_dir = Path(row["output_folder"]).expanduser()
        output_path = output_dir / row["audio_filename"]
        print(f"{row['id']} -> {output_path}")

        if args.dry_run:
            continue
        if output_path.exists() and not args.overwrite:
            print(f"  skip existing: {output_path}")
            continue

        output_dir.mkdir(parents=True, exist_ok=True)
        audio = request_voiceover(
            api_key=api_key,
            voice_id=voice_id,
            text=row["script_text"],
            model_id=row.get("model_id") or "eleven_multilingual_v2",
            output_format=row.get("output_format") or "mp3_44100_128",
        )
        output_path.write_bytes(audio)
        generated += 1
        time.sleep(args.sleep)

    print(f"Voiceover generation complete. Generated {generated} file(s).")


if __name__ == "__main__":
    main()
