"""
config/ph_locations.py - Philippine Geographic Hazard Presets & Active Fault Locations
"""

PH_LOCATION_PRESETS = {
    "Custom Configuration": {
        "zone": "Zone 4", "soil_type": "SD", "fault_dist": 5.0, "pga": 0.40,
        "name": "Custom Project Location"
    },
    "Metro Manila - Quezon City (West Valley Fault Corridor)": {
        "zone": "Zone 4", "soil_type": "SD", "fault_dist": 2.2, "pga": 0.45,
        "name": "Quezon City, Metro Manila"
    },
    "Metro Manila - Marikina / Pasig Valley (Soft Alluvium)": {
        "zone": "Zone 4", "soil_type": "SE", "fault_dist": 1.5, "pga": 0.50,
        "name": "Marikina City, Metro Manila"
    },
    "Metro Manila - BGC Taguig / Makati CBD": {
        "zone": "Zone 4", "soil_type": "SD", "fault_dist": 3.8, "pga": 0.40,
        "name": "Taguig / Makati, Metro Manila"
    },
    "Cebu City - Urban Stiff Soil (Central Cebu Fault)": {
        "zone": "Zone 4", "soil_type": "SC", "fault_dist": 11.5, "pga": 0.35,
        "name": "Cebu City, Central Visayas"
    },
    "Davao City - Urban Alluvium (Central Davao Fault)": {
        "zone": "Zone 4", "soil_type": "SD", "fault_dist": 6.2, "pga": 0.40,
        "name": "Davao City, Region XI"
    },
    "Baguio City - Mountain Rock (Digdig / Tebyacan Fault)": {
        "zone": "Zone 4", "soil_type": "SB", "fault_dist": 8.0, "pga": 0.50,
        "name": "Baguio City, Benguet"
    },
    "Iloilo City - Coastal Plain (West Panay Fault)": {
        "zone": "Zone 4", "soil_type": "SD", "fault_dist": 14.0, "pga": 0.35,
        "name": "Iloilo City, Western Visayas"
    },
    "Puerto Princesa, Palawan (Low Seismicity Zone 2)": {
        "zone": "Zone 2", "soil_type": "SB", "fault_dist": 30.0, "pga": 0.12,
        "name": "Puerto Princesa City, Palawan"
    }
}
