import re
import sqlite3
from pathlib import Path

import pandas as pd

from config import RAW_DATA_DB, PROJECT_ROOT


COLUMN_MAPPING = PROJECT_ROOT / "docs" / "column_mapping.csv"
OUTPUT_TABLE = "applications_master"


BASE_COLUMNS = [
    "application_uid",
    "application_id_raw",
    "application_id_std",
    "_source_year",
    "_source_file_id",
    "_source_file_name",
    "_source_table_id",
    "_source_sheet_name",
    "_source_row_number",
]


def normalise_name(name):
    """Normalise column names for loose matching."""
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def find_column(df, wanted_column):
    """Find a source column even if spacing/case differs slightly."""
    if wanted_column in df.columns:
        return wanted_column

    wanted_clean = normalise_name(wanted_column)

    for col in df.columns:
        if normalise_name(col) == wanted_clean:
            return col

    return None


def get_keyed_table_map(con):
    """Map T001, T005, etc. to keyed SQLite table names."""
    tables = pd.read_sql(
        """
        SELECT name AS sqlite_table_name
        FROM sqlite_master
        WHERE type = 'table'
          AND name LIKE 'keyed_raw%'
        ORDER BY name
        """,
        con,
    )

    tables["table_id"] = (
        tables["sqlite_table_name"]
        .str.extract(r"(t\d{3})", expand=False)
        .str.upper()
    )

    return dict(zip(tables["table_id"], tables["sqlite_table_name"]))


def build_applications_master():
    if not COLUMN_MAPPING.exists():
        raise FileNotFoundError(
            f"Column mapping file not found: {COLUMN_MAPPING}"
        )

    mapping = pd.read_csv(COLUMN_MAPPING, dtype=str)

    required_cols = {"table_id", "source_column", "canonical_column"}
    missing = required_cols - set(mapping.columns)

    if missing:
        raise ValueError(f"column_mapping.csv is missing columns: {missing}")

    all_standardised_tables = []

    with sqlite3.connect(RAW_DATA_DB) as con:
        keyed_table_map = get_keyed_table_map(con)

        for table_id, table_mapping in mapping.groupby("table_id"):
            keyed_table = keyed_table_map.get(table_id)

            if keyed_table is None:
                print(f"Skipping {table_id}: no keyed table found")
                continue

            df = pd.read_sql(f'SELECT * FROM "{keyed_table}"', con)

            output = pd.DataFrame()

            # Keep base/provenance columns
            for col in BASE_COLUMNS:
                if col in df.columns:
                    output[col] = df[col]
                else:
                    output[col] = pd.NA

            # Rename mapped source columns to canonical columns
            for _, row in table_mapping.iterrows():
                source_col = row["source_column"]
                canonical_col = row["canonical_column"]

                actual_col = find_column(df, source_col)

                if actual_col is None:
                    print(f"Missing in {table_id}: {source_col} -> {canonical_col}")
                    output[canonical_col] = pd.NA
                else:
                    output[canonical_col] = df[actual_col]

            all_standardised_tables.append(output)

            print(
                f"Added {table_id}: {keyed_table} "
                f"({len(output)} rows, {len(output.columns)} columns)"
            )

        if not all_standardised_tables:
            raise ValueError("No tables were added. Check column_mapping.csv.")

        applications_master = pd.concat(
            all_standardised_tables,
            ignore_index=True,
            sort=False
        )

        applications_master.to_sql(
            OUTPUT_TABLE,
            con,
            if_exists="replace",
            index=False
        )

    print(f"\nCreated {OUTPUT_TABLE} with {len(applications_master)} rows")
    print(f"Saved to: {RAW_DATA_DB}")


if __name__ == "__main__":
    build_applications_master()
    