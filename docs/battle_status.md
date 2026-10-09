# Battle translation status

3575 unique battle lines (5113 stored occurrences) have English drafts. Story dialogue is excluded.

Read [the English battle lines](battle_lines_en.md). The canonical catalog is `localization/locales/en/battle_lines.json`; `analysis/battle_line_pending.json` records 54 review flags.

## Scope and extraction

The local SRVC contains 39 banks. Its offset table was discovered and structurally checked in Rengoku’s own decrypted executable at `0x952e80`; sibling executable offsets were not used. The catalog also includes RPW/executable retreat quotes. Intact unused battle lines and player-facing farewell lines in the battle banks remain included.

Thirty malformed, unreferenced pool remnants and two short ELF binary false positives are excluded. The immutable discovery catalog retains the two latter candidates for audit. All indexed pointers stay inside their bank and land at string starts.

## Review and terminology

Drafts and independent meaning proofs use 80-row slices plus neighboring context. Source/proposal hashes and exact previous-text guards bind corrections to the reviewed text. Meaning fixes precede scripted terminology normalization. See `analysis/battle_review_index.json`, `analysis/battle_terms.json` and `analysis/battle_terminology_applied.json`.

The inherited glossary remains unchanged. Local additions distinguish researched spellings, established project forms and provisional readings. Ambiguous omitted subjects, alien names, jokes and incantations retain explicit review notes. Original Japanese, quote wrappers, runtime tokens, literal backslash-n controls and actual retreat-quote newlines are preserved.

## Limits

This is translation source, not a playable patch. No insertion or runtime layout validation was performed. Voice-cue pairing and all speaker identities are not proven; numeric bank IDs alone are not identity evidence.

The longest expanded English line is 148 characters. This is a descriptive count, not a verified screen budget. Font coverage, glyph widths, line wrapping, relocation and pointer consumers still need runtime work; full meaning was not shortened to fit source bytes.

The broader image/opaque-asset limits remain in [the non-dialogue coverage report](non_dialogue_status.md).
