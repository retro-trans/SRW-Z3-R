# Preparing a public release

Current releases use [Retro Trans's standard](https://github.com/retro-trans/retro-trans-tools/blob/main/docs/RELEASE_STANDARD.md)
manifest **v1** and bare whole-PKG xdeltas. **0.1.1 is the first public release.**
Never replace published patch bytes or reuse a published version.

1. Verify a complete local NPJB00689 build and `verification/RESULT.json`.
   Keep original packages and extracted files untouched. Record runtime and
   translation limits separately from binary validation.
2. Preview `tools/repack_runtime_pkg.py` with the original `--pkg`, verified
   `--build` and a NEW `--out` under `work/`, inspect the offsets, then repeat
   with `--write`. This preserves unchanged retail ciphertext for safe deltas.
   It clears invalid authentication and is for RPCS3, not console installation.
   Keep CFW debug PKGs local: re-encryption destroys source reuse and a
   whole-package xdelta would contain the complete game.
3. Preview `tools/verify_runtime_pkg_install.py`, then repeat with `--write`
   using a NEW isolated RPCS3 directory. Compare all 77 files, accounting for
   native SDAT decryption. Record teardown issues separately from file identity.
4. Publish reviewed sources and sanitized English exports first. Supply that
   full commit to `tools/package_retro_release.py` with package/install proofs.
   Preview identities, then use `--write` in a NEW release directory. For an
   upgrade supply `--previous` and its published `--previous-manifest`.
   A current `retro-trans-tools` checkout fully decodes/validates both patches.
5. Publish exactly one `BUILD-MANIFEST.json`, its bare `.xdelta` assets, `VALIDATION.json`
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

## Player-facing release format

Follow [SRW-Z3 release 0.6.25](https://github.com/retro-trans/SRW-Z3/releases/tag/v0.6.25)
and `.github/RELEASE_TEMPLATE.md`: title `VERSION — SUMMARY`, a brief game/edition
introduction, then Apply, What changed, PS3 and RPCS3 compatibility, What's
included, How it was translated, Acknowledgements, Source code and Contribute.
The first release uses What changed without a previous-version suffix.
Apply includes a source-to-patch table, manual command, input/output identities
and download size. Keep detailed binary evidence under `docs/validation/`.
Use verified Rengoku facts and credits; reference formatting does not transfer
Jigoku-hen ISO identities, upgrade routes or hardware support to this game.
