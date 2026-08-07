import streamlit as st
import pandas as pd

# Navigation option back to Home Page
if st.button("← Back to Home"):
    st.switch_page("pages/home.py")

st.title("🗺️ PATH C: E2A Data Map")
st.markdown("Navigate the data hierarchy from left to right to discover authorized data sources.")
st.markdown("---")

# Initialize session state variables to track the user's clickable path
if "selected_domain" not in st.session_state:
    st.session_state.selected_domain = None
if "selected_type" not in st.session_state:
    st.session_state.selected_type = None

# Callback functions to handle button clicks and manage state
def set_domain(domain):
    st.session_state.selected_domain = domain
    st.session_state.selected_type = None # Reset type when domain changes

def set_type(dtype):
    st.session_state.selected_type = dtype

# Fetch active Data Source records from Neon DB
try:
    conn = st.connection("neon_db", type="sql")
    query = "SELECT * FROM tbl_data_map WHERE datasource_visiblestatus = TRUE;"
    df = conn.query(query, ttl="10s")
except Exception as e:
    st.error(f"Error connecting to the database: {e}")
    df = pd.DataFrame()

if df.empty:
    st.info("No data sources found in the Data Map yet.")
else:
    # Top Control Bar: Search functionality
    search_query = st.text_input("🔍 Global Search (Data Source, Type, or Purpose)", "")
    st.markdown("---")

    # If user is searching, bypass the cascade and show standard results
    if search_query:
        st.subheader("🔎 Search Results")
        search_df = df[
            df["datasource_title"].str.contains(search_query, case=False, na=False) |
            df["datasource_purpose"].str.contains(search_query, case=False, na=False) |
            df["datasource_tag"].str.contains(search_query, case=False, na=False) |
            df["datasource_data_type"].str.contains(search_query, case=False, na=False)
        ]
        
        if search_df.empty:
            st.warning("No matching data sources found.")
        else:
            for idx, row in search_df.iterrows():
                with st.container(border=True):
                    st.subheader(row['datasource_title'])
                    st.caption(f"🏢 **Domain:** {row.get('datasource_business_domain')} | 💾 **Type:** {row.get('datasource_data_type')} | 🏷️ **Tags:** {row.get('datasource_tag')}")
                    st.write(row.get('datasource_purpose', 'No description available.'))
                    collibra_link = row.get('datasource_link_to_collibra')
                    if pd.notna(collibra_link) and collibra_link.strip() != "":
                        st.link_button("🔗 Access in Collibra", collibra_link)
    
    # Cascade UI (Matching the Wireframe)
    else:
        # Create 3 columns simulating the Miller Columns UI
        col_dom, col_typ, col_src = st.columns([1, 1, 1.5])
        
        # --- COLUMN 1: DOMAIN ---
        with col_dom:
            domains = sorted(df["datasource_business_domain"].dropna().unique())
            st.markdown(f"**DOMAIN** `{len(domains)}`")
            
            for domain in domains:
                # Calculate metrics for the button labels
                dom_df = df[df["datasource_business_domain"] == domain]
                type_count = dom_df["datasource_data_type"].nunique()
                src_count = len(dom_df)
                
                is_selected = (st.session_state.selected_domain == domain)
                btn_type = "primary" if is_selected else "secondary"
                
                # Render the button. (Streamlit buttons don't support deep HTML styling natively, 
                # so we format the string to mimic the wireframe's data presentation).
                btn_label = f"🏢 {domain} \n\n {type_count} types • {src_count} sources"
                st.button(
                    btn_label, 
                    key=f"dom_{domain}", 
                    type=btn_type, 
                    use_container_width=True, 
                    on_click=set_domain, 
                    args=(domain,)
                )

        # --- COLUMN 2: DATA TYPE ---
        with col_typ:
            if st.session_state.selected_domain:
                type_df = df[df["datasource_business_domain"] == st.session_state.selected_domain]
                dtypes = sorted(type_df["datasource_data_type"].dropna().unique())
                
                st.markdown(f"**DATA TYPE** `{len(dtypes)}`")
                
                for dtype in dtypes:
                    src_count = len(type_df[type_df["datasource_data_type"] == dtype])
                    
                    is_selected = (st.session_state.selected_type == dtype)
                    btn_type = "primary" if is_selected else "secondary"
                    
                    btn_label = f"📂 {dtype} \n\n {src_count} sources"
                    st.button(
                        btn_label, 
                        key=f"typ_{dtype}", 
                        type=btn_type, 
                        use_container_width=True, 
                        on_click=set_type, 
                        args=(dtype,)
                    )

        # --- COLUMN 3: DATA SOURCES ---
        with col_src:
            if st.session_state.selected_domain and st.session_state.selected_type:
                src_df = df[
                    (df["datasource_business_domain"] == st.session_state.selected_domain) & 
                    (df["datasource_data_type"] == st.session_state.selected_type)
                ]
                
                st.markdown(f"**DATA SOURCES** `{len(src_df)}`")
                
                for idx, row in src_df.iterrows():
                    with st.container(border=True):
                        st.markdown(f"**{row['datasource_title']}**")
                        
                        # Process tags to mimic the wireframe's pill design
                        tags_raw = str(row.get('datasource_tag', ''))
                        tag_html = ""
                        if tags_raw and tags_raw != 'nan':
                            tags_list = [t.strip() for t in tags_raw.split(',')]
                            for tag in tags_list:
                                # Simple inline CSS to create pill-like tags
                                tag_html += f'<span style="background-color:#E0E0E0; color:#333; padding:2px 8px; border-radius:12px; font-size:12px; margin-right:5px;">{tag}</span>'
                        
                        st.markdown(tag_html, unsafe_allow_html=True)
                        st.write(row.get('datasource_purpose', ''))
                        
                        collibra_link = row.get('datasource_link_to_collibra')
                        if pd.notna(collibra_link) and collibra_link.strip() != "":
                            st.link_button("🔗 Access in Collibra", collibra_link)
