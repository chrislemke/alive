"""
OPTIMAL QUANTUM COMPUTING RESEARCH INVESTMENT STRATEGY

Based on analysis showing fidelity is the bottleneck, model:
1. Cost/difficulty of improving each metric
2. Impact on algorithm feasibility
3. Optimal allocation of research resources

Key insight: Not all improvements are equally valuable or equally achievable
"""

import numpy as np
import matplotlib.pyplot as plt
from coherence_threshold import ALGORITHMS, CoherenceModel
from typing import Dict, List, Tuple
import json
from datetime import datetime


class TechnologyImprovement:
    """Model a research direction with cost and impact"""

    def __init__(self, name: str, current_value: float, target_value: float,
                 difficulty: float, timeline_years: float):
        """
        Parameters:
        - name: Technology parameter being improved
        - current_value: Current achieved value (Feb 2026)
        - target_value: Target value for improvement
        - difficulty: Relative difficulty (1=easy, 10=extremely hard)
        - timeline_years: Estimated years to achieve target
        """
        self.name = name
        self.current_value = current_value
        self.target_value = target_value
        self.difficulty = difficulty
        self.timeline_years = timeline_years

    def __repr__(self):
        return f"{self.name}: {self.current_value} → {self.target_value} (difficulty={self.difficulty}, {self.timeline_years}yr)"


# Define improvement scenarios
IMPROVEMENTS = {
    # Coherence time improvements
    "coherence_conservative": TechnologyImprovement(
        "Coherence (13s → 30s)", 13.0, 30.0, difficulty=3, timeline_years=2
    ),
    "coherence_ambitious": TechnologyImprovement(
        "Coherence (13s → 100s)", 13.0, 100.0, difficulty=6, timeline_years=5
    ),

    # Gate fidelity improvements
    "fidelity_incremental": TechnologyImprovement(
        "Fidelity (99.9% → 99.95%)", 0.999, 0.9995, difficulty=4, timeline_years=2
    ),
    "fidelity_modest": TechnologyImprovement(
        "Fidelity (99.9% → 99.99%)", 0.999, 0.9999, difficulty=7, timeline_years=4
    ),
    "fidelity_aggressive": TechnologyImprovement(
        "Fidelity (99.9% → 99.999%)", 0.999, 0.99999, difficulty=10, timeline_years=7
    ),

    # Qubit count (less relevant for near-term)
    "qubits_scale": TechnologyImprovement(
        "Qubits (6k → 100k)", 6000, 100000, difficulty=5, timeline_years=3
    ),

    # Gate speed improvements
    "gate_speed": TechnologyImprovement(
        "Gate time (1μs → 0.1μs)", 1.0, 0.1, difficulty=6, timeline_years=4
    ),

    # Quantum error correction (enables logical qubits)
    "error_correction": TechnologyImprovement(
        "Error correction (physical → logical)", 0, 1, difficulty=8, timeline_years=5
    ),
}


def compute_impact(improvement: TechnologyImprovement, base_fidelity=0.999,
                  base_coherence=13.0, base_gate_time=1.0) -> Dict:
    """
    Compute impact of an improvement on algorithm feasibility

    Returns: {
        "algorithms_unlocked": int,
        "impact_per_difficulty": float,
        "impact_per_year": float,
        "unlocked_categories": dict
    }
    """

    # Baseline model
    model_baseline = CoherenceModel(gate_time_us=base_gate_time, gate_fidelity=base_fidelity)
    n_baseline = sum(1 for a in ALGORITHMS if model_baseline.is_feasible(a, base_coherence, safety_factor=3.0)[0])

    # Model after improvement
    new_fidelity = base_fidelity
    new_coherence = base_coherence
    new_gate_time = base_gate_time

    if "Coherence" in improvement.name:
        new_coherence = improvement.target_value
    elif "Fidelity" in improvement.name:
        new_fidelity = improvement.target_value
    elif "Gate time" in improvement.name:
        new_gate_time = improvement.target_value

    model_improved = CoherenceModel(gate_time_us=new_gate_time, gate_fidelity=new_fidelity)
    n_improved = sum(1 for a in ALGORITHMS if model_improved.is_feasible(a, new_coherence, safety_factor=3.0)[0])

    unlocked = n_improved - n_baseline

    # Count by category
    unlocked_by_category = {}
    for algo in ALGORITHMS:
        old = model_baseline.is_feasible(algo, base_coherence, safety_factor=3.0)[0]
        new = model_improved.is_feasible(algo, new_coherence, safety_factor=3.0)[0]
        if new and not old:
            unlocked_by_category[algo.category] = unlocked_by_category.get(algo.category, 0) + 1

    return {
        "algorithms_unlocked": unlocked,
        "impact_per_difficulty": unlocked / improvement.difficulty,
        "impact_per_year": unlocked / improvement.timeline_years,
        "efficiency_score": unlocked / (improvement.difficulty * improvement.timeline_years),
        "unlocked_categories": unlocked_by_category,
    }


