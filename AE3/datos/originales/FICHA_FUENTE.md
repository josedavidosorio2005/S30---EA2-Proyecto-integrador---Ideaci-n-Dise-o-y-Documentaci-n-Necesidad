---
license: mit
task_categories:
  - tabular-classification
  - tabular-regression
language:
  - en
tags:
  - cafe
  - sales
  - transactions
  - data-cleaning
  - retail
  - tabular
size_categories:
  - 1K<n<10K
---

# ☕ Cafe Sales Dataset (Cleaned)

A cleaned and preprocessed version of a synthetic cafe sales transaction dataset. Originally a **dirty, real-world-style dataset** riddled with missing values, corrupt entries, and wrong data types — now fully cleaned and ready for analysis or ML tasks.

---

![Cafe Sales Dataset – Before vs After Cleaning](README_Image.png)

---

## 📋 Dataset Overview

| Property | Value |
|---|---|
| **Original Rows** | 10,000 |
| **Cleaned Rows** | 9,540 |
| **Columns** | 8 |
| **Time Period** | January 2023 – December 2023 |
| **Domain** | Retail / Food & Beverage |

---

## 📁 Files

| File | Description |
|---|---|
| `cleaned_cafe_sales.csv` | Final cleaned dataset, ready for use |
| `dirty_cafe_sales.csv` | Original raw dataset with all issues intact |
| `cafe_data_cleaning.ipynb` | Full cleaning pipeline notebook (step-by-step) |

---

## 🗂️ Column Description

| Column | Type | Description |
|---|---|---|
| `Transaction ID` | string | Unique identifier for each transaction (e.g., `TXN_1961373`) |
| `Item` | string | Menu item purchased (`Coffee`, `Tea`, `Cake`, `Cookie`, `Sandwich`, `Salad`, `Juice`, `Smoothie`) |
| `Quantity` | float | Number of units purchased (1–5) |
| `Price Per Unit` | float | Price of a single unit in USD (1.0–5.0) |
| `Total Spent` | float | Total transaction amount = `Quantity × Price Per Unit` |
| `Payment Method` | string | Payment type used (`Cash`, `Credit Card`, `Digital Wallet`) |
| `Location` | string | Where the order was placed (`In-store`, `Takeaway`, `Unknown`) |
| `Transaction Date` | string | Date of transaction in `YYYY-MM-DD` format |

---

## 🧹 Data Cleaning — What Was Wrong & How It Was Fixed

The raw dataset had several real-world data quality issues. Here's a complete breakdown:

### 1. Corrupt String Values (`"ERROR"` and `"UNKNOWN"`)
**Problem:** Multiple columns contained `"ERROR"` and `"UNKNOWN"` strings instead of actual values or proper nulls. These were scattered across `Item`, `Quantity`, `Price Per Unit`, `Total Spent`, `Payment Method`, and `Location`.

**Fix:** All `"ERROR"` and `"UNKNOWN"` strings were replaced with `NaN` (proper missing values) using `df.replace(["ERROR", "UNKNOWN"], np.nan)`.

**Impact after replacement:**

| Column | Missing Before Replace | Missing After Replace |
|---|---|---|
| Item | 333 | 969 |
| Quantity | 138 | 479 |
| Price Per Unit | 179 | 533 |
| Total Spent | 173 | 502 |
| Payment Method | 2,579 | 3,178 |
| Location | 3,265 | 3,961 |
| Transaction Date | 159 | 460 |

---

### 2. Wrong Data Types
**Problem:** All numeric columns (`Quantity`, `Price Per Unit`, `Total Spent`) were loaded as `object/str` dtype because of the corrupt string values mixed in.

**Fix:** Converted all three to `float64` using `pd.to_numeric(..., errors='coerce')`, which automatically turned any remaining non-numeric values into `NaN`.

---

### 3. Missing Values in Categorical Columns
**Problem:** `Item`, `Payment Method`, and `Location` had significant missing data (up to ~32–40%).

**Fix:**
- `Item` → filled with **mode** (most frequent value)
- `Payment Method` → filled with **mode** (most frequent value)
- `Location` → filled with `"Unknown"` (a distinct, interpretable label rather than imputing a false value, since ~40% was missing — too high to impute reliably)

---

