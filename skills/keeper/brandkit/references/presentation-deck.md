# Presentation deck

Create once logo, palette, and typography are separately approved. Do not ask for another combined approval.

Read `get_essential_kit` through the Brandkit state script, then load the `powerpoint` skill with `skill_view`.

## Intake

Require:

- deck purpose
- audience
- source content
- desired slide count
- exact claims/data
- requested aspect ratio
- existing PPTX template, if any

Do not invent mission, values, market statistics, pricing, claims, contacts, or product variants to fill slides.

## Build

- Existing PPTX → edit its masters/layouts.
- No template → create a small coherent layout family in PptxGenJS.
- Use approved logo, palette, and fonts.
- Keep all text/shapes editable.
- Keep imagery replaceable.
- Use generated imagery only as optional supporting assets.
- Do not flatten whole slides into images.

Create only slide types required by the content, such as cover, divider, image/copy, comparison, process, data, quote, and closing.

## QA and approval

Follow the PowerPoint render/inspect/fix loop. Check overflow, collisions, alignment, font substitution, contrast, and placeholder residue.

Deliver editable PPTX plus previews/PDF when requested. Save only the approved deck through `approve_brandbook_element` using key `presentation-deck` and `required_slots: ["logo","palette","typography"]`.
