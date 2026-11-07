# EntityIQ – Technical Report

## 1. Problem statement
Business directories often contain multiple representations of one organization across sources. EntityIQ standardizes records and proposes duplicate links while retaining source lineage and a record-to-entity map.

## 2. Data availability and assumptions
No source business dataset was attached at build time. A deterministic generator creates 10,000 synthetic records representing 5,000 paired entities. This provides a repeatable smoke-test dataset, not a proxy for real-world accuracy. The generator writes labelled pair truth to `data/raw/ground_truth_pairs.csv`.

## 3. Methodology
1. Ingest CSV files, harmonize aliases, assign stable source-prefixed record IDs.
2. Preserve raw values and derive normalized name, address, phone, email, website, postal and geographic fields.
3. Generate candidates with multiple independent blocking keys and deduplicate pairs.
4. Calculate name/address sequence and token similarities plus contact-field similarities.
5. Compute a normalized weighted score and map it to configurable classes.
6. Apply conservative guards and union-find grouping; create deterministic IDs from sorted source record IDs.
7. Select canonical values by most frequent non-empty observed value with deterministic tie-breaking.
8. Persist CSV outputs and SQL tables.

## 4. Blocking strategy
The implementation uses name prefix, name+postal, name+city, postal, phone prefix and website domain. Blocking reduces comparisons from the theoretical `n(n-1)/2` to the candidate-pair count. Pair completeness is the fraction of known true pairs that survive blocking. Reduction ratio is `1 - candidate_pairs / all_pairs`. Large blocks are skipped using a configurable cap to avoid pathological pair explosion; this trade-off must be measured for each dataset.

## 5. Feature engineering and scoring
Features are in [0,1]. Name and address take the maximum of sequence ratio and token Jaccard. Phone, email and website use exact equality first and sequence ratio otherwise. The default weights sum to 1.0: name 0.35, address 0.25, phone 0.18, email 0.10, website 0.12. Missing values contribute zero under a fixed denominator. This makes sparse data less likely to receive a misleadingly high score.

## 6. Decision thresholds
- Exact Match: score >= 0.94
- Probable Match: score >= 0.82 and < 0.94
- Non-Match: score < 0.82

These are configurable initial thresholds. Select final thresholds by evaluating precision/recall on a manually reviewed, representative validation sample. In entity resolution, false positives can merge distinct businesses, so precision and cluster consistency deserve special attention.

## 7. Entity construction and safeguards
Accepted pairs are processed in descending score order. The resolver requires reasonable name similarity or a shared strong identifier and rejects a pair when both populated phone and email conflict. Entity IDs are deterministic hashes of member record IDs. Canonical fields are chosen by frequency among non-empty raw values. This is explainable but not a full probabilistic linkage model; production deployments should add cluster-level contradiction checks, branch/address semantics and a review queue.

## 8. Evaluation plan
For labelled data, calculate:
- Precision = TP / (TP + FP)
- Recall = TP / (TP + FN)
- F1 = harmonic mean of precision and recall
- Pair completeness = true duplicate pairs found by blocking / all known true duplicate pairs
- Reduction ratio = 1 - generated candidate pairs / all possible pairs

Compare blocking variants by enabling/disabling individual keys and compare thresholds on the same held-out labels. Track record count, candidate pairs, accepted pairs, unique entities, invalid records and elapsed time. `run_metrics.json` reports observed operational counts. No benchmark metrics are asserted here because the actual run and dataset-specific validation are expected in the user's environment.

## 9. AWS Glue
The Glue script reads S3 CSVs, normalizes fields, forms bounded blocks, self-joins candidates and writes standardized records and candidate-match scores. It is Glue-compatible code but has not been deployed or executed in an AWS account. It intentionally documents its reduced matching scope; use the local implementation as the correctness reference until the distributed resolver is extended and validated.

## 10. Limitations and conclusion
EntityIQ provides a reproducible modular baseline with lineage, multiple blocking passes, explainable similarity features, configurable thresholds, SQL persistence and unit tests. Accuracy depends on source quality and representative labelled examples. Before production use, validate on real data, tune blocking/thresholds, review probable matches, test cluster-level false merges and run load tests on the target AWS Glue configuration.


## 11. Executed synthetic benchmark results

A local run on the bundled synthetic benchmark (10,000 records and 5,000 labelled duplicate pairs) completed in 30.30 seconds in the build environment. It generated 15,478 candidate pairs from 49,995,000 possible pairs (99.9690% reduction). All 5,000 labelled duplicate pairs survived blocking (100.00% pair completeness). The resolver accepted 4,344 pairs: 4,323 true positives and 21 false positives, giving pair precision 99.52%, recall 86.46%, and F1 92.53%. It emitted 5,677 clusters/entities.

Interpretation: high precision is accompanied by missed true links, so the default thresholds/safeguards are conservative. These results apply only to the generated synthetic dataset and must not be generalized to real business records. The generated dataset intentionally contains controlled name/address variants; real-world abbreviations, branch semantics, shared switchboard numbers, recycled phone numbers and missing data may materially change performance.
