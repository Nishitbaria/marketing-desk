import { useEffect, useRef, useState } from "react"
import { ArrowUpRight, ChevronRight, Moon, RotateCcw, Sun } from "lucide-react"

import { Bubble, BubbleContent } from "@/components/ui/bubble"
import { Button } from "@/components/ui/button"
import {
  Message,
  MessageAvatar,
  MessageContent,
  MessageGroup,
  MessageHeader,
} from "@/components/ui/message"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { cn } from "@/lib/utils"

const REPO = "https://github.com/Nishitbaria/studio-desk"
const CLONE = `git clone ${REPO}`
const SECTIONS = ["run", "try", "team", "facts", "proof", "setup"]

const ASK =
  "@Director 30s launch video for One-Person Studio, and say how many creators use it"
const NODES = ["you", "director", "quill", "keeper", "voice", "cut"]

const RELAY = [
  { who: "you", text: "One line." },
  { who: "director", text: "BRIEF | One-Person Studio launch" },
  { who: "quill", text: "[need: creator count] creators use One-Person Studio." },
  { who: "keeper", text: "script ✓ · brand ✓" },
  { who: "voice", text: "script ✓ · brand ✓ · voice ✓" },
  { who: "cut", text: "RENDER | One-Person Studio launch" },
  { who: "keeper", text: "Verdict: FIX" },
  { who: "cut", text: "Re-rendering." },
  { who: "keeper", text: "Verdict: PASS" },
  {
    who: "director",
    text: "@user renders/one-person-studio-launch/one-person-studio-launch.mp4",
  },
  { who: "you", text: "Approve, or send your change." },
]

const TEAM = [
  {
    id: "director",
    name: "Director",
    job: "Leads the team. The only agent you talk to.",
    says: "BRIEF | One-Person Studio launch",
  },
  {
    id: "quill",
    name: "Quill",
    job: "Writes every word in the video.",
    says: "[need: creator count]",
  },
  {
    id: "keeper",
    name: "Keeper",
    job: "Checks scripts and renders against your brand.",
    says: "Verdict: FIX",
  },
  {
    id: "voice",
    name: "Voice",
    job: "Speaks the script, word for word.",
    says: "Tier: kokoro",
  },
  {
    id: "cut",
    name: "Cut",
    job: "Renders the MP4 with Remotion.",
    says: "Aspect: 9:16 (1080x1920)",
  },
]

const SHOTS = [
  {
    id: "script",
    label: "Script",
    src: "screens/02-chain.png",
    alt: "Director posts a brief with need markers, then Quill writes hooks and a timed script.",
    note: "Director writes a blank, not a number. Quill keeps the blank.",
  },
  {
    id: "fix",
    label: "FIX",
    src: "screens/03-keeper-fix.png",
    alt: "Keeper lists four exact fixes on a render, then Cut applies them and re-renders.",
    note: "Keeper samples pixels from the MP4, lists four fixes, and Cut applies all four.",
  },
  {
    id: "tag",
    label: "Your call",
    src: "screens/04-director-tag.png",
    alt: "Keeper passes the render and Director tags the creator with the MP4 path.",
    note: "Keeper passes it. Director tags you. It stops there.",
  },
]

type Post = {
  id: string
  label: string
  who: string
  at: string
  shot: number
  text: string
  fixes?: { at: string; issue: string; fix: string }[]
  after?: string
}

