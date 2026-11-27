# 04 — Continue an existing Forge model

Use this for a model owner that already exists in Git and already has maintained Forge Python.

This is an editing workflow, not a reconstruction workflow.

## 1. Start the CAD work branch

~~~powershell
git -C .repos/cad switch dev
git -C .repos/cad pull --ff-only
git -C .repos/cad switch -c issue/<issue>-<change>
~~~

Start from a clean worktree.

## 2. Select the existing owner

~~~powershell
.\scripts\select-model.ps1 -Model "models/components/<owner>"
~~~

This changes local target state and generated client configuration only.

## 3. Run doctor and open VS Code

~~~powershell
.\scripts\doctor.ps1
~~~

Open .generated/forge-cad.code-workspace.

## 4. Start the editing workflow

Begin with:

~~~text
environment
skill_list
skill_reference forge-editing
skill_reference forge-checking
workspace_status
workspace_list
~~~

Read existing Forge Python before changing it.

If reference/*.sc exists, treat those files as read-only native evidence. They may be analyzed/rendered for comparison, but normal Forge editing does not modify them.

## 5. Make the smallest source change

Typical loop: read existing Python, write the source change, compile, replay to build/*.sc, analyze/evaluate/components, render snapshots when useful, then run forge-checking.

Do not patch generated JSON or generated .sc.

## 6. Review and commit

~~~powershell
git -C .repos/cad status
~~~

Commit only maintained source/metadata/reference changes required by the issue.

If the task is actually to translate a newer independently authored SolidCraft design, stop and use the SolidCraft-to-Forge workflow instead.

## Acceptance

Accepted when the AI understands the existing Forge model, makes a bounded source edit, verifies it and leaves unrelated source and native references unchanged.
