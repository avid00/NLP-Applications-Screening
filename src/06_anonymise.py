import re
import sqlite3
import pandas as pd

from config import RAW_DATA_DB, INVENTORY_DB, PROJECT_ROOT


INPUT_TABLE = "applications_screening_flags"
OUTPUT_TABLE = "applications_anonymised"
TEXT_CORPUS_TABLE = "free_text_corpus"

COLUMN_MAPPING = PROJECT_ROOT / "docs" / "column_mapping.csv"


# These are the free-text fields we want for NLP
#  NOT dropping them, but I will scrub obvious identifiers from them.
FREE_TEXT_FIELDS = [
    "personal_statement_meaning_of_study",
    "course_interest_statement",
    "english_proficiency_statement",
]


# marked as PIIs
DIRECT_DROP_COLUMNS = {
    "application_uid",
    "application_id_raw",
    "application_id_std",
    "form_id",
    "cao_number",
    "setu_student_id",
    "signature",
    "signature_date",
    "_source_file_name",
    "_source_row_number",
}


# extra safety net in case any direct PIIs slipped through mapping.
DROP_IF_COLUMN_CONTAINS = [
    "email",
    "phone",
    "telephone",
    "address",
    "eircode",
    "postcode",
    "postalcode",
    "dateofbirth",
    "date_of_birth",
    "dob",
    "passport",
    "pps",
    "ppsn",
    "referee",
    "signature",
]


def normalise_name(value):
    """Normalise a column names for matching messy Excel headers."""
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def is_missing(value):
    if pd.isna(value):
        return True

    value = str(value).strip().lower()

    return value in {
        "",
        "nan",
        "none",
        "null",
        "n/a",
        "na",
        "not applicable",
    }


def scrub_text(value):
    """
    Basic free-text de-identification.

    Does not guarantee perfect anonymisation, but it removes obvious
    direct identifiers before NLP/theme tagging.
    """
    if is_missing(value):
        return pd.NA

    text = str(value)

    # Emails
    text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "[EMAIL]",
        text,
    )

    # URLs
    text = re.sub(
        r"https?://\S+|www\.\S+",
        "[URL]",
        text,
        flags=re.IGNORECASE,
    )

    # Irish Eircode-style patterns
    text = re.sub(
        r"\b[A-Z0-9]{3}\s?[A-Z0-9]{4}\b",
        "[EIRCODE]",
        text,
        flags=re.IGNORECASE,
    )

    # Phone-like long digit sequences
    text = re.sub(
        r"\+?\d[\d\s().-]{6,}\d",
        "[PHONE_OR_ID]",
        text,
    )

    # Long standalone numeric identifiers
    text = re.sub(
        r"\b\d{7,}\b",
        "[NUMERIC_ID]",
        text,
    )

    # Collapse repeated whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text if text else pd.NA


def get_pii_canonical_columns():
    """
    Use inventory_columns + column_mapping.csv to find canonical columns
    whose original source columns were marked as is_pii.
    """
    if not COLUMN_MAPPING.exists():
        raise FileNotFoundError(f"Missing column mapping file: {COLUMN_MAPPING}")

    mapping = pd.read_csv(COLUMN_MAPPING, dtype=str)

    with sqlite3.connect(INVENTORY_DB) as con:
        inventory_columns = pd.read_sql(
            """
            SELECT *
            FROM inventory_columns
            """,
            con,
        )

    if "type" not in inventory_columns.columns:
        raise ValueError("inventory_columns must contain a 'type' column.")

    required_mapping_cols = {"table_id", "source_column", "canonical_column"}
    missing_mapping_cols = required_mapping_cols - set(mapping.columns)

    if missing_mapping_cols:
        raise ValueError(
            f"column_mapping.csv is missing columns: {missing_mapping_cols}"
        )

    required_inventory_cols = {"table_id", "column_name_raw", "type"}
    missing_inventory_cols = required_inventory_cols - set(inventory_columns.columns)

    if missing_inventory_cols:
        raise ValueError(
            f"inventory_columns is missing columns: {missing_inventory_cols}"
        )

    pii_columns = inventory_columns[
        inventory_columns["type"]
        .fillna("")
        .str.strip()
        .str.lower()
        .eq("is_pii")
    ].copy()

    mapping = mapping.copy()

    pii_columns["table_id_norm"] = pii_columns["table_id"].str.strip().str.upper()
    pii_columns["source_norm"] = pii_columns["column_name_raw"].apply(normalise_name)

    mapping["table_id_norm"] = mapping["table_id"].str.strip().str.upper()
    mapping["source_norm"] = mapping["source_column"].apply(normalise_name)

    joined = mapping.merge(
        pii_columns[["table_id_norm", "source_norm", "column_name_raw"]],
        on=["table_id_norm", "source_norm"],
        how="inner",
    )

    pii_canonical_columns = set(joined["canonical_column"].dropna())

    return pii_canonical_columns


