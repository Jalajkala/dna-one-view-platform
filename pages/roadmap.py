import streamlit as st
import pandas as pd

# Navigation option back to Home Page
if st.button("← Back to Home"):
    st.switch_page("pages/home.py")

st.title("🚀 E2A Product & Data Roadmap")
st.markdown("Explore upcoming data sources and analytical products organized by delivery horizons.")
st.markdown("---")

# Fetch roadmap records from Neon DB
try:
    conn = st.connection("neon_db", type="sql")
    query = "SELECT * FROM tbl_roadmap WHERE visiblestatus = TRUE ORDER BY target_date ASC;"
    df = conn.query(query, ttl="10s")
except Exception as e:
    st.error(f"Error connecting to the database: {e}")
    df = pd.DataFrame()

if df.empty:
    st.info("No roadmap items found. You can add items using the Admin Panel.")
else:
    # Define your horizon columns
    horizons = ["Q3 2026", "Q4 2026", "2027 & Beyond"]
    
    # Create 3 side-by-side columns for the Kanban board
    cols = st.columns(len(horizons))
    
    for i, horizon in enumerate(horizons):
        with cols[i]:
            st.markdown(f"### 📌 {horizon}")
            st.markdown("---")
            
            # Filter items belonging to this specific horizon
            horizon_df = df[df["target_horizon"] == horizon]
            
            if horizon_df.empty:
                st.caption("No planned releases.")
            else:
                for _, row in horizon_df.iterrows():
                    with st.container(border=True):
                        st.markdown(f"**{row['item_title']}**")
                        
                        # Type & Domain badges
                        itype = row.get('item_type', 'Product')
                        domain = row.get('business_domain', 'General')
                        
                        type_emoji = "💾" if itype == "Data Source" else "📈"
                        st.caption(f"🏢 {domain} | {type_emoji} {itype}")
                        
                        # Description
                        st.write(row.get('description', 'No description provided.'))
                        
                        # Target Audience
                        audience = row.get('target_audience')
                        if pd.notna(audience) and audience.strip() != "":
                            st.markdown(f"🎯 *Audience:* {audience}")
