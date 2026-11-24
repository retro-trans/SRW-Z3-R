** Organize folder like this **
work - work folder
    output - contains the file for testing (iso, zip, etc...)
    glossary - contains the one or many json files for glossary
    ui - contains screenshot of actual UI element ingame with label on screenshot if possible, contains files (json,py,...) describe the coordinate, width and height, id and other attributes
    translation/<language code> - contains the target translation of ui element or dialogues or anything that need translation
docs - documents
tools - any tools help with translation
incoming - outside files that need agent to look into

** SOME RULES **
- Avoid contains extensive Japanese scripts (UI elements is fine)
- Identified each build with version 0.x.y (start at 0.1.0)
- Always write change log
- If user told you to remember anything write it down here, make sure to ask user if the new one conflict with old one
- Be conscious of subscription limit before creating sub-agents

** REMEMBER **
- Follow the editorial-pass workflow in `BASE_RULES.md` for translated scripts: accuracy review, editorial review for clarity and character voice, then final proofreading.
- Do not create or publish a GitHub release until the user explicitly requests a release for that build. Translation and local builds do not imply release permission.
- In the title screen put 'github.com/retro-trans' and current version in the bottom right corner

# Project instructions

Read `BASE_RULES.md` and `HANDOFF.md` before translation work.
Read `MEMORY.md` before building or packaging.

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
- Spirit names follow the sibling by Japanese identity: 直撃 is Break (Br),
  闘志 is Fury (Fu). Keep the unrelated 戦意高揚 pilot skill Fighting Sp.
  Preserve Rengoku effects/costs/durations. See `analysis/spirit_alignment.json`
  and the dry-run-first `tools/align_spirit_terms.py` audit.
- Every complete build must show its own incremented semantic version and
  `github.com/retro-trans` in the title screen's bottom-right corner, using
  Rengoku's own background resource. Keep footer, build manifest, package and
  release version consistent. Verify the packed footer before packaging.
  Dry runs and failed builds must not consume a version number.
- Drafting checks are not runtime validation. Rengoku's font, text bounds,
  executable offsets and insertion path must be verified independently.
  Do not transplant Z3 executable addresses or describe drafts as playable.
- Keep game data, package files, extracted scripts and local tools under
  ignored paths. Do not publish or upload them.
