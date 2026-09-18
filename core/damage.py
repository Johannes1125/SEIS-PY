"""
core/damage.py - Park-Ang Damage Index & PHIVOLCS PEIS Intensity Classification
"""
import numpy as np

def classify_damage_state(damage_index: float, pga: float):
    """
    Classifies structural damage state into performance levels,
    correlating with PHIVOLCS Earthquake Intensity Scale (PEIS).
    """
    if damage_index < 0.10:
        return (
            "Operational / Negligible Damage",
            "PEIS V - VI (Strong)",
            "Negligible structural damage; hairline superficial flexural cracks in plaster/finishes. Safe for immediate re-occupancy.",
            "#10b981" # Emerald Green
        )
    elif damage_index < 0.25:
        return (
            "Immediate Occupancy / Minor Damage",
            "PEIS VII (Destructive)",
            "Minor cracks in RC beams/columns and CHB infill. Rebar remains elastic. Building is fully habitable after minor inspection.",
            "#0284c7" # Sky Blue
        )
    elif damage_index < 0.40:
        return (
            "Life Safety / Moderate Damage",
            "PEIS VII - VIII (Very Destructive)",
            "Significant concrete spalling and visible yielding in beam-column joints. Infill masonry fractured. Structure requires repair prior to full occupancy.",
            "#eab308" # Amber Yellow
        )
    elif damage_index < 0.80:
        return (
            "Collapse Prevention / Severe Damage",
            "PEIS VIII - IX (Devastating)",
            "Severe concrete crushing, buckled rebar, wide shear cracks in columns, extensive non-ductile infill failure. Evacuation required; significant structural retrofitting needed.",
            "#f97316" # Orange
        )
    else:
        return (
            "Near Collapse / Critical Failure",
            "PEIS IX+ (Completely Devastating)",
            "Partial or complete structural failure mechanism formed (soft-story or column failure). Total structural condemnation risk.",
            "#ef4444" # Crimson Red
        )
