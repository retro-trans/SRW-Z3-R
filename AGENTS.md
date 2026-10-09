# Project instructions

Read `BASE_RULES.md` and `HANDOFF.md` before translation work.

- This is PS3 Rengoku-hen, NPJB00689. The sibling `../SRW Z3` is a
  read-only glossary/tooling reference, not this game's build target.
- Canonical story English is `localization/locales/en/STG*.json`.
  `docs/opening_draft.md` is a generated reading copy; do not edit it as source.
- The imported glossary English is `localization/locales/en/glossary.json`;
  its inherited research/identity snapshot is `analysis/glossary.json`.
  Add researched Rengoku terms and explicit spelling overrides in
  `localization/glossary_additions.json`. Resolve with `tools/localization.py`.
- Use glossary references `$$Japanese$$` in dialogue, including speakers.
  Preserve source IDs, source fingerprints, runtime substitutions, keyword
  link order and internal-monologue/speech wrappers.
- Work in 80-record slices, with adjacent context and a report of records
  examined, unresolved choices and terminology decisions.
- Scripts that mutate project data default to dry-run. Inspect their concrete
  output before repeating with `--write`. Never overwrite original package
  data or an existing extracted source tree.
- Run focused validation after changes. Record progress and remaining work
  in `CHANGELOG.md` and `HANDOFF.md`.
- Drafting checks are not runtime validation. Rengoku's font, text bounds,
  executable offsets and insertion path must be verified independently.
  Do not transplant Z3 executable addresses or describe drafts as playable.
- Keep game data, package files, extracted scripts and local tools under
  ignored paths. Do not publish or upload them.
