import streamlit as st
import pandas as pd
import plotly.express as px

# Navigation option back to Home Page
if st.button("← Back to Home"):
    st.switch_page("pages/home.py")

st.title("🚀 E2A Product & Data Roadmap")
st.markdown("Chronological milestone timeline of upcoming Analytical Products and Data Sources. Hover over any card to view detailed descriptions.")
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
    df = df.sort_values('target_date', ascending=True).reset_index(drop=True)
    
    if df.empty:
        st.info("Roadmap items require valid target dates to display on the timeline chart.")
    else:
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
            # Assign staggered vertical lanes (0 to 3) so cards cascade across time nicely like the reference wireframe
            filtered_df['lane'] = [i % 4 for i in range(len(filtered_df))]
            
            # Format display labels for the cards plotted on the timeline
            filtered_df['card_label'] = filtered_df['item_title'] + "<br>(" + filtered_df['item_type'] + ")"

            # Create Plotly Scatter Milestone Timeline
            fig = px.scatter(
                filtered_df,
                x="target_date",
                y="lane",
                color="item_type",
                text="item_title",
                color_discrete_map={
                    "Analytical Product": "#2563EB",  # Professional Blue
                    "Data Source": "#D97706"          # Warm Amber/Orange
                },
                custom_data=["item_type", "business_domain", "target_horizon", "description", "target_audience"],
                labels={"target_date": "Target Date", "item_type": "Artifact Type"}
            )

            # Style markers to look like clean cards/nodes
            fig.update_traces(
                marker=dict(size=18, symbol="square", line=dict(width=2, color="white")),
                textposition="top center",
                textfont=dict(size=11, family="sans-serif", color="black")
            )

            # Custom hover template showing all item details and full description on mouseover
            fig.update_traces(
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "📅 <b>Target Date:</b> %{x|%B %d, %Y}<br>"
                    "🏷️ <b>Type:</b> %{customdata[0]}<br>"
                    "🏢 <b>Domain:</b> %{customdata[1]}<br>"
                    "🎯 <b>Horizon:</b> %{customdata[2]}<br>"
                    "👥 <b>Audience:</b> %{customdata[4]}<br>"
                    "________________________________________<br>"
                    "📝 <b>Description:</b> %{customdata[3]}"
                    "<extra></extra>"
                )
            )

            # Layout styling for a professional executive look
            fig.update_layout(
                title="<b>Strategic Roadmap Milestone Timeline</b>",
                xaxis_title="<b>Timeline (Target Delivery Date)</b>",
                yaxis_title="",
                legend_title="<b>Artifact Legend</b>",
                font=dict(family="sans-serif", size=13),
                height=500,
                margin=dict(l=20, r=20, t=60, b=20),
                xaxis=dict(
                    showgrid=True, 
                    gridcolor='rgba(200,200,200,0.3)',
                    type='date'
                ),
                yaxis=dict(
                    showticklabels=False, 
                    showgrid=False, 
                    zeroline=False,
                    range=[-1, 4] # Padding for top/bottom labels
                ),
                plot_bgcolor='rgba(248,250,252,1)'
            )

            st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.subheader("📋 Detailed Roadmap Inventory")
            
            # Summary table below for quick reference
            display_df = filtered_df[['item_title', 'item_type', 'business_domain', 'target_horizon', 'target_date', 'target_audience', 'description']]
            display_df.columns = ['Title', 'Type', 'Domain', 'Horizon', 'Target Date', 'Audience', 'Description']
            display_df['Target Date'] = pd.to_datetime(display_df['Target Date']).dt.strftime('%b %d, %Y')
            st.dataframe(display_df, use_container_width=True, hide_index=True)
