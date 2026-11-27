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
- MCP and Forge are exact externals declared in `dependencies.repos` and
  materialized with vcs2l under `ext/`;
- one dedicated `cad-mcp-workspace` Conda environment contains vcs2l and the
  Forge MCP/runtime dependencies;
- the CAD catalog is configured as
  `brainboxemb/2026-011-02.cad.solidcraft` with initial branch `dev`;
- the active CAD worktree is local at `.repos/cad/` and is never
  pull/reset/clean/switch managed once it exists;
- the active target is local in ignored `workspace.local.yml`;
- generated client configuration lives below ignored `.generated/`.

## Lane rule

Normal workspace-source work starts from `dev` on a short-lived branch.

- short-lived branch -> `dev`: squash through `/merge`;
- `dev` -> `main`: merge commit through `/merge`;
- `main` -> `dev`: merge commit only for stable-only content.

CAD model branches remain governed by the CAD repository, not this workspace.

## Engineering constraints

- reuse vcs2l for external repository materialization;
- keep MCP/Forge revisions exact and committed;
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
- next concrete gate: clone this workspace locally, create
  `workspace.local.yml`, run vcs2l/bootstrap + doctor, open the generated VS
  Code workspace and complete real MCP `environment` + `skill_list` calls;
- blocker/external work: requires the local SolidCraft CLI path.

## Open issue assignment

| Issue | Lane/owner | Status | Next action |
| --- | --- | --- | --- |
| #19 | workspace `dev` | now | Synchronize the lightweight initial CAD clone from the template |
| #1 | local Windows acceptance | after #19 | Perform vcs2l/bootstrap, doctor and real VS Code MCP calls |

## Recently completed

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

1. basic installation succeeds with no target selected;
2. create and verify one new Forge model;
3. convert one independently authored SolidCraft .sc checkpoint to Forge while
   preserving the original under `reference/`;
4. continue one existing Forge model from Git;
5. prove owner-local `build/` scratch never appears as maintained Git source.

After that, record any proven template friction upstream in
`brainboxemb/template.cad.mcp.workspace`.
