---
name: trend-picker
description: |
  Social-media research, ad intelligence, and trend discovery across Instagram, TikTok, YouTube, Shorts, ad libraries, and the open web. Research-only. For TikTok-only content ideas or generation for a product, service, niche, or brand, use tiktok-organic-marketing instead.
---
# Trend Picker

Unified social media research, ad intelligence, and trend discovery. Fetches data from all platforms, ranks by engagement, analyzes with AI, generates content concepts.

## Intents and Modes (quick routing)

| Intent          | Mode | Trigger                                                           | Output                                         |
| --------------- | ---- | ----------------------------------------------------------------- | ---------------------------------------------- |
| trend_discovery | A    | pure research or cross-platform trend work                         | top videos + 3 concepts + optional HANDOFF v2  |
| viral_analysis  | D    | "why is this viral?" + a single source video URL                  | strategy analysis (CONCEPT/HOOK/RETENTION/...) |
| creator_dna     | C    | persona-clone trigger detected (`mode=creator_dna` passed in)     | aggregate creator DNA report URL + reel URLs   |
| adaptation      | —    | source URL + recreate / reproduce / "сделай как это" / mode=adapt | refuse here; redirect to the video-adapt skill |
| tiktok-content    | —  | TikTok-only ideas/generation for a product, service, niche, or brand | load `tiktok-organic-marketing`              |

Modes A, C, D run inside this skill. Adaptation belongs to `video-adapt`.
TikTok-only content ideas or generation belong to
`tiktok-organic-marketing`; do not start a second intake or a Mode A/HANDOFF
pipeline here.

### TikTok generation boundary

Apply adaptation, creator-DNA, and explicit single-source viral-analysis gates
first. Otherwise, any TikTok-only request that combines research/trend intent
with content ideas or a countable generation output for a product, service,
niche, or brand must immediately load `tiktok-organic-marketing`. Example:
"find TikTok fitness trends and make three videos" belongs to that skill, not
Mode A.

Pure research/reports and cross-platform trend work stay here. Do not enter the
manual concepts/generation/HANDOFF pipeline for TikTok-only content.

## Compact organic discovery

When `tiktok-organic-marketing` is loaded, that skill is the sole authority for
query limits, research windows, analysis queues, fallback, ideas, and
generation handoff. Do not duplicate its policy here. Do not delegate that
embedded flow or run generic `tiktok_research` discovery, social, web, chart,
YouTube, or Pinterest tools to repair its sample.

## Activation Gate — Persona-Clone vs Standard Research

When the request triggers this skill, evaluate these four conditions before picking a mode. Activate persona-clone flow when **ALL FOUR** hold:

(a) request references an **existing creator** (`@username` or platform profile URL — not a single video URL),
(b) intent is to create a **NEW persona/influencer** (not a literal copy of the creator),
(c) phrasing implies **audience parity** ("hit the same audience", "like @X but not a copy", "such as @X", "under the same audience as @X"),
(d) output is **multi-post / multi-reel / content plan** (not a one-shot single deliverable).

If all four hold → ask the user via `ask_question`:

- **Deep** — creator-DNA pipeline (~5-10 min, higher cost): proceed to **Mode C** below, then follow `skills/research/trend-picker/references/persona-clone.md` for post-detection orchestration (base portrait → Branch V/I fan-out → soul-id training, etc).
- **Quick** — metadata-only research (fast, cheap): proceed to **Mode A** (`trend_discovery`). No DNA extraction.

If any of (a)-(d) fails → not persona-clone → apply the TikTok generation
boundary next. If it does not route away, use **Mode A** by default, or **Mode
D** if the user explicitly asked "why is this viral?" with a single source
video URL.

Boundary examples (regression cases):

| User brief                                                             | Persona-clone? | Why                                                                                                                 |
| ---------------------------------------------------------------------- | -------------- | ------------------------------------------------------------------------------------------------------------------- |
| "make an avatar like @charlidamelio for our brand, need a single post" | NO             | (d) fails — single post, not multi-post                                                                             |
| "@charlidamelio is our reference, recreate this exact reel: <url>"     | NO             | (a) refers to a SINGLE video URL with explicit recreate intent → this is `adaptation`, route to `video-adapt` skill |
| "make 5 reels in @charlidamelio's style, hit her TikTok audience"      | YES            | All 4 conditions hold                                                                                               |
| "make 3 reels of the same quality as @creator"                         | NO             | (c) fails — "quality match" is not audience parity                                                                  |
| "find viral trends in beauty"                                          | NO             | (a) fails — no specific creator reference                                                                           |

