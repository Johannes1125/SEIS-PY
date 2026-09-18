"""
model.py - Structural Engineering Physics & Machine Learning Pipeline
(Maintains 100% backward compatibility by re-exporting from config, core, and ml packages)
"""
from config.nscp_tables import (
    SOIL_TYPES,
    PLAN_SHAPES,
    FRAME_TYPES,
    SEISMIC_ZONES,
    get_near_source_factors,
    get_seismic_coefficients
)
from core.spectrum import generate_nscp_spectrum
from core.damage import classify_damage_state
from core.physics import calculate_physics_response
from ml.dataset import generate_synthetic_dataset
from ml.predictor import SeismicMLPredictor, get_trained_model

__all__ = [
    "SOIL_TYPES",
    "PLAN_SHAPES",
    "FRAME_TYPES",
    "SEISMIC_ZONES",
    "get_near_source_factors",
    "get_seismic_coefficients",
    "generate_nscp_spectrum",
    "classify_damage_state",
    "calculate_physics_response",
    "generate_synthetic_dataset",
    "SeismicMLPredictor",
    "get_trained_model"
]