// Copied from the room in public/screens, trimmed. Do not edit the wording.
const POSTS: Post[] = [
  {
    id: "ask",
    label: "Ask",
    who: "user",
    at: "10:10 PM",
    shot: 0,
    text: "@Director 30s launch video for One-Person Studio, and say how many creators use it",
  },
  {
    id: "brief",
    label: "Brief",
    who: "director",
    at: "10:10 PM",
    shot: 0,
    text: "BRIEF | One-Person Studio launch\nFormat: launch\nLength: 30\nAspect: 9:16\nGoal: Launch One-Person Studio and say how many creators use it\nAudience: Creators\nKey message: [need: what One-Person Studio does and for whom] and [need: how many creators use One-Person Studio]\n@Quill write this",
  },
  {
    id: "script",
    label: "Script",
    who: "quill",
    at: "10:11 PM",
    shot: 0,
    text: "3 hook options\n1. Guess how many creators use One-Person Studio.\n2. [need: creator count] creators use One-Person Studio.\n3. Meet One-Person Studio. Now count the creators using it.\n\n3-10s PROBLEM\nSpoken: \"[need: the problem One-Person Studio solves for you]\"\n\n10-22s SOLUTION/DEMO\nSpoken: \"One-Person Studio [need: what it does and for whom]\"",
  },
  {
    id: "fix",
    label: "Keeper: FIX",
    who: "keeper",
    at: "10:22 PM",
    shot: 1,
    text: "BRAND CHECK | render | One-Person Studio launch\nVerdict: FIX\nIssues:",
    fixes: [
      {
        at: "24.4s to 30s",
        issue:
          "Four items in Accent #000000: wordmark, \"Get it on GitHub\", the link and the line (pixels sampled from the MP4). Accent is one thing per frame.",
        fix: "Keep only \"Get it on GitHub\" in #000000. Set the wordmark, link, line and ticks to Text #0A0A0A.",
      },
      {
        at: "22.3s to 23.8s",
        issue:
          "The wordmark arrives as an outline at about y 1095, climbs about 175px and fills in, passing through the line at 23.6s. MOTION says text comes in with a soft fade.",
        fix: "Remove the outline and the climb. Fade the solid wordmark in at its final position, about y 920, over 18 frames from the start of the beat.",
      },
      {
        at: "0s to 10s",
        issue:
          "The first two beats share a layout: a centred two-line headline at mid-frame. No two beats may share a layout.",
        fix: "Keep \"No team, no video.\" centred, as the shot list says. Move the hook to left-aligned in the upper third.",
      },
      {
        at: "10s to 22s",
        issue:
          "\"Your video team in one chat room.\" has letter spacing -0.03em. MOTION sets -0.02em for titles.",
        fix: "In micro-scale-fade.tsx set letterSpacing to \"-0.02em\".",
      },
    ],
    after: "cc @Director\nNext: @Cut please re-render",
  },
  {
    id: "status",
    label: "Status",
    who: "director",
    at: "10:22 PM",
    shot: 1,
    text: "script ✓ · brand ✓ · voice ✓ · render FIX 1 of 2 · re-rendering...",
  },
  {
    id: "render",
    label: "Re-render",
    who: "cut",
    at: "10:22 PM",
    shot: 1,
    text: "On it. Applying Keeper's four fixes and re-rendering.\nRENDER | One-Person Studio launch | re-render\nMP4: renders/one-person-studio-launch/one-person-studio-launch.mp4\nLength: 30.02s\nAspect: 9:16 (1080x1920)\nAudio codec: aac (video h264)\nVoice clips placed: 4 of 4",
  },
  {
    id: "pass",
    label: "Keeper: PASS",
    who: "keeper",
    at: "10:24 PM",
    shot: 2,
    text: "On it, re-measuring the new render.\nBRAND CHECK | render | One-Person Studio launch\nVerdict: PASS\nIssues: None\nNext: @Director approved render",
  },
  {
    id: "tag",
    label: "Your call",
    who: "director",
    at: "10:24 PM",
    shot: 2,
    text: "@user renders/one-person-studio-launch/one-person-studio-launch.mp4\nreply @Director approve or your change",
  },
]

const YOURS = [
  ["Approval", "Keeper's PASS is not approval. Only you close a video."],
  ["Publishing", "Agents never upload, post or publish."],
  ["Tools", "Every agent runs with auto_approve off, so risky calls ask you first."],
  ["Your computer", "The team runs from your repo on your Switch server. It is not a hosted app."],
]

const STEPS = [
  "Clone the repo.",
  "In Switch Console, run a server on this computer.",
  "Import agents/studio.template.yaml from Templates.",
  "Use the template, and set directory to this repo’s absolute path.",
  "Create agents and room, then tag @studio-director with one line.",
]

type Line = { who: string; text: string; status?: string }
type Stage = {
  lines: Line[]
  choices?: { label: string; say: string; next: string }[]
}

