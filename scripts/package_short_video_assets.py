#!/usr/bin/env python3
"""Create per-short production folders from the ThermaForge short-video script CSV.

This writes script, caption, metadata, and shot direction files into the Desktop media
command center so an editor can assemble TikTok/Reels/Shorts quickly.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

DEFAULT_DESKTOP_ROOT = Path.home() / "Desktop" / "ThermaForge-Media-Command-Center"


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def srt_timestamp(seconds: int) -> str:
    return f"00:00:{seconds:02d},000"


def make_caption(script: str, total_seconds: int) -> str:
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", script) if part.strip()]
    if not sentences:
        sentences = [script]
    segment = max(2, total_seconds // max(1, len(sentences)))
    blocks = []
    start = 0
    for idx, sentence in enumerate(sentences, 1):
        end = total_seconds if idx == len(sentences) else min(total_seconds, start + segment)
        blocks.append(f"{idx}\n{srt_timestamp(start)} --> {srt_timestamp(end)}\n{sentence}\n")
        start = end
    return "\n".join(blocks)


def main() -> None:
    parser = argparse.ArgumentParser(description="Package ThermaForge short-video production assets.")
    parser.add_argument("--scripts", default="marketing/thermaforge-short-video-scripts.csv")
    parser.add_argument("--desktop-root", default=str(DEFAULT_DESKTOP_ROOT))
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    desktop_root = Path(args.desktop_root).expanduser()
    ready_root = desktop_root / "05_Ready_To_Post" / "short_video_packages"
    export_root = desktop_root / "07_Exports_By_Platform" / "TikTok_Reels_Shorts"
    ready_root.mkdir(parents=True, exist_ok=True)
    export_root.mkdir(parents=True, exist_ok=True)

    rows = list(csv.DictReader(Path(args.scripts).open(newline="")))
    if args.limit:
        rows = rows[: args.limit]

    for row in rows:
        folder_name = f"{row['id'].lower()}_{slugify(row['theme'])}"
        folder = ready_root / folder_name
        folder.mkdir(parents=True, exist_ok=True)

        (folder / "script.txt").write_text(row["script_text"] + "\n", encoding="utf-8")
        (folder / "hook.txt").write_text(row["hook"] + "\n", encoding="utf-8")
        (folder / "on_screen_text.txt").write_text(row["on_screen_text"] + "\n", encoding="utf-8")
        (folder / "b_roll_direction.txt").write_text(row["b_roll_direction"] + "\n", encoding="utf-8")
        (folder / "captions.srt").write_text(make_caption(row["script_text"], int(row["duration_seconds"])), encoding="utf-8")
        (folder / "metadata.json").write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")

        export_note = export_root / f"{row['id'].lower()}_{slugify(row['theme'])}_export_note.txt"
        export_note.write_text(
            "Final edited MP4 for this short should be exported here.\n"
            f"Expected voiceover filename: {row['audio_filename']}\n"
            "Recommended format: 1080x1920 MP4, H.264, burned captions or native platform captions.\n",
            encoding="utf-8",
        )
        print(folder)

    print(f"Packaged {len(rows)} short-video folder(s).")


if __name__ == "__main__":
    main()
