# workspace.cad.mcp.models plan

This file is the current source of truth for unfinished work in
`brainboxemb/workspace.cad.mcp.models`.

This repository is the concrete local assistant workspace for
`brainboxemb/2026-011-02.cad.solidcraft`. It owns workspace configuration and
local bootstrap/client generation only; model implementation remains in the CAD
catalog repository.

## Current accepted baseline

- permanent source lanes are `main` and `dev`;
- normal source integration uses the repository-local `/merge` policy;
- MCP and Forge are exact released externals declared in `dependencies.repos`
  and materialized with vcs2l under `ext/`;
- the accepted toolchain pins are Forge CAD MCP `v0.0.5` and Forge
  `v0.25.0`, with SolidCraft 0.50.0 / CAD runtime v0.3.8 live GUI control plus
  headless evidence;
- one dedicated `cad-mcp-workspace` Conda environment contains vcs2l and the
  Forge MCP/runtime dependencies;
- the CAD catalog is configured as
  `brainboxemb/2026-011-02.cad.solidcraft` with initial branch `dev`;
- the active CAD worktree is local at `.repos/cad/` and is never
  pull/reset/clean/switch managed once it exists;
- the active target is local in ignored `workspace.local.yml` and may be
  either a maintained catalog owner or an ignored standalone workbench;
- generated client configuration lives below ignored `.generated/`;
- bootstrap/update reconcile clean vcs2l-managed MCP/Forge externals to the
  committed release tags automatically and never touch the CAD worktree.

## Lane rule

Normal workspace-source work starts from `dev` on a short-lived branch.

- short-lived branch -> `dev`: squash through `/merge`;
- `dev` -> `main`: merge commit through `/merge`;
- `main` -> `dev`: merge commit only for stable-only content.

CAD model branches remain governed by the CAD repository, not this workspace.

## Engineering constraints

- reuse vcs2l for external repository materialization;
- keep MCP/Forge release tags exact and committed;
- materialize MCP/Forge release externals as shallow exact-tag checkouts; full
  Git history is not part of the local workspace toolchain;
- keep the active CAD worktree independent from external dependency state;
- keep model target selection explicit/local;
- keep normal VS Code context limited to the exact target owner;
- do not move reusable workspace implementation from
  `template.cad.mcp.workspace` into consumer-only copies unless a local
  override is intentionally required.

## Active workstreams

### WS1 — first local Windows acceptance

State:

- owner/lane: local Windows consumer + workspace `dev`;
- current status: source configuration is aligned with the current
  template/vcs2l baseline and permanent `dev` CI is green; local Windows
  acceptance remains;
- next concrete gate: pull this workspace on Windows, update to MCP v0.0.5,
  create `mcp-test` without a CAD checkout, run doctor and complete the
  documented 60 × 20 × 4 mm / Ø8 live SolidCraft demo;
- blocker/external work: the real Windows GUI acceptance still has to be run.

## Open issue assignment

| Issue | Lane/owner | Status | Next action |
| --- | --- | --- | --- |
| #50 | workspace `dev` | now | Adopt released MCP v0.0.5 fast-status patch for Windows Codex acceptance |
| #47 | workspace `dev` | complete | Project-local Codex MCP config published to stable main |
| #44 | workspace `dev` | complete | Shallow exact-tag MCP/Forge externals published and proven on Windows |
| #41 | workspace `dev` | complete | MCP v0.0.4 / SolidCraft 0.50.0 baseline published to stable main |
| #1 | local Windows acceptance | next | Run the 60 × 20 × 4 mm / Ø8 live workbench demo on Windows |

## Recently completed

- #47 synchronizes project-local `.codex/config.toml` generation for standalone
  workbenches so Codex IDE can discover `forgeCad` without a global Codex CLI.
- #44 replaced full-history MCP/Forge externals with shallow exact-tag
  checkouts; the concrete Windows Forge external dropped from about 192 MB to
  about 8 MB.
- #41 adopts Forge CAD MCP v0.0.4 with Forge/SCPF v0.25.0 and SolidCraft
  0.50.0 / CAD runtime v0.3.8.
- #38 synchronizes the standalone workbench, local `project.yml`, MCP
  `v0.0.3` live SolidCraft control and no-CAD-checkout bootstrap from the
  stable workspace template.
- #35 fixes the Windows external-rematerialization hang by passing
  `dependencies.repos` to `vcs delete` as a file with `--input` instead
  of through a PowerShell stdin pipe.
- #32 fixes the first real Windows update regression: generated Python package
  metadata below pinned externals no longer looks like user source, while
  tracked edits and untracked real content still fail safely.
- #29 synchronizes automatic MCP/Forge external reconciliation from the
  workspace template, so normal upgrades use `git pull` +
  `scripts/update.ps1` without manual `ext/` deletion.
- #24 adopts the released MCP `v0.0.2` + Forge `v0.25.0` compatibility
  baseline from the workspace template, replacing opaque commit-SHA pins.
- #21 synchronized the template PR helper. `scripts/pr.ps1` can publish either
  the workspace repository or `.repos/cad`, wait for PR checks and request the
  existing repository-policy merge with `/merge`.
- #19 synchronized the lightweight initial CAD checkout: only the configured
  development branch is cloned and historical blobs are fetched lazily.
- #12 synchronized the target-optional installation, new-model owner creation,
  immutable SolidCraft reference import and ordered model workflows from the
  workspace template.
- #8 synchronized the accepted procedural daily manual and rewrote the concrete
  workspace developer manual as an ordered maintenance procedure. Setup now
  states exactly when `bootstrap.ps1` creates/updates
  `cad-mcp-workspace` and what happens next.
- #5 adopts the template's single Conda environment model: vcs2l and the Forge
  MCP/runtime both run in `cad-mcp-workspace`; no environment switching is
  part of the normal workflow.
- Workspace source is synchronized with the accepted template/vcs2l baseline,
  configured for `brainboxemb/2026-011-02.cad.solidcraft`, and green on
  permanent `dev` CI.

## Next release/checkpoint

The first acceptance checkpoint is now an ordered workflow test:

1. basic installation succeeds with no target and without a CAD checkout;
2. create the ignored `mcp-test` workbench and local `project.yml`;
3. create a 60 × 20 × 4 mm plate with one centered Ø8 mm hole through Forge;
4. apply it to the running SolidCraft GUI, inspect it, change one exposed
   parameter natively, set a useful view and retrieve a live render;
5. confirm `build/session.jsonl`, replay evidence and the render stay inside
   the workbench;
6. only after that continue with catalog-model, conversion and existing-model
   acceptance.

After that, record any proven template friction upstream in
`brainboxemb/template.cad.mcp.workspace`.