def optimize_portfolio(budget_difficulty: float = 10.0) -> List[Tuple[str, float]]:
    """
    Find optimal allocation of research resources (greedy algorithm)

    Budget is in "difficulty units" (total research effort)
    Returns: List of (improvement_name, allocation) tuples
    """

    # Compute impact for each improvement
    impacts = {name: compute_impact(imp) for name, imp in IMPROVEMENTS.items()}

    # Sort by efficiency (impact per difficulty-year)
    sorted_improvements = sorted(
        impacts.items(),
        key=lambda x: x[1]["efficiency_score"],
        reverse=True
    )

    # Greedy allocation
    portfolio = []
    remaining_budget = budget_difficulty
    total_unlocked = 0

    for imp_name, impact in sorted_improvements:
        imp = IMPROVEMENTS[imp_name]
        cost = imp.difficulty

        if cost <= remaining_budget:
            portfolio.append((imp_name, 1.0))  # Full investment
            remaining_budget -= cost
            total_unlocked += impact["algorithms_unlocked"]
        elif remaining_budget > 0:
            fraction = remaining_budget / cost
            portfolio.append((imp_name, fraction))
            remaining_budget = 0
            total_unlocked += impact["algorithms_unlocked"] * fraction
            break

    return portfolio, total_unlocked