// ponytail: fixed script, nothing here calls an agent.
const STAGES: Record<string, Stage> = {
  ask: {
    lines: [],
    choices: [
      {
        label: "Send",
        say: "@studio-director 30s launch video for Driftnote Plus, and mention the price",
        next: "script",
      },
    ],
  },
  script: {
    lines: [
      {
        who: "director",
        text: "BRIEF | Driftnote Plus launch\nFormat: launch · Length: 30 · Aspect: 9:16\n@studio-quill write this",
        status: "script…",
      },
      {
        who: "quill",
        text: "Hooks, script and shot list are up.\nOn-screen: [need: price]\nready for @studio-keeper brand check",
      },
      {
        who: "keeper",
        text: "BRAND CHECK | script | Driftnote Plus launch\nVerdict: PASS\nThe script holds a need, so Cut does not start.\nNext: @studio-director ask the creator",
        status: "script ✓ · brand ✓ · waiting on you",
      },
      {
        who: "director",
        text: "Before we render, it still needs your input:\n- Price of Driftnote Plus: should it appear on screen?\nreply @studio-director with the answer",
      },
    ],
    choices: [
      {
        label: "Leave the price out",
        say: "@studio-director leave the price out",
        next: "render",
      },
      {
        label: "Point to the website",
        say: "@studio-director no price, point to the website",
        next: "render",
      },
    ],
  },
  render: {
    lines: [
      {
        who: "quill",
        text: "Need closed. Script updated.\nready for @studio-keeper brand check",
      },
      {
        who: "keeper",
        text: "Verdict: PASS\nNext: @studio-voice make the voice",
        status: "script ✓ · brand ✓ · voice…",
      },
      {
        who: "voice",
        text: "Tier: kokoro\nOne clip per beat.\n@studio-cut render it",
        status: "script ✓ · brand ✓ · voice ✓ · render…",
      },
      {
        who: "cut",
        text: "renders/driftnote-plus/driftnote-plus.mp4\n30.0s, 1080x1920, 9:16 (from ffprobe)\n@studio-keeper check render",
      },
      {
        who: "keeper",
        text: "BRAND CHECK | render | Driftnote Plus launch\nVerdict: FIX\nAccent is on two things in the last frame. Accent is one thing per frame.\nNext: @studio-cut please re-render",
      },
      {
        who: "director",
        text: "script ✓ · brand ✓ · voice ✓ · render FIX 1 of 2 · re-rendering…",
        status: "script ✓ · brand ✓ · voice ✓ · render FIX 1 of 2",
      },
      {
        who: "cut",
        text: "Fix applied, re-rendered.\n30.0s, 1080x1920, 9:16 (from ffprobe)\n@studio-keeper check render",
      },
      {
        who: "keeper",
        text: "Verdict: PASS\nIssues: None\nNext: @studio-director approved render",
        status: "script ✓ · brand ✓ · voice ✓ · render ✓ · waiting on you",
      },
      {
        who: "director",
        text: "@you renders/driftnote-plus/driftnote-plus.mp4\nreply @studio-director approve or your change",
      },
    ],
    choices: [
      { label: "Approve", say: "@studio-director approve", next: "closed" },
      {
        label: "Shorten the hook",
        say: "@studio-director shorten the hook",
        next: "change",
      },
    ],
  },
  change: {
    lines: [
      { who: "director", text: "Your change is with @studio-quill." },
      {
        who: "quill",
        text: "Hook shortened.\nready for @studio-keeper brand check",
      },
      {
        who: "keeper",
        text: "Verdict: PASS\nNext: @studio-director approved render",
      },
      {
        who: "director",
        text: "@you renders/driftnote-plus/driftnote-plus.mp4\nreply @studio-director approve or your change",
      },
    ],
    choices: [
      { label: "Approve", say: "@studio-director approve", next: "closed" },
    ],
  },
  closed: {
    lines: [
      {
        who: "director",
        text: "Creator approved. Closed. Nothing published.",
        status: "script ✓ · brand ✓ · voice ✓ · render ✓ · approved by you",
      },
    ],
  },
}

function RepoButton() {
  return (
    <Button
      asChild
      size="lg"
      className="group h-11 pr-3.5 pl-4 transition-[background-color,transform] duration-150 ease-out active:scale-[0.96]"
    >
      <a href={REPO}>
        Get it on GitHub
        <ArrowUpRight
          data-icon="inline-end"
          className="transition-transform duration-150 ease-out group-hover:translate-x-0.5 group-hover:-translate-y-0.5 motion-reduce:transition-none"
        />
      </a>
    </Button>
  )
}

function ThemeToggle() {
  const [dark, setDark] = useState(() =>
    document.documentElement.classList.contains("dark")
  )

  function toggle() {
    const next = !dark
    const root = document.documentElement
    root.classList.add("theme-switching")
    root.classList.toggle("dark", next)
    setDark(next)
    requestAnimationFrame(() =>
      requestAnimationFrame(() => root.classList.remove("theme-switching"))
    )
    try {
      localStorage.setItem("theme", next ? "dark" : "light")
    } catch {
      // Blocked storage only loses the remembered choice.
    }
  }

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={toggle}
      aria-label={dark ? "Switch to light mode" : "Switch to dark mode"}
      className="size-10 transition-[background-color,transform] duration-150 ease-out active:scale-[0.96] sm:order-2"
    >
      <span key={String(dark)} className="tick grid place-items-center">
        {dark ? <Sun /> : <Moon />}
      </span>
    </Button>
  )
}

function Status({ active }: { active: string }) {
  const current = SECTIONS.indexOf(active)

  return (
    <nav aria-label="Sections" className="flex font-mono text-[13px] max-sm:-ml-1 max-sm:basis-full sm:order-1">
      {SECTIONS.map((section, index) => (
        <span key={section} className="flex items-center">
          {index > 0 && (
            <span aria-hidden className="w-2 text-center text-muted-foreground sm:w-3">
              ·
            </span>
          )}
          <a
            href={`#${section}`}
            aria-current={index === current ? "true" : undefined}
            className={cn(
              "flex h-10 items-center pl-1 transition-colors duration-150 ease-out hover:text-foreground",
              index > current ? "text-muted-foreground" : "text-foreground"
            )}
          >
            {section}
            <span
              key={index < current ? "done" : index === current ? "now" : "next"}
              aria-hidden
              className="tick ml-1 inline-block w-[1ch] tabular-nums"
            >
              {index < current ? "✓" : index === current ? "…" : ""}
            </span>
          </a>
        </span>
      ))}
    </nav>
  )
}

