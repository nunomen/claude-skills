#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "fal-client>=0.5.0",
#     "httpx>=0.27.0",
# ]
# ///
"""
Generate videos from text prompts using fal.ai models (no input image required).

Usage:
    ./generate_video_text.py "a cat walking on the beach at sunset"
    ./generate_video_text.py "cinematic drone shot of mountains" --model hunyuan
    ./generate_video_text.py "person dancing" --aspect 9:16 --resolution 1080p

Models:
    ltx-v2-fast (default) - LTX Video 2.0 Fast, good quality, fast
    ltx-v2               - LTX Video 2.0, higher quality
    ltx                  - LTX Video (preview)
    hunyuan              - Hunyuan video, high quality
    hunyuan-v1.5         - Hunyuan 1.5, improved motion
    minimax              - MiniMax video
    wan                  - Wan 2.1 text-to-video

Duration:
    Varies by model (typically 5-10 seconds max)
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime

from fal_helper import FalClient


def main():
    parser = argparse.ArgumentParser(
        description="Generate videos from text prompts using fal.ai",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("prompt", nargs="?", help="Text description of the video to generate")
    parser.add_argument(
        "--model", "-m",
        default="ltx-v2-fast",
        help="Model to use (default: ltx-v2-fast)"
    )
    parser.add_argument(
        "--aspect", "-a",
        default="16:9",
        help="Aspect ratio (default: 16:9). Options: 16:9, 9:16, 1:1, 4:3, 3:4"
    )
    parser.add_argument(
        "--resolution", "-r",
        default="720p",
        help="Video resolution (default: 720p). Options: 480p, 720p, 1080p"
    )
    parser.add_argument(
        "--duration", "-d",
        type=float,
        default=None,
        help="Video duration in seconds (model-dependent, typically 5-10s max)"
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=None,
        help="Random seed for reproducibility"
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
        help="List available text-to-video models and exit"
    )

    args = parser.parse_args()

    client = FalClient()

    # List models and exit if requested
    if args.list_models:
        print("Available text-to-video models:")
        print("-" * 60)
        for shortname, full_id in client.TEXT_TO_VIDEO_MODELS.items():
            cost_info = client.estimate_video_cost(full_id, 5.0)
            cost_str = f"~${cost_info['cost']:.2f}/5s" if cost_info else "pricing N/A"
            print(f"  {shortname:15} -> {full_id}")
            print(f"                     {cost_str}")
        print()
        print("Use --model <shortname> or --model <full-id>")
        return

    # Require prompt if not listing models
    if not args.prompt:
        parser.error("the following arguments are required: prompt")

    # Generate video
    print(f"Generating video with {args.model}...")
    print(f"Prompt: {args.prompt}")
    print(f"Aspect: {args.aspect}, Resolution: {args.resolution}")
    if args.duration:
        print(f"Duration: {args.duration}s")
    print()
    print("This may take several minutes...")

    try:
        result = client.generate_video_from_text(
            prompt=args.prompt,
            model=args.model,
            aspect_ratio=args.aspect,
            resolution=args.resolution,
            duration=args.duration,
            seed=args.seed,
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
        output_path = Path.cwd() / f"fal_video_t2v_{timestamp}.mp4"

    # Download video
    print(f"Downloading video...")
    try:
        saved_path = client.download_file(video_url, str(output_path))
        print(f"Saved: {saved_path}")
    except Exception as e:
        print(f"Error downloading video: {e}", file=sys.stderr)
        print(f"Video URL (download manually): {video_url}")
        sys.exit(1)

    # Show cost estimate
    model_id = client.TEXT_TO_VIDEO_MODELS.get(args.model, args.model)
    duration = args.duration or 5.0  # Default estimate
    cost_info = client.estimate_video_cost(
        model_id=model_id,
        duration_seconds=duration,
    )
    if cost_info:
        print(f"Estimated cost: ${cost_info['cost']:.4f} ({cost_info['breakdown']})")

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
