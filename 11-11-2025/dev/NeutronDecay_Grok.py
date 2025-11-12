import numpy as np
import random
import time

# Simulation Parameters
CIRCUMFERENCE = 1.0
NUM_TRIALS_FULL = 1000
TIME_STEP_COARSE = 1.0
TIME_STEP_FINE = 1e-6
MAX_SIM_TIME = 10000.0
MEAN_LIFETIME_TARGET = 878
HALF_LIFE_TARGET = MEAN_LIFETIME_TARGET * np.log(2)  # ~608.8

# Derived params for CV≈1
CRASH_THRESHOLD = 2.805e-19  # Arbitrary but fixed
drift = CRASH_THRESHOLD / MEAN_LIFETIME_TARGET  # ~3.19e-22
g_jitter = np.sqrt(12 * drift * CRASH_THRESHOLD)  # ~3.25e-20
g_leak = g_jitter / 2 - drift  # ~1.59e-20

COLLISION_DIST = 0.01
g_attract = 4e-2
g_drag = 1e-10
g_repel = 0.0  # Initial global

class NeutronSim:
    def __init__(self):
        self.pos1 = 0.0
        self.pos2 = 0.5
        self.vel1 = 0.0
        self.vel2 = 0.0
        self.flare1_spin = 1
        self.flare2_spin = -1
        self.flare_energy = 0.0
        self.time = 0.0
        self.time_step = TIME_STEP_COARSE
        
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
        
        f_attract = g_attract / (dist ** 2)
        dir1 = 1 if self.pos2 > self.pos1 else -1
        dir2 = -dir1
        
        f_repel = g_repel * np.exp(-dist / (CIRCUMFERENCE / 10))
        
        f1 = f_attract * dir1 - f_repel * dir1
        f2 = f_attract * dir2 - f_repel * dir2
        
        return f1, f2

    def step(self):
        f1, f2 = self.forces()
        
        self.vel1 += (f1 - g_drag * self.vel1) * self.time_step
        self.vel2 += (f2 - g_drag * self.vel2) * self.time_step
        
        self.pos1 = (self.pos1 + self.vel1 * self.time_step) % CIRCUMFERENCE
        self.pos2 = (self.pos2 + self.vel2 * self.time_step) % CIRCUMFERENCE
        
        self.time += self.time_step

    def run(self):
        self.time_step = TIME_STEP_COARSE
        while self.time < MAX_SIM_TIME:
            p_in = abs(random.uniform(-g_jitter, g_jitter))
            p_out = g_leak
            net_charge = p_in - p_out
            self.flare_energy += net_charge
            if self.flare_energy < 0:
                self.flare_energy = 0.0
            if self.flare_energy > CRASH_THRESHOLD:
                global g_repel
                g_repel = 0.0
                break
            self.time += self.time_step
        
        if self.flare_energy <= CRASH_THRESHOLD:
            return None
        
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

# --- MAIN EXECUTION ---
print(f"Running with {NUM_TRIALS_FULL} trials...")
decay_times = []
start_time = time.time()

for i in range(NUM_TRIALS_FULL):
    dt = run_trial(i)
    if dt is not None:
        decay_times.append(dt)
    if (i + 1) % 100 == 0:
        print(f"Progress: { (i+1) / NUM_TRIALS_FULL *100:.1f}% , Decays: {len(decay_times)}")

end_time = time.time()
print(f"Finished in {end_time - start_time:.2f} seconds.")

if decay_times:
    mean_life_sim = np.mean(decay_times)
    half_life_sim = np.median(decay_times)
    std_life = np.std(decay_times)
    print(f"Simulated Mean Lifetime: {mean_life_sim / 60:.2f} minutes (std: {std_life / 60:.2f} min, CV: {std_life / mean_life_sim:.2f})")
    print(f"Target Mean: {MEAN_LIFETIME_TARGET / 60:.2f} minutes")
    print(f"Simulated Half-Life (median): {half_life_sim / 60:.2f} minutes")
    print(f"Target Half-Life: {HALF_LIFE_TARGET / 60:.2f} minutes")
    error_mean = abs(mean_life_sim - MEAN_LIFETIME_TARGET) / MEAN_LIFETIME_TARGET * 100
    print(f"Mean Error: {error_mean:.2f}%")
    print(f"Min: {np.min(decay_times):.2f} s, Max: {np.max(decay_times):.2f} s")
    plt.hist(decay_times, bins=50, alpha=0.7, label='Decay Times')
    plt.axvline(mean_life_sim, color='green', linestyle='--', label=f'Mean: {mean_life_sim/60:.2f} min')
    plt.axvline(half_life_sim, color='orange', linestyle='--', label=f'Median: {half_life_sim/60:.2f} min')
    plt.axvline(MEAN_LIFETIME_TARGET, color='red', linestyle='--', label='Target Mean')
    plt.axvline(HALF_LIFE_TARGET, color='blue', linestyle='--', label='Target Half')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Frequency')
    plt.legend()
    plt.savefig('ignition_model_histogram.png')
else:
    print("No decays - adjust parameters")

    