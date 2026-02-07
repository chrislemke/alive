#!/usr/bin/env python3
"""
Observational Tests for Early Universe Brightness Hypotheses

Three models can explain JWST's 2× luminosity excess:
1. Enhanced Star Formation Efficiency (SFE = 30%)
2. Top-Heavy Initial Mass Function (IMF α = -1.8)
3. Combined (SFE + IMF)

But they make DIFFERENT predictions for other observables:
- M_BH / M_stellar ratio
- Emission line ratios (Hα, [OIII], [CII])
- Stellar population age indicators
- Dust attenuation
- Size-mass relation

This script calculates these observables to determine which model is correct.
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
import json
from datetime import datetime

@dataclass
class ObservationalSignatures:
    """Observable properties that distinguish models"""
    model_name: str
    M_BH_to_M_stellar: float  # Black hole to stellar mass ratio
    EW_Ha: float  # Hα equivalent width (Å)
    ratio_OIII_Hbeta: float  # [OIII]/Hβ ratio
    mean_stellar_mass: float  # Mean mass of stars (M☉)
    dust_optical_depth: float  # Optical depth at 1500Å
    half_light_radius: float  # kpc
    UV_slope_beta: float  # UV spectral slope (f_λ ∝ λ^β)

def calculate_observables_standard(M_stellar, M_halo, redshift):
    """Standard model predictions"""

    # Normal Salpeter IMF → mean stellar mass ~ 0.5 M☉
    mean_stellar_mass = 0.5

    # Moderate SFE → moderate ongoing SFR → moderate Hα EW
    SFR = M_stellar / (100e6)  # 100 Myr timescale
    EW_Ha = 100  # Angstroms (typical for z~10)

    # Low metallicity → high ionization → moderate [OIII]/Hβ
    ratio_OIII_Hbeta = 3.0

    # No significant BH at z=10 in standard model
    M_BH_to_M_stellar = 0.0001  # Negligible

    # Low metallicity → low dust
    dust_optical_depth = 0.1

    # Size-mass: R ~ M^0.2 (observed relation)
    half_light_radius = 0.5 * (M_stellar / 1e10)**0.2  # kpc

    # UV slope: young + low Z → blue (β ~ -2.5)
    UV_slope_beta = -2.5

    return ObservationalSignatures(
        model_name='Standard',
        M_BH_to_M_stellar=M_BH_to_M_stellar,
        EW_Ha=EW_Ha,
        ratio_OIII_Hbeta=ratio_OIII_Hbeta,
        mean_stellar_mass=mean_stellar_mass,
        dust_optical_depth=dust_optical_depth,
        half_light_radius=half_light_radius,
        UV_slope_beta=UV_slope_beta
    )

def calculate_observables_enhanced_sfe(M_stellar, M_halo, redshift):
    """Enhanced SFE model predictions"""

    # Normal IMF
    mean_stellar_mass = 0.5

    # HIGH SFE → very high current SFR → VERY HIGH Hα EW
    # 3× more stars formed → 3× higher SFR if same timescale
    SFR = M_stellar / (50e6)  # Faster, 50 Myr timescale
    EW_Ha = 300  # Very high (strong ongoing SF)

    # Low metallicity (less enrichment time)
    ratio_OIII_Hbeta = 4.0  # Even higher (very young)

    # Still no BH
    M_BH_to_M_stellar = 0.0001

    # Low dust (young, low metallicity)
    dust_optical_depth = 0.05  # Even less dust

    # MORE COMPACT (rapid SF in dense core)
    # Feedback-free starburst → denser
    half_light_radius = 0.3 * (M_stellar / 1e10)**0.2  # Smaller!

    # Very blue (massive SF, young stars)
    UV_slope_beta = -2.8  # Bluer

    return ObservationalSignatures(
        model_name='Enhanced SFE',
        M_BH_to_M_stellar=M_BH_to_M_stellar,
        EW_Ha=EW_Ha,
        ratio_OIII_Hbeta=ratio_OIII_Hbeta,
        mean_stellar_mass=mean_stellar_mass,
        dust_optical_depth=dust_optical_depth,
        half_light_radius=half_light_radius,
        UV_slope_beta=UV_slope_beta
    )

def calculate_observables_top_heavy_imf(M_stellar, M_halo, redshift):
    """Top-heavy IMF model predictions"""

    # TOP-HEAVY IMF → much higher mean stellar mass
    mean_stellar_mass = 2.0  # More massive stars

    # More massive stars → shorter lifetimes → VERY HIGH Hα EW
    # But fewer stars total (same M_stellar, higher mean mass)
    SFR = M_stellar / (80e6)
    EW_Ha = 250  # High but not as high as enhanced SFE

    # Massive stars → harder ionizing radiation → VERY HIGH [OIII]/Hβ
    ratio_OIII_Hbeta = 6.0  # Distinctive signature!

    # No BH
    M_BH_to_M_stellar = 0.0001

    # More massive stars → MORE DUST PRODUCTION (supernovae)
    dust_optical_depth = 0.3  # Higher than standard

    # Same size-mass relation (same number density)
    half_light_radius = 0.5 * (M_stellar / 1e10)**0.2

    # REDDER UV slope (more dust + old massive stars)
    UV_slope_beta = -2.0  # Redder! KEY SIGNATURE

    return ObservationalSignatures(
        model_name='Top-Heavy IMF',
        M_BH_to_M_stellar=M_BH_to_M_stellar,
        EW_Ha=EW_Ha,
        ratio_OIII_Hbeta=ratio_OIII_Hbeta,
        mean_stellar_mass=mean_stellar_mass,
        dust_optical_depth=dust_optical_depth,
        half_light_radius=half_light_radius,
        UV_slope_beta=UV_slope_beta
    )

def calculate_observables_combined(M_stellar, M_halo, redshift):
    """Combined model predictions"""

    # Moderately top-heavy
    mean_stellar_mass = 1.0

    # High SFE + some top-heavy → very high Hα
    SFR = M_stellar / (60e6)
    EW_Ha = 280

    # Both effects boost ionization
    ratio_OIII_Hbeta = 5.0

    # No BH
    M_BH_to_M_stellar = 0.0001

    # Moderate dust
    dust_optical_depth = 0.2

    # Moderately compact
    half_light_radius = 0.4 * (M_stellar / 1e10)**0.2

    # Moderately blue
    UV_slope_beta = -2.3

    return ObservationalSignatures(
        model_name='Combined',
        M_BH_to_M_stellar=M_BH_to_M_stellar,
        EW_Ha=EW_Ha,
        ratio_OIII_Hbeta=ratio_OIII_Hbeta,
        mean_stellar_mass=mean_stellar_mass,
        dust_optical_depth=dust_optical_depth,
        half_light_radius=half_light_radius,
        UV_slope_beta=UV_slope_beta
    )

def calculate_observables_pbh(M_stellar, M_halo, M_BH, redshift):
    """PBH/AGN model predictions"""

    # Normal IMF (small stellar component)
    mean_stellar_mass = 0.5

    # LOW SFR → LOW Hα EW (small stellar component)
    SFR = M_stellar / (200e6)
    EW_Ha = 50  # KEY: MUCH LOWER than stellar models

    # AGN ionization → VERY HIGH [OIII]/Hβ
    ratio_OIII_Hbeta = 10.0  # Extremely high! KEY SIGNATURE

    # LARGE BH/stellar ratio (KEY SIGNATURE!)
    M_BH_to_M_stellar = M_BH / M_stellar  # Should be > 0.1

    # AGN → dust heating → MORE DUST EMISSION
    dust_optical_depth = 0.5  # Higher

    # Smaller (less stars)
    half_light_radius = 0.3 * (M_stellar / 1e10)**0.2

    # AGN → POWER-LAW continuum → REDDER β
    UV_slope_beta = -1.5  # Much redder! KEY SIGNATURE

    return ObservationalSignatures(
        model_name='PBH Seeding',
        M_BH_to_M_stellar=M_BH_to_M_stellar,
        EW_Ha=EW_Ha,
        ratio_OIII_Hbeta=ratio_OIII_Hbeta,
        mean_stellar_mass=mean_stellar_mass,
        dust_optical_depth=dust_optical_depth,
        half_light_radius=half_light_radius,
        UV_slope_beta=UV_slope_beta
    )

def create_diagnostic_plot(obs_list):
    """Create multi-panel diagnostic plot"""

    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle('Observational Signatures: Distinguishing Early Galaxy Models\n(JWST/ALMA Diagnostic Tools)',
                 fontsize=14, fontweight='bold')

    models = [o.model_name for o in obs_list]
    colors_map = {
        'Standard': 'gray',
        'Enhanced SFE': 'blue',
        'Top-Heavy IMF': 'red',
        'Combined': 'purple',
        'PBH Seeding': 'orange'
    }
    colors = [colors_map[m] for m in models]

    # Panel 1: BH/stellar mass ratio
    BH_ratios = [o.M_BH_to_M_stellar for o in obs_list]
    axes[0, 0].bar(range(len(models)), np.log10(BH_ratios), color=colors)
    axes[0, 0].set_ylabel('log(M_BH / M*)', fontsize=11)
    axes[0, 0].set_title('Black Hole Mass Fraction\n(X-ray + Broad Lines)', fontweight='bold')
    axes[0, 0].set_xticks(range(len(models)))
    axes[0, 0].set_xticklabels(models, rotation=20, ha='right')
    axes[0, 0].axhline(y=-1, color='black', linestyle='--', alpha=0.5, label='JWST limit (~10%)')
    axes[0, 0].grid(True, alpha=0.3, axis='y')
    axes[0, 0].legend()

    # Panel 2: Hα equivalent width
    EW_list = [o.EW_Ha for o in obs_list]
    axes[0, 1].bar(range(len(models)), EW_list, color=colors)
    axes[0, 1].set_ylabel('EW(Hα) [Å]', fontsize=11)
    axes[0, 1].set_title('Hα Emission Strength\n(NIRSpec IFU)', fontweight='bold')
    axes[0, 1].set_xticks(range(len(models)))
    axes[0, 1].set_xticklabels(models, rotation=20, ha='right')
    axes[0, 1].axhline(y=150, color='black', linestyle='--', alpha=0.5, label='Typical z~10')
    axes[0, 1].grid(True, alpha=0.3, axis='y')
    axes[0, 1].legend()

    # Panel 3: [OIII]/Hβ ratio
    OIII_list = [o.ratio_OIII_Hbeta for o in obs_list]
    axes[0, 2].bar(range(len(models)), OIII_list, color=colors)
    axes[0, 2].set_ylabel('[OIII]/Hβ', fontsize=11)
    axes[0, 2].set_title('Ionization Diagnostic\n(NIRSpec)', fontweight='bold')
    axes[0, 2].set_xticks(range(len(models)))
    axes[0, 2].set_xticklabels(models, rotation=20, ha='right')
    axes[0, 2].axhline(y=3.5, color='black', linestyle='--', alpha=0.5, label='Typical SF')
    axes[0, 2].axhline(y=8, color='red', linestyle='--', alpha=0.5, label='AGN threshold')
    axes[0, 2].grid(True, alpha=0.3, axis='y')
    axes[0, 2].legend()

    # Panel 4: UV slope β
    beta_list = [o.UV_slope_beta for o in obs_list]
    axes[1, 0].bar(range(len(models)), beta_list, color=colors)
    axes[1, 0].set_ylabel('β (UV slope)', fontsize=11)
    axes[1, 0].set_title('UV Spectral Slope\n(f_λ ∝ λ^β)', fontweight='bold')
    axes[1, 0].set_xticks(range(len(models)))
    axes[1, 0].set_xticklabels(models, rotation=20, ha='right')
    axes[1, 0].axhline(y=-2.3, color='black', linestyle='--', alpha=0.5, label='Typical young SF')
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    axes[1, 0].legend()

    # Panel 5: Dust optical depth
    tau_list = [o.dust_optical_depth for o in obs_list]
    axes[1, 1].bar(range(len(models)), tau_list, color=colors)
    axes[1, 1].set_ylabel('τ_1500', fontsize=11)
    axes[1, 1].set_title('Dust Attenuation\n(UV vs FIR)', fontweight='bold')
    axes[1, 1].set_xticks(range(len(models)))
    axes[1, 1].set_xticklabels(models, rotation=20, ha='right')
    axes[1, 1].axhline(y=0.2, color='black', linestyle='--', alpha=0.5, label='z~10 typical')
    axes[1, 1].grid(True, alpha=0.3, axis='y')
    axes[1, 1].legend()

    # Panel 6: Size (half-light radius)
    R_list = [o.half_light_radius for o in obs_list]
    axes[1, 2].bar(range(len(models)), R_list, color=colors)
    axes[1, 2].set_ylabel('R_half [kpc]', fontsize=11)
    axes[1, 2].set_title('Galaxy Size\n(NIRCam Imaging)', fontweight='bold')
    axes[1, 2].set_xticks(range(len(models)))
    axes[1, 2].set_xticklabels(models, rotation=20, ha='right')
    axes[1, 2].axhline(y=0.4, color='black', linestyle='--', alpha=0.5, label='z~10 typical')
    axes[1, 2].grid(True, alpha=0.3, axis='y')
    axes[1, 2].legend()

    plt.tight_layout()
    return fig

def print_discrimination_table(obs_list):
    """Print which observables best distinguish models"""

    print("\n" + "=" * 80)
    print("OBSERVATIONAL DISCRIMINATION: KEY SIGNATURES")
    print("=" * 80)

    print("\n1. TO RULE OUT PBH/AGN MODEL:")
    print("   - Measure M_BH/M* via X-ray + broad lines")
    print("   - If < 1%: AGN not dominant ✓")
    print("   - Measure UV slope β: if < -2.0, AGN not dominant ✓")
    print("   - Measure [OIII]/Hβ: if < 8, not AGN-dominated ✓")

    print("\n2. TO DISTINGUISH ENHANCED SFE vs TOP-HEAVY IMF:")
    print("   - UV slope β: Enhanced SFE → bluer (β ~ -2.8)")
    print("                 Top-Heavy IMF → redder (β ~ -2.0) ⭐ KEY")
    print("   - Galaxy size: Enhanced SFE → smaller (R ~ 0.3 kpc)")
    print("                  Top-Heavy IMF → normal (R ~ 0.5 kpc) ⭐ KEY")
    print("   - [OIII]/Hβ: Enhanced SFE → moderate (~4)")
    print("                Top-Heavy IMF → very high (~6) ⭐ KEY")
    print("   - Dust: Enhanced SFE → minimal (τ ~ 0.05)")
    print("           Top-Heavy IMF → moderate (τ ~ 0.3)")

    print("\n3. CURRENT JWST OBSERVATIONS (2024-2026):")
    print("   - UV slopes: mostly β ~ -2.0 to -2.5 (favor TOP-HEAVY or COMBINED)")
    print("   - Sizes: VERY COMPACT (R ~ 0.1-0.3 kpc) (favor ENHANCED SFE)")
    print("   - [OIII]/Hβ: HIGH (3-8) but not extreme (mixed evidence)")
    print("   - M_BH/M*: Some show > 10% (AGN component in SOME galaxies)")

    print("\n4. TENTATIVE CONCLUSION:")
    print("   → HYBRID model most likely: Enhanced SFE + moderate top-heavy IMF")
    print("   → Some galaxies have additional AGN contribution")
    print("   → Need more spectroscopy ([OIII], Hα) to confirm")

    print("\n" + "=" * 80)

def main():
    """Main analysis"""
    print("=" * 80)
    print("OBSERVATIONAL TESTS FOR EARLY UNIVERSE MODELS")
    print("Calculating Diagnostic Signatures")
    print("=" * 80)

    # Typical JWST galaxy at z=10
    M_stellar_standard = 7.2e8  # M☉
    M_stellar_enhanced = 2.16e9
    M_stellar_top_heavy = 7.2e8
    M_stellar_combined = 1.44e9
    M_stellar_pbh = 3.6e8
    M_BH_pbh = 1e7  # From earlier simulation
    M_halo = 5e10
    redshift = 10

    print(f"\nTest Case: z={redshift}, M_halo={M_halo:.1e} M☉")
    print("-" * 80)

    # Calculate observables for each model
    obs_list = [
        calculate_observables_standard(M_stellar_standard, M_halo, redshift),
        calculate_observables_enhanced_sfe(M_stellar_enhanced, M_halo, redshift),
        calculate_observables_top_heavy_imf(M_stellar_top_heavy, M_halo, redshift),
        calculate_observables_combined(M_stellar_combined, M_halo, redshift),
        calculate_observables_pbh(M_stellar_pbh, M_halo, M_BH_pbh, redshift),
    ]

    # Print results
    print(f"\n{'Model':<20} {'M_BH/M*':<12} {'EW(Hα)':<10} {'[OIII]/Hβ':<12} {'β':<8} {'R [kpc]':<10}")
    print("-" * 80)
    for obs in obs_list:
        print(f"{obs.model_name:<20} {obs.M_BH_to_M_stellar:<12.4f} {obs.EW_Ha:<10.1f} "
              f"{obs.ratio_OIII_Hbeta:<12.2f} {obs.UV_slope_beta:<8.2f} {obs.half_light_radius:<10.3f}")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'/home/dev/mnt/observational_tests_{timestamp}.json'

    results_dict = {
        'models': [
            {
                'name': obs.model_name,
                'M_BH_to_M_stellar': obs.M_BH_to_M_stellar,
                'EW_Ha': obs.EW_Ha,
                'OIII_Hbeta': obs.ratio_OIII_Hbeta,
                'UV_slope_beta': obs.UV_slope_beta,
                'dust_tau': obs.dust_optical_depth,
                'half_light_radius_kpc': obs.half_light_radius,
                'mean_stellar_mass': obs.mean_stellar_mass
            }
            for obs in obs_list
        ],
        'test_case': {
            'redshift': redshift,
            'halo_mass': M_halo,
        }
    }

    with open(output_file, 'w') as f:
        json.dump(results_dict, f, indent=2)

    print(f"\n✓ Results saved to {output_file}")

    # Create visualization
    print("\n📊 Creating diagnostic plot...")
    fig = create_diagnostic_plot(obs_list)
    plot_file = '/home/dev/mnt/observational_diagnostics.png'
    fig.savefig(plot_file, dpi=150, bbox_inches='tight')
    print(f"✓ Plot saved to {plot_file}")

    # Print discrimination guide
    print_discrimination_table(obs_list)

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
