# Concept Generation Guide

Template for generating new video concepts based on analyzed competitor content. Used as a reference for Claude when generating concepts inline.

## Generation Template

When generating new concepts for a client, follow this structure. Replace `{{variables}}` with actual client data from `client-profiles.md`.

---

**Role:** You are an expert in creating viral short-form video content.

**Task:** Based on the reference video analysis below, generate 3 NEW video concepts adapted for **{{client.name}}**.

**Rules:**
- Do not copy the original
- Translate the core idea into the {{client.niche}} context
- Mainly iterate and sharpen the HOOKS — the hook is the most valuable part
- The first 3 seconds must stop {{client.audience}} from scrolling
- Each concept MUST cite which reference video(s) inspired it using GFM footnote syntax (`[^1]`, `[^2]`) and what specific element was adapted

**Style guidelines:**
{{client.style}}

**Reference video analysis:**
{{video_analysis}}

---

## Output Format

Each concept MUST be emitted as a **human section followed by a typed JSON block**. Both are mandatory.

### Human Section (goes into report's `## Content Concepts`)

```
# CONCEPT 1
Text description of the concept (1-3 sentences)

## HOOK
Detailed hook description (1-3 sentences)
- What is seen in the first 2 seconds
- What is said in the first line
- Why this hook works for {{client.audience}}

## SCRIPT
Detailed script (1-20 sentences, as many as needed)
- Scene flow
- Spoken text / voiceover
- Clear payoff
- Tone matching {{client.name}}'s style

## SOURCES
- Inspired by: [^N] @creator — what specific element was adapted
```

### Typed JSON Block (goes into report's `## HANDOFF`)

Immediately after each human section, emit a fenced JSON block with fixed fields. The orchestrator will aggregate these into the final HANDOFF array.

```json
{
  "id": 1,
  "source_signature": {
    "format_type": "one-line archetype label (e.g. 'POV gym fail with non-shame recovery')",
    "mechanic": "one-line near-verbatim from CONCEPT/RETENTION — HOW the source grabs attention",
    "must_preserve": [
      "concrete element 1 (specific gesture, secondary actor, prop, transition — copied verbatim from Gemini RETENTION+SCRIPT)",
      "concrete element 2",
      "concrete element 3"
    ]
  },
  "brand_adaptation": {
    "topic_shift": "from <source topic> → <client topic>",
    "payoff_message": "one line: what the closing beat says about the brand"
  },
  "hook": {
    "visual": "what is seen in the first 2 seconds — every actor, gesture, framing, lighting verbatim",
    "line": "first spoken line verbatim (empty string if no speech)",
    "psychology": "curiosity_gap",
    "sound_cue": "audio cue at hook moment (empty string if none)",
    "on_screen_text": [
      {"text": "verbatim overlay copy with emoji preserved", "position": "top-center", "animation": "fade-in", "appears_at_s": 0.5, "duration_s": 1.5}
    ],
    "reference_url": "https://..."
  },
  "beats": [
    {
      "visual": "scene description verbatim — every actor, gesture, prop, camera, lighting",
      "on_screen_text": [{"text": "...", "position": "...", "animation": "...", "appears_at_s": 0, "duration_s": 0}],
      "audio": "sound design directive",
      "speech": "spoken dialogue verbatim (empty string if none)",
      "duration_s": 4
    }
  ],
  "total_duration_s": 12,
  "audio_overall": "track type + BPM + mood (no track names)",
  "reference_urls": ["https://..."],
  "tier": "director",
  "style_preset": "entertainment"
}
```

Repeat both blocks (human + JSON) for CONCEPT 2 and CONCEPT 3. Footnote definitions go at the very end:

```
[^1]: @creator — platform — Source URL
[^2]: @creator — platform — Source URL
```

## Final Envelope (emit ONCE after all CONCEPT blocks)

After all CONCEPT N blocks (and their per-concept JSON), emit a single final fenced JSON block under `## HANDOFF` that wraps every concept into the envelope expected by `video-generation` / `image-generation`:

```json
{
  "schema_version": "2",
  "mode": "research_to_video",
  "concepts": [
    /* paste each concept JSON in order — concept 1, concept 2, concept 3 */
  ],
  "client_brand": null
}
```

If `brand-analyzer` was run this turn and produced a brand pack, replace `"client_brand": null` with the full brand-analyzer payload (see `brand-analyzer` SKILL.md for the exact shape).

For image targets use `"mode": "research_to_image"` and the image-concept schema (`subject`, `must_preserve[]`, `visual_dna`, `text_overlay`) instead of the video schema.

**Without this envelope, downstream generation skills silently fall through to manual prompt construction — captions get rebuilt from scratch and the upstream video analysis is wasted.**

---

## Hook Psychology (required taxonomy)

The `hook.psychology` field in the JSON block must be exactly ONE of these 7 values. Pick the single dominant mechanism that makes the viewer stop. Copy the string literally (snake_case, no synonyms).

- `fear_of_loss` — viewer senses they're missing out, will regret skipping, or about to lose something. Signals: "stop scrolling if…", "don't buy X before…", countdown / expiring framing.
- `curiosity_gap` — a question is opened, unanswered. Paradox, covered object, unfinished reveal. Signals: "wait until you see…", "I tried X and…", "nobody told me…".
- `identity_relevance` — hook calls out the viewer's specific identity / role / situation. Signals: "if you're a <role>…", "<city> people only…", "for anyone who hates X…".
- `authority_flip` — credible figure states the opposite of common belief. Signals: "as a doctor, I'd never…", "stop doing X…", credentials visible on screen.
- `shock_visual` — unexpected visual carries the hook. Extreme before/after, transformation, "is this real?" framing. Often minimal speech.
- `social_proof` — signals many others are doing / buying / loving the thing. Signals: "everyone is obsessed…", "10M people already…", crowd shots, "trending now" overlays.
- `pattern_break` — first frame breaks the expected feed format. Unusual aspect, black screen + single word, silence after loud scroll, extreme close-up of unusual object.

If a hook seems to fit two categories, pick the dominant one. Never invent new categories, never combine categories, never use a synonym.

## Style Presets

When generating concepts, match the client's tone. Common presets:

### Authority (business, real estate, finance)
- Calm confidence > hype
- Emotional credibility > performance
- No shouting, no buzzwords, no exaggeration
- Subtle authority, not selling

### Practical (tech, AI, productivity)
- Practical value > hype
- Show, don't just tell
- No buzzwords, no exaggeration
- Demonstration of the tool or workflow

### Entertainment (lifestyle, travel, food)
- Energy and personality
- Visual storytelling > talking head
- Relatable moments > polished perfection
- Authentic reactions

### Educational (coaching, tutorials, how-to)
- Clear structure > clever delivery
- One lesson per video
- Immediate takeaway
- "You can do this too" framing