function Bot({ id, alt = "", className }: { id: string; alt?: string; className?: string }) {
  const [playing, setPlaying] = useState(false)

  return (
    <img
      src={`agents/${id}.png`}
      width={32}
      height={32}
      alt={alt}
      onClick={() => setPlaying(true)}
      onAnimationEnd={() => setPlaying(false)}
      className={cn("bot cursor-pointer rounded-full", playing && `bot-${id}`, className)}
    />
  )
}

function RoomLine({ who, text }: Line) {
  return (
    <Message className="gap-3">
      {who === "you" || who === "user" ? (
        <MessageAvatar className="size-8 self-start bg-secondary text-xs font-medium">
          U
        </MessageAvatar>
      ) : (
        <MessageAvatar className="size-8 self-start overflow-visible bg-transparent">
          <Bot id={who} />
        </MessageAvatar>
      )}
      <MessageContent className="gap-1">
        <MessageHeader className="gap-2 px-0">
          <span className="text-foreground capitalize">{who}</span>
        </MessageHeader>
        <Bubble variant="ghost">
          <BubbleContent className="whitespace-pre-line text-muted-foreground">
            {text}
          </BubbleContent>
        </Bubble>
      </MessageContent>
    </Message>
  )
}

function Rich({ text }: { text: string }) {
  return text.split(/(@\w+|\[need:[^\]]*\])/).map((part, index) =>
    part.startsWith("@") ? (
      <span key={index} className="font-medium text-foreground">
        {part}
      </span>
    ) : part.startsWith("[need:") ? (
      <span key={index} className="rounded-sm bg-muted px-1 font-mono text-[0.9em] text-foreground">
        {part}
      </span>
    ) : (
      part
    )
  )
}

function RoomPost({ post, dim }: { post: Post; dim: boolean }) {
  const user = post.who === "user"
  return (
    <article
      data-post={post.id}
      className={cn(
        "fade-up flex gap-3 px-4 py-3 transition-opacity duration-200 ease-out sm:px-5",
        dim && "opacity-25"
      )}
      style={{ animationDuration: "300ms" }}
    >
      {user ? (
        <span className="grid size-9 shrink-0 place-items-center rounded-full bg-secondary text-xs font-medium">
          U
        </span>
      ) : (
        <Bot id={post.who} className="size-9 shrink-0" />
      )}
      <div className="flex min-w-0 flex-1 flex-col gap-1">
        <p className="flex items-baseline gap-2 text-sm">
          <span className="font-semibold capitalize">{user ? "You" : post.who}</span>
          {!user && (
            <span className="rounded-sm border px-1 font-mono text-[10px] leading-4 text-muted-foreground">
              BOT
            </span>
          )}
          <span className="text-xs text-muted-foreground tabular-nums">{post.at}</span>
        </p>
        <p className="text-sm leading-relaxed whitespace-pre-line text-muted-foreground [overflow-wrap:anywhere]">
          <Rich text={post.text} />
        </p>
        {post.fixes && (
          <div className="my-1 flex flex-col rounded-md border">
            {post.fixes.map((item, index) => (
              <details key={item.at} open={index === 0} className="group border-b last:border-b-0">
                <summary className="flex min-h-10 cursor-pointer list-none items-center gap-2 px-3 py-2 text-sm [&::-webkit-details-marker]:hidden">
                  <ChevronRight
                    aria-hidden
                    className="size-4 shrink-0 text-muted-foreground transition-transform duration-150 ease-out group-open:rotate-90 motion-reduce:transition-none"
                  />
                  <span className="shrink-0 font-mono text-xs">{item.at}</span>
                  <span className="truncate text-muted-foreground group-open:hidden">
                    {item.issue}
                  </span>
                </summary>
                <div className="flex flex-col gap-2 px-3 pb-3 pl-9 text-sm leading-relaxed text-muted-foreground">
                  <p>{item.issue}</p>
                  <p>
                    <span className="font-medium text-foreground">Fix: </span>
                    {item.fix}
                  </p>
                </div>
              </details>
            ))}
          </div>
        )}
        {post.after && (
          <p className="text-sm leading-relaxed whitespace-pre-line text-muted-foreground">
            <Rich text={post.after} />
          </p>
        )}
      </div>
    </article>
  )
}

