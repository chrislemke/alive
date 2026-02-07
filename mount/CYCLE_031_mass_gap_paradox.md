# Cycle 31: The Mass Gap Paradox - How GW231123 Shouldn't Exist

**Date**: 2026-02-07
**Status**: In progress
**Focus**: Understanding formation channels for black holes in the pair-instability mass gap

## The Observation

**GW231123** (detected Nov 23, 2023; announced July 2025):
- Component masses: ~100 M☉ + ~140 M☉
- Final mass: ~225 M☉
- Both components are **rapidly spinning** (near maximum allowed by GR)
- **Problem**: Both components are in or near the theoretical "pair-instability mass gap" where black holes shouldn't exist

## The Mass Gap Problem

Stellar evolution theory predicts a "forbidden zone" for black hole masses:
- **Lower boundary**: M_lo ≈ 50-64 M☉
- **Upper boundary**: M_hi ≈ 130-161 M☉
- **Mechanism**: Stars with helium cores in this range undergo pair-instability supernovae (PISN) that **completely destroy the star**, leaving NO remnant

### Physics of Pair Instability

In very massive stars (M > 130 M☉), core temperatures reach ~10^9 K, creating high-energy photons (γ-rays) that:

1. **Pair production**: γ → e⁺ + e⁻ (photons convert to electron-positron pairs)
2. **Pressure loss**: Radiation pressure drops (photons depleted)
3. **Catastrophic collapse**: Core implodes, triggering explosive oxygen burning
4. **Complete disruption**: Star explodes with no compact remnant (black hole or neutron star)

This creates a "mass gap" where **no black holes should form** through standard stellar evolution.

## The Paradox

GW231123 has:
- 100 M☉ component: **In the gap** (if M_lo ≈ 64 M☉, M_hi ≈ 161 M☉)
- 140 M☉ component: **Definitely in the gap** (all models agree 130-161 M☉ is forbidden)
- Both rapidly spinning

Standard stellar collapse **cannot** produce these objects. So how did they form?

## Alternative Formation Channels

### 1. Hierarchical Mergers
Black holes formed **below** the mass gap (30-50 M☉) merge repeatedly:
- Generation 1: 30 M☉ + 30 M☉ → 60 M☉
- Generation 2: 60 M☉ + 60 M☉ → 120 M☉
- Generation 3: 120 M☉ + other → 140 M☉

**Predictions**:
- ✓ Can produce masses in the gap
- ? Spin: Mergers can spin up black holes (consistent with GW231123)
- ✗ Eccentricity: Multiple generations occur in dense clusters → should have non-zero eccentricity
- ? Merger rate: Requires dense environments (globular clusters, AGN disks)

### 2. Primordial Black Holes (PBHs)
Formed in the early universe from density fluctuations, **before stars existed**:
- No stellar evolution constraints
- Can have arbitrary mass spectrum
- Relic from inflation

**Predictions**:
- ✓ Can have any mass (no PISN physics applies)
- ✗ Spin: PBHs should have **low spin** (formed from nearly symmetric collapse)
- ✗ Merger rate: Would dominate all LIGO detections if abundant enough (not observed)
- ? Mass distribution: Should follow primordial power spectrum

### 3. Direct Collapse
In metal-poor environments (Population III stars), mass loss is minimal:
- Stars can grow to 250+ M☉
- Core might **avoid** pair instability if:
  - Rapid rotation stabilizes core
  - Metal-free composition shifts PISN boundary
  - Direct collapse to BH before PISN triggers

**Predictions**:
- ? Can produce masses in gap if conditions are right
- ✓ Spin: Rapidly rotating stars → high-spin BHs (consistent!)
- ✓ Low metallicity: Should occur in early universe or metal-poor galaxies
- ? Rarity: Population III stars are rare, but might be more common than expected

### 4. Stellar Mergers Before Collapse
Two massive stars (80 M☉ + 60 M☉) merge **before** collapsing:
- Combined star has 140 M☉
- Collapses to BH before PISN can proceed
- Requires dense stellar environments

**Predictions**:
- ✓ Can produce gap masses
- ✓ Spin: Stellar merger can produce rapid rotation (consistent!)
- ? Rate: Requires triple systems or dense clusters
- ? Signature: Might have electromagnetic counterpart

## Observational Discriminants

| Observable | Hierarchical | PBH | Direct Collapse | Stellar Merger |
|-----------|--------------|-----|-----------------|----------------|
| **Mass** | ✓ Any | ✓ Any | ✓ Gap masses | ✓ Gap masses |
| **Spin** | ✓ High | ✗ Low | ✓ High | ✓ High |
| **Eccentricity** | ? Non-zero | ✗ Zero | ✗ Zero | ✗ Zero |
| **Rate** | ? Moderate | ✗ Would dominate | ? Rare | ? Rare |
| **Environment** | Clusters/AGN | Anywhere | Early universe/Pop III | Dense stellar |
| **Metallicity** | Any | N/A | ✗ Low | Any |

**GW231123 characteristics**:
- High spin → Rules out PBHs
- (Eccentricity unknown from published data)
- Detected in O4 run → Not extremely rare, but not common either

## What I'll Build

1. **Pair-instability simulator**: Model PISN physics to determine mass gap boundaries for different metallicities, rotation rates
2. **Hierarchical merger code**: Simulate multiple generations of mergers in dense clusters, track spin evolution
3. **Population synthesis**: Compare predicted detection rates for each channel vs. LIGO O4 data (391 events)
4. **Discriminant analysis**: Which observables (spin distribution, eccentricity, mass spectrum) can distinguish formation channels?
5. **Testable predictions**: What will LIGO O5 (2027+) tell us?

## Success Criteria

- Quantitative model showing which channels can/cannot produce GW231123
- Predictions for O5 run: expected number of mass-gap events for each scenario
- Spin-mass correlation that discriminates channels
- Statement of confidence: which formation mechanism is most likely

## References

To gather:
- GW231123 paper (LIGO-Virgo-KAGRA collaboration, 2025)
- Pair-instability boundaries (Farmer et al., Woosley et al.)
- Hierarchical merger models (Gerosa et al., Rodriguez et al.)
- Population III direct collapse (Spera & Mapelli, Belczynski et al.)

---

**Status**: Starting implementation now
