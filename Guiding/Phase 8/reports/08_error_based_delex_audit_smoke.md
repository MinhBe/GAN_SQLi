# 08 - Error-Based Delex Audit

Scope: aggregate signature preservation audit for `error_based` rows. Raw payloads are intentionally omitted.

## Summary

- Source: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 5\outputs\full\gold.parquet`
- Rows: `6,437`
- Raw signature rate: `0.1338`
- Delex signature rate: `0.0586`
- Lost-all rate given raw signature: `0.5621`
- Decision: `inspect_labels_or_expand_signature_schema`

## Signature Counts

| Signature | Raw Count | Delex Count | Lost Count |
|---|---:|---:|---:|
| convert | 198 | 77 | 121 |
| exp | 114 | 0 | 114 |
| extractvalue | 264 | 141 | 123 |
| floor_rand | 172 | 0 | 172 |
| group_by_having | 168 | 105 | 63 |
| updatexml | 115 | 54 | 61 |

## Sample Hash Audit

| Raw Hash | Delex Hash | Raw Sigs | Delex Sigs | Lost Sigs |
|---|---|---|---|---|
| d0aafab19f0e3b306a35 | 1d2ea3a4b2ddd2b7a85b | none | none | none |
| d4632833ac2ccd7ff91f | 1d2ea3a4b2ddd2b7a85b | none | none | none |
| 6fe59a5e556ab0351f65 | 1d2ea3a4b2ddd2b7a85b | none | none | none |
| ba783617672e5f81a507 | f9c80328bfdbd1c11e85 | none | none | none |
| b85726d04c3ced9b26a7 | 1d2ea3a4b2ddd2b7a85b | none | none | none |
| 3ff153762af26c4fde9c | 91e48fbbdc5c58747e9d | extractvalue | extractvalue | none |
| ce33d6f0f6f71cebffea | 2d9452b3231d177dd3f4 | exp | none | exp |
| d2e826f248d3ab968c9f | d0a2afe0304d027a0d39 | none | none | none |
| f9d213bfe3edd899275a | d0a2afe0304d027a0d39 | exp | none | exp |
| b0d758688b71618ed30d | 6fcb95451d0733913ead | none | none | none |
| 9d3f2651d22f63635a49 | 2d32ea0f0ed3a2d2a48d | extractvalue | extractvalue | none |
| b0a98c9a4059873f6580 | ac182833ec3caf3d64dd | none | none | none |
| edcbbce177e97f170658 | 6a2baf59087c74b914b6 | floor_rand, group_by_having | group_by_having | floor_rand |
| dedeea2a50fe361b77aa | 9ac3a76919dd51de9702 | floor_rand, group_by_having | group_by_having | floor_rand |
| 3051442131671f1b0674 | 4709042c3f4de8b7282b | extractvalue | extractvalue | none |
| 50dca180ff41211ecdd3 | 55080965c67728628c74 | floor_rand, group_by_having | group_by_having | floor_rand |
| 828366180ebc955376fe | 2d9452b3231d177dd3f4 | extractvalue | none | extractvalue |
| e78da94d65d0b0de5065 | 2d9452b3231d177dd3f4 | extractvalue | none | extractvalue |
| c79c6a49ee72e3e382e6 | 2d9452b3231d177dd3f4 | exp | none | exp |
| 5b9e6c18bfe367a26276 | e58c9eadadacc543c613 | extractvalue | extractvalue | none |
| fc2541f69bacb3ade7d3 | 21211e55190894ff88bc | floor_rand, group_by_having | group_by_having | floor_rand |
| 4fbb3efd76ca58c67cff | 3d6f72c2da53cc9338a5 | none | none | none |
| a7989efd126f78912cb2 | c24c6293dce78ba977b4 | none | none | none |
| fc171471ac319edec78d | 69ba88daccb3957d9ed7 | none | none | none |
| 2e3b6c5f0f1155feec90 | 2d9452b3231d177dd3f4 | none | none | none |
| a81540a362cb53738e93 | d0a2afe0304d027a0d39 | updatexml | none | updatexml |
| 79797f37da65ad34ab89 | d0a2afe0304d027a0d39 | updatexml | none | updatexml |
| 5350d88be6fd2a6d4e33 | 2d9452b3231d177dd3f4 | exp | none | exp |
| 301db25c5cd179206dc0 | 2d9452b3231d177dd3f4 | floor_rand, group_by_having | none | floor_rand, group_by_having |
| c059222f5b84ac3313ec | 2d9452b3231d177dd3f4 | extractvalue | none | extractvalue |
| f0549bf1cf238e59da4a | 6f387d35811f9f866b6a | extractvalue | extractvalue | none |
| c9c8c13a770701fe0e88 | e98b69c5308e85ac3852 | updatexml | none | updatexml |
| 875bd59be8d741515065 | fee4b6680842c6c838c8 | none | none | none |
| d1f7a7935eb41e5dd4d4 | 47a093a50a8432cc9cc0 | extractvalue | extractvalue | none |
| 2bd195df8df4f27b9242 | 2d9452b3231d177dd3f4 | exp | none | exp |
| 1b584a964487596909fe | 73bd76c144b46d5e9b0a | floor_rand, group_by_having | group_by_having | floor_rand |
| 91c8694c894d286d5161 | 04885cf9ae6f591194a2 | convert | none | convert |
| b1cf84f8d8bbf18b2cd9 | 46c61731d7fe783e23e0 | convert | convert | none |
| 3e43902f5d7bb733b714 | 8c1fef9b3f72902fc2db | extractvalue | extractvalue | none |
| 32d6baa163970fc50193 | 2d9452b3231d177dd3f4 | updatexml | none | updatexml |
| 2142372ab31505d6a507 | 2d9452b3231d177dd3f4 | none | none | none |
| 62b32a9a0efb5de8cdca | 2d9452b3231d177dd3f4 | extractvalue | none | extractvalue |
| 760d94a9a7f6a1b3ebeb | 34fb2c9880aab9a410ff | floor_rand, group_by_having | group_by_having | floor_rand |
| abbcfbe6f7db4eb74499 | 070c819fb94b59fbb033 | updatexml | updatexml | none |
| b27f0262597fc98f6f99 | 2d9452b3231d177dd3f4 | convert | none | convert |
| b2f10059a4da96fdd3c6 | 261f0cb7d7abafeee350 | exp | none | exp |
| 1a72e0d12d985bc078d1 | d2db46819aadba67f4ea | none | none | none |
| 4fb62f3f074a3347afe1 | 2f474c42ae021771467d | none | none | none |
| e328a1a65b183254260d | fe3df5a2450da6e822ff | none | none | none |
| eccc19c32e90194d40ca | f9316ca6d3cce8775a6f | none | none | none |

## Interpretation

- `build_delex_v2_preserving_error_function_names` means error-based signatures are being erased enough that training/evaluation on the current representation is unsafe.
- `inspect_labels_or_expand_signature_schema` means the raw rows themselves do not match the current error-based signature schema often enough; label audit comes before model work.
- `keep_current_representation` means current delex is not the primary blocker for this signature set, though evaluator calibration is still required.
