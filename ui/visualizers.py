"""
ui/visualizers.py - Plotly Interactive 3D & 2D Seismic Deflection Models, Spectra & Charts
"""
import math
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from config.nscp_tables import PLAN_SHAPES
from core.spectrum import generate_nscp_spectrum

def create_drift_profile_plot(story_elevations, drifts, drift_limit):
    """Generates Inter-Story Drift Ratio vs Height plot."""
    fig = go.Figure()
    y_elev = [0.0] + story_elevations
    x_drift = [0.0] + drifts
    
    fig.add_trace(go.Scatter(
        x=x_drift,
        y=y_elev,
        mode='lines+markers',
        name='Calculated Inelastic Drift (IDR)',
        line=dict(color='#0284c7', width=3.5),
        marker=dict(size=8, color='#0369a1', symbol='circle')
    ))
    
    fig.add_vline(
        x=drift_limit,
        line_dash="dash",
        line_color="#ef4444",
        line_width=2,
        annotation_text=f"NSCP Allowable Limit ({drift_limit:.1f}%)",
        annotation_position="top right"
    )
    
    fig.update_layout(
        title="<b>Inter-Story Drift Ratio (IDR %) vs Building Elevation</b>",
        xaxis_title="Inter-Story Drift Ratio (%)",
        yaxis_title="Elevation (meters)",
        template="plotly_white",
        hovermode="x unified",
        height=380,
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig

def create_displacement_profile_plot(story_elevations, disps):
    """Generates cumulative inelastic displacement profile."""
    fig = go.Figure()
    y_elev = [0.0] + story_elevations
    x_disp = [0.0] + disps
    
    fig.add_trace(go.Scatter(
        x=x_disp,
        y=y_elev,
        mode='lines+markers',
        name='Inelastic Deflection Δm',
        line=dict(color='#10b981', width=3.5),
        marker=dict(size=8, color='#047857', symbol='diamond'),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.1)'
    ))
    
    fig.update_layout(
        title="<b>Inelastic Lateral Deflection Profile Δm (mm)</b>",
        xaxis_title="Lateral Displacement (mm)",
        yaxis_title="Elevation (meters)",
        template="plotly_white",
        hovermode="x unified",
        height=380,
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig

def create_spectrum_plot(Ca, Cv, T1):
    """Generates NSCP 2015 Design Response Spectrum plot."""
    T_vals, Sa_vals, To, Ts = generate_nscp_spectrum(Ca, Cv, max_T=3.0)
    Sa_T1 = float(np.interp(T1, T_vals, Sa_vals))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=T_vals,
        y=Sa_vals,
        mode='lines',
        name='NSCP 2015 Design Spectrum Sa(T)',
        line=dict(color='#2563eb', width=3),
        fill='tozeroy',
        fillcolor='rgba(37, 99, 235, 0.08)'
    ))
    
    fig.add_trace(go.Scatter(
        x=[T1],
        y=[Sa_T1],
        mode='markers',
        name=f'Building T₁ = {T1:.3f}s (Sa = {Sa_T1:.3f}g)',
        marker=dict(size=13, color='#dc2626', symbol='cross', line=dict(width=2, color='white'))
    ))
    
    fig.add_vline(x=T1, line_dash="dot", line_color="#dc2626", line_width=1.5)
    fig.add_vline(x=To, line_dash="dash", line_color="#94a3b8", annotation_text=f"To = {To:.2f}s")
    fig.add_vline(x=Ts, line_dash="dash", line_color="#94a3b8", annotation_text=f"Ts = {Ts:.2f}s")
    
    fig.update_layout(
        title="<b>Design Response Spectrum Sa(T) vs Fundamental Period</b>",
        xaxis_title="Period T (seconds)",
        yaxis_title="Spectral Acceleration Sa (g)",
        template="plotly_white",
        height=400,
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig, To, Ts, Sa_T1

def create_3d_wireframe_plot(plan_shape, plan_area, stories, story_height, disps, disp_scale):
    """Generates real 3D deformed building wireframe with torsional rotation."""
    bay_x = math.sqrt(plan_area) * 0.85
    bay_y = plan_area / max(bay_x, 1.0)
    center_x = bay_x / 2.0
    center_y = bay_y / 2.0
    
    if plan_shape == "L_SHAPE":
        corners = [
            (0, 0),
            (bay_x, 0),
            (bay_x, bay_y * 0.45),
            (bay_x * 0.45, bay_y * 0.45),
            (bay_x * 0.45, bay_y),
            (0, bay_y)
        ]
        slab_contour = corners + [corners[0]]
        torsion_angle_base = 0.045
    elif plan_shape == "T_SHAPE":
        corners = [
            (bay_x * 0.25, 0),
            (bay_x * 0.75, 0),
            (bay_x * 0.75, bay_y * 0.45),
            (bay_x, bay_y * 0.45),
            (bay_x, bay_y),
            (0, bay_y),
            (0, bay_y * 0.45),
            (bay_x * 0.25, bay_y * 0.45)
        ]
        slab_contour = corners + [corners[0]]
        torsion_angle_base = 0.035
    else: # REGULAR or SOFT_STORY
        corners = [(0, 0), (bay_x, 0), (bay_x, bay_y), (0, bay_y)]
        slab_contour = [(0, 0), (bay_x, 0), (bay_x, bay_y), (0, bay_y), (0, 0)]
        torsion_angle_base = 0.01 if plan_shape == "SOFT_STORY" else 0.0

    fig_3d = go.Figure()
    
    # Columns
    for idx, (cx, cy) in enumerate(corners):
        fig_3d.add_trace(go.Scatter3d(
            x=[cx, cx],
            y=[cy, cy],
            z=[0, stories * story_height],
            mode='lines',
            line=dict(color='#cbd5e1', width=3.5, dash='dash'),
            showlegend=False
        ))
        
        def_x = [cx]
        def_y = [cy]
        def_z = [0]
        
        for i in range(stories):
            dx = (disps[i] / 1000.0) * disp_scale
            theta = torsion_angle_base * (disps[i] / max(disps[-1], 1e-4)) * (disp_scale / 25.0)
            
            rel_x = cx - center_x
            rel_y = cy - center_y
            rot_x = center_x + rel_x * math.cos(theta) - rel_y * math.sin(theta) + dx
            rot_y = center_y + rel_x * math.sin(theta) + rel_y * math.cos(theta)
            
            def_x.append(rot_x)
            def_y.append(rot_y)
            def_z.append((i + 1) * story_height)
        
        is_soft_ground = (plan_shape == "SOFT_STORY" and idx in [0, 1])
        col_color = '#f97316' if is_soft_ground else '#0284c7'
        
        fig_3d.add_trace(go.Scatter3d(
            x=def_x,
            y=def_y,
            z=def_z,
            mode='lines+markers',
            line=dict(color=col_color, width=6),
            marker=dict(size=4, color='#0f172a'),
            name='Open Carport Column' if is_soft_ground else ('Deformed RC Column' if idx == 0 else None),
            showlegend=(idx == 0 or is_soft_ground)
        ))
        
    # Floor Slabs
    for i in range(stories):
        z_lvl = (i + 1) * story_height
        dx = (disps[i] / 1000.0) * disp_scale
        theta = torsion_angle_base * (disps[i] / max(disps[-1], 1e-4)) * (disp_scale / 25.0)
        
        slab_x = []
        slab_y = []
        for (px, py) in slab_contour:
            rel_x = px - center_x
            rel_y = py - center_y
            rot_x = center_x + rel_x * math.cos(theta) - rel_y * math.sin(theta) + dx
            rot_y = center_y + rel_x * math.sin(theta) + rel_y * math.cos(theta)
            slab_x.append(rot_x)
            slab_y.append(rot_y)
            
        slab_z = [z_lvl] * len(slab_x)
        
        fig_3d.add_trace(go.Scatter3d(
            x=slab_x,
            y=slab_y,
            z=slab_z,
            mode='lines',
            line=dict(color='#0f766e', width=5),
            name=f'Floor Diaphragm L{i+1}',
            showlegend=(i == 0)
        ))
        
    fig_3d.update_layout(
        title=f"<b>3D Building Deflection & Torsion Model: {PLAN_SHAPES[plan_shape]['name']} ({disp_scale:.0f}x Scale)</b>",
        scene=dict(
            xaxis_title='X (m) [Seismic Demand Axis]',
            yaxis_title='Y (m) [Building Width]',
            zaxis_title='Z (m) [Height]',
            camera=dict(eye=dict(x=1.8, y=-1.8, z=1.2))
        ),
        template="plotly_white",
        height=520,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig_3d

def create_damage_gauge_plot(damage_index, color_code):
    """Generates Park-Ang damage index gauge."""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = damage_index,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "<b>Park-Ang Damage Index (DI)</b>", 'font': {'size': 16}},
        gauge = {
            'axis': {'range': [0, 1.0], 'tickwidth': 1, 'tickcolor': "#334155"},
            'bar': {'color': color_code},
            'steps': [
                {'range': [0, 0.10], 'color': "rgba(16, 185, 129, 0.25)"},
                {'range': [0.10, 0.25], 'color': "rgba(2, 132, 199, 0.25)"},
                {'range': [0.25, 0.40], 'color': "rgba(234, 179, 8, 0.25)"},
                {'range': [0.40, 0.80], 'color': "rgba(249, 115, 22, 0.25)"},
                {'range': [0.80, 1.0], 'color': "rgba(239, 68, 68, 0.25)"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0.80
            }
        }
    ))
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=20))
    return fig
