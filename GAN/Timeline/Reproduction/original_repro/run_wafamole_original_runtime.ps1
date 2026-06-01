$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
$image = "gan-sqli-wafamole-legacy:py37"
$dockerfile = "Timeline\Reproduction\original_repro\Dockerfile.wafamole-legacy"
$probe = "/workspace/Timeline/Reproduction/original_repro/probe_wafamole_original.py"

docker build -f $dockerfile -t $image $repoRoot
docker run --rm -v "${repoRoot}:/workspace" $image python $probe
