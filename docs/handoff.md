# Handoff

Read `docs/plan.md` first. The repository is the reusable local workspace
template for Forge CAD MCP.

The template coordinates local MCP, exact Forge and CAD-library checkouts. It
does not own those products. The CAD checkout is only cloned when absent and is
never reset or branch-switched by workspace maintenance once it exists.

Normal work starts from `dev`; integrate with the repository-local `/merge`
policy.
