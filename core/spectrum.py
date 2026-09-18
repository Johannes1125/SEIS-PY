"""
core/spectrum.py - NSCP 2015 Section 208 Design Response Spectrum Generator
"""
import numpy as np

def generate_nscp_spectrum(Ca: float, Cv: float, max_T: float = 3.0, num_points: int = 200):
    """
    Generates the NSCP 2015 Design Response Spectrum Sa(T).
    Control periods:
    To = 0.2 * Cv / Ca
    Ts = Cv / (2.5 * Ca)
    """
    To = 0.2 * Cv / Ca if Ca > 0 else 0.05
    Ts = Cv / (2.5 * Ca) if Ca > 0 else 0.5
    
    T_vals = np.linspace(0.01, max_T, num_points)
    Sa_vals = []
    
    for T in T_vals:
        if T < To:
            Sa = Ca + (2.5 * Ca - Ca) * (T / To)
        elif T <= Ts:
            Sa = 2.5 * Ca
        else:
            Sa = Cv / T
        Sa_vals.append(Sa)
        
    return T_vals, np.array(Sa_vals), To, Ts
