# template.cad.mcp.workspace

Reusable local workspace template for a Forge CAD assistant environment.

A repository created from this template does **not** own CAD models, Forge or
the MCP implementation. It coordinates local checkouts of those repositories,
creates the Conda environment, generates the VS Code/Copilot MCP configuration
and binds one exact CAD model owner as the assistant target.

Typical concrete repository:

```text
template.cad.mcp.workspace
        ↓ use template
workspace.cad.mcp.models
```

Local generated state:

```text
workspace.cad.mcp.models/
├── workspace.yml
├── workspace.local.yml       # local, ignored
├── .repos/                   # managed/local checkouts, ignored
│   ├── mcp/
│   ├── forge/
│   └── cad/
└── .generated/               # generated client files, ignored
    ├── forge-cad.code-workspace
    ├── mcp-config.json
    └── state.json
```

Start with [docs/developer-manual.md](docs/developer-manual.md) when creating a
new concrete workspace. Daily operation is in [docs/manual.md](docs/manual.md).

The template uses `main` for stable content and `dev` for integration.
After the one-time empty-repository bootstrap, all source integrations use the
repository-local `/merge` policy.
