# SQL Query Cheatsheet for Applications Screening Pipeline

These queries are for checking each stage of the scholarship application pipeline in DB Browser for SQLite.

---

## 1. Inventory database checks

Use these on:

```text
sanctuary_inventory.sqlite
```

### Check inventory tables exist

```sql
SELECT name
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;
```

### Check file inventory

```sql
SELECT *
FROM inventory_files;
```

### Check table inventory

```sql
SELECT 
    table_id,
    file_id,
    year,
    table_name,
    table_kind
FROM inventory_tables
ORDER BY table_id;
```

### Check application ID columns

```sql
SELECT 
    table_id,
    column_name_raw,
    type
FROM inventory_columns
WHERE LOWER(TRIM(type)) = 'is_application_id'
ORDER BY table_id;
```

### Check free-text / NLP candidate fields

```sql
SELECT 
    table_id,
    column_name_raw,
    type
FROM inventory_columns
WHERE LOWER(TRIM(type)) = 'is_free_text'
ORDER BY table_id;
```

### Check relationships

```sql
SELECT *
FROM inventory_relationships
ORDER BY rel_id;
```

---

## 2. Raw import checks

Use these on:

```text
sanctuary_raw_import.sqlite
```

### List all raw imported tables

```sql
SELECT name
FROM sqlite_master
WHERE type = 'table'
AND name LIKE 'raw%'
ORDER BY name;
```

### Check raw table row counts

```sql
SELECT 
    'raw2020_2024_t001_setuwaterfordinstituteofsanctua' AS table_name,
    COUNT(*) AS rows
FROM raw2020_2024_t001_setuwaterfordinstituteofsanctua

UNION ALL

SELECT 
    'raw2025_2026_t005_universityofsanctuaryacademicsc',
    COUNT(*)
FROM raw2025_2026_t005_universityofsanctuaryacademicsc;
```

### Check imported provenance columns

```sql
SELECT 
    _source_file_id,
    _source_file_name,
    _source_table_id,
    _source_sheet_name,
    _source_year,
    _source_row_number
FROM raw2025_2026_t005_universityofsanctuaryacademicsc
LIMIT 20;
```

---

## 3. Keyed table checks

### List all keyed tables

```sql
SELECT name
FROM sqlite_master
WHERE type = 'table'
AND name LIKE 'keyed_%'
ORDER BY name;
```

### Check generated application IDs

```sql
SELECT 
    application_id_raw,
    application_id_std,
    application_uid,
    _source_year,
    _source_table_id
FROM keyed_raw2025_2026_t005_universityofsanctuaryacademicsc
LIMIT 20;
```

### Check duplicate application UIDs in a core table

```sql
SELECT 
    application_uid,
    COUNT(*) AS count
FROM keyed_raw2025_2026_t005_universityofsanctuaryacademicsc
GROUP BY application_uid
HAVING COUNT(*) > 1;
```

### Check duplicate application UIDs across applications master later

```sql
SELECT 
    application_uid,
    COUNT(*) AS count
FROM applications_master
GROUP BY application_uid
HAVING COUNT(*) > 1;
```

---

## 4. Relationship validation checks

### View relationship validation results

```sql
SELECT *
FROM relationship_validation_results
ORDER BY rel_id;
```

### Summarise relationship statuses

```sql
SELECT 
    status,
    COUNT(*) AS relationship_count
FROM relationship_validation_results
GROUP BY status;
```

### Check failed or warning relationships

```sql
SELECT *
FROM relationship_validation_results
WHERE status <> 'pass'
ORDER BY rel_id;
```

### Check match rates

```sql
SELECT 
    rel_id,
    parent_table_id,
    child_table_id,
    parent_rows,
    child_rows,
    matched_child_rows,
    orphan_child_rows,
    child_match_rate,
    detected_cardinality
FROM relationship_validation_results
ORDER BY rel_id;
```

---

## 5. Applications master checks

### Preview applications master

```sql
SELECT *
FROM applications_master
LIMIT 20;
```

### Count applications by year

```sql
SELECT 
    _source_year,
    COUNT(*) AS applications
FROM applications_master
GROUP BY _source_year
ORDER BY _source_year;
```

### Count applications by source table

```sql
SELECT 
    _source_table_id,
    _source_year,
    COUNT(*) AS applications
FROM applications_master
GROUP BY _source_table_id, _source_year
ORDER BY _source_year, _source_table_id;
```

### Check mapped fields

```sql
SELECT 
    application_uid,
    _source_year,
    _source_table_id,
    course_name,
    course_code,
    course_preference,
    years_in_ireland,
    current_status
FROM applications_master
LIMIT 30;
```

### Check free-text fields for NLP

```sql
SELECT 
    application_uid,
    _source_year,
    personal_statement_meaning_of_study,
    course_interest_statement
FROM applications_master
WHERE personal_statement_meaning_of_study IS NOT NULL
   OR course_interest_statement IS NOT NULL
LIMIT 30;
```

---

## 6. Screening flags checks

### Preview screening table

```sql
SELECT *
FROM applications_screening_flags
LIMIT 20;
```

### Summary by year

