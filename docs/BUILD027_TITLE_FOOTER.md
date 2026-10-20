# Build027 — bottom-left version and Retro Trans credit

User request, 2026-10-20: place the version above `github.com/retro-trans` at
the bottom-left, using the supplied example's small outlined two-line treatment.
This supersedes the prior bottom-right placement for new builds.

The new footer is left-aligned in the 340x56px rectangle (28,640)–(368,696)
on Rengoku's own 1280x720 title background: 28px left / 24px bottom margin,
18px Rodin Latin Bold, white text with a dark outline and 4x supersampling.
The version is selected automatically; this build uses **v0.1.6**.

Insertion remains bound to NPJB00689 EFF member133, GTF0xecfe0, texture0.
No sibling background, executable offsets or animation data are transplanted.
The footer is composed from original pixels, so the previous right corner
does not retain a duplicate. Changes outside the footer rectangle, other
textures, native Z sprites and animation data are rejected by verification.

All eight footer/version checks pass. They include left alignment and clear
right-corner pixels, rejection of stale/missing versions and source drift,
preservation of title/Library resources, success-only version consumption,
and verification of actual build026's legacy right-corner packed footer.
Older build reports select their recorded rectangle; new builds default left.
Preview cropping follows the new corner in both the standalone helper and
the complete builder. The preview was visually inspected on the extracted
Rengoku background; this is not a running-game screenshot.

AGENTS.md, BASE_RULES.md, MEMORY.md and the release guide retain the new
placement and the requirement to update the version/credit on every complete
build. Existing builds and public v0.1.5 remain unchanged. Build027 also carries
the separately reviewed Crowe referent correction in STG00021:00060.

Complete build027/v0.1.6 passes packed-footer and archive/folder/overlay/ZIP
readbacks, all three native offline decryptions, 296 compiled condition
lookups and the exact corrected Crowe dialogue. The successful counter now
reads 0.1.6; next automatic version is 0.1.7.

Local RPCS3 test package:
`work/runtime_pkg_016/SRW-Z3-R-NPJB00689-English-build027-RPCS3.pkg`.
725,958,400 bytes; SHA256
`3983fc18a520ca852a00b1d037b2b5d5d8e59e6b8a52efbbcec8fc4aa81045dd`.
All 77 package-member and isolated installed file hashes match, including
native stage decryption. Installer teardown assertion 3221226505 is separate
from successful file checks. Instructions, package/install proof and checksum
files accompany the PKG. This is a local test build; public v0.1.5 stays intact.
Actual title-screen appearance, game boot and physical hardware remain untested.
