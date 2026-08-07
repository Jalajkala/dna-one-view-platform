import streamlit as st
import pandas as pd
from sqlalchemy import text

# Navigation option back to Home Page
if st.button("← Back to Home"):
    st.switch_page("pages/home.py")

st.title("⚙️ ADMIN: Manage Access Control & Data")
st.markdown("Add, update, or remove records across all platform catalogs and the product roadmap using structured forms.")
st.markdown("---")

# Role-Based Access Security Check
user_role = st.session_state.get("user_role", "Viewer")

if user_role == "Viewer":
    st.error("🚫 Access Denied: This component is available only to Administrators and Contributors.")
    st.stop()

# Initialize DB Connection
try:
    conn = st.connection("neon_db", type="sql")
except Exception as e:
    st.error(f"Error connecting to database: {e}")
    st.stop()

# Section Layout via Tabs (Added Roadmap Tab)
tab_kpi, tab_analytics, tab_datamap, tab_roadmap, tab_users = st.tabs([
    "📊 KPI Catalog", 
    "📈 Analytical Products", 
    "🗺️ Data Map",
    "🚀 Roadmap",
    "👥 User Access Management"
])

# ==========================================
# TAB 1: KPI Catalog (PATH A)
# ==========================================
with tab_kpi:
    st.subheader("Manage KPI Catalog")
    action_kpi = st.radio(
        "Choose Action:", 
        ["➕ Add New KPI", "✏️ Update / Delete Existing KPI"], 
        horizontal=True, key="action_kpi"
    )

    if action_kpi == "➕ Add New KPI":
        with st.form("form_add_kpi", clear_on_submit=True):
            kpi_title = st.text_input("KPI Title *")
            kpi_description = st.text_area("KPI Description")
            col1, col2 = st.columns(2)
            with col1:
                kpi_domain = st.text_input("Business Domain")
                kpi_targetaudience = st.text_input("Target Audience")
            with col2:
                kpi_subdomain = st.text_input("Business Subdomain")
                kpi_appsource = st.text_input("Application Sources")
            
            kpi_definitionformula = st.text_area("Calculation / Definition Formula")
            kpi_showonscreenstatus = st.checkbox("Show on Screen (Visible)", value=True)

            submit_kpi = st.form_submit_button("➕ Save New KPI")

            if submit_kpi:
                if not kpi_title.strip():
                    st.error("KPI Title is required.")
                else:
                    with conn.session as s:
                        s.execute(text("""
                            INSERT INTO tbl_standardkpi_catalog 
                            (kpi_title, kpi_description, kpi_domain, kpi_subdomain, kpi_definitionformula, kpi_targetaudience, kpi_showonscreenstatus, kpi_appsource)
                            VALUES (:title, :desc, :domain, :subdomain, :formula, :audience, :status, :source)
                        """), {
                            "title": kpi_title, "desc": kpi_description, "domain": kpi_domain,
                            "subdomain": kpi_subdomain, "formula": kpi_definitionformula,
                            "audience": kpi_targetaudience, "status": kpi_showonscreenstatus,
                            "source": kpi_appsource
                        })
                        s.commit()
                    st.success(f"KPI '{kpi_title}' successfully created!")
                    st.rerun()

    else:
        df_kpi = conn.query("SELECT * FROM tbl_standardkpi_catalog ORDER BY kpi_id", ttl="0s")
        if df_kpi.empty:
            st.info("No KPI records found in the database.")
        else:
            kpi_options = {f"ID {row['kpi_id']} - {row['kpi_title']}": row['kpi_id'] for _, row in df_kpi.iterrows()}
            selected_kpi_label = st.selectbox("Select KPI to Modify:", list(kpi_options.keys()))
            selected_kpi_id = kpi_options[selected_kpi_label]
            row_data = df_kpi[df_kpi['kpi_id'] == selected_kpi_id].iloc[0]

            with st.form("form_edit_kpi"):
                e_title = st.text_input("KPI Title *", value=row_data['kpi_title'])
                e_desc = st.text_area("KPI Description", value=row_data.get('kpi_description') or "")
                col1, col2 = st.columns(2)
                with col1:
                    e_domain = st.text_input("Business Domain", value=row_data.get('kpi_domain') or "")
                    e_audience = st.text_input("Target Audience", value=row_data.get('kpi_targetaudience') or "")
                with col2:
                    e_subdomain = st.text_input("Business Subdomain", value=row_data.get('kpi_subdomain') or "")
                    e_source = st.text_input("Application Sources", value=row_data.get('kpi_appsource') or "")
                
                e_formula = st.text_area("Calculation / Definition Formula", value=row_data.get('kpi_definitionformula') or "")
                e_status = st.checkbox("Show on Screen (Visible)", value=bool(row_data.get('kpi_showonscreenstatus')))

                col_btn1, col_btn2 = st.columns([1, 1])
                with col_btn1:
                    btn_update = st.form_submit_button("💾 Save Changes")
                with col_btn2:
                    btn_delete = st.form_submit_button("🗑️ Delete KPI", type="secondary")

                if btn_update:
                    with conn.session as s:
                        s.execute(text("""
                            UPDATE tbl_standardkpi_catalog SET
                            kpi_title = :title, kpi_description = :desc, kpi_domain = :domain,
                            kpi_subdomain = :subdomain, kpi_definitionformula = :formula,
                            kpi_targetaudience = :audience, kpi_showonscreenstatus = :status,
                            kpi_appsource = :source WHERE kpi_id = :id
                        """), {
                            "title": e_title, "desc": e_desc, "domain": e_domain,
                            "subdomain": e_subdomain, "formula": e_formula,
                            "audience": e_audience, "status": e_status,
                            "source": e_source, "id": selected_kpi_id
                        })
                        s.commit()
                    st.success("KPI record updated successfully!")
                    st.rerun()

                if btn_delete:
                    with conn.session as s:
                        s.execute(text("DELETE FROM tbl_standardkpi_catalog WHERE kpi_id = :id"), {"id": selected_kpi_id})
                        s.commit()
                    st.warning("KPI record deleted successfully!")
                    st.rerun()


