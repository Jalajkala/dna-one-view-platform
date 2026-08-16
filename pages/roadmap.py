import streamlit as st
import pandas as pd
import plotly.express as px

# Navigation option back to Home Page
if st.button("← Back to Home"):
    st.switch_page("pages/home.py")

st.title("🚀 E2A Product & Data Roadmap")
st.markdown("Interactive strategic delivery timeline of upcoming Analytical Products and Data Sources.")
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
    # Ensure target_date is formatted correctly
    df['target_date'] = pd.to_datetime(df['target_date'], errors='coerce')
    df = df.dropna(subset=['target_date'])
    
    if df.empty:
        st.info("Roadmap items require valid target dates to display on the timeline chart.")
    else:
        # Create visual start and end windows around the target date for the timeline bars
        df['start_date'] = df['target_date'] - pd.Timedelta(days=15)
        df['end_date'] = df['target_date'] + pd.Timedelta(days=15)
        df = df.sort_values('target_date', ascending=True)

        # Domain Filter Control
        col_f1, _ = st.columns([2, 2])
        with col_f1:
            selected_domains = st.multiselect(
                "Filter by Business Domain", 
                options=sorted(df['business_domain'].dropna().unique()), 
                default=[]
            )

        filtered_df = df
        if selected_domains:
            filtered_df = filtered_df[filtered_df['business_domain'].isin(selected_domains)]

        if filtered_df.empty:
            st.warning("No roadmap items match the selected domain filter.")
        else:
            # Create Plotly Gantt Timeline Chart with distinct colors and legend
            fig = px.timeline(
                filtered_df,
                x_start="start_date",
                x_end="end_date",
                y="item_title",
                color="item_type",
                color_discrete_map={
                    "Analytical Product": "#2563EB",  # Professional Blue
                    "Data Source": "#D97706"          # Warm Amber/Orange
                },
                hover_data={
                    "business_domain": True,
                    "target_horizon": True,
                    "target_date": True,
                    "description": True,
                    "target_audience": True,
                    "start_date": False,
                    "end_date": False
                },
                labels={"item_title": "Deliverable", "item_type": "Artifact Type"}
            )

            # Styling the chart layout for a slick, polished presentation
            fig.update_layout(
                title="<b>Strategic Delivery Timeline & Artifact Legend</b>",
                xaxis_title="<b>Target Delivery Window</b>",
                yaxis_title="",
                legend_title="<b>Artifact Type</b>",
                font=dict(family="sans-serif", size=13),
                height=450,
                margin=dict(l=20, r=20, t=60, b=20),
                xaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.2)'),
                yaxis=dict(autorange="reversed") # Orders earliest deliverables at the top
            )

            st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.subheader("📋 Detailed Roadmap Inventory")
            
            # Display summary table below for easy tabular referencing
            display_df = filtered_df[['item_title', 'item_type', 'business_domain', 'target_horizon', 'target_date', 'target_audience', 'description']]
            display_df.columns = ['Title', 'Type', 'Domain', 'Horizon', 'Target Date', 'Audience', 'Description']
            st.dataframe(display_df, use_container_width=True, hide_index=True)
