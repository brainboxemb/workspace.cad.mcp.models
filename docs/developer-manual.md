# Developer manual

Use this document when changing or maintaining
`brainboxemb/workspace.cad.mcp.models` itself.

For normal model work use the ordered procedures in `docs/manual/`: basic installation, new model, SolidCraft-to-Forge conversion and existing-model editing. `docs/manual.md` is only the entrypoint.

This repository is a concrete consumer of
`brainboxemb/template.cad.mcp.workspace`. Reusable workspace behavior should
normally be fixed in the template first and then synchronized here.

## Before changing this repository

1. inspect current issues, pull requests and branches;
2. read `AGENTS.md`;
3. read `docs/plan.md`;
4. create an issue if the change has none;
5. branch from `dev`;
6. keep one logical change to one branch and PR.

Do not perform CAD model work in this repository. Model source belongs in
`.repos/cad/` and in `brainboxemb/2026-011-02.cad.solidcraft`.

## Synchronize an accepted template change

Use this procedure when `brainboxemb/template.cad.mcp.workspace` has accepted
reusable behavior that this concrete workspace should adopt.

### 1. Read the accepted template change

Use the template's stable `main` branch as the source. Identify exactly which
shared files changed. Typical shared files are `environment.yml`,
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
If the template changes `docs/manual.md`, copy that manual as the shared user
procedure unless this consumer has a proven local reason to differ.

If commands or file layout change, update this developer manual and the plan in
the same issue.

The first CAD checkout is intentionally lightweight: bootstrap clones only the
configured development branch and uses a blobless partial clone. This prevents
large generated or historical blobs from unrelated refs from being transferred
during initial setup. After the checkout exists, workspace maintenance only
validates its origin and never changes its branch or worktree state.

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

After the issue-branch changes are committed, the workspace helper can push the
branch, open the PR, wait for the central checks and request the existing merge
policy:

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

After merge, remove the completed workstream from active work in
`docs/plan.md` and leave only a short recently-completed note when useful.

### 6. Publish the accepted dev checkpoint

Create a `dev -> main` PR and use `/merge` again. Do not manually choose
merge, squash or rebase.

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

## Change the active model

The active owner is local state in ignored `workspace.local.yml`.

Use:

`./scripts/select-model.ps1 -Model models/components/wall_hook`

This is a local session operation and does not require a repository PR.

## Test a reusable bootstrap change locally

For changes that affect bootstrap, dependency import, Conda setup, target
selection, doctor or generated client configuration, repository CI is not the
final acceptance.

Use a concrete Windows checkout and follow `docs/manual.md` from the relevant
step. At minimum prove:

1. `bootstrap.ps1` succeeds;
2. `doctor.ps1` succeeds;
3. the generated VS Code workspace opens the intended target;
4. the generated MCP definition starts;
5. the assistant can call `environment`;
6. the assistant can call `skill_list`.

If the failure is reusable, fix it in
`brainboxemb/template.cad.mcp.workspace` first and then synchronize the
accepted fix back here.
