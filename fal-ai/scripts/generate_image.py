#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "fal-client>=0.5.0",
#     "httpx>=0.27.0",
# ]
# ///
"""
Generate images from text prompts using fal.ai models.

Usage:
    ./generate_image.py "A serene mountain landscape at sunset"
    ./generate_image.py "A cyberpunk city" --model flux-pro --aspect landscape_16_9
    ./generate_image.py "A cute robot" --num 4 --output ./robots/

Models:
    flux-schnell (default) - Fast, good quality
    flux-dev               - Higher quality, slower
    flux-pro               - Best quality (paid)
    flux-realism           - Photorealistic style
    recraft-v3             - Artistic/design focused
    stable-diffusion-xl    - Classic SD architecture

Aspect Ratios:
    square, square_hd, portrait_4_3, portrait_16_9,
    landscape_4_3, landscape_16_9, 21_9, 9_21
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime

from fal_helper import FalClient


def main():
    parser = argparse.ArgumentParser(
        description="Generate images from text prompts using fal.ai",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("prompt", help="Text description of the image to generate")
    parser.add_argument(
        "--model", "-m",
        default="flux-schnell",
        help="Model to use (default: flux-schnell)"
    )
    parser.add_argument(
        "--aspect", "-a",
        default="square",
        choices=FalClient.ASPECT_RATIOS,
        help="Aspect ratio (default: square)"
    )
    parser.add_argument(
        "--num", "-n",
        type=int,
        default=1,
        help="Number of images to generate (1-4, default: 1)"
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--negative", "-neg",
        help="Negative prompt (things to avoid)"
    )
    parser.add_argument(
        "--output", "-o",
        default=".",
        help="Output directory (default: current directory)"
    )
    parser.add_argument(
        "--no-safety",
        action="store_true",
        help="Disable safety checker"
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open generated images with default viewer"
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available image models and exit"
    )

    args = parser.parse_args()

    client = FalClient()

    # List models and exit if requested
    if args.list_models:
        print("Available image generation models:")
        print("-" * 50)
        for shortname, full_id in client.IMAGE_MODELS.items():
            print(f"  {shortname:20} -> {full_id}")
        print()
        print("Use --model <shortname> or --model <full-id>")
        return

    # Generate images
    print(f"Generating {args.num} image(s) with {args.model}...")
    print(f"Prompt: {args.prompt}")

    try:
        images = client.generate_image(
            prompt=args.prompt,
            model=args.model,
            aspect_ratio=args.aspect,
            num_images=args.num,
            seed=args.seed,
            enable_safety_checker=not args.no_safety,
            negative_prompt=args.negative,
        )
    except Exception as e:
        print(f"Error generating images: {e}", file=sys.stderr)
        sys.exit(1)

    if not images:
        print("No images were generated.", file=sys.stderr)
        sys.exit(1)

    # Download images
    output_dir = Path(args.output).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    downloaded_paths = []

    for i, image in enumerate(images):
        url = image.get("url")
        if not url:
            print(f"Warning: Image {i+1} has no URL", file=sys.stderr)
            continue

        # Generate filename
        suffix = "_" + str(i+1) if len(images) > 1 else ""
        filename = f"fal_image_{timestamp}{suffix}.png"
        output_path = output_dir / filename

        print(f"Downloading image {i+1}...")
        try:
            saved_path = client.download_file(url, str(output_path))
            downloaded_paths.append(saved_path)
            print(f"  Saved: {saved_path}")
        except Exception as e:
            print(f"  Error downloading: {e}", file=sys.stderr)

    # Summary
    print()
    print(f"Generated {len(downloaded_paths)} image(s) in {output_dir}")

    # Open images if requested
    if args.open and downloaded_paths:
        for path in downloaded_paths:
            try:
                if sys.platform == "darwin":
                    subprocess.run(["open", str(path)], check=True)
                elif sys.platform == "linux":
                    subprocess.run(["xdg-open", str(path)], check=True)
                elif sys.platform == "win32":
                    subprocess.run(["start", str(path)], check=True, shell=True)
            except subprocess.CalledProcessError:
                pass  # Ignore if open fails


if __name__ == "__main__":
    main()
