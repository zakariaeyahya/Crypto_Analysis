# Dataset Cleaning Report

This document summarizes the data cleaning pipeline applied to the raw dataset to prepare it for Natural Language Processing (NLP) analysis.

---

## 🧹 Cleaning Summary

The pipeline processed an initial dataset of 28,731 rows. After applying all cleaning steps, 1,593 rows (5.54%) were removed, resulting in a final, clean dataset of 27,138 rows (94.46% of the original).

### Overall Statistics
* **Initial Rows:** 28,731
* **Final Rows:** 27,138
* **Total Rows Removed:** 1,593 (5.54%)
* **Total Rows Retained:** 94.46%

### Breakdown of Removed Rows
The following table details the specific criteria for row removal and the number of rows affected by each rule.

| Removal Criterion | Rows Removed | Notes |
| :--- | :--- | :--- |
| **Too short (<10 chr)** | 1,158 | Removed posts/comments with fewer than 10 characters. |
| **Bot accounts** | 334 | Identified and removed posts from suspected bot accounts. |
| **Post-cleaning short** | 101 | Removed rows that became too short after other cleaning steps (e.g., URL/emoji removal). |
| **Invalid dates** | 0 | All date entries were valid. |
| **Missing critical data** | 0 | No rows were missing essential data (e.g., body text, author). |
| **Exact duplicates** | 0 | No duplicate rows were found. |
| **High-freq posters** | 0 | No authors were flagged for excessive posting frequency. |
| **Repeated spam** | 0 | No instances of repeated spam content were found. |
| **Total Removed** | **1,593** | |

---

## 📊 Final Dataset Statistics

The resulting clean dataset has the following characteristics:

* **Total Records:** 27,138
* **Content Breakdown:**
    * Posts: 2,225
    * Comments: 24,913
* **Unique Authors:** 12,802
* **Date Range:** 2025-09-29 22:06:41 to 2025-11-01 14:23:34
* **Average Text Length:** 155.6 characters
* **Final Memory Usage:** 17.27 MB

---

## ✅ Status

**CLEANING PIPELINE COMPLETED SUCCESSFULLY**

The dataset is now considered clean, validated, and ready for NLP analysis.