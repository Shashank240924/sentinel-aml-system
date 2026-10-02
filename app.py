import streamlit as st
import pandas as pd
import plotly.express as px
import networkx as nx
import os
import joblib
import numpy as np
import time
import streamlit.components.v1 as components
from pyvis.network import Network
from fpdf import FPDF
import base64
import csv
from datetime import datetime

# Import Custom Modules
from explain_natural import natural_language_explanation
try:
    from agent import generate_investigation_report, get_available_model
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False

# -----------------------------
# 0. UI CONFIGURATION (THE VISUAL UPGRADE)
# -----------------------------
st.set_page_config(
    page_title="SENTINEL: AML Command Center", 
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 🎨 CUSTOM CSS: THE "CYBER-OPS" THEME ---
st.markdown("""
<style>
    /* IMPORT FONTS */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600&display=swap');
    
    /* GLOBAL STYLES */
    .stApp {
        background-color: #050505;
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'JetBrains Mono', monospace;
        color: #E5E7EB;
        font-weight: 700;
    }
    
    /* CUSTOM CARDS (Glassmorphism) */
    .css-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease-in-out;
    }
    .css-card:hover {
        border-color: rgba(59, 130, 246, 0.5); /* Blue glow on hover */
    }
    
    /* METRIC BOXES */
    div[data-testid="stMetric"] {
        background-color: #111;
        border: 1px solid #333;
        padding: 15px;
        border-radius: 8px;
        color: white;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #00FF41; /* Hacker Green */
    }
    
    /* CUSTOM BUTTONS */
    .stButton>button {
        font-family: 'JetBrains Mono', monospace;
        border-radius: 6px;
        font-weight: bold;
        transition: all 0.3s;
    }
    /* Primary Action Button (Red) */
    .stButton>button[kind="primary"] {
        background: linear-gradient(45deg, #DC2626, #991B1B);
        border: none;
        box-shadow: 0 4px 14px 0 rgba(220, 38, 38, 0.39);
    }
    
    /* STATUS BADGES */
    .badge-critical {
        background-color: rgba(220, 38, 38, 0.2);
        color: #F87171;
        padding: 4px 12px;
        border-radius: 12px;
        border: 1px solid #F87171;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
    }
    .badge-suspicious {
        background-color: rgba(245, 158, 11, 0.2);
        color: #FBBF24;
        padding: 4px 12px;
        border-radius: 12px;
        border: 1px solid #FBBF24;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
    }
    .badge-safe {
        background-color: rgba(16, 185, 129, 0.2);
        color: #34D399;
        padding: 4px 12px;
        border-radius: 12px;
        border: 1px solid #34D399;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
    }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #222;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 1. AUTHENTICATION (Login Screen)
# -----------------------------
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_login():
    if st.session_state.username == 'admin' and st.session_state.password == 'sentinel2025':
        st.session_state.authenticated = True
    else:
        st.error("❌ Access Denied")

if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; border: 1px solid #333; padding: 40px; border-radius: 15px; background: #111;">
            <h1 style="color:#00FF41;">🛡️ SENTINEL</h1>
            <p style="color:#888; font-family:'JetBrains Mono'">FINANCIAL CRIME INTELLIGENCE UNIT</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.text_input("Agent ID", key="username")
        st.text_input("Access Key", type="password", key="password")
        st.button("🔒 AUTHENTICATE", on_click=check_login, use_container_width=True, type="primary")
        st.info("Demo: admin / sentinel2025")
    st.stop()

# -----------------------------
# 2. PDF GENERATOR
# -----------------------------
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'CONFIDENTIAL - SUSPICIOUS ACTIVITY REPORT (SAR)', 0, 1, 'C')
        self.ln(10)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_sar_pdf(txn_data, explanation):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Header Info
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(0, 10, f"Subject: Transaction {txn_data['txn_id']}", 0, 1, 'L', 1)
    pdf.ln(5)
    # Details
    pdf.set_font("Arial", 'B', 11); pdf.cell(40, 10, "Timestamp:"); pdf.set_font("Arial", '', 11); pdf.cell(0, 10, str(txn_data['timestamp']), ln=True)
    pdf.set_font("Arial", 'B', 11); pdf.cell(40, 10, "Entities:"); pdf.set_font("Arial", '', 11); pdf.cell(0, 10, f"{txn_data['from_acc']} -> {txn_data['to_acc']}", ln=True)
    pdf.set_font("Arial", 'B', 11); pdf.cell(40, 10, "Amount:"); pdf.set_font("Arial", '', 11); pdf.cell(0, 10, f"${txn_data['amount']:,.2f}", ln=True)
    pdf.set_font("Arial", 'B', 11); pdf.cell(40, 10, "Risk Score:"); pdf.set_font("Arial", '', 11); pdf.cell(0, 10, f"{txn_data['total_risk']:.2f}", ln=True)
    pdf.ln(10)
    # Narrative
    pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "Investigative Narrative", 0, 1)
    pdf.set_font("Arial", '', 11)
    # Latin-1 encoding fix for PDF
    safe_text = explanation.replace("🔴", "[HIGH RISK]").replace("🔵", "[LOW RISK]").encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 6, safe_text)
    return pdf.output(dest='S').encode('latin-1')

# -----------------------------
# 3. DATA LOADING
# -----------------------------
@st.cache_data
def load_data():
    if not os.path.exists("data/transactions_final.csv"):
        st.error("⚠️ System Offline: Risk Data Missing. Run fusion engine.")
        st.stop()
    df = pd.read_csv("data/transactions_final.csv", parse_dates=['timestamp'])
    return df

df = load_data()

# -----------------------------
# 4. SIDEBAR DASHBOARD
# -----------------------------
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px; border-bottom: 1px solid #333; margin-bottom: 20px;">
        <h2 style="color:#3B82F6; margin:0;">🛡️ SENTINEL</h2>
        <p style="color:#666; font-size: 12px;">AI-POWERED AML OPS</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🔍 Filters")
    threshold = st.slider("Risk Sensitivity", 0.0, 1.0, 0.0, 0.05)
    min_amount = st.number_input("Min Amount ($)", 0.0, step=1000.0)
    search_acc = st.text_input("Account Lookup", placeholder="e.g. A100...")
    
    st.divider()
    
    # Quick Stats in Sidebar
    st.markdown("**System Status**")
    st.markdown("🟢 AI Model: **Online**")
    st.markdown("🟢 Graph DB: **Connected**")
    
    st.divider()
    if st.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# Filter Data
filtered_df = df[(df['total_risk'] >= threshold) & (df['amount'] >= min_amount)]
if search_acc:
    filtered_df = filtered_df[filtered_df['from_acc'].str.contains(search_acc, case=False) | df['to_acc'].str.contains(search_acc, case=False)]

# -----------------------------
# 5. MAIN DASHBOARD HEADER
# -----------------------------
st.title("🌍 Global Threat Monitor")
st.markdown("Real-time surveillance of financial transaction streams.")

# Custom CSS Metrics Row
m1, m2, m3, m4 = st.columns(4)
with m1: st.metric("Alerts Triggered", f"{len(filtered_df):,}", delta="Live")
with m2: st.metric("Total Volume", f"${filtered_df['amount'].sum()/1e6:.1f}M", delta="USD")
with m3: st.metric("Avg Risk Score", f"{filtered_df['total_risk'].mean():.2f}", delta_color="inverse")
with m4: st.metric("High Priority", f"{len(filtered_df[filtered_df['total_risk']>0.8])}", delta="Critical")

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------
# 6. TABS
# -----------------------------
tab_live, tab_investigate, tab_network = st.tabs(["📊 Live Feed", "🕵️ Investigation", "🕸️ Link Analysis"])

# --- TAB 1: LIVE FEED ---
with tab_live:
    c_chart, c_list = st.columns([1, 2])
    
    with c_chart:
        st.markdown('<div class="css-card"><h4>📉 Risk Distribution</h4>', unsafe_allow_html=True)
        fig = px.histogram(filtered_df, x="total_risk", nbins=30, 
                           color_discrete_sequence=['#3B82F6'], template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=0, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_list:
        st.markdown('<div class="css-card"><h4>📡 Transaction Stream</h4>', unsafe_allow_html=True)
        
        start_btn = st.button("▶️  Connect Live Feed")
        t_ph = st.empty()
        
        if start_btn:
            sim_data = df.sort_values("timestamp", ascending=True).head(100)
            for i in range(1, len(sim_data)):
                subset = sim_data.iloc[:i].sort_values('timestamp', ascending=False)
                t_ph.dataframe(
                    subset[['txn_id', 'timestamp', 'from_acc', 'amount', 'total_risk']],
                    column_config={
                        "total_risk": st.column_config.ProgressColumn("Risk", min_value=0, max_value=1, format="%.2f"),
                        "amount": st.column_config.NumberColumn("Amount", format="$%.2f")
                    },
                    use_container_width=True, height=300
                )
                time.sleep(0.05)
        else:
            t_ph.dataframe(
                filtered_df[['txn_id', 'timestamp', 'from_acc', 'amount', 'total_risk']].head(20),
                column_config={
                    "total_risk": st.column_config.ProgressColumn("Risk", min_value=0, max_value=1, format="%.2f"),
                    "amount": st.column_config.NumberColumn("Amount", format="$%.2f")
                },
                use_container_width=True, height=300
            )
        st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: INVESTIGATION ---
with tab_investigate:
    if filtered_df.empty:
        st.info("No active alerts match your filters.")
    else:
        col_sel, col_det = st.columns([1, 2])
        
        with col_sel:
            st.markdown("##### Select Alert")
            sel_id = st.selectbox("Transaction ID", filtered_df['txn_id'].unique(), label_visibility="collapsed")
            row = filtered_df[filtered_df['txn_id'] == sel_id].iloc[0]
            
            # Profile Card
            st.markdown(f"""
            <div class="css-card">
                <h3 style="color:#3B82F6">{row['txn_id']}</h3>
                <p><strong>From:</strong> {row['from_acc']}<br>
                <strong>To:</strong> {row['to_acc']}</p>
                <h2 style="color:white">${row['amount']:,.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            # Risk Badge
            risk_val = row['total_risk']
            if risk_val > 0.8:
                st.markdown(f'<span class="badge-critical">🚨 CRITICAL RISK ({risk_val:.2f})</span>', unsafe_allow_html=True)
            elif risk_val > 0.5:
                st.markdown(f'<span class="badge-suspicious">⚠️ SUSPICIOUS ({risk_val:.2f})</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="badge-safe">✅ NORMAL ({risk_val:.2f})</span>', unsafe_allow_html=True)

        with col_det:
            st.markdown('<div class="css-card">', unsafe_allow_html=True)
            st.markdown("#### 🧠 Sentinel AI Analysis")
            
            # Logic for Explanation
            explanation_points = "Technical analysis unavailable."
            try:
                shap_store = joblib.load("models/shap_data_safe.pkl")
                shap_vals, X_shap, feature_cols = shap_store[1], shap_store[2], shap_store[5]
                idx = df[df['txn_id'] == sel_id].index[0]
                if idx in X_shap.index:
                    loc = X_shap.index.get_loc(idx)
                    explanation_points = natural_language_explanation(shap_vals[loc], feature_cols, X_shap.loc[idx].values)
            except:
                pass
            
            st.info(explanation_points)
            
            # --- AI AGENT ---
            st.markdown("---")
            c_gen, c_act = st.columns([1, 1])
            with c_gen:
                if AGENT_AVAILABLE:
                    if st.button("🤖 Auto-Draft SAR Report", type="primary", use_container_width=True):
                        with st.spinner("Agent analyzing graph topology & risk vectors..."):
                            narrative = generate_investigation_report(row, explanation_points)
                            st.text_area("Generated Narrative", value=narrative, height=150)
                            st.session_state['ai_sar'] = narrative
            
            # --- PDF DOWNLOAD ---
            final_narrative = st.session_state.get('ai_sar', explanation_points)
            pdf_data = generate_sar_pdf(row, final_narrative)
            b64_pdf = base64.b64encode(pdf_data).decode('latin-1')
            st.markdown(f'<a href="data:application/pdf;base64,{b64_pdf}" download="SAR_{sel_id}.pdf" style="text-decoration:none;"><button style="width:100%; background:#333; color:white; border:1px solid #555; padding:10px; border-radius:5px; cursor:pointer;">📄 Download Case File (PDF)</button></a>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # --- FEEDBACK ---
            st.markdown("##### 👮 Analyst Verification")
            cf1, cf2 = st.columns(2)
            with cf1:
                if st.button("✅ Confirm Fraud", use_container_width=True):
                    with open("data/feedback.csv", "a", newline="") as f:
                        csv.writer(f).writerow([row['txn_id'], datetime.now(), 1])
                    st.toast("Feedback Logged: Model Retraining Scheduled.")
            with cf2:
                if st.button("❌ False Alarm", use_container_width=True):
                    with open("data/feedback.csv", "a", newline="") as f:
                        csv.writer(f).writerow([row['txn_id'], datetime.now(), 0])
                    st.toast("Exception Logged: Allow-list updated.")

# --- TAB 3: NETWORK ---
with tab_network:
    st.markdown("### 🕸️ Link Analysis Unit")
    
    col_ctrl, col_viz = st.columns([1, 4])
    
    with col_ctrl:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown("**Graph Controls**")
        physics = st.toggle("Physics Engine", value=True)
        st.markdown("---")
        if st.button("⚡ Visualize Topology", type="primary", use_container_width=True):
            st.session_state['gen_graph'] = True
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_viz:
        if st.session_state.get('gen_graph'):
            with st.spinner("Tracing money flow vectors..."):
                # Balanced Sampling
                high_risk = df.sort_values('total_risk', ascending=False).head(20)
                high_amt = df.sort_values('amount', ascending=False).head(10)
                low_risk = df.sort_values('total_risk', ascending=True).head(20)
                random_sample = df.sample(min(20, len(df)))
                sample = pd.concat([high_risk, high_amt, low_risk, random_sample]).drop_duplicates()
                
                # Context
                if 'sel_id' in locals():
                    target = df[df['txn_id'] == sel_id]
                    sample = pd.concat([sample, target]).drop_duplicates()
                
                sample = sample.dropna(subset=['from_acc', 'to_acc'])
                
                # Build Graph
                G = nx.from_pandas_edgelist(sample, 'from_acc', 'to_acc', ['amount'], create_using=nx.DiGraph())
                
                net = Network(height='600px', width='100%', bgcolor='#050505', font_color='white', directed=True)
                
                # Physics Settings
                if physics:
                    net.force_atlas_2based(gravity=-50, central_gravity=0.01, spring_length=100, damping=0.4)
                else:
                    net.barnes_hut()
                
                # Coloring
                risk_map = df.groupby('from_acc')['total_risk'].mean().to_dict()
                node_max_amt = {}
                for u, v, data in G.edges(data=True):
                    amt = data.get('amount', 0)
                    node_max_amt[u] = max(node_max_amt.get(u, 0), amt)
                    node_max_amt[v] = max(node_max_amt.get(v, 0), amt)

                for node in G.nodes():
                    risk = risk_map.get(node, 0.0)
                    amt = node_max_amt.get(node, 0)
                    
                    if risk > 0.6 or amt > 15000:
                        color = "#EF4444" # Red
                        size = 20
                    elif risk > 0.3:
                        color = "#F59E0B" # Orange
                        size = 15
                    else:
                        color = "#10B981" # Green
                        size = 10
                        
                    tooltip = f"Acc: {node} | Risk: {risk:.2f} | Vol: ${amt:,.0f}"
                    net.add_node(str(node), label=str(node), title=tooltip, color=color, size=size)

                for u, v, d in G.edges(data=True):
                    net.add_edge(str(u), str(v), color='#333333')

                # Render
                path = "graph_final.html"
                net.save_graph(path)
                with open(path, 'r', encoding='utf-8') as f:
                    source = f.read()
                components.html(source, height=620, scrolling=False)
        else:
            st.info("Select 'Visualize Topology' to render the account network.")