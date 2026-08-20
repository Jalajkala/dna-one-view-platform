import streamlit as st
import pandas as pd

# --- CSS Injection to fix scaling ---
st.markdown("""
<style>
/* Force all Streamlit images to act as fixed-height banners */
[data-testid="stImage"] img {
    max-height: 160px;
    object-fit: cover;
    border-radius: 6px;
}
/* Slightly increase caption size for better readability on large screens */
[data-testid="stCaptionContainer"] {
    font-size: 1rem;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("Welcome to the E2A D&A One View Platform")
st.subheader("Simplifying your Data & Analytics journey through 3 logical paths..")
st.markdown("---")

# --- Fetch Metrics from Neon DB ---
try:
    conn = st.connection("neon_db", type="sql")
    # Fetch active KPI count
    kpi_count = conn.query("SELECT COUNT(*) as count FROM tbl_standardkpi_catalog WHERE kpi_showonscreenstatus = TRUE", ttl="1m").iloc[0]['count']
    # Fetch active Analytical Product count
    ap_count = conn.query("SELECT COUNT(*) as count FROM tbl_analytical_product_catalog WHERE analytical_product_visiblestatus = TRUE", ttl="1m").iloc[0]['count']
    # Fetch active Data Source count
    dm_count = conn.query("SELECT COUNT(*) as count FROM tbl_data_map WHERE datasource_visiblestatus = TRUE", ttl="1m").iloc[0]['count']
except Exception as e:
    # Fallback if the database connection fails
    kpi_count = "N/A"
    ap_count = "N/A"
    dm_count = "N/A"

# Create three equal-width columns with a larger gap for breathing room
col1, col2, col3 = st.columns(3, gap="large")

# --- Column 1: PATH A ---
with col1:
    with st.container(border=True):
        st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=500&auto=format&fit=crop&q=60", use_container_width=True)
        st.subheader("PATH A")
        st.caption("“I want to build my understanding on various Standard KPIs”")
        st.markdown("**KPI Catalog**")
        
        # Display the metric
        st.metric(label="Total Available KPIs", value=kpi_count)
        
        if st.button("Explore KPI Catalog", use_container_width=True, type="primary"):
            st.switch_page("pages/path_a_kpi.py")

# --- Column 2: PATH B ---
with col2:
    with st.container(border=True):
        st.image("https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=500&auto=format&fit=crop&q=60", use_container_width=True)
        st.subheader("PATH B")
        st.caption("“I want to explore which Analytical Products are available to use, so I adopt, reuse and not rebuild”")
        st.markdown("**Analytical Products Catalog**")
        
        # Display the metric
        st.metric(label="Total Analytical Products", value=ap_count)
        
        if st.button("Explore Analytical Products", use_container_width=True, type="primary"):
            st.switch_page("pages/path_b_analytical.py")

# --- Column 3: PATH C ---
with col3:
    with st.container(border=True):
        st.image("https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=500&auto=format&fit=crop&q=60", use_container_width=True)
        st.subheader("PATH C")
        st.caption("“My need is not Standard or is not covered by available Analytical Products. I would like to explore authorized data sources...”")
        st.markdown("**E2A Data Map**")
        
        # Display the metric
        st.metric(label="Total Sources of Truth", value=dm_count)
        
        if st.button("Explore E2A Data Map", use_container_width=True, type="primary"):
            st.session_state.show_path_c_alert = True

st.markdown("---")

# --- Alert logic for PATH C selection ---
if st.session_state.get("show_path_c_alert", False):
    st.warning("Have you browsed the Analytical Catalog to be sure your need is not already covered?")
    
    alert_col1, alert_col2, _ = st.columns([1, 1, 2])
    with alert_col1:
        if st.button("Yes (Proceed to Data Map)", use_container_width=True):
            st.session_state.show_path_c_alert = False
            st.switch_page("pages/path_c_datamap.py")
    with alert_col2:
        if st.button("No (Take me to Catalog)", use_container_width=True):
            st.session_state.show_path_c_alert = False
            st.switch_page("pages/path_b_analytical.py")
