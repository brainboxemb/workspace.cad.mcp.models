# 02 — Create a new Forge model

Use this when the model does not yet exist in the CAD catalog.

The operator chooses the exact catalog path and creates the owner boundary. After that, the AI may author Forge Python only inside that selected owner.

## 1. Start a CAD work branch

The workspace never switches or updates the CAD repository for you.

~~~powershell
git -C .repos/cad switch dev
git -C .repos/cad pull --ff-only
git -C .repos/cad switch -c issue/<issue>-<model>
~~~

Start from a clean CAD worktree.

## 2. Create and select the owner

From the workspace root:

~~~powershell
.\scripts\create-model.ps1 -Model "models/basic/<owner>" -Id "<model-id>" -Title "<Model title>" -Priority 10
~~~

Allowed owner sections:

~~~text
models/basic/<owner>
models/components/<owner>
models/subassemblies/<owner>
models/assemblies/<owner>
~~~

The command refuses main, the configured development branch and a dirty CAD worktree. It creates model.yml and ci.yml, selects the exact owner locally and regenerates the client configuration.

It deliberately does not create scpf/model.py. That is the first maintained CAD source file the AI authors.

## 3. Run doctor

~~~powershell
.\scripts\doctor.ps1
~~~

Do not start the assistant until doctor succeeds.

## 4. Open VS Code

Open .generated/forge-cad.code-workspace and use .generated/mcp-config.json as the MCP definition.

## 5. Start the AI workflow

The first MCP calls should be:

~~~text
environment
skill_list
skill_reference forge-modeling
skill_reference forge-checking
workspace_status
~~~

Confirm the exact target owner, then give the modeling assignment.

The AI should inspect model.yml and ci.yml, create scpf/model.py, compile, replay, inspect numeric/structural evidence, render views when useful and iterate by changing Forge Python.

## 6. Generated .sc handling

For a new Forge model there is no hand-authored SolidCraft source to preserve.

Maintained source:

~~~text
scpf/model.py
~~~

Generated replay evidence:

~~~text
build/*.sc
build/*.json
build/*.png
~~~

Keep these build files during a session if useful. They may be overwritten or deleted and are never the model source.

Never move a Forge-generated replay file into reference/.

## 7. Review Git changes

~~~powershell
git -C .repos/cad status
~~~

Intended source changes are normally model.yml, ci.yml and scpf/model.py. Owner-local build/ must remain ignored.

## 8. Publish the CAD change

After the maintained CAD changes are committed on the issue branch, the
workspace can open the CAD PR and request the normal repository-policy merge:

~~~powershell
.\scripts\pr.ps1 publish -Path .repos\cad -Title "<PR title>"
~~~

This waits for PR checks and then posts `/merge`; it does not merge around the
repository policy.

## Acceptance

Accepted when a fresh owner can be created, the AI authors Forge source without manual Python editing, replay/checking succeeds, and Git contains only maintained source rather than MCP scratch.
