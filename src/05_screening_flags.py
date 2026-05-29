import re
import sqlite3
import pandas as pd

from config import RAW_DATA_DB


OUTPUT_TABLE = "applications_screening_flags"


CHILD_TABLE_FLAGS = {
    "T002": "previous_education",
    "T006": "english_evidence",
    "T007": "supporting_documents_3",
    "T008": "supporting_documents_2",
    "T009": "supporting_documents",
    "T010": "proof_current_status",
}
PERSONAL_STATEMENT_FIELDS = [
    "personal_statement_meaning_of_study",
    "course_interest_statement",
]

REQUIRED_FIELDS_BY_TABLE = {
    "T001": [
        "course_name",
        "course_code",
        "years_in_ireland",
        "current_status",
        "personal_statement",
    ],
    "T004": [
        "course_code",
        "years_in_ireland",
        "current_status",
    ],
    "T005": [
        "course_code",
        "years_in_ireland",
        "current_status",
    ],
}

def is_missing(value):
    """Return True if a value is blank/null/meaningless."""
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


def get_keyed_table_map(con):
    """Map T001/T005/etc. to actual keyed table names."""
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


def add_basic_missing_flags(df):
    """Create missingness flags only where the field was expected on that form."""

    all_possible_fields = {
        "course_name",
        "course_code",
        "years_in_ireland",
        "current_status",
        "personal_statement",
    }

    for field in all_possible_fields:
        flag_name = f"flag_missing_{field}"
        df[flag_name] = pd.NA

        for table_id, required_fields in REQUIRED_FIELDS_BY_TABLE.items():
            mask = df["_source_table_id"] == table_id

            if field in required_fields:
                if field in df.columns:
                    df.loc[mask, flag_name] = df.loc[mask, field].apply(is_missing)
                else:
                    df.loc[mask, flag_name] = True
            else:
                df.loc[mask, flag_name] = pd.NA

    return df


def add_child_table_counts(df, con):
    """
    Add counts/has flags from child tables:
    documents, proof of status, education evidence, etc.
    """
    keyed_table_map = get_keyed_table_map(con)

    for table_id, label in CHILD_TABLE_FLAGS.items():
        child_table = keyed_table_map.get(table_id)

        count_col = f"{label}_count"
        has_col = f"has_{label}"

        # Default values
        df[count_col] = 0
        df[has_col] = False

        if child_table is None:
            print(f"Skipping {table_id}: no keyed child table found")
            continue

        child_df = pd.read_sql(
            f'SELECT application_uid FROM "{child_table}"',
            con,
        )

        if "application_uid" not in child_df.columns:
            print(f"Skipping {table_id}: no application_uid column")
            continue

        counts = child_df["application_uid"].value_counts()

        df[count_col] = (
            df["application_uid"]
            .map(counts)
            .fillna(0)
            .astype(int)
        )

        df[has_col] = df[count_col] > 0

        print(f"Added {count_col} from {child_table}")

    return df
    


def add_document_flags(df):
    """Create higher-level screening flags from child table counts."""

    df["flag_missing_any_supporting_document"] = (
        (df.get("supporting_documents_count", 0) == 0)
        & (df.get("supporting_documents_2_count", 0) == 0)
        & (df.get("supporting_documents_3_count", 0) == 0)
    )

    df["flag_missing_proof_current_status"] = (
        df.get("proof_current_status_count", 0) == 0
    )

    df["flag_missing_english_evidence"] = (
        df.get("english_evidence_count", 0) == 0
    )

    df["flag_missing_previous_education"] = (
        df.get("previous_education_count", 0) == 0
    )

    return df

def add_personal_statement_group_flags(df):
    """
    Treat all personal statement / course interest text fields as one NLP text group.
    Creates:
    - personal_statement_fields_applicable
    - personal_statement_fields_missing
    - flag_missing_all_personal_statement_text
    - flag_missing_any_personal_statement_text
    """

    available_fields = [
        col for col in PERSONAL_STATEMENT_FIELDS
        if col in df.columns
    ]

    df["personal_statement_fields_applicable"] = len(available_fields)

    if not available_fields:
        df["personal_statement_fields_missing"] = pd.NA
        df["flag_missing_all_personal_statement_text"] = pd.NA
        df["flag_missing_any_personal_statement_text"] = pd.NA
        return df

    missing_matrix = df[available_fields].map(is_missing)

    df["personal_statement_fields_missing"] = missing_matrix.sum(axis=1)

    df["flag_missing_all_personal_statement_text"] = (
        df["personal_statement_fields_missing"] == len(available_fields)
    )

    df["flag_missing_any_personal_statement_text"] = (
        df["personal_statement_fields_missing"] > 0
    )

    return df

def add_completeness_score(df):
    """Calculate a simple completeness score from available flags."""

    flag_cols = [
        col for col in df.columns
        if col.startswith("flag_missing_")
    ]

    # Only use boolean flags, ignore NA-only columns
    usable_flags = [
        col for col in flag_cols
        if df[col].dropna().isin([True, False]).all()
    ]

    if not usable_flags:
        df["missing_flag_count"] = 0
        df["completeness_score"] = pd.NA
        return df

    df["missing_flag_count"] = df[usable_flags].sum(axis=1)

    df["completeness_score"] = (
        1 - (df["missing_flag_count"] / len(usable_flags))
    ).round(3)

    return df


def build_screening_flags():
    with sqlite3.connect(RAW_DATA_DB) as con:
        df = pd.read_sql(
            """
            SELECT *
            FROM applications_master
            """,
            con,
        )

        df = add_basic_missing_flags(df)
        df = add_personal_statement_group_flags(df)
        df = add_child_table_counts(df, con)
        df = add_document_flags(df)
        df = add_completeness_score(df)
        

        df.to_sql(
            OUTPUT_TABLE,
            con,
            if_exists="replace",
            index=False,
        )

    print(f"Created {OUTPUT_TABLE} with {len(df)} rows")


if __name__ == "__main__":
    build_screening_flags()