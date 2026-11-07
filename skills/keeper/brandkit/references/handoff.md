# Brandkit state routing

Brandkit approval state lives in `.brandkit/state.json` inside the current chat's managed-sandbox working directory. Drafts never enter it. The script writes atomically and preserves independent logo, palette, typography, visual-axis, and downstream-element revisions.

Run every operation through:

```bash
python3 "$BRANDKIT_SKILL/scripts/brandkit.py" state --action ACTION [--input INPUT.json]
```

Create payload files with `write_file`; never interpolate JSON or user text into the shell command.

Before the first state write, load [exact state payloads](state-payloads.md) and copy only the matching complete object shape. Replace values, not keys or nesting.

## Call moments

### Start of any Brandkit turn

```bash
python3 "$BRANDKIT_SKILL/scripts/brandkit.py" state --action get_status
```

### Lock user-supplied official assets

Immediately after asset analysis, write one input object with the matching top-level slot, then call only its action:

```text
lock_authoritative_logo       {"source_summary": "...", "logo": {...}}
lock_authoritative_palette    {"source_summary": "...", "palette": {...}}
lock_authoritative_typography {"source_summary": "...", "typography": {...}}
```

These actions preserve official assets the user already owns. They do not approve generated work, and an authoritative slot cannot be replaced by a later generated choice.

### Persist visual axes

```json
{
  "visual_axes": {
    "restrained_expressive": 50,
    "geometric_organic": 50,
    "familiar_experimental": 50
  }
}
```

Call `set_visual_axes`; later read with `get_visual_axes`.

### Read only the required slot

- `get_logo` before logo placement, export, or logo-dependent revisions.
- `get_palette` for color-dependent work.
- `get_typography` for type-dependent work.
- `get_essential_kit` only when logo, palette, and typography are all genuinely required.

Never use `get_essential_kit` as a universal gate for partial outputs.

### Browse approved downstream elements

Call `list_brandbook_elements`, then use `get_brandbook_element` with:

```json
{ "key": "exact-element-key" }
```

### Approve generated elements independently

After an explicit user selection, write the exact selected object under its slot and call:

```text
approve_logo       {"approval_summary": "...", "logo": {...}}
approve_palette    {"approval_summary": "...", "palette": {...}}
approve_typography {"approval_summary": "...", "typography": {...}}
```

The script assigns the next revision. Do not put generated-but-unapproved work into state.

### Approve a downstream element

Only after explicit approval:

```json
{
  "approval_summary": "User approved the primary mockup.",
  "required_slots": ["logo", "palette"],
  "brandbook_element": {
    "key": "mockup-primary",
    "kind": "mockup",
    "name": "Primary packaging mockup",
    "asset": { "id": "...", "url": "..." }
  }
}
```

Call `approve_brandbook_element`. Declare exactly the foundation slots the output used.

## Recovery

The per-chat sandbox workspace is the durable source of truth. If the state file is unexpectedly absent after this chat previously had approvals, do not infer or silently recreate approvals. Stop and report the recovery failure. An explicit user request to restart may use `clear`.

## Never

- Never load the entire state file directly when a narrow read action is enough.
- Never put drafts into an authoritative lock.
- Never delay locking a user-declared official asset.
- Never store generated-but-unapproved assets.
- Never require or request approval for an unrelated missing slot.
- Never ask for combined approval after independent selections.
- Never use this state outside Brandkit.
- Never use user memory or `element` as a substitute.