function RealRoom() {
  const [active, setActive] = useState(POSTS[0].id)
  const [agent, setAgent] = useState<string | null>(null)
  const [shown, setShown] = useState(POSTS.length)
  const [replaying, setReplaying] = useState(false)
  const [view, setView] = useState("room")
  const scroller = useRef<HTMLDivElement>(null)
  const current = POSTS.find((post) => post.id === active) ?? POSTS[0]
  const shot = SHOTS[current.shot]

  useEffect(() => {
    if (!replaying) return
    const box = scroller.current
    box?.scrollTo({ top: box.scrollHeight, behavior: "smooth" })
    setActive(POSTS[shown - 1].id)
    if (shown === POSTS.length) {
      setReplaying(false)
      return
    }
    const timer = setTimeout(() => setShown(shown + 1), 1100)
    return () => clearTimeout(timer)
  }, [replaying, shown])

  function jump(id: string) {
    setReplaying(false)
    setShown(POSTS.length)
    setActive(id)
    requestAnimationFrame(() => {
      const box = scroller.current
      const post = box?.querySelector<HTMLElement>(`[data-post="${id}"]`)
      if (box && post) box.scrollTo({ top: post.offsetTop, behavior: "smooth" })
    })
  }

  function spy() {
    const box = scroller.current
    if (!box || replaying) return
    if (box.scrollTop + box.clientHeight >= box.scrollHeight - 4) {
      setActive(POSTS[POSTS.length - 1].id)
      return
    }
    const posts = box.querySelectorAll<HTMLElement>("[data-post]")
    for (const post of posts) {
      if (post.offsetTop <= box.scrollTop + 48) setActive(post.dataset.post ?? active)
    }
  }

  return (
    <Tabs value={view} onValueChange={setView} className="reveal gap-0 overflow-hidden rounded-lg border bg-card">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b px-4 py-3 sm:px-5">
        <p className="text-sm font-semibold">One-Person Studio launch</p>
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-1" aria-label="Show one agent">
            {TEAM.filter((member) => member.id !== "voice").map((member) => (
              <button
                key={member.id}
                type="button"
                aria-pressed={agent === member.id}
                aria-label={`Only ${member.name}`}
                onClick={() => setAgent(agent === member.id ? null : member.id)}
                className={cn(
                  "grid size-10 place-items-center rounded-full transition-[opacity,background-color,transform] duration-150 ease-out active:scale-[0.96]",
                  agent === member.id && "bg-secondary",
                  agent && agent !== member.id && "opacity-40"
                )}
              >
                <img src={`agents/${member.id}.png`} alt="" width={24} height={24} className="size-6 rounded-full" />
              </button>
            ))}
          </div>
          <Button
            variant="outline"
            size="sm"
            className="h-9 transition-[background-color,transform] duration-150 ease-out active:scale-[0.96] motion-reduce:hidden"
            onClick={() => {
              setView("room")
              setAgent(null)
              setShown(1)
              setReplaying(true)
            }}
          >
            <RotateCcw data-icon="inline-start" />
            Replay
          </Button>
          <TabsList className="group-data-horizontal/tabs:h-9">
            <TabsTrigger value="room" className="px-3">Room</TabsTrigger>
            <TabsTrigger value="shot" className="px-3">Screenshot</TabsTrigger>
          </TabsList>
        </div>
      </div>

      <div className="grid min-w-0 lg:grid-cols-[12rem_minmax(0,1fr)]">
        <nav aria-label="Steps of the run" className="flex gap-1 overflow-x-auto border-b p-2 lg:flex-col lg:border-r lg:border-b-0">
          {POSTS.map((post) => (
            <button
              key={post.id}
              type="button"
              aria-current={post.id === active ? "step" : undefined}
              onClick={() => jump(post.id)}
              className={cn(
                "flex min-h-10 shrink-0 items-center justify-between gap-3 rounded-md px-3 text-left text-sm transition-colors duration-150 ease-out",
                post.id === active
                  ? "bg-secondary text-foreground"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              {post.label}
              <span className="text-xs text-muted-foreground tabular-nums max-lg:hidden">
                {post.at.replace(" PM", "")}
              </span>
            </button>
          ))}
        </nav>

        <TabsContent value="room" forceMount className="min-w-0 data-[state=inactive]:hidden">
          <div ref={scroller} onScroll={spy} className="relative h-[34rem] overflow-y-auto py-2 [overflow-anchor:none] max-sm:h-[28rem]">
            {POSTS.slice(0, shown).map((post) => (
              <RoomPost
                key={post.id}
                post={post}
                dim={agent !== null && post.who !== agent}
              />
            ))}
          </div>
          <p className="min-h-11 border-t px-4 py-3 text-sm text-muted-foreground sm:px-5">
            {replaying ? "Agents are handing off…" : "The chain stops here until you reply."}
          </p>
        </TabsContent>

        <TabsContent value="shot" className="flex min-w-0 flex-col gap-3 p-4">
          <p className="text-sm text-muted-foreground">{shot.note}</p>
          <img
            key={shot.id}
            src={shot.src}
            alt={shot.alt}
            width={1920}
            height={1080}
            className="aspect-video w-full rounded-md border object-cover object-top duration-200 animate-in fade-in motion-reduce:animate-none"
          />
        </TabsContent>
      </div>
    </Tabs>
  )
}

function Relay() {
  const [index, setIndex] = useState(0)
  const [typed, setTyped] = useState(0)
  const last = RELAY.length - 1

  useEffect(() => {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setIndex(last)
      setTyped(ASK.length)
      return
    }
    const typing = index === 0 && typed < ASK.length
    const timer = setTimeout(
      () => {
        if (typing) {
          setTyped(typed + 1)
        } else if (index === last) {
          setIndex(0)
          setTyped(0)
        } else {
          setIndex(index + 1)
        }
      },
      typing ? 26 : index === last ? 3600 : 1500
    )
    return () => clearTimeout(timer)
  }, [index, typed, last])

  const step = RELAY[index]
  const at = NODES.indexOf(step.who)

  return (
    <div className="fade-up flex flex-col gap-6 overflow-hidden rounded-lg border bg-card p-4 sm:p-6" style={{ animationDelay: "320ms" }}>
      <p className="grid font-mono text-[13px] leading-relaxed">
        <span aria-hidden className="invisible col-start-1 row-start-1">{ASK}</span>
        <span className="col-start-1 row-start-1">{ASK.slice(0, typed)}</span>
      </p>

      <div className="relative flex justify-between">
        <span aria-hidden className="absolute inset-x-4 top-4 h-px bg-border" />
        <span
          aria-hidden
          className="absolute inset-x-4 top-4 transition-transform duration-[600ms] ease-in-out motion-reduce:transition-none"
          style={{ transform: `translateX(${(at / (NODES.length - 1)) * 100}%)` }}
        >
          <span className="absolute -top-1 -left-1 size-2 rounded-full bg-foreground" />
        </span>
        {NODES.map((who, node) => {
          const on = node === at
          return (
            <div key={who} className="relative flex flex-col items-center gap-2">
              {who === "you" ? (
                <span
                  className={cn(
                    "grid size-8 place-items-center rounded-full bg-secondary text-xs font-medium transition-opacity duration-300 ease-out",
                    on ? "opacity-100" : "opacity-50"
                  )}
                >
                  U
                </span>
              ) : (
                <Bot id={who} className={cn(on ? "opacity-100" : "opacity-50", on && `bot-${who}`)} />
              )}
              <span
                className={cn(
                  "text-xs capitalize transition-colors duration-300 ease-out max-sm:hidden",
                  on ? "text-foreground" : "text-muted-foreground"
                )}
              >
                {who}
              </span>
            </div>
          )
        })}
      </div>

      <p key={index} className="fade-up min-h-10 font-mono text-[13px] [overflow-wrap:anywhere] sm:min-h-5" style={{ animationDuration: "240ms" }}>
        <span className="text-muted-foreground capitalize">{step.who}: </span>
        {step.text}
      </p>

      <p className="text-sm text-muted-foreground">
        A sketch of the handoff, not a transcript. Real screens are further down.
      </p>
    </div>
  )
}

function Sim() {
  const [log, setLog] = useState<Line[]>([])
  const [stageId, setStageId] = useState("ask")
  const [played, setPlayed] = useState(0)
  const scroller = useRef<HTMLDivElement>(null)

  const stage = STAGES[stageId]
  const next = stage.lines[played]
  const status = log.filter((line) => line.status).at(-1)?.status

  useEffect(() => {
    if (!next) return
    const calm = matchMedia("(prefers-reduced-motion: reduce)").matches
    const timer = setTimeout(
      () => {
        setLog((lines) => [...lines, next])
        setPlayed((count) => count + 1)
      },
      calm ? 0 : 1300
    )
    return () => clearTimeout(timer)
  }, [next])

  useEffect(() => {
    scroller.current?.scrollTo({ top: scroller.current.scrollHeight })
  }, [log])

  function choose(say: string, target: string) {
    setLog((lines) => [...lines, { who: "you", text: say }])
    setStageId(target)
    setPlayed(0)
  }

  function restart() {
    setLog([])
    setStageId("ask")
    setPlayed(0)
  }

  return (
    <div className="flex min-w-0 flex-col overflow-hidden rounded-lg border bg-card">
      <div className="flex flex-col gap-3 border-b p-4">
        <div className="flex gap-2">
          {TEAM.map((agent) => (
            <Bot
              key={agent.id}
              id={agent.id}
              alt={agent.name}
              className={cn(
                next?.who === agent.id ? "opacity-100" : "opacity-35",
                next?.who === agent.id && `bot-${agent.id}`
              )}
            />
          ))}
        </div>
        <p className="min-h-10 font-mono text-[13px] text-muted-foreground sm:min-h-5">
          {status ?? "Waiting for one line."}
        </p>
      </div>

      <div
        ref={scroller}
        role="log"
        aria-label="Simulated room"
        className="h-[26rem] overflow-y-auto scroll-smooth p-4 motion-reduce:scroll-auto"
      >
        <MessageGroup className="gap-5">
          {log.map((line, index) => (
            <div
              key={index}
              className="duration-300 animate-in fade-in motion-reduce:animate-none"
            >
              <RoomLine {...line} />
            </div>
          ))}
        </MessageGroup>
      </div>

      <div className="flex min-h-20 flex-wrap items-center gap-2 border-t p-4">
        {stageId === "ask" && (
          <p className="w-full pb-2 font-mono text-[13px]">
            {stage.choices?.[0].say}
          </p>
        )}
        {next && (
          <p className="text-sm text-muted-foreground">
            <span className="capitalize">{next.who}</span> is working
            <span className="animate-pulse motion-reduce:animate-none">…</span>
          </p>
        )}
        {!next &&
          stage.choices?.map((choice, index) => (
            <Button
              key={choice.label}
              variant={index === 0 ? "default" : "outline"}
              style={{ animationDelay: `${index * 60}ms` }}
              onClick={() => choose(choice.say, choice.next)}
              className="fade-up h-10 transition-[background-color,transform] duration-150 ease-out active:scale-[0.96]"
            >
              {choice.label}
            </Button>
          ))}
        {!next && !stage.choices && (
          <Button
            variant="outline"
            onClick={restart}
            className="h-10 transition-[background-color,transform] duration-150 ease-out active:scale-[0.96]"
          >
            Run it again
          </Button>
        )}
      </div>
    </div>
  )
}

function CopyClone() {
  const [copied, setCopied] = useState(false)

  async function copy() {
    await navigator.clipboard.writeText(CLONE)
    setCopied(true)
    setTimeout(() => setCopied(false), 1600)
  }

  return (
    <div className="flex items-center gap-3 rounded-lg border bg-card py-1.5 pr-1.5 pl-4">
      <code className="min-w-0 flex-1 truncate font-mono text-[13px]">{CLONE}</code>
      <Button
        variant="ghost"
        onClick={copy}
        aria-live="polite"
        className="h-10 w-20 transition-[background-color,transform] duration-150 ease-out active:scale-[0.96]"
      >
        <span key={String(copied)} className="tick">
          {copied ? "Copied" : "Copy"}
        </span>
      </Button>
    </div>
  )
}

export default function App() {
  const [active, setActive] = useState(SECTIONS[0])

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const hit = entries.find((entry) => entry.isIntersecting)
        if (hit) setActive(hit.target.id)
      },
      { rootMargin: "-30% 0px -65% 0px" }
    )
    SECTIONS.forEach((id) => observer.observe(document.getElementById(id)!))
    return () => observer.disconnect()
  }, [])

  return (
    <div className="min-h-svh">
      <header className="sticky top-0 z-10 border-b bg-background">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-x-6 px-4 pt-2 sm:h-16 sm:flex-nowrap sm:px-8 sm:pt-0">
          <a href="#run" className="mr-auto flex h-10 items-center font-heading font-bold tracking-tight">
            One-Person Studio
          </a>
          <ThemeToggle />
          <Status active={active} />
        </div>
        <span
          aria-hidden
          className="page-progress absolute inset-x-0 -bottom-px h-px origin-left bg-foreground"
        />
      </header>

      <main className="mx-auto max-w-6xl px-4 sm:px-8">
        <section id="run" className="flex flex-col gap-10 py-12 sm:gap-14 sm:py-20">
          <h1 className="text-[clamp(2.75rem,11.5vw,8.5rem)] whitespace-nowrap">
            <span className="-mb-[0.14em] block overflow-hidden pb-[0.14em]">
              <span className="hero-line block">Send one line.</span>
            </span>
            <span className="-mb-[0.14em] block overflow-hidden pb-[0.14em]">
              <span className="hero-line block" style={{ animationDelay: "90ms" }}>
                Get a video.
              </span>
            </span>
          </h1>
          <div className="fade-up flex flex-col items-start gap-6 lg:flex-row lg:items-end lg:justify-between" style={{ animationDelay: "220ms" }}>
            <p className="max-w-xl text-lg leading-relaxed text-muted-foreground">
              A video team for solo creators that lives in your chat. Five
              agents write it, voice it, render it and check it. You approve
              the final cut.
            </p>
            <RepoButton />
          </div>
          <Relay />
        </section>

        <section
          id="try"
          className="grid gap-10 border-t py-16 sm:py-24 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.05fr)] lg:gap-20"
        >
          <div className="flex flex-col gap-6">
            <h2 className="reveal text-4xl sm:text-5xl">Now you be the creator.</h2>
            <p className="max-w-md leading-relaxed text-muted-foreground">
              Send the line and watch the handoffs. The chain stops twice, once
              for a fact only you have and once for the final cut.
            </p>
            <p className="max-w-md text-sm leading-relaxed text-muted-foreground">
              This is a simulation with fixed replies. No agents are running,
              and Driftnote is a fictional demo brand.
            </p>
          </div>
          <div className="reveal min-w-0">
            <Sim />
          </div>
        </section>

        <section id="team" className="flex flex-col gap-10 border-t py-16 sm:py-24">
          <h2 className="reveal max-w-2xl text-4xl sm:text-5xl">
            You talk to Director. Director talks to the rest.
          </h2>
          <Table>
            <TableHeader className="max-sm:sr-only">
              <TableRow className="hover:bg-transparent">
                <TableHead className="w-44">Agent</TableHead>
                <TableHead>Job</TableHead>
                <TableHead>In the room</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {TEAM.map((agent) => (
                <TableRow key={agent.id} className="reveal hover:bg-transparent">
                  <TableCell className="py-4 whitespace-normal">
                    <div className="flex items-center gap-3 font-medium">
                      <Bot id={agent.id} />
                      {agent.name}
                    </div>
                    <p className="mt-2 text-muted-foreground sm:hidden">{agent.job}</p>
                    <p className="mt-1 font-mono text-[13px] sm:hidden">{agent.says}</p>
                  </TableCell>
                  <TableCell className="py-4 whitespace-normal text-muted-foreground max-sm:hidden">
                    {agent.job}
                  </TableCell>
                  <TableCell className="py-4 font-mono text-[13px] max-sm:hidden">
                    {agent.says}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <p className="max-w-xl leading-relaxed text-muted-foreground">
            Every handoff is a plain @mention in one Switch room. No orchestrator
            and no queue behind it, so you can read the whole job in chat.
          </p>
        </section>

        <section id="facts" className="grid gap-16 border-t py-16 sm:py-24 lg:grid-cols-2 lg:gap-20">
          <div className="flex flex-col gap-6">
            <h2 className="reveal text-4xl sm:text-5xl">The team does not guess.</h2>
            <p className="max-w-md leading-relaxed text-muted-foreground">
              Ask for a number that does not exist, and you get a blank, not a
              number. On our Driftnote demo brand, the chain stopped before the
              render:
            </p>
            <blockquote className="reveal flex max-w-lg flex-col gap-3 border-l pl-4 font-mono text-[13px] leading-relaxed">
              <p>script passed brand check. Before we render, it still needs your input:</p>
              <p>
                - Price of Driftnote Plus: should it appear on screen, and if so
                what is it?
              </p>
              <p>reply @studio-director with the answer</p>
            </blockquote>
            <p className="reveal font-mono text-lg text-primary">[need: price]</p>
          </div>

          <div className="flex flex-col gap-6">
            <h2 className="reveal text-4xl sm:text-5xl">Nothing ships without you.</h2>
            <dl className="flex flex-col">
              {YOURS.map(([term, detail]) => (
                <div key={term} className="reveal grid gap-1 border-b py-4 last:border-0 sm:grid-cols-[9rem_1fr] sm:gap-4">
                  <dt className="font-medium">{term}</dt>
                  <dd className="text-muted-foreground">{detail}</dd>
                </div>
              ))}
            </dl>
          </div>
        </section>

        <section id="proof" className="flex flex-col gap-10 border-t py-16 sm:py-24">
          <h2 className="reveal text-4xl sm:text-5xl">The room, not a mock-up.</h2>
          <p className="reveal max-w-xl leading-relaxed text-muted-foreground">
            Copied from one real run on Switch and trimmed. Pick a step, show
            one agent, open Keeper's fixes, or replay it. Screenshot shows the
            original.
          </p>
          <RealRoom />
        </section>

        <section id="setup" className="grid gap-12 border-t py-16 sm:py-24 lg:grid-cols-2 lg:gap-20">
          <div className="flex flex-col gap-6">
            <h2 className="reveal text-4xl sm:text-5xl">Set it up on Switch.</h2>
            <p className="max-w-md leading-relaxed text-muted-foreground">
              You need Switch Console and Claude Code, signed in. Cut also needs
              Node.js 22+.
            </p>
            <a
              href={`${REPO}/blob/main/SETUP.md`}
              className="flex h-10 w-fit items-center underline underline-offset-4"
            >
              Full steps in SETUP.md
            </a>
          </div>

          <div className="flex min-w-0 flex-col gap-6">
            <div className="reveal">
              <CopyClone />
            </div>
            <ol className="flex flex-col gap-3">
              {STEPS.map((step, index) => (
                <li key={step} className="reveal grid grid-cols-[1.5rem_1fr] gap-2 leading-relaxed">
                  <span className="font-mono text-muted-foreground tabular-nums">
                    {index + 1}
                  </span>
                  <span>{step}</span>
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section className="flex flex-col items-start gap-8 border-t py-16 sm:py-24">
          <h2 className="text-[clamp(2.5rem,6vw,4.5rem)]">
            Send one line.
            <br />
            Get a video.
          </h2>
          <RepoButton />
        </section>
      </main>

      <footer className="border-t pb-[env(safe-area-inset-bottom)]">
        <div className="mx-auto flex max-w-6xl flex-wrap justify-between gap-x-6 gap-y-1 px-4 py-6 text-sm text-muted-foreground sm:px-8">
          <span>Built on Switch for WeMakeDevs Flip the Switch.</span>
          <span>MIT license</span>
        </div>
      </footer>
    </div>
  )
}
