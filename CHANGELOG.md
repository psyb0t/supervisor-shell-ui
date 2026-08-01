# Changelog

All notable changes per release. Versions follow [semver](https://semver.org).

## v0.3.1 — 2026-08-01

Infrastructure and docs only. No changes to the application.

- Mirror the repo to Codeberg alongside GitLab on every branch and tag push,
  and archive it to the Wayback Machine, Software Heritage and archive.org.
  Pull requests are switched off on both mirrors — they are force-pushed from
  GitHub, so anything merged there is destroyed by the next sync; issues and
  forking stay on.
- Pull issues opened on either mirror back into GitHub every six hours, and
  close them here when the original closes. The scheduled run jitters to avoid
  hammering both mirrors at the same minute; a manual run does not.
- Split the mirroring, archiving and issue-pull jobs out of `pipeline.yml` into
  their own workflow files.
- Ignore `git-update.sh`, the per-release script that is written for each
  release and never committed.
- README: note the missing authenticated RPC support under a TODO section.
