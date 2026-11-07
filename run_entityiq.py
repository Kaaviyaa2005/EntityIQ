"""Command-line entry point: python run_entityiq.py data/raw/businesses_a.csv data/raw/businesses_b.csv"""
import sys
from src.pipeline import run_pipeline
if __name__ == "__main__":
    paths = sys.argv[1:] or ["data/raw/businesses_a.csv", "data/raw/businesses_b.csv"]
    result = run_pipeline(paths)
    print("EntityIQ run complete")
    for key, value in result["metrics"].items(): print(f"{key}: {value}")
