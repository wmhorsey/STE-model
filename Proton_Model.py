import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class ProtonModel:
    """
    STE Model of the Proton: 2 Void Cores (Up Quarks) inducing a 3rd Spike Core (Down Quark)
    Mapped to a Tetrahedral Lattice.
    - Triangular base: 3 quark positions (2 voids + 1 spike).
    - Overall intake: Gravitational pull at the centroid.
    - Spikes form a band projecting outward: EM wash for electron formation.
    """

    def __init__(self, radius=1.0):
        self.radius = radius
        self.quark_positions = self._setup_tetrahedral_lattice()
        self.intake_center = np.mean(self.quark_positions, axis=0)  # Centroid for gravitational pull
        self.em_wash_band = self._generate_em_wash()

    def _setup_tetrahedral_lattice(self):
        """
        Tetrahedral lattice: Base triangle for 3 quarks.
        Down quark: 1/2 physical size, equal strength.
        Up quarks: Complementary spins pulling inward, forced apart by radiant spike.
        """
        # Equilateral triangle base, but adjust for forces
        angle = 2 * np.pi / 3
        positions = []
        for i in range(3):
            x = self.radius * np.cos(i * angle)
            y = self.radius * np.sin(i * angle)
            z = 0  # Base plane
            if i == 2:  # Down quark (spike) inside radius, smaller
                x *= 0.5
                y *= 0.5
            positions.append([x, y, z])
        # Force up quarks apart due to spike: slightly expand their positions
        # Up quarks at 0 and 1, down at 2
        for i in [0, 1]:
            pos = np.array(positions[i])
            direction = pos / np.linalg.norm(pos)  # Outward
            positions[i] = (pos + 0.2 * direction).tolist()  # Push apart
        return np.array(positions)

    def _generate_em_wash(self):
        """
        Spikes form a band down one side projecting outward.
        Model as a helical band around the tetrahedron's edge.
        """
        # Simplified: Band along one edge, projecting outward
        edge_start = self.quark_positions[0]
        edge_end = self.quark_positions[1]
        num_points = 20
        t = np.linspace(0, 1, num_points)
        band = []
        for ti in t:
            pos = (1 - ti) * edge_start + ti * edge_end
            # Project outward along normal
            normal = np.array([0, 0, 1])  # Upward projection
            projection = pos + 0.5 * normal * (1 + np.sin(2 * np.pi * ti * 5))  # Wavy band
            band.append(projection)
        return np.array(band)

    def visualize(self):
        """
        Visualize the proton model.
        """
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        # Plot quarks with sizes
        sizes = [100, 100, 50]  # Down quark 1/2 size
        colors = ['blue', 'blue', 'red']  # 2 voids (blue), 1 spike (red)
        labels = ['Up Quark (Void)', 'Up Quark (Void)', 'Down Quark (Spike)']
        for i, pos in enumerate(self.quark_positions):
            ax.scatter(*pos, color=colors[i], s=sizes[i], label=labels[i])
            ax.text(*pos, f'Q{i+1}', fontsize=12)

        # Add spin arrows: Up quarks pulling inward (complementary spins)
        for i in [0, 1]:
            pos = self.quark_positions[i]
            inward_dir = -pos / np.linalg.norm(pos)  # Inward direction
            ax.quiver(*pos, *inward_dir * 0.3, color='cyan', label='Inward Spin' if i == 0 else "")

        # Down quark (spike) radiating energy outward
        spike_pos = self.quark_positions[2]
        outward_dirs = [np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([0, 0, 1])]  # Radial outward
        for dir_vec in outward_dirs:
            ax.quiver(*spike_pos, *dir_vec * 0.2, color='yellow', label='Spike Radiation' if dir_vec[0] == 1 else "")

        # Plot tetrahedral edges (simplified base triangle)
        for i in range(3):
            start = self.quark_positions[i]
            end = self.quark_positions[(i+1) % 3]
            ax.plot([start[0], end[0]], [start[1], end[1]], [start[2], end[2]], 'k--')

        # Plot intake center
        ax.scatter(*self.intake_center, color='green', s=150, marker='x', label='Gravitational Intake (Centroid)')

        # Plot EM wash band
        ax.plot(self.em_wash_band[:, 0], self.em_wash_band[:, 1], self.em_wash_band[:, 2],
                color='orange', linewidth=3, label='EM Wash Band (Electron Formation)')

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('STE Proton Model: Tetrahedral Lattice with Void/Spike Cores')
        ax.legend()
        plt.savefig('proton_model.png', dpi=300, bbox_inches='tight')
        plt.show()  # Optional, remove if no GUI

# Example usage
if __name__ == "__main__":
    proton = ProtonModel(radius=1.0)
    proton.visualize()