# Sanctuary Pipeline Table Reference Guide

_Generated from the uploaded `data_inventory.xlsx`. Use this as a quick lookup when you forget what T001, T002, etc. mean._

## How to read this

- `T###` = one source sheet or standalone source table from the inventory.
- `core_application` = main application form table, usually one row per application.
- `documents`, `other`, `referees` = child or related tables that attach extra records to applications.
- In SQLite, you can create/use views such as `t001`, `t002`, etc. as friendly shortcuts for the longer `keyed_raw_*` table names.
- For dashboarding, avoid directly joining 1:many child tables into `applications_master`; aggregate them first into counts/flags.

## Quick table catalogue

| Table | File | Year | Kind | Rows est. | What it is | Main use |
|---|---|---:|---|---:|---|---|
| `T001` | `F001` | 2020-2024 | `core_application` | 56 | Main/core application table for the older Waterford Institute of Sanctuary application file. This is a parent application table. | Use for older-cycle application overview, applicant status, course fields, years in Ireland, and the older personal statement text. |
| `T002` | `F001` | 2020-2024 | `documents` | 91 | Previous education/details child table linked to T001. One application can have multiple education rows. | Use to count or inspect previous education records for T001 applications. |
| `T004` | `F002` | 2024-2026 | `core_application` | 144 | Core application table for the 2024–2025 application structure. In this version, many evidence/document fields appear inside the main application table rather than as separate child sheets. | Use for 2024–2025 application-level analysis, including status, years in Ireland, education/work history, course preference, and free-text statements. |
| `T005` | `F003` | 2025-2026 | `core_application` | 26 | Core application table for the 2025–2026 / current application structure. This is the parent table for separate evidence/document upload sheets. | Use for current-cycle application-level analysis, current status, education/work history, English language information, course code/name field, personal statement, course interest statement, review outcome and return reasons. |
| `T006` | `F003` | 2025-2026 | `other` | 11 | English language evidence upload child table for the current application structure. | Use to count whether an applicant uploaded English language evidence. |
| `T007` | `F003` | 2025-2026 | `documents` | 4 | Supporting Documents 3 upload child table for current applications. | Use for document upload count/flagging for T005 applications. |
| `T008` | `F003` | 2025-2026 | `documents` | 17 | Supporting Documents 2 upload child table for current applications. | Use for document upload count/flagging for T005 applications. |
| `T009` | `F003` | 2025-2026 | `documents` | 23 | Supporting Documents upload child table for current applications. | Use for document upload count/flagging for T005 applications. |
| `T010` | `F003` | 2025-2026 | `documents` | 37 | Proof of Current Status upload child table for current applications. | Use to count whether current-cycle applicants uploaded proof of status. |
| `T003` | `F004` | 2024-2025 | `referees` | 87 | Standalone referee form table for the 2024–2025 cycle. | Use only when you want to inspect referee responses/statements separately. |
| `T011` | `F005` | 2023-2024 | `referees` | 34 | Standalone referee form table for the older 2023–2024 cycle. | Use only when you want to inspect referee statements separately. |

## Detailed table notes

### `T001` — SETUWaterfordInstituteOfSanctua

- **File:** `F001` — WIT_20232024Application
- **Year/cycle in inventory:** 2020-2024
- **Kind:** `core_application`
- **Estimated rows:** 56
- **Plain-English meaning:** Main/core application table for the older Waterford Institute of Sanctuary application file. This is a parent application table.
- **Use it for:** Use for older-cycle application overview, applicant status, course fields, years in Ireland, and the older personal statement text.
- **Application/join key columns tagged:** `SETUWaterfordInstituteOfSanctua_Id`
- **Column count in inventory:** 31
- **PII-tagged source columns:** 15
- **Free-text/NLP candidate fields:**
  - `PersonalStatement200Words_WhatWouldTheOpportunityToStudyAtThirdLevelMeanToYou`
- **Parent relationships:**
  - `R001`: `T001` → `T002` on `SETUWaterfordInstituteOfSanctua_Id` = `SETUWaterfordInstituteOfSanctua_Id` (1:many, high) — Previous education rows linked to core application
- **Caution:** Contains direct PII in source columns. Use keyed/anonymised outputs for analysis.

### `T002` — DetailsOfPreviousEducation.Deta

