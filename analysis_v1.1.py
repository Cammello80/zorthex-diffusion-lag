"""
ZORTHEX v1.1 — Public Attention Diffusion Lag
Model with explicit uncertainty and censoring correction

Changes from v1.0:
- Added uncertainty_low / uncertainty_high per observation
- Added censoring_flag (none / left-censored / right-censored / ambiguous)
- Added data_quality_score (0-1)
- Domain stratification instead of single cluster
- Removed claim of "stable cluster" — replaced with "observed distribution"
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# LOAD v1.1 DATASET
# ============================================================

df = pd.read_csv('/home/claude/zorthex_repo/results/L_values_v1.1.csv')

# Separate valid observations from censored
valid = df[df['censoring_flag'] == 'none'].copy()
censored = df[df['censoring_flag'] != 'none'].copy()

print("ZORTHEX v1.1 — DOMAIN STRATIFICATION")
print("="*65)
print(f"Total observations: {len(df)}")
print(f"Valid (observable): {len(valid)}")
print(f"Censored (not observable): {len(censored)}")
print()

# ============================================================
# DOMAIN STATISTICS
# ============================================================

print("STATISTICS BY DOMAIN (valid observations only)")
print("="*65)

domain_stats = {}
for domain in valid['domain'].unique():
    subset = valid[valid['domain'] == domain]
    L_vals = subset['L_months'].values
    
    if len(L_vals) >= 2:
        mean_L = np.mean(L_vals)
        std_L = np.std(L_vals)
        cv = std_L / mean_L if mean_L > 0 else None
    else:
        mean_L = L_vals[0] if len(L_vals) == 1 else None
        std_L = None
        cv = None
    
    domain_stats[domain] = {
        'n': len(L_vals),
        'mean': mean_L,
        'std': std_L,
        'cv': cv,
        'range': f"{min(L_vals)}-{max(L_vals)}",
        'technologies': list(subset['technology'].values)
    }
    
    print(f"\n{domain.upper()} (n={len(L_vals)}):")
    print(f"  Technologies: {', '.join(subset['technology'].values)}")
    print(f"  L values: {list(L_vals)}")
    if mean_L:
        print(f"  Mean: {mean_L:.1f}m | Std: {std_L:.1f}m | CV: {cv:.3f}" if std_L else f"  Mean: {mean_L:.1f}m (single observation)")
    print(f"  Range: {min(L_vals)}-{max(L_vals)} months")

# ============================================================
# OVERALL DISTRIBUTION (valid only)
# ============================================================

print("\n" + "="*65)
print("OVERALL DISTRIBUTION (valid observations, n={})".format(len(valid)))
print("="*65)
print(f"Mean L:   {valid['L_months'].mean():.1f} months")
print(f"Median L: {valid['L_months'].median():.1f} months")
print(f"Std L:    {valid['L_months'].std():.1f} months")
print(f"CV:       {valid['L_months'].std()/valid['L_months'].mean():.3f}")
print(f"Range:    {valid['L_months'].min()}-{valid['L_months'].max()} months")
print()
print("CORRECT INTERPRETATION:")
print("The observed distribution of L spans approximately 29-187 months")
print("with a concentration between 50-90 months for most observable cases.")
print("This is NOT a tight cluster — it is a broad distribution with")
print("domain-specific variation, censored data, and selection bias.")

# ============================================================
# VISUALIZATION WITH ERROR BARS
# ============================================================

fig, axes = plt.subplots(1, 2, figsize=(18, 9))
fig.patch.set_facecolor('#0a0a1a')

DOMAIN_COLORS = {
    'AI': '#00b4d8',
    'biotech_medical': '#e63946',
    'consumer_tech': '#a8a8a8',
    'financial_tech': '#f4a261',
    'infrastructure': '#ff9f1c',
    'materials_science': '#ffd166'
}

ax1, ax2 = axes
for ax in axes:
    ax.set_facecolor('#0d0d2b')
    ax.tick_params(colors='#aaaaaa', labelsize=8)
    ax.spines[:].set_color('#333366')

# --- Plot 1: L with error bars per technology ---
valid_sorted = valid.sort_values('L_months')

y_pos = range(len(valid_sorted))
colors = [DOMAIN_COLORS.get(d, '#ffffff') for d in valid_sorted['domain']]

# Error bars
xerr_low = valid_sorted['L_months'] - valid_sorted['uncertainty_low']
xerr_high = valid_sorted['uncertainty_high'] - valid_sorted['L_months']

ax1.barh(list(y_pos), valid_sorted['L_months'],
         color=colors, alpha=0.7, edgecolor='white', linewidth=0.5)

ax1.errorbar(valid_sorted['L_months'], list(y_pos),
            xerr=[xerr_low.fillna(0), xerr_high.fillna(0)],
            fmt='none', color='white', alpha=0.6, capsize=4, linewidth=1.5)

# Censored marker
for _, row in censored.iterrows():
    ax1.annotate(f"{row['technology']} [CENSORED]",
                xy=(5, len(valid_sorted) - 0.5),
                color='#ffd166', fontsize=7, style='italic')

ax1.set_yticks(list(y_pos))
ax1.set_yticklabels(
    [f"{row['technology']}\n[{row['domain'][:6]}]"
     for _, row in valid_sorted.iterrows()],
    color='white', fontsize=7
)

ax1.set_xlabel('L — months (with uncertainty range)', color='#aaaaaa', fontsize=9)
ax1.set_title('Public Attention Diffusion Lag — v1.1\nWith explicit uncertainty (error bars) and domain stratification',
             color='white', fontsize=10, pad=10)

# Shaded region 50-90
ax1.axvspan(50, 90, alpha=0.08, color='white', label='Observed concentration 50-90m')
ax1.axvline(x=valid['L_months'].mean(), color='white', linestyle='--',
           linewidth=1, alpha=0.5, label=f'Mean={valid["L_months"].mean():.0f}m')
ax1.legend(fontsize=7, facecolor='#0d0d2b', labelcolor='white')

# Legend
legend_patches = [mpatches.Patch(color=c, alpha=0.8, label=d)
                 for d, c in DOMAIN_COLORS.items() if d in valid['domain'].values]
ax1.legend(handles=legend_patches, fontsize=7, facecolor='#0d0d2b',
          labelcolor='white', loc='lower right')

# --- Plot 2: Domain comparison ---
domains_with_data = [(d, s) for d, s in domain_stats.items() if s['n'] >= 1]

for i, (domain, s) in enumerate(domains_with_data):
    subset = valid[valid['domain'] == domain]
    color = DOMAIN_COLORS.get(domain, '#ffffff')

    ax2.scatter([i] * len(subset), subset['L_months'],
               color=color, s=100, zorder=5,
               edgecolors='white', linewidth=1, alpha=0.9)

    for _, row in subset.iterrows():
        ax2.annotate(row['technology'].split()[0],
                    (i, row['L_months']),
                    textcoords="offset points",
                    xytext=(8, 0), color='white', fontsize=6)

    if s['mean'] and s['std']:
        ax2.errorbar([i], [s['mean']], yerr=[[s['std']], [s['std']]],
                    fmt='D', color=color, markersize=10,
                    ecolor=color, elinewidth=2, capsize=5,
                    zorder=6, markeredgecolor='white', markeredgewidth=1.5)
        ax2.text(i, s['mean'] + s['std'] + 5,
                f"μ={s['mean']:.0f}m\nσ={s['std']:.0f}m",
                ha='center', color=color, fontsize=7, fontweight='bold')

ax2.axhspan(50, 90, alpha=0.08, color='white', label='Observed concentration 50-90m')
ax2.set_xticks(range(len(domains_with_data)))
ax2.set_xticklabels([d[0].replace('_', '\n') for d in domains_with_data],
                   color='white', fontsize=7)
ax2.set_ylabel('L (months)', color='#aaaaaa', fontsize=9)
ax2.set_title('Domain Stratification\n(◆ = domain mean ± std)',
             color='white', fontsize=10, pad=10)
ax2.legend(fontsize=7, facecolor='#0d0d2b', labelcolor='white')

ax2.text(0.5, 0.02,
        "NOT a tight cluster — a broad distribution with domain variation,\ncensored data, and selection bias. Interpret with caution.",
        transform=ax2.transAxes, ha='center', va='bottom',
        color='#888888', fontsize=7, style='italic')

plt.suptitle(
    "ZORTHEX v1.1 — Public Attention Diffusion Lag\n"
    "Observed distribution with explicit uncertainty | NOT a universal law",
    color='white', fontsize=12, fontweight='bold', y=1.01
)

plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/zorthex_v1.1.png',
           dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
plt.close()
print("\nVisualization saved.")
