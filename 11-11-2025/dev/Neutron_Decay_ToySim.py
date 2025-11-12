import numpy as np
import matplotlib.pyplot as plt
import random
import time
import multiprocessing

# Simulation Parameters
CIRCUMFERENCE = 1.0
NUM_TRIALS_FULL = 50000 # Full run
TIME_STEP_COARSE = 1.0  # 1 second "Wait" step
TIME_STEP_FINE = 1e-6   # 1 microsecond "Crash" step
MAX_SIM_TIME = 10000.0  # 10,000s timeout
HALF_LIFE_TARGET = 15 * 60  # 900 seconds

# --- NEW "KNOBS" ---
g_attract = 4e-2  # Strong attraction for crash
g_drag = 1e-10     # Superfluid viscosity
g_jitter = 1.24e-21  # Power In
g_leak = 3.474e-22      # Calculated value
CRASH_THRESHOLD = 2.805e-19  # Battery size (calculated)

COLLISION_DIST = 0.01

class NeutronSim:
    def __init__(self):
        # Initial positions: Flares at 0 and 0.5
        self.pos1 = 0.0
        self.pos2 = 0.5
        self.vel1 = 0.0
        self.vel2 = 0.0
        self.flare1_spin = 1   # d-flare
        self.flare2_spin = -1  # anti-d-flare
        self.flare_energy = 0.0  # Cumulative charging
        self.time = 0.0
        self.time_step = TIME_STEP_COARSE
        
        # --- FORCE BALANCING ---
        global g_repel
        initial_dist = self.distance()
        initial_f_attract = g_attract / (initial_dist ** 2)
        initial_f_repel_base = np.exp(-initial_dist / (CIRCUMFERENCE / 10))
        if initial_f_repel_base > 0:
            g_repel = initial_f_attract / initial_f_repel_base
        else:
            g_repel = 0

    def distance(self):
        dist = abs(self.pos1 - self.pos2)
        return min(dist, CIRCUMFERENCE - dist)

    def forces(self):
        dist = self.distance()
        if dist == 0: dist = 1e-20
        
        # Attraction (always on)
        f_attract = g_attract / (dist ** 2)
        dir1 = 1 if self.pos2 > self.pos1 else -1
        dir2 = -dir1
        
        # Repulsion (barrier, can be turned off)
        f_repel = g_repel * np.exp(-dist / (CIRCUMFERENCE / 10))
        
        # Total forces
        f1 = f_attract * dir1 - f_repel * dir1
        f2 = f_attract * dir2 - f_repel * dir2
        
        return f1, f2

    def step(self):
        # --- THIS IS A "DUMB" MECHANICAL STEP ---
        # The "brain" (the run() function) has
        # already set the g_repel and time_step.
        
        # --- Phase 2: Mechanical Sim ---
        f1, f2 = self.forces()
        
        # Update velocities
        self.vel1 += (f1 - g_drag * self.vel1) * self.time_step
        self.vel2 += (f2 - g_drag * self.vel2) * self.time_step
        
        # Update positions
        self.pos1 = (self.pos1 + self.vel1 * self.time_step) % CIRCUMFERENCE
        self.pos2 = (self.pos2 + self.vel2 * self.time_step) % CIRCUMFERENCE
        
        self.time += self.time_step

    def run(self):
        # --- LOOP 1: THE "WAIT" PHASE (Leaky Capacitor) ---
        self.time_step = TIME_STEP_COARSE
        while self.time < MAX_SIM_TIME:
            # Calculate net charge
            p_in = abs(random.uniform(-g_jitter, g_jitter))
            p_out = g_leak
            net_charge = p_in - p_out
            if net_charge > 0:
                self.flare_energy += net_charge
            if self.flare_energy > CRASH_THRESHOLD:
                # print(f"Ignition at time {self.time:.1f}s, entering crash phase.")
                global g_repel
                g_repel = 0.0
                break
            self.time += self.time_step
        
        if self.flare_energy <= CRASH_THRESHOLD:
            return None  # No ignition
        
        # --- LOOP 2: THE "CRASH" PHASE ---
        self.time_step = TIME_STEP_FINE
        crash_timeout = self.time + 10.0
        while self.time < crash_timeout:
            self.step()
            if self.distance() < COLLISION_DIST:
                return self.time
        
        return None

def run_trial(_):
    sim = NeutronSim()
    return sim.run()

if __name__ == '__main__':
    # --- MAIN EXECUTION ---
    print(f"Running Ignition Model simulation with {NUM_TRIALS_FULL} trials...")
    decay_times = []
    progress_interval = NUM_TRIALS_FULL / 10
    next_progress = progress_interval

    start_time = time.time()
    last_update_time = start_time

    # Use multiprocessing to parallelize
    num_cores = multiprocessing.cpu_count()
    print(f"Using {num_cores} CPU cores for parallel processing.")

    with multiprocessing.Pool(processes=num_cores) as pool:
        results = pool.imap_unordered(run_trial, range(NUM_TRIALS_FULL))
        
        for i, decay_time in enumerate(results):
            if decay_time is not None:
                decay_times.append(decay_time)
            current_time = time.time()
            if i >= next_progress or (current_time - last_update_time) >= 15:
                progress_pct = int((i / NUM_TRIALS_FULL) * 100)
                if decay_times:
                    min_dt = np.min(decay_times)
                    mean_dt = np.mean(decay_times)
                    max_dt = np.max(decay_times)
                    print(f"Progress: {progress_pct}% complete - Decays: {len(decay_times)}, Min: {min_dt:.2e}s, Mean: {mean_dt:.2e}s, Max: {max_dt:.2e}s")
                else:
                    print(f"Progress: {progress_pct}% complete - No decays yet")
                next_progress += progress_interval
                last_update_time = current_time

    # --- ANALYSIS ---
    end_time = time.time()
    print(f"Simulation finished in {end_time - start_time:.2f} seconds.")

    if decay_times:
        half_life_sim = np.median(decay_times)
        print(f"Simulated Half-Life: {half_life_sim / 60:.2f} minutes")
        print(f"Target: {HALF_LIFE_TARGET / 60:.2f} minutes")
        error = abs(half_life_sim - HALF_LIFE_TARGET) / HALF_LIFE_TARGET * 100
        print(f"Error: {error:.2f}%")
        
        plt.hist(decay_times, bins=50, alpha=0.7, label='Decay Times')
        plt.axvline(half_life_sim, color='orange', linestyle='--', label=f'Sim: {half_life_sim/60:.2f} min')
        plt.axvline(HALF_LIFE_TARGET, color='red', linestyle='--', label='Target: 15.00 min')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Frequency')
        plt.title(f'Ignition Model: {len(decay_times)} Decays')
        plt.legend()
        plt.savefig('ignition_model_histogram.png')
        plt.show()
    else:
        print("No decays - adjust CRASH_THRESHOLD")
