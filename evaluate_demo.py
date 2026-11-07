"""Evaluate the most recent local run against generated labelled duplicate pairs."""
import pandas as pd
from src.evaluation import pair_metrics
from src.pipeline import run_pipeline

if __name__ == "__main__":
    result = run_pipeline(["data/raw/businesses_a.csv", "data/raw/businesses_b.csv"])
    truth_df = pd.read_csv("data/raw/ground_truth_pairs.csv")
    truth = list(zip(truth_df.left_record_id.astype(str), truth_df.right_record_id.astype(str)))
    metrics = pair_metrics(result["matches"], truth)
    print("Pair-level labelled evaluation (synthetic dataset):")
    for key, value in metrics.items():
        print(f"{key}: {value}")
    print("Operational metrics:", result["metrics"])
