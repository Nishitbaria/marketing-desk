---
name: montage
description: |
  Video assembly and post-processing for existing video files: concatenate/stitch/merge clips into one file, overlay background music, attach or burn subtitles, and similar edits.
---
# Montage Skill

Assemble multiple generated video clips into a single final video using ffmpeg.

## Transition Rule
**Default: hard cut.** All clips joined via direct concatenation with no transitions. Transitions allowed ONLY by explicit user request.

## Assembly Methods

### 1. Concatenation (hard cut)
```bash
for f in output/videos/shot_*.mp4; do echo "file '$f'" >> output/filelist.txt; done
ffmpeg -f concat -safe 0 -i output/filelist.txt -c copy output/final.mp4
```

### 2. Add Background Music
```bash
ffmpeg -i output/final.mp4 -i bgm.mp3 -c:v copy -c:a aac -shortest output/final_with_bgm.mp4
```

### 3. Burned captions (TikTok-style .ass)
Uses `scripts/make_captions.py` — mirrored from the capsmith production renderer.

1. Transcribe with `faster-whisper`: `python3 -m pip install -q faster-whisper`
2. Extract mono audio: `ffmpeg -y -i output/final.mp4 -vn -ac 1 -ar 16000 output/final_audio.wav`
3. Run transcription: `python3 ~/.hermes/skills/video-explainer-workflow/scripts/audio_to_captions.py output/final_audio.wav --json output/captions.json`
4. Render captions: `python3 $HOME/.hermes/skills/montage/scripts/make_captions.py output/segments.json -o output/captions.ass --size 50 --no-caps`
5. Burn: `ffmpeg -y -i output/final.mp4 -vf "ass=output/captions.ass:fontsdir=$HOME/.hermes/skills/montage/scripts/fonts" -c:a copy output/final_captioned.mp4`

## Quality Rule
Output resolution = source resolution. Never upscale, never downscale.

## Output
- Final video saved to `output/final.mp4`