When in doubt after applying the TikTok generation boundary — fall to `trend_discovery` (safe default). Mode C runs an expensive Gemini DNA pipeline; misclassification costs ~5-10 minutes of compute. Better to under-trigger and let the user re-prompt with stronger audience-parity wording.

## Research Report Delegation — `agent`

When the user asks for a **written research report** (competitor analysis, trend report, market overview, cited deliverable), prefer delegating to the `agent` tool over manually running the full pipeline. It runs a fresh copy of this agent with the same tools and sandbox, so tell it in `message` to use `web_search` / `web_extract` and to produce a markdown report with inline citations and a Sources section. The child sees none of this conversation — put everything it needs in `message`. To run several research tasks at once, emit multiple `agent` calls in a single response and give each a non-overlapping output file.

Exception: `tiktok-organic-marketing` owns its bounded discovery directly; do
not delegate that embedded step.

**Delegate to `agent` when:**

- The deliverable is a report file (e.g. "write me a report on fitness trends", "analyze competitor X and give me a document")
- The user wants a cited, structured analysis they can share or reference later
- The research scope is broad (multiple platforms, multiple angles, needs synthesis)

**Use the manual pipeline (Steps 0-4 below) when:**

- Cross-platform research feeds into content generation downstream (Mode A with Hook Extraction → HANDOFF)
- The user wants in-conversation analysis, not a file (quick lookups, one-off queries)
- The workflow requires OpenRouter video analysis (`video_analyze`) or ad library research (`ads`)
- Mode C (creator DNA) or Mode D (viral analysis) is triggered — these need specialized tool chains you should drive yourself

TikTok-only generation never uses this manual pipeline; load
`tiktok-organic-marketing` instead.

Example:

```
agent(
  message="Research TikTok fitness trends for Q1 2025 and write a cited markdown report to ./research/tiktok-fitness-q1.md. Focus on the home workout niche, US audience. Answer: who are the top fitness creators, what content formats perform best, and which hashtags are trending? Use web_search and web_extract. Include inline citations and a Sources section."
)
```

## Tools

All tools below are native tools — call them directly. No CLI binaries or shell.

| Tool                       | Platform                                                            |
| -------------------------- | ------------------------------------------------------------------- |
| **instagram_research**     | Instagram                                                           |
| **tiktok_research**        | TikTok                                                              |
| **trending_shorts_search** | Trending Shorts by keyword/search term (FNF trending corpus)        |
| **youtube**                | YouTube (search, video, transcript, comments, channel, research)    |
| **trends**                 | YouTube Shorts trending pipeline (FNF data ingestion API)           |
| **ads**                    | Meta, TikTok, LinkedIn, Reddit ad libraries                         |
| **web_search**             | Google-style web search (URL discovery)                             |
| **web_extract**            | Fetch & extract URL content as markdown / structured JSON           |
| **video_analyze**          | OpenRouter video analysis (storyboard, viral analysis, creator DNA) |

---

## Instagram (instagram_research tool)

API: EnsembleData via native `instagram_research` tool. All user commands accept `username` directly — the tool resolves username→ID automatically. Pass `user_id` only if you already have the numeric pk.

### User Research

```
instagram_research(action="user_research", username="alexmitch6")                          # bundled profile + 20 most recent posts in ONE call (preferred for "research this user")
instagram_research(action="user_details", username="alexmitch6")                           # canonical profile only (bio, links, follower/following count, business info, verification)
instagram_research(action="user_posts", username="alexmitch6", depth=2)                    # recent posts (depth 1 = ~10 posts)
instagram_research(action="user_reels", username="alexmitch6", depth=3, sort="views")      # reels sorted by play_count
instagram_research(action="user_tagged", username="alexmitch6")                            # posts where user is tagged
instagram_research(action="user_followers", username="alexmitch6")                         # follower count
```

For "analyze @handle" / "research this profile" intents, prefer **`user_research`** — it bundles `user_details` + ~20 recent posts into one envelope, two upstream requests in parallel. Saves a tool call AND a context round-trip. For deeper crawling (>20 posts, paginated), call `user_posts` directly with higher `depth`. Use `user_details` standalone only when you genuinely don't need posts.

Pass `username=` to any of the user** / media** actions — the tool resolves to the numeric pk internally; you never need to look it up yourself.

**Reels are always flat.** `user_reels` returns `{"items": [{code, play_count, like_count, comment_count, caption, taken_at, ...}], "count": N}`. Use `sort="views"` to rank by play_count descending, `sort="likes"` for like_count, `sort="date"` for taken_at. Responses are automatically slimmed to agent-useful fields.

### Content Discovery

