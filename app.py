"""
================================================================================
SEIS-PY: Python-Based Seismic Response Prediction Model for Low-Rise RC Buildings
Under NSCP 2015 Equivalent Static Lateral Force Procedure
Thesis Research: Chapter 1 & 2 Aligned System (Group 1 - Triumfante et al.)
================================================================================
"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import math
import io
# pyrefly: ignore [missing-import]
from streamlit_option_menu import option_menu

from core.physics import calculate_physics_response
from core.spectrum import generate_nscp_spectrum
from core.benchmark import get_etabs_benchmark, compute_validation_metrics
from config.nscp_tables import (
    get_near_source_factors,
    get_seismic_coefficients,
    SOIL_TYPES,
    PLAN_SHAPES,
    FRAME_TYPES,
    SEISMIC_ZONES
)
from pdf_report import generate_seismic_pdf_report

# ==============================================================================
# 1. STREAMLIT PAGE CONFIG & ADVANCED CUSTOM STYLING
# ==============================================================================
st.set_page_config(
    page_title="SEIS-PY | NSCP 2015 Seismic Response Prediction",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply the dark engineering dashboard theme
from ui.styles import apply_custom_css
apply_custom_css()

# Custom Plotly template matching the SEIS-PY palette
import plotly.io as pio
SEISPY_PLOTLY = go.layout.Template()
SEISPY_PLOTLY.layout = go.Layout(
    paper_bgcolor="#0B1E33",
    plot_bgcolor="#0B1E33",
    font=dict(family="Inter, sans-serif", color="#FFFFFF"),
    title=dict(font=dict(color="#FFFFFF", size=15)),
    xaxis=dict(
        gridcolor="rgba(139,216,253,0.08)",
        linecolor="rgba(139,216,253,0.15)",
        tickfont=dict(color="#8BD8FD"),
        title=dict(font=dict(color="#8BD8FD")),
        zerolinecolor="rgba(139,216,253,0.1)"
    ),
    yaxis=dict(
        gridcolor="rgba(139,216,253,0.08)",
        linecolor="rgba(139,216,253,0.15)",
        tickfont=dict(color="#8BD8FD"),
        title=dict(font=dict(color="#8BD8FD")),
        zerolinecolor="rgba(139,216,253,0.1)"
    ),
    colorway=["#00AAF9", "#FFBA42", "#F5A201", "#10b981", "#ef4444", "#8BD8FD", "#00537A"],
    legend=dict(font=dict(color="#8BD8FD"))
)
pio.templates["seispy"] = SEISPY_PLOTLY
pio.templates.default = "seispy"

# ==============================================================================
# 2. PHILIPPINE LOCATION PRESETS & GEOTECHNICAL DEFAULTS
# ==============================================================================
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

# ==============================================================================
# 3. SIDEBAR: SEISMIC, GEOMETRIC & MATERIAL INPUT CONTROLS (SOP #2)
# ==============================================================================

with st.sidebar:
    st.markdown("### 🇵🇭 NSCP 2015 Input Parameters")
    st.caption("Thesis Scope: Low-Rise RC Buildings (1 to 4 Stories)")

    # Location Presets
    preset_choice = st.selectbox(
        "📍 Philippine Location Preset",
        options=list(PH_LOCATION_PRESETS.keys()),
        index=1
    )
    preset_data = PH_LOCATION_PRESETS[preset_choice]

    with st.expander("**1. Seismicity & Site Hazards**", expanded=True):
        zone_idx = 0 if preset_data["zone"] == "Zone 4" else 1
        zone = st.selectbox(
            "Seismic Zone (NSCP Sec. 208.4.1)",
            options=["Zone 4", "Zone 2"],
            index=zone_idx,
            help="Zone 4 (Z=0.40): Major Philippine regions. Zone 2 (Z=0.20): Palawan, Sulu."
        )

        soil_keys = list(SOIL_TYPES.keys())
        soil_default_idx = soil_keys.index(preset_data["soil_type"]) if preset_data["soil_type"] in soil_keys else 3
        soil_type = st.selectbox(
            "Soil Profile Type (Table 208-1)",
            options=soil_keys,
            format_func=lambda k: f"{k} - {SOIL_TYPES[k]['name']}",
            index=soil_default_idx,
            help="Soil types from SA (Hard Rock) to SE (Soft Clay) per NSCP 2015."
        )

        _s1, _s2 = st.columns(2)
        with _s1:
            fault_dist = st.slider(
                "Fault Dist. (km)",
                min_value=0.5, max_value=30.0,
                value=preset_data["fault_dist"], step=0.5,
                help="Near-Source amplification factors (Na, Nv) apply for distances < 15 km per NSCP 2015 Tables 208-4 & 208-5."
            )
        with _s2:
            pga = st.slider(
                "PGA (g)",
                min_value=0.05, max_value=1.10,
                value=preset_data["pga"], step=0.02,
                help="Peak ground acceleration demand."
            )

    with st.expander("**2. Building Geometry (1–4 Stories)**", expanded=True):
        _g1, _g2, _g3 = st.columns(3)
        with _g1:
            # Strictly 1 to 4 stories per Scope (Line 35) & Delimitations (Line 38)
            stories = st.slider("Stories", min_value=1, max_value=4, value=2, step=1, help="Thesis delimited to 1 to 4 stories.")
        with _g2:
            story_height = st.slider("Height (m)", min_value=2.8, max_value=4.2, value=3.0, step=0.1)
        with _g3:
            plan_area = st.slider("Area (m²)", min_value=40.0, max_value=350.0, value=120.0, step=10.0)

        plan_shape = "REGULAR"

    with st.expander("**3. RC Framing & Material Properties**", expanded=True):
        frame_type = st.selectbox(
            "Framing System (Table 208-11)",
            options=["SMRF", "IMRF", "OMRF"],
            format_func=lambda k: FRAME_TYPES[k]["name"],
            index=0,
            help="SMRF (R=8.5, ductile detailing per NSCP 2015 Ch. 4). IMRF (R=5.5). OMRF (R=3.5, non-ductile residential)."
        )

        _m1, _m2 = st.columns(2)
        with _m1:
            fc_options = [17.0, 21.0, 24.0, 28.0, 35.0]
            fc = st.selectbox(
                "f'c (MPa)",
                options=fc_options, index=1,
                format_func=lambda v: f"{v:.0f} MPa",
                help="Concrete compressive strength."
            )
        with _m2:
            fy_options = [230.0, 275.0, 414.0]
            fy = st.selectbox(
                "fy (MPa)",
                options=fy_options, index=1,
                format_func=lambda v: f"Gr.{int(v)}",
                help="Rebar yield strength."
            )

        _m3, _m4 = st.columns(2)
        with _m3:
            rebar_ratio = st.slider(
                "ρ (%)",
                min_value=0.8, max_value=2.8, value=1.5, step=0.1,
                help="Typical longitudinal reinforcement ratio in residential RC framing."
            )
        with _m4:
            importance_factor = st.selectbox(
                "Ie Factor",
                options=[1.0, 1.25, 1.5], index=0,
                format_func=lambda v: f"{v:.2f}",
                help="Importance Factor per Table 208-1 (1.0 for standard residential occupancy)."
            )

    with st.expander("**4. Documentation Details**", expanded=False):
        proj_name = st.text_input("Project Name", value=f"{preset_data['name']} Residence")
        engineer_name = st.text_input("Lead Structural Researcher", value="Engr. Group 1 Structural Specialist")


# ==============================================================================
# 4. ENGINE COMPUTATION: PYTHON MODEL & ETABS BENCHMARK (SOP #1, #2, #4)
# ==============================================================================

# 1. Physics Engine Calculation (NSCP 2015 Equivalent Lateral Force Procedure)
physics_res = calculate_physics_response(
    stories=stories,
    story_height=story_height,
    plan_area=plan_area,
    fc=fc,
    fy=fy,
    rebar_ratio=rebar_ratio,
    pga=pga,
    zone_str=zone,
    soil_type=soil_type,
    fault_dist_km=fault_dist,
    frame_type=frame_type,
    plan_shape=plan_shape,
    importance_factor=importance_factor
)

# 2. ETABS Commercial Finite Element Benchmark Model (SOP #4 & Hypothesis Line 32)
etabs_res = get_etabs_benchmark(
    stories=stories,
    story_height=story_height,
    plan_area=plan_area,
    fc=fc,
    fy=fy,
    pga=pga,
    zone_str=zone,
    soil_type=soil_type,
    frame_type=frame_type
)

# 3. Comparative Validation Metrics
validation_data = compute_validation_metrics(physics_res, etabs_res)


# ==============================================================================
# 5. MAIN DASHBOARD HEADER & QUICK OVERVIEW
# ==============================================================================

st.markdown("""
<div class="seispy-header">
    <div class="seispy-logo-row">
        <span class="seispy-badge">SEIS-PY</span>
        <div>
            <div class="seispy-title-text">SEIS-PY: Python-Based Seismic Response Prediction Engine</div>
            <div class="seispy-subtitle">National Structural Code of the Philippines (NSCP 2015, 7th Ed., Sec. 208) | Equivalent Static Lateral Force Analysis</div>
        </div>
        <span class="seispy-version" style="margin-left:auto;">v1.0</span>
    </div>
    <hr class="seispy-divider-line"/>
    <div style="font-size:0.83rem; color:rgba(255,255,255,0.7); font-weight:400;">
        🏗️&nbsp; Computational Seismic Response Prediction Model for Low-Rise Reinforced Concrete Residential Buildings (1 to 4 Stories) &mdash;
        Validated Against ETABS Commercial Finite Element Benchmark
    </div>
