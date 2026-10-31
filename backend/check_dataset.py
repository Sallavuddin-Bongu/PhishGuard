
from pathlib import Path
import pandas as pd

files = list(Path("datasets/phiusiil").rglob("*.csv"))

if not files:
    raise SystemExit("No CSV file found in datasets/phiusiil")

for file in files:
    print(f"\nDataset: {file.name}")
    print(f"Size: {file.stat().st_size:,} bytes")

    header = pd.read_csv(file, nrows=0)
    print(f"Number of columns: {len(header.columns)}")
    print("Column names:")
    print(header.columns.tolist())

    if "label" not in header.columns:
        print("ERROR: No label column found.")
        continue

    label_counts = {}
    total_rows = 0

    for chunk in pd.read_csv(file, chunksize=100_000):
        total_rows += len(chunk)
        counts = chunk["label"].value_counts(dropna=False)
        for label, count in counts.items():
            label_counts[label] = label_counts.get(label, 0) + int(count)

    print(f"\nTotal rows: {total_rows:,}")
    print("Label counts:", label_counts)
