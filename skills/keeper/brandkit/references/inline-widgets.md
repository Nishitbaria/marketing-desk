# Inline review widgets

Show every Brandkit review stage directly inside chat using `jsx_preview`. Editable HTML/SVG files remain downloads; the widget is the immediate review surface.

## Rules

- Output raw JSX inside a fenced `jsx_preview` block.
- Use the exact `jsx_preview` template below with the uploaded HTML URL. Its first line must be three backticks immediately followed by `jsx_preview`; its last line must be three backticks. Never remove either fence or paste `<div>`, `<iframe>`, or `<a>` as ordinary markdown.
- The renderer recognizes only that fenced code-block syntax. Literal `<jsx_preview>` and `</jsx_preview>` tags are invalid, render as ordinary text, and must never appear.
- No imports, exports, component declarations, hooks, scripts, or fetches.
- Use ordinary `div`, `iframe`, `img`, `a`, headings, and text.
- Use host CSS variables for widget chrome.
- Do not create fake buttons or selection controls. Ask for feedback in normal chat after the widget and STOP.
- Never print filenames without rendering the associated visual, except final brandbook delivery, which intentionally contains only PPTX and PDF links.

## HTML palette, typography, and Essential Kit reviews

`scripts/brandkit.py preview` returns local HTML paths. Upload them with `upload`, then use each returned `uploads[].url` in this exact structure:

Before writing a preview input, load [exact preview payloads](preview-payloads.md) and copy the complete shape for that stage.

```jsx_preview
<div className="overflow-hidden rounded-xl bg-[var(--color-surface-primary)]">
  <iframe
    src="RETURNED_WIDGET_READY_URL"
    title="Brandkit review"
    className="h-[520px] w-full border-0"
  />
  <div className="flex gap-3 p-3 text-sm">
    <a href="RETURNED_WIDGET_READY_URL" target="_blank" rel="noreferrer">
      View full screen
    </a>
    <a href="RETURNED_WIDGET_READY_URL" className="underline">
      Download editable HTML
    </a>
  </div>
</div>
```

Replace every placeholder with the actual returned URL. For 2–3 HTML options, repeat the complete card inside one `<div className="grid gap-6">`. Keep every iframe card full width and vertically stacked at every breakpoint. Never add `grid-cols-2`, `grid-cols-3`, `md:grid-cols-*`, or another multi-column class to an HTML-review wrapper. Do not make the user open each file to understand it.

Before sending, silently verify that every review uses the fenced form shown above. If either fence is missing or an XML-like `jsx_preview` tag appears, fix the response before sending it.

## Recraft logo review

The HTML preview script does not handle logo creation or comparison. Embed the three Recraft SVG result URLs directly. This widget remains mandatory in explicit auto/no-question mode; never replace it with a prose list of bare SVG URLs:

```jsx_preview
<div className="grid gap-4 md:grid-cols-3">
  <div className="rounded-xl border border-[var(--color-neutral-surface-subtle)] bg-[var(--color-surface-primary)] p-3">
    <h3 className="mb-2 text-sm font-semibold">Candidate 1</h3>
    <img src="RECRAFT_SVG_URL_1" alt="Logo candidate 1" className="aspect-square w-full object-contain" />
    <a href="RECRAFT_SVG_URL_1" className="mt-2 inline-block text-sm underline">
      Download SVG
    </a>
  </div>
  {/* Repeat with the real candidate 2 and 3 URLs. */}
</div>
```

Do not redraw, normalize, recolor, rasterize, or otherwise modify the returned Recraft SVGs.

## Logo color-revision/export review

When `scripts/brandkit.py logo-export` returns the color pair and any explicitly requested monochrome/reverse or single-color SVG/2048 PNG pairs, upload only the files intended for the user and set `svg_mode="preserve"` so SVG bytes remain editable:

- With `delivery: "internal"`, show only the selected full-color preview and do not link the internal files.
- With `delivery: "user"`, link every returned SVG and PNG variant.
- State that geometry is unchanged and the PNG is a review/export preview.
- Never show only PNG filenames or hide the SVG variants.

## Review messages

After palette review:

> Take your time. Reply with the palette you prefer and any colors you want changed.

After logo review:

> Take your time reviewing the three marks. Reply with the direction you prefer and any shape or balance changes.

After typography review:

> Review how each type pair works with the selected mark and palette. Reply with your preferred direction or changes.

After showing the combined Essential Kit HTML preview:

> Does the complete logo, palette, and typography system feel right together? Approve it or tell me which element should change.

Each message ends the turn. Never continue to the next stage until the user responds.