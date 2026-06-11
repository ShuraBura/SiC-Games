# Repo Migration Walkthrough — move SiC-Games off the Drive-synced path

**For:** Claude Code, to run **interactively with the supervisor** on the machine where the repo
lives. **Not** a script to execute unattended.
**Date:** 2026-06-09
**Stakes:** this is surgery on the project's single source of truth. The cost of a half-done
migration (two divergent copies, or deleting the wrong one) is worse than the current latent
risk. The current setup *works* because access has been serialized (one machine at a time). This
is **not urgent** — do it when there is focus for it, not in passing.

## Why

The repo is inside a Google-Drive-synced folder. Git rewrites many small files inside `.git`
rapidly during commits/merges; Drive tries to sync each change; the two race. Failure modes:
corrupted `.git` index, and Drive conflict-copies (`ROADMAP (1).md` beside `ROADMAP.md`) — the
exact duplication disease already cured once. Git's GitHub remote is already the proper cross-
machine sync, which makes Drive redundant for the repo itself.

**Target end state:** working repo in a normal, non-synced local path on each machine; GitHub
remote as the only sync mechanism; Drive (if kept at all) used only as a separate flat-file
export mirror, never a live clone of the working tree.

## Principles for CC during the walkthrough

- **Read state, do not assume it.** Inspect actual git status, branch, remote, and ahead/behind
  counts before proposing any command. Fill in real commands from what you observe; do not run
  commands written from memory of a generic setup.
- **Confirm before every irreversible step.** Deleting or moving the Drive copy is irreversible-
  ish; get explicit supervisor confirmation, stating exactly what will be removed and from where.
- **Never delete the Drive copy until the non-synced clone is verified working AND the remote is
  confirmed to hold everything.** Order matters.
- **One machine at a time.** Do not migrate both machines in parallel.
- **Pause Drive sync during the operation if possible** (the supervisor can quit/pause the Drive
  client) so nothing syncs mid-move.

## Checklist (each step: inspect → propose real command → confirm → execute → verify)

### Phase A — establish that GitHub is the true source of truth
1. Identify the current repo path and confirm it is inside the Drive-synced folder.
2. Inspect working state: uncommitted changes, untracked files, current branch.
3. **Resolve all uncommitted work** — commit or stash, supervisor's call per file. The ROADMAP
   and any CC-maintained local docs are the priority (memory notes flag ROADMAP as local-drive-
   maintained; make sure its latest state is committed).
4. Confirm the remote is configured and reachable; push so the remote is current.
5. Verify ahead/behind: the local branch should be **0 ahead** of the remote after the push
   (i.e. the remote has everything). Do not proceed until this is true.
6. Check for any Drive conflict-copies already present (files like `* (1).md`, `*conflicted*`).
   If found, this is a pre-existing divergence — surface it, reconcile with the supervisor, and
   re-push before continuing. This is the single most important check.

### Phase B — create the non-synced working clone
7. Choose a non-synced local path with the supervisor (e.g. a `projects/` or `dev/` directory
   that Drive does not sync). Confirm Drive is not watching that path.
8. Clone fresh from the GitHub remote into the new path. (Fresh clone, not a copy of the Drive
   working tree — a fresh clone guarantees a clean `.git`.)
9. Verify the new clone: branch matches, `git status` clean, file tree matches expectation, a
   spot-check of key docs (INDEX, ROADMAP, PARAMETERS, concept map, HYPOTHESES) shows current
   content.
10. Run whatever the project's "is it alive" check is (test suite / a trivial model import) from
    the new clone to confirm it is a working repo, not just files.

### Phase C — decommission the Drive copy (only after B verifies)
11. Confirm once more that the remote holds everything and the new clone works.
12. Decide with the supervisor what happens to the old Drive folder:
    - simplest: delete the working repo from Drive entirely (GitHub + the new clone hold all).
    - or: keep a Drive folder as a *flat-file export mirror* — but it must NOT contain a `.git`
      or be a clone; it holds only deliberately-copied exports (docs snapshots, the terrain
      prototype, PDFs). If keeping it, make it a clearly-separate directory, not the old repo.
13. Execute the chosen decommission with explicit confirmation, stating the exact path being
    removed/repurposed.

### Phase D — second machine
14. Repeat Phases A–C on the other machine when next on it, **after** confirming that machine has
    no unpushed local work (it was idle as of this session, but re-verify). Clone fresh into a
    non-synced path there too; decommission its Drive copy.

### Phase E — going forward
15. Update any project notes / CLAUDE.md / INDEX that reference the repo path so they point to the
    non-synced location.
16. Standing discipline from here: pull before a session, push after; git is the sync; Drive is
    never again the live working tree.

## Stop conditions (halt and consult the supervisor)
- Any Drive conflict-copy or already-divergent state discovered in Phase A.
- Remote not reachable or ahead/behind shows the remote is missing commits.
- The new clone fails its alive-check.
- Any uncertainty about whether a path is Drive-synced.

In all of these, the safe action is to **stop and keep the existing (working, serialized) setup**
rather than risk the canon.
