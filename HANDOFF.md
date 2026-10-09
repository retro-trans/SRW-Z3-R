# Public repository handoff

Updated 2026-10-09 using `binhlt0402`:
- Public repository: https://github.com/retro-trans/SRW-Z3-R
- First public release: https://github.com/retro-trans/SRW-Z3-R/releases/tag/v0.1.1
- Retro Trans compatibility: standard manifest v1 and one bare xdelta from the
  original NPJB00689 PKG to a new English PKG. Automatic and Apply xdelta are
  supported. Refresh the catalog before selecting Latest.
- Original recognition, Latest/Next/specific routes, actual public download
  and actual patch application passed through the live shared catalog.
  All six release assets were downloaded and verified. See
  docs/releases/0.1.1-public-download-validation.json for output identities.
- All 77 package files were verified. Native isolated RPCS3 installation
  produced all 77 expected files, including verified stage SDAT plaintext.
  Headless teardown exits with an assertion; this is not a clean process-exit
  or gameplay claim. See docs/releases/0.1.1.md for the full limits.
- The new PKG targets RPCS3 only and is not a signed console installer.
  Gameplay and PS3 hardware checks remain pending.

PS3 Rengoku-hen, NPJB00689. Release 0.1.1 uses build-018 translation
and layout content. The 0.1.1 source commit identifies current packaging tools
and unchanged English exports; the historical pre-Git build commit is unknown.
Read BASE_RULES.md, docs/LOCAL_SOURCE_DATA.md and docs/RELEASING.md.
English locales are publication exports without original script fields;
source-dependent checks/builds require matching private local inputs.
Preserve IDs, fingerprints, glossary references and runtime wrappers.
