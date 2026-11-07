"use client";

import { loadFont } from "@remotion/google-fonts/Geist";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  AbsoluteFill,
  continueRender,
  delayRender,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type { GradientParams } from "@/lib/remocn/gsh/gradient-engine";
import { GshGround } from "@/lib/remocn/gsh/gsh-ground";
import type { GshPresetId } from "@/lib/remocn/gsh/presets";

const onest = loadFont("normal", {
  weights: ["700"],
  subsets: ["latin"],
});
const serif = onest;

export interface LooksLikeThisProps {
  lead?: string;
  word?: string;
  end?: string;
  src?: string;
  aspect?: number;
  accent?: string;
  background?: string;
  speed?: number;
  theme?: "dark" | "light";
  ground?: GshPresetId;
  groundParams?: Partial<GradientParams>;
}

const THEMES = {
  dark: {
    ink: "#F4F3EF",
    accent: "#B4C3FF",
    well: "#101218",
    preset: "velvet-hour" as GshPresetId,
    groundOffset: 6,
    edge: "rgba(255,255,255,0.1)",
    lift: "0 2px 6px rgba(0,0,0,0.35), 40px 90px -24px rgba(0,0,0,0.75)",
  },
  light: {
    ink: "#141519",
    accent: "#2D46D6",
    well: "#dfe2e8",
    preset: "glasswork" as GshPresetId,
    groundOffset: 3,
    edge: "rgba(0,0,0,0.1)",
    lift: "0 2px 6px rgba(30,30,60,0.08), 40px 90px -24px rgba(30,30,70,0.32)",
  },
} as const;

const WGHT = 700;
const TRACK = -0.02;
const SERIF_TRACK = -0.02;
const PX = 200;
const CHIP_H = 0.74;
const CHIP_GAP = 0.14;

const TYPE_IN = Easing.bezier(0.22, 1, 0.36, 1);
const CLAMP = {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
} as const;

type Measure = { sans: (s: string) => number; serif: (s: string) => number };

function buildMetrics(_version: number): Measure {
  const ctx = document.createElement("canvas").getContext("2d");
  const make = (font: string, track: number) => {
    const cache: Record<string, number> = {};
    return (s: string) => {
      if (cache[s] === undefined) {
        if (!ctx) return s.length * 0.5;
        ctx.font = font;
        cache[s] = ctx.measureText(s).width / PX + track * Array.from(s).length;
      }
      return cache[s];
    };
  };
  return {
    sans: make(`${WGHT} ${PX}px "${onest.fontFamily}"`, TRACK),
    serif: make(`${WGHT} ${PX}px "${serif.fontFamily}"`, SERIF_TRACK),
  };
}

function useMetrics() {
  const [version, setVersion] = useState(0);
  const [handle] = useState(() => delayRender("looks-like-this: measuring"));
  const released = useRef(false);
  useEffect(() => {
    let live = true;
    const bump = () => {
      if (live) setVersion((v) => v + 1);
    };
    document.fonts.addEventListener("loadingdone", bump);
    Promise.all([
      onest.waitUntilDone(),
      serif.waitUntilDone(),
      document.fonts.load(`${WGHT} 100px "${onest.fontFamily}"`),
      document.fonts.load(`${WGHT} 100px "${serif.fontFamily}"`),
    ])
      .catch(() => undefined)
      .then(() => {
        bump();
        if (!released.current) {
          released.current = true;
          continueRender(handle);
        }
      });
    return () => {
      live = false;
      document.fonts.removeEventListener("loadingdone", bump);
    };
  }, [handle]);
  return useMemo(() => buildMetrics(version), [version]);
}

interface Token {
  w: number;
  gap: number;
  glue?: boolean;
}

interface Placed {
  x: number;
  y: number;
}

function layout(
  tokens: Token[],
  size: number,
  maxW: number,
  centerX: number,
  topY: number,
  leading: number,
) {
  const lines: number[][] = [[]];
  let run = 0;
  tokens.forEach((t, i) => {
    const line = lines[lines.length - 1];
    const add = (line.length > 0 ? t.gap : 0) + t.w;
    if (line.length > 0 && (run + add) * size > maxW) {
      if (t.glue && line.length > 1) {
        const prev = line.pop() as number;
        lines.push([prev, i]);
        run = tokens[prev].w + t.gap + t.w;
      } else {
        lines.push([i]);
        run = t.w;
      }
    } else {
      line.push(i);
      run += add;
    }
  });
  const placed: Placed[] = new Array(tokens.length);
  lines.forEach((line, li) => {
    const total = line.reduce(
      (acc, i, k) => acc + tokens[i].w + (k > 0 ? tokens[i].gap : 0),
      0,
    );
    let x = centerX - (total * size) / 2;
    line.forEach((i, k) => {
      if (k > 0) x += tokens[i].gap * size;
      placed[i] = { x, y: topY + li * leading * size };
      x += tokens[i].w * size;
    });
  });
  return { placed, lines: lines.length };
}

