"""
ui/styles.py - SEIS-PY Visual Design System & CSS Styling
Dark Engineering Dashboard Theme (Vercel / Linear inspired)
Palette: #0B1E33 | #013C58 | #00537A | #00AAF9 | #F5A201 | #FFBA42
"""
import streamlit as st

def apply_custom_css():
    """Applies SEIS-PY dark engineering dashboard CSS theme."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&family=Outfit:wght@300;400;500;600;700;800&display=swap');

        /* ============================================================
           DESIGN TOKENS — Exact Palette
           ============================================================ */
        :root {
            --bg-base:       #0B1E33;
            --bg-card:       #013C58;
            --bg-elevated:   #01476a;
            --accent-blue:   #00537A;
            --accent-bright: #00AAF9;
            --accent-amber:  #F5A201;
            --accent-gold:   #FFBA42;
            --text-primary:  #FFFFFF;
            --text-muted:    #8BD8FD;
            --text-dim:      rgba(139,216,253,0.45);
            --border:        rgba(0,170,249,0.12);
            --border-accent: rgba(0,83,122,0.5);
            --success:       #10b981;
            --success-bg:    rgba(16,185,129,0.1);
            --danger:        #ef4444;
            --danger-bg:     rgba(239,68,68,0.1);
            --radius:        12px;
            --radius-sm:     8px;
            --radius-xs:     6px;
            --transition:    all 0.25s cubic-bezier(.25,.8,.25,1);
        }

        /* ============================================================
           GLOBAL TYPOGRAPHY & BACKGROUND
           ============================================================ */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        }

        .main .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }

        /* Text colors for main area */
        .main .block-container p,
        .main .block-container li,
        .main .block-container span,
        .main .block-container td,
        .main .block-container th {
            color: var(--text-primary);
        }
        .main .block-container strong,
        .main .block-container b {
            color: var(--text-primary);
        }

        /* Headings */
        .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
            font-family: 'Outfit', sans-serif !important;
            color: var(--text-primary) !important;
            letter-spacing: -0.02em;
        }
        .main h4 {
            color: var(--accent-gold) !important;
        }

        /* Code font */
        .code-font, code {
            font-family: 'JetBrains Mono', monospace;
            color: var(--accent-bright);
        }

        /* HR */
        .main hr {
            border-color: var(--border) !important;
        }

        /* ============================================================
           HERO HEADER
           ============================================================ */
        .seispy-header {
            background: linear-gradient(135deg, #0B1E33 0%, #013C58 55%, #00537A 100%);
            color: white;
            padding: 1.4rem 1.8rem;
            border-radius: var(--radius);
            margin-bottom: 1rem;
            border: 1px solid var(--border);
            position: relative;
            overflow: hidden;
        }
        .seispy-header::before {
            content: '';
            position: absolute;
            top: -50px; right: -50px;
            width: 220px; height: 220px;
            background: radial-gradient(circle, rgba(245,162,1,0.1) 0%, transparent 70%);
            pointer-events: none;
        }
        .seispy-header::after {
            content: '';
            position: absolute;
            bottom: -40px; left: 25%;
            width: 300px; height: 150px;
            background: radial-gradient(ellipse, rgba(0,170,249,0.06) 0%, transparent 70%);
            pointer-events: none;
        }
        .seispy-logo-row {
            display: flex; align-items: center; gap: 1rem; margin-bottom: 0.4rem;
        }
        .seispy-badge {
            background: linear-gradient(135deg, var(--accent-amber), var(--accent-gold));
            color: var(--bg-base);
            font-family: 'Outfit', sans-serif;
            font-size: 1.5rem; font-weight: 800; letter-spacing: 0.03em;
            padding: 0.2rem 0.8rem; border-radius: var(--radius-sm);
            box-shadow: 0 2px 16px rgba(245,162,1,0.25);
        }
        .seispy-version {
            background: rgba(0,170,249,0.12);
            border: 1px solid rgba(0,170,249,0.2);
            color: var(--text-muted);
            font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em;
            padding: 0.15rem 0.6rem; border-radius: 20px; text-transform: uppercase;
        }
        .seispy-title-text {
            font-family: 'Outfit', sans-serif; font-size: 1rem; font-weight: 600;
            color: var(--text-primary); letter-spacing: 0.005em;
        }
        .seispy-subtitle {
            font-size: 0.8rem; color: var(--text-muted); font-weight: 400;
            margin-top: 0.1rem;
        }
        .seispy-divider-line {
            height: 1px;
            background: linear-gradient(90deg, var(--accent-amber) 0%, rgba(0,170,249,0.15) 50%, transparent 100%);
            margin: 0.7rem 0 0.55rem 0; border: none;
        }

        /* ============================================================
           METRIC CARDS — #013C58 bg, #00537A border accent
           ============================================================ */
        .metric-card {
            background: var(--bg-card);
            border: 1px solid var(--border-accent);
            border-radius: var(--radius);
            padding: 0.9rem 1.1rem;
            transition: var(--transition);
            position: relative;
            overflow: hidden;
        }
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 2.5px;
            background: linear-gradient(90deg, var(--accent-bright) 0%, var(--accent-blue) 100%);
            transition: background 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-3px);
            border-color: var(--accent-bright);
            box-shadow: 0 8px 30px rgba(0,170,249,0.12);
        }
        .metric-card:hover::before {
            background: linear-gradient(90deg, var(--accent-amber) 0%, var(--accent-gold) 100%);
        }
        .metric-label {
            font-size: 0.65rem; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.09em;
            color: var(--text-muted); margin-bottom: 0.25rem;
        }
        .metric-value {
            font-family: 'Outfit', sans-serif;
            font-size: 1.5rem; font-weight: 800; color: var(--text-primary); line-height: 1.1;
        }
        .metric-unit {
            font-size: 0.75rem; font-weight: 600; color: var(--text-muted); margin-left: 0.15rem;
        }
        .metric-sub {
            font-size: 0.68rem; margin-top: 0.25rem; font-weight: 600; color: var(--accent-bright);
        }

        /* ============================================================
           COMPLIANCE BANNERS — Dark with colored accent borders
           ============================================================ */
        .compliance-pass {
            background: var(--success-bg);
            border: 1px solid rgba(16,185,129,0.3);
            border-left: 4px solid var(--success);
            color: var(--text-primary);
            padding: 0.8rem 1.3rem; border-radius: var(--radius);
            font-weight: 600; display: flex; align-items: center; gap: 0.6rem;
        }
        .compliance-fail {
            background: var(--danger-bg);
            border: 1px solid rgba(239,68,68,0.3);
            border-left: 4px solid var(--danger);
            color: var(--text-primary);
            padding: 0.8rem 1.3rem; border-radius: var(--radius);
            font-weight: 600; display: flex; align-items: center; gap: 0.6rem;
        }

        /* ============================================================
           STAT BOX
           ============================================================ */
        .stat-box {
            background: var(--bg-card);
            border: 1px solid var(--border-accent);
            border-radius: var(--radius);
            padding: 0.85rem 1.2rem; display: flex; align-items: center;
            justify-content: space-between;
        }
        .stat-box-label {
            font-size: 0.65rem; text-transform: uppercase; font-weight: 700;
            letter-spacing: 0.09em; color: var(--text-muted);
        }
        .stat-box-value {
            font-family: 'Outfit', sans-serif; font-size: 1.1rem; font-weight: 800;
        }

        /* ============================================================
           SECTION HEADERS
           ============================================================ */
        .section-title {
            font-family: 'Outfit', sans-serif;
            font-size: 1.1rem; font-weight: 700; color: var(--text-primary);
            margin-top: 0.8rem; margin-bottom: 0.6rem;
            display: flex; align-items: center; gap: 0.4rem;
        }

        /* ============================================================
           SIDEBAR — Deep navy gradient & Compact top spacing
           ============================================================ */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0B1E33 0%, #012e47 100%) !important;
            border-right: 1px solid rgba(0,170,249,0.08) !important;
        }
        [data-testid="stSidebar"] .block-container,
        section[data-testid="stSidebar"] .block-container,
        [data-testid="stSidebarUserContent"],
        [data-testid="stSidebarContent"] {
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
        }
        [data-testid="stSidebarHeader"] {
            padding-top: 0.4rem !important;
            padding-bottom: 0rem !important;
            min-height: auto !important;
        }
        [data-testid="stSidebar"] h3:first-child,
        [data-testid="stSidebar"] h3:first-of-type,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3:first-child {
            margin-top: 0.1rem !important;
            padding-top: 0 !important;
        }
        [data-testid="stSidebar"] * {
            color: var(--text-primary) !important;
        }
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4 {
            color: var(--accent-gold) !important;
            font-family: 'Outfit', sans-serif !important;
        }
        [data-testid="stSidebar"] hr {
            border-color: rgba(0,170,249,0.1) !important;
        }

        /* Sidebar widget inputs */
        [data-testid="stSidebar"] [data-baseweb="select"] > div,
        [data-testid="stSidebar"] [data-baseweb="input"] > div,
        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] textarea {
            background-color: rgba(0,170,249,0.06) !important;
            border-color: rgba(0,170,249,0.15) !important;
            color: var(--text-primary) !important;
        }

        /* Dropdown menus */
        [data-baseweb="popover"] [role="option"],
        [data-baseweb="menu"] li {
            background-color: #012e47 !important;
            color: var(--text-primary) !important;
        }
        [data-baseweb="popover"] [role="option"]:hover,
        [data-baseweb="menu"] li:hover {
            background-color: var(--accent-blue) !important;
        }

        /* Slider thumb */
        [data-testid="stSidebar"] [data-testid="stSlider"] div[role="slider"] {
            background-color: var(--accent-amber) !important;
        }

        /* Expanders */
        [data-testid="stSidebar"] [data-testid="stExpander"] {
            background: rgba(0,170,249,0.03) !important;
            border: 1px solid rgba(0,170,249,0.1) !important;
            border-radius: var(--radius-sm) !important;
        }

        /* ============================================================
           BUTTONS — Amber/Gold gradient
           ============================================================ */
        .stDownloadButton > button,
        .stButton > button {
            background: linear-gradient(135deg, var(--accent-amber) 0%, var(--accent-gold) 100%) !important;
            color: var(--bg-base) !important;
            font-weight: 700 !important;
            border: none !important;
            border-radius: var(--radius-sm) !important;
            padding: 0.5rem 1.4rem !important;
            transition: var(--transition) !important;
            box-shadow: 0 2px 12px rgba(245,162,1,0.15) !important;
            letter-spacing: 0.01em !important;
        }
        .stDownloadButton > button:hover,
        .stButton > button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 24px rgba(245,162,1,0.3) !important;
        }

        /* ============================================================
           ALERTS — Dark styled
           ============================================================ */
        [data-testid="stAlert"] {
            background-color: var(--bg-card) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-sm) !important;
            color: var(--text-primary) !important;
        }

        /* ============================================================
           DATA TABLES
           ============================================================ */
        [data-testid="stDataFrame"] {
            border-radius: var(--radius) !important;
            overflow: hidden;
        }

        /* ============================================================
           ANIMATIONS
           ============================================================ */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .metric-card,
        .compliance-pass,
        .compliance-fail,
        .stat-box,
        .seispy-header {
            animation: fadeInUp 0.35s ease-out;
        }

        /* ============================================================
           SCROLLBAR — Minimal dark
           ============================================================ */
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb {
            background: rgba(0,170,249,0.15);
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover { background: rgba(0,170,249,0.3); }

        /* ============================================================
           CUSTOM INFO CARDS (used in tabs)
           ============================================================ */
        .dark-card {
            background: var(--bg-card);
            border: 1px solid var(--border-accent);
            border-radius: var(--radius);
            padding: 1.2rem;
        }
        .dark-card-title {
            font-size: 0.68rem; font-weight: 700;
            text-transform: uppercase; letter-spacing: 0.09em;
            color: var(--text-muted); margin-bottom: 0.3rem;
        }
        .dark-card-value {
            font-family: 'Outfit', sans-serif;
            font-size: 1.3rem; font-weight: 800;
            margin-top: 0.2rem;
        }
        .dark-card p {
            font-size: 0.85rem; color: var(--text-muted);
            line-height: 1.55; margin: 0;
        }
        .dark-card hr {
            border: none; border-top: 1px solid rgba(0,170,249,0.1);
            margin: 0.7rem 0;
        }

    </style>
    """, unsafe_allow_html=True)
