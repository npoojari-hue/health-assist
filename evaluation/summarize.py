# summarize.py - prints the summary of the newest (or a chosen) results CSV without re-running the evaluation.
# usage (project root):  python -m evaluation.summarize            or   python -m evaluation.summarize evaluation/results/results_XXXX.csv
import csv
import sys
from pathlib import Path

from evaluation.run_eval import print_summary

HERE = Path(__file__).parent


def main():
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    else:
        files = sorted((HERE / "results").glob("results_*.csv"))
        if not files:
            sys.exit("No results CSV found in evaluation/results/")
        path = files[-1]
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    print("file:", path.name)
    models = list(dict.fromkeys(r["model"] for r in rows))
    modes = list(dict.fromkeys(r["mode"] for r in rows))
    print_summary(rows, models, modes)


if __name__ == "__main__":
    main()