def should_drop_column(column_name, pii_canonical_columns):
    """
    Decide whether a column should be removed from applications_anonymised.
    """
    col = str(column_name)
    col_norm = normalise_name(col)

    # Keep scrubbed free-text fields for NLP, even if they are sensitive.
    if col in FREE_TEXT_FIELDS:
        return False

    if col in DIRECT_DROP_COLUMNS:
        return True

    if col in pii_canonical_columns:
        return True

    for pattern in DROP_IF_COLUMN_CONTAINS:
        if pattern in col_norm:
            return True

    return False


def create_anon_ids(df):
    """
    Create stable anonymous IDs for this output.
    !Does not save the application_uid -> anon_applicant_id lookup separately.
    """
    if "application_uid" not in df.columns:
        raise ValueError("Input table must contain application_uid.")

    unique_ids = (
        df["application_uid"]
        .dropna()
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

    anon_lookup = {
        application_uid: f"A{index:05d}"
        for index, application_uid in enumerate(unique_ids, start=1)
    }

    df.insert(
        0,
        "anon_applicant_id",
        df["application_uid"].map(anon_lookup)
    )

    return df


def build_free_text_corpus(df):
    """
    Convert wide free-text fields into a long NLP corpus table:
    one row per applicant per text field.
    """
    corpus_rows = []

    available_text_fields = [
        field for field in FREE_TEXT_FIELDS
        if field in df.columns
    ]

    for _, row in df.iterrows():
        for field in available_text_fields:
            text = row[field]

            if is_missing(text):
                continue

            corpus_rows.append({
                "anon_applicant_id": row.get("anon_applicant_id"),
                "_source_year": row.get("_source_year"),
                "_source_table_id": row.get("_source_table_id"),
                "text_field": field,
                "response_text": text,
                "response_length_chars": len(str(text)),
            })

    return pd.DataFrame(corpus_rows)


def anonymise_applications():
    pii_canonical_columns = get_pii_canonical_columns()

    print("PII canonical columns identified from inventory/mapping:")
    for col in sorted(pii_canonical_columns):
        print(f" - {col}")

    with sqlite3.connect(RAW_DATA_DB) as con:
        df = pd.read_sql(
            f"""
            SELECT *
            FROM {INPUT_TABLE}
            """,
            con,
        )

        df = create_anon_ids(df)

        # Scrub free-text fields before saving them anywhere anonymised.
        # for field in FREE_TEXT_FIELDS:
        #     if field in df.columns:
        #         df[field] = df[field].apply(scrub_text)

        drop_columns = [
            col for col in df.columns
            if should_drop_column(col, pii_canonical_columns)
        ]

        anonymised_df = df.drop(columns=drop_columns, errors="ignore")

        corpus_df = build_free_text_corpus(anonymised_df)

        anonymised_df.to_sql(
            OUTPUT_TABLE,
            con,
            if_exists="replace",
            index=False,
        )

        corpus_df.to_sql(
            TEXT_CORPUS_TABLE,
            con,
            if_exists="replace",
            index=False,
        )

    print(f"\nCreated {OUTPUT_TABLE} with {len(anonymised_df)} rows")
    print(f"Created {TEXT_CORPUS_TABLE} with {len(corpus_df)} rows")

    print("\nDropped columns:")
    for col in drop_columns:
        print(f" - {col}")


if __name__ == "__main__":
    anonymise_applications()