import re
import sqlite3
import pandas as pd

from config import RAW_DATA_DB, INVENTORY_DB


def clean_application_id(value):
    if pd.isna(value):
        return None

    value = str(value).strip()
    value = re.sub(r"\.0$", "", value)
    value = value.upper()
    return value


def add_application_keys(df, raw_id_column):
    df["application_id_raw"] = df[raw_id_column]
    df["application_id_std"] = df[raw_id_column].apply(clean_application_id)

    # IDs restart each year, so year + cleaned ID makes it globally safer
    df["application_uid"] = (
        df["_source_year"].astype(str)
        + "_"
        + df["application_id_std"].astype(str)
    )

    return df


def create_keyed_tables():
    with sqlite3.connect(INVENTORY_DB) as inv_con:
        tables_meta = pd.read_sql(
    """
    SELECT
        t.table_id,
        t.table_name,
        t.table_kind,
        c.column_name_raw AS application_id_column_raw
    FROM inventory_tables t
    JOIN inventory_columns c
        ON t.table_id = c.table_id
    WHERE LOWER(TRIM(c.type)) = 'is_application_id'
    """,
    inv_con
)

    with sqlite3.connect(RAW_DATA_DB) as raw_con:
        raw_tables = pd.read_sql(
            """
            SELECT name AS sqlite_table_name
            FROM sqlite_master
            WHERE type = 'table'
            AND name LIKE 'raw%'
            """,
            raw_con
        )

        raw_tables["table_id"] = (
            raw_tables["sqlite_table_name"]
            .str.extract(r"(t\d{3})", expand=False)
            .str.upper()
        )

        plan = raw_tables.merge(tables_meta, on="table_id", how="inner")

        for _, row in plan.iterrows():
            table_id = row["table_id"]
            raw_table = row["sqlite_table_name"]
            raw_id_column = row["application_id_column_raw"]

            df = pd.read_sql(f'SELECT * FROM "{raw_table}"', raw_con)

            if raw_id_column not in df.columns:
                print(f"Skipping {table_id}: missing ID column {raw_id_column}")
                continue

            df = add_application_keys(df, raw_id_column)

            keyed_table = f"keyed_{raw_table}"

            df.to_sql(
                keyed_table,
                raw_con,
                if_exists="replace",
                index=False
            )

            print(f"Created {keyed_table}")

if __name__ == "__main__":
    create_keyed_tables()