"""
config/nscp_tables.py - NSCP 2015 Structural Code Tables, Coefficients & Limit Constants
"""

SOIL_TYPES = {
    "SA": {"name": "SA - Hard Rock", "desc": "Hard rock with shear wave velocity > 1500 m/s"},
    "SB": {"name": "SB - Rock", "desc": "Rock with shear wave velocity 760 - 1500 m/s"},
    "SC": {"name": "SC - Dense Soil / Soft Rock", "desc": "Very dense soil or soft rock (360 - 760 m/s)"},
    "SD": {"name": "SD - Stiff Soil (Typical PH)", "desc": "Stiff soil profile (180 - 360 m/s, common in Metro Manila/urban PH)"},
    "SE": {"name": "SE - Soft Soil Profile", "desc": "Soft clay or loose sand (< 180 m/s)"}
}

PLAN_SHAPES = {
    "REGULAR": {
        "name": "Regular Box / Rectangular",
        "desc": "Symmetrical rectangular plan; Center of Mass (CM) aligns with Center of Rigidity (CR). Minimal torsional eccentricity.",
        "torsion_mult": 1.0,
        "soft_story_mult": 1.0,
        "nscp_ref": "Regular Structural Configuration"
    },
    "L_SHAPE": {
        "name": "L-Shaped (Re-entrant Corner)",
        "desc": "Plan Irregularity Type 2 (Re-entrant Corners) per NSCP 2015 Table 208-9. Induces 3D torsional twisting and stress concentration at internal notch.",
        "torsion_mult": 1.25,
        "soft_story_mult": 1.0,
        "nscp_ref": "NSCP 2015 Table 208-9 Plan Irregularity Type 2"
    },
    "T_SHAPE": {
        "name": "T-Shaped / Cross Plan",
        "desc": "Plan Irregularity with projecting wings per NSCP Table 208-9. Asymmetric stiffness distribution causes moderate torsional coupling.",
        "torsion_mult": 1.20,
        "soft_story_mult": 1.0,
        "nscp_ref": "NSCP 2015 Table 208-9 Plan Irregularity Type 2"
    },
    "SOFT_STORY": {
        "name": "Open Ground Floor / Carport (Soft-Story)",
        "desc": "Vertical Stiffness Irregularity Type 1 (Soft Story) per NSCP 2015 Table 208-10. Open ground floor parking significantly reduces lower level lateral stiffness.",
        "torsion_mult": 1.15,
        "soft_story_mult": 1.45,
        "nscp_ref": "NSCP 2015 Table 208-10 Vertical Irregularity Type 1"
    }
}

FRAME_TYPES = {
    "SMRF": {"name": "Special RC Moment Frame (SMRF)", "R": 8.5, "desc": "High ductility, ductile detailing per NSCP 2015"},
    "IMRF": {"name": "Intermediate RC Frame (IMRF)", "R": 5.5, "desc": "Moderate ductility, standard residential detailing"},
    "OMRF": {"name": "Ordinary RC Frame (OMRF)", "R": 3.5, "desc": "Low ductility, basic residential concrete frame"}
}

SEISMIC_ZONES = {
    "Zone 4": {"Z": 0.40, "desc": "High Seismicity - Majority of Philippine Archipelago"},
    "Zone 2": {"Z": 0.20, "desc": "Moderate Seismicity - Palawan, Sulu, Tawi-Tawi"}
}

def get_near_source_factors(zone_str: str, fault_dist_km: float):
    """
    Computes Near-Source Factors Na and Nv per NSCP 2015 Tables 208-4 and 208-5.
    Seismic Source Type A (Major active faults like West Valley Fault, Philippine Fault).
    """
    if zone_str == "Zone 2":
        return 1.0, 1.0

    if fault_dist_km <= 2.0:
        Na = 1.5
        Nv = 2.0
    elif fault_dist_km <= 5.0:
        ratio = (fault_dist_km - 2.0) / 3.0
        Na = 1.5 - ratio * (1.5 - 1.2)
        Nv = 2.0 - ratio * (2.0 - 1.6)
    elif fault_dist_km <= 10.0:
        ratio = (fault_dist_km - 5.0) / 5.0
        Na = 1.2 - ratio * (1.2 - 1.0)
        Nv = 1.6 - ratio * (1.6 - 1.2)
    elif fault_dist_km <= 15.0:
        ratio = (fault_dist_km - 10.0) / 5.0
        Na = 1.0
        Nv = 1.2 - ratio * (1.2 - 1.0)
    else:
        Na = 1.0
        Nv = 1.0
    return round(Na, 3), round(Nv, 3)

def get_seismic_coefficients(zone_str: str, soil_type: str, Na: float, Nv: float):
    """
    Computes Seismic Coefficients Ca and Cv per NSCP 2015 Tables 208-7 and 208-8.
    """
    Z = SEISMIC_ZONES.get(zone_str, {"Z": 0.40})["Z"]
    
    if zone_str == "Zone 4":
        ca_table = {"SA": 0.32 * Na, "SB": 0.40 * Na, "SC": 0.40 * Na, "SD": 0.44 * Na, "SE": 0.44 * Na}
        cv_table = {"SA": 0.32 * Nv, "SB": 0.40 * Nv, "SC": 0.56 * Nv, "SD": 0.64 * Nv, "SE": 0.96 * Nv}
    else: # Zone 2
        ca_table = {"SA": 0.16, "SB": 0.20, "SC": 0.24, "SD": 0.28, "SE": 0.34}
        cv_table = {"SA": 0.16, "SB": 0.20, "SC": 0.32, "SD": 0.40, "SE": 0.64}
        
    Ca = ca_table.get(soil_type, 0.44 * Na)
    Cv = cv_table.get(soil_type, 0.64 * Nv)
    return round(Ca, 3), round(Cv, 3)
