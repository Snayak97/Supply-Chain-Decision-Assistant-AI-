import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
from dotenv import load_dotenv
import os
load_dotenv(override=True)


# ─── Config ───────────────────────────────────────────────
# API_URL = "http://127.0.0.1:8000/scenario/simulate"
# RESET_URL = "http://127.0.0.1:8000/scenario/reset"

# API_URL = "http://api:8000/scenario/simulate"
# RESET_URL = "http://api:8000/scenario/reset"



BACKEND_URL = os.getenv("BACKEND_URL", "http://api:8000")
API_URL = f"{BACKEND_URL}/scenario/simulate"
RESET_URL = f"{BACKEND_URL}/scenario/reset"
print("BACKEND_URL:", BACKEND_URL)
print("API_URL:", API_URL)
print("RESET_URL:", RESET_URL)

st.set_page_config(
    page_title="SC Decision Assistant",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Custom CSS ───────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main { background-color: #0f1117; }

    .metric-card {
        background: #1a1d27;
        border: 1px solid #2d3148;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 12px;
    }

    .metric-label {
        font-size: 12px;
        font-weight: 500;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 6px;
    }

    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #f9fafb;
        line-height: 1.1;
    }

    .metric-value.negative { color: #f87171; }
    .metric-value.positive { color: #34d399; }
    .metric-value.warning  { color: #fbbf24; }

    .scenario-chip {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #1e2235;
        border: 1px solid #3b4fd8;
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 13px;
        font-weight: 500;
        color: #818cf8;
        margin-right: 8px;
        margin-bottom: 8px;
    }

    .section-title {
        font-size: 16px;
        font-weight: 600;
        color: #e5e7eb;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 1px solid #1f2335;
    }

    .risk-badge-CRITICAL {
        background: #450a0a;
        color: #fca5a5;
        border: 1px solid #7f1d1d;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
    }

    .risk-badge-HIGH {
        background: #431407;
        color: #fdba74;
        border: 1px solid #7c2d12;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
    }

    .core-badge {
        background: #1e1b4b;
        color: #a5b4fc;
        border: 1px solid #3730a3;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 500;
    }

    .rec-card {
        background: #1a1d27;
        border: 1px solid #2d3148;
        border-left: 3px solid #3b4fd8;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 10px;
    }

    .rec-card.HIGH { border-left-color: #f87171; }
    .rec-card.MEDIUM { border-left-color: #fbbf24; }

    .rec-action {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        padding: 2px 8px;
        border-radius: 4px;
        margin-right: 8px;
    }

    .rec-action.buy      { background: #064e3b; color: #6ee7b7; }
    .rec-action.expedite { background: #1e3a5f; color: #93c5fd; }
    .rec-action.cancel   { background: #450a0a; color: #fca5a5; }
    .rec-action.delay    { background: #431407; color: #fdba74; }
    .rec-action.hold     { background: #1f2937; color: #9ca3af; }

    .tool-call-row {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 10px 0;
        border-bottom: 1px solid #1f2335;
    }

    .tool-name {
        font-size: 12px;
        font-weight: 600;
        color: #818cf8;
        min-width: 180px;
        font-family: monospace;
    }

    .tool-result {
        font-size: 12px;
        color: #9ca3af;
        line-height: 1.5;
    }

    .chat-bubble-user {
        background: #1e2235;
        border: 1px solid #2d3148;
        border-radius: 12px 12px 2px 12px;
        padding: 12px 16px;
        font-size: 14px;
        color: #e5e7eb;
        margin-bottom: 8px;
        max-width: 80%;
        margin-left: auto;
    }

    .chat-bubble-assistant {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px 12px 12px 2px;
        padding: 12px 16px;
        font-size: 14px;
        color: #d1d5db;
        margin-bottom: 8px;
        max-width: 80%;
    }

    div[data-testid="stChatMessage"] {
        background: transparent !important;
    }

    .stButton > button {
        background: transparent;
        border: 1px solid #374151;
        color: #9ca3af;
        border-radius: 8px;
        font-size: 13px;
        padding: 6px 16px;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        border-color: #6b7280;
        color: #e5e7eb;
    }

    .stChatInputContainer {
        background: #1a1d27 !important;
        border: 1px solid #2d3148 !important;
        border-radius: 12px !important;
    }

    hr { border-color: #1f2335 !important; }

    # .otb-bar-bg {
    #     background: #1f2937;
    #     border-radius: 4px;
    #     height: 6px;
    #     margin-top: 6px;
    # }

    # .otb-bar-fill {
    #     height: 6px;
    #     border-radius: 4px;
    # }

    .otb-bar-bg {
        width: 100%;
        height: 10px;
        background: #374151;
        border-radius: 10px;
        overflow: hidden;
    }

    .otb-bar-fill {
        height: 100%;
        border-radius: 10px;
    }

</style>
""", unsafe_allow_html=True)


# ─── Session state ────────────────────────────────────────
for key, default in {
    "session_id": None,
    "messages": [],
    "last_result": None,
    "perturbations": []
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ─── Helper functions ─────────────────────────────────────
def fmt_currency(v):
    if abs(v) >= 1_000_000:
        return f"${v/1_000_000:.1f}M"
    if abs(v) >= 1_000:
        return f"${v/1_000:.0f}K"
    return f"${v:.0f}"

def fmt_units(v):
    if abs(v) >= 1_000_000:
        return f"{v/1_000_000:.2f}M"
    if abs(v) >= 1_000:
        return f"{v/1_000:.1f}K"
    return f"{v:.0f}"

def perturbation_label(p):
    ptype = p.get("type")
    if ptype == "shipment_delay":
        return f"⏱ Delay {p.get('delay_days')} days"
    mult = p.get("multiplier", 1)
    pct = (mult - 1) * 100
    sign = "+" if pct > 0 else ""
    name = p.get("channel") or p.get("category") or "Topline"
    return f"{name} {sign}{pct:.0f}%"


# ─── Header ───────────────────────────────────────────────
col_title, col_clear = st.columns([6, 1])
with col_title:
    st.markdown("## Supply Chain Decision Assistant")
    st.caption("Ask forward-looking what-if questions in plain language")

with col_clear:
    if st.session_state.perturbations:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("↺ Clear Scenario"):
            if st.session_state.session_id:
                try:
                    requests.post(f"{RESET_URL}?session_id={st.session_state.session_id}")
                except:
                    pass
            st.session_state.perturbations = []
            st.session_state.last_result = None
            st.session_state.messages = []
            st.rerun()

# ─── Scenario chips ───────────────────────────────────────
if st.session_state.perturbations:
    chips_html = "".join([
        f'<span class="scenario-chip">◆ {perturbation_label(p)}</span>'
        for p in st.session_state.perturbations
    ])
    st.markdown(f'<div style="margin-bottom:16px">{chips_html}</div>', unsafe_allow_html=True)

st.divider()

# ─── Layout: chat left, results right ────────────────────
left, right = st.columns([1, 2], gap="large")

with left:
    st.markdown('<div class="section-title">Scenario Chat</div>', unsafe_allow_html=True)

    # Chat history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-assistant">💬 {msg["content"]}</div>', unsafe_allow_html=True)

    # Example queries
    if not st.session_state.messages:
        st.markdown('<div style="color:#6b7280;font-size:13px;margin-bottom:12px">Try asking:</div>', unsafe_allow_html=True)
        examples = [
            "Reduce DTC demand by 15%",
            "Increase topline by 25%",
            "Apparel demand up 30%",
            "Shipment delay 5 days"
        ]
        for ex in examples:
            if st.button(ex, key=f"ex_{ex}"):
                st.session_state._pending_query = ex
                st.rerun()

    # Chat input
    query = st.chat_input("Ask a what-if question...")

    # Handle example button clicks
    if hasattr(st.session_state, '_pending_query'):
        query = st.session_state._pending_query
        del st.session_state._pending_query

    if query:
        st.session_state.messages.append({"role": "user", "content": query})

        with st.spinner("Running scenario simulation..."):
            try:
                payload = {"query": query}
                if st.session_state.session_id:
                    payload["session_id"] = st.session_state.session_id

                response = requests.post(API_URL, json=payload, timeout=120)
                result = response.json()

                st.session_state.session_id = result["session_id"]
                st.session_state.perturbations = result["perturbations"]
                st.session_state.last_result = result
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["summary"]
                })
            except Exception as e:
                st.error(f"API error: {e}")

        st.rerun()


# ─── Results panel ────────────────────────────────────────
with right:
    if not st.session_state.last_result:
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                    height:400px;color:#374151;text-align:center">
            <div style="font-size:48px;margin-bottom:16px">📊</div>
            <div style="font-size:18px;font-weight:600;color:#6b7280">No scenario running</div>
            <div style="font-size:14px;color:#4b5563;margin-top:8px">
                Ask a what-if question to see results
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        result = st.session_state.last_result
        adj    = result.get("adjusted_forecast", {})
        risk   = result.get("stockout_risk", {})
        otb    = result.get("otb_position", {})
        recs   = result.get("recommendations", {})

        # ── Tabs ──────────────────────────────────────────
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Forecast", "⚠️ Risk", "💰 OTB", "🎯 Recommendations", "🔍 Workings"
        ])

        # ══ TAB 1: FORECAST ══════════════════════════════
        with tab1:
            # KPI row
            change_pct = adj.get("total_change_pct", 0)
            c1, c2, c3 = st.columns(3)

            with c1:
                color = "negative" if change_pct < 0 else "positive"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Forecast Change</div>
                    <div class="metric-value {color}">{change_pct:+.1f}%</div>
                </div>""", unsafe_allow_html=True)

            with c2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Baseline Units</div>
                    <div class="metric-value">{fmt_units(adj.get("original_total_qty", 0))}</div>
                </div>""", unsafe_allow_html=True)

            with c3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Scenario Units</div>
                    <div class="metric-value">{fmt_units(adj.get("adjusted_total_qty", 0))}</div>
                </div>""", unsafe_allow_html=True)

            # Channel chart
            channel_data = adj.get("channel_breakdown", {})
            if channel_data:
                channels = list(channel_data.keys())
                orig_vals = [channel_data[c]["original"] for c in channels]
                adj_vals  = [channel_data[c]["adjusted"] for c in channels]

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name="Baseline", x=channels, y=orig_vals,
                    marker_color="#3b4fd8", marker_opacity=0.8
                ))
                fig.add_trace(go.Bar(
                    name="Scenario", x=channels, y=adj_vals,
                    marker_color="#818cf8"
                ))
                fig.update_layout(
                    barmode="group",
                    title=dict(text="Channel Breakdown", font=dict(color="#e5e7eb", size=14)),
                    plot_bgcolor="#0f1117",
                    paper_bgcolor="#0f1117",
                    font=dict(color="#9ca3af"),
                    legend=dict(bgcolor="#1a1d27", bordercolor="#2d3148"),
                    height=260,
                    margin=dict(l=0, r=0, t=40, b=0),
                    xaxis=dict(gridcolor="#1f2335"),
                    yaxis=dict(gridcolor="#1f2335")
                )
                st.plotly_chart(fig, use_container_width=True)

            # Category chart
            cat_data = adj.get("category_breakdown", {})
            if cat_data:
                cats = list(cat_data.keys())
                orig_vals = [cat_data[c]["original"] for c in cats]
                adj_vals  = [cat_data[c]["adjusted"] for c in cats]

                fig2 = go.Figure()
                fig2.add_trace(go.Bar(
                    name="Baseline", x=cats, y=orig_vals,
                    marker_color="#0d9488", marker_opacity=0.8
                ))
                fig2.add_trace(go.Bar(
                    name="Scenario", x=cats, y=adj_vals,
                    marker_color="#2dd4bf"
                ))
                fig2.update_layout(
                    barmode="group",
                    title=dict(text="Category Breakdown", font=dict(color="#e5e7eb", size=14)),
                    plot_bgcolor="#0f1117",
                    paper_bgcolor="#0f1117",
                    font=dict(color="#9ca3af"),
                    legend=dict(bgcolor="#1a1d27", bordercolor="#2d3148"),
                    height=260,
                    margin=dict(l=0, r=0, t=40, b=0),
                    xaxis=dict(gridcolor="#1f2335"),
                    yaxis=dict(gridcolor="#1f2335")
                )
                st.plotly_chart(fig2, use_container_width=True)

        # ══ TAB 2: RISK ══════════════════════════════════
        with tab2:
            c1, c2, c3 = st.columns(3)

            with c1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">SKUs at Risk</div>
                    <div class="metric-value warning">{risk.get("sku_count_at_risk", 0)}</div>
                </div>""", unsafe_allow_html=True)

            with c2:
                rev = risk.get("total_revenue_at_risk", 0)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Revenue at Risk</div>
                    <div class="metric-value negative">{fmt_currency(rev)}</div>
                </div>""", unsafe_allow_html=True)

            with c3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Core SKUs at Risk</div>
                    <div class="metric-value warning">{risk.get("core_sku_count_at_risk", 0)}</div>
                </div>""", unsafe_allow_html=True)

            # Risk by category chart
            cat_risk = risk.get("category_breakdown", {})
            if cat_risk:
                cats = list(cat_risk.keys())
                revs = [cat_risk[c]["revenue_at_risk"] for c in cats]
                skus = [cat_risk[c]["sku_count"] for c in cats]

                fig3 = go.Figure()
                fig3.add_trace(go.Bar(
                    name="Revenue at Risk ($)",
                    x=cats, y=revs,
                    marker_color="#f87171",
                    yaxis="y"
                ))
                fig3.add_trace(go.Scatter(
                    name="SKU Count",
                    x=cats, y=skus,
                    mode="markers+lines",
                    marker=dict(color="#fbbf24", size=10),
                    line=dict(color="#fbbf24"),
                    yaxis="y2"
                ))
                fig3.update_layout(
                    title=dict(text="Risk by Category", font=dict(color="#e5e7eb", size=14)),
                    plot_bgcolor="#0f1117",
                    paper_bgcolor="#0f1117",
                    font=dict(color="#9ca3af"),
                    height=260,
                    margin=dict(l=0, r=0, t=40, b=0),
                    xaxis=dict(gridcolor="#1f2335"),
                    yaxis=dict(gridcolor="#1f2335", title="Revenue at Risk"),
                    yaxis2=dict(overlaying="y", side="right", title="SKU Count"),
                    legend=dict(bgcolor="#1a1d27", bordercolor="#2d3148")
                )
                st.plotly_chart(fig3, use_container_width=True)

            # SKU table
            at_risk = risk.get("at_risk_skus", [])
            if at_risk:
                st.markdown('<div class="section-title">Top At-Risk SKUs</div>', unsafe_allow_html=True)
                df = pd.DataFrame(at_risk)
                df = df[["sku_id", "category", "channel", "is_core", "risk_level",
                          "stockout_probability", "revenue_at_risk", "net_available_qty"]]
                df["stockout_probability"] = df["stockout_probability"].apply(lambda x: f"{x:.1%}")
                df["revenue_at_risk"]      = df["revenue_at_risk"].apply(lambda x: fmt_currency(x))
                df["net_available_qty"]    = df["net_available_qty"].apply(lambda x: f"{x:,.0f}")
                df["is_core"]              = df["is_core"].apply(lambda x: "★ Core" if x else "")
                df.columns = ["SKU", "Category", "Channel", "Core", "Risk", "Stockout %", "Revenue at Risk", "Inventory"]
                st.dataframe(df, use_container_width=True, hide_index=True)

        # ══ TAB 3: OTB ═══════════════════════════════════
#         with tab3:
#             c1, c2, c3 = st.columns(3)

#             avail = otb.get("total_available", 0)
#             avail_color = "negative" if avail < 0 else "positive"

#             with c1:
#                 st.markdown(f"""
#                 <div class="metric-card">
#                     <div class="metric-label">Total Budget</div>
#                     <div class="metric-value">{fmt_currency(otb.get("total_budget", 0))}</div>
#                 </div>""", unsafe_allow_html=True)

#             with c2:
#                 st.markdown(f"""
#                 <div class="metric-card">
#                     <div class="metric-label">Committed Spend</div>
#                     <div class="metric-value warning">{fmt_currency(otb.get("total_committed", 0))}</div>
#                 </div>""", unsafe_allow_html=True)

#             with c3:
#                 st.markdown(f"""
#                 <div class="metric-card">
#                     <div class="metric-label">Available OTB</div>
#                     <div class="metric-value {avail_color}">{fmt_currency(avail)}</div>
#                 </div>""", unsafe_allow_html=True)

#             # OTB by category
#             cat_positions = otb.get("category_positions", [])
#             if cat_positions:
#                 st.markdown('<div class="section-title" style="margin-top:16px">OTB by Category & Period</div>', unsafe_allow_html=True)
# #                 for pos in cat_positions:
# #                     util = pos.get("utilization_pct", 0)
# #                     over = pos.get("is_overcommitted", False)
# #                     bar_color = "#f87171" if over else "#34d399"
# #                     bar_width = min(util, 200)
# #                     label_color = "#f87171" if over else "#34d399"

# #                     st.markdown(f"""
# #                     <div class="metric-card" style="padding:14px 20px;margin-bottom:8px">
# #                         <div style="display:flex;justify-content:space-between;align-items:center">
# #                             <div>
# #                                 <span style="font-weight:600;color:#e5e7eb">{pos['category']}</span>
# #                                 <span style="color:#6b7280;font-size:12px;margin-left:8px">{pos['period']}</span>
# #                                 {"<span style='color:#f87171;font-size:11px;margin-left:8px;font-weight:600'>● OVERCOMMITTED</span>" if over else ""}
# #                             </div>
# #                             <div style="color:{label_color};font-weight:700;font-size:15px">{util:.1f}%</div>
# #                         </div>
# #                         <div style="display:flex;justify-content:space-between;margin-top:8px;font-size:12px;color:#6b7280">
# #                             <span>Budget: {fmt_currency(pos['budget'])}</span>
# #                             <span>Committed: {fmt_currency(pos['committed_spend'])}</span>
# #                             <span>Available: {fmt_currency(pos['available_otb'])}</span>
# #                         </div>
# #                         <div class="otb-bar-bg">
# #                             <div class="otb-bar-fill" style="width:{bar_width}%;background:{bar_color}"></div>
# #                         </div>
# #                     </div>
# #                     """, unsafe_allow_html=True)
# # # 
#                 for pos in cat_positions:
#                     util = pos.get("utilization_pct", 0)
#                     over = pos.get("is_overcommitted", False)
#                     bar_color = "#f87171" if over else "#34d399"
#                     bar_width = min(util, 100)
#                     label_color = "#f87171" if over else "#34d399"
#                     overcommit_badge = "<span style='color:#f87171;font-size:11px;margin-left:8px;font-weight:600'>● OVERCOMMITTED</span>" if over else ""

#                     st.markdown(f"""
#     <div class="metric-card" style="padding:14px 20px;margin-bottom:8px">
#         <div style="display:flex;justify-content:space-between;align-items:center">
#             <div>
#                 <span style="font-weight:600;color:#e5e7eb">{pos['category']}</span>
#                 <span style="color:#6b7280;font-size:12px;margin-left:8px">{pos['period']}</span>
#                 {overcommit_badge}
#             </div>
#             <div style="color:{label_color};font-weight:700;font-size:15px">{util:.1f}%</div>
#         </div>
#         <div style="display:flex;justify-content:space-between;margin-top:8px;font-size:12px;color:#6b7280">
#             <span>Budget: {fmt_currency(pos['budget'])}</span>
#             <span>Committed: {fmt_currency(pos['committed_spend'])}</span>
#             <span>Available: {fmt_currency(pos['available_otb'])}</span>
#         </div>
#         <div class="otb-bar-bg">
#             <div class="otb-bar-fill" style="width:{bar_width}%;background:{bar_color}"></div>
#         </div>
#     </div>
#     """, unsafe_allow_html=True)

        # ══ TAB 3: OTB ═══════════════════════════════════
        with tab3:
            avail = otb.get("total_available", 0)

            # KPI row
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric(
                    label="Total Budget",
                    value=fmt_currency(otb.get("total_budget", 0))
                )
            with c2:
                st.metric(
                    label="Committed Spend",
                    value=fmt_currency(otb.get("total_committed", 0))
                )
            with c3:
                st.metric(
                    label="Available OTB",
                    value=fmt_currency(avail),
                    delta=f"{'Overcommitted' if avail < 0 else 'Available'}",
                    delta_color="inverse" if avail < 0 else "normal"
                )

            st.markdown("---")

            # Summary warning
            overcommitted = list(set(otb.get("overcommitted_categories", [])))
            if overcommitted:
                st.error(f"⚠️ Overcommitted categories: {', '.join(overcommitted)} — Total overcommit: {fmt_currency(otb.get('total_overcommit_amount', 0))}")

            additional = otb.get("additional_commitment_required", 0)
            if additional > 0:
                st.warning(f"📦 Scenario requires {fmt_currency(additional)} additional commitment")
            elif additional < 0:
                st.success(f"💰 Scenario releases {fmt_currency(abs(additional))} from commitment")

            st.markdown("---")

            # OTB by category and period
            st.markdown("### OTB by Category & Period")

            cat_positions = otb.get("category_positions", [])
            if cat_positions:
                for pos in cat_positions:
                    util  = pos.get("utilization_pct", 0)
                    over  = pos.get("is_overcommitted", False)
                    avail_pos = pos.get("available_otb", 0)

                    # Card header
                    col_a, col_b, col_c = st.columns([2, 1, 1])
                    with col_a:
                        if over:
                            st.markdown(f"🔴 **{pos['category']}** `{pos['period']}`")
                        else:
                            st.markdown(f"✅ **{pos['category']}** `{pos['period']}`")
                    with col_b:
                        st.markdown(f"Utilization: **{util:.1f}%**")
                    with col_c:
                        if over:
                            st.markdown(f"Overcommit: **{fmt_currency(pos.get('overcommit_amount', 0))}**")
                        else:
                            st.markdown(f"Available: **{fmt_currency(avail_pos)}**")

                    # Metrics row
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Budget",    fmt_currency(pos["budget"]))
                    m2.metric("Committed", fmt_currency(pos["committed_spend"]))
                    m3.metric("Available", fmt_currency(avail_pos))

                    # Progress bar
                    progress_val = min(int(util), 100)
                    st.progress(progress_val)

                    st.markdown("---")

        # ══ TAB 4: RECOMMENDATIONS ════════════════════════
        with tab4:
            c1, c2, c3 = st.columns(3)

            with c1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total Cost</div>
                    <div class="metric-value negative">{fmt_currency(recs.get("total_cost", 0))}</div>
                </div>""", unsafe_allow_html=True)

            with c2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Revenue Protected</div>
                    <div class="metric-value positive">{fmt_currency(recs.get("total_revenue_protected", 0))}</div>
                </div>""", unsafe_allow_html=True)

            with c3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Cash Released</div>
                    <div class="metric-value positive">{fmt_currency(recs.get("total_cash_released", 0))}</div>
                </div>""", unsafe_allow_html=True)

            rec_list = recs.get("recommendations", [])
            if rec_list:
                st.markdown('<div class="section-title" style="margin-top:16px">Action Plan</div>', unsafe_allow_html=True)
                for i, rec in enumerate(rec_list):
                    action   = rec.get("action_type", "hold")
                    priority = rec.get("priority", "MEDIUM")
                    desc     = rec.get("description", "")
                    rationale= rec.get("rationale", "")
                    cost     = rec.get("cost", 0)
                    rev_prot = rec.get("revenue_protected", 0)
                    conf     = rec.get("confidence", 0)
                    caveats  = rec.get("caveats", [])

                    with st.expander(f"{desc}", expanded=False):
                        col_a, col_b, col_c = st.columns(3)
                        col_a.metric("Cost", fmt_currency(cost))
                        col_b.metric("Revenue Protected", fmt_currency(rev_prot))
                        col_c.metric("Confidence", f"{conf:.0%}")

                        st.markdown(f"**Rationale:** {rationale}")

                        if caveats:
                            for c in caveats:
                                st.caption(f"⚠️ {c}")

        # ══ TAB 5: SHOW YOUR WORK ════════════════════════
        with tab5:
            st.markdown('<div class="section-title">Tool Execution Trace</div>', unsafe_allow_html=True)
            tool_calls = result.get("tool_calls", [])
            for i, tc in enumerate(tool_calls):
                st.markdown(f"""
                <div class="tool-call-row">
                    <div class="tool-name">{i+1}. {tc['tool']}</div>
                    <div class="tool-result">{tc['result']}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('<div class="section-title" style="margin-top:20px">Raw Perturbations</div>', unsafe_allow_html=True)
            for p in result.get("perturbations", []):
                st.json(p)


# import subprocess
# import sys

# if __name__ == "__main__":
#     subprocess.run([
#         sys.executable,
#         "-m",
#         "streamlit",
#         "run",
#         "test_ui.py",
#         "--server.address=0.0.0.0",
#         "--server.port=8501"
#     ])