- **File:** `F001` — WIT_20232024Application
- **Year/cycle in inventory:** 2020-2024
- **Kind:** `documents`
- **Estimated rows:** 91
- **Plain-English meaning:** Previous education/details child table linked to T001. One application can have multiple education rows.
- **Use it for:** Use to count or inspect previous education records for T001 applications.
- **Application/join key columns tagged:** `SETUWaterfordInstituteOfSanctua_Id`
- **Column count in inventory:** 6
- **PII-tagged source columns:** 0
- **Free-text/NLP candidate fields:** none tagged in uploaded inventory.
- **Child of:**
  - `R001`: `T001` → `T002` on `SETUWaterfordInstituteOfSanctua_Id` = `SETUWaterfordInstituteOfSanctua_Id` (1:many, high)
- **Caution:** Join to T001 using SETUWaterfordInstituteOfSanctua_Id. Do not directly join into a one-row-per-applicant table without aggregating first, because it is 1:many.

### `T004` — UniversityOfSanctuaryAcademicSc

- **File:** `F002` — UniversityOfSanctuaryAcademicScholarship20252026ApplicationForm
- **Year/cycle in inventory:** 2024-2026
- **Kind:** `core_application`
- **Estimated rows:** 144
- **Plain-English meaning:** Core application table for the 2024–2025 application structure. In this version, many evidence/document fields appear inside the main application table rather than as separate child sheets.
- **Use it for:** Use for 2024–2025 application-level analysis, including status, years in Ireland, education/work history, course preference, and free-text statements.
- **Application/join key columns tagged:** `#`
- **Column count in inventory:** 65
- **PII-tagged source columns:** 45
- **Free-text/NLP candidate fields:**
  - `Duties`
  - `Duties13`
  - `Duties18`
  - `What would the opportunity to study at third level mean to you?`
  - `Course preference`
  - `Please provide a statement indicating what aspects of your chosen course interests you.`
- **Caution:** Uploaded inventory shows the table year as 2024–2026; if you corrected this locally to 2024–2025, keep the Excel inventory and SQLite inventory aligned.

### `T005` — UniversityOfSanctuaryAcademicSc

- **File:** `F003` — UniversityOfSanctuaryAcademicScholarship20262027ApplicationForm - 11.05.2026
- **Year/cycle in inventory:** 2025-2026
- **Kind:** `core_application`
- **Estimated rows:** 26
- **Plain-English meaning:** Core application table for the 2025–2026 / current application structure. This is the parent table for separate evidence/document upload sheets.
- **Use it for:** Use for current-cycle application-level analysis, current status, education/work history, English language information, course code/name field, personal statement, course interest statement, review outcome and return reasons.
- **Application/join key columns tagged:** `UniversityOfSanctuaryAcademicSc_Id`
- **Column count in inventory:** 90
- **PII-tagged source columns:** 58
- **Free-text/NLP candidate fields:**
  - `SubjectsStudied`
  - `SubjectsStudied2`
  - `SubjectsStudied3`
  - `Duties`
  - `Duties2`
  - `Duties3`
  - `PleaseOutlineYourEnglishLanguageProficiency`
  - `WhatWouldTheOpportunityToStudyAtThirdLevelMeanToYou`
  - `PleaseEnterTheCourseCodeOrExactCourseNameYouAppliedToThroughCAO`
  - `PleaseProvideAStatementIndicatingWhatAspectsOfYourChosenCourseInterestsYou`
- **Parent relationships:**
  - `R002`: `T005` → `T006` on `UniversityOfSanctuaryAcademicSc_Id` = `UniversityOfSanctuaryAcademicSc_Id` (4.2361111111111113E-2, high) — English evidence upload
  - `R003`: `T005` → `T007` on `UniversityOfSanctuaryAcademicSc_Id` = `UniversityOfSanctuaryAcademicSc_Id` (1:many, high) — Supporting documents 3
  - `R004`: `T005` → `T008` on `UniversityOfSanctuaryAcademicSc_Id` = `UniversityOfSanctuaryAcademicSc_Id` (1:many, high) — Supporting documents 2
  - `R005`: `T005` → `T009` on `UniversityOfSanctuaryAcademicSc_Id` = `UniversityOfSanctuaryAcademicSc_Id` (1:many, high) — Supporting documents
  - `R006`: `T005` → `T010` on `UniversityOfSanctuaryAcademicSc_Id` = `UniversityOfSanctuaryAcademicSc_Id` (1:many, high) — Proof of current status
