
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
# print(f"Project root directory: {PROJECT_ROOT}")


INVENTORY_DB = PROJECT_ROOT /"data"/"sql"/ "sanctuary_inventory.sqlite"

RAW_DATA_DB = PROJECT_ROOT /"data"/"sql"/ "sanctuary_raw_import.sqlite"

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

RAW_FILE_F001 = PROJECT_ROOT / "data" / "raw" / "2020-2024/F001_WIT_20232024Application.xlsx"
RAW_FILE_F004 = PROJECT_ROOT / "data" / "raw" / "2020-2024/F004_20242025RefereeForm.xlsx"
RAW_FILE_F005 = PROJECT_ROOT / "data" / "raw" / "2020-2024/F005_WIT_20232024RefereeForm.xlsx"
RAW_FILE_F002 = PROJECT_ROOT / "data" / "raw" / "2025/F002_UniversityOfSanctuaryAcademicScholarship20252026ApplicationForm.xlsx"
RAW_FILE_F003 = PROJECT_ROOT / "data" / "raw" / "2026/F003_UniversityOfSanctuaryAcademicScholarship20262027ApplicationForm - 11.05.2026.xlsx"

RAW_FILES ={
    "F001": RAW_FILE_F001,
    "F002": RAW_FILE_F002,
    "F003": RAW_FILE_F003,
    "F004": RAW_FILE_F004,
    "F005": RAW_FILE_F005
}

