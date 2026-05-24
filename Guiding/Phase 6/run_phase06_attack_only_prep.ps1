$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$py = "python"
$phase = Join-Path $root "Guiding\Phase 6"

& $py (Join-Path $phase "phase06_01_tokenize_shards.py") `
  --cache-dir (Join-Path $phase "cache\token_shards_attack_only") `
  --report-dir (Join-Path $phase "reports") `
  --report-name "06_token_shard_attack_only_report.md" `
  --log-dir (Join-Path $phase "logs") `
  --progress-name "phase06_attack_only_tokenize_progress.json" `
  --include-techniques "boolean_blind,time_blind,union_based,error_based" `
  --overwrite