def visualize_investment_landscape():
    """Create comprehensive visualization of research investment options"""

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Compute all impacts
    impacts = {name: compute_impact(imp) for name, imp in IMPROVEMENTS.items()}

    # Plot 1: Impact vs Difficulty
    ax = axes[0, 0]

    names = list(IMPROVEMENTS.keys())
    difficulties = [IMPROVEMENTS[n].difficulty for n in names]
    unlocked = [impacts[n]["algorithms_unlocked"] for n in names]
    colors = ['blue' if 'Coherence' in IMPROVEMENTS[n].name
             else 'red' if 'Fidelity' in IMPROVEMENTS[n].name
             else 'green' if 'Error' in IMPROVEMENTS[n].name
             else 'orange' for n in names]

    for i, name in enumerate(names):
        ax.scatter(difficulties[i], unlocked[i], s=200, alpha=0.7, color=colors[i])
        ax.text(difficulties[i] + 0.2, unlocked[i], IMPROVEMENTS[name].name.split('(')[0],
               fontsize=8, verticalalignment='center')

    ax.set_xlabel('Difficulty (1=easy, 10=hard)', fontsize=12)
    ax.set_ylabel('Algorithms Unlocked', fontsize=12)
    ax.set_title('Impact vs Difficulty Trade-off', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='blue', label='Coherence time'),
        Patch(facecolor='red', label='Gate fidelity'),
        Patch(facecolor='green', label='Error correction'),
        Patch(facecolor='orange', label='Other'),
    ]
    ax.legend(handles=legend_elements, fontsize=10)

    # Plot 2: Efficiency score (impact per difficulty-year)
    ax = axes[0, 1]

    efficiency = [impacts[n]["efficiency_score"] for n in names]
    sorted_indices = np.argsort(efficiency)[::-1]

    bars = ax.barh([IMPROVEMENTS[names[i]].name for i in sorted_indices],
                  [efficiency[i] for i in sorted_indices],
                  color=[colors[i] for i in sorted_indices],
                  alpha=0.7)

    ax.set_xlabel('Efficiency Score (impact/difficulty/year)', fontsize=12)
    ax.set_title('Research Investment Efficiency Ranking', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')

    # Plot 3: Timeline vs Impact
    ax = axes[1, 0]

    timelines = [IMPROVEMENTS[n].timeline_years for n in names]

    for i, name in enumerate(names):
        ax.scatter(timelines[i], unlocked[i], s=difficulties[i]*30, alpha=0.7, color=colors[i])
        ax.text(timelines[i] + 0.1, unlocked[i], IMPROVEMENTS[name].name.split('(')[0],
               fontsize=8, verticalalignment='center')

    ax.set_xlabel('Timeline (years)', fontsize=12)
    ax.set_ylabel('Algorithms Unlocked', fontsize=12)
    ax.set_title('Impact vs Timeline (bubble size = difficulty)', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # Plot 4: Optimal portfolio
    ax = axes[1, 1]

    budgets = [5, 10, 15, 20]
    portfolio_results = []

    for budget in budgets:
        portfolio, total = optimize_portfolio(budget_difficulty=budget)
        portfolio_results.append((budget, total, portfolio))

    budget_vals = [r[0] for r in portfolio_results]
    total_unlocked = [r[1] for r in portfolio_results]

    ax.plot(budget_vals, total_unlocked, 'o-', linewidth=2, markersize=10, color='purple')

    ax.set_xlabel('Research Budget (difficulty units)', fontsize=12)
    ax.set_ylabel('Total Algorithms Unlocked', fontsize=12)
    ax.set_title('Returns on Research Investment', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('quantum_investment_strategy.png', dpi=150, bbox_inches='tight')
    print("Saved visualization to quantum_investment_strategy.png")

    return portfolio_results


def generate_strategy_report():
    """Generate comprehensive research investment strategy report"""

    print("\n" + "=" * 80)
    print("OPTIMAL QUANTUM COMPUTING RESEARCH INVESTMENT STRATEGY")
    print("=" * 80)

    # Compute impacts
    impacts = {name: compute_impact(imp) for name, imp in IMPROVEMENTS.items()}

    # Sort by efficiency
    sorted_by_efficiency = sorted(
        impacts.items(),
        key=lambda x: x[1]["efficiency_score"],
        reverse=True
    )

    print("\n📊 RESEARCH DIRECTIONS RANKED BY EFFICIENCY:")
    print(f"{'Rank':<5} {'Direction':<40} {'Unlocked':<10} {'Difficulty':<12} {'Timeline':<10} {'Efficiency':<12}")
    print("-" * 100)

    for i, (name, impact) in enumerate(sorted_by_efficiency, 1):
        imp = IMPROVEMENTS[name]
        print(f"{i:<5} {imp.name:<40} {impact['algorithms_unlocked']:<10} "
              f"{imp.difficulty:<12.1f} {imp.timeline_years:<10.1f} {impact['efficiency_score']:<12.3f}")

    print("\n🎯 TOP 3 HIGHEST IMPACT (absolute):")
    sorted_by_impact = sorted(impacts.items(), key=lambda x: x[1]["algorithms_unlocked"], reverse=True)
    for i, (name, impact) in enumerate(sorted_by_impact[:3], 1):
        imp = IMPROVEMENTS[name]
        print(f"  {i}. {imp.name}: unlocks {impact['algorithms_unlocked']} algorithms")
        if impact['unlocked_categories']:
            cats = ", ".join(f"{k}={v}" for k, v in impact['unlocked_categories'].items())
            print(f"     Categories: {cats}")

    print("\n🚀 TOP 3 BEST EFFICIENCY (impact per difficulty-year):")
    for i, (name, impact) in enumerate(sorted_by_efficiency[:3], 1):
        imp = IMPROVEMENTS[name]
        print(f"  {i}. {imp.name}: efficiency = {impact['efficiency_score']:.3f}")
        print(f"     ({impact['algorithms_unlocked']} algorithms / {imp.difficulty} difficulty / {imp.timeline_years} years)")

    print("\n💰 OPTIMAL PORTFOLIO ALLOCATION:")
    budgets = [5, 10, 15, 20]
    for budget in budgets:
        portfolio, total = optimize_portfolio(budget_difficulty=budget)
        print(f"\n  Budget = {budget} difficulty units → {total:.1f} algorithms unlocked:")
        for imp_name, fraction in portfolio:
            if fraction > 0.01:  # Only show >1% allocations
                print(f"    • {IMPROVEMENTS[imp_name].name}: {fraction*100:.0f}% allocation")

    print("\n🔬 KEY STRATEGIC INSIGHTS:")
    print("\n  1. FIDELITY > COHERENCE for near-term impact")
    fid_impact = sum(impacts[k]["algorithms_unlocked"] for k in impacts if "Fidelity" in k)
    coh_impact = sum(impacts[k]["algorithms_unlocked"] for k in impacts if "Coherence" in k)
    print(f"     Fidelity improvements: {fid_impact} algorithms unlocked")
    print(f"     Coherence improvements: {coh_impact} algorithms unlocked")
    print(f"     Ratio: {fid_impact/max(1,coh_impact):.1f}× more impact from fidelity")

    print("\n  2. DIMINISHING RETURNS beyond 13s coherence")
    print(f"     Coherence 13s→30s unlocks {impacts['coherence_conservative']['algorithms_unlocked']} algorithms")
    print(f"     Coherence 13s→100s unlocks {impacts['coherence_ambitious']['algorithms_unlocked']} algorithms")
    print(f"     Conclusion: Additional coherence gains have limited value at current fidelity")

    print("\n  3. INCREMENTAL FIDELITY improvements are HIGH VALUE")
    print(f"     Even 99.9%→99.95% unlocks {impacts['fidelity_incremental']['algorithms_unlocked']} algorithms (difficulty=4)")
    print(f"     Full 99.9%→99.99% unlocks {impacts['fidelity_modest']['algorithms_unlocked']} algorithms (difficulty=7)")
    print(f"     Efficiency: incremental approach is {impacts['fidelity_incremental']['efficiency_score']/impacts['fidelity_modest']['efficiency_score']:.1f}× more efficient")

    print("\n  4. ERROR CORRECTION is long-term path to scaling")
    print(f"     Difficulty: {IMPROVEMENTS['error_correction'].difficulty}/10 (very hard)")
    print(f"     Timeline: {IMPROVEMENTS['error_correction'].timeline_years} years")
    print(f"     But necessary for >10^6 gate algorithms (Shor, etc.)")

    print("\n📈 RECOMMENDED RESEARCH PRIORITIES (2026-2030):")
    print("\n  Phase 1 (2026-2028): Focus on FIDELITY")
    print("    • Target: 99.9% → 99.95% (incremental improvement)")
    print("    • Methods: Better laser control, improved qubit isolation, enhanced calibration")
    print("    • Impact: Unlocks quantum chemistry, QAOA, near-term applications")

    print("\n  Phase 2 (2028-2030): Advance ERROR CORRECTION")
    print("    • Target: Physical → logical qubits with surface codes")
    print("    • Methods: Improved syndrome extraction, faster decode, higher code distance")
    print("    • Impact: Path to Shor's algorithm, fault-tolerant quantum computing")

    print("\n  Phase 3 (2030+): Optimize COHERENCE and SCALE")
    print("    • Target: 100s+ coherence, 10^6+ qubits")
    print("    • Methods: Better vacuum, cryogenic systems, architectural innovations")
    print("    • Impact: Large-scale quantum simulation, cryptography")

    print("\n⚠️  DE-PRIORITIZE (diminishing returns):")
    print("    • Coherence beyond 30s (limited value without better fidelity)")
    print("    • Qubit count beyond 10^5 (need error correction first)")
    print("    • Gate speed improvements (1μs is adequate for near-term)")

    print("\n💡 TESTABLE PREDICTION:")
    print("    Labs focusing on fidelity (99.9%→99.99%) will demonstrate quantum")
    print("    advantage for chemistry/optimization 2-3 years BEFORE labs focusing")
    print("    solely on coherence time or qubit count.")

    print("=" * 80)

    return {
        "timestamp": datetime.now().isoformat(),
        "rankings": {
            "by_efficiency": [
                {
                    "name": IMPROVEMENTS[name].name,
                    "efficiency": impact["efficiency_score"],
                    "algorithms_unlocked": impact["algorithms_unlocked"],
                    "difficulty": IMPROVEMENTS[name].difficulty,
                    "timeline_years": IMPROVEMENTS[name].timeline_years,
                }
                for name, impact in sorted_by_efficiency
            ],
            "by_impact": [
                {
                    "name": IMPROVEMENTS[name].name,
                    "algorithms_unlocked": impact["algorithms_unlocked"],
                }
                for name, impact in sorted_by_impact
            ],
        },
        "strategic_insights": {
            "fidelity_vs_coherence_ratio": fid_impact / max(1, coh_impact),
            "recommended_phase_1": "Fidelity 99.9% → 99.95%",
            "recommended_phase_2": "Error correction (logical qubits)",
            "recommended_phase_3": "Coherence + scale",
        }
    }


if __name__ == "__main__":
    portfolio_results = visualize_investment_landscape()
    report = generate_strategy_report()

    with open(f"quantum_strategy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(report, f, indent=2)