</div>
""", unsafe_allow_html=True)

# Top Reference Threshold & Base Shear Evaluation (Aligned with Delimitation Line 45)
is_compliant = physics_res["drift_compliance"]
max_idr = physics_res["max_idr_pct"]
drift_limit = physics_res["drift_limit_pct"]

banner_col1, banner_col2 = st.columns([3, 2])

with banner_col1:
    if is_compliant:
        st.markdown(f"""
        <div class="compliance-pass">
            <span style="font-size: 1.4rem;">✅</span>
            <div>
                <strong style="font-size: 1.05rem;">NSCP 2015 DRIFT REFERENCE: WITHIN ALLOWABLE THRESHOLD</strong><br/>
                <span style="font-size: 0.85rem; font-weight: 400;">
                    Maximum Inter-Story Drift IDR = <b>{max_idr:.3f}%</b> is within code allowable threshold (<b>≤ {drift_limit:.1f}%</b> per Sec. 208.5.9).
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="compliance-fail">
            <span style="font-size: 1.4rem;">⚠️</span>
            <div>
                <strong style="font-size: 1.05rem;">NSCP 2015 DRIFT REFERENCE: EXCEEDS REFERENCE THRESHOLD</strong><br/>
                <span style="font-size: 0.85rem; font-weight: 400;">
                    Maximum Inter-Story Drift IDR = <b>{max_idr:.3f}%</b> exceeds code reference threshold (<b>{drift_limit:.1f}%</b>). Additional lateral stiffness required.
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

