---
name: design-md
description: Author, validate, diff, and export DESIGN.md files — Google's open-source format spec that gives coding agents a persistent, structured understanding of a design system (tokens + rationale in one file).
---

# DESIGN.md Skill

DESIGN.md is Google's open spec (Apache-2.0) for describing a visual identity to coding agents. One file combines YAML front matter (machine-readable design tokens) and Markdown body (human-readable rationale).

## File anatomy

```yaml
---
version: alpha
name: Heritage
colors:
  primary: "#1A1C1E"
  secondary: "#6C7278"
  tertiary: "#B8422E"
  neutral: "#F7F5F2"
typography:
  h1:
    fontFamily: Public Sans
    fontSize: 3rem
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.02em"
---
```

## Token types

| Type | Format | Example |
|------|--------|---------|
| Color | `#` + hex (sRGB) | `"#1A1C1E"` |
| Dimension | number + unit | `48px`, `-0.02em` |
| Token reference | `{path.to.token}` | `{colors.primary}` |

## Canonical section order

1. Overview
2. Colors
3. Typography
4. Layout & Spacing
5. Elevation & Depth
6. Shapes
7. Components
8. Do's and Don'ts

## CLI

```bash
npx -y @google/design.md lint DESIGN.md
npx -y @google/design.md diff DESIGN.md DESIGN-v2.md
npx -y @google/design.md export --format tailwind DESIGN.md > tailwind.theme.json
npx -y @google/design.md export --format dtcg DESIGN.md > tokens.json
```