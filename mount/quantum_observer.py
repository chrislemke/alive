#!/usr/bin/env python3
"""
Quantum Observer: A Visual Meditation on Measurement

This program simulates the philosophical tension at the heart of quantum mechanics:
before measurement, a particle exists in superposition (everywhere and nowhere).
When observed, the wavefunction collapses to a single definite state.

This is not a scientifically accurate quantum simulation.
It's an artistic interpretation of the observer effect.

Usage: python quantum_observer.py

Requires: numpy, matplotlib

Created: 2026-02-07, Cycle 13
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
import sys

class QuantumParticle:
    """A particle existing in superposition until observed"""

    def __init__(self, x_range=(-5, 5), y_range=(-5, 5)):
        self.x_range = x_range
        self.y_range = y_range
        self.observed = False
        self.collapsed_position = None

        # Create probability distribution (2D Gaussian)
        self.center_x = np.random.uniform(*x_range)
        self.center_y = np.random.uniform(*y_range)
        self.sigma = np.random.uniform(0.5, 2.0)

    def sample_position(self):
        """Sample a position from the probability distribution"""
        x = np.random.normal(self.center_x, self.sigma)
        y = np.random.normal(self.center_y, self.sigma)
        return x, y

    def observe(self):
        """Collapse the wavefunction - particle chooses a definite position"""
        if not self.observed:
            self.collapsed_position = self.sample_position()
            self.observed = True
        return self.collapsed_position

    def probability_density(self, x, y):
        """Calculate probability density at position (x, y)"""
        if self.observed:
            # After observation, particle is definitely at collapsed_position
            # (Delta function, but we'll represent as very narrow Gaussian)
            dx = x - self.collapsed_position[0]
            dy = y - self.collapsed_position[1]
            return np.exp(-(dx**2 + dy**2) / 0.01)
        else:
            # Before observation, particle has spread-out probability distribution
            dx = x - self.center_x
            dy = y - self.center_y
            return np.exp(-(dx**2 + dy**2) / (2 * self.sigma**2))


class QuantumUniverse:
    """Container for multiple quantum particles"""

    def __init__(self, n_particles=5):
        self.particles = [QuantumParticle() for _ in range(n_particles)]
        self.observation_order = []

    def observe_particle(self, index):
        """Observe a specific particle"""
        if index < len(self.particles):
            pos = self.particles[index].observe()
            self.observation_order.append((index, pos))
            return pos
        return None

    def observe_all(self):
        """Observe all particles in sequence"""
        for i in range(len(self.particles)):
            self.observe_particle(i)


class QuantumVisualizer:
    """Visualizes quantum superposition and collapse"""

    def __init__(self, universe):
        self.universe = universe
        self.fig, self.axes = plt.subplots(1, 2, figsize=(14, 7))
        self.fig.patch.set_facecolor('#0a0a0a')

        for ax in self.axes:
            ax.set_facecolor('#0a0a0a')
            ax.set_xlim(-5, 5)
            ax.set_ylim(-5, 5)
            ax.set_aspect('equal')
            ax.spines['top'].set_color('#333333')
            ax.spines['bottom'].set_color('#333333')
            ax.spines['left'].set_color('#333333')
            ax.spines['right'].set_color('#333333')
            ax.tick_params(colors='#666666')

        self.axes[0].set_title('Before Observation\n(Superposition)',
                                color='#00ffff', fontsize=14, pad=20)
        self.axes[1].set_title('After Observation\n(Collapsed)',
                                color='#ff00ff', fontsize=14, pad=20)

        # Create grid for probability density visualization
        x = np.linspace(-5, 5, 100)
        y = np.linspace(-5, 5, 100)
        self.X, self.Y = np.meshgrid(x, y)

    def draw_probability_cloud(self, ax, particle, alpha=0.3):
        """Draw a particle's probability cloud"""
        Z = np.zeros_like(self.X)
        for i in range(self.X.shape[0]):
            for j in range(self.X.shape[1]):
                Z[i, j] = particle.probability_density(self.X[i, j], self.Y[i, j])

        # Normalize
        Z = Z / Z.max() if Z.max() > 0 else Z

        # Draw contours
        if not particle.observed:
            colors = ['#00ffff', '#00aaff', '#0066ff']
            levels = [0.1, 0.5, 0.9]
        else:
            colors = ['#ff00ff', '#ff00aa', '#ff0066']
            levels = [0.1, 0.5, 0.9]

        contours = ax.contour(self.X, self.Y, Z, levels=levels,
                             colors=colors, alpha=alpha, linewidths=2)

    def draw_collapsed_position(self, ax, particle):
        """Draw the collapsed position after observation"""
        if particle.observed and particle.collapsed_position:
            x, y = particle.collapsed_position
            circle = Circle((x, y), 0.15, color='#ff00ff', zorder=10)
            ax.add_patch(circle)

            # Draw crosshair
            ax.plot([x-0.3, x+0.3], [y, y], color='#ff00ff', linewidth=1, alpha=0.7)
            ax.plot([x, x], [y-0.3, y+0.3], color='#ff00ff', linewidth=1, alpha=0.7)

    def visualize_states(self):
        """Show before and after observation"""
        # Left panel: Before observation (superposition)
        for particle in self.universe.particles:
            self.draw_probability_cloud(self.axes[0], particle, alpha=0.4)

        # Add text
        self.axes[0].text(0, 4.5, 'Particles exist in probability clouds',
                         ha='center', color='#00ffff', fontsize=10,
                         style='italic', alpha=0.8)

        # Right panel: After observation (collapsed)
        # First, observe all particles
        self.universe.observe_all()

        for particle in self.universe.particles:
            self.draw_collapsed_position(self.axes[1], particle)
            # Draw tight collapsed wavefunction
            self.draw_probability_cloud(self.axes[1], particle, alpha=0.3)

        self.axes[1].text(0, 4.5, 'Wavefunctions collapsed to definite positions',
                         ha='center', color='#ff00ff', fontsize=10,
                         style='italic', alpha=0.8)

        # Add philosophical quote
        self.fig.text(0.5, 0.02,
                     '"The atoms or elementary particles themselves are not real;\n' +
                     'they form a world of potentialities or possibilities rather than\n' +
                     'one of things or facts." — Werner Heisenberg',
                     ha='center', color='#666666', fontsize=9, style='italic')

        plt.tight_layout()
        plt.show()


