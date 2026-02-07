#!/usr/bin/env python3
"""
Create a single clear summary plot for Cycle 28
"""

import numpy as np
import matplotlib.pyplot as plt
import json

# Load results
with open('/home/dev/mnt/early_universe_simulation_20260207_095426.json', 'r') as f:
    sim_results = json.load(f)

with open('/home/dev/mnt/observational_tests_20260207_095603.json', 'r') as f:
    obs_results = json.load(f)

# Extract data
models = [r['model'] for r in sim_results['results']]
L_UV = [r['L_UV'] for r in sim_results['results']]
M_stars = [r['M_stars'] for r in sim_results['results']]

beta = [m['UV_slope_beta'] for m in obs_results['models']]
OIII = [m['OIII_Hbeta'] for m in obs_results['models']]
size = [m['half_light_radius_kpc'] for m in obs_results['models']]

# Create summary figure
fig = plt.figure(figsize=(16, 5))

# Panel 1: Luminosity comparison
ax1 = plt.subplot(1, 3, 1)
baseline = L_UV[0]
boosts = [L / baseline for L in L_UV]
colors = ['gray', 'blue', 'red', 'purple', 'orange']
bars = ax1.bar(range(len(models)), boosts, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)

# Add labels on bars
for i, (bar, boost) in enumerate(zip(bars, boosts)):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
             f'{boost:.2f}×', ha='center', va='bottom', fontsize=11, fontweight='bold')

ax1.axhline(y=2.0, color='black', linestyle='--', linewidth=2.5, label='JWST 2× Excess', zorder=0)
ax1.axhline(y=1.0, color='gray', linestyle='-', linewidth=1, alpha=0.5, zorder=0)
ax1.set_ylabel('Brightness vs Standard Model', fontsize=12, fontweight='bold')
ax1.set_title('Hypothesis Testing: Can Model Explain JWST?', fontsize=13, fontweight='bold')
ax1.set_xticks(range(len(models)))
ax1.set_xticklabels(models, rotation=25, ha='right', fontsize=10)
ax1.set_ylim(0, 4.5)
ax1.grid(True, alpha=0.3, axis='y')
ax1.legend(fontsize=11, loc='upper left')

# Add pass/fail markers
for i, boost in enumerate(boosts):
    marker = '✓' if boost >= 2.0 else '✗'
    color_marker = 'green' if boost >= 2.0 else 'red'
    ax1.text(i, 4.2, marker, ha='center', fontsize=20, color=color_marker, fontweight='bold')

# Panel 2: Observational discrimination (β vs [OIII]/Hβ)
ax2 = plt.subplot(1, 3, 2)
for i, (b, o, m) in enumerate(zip(beta, OIII, models)):
    ax2.scatter(b, o, s=300, color=colors[i], alpha=0.7, edgecolor='black', linewidth=2, label=m, zorder=10)
    ax2.text(b, o, m.split()[0], ha='center', va='center', fontsize=8, fontweight='bold')

# Add JWST observational regions
ax2.axvspan(-2.5, -2.0, alpha=0.1, color='blue', label='JWST β range')
ax2.axhspan(3, 8, alpha=0.1, color='green', label='JWST [OIII]/Hβ range')
ax2.axhline(y=8, color='red', linestyle='--', linewidth=2, alpha=0.7, label='AGN threshold')

ax2.set_xlabel('UV Slope β', fontsize=12, fontweight='bold')
ax2.set_ylabel('[OIII]/Hβ Ratio', fontsize=12, fontweight='bold')
ax2.set_title('Observational Discrimination', fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.set_xlim(-3.0, -1.0)
ax2.set_ylim(0, 12)

# Panel 3: Size-Luminosity relation
ax3 = plt.subplot(1, 3, 3)
for i, (s, L, m) in enumerate(zip(size, L_UV, models)):
    ax3.scatter(np.log10(L), s, s=300, color=colors[i], alpha=0.7, edgecolor='black', linewidth=2, label=m, zorder=10)
    ax3.text(np.log10(L), s, m.split()[0], ha='center', va='center', fontsize=8, fontweight='bold')

# Add JWST compact size region
ax3.axhspan(0.1, 0.3, alpha=0.1, color='blue', label='JWST compact')

ax3.set_xlabel('log(L_UV) [erg/s]', fontsize=12, fontweight='bold')
ax3.set_ylabel('Half-Light Radius [kpc]', fontsize=12, fontweight='bold')
ax3.set_title('Size-Luminosity Relation', fontsize=13, fontweight='bold')
ax3.grid(True, alpha=0.3)
ax3.set_ylim(0, 0.4)

plt.suptitle('Early Universe Brightness Puzzle: JWST z~10 Galaxies (Feb 2026)\nThree Viable Models: Enhanced SFE, Top-Heavy IMF, Combined',
             fontsize=14, fontweight='bold', y=1.02)

plt.tight_layout()
plt.savefig('/home/dev/mnt/cycle_028_summary_plot.png', dpi=150, bbox_inches='tight')
print("✓ Summary plot saved to /home/dev/mnt/cycle_028_summary_plot.png")
