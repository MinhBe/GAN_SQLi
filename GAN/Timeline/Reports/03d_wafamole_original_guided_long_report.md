# WAF-A-MoLE Original Guided Long Run

## Summary

This run extends the original-faithful WAF-A-MoLE guided engine beyond the initial smoke probe. It uses the legacy Docker runtime and bundled upstream example models. Payload text is not written to reports or logs.

## Metrics

| Metric | Value |
| --- | ---: |
| Models total | 5 |
| Guided attempted | 4 |
| Threshold reached | 0 |
| Skipped, initial below threshold | 1 |
| Failed | 0 |
| No threshold reached | 4 |

## Per-Model Results

| Type | Model | Status | Initial confidence | Final confidence | Threshold reached | Seconds |
| --- | --- | --- | ---: | ---: | --- | ---: |
| token | naive_bayes_trained.dump | max_rounds_or_timeout_no_threshold | 0.998935 | 0.998935 | false | 1.019 |
| token | random_forest_trained.dump | max_rounds_or_timeout_no_threshold | 0.758333 | 0.533333 | false | 4.898 |
| token | lin_svm_trained.dump | max_rounds_or_timeout_no_threshold | 0.512992 | 0.512992 | false | 0.986 |
| token | gauss_svm_trained.dump | skipped_initial_below_threshold | 0.314399 | 0.314399 | false | 0.021 |
| mlbasedwaf | mlbasedwaf_ada.dump | max_rounds_or_timeout_no_threshold | 0.519100 | 0.506153 | false | 14.053 |

## Claim Rule

Claim evasion success only for rows with `status=threshold_reached`. Rows with `skipped_initial_below_threshold` are not guided evasion successes because the starting payload was already below the classifier threshold.
