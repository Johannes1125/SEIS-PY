"""
config package initializer
"""
from .nscp_tables import (
    SOIL_TYPES,
    PLAN_SHAPES,
    FRAME_TYPES,
    SEISMIC_ZONES,
    get_near_source_factors,
    get_seismic_coefficients
)
from .ph_locations import PH_LOCATION_PRESETS