# ==========================================
# TAB 2: Analytical Products (PATH B)
# ==========================================
with tab_analytics:
    st.subheader("Manage Analytical Products Catalog")
    action_ap = st.radio(
        "Choose Action:", 
        ["➕ Add New Analytical Product", "✏️ Update / Delete Existing Product"], 
        horizontal=True, key="action_ap"
    )

    if action_ap == "➕ Add New Analytical Product":
        with st.form("form_add_ap", clear_on_submit=True):
            ap_title = st.text_input("Product Title *")
            ap_desc = st.text_area("Product Description")
            col1, col2 = st.columns(2)
            with col1:
                ap_domain = st.text_input("Business Domain")
                ap_audience = st.text_input("Target Audience")
            with col2:
                ap_subdomain = st.text_input("Business Subdomain")
                ap_banner = st.text_input("Banner Image URL")
            
            ap_collibra = st.text_input("Collibra Hyperlink")
            ap_status = st.checkbox("Visible Status", value=True)

            submit_ap = st.form_submit_button("➕ Save New Product")

            if submit_ap:
                if not ap_title.strip():
                    st.error("Product Title is required.")
                else:
                    with conn.session as s:
                        s.execute(text("""
                            INSERT INTO tbl_analytical_product_catalog 
                            (analytical_product_title, analytical_product_description, analytical_business_domain, analytical_business_subdomain, analytical_product_targetaudience, analytical_product_visiblestatus, analytical_product_collibra_link, analytical_product_banner)
                            VALUES (:title, :desc, :domain, :subdomain, :audience, :status, :collibra, :banner)
                        """), {
                            "title": ap_title, "desc": ap_desc, "domain": ap_domain,
                            "subdomain": ap_subdomain, "audience": ap_audience,
                            "status": ap_status, "collibra": ap_collibra, "banner": ap_banner
                        })
                        s.commit()
                    st.success(f"Product '{ap_title}' added successfully!")
                    st.rerun()

    else:
        df_ap = conn.query("SELECT * FROM tbl_analytical_product_catalog ORDER BY product_id", ttl="0s")
        if df_ap.empty:
            st.info("No Analytical Products found.")
        else:
            ap_options = {f"ID {row['product_id']} - {row['analytical_product_title']}": row['product_id'] for _, row in df_ap.iterrows()}
            selected_ap_label = st.selectbox("Select Product to Modify:", list(ap_options.keys()))
            selected_ap_id = ap_options[selected_ap_label]
            row_data = df_ap[df_ap['product_id'] == selected_ap_id].iloc[0]

            with st.form("form_edit_ap"):
                e_title = st.text_input("Product Title *", value=row_data['analytical_product_title'])
                e_desc = st.text_area("Product Description", value=row_data.get('analytical_product_description') or "")
                col1, col2 = st.columns(2)
                with col1:
                    e_domain = st.text_input("Business Domain", value=row_data.get('analytical_business_domain') or "")
                    e_audience = st.text_input("Target Audience", value=row_data.get('analytical_product_targetaudience') or "")
                with col2:
                    e_subdomain = st.text_input("Business Subdomain", value=row_data.get('analytical_business_subdomain') or "")
                    e_banner = st.text_input("Banner Image URL", value=row_data.get('analytical_product_banner') or "")
                
                e_collibra = st.text_input("Collibra Hyperlink", value=row_data.get('analytical_product_collibra_link') or "")
                e_status = st.checkbox("Visible Status", value=bool(row_data.get('analytical_product_visiblestatus')))

                col_btn1, col_btn2 = st.columns([1, 1])
                with col_btn1:
                    btn_update = st.form_submit_button("💾 Save Changes")
                with col_btn2:
                    btn_delete = st.form_submit_button("🗑️ Delete Product", type="secondary")

                if btn_update:
                    with conn.session as s:
                        s.execute(text("""
                            UPDATE tbl_analytical_product_catalog SET
                            analytical_product_title = :title, analytical_product_description = :desc,
                            analytical_business_domain = :domain, analytical_business_subdomain = :subdomain,
                            analytical_product_targetaudience = :audience, analytical_product_visiblestatus = :status,
                            analytical_product_collibra_link = :collibra, analytical_product_banner = :banner
                            WHERE product_id = :id
                        """), {
                            "title": e_title, "desc": e_desc, "domain": e_domain,
                            "subdomain": e_subdomain, "audience": e_audience,
                            "status": e_status, "collibra": e_collibra, "banner": e_banner,
                            "id": selected_ap_id
                        })
                        s.commit()
                    st.success("Analytical Product updated successfully!")
                    st.rerun()

                if btn_delete:
                    with conn.session as s:
                        s.execute(text("DELETE FROM tbl_analytical_product_catalog WHERE product_id = :id"), {"id": selected_ap_id})
                        s.commit()
                    st.warning("Analytical Product deleted successfully!")
                    st.rerun()


