from pathlib import Path
import csv


def load_salinity(csv_path: Path) -> list[float]:
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [float(row["salinity"]) for row in reader]


def main() -> None:
    data_path = Path(__file__).parents[1] / "data" / "raw" / "observations.csv"
    salinity = load_salinity(data_path)
    avg = sum(salinity) / len(salinity)
    print(f"Average salinity: {avg:.2f}")


if __name__ == "__main__":
    main()
