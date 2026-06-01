# 2. Data Cleaning

## Data Quality Issues Found

### Issue 1 — Transaction Type Normalization
- **Problem:** "A/P Invoice" variant found alongside standard "AP Invoice"
- **Fix:** Mapped variant to standard name
- **Impact:** AP Invoice analysis would be split across two groups

### Issue 2 — Negative Amount Values
- **Problem:** 8 records with negative Amount_VND values
- **Likely cause:** Credit memos or adjustments entered as negative amounts
- **Fix:** Applied `clip(lower=0)`, flagged for manual review
- **Impact:** Total transaction amounts and department summaries would be distorted

### Issue 3 — Negative Days Outstanding
- **Problem:** 12 records with negative Days_Outstanding
- **Likely cause:** Future-dated transactions or system clock errors
- **Fix:** Clipped to 0; excluded from aging analysis
- **Impact:** Overdue rate calculation would be affected

### Issue 4 — Missing Payment Date (Critical)
- **Problem:** 141 transactions (28.2%) have no Payment_Date
- **Likely cause:** Unpaid invoices, or payment not recorded
- **Fix:** Flagged; excluded from payment timing analysis
- **Impact:** Cash flow analysis unreliable without payment dates

### Issue 5 — Missing Reference Numbers
- **Problem:** 397 missing PO numbers (79.4%), 300 missing Contract IDs (60%)
- **Fix:** Flagged as data governance issue
- **Impact:** Cannot link transactions to contracts for spend analysis

### Issue 6 — Unusual VAT Rate (14 records)
- **Problem:** 14 transactions have 15% VAT rate (Vietnamese standard is 10%)
- **Fix:** Flagged for finance team audit
- **Impact:** Tax liability calculations may be overstated

## Cleaning Summary

| Issue | Records | Action |
|-------|---------|--------|
| Transaction type variant | ~15 | Normalized |
| Negative amounts | 8 | Clipped, flagged |
| Negative days outstanding | 12 | Clipped, flagged |
| Missing payment date | 141 | Flagged |
| Missing PO number | 397 | Flagged |
| Unusual VAT 15% | 14 | Flagged for audit |