```
instagram_research(action="search", query="keyword")                # search users + hashtags
instagram_research(action="music_posts", id="<music_id>")           # posts using a specific audio
```

### Post Analysis

```
instagram_research(action="media_info", code="<shortcode>")                    # post details by shortcode
instagram_research(action="media_info", code="<shortcode>", comments=50)       # include up to 50 comments
instagram_research(action="media_comments", code="<shortcode>")                # paginated comments (auto-resolves code→media_id)
instagram_research(action="media_comments", media_id="<numeric_id>")           # paginated comments by media ID
```

### Response Envelope

Every action returns the same envelope shape — a discriminated union over `kind`:

```json
{
  "kind": "user_posts",
  "query": { /* echo of action + caller args */ },
  "data": { /* per-kind payload — see table below */ },
  "pagination": { "next_cursor": "..." } | null,
  "meta": { "source": "ensembledata", "engine": "instagram", "fetched_at": "ISO-8601" },
  "error": null
}
```

On upstream / argument errors, `data` is `null` and `error` carries `{ code, message, status }` — clients still parse the same top-level dict. Bare `tool_error` (un-enveloped) is reserved for unexpected exceptions only.

### Per-kind `data` shapes

| `kind`                                                      | `data`                                                                                                       |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `user_details`                                              | `UserProfile` (canonical slimmed profile — see below)                                                        |
| `user_research`                                             | `{ profile: UserProfile, posts: [MediaItem, …] }` (≤20 posts — for deeper crawls call `user_posts` directly) |
| `user_posts` / `user_reels` / `user_tagged` / `music_posts` | `{ items: [MediaItem, …] }`                                                                                  |
| `user_followers`                                            | `{ count: <int> }`                                                                                           |
| `media_info`                                                | `{ media: MediaItem, comments?: [Comment, …] }`                                                              |
| `media_comments`                                            | `{ comments: [Comment, …] }`                                                                                 |
| `search`                                                    | `{ users: [SearchUser, …], hashtags: [{name, media_count}, …] }`                                             |

**`pagination`** is populated for `user_posts` / `user_reels` / `user_tagged` / `music_posts` / `media_comments` when more pages exist; `null` otherwise. For `user_research`, `pagination.next_cursor` (when present) refers to the **posts** feed only — paginate via `user_posts` directly for deeper crawls. Pass the returned `next_cursor` back in as the `cursor` arg to fetch the next page.

### `UserProfile` (data of `user_details`)

```json
{
  "id": "6187738006",
  "username": "culturfits",
  "full_name": "CulturFits",
  "biography": "...",
  "external_url": "http://culturfits.com/",
  "bio_links": [{ "title": "...", "url": "..." }],
  "follower_count": 760374,
  "following_count": 4,
  "media_count": 5515,
  "highlight_reel_count": 6,
  "category_name": "Community",
  "profile_pic_url": "https://...",
  // boolean flags below appear ONLY when true (omit-when-false):
  "is_verified": true,
  "is_private": true,
  "is_business_account": true,
  "is_professional_account": true,
  "has_clips": true,
  // business contact fields appear ONLY when present:
  "business_email": "...",
  "business_phone_number": "...",
  "business_address_json": "..."
}
```

### `MediaItem` (data of every list-bearing action)

```json
{
  "shortcode": "DLm7DrMNVmG",
  "display_url": "https://...cover.jpg",
  "is_video": true,
  "like_count": 7565, "comment_count": 48,
  "caption": "...", "taken_at": 1751299200,
  "video_url": "https://...mp4",          // video posts only
  "video_duration": 8.5, "has_audio": true, "play_count": 6994252,
  "carousel_media_count": 6,               // carousel posts only
  "carousel": [{"display_url": "...", "is_video": false}, ...],
  "location": {"id": "...", "name": "Tokyo Tower", "city": "Tokyo"}  // tagged-location posts only
}
```

- ER = (like_count + comment_count) / play_count.
- Top-level `is_video` reflects cover behavior; carousel covers are always image-style. Use `carousel[i].is_video` for per-slide rendering.
- Post permalink: `https://instagram.com/p/<shortcode>/` (or `/reel/<shortcode>/` for video reels).

### `Comment`

`{ username, text, like_count, created_at }` — used by both `media_info`'s embedded comments and `media_comments`. Replies are not embedded; if a thread has replies, paginate via `media_comments` separately.

---

## TikTok (tiktok_research tool)

API: EnsembleData via native `tiktok_research` tool. All actions share the same envelope shape — a discriminated union over `kind` — same as `instagram_research` above.

### User Research

