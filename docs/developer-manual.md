# Developer manual

This repository is a concrete consumer of
`brainboxemb/template.cad.mcp.workspace`.

## Ownership

This repository owns only configuration specific to the models workspace:

- which CAD catalog is used;
- exact MCP/Forge external revisions inherited/accepted from the template;
- local bootstrap/client-generation entrypoints;
- workspace-specific acceptance status.

Reusable workspace behavior should be fixed in
`brainboxemb/template.cad.mcp.workspace` first and then synchronized here.

## External dependencies

`dependencies.repos` declares MCP and Forge. The shared vcs2l installation is
provided by `brainboxemb/tool.py-dev-env`.

```text
dependencies.repos
    -> vcs import --input dependencies.repos ext
    -> ext/mcp
    -> ext/forge
```

Do not replace this with custom clone/fetch/checkout code.

## Active CAD worktree

`workspace.yml` configures:

```yaml
repositories:
  cad:
    url: https://github.com/brainboxemb/2026-011-02.cad.solidcraft.git
    branch: dev
```

First bootstrap may clone that repository into `.repos/cad`. Once it exists,
workspace tooling verifies the origin only. It must not update/switch/reset the
worktree because normal CAD work happens there.

## Local target

Create ignored `workspace.local.yml` from the example and select one exact
owner:

```yaml
schema: 1

target:
  model: models/assemblies/simple_mft_assembly

solidcraft:
  cli: C:\\path\\to\\solidcraft-cli.exe
```

Changing target is a local session operation and is not committed.

## Template synchronization

When reusable behavior changes upstream:

1. inspect the accepted template `main`;
2. update shared scripts/tests/workflows/manual text in one workspace issue/PR;
3. preserve consumer-specific `README.md`, `workspace.yml`,
   `docs/handoff.md`, `docs/plan.md`, `docs/developer-manual.md` and
   `AGENTS.md`;
4. run workspace CI;
5. use `/merge`;
6. perform the local acceptance affected by the change.

Do not silently advance MCP/Forge revisions while synchronizing unrelated
template changes.

## First local acceptance

From a clean clone:

```powershell
Copy-Item workspace.local.example.yml workspace.local.yml
# edit target.model and solidcraft.cli
.\scripts\bootstrap.ps1
.\scripts\doctor.ps1
```

Then open `.generated/forge-cad.code-workspace`, configure the Copilot MCP
server from `.generated/mcp-config.json` and prove real `environment` and
`skill_list` calls.
