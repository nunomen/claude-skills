#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "fal-client>=0.5.0",
#     "httpx>=0.27.0",
# ]
# ///
"""
Convert text to speech using fal.ai models.

Usage:
    ./generate_speech.py "Hello, world!"
    ./generate_speech.py "Welcome to our podcast" --model kokoro
    ./generate_speech.py "Clone my voice" --reference voice_sample.mp3

Models:
    f5-tts (default) - Good quality, supports voice cloning
    kokoro           - Natural sounding, multiple voices
    playht           - PlayHT v3 (high quality)
    minimax-tts      - MiniMax TTS

Voice Cloning:
    Use --reference to provide a sample audio file for voice cloning.
    Works best with f5-tts model.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime

from fal_helper import FalClient


def main():
    parser = argparse.ArgumentParser(
        description="Convert text to speech using fal.ai",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("text", help="Text to convert to speech")
    parser.add_argument(
        "--model", "-m",
        default="f5-tts",
        help="Model to use (default: f5-tts)"
    )
    parser.add_argument(
        "--reference", "-r",
        help="Reference audio file for voice cloning"
    )
    parser.add_argument(
        "--voice", "-v",
        help="Voice ID (model-dependent)"
    )
    parser.add_argument(
        "--speed", "-s",
        type=float,
        default=1.0,
        help="Speech speed multiplier (default: 1.0)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: auto-generated in current directory)"
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open generated audio with default player"
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available TTS models and exit"
    )

    args = parser.parse_args()

    client = FalClient()

    # List models and exit if requested
    if args.list_models:
        print("Available text-to-speech models:")
        print("-" * 50)
        for shortname, full_id in client.TTS_MODELS.items():
            print(f"  {shortname:15} -> {full_id}")
        print()
        print("Use --model <shortname> or --model <full-id>")
        return

    # Validate reference audio if provided
    if args.reference:
        ref_path = Path(args.reference).expanduser().resolve()
        if not ref_path.exists():
            print(f"Error: Reference audio not found: {args.reference}", file=sys.stderr)
            sys.exit(1)

    # Generate speech
    print(f"Generating speech with {args.model}...")
    print(f"Text: {args.text[:100]}{'...' if len(args.text) > 100 else ''}")
    if args.reference:
        print(f"Reference audio: {args.reference}")
    if args.speed != 1.0:
        print(f"Speed: {args.speed}x")

    try:
        result = client.text_to_speech(
            text=args.text,
            model=args.model,
            voice=args.voice,
            reference_audio=args.reference,
            speed=args.speed,
        )
    except Exception as e:
        print(f"Error generating speech: {e}", file=sys.stderr)
        sys.exit(1)

    # Get the audio URL
    audio_url = result.get("url") if isinstance(result, dict) else None
    if not audio_url:
        # Try alternate response formats
        if isinstance(result, dict):
            audio_url = result.get("audio_url") or result.get("audio", {}).get("url")
        if not audio_url:
            print(f"Unexpected result format: {result}", file=sys.stderr)
            sys.exit(1)

    # Determine output path
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Determine extension from URL or default to wav
        ext = "wav"
        if ".mp3" in audio_url:
            ext = "mp3"
        elif ".ogg" in audio_url:
            ext = "ogg"
        output_path = Path.cwd() / f"fal_speech_{timestamp}.{ext}"

    # Download audio
    print(f"Downloading audio...")
    try:
        saved_path = client.download_file(audio_url, str(output_path))
        print(f"Saved: {saved_path}")
    except Exception as e:
        print(f"Error downloading audio: {e}", file=sys.stderr)
        print(f"Audio URL (download manually): {audio_url}")
        sys.exit(1)

    # Open audio if requested
    if args.open:
        try:
            if sys.platform == "darwin":
                subprocess.run(["open", str(saved_path)], check=True)
            elif sys.platform == "linux":
                subprocess.run(["xdg-open", str(saved_path)], check=True)
            elif sys.platform == "win32":
                subprocess.run(["start", str(saved_path)], check=True, shell=True)
        except subprocess.CalledProcessError:
            pass  # Ignore if open fails


if __name__ == "__main__":
    main()
