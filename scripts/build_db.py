"""Build the read-only SQLite database from the 2014 GRU CSV exports.

Reads `data/csv/result_with_price.csv` (electric) and `data/csv/Water_fixed.csv`
(water), creates tables matching the Django model schema, indexes
ServiceAddress, and writes `data/utility.sqlite3`.

Usage:
    python scripts/build_db.py [--csv-dir data/csv] [--out data/utility.sqlite3]
"""

from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from pathlib import Path

ELECTRIC_CSV = "result_with_price.csv"
WATER_CSV = "Water_fixed.csv"

ELECTRIC_DDL = """
CREATE TABLE Utility_electric (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ServiceAddress VARCHAR(120) NOT NULL,
    Month VARCHAR(20) NOT NULL,
    Year VARCHAR(4) NOT NULL,
    KWH_Consumption INTEGER NOT NULL,
    Charge INTEGER NOT NULL DEFAULT 0
);
"""

WATER_DDL = """
CREATE TABLE Utility_water (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ServiceAddress VARCHAR(120) NOT NULL,
    Month VARCHAR(20) NOT NULL,
    Year VARCHAR(4) NOT NULL,
    Water_Consumption INTEGER NOT NULL,
    Charge INTEGER NOT NULL DEFAULT 0
);
"""


def _row(record: list[str]) -> tuple[str, str, str, int, int] | None:
    if len(record) != 5:
        return None
    address, month, year, consumption, charge = (c.strip() for c in record)
    if not address:
        return None
    try:
        return address, month, year, int(consumption), int(charge)
    except ValueError:
        return None


def _load_csv(conn: sqlite3.Connection, table: str, csv_path: Path) -> int:
    if not csv_path.exists():
        raise FileNotFoundError(f"missing CSV: {csv_path}")

    sql = f"INSERT INTO {table} (ServiceAddress, Month, Year, {'KWH_Consumption' if table == 'Utility_electric' else 'Water_Consumption'}, Charge) VALUES (?, ?, ?, ?, ?)"
    inserted = 0
    batch: list[tuple] = []
    with csv_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        for record in reader:
            row = _row(record)
            if row is None:
                continue
            batch.append(row)
            if len(batch) >= 10_000:
                conn.executemany(sql, batch)
                inserted += len(batch)
                batch = []
        if batch:
            conn.executemany(sql, batch)
            inserted += len(batch)
    return inserted


def build(csv_dir: Path, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()

    conn = sqlite3.connect(out)
    try:
        conn.execute("PRAGMA journal_mode = OFF;")
        conn.execute("PRAGMA synchronous = OFF;")
        conn.execute("PRAGMA temp_store = MEMORY;")

        conn.executescript(ELECTRIC_DDL)
        conn.executescript(WATER_DDL)

        with conn:
            elec = _load_csv(conn, "Utility_electric", csv_dir / ELECTRIC_CSV)
            print(f"electric: inserted {elec:,} rows", file=sys.stderr)

        with conn:
            water = _load_csv(conn, "Utility_water", csv_dir / WATER_CSV)
            print(f"water: inserted {water:,} rows", file=sys.stderr)

        conn.execute(
            "CREATE INDEX Utility_electric_address_idx ON Utility_electric (ServiceAddress);"
        )
        conn.execute(
            "CREATE INDEX Utility_water_address_idx ON Utility_water (ServiceAddress);"
        )
        conn.commit()

        conn.execute("VACUUM;")
        conn.execute("ANALYZE;")
        conn.commit()
    finally:
        conn.close()

    size_mb = out.stat().st_size / (1024 * 1024)
    print(f"wrote {out} ({size_mb:.1f} MB)", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--csv-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data" / "csv",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data" / "utility.sqlite3",
    )
    args = parser.parse_args()
    build(args.csv_dir, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
