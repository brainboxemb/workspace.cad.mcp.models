# Agent guidance

## Purpose

This repository is a reusable template for local CAD MCP workspaces. It owns
workspace/bootstrap behavior only.

It does not own:

- Forge Python API behavior: `brainboxemb/lib.py.solidcraft.forge`;
- Forge CAD MCP behavior: `brainboxemb/tool.cad.mcp.forge`;
- CAD model source: the concrete CAD-library repository configured by a
  workspace created from this template;
- SolidCraft engine behavior.

## Start work

Before changing the template:

1. read `docs/plan.md`;
2. read `docs/developer-manual.md`;
3. read `docs/manual.md` when changing user-visible workflow;
4. create a short-lived branch from `dev`;
5. keep one logical change per issue/branch/PR;
6. run the workspace unit tests.

## Branch model

Permanent branches are only `main` and `dev`.

- short-lived branch -> `dev`: squash;
- `dev` -> `main`: merge commit;
- `main` -> `dev`: merge commit only for stable-only content not already on
  dev.

Every integration uses `/merge` and the repository-local merge-policy
workflow. Never select merge/squash/rebase manually and never use direct GitHub
merge as fallback.

Merged temporary branches are cleanup candidates. `main` and `dev` never
are.

## Workspace safety

The template may manage MCP and exact Forge toolchain checkouts. It must not
reset, force-checkout, clean or otherwise rewrite an existing CAD checkout.
After initial clone, the CAD repository is the user's real worktree.

The exact target model owner is explicit local configuration. Never implement
fuzzy model discovery or automatic target switching.

Generated VS Code project context should expose the selected model owner as the
normal folder. Do not expose the entire managed Forge/MCP/CAD checkout set as
ordinary assistant browse context.

Nested repositories and generated files stay below ignored `.repos/` and
`.generated/`.

## Bootstrap behavior

Bootstrap must be idempotent and fail closed on unexpected modifications in
managed MCP/Forge toolchain checkouts. It may clone the configured CAD
repository when absent, but must leave an existing CAD checkout's branch and
working tree untouched.

Do not expose Git clone/update behavior as an MCP model-work tool. Repository
management is an operator/workspace responsibility.