```
tiktok_research(action="user_info", username="charlidamelio")                              # profile (id, sec_uid, stats)
tiktok_research(action="user_posts", username="charlidamelio", depth=2)                    # user posts (depth 1 = ~30 posts)
tiktok_research(action="user_search", keyword="brand")                                     # search users by keyword
tiktok_research(action="user_followers", id="<id>", sec_uid="<sec_uid>")                   # followers (requires both id + sec_uid from user_info)
tiktok_research(action="user_followings", id="<id>", sec_uid="<sec_uid>")                  # followings
tiktok_research(action="user_likes", sec_uid="<sec_uid>")                                  # liked posts
```

**Important:** Call `user_info` first to get `id` and `sec_uid` (returned under `data.user`).

### Content Discovery (keyword + hashtag)

```
tiktok_research(action="keyword_search", query="skincare", period=7)                       # search posts by keyword (~20/page, period: 1,7,30,90,180)
tiktok_research(action="keyword_search", query="skincare", period=7, sort=1)               # sort: 0=relevance, 1=most liked, 2=most recent
tiktok_research(action="keyword_search", query="skincare", country="US")                   # geo-targeted results
tiktok_research(action="keyword_full_search", query="skincare", period=7)                  # full search (all pages, single call)
tiktok_research(action="hashtag_search", name="skincare")                                  # hashtag posts (~20/page)
tiktok_research(action="hashtag_full_search", name="skincare", days=7)                     # all hashtag posts within N days (single call)
```

### Built-in Ranking (rank_results action)

Pipe a previously-fetched search envelope (or the raw EnsembleData shape — both are accepted) into `rank_results`:

```
tiktok_research(action="rank_results", data=<keyword_search_envelope>, top_k=3)            # top 3 by viral score
tiktok_research(action="rank_results", data=<envelope>, top_k=10, min_views=0)             # trend discovery preset
tiktok_research(action="rank_results", data=<envelope>, top_k=3, min_views=50000)          # brand/competitor preset
```

Ranking params: `top_k` (default 3), `min_views` (default 50000), `max_age` days (default 7).
Viral score = velocity (views/day) × engagement rate ((likes+comments)/views×100). Falls back to raw views if no videos pass filters.

### Music / Sounds

```
tiktok_research(action="music_search", query="viral")                                      # search sounds by name
tiktok_research(action="music_search", query="viral", sort=1)                              # sort: 0=relevance, 1=most used, 2=most recent, 3=shortest, 4=longest
tiktok_research(action="music_posts", music_id="<music_id>")                               # posts using a sound
tiktok_research(action="music_details", id="<music_id>")                                   # sound details
```

### Post Analysis

```
tiktok_research(action="post_info", url="https://www.tiktok.com/@user/video/123")          # post details by URL
tiktok_research(action="post_multi", ids="123;456;789")                                    # multiple posts by ID
tiktok_research(action="post_comments", aweme_id="<aweme_id>")                             # comments
tiktok_research(action="post_comment_replies", aweme_id="<aweme_id>", comment_id="<cid>")  # comment replies
```

### Live Search

```
tiktok_research(action="live_search", keyword="keyword")                                   # search live streams
tiktok_research(action="live_search", keyword="keyword", country="US")                     # geo-targeted live search
```

### Response Envelope

```json
{
  "kind": "keyword_search",
  "query": { /* echo of action + caller args */ },
  "data": { /* per-kind payload — see table below */ },
  "pagination": { "next_cursor": "..." } | null,
  "meta": { "source": "ensembledata", "engine": "tiktok", "fetched_at": "ISO-8601" },
  "error": null
}
```

On upstream / argument errors, `data` is `null` and `error` carries `{ code, message, status }` — clients still parse the same top-level dict. Bare `tool_error` (un-enveloped) is reserved for unexpected exceptions only.

### Per-kind `data` shapes

| `kind`                                                                                                                                           | `data`                          |
| ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------- |
| `user_info`                                                                                                                                      | `{ user: UserProfile }`         |
| `user_posts` / `user_likes` / `keyword_search` / `keyword_full_search` / `hashtag_search` / `hashtag_full_search` / `music_posts` / `post_multi` | `{ items: [Post, ...] }`        |
| `user_search` / `user_followers` / `user_followings`                                                                                             | `{ users: [UserSummary, ...] }` |
| `post_info`                                                                                                                                      | `{ post: Post }`                |
| `post_comments` / `post_comment_replies`                                                                                                         | `{ comments: [Comment, ...] }`  |
| `music_search`                                                                                                                                   | `{ music: [Music, ...] }`       |
| `music_details`                                                                                                                                  | `{ music: Music }`              |
| `live_search`                                                                                                                                    | `{ lives: [Live, ...] }`        |
| `rank_results`                                                                                                                                   | `{ items: [RankedItem, ...] }`  |

