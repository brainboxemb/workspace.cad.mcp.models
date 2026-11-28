# Developer manual

Use this document when changing or maintaining
`brainboxemb/workspace.cad.mcp.models` itself.

For normal work use the ordered procedures in `docs/manual/`: basic
installation, local MCP workbench, catalog model creation,
SolidCraft-to-Forge conversion and existing-model editing.
`docs/manual.md` is only the entrypoint.

This repository is a concrete consumer of
`brainboxemb/template.cad.mcp.workspace`. Reusable workspace behavior should
normally be fixed in the template first and then synchronized here.

## Before changing this repository

1. inspect current issues, pull requests and branches;
2. read `AGENTS.md`;
3. read the current `main:docs/plan.md`, not a stale dev copy;
4. create an issue if the change has none;
5. branch from `dev`;
6. keep one logical change to one branch and PR.

Do not perform CAD model work in this repository. Model source belongs in
`.repos/cad/` and in `brainboxemb/2026-011-02.cad.solidcraft`.

## Local VS Code development

Use Git, VS Code with the Python extension, Conda and GitHub CLI. An IDE
coding assistant is optional; the local workflow does not depend on ChatGPT.
Open this workspace repository itself when changing scripts and tests, not
the generated model-only VS Code workspace. Select cad-mcp-workspace as
Python interpreter. Create/update that environment from environment.yml if
needed; unit tests do not require a selected CAD target or a SolidCraft GUI.

~~~powershell
conda env create -f environment.yml # only if the environment does not exist
conda activate cad-mcp-workspace
code .
.\scripts\test.ps1
~~~

Use conda env update -n cad-mcp-workspace -f environment.yml for an existing
environment. For debugging, run individual pytest tests in VS Code or the
activated terminal. Read AGENTS.md before asking an IDE assistant to change
shared behavior. Fix shared behavior in the template first.

## Synchronize an accepted template change

Use this procedure when `brainboxemb/template.cad.mcp.workspace` has accepted
reusable behavior that this concrete workspace should adopt.

### 1. Read the accepted template change

