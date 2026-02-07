#!/usr/bin/env python3
"""
GW231123 Formation Channel Comparison

Compares all proposed formation channels for the mass-gap black holes
in GW231123 (100 M☉ + 140 M☉).

Channels:
1. Direct stellar collapse (Pop III stars)
2. Hierarchical mergers (globular/nuclear clusters, AGN disks)
3. Primordial black holes
4. Stellar mergers before collapse

Creates comprehensive comparison based on:
- Mass feasibility
- Spin predictions
- Merger rate predictions
- Observational discriminants
"""

import numpy as np
import matplotlib.pyplot as plt
import json


class FormationChannelComparison:
    """Compare all formation channels for GW231123"""

    def __init__(self):
        # Load results from previous analyses
        with open('/home/dev/mnt/pair_instability_results.json', 'r') as f:
            self.pisn_results = json.load(f)

        with open('/home/dev/mnt/hierarchical_merger_results.json', 'r') as f:
            self.merger_results = json.load(f)

        # Define channels
        self.channels = {
            'Pop III Collapse': {
                'can_produce_100': True,  # From PISN analysis (with optimistic rates)
                'can_produce_140': True,
                'spin_100': 0.5,  # Moderate (rotating Pop III star)
                'spin_100_std': 0.3,
                'spin_140': 0.5,
                'spin_140_std': 0.3,
                'metallicity': 0.0,
                'formation_time': 'z > 10 (early universe)',
                'merger_rate': 'Very low (Pop III rare)',
                'eccentricity': 0.0,
                'evidence_for': ['Can produce masses', 'High spin possible'],
                'evidence_against': ['Pop III stars very rare', 'Low metallicity required',
                                   'Why both components at z~2?']
            },
            'AGN Disk Mergers': {
                'can_produce_100': self.merger_results['agn_disk']['100_solar_masses']['success_rate'] > 0.5,
                'can_produce_140': self.merger_results['agn_disk']['140_solar_masses']['success_rate'] > 0.5,
                'spin_100': self.merger_results['agn_disk']['100_solar_masses']['typical_spin'],
                'spin_100_std': self.merger_results['agn_disk']['100_solar_masses']['spin_std'],
                'spin_140': self.merger_results['agn_disk']['140_solar_masses']['typical_spin'],
                'spin_140_std': self.merger_results['agn_disk']['140_solar_masses']['spin_std'],
                'metallicity': 'Any',
                'formation_time': 'z ~ 0-3 (AGN active era)',
                'merger_rate': 'Moderate (10-20% of LIGO events)',
                'eccentricity': 0.0,  # Circularized in gas disk
                'evidence_for': ['✓ Produces both masses easily',
                               '✓ High spin (χ~0.99) matches observation',
                               '✓ Efficient retention (95%)',
                               '✓ Fast timescales (generations in 10-100 Myr)'],
                'evidence_against': ['? Need AGN disk environment',
                                    '? Should see signature in host galaxy']
            },
            'Nuclear Cluster': {
                'can_produce_100': False,
                'can_produce_140': False,
                'spin_100': None,
                'spin_100_std': None,
                'spin_140': None,
                'spin_140_std': None,
                'metallicity': 'Any',
                'formation_time': 'z ~ 0-2',
                'merger_rate': 'Moderate',
                'eccentricity': 0.0,
                'evidence_for': ['Dense environment', 'Some retention'],
                'evidence_against': ['✗ Cannot reach 100 M☉',
                                   '✗ Population exhausted too quickly',
                                   '70% retention insufficient']
            },
            'Globular Cluster': {
                'can_produce_100': False,
                'can_produce_140': False,
                'spin_100': None,
                'spin_100_std': None,
                'spin_140': None,
                'spin_140_std': None,
                'metallicity': 'Low (globulars are old)',
                'formation_time': 'z ~ 2-5',
                'merger_rate': 'Low-moderate',
                'eccentricity': 0.01,  # Slight residual
                'evidence_for': ['Well-studied environment'],
                'evidence_against': ['✗ Cannot reach 100 M☉',
                                   '✗ Low retention (30%)',
                                   '✗ Population exhausted by gen 2']
            },
            'Primordial BHs': {
                'can_produce_100': True,
                'can_produce_140': True,
                'spin_100': 0.0,  # PBHs have negligible spin
                'spin_100_std': 0.1,
                'spin_140': 0.0,
                'spin_140_std': 0.1,
                'metallicity': 'N/A',
                'formation_time': 'z > 1000 (Big Bang)',
                'merger_rate': 'Would dominate all events if abundant',
                'eccentricity': 0.0,
                'evidence_for': ['Can have any mass'],
                'evidence_against': ['✗ Low spin (χ~0) contradicts GW231123',
                                   '✗ Would dominate LIGO if abundant enough',
                                   '✗ No other evidence for PBH population']
            },
            'Stellar Merger → BH': {
                'can_produce_100': True,
                'can_produce_140': True,
                'spin_100': 0.6,
                'spin_100_std': 0.2,
                'spin_140': 0.6,
                'spin_140_std': 0.2,
                'metallicity': 'Low preferred',
                'formation_time': 'z ~ 0-3',
                'merger_rate': 'Very low (requires triple systems)',
                'eccentricity': 0.0,
                'evidence_for': ['Can produce gap masses',
                               'High spin from rotation',
                               'Avoids PISN'],
                'evidence_against': ['? Very rare (need triple/quadruple systems)',
                                   '? Both components via this route unlikely',
                                   'No EM counterpart observed']
            }
        }

    def discriminant_matrix(self) -> dict:
        """
        Create matrix of observables that discriminate between channels.

        Observables:
        - Mass (100 M☉, 140 M☉)
        - Spin (χ ~ 0.99)
        - Eccentricity (e < 0.01 from LIGO)
        - Merger rate (frequency in LIGO O4)
        - Host environment (if detectable)
        """
        observables = {
            'mass_100': {
                'observed': 100.0,
                'Pop III Collapse': 'Marginal (needs Z=0, optimistic rates)',
                'AGN Disk Mergers': '✓ Easy (100% success)',
                'Nuclear Cluster': '✗ Cannot produce',
                'Globular Cluster': '✗ Cannot produce',
                'Primordial BHs': '✓ Any mass',
                'Stellar Merger → BH': '✓ Possible'
            },
            'mass_140': {
                'observed': 140.0,
                'Pop III Collapse': 'Marginal (M_init ~ 220 M☉, Z=0)',
                'AGN Disk Mergers': '✓ Easy (100% success)',
                'Nuclear Cluster': '✗ Cannot produce',
                'Globular Cluster': '✗ Cannot produce',
                'Primordial BHs': '✓ Any mass',
                'Stellar Merger → BH': '✓ Possible (rare)'
            },
            'spin_high': {
                'observed': 'χ ~ 0.99 (near maximal)',
                'Pop III Collapse': '? Moderate (χ ~ 0.3-0.7)',
                'AGN Disk Mergers': '✓✓ χ ~ 0.99 ± 0.03 (PERFECT MATCH)',
                'Nuclear Cluster': 'N/A',
                'Globular Cluster': 'N/A',
                'Primordial BHs': '✗ χ ~ 0 (near zero)',
                'Stellar Merger → BH': '? Moderate (χ ~ 0.4-0.8)'
            },
            'eccentricity': {
                'observed': 'e < 0.01 (circular)',
                'Pop III Collapse': '✓ e = 0 (binary evolution)',
                'AGN Disk Mergers': '✓ e = 0 (gas circularizes)',
                'Nuclear Cluster': '✓ e ~ 0 (GW circularizes)',
                'Globular Cluster': '? e ~ 0.01 (slight residual)',
                'Primordial BHs': '✓ e = 0',
                'Stellar Merger → BH': '✓ e = 0'
            },
            'merger_rate': {
                'observed': '1 event in O4 (391 total)',
                'Pop III Collapse': '✗ Very rare (Pop III rare)',
                'AGN Disk Mergers': '✓ Moderate (10-20% of events plausible)',
                'Nuclear Cluster': '? Moderate (but can\'t produce masses)',
                'Globular Cluster': '? Moderate (but can\'t produce masses)',
                'Primordial BHs': '✗ Would dominate if abundant',
                'Stellar Merger → BH': '✗ Very rare'
            }
        }

        return observables

    def score_channels(self) -> dict:
        """
        Score each channel on ability to explain GW231123.

        Scoring:
        +2: Strong evidence for
        +1: Consistent with
        0: Neutral/unknown
        -1: Tension with observation
        -2: Ruled out
        """
        scores = {}

        for channel_name, channel_data in self.channels.items():
            score = 0
            reasons = []

            # Mass production
            if channel_data['can_produce_100'] and channel_data['can_produce_140']:
                score += 2
                reasons.append('+2: Can produce both masses')
            elif channel_data['can_produce_100'] or channel_data['can_produce_140']:
                score += 0
                reasons.append('+0: Can produce one mass (insufficient)')
            else:
                score -= 2
                reasons.append('-2: Cannot produce masses')

            # Spin (critical discriminant for GW231123)
            if channel_data['spin_100'] is not None and channel_data['spin_140'] is not None:
                avg_spin = (channel_data['spin_100'] + channel_data['spin_140']) / 2

                if avg_spin > 0.85:  # High spin (matches observation)
                    score += 2
                    reasons.append('+2: High spin matches χ~0.99')
                elif avg_spin > 0.5:
                    score += 1
                    reasons.append('+1: Moderate spin (possible)')
                elif avg_spin < 0.2:
                    score -= 2
                    reasons.append('-2: Low spin contradicts observation')
                else:
                    score += 0
                    reasons.append('+0: Spin uncertain')

            # Merger rate
            if 'Very low' in channel_data['merger_rate']:
                score -= 1
                reasons.append('-1: Very rare (unlikely)')
            elif 'Moderate' in channel_data['merger_rate']:
                score += 1
                reasons.append('+1: Merger rate plausible')

            scores[channel_name] = {
                'total_score': score,
                'reasons': reasons,
                'verdict': self._verdict(score)
            }

        return scores

    def _verdict(self, score: int) -> str:
        """Convert score to verdict"""
        if score >= 4:
            return 'STRONGLY FAVORED'
        elif score >= 2:
            return 'PLAUSIBLE'
        elif score >= 0:
            return 'MARGINALLY VIABLE'
        elif score >= -2:
            return 'UNLIKELY'
        else:
            return 'RULED OUT'

    def plot_comparison(self, save_path: str = None):
        """Comprehensive comparison visualization"""
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.35)

        # Panel 1: Channel viability matrix
        ax1 = fig.add_subplot(gs[0, :2])
        channels_list = list(self.channels.keys())
        criteria = ['100 M☉', '140 M☉', 'High Spin', 'Rate']

        matrix = []
        for ch in channels_list:
            row = [
                2 if self.channels[ch]['can_produce_100'] else -2,
                2 if self.channels[ch]['can_produce_140'] else -2,
                2 if (self.channels[ch]['spin_100'] or 0) > 0.85 else
                -2 if (self.channels[ch]['spin_100'] or 0) < 0.2 else 0,
                1 if 'Moderate' in self.channels[ch]['merger_rate'] else
                -1 if 'Very low' in self.channels[ch]['merger_rate'] else 0
            ]
            matrix.append(row)

        im = ax1.imshow(matrix, cmap='RdYlGn', aspect='auto', vmin=-2, vmax=2)
        ax1.set_xticks(range(len(criteria)))
        ax1.set_yticks(range(len(channels_list)))
        ax1.set_xticklabels(criteria)
        ax1.set_yticklabels(channels_list)
        ax1.set_title('Formation Channel Viability Matrix\n(Green=Good, Red=Bad)', fontsize=12, weight='bold')

        # Add values
        for i in range(len(channels_list)):
            for j in range(len(criteria)):
                val = matrix[i][j]
                symbol = '✓✓' if val == 2 else '✓' if val == 1 else '?' if val == 0 else '✗' if val == -1 else '✗✗'
                color = 'white' if abs(val) > 0.5 else 'black'
                ax1.text(j, i, symbol, ha='center', va='center', color=color, fontsize=14, weight='bold')

        plt.colorbar(im, ax=ax1, label='Score')

        # Panel 2: Spin predictions
        ax2 = fig.add_subplot(gs[0, 2])
        viable_channels = [ch for ch in channels_list if self.channels[ch]['can_produce_100']]
        spins_100 = [self.channels[ch]['spin_100'] for ch in viable_channels if self.channels[ch]['spin_100'] is not None]
        spins_140 = [self.channels[ch]['spin_140'] for ch in viable_channels if self.channels[ch]['spin_140'] is not None]
        labels_viable = [ch for ch in viable_channels if self.channels[ch]['spin_100'] is not None]

        x_pos = np.arange(len(labels_viable))
        ax2.barh(x_pos - 0.2, spins_100, 0.4, label='100 M☉ component', color='orange', alpha=0.8)
        ax2.barh(x_pos + 0.2, spins_140, 0.4, label='140 M☉ component', color='red', alpha=0.8)
        ax2.axvline(0.99, color='black', linestyle='--', linewidth=2, label='GW231123 (χ~0.99)')
        ax2.set_yticks(x_pos)
        ax2.set_yticklabels(labels_viable, fontsize=9)
        ax2.set_xlabel('Predicted Spin χ')
        ax2.set_title('Spin Predictions', fontsize=11, weight='bold')
        ax2.legend(fontsize=8)
        ax2.set_xlim(0, 1.05)
        ax2.grid(axis='x', alpha=0.3)

        # Panel 3: Score ranking
        ax3 = fig.add_subplot(gs[1, :])
        scores = self.score_channels()
        channels_sorted = sorted(scores.keys(), key=lambda ch: scores[ch]['total_score'], reverse=True)
        score_values = [scores[ch]['total_score'] for ch in channels_sorted]
        verdicts = [scores[ch]['verdict'] for ch in channels_sorted]

        colors = ['darkgreen' if s >= 4 else 'green' if s >= 2 else 'yellow' if s >= 0 else 'orange' if s >= -2 else 'red'
                 for s in score_values]

        bars = ax3.barh(channels_sorted, score_values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        ax3.axvline(0, color='black', linewidth=1)
        ax3.set_xlabel('Overall Score', fontsize=12, weight='bold')
        ax3.set_title('Formation Channel Rankings for GW231123', fontsize=13, weight='bold')
        ax3.grid(axis='x', alpha=0.3)

        # Add verdict labels
        for i, (ch, bar) in enumerate(zip(channels_sorted, bars)):
            verdict = verdicts[i]
            score = score_values[i]
            x_pos_label = score + 0.3 if score >= 0 else score - 0.3
            ha = 'left' if score >= 0 else 'right'
            ax3.text(x_pos_label, i, verdict, ha=ha, va='center', fontsize=9, weight='bold')

        # Panel 4: Evidence summary (text)
        ax4 = fig.add_subplot(gs[2, :])
        ax4.axis('off')

        winner = channels_sorted[0]
        winner_score = scores[winner]['total_score']

        summary = f"VERDICT: GW231123 FORMATION CHANNEL\n"
        summary += "="*70 + "\n\n"
        summary += f"MOST LIKELY: {winner} (score: {winner_score}/6)\n\n"

        summary += "Evidence FOR:\n"
        for reason in self.channels[winner]['evidence_for']:
            summary += f"  {reason}\n"

        summary += "\nEvidence AGAINST:\n"
        for reason in self.channels[winner]['evidence_against']:
            summary += f"  {reason}\n"

        summary += "\n" + "-"*70 + "\n"
        summary += "RUNNER-UP:\n"
        if len(channels_sorted) > 1:
            runner_up = channels_sorted[1]
            runner_score = scores[runner_up]['total_score']
            summary += f"{runner_up} (score: {runner_score}/6)\n"
            summary += f"Reasons: {'; '.join(scores[runner_up]['reasons'])}\n"

        summary += "\n" + "-"*70 + "\n"
        summary += "RULED OUT:\n"
        ruled_out = [ch for ch in channels_sorted if scores[ch]['total_score'] <= -2]
        for ch in ruled_out:
            summary += f"✗ {ch}: {scores[ch]['total_score']}/6\n"
            summary += f"  Why: {'; '.join(scores[ch]['reasons'])}\n"

        ax4.text(0.05, 0.95, summary, transform=ax4.transAxes,
                fontsize=10, verticalalignment='top', family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved comparison plot to {save_path}")

        return fig


if __name__ == "__main__":
    print("="*70)
    print("GW231123 FORMATION CHANNEL COMPARISON")
    print("="*70)
    print()

    comparison = FormationChannelComparison()

    # Get discriminant matrix
    print("DISCRIMINANT MATRIX:")
    print("-"*70)
    observables = comparison.discriminant_matrix()

    for obs_name, obs_data in observables.items():
        print(f"\n{obs_name.upper().replace('_', ' ')}:")
        print(f"  Observed: {obs_data['observed']}")
        for channel in comparison.channels.keys():
            print(f"    {channel:25s}: {obs_data[channel]}")

    # Score channels
    print("\n" + "="*70)
    print("CHANNEL SCORING:")
    print("="*70)

    scores = comparison.score_channels()
    sorted_channels = sorted(scores.keys(), key=lambda ch: scores[ch]['total_score'], reverse=True)

    for i, channel in enumerate(sorted_channels, 1):
        score_data = scores[channel]
        print(f"\n{i}. {channel}: {score_data['total_score']}/6 ({score_data['verdict']})")
        for reason in score_data['reasons']:
            print(f"     {reason}")

    # Create visualization
    print("\n" + "="*70)
    print("Generating comprehensive comparison plot...")
    print("="*70)

    fig = comparison.plot_comparison('/home/dev/mnt/formation_channel_comparison.png')

    # Save detailed results
    results = {
        'scores': scores,
        'ranked_channels': sorted_channels,
        'winner': sorted_channels[0],
        'winner_score': scores[sorted_channels[0]]['total_score'],
        'discriminant_matrix': observables
    }

    with open('/home/dev/mnt/formation_channel_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\n✓ Analysis complete!")
    print(f"  Winner: {sorted_channels[0]}")
    print(f"  Score: {scores[sorted_channels[0]]['total_score']}/6")
    print(f"  Verdict: {scores[sorted_channels[0]]['verdict']}")
    print(f"\n  Results: formation_channel_results.json")
    print(f"  Plot: formation_channel_comparison.png")
