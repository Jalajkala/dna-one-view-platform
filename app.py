import streamlit as st

# Configure the main application layout
st.set_page_config(page_title="E2A D&A One View Platform", layout="wide")

# Setup the Neon DB Connection using Streamlit Secrets
conn = st.connection("neon_db", type="sql")
st.session_state.db_conn = conn

# Define Application Pages
home_page = st.Page("pages/home.py", title="Home", icon="🏠", default=True)
path_a = st.Page("pages/path_a_kpi.py", title="PATH A: KPI Catalog", icon="📊")
path_b = st.Page("pages/path_b_analytical.py", title="PATH B: Analytical Products", icon="📈")
path_c = st.Page("pages/path_c_datamap.py", title="PATH C: E2A Data Map", icon="🗺️")
admin_panel = st.Page("pages/admin_panel.py", title="ADMIN: Data Management", icon="⚙️")

# Mock Authentication for Role-Based Access Control
if "user_role" not in st.session_state:
    st.session_state.user_role = "Viewer"

with st.sidebar:
    st.markdown("### User Access Simulation")
    # This dropdown simulates the 'Manage Access Control' user roles
    st.session_state.user_role = st.selectbox(
        "Select your Role:", 
        ["Viewer", "Contributor", "Admin"]
    )

# Establish base navigation array
nav_pages = [home_page, path_a, path_b, path_c]

# The Admin Panel is appended only if the user role permits updates/modifications
if st.session_state.user_role in ["Contributor", "Admin"]:
    nav_pages.append(admin_panel)

# Initialize and run the multi-page router
pg = st.navigation(nav_pages)
pg.run()
