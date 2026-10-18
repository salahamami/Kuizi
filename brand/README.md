# Kuizi brand sources

Source files for the Kuizi brand (T231, [ADR 0008](../docs/architecture/decisions/0008-monorepo-layout-and-toolchains.md)). How to use them, colours, clear space, sizes and the voice: [`docs/design/brand-guide.md`](../docs/design/brand-guide.md). **Status: draft** until the Arabic type review and the trademark check in [`docs/design/brand-reviews.md`](../docs/design/brand-reviews.md) are done.

Every file is a hand-built SVG: a `viewBox`, flat fills in Cyanotype colours, no fonts, no `<text>`, no raster images, no gradients or filters. Letters are drawn as shapes, so they render the same everywhere.

| Folder | Files |
| --- | --- |
| `mark/` | Star mark: `kuizi-star.svg` (cyan, light backgrounds), `-dark` (cyan-light, night backgrounds), `-mono` (one colour, `currentColor`), `-micro` (24 px and below), `-construction` (grid diagram) |
| `logo/` | Logotypes `kuizi-wordmark-latin.svg`, `kuizi-wordmark-arabic.svg` (`currentColor`); lockups `kuizi-lockup-{latin,arabic,bilingual}-{light,dark,mono}.svg`; `kuizi-wordmarks-construction.svg` (shared metrics) |
| `app-icon/ios/` | 1024 masters: `kuizi-ios-default.svg` (opaque), `-dark` (transparent), `-tinted` (grayscale) |
| `app-icon/android/` | Adaptive layers on 108 dp: `kuizi-adaptive-{background,foreground,monochrome}.svg`; legacy `kuizi-legacy-{square,round}.svg` (48 dp) |
| `app-icon/web/` | `favicon.svg`, PWA `icon-any.svg` and `icon-maskable.svg` |
| `social/` | `og-image.svg` (1200 × 630), `play-feature-graphic.svg` (1024 × 500) |
| `export.json` | Every PNG to render: source, output path, pixel size, background |
| `export/` | Rendered PNGs (created from `export.json`; do not edit by hand) |

## Rendering

Render each entry of [`export.json`](export.json) with any standards-compliant SVG renderer, scaling the whole `viewBox` to the listed size. `background` is either `transparent` or a colour to flatten onto (no alpha channel). For example, with resvg:

```sh
resvg -w 1024 -h 1024 --background '#0B1E3A' brand/app-icon/ios/kuizi-ios-default.svg brand/export/ios/AppIcon-1024.png
```

Change a shape in the SVG source, never in a PNG, then re-render.

The PNGs in `export/` were first rendered on 2026-10-18 with headless Chromium (Playwright), each SVG drawn at exactly the listed size; entries with a background colour were flattened to RGB without alpha, and `favicon.ico` bundles the 16, 32 and 48 px favicons. All 67 outputs were checked for size and alpha channel, and previews were looked at on light and dark backgrounds (favicon at 16 px, Arabic logotype at 90 px, adaptive layers, social image).
