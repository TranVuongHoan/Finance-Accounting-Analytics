-- ============================================================
-- Finance & Accounting Transactions – SQL Analysis
-- Dataset : 08_Finance_Accounting.xlsx | Sheet: 2_CLEANED_DATA
-- Engine  : DuckDB / PostgreSQL compatible
-- Table   : finance_txn  (load via DuckDB: CREATE TABLE finance_txn AS SELECT * FROM read_xlsx('08_Finance_Accounting (1).xlsx', sheet='2_CLEANED_DATA'))
-- ============================================================

-- ── NORMALIZATION CTE (used throughout) ──────────────────────────────────────
-- Embed at top of any query that needs clean fields

/*
WITH norm AS (
    SELECT *,
        -- Merge A/P Invoice typo
        CASE WHEN Transaction_Type = 'A/P Invoice' THEN 'AP Invoice'
             ELSE Transaction_Type END                          AS txn_type,
        -- Clip negative amounts
        GREATEST(Amount_VND, 0)                                AS amt_clean,
        -- Clip negative days
        GREATEST(Days_Outstanding, 0)                          AS days_clean,
        -- Net margin recalc placeholder (not needed here)
        CAST(Budget_Variance_Pct AS DOUBLE)                    AS bv_pct
    FROM finance_txn
)
*/

-- ────────────────────────────────────────────────────────────────────────────
-- QUERY 01 | Overall KPIs
-- ────────────────────────────────────────────────────────────────────────────
WITH norm AS (
    SELECT *,
        CASE WHEN Transaction_Type = 'A/P Invoice' THEN 'AP Invoice'
             ELSE Transaction_Type END AS txn_type,
        GREATEST(Amount_VND, 0)        AS amt_clean,
        GREATEST(Days_Outstanding, 0)  AS days_clean
    FROM finance_txn
)
SELECT
    COUNT(*)                                                           AS total_transactions,
    ROUND(SUM(amt_clean) / 1e9, 2)                                    AS total_amount_B_VND,
    SUM(CASE WHEN Overdue_Flag = 'Yes' THEN 1 ELSE 0 END)             AS overdue_count,
    ROUND(AVG(CASE WHEN Overdue_Flag = 'Yes' THEN 1.0 ELSE 0 END)*100,1) AS overdue_pct,
    SUM(CASE WHEN Approval_Status = 'Rejected' THEN 1 ELSE 0 END)    AS rejected_count,
    ROUND(AVG(CASE WHEN Approval_Status = 'Rejected' THEN 1.0 ELSE 0 END)*100,1) AS rejected_pct,
    SUM(CASE WHEN Approval_Status = 'Pending' THEN 1 ELSE 0 END)     AS pending_count,
    ROUND(AVG(days_clean), 1)                                         AS avg_days_outstanding,
    SUM(CASE WHEN Amount_VND < 0 THEN 1 ELSE 0 END)                  AS negative_amounts,
    SUM(CASE WHEN Days_Outstanding < 0 THEN 1 ELSE 0 END)            AS negative_days,
    SUM(CASE WHEN Currency != 'VND' THEN 1 ELSE 0 END)               AS multi_currency_txns
FROM norm;


-- ────────────────────────────────────────────────────────────────────────────
-- QUERY 02 | Transaction Type Performance Ranking
-- ────────────────────────────────────────────────────────────────────────────
WITH norm AS (
    SELECT *,
        CASE WHEN Transaction_Type = 'A/P Invoice' THEN 'AP Invoice'
             ELSE Transaction_Type END AS txn_type,
        GREATEST(Amount_VND, 0)        AS amt_clean,
        GREATEST(Days_Outstanding, 0)  AS days_clean
    FROM finance_txn
)
SELECT
    txn_type,
    COUNT(*)                                                          AS txn_count,
    ROUND(SUM(amt_clean) / 1e9, 2)                                   AS total_B_VND,
    SUM(CASE WHEN Overdue_Flag = 'Yes' THEN 1 ELSE 0 END)            AS overdue_count,
    ROUND(AVG(CASE WHEN Overdue_Flag = 'Yes' THEN 1.0 ELSE 0 END)*100,1) AS overdue_pct,
    SUM(CASE WHEN Approval_Status = 'Rejected' THEN 1 ELSE 0 END)   AS rejected_count,
    ROUND(AVG(CASE WHEN Approval_Status = 'Rejected' THEN 1.0 ELSE 0 END)*100,1) AS rejected_pct,
    ROUND(AVG(days_clean), 1)                                        AS avg_days_outstanding
FROM norm
GROUP BY txn_type
ORDER BY overdue_pct DESC;


