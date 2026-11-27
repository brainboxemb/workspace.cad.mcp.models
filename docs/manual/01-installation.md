# 01 — Basic installation

Use this once on a Windows machine before choosing a model workflow.

This procedure starts from a machine that may not have Conda installed yet. It
installs the machine-level Conda distribution and the workspace toolchain. It
does not select a target and does not clone the CAD catalog unless a later
catalog-model workflow actually needs it.

## 1. Check Git

Open PowerShell and run:

~~~powershell
git --version
~~~

If Git is not available, install Git for Windows first, open a new PowerShell
window and repeat the command.

If you want the workspace to open and merge GitHub pull requests for you, also
check GitHub CLI:

~~~powershell
gh --version
gh auth status
~~~

If `gh` is missing, install GitHub CLI. If it is not authenticated, run
`gh auth login`. The workspace PR helper uses that existing authentication and
does not store a separate GitHub token.

## 2. Install Conda

Check whether Conda is already available:

~~~powershell
conda --version
~~~

If that command succeeds, keep the existing Conda installation and continue
with step 3.

If it does not succeed, install **Miniforge3** for Windows from the official
conda-forge release:

https://github.com/conda-forge/miniforge/releases/latest

Choose the Windows installer that matches the machine architecture. For the
normal x86-64 Windows installation this is:

~~~text
Miniforge3-Windows-x86_64.exe
~~~

Run the installer with the normal per-user settings.

After installation, open **Miniforge Prompt** once and initialize Conda for
PowerShell:

~~~powershell
conda init powershell
~~~

Close all PowerShell windows and open a new PowerShell window.

Verify:

~~~powershell
conda --version
~~~

Do not create the project environment manually. This step installs Conda on the
machine only. Later, `bootstrap.ps1` creates the dedicated project environment
named `cad-mcp-workspace`.

## 3. Check SolidCraft

Make sure the SolidCraft CLI is installed and note its executable path. You
will put that path in `workspace.local.yml` in step 5.

## 4. Clone the concrete workspace

For the models workspace:

~~~powershell
git clone https://github.com/brainboxemb/workspace.cad.mcp.models.git
cd workspace.cad.mcp.models
~~~

The committed `workspace.yml` identifies the CAD catalog. The qualified
toolchain is pinned by immutable release tags in `dependencies.repos`:
Forge CAD MCP `v0.0.5` and Forge/SCPF `v0.25.0`.

## 5. Create local machine configuration

Create:

~~~powershell
Copy-Item workspace.local.example.yml workspace.local.yml
~~~

Edit only the local SolidCraft CLI path:

~~~yaml
schema: 1

solidcraft:
  cli: C:\path\to\solidcraft-cli.exe
~~~

Do not add a target yet. Target selection belongs to the model workflow.

## 6. Run bootstrap

Run:

~~~powershell
.\scripts\bootstrap.ps1
~~~

On the first run the script:

1. checks whether the project Conda environment `cad-mcp-workspace` exists;
2. creates it from `environment.yml` when it does not exist;
3. updates that same environment from `environment.yml` on later bootstrap
   runs;
4. installs Python, vcs2l and workspace dependencies in that environment;
5. validates the existing MCP/Forge checkouts against `dependencies.repos`;
6. if they already match, keeps them in place; if the committed release tags
   changed, rematerializes only the clean vcs2l-managed externals and then
   validates them again;
7. materializes exact shallow MCP and Forge tag checkouts under `ext/mcp`
   and `ext/forge`, so workspace externals do not retain unrelated Git
   history;
8. installs Forge CAD MCP and SCPF into `cad-mcp-workspace`.

With no target selected, or with a standalone workbench selected, bootstrap
does **not** clone or require `.repos/cad`. The CAD catalog is materialized
only when a catalog-model target is actually used.

Bootstrap never rewrites the CAD worktree. It also refuses to discard local
changes or an unexpected origin below `ext/`; those conditions must be
resolved explicitly rather than silently deleted.

The two Conda levels are therefore:

~~~text
Miniforge3 / Conda
    = installed once on the Windows machine

cad-mcp-workspace
    = project environment created and maintained by bootstrap.ps1
~~~

Because no model is selected, the expected final state is toolchain ready with
no target selected. That is successful installation.

## 7. Verify the installation

Verify vcs2l inside the project environment:

~~~powershell
conda run --no-capture-output --name cad-mcp-workspace vcs --help
~~~

Verify these folders exist:

~~~text
ext/mcp/
ext/forge/
~~~

`.repos/cad/` may correctly be absent at this point. It is not required for
the standalone workbench.

Do not run `doctor.ps1` yet. Doctor validates an exact selected target.

## 8. Update an existing installation

After pulling an accepted workspace/toolchain change, use the normal update
path:

~~~powershell
git switch main
git pull --ff-only
.\scripts\update.ps1
~~~

`update.ps1` updates the same `cad-mcp-workspace` Conda environment,
reconciles MCP and Forge to shallow checkouts of the exact release tags in
`dependencies.repos`, reinstalls the local toolchain packages and regenerates
client state when a target is selected. An existing full-history external is
treated as stale and is safely rematerialized once when it is clean.

Do not manually delete `ext/` to adopt a new MCP or Forge release.
`.repos/cad/`, when present for catalog work, is the active CAD worktree and
is never reset, pulled, cleaned or branch-switched by update. Workbench/no-target
updates do not require or create it.

## 9. Continue

For the first acceptance continue with
[02 — Local MCP workbench](02-local-workbench.md).