# ==========================================
# TAB 3: Data Map (PATH C)
# ==========================================
with tab_datamap:
    st.subheader("Manage E2A Data Map")
    action_dm = st.radio(
        "Choose Action:", 
        ["➕ Add New Data Source", "✏️ Update / Delete Existing Data Source"], 
        horizontal=True, key="action_dm"
    )

    if action_dm == "➕ Add New Data Source":
        with st.form("form_add_dm", clear_on_submit=True):
            dm_title = st.text_input("Data Source Title *")
            dm_purpose = st.text_area("Data Source Purpose")
            col1, col2 = st.columns(2)
            with col1:
                dm_domain = st.text_input("Business Domain")
                dm_type = st.text_input("Data Type")
            with col2:
                dm_subdomain = st.text_input("Business Subdomain")
                dm_tag = st.text_input("Tags (e.g., DRUX, Group, Region)")
            
            dm_collibra = st.text_input("Collibra Hyperlink")
            dm_status = st.checkbox("Visible Status", value=True)

            submit_dm = st.form_submit_button("➕ Save New Data Source")

            if submit_dm:
                if not dm_title.strip():
                    st.error("Data Source Title is required.")
                else:
                    with conn.session as s:
                        s.execute(text("""
                            INSERT INTO tbl_data_map 
                            (datasource_title, datasource_purpose, datasource_business_domain, datasource_business_subdomain, datasource_data_type, datasource_tag, datasource_visiblestatus, datasource_link_to_collibra)
                            VALUES (:title, :purpose, :domain, :subdomain, :type, :tag, :status, :collibra)
                        """), {
                            "title": dm_title, "purpose": dm_purpose, "domain": dm_domain,
                            "subdomain": dm_subdomain, "type": dm_type, "tag": dm_tag,
                            "status": dm_status, "collibra": dm_collibra
                        })
                        s.commit()
                    st.success(f"Data Source '{dm_title}' added successfully!")
                    st.rerun()

    else:
        df_dm = conn.query("SELECT * FROM tbl_data_map ORDER BY datasource_id", ttl="0s")
        if df_dm.empty:
            st.info("No Data Map records found.")
        else:
            dm_options = {f"ID {row['datasource_id']} - {row['datasource_title']}": row['datasource_id'] for _, row in df_dm.iterrows()}
            selected_dm_label = st.selectbox("Select Data Source to Modify:", list(dm_options.keys()))
            selected_dm_id = dm_options[selected_dm_label]
            row_data = df_dm[df_dm['datasource_id'] == selected_dm_id].iloc[0]

            with st.form("form_edit_dm"):
                e_title = st.text_input("Data Source Title *", value=row_data['datasource_title'])
                e_purpose = st.text_area("Data Source Purpose", value=row_data.get('datasource_purpose') or "")
                col1, col2 = st.columns(2)
                with col1:
                    e_domain = st.text_input("Business Domain", value=row_data.get('datasource_business_domain') or "")
                    e_type = st.text_input("Data Type", value=row_data.get('datasource_data_type') or "")
                with col2:
                    e_subdomain = st.text_input("Business Subdomain", value=row_data.get('datasource_business_subdomain') or "")
                    e_tag = st.text_input("Tags", value=row_data.get('datasource_tag') or "")
                
                e_collibra = st.text_input("Collibra Hyperlink", value=row_data.get('datasource_link_to_collibra') or "")
                e_status = st.checkbox("Visible Status", value=bool(row_data.get('datasource_visiblestatus')))

                col_btn1, col_btn2 = st.columns([1, 1])
                with col_btn1:
                    btn_update = st.form_submit_button("💾 Save Changes")
                with col_btn2:
                    btn_delete = st.form_submit_button("🗑️ Delete Data Source", type="secondary")

                if btn_update:
                    with conn.session as s:
                        s.execute(text("""
                            UPDATE tbl_data_map SET
                            datasource_title = :title, datasource_purpose = :purpose,
                            datasource_business_domain = :domain, datasource_business_subdomain = :subdomain,
                            datasource_data_type = :type, datasource_tag = :tag,
                            datasource_visiblestatus = :status, datasource_link_to_collibra = :collibra
                            WHERE datasource_id = :id
                        """), {
                            "title": e_title, "purpose": e_purpose, "domain": e_domain,
                            "subdomain": e_subdomain, "type": e_type, "tag": e_tag,
                            "status": e_status, "collibra": e_collibra, "id": selected_dm_id
                        })
                        s.commit()
                    st.success("Data Source updated successfully!")
                    st.rerun()

                if btn_delete:
                    with conn.session as s:
                        s.execute(text("DELETE FROM tbl_data_map WHERE datasource_id = :id"), {"id": selected_dm_id})
                        s.commit()
                    st.warning("Data Source deleted successfully!")
                    st.rerun()


