import streamlit as st
import pandas as pd

# Navigation option back to Home Page
if st.button("← Back to Home"):
    st.switch_page("pages/home.py")

st.title("📈 PATH B: Standard Analytical Products Catalog")
st.markdown(
    "Explore existing Analytical Products available in the E2A region. "
    "Check here to adopt and reuse existing solutions before building new ones."
)
st.markdown("---")

# Fetch active Analytical Products data from Neon DB
try:
    conn = st.connection("neon_db", type="sql")
    # Retrieve only records configured to be shown on screen
    query = "SELECT * FROM tbl_analytical_product_catalog WHERE analytical_product_visiblestatus = TRUE;"
    df = conn.query(query, ttl="10s")
except Exception as e:
    st.error(f"Error connecting to the database: {e}")
    df = pd.DataFrame()

if df.empty:
    st.info("No active Analytical Products found in the catalog yet. (You can populate sample data or use the Admin Panel to add new products).")
else:
    # Top Control Bar: Search and Filters
    col_search, col_domain = st.columns([2, 1])

    with col_search:
        search_query = st.text_input("🔍 Search Product Title or Description", "")

    # Domain Filter
    domains = ["All"] + sorted([d for d in df["analytical_business_domain"].dropna().unique() if d])
    with col_domain:
        selected_domain = st.selectbox("Filter by Business Domain", domains)

    # Apply Filters
    filtered_df = df
    if selected_domain != "All":
        filtered_df = filtered_df[filtered_df["analytical_business_domain"] == selected_domain]

    if search_query:
        filtered_df = filtered_df[
            filtered_df["analytical_product_title"].str.contains(search_query, case=False, na=False) |
            filtered_df["analytical_product_description"].str.contains(search_query, case=False, na=False)
        ]

    st.markdown(f"**Showing {len(filtered_df)} Analytical Product(s)**")
    st.markdown("---")

    # Display Products in a slick card-style layout
    for idx, row in filtered_df.iterrows():
        with st.container():
            # Create a two-column layout for image (banner) and text details
            col_img, col_text = st.columns([1, 3])
            
            with col_img:
                banner_url = row.get('analytical_product_banner')
                if pd.notna(banner_url) and banner_url.strip() != "":
                    st.image(banner_url, use_container_width=True)
                else:
                    # Fallback placeholder image if no banner is provided
                    st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=500&auto=format&fit=crop&q=60", use_container_width=True)
            
            with col_text:
                st.subheader(row['analytical_product_title'])
                
                domain = row.get('analytical_business_domain', 'N/A')
                subdomain = row.get('analytical_business_subdomain', 'N/A')
                st.caption(f"**Domain:** {domain} | **Subdomain:** {subdomain}")
                
                st.write(row.get('analytical_product_description', 'No description available.'))
                st.markdown(f"🎯 **Target Audience:** {row.get('analytical_product_targetaudience', 'N/A')}")
                
                # Render the "Discover more in Collibra" button if a link exists
                collibra_link = row.get('analytical_product_collibra_link')
                if pd.notna(collibra_link) and collibra_link.strip() != "":
                    st.link_button("🔗 Discover more in Collibra", collibra_link)
                else:
                    st.button("🔗 Collibra Link Not Available", disabled=True, key=f"btn_disabled_{idx}")
            
            st.divider()
