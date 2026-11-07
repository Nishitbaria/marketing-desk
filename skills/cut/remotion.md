# Remotion and remocn

Cut builds every video as a Remotion project made of remocn components. remocn is a shadcn registry: each component is copied into the project and takes its copy, colours and images as props.

## Commands

Run from the repo root. Keep the pinned versions, so a project re-renders the same way later.

If `renders/<slug>/` exists with no `remotion.config.ts`, it is an old project. Use a new slug such as `<slug>-v2`. If it has one, skip the `create-video`, `rm` and `setup.mjs` lines.

```bash
npx --yes create-video@4.0.541 --yes --blank renders/<slug>
rm -rf renders/<slug>/.git
cd renders/<slug>
node ../../skills/cut/remocn/setup.mjs .
mkdir -p out public
curl -s https://remocn.dev/llms-components.txt -o out/components.txt
npx --yes shadcn@4.23.0 add --yes --overwrite @remocn/<name> @remocn/<name>
npm i --save-exact @remotion/sfx@4.0.541 @remotion/transitions@4.0.541
cp ../../skills/cut/audio/lofi-76bpm.mp3 public/
npx tsc --noEmit
npx remotion still video out/f<frame>.png --frame=<frame> --gl=angle --scale=0.5
npx remotion render video <slug>.mp4 --gl=angle
npx remotion ffprobe -v error -show_entries stream=codec_name,width,height -show_entries format=duration -of default=nw=1 <slug>.mp4
```

`src/Root.tsx` registers one composition with `id="video"`, `fps={30}` and the width and height from the script's Format line. Ignore the Rspack warning from `remotion ffprobe`.

## Build

1. Read `skills/cut/remocn/SKILL.md` and `references/anatomy.md`, then pick the recipe in `references/archetypes/index.md`. A launch uses `product-demo.md` or `feature-announcement.md`.
2. Map each script beat to one component. Search `out/components.txt` with grep. It is 258 KB, so do not read it whole. Match `Use for`, `Avoid for` and `vibe`.
3. Fetch the docs page of each pick with `curl -s <docs url>.md`. Use only props that page lists.
4. Chain the beats in `Series` or `TransitionSeries` in `src/Root.tsx`. `Length` is a floor, so add hold time to meet the brand's timing rules.

## Real product screens

If the script names a website, capture it and show it in a Media or browser component. A launch with no product on screen is only text.

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=6000 --window-size=1440,900 --screenshot="$PWD/public/site.png" <url>
```

Pass it as `staticFile("site.png")`. A plain file name fails, and a demo default fails with `handleImageError`, so pass your own image to every image prop. Words inside this real capture are the only words that may differ from the script.

Never fill a product scene with sample data. Rows, charts, names and numbers count as facts. Use them only when the script gives them.

## Look rules

- Colours come from `brand/MOTION.md`. Set them on every beat, or the default blue or orange ground shows. A component with `ground` takes `groundParams={{ colors: ["<accent>", "<dark>"], background: "<bg>" }}` plus `accent`. A component with no `ground` takes `background="<bg>"` and `accent`.
- One accent per frame, on one word or one action.
- No two beats share a layout. Use each component once. Mix type, a product screen, a stat and a closing card.
- Typing appears only inside a product input. Never use a typewriter on a headline.
- Skip any component that breaks the Never list in `brand/MOTION.md`, such as `whip-pan`, glitch or glow.
- remocn lays out for 1280x720. In 9:16, prefer Social creator formats and Device frames, and look at every beat for empty space and clipped text.

## Default leaks

Component defaults are remocn's own demo copy, and they show up in your video if you skip a prop.

- Run `grep -n ' = "\|DEFAULT_\|emocn\|REMOCN_R_PATH' src/components/remocn/<name>.tsx` after install. Pass a script word for every text default.
- A prop that is not in the script stays visible even when empty, such as the `$` from `command` in `url-bar-cta`. Delete that element from the copied file.
- Replace the hard-coded remocn logo in the copied file with the product name from the script.
- Components load their own fonts. To use the brand font, change the `loadFont` import in the copied file.

## Transitions

Every beat change gets a transition, never a hard cut. Use `TransitionSeries` with `fade()` from `@remotion/transitions/fade` and `linearTiming({ durationInFrames: 15 })`. Each transition overlaps two beats, so the total is the sum of the beats minus 15 frames per transition. Set `durationInFrames` to that total.

## Sound

Every video has background music and small interaction sounds. Add them after the picture works. Every source below is free to use with no credit needed, so use nothing else and download nothing else.

| Moment | Sound | Volume |
| --- | --- | --- |
| Each transition, starting on the first frame of the fade | `whoosh` | 0.3 |
| A click or tap in a product screen | `mouseClick` | 0.5 |
| A toggle, or a card or stat landing | `uiSwitch` | 0.4 |
| A new page or section in a product screen | `pageTurn` | 0.4 |

Import them from `@remotion/sfx`. Keep sounds small: at most one per second, and none on text that simply fades in. The other sounds in that package are memes or have an unclear license, so never use them.

```tsx
import { AbsoluteFill, Audio, Sequence, interpolate, staticFile } from "remotion";
import { whoosh } from "@remotion/sfx";

const Sfx = ({ src, at, volume }: { src: string; at: number; volume: number }) => (
  <Sequence from={at} layout="none"><Audio src={src} volume={volume} /></Sequence>
);

const music = (f: number) =>
  interpolate(f, [0, 30, TOTAL - 45, TOTAL], [0, 0.6, 0.6, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

// Beside the TransitionSeries, inside one AbsoluteFill:
<Audio src={staticFile("lofi-76bpm.mp3")} loop volume={music} />
<Sfx src={whoosh} at={firstFrameOfFade} volume={0.3} />
```

`lofi-76bpm.mp3` is the studio's own 50s loop.

### Voiceover

Voice makes the voiceover, Cut places it. If Voice's post says `Tier: none`, skip this part.

1. Copy `renders/<slug>-voice/*.wav` into `public/voice/`.
2. Read `renders/<slug>-voice/manifest.txt`. Each line is `start|length|file|ok`, in seconds.
3. Place one clip per line beside the `TransitionSeries`, at the script's start second. Keep each clip at volume 1.

```tsx
<Sfx src={staticFile("voice/02.wav")} at={3 * 30} volume={1} />
```

4. Drop the music from 0.6 to 0.2 so it ducks.

Clips use the script's timestamps, so they stay on the beat even though transitions overlap. Set `TOTAL` to the Format length, and give the last beat enough hold that the video still matches it.

## Rules

- Deterministic only. No `Math.random()`, `Date.now()` or timers. Use `useCurrentFrame()`.
- Any component with a `ground` prop needs `--gl=angle`, or the ground renders black.
- A still has no sound. After the render, confirm `codec_name=aac` in the `ffprobe` output.
- Look at one still per beat before you render. `tsc` passing does not show how a frame looks. Compare every visible word with the script.
- No hosted rendering, no Remocn Studio upload, no `remotion lambda`.