### 4. Missing Values in Numeric Columns
**Problem:** `Quantity` (479 missing) and `Price Per Unit` (533 missing) had nulls after type conversion.

**Fix:** Both filled with their respective **medians** (both were `3.0`), which is robust against skew and the limited range of values (1–5).

---

### 5. Missing `Total Spent` — Derived Column Recovery
**Problem:** 502 rows had missing `Total Spent`.

**Fix:** Since `Total Spent = Quantity × Price Per Unit` was a deterministic relationship (verified — 0 mismatches existed in rows where all three were present), missing values were **recalculated** directly: `df["Total Spent"] = df["Total Spent"].fillna(df["Quantity"] * df["Price Per Unit"])`.

---

### 6. Missing & Invalid `Transaction Date`
**Problem:** 460 rows had missing or invalid dates (including `"ERROR"` strings parsed as `NaT`).

**Fix:** Parsed the column to `datetime64` using `pd.to_datetime(..., errors='coerce')`, then **dropped all rows** where the date was null. Dates are a critical anchor for time-series analysis — imputing fake dates would corrupt temporal patterns.

**Result:** 10,000 → **9,540 rows** after dropping 460 undated rows.

---

### 7. `Total Spent` Consistency Recheck
**Problem:** After all imputations, a final audit revealed **696 rows** where `Total Spent` didn't match `Quantity × Price Per Unit` (due to median-filled values for `Quantity`/`Price Per Unit` changing the expected total).

**Fix:** Recomputed `Total Spent` from scratch for all rows: `df["Total Spent"] = df["Quantity"] * df["Price Per Unit"]`. This guarantees 100% internal consistency.

---

### 8. Duplicate Check
**Problem:** Potential duplicate rows or duplicate `Transaction ID`s.

**Result:** ✅ 0 duplicate rows. ✅ 0 duplicate Transaction IDs. No action needed.

---

### 9. Whitespace in Categorical Columns
**Fix:** Applied `.str.strip()` to `Item`, `Payment Method`, and `Location` to remove any leading/trailing spaces.

---

## ✅ Final Dataset Stats

```
Shape: (9540, 8)
Missing values: 0 in all columns
Duplicate rows: 0
Duplicate Transaction IDs: 0
Total Spent mismatches: 0
```

**Data Types:**
```
Transaction ID       str
Item                 str
Quantity             float64
Price Per Unit       float64
Total Spent          float64
Payment Method       str
Location             str
Transaction Date     str (YYYY-MM-DD)
```

---

## 📊 Value Distributions (Cleaned Data)

**Item:**
| Item | Count |
|---|---|
| Juice | 2,051 |
| Coffee | 1,123 |
| Salad | 1,099 |
| Cake | 1,082 |
| Sandwich | 1,075 |
| Smoothie | 1,048 |
| Cookie | 1,035 |
| Tea | 1,027 |

**Payment Method:**
| Method | Count |
|---|---|
| Digital Wallet | 5,212 |
| Credit Card | 2,170 |
| Cash | 2,158 |

**Location:**
| Location | Count |
|---|---|
| Unknown | 3,779 |
| Takeaway | 2,889 |
| In-store | 2,872 |

**Numeric Ranges:**
| Column | Min | Max | Mean | Median |
|---|---|---|---|---|
| Quantity | 1.0 | 5.0 | 3.02 | 3.0 |
| Price Per Unit | 1.0 | 5.0 | 2.95 | 3.0 |
| Total Spent | 1.0 | 25.0 | 8.92 | 8.0 |

---

## 💻 Usage

```python
import pandas as pd

df = pd.read_csv("cleaned_cafe_sales.csv", parse_dates=["Transaction Date"])
df.head()
```

---

## 🛠️ Cleaning Notebook

The full cleaning process is documented step-by-step in `cafe_data_cleaning.ipynb`. It covers:
- Initial EDA and dirty data exploration
- Corrupt value detection and replacement
- Type casting and null handling strategies
- Derived column consistency verification
- Final quality audit

---

## 📜 License

This dataset is released under the **MIT License**. Free to use for personal, educational, and commercial purposes.

---

## 👤 Author

**Aditya Suyal**  
[HuggingFace Profile](https://huggingface.co/rohansuyal)
