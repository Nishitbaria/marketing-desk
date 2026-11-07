import { loadFont } from "@remotion/google-fonts/Geist";
import type { ReactNode } from "react";
import {
  AbsoluteFill,
  Composition,
  interpolate,
  Sequence,
  Series,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { FadeThrough } from "@/components/remocn/fade-through";
import { FirstLight } from "@/components/remocn/first-light";
import { LooksLikeThis } from "@/components/remocn/looks-like-this";
import { MaskRevealUp } from "@/components/remocn/mask-reveal-up";
import { SoftBlurIn } from "@/components/remocn/soft-blur-in";
import { StaggeredFadeUp } from "@/components/remocn/staggered-fade-up";

const { fontFamily } = loadFont("normal", {
  weights: ["400", "700", "800"],
  subsets: ["latin"],
});

const BG = "#FFFFFF";
const TEXT = "#0A0A0A";
const ACCENT = "#000000";

const FadeOut = ({ children }: { children: ReactNode }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const opacity = interpolate(
    frame,
    [durationInFrames - 10, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  return <AbsoluteFill style={{ opacity }}>{children}</AbsoluteFill>;
};

const Video = () => (
  <AbsoluteFill
    style={
      {
        background: BG,
        fontFamily,
        "--font-geist-sans": fontFamily,
      } as React.CSSProperties
    }
  >
    <Series>
      <Series.Sequence durationInFrames={90}>
        <FadeOut>
          <SoftBlurIn
            text="Where did your last click come from?"
            highlight="last click"
            accent={ACCENT}
            color={TEXT}
            fontSize={132}
            fontWeight={700}
            speed={2}
          />
        </FadeOut>
      </Series.Sequence>
      <Series.Sequence durationInFrames={210}>
        <FadeOut>
          <StaggeredFadeUp
            text="You post your link everywhere."
            color={TEXT}
            fontSize={150}
            fontWeight={700}
            staggerDelay={6}
          />
        </FadeOut>
      </Series.Sequence>
      <Series.Sequence durationInFrames={210}>
        <FadeOut>
          <LooksLikeThis
            lead="A page that looks like"
            word="you"
            end=""
            src={staticFile("site-hero.png")}
            aspect={500 / 590}
            accent={ACCENT}
            background={BG}
            theme="light"
          />
        </FadeOut>
      </Series.Sequence>
      <Series.Sequence durationInFrames={150}>
        <FadeOut>
          <FadeThrough
            fromText=""
            toText="Where every click came from"
            color={TEXT}
            fontSize={120}
            fontWeight={700}
            top={384}
          />
          <Sequence from={70}>
            <FadeThrough
              fromText=""
              toText="Country, device, browser, referrer"
              color={TEXT}
              fontSize={120}
              fontWeight={400}
              top={708}
              lineHeight={1.5}
            />
          </Sequence>
        </FadeOut>
      </Series.Sequence>
      <Series.Sequence durationInFrames={136}>
        <MaskRevealUp
          text={"Start for free\nlinkio.site/signup"}
          color={TEXT}
          fontSize={112}
          fontWeight={700}
          bottom={460}
        />
      </Series.Sequence>
      <Series.Sequence durationInFrames={104}>
        <FirstLight
          tagline="Your audience is clicking. Start counting."
          color={TEXT}
          background={BG}
        />
      </Series.Sequence>
    </Series>
  </AbsoluteFill>
);

export const RemotionRoot: React.FC = () => (
  <Composition
    id="video"
    component={Video}
    durationInFrames={900}
    fps={30}
    width={1080}
    height={1920}
  />
);
