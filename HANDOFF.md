# Public repository handoff

Updated 2026-10-10 using binhlt0402. Public repo: retro-trans/SRW-Z3-R.
Latest release **0.1.2** contains local build022, with Z3 release section order.
First public release **0.1.1** remains unchanged.

- Public output is RPCS3-only, with cleared authentication. CFW debug PKGs
  remain private because a whole-debug-PKG xdelta embeds the complete game.
  Local CFW build helpers require private inputs; PS3 boot is unverified.
- Standard manifest v1, bare xdelta routes from original Japanese NPJB00689
  and exact English 0.1.1 PKG. Retro Trans 0.5.1+, DeltaPatcher and xdelta3 supported.
- All 8 public assets and both actual live catalog/apply routes pass full
  identity checks. Scoped Refresh patch catalog run 38028076086 succeeded.
- Tag d46357eb802a8cb12b61372947eed608674de9c5; source snapshot
  3df241c3864ae7c10885f106b052315530cb9e66. Preserve published assets/tags.
- All 77 native RPCS3 installed file hashes match. Known headless teardown
  assertion is not a clean shutdown/boot result; gameplay remains pending.
- Public locales omit original source text. Source-dependent checks/builds
  require matching private inputs. Keep game data, licenses and tools ignored.

Read BASE_RULES.md, docs/LOCAL_SOURCE_DATA.md, docs/RELEASING.md,
docs/releases/0.1.2.md and docs/validation/0.1.2.md.
Preserve IDs, fingerprints, glossary references and runtime wrappers.
