# Developer manual

This document explains how to create and maintain a concrete CAD assistant
workspace from `template.cad.mcp.workspace`.

## Repository roles

```text
template.cad.mcp.workspace
        |
        | GitHub template
        v
workspace.cad.mcp.models
        |
        +-- local .repos/mcp    -> tool.cad.mcp.forge
        +-- local .repos/forge  -> lib.py.solidcraft.forge
        +-- local .repos/cad    -> concrete CAD library
        |
        +-- local target owner  -> one models/... owner
```

The concrete workspace repository owns only environment configuration. CAD
source remains in the CAD repository.

## Create workspace.cad.mcp.models

1. Mark `template.cad.mcp.workspace` as a GitHub template repository if that
   repository setting is not enabled yet.
2. Choose **Use this template** and create:
   `brainboxemb/workspace.cad.mcp.models`.
3. Clone the new workspace repository.
4. Edit committed `workspace.yml`:

```yaml
workspace:
  id: models

repositories:
  cad:
    url: https://github.com/brainboxemb/2026-011-02.cad.solidcraft.git
    branch: dev
```

Do not replace the Forge pin merely because a newer release exists. The
template's Forge/SolidCraft values must match the MCP baseline it has accepted.

5. Create local configuration:

```powershell
Copy-Item workspace.local.example.yml workspace.local.yml
```

Set one exact target owner and the SolidCraft CLI:

```yaml
schema: 1

target:
  model: models/assemblies/simple_mft_assembly

solidcraft:
  cli: C:\\path\\to\\solidcraft-cli.exe
```

6. Run:

```powershell
.\scripts\bootstrap.ps1
.\scripts\doctor.ps1
```

7. Open `.generated/forge-cad.code-workspace`.
8. Configure the VS Code Copilot harness from
   `.generated/mcp-config.json`.
9. Perform an actual MCP `environment` call before model work.

## Why child checkouts are ignored

`.repos/` contains real Git repositories. They are local dependencies, not
content owned by the workspace repository. Committing them as submodules would
make CAD worktree state part of workspace source control and would couple model
branching to workspace revisions. That is intentionally avoided.

The workspace configuration pins the toolchain; bootstrap materializes it.

## Why the target is local

`workspace.yml` says which CAD library belongs to this assistant environment.
`workspace.local.yml` says which exact model you are working on now.

That prevents a commit every time you move from one model to another and avoids
teaching the AI to search the catalog for a likely target.

## Why VS Code opens only the target owner

The child checkouts necessarily exist on disk, but the normal assistant project
context should not be all of `.repos/mcp`, `.repos/forge` and
`.repos/cad`.

That would let a client agent browse or edit outside the MCP boundary using
ordinary editor/file tools.

The generated `.code-workspace` therefore exposes the selected
`models/.../<owner>` directory as its normal folder. Forge/MCP and catalog
dependencies remain reachable through their intended MCP interfaces.

This is a workflow boundary, not a filesystem sandbox. A sufficiently
privileged editor agent can still access local files if the client grants it
such permission. The MCP itself nevertheless keeps one exact writable owner and
read-only exact dependency access.

## Bootstrap contract

`scripts/bootstrap.ps1` creates/updates the Conda environment then runs the
Python workspace manager.

Managed toolchain behavior:

- MCP: clone when absent; later require a clean tracked tree and check out the
  exact configured commit detached;
- Forge: clone/fetch and check out the exact configured commit detached; fail on
  tracked modifications;
- CAD: clone the configured starting branch only when absent; if present,
  verify it is the configured repository and leave branch/worktree untouched;
- install MCP editable and SCPF from the exact Forge checkout;
- generate target-specific client files when local target configuration exists.

No repository-management MCP tool is added. Repository management remains an
operator/workspace concern.

## Update contract

`scripts/update.ps1` updates only the managed toolchain:

- ensure exact MCP commit;
- ensure exact Forge commit;
- reinstall Python packages;
- regenerate client files.

It never pulls/switches/resets CAD.

## Target selection contract

`scripts/select-model.ps1`:

- accepts a catalog-relative path only;
- rejects absolute paths and `..`;
- requires first path element `models`;
- requires an existing owner with `model.yml`;
- stores the value in ignored `workspace.local.yml`;
- regenerates client files.

It does not change Git branches.

## Template maintenance

Template source uses `main` and `dev`. Normal work:

```text
issue/* -> dev    squash through /merge
dev -> main       merge commit through /merge
main -> dev       merge commit only for stable-only content
```

Keep `docs/plan.md` as the source of truth for unfinished template work.
Do not put concrete model tasks in this repository's plan.

## Compatibility changes

When Forge CAD MCP adopts a different Forge/SolidCraft baseline:

1. update the template pins in one issue/PR;
2. update tests and manuals in the same change;
3. prove bootstrap + doctor against a concrete workspace;
4. only then update concrete workspace repositories.

Do not float the Forge checkout independently from MCP.
