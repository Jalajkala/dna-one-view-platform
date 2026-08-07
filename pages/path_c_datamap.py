import streamlit as st
import pandas as pd
from streamlit_agraph import agraph, Node, Edge, Config

# Navigation option back to Home Page
if st.button("← Back to Home"):
    st.switch_page("pages/home.py")

st.title("🗺️ PATH C: E2A Data Map")
st.markdown(
    "Explore the E2A data hierarchy using the interactive mind map below. "
    "**Click on any Data Source node (green boxes)** to view its details and access it in Collibra, "
    "or use the search bar to find specific data immediately."
)
st.markdown("---")

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
    
    # 2. Interactive Mind Map UI
    else:
        nodes = []
        edges = []
        
        # Track added nodes to prevent duplicates
        added_domains = set()
        added_types = set()

        # Add the Central Root Node
        nodes.append(Node(id="Root", label="E2A Data Map", size=25, shape="diamond", color="#FF6B6B"))

        # Build the graph hierarchy
        for _, row in df.iterrows():
            domain = row.get('datasource_business_domain', 'Unknown Domain')
            dtype = row.get('datasource_data_type', 'Unknown Type')
            source_title = row['datasource_title']
            
            # Create unique IDs for intermediate nodes
            domain_id = f"domain_{domain}"
            type_id = f"type_{domain}_{dtype}"
            
            # --- Add Domain Nodes ---
            if domain_id not in added_domains:
                nodes.append(Node(id=domain_id, label=domain, size=20, shape="dot", color="#4ECDC4"))
                edges.append(Edge(source="Root", target=domain_id))
                added_domains.add(domain_id)
                
            # --- Add Data Type Nodes ---
            if type_id not in added_types:
                nodes.append(Node(id=type_id, label=dtype, size=15, shape="dot", color="#45B7D1"))
                edges.append(Edge(source=domain_id, target=type_id))
                added_types.add(type_id)
                
            # --- Add Data Source Nodes ---
            # We use the exact title as the node ID so we can look it up when clicked
            nodes.append(Node(id=source_title, label=source_title, size=15, shape="box", color="#A8E6CF"))
            edges.append(Edge(source=type_id, target=source_title))

        # Configure graph physics and layout
        config = Config(
            width="100%",
            height=500,
            directed=True,
            physics=True,
            hierarchical=False, # Set to True for a strict top-down tree, False for a floating mind map
            nodeHighlightBehavior=True,
            highlightColor="#F7A7A6",
            collapsible=False
        )

        st.subheader("🗂️ Interactive Data Explorer")
        
        # Render the graph and capture the clicked node ID
        clicked_node_id = agraph(nodes=nodes, edges=edges, config=config)
        
        # 3. Display Detail Card when a Data Source is clicked
        if clicked_node_id:
            # Check if the clicked node is an actual Data Source (not a domain or type)
            selected_row = df[df["datasource_title"] == clicked_node_id]
            
            if not selected_row.empty:
                row_data = selected_row.iloc[0]
                
                st.markdown("### 📄 Source Details")
                with st.container(border=True):
                    st.subheader(row_data['datasource_title'])
                    
                    subdomain = row_data.get('datasource_business_subdomain', 'N/A')
                    tags = row_data.get('datasource_tag', 'None')
                    st.caption(f"**Subdomain:** {subdomain} | 🏷️ **Tags:** {tags}")
                    
                    st.write(row_data.get('datasource_purpose', 'No description available.'))
                    
                    st.divider()
                    collibra_link = row_data.get('datasource_link_to_collibra')
                    if pd.notna(collibra_link) and collibra_link.strip() != "":
                        st.link_button("🔗 Access in Collibra", collibra_link, use_container_width=True)
                    else:
                        st.button("🔗 No Collibra Link", disabled=True, use_container_width=True)
            else:
                st.info("💡 Keep drilling down: Click on a green Data Source box to view its details.")
