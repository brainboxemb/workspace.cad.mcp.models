# Workspace manual

Use this manual for an existing concrete CAD MCP workspace, for example
`workspace.cad.mcp.models`.

If you are creating a new workspace repository from the template, use
`docs/developer-manual.md` instead.

## First use on a machine

Clone the concrete workspace repository:

```powershell
git clone https://github.com/brainboxemb/workspace.cad.mcp.models.git
cd workspace.cad.mcp.models
```

Create your ignored local configuration:

```powershell
Copy-Item workspace.local.example.yml workspace.local.yml
```

Edit `workspace.local.yml` and set:

- the exact `target.model`;
- the local SolidCraft CLI path.

Then run:

```powershell
.\scripts\bootstrap.ps1
.\scripts\doctor.ps1
```

You do not create or activate a Conda environment yourself.

The first `bootstrap.ps1` run creates `cad-mcp-workspace` from
`environment.yml`. Later bootstrap runs update that same environment. vcs2l,
the Forge MCP runtime and the workspace Python dependencies all run from this
one environment.

When doctor succeeds, open:

```text
.generated/forge-cad.code-workspace
```

Use `.generated/mcp-config.json` as the MCP server definition for the VS Code
assistant.

## Start a normal work session

For an already bootstrapped workspace:

1. open PowerShell in the workspace repository;
2. run:

   ```powershell
   .\scripts\doctor.ps1
   ```

3. open `.generated/forge-cad.code-workspace`;
4. start the assistant;
5. ask it to call `environment`;
6. confirm `cad_ready: true` and the expected target owner;
7. ask it to call `skill_list` before starting CAD work.

You normally do not activate `cad-mcp-workspace` manually. The workspace
scripts and generated MCP configuration invoke it directly.

## Work on the CAD repository

The active CAD worktree is:

```text
.repos/cad/
```

Use normal Git branches, commits and PRs there for model work.

Workspace maintenance does not pull, reset, clean or switch this checkout after
it exists.

Do not commit CAD model changes to the workspace repository.

## Change the active model

From the workspace repository:

```powershell
.\scripts\select-model.ps1 -Model models\components\wall_hook
.\scripts\doctor.ps1
```

The selected path must be an exact model owner containing `model.yml`.

The command updates ignored `workspace.local.yml` and regenerates the client
configuration. It does not change the CAD Git branch.

Restart the MCP/assistant session after changing the target.

## Update the MCP/Forge toolchain

When the workspace repository receives an accepted change to
`environment.yml` or `dependencies.repos`, run:

```powershell
.\scripts\update.ps1
.\scripts\doctor.ps1
```

`update.ps1`:

1. updates the existing `cad-mcp-workspace` environment from
   `environment.yml`;
2. reruns vcs2l using the exact revisions in `dependencies.repos`;
3. reinstalls MCP/SCPF from `ext/mcp` and `ext/forge`;
4. regenerates the client files.

It does not choose newer MCP or Forge revisions by itself and it does not update
the CAD worktree.

## Verify the local environment

To verify that vcs2l is installed in the one workspace environment:

```powershell
conda run --no-capture-output --name cad-mcp-workspace vcs --help
```

To inspect the environment itself:

```powershell
conda env list
```

You should see `cad-mcp-workspace`.

## If bootstrap fails

Run the failing step again only after reading its error.

Common checks:

### Conda is not found

Verify:

```powershell
conda --version
```

If that command fails, fix the local Conda installation first.

### MCP or Forge checkout is missing

Run:

```powershell
.\scripts\import-dependencies.ps1
```

That command uses vcs2l from `cad-mcp-workspace` and recreates the exact
external revisions from `dependencies.repos`.

### CAD checkout is dirty

That is normally expected during model development. Bootstrap/update must not
clean it.

### Doctor fails on the target

Check `workspace.local.yml`. `target.model` must point to an existing exact
owner below `.repos/cad/models/` and that owner must contain `model.yml`.

### SolidCraft CLI is not found

Correct `solidcraft.cli` in `workspace.local.yml`, then rerun:

```powershell
.\scripts\doctor.ps1
```

## Local files created by the workspace

These paths are intentionally not committed:

```text
workspace.local.yml
ext/
.repos/
.generated/
```

Their roles are:

- `workspace.local.yml`: current local target and SolidCraft path;
- `ext/`: exact MCP and Forge external checkouts;
- `.repos/cad/`: active CAD worktree;
- `.generated/`: generated VS Code and MCP client configuration.