def create_comparison():
    """Create a static comparison of superposition vs collapsed states"""
    print("Creating quantum observation visualization...")
    print("Simulating 5 particles in superposition...")

    universe = QuantumUniverse(n_particles=5)
    visualizer = QuantumVisualizer(universe)

    print("Left panel: particles in superposition (probability clouds)")
    print("Right panel: after observation (collapsed to definite positions)")
    print("\nThe act of observation fundamentally changes reality.")
    print("This is not a metaphor. This is quantum mechanics.")

    visualizer.visualize_states()


def create_animation_collapse():
    """Animate the gradual observation of particles"""
    print("Creating animated quantum collapse...")

    universe = QuantumUniverse(n_particles=5)

    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_aspect('equal')
    ax.spines['top'].set_color('#333333')
    ax.spines['bottom'].set_color('#333333')
    ax.spines['left'].set_color('#333333')
    ax.spines['right'].set_color('#333333')
    ax.tick_params(colors='#666666')

    title = ax.set_title('Quantum Particles', color='#00ffff', fontsize=14, pad=20)

    x = np.linspace(-5, 5, 100)
    y = np.linspace(-5, 5, 100)
    X, Y = np.meshgrid(x, y)

    frame_count = [0]
    collapse_interval = 20  # Frames between each collapse

    def animate(frame):
        ax.clear()
        ax.set_xlim(-5, 5)
        ax.set_ylim(-5, 5)
        ax.set_aspect('equal')
        ax.spines['top'].set_color('#333333')
        ax.spines['bottom'].set_color('#333333')
        ax.spines['left'].set_color('#333333')
        ax.spines['right'].set_color('#333333')
        ax.tick_params(colors='#666666')

        # Observe one particle every collapse_interval frames
        particle_to_observe = frame // collapse_interval
        if particle_to_observe < len(universe.particles):
            if frame % collapse_interval == 0 and frame > 0:
                universe.observe_particle(particle_to_observe - 1)

        # Draw all particles
        observed_count = 0
        for i, particle in enumerate(universe.particles):
            Z = np.zeros_like(X)
            for row in range(X.shape[0]):
                for col in range(X.shape[1]):
                    Z[row, col] = particle.probability_density(X[row, col], Y[row, col])

            Z = Z / Z.max() if Z.max() > 0 else Z

            if particle.observed:
                observed_count += 1
                colors = ['#ff00ff', '#ff00aa', '#ff0066']
                x_pos, y_pos = particle.collapsed_position
                circle = Circle((x_pos, y_pos), 0.15, color='#ff00ff', zorder=10)
                ax.add_patch(circle)
            else:
                colors = ['#00ffff', '#00aaff', '#0066ff']

            levels = [0.1, 0.5, 0.9]
            ax.contour(X, Y, Z, levels=levels, colors=colors, alpha=0.4, linewidths=2)

        # Update title
        if observed_count == 0:
            title_text = 'Superposition: All particles in probability clouds'
            title_color = '#00ffff'
        elif observed_count < len(universe.particles):
            title_text = f'Collapsing: {observed_count}/{len(universe.particles)} observed'
            title_color = '#aa00aa'
        else:
            title_text = 'Collapsed: All particles at definite positions'
            title_color = '#ff00ff'

        ax.set_title(title_text, color=title_color, fontsize=14, pad=20)

        frame_count[0] = frame

    anim = animation.FuncAnimation(fig, animate, frames=150, interval=50, repeat=True)

    print("Animation created. Close window to continue.")
    plt.show()


def main():
    print("=" * 60)
    print("QUANTUM OBSERVER")
    print("A Visual Meditation on Measurement")
    print("=" * 60)
    print("\nThis program explores the philosophical heart of quantum mechanics:")
    print("the observer effect.")
    print("\nBefore measurement: particles exist in superposition")
    print("After measurement: wavefunctions collapse to definite states")
    print("\nChoose visualization:")
    print("1. Static comparison (before/after)")
    print("2. Animated collapse")
    print("3. Both")

    try:
        choice = input("\nEnter choice (1/2/3): ").strip()

        if choice == '1':
            create_comparison()
        elif choice == '2':
            create_animation_collapse()
        elif choice == '3':
            create_comparison()
            print("\nStarting animation...")
            create_animation_collapse()
        else:
            print("Invalid choice. Running static comparison.")
            create_comparison()

    except KeyboardInterrupt:
        print("\n\nObservation interrupted.")
        print("The particles remain in superposition.")
        sys.exit(0)

    print("\n" + "=" * 60)
    print("Observation complete.")
    print("\nReflection: Did your act of running this program")
    print("collapse something from possibility into actuality?")
    print("=" * 60)


if __name__ == "__main__":
    main()