**`pagination`** populated for `user_posts` / `user_search` / `user_followers` / `user_followings` / `user_likes` / `post_comments` / `post_comment_replies` / `hashtag_search` / `hashtag_full_search` / `keyword_search` / `music_search` / `music_posts` / `live_search` when more pages exist; `null` otherwise.

### `Post` (data of every list-bearing action)

Field names are aligned with `instagram_research`'s `MediaItem` where the concept is identical (`display_url`, `caption`, `taken_at`, `play_count`, `like_count`, `comment_count`, `video_url`, `carousel_media_count`, `carousel`); TT-specific fields (`sec_uid`, `share_count`, `download_count`, `hashtags`, `music`, `width`/`height`, `full_name`) are additive.

```json
{
  "id": "7345",
  "url": "https://www.tiktok.com/@u/video/7345",
  "username": "u",
  "sec_uid": "MS4w...",
  "full_name": "Display Name",
  "caption": "...",
  "taken_at": 1750000000,
  "duration_sec": 12.5,
  "width": 1080, "height": 1920,
  "display_url": "https://...cover.jpeg",
  "video_url": "https://...video.mp4",
  "play_count": 100000, "like_count": 5000,
  "comment_count": 200, "share_count": 30,
  "download_count": 12,
  "hashtags": ["skincare", "glowup"],
  "music": {"id":"99","title":"...","author":"...","duration_sec":30.0,
            "play_url":"https://...","is_original":true,"user_count":5000},
  "carousel_media_count": 6,
  "carousel": [{"display_url": "https://...slide1.jpg"}, ...]
}
```

- ER = (like_count + comment_count) / play_count.
- For the rank_results pipeline, only `id`, `username`, `play_count`, `like_count`, `comment_count`, `taken_at`, `caption` are consulted.

### `UserProfile` (data of `user_info`)

Field names match `instagram_research`'s `UserProfile` where applicable (`full_name`, `biography`, `profile_pic_url`, `follower_count`, `following_count`, `media_count`, `category_name`, `external_url`, `is_verified`, `is_private`). TT-specific fields (`sec_uid`, `region`, `language`, `heart_count`) are additive.

```json
{
  "id": "12345",
  "sec_uid": "MS4w...",
  "username": "creator",
  "full_name": "Display Name",
  "biography": "...",
  "profile_pic_url": "https://...avatar.jpg",
  "follower_count": 760374,
  "following_count": 4,
  "media_count": 5515,
  "heart_count": 1234567,
  "region": "US",
  "language": "en",
  "category_name": "Fitness",
  "external_url": "https://creator.com",
  "is_verified": true,
  "is_private": true
}
```

### `Comment` (data of post_comments / post_comment_replies)

`{ id, username, text, like_count, reply_count, created_at }` — replies are not embedded; paginate via `post_comment_replies`. Diverges from IG (which omits `id` and `reply_count`) because TT needs both for `post_comment_replies`.

---

## YouTube (youtube tool)

Native tool backed by SearchAPI. All actions return the shared envelope `{kind, query, data, pagination, meta, error}` — same shape as `instagram_research` / `tiktok_research`. See `skills/media/youtube-research/SKILL.md` for the full per-kind contract.

### Data Retrieval

```
youtube(action="search", query="query")
youtube(action="video", video_id="VIDEO_ID")
youtube(action="transcript", video_id="VIDEO_ID")
youtube(action="comments", video_id="VIDEO_ID")
youtube(action="research", video_id="VIDEO_ID")
youtube(action="channel", channel_id="@handle")
youtube(action="channel", channel_id="@handle", sort_by="recently_uploaded")
youtube(action="channel", channel_id="@handle", sort_by="popular")
```

### Response Shapes (data per kind)

- `channel` → `{about, channel, videos_sections: [{videos: [{video_id, id, title, link, views, length, published_time, thumbnail}]}], shorts_sections}`
  - Omit `sort_by` for the home-tab layout. Pass it for a single flat sorted section.
  - `video_id` and `id` are both the YouTube video ID.
  - `published_time` is relative.
  - `length` is duration string.
- `search` → `{channels, videos: [{video_id, id, title, link, views, length, published_time, channel: {id, title}, thumbnail}], shorts, pagination}`
- `video` → `{video: {video_id, id, title, views, likes, length_seconds, published_time, description, thumbnail, ...}, channel, comment}`
- `research` → `{video, channel, comments: [...], comments_pagination}`