- **Caution:** Contains many PII source columns. It is the main parent table for T006–T010.

### `T006` — PleaseUploadEvidenceOfYourEngli

- **File:** `F003` — UniversityOfSanctuaryAcademicScholarship20262027ApplicationForm - 11.05.2026
- **Year/cycle in inventory:** 2025-2026
- **Kind:** `other`
- **Estimated rows:** 11
- **Plain-English meaning:** English language evidence upload child table for the current application structure.
- **Use it for:** Use to count whether an applicant uploaded English language evidence.
- **Application/join key expected by relationships:** `UniversityOfSanctuaryAcademicSc_Id`
- **Column count in inventory:** 14
- **PII-tagged source columns:** 0
- **Free-text/NLP candidate fields:** none tagged in uploaded inventory.
- **Child of:**
  - `R002`: `T005` → `T006` on `UniversityOfSanctuaryAcademicSc_Id` = `UniversityOfSanctuaryAcademicSc_Id` (4.2361111111111113E-2, high)
- **Caution:** Only applicable to the newer/current form structure. Older years should be treated as not applicable, not missing.

### `T007` — SupportingDocuments3

- **File:** `F003` — UniversityOfSanctuaryAcademicScholarship20262027ApplicationForm - 11.05.2026
- **Year/cycle in inventory:** 2025-2026
- **Kind:** `documents`
- **Estimated rows:** 4
- **Plain-English meaning:** Supporting Documents 3 upload child table for current applications.
- **Use it for:** Use for document upload count/flagging for T005 applications.
- **Application/join key columns tagged:** `UniversityOfSanctuaryAcademicSc_Id`
- **Column count in inventory:** 14
- **PII-tagged source columns:** 0
- **Free-text/NLP candidate fields:** none tagged in uploaded inventory.
- **Child of:**
  - `R003`: `T005` → `T007` on `UniversityOfSanctuaryAcademicSc_Id` = `UniversityOfSanctuaryAcademicSc_Id` (1:many, high)
- **Caution:** Aggregate to counts/has_document flags before combining with applications_master.

### `T008` — SupportingDocuments2

- **File:** `F003` — UniversityOfSanctuaryAcademicScholarship20262027ApplicationForm - 11.05.2026
- **Year/cycle in inventory:** 2025-2026
- **Kind:** `documents`
- **Estimated rows:** 17
- **Plain-English meaning:** Supporting Documents 2 upload child table for current applications.
- **Use it for:** Use for document upload count/flagging for T005 applications.
- **Application/join key columns tagged:** `UniversityOfSanctuaryAcademicSc_Id`
- **Column count in inventory:** 14
- **PII-tagged source columns:** 0
- **Free-text/NLP candidate fields:** none tagged in uploaded inventory.
- **Child of:**
  - `R004`: `T005` → `T008` on `UniversityOfSanctuaryAcademicSc_Id` = `UniversityOfSanctuaryAcademicSc_Id` (1:many, high)
- **Caution:** Aggregate to counts/has_document flags before combining with applications_master.

### `T009` — SupportingDocuments

- **File:** `F003` — UniversityOfSanctuaryAcademicScholarship20262027ApplicationForm - 11.05.2026
- **Year/cycle in inventory:** 2025-2026
- **Kind:** `documents`
- **Estimated rows:** 23
- **Plain-English meaning:** Supporting Documents upload child table for current applications.
- **Use it for:** Use for document upload count/flagging for T005 applications.
- **Application/join key columns tagged:** `UniversityOfSanctuaryAcademicSc_Id`
- **Column count in inventory:** 14
- **PII-tagged source columns:** 0
- **Free-text/NLP candidate fields:** none tagged in uploaded inventory.
- **Child of:**
  - `R005`: `T005` → `T009` on `UniversityOfSanctuaryAcademicSc_Id` = `UniversityOfSanctuaryAcademicSc_Id` (1:many, high)
- **Caution:** Aggregate to counts/has_document flags before combining with applications_master.

### `T010` — ProofOfCurrentStatus

