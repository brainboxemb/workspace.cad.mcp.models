# Workspace template plan

This file contains unfinished work only.

## Now

### #1 — bootstrap the reusable workspace template

Establish the first complete workspace contract:

- explicit MCP, Forge and CAD repository configuration;
- exact Forge/SCPF and SolidCraft compatibility pins matching the current MCP
  stable baseline;
- Conda bootstrap;
- local target selection;
- generated VS Code/Copilot MCP configuration;
- doctor/update/select commands;
- user and developer manuals;
- repository CI, merge policy and branch cleanup.

The initial empty-repository bootstrap is the only direct `main` commit
exception because no merge-policy workflow existed yet.

## Next

Create the first concrete repository from this template:
`workspace.cad.mcp.models`. Configure it for
`brainboxemb/2026-011-02.cad.solidcraft`, select one real model owner, run
bootstrap + doctor and use the generated VS Code workspace for the first
end-to-end assistant session.

After that real use, feed only proven setup friction back into this template.