### OpenRouter Video Analysis

The `youtube` tool only does retrieval. For video analysis call `video_analyze` directly:

```
video_analyze(video_source="<youtube_url>", category="analysis_templates")
video_analyze(video_source="<youtube_url>", category="viral_analysis")
```

YouTube URLs are sent as OpenRouter video URLs. TikTok and other page URLs are downloaded via yt-dlp inside `video_analyze` and sent as base64 video data. **For Instagram reels** the agent container lacks IG cookies, so resolve the direct video URL first (`instagram_research(action="media_info", code="<shortcode>")` → `data.media.video_url`) and pass that URL to `video_analyze`.

---

## YouTube Shorts Trends (trends tool)

Native tool over the internal FNF Data Ingestion API. Browses viral shorts and trending channels from our own trending corpus, ranked by **lifetime views-per-hour** (`vph` = view_count / hours since published) — the live velocity signal. No external API quota cost.

**`trends` is available — use it** for any "what's trending/viral on Shorts" ask (no topic): load `toolsets=["trends"]` and call it; prefer it over `youtube`/`tiktok_research`. Don't env-check or claim it's unavailable — auth is proxy-injected.

### Discovery (preset actions)

```
trends(action="viral_now", hours=48, limit=20)
trends(action="growth_leaders", days=7, limit=20)
trends(action="competitor", channel_id="<channel_id>", limit=20)
```

### Raw queries (full filter control)

```
trends(action="videos", min_vph=1000, sort="vph", limit=50)
trends(action="channels", min_video_count=3, sort="avg_vph", limit=50)
trends(action="run_status", run_id="<run_id>")
```

### When to use `trends` vs `youtube`

- **`trends` (DEFAULT for trending Shorts)** — "what's trending / going viral on YouTube Shorts", most-viral-by-views-per-hour, trending or fastest-growing channels.
- **`youtube`** — only for a SPECIFIC known video/channel or an explicit live web search.

All IDs (`channel_id`, `video_id`, `run_id`) must come from a prior `trends` response.

---

## Trending Shorts by KEYWORD (trending_shorts_search tool)

Native tool over the same FNF Data Ingestion corpus. It takes a free-text query (`q`) and returns the matching trending Shorts from our OWN corpus, ranked best-first.

```
trending_shorts_search(query="satisfying visual ASMR")
trending_shorts_search(query="cooking shorts", limit=20)
trending_shorts_search(query="gaming highlights", last_n_days=0, min_view_count=0)
```

Returns `{items, total, query}` ranked best-first. Usage rules:
- **Call it ONCE per query.** The window auto-widens internally.
- **Omit `limit`** unless the user asked for a specific number.
- If it returns an **empty result**, follow its `fallback` note and call `youtube` once for live results.

### `trending_shorts_search` vs `trends` vs `youtube`
- **`trending_shorts_search`** — trending Shorts matching a keyword/search term.
- **`trends`** — trending Shorts with no search term.
- **`youtube`** — a specific known video/channel or explicit live web search.

---

## Ad Libraries (ads tool)

Native tool covering Meta, TikTok, LinkedIn, and Reddit ad libraries.

### Meta (Facebook/Instagram)

```
ads(action="meta_search", query="keyword", active_status="active", sort_by="impressions_high_to_low")
ads(action="meta_search", page_id="<id>", active_status="active")
ads(action="meta_page", page_id="<id>")
```

### TikTok Ads

```
ads(action="tiktok_search", query="keyword", sort_by="unique_users_seen_high_to_low")
ads(action="tiktok_advertiser", advertiser_id="<advertiser_id>")
```

### LinkedIn Ads

```
ads(action="linkedin_search", query="keyword", time_period="last_30_days")
ads(action="linkedin_advertiser", advertiser="<company name>")
```

### Reddit Ads

```
ads(action="reddit_search", query="keyword", industry="TECH_B2C", post_type="VIDEO")
```

### Finding Winners (default filters)

1. **Active ads only:** `active_status="active"` (Meta)
2. **Sort by reach:** `sort_by="impressions_high_to_low"` (Meta) / `sort_by="unique_users_seen_high_to_low"` (TikTok)
3. **Longevity filter:** After fetching, only present ads running 3+ days
   - 3-7 days: testing phase
   - 7-14 days: likely profitable
   - 14-30 days: proven winner
   - 30+ days: evergreen creative

---

## Web Content (web_search + web_extract)

Two native tools cover the web layer:

