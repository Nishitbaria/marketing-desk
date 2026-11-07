# Subtitle fonts
`burn_caps_clean.sh` looks for a bold .ttf/.otf here (default family: Poppins —
drop in `Poppins-Bold.ttf`, SIL OFL, Google Fonts). Binaries are NOT committed
(marketplace sync skips them): download the .ttf into this folder on the machine
that burns subtitles, or pass `--fontsdir`/`--font`. Without it libass falls back
to a system font (the script warns; the look will differ).
