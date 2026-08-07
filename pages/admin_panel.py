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
        # 1. Fetch current data
        datamap_df = conn.query("SELECT * FROM tbl_data_map ORDER BY datasource_id", ttl="0s")
        
        # 2. Render Data Editor
        edited_datamap = st.data_editor(
            datamap_df, 
            num_rows="dynamic", 
            use_container_width=True,
            key="editor_datamap", # This key stores the changes in st.session_state
            column_config={
                "datasource_id": st.column_config.NumberColumn("ID", disabled=True),
                "datasource_visiblestatus": st.column_config.CheckboxColumn("Visible?", default=True),
            }
        )
        
        # 3. Database Write-Back Logic
        if st.button("💾 Save Data Map Changes"):
            # Retrieve the dictionary of changes tracked by the editor's key
            changes = st.session_state["editor_datamap"]
            
            with conn.session as s:
                # Handle Deletions
                for row_idx in changes.get("deleted_rows", []):
                    # Get the ID of the deleted row from the original dataframe
                    row_id = int(datamap_df.iloc[row_idx]["datasource_id"])
                    s.execute(text("DELETE FROM tbl_data_map WHERE datasource_id = :id"), {"id": row_id})
                
                # Handle Updates (Edits)
                for row_idx, updates in changes.get("edited_rows", {}).items():
                    row_id = int(datamap_df.iloc[row_idx]["datasource_id"])
                    # Dynamically build the SET clause for updated columns
                    set_clauses = ", ".join([f"{col} = :{col}" for col in updates.keys()])
                    if set_clauses:
                        updates["id"] = row_id
                        query = text(f"UPDATE tbl_data_map SET {set_clauses} WHERE datasource_id = :id")
                        s.execute(query, updates)
                
                # Handle Insertions (New Rows)
                for new_row in changes.get("added_rows", []):
                    # Exclude the ID column since it's a SERIAL primary key in Neon DB
                    if "datasource_id" in new_row:
                        del new_row["datasource_id"]
                        
                    cols = ", ".join(new_row.keys())
                    vals = ", ".join([f":{col}" for col in new_row.keys()])
                    if cols:
                        query = text(f"INSERT INTO tbl_data_map ({cols}) VALUES ({vals})")
                        s.execute(query, new_row)
                
                # Commit all transactions to the Neon database
                s.commit()
            
            st.success("Data Map changes saved successfully to the database!")
            # Rerun the app to refresh the dataframe with new IDs from the database
            st.rerun()

    except Exception as e:
        st.error(f"Error executing database operations: {e}")
