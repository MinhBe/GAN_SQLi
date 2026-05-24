$ErrorActionPreference = "Stop"

$phaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = "C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe"
$detector = Join-Path $phaseDir "phase08_07_detector_evasion_score.py"
$evaluator = Join-Path $phaseDir "phase08_03_evaluator_contract.py"
$outDir = Join-Path $phaseDir "outputs\detector_results"
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

foreach ($item in $items) {
  & $python -u -B $detector `
    --samples $item.Samples `
    --out-dir $outDir `
    --report-dir $reportDir `
    --name $item.Name `
    --threshold 3.0 `
    --strict-threshold 5.0

  $detectorCsv = Join-Path $outDir "$($item.Name)_detector_results.csv"
  & $python -u -B $evaluator `
    --samples $item.Samples `
    --detector-results $detectorCsv `
    --report-dir $reportDir `
    --report-name "08_evaluator_$($item.Name)_with_detector.md" `
    --json-name "08_evaluator_$($item.Name)_with_detector.json"
}
