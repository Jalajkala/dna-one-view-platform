import streamlit as st

st.title("Welcome to the E2A D&A One View Platform")
st.markdown("Please choose a path based on your data and analytical needs.")
st.markdown("---")

# Section: PATH A
st.subheader("PATH A : KPI Catalog")
st.write("“I want to build my understanding on various Standard KPIs”")
if st.button("Explore KPI Catalog"):
    st.switch_page("pages/path_a_kpi.py")

st.markdown("---")

# Section: PATH B
st.subheader("PATH B : Analytical Products Catalog")
st.write("“I want to explore which Analytical Products are available to use, so I adopt, reuse and not rebuild”")
if st.button("Explore Analytical Products"):
    st.switch_page("pages/path_b_analytical.py")

st.markdown("---")

# Section: PATH C
st.subheader("PATH C : E2A Data Map")
st.write("“My need is not Standard or is not covered by available Analytical Products. I would like to explore authorized data sources so I could build my analytical need as a citizen”")

if st.button("Explore E2A Data Map"):
    # Triggers the required alert before proceeding to Path C
    st.session_state.show_path_c_alert = True

# Alert logic for PATH C selection
if st.session_state.get("show_path_c_alert", False):
    st.warning("Have you browsed the Analytical Catalog to be sure your need is not already covered ?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes (Proceed to Data Map)"):
            st.session_state.show_path_c_alert = False
            st.switch_page("pages/path_c_datamap.py")
    with col2:
        if st.button("No (Take me to Analytical Catalog)"):
            st.session_state.show_path_c_alert = False
            st.switch_page("pages/path_b_analytical.py")
