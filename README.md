# Applications-Screening

A privacy-conscious pilot data pipeline for Sanctuary Scholarship screening support and planning.

## Project Overview

This project transforms fragmented, multi-year scholarship application records into a consistent analytics-ready dataset to support:

- cleaner and more consistent screening workflows,
- transparent follow-up flags for incomplete applications,
- thematic insight from anonymised free-text responses,
- trend reporting across cycles,
- planning dashboards for demand, capacity, and support needs.

> This pipeline is designed for **decision support**, not decision automation. Human review remains central.

## Why this project exists

Scholarship applications often live across different workbooks, sheet structures, and historical formats. Valuable insight is lost when data cannot be consistently joined and analysed.

This repository provides a practical framework to:

1. inventory source files and structures,
2. standardise fields into a canonical schema,
3. anonymise sensitive data,
4. generate screening quality flags,
5. produce dashboard-ready outputs.

## Scope

### Included
- Data inventory and schema mapping.
- Multi-sheet / multi-file integration by application ID.
- Data quality checks and completeness indicators.
- Anonymisation and privacy-by-design handling.
- Starter pathway for rule-based and AI-assisted thematic tagging on anonymised text.

### Not included
- Automated scholarship decision-making.
- Use of identifiable applicant data in external AI tools.

## Repository Structure

```text
Applications-Screening/
├── README.md
├── data/
│   ├── raw/           # Original source files (do not edit)
│   ├── processed/     # Cleaned and standardised outputs
│   └── anonymised/    # Analysis-ready anonymised outputs
├── docs/
│   ├── data_inventory.xlsx
│   ├── data_dictionary.csv
│   └── column_mapping.csv
└── src/
    ├── 01_profile_raw.py
    ├── 02_map_and_union.py
    └── 03_anonymise.py
```

## Suggested Workflow

1. **Inventory** all files, sheets, and relationships.
2. **Map** source columns to canonical fields.
3. **Ingest + union** yearly records with provenance.
4. **Anonymise** sensitive columns and generate internal IDs.
5. **Flag** missing/inconsistent screening fields.
6. **Tag themes** in anonymised free text with human validation.
7. **Report** in Power BI.

## Data Inventory Model (recommended)

Use a relational inventory workbook with tabs:

- `files` (one row per physical file),
- `tables` (one row per sheet or standalone table),
- `relationships` (table joins via application ID),
- `columns` (one row per column per table),
- `issues_log` (data quality/action tracker).

This structure handles years where referees are in separate files and years where they are in workbook sheets.

## Privacy and Governance Principles

- Remove or mask direct identifiers before analysis.
- Use anonymised applicant IDs.
- Restrict reporting to aggregated insights.
- Keep sensitive raw data in controlled storage.
- Maintain an auditable transformation process.

## Portfolio Positioning

This project demonstrates real-world data science capability in:

- messy multi-source integration,
- reproducible data engineering,
- responsible NLP on sensitive domains,
- analytics communication for non-technical stakeholders,
- governance-aware AI implementation.

## Next Steps

- Add inventory templates and sample mapping files.
- Implement initial profiling, mapping, and anonymisation scripts.
- Add evaluation notebook for thematic tagging agreement.
- Publish dashboard screenshots and methodology notes.

## License

For internal pilot and portfolio demonstration use. Add formal license terms before public release.