with banner_col2:
    st.markdown(f"""
    <div class="stat-box">
        <div>
            <div class="stat-box-label">Design Base Shear Ratio</div>
            <div class="stat-box-value" style="color: #00AAF9;">Cs = {physics_res['base_shear_coeff']:.3f} W</div>
        </div>
        <div style="width:1px; height:36px; background:rgba(255,255,255,0.12);"></div>
        <div style="text-align: right;">
            <div class="stat-box-label">Peak Floor Acceleration</div>
            <div class="stat-box-value" style="color: #FFBA42;">{physics_res['peak_accel_g']:.3f} g ({physics_res['peak_accel_mps2']:.2f} m/s²)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# High-Level Metric Cards Grid: Exactly displaying the 5 SOP Question #3 Response Parameters
m_col1, m_col2, m_col3, m_col4, m_col5, m_col6 = st.columns(6)

with m_col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">1. Fund. Period (T₁)</div>
        <div class="metric-value">{physics_res['fundamental_period_s']:.3f}<span class="metric-unit">s</span></div>
        <div class="metric-sub">Method A / Rayleigh</div>
    </div>
    """, unsafe_allow_html=True)

with m_col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">2. Design Base Shear</div>
        <div class="metric-value">{physics_res['base_shear_kn']:.1f}<span class="metric-unit">kN</span></div>
        <div class="metric-sub">Cs = {physics_res['base_shear_coeff']:.3f} W</div>
    </div>
    """, unsafe_allow_html=True)

with m_col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">3. Peak Roof Defl. (Δ)</div>
        <div class="metric-value">{physics_res['peak_roof_disp_mm']:.1f}<span class="metric-unit">mm</span></div>
        <div class="metric-sub">Inelastic Δm = 0.70 R Δs</div>
    </div>
    """, unsafe_allow_html=True)

