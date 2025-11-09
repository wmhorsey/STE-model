import numpy as np

# --- FUNDAMENTAL ANCHORS ---
# The two anchors of the STE model. Everything else is derived from these.
E_PL = 1.22e19  # Planck Energy (GeV) - The 3D Bulk Scale
V_HIGGS = 246.0 # Higgs VEV (GeV) - The 2D Surface Scale

# --- THE FUNDAMENTAL GEARING FACTOR (H) ---
# The logarithmic hierarchy that defines all force strengths.
# H = ln(E_PL / V_HIGGS) approx 38.43
H_GEAR = np.log(E_PL / V_HIGGS)

# --- DERIVED FORCE CONSTANTS ---
# 1. Gravity (Bulk): Defined by E_PL (already set)
# 2. Strong Force (Surface): Defined by V_HIGGS (already set)

# 3. Weak Force (3D-to-2D Projection): alpha_W = e^(-2*H)
ALPHA_W = np.exp(-2 * H_GEAR)

# 4. Electromagnetism (2D-to-2D Leak):
# The "bare" alpha at the 246 GeV scale.
# alpha_bare = 1 / (pi * H_GEAR)
ALPHA_BARE = 1 / (np.pi * H_GEAR)

# The "screened" alpha at low energy (observed value for standard physics)
# We use the standard CODATA value for low-energy interactions.
ALPHA_SCREENED = 1 / 137.035999

# --- PARTICLE MASSES (GeV) ---
# Needed for the Lensing Law calculations
M_ELECTRON = 0.511e-3
M_MUON = 0.10566
M_TAU = 1.7768
M_PROTON = 0.93827

# --- STANDARD PHYSICAL CONSTANTS ---
# For converting to SI units if needed
C_LIGHT = 299792458 # m/s
H_BAR = 6.582119569e-25 # GeV*s