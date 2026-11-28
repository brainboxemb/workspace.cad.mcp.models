# Agent guidance

## Purpose

This repository is a reusable template for local CAD MCP workspaces. It owns
workspace/bootstrap behavior only.

It does not own:

- Forge Python API behavior: `brainboxemb/lib.py.solidcraft.forge`;
- Forge CAD MCP behavior: `brainboxemb/tool.cad.mcp.forge`;
- vcs2l upstream behavior;
- CAD model source: the concrete CAD-library repository configured by a
  workspace created from this template;
- SolidCraft engine behavior.

## Start work

Before changing the template:

1. read the current `main:docs/plan.md` (not a potentially stale dev copy);
2. read `docs/developer-manual.md`;
3. read `docs/manual.md` when changing user-visible workflow;
4. keep `docs/plan.md` and `docs/handoff.md` structurally aligned with
   `brainboxemb/meta.cad.solidcraft/templates/docs/`;
5. create a short-lived branch from `dev` for normal source/docs work;
6. for stable control-doc-only work limited to `docs/plan.md` and/or
   `docs/handoff.md`, create the short-lived branch from `main` instead;
7. keep one logical change per issue/branch/PR;
8. run the workspace unit tests via `scripts/test.ps1` or the equivalent CI commands.
9. keep the developer and user manuals aligned with any workflow change; document reviewed consumer adoption separately.

## Branch model

Permanent branches are only `main` and `dev`.

- short-lived branch -> `dev`: squash;
- `dev` -> `main`: merge commit;
- stable control-doc-only branch -> `main`: squash, only when the complete PR
  changes `docs/plan.md` and/or `docs/handoff.md`;
- `main` -> `dev`: merge commit only for stable-only content not already on
  dev.

Every integration uses `/merge` and the repository-local merge-policy
workflow. Never select merge/squash/rebase manually and never use direct GitHub
merge as fallback.

Merged temporary branches are cleanup candidates. `main` and `dev` never
are.

## Workspace safety

MCP and Forge are external source dependencies. Their Git materialization is
owned by vcs2l through committed `dependencies.repos`; do not reimplement
clone/fetch/checkout/update logic for them in workspace Python.

The CAD repository is different: it is the user's active worktree. Workspace
bootstrap may clone it when absent and verify its origin when present, but must
not reset, force-checkout, clean, pull or otherwise rewrite an existing CAD
checkout.

The exact target model owner is explicit local configuration. Never implement
fuzzy model discovery or automatic target switching.

Generated VS Code project context should expose the selected model owner as the
normal folder. Do not expose the complete external toolchain or CAD catalog as
ordinary assistant browse context.

vcs2l externals stay below ignored `ext/`. The active CAD worktree stays below
ignored `.repos/cad/`. Generated client files stay below ignored
`.generated/`.

## Bootstrap behavior

Bootstrap uses one dedicated `cad-mcp-workspace` Conda environment. That
environment contains vcs2l plus the MCP/runtime dependencies. Do not introduce a
second environment or require environment switching for normal workspace use.

Do not expose Git clone/update behavior as an MCP model-work tool. Repository
management is an operator/workspace responsibility.
