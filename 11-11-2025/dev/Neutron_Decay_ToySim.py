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
CIRCUMFERENCE = 1.0  # Normalized for sim stability
NUM_TRIALS_BASE = 10
NUM_TRIALS_FULL = 50000
TIME_STEP = 1.0  # seconds
MAX_SIM_TIME = 10000.0  # 10,000 seconds
HALF_LIFE_TARGET = 15 * 60  # 15 minutes in seconds

# Force Constants (hybrid model, scaled)
g_attract = 4e-10  # Scaled for CIRCUMFERENCE = 1
g_repel = 5.93e-8  # Scaled for balance
g_drag = 1.0       # Viscosity
g_jitter = 1.24e-21  # Unchanged
SPIN_FLIP_BARRIER = 1.238e-21  # Lower for decays

COLLISION_DIST = 0.01  # 1% of circumference

class NeutronSim:
    def __init__(self):
        # Initial positions: Flares at 0 and 0.5 (opposite sides)
        self.pos1 = 0.0
        self.pos2 = 0.5
        self.vel1 = 0.0
        self.vel2 = 0.0
        self.flare1_spin = 1
        self.flare2_spin = 1
        self.time = 0.0

        # --- THIS IS THE FIX ---
        # 1. Set our g_attract (this is a tunable knob)
        global g_attract
        g_attract = 4e-10 
        
        # 2. Calculate the "F_attract" at the start
        initial_dist = self.distance()
        initial_f_attract = g_attract / (initial_dist ** 2)
        
        # 3. Calculate the "F_repel_base" at the start
        #    (This is the np.exp() part of the formula)
        initial_f_repel_base = np.exp(-initial_dist / (CIRCUMFERENCE / 10))
        
        # 4. NOW, *SET* g_repel to *perfectly balance* g_attract
        global g_repel
        if initial_f_repel_base > 0:
             g_repel = initial_f_attract / initial_f_repel_base
        else:
             g_repel = 0 # Avoid division by zero, though exp() shouldn't be zero
        
        # --- END FIX ---
        
        # (Load g_jitter and SPIN_FLIP_BARRIER here)
        global g_jitter, SPIN_FLIP_BARRIER, g_drag
        g_jitter = 1.24e-21
        SPIN_FLIP_BARRIER = 1.238e-21 # Your manually tuned value
        g_drag = 1.0 # Keep drag for the crash phase

        # Optional: Print to confirm balance
        # print(f"--- SIM INITIALIZED ---")
        # print(f"Initial F_attract: {initial_f_attract:.2e}")
        # print(f"Calculated g_repel: {g_repel:.2e}")
        # print(f"Initial F_repel: {g_repel * initial_f_repel_base:.2e}")
        # print(f"--- FORCES ARE BALANCED ---")

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

        # Repulsion: Exponential for Pauli (conditional on spins)
        f_repel = 0
        if self.flare1_spin == self.flare2_spin:
            f_repel = g_repel * np.exp(-dist / (CIRCUMFERENCE / 10))
        dir_repel1 = -dir1  # Away from pos2
        dir_repel2 = -dir_repel1

        # Drag: Opposes velocity
        f_drag1 = -g_drag * self.vel1
        f_drag2 = -g_drag * self.vel2

        # Jitter: Random (removed from forces, only for spin-flip)
        f_jitter1 = 0
        f_jitter2 = 0

        # Total forces
        f1 = f_attract * dir1 + f_repel * dir_repel1 + f_drag1 + f_jitter1
        f2 = f_attract * dir2 + f_repel * dir_repel2 + f_drag2 + f_jitter2

        return f1, f2

    def step(self):
        # Phase 1: Check for Trigger
        jitter_kick = abs(random.uniform(-g_jitter, g_jitter))
        if jitter_kick > SPIN_FLIP_BARRIER:
            self.flare2_spin = -1  # Flip one spin

        # Phase 2: Run Mechanical Sim
        f1, f2 = self.forces()
        # Update velocities (F = ma, assume m=1)
        self.vel1 += f1 * TIME_STEP
        self.vel2 += f2 * TIME_STEP
        # Update positions (modulo circumference)
        self.pos1 = (self.pos1 + self.vel1 * TIME_STEP) % CIRCUMFERENCE
        self.pos2 = (self.pos2 + self.vel2 * TIME_STEP) % CIRCUMFERENCE
        self.time += TIME_STEP

    def run(self):
        while self.time < MAX_SIM_TIME:
            self.step()
            if self.distance() < COLLISION_DIST:
                return self.time  # Decay time
        return None  # No decay

# Autotune Function
def autotune_params(target_half_life, num_trials=10, max_iter=100):
    global SPIN_FLIP_BARRIER
    best_error = float('inf')
    best_barrier = SPIN_FLIP_BARRIER
    
    for iteration in range(max_iter):
        decay_times = []
        for trial in range(num_trials):
            sim = NeutronSim()
            decay_time = sim.run()
            if decay_time is not None:
                decay_times.append(decay_time)
        
        if decay_times:
            sim_half_life = np.median(decay_times)
            error = abs(sim_half_life - target_half_life) / target_half_life
            if error < best_error:
                best_error = error
                best_barrier = SPIN_FLIP_BARRIER
                print(f"Iter {iteration}: Half-Life {sim_half_life/60:.2f} min, Error {error*100:.2f}%")
        
        # Adjust barrier randomly (simple hill-climbing)
        SPIN_FLIP_BARRIER *= random.uniform(0.99, 1.01)
    
    SPIN_FLIP_BARRIER = best_barrier
    print(f"Autotuned Barrier: {SPIN_FLIP_BARRIER:.2e}")

# Run Autotune
# print("Autotuning parameters over 10 trials...")
# autotune_params(HALF_LIFE_TARGET, NUM_TRIALS_BASE)

# Now run full simulation with tuned params
print("Running full simulation with 50,000 trials...")
decay_times = []
progress_interval = NUM_TRIALS_FULL / 10  # Heartbeat every 10%
next_progress = progress_interval
for trial in range(NUM_TRIALS_FULL):
    if trial >= next_progress:
        print(f"Full sim progress: {int((trial / NUM_TRIALS_FULL) * 100)}% complete")
        next_progress += progress_interval
    sim = NeutronSim()
    decay_time = sim.run()
    if decay_time is not None:
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