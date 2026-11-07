# HyperFrames core notes

HyperFrames renders one HTML composition to MP4. Condensed from the notes `hyperframes init` writes into each project, plus what failed while building `renders/notely-launch`.

## Commands

Pin the version, so a project re-renders the same way later. Run these from the repo root unless noted.

```bash
npx --yes hyperframes@0.9.19 init renders/<slug> --non-interactive --skip-skills
cd renders/<slug>
npx --yes hyperframes@0.9.19 check
npx --yes hyperframes@0.9.19 snapshot --at <one time per on-screen card>
npx --yes hyperframes@0.9.19 render --output <slug>.mp4
ffprobe -v error -show_entries stream=codec_name,width,height -show_entries format=duration -of default=nw=1 <slug>.mp4
```

Do not run `hyperframes skills update` or `npx skills add`. Installing skills is the creator's step.

## Composition rules

- `index.html` is the composition. The root element carries `data-composition-id`, `data-width`, `data-height`.
- Every timed element needs `data-start` and `data-duration`, plus `class="clip"`.
- Register one paused GSAP timeline per composition on `window.__timelines`, keyed by the composition id.
- Child timelines added to the root must not be paused.
- For 9:16, `init` writes 1920x1080, so set `data-width="1080"`, `data-height="1920"` and the matching `viewport` meta.
- Deterministic logic only. No `Date.now()`, no `Math.random()`, no network fetches at runtime.

## What `check` will stop on

- A `font-family` with no `@font-face` and no Google Fonts `<link>` is an error, even when the font appears to render. Declare every family.
- `first_frame_empty`: something must be visible at t=0. Do not fade the hook in from nothing.
- `dead_stretch`: a long still hold is flagged. Put `data-hold` on the element that holds on purpose.
- `film_silent` is expected. Studio videos have no audio until a voiceover exists.

## Before you call it done

`check` passing does not show how a frame looks. Snapshot one frame per on-screen card, since a beat can hold two cards, and look at each one. Compare every visible word with the script.
