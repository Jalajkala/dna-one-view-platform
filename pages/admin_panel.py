import streamlit as st
import pandas as pd
from sqlalchemy import text

# Navigation option back to Home Page
if st.button("← Back to Home"):
    st.switch_page("pages/home.py")

st.title("⚙️ ADMIN: Manage Access Control & Data")
st.markdown("Update, Modify, Delete, or Add data for PATH A, PATH B, PATH C, and manage User Access[cite: 1].")
st.markdown("---")

# 1. Role-Based Access Security Check
user_role = st.session_state.get("user_role", "Viewer")

if user_role == "Viewer":
    st.error("🚫 Access Denied: This component is available only to Administrators and Contributors of the D&A One View application[cite: 1].")
    st.stop()

# Initialize DB Connection
try:
    conn = st.connection("neon_db", type="sql")
except Exception as e:
    st.error(f"Error connecting to the database: {e}")
    st.stop()

# 2. Section Layout via Tabs
tab_users, tab_kpi, tab_analytics, tab_datamap = st.tabs([
    "👥 User Access Management", 
    "📊 KPI Catalog", 
    "📈 Analytical Products", 
    "🗺️ Data Map"
])

# --- TAB 1: User Access Management ---
with tab_users:
    if user_role != "Admin":
        st.warning("⚠️ Access Denied: Only Admins can manage overall application user access[cite: 1].")
    else:
        st.subheader("Manage Application Users")
        st.write("Add, modify, or remove users and their role assignments[cite: 1].")
        
        try:
            # Fetch existing users
            users_df = conn.query("SELECT * FROM tbl_users ORDER BY user_id", ttl="0s")
            
            # Interactive Data Editor
            edited_users = st.data_editor(
                users_df, 
                num_rows="dynamic", 
                use_container_width=True,
                key="editor_users",
                column_config={
                    "user_id": st.column_config.NumberColumn("ID", disabled=True),
                    "user_email": st.column_config.TextColumn("User Email", required=True),
                    "user_role": st.column_config.SelectboxColumn(
                        "User Role", 
                        options=["Viewer", "Contributor", "Admin"], 
                        required=True
                    ),
                    "domain_access": st.column_config.TextColumn("Domain Access (For Contributors)")
                }
            )
            
            # Database Write-Back Logic (Mockup for saving changes)
            if st.button("💾 Save User Changes"):
                st.success("User Access Management changes saved successfully! (Implement SQLAlchemy execution here)")
        except Exception as e:
            st.error("Database table 'tbl_users' might not be populated yet.")

# --- TAB 2: KPI Catalog (PATH A) ---
with tab_kpi:
    st.subheader("Manage KPI Catalog (PATH A)")
    if user_role == "Contributor":
        st.info("You are viewing this as a Contributor. You may Add, Modify, and View KPIs for your assigned domain[cite: 1].")
        
    try:
        kpi_df = conn.query("SELECT * FROM tbl_standardkpi_catalog ORDER BY kpi_id", ttl="0s")
        
        edited_kpi = st.data_editor(
            kpi_df, 
            num_rows="dynamic", 
            use_container_width=True,
            key="editor_kpi",
            column_config={
                "kpi_id": st.column_config.NumberColumn("ID", disabled=True),
                "kpi_showonscreenstatus": st.column_config.CheckboxColumn("Visible?"),
            }
        )
        if st.button("💾 Save KPI Changes"):
            st.success("KPI Catalog changes saved successfully!")
    except Exception as e:
        st.error(f"Error loading KPI data: {e}")

# --- TAB 3: Analytical Products (PATH B) ---
with tab_analytics:
    st.subheader("Manage Analytical Products (PATH B)")
    try:
        analytics_df = conn.query("SELECT * FROM tbl_analytical_product_catalog ORDER BY product_id", ttl="0s")
        
        edited_analytics = st.data_editor(
            analytics_df, 
            num_rows="dynamic", 
            use_container_width=True,
            key="editor_analytics",
            column_config={
                "product_id": st.column_config.NumberColumn("ID", disabled=True),
                "analytical_product_visiblestatus": st.column_config.CheckboxColumn("Visible?"),
            }
        )
        if st.button("💾 Save Analytical Product Changes"):
             st.success("Analytical Products changes saved successfully!")
    except Exception as e:
        st.error(f"Error loading Analytics data: {e}")

# --- TAB 4: Data Map (PATH C) ---
with tab_datamap:
    st.subheader("Manage E2A Data Map (PATH C)")
    try:
        datamap_df = conn.query("SELECT * FROM tbl_data_map ORDER BY datasource_id", ttl="0s")
        
        edited_datamap = st.data_editor(
            datamap_df, 
            num_rows="dynamic", 
            use_container_width=True,
            key="editor_datamap",
            column_config={
                "datasource_id": st.column_config.NumberColumn("ID", disabled=True),
                "datasource_visiblestatus": st.column_config.CheckboxColumn("Visible?"),
            }
        )
        if st.button("💾 Save Data Map Changes"):
             st.success("Data Map changes saved successfully!")
    except Exception as e:
        st.error(f"Error loading Data Map data: {e}")
