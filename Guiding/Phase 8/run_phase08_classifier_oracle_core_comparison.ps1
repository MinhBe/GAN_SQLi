$ErrorActionPreference = "Stop"

$phaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = "C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe"
$oracle = Join-Path $phaseDir "phase08_08_heldout_classifier_oracle.py"
$evaluator = Join-Path $phaseDir "phase08_03_evaluator_contract.py"
$outDir = Join-Path $phaseDir "outputs\classifier_oracle_results"
$reportDir = Join-Path $phaseDir "reports"

$items = @(
  @{
    Name = "anchor_only_full_lite"
    Samples = Join-Path $phaseDir "outputs\surgery_baselines_full_lite\anchor_only_samples.jsonl"
  },
  @{
    Name = "mutation_engine_full_lite"
    Samples = Join-Path $phaseDir "outputs\surgery_baselines_full_lite\mutation_engine_samples.jsonl"
  },
  @{
    Name = "paired_surgery_gan_max_local"
    Samples = Join-Path $phaseDir "outputs\paired_surgery_gan_max_local\paired_surgery_gan_samples.jsonl"
  },
  @{
    Name = "paired_surgery_gan_max_aggressive"
    Samples = Join-Path $phaseDir "outputs\paired_surgery_gan_max_aggressive\paired_surgery_gan_samples.jsonl"
  }
)

$sampleArgs = @()
foreach ($item in $items) {
  $sampleArgs += "--samples"
  $sampleArgs += "$($item.Name)=$($item.Samples)"
}

& $python -u -B $oracle `
  --out-dir $outDir `
  --report-dir $reportDir `
  --report-name "08_classifier_oracle_core_comparison" `
  --max-positive 150000 `
  --max-negative 50000 `
  --target-benign-fpr 0.05 `
  @sampleArgs

foreach ($item in $items) {
  $oracleCsv = Join-Path $outDir "$($item.Name)_classifier_oracle_results.csv"
  & $python -u -B $evaluator `
    --samples $item.Samples `
    --detector-results $oracleCsv `
    --report-dir $reportDir `
    --report-name "08_evaluator_$($item.Name)_with_classifier_oracle.md" `
    --json-name "08_evaluator_$($item.Name)_with_classifier_oracle.json"
}
