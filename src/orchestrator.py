import argparse
import subprocess
import sys
from pathlib import Path

from config import RAW_DATA_DB


SRC_DIR = Path(__file__).resolve().parent

PIPELINE_STEPS = [
    "00_data_inventory.py",
    "01_dataImport.py",
    "02_map_and_union.py",
    "03_validate_relationships.py",
    "04_build_applications_master.py",
    "05_screening_flags.py",
]


def delete_raw_database(): #not always necessary!
    """Delete raw SQLite DB and sidecar files for a clean rebuild."""
    files_to_delete = [
        RAW_DATA_DB,
        RAW_DATA_DB.with_name(RAW_DATA_DB.name + "-journal"),
        RAW_DATA_DB.with_name(RAW_DATA_DB.name + "-wal"),
        RAW_DATA_DB.with_name(RAW_DATA_DB.name + "-shm"),
    ]

    for file_path in files_to_delete:
        if file_path.exists():
            file_path.unlink()
            print(f"Deleted: {file_path}")


def run_pipeline(fresh=False):
    if fresh:
        delete_raw_database()

    for step in PIPELINE_STEPS:
        script_path = SRC_DIR / step

        if not script_path.exists():
            raise FileNotFoundError(f"Missing pipeline script: {script_path}")

        print(f"\n=== Running {step} ===")

        subprocess.run(
            [sys.executable, str(script_path)],
            check=True
        )

    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Delete the raw SQLite database before rebuilding."
    )

    args = parser.parse_args()

    run_pipeline(fresh=args.fresh)