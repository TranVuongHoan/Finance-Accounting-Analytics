"""
Finance & Accounting Transactions – EDA Script
Dataset: 08_Finance_Accounting.xlsx | Sheet: 2_CLEANED_DATA | 500 rows × 43 cols
Charts: 7 matplotlib figures saved to C:\Data Analysis\Output\
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.patches import FancyBboxPatch
import warnings
warnings.filterwarnings('ignore')

# ── CONFIG ─────────────────────────────────────────────────────────────────────
FILE   = r"C:\Data Analysis\08_Finance_Accounting (1).xlsx"
SHEET  = "2_CLEANED_DATA"
OUTDIR = r"C:\Data Analysis\Output"

COLORS = {
    'primary'  : '#1a56db',
    'danger'   : '#e02424',
    'warning'  : '#ff8c00',
    'success'  : '#057a55',
    'neutral'  : '#6b7280',
    'light'    : '#e5edff',
    'bg'       : '#f8f9fa',
}

# ── LOAD & NORMALIZE ───────────────────────────────────────────────────────────
df = pd.read_excel(FILE, sheet_name=SHEET)

# Merge 'A/P Invoice' → 'AP Invoice'
txn_map = {'A/P Invoice': 'AP Invoice'}
df['txn_type'] = df['Transaction_Type'].replace(txn_map)

# Clip negatives
df['amt_clean']  = df['Amount_VND'].clip(lower=0)
df['days_clean'] = df['Days_Outstanding'].clip(lower=0)

month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
df['Month_cat'] = pd.Categorical(df['Month'], categories=month_order, ordered=True)

# ── FQ1: Transaction Type – Amount & Approval ─────────────────────────────────
def fq1_transaction_overview():
    g = df.groupby('txn_type').agg(
        total_amt = ('amt_clean','sum'),
        overdue   = ('Overdue_Flag', lambda x: (x=='Yes').sum()),
        count     = ('Transaction_ID','count'),
        rejected  = ('Approval_Status', lambda x: (x=='Rejected').sum())
    ).reset_index()
    g['overdue_pct']  = g['overdue']  / g['count'] * 100
    g['rejected_pct'] = g['rejected'] / g['count'] * 100
    g['total_B']      = g['total_amt'] / 1e9
    g = g.sort_values('total_B', ascending=True)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(COLORS['bg'])
    fig.suptitle('Transaction Overview by Type', fontsize=16, fontweight='bold', y=1.01)

    # Left: horizontal bar – total amount
    ax = axes[0]
    ax.set_facecolor(COLORS['bg'])
    bars = ax.barh(g['txn_type'], g['total_B'],
                   color=[COLORS['danger'] if v > 20 else COLORS['primary'] for v in g['total_B']],
                   edgecolor='white', height=0.6)
    ax.set_xlabel('Total Amount (Billion VND)', fontsize=10)
    ax.set_title('Total Amount by Transaction Type', fontsize=12, fontweight='bold')
    for bar, val in zip(bars, g['total_B']):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}B', va='center', fontsize=9)
    ax.spines[['top','right']].set_visible(False)

    # Right: overdue & rejected %
    ax2 = axes[1]
    ax2.set_facecolor(COLORS['bg'])
    x  = np.arange(len(g))
    w  = 0.35
    ax2.barh(x - w/2, g['overdue_pct'],  w, label='Overdue %',  color=COLORS['warning'], alpha=0.85)
    ax2.barh(x + w/2, g['rejected_pct'], w, label='Rejected %', color=COLORS['danger'],  alpha=0.85)
    ax2.set_yticks(x)
    ax2.set_yticklabels(g['txn_type'], fontsize=9)
    ax2.set_xlabel('Percentage (%)', fontsize=10)
    ax2.set_title('Overdue & Rejected Rate by Type', fontsize=12, fontweight='bold')
    ax2.axvline(25, color=COLORS['neutral'], linestyle='--', alpha=0.5, linewidth=1)
    ax2.legend(fontsize=9)
    ax2.spines[['top','right']].set_visible(False)

    # Highlight Tax Payment
    tax_idx = list(g['txn_type']).index('Tax Payment')
    ax2.barh(tax_idx - w/2, g.loc[g['txn_type']=='Tax Payment','overdue_pct'].values[0],
             w, color=COLORS['danger'], alpha=1.0)
    ax2.text(37, tax_idx, '⚠ 36%', fontsize=9, va='center', color=COLORS['danger'], fontweight='bold')

    plt.tight_layout()
    plt.savefig(f"{OUTDIR}\\fq1_transaction_overview.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ fq1_transaction_overview.png")

# ── FQ2: Department Analysis ───────────────────────────────────────────────────
def fq2_department_analysis():
    g = df.groupby('Department').agg(
        total_amt    = ('amt_clean','sum'),
        overdue      = ('Overdue_Flag', lambda x: (x=='Yes').sum()),
        count        = ('Transaction_ID','count'),
        avg_variance = ('Budget_Variance_%','mean')
    ).reset_index()
    g['overdue_pct'] = g['overdue'] / g['count'] * 100
    g['total_B']     = g['total_amt'] / 1e9
    g = g.sort_values('overdue_pct', ascending=True)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(COLORS['bg'])
    fig.suptitle('Department Performance Analysis', fontsize=16, fontweight='bold')

    # Left: overdue % by dept
    ax = axes[0]
    ax.set_facecolor(COLORS['bg'])
    bar_colors = [COLORS['danger'] if v > 30 else (COLORS['warning'] if v > 20 else COLORS['success'])
                  for v in g['overdue_pct']]
    bars = ax.barh(g['Department'], g['overdue_pct'], color=bar_colors, edgecolor='white', height=0.6)
    ax.axvline(25.8, color=COLORS['neutral'], linestyle='--', linewidth=1.2, label='Avg 25.8%')
    ax.set_xlabel('Overdue Transaction %', fontsize=10)
    ax.set_title('Overdue Rate by Department', fontsize=12, fontweight='bold')
    for bar, val in zip(bars, g['overdue_pct']):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}%', va='center', fontsize=9)
    ax.legend(fontsize=9)
    ax.spines[['top','right']].set_visible(False)

    # Right: budget variance bubble
    ax2 = axes[1]
    ax2.set_facecolor(COLORS['bg'])
    g2 = g.sort_values('avg_variance')
    bar_colors2 = [COLORS['danger'] if v > 4 else (COLORS['warning'] if v > 2 else COLORS['success'])
                   for v in g2['avg_variance']]
    bars2 = ax2.barh(g2['Department'], g2['avg_variance'], color=bar_colors2, edgecolor='white', height=0.6)
    ax2.axvline(0, color='black', linewidth=0.8)
    ax2.axvline(2.81, color=COLORS['neutral'], linestyle='--', linewidth=1.2, label='Avg +2.81%')
    ax2.set_xlabel('Avg Budget Variance (%)', fontsize=10)
    ax2.set_title('Average Budget Variance by Department', fontsize=12, fontweight='bold')
    for bar, val in zip(bars2, g2['avg_variance']):
        ax2.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                 f'+{val:.1f}%' if val >= 0 else f'{val:.1f}%', va='center', fontsize=9)
    ax2.legend(fontsize=9)
    ax2.spines[['top','right']].set_visible(False)

    plt.tight_layout()
    plt.savefig(f"{OUTDIR}\\fq2_department_analysis.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ fq2_department_analysis.png")

# ── FQ3: Approval & Overdue Status ────────────────────────────────────────────
def fq3_approval_overdue():
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.patch.set_facecolor(COLORS['bg'])
    fig.suptitle('Approval Status & Overdue Analysis', fontsize=16, fontweight='bold')

    # Pie: approval status
    ax = axes[0]
    ax.set_facecolor(COLORS['bg'])
    vals   = [317, 93, 87]
    labels = ['Approved\n63.4%', 'Pending\n18.6%', 'Rejected\n17.4%']
    colors = [COLORS['success'], COLORS['warning'], COLORS['danger']]
    wedges, _ = ax.pie(vals, labels=labels, colors=colors,
                       startangle=90, wedgeprops={'edgecolor':'white','linewidth':2})
    ax.set_title('Approval Status Distribution', fontsize=12, fontweight='bold')

    # Bar: overdue by payment method
    ax2 = axes[1]
    ax2.set_facecolor(COLORS['bg'])
    pm_data = {'Bank Transfer': 27.7, 'Cash': 29.7, 'Check': 33.1, 'Online Banking': 14.5}
    pm_names = list(pm_data.keys())
    pm_vals  = list(pm_data.values())
    bar_c = [COLORS['danger'] if v > 30 else (COLORS['warning'] if v > 25 else COLORS['success'])
             for v in pm_vals]
    bars = ax2.bar(pm_names, pm_vals, color=bar_c, edgecolor='white', width=0.6)
    ax2.axhline(25.8, color=COLORS['neutral'], linestyle='--', linewidth=1.2, label='Avg 25.8%')
    ax2.set_ylabel('Overdue %', fontsize=10)
    ax2.set_title('Overdue % by Payment Method', fontsize=12, fontweight='bold')
    for bar, val in zip(bars, pm_vals):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                 f'{val:.1f}%', ha='center', fontsize=9)
    ax2.legend(fontsize=9)
    ax2.spines[['top','right']].set_visible(False)
    ax2.tick_params(axis='x', rotation=15)

    # Scatter: days outstanding vs amount (overdue highlighted)
    ax3 = axes[2]
    ax3.set_facecolor(COLORS['bg'])
    overdue_yes = df[df['Overdue_Flag'] == 'Yes']
    overdue_no  = df[df['Overdue_Flag'] == 'No']
    ax3.scatter(overdue_no['days_clean']/30,  overdue_no['amt_clean']/1e6,
                alpha=0.4, color=COLORS['primary'], s=20, label='On-Time')
    ax3.scatter(overdue_yes['days_clean']/30, overdue_yes['amt_clean']/1e6,
                alpha=0.7, color=COLORS['danger'],  s=30, label='Overdue ⚠')
    ax3.set_xlabel('Months Outstanding', fontsize=10)
    ax3.set_ylabel('Amount (Million VND)', fontsize=10)
    ax3.set_title('Days Outstanding vs Amount', fontsize=12, fontweight='bold')
    ax3.legend(fontsize=9)
    ax3.spines[['top','right']].set_visible(False)

    plt.tight_layout()
    plt.savefig(f"{OUTDIR}\\fq3_approval_overdue.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ fq3_approval_overdue.png")

# ── FQ4: Budget Variance Analysis ─────────────────────────────────────────────
def fq4_budget_variance():
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(COLORS['bg'])
    fig.suptitle('Budget Variance Analysis', fontsize=16, fontweight='bold')

    # Left: histogram of variance
    ax = axes[0]
    ax.set_facecolor(COLORS['bg'])
    bv = df['Budget_Variance_%']
    ax.hist(bv, bins=30, color=COLORS['primary'], alpha=0.7, edgecolor='white')
    ax.axvline(0,    color='black',         linewidth=1.5, linestyle='--', label='Zero baseline')
    ax.axvline(2.81, color=COLORS['danger'],linewidth=1.5, linestyle='--', label='Mean +2.81%')
    ax.set_xlabel('Budget Variance (%)', fontsize=10)
    ax.set_ylabel('Number of Transactions', fontsize=10)
    ax.set_title('Distribution of Budget Variance', fontsize=12, fontweight='bold')

    # Annotate buckets
    buckets = [
        ('Under\n-20%', 36,  -21, 60),
        ('On-budget\n±10%', 175, -1, 90),
        ('Over\n+20%', 98,  21, 60),
    ]
    for label, count, xpos, ypos in buckets:
        ax.annotate(f'{label}\n({count})', xy=(xpos, ypos), fontsize=8,
                    ha='center', color=COLORS['neutral'])
    ax.legend(fontsize=9)
    ax.spines[['top','right']].set_visible(False)

    # Right: quarterly variance trend
    ax2 = axes[1]
    ax2.set_facecolor(COLORS['bg'])
    q_data = {'Q1': 1.50, 'Q2': 2.33, 'Q3': 2.63, 'Q4': 4.63}
    quarters = list(q_data.keys())
    variances = list(q_data.values())
    bar_c = [COLORS['danger'] if v > 4 else (COLORS['warning'] if v > 2 else COLORS['success'])
             for v in variances]
    bars = ax2.bar(quarters, variances, color=bar_c, edgecolor='white', width=0.5)
    ax2.axhline(0, color='black', linewidth=0.8)
    ax2.set_ylabel('Avg Budget Variance (%)', fontsize=10)
    ax2.set_title('Budget Variance Trending UP by Quarter', fontsize=12, fontweight='bold')
    for bar, val in zip(bars, variances):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                 f'+{val:.2f}%', ha='center', fontsize=10, fontweight='bold')
    ax2.annotate('⚠ Q4 overspend\naccelerating', xy=(3, 4.63),
                 xytext=(2.2, 5.5), fontsize=9, color=COLORS['danger'],
                 arrowprops=dict(arrowstyle='->', color=COLORS['danger']))
    ax2.spines[['top','right']].set_visible(False)

    plt.tight_layout()
    plt.savefig(f"{OUTDIR}\\fq4_budget_variance.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ fq4_budget_variance.png")

# ── FQ5: Monthly Trend ─────────────────────────────────────────────────────────
def fq5_monthly_trend():
    monthly = df.groupby('Month_cat', observed=True).agg(
        count    = ('Transaction_ID','count'),
        total_amt= ('amt_clean','sum'),
        overdue  = ('Overdue_Flag', lambda x: (x=='Yes').sum())
    ).reset_index()
    monthly['overdue_pct'] = monthly['overdue'] / monthly['count'] * 100
    monthly['total_B']     = monthly['total_amt'] / 1e9

    fig, axes = plt.subplots(2, 1, figsize=(14, 8))
    fig.patch.set_facecolor(COLORS['bg'])
    fig.suptitle('Monthly Transaction Trends (FY2024)', fontsize=16, fontweight='bold')

    months = [str(m) for m in monthly['Month_cat']]
    x = np.arange(len(months))

    # Top: transaction volume + amount
    ax = axes[0]
    ax.set_facecolor(COLORS['bg'])
    ax2_twin = ax.twinx()
    ax.bar(x, monthly['count'], color=COLORS['light'], edgecolor=COLORS['primary'],
           width=0.6, label='# Transactions')
    ax2_twin.plot(x, monthly['total_B'], 'o-', color=COLORS['primary'],
                  linewidth=2, markersize=6, label='Amount (B VND)')
    ax.set_xticks(x)
    ax.set_xticklabels(months)
    ax.set_ylabel('Number of Transactions', fontsize=10, color=COLORS['neutral'])
    ax2_twin.set_ylabel('Amount (Billion VND)', fontsize=10, color=COLORS['primary'])
    ax.set_title('Monthly Volume & Amount', fontsize=12, fontweight='bold')
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9)
    ax.spines[['top','right']].set_visible(False)

    # Highlight Mar spike
    ax.annotate('Mar spike\n15.6B VND', xy=(2, 44), xytext=(3.5, 50),
                fontsize=9, color=COLORS['danger'],
                arrowprops=dict(arrowstyle='->', color=COLORS['danger']))

    # Bottom: overdue %
    ax3 = axes[1]
    ax3.set_facecolor(COLORS['bg'])
    bar_c = [COLORS['danger'] if v > 30 else (COLORS['warning'] if v > 20 else COLORS['success'])
             for v in monthly['overdue_pct']]
    ax3.bar(x, monthly['overdue_pct'], color=bar_c, edgecolor='white', width=0.6)
    ax3.axhline(25.8, color=COLORS['neutral'], linestyle='--', linewidth=1.2, label='Avg 25.8%')
    ax3.set_xticks(x)
    ax3.set_xticklabels(months)
    ax3.set_ylabel('Overdue %', fontsize=10)
    ax3.set_title('Monthly Overdue Rate – Oct Peak 36.2%', fontsize=12, fontweight='bold')
    for i, val in enumerate(monthly['overdue_pct']):
        ax3.text(i, val + 0.5, f'{val:.0f}%', ha='center', fontsize=8)
    ax3.legend(fontsize=9)
    ax3.spines[['top','right']].set_visible(False)

    plt.tight_layout()
    plt.savefig(f"{OUTDIR}\\fq5_monthly_trend.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ fq5_monthly_trend.png")

# ── FQ6: Cost Type & Expense Category ─────────────────────────────────────────
def fq6_cost_expense():
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(COLORS['bg'])
    fig.suptitle('Cost Type & Expense Category Breakdown', fontsize=16, fontweight='bold')

    # Left: Cost type donut
    ax = axes[0]
    ax.set_facecolor(COLORS['bg'])
    cost_data = {'CAPEX': 48.91, 'Revenue': 27.44, 'OPEX': 24.82, 'COGS': 10.51, 'Tax': 4.92}
    sizes  = list(cost_data.values())
    labels = [f'{k}\n{v:.1f}B' for k, v in cost_data.items()]
    colors = [COLORS['primary'], COLORS['success'], COLORS['warning'],
              '#7e3af2', COLORS['danger']]
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct='%1.0f%%',
        startangle=90, pctdistance=0.75,
        wedgeprops={'edgecolor':'white','linewidth':2}
    )
    for at in autotexts:
        at.set_fontsize(8)
    # Draw white circle for donut
    centre_circle = plt.Circle((0, 0), 0.55, fc='white')
    ax.add_patch(centre_circle)
    ax.text(0, 0, '116.6B\nVND', ha='center', va='center', fontsize=11, fontweight='bold')
    ax.set_title('Cost Type Distribution', fontsize=12, fontweight='bold')

    # Right: expense category + avg days
    ax2 = axes[1]
    ax2.set_facecolor(COLORS['bg'])
    cat_data = {
        'Equipment': (48.91, 31.0),
        'Product Sales': (16.95, 41.2),
        'Salary': (15.51, 33.1),
        'Raw Material': (10.51, 32.2),
        'Customer Pmt': (10.49, 47.5),
        'Supplier Pmt': (5.42, 14.8),
        'VAT': (4.92, 63.7),
        'Travel': (0.33, 63.5),
    }
    cats   = list(cat_data.keys())
    amts   = [v[0] for v in cat_data.values()]
    days   = [v[1] for v in cat_data.values()]
    x = np.arange(len(cats))
    w = 0.4

    ax2_twin = ax2.twinx()
    bars = ax2.bar(x - w/2, amts, w, color=COLORS['primary'], alpha=0.8, label='Amount (B VND)')
    ax2_twin.plot(x, days, 'D-', color=COLORS['warning'], linewidth=2, markersize=7, label='Avg Days')

    ax2.set_xticks(x)
    ax2.set_xticklabels(cats, rotation=30, ha='right', fontsize=8)
    ax2.set_ylabel('Amount (Billion VND)', fontsize=10, color=COLORS['primary'])
    ax2_twin.set_ylabel('Avg Days Outstanding', fontsize=10, color=COLORS['warning'])
    ax2.set_title('Amount vs Avg Days by Category', fontsize=12, fontweight='bold')
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=9)

    # Highlight VAT & Travel high days
    ax2.annotate('⚠ High\ndays', xy=(6, 4.92), xytext=(5, 25),
                 fontsize=8, color=COLORS['danger'],
                 arrowprops=dict(arrowstyle='->', color=COLORS['danger']))

    ax2.spines[['top','right']].set_visible(False)

    plt.tight_layout()
    plt.savefig(f"{OUTDIR}\\fq6_cost_expense.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ fq6_cost_expense.png")

# ── FQ7: Data Quality ─────────────────────────────────────────────────────────
def fq7_data_quality():
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(COLORS['bg'])
    fig.suptitle('Data Quality Report – 08_Finance_Accounting', fontsize=16, fontweight='bold')

    # Left: missing / anomaly counts
    ax = axes[0]
    ax.set_facecolor(COLORS['bg'])
    issues = {
        'Missing Payment Date': 141,
        'Missing Project Code': 305,
        'Missing PO Number'   : 397,
        'Missing Contract No.': 300,
        'Negative Amount_VND' :   8,
        'Negative Days_Outstd':  12,
        'VAT Rate 15% (Unusual)': 14,
        'TxnType Name Variant':   1,
    }
    keys = list(issues.keys())
    vals = list(issues.values())
    bar_c = [COLORS['danger'] if v > 100 else COLORS['warning'] for v in vals]
    bars = ax.barh(keys, vals, color=bar_c, edgecolor='white', height=0.6)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                str(val), va='center', fontsize=9)
    ax.set_xlabel('Count', fontsize=10)
    ax.set_title('Data Quality Issues Found', fontsize=12, fontweight='bold')
    ax.spines[['top','right']].set_visible(False)

    # Right: completeness radar / bar
    ax2 = axes[1]
    ax2.set_facecolor(COLORS['bg'])
    fields = ['Transaction_ID','Transaction_Date','Amount_VND','Department',
              'Approval_Status','Payment_Date','Project_Code','PO_Number']
    completeness = []
    for f in fields:
        if f in ['Project_Code','PO_Number','Payment_Date']:
            missing = df[f].isna().sum()
        else:
            missing = df[f].isna().sum()
        completeness.append(round((1 - missing/500) * 100, 1))

    bar_c2 = [COLORS['success'] if v >= 90 else (COLORS['warning'] if v >= 60 else COLORS['danger'])
              for v in completeness]
    bars2 = ax2.barh(fields, completeness, color=bar_c2, edgecolor='white', height=0.6)
    ax2.axvline(100, color=COLORS['neutral'], linestyle='--', linewidth=1, alpha=0.5)
    ax2.set_xlim(0, 110)
    ax2.set_xlabel('Completeness %', fontsize=10)
    ax2.set_title('Field Completeness Rate', fontsize=12, fontweight='bold')
    for bar, val in zip(bars2, completeness):
        ax2.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                 f'{val:.0f}%', va='center', fontsize=9)
    ax2.spines[['top','right']].set_visible(False)

    plt.tight_layout()
    plt.savefig(f"{OUTDIR}\\fq7_data_quality.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ fq7_data_quality.png")

# ── RUN ALL ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Running Finance & Accounting EDA...")
    fq1_transaction_overview()
    fq2_department_analysis()
    fq3_approval_overdue()
    fq4_budget_variance()
    fq5_monthly_trend()
    fq6_cost_expense()
    fq7_data_quality()
    print("\nAll 7 charts saved to:", OUTDIR)
