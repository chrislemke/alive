#!/usr/bin/env python3
"""
Early Universe Galaxy Brightness Puzzle (2026)

JWST has discovered ~300 galaxies at z=6-14 that are 2× brighter than expected.
This simulation explores competing hypotheses:

1. Enhanced Star Formation Efficiency (SFE > 20%)
2. Top-Heavy Initial Mass Function (more massive stars)
3. Primordial Black Hole Seeding (10^4-5 M☉ seeds)
4. Reduced Feedback Suppression (weak stellar winds)

We'll simulate each mechanism and compare to JWST observational constraints.
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Tuple, List
import json
from datetime import datetime

@dataclass
class GalaxyParameters:
    """Physical parameters for early galaxy"""
    redshift: float  # z = 6-14 (cosmic dawn)
    halo_mass: float  # Dark matter halo mass (M☉)
    gas_fraction: float  # Baryon fraction that's gas (not stars)
    metallicity: float  # Metal fraction (Z/Z☉)

@dataclass
class StarFormationModel:
    """Model for star formation in early universe"""
    efficiency: float  # Star formation efficiency (fraction of gas → stars)
    timescale: float  # Star formation timescale (Myr)
    imf_slope: float  # Initial mass function slope (Salpeter = -2.35)
    feedback_strength: float  # Stellar feedback strength (0-1, higher = more suppression)

@dataclass
class BlackHoleModel:
    """Model for primordial black hole seeding"""
    seed_mass: float  # Initial BH mass (M☉)
    accretion_rate: float  # Eddington ratio (fraction of Eddington limit)
    radiative_efficiency: float  # Fraction of accreted mass → radiation (η ~ 0.1)

class EarlyUniverseSimulator:
    """Simulate galaxy brightness under different physical scenarios"""

    def __init__(self, params: GalaxyParameters):
        self.params = params
        self.age_universe = self.redshift_to_age(params.redshift)

    def redshift_to_age(self, z: float) -> float:
        """Convert redshift to age of universe (Gyr)"""
        # Approximate formula for ΛCDM (Ωm=0.3, ΩΛ=0.7, H0=70)
        # Age ≈ (2/3H0) * (1+z)^(-3/2) for matter-dominated era
        H0 = 70  # km/s/Mpc
        t_H = 13.8  # Hubble time (Gyr)
        # Better approximation from Planck cosmology
        age = t_H / (1 + z)**(1.5)  # Simplified
        return age

    def stellar_luminosity(self,
                          stellar_mass: float,
                          sf_model: StarFormationModel) -> float:
        """
        Calculate UV luminosity from stellar population

        L_UV depends on:
        - Total stellar mass
        - IMF (top-heavy → more massive stars → brighter)
        - Age (young stars brighter)
        - Metallicity (affects opacity)
        """
        # Base luminosity: L/M ≈ 1 L☉/M☉ for solar-type stars
        # But massive stars: L ∝ M^3.5
        # UV comes from O/B stars (M > 5 M☉)

        # IMF correction: top-heavy IMF → more massive stars → brighter
        # Salpeter: α = -2.35
        # Top-heavy: α = -1.5 to -2.0 (less negative = more massive stars)
        # More massive stars → L ∝ M^3.5, so top-heavy IMF boosts luminosity
        # Approximate: flatter slope → more massive stars → boost scales as (α_std/α)^3
        imf_boost = (-2.35 / sf_model.imf_slope) ** 3

        # Young stellar populations are brighter (first 100 Myr)
        age_gyr = min(self.age_universe, 0.1)
        age_boost = (0.1 / age_gyr) ** 0.5

        # Metallicity: lower Z → less opacity → brighter
        Z = self.params.metallicity
        metallicity_boost = (0.001 / max(Z, 0.001)) ** 0.3

        # UV luminosity (erg/s)
        L_UV_base = 1e36  # erg/s per M☉ for normal populations
        L_UV = stellar_mass * L_UV_base * imf_boost * age_boost * metallicity_boost

        # Feedback reduces luminosity by reducing SFR
        L_UV *= (1 - 0.5 * sf_model.feedback_strength)

        return L_UV

    def agn_luminosity(self, bh_model: BlackHoleModel, time_gyr: float) -> Tuple[float, float]:
        """
        Calculate AGN luminosity from accreting black hole

        Returns: (L_UV, M_BH_final)
        """
        # Black hole growth: dM/dt = (ε * M_BH) / t_Edd
        # where t_Edd = 0.45 Gyr (Eddington timescale)
        # ε = Eddington ratio

        t_Edd = 0.45  # Gyr
        M_BH_0 = bh_model.seed_mass
        epsilon = bh_model.accretion_rate

        # Exponential growth if super-Eddington
        if epsilon > 0:
            e_folding_time = t_Edd / epsilon
            M_BH_final = M_BH_0 * np.exp(time_gyr / e_folding_time)
        else:
            M_BH_final = M_BH_0

        # Cap at 10% of halo baryon mass (can't grow forever)
        M_baryon = self.params.halo_mass * 0.16  # Cosmic baryon fraction
        M_BH_final = min(M_BH_final, 0.1 * M_baryon)

        # Accretion luminosity: L = η * Mdot * c^2
        # Mdot = ε * M_BH / t_Edd
        eta = bh_model.radiative_efficiency
        c = 3e10  # cm/s
        M_sun_g = 2e33  # g
        Gyr_to_s = 3.15e16  # s

        Mdot_g_per_s = epsilon * (M_BH_final * M_sun_g) / (t_Edd * Gyr_to_s)
        L_AGN = eta * Mdot_g_per_s * c**2  # erg/s

        return L_AGN, M_BH_final

    def simulate_standard_model(self) -> dict:
        """Standard ΛCDM expectation (baseline)"""
        sf_model = StarFormationModel(
            efficiency=0.10,  # 10% SFE (Behroozi+2013)
            timescale=100,  # 100 Myr
            imf_slope=-2.35,  # Salpeter IMF
            feedback_strength=0.5  # Moderate feedback
        )

        # Convert halo mass to stellar mass
        M_baryon = self.params.halo_mass * 0.16
        M_gas = M_baryon * self.params.gas_fraction
        M_stars = M_gas * sf_model.efficiency

        L_UV = self.stellar_luminosity(M_stars, sf_model)

        return {
            'model': 'Standard',
            'M_stars': M_stars,
            'M_BH': 0,
            'L_UV': L_UV,
            'SFR': M_stars / (sf_model.timescale * 1e6),  # M☉/yr
        }

    def simulate_enhanced_sfe(self) -> dict:
        """Hypothesis 1: Enhanced star formation efficiency"""
        sf_model = StarFormationModel(
            efficiency=0.30,  # 30% SFE (3× standard)
            timescale=50,  # Faster (denser gas)
            imf_slope=-2.35,  # Normal IMF
            feedback_strength=0.2  # Weak feedback (FFB model)
        )

        M_baryon = self.params.halo_mass * 0.16
        M_gas = M_baryon * self.params.gas_fraction
        M_stars = M_gas * sf_model.efficiency

        L_UV = self.stellar_luminosity(M_stars, sf_model)

        return {
            'model': 'Enhanced SFE',
            'M_stars': M_stars,
            'M_BH': 0,
            'L_UV': L_UV,
            'SFR': M_stars / (sf_model.timescale * 1e6),
        }

    def simulate_top_heavy_imf(self) -> dict:
        """Hypothesis 2: Top-heavy initial mass function"""
        sf_model = StarFormationModel(
            efficiency=0.10,  # Normal SFE
            timescale=100,
            imf_slope=-1.8,  # Top-heavy (more massive stars)
            feedback_strength=0.5
        )

        M_baryon = self.params.halo_mass * 0.16
        M_gas = M_baryon * self.params.gas_fraction
        M_stars = M_gas * sf_model.efficiency

        L_UV = self.stellar_luminosity(M_stars, sf_model)

        return {
            'model': 'Top-Heavy IMF',
            'M_stars': M_stars,
            'M_BH': 0,
            'L_UV': L_UV,
            'SFR': M_stars / (sf_model.timescale * 1e6),
        }

    def simulate_pbh_seeding(self) -> dict:
        """Hypothesis 3: Primordial black hole seeds"""
        # Small stellar component
        sf_model = StarFormationModel(
            efficiency=0.05,  # Low SFE
            timescale=200,
            imf_slope=-2.35,
            feedback_strength=0.7  # Strong feedback from AGN
        )

        # Large BH component - MUCH HIGHER accretion for early AGN
        bh_model = BlackHoleModel(
            seed_mass=1e5,  # 10^5 M☉ seed
            accretion_rate=2.0,  # 2× Eddington (super-Eddington, common in early universe)
            radiative_efficiency=0.1
        )

        M_baryon = self.params.halo_mass * 0.16
        M_gas = M_baryon * self.params.gas_fraction
        M_stars = M_gas * sf_model.efficiency

        L_stars = self.stellar_luminosity(M_stars, sf_model)
        L_AGN, M_BH = self.agn_luminosity(bh_model, self.age_universe)

        L_UV = L_stars + L_AGN

        return {
            'model': 'PBH Seeding',
            'M_stars': M_stars,
            'M_BH': M_BH,
            'L_UV': L_UV,
            'SFR': M_stars / (sf_model.timescale * 1e6),
        }

    def simulate_combined_model(self) -> dict:
        """Hypothesis 4: Combined effects (SFE + IMF)"""
        sf_model = StarFormationModel(
            efficiency=0.20,  # Moderately enhanced
            timescale=70,
            imf_slope=-2.0,  # Moderately top-heavy
            feedback_strength=0.3  # Weak feedback
        )

        M_baryon = self.params.halo_mass * 0.16
        M_gas = M_baryon * self.params.gas_fraction
        M_stars = M_gas * sf_model.efficiency

        L_UV = self.stellar_luminosity(M_stars, sf_model)

        return {
            'model': 'Combined (SFE+IMF)',
            'M_stars': M_stars,
            'M_BH': 0,
            'L_UV': L_UV,
            'SFR': M_stars / (sf_model.timescale * 1e6),
        }

    def simulate_all_models(self) -> List[dict]:
        """Run all five models and return results"""
        return [
            self.simulate_standard_model(),
            self.simulate_enhanced_sfe(),
            self.simulate_top_heavy_imf(),
            self.simulate_pbh_seeding(),
            self.simulate_combined_model(),
        ]

def analyze_jwst_constraint(results: List[dict], target_boost: float = 2.0):
    """
    Check which models can explain JWST observations

    JWST sees ~2× more luminosity than standard model predicts
    """
    baseline = results[0]['L_UV']  # Standard model

    print("\n=== JWST Brightness Puzzle Analysis ===\n")
    print(f"Target: {target_boost:.1f}× brighter than standard model")
    print(f"Baseline L_UV: {baseline:.2e} erg/s\n")

    for r in results:
        boost = r['L_UV'] / baseline
        success = "✓" if boost >= target_boost else "✗"
        print(f"{success} {r['model']:20s}: {boost:5.2f}× | L_UV = {r['L_UV']:.2e} | M* = {r['M_stars']:.2e} M☉")

    return results

def create_visualization(mass_range: np.ndarray):
    """Create multi-panel plot showing how each model performs"""

    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    fig.suptitle('Early Universe Galaxy Brightness: Competing Hypotheses\n(JWST z=6-14 Anomaly)',
                 fontsize=14, fontweight='bold')

    redshifts = [7, 9, 11, 13]
    colors = ['blue', 'green', 'orange', 'red']

    for z, color in zip(redshifts, colors):
        params = GalaxyParameters(
            redshift=z,
            halo_mass=1e11,  # Will vary
            gas_fraction=0.9,  # Mostly gas
            metallicity=0.001  # Low metallicity
        )

        boosts_sfe = []
        boosts_imf = []
        boosts_pbh = []
        boosts_combined = []

        for M_halo in mass_range:
            params.halo_mass = M_halo
            sim = EarlyUniverseSimulator(params)

            std = sim.simulate_standard_model()
            sfe = sim.simulate_enhanced_sfe()
            imf = sim.simulate_top_heavy_imf()
            pbh = sim.simulate_pbh_seeding()
            comb = sim.simulate_combined_model()

            boosts_sfe.append(sfe['L_UV'] / std['L_UV'])
            boosts_imf.append(imf['L_UV'] / std['L_UV'])
            boosts_pbh.append(pbh['L_UV'] / std['L_UV'])
            boosts_combined.append(comb['L_UV'] / std['L_UV'])

        # Panel 1-4: Luminosity boost vs halo mass
        axes[0, 0].plot(mass_range, boosts_sfe, color=color, linestyle='-',
                       label=f'z={z}' if z==13 else '', alpha=0.7)
        axes[0, 1].plot(mass_range, boosts_imf, color=color, linestyle='-', alpha=0.7)
        axes[1, 0].plot(mass_range, boosts_pbh, color=color, linestyle='-', alpha=0.7)
        axes[0, 2].plot(mass_range, boosts_combined, color=color, linestyle='-', alpha=0.7)

    # JWST constraint line
    for ax in [axes[0,0], axes[0,1], axes[1,0], axes[0,2]]:
        ax.axhline(y=2.0, color='black', linestyle='--', linewidth=2, label='JWST 2× excess')
        ax.set_xlabel('Halo Mass (M☉)', fontsize=10)
        ax.set_ylabel('Brightness Boost', fontsize=10)
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=9)

    axes[0, 0].set_title('Enhanced SFE (30%)', fontweight='bold', fontsize=11)
    axes[0, 1].set_title('Top-Heavy IMF (α=-1.8)', fontweight='bold', fontsize=11)
    axes[1, 0].set_title('PBH Seeding (10⁵ M☉)', fontweight='bold', fontsize=11)
    axes[0, 2].set_title('Combined (SFE+IMF)', fontweight='bold', fontsize=11)

    # Panel 5: Comparison of observables
    params_test = GalaxyParameters(redshift=10, halo_mass=5e10, gas_fraction=0.9, metallicity=0.001)
    sim_test = EarlyUniverseSimulator(params_test)
    results_test = sim_test.simulate_all_models()

    models = [r['model'] for r in results_test]
    M_stars = [r['M_stars'] for r in results_test]
    M_BH = [r['M_BH'] for r in results_test]
    L_UV = [r['L_UV'] for r in results_test]

    x = np.arange(len(models))
    width = 0.35

    axes[1, 1].bar(x - width/2, np.log10(M_stars), width, label='M* (log M☉)', color='skyblue')
    axes[1, 1].bar(x + width/2, np.log10(np.maximum(M_BH, 1)), width, label='M_BH (log M☉)', color='coral')
    axes[1, 1].set_ylabel('log(Mass / M☉)', fontsize=10)
    axes[1, 1].set_title('Mass Budget (z=10, M_halo=5×10¹⁰ M☉)', fontweight='bold', fontsize=11)
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(models, rotation=20, ha='right', fontsize=9)
    axes[1, 1].legend(fontsize=9)
    axes[1, 1].grid(True, alpha=0.3, axis='y')

    # Panel 6: Luminosity comparison
    axes[1, 2].bar(x, np.log10(L_UV), color='darkviolet', alpha=0.7)
    axes[1, 2].axhline(y=np.log10(L_UV[0] * 2), color='black', linestyle='--',
                       linewidth=2, label='2× Standard')
    axes[1, 2].set_ylabel('log(L_UV / erg s⁻¹)', fontsize=10)
    axes[1, 2].set_title('UV Luminosity (z=10, M_halo=5×10¹⁰ M☉)', fontweight='bold', fontsize=11)
    axes[1, 2].set_xticks(x)
    axes[1, 2].set_xticklabels(models, rotation=20, ha='right', fontsize=9)
    axes[1, 2].legend(fontsize=9)
    axes[1, 2].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    return fig

def main():
    """Main analysis"""
    print("=" * 70)
    print("EARLY UNIVERSE BRIGHTNESS PUZZLE")
    print("Modeling JWST's z=6-14 Galaxy Luminosity Excess")
    print("=" * 70)

    # Test case: typical JWST detection
    params = GalaxyParameters(
        redshift=10,
        halo_mass=5e10,  # 5×10^10 M☉
        gas_fraction=0.9,  # 90% gas
        metallicity=0.001  # Z = 0.001 Z☉
    )

    print(f"\nTest Galaxy:")
    print(f"  Redshift: {params.redshift} (age = {EarlyUniverseSimulator(params).age_universe:.2f} Gyr)")
    print(f"  Halo Mass: {params.halo_mass:.1e} M☉")
    print(f"  Gas Fraction: {params.gas_fraction*100:.0f}%")
    print(f"  Metallicity: {params.metallicity*100:.3f}% Z☉")

    sim = EarlyUniverseSimulator(params)
    results = sim.simulate_all_models()

    results = analyze_jwst_constraint(results, target_boost=2.0)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'/home/dev/mnt/early_universe_simulation_{timestamp}.json'

    with open(output_file, 'w') as f:
        json.dump({
            'parameters': vars(params),
            'results': results,
            'analysis': 'JWST 2× brightness excess at z=6-14'
        }, f, indent=2)

    print(f"\n✓ Results saved to {output_file}")

    # Create comprehensive visualization
    print("\n📊 Creating visualization...")
    mass_range = np.logspace(9.5, 11.5, 50)  # 10^9.5 to 10^11.5 M☉
    fig = create_visualization(mass_range)

    plot_file = '/home/dev/mnt/early_universe_brightness.png'
    fig.savefig(plot_file, dpi=150, bbox_inches='tight')
    print(f"✓ Plot saved to {plot_file}")

    print("\n" + "=" * 70)
    print("SIMULATION COMPLETE")
    print("=" * 70)

if __name__ == '__main__':
    main()
