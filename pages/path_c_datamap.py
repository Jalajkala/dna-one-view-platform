import streamlit as st
import pandas as pd

# Navigation option back to Home Page
if st.button("← Back to Home"):
    st.switch_page("pages/home.py")

st.title("🗺️ PATH C: E2A Data Map")
st.markdown(
    "Navigate the data hierarchy from left to right to discover authorized data sources, "
    "or use the search bar to find specific data immediately."
)
st.markdown("---")

# Fetch active Data Source records from Neon DB
try:
    conn = st.connection("neon_db", type="sql")
    # Retrieve only data sources configured to be shown on screen
    query = "SELECT * FROM tbl_data_map WHERE datasource_visiblestatus = TRUE;"
    df = conn.query(query, ttl="10s")
except Exception as e:
    st.error(f"Error connecting to the database: {e}")
    df = pd.DataFrame()

if df.empty:
    st.info("No data sources found in the Data Map yet.")
else:
    # 1. Standalone Search Functionality
    search_query = st.text_input("🔍 Global Search (Data Source, Type, or Purpose)", "")
    st.markdown("---")

    # If user is searching, bypass the graph and show standard results
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
                    st.write(row.get('datasource_purpose', 'No purpose description available.'))
                    collibra_link = row.get('datasource_link_to_collibra')
                    if pd.notna(collibra_link) and collibra_link.strip() != "":
                        st.link_button("🔗 Access in Collibra", collibra_link)
    
    # 2. Left-to-Right Clickable Graph UI (Cascading Drill-Down)
    else:
        st.subheader("🗂️ Data Hierarchy Explorer")
        
        # Create 4 columns for the left-to-right flow
        col_domain, col_type, col_source, col_details = st.columns([1.2, 1.2, 1.5, 2.5])

        # --- Level 1: Domain ---
        with col_domain:
            st.markdown("**1. Domain**")
            domains = sorted(df["datasource_business_domain"].dropna().unique())
            selected_domain = st.radio("Select Domain", options=domains, label_visibility="collapsed")

        # --- Level 2: Data Type ---
        if selected_domain:
            with col_type:
                st.markdown("**2. Data Type**")
                # Filter by Domain
                type_df = df[df["datasource_business_domain"] == selected_domain]
                types = sorted(type_df["datasource_data_type"].dropna().unique())
                selected_type = st.radio("Select Data Type", options=types, label_visibility="collapsed")

            # --- Level 3: Datasource ---
            if selected_type:
                with col_source:
                    st.markdown("**3. Datasource**")
                    # Filter by Domain AND Data Type
                    source_df = type_df[type_df["datasource_data_type"] == selected_type]
                    sources = sorted(source_df["datasource_title"].dropna().unique())
                    selected_source = st.radio("Select Datasource", options=sources, label_visibility="collapsed")

                # --- Level 4: Details Card ---
                if selected_source:
                    with col_details:
                        st.markdown("**4. Source Details**")
                        # Extract the specific selected row
                        selected_row = source_df[source_df["datasource_title"] == selected_source].iloc[0]
                        
                        # Render the final clickable card
                        with st.container(border=True):
                            st.subheader(selected_row['datasource_title'])
                            
                            subdomain = selected_row.get('datasource_business_subdomain', 'N/A')
                            tags = selected_row.get('datasource_tag', 'None')
                            st.caption(f"**Subdomain:** {subdomain}[cite: 1]")
                            st.caption(f"🏷️ **Tags:** {tags}[cite: 1]")
                            
                            st.write(selected_row.get('datasource_purpose', 'No description available.') + "[cite: 1]")
                            
                            st.divider()
                            collibra_link = selected_row.get('datasource_link_to_collibra')
                            if pd.notna(collibra_link) and collibra_link.strip() != "":
                                st.link_button("🔗 Access in Collibra", collibra_link, use_container_width=True)
                            else:
                                st.button("🔗 No Collibra Link", disabled=True, use_container_width=True)
