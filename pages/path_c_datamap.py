import streamlit as st
import pandas as pd

# Navigation option back to Home Page
if st.button("← Back to Home"):
    st.switch_page("pages/home.py")

st.title("🗺️ PATH C: E2A Data Map")
st.markdown(
    "Explore authorized data sources across the E2A region. Use the filters below to find the data you need for your citizen development projects, then click through to Collibra for access details."
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
    st.info("No data sources found in the Data Map yet. (You can populate sample data or use the Admin Panel to add new sources).")
else:
    # Top Control Bar: Search and Multi-Select Filters
    col_search, col_domain, col_type = st.columns([2, 1, 1])

    with col_search:
        search_query = st.text_input("🔍 Search Data Source or Purpose", "")

    # Domain Filter
    domains = sorted([d for d in df["datasource_business_domain"].dropna().unique() if d])
    with col_domain:
        selected_domains = st.multiselect("Filter by Domain", options=domains, default=[])

    # Data Type Filter
    data_types = sorted([dt for dt in df["datasource_data_type"].dropna().unique() if dt])
    with col_type:
        selected_types = st.multiselect("Filter by Data Type", options=data_types, default=[])

    # Apply Filters
    filtered_df = df
    
    if selected_domains:
        filtered_df = filtered_df[filtered_df["datasource_business_domain"].isin(selected_domains)]
        
    if selected_types:
        filtered_df = filtered_df[filtered_df["datasource_data_type"].isin(selected_types)]

    if search_query:
        filtered_df = filtered_df[
            filtered_df["datasource_title"].str.contains(search_query, case=False, na=False) |
            filtered_df["datasource_purpose"].str.contains(search_query, case=False, na=False) |
            filtered_df["datasource_tag"].str.contains(search_query, case=False, na=False)
        ]

    st.markdown(f"**Showing {len(filtered_df)} Authorized Data Source(s)**")
    st.markdown("---")

    # Display Data Sources in a structured, scannable format
    for idx, row in filtered_df.iterrows():
        with st.container():
            col_main, col_action = st.columns([3, 1])
            
            with col_main:
                st.subheader(row['datasource_title'])
                
                # Format Metadata Tags visually
                domain = row.get('datasource_business_domain', 'N/A')
                subdomain = row.get('datasource_business_subdomain', 'N/A')
                dtype = row.get('datasource_data_type', 'N/A')
                tags = row.get('datasource_tag', 'None')
                
                st.caption(f"🏢 **Domain:** {domain} ({subdomain}) | 💾 **Type:** {dtype} | 🏷️ **Tags:** {tags}")
                st.write(row.get('datasource_purpose', 'No purpose description available.'))
            
            with col_action:
                st.write("") # Spacing
                st.write("") # Spacing
                collibra_link = row.get('datasource_link_to_collibra')
                if pd.notna(collibra_link) and collibra_link.strip() != "":
                    st.link_button("🔗 Access in Collibra", collibra_link, use_container_width=True)
                else:
                    st.button("🔗 No Collibra Link", disabled=True, key=f"btn_disabled_map_{idx}", use_container_width=True)
            
            st.divider()
