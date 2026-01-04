#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "fal-client>=0.5.0",
#     "httpx>=0.27.0",
# ]
# ///
"""
Generate videos from images using fal.ai models.

Usage:
    ./generate_video.py image.png
    ./generate_video.py image.png --prompt "camera slowly zooms in"
    ./generate_video.py image.png --model runway-gen3 --duration 10

Models:
    kling (default) - High quality, good motion
    minimax         - Good quality, fast
    luma            - Luma Dream Machine
    runway-gen3     - Runway Gen-3 Turbo
    hunyuan         - Hunyuan video model

Duration:
    Varies by model (typically 5-10 seconds)
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime

from fal_helper import FalClient


def main():
    parser = argparse.ArgumentParser(
        description="Generate videos from images using fal.ai",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("image", help="Path to the source image")
    parser.add_argument(
        "--prompt", "-p",
        help="Motion/action description (optional)"
    )
    parser.add_argument(
        "--model", "-m",
        default="kling",
        help="Model to use (default: kling)"
    )
    parser.add_argument(
        "--duration", "-d",
        type=float,
        default=5.0,
        help="Video duration in seconds (default: 5.0)"
    )
    parser.add_argument(
        "--aspect", "-a",
        help="Override aspect ratio (usually auto-detected from image)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: auto-generated in current directory)"
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open generated video with default player"
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available video models and exit"
    )

    args = parser.parse_args()

    client = FalClient()

    # List models and exit if requested
    if args.list_models:
        print("Available image-to-video models:")
        print("-" * 50)
        for shortname, full_id in client.VIDEO_MODELS.items():
            print(f"  {shortname:15} -> {full_id}")
        print()
        print("Use --model <shortname> or --model <full-id>")
        return

    # Validate input image exists
    image_path = Path(args.image).expanduser().resolve()
    if not image_path.exists():
        print(f"Error: Image not found: {args.image}", file=sys.stderr)
        sys.exit(1)

    # Generate video
    print(f"Generating video with {args.model}...")
    print(f"Source image: {image_path}")
    if args.prompt:
        print(f"Prompt: {args.prompt}")
    print(f"Duration: {args.duration}s")
    print()
    print("This may take several minutes...")

    try:
        result = client.generate_video(
            image_path=str(image_path),
            prompt=args.prompt,
            model=args.model,
            duration=args.duration,
            aspect_ratio=args.aspect,
        )
    except Exception as e:
        print(f"Error generating video: {e}", file=sys.stderr)
        sys.exit(1)

    # Get the video URL
    video_url = result.get("url") if isinstance(result, dict) else None
    if not video_url:
        print(f"Unexpected result format: {result}", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path.cwd() / f"fal_video_{timestamp}.mp4"

    # Download video
    print(f"Downloading video...")
    try:
        saved_path = client.download_file(video_url, str(output_path))
        print(f"Saved: {saved_path}")
    except Exception as e:
        print(f"Error downloading video: {e}", file=sys.stderr)
        print(f"Video URL (download manually): {video_url}")
        sys.exit(1)

    # Open video if requested
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