-- ────────────────────────────────────────────────────────────────────────────
-- QUERY 03 | Department Analysis – Overdue & Budget Variance
-- ────────────────────────────────────────────────────────────────────────────
WITH norm AS (
    SELECT *, GREATEST(Amount_VND, 0) AS amt_clean
    FROM finance_txn
)
SELECT
    Department,
    COUNT(*)                                                               AS txn_count,
    ROUND(SUM(amt_clean) / 1e9, 2)                                        AS total_B_VND,
    SUM(CASE WHEN Overdue_Flag = 'Yes' THEN 1 ELSE 0 END)                 AS overdue_count,
    ROUND(AVG(CASE WHEN Overdue_Flag = 'Yes' THEN 1.0 ELSE 0 END)*100, 1) AS overdue_pct,
    SUM(CASE WHEN Approval_Status = 'Rejected' THEN 1 ELSE 0 END)         AS rejected_count,
    ROUND(AVG("Budget_Variance_%"), 2)                                     AS avg_budget_variance_pct,
    ROUND(MAX("Budget_Variance_%"), 2)                                     AS max_budget_variance_pct
FROM norm
GROUP BY Department
ORDER BY overdue_pct DESC;


-- ────────────────────────────────────────────────────────────────────────────
-- QUERY 04 | Quarterly Trend – Volume, Amount, Overdue, Budget
-- ────────────────────────────────────────────────────────────────────────────
WITH norm AS (
    SELECT *, GREATEST(Amount_VND, 0) AS amt_clean
    FROM finance_txn
)
SELECT
    Quarter,
    COUNT(*)                                                               AS txn_count,
    ROUND(SUM(amt_clean) / 1e9, 2)                                        AS total_B_VND,
    SUM(CASE WHEN Overdue_Flag = 'Yes' THEN 1 ELSE 0 END)                 AS overdue_count,
    ROUND(AVG(CASE WHEN Overdue_Flag = 'Yes' THEN 1.0 ELSE 0 END)*100, 1) AS overdue_pct,
    SUM(CASE WHEN Approval_Status = 'Rejected' THEN 1 ELSE 0 END)         AS rejected_count,
    ROUND(AVG("Budget_Variance_%"), 2)                                     AS avg_budget_variance_pct
FROM norm
GROUP BY Quarter
ORDER BY Quarter;


-- ────────────────────────────────────────────────────────────────────────────
-- QUERY 05 | Monthly Trend – Transaction Volume & Overdue Rate
-- ────────────────────────────────────────────────────────────────────────────
WITH norm AS (
    SELECT *, GREATEST(Amount_VND, 0) AS amt_clean
    FROM finance_txn
)
SELECT
    Month,
    COUNT(*)                                                               AS txn_count,
    ROUND(SUM(amt_clean) / 1e9, 2)                                        AS total_B_VND,
    SUM(CASE WHEN Overdue_Flag = 'Yes' THEN 1 ELSE 0 END)                 AS overdue_count,
    ROUND(AVG(CASE WHEN Overdue_Flag = 'Yes' THEN 1.0 ELSE 0 END)*100, 1) AS overdue_pct
FROM norm
GROUP BY Month
ORDER BY CASE Month
    WHEN 'Jan' THEN 1 WHEN 'Feb' THEN 2 WHEN 'Mar' THEN 3
    WHEN 'Apr' THEN 4 WHEN 'May' THEN 5 WHEN 'Jun' THEN 6
    WHEN 'Jul' THEN 7 WHEN 'Aug' THEN 8 WHEN 'Sep' THEN 9
    WHEN 'Oct' THEN 10 WHEN 'Nov' THEN 11 WHEN 'Dec' THEN 12 END;


-- ────────────────────────────────────────────────────────────────────────────
-- QUERY 06 | Cost Type Breakdown with Budget Variance
-- ────────────────────────────────────────────────────────────────────────────
WITH norm AS (
    SELECT *, GREATEST(Amount_VND, 0) AS amt_clean
    FROM finance_txn
)
SELECT
    Cost_Type,
    COUNT(*)                                   AS txn_count,
    ROUND(SUM(amt_clean) / 1e9, 2)             AS total_B_VND,
    ROUND(AVG("Budget_Variance_%"), 2)          AS avg_variance_pct,
    ROUND(MAX("Budget_Variance_%"), 2)          AS max_variance_pct,
    ROUND(MIN("Budget_Variance_%"), 2)          AS min_variance_pct,
    SUM(CASE WHEN "Budget_Variance_%" > 10 THEN 1 ELSE 0 END) AS over_10pct_count
