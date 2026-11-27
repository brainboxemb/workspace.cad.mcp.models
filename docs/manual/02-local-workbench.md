# 02 — Local MCP workbench

Use this for the first MCP test or for disposable Forge experiments that should
not become a CAD-catalog model yet.

A workbench is local workspace state. It is not a Git model owner, does not
require a CAD issue branch and is ignored by the workspace repository. It has
no catalog `model.yml` or `ci.yml`.

## 1. Create and select a workbench

From the workspace root:

~~~powershell
.\scripts\create-workbench.ps1 -Name mcp-test
~~~

This creates:

~~~text
.workbench/mcp-test/
├── project.yml
├── AGENTS.md
└── .codex/
    └── config.toml
~~~

The `.codex/config.toml` file binds the Codex IDE extension directly to the
same Forge CAD MCP stdio command used by the workspace. A separately installed
global `codex` CLI is not required for the normal VS Code workbench flow.

The generated `AGENTS.md` is the Codex router for the standalone workbench,
matching the pattern used by SolidCraft itself: hard boundaries stay in
`AGENTS.md`, while task-specific instructions stay in MCP skills. It routes
Forge authoring to `forge-modeling`, live GUI work to `solidcraft-control`
and native SolidCraft conversion to `solidcraft-to-forge`. Codex loads the
matching `SKILL.md` through `forgeCad.skill_reference` before task-specific
work and reads API/docs/examples through that skill.

Codex must not inspect `ext/forge` directly or use GitHub/web search as an
implicit fallback for release-matched CAD knowledge. Repository or external
research is still allowed when the user explicitly asks for it. `update.ps1`
regenerates this local policy for an existing standalone workbench.

and writes the local target to `workspace.local.yml`.

The generated `project.yml` is local MCP workbench configuration:

~~~yaml
schema: 1
forge:
  source: scpf/model.py
solidcraft:
  connect: auto
evidence:
  enabled: true
  log: build/session.jsonl
  render: build/live/model.png
~~~

It is not CAD catalog metadata. The MCP uses it for the default Forge source,
the running SolidCraft GUI connection and bounded session evidence.

The command also regenerates:

~~~text
.generated/forge-cad.code-workspace
.generated/mcp-config.json
.generated/state.json
~~~

The MCP server is bound with its standalone `--workspace` contract. It is not
bound to `.repos/cad` and catalog dependency tools are therefore unavailable
in this mode.

## 2. Enable live SolidCraft control

Start SolidCraft and enable:

~~~text
Preferences
  → Assistant
  → Agents through MCP
  → Let AI agents connect
~~~

The Forge CAD MCP discovers the authenticated localhost control channel through
Forge. Do not copy ports or tokens into the project file for the normal local
workflow.

## 3. Run doctor

~~~powershell
.\scripts\doctor.ps1
~~~

Doctor validates the pinned MCP/Forge toolchain, SolidCraft and the exact local
workbench root.

## 4. Open VS Code

Open:

~~~text
.generated/forge-cad.code-workspace
~~~

The only project folder is the selected local workbench. The generated
workspace also selects the same Python executable from the `cad-mcp-workspace`
Conda environment that runs the MCP server, so editor analysis and MCP use the
same installed Forge/SCPF package.

For Codex, trust the local workbench project when prompted and reload or reopen
the VS Code window after `.codex/config.toml` is first generated or changed.
Codex then starts `forgeCad` from that project-local configuration; there is no
separate `codex mcp add` step.

## 5. Start the MCP workflow

The first MCP calls should be:

~~~text
environment
skill_list
skill_reference forge-modeling
skill_reference solidcraft-control
workspace_status
~~~

The assistant should use the maintained Forge source only when it needs it:

~~~text
scpf/model.py
~~~

For interactive work it can then use:

~~~text
workspace_write
forge_live
solidcraft_live_inspect
solidcraft_live_execute
solidcraft_live_render
~~~

Live actions and evidence are recorded according to `project.yml`. Generated
files remain below `build/`.

## 6. First acceptance demo

Use this deliberately small model:

~~~text
plate: 60 × 20 × 4 mm
hole:  Ø8 mm
hole position: centred in the plate
~~~

Acceptance sequence:

1. Ask the assistant to create the plate as maintainable Forge Python.
2. Apply it to a new active SolidCraft GUI design with `forge_live`.
3. Inspect the active SolidCraft design and verify the intended dimensions and
   native structure.
4. Use native SolidCraft parameter control to change one exposed dimension,
   then inspect the design again.
5. Set a useful isometric or top view through SolidCraft live control.
6. Retrieve the current model image with `solidcraft_live_render`.
7. Confirm that `build/session.jsonl`, the live render and replay evidence were
   created inside the workbench.

The purpose of this demo is to prove one complete AI → Forge → live SolidCraft
control/evidence loop, not catalog publication.

## 7. Decide what happens next

If the experiment is disposable, remove the local workbench when finished.

If it should become a maintained catalog model, create a real catalog owner
with [Create a new Forge catalog model](02-new-model.md) and move/re-author the
maintained Forge source through that reviewed workflow. Do not treat the
ignored workbench itself as maintained repository source.

## Acceptance

Accepted when a fresh local workbench can pass doctor and complete a real Forge
authoring → live SolidCraft apply/inspect/mutate/view/render cycle without a CAD
repository branch, issue or PR.
