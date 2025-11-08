# STE_BASE.py — The Complete Fluid Universe
# Run: python STE_BASE.py
# Your laptop = the cosmos

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# === STE CONSTANTS ===
E_Pl = 1.22e19          # Planck scale (GeV)
v = 246.22              # Higgs VEV (GeV)
H = np.log(E_Pl / v)    # Fundamental Gearing Factor = 38.43
alpha_W = np.exp(-2 * H)  # Weak coupling = 4.06e-34
alpha_v = 1 / (np.pi * H) # Bare EM at v = 1/120.7
alpha = alpha_v * (1 + (11/3) * np.log(v / 0.511) / (4 * np.pi))  # QED running to low energy
L_F = 4 * np.pi * 5.29e-11 * alpha  # Void-shell wavelength
K_G = 5.29e-11 / (L_F / (4 * np.pi))  # Gear ratio
r_p = K_G * L_F * 1e15  # Proton radius in fm

print(f"H = {H:.3f}")
print(f"alpha_W = {alpha_W:.2e}")
print(f"alpha(v) = {alpha_v:.5f}")
print(f"alpha(0) = {alpha:.5f}")
print(f"L_F = {L_F:.2e} m")
print(f"K_G = {K_G:.1f}")
print(f"r_p = {r_p:.3f} fm")

# === VISUALIZE THE FLUID ===
fig, ax = plt.subplots(figsize=(10,10), facecolor='black')
ax.set_facecolor('black')
ax.set_xlim(-100, 100)
ax.set_ylim(-100, 100)
ax.set_title("STE Fluid: 3D Bulk → 2D Shell → 1D Leak", color='white', fontsize=16)
ax.axis('off')

# Bulk (Gravity)
bulk = plt.Circle((0,0), 90, color='darkblue', alpha=0.3, label='3D Bulk (Gravity)')
ax.add_patch(bulk)

# Shell (Strong)
shell = plt.Circle((0,0), 50, color='cyan', alpha=0.5, label='2D Shell (Strong)')
ax.add_patch(shell)

# Leak (EM)
leak = plt.Circle((0,0), 20, color='lime', alpha=0.7, label='2D→2D Leak (EM)')
ax.add_patch(leak)

# Higgs VEV
higgs = plt.Circle((0,0), 5, color='magenta', alpha=1.0, label='Higgs VEV (v)')
ax.add_patch(higgs)

# Labels
plt.text(0, 95, f"$\\mathcal{{H}} = {H:.2f}$", color='white', ha='center', fontsize=14)
plt.text(0, 55, f"Strong = $v$", color='cyan', ha='center', fontsize=12)
plt.text(0, 25, f"EM = $1/(\\pi \\mathcal{{H}})$", color='lime', ha='center', fontsize=12)
plt.text(0, -5, f"Weak = $e^{{-2\\mathcal{{H}}}}$", color='yellow', ha='center', fontsize=12)

ax.legend(loc='upper right', facecolor='black', frameon=False, fontsize=10)
plt.tight_layout()
plt.savefig("STE_FLUID.png", dpi=300, facecolor='black')
print("STE_FLUID.png saved — your universe in one image.")