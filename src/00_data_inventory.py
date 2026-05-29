import sqlite3
import pandas as pd

from config import PROJECT_ROOT, INVENTORY_DB

INVENTORY_XLSX = PROJECT_ROOT / "docs" / "data_inventory.xlsx"

TABLE_NAME_MAP = {
    "files": "inventory_files",
    "table": "inventory_tables",
    "relationships": "inventory_relationships",
    "columns": "inventory_columns",
    "issues_log": "inventory_issues",
    "issues": "inventory_issues",
}


def rebuild_inventory_db():
    sheets = pd.read_excel(
        INVENTORY_XLSX,
        sheet_name=None,
        dtype=str
    )

    with sqlite3.connect(INVENTORY_DB) as con:
        for sheet_name, df in sheets.items():
            normalised_sheet_name = sheet_name.strip().lower()
            table_name = TABLE_NAME_MAP.get(normalised_sheet_name)

            if table_name is None:
                print(f"Skipping unknown sheet: {sheet_name}")
                continue

            df.to_sql(
                table_name,
                con,
                if_exists="replace",
                index=False
            )

            print(f"Created {table_name} with {len(df)} rows")

    print("Inventory SQLite rebuild complete.")


if __name__ == "__main__":
    rebuild_inventory_db()