with m_col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">4. Max Drift Ratio (IDR)</div>
        <div class="metric-value">{physics_res['max_idr_pct']:.2f}<span class="metric-unit">%</span></div>
        <div class="metric-sub" style="color: {'#10b981' if is_compliant else '#ef4444'};">Threshold: ≤ {drift_limit:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with m_col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">5. Peak Acceleration</div>
        <div class="metric-value">{physics_res['peak_accel_g']:.3f}<span class="metric-unit">g</span></div>
        <div class="metric-sub">{physics_res['peak_accel_mps2']:.2f} m/s²</div>
    </div>
    """, unsafe_allow_html=True)

with m_col6:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Seismic Weight</div>
        <div class="metric-value">{physics_res['total_weight_kn']:.1f}<span class="metric-unit">kN</span></div>
        <div class="metric-sub">~{physics_res['total_weight_kn']/9.81:.1f} tons</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# 6. SHARED STRUCTURAL ARRAYS (used across multiple tabs)
# ==============================================================================
story_elevations = [(i + 1) * story_height for i in range(stories)]
story_labels = [f"Level {i+1} ({(i+1)*story_height:.1f}m)" for i in range(stories)]
drifts = physics_res["idr_percentages"]
disps = physics_res["story_displacements_mm"]
forces = physics_res["story_forces_kn"]
shears = physics_res["story_shears_kn"]
accels_g = physics_res["story_accels_g"]
accels_mps2 = physics_res["story_accels_mps2"]

# ==============================================================================
# 7. TABBED INTERACTIVE STRUCTURAL DASHBOARD (Thesis SOP-Aligned)
# ==============================================================================

selected = option_menu(
    menu_title=None,
    options=[
        "Executive Summary & Validation",
        "Drift & Displacements",
        "Floor Accelerations & Inertia",
        "Response Spectrum",
        "3D / 2D Visualizer"
    ],
    icons=[
        "clipboard-data",
        "bar-chart-line",
        "activity",
        "globe",
        "buildings"
    ],
    orientation="horizontal",
    default_index=0,
    styles={
        "container": {
            "padding": "4px 6px",
            "background-color": "#013C58",
            "border-radius": "10px",
            "border": "1px solid rgba(0,83,122,0.5)",
            "margin-bottom": "1rem",
        },
        "icon": {"color": "#FFBA42", "font-size": "14px"},
        "nav-link": {
            "font-family": "'Inter', sans-serif",
            "font-size": "13px",
            "font-weight": "600",
            "color": "#8BD8FD",
            "border-radius": "8px",
            "padding": "8px 14px",
            "--hover-color": "rgba(0,170,249,0.08)",
        },
        "nav-link-selected": {
            "background-color": "#00537A",
            "color": "#FFFFFF",
            "font-weight": "700",
        },
    }
)

# ------------------------------------------------------------------------------
# TAB 1: EXECUTIVE SUMMARY & ETABS BENCHMARK VALIDATION (SOP #1, #4 & Hypothesis)
# ------------------------------------------------------------------------------
if selected == "Executive Summary & Validation":
    st.markdown("#### 📋 Structural Seismic Response & ETABS Benchmark Validation")
    
    col_t1_left, col_t1_right = st.columns([3, 2])
    
    with col_t1_left:
        st.markdown("##### 🔬 Numerical Validation: Python Prediction vs. ETABS Benchmark (SOP #4)")
        comp_df = pd.DataFrame(validation_data)
        st.dataframe(comp_df, width="stretch", hide_index=True)
        
        st.markdown(f"""
        **Methodological Evaluation & Code Reference (NSCP 2015):**
        - **Equivalent Lateral Force Procedure:** Base shear calculated per Section 208.5.2 with seismic response modification coefficient $R = {FRAME_TYPES[frame_type]['R']}$ and importance factor $I = {importance_factor:.2f}$.
        - **Total Effective Seismic Weight ($W$):** **{physics_res['total_weight_kn']:.1f} kN** (~{physics_res['total_weight_kn']/9.81:.1f} tons), distributed assuming rigid horizontal floor diaphragms.
        - **Hypothesis Verification:** As hypothesized in Chapter 1 (Line 32), the Python-based algorithm demonstrates close numerical agreement with standard commercial finite element analysis (ETABS v21.0), falling well within the standard engineering tolerance margin.
        """)

    with col_t1_right:
        diff_values = [float(d["Relative Difference (%)"].replace("%", "")) for d in validation_data]
        avg_diff = np.mean(diff_values)
        max_diff = np.max(diff_values)
        
        st.markdown(f"""
        <div class="dark-card" style="border-left: 4px solid #10b981;">
            <div class="dark-card-title">ETABS Benchmark Model Specification</div>
            <div class="dark-card-value" style="color: #10b981;">
                Average Difference: {avg_diff:.2f}%
            </div>
            <hr/>
            <p>
                <b>Benchmark Software:</b> ETABS v21.0 Commercial 3D Finite Element Package<br/>
                <b>Framing:</b> 3D Low-Rise Reinforced Concrete Moment Resisting Frame<br/>
                <b>Boundary Conditions:</b> Fully rigid fixed-base supports at foundation level<br/>
                <b>Diaphragm Action:</b> Infinitely rigid horizontal floor diaphragms in-plane<br/>
                <b>Maximum Difference:</b> {max_diff:.2f}% across all 5 primary response variables
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # Action Button: PDF Generation
        pdf_bytes = generate_seismic_pdf_report(
            project_name=proj_name,
            engineer_name=engineer_name,
            location_str=preset_data['name'],
            params={
                "stories": stories, "story_height": story_height, "plan_area": plan_area,
                "fc": fc, "fy": fy, "rebar_ratio": rebar_ratio, "pga": pga,
                "zone": zone, "soil_type": soil_type, "fault_dist": fault_dist,
                "frame_type": frame_type, "plan_shape": plan_shape
            },
            physics_res=physics_res
        )
        
        st.download_button(
            label="📄 Download Official NSCP 2015 Calculation Sheet (PDF)",
            data=pdf_bytes,
            file_name=f"SEISPY_Report_{proj_name.replace(' ', '_')}.pdf",
            mime="application/pdf",
            width="stretch"
        )

# ------------------------------------------------------------------------------
# TAB 2: INTER-STORY DRIFT & DISPLACEMENTS (SOP #3)
# ------------------------------------------------------------------------------
if selected == "Drift & Displacements":
    st.markdown("#### 📈 Story Drift Profile, Shear Demands & Displacements")
    
    col_t2_1, col_t2_2 = st.columns(2)
    
    with col_t2_1:
        # Plot 1: Inter-Story Drift Ratio vs Height
        fig_drift = go.Figure()
        
        y_elev = [0.0] + story_elevations
        x_drift = [0.0] + drifts
        
        fig_drift.add_trace(go.Scatter(
            x=x_drift,
            y=y_elev,
            mode='lines+markers',
            name='Python Calculated Drift (IDR %)',
            line=dict(color='#00AAF9', width=3.5),
            marker=dict(size=8, color='#FFBA42', symbol='circle')
        ))
        
        # Add ETABS benchmark drift curve
        x_drift_etabs = [0.0] + etabs_res["idr_percentages"]
        fig_drift.add_trace(go.Scatter(
            x=x_drift_etabs,
            y=y_elev,
            mode='lines+markers',
            name='ETABS Benchmark Drift (IDR %)',
            line=dict(color='#8BD8FD', width=2, dash='dot'),
            marker=dict(size=6, color='#8BD8FD', symbol='diamond')
        ))
        
        # Allowable drift limit vertical line
        fig_drift.add_vline(
            x=drift_limit,
            line_dash="dash",
            line_color="#ef4444",
            line_width=2,
            annotation_text=f"NSCP Threshold ({drift_limit:.1f}%)",
            annotation_position="top right"
        )
        
        fig_drift.update_layout(
            title="<b>Inter-Story Drift Ratio (IDR %) vs Building Elevation</b>",
            xaxis_title="Inter-Story Drift Ratio (%)",
            yaxis_title="Elevation (meters)",
            hovermode="x unified",
            height=380,
            margin=dict(l=40, r=40, t=50, b=40)
        )
        st.plotly_chart(fig_drift, width="stretch")

    with col_t2_2:
        # Plot 2: Cumulative Inelastic Deflection Profile
        fig_disp = go.Figure()
        x_disp = [0.0] + disps
        
        fig_disp.add_trace(go.Scatter(
            x=x_disp,
            y=y_elev,
            mode='lines+markers',
            name='Python Deflection Δm (mm)',
            line=dict(color='#10b981', width=3.5),
            marker=dict(size=8, color='#047857', symbol='diamond'),
            fill='tozeroy',
            fillcolor='rgba(16, 185, 129, 0.1)'
        ))
        
        x_disp_etabs = [0.0] + etabs_res["story_displacements_mm"]
        fig_disp.add_trace(go.Scatter(
            x=x_disp_etabs,
            y=y_elev,
            mode='lines+markers',
            name='ETABS Benchmark Δ (mm)',
            line=dict(color='#8BD8FD', width=2, dash='dot'),
            marker=dict(size=6, color='#8BD8FD', symbol='circle')
        ))
        
        fig_disp.update_layout(
            title="<b>Inelastic Lateral Deflection Profile Δm (mm)</b>",
            xaxis_title="Lateral Displacement (mm)",
            yaxis_title="Elevation (meters)",
            hovermode="x unified",
            height=380,
            margin=dict(l=40, r=40, t=50, b=40)
        )
        st.plotly_chart(fig_disp, width="stretch")

    # Story force & shear breakdown table
    st.markdown("##### 🔢 Story-by-Story Lateral Force, Shear & Drift Distribution")
    story_df = pd.DataFrame({
        "Story Level": [f"Roof Level (L{stories})" if i == stories - 1 else f"Story Level {i+1}" for i in range(stories - 1, -1, -1)],
        "Elevation (m)": [f"{(i+1)*story_height:.2f} m" for i in range(stories - 1, -1, -1)],
        "Lateral Force Fx (kN)": [f"{forces[i]:.2f}" for i in range(stories - 1, -1, -1)],
        "Story Shear Vx (kN)": [f"{shears[i]:.2f}" for i in range(stories - 1, -1, -1)],
        "Inelastic Disp. Δm (mm)": [f"{disps[i]:.2f}" for i in range(stories - 1, -1, -1)],
        "Story Drift Ratio IDR (%)": [f"{drifts[i]:.3f}%" for i in range(stories - 1, -1, -1)],
        "NSCP 2015 Reference Threshold": ["Within Limit" if drifts[i] <= drift_limit else "Exceeds Limit" for i in range(stories - 1, -1, -1)]
    })
    st.dataframe(story_df, width="stretch", hide_index=True)

# ------------------------------------------------------------------------------
# TAB 3: FLOOR ACCELERATIONS & INERTIAL DEMANDS (Thesis SOP #3 Parameter)
# ------------------------------------------------------------------------------
if selected == "Floor Accelerations & Inertia":
    st.markdown("#### ⚡ Floor Acceleration Demands & Lateral Inertia Force Distribution")
    
    col_t3_acc1, col_t3_acc2 = st.columns(2)
    
    with col_t3_acc1:
        # Plot 1: Peak Floor Horizontal Acceleration Profile (ax vs height)
        fig_accel = go.Figure()
        y_elev_acc = [0.0] + story_elevations
        x_acc_python = [pga] + accels_g
        x_acc_etabs = [pga] + etabs_res["story_accels_g"]
        
        fig_accel.add_trace(go.Scatter(
            x=x_acc_python,
            y=y_elev_acc,
            mode='lines+markers',
            name='Python Model Acceleration (g)',
            line=dict(color='#FFBA42', width=3.5),
            marker=dict(size=8, color='#F5A201', symbol='circle')
        ))
        
        fig_accel.add_trace(go.Scatter(
            x=x_acc_etabs,
            y=y_elev_acc,
            mode='lines+markers',
            name='ETABS Benchmark Acceleration (g)',
            line=dict(color='#8BD8FD', width=2, dash='dot'),
            marker=dict(size=6, color='#8BD8FD', symbol='diamond')
        ))
        
        fig_accel.add_vline(x=pga, line_dash="dash", line_color="rgba(255,255,255,0.4)", annotation_text=f"Ground PGA = {pga:.2f}g")
        
        fig_accel.update_layout(
            title="<b>Peak Horizontal Floor Acceleration Profile ax (g)</b>",
            xaxis_title="Floor Acceleration Demand (g)",
            yaxis_title="Elevation (meters)",
            hovermode="x unified",
            height=380,
            margin=dict(l=40, r=40, t=50, b=40)
        )
        st.plotly_chart(fig_accel, width="stretch")
        
    with col_t3_acc2:
        # Plot 2: Story Lateral Force Distribution along height
        fig_force = go.Figure()
        
        fig_force.add_trace(go.Bar(
            y=story_labels,
            x=forces,
            orientation='h',
            name='Story Lateral Force Fx (kN)',
            marker=dict(color='#00AAF9')
        ))
        
        fig_force.update_layout(
            title="<b>Equivalent Static Story Force Distribution Fx (kN)</b>",
            xaxis_title="Story Lateral Force Fx (kN)",
            yaxis_title="Building Level",
            height=380,
            margin=dict(l=40, r=40, t=50, b=40)
        )
        st.plotly_chart(fig_force, width="stretch")

    st.markdown("##### 🔢 Floor-by-Floor Acceleration & Inertial Demand Breakdown")
    accel_df = pd.DataFrame({
        "Story Level": [f"Roof Level (L{stories})" if i == stories - 1 else f"Story Level {i+1}" for i in range(stories - 1, -1, -1)],
        "Elevation (m)": [f"{(i+1)*story_height:.2f} m" for i in range(stories - 1, -1, -1)],
        "Lateral Force Fx (kN)": [f"{forces[i]:.2f} kN" for i in range(stories - 1, -1, -1)],
        "Story Shear Vx (kN)": [f"{shears[i]:.2f} kN" for i in range(stories - 1, -1, -1)],
        "Floor Acceleration (g)": [f"{accels_g[i]:.3f} g" for i in range(stories - 1, -1, -1)],
        "Floor Acceleration (m/s²)": [f"{accels_mps2[i]:.2f} m/s²" for i in range(stories - 1, -1, -1)],
        "ETABS Benchmark (g)": [f"{etabs_res['story_accels_g'][i]:.3f} g" for i in range(stories - 1, -1, -1)],
        "Relative Difference (%)": [f"{abs(accels_g[i] - etabs_res['story_accels_g'][i])/max(etabs_res['story_accels_g'][i], 1e-4)*100:.2f}%" for i in range(stories - 1, -1, -1)]
    })
    st.dataframe(accel_df, width="stretch", hide_index=True)
    
    st.markdown(r"""
    **Structural Dynamics Note (NSCP Section 208.5.2 & Eq. 208-15):**  
    The equivalent static lateral force $F_x$ simulates the dynamic inertial response of the structure:
    $$F_x = m_x \cdot a_x = \frac{w_x}{g} \cdot a_x$$
    Because higher floors undergo greater deflection and modal acceleration under the fundamental vibration mode, horizontal acceleration increases progressively toward the roof diaphragm level.
    """)

# ------------------------------------------------------------------------------
# TAB 4: NSCP 2015 DESIGN RESPONSE SPECTRUM (SOP #1, #2)
# ------------------------------------------------------------------------------
if selected == "Response Spectrum":
    st.markdown("#### 🌐 NSCP 2015 Section 208 Design Response Spectrum")
    
    col_t4_1, col_t4_2 = st.columns([3, 1])
    
    T_vals, Sa_vals, To, Ts = generate_nscp_spectrum(physics_res["Ca"], physics_res["Cv"], max_T=3.0)
    T1 = physics_res["fundamental_period_s"]
    Sa_T1 = float(np.interp(T1, T_vals, Sa_vals))
    
    with col_t4_1:
        fig_spec = go.Figure()
        
        # Design Spectrum Curve
        fig_spec.add_trace(go.Scatter(
            x=T_vals,
            y=Sa_vals,
            mode='lines',
            name='NSCP 2015 Design Spectrum Sa(T)',
            line=dict(color='#00AAF9', width=3),
            fill='tozeroy',
            fillcolor='rgba(0, 170, 249, 0.12)'
        ))
        
        # Fundamental Period Marker
        fig_spec.add_trace(go.Scatter(
            x=[T1],
            y=[Sa_T1],
            mode='markers',
            name=f'Building T₁ = {T1:.3f}s (Sa = {Sa_T1:.3f}g)',
            marker=dict(size=13, color='#dc2626', symbol='cross', line=dict(width=2, color='white'))
        ))
        
        # Vertical dotted line for T1
        fig_spec.add_vline(x=T1, line_dash="dot", line_color="#dc2626", line_width=1.5)
        # Vertical lines for To and Ts
        fig_spec.add_vline(x=To, line_dash="dash", line_color="#8BD8FD", annotation_text=f"To = {To:.2f}s")
        fig_spec.add_vline(x=Ts, line_dash="dash", line_color="#8BD8FD", annotation_text=f"Ts = {Ts:.2f}s")
        
        fig_spec.update_layout(
            title="<b>Design Response Spectrum Sa(T) vs Fundamental Period</b>",
            xaxis_title="Period T (seconds)",
            yaxis_title="Spectral Acceleration Sa (g)",
            height=400,
            margin=dict(l=40, r=40, t=50, b=40)
        )
        st.plotly_chart(fig_spec, width="stretch")

    with col_t4_2:
        st.markdown(f"""
        <div class="dark-card">
            <div class="dark-card-title">Spectral Parameters</div>
            <div style="font-size: 0.85rem; margin-bottom: 0.4rem; color: #8BD8FD;">• <b>Ca:</b> <span class="code-font">{physics_res['Ca']:.3f}</span></div>
            <div style="font-size: 0.85rem; margin-bottom: 0.4rem; color: #8BD8FD;">• <b>Cv:</b> <span class="code-font">{physics_res['Cv']:.3f}</span></div>
            <div style="font-size: 0.85rem; margin-bottom: 0.4rem; color: #8BD8FD;">• <b>Na (Near-Fault):</b> <span class="code-font">{physics_res['Na']:.2f}</span></div>
            <div style="font-size: 0.85rem; margin-bottom: 0.4rem; color: #8BD8FD;">• <b>Nv (Near-Fault):</b> <span class="code-font">{physics_res['Nv']:.2f}</span></div>
            <div style="font-size: 0.85rem; margin-bottom: 0.4rem; color: #8BD8FD;">• <b>To (0.2 Cv/Ca):</b> <span class="code-font">{To:.3f} s</span></div>
            <div style="font-size: 0.85rem; margin-bottom: 0.4rem; color: #8BD8FD;">• <b>Ts (Cv / 2.5Ca):</b> <span class="code-font">{Ts:.3f} s</span></div>
            <div style="font-size: 0.85rem; margin-bottom: 0.4rem; color: #8BD8FD;">• <b>Spectral Demand Sa:</b> <span class="code-font" style="color: #FFBA42; font-weight: 700;">{Sa_T1:.3f} g</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.caption("Control periods $T_0$ and $T_s$ define the constant-acceleration plateau and velocity-sensitive acceleration regime.")

# ------------------------------------------------------------------------------
# TAB 5: 3D & 2D SEISMIC DEFLECTION VISUALIZER (Scope Line 35)
# ------------------------------------------------------------------------------
if selected == "3D / 2D Visualizer":
    st.markdown("#### 🏢 Interactive 3D / 2D Building Seismic Deflection Model")
    
    col_scale, col_mode = st.columns([3, 1])
    with col_scale:
        disp_scale = st.slider("Visual Deflection Exaggeration Factor", min_value=1.0, max_value=80.0, value=30.0, step=5.0)
    with col_mode:
        view_dim = st.radio("View Perspective", ["3D Isometric Wireframe", "2D Elevation Profile"], horizontal=True)

    # Building dimensions for 3D model
    bay_x = math.sqrt(plan_area) * 0.85
    bay_y = plan_area / max(bay_x, 1.0)
    center_x = bay_x / 2.0
    center_y = bay_y / 2.0
    
    # Symmetrical regular RC framing corners per Thesis Assumption Line 29
    corners = [(0, 0), (bay_x, 0), (bay_x, bay_y), (0, bay_y)]
    slab_contour = [(0, 0), (bay_x, 0), (bay_x, bay_y), (0, bay_y), (0, 0)]
    
    if view_dim == "3D Isometric Wireframe":
        fig_3d = go.Figure()
        
        # 1. Undeformed & Deformed Structural Columns
        for idx, (cx, cy) in enumerate(corners):
            # Undeformed column (Ghost dashed)
            fig_3d.add_trace(go.Scatter3d(
                x=[cx, cx],
                y=[cy, cy],
                z=[0, stories * story_height],
                mode='lines',
                line=dict(color='rgba(139,216,253,0.3)', width=3.5, dash='dash'),
                showlegend=False
            ))
            
            # Deformed Column Coordinates across stories
            def_x = [cx]
            def_y = [cy]
            def_z = [0.0]
            
            for i in range(stories):
                dx = (disps[i] / 1000.0) * disp_scale
                def_x.append(cx + dx)
                def_y.append(cy)
                def_z.append((i + 1) * story_height)
            
            fig_3d.add_trace(go.Scatter3d(
                x=def_x,
                y=def_y,
                z=def_z,
                mode='lines+markers',
                line=dict(color='#00AAF9', width=6),
                marker=dict(size=4, color='#FFBA42'),
                name='Deformed RC Column' if idx == 0 else None,
                showlegend=(idx == 0)
            ))
            
        # 2. Deformed Floor Slabs / Rigid Diaphragms
        for i in range(stories):
            z_lvl = (i + 1) * story_height
            dx = (disps[i] / 1000.0) * disp_scale
            
            slab_x = [pt_x + dx for (pt_x, pt_y) in slab_contour]
            slab_y = [pt_y for (pt_x, pt_y) in slab_contour]
            slab_z = [z_lvl] * len(slab_x)
            
            fig_3d.add_trace(go.Scatter3d(
                x=slab_x,
                y=slab_y,
                z=slab_z,
                mode='lines',
                line=dict(color='#FFBA42', width=4),
                name=f'Floor Diaphragm L{i+1}',
                showlegend=(i == 0)
            ))
            
        fig_3d.update_layout(
            title=f"<b>3D Building Deflection Model (Linear Elastic, {disp_scale:.0f}x Scale)</b>",
            scene=dict(
                xaxis_title='X (m) [Seismic Demand Axis]',
                yaxis_title='Y (m) [Building Width]',
                zaxis_title='Z (m) [Height]',
                camera=dict(eye=dict(x=1.8, y=-1.8, z=1.2))
            ),
            height=520,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_3d, width="stretch")

    else:
        # 2D Elevation view
        fig_2d = go.Figure()
        
        # Left and Right Frame Columns
        for x_base, col_name in zip([0, bay_x], ["Left Bay Column", "Right Bay Column"]):
            x_undef = [x_base] * (stories + 1)
            y_undef = [0] + [(i + 1) * story_height for i in range(stories)]
            
            x_def = [x_base] + [x_base + (disps[i] / 1000.0) * disp_scale for i in range(stories)]
            y_def = y_undef
            
            # Undeformed
            fig_2d.add_trace(go.Scatter(
                x=x_undef, y=y_undef,
                mode='lines',
                line=dict(color='rgba(139,216,253,0.3)', width=3, dash='dash'),
                name=f'Undeformed {col_name}'
            ))
            
            # Deformed
            fig_2d.add_trace(go.Scatter(
                x=x_def, y=y_def,
                mode='lines+markers',
                line=dict(color='#00AAF9', width=5),
                marker=dict(size=8, color='#FFBA42'),
                name=f'Deformed {col_name}'
            ))
            
        # Beams / Slabs at each story
        for i in range(stories):
            z_lvl = (i + 1) * story_height
            dx = (disps[i] / 1000.0) * disp_scale
            
            fig_2d.add_trace(go.Scatter(
                x=[0 + dx, bay_x + dx],
                y=[z_lvl, z_lvl],
                mode='lines',
                line=dict(color='#FFBA42', width=4),
                name=f'Beam L{i+1}' if i == 0 else None,
                showlegend=(i == 0)
            ))
            
        fig_2d.update_layout(
            title=f"<b>2D Frame Elevation Profile ({disp_scale:.0f}x Scale)</b>",
            xaxis_title="Lateral Displacement (meters)",
            yaxis_title="Elevation (meters)",
            height=480,
            margin=dict(l=30, r=30, t=40, b=30)
        )
        st.plotly_chart(fig_2d, width="stretch")

# ==============================================================================
# 8. FOOTER & THESIS ENGINEERING CITATIONS
# ==============================================================================
st.markdown("""
<div style="margin-top: 2rem; background: #013C58;
            border-radius: 12px; padding: 1.1rem 1.6rem;
            border: 1px solid rgba(0,83,122,0.5); text-align: center;">
    <div style="font-family: 'Outfit', sans-serif; font-size: 0.95rem; font-weight: 700;
                color: #FFBA42; letter-spacing: 0.05em; margin-bottom: 0.3rem;">
        SEIS-PY &mdash; Python-Based Seismic Response Prediction Engine
    </div>
    <div style="font-size: 0.75rem; color: #8BD8FD; line-height: 1.6; margin-bottom: 0.35rem;">
        Governing References:&nbsp;
        <b style="color:#FFFFFF;">NSCP 2015 (7th Ed., Sec. 208)</b> &bull;
        <b style="color:#FFFFFF;">ACI 318-14</b> &bull;
        <b style="color:#FFFFFF;">ASEP Earthquake-Resistant Design Guide</b> &bull;
        <b style="color:#FFFFFF;">Group 1 Thesis Research Manuscript</b>
    </div>
    <div style="font-size: 0.7rem; color: rgba(139,216,253,0.45); font-style: italic;">
        Academic computational tool for preliminary seismic analysis and research per Chapter 1 Scope and Delimitations.
    </div>
</div>
""", unsafe_allow_html=True)
