import streamlit as st
import pandas as pd

# Navigation option back to Home Page
if st.button("← Back to Home"):
    st.switch_page("pages/home.py")

st.title("📊 PATH A: Standard KPI Catalog")
st.markdown("Navigate the catalog from left to right: Select a Domain, choose a Sub-domain, and view the Standard KPIs.")
st.markdown("---")

# Fetch active KPI data from Neon DB
try:
    conn = st.connection("neon_db", type="sql")
    query = "SELECT * FROM tbl_standardkpi_catalog WHERE kpi_showonscreenstatus = TRUE;"
    df = conn.query(query, ttl="10s")
except Exception as e:
    st.error(f"Error connecting to the database: {e}")
    df = pd.DataFrame()

if df.empty:
    st.info("No active KPIs found in the catalog database yet.")
else:
    # Initialize session state for cascading selections
    if "kpi_domain" not in st.session_state:
        st.session_state.kpi_domain = None
    if "kpi_subdomain" not in st.session_state:
        st.session_state.kpi_subdomain = None
    if "kpi_selected" not in st.session_state:
        st.session_state.kpi_selected = None

    def select_domain(dom):
        st.session_state.kpi_domain = dom
        st.session_state.kpi_subdomain = None
        st.session_state.kpi_selected = None

    def select_subdomain(sub):
        st.session_state.kpi_subdomain = sub
        st.session_state.kpi_selected = None

    def select_kpi(kpi):
        st.session_state.kpi_selected = kpi

    # Domain Images Mapping
    domain_images = {
        "Sales & Marketing": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=500&auto=format&fit=crop&q=60",
        "Supply Chain & Logistics": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=500&auto=format&fit=crop&q=60",
        "Finance": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=500&auto=format&fit=crop&q=60",
        "Service Personnel": "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=500&auto=format&fit=crop&q=60",
        "Quality": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=500&auto=format&fit=crop&q=60"
    }
    default_img = "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=500&auto=format&fit=crop&q=60"

    # 3-Column Miller Layout
    col_dom, col_sub, col_kpi = st.columns(3)

    # --- COLUMN 1: DOMAIN CARDS WITH IMAGES ---
    with col_dom:
        st.markdown("### 🏢 1. DOMAIN")
        domains = sorted([d for d in df["kpi_domain"].dropna().unique() if d])
        
        for dom in domains:
            is_selected = (st.session_state.kpi_domain == dom)
            btn_type = "primary" if is_selected else "secondary"
            
            img_url = domain_images.get(dom, default_img)
            with st.container(border=True):
                st.image(img_url, use_container_width=True)
                count = len(df[df["kpi_domain"] == dom])
                st.markdown(f"**{dom}**")
                st.caption(f"{count} KPIs registered")
                if st.button(f"Select Domain", key=f"btn_dom_{dom}", type=btn_type, use_container_width=True):
                    select_domain(dom)

    # --- COLUMN 2: SUB-DOMAINS ---
    with col_sub:
        st.markdown("### 📂 2. SUB-DOMAIN")
        if st.session_state.kpi_domain:
            sub_df = df[df["kpi_domain"] == st.session_state.kpi_domain]
            subdomains = sorted([s for s in sub_df["kpi_subdomain"].dropna().unique() if s])
            
            if subdomains:
                for sub in subdomains:
                    is_selected = (st.session_state.kpi_subdomain == sub)
                    btn_type = "primary" if is_selected else "secondary"
                    
                    count = len(sub_df[sub_df["kpi_subdomain"] == sub])
                    with st.container(border=True):
                        st.markdown(f"**{sub}**")
                        st.caption(f"{count} KPIs available")
                        if st.button("Select Sub-domain", key=f"btn_sub_{sub}", type=btn_type, use_container_width=True):
                            select_subdomain(sub)
            else:
                st.info("No sub-domains available for this domain.")
        else:
            st.info("👈 Select a Domain to view sub-domains.")

    # --- COLUMN 3: STANDARD KPIS ---
    with col_kpi:
        st.markdown("### 📌 3. STANDARD KPI")
        if st.session_state.kpi_subdomain:
            kpi_df = df[
                (df["kpi_domain"] == st.session_state.kpi_domain) & 
                (df["kpi_subdomain"] == st.session_state.kpi_subdomain)
            ]
            
            if not kpi_df.empty:
                for idx, row in kpi_df.iterrows():
                    kpi_title = row['kpi_title']
                    is_selected = (st.session_state.kpi_selected == kpi_title)
                    btn_type = "primary" if is_selected else "secondary"
                    
                    with st.container(border=True):
                        st.markdown(f"**{kpi_title}**")
                        if st.button("View KPI Card", key=f"btn_kpi_{row['kpi_id']}", type=btn_type, use_container_width=True):
                            select_kpi(kpi_title)
            else:
                st.info("No KPIs found.")
        else:
            st.info("👈 Select a Sub-domain to view KPIs.")

    # --- EXPANDED KPI DETAIL CARD (Appears below when a KPI is selected) ---
    if st.session_state.kpi_selected:
        st.markdown("---")
        selected_row = df[df["kpi_title"] == st.session_state.kpi_selected].iloc[0]
        
        st.subheader(f"📌 KPI Detail Card: {selected_row['kpi_title']}")
        with st.container(border=True):
            det_col1, det_col2 = st.columns(2)
            with det_col1:
                st.markdown(f"🏢 **Domain:** {selected_row.get('kpi_domain', 'N/A')}")
                st.markdown(f"📂 **Sub-domain:** {selected_row.get('kpi_subdomain', 'N/A')}")
                st.markdown(f"🎯 **Target Audience:** {selected_row.get('kpi_targetaudience', 'N/A')}")
            with det_col2:
                st.markdown(f"💻 **Application Sources:** {selected_row.get('kpi_appsource', 'N/A')}")
            
            st.markdown("---")
            st.markdown("📝 **Description:**")
            st.write(selected_row.get('kpi_description', 'N/A'))
            
            st.markdown("📐 **Calculation / Definition Formula:**")
            st.code(selected_row.get('kpi_definitionformula', 'No formula provided.'), language="text")
