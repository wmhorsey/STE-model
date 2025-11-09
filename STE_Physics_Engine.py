import numpy as np
from ste_constants import *

class STEPhysicsEngine:
    def __init__(self):
        self.h_gear = H_GEAR
        self.alpha_w = ALPHA_W
        self.alpha_bare = ALPHA_BARE
        self.alpha_screened = ALPHA_SCREENED

    def get_gearing_factor(self):
        """Returns the fundamental logarithmic gearing of the universe."""
        return self.h_gear

    def lensing_law(self, m_probe, m_baseline=M_ELECTRON):
        """
        Calculates the Logarithmic Lensing suppression factor (L) for a given probe.
        L = alpha * ln(m_probe / m_baseline)
        """
        # We use the screened alpha for low-energy orbital mechanics
        return self.alpha_screened * np.log(m_probe / m_baseline)

    def proton_radius_reduction(self, m_probe):
        """
        Calculates the predicted % reduction in proton radius for a given probe.
        delta = L
        """
        return self.lensing_law(m_probe)

    def rk_suppression(self, m_probe):
        """
        Calculates the R_K suppression factor for a 4-vertex decay.
        S_f = 4 * L
        Returns the predicted R_K ratio (1 - S_f).
        """
        l_factor = self.lensing_law(m_probe)
        s_f = 4 * l_factor
        return 1.0 - s_f

    def g_minus_2_anomaly(self, m_probe):
        """
        Calculates the predicted relative anomaly for g-2.
        Delta_a = L * alpha^2
        """
        l_factor = self.lensing_law(m_probe)
        return l_factor * (self.alpha_screened ** 2)

    def weak_force_coupling(self):
        """Returns the derived Weak Force coupling constant."""
        return self.alpha_w

    def gravity_hierarchy(self):
        """
        Returns the order-of-magnitude gap between Strong and Gravity forces.
        This is directly equal to the Gearing Factor H.
        """
        return self.h_gear

# --- SIMULATION TEST ---
if __name__ == '__main__':
    sim = STEPhysicsEngine()

    print(f"--- STE UNIVERSAL CONSTANTS ---")
    print(f"Fundamental Gearing Factor (H): {sim.get_gearing_factor():.4f}")
    print(f"Derived Weak Force (alpha_W):   {sim.weak_force_coupling():.4e}")
    print(f"Derived Bare EM Force (alpha):  1/{1/sim.alpha_bare:.4f}")
    print("-" * 30)
    print(f"--- LENSING LAW PREDICTIONS ---")
    
    # 1. Muon Tests
    l_muon = sim.lensing_law(M_MUON)
    print(f"[MUON] Mass Ratio: {M_MUON/M_ELECTRON:.1f}x")
    print(f"[MUON] Lensing Factor (L): {l_muon:.6f}")
    print(f"  -> Proton Radius Reduction: {sim.proton_radius_reduction(M_MUON)*100:.2f}%")
    print(f"  -> R_K Ratio Predicted:     {sim.rk_suppression(M_MUON):.4f}")
    print(f"  -> g-2 Relative Anomaly:    {sim.g_minus_2_anomaly(M_MUON)*1e6:.2f} ppm")
    print("-" * 30)

    # 2. Tau Tests (The Future Prediction)
    print(f"[TAU] Mass Ratio: {M_TAU/M_ELECTRON:.1f}x")
    print(f"  -> Proton Radius Reduction: {sim.proton_radius_reduction(M_TAU)*100:.2f}%")