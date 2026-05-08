# ElevenLabs Voiceover Pipeline

This repo now has a safe, no-secrets-committed workflow for turning ThermaForge short-video scripts into ElevenLabs voiceovers.

## Files

| File | Purpose |
|---|---|
| `marketing/thermaforge-short-video-scripts.csv` | First 25 TikTok/Reels/Shorts-ready scripts with hooks, script text, on-screen text, B-roll direction, and output folders. |
| `marketing/thermaforge-elevenlabs-voiceover-queue.csv` | Batch queue for ElevenLabs generation. Each row maps a script to a voice role and output filename. |
| `scripts/generate_elevenlabs_voiceovers.py` | Python generator that reads the queue, calls ElevenLabs, and saves MP3s into the Desktop media command center. |
| `scripts/package_short_video_assets.py` | Packages each short into Desktop production folders with script, hook, on-screen text, B-roll notes, captions, and metadata. |

## Secret handling

Do not commit API keys or voice IDs. Set them as environment variables only:

```bash
export ELEVENLABS_API_KEY="..."
export ELEVENLABS_OPERATOR_VOICE_ID="..."
export ELEVENLABS_AD_VOICE_ID="..."
export ELEVENLABS_EXPLAINER_VOICE_ID="..."
```

If you only want to use one voice for all roles, set all three voice variables to the same voice ID.

## Package short-video production folders

```bash
python3 scripts/package_short_video_assets.py --limit 25
```

This creates per-video folders under:

```text
/root/Desktop/ThermaForge-Media-Command-Center/05_Ready_To_Post/short_video_packages
```

## Dry-run validation

```bash
python3 scripts/generate_elevenlabs_voiceovers.py --dry-run --limit 5
```

## Generate the first 5 voiceovers

```bash
python3 scripts/generate_elevenlabs_voiceovers.py --limit 5
```

## Generate all queued voiceovers

```bash
python3 scripts/generate_elevenlabs_voiceovers.py
```

## Output location

MP3 files are saved into:

```text
/root/Desktop/ThermaForge-Media-Command-Center/07_Exports_By_Platform/TikTok_Reels_Shorts
```

Move finished edited videos into:

```text
/root/Desktop/ThermaForge-Media-Command-Center/05_Ready_To_Post
```

## Recommended voice mapping

| Role | Env var | Recommended tone |
|---|---|---|
| Operator/founder | `ELEVENLABS_OPERATOR_VOICE_ID` | Calm, direct HVAC operator speaking to another owner. |
| Ad voice | `ELEVENLABS_AD_VOICE_ID` | Clear, firm, slightly urgent, no radio-announcer energy. |
| Explainer | `ELEVENLABS_EXPLAINER_VOICE_ID` | Calm, instructional, confident, service-business operator tone. |
