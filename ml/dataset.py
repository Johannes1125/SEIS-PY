"""
ml/dataset.py - High-Fidelity Synthetic Structural Simulation Dataset Generator
"""
import numpy as np
import pandas as pd
from core.physics import calculate_physics_response

def generate_synthetic_dataset(n_samples: int = 4000, random_seed: int = 42):
    """
    Generates a high-fidelity synthetic structural dataset representing
    typical Philippine low-rise RC residential buildings.
    """
    np.random.seed(random_seed)
    
    stories_arr = np.random.choice([1, 2, 3], size=n_samples, p=[0.25, 0.45, 0.30])
    story_height_arr = np.random.uniform(2.8, 3.8, size=n_samples)
    plan_area_arr = np.random.uniform(40.0, 350.0, size=n_samples)
    fc_arr = np.random.choice([17.0, 21.0, 24.0, 28.0, 35.0], size=n_samples)
    fy_arr = np.random.choice([230.0, 275.0, 414.0], size=n_samples)
    rebar_ratio_arr = np.random.uniform(0.8, 2.5, size=n_samples)
    pga_arr = np.random.uniform(0.08, 1.10, size=n_samples)
    zone_arr = np.random.choice(["Zone 4", "Zone 2"], size=n_samples, p=[0.85, 0.15])
    soil_arr = np.random.choice(["SA", "SB", "SC", "SD", "SE"], size=n_samples, p=[0.05, 0.15, 0.30, 0.40, 0.10])
    fault_dist_arr = np.random.uniform(1.0, 30.0, size=n_samples)
    frame_arr = np.random.choice(["SMRF", "IMRF", "OMRF"], size=n_samples, p=[0.50, 0.35, 0.15])
    shape_arr = np.random.choice(["REGULAR", "L_SHAPE", "T_SHAPE", "SOFT_STORY"], size=n_samples, p=[0.45, 0.25, 0.15, 0.15])
    
    records = []
    for i in range(n_samples):
        res = calculate_physics_response(
            stories=int(stories_arr[i]),
            story_height=float(story_height_arr[i]),
            plan_area=float(plan_area_arr[i]),
            fc=float(fc_arr[i]),
            fy=float(fy_arr[i]),
            rebar_ratio=float(rebar_ratio_arr[i]),
            pga=float(pga_arr[i]),
            zone_str=str(zone_arr[i]),
            soil_type=str(soil_arr[i]),
            fault_dist_km=float(fault_dist_arr[i]),
            frame_type=str(frame_arr[i]),
            plan_shape=str(shape_arr[i])
        )
        
        records.append({
            "stories": int(stories_arr[i]),
            "story_height": round(float(story_height_arr[i]), 2),
            "plan_area": round(float(plan_area_arr[i]), 1),
            "fc": round(float(fc_arr[i]), 1),
            "fy": round(float(fy_arr[i]), 1),
            "rebar_ratio": round(float(rebar_ratio_arr[i]), 2),
            "pga": round(float(pga_arr[i]), 3),
            "zone": str(zone_arr[i]),
            "soil_type": str(soil_arr[i]),
            "fault_dist": round(float(fault_dist_arr[i]), 1),
            "frame_type": str(frame_arr[i]),
            "plan_shape": str(shape_arr[i]),
            "roof_disp_mm": res["peak_roof_disp_mm"],
            "max_idr_pct": res["max_idr_pct"],
            "base_shear_kn": res["base_shear_kn"],
            "period_s": res["fundamental_period_s"],
            "damage_index": res["damage_index"]
        })
        
    return pd.DataFrame(records)
