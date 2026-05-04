"""
ZORTHEX v1.0 — Public Attention Diffusion Lag Framework
Main Analysis Pipeline

Author: Renato [Surname], Independent Researcher, Italy
AI Assistance: Claude (Anthropic)
Version: 1.0 — May 2026
Status: Preliminary — not peer reviewed

Usage:
    python pipeline.py --technology "your technology" --file data/raw/your_file.csv
    
    Or run directly to reproduce all results:
    python pipeline.py --reproduce-all
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import argparse
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# ZORTHEX v1.0 — LOCKED DEFINITIONS
# Do not modify without incrementing version number
# ============================================================

VERSION = "1.0"

THRESHOLD_PRIMARY = 25      # Google Trends score threshold
WINDOW_PRIMARY = 3          # Consecutive months required
FALLBACK_PCT = 0.40         # Fallback: 40% of absolute peak

# Alternative definitions for robustness check
THRESHOLD_B = 15            # Version B: permissive threshold
WINDOW_B = 3
THRESHOLD_C = 25            # Version C: strict window
WINDOW_C = 6

# ============================================================
# CORE FUNCTIONS
# ============================================================

def load_google_trends(filepath):
    """
    Load Google Trends CSV file.
    Handles the standard Google Trends export format.
    
    Args:
        filepath: path to CSV file downloaded from trends.google.com
    
    Returns:
        DataFrame with columns: date (datetime), score (float)
    """
    df = pd.read_csv(filepath, skiprows=2)
    df.columns = ['date', 'score']
    df['date'] = pd.to_datetime(df['date'])
    # Handle "< 1" values from Google Trends
    df['score'] = pd.to_numeric(
        df['score'].astype(str).str.replace('< 1', '0.5'),
        errors='coerce'
    ).fillna(0)
    return df


def find_t_peak(df, threshold=THRESHOLD_PRIMARY, window=WINDOW_PRIMARY):
    """
    Find t_peak: first window of `window` consecutive months 
    with Google Trends score >= threshold.
    
    Fallback: if threshold never reached, use first window
    above 40% of absolute peak score.
    
    Args:
        df: DataFrame with date and score columns
        threshold: minimum score (default: 25)
        window: consecutive months required (default: 3)
    
    Returns:
        tuple: (t_peak datetime, rule_applied str)
    """
    above = df['score'] >= threshold
    for i in range(len(df) - window):
        if above.iloc[i:i+window].all():
            return df.iloc[i]['date'], 'primary'
    
    # Fallback rule
    fallback_threshold = df['score'].max() * FALLBACK_PCT
    above_fb = df['score'] >= fallback_threshold
    for i in range(len(df) - window):
        if above_fb.iloc[i:i+window].all():
            return df.iloc[i]['date'], f'fallback_{int(FALLBACK_PCT*100)}pct'
    
    # Last resort: absolute peak
    peak_idx = df['score'].idxmax()
    return df.loc[peak_idx, 'date'], 'absolute_peak'


def calculate_L(t_peak, t_start):
    """
    Calculate L = t_peak - t_start in months.
    
    Args:
        t_peak: pandas Timestamp
        t_start: pandas Timestamp
    
    Returns:
        int: L in months (minimum 0)
    """
    L = (t_peak.year - t_start.year) * 12 + (t_peak.month - t_start.month)
    return max(L, 0)


def robustness_check(df, t_start):
    """
    Calculate L under three alternative definitions.
    
    Returns:
        dict with L_A (primary), L_B (permissive), L_C (strict)
    """
    t_peak_A, rule_A = find_t_peak(df, THRESHOLD_PRIMARY, WINDOW_PRIMARY)
    t_peak_B, rule_B = find_t_peak(df, THRESHOLD_B, WINDOW_B)
    t_peak_C, rule_C = find_t_peak(df, THRESHOLD_C, WINDOW_C)
    
    return {
        'L_A': calculate_L(t_peak_A, t_start),
        'L_B': calculate_L(t_peak_B, t_start),
        'L_C': calculate_L(t_peak_C, t_start),
        'rule_A': rule_A,
        'rule_B': rule_B,
        'rule_C': rule_C,
        't_peak_A': t_peak_A,
        't_peak_B': t_peak_B,
        't_peak_C': t_peak_C,
    }


def analyze_single_technology(name, filepath, t_start, regime, notes=""):
    """
    Full analysis pipeline for a single technology.
    
    Args:
        name: technology name
        filepath: path to Google Trends CSV
        t_start: pandas Timestamp (first public emergence)
        regime: 'scientific', 'product', or 'slow-burn'
        notes: optional documentation notes
    
    Returns:
        dict with all computed values
    """
    print(f"\nAnalyzing: {name}")
    print(f"  t_start: {t_start.strftime('%Y-%m')}")
    
    df = load_google_trends(filepath)
    rb = robustness_check(df, t_start)
    
    print(f"  t_peak (primary): {rb['t_peak_A'].strftime('%Y-%m')} [{rb['rule_A']}]")
    print(f"  L = {rb['L_A']} months ({rb['L_A']/12:.1f} years)")
    print(f"  Robustness: L_A={rb['L_A']}, L_B={rb['L_B']}, L_C={rb['L_C']}")
    
    # Flag if definition-sensitive
    L_range = max(rb['L_A'], rb['L_B'], rb['L_C']) - min(rb['L_A'], rb['L_B'], rb['L_C'])
    if L_range > 12:
        print(f"  ⚠️  Definition-sensitive: range = {L_range} months")
    
    return {
        'technology': name,
        'regime': regime,
        't_start': t_start,
        't_peak': rb['t_peak_A'],
        'L_months': rb['L_A'],
        'L_years': round(rb['L_A'] / 12, 1),
        'L_B': rb['L_B'],
        'L_C': rb['L_C'],
        'rule_applied': rb['rule_A'],
        'peak_score': df['score'].max(),
        'pre_peak_mean': df[df['date'] < rb['t_peak_A']]['score'].mean(),
        'post_peak_mean': df[df['date'] >= rb['t_peak_A']]['score'].mean(),
        'notes': notes,
    }


def aggregate_statistics(results):
    """
    Compute aggregate statistics by regime.
    
    Args:
        results: list of dicts from analyze_single_technology
    
    Returns:
        dict with statistics per regime and overall
    """
    df = pd.DataFrame(results)
    stats_out = {}
    
    for regime in df['regime'].unique():
        subset = df[df['regime'] == regime]['L_months'].values
        stats_out[regime] = {
            'n': len(subset),
            'mean': round(np.mean(subset), 1),
            'std': round(np.std(subset), 1),
            'cv': round(np.std(subset) / np.mean(subset), 3) if np.mean(subset) > 0 else None,
            'min': min(subset),
            'max': max(subset),
            'values': list(subset)
        }
    
    # Cross-regime test
    sci = df[df['regime'] == 'scientific']['L_months'].values
    prod = df[df['regime'] == 'product']['L_months'].values
    
    if len(sci) >= 3 and len(prod) >= 3:
        u_stat, p_val = stats.mannwhitneyu(sci, prod, alternative='two-sided')
        stats_out['mann_whitney'] = {
            'statistic': round(u_stat, 1),
            'p_value': round(p_val, 4),
            'interpretation': 'significant (p<0.05)' if p_val < 0.05 else 'not significant (p>=0.05)',
            'caveat': 'small sample — interpret with caution'
        }
    
    return stats_out


def reproduce_all_results():
    """
    Reproduce all results from the v1.0 dataset.
    Requires data files in data/raw/ directory.
    """
    
    # Dataset configuration
    DATASET = [
        {
            'name': 'LLM',
            'file': 'data/raw/llm.csv',
            't_start': pd.Timestamp('2017-06-01'),
            'regime': 'scientific',
            'notes': 'Attention is all you need (Vaswani et al. 2017)'
        },
        {
            'name': 'mRNA vaccine',
            'file': 'data/raw/mrna.csv',
            't_start': pd.Timestamp('2015-01-01'),
            'regime': 'scientific',
            'notes': 'First mRNA therapeutic trials'
        },
        {
            'name': 'CRISPR',
            'file': 'data/raw/crispr.csv',
            't_start': pd.Timestamp('2012-06-01'),
            'regime': 'scientific',
            'notes': 'Doudna/Charpentier Science 2012'
        },
        {
            'name': 'Deep Learning',
            'file': 'data/raw/deep_learning.csv',
            't_start': pd.Timestamp('2012-09-01'),
            'regime': 'scientific',
            'notes': 'AlexNet ImageNet (Krizhevsky et al. 2012)'
        },
        {
            'name': 'VR',
            'file': 'data/raw/vr.csv',
            't_start': pd.Timestamp('2010-01-01'),
            'regime': 'slow-burn',
            'notes': 'First consumer VR development period'
        },
        {
            'name': 'Quantum Computing',
            'file': 'data/raw/quantum.csv',
            't_start': pd.Timestamp('2010-01-01'),
            'regime': 'slow-burn',
            'notes': 'IBM and Google early quantum research'
        },
        {
            'name': 'iPhone',
            'file': 'data/raw/iphone.csv',
            't_start': pd.Timestamp('2007-01-01'),
            'regime': 'product',
            'notes': 'Apple iPhone launch January 2007'
        },
        {
            'name': 'Cloud computing',
            'file': 'data/raw/cloud.csv',
            't_start': pd.Timestamp('2006-03-01'),
            'regime': 'product',
            'notes': 'AWS launch March 2006'
        },
        {
            'name': 'Facebook',
            'file': 'data/raw/facebook.csv',
            't_start': pd.Timestamp('2004-02-01'),
            'regime': 'product',
            'notes': 'Facebook launch February 2004'
        },
        {
            'name': 'Bitcoin',
            'file': 'data/raw/bitcoin.csv',
            't_start': pd.Timestamp('2008-10-01'),
            'regime': 'product',
            'notes': 'Nakamoto whitepaper October 2008'
        },
    ]
    
    results = []
    for tech in DATASET:
        if os.path.exists(tech['file']):
            r = analyze_single_technology(
                tech['name'], tech['file'],
                tech['t_start'], tech['regime'], tech['notes']
            )
            results.append(r)
        else:
            print(f"⚠️  File not found: {tech['file']} — skipping {tech['name']}")
    
    if results:
        stats_out = aggregate_statistics(results)
        
        print("\n" + "="*60)
        print("AGGREGATE STATISTICS BY REGIME")
        print("="*60)
        for regime, s in stats_out.items():
            if regime == 'mann_whitney':
                print(f"\nMann-Whitney (scientific vs product):")
                print(f"  U={s['statistic']}, p={s['p_value']} — {s['interpretation']}")
                print(f"  Caveat: {s['caveat']}")
            else:
                print(f"\n{regime.upper()} (n={s['n']}):")
                print(f"  Mean={s['mean']}m, Std={s['std']}m, CV={s['cv']}")
                print(f"  Range: {s['min']}–{s['max']} months")
        
        return results, stats_out
    
    return [], {}


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='ZORTHEX v1.0 — Public Attention Diffusion Lag Pipeline'
    )
    parser.add_argument('--reproduce-all', action='store_true',
                       help='Reproduce all v1.0 results')
    parser.add_argument('--technology', type=str, help='Technology name')
    parser.add_argument('--file', type=str, help='Path to Google Trends CSV')
    parser.add_argument('--t-start', type=str, help='t_start date (YYYY-MM)')
    parser.add_argument('--regime', type=str, 
                       choices=['scientific', 'product', 'slow-burn'],
                       help='Technology regime')
    
    args = parser.parse_args()
    
    print(f"ZORTHEX v{VERSION} — Public Attention Diffusion Lag Framework")
    print("Status: Preliminary — not peer reviewed")
    print("="*60)
    
    if args.reproduce_all:
        reproduce_all_results()
    elif args.technology and args.file and args.t_start and args.regime:
        t_start = pd.Timestamp(args.t_start + '-01')
        result = analyze_single_technology(
            args.technology, args.file, t_start, args.regime
        )
        print(f"\nResult: L = {result['L_months']} months ({result['L_years']} years)")
    else:
        print("\nUsage examples:")
        print("  python pipeline.py --reproduce-all")
        print("  python pipeline.py --technology 'Solar Energy' --file data/raw/solar.csv --t-start 2010-01 --regime scientific")
