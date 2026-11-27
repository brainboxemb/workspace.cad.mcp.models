# Workspace manual

This manual is for daily use of a concrete repository created from
`template.cad.mcp.workspace`, for example `workspace.cad.mcp.models`.

## Files you normally touch

Committed:

- `workspace.yml`: identifies the MCP/toolchain and CAD repository for this
  workspace.

Local and ignored:

- `workspace.local.yml`: exact active model owner and SolidCraft CLI;
- `.repos/`: local child checkouts;
- `.generated/`: generated VS Code and MCP client files.

Do not edit files below `.generated/` manually.

## First local setup

From PowerShell in the concrete workspace repository:

```powershell
Copy-Item workspace.local.example.yml workspace.local.yml
# Edit workspace.local.yml: target.model + solidcraft.cli
.\scripts\bootstrap.ps1
.\scripts\doctor.ps1
```

Bootstrap creates/updates the dedicated Conda environment, manages the MCP and
exact Forge toolchain checkouts, clones the configured CAD repository when it
does not exist, installs MCP/SCPF and generates client files.

An existing CAD checkout is never reset, cleaned, switched or pulled by
bootstrap.

## Generated files

`.generated/forge-cad.code-workspace` opens only the selected target owner as
the normal VS Code project folder.

`.generated/mcp-config.json` contains the absolute stdio MCP definition for
the selected target. It uses the Conda environment's Python directly.

Use the generated MCP definition in the VS Code Copilot MCP configuration.
Do not hand-maintain another set of these absolute paths.

## Select another model

```powershell
.\scripts\select-model.ps1 -Model models\components\wall_hook
.\scripts\doctor.ps1
```

Selection must resolve to one folder below the CAD repository's `models/`
tree containing its own `model.yml`.

The command rewrites only local `workspace.local.yml` and generated client
files. It does not change the CAD Git branch.

Restart the MCP/session after changing target.

## Update the toolchain

```powershell
.\scripts\update.ps1
.\scripts\doctor.ps1
```

Update reasserts the exact configured MCP and Forge commits, then reinstalls
their Python packages.

It deliberately does **not** update or switch the CAD repository. Manage the CAD
worktree with normal Git because it can contain your active branch and edits.

## Daily model workflow

1. Open `.generated/forge-cad.code-workspace`.
2. Make sure the generated MCP config is active in the Copilot harness.
3. Ask the assistant to call `environment`.
4. Verify `cad_ready: true` and the exact `model_id` / `model_relative`.
5. Ask it to call `skill_list` and read the appropriate skill.
6. Work on the selected owner.
7. Keep Git branching/commit/PR work in the CAD repository, not in this
   workspace repository.

## Troubleshooting

Run:

```powershell
.\scripts\doctor.ps1
```

The underlying MCP doctor validates the configured CAD library and exact model
owner, the supported SCPF/Forge pair and the SolidCraft CLI version.

If bootstrap reports a dirty MCP or Forge checkout, do not force-clean it.
Inspect the unexpected modification first.

If the CAD checkout is dirty, that is normal during model work; workspace
bootstrap does not modify it.
