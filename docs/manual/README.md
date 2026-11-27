# CAD MCP workspace procedures

These procedures are for a concrete workspace such as workspace.cad.mcp.models.

For the first acceptance, use them in this order:

1. [01 — Basic installation](01-installation.md)
2. [02 — Create a new Forge model](02-new-model.md)
3. [03 — Convert a SolidCraft design to Forge](03-solidcraft-to-forge.md)
4. [04 — Continue an existing Forge model](04-existing-model.md)

[05 — Files and artifacts](05-files-and-artifacts.md) defines which files are maintained source, frozen reference, local scratch or generated client state.

The three model workflows deliberately test different responsibilities:

- new model: Forge Python is the original maintained CAD source;
- SolidCraft to Forge: an independently authored .sc file is the frozen input reference and Forge Python is reconstructed from it;
- existing model: existing Forge Python and Git history are the maintained source and may already have native reference files.

A model-local build/ directory is local MCP scratch/evidence. It is not the catalog generated build branch.
