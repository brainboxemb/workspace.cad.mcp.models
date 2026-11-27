# 03 — Convert a SolidCraft design to Forge

Use this when geometry was first created independently in SolidCraft and should become maintained Forge Python.

The original SolidCraft file is the frozen input reference. A Forge replay is a candidate. Never confuse the two.

## 1. Save a deliberate SolidCraft checkpoint

In SolidCraft, save the design you actually want to translate to a normal .sc file before starting conversion.

The conversion cannot preserve an unsaved GUI state.

Do not continue editing that same file while the conversion is in progress. If the native design later changes materially, save and import a new checkpoint.

## 2. Start a CAD work branch

~~~powershell
git -C .repos/cad switch dev
git -C .repos/cad pull --ff-only
git -C .repos/cad switch -c issue/<issue>-<model>
~~~

## 3. Create or select the target owner

For a new catalog owner:

~~~powershell
.\scripts\create-model.ps1 -Model "models/components/<owner>" -Id "<model-id>" -Title "<Model title>"
~~~

For an existing owner:

~~~powershell
.\scripts\select-model.ps1 -Model "models/components/<owner>"
~~~

## 4. Import the native reference

~~~powershell
.\scripts\import-solidcraft-reference.ps1 -Source "C:\\path\\to\\original.sc" -Name "source.sc"
~~~

The helper copies bytes without parsing the native file, verifies SHA-256, writes under reference/ and refuses to overwrite an existing reference with different content.

The resulting reference/source.sc is maintained evidence and should be committed.

For a later native checkpoint, use a new filename such as source-v2.sc rather than silently replacing the conversion baseline.

## 5. Run doctor and open VS Code

~~~powershell
.\scripts\doctor.ps1
~~~

Open .generated/forge-cad.code-workspace.

## 6. Start the conversion workflow

Relevant MCP calls include:

~~~text
environment
skill_list
skill_reference solidcraft-to-forge
skill_reference forge-checking
model_input_summary reference/source.sc
solidcraft_analyze reference/source.sc
~~~

Render reference views when useful. The AI reconstructs modeling intent, creates scpf/model.py and compiles/replays a candidate.

## 7. Keep original and candidate separate

Frozen original: reference/source.sc.

Generated candidate/evidence lives under build/, for example build/solidcraft.json, build/*.sc, build/*.json and build/*.png.

The candidate may be replaced every iteration. The reference may not.

## 8. Review Git changes

Typical maintained files are model.yml, ci.yml, reference/source.sc and scpf/model.py. Owner-local build/ remains ignored.

## Acceptance

Accepted when the native checkpoint remains byte-identical and committed, Forge Python reproduces the required design intent, and verification compares the original against a separately generated candidate.
