[README.md](https://github.com/user-attachments/files/27854398/README.md)
# CVE Description Completeness Analysis

This repository provides a reproducible experimental pipeline for analyzing the fine-grained completeness of CVE vulnerability descriptions. It compares original CVE descriptions before multi-source supplementation, supplemented CVE descriptions after multi-source aggregation, and manually reviewed validation results. The pipeline is organized around RQ1–RQ4.

---

## 1. Project Objective

This project studies whether CVE description text explicitly covers fine-grained information needed for vulnerability analysis. The target of analysis is not CVSS or CWE metadata itself, but whether the CVE description text clearly expresses each required field.

The experiments are organized into four research questions:

| Research Question | Objective | Main Analyses |
|---|---|---|
| RQ1 | Analyze missingness patterns in original CVE descriptions before supplementation | Field presence rate, category-level completeness, co-missingness patterns |
| RQ2 | Evaluate whether multi-source supplementation improves description completeness | Before/after paired comparison, Gain, FillRate, McNemar test, confidence intervals |
| RQ3 | Analyze fields that remain missing after supplementation | Residual ranking, high-residual sampling, manual attribution and calibration |
| RQ4 | Analyze bias introduced by automatic labeling and the experimental workflow | n10 review, missed recognition, boundary bias, residual overestimation, bias metrics |

---

## 2. Recommended Project Structure

```text
cve_description_study_clean/
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   └── processed/
│       └── .gitkeep
│
├── outputs/
│   └── .gitkeep
│
└── src/
    ├── common/
    │   ├── __init__.py
    │   ├── config.py
    │   ├── fields.py
    │   └── io_utils.py
    │
    ├── rq1/
    │   ├── __init__.py
    │   ├── rq1_field_metrics.py
    │   ├── rq1_category_metrics.py
    │   └── rq1_comissing_analysis.py
    │
    ├── rq2/
    │   ├── __init__.py
    │   ├── rq2_build_paired_dataset.py
    │   ├── rq2_field_metrics.py
    │   ├── rq2_category_metrics.py
    │   ├── rq2_sample_metrics.py
    │   ├── rq2_statistical_tests.py
    │   └── rq2_confidence_intervals.py
    │
    ├── rq3/
    │   ├── __init__.py
    │   ├── rq3_residual_metrics.py
    │   ├── rq3_sample_high_residual.py
    │   └── rq3_manual_calibration.py
    │
    └── rq4/
        ├── __init__.py
        ├── rq4_build_bias_input.py
        ├── rq4_manual_review_summary.py
        └── rq4_bias_metrics.py
```

---

## 3. Directory Descriptions

### 3.1 `data/processed/`

`data/processed/` stores the input data files used by the scripts. The scripts mainly read from this directory by default.

At minimum, place the following files here:

```text
5000cve_before.xlsx
cve_after.xlsx
cve_description.json
```

To run the manual-calibration and bias-analysis parts of RQ3 and RQ4, also place the following manually reviewed files here:

```text
RQ2_n10_manual_review.xlsx
RQ3_manual_review.xlsx
```

---

### 3.2 `outputs/`

`outputs/` stores automatically generated results. After running the scripts, statistical tables, paired datasets, sampling tables, calibration tables, and bias-analysis tables will be saved here.

Do not manually place raw input data in `outputs/`. Files in this directory are usually reproducible and are therefore ignored by Git by default.

---

### 3.3 `src/common/`

`src/common/` contains shared code used by all research-question modules.

| File | Purpose |
|---|---|
| `config.py` | Manages the project root, processed-data directory, and output directory |
| `fields.py` | Defines the 24 fine-grained fields, English labels, category mapping, and display names |
| `io_utils.py` | Provides shared utilities for Excel I/O, directory creation, and binary-field cleaning |
| `__init__.py` | Marks the directory as a Python package so modules can be imported reliably |

---

## 4. Field Taxonomy

This project uses 6 top-level categories and 24 fine-grained fields to evaluate whether CVE descriptions are complete.

### 4.1 Vulnerability Type

| Field Name | Meaning |
|---|---|
| `has_specific_vuln_type` | Specific vulnerability type |
| `has_big_category` | Broad vulnerability category |
| `has_core_feature` | Core vulnerability behavior/feature |
| `has_trigger_condition` | Trigger condition |

### 4.2 Root Cause

| Field Name | Meaning |
|---|---|
| `has_specific_error_point` | Specific error point |
| `has_error_type_attribution` | Error-type attribution |
| `has_direct_program_anomaly` | Direct program anomaly |

### 4.3 Affected Product

| Field Name | Meaning |
|---|---|
| `has_vendor_or_maintainer` | Vendor or maintainer |
| `has_product_name` | Product name |
| `has_affected_version` | Affected version |
| `has_affected_component` | Affected component |
| `has_environment_constraint` | Affected environment or environmental constraint |

### 4.4 Attacker Type

| Field Name | Meaning |
|---|---|
| `has_attacker_identity_type` | Attacker identity type |
| `has_attacker_privilege_traits` | Attacker privilege traits |
| `has_attack_operation_method` | Attack operation method |
| `has_precondition_constraints` | Preconditions or prerequisite constraints |

### 4.5 Impact

| Field Name | Meaning |
|---|---|
| `has_core_impact_type` | Core impact type |
| `has_specific_harm_action` | Specific harmful action |
| `has_harm_constraints` | Constraints on harm or impact |
| `has_followon_escalation_harm` | Follow-on or escalation harm |

### 4.6 Attack Carrier

| Field Name | Meaning |
|---|---|
| `has_vector_general_class` | General carrier/vector class |
| `has_vector_specific_form` | Specific carrier/vector form |
| `has_vector_delivery_method` | Carrier/vector delivery method |
| `has_specific_attack_point` | Specific attack point |

---

## 5. Environment Setup

Python 3.9 or later is recommended.

Install dependencies:

```bash
pip install -r requirements.txt
```

A typical `requirements.txt` contains:

```text
pandas
numpy
openpyxl
xlsxwriter
scipy
pyyaml
```

If no YAML configuration file is used, `pyyaml` is optional.

---

## 6. Input File Requirements

### 6.1 `5000cve_before.xlsx`

This file is the baseline table for CVE descriptions before supplementation.

Recommended path:

```text
data/processed/5000cve_before.xlsx
```

Recommended basic columns:

```text
cve_id
cwe_id
description
```

It must also contain the 24 binary `has_*` fields, for example:

```text
has_specific_vuln_type
has_big_category
has_core_feature
has_trigger_condition
...
has_specific_attack_point
```

Field values should be `0` or `1`.

---

### 6.2 `cve_after.xlsx`

This file contains the CVE description status after multi-source supplementation.

Recommended path:

```text
data/processed/cve_after.xlsx
```

Recommended columns:

```text
cve_id
description
24 has_* fields
```

For RQ2 pairing to work properly, each `cve_id` in `cve_after.xlsx` should be present in `5000cve_before.xlsx`.

---

### 6.3 `cve_description.json`

This file stores multi-source description information for each CVE.

Recommended path:

```text
data/processed/cve_description.json
```

It is mainly used to:

```text
count source_count
extract source_type
provide after/source text snippets for RQ3 sampling
support construction of the RQ4 bias-analysis input table
```

---

## 7. Manual Review Files

RQ3 and RQ4 require manual review. Automatic scripts cannot fully replace human judgment, so some generated tables must be manually completed before later scripts can run.

---

### 7.1 RQ2 n10 Manual Review File

Recommended file name:

```text
data/processed/RQ2_n10_manual_review.xlsx
```

This file reviews abnormal downward transitions in RQ2:

```text
before = 1, after = 0
```

This transition is called `n10`. In principle, after multi-source supplementation, a field should not disappear. Therefore, n10 cases require targeted review.

Recommended core sheet name:

```text
n10_detail
```

Recommended columns:

```text
cve_id
field
field_zh
review_result
suggested_before
suggested_after
review_reason
before_excerpt
after_excerpt
similarity
```

Recommended values for `review_result`:

| Value | Meaning |
|---|---|
| `before_over_broad` | The before label was too broad; before should not have been 1 |
| `after_missed_label` | The after text contains evidence, but after was incorrectly labeled as 0 |
| `boundary_issue` | The field boundary is ambiguous under strict vs. lenient criteria |
| `pairing_issue` | The before/after pair is not a valid matched sample or has a text-pairing issue |

If your existing review file still uses Chinese labels such as `before过宽标注`, `after漏标`, `边界问题`, or `样本配对异常`, either keep the script-compatible mapping in the code or normalize them to the English values above.

---

### 7.2 RQ3 High-Residual Manual Attribution File

Recommended file name:

```text
data/processed/RQ3_manual_review.xlsx
```

This file reviews high-residual field samples that were automatically judged as still missing after supplementation.

The core sheet can be named:

```text
Sheet1
```

or changed in the script if you use another sheet name.

Recommended columns:

```text
cve_id
field_key
field
category
auto_after_status
manual_after_status
attribution_type
evidence_text
comment
```

#### `manual_after_status`

This indicates whether the field is present in the after description after manual review.

| Value | Meaning |
|---|---|
| `0` | The after description does not explicitly express this field |
| `1` | The after description contains clear, direct, and locatable evidence for this field |

#### `attribution_type`

This explains why an automatic residual case occurred.

| Type | Meaning | Corresponding RQ4 Bias |
|---|---|---|
| A | True residual missingness: the merged after description does not explicitly express the field | Not a methodological error |
| B | Implicit or boundary-ambiguous evidence: weak signals exist, but strict criteria cannot label it as 1 | E4 boundary bias |
| C | Granularity mismatch: related information exists but does not meet the required field granularity | E2/E4 granularity or category-boundary bias |
| D | Automatic or annotation missed recognition: the after text contains clear evidence but was originally labeled as 0 | E1 field-presence false negative |

#### `evidence_text`

Fill in the original after-text evidence that supports the manual judgment.

For type A true residual missingness, you may write:

```text
No explicit evidence found.
```

#### `comment`

Use this column for brief notes, for example:

```text
The description only states the vulnerability type but does not specify attacker privileges.
```

or:

```text
The text contains a related clue, but the granularity is insufficient for a strict positive label.
```

---

## 8. How to Run

### Run step by step

Running step by step is recommended if you want to inspect intermediate outputs.

#### RQ1

```bash
python src/rq1/rq1_field_metrics.py
python src/rq1/rq1_category_metrics.py
python src/rq1/rq1_comissing_analysis.py
```

#### RQ2

```bash
python src/rq2/rq2_build_paired_dataset.py
python src/rq2/rq2_field_metrics.py
python src/rq2/rq2_category_metrics.py
python src/rq2/rq2_sample_metrics.py
python src/rq2/rq2_statistical_tests.py
python src/rq2/rq2_confidence_intervals.py
```

#### RQ3

```bash
python src/rq3/rq3_residual_metrics.py
python src/rq3/rq3_sample_high_residual.py
```

After the high-residual sampling table is generated, manually fill in the review columns.

After manual review is completed, run:

```bash
python src/rq3/rq3_manual_calibration.py
```

#### RQ4

```bash
python src/rq4/rq4_build_bias_input.py
python src/rq4/rq4_manual_review_summary.py
python src/rq4/rq4_bias_metrics.py
```

---

## 9. Script Descriptions

### 9.1 RQ1 Scripts

#### `rq1_field_metrics.py`

Purpose: Compute the presence rate and missing rate of each fine-grained field in original CVE descriptions before supplementation.

Input:

```text
data/processed/5000cve_before.xlsx
```

Output:

```text
outputs/rq1_field_metrics.xlsx
```

Main sheet:

```text
field_metrics
```

---

#### `rq1_category_metrics.py`

Purpose: Compute category-level average presence rate, full-presence ratio, full-missing ratio, ratio of samples missing at least half of category fields, and per-CVE category missing counts.

Input:

```text
data/processed/5000cve_before.xlsx
```

Output:

```text
outputs/rq1_category_metrics.xlsx
```

Main sheets:

```text
category_metrics
missing_distribution
per_cve_category
```

---

#### `rq1_comissing_analysis.py`

Purpose: Analyze whether fields tend to be missing together. It computes co-missing count, co-missing rate, Jaccard similarity, and phi coefficient.

Input:

```text
data/processed/5000cve_before.xlsx
```

Output:

```text
outputs/rq1_comissing_analysis.xlsx
```

Main sheets:

```text
all_field_pairs
top_phi_pairs
phi_matrix
comissing_rate_matrix
```

---

### 9.2 RQ2 Scripts

#### `rq2_build_paired_dataset.py`

Purpose: Build a before/after paired dataset by inner joining the before and after tables on `cve_id`.

Inputs:

```text
data/processed/5000cve_before.xlsx
data/processed/cve_after.xlsx
```

Output:

```text
outputs/rq2_paired_dataset.xlsx
```

Main sheets:

```text
paired_dataset
pairing_summary
```

---

#### `rq2_field_metrics.py`

Purpose: Compute before completeness, after completeness, Gain, FillRate, ResidualMiss, DropRate, and the 2×2 transition table for each field.

Output:

```text
outputs/rq2_field_metrics.xlsx
```

Main sheets:

```text
field_metrics
abnormal_drop_fields
```

---

#### `rq2_category_metrics.py`

Purpose: Aggregate before/after average completeness, category-level Gain, and changes in category-level missing counts across the six top-level categories.

Output:

```text
outputs/rq2_category_metrics.xlsx
```

Main sheets:

```text
category_metrics
missing_distribution
category_sample_gain
```

---

#### `rq2_sample_metrics.py`

Purpose: Analyze sample-level changes in the number of covered fields for each CVE before and after supplementation.

Output:

```text
outputs/rq2_sample_metrics.xlsx
```

Main sheets:

```text
sample_metrics
gain_distribution
stratified_gain
```

---

#### `rq2_statistical_tests.py`

Purpose: Run McNemar tests for each field and extract n10 abnormal-drop fields and samples.

Output:

```text
outputs/rq2_statistical_tests.xlsx
```

Main sheets:

```text
mcnemar_results
abnormal_drop_fields
abnormal_drop_samples
category_review
```

---

#### `rq2_confidence_intervals.py`

Purpose: Estimate 95% confidence intervals for field-level, category-level, and sample-level gains.

Output:

```text
outputs/rq2_confidence_intervals.xlsx
```

Main sheets:

```text
field_ci
category_ci
sample_ci
```

---

### 9.3 RQ3 Scripts

#### `rq3_residual_metrics.py`

Purpose: Compute the residual missing rate for each field based on after status and identify high-residual fields.

Inputs:

```text
outputs/rq2_paired_dataset.xlsx
data/processed/cve_description.json
```

Output:

```text
outputs/rq3_residual_metrics.xlsx
```

Main sheets:

```text
after_status
field_residual
high_residual_fields
category_residual
source_count_aux
```

---

#### `rq3_sample_high_residual.py`

Purpose: Sample high-residual field cases for manual review.

Output:

```text
outputs/rq3_high_residual_samples.xlsx
```

Main sheets:

```text
manual_samples
field_sample_summary
```

After this file is generated, manually fill in the review columns. Save the reviewed file as:

```text
data/processed/RQ3_manual_review.xlsx
```

---

#### `rq3_manual_calibration.py`

Purpose: Read manual review results, summarize A/B/C/D attribution, and calculate manually calibrated residuals.

Inputs:

```text
data/processed/RQ3_manual_review.xlsx
outputs/rq3_residual_metrics.xlsx
```

Output:

```text
outputs/rq3_manual_calibration.xlsx
```

Main sheets:

```text
overall_attribution
by_field
by_category
manual_samples
```

---

### 9.4 RQ4 Scripts

#### `rq4_build_bias_input.py`

Purpose: Integrate RQ2 paired results, n10 review, and RQ3 manual attribution results into a CVE×field-level bias-analysis input table.

Inputs:

```text
outputs/rq2_paired_dataset.xlsx
outputs/rq2_statistical_tests.xlsx
data/processed/RQ2_n10_manual_review.xlsx
data/processed/RQ3_manual_review.xlsx
outputs/rq3_manual_calibration.xlsx
```

Output:

```text
outputs/rq4_bias_input.xlsx
```

Main sheets:

```text
bias_input
field_metadata
```

---

#### `rq4_manual_review_summary.py`

Purpose: Summarize the RQ2 n10 review and RQ3 manual attribution results as evidence for RQ4 bias analysis.

Output:

```text
outputs/rq4_manual_review_summary.xlsx
```

Main sheets:

```text
rq3_attribution_summary
rq3_by_field
rq3_by_category
n10_review_summary
n10_by_field
n10_by_category
```

---

#### `rq4_bias_metrics.py`

Purpose: Compute core RQ4 bias metrics, including E1/E2/E4 rates, true residual rate, residual overestimation rate, and n10 method-explanation rate.

Output:

```text
outputs/rq4_bias_metrics.xlsx
```

Main sheets:

```text
bias_metrics
rq3_field_bias
n10_bias
```

---

## 10. Output Files

| File | Description |
|---|---|
| `rq1_field_metrics.xlsx` | RQ1 field-level presence rates |
| `rq1_category_metrics.xlsx` | RQ1 category-level missingness structure |
| `rq1_comissing_analysis.xlsx` | RQ1 field co-missingness analysis |
| `rq2_paired_dataset.xlsx` | RQ2 before/after paired dataset |
| `rq2_field_metrics.xlsx` | RQ2 field-level supplementation effects |
| `rq2_category_metrics.xlsx` | RQ2 category-level supplementation effects |
| `rq2_sample_metrics.xlsx` | RQ2 sample-level supplementation gains |
| `rq2_statistical_tests.xlsx` | RQ2 McNemar tests and n10 extraction |
| `rq2_confidence_intervals.xlsx` | RQ2 confidence intervals |
| `rq3_residual_metrics.xlsx` | RQ3 residual metrics |
| `rq3_high_residual_samples.xlsx` | RQ3 high-residual manual sampling table |
| `rq3_manual_calibration.xlsx` | RQ3 manual attribution and calibration results |
| `rq4_bias_input.xlsx` | RQ4 bias-analysis input table |
| `rq4_manual_review_summary.xlsx` | RQ4 manual review summary |
| `rq4_bias_metrics.xlsx` | RQ4 bias metrics |

---

## 11. Notes on GitHub Release

The repository is intended to publish code and reproducible workflow logic. Large data files, complete manual review files, and generated output workbooks should normally not be committed unless you explicitly decide to release them.

Recommended `.gitignore` behavior:

```text
data/processed/*
outputs/*
*.xlsx
*.csv
*.json
__pycache__/
*.pyc
```

Keep `.gitkeep` files if you want GitHub to preserve empty directories such as `data/processed/` and `outputs/`.

---

## 12. Common Issues

### Missing input files

If a script reports that an input file cannot be found, check whether the required files are placed under:

```text
data/processed/
```

### Missing required columns

If a script reports missing columns, make sure that `5000cve_before.xlsx` and `cve_after.xlsx` contain `cve_id`, `description`, and all 24 `has_*` fields.

### RQ3 or RQ4 cannot run completely

RQ3 and RQ4 depend on manually reviewed files. Run the automatic sampling step first, complete the manual review columns, save the reviewed workbook to `data/processed/`, and then run the calibration or bias-analysis scripts.

### Chinese manual-review labels in older workbooks

If older review workbooks use Chinese labels, either normalize them to English or keep a mapping in the script. For public GitHub release, English labels are recommended.

