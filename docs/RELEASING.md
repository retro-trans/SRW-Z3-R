# Preparing a public release

Current releases use [Retro Trans's standard](https://github.com/retro-trans/retro-trans-tools/blob/main/docs/RELEASE_STANDARD.md)
manifest **v1** and a bare whole-PKG xdelta. The 0.1.0 custom folder installer
remains historical; never replace its published patch bytes or reuse its version.

1. Verify a complete local NPJB00689 build and `verification/RESULT.json`.
   Keep original packages and extracted files untouched. Record runtime and
   translation limits separately from binary validation.
2. Preview `tools/repack_runtime_pkg.py` with `--pkg`, `--build` and a NEW
   `--out` directory under `work/`. Inspect the exact changed paths/offsets,
   then repeat with `--write`. This builds a local RPCS3-only modified package,
   clears invalid authentication, and compares all 77 members with the build.
   Never upload the complete PKG. This is not a signed console installer.
3. Verify installation with an isolated RPCS3 copy, preserving the user's
   installation. Compare every installed member; the stage SDAT is natively
   decrypted and must match the independently verified plaintext stage.
   Record process exit/shutdown issues independently from file identity checks.
4. Publish reviewed packaging/tool sources and unchanged English exports first.
   Supply their full Git commit to `tools/package_retro_release.py` together
   with the original/target PKGs, package validation and RPCS3 validation files.
   Preview, inspect hashes, then repeat with `--write` in a NEW output directory.
   The helper uses a current `retro-trans-tools` checkout via `--retro-tools`,
   or an installed package, to encode, fully decode and validate the release.
5. Publish exactly one `BUILD-MANIFEST.json`, its bare `.xdelta`, `VALIDATION.json`
   and `SHA256SUMS.txt`. Additional installation notes or detailed runtime
   evidence may be separate assets. No game binaries or local configurations.
6. Test Retro Trans recognition, route selection and actual output against the
   expected full-package SHA-256. Download the public release and validate it
   with `python -m retro_trans.release validate <download-directory>`.
7. Publish a regular numeric version so Retro Trans's catalog discovers it;
   its catalog intentionally skips GitHub prereleases. Clearly label test
   translation content and pending gameplay/hardware checks in the notes.
   Dispatch the tool repository's scoped **Refresh patch catalog** workflow
   with `repository=retro-trans/SRW-Z3-R`, then verify the published catalog
   recognizes the original and selects the intended route.

`source_commit` identifies the published translation/packaging snapshot.
Build 018 predates Git: do not present this newer packaging commit as its
historical build commit. Record the original build report hash and provenance
in separate detailed validation. Preserve old releases and tag identities.

Use `.github/RELEASE_TEMPLATE.md`. Source-dependent checks/builds require the
private inputs described in `LOCAL_SOURCE_DATA.md`. No original script dumps,
game files, licenses, fonts or downloaded executable tools belong in Git.
