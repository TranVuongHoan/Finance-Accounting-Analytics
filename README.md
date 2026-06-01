# 💳 Finance & Accounting Analytics

This repository contains a comprehensive analysis of financial transactions extracted from `08_Finance_Accounting.xlsx`. The analysis covers 500 transactions totaling **116.59B VND** across 8 departments, 10 transaction types, and 3 currencies.

---

## 📁 Repository Structure

| Folder | Contents |
|--------|----------|
| `1. Data Preparation/` | Dataset overview, field descriptions |
| `2. Data Cleaning/` | Transaction type normalization, anomaly detection |
| `3. Data Analysis/` | 20 SQL queries + 7 Python EDA charts |
| `4. Report Creation/` | Interactive HTML dashboard |

---

## 🔑 Key Findings

- **25.8% overdue rate** — 1 in 4 transactions past due
- **Tax Payment crisis:** 36% overdue + 30% rejected — highest compliance risk
- **Sales Dept leads overdue at 39.4%**, Logistics Dept at 33.3%
- **Budget variance accelerating:** Q1 +1.5% → Q4 +4.63%
- **14 transactions with 15% VAT** (standard is 10%) — requires audit
- **141 transactions** missing payment date

---

## 🛠️ Tools Used
- **Python** — pandas, matplotlib
- **SQL** — DuckDB/PostgreSQL compatible
- **HTML/JS/Chart.js** — Interactive dashboard