export function LooksLikeThis({
  lead = "Your next launch looks like",
  word = "this",
  end = ".",
  src,
  aspect = 16 / 9,
  accent,
  background,
  speed = 1,
  theme = "dark",
  ground,
  groundParams,
}: LooksLikeThisProps) {
  const frame = useCurrentFrame();
  const { width: W, height: H, durationInFrames: D } = useVideoConfig();
  const c = THEMES[theme];
  const hi = accent ?? c.accent;
  const image = src ?? staticFile("hero.png");
  const m = useMetrics();

  const words = lead.split(/\s+/).filter(Boolean);
  const k = Math.min(1.6, Math.max(0.6, D / 150));
  const t = frame * speed;
  const portrait = H > W * 1.1;
  const u = portrait ? W / 1080 : W / 1280;
  const sp = m.sans(" ");
  const chipW = CHIP_H * aspect;
  const leading = 1.08;
  const wordW = m.serif(word);
  const endW = m.sans(end);

  const tokensA: Token[] = [
    ...words.map((wd) => ({ w: m.sans(wd), gap: sp })),
    { w: chipW + CHIP_GAP * 2 + endW, gap: sp - CHIP_GAP, glue: true },
  ];
  const tokensB: Token[] = [
    ...words.map((wd) => ({ w: m.sans(wd), gap: sp })),
    { w: wordW + endW, gap: sp, glue: true },
  ];

  const maxW = W * (portrait ? 0.84 : 0.8);
  const lineA = tokensA.reduce(
    (acc, tk, i) => acc + tk.w + (i > 0 ? tk.gap : 0),
    0,
  );
  const sizeA = Math.max(
    portrait ? W * 0.095 : H * 0.075,
    Math.min(portrait ? W * 0.12 : H * 0.12, maxW / lineA),
  );
  const sizeB = portrait ? W * 0.085 : H * 0.074;

  const probeA = layout(tokensA, sizeA, maxW, W / 2, 0, leading);
  const blockA = (probeA.lines - 1) * leading * sizeA + sizeA;
  const A = layout(tokensA, sizeA, maxW, W / 2, (H - blockA) / 2, leading);

  const probeB = layout(tokensB, sizeB, maxW, W / 2, 0, leading);
  const blockB = (probeB.lines - 1) * leading * sizeB + sizeB;
  const gapB = H * (portrait ? 0.035 : 0.05);
  const heroMaxW = W * (portrait ? 0.7 : 0.72);
  const heroAspect = portrait ? Math.min(aspect, 1) : aspect;
  const heroRoom = H * (portrait ? 0.78 : 0.8) - blockB - gapB;
  const heroH = Math.min(heroRoom, heroMaxW / heroAspect);
  const heroW = heroH * heroAspect;
  const topB = portrait ? (H - (blockB + gapB + heroH)) / 2 : H * 0.085;
  const B = layout(tokensB, sizeB, maxW, W / 2, topB, leading);
  const hero = {
    x: (W - heroW) / 2,
    y: topB + blockB + gapB,
    w: heroW,
    h: heroH,
  };

  // Text set in place, capture soft fades in at final size: MOTION.md rules out the chip morph.
  const FADE_AT = 12;
  const FADE_END = 36;

  const p = 1;
  const pChip = 1;
  const lerp = (a: number, b: number, q: number) => a + (b - a) * q;
  const size = lerp(sizeA, sizeB, p);

  const last = words.length;
  const slotA = A.placed[last];
  const chipRect0 = {
    x: slotA.x + CHIP_GAP * sizeA,
    y: slotA.y + sizeA * (0.6 - CHIP_H / 2),
    w: chipW * sizeA,
    h: CHIP_H * sizeA,
  };
  const chipY = lerp(chipRect0.y, hero.y, pChip);
  const lineFloor = lerp(slotA.y, B.placed[words.length].y, p) + size * 1.14;
  const leave = interpolate(pChip, [0, 0.14], [0, 1], CLAMP);
  const chip = {
    x: lerp(chipRect0.x, hero.x, pChip),
    y: lerp(chipY, Math.max(chipY, lineFloor), leave),
    w: lerp(chipRect0.w, hero.w, pChip),
    h: lerp(chipRect0.h, hero.h, pChip),
  };
  const radius = lerp(sizeA * 0.12, 16 * u, pChip);
  const settle = interpolate(t, [FADE_END, D], [1, 1.06], CLAMP);
  const imgScale = lerp(1.2, settle, pChip);

  const endA = {
    x: slotA.x + (CHIP_GAP * 2 + chipW) * sizeA,
    y: slotA.y,
  };
  const slotB = B.placed[last];
  const endB = { x: slotB.x + wordW * sizeB, y: slotB.y };
  const endY = lerp(endA.y, endB.y, p);

  const wordIn = interpolate(t, [last * 2.5 * k, last * 2.5 * k + 12 * k], [0, 1], {
    ...CLAMP,
    easing: TYPE_IN,
  });

  const prevA = A.placed[last - 1];
  const prevB = B.placed[last - 1];
  const wordX =
    last > 0
      ? lerp(prevA.x, prevB.x, p) + (m.sans(words[last - 1]) + sp) * size
      : lerp(slotA.x, slotB.x, p);

  const endX = lerp(
    endA.x,
    wordX + wordW * size,
    interpolate(p, [0, 0.55], [0, 1], { ...CLAMP, easing: TYPE_IN }),
  );

  const flat = background !== undefined;

  const textStyle = {
    position: "absolute" as const,
    left: 0,
    top: 0,
    fontFamily: onest.fontFamily,
    fontWeight: WGHT,
    fontSize: size,
    lineHeight: 1,
    letterSpacing: `${TRACK}em`,
    whiteSpace: "pre" as const,
    color: c.ink,
  };

  const visW = chip.w;

  return (
    <AbsoluteFill
      style={{
        background:
          flat && background !== "transparent" ? background : undefined,
        overflow: "hidden",
      }}
    >
      {flat ? null : (
        <GshGround
          preset={ground ?? (groundParams ? undefined : c.preset)}
          params={groundParams}
          timeOffset={c.groundOffset}
          timeScale={0.4}
        />
      )}
      {words.map((wd, i) => {
        const a = A.placed[i];
        const b = B.placed[i];
        const enter = interpolate(
          t,
          [i * 2.5 * k, i * 2.5 * k + 12 * k],
          [0, 1],
          { ...CLAMP, easing: TYPE_IN },
        );
        const x = lerp(a.x, b.x, p);
        const y = lerp(a.y, b.y, p);
        return (
          <span
            key={`${wd}-${i.toString()}`}
            style={{
              ...textStyle,
              transform: `translate(${x}px, ${y}px)`,
              opacity: enter,
            }}
          >
            {wd}
          </span>
        );
      })}
      <span
        style={{
          ...textStyle,
          transform: `translate(${endX}px, ${endY}px)`,
          opacity: interpolate(t, [10 * k, 18 * k], [0, 1], {
            ...CLAMP,
            easing: TYPE_IN,
          }),
        }}
      >
        {end}
      </span>
      <span
        style={{
          ...textStyle,
          fontFamily: serif.fontFamily,
          fontWeight: WGHT,
          letterSpacing: `${SERIF_TRACK}em`,
          color: hi,
          transform: `translate(${wordX}px, ${lerp(slotA.y, slotB.y, p)}px)`,
          opacity: wordIn,
        }}
      >
        {word}
      </span>
      <div
        style={{
          position: "absolute",
          left: chip.x + (chip.w - visW) / 2,
          top: chip.y,
          width: visW,
          height: chip.h,
          borderRadius: radius,
          overflow: "hidden",
          background: c.well,
          boxShadow: pChip > 0.3 ? c.lift : "none",
          opacity: interpolate(t, [FADE_AT, FADE_END], [0, 1], {
            ...CLAMP,
            easing: TYPE_IN,
          }),
        }}
      >
        <Img
          src={image}
          style={{
            position: "absolute",
            left: -(chip.w - visW) / 2,
            top: 0,
            width: chip.w,
            height: chip.h,
            objectFit: "cover",
            transform: `scale(${imgScale})`,
          }}
        />
        <div
          style={{
            position: "absolute",
            inset: 0,
            borderRadius: "inherit",
            boxShadow: `inset 0 0 0 1px ${c.edge}`,
          }}
        />
      </div>
    </AbsoluteFill>
  );
}