FROM norm
GROUP BY Cost_Type
ORDER BY total_B_VND DESC;


-- ────────────────────────────────────────────────────────────────────────────
-- QUERY 07 | Approval Status by Department
-- ────────────────────────────────────────────────────────────────────────────
SELECT
    Department,
    Approval_Status,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY Department), 1) AS pct_of_dept
FROM finance_txn
GROUP BY Department, Approval_Status
ORDER BY Department, Approval_Status;


-- ────────────────────────────────────────────────────────────────────────────
-- QUERY 08 | Tax Payment Crisis – Overdue + Rejected
-- ────────────────────────────────────────────────────────────────────────────
WITH norm AS (
    SELECT *,
        CASE WHEN Transaction_Type = 'A/P Invoice' THEN 'AP Invoice'
             ELSE Transaction_Type END AS txn_type,
        GREATEST(Days_Outstanding, 0)  AS days_clean
    FROM finance_txn
)
SELECT
    txn_type,
    COUNT(*)                                                               AS count,
    SUM(CASE WHEN Overdue_Flag = 'Yes' THEN 1 ELSE 0 END)                 AS overdue,
    ROUND(AVG(CASE WHEN Overdue_Flag = 'Yes' THEN 1.0 ELSE 0 END)*100, 1) AS overdue_pct,
    SUM(CASE WHEN Approval_Status = 'Rejected' THEN 1 ELSE 0 END)         AS rejected,
    ROUND(AVG(CASE WHEN Approval_Status = 'Rejected' THEN 1.0 ELSE 0 END)*100, 1) AS rejected_pct,
    ROUND(AVG(days_clean), 1)                                              AS avg_days
FROM norm
WHERE txn_type = 'Tax Payment'
GROUP BY txn_type;


-- ────────────────────────────────────────────────────────────────────────────
-- QUERY 09 | Overdue Transactions – Top 20 by Days Outstanding
-- ────────────────────────────────────────────────────────────────────────────
WITH norm AS (
    SELECT *,
        CASE WHEN Transaction_Type = 'A/P Invoice' THEN 'AP Invoice'
             ELSE Transaction_Type END AS txn_type,
        GREATEST(Amount_VND, 0)        AS amt_clean,
        GREATEST(Days_Outstanding, 0)  AS days_clean
    FROM finance_txn
)
SELECT
    Transaction_ID,
    Department,
    txn_type,
    days_clean                                 AS days_outstanding,
    ROUND(amt_clean / 1e6, 1)                  AS amount_M_VND,
    Approval_Status,
    Expense_Category,
    Vendor_Customer_Name,
    CASE
        WHEN days_clean > 270 THEN 'CRITICAL (>9 months)'
        WHEN days_clean > 180 THEN 'SEVERE (6–9 months)'
        WHEN days_clean > 90  THEN 'HIGH (3–6 months)'
        ELSE 'MODERATE (<3 months)'
    END AS severity
FROM norm
WHERE Overdue_Flag = 'Yes'
ORDER BY days_clean DESC
LIMIT 20;


-- ────────────────────────────────────────────────────────────────────────────
-- QUERY 10 | Budget Variance Distribution Buckets
-- ────────────────────────────────────────────────────────────────────────────
SELECT
    CASE
        WHEN "Budget_Variance_%" < -20  THEN '< -20% (Severely Under)'
        WHEN "Budget_Variance_%" < -10  THEN '-20% to -10% (Under)'
        WHEN "Budget_Variance_%" <= 10  THEN '-10% to +10% (On Budget)'
        WHEN "Budget_Variance_%" <= 20  THEN '+10% to +20% (Over)'
        ELSE '> +20% (Severely Over)'
    END AS variance_bucket,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / 500, 1) AS pct_of_total,
    ROUND(AVG("Budget_Variance_%"), 2) AS avg_variance
FROM finance_txn
GROUP BY variance_bucket
ORDER BY MIN("Budget_Variance_%");


-- ────────────────────────────────────────────────────────────────────────────
-- QUERY 11 | Payment Method Overdue Analysis
-- ────────────────────────────────────────────────────────────────────────────
WITH norm AS (
    SELECT *, GREATEST(Days_Outstanding, 0) AS days_clean
    FROM finance_txn
)
SELECT
    Payment_Method,
    COUNT(*) AS count,
    SUM(CASE WHEN Overdue_Flag = 'Yes' THEN 1 ELSE 0 END) AS overdue_count,
    ROUND(AVG(CASE WHEN Overdue_Flag = 'Yes' THEN 1.0 ELSE 0 END)*100, 1) AS overdue_pct,
    ROUND(AVG(days_clean), 1) AS avg_days_outstanding
