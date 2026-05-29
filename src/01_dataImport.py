from config import RAW_DATA_DB, INVENTORY_DB, RAW_FILES
import re
import sqlite3
from datetime import datetime,timezone
import pandas as pd

def make_safe_table_name(year, table_id,table_name):
    """Create a safe table name by combining year, table_id, and a cleaned version of the table_name."""
    # Replace any characters that are not allowed in table names with underscores
    raw_name = f"raw{year}_{table_id}_{table_name}"
    raw_name = raw_name.lower()
    raw_name = re.sub(r'[^a-zA-Z0-9_]', '_', raw_name)
    return raw_name.strip("_") 

def load_import_plan():
    """REad files and tabels from the inventory database."""
    with sqlite3.connect(INVENTORY_DB) as conn:
        files = pd.read_sql_query("SELECT * FROM inventory_files", conn)
        tables = pd.read_sql_query("SELECT * FROM inventory_tables", conn)

        import_plan = tables.merge(files, on = "file_id", suffixes=("_table", "_file"))
        return import_plan

def import_excel_tables():
    import_plan=load_import_plan()
    print(import_plan.columns.tolist())
    registry_rows=[]
    with sqlite3.connect(RAW_DATA_DB) as out_conn:
        for _, row in import_plan.iterrows():
            file_id = row["file_id"]
            table_id = row["table_id"]
            sheet_name = row["table_name"]
            file_path = RAW_FILES[file_id]
            # table_name = row["table_name"]
            year = row["year_table"]

            file_path = RAW_FILES.get(file_id)

            if not file_path:
                registry_rows.append({
                    "file_id": file_id,
                    "table_id": table_id,
                    "sheet_name": sheet_name,
                    "status": "failed_missing_file_path",
                    "error": f"No path found in RAW_FILEs for {file_id}",
                    "datetime": datetime.now(timezone.utc).isoformat()
                })
                continue

            if not file_path.exists():
                registry_rows.append({
                    "file_id": file_id,
                    "table_id": table_id,
                    "sheet_name": sheet_name,
                    "status": "failed_file_not_found",
                    "error": f"File not found at {file_path}",
                    "datetime": datetime.now(timezone.utc).isoformat()
                })
                continue

            try:
                df = pd.read_excel(file_path,sheet_name=sheet_name, dtype=str)

                df["_source_file_id"] = file_id
                df["_source_table_id"] = table_id
                df["_source_file_name"] = file_path.name
                df["_source_sheet_name"] = sheet_name
                df["_source_year"] = year
                df["_source_row_number"] = range(1, len(df)+1)
                df["_source_import_timestamp"] = datetime.now(timezone.utc).isoformat()

                sqlite_table_name = make_safe_table_name(year,table_id,sheet_name)

                df.to_sql(
                    sqlite_table_name,
                    out_conn,
                    if_exists="replace",
                    index=False
                    )

                registry_rows.append({
                    "file_id": file_id, 
                    "table_id": table_id,
                    "sheet_name": sheet_name,
                    "sqlite_table_name": sqlite_table_name,
                    "row_count": len(df),
                    "status": "success",
                    "column_count": len(df.columns),
                    "status": "success",
                    "error":"",
                    "imported_at": datetime.now(timezone.utc).isoformat()
                }) 

                print(f"Imported {table_id}:{sheet_name} from {sqlite_table_name} with {len(df)} rows and {len(df.columns)} columns")
            
            except ValueError as e:
                registry_rows.append({
                    "file_id": file_id,
                    "table_id": table_id,
                    "sheet_name": sheet_name,
                    "status": "failed_sheet_not_found",
                    "error": str(e),
                    "imported_at": datetime.now(timezone.utc).isoformat()
                })

                print(f"Sheet not found: {table_id} - {sheet_name}")

            except Exception as e:
                registry_rows.append({
                    "file_id": file_id,
                    "table_id": table_id,
                    "sheet_name": sheet_name,
                    "status": "failed_read_error",
                    "error": str(e),
                    "imported_at": datetime.now(timezone.utc).isoformat()
                })

                print(f"Error occurred while reading {table_id} - {sheet_name}: {e}")

                registry = pd.DataFrame(registry_rows)
                registry.to_sql(
                    "raw_import_registry",
                    out_conn,
                    if_exists="replace",
                    index=False
        )


if __name__ == "__main__":
    import_excel_tables()