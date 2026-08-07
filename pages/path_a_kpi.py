import streamlit as st
import pandas as pd

# Navigation option back to Home Page
if st.button("← Back to Home"):
    st.switch_page("pages/home.py")

st.title("📊 PATH A: Standard KPI Catalog")
st.markdown(
    "Explore standard KPIs across business domains to understand core definitions, calculation formulas, target audiences, and data sources."
)
st.markdown("---")

# Fetch active KPI data from Neon DB
try:
    conn = st.connection("neon_db", type="sql")
    # Retrieve only records configured to be shown on screen
    query = "SELECT * FROM tbl_standardkpi_catalog WHERE kpi_showonscreenstatus = TRUE;"
    df = conn.query(query, ttl="10s")
except Exception as e:
    st.error(f"Error connecting to the database: {e}")
    df = pd.DataFrame()

if df.empty:
    st.info("No active KPIs found in the catalog database yet. (You can populate sample data or use the Admin Panel to add new KPIs).")
else:
    # Top Control Bar: Search and Filters
    col_search, col_domain, col_subdomain = st.columns([2, 1, 1])

    with col_search:
        search_query = st.text_input("🔍 Search KPI Title or Description", "")

    # Domain Filter
    domains = ["All"] + sorted([d for d in df["kpi_domain"].dropna().unique() if d])
    with col_domain:
        selected_domain = st.selectbox("Filter by Domain", domains)

    # Filter dataframe by selected domain to populate dynamic subdomains
    if selected_domain != "All":
        filtered_df = df[df["kpi_domain"] == selected_domain]
    else:
        filtered_df = df

    # Subdomain Filter
    subdomains = ["All"] + sorted([s for s in filtered_df["kpi_subdomain"].dropna().unique() if s])
    with col_subdomain:
        selected_subdomain = st.selectbox("Filter by Subdomain", subdomains)

    # Apply Subdomain Filter
    if selected_subdomain != "All":
        filtered_df = filtered_df[filtered_df["kpi_subdomain"] == selected_subdomain]

    # Apply Search Filter
    if search_query:
        filtered_df = filtered_df[
            filtered_df["kpi_title"].str.contains(search_query, case=False, na=False) |
            filtered_df["kpi_description"].str.contains(search_query, case=False, na=False)
        ]

    st.markdown(f"**Showing {len(filtered_df)} cataloged KPI(s)**")
    st.markdown("---")

    # Display KPI Records as Interactive Cards
    for idx, row in filtered_df.iterrows():
        domain_tag = row.get('kpi_domain') or 'General'
        subdomain_tag = row.get('kpi_subdomain') or 'General'
        
        with st.expander(f"📌 **{row['kpi_title']}** | *{domain_tag} → {subdomain_tag}*"):
            st.markdown(f"**Description:** {row.get('kpi_description', 'N/A')}")
            
            st.markdown("#### 📐 Calculation / Definition Formula")
            st.code(row.get('kpi_definitionformula', 'No formula provided.'), language="text")
            
            col_meta1, col_meta2 = st.columns(2)
            with col_meta1:
                st.markdown(f"🎯 **Target Audience:** {row.get('kpi_targetaudience', 'N/A')}")
            with col_meta2:
                st.markdown(f"💻 **Application Sources:** {row.get('kpi_appsource', 'N/A')}")
