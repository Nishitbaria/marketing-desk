# Exact Brandkit logo-export payloads

Use with `logo-export --input`:

```json
{
  "name": "northline-symbol",
  "logo_svg": "https://replace-with-selected-recraft-result.svg",
  "delivery": "user",
  "replacements": [],
  "include_monochrome": false
}
```

For an explicitly requested one-color export, add `"single_color": "#101820"`.

For explicitly requested black/white production variants, set `"include_monochrome": true` and add `"primary_color": "#00AEEF"`.

Upload returned SVG and PNG paths together with `upload(svg_mode="preserve")`. Use the returned `uploads[].file`, `uploads[].type`, and `uploads[].url` exactly; never label a rasterized `.png` as SVG.