Use the template's stable `main` branch as the source. Record the exact new
and previously adopted stable template SHAs in the consumer issue. Identify
exactly which shared files changed. The [template developer manual](https://github.com/brainboxemb/template.cad.mcp.workspace/blob/main/docs/developer-manual.md) owns the general adoption workflow. Typical shared files are `environment.yml`,
`dependencies.repos`, `scripts/`, `tests/`, `.github/workflows/` and
`docs/manual.md`.

Do not blindly replace the whole repository.

### 2. Preserve consumer-specific files

Do not overwrite these files with template placeholders:

- `README.md`;
- `AGENTS.md`;
- `workspace.yml`;
- `docs/handoff.md`;
- `docs/plan.md`;
- `docs/developer-manual.md`.

`workspace.yml` must keep `workspace.id: models` and the CAD repository
`brainboxemb/2026-011-02.cad.solidcraft` on its configured initial branch.

### 3. Copy only the intended shared changes

Bring the relevant accepted files from template `main` into the issue branch.
For example (replace the issue and SHA placeholders):

~~~powershell
.\scripts\branch.ps1 -Issue 123 -Name adopt-template-change
git remote add workspace-template https://github.com/brainboxemb/template.cad.mcp.workspace.git
git fetch workspace-template main
git diff <previous-template-sha> <new-template-sha> -- scripts tests docs
git restore --source=<new-template-sha> -- scripts/test.ps1
~~~

If the remote already exists, verify its URL instead of adding it again.
Only restore a file that has no consumer-specific changes; apply relevant
hunks manually to customized files. Review new/deleted paths explicitly.
Never merge unrelated template history or reset the consumer to template.
Keep dependency pins unchanged unless an explicit compatibility adoption
is being made. Preserve local ignored files and the active CAD worktree.
If the template changes `docs/manual.md`, copy that manual as the shared user
procedure unless this consumer has a proven local reason to differ.

If commands or file layout change, update this developer manual and reconcile
the canonical plan via a separate main-based control-doc PR; never edit it
on the dev-based implementation branch.

A basic bootstrap or standalone workbench does not create the CAD checkout.
When catalog work is selected for the first time, that checkout is intentionally
lightweight: only the configured development branch is cloned with a blobless
partial clone. After it exists, workspace maintenance only validates its origin
and never changes its branch or worktree state.

MCP and Forge are different: they are disposable vcs2l-managed externals below
`ext/`. Bootstrap and update validate them against `dependencies.repos`.
When a committed release tag changes, the workspace rematerializes the clean
external set through vcs2l. It must never require the operator to manually
delete `ext/`, and it must refuse to discard local external changes or an
unexpected repository origin.

### 4. Publish through the repository policy

Install and authenticate GitHub CLI once:

~~~powershell
gh --version
gh auth status
~~~

If needed, install GitHub CLI and run `gh auth login`.

Test and review the issue branch, then stage explicit files and commit:

~~~powershell
.\scripts\test.ps1
git diff
.\scripts\commit.ps1 -Message "Adopt shared changes (#123)" -Files @("scripts/test.ps1")
.\scripts\pr.ps1 open -Title "Adopt shared changes (#123)" -Body "Refs #123. Template SHA and test evidence: ..."
.\scripts\pr.ps1 merge
~~~

The example paths and issue number are placeholders. Review the PR before
requesting merge. The workspace helper can also combine push, PR and merge
request into one command:

~~~powershell
.\scripts\pr.ps1 publish -Title "Describe the workspace change"
~~~

The helper posts `/merge`; it never performs a direct GitHub merge. The
repository merge-policy workflow remains authoritative.

The same helper can publish model work from the active CAD repository:

~~~powershell
.\scripts\pr.ps1 publish -Path .repos\cad -Title "Describe the model change"
~~~

The steps can also be separated with `pr.ps1 open` and `pr.ps1 merge`.

### 5. Update the plan

After merge, reconcile the main-owned plan through a main-based control-doc
PR. Record the adopted template SHA, actual files and any consumer differences
on the issue. Keep uncompleted live acceptance visible.

### 6. Publish the accepted dev checkpoint

Create a `dev -> main` PR and use `/merge` again, for example after
switching to dev and pulling --ff-only: pr.ps1 open -Base main followed by
pr.ps1 merge. Do not manually choose merge, squash or rebase. After stable
integration pull consumer main on the operator machine; run update.ps1
only for changes that affect the installed environment/toolchain or client
configuration. Docs and local Git helper changes need no reinstall.

## Change MCP or Forge revisions

MCP and Forge external revisions live only in `dependencies.repos`.

When changing a revision:

1. change the required MCP/Forge entry in `dependencies.repos`;
2. update compatibility documentation in the same issue;
3. run CI;
4. run the local workspace acceptance affected by the version change;
5. only then publish the accepted dependency pair.

`scripts/update.ps1` never chooses a newer revision by itself. It reconciles
the existing MCP/Forge externals to exactly what `dependencies.repos`
declares. Matching checkouts remain in place; clean stale checkouts are
rematerialized through vcs2l. The CAD checkout is not part of this operation.

## Change the workspace Conda environment

The one normal-use Conda environment is `cad-mcp-workspace`. Its declarative
source is `environment.yml`.

If the runtime needs a Python dependency or tool such as vcs2l, change
`environment.yml`. Do not add a second normal-use Conda environment.

On the next `scripts/bootstrap.ps1` or `scripts/update.ps1` run, that same
environment is updated from `environment.yml`.

## Change the CAD catalog identity

The concrete catalog identity lives in committed `workspace.yml`. Changing it
is a workspace identity change and must be an explicit reviewed repository
change.

Do not use `workspace.yml` to select the model you happen to be editing today.

## Change the active target

The active target is local state in ignored `workspace.local.yml`.

For a disposable standalone session:

`./scripts/create-workbench.ps1 -Name mcp-test`

For an existing catalog owner:

`./scripts/select-model.ps1 -Model models/components/wall_hook`

A workbench stays below ignored `.workbench/` and does not require the CAD
catalog. Catalog selection uses the configured `.repos/cad` checkout. These
are local session operations and do not require a workspace repository PR.

## Test a reusable bootstrap change locally

For changes that affect bootstrap, dependency import, Conda setup, target
selection, doctor or generated client configuration, repository CI is not the
final acceptance.

Use a concrete Windows checkout and follow `docs/manual.md` from the relevant
step. At minimum prove:

1. `bootstrap.ps1` succeeds without creating the CAD catalog for a standalone
   workbench;
2. `create-workbench.ps1 -Name mcp-test` creates local `project.yml`;
3. `doctor.ps1` succeeds;
4. the generated VS Code workspace opens only the intended workbench;
5. the generated MCP definition starts;
6. the assistant can call `environment`, `skill_list`,
   `forge-modeling` and `solidcraft-control`;
7. the documented live SolidCraft author/apply/inspect/mutate/view/render demo
   completes and writes bounded evidence below `build/`.

If the failure is reusable, fix it in
`brainboxemb/template.cad.mcp.workspace` first and then synchronize the
accepted fix back here.
