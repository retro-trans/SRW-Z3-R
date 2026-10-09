# Preparing a public release

Follow the structure of [retro-trans/SRW-Z3](https://github.com/retro-trans/SRW-Z3),
using Rengoku-hen's independently verified **NPJB00689** inputs and executable.
The release stream starts at `0.1.0`, corresponding to local test build 018.
Use a new version for changed patch bytes and keep older assets available.

1. Verify a complete local build and its `verification/RESULT.json`. Record
   coverage, review flags and actual runtime testing separately.
2. Preview `tools/package_public_release.py` against that build, exact original
   extraction, xdelta3 and a new ignored output directory. Inspect all input
   and output hashes, then repeat with `--write`.
3. Decode every patch against its exact source and verify the complete output
   SHA-256 and byte size. Test the included installer on a new complete folder.
   Publish only the patch ZIP, BUILD-MANIFEST.json, VALIDATION.json and
   SHA256SUMS.txt; the ZIP's contents are deltas and support text/code.
4. Export reviewed public sources with `tools/publication_snapshot.py`:
   dry-run first, then `--write` into a new ignored directory. Audit the files
   and entire Git tree before committing or pushing. Keep original-text locale
   fields and source catalogs local as explained in `LOCAL_SOURCE_DATA.md`.
5. Fill `.github/RELEASE_TEMPLATE.md`, include the exact release filenames,
   coverage and limitations, and attach the files to a draft release. Check
   uploaded names, sizes and SHA-256 digests against local artifacts before
   publishing. Download the public assets and verify them afterwards.

This release uses a custom `srw-z3-r-file-patches-v1` manifest and extracted
directory inputs. It is not compatible with Retro Trans's whole-image
Automatic mode. Do not enroll it as a standard ISO route or invent ISO/PKG
identities. Adding that route requires a separately built and verified complete
image, a supported manifest and a full decode round trip.

Repository/source archives must contain no original script dump, complete game
files, images, licensed fonts, package/activation data or downloaded tools.
Prerelease notes should distinguish passing asset/format checks from gameplay
or real-console testing. Publication follows explicit user authorization.
