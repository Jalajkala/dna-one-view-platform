import streamlit as st

st.title("Welcome to the E2A D&A One View Platform")
st.markdown("Please choose a path based on your data and analytical needs.")
st.markdown("---")

# Create three equal-width columns for a side-by-side layout
col1, col2, col3 = st.columns(3)

# --- Column 1: PATH A ---
with col1:
    # You can replace this URL with a local file path like "images/kpi_icon.png"
    st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=500&auto=format&fit=crop&q=60", use_container_width=True)
    st.subheader("PATH A")
    st.markdown("**KPI Catalog**")
    st.caption("“I want to build my understanding on various Standard KPIs”")
    
    # use_container_width=True makes the button stretch to match the image width
    if st.button("Explore KPI Catalog", use_container_width=True):
        st.switch_page("pages/path_a_kpi.py")

# --- Column 2: PATH B ---
with col2:
    st.image("https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=500&auto=format&fit=crop&q=60", use_container_width=True)
    st.subheader("PATH B")
    st.markdown("**Analytical Products Catalog**")
    st.caption("“I want to explore which Analytical Products are available to use, so I adopt, reuse and not rebuild”")
    
    if st.button("Explore Analytical Products", use_container_width=True):
        st.switch_page("pages/path_b_analytical.py")

# --- Column 3: PATH C ---
with col3:
    st.image("https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=500&auto=format&fit=crop&q=60", use_container_width=True)
    st.subheader("PATH C")
    st.markdown("**E2A Data Map**")
    st.caption("“My need is not Standard or is not covered by available Analytical Products. I would like to explore authorized data sources so I could build my analytical need as a citizen”")
    
    if st.button("Explore E2A Data Map", use_container_width=True):
        # Triggers the required alert before proceeding to Path C
        st.session_state.show_path_c_alert = True

st.markdown("---")

# --- Alert logic for PATH C selection ---
# This will render below the columns if the PATH C button is clicked
if st.session_state.get("show_path_c_alert", False):
    st.warning("Have you browsed the Analytical Catalog to be sure your need is not already covered ?")
    
    alert_col1, alert_col2 = st.columns(2)
    with alert_col1:
        if st.button("Yes (Proceed to Data Map)", use_container_width=True):
            st.session_state.show_path_c_alert = False
            st.switch_page("pages/path_c_datamap.py")
    with alert_col2:
        if st.button("No (Take me to Analytical Catalog)", use_container_width=True):
            st.session_state.show_path_c_alert = False
            st.switch_page("pages/path_b_analytical.py")
