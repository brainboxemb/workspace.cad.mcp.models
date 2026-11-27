# Workspace manual

This manual is for daily use of a concrete repository created from
`template.cad.mcp.workspace`, for example `workspace.cad.mcp.models`.

## Files you normally touch

Committed:

- `dependencies.repos`: exact MCP and Forge external Git revisions consumed by
  vcs2l;
- `workspace.yml`: identifies the active CAD repository and workspace/runtime
  settings.

Local and ignored:

- `workspace.local.yml`: exact active model owner and SolidCraft CLI;
- `ext/`: vcs2l-managed MCP and Forge checkouts;
- `.repos/cad/`: active CAD worktree;
- `.generated/`: generated VS Code and MCP client files.

Do not edit files below `.generated/` manually.

## Conda environment

This workspace uses one dedicated Conda environment:

```text
cad-mcp-workspace
  ├── vcs2l
  ├── Forge CAD MCP runtime
  └── workspace Python dependencies
```

`bootstrap.ps1` creates this environment once from `environment.yml` or
updates it when the committed environment definition changes. There is no
normal workflow that switches to a second developer-tools environment.

## First local setup

From PowerShell in the concrete workspace repository:

```powershell
Copy-Item workspace.local.example.yml workspace.local.yml
# Edit workspace.local.yml: target.model + solidcraft.cli
.\scripts\bootstrap.ps1
.\scripts\doctor.ps1
```

Bootstrap:

1. creates/updates `cad-mcp-workspace` from `environment.yml`;
2. runs `vcs import --input dependencies.repos ext` in that environment;
3. clones the configured CAD repository only when `.repos/cad` is absent;
4. installs the MCP and SCPF packages from `ext/mcp` and `ext/forge` in the
   same environment;
5. generates target-specific client files.

An existing CAD checkout is never reset, cleaned, switched or pulled by
bootstrap.

## Generated files

`.generated/forge-cad.code-workspace` opens only the selected target owner as
the normal VS Code project folder.

`.generated/mcp-config.json` contains the absolute stdio MCP definition for
the selected target. It uses the project Conda environment's Python directly.

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

## Update the external toolchain

```powershell
.\scripts\update.ps1
.\scripts\doctor.ps1
```

`update.ps1` reruns vcs2l against the exact revisions committed in
`dependencies.repos`, reinstalls the project packages and regenerates client
files.

Changing an MCP or Forge revision means editing `dependencies.repos` in a
reviewed workspace-template change. The script does not invent or advance
versions.

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

To verify vcs2l in the workspace environment:

```powershell
conda run --no-capture-output --name cad-mcp-workspace vcs --help
```

If `ext/mcp` or `ext/forge` is missing, rerun
`scripts/import-dependencies.ps1`. Do not replace vcs2l with ad-hoc clone
logic.

If the CAD checkout is dirty, that is normal during model work; workspace
bootstrap does not modify it.
