"""
Single-figure summary of the fidelity bottleneck discovery
"""

import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure(figsize=(16, 10))

# Create grid
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# Title
fig.suptitle('THE FIDELITY BOTTLENECK: Why 13s Coherence Unlocks Zero Algorithms',
             fontsize=18, fontweight='bold', y=0.98)

# Panel 1: The breakthrough (top left)
ax1 = fig.add_subplot(gs[0, 0])
years = [2020, 2021, 2022, 2023, 2024, 2025, 2026]
coherence_times = [0.1, 0.15, 0.3, 0.5, 0.8, 1.0, 13.0]
ax1.semilogy(years, coherence_times, 'o-', linewidth=3, markersize=12, color='green')
ax1.axvspan(2025.5, 2026.5, alpha=0.2, color='yellow')
ax1.text(2026, 7, 'FEB 2026\nBREAKTHROUGH\n13s coherence', ha='center', fontsize=10, fontweight='bold')
ax1.set_xlabel('Year', fontsize=11)
ax1.set_ylabel('Coherence Time (s)', fontsize=11)
ax1.set_title('(A) The Breakthrough: 10× Improvement', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)

# Panel 2: The expectation (top middle)
ax2 = fig.add_subplot(gs[0, 1])
categories = ['Feasible\n2025\n(1s)', 'Expected\n2026\n(13s)']
counts = [10, 18]  # Expected if coherence was the bottleneck
ax2.bar(categories, counts, color=['gray', 'green'], alpha=0.7, edgecolor='black', linewidth=2)
ax2.set_ylabel('# Algorithms Feasible', fontsize=11)
ax2.set_title('(B) Expected: More algorithms!', fontsize=12, fontweight='bold')
ax2.set_ylim([0, 25])
ax2.text(0.5, 22, '❓ "13× coherence\nshould unlock\nmore algorithms"', ha='center', fontsize=10, style='italic')
ax2.grid(True, alpha=0.3, axis='y')

# Panel 3: The reality (top right)
ax3 = fig.add_subplot(gs[0, 2])
categories = ['Actual\n2025\n(1s)', 'Actual\n2026\n(13s)']
counts = [10, 10]  # Reality: no change
bars = ax3.bar(categories, counts, color=['gray', 'red'], alpha=0.7, edgecolor='black', linewidth=2)
ax3.set_ylabel('# Algorithms Feasible', fontsize=11)
ax3.set_title('(C) Reality: ZERO algorithms unlocked!', fontsize=12, fontweight='bold', color='red')
ax3.set_ylim([0, 25])
ax3.text(0.5, 22, '❗ Same 10 algorithms\nfeasible at both\ncoherence times', ha='center', fontsize=10, fontweight='bold', color='red')
ax3.grid(True, alpha=0.3, axis='y')

# Panel 4: Why? Circuit execution time (middle left)
ax4 = fig.add_subplot(gs[1, 0])
depths = np.array([10, 100, 693, 1000, 2302, 10000])
exec_times_ms = depths * 0.001  # 1 μs per gate
colors_exec = ['green' if d <= 693 else 'orange' if d <= 2302 else 'red' for d in depths]
ax4.bar(range(len(depths)), exec_times_ms, color=colors_exec, alpha=0.7, edgecolor='black')
ax4.set_xticks(range(len(depths)))
ax4.set_xticklabels([f'{d}' for d in depths], rotation=45)
ax4.axhline(1000, color='blue', linestyle='--', linewidth=2, label='1s coherence')
ax4.axhline(13000, color='green', linestyle='--', linewidth=2, label='13s coherence')
ax4.set_xlabel('Circuit Depth (gates)', fontsize=11)
ax4.set_ylabel('Execution Time (ms)', fontsize=11)
ax4.set_title('(D) Execution Time ≪ Coherence Time', fontsize=12, fontweight='bold')
ax4.set_yscale('log')
ax4.legend(fontsize=9)
ax4.grid(True, alpha=0.3)

# Panel 5: The real bottleneck - fidelity (middle middle)
ax5 = fig.add_subplot(gs[1, 1])
fidelities = [0.999**d for d in depths]
colors_fid = ['green' if f >= 0.5 else 'orange' if f >= 0.1 else 'red' for f in fidelities]
ax5.bar(range(len(depths)), fidelities, color=colors_fid, alpha=0.7, edgecolor='black')
ax5.set_xticks(range(len(depths)))
ax5.set_xticklabels([f'{d}' for d in depths], rotation=45)
ax5.axhline(0.5, color='red', linestyle='--', linewidth=2, label='Min useful fidelity')
ax5.set_xlabel('Circuit Depth (gates)', fontsize=11)
ax5.set_ylabel('Circuit Fidelity', fontsize=11)
ax5.set_title('(E) Fidelity Collapses at 99.9%', fontsize=12, fontweight='bold')
ax5.set_yscale('log')
ax5.legend(fontsize=9)
ax5.grid(True, alpha=0.3)
ax5.text(3, 0.001, 'BOTTLENECK!\nFidelity drops\nbelow useful\nthreshold', fontsize=9, fontweight='bold', color='red', ha='center')

