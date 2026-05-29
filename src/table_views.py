import sqlite3
import re

from config import RAW_DATA_DB


def extract_table_id(table_name):
    match = re.search(r"(t\d{3})", table_name.lower())
    return match.group(1) if match else None


def create_table_views():
    with sqlite3.connect(RAW_DATA_DB) as con:
        cursor = con.cursor()

        tables = cursor.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name LIKE 'keyed_raw%'
            ORDER BY name;
            """
        ).fetchall()

        for (table_name,) in tables:
            table_id = extract_table_id(table_name)

            if table_id is None:
                continue

            view_name = table_id

            cursor.execute(f'DROP VIEW IF EXISTS "{view_name}"')

            cursor.execute(
                f"""
                CREATE VIEW "{view_name}" AS
                SELECT *
                FROM "{table_name}";
                """
            )

            print(f"Created view {view_name} -> {table_name}")

        con.commit()

    print("Table views created.")


if __name__ == "__main__":
    create_table_views()
    