# ==========================================
# TAB 4: Roadmap Management
# ==========================================
with tab_roadmap:
    st.subheader("Manage Product & Data Roadmap")
    action_rm = st.radio(
        "Choose Action:", 
        ["➕ Add New Roadmap Item", "✏️ Update / Delete Existing Item"], 
        horizontal=True, key="action_rm"
    )

    if action_rm == "➕ Add New Roadmap Item":
        with st.form("form_add_rm", clear_on_submit=True):
            rm_title = st.text_input("Item Title *")
            rm_type = st.selectbox("Item Type", ["Data Source", "Analytical Product"])
            col1, col2 = st.columns(2)
            with col1:
                rm_domain = st.text_input("Business Domain")
                rm_horizon = st.selectbox("Target Horizon", ["Q3 2026", "Q4 2026", "2027 & Beyond"])
            with col2:
                rm_date = st.date_input("Target Date")
                rm_audience = st.text_input("Target Audience")
            
            rm_desc = st.text_area("Description")
            rm_status = st.checkbox("Visible Status", value=True)

            submit_rm = st.form_submit_button("➕ Save Roadmap Item")

            if submit_rm:
                if not rm_title.strip():
                    st.error("Item Title is required.")
                else:
                    with conn.session as s:
                        s.execute(text("""
                            INSERT INTO tbl_roadmap 
                            (item_title, item_type, business_domain, target_horizon, target_date, description, target_audience, visiblestatus)
                            VALUES (:title, :itype, :domain, :horizon, :tdate, :desc, :audience, :status)
                        """), {
                            "title": rm_title, "itype": rm_type, "domain": rm_domain,
                            "horizon": rm_horizon, "tdate": rm_date, "desc": rm_desc,
                            "audience": rm_audience, "status": rm_status
                        })
                        s.commit()
                    st.success(f"Roadmap item '{rm_title}' added successfully!")
                    st.rerun()

    else:
        df_rm = conn.query("SELECT * FROM tbl_roadmap ORDER BY roadmap_id", ttl="0s")
        if df_rm.empty:
            st.info("No roadmap records found.")
        else:
            rm_options = {f"ID {row['roadmap_id']} - {row['item_title']} ({row['target_horizon']})": row['roadmap_id'] for _, row in df_rm.iterrows()}
            selected_rm_label = st.selectbox("Select Roadmap Item to Modify:", list(rm_options.keys()))
            selected_rm_id = rm_options[selected_rm_label]
            row_data = df_rm[df_rm['roadmap_id'] == selected_rm_id].iloc[0]

            with st.form("form_edit_rm"):
                e_title = st.text_input("Item Title *", value=row_data['item_title'])
                
                types = ["Data Source", "Analytical Product"]
                curr_type_idx = types.index(row_data['item_type']) if row_data['item_type'] in types else 0
                e_type = st.selectbox("Item Type", types, index=curr_type_idx)
                
                col1, col2 = st.columns(2)
                with col1:
                    e_domain = st.text_input("Business Domain", value=row_data.get('business_domain') or "")
                    
                    horizons = ["Q3 2026", "Q4 2026", "2027 & Beyond"]
                    curr_hz_idx = horizons.index(row_data['target_horizon']) if row_data['target_horizon'] in horizons else 0
                    e_horizon = st.selectbox("Target Horizon", horizons, index=curr_hz_idx)
                with col2:
                    default_date = pd.to_datetime(row_data['target_date']).date() if pd.notna(row_data['target_date']) else None
                    e_date = st.date_input("Target Date", value=default_date)
                    e_audience = st.text_input("Target Audience", value=row_data.get('target_audience') or "")
                
                e_desc = st.text_area("Description", value=row_data.get('description') or "")
                e_status = st.checkbox("Visible Status", value=bool(row_data.get('visiblestatus')))

                col_btn1, col_btn2 = st.columns([1, 1])
                with col_btn1:
                    btn_update = st.form_submit_button("💾 Save Changes")
                with col_btn2:
                    btn_delete = st.form_submit_button("🗑️ Delete Item", type="secondary")

                if btn_update:
                    with conn.session as s:
                        s.execute(text("""
                            UPDATE tbl_roadmap SET
                            item_title = :title, item_type = :itype, business_domain = :domain,
                            target_horizon = :horizon, target_date = :tdate, description = :desc,
                            target_audience = :audience, visiblestatus = :status
                            WHERE roadmap_id = :id
                        """), {
                            "title": e_title, "itype": e_type, "domain": e_domain,
                            "horizon": e_horizon, "tdate": e_date, "desc": e_desc,
                            "audience": e_audience, "status": e_status, "id": selected_rm_id
                        })
                        s.commit()
                    st.success("Roadmap item updated successfully!")
                    st.rerun()

                if btn_delete:
                    with conn.session as s:
                        s.execute(text("DELETE FROM tbl_roadmap WHERE roadmap_id = :id"), {"id": selected_rm_id})
                        s.commit()
                    st.warning("Roadmap item deleted successfully!")
                    st.rerun()


