"""
Neutron Decay Toy Simulation: STE Model Validation
Date: November 11, 2025 (Double 11s - Transition to Testing)
Author: Ceryn Nekoi (VoidPlumber)

This is a simplified 1D agent-based toy model for neutron beta decay.
- Neutron: Single u-void with two d-flares on a circular path.
- Forces: Attraction (pulls flares together), Repulsion (Pauli-like push), Drag (viscosity), Jitter (random noise).
- Goal: Emergent exponential decay matching 15-minute half-life.
- Run 10,000 trials, plot histogram of decay times.
"""

import numpy as np
import matplotlib.pyplot as plt
import random

# Simulation Parameters
CIRCUMFERENCE = 2 * np.pi * 0.841e-15  # ~ Proton radius in meters (scaled for sim)
NUM_TRIALS_BASE = 10  # For tuning
NUM_TRIALS_FULL = 50000  # For full validation
TIME_STEP = 1.0  # seconds
MAX_TIME = 3600 * 24  # 1 day in seconds
HALF_LIFE_TARGET = 15 * 60  # 15 minutes in seconds

# Initial Force Constants (will be autotuned)
g_attract = 1e-20
g_repel = 1e-19
g_drag = 0.01
g_jitter = 1e-21

# Collision Threshold
COLLISION_DIST = CIRCUMFERENCE / 100  # Small fraction of circumference

class NeutronSim:
    def __init__(self):
        # Initial positions: Flares at 0 and pi (opposite sides)
        self.pos1 = 0.0
        self.pos2 = CIRCUMFERENCE / 2
        self.vel1 = 0.0
        self.vel2 = 0.0
        self.time = 0.0

    def distance(self):
        # Shortest distance on circle
        dist = abs(self.pos1 - self.pos2)
        return min(dist, CIRCUMFERENCE - dist)

    def forces(self):
        dist = self.distance()
        if dist == 0:
            return 0, 0  # Avoid division

        # Attraction: Inverse square
        f_attract = g_attract / (dist ** 2)
        dir1 = 1 if self.pos2 > self.pos1 else -1  # Toward pos2
        dir2 = -dir1

        # Repulsion: Exponential for Pauli (strong at close range)
        f_repel = g_repel * np.exp(-dist / (CIRCUMFERENCE / 10))
        dir_repel1 = -dir1  # Away from pos2
        dir_repel2 = -dir_repel1

        # Drag: Opposes velocity
        f_drag1 = -g_drag * self.vel1
        f_drag2 = -g_drag * self.vel2

        # Jitter: Random
        f_jitter1 = random.uniform(-g_jitter, g_jitter)
        f_jitter2 = random.uniform(-g_jitter, g_jitter)

        # Total forces
        f1 = f_attract * dir1 + f_repel * dir_repel1 + f_drag1 + f_jitter1
        f2 = f_attract * dir2 + f_repel * dir_repel2 + f_drag2 + f_jitter2

        return f1, f2

    def step(self):
        f1, f2 = self.forces()
        # Update velocities (F = ma, assume m=1)
        self.vel1 += f1 * TIME_STEP
        self.vel2 += f2 * TIME_STEP
        # Update positions (modulo circumference)
        self.pos1 = (self.pos1 + self.vel1 * TIME_STEP) % CIRCUMFERENCE
        self.pos2 = (self.pos2 + self.vel2 * TIME_STEP) % CIRCUMFERENCE
        self.time += TIME_STEP

    def run(self):
        while self.time < MAX_TIME:
            self.step()
            if self.distance() < COLLISION_DIST:
                return self.time  # Decay time
        return None  # No decay

# Autotune Function
def autotune_params(target_half_life, num_trials=10, max_iter=50):
    global g_attract, g_repel, g_drag, g_jitter
    best_error = float('inf')
    best_params = (g_attract, g_repel, g_drag, g_jitter)
    
    for iteration in range(max_iter):
        decay_times = []
        for trial in range(num_trials):
            sim = NeutronSim()
            decay_time = sim.run()
            if decay_time:
                decay_times.append(decay_time)
        
        if decay_times:
            sim_half_life = np.median(decay_times)
            error = abs(sim_half_life - target_half_life) / target_half_life
            if error < best_error:
                best_error = error
                best_params = (g_attract, g_repel, g_drag, g_jitter)
                print(f"Iter {iteration}: Half-Life {sim_half_life/60:.2f} min, Error {error*100:.2f}%")
        
        # Adjust params randomly (simple hill-climbing)
        g_attract *= random.uniform(0.9, 1.1)
        g_repel *= random.uniform(0.9, 1.1)
        g_drag *= random.uniform(0.9, 1.1)
        g_jitter *= random.uniform(0.9, 1.1)
    
    g_attract, g_repel, g_drag, g_jitter = best_params
    print(f"Autotuned Params: Attract={g_attract:.2e}, Repel={g_repel:.2e}, Drag={g_drag:.2e}, Jitter={g_jitter:.2e}")

# Run Autotune
print("Autotuning parameters over 10 trials...")
autotune_params(HALF_LIFE_TARGET, NUM_TRIALS_BASE)

# Now run full simulation with tuned params
print("Running full simulation with 50,000 trials...")
decay_times = []
for trial in range(NUM_TRIALS_FULL):
    sim = NeutronSim()
    decay_time = sim.run()
    if decay_time:
        decay_times.append(decay_time)

# Analyze results
if decay_times:
    half_life_sim = np.median(decay_times)
    print(f"Full Sim Half-Life: {half_life_sim / 60:.2f} minutes")
    print(f"Target: {HALF_LIFE_TARGET / 60:.2f} minutes")
    print(f"Error: {abs(half_life_sim - HALF_LIFE_TARGET) / HALF_LIFE_TARGET * 100:.2f}%")

    # Plot histogram
    plt.hist(decay_times, bins=50, alpha=0.7, label='Decay Times')
    plt.axvline(HALF_LIFE_TARGET, color='red', linestyle='--', label='Target Half-Life')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Frequency')
    plt.title('Neutron Decay Simulation: 50k Trials')
    plt.legend()
    plt.savefig('neutron_decay_histogram_50k.png')
    plt.show()
else:
    print("No decays - params need further tuning!")