#!/usr/bin/env python3
"""
Pair-Instability Supernova Physics Simulator

Models the pair-instability mass gap for black hole formation.
Determines which stellar masses produce black holes vs. complete disruption.

Physics:
- Pair production: γ → e⁺ + e⁻ when photon energy exceeds 2m_e c²
- Pressure loss: Radiation pressure ∝ photon density drops
- Dynamical instability: When pressure drops too much, core collapses
- Explosive oxygen burning: Runaway nuclear fusion
- Pulsational mass loss: Partially unstable stars pulsate and lose mass
- Complete disruption: No remnant if explosion energy exceeds binding energy

References:
- Woosley 2017, ApJ 836, 244 (PISN mass ranges)
- Farmer et al. 2019, ApJ 887, 53 (lower edge uncertainties)
- Woosley et al. 2021, ApJ 912, L31 (upper edge uncertainties)
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Tuple, List
import json


@dataclass
class StellarParameters:
    """Parameters for a massive star at core helium burning"""
    initial_mass: float  # Solar masses
    metallicity: float   # Z/Z_sun (0 = Pop III, 1 = solar, 0.001 = low-Z)
    rotation: float      # Ω/Ω_critical (0 = non-rotating, 1 = breakup)
    helium_core_mass: float  # Derived from initial mass


class PairInstabilityModel:
    """
    Model pair-instability supernovae and mass gap boundaries.

    Mass gap formation:
    1. Below M_lo: Core collapses quietly to black hole
    2. M_lo to M_hi: Pair instability disrupts star (no remnant)
    3. Above M_hi: Pair instability occurs but core still massive enough → BH

    Boundaries depend on metallicity (mass loss), rotation (mixing), and
    nuclear reaction rate uncertainties.
    """

    def __init__(self):
        # Base parameters (solar metallicity, non-rotating, nominal rates)
        self.M_lo_base = 55.0  # Solar masses (lower edge, Farmer+ 2019)
        self.M_hi_base = 135.0  # Solar masses (upper edge, Woosley 2017)

        # Uncertainties from nuclear rates (Woosley+ 2021)
        self.M_lo_max = 64.0  # Maximum lower edge (pessimistic rates)
        self.M_hi_max = 161.0  # Maximum upper edge (optimistic rates)

        # Pulsational mass loss extends gap downward
        self.M_pulsation = 45.0  # Pulsational PISN starts here

        # Relation between initial mass and helium core mass
        # M_He ≈ 0.3 * M_init for massive stars (rough approximation)
        self.he_core_fraction = 0.3

    def helium_core_mass(self, initial_mass: float, metallicity: float) -> float:
        """
        Estimate helium core mass from initial stellar mass.

        Higher metallicity → more mass loss → smaller He core.
        """
        # Metallicity correction: more metals → more stellar winds → less He core
        # At Z=1, factor ≈ 0.3; at Z=0, factor ≈ 0.5 (Pop III retains more mass)
        base_fraction = 0.3 + 0.2 * np.exp(-2 * metallicity)

        return initial_mass * base_fraction

    def mass_gap_boundaries(
        self,
        metallicity: float = 1.0,
        rotation: float = 0.0,
        rate_uncertainty: str = 'nominal'
    ) -> Tuple[float, float, float]:
        """
        Calculate mass gap boundaries for given stellar parameters.

        Returns (M_pulsation, M_lo, M_hi) in solar masses.

        - M_pulsation: Onset of pulsational mass loss
        - M_lo: Lower boundary (BH → no remnant transition)
        - M_hi: Upper boundary (no remnant → BH transition)

        Parameters:
            metallicity: Z/Z_sun (lower Z → higher mass gap)
            rotation: Ω/Ω_crit (rotation can shift boundaries)
            rate_uncertainty: 'nominal', 'pessimistic', 'optimistic'
        """
        # Base values
        if rate_uncertainty == 'pessimistic':
            M_lo = self.M_lo_max
            M_hi = self.M_hi_max
        elif rate_uncertainty == 'optimistic':
            M_lo = self.M_lo_base - 5
            M_hi = self.M_hi_base - 10
        else:  # nominal
            M_lo = self.M_lo_base
            M_hi = self.M_hi_base

        # Metallicity correction
        # Lower metallicity → less mass loss → need higher initial mass to reach gap
        # At Z=0 (Pop III), boundaries shift up by ~10-20%
        metal_factor = 1.0 + 0.15 * np.exp(-2 * metallicity)

        # Rotation correction
        # Rapid rotation can stabilize core, shifting boundaries higher
        rotation_factor = 1.0 + 0.1 * rotation

        M_lo_final = M_lo * metal_factor * rotation_factor
        M_hi_final = M_hi * metal_factor * rotation_factor
        M_puls_final = self.M_pulsation * metal_factor

        return M_puls_final, M_lo_final, M_hi_final

    def classify_remnant(
        self,
        initial_mass: float,
        metallicity: float = 1.0,
        rotation: float = 0.0,
        rate_uncertainty: str = 'nominal'
    ) -> Tuple[str, float]:
        """
        Determine what remnant a star produces and its mass.

        Returns (remnant_type, remnant_mass) where:
            remnant_type: 'neutron_star', 'black_hole', 'disrupted', 'heavy_black_hole'
            remnant_mass: Final compact object mass (0 if disrupted)
        """
        M_puls, M_lo, M_hi = self.mass_gap_boundaries(
            metallicity, rotation, rate_uncertainty
        )

        # Below 20 M_sun: typically neutron stars (not our focus)
        if initial_mass < 20:
            return 'neutron_star', 1.4

        # 20-45 M_sun: Normal black hole formation
        if initial_mass < M_puls:
            # Rough remnant mass: ~0.5 * initial mass (rest lost in supernova)
            remnant_mass = 0.5 * initial_mass
            return 'black_hole', remnant_mass

        # Pulsational mass loss region (45-55 M_sun nominal)
        if initial_mass < M_lo:
            # Pulsations eject mass, leaves smaller remnant
            remnant_mass = 0.3 * initial_mass
            if remnant_mass < 2.5:
                return 'neutron_star', remnant_mass
            return 'black_hole', remnant_mass

        # Pair-instability mass gap (55-135 M_sun nominal)
        if initial_mass < M_hi:
            return 'disrupted', 0.0  # Complete disruption, no remnant

        # Above mass gap: Very massive stars
        # Direct collapse or weak PISN, but core massive enough for BH
        if initial_mass < 250:
            remnant_mass = 0.6 * initial_mass  # Less mass loss at high masses
            return 'heavy_black_hole', remnant_mass

        # Extreme masses (> 250 M_sun): Direct collapse
        remnant_mass = 0.8 * initial_mass
        return 'heavy_black_hole', remnant_mass

    def can_produce_mass(
        self,
        target_bh_mass: float,
        metallicity_range: Tuple[float, float] = (0.0, 1.0),
        rotation_range: Tuple[float, float] = (0.0, 0.8),
        num_samples: int = 100
    ) -> dict:
        """
        Determine if standard stellar evolution can produce a BH of target mass.

        Scans parameter space (metallicity, rotation, nuclear uncertainties) to see
        if any combination yields the desired BH mass.

        Returns dict with:
            - can_produce: bool
            - scenarios: list of viable parameter combinations
            - closest_miss: if can't produce, what's the closest achievable mass
        """
        scenarios = []
        all_masses = []

        Z_range = np.linspace(metallicity_range[0], metallicity_range[1], num_samples)
        omega_range = np.linspace(rotation_range[0], rotation_range[1], num_samples)
        uncertainties = ['optimistic', 'nominal', 'pessimistic']

        for Z in Z_range:
            for omega in omega_range:
                for uncert in uncertainties:
                    # Try range of initial masses
                    for M_init in np.linspace(10, 300, 500):
                        remnant_type, remnant_mass = self.classify_remnant(
                            M_init, Z, omega, uncert
                        )

                        all_masses.append(remnant_mass)

                        # Check if this produces target mass (within 5%)
                        if remnant_type in ['black_hole', 'heavy_black_hole']:
                            if abs(remnant_mass - target_bh_mass) / target_bh_mass < 0.05:
                                scenarios.append({
                                    'initial_mass': M_init,
                                    'metallicity': Z,
                                    'rotation': omega,
                                    'uncertainty': uncert,
                                    'remnant_mass': remnant_mass,
                                    'remnant_type': remnant_type
                                })

        # Find closest achievable mass if target can't be produced
        all_masses = np.array([m for m in all_masses if m > 0])
        if len(all_masses) > 0:
            closest_idx = np.argmin(np.abs(all_masses - target_bh_mass))
            closest_mass = all_masses[closest_idx]
        else:
            closest_mass = 0.0

        return {
            'can_produce': len(scenarios) > 0,
            'num_scenarios': len(scenarios),
            'scenarios': scenarios[:10],  # Return up to 10 examples
            'closest_miss': closest_mass if len(scenarios) == 0 else None
        }

    def plot_mass_gap_landscape(self, save_path: str = None):
        """
        Visualize the mass gap across parameter space.

        4 panels:
        1. Mass gap boundaries vs metallicity
        2. Final BH mass vs initial stellar mass (different Z)
        3. Mass gap region in initial mass - remnant mass space
        4. Forbidden zone for GW231123 components
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))

        # Panel 1: Boundaries vs metallicity
        ax = axes[0, 0]
        Z_values = np.linspace(0, 1.5, 100)

        for uncert, color, label in [
            ('optimistic', 'green', 'Optimistic rates'),
            ('nominal', 'blue', 'Nominal rates'),
            ('pessimistic', 'red', 'Pessimistic rates')
        ]:
            M_puls_arr, M_lo_arr, M_hi_arr = [], [], []
            for Z in Z_values:
                M_puls, M_lo, M_hi = self.mass_gap_boundaries(Z, 0.0, uncert)
                M_puls_arr.append(M_puls)
                M_lo_arr.append(M_lo)
                M_hi_arr.append(M_hi)

            ax.fill_between(Z_values, M_lo_arr, M_hi_arr, alpha=0.2, color=color)
            ax.plot(Z_values, M_lo_arr, '--', color=color, label=f'{label} (lower)')
            ax.plot(Z_values, M_hi_arr, '-', color=color, label=f'{label} (upper)')

        ax.axhline(100, color='orange', linestyle=':', linewidth=2, label='GW231123 (100 M☉)')
        ax.axhline(140, color='red', linestyle=':', linewidth=2, label='GW231123 (140 M☉)')
        ax.set_xlabel('Metallicity (Z/Z☉)')
        ax.set_ylabel('Initial Stellar Mass (M☉)')
        ax.set_title('Pair-Instability Mass Gap Boundaries')
        ax.legend(fontsize=8, loc='upper left')
        ax.grid(True, alpha=0.3)

        # Panel 2: Initial mass → remnant mass
        ax = axes[0, 1]
        M_init_range = np.linspace(10, 250, 500)

        for Z, color, label in [
            (0.0, 'purple', 'Z=0 (Pop III)'),
            (0.01, 'blue', 'Z=0.01 Z☉'),
            (1.0, 'green', 'Z=Z☉ (solar)')
        ]:
            remnant_masses = []
            for M_init in M_init_range:
                _, M_rem = self.classify_remnant(M_init, Z, 0.0, 'nominal')
                remnant_masses.append(M_rem)

            ax.plot(M_init_range, remnant_masses, color=color, label=label, linewidth=2)

        # Mark GW231123 components
        ax.scatter([100, 140], [100, 140], s=200, c='red', marker='*',
                  edgecolor='black', linewidth=2, zorder=10, label='GW231123 needs')
        ax.axhline(100, color='orange', linestyle=':', alpha=0.5)
        ax.axhline(140, color='red', linestyle=':', alpha=0.5)

        ax.set_xlabel('Initial Stellar Mass (M☉)')
        ax.set_ylabel('Remnant BH Mass (M☉)')
        ax.set_title('Stellar Evolution: Initial → Final Mass')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 200)

        # Panel 3: Heatmap of viable parameter space
        ax = axes[1, 0]
        Z_grid = np.linspace(0, 1.5, 100)
        M_grid = np.linspace(10, 250, 100)
        Z_mesh, M_mesh = np.meshgrid(Z_grid, M_grid)

        # Compute remnant type
        remnant_grid = np.zeros_like(Z_mesh)
        for i in range(len(M_grid)):
            for j in range(len(Z_grid)):
                remnant_type, remnant_mass = self.classify_remnant(
                    M_mesh[i, j], Z_mesh[i, j], 0.0, 'nominal'
                )
                if remnant_type == 'disrupted':
                    remnant_grid[i, j] = 0  # No remnant
                elif remnant_type in ['black_hole', 'heavy_black_hole']:
                    remnant_grid[i, j] = remnant_mass
                else:
                    remnant_grid[i, j] = -1  # Neutron star

        # Mask disrupted regions
        remnant_masked = np.ma.masked_where(remnant_grid == 0, remnant_grid)

        im = ax.contourf(Z_mesh, M_mesh, remnant_masked, levels=20, cmap='viridis')
        ax.contour(Z_mesh, M_mesh, remnant_grid, levels=[0], colors='red',
                  linewidths=2, linestyles='--')

        ax.axhline(100, color='orange', linestyle=':', linewidth=2, alpha=0.8)
        ax.axhline(140, color='red', linestyle=':', linewidth=2, alpha=0.8)

        ax.set_xlabel('Metallicity (Z/Z☉)')
        ax.set_ylabel('Initial Stellar Mass (M☉)')
        ax.set_title('Remnant BH Mass (Red = PISN Gap)')
        plt.colorbar(im, ax=ax, label='BH Mass (M☉)')

        # Panel 4: Verdict on GW231123
        ax = axes[1, 1]
        ax.axis('off')

        # Check if either component can be produced
        result_100 = self.can_produce_mass(100, num_samples=20)
        result_140 = self.can_produce_mass(140, num_samples=20)

        verdict_text = "GW231123 FORMATION ANALYSIS\n"
        verdict_text += "="*50 + "\n\n"

        verdict_text += f"100 M☉ Component:\n"
        verdict_text += f"  Can produce via standard evolution? {result_100['can_produce']}\n"
        verdict_text += f"  Number of viable scenarios: {result_100['num_scenarios']}\n"
        if not result_100['can_produce']:
            verdict_text += f"  Closest achievable: {result_100['closest_miss']:.1f} M☉\n"
        verdict_text += "\n"

        verdict_text += f"140 M☉ Component:\n"
        verdict_text += f"  Can produce via standard evolution? {result_140['can_produce']}\n"
        verdict_text += f"  Number of viable scenarios: {result_140['num_scenarios']}\n"
        if not result_140['can_produce']:
            verdict_text += f"  Closest achievable: {result_140['closest_miss']:.1f} M☉\n"
        verdict_text += "\n"

        verdict_text += "CONCLUSION:\n"
        if not result_100['can_produce'] and not result_140['can_produce']:
            verdict_text += "❌ BOTH components are FORBIDDEN by\n"
            verdict_text += "   standard stellar evolution.\n\n"
            verdict_text += "Alternative formation required:\n"
            verdict_text += "  • Hierarchical mergers\n"
            verdict_text += "  • Primordial black holes (ruled out by spin)\n"
            verdict_text += "  • Stellar mergers before collapse\n"
            verdict_text += "  • Direct collapse (exotic scenarios)\n"
        elif result_100['can_produce'] and not result_140['can_produce']:
            verdict_text += "⚠️  100 M☉ is POSSIBLE (marginal)\n"
            verdict_text += "❌ 140 M☉ is FORBIDDEN\n"
            verdict_text += "\nAlternative formation needed for 140 M☉\n"
        else:
            verdict_text += "✓ Both masses achievable in some scenarios\n"
            verdict_text += "  (likely requires low metallicity + rotation)\n"

        ax.text(0.05, 0.95, verdict_text, transform=ax.transAxes,
               fontsize=11, verticalalignment='top', family='monospace',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved mass gap landscape to {save_path}")

        return fig


if __name__ == "__main__":
    model = PairInstabilityModel()

    print("="*60)
    print("PAIR-INSTABILITY MASS GAP ANALYSIS")
    print("="*60)
    print()

    # Compute mass gap for different scenarios
    scenarios = [
        ("Solar metallicity (Z=Z☉)", 1.0, 0.0, 'nominal'),
        ("Low metallicity (Z=0.01 Z☉)", 0.01, 0.0, 'nominal'),
        ("Pop III (Z=0)", 0.0, 0.0, 'nominal'),
        ("Solar Z, rotating (Ω=0.5)", 1.0, 0.5, 'nominal'),
        ("Pessimistic rates", 1.0, 0.0, 'pessimistic'),
    ]

    print("Mass Gap Boundaries:")
    print("-" * 60)
    for name, Z, omega, uncert in scenarios:
        M_puls, M_lo, M_hi = model.mass_gap_boundaries(Z, omega, uncert)
        print(f"{name:35s}: {M_lo:5.1f} - {M_hi:5.1f} M☉")
    print()

    # Check GW231123 components
    print("="*60)
    print("GW231123 COMPONENT ANALYSIS")
    print("="*60)
    print()

    for target_mass in [100, 140]:
        print(f"\n{target_mass} M☉ Component:")
        print("-" * 60)
        result = model.can_produce_mass(target_mass, num_samples=30)

        print(f"Can produce via standard evolution? {result['can_produce']}")
        print(f"Number of viable scenarios: {result['num_scenarios']}")

        if result['can_produce'] and len(result['scenarios']) > 0:
            print("\nExample scenarios:")
            for i, scenario in enumerate(result['scenarios'][:3], 1):
                print(f"  {i}. M_init={scenario['initial_mass']:.1f} M☉, "
                      f"Z={scenario['metallicity']:.3f}, "
                      f"Ω={scenario['rotation']:.2f}, "
                      f"rates={scenario['uncertainty']}")
                print(f"     → {scenario['remnant_mass']:.1f} M☉ {scenario['remnant_type']}")
        else:
            print(f"\n❌ CANNOT produce {target_mass} M☉ BH via standard evolution")
            print(f"   Closest achievable: {result['closest_miss']:.1f} M☉")

    print("\n" + "="*60)
    print("Generating visualization...")
    print("="*60)

    fig = model.plot_mass_gap_landscape('/home/dev/mnt/mass_gap_landscape.png')

    # Save results
    results = {
        'mass_gap_boundaries': {
            name: {
                'M_pulsation': float(M_puls),
                'M_lo': float(M_lo),
                'M_hi': float(M_hi)
            }
            for name, Z, omega, uncert in scenarios
            for M_puls, M_lo, M_hi in [model.mass_gap_boundaries(Z, omega, uncert)]
        },
        'gw231123_100': model.can_produce_mass(100, num_samples=30),
        'gw231123_140': model.can_produce_mass(140, num_samples=30),
    }

    with open('/home/dev/mnt/pair_instability_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print("\n✓ Analysis complete!")
    print("  Results: pair_instability_results.json")
    print("  Plot: mass_gap_landscape.png")
