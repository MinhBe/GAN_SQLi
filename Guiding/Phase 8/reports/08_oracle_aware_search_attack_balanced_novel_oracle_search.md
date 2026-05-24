# 08 - Oracle-Aware Search Report

- Seed samples: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\classifier_oracle_rerank\max_aggressive_candidates_top400_attack_balanced_novel.jsonl`
- Output samples: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\oracle_aware_search\attack_balanced_novel_oracle_search.jsonl`
- Detector results: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\oracle_aware_search\attack_balanced_novel_oracle_search_classifier_oracle_results.csv`
- Generated candidates: `6,800`
- Candidates after filters: `6,791`
- Selected: `400`
- Rejected: `{'not_novel': 9}`

## Selected Summary

- Balanced delimiter rate: `1.0000`
- Novel vs train template rate: `1.0000`
- Batch template duplicate rate: `0.0000`
- Technique hint rate: `0.9950`
- Classifier-oracle bypass rate: `0.0050`
- By technique: `{'boolean_blind': 9, 'error_based': 36, 'time_blind': 100, 'union_based': 255}`

## Oracle Quality

- Test accuracy: `0.9999`
- Test SQLi recall: `1.0000`
- Test benign FPR: `0.0216`
