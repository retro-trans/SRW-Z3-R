# Non-dialogue English draft — 2026-09-25

5295 English entries and 182 artwork/manual blocks are drafted. 8 catalog entries contain preserved engine keys; 509 entries have explicit exclusions listed in the coverage report. No translatable catalog entry is left empty.

This is translation source, not a playable patch. Story dialogue and battle speech are translated in separate catalogs; read [the battle draft](battle_lines_en.md) and [the project handoff](../HANDOFF.md). The sibling SRW Z3 glossary was the starting point; local research and explicit overrides are retained separately.

## Reading copies

| Category | English entries | Source occurrences | Longest English entry / line |
|---|---:|---:|---:|
| [Library](non_dialogue/library.md) | 201 | 526 | 1392 / 423 characters |
| [Gameplay](non_dialogue/gameplay.md) | 1169 | 1169 | 177 / 177 characters |
| [Scenario](non_dialogue/scenario.md) | 112 | 782 | 414 / 73 characters |
| [Interface](non_dialogue/interface.md) | 1627 | 2493 | 1392 / 410 characters |
| [Menu Resource](non_dialogue/menu_resource.md) | 1821 | 3412 | 751 / 125 characters |
| [Narration](non_dialogue/narration.md) | 32 | 32 | 66 / 66 characters |
| [Credits](non_dialogue/credits.md) | 304 | 334 | 54 / 54 characters |
| [Map Terrain](non_dialogue/map_terrain.md) | 19 | 419 | 16 / 16 characters |
| [Developer Comment](non_dialogue/developer_comment.md) | 10 | 10 | 95 / 95 characters |

Also read [the manual](manual_en.md) and [artwork labels](artwork_en.md).

## Review and coverage

9177 occurrence bindings were re-extracted and checked against local source assets. 63 guarded proof reports are indexed in `analysis/non_dialogue_review_index.json`. Meaning corrections preceded scripted terminology normalization. 97 entries retain review flags; see `analysis/non_dialogue_pending.json`.

The broad discovery pass examined 78 package assets and 26 non-code ELF sections. Its 6764 candidates are classified in `analysis/non_dialogue_coverage.json`; this is a byte-scan inventory, not a claim that every raster image was inspected.

The inherited glossary has 1,168 entries; the effective glossary now has 1320 entries. Rengoku names, title spellings and explicit alternatives are recorded in `analysis/rengoku_terms.json` and `localization/glossary_additions.json`.

## Remaining work

- Draft catalogs only: no translated strings or images have been inserted into a playable game.
- NUL-delimited CP932/UTF-8 scanning is heuristic. Short strings, pointer consumers and embedded binary text are not exhaustively proven.
- Manual, startup screens, chapter cards, inspected menu atlases and common battle UI have visual transcriptions. Remaining robot/weapon/effect/map textures have not all been visually inspected.
- A small ambiguous mark in AID atlas 1_2 at roughly (126,128)-(176,177) may be geometry rather than text; its runtime use remains unresolved.
- DATA01.EDAT is a 496-byte opaque asset; no readable text was established from it.
- Character/reading tables, Japanese font glyphs and internal metadata are excluded. Story dialogue and battle speech have separate English catalogs; earlier immutable extraction exclusions record the previous scope.
- Original field lengths are extraction bounds, not English screen budgets. Font coverage, variable expansion widths, line wrapping and relocation remain untested.
- The encrypted executable was read with the supplied local RAP. The ELF is a verified text-extraction reconstruction, not a rebuilt executable.

The 64-byte credit fields, 28-byte terrain names and indexed binary text spans are source-storage bounds only. Full English was retained. There is no verified maximum English character count or runtime screenshot measurement yet.

## Checks

Run `python -X utf8 tools/non_dialogue.py check`, `python -X utf8 tools/localization.py check`, `python -X utf8 tools/verify_source.py`, and `python -X utf8 -m unittest discover -s tests -v`. This report additionally re-extracts every catalog source binding and verifies artwork image hashes and screenshot cross-references.
