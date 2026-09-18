"""
core package initializer
"""
from .physics import calculate_physics_response
from .spectrum import generate_nscp_spectrum
from .damage import classify_damage_state
from .retrofitting import get_retrofit_recommendations
