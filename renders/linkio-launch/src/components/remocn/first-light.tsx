"use client";

import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";

export interface FirstLightProps {
  src?: string;
  tagline: string;
  color: string;
  background: string;
}

const fade = (frame: number, from: number, to: number) =>
  interpolate(frame, [from, to], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.45, 0, 0.55, 1),
  });

// Cut down to soft fades only: brand/MOTION.md rules out the original sun line
// and outline climb. Wordmark in over 0.7s, end line in by 1.5s.
export function FirstLight({
  src = "wordmark.png",
  tagline,
  color,
  background,
}: FirstLightProps) {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        background,
        alignItems: "center",
        justifyContent: "center",
        gap: 72,
      }}
    >
      <Img
        src={staticFile(src)}
        style={{ width: 648, opacity: fade(frame, 0, 21) }}
      />
      <div
        style={{
          maxWidth: "84%",
          textAlign: "center",
          fontFamily: "var(--font-geist-sans)",
          fontWeight: 700,
          fontSize: 76,
          lineHeight: 1.05,
          letterSpacing: "-0.02em",
          color,
          opacity: fade(frame, 24, 45),
        }}
      >
        {tagline}
      </div>
    </AbsoluteFill>
  );
}
