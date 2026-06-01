# 1. Data Preparation

## Dataset Overview

The dataset `08_Finance_Accounting.xlsx` contains **500 financial transaction records** across **8 departments**, **10 transaction types**, and **3 currencies** (VND, USD, EUR).

## Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `Transaction_ID` | String | Unique transaction identifier (e.g., TXN-00001) |
| `Transaction_Name` | String | Descriptive transaction name |
| `Transaction_Type` | String | Type: AP Invoice, AR Invoice, Tax Payment, Payroll, etc. |
| `Department` | String | Responsible department |
| `Cost_Type` | String | OPEX, CAPEX, COGS, Revenue, Tax |
| `Expense_Category` | String | Detailed expense classification |
| `Amount_VND` | Float | Transaction amount in Vietnamese Dong |
| `Currency` | String | Transaction currency (VND, USD, EUR) |
| `VAT_Rate_Pct` | Float | VAT rate applied (%) |
| `Transaction_Date` | Date | Date transaction was created |
| `Payment_Date` | Date | Date payment was made/received |
| `Due_Date` | Date | Payment due date |
| `Days_Outstanding` | Integer | Days since transaction was created |
| `Approval_Status` | String | Approved, Pending, Rejected |
| `Payment_Method` | String | Bank Transfer, Cash, Check, Online Banking |
| `PO_Number` | String | Purchase Order reference |
| `Contract_ID` | String | Contract reference |
| `Project_Code` | String | Project cost center code |
| `Budget_Variance_Pct` | Float | % deviation from budgeted amount |

## Dataset Size

- **Rows:** 500 transactions
- **Total Amount:** 116.59B VND
- **Currencies:** VND (281), USD (141), EUR (74)
- **Departments:** 8
- **Transaction Types:** 10