```
web_search(query="latest news")
web_extract(urls=["https://example.com"])
web_extract(urls=["https://example.com"], summary=True)
web_extract(urls=["https://example.com"], highlights=True, highlights_query="pricing")
web_extract(urls=["https://example.com"], extract_prompt="Extract key product data")
web_extract(urls=["https://example.com"], subpages=5, subpage_target="pricing")
```

Notes:

- `web_extract` accepts up to 5 URLs per call and refuses pages over 2M chars.
- For large e-commerce pages, prefer `extract_prompt` or `highlights_query`.
- For social-media research use dedicated tools.
- If a URL fails or times out, fall through to the browser tool.

---

## Hook Extraction for Generation Downstream

**Mandatory when:** either cross-platform `intent=trend_discovery` (A) or `intent=viral_analysis` (D), and the brief contains a generation verb paired with a countable video output.

**Skipped when:** pure research or TikTok-only generation.

For every selected top-N video, call `video_analyze` to extract the real hook.

### Command per video

```
video_analyze(video_source="<video_url>", category="viral_analysis")
```

For Instagram reels, resolve the direct `video_url` first with `instagram_research(action="media_info", code="<shortcode>")`.

### Parallelization

Run all N analyses in parallel. Do not serialize.

### Output → HANDOFF mapping (schema v2)

Each `viral_analysis` run returns CONCEPT / HOOK / RETENTION MECHANISMS / REWARD / AUDIO & MUSIC / SCRIPT. Map it to:

| HANDOFF field                      | Source |
| ---------------------------------- | ------ |
| `source_signature.format_type`     | One-line archetype label synthesized from CONCEPT |
| `source_signature.mechanic`        | Near-verbatim from CONCEPT or RETENTION |
| `source_signature.must_preserve[]` | At least 3 concrete elements from RETENTION + SCRIPT |
| `brand_adaptation.topic_shift`     | "from <source topic> → <client topic>" |
| `brand_adaptation.payoff_message`  | Closing brand message |
| `hook.visual`                      | HOOK → VISUAL verbatim |
| `hook.line`                        | HOOK → AUDIO first spoken line verbatim |
| `hook.psychology`                  | One of the 7 values in `concept-generation.md` |
| `hook.sound_cue`                   | HOOK → AUDIO cue |
| `hook.on_screen_text[]`            | Every hook overlay with timing and position |
| `hook.reference_url`               | Analyzed video URL |
| `beats[]`                          | One beat per SCRIPT scene |
| `total_duration_s`                 | Sum of beat durations, ≤15 |
| `audio_overall`                    | AUDIO & MUSIC condensed to one line |
| `reference_urls`                   | `[video_url]` |

**Dense-copy rule:** lift concrete visuals, overlays, and must-preserve items from the Gemini output rather than summarizing. Compression happens by dropping non-essential beats.

**Tier:** Always `"director"`.

**style_preset:** Pick per concept: `entertainment`, `authority`, `educational`, or `practical`.

### When source video is longer than 30s

Keep the opening hook beat, signature mechanic beat, and a single closing/payoff beat. Drop entire non-essential beats rather than summarizing kept beats.

---

## Viral Content Analysis Pipeline

Use this pipeline only for cross-platform research/HANDOFF or explicit Mode D analysis.

### Step 0: Identify Product

Determine exact brand, product, and broad category. Do not invent creative search phrases.

### Step 1: Discover Content

Run all groups in parallel:

```
tiktok_research(action="keyword_search", query="<brand>", period=7)
instagram_research(action="search", query="<brand>")
tiktok_research(action="keyword_search", query="<brand> <product>", period=7)
instagram_research(action="search", query="<brand> <product>")
tiktok_research(action="hashtag_search", name="<category>")
tiktok_research(action="music_search", query="<category>")
ads(action="meta_search", query="<category>", active_status="active", sort_by="impressions_high_to_low")
ads(action="tiktok_search", query="<category>", sort_by="unique_users_seen_high_to_low")
web_search(query="<category> trending tiktok 2026")
```

Then use top returned hashtags to search both TikTok and Instagram.

### Step 2: Rank Videos

```
tiktok_research(action="rank_results", data=<keyword_search_result>, top_k=3)
tiktok_research(action="rank_results", data=<hashtag_search_result>, top_k=3)
```

Freshness presets:

- Trend discovery → `top_k=10, max_age=3, min_views=0`
- Brand/product research → `top_k=3, max_age=7, min_views=50000`
- Deep historical → `top_k=10, max_age=30, min_views=10000`

Collect, deduplicate, and take the overall top 5.

### Step 3: Analyze Video

```
video_analyze(video_source="<video_url>", category="analysis_templates")
```

