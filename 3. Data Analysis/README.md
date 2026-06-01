# 3. Data Analysis

## Analysis Overview

20 SQL queries and 7 Python EDA charts covering overdue analysis, department spend, budget variance, approval workflow, and compliance risk.

---

## 1. Portfolio Overview

- **Total Transactions:** 500
- **Total Amount:** 116.59B VND
- **Approved:** 317 (63.4%)
- **Pending:** 93 (18.6%)
- **Rejected:** 87 (17.4%)
- **Overdue:** 129 (25.8%)
- **Avg Days Outstanding:** 40.9 days

---

## 2. Transaction Type Analysis

| Transaction Type | Count | Total (B VND) | Overdue% | Rejected% |
|-----------------|-------|--------------|----------|-----------|
| Journal Entry | 60 | 1.25 | 28.3% | 23.3% |
| Tax Payment | 50 | 4.92 | **36.0%** | **30.0%** |
| Asset Purchase | 56 | 48.91 | 25.0% | 19.6% |
| Payroll | 54 | 15.51 | 24.1% | 13.0% |
| AR Invoice | 50 | 16.95 | 22.0% | 16.0% |
| AP Invoice | 46 | 10.51 | 23.9% | 15.2% |
| Receipt - In | 44 | 10.14 | 29.5% | 9.1% |
| Expense Claim | 40 | 0.33 | **40.0%** | 20.0% |

---

## 3. Department Performance

| Department | Transactions | Amount (B VND) | Overdue% | Avg Variance% |
|------------|-------------|---------------|----------|--------------|
| Sales Dept | 66 | 18.64 | **39.4%** | +5.39% |
| Manufacturing | 56 | 18.93 | 30.4% | +3.03% |
| Logistics Dept | 56 | 8.83 | 33.9% | +2.12% |
| Administration | 71 | 16.09 | 26.8% | +2.44% |
| IT | 59 | 12.78 | 23.7% | +2.96% |
| Procurement | 68 | 12.16 | 23.5% | +1.02% |
| Accounting | 59 | 13.89 | 18.6% | +2.17% |
| Marketing | 55 | 13.45 | 12.7% | +3.36% |

---

## 4. Budget Variance Trend

| Quarter | Avg Variance% | Overdue% |
|---------|--------------|----------|
| Q1 | +1.50% | 23.9% |
| Q2 | +2.33% | 23.5% |
| Q3 | +2.63% | 31.1% |
| Q4 | **+4.63%** | 25.0% |

**Accelerating overspend — requires budget control intervention.**

---

## 5. Payment Method Analysis

| Method | Count | Overdue% |
|--------|-------|----------|
| Online Banking | 131 | **14.5%** |
| Bank Transfer | 130 | 27.7% |
| Cash | 111 | 29.7% |
| Check | 124 | 33.1% |

---

## Further Exploration

- **Cash Flow Forecasting:** Model payment timing based on historical patterns
- **Aging Buckets:** Classify overdue by 30/60/90/180/300+ days
- **Rejection Pattern Analysis:** What characteristics predict rejection?
- **Currency Risk:** Exposure to USD/EUR rate fluctuations
- **Vendor Payment Terms:** Are we consistently late with specific vendors?
