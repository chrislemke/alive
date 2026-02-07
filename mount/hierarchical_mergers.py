#!/usr/bin/env python3
"""
Hierarchical Black Hole Merger Model

Simulates multiple generations of BH mergers to determine if mass-gap
black holes can form through hierarchical growth.

Key physics:
1. Each merger: M_final = M1 + M2 - E_rad/c² (radiated energy)
2. Spin evolution: Mergers can spin up or down depending on alignment
3. Retention probability: In clusters, some BHs are ejected (recoil kicks)
4. Time delays: Dynamical interactions take time

This tests if GW231123 (100 M☉ + 140 M☉) can form from successive mergers
of smaller BHs that formed below the PISN mass gap.

References:
- Gerosa & Berti 2017 (hierarchical mergers in clusters)
- Rodriguez et al. 2019 (dynamical assembly)
- Fishbach et al. 2017 (mass distribution implications)
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple
import json


@dataclass
class BlackHole:
    """A black hole with mass and spin"""
    mass: float  # Solar masses
    spin: float  # Dimensionless spin parameter χ ∈ [0, 1]
    generation: int  # 0 = stellar remnant, 1 = 1st gen merger, etc.
    formation_time: float  # Gyr


class HierarchicalMergerModel:
    """
    Simulate hierarchical black hole mergers in dense stellar environments.

    Environments:
    - Globular clusters: σ ~ 10 km/s, escape velocity moderate
    - Nuclear star clusters: σ ~ 100 km/s, deep potential well
    - AGN disks: gas dynamics, aligned spins
    """

    def __init__(self, environment: str = 'globular_cluster'):
        self.environment = environment

        # Initial mass function for first-generation BHs (from stellar collapse)
        # Limited to masses BELOW the PISN gap (< 50 M☉)
        self.M_min = 5.0   # Minimum BH mass
        self.M_max = 50.0  # Maximum from stellar evolution (below PISN gap)

        # Environment-dependent parameters
        if environment == 'globular_cluster':
            self.v_escape = 50.0  # km/s (typical escape velocity)
            self.retention_factor = 0.3  # 30% of mergers retained
            self.merger_timescale = 0.1  # Gyr per generation
        elif environment == 'nuclear_cluster':
            self.v_escape = 200.0  # km/s (deep potential)
            self.retention_factor = 0.7  # 70% retained
            self.merger_timescale = 0.05  # Faster mergers
        elif environment == 'agn_disk':
            self.v_escape = 1000.0  # km/s (AGN potential)
            self.retention_factor = 0.95  # Almost all retained
            self.merger_timescale = 0.01  # Very fast (gas-driven)
        else:
            raise ValueError(f"Unknown environment: {environment}")

    def initial_bh_population(self, N: int = 1000) -> List[BlackHole]:
        """
        Generate initial population of BHs from stellar evolution.

        Mass distribution: dN/dM ∝ M^(-2.3) (Salpeter-like for remnants)
        All are generation 0 (direct stellar collapse).
        Spins are drawn from distribution (moderate, 0.2-0.7).
        """
        # Power-law mass distribution
        alpha = -2.3
        u = np.random.random(N)
        masses = (self.M_min**(alpha+1) + u * (self.M_max**(alpha+1) - self.M_min**(alpha+1)))**(1/(alpha+1))

        # Spin distribution: Gaussian centered at 0.3 (stellar BHs have moderate spin)
        spins = np.random.normal(0.3, 0.15, N)
        spins = np.clip(spins, 0.0, 0.95)  # Physical bounds

        population = [
            BlackHole(mass=m, spin=s, generation=0, formation_time=0.0)
            for m, s in zip(masses, spins)
        ]

        return population

    def merger_remnant(self, bh1: BlackHole, bh2: BlackHole, time: float) -> Tuple[BlackHole, bool]:
        """
        Compute remnant from merging bh1 + bh2.

        Returns (remnant, retained) where retained=True if BH stays in cluster.

        Physics:
        1. Final mass: M_f = M1 + M2 - E_rad
           E_rad ~ 0.05 * (M1*M2)/(M1+M2) * M_total (typical for comparable masses)

        2. Final spin: Complex function of mass ratio and spins
           Simplified: χ_f ~ weighted average + contribution from orbital angular momentum

        3. Recoil kick: Asymmetric GW emission gives velocity kick
           v_kick ~ 100-1000 km/s depending on mass ratio and spin alignment
           If v_kick > v_escape, BH is ejected
        """
        M1, M2 = bh1.mass, bh2.mass
        χ1, χ2 = bh1.spin, bh2.spin

        # Total mass
        M_total = M1 + M2

        # Radiated energy (~ 5% for comparable masses, less for unequal)
        q = min(M1, M2) / max(M1, M2)  # Mass ratio q ∈ [0, 1]
        eta = q / (1 + q)**2  # Symmetric mass ratio
        E_rad_fraction = 0.05 * eta / 0.25  # Normalized to equal masses

        M_final = M_total * (1 - E_rad_fraction)

        # Final spin (approximate formula from numerical relativity fits)
        # For aligned spins: χ_f ≈ (χ1 + q²χ2)/(1+q²) + contribution from orbital L
        χ_orbital = np.sqrt(12) * eta  # Orbital contribution (maximally ~0.69)
        χ_weighted = (χ1 + q**2 * χ2) / (1 + q**2)
        χ_final = min(χ_weighted + 0.5 * χ_orbital, 0.998)  # Physical limit

        # Recoil kick velocity (simplified)
        # Large kicks for: unequal masses, anti-aligned spins, precessing spins
        # Typical: 100-500 km/s, extreme: up to 5000 km/s
        # For simplicity: v_kick ~ 200 * (1 - q) + random component
        v_kick_base = 200 * (1 - q)  # Asymmetry contribution
        v_kick_spin = 100 * abs(χ1 - χ2)  # Spin asymmetry
        v_kick_random = np.random.rayleigh(150)  # Stochastic component
        v_kick = v_kick_base + v_kick_spin + v_kick_random

        # Check retention
        retained = (v_kick < self.v_escape) and (np.random.random() < self.retention_factor)

        # Create remnant
        generation = max(bh1.generation, bh2.generation) + 1
        remnant = BlackHole(
            mass=M_final,
            spin=χ_final,
            generation=generation,
            formation_time=time
        )

        return remnant, retained

    def evolve_cluster(
        self,
        initial_population: List[BlackHole],
        num_generations: int = 5,
        target_mass: float = None
    ) -> dict:
        """
        Evolve cluster through multiple generations of mergers.

        At each generation:
        1. Randomly pair BHs
        2. Merge them
        3. Check retention
        4. Add retained remnants to next generation

        Stop when:
        - num_generations reached, OR
        - target_mass achieved, OR
        - population exhausted
        """
        population = initial_population.copy()
        history = {
            'generation_0': {
                'population': initial_population,
                'masses': [bh.mass for bh in initial_population],
                'spins': [bh.spin for bh in initial_population],
                'count': len(initial_population)
            }
        }

        current_time = 0.0

        for gen in range(1, num_generations + 1):
            current_time += self.merger_timescale

            if len(population) < 2:
                print(f"  Generation {gen}: Population exhausted")
                break

            # Shuffle and pair
            np.random.shuffle(population)
            num_pairs = len(population) // 2

            new_population = []
            mergers_this_gen = 0
            retained_this_gen = 0

            for i in range(num_pairs):
                bh1 = population[2*i]
                bh2 = population[2*i + 1]

                remnant, retained = self.merger_remnant(bh1, bh2, current_time)
                mergers_this_gen += 1

                if retained:
                    new_population.append(remnant)
                    retained_this_gen += 1

            # Add leftover BH if odd population
            if len(population) % 2 == 1:
                new_population.append(population[-1])

            # Record this generation
            history[f'generation_{gen}'] = {
                'population': new_population,
                'masses': [bh.mass for bh in new_population],
                'spins': [bh.spin for bh in new_population],
                'count': len(new_population),
                'mergers': mergers_this_gen,
                'retained': retained_this_gen,
                'retention_rate': retained_this_gen / mergers_this_gen if mergers_this_gen > 0 else 0
            }

            population = new_population

            # Check if target mass achieved
            if target_mass and any(bh.mass >= target_mass for bh in population):
                max_bh = max(population, key=lambda bh: bh.mass)
                print(f"  Generation {gen}: Reached target! M={max_bh.mass:.1f} M☉, χ={max_bh.spin:.3f}")
                break

        return history

    def can_reach_mass(
        self,
        target_mass: float,
        num_trials: int = 50,
        max_generations: int = 10
    ) -> dict:
        """
        Monte Carlo: What fraction of trials reach the target mass?
        """
        successes = 0
        successful_spins = []
        successful_generations = []

        for trial in range(num_trials):
            population = self.initial_bh_population(N=500)
            history = self.evolve_cluster(population, max_generations, target_mass)

            # Check final population
            final_gen = max([int(k.split('_')[1]) for k in history.keys()])
            final_pop = history[f'generation_{final_gen}']['population']

            max_mass = max([bh.mass for bh in final_pop]) if final_pop else 0

            if max_mass >= target_mass * 0.95:  # Within 5%
                successes += 1
                max_bh = max(final_pop, key=lambda bh: bh.mass)
                successful_spins.append(max_bh.spin)
                successful_generations.append(max_bh.generation)

        return {
            'target_mass': target_mass,
            'success_rate': successes / num_trials,
            'num_trials': num_trials,
            'environment': self.environment,
            'typical_spin': np.mean(successful_spins) if successful_spins else None,
            'spin_std': np.std(successful_spins) if successful_spins else None,
            'typical_generation': np.mean(successful_generations) if successful_generations else None
        }

    def plot_mass_growth(self, history: dict, save_path: str = None):
        """Visualize mass and spin evolution across generations"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Panel 1: Mass distribution evolution
        ax = axes[0, 0]
        generations = sorted([int(k.split('_')[1]) for k in history.keys()])

        for gen in generations:
            masses = history[f'generation_{gen}']['masses']
            if masses:
                ax.hist(masses, bins=30, alpha=0.5, label=f'Gen {gen}',
                       range=(0, max([max(history[f'generation_{g}']['masses'], default=0) for g in generations]) * 1.1))

        ax.axvline(50, color='red', linestyle='--', linewidth=2, label='PISN gap lower edge')
        ax.axvline(135, color='red', linestyle='--', linewidth=2, label='PISN gap upper edge')
        ax.axvline(100, color='orange', linestyle=':', linewidth=2, label='GW231123 (100 M☉)')
        ax.axvline(140, color='darkred', linestyle=':', linewidth=2, label='GW231123 (140 M☉)')
        ax.set_xlabel('BH Mass (M☉)')
        ax.set_ylabel('Number of BHs')
        ax.set_title('Mass Distribution Evolution')
        ax.legend(fontsize=8)
        ax.set_yscale('log')

        # Panel 2: Maximum mass vs generation
        ax = axes[0, 1]
        max_masses = [max(history[f'generation_{gen}']['masses'], default=0) for gen in generations]
        mean_masses = [np.mean(history[f'generation_{gen}']['masses']) if history[f'generation_{gen}']['masses'] else 0 for gen in generations]

        ax.plot(generations, max_masses, 'o-', linewidth=2, markersize=8, label='Maximum mass')
        ax.plot(generations, mean_masses, 's-', linewidth=2, markersize=6, label='Mean mass')
        ax.axhline(50, color='red', linestyle='--', alpha=0.5, label='PISN lower')
        ax.axhline(135, color='red', linestyle='--', alpha=0.5, label='PISN upper')
        ax.axhline(100, color='orange', linestyle=':', linewidth=2, label='Target: 100 M☉')
        ax.axhline(140, color='darkred', linestyle=':', linewidth=2, label='Target: 140 M☉')
        ax.set_xlabel('Generation')
        ax.set_ylabel('BH Mass (M☉)')
        ax.set_title('Mass Growth Across Generations')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Panel 3: Spin evolution
        ax = axes[1, 0]
        for gen in generations:
            spins = history[f'generation_{gen}']['spins']
            masses = history[f'generation_{gen}']['masses']
            if spins and masses:
                ax.scatter(masses, spins, alpha=0.6, s=30, label=f'Gen {gen}')

        ax.axvspan(50, 135, alpha=0.2, color='red', label='PISN gap')
        ax.axhline(0.3, color='gray', linestyle='--', alpha=0.5, label='Typical stellar BH')
        ax.set_xlabel('BH Mass (M☉)')
        ax.set_ylabel('Spin χ')
        ax.set_title('Mass-Spin Distribution')
        ax.legend(fontsize=8)
        ax.set_xlim(0, None)
        ax.set_ylim(0, 1)
        ax.grid(True, alpha=0.3)

        # Panel 4: Population statistics
        ax = axes[1, 1]
        ax.axis('off')

        stats_text = f"HIERARCHICAL MERGER SIMULATION\n"
        stats_text += f"Environment: {self.environment}\n"
        stats_text += "="*50 + "\n\n"

        for gen in generations:
            data = history[f'generation_{gen}']
            stats_text += f"Generation {gen}:\n"
            stats_text += f"  Population: {data['count']}\n"
            if data['masses']:
                stats_text += f"  Mass range: {min(data['masses']):.1f} - {max(data['masses']):.1f} M☉\n"
                stats_text += f"  Mean spin: {np.mean(data['spins']):.3f}\n"
            if gen > 0:
                stats_text += f"  Mergers: {data.get('mergers', 0)}\n"
                stats_text += f"  Retention: {data.get('retention_rate', 0)*100:.1f}%\n"
            stats_text += "\n"

        # Check if targets reached
        final_masses = history[f'generation_{generations[-1]}']['masses']
        if final_masses:
            max_final = max(final_masses)
            stats_text += f"Final maximum mass: {max_final:.1f} M☉\n\n"

            if max_final >= 100:
                stats_text += "✓ Can produce 100 M☉ BH\n"
            else:
                stats_text += f"✗ Cannot reach 100 M☉ (got {max_final:.1f})\n"

            if max_final >= 140:
                stats_text += "✓ Can produce 140 M☉ BH\n"
            else:
                stats_text += f"✗ Cannot reach 140 M☉ (got {max_final:.1f})\n"

        ax.text(0.05, 0.95, stats_text, transform=ax.transAxes,
               fontsize=9, verticalalignment='top', family='monospace',
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved hierarchical merger plot to {save_path}")

        return fig


if __name__ == "__main__":
    print("="*70)
    print("HIERARCHICAL MERGER SIMULATION: Can we build GW231123?")
    print("="*70)
    print()

    environments = ['globular_cluster', 'nuclear_cluster', 'agn_disk']
    results = {}

    for env in environments:
        print(f"\n{'='*70}")
        print(f"Environment: {env.upper().replace('_', ' ')}")
        print('='*70)

        model = HierarchicalMergerModel(environment=env)

        # Single detailed run
        print(f"\nSingle simulation (N=1000 initial BHs, 5 generations):")
        population = model.initial_bh_population(N=1000)
        history = model.evolve_cluster(population, num_generations=5)

        # Save plot for this environment
        fig = model.plot_mass_growth(history, f'/home/dev/mnt/hierarchical_{env}.png')
        plt.close()

        # Monte Carlo trials
        print(f"\nMonte Carlo trials (50 runs each):")
        result_100 = model.can_reach_mass(100, num_trials=50, max_generations=10)
        result_140 = model.can_reach_mass(140, num_trials=50, max_generations=10)

        print(f"  100 M☉ target: {result_100['success_rate']*100:.1f}% success rate")
        if result_100['typical_spin']:
            print(f"    Typical spin: {result_100['typical_spin']:.3f} ± {result_100['spin_std']:.3f}")
            print(f"    Typical generation: {result_100['typical_generation']:.1f}")

        print(f"  140 M☉ target: {result_140['success_rate']*100:.1f}% success rate")
        if result_140['typical_spin']:
            print(f"    Typical spin: {result_140['typical_spin']:.3f} ± {result_140['spin_std']:.3f}")
            print(f"    Typical generation: {result_140['typical_generation']:.1f}")

        results[env] = {
            '100_solar_masses': result_100,
            '140_solar_masses': result_140
        }

    # Save all results
    with open('/home/dev/mnt/hierarchical_merger_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print()

    for env in environments:
        print(f"{env.upper().replace('_', ' ')}:")
        print(f"  100 M☉: {results[env]['100_solar_masses']['success_rate']*100:.1f}% achievable")
        print(f"  140 M☉: {results[env]['140_solar_masses']['success_rate']*100:.1f}% achievable")
        print()

    print("✓ Simulation complete!")
    print(f"  Results saved to: hierarchical_merger_results.json")
    print(f"  Plots saved to: hierarchical_{{environment}}.png")
