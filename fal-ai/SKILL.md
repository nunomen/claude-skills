---
name: fal-ai
description: Generate images, videos, and speech using fal.ai API. Use when asked to create images from text, animate images into videos, or convert text to speech using fal.ai models like Flux, Kling, Runway, or F5-TTS.
---

# fal.ai Media Generation

Generate images, videos, and speech using fal.ai's suite of AI models.

## Setup

Set your fal.ai API key:

```bash
export FAL_API_KEY="your-api-key-here"
```

Get your API key from https://fal.ai/dashboard/keys

## Quick Reference

| Task | Command |
|------|---------|
| Generate image | `./scripts/generate_image.py "prompt"` |
| Generate video from image | `./scripts/generate_video.py image.png` |
| Convert text to speech | `./scripts/generate_speech.py "text"` |
| List image models | `./scripts/generate_image.py --list-models ""` |
| List video models | `./scripts/generate_video.py --list-models` |
| List TTS models | `./scripts/generate_speech.py --list-models` |

## Text-to-Image Generation

Generate images from text descriptions using state-of-the-art models.

### Available Models

| Model | Description | Speed | Quality |
|-------|-------------|-------|---------|
| `flux-schnell` (default) | Fast generation | Fast | Good |
| `flux-dev` | Development model | Medium | High |
| `flux-pro` | Production quality | Slow | Best |
| `flux-realism` | Photorealistic | Medium | High |
| `recraft-v3` | Design/artistic | Medium | High |
| `stable-diffusion-xl` | Classic SD | Medium | Good |

### Usage

```bash
# Basic generation
./scripts/generate_image.py "A serene mountain landscape at sunset"

# Specify model and aspect ratio
./scripts/generate_image.py "A cyberpunk cityscape" --model flux-pro --aspect landscape_16_9

# Generate multiple images
./scripts/generate_image.py "A cute robot mascot" --num 4 --output ./robots/

# With negative prompt and seed
./scripts/generate_image.py "Professional headshot" --negative "cartoon, anime" --seed 42

# Open image after generation
./scripts/generate_image.py "A beautiful garden" --open
```

### Aspect Ratios

- `square` (default) - 1:1
- `square_hd` - 1:1 high resolution
- `portrait_4_3` - 3:4 portrait
- `portrait_16_9` - 9:16 tall portrait
- `landscape_4_3` - 4:3 landscape
- `landscape_16_9` - 16:9 widescreen
- `21_9` - Ultra-wide
- `9_21` - Ultra-tall

## Image-to-Video Generation

Animate static images into videos.

### Available Models

| Model | Description | Quality |
|-------|-------------|---------|
| `kling` (default) | Kling v1.5 Pro | Excellent |
| `minimax` | MiniMax video | Good |
| `luma` | Luma Dream Machine | Good |
| `runway-gen3` | Runway Gen-3 Turbo | Excellent |
| `hunyuan` | Hunyuan video | Good |

### Usage

```bash
# Basic video generation
./scripts/generate_video.py image.png

# With motion prompt
./scripts/generate_video.py portrait.jpg --prompt "person slowly smiles and nods"

# Different model and duration
./scripts/generate_video.py landscape.png --model runway-gen3 --duration 10

# Specify output path
./scripts/generate_video.py photo.jpg --output ./videos/animated.mp4 --open
```

### Tips for Video Generation

1. **Image quality matters** - Use high-resolution, clear images
2. **Simple motion prompts** - Describe the motion, not the scene
3. **Duration limits** - Most models support 5-10 seconds
4. **Aspect ratio** - Usually auto-detected from the input image

## Text-to-Speech

Convert text to natural-sounding speech.

### Available Models

| Model | Description | Features |
|-------|-------------|----------|
| `f5-tts` (default) | F5-TTS | Voice cloning |
| `kokoro` | Kokoro | Multiple voices |
| `playht` | PlayHT v3 | High quality |
| `minimax-tts` | MiniMax TTS | Fast |

### Usage

```bash
# Basic text-to-speech
./scripts/generate_speech.py "Hello, welcome to our application!"

# Different model
./scripts/generate_speech.py "This is a test." --model kokoro

# Voice cloning with reference audio
./scripts/generate_speech.py "Clone this voice" --reference my_voice.mp3

# Adjust speed
./scripts/generate_speech.py "Speaking faster now" --speed 1.2

# Specify output and open
./scripts/generate_speech.py "Podcast intro" --output intro.wav --open
```

### Voice Cloning

To clone a voice, provide a reference audio sample:

```bash
./scripts/generate_speech.py "Text in cloned voice" --reference sample.mp3 --model f5-tts
```

Best practices for reference audio:
- 5-30 seconds of clear speech
- Minimal background noise
- Single speaker
- Natural speaking pace

## Common Workflows

### Create a Short Video from Scratch

```bash
# 1. Generate the image
./scripts/generate_image.py "A majestic eagle perched on a cliff" --model flux-pro --output eagle.png

# 2. Animate it
./scripts/generate_video.py eagle.png --prompt "eagle spreads wings and takes flight" --open
```

### Generate Marketing Assets

```bash
# Product image variations
./scripts/generate_image.py "Minimalist product photo of headphones on white background" --num 4 --aspect square_hd

# Social media formats
./scripts/generate_image.py "Summer sale banner" --aspect landscape_16_9 --output banner_wide.png
./scripts/generate_image.py "Summer sale banner" --aspect portrait_16_9 --output banner_story.png
```

### Create Voiceover

```bash
# Generate narration
./scripts/generate_speech.py "Welcome to our product demo. Today we'll explore the amazing features..." --output narration.wav

# With custom voice
./scripts/generate_speech.py "Welcome to our product demo." --reference brand_voice.mp3 --output narration.wav
```

## API Reference

All scripts are built on the shared `fal_helper.py` library. You can import it directly for programmatic use:

```python
from fal_helper import FalClient

client = FalClient()

# Generate images
images = client.generate_image(
    prompt="A beautiful sunset",
    model="flux-schnell",
    aspect_ratio="landscape_16_9",
    num_images=2,
)

# Generate video
video = client.generate_video(
    image_path="image.png",
    prompt="camera slowly pans right",
    model="kling",
    duration=5.0,
)

# Text to speech
audio = client.text_to_speech(
    text="Hello world",
    model="f5-tts",
    reference_audio="voice_sample.mp3",  # optional
)

# Download results
client.download_file(images[0]["url"], "output.png")
```

## Troubleshooting

### "FAL_API_KEY environment variable is not set"

Set your API key:
```bash
export FAL_API_KEY="your-key-here"
```

### Video generation is slow

Video generation typically takes 2-5 minutes. The models process frames sequentially which takes time.

### Image quality issues

- Try a higher-quality model (`flux-pro` instead of `flux-schnell`)
- Use more specific prompts
- Add negative prompts to avoid unwanted elements
- Use `square_hd` for higher resolution

### Voice cloning sounds off

- Ensure reference audio is clear with no background noise
- Use 10-30 seconds of reference audio
- The reference should be natural speech, not singing or whispering
- Try the `f5-tts` model which has the best voice cloning

## Notes

- All scripts auto-install dependencies via `uv run`
- Generated files include timestamps to avoid overwrites
- Use `--open` flag to immediately view/play generated media
- Video generation consumes more API credits than images
- Some models may have content restrictions
