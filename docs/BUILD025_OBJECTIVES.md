# Build025 / v0.1.4 — numbered operation conditions

User test screenshots, 2026-10-15:

- Elgan's requested spelling is **Elgan Roddick**. It is present in canonical
  glossary/story sources and local builds023/024. The older Rhodic spelling
  in the screenshot is not the current resolved story text. Build025 includes
  the correction and an updated version/Retro Trans footer for identification.
- Victory: **Defeat all enemies.** Defeat: **Any allied unit is defeated.**
  Both were already translated in the catalog; their runtime formatting was
  missing from the exact-match English lookup.

The NPJB00689 formatter at 0x1a95c8 keeps original Japanese in 101-byte slots,
in 103-byte records. It appends native fullwidth number prefixes 1–3 for
victory/defeat entries, splits at LF, and pads continuation lines with two
ideographic spaces. Unnumbered SR rows do not receive these prefixes.

The new source-guarded adapter generates exact lookup keys for all three
numbers, bare SR rows and continuation forms. The original native buffers,
color/state flags and operation tables remain unchanged. English stays in
owned display storage and includes the full condition text. There are 72
operation occurrences / 37 distinct original conditions in this category.
Shared first-line fragments use their unambiguous standalone translation;
English wrapping never pulls a following clause into a shared source key.

Numbered lines include prefix width in the 950px limit. The two screenshot
rows measure 366px and 486px at 32px; all generated forms fit. Native lookup
execution tests cover both direct and converted drawers, 1/2/3 numbering,
continuations, unchanged native tables, unrelated-text fallback and guards.
The old build024 executable lacks the composite numbered key, confirming the
specific gap rather than missing English catalog entries.

Four new focused regressions and six existing category/layout checks pass.
Fresh build025/v0.1.4 has completed its archive/folder/overlay/ZIP readbacks
and success stamp. An independent compiled-data check verifies all 296
formatted lookup cases and confirms STG00004 contains encoded Roddick and no
Rhodic. The packed title/footer identifies v0.1.4.

Five diagnostic metric rows were refreshed from the actual compiled font:
the running builder had loaded the earlier canonical-line metric formula.
BUILD_REPORT-before-metric-refresh.json preserves its initial report. Only
diagnostic line counts/widths changed; game bytes and the success stamp did
not. Source now measures the actual wrapped display consistently.

All three native offline decryptions pass with exit0 and byte-identical
outputs. The old shared checker timed out before logging; a fresh isolated
runtime in `work/offline_rpcs3_025_retry01` passes, with the first-attempt report
preserved. Future verification can select a fresh runtime with `--runtime`.

Local CFW package:
`work/builds/rengoku_en_025_cfw_pkg_test1/SRW-Z3-R-NPJB00689-English-build025-CFW-test1.pkg`.
621,868,688 bytes; SHA256
`52caaa873f3e2c3322f9d2e216ce1013965a903433fa4548bd53a587ff2b184a`.
Full cipher/authentication roundtrip and all 77 package-member hashes pass.
Package and title version/credit agree. Native installation verification in
`work/rpcs3_cfw_pkg025_test1` matches all 77 hashes, with the known teardown
assertion 3221226505 kept separate from successful extraction.
Source/layout tests and compiled data readback do not establish
live gameplay or physical PS3 testing.
