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
│   └── cad/                   # optional catalog worktree, ignored
├── .workbench/                # local standalone MCP experiments, ignored
│   └── <name>/
│       └── project.yml        # local Forge/SolidCraft/evidence settings
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
worktree where catalog-model branches and edits live. A basic installation or
standalone workbench does not require it. The workspace creates it only when a
catalog-model target is used, and never pulls, resets, cleans or branch-switches
an existing CAD checkout.

## First local run

```powershell
Copy-Item workspace.local.example.yml workspace.local.yml
# Edit only solidcraft.cli
.\scripts\bootstrap.ps1
.\scripts\create-workbench.ps1 -Name mcp-test
.\scripts\doctor.ps1
```

This first run does not need `.repos/cad`. Start SolidCraft, enable
**Preferences → Assistant → Agents through MCP → Let AI agents connect**, then
open `.generated/forge-cad.code-workspace`.

The first acceptance model is a 60 × 20 × 4 mm plate with one centered Ø8 mm
hole. The detailed live Forge/SolidCraft procedure is in
`docs/manual/02-local-workbench.md`.

See [docs/manual.md](docs/manual.md) for daily use and
[docs/developer-manual.md](docs/developer-manual.md) for workspace maintenance.

This repository uses permanent `main` and `dev` branches. Normal source
integration uses the repository-local `/merge` policy.
