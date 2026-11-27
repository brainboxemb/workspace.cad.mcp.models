# workspace.cad.mcp.models

Concrete local Forge CAD MCP assistant workspace for
`brainboxemb/2026-011-02.cad.solidcraft`.

This repository owns workspace configuration only. It does not own CAD model
source, Forge, the Forge MCP server, vcs2l or SolidCraft.

Local layout after bootstrap:

```text
workspace.cad.mcp.models/
├── dependencies.repos         # exact MCP + Forge vcs2l pins
├── workspace.yml              # this workspace + CAD catalog config
├── workspace.local.yml        # local target, ignored
├── ext/                       # vcs2l externals, ignored
│   ├── mcp/
│   └── forge/
├── .repos/
│   └── cad/                   # active CAD worktree, ignored
└── .generated/
    ├── forge-cad.code-workspace
    ├── mcp-config.json
    └── state.json
```

The workspace uses one dedicated `cad-mcp-workspace` Conda environment. It
contains vcs2l, the Forge MCP runtime and the workspace Python dependencies.
Bootstrap creates or updates it once and all workspace commands use that same
environment.

The CAD repository is different from an external dependency: it is the active
worktree where model branches and edits live. Workspace maintenance may clone it
when absent, but never pulls, resets, cleans or branch-switches an existing CAD
checkout.

## First local run

```powershell
Copy-Item workspace.local.example.yml workspace.local.yml
# Edit target.model and solidcraft.cli
.\scripts\bootstrap.ps1
.\scripts\doctor.ps1
```

Then open `.generated/forge-cad.code-workspace` and configure the VS Code
Copilot harness from `.generated/mcp-config.json`.

See [docs/manual.md](docs/manual.md) for daily use and
[docs/developer-manual.md](docs/developer-manual.md) for workspace maintenance.

This repository uses permanent `main` and `dev` branches. Normal source
integration uses the repository-local `/merge` policy.
