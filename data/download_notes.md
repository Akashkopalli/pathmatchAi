# O*NET Occupational Dataset & Data Integrity Policy

## PathMatch AI — SIH25034

### 1. Official Data Source
PathMatch uses the occupational taxonomy defined by the **U.S. Department of Labor O*NET Center**:
- Official Portal: [https://www.onetcenter.org/database.html](https://www.onetcenter.org/database.html)
- Standard Classification: Standard Occupational Classification (SOC) 2018 System.

### 2. Supported Official Raw Files
When importing the full official O*NET database release (e.g. O*NET 29.1+), place the unzipped tab-delimited text files into `data/onet_raw/`:
- `Occupation Data.txt` — SOC codes, titles, and descriptions.
- `Skills.txt` — Occupational skill requirements and importance levels.
- `Knowledge.txt` — Knowledge domain ratings.
- `Work Activities.txt` — Generalized work activities.
- `Technology Skills.txt` — Hot technologies and in-demand software tools.

### 3. Educational Sample Dataset
Per SIH25034 guidelines:
- If official raw files are not downloaded, PathMatch operates using the curated educational sample dataset (`data/sample_occupations.csv`).
- Every record is explicitly tagged:
  - `source`: e.g. `"O*NET 29.1 Educational Reference"`
  - `verification_status`: `"verified_sample"` (or `"official_imported"` when loaded from the full O*NET database).
- **NO INVENTED SOC CODES**: All SOC codes conform to real O*NET structure (e.g. `15-2051.00`, `15-1252.00`).

### 4. Critical Distinction Regarding Internships
- **O*NET provides occupational role profiles**, not live hiring vacancies or corporate postings.
- PathMatch AI recommends **occupational role categories and internship profile alignments**, NOT live employer vacancies.
- Fictional hiring companies, fake salaries, and unverified vacancy counts are strictly forbidden.

