# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "fal-client>=0.5.0",
#     "httpx>=0.27.0",
# ]
# ///
"""
Shared fal.ai client library for all fal-ai skill scripts.

This module provides a unified interface for interacting with fal.ai's
various AI models including image generation, video generation, and
text-to-speech.
"""

import os
import sys
import base64
import httpx
from pathlib import Path
from typing import Literal

# Check for API key early
def get_api_key() -> str:
    """Get the fal.ai API key from environment."""
    api_key = os.environ.get("FAL_API_KEY")
    if not api_key:
        print("Error: FAL_API_KEY environment variable is not set.", file=sys.stderr)
        print("Get your API key from https://fal.ai/dashboard/keys", file=sys.stderr)
        sys.exit(1)
    return api_key


class FalClient:
    """Client for interacting with fal.ai API."""

    # Popular image generation models
    IMAGE_MODELS = {
        "flux-pro": "fal-ai/flux-pro/v1.1",
        "flux-dev": "fal-ai/flux/dev",
        "flux-schnell": "fal-ai/flux/schnell",
        "flux-realism": "fal-ai/flux-realism",
        "stable-diffusion-xl": "fal-ai/stable-diffusion-v3-medium",
        "recraft-v3": "fal-ai/recraft-v3",
    }

    # Video generation models
    VIDEO_MODELS = {
        "kling": "fal-ai/kling-video/v1.5/pro/image-to-video",
        "minimax": "fal-ai/minimax-video/image-to-video",
        "luma": "fal-ai/luma-dream-machine/image-to-video",
        "runway-gen3": "fal-ai/runway-gen3/turbo/image-to-video",
        "hunyuan": "fal-ai/hunyuan-video/image-to-video",
    }

    # Text-to-speech models
    TTS_MODELS = {
        "f5-tts": "fal-ai/f5-tts",
        "kokoro": "fal-ai/kokoro",
        "playht": "fal-ai/playht/tts/v3",
        "minimax-tts": "fal-ai/minimax-tts/text-to-speech",
    }

    # Image aspect ratios
    ASPECT_RATIOS = [
        "square", "square_hd", "portrait_4_3", "portrait_16_9",
        "landscape_4_3", "landscape_16_9", "21_9", "9_21"
    ]

    # Image sizes (for models that support explicit sizes)
    IMAGE_SIZES = {
        "square": (1024, 1024),
        "square_hd": (1536, 1536),
        "portrait_4_3": (896, 1152),
        "portrait_16_9": (768, 1344),
        "landscape_4_3": (1152, 896),
        "landscape_16_9": (1344, 768),
    }

    def __init__(self):
        """Initialize the fal.ai client."""
        self.api_key = get_api_key()
        self.base_url = "https://queue.fal.run"
        self.http_client = httpx.Client(
            headers={
                "Authorization": f"Key {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=300.0,  # 5 minute timeout for long-running tasks
        )

    def _submit_request(self, model_id: str, payload: dict) -> dict:
        """Submit a request to fal.ai and wait for the result."""
        import fal_client as fal

        # Set the API key for fal_client (it uses FAL_KEY)
        os.environ["FAL_KEY"] = self.api_key

        # Use fal.subscribe() for queued execution with status updates
        result = fal.subscribe(model_id, arguments=payload, with_logs=True)
        return result

    def generate_image(
        self,
        prompt: str,
        model: str = "flux-schnell",
        aspect_ratio: str = "square",
        num_images: int = 1,
        seed: int | None = None,
        enable_safety_checker: bool = True,
        negative_prompt: str | None = None,
    ) -> list[dict]:
        """
        Generate images from a text prompt.

        Args:
            prompt: Text description of the image to generate
            model: Model shortname or full fal.ai model ID
            aspect_ratio: Aspect ratio (square, portrait_4_3, landscape_16_9, etc.)
            num_images: Number of images to generate (1-4)
            seed: Random seed for reproducibility
            enable_safety_checker: Whether to enable NSFW filtering
            negative_prompt: Things to avoid in the image

        Returns:
            List of dicts with 'url', 'width', 'height' for each image
        """
        # Resolve model shortname to full ID
        model_id = self.IMAGE_MODELS.get(model, model)

        payload = {
            "prompt": prompt,
            "num_images": min(max(num_images, 1), 4),
            "enable_safety_checker": enable_safety_checker,
        }

        # Add optional parameters
        if aspect_ratio and aspect_ratio != "square":
            payload["image_size"] = aspect_ratio

        if seed is not None:
            payload["seed"] = seed

        if negative_prompt:
            payload["negative_prompt"] = negative_prompt

        result = self._submit_request(model_id, payload)
        return result.get("images", [])

    def generate_video(
        self,
        image_path: str,
        prompt: str | None = None,
        model: str = "kling",
        duration: float = 5.0,
        aspect_ratio: str | None = None,
    ) -> dict:
        """
        Generate a video from an image.

        Args:
            image_path: Path to the source image
            prompt: Optional motion/action description
            model: Model shortname or full fal.ai model ID
            duration: Video duration in seconds (model-dependent)
            aspect_ratio: Override aspect ratio (usually auto-detected)

        Returns:
            Dict with 'url' for the generated video
        """
        # Resolve model shortname to full ID
        model_id = self.VIDEO_MODELS.get(model, model)

        # Read and encode the image
        image_data = self._encode_image(image_path)

        payload = {
            "image_url": image_data,
        }

        # Add optional parameters based on model
        if prompt:
            payload["prompt"] = prompt

        if duration:
            payload["duration"] = str(int(duration))

        if aspect_ratio:
            payload["aspect_ratio"] = aspect_ratio

        result = self._submit_request(model_id, payload)
        return result.get("video", result)

    def text_to_speech(
        self,
        text: str,
        model: str = "f5-tts",
        voice: str | None = None,
        reference_audio: str | None = None,
        speed: float = 1.0,
    ) -> dict:
        """
        Convert text to speech.

        Args:
            text: Text to convert to speech
            model: Model shortname or full fal.ai model ID
            voice: Voice ID (model-dependent)
            reference_audio: Path to reference audio for voice cloning
            speed: Speech speed multiplier

        Returns:
            Dict with 'url' for the generated audio
        """
        # Resolve model shortname to full ID
        model_id = self.TTS_MODELS.get(model, model)

        payload = {
            "gen_text": text,
        }

        # Handle reference audio for voice cloning
        if reference_audio:
            audio_data = self._encode_audio(reference_audio)
            payload["ref_audio_url"] = audio_data

        if voice:
            payload["voice"] = voice

        if speed != 1.0:
            payload["speed"] = speed

        result = self._submit_request(model_id, payload)
        return result.get("audio", result)

    def _encode_image(self, image_path: str) -> str:
        """Encode an image file to a data URL."""
        path = Path(image_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Determine MIME type
        suffix = path.suffix.lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }
        mime_type = mime_types.get(suffix, "image/png")

        # Read and encode
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")

        return f"data:{mime_type};base64,{data}"

    def _encode_audio(self, audio_path: str) -> str:
        """Encode an audio file to a data URL."""
        path = Path(audio_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"Audio not found: {audio_path}")

        # Determine MIME type
        suffix = path.suffix.lower()
        mime_types = {
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".ogg": "audio/ogg",
            ".m4a": "audio/mp4",
            ".flac": "audio/flac",
        }
        mime_type = mime_types.get(suffix, "audio/mpeg")

        # Read and encode
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")

        return f"data:{mime_type};base64,{data}"

    def download_file(self, url: str, output_path: str) -> Path:
        """Download a file from a URL to a local path."""
        path = Path(output_path).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)

        response = self.http_client.get(url)
        response.raise_for_status()

        with open(path, "wb") as f:
            f.write(response.content)

        return path

    def list_models(self, category: Literal["image", "video", "tts"] = "image") -> dict:
        """List available models for a category."""
        if category == "image":
            return self.IMAGE_MODELS
        elif category == "video":
            return self.VIDEO_MODELS
        elif category == "tts":
            return self.TTS_MODELS
        else:
            raise ValueError(f"Unknown category: {category}")
