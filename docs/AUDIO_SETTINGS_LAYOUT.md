# Audio and BGM menu overlap correction

The two screenshots reported on 2026-11-22 show overlapping system-settings
labels and BGM button hints. This is a layout correction for Rengoku-hen
NPJB00689. Original scripts, translation identities and gameplay values are
unchanged; full English catalog wording remains available as source.

The audio menu is a multiline label with independently drawn Play text,
triangle button, sliders and ON/OFF options. Four audio variants now use
`Voice` and a separate `: Play` hint. `Remember Sort / Info` fits before the
option bracket in both affected audio variants; the map-settings counterpart
already uses that caption. Two Maximum Break/BGM split rows use `Max. Break`
to leave room for the adjacent BGM caption.

Each of three BGM headers was stored as four separate title pieces plus a
colon and subheading. They now draw `BGM Setup` once, with `Target` or
`Replace` beside it. Six music Confirm hints use `OK` to fit the narrow native
button gaps. The system-config Change hint uses `Chg.` before the Done icon.
Font presets, coordinates, button sprites, tint, multiline pitch, slider
values and option brackets retain their native metadata.

At native 1280x720, labels begin at x191.5 and option brackets at x599.5.
The shortened remembered-sort label measures 322.875px, leaving 85.125px
before the bracket. BGM Setup measures 169.53125px at its native 31px quad,
leaving 29.46875px before the x223.5 subheading. The narrowest music control
gap leaves 48px after reserving a 32px icon and 8px gap: OK is 44.625px,
where Confirm would need 96.46875px. Measurements use Rengoku's Rodin glyph
advances and its own FSSA records, not sibling executable addresses.

Mechanical layout audit scanned three 80-record FSSA slices beginning at
0x8c424, 0x93e24 and 0x94c24, plus two neighboring records on each side
(240 in-slice + 12 context = 252). The adapter checks 36 caption records.
This was not a meaning review of the unrelated dialogue/debug rows in those
slices. No name or glossary decisions were needed. Unresolved: appearance
in a running game, including transition/inactive states, needs confirmation.
The wider Quick Commands line includes inline controller slots and retains
its existing composition; this change only checks its remembered-sort row.

Five focused regression tests pass: reported overlaps, all affected audio
states, BGM title/subheading bounds, button gaps, unchanged metadata and
rejection of source/style drift. Four existing roster/settings checks also
pass. Complete local build029/v0.9.1 passes all 36 packed-caption readbacks,
296 compiled operation-condition lookups, archive/folder/overlay/ZIP checks,
matching bottom-left version/credit and all three native offline decryptions.

The local RPCS3 package and isolated installation match all 77 expected files.
Package: `work/runtime_pkg_091/SRW-Z3-R-NPJB00689-English-build029-RPCS3.pkg`.
Size: 725,959,632 bytes; SHA256
`ac525e8355edbee47cbe9ac3cab58514738eb24b01777fd4d7644e130601d849`.
Package proof: `work/runtime_pkg_091/PKG-VALIDATION.json`; native installation
proof: `work/rpcs3_pkg_091/INSTALL-VALIDATION.json`. The known installer
teardown assertion 3221226505 is separate from successful file validation
and is not a game boot result. The three offline decryptions exit 0.

Compared with build028/v0.9.0, 74 game files are byte-identical. The menu and
title/footer archives change; the freshly encrypted stage wrapper differs
but its native-decrypted payload is byte-identical (SHA256
`67098423c91be68ef4c0c0709abae9069894f0ccbdda70e6e6a3eda0b90e94e4`).
Canonical catalogs and original inputs remain unchanged. The next complete
build is 0.9.2. Public v0.9.0 is unchanged; v0.9.1 is local only. Appearance
in a running game and physical PS3 compatibility remain unverified.