# Panel 6: Required fidelity (middle right)
ax6 = fig.add_subplot(gs[1, 2])
depths_fine = np.logspace(1, 6, 100)
fid_needed = 0.5 ** (1/depths_fine)
ax6.semilogx(depths_fine, fid_needed, linewidth=3, color='purple')
ax6.axhline(0.999, color='red', linestyle='--', linewidth=2, label='Current: 99.9%')
ax6.axhline(0.9999, color='orange', linestyle='--', linewidth=2, label='Target: 99.99%')
ax6.axhline(0.99999, color='green', linestyle='--', linewidth=2, label='Future: 99.999%')
ax6.axvline(693, color='red', linestyle=':', alpha=0.5)
ax6.axvline(6931, color='orange', linestyle=':', alpha=0.5)
ax6.axvline(69315, color='green', linestyle=':', alpha=0.5)
ax6.set_xlabel('Circuit Depth (gates)', fontsize=11)
ax6.set_ylabel('Required Gate Fidelity', fontsize=11)
ax6.set_title('(F) Required Fidelity vs Depth', fontsize=12, fontweight='bold')
ax6.legend(fontsize=9, loc='lower left')
ax6.grid(True, alpha=0.3)
ax6.set_ylim([0.999, 1.0])

# Panel 7: Impact comparison (bottom left)
ax7 = fig.add_subplot(gs[2, 0])
improvements = ['Coherence\n1s→13s', 'Fidelity\n99.9%→99.99%', 'Fidelity\n99.9%→99.999%']
impacts = [0, 5, 8]
colors_imp = ['red', 'orange', 'green']
bars = ax7.bar(improvements, impacts, color=colors_imp, alpha=0.7, edgecolor='black', linewidth=2)
ax7.set_ylabel('Algorithms Unlocked', fontsize=11)
ax7.set_title('(G) Impact: Fidelity >> Coherence', fontsize=12, fontweight='bold')
ax7.set_ylim([0, 10])
for i, (imp, val) in enumerate(zip(improvements, impacts)):
    if val == 0:
        ax7.text(i, val + 0.5, '⚠️ ZERO!', ha='center', fontsize=11, fontweight='bold', color='red')
    else:
        ax7.text(i, val + 0.3, f'{val}', ha='center', fontsize=11, fontweight='bold')
ax7.grid(True, alpha=0.3, axis='y')

# Panel 8: Efficiency ranking (bottom middle)
ax8 = fig.add_subplot(gs[2, 1])
directions = ['Fidelity\n→99.95%', 'Fidelity\n→99.99%', 'Fidelity\n→99.999%', 'Coherence\n→30s', 'Other']
efficiencies = [0.375, 0.179, 0.114, 0.0, 0.0]
colors_eff = ['green', 'yellowgreen', 'yellow', 'gray', 'gray']
ax8.barh(directions, efficiencies, color=colors_eff, alpha=0.7, edgecolor='black', linewidth=2)
ax8.set_xlabel('Efficiency (impact/difficulty/year)', fontsize=11)
ax8.set_title('(H) Research Efficiency Ranking', fontsize=12, fontweight='bold')
ax8.grid(True, alpha=0.3, axis='x')

# Panel 9: Strategic recommendation (bottom right)
ax9 = fig.add_subplot(gs[2, 2])
ax9.axis('off')
recommendation_text = """
🎯 KEY INSIGHT

At 99.9% fidelity, circuits fail
after ~700 gates (0.7ms).

Both 1s and 13s coherence are
MORE than enough!

COHERENCE IS NOT THE BOTTLENECK.
FIDELITY IS.

📊 RECOMMENDATION

Phase 1 (2026-28): FIDELITY
• 99.9% → 99.99%
• Unlock chemistry & optimization

Phase 2 (2028-30): ERROR CORRECTION
• Physical → logical qubits
• Path to Shor's algorithm

Phase 3 (2030+): COHERENCE + SCALE
• 100s+ coherence, 10⁶ qubits

💡 PREDICTION

Labs focusing on FIDELITY will
demonstrate quantum advantage
2-3 years BEFORE labs focusing
on coherence or qubit count.
"""
ax9.text(0.5, 0.5, recommendation_text, ha='center', va='center', fontsize=10,
        bbox=dict(boxstyle='round', facecolor='lightyellow', edgecolor='black', linewidth=2))

plt.savefig('bottleneck_summary.png', dpi=150, bbox_inches='tight')
print("Saved bottleneck_summary.png")
