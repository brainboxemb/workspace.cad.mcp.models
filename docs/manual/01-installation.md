# 01 — Basic installation

Use this once on a machine before choosing a model workflow.

This step installs the workspace toolchain and clones the CAD catalog. It does not select a model.

## 1. Prerequisites

PowerShell needs Git, Conda, repository access and a working SolidCraft CLI.

Verify:

~~~powershell
git --version
conda --version
~~~

Do not create a Conda environment yourself and do not install vcs2l separately.

## 2. Clone the concrete workspace

For the models workspace:

~~~powershell
git clone https://github.com/brainboxemb/workspace.cad.mcp.models.git
cd workspace.cad.mcp.models
~~~

The committed workspace.yml identifies the CAD catalog. Exact MCP and Forge revisions are in dependencies.repos.

## 3. Create local machine configuration

~~~powershell
Copy-Item workspace.local.example.yml workspace.local.yml
~~~

Edit only the local SolidCraft CLI path:

~~~yaml
schema: 1

solidcraft:
  cli: C:\\path\\to\\solidcraft-cli.exe
~~~

Do not add a target yet. Target selection belongs to the model workflow.

## 4. Run bootstrap

~~~powershell
.\scripts\bootstrap.ps1
~~~

On the first run the script:

1. creates cad-mcp-workspace from environment.yml;
2. installs Python, vcs2l and workspace dependencies there;
3. runs vcs import --input dependencies.repos ext in the same environment;
4. materializes exact MCP and Forge checkouts under ext/mcp and ext/forge;
5. clones the configured CAD repository to .repos/cad when absent;
6. installs Forge CAD MCP and SCPF into cad-mcp-workspace.

Because no model is selected, the expected final state is toolchain ready with no target selected. That is successful installation.

## 5. Verify the installation

~~~powershell
conda run --no-capture-output --name cad-mcp-workspace vcs --help
~~~

Verify these folders exist:

~~~text
ext/mcp/
ext/forge/
.repos/cad/
~~~

Do not run doctor yet. Doctor validates an exact selected model.

## 6. Continue

For the first acceptance continue with [02 — Create a new Forge model](02-new-model.md).