- **File:** `F003` — UniversityOfSanctuaryAcademicScholarship20262027ApplicationForm - 11.05.2026
- **Year/cycle in inventory:** 2025-2026
- **Kind:** `documents`
- **Estimated rows:** 37
- **Plain-English meaning:** Proof of Current Status upload child table for current applications.
- **Use it for:** Use to count whether current-cycle applicants uploaded proof of status.
- **Application/join key columns tagged:** `UniversityOfSanctuaryAcademicSc_Id`
- **Column count in inventory:** 14
- **PII-tagged source columns:** 0
- **Free-text/NLP candidate fields:** none tagged in uploaded inventory.
- **Child of:**
  - `R006`: `T005` → `T010` on `UniversityOfSanctuaryAcademicSc_Id` = `UniversityOfSanctuaryAcademicSc_Id` (1:many, high)
- **Caution:** Only applicable to the newer/current form structure. Older years should be treated as not applicable, not missing.

### `T003` — SouthEastTechnologicalUniversit

- **File:** `F004` — 20242025RefereeForm
- **Year/cycle in inventory:** 2024-2025
- **Kind:** `referees`
- **Estimated rows:** 87
- **Plain-English meaning:** Standalone referee form table for the 2024–2025 cycle.
- **Use it for:** Use only when you want to inspect referee responses/statements separately.
- **Application/join key columns tagged:** `SouthEastTechnologicalUniversit_Id`
- **Column count in inventory:** 32
- **PII-tagged source columns:** 21
- **Free-text/NLP candidate fields:**
  - `RefereesDetails_ReferenceStatement`
- **Caution:** Currently not part of the MVP validated joins. Treat as separate until the reference ID relationship to applications is confirmed.

### `T011` — SouthEastTechnologicalUniversit

- **File:** `F005` — WIT_20232024RefereeForm
- **Year/cycle in inventory:** 2023-2024
- **Kind:** `referees`
- **Estimated rows:** 34
- **Plain-English meaning:** Standalone referee form table for the older 2023–2024 cycle.
- **Use it for:** Use only when you want to inspect referee statements separately.
- **Application/join key columns tagged:** `SouthEastTechnologicalUniversit_Id`
- **Column count in inventory:** 34
- **PII-tagged source columns:** 21
- **Free-text/NLP candidate fields:**
  - `RefereesDetails_ReferenceStatement`
- **Caution:** Currently not part of the MVP validated joins. Treat as separate until the reference ID relationship to applications is confirmed.

## Validated MVP relationships

| Relationship | Parent | Child | Join key | Cardinality | Meaning |
|---|---|---|---|---|---|
| `R001` | `T001` | `T002` | `SETUWaterfordInstituteOfSanctua_Id` = `SETUWaterfordInstituteOfSanctua_Id` | `1:many` | Previous education rows linked to core application |
| `R002` | `T005` | `T006` | `UniversityOfSanctuaryAcademicSc_Id` = `UniversityOfSanctuaryAcademicSc_Id` | `4.2361111111111113E-2` | English evidence upload |
| `R003` | `T005` | `T007` | `UniversityOfSanctuaryAcademicSc_Id` = `UniversityOfSanctuaryAcademicSc_Id` | `1:many` | Supporting documents 3 |
| `R004` | `T005` | `T008` | `UniversityOfSanctuaryAcademicSc_Id` = `UniversityOfSanctuaryAcademicSc_Id` | `1:many` | Supporting documents 2 |
| `R005` | `T005` | `T009` | `UniversityOfSanctuaryAcademicSc_Id` = `UniversityOfSanctuaryAcademicSc_Id` | `1:many` | Supporting documents |
| `R006` | `T005` | `T010` | `UniversityOfSanctuaryAcademicSc_Id` = `UniversityOfSanctuaryAcademicSc_Id` | `1:many` | Proof of current status |

## Current pipeline outputs to remember

- `raw_*` tables: direct Excel imports, with provenance metadata.
- `keyed_raw_*` tables: raw tables plus `application_id_raw`, `application_id_std`, and `application_uid`.
- `relationship_validation_results`: output of the relationship validation script.
- `applications_master`: standardised cross-year application table built from mapped core application tables.
- `applications_screening_flags`: dashboard-ready screening support table with missingness flags, child-table counts, and completeness score.

## Notes for future!!

- If you change `data_inventory.xlsx`, rebuild `sanctuary_inventory.sqlite` before rerunning the later scripts.
- If year labels or table names change, rebuild the raw SQLite database fresh to avoid zombie tables.
- For GitHub, keep this reference guide but do not commit real data, raw Excel files, SQLite databases, Power BI files, or applicant free text.
- For NLP, use only anonymised free-text outputs, not raw application text.