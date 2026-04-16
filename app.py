"""
CareerPath AI — Final Production App
Matches IT_Career_Planner_UI_v2.html design exactly
Student: Hein Htet Phyo | 25036746 | UFCEKP-30-3 | UWE Bristol
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import html
import os
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, f1_score
from xgboost import XGBClassifier

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CareerPath AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Helper: render HTML safely ─────────────────────────────────────────────
DEFAULT_SESSION_STATE = {
    'ran': False,
    'show_deep': False,
    'sel_role': None,
    'profile': None,
    'scroll_target': None,
    'scroll_token': 0,
}


def H(content: str) -> None:
    """Render trusted HTML into the Streamlit page."""
    st.markdown(content, unsafe_allow_html=True)


def initialize_session_state() -> None:
    """Populate the Streamlit session with the keys this app expects."""
    for key, default_value in DEFAULT_SESSION_STATE.items():
        st.session_state.setdefault(key, default_value)


def read_query_param(name: str):
    """Return a single query param value, normalizing Streamlit's list/string shape."""
    value = st.query_params.get(name)
    if isinstance(value, list):
        return value[0] if value else None
    return value


def queue_scroll(target: str) -> None:
    """Store a pending smooth-scroll target for the next rerender."""
    st.session_state['scroll_target'] = target
    st.session_state['scroll_token'] = st.session_state.get('scroll_token', 0) + 1


def select_role(role: str, scroll_target: str = 'deep-dive-header') -> None:
    """Update the selected role and open the deep-dive section."""
    st.session_state['sel_role'] = role
    st.session_state['show_deep'] = True
    queue_scroll(scroll_target)

def scroll_to_anchor(anchor_id, token=0):
    components.html(f"""
<script>
const scrollToken = {token};
const jumpToAnchor = () => {{
  const el =
    (window.parent && window.parent.document
      ? window.parent.document.getElementById('{anchor_id}')
      : null) ||
    document.getElementById('{anchor_id}');
  if (el) {{
    el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
  }}
}};
setTimeout(jumpToAnchor, 80);
setTimeout(jumpToAnchor, 240);
setTimeout(jumpToAnchor, 500);
setTimeout(jumpToAnchor, 800);
</script>
""", height=0)

def style_form_panels():
    components.html("""
<script>
const applyPanelStyles = () => {
  const doc = window.parent.document;
  const panelSpecs = [
    { marker: '.skills-panel-marker', topBorder: 'linear-gradient(135deg,#38bdf8,#14b8a6)' },
    { marker: '.interest-panel-marker', topBorder: 'linear-gradient(135deg,#0ea5e9,#14b8a6)' },
    { marker: '.prefs-panel-marker', topBorder: 'linear-gradient(135deg,#fb7185,#f59e0b)' },
  ];

  panelSpecs.forEach(({ marker, topBorder }) => {
    doc.querySelectorAll(marker).forEach((el) => {
      const wrapper =
        el.closest('[data-testid="stVerticalBlockBorderWrapper"]') ||
        el.closest('[data-testid="stVerticalBlock"]');
      if (!wrapper) return;

      wrapper.style.background = 'rgba(255,255,255,0.88)';
      wrapper.style.backdropFilter = 'blur(18px)';
      wrapper.style.webkitBackdropFilter = 'blur(18px)';
      wrapper.style.border = '1px solid rgba(15,23,42,0.08)';
      wrapper.style.borderRadius = '14px';
      wrapper.style.boxShadow = '0 16px 44px rgba(148,163,184,0.14)';
      wrapper.style.padding = '26px';
      wrapper.style.marginBottom = marker === '.interest-panel-marker' ? '0px' : '18px';
      wrapper.style.marginTop = marker === '.prefs-panel-marker' ? '0px' : '0px';
      wrapper.style.width = '100%';
      wrapper.style.boxSizing = 'border-box';
      wrapper.style.alignSelf = 'stretch';
      wrapper.style.position = 'relative';
      wrapper.style.overflow = 'hidden';
      wrapper.style.minHeight = marker === '.skills-panel-marker' ? '1062px' : 'auto';

      if (!wrapper.querySelector('.panel-top-bar')) {
        const topBar = doc.createElement('div');
        topBar.className = 'panel-top-bar';
        topBar.style.position = 'absolute';
        topBar.style.top = '0';
        topBar.style.left = '0';
        topBar.style.right = '0';
        topBar.style.height = '2px';
        topBar.style.background = topBorder;
        wrapper.prepend(topBar);
      }

      const parentBlock = wrapper.parentElement;
      if (parentBlock && marker === '.interest-panel-marker') {
        parentBlock.style.gap = '0px';
        parentBlock.style.rowGap = '0px';
        parentBlock.style.alignItems = 'stretch';
      }
    });
  });
};

setTimeout(applyPanelStyles, 60);
setTimeout(applyPanelStyles, 240);
setTimeout(applyPanelStyles, 600);
</script>
""", height=0)

def render_top3_card(role, rank_label, readiness, readiness_color, gradient, is_selected):
    border = 'rgba(14,165,233,0.38)' if is_selected else 'rgba(15,23,42,0.08)'
    shadow = '0 18px 48px rgba(14,165,233,0.18)' if is_selected else '0 12px 36px rgba(148,163,184,0.14)'
    html_card = f"""
    <html>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
      </head>
      <body style="margin:0;background:transparent;">
        <div style="
          background:rgba(255,255,255,0.88);
          border:1.5px solid {border};
          box-shadow:{shadow};
          border-radius:18px;
          padding:20px 20px 22px;
          min-height:268px;
          display:flex;
          flex-direction:column;
          justify-content:space-between;
          overflow:hidden;
          position:relative;
          box-sizing:border-box;">
          <div style="position:absolute;top:-32px;right:-28px;width:120px;height:120px;border-radius:50%;
            background:radial-gradient(circle, rgba(56,189,248,0.18), transparent 70%);"></div>
          <div style="position:relative;display:flex;flex-direction:column;flex:1;">
            <div style="font-size:34px;margin-bottom:10px;">{ROLE_EMOJI[role]}</div>
            <div style="min-height:22px;display:flex;align-items:center;gap:8px;margin-bottom:10px;color:#5b7a90;
              font-family:'DM Mono',monospace;font-size:11px;letter-spacing:0.4px;">{rank_label}</div>
            <div style="font-family:'Syne',sans-serif;font-size:19px;font-weight:800;letter-spacing:-0.3px;
              margin-bottom:10px;color:#0f172a;min-height:68px;line-height:1.15;display:flex;align-items:flex-start;">
              {role}
            </div>
            <div style="margin-top:auto;min-height:56px;">
              <div style="display:flex;justify-content:space-between;font-size:11px;color:#527184;margin-bottom:6px;font-family:'DM Sans',sans-serif;">
                <span>Readiness</span>
                <span style="font-family:'DM Mono',monospace;font-size:14px;font-weight:700;color:{readiness_color};">{readiness}%</span>
              </div>
              <div style="height:8px;background:#dbeef4;border-radius:999px;overflow:hidden;">
                <div style="width:{readiness}%;height:100%;background:{gradient};border-radius:999px;"></div>
              </div>
            </div>
          </div>
        </div>
      </body>
    </html>
    """
    components.html(html_card, height=318)

