"use client";

import { Easing, interpolate, useCurrentFrame } from "remotion";

export interface SoftBlurInProps {
  text: string;
  blur?: number;
  fontSize?: number;
  color?: string;
  fontWeight?: number;
  speed?: number;
  className?: string;
  highlight?: string;
  accent?: string;
}

export function SoftBlurIn({
  text,
  blur = 12,
  fontSize = 72,
  color = "#171717",
  fontWeight = 600,
  speed = 1,
  className,
  highlight,
  accent,
}: SoftBlurInProps) {
  const frame = useCurrentFrame() * speed;

  const chars = Array.from(text);
  const hiStart = highlight ? text.indexOf(highlight) : -1;
  const hiEnd = hiStart + (highlight?.length ?? 0);
  // Group by word so lines wrap on spaces, never inside a word.
  const words: { char: string; i: number }[][] = [[]];
  chars.forEach((char, i) => {
    words[words.length - 1].push({ char, i });
    if (char === " ") words.push([]);
  });
  const charDurationFrames = 27;
  const charTravelFrames = 9;
  const staggerFrames = 1;

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "transparent",
      }}
    >
      <span
        className={className}
        style={{
          fontSize,
          fontWeight,
          color,
          letterSpacing: "-0.02em",
          lineHeight: 1.05,
          textAlign: "center",
          maxWidth: "84%",
          fontFamily:
            "var(--font-geist-sans), -apple-system, BlinkMacSystemFont, sans-serif",
        }}
      >
        {words.map((word, w) => (
          <span key={w} style={{ display: "inline-block", whiteSpace: "pre" }}>
        {word.map(({ char, i }) => {
          const local = frame - i * staggerFrames;
          const easing = Easing.bezier(0.22, 1, 0.36, 1);
          const opacity = interpolate(local, [0, charDurationFrames], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing,
          });
          const y = interpolate(local, [0, charTravelFrames], [16, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing,
          });
          const blurAmount = interpolate(
            local,
            [0, charDurationFrames],
            [blur, 0],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing },
          );
          return (
            <span
              key={i}
              style={{
                display: "inline-block",
                whiteSpace: "pre",
                backfaceVisibility: "hidden",
                transformOrigin: "50% 55%",
                opacity,
                ...(i >= hiStart && i < hiEnd ? { color: accent, fontWeight: 800 } : null),
                translate: `0 ${y}px`,
                filter: `blur(${blurAmount}px)`,
              }}
            >
              {char}
            </span>
          );
        })}
          </span>
        ))}
      </span>
    </div>
  );
}
