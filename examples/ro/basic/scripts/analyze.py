from pathlib import Path
import csv


def summarize_counts(csv_path: Path) -> int:
    total = 0
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            total += int(row["count"])
    return total


def main() -> None:
    data_path = Path(__file__).parents[1] / "data" / "observations.csv"
    total = summarize_counts(data_path)
    print(f"Total seagrass counts: {total}")


if __name__ == "__main__":
    main()
