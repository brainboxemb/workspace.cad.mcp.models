# 02 — Local MCP workbench

Use this for the first MCP test or for disposable Forge experiments that should
not become a CAD-catalog model yet.

A workbench is local workspace state. It is not a Git model owner, does not
require a CAD issue branch and is ignored by the workspace repository.

## 1. Create and select a workbench

From the workspace root:

~~~powershell
.\scripts\create-workbench.ps1 -Name mcp-test
~~~

This creates:

~~~text
.workbench/mcp-test/
~~~

and writes the local target to `workspace.local.yml`.

It also regenerates:

~~~text
.generated/forge-cad.code-workspace
.generated/mcp-config.json
.generated/state.json
~~~

The MCP server is bound with its standalone `--workspace` contract. It is not
bound to `.repos/cad` and catalog dependency tools are therefore unavailable
in this mode.

## 2. Run doctor

~~~powershell
.\scripts\doctor.ps1
~~~

Doctor validates the pinned MCP/Forge toolchain, SolidCraft and the exact local
workbench root.

## 3. Open VS Code

Open:

~~~text
.generated/forge-cad.code-workspace
~~~

The only project folder is the selected local workbench.

## 4. Start the MCP workflow

The first MCP calls should be:

~~~text
environment
skill_list
skill_reference forge-modeling
skill_reference forge-checking
workspace_status
~~~

Then give the modeling assignment.

The assistant can create:

~~~text
scpf/model.py
~~~

through `workspace_write`, compile it, replay it through SolidCraft and keep
generated evidence below `build/`.

## 5. Decide what happens next

If the experiment is disposable, remove the local workbench when finished.

If it should become a maintained catalog model, create a real catalog owner
with [Create a new Forge catalog model](02-new-model.md) and move/re-author the
maintained Forge source through that reviewed workflow. Do not treat the
ignored workbench itself as maintained repository source.

## Acceptance

Accepted when a fresh local workbench can pass doctor and complete a real
Forge authoring -> compile -> SolidCraft replay/check cycle without requiring a
CAD repository branch, issue or PR.