FROM norm
GROUP BY Payment_Method
ORDER BY overdue_pct DESC;


-- ────────────────────────────────────────────────────────────────────────────
-- QUERY 12 | Multi-Currency Exposure
-- ────────────────────────────────────────────────────────────────────────────
WITH norm AS (
    SELECT *, GREATEST(Amount_VND, 0) AS amt_clean
    FROM finance_txn
)
SELECT
    Currency,
    COUNT(*) AS txn_count,
    ROUND(SUM(amt_clean) / 1e9, 2) AS total_B_VND,
    ROUND(SUM(amt_clean) * 100.0 / SUM(SUM(amt_clean)) OVER (), 1) AS pct_of_total,
    ROUND(AVG(Exchange_Rate), 0) AS avg_exchange_rate,
    SUM(CASE WHEN Overdue_Flag = 'Yes' THEN 1 ELSE 0 END) AS overdue_count
FROM norm
GROUP BY Currency
ORDER BY total_B_VND DESC;


-- ────────────────────────────────────────────────────────────────────────────
-- QUERY 13 | Expense Claim Alert – Highest Overdue Rate
-- ────────────────────────────────────────────────────────────────────────────
WITH norm AS (
    SELECT *,
        CASE WHEN Transaction_Type = 'A/P Invoice' THEN 'AP Invoice'
             ELSE Transaction_Type END AS txn_type,
        GREATEST(Days_Outstanding, 0) AS days_clean
    FROM finance_txn
)
SELECT
    Transaction_ID,
    Department,
    Vendor_Customer_Name,
    days_clean        AS days_outstanding,
    ROUND(GREATEST(Amount_VND, 0) / 1e6, 1) AS amount_M_VND,
    Approval_Status,
    Expense_Category
FROM norm
WHERE txn_type = 'Expense Claim'
  AND Overdue_Flag = 'Yes'
ORDER BY days_clean DESC;


-- ────────────────────────────────────────────────────────────────────────────
-- QUERY 14 | VAT Rate Anomaly – 15% Rate
-- ────────────────────────────────────────────────────────────────────────────
SELECT
    Transaction_ID,
    Department,
    Transaction_Type,
    VAT_Rate,
    ROUND(GREATEST(Amount_VND, 0) / 1e6, 1) AS amount_M_VND,
    VAT_Amount_VND,
    Approval_Status,
    Notes
FROM finance_txn
WHERE VAT_Rate = '15%'
ORDER BY VAT_Amount_VND DESC;
-- NOTE: Vietnamese VAT standard rates are 0%, 5%, 10%.
-- 15% rate (14 transactions) is non-standard and likely a data entry error.


-- ────────────────────────────────────────────────────────────────────────────
-- QUERY 15 | Pending Approval – Aging Analysis
-- ────────────────────────────────────────────────────────────────────────────
WITH norm AS (
    SELECT *,
        CASE WHEN Transaction_Type = 'A/P Invoice' THEN 'AP Invoice'
             ELSE Transaction_Type END AS txn_type,
        GREATEST(Amount_VND, 0)        AS amt_clean,
        GREATEST(Days_Outstanding, 0)  AS days_clean
    FROM finance_txn
    WHERE Approval_Status = 'Pending'
)
SELECT
    txn_type,
    COUNT(*) AS pending_count,
    ROUND(SUM(amt_clean) / 1e6, 1) AS pending_total_M_VND,
    ROUND(AVG(days_clean), 1)      AS avg_days_pending,
    MAX(days_clean)                AS max_days_pending,
    SUM(CASE WHEN Overdue_Flag = 'Yes' THEN 1 ELSE 0 END) AS also_overdue
FROM norm
GROUP BY txn_type
ORDER BY pending_total_M_VND DESC;


-- ────────────────────────────────────────────────────────────────────────────
-- QUERY 16 | Budget Overspend – Worst Transactions
-- ────────────────────────────────────────────────────────────────────────────
SELECT
    Transaction_ID,
    Department,
    Transaction_Type,
    Expense_Category,
    ROUND(GREATEST(Amount_VND, 0) / 1e6, 1)  AS actual_M_VND,
    ROUND(Budget_Amount_VND / 1e6, 1)          AS budget_M_VND,
    Budget_Variance_VND                         AS variance_VND,
    ROUND("Budget_Variance_%", 1)               AS variance_pct,
    Approval_Status
FROM finance_txn
WHERE "Budget_Variance_%" > 30
ORDER BY "Budget_Variance_%" DESC
LIMIT 20;


