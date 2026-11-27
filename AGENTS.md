# Agent guidance

## Purpose

This repository is the concrete Forge CAD MCP assistant workspace for
`brainboxemb/2026-011-02.cad.solidcraft`.

It owns only workspace configuration and local bootstrap/client-generation
mechanics.

It does not own:

- Forge Python API behavior: `brainboxemb/lib.py.solidcraft.forge`;
- Forge CAD MCP behavior: `brainboxemb/tool.cad.mcp.forge`;
- vcs2l/shared developer tooling: `brainboxemb/tool.py-dev-env`;
- CAD model source: `brainboxemb/2026-011-02.cad.solidcraft`;
- reusable workspace architecture:
  `brainboxemb/template.cad.mcp.workspace`;
- SolidCraft engine behavior.

## Start work

1. inspect current issues, pull requests and branches;
2. read `docs/plan.md`;
3. read `docs/developer-manual.md`;
4. read `docs/manual.md` for user-visible workflow;
5. keep handoff/plan structure aligned with
   `brainboxemb/meta.cad.solidcraft/templates/docs/`;
6. create a short-lived branch from `dev`;
7. keep one logical change per issue/branch/PR;
8. use `/merge` for every integration.

## Dependency boundary

MCP and Forge are externals declared only in `dependencies.repos` and
materialized by vcs2l below `ext/`. Do not reimplement Git dependency
management in this repository.

The CAD checkout below `.repos/cad/` is the active worktree. Bootstrap may
clone it when absent and verify origin when present, but must never pull,
reset, clean or switch an existing CAD checkout.

The exact target model owner is local configuration in
`workspace.local.yml`. Never add fuzzy target discovery or implicit target
switching.

## Branch model

Permanent branches are `main` and `dev`.

- short-lived branch -> `dev`: squash through `/merge`;
- `dev` -> `main`: merge commit through `/merge`;
- `main` -> `dev`: merge commit only for stable-only content not already on
  dev.

Model-development Git work belongs in the CAD repository, not this workspace
repository.
