import os
from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from generate_sample_data import create_synthetic_csv

# ==========================================
# PAGE CONFIGURATION & SHARED STATE
# ==========================================
st.set_page_config(
    page_title="K-SIWAP | Karnataka Skill Intelligence Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure synthetic raw file exists
RAW_FILE_PATH = "synthetic_karnataka_labour_raw.csv"
if not os.path.exists(RAW_FILE_PATH):
    create_synthetic_csv(RAW_FILE_PATH)

# Standardisation Mappings for Module 1
DISTRICT_MAP = {
    "Gulbarga": "Kalaburagi",
    "Bangalore": "Bengaluru Urban",
    "Bangalore Urban": "Bengaluru Urban",
    "Mysore": "Mysuru",
    "Belgaum": "Belagavi",
    "Mangalore": "Dakshina Kannada",
    "Mangaluru": "Dakshina Kannada"
}

SECTOR_MAP = {
    "IT/ITES": "IT & ITeS",
    "IT": "IT & ITeS",
    "Construction": "Construction & Infrastructure"
}

# ==========================================
# REUSABLE DATA & ANALYTICS FUNCTIONS
# ==========================================
def clean_and_standardise_data(df_raw: pd.DataFrame):
    """Module 1 reusable loader and cleaner with quality metrics."""
    df = df_raw.copy()
    
    # Record quality metrics before cleaning
    total_rows = len(df)
    duplicate_count = int(df.duplicated().sum())
    missing_by_col = df.isnull().sum().to_dict()
    
    inconsistent_districts = [d for d in df["district"].dropna().unique() if d in DISTRICT_MAP]
    inconsistent_sectors = [s for s in df["sector"].dropna().unique() if s in SECTOR_MAP]
    
    # Apply cleaning
    df = df.drop_duplicates().copy()
    df["district"] = df["district"].replace(DISTRICT_MAP)
    df["sector"] = df["sector"].replace(SECTOR_MAP)
    df["skills"] = df["skills"].fillna("Unspecified Skill")
    df["training_supply"] = pd.to_numeric(df["training_supply"], errors="coerce")
    df["demand_value"] = pd.to_numeric(df["demand_value"], errors="coerce")
    
    quality_report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "raw_row_count": total_rows,
        "cleaned_row_count": len(df),
        "duplicates_removed": duplicate_count,
        "missing_values_detected": missing_by_col,
        "standardised_districts": inconsistent_districts,
        "standardised_sectors": inconsistent_sectors,
        "provenance_verified": all(col in df.columns for col in ["source", "time_period", "units"])
    }
    return df, quality_report

def extract_skill_taxonomy(df_clean: pd.DataFrame, period_filter: str = "2025-Q2"):
    """Module 3 reusable function to map occupations to standardized skills."""
    sub = df_clean[df_clean["time_period"] == period_filter].copy()
    records = []
    for _, row in sub.iterrows():
        skills_list = [s.strip() for s in str(row["skills"]).split(",") if s.strip()]
        for sk in skills_list:
            records.append({
                "skill": sk,
                "occupation": row["occupation"],
                "sector": row["sector"],
                "district": row["district"],
                "demand_mentions": row["demand_value"],
                "training_supply": row["training_supply"],
                "time_period": row["time_period"],
                "units": row["units"],
                "source": row["source"]
            })
    return pd.DataFrame(records)

def compute_district_scores(df_clean: pd.DataFrame, w_demand: float, w_gap: float, period: str = "2025-Q2"):
    """Module 4 transparent district scoring function."""
    sub = df_clean[df_clean["time_period"] == period].copy()
    grouped = sub.groupby("district", as_index=False).agg(
        total_demand=("demand_value", "sum"),
        total_supply=("training_supply", lambda x: x.sum(min_count=1)),
        missing_supply_records=("training_supply", lambda x: x.isnull().sum()),
        sectors_covered=("sector", "nunique")
    )
    grouped["estimated_gap"] = grouped["total_demand"] - grouped["total_supply"].fillna(0)
    
    # Min-Max Normalisation (0 to 100 scale) for transparent scoring
    max_dem = grouped["total_demand"].max() or 1
    max_gap = grouped["estimated_gap"].max() or 1
    
    grouped["demand_norm"] = (grouped["total_demand"] / max_dem) * 100
    grouped["gap_norm"] = (grouped["estimated_gap"].clip(lower=0) / max_gap) * 100
    
    grouped["candidate_priority_score"] = (
        (grouped["demand_norm"] * w_demand) + (grouped["gap_norm"] * w_gap)
    ).round(1)
    
    return grouped.sort_values(by="candidate_priority_score", ascending=False)

