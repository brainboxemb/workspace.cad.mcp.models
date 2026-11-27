# 05 — Files and artifacts

Use this when deciding whether a file is source, reference or scratch.

| Path | Role | Commit? | Normal iteration may overwrite? |
| --- | --- | --- | --- |
| workspace.yml | workspace identity/config | yes | only reviewed workspace change |
| workspace.local.yml | local machine + active target | no | yes |
| dependencies.repos | exact MCP/Forge pins | yes | only reviewed dependency change |
| ext/mcp/ | materialized MCP checkout | no | yes, from declared pin |
| ext/forge/ | materialized Forge checkout | no | yes, from declared pin |
| .repos/cad/ | active CAD Git worktree | separate repo | normal Git workflow |
| model.yml | model metadata | yes | reviewed source edit |
| ci.yml | model build config | yes | reviewed source edit |
| scpf/*.py | maintained Forge CAD source | yes | yes, as source |
| reference/*.sc | frozen independent SolidCraft checkpoint | yes | no during conversion/editing |
| owner-local build/*.json | MCP compile/analysis scratch | no | yes |
| owner-local build/*.sc | generated Forge replay candidate | no | yes |
| owner-local build/*.png | local visual evidence | no | yes |
| .generated/* | generated VS Code/MCP config | no | yes |

## Two kinds of .sc

reference/source.sc means this exact independently authored SolidCraft checkpoint is an input used to understand or verify the Forge model. It is source-owned evidence and is committed.

build/model.sc means this is what current Forge Python replayed into SolidCraft during local iteration. It is reproducible scratch and is not committed.

Never copy a Forge-generated candidate into reference/ merely to make a comparison pass.

## Keeping build files between iterations

It is fine to leave owner-local build/ in place while working. That is useful for snapshots and analysis across attempts.

The directory must remain ignored by Git and may be deleted at any time. A clean rebuild must recreate its contents.

## Updating a native reference

Do not overwrite a conversion baseline silently.

If SolidCraft itself was intentionally changed:

1. save the new design explicitly;
2. import it with a new checkpoint filename;
3. review/commit that reference change;
4. state which checkpoint is the intended baseline.
