import re
import sqlite3
from datetime import datetime, timezone

import pandas as pd

from config import INVENTORY_DB, RAW_DATA_DB


def clean_application_id(value):
    """Clean join/application IDs consistently."""
    if pd.isna(value):
        return None

    value = str(value).strip()
    value = re.sub(r"\.0$", "", value)
    value = re.sub(r"\s+", "", value)
    value = value.upper()

    return value if value else None


def find_column(df, wanted_column):
    """
    Find a column even if there are small spacing/case differences.
    Returns the real dataframe column name.
    """
    if wanted_column in df.columns:
        return wanted_column

    wanted_clean = re.sub(r"[^a-z0-9]", "", str(wanted_column).lower())

    for col in df.columns:
        col_clean = re.sub(r"[^a-z0-9]", "", str(col).lower())
        if col_clean == wanted_clean:
            return col

    return None


def get_keyed_table_map(con):
    """Map inventory table IDs like T001 to actual keyed SQLite table names."""
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


def detect_cardinality(parent_keys, child_keys):
    """Detect whether relationship behaves like 1:1 or 1:many."""
    parent_counts = parent_keys.value_counts(dropna=True)
    child_counts = child_keys.value_counts(dropna=True)

    max_parent_count = int(parent_counts.max()) if not parent_counts.empty else 0
    max_child_count = int(child_counts.max()) if not child_counts.empty else 0

    if max_parent_count > 1:
        return "parent_key_duplicates"

    if max_child_count > 1:
        return "1:many"

    return "1:1_or_0:1"


def validate_relationship(row, raw_con, keyed_table_map):
    rel_id = row.get("rel_id", "")
    year = row.get("year_cycle", row.get("year", ""))

    parent_table_id = row["parent_table_id"]
    child_table_id = row["child_table_id"]

    parent_key_raw = row["parent_key"]
    child_key_raw = row["child_key"]

    expected_cardinality = row.get("cardinality", "")
    join_confidence = row.get("join_confidence", "")

    parent_sqlite_table = keyed_table_map.get(parent_table_id)
    child_sqlite_table = keyed_table_map.get(child_table_id)

    result = {
        "rel_id": rel_id,
        "year": year,
        "parent_table_id": parent_table_id,
        "child_table_id": child_table_id,
        "parent_key": parent_key_raw,
        "child_key": child_key_raw,
        "expected_cardinality": expected_cardinality,
        "declared_join_confidence": join_confidence,
        "parent_sqlite_table": parent_sqlite_table,
        "child_sqlite_table": child_sqlite_table,
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
    }

    if parent_sqlite_table is None or child_sqlite_table is None:
        result.update({
            "status": "failed_missing_keyed_table",
            "error": "Parent or child keyed table not found",
        })
        return result

    parent_df = pd.read_sql(f'SELECT * FROM "{parent_sqlite_table}"', raw_con)
    child_df = pd.read_sql(f'SELECT * FROM "{child_sqlite_table}"', raw_con)

    parent_key_col = find_column(parent_df, parent_key_raw)
    child_key_col = find_column(child_df, child_key_raw)

    if parent_key_col is None or child_key_col is None:
        result.update({
            "status": "failed_missing_join_column",
            "error": f"Missing parent key {parent_key_raw} or child key {child_key_raw}",
            "parent_rows": len(parent_df),
            "child_rows": len(child_df),
        })
        return result

    parent_keys = parent_df[parent_key_col].apply(clean_application_id)
    child_keys = child_df[child_key_col].apply(clean_application_id)

    parent_key_set = set(parent_keys.dropna())
    child_key_set = set(child_keys.dropna())

    matched_child_rows = child_keys.isin(parent_key_set).sum()
    child_key_not_null = child_keys.notna().sum()
    orphan_child_rows = child_key_not_null - matched_child_rows

    matched_parent_keys = parent_key_set.intersection(child_key_set)
    parent_without_child_keys = parent_key_set.difference(child_key_set)

    match_rate = (
        matched_child_rows / child_key_not_null
        if child_key_not_null > 0
        else 0
    )

    detected_cardinality = detect_cardinality(parent_keys, child_keys)

    if child_key_not_null == 0:
        status = "warning_no_child_keys"
    elif orphan_child_rows == 0:
        status = "pass"
    elif match_rate >= 0.8:
        status = "warning_partial_match"
    else:
        status = "fail_many_orphans"

    result.update({
        "status": status,
        "error": "",
        "parent_rows": len(parent_df),
        "child_rows": len(child_df),
        "parent_non_null_keys": int(parent_keys.notna().sum()),
        "child_non_null_keys": int(child_key_not_null),
        "parent_unique_keys": len(parent_key_set),
        "child_unique_keys": len(child_key_set),
        "matched_child_rows": int(matched_child_rows),
        "orphan_child_rows": int(orphan_child_rows),
        "matched_parent_keys": len(matched_parent_keys),
        "parent_without_child_keys": len(parent_without_child_keys),
        "child_match_rate": round(match_rate, 4),
        "detected_cardinality": detected_cardinality,
    })

    return result


def validate_all_relationships():
    with sqlite3.connect(INVENTORY_DB) as inv_con:
        relationships = pd.read_sql(
            """
            SELECT *
            FROM inventory_relationships
            """,
            inv_con,
        )

    results = []

    with sqlite3.connect(RAW_DATA_DB) as raw_con:
        keyed_table_map = get_keyed_table_map(raw_con)

        for _, row in relationships.iterrows():
            result = validate_relationship(row, raw_con, keyed_table_map)
            results.append(result)

            print(
                f"{result['rel_id']} | "
                f"{result['parent_table_id']} -> {result['child_table_id']} | "
                f"{result['status']}"
            )

        results_df = pd.DataFrame(results)

        results_df.to_sql(
            "relationship_validation_results",
            raw_con,
            if_exists="replace",
            index=False,
        )

    print("\nRelationship validation complete.")
    print("Results saved to: relationship_validation_results")


if __name__ == "__main__":
    validate_all_relationships()