-- ────────────────────────────────────────────────────────────────────────────
-- QUERY 17 | Kinh Doanh Department Deep-Dive (39.4% overdue)
-- ────────────────────────────────────────────────────────────────────────────
WITH norm AS (
    SELECT *,
        CASE WHEN Transaction_Type = 'A/P Invoice' THEN 'AP Invoice'
             ELSE Transaction_Type END AS txn_type,
        GREATEST(Amount_VND, 0)        AS amt_clean,
        GREATEST(Days_Outstanding, 0)  AS days_clean
    FROM finance_txn
    WHERE Department = 'Kinh Doanh'
)
SELECT
    txn_type,
    Expense_Category,
    COUNT(*) AS count,
    SUM(CASE WHEN Overdue_Flag = 'Yes' THEN 1 ELSE 0 END) AS overdue,
    ROUND(AVG(CASE WHEN Overdue_Flag = 'Yes' THEN 1.0 ELSE 0 END)*100,1) AS overdue_pct,
    ROUND(SUM(amt_clean)/1e6, 1) AS total_M_VND,
    ROUND(AVG(days_clean), 1)    AS avg_days
FROM norm
GROUP BY txn_type, Expense_Category
ORDER BY overdue_pct DESC;


-- ────────────────────────────────────────────────────────────────────────────
-- QUERY 18 | Q4 Budget Variance Escalation – Root Cause
-- ────────────────────────────────────────────────────────────────────────────
SELECT
    Quarter,
    Department,
    Cost_Type,
    COUNT(*) AS count,
    ROUND(AVG("Budget_Variance_%"), 2) AS avg_variance,
    SUM(CASE WHEN "Budget_Variance_%" > 10 THEN 1 ELSE 0 END) AS over_10pct,
    SUM(CASE WHEN "Budget_Variance_%" > 30 THEN 1 ELSE 0 END) AS over_30pct
FROM finance_txn
WHERE Quarter = 'Q4'
GROUP BY Quarter, Department, Cost_Type
ORDER BY avg_variance DESC;


-- ────────────────────────────────────────────────────────────────────────────
-- QUERY 19 | Transaction Name Audit – Normalization Check
-- ────────────────────────────────────────────────────────────────────────────
SELECT
    Transaction_Type       AS raw_name,
    COUNT(*)               AS occurrences,
    CASE
        WHEN Transaction_Type = 'A/P Invoice' THEN '⚠ TYPO → should be AP Invoice'
        ELSE '✅ OK'
    END                    AS status
FROM finance_txn
GROUP BY Transaction_Type
ORDER BY occurrences DESC;


-- ────────────────────────────────────────────────────────────────────────────
-- QUERY 20 | Data Quality Summary
-- ────────────────────────────────────────────────────────────────────────────
SELECT
    'Total transactions'                                              AS metric,
    COUNT(*)                                                          AS value
FROM finance_txn
UNION ALL
SELECT 'Negative Amount_VND',
    SUM(CASE WHEN Amount_VND < 0 THEN 1 ELSE 0 END)
FROM finance_txn
UNION ALL
SELECT 'Negative Days_Outstanding',
    SUM(CASE WHEN Days_Outstanding < 0 THEN 1 ELSE 0 END)
FROM finance_txn
UNION ALL
SELECT 'Missing Payment_Date',
    SUM(CASE WHEN Payment_Date IS NULL THEN 1 ELSE 0 END)
FROM finance_txn
UNION ALL
SELECT 'Missing Project_Code',
    SUM(CASE WHEN Project_Code IS NULL THEN 1 ELSE 0 END)
FROM finance_txn
UNION ALL
SELECT 'Missing PO_Number',
    SUM(CASE WHEN PO_Number IS NULL THEN 1 ELSE 0 END)
FROM finance_txn
UNION ALL
SELECT 'Missing Contract_Number',
    SUM(CASE WHEN Contract_Number IS NULL THEN 1 ELSE 0 END)
FROM finance_txn
UNION ALL
SELECT 'VAT Rate 15% (non-standard)',
    SUM(CASE WHEN VAT_Rate = '15%' THEN 1 ELSE 0 END)
FROM finance_txn
UNION ALL
SELECT 'Approval Status = Pending',
    SUM(CASE WHEN Approval_Status = 'Pending' THEN 1 ELSE 0 END)
FROM finance_txn
UNION ALL
SELECT 'Approval Status = Rejected',
    SUM(CASE WHEN Approval_Status = 'Rejected' THEN 1 ELSE 0 END)
FROM finance_txn
ORDER BY metric;
