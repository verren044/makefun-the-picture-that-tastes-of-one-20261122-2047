# BUILD_LOG — the-picture-that-tastes-of-one-20261122-2047

- Competition: "The picture that tastes of one ingredient", $20, deadline 2026-11-22T21:47:00Z (04:47 WIB 23 Nov 2026).
- Kit: level 36 (0.1.0, build 98fe3e67b4f8). Output: /output/entry.png, PNG/JPEG, <=1 MiB, <=1024x1024.
- Suggested repo: `makefun-the-picture-that-tastes-of-one-20261122-2047` (owner verren044).
- Entry title: "One Ingredient — Strawberry".

## Approach
One hero ingredient fills the frame so the picture reads at ~300px: a single
ripe strawberry in macro, drawn fully in code with Pillow (no external images,
no network). Layered build: warm dark background with soft bokeh, radial
gradient berry body with flesh speckle texture, staggered seeds in shallow pit
shadows, dew drops, gloss highlight, green calyx + stem, a halved strawberry
(cut face, white core, seed ring) cropped at the bottom-left corner, vignette,
and a small caption "ONE INGREDIENT · STRAWBERRY". Fonts (DejaVu) are bundled
under fonts/ so rendering is identical in the grader sandbox.

## Practice
- `MAKEFUN_OUTPUT_DIR=/tmp/out1 python3 main.py` -> entry.png 301,566 bytes, 1024x1024 PNG.
- Second run byte-identical: sha256 4bfa7ca02dd4f722986ab3ce02132ebc34fda4c7579728678a3547229c636cc3 (both runs).
- Rendered image inspected visually: berry silhouette, seeds, calyx and
  caption all legible; fixed seed-grid regularity (stagger + pit shadows) and
  caption/half-berry overlap before final run.

## Notes for submitter
- Do NOT commit kit/. Repo must be created after the competition opens.
- Entry is main.py (Python 3.13, stdlib + Pillow, deterministic, no clock/network).
