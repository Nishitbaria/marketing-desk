# Essential Kit selection

The visual concept is not a separate abstract direction. It is the combined result of the user's selected palette, logo mark, and typography.

Each generated element remains draft only until the user selects that element. Approved palette, logo, and typography slots persist independently.

## Input analysis

Build options from:

- Brand/product brief
- Audience, positioning, and tone supplied by the user
- User preferences and comments
- Uploaded references, screenshots, logos, fonts, colors, or existing assets

Invite uploads before starting. Ask what the user specifically likes about each reference: palette, typography, composition, shape language, material, or overall aesthetic. If they give no explanation, use the overall character as inspiration without copying distinctive elements.

## Step 1 — Palette options

For every interactive new-identity flow that needs a logo, start here and complete this review before Step 2. Intake phrases such as "pastel," "blue," or "warm neutrals" are preferences used to build the options, not a selected palette. Skip this review only when the user supplied an authoritative palette or explicitly selected exact palette colors, or when the user requested auto/no-question mode. In auto/no-question mode, build one exact palette from the brief and call `approve_palette` before Step 2; continue only after the state script confirms success. Never merely describe that palette as locked.

Create 2–3 considered palette options from the brief and references. Each option must include:

- Named flat colors with exact hex values
- Background and text colors
- Optional gradients only when relevant
- One-sentence rationale
- Small usage examples
- 2–3 rough logo mechanism seeds showing what the palette could support

`logo_ideas` is mandatory for every palette option. The preview script rejects a palette review that omits them.

Render all options in editable HTML with `scripts/brandkit.py preview`, upload the resulting HTML files through `upload`, and place the returned URLs into `jsx_preview`. Do not generate PNG or SVG duplicates and do not send filenames alone.

Every palette review object must set `stage: "palette"`. Omit `display_font`, `body_font`, `logo_svg`, `headline`, and `body`; `logo_ideas` must contain 2–3 entries. The palette board must not display a typography specimen, placeholder font pairing, or wordmark. Typography appears only after the user selects a logo.

Load `inline-widgets.md`. Upload every returned local HTML path with `upload`, embed each resulting `uploads[].url` directly in the exact fenced `jsx_preview` syntax, then provide the same URL as the editable HTML download. Never use literal `<jsx_preview>` tags. For 2–3 HTML options, use a vertical full-width stack at every viewport size; never place iframe cards in responsive columns.

After showing the assets, send a normal assistant message:

> Take your time reviewing the palettes. Reply with the option you prefer and any colors you want changed, added, or removed.

Do not use `ask_question` or a multiple-choice list. Wait for the user's ordinary next message.

When the user selects a palette, immediately call the Brandkit state script's `approve_palette` action with that exact palette and the selection message as approval evidence. Continue only if the original request needs another missing slot or output.

## Step 2 — Logo mark options

Enter this step only after Step 1 produced a user-selected and persisted palette, or after an authoritative/explicitly selected palette was already available. Never treat general color preferences from intake as palette selection.

For this entire internal sequence, send at most one short user-facing status: "I'm generating three logo options now." After it, send no other process/status text until the finished review. Do not mention Design Brain, mechanisms, enhancer prompts, model lookup, Recraft parameters, or intermediate validation.

Using the selected draft palette plus Brandkit Design Brain:

1. Design Brain returns exactly three original logo mechanisms.
2. Call `enhancer(flow="brandkit-logo")` once per mechanism.
3. Pass each enhanced prompt separately to Recraft V4.1 with the selected logo color subset in `params.colors` and selected background in `params.background_color`. Use the one, two, or three logo colors the concept needs; never pad to three. Exceed three only when the user explicitly requested more.
4. Use Recraft's returned SVG URLs directly. Do not pass them through the HTML preview script.
5. Show all three in the inline logo-review widget with direct SVG links. This widget is mandatory in interactive and explicit auto/no-question modes; bare SVG URLs are not a review.

When interaction is allowed, send a normal message asking the user to review and comment. In explicit auto/no-question mode, do not ask a follow-up question. Do not self-select, use `image_analyze` as approval, or start typography before the user responds.

When the user selects a logo, immediately call the Brandkit state script's `approve_logo` action with the exact Recraft SVG asset, name, fingerprint, and any explicitly requested variants. A logo-only request is complete at this point; typography is not mandatory.

## Step 3 — Typography options

Using Design Brain with the selected draft palette and selected Recraft SVG:

- Propose 2–3 suitable font pairs.
- Use user-uploaded licensed fonts when supplied; otherwise use verified Google Fonts and include official download links.
- Render the real brand name and short sample copy through `scripts/brandkit.py preview`.
- Show the selected mark next to each wordmark treatment so type/mark cohesion is visible.
- Use one contrasting `text_color` for both display and body samples; it must not equal the background color.
- Return a visible preview/card and downloadable HTML. Present both through the inline typography-review widget.

Every typography review object must set `stage: "typography"` and include `display_font`, `body_font`, `logo_svg`, and one shared contrasting `text_color`.

Ask for feedback in a normal message and wait. Do not use a choice list.

When the user selects a type pair, immediately call the Brandkit state script's `approve_typography` action with the exact approved font metadata and specimen.

## Optional combined Essential Kit HTML

Render a combined board only when all three slots are approved and the user requested a full identity/Brandkit or asks to see them together. Otherwise show the available individual review boards. Use `scripts/brandkit.py preview` with one `stage: "essential"` review containing the approved logo, palette, and type slots.

Upload the returned HTML file, embed its URL with the `jsx_preview` template, and include full-screen/editable HTML links. This board is a presentation view, not another approval gate. Do not ask the user to approve the system again.

## Continue the original request

Once the slots required by the first-message deliverables are approved, load those output modules and continue. Never force missing unrelated slots or ask the user to choose scope again.