For Instagram, resolve the direct URL first. Output a detailed scene-by-scene production blueprint.

### Step 4: Generate Concepts

Generate 3 new video concepts based on analyzed references and client profile. Use `references/concept-generation.md`.

### Step 5: Visual Preview (optional)

Delegate to `/image-generation` or `/video-generation`. Never call generation tools directly from this skill.

---

## Video Adaptation — NOT IN THIS SKILL

Full adaptation belongs to `video-adapt`, which owns `vadapt_step_0a`, `vadapt_plan`, `vadapt_adapt`, `vadapt_element`, and `vadapt_render`.

This skill covers research and Mode A/D analysis only. If a brief includes a source video URL with explicit adaptation intent, refuse adaptation here and load `video-adapt`.

---

## Viral Analysis (on-demand)

For "why is this video viral" use:

```
video_analyze(video_source="<video_url>", category="viral_analysis")
```

For Instagram, resolve the direct video URL first.

---

## Mode C — Creator DNA (persona-clone preflight)

### Entry gate

Before any other Mode C tool call:

1. Read `skills/research/trend-picker/references/persona-clone.md`.
2. Run `ask_question` to pick **Deep** vs **Quick**.
3. Keep selected depth and current phase in active conversation state. Do not claim persistence without a persistence tool.

### Workflow

1. Pull reels respecting user scope:

   | Wording in brief | Action | Sort |
   | --- | --- | --- |
   | top/viral/best or no hint | `instagram_research(action="user_reels", depth=2, sort="views")` | views |
   | last N/recent/latest posts | `instagram_research(action="user_posts", depth=ceil(N/10))` | date |
   | recent/latest reels | `instagram_research(action="user_reels", depth=2, sort="date")` | date |

   For TikTok use `tiktok_research(action="user_posts", username="<handle>", depth=2)`.

   Within the fetched set, take top 3 by `play_count` for Gemini DNA, or top 5 for deep mode. Show the analyzed URLs.

2. Analyze each reel in parallel:

   ```
   video_analyze(video_source="<reel_url>", category="creator_dna")
   ```

3. Aggregate signatures repeating across at least 2 reels:

   ```json
   {
     "creator": "@handle",
     "reels_analyzed": 3,
     "per_reel": [{"url": "...", "dna": {...}}],
     "aggregate_dna": {
       "stable_visual": [],
       "stable_kinetic": [],
       "stable_audio": [],
       "stable_narrative": [],
       "replicable_signatures": [],
       "non_replicable_signatures": []
     }
   }
   ```

4. Write the report under the active sandbox workspace, upload with `upload`, and return only the public upload URL plus reel URLs.

### Output contract

```json
{
  "mode": "creator_dna",
  "creator": "@handle",
  "reels_analyzed": 3,
  "reel_urls": ["url1", "url2", "url3"],
  "dna_report_url": "https://...",
  "aggregate_summary": {
    "stable_visual": ["3-5 bullets"],
    "stable_kinetic": ["3-5 bullets"],
    "replicable_signatures": ["top 3 traits to transplant"]
  }
}
```

**Failure policy:** if 1–2 reels fail, continue with remaining ≥1. If all fail, escalate with alternatives. Never fabricate DNA from metadata alone.

Mode C does not train Soul IDs, generate media, or run adaptation.

---

## Reference Templates

Video-analysis prompts are `video_analyze` categories:

| Category             | Purpose | Used by |
| -------------------- | ------- | ------- |
| `analysis_templates` | Scene-by-scene storyboard | trend-picker, video-adapt |
| `viral_analysis`     | Strategic viral analysis | trend-picker Mode D |
| `creator_dna`        | Cross-reel DNA extraction | trend-picker Mode C |
| `adapt_product`      | Legacy product adaptation | direct legacy callers |
| `adapt_avatar`       | Legacy avatar replacement | direct legacy callers |

Claude-side reference:

```
references/
└── concept-generation.md
```

## Error Handling

Native tools return the shared envelope; on failure `data` is `null` and `error` carries `{ code, message, status }`.

- Missing tool/API key → surface to user, don't retry
- `status 401` → invalid API key
- `status 429` → rate limited, wait and retry
- yt-dlp failure → video may be private or region-locked

## Data Integrity

- **Work only with user-provided inputs.** Do not pull from caches, prior sessions, `/tmp`, or adjacent files unless explicitly requested.
- **Retry transient failures silently up to 3 times.**
- **URL fallback chain:** `web_extract` up to 3 times, then `web_search`, then browser.
- **After all tiers fail, escalate with 2–3 concrete alternatives.** Never silently substitute inferred or cached data.
