# workspace.cad.mcp.models handoff

Repository: `brainboxemb/workspace.cad.mcp.models`.

This document is the easy-to-find handoff entrypoint for a new work session.
It contains one copyable handoff message below.

The handoff is an entrypoint, not a second plan. Current work must always be
derived from live GitHub state and `docs/plan.md`.

Shared SolidCraft/CAD documentation conventions live in
`brainboxemb/meta.cad.solidcraft`.

## Handoff message

Copy the complete text block below into a new chat.

~~~text
You are continuing work on brainboxemb/workspace.cad.mcp.models.

Repository role:

- this is the concrete local Forge CAD MCP assistant workspace for
  brainboxemb/2026-011-02.cad.solidcraft;
- it owns workspace configuration, local bootstrap and generated VS Code/Copilot
  client configuration only;
- MCP and Forge source are exact externals from dependencies.repos, materialized
  with vcs2l; the CAD catalog is a separate active worktree;
- reusable workspace behavior belongs in brainboxemb/template.cad.mcp.workspace,
  Forge behavior in brainboxemb/lib.py.solidcraft.forge, MCP behavior in
  brainboxemb/tool.cad.mcp.forge, and CAD model source in
  brainboxemb/2026-011-02.cad.solidcraft.

Use this handoff only as the entrypoint. Do not treat copied handoff text as
fresher than GitHub or docs/plan.md.

Start by:

1. inspecting current issues, pull requests and branches;
2. reading AGENTS.md;
3. reading docs/plan.md;
4. treating docs/plan.md as the source of truth for unfinished work;
5. following the current work order from the plan rather than old handoff text;
6. creating an issue before implementation when a logical change has none;
7. keeping one logical change to one issue, branch and PR;
8. updating manuals when workspace behavior changes;
9. updating the plan after merge/checkpoint.

Durable working rules:

- MCP/Forge dependency revisions live only in dependencies.repos and are
  materialized with vcs2l below ext/ from the same cad-mcp-workspace Conda
  environment that runs the MCP;
- .repos/cad is the user's active CAD worktree and must not be reset, cleaned,
  pulled or branch-switched by workspace maintenance once it exists;
- the active model owner is explicit local configuration in
  workspace.local.yml;
- generated VS Code context exposes the selected target owner, not the complete
  toolchain/catalog checkout set;
- permanent source branches are main and dev; all normal integrations use the
  repository-local /merge policy.

Shared document structures live in brainboxemb/meta.cad.solidcraft:
templates/docs/plan.md and templates/docs/handoff.md.

Do not copy current SHAs, dependency pins, active issue/PR state or temporary
next-action lists into this handoff. Those facts belong in GitHub and
docs/plan.md.
~~~

## Template guidance

The text block above is the actual handoff message. Keep durable role/boundary
guidance here and current status in `docs/plan.md`.