```sql
SELECT 
    _source_year,
    COUNT(*) AS applications,
    ROUND(AVG(completeness_score), 3) AS avg_completeness,
    COALESCE(SUM(flag_missing_course_name), 0) AS missing_course_name,
    COALESCE(SUM(flag_missing_proof_current_status), 0) AS missing_status_proof
FROM applications_screening_flags
GROUP BY _source_year
ORDER BY _source_year;
```

### Better QA version: applicable vs missing

```sql
SELECT 
    _source_year,
    COUNT(*) AS applications,

    SUM(CASE WHEN flag_missing_course_name IS NOT NULL THEN 1 ELSE 0 END) AS course_name_applicable,
    SUM(CASE WHEN flag_missing_course_name = 1 THEN 1 ELSE 0 END) AS course_name_missing,

    SUM(CASE WHEN flag_missing_proof_current_status IS NOT NULL THEN 1 ELSE 0 END) AS proof_status_applicable,
    SUM(CASE WHEN flag_missing_proof_current_status = 1 THEN 1 ELSE 0 END) AS proof_status_missing,

    ROUND(AVG(completeness_score), 3) AS avg_completeness

FROM applications_screening_flags
GROUP BY _source_year
ORDER BY _source_year;
```

### Personal statement / NLP text coverage

```sql
SELECT 
    _source_year,
    COUNT(*) AS applications,
    SUM(personal_statement_fields_applicable) AS text_fields_expected,
    SUM(personal_statement_fields_missing) AS text_fields_missing,
    COALESCE(SUM(flag_missing_all_personal_statement_text), 0) AS missing_all_text,
    COALESCE(SUM(flag_missing_any_personal_statement_text), 0) AS missing_any_text
FROM applications_screening_flags
GROUP BY _source_year
ORDER BY _source_year;
```

### Most incomplete applications

```sql
SELECT 
    application_uid,
    _source_year,
    _source_table_id,
    completeness_score,
    missing_flag_count
FROM applications_screening_flags
ORDER BY completeness_score ASC
LIMIT 20;
```

### Document/proof counts

```sql
SELECT 
    application_uid,
    _source_year,
    proof_current_status_count,
    english_evidence_count,
    supporting_documents_count,
    supporting_documents_2_count,
    supporting_documents_3_count
FROM applications_screening_flags
WHERE _source_table_id = 'T005'
LIMIT 30;
```

---

## 7. Quick dashboard-ready queries

### Applications over time

```sql
SELECT 
    _source_year,
    COUNT(*) AS applications
FROM applications_screening_flags
GROUP BY _source_year
ORDER BY _source_year;
```

### Average completeness by year

```sql
SELECT 
    _source_year,
    ROUND(AVG(completeness_score), 3) AS avg_completeness
FROM applications_screening_flags
GROUP BY _source_year
ORDER BY _source_year;
```

### Current status breakdown

```sql
SELECT 
    _source_year,
    current_status,
    COUNT(*) AS applications
FROM applications_screening_flags
GROUP BY _source_year, current_status
ORDER BY _source_year, applications DESC;
```

### Course code / preference demand

```sql
SELECT 
    _source_year,
    COALESCE(course_code, course_preference) AS course_field,
    COUNT(*) AS applications
FROM applications_screening_flags
WHERE COALESCE(course_code, course_preference) IS NOT NULL
GROUP BY _source_year, COALESCE(course_code, course_preference)
ORDER BY _source_year, applications DESC;
```

---

## 8. NLP preparation checks

### Extract rows with usable text

```sql
SELECT 
    application_uid,
    _source_year,
    personal_statement_meaning_of_study,
    course_interest_statement
FROM applications_screening_flags
WHERE personal_statement_meaning_of_study IS NOT NULL
   OR course_interest_statement IS NOT NULL;
```

### Count text availability by year

```sql
SELECT 
    _source_year,
    COUNT(*) AS applications,
    SUM(CASE WHEN personal_statement_meaning_of_study IS NOT NULL THEN 1 ELSE 0 END) AS has_meaning_statement,
    SUM(CASE WHEN course_interest_statement IS NOT NULL THEN 1 ELSE 0 END) AS has_course_interest_statement
FROM applications_screening_flags
GROUP BY _source_year
ORDER BY _source_year;
```

### Find very short text responses

```sql
SELECT 
    application_uid,
    _source_year,
    LENGTH(personal_statement_meaning_of_study) AS meaning_statement_length,
    personal_statement_meaning_of_study
FROM applications_screening_flags
WHERE personal_statement_meaning_of_study IS NOT NULL
ORDER BY meaning_statement_length ASC
LIMIT 20;
```

---

## 9. Safety checks before Power BI

### Confirm no obvious direct identifiers in master table columns

```sql
PRAGMA table_info(applications_master);
```

Look for columns like:

```text
name
email
phone
address
cao_number
student_id
signature
```

These should not go into public/demo outputs.

### Check which tables exist before connecting Power BI

```sql
SELECT name
FROM sqlite_master
WHERE type IN ('table', 'view')
ORDER BY name;
```

For Power BI, the main tables are:

```text
applications_master
applications_screening_flags
relationship_validation_results
```

For later NLP:

```text
free_text_corpus
theme_tags
```
