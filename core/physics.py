"""
core/physics.py - NSCP 2015 Structural Mechanics & Physics Simulator
"""
import math
import numpy as np
from config.nscp_tables import (
    SEISMIC_ZONES,
    FRAME_TYPES,
    PLAN_SHAPES,
    get_near_source_factors,
    get_seismic_coefficients
)
from core.damage import classify_damage_state

def calculate_physics_response(
    stories: int,
    story_height: float,
    plan_area: float,
    fc: float,
    fy: float,
    rebar_ratio: float,
    pga: float,
    zone_str: str = "Zone 4",
    soil_type: str = "SD",
    fault_dist_km: float = 5.0,
    frame_type: str = "SMRF",
    plan_shape: str = "REGULAR",
    importance_factor: float = 1.0
):
    """
    Full physics-based structural dynamics calculation per NSCP 2015 & ACI 318.
    Computes Fundamental Period, Base Shear, Inelastic Story Displacements,
    Inter-Story Drift Ratios, Torsional Amplification, and Park-Ang Damage Index.
    """
    H_total = stories * story_height
    Z = SEISMIC_ZONES.get(zone_str, {"Z": 0.40})["Z"]
    R = FRAME_TYPES.get(frame_type, {"R": 8.5})["R"]
    Ie = importance_factor
    
    # Extract plan shape irregularity factors
    shape_info = PLAN_SHAPES.get(plan_shape, PLAN_SHAPES["REGULAR"])
    torsion_mult = shape_info["torsion_mult"]
    soft_story_mult = shape_info["soft_story_mult"]
    
    # 1. Near Source & Seismic Coefficients
    Na, Nv = get_near_source_factors(zone_str, fault_dist_km)
    Ca, Cv = get_seismic_coefficients(zone_str, soil_type, Na, Nv)
    
    # Scale Ca and Cv with user-specified PGA if different from baseline zone PGA
    pga_scale = pga / (Z * Na) if (Z * Na) > 0 else 1.0
    Ca_eff = Ca * pga_scale
    Cv_eff = Cv * pga_scale
    
    # 2. Building Mass & Weights (Typical Philippine Low-Rise RC Residence)
    floor_dl_ll = 6.3 # kN/m2
    roof_dl_ll = 4.8  # kN/m2
    
    story_weights = []
    story_masses = []
    for i in range(1, stories + 1):
        w_unit = roof_dl_ll if i == stories else floor_dl_ll
        w_i = w_unit * plan_area # kN
        m_i = (w_i * 1000) / 9.81 # kg
        story_weights.append(w_i)
        story_masses.append(m_i)
        
    W_total = sum(story_weights) # Total Seismic Weight in kN
    
    # 3. Lateral Stiffness per Story
    Ec = 4700 * math.sqrt(fc) * 1e6 # N/m2 (Pa)
    b_col = 0.35 # m
    h_col = 0.35 # m
    Ig = (b_col * (h_col**3)) / 12.0 # Gross moment of inertia per column
    
    rebar_boost = 1.0 + (rebar_ratio / 100.0) * (200000.0 / (Ec / 1e6)) * 0.05
    Ieff = 0.70 * Ig * rebar_boost
    
    num_columns = max(4, int(math.ceil(plan_area / 16.0)) + 2)
    infill_factor = 1.25
    k_base_story = num_columns * (12.0 * Ec * Ieff / (story_height**3)) * infill_factor # N/m
    
    # Apply soft-story stiffness reduction to ground floor if soft-story carport selected
    story_stiffness = []
    for i in range(stories):
        if i == 0 and soft_story_mult > 1.0:
            story_stiffness.append(k_base_story / soft_story_mult)
        else:
            story_stiffness.append(k_base_story)
    
    # 4. Fundamental Period T1
    T_code = 0.0731 * (H_total ** 0.75)
    phi = [math.sin(((2 * i - 1) / (2 * stories + 1)) * (math.pi / 2)) for i in range(1, stories + 1)]
    k_gen = sum(story_stiffness[i] * ((phi[i] - (phi[i-1] if i > 0 else 0)) ** 2) for i in range(stories))
    m_gen = sum(story_masses[i] * (phi[i] ** 2) for i in range(stories))
    omega_1 = math.sqrt(k_gen / m_gen) if m_gen > 0 else 10.0
    T_dyn = (2.0 * math.pi) / omega_1
    
    T1 = min(T_dyn, 1.4 * T_code)
    T1 = max(0.08, T1)
    
    # 5. Design Base Shear V per NSCP 2015 Section 208.5.2
    V_calc = (Cv_eff * Ie / (R * T1)) * W_total
    V_max = (2.5 * Ca_eff * Ie / R) * W_total
    V_min = 0.11 * Ca_eff * Ie * W_total
    if zone_str == "Zone 4":
        V_min_z4 = (0.8 * Z * Nv * Ie / R) * W_total
        V_min = max(V_min, V_min_z4)
        
    Base_Shear = max(min(V_calc, V_max), V_min) # kN
    Base_Shear_coeff = Base_Shear / W_total
    
    # 6. Lateral Force Distribution along height
    Ft = 0.07 * T1 * Base_Shear if T1 > 0.7 else 0.0
    Ft = min(Ft, 0.25 * Base_Shear)
    V_dist = Base_Shear - Ft
    
    wh_sum = sum(story_weights[i] * ((i + 1) * story_height) for i in range(stories))
    story_forces = []
    for i in range(stories):
        h_i = (i + 1) * story_height
        Fx = (V_dist * story_weights[i] * h_i) / wh_sum
        if i == stories - 1:
            Fx += Ft
        story_forces.append(Fx) # kN
        
    story_shears = [sum(story_forces[j] for j in range(i, stories)) for i in range(stories)] # kN
    
    # 7. Elastic and Inelastic Displacements & Drift Ratios
    elastic_drifts = [(story_shears[i] * 1000.0) / story_stiffness[i] for i in range(stories)] # meters
    inelastic_drifts_m = [0.7 * R * d * torsion_mult for d in elastic_drifts] # meters
    inelastic_disps_m = [sum(inelastic_drifts_m[:i+1]) for i in range(stories)] # meters
    
    story_displacements_mm = [round(d * 1000.0, 2) for d in inelastic_disps_m]
    peak_roof_disp_mm = story_displacements_mm[-1]
    
    idr_percentages = [round((inelastic_drifts_m[i] / story_height) * 100.0, 3) for i in range(stories)]
    max_idr_pct = max(idr_percentages)
    
    drift_limit_pct = 2.5 if T1 < 0.7 else 2.0
    drift_compliance = max_idr_pct <= drift_limit_pct
    
    # 8. Floor Peak Horizontal Accelerations (Thesis SOP Question #3)
    story_accels_g = [round(story_forces[i] / story_weights[i], 3) for i in range(stories)]
    story_accels_mps2 = [round(a * 9.81, 2) for a in story_accels_g]
    peak_accel_g = max(story_accels_g)
    peak_accel_mps2 = max(story_accels_mps2)

    # 9. Park-Ang Damage Index Calculation (Retained for backwards compatibility)
    yield_disp_m = (Base_Shear * 1000.0) / (0.75 * sum(story_stiffness) / stories) # m
    mu_capacity = 4.0 if frame_type == "OMRF" else (5.5 if frame_type == "IMRF" else 7.5)
    ultimate_disp_m = yield_disp_m * mu_capacity
    
    deformation_term = (inelastic_disps_m[-1] / max(ultimate_disp_m, 1e-4))
    beta_cyclic = 0.05
    energy_term = beta_cyclic * (pga / 0.40) * (Base_Shear / max(W_total * 0.25, 1.0)) * (H_total / 3.0) * torsion_mult
    damage_index = float(np.clip(deformation_term + energy_term, 0.01, 1.25))
    
    safety_level, peis_level, damage_desc, color_code = classify_damage_state(damage_index, pga)
    
    return {
        "peak_roof_disp_mm": round(peak_roof_disp_mm, 2),
        "max_idr_pct": round(max_idr_pct, 3),
        "base_shear_kn": round(Base_Shear, 2),
        "base_shear_coeff": round(Base_Shear_coeff, 3),
        "fundamental_period_s": round(T1, 3),
        "peak_accel_g": round(peak_accel_g, 3),
        "peak_accel_mps2": round(peak_accel_mps2, 2),
        "story_accels_g": story_accels_g,
        "story_accels_mps2": story_accels_mps2,
        "damage_index": round(damage_index, 3),
        "drift_limit_pct": drift_limit_pct,
        "drift_compliance": drift_compliance,
        "story_displacements_mm": story_displacements_mm,
        "idr_percentages": idr_percentages,
        "story_forces_kn": [round(f, 2) for f in story_forces],
        "story_shears_kn": [round(v, 2) for v in story_shears],
        "total_weight_kn": round(W_total, 1),
        "Ca": Ca,
        "Cv": Cv,
        "Na": Na,
        "Nv": Nv,
        "plan_shape": plan_shape,
        "torsion_mult": torsion_mult,
        "soft_story_mult": soft_story_mult,
        "safety_level": safety_level,
        "peis_level": peis_level,
        "damage_desc": damage_desc,
        "color_code": color_code
    }