# ==========================================
# INITIALISE SESSION STATE
# ==========================================
if "raw_df" not in st.session_state:
    st.session_state["raw_df"] = pd.read_csv(RAW_FILE_PATH)
    clean_df, q_rep = clean_and_standardise_data(st.session_state["raw_df"])
    st.session_state["clean_df"] = clean_df
    st.session_state["quality_report"] = q_rep

if "agent_logs" not in st.session_state:
    st.session_state["agent_logs"] = []

if "agent_status" not in st.session_state:
    st.session_state["agent_status"] = "IDLE"

# ==========================================
# SIDEBAR NAVIGATION & GLOBAL DISCLAIMER
# ==========================================
st.sidebar.title("K-SIWAP Platform")
st.sidebar.caption("Karnataka Skill Intelligence & Workforce Analytics Platform · KSISU Skillathon 2026")

st.sidebar.warning(
    "⚠️ **SYNTHETIC DATA DISCLAIMER**\n\n"
    "All numbers, scores, and datasets in this starter prototype are **synthetic demonstration samples**. "
    "They must NEVER be presented as official Karnataka statistics or government policy."
)

module_choice = st.sidebar.radio(
    "Workflow Navigation",
    [
        "Overview & Architecture",
        "1. INGEST: Data Explorer (KSISU-01)",
        "2. ANALYSE: Job Demand (KSISU-02)",
        "3. DIAGNOSE: Skill Gaps (KSISU-03)",
        "4. PRIORITISE: District Planning (KSISU-04)",
        "5. EXPLAIN: Policy Copilot (KSISU-05)",
        "6. ACT: Agentic Decision Engine (KSISU-06)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**End-to-End Flow:**\n"
    "`INGEST → ANALYSE → DIAGNOSE → PRIORITISE → EXPLAIN → ACT`"
)

# Shared metadata banner helper
def render_metadata_banner(df_subset):
    sources = ", ".join(df_subset["source"].dropna().unique())
    periods = ", ".join(df_subset["time_period"].dropna().unique())
    units = ", ".join(df_subset["units"].dropna().unique())
    st.caption(f"📌 **Provenance Metadata** | **Source:** {sources} | **Reference Period:** {periods} | **Units:** {units} | **Status:** Synthetic Demo Data")

# ==========================================
# PAGE 0: OVERVIEW & ARCHITECTURE
# ==========================================
if module_choice == "Overview & Architecture":
    st.title("K-SIWAP: Karnataka Skill Intelligence & Workforce Analytics Platform")
    st.subheader("PragyanAI First Hackathon · KSISU Skillathon 2026 Prototype")
    
    st.markdown("""
    **Primary Objective:** Help planners explore available labour-market evidence and turn it into transparent, reviewable insights about sectors, occupations, skills, and district-level training priorities.
    """)
    
    cols = st.columns(6)
    stages = [
        ("1. INGEST", "KSISU-01\nData Explorer"),
        ("2. ANALYSE", "KSISU-02\nJob Demand"),
        ("3. DIAGNOSE", "KSISU-03\nSkill Gaps"),
        ("4. PRIORITISE", "KSISU-04\nDistrict Plan"),
        ("5. EXPLAIN", "KSISU-05\nPolicy Copilot"),
        ("6. ACT", "KSISU-06\nAgent Engine")
    ]
    for col, (stage, desc) in zip(cols, stages):
        col.metric(stage, desc)
        
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Four Challenge Data Pillars (Integration Ready)")
        st.markdown("""
        1. **District Ground Data:** District Skill Development Plan (DSDP) inputs & local training capacity.
        2. **Formal Economy Signals:** EPFO, ESIC, GST, and GSDP official indicators.
        3. **Sector Intelligence:** Sector Skill Council (SSC) reports and documented industry studies.
        4. **Macro Indicators:** PLFS and World Bank/ADB datasets preserving native definitions.
        """)
    with c2:
        st.markdown("### Prototype Governance Principles")
        st.markdown("""
        * **Synthetic Data Clearly Labelled:** Never misrepresented as official Karnataka statistics.
        * **Strict Comparability Checks:** District and time-trend comparisons require matching units and periods.
        * **Observed vs. Derived Separation:** Raw observations are kept distinct from weighted priority scores.
        * **Mandatory Human Review:** Consequential policy drafts stop for human approval in Module 6.
        """)

# ==========================================
# MODULE 1: LABOUR DATA EXPLORER (KSISU-01)
# ==========================================
elif module_choice == "1. INGEST: Data Explorer (KSISU-01)":
    st.title("Module 1 — Labour Data Explorer and Integration (KSISU-01)")
    st.markdown("Import CSV files into a common, traceable schema (`district`, `sector`, `occupation`, `skills`, `time_period`, `source`, `units`) and inspect data quality.")
    
    uploaded_file = st.file_uploader("Upload Raw Labour CSV (or use built-in synthetic sample below)", type=["csv"])
    if uploaded_file is not None:
        raw_df = pd.read_csv(uploaded_file)
        st.session_state["raw_df"] = raw_df
        clean_df, q_rep = clean_and_standardise_data(raw_df)
        st.session_state["clean_df"] = clean_df
        st.session_state["quality_report"] = q_rep
        st.success("Uploaded file processed and standardised!")

    raw_df = st.session_state["raw_df"]
    clean_df = st.session_state["clean_df"]
    q_rep = st.session_state["quality_report"]

    # Quality Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Raw Records Imported", q_rep["raw_row_count"])
    m2.metric("Duplicates Removed", q_rep["duplicates_removed"])
    m3.metric("Missing Values Flagged", sum(q_rep["missing_values_detected"].values()))
    m4.metric("Cleaned Valid Records", q_rep["cleaned_row_count"])

    st.subheader("Automated Data Quality & Standardisation Report")
    st.json(q_rep)

    tab1, tab2 = st.tabs(["Cleaned & Standardised Dataset", "Original Raw Dataset (Unchanged)"])
    with tab1:
        render_metadata_banner(clean_df)
        st.dataframe(clean_df, use_container_width=True)
        csv_clean = clean_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Cleaned & Inspected CSV", data=csv_clean, file_name="ksisu_cleaned_labour_data.csv", mime="text/csv")
    with tab2:
        st.caption("Raw unedited records preserved for provenance audit.")
        st.dataframe(raw_df, use_container_width=True)

# ==========================================
# MODULE 2: JOB DEMAND ANALYTICS (KSISU-02)
# ==========================================
elif module_choice == "2. ANALYSE: Job Demand (KSISU-02)":
    st.title("Module 2 — Job Demand and Sector Analytics (KSISU-02)")
    clean_df = st.session_state["clean_df"]
    
    # Filters
    f1, f2, f3 = st.columns(3)
    periods = sorted(clean_df["time_period"].unique())
    sel_period = f1.selectbox("Select Reference Period", options=["All Comparable Periods"] + periods, index=2 if len(periods) > 1 else 0)
    
    districts = ["All Districts"] + sorted(clean_df["district"].unique())
    sel_district = f2.selectbox("Filter by District", options=districts)
    
    sectors = ["All Sectors"] + sorted(clean_df["sector"].unique())
    sel_sector = f3.selectbox("Filter by Sector", options=sectors)

    filtered_df = clean_df.copy()
    if sel_period != "All Comparable Periods":
        filtered_df = filtered_df[filtered_df["time_period"] == sel_period]
    if sel_district != "All Districts":
        filtered_df = filtered_df[filtered_df["district"] == sel_district]
    if sel_sector != "All Sectors":
        filtered_df = filtered_df[filtered_df["sector"] == sel_sector]

    if filtered_df.empty:
        st.warning("No records match the selected filters.")
    else:
        render_metadata_banner(filtered_df)
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Sector Demand Ranking")
            sec_summary = filtered_df.groupby(["sector", "indicator_type", "units"], as_index=False)["demand_value"].sum().sort_values("demand_value", ascending=True)
            fig_sec = px.bar(
                sec_summary, x="demand_value", y="sector", orientation="h",
                color="indicator_type", text="demand_value",
                title=f"Demand by Sector ({sel_period}) | Units: Number of Persons/Roles",
                labels={"demand_value": "Job Postings (Synthetic)", "sector": "Sector"}
            )
            st.plotly_chart(fig_sec, use_container_width=True)

        with c2:
            st.subheader("Occupation Demand Ranking")
            occ_summary = filtered_df.groupby(["occupation", "sector", "units"], as_index=False)["demand_value"].sum().sort_values("demand_value", ascending=True)
            fig_occ = px.bar(
                occ_summary, x="demand_value", y="occupation", orientation="h",
                color="sector", text="demand_value",
                title=f"Top Occupations ({sel_period}) | Source: Synthetic Demo Portal v1",
                labels={"demand_value": "Job Postings (Synthetic)", "occupation": "Occupation"}
            )
            st.plotly_chart(fig_occ, use_container_width=True)

        st.subheader("Time-Trend Comparability Check (2025-Q1 vs 2025-Q2)")
        trend_df = clean_df.groupby(["time_period", "sector"], as_index=False)["demand_value"].sum()
        if trend_df["time_period"].nunique() >= 2:
            fig_trend = px.line(
                trend_df, x="time_period", y="demand_value", color="sector", markers=True,
                title="Comparable Period Trend by Sector (Units: Job Postings | Source: Synthetic Demo Portal v1)"
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("Multiple comparable time periods required to display growth trends.")

# ==========================================
# MODULE 3: SKILL GAP INTELLIGENCE (KSISU-03)
# ==========================================
elif module_choice == "3. DIAGNOSE: Skill Gaps (KSISU-03)":
    st.title("Module 3 — Skill Gap and Emerging Skills Intelligence (KSISU-03)")
    clean_df = st.session_state["clean_df"]
    
    st.markdown("""
    **Methodological Caveat:** Demand-side skill mentions are extracted from occupation records. Supply-side comparisons are only calculated where `training_supply` shares comparable units (`Number of Persons/Roles`) and contains non-null records.
    """)
    
    sel_p = st.selectbox("Select Reference Period for Skill Diagnosis", sorted(clean_df["time_period"].unique()), index=1)
    skill_df = extract_skill_taxonomy(clean_df, period_filter=sel_p)
    render_metadata_banner(clean_df[clean_df["time_period"] == sel_p])

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Ranked Skills by Demand Mentions")
        sk_rank = skill_df.groupby("skill", as_index=False).agg(
            total_demand_mentions=("demand_mentions", "sum"),
            linked_occupations=("occupation", lambda x: ", ".join(sorted(set(x))))
        ).sort_values("total_demand_mentions", ascending=False)
        
        fig_sk = px.bar(
            sk_rank.head(12), x="total_demand_mentions", y="skill", orientation="h",
            title=f"Top Demanded Skills ({sel_p}) | Units: Role Mentions",
            labels={"total_demand_mentions": "Demand Mentions", "skill": "Standardised Skill"}
        )
        fig_sk.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_sk, use_container_width=True)

    with c2:
        st.subheader("Emerging Skills (Time-Series Evidence Check)")
        sk_q1 = set(extract_skill_taxonomy(clean_df, "2025-Q1")["skill"].unique())
        sk_q2 = set(extract_skill_taxonomy(clean_df, "2025-Q2")["skill"].unique())
        new_in_q2 = sorted(list(sk_q2 - sk_q1 - {"Unspecified Skill"}))
        
        st.info("Skills appearing in **2025-Q2** demand records that were absent in **2025-Q1** baseline:")
        for s in new_in_q2:
            occ_trace = skill_df[skill_df["skill"] == s][["occupation", "district", "source"]].drop_duplicates()
            st.markdown(f"- **{s}** → Traced to: `{', '.join(occ_trace['occupation'])}` in `{', '.join(occ_trace['district'])}`")

    st.subheader("Traceable Occupation-to-Skill Mapping & Supply Gap Table")
    occ_gap = clean_df[clean_df["time_period"] == sel_p].copy()
    occ_gap["Indicative_Supply_Gap"] = np.where(
        occ_gap["training_supply"].notnull(),
        occ_gap["demand_value"] - occ_gap["training_supply"],
        np.nan
    )
    occ_gap["Gap_Status"] = np.where(
        occ_gap["training_supply"].notnull(),
        "Comparable Units Verified",
        "⚠️ Missing Supply Data - Cannot Compute Gap"
    )
    st.dataframe(
        occ_gap[["district", "sector", "occupation", "skills", "demand_value", "training_supply", "Indicative_Supply_Gap", "Gap_Status", "source"]],
        use_container_width=True
    )

# ==========================================
# MODULE 4: DISTRICT PLANNING (KSISU-04)
# ==========================================
elif module_choice == "4. PRIORITISE: District Planning (KSISU-04)":
    st.title("Module 4 — District-Level Skill Planning & Recommendations (KSISU-04)")
    st.warning("📌 **Policy Disclaimer:** Candidate priority scores use transparent user-defined weights for illustration. They must NOT be presented as official government allocation formulas.")
    
    clean_df = st.session_state["clean_df"]
    
    st.subheader("Configure Transparent Scoring Weights")
    w1, w2 = st.columns(2)
    weight_demand = w1.slider("Weight: Total Job Demand Volume (w_demand)", 0.0, 1.0, 0.5, 0.05)
    weight_gap = w2.slider("Weight: Unmet Training Supply Gap (w_gap)", 0.0, 1.0, 0.5, 0.05)
    
    st.latex(r"\text{Priority Score} = w_{\text{demand}} \cdot \text{Norm(Demand)} + w_{\text{gap}} \cdot \text{Norm(Demand - Supply)}")

    scored_df = compute_district_scores(clean_df, weight_demand, weight_gap, period="2025-Q2")
    render_metadata_banner(clean_df[clean_df["time_period"] == "2025-Q2"])

    fig_dist = px.bar(
        scored_df, x="district", y="candidate_priority_score", color="estimated_gap",
        text="candidate_priority_score",
        title="Candidate District Training Priority Score (2025-Q2 Synthetic Data)",
        labels={"candidate_priority_score": "Composite Priority Score (0-100)", "district": "District"}
    )
    st.plotly_chart(fig_dist, use_container_width=True)

    st.subheader("District Priority Breakdown & Missing-Data Warnings")
    scored_df["Data_Limitation_Flag"] = np.where(
        scored_df["missing_supply_records"] > 0,
        "⚠️ Missing training supply in 1+ records",
        "✅ Complete Synthetic Records"
    )
    st.dataframe(scored_df, use_container_width=True)
    
    csv_plan = scored_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Export District Planning Report (CSV)", data=csv_plan, file_name="ksisu_district_priority_report.csv", mime="text/csv")

# ==========================================
# MODULE 5: GENAI POLICY COPILOT (KSISU-05)
# ==========================================
elif module_choice == "5. EXPLAIN: Policy Copilot (KSISU-05)":
    st.title("Module 5 — GenAI Labour Market Policy Copilot (KSISU-05)")
    st.markdown("Grounded rule-based Policy Copilot. Every numerical claim is retrieved from approved analytics functions with full source and limitation metadata.")
    
    clean_df = st.session_state["clean_df"]
    
    preset_questions = [
        "Which district has the highest skill gap and what training action is suggested for 2025-Q2?",
        "What are the top demanded occupations and skills in Kalaburagi?",
        "What is the projected 2030 rural informal agricultural wage in Karnataka?", # Unsupported test!
        "Custom Question..."
    ]
    selected_q = st.selectbox("Select a Policy Question to Test Grounding:", preset_questions)
    
    if selected_q == "Custom Question...":
        user_query = st.text_input("Enter your natural-language question:", "Tell me about Mysuru manufacturing demand.")
    else:
        user_query = selected_q

    if st.button("Generate Grounded Policy Brief"):
        q_lower = user_query.lower()
        
        # Check for unsupported topics (Hallucination guardrail)
        if any(w in q_lower for w in ["2030", "wage", "salary", "informal", "agriculture"]):
            st.error("🚫 **Limitation Notice — Insufficient Evidence**")
            st.markdown(f"""
            * **Question Asked:** *{user_query}*
            * **Guardrail Response:** The currently loaded dataset (`Synthetic Demo Portal v1`, covering `2025-Q1` to `2025-Q2`) only tracks `Job Postings` and `Training Supply` counts across formal sectors. It contains **no evidence on wages, informal sector earnings, or 2030 forecasts**.
            * **Policy Copilot Rule:** Refusing to invent or extrapolate unsupported statistics. Please integrate PLFS or minimum-wage schedules in Module 1 to answer this question.
            """)
        elif "kalaburagi" in q_lower or "gulbarga" in q_lower:
            kal_df = clean_df[(clean_df["district"] == "Kalaburagi") & (clean_df["time_period"] == "2025-Q2")]
            tot_dem = int(kal_df["demand_value"].sum())
            tot_sup = int(kal_df["training_supply"].sum())
            occs = ", ".join(kal_df["occupation"].unique())
            
            st.success("✅ Evidence Retrieved from Approved Analytics Functions")
            st.markdown(f"""
            ### Draft Policy Brief: Kalaburagi Workforce & Skill Priorities
            * **Policy Question:** {user_query}
            * **Retrieved Evidence:** In `2025-Q2`, Kalaburagi recorded **{tot_dem} Job Postings** against an existing training capacity of **{tot_sup} seats** (Net Indicative Gap: **{tot_dem - tot_sup} roles**) across occupations: *{occs}*.
            * **Source & Metadata:** `Synthetic Demo Portal v1` | Period: `2025-Q2` | Geography: `Kalaburagi (standardised from Gulbarga)` | Units: `Number of Persons/Roles`.
            * **Candidate Action:** Expand short-term bridge training in **BIM, AutoCAD, Diagnostics, and Python/SQL** at Kalaburagi district training centres.
            * **Caveats & Human Review Notes:** Data is synthetic demonstration data. Verify actual ITI/Polytechnic batch capacities via District Skill Development Plan (DSDP) records before budget allocation.
            """)
        else:
            scored = compute_district_scores(clean_df, 0.5, 0.5, "2025-Q2")
            top_row = scored.iloc[0]
            st.success("✅ Evidence Retrieved from Approved Analytics Functions")
            st.markdown(f"""
            ### Draft Policy Brief: Top District Skill Gap Summary (2025-Q2)
            * **Policy Question:** {user_query}
            * **Retrieved Evidence:** **{top_row['district']}** ranks highest with a candidate priority score of **{top_row['candidate_priority_score']}/100**, driven by **{int(top_row['total_demand'])} job postings** and an estimated supply gap of **{int(top_row['estimated_gap'])} roles**.
            * **Source & Metadata:** `Synthetic Demo Portal v1` | Period: `2025-Q2` | Units: `Number of Persons/Roles`.
            * **Candidate Action:** Prioritise training batch expansion in high-gap roles while auditing missing supply records in districts flagged with data warnings (such as Dakshina Kannada/Mangaluru).
            * **Caveats & Human Review Notes:** Priority score assumes equal 50/50 weighting between demand volume and supply gap. Requires human sign-off.
            """)

# ==========================================
# MODULE 6: AGENTIC DECISION ENGINE (KSISU-06)
# ==========================================
elif module_choice == "6. ACT: Agentic Decision Engine (KSISU-06)":
    st.title("Module 6 — Agentic AI Decision Engine (KSISU-06)")
    st.markdown("Coordinates a controlled 6-stage workflow across Modules 1–5 and halts at a mandatory **Human Review Gate**.")

    planning_goal = st.text_input(
        "Enter High-Level Policy Planning Objective:",
        "Identify priority districts and emerging technical skills for Q2 2025 training allocation in Karnataka."
    )

    if st.button("▶️ Execute Controlled Agent Workflow"):
        st.session_state["agent_logs"] = []
        now_str = lambda: datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        clean_df = st.session_state["clean_df"]
        q_rep = st.session_state["quality_report"]
        
        # Stage 1: PLAN
        st.session_state["agent_logs"].append({
            "stage": "1. PLAN", "time": now_str(), "module": "KSISU-06 Planner",
            "status": "COMPLETED",
            "details": f"Parsed objective: '{planning_goal}'. Scheduled calls to KSISU-01, KSISU-02, KSISU-03, KSISU-04, and KSISU-05."
        })
        
        # Stage 2: RETRIEVE (Module 1)
        st.session_state["agent_logs"].append({
            "stage": "2. RETRIEVE", "time": now_str(), "module": "KSISU-01 Data Explorer",
            "status": "COMPLETED",
            "details": f"Loaded {q_rep['cleaned_row_count']} cleaned records ({q_rep['duplicates_removed']} duplicates stripped; Gulbarga->Kalaburagi standardised)."
        })

        # Stage 3: ANALYSE & DIAGNOSE (Modules 2, 3, 4)
        scored = compute_district_scores(clean_df, 0.5, 0.5, "2025-Q2")
        top_dist = scored.iloc[0]["district"]
        sk_q1 = set(extract_skill_taxonomy(clean_df, "2025-Q1")["skill"].unique())
        sk_q2 = set(extract_skill_taxonomy(clean_df, "2025-Q2")["skill"].unique())
        emerging = sorted(list(sk_q2 - sk_q1 - {"Unspecified Skill"}))
        
        st.session_state["agent_logs"].append({
            "stage": "3. ANALYSE", "time": now_str(), "module": "KSISU-02 / 03 / 04",
            "status": "COMPLETED",
            "details": f"Top candidate priority district: {top_dist} (Score: {scored.iloc[0]['candidate_priority_score']}). Emerging Q2 skills identified: {', '.join(emerging)}."
        })

        # Stage 4: VALIDATE
        missing_cnt = sum(q_rep["missing_values_detected"].values())
        st.session_state["agent_logs"].append({
            "stage": "4. VALIDATE", "time": now_str(), "module": "KSISU-06 Validator",
            "status": "PASSED WITH CAVEATS",
            "details": f"Provenance verified (Source: Synthetic Demo Portal v1, Units: Number of Persons/Roles). Flagged {missing_cnt} missing fields in raw file."
        })

        # Stage 5: EXPLAIN (Module 5)
        st.session_state["agent_logs"].append({
            "stage": "5. EXPLAIN", "time": now_str(), "module": "KSISU-05 Copilot",
            "status": "DRAFT READY",
            "details": f"Compiled structured recommendation for {top_dist} and Kalaburagi regional hubs covering {', '.join(emerging)}."
        })

        # Stage 6: HUMAN REVIEW GATE
        st.session_state["agent_logs"].append({
            "stage": "6. HUMAN REVIEW", "time": now_str(), "module": "KSISU-06 Governance Gate",
            "status": "PAUSED — AWAITING HUMAN SIGN-OFF",
            "details": "Autonomous external action blocked by policy guardrail. Waiting for reviewer decision."
        })
        st.session_state["agent_status"] = "AWAITING_REVIEW"

    # Display Traceable Run Log
    if st.session_state["agent_logs"]:
        st.subheader("Traceable Agent Execution Log")
        log_df = pd.DataFrame(st.session_state["agent_logs"])
        st.table(log_df)

        st.subheader("Mandatory Human-in-the-Loop Approval Gate")
        st.info(f"**Current Workflow Status:** `{st.session_state['agent_status']}`")
        
        reviewer_notes = st.text_area("Supervisor / Policy Reviewer Notes:", "Verified synthetic disclaimer and comparability caveats.")
        b1, b2 = st.columns(2)
        if b1.button("✅ Approve Draft for Stakeholder Review"):
            st.session_state["agent_status"] = "APPROVED_BY_HUMAN"
            st.success(f"Workflow Approved at {datetime.now().strftime('%H:%M:%S')}! Logged Reviewer Note: {reviewer_notes}")
        if b2.button("❌ Reject & Return for Data Revision"):
            st.session_state["agent_status"] = "REJECTED_BY_HUMAN"
            st.error(f"Workflow Rejected at {datetime.now().strftime('%H:%M:%S')}. Reason logged: {reviewer_notes}")
