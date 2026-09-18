"""
core/retrofitting.py - ASEP & DPWH Structural Retrofitting Recommendations Engine
"""

def get_retrofit_recommendations(damage_index: float) -> list:
    """
    Returns prioritized engineering retrofit measures based on structural damage index.
    """
    if damage_index < 0.10:
        return [
            "• <b>Superficial Visual Inspection:</b> Conduct standard post-earthquake survey for non-structural plaster cracks.",
            "• <b>CHB Wall Joint Maintenance:</b> Reseal cosmetic interface joints between concrete columns and masonry partitions.",
            "• <b>Standard Building Maintenance:</b> Ensure roof anchorage, drainage, and foundation perimeter are clear per local building maintenance ordinances."
        ]
    elif damage_index < 0.25:
        return [
            "• <b>Epoxy Crack Injection:</b> High-pressure structural epoxy injection for flexural cracks exceeding 0.3mm in RC beams.",
            "• <b>Masonry Dowel Anchors:</b> Ensure Concrete Hollow Block (CHB) infills have 10mm rebars anchored into adjacent columns @ 600mm O.C. per DPWH guidelines.",
            "• <b>Non-Structural Fastening:</b> Secure heavy parapets, water tanks, solar panels, and architectural fixtures against seismic toppling."
        ]
    elif damage_index < 0.40:
        return [
            "• <b>RC Column Jacketing / Enlargement:</b> Increase column cross-section dimensions and add confining steel ties (stirrups spaced @ 100mm O.C.) per NSCP 2015 Chapter 4 ductile detailing.",
            "• <b>Carbon Fiber Reinforced Polymer (CFRP):</b> Apply CFRP composite wrap at beam-column joint zones to enhance shear capacity and ductility.",
            "• <b>Soft-Story Remediation:</b> Eliminate open-ground soft-story irregularities by adding reinforced masonry shear panels or steel diagonal bracing."
        ]
    elif damage_index < 0.80:
        return [
            "• <b>Comprehensive Structural Retrofitting:</b> Substantial column jacketing, new reinforced concrete shear walls, and foundation micro-piling required.",
            "• <b>Frame Ductility Upgrading:</b> Convert Ordinary Moment Resisting Frame (OMRF) joints to ductile detailing conforming to Special Moment Resisting Frames (SMRF, R=8.5).",
            "• <b>Occupancy Restriction:</b> Restrict building access until structural integrity is certified by a registered Philippine Civil / Structural Engineer (ASEP member)."
        ]
    else:
        return [
            "• <b>CRITICAL EVACUATION & CONDEMNATION:</b> Building is at severe risk of collapse under strong ground motion. Immediate evacuation mandatory.",
            "• <b>Comprehensive Forensics / Demolition Assessment:</b> Engage a licensed Structural Forensic Consultant to determine if demolition or total structural reconstruction is necessary.",
            "• <b>Geotechnical & Foundation Remediation:</b> Conduct deep Soil Boring Tests (SPT) to evaluate soil liquefaction risks."
        ]