# ==========================================
# TAB 5: User Access Management
# ==========================================
with tab_users:
    if user_role != "Admin":
        st.warning("⚠️ Access Denied: Only Admins can manage user access permissions.")
    else:
        st.subheader("Manage User Permissions")
        action_u = st.radio(
            "Choose Action:", 
            ["➕ Add New User", "✏️ Update / Delete Existing User"], 
            horizontal=True, key="action_u"
        )

        if action_u == "➕ Add New User":
            with st.form("form_add_user", clear_on_submit=True):
                u_email = st.text_input("User Email *")
                u_role = st.selectbox("User Role", ["Viewer", "Contributor", "Admin"])
                u_domain = st.text_input("Domain Access (Required if Contributor)")

                submit_user = st.form_submit_button("➕ Save User")

                if submit_user:
                    if not u_email.strip():
                        st.error("User Email is required.")
                    else:
                        with conn.session as s:
                            s.execute(text("""
                                INSERT INTO tbl_users (user_email, user_role, domain_access)
                                VALUES (:email, :role, :domain)
                            """), {"email": u_email, "role": u_role, "domain": u_domain})
                            s.commit()
                        st.success(f"User '{u_email}' added successfully!")
                        st.rerun()

        else:
            df_u = conn.query("SELECT * FROM tbl_users ORDER BY user_id", ttl="0s")
            if df_u.empty:
                st.info("No User records found.")
            else:
                u_options = {f"ID {row['user_id']} - {row['user_email']} ({row['user_role']})": row['user_id'] for _, row in df_u.iterrows()}
                selected_u_label = st.selectbox("Select User to Modify:", list(u_options.keys()))
                selected_u_id = u_options[selected_u_label]
                row_data = df_u[df_u['user_id'] == selected_u_id].iloc[0]

                with st.form("form_edit_user"):
                    e_email = st.text_input("User Email *", value=row_data['user_email'])
                    
                    roles = ["Viewer", "Contributor", "Admin"]
                    current_role_index = roles.index(row_data['user_role']) if row_data['user_role'] in roles else 0
                    e_role = st.selectbox("User Role", roles, index=current_role_index)
                    
                    e_domain = st.text_input("Domain Access", value=row_data.get('domain_access') or "")

                    col_btn1, col_btn2 = st.columns([1, 1])
                    with col_btn1:
                        btn_update = st.form_submit_button("💾 Save Changes")
                    with col_btn2:
                        btn_delete = st.form_submit_button("🗑️ Delete User", type="secondary")

                    if btn_update:
                        with conn.session as s:
                            s.execute(text("""
                                UPDATE tbl_users SET user_email = :email, user_role = :role, domain_access = :domain
                                WHERE user_id = :id
                            """), {"email": e_email, "role": e_role, "domain": e_domain, "id": selected_u_id})
                            s.commit()
                        st.success("User permissions updated successfully!")
                        st.rerun()

                    if btn_delete:
                        with conn.session as s:
                            s.execute(text("DELETE FROM tbl_users WHERE user_id = :id"), {"id": selected_u_id})
                            s.commit()
                        st.warning("User deleted successfully!")
                        st.rerun()