# ─────────────────────────────────────────────────────────────────────────────
# MASTER CSS — modern light theme
# ─────────────────────────────────────────────────────────────────────────────
H("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
  --bg:     #f4fbff;
  --bg2:    #e8f6fb;
  --bg3:    #d9eef5;
  --card:   rgba(255, 255, 255, 0.82);
  --border: rgba(15, 23, 42, 0.08);
  --border2:rgba(14, 116, 144, 0.18);
  --text:   #0f172a;
  --muted:  #527184;
  --v1: #38bdf8;
  --v2: #8b5cf6;
  --v3: #2dd4bf;
  --v4: #fb7185;
  --v5: #f59e0b;
  --v6: #22c55e;
  --v7: #60a5fa;
  --g1: linear-gradient(135deg,#38bdf8,#14b8a6);
  --g2: linear-gradient(135deg,#2dd4bf,#60a5fa);
  --g3: linear-gradient(135deg,#fb7185,#f59e0b);
  --g4: linear-gradient(135deg,#22c55e,#2dd4bf);
  --g5: linear-gradient(135deg,#60a5fa,#38bdf8);
  --r: 14px;
}

/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"], .stApp {
  font-family: 'DM Sans', sans-serif !important;
  background:
    radial-gradient(circle at top left, rgba(56,189,248,0.16), transparent 34%),
    radial-gradient(circle at top right, rgba(45,212,191,0.12), transparent 30%),
    linear-gradient(135deg, #f8fdff 0%, #eef8fb 48%, #e4f3f8 100%) !important;
  color: var(--text) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer,
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stSidebar"] { display: none !important; }

/* ── Remove padding ── */
[data-testid="stAppViewContainer"] {
  padding-top: 0 !important;
  margin-top: 0 !important;
}
.main .block-container {
  padding: 0 !important;
  max-width: 100% !important;
  margin-top: 0 !important;
}
section.main > div { padding: 0 !important; }

/* ── Animated mesh background ── */
body::before {
  content: '';
  position: fixed; inset: 0;
  pointer-events: none; z-index: 0;
  background:
    radial-gradient(ellipse 780px 760px at -10% -10%, rgba(56,189,248,0.22) 0%, transparent 60%),
    radial-gradient(ellipse 560px 520px at 110% 105%, rgba(20,184,166,0.18) 0%, transparent 60%),
    radial-gradient(ellipse 420px 420px at 50% 45%, rgba(251,113,133,0.10) 0%, transparent 60%);
  animation: meshDrift 14s ease-in-out infinite alternate;
}
@keyframes meshDrift {
  0%   { transform: translate(0,0) scale(1); }
  100% { transform: translate(30px,20px) scale(1.04); }
}

/* ── Grid dots ── */
body::after {
  content: '';
  position: fixed; inset: 0;
  background-image: radial-gradient(rgba(15,23,42,0.05) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none; z-index: 0;
}

/* ── All content above bg ── */
.stApp > * { position: relative; z-index: 1; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-thumb {
  background: linear-gradient(var(--v1), var(--v2));
  border-radius: 10px;
}

/* ── Sliders ── */
[data-testid="stSlider"] {
  padding: 0 !important;
}
[data-testid="stSlider"] label {
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.84rem !important;
  font-weight: 500 !important;
  color: var(--muted) !important;
  margin-bottom: 2px !important;
}
[data-testid="stSlider"] > div > div > div {
  background: rgba(255,255,255,0.92) !important;
  border-radius: 999px !important;
}
[data-testid="stSlider"] > div > div > div > div[data-testid="stSlider-track-fill"] {
  background: linear-gradient(90deg, var(--v1), var(--v2)) !important;
}
[data-testid="stSlider"] > div > div > div[role="slider"] {
  background: var(--v1) !important;
  border: 2px solid white !important;
  box-shadow: 0 0 12px rgba(56,189,248,0.35) !important;
  width: 18px !important;
  height: 18px !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] label {
  font-family: 'DM Mono', monospace !important;
  font-size: 0.68rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.8px !important;
  color: var(--muted) !important;
}
[data-testid="stSelectbox"] > div > div {
  background: rgba(255,255,255,0.92) !important;
  border: 1.5px solid var(--border2) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stSelectbox"] > div > div:focus-within {
  border-color: var(--v1) !important;
}
[data-testid="stSelectbox"] svg {
  fill: #5b7a90 !important;
  color: #5b7a90 !important;
  opacity: 1 !important;
  width: 20px !important;
  height: 20px !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  padding-right: 40px !important;
}

/* ── Button ── */
.stButton > button {
  font-family: 'Syne', sans-serif !important;
  font-weight: 700 !important;
  font-size: 1rem !important;
  border: none !important;
  border-radius: 999px !important;
  padding: 14px 28px !important;
  background: linear-gradient(135deg, #38bdf8, #2dd4bf) !important;
  color: white !important;
  box-shadow: 0 12px 30px rgba(56,189,248,0.24) !important;
  width: 100% !important;
  cursor: pointer !important;
  transition: all 0.25s ease !important;
  letter-spacing: -0.2px !important;
}
.stButton > button span,
.stButton > button p,
.stButton > button div {
  font-family: 'Syne', sans-serif !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 12px 34px rgba(20,184,166,0.28) !important;
}
.stButton > button:active {
  transform: scale(0.98) !important;
}

/* ── Tab bar ── */
.stTabs [data-baseweb="tab-list"] {
  background: rgba(255,255,255,0.72) !important;
  border-radius: 999px !important;
  padding: 4px !important;
  gap: 2px !important;
  border: 1px solid var(--border) !important;
  width: fit-content !important;
}
.stTabs [data-baseweb="tab"] {
  font-family: 'Syne', sans-serif !important;
  font-size: 0.87rem !important;
  font-weight: 600 !important;
  color: var(--muted) !important;
  background: transparent !important;
  border-radius: 999px !important;
  padding: 8px 22px !important;
  border: none !important;
  transition: all 0.2s !important;
}
.stTabs [data-baseweb="tab"] *,
.stTabs [data-baseweb="tab"] span,
.stTabs [data-baseweb="tab"] div,
.stTabs [data-baseweb="tab"] p {
  font-family: 'Syne', sans-serif !important;
}
[aria-selected="true"][data-baseweb="tab"] {
  background: linear-gradient(135deg, #0ea5e9, #14b8a6) !important;
  color: white !important;
}
[data-baseweb="tab-highlight"] {
  display: none !important;
}
[data-baseweb="tab-border"] {
  display: none !important;
}
[data-testid="stTabsContent"] { padding: 0 !important; }

/* ── Pyplot ── */
[data-testid="stImage"] img { border-radius: 12px; }

/* ── Column gap ── */
[data-testid="stHorizontalBlock"] { gap: 18px !important; align-items: start !important; }
[data-testid="column"] > div { height: 100%; }
.top3-col {
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 392px;
  background: rgba(255,255,255,0.88);
  border-radius: 18px;
  padding: 22px;
  border: 1.5px solid rgba(15,23,42,0.08);
  box-shadow: 0 12px 36px rgba(148,163,184,0.14);
  overflow: hidden;
}
.top3-card {
  background: transparent;
  border-radius: 0;
  padding: 0;
  position: relative;
  overflow: visible;
  min-height: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  flex: 1;
  box-shadow: none !important;
  border: none !important;
}
.top3-title {
  font-family: 'Syne', sans-serif;
  font-size: 19px;
  font-weight: 800;
  letter-spacing: -0.3px;
  margin-bottom: 12px;
  color: #0f172a;
  min-height: 92px;
  line-height: 1.25;
  display: flex;
  align-items: flex-start;
}
.top3-metrics {
  min-height: 72px;
}
.top3-rank {
  min-height: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: #5b7a90;
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.4px;
}
.top3-button {
  margin-top: auto;
  min-height: 54px;
  padding-top: 18px;
}
.top3-link-button {
  width: 100%;
  height: 52px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 52px !important;
  min-height: 52px;
  padding: 0 20px;
  font-family: 'Syne', sans-serif;
  font-size: 0.95rem;
  font-weight: 700;
  line-height: 1;
  color: #ffffff !important;
  text-decoration: none !important;
  border-radius: 999px;
  background: linear-gradient(135deg, #38bdf8, #2dd4bf);
  box-shadow: 0 10px 28px rgba(14,165,233,0.24);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.top3-link-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 34px rgba(20,184,166,0.28);
}
.top3-real-button {
  margin-top: -22px;
  padding: 0 14px 14px;
  position: relative;
  z-index: 5;
}
.top3-real-button .stButton > button {
  height: 52px !important;
  min-height: 52px !important;
  border-radius: 999px !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 700 !important;
}
.top3-real-button .stButton > button *,
.top3-real-button .stButton > button span,
.top3-real-button .stButton > button p,
.top3-real-button .stButton > button div {
  font-family: 'Syne', sans-serif !important;
  font-weight: 700 !important;
}
.jump-anchor {
  scroll-margin-top: 110px;
}
.site-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  width: 100%;
  z-index: 1000;
  padding: 10px 40px 12px;
  min-height: 78px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: nowrap;
  background: rgba(248,253,255,0.94);
  border-bottom: 1px solid rgba(14,165,233,0.10);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  box-shadow: 0 6px 18px rgba(15,23,42,0.05);
}
.site-header-brand {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
  flex: 0 1 auto;
}
.site-header-title {
  font-family: 'Syne', sans-serif;
  font-size: 30px;
  font-weight: 800;
  letter-spacing: -1.2px;
  color: #0f172a;
  line-height: 1;
  white-space: nowrap;
}
.site-header-badges {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: nowrap;
  min-width: 0;
  flex: 1 1 auto;
}
.site-header-badge {
  padding: 9px 18px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  font-family: 'DM Mono', monospace;
  letter-spacing: 0.35px;
  white-space: nowrap;
}
.site-header-badge.purple {
  background: rgba(14,165,233,0.10);
  color: #0284c7;
  border: 1px solid rgba(14,165,233,0.18);
}
.site-header-badge.cyan {
  background: rgba(245,158,11,0.12);
  color: #b45309;
  border: 1px solid rgba(245,158,11,0.20);
}
.site-header-badge.green {
  background: rgba(34,197,94,0.10);
  color: #15803d;
  border: 1px solid rgba(34,197,94,0.18);
}

/* ── Card component ── */
.cp-card {
  background: var(--card);
  backdrop-filter: blur(18px);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 26px;
  position: relative;
  overflow: hidden;
  margin-bottom: 18px;
  box-shadow: 0 16px 44px rgba(148, 163, 184, 0.14);
}
.cp-card-bar {
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: var(--g1);
}
.skills-panel-marker { display: none; }
.interest-panel-marker { display: none; }
.prefs-panel-marker { display: none; }
.skills-panel-header {
  margin-bottom: 18px;
}
.skills-panel-title {
  font-family: 'Syne', sans-serif;
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.2px;
  color: #0f172a;
  margin-bottom: 6px;
}
.skills-panel-subtitle {
  font-size: 13px;
  color: #527184;
  line-height: 1.5;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.skills-panel-marker),
div[data-testid="stVerticalBlockBorderWrapper"]:has(.interest-panel-marker),
div[data-testid="stVerticalBlockBorderWrapper"]:has(.prefs-panel-marker) {
  background: var(--card);
  backdrop-filter: blur(18px);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 26px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 16px 44px rgba(148, 163, 184, 0.14);
  margin-bottom: 18px;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.skills-panel-marker)::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--g1);
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.interest-panel-marker)::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(135deg,#0ea5e9,#14b8a6);
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.prefs-panel-marker)::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(135deg,#fb7185,#f59e0b);
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.skills-panel-marker) [data-testid="stSlider"] {
  margin-bottom: 8px;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.interest-panel-marker) [data-testid="stSlider"] {
  margin-bottom: 8px;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.prefs-panel-marker) [data-testid="stSelectbox"] {
  margin-bottom: 6px;
}

/* ── Animations ── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(18px); }
  to   { opacity: 1; transform: translateY(0); }
}
.fade-up { animation: fadeUp 0.45s cubic-bezier(0.4,0,0.2,1) forwards; }

@keyframes pulseDot {
  0%,100% { opacity:1; transform:scale(1); }
  50% { opacity:0.4; transform:scale(1.5); }
}

@media (max-width: 900px) {
  [data-testid="stHorizontalBlock"] {
    gap: 14px !important;
  }
  .top3-col {
    min-height: 410px;
  }
  .top3-card {
    min-height: 0;
  }
  .top3-title {
    min-height: 96px;
    font-size: 18px;
  }
  .top3-metrics {
    min-height: 62px;
  }
  .site-header {
    padding: 10px 18px 12px;
    min-height: auto;
    flex-wrap: wrap;
  }
  .site-header-title {
    font-size: 24px;
  }
  .site-header-badges {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
  }
}
</style>
""")

# ─────────────────────────────────────────────────────────────────────────────
# DATA & ML
# ─────────────────────────────────────────────────────────────────────────────
BASE = os.path.dirname(__file__)
DATA = os.path.join(BASE, 'data')

ROLES = ['Data Analyst','Data Scientist','Machine Learning Engineer',
         'Software Engineer','Web Developer','Cloud/DevOps Engineer']

ROLE_GRAD = {
    'Data Analyst':          'linear-gradient(135deg,#5ca8fc,#a855f7)',
    'Data Scientist':        'linear-gradient(135deg,#a855f7,#ec4899)',
    'Machine Learning Engineer':'linear-gradient(135deg,#ec4899,#f97316)',
    'Software Engineer':     'linear-gradient(135deg,#f97316,#f59e0b)',
    'Web Developer':         'linear-gradient(135deg,#22d3ee,#a855f7)',
    'Cloud/DevOps Engineer': 'linear-gradient(135deg,#34d399,#06b6d4)',
}
ROLE_COLOR = {
    'Data Analyst':'#5ca8fc','Data Scientist':'#a855f7',
    'Machine Learning Engineer':'#ec4899','Software Engineer':'#f97316',
    'Web Developer':'#22d3ee','Cloud/DevOps Engineer':'#34d399',
}
ROLE_EMOJI = {
    'Data Analyst':'📊','Data Scientist':'🔬',
    'Machine Learning Engineer':'🤖','Software Engineer':'💻',
    'Web Developer':'🌐','Cloud/DevOps Engineer':'☁️'
}
CAPSTONE_TITLES = {
    'Data Analyst': 'Complete a mini data analysis project',
    'Data Scientist': 'Complete a small data science project',
    'Machine Learning Engineer': 'Complete a small ML engineering project',
    'Software Engineer': 'Complete a small software development project',
    'Web Developer': 'Build a small responsive web project',
    'Cloud/DevOps Engineer': 'Complete a small cloud automation project',
}

SKILL_COLS = ['skill_python','skill_sql','skill_statistics','skill_machine_learning',
              'skill_programming_fundamentals','skill_web_development','skill_cloud',
              'skill_devops','skill_data_visualisation','skill_git']
INTEREST_COLS = ['interest_data_analysis','interest_ai_ml','interest_software_development',
                 'interest_web_development','interest_cloud_infrastructure',
                 'interest_business_problem_solving']
SKILL_MAP = {
    'skill_python':'python_required','skill_sql':'sql_required',
    'skill_statistics':'statistics_required','skill_machine_learning':'ml_required',
    'skill_programming_fundamentals':'programming_required',
    'skill_web_development':'web_required','skill_cloud':'cloud_required',
    'skill_devops':'devops_required','skill_data_visualisation':'data_viz_required',
    'skill_git':'git_required'
}
SKILL_TAG_MAP = {
    'Python':'Python','Sql':'SQL','Statistics':'Statistics',
    'Machine Learning':'Machine Learning',
    'Programming Fundamentals':'Programming Fundamentals',
    'Web Development':'Web Development','Cloud':'Cloud',
    'Devops':'DevOps','Data Visualisation':'Data Visualisation','Git':'Git'
}
ROLE_INTEREST_MAP = {
    'Data Analyst':'interest_data_analysis','Data Scientist':'interest_ai_ml',
    'Machine Learning Engineer':'interest_ai_ml',
    'Software Engineer':'interest_software_development',
    'Web Developer':'interest_web_development',
    'Cloud/DevOps Engineer':'interest_cloud_infrastructure'
}
ROLE_SKILL_MAP = {
    'Data Analyst':'skill_sql','Data Scientist':'skill_statistics',
    'Machine Learning Engineer':'skill_machine_learning',
    'Software Engineer':'skill_programming_fundamentals',
    'Web Developer':'skill_web_development','Cloud/DevOps Engineer':'skill_cloud'
}
SKILL_DISPLAY = {
    'skill_sql':'SQL','skill_statistics':'Statistics',
    'skill_machine_learning':'Machine Learning',
    'skill_programming_fundamentals':'Programming Fundamentals',
    'skill_web_development':'Web Development','skill_cloud':'Cloud'
}
SKILL_UI = [
    ('skill_python','🐍','Python','#a855f7'),
    ('skill_sql','🗄️','SQL','#ec4899'),
    ('skill_statistics','📐','Statistics','#06b6d4'),
    ('skill_machine_learning','🤖','Machine Learning','#f97316'),
    ('skill_programming_fundamentals','💻','Programming','#f59e0b'),
    ('skill_web_development','🌐','Web Development','#22d3ee'),
    ('skill_cloud','☁️','Cloud','#34d399'),
    ('skill_devops','⚙️','DevOps','#a78bfa'),
    ('skill_data_visualisation','📊','Data Viz','#fb7185'),
    ('skill_git','🔀','Git','#38bdf8'),
]
INT_UI = [
    ('interest_data_analysis','📊','Data Analysis','#06b6d4'),
    ('interest_ai_ml','🤖','AI / ML','#a855f7'),
    ('interest_software_development','💻','Software Dev','#f97316'),
    ('interest_web_development','🌐','Web Dev','#22d3ee'),
    ('interest_cloud_infrastructure','☁️','Cloud Infra','#34d399'),
    ('interest_business_problem_solving','💼','Business Problems','#f59e0b'),
]

# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_and_train():
    up = pd.read_csv(os.path.join(DATA, 'user_profiles.csv'))
    rsm = pd.read_csv(os.path.join(DATA, 'role_skill_matrix.csv'))
    rm = pd.read_csv(os.path.join(DATA, 'role_metadata.csv'))
    rt = pd.read_csv(os.path.join(DATA, 'roadmap_templates.csv'))
    rc = pd.read_csv(os.path.join(DATA, 'resource_catalogue.csv'))

    df = up.copy()
    df['total_skill_score'] = df[SKILL_COLS].sum(axis=1)
    df['top_interest'] = df[INTEREST_COLS].idxmax(axis=1).str.replace('interest_', '')

    le_work = LabelEncoder()
    le_style = LabelEncoder()
    le_goal = LabelEncoder()
    le_int = LabelEncoder()
    le_tgt = LabelEncoder()

    df['preferred_work_type_enc'] = le_work.fit_transform(df['preferred_work_type'])
    df['preferred_learning_style_enc'] = le_style.fit_transform(df['preferred_learning_style'])
    df['career_goal_enc'] = le_goal.fit_transform(df['career_goal'])
    df['top_interest_enc'] = le_int.fit_transform(df['top_interest'])
    df['target_encoded'] = le_tgt.fit_transform(df['target_role'])

    fcols = (
        [c for c in df.columns if c.startswith('interest_')] +
        [c for c in df.columns if c.startswith('skill_')] +
        [
            'preferred_work_type_enc',
            'preferred_learning_style_enc',
            'career_goal_enc',
            'top_interest_enc',
            'total_skill_score',
        ]
    )

    X = df[fcols]
    y = df['target_encoded']
    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    sc = StandardScaler()
    Xtrs = sc.fit_transform(Xtr)
    Xtes = sc.transform(Xte)
    mdl = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        eval_metric='mlogloss',
        random_state=42,
        n_jobs=-1,
    )
    mdl.fit(Xtrs,ytr)
    y_pred = mdl.predict(Xtes)

    return {
        'model': mdl,
        'scaler': sc,
        'le_work': le_work,
        'le_style': le_style,
        'le_goal': le_goal,
        'le_int': le_int,
        'le_tgt': le_tgt,
        'fcols': fcols,
        'f1': f1_score(yte, y_pred, average='macro'),
        'acc': accuracy_score(yte, y_pred),
        'up': up,
        'rsm': rsm,
        'rm': rm,
        'rt': rt,
        'rc': rc,
    }

def softmax(x):
    e=np.exp(x-np.max(x)); return e/e.sum()

def encode_profile(p,M):
    row = {k: p.get(k, 3) for k in INTEREST_COLS + SKILL_COLS}
    row['preferred_work_type_enc'] = M['le_work'].transform([p['preferred_work_type']])[0]
    row['preferred_learning_style_enc'] = M['le_style'].transform([p['preferred_learning_style']])[0]
    row['career_goal_enc'] = M['le_goal'].transform([p['career_goal']])[0]
    top = max(INTEREST_COLS, key=lambda key: row[key]).replace('interest_', '')
    row['top_interest_enc'] = M['le_int'].transform([top])[0]
    row['total_skill_score'] = sum(row[k] for k in SKILL_COLS)
    return M['scaler'].transform(pd.DataFrame([row])[M['fcols']])

def predict_ranked(p,M):
    vec=encode_profile(p,M)
    proba=M['model'].predict_proba(vec)[0]
    scores=softmax(proba)
    df=pd.DataFrame({'Role':M['le_tgt'].classes_,'Score':scores})\
        .sort_values('Score',ascending=False).reset_index(drop=True)
    return df

def readiness_score(p,role,M):
    rr=M['rsm'][M['rsm']['role']==role].iloc[0]
    tot=sum(rr[v] for v in SKILL_MAP.values())
    got=sum(min(p.get(k,1),rr[v]) for k,v in SKILL_MAP.items())
    return round(got/tot*100,1)

def compute_gap(p,role,M):
    rr=M['rsm'][M['rsm']['role']==role].iloc[0]; rows=[]
    for uc,rc2 in SKILL_MAP.items():
        sn=uc.replace('skill_','').replace('_',' ').title()
        cur=p.get(uc,1); req=rr[rc2]; gap=max(0,req-cur)
        st2='No Gap' if gap==0 else 'Moderate Gap' if gap==1 else 'Major Gap'
        pri='Low' if gap==0 else 'High' if gap>=2 else ('High' if req>=4 else 'Medium' if req>=3 else 'Low')
        rows.append({'Skill':sn,'key':uc,'Current':cur,'Required':req,'Gap':gap,'Status':st2,'Priority':pri})
    return pd.DataFrame(rows).sort_values(['Gap','Required'],ascending=[False,False]).reset_index(drop=True)

def why_fits(p,role):
    ic=ROLE_INTEREST_MAP.get(role,''); sc2=ROLE_SKILL_MAP.get(role,'')
    iv=p.get(ic,0); sv=p.get(sc2,0)
    wt=p.get('preferred_work_type',''); cg=p.get('career_goal','')
    iname=ic.replace('interest_','').replace('_',' ')
    sname=SKILL_DISPLAY.get(sc2,sc2.replace('skill_',''))
    is_='strong' if iv>=4 else 'good' if iv==3 else 'developing'
    sk_='excellent' if sv>=4 else 'solid' if sv==3 else 'developing'
    return (f'This role fits because you show <strong>{is_}</strong> interest in '
            f'<strong>{iname}</strong>, <strong>{sk_}</strong> '
            f'<strong>{sname}</strong> ability, and prefer '
            f'<strong>{wt.lower()}</strong> work. Your career goal to '
            f'<strong>"{cg.lower()}"</strong> aligns with what {role}s do day-to-day.')

def clean_step(t):
    text = re.sub(r'<[^>]+>', ' ', str(t))
    text = html.unescape(text)
    text = re.sub(r'</?\s*div\b', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'/\s*div', ' ', text, flags=re.IGNORECASE)
    text = text.replace('<', ' ').replace('>', ' ').replace('"', ' ')
    text = re.sub(r'^Step\s+\d+\s*[-\u2013]\s*', '', text).strip()
    text = re.sub(r'\s+', ' ', text).strip(" -_/.,:;")
    if re.fullmatch(r'[/\s\w<>-]*div[/\s\w<>-]*', text, flags=re.IGNORECASE):
        return ''
    return text

def safe_step_title(text, fallback):
    cleaned = clean_step(text)
    if not cleaned or '</' in cleaned or '<' in cleaned:
        return fallback
    return cleaned
def get_level(s):  return 'Beginner' if s<=2 else 'Intermediate' if s==3 else 'Advanced'

def get_resources(skill_label,level_score,role,M,n=3):
    tag_name = skill_label.title()
    if tag_name == 'Data Visualisation': tag_name = 'Data Visualisation'
    lvl=get_level(level_score)
    filt=M['rc'][M['rc']['skill_tag'].str.strip()==tag_name]
    if filt.empty:
        for tk in SKILL_TAG_MAP.values():
            if tk.lower() in skill_label.lower():
                filt=M['rc'][M['rc']['skill_tag'].str.strip()==tk]; break
    role_filt=filt[filt['role_relevance'].str.contains(role.split(' ')[0],na=False)]
    if not role_filt.empty: filt=role_filt
    matched=filt[filt['level']==lvl]
    if matched.empty: matched=filt[filt['level']=='Beginner']
    if matched.empty: matched=filt
    return matched.drop_duplicates('resource_title').head(n)

def build_roadmap(gd,role,M):
    rm2=M['rt'][M['rt']['role']==role].copy()
    rm2['skill_norm']=rm2['skill_tag'].str.title()
    steps=[]; n=1
    for _,r in gd[gd['Gap']>0].iterrows():
        m=rm2[rm2['skill_norm']==r['Skill']]
        if m.empty: m=rm2[rm2['skill_norm'].str.contains(r['Skill'].split()[0],na=False,case=False)]
        if m.empty: continue
        action = safe_step_title(m.iloc[0]['step_template'], f'Build stronger {r["Skill"]} skills')
        steps.append({'n':n,'skill':r['Skill'],'key':r['key'],'gap':int(r['Gap']),
                      'status':r['Status'],'priority':r['Priority'],
                      'action':action,
                      'resources':get_resources(r['Skill'],r['Current'],role,M)}); n+=1
    for _,r in gd[gd['Gap']==0].iterrows():
        m=rm2[rm2['skill_norm']==r['Skill']]
        if m.empty: continue
        action = safe_step_title(m.iloc[0]['step_template'], f'Keep practicing {r["Skill"]}')
        steps.append({'n':n,'skill':r['Skill'],'gap':0,'status':'No Gap','priority':'Low',
                      'action':action,
                      'resources':pd.DataFrame()}); n+=1
    proj=rm2[rm2['project_step_flag']==1]
    if not proj.empty:
        project_title = CAPSTONE_TITLES.get(
            role,
            safe_step_title(proj.iloc[0]['step_template'], f'Complete a small {role} project')
        )
        steps.append({'n':n,'skill':'Capstone Project','gap':0,'status':'Capstone',
                      'priority':'','action':project_title,
                      'resources':pd.DataFrame()})
    return steps

def rc_col(v):
    if v>=75: return '#34d399'
    if v>=50: return '#f59e0b'
    return '#f472b6'

# ─────────────────────────────────────────────────────────────────────────────
# STEP INDICATOR
# ─────────────────────────────────────────────────────────────────────────────
def step_bar(active=1):
    labels=['Your Profile','Your Matches','Your Roadmap']
    items=[]
    for i,lbl in enumerate(labels):
        n=i+1
        if n<active:
            items.append(
                f'<div style="display:flex;align-items:center;gap:9px;padding:9px 18px;'
                f'border-radius:999px;font-size:13px;font-weight:600;color:#34d399;">'
                f'<div style="width:24px;height:24px;border-radius:50%;display:flex;align-items:center;'
                f'justify-content:center;font-size:11px;font-weight:700;background:rgba(52,211,153,0.2);'
                f'border:1.5px solid #34d399;color:#34d399;">✓</div>{lbl}</div>'
            )
        elif n==active:
            items.append(
                f'<div style="display:flex;align-items:center;gap:9px;padding:9px 18px;'
                f'background:rgba(14,165,233,0.10);border:1px solid rgba(14,165,233,0.20);'
                f'border-radius:999px;font-size:13px;font-weight:600;color:#0284c7;">'
                f'<div style="width:24px;height:24px;border-radius:50%;display:flex;align-items:center;'
                f'justify-content:center;font-size:11px;font-weight:700;background:linear-gradient(135deg,#0ea5e9,#14b8a6);'
                f'color:white;">{n}</div>{lbl}</div>'
            )
        else:
            items.append(
                f'<div style="display:flex;align-items:center;gap:9px;padding:9px 18px;'
                f'border-radius:999px;font-size:13px;font-weight:600;color:#527184;">'
                f'<div style="width:24px;height:24px;border-radius:50%;display:flex;align-items:center;'
                f'justify-content:center;font-size:11px;font-weight:700;background:rgba(255,255,255,0.92);'
                f'border:1.5px solid rgba(15,23,42,0.10);color:#527184;">{n}</div>{lbl}</div>'
            )
        if i<2:
            c='linear-gradient(90deg,rgba(14,165,233,0.45),rgba(20,184,166,0.45))' if n<active else 'rgba(15,23,42,0.10)'
            items.append(f'<div style="width:36px;height:2px;background:{c};"></div>')
    return (
        f'<div style="display:flex;align-items:center;justify-content:center;'
        f'gap:0;margin-bottom:52px;flex-wrap:wrap;">' + ''.join(items) + '</div>'
    )

# ─────────────────────────────────────────────────────────────────────────────
# SECTION: HEADER
# ─────────────────────────────────────────────────────────────────────────────
def render_header():
    H("""
<div class="site-header">
  <div class="site-header-brand">
    <span class="site-header-title">
      CareerPath<span style="background:linear-gradient(135deg,#0ea5e9,#14b8a6);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">AI</span>
    </span>
  </div>
  <div class="site-header-badges">
    <span class="site-header-badge purple">XGBoost - F1 0.9975</span>
    <span class="site-header-badge cyan">6 IT Roles</span>
    <span class="site-header-badge green">6K Profiles</span>
  </div>
</div>
""")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION: HERO + FORM
# ─────────────────────────────────────────────────────────────────────────────
def render_hero_and_form(active_step):
    H(f"""
<div style="max-width:1240px;margin:0 auto;padding:76px 24px 0;">
  <div style="text-align:center;padding:20px 20px 40px;">
    <div style="display:inline-flex;align-items:center;gap:8px;padding:6px 18px;
      background:rgba(14,165,233,0.08);border:1px solid rgba(14,165,233,0.20);
      border-radius:999px;font-size:12px;color:#0284c7;font-family:'DM Mono',monospace;
      margin-bottom:28px;letter-spacing:0.5px;">
      <span style="width:7px;height:7px;background:#0ea5e9;border-radius:50%;
        animation:pulseDot 1.8s ease-in-out infinite;display:inline-block;"></span>
      ✦ AI-Powered Career Intelligence &nbsp;·&nbsp; UWE Bristol UFCEKP-30-3
    </div>
    <h1 style="font-family:'Syne',sans-serif;font-size:clamp(44px,6vw,76px);
      font-weight:800;line-height:1.03;letter-spacing:-3px;margin-bottom:22px;color:#0f172a;">
      Find your <span style="background:linear-gradient(135deg,#0ea5e9,#14b8a6);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">perfect IT role</span><br>in seconds
    </h1>
    <p style="font-size:17px;color:#527184;max-width:500px;margin:0 auto 40px;line-height:1.75;">
      Set your skill levels and interests. Our XGBoost ML model matches you to the best IT career and builds your personalised learning roadmap.
    </p>
    {step_bar(active_step)}
  </div>
</div>
""")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION: FORM INPUTS
# ─────────────────────────────────────────────────────────────────────────────
def render_form():
    H('<div style="max-width:1240px;margin:0 auto;padding:0 24px;">')

    left_col, right_col = st.columns(2, gap='medium')

    with left_col:
        skills_box = st.container(border=True)
        with skills_box:
            H("""<div class="skills-panel-marker"></div>
            <div class="skills-panel-header">
              <div class="skills-panel-title">🛠️ Technical Skills</div>
              <div class="skills-panel-subtitle">Rate your current level — 1 = Beginner, 5 = Expert</div>
            </div>""")
            skills = {}
            for key,ico,label,col in SKILL_UI:
                skills[key] = st.slider(f'{ico}  {label}', 1, 5, 3, key=f'sk_{key}')

    with right_col:
        interest_box = st.container(border=True)
        with interest_box:
            H("""<div class="interest-panel-marker"></div>
            <div class="skills-panel-header">
              <div class="skills-panel-title">💡 Interest Areas</div>
              <div class="skills-panel-subtitle">What excites you most? — 1 = Low, 5 = High</div>
            </div>""")
            interests = {}
            for key,ico,label,col in INT_UI:
                interests[key] = st.slider(f'{ico}  {label}', 1, 5, 3, key=f'int_{key}')

        prefs_box = st.container(border=True)
        with prefs_box:
            H("""<div class="prefs-panel-marker"></div>
            <div class="skills-panel-header">
              <div class="skills-panel-title">⚙️ Preferences</div>
              <div class="skills-panel-subtitle">How you work and learn best</div>
            </div>""")
            wt = st.selectbox('Preferred Work Type', [
                'Analytical','Research-Oriented','System Building',
                'User-Facing Development','Automation-Focused','Infrastructure/Operations'
            ], key='wt')
            ls = st.selectbox('Learning Style', [
                'Practical','Visual','Project-Based','Theory-First'
            ], key='ls')
            cg = st.selectbox('Career Goal', [
                'Work with Data','Build AI Systems','Build Software',
                'Build Websites','Manage Cloud/Deployment Systems','Exploring Options'
            ], key='cg')
            H('<div style="height:8px;"></div>')
            run = st.button('✦  Find My IT Role', key='run_btn', use_container_width=True)

    H('</div>')

    profile = {
        **skills, **interests,
        'preferred_work_type':wt, 'preferred_learning_style':ls, 'career_goal':cg
    }
    return profile, run

# ─────────────────────────────────────────────────────────────────────────────
# SECTION: RESULTS
# ─────────────────────────────────────────────────────────────────────────────
def render_results(profile, M):
    ranked = predict_ranked(profile, M)
    top3 = ranked.head(3).copy()
    top3_roles = top3['Role'].tolist()
    sel_role = st.session_state.get('sel_role') or top3_roles[0]
    if sel_role not in top3_roles:
        sel_role = top3_roles[0]
    st.session_state['sel_role'] = sel_role

    H('<div style="height:1.5px;background:linear-gradient(90deg,transparent,rgba(14,165,233,0.28),transparent);margin:40px 0;"></div>')

    # ── Top 3 role cards ──
    H("""<div id="top3-header" class="jump-anchor" style="font-family:'Syne',sans-serif;font-size:26px;font-weight:800;
      letter-spacing:-0.8px;margin-bottom:5px;color:#0f172a;">🏆 Your Top 3 Role Recommendations</div>
    <div style="font-size:14px;color:#527184;margin-bottom:26px;line-height:1.6;">
      Click one of the 3 recommendations below to open a single detailed role analysis.</div>""")

    labels = ['🥇 Best Match', '🥈 Great Fit', '🥉 Worth Exploring']
    c1, c2, c3 = st.columns(3, gap='medium')
    for i, (col, (_, row)) in enumerate(zip([c1, c2, c3], top3.iterrows())):
        role = row['Role']
        rdv = readiness_score(profile, role, M)
        rc_c = rc_col(rdv)
        grad = ROLE_GRAD[role]
        is_sel = role == sel_role
        with col:
            render_top3_card(role, labels[i], rdv, rc_c, grad, is_sel)
            H('<div class="top3-real-button">')
            if st.button('View role ->', key=f'top3_view_{role.replace(" ","_").replace("/","_")}'):
                select_role(role)
                st.rerun()
            H('</div>')

    H('<div style="height:1.5px;background:linear-gradient(90deg,transparent,rgba(14,165,233,0.28),transparent);margin:40px 0;"></div>')

    # ── All readiness ──
    H("""<div style="font-family:'Syne',sans-serif;font-size:26px;font-weight:800;
      letter-spacing:-0.8px;margin-bottom:5px;color:#0f172a;">📊 Readiness Across All Roles</div>
    <div style="font-size:14px;color:#527184;margin-bottom:26px;">
      How prepared you are for each IT career path right now</div>""")

    readiness_rows = []
    for _,row in ranked.iterrows():
        role=row['Role']; rdv=readiness_score(profile,role,M)
        rc_c=rc_col(rdv); grad=ROLE_GRAD[role]
        readiness_rows.append(f"""<div style="display:flex;align-items:center;gap:12px;padding:10px 0;
          border-bottom:1px solid rgba(15,23,42,0.08);">
          <span style="font-size:20px;width:26px;text-align:center;">{ROLE_EMOJI[role]}</span>
          <span style="font-size:13px;font-weight:600;min-width:200px;color:#0f172a;">{role}</span>
          <div style="flex:1;height:8px;background:#dbeef4;border-radius:4px;overflow:hidden;">
            <div style="width:{rdv}%;height:100%;background:{grad};border-radius:4px;
              transition:width 1s;"></div>
          </div>
          <span style="font-family:'DM Mono',monospace;font-size:12px;font-weight:700;
            min-width:38px;text-align:right;color:{rc_c};">{rdv}%</span>
        </div>""")
    H(f'<div class="cp-card"><div class="cp-card-bar"></div>{"".join(readiness_rows)}</div>')

    H('<div style="height:1.5px;background:linear-gradient(90deg,transparent,rgba(14,165,233,0.28),transparent);margin:40px 0;"></div>')

    H(f"""<div style="display:flex;align-items:flex-start;justify-content:space-between;
      flex-wrap:wrap;gap:14px;margin-bottom:22px;">
      <div>
        <div id="deep-dive-header" class="jump-anchor" style="font-family:'Syne',sans-serif;font-size:26px;font-weight:800;
          letter-spacing:-0.8px;margin-bottom:5px;color:#0f172a;">🔍 Deep Dive - {sel_role}</div>
        <div style="font-size:14px;color:#527184;">Showing detailed analysis for the role you selected from the top 3 careers</div>
      </div>
    </div>""")

    render_deep_dive(sel_role, profile, M)
    if st.session_state.get('scroll_target'):
        scroll_to_anchor(
            st.session_state['scroll_target'],
            st.session_state.get('scroll_token', 0)
        )
        st.session_state['scroll_target'] = None

# ─────────────────────────────────────────────────────────────────────────────
# SECTION: DEEP DIVE
# ─────────────────────────────────────────────────────────────────────────────
def render_deep_dive(role, profile, M):
    grad = ROLE_GRAD[role]
    meta = M['rm'][M['rm']['role']==role].iloc[0]
    gd   = compute_gap(profile, role, M)
    rdv  = readiness_score(profile, role, M)
    gaps  = gd[gd['Gap']>0]
    mets  = gd[gd['Gap']==0]

    # Why card
    H(f"""<div style="background:linear-gradient(135deg,rgba(14,165,233,0.10),rgba(20,184,166,0.06));
      border:1.5px solid rgba(14,165,233,0.18);border-radius:14px;padding:22px 26px;
      font-size:15px;line-height:1.75;position:relative;overflow:hidden;margin-bottom:20px;">
      <div style="position:absolute;top:-16px;left:14px;font-size:90px;
        font-family:'Syne',sans-serif;color:rgba(14,165,233,0.12);line-height:1;">"</div>
      <div style="font-size:11px;font-weight:700;letter-spacing:1.2px;color:#0284c7;
        margin-bottom:10px;font-family:'DM Mono',monospace;">WHY THIS ROLE FITS YOU</div>
      <div style="color:#0f172a;">{why_fits(profile,role)}</div>
    </div>""")

    # Stats row
    H(f"""<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:22px;">
      <div style="background:rgba(255,255,255,0.82);border:1px solid rgba(15,23,42,0.08);border-radius:12px;
        padding:18px;text-align:center;">
        <div style="font-family:'Syne',sans-serif;font-size:30px;font-weight:800;
          letter-spacing:-1px;background:{grad};-webkit-background-clip:text;
          -webkit-text-fill-color:transparent;background-clip:text;">{rdv}%</div>
        <div style="font-size:12px;color:#527184;margin-top:3px;">Readiness Score</div>
      </div>
      <div style="background:rgba(255,255,255,0.82);border:1px solid rgba(15,23,42,0.08);border-radius:12px;
        padding:18px;text-align:center;">
        <div style="font-family:'Syne',sans-serif;font-size:30px;font-weight:800;
          letter-spacing:-1px;background:{grad};-webkit-background-clip:text;
          -webkit-text-fill-color:transparent;background-clip:text;">{len(gaps)}</div>
        <div style="font-size:12px;color:#527184;margin-top:3px;">Skills to Develop</div>
      </div>
      <div style="background:rgba(255,255,255,0.82);border:1px solid rgba(15,23,42,0.08);border-radius:12px;
        padding:18px;text-align:center;">
        <div style="font-family:'Syne',sans-serif;font-size:30px;font-weight:800;
          letter-spacing:-1px;background:{grad};-webkit-background-clip:text;
          -webkit-text-fill-color:transparent;background-clip:text;">{len(mets)}</div>
        <div style="font-size:12px;color:#527184;margin-top:3px;">Strengths Met</div>
      </div>
    </div>""")

    # Tabs
    tab1, tab2 = st.tabs(['📊  Skill Gap', '🗺️  Roadmap'])

    # ── TAB 1: SKILL GAP ──
    with tab1:
        gap_rows = []

        for _,r in gd.iterrows():
            gap   = r['Gap']
            if gap==0: badge='<span style="padding:3px 10px;border-radius:999px;font-size:10px;font-weight:700;font-family:DM Mono,monospace;background:rgba(52,211,153,0.15);color:#34d399;border:1px solid rgba(52,211,153,0.3);">No Gap</span>'
            elif gap==1: badge='<span style="padding:3px 10px;border-radius:999px;font-size:10px;font-weight:700;font-family:DM Mono,monospace;background:rgba(245,158,11,0.15);color:#f59e0b;border:1px solid rgba(245,158,11,0.3);">Moderate Gap</span>'
            else: badge='<span style="padding:3px 10px;border-radius:999px;font-size:10px;font-weight:700;font-family:DM Mono,monospace;background:rgba(236,72,153,0.15);color:#f472b6;border:1px solid rgba(236,72,153,0.3);">Major Gap</span>'
            cur_w=int(r['Current']/5*100); req_w=int(r['Required']/5*100)
            opacity_req = '0.85' if gap>0 else '0.25'
            gap_rows.append(f"""<div style="display:flex;align-items:center;gap:12px;padding:11px 0;
              border-bottom:1px solid rgba(15,23,42,0.07);">
              <div style="font-size:13px;font-weight:600;min-width:155px;color:#0f172a;
                display:flex;align-items:center;gap:6px;">{r['Skill']}</div>
              <div style="flex:1;display:flex;align-items:center;gap:8px;">
                <div style="height:9px;border-radius:5px;background:#22d3ee;opacity:0.85;
                  width:{cur_w}%;transition:width 0.8s;"></div>
                <span style="font-family:'DM Mono',monospace;font-size:11px;
                  color:#527184;white-space:nowrap;">{int(r['Current'])}→{int(r['Required'])}</span>
                <div style="height:9px;border-radius:5px;background:#ec4899;
                  opacity:{opacity_req};width:{req_w}%;transition:width 0.8s;"></div>
              </div>
              {badge}
            </div>""")

        H(f"""<div class="cp-card" style="margin-top:12px;">
          <div class="cp-card-bar"></div>
          <div style="font-family:'Syne',sans-serif;font-size:17px;font-weight:700;
            margin-bottom:5px;color:#0f172a;">🔍 Skill Gap Analysis</div>
          <div style="font-size:13px;color:#527184;margin-bottom:16px;">
            Current vs required skill levels for {role}</div>
          <div style="display:flex;gap:16px;font-size:12px;color:#527184;margin-bottom:18px;">
            <span><span style="display:inline-block;width:10px;height:6px;border-radius:3px;
              background:#22d3ee;margin-right:4px;"></span>Current level</span>
            <span><span style="display:inline-block;width:10px;height:6px;border-radius:3px;
              background:#ec4899;margin-right:4px;"></span>Required level</span>
          </div>
          <div>{"".join(gap_rows)}</div>
        </div>""")

    # ── TAB 2: ROADMAP ──
    with tab2:
        steps = build_roadmap(gd, role, M)
        step_blocks = []
        for s in steps:
            status = s['status']
            if status=='Major Gap':
                circle_style='background:rgba(236,72,153,0.2);color:#f472b6;border:2px solid rgba(236,72,153,0.4);'
                badge='<span style="padding:3px 10px;border-radius:999px;font-size:10px;font-weight:700;background:rgba(236,72,153,0.15);color:#f472b6;border:1px solid rgba(236,72,153,0.4);">⚡ MAJOR GAP</span>'
                pri='High'
            elif status=='Moderate Gap':
                circle_style='background:rgba(245,158,11,0.2);color:#f59e0b;border:2px solid rgba(245,158,11,0.4);'
                badge='<span style="padding:3px 10px;border-radius:999px;font-size:10px;font-weight:700;background:rgba(245,158,11,0.15);color:#f59e0b;border:1px solid rgba(245,158,11,0.4);">⚠️ MODERATE GAP</span>'
                pri='Medium'
            elif status=='Capstone':
                circle_style='background:linear-gradient(135deg,#a855f7,#ec4899);color:white;border:none;box-shadow:0 4px 16px rgba(168,85,247,0.5);'
                badge='<span style="padding:3px 10px;border-radius:999px;font-size:10px;font-weight:700;background:rgba(168,85,247,0.2);color:#c084fc;border:1px solid rgba(168,85,247,0.4);">🚀 CAPSTONE PROJECT</span>'
                pri=''
            else:
                circle_style='background:rgba(52,211,153,0.12);color:#34d399;border:2px solid rgba(52,211,153,0.3);'
                badge='<span style="padding:3px 10px;border-radius:999px;font-size:10px;font-weight:700;background:rgba(52,211,153,0.15);color:#34d399;border:1px solid rgba(52,211,153,0.3);">✅ SKILL MET</span>'
                pri=''

            title_style = 'color:#527184;' if status=='No Gap' else 'color:#0f172a;'
            pri_html = f'<span style="font-size:12px;color:#527184;">Priority: {pri}</span>' if pri else ''

            # Resources
            res_html=''
            if status not in ['No Gap','Capstone'] and len(s.get('resources',pd.DataFrame()))>0:
                res_html='<div style="margin-top:8px;">'
                for _,r in s['resources'].iterrows():
                    res_html+=(f'<a href="{r["url"]}" target="_blank" style="display:inline-flex;'
                               f'align-items:center;gap:6px;padding:5px 12px;background:rgba(255,255,255,0.92);'
                               f'border:1.5px solid rgba(15,23,42,0.10);border-radius:8px;'
                               f'font-size:12px;color:#0284c7;text-decoration:none;'
                               f'margin:3px 4px 3px 0;font-family:DM Sans,sans-serif;font-weight:500;">'
                               f'📚 {html.escape(str(r["resource_title"]))} <span style="opacity:0.55;">- {html.escape(str(r["platform"]))}</span></a>')
                res_html+='</div>'

            step_title = html.escape(clean_step(s['action']))
            connector_html = ''
            if s['n'] != len(steps):
                connector_html = '<div style="position:absolute;left:17px;top:48px;bottom:0;width:2px;background:rgba(15,23,42,0.10);"></div>'
            step_blocks.append(
                f'<div style="display:flex;gap:14px;padding:14px 0;position:relative;">'
                f'{connector_html}'
                f'<div style="width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;'
                f'font-size:13px;font-weight:800;font-family:DM Mono,monospace;flex-shrink:0;position:relative;z-index:1;{circle_style}">{s["n"]}</div>'
                f'<div style="flex:1;padding-top:4px;">'
                f'<div style="font-size:15px;font-weight:700;margin-bottom:5px;letter-spacing:-0.2px;{title_style}">{step_title}</div>'
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;flex-wrap:wrap;">{badge}{pri_html}</div>'
                f'{res_html}'
                f'</div>'
                f'</div>'
            )
        H(f"""<div class="cp-card" style="margin-top:12px;">
          <div class="cp-card-bar" style="background:linear-gradient(135deg,#0ea5e9,#14b8a6)"></div>
          <div style="font-family:'Syne',sans-serif;font-size:17px;font-weight:700;
            margin-bottom:5px;color:#0f172a;">🗺️ Personalised Learning Roadmap</div>
          <div style="font-size:13px;color:#527184;margin-bottom:18px;">
            Gap skills first → already met skills → capstone project</div>
          <div>{"".join(step_blocks)}</div>
        </div>""")

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    initialize_session_state()

    with st.spinner('Loading CareerPath AI...'):
        M = load_and_train()

    selected_role_qp = read_query_param('selected_role')
    if selected_role_qp:
        st.session_state['sel_role'] = selected_role_qp
        st.session_state['show_deep'] = True
        st.session_state['ran'] = True

    jump_qp = read_query_param('jump')
    if jump_qp:
        queue_scroll(jump_qp)

    # Step indicator state
    active_step = 1
    if st.session_state.get('ran'): active_step = 2
    if st.session_state.get('show_deep'): active_step = 3

    render_header()
    render_hero_and_form(active_step)
    profile, run = render_form()
    style_form_panels()

    if run:
        st.session_state['ran'] = True
        st.session_state['profile'] = profile
        st.session_state['sel_role'] = None
        st.session_state['show_deep'] = True
        queue_scroll('top3-header')
        st.rerun()

    if st.session_state.get('ran'):
        H('<div style="max-width:1240px;margin:0 auto;padding:0 24px;">')
        render_results(st.session_state['profile'], M)
        H('</div>')

    # Footer
    H("""
<footer style="background:rgba(255,255,255,0.78);border-top:1px solid rgba(15,23,42,0.08);
  padding:40px 40px;margin-top:60px;">
  <div style="max-width:1240px;margin:0 auto;display:flex;justify-content:space-between;
    align-items:center;flex-wrap:wrap;gap:20px;">
    <div>
      <div style="display:flex;align-items:center;gap:9px;margin-bottom:8px;">
        <div style="width:32px;height:32px;background:linear-gradient(135deg,#0ea5e9,#14b8a6);
          border-radius:9px;display:flex;align-items:center;justify-content:center;">🎯</div>
        <span style="font-family:'Syne',sans-serif;font-size:18px;font-weight:800;color:#0f172a;">
          CareerPath<span style="background:linear-gradient(135deg,#0ea5e9,#14b8a6);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;">AI</span>
        </span>
      </div>
      <div style="color:#527184;font-size:13px;line-height:1.6;">
        Hein Htet Phyo &nbsp;·&nbsp; 25036746 &nbsp;·&nbsp; UFCEKP-30-3<br>
        UWE Bristol &nbsp;·&nbsp; April 2026
      </div>
    </div>
    <div style="display:flex;gap:12px;flex-wrap:wrap;">
      <div style="background:rgba(255,255,255,0.86);border:1px solid rgba(15,23,42,0.08);border-radius:12px;
        padding:14px 20px;text-align:center;min-width:88px;">
        <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;
          background:linear-gradient(135deg,#0ea5e9,#14b8a6);-webkit-background-clip:text;
          -webkit-text-fill-color:transparent;">0.9975</div>
        <div style="font-size:11px;color:#527184;margin-top:2px;">Macro F1</div>
      </div>
      <div style="background:rgba(255,255,255,0.86);border:1px solid rgba(15,23,42,0.08);border-radius:12px;
        padding:14px 20px;text-align:center;min-width:88px;">
        <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;
          background:linear-gradient(135deg,#14b8a6,#60a5fa);-webkit-background-clip:text;
          -webkit-text-fill-color:transparent;">6,000</div>
        <div style="font-size:11px;color:#527184;margin-top:2px;">Profiles</div>
      </div>
      <div style="background:rgba(255,255,255,0.86);border:1px solid rgba(15,23,42,0.08);border-radius:12px;
        padding:14px 20px;text-align:center;min-width:88px;">
        <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;
          background:linear-gradient(135deg,#34d399,#06b6d4);-webkit-background-clip:text;
          -webkit-text-fill-color:transparent;">300</div>
        <div style="font-size:11px;color:#527184;margin-top:2px;">Resources</div>
      </div>
      <div style="background:rgba(255,255,255,0.86);border:1px solid rgba(15,23,42,0.08);border-radius:12px;
        padding:14px 20px;text-align:center;min-width:88px;">
        <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;
          background:linear-gradient(135deg,#f59e0b,#f97316);-webkit-background-clip:text;
          -webkit-text-fill-color:transparent;">5</div>
        <div style="font-size:11px;color:#527184;margin-top:2px;">Datasets</div>
      </div>
    </div>
  </div>
</footer>
""")

if __name__ == '__